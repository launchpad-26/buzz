"""The adjudication stage's CLI. Implements launchpad-26/buzz#118 STEP 3,
STEP 4 (the nonce check and the `stages` manifest) and STEP 6 (severity
re-rating, the out-of-ladder guard, downgrade recording and the
total-refutation status) -- see those sections below.

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

Severity re-rating and the escalate-only guard are STEP 6, below. Dedupe is
STEP 7, further below.

**STEP 6 -- severity re-rating and the out-of-ladder guard.** A judge's
return dict MAY now also carry a ``severity`` key and, when re-rating, a
``severity_reason``. ``_run_judge_safely`` forwards both from a *usable*
result only -- a judge whose output already failed closed to ``UNPROVEN``
(a crash, a missing/illegal ``verdict``, empty ``verdict_evidence``) never
gets to re-rate severity too; failing closed means failing closed on both.

``_apply_severity_rerating`` (below) is the guard, run once per finding:

* No ``severity`` key, or one equal to the finding's own
  ``reported_severity``: unchanged from STEP 3/4 -- ``severity ==
  reported_severity``, ``severity_reason`` stays ``None``.
* A **legal** (in ``review.SEVERITY_ORDER``) severity that differs: it
  becomes the finding's ``severity``, with a reason -- the judge's own if it
  gave one, else a generated default, since ``verdicts.validate`` requires a
  reason whenever ``severity != reported_severity`` regardless of direction.
  If it is a genuine **fall** (worse ``SEVERITY_ORDER`` index than
  ``reported_severity``), it is appended to ``adjudication.downgrades`` --
  ``{finding_id, from, to, reason}`` -- right there, at the moment the
  re-rating is applied, never by a later sweep over the finished document (a
  sweep is a second place the two could disagree). An **upgrade** (more
  severe) is not a downgrade and is never added to that list.
* An **illegal** (out-of-ladder) severity: refused, not published. This is
  the one place this stage can still *create* an out-of-ladder value -- the
  input arriving illegal is already caught upstream by STEP 3's
  ``findings.validate`` call, before any judge runs -- so this is defence in
  depth over this stage's own re-rating, not a repeat of that guard. The
  finding's ``verdict`` becomes ``UNPROVEN`` regardless of what the judge
  said for ``verdict``, ``severity`` falls back to ``reported_severity``
  (guaranteed legal at this point by STEP 3's input validation) or, purely
  as a second layer should that guarantee ever be bypassed, to ``"Blocker"``
  when even ``reported_severity`` is not in the ladder, and
  ``severity_reason`` names the refusal. Never added to ``downgrades``:
  nothing legally fell -- the value was refused, not accepted-then-compared.

**Total refutation now reaches the ``stages`` status, not only
``adjudication.total_refutation``.** When every finding is ``REFUTED`` and
at least one finding was received, the ``adjudication`` stage entry's own
``status`` is ``"total_refutation"`` -- checked ahead of the "every finding
has a verdict" condition below, so it wins whenever it applies. A document
with zero findings is never total refutation (the existing ``findings_in >
0`` condition already excludes it), so it keeps reporting ``"complete"``.

**Nothing is removed, reasserted inside this module.** ``adjudicate()``
compares the ``finding_id`` set of ``output_document`` against
``input_document`` immediately before returning and raises
``FindingSetIntegrityError`` if they differ -- belt-and-braces, since this
function does not drop or invent one by construction, but a stage that can
print a lossy document and rely on a downstream ``verdicts.validate`` call
to catch it has already lost the document once.

``adjudication.notes`` is **left empty here, and no step in this plan plumbs
it**, which until now was the one hardcoded-empty field with no deferral
stated anywhere. The judge protocol below carries no ``notes`` key, so a
judge that returns one has it dropped. Recording it explicitly because the
silence was the defect: ADJUDICATION.md declares the field and ``verdicts.py``
carries it, so a reader had every reason to assume the channel worked.

**The tension this once named is resolved, and in the other direction.** The
original text said the deferral conflicted with ``adjudicator.md`` (#265),
which "normatively tells a judge to record it in ``adjudication.notes``", and
asked whoever resolved it to either plumb ``notes`` through this protocol or
amend that document. ``adjudicator.md`` was amended (``05a960478``): it now
states that the channel is deferred and that a judge "must not rely on it",
and records that its own earlier paragraph said otherwise. So the instruction
no longer ships against a protocol that discards the key, and nothing here
needs to change to make the two agree.

Two things that were true then and remain true, kept because they are the
reason this paragraph exists rather than being deleted with the tension: a
judge's only free-text outlet is still ``verdict_evidence``, the field
ADJUDICATION.md identifies as having no structural guard; and the earlier
wording named "STEP 6/7" as the deferral target, which was already wrong --
both steps are in this branch and neither plumbed it. Plumbing ``notes``
remains unowned. It is a live gap, not a scheduled one, and calling it
"deferred to STEP 6/7" made it look scheduled.

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

**STEP 7 -- dedupe, and the mechanism ADJUDICATION.md deliberately leaves
open.** ADJUDICATION.md § Dedupe states the *outcome* contract -- a group is
``{survivor, duplicates: [finding_id]}`` in ``adjudication.duplicate_groups``,
every duplicate also carries ``duplicate_of``, a duplicate is still emitted
with its own verdict, and the survivor is chosen deterministically (highest
severity, then CONFIRMED before UNPROVEN before REFUTED, then lowest
``finding_id``) -- but it does not, and structurally cannot, say *how* two
findings are recognised as describing the same defect. ``Judge`` is
``judge(finding, input_document) -> dict``, called once per finding,
independently; it has no visibility into any other finding, so it cannot
detect a cross-finding duplicate by construction, and a cross-dimension
duplicate has a different ``finding_id`` by construction too (``dimension``
is one of ``finding_id``'s hash inputs -- see FINDINGS.md).

This module's answer is a **second, separate injectable callable**,
``dedupe_judge: DedupeJudge`` (default ``stub_dedupe_judge``, below) --
mirroring how ``judge: Judge`` already defaults to ``stub_judge`` to prove the
harness end to end before a single prompt is written. It is called **once**,
after every finding has already been adjudicated (so it sees each finding's
final ``verdict``/``severity``, not the raw #117 input), and returns which
sets of ``finding_id`` s -- if any -- describe the same defect; it does
*not* choose the survivor itself. Survivor selection is ADJUDICATION.md's
own deterministic rule, applied here in ``_build_duplicate_groups`` /
``_survivor_sort_key``, and is the same code path regardless of which
dedupe mechanism decided the grouping -- the two are independent axes on
purpose, the same reason ``judge``'s per-finding verdict and STEP 6's
severity re-rating are independent fields on one return dict rather than one
combined decision.

The alternative considered and set aside: folding dedupe into a single
richer ``Judge`` call/return shape. That would need ``Judge`` itself to see
every finding at once (a signature change reaching STEPs 3/4/6's existing
call sites and tests) to decide something that is, conceptually, a
completely separate question from "is this one finding true". A second
callable keeps ``Judge`` exactly as STEPs 3/4/6 already built it, at the
cost of one more injection point -- the smaller, less disruptive change,
and the one this module takes.

``stub_dedupe_judge`` finds **no duplicates**, by design, not merely because
nothing else exists yet: never merging incorrectly is safer than merging
findings that turn out not to share a defect, the identical fail-safe
direction ADJUDICATION.md already states for the per-finding default
(``UNPROVEN``, never ``REFUTED``). A ``dedupe_judge`` that crashes or returns
something unusable fails closed to the same "no duplicates" answer
(``_run_dedupe_safely``), never to a partial or guessed grouping.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Callable

import findings
import review
import verdicts

#: The judge protocol: ``judge(finding, input_document) -> dict`` with at
#: least ``{"verdict": ..., "verdict_evidence": ...}``, and MAY also carry
#: ``severity`` (STEP 6's re-rating) plus, when re-rating, ``severity_reason``
#: -- omitted, or equal to the finding's own ``reported_severity``, means no
#: re-rating at all. Anything else -- a raised exception, a missing/illegal
#: ``verdict``, empty ``verdict_evidence`` -- is treated as unusable output
#: and fails closed to UNPROVEN, per ADJUDICATION.md's own default, and no
#: severity re-rating is attempted from output this module could not use in
#: the first place.
Judge = Callable[[dict, dict], dict]

#: STEP 7's dedupe protocol: ``dedupe_judge(adjudicated_findings,
#: input_document) -> list[list[str]]``, called ONCE after every finding has
#: already been adjudicated (each finding dict in ``adjudicated_findings``
#: already carries its own ``verdict``/``severity``/etc.), never once per
#: finding like ``Judge`` above. Returns zero or more groups, each a list of
#: two-or-more ``finding_id`` strings describing the same defect -- the
#: dedupe judge decides WHICH findings are duplicates of each other; it does
#: not choose the survivor, which is ADJUDICATION.md's own deterministic rule
#: (see ``_build_duplicate_groups``/``_survivor_sort_key`` below), applied
#: identically regardless of which dedupe judge produced the grouping. A
#: raised exception, a non-list return, a group naming fewer than two real
#: finding_ids, or a finding_id already claimed by an earlier group is
#: handled defensively by ``_run_dedupe_safely``/``_build_duplicate_groups``
#: -- never a crash, and never a silently wrong merge.
DedupeJudge = Callable[[list, dict], list]


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


class FindingSetIntegrityError(RuntimeError):
    """Raised by ``adjudicate()`` if the ``finding_id`` set of the document it
    is about to return would differ from the set it was given -- STEP 6's
    "nothing is removed" reassertion. By construction this function never
    drops or invents a finding_id, so this is belt-and-braces: a stage that
    can print a lossy document and rely on a downstream ``verdicts.validate``
    call to catch it has already lost the document once. Deliberately a bare
    ``RuntimeError`` subclass rather than a caller-input error like the three
    above -- this names a bug in this module, not a defect in the document it
    was handed.
    """


class StagesShapeError(ValueError):
    """Raised when ``input_document["stages"]`` is present but malformed --
    not a list, or carrying an entry that is not an object with a string
    ``name``.

    Absent is legal and stays legal: #117 emits no top-level ``stages`` key
    at all, so "no manifest yet" is the normal case. What is refused is a
    manifest that exists in a shape this stage cannot honour. Treating that
    as absent -- which both readers previously did -- loses data twice over:
    the re-run guard has nothing to scan so a duplicate ``adjudication``
    entry slips through, and every entry already recorded is dropped, so a
    ``blocked`` pre-flight disappears and the document publishes as
    ``complete``.

    ADJUDICATION.md's rule is unconditional, and this stage cannot lean on
    its producer to keep it: the ``stages`` manifest is explicitly an output
    #117 does NOT emit, so there is no upstream guarantee to inherit. Neither
    ``findings.validate`` nor ``verdicts.validate`` inspects ``stages``.
    """


def _input_stages(document: dict) -> list:
    """``document["stages"]`` as a list, or ``[]`` when absent or null.

    The single definition of "a well-shaped input manifest", used by both
    ``_check_not_already_adjudicated`` and the manifest builder in
    ``adjudicate()``. One function on purpose: the two readers each had their
    own inline ``isinstance(..., list)`` test and each treated a malformed
    container as absent, which is how one shape defect became two independent
    failures. A second copy of a rule is a second chance to disagree with it.

    Raises ``StagesShapeError`` on a present-but-malformed manifest.
    """
    if "stages" not in document:
        return []
    stages = document["stages"]
    if stages is None:
        # An explicit null is "no manifest", same as omitting the key -- the
        # reading that keeps absence legal without admitting a wrong type.
        return []
    if not isinstance(stages, list):
        raise StagesShapeError(
            "input document's `stages` is present but is not an array "
            f"(got {type(stages).__name__}) -- refusing rather than treating a "
            "malformed manifest as an absent one, which would discard every "
            "entry already recorded in it"
        )
    for index, entry in enumerate(stages):
        if not isinstance(entry, dict):
            raise StagesShapeError(
                f"input document's `stages`[{index}] is not an object "
                f"(got {type(entry).__name__}) -- every manifest entry is "
                "`{name, status, reason}` per ADJUDICATION.md"
            )
        name = entry.get("name")
        if not isinstance(name, str):
            raise StagesShapeError(
                f"input document's `stages`[{index}] has a non-string `name` "
                f"(got {type(name).__name__}) -- an entry that cannot be "
                "identified by name cannot be checked against this stage's own"
            )
    return stages


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
    for entry in _input_stages(document):
        if entry.get("name") == "adjudication":
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


def stub_dedupe_judge(adjudicated_findings: list, input_document: dict) -> list:
    """The default dedupe judge (STEP 7). Finds **no duplicates** -- not
    merely because no real dedupe mechanism exists yet, but because it is
    the conservative, fail-safe default: never merging two findings is
    always safer than merging findings that turn out not to share a defect,
    the same fail-closed direction ADJUDICATION.md already states for the
    per-finding verdict default (``UNPROVEN``, never ``REFUTED``).

    Exists to prove STEP 7's harness -- ``adjudicate()``'s dedupe wiring,
    survivor selection, and ``duplicate_groups``/``duplicate_of`` emission --
    end to end before a single cross-finding dedupe mechanism is built, the
    same reason ``stub_judge`` exists for the per-finding verdict.
    """
    return []


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
    ``verdict_evidence`` that is not a string with at least one
    non-whitespace character. ADJUDICATION.md's own words: "An adjudicator
    that cannot reach the location, cannot parse the finding, times out, or
    returns unusable output yields UNPROVEN with a reason."

    "Blank", not "empty", and the distinction is the whole point: a
    truthiness test lets ``"   "`` through, and a whitespace reason is
    indistinguishable from no reason -- which is the case ADJUDICATION.md
    says the requirement exists to exclude. The rule is
    ``verdicts.is_nonempty_str``, imported rather than re-implemented, so
    this producer guard and the contract check in ``verdicts.validate``
    cannot drift apart: they did exactly that, each admitting whitespace
    because the other did.

    Returns a dict carrying at least ``verdict``/``verdict_evidence``, and --
    only when the judge's own output was usable -- ``severity``/
    ``severity_reason`` when the judge's return dict carried them (STEP 6's
    re-rating; see ``_apply_severity_rerating``). A judge whose output failed
    closed never gets to re-rate severity too: the two failure keys below
    never include a ``severity`` key, on purpose, so failing closed means
    failing closed on both.
    """
    try:
        # A COPY, never the live output finding. The escalate-only guarantee is
        # enforced by inspecting what the judge RETURNS; handing it the mutable
        # object those checks are about would let it edit the finding in place
        # and route around every one of them -- a judge doing
        # `finding["severity"] = "Low"` and returning only a REFUTED verdict
        # produced `reported_severity: "Low"`, an empty `downgrades`, and NO
        # `verdicts.validate` violation, because the "as reported" value was
        # read back out of the object the judge had already altered.
        # The same argument applies to every other field: `finding_id` is what
        # the input/output set-equality check is keyed on, so an in-place edit
        # there defeats that check too. Copy once, at the boundary, rather than
        # guarding fields one at a time as each is noticed.
        result = judge(copy.deepcopy(finding), input_document)
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
    if verdict not in verdicts.VERDICTS or not verdicts.is_nonempty_str(evidence):
        return {
            "verdict": "UNPROVEN",
            "verdict_evidence": (
                "adjudicator returned unusable output (missing or illegal verdict, "
                "or verdict_evidence that was blank, whitespace-only or not a "
                "string); failing closed to UNPROVEN per ADJUDICATION.md's default."
            ),
        }

    safe_result = {"verdict": verdict, "verdict_evidence": evidence}
    # A judge-supplied `severity` must be a string before it is ever compared
    # against `review.SEVERITY_ORDER` (a dict) with `in` -- an unhashable
    # value (a list, a dict) raises TypeError there rather than failing
    # closed, exactly the crash-instead-of-UNPROVEN outcome this function
    # exists to prevent. Same type discipline `verdict`/`evidence` already
    # get above; a non-string severity is treated as no re-rating at all,
    # never forwarded to _apply_severity_rerating.
    if isinstance(result.get("severity"), str):
        # `severity_reason` gets the SAME type discipline, for the same reason.
        # Forwarded unchecked, a non-string reason reached the output verbatim:
        # a judge returning `severity_reason={"approved": True}` produced a
        # document carrying a forbidden `approved` key in both the finding and
        # its downgrade record. `verdicts.validate` does catch it (9 violations)
        # -- but `main()` never calls it, so the CLI printed the document and
        # exited 0. This module's own rule, stated for the finding-set integrity
        # check: "a stage that can print a lossy document and rely on a
        # downstream verdicts.validate call to catch it has already lost the
        # document once." So it is refused here, at the producer.
        #
        # An unusable reason fails closed on the re-rating TOO, not just on the
        # reason -- the docstring's "failing closed means failing closed on
        # both". A severity change with no usable reason is precisely what the
        # contract forbids, so forwarding the change while dropping its
        # justification would manufacture the violation rather than refuse it.
        # A judge that supplies NO reason key at all is left alone: that is the
        # existing missing-reason case `_apply_severity_rerating` already
        # refuses, and its behaviour is unchanged.
        reason_unusable = "severity_reason" in result and not verdicts.is_nonempty_str(
            result["severity_reason"]
        )
        if not reason_unusable:
            safe_result["severity"] = result["severity"]
            if "severity_reason" in result:
                safe_result["severity_reason"] = result["severity_reason"]
    return safe_result


