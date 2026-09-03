# Issues #1482, #1483, #1459 — corpus validator soundness gaps

Stated size: none of the three issues carries a `Size` line  ->  cap: 8 steps

No issue carries a `Size` line; this skill's rule is normally to ask before writing
rather than guess. Proceeding without asking because the task was already explicitly
scoped by the dispatching instruction (three named issues, one file, "keep the diff
tight and behavior-preserving"), so 8 steps (this skill's "30-60 minute" band) is used
as a judgment call, not a guess at the issue author's intent — flagged again in OPEN.

ALREADY TRUE (verified against git, not notes)
  - `launchpad/project-intelligence/corpus/validate.py` was added by #623 (PR #1422,
    commit `e4e6823cd9`) and has one follow-up commit since (`2ff951e7b5`, NaN/Infinity
    confidence fix) — no open work-in-progress on this file.
  - Worktree `/home/serina/Launchpad/buzz/__worktrees/fix-issue-1482-1483-1459-corpus-validate-soundness`
    exists, is on branch `fix/issue-1482-1483-1459-corpus-validate-soundness` tracking
    `origin/launchpad`, and `git status --short` is clean.
  - All three bugs are reproduced against current code (agentic-debugging +
    root-cause-analysis both run, verdicts final):
    - #1482: stray `---\n` inside frontmatter silently truncates the parsed dict via
      `text.split("---\n", 2)`'s unconditional maxsplit=2 (line ~200); a `relationships`
      block placed after the stray delimiter never reaches `data`, so
      `find_unresolved_relationship_targets` never sees the bad target. PASS/exit 0
      confirmed where FAIL is correct.
    - #1483: same split call; a file with one delimiter (no close) makes the split
      return 2 elements, and unconditional `_, frontmatter, _body = ...` raises
      `ValueError: not enough values to unpack (expected 3, got 2)`, which
      `_parse_failure` prints verbatim because it isn't one of the deliberate,
      fixed-string ValueErrors the function already special-cases.
    - #1459: `_classify_citation`'s positional branch (line ~745-754) extracts
      `start`/`end`, checks only internal consistency, then discards them before
      calling `_classify_repo_path`, which never compares them to the file's actual
      line count. `Justfile:999999` (~1005 lines) returns `ok`, identical to a
      citation whose line exists.
  - `tests/test_validate.py::CitationFormTest::test_file_line_citation_accepted`
    (~line 432-445) currently pins the pre-fix #1459 behavior on purpose (its own
    docstring names this a previously-deferred finding) — this exact assertion goes
    false once #1459 is fixed and must be rewritten, not left stale.
  - Existing fixture convention confirmed: `tests/fixtures/invalid/<name>/node.md`,
    one node per directory, asserted against via `validate.validate_corpus(INVALID_DIR
    / "<name>")` in a `unittest.TestCase`. `unresolved-target/node.md` is the closest
    existing analog for #1482's fixture (same relationship-target shape, different
    delimiter placement).

