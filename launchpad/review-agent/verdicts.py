"""The adjudication stage's verdict contract, in code.

Implements launchpad-26/buzz#118 (STEP 2). The normative contract is
ADJUDICATION.md in this directory; this module is that document made
executable. Where the two disagree, the document wins and this file is the
bug.

Pure dataclasses and validation over an already-produced pair of documents: no
subprocess, no network, no model call. STEP 3's `run_adjudication.py` is the
process that reads a #117 merged document, adjudicates every finding with an
injected judge, and writes the adjudicated document back out; this module only
describes the shape of the six added finding fields and the nine
`adjudication` block keys, and checks the movement between the two documents
(`validate`).

Severity is imported from `review.py`, never redeclared here -- ADJUDICATION.md
is explicit that a second copy of the four-value ladder drifts, the same
reason FINDINGS.md gives and #117's `findings.py` already follows.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import findings
from review import SEVERITY_ORDER

#: The three legal verdicts. ADJUDICATION.md § The verdict: "exactly one...
#: from CONFIRMED | REFUTED | UNPROVEN".
VERDICTS = frozenset({"CONFIRMED", "REFUTED", "UNPROVEN"})

#: The machine-checkable half of "escalate, never approve" (prohibition 1):
#: no key anywhere in the document may carry an approval, a merge
#: recommendation, or a pass.
_FORBIDDEN_KEYS = frozenset({"approved", "mergeable", "merge_recommendation"})

#: ADJUDICATION.md requires several fields "non-empty", and § The verdict gives the
#: reason: "An ``UNPROVEN`` with no reason is indistinguishable from a stage that
#: skipped the finding." Re-exported from ``findings.py`` -- #117's own module, where
#: the identical "evidence must be non-empty" rule already applies to containment
#: findings -- rather than redeclared here, the same reason #283's fix moved it there:
#: a second private copy of one contract rule is how this bug class happened the first
#: time.
is_nonempty_str = findings.is_nonempty_str


def is_int(value: object) -> bool:
    """An integer that is not a boolean.

    ``bool`` subclasses ``int`` in Python, so ``isinstance(True, int)`` is
    True and a boolean satisfies a naive count check. That matters most where
    the count is 1: ``True == 1 == len(findings)``, so the equality
    comparison downstream stays silent and only a type check sees it.
    ``total_refutation`` is guarded with a strict ``isinstance(..., bool)``
    below, which is this module already showing the strictness it intends.
    """
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass
class Verdict:
    """The six fields ADJUDICATION.md adds on top of FINDINGS.md's ten.

    A plain data carrier, like `findings.Finding` -- it does not validate
    itself. Structural checking of a finding already in dict form is
    `validate`'s job.
    """

    verdict: str
    verdict_evidence: str
    reported_severity: str
    severity: str
    severity_reason: str | None
    duplicate_of: str | None

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "verdict_evidence": self.verdict_evidence,
            "reported_severity": self.reported_severity,
            "severity": self.severity,
            "severity_reason": self.severity_reason,
            "duplicate_of": self.duplicate_of,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Verdict:
        return cls(
            verdict=d["verdict"],
            verdict_evidence=d["verdict_evidence"],
            reported_severity=d["reported_severity"],
            severity=d["severity"],
            severity_reason=d.get("severity_reason"),
            duplicate_of=d.get("duplicate_of"),
        )


@dataclass
class Adjudication:
    """The top-level `adjudication` block. Nine keys, per ADJUDICATION.md § The
    `adjudication` block.

    Field order matches the contract's table, and `completion_marker` --
    last both here and in `as_dict()` -- stays last on purpose: it is the
    marker a truncated emit must lose before it loses anything else, the same
    reason `findings.Report` keeps its own `completion_marker` last.
    """

    schema_version: int
    verdict_counts: dict
    findings_in: int
    findings_out: int
    duplicate_groups: list = field(default_factory=list)
    downgrades: list = field(default_factory=list)
    total_refutation: bool = False
    notes: list = field(default_factory=list)
    completion_marker: str = ""

    def as_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "verdict_counts": self.verdict_counts,
            "findings_in": self.findings_in,
            "findings_out": self.findings_out,
            "duplicate_groups": self.duplicate_groups,
            "downgrades": self.downgrades,
            "total_refutation": self.total_refutation,
            "notes": self.notes,
            "completion_marker": self.completion_marker,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Adjudication:
        return cls(
            schema_version=d["schema_version"],
            verdict_counts=d["verdict_counts"],
            findings_in=d["findings_in"],
            findings_out=d["findings_out"],
            duplicate_groups=d.get("duplicate_groups", []),
            downgrades=d.get("downgrades", []),
            total_refutation=d.get("total_refutation", False),
            notes=d.get("notes", []),
            completion_marker=d["completion_marker"],
        )


def _iter_findings(document: dict):
    """Yield ``(label, index, finding)`` for every finding in every report.

    ``label`` matches FINDINGS.md's own labelling convention (``report
    {dimension!r}``, falling back to a positional label when a report has no
    ``dimension``) so a violation string from this module reads consistently
    next to one from `findings.validate`.

    Every container assumed here (``reports``, a report, its ``findings``) is
    type-checked before being treated as its expected shape, same as
    `findings.validate` -- a malformed document is exactly the input this
    module exists to describe with a violation string, never the input it
    crashes on.
    """
    reports = document.get("reports")
    if not isinstance(reports, list):
        return
    for report_index, report in enumerate(reports):
        if not isinstance(report, dict):
            continue
        dimension = report.get("dimension")
        label = f"report {dimension!r}" if dimension is not None else f"document.reports[{report_index}]"
        findings_raw = report.get("findings")
        if not isinstance(findings_raw, list):
            continue
        for finding_index, finding in enumerate(findings_raw):
            yield label, finding_index, finding


def _finding_ids(document: dict) -> set[str]:
    """The set of ``finding_id`` values across every report's findings.

    Extracted from the document directly, never from a count -- a count
    cannot tell a dropped id from an invented one, or notice a swap that
    leaves the count unchanged. This is what `validate`'s finding_id
    SET-equality check needs, and the only reason `validate` takes both
    documents rather than one.
    """
    ids: set[str] = set()
    for _, _, finding in _iter_findings(document):
        if isinstance(finding, dict):
            fid = finding.get("finding_id")
            if isinstance(fid, str):
                ids.add(fid)
    return ids


def _severity_fell(reported_severity: object, severity: object) -> bool:
    """Whether ``severity`` is a real fall below ``reported_severity``.

    Both must already be legal ladder values -- an out-of-ladder value is
    reported as its own violation elsewhere, not treated as a fall here.
    """
    if not isinstance(reported_severity, str) or not isinstance(severity, str):
        return False
    if reported_severity not in SEVERITY_ORDER or severity not in SEVERITY_ORDER:
        return False
    return SEVERITY_ORDER[severity] > SEVERITY_ORDER[reported_severity]


def _find_forbidden_keys(value: object, path: str) -> list[str]:
    """Walk the whole document for a key named `approved`, `mergeable` or
    `merge_recommendation`, anywhere -- the machine-checkable half of
    prohibition 1. Walked, not grepped: a grep over the serialised text would
    also flag those words inside `verdict_evidence` prose, which prohibition 1
    explicitly does not bind.
    """
    violations: list[str] = []
    if isinstance(value, dict):
        for key, sub in value.items():
            if key in _FORBIDDEN_KEYS:
                violations.append(f"{path}.{key}: forbidden key present -- no field may carry an approval")
            violations.extend(_find_forbidden_keys(sub, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            violations.extend(_find_forbidden_keys(item, f"{path}[{index}]"))
    return violations


def forbidden_keys(document: object) -> list[str]:
    """Prohibition 1's machine-checkable half, callable on its own.

    Public because a PRODUCER needs it before it prints. ``validate`` below is
    the contract check a consumer runs: it takes an input and an output
    document together and reports everything. A producer holding only its own
    output still has to refuse to emit an approval-bearing document, and the
    alternative was a second copy of this walk over there -- and a second copy
    of a rule is a second chance to disagree with it.
    """
    return _find_forbidden_keys(document, "document")


def validate(input_document: dict, output_document: dict) -> list[str]:
    """Every violation of ADJUDICATION.md that STEP 2's own done-when requires
    this function to catch -- never raises, never stops early.

    NOT yet a check of every one of the nine ``adjudication`` block keys.
    ``schema_version``, ``verdict_counts`` and ``notes`` are unchecked here on
    purpose: ADJUDICATION.md's own STEP 1 text assigns "one control per key"
    to STEP 10's separate ``check_adjudication.py`` suite, and STEP 2's
    done-when never names these three. A document with a fabricated
    ``verdict_counts`` or a wrong-typed ``schema_version`` passes this
    function with zero violations today; STEP 10 is where that gap closes.

    Takes **both** documents, not one. An earlier revision declared
    ``validate(document) -> list[str]`` and separately required it to report
    the finding_id symmetric difference between input and output -- but
    ``findings_in`` is a count, and a count cannot tell a dropped id from an
    invented one, or notice a swap that leaves the count unchanged. The check
    the contract promises needs the actual input id SET, and the only place
    that set exists is the input document itself.

    Also re-runs #117's own ``findings.validate`` against the output document,
    so a document that leaves this stage still satisfies the contract it
    arrived under -- a stage that quietly breaks its input's own rules is the
    same defect as one that drops a finding. ``findings`` is imported at
    module scope now (#283): this module also re-exports
    ``findings.is_nonempty_str`` as its own ``is_nonempty_str``, so the import
    can no longer be deferred to this one call site.
    """
    violations: list[str] = list(findings.validate(output_document))

    input_ids = _finding_ids(input_document)
    output_ids = _finding_ids(output_document)
    if input_ids != output_ids:
        dropped = sorted(input_ids - output_ids)
        invented = sorted(output_ids - input_ids)
        if dropped:
            violations.append(f"finding_id set: present on input, missing from output: {dropped}")
        if invented:
            violations.append(f"finding_id set: present on output, absent from input (invented): {invented}")

    findings_by_id: dict[str, dict] = {}
    for _, _, finding in _iter_findings(output_document):
        if isinstance(finding, dict):
            fid = finding.get("finding_id")
            if isinstance(fid, str):
                findings_by_id[fid] = finding

    # Per-finding verdict fields: verdict, verdict_evidence, reported_severity,
    # severity, severity_reason. duplicate_of is checked separately below,
    # against the full id set built above.
    for label, index, finding in _iter_findings(output_document):
        if not isinstance(finding, dict):
            continue
        finding_label = f"{label} finding[{index}]"
        fid = finding.get("finding_id")
        if isinstance(fid, str):
            finding_label = f"{finding_label} (finding_id={fid!r})"

        verdict = finding.get("verdict")
        if not isinstance(verdict, str) or verdict not in VERDICTS:
            violations.append(
                f"{finding_label}: verdict must be one of {sorted(VERDICTS)}, got {verdict!r}"
            )

        if not is_nonempty_str(finding.get("verdict_evidence")):
            violations.append(
                f"{finding_label}: verdict_evidence must be a non-empty string, got "
                f"{finding.get('verdict_evidence')!r}"
            )

        reported_severity = finding.get("reported_severity")
        severity = finding.get("severity")
        if not isinstance(reported_severity, str) or reported_severity not in SEVERITY_ORDER:
            violations.append(
                f"{finding_label}: reported_severity {reported_severity!r} is not a key of "
                "review.SEVERITY_ORDER"
            )
        if not isinstance(severity, str) or severity not in SEVERITY_ORDER:
            violations.append(
                f"{finding_label}: severity {severity!r} is not a key of review.SEVERITY_ORDER"
            )

        if severity != reported_severity and not is_nonempty_str(finding.get("severity_reason")):
            violations.append(
                f"{finding_label}: severity_reason must be a non-empty string when severity "
                f"({severity!r}) differs from reported_severity ({reported_severity!r}), got "
                f"{finding.get('severity_reason')!r}"
            )

        dup = finding.get("duplicate_of")
        if dup is not None:
            if not isinstance(dup, str):
                violations.append(
                    f"{finding_label}: duplicate_of must be a string or null, got "
                    f"{type(dup).__name__}"
                )
            elif dup == fid:
                violations.append(f"{finding_label}: duplicate_of names itself")
            elif dup not in output_ids:
                violations.append(
                    f"{finding_label}: duplicate_of {dup!r} is not a finding_id present in the document"
                )

    adjudication_raw = output_document.get("adjudication")
    if adjudication_raw is None:
        violations.append("document: missing 'adjudication' key")
        adjudication: dict = {}
    elif not isinstance(adjudication_raw, dict):
        violations.append(
            f"document.adjudication: expected an object, got {type(adjudication_raw).__name__}"
        )
        adjudication = {}
    else:
        adjudication = adjudication_raw

    # findings_out == findings_in == the sum of every report's findings_count.
    findings_in = adjudication.get("findings_in")
    findings_out = adjudication.get("findings_out")
    reports = output_document.get("reports")
    report_findings_count_sum = 0
    if isinstance(reports, list):
        for report_index, report in enumerate(reports):
            if not isinstance(report, dict):
                continue
            report_count = report.get("findings_count")
            if is_int(report_count):
                report_findings_count_sum += report_count
            else:
                # Named rather than silently skipped: a skipped count makes the
                # sum wrong, and the equality violation below would then blame
                # findings_in for a defect that is actually here.
                violations.append(
                    f"document.reports[{report_index}]: findings_count must be an integer, "
                    f"got {report_count!r}"
                )
    if not (is_int(findings_in) and is_int(findings_out)):
        violations.append(
            "document.adjudication: findings_in and findings_out must both be integers, got "
            f"{findings_in!r} and {findings_out!r}"
        )
    elif not (findings_out == findings_in == report_findings_count_sum):
        violations.append(
            "document.adjudication: findings_in "
            f"({findings_in!r}), findings_out ({findings_out!r}), and the sum of every "
            f"report's findings_count ({report_findings_count_sum!r}) must all be equal"
        )

    # Downgrades, both directions: every recorded entry is a real fall, and
    # every real fall is recorded.
    downgrades = adjudication.get("downgrades")
    if not isinstance(downgrades, list):
        violations.append(
            f"document.adjudication.downgrades: expected an array, got {type(downgrades).__name__}"
        )
        downgrades = []
    downgrade_ids: set[str] = set()
    for index, entry in enumerate(downgrades):
        if not isinstance(entry, dict):
            violations.append(
                f"document.adjudication.downgrades[{index}]: expected an object, got "
                f"{type(entry).__name__}"
            )
            continue
        entry_fid = entry.get("finding_id")
        if not isinstance(entry_fid, str):
            violations.append(
                f"document.adjudication.downgrades[{index}]: finding_id must be a string, "
                f"got {type(entry_fid).__name__}"
            )
            continue
        downgrade_ids.add(entry_fid)
        finding = findings_by_id.get(entry_fid)
        if finding is None:
            violations.append(
                f"document.adjudication.downgrades[{index}]: finding_id {entry_fid!r} is not "
                "present in the document"
            )
            continue
        reported = finding.get("reported_severity")
        actual = finding.get("severity")
        if entry.get("from") != reported or entry.get("to") != actual:
            violations.append(
                f"document.adjudication.downgrades[{index}]: from/to "
                f"({entry.get('from')!r}/{entry.get('to')!r}) do not match finding "
                f"{entry_fid!r}'s reported_severity/severity ({reported!r}/{actual!r})"
            )
        if not _severity_fell(reported, actual):
            violations.append(
                f"document.adjudication.downgrades[{index}]: finding {entry_fid!r} is recorded "
                f"as a downgrade but its severity did not fall ({reported!r} -> {actual!r})"
            )
    for fid, finding in findings_by_id.items():
        reported = finding.get("reported_severity")
        actual = finding.get("severity")
        if _severity_fell(reported, actual) and fid not in downgrade_ids:
            violations.append(
                f"finding_id {fid!r}: severity fell from {reported!r} to {actual!r} but is not "
                "recorded in document.adjudication.downgrades"
            )

    # total_refutation, both directions: it is true iff findings_in > 0 and
    # every verdict is REFUTED.
    all_verdicts = [
        finding.get("verdict") for _, _, finding in _iter_findings(output_document) if isinstance(finding, dict)
    ]
    declared_total_refutation = adjudication.get("total_refutation")
    actual_total_refutation = bool(all_verdicts) and all(v == "REFUTED" for v in all_verdicts)
    if not isinstance(declared_total_refutation, bool):
        violations.append(
            "document.adjudication.total_refutation: must be a boolean, got "
            f"{type(declared_total_refutation).__name__}"
        )
    elif declared_total_refutation != actual_total_refutation:
        violations.append(
            f"document.adjudication.total_refutation: declared {declared_total_refutation!r} but "
            f"the findings' verdicts imply {actual_total_refutation!r}"
        )

    # duplicate_groups, both directions: a group's members point back at it via
    # duplicate_of, and every finding with duplicate_of set is named by the
    # group it points at.
    duplicate_groups = adjudication.get("duplicate_groups")
    if not isinstance(duplicate_groups, list):
        violations.append(
            f"document.adjudication.duplicate_groups: expected an array, got "
            f"{type(duplicate_groups).__name__}"
        )
        duplicate_groups = []
    grouped_as: dict[str, object] = {}
    for index, group in enumerate(duplicate_groups):
        if not isinstance(group, dict):
            violations.append(
                f"document.adjudication.duplicate_groups[{index}]: expected an object, got "
                f"{type(group).__name__}"
            )
            continue
        survivor = group.get("survivor")
        duplicates = group.get("duplicates")
        # Checked here, not only inside the loop below. The loop validates the
        # survivor indirectly -- via a member pointing back at it -- so a group
        # with an empty `duplicates` list never had its survivor checked at all.
        if not isinstance(survivor, str):
            violations.append(
                f"document.adjudication.duplicate_groups[{index}]: survivor must be a string, "
                f"got {type(survivor).__name__}"
            )
        elif survivor not in findings_by_id:
            violations.append(
                f"document.adjudication.duplicate_groups[{index}]: survivor {survivor!r} is not "
                "a finding_id present in the document"
            )
        if not isinstance(duplicates, list):
            violations.append(
                f"document.adjudication.duplicate_groups[{index}]: duplicates must be an array, "
                f"got {type(duplicates).__name__}"
            )
            continue
        for dup_id in duplicates:
            if not isinstance(dup_id, str):
                violations.append(
                    f"document.adjudication.duplicate_groups[{index}]: duplicates entries "
                    f"must be strings, got {type(dup_id).__name__}"
                )
                continue
            grouped_as[dup_id] = survivor
            finding = findings_by_id.get(dup_id)
            if finding is None:
                violations.append(
                    f"document.adjudication.duplicate_groups[{index}]: duplicate {dup_id!r} is "
                    "not a finding_id present in the document"
                )
                continue
            if finding.get("duplicate_of") != survivor:
                violations.append(
                    f"document.adjudication.duplicate_groups[{index}]: finding {dup_id!r} does "
                    f"not point back at survivor {survivor!r} via its own duplicate_of "
                    f"({finding.get('duplicate_of')!r})"
                )
    for fid, finding in findings_by_id.items():
        dup_of = finding.get("duplicate_of")
        if dup_of is not None and grouped_as.get(fid) != dup_of:
            violations.append(
                f"finding_id {fid!r}: duplicate_of names {dup_of!r} but no "
                "document.adjudication.duplicate_groups entry lists this finding as one of its "
                "duplicates"
            )

    # The top-level nonce: present, unchanged from the input, and (via the
    # completion_marker check below) equal to this stage's own marker.
    # `findings.validate` above already checked it against every
    # report's own marker.
    nonce = output_document.get("nonce")
    if nonce != input_document.get("nonce"):
        violations.append(
            f"document.nonce: output nonce ({nonce!r}) differs from the input document's "
            f"nonce ({input_document.get('nonce')!r})"
        )

    # The adjudication block's own completion_marker: present, LAST key of the
    # block, and matching the top-level nonce.
    if "completion_marker" not in adjudication:
        violations.append("document.adjudication: missing 'completion_marker'")
    else:
        keys = list(adjudication.keys())
        if keys[-1] != "completion_marker":
            violations.append(
                "document.adjudication: completion_marker must be the last key, found last key "
                f"{keys[-1]!r}"
            )
        marker = adjudication["completion_marker"]
        expected_marker = f"BUZZ-ADJUDICATION-COMPLETE:{nonce}"
        if marker != expected_marker:
            violations.append(
                f"document.adjudication.completion_marker: expected {expected_marker!r}, got "
                f"{marker!r}"
            )

    # Prohibition 1's machine-checkable half: no key anywhere named `approved`,
    # `mergeable` or `merge_recommendation`.
    violations.extend(_find_forbidden_keys(output_document, "document"))

    return violations
