"""Corroboration, envelope detection, and mechanical classification —
`code/P-07-judgement.md` §3 steps 6-8.

Pure functions and value builders only; every decision about what a finding
*means* for the judgement (which sets it lands in, what disposition follows)
is `judge.py`'s to make. This module never raises `JudgementError` itself —
`is_malformed` reports a fact, `judge.py` decides what to do with it — so it
carries no dependency back on `judge.py` and the package has no import cycle.

Synthetic findings (`build_injection_finding`, `build_envelope_finding`,
`build_suspicious_clean_finding`) are the mechanical conversion `CONTRACTS.md`
§12.2 requires: "P-07 deterministically converts every item into a blocking
`EVIDENCE` finding before authority or repository policy is considered."
None of the three ever inspects PR content for phrases or keywords — the
envelope scan is a structural bracket-balance count over the nonce-envelope
grammar (`<<<label:nonce>>>` / `<<<END:label:nonce>>>`), never a semantic
read of what is inside it.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping

from rqa.contracts import MECHANICAL_GROUP, Category, Finding, InjectionAttempt, Location

__all__ = [
    "fingerprint",
    "is_malformed",
    "corroborating_families",
    "cited_pr_failing_check",
    "is_blocking_by_policy",
    "is_remediation_candidate",
    "build_injection_finding",
    "scan_envelope_breaks",
    "build_envelope_finding",
    "build_suspicious_clean_finding",
]

Fingerprint = tuple[tuple[str, ...], str, "int | None"]

#: The nonce-envelope grammar (`rqa.protocol.envelope`'s own wire format),
#: matched structurally — never a phrase list, never a semantic read.
_OPEN_MARKER = re.compile(r"<<<(?!END:)([^:<>]+):([^:<>]+)>>>")
_CLOSE_MARKER = re.compile(r"<<<END:([^:<>]+):([^:<>]+)>>>")


def fingerprint(finding: Finding) -> Fingerprint:
    """The exact §3 step 6 fingerprint, verbatim:
    `(tuple(sorted(category.value for category in categories)),
    location.path.casefold().strip(), location.line)`."""
    return (
        tuple(sorted(category.value for category in finding.categories)),
        finding.location.path.casefold().strip(),
        finding.location.line,
    )


def is_malformed(finding: Finding) -> bool:
    """A finding a validated verdict should never carry: no category, no
    location path, or no evidence text — §3 step 6's "supposedly validated
    malformed value"."""
    return (
        not finding.categories
        or not finding.location.path.strip()
        or not finding.evidence.strip()
    )


def corroborating_families(
    group: Iterable[Finding], *, attempt_family_by_id: Mapping[str, str]
) -> frozenset[str]:
    """Distinct attested provider families reporting this fingerprint group."""
    return frozenset(
        attempt_family_by_id[finding.source_attempt]
        for finding in group
        if finding.source_attempt in attempt_family_by_id
    )


def cited_pr_failing_check(evidence: str, *, pr_failing_checks: Iterable[str]) -> str | None:
    """The PR-attributed failing head check `evidence` cites, or `None`.

    The citation must appear in the finding's own evidence text, so a finding
    can never borrow credibility from an unrelated failing check.
    """
    haystack = evidence.casefold()
    for name in pr_failing_checks:
        if name and name.casefold() in haystack:
            return name
    return None


def is_blocking_by_policy(finding: Finding, *, blocking_categories: frozenset[Category]) -> bool:
    """§3 step 7 / `CONTRACTS.md` §11: a corroborated finding blocks when any of
    its categories blocks under policy."""
    return any(category in blocking_categories for category in finding.categories)


def is_remediation_candidate(
    finding: Finding,
    *,
    mechanical_categories: frozenset[Category],
    mechanical_tools: frozenset[str],
    captured_paths: frozenset[str],
) -> bool:
    """§3 step 7, corrected against `CONTRACTS.md` §11 (the seam rule: §11 wins
    where the part contract disagrees — `P-07-judgement.md` §3 step 7 omits
    this condition; see the handoff's Disclosures). Callers pass only
    corroborated findings — §7's "It is a remediation candidate only when..."
    shares the same antecedent ("a corroborated finding") as the blocking
    sentence before it.

    §11 verbatim: "its exact paths are present in the captured files" — a
    `Remedy` naming a path P-10 could never resolve inside the worktree is
    never eligible, even when every other condition holds.
    """
    if not (finding.categories <= MECHANICAL_GROUP):
        return False
    if not (finding.categories <= mechanical_categories):
        return False
    if finding.remedy is None:
        return False
    if not set(finding.remedy.paths) <= captured_paths:
        return False
    if finding.remedy.tool not in mechanical_tools:
        return False
    return finding.behaviour_changing is False