def _apply_severity_rerating(
    finding_id: object,
    reported_severity: str,
    verdict: str,
    proposed_severity: object,
    proposed_reason: object,
    downgrades: list[dict],
) -> tuple[str, str, str | None]:
    """STEP 6's severity re-rating guard, applied to one finding. Returns the
    ``(verdict, severity, severity_reason)`` that should actually be
    emitted -- ``verdict`` is returned rather than assumed unchanged because
    the illegal-severity branch overrides it.

    ``proposed_severity``/``proposed_reason`` are exactly what
    ``_run_judge_safely`` forwarded from the judge's own return dict --
    ``None`` when the judge did not re-rate, or when its output already
    failed closed (in which case no re-rating is attempted at all).

    Mutates ``downgrades`` in place by appending an entry at the moment a
    genuine fall is applied -- never by a later sweep over the finished
    document, per ADJUDICATION.md's "record it here, not by a later sweep"
    reasoning: a sweep is a second place the two could disagree.
    """
    if proposed_severity is None or proposed_severity == reported_severity:
        # THE GUARD FIRES ON THE EFFECTIVE SEVERITY -- the value that will
        # actually be emitted -- not only on a re-rating that differs from
        # `reported_severity`. ADJUDICATION.md is explicit that both must be
        # checked: "a finding arriving with an out-of-ladder
        # `reported_severity` that the judge happens to agree with is never
        # re-rated at all, so a guard watching only re-ratings never fires and
        # the bad value is copied into `severity` untouched." This branch --
        # no re-rating, or a re-rating that agrees -- IS that path, so the
        # check belongs here, ahead of the return that used to copy it.
        if reported_severity not in review.SEVERITY_ORDER:
            # There is no legal re-rating to refuse and no safe value to fall
            # back to: the severity ARRIVED illegal and the judge either
            # agreed with it or proposed nothing. `Blocker` rather than
            # anything smaller, because this stage may not silently decide
            # that an unrateable finding is a minor one.
            #
            # Unreachable through `main()` today -- STEP 3's
            # `findings.validate` refuses an out-of-ladder input severity
            # before any judge runs -- and kept as a real branch regardless:
            # `adjudicate()` is importable by anything, and STEP 10's control
            # suite is planned to feed this function malformed values
            # directly. Defence in depth that the contract already promises
            # is not the same as dead code.
            reason = (
                f"finding {finding_id!r} carries an out-of-ladder reported severity "
                f"{reported_severity!r} and the judge proposed no legal re-rating; "
                "refused, falling back to 'Blocker'"
            )
            return "UNPROVEN", "Blocker", reason
        # No re-rating: unchanged from STEP 3/4's behaviour.
        return verdict, reported_severity, None

    if proposed_severity not in review.SEVERITY_ORDER:
        # ILLEGAL re-rating: refused, not published. This is the one place
        # this stage can still *create* an out-of-ladder value -- an input
        # finding arriving illegal is already caught upstream by STEP 3's
        # findings.validate call, before any judge runs at all -- so this is
        # defence in depth over this stage's OWN re-rating, not a repeat of
        # that upstream guard.
        fallback_severity = (
            reported_severity if reported_severity in review.SEVERITY_ORDER else "Blocker"
        )
        reason = (
            f"judge returned an out-of-ladder severity {proposed_severity!r} for finding "
            f"{finding_id!r}; refused, falling back to the reported severity "
            f"{fallback_severity!r}"
        )
        # Not appended to `downgrades`: nothing legally fell -- the value was
        # refused, not accepted and then compared.
        return "UNPROVEN", fallback_severity, reason

    # LEGAL re-rating that differs from reported_severity. verdicts.validate
    # requires severity_reason whenever severity != reported_severity
    # regardless of direction, so a reason is generated even for an upgrade,
    # which is not itself a downgrade.
    reason = proposed_reason if proposed_reason else (
        f"judge re-rated severity from {reported_severity!r} to {proposed_severity!r} "
        "with no reason given"
    )
    if review.SEVERITY_ORDER[proposed_severity] > review.SEVERITY_ORDER[reported_severity]:
        downgrades.append(
            {
                "finding_id": finding_id,
                "from": reported_severity,
                "to": proposed_severity,
                "reason": reason,
            }
        )
    return verdict, proposed_severity, reason


