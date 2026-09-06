Issue #283 — bug: containment evidence accepts whitespace — the last site of one truthiness idiom
Stated size: none on the issue, treated as <=30 minutes  ->  cap: 5 steps.
(No `Size` line on the issue. Flagged here per the skill's "no Size line -> ask before writing"
rule; proceeding on the smaller cap rather than blocking, since the issue body itself scopes the
fix tightly ("This is the one left standing") and a reproduction probe has already measured the
defect — one call-site fix plus a predicate relocation, fully diagnosed already.)

ALREADY TRUE  (verified against git + a reproduction probe run against current origin/launchpad HEAD)
  launchpad/review-agent/findings.py:239 reads `if not evidence:` inside `_validate_finding` —
    confirmed by reading the file directly.
  launchpad/review-agent/verdicts.py:37 defines `is_nonempty_str(value) -> bool:
    isinstance(value, str) and bool(value.strip())`, public, used at verdicts.py:308
    (verdict_evidence) and verdicts.py:326 (severity_reason) — confirmed by reading the file.
  launchpad/review-agent/run_adjudication.py:266 does `import verdicts` (module scope) and calls
    `verdicts.is_nonempty_str(...)` at lines 729 and 767 — confirmed by grep.
  launchpad/review-agent/verdicts.py:270 does `import findings as findings_module` LOCALLY,
    inside `validate()` only — confirmed by reading the file. findings.py has no import of
    verdicts.py anywhere (confirmed by grep for "verdicts" in findings.py: no hits).
  Commit 8593c30fe3 ("#118 STEP 2: make the two contract predicates public") is the precedent:
    it promoted `_is_nonempty_str`/`_is_int` to public in verdicts.py specifically so #263
    (run_adjudication.py) could import rather than re-implement.
  Reproduction probe (run against origin/launchpad HEAD, before any fix), for an otherwise
    well-formed containment finding with entry_point set:
      evidence="   "        -> 0 violations (bug)
      evidence=42            -> 0 violations (bug)
      evidence=True           -> 0 violations (bug)
      evidence=["x"]          -> 0 violations (bug)
      evidence={"a": 1}       -> 0 violations (bug)
      evidence="" (control)   -> 1 violation (correct: "evidence must be set ...")
  test_findings.py:175 already has an `EntryPointEvidenceTests` class with the fixtures
    (`make_finding`, `make_report`, `make_document`) needed for new tests, no new helpers needed.
  test_verdicts.py:379 already has a `VerdictEvidenceTests` class with the exact test shape to
    mirror (`test_whitespace_only_verdict_evidence_is_rejected`,
    `test_non_string_verdict_evidence_is_rejected`).

