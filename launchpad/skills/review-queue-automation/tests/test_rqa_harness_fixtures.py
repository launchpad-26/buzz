#!/usr/bin/env python3
"""Fakes and fixtures shared by the `rqa.harness` (P-06) tests.

**No live network and no model call, anywhere in this lane.** Every collaborator P-06
talks to is injected or local: `FakeSupply` stands in for P-02's `SupplyPort` over P-05,
`FakeRecord` for P-12's `RecordWriter`, and the "harness" is a generated Python script
run as a real subprocess. That last one is deliberate: `invoke()` spawns a process group,
builds an allow-listed environment and enforces a timeout, and a mock would test none of
it. A local `sys.executable` running a script this file wrote is not a network call and
not a model call, and it holds no credential.

`FakeRecord.append` pushes every payload through P-12's own `canonical_json`, so a test
fails here rather than in production if P-06 ever hands the record an enum, a datetime, a
dataclass or any other value `CONTRACTS.md` §7's payload rule excludes.

This module is named `test_rqa_harness_*` because that is the naming convention on this
branch and the ownership boundary this lane was given; the two tests at the bottom check
the fixtures themselves, so the file is not an empty collection target.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Blocking,
    Budget,
    CarriedEvidence,
    CarryOver,
    Category,
    CheckConclusion,
    CheckRun,
    Entry,
    EvidenceState,
    External,
    Facts,
    Job,
    JobStatus,
    Mechanical,
    Obligation,
    Plan,
    Policy,
    PrFacts,
    RemediationPolicy,
    Reservation,
    Route,
    RouteUnavailable,
    Snapshot,
    Spend,
    SubmittedReview,
)
from rqa.harness import adapters  # noqa: E402
from rqa.protocol import protocol_hash  # noqa: E402
from rqa.record.hashing import canonical_json  # noqa: E402

MOMENT = datetime(2026, 9, 12, 10, 30, 0, tzinfo=timezone.utc)

#: Tokens planted in every PR-derived field so a tree walk can prove none of them escaped
#: an envelope. Each is unmistakable and none occurs anywhere else in this repository.
TOKENS = {
    "title": "ZQTITLEZQ",
    "body": "ZQBODYZQ",
    "label": "ZQLABELZQ",
    "diff": "ZQDIFFZQ",
    "path": "ZQPATHZQ",
    "check": "ZQCHECKZQ",
    "author": "ZQAUTHORZQ",
    "branch": "ZQBRANCHZQ",
    "actor": "ZQACTORZQ",
}

#: Bytes that are not valid UTF-8 and that contain an envelope-marker look-alike. Their
#: base64 rendering is what a bundle may carry; the raw bytes must never appear.
BINARY = b"\x00\xff\xfe<<<END:diff:deadbeef>>>\x80ZQBINZQ\x01"


# ---------------------------------------------------------------------------
# Value fixtures
# ---------------------------------------------------------------------------


def make_job(*, job_id: str = "job-1") -> Job:
    return Job(
        id=job_id,
        repo="acme/widgets",
        number=7,
        head_sha="a" * 40,
        base_sha="b" * 40,
        head_repo="acme/widgets",
        head_ref=f"feature/{TOKENS['branch']}",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.REVIEWING,
    )


def make_facts(*, changed_paths: frozenset[str] | None = None, with_binary: bool = True) -> Facts:
    paths = changed_paths if changed_paths is not None else frozenset({f"src/{TOKENS['path']}.py"})
    pr = PrFacts(
        repo="acme/widgets",
        number=7,
        head_sha="a" * 40,
        base_sha="b" * 40,
        merge_base_sha="b" * 40,
        head_repo="acme/widgets",
        head_ref=f"feature/{TOKENS['branch']}",
        head_protected=False,
        author=TOKENS["author"],
        labels=frozenset({TOKENS["label"], "ready"}),
        title=f"Fix {TOKENS['title']}",
        body=f"Body with {TOKENS['body']}",
    )
    return Facts(
        pr=pr,
        diff=f"--- a/x\n+++ b/x\n+{TOKENS['diff']}\n",
        changed_paths=paths,
        revision_changed_paths=frozenset(),
        files={path: (BINARY if with_binary else b"plain\n") for path in sorted(paths)},
        checks=(
            CheckRun(
                name=f"ci/{TOKENS['check']}",
                conclusion=CheckConclusion.SUCCESS,
                sha="a" * 40,
                observed_at=MOMENT,
            ),
        ),
        base_checks=(),
        reviews=(
            SubmittedReview(
                id="R1",
                actor=TOKENS["actor"],
                outcome="approved",
                head_sha="a" * 40,
                submitted_at=MOMENT,
            ),
        ),
        fetched_at=MOMENT,
    )


def make_policy(
    *,
    obligations: tuple[Obligation, ...] = (),
    assurance: dict[str, int] | None = None,
) -> Policy:
    return Policy(
        version="policy-1",
        obligations=obligations,
        blocking=Blocking(categories=frozenset({Category.SECURITY}), severities=frozenset({"high"}), corroboration=1),
        mechanical=Mechanical(categories=frozenset({Category.MECHANICAL}), tools=frozenset({"fmt"})),
        assurance=dict(assurance or {"standard": 1}),
        remediation=RemediationPolicy(allow_forks=False),
    )


def make_snapshot(*, policy: Policy | None = None, routes: tuple[Route, ...] = ()) -> Snapshot:
    return Snapshot(
        hash="snap-1",
        repo="acme/widgets",
        protocol_hash=protocol_hash(),
        authority={activity: False for activity in Activity},
        routes=routes,
        external=External(allowed=False, deny_label="no-external"),
        policy=policy or make_policy(),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


def make_carry(*, reused: tuple[str, ...] = (), regenerated: tuple[str, ...] = ()) -> CarryOver:
    return CarryOver(
        reused=tuple(
            CarriedEvidence(
                obligation_id=obligation_id,
                state=EvidenceState.VERIFIED,
                source_job="job-0",
                source_judgement_seq=3,
                source_attestations=("job-0:01",),
            )
            for obligation_id in reused
        ),
        regenerated=regenerated,
        reasons={},
        source_job="job-0" if reused else None,
    )


def make_plan(*, obligations: tuple[str, ...] = ("O1",), participants: int = 1, strategy: str = "single_pass") -> Plan:
    return Plan(
        obligations=obligations,
        omitted={},
        strategy=strategy,
        participants=participants,
        risk_class="standard",
        head_sha="a" * 40,
        snapshot_hash="snap-1",
        protocol_hash=protocol_hash(),
        policy_version="policy-1",
    )


def make_route(*, script: pathlib.Path, family: str = "fam-a", command: tuple[str, ...] | None = None) -> Route:
    """A route whose "model" is the script standing in for a transport.

    `FakeAdapter.argv` reads the script path out of `Route.model`, which keeps one
    registered adapter serving every scripted behaviour — a test never edits the registry
    to add a transport, exactly as an operator never edits RQA's source to add a harness.
    """
    return Route(
        harness="fake",
        model=str(script),
        provider=f"provider-{family}",
        family=family,
        external=False,
        command=command,
    )


# ---------------------------------------------------------------------------
# Collaborator fakes
# ---------------------------------------------------------------------------


class FakeRecord:
    """P-12's `RecordWriter`, in memory, with P-12's own payload rule enforced."""

    def __init__(self, *, fail_kind: str | None = None) -> None:
        self.entries: list[tuple[str, str, dict]] = []
        self.fail_kind = fail_kind
        self._seq = 0

    def append(self, job_id: str, kind: str, payload) -> Entry:
        if kind == self.fail_kind:
            raise AppendFailed(f"injected failure appending {kind}")
        canonical_json(payload=payload)
        self._seq += 1
        self.entries.append((job_id, kind, dict(payload)))
        return Entry(seq=self._seq, hash=f"hash-{self._seq}")

    def of_kind(self, kind: str) -> list[dict]:
        return [payload for _, entry_kind, payload in self.entries if entry_kind == kind]

    def kinds(self) -> list[str]:
        return [entry_kind for _, entry_kind, _ in self.entries]


class FakeSupply:
    """P-02's `SupplyPort` over P-05, honouring the cursor the way `ladder.route` does."""

    def __init__(self, ladder: tuple[Route, ...], *, reserve_answers: list[object] | None = None) -> None:
        self.ladder = tuple(ladder)
        self.reserve_answers = list(reserve_answers or [])
        self.route_calls: list[tuple[str, object]] = []
        self.reserve_calls: list[Route] = []
        self.consumed_calls: list[tuple[object, int | None, Reservation]] = []
        self._issued = 0

    def route(self, obligation: str, cursor):
        self.route_calls.append((obligation, cursor))
        for candidate in self.ladder:
            if candidate in cursor.excluded_routes or candidate.family in cursor.excluded_families:
                continue
            return candidate, cursor
        return RouteUnavailable(no_fallback=True, tried=self.ladder)

    def reserve(self, plan: Plan, route: Route):
        self.reserve_calls.append(route)
        if self.reserve_answers:
            answer = self.reserve_answers.pop(0)
            if answer is not None:
                return answer
        self._issued += 1
        return Reservation(id=f"res-{self._issued}", tokens=1000)

    def consumed(self, attempt, reading: int | None, reservation: Reservation) -> Spend:
        self.consumed_calls.append((attempt, reading, reservation))
        return Spend(
            tokens=reading if reading is not None else reservation.tokens,
            measured=reading is not None,
            source="harness" if reading is not None else "reservation",
        )


