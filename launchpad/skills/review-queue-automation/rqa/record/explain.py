"""`explain` / `explain_job` — E-17, `code/P-12-record.md` §3.3.

Reconstructs every RQA-FR-012 / CL-033 (AC06) element from `record_entries` alone:
no GitHub call, no model call, no network, no read of `jobs/<job>/trace.jsonl`, and
no read of any table another part owns (§7). This is the offline half of P-12 —
U-RESILIENCE-07's "read-only operator reconstruction of a job's outcome", carried
into this package, and U-DOCS-16's explain-procedure documentation, rewritten here
rather than left in `scripts/explain.py` (bin: U-DISPATCH-04's "Backup" citation of
that same file names no responsibility this module owns; nothing here backs up
anything, which is the deliberate absence that disposition records). U-VERDICT-17
("Versioned `risk-assessment.json` persistence", bin) is honoured the same way:
RQA-FR-012's reconstruction obligation is met by `explain` from the record alone,
so no separate `risk-assessment.json` file or reader exists here or anywhere else
in this package.

**What "trusted prefix" means for reconstruction, precisely.** `verify(job_id)`
walks the job's rows and returns `bad_seq` — the first sequence it stopped
trusting, or `None`. The rows this module reduces over are exactly
`row.seq < bad_seq` (or every row, when `bad_seq is None`) — never the rows at or
after a break. A legacy (migrated) row is never excluded on that basis alone: it
simply carries no chain to break, so it is readable, and its contribution is
honestly marked by `legacy=True` and `verified=False` rather than being dropped or
disguised as authenticated (§6: "never `verified=True` from `explain`, regardless
of how well-formed its content is").

**Disposition is read, never decided.** §7: "Does not decide a job's disposition."
`DISPOSITION_TABLE` is `flow-review-lifecycle.md` §4's closed 13-internal-state →
FR-016 table, applied to the *last* recorded `transition`'s `to_state` — the same
copy of a P-02-owned decision every other reconstruction in this module reads
rather than re-derives. `superseded` has no FR-016 value in that table (a
superseded job is never the one the disposition command answers for); an
`explain_job` call made directly against a superseded job's id renders its raw
`to_state` rather than forcing it into one of the six FR-016 values, since forcing
it would be a fabrication `explain` is not permitted to make.

**Field provenance, where §3.3's prose leaves the exact source implicit
(the contract's own words: "anything not stated is the implementer's choice,
provided the stated shape, behaviour and tests hold")**:

* `pr_revision` — the last `transition` row's `head_sha`.
* `protocol_hash` / `policy_version` / `snapshot_hash` — the last `plan` row's pins,
  exactly as §3.3 step 2 states ("the last `plan` supplies pins"); `None` when no
  `plan` row is in the trusted prefix.
* `reviewer_identity` / `harness` / `model` / `provider` — the ordered,
  de-duplicated `(harness, model, provider)` triples of every harness-shaped
  `attestation` row (a `harness` key, never a `login` key — §6 distinguishes the
  two capability-probe/harness-attempt attestation subjects by shape). For an AI
  review, `reviewer_identity` is the same ordered harness values: RQA's own
  attested "what performed the review" (RQA-NFR-032), never the untrusted
  `self_reported_identity` field. A terminal `decision` row overrides both:
  `reviewer_type="human"`, `reviewer_identity=(actor,)`. No attestation and no
  decision at all: `reviewer_type="none"`, `reviewer_identity=()`.
* `evidence` — the last `judgement` row's `obligations` mapping, rendered exactly
  as stored (obligation id → `EvidenceState` string).
* `findings` — the last `judgement` row's `findings`, each decorated with
  `blocking`/`corroborated` booleans from that same judgement's own id sets (T19).
* `decision_basis` — the last `judgement` row's `rendered_body`: the one
  judgement-owned prose field §6 adds to the payload, and the natural analogue of
  "why", since `Judgement` itself carries no separate `basis` field to re-export.
* `disposition` — `DISPOSITION_TABLE[last transition.to_state]`, not
  `judgement.disposition` — see above.

**`reused_from` never a pointer to ignore (§3.3 step 3).** A materialised current
judgement whose `reused_from` names a predecessor job walks that predecessor's own
trusted prefix (recursively, if the predecessor's own judgement was itself reused),
merges its harness-shaped attestations ahead of this job's own (oldest predecessor
first, then nearer predecessors, then this job's own, de-duplicated), and folds its
`verify` outcome into this job's `verified`/`hmac_checked`/`unverifiable`/`legacy`.
A missing predecessor, a predecessor with no judgement in its own trusted prefix, a
malformed `reused_from`, or a repeated job id (a cycle) all raise
`ReuseResolutionError` — never a guess, never a silent omission.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from rqa.contracts import ExplanationUnavailable, KeyStore
from rqa.record.keychain import OSKeyStore
from rqa.record.reader import AmbiguousHead, NoRecord, ResolvedJob, resolve_job
from rqa.record.store import StoredEntry, entries_for_job, is_legacy
from rqa.record.verify import UnverifiableSegment, VerifyResult, verify

__all__ = ["explain", "explain_job", "resolve_job", "Explanation", "ReuseResolutionError"]


class ReuseResolutionError(Exception):
    """A current judgement's `reused_from` chain cannot be resolved from trusted
    record rows: malformed/missing predecessor, missing source judgement or
    attestation, predecessor tamper before the cited evidence, or a cycle. It is a
    corrupt record reference, never a fabricated explanation."""


@dataclass(frozen=True)
class Explanation:
    job_id: str
    repo: str
    number: int
    # The twelve RQA-FR-012 / CL-033 (AC06) elements, in fit-criterion order:
    pr_revision: str
    protocol_hash: str | None
    policy_version: str | None
    reviewer_identity: tuple[str, ...]
    reviewer_type: Literal["ai", "human", "none"]
    harness: tuple[str, ...]
    model: tuple[str, ...]
    provider: tuple[str, ...]
    evidence: Mapping[str, str]
    findings: tuple[Mapping[str, Any], ...]
    decision_basis: str | None
    disposition: str
    # Supporting trust/rendering fields:
    snapshot_hash: str | None
    verified: bool
    hmac_checked: bool
    unverifiable: tuple[UnverifiableSegment, ...]
    truncated_at: int | None
    legacy: bool


#: `flow-review-lifecycle.md` §4's closed internal-state → FR-016 disposition
#: table. `superseded` carries no FR-016 value there (the disposition command never
#: answers for a superseded job); rendered as its own raw name rather than forced
#: into one of the six, since forcing it would be a fabrication.
DISPOSITION_TABLE: Mapping[str, str] = {
    "queued": "being reviewed",
    "claimed": "being reviewed",
    "planned": "being reviewed",
    "reviewing": "being reviewed",
    "judged": "being reviewed",
    "submitting": "being reviewed",
    "remediating": "awaiting remediation",
    "escalated": "awaiting human judgement",
    "changes_requested": "blocked",
    "approved": "review-complete",
    "merged": "review-complete",
    "stopped": "unable to progress",
    "superseded": "superseded",
}


def _readable(rows: tuple[StoredEntry, ...], bad_seq: int | None) -> list[StoredEntry]:
    if bad_seq is None:
        return list(rows)
    return [row for row in rows if row.seq < bad_seq]


def _last_payload_of_kind(rows: list[StoredEntry], kind: str) -> dict[str, Any] | None:
    for row in reversed(rows):
        if row.kind == kind:
            payload = json.loads(row.payload)
            return payload if isinstance(payload, dict) else None
    return None


def _harness_attestations(rows: list[StoredEntry]) -> list[tuple[str, str, str]]:
    """Every harness-shaped `attestation` row (a `harness` key, never a `login`
    key — §6), in seq order, as `(harness, model, provider)` triples."""
    triples: list[tuple[str, str, str]] = []
    for row in rows:
        if row.kind != "attestation":
            continue
        payload = json.loads(row.payload)
        if not isinstance(payload, dict) or "harness" not in payload:
            continue
        triples.append(
            (str(payload.get("harness", "")), str(payload.get("model", "")), str(payload.get("provider", "")))
        )
    return triples


def _dedup_triples(triples: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    ordered: list[tuple[str, str, str]] = []
    for triple in triples:
        if triple not in seen:
            seen.add(triple)
            ordered.append(triple)
    return ordered


@dataclass
class _Hop:
    """One job's contribution while walking a `reused_from` chain."""

    attestations: list[tuple[str, str, str]]
    verify_result: VerifyResult
    legacy_present: bool


