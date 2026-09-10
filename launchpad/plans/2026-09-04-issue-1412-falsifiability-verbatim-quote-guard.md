Issue #1412 — bug: FALSIFIABILITY.md's verbatim-quote guard proves substring containment, not exact match
Stated size: no `Size` line on the issue  ->  cap: 5 steps (the issue's own "Suggested fix" section is narrow and fully specifies the change; treated as a ≤30-minute-class fix). Flagged here per plan-issue's rule rather than asked about, since the issue text and the dispatching instructions already pin the fix to one function in one file with no open design question.

ALREADY TRUE  (verified against git and the live files, not notes)
  - `launchpad/review-agent/check_adjudication.py` (999 lines) ends with a guard (lines 959-996) that:
    - builds `_all_recorded_evidence` / `_all_real_evidence` by concatenating EVERY `verdict_evidence`
      from every `*.json` under `fixtures/adjudication/recordings/` into one string (lines 970-979)
    - extracts each "Before" blockquote's quoted text from `FALSIFIABILITY.md` via regex (lines 981-992)
    - asserts `_quoted_text in _all_real_evidence` — Python substring containment (line 994)
  - `FALSIFIABILITY.md` has exactly four "Pair N" sections, each with a `Target: \`<finding_id>\`
    (dimension, \`<fixture>.json\`)` line immediately above its own "Before (full adjudicator.md), the
    actual recorded verdict:" blockquote — confirmed by reading the file directly (lines 38-41, 78-82,
    113-116, 152-156).
  - Reproduced both gaps against the CURRENT code (not hypothetically):
    - a truncated version of pair 1's real quote (dropped final ~12 words) is still `in`
      `_all_real_evidence` → `True` (should be rejected once "quoted in full" is enforced)
    - a fabricated string built from the tail of one recording's evidence + the head of the NEXT
      recording's evidence (in `_all_recorded_evidence`'s flat, cross-file order) is `in`
      `_all_real_evidence` → `True`, while it is absent from every SINGLE recording's evidence → `False`
  - Confirmed the fix direction is sound before writing any code: building a `finding_id ->
    verdict_evidence` lookup restricted to one target and requiring exact equality after whitespace
    normalization makes all four REAL pairs match exactly (`norm(quoted) == norm(real)` is `True` for
    all four), and makes both reproduced bad cases fail as intended.
  - `run_adjudication.make_replay_judge(replay_dir)` (run_adjudication.py:581-620) already builds
    exactly the `finding_id -> recorded output` lookup this fix needs (merges every `*.json` in a
    replay dir, skips `_`-prefixed keys, fails closed with a synthetic UNPROVEN/"no recording for this
    finding_id" entry when a finding_id is absent) — already imported and used elsewhere in this same
    file (e.g. lines 242, 521), so no new lookup logic needs inventing.
  - `git status` in the worktree is clean; `git log` shows no in-flight work touching this file.

STEP 1  Refactor the guard: per-target lookup + exact-equality-after-normalization        [independent] ← RUNS HERE
        In `check_adjudication.py`, replace the concatenation block (lines 970-979) and the substring
        assertion (line 994) with:
          - a small `_normalize_whitespace(text: str) -> str` helper (the same
            `" ".join(_re.sub(r"\s+", " ", text).split()).strip()` shape already duplicated at
            lines 978 and 987 — collapse both call sites onto this one helper)
          - a regex that captures BOTH the `Target: \`<finding_id>\`` and its own "Before" blockquote
            per pair, in document order (extend the existing `_before_heading` pattern rather than
            writing a second, unrelated one — reuse `(?:> .*\n?)+` for the blockquote body verbatim)
          - a lookup built via `run_adjudication.make_replay_judge(RECORDINGS_DIR)`, called once per
            pair as `_judge({"finding_id": fid}, {})` to fetch that ONE recording's `verdict_evidence`
            — not the concatenation
          - the assertion changed from `_quoted_text in _all_real_evidence` to
            `_normalize_whitespace(_quoted_text) == _normalize_whitespace(_target_evidence)`
        Keep the existing "exactly four 'Before' blocks" check. Do not touch `FALSIFIABILITY.md` or any
        `fixtures/adjudication/recordings/*.json` file — the fix is in the checker, not the fixtures.
        done when: `python3 check_adjudication.py` (run from `launchpad/review-agent/`) exits 0, and the
        four `pair N: the 'Before' quote is byte-verbatim against...` checks (now naming the specific
        target, not "some real recording") print PASS with no other check regressed.

STEP 2  Add regression coverage: truncated quote, cross-recording boundary, legit-still-passes  [needs 1]
        Add three new checks near the refactored guard, using the SAME `_normalize_whitespace` +
        per-target-lookup logic from Step 1, fed hand-built inputs (this file's own established idiom —
        see e.g. lines 767-787's "hand-built, fed straight to verdicts.validate" checks) rather than
        mutating the real fixtures:
          (a) Truncated-quote case: take a REAL target's `verdict_evidence` (e.g. pair 1's
              `74046c6b01333e4b` from `line-anchored-findings.json`), drop its final sentence, and
              assert the exact-equality check now rejects it — this must FAIL under the pre-fix
              substring check and PASS (i.e. correctly be rejected) under the post-fix logic.
          (b) Cross-recording boundary case: build a fabricated string from the tail of one real
              recording's evidence + the head of a DIFFERENT real recording's evidence (reproducing the
              exact construction used to confirm the bug above), targeted at the first recording's
              finding_id, and assert it is rejected — again must fail pre-fix, pass post-fix.
          (c) Regression guard: assert the real `FALSIFIABILITY.md`'s four pairs still produce zero
              violations under the new exact-equality-per-target logic (this already follows from
              Step 1's done-when, but give it its own explicit `check()` call so a future edit that
              breaks it fails loudly here rather than only via the top-level exit code).
        done when: `python3 check_adjudication.py` shows PASS for all three new checks, and running the
        same three checks against a scratch copy with Step 1's diff reverted shows (a) and (b) FAIL
        (proving they exercise the fixed code, not something else) while (c) still PASSes (proving the
        legit fixture was never the problem).

STEP 3  Full-file verification, no unrelated changes                                       [needs 2]
        Run `python3 check_adjudication.py` in full from `launchpad/review-agent/` and read the final
        `N failure(s)` line and exit code. Re-read the diff against `origin/launchpad` line by line —
        every changed line must trace back to the substring→exact-match fix or its regression tests;
        no drive-by renames or unrelated cleanup.
        done when: `python3 check_adjudication.py` reports `0 failure(s)` and exits 0; `git diff
        origin/launchpad -- launchpad/review-agent/check_adjudication.py` contains only the guard
        refactor and the three new checks.

PARALLEL  None of these can run in parallel — all three steps edit the same function in the same file
          in sequence (extract → cover with regression tests → verify the whole file). This is a single
          small, tightly-scoped change; fanning it out would cost more than it saves.
GATES     `review-code` and `review-tests` apply after Step 3 (this is a Python check-script change with
          new assertions, not a doc or config-only change). `qa` explore mode does not apply — there is
          no product-facing runtime interface (CLI arg surface, API, UI) being changed; the "explore"
          equivalent here is running `python3 check_adjudication.py` itself, which Steps 1-3's
          done-when conditions already require. `serina:build-change` hands off to its own review gate
          per the dispatching instructions; per this repo's `pr-gate.sh`, the PR will likely land as a
          draft (no `review-final` ledger verdict from this pipeline) — expected, not a defect to chase.
BUDGET    Step 1 (the regex extension: capturing `Target:` and its blockquote as one pair, in the right
          order, without over- or under-matching across pair boundaries) is the step most likely to eat
          the time budget — confirmed during investigation that a careless `re.DOTALL` flag makes the
          blockquote group swallow the entire rest of the document; the working pattern uses `[\s\S]*?`
          for the "skip to the next Before heading" span instead of enabling DOTALL globally.
OPEN      Whether to also assert the `Target:` line's named fixture filename (e.g.
          `line-anchored-findings.json`) matches the file the finding_id was actually found in, as a
          second, independent cross-check. The issue's suggested fix asks only for per-finding_id exact
          matching; finding_ids are content-derived hashes (via `findings.finding_id`) and already
          globally unique across all four real fixtures, so this second check would be redundant
          defense-in-depth, not a gap-closer. Left for a reviewer to request if they disagree.
LEFT OUT  No changes to `check_adjudication_mutations.py` (the STEP 11 mutation harness) — the issue's
          suggested fix and the dispatching instructions ask for direct regression checks in
          `check_adjudication.py` itself, not a new named mutation target; adding one would be scope
          growth beyond what either asks for. No changes to `FALSIFIABILITY.md` or any recording
          `*.json` — the real fixtures already pass the stricter check as confirmed during investigation,
          so there is nothing in the fixtures to fix.