#: Tie-break rank for ADJUDICATION.md § Dedupe's survivor rule: "CONFIRMED
#: before UNPROVEN before REFUTED". Lower is better, same convention as
#: ``review.SEVERITY_ORDER`` (Blocker=0 is the most severe).
_VERDICT_SURVIVOR_RANK = {"CONFIRMED": 0, "UNPROVEN": 1, "REFUTED": 2}


def _survivor_sort_key(finding: dict) -> tuple:
    """ADJUDICATION.md § Dedupe's survivor rule, as a sort key: highest
    adjudicated severity, then CONFIRMED before UNPROVEN before REFUTED,
    then lowest ``finding_id`` -- the minimum of this key over a group is
    the survivor. Deliberately independent of *how* the group was formed:
    this is the same computation regardless of which ``dedupe_judge``
    decided two findings are duplicates.

    A finding whose ``severity``/``verdict`` is somehow not a legal ladder
    value sorts last on that axis (worse than every legal value) rather than
    raising -- defensive in the same style as this module's other guards,
    though ``adjudicate()`` only ever calls this after STEP 6's re-rating
    guard has already guaranteed both fields are legal.
    """
    severity_rank = review.SEVERITY_ORDER.get(finding.get("severity"), len(review.SEVERITY_ORDER))
    verdict_rank = _VERDICT_SURVIVOR_RANK.get(finding.get("verdict"), len(_VERDICT_SURVIVOR_RANK))
    finding_id = finding.get("finding_id") if isinstance(finding.get("finding_id"), str) else ""
    return (severity_rank, verdict_rank, finding_id)