def _walk_reuse_chain(
    connection: sqlite3.Connection, start_job_id: object, *, keystore: KeyStore
) -> list[_Hop]:
    """Follow `reused_from` links starting at `start_job_id`, oldest predecessor
    first. Raises `ReuseResolutionError` for every malformed, missing, cyclic, or
    judgement-less hop (§3.3 step 3).

    **Interim, not the pinned reference §3.3 describes.** §3.3 step 3 says to obtain
    "the predecessor judgement at the carried source sequence"; this resolves the
    predecessor's *latest* judgement in its own trusted prefix instead, because no
    carried sequence exists anywhere to read: `Judgement.reused_from`
    (`CONTRACTS.md` §6) is a bare job id, and `CarriedEvidence.source_judgement_seq`
    is `CarryOver`'s field (P-13's), never carried onto the judgement itself. The
    pinned `(job, seq)` reference this step calls for is tracked in **#2236**
    (a `CONTRACTS.md` §6 change plus `judge()`/`carry_over()` obligations); this
    accepted-interim behaviour does not change until that lands.
    """
    hops: list[_Hop] = []
    visited: set[str] = set()
    current = start_job_id
    while True:
        if not isinstance(current, str) or not current:
            raise ReuseResolutionError(f"malformed reused_from: {current!r}")
        if current in visited:
            raise ReuseResolutionError(f"reuse cycle detected at job {current!r}")
        visited.add(current)

        rows = entries_for_job(connection=connection, job=current)
        if not rows:
            raise ReuseResolutionError(f"predecessor job {current!r} has no record entries")

        vr = verify(connection, current, keystore=keystore)
        readable = _readable(rows, vr.bad_seq)
        # Interim (see the docstring above and #2236): the predecessor's *latest*
        # trusted judgement, not the one at a carried source sequence — no such
        # sequence is readable from `reused_from` (a bare job id) or from anything
        # else this payload carries.
        judgement = _last_payload_of_kind(readable, "judgement")
        if judgement is None:
            raise ReuseResolutionError(
                f"no judgement in predecessor job {current!r}'s trusted prefix"
            )

        hops.insert(
            0,
            _Hop(
                attestations=_harness_attestations(readable),
                verify_result=vr,
                legacy_present=any(is_legacy(entry=row) for row in readable),
            ),
        )

        next_link = judgement.get("reused_from")
        if next_link is None:
            return hops
        current = next_link