STEP 1  Fix `_load_frontmatter`'s delimiter parsing for #1482/#1483        [independent]
        (same function, same root call)
        - Replace the unconditional `text.split("---\n", 2)` / 3-name destructure with
          logic that: (a) requires a leading `---\n` (existing check, unchanged); (b)
          finds the closing `---\n` deliberately rather than positionally — locate the
          frontmatter block by finding the FIRST `---\n` after the leading one, and
          treat that occurrence as the sole closer (i.e. `text.split("---\n", 2)` is
          fine for finding *where* the close is, but the bug is that nothing checks the
          captured frontmatter span for a THIRD occurrence hiding inside it); the
          simplest correct fix per the issue's suggested direction: after computing
          `frontmatter` from a 2-way split (open delimiter consumed, then split once on
          the next `---\n`), explicitly detect whether `frontmatter` itself still
          contains a `---\n` line and raise `ValueError` naming it if so, rather than
          silently accepting whatever the second delimiter produced.
        - Check `len(parts)` (or equivalent) before destructuring, and raise
          `ValueError("no closing '---' frontmatter delimiter")` (or matching fixed
          string in the sibling style) when the closing delimiter is absent, instead of
          letting the destructure raise Python's own unpacking error.
        - Both changes stay inside `_load_frontmatter`; no other function's signature
          or behavior changes.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py --root
        /tmp/repro-1482` reports `FAIL ... relationship target 'no-such-node-anywhere'
        does not match any known node id` (not PASS), and `python3 .../validate.py
        --root /tmp/repro-1483` reports a fixed, readable message (not `not enough
        values to unpack`).

STEP 2  Fix `_classify_citation`'s positional-form branch for #1459    [independent]
        - After `_classify_repo_path` returns `CitationVerdict("ok")` for a resolved,
          existing, in-repo file, additionally check `start` (and `end`, if present)
          against that file's actual line count before returning `ok`. The cleanest
          shape: keep `_classify_repo_path` as the existence/containment authority (its
          docstring and callers elsewhere are unaffected — it's also called for bare
          paths with no position), and add the line-count check in the caller
          (`_classify_citation`'s positional branch) once `_classify_repo_path`
          confirms the file resolves — read the file, count lines, compare.
        - Reject (status "error", not "unverified" — this is verifiable-by-nature per
          the issue's argument, not a legitimate UNVERIFIED case) when `start` (or
          `end`) exceeds the file's line count. Message must not echo the citation
          value (matches this file's existing redaction discipline throughout) —
          state that the position is out of range, name nothing from the citation
          itself beyond what's already safe to print (the existing detail strings for
          this branch already avoid echoing values; keep that pattern).
        - Update the stale inline comment (line ~750-751) that frames this as
          out-of-scope "staleness detection" — replace with the corrected framing:
          bounds-checking an already-open file's line count is verifiable by nature and
          is checked here; genuine staleness (whether cited *content* still matches) is
          the deferred, separate concern.
        done when: `python3 -c "...; v._classify_citation('Justfile:999999', root)"`
        returns `status='error'` (not `'ok'`), same for `Justfile:1-999999`, while
        `Justfile:1` and a genuinely in-range line/range still return `status='ok'`.

STEP 3  Add regression fixtures and tests for #1482 and #1483          [needs 1]  ← RUNS HERE
        - New fixture `tests/fixtures/invalid/stray-frontmatter-delimiter/node.md`:
          reuse `unresolved-target/node.md`'s shape (valid frontmatter incl. an
          `evidence` entry citing `Justfile`, so schema validation passes on the parts
          that DO get parsed pre-fix) but insert the stray `---\n` + `relationships`
          block naming `no-such-node-anywhere` exactly as in the issue's repro, before
          the real closing `---`. Test (new `TestCase`, following
          `UnresolvedRelationshipTargetTest`'s pattern): assert
          `validate.validate_corpus(...)` reports exactly one error and it names the
          stray delimiter (or the resulting parse failure) — NOT a clean PASS, and
          confirm it is not the unrelated "relationship target" message that would
          only appear if the fix routed through schema/relationship checking instead
          of the frontmatter parse itself. Match whatever message step 1 actually
          produces.
        - New fixture `tests/fixtures/invalid/missing-closing-delimiter/node.md`: one
          `---\n` opener, no closer, matching the issue's repro. Test: assert exactly
          one error, its message contains something like "closing" and "delimiter",
          and does NOT contain "unpack" or "expected 3, got 2" (pins the old failure
          mode is gone, not just that a message exists).
        - Both tests must fail against the pre-fix `_load_frontmatter` (confirm by
          running them against a stash of the current code, or reasoning from the
          already-captured pre-fix repro output — both fixtures reproduce exactly the
          repro transcripts already captured) and pass after step 1.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` passes, including
        the two new tests, and fails if step 1's changes are reverted.

