Issue #284 — bug: the pass-through test cannot detect the loss of the guarantee it asserts
Stated size: no `Size` line on the issue; scope stated unambiguously as one assertion shape in one test method, no production code change  ->  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  `launchpad/review-agent/test_run_adjudication.py` exists on `origin/launchpad`
  (HEAD `aef93f2c2`) and its `ByteIdenticalPassThroughTests.
  test_pr_merge_base_head_and_containment_survive_untouched` (lines 183-193) compares
  `output_doc[key]` against `input_doc[key]` AFTER calling `adjudicate()` — confirmed by
  direct read.
  `run_adjudication.adjudicate()` builds `output_document` via
  `output_document = copy.deepcopy(input_document)` (line 1080) and never mutates
  `input_document` itself — confirmed by direct read.
  Reproduced the defect directly: with `copy.deepcopy(input_document)` replaced by a plain
  alias (`output_document = input_document`) in a worktree scratch edit, the full
  `test_run_adjudication` suite (101 tests today, not 19 — the suite has grown since the
  issue's #263-era measurement) goes to 4 failures/errors, but the specific target test
  `test_pr_merge_base_head_and_containment_survive_untouched` still reports `ok` in
  isolation — the mutant survives that one test exactly as the issue describes. Reverted
  and confirmed byte-identical (`git diff --stat` empty) before writing this plan.
  `test_verdicts.py`'s `DeepCopyIsolationTests.test_validate_does_not_mutate_either_document`
  (lines 543-550) already uses the snapshot-before-call shape this issue asks for:
  `input_before = copy.deepcopy(input_doc)` taken before the call under test, compared
  against afterwards.
  No mutation-testing harness in this repo currently exercises
  `test_run_adjudication.py`'s own suite against `run_adjudication.py` mutants.
  `check_adjudication_mutations.py` mutates `verdicts.py`/`run_adjudication.py`/
  `findings.py` and runs `check_adjudication.py` (a separate ~90-check control script) as
  its target — it does not invoke `test_run_adjudication.py` at all, so it is the wrong
  place to add M1 coverage and is out of scope for this fix.

STEP 1  Snapshot `input_doc` before calling `adjudicate()` in                [independent]
        `test_pr_merge_base_head_and_containment_survive_untouched`, and compare
        `output_doc[key]` and the (unmodified) `input_doc[key]` against that snapshot
        instead of against each other directly — matching `DeepCopyIsolationTests`'s shape:
        `input_before = copy.deepcopy(input_doc)` taken immediately before the
        `run_adjudication.adjudicate(...)` call; then for each of `pr`, `merge_base_sha`,
        `head_sha`, `containment`, assert `json.dumps(output_doc[key], sort_keys=True) ==
        json.dumps(input_before[key], sort_keys=True)` AND additionally assert
        `json.dumps(input_doc[key], sort_keys=True) == json.dumps(input_before[key],
        sort_keys=True)` (the second assertion is what actually distinguishes a real
        deepcopy from an alias — if `adjudicate()` ever aliased instead of copying,
        `input_doc` itself would carry the added `verdict`/`adjudication` keys after the
        call, and this assertion would fail even though the first, output-vs-snapshot
        comparison alone would not).
        done when: the edited test method no longer computes its comparison values by
        reading `input_doc[key]` after the `adjudicate()` call — every comparison reads
        either `output_doc` or `input_before`, never `input_doc`, post-call.

STEP 2  Reproduce the M1 mutant against the FIXED test and confirm it now dies.  [needs 1]
        In a scratch/temporary edit (never committed, reverted immediately after), replace
        `output_document = copy.deepcopy(input_document)` in `run_adjudication.py` with
        `output_document = input_document`, run
        `python3 -m unittest test_run_adjudication.ByteIdenticalPassThroughTests.
        test_pr_merge_base_head_and_containment_survive_untouched -v`, capture the failure
        output as before/after proof, then restore the original line and re-run the same
        command to confirm it passes clean again. Also re-run the full
        `test_run_adjudication` suite on the restored file to confirm nothing else
        regressed.
        done when: the mutant run shows the target test FAILING (not erroring for an
        unrelated reason — the failure message must name a pass-through key mismatch), the
        restored run shows the same test passing, `git diff --stat run_adjudication.py` is
        empty after restoring, and the full suite is green on the restored file.
        ← RUNS HERE

STEP 3  Decide and record scope for M3/M5 (the issue's own aside).              [needs 1]
        The issue names M3 (`anchor pr` branch removed) and M5 (`stub_judge` returns
        CONFIRMED) as separately surviving mutants and says they are "worth deciding on in
        the same pass" but explicitly "not a blocker on #263" — this repo's driving
        instructions for this fix scope the work to the M1 assertion shape only. Record
        that decision explicitly in the plan's OPEN section (below) and in the PR body
        rather than silently expanding scope or silently dropping the issue's own note.
        done when: this plan's OPEN section names M3/M5 as out of scope for this fix, with
        the reason (explicit task scoping to M1), and the PR body does the same.

STEP 4  Run the full existing test suite and repo quality gates on the real fix. [needs 2]
        `python3 -m unittest test_run_adjudication -v` (full file, no mutation) must stay
        green with the real fix applied (not the mutant). Where `just ci`-equivalent
        checks apply to a Python-only, non-Rust/non-desktop change in `launchpad/`, run
        whatever this subtree's own lint/format convention is (check for a local
        Makefile/lint target under `launchpad/review-agent/` first) rather than assuming
        `just ci` covers Python files it does not touch.
        done when: `python3 -m unittest test_run_adjudication` reports `OK` with the real
        (non-mutant) `run_adjudication.py`, and any subtree-local lint/format check that
        applies to the touched file passes or is confirmed not to exist.

STEP 5  Commit, push, open the PR against `launchpad` closing #284.            [needs 4]
        Commit with `git commit -s` (DCO). Push the branch. Open the PR with `gh pr
        create` as a lone command (no `cd` prefix in the same call — this repo's pr-gate
        hook rejects that shape), base `launchpad`, body includes "Closes #284", body
        states the before/after M1 mutant proof from STEP 2, and body explicitly notes the
        M3/M5 out-of-scope decision from STEP 3. Match the `by:agent` label convention
        used by recent merged agent-authored PRs (check via `gh pr list --repo
        launchpad-26/buzz --search "is:merged label:by:agent" --limit 3 --json
        number,labels` first).
        done when: the PR exists, targets `launchpad`, its body contains "Closes #284" and
        the mutant before/after proof, and its labels match the confirmed convention.

PARALLEL  Nothing here is independent of the others in practice: steps 2-5 all read or
          depend on the single edited test method from step 1, and step 1 is a single
          small edit not worth splitting into parallel subagents. This is a one-person,
          sequential fix by design — the smallest correct change is a single assertion
          shape in one test method.
GATES     `serina:review-tests` applies after step 1/2 (the diff only touches a test file)
          — it should confirm the new assertion shape actually distinguishes deepcopy from
          alias and does not merely restate the existing broken comparison in different
          words. `serina:review-code` is not required in the strict sense (no production
          code changes ship), but a quick pass costs nothing given the diff is one file.
          `qa` explore mode does not apply — there is no runtime/CLI interface being
          exercised by this fix beyond the existing unittest suite already run in STEP 2/4.
          `serina:review-final` runs once before merge per repo convention, via
          `build-change`'s own handoff.
BUDGET    STEP 2 is the step most likely to eat the budget: it requires a careful,
          reversible scratch mutation of production code, precise before/after capture,
          and a clean restore verified byte-for-byte — get the restore wrong and the
          "fix" ships with a broken `adjudicate()`.
OPEN      Whether M3 (`anchor pr` branch removed survives) and M5 (`stub_judge` returns
          CONFIRMED survives) should be fixed in this same PR or filed as separate
          follow-up issues. This plan scopes to M1 only, per the task's explicit
          instructions and the issue's own "not a blocker" framing; M3/M5 are left as
          follow-up issue candidates rather than silently expanded into this fix or
          silently dropped.
          The issue has no `Size` line; this plan assumes small/single-assertion scope
          based on the issue body and the task's explicit instructions rather than asking,
          since the fix shape (a single test method's comparison target) is stated
          unambiguously in the issue's own "Expected behaviour" section.
LEFT OUT  Any change to `run_adjudication.py` itself — the implementation is correct per
          the issue ("Not a blocker on #263. The implementation is correct; only the
          test's ability to prove it is not.") and per this plan's own STEP 2
          confirmation that a real deepcopy is present and functioning.
          Filing separate GitHub issues for M3/M5 — left to the PR reviewer/Serina's
          judgment per STEP 3, not auto-filed by this plan, since the task's explicit
          scope is the M1 fix alone.
