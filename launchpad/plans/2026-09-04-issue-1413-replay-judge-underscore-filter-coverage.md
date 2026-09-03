Issue #1413 — bug: make_replay_judge's reserved underscore-key filter has no test or mutation coverage
Stated size: no `Size` line on the issue -> cap: 5 steps (the issue's own
"Suggested fix" paragraph names exactly two artefacts — one direct test, one
named mutation — so this is a sub-30-minute shape by inspection; not asking
separately since the dispatching task already specified the fix shape,
acceptance criteria, and file list in full).

ALREADY TRUE (verified against git and the current worktree, origin/launchpad HEAD aef93f2c2)
  launchpad/review-agent/run_adjudication.py:605 (`make_replay_judge`, defined
    at line 581) reads
    `recordings.update({k: v for k, v in data.items() if not k.startswith("_")})`,
    filtering out any top-level recording-file key starting with `_` before
    merging it into the `finding_id -> judge output` lookup. Confirmed by
    direct read; behavior is correct today and must not change.
  launchpad/review-agent/test_run_adjudication.py already has a
    `ReplayJudgeTests` class (line 310) covering: a matching recording is
    used, a missing recording fails closed to UNPROVEN, and a nonexistent
    replay_dir fails closed. None of its fixtures ever build a recording file
    with an underscore-prefixed top-level key, and none look up
    `finding_id="_provenance"` — confirmed by reading the whole class body.
  launchpad/review-agent/check_adjudication.py (999 lines) is the file
    `check_adjudication_mutations.py` actually executes as its mutation
    target (`TARGET = "check_adjudication.py"`, `run_target()` runs it as a
    subprocess and parses its own `PASS `/`FAIL ` stdout lines). It already
    uses `make_replay_judge(RECORDINGS_DIR)` in several checks (lines 242,
    521, 620, 751, 804, 955) against the four real fixtures under
    `fixtures/adjudication/recordings/`, but none of those checks build a
    synthetic recording with a reserved key — confirmed by grep across the
    file for "replay"/"_provenance"/"startswith".
  launchpad/review-agent/check_adjudication_mutations.py's `MUTATIONS` list
    (16 entries) mutates `verdicts.py`, `findings.py`, and
    `run_adjudication.py`, always re-running `check_adjudication.py` as
    `TARGET` and asserting a specific FAIL-line substring appears. There is
    no existing entry targeting `make_replay_judge`'s underscore guard —
    confirmed by reading the full `MUTATIONS` list.
  This means: the harness (`check_adjudication_mutations.py`) can only prove
  a mutation is caught if the catching assertion lives in
  `check_adjudication.py` — a unittest-only assertion in
  `test_run_adjudication.py` is never executed by this harness. Both files
  need a check; only the `check_adjudication.py` one is what the mutation
  harness will actually exercise.

STEP 1  Add a direct unit test to ReplayJudgeTests [independent]
        Add a test to `ReplayJudgeTests` in `test_run_adjudication.py`
        proving the underscore-key filter:
        build a recording file containing both a normal `finding_id` entry
        AND a top-level `_provenance` key holding a distinct, recognizable
        dict; call `make_replay_judge`; assert (a) the normal finding_id
        still resolves to its real recorded verdict, and (b) a lookup for
        `finding_id="_provenance"` returns `None` from the judge's own
        UNPROVEN fail-closed path (i.e. `_provenance`'s value was never
        merged into the lookup at all) rather than the reserved dict's
        contents leaking through.
        done when: `python3 -m unittest test_run_adjudication -v` (from
        `launchpad/review-agent/`) shows the new test passing, and
        temporarily reverting `run_adjudication.py`'s guard to
        `recordings.update(data)` makes this specific new test fail (proving
        it is not vacuous) — revert the temporary change immediately after
        confirming.