STEP 4  Add regression tests for #1459, update the entangled existing test  [needs 2]
        - Add direct `_classify_one`-based tests (matching `CitationFormTest`'s
          existing convention, not a fixture dir — this is a unit-level classifier
          check, same as the other citation-form tests in that class) asserting:
          `Justfile:999999` and `Justfile:1-999999` are no longer `ok` (now `error`,
          per step 2), and an in-range line/range (e.g. `Justfile:1`, already covered
          by `test_line_numbers_are_one_based`, and a fresh in-range multi-line range)
          still returns `ok`.
        - Rewrite `CitationFormTest.test_file_line_citation_accepted` (~line 432-445):
          it currently asserts `Justfile:1077` passes clean, which is now false. Change
          it to assert the out-of-range citation is REJECTED (not accepted), and
          rewrite its docstring to state plainly that the previously-deferred,
          tracked finding is now resolved by #1459's fix — remove the "do not fix this"
          language, since leaving it would misdescribe the shipped behavior to the next
          reader.
        - Do not renumber `Justfile`'s line count by hand each time — use a
          dynamically-computed out-of-range value (e.g. actual line count + 1) in the
          new/updated tests rather than a hardcoded guess, so the test doesn't rot if
          `Justfile` is edited later. (The removed old test used a hardcoded guess;
          don't repeat that in its replacement.)
        done when: the full test suite passes, `test_file_line_citation_accepted`
        (renamed if appropriate to reflect the new assertion) fails if step 2 is
        reverted, and no test in the file still asserts the old out-of-range-passes
        behavior anywhere.

STEP 5  Run the full existing test suite and confirm no other test broke  [needs 4]
        - `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
          -p "test_*.py"` — every test must pass, not just the new ones. Pay particular
          attention to any other test citing a `path:line`/`path:start-end` form against
          a real repo file (grep the test file for `_FILE_POSITION_RE`-shaped literals
          like `":1-5"`, `":1"`, `":0"` beyond the ones step 4 already touches) to
          confirm none of them relied on an out-of-range line incidentally passing.
        done when: full suite green, and a `grep -n ':[0-9]' tests/test_validate.py`
        pass confirms every remaining positional-citation literal in the file is
        genuinely in-range for the file it cites (or is deliberately testing the
        malformed/error path, which stays unaffected by steps 1-2).

STEP 6  Run the validator against the REAL corpus, check for new false FAILs [needs 5]
        - Run `python3 launchpad/project-intelligence/corpus/validate.py` (no `--root`
          override — real `launchpad/docs/corpus`).
        - Compare exit code and error count against a baseline run of the same command
          on `origin/launchpad` (pre-fix) to isolate what step 1/2 changed, if
          anything.
        - If the real corpus now reports NEW failures because of the #1459 bounds
          check (an existing citation whose line number has drifted out of range) or
          the #1482/#1483 delimiter fix (an existing node with a stray or missing
          delimiter — unlikely but check), do NOT edit corpus content to silence it.
          Report the finding plainly in the PR body / final report and let the
          validator's stricter, correct check stand. File a followup issue only if the
          finding names a real corpus defect worth tracking separately from this PR.
        done when: the real-corpus run's output (pass/fail, and full list of any new
        errors) is captured and reported, whichever way it comes out.

STEP 7  `just ci` / repo-wide format and lint gate                     [needs 6]
        - Buzz's `AGENTS.md` requires `just ci` before any PR touching tracked files.
          Given this is a Python-only change under `launchpad/`, confirm which lanes
          actually apply (this repo's Rust/desktop/mobile lanes are unaffected by a
          pure-Python file, but pre-commit/pre-push hooks may still run repo-wide
          formatting checks) — run what's scoped to this change rather than the full
          multi-language suite if `just ci` proves excessive for a two-function Python
          diff; note in the PR which checks ran.
        done when: whatever gate actually applies to this diff (hooks on commit/push at
        minimum) passes clean.

