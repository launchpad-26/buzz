Issue #1785 — docs: INTERFACE.md cites AGENTS.md's superseded two-approving-reviews/admin:org claim
Stated size: none stated, treated as <=30 min (single-paragraph doc fix)  ->  cap: 5 steps

ALREADY TRUE  (verified against git and live GitHub API, not notes)
  - `launchpad/scripts/INTERFACE.md` line 48-50 (current `origin/launchpad` HEAD,
    aef93f2c2) still reads: "`launchpad/AGENTS.md` §6 states that the `launchpad`
    branch requires at least two approving reviews, that the ruleset enforcing it is
    unreadable without `admin:org`, and that a live PR's `reviewDecision` confirms
    review is *required* without exposing the count."
  - `launchpad/AGENTS.md` §6 (current HEAD) already carries the corrected text, landed
    in commit 87abbed795 (PR #1770, ADR-0052, merged 2026-08-28): "`launchpad` is
    protected, and thinner than this file used to claim. Measured 2026-08-28 via
    `repos/launchpad-26/buzz/branches/launchpad/protection`, which *is* readable:
    **one** approving review is required — not two — ... ADR-0019 recorded the count
    as 1 back on 2026-08-21; the 'two approving reviews' figure in this file came from
    a merge box read on 2026-08-13 and was already wrong."
  - Live verification performed this session (2026-09-04):
    - `gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name,protected}'` →
      `{"name":"launchpad","protected":true}` — protection/ruleset enforcement is
      active on the branch.
    - `gh api repos/launchpad-26/buzz/branches/launchpad/protection` → 404 for this
      session's token (no repo `admin` permission — `permissions.admin: false`,
      `maintain: true` on `repos/launchpad-26/buzz`). This is permission-dependent,
      not proof of "no protection" — confirmed by the `protected: true` flag above and
      by AGENTS.md's own dated record that a differently-permissioned session read this
      exact endpoint successfully on 2026-08-28.
    - `gh api repos/launchpad-26/buzz/rulesets` and
      `gh api repos/launchpad-26/buzz/rules/branches/launchpad` (also tried
      `?includes_parents=true` and the GraphQL `rulesets`/`branchProtectionRules`
      equivalents) → all return `200` with an empty list for this session, again
      consistent with missing repo-admin permission rather than "nothing enforces
      this branch".
    - `gh api orgs/launchpad-26/rulesets` → genuine `404` with an explicit
      `"needs the admin:org scope"` message. This is a **different, org-wide** endpoint
      than the branch-scoped one INTERFACE.md's paragraph is about. INTERFACE.md's own
      "Three rules a consumer can rely on" § bullet 2 (line 66) already makes this exact
      correct claim — "org-level rulesets are unreadable without `admin:org`" — and that
      line is NOT part of this issue's scope and must not be touched.
  - Conclusion: the review count is **1**, not 2 (uncontradicted by any live evidence,
    corroborated by ADR-0019 2026-08-21 and AGENTS.md §6's 2026-08-28 correction). The
    `admin:org` claim in INTERFACE.md's "Two gates" paragraph conflates the org-wide
    ruleset-listing endpoint (which genuinely needs `admin:org`, already correctly
    described elsewhere in the file) with the branch-scoped protection/ruleset read
    (which does not need `admin:org` — it needs repo `admin` permission, a different
    axis entirely). Both the specific number and the specific admin:org claim in the
    "Two gates" paragraph are stale.
  - The file already has a drift-prevention pattern to follow: line 34 defers to "the
    resolved AGENTS.md **and** CLAUDE.md" rather than restating their rules, and line 56
    already declines to restate the review count "because ... §6's figure could drift."
    The fix in this plan extends that same pattern to the paragraph's opening clause.

STEP 1  Re-confirm current text of both files at HEAD in the worktree            [independent]
        done when: `git show HEAD:launchpad/scripts/INTERFACE.md` (lines 48-56) and
        `git show HEAD:launchpad/AGENTS.md` (§6, the "launchpad is protected" bullet)
        match the "ALREADY TRUE" quotes above, confirming no further drift happened
        between the issue being filed and this build starting.

STEP 2  Edit `launchpad/scripts/INTERFACE.md`'s "Two gates, asked separately."   [needs 1]  ← RUNS HERE
        paragraph (lines 48-56) to stop restating the review count and the
        admin:org claim, and instead point at `AGENTS.md` §6 as the single source of
        truth for the review-requirement facts — matching the file's own existing
        drift-prevention pattern (line 34's AGENTS.md deferral, line 56's "could
        drift" reasoning). Keep the rest of the paragraph's actual contract
        (`configured` vs `review_required`, the `configured: false` warning, and the
        note that the record omits the count because `reviewDecision` doesn't carry
        it) intact — only the opening clause naming a specific number and a specific
        readability claim changes. Do not touch line 66 (the org-level rulesets
        `admin:org` claim), which is a separate, still-accurate statement about a
        different endpoint.
        done when: the paragraph no longer contains the strings "two approving
        reviews" or "unreadable without `admin:org`" in reference to the
        branch-level gate, `AGENTS.md §6` is named as the place to check the current
        review requirement, and `git diff` for this step touches only that one
        paragraph in `INTERFACE.md`.

STEP 3  Proofread the edited paragraph for sense and self-consistency            [needs 2]
        done when: the paragraph reads coherently standalone (no dangling "that ...,
        that ..." list fragments left over from the removed clauses), and a
        `grep -n "two approving\|admin:org" launchpad/scripts/INTERFACE.md` shows
        line 66's org-level claim as the only remaining hit.

STEP 4  Commit the change with DCO sign-off                                     [needs 3]
        done when: `git log -1 --format=%B` on the new commit shows a
        `docs(launchpad):` conventional title, a body explaining the fix, and a
        `Signed-off-by:` trailer (from `git commit -s`); `git status` is clean.

PARALLEL  None of these steps are meaningfully parallelizable — they are a strict
          read-edit-review-commit chain on the same single file/paragraph, so
          splitting across subagents would only add coordination overhead for a
          five-line diff.
GATES     `serina:review-code` does not apply (no executable code changes — this is a
          documentation-only edit with no runtime surface). `qa` explore mode does not
          apply for the same reason: there is no CLI, API, or UI behavior to exercise:
          the change only edits prose in a markdown file. `serina:review-final` still
          runs at the branch level per the standard `build-change` → PR handoff (and
          the repo's `pr-gate.sh` hook, which will likely fall back to a draft PR since
          this pipeline does not produce a `review-final` ledger verdict — expected and
          documented behavior, not a failure to fix).
BUDGET    Step 2 (the actual rewrite) is the only step with any judgment call in it —
          getting the replacement wording right without breaking the paragraph's
          surrounding technical claims (the `configured`/`review_required` contract)
          is the one place this could overrun a 30-minute budget.
OPEN      The issue does not state a `Size`; this plan assumed ≤30 minutes given the
          scope (one paragraph, one file, no tests to write or run). If that assumption
          is wrong, the cap should be revisited before Step 2.
LEFT OUT  - Not fixing AGENTS.md §6 itself: it already carries the correct, dated
            2026-08-28 correction and is out of this issue's scope.
          - Not re-litigating or re-verifying the org-level `admin:org` claim at line
            66 — it was independently confirmed still accurate during investigation
            (live `orgs/launchpad-26/rulesets` call 404s exactly on that scope) and is
            not part of what #1785 reports as wrong.
          - Not adding a schema/regression test for this doc paragraph — INTERFACE.md
            is prose describing a JSON contract; the existing `test_preflight_core`
            suite is unaffected by this wording change and does not need updating.
