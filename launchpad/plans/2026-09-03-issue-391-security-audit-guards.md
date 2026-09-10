Issue #391 — bug: ignore-coverage passes on a negated pattern, and the newly-hidden WARN swallows git failures
Stated size: no `Size` line in the issue (checked 5 recent `type:bug` issues in this repo — none carry one, so this appears to be a bug-report convention, not an omission)  →  cap: 8 steps, sized by scope alone as ~30-60 minutes (two narrowly-scoped functions, existing test scaffolding already in place for both files)

ALREADY TRUE  (verified against the repo and by direct reproduction, not notes)
  launchpad/scripts/security_audit_ignore_coverage_check.py `run()` (:65-98) checks only
    literal-line presence (`pattern not in line_set`) — no ignore-effect check exists.
    Reproduced: a `.gitignore` containing `*.pem` then `!*.pem` still returns PASS, while
    `git status --ignored=matching` / `git add -n` on a sample `.pem` file confirm it is
    genuinely NOT ignored.
  launchpad/scripts/security_audit_tracked_files_check.py `_check_newly_hidden_tracked_files`
    (:88-150) returns `[]` on `git fetch` failure (:104-112, bare `except: return []`) and
    `continue`s past a failed per-file `git diff` (:116-125) with no distinguishing signal.
    Reproduced: a repo with no reachable `origin` remote and `GITHUB_BASE_REF` set makes the
    full `run()` report a clean `PASS`, indistinguishable from "nothing newly hidden."
  The sibling `_tracked_paths()` in the same file already fails closed: returns `None` on
    `git ls-tree` failure, and `run()` (:195-196) maps that to `Status.INDETERMINATE` — this
    is the existing vocabulary/pattern the fix mirrors, not a new one being invented.
  `security_audit_core.py` defines four statuses (PASS/FAIL/WARN/INDETERMINATE) and documents
    INDETERMINATE as "must never render or count as pass."
  Existing test suites: `test_security_audit_ignore_coverage_check.py` (12 tests, real files
    in a plain tmpdir, no git) and `test_security_audit_tracked_files_check.py` (real git
    repos built in tmpdirs, `_NoUpstreamMixin` mocks only `fetch_upstream_blobs`).
  `git check-ignore --no-index` still requires an actual git repository (confirmed:
    `fatal: not a git repository` in a plain temp dir) — this rules out a full git-effect
    implementation without also converting all 12 existing ignore-coverage tests to real git
    repos (see LEFT OUT).

STEP 1  Add negation-awareness to the ignore-coverage check.                    [independent]
        In `security_audit_ignore_coverage_check.py::run()`, for each required pattern already
        found present as a literal line, find the LAST line index equal to the pattern and the
        LAST line index equal to `"!" + pattern`. If a negation index exists and is greater than
        the pattern's index, the pattern is present but negated later in the file — add it to
        `missing` with a message naming the negating line, distinct from "not present at all."
        Update the module docstring to state this handling and its remaining limitation (a
        differently-spelled negation, e.g. a character-class variant of the same glob, is not
        caught) — mirroring how the respelling-drift trade-off is already documented there.
        done when: the debugging-phase reproduction (`*.pem` then `!*.pem`) now returns FAIL,
        and the reverse order (`!*.pem` then `*.pem`) still returns PASS (order-sensitivity,
        matching real `git check-ignore` last-rule-wins semantics verified during debugging).

STEP 2  Regression tests for the negation case.                                     [needs 1]
        Add to `test_security_audit_ignore_coverage_check.py`: (a) full coverage plus a later
        exact negation of one required pattern → FAIL, detail names the pattern; (b) negation
        appearing BEFORE the pattern → still PASS, proving the fix is order-aware rather than
        "any negation line anywhere fails."
        done when: `python3 -m pytest launchpad/scripts/test_security_audit_ignore_coverage_check.py -q`
        passes including the two new tests, and manually reverting STEP 1 makes test (a) fail.
        ← RUNS HERE (first demonstrable, independently-testable fix)

STEP 3  Make the newly-hidden-file heuristic's failures distinguishable from "found nothing." [independent]
        In `security_audit_tracked_files_check.py::_check_newly_hidden_tracked_files` (a
        different file from steps 1-2), change the return type to `Optional[List[str]]`. Return
        `None` immediately on `git fetch` failure (unchanged trigger, changed signal). Track a
        `diff_failed` flag when a per-file `git diff` returns non-zero; at the end, if
        `diff_failed` is set and no findings were
        collected, return `None` — a real finding from another watched gitignore path still wins
        over an unrelated file's diff failure rather than being masked by it. Update the
        function's docstring to state the `None` (could not determine) vs `[]` (nothing found,
        or not in PR mode) contract explicitly.
        done when: the debugging-phase reproduction (no reachable `origin`, `GITHUB_BASE_REF`
        set) calling `_check_newly_hidden_tracked_files` directly now returns `None`, not `[]`.