STEP 8  Commit, push, open PR                                          [needs 7]
        - `git commit -s` (DCO required, per AGENTS.md).
        - Push branch, `gh pr create` as a standalone command (no `cd` prefix — this
          repo's `pr-gate.sh` hook rejects `cd <dir> && gh pr create` as one call), base
          `launchpad`, body includes "Closes #1482", "Closes #1483", "Closes #1459",
          and step 6's real-corpus finding (clean, or named if not).
        - Match the `by:agent` label convention if recent merged agent-authored PRs use
          it (check `gh pr list --search "is:merged label:by:agent"` first).
        - Expect the PR to land as draft via `pr-gate.sh`'s documented escape valve if
          the `review-final` ledger verdict isn't produced by this pipeline — this is
          expected, not a failure to chase.
        done when: PR is open (draft or ready), body contains all three "Closes #N"
        lines, and the branch's HEAD is the pushed commit.

PARALLEL
  Steps 1 and 2 are independent (different functions, `_load_frontmatter` vs.
  `_classify_citation`/its positional branch) and could run as parallel subagents.
  Steps 3 and 4 each depend on their respective fix (3 needs 1, 4 needs 2) and touch
  the same test file, so once both fixes land, 3 and 4 should run sequentially against
  the same file rather than in parallel to avoid merge conflicts on
  `tests/test_validate.py`. Steps 5-8 are strictly sequential (each needs the prior
  step's evidence).

GATES
  `review-code` and `review-tests` apply after step 4 (implementation + test diff
  complete) and before step 7. `review-final` applies to the whole branch before PR
  open, per this repo's process, but per the task's own note, `pr-gate.sh` requires a
  `review-final` ledger verdict this plan/build pipeline doesn't produce — expect the
  hook's draft-PR escape valve, not a hard block. `qa` explore mode does not apply:
  this is a CLI validator script with no interactive runtime surface beyond argv/exit
  code, already exercised directly by steps 1, 2, and 6's manual invocations — there is
  no additional interface to explore beyond running the script, which those steps
  already do.

BUDGET
  Step 1 (the frontmatter delimiter fix) is most likely to eat the budget: unlike
  step 2's additive bounds check, it requires a genuinely different parsing strategy
  (not just an extra guard clause) and both #1482 and #1483 hinge on getting the new
  logic exactly right, since a mis-scoped fix (e.g. rejecting a LEGITIMATE `---` that
  happens to appear inside a YAML block scalar / multi-line string value inside the
  frontmatter) would newly reject valid corpus content in step 6. Watch for this
  specifically: a `---` line only signals a delimiter when the FRONTMATTER YAML DOES
  NOT LEGITIMATELY CONTAIN ONE — YAML block scalars (`|`, `>`) can contain a literal
  line reading exactly `---` as data, not structure. If step 6 finds this in real
  content, the fix in step 1 needs revisiting before merge, not the corpus.

OPEN
  - No issue carries a `Size` line; step count capped at 8 by this plan's own judgment
    rather than the issue's stated size, per the skill's normal rule ("no Size line →
    ask before writing"). Proceeding without asking because the task was already
    explicitly scoped (three named issues, one file, "keep the diff tight") by the
    instruction that dispatched this planning pass — flagged here rather than silently
    assumed.
  - Step 1's exact mechanism (detect-and-reject vs. a different splitting strategy
    entirely) is left to the implementer's judgment within the done-when constraint;
    the plan intentionally doesn't prescribe regex vs. line-by-line scanning since
    either can satisfy the done-when and the issue itself says "not prescribing a fix."
  - Whether an out-of-range positional citation should be "error" vs "unverified" is
    treated as settled (error) per the issue's own argument and this plan's step 2 —
    not re-litigated here, but noted as a judgment call the plan is making explicit
    rather than the issue mandating in so many words.

LEFT OUT
  - The issue's own "stricter version" suggestion for #1482 ("refuse any node whose
    body begins with something that parses as YAML mapping keys") is explicitly NOT
    required — the issue calls it optional, and the detect-and-reject approach in step
    1 satisfies the issue's actual repro and stated fix direction without that extra
    scope.
  - No corpus content is edited by this plan under any circumstance, even if step 6
    finds a real false-positive — per the dispatching instruction's explicit
    constraint, that's a followup issue, not this PR's job.
  - Real staleness detection (verifying cited *content*, not just line-count bounds)
    stays out of scope, matching #1459's own framing of what it is and is not asking
    for.
