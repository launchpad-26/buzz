# FALSIFIABILITY — what would show this recording is not real

`pr-261-comments.json` and `pr-264-comments.json` claim to be the actual,
unedited bodies of four real GitHub PR comments. That claim is checkable,
not just asserted:

1. **Regeneration.** `python3 ../generate.py` re-fetches both PRs live via
   `gh api` and reproduces these two files. If either file's committed bytes
   ever silently diverged from a hand edit, `generate.py` writing fresh
   bytes and `git diff` showing a change is exactly how that would be
   caught — the same mechanism `fixtures/adjudication/`'s own
   `test_adjudication_fixtures.py` regeneration check relies on, applied
   here as a manual re-run rather than an automated one (no seed/nonce
   scheme exists for raw comment bodies to pin against in CI the way an
   adjudication document's nonce does).

2. **Cross-check against the live control.** `check_verdict_resolution.py`
   (#287 STEP 5, network-required) resolves PR #261 and PR #264 by calling
   `pr_comments.fetch_and_locate` directly against the live API — it does
   not read these recordings at all. `test_verdict_resolution.py` (#287
   STEP 6, no network) resolves the SAME two PRs by loading these
   recordings through `pr_comments.from_items` instead. Both paths are
   asserted to reach the identical outcome: PR #261 accepts comment
   `5364261676` and reports `5364185647` superseded; PR #264 accepts
   `5364504768` (the Blocker promotion) and reports `5364221899`
   superseded. If a recording had been hand-edited to make a test pass —
   trimming a row, closing an unclosed fence, changing a severity — the
   live control and the fixture-based test would disagree, and disagreeing
   is a red suite, not a silent divergence.

Both files were produced from a single fetch to `gh api
repos/launchpad-26/buzz/issues/{261,264}/comments --paginate --slurp` on
2026-08-27, filtered to the two comment ids ADJUDICATION.md names for each
PR, with `id`/`created_at`/`user.login`/`body` kept verbatim. No row, verdict,
or severity value in either file was typed by hand.