def build_injection_finding(*, attempt_id: str, injection: InjectionAttempt) -> Finding:
    """§3 step 8: one deterministic, immediately-corroborated, policy-independent
    blocking `EVIDENCE` finding per `InjectionAttempt`. The id covers the source
    attempt, field, span hash and reason; the evidence carries only the hash and
    reason, never the untrusted bytes.
    """
    digest = hashlib.sha256(
        f"{attempt_id}\x1f{injection.field}\x1f{injection.span_hash}\x1f{injection.reason}".encode()
    ).hexdigest()
    return Finding(
        id=f"injection:{digest}",
        categories=frozenset({Category.EVIDENCE}),
        extra_tags=frozenset({"injection_attempt"}),
        location=Location(path=injection.field, line=None),
        evidence=f"{injection.span_hash}: {injection.reason}",
        severity="blocker",
        remedy=None,
        behaviour_changing=True,
        source_attempt=attempt_id,
    )


def scan_envelope_breaks(fields: Mapping[str, str]) -> tuple[tuple[str, str, str, int, int], ...]:
    """`(field, label, nonce, opens, closes)` for every marker pair that is
    unbalanced (open/close counts disagree) or forged by order — an
    "unbalanced or forged nonce envelope" (§3 step 8). Purely structural:
    matches marker shape by exact grammar, never a phrase list or semantic
    read.

    Order detection agrees with the landed primitive rather than inventing a
    second rule: `rqa.protocol.envelope.extract` recovers content only when
    its first open marker precedes its last close marker
    (`end < start` -> `None`, i.e. no envelope at all); a close marker for a
    `(label, nonce)` pair that precedes every open marker for that same pair
    — `<<<END:label:nonce>>>` before `<<<label:nonce>>>` — is exactly that
    crossed case, so it is flagged here too, in addition to plain count
    mismatch (E-B3b-2).
    """
    breaks: list[tuple[str, str, str, int, int]] = []
    for field in sorted(fields):
        text = fields[field]
        open_positions: dict[tuple[str, str], list[int]] = {}
        close_positions: dict[tuple[str, str], list[int]] = {}
        for match in _OPEN_MARKER.finditer(text):
            key = (match.group(1), match.group(2))
            open_positions.setdefault(key, []).append(match.start())
        for match in _CLOSE_MARKER.finditer(text):
            key = (match.group(1), match.group(2))
            close_positions.setdefault(key, []).append(match.start())
        for key in sorted(set(open_positions) | set(close_positions)):
            opens = open_positions.get(key, [])
            closes = close_positions.get(key, [])
            open_count, close_count = len(opens), len(closes)
            count_mismatch = open_count != close_count
            order_violation = bool(opens) and bool(closes) and max(closes) < min(opens)
            if count_mismatch or order_violation:
                breaks.append((field, key[0], key[1], open_count, close_count))
    return tuple(breaks)


def build_envelope_finding(
    *, field: str, label: str, nonce: str, opens: int, closes: int
) -> Finding:
    """One deterministic, immediately-corroborated, policy-independent blocking
    `EVIDENCE` finding for one unbalanced/forged envelope marker pair (§3 step 8).

    `label` and `nonce` are captured directly from untrusted PR text by the
    marker regexes (§3 step 8: "its evidence contains only the hash/reason,
    never the untrusted bytes" — the same rule the injection finding follows).
    Neither is ever interpolated into `evidence`; only their digest and the
    structural open/close counts are.
    """
    marker_hash = hashlib.sha256(f"{label}\x1f{nonce}".encode()).hexdigest()
    digest = hashlib.sha256(
        f"{field}\x1f{label}\x1f{nonce}\x1f{opens}\x1f{closes}".encode()
    ).hexdigest()
    return Finding(
        id=f"envelope:{digest}",
        categories=frozenset({Category.EVIDENCE}),
        extra_tags=frozenset({"envelope_break"}),
        location=Location(path=field, line=None),
        evidence=f"unbalanced envelope marker {marker_hash}: opens={opens} closes={closes}",
        severity="blocker",
        remedy=None,
        behaviour_changing=True,
        source_attempt="",
    )


def build_suspicious_clean_finding(*, job_id: str) -> Finding:
    """The defense-in-depth `suspicious_clean_verdict` blocking `EVIDENCE`
    finding (§3 step 8 / `CONTRACTS.md` §12.4): fewer than two independent
    provider families reported an all-`VERIFIED`, zero-finding result for an
    evidence-bearing changed path. Deterministic per job, so two runs over the
    same job with the same inputs render byte-identically (T1).
    """
    digest = hashlib.sha256(f"suspicious_clean_verdict\x1f{job_id}".encode()).hexdigest()
    return Finding(
        id=f"suspicious_clean_verdict:{digest}",
        categories=frozenset({Category.EVIDENCE}),
        extra_tags=frozenset({"suspicious_clean_verdict"}),
        location=Location(path=f"job:{job_id}", line=None),
        evidence="fewer than two independent provider families reported a clean result",
        severity="blocker",
        remedy=None,
        behaviour_changing=True,
        source_attempt="",
    )
