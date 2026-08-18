"""The review agent's per-dimension output contract, in code.

Implements launchpad-26/buzz#117 (STEP 2). The normative contract is FINDINGS.md in
this directory; this module is that document made executable. Where the two
disagree, the document wins and this file is the bug.

Pure dataclasses and validation over already-produced data: no subprocess, no
network, no model call. A dimension's raw JSON output is parsed through this module
(``parse``/``Report.from_dict``), and a merged document — the whole-run structure
FINDINGS.md's "The merged document" section defines — is checked against every rule
that document states normatively (``validate``), before #118 (adjudication) or #119
(publish) ever see it.

Severity is imported from ``review.py``, never redeclared here — FINDINGS.md
§ Severity is explicit that a second copy of the four-value ladder drifts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from review import SEVERITY_ORDER

#: The three legal shapes containment findings may declare. FINDINGS.md
#: § "Where containment findings live" names these three and no others.
_CONTAINMENT_KINDS = frozenset({"delimiter_forge", "delimiter_lookalike", "injection_attempt"})


def finding_id(
    dimension: str,
    anchor: str,
    file: str | None,
    line: int | None,
    entry_point: str | None,
    defect: str,
    evidence: str | None,
) -> str:
    """A stable id for a finding, per FINDINGS.md § ``finding_id``.

    ``repr`` of the whole tuple, not a plain join, so that ``None`` vs the string
    ``"None"``, or a field boundary landing inside another field's text, can never
    collide two distinct findings onto one hash.

    Sliced to 16 hex chars (64 bits) rather than ``make_nonce``'s 32: this id only
    needs to be unlikely to collide among one PR's findings, not to resist an
    adversary the way a run nonce must, so it borrows the same "hash and slice"
    shape without the same length. A judgement call, made explicit here so a later
    reader does not assume 16 was arbitrary.
    """
    payload = repr((dimension, anchor, file, line, entry_point, defect, evidence))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class Finding:
    """One dimension's finding record. Ten fields, per FINDINGS.md § The finding record.

    A plain data carrier, like ``contain.Finding`` — it does not validate itself.
    Structural checking of a finding already in dict form is ``validate``'s job.
    """

    dimension: str
    severity: str
    anchor: str
    file: str | None
    line: int | None
    defect: str
    failure: str
    finding_id: str
    entry_point: str | None
    evidence: str | None

    def as_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "severity": self.severity,
            "anchor": self.anchor,
            "file": self.file,
            "line": self.line,
            "defect": self.defect,
            "failure": self.failure,
            "finding_id": self.finding_id,
            "entry_point": self.entry_point,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Finding:
        return cls(
            dimension=d["dimension"],
            severity=d["severity"],
            anchor=d["anchor"],
            file=d["file"],
            line=d["line"],
            defect=d["defect"],
            failure=d["failure"],
            finding_id=d["finding_id"],
            entry_point=d["entry_point"],
            evidence=d["evidence"],
        )


@dataclass
class Report:
    """One dimension's report envelope. Eleven fields, per FINDINGS.md § The report envelope.

    Field order matches the contract's table, and ``completion_marker`` — last both
    here and in ``as_dict()`` — stays last on purpose: a report truncated mid-emit
    must lose the marker before it loses anything else.
    """

    schema_version: int
    dimension: str
    pr: int
    merge_base_sha: str
    head_sha: str
    status: str
    outcome: str | None
    error: dict | None
    findings: list[Finding]
    findings_count: int
    completion_marker: str

    def as_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "dimension": self.dimension,
            "pr": self.pr,
            "merge_base_sha": self.merge_base_sha,
            "head_sha": self.head_sha,
            "status": self.status,
            "outcome": self.outcome,
            "error": self.error,
            "findings": [f.as_dict() for f in self.findings],
            "findings_count": self.findings_count,
            "completion_marker": self.completion_marker,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Report:
        return cls(
            schema_version=d["schema_version"],
            dimension=d["dimension"],
            pr=d["pr"],
            merge_base_sha=d["merge_base_sha"],
            head_sha=d["head_sha"],
            status=d["status"],
            outcome=d["outcome"],
            error=d["error"],
            findings=[Finding.from_dict(fd) for fd in d["findings"]],
            findings_count=d["findings_count"],
            completion_marker=d["completion_marker"],
        )


def parse(text: str) -> Report:
    """Parse one dimension's raw JSON output into a ``Report``.

    ``json.loads`` raises on malformed JSON, and ``Report.from_dict``/
    ``Finding.from_dict`` raise ``KeyError`` on a missing required key — both
    propagate. This function's contract is "parse what a well-formed reviewer
    emitted"; a *malformed* structure that still parses as JSON is ``validate``'s
    job, run against the dict directly rather than through this function.
    """
    return Report.from_dict(json.loads(text))


def _validate_finding(
    finding: object, report_label: str, index: int, entry_points: frozenset[str]
) -> list[str]:
    label = f"{report_label} finding[{index}]"
    # A malformed document may hold anything where a finding object belongs (a bare
    # string, a number). Every field access below assumes a dict, so that assumption
    # is checked once, here, rather than trusted at each of the six call sites below.
    if not isinstance(finding, dict):
        return [f"{label}: expected an object, got {type(finding).__name__}"]

    violations: list[str] = []

    dimension_field = finding.get("dimension")
    if not isinstance(dimension_field, str) or not dimension_field:
        violations.append(f"{label}: dimension must be a non-empty string")

    anchor = finding.get("anchor")
    file = finding.get("file")
    line = finding.get("line")

    if anchor == "pr":
        if file is not None:
            violations.append(f"{label}: anchor 'pr' requires file to be null, got {file!r}")
        if line is not None:
            violations.append(f"{label}: anchor 'pr' requires line to be null, got {line!r}")
    elif anchor == "file":
        if file is None:
            violations.append(f"{label}: anchor 'file' requires a non-null file")
        if line is not None:
            violations.append(f"{label}: anchor 'file' requires line to be null, got {line!r}")
    elif anchor == "line":
        if file is None:
            violations.append(f"{label}: anchor 'line' requires a non-null file")
        if line is None:
            violations.append(f"{label}: anchor 'line' requires a non-null line")
    else:
        violations.append(f"{label}: anchor must be one of 'line', 'file', 'pr', got {anchor!r}")

    severity = finding.get("severity")
    if not isinstance(severity, str):
        # ``severity not in SEVERITY_ORDER`` requires a hashable value, same as the
        # entry_point guard above — an unhashable severity (a dict, a list) would
        # raise TypeError before this function could report it.
        violations.append(f"{label}: severity must be a string, got {type(severity).__name__}")
    elif severity not in SEVERITY_ORDER:
        violations.append(f"{label}: severity {severity!r} is not a key of SEVERITY_ORDER")

    defect_field = finding.get("defect")
    if not defect_field:
        violations.append(f"{label}: defect must be non-empty")
    if not finding.get("failure"):
        violations.append(f"{label}: failure must be non-empty")

    entry_point = finding.get("entry_point")
    evidence = finding.get("evidence")
    if entry_point is not None:
        if not isinstance(entry_point, str):
            # ``entry_point not in entry_points`` requires a hashable value —
            # an unhashable entry_point (a dict, a list) would raise TypeError
            # before this function could report it, the same "never raises on
            # malformed input" contract as the container-shape guards above.
            violations.append(
                f"{label}: entry_point must be a string or null, got "
                f"{type(entry_point).__name__}"
            )
        elif entry_point not in entry_points:
            violations.append(
                f"{label}: entry_point {entry_point!r} is not one of contain.ENTRY_POINTS"
            )
        if not evidence:
            violations.append(
                f"{label}: evidence must be set (non-null, non-empty) when entry_point is set"
            )
    elif evidence is not None:
        violations.append(f"{label}: evidence must be null when entry_point is null")

    finding_id_field = finding.get("finding_id")
    if not isinstance(finding_id_field, str) or not finding_id_field:
        violations.append(f"{label}: finding_id must be a non-empty string")
    else:
        # The stronger check FINDINGS.md's stability claim actually rests on:
        # #118 attaches one verdict per finding_id, so an id that does not match
        # what its own seven fields hash to is not stable, it is just present.
        # ``finding_id()`` is safe to call on raw, unvalidated field values here —
        # it only ever feeds them through ``repr()`` before hashing, so it cannot
        # raise regardless of what type any of them turned out to be.
        expected_id = finding_id(
            dimension_field, anchor, file, line, entry_point, defect_field, evidence
        )
        if finding_id_field != expected_id:
            violations.append(
                f"{label}: finding_id {finding_id_field!r} does not match the id "
                f"recomputed from this finding's own fields ({expected_id!r})"
            )

    return violations


def _validate_report(
    report: object, index: int, document_nonce: object, entry_points: frozenset[str]
) -> list[str]:
    if not isinstance(report, dict):
        return [f"document.reports[{index}]: expected an object, got {type(report).__name__}"]

    dimension = report.get("dimension")
    if dimension is None:
        # No dimension to name the report by, so the label falls back to its
        # position — and the missing key is its own violation, not just a symptom
        # readers would otherwise have to infer from a confusing marker mismatch
        # further down.
        label = f"document.reports[{index}]"
        violations: list[str] = [f"{label}: missing required key 'dimension'"]
    else:
        label = f"report {dimension!r}"
        violations = []

    for key in ("schema_version", "pr", "merge_base_sha", "head_sha"):
        if key not in report:
            violations.append(f"{label}: missing required key {key!r}")

    if dimension == "containment":
        violations.append(f"{label}: dimension may not be the reserved slug 'containment'")

    findings_raw = report.get("findings", [])
    if not isinstance(findings_raw, list):
        # ``report["findings"]: null`` is the confirmed crash: ``.get(..., [])``
        # only substitutes the default for an ABSENT key, not an explicit null, so
        # ``len(findings)`` below would raise on anything but a real list.
        violations.append(f"{label}: findings must be an array, got {type(findings_raw).__name__}")
        findings: list = []
    else:
        findings = findings_raw

    findings_count = report.get("findings_count")
    if findings_count != len(findings):
        violations.append(
            f"{label}: findings_count ({findings_count!r}) does not equal "
            f"len(findings) ({len(findings)})"
        )

    status = report.get("status")
    outcome = report.get("outcome")
    error = report.get("error")
    if status == "complete":
        if outcome is None or error is not None:
            violations.append(f"{label}: status 'complete' requires outcome set and error null")
        # Independent of the mutual-exclusivity check above: outcome may be SET
        # (so the check above passes) and still be neither legal value.
        if outcome is not None and outcome not in ("clean", "findings"):
            violations.append(
                f"{label}: outcome must be 'clean' or 'findings' when status is "
                f"'complete', got {outcome!r}"
            )
    elif status == "failed":
        if error is None or outcome is not None:
            violations.append(f"{label}: status 'failed' requires error set and outcome null")
    else:
        violations.append(f"{label}: status must be 'complete' or 'failed', got {status!r}")

    if outcome == "clean" and findings:
        violations.append(f"{label}: outcome 'clean' requires an empty findings array")
    if outcome == "findings" and not findings:
        violations.append(f"{label}: outcome 'findings' requires a non-empty findings array")

    keys = list(report.keys())
    if "completion_marker" not in report:
        violations.append(f"{label}: missing 'completion_marker'")
    elif keys[-1] != "completion_marker":
        violations.append(
            f"{label}: completion_marker must be the last key, found last key {keys[-1]!r}"
        )
    else:
        marker = report["completion_marker"]
        parts = marker.split(":", 2) if isinstance(marker, str) else []
        if not marker or not isinstance(marker, str) or parts[0] != "BUZZ-DIMENSION-COMPLETE" or len(parts) != 3:
            violations.append(f"{label}: completion_marker is malformed: {marker!r}")
        else:
            _, marker_dimension, marker_nonce = parts
            if marker_dimension != dimension:
                violations.append(
                    f"{label}: completion_marker dimension {marker_dimension!r} does not "
                    f"match report dimension {dimension!r}"
                )
            if marker_nonce != document_nonce:
                violations.append(f"{label}: completion_marker nonce does not match document nonce")

    for finding_index, finding in enumerate(findings):
        violations.extend(_validate_finding(finding, label, finding_index, entry_points))

    return violations


def validate(document: dict) -> list[str]:
    """Every violation in a merged document, per FINDINGS.md — never raises, never stops early.

    Takes a plain ``dict`` rather than a dataclass specifically so the original JSON
    key ORDER survives (``json.loads`` preserves object key order), which is what
    lets the ``completion_marker``-must-be-last rule be checked structurally instead
    of by convention.

    ``contain`` is imported here, locally, rather than at module scope — this module
    has no other reason to import it, and the constraint on this file is that
    ``contain``/``fetch`` are not module-scope dependencies of it. ``contain.py``'s
    own ``render()`` does the same local-import for the same reason.

    Every container assumed below (``containment``, ``states``, ``reports``, a
    finding array, an array entry) is type-checked before being treated as its
    expected shape. A malformed document is exactly the input this function exists
    to describe with a violation string, not the input it crashes on — the
    docstring's "never raises" is a contract on every branch, not just the obvious
    ones.
    """
    import contain

    entry_points = frozenset(contain.ENTRY_POINTS)
    violations: list[str] = []

    for key in ("pr", "merge_base_sha", "head_sha", "reports"):
        if key not in document:
            violations.append(f"document: missing required key {key!r}")

    nonce = document.get("nonce")
    if not nonce:
        violations.append("document: missing or empty top-level 'nonce'")

    containment = document.get("containment")
    if containment is None:
        violations.append("document: missing 'containment' key")
    elif not isinstance(containment, dict):
        violations.append(
            f"document.containment: expected an object, got {type(containment).__name__}"
        )
    else:
        states = containment.get("states")
        if states is None:
            violations.append("document.containment: missing 'states' key")
        elif not isinstance(states, dict):
            violations.append(
                f"document.containment.states: expected an object, got {type(states).__name__}"
            )
        else:
            actual = set(states.keys())
            if actual != entry_points:
                missing = sorted(entry_points - actual)
                extra = sorted(actual - entry_points)
                detail = []
                if missing:
                    detail.append(f"missing {missing}")
                if extra:
                    detail.append(f"unexpected {extra}")
                violations.append(
                    "document.containment.states: keys must be exactly the seven "
                    f"contain.ENTRY_POINTS values ({'; '.join(detail)})"
                )

        containment_findings = containment.get("findings", [])
        if not isinstance(containment_findings, list):
            violations.append(
                "document.containment.findings: expected an array, got "
                f"{type(containment_findings).__name__}"
            )
        else:
            for index, cf in enumerate(containment_findings):
                if not isinstance(cf, dict):
                    violations.append(
                        f"document.containment.findings[{index}]: expected an object, got "
                        f"{type(cf).__name__}"
                    )
                    continue
                kind = cf.get("kind")
                if not isinstance(kind, str):
                    # Same unhashable-crash class as severity/entry_point: ``kind not
                    # in _CONTAINMENT_KINDS`` needs a hashable value first.
                    violations.append(
                        f"document.containment.findings[{index}]: kind must be a string, "
                        f"got {type(kind).__name__}"
                    )
                elif kind not in _CONTAINMENT_KINDS:
                    violations.append(
                        f"document.containment.findings[{index}]: kind {kind!r} is not one of "
                        f"{sorted(_CONTAINMENT_KINDS)}"
                    )

    reports_raw = document.get("reports", [])
    if not isinstance(reports_raw, list):
        violations.append(f"document.reports: expected an array, got {type(reports_raw).__name__}")
    else:
        if not reports_raw:
            # Indistinguishable from "every dimension ran and found nothing" if left
            # unchecked — exactly the reads-as-clean-when-incomplete ambiguity
            # FINDINGS.md argues against for outcome/findings, applied one level up:
            # zero reports means no dimension ran at all, not that all of them ran
            # clean.
            violations.append("document.reports: must not be empty — a run produces at least one report")
        for index, report in enumerate(reports_raw):
            violations.extend(_validate_report(report, index, nonce, entry_points))

    return violations