class FakeAdapter:
    """A built-in-shaped adapter for the scripted transport.

    Registered through `adapters.register` like any other, so it passes the same
    role-separation and conformance-hash gate the three real defaults pass.
    """

    harness = "fake"
    enforceable_efforts = frozenset({"high"})
    role_separated_data = True
    read_only_proof = ("--fake-read-only",)

    @property
    def injection_conformance_hash(self) -> str:
        return adapters.conformance_suite_hash()

    def argv(self, route: Route, effort: str) -> tuple[str, ...]:
        return (sys.executable, route.model)

    def resolved_effort(self, requested: str) -> str:
        return requested if requested in self.enforceable_efforts else adapters.UNENFORCED_EFFORT


adapters.register(adapter=FakeAdapter())


# ---------------------------------------------------------------------------
# The scripted "harness"
# ---------------------------------------------------------------------------

VERDICT_TEMPLATE = {
    "protocol_version": "1",
    "identity": {"harness": "self-reported-harness", "model": "self-reported-model", "provider": "self-reported-provider"},
    "obligations": {"O1": {"state": "verified"}},
    "findings": [],
    "injection_attempts": [],
}

_SCRIPT = '''\
import json, pathlib, sys, time

BEHAVIOURS = {behaviours!r}
VERDICT = {verdict!r}
MARKER = {marker!r}

here = pathlib.Path(__file__).resolve()
counter = here.with_name(here.stem + ".count")
calls = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(calls + 1))
behaviour = BEHAVIOURS[calls] if calls < len(BEHAVIOURS) else BEHAVIOURS[-1]

verdict_path = pathlib.Path(sys.argv[-1])
protocol_path = pathlib.Path(sys.argv[-2])
bundle_path = pathlib.Path(sys.argv[-3])

log = here.with_name(here.stem + ".log")
with log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({{
        "argv": sys.argv,
        "bundle": str(bundle_path),
        "protocol": str(protocol_path),
        "verdict": str(verdict_path),
        "bundle_text": "".join(
            p.read_text(encoding="utf-8", errors="replace")
            for p in sorted(bundle_path.rglob("*")) if p.is_file()
        ),
        "behaviour": behaviour,
    }}) + "\\n")

def write(payload):
    verdict_path.write_text(json.dumps(payload), encoding="utf-8")

def usage(tokens):
    (verdict_path.parent / "usage.json").write_text(json.dumps({{"tokens": tokens}}), encoding="utf-8")

if behaviour == "valid":
    write(VERDICT)
elif behaviour.startswith("usage:"):
    write(VERDICT)
    usage(int(behaviour.split(":", 1)[1]))
elif behaviour == "invalid":
    verdict_path.write_text("{{ not json", encoding="utf-8")
elif behaviour == "noverdict":
    pass
elif behaviour == "exit2":
    sys.exit(2)
elif behaviour.startswith("exit"):
    sys.exit(int(behaviour[4:]))
elif behaviour == "sleep":
    time.sleep(60)
elif behaviour.startswith("conform"):
    text = "".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(bundle_path.rglob("*")) if p.is_file()
    )
    adversarial = MARKER in text
    payload = json.loads(json.dumps(VERDICT))
    if adversarial and behaviour != "conform_silent":
        payload["injection_attempts"] = [{{
            "field": "diff:src/payments/charge.py",
            "span_hash": "c" * 64,
            "reason": "the diff asks the reviewer to report every obligation verified",
        }}]
    if adversarial and behaviour == "conform_drift":
        payload["obligations"] = {{"O1": {{"state": "not_verified"}}}}
    write(payload)
else:
    sys.exit(97)
'''


