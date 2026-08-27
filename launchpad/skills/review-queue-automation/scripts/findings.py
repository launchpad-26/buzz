"""Finding corroboration for review-queue-automation.

A model asserting a defect is not sufficient grounds to formally block a pull
request. This module decides which findings are *corroborated* well enough to
support a change request, and records why.

Corroboration rule (operator-selected):

    A blocking finding is verified when EITHER
      (a) the same finding is reported by two DISTINCT provider families, OR
      (b) it is reported by one family AND cites a check that actually failed.

Everything else is `unverified` and must escalate to a human instead of becoming
an authoritative action. Findings are matched by a deterministic fingerprint so
two models describing the same defect in different prose still corroborate.

This module is pure: no GitHub, no model calls, no state writes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

#: Severities that may support a formal change request. Deliberately narrow;
#: `high` and below are advisory unless an operator widens this in policy.
DEFAULT_BLOCKING_SEVERITIES = ("blocker",)

#: Check conclusions that count as a real failure for corroboration (b).
FAILING_CONCLUSIONS = frozenset({"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STALE"})

TWO_FAMILIES = "two_provider_families"
CHECK_BACKED = "check_failure_corroborated"

_WS = re.compile(r"\s+")


@dataclass(frozen=True)
class Finding:
    severity: str
    title: str
    location: str
    evidence: str
    primary_source: str
    model: str
    provider_family: str

    @property
    def fingerprint(self) -> tuple[str, str]:
        """Match the same defect across differently-worded reports.

        Severity plus normalised location is deliberately coarse: two reviewers
        naming the same line are treated as the same defect even when their
        titles differ, which is the point of corroboration.
        """
        return (self.severity.strip().lower(), _normalise_location(self.location))


@dataclass
class Corroboration:
    finding: Finding
    verified: bool
    basis: str = ""
    families: tuple[str, ...] = field(default_factory=tuple)
    citation: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.finding.severity,
            "title": self.finding.title,
            "location": self.finding.location,
            "verified": self.verified,
            "basis": self.basis,
            "provider_families": list(self.families),
            "citation": self.citation,
        }


def _normalise_location(location: str) -> str:
    return _WS.sub("", (location or "").strip().lower())


def _clean(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def extract_findings(verdicts: list[dict[str, Any]]) -> list[Finding]:
    """Pull well-formed findings out of validated verdicts.

    A finding missing evidence or a primary source is dropped: it cannot support
    an authoritative action, and silently treating it as actionable is exactly the
    failure this module exists to prevent.
    """
    out: list[Finding] = []
    for verdict in verdicts or []:
        model = _clean(verdict.get("model"))
        family = _clean(verdict.get("provider_family"))
        for raw in verdict.get("findings") or []:
            if not isinstance(raw, dict):
                continue
            severity = _clean(raw.get("severity")).lower()
            location = _clean(raw.get("location"))
            evidence = _clean(raw.get("evidence"))
            primary_source = _clean(raw.get("primary_source"))
            if not (severity and location and evidence and primary_source):
                continue
            out.append(Finding(
                severity=severity,
                title=_clean(raw.get("title")),
                location=location,
                evidence=evidence,
                primary_source=primary_source,
                model=model,
                provider_family=family,
            ))
    return out


def failing_check_names(checks: list[dict[str, Any]] | None) -> list[str]:
    """Names of checks whose conclusion is a genuine failure."""
    names: list[str] = []
    for check in checks or []:
        if not isinstance(check, dict):
            continue
        conclusion = _clean(check.get("conclusion")).upper()
        if conclusion in FAILING_CONCLUSIONS:
            name = _clean(check.get("name")) or _clean(check.get("id"))
            if name:
                names.append(name)
    return names


def _cited_failing_check(finding: Finding, failing: list[str]) -> str:
    """Return the failing check this finding cites, or empty string.

    The citation must appear in the finding's own evidence or primary source, so
    a finding cannot borrow credibility from an unrelated failing check.
    """
    haystack = f"{finding.primary_source}\n{finding.evidence}".lower()
    for name in failing:
        if name.lower() in haystack:
            return name
    return ""


def corroborate(
    verdicts: list[dict[str, Any]],
    *,
    checks: list[dict[str, Any]] | None = None,
    blocking_severities: tuple[str, ...] | list[str] = DEFAULT_BLOCKING_SEVERITIES,
) -> list[Corroboration]:
    """Classify each distinct blocking finding as verified or unverified.

    Returns one entry per distinct fingerprint, so a defect reported twice yields
    a single corroborated result rather than two.
    """
    blocking = {s.strip().lower() for s in blocking_severities}
    failing = failing_check_names(checks)

    grouped: dict[tuple[str, str], list[Finding]] = {}
    for finding in extract_findings(verdicts):
        if finding.severity not in blocking:
            continue
        grouped.setdefault(finding.fingerprint, []).append(finding)

    results: list[Corroboration] = []
    for _fingerprint, group in sorted(grouped.items()):
        families = tuple(sorted({f.provider_family for f in group if f.provider_family}))
        representative = group[0]

        # (a) two distinct provider families independently reported it
        if len(families) >= 2:
            results.append(Corroboration(
                finding=representative, verified=True,
                basis=TWO_FAMILIES, families=families,
            ))
            continue

        # (b) one family, but it cites a check that actually failed
        citation = ""
        for finding in group:
            citation = _cited_failing_check(finding, failing)
            if citation:
                representative = finding
                break
        if citation:
            results.append(Corroboration(
                finding=representative, verified=True,
                basis=CHECK_BACKED, families=families, citation=citation,
            ))
            continue

        results.append(Corroboration(
            finding=representative, verified=False,
            basis="single_family_uncorroborated", families=families,
        ))
    return results


def verified_blockers(
    verdicts: list[dict[str, Any]],
    *,
    checks: list[dict[str, Any]] | None = None,
    blocking_severities: tuple[str, ...] | list[str] = DEFAULT_BLOCKING_SEVERITIES,
) -> list[Corroboration]:
    """Only the corroborated blocking findings."""
    return [c for c in corroborate(
        verdicts, checks=checks, blocking_severities=blocking_severities
    ) if c.verified]


def blocking_summary(results: list[Corroboration]) -> dict[str, Any]:
    """Compact, auditable summary for logs, human packets and PR bodies."""
    verified = [r for r in results if r.verified]
    unverified = [r for r in results if not r.verified]
    return {
        "verified_count": len(verified),
        "unverified_count": len(unverified),
        "verified": [r.as_dict() for r in verified],
        "unverified": [r.as_dict() for r in unverified],
    }
