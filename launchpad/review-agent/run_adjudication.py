"""The adjudication stage's CLI. Implements launchpad-26/buzz#118 STEP 3.

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

    Raises ``InputValidationError`` -- adjudicating nothing, calling ``judge``
    zero times -- when ``input_document`` fails #117's own
    ``findings.validate``. This is the boundary STEP 1/STEP 2 call load-bearing:
    a finding whose ``severity`` already arrived illegal is refused here,
    wholesale, rather than reaching a per-finding fallback with no good answer.

    Pass-through fields (``pr``, ``merge_base_sha``, ``head_sha``,
    ``containment``) are never touched: the output starts as a
    ``copy.deepcopy`` of the input, and only a finding dict's own six new keys
    are ever written. Severity re-rating, the escalate-only guard, downgrade
    recording and dedupe are later steps' job -- every finding's ``severity``
    here is left exactly equal to its ``reported_severity``, and
    ``duplicate_of`` is always null.
    """
    violations = findings.validate(input_document)
    if violations:
        raise InputValidationError(violations)

    output_document = copy.deepcopy(input_document)
    nonce = output_document.get("nonce")

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

    print(json.dumps(output_document))
    return 0


if __name__ == "__main__":
    sys.exit(main())