STEP 4  Wire the `None` signal into `run()`.                                        [needs 3]
        In `run()`, when `_check_newly_hidden_tracked_files` returns `None`, return
        `CheckResult(NAME, Status.INDETERMINATE, ...)` with a detail naming that the heuristic
        could not run (git fetch/diff failed), not that nothing was found. Place this branch
        after the existing FAIL (cohort hits) and INDETERMINATE (unknown ownership) branches,
        so a real cohort-owned sensitive file still takes priority over an unrelated heuristic
        failure, and before the existing WARN/PASS branches.
        done when: the fetch-failure reproduction run against the full `run()` (not just the
        helper) now returns `Status.INDETERMINATE`, not `Status.PASS`.

STEP 5  Regression tests for the git-failure case.                                  [needs 4]
        Add to `test_security_audit_tracked_files_check.py`: (a) `GITHUB_BASE_REF` set, no
        reachable `origin` remote, no sensitive tracked files → `run()` is INDETERMINATE, detail
        distinguishes "could not determine" from "nothing found"; (b) same fetch failure but with
        a real cohort-owned sensitive tracked file also present → `run()` still FAILs (priority
        preserved — a real hit is never masked by an unrelated heuristic's failure).
        done when: `python3 -m pytest launchpad/scripts/test_security_audit_tracked_files_check.py -q`
        passes including the two new tests, and reverting STEP 3/4 makes test (a) fail (returns
        PASS instead of INDETERMINATE).

STEP 6  Full verification against the real repo.                                    [needs 5]
        Run both edited test files together, plus the existing full script-family suite
        (`test_security_audit.py`, `test_security_audit_classifier.py`,
        `test_security_audit_secrets_check.py`, `test_security_audit_agent_surface_check.py`,
        `test_security_audit_gitleaks_ruleset.py`) to confirm nothing else regressed. Then run
        `security_audit.py` against this worktree's actual root to confirm `ignore-coverage` and
        `tracked-sensitive-files` both still report their pre-fix real-world result (PASS) —
        proving the fix changes behaviour only for the negated/git-failure cases, not the
        ordinary case.
        done when: all listed test files pass, and
        `python3 launchpad/scripts/security_audit.py <worktree-root>` exits 0 with both checks
        shown as PASS.

PARALLEL: Steps 1-2 (ignore-coverage file) and 3-5 (tracked-files file) touch entirely separate
  files and could run as two parallel subagents; step 6 needs both branches done first. Given
  the total size (two files, ~578 lines of existing code+tests combined), running serially by
  one implementer is also reasonable and avoids merge coordination for a change this small.
GATES: review-code after step 6 (the order-sensitivity logic in step 1 and the
  priority-ordering in step 4 are the two places a subtle bug could hide). review-tests after
  step 6 (confirm every new test can actually fail — flip the corresponding fix and check, per
  this plan's own done-when conditions). qa explore mode does not apply: this is a CI script
  with no runtime UI or API surface to explore interactively — its only "runtime" is the test
  suite and the direct `security_audit.py` invocation already exercised in step 6.
BUDGET: Step 5(b) is most likely to eat time — constructing a fixture where the fetch genuinely
  fails AND a real cohort-owned sensitive file is simultaneously tracked, without the easier FAIL
  path accidentally short-circuiting before the fetch is even attempted, requires reading the
  existing `run()` ordering carefully (sensitive-hit partitioning happens independently of and
  before the newly-hidden check, so this should be straightforward, but it is the step most
  likely to need a re-read of `run()`'s branch order if the first attempt gets it wrong).
OPEN: No `Size` line exists on the issue; sizing here is inferred from scope. If a stricter
  process wants issues re-filed with an explicit Size line before planning, this plan should be
  re-confirmed against that line once added — flagging rather than blocking on it, since the
  scope is unambiguous and small.
LEFT OUT: A full `git check-ignore`-based effect verification (the issue's first suggested
  option) is deliberately not implemented. It requires an actual git repository even with
  `--no-index` (confirmed by reproduction), which would force all 12 existing
  ignore-coverage unit tests — currently plain non-git tmpdirs — to become real git
  repositories, a blast-radius disproportionate to a bug the issue itself marks non-blocking.
  The chosen fix (exact literal-negation detection, ordered correctly) resolves the issue's
  actual reproduction case without that cost; the residual gap (a differently-spelled negation
  escaping detection) is documented in the module docstring per the issue's second acceptable
  option. Not touching `_partition_by_ownership`, `_matches_sensitive_shape`, `security_audit_core.py`,
  or any other check in the family — scope is exactly the two named functions.
