# Issue #387 — bug: 'safe to require' check set counts eventually-green as always-green

Stated size: no Size line on the issue, treated as small (single doc section)  →  cap: 5 steps

This is a docs-only correction to one research finding's evidence section;
there is no code path or runtime surface to size against, so the plan-issue
skill's size table doesn't map cleanly. Flagged in OPEN below rather than
silently assumed.

ALREADY TRUE (verified against git and the live GitHub API, not notes)

- `launchpad/Research/358-who-can-require-a-check.md` exists at HEAD (`aef93f2c2`
  on `origin/launchpad`) and contains the "Which checks are safe to require"
  section (lines 112-146) using `select(.conclusion=="success")` as its filter.
- Reproduced the issue's own evidence: on PR #216's head commit
  `43366affaa63ddbee010c9c24b1b7a81f278a908`, `gh api .../check-runs --jq
  '[.check_runs[] | select(.conclusion=="failure") | .name] | unique'` returns
  `["check"]`.
- Fetched full check-run history (all attempts, `started_at` + `id` present) for
  both named commits (`2f5c75ea...` for PR #308, `43366aff...` for PR #216).
  Grouping by check name and taking the earliest `started_at` per name gives:
  - PR #216, name `check`: first attempt (03:31:37Z) = `failure`, second
    attempt (03:38:55Z) = `failure`, third attempt (03:59:27Z) = `success`.
  - PR #216, the other four claimed-safe names (`adr-boundary`,
    `Dead Token Reference Guard`, `Detect Changed Paths`, `scripts`): every
    attempt across every rerun is `success` — none was ever red.
  - PR #308: `check` ran twice, both `success` — no failure in its history on
    that commit.
- Each of the three `check` check-runs on `43366aff...` belongs to a distinct
  workflow run (`32095795201`, `32096230375`, `32097460933`) and check-suite,
  strictly ordered by `started_at`/`id` — i.e. genuine sequential
  reruns-on-the-same-SHA, not concurrent matrix legs with a shared name.
- **Conclusion: option (a) — re-deriving with first-attempt conclusions — is
  feasible from the exact same evidence source (the per-commit `check-runs`
  REST endpoint) the document already used**; it only needs `started_at`/`id`
  ordering plus a group-by-name-take-earliest step, not new API scope or new
  data. It is more honest than a caveat-only fix (b), and it changes the
  answer: under first-attempt semantics, the intersection of "safe" checks is
  **4**, not 5 — `check` drops out because its first attempt on PR #216 was
  `failure`. The other four names are unaffected (first attempt was
  `success` on both PRs in every case).
- Confirmed no other document in `launchpad/` reproduces or depends on the
  specific 5-name list or the "5 of 30" framing — other docs referencing #358
  (`328-ci-jobs-on-launchpad.md`, `353-full-ci-matrix-and-drop-cost.md`,
  `369-enforcing-the-upstream-boundary.md`, `354-dco-check-on-vendor-drops.md`)
  cite its permissions/protection findings only, not the check-safety list.
  The fix is scoped entirely to `358-who-can-require-a-check.md`.
- Per the issue and the task brief, out of scope: touching any actual CI
  config or required-checks/branch-protection/ruleset settings. This is a
  documentation-only fix.

