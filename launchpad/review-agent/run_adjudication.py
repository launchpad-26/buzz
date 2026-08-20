"""The adjudication stage's CLI. Implements launchpad-26/buzz#118 STEP 3 and
STEP 4 (the nonce check and the `stages` manifest -- see that section below).

Reads one #117 **merged document** on stdin, adjudicates every finding with an
**injected judge callable** -- defaulting to a stub that returns ``UNPROVEN``
with a stated reason -- and prints one document on stdout, in the shape
ADJUDICATION.md defines and ``verdicts.validate`` checks. Demonstrable before a
single adjudication prompt is written (STEP 5).

Three things this module must get right, each a way to lose data rather than a
missing feature:

**Pass-through is byte-identical where it is pass-through.** ``pr``,
``merge_base_sha``, ``head_sha`` and the whole ``containment`` block leave
exactly as they arrived -- this module builds the output from a
``copy.deepcopy`` of the input and only ever mutates a finding dict's own six
new keys, never touching those four. The evidence inside a containment finding
is raw per FINDINGS.md's contract, and #119 escapes at render time; a stage
that re-serialises through anything lossy would publish an excerpt that no
longer matches what the author wrote.

**The adjudicator never re-reads raw PR text.** CONTAINMENT.md forbids
re-reading raw PR text "to check for itself". This module makes no
``fetch.fetch_all`` call and no ``gh`` call for any of the seven surfaces --
the only input it ever reads is the merged document already on stdin. A judge
injected here *may* read the repository at ``head_sha`` -- the file a finding
is anchored at -- because that is the change under review as **code**, the
artefact the finding claims a defect about; it is never the author's PR
title/body/comments/diff-as-prose, which is the surface CONTAINMENT.md
contains and this module must not touch a second time. This module's own
stub judge does neither: it reads only the finding dict it is given.

**Anchor ``pr`` is normal, not an error.** A finding with ``file`` and
``line`` both null is structurally valid per FINDINGS.md, and this module
adjudicates it without raising. ``_location_description`` below is the one
place this module describes *where* a finding is anchored, and it branches on
``anchor`` first, before ever touching ``file``/``line`` -- never the reverse.

**The input is validated before a single finding is adjudicated.**
``adjudicate()`` runs #117's own ``findings.validate`` against the input
document first and raises ``InputValidationError`` -- adjudicating nothing --
when it fails; ``main()`` turns that into a non-zero exit with no document
printed at all. This is what keeps STEP 2's severity guarantee reachable: a
finding whose ``severity`` arrives out-of-ladder (an ``"Info"``, say -- #117's
own field name, before this stage ever renames it to ``reported_severity``)
fails ``findings.validate`` on that ground alone and never reaches this
module's per-finding logic, where "there is no legal value to preserve it as"
would otherwise be a real question with no good answer.

Two ways to obtain a verdict, and no others: ``--judge stub`` (the default --
``stub_judge`` below) and ``--replay <dir>`` (``make_replay_judge``, reading
STEP 9's future recorded judge outputs). This is also what keeps "choosing the
model" out of scope here, per #117's own framing and #118's issue: this module
never names one, and neither flag lets a caller supply one.

Severity re-rating, the escalate-only guard, downgrade recording and dedupe
are STEP 6/7's job, layered on top of this module later. This step leaves
every finding's ``severity`` exactly equal to its ``reported_severity`` --
the honest behaviour for a judge (the stub) that never rates anything -- and
``duplicate_of`` always null.

**STEP 4 -- the nonce check and the `stages` manifest.** Two more things
``adjudicate()`` does, on top of STEP 3's pass-through/anchor/validation-order
guarantees above, both implemented in this module because STEP 3 and STEP 4
are two facets of one CLI:

The top-level ``nonce`` is checked and passed through, **never generated**.
``_verify_nonce`` runs BEFORE #117's own ``findings.validate`` -- deliberately
reordered from STEP 3's original sequence, and this is why: ``findings.
validate`` independently rejects a document whose marker disagrees with the
top-level key too, but it does so with one generic per-report message,
identical whether the reports disagree with EACH OTHER or merely with the
top-level key. Running it first would mean ``_verify_nonce``'s three distinct
refusals below could never actually surface through ``main()`` -- every
document that would trigger one of them already fails ``findings.validate``
first, so the operator would only ever see the generic message and never the
category. Checking the nonce first makes the three refusals genuinely
observable end to end, which is what ADJUDICATION.md's "own reason, distinct
from the first" requirement means in practice. ``findings.validate`` still
runs -- second now, but still before a single finding reaches the judge loop,
which is STEP 3's actual guarantee, not "first" in an absolute sense.

One exception: a document whose ``reports`` key is missing, non-list, or
empty defers straight to ``findings.validate`` instead of ``_verify_nonce``
-- there is nothing for nonce verification to compare against, and calling
that "absent provenance" would bury ``findings.validate``'s more specific,
more useful message for exactly that shape defect. See ``adjudicate``'s own
body for the precise condition.

Three refusals, checked in this fixed order because one document can satisfy
more than one at once:
  1. ``"absent provenance"`` -- no top-level ``nonce``, or no report carries a
     parseable completion marker. Checked first because the other two need a
     value to compare against.
  2. ``"mixed document"`` -- the reports disagree with EACH OTHER. Checked
     second, and wins over 3 when a document exhibits both: a mixed document
     is the larger fact and a header mismatch is its consequence.
  3. ``"mismatched envelope"`` -- the reports agree with each other but not
     with the top-level key.
This module never picks a winner among disagreeing nonces and never accepts
a caller-supplied one -- ``_verify_nonce`` reads only ``document`` itself.

The ``stages`` manifest. #117 emits no top-level ``stages`` array; it is the
manifest #119 reads for stages -- #116's pre-flight, this one -- that produce
no envelope of their own. ``adjudicate()`` copies through every entry already
present on input and appends exactly one new ``{name: "adjudication", status,
reason}`` entry. An input already carrying an ``adjudication`` entry is a
re-run against an already-adjudicated document, and is refused outright
(``AlreadyAdjudicatedError``) rather than silently overwritten.

``status`` is ``"complete"`` only when every finding received a verdict and
the nonce was established. STEP 6's total-refutation flag does not exist yet
-- when it lands it becomes a third condition ANDed into ``adjudicate()``'s
``stage_complete`` computation below, not a rewrite of it.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Callable

import findings
import verdicts

#: The judge protocol: ``judge(finding, input_document) -> dict`` with at
#: least ``{"verdict": ..., "verdict_evidence": ...}``. Anything else --
#: a raised exception, a missing/illegal ``verdict``, empty
#: ``verdict_evidence`` -- is treated as unusable output and fails closed to
#: UNPROVEN, per ADJUDICATION.md's own default.
Judge = Callable[[dict, dict], dict]


class InputValidationError(ValueError):
    """Raised by ``adjudicate()`` when the input document fails #117's own
    ``findings.validate`` -- carries every violation, never just the first,
    the same "report everything" discipline ``findings.validate`` and
    ``verdicts.validate`` both already follow.
    """

    def __init__(self, violations: list[str]):
        self.violations = violations
        super().__init__("input document fails findings.validate: " + "; ".join(violations))


class NonceVerificationError(ValueError):
    """Raised by ``_verify_nonce`` when the document's provenance cannot be
    established -- one of the three refusals ADJUDICATION.md § The
    ``adjudication`` block names. ``reason`` is one of ``"absent provenance"``,
    ``"mixed document"`` or ``"mismatched envelope"``; ``detail`` is the
    human-readable specifics. Kept as two separate attributes (rather than one
    formatted string) so a caller -- ``main`` below, or a future control --
    can assert on the *category* without parsing prose.
    """

    def __init__(self, reason: str, detail: str):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


class AlreadyAdjudicatedError(ValueError):
    """Raised when ``input_document["stages"]`` already carries an
    ``"adjudication"`` entry. That shape means this exact document has
    already been through this stage once -- a re-run -- and ADJUDICATION.md
    § The ``stages`` entry requires refusing it outright rather than
    silently overwriting the earlier result.
    """


def _report_marker_nonce(report: dict) -> str | None:
    """Extract the nonce embedded in one report's ``completion_marker``, or
    ``None`` when the marker is missing, non-string, or does not parse as
    ``BUZZ-DIMENSION-COMPLETE:{dimension}:{nonce}`` -- the exact format
    ``findings.py``'s own ``_validate_report`` parses, matched here rather
    than re-invented, since #117 is this format's one producer.
    """
    marker = report.get("completion_marker")
    if not isinstance(marker, str):
        return None
    parts = marker.split(":", 2)
    if len(parts) != 3 or parts[0] != "BUZZ-DIMENSION-COMPLETE":
        return None
    return parts[2]


def _verify_nonce(document: dict) -> str:
    """Verify the document's top-level ``nonce`` against every report's own
    completion marker and return it. Raises ``NonceVerificationError`` --
    naming exactly one of the three refusals, in the fixed order
    ADJUDICATION.md states -- when it cannot be established. Never invents a
    nonce and never accepts one from anywhere but ``document`` itself.

    Reads ``document`` directly rather than trusting ``findings.validate``
    to have run first -- it runs BEFORE ``findings.validate`` in
    ``adjudicate()`` (see the module docstring's STEP 4 section for why): a
    stage agnostic about its producer verifies this itself.
    """
    top_nonce = document.get("nonce")
    reports_raw = document.get("reports")
    reports = reports_raw if isinstance(reports_raw, list) else []
    report_nonces = [
        _report_marker_nonce(report) if isinstance(report, dict) else None for report in reports
    ]

    # Refusal 1: ABSENT PROVENANCE. No top-level nonce, or at least one
    # report's marker does not parse -- "must equal the nonce embedded in
    # EVERY report's completion marker" cannot be checked for a report whose
    # marker cannot even be read, so one unparseable report is enough to
    # withhold provenance for the whole document, not just that report.
    # Checked first: refusals 2 and 3 both need a value to compare against.
    if not top_nonce:
        raise NonceVerificationError("absent provenance", "no top-level `nonce` is present")
    if not report_nonces or any(n is None for n in report_nonces):
        raise NonceVerificationError(
            "absent provenance",
            "at least one report carries no parseable completion marker to compare against",
        )

    # Refusal 2: MIXED DOCUMENT. The reports disagree with each other. Wins
    # over refusal 3 even when every report also disagrees with the
    # top-level key: a mixed document is the larger fact, and the header
    # mismatch that also follows from it is that fact's consequence, not a
    # second, independent finding.
    distinct_report_nonces = set(report_nonces)
    if len(distinct_report_nonces) > 1:
        raise NonceVerificationError(
            "mixed document",
            "reports carry different nonces in their completion markers: "
            f"{sorted(distinct_report_nonces)}",
        )

    # Refusal 3: MISMATCHED ENVELOPE. The reports agree with each other but
    # not with the top-level key -- one run's reports under another run's
    # header.
    (agreed_nonce,) = distinct_report_nonces
    if agreed_nonce != top_nonce:
        raise NonceVerificationError(
            "mismatched envelope",
            f"every report's completion marker carries nonce {agreed_nonce!r}, which does "
            f"not match the top-level nonce {top_nonce!r}",
        )

    return top_nonce


def _check_not_already_adjudicated(document: dict) -> None:
    """Raise ``AlreadyAdjudicatedError`` when ``document["stages"]`` already
    carries an entry named ``"adjudication"``. Run before ``_verify_nonce``
    in ``adjudicate()`` -- a re-run is a structural defect in the request
    itself, independent of whether this particular re-run's nonce happens to
    check out.
    """
    stages = document.get("stages")
    if not isinstance(stages, list):
        return
    for entry in stages:
        if isinstance(entry, dict) and entry.get("name") == "adjudication":
            raise AlreadyAdjudicatedError(
                "input document's `stages` array already carries an `adjudication` entry -- "
                "refusing to re-run adjudication over an already-adjudicated document"
            )


def _location_description(finding: dict) -> str:
    """Describe where a finding is anchored, branching on ``anchor`` FIRST --
    never assuming ``file``/``line`` exist. Anchor ``"pr"`` is a normal, valid
    shape (file and line both null; see FINDINGS.md and ADJUDICATION.md), not
    an error case, so it gets its own branch rather than falling through to a
    file/line format string that would render ``"None:None"``.
    """
    anchor = finding.get("anchor")
    if anchor == "pr":
        return "the whole pull request (no file or line anchor)"
    if anchor == "file":
        return f"{finding.get('file')}"
    if anchor == "line":
        return f"{finding.get('file')}:{finding.get('line')}"
    return "a finding with an unrecognised anchor"


def stub_judge(finding: dict, document: dict) -> dict:
    """The default judge (``--judge stub``). Establishes nothing about any
    finding -- it exists to prove the harness end to end before a single
    adjudication prompt is written (STEP 5). Every verdict it returns is
    ``UNPROVEN`` with a stated reason, per ADJUDICATION.md's own default,
    never ``CONFIRMED`` or ``REFUTED``.
    """
    return {
        "verdict": "UNPROVEN",
        "verdict_evidence": (
            "stub judge: no adjudication was performed; "
            f"{_location_description(finding)} was not examined."
        ),
    }


def make_replay_judge(replay_dir: Path) -> Judge:
    """Build a judge that replays recorded judge outputs from ``replay_dir``
    (STEP 9's future recordings) instead of calling a live model.

    STEP 9 has not been built yet and ``replay_dir`` will not exist when this
    runs in practice today -- this is a real, reachable code path per STEP 3's
    own scope, not one exercised end to end here. The format it reads: every
    ``*.json`` file directly under ``replay_dir`` is a JSON object mapping
    ``finding_id`` -> ``{"verdict": ..., "verdict_evidence": ...}``. Every
    file found is loaded and merged into one lookup; a ``finding_id`` with no
    matching entry anywhere fails closed to ``UNPROVEN`` with a reason naming
    the missing recording -- "no recording for this finding" is "cannot reach
    the finding", the same failure family ``_run_judge_safely`` already covers,
    not a crash.
    """
    recordings: dict[str, dict] = {}
    if replay_dir.is_dir():
        for path in sorted(replay_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                recordings.update(data)

    def _replay(finding: dict, document: dict) -> dict:
        finding_id = finding.get("finding_id")
        recorded = recordings.get(finding_id)
        if recorded is None:
            return {
                "verdict": "UNPROVEN",
                "verdict_evidence": (
                    f"replay: no recorded judge output for finding_id {finding_id!r} "
                    f"under {replay_dir}"
                ),
            }
        return recorded

    return _replay


def _run_judge_safely(judge: Judge, finding: dict, input_document: dict) -> dict:
    """Call ``judge`` and fail closed to ``UNPROVEN`` on anything unusable --
    a raised exception, a non-dict return, an illegal/missing ``verdict``, or
    empty ``verdict_evidence``. ADJUDICATION.md's own words: "An adjudicator
    that cannot reach the location, cannot parse the finding, times out, or
    returns unusable output yields UNPROVEN with a reason."
    """
    try:
        result = judge(finding, input_document)
    except Exception as exc:  # noqa: BLE001 -- a judge's own crash is exactly
        # the "cannot parse / times out" case above, and must fail closed
        # rather than propagate and abort the whole run over one finding.
        return {
            "verdict": "UNPROVEN",
            "verdict_evidence": (
                f"adjudicator raised {type(exc).__name__}: {exc}; failing closed "
                "to UNPROVEN per ADJUDICATION.md's default."
            ),
        }

    verdict = result.get("verdict") if isinstance(result, dict) else None
    evidence = result.get("verdict_evidence") if isinstance(result, dict) else None
    if verdict not in verdicts.VERDICTS or not evidence:
        return {
            "verdict": "UNPROVEN",
            "verdict_evidence": (
                "adjudicator returned unusable output (missing or illegal verdict, "
                "or empty verdict_evidence); failing closed to UNPROVEN per "
                "ADJUDICATION.md's default."
            ),
        }
    return {"verdict": verdict, "verdict_evidence": evidence}


def adjudicate(input_document: dict, judge: Judge) -> dict:
    """Adjudicate every finding in ``input_document`` with ``judge`` and
    return the adjudicated output document. Never mutates ``input_document``.

    Raises ``AlreadyAdjudicatedError`` when ``input_document["stages"]``
    already carries an ``adjudication`` entry (a re-run), and
    ``NonceVerificationError`` when the top-level ``nonce`` cannot be
    established against every report's completion marker (STEP 4; see the
    module docstring for why these run BEFORE ``findings.validate`` now).

    Raises ``InputValidationError`` -- adjudicating nothing, calling ``judge``
    zero times -- when ``input_document`` fails #117's own
    ``findings.validate``. This is the boundary STEP 1/STEP 2 call load-bearing:
    a finding whose ``severity`` already arrived illegal is refused here,
    wholesale, rather than reaching a per-finding fallback with no good answer.
    Checked after the two STEP 4 gates above, but still before any finding
    reaches the judge loop -- STEP 3's actual guarantee.

    Pass-through fields (``pr``, ``merge_base_sha``, ``head_sha``,
    ``containment``) are never touched: the output starts as a
    ``copy.deepcopy`` of the input, and only a finding dict's own six new keys
    are ever written. Severity re-rating, the escalate-only guard, downgrade
    recording and dedupe are later steps' job -- every finding's ``severity``
    here is left exactly equal to its ``reported_severity``, and
    ``duplicate_of`` is always null.
    """
    _check_not_already_adjudicated(input_document)

    # `_verify_nonce`'s job is provenance, not `reports`'s basic shape. A
    # document whose `reports` key is missing, non-list, or empty has nothing
    # for nonce verification to compare against -- `_verify_nonce` would call
    # that "absent provenance", which is technically true but masks the more
    # specific, more useful message findings.validate already gives for
    # exactly this ("missing required key 'reports'", "must not be empty",
    # "expected an array"). So a document this malformed defers straight to
    # findings.validate instead of being told the wrong subsystem is broken.
    reports_raw = input_document.get("reports")
    reports_present_and_nonempty = isinstance(reports_raw, list) and len(reports_raw) > 0

    if reports_present_and_nonempty:
        nonce = _verify_nonce(input_document)
        violations = findings.validate(input_document)
        if violations:
            raise InputValidationError(violations)
    else:
        violations = findings.validate(input_document)
        if violations:
            raise InputValidationError(violations)
        # Unreachable in practice: a missing, non-list, or empty `reports`
        # always fails findings.validate above, on one of the three grounds
        # named in this branch's comment. Kept as a real call, not asserted
        # away, the same "real branch" discipline `stage_complete`'s
        # nonce_established condition already uses below for STEP 6's
        # not-yet-built flag.
        nonce = _verify_nonce(input_document)

    output_document = copy.deepcopy(input_document)

    verdict_counts = {"CONFIRMED": 0, "REFUTED": 0, "UNPROVEN": 0}
    findings_in = 0

    for report in output_document.get("reports", []):
        for finding in report.get("findings", []):
            findings_in += 1
            result = _run_judge_safely(judge, finding, input_document)
            reported_severity = finding["severity"]
            finding["verdict"] = result["verdict"]
            finding["verdict_evidence"] = result["verdict_evidence"]
            finding["reported_severity"] = reported_severity
            # No re-rating in this stage: `severity` (#117's own field, already
            # present on `finding`) is left exactly as reported. STEP 6 adds
            # the guard that lets a judge's re-rating land here safely.
            finding["severity_reason"] = None
            finding["duplicate_of"] = None
            verdict_counts[result["verdict"]] += 1

    # Nothing is dropped or invented at this stage, so the two counts are the
    # same number by construction -- kept as two separate values (rather than
    # one variable used twice) because that is the shape STEP 7's dedupe and a
    # future drop/invent defect would change independently.
    findings_out = findings_in
    total_refutation = findings_in > 0 and verdict_counts["REFUTED"] == findings_in

    output_document["adjudication"] = verdicts.Adjudication(
        schema_version=1,
        verdict_counts=verdict_counts,
        findings_in=findings_in,
        findings_out=findings_out,
        duplicate_groups=[],
        downgrades=[],
        total_refutation=total_refutation,
        notes=[],
        completion_marker=f"BUZZ-ADJUDICATION-COMPLETE:{nonce}",
    ).as_dict()

    # The `stages` manifest (STEP 4). Every entry already on input, in order,
    # plus exactly one new `adjudication` entry -- `_check_not_already_
    # adjudicated` above already guarantees none of the input entries is
    # itself named `adjudication`.
    input_stages_raw = input_document.get("stages")
    input_stages = copy.deepcopy(input_stages_raw) if isinstance(input_stages_raw, list) else []

    # `status` is "complete" only when every finding received a verdict AND
    # the nonce was established. The nonce condition is always True here --
    # `_verify_nonce` above would have raised otherwise -- named explicitly
    # anyway so the AND reads as the real, multi-condition guarantee
    # ADJUDICATION.md states rather than a constant. `every_finding_has_
    # verdict` is read back off `output_document` itself (not tracked as a
    # separate counter through the loop above) so it is a check ON the
    # produced data rather than a second bookkeeping path that could drift
    # from it. STEP 6's total-refutation flag is a third condition this stage
    # does not build yet -- its absence must not make `stage_complete` wrongly
    # unconditional, which is why it is named as its own boolean rather than
    # inlined into one `and` chain that silently drops it.
    nonce_established = True
    every_finding_has_verdict = all(
        finding.get("verdict") in verdicts.VERDICTS
        for report in output_document.get("reports", [])
        for finding in report.get("findings", [])
    )
    stage_complete = every_finding_has_verdict and nonce_established

    if stage_complete:
        stage_status, stage_reason = "complete", None
    else:
        # Unreachable today: `_run_judge_safely` always returns a legal
        # verdict, so `every_finding_has_verdict` is always True by the time
        # this runs, and a False `nonce_established` would already have
        # raised above. Kept as a real branch, not asserted away, so STEP 6
        # can add its own condition here without restructuring this function.
        stage_status = "incomplete"
        stage_reason = "not every finding received a verdict"

    output_document["stages"] = [
        *input_stages,
        {"name": "adjudication", "status": stage_status, "reason": stage_reason},
    ]

    return output_document


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_adjudication.py",
        description=(
            "Adjudicate every finding in a #117 merged document (read on stdin) "
            "and print the adjudicated document on stdout. See ADJUDICATION.md."
        ),
    )
    parser.add_argument(
        "--judge",
        choices=["stub"],
        default="stub",
        help="the built-in judge to use when --replay is not given (default: %(default)s)",
    )
    parser.add_argument(
        "--replay",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "replay recorded judge outputs from DIR (STEP 9) instead of calling "
            "--judge. Takes precedence over --judge when both are given."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    raw = sys.stdin.read()
    try:
        input_document = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"run_adjudication: malformed JSON on stdin: {exc}", file=sys.stderr)
        return 1

    # Valid JSON does not imply a JSON *object*: `[]`, `"x"`, `42` all parse.
    # findings.validate assumes a dict (document.get(...), key not in document)
    # and is not guaranteed to raise cleanly on other JSON types -- reachable
    # directly from this CLI's untrusted stdin, so it is refused here, before
    # that assumption is ever exercised, the same way malformed JSON is.
    if not isinstance(input_document, dict):
        print(
            "run_adjudication: input must be a JSON object, got "
            f"{type(input_document).__name__}",
            file=sys.stderr,
        )
        return 1

    judge: Judge = make_replay_judge(args.replay) if args.replay is not None else stub_judge

    try:
        output_document = adjudicate(input_document, judge)
    except InputValidationError as exc:
        for violation in exc.violations:
            print(f"run_adjudication: {violation}", file=sys.stderr)
        return 1
    except AlreadyAdjudicatedError as exc:
        print(f"run_adjudication: {exc}", file=sys.stderr)
        return 1
    except NonceVerificationError as exc:
        print(f"run_adjudication: {exc.reason}: {exc.detail}", file=sys.stderr)
        return 1

    print(json.dumps(output_document))
    return 0


if __name__ == "__main__":
    sys.exit(main())