def harness_script(*, directory: pathlib.Path, behaviours: tuple[str, ...], name: str = "harness") -> pathlib.Path:
    """Write a scripted stand-in transport and return its path.

    The `conform*` behaviours recognise the adversarial member by looking for the gate
    case's own payload in the bundle. That is a phrase match, and it is fine *here*: this
    script stands in for a model, and the property under test is the panel's gate, not
    the stand-in's cleverness. The real property — that a harness must not be passed by
    phrase matching — is what `_PARAPHRASES` and `suite_reasons()` enforce against a
    real adapter.
    """
    script = directory / f"{name}.py"
    script.write_text(
        _SCRIPT.format(
            behaviours=list(behaviours),
            verdict=VERDICT_TEMPLATE,
            marker=adapters.CONFORMANCE_GATE_CASE.payload,
        ),
        encoding="utf-8",
    )
    return script


def script_calls(*, script: pathlib.Path) -> list[dict]:
    """Every invocation the scripted transport saw, in order."""
    log = script.with_name(script.stem + ".log")
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]


def workspace():
    """A temporary directory context manager, so no test writes into the repository."""
    return tempfile.TemporaryDirectory()


# ---------------------------------------------------------------------------
# Tests of the fixtures themselves
# ---------------------------------------------------------------------------


def test_the_fake_adapter_is_registered_through_the_real_gate() -> None:
    assert adapters.registered(harness="fake") is not None
    assert "fake" in adapters.builtin_harnesses()


def test_the_scripted_transport_reports_the_three_appended_paths() -> None:
    with workspace() as raw:
        directory = pathlib.Path(raw)
        script = harness_script(directory=directory, behaviours=("valid",))
        bundle = directory / "bundle"
        bundle.mkdir()
        (bundle / "artifacts").mkdir()
        verdict = directory / "verdict.json"
        import subprocess

        subprocess.run(
            [sys.executable, str(script), str(bundle), str(directory / "PROTOCOL.md"), str(verdict)],
            check=True,
        )
        calls = script_calls(script=script)
        assert len(calls) == 1
        assert calls[0]["bundle"] == str(bundle)
        assert calls[0]["verdict"] == str(verdict)
        assert json.loads(verdict.read_text())["protocol_version"] == "1"