STEP 1  Re-derive the safe-check evidence with first-attempt semantics  [independent]
        Re-run, against live `gh api`, the group-by-name / earliest-`started_at`
        derivation for both `2f5c75ea1ac0177b443981b95865d09c777f61de` (#308)
        and `43366affaa63ddbee010c9c24b1b7a81f278a908` (#216), and intersect
        the names whose *first-attempt* conclusion is `success` on both.
        done when: the command output on hand reproduces the ALREADY TRUE
        findings above — PR #216 first-attempt-success set excludes `check`
        (first attempt = `failure`); intersection with PR #308's
        first-attempt-success set is exactly `{adr-boundary, Dead Token
        Reference Guard, Detect Changed Paths, scripts}` (4 names).

STEP 2  Rewrite the "Which checks are safe to require" section            [needs 1]
        ← RUNS HERE
        In `launchpad/Research/358-who-can-require-a-check.md`:
        - Replace the `comm -12`/`comm -13` success-only derivation (lines
          112-146) with the first-attempt derivation: state the method
          precisely (group check-runs by name per commit, take the
          conclusion of the earliest `started_at`, intersect where both
          PRs' first attempt was `success`), and show the corrected
          commands/output.
        - State the corrected result plainly, not as an added caveat: **4**
          checks are safe to require under first-attempt semantics —
          `adr-boundary`, `Dead Token Reference Guard`, `Detect Changed
          Paths`, `scripts` — and `check` is demoted, named explicitly with
          why: it ran red on its first attempt on PR #216
          (`43366aff...`, 03:31:37Z and 03:38:55Z both `failure`) and only
          went green on a third, later attempt (03:59:27Z). Distinguish this
          precisely from "never ran red at all" — `check` did run red once
          on a first attempt that we know of; the other four never did, on
          either commit, across any rerun.
        - Update every place in the document that states or depends on "5 of
          30" / lists all five names as the safe set: the Summary line
          (line 4), the Finding section's five-name block and its
          surrounding prose (lines 30-40), and the "What this means for
          #273" section (lines 150-161, e.g. "Require only the five
          always-running checks").
        - Do not alter the "30" denominator, the permissions findings, the
          ruleset findings, or the "Confidence and limits" section's
          existing caveat about comparing only two PRs — that caveat is
          about path-filtering breadth, not reruns, and stays as-is per the
          issue.
        - Add one precise line to "Confidence and limits" naming the new,
          narrower thing checked: first-attempt conclusions were verified
          only on these same two commits (not across all 216 PRs), so a
          check that is currently "always green from a first attempt" could
          still be flaky on a PR shape not sampled here.
        done when: the document contains no unqualified "5" count or
        unqualified five-name list; `check` is described as demoted with its
        two-failure/one-eventual-success first-attempt history stated
        inline; the four remaining names are stated as the corrected safe
        set; a `grep -n "check$\|five\|5 of 30" launchpad/Research/358-who-can-require-a-check.md`
        pass confirms no stale unqualified claim remains.

STEP 3  Proofread and verify against the live commands                    [needs 2]
        Re-run every `gh api` command now embedded in the rewritten section
        against the live repo and confirm the pasted output byte-matches
        (modulo formatting) what actually comes back — the doc is evidence,
        so a transcription slip here is the same class of bug as the one
        being fixed.
        done when: every command block in the rewritten section, run
        verbatim, reproduces the output shown in the document.

PARALLEL  Step 1 could run standalone (pure evidence-gathering, already
          largely done above). Steps 2 and 3 are sequential on the same file
          and on Step 1's derived facts. No step here benefits from a
          subagent fan-out — it is one file, one linear edit, verified
          against one shared command set.
GATES     No `review-code`, `review-tests`, or `review-a11y` — no code or UI
          changed. `qa` explore mode does not apply — no runtime interface,
          config, or CI behaviour changes; the fix is prose plus embedded
          command transcripts. The repo's standard PR-time gates
          (`pr-gate.sh`, DCO check) still apply at push/PR time per
          `AGENTS.md`, not as a build-time review gate for this plan.
BUDGET    Step 2 is where the budget goes — it is the one step doing
          judgment work (deciding exactly how to phrase "demoted" vs. the
          existing "sound lower bound" caveat so the two are clearly
          distinguished, per the issue's explicit instruction not to conflate
          "never ran red then rerun" with "never ran red at all").
OPEN      The issue has no `Size` line; this plan assumed "small, single-doc
          fix" rather than asking, since the issue itself is unambiguous
          about scope (one section of one file) and the task brief that
          spawned this plan already fixed the two options and the
          feasibility question. Flagged rather than silently resolved.
LEFT OUT  No change to any CI workflow, branch protection, or ruleset
          config — out of scope per the issue and per #153/#146, which own
          that decision. No change to the "30" denominator or the admin/
          permissions findings, which the issue states are independently
          correct. No re-sampling beyond the two named commits (#308, #216)
          — the issue's own reproduction is scoped to exactly those two, and
          widening the sample is a different, larger piece of work than this
          bug fix.
