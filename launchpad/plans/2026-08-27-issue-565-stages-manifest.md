Issue #565 — task: run_dimensions must name each dimension in the stages manifest, or #119's condition (7) can never fire
Stated size: none in the issue (no `Size` line, no size label — checked `gh issue view 565`); the dispatching brief sized it as a task, "a small number of STEPs" → cap: 5 steps
Planned at 5. If a builder finds the work does not fit 5 steps, say so and stop rather than
growing it — the issue is one function, its tests, and two documents.

Planned against the worktree `/home/serina/Launchpad/buzz/__worktrees/task-565-stages-manifest`,
branch `task/565-stages-manifest`, base `origin/launchpad` at `9314e5e1a`, tree clean. Every
path and line number below was read there, not in the main checkout.

ALREADY TRUE  (verified against git and the running code, not against the issue text)
  `run_dimensions.py` emits no `stages` key. `build_document` (`run_dimensions.py:377-409`)
    returns exactly six keys: `pr, merge_base_sha, head_sha, reports, containment, nonce`.
    Confirmed by running the real CLI in the worktree:
    `python3 run_dimensions.py --payload fixtures/dimensions/paraphrase.json --seed probe`
    → exit 0, keys `['pr','merge_base_sha','head_sha','reports','containment','nonce']`,
    reports for all three real slugs. `git grep -c '"stages"' run_dimensions.py` → 0.
  `run_adjudication.py` is the only writer. `run_adjudication.py:1195-1198` sets
    `output_document["stages"] = [*input_stages, {"name": "adjudication", ...}]` — arrived
    entries pass through unchanged, exactly one entry is appended. `_input_stages`
    (`:392-431`) already accepts a populated array and validates each entry is a dict with a
    string `name`, so dimension entries need no change there.
  `build_document` ALREADY HOLDS THE DISPATCHED SET. `dimensions: list[str]` is an explicit
    parameter (`:382`), and `main()` is its only caller that fills it — from
    `list_dimensions()` at `:705`, passed at `:749-752`. So the correct source is already in
    scope; nothing needs to be plumbed in for this issue.
  `list_dimensions()` (`:128-137`) returns sorted `dimensions/*.py` stems. On disk today:
    `claim-vs-evidence`, `correctness-and-failure-modes`, `secrets-and-access` — verified by
    `python3 run_dimensions.py --list`. Report envelopes carry that same string in their
    `dimension` field (`:257`, `:169`), so slug equality between manifest and report is
    already guaranteed by construction, not by a mapping table.
  Every dispatched dimension currently produces a report. `_run_dimensions_concurrently`
    (`:327-369`) returns one `_collect_report` result per slug, and every failure path
    returns a `_failed_report` rather than nothing. So "no report at all" is not reachable
    through this module's own happy path today — see OPEN.
  `findings.validate` tolerates an extra top-level `stages` key. Verified empirically in the
    worktree: a real `build_document` output with `stages` appended returned `[]` from
    `findings.validate`. No validator change is needed.
  Baseline suites are green: `python3 -m unittest test_run_dimensions -q` → 53 tests, OK;
    `test_run_adjudication` → 100 tests, OK.
  CI DOES run these suites. `run_controls.py` lists `check_unit_suites.py`, which runs
    `unittest discover` over `test_*.py` in `launchpad/review-agent/`, and
    `.github/workflows/launchpad-review-agent-controls.yml` runs `python3 run_controls.py`
    on any `launchpad/review-agent/**` change. New tests added by this plan gate CI.
  ADJUDICATION.md IS ALREADY CORRECT and is out of scope. `8da3d0307` is an ancestor of this
    worktree's base (`git merge-base --is-ancestor` → yes); `ADJUDICATION.md:207-247` already
    strikes the superseded sentence, quotes #119's corrected definition, states that
    deriving entries from `reports[].dimension` cannot work, and names `list_dimensions()` as
    the only source. This plan copies that wording rather than inventing another.
  `launchpad/plans/2026-08-12-issue-117-review-dimensions.md:377` still asserts the
    superseded definition — one occurrence, verified: `grep -n 'no envelope'` on that file
    returns line 377 and nothing else.
  FINDINGS.md says nothing about `stages`. `grep -n stages FINDINGS.md` returns one
    unrelated hit (`:12`, about CONTAINMENT.md's stage table). § The merged document
    (`:153-165`) lists the six keys above and no seventh. § Contract changes since revision 3
    (`:263`) opens with the words "Six changes:" followed by six numbered items — the count
    word is prose and must be kept honest by hand.
  Nothing in the repo reads FINDINGS.md as a control. `check_contract.py` reads
    CONTAINMENT.md only. So the FINDINGS.md edit is checked by grep in STEP 5, not by a suite.
  `fixtures/adjudication/*.json` will NOT drift. `fixtures/adjudication/generate.py:156-164`
    assembles its merged document from a hand-written key list, not by copying
    `build_document`'s return, so a new key does not flow into the four committed fixtures
    and no regeneration is forced. Verified by reading `_build_from_per_dimension_reviewers`.
  KNOWN TRIVIAL CONFLICT — do not merge, do not depend on it. PR #1460 (`OPEN`, not draft,
    branch `feat/review-agent-publish-119` → `launchpad`) touches exactly three of the same
    regions: it adds a `"reviewer"` key to `build_document`'s returned dict immediately
    before `"reports"` (`run_dimensions.py:427-430` on that branch), widens the same key-set
    assertion in `test_run_dimensions.py:145-153`, and adds a row to the same FINDINGS.md
    merged-document table. All three resolve by keeping both additions. Intended final key
    order once both land: `pr, merge_base_sha, head_sha, reviewer, stages, reports,
    containment, nonce`. This branch must not rebase onto or cherry-pick from #1460.

