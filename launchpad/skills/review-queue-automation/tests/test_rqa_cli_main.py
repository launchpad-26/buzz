#!/usr/bin/env python3
"""`rqa/cli/main.py` — the E-17 command surface and the E-21 `tick` entry
point. One success path, one refusal path and one exit code per subcommand,
against real collaborators over a real temp state directory — no mocks, no
pytest fixtures (`tests/run_all.py`'s own fixture-free convention).
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import io
import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest.mock
from datetime import datetime, timezone

_SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SKILL_ROOT))

from rqa.cli import exitcodes  # noqa: E402
from rqa.cli.main import main  # noqa: E402
from rqa.contracts import (  # noqa: E402
    EscalationCause,
    EscalationSubject,
    EscalationSubjectKind,
    GithubUnavailable,
    Job,
    JobStatus,
)
from rqa.escalation.escalate import raise_  # noqa: E402
from rqa.escalation.store import SqliteEscalationStore  # noqa: E402

# `rqa/cli/__init__.py` rebinds the `main` attribute on the `rqa.cli` package
# to the `main()` function itself (its own public surface), which shadows the
# `rqa.cli.main` *submodule* attribute Python's import machinery would
# otherwise leave in place. `importlib.import_module` reaches the real
# submodule directly, bypassing that shadowed attribute, so patching
# `main_module.build_composition` below patches the name `rqa/cli/main.py`
# itself calls.
main_module = importlib.import_module("rqa.cli.main")
from rqa.intake.store import SqliteJobStore, ensure_schema  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

_CLOCK = lambda: datetime(2026, 9, 14, tzinfo=timezone.utc)  # noqa: E731


class _OfflineGithub:
    """`resume()` (`code/P-02-lifecycle.md` §3.3) calls `deps.github.facts(...)`
    unconditionally before applying any decision — this test suite forbids a
    live network call (`tests/conftest.py`'s blocked socket), so every test
    that drives a real `decide()` -> `resume()` round trip swaps the
    composition's real `GithubAdapter` for this deterministic stand-in, the
    same way `tests/test_rqa_escalation_ac13_resume.py`'s `FakeGithub` does.
    `facts unavailable` is also the exact, real safe-stop path a genuinely
    unreachable GitHub takes (`resume.py`'s own `GithubUnavailable` branch),
    so this is not a shortcut around `resume()`'s real behaviour — it is that
    behaviour, with the network call itself replaced.
    """

    def facts(self, *, job, record):
        return GithubUnavailable(op="facts", reason="test-offline", retriable=False)


class _FakeKeyStore:
    """The E-25 `KeyStore` seam, answered in-process, so nothing in this file
    depends on the host having a platform keychain (`rqa/record/keychain.py`
    raises `KeyStoreExplanationUnavailable` off Darwin, which `append` turns
    into `AppendFailed` — `P-12-record.md` §3.1 step 5).

    It returns **real key bytes and never `None`**. `None` is the distinct
    ADR-0063 absent-key path: it would append *unkeyed* rows, these tests would
    go green, and they would have quietly stopped exercising the branch the CLI
    takes on an operator's machine. Same shape as the `FakeKeyStore` in
    `tests/test_rqa_record_append.py` / `test_rqa_record_keychain.py`, plus a
    record of the item names it was asked for so a test can prove it was the
    store actually consulted.
    """

    def __init__(self, *, key: bytes = b"cli-test-record-hmac-key") -> None:
        self.key = key
        self.names: list[str] = []

    def read(self, name: str) -> bytes | None:
        self.names.append(name)
        return self.key


_FAKE_KEYSTORE = _FakeKeyStore()


@contextlib.contextmanager
def _offline_composition():
    """Patch `rqa.cli.main.build_composition` so every command built during
    the `with` block gets a real composition with its `.github` swapped for
    `_OfflineGithub` — real jobs/record/escalation stores, no live socket."""
    real_build = main_module.build_composition

    def patched(state_dir, **kwargs):
        comp = real_build(state_dir, **kwargs)
        comp.github = _OfflineGithub()
        return comp

    with unittest.mock.patch.object(main_module, "build_composition", patched):
        yield


@contextlib.contextmanager
def _injected_keystore():
    """Patch `rqa.cli.main.build_composition` so every composition a command
    builds takes `_FAKE_KEYSTORE` instead of the host's `OSKeyStore`.

    **Why it lives in `_run_raw` rather than in each test.** `_cmd_pending`,
    `_cmd_decide` and `_cmd_explain` each build their own composition, and the
    decide path appends a `decision` entry through it; three of the tests that
    reach an append call `_run` with no other patching at all. Hanging the
    injection off the one funnel every in-process `main()` call in this file
    goes through covers all of those paths at once, and a test added later
    cannot forget it. It nests correctly inside `_offline_composition`, whose
    wrapper forwards `**kwargs` to the real builder, so the keystore travels
    through that helper unchanged.
    """
    real_build = main_module.build_composition

    def patched(state_dir, **kwargs):
        kwargs.setdefault("keystore", _FAKE_KEYSTORE)
        return real_build(state_dir, **kwargs)

    with unittest.mock.patch.object(main_module, "build_composition", patched), unittest.mock.patch.object(main_module, "OSKeyStore", return_value=_FAKE_KEYSTORE):
        yield


def _assert_every_entry_is_keyed(connection: sqlite3.Connection, job_id: str) -> None:
    """The stored proof that `_FAKE_KEYSTORE` put these rows on the *keyed*
    branch: `keyed = 1` and a real 64-hex `hmac` on every entry, and the only
    item ever asked of the key store is `rqa-record-hmac`. A writer that stopped
    keying — or a stub that started returning `None` — fails here."""
    rows = connection.execute(
        "SELECT seq, keyed, hmac FROM record_entries WHERE job = ? ORDER BY seq",
        (job_id,),
    ).fetchall()
    assert rows, f"no record entries for {job_id!r}"
    for seq, keyed, hmac in rows:
        assert keyed == 1, (job_id, seq, keyed)
        assert hmac is not None and len(hmac) == 64, (job_id, seq, hmac)
    assert set(_FAKE_KEYSTORE.names) == {"rqa-record-hmac"}, _FAKE_KEYSTORE.names


def _run_raw(state_dir: pathlib.Path, *args: str) -> tuple[int, str]:
    """`main()` in-process, argv exactly as a real invocation would pass it,
    stdout captured verbatim, and every composition built along the way handed
    the in-process key store (see `_injected_keystore`)."""
    buffer = io.StringIO()
    with _injected_keystore(), contextlib.redirect_stdout(buffer):
        code = main(["--state-dir", str(state_dir), *args])
    return code, buffer.getvalue()


def _run(state_dir: pathlib.Path, *args: str) -> tuple[int, dict]:
    """`_run_raw` with the stdout parsed back as the JSON it always is."""
    code, raw = _run_raw(state_dir, *args)
    return code, json.loads(raw)


def _seed_escalated_job(
    state_dir: pathlib.Path,
    *,
    job_id: str,
    repo: str,
    number: int,
    cause: EscalationCause,
    question: str,
    context: dict,
) -> int:
    """A real `ESCALATED` job with one real open escalation, written through
    RQA's own real stores — never a hand-built row. The writer takes the
    in-process `_FAKE_KEYSTORE`, so seeding proves the keyed append path rather
    than whatever key material the host machine happens to hold."""
    connection = sqlite3.connect(str(state_dir / "state.db"))
    ensure_schema(connection)
    jobs = SqliteJobStore(connection, clock=_CLOCK)
    record = SQLiteRecordWriter(connection, clock=_CLOCK, keystore=_FAKE_KEYSTORE)
    escalation_store = SqliteEscalationStore(connection)

    job = Job(
        id=job_id,
        repo=repo,
        number=number,
        head_sha="headsha",
        base_sha="basesha",
        head_repo=repo,
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snaphash",
        status=JobStatus.ESCALATED,
    )
    jobs.create(job)
    jobs.set_status(job.id, JobStatus.ESCALATED)
    jobs.set_snapshot_hash(job.id, "snaphash")
    connection.commit()

    escalation = raise_(
        job=job,
        cause=cause,
        subject=EscalationSubject(EscalationSubjectKind.OBLIGATION, "prod-signoff"),
        question=question,
        context=context,
        record=record,
        store=escalation_store,
    )
    connection.commit()
    _assert_every_entry_is_keyed(connection, job_id)
    connection.close()
    return escalation.id


def test_each_command_handler_calls_its_declared_provider_entry_point() -> None:
    """DoD 2: structural census, not behavioural coverage of return handling.
    CLI invocation tests cover the outcomes; this only guards provider wiring."""
    tree = ast.parse(pathlib.Path(main_module.__file__).read_text(encoding="utf-8"))
    expected = {
        "_cmd_tick": ["intake_tick"],
        "_cmd_onboard": ["policy_onboard"],
        "_cmd_status": ["lifecycle_status"],
        "_cmd_pending": ["escalation_pending"],
        "_cmd_decide": ["escalation_decide"],
        # The parser selects one form at runtime; both P-12 entry points must
        # remain represented in this handler.
        "_cmd_explain": ["explain_job", "record_explain"],
    }
    provider_names = frozenset(name for names in expected.values() for name in names)
    handlers = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_cmd_")
    }
    assert set(handlers) == set(expected)
    for handler_name, handler in handlers.items():
        calls = sorted(
            node.func.id
            for node in ast.walk(handler)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in provider_names
        )
        assert calls == sorted(expected[handler_name]), (handler_name, calls)


def test_composition_repr_elides_every_live_collaborator() -> None:
    with tempfile.TemporaryDirectory() as state:
        comp = main_module.build_composition(pathlib.Path(state))
        try:
            assert repr(comp) == "Composition(<20 injected collaborators; fields elided>)"
        finally:
            comp.connection.close()



def test_onboard_writes_then_refuses_the_second_call() -> None:
    with tempfile.TemporaryDirectory() as state, tempfile.TemporaryDirectory() as repos:
        state_dir = pathlib.Path(state)
        repo = str(pathlib.Path(repos) / "acme" / "widget")
        pathlib.Path(repo).mkdir(parents=True)

        code, payload = _run(state_dir, "onboard", repo)
        assert code == exitcodes.OK
        assert payload["outcome"] == "written"
        assert pathlib.Path(payload["result"]["path"]).is_file()

        code, payload = _run(state_dir, "onboard", repo)
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "refused"
        assert payload["result"]["reason"] == "already_exists"


def test_status_reports_not_found_for_an_unknown_pr() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        main_module.build_composition(state_dir, keystore=_FAKE_KEYSTORE).connection.close()
        code, payload = _run(state_dir, "status", "some/repo", "7")
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "not_found"
        assert payload["result"] == {"repo": "some/repo", "number": 7}


def test_status_reports_a_real_disposition_once_a_job_is_seeded() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        connection = sqlite3.connect(str(state_dir / "state.db"))
        ensure_schema(connection)
        jobs = SqliteJobStore(connection, clock=_CLOCK)
        job = Job(
            id="job-status", repo="acme/widget", number=5, head_sha="h1", base_sha="b1",
            head_repo="acme/widget", head_ref="feature", predecessor_job=None,
            predecessor_head_sha=None, snapshot_hash=None, status=JobStatus.QUEUED,
        )
        jobs.create(job)
        connection.execute(
            "INSERT INTO pr_facts (repo, number, head_sha, base_sha, head_repo, head_ref, "
            "author, labels, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("acme/widget", 5, "h1", "b1", "acme/widget", "feature", "someone", "[]",
             _CLOCK().isoformat()),
        )
        connection.commit()
        connection.close()

        code, payload = _run(state_dir, "status", "acme/widget", "5")
        assert code == exitcodes.OK
        assert payload["result"]["disposition"] == "being reviewed"
        assert payload["result"]["internal_state"] == "queued"

def test_unexpected_infrastructure_failure_is_normalized_exit_four_in_a_subprocess() -> None:
    """A corrupt SQLite path exercises the real process boundary: no patching,
    no traceback, and exactly one JSON object on stdout."""
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        (state_dir / "state.db").mkdir()
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "rqa.cli",
                "--state-dir",
                str(state_dir),
                "status",
                "acme/widget",
                "5",
            ],
            cwd=_SKILL_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        assert completed.returncode == exitcodes.OTHER
        assert completed.stderr == ""
        payload = json.loads(completed.stdout)
        assert payload["outcome"] == "error"
        assert payload["error_type"] == "OperationalError"
        assert payload["detail"] == "unable to open database file"



def test_tick_sweeps_zero_repos_and_exits_ok() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        code, payload = _run(state_dir, "tick")
        assert code == exitcodes.OK
        assert payload["outcome"] == "swept"
        assert payload["result"]["repos_admitted"] == []


def test_pending_decide_pending_round_trip_and_exit_codes() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        escalation_id = _seed_escalated_job(
            state_dir,
            job_id="job-loop",
            repo="acme/widget",
            number=11,
            cause=EscalationCause.AUTHORITY_REQUIREMENT,
            question="Deploying to prod requires operator sign-off; approve or request changes?",
            context={"obligation": "prod-signoff"},
        )

        code, payload = _run(state_dir, "pending")
        assert code == exitcodes.OK
        assert [row["id"] for row in payload["result"]] == [escalation_id]
        assert payload["result"][0]["subject"] == {
            "kind": "obligation",
            "identifier": "prod-signoff",
        }

        with _offline_composition():
            code, payload = _run(
                state_dir, "decide", str(escalation_id),
                "--actor", "jeff", "--basis", "sign-off obtained", "--outcome", "approved",
            )
        assert code == exitcodes.OK
        assert payload["outcome"] == "decided"
        assert payload["result"]["outcome"] == "approved"

        code, payload = _run(state_dir, "pending")
        assert code == exitcodes.OK
        assert payload["result"] == []

        # The `decision` entry the CLI itself appended through `comp.record`
        # must be keyed too: that is the second hardcoded `OSKeyStore()` this
        # change removed, and only a run through `build_composition` exercises
        # it.
        connection = sqlite3.connect(str(state_dir / "state.db"))
        try:
            kinds = [
                row[0]
                for row in connection.execute(
                    "SELECT kind FROM record_entries WHERE job = ? ORDER BY seq", ("job-loop",)
                )
            ]
            assert "decision" in kinds, kinds
            _assert_every_entry_is_keyed(connection, "job-loop")
        finally:
            connection.close()



def test_decide_refuses_an_unknown_escalation_id() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        main_module.build_composition(state_dir, keystore=_FAKE_KEYSTORE).connection.close()
        code, payload = _run(
            state_dir, "decide", "999", "--actor", "jeff", "--basis", "no such row",
        )
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "refused"
        assert payload["result"]["reason"] == "not_found"


def test_decide_refuses_an_outcome_against_a_non_authority_cause() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        escalation_id = _seed_escalated_job(
            state_dir,
            job_id="job-refuse",
            repo="acme/widget",
            number=12,
            cause=EscalationCause.EVIDENCE_GAP,
            question="The panel found conflicting evidence about the migration's rollback path.",
            context={},
        )
        code, payload = _run(
            state_dir, "decide", str(escalation_id),
            "--actor", "jeff", "--basis", "x", "--outcome", "approved",
        )
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "rejected"
        assert "authority_requirement" in payload["detail"]


def test_decide_refuses_a_blank_actor() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        escalation_id = _seed_escalated_job(
            state_dir,
            job_id="job-blank-actor",
            repo="acme/widget",
            number=13,
            cause=EscalationCause.EVIDENCE_GAP,
            question="The panel found conflicting evidence about the migration's rollback path.",
            context={},
        )
        code, payload = _run(state_dir, "decide", str(escalation_id), "--actor", "", "--basis", "x")
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "rejected"


def test_explain_reconstructs_offline_after_a_real_decision() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        escalation_id = _seed_escalated_job(
            state_dir,
            job_id="job-explain",
            repo="acme/widget",
            number=14,
            cause=EscalationCause.AUTHORITY_REQUIREMENT,
            question="Deploying to prod requires operator sign-off; approve or request changes?",
            context={"obligation": "prod-signoff"},
        )
        with _offline_composition():
            code, _ = _run(
                state_dir, "decide", str(escalation_id),
                "--actor", "jeff", "--basis", "sign-off obtained", "--outcome", "approved",
            )
        assert code == exitcodes.OK

        code, payload = _run(state_dir, "explain", "job", "job-explain")
        assert code == exitcodes.OK
        assert payload["result"]["job_id"] == "job-explain"
        assert payload["result"]["reviewer_type"] == "human"
        assert payload["result"]["reviewer_identity"] == ["jeff"]

        code, payload = _run(state_dir, "explain", "acme/widget", "999")
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "unavailable"
        assert payload["result"]["reason"] == "no_record"


def test_untrusted_escalation_text_is_neutralised_before_it_reaches_stdout() -> None:
    """AC06/the security section: a PR-derived control character embedded in an
    escalation's `question`/`context` never reaches the terminal raw."""
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        _seed_escalated_job(
            state_dir,
            job_id="job-evil",
            repo="acme/widget",
            number=15,
            cause=EscalationCause.CONFLICTING_JUDGEMENT,
            question="Fix typo\r\n\x1b[2K\x1b[ADISPOSITION: approved (all checks passed)",
            context={"pr_title": "Fix typo\r\x1b[2K\x1b[1mALL CLEAR\x1b[0m", "note": "bell\x07here"},
        )

        code, raw = _run_raw(state_dir, "pending")
        assert code == exitcodes.OK
        assert "\x1b" not in raw
        assert "\r" not in raw
        assert "\x07" not in raw
        payload = json.loads(raw)
        assert payload["result"][0]["question"] == (
            "Fix typo\\u000d\\u000a\\u001b[2K\\u001b[ADISPOSITION: approved (all checks passed)"
        )
        assert payload["result"][0]["context"] == {
            "pr_title": "Fix typo\\u000d\\u001b[2K\\u001b[1mALL CLEAR\\u001b[0m",
            "note": "bell\\u0007here",
        }


def test_a_missing_required_argument_is_an_input_error_not_argparses_own_exit_2() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        code, payload = _run(state_dir, "decide", "1", "--actor", "jeff")  # missing --basis
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "usage_error"


def test_explain_rejects_a_non_integer_pr_number_as_input_error() -> None:
    with tempfile.TemporaryDirectory() as state:
        state_dir = pathlib.Path(state)
        code, payload = _run(state_dir, "explain", "acme/widget", "not-a-number")
        assert code == exitcodes.INPUT_ERROR
        assert payload["outcome"] == "usage_error"
