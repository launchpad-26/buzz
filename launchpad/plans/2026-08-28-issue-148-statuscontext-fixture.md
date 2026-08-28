Issue #148 — task: record a StatusContext response, and settle how a legacy commit status maps into the record
Stated size: none given (issue has no `Size` line) → user-selected cap: 8 steps

ALREADY TRUE  (verified against git and the repo, not notes)
  `_normalise_check` (`launchpad/scripts/preflight_core.py:442-466`) already branches on
    `node.get("__typename") == "StatusContext"`, mapping `state` -> `conclusion` and
    leaving `status: None`. Its docstring already states this reasoning in prose.
  `test_preflight_core.py:305-314`
    (`RecordShape.test_status_context_shape_does_not_invent_a_status`) drives that branch
    from a hand-built dict, not a recorded fixture — the exact gap the issue names.
  `testdata/README.md` documents every fixture as recorded from the live API on
    2026-08-13, with none noted as a hand-written exception. Per the issue, all 47 nodes
    in `pr86-checks.json` are `CheckRun`; no `StatusContext` fixture exists.
  `INTERFACE.md`'s `checks` row (line 32) lists `conclusion` with no note that it may
    carry a `StatusState` value (`PENDING`, `EXPECTED`) that is not a member of
    `CheckConclusionState`.
  `record.sh` has no step that records a `StatusContext`-bearing PR; its existing
    GraphQL query (the PR-86 fixture (i) block) already asks for `... on
    StatusContext{context state targetUrl isRequired(...)}` and can be reused as-is
    against a different PR number.
  `#116`, which #148 is explicitly scoped not to touch, is CLOSED.
  No branch, PR, or plan for #148 existed before this one (`task/148-statuscontext-fixture`,
    branched fresh off `origin/launchpad`).

STEP 1  [independent] Update INTERFACE.md's `checks` row and the module/function
        docstring in preflight_core.py to state explicitly that `conclusion` may carry a
        `StatusState` value (`PENDING`, `EXPECTED`) that is not a `CheckConclusionState`
        member — the documentation route the DoD names for the PENDING decision. ← RUNS HERE
        done when: `grep -n "StatusState" launchpad/scripts/INTERFACE.md` returns a line
        stating `conclusion` may hold a StatusState value distinct from
        CheckConclusionState, and the same is true of `preflight_core.py`'s docstring.

STEP 2  [independent] Search for a live PR whose `statusCheckRollup` contains a
        `StatusContext` node, using record.sh's existing GraphQL query as the probe,
        against the issue's candidate sources: an upstream `block/buzz` PR touched by a
        third-party integration, a repo whose CI posts via `POST /repos/{o}/{r}/statuses/`,
        or a Vercel/Netlify-style deployment-status PR.
        done when: either a PR number is found where the query returns a node with
        `__typename: "StatusContext"`, or the candidate sources actually checked are
        listed with a "none found" conclusion.

STEP 3  [needs 2] If STEP 2 found a PR: add a recording step for it to record.sh (reusing
        the query already there), run it, and save the new fixture JSON under `testdata/`.
        If STEP 2 found nothing: this step is N/A — move to STEP 4's fallback.
        done when: a new `testdata/*.json` file exists containing at least one
        `StatusContext` node with real `context`, `state`, and `isRequired` values.

STEP 4  [needs 3] Add the new fixture's provenance row to `testdata/README.md`'s table,
        naming the live PR and endpoint it was recorded from, in the file's existing
        per-row format. If STEP 2 found nothing: instead write the "unrecorded, and why"
        line the DoD names as the honest fallback, next to the existing table.
        done when: README.md documents the new fixture, or (fallback) states plainly that
        the StatusContext path is unrecorded and why.

STEP 5  [needs 4] Replace `test_status_context_shape_does_not_invent_a_status`'s
        hand-built node with one loaded from the new fixture via the `fixture()` helper
        already used by other `RecordShape`/`ClosingIssue` tests, asserting the same
        output shape `_normalise_check` already produces. If STEP 2 found nothing: this
        step is out of scope — the hand-written control stays, and a one-line comment
        above it says why (no live StatusContext has been found; see README.md).
        done when: `cd launchpad/scripts && python3 -m unittest
        test_preflight_core.RecordShape.test_status_context_shape_does_not_invent_a_status
        -v` passes, reading its input from the recorded fixture (or, in the fallback
        case, the existing hand-built test is unchanged and its "why" comment is present).

STEP 6  [needs 1, 5] Run the full control suite and the mutation harness to confirm
        nothing regressed.                                                  [needs 1, 5]
        done when: `cd launchpad/scripts && python3 -m unittest discover -s . -t .`
        passes, and `python3 launchpad/scripts/mutation_harness.py` reports every phase
        clean.

PARALLEL  STEP 1 (INTERFACE.md + docstring) and STEP 2 (the fixture search) touch
          disjoint files and share no state — both may run as parallel subagents. STEP 3
          through STEP 6 are sequential: each depends on what STEP 2 actually found (a
          real PR or nothing), and STEP 6 needs every prior change settled before the
          suite and mutation harness can give a real answer.
GATES     review-code and review-tests apply after STEP 6 — this changes a controlled
          test's input source and, conditionally, `preflight_core.py`'s docstring and
          `INTERFACE.md`'s contract text. qa explore mode does not apply: no CLI or
          runtime-interface behaviour changes here, only fixture provenance, a test's
          input, and documentation, all exercised through the existing unittest suite.
BUDGET    STEP 2 — finding a live PR whose rollup actually contains a StatusContext node.
          There is no guarantee one exists among reachable repos; the search could run
          long before the honest answer is "none found."
OPEN      The issue names three candidate categories for finding a live StatusContext PR
          but does not say how long to search before falling back to the documentation
          route, nor which repos beyond `block/buzz` and this fork are in scope to check.
LEFT OUT  No change to `_normalise_check`'s actual mapping logic is planned unless STEP 2
          turns up a fixture that reveals it produces a wrong shape. Per the issue, the
          current mapping already matches the "state -> conclusion, status stays None"
          decision recorded in its own docstring — the DoD only requires correcting *or*
          documenting the PENDING case, and STEP 1 takes the documentation route
          independently of whether STEP 2 finds a real fixture.
