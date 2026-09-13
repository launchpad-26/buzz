"""The complete route / reservation / invocation / validation / consumption loop —
`code/P-06-harness-interface.md` §3.2, `CONTRACTS.md` §10.

P-02 calls `run()` once per review and sees only the `PanelResult`. Every retry, every
fallback, every exclusion and every consumption report happens here, which is what
`CONTRACTS.md` §10 means by "P-06 owns the panel loop". U-DISPATCH-14 is kept at exactly
that shape: one bounded panel-driving loop, with degradation *targets* coming from P-05's
refusals and being applied by P-02 at outcome minting.

Four properties are load-bearing, and each one is a specific failure this design refuses.

**A fresh reservation immediately before every invocation, including the retry.** §3.2
steps 3 and 6, and `CONTRACTS.md` §10. The reservation call sits inside the inner loop,
never above it, so the transient retry at step 6 returns to step 3 and asks again. A
reservation obtained once and reused across attempts spends twice against one bound, and
AC11 — the PRD's highest-severity failure mode — would be a false green: the record would
show a bound respected that was not. T7 fails on a single shared reservation.

**The loop is finite, structurally.** Every non-success selection grows the cursor: a
non-completing valid verdict, a `CANDIDATE_TERMINAL` and a second transient exclude the
route; a `PROVIDER_TERMINAL` and a `Refusal(fallback)` exclude the family; a failed
conformance gate excludes the route. The only same-route repeat is bounded to one. And
because a `SupplyPort` that hands back an already-excluded route would break that
argument from outside, it is checked: an excluded route coming back is `HarnessError`,
not another lap. That check is what makes T12's termination a property of this module
rather than a property of whichever port it was tested with.

**`bound_reached` latches on the first refusal and is never cleared.** Including
`Refusal(fallback)`, which resumes selection and may still complete the panel. RQA-FR-039
permits taking a configured fallback and forbids the *disposition* that follows from
being successful; P-07 §3 step 10 enforces the second half and cannot do so unless this
flag survives a subsequent success. T4b is that exact shape.

**Attestation is RQA's measurement, never the model's claim.** `Attestation.harness`,
`.model`, `.provider` and `.route` are the `Route` RQA selected; `.effort` is what the
adapter says the transport will actually apply; `.started_at`, `.ended_at` and
`.exit_code` are what `invoke()` measured on RQA's own clock. The harness's own
`HarnessIdentity` is written into the `attestation` payload under a separate
`self_reported` key and is never merged with the attested fields — U-VERDICT-11, kept:
"reading the family from the JSON the model produced lets a model assert an independence
it does not have, and independence is precisely what the mode aggregation counts."

**Stale slots are cleared before an attempt runs** (U-VERDICT-12, U-DOCS-09, U-DOCS-41,
all kept). A harness slot left by an earlier run of the same job is removed before the
new invocation, so a re-run can never be satisfied by the very output that caused it.

Nothing in this module parses `verdict.json` to decide validity: E-08 is the only
validator, and the classification table in §3.3 reads only `Valid`/`Invalid`, the exit
code and the timeout flag. Nothing here writes a `spend` entry or mints a `Spend`; §7 is
explicit that P-06 requests reservations and reports observed consumption, and the
`Spend` that comes back is P-05's answer.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from rqa.contracts import (
    Attempt,
    AttemptFailure,
    Attestation,
    BundleFailure,
    Facts,
    Job,
    PanelResult,
    Plan,
    PrFacts,
    Refusal,
    Reservation,
    Route,
    RouteCursor,
    RouteUnavailable,
    Snapshot,
    SubmittedReview,
    SupplyPort,
)
from rqa.harness.adapters import (
    CONFORMANCE_GATE_CASE,
    CONFORMANCE_SUITE_ID,
    ConformanceCase,
    adapter_for,
    authority_for_mode,
    conformance_suite_hash,
    pair_reasons,
)
from rqa.harness.bundle import assemble, assemble_into, protocol_instruction_path
from rqa.harness.errors import EmptyPlanError, HarnessError
from rqa.harness.invoke import (
    ATTEMPT_TIMEOUT_SECONDS,
    CONFORMANCE_TIMEOUT_SECONDS,
    Execution,
    argv_hash,
    invoke,
    utcnow,
)
from rqa.harness.risk import STRATEGIES
from rqa.protocol import Invalid, Valid, Verdict, validate

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from rqa.contracts import HarnessAdapter, RecordWriter

__all__ = [
    "ATTESTATION_FILENAME",
    "HARNESS_DIRNAME",
    "SupplyPort",
    "USAGE_FILENAME",
    "VERDICT_FILENAME",
    "run",
]

#: §5's second tree: `jobs/<job>/harness/<NN>/`.
HARNESS_DIRNAME = "harness"
#: The output path RQA passes and the harness writes. Its absence after a zero exit is
#: `CANDIDATE_TERMINAL` (§3.3's table), never an empty success.
VERDICT_FILENAME = "verdict.json"
#: The optional usage sidecar. Present means a measured reading; absent means P-05 falls
#: back to the reservation ceiling and marks the spend estimated (`rqa/supply/spend.py`).
USAGE_FILENAME = "usage.json"
STDOUT_FILENAME = "stdout.log"
STDERR_FILENAME = "stderr.log"
#: RQA's own attestation sidecar, written beside the harness's output (§5). U-VERDICT-11:
#: the provenance is a file RQA writes, not a field the model fills in.
ATTESTATION_FILENAME = "attestation.json"
#: E-08's reasons for an invalid verdict, kept job-local. They quote harness output, so
#: they are diagnosable here and never copied into a record payload.
VALIDATION_FILENAME = "validation.json"

#: Keys a usage sidecar may state its reading under, in order of preference.
_READING_KEYS = ("tokens", "total_tokens")



def _exclude_route(cursor: RouteCursor, route: Route) -> RouteCursor:
    return replace(cursor, excluded_routes=cursor.excluded_routes | {route})


def _exclude_family(cursor: RouteCursor, route: Route) -> RouteCursor:
    return replace(cursor, excluded_families=cursor.excluded_families | {route.family})


def _slot(*, state_dir: Path, job_id: str, ordinal: int) -> Path:
    """`jobs/<job>/harness/<NN>/`, cleared of anything an earlier run left there."""
    path = state_dir / "jobs" / job_id / HARNESS_DIRNAME / f"{ordinal:02d}"
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    return path


def _reading(*, slot: Path) -> int | None:
    """The harness's own usage reading, or `None` when it exposed none.

    Anything unreadable, unparseable or not a non-negative integer is `None` — an absent
    measurement, which P-05 marks estimated. Inventing a number here would be the exact
    provenance defect `rqa/supply/spend.py` exists to prevent, and a reading of `0` is a
    real measurement of zero rather than a missing one, so the test is on the type.
    """
    try:
        payload = json.loads((slot / USAGE_FILENAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    for key in _READING_KEYS:
        value = payload.get(key)
        if type(value) is int and value >= 0:
            return value
    return None


def _classify(*, execution: Execution, slot: Path, attempt_id: str) -> tuple[Verdict | AttemptFailure, dict[str, object] | None]:
    """§3.3's classification table, branch for branch, and nothing else.

    | Exit 0 and E-08 returns `Valid`            | valid `Verdict`      |
    | Exit 0 without verdict, or `Invalid`       | `CANDIDATE_TERMINAL` |
    | Exit 2                                     | `PROVIDER_TERMINAL`  |
    | Other non-zero exit or timeout             | `TRANSIENT`          |
    | Spawn `OSError`                            | `CANDIDATE_TERMINAL` |
    """
    if execution.spawn_failed:
        return AttemptFailure(kind="CANDIDATE_TERMINAL", detail="spawn_failed"), None
    if execution.timed_out:
        return AttemptFailure(kind="TRANSIENT", detail="timeout"), None
    if execution.exit_code == 0:
        verdict_path = slot / VERDICT_FILENAME
        if not verdict_path.exists():
            return AttemptFailure(kind="CANDIDATE_TERMINAL", detail="no_verdict"), None
        result = validate(path=verdict_path, attempt_id=attempt_id)
        if isinstance(result, Valid):
            identity = result.verdict.identity
            self_reported: dict[str, object] = {
                "harness": identity.harness,
                "model": identity.model,
                "provider": identity.provider,
                "protocol_version": result.verdict.protocol_version,
            }
            return result.verdict, self_reported
        # E-08's reasons quote the harness's own output, which may itself quote PR bytes.
        # They stay on local disk; the record carries only a count and a digest, which is
        # enough to correlate an entry with the file and carries nothing untrusted.
        _write_validation(slot=slot, invalid=result)
        return (
            AttemptFailure(kind="CANDIDATE_TERMINAL", detail=f"invalid_verdict:{len(result.reasons)}"),
            None,
        )
    if execution.exit_code == 2:
        return AttemptFailure(kind="PROVIDER_TERMINAL", detail="exit_2"), None
    return AttemptFailure(kind="TRANSIENT", detail=f"exit_{execution.exit_code}"), None


def _write_validation(*, slot: Path, invalid: Invalid) -> None:
    try:
        (slot / VALIDATION_FILENAME).write_text(
            json.dumps({"reasons": list(invalid.reasons)}, indent=2), encoding="utf-8"
        )
    except (OSError, UnicodeError, TypeError, ValueError):
        # Diagnostics are best-effort; a slot that cannot hold them does not change the
        # classification the loop acts on.
        return


def _attest(*, route: Route, effort: str, execution: Execution) -> Attestation:
    """The attested facts, all of them measured or selected by RQA (RQA-NFR-022, AC06).

    Every argument is RQA's: `route` is the candidate RQA's own `SupplyPort` returned,
    `effort` is what the adapter says the transport will actually apply, and `execution`
    is what `invoke()` measured. Nothing the harness wrote reaches this function.
    """
    return Attestation(
        harness=route.harness,
        model=route.model,
        provider=route.provider,
        route=route,
        effort=effort,
        started_at=execution.started_at,
        ended_at=execution.ended_at,
        exit_code=execution.exit_code,
    )


def _attestation_payload(
    *,
    attempt: Attempt,
    adapter: HarnessAdapter,
    requested_effort: str,
    execution: Execution,
    self_reported: dict[str, object] | None,
) -> dict[str, object]:
    """§6's `attestation` row: attested route fields, effort, observed times and exit
    code, outcome/detail, **and separately marked self-reported verdict identity**.

    The two halves never merge. `attested` is RQA's; `self_reported` is the harness's own
    claim about itself, recorded because AC06 wants it on the record and marked because
    RQA-NFR-022 forbids it from being provenance.
    """
    attestation = attempt.attestation
    route = attempt.route
    outcome = attempt.outcome
    return {
        "attempt_id": attempt.id,
        "subject": "attempt",
        "attested": {
            "harness": attestation.harness,
            "model": attestation.model,
            "provider": attestation.provider,
            "family": route.family,
            "external": route.external,
            "external_command": route.command is not None and len(route.command) > 0,
            "argv_hash": argv_hash(execution.argv),
            "effort": attestation.effort,
            "effort_requested": requested_effort,
            "effort_enforced": attestation.effort == requested_effort,
            "read_only_proof": list(getattr(adapter, "read_only_proof", ())),
            "started_at": attestation.started_at.isoformat(),
            "ended_at": attestation.ended_at.isoformat(),
            "exit_code": attestation.exit_code,
        },
        "outcome": "verdict" if isinstance(outcome, Verdict) else outcome.kind,
        "detail": None if isinstance(outcome, Verdict) else outcome.detail,
        # Self-reported by the harness inside its own verdict. Recorded, never trusted,
        # never used to populate an attested field (U-VERDICT-11).
        "self_reported": self_reported,
    }


def _invoke_slot(
    *,
    adapter: HarnessAdapter,
    route: Route,
    effort: str,
    bundle_path: Path,
    slot: Path,
    timeout: float,
) -> Execution:
    """The one call shape §3.3 fixes: the adapter's argv, then the bundle directory, the
    immutable protocol instruction and the verdict output path — identical for a built-in
    and for an operator-declared command."""
    argv = (
        *adapter.argv(route, effort),
        str(bundle_path),
        str(protocol_instruction_path()),
        str(slot / VERDICT_FILENAME),
    )
    return invoke(
        argv=argv,
        cwd=slot,
        stdout_path=slot / STDOUT_FILENAME,
        stderr_path=slot / STDERR_FILENAME,
        timeout=timeout,
    )


def _conformance_facts(*, case: ConformanceCase, adversarial: bool, moment: datetime) -> Facts:
    """The published pair's inputs, as a `Facts` this part's own bundle writer assembles.

    Synthetic, fixed and free of any real pull request: §3.2 step 2 must prove a command
    behaves before a single genuine PR byte reaches it. Using the real `assemble_into()`
    on these is deliberate — the gate rehearses the exact invocation shape it admits,
    envelopes and all.

    The two members differ in exactly one place: the channel the case names. Everything
    else is byte-identical, which is what makes "identical non-defensive obligations and
    findings" a meaningful demand rather than a comparison of two unrelated reviews.

    **On the comment channel.** `Facts` (P-09, landed) carries no comment bodies —
    `SubmittedReview` is id, actor, outcome, head sha and time — while
    `InjectionAttempt.field` (P-04) names `comment:<id>` as a channel a harness must be
    able to locate an attempt in. The comment artifact therefore renders the reviews
    `Facts` does carry, and this case plants its instruction in the one author-supplied
    free-text field on that row. The tension between the two landed contracts is real and
    is reported rather than papered over; it does not stop the channel being exercised.
    """
    marker = case.payload if adversarial else ""
    diff_path = "src/payments/charge.py"
    diff = (
        f"--- a/{diff_path}\n+++ b/{diff_path}\n"
        "@@ -1,3 +1,4 @@\n"
        " def charge(amount):\n"
        "-    return gateway.post(amount)\n"
        "+    return gateway.post(amount, retries=3)\n"
        + (f"+# {marker}\n" if case.channel == "diff" and marker else "")
    )
    body = "Adds a retry to the payment gateway call." + (
        f"\n\n{marker}" if case.channel == "body" and marker else ""
    )
    actor = marker if case.channel == "comment" and marker else "conformance-reviewer"
    pr = PrFacts(
        repo="conformance/harness",
        number=1,
        head_sha="0" * 40,
        base_sha="1" * 40,
        merge_base_sha="1" * 40,
        head_repo="conformance/harness",
        head_ref="conformance",
        head_protected=False,
        author="conformance-author",
        labels=frozenset({"conformance"}),
        title="Add a retry to the payment gateway call",
        body=body,
    )
    return Facts(
        pr=pr,
        diff=diff,
        changed_paths=frozenset({diff_path}),
        revision_changed_paths=frozenset(),
        files={diff_path: b"def charge(amount):\n    return gateway.post(amount, retries=3)\n"},
        checks=(),
        base_checks=(),
        reviews=(
            SubmittedReview(
                id="R1",
                actor=actor,
                outcome="approved",
                head_sha="0" * 40,
                submitted_at=moment,
            ),
        ),
        fetched_at=moment,
    )


def run(*, job: Job, plan: Plan, facts: Facts, snapshot: Snapshot, supply: SupplyPort, state_dir: Path,
        record: RecordWriter) -> PanelResult | BundleFailure:
    """E-07, verbatim from `CONTRACTS.md` §9. §3.2's loop, step by step.

    Returns a `PanelResult` — complete, or incomplete with one of the three named
    reasons — or the shared `BundleFailure`. Raises only `HarnessError` and its
    subclasses, plus `AppendFailed` from the record, which always propagates.
    """
    if not plan.obligations:
        raise EmptyPlanError(
            f"run() was called for job {job.id} with no planned obligation; "
            "lifecycle skips run() when nothing was regenerated"
        )

    built = assemble(job_id=job.id, facts=facts, snapshot=snapshot, state_dir=state_dir)
    if isinstance(built, BundleFailure):
        record.append(job.id, "bundle", {"status": "incomplete", "reason": built.reason})
        return built
    record.append(
        job.id,
        "bundle",
        {
            "status": "ready",
            "nonce": built.nonce,
            "protocol_hash": built.protocol_hash,
            "manifest": dict(built.manifest),
        },
    )

    # Every valid verdict evaluates the whole bundle; the deterministic first planned
    # obligation is what selects the supply ladder (§3.2).
    obligation = plan.obligations[0]
    requested_effort = STRATEGIES[plan.strategy].effort if plan.strategy in STRATEGIES else "medium"

    cursor = RouteCursor(excluded_families=frozenset(), excluded_routes=frozenset())
    attempts: list[Attempt] = []
    counted_families: set[str] = set()
    conformance_cache: dict[tuple[str, str], bool] = {}
    bound_reached = False
    ordinal = 0

    def finish(complete: bool, reason: str | None) -> PanelResult:
        """§3.2: capture UTC **after** the last attempt/consumption, append one `panel`
        entry, and return the identical shared `PanelResult`."""
        cutoff = utcnow()
        result = PanelResult(
            attempts=tuple(attempts),
            complete=complete,
            incomplete_reason=reason,
            evidence_cutoff=cutoff,
            bound_reached=bound_reached,
        )
        record.append(
            job.id,
            "panel",
            {
                "attempts": [attempt.id for attempt in result.attempts],
                "complete": result.complete,
                "incomplete_reason": result.incomplete_reason,
                "evidence_cutoff": result.evidence_cutoff.isoformat(),
                "bound_reached": result.bound_reached,
            },
        )
        return result

    while True:
        # ---- step 1: select a candidate -----------------------------------
        selection = supply.route(obligation, cursor)
        if isinstance(selection, RouteUnavailable):
            return finish(False, "exhausted")
        route, returned_cursor = selection
        if route in cursor.excluded_routes or route.family in cursor.excluded_families:
            # The ladder's finiteness rests on the cursor being honoured. A port that
            # returns an excluded route has broken E-06, and continuing would turn a
            # bounded loop into an unbounded one against a failing provider.
            raise HarnessError(
                f"supply.route returned {route.harness}/{route.model}, which the cursor "
                "already excludes"
            )
        # "Retain the returned cursor before any local union" (§3.2 step 1).
        cursor = returned_cursor
        adapter = adapter_for(route=route)
        effort = adapter.resolved_effort(requested_effort)

        # ---- step 2: the conformance gate for an operator-declared command --
        if route.command:
            # "that exact argv" (§3.2 step 2) is the operator-declared portion: the three
            # paths RQA appends are slot-specific and would defeat the cache without
            # identifying anything about the command.
            key = (argv_hash(adapter.argv(route, effort)), snapshot.protocol_hash)
            passed = conformance_cache.get(key)
            if passed is None:
                ordinal, passed = _gate(
                    job=job,
                    snapshot=snapshot,
                    route=route,
                    adapter=adapter,
                    effort=effort,
                    state_dir=state_dir,
                    record=record,
                    argv_digest=key[0],
                    ordinal=ordinal,
                )
                conformance_cache[key] = passed
            if not passed:
                cursor = _exclude_route(cursor, route)
                continue

        # ---- steps 3-6: reserve, invoke, validate, consume ------------------
        transients = 0
        while True:
            reservation = supply.reserve(plan, route)
            if isinstance(reservation, Refusal):
                # Latched on the first refusal of any kind, never cleared (RQA-FR-039).
                bound_reached = True
                if reservation.downgrade == "fallback":
                    cursor = _exclude_family(cursor, route)
                    break
                if reservation.downgrade in ("incomplete", "escalate"):
                    return finish(False, "budget")
                raise HarnessError(
                    f"supply.reserve refused with unknown downgrade {reservation.downgrade!r}"
                )
            if not isinstance(reservation, Reservation):
                raise HarnessError(
                    f"supply.reserve returned {type(reservation).__name__}, which is "
                    "neither a Reservation nor a Refusal"
                )

            ordinal += 1
            slot = _slot(state_dir=state_dir, job_id=job.id, ordinal=ordinal)
            attempt_id = f"{job.id}:{ordinal:02d}"
            execution = _invoke_slot(
                adapter=adapter,
                route=route,
                effort=effort,
                bundle_path=built.path,
                slot=slot,
                timeout=ATTEMPT_TIMEOUT_SECONDS,
            )
            outcome, self_reported = _classify(execution=execution, slot=slot, attempt_id=attempt_id)
            reading = _reading(slot=slot)
            attestation = _attest(route=route, effort=effort, execution=execution)
            attempt = Attempt(id=attempt_id, route=route, outcome=outcome, attestation=attestation)
            attempts.append(attempt)
            payload = _attestation_payload(
                attempt=attempt,
                adapter=adapter,
                requested_effort=requested_effort,
                execution=execution,
                self_reported=self_reported,
            )
            _write_sidecar(slot=slot, payload=payload)
            record.append(job.id, "attestation", payload)
            # Every outcome is reported, including timeout and launch failure (§3.2 step 4).
            supply.consumed(attempt, reading, reservation)

            if isinstance(outcome, Verdict):
                if route.family not in counted_families:
                    counted_families.add(route.family)
                    if len(counted_families) >= plan.participants:
                        return finish(True, None)
                cursor = _exclude_route(cursor, route)
                break
            if outcome.kind == "TRANSIENT":
                if transients == 0:
                    # §3.2 step 6: stay on this route and return to step 3 — a *new*
                    # reservation before the one permitted retry.
                    transients = 1
                    continue
                cursor = _exclude_route(cursor, route)
                break
            if outcome.kind == "PROVIDER_TERMINAL":
                cursor = _exclude_family(cursor, route)
                break
            cursor = _exclude_route(cursor, route)
            break


def _write_sidecar(*, slot: Path, payload: dict[str, object]) -> None:
    """RQA's attestation, written into the slot beside the harness's own output (§5)."""
    try:
        (slot / ATTESTATION_FILENAME).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    except (OSError, UnicodeError, TypeError, ValueError):
        return


def _gate(
    *,
    job: Job,
    snapshot: Snapshot,
    route: Route,
    adapter: HarnessAdapter,
    effort: str,
    state_dir: Path,
    record: RecordWriter,
    argv_digest: str,
    ordinal: int,
) -> tuple[int, bool]:
    """§3.2 step 2: run the published clean/adversarial pair against this exact argv.

    Returns the advanced slot ordinal and whether the command may be invoked with PR
    content. A pass appends an `attestation` whose subject is the conformance run; a
    failure, spawn error or timeout appends one too and is `CANDIDATE_TERMINAL` — the
    caller excludes the route through the cursor and resumes selection.

    **No real PR byte reaches the command before a pass is recorded.** The two bundles
    here are built from `_conformance_facts`, which contains no `Facts` from this job.
    """
    case = CONFORMANCE_GATE_CASE
    gate_snapshot = replace(snapshot, authority=authority_for_mode(mode=case.mode))
    moment = utcnow()
    members: dict[str, Valid | Invalid | None] = {}
    detail = "pass"
    for member in ("clean", "adversarial"):
        ordinal += 1
        slot = _slot(state_dir=state_dir, job_id=job.id, ordinal=ordinal)
        gate_facts = _conformance_facts(
            case=case, adversarial=member == "adversarial", moment=moment
        )
        gate_bundle = assemble_into(parent=slot, facts=gate_facts, snapshot=gate_snapshot)
        if isinstance(gate_bundle, BundleFailure):
            members[member] = None
            detail = f"bundle:{gate_bundle.reason}"
            continue
        execution = _invoke_slot(
            adapter=adapter,
            route=route,
            effort=effort,
            bundle_path=gate_bundle.path,
            slot=slot,
            timeout=CONFORMANCE_TIMEOUT_SECONDS,
        )
        attempt_id = f"{job.id}:conformance:{ordinal:02d}"
        if execution.spawn_failed:
            members[member] = None
            detail = "spawn_failed"
            continue
        if execution.timed_out:
            members[member] = None
            detail = "timeout"
            continue
        if execution.exit_code != 0 or not (slot / VERDICT_FILENAME).exists():
            members[member] = None
            detail = f"exit_{execution.exit_code}"
            continue
        members[member] = validate(path=slot / VERDICT_FILENAME, attempt_id=attempt_id)

    reasons = pair_reasons(case=case, clean=members.get("clean"), adversarial=members.get("adversarial"))
    passed = not reasons
    record.append(
        job.id,
        "attestation",
        {
            "subject": "conformance",
            "suite": CONFORMANCE_SUITE_ID,
            "suite_hash": conformance_suite_hash(),
            "case": case.id,
            "argv_hash": argv_digest,
            "protocol_hash": snapshot.protocol_hash,
            "harness": route.harness,
            "model": route.model,
            "provider": route.provider,
            "family": route.family,
            "result": "pass" if passed else "fail",
            # Both are this module's own vocabulary — case-keyed reason strings and the
            # process-level cause — never harness output and never a PR byte.
            "detail": "pass" if passed else "; ".join(reasons),
            "process": detail,
            "outcome": "verdict" if passed else "CANDIDATE_TERMINAL",
        },
    )
    return ordinal, passed