DECIDED HERE (the issue's "Not verified" section hands this decision to this plan)
  The status vocabulary reuses the report's own, plus exactly one new value for absence:
    - a dimension whose report arrived with `status: "complete"` → `{"name": <slug>,
      "status": "complete", "reason": None}`
    - a dimension whose report arrived with `status: "failed"` → `"failed"`, and `reason` is
      that report's own `error["reason"]` verbatim, never re-worded
    - a dimension that was dispatched and whose report is absent → `"no_report"`, with a
      fixed reason naming the absence
  Why reuse rather than invent: a second vocabulary needs a translation table, and a
  translation table is a second source for one fact — the defect ADJUDICATION.md's own
  `_input_stages` docstring describes ("a second copy of a rule is a second chance to
  disagree with it"). Why one new value is unavoidable: absence has no report status to
  mirror. Why any non-`complete` value is sufficient for #119: its condition (1) fires on
  "a stage in the manifest has status other than `complete`". The manifest's `status` field
  is already an open per-stage vocabulary — `run_adjudication.py:1176-1193` emits
  `total_refutation` and `incomplete` for its own entry — so nothing global is being widened.

STEP 1  `build_stages(dimensions, reports)` in run_dimensions.py, wired   [independent]
        into `build_document`.                                              ← RUNS HERE
        A new module-level (public, docstring'd) function taking the DISPATCHED list first
        and the collected reports second. It iterates `dimensions` and only `dimensions`;
        `reports` is INDEXED BY NAME AND LOOKED UP, never enumerated to produce the name
        list. A report whose `dimension` is not in `dimensions` contributes no entry.
        Emit the result as `document["stages"]`, positioned immediately before `"reports"`.
        The docstring must state the source rule and why — a report cannot testify to its
        own absence, so the manifest is built from what was dispatched, not from what came
        back — in the same words ADJUDICATION.md:236-243 already uses.
        done when: `python3 run_dimensions.py --payload fixtures/dimensions/paraphrase.json
        --seed probe` exits 0 and its stdout JSON satisfies all four, checked in one run:
          (a) `[s["name"] for s in doc["stages"]]` equals the lines of
              `python3 run_dimensions.py --list`, in that order — today
              `["claim-vs-evidence","correctness-and-failure-modes","secrets-and-access"]`
          (b) every entry's key set is exactly `{"name","status","reason"}`
          (c) on this clean stub run every entry is `status: "complete"`, `reason: null`
          (d) `findings.validate(doc) == []`
        and `doc["stages"][i]["name"] == doc["reports"][i]["dimension"]` for all i, so the
        slug match required by the issue's first checkbox is asserted, not assumed.

STEP 2  The tests that pin the SOURCE, not merely the shape.                  [needs 1]
        In `test_run_dimensions.py` (which already imports `unittest.mock` and already uses
        `mock.patch.object(run_dimensions, ...)` at :310/:370/:492 — same idiom, no new
        dependency). Six tests, and (a), (b) and (f) are the ones this whole issue exists
        for:
          (a) a dispatched dimension whose report is dropped is STILL NAMED. Call
              `run_dimensions.build_document` with `dimensions=["dim-gamma","dim-alpha",
              "dim-beta"]` and `_run_dimensions_concurrently` patched to return reports for
              gamma and alpha only. Assert the manifest names exactly
              `["dim-gamma","dim-alpha","dim-beta"]` IN THAT ORDER; assert `"dim-beta"` is
              in the manifest and absent from `reports`; assert its status is `"no_report"`
              and is not `"complete"`.
              The dispatch list is deliberately NOT in alphabetical order. The plan review
              noted that every real caller reaches `build_document` via `list_dimensions()`,
              which is `sorted(...)`, so with a sorted fixture an implementation that
              re-sorts its own output is indistinguishable from one that preserves the given
              order — "iterates `dimensions` and only `dimensions`" would be asserted
              nowhere. `build_document` takes `dimensions` as a parameter, so a test can
              hand it an unsorted list even though today's production path never does, and
              the two strategies then diverge visibly.
          (b) a report for an UNDISPATCHED dimension is NOT named. `dimensions=["dim-alpha",
              "dim-beta"]`, patched reports containing a third for `"dim-gamma"`. Assert the
              manifest names exactly alpha and beta.
          (c) end-to-end through `main()`: extend `PayloadModeNetworkFreeTests` (which
              already builds a temp `dimensions/` of three stub files via
              `_with_fake_dimensions_dir`) to assert the printed document's stage names are
              `["dim-one","dim-three","dim-two"]` — `list_dimensions()`'s sorted order, which
              pins the `list_dimensions() → build_document → stages` wiring through the real
              production path.
          (d) a failed report maps to `status: "failed"` with `reason` equal to that
              report's own `error["reason"]` string, character for character.
          (e) widen `test_merged_document_has_exactly_the_contract_keys` (:141-153) to expect
              `"stages"`.
          (f) TOTAL OUTAGE — every dispatched dimension is still named when NOTHING comes
              back. `dimensions=["dim-alpha","dim-beta","dim-gamma"]` with
              `_run_dimensions_concurrently` patched to return `[]`. Assert three entries,
              in dispatch order, every one `status: "no_report"`, and `reports` empty.
              Added because the plan review found tests (a)-(e) all supply at least one
              report, so this implementation passes every one of them while being wrong:
                  if not reports: return []
                  by_name = {r["dimension"]: r for r in reports}
                  return [make_entry(d, by_name.get(d)) for d in dimensions]
              It sources from `dimensions` (so M1 does not catch it) and never unions in
              extras (so M2 does not catch it). Its only wrong input is the one no other
              test supplies. This is the case where naming the dispatched set matters most
              — a run in which every dimension died is exactly the run that must not
              publish as COMPLETE.
        (a), (b) AND (f) MUST GO THROUGH `build_document`, NOT `build_stages` ALONE. A
        helper-only test is explicitly insufficient here: it would still pass if
        `build_document` called `build_stages([r["dimension"] for r in reports], reports)`,
        which is precisely the wrong implementation this issue was filed to make impossible.
        Testing the helper as well is fine; testing only the helper is not.
        done when: `python3 -m unittest test_run_dimensions -q` exits 0 having run at least
        59 tests (53 baseline + 6), and `git grep -n 'build_document' test_run_dimensions.py`
        shows tests (a), (b) and (f) calling `build_document`, with
        `mock.patch.object(run_dimensions, "_run_dimensions_concurrently", ...)` in each.

STEP 3  Prove (a), (b) and (f) can actually fail — against the plausible     [needs 2]
        wrong implementations, not neutered ones.
        Copy `launchpad/review-agent/` into the session scratchpad (never mutate the
        worktree; `check_adjudication_mutations.py` establishes exactly this scratch-copy
        convention in this directory). Apply four mutants to the copy, one at a time:
          M1 "reports-derived" — `build_stages` builds its name list from
             `[r["dimension"] for r in reports]` instead of from `dimensions`. This is the
             fix the original reviewer proposed and the issue rejected.
          M2 "union" — the name list is `dimensions` plus any report dimension not in it.
          M3 "empty-reports short-circuit" — `build_stages` returns `[]` when `reports` is
             empty, and is otherwise correct. Sources from `dimensions`, unions nothing, so
             M1's and M2's tests both stay green; only test (f) fails. Its inclusion is the
             plan review's Medium finding, and it is the reason (f) exists.
          M4 "re-sorts its output" — `build_stages` returns its entries in `sorted(...)`
             order rather than the order `dimensions` gave. Correct for every production
             caller, because `list_dimensions()` already sorts; wrong the moment anything
             hands `build_document` an unsorted list. Only test (a)'s ordering assertion
             catches it, and only because (a)'s fixture is deliberately unsorted. This is
             the plan review's Low finding.
        A mutant that stubs the function to a constant proves nothing and does not count —
        `check_adjudication_mutations.py`'s own docstring gives the reasoning.
        done when: on the scratch copy, `python3 -m unittest test_run_dimensions` exits
        NON-ZERO under M1 with test (a) named in the failure output; NON-ZERO under M2 with
        test (b) named; NON-ZERO under M3 with test (f) named AND with (a), (b), (c), (d),
        (e) all still passing under M3 — that last clause is the whole point of M3, since a
        mutant the older tests also catch would not demonstrate the gap (f) was added to
        close. NON-ZERO under M4 with test (a) named, and (b)-(f) still passing, for the
        same reason. In each case the mutation is targeted, not a wrecking ball. Back in the
        worktree, `git status --porcelain launchpad/review-agent` is empty. All four mutant
        diffs and their failure outputs go into the PR body under Verification — this is the
        evidence that the manifest's source is genuinely pinned, and it is the single most
        important artefact this issue produces.

STEP 4  Pin adjudication's pass-through against a manifest that now          [needs 1]
        carries dimension entries, and drop the sentence this change falsifies.
        No behaviour change in `run_adjudication.py` — the issue's fourth checkbox says none
        is needed, and STEP 4 must not introduce one. Two edits:
          - a new test in `test_run_adjudication.py`, placed beside the two existing
            pass-through tests it extends —
            `test_output_stages_carries_input_entries_plus_one_new_adjudication_entry`
            (`:783`) and `test_input_stages_list_is_not_mutated` (`:808`), which today
            exercise a single `preflight` entry and nothing resembling a dimension. The new
            test builds `make_document()` and sets `stages` to three dimension entries using
            the real slugs, at least one with a status other than `"complete"` (a
            `"no_report"` entry is the case #119 depends on). Assert the output's `stages` is
            those three entries verbatim, in the same order, followed by exactly one
            `{"name": "adjudication", ...}` entry — length 4, no arrived entry's `status` or
            `reason` altered — and that `input_doc["stages"]` is unchanged after the call.
          - `run_adjudication.py:386-387` currently states "the `stages` manifest is
            explicitly an output #117 does NOT emit, so there is no upstream guarantee to
            inherit." STEP 1 makes the first clause false. Replace it with the true version
            that preserves the rule it was justifying: the manifest now arrives populated
            from #117, and this stage still enforces pass-through itself rather than
            inheriting a guarantee from its producer.
        This step is `[needs 1]` for the entry SHAPE, not for the code: a hand-built manifest
        that disagreed with what STEP 1 emits would be a pin against a shape nothing produces.
        done when: `python3 -m unittest test_run_adjudication -q` exits 0 with at least 101
        tests; `grep -c 'does NOT emit' run_adjudication.py` returns 0; and
        `git diff -U0 run_adjudication.py` shows changed lines confined to the docstring
        block at :380-390 — no executable line altered.

STEP 5  The two documents, agreeing with the two that already exist.      [independent]
        FINDINGS.md:
          - add a `stages` row to § The merged document's key table (`:157-164`);
          - add a `### The stages manifest` subsection stating the definition: it names every
            stage the review depended on, INCLUDING each of #117's dimensions by slug; it is
            produced from `list_dimensions()` (what was dispatched) and never from
            `reports[].dimension`, because A REPORT CANNOT TESTIFY TO ITS OWN ABSENCE; the
            three status values and what `reason` carries for each; and that #118 appends
            exactly one `adjudication` entry and passes everything else through. Reuse
            ADJUDICATION.md:207-247's sentences — this is a fourth location for one rule, so
            it must quote, not paraphrase.
          - add a numbered item to § Contract changes since revision 3 (`:263`), since #119's
            plan is committed against revision 3 and that section exists so its author can
            diff. THE LEADING COUNT WORD IS PROSE: "Six changes:" must become "Seven
            changes:" in the same edit.
        `launchpad/plans/2026-08-12-issue-117-review-dimensions.md:377`: strike the clause
        "covering stages that emit no envelope" and follow it with the corrected definition
        plus a dated amendment note — the in-place amendment convention that file itself
        describes at :166 ("struck through, with the corrected claim following") and which
        ADJUDICATION.md used on 2026-08-24. See OPEN for the one reading of the issue's
        checkbox this could be wrong about.
        done when: all four greps behave, run from `launchpad/review-agent/`:
          (a) `grep -n 'stages that emit no envelope'
              ../plans/2026-08-12-issue-117-review-dimensions.md` returns no line that
              ASSERTS it — every surviving occurrence is inside the dated amendment block and
              is marked as superseded;
          (b) `grep -c '^| `stages` |' FINDINGS.md` returns 1 and
              `grep -c '^### The stages manifest' FINDINGS.md` returns 1;
          (c) `grep -in 'cannot testify to its own absence' FINDINGS.md ADJUDICATION.md
              ../plans/2026-08-12-issue-119-publish-one-review.md` returns at least one hit
              in EACH of the three files — the mechanical form of "agrees rather than adding
              a fourth wording";
          (d) the count word before "changes:" in FINDINGS.md equals the number of numbered
              items beneath it.

PARALLEL  STEP 5 is genuinely independent and is the only step worth dispatching as a
          parallel subagent — it touches `FINDINGS.md` and the #117 plan file, which no other
          step opens. It can start immediately, because this plan (not STEP 1's code) fixes
          the vocabulary it documents.
          STEPs 1 → 2 → 3 are strictly sequential: 2 tests what 1 built, 3 mutates what 2
          wrote, and 1 and 2 both edit files 3 copies.
          STEP 4 touches `run_adjudication.py` and `test_run_adjudication.py` — files no
          other step opens — so it CAN run alongside STEP 2/3 once STEP 1 has landed the
          entry shape. Running it before STEP 1 risks pinning a shape nothing emits.
          Nothing here is dispatched by this plan.

GATES     review-plan on this file before building (it has not been reviewed; this skill does
          not review its own output). review-code and review-tests after STEP 3 — STEP 2/3
          are the substance of the issue and the place a wrong implementation would hide.
          review-adjudicate after those two. review-final once before push, and per this
          repo's standing convention it must be CROSS-MODEL: three same-model passes on #120
          missed what one Codex pass caught immediately, and this issue's whole subject is a
          plausible-looking wrong implementation, which is exactly the class same-model
          review is worst at. review-a11y: not applicable, no UI surface.
          qa explore mode: APPLIES, narrowly. There is a real runtime argument surface —
          `run_dimensions.py --payload/--seed/--degrade/--timeout/--list`. Worth exercising
          beyond the fixtures: `--degrade` specs so a surface is unreadable, a reviewer that
          times out (`--timeout 0.001`), and a run against an empty `dimensions/` (exit 5,
          `main()` refuses before `build_document`, so no manifest is printed — confirm that
          is still true). Not a full interactive exploration; there is no UI.
          The controls entry point is `python3 run_controls.py` from
          `launchpad/review-agent/` — two of its rows need network and will SKIP offline. A
          SKIP is not a PASS; report skips explicitly.

BUDGET    STEP 3. Producing two mutants that are genuinely targeted — each failing its own
          test while leaving the other four passing — takes more iteration than writing the
          feature did, and a scratch copy that will not import (or that silently runs the
          worktree's modules instead of the copy's) burns time before any mutation is even
          applied. STEP 5(c)'s three-file agreement grep is the second most likely to bite,
          because it fails until the exact sentence is present in all three files.

OPEN      The `no_report` branch is UNREACHABLE through `build_document`'s own code today —
          `_run_dimensions_concurrently` always returns one report per dispatched dimension.
          This plan keeps it as a real branch rather than asserting it away, matching
          `run_adjudication.py:1186-1193`'s own precedent for exactly this situation
          ("Unreachable today ... Kept as a real branch, not asserted away"), and exercises
          it through the patched seam in STEP 2(a). A reviewer could reasonably argue the
          branch is dead code; the counter-argument is that the issue's third checkbox
          requires the behaviour by name, and a manifest that can only describe reports it
          holds is the defect being fixed. Flagged, not hidden.
          "No longer carries the superseded wording" (sixth checkbox) admits two readings:
          strike-through-and-correct (this plan's choice, matching the file's own convention)
          or outright deletion. If a reviewer reads it as deletion, it is a one-line change.
          The status vocabulary was DECIDED in this plan because the issue's "Not verified"
          section delegates it here. It is stated in one place above so a reviewer can
          overturn it in one place.
          A dimension slug literally named `adjudication` would trip
          `run_adjudication._check_not_already_adjudicated`, which matches on `name` alone.
          Not reachable with today's three slugs, and not guarded by this issue.

LEFT OUT  #119's consumption of the manifest — condition (7) itself. The issue's own "Out of
          scope"; this issue supplies the input, it does not implement the check.
          ADJUDICATION.md's wording. Already corrected at `8da3d0307`, verified above to be
          an ancestor of this worktree's base.
          Regenerating `fixtures/adjudication/*.json`. `generate.py` assembles its merged
          document from a hand-written key list, so nothing forces it (verified above). If
          #119 later needs a committed fixture carrying dimension entries, that is a
          follow-up issue in `launchpad-26/buzz`, not this task.
          A control that reads FINDINGS.md the way `check_contract.py` reads CONTAINMENT.md.
          Nothing reads FINDINGS.md today, and that is a real gap — a normative document with
          no control drifts, which is `check_contract.py`'s own stated reason for existing.
          Worth filing as a non-blocking follow-up issue; it is not this task's size.
          `main()`'s exit code, still derived from `reports` alone and deliberately unchanged.
          Anything from PR #1460. Not merged, not depended on, not cherry-picked — only its
          three conflict sites are recorded above.