def explain_job(connection: sqlite3.Connection, job_id: str) -> Explanation | ExplanationUnavailable:
    """§3.3's reconstruction, named job first. Every branch returns or raises."""
    keystore: KeyStore = OSKeyStore()

    rows = entries_for_job(connection=connection, job=job_id)
    if not rows:
        return ExplanationUnavailable(repo="", number=0, reason="no_record")

    vr = verify(connection, job_id, keystore=keystore)
    readable = _readable(rows, vr.bad_seq)

    transition = _last_payload_of_kind(readable, "transition")
    repo = str(transition.get("repo", "")) if transition else ""
    number = int(transition.get("number", 0)) if transition else 0
    pr_revision = str(transition.get("head_sha", "")) if transition else ""
    disposition = (
        DISPOSITION_TABLE.get(str(transition.get("to_state", "")), str(transition.get("to_state", "")))
        if transition
        else "unknown"
    )

    plan = _last_payload_of_kind(readable, "plan")
    protocol_hash = plan.get("protocol_hash") if plan else None
    policy_version = plan.get("policy_version") if plan else None
    snapshot_hash = plan.get("snapshot_hash") if plan else None

    judgement = _last_payload_of_kind(readable, "judgement")
    evidence: Mapping[str, str] = dict(judgement.get("obligations", {})) if judgement else {}
    decision_basis = judgement.get("rendered_body") if judgement else None

    blocking_ids = set(judgement.get("blocking", [])) if judgement else set()
    corroborated_ids = set(judgement.get("corroborated", [])) if judgement else set()
    findings: tuple[Mapping[str, Any], ...] = tuple(
        {
            **finding,
            "blocking": finding.get("id") in blocking_ids,
            "corroborated": finding.get("id") in corroborated_ids,
        }
        for finding in (judgement.get("findings", []) if judgement else [])
    )

    local_attestations = _harness_attestations(readable)
    local_legacy_present = any(is_legacy(entry=row) for row in readable)

    hops: list[_Hop] = []
    reused_from = judgement.get("reused_from") if judgement else None
    if reused_from is not None:
        hops = _walk_reuse_chain(connection, reused_from, keystore=keystore)

    combined_attestations = _dedup_triples(
        [triple for hop in hops for triple in hop.attestations] + local_attestations
    )
    harness = tuple(triple[0] for triple in combined_attestations)
    model = tuple(triple[1] for triple in combined_attestations)
    provider = tuple(triple[2] for triple in combined_attestations)

    decision = _last_payload_of_kind(readable, "decision")
    if decision is not None:
        reviewer_type: Literal["ai", "human", "none"] = "human"
        actor = decision.get("actor")
        reviewer_identity: tuple[str, ...] = (str(actor),) if actor else ()
    elif combined_attestations:
        reviewer_type = "ai"
        reviewer_identity = harness
    else:
        reviewer_type = "none"
        reviewer_identity = ()

    local_hmac_checked = vr.ok and vr.unverifiable == ()
    local_verified = local_hmac_checked and not local_legacy_present
    hop_hmac_checked = [hop.verify_result.ok and hop.verify_result.unverifiable == () for hop in hops]
    hop_verified = [
        checked and not hop.legacy_present for checked, hop in zip(hop_hmac_checked, hops, strict=True)
    ]

    verified = local_verified and all(hop_verified)
    hmac_checked = local_hmac_checked and all(hop_hmac_checked)
    legacy = local_legacy_present or any(hop.legacy_present for hop in hops)
    unverifiable: tuple[UnverifiableSegment, ...] = tuple(vr.unverifiable) + tuple(
        segment for hop in hops for segment in hop.verify_result.unverifiable
    )

    return Explanation(
        job_id=job_id,
        repo=repo,
        number=number,
        pr_revision=pr_revision,
        protocol_hash=protocol_hash,
        policy_version=policy_version,
        reviewer_identity=reviewer_identity,
        reviewer_type=reviewer_type,
        harness=harness,
        model=model,
        provider=provider,
        evidence=evidence,
        findings=findings,
        decision_basis=decision_basis,
        disposition=disposition,
        snapshot_hash=snapshot_hash,
        verified=verified,
        hmac_checked=hmac_checked,
        unverifiable=unverifiable,
        truncated_at=vr.bad_seq,
        legacy=legacy,
    )


def explain(connection: sqlite3.Connection, repo: str, number: int) -> Explanation | ExplanationUnavailable:
    """§3.3: resolve the current head job for `(repo, number)`, then reconstruct it.

    Every ordinary absence/ambiguity case is a returned `ExplanationUnavailable`,
    never an exception; `ReuseResolutionError` is the one named reconstruction
    failure, and it propagates unmodified from `explain_job`.
    """
    resolved = resolve_job(connection, repo, number)
    if isinstance(resolved, NoRecord):
        return ExplanationUnavailable(repo=repo, number=number, reason="no_record")
    if isinstance(resolved, AmbiguousHead):
        return ExplanationUnavailable(repo=repo, number=number, reason="ambiguous_head")
    assert isinstance(resolved, ResolvedJob)

    result = explain_job(connection, resolved.job_id)
    if isinstance(result, ExplanationUnavailable):
        # `explain_job` cannot itself know `repo`/`number` when it has nothing to
        # read; `explain` does, and fills them in (§3.3).
        return ExplanationUnavailable(repo=repo, number=number, reason=result.reason)
    return result
