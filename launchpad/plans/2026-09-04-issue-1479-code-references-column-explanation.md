Issue #1479 — bug: code-references section 2 points at an explanation that does not cover the path:line:col case
Stated size: no `Size` line in the issue; assumed <= 30 minutes given confirmed Low severity  →  cap: 5 steps

ALREADY TRUE  (verified against git and the file, not notes)
  - `launchpad/docs/corpus/standards/code-references.md` exists at HEAD (aef93f2c2, `launchpad`
    branch) and is the only file this issue names.
  - Section 2's table (line 147) reads: `| Path with a column or fragment | …kind.rs:219:5,
    …kind.rs#symbol=Kind | error | — not a supported form; see *Enforcement* for the misleading
    message |` — one row, one pointer, covering two examples.
  - Section "Enforcement" item 4 (lines 245-249) reads: "A citation containing no whitespace that
    matches no other form falls through to the repository-path rule, so `#1459` and
    `launchpad-26/buzz#1459` are reported as paths that 'do not resolve to a real file in the
    repository'." This is the only prose the pointer resolves to.
  - Reproduced directly against current `launchpad/project-intelligence/corpus/validate.py`:
    `_FILE_POSITION_RE.match('crates/buzz-core/src/kind.rs:219:5').groupdict()` returns
    `{'path': 'crates/buzz-core/src/kind.rs:219', 'start': '5', 'end': None}` — the regex DOES
    match, taking `_classify_citation`'s POSITION branch (`validate.py` line ~745-754), not the
    whitespace-free fallthrough at line ~762 that item 4 describes. `kind.rs#symbol=Kind` (no
    colon) does take the whitespace-free fallthrough, so item 4 is already correct for that half
    of the row's example pair.
  - No `Size` line, no existing WIP commits on this branch beyond the merge base, no related
    open PR touching this file (git log shows no in-flight work on this path).

STEP 1  Draft the corrected prose for Enforcement item 4                              [independent]
        Extend item 4 to state both mechanisms that reach the same rejection message, keeping
        each anchored to a concrete example from section 2's row:
          (a) existing case — a whitespace-free citation matching no recognised form (`#1459`,
              `launchpad-26/buzz#1459`, and the fragment example `kind.rs#symbol=Kind`) falls
              through to the repository-path rule directly.
          (b) new case — a `path:line:col` citation (`kind.rs:219:5`) DOES match
              `_FILE_POSITION_RE`, because the pattern's non-greedy path group backtracks until
              the trailing suffix satisfies `:\d+(-\d+)?$` at end-of-string, which only happens
              at the LAST colon. The path capture ends up as `crates/buzz-core/src/kind.rs:219`
              (it absorbs the first colon and the middle digits as literal trailing text, it is
              not truncated at the first colon), and `5` is captured as a bogus start line. This
              reaches the repository-path rule through the POSITION branch, not the fallthrough,
              and fails for the same reason (no file by that mangled name exists) — hence the
              same message despite the different route.
        done when: the new paragraph names both routes, cites the correct `validate.py` mechanism
        for each (whitespace-fallthrough vs. POSITION-branch regex absorption), and does not
        claim the path is "truncated at the first colon" (it is not — verified by the reproduction
        above).

STEP 2  Apply the edit to code-references.md                          [needs 1]  ← RUNS HERE
        Edit only `Enforcement` item 4 (and, if needed for clarity, section 2's table-row footnote
        text) in `launchpad/docs/corpus/standards/code-references.md`. Do not touch
        `validate.py` — this is a documentation-only fix. Section 2's pointer text ("see
        *Enforcement* for the misleading message") stays a single pointer to item 4, since item 4
        now covers both example citations in that row.
        done when: `git diff` shows changes confined to
        `launchpad/docs/corpus/standards/code-references.md`, item 4 discusses both the
        `#symbol=Kind`-style fallthrough and the `:219:5`-style POSITION-branch case, and the
        `does not resolve to a real file in the repository` message text is preserved verbatim
        (it must still match what `validate.py` actually emits).

STEP 3  Re-verify the corrected text against current validate.py behaviour            [needs 2]
        Re-run the two reproductions from ALREADY TRUE (the `#symbol=Kind` fallthrough path and
        the `:219:5` POSITION-branch path) against `launchpad/project-intelligence/corpus/
        validate.py` at the worktree's HEAD, and re-read the edited paragraph side by side with
        both outputs.
        done when: both reproductions still produce the groupdict/route described in the new
        prose, with no discrepancy between the doc's claim and the live code.

STEP 4  Run the corpus validator against the edited doc                               [needs 2]
        `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root (the file
        carries frontmatter evidence citations of its own, several already pointing at this same
        file and at `validate.py`'s line-level behaviour, so an edit to prose near those citations
        is worth a real validator pass, not just a visual check).
        done when: the command exits 0, or any non-zero exit is shown to be pre-existing and
        unrelated to this change (reproduce the same exit against the pre-edit file on the same
        HEAD to confirm).

STEP 5  Commit                                                          [needs 3, 4]
        `git commit -s` with a message describing the doc fix and referencing #1479. No code
        files staged.
        done when: `git status` shows a clean tree, `git log -1 --format=%B` contains a
        `Signed-off-by` trailer, and the commit touches exactly one file.

PARALLEL  Step 1 (drafting the prose) can be thought through independently of any file state, but
          since this is a 5-step single-file plan there is no real benefit to fanning it out —
          steps 2-5 are strictly sequential (same file, then validate, then commit). Run this
          plan as one continuous pass rather than dispatching subagents.
GATES     `review-code` does not apply (no code change). `review-a11y` does not apply (no UI).
          `review-tests` does not apply (no tests, docs-only). `qa` explore mode does not apply —
          there is no runtime interface to exercise beyond the validator invocation already
          covered in step 4. `review-final` runs at hand-off per this repo's build-change →
          review-gate pipeline, and per prior findings in this repo it will likely fall back to a
          draft PR via `pr-gate.sh`'s documented escape valve since this pipeline does not produce
          a `review-final` ledger verdict — expected, not a failure to fix.
BUDGET    Step 1 (getting the POSITION-branch explanation exactly right without overclaiming or
          contradicting the issue's own — slightly imprecise — "truncated at the first colon"
          framing) is the step most likely to eat the budget; everything after it is mechanical.
OPEN      Whether section 2's table row itself should also gain a footnote distinguishing the two
          examples, or whether extending item 4 alone (leaving one shared pointer) is sufficient.
          This plan takes the latter, lighter-touch approach per the issue's own "Expected"
          section, which offers both as acceptable outcomes.
LEFT OUT  Any change to `validate.py`'s actual regex or classification behaviour — #1459 (line
          numbers not checked against file length) and the POSITION-branch mangling itself are
          separate, already-tracked defects; this issue is scoped to the documentation pointer
          only, and the standard's own "Enforcement" section states that when the document and
          the validator disagree, the validator is fixed by fixing the document, not by changing
          the validator's behaviour to match a document's claim.