STEP 2  Add the equivalent control to check_adjudication.py [needs 1]  <- RUNS HERE
        Add the equivalent control to `check_adjudication.py` — the file the
        mutation harness actually runs — since a `test_run_adjudication.py`
        assertion alone is invisible to `check_adjudication_mutations.py`.
        Build a synthetic recording directory with one normal
        `finding_id -> {verdict, verdict_evidence}` entry plus a top-level
        `_provenance` key, call `run_adjudication.make_replay_judge`, and
        `check()` that a finding whose `finding_id` is `"_provenance"` comes
        back UNPROVEN (i.e. was never satisfied by the reserved key's
        value), with a label text specific enough to serve as a mutation
        harness anchor (e.g. "make_replay_judge never returns a reserved
        underscore-prefixed key's value for any finding_id lookup").
        done when: `python3 check_adjudication.py` (from
        `launchpad/review-agent/`) exits 0 and prints a new `PASS` line with
        that label.

STEP 3  Add one named mutation to check_adjudication_mutations.py [needs 2]
        Target `run_adjudication.py`'s
        `recordings.update({k: v for k, v in data.items() if not
        k.startswith("_")})` line, replacing it with the unconditional
        `recordings.update(data)` (the issue's own suggested regression).
        `must_fail` must be a substring unique to STEP 2's new check label.
        Leave `still_passes_substrings` non-empty if an obviously unrelated
        check (e.g. the "replaying all four real fixtures in-process..."
        line) should stay green — confirm this once the harness runs.
        done when: the tuple is appended to `MUTATIONS` with a distinct
        `name`, correct `filename="run_adjudication.py"`, and `find`/`replace`
        strings that match the current source exactly (single, unambiguous
        occurrence — `apply_mutation` refuses on `count != 1`).

STEP 4  Prove the check is what catches the mutation [needs 3]
        Not by assertion: run `python3 check_adjudication_mutations.py`
        twice from a state where STEP 2's check is temporarily removed
        (stash/comment it out) to confirm the new mutation's target label is
        ABSENT from both PASS and FAIL output (proving today's gap is real),
        then restore STEP 2's check and re-run to confirm the same mutation
        now shows up as a named FAIL line and the harness's overall exit
        code area reports it caught.
        done when: both harness runs' relevant stdout excerpts are captured
        (with-check vs without-check) and clearly show the check flips from
        absent/uncaught to present/FAIL for the new mutation's label.

STEP 5  Run the full existing suites once more [needs 4]
        Confirm no regression: `python3 -m unittest test_run_adjudication`
        (full file, not just the new test), `python3 check_adjudication.py`,
        and `python3 check_adjudication_mutations.py` (full run, all
        mutations, not just the new one) all exit 0 with zero unexpected
        FAILs.
        done when: all three commands exit 0 and the mutation harness's own
        final "N failure(s)" line reads "0 failure(s)".

PARALLEL  Step 1 could start independently of everything else (it only
          touches `test_run_adjudication.py`). Steps 2-5 are strictly
          sequential: step 2 needs the vocabulary/shape decided in step 1 to
          stay consistent (same reserved-key example, `_provenance`), step 3
          needs step 2's exact check label to anchor `must_fail`, step 4
          needs step 3's mutation to exist to prove anything, step 5 is a
          final full-suite sweep. In practice, given how small this issue is,
          running steps 1 and 2 together in one pass is reasonable — they
          touch different files.
GATES     `review-tests` applies after step 1 (new unit test must not be
          vacuous — this plan's step 1 done-when already forces one round of
          revert-and-confirm, but review-tests should verify that check
          independently). `review-code` applies after step 2-3 (the new
          check-script code and the mutation tuple are, code). No UI surface
          exists in this change, so `review-a11y` does not apply. `qa`
          explore mode does not apply — there is no runtime interface beyond
          the two Python scripts already exercised directly by steps 2/4/5.
          `review-final` runs once per this repo's stated PR process, ahead
          of the PR gate hook.
BUDGET    Step 4 is the step most likely to eat the budget: temporarily
          removing STEP 2's check to prove the "before" state, then restoring
          it, is fiddly to do cleanly without leaving the tree dirty or
          accidentally committing the "without-check" state.
OPEN      The issue does not say whether the synthetic recording in step 2
          should also exercise `_dedupe_groups` (the OTHER reserved key
          `make_replay_judge`'s own docstring names) or only `_provenance`.
          This plan covers `_provenance` only, since the issue's own example
          and suggested fix both name it first and `_dedupe_groups` is
          explicitly read by a different function
          (`make_replay_dedupe_judge`) per the docstring at
          run_adjudication.py:592 — treating both together risks conflating
          two separate reserved-key consumers in one control. If review
          wants `_dedupe_groups` covered too, that is a natural, minimal
          follow-up rather than scope creep on this issue.
LEFT OUT  No change to `make_replay_judge`'s actual behavior — this issue is
          pure coverage, confirmed correct by STEP 1/2's "revert the guard,
          watch it fail" step. No change to `make_replay_dedupe_judge` or the
          `_dedupe_groups` reserved key (see OPEN above). No new CI wiring —
          `check_adjudication.py` and `check_adjudication_mutations.py` are
          already registered/run by existing tooling per their own
          docstrings; this issue only adds content inside them.