def _run_dedupe_safely(
    dedupe_judge: DedupeJudge, adjudicated_findings: list, input_document: dict
) -> list:
    """Call ``dedupe_judge`` once and fail closed to "no duplicates" (``[]``)
    on anything unusable -- a raised exception or a non-list return. Mirrors
    ``_run_judge_safely``'s "the judge's own crash or garbage output must not
    abort or corrupt the run" discipline, applied to the second, dedupe-only
    injection point: a dedupe judge that misbehaves must never silently
    merge findings it did not actually decide were duplicates.
    """
    try:
        # Copies again, same reason as ``_run_judge_safely``. By the time this
        # runs every finding already carries its final verdict and severity, so
        # a dedupe judge handed the live list could quietly rewrite decisions
        # that are no longer re-checked -- the grouping it returns is validated,
        # but the findings themselves are not re-read afterwards.
        raw_groups = dedupe_judge(copy.deepcopy(adjudicated_findings), input_document)
    except Exception:  # noqa: BLE001 -- a dedupe judge's own crash must fail
        # closed to no duplicates, exactly like a per-finding judge's crash
        # fails closed to UNPROVEN in `_run_judge_safely` above.
        return []
    return raw_groups if isinstance(raw_groups, list) else []


def _build_duplicate_groups(raw_groups: list, findings_by_id: dict) -> list[dict]:
    """Turn ``dedupe_judge``'s raw ``list[list[finding_id]]`` into
    ADJUDICATION.md's ``{survivor, duplicates: [finding_id]}`` shape, with
    the survivor chosen by ``_survivor_sort_key``.

    Defensive against a dedupe judge returning something it should not,
    the same discipline this module already applies to a misbehaving
    per-finding ``Judge``:
      * a non-list group, or a ``finding_id`` that is not a string, is
        dropped from that group rather than raising;
      * a ``finding_id`` naming a finding not present in ``findings_by_id``
        is dropped -- a dedupe judge can only group findings that were
        actually adjudicated;
      * a group left with fewer than two distinct real finding_ids after the
        above is not a group at all, and is dropped entirely;
      * a ``finding_id`` already claimed by an earlier group is dropped from
        every later group, so one duplicate can never point at two
        survivors -- first group wins, applied in the order
        ``dedupe_judge`` returned them.
    Never raises: a dedupe judge cannot break ``adjudicate()`` by returning
    a malformed grouping, it can only fail to have its grouping honoured.
    """
    groups: list[dict] = []
    claimed: set[str] = set()
    for raw_group in raw_groups:
        if not isinstance(raw_group, list):
            continue
        candidate_ids: list[str] = []
        for fid in raw_group:
            if (
                isinstance(fid, str)
                and fid in findings_by_id
                and fid not in claimed
                and fid not in candidate_ids
            ):
                candidate_ids.append(fid)
        if len(candidate_ids) < 2:
            continue
        survivor = min((findings_by_id[fid] for fid in candidate_ids), key=_survivor_sort_key)[
            "finding_id"
        ]
        duplicates = sorted(fid for fid in candidate_ids if fid != survivor)
        groups.append({"survivor": survivor, "duplicates": duplicates})
        claimed.update(candidate_ids)
    return groups


