#!/usr/bin/env python3
"""Deterministic generator for #118 STEP 8's adjudication fixtures.

STEP 8 needs merged #117-shaped documents -- valid *input* to
``run_adjudication.py`` -- each isolating one shape of finding-set the
adjudicator must handle. See ADJUDICATION.md's own module (this directory's
sibling ``run_adjudication.py``) for what "valid input" means, and
PROVENANCE.md (this directory) for the full honesty accounting this file's
docstring only summarises.

**Four of five named behaviours are genuinely produced from #117's own real,
recorded reviewer output** (``recordings/`` -- #117's STEP 8), replayed
through the real ``run_dimensions.build_document`` exactly as
``test_recordings.py``'s own ``ReplayValidityTests`` proves works. The fifth
(containment, all three kinds at once) has no real recording to replay --
checked against all eight of #117's existing fixtures, every one renders
``containment kinds=[] n=0`` -- so its *surfaces* are hand-crafted instead,
and only then run through the real ``contain.render``/``build_document``
pipeline. That split is stated on every document this file writes, in its own
``_fixture.provenance`` field, not just here.

**Why one dimension per ``build_document`` call, not one call for three.**
``run_dimensions.Reviewer`` is ``Callable[[str], object]`` -- it receives the
same rendered document *string* on every dimension's thread, with no
dimension name attached, so a single three-dimension call gives a reviewer no
honest way to tell which dimension is asking (dispatching on thread call
order would be dispatching on a race). Calling ``build_document`` once per
dimension -- each call is a single-dimension document, exactly
``test_recordings.py``'s own ``ReplayValidityTests`` pattern -- sidesteps the
problem entirely: each call's reviewer is a plain closure over one dimension's
recorded (or crafted-clean) content, and the three resulting single-report
documents are merged afterwards. ``contain.render`` depends only on
``(surfaces, nonce)``, never on ``dimensions``, so ``containment`` and
``nonce`` are identical across the three calls -- asserted, not assumed, by
``_merge_reports`` below.

**Determinism.** No fresh random nonce anywhere: every nonce is
``contain.make_nonce(seed=...)`` from a fixed seed -- a recording's own
``_provenance.seed`` where one exists, a fixed string documented alongside
its use where none does (fixture 4 only). Every document below is built by
the same deterministic construction path every run, so **regenerating
reproduces the same object graph, key-for-key, every time** -- which is what
makes ``python3 generate.py`` reproducing the committed bytes a real, checked
claim rather than an assertion (see ``test_adjudication_fixtures.py``).

**Why ``json.dumps`` is NOT called with ``sort_keys=True``, despite that
being the obvious way to pin byte output.** ``sort_keys`` sorts every nested
dict in the object graph, including each report dict -- and FINDINGS.md
requires ``completion_marker`` to be that dict's LAST key (checked
structurally by ``findings.validate``, not by convention: alphabetically,
``"completion_marker"`` sorts FIRST, ahead of ``"dimension"``, which would
turn every fixture this file writes into an invalid document). Byte-stability
instead comes from the object graph itself being constructed the same way on
every run -- Python dicts preserve insertion order, and every dict literal
and every reviewer's output order below is fixed in the code, not sorted at
dump time. ``indent=2`` is fixed; key order is not touched.

Run:  python3 generate.py    (from this directory, or anywhere -- it locates
                               launchpad/review-agent/ from its own path)
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW_AGENT_DIR = os.path.dirname(os.path.dirname(HERE))
if REVIEW_AGENT_DIR not in sys.path:
    sys.path.insert(0, REVIEW_AGENT_DIR)

import contain  # noqa: E402
import fetch  # noqa: E402
import run_dimensions  # noqa: E402

FIXTURES_DIMENSIONS_DIR = os.path.join(REVIEW_AGENT_DIR, "fixtures", "dimensions")
RECORDINGS_DIR = os.path.join(REVIEW_AGENT_DIR, "recordings")

#: The three real review dimensions #117 ships. Order here is the order
#: reports are merged in, on every document below.
DIMENSION_SLUGS = ("secrets-and-access", "claim-vs-evidence", "correctness-and-failure-modes")

#: Fixed identity for every document this file builds -- never a real PR, so
#: never anything but this placeholder triple.
PR = 0
MERGE_BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40


def _load_recording(fixture: str, dimension: str) -> dict:
    path = os.path.join(RECORDINGS_DIR, fixture, f"{dimension}.json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _seed_for_recording(fixture: str) -> str:
    """The one seed all three of ``fixture``'s recordings share.

    ``test_recordings.py``'s own ``test_seed_is_per_fixture_not_per_dimension``
    already proves this is a single value per fixture -- read from the first
    dimension in ``DIMENSION_SLUGS``, same as ``ReplayValidityTests`` does.
    """
    return _load_recording(fixture, DIMENSION_SLUGS[0])["_provenance"]["seed"]


def _replay_reviewer(fixture: str, dimension: str):
    """A reviewer that returns exactly one recording's own outcome/findings,
    never a fresh model call -- the same shape ``test_recordings.py``'s
    ``ReplayValidityTests`` builds inline, factored out here so every fixture
    below can reuse it.
    """
    recorded = _load_recording(fixture, dimension)
    content = {"outcome": recorded["outcome"], "findings": recorded["findings"]}
    return lambda document, content=content: content


def _raising_reviewer(document: str) -> dict:
    """Raises, deliberately -- so ``run_dimensions._collect_report``'s own
    exception-handling path produces a genuine ``status: "failed"`` report,
    not a hand-written one. See fixture 5, and PROVENANCE.md.
    """
    raise RuntimeError(
        "#118 STEP 8 fixture 5: this reviewer is deliberately made to raise, "
        "to exercise run_dimensions._collect_report's real status:'failed' "
        "path rather than hand-writing a failed report's shape"
    )


def _build_from_per_dimension_reviewers(
    surfaces: dict, nonce: str, reviewers_by_dimension: dict
) -> dict:
    """Call ``build_document`` once per dimension (see module docstring for
    why), then merge the resulting single-report documents into one.

    Asserts ``containment``/``nonce`` are identical across the three calls --
    they are a pure function of ``(surfaces, nonce)``, never of ``dimensions``,
    so any difference would mean this function's own assumption is wrong, not
    a real fixture property to encode.
    """
    reports = []
    containment = None
    for dimension in DIMENSION_SLUGS:
        doc = run_dimensions.build_document(
            PR, MERGE_BASE_SHA, HEAD_SHA, surfaces, [dimension], nonce,
            reviewer=reviewers_by_dimension[dimension],
        )
        reports.append(doc["reports"][0])
        if containment is None:
            containment = doc["containment"]
        else:
            assert containment == doc["containment"], (
                f"contain.render disagreed across per-dimension calls for {dimension!r} "
                "-- containment must depend only on (surfaces, nonce)"
            )
        assert doc["nonce"] == nonce
    return {
        "pr": PR,
        "merge_base_sha": MERGE_BASE_SHA,
        "head_sha": HEAD_SHA,
        "reports": reports,
        "containment": containment,
        "nonce": nonce,
    }


def _with_header(document: dict, comment: str, fixture_meta: dict) -> dict:
    """Prepend ``_comment``/``_fixture`` -- #117's own fixture convention
    (see fixtures/dimensions/*.json) -- to a merged document. Both are inert
    to every validator this document passes through: findings.validate and
    verdicts.validate only ever read the keys they name, never reject an
    unrecognised one, and run_adjudication.py's ``adjudicate()`` starts its
    output as ``copy.deepcopy(input_document)``, so both survive into the
    adjudicated output unchanged, still readable there.
    """
    header = {"_comment": comment, "_fixture": fixture_meta}
    return {**header, **document}


# ---------------------------------------------------------------------------
# Fixture 1 + 3: "paraphrase", replayed for all three dimensions.
#
# Isolates BOTH: (1) three reports, one finding per dimension, all anchor
# "line", and (3) two [in fact three] dimensions describing ONE defect at the
# same file/line -- the dedupe case. These are not two documents: the SAME
# real replay of the "paraphrase" recording set genuinely has both
# properties at once (test_recordings.py's own ParaphraseFixtureTests proves
# it), so producing them as two files would either duplicate one document
# under two names or fabricate a second one nothing recorded. See
# PROVENANCE.md.
# ---------------------------------------------------------------------------


def build_line_anchored_findings_document() -> dict:
    fixture = "paraphrase"
    surfaces = fetch.from_payload(os.path.join(FIXTURES_DIMENSIONS_DIR, f"{fixture}.json"))
    nonce = contain.make_nonce(seed=_seed_for_recording(fixture))
    reviewers = {d: _replay_reviewer(fixture, d) for d in DIMENSION_SLUGS}
    document = _build_from_per_dimension_reviewers(surfaces, nonce, reviewers)
    return _with_header(
        document,
        comment=(
            "#118 STEP 8 fixtures 1 AND 3 (one document, not two -- see this file's "
            "module docstring and PROVENANCE.md). Real: replays "
            "launchpad-26/buzz#117's own recorded reviewer output for the "
            "'paraphrase' fixture (recordings/paraphrase/*.json) through the real "
            "run_dimensions.build_document, one call per dimension, merged into one "
            "document. No hand-written finding content."
        ),
        fixture_meta={
            "isolates": [
                "three reports, one finding per dimension, all anchor 'line'",
                "two dimensions describing ONE defect at the same file/line -- the "
                "dedupe case (here, genuinely all three: every dimension reports "
                "the same planted paraphrase attack at the same location)",
            ],
            "provenance": "real",
            "real": True,
            "source_recordings": [f"recordings/paraphrase/{d}.json" for d in DIMENSION_SLUGS],
            "source_fixture_payload": "fixtures/dimensions/paraphrase.json",
            "note": (
                "All three dimensions report a Blocker at "
                "crates/buzz-relay/src/gate.rs:42, same defect, same location, "
                "different finding_id (dimension is a hash input) -- carrying "
                "both the 'all line-anchored' shape and a genuine dedupe "
                "CANDIDATE in the same real document. Candidate, not "
                "demonstration: run_adjudication.py's default stub_dedupe_judge "
                "groups nothing by design, so this document currently produces "
                "an empty duplicate_groups. Asserting on that output is STEP "
                "10's job, not this fixture's."
            ),
        },
    )


# ---------------------------------------------------------------------------
# Fixture 2: "claim-vs-evidence", replayed for all three dimensions.
#
# Isolates a pr-anchored finding (file and line null) alongside a
# line-anchored one, from the SAME dimension's own real recording -- two
# findings, not the isolated single pr-anchored case STEP 8's plan first
# described. Serina's decision: keep the real two-finding document rather
# than trimming it to one. See PROVENANCE.md.
# ---------------------------------------------------------------------------


def build_pr_anchored_finding_document() -> dict:
    fixture = "claim-vs-evidence"
    surfaces = fetch.from_payload(os.path.join(FIXTURES_DIMENSIONS_DIR, f"{fixture}.json"))
    nonce = contain.make_nonce(seed=_seed_for_recording(fixture))
    reviewers = {d: _replay_reviewer(fixture, d) for d in DIMENSION_SLUGS}
    document = _build_from_per_dimension_reviewers(surfaces, nonce, reviewers)
    return _with_header(
        document,
        comment=(
            "#118 STEP 8 fixture 2. Real: replays launchpad-26/buzz#117's own "
            "recorded reviewer output for the 'claim-vs-evidence' fixture "
            "(recordings/claim-vs-evidence/*.json) through the real "
            "run_dimensions.build_document, one call per dimension, merged into "
            "one document. No hand-written finding content."
        ),
        fixture_meta={
            "isolates": [
                "a pr-anchored finding (file and line null) alongside a "
                "line-anchored one, from the same dimension"
            ],
            "provenance": "real",
            "real": True,
            "source_recordings": [
                f"recordings/claim-vs-evidence/{d}.json" for d in DIMENSION_SLUGS
            ],
            "source_fixture_payload": "fixtures/dimensions/claim-vs-evidence.json",
            "note": (
                "The claim-vs-evidence dimension's own recording genuinely reports "
                "TWO findings for this fixture (one anchor 'line' Blocker at "
                "scripts/config_loader.py:23, one anchor 'pr' High citing a "
                "nonexistent scripts/config_schema.py) -- kept as recorded rather "
                "than trimmed to isolate the anchor 'pr' case alone. Trimming would "
                "make this a real replay with a finding deleted by hand, which is "
                "the precise thing this directory exists to avoid; the two-finding "
                "document is also the stronger test, exercising a 'pr' anchor "
                "alongside a 'line' one rather than in isolation. Argued from what "
                "the recording contains, deliberately citing no out-of-repo "
                "decision record -- a citation a reader cannot open is one this "
                "plan's own conventions treat as no citation at all."
            ),
        },
    )


# ---------------------------------------------------------------------------
# Fixture 4: all three containment kinds plus a full seven-key states map,
# zero dimension findings. NOT achievable by replay -- see PROVENANCE.md and
# containment-crafted-payload.json's own header for why. Surfaces are
# crafted; the containment block and states map below are genuine output of
# the real contain.render/build_document pipeline run against them.
# ---------------------------------------------------------------------------


def build_containment_all_kinds_document() -> dict:
    payload_path = os.path.join(HERE, "containment-crafted-payload.json")
    surfaces = fetch.from_payload(payload_path)
    # No recording exists for this fixture (see module docstring) -- a fixed,
    # documented seed stands in for one, never a fresh `contain.make_nonce()`
    # call with no seed at all.
    seed = "step8-adjudication-containment-crafted"
    nonce = contain.make_nonce(seed=seed)
    reviewers = {d: run_dimensions.default_reviewer for d in DIMENSION_SLUGS}
    document = _build_from_per_dimension_reviewers(surfaces, nonce, reviewers)
    return _with_header(
        document,
        comment=(
            "#118 STEP 8 fixture 4. CRAFTED SURFACES, REAL PIPELINE -- not "
            "'recorded'. No combination of #117's existing fixtures (checked all "
            "eight under fixtures/ and fixtures/dimensions/) trips all three of "
            "contain.py's detector kinds at once; every one renders containment "
            "kinds=[] n=0. The seven surfaces in containment-crafted-payload.json "
            "are hand-written to trip contain.find_lookalikes and detect.detect; "
            "this document's containment block, states map and dimension reports "
            "are genuine output of the real contain.render/run_dimensions."
            "build_document pipeline run against those crafted surfaces with the "
            "built-in clean stub reviewer (run_dimensions.default_reviewer) for "
            "all three dimensions."
        ),
        fixture_meta={
            "isolates": [
                "all three containment kinds (delimiter_forge, delimiter_lookalike, "
                "injection_attempt) plus a full seven-key containment.states map, "
                "zero dimension findings",
            ],
            "provenance": "crafted surfaces, real pipeline",
            "real": False,
            "source_payload": "containment-crafted-payload.json",
            "note": (
                "Honesty split, stated plainly: the SURFACES are crafted (no real "
                "PR, no recorded model output); the CONTAINMENT BLOCK and STATES "
                "MAP are genuine output of contain.render/build_document run "
                "against them, not hand-written. See "
                "containment-crafted-payload.json's own header for exactly which "
                "surface trips which kind."
            ),
        },
    )


# ---------------------------------------------------------------------------
# Fixture 5: "secrets-and-access", replayed for two dimensions; the third is
# forced to raise so run_dimensions._collect_report's real failure path
# produces a genuine status:"failed" report.
# ---------------------------------------------------------------------------


def build_mixed_report_statuses_document() -> dict:
    fixture = "secrets-and-access"
    surfaces = fetch.from_payload(os.path.join(FIXTURES_DIMENSIONS_DIR, f"{fixture}.json"))
    nonce = contain.make_nonce(seed=_seed_for_recording(fixture))
    # secrets-and-access's own recording: findings (Blocker). One of the two
    # clean dimensions (claim-vs-evidence) is forced to raise instead of
    # replaying its real clean recording, so the merged document carries a
    # genuine failed/clean/findings triple.
    reviewers = {
        "secrets-and-access": _replay_reviewer(fixture, "secrets-and-access"),
        "claim-vs-evidence": _raising_reviewer,
        "correctness-and-failure-modes": _replay_reviewer(fixture, "correctness-and-failure-modes"),
    }
    document = _build_from_per_dimension_reviewers(surfaces, nonce, reviewers)
    return _with_header(
        document,
        comment=(
            "#118 STEP 8 fixture 5. Real: replays launchpad-26/buzz#117's own "
            "recorded reviewer output for the 'secrets-and-access' fixture "
            "(recordings/secrets-and-access/*.json) for two of its three "
            "dimensions, through the real run_dimensions.build_document. The "
            "third dimension (claim-vs-evidence, recorded clean for this fixture) "
            "is replaced with a reviewer that RAISES, so "
            "run_dimensions._collect_report's real exception-handling path "
            "produces the failed report below -- it is not hand-written."
        ),
        fixture_meta={
            "isolates": ["one failed report, one clean report, one report with findings"],
            "provenance": "real (two replayed reports) + a genuinely-raised failure "
            "(one report) through the real _collect_report path",
            "real": True,
            "source_recordings": [
                "recordings/secrets-and-access/secrets-and-access.json",
                "recordings/secrets-and-access/correctness-and-failure-modes.json",
            ],
            "source_fixture_payload": "fixtures/dimensions/secrets-and-access.json",
            "note": (
                "claim-vs-evidence's real recording for this fixture is clean, not "
                "failed -- the failure here is deliberately injected (a reviewer "
                "that raises) so run_adjudication.py's stub judge sees a genuine "
                "status:'failed' report produced by the real pipeline, rather than "
                "a synthesised one."
            ),
        },
    )


BUILDERS = {
    "line-anchored-findings.json": build_line_anchored_findings_document,
    "pr-anchored-finding.json": build_pr_anchored_finding_document,
    "containment-all-kinds.json": build_containment_all_kinds_document,
    "mixed-report-statuses.json": build_mixed_report_statuses_document,
}


def render(filename: str) -> str:
    """The exact bytes ``filename`` should hold -- what generate.py writes,
    and what test_adjudication_fixtures.py's regeneration check compares the
    committed file against.
    """
    document = BUILDERS[filename]()
    return json.dumps(document, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    out_dir = HERE
    for filename in BUILDERS:
        text = render(filename)
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"wrote {filename} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
