#!/usr/bin/env python3
"""§8 row T16 — the credential appears nowhere after a real call.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

This is the one test in the file set that wires the *real* pieces together: the real
`Gate`, the real `credential()` over a substituted process, the real
`SqliteCapabilityStore` over a real on-disk database, and a record fake that keeps every
byte it is handed. After a full grant it searches for the token value in

* the store's file, as bytes on disk;
* every record payload, as JSON;
* everything written to the root logger, stdout and stderr during the call;
* the returned `Grant` and the persisted `CapabilityProof`.

RQA-NFR-025 is the requirement: the credential is held in memory for the duration of one
probe and written nowhere. A comment asserting that is worth nothing; this searches.
"""

from __future__ import annotations

import contextlib
import io
import json
import logging
import pathlib
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.authority.capability as capability  # noqa: E402
from rqa.authority.gate import Gate  # noqa: E402
from rqa.authority.store import SqliteCapabilityStore  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    Blocking,
    Budget,
    CapabilityReading,
    Category,
    Entry,
    External,
    Mechanical,
    Policy,
    RemediationPolicy,
    Snapshot,
)

REPO = "launchpad-26/buzz"
JOB = "job-1"
# Deliberately token-shaped, and deliberately not a real token: the point of the row is
# that a distinctive string put into `gh auth token`'s stdout comes back out nowhere.
TOKEN = "gho_T16CanaryTokenValue000000000000000000"  # nosec


class RecordingRecord:
    def __init__(self):
        self.rows: list[tuple[str, str, dict]] = []

    def append(self, job_id: str, kind: str, payload: dict) -> Entry:
        self.rows.append((job_id, kind, dict(payload)))
        seq = len(self.rows)
        return Entry(seq=seq, hash=f"{seq:064d}")


class Probe:
    """A probe that is handed the credential and reports a full capability set."""

    def __init__(self):
        self.credentials: list[str] = []

    def probe(self, *, repo: str, credential: str):
        self.credentials.append(credential)
        return CapabilityReading(
            capabilities=frozenset({"pulls:read", "contents:read", "checks:read", "issues:write"}),
            attested_not_proven=frozenset({"admin:org"}),
            login="rqa-operator",
        )