RESOLVED DESIGN QUESTION (the issue's one deliberate decision point)
  verdicts.py already depends on findings.py (locally, inside validate()); findings.py has no
  reverse dependency. Moving `is_nonempty_str` into findings.py and having verdicts.py import it
  from there follows the existing dependency edge. The alternative — findings.py importing from
  verdicts.py — would add a new, backwards edge (findings.py, #117's earlier-stage contract,
  would depend on verdicts.py, #118's later-stage contract). A private copy in findings.py is
  the second alternative the issue names explicitly as the wrong default: "a copy is what caused
  this class of bug in the first place." Decision: move the predicate into findings.py; verdicts.py
  imports and re-exports it under the same name so run_adjudication.py's existing
  `verdicts.is_nonempty_str(...)` call sites need no changes.

STEP 1  Move `is_nonempty_str` into findings.py; verdicts.py re-exports it        [independent]
        - In findings.py: add the `is_nonempty_str(value: object) -> bool` function (verbatim
          body: `isinstance(value, str) and bool(value.strip())`), keeping its docstring,
          placed near the top of the module (module is currently import-then-constants-then-
          functions; put it directly after the `_CONTAINMENT_KINDS` constant, before
          `finding_id`).
        - In verdicts.py: delete the local `is_nonempty_str` function body; promote the existing
          local `import findings as findings_module` (currently inside `validate()`) to a
          module-level `import findings`, and add `is_nonempty_str = findings.is_nonempty_str`
          at module scope (immediately after the import, before `VERDICTS`). Update
          `validate()`'s body to use the module-level `findings` import instead of its own local
          one (drop the now-redundant local `import findings as findings_module` line and its
          two internal call sites `findings_module.validate(...)`, changing them to
          `findings.validate(...)`).
        - Confirm no circular import: findings.py must contain no `import verdicts` anywhere
          (grep check) — it doesn't need one for this fix.
        done when: `grep -n "^import findings" launchpad/review-agent/verdicts.py` shows a
          module-level import; `grep -n "def is_nonempty_str" launchpad/review-agent/findings.py`
          shows the function now lives there; `grep -n "def is_nonempty_str"
          launchpad/review-agent/verdicts.py` shows nothing (no local def left); `python3 -c
          "import sys; sys.path.insert(0,'.'); import verdicts, findings; assert verdicts.is_nonempty_str is findings.is_nonempty_str"`
          run from `launchpad/review-agent/` exits 0.

STEP 2  Fix findings.py:239 to use the predicate                    [needs 1]  ← RUNS HERE
        - Replace `if not evidence:` in `_validate_finding` with `if not
          is_nonempty_str(evidence):`, keeping the existing violation message unchanged.
        done when: re-running the reproduction probe (evidence="   ", 42, True, ["x"],
          {"a": 1}, "" against an otherwise well-formed containment finding with entry_point
          set) shows all six cases now produce >=1 violation each, and each violation message
          still reads "evidence must be set (non-null, non-empty) when entry_point is set".

STEP 3  Add regression tests to test_findings.py                    [needs 2]
        - In `EntryPointEvidenceTests` (test_findings.py:175), add
          `test_whitespace_only_evidence_is_rejected` (subTest over "   ", "\n", "\t",
          "  \n  ", "\xa0", mirroring test_verdicts.py's
          `test_whitespace_only_verdict_evidence_is_rejected`) and
          `test_non_string_evidence_is_rejected` (subTest over 42, True, 0.5, ["x"],
          {"a": 1}, mirroring `test_non_string_verdict_evidence_is_rejected`), each building a
          finding via `make_finding(anchor="pr", file=None, line=None, entry_point="pr_body",
          evidence=<case>)` inside `make_document(reports=[make_report(findings_list=[...])])`,
          asserting `any("evidence must be set" in v for v in findings.validate(doc))`.
        - Verify each new test fails against the pre-fix guard (temporarily confirm by checking
          out the pre-Step-2 diff, or simply trust the probe from Step 2 as the fail evidence —
          either is acceptable, but state which was done) and passes after Step 2's fix.
        done when: `python3 -m unittest test_findings` run from `launchpad/review-agent/` is
          green including the two new tests, and stashing/reverting only Step 2's one-line
          change locally reproduces both new tests failing (confirms they are not vacuous).

STEP 4  Add a no-drift test to test_verdicts.py, then run the full suite       [needs 1, 3]
        - Add a test mirroring test_findings.py's `SharedSeverityTests
          .test_severity_order_is_the_same_object_as_reviews` pattern:
          `self.assertIs(verdicts.is_nonempty_str, findings.is_nonempty_str)` in a small new
          test class (e.g. `SharedPredicateTests`) in test_verdicts.py.
        - Run the full existing suite: `python3 -m unittest test_findings test_verdicts
          test_run_adjudication` from `launchpad/review-agent/` (add any other test module in
          that directory that imports findings/verdicts, found via `grep -l "^import findings\|^import verdicts" launchpad/review-agent/test_*.py`).
        done when: every test module found by that grep passes with zero failures/errors, and
          the new identity-check test passes.

STEP 5  Re-run the reproduction probe post-fix and record before/after counts   [needs 2]
        - Re-run the exact probe script used pre-fix (six cases: "   ", 42, True, ["x"],
          {"a": 1}, "") and record the violation count for each, confirming the fix without
          re-deriving the probe from scratch.
        done when: probe output is captured showing 1+ violation for all six cases (previously
          0 for five of six), matching Step 2's done-when.

PARALLEL  Step 1 has no dependency on prior work in this plan and could run alone, but every
          later step depends on it (either directly or transitively), so in practice this plan
          is a straight sequential chain — no genuine fan-out opportunity. Steps 3 and 5 both
          only need Step 2, and are independent of each other (different files: test_findings.py
          vs. an ad-hoc probe script), so they could run as two parallel subagents once Step 2
          lands; Step 4 needs both 1 and 3 to complete first regardless.
GATES     serina:review-code applies after Step 2 (the behavioural fix + the shared-predicate
          move). serina:review-tests applies after Step 3 and Step 4 (new tests must not be
          vacuous — the plan's own done-when for Step 3 requires demonstrating each new test
          fails pre-fix). qa explore mode does not apply: findings.py/verdicts.py are pure
          validation functions over dicts with no runtime interface (CLI, API, UI) to exercise
          exploratorily — the reproduction probe in Step 5 already is the direct-execution
          equivalent for this kind of module. serina:review-final applies once the branch is
          ready to merge, per this repo's normal PR flow.
BUDGET    Step 1 is the step most likely to eat the budget: it is a cross-file refactor (moving
          a function, changing an import from local-to-module-scope, updating two internal call
          sites in verdicts.py's validate()) rather than a pure one-line fix, and a mistake there
          (e.g. leaving a stale local import, or missing one of the two `findings_module.validate`
          call sites) would surface as a confusing NameError far from the actual cause.
OPEN      The issue has no stated `Size`; this plan assumed the smallest bracket given the
          issue's own tight scoping ("the one left standing") — flagged rather than silently
          picked. The issue does not say whether `is_int` (verdicts.py's sibling predicate,
          not implicated in this bug) should move alongside `is_nonempty_str` for consistency;
          this plan leaves `is_int` in verdicts.py untouched, since findings.py has no current
          need for it and moving it is not required to fix #283.
LEFT OUT  No changes to contain.py or any other dimension-specific file. No changes to
          run_adjudication.py — its existing `verdicts.is_nonempty_str(...)` call sites keep
          working unmodified by construction (Step 1's re-export), so it needs no edits and no
          new tests of its own; test_run_adjudication.py is still run in Step 4 as a regression
          check, not because it's expected to change. No change to `is_int` (see OPEN). No
          change to FINDINGS.md or ADJUDICATION.md normative text — the contract they describe
          ("evidence must be set, non-null, non-empty") is unchanged; only the code's fidelity
          to it is being corrected.