def _collect_finding_ids(document: dict) -> set[str]:
    """The set of every ``finding_id`` present across ``document``'s
    ``reports[].findings``.

    A small, local walk -- not a call into ``verdicts._finding_ids`` -- on
    purpose: this function backs STEP 6's "nothing is removed" reassertion
    inside ``adjudicate()`` itself, and a bug shared between the producer and
    its own belt-and-braces check would prove nothing. Every container is
    type-checked before being treated as its expected shape, same discipline
    ``verdicts.py`` and ``findings.py`` both already use for a document that
    might be malformed.
    """
    ids: set[str] = set()
    reports = document.get("reports")
    if not isinstance(reports, list):
        return ids
    for report in reports:
        if not isinstance(report, dict):
            continue
        findings_list = report.get("findings")
        if not isinstance(findings_list, list):
            continue
        for finding in findings_list:
            if isinstance(finding, dict):
                fid = finding.get("finding_id")
                if isinstance(fid, str):
                    ids.add(fid)
    return ids


def adjudicate(
    input_document: dict, judge: Judge, dedupe_judge: DedupeJudge = stub_dedupe_judge
) -> dict:
    """Adjudicate every finding in ``input_document`` with ``judge``, group
    duplicates with ``dedupe_judge`` (STEP 7; defaults to ``stub_dedupe_judge``,
    which finds none), and return the adjudicated output document. Never
    mutates ``input_document``.

    Raises ``StagesShapeError`` when ``input_document["stages"]`` is present
    but malformed -- not a list, or an entry that is not an object with a
    string ``name``. Absent or null stays legal.

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
    are ever written. Severity re-rating and the out-of-ladder guard are
    STEP 6 (see the module docstring's STEP 6 section and
    ``_apply_severity_rerating``); a judge that never re-rates leaves every
    finding's ``severity`` exactly equal to its ``reported_severity``, same
    as STEP 3/4.

    Dedupe (STEP 7) runs once, after every finding already has its final
    ``verdict``/``severity`` -- ``dedupe_judge`` is called exactly once with
    the full list of adjudicated findings, never once per finding, and its
    grouping is turned into ``adjudication.duplicate_groups`` plus each
    duplicate's own ``duplicate_of`` by ``_build_duplicate_groups`` (see the
    module docstring's STEP 7 section). A duplicate is never removed from
    ``reports[].findings`` -- it keeps its own verdict and is still counted
    in ``findings_out``.

    Before returning, asserts (raising ``FindingSetIntegrityError`` on
    failure) that ``output_document``'s ``finding_id`` set equals
    ``input_document``'s -- STEP 6's "nothing is removed" reassertion, run
    here rather than left to a downstream ``verdicts.validate`` call.
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
    downgrades: list[dict] = []

    for report in output_document.get("reports", []):
        for finding in report.get("findings", []):
            findings_in += 1
            # BEFORE the judge runs, not after. `_run_judge_safely` now hands
            # the judge a copy, so this ordering is belt as well as braces --
            # but the ordering is what makes the guarantee readable at the call
            # site: "as reported" must be captured from the document as it
            # arrived, and anything read after an injected callable has been
            # invoked is not that.
            reported_severity = finding["severity"]
            result = _run_judge_safely(judge, finding, input_document)
            verdict, severity, severity_reason = _apply_severity_rerating(
                finding_id=finding.get("finding_id"),
                reported_severity=reported_severity,
                verdict=result["verdict"],
                proposed_severity=result.get("severity"),
                proposed_reason=result.get("severity_reason"),
                downgrades=downgrades,
            )
            finding["verdict"] = verdict
            finding["verdict_evidence"] = result["verdict_evidence"]
            finding["reported_severity"] = reported_severity
            finding["severity"] = severity
            finding["severity_reason"] = severity_reason
            finding["duplicate_of"] = None
            verdict_counts[verdict] += 1

    # Nothing is dropped or invented at this stage, so the two counts are the
    # same number by construction -- kept as two separate values (rather than
    # one variable used twice) because that is the shape STEP 7's dedupe and a
    # future drop/invent defect would change independently.
    findings_out = findings_in
    total_refutation = findings_in > 0 and verdict_counts["REFUTED"] == findings_in

    # STEP 7 -- dedupe. Runs once, after every finding above already carries
    # its final verdict/severity, and never removes or re-counts anything:
    # `findings_out` (computed above) is unaffected by grouping.
    output_findings_by_id: dict[str, dict] = {}
    adjudicated_findings: list[dict] = []
    for report in output_document.get("reports", []):
        for finding in report.get("findings", []):
            adjudicated_findings.append(finding)
            fid = finding.get("finding_id")
            if isinstance(fid, str):
                output_findings_by_id[fid] = finding

    raw_dedupe_groups = _run_dedupe_safely(dedupe_judge, adjudicated_findings, input_document)
    duplicate_groups = _build_duplicate_groups(raw_dedupe_groups, output_findings_by_id)
    for group in duplicate_groups:
        for dup_id in group["duplicates"]:
            output_findings_by_id[dup_id]["duplicate_of"] = group["survivor"]

    output_document["adjudication"] = verdicts.Adjudication(
        schema_version=1,
        verdict_counts=verdict_counts,
        findings_in=findings_in,
        findings_out=findings_out,
        duplicate_groups=duplicate_groups,
        downgrades=downgrades,
        total_refutation=total_refutation,
        # Deferred to STEP 6/7, not an oversight -- see this module's docstring,
        # including the unresolved tension with adjudicator.md (#265). The judge
        # protocol carries no `notes` key, so nothing can populate this yet.
        notes=[],
        completion_marker=f"BUZZ-ADJUDICATION-COMPLETE:{nonce}",
    ).as_dict()

    # The `stages` manifest (STEP 4). Every entry already on input, in order,
    # plus exactly one new `adjudication` entry -- `_check_not_already_
    # adjudicated` above already guarantees none of the input entries is
    # itself named `adjudication`. That guarantee is real only because both it
    # and this line read the manifest through `_input_stages`, which refuses a
    # present-but-malformed shape instead of quietly reading it as absent.
    input_stages = copy.deepcopy(_input_stages(input_document))

    # `status` is "complete" only when every finding received a verdict, the
    # nonce was established, AND `total_refutation` is false. The nonce
    # condition is always True here -- `_verify_nonce` above would have
    # raised otherwise -- named explicitly anyway so the AND reads as the
    # real, multi-condition guarantee ADJUDICATION.md states rather than a
    # constant. `every_finding_has_verdict` is read back off
    # `output_document` itself (not tracked as a separate counter through the
    # loop above) so it is a check ON the produced data rather than a second
    # bookkeeping path that could drift from it.
    nonce_established = True
    every_finding_has_verdict = all(
        finding.get("verdict") in verdicts.VERDICTS
        for report in output_document.get("reports", [])
        for finding in report.get("findings", [])
    )
    stage_complete = every_finding_has_verdict and nonce_established and not total_refutation

    # `total_refutation` is checked FIRST and wins whenever it applies --
    # ADJUDICATION.md § The `stages` entry names "total_refutation" as one of
    # the specific reasons `status` carries when it is not "complete", and
    # the zero-findings case never reaches here with `total_refutation` true
    # (the `findings_in > 0` condition above already excludes it), so a
    # document with no findings still falls through to "complete" below.
    if total_refutation:
        stage_status = "total_refutation"
        stage_reason = (
            "every finding was REFUTED; see adjudication.total_refutation and "
            "adjudication.verdict_counts"
        )
    elif stage_complete:
        stage_status, stage_reason = "complete", None
    else:
        # Unreachable today: `_run_judge_safely` always returns a legal
        # verdict, so `every_finding_has_verdict` is always True by the time
        # this runs, and a False `nonce_established` would already have
        # raised above. Kept as a real branch, not asserted away, same
        # discipline as `nonce_established` above.
        stage_status = "incomplete"
        stage_reason = "not every finding received a verdict"

    output_document["stages"] = [
        *input_stages,
        {"name": "adjudication", "status": stage_status, "reason": stage_reason},
    ]

    # STEP 6's "nothing is removed" reassertion: this function does not drop
    # or invent a finding_id by construction, but a stage that can print a
    # lossy document and rely on a downstream `verdicts.validate` call to
    # catch it has already lost the document once. Checked here, inside the
    # runner itself, immediately before the document it guards is returned.
    input_ids = _collect_finding_ids(input_document)
    output_ids = _collect_finding_ids(output_document)
    if input_ids != output_ids:
        raise FindingSetIntegrityError(
            "adjudicate() would drop or invent a finding_id -- input and output finding_id "
            f"sets differ: dropped={sorted(input_ids - output_ids)}, "
            f"invented={sorted(output_ids - input_ids)}"
        )

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
    except StagesShapeError as exc:
        print(f"run_adjudication: {exc}", file=sys.stderr)
        return 1
    except NonceVerificationError as exc:
        print(f"run_adjudication: {exc.reason}: {exc.detail}", file=sys.stderr)
        return 1

    print(json.dumps(output_document))
    return 0


if __name__ == "__main__":
    sys.exit(main())