def snapshot() -> Snapshot:
    return Snapshot(
        hash="a" * 64,
        repo=REPO,
        protocol_hash="b" * 64,
        authority={activity: activity is Activity.REVIEW for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label=""),
        policy=Policy(
            version="unversioned",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(
                categories=frozenset({Category.MECHANICAL}), tools=frozenset({"ruff"})
            ),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


@contextlib.contextmanager
def gh_returns(token: str):
    original = capability._run
    capability._run = lambda argv: subprocess.CompletedProcess(
        list(argv), 0, token.encode() + b"\n", b""
    )
    try:
        yield
    finally:
        capability._run = original


@contextlib.contextmanager
def captured():
    """Everything a handler could see: root-logger output, stdout and stderr."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.NOTSET)
    root = logging.getLogger()
    previous_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    out, err = io.StringIO(), io.StringIO()
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    try:
        yield lambda: stream.getvalue() + out.getvalue() + err.getvalue()
    finally:
        sys.stdout, sys.stderr = real_out, real_err
        root.removeHandler(handler)
        root.setLevel(previous_level)


def test_t16_the_token_appears_in_no_store_row_no_record_row_and_no_log_output() -> None:
    path = pathlib.Path(__file__).resolve().parent / "_rqa_authority_t16.db"
    path.unlink(missing_ok=True)
    connection = sqlite3.connect(path)
    try:
        store = SqliteCapabilityStore(connection)
        record = RecordingRecord()
        probe = Probe()
        with gh_returns(TOKEN), captured() as output:
            answer = Gate(repos=frozenset({REPO})).grant(
                repo=REPO,
                activity=Activity.REVIEW,
                snapshot=snapshot(),
                job_id=JOB,
                categories=None,
                record=record,
                github=probe,
                store=store,
            )
            logged = output()
        connection.commit()

        # The probe really did receive it: without this the search below proves nothing.
        assert probe.credentials == [TOKEN]

        assert TOKEN not in path.read_bytes().decode("utf-8", "replace"), "token in the store file"
        assert TOKEN not in json.dumps(record.rows, default=str), "token in a record row"
        assert TOKEN not in logged, "token in log/stdout/stderr output"
        assert TOKEN not in repr(answer), "token in the returned Grant"
        assert TOKEN not in repr(store.current(REPO, JOB)), "token in the persisted proof"
    finally:
        connection.close()
        path.unlink(missing_ok=True)


def test_t16_a_failed_credential_read_leaks_nothing_either() -> None:
    """The failure paths are where a token usually escapes — into the message that
    explains what went wrong."""
    original = capability._run
    capability._run = lambda argv: subprocess.CompletedProcess(
        list(argv), 1, TOKEN.encode(), TOKEN.encode()
    )
    try:
        with captured() as output:
            try:
                capability.credential()
            except capability.CredentialGithubUnavailable as error:
                assert TOKEN not in str(error)
                assert TOKEN not in repr(error)
                assert TOKEN not in output()
                return
    finally:
        capability._run = original
    raise AssertionError("a non-zero `gh auth token` did not raise")


def _reachable_from(error: BaseException) -> str:
    """Every string the raised exception can be made to yield by introspection: its own
    text, its attributes, and everything on `__context__`/`__cause__` recursively, plus
    this package's frames on each traceback.

    `CredentialGithubUnavailable` propagates uncaught out of `probe_capability` and
    `Gate.grant` by design, so a downstream consumer — P-02's error handling, a
    structured reporter, `traceback.TracebackException(chain=True)`, a debugger,
    `vars(error)` — sees exactly this. A search that stops at `str()` is not the search
    §8 T16 commits to.
    """
    seen: list[BaseException] = []
    pending: list[BaseException | None] = [error]
    while pending:
        current = pending.pop()
        if current is None or any(current is item for item in seen):
            continue
        seen.append(current)
        pending.extend([current.__context__, current.__cause__])
    parts: list[str] = []
    for item in seen:
        parts.extend([str(item), repr(item), repr(getattr(item, "args", ()))])
        parts.extend(repr(value) for value in vars(item).values())
        for attribute in ("output", "stdout", "stderr"):
            parts.append(repr(getattr(item, attribute, None)))
        frame = item.__traceback__
        while frame is not None:
            if "rqa/authority/" in frame.tb_frame.f_code.co_filename:
                parts.append(repr(frame.tb_frame.f_locals))
            frame = frame.tb_next
    return "".join(parts)


def test_t16_a_timed_out_credential_read_leaks_nothing_through_the_exception_chain() -> None:
    """The branch `test_t16_a_failed_credential_read_leaks_nothing_either` never reached:
    a real `subprocess.TimeoutExpired`, carrying the credential in both `output` and
    `stderr`, raised out of `_run` and caught by `credential()`.

    `raise ... from None` suppresses the chain's *display* and leaves the caught object
    attached to `__context__`, so `str()`-only searches — including this file's own, in
    round 1 — report zero occurrences while the live credential sits one attribute away.
    """
    timeout = subprocess.TimeoutExpired(
        list(capability.GH_TOKEN_ARGV), 30.0, output=TOKEN.encode(), stderr=TOKEN.encode()
    )

    def explode(argv):
        raise timeout

    original = capability._run
    capability._run = explode
    try:
        with captured() as output:
            try:
                capability.credential()
            except capability.CredentialGithubUnavailable as error:
                assert error.__context__ is None, (
                    "the TimeoutExpired that captured the credential is still reachable "
                    "through __context__"
                )
                assert error.__cause__ is None
                assert TOKEN not in _reachable_from(error)
                assert TOKEN not in output()
                return
    finally:
        capability._run = original
    raise AssertionError("a timed-out `gh auth token` did not raise")


def test_t16_the_failing_credential_paths_are_searched_the_same_way() -> None:
    """The non-zero-exit branch, put through the same chain walk as the timeout branch
    rather than through `str()` alone."""
    original = capability._run
    capability._run = lambda argv: subprocess.CompletedProcess(
        list(argv), 1, TOKEN.encode(), TOKEN.encode()
    )
    try:
        try:
            capability.credential()
        except capability.CredentialGithubUnavailable as error:
            assert TOKEN not in _reachable_from(error)
            return
    finally:
        capability._run = original
    raise AssertionError("a non-zero `gh auth token` did not raise")


def test_t16_the_token_is_not_held_on_the_frame_of_a_propagating_probe_failure() -> None:
    """`probe_capability` drops the credential in a `finally`, so a traceback walked by
    a handler that prints frame locals carries no credential out of this package.

    Scoped to this package's own frames on purpose: the injected probe is *handed* the
    credential by E-16, so its frame holds one by contract. What P-08 controls is that
    its own frames do not keep a copy once the probe has been made.
    """

    class Exploding:
        def probe(self, *, repo: str, credential: str):
            raise RuntimeError("the adapter failed")

    store = SqliteCapabilityStore(sqlite3.connect(":memory:"))
    with gh_returns(TOKEN):
        try:
            capability.probe_capability(REPO, Exploding(), store, JOB)
        except RuntimeError as error:
            frames = []
            traceback = error.__traceback__
            while traceback is not None:
                code = traceback.tb_frame.f_code
                if "rqa/authority/" in code.co_filename:
                    frames.append((code.co_name, repr(traceback.tb_frame.f_locals)))
                traceback = traceback.tb_next
            assert [name for name, _ in frames] == ["probe_capability"], frames
            assert TOKEN not in "".join(locals_ for _, locals_ in frames)
            return
    raise AssertionError("the adapter failure did not propagate")


def test_t16_the_package_source_contains_no_credential_bearing_write() -> None:
    """A static companion to the searches above: nothing in the package hands the
    credential to a store, a record, a logger or a formatted string."""
    package = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "authority"
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for leak in ("logging.", "print(", "credential=credential", "token}", "{token"):
            assert leak not in source, f"{path.name} contains {leak!r}"


def test_t16_probed_at_is_a_timestamp_not_a_token() -> None:
    """Guards the search above from passing because nothing at all was written."""
    store = SqliteCapabilityStore(sqlite3.connect(":memory:"))
    with gh_returns(TOKEN):
        proof = capability.probe_capability(REPO, Probe(), store, JOB)
    assert isinstance(proof.probed_at, datetime)
    assert proof.probed_at.tzinfo is not None
    assert proof.probed_at <= datetime.now(timezone.utc)
    assert proof.login == "rqa-operator"
