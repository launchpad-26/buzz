---
id: verification-ci-required-checks
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "launchpad-26/buzz's default branch is `launchpad`, and it has no classic GitHub branch-protection rule configured: the branch-protection REST endpoint returns HTTP 404 for it."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz') -> default_branch: launchpad"
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found (Branch not protected)"
  - statement: "launchpad-26/buzz carries zero repository-level rulesets."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> []"
  - statement: "No active rule -- at repository or organization level -- currently applies to the `launchpad` branch. GitHub's own REST reference for this endpoint states it returns 'all active rules that apply ... regardless of the level at which they are configured (e.g. repository or organization)', so an empty result here is not merely 'no repository ruleset', it is 'nothing GitHub currently enforces on this branch, from any level of configuration'."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/rules/branches/launchpad') -> []"
      - "https://docs.github.com/en/rest/repos/rules?apiVersion=2022-11-28#get-rules-for-a-branch"
  - statement: "launchpad-26/buzz has no merge queue configured for the `launchpad` branch, so a merge-queue-level required-check gate is not a hidden alternate enforcement path either."
    entry_class: FACT
    evidence:
      - "gh_api_graphql('repository(owner: \"launchpad-26\", name: \"buzz\") { mergeQueue(branch: \"launchpad\") { id } }') -> mergeQueue: null"
  - statement: "The current caller's token lacks the `admin:org` scope needed to list organization-level rulesets directly via `GET /orgs/launchpad-26/rulesets`, so that specific listing could not be independently cross-checked; the per-branch 'rules for a branch' query above is relied on instead, per its own documented scope of covering org-level rules too."
    entry_class: FACT
    evidence:
      - "gh_api('orgs/launchpad-26/rulesets') -> 404 Not Found, message: 'This API operation needs the \"admin:org\" scope.'"
  - statement: "ADR-0020 (accepted 2026-08-21) independently recorded the same absence of enforcement under the same mechanism, in its own words: '`required_status_checks` on `launchpad` returns 404 -- not configured.'"
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0052 (accepted 2026-08-28, supersedes ADR-0019, decided in launchpad-26/buzz#1765) independently re-measured the same fact eight days later and reached the same number: 'required_approving_review_count is 1, required_status_checks is empty, and enforce_admins is false on both trunks,' and explicitly retains ADR-0019's ruling that 'Enforcement of required checks stays deferred until the CI/CD pipeline programme (launchpad-26/buzz-infrastructure#105) is live,' with a stated revisit date of 2026-09-05 if #105 has not landed by then."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "The absence of a required check is not merely theoretical: pull requests carrying FAILURE conclusions on their `check` and/or `audit` status checks have been merged into `launchpad`. Two concrete examples, sampled from the ten most recently merged PRs: #1997 merged 2026-08-31T22:00:25Z with two FAILURE `check` conclusions in its final status-check rollup; #1989 merged 2026-08-31T19:57:05Z with four FAILURE `check` conclusions and one FAILURE `audit` conclusion in its final status-check rollup."
    entry_class: FACT
    evidence:
      - "gh_pr_view(1997, repo='launchpad-26/buzz') -> baseRefName: launchpad, mergedAt: 2026-08-31T22:00:25Z, statusCheckRollup contains 2 entries {name: check, conclusion: FAILURE}"
      - "gh_pr_view(1989, repo='launchpad-26/buzz') -> baseRefName: launchpad, mergedAt: 2026-08-31T19:57:05Z, statusCheckRollup contains 4 entries {name: check, conclusion: FAILURE} and 1 entry {name: audit, conclusion: FAILURE}"
  - statement: "Of the ten most recently merged pull requests sampled against launchpad-26/buzz at the recorded revision (#1997, #1994, #1992, #1991, #1989, #1987, #1986, #1984, #1982, #1978), nine carried at least one FAILURE status-check conclusion in their final rollup and all ten merged into `launchpad` regardless."
    entry_class: FACT
    evidence:
      - "gh_pr_list(state='merged', limit=10, repo='launchpad-26/buzz') -> 9 of 10 sampled PRs (#1997,#1994,#1992,#1991,#1989,#1987,#1986,#1982,#1978) show at least one FAILURE conclusion in statusCheckRollup; all baseRefName=launchpad"
  - statement: "Every check that runs on a pull request against launchpad-26/buzz is posted by a workflow triggered on the `pull_request` event -- for example `rust-lint` and `unit-tests` in `ci.yml`, `check` in `launchpad-pr-check.yml`, `audit` in `launchpad-security-audit.yml`, `adr-boundary` in `launchpad-adr-check.yml`, and `validate` in `launchpad-corpus-validate.yml` -- and none of them is marked as a required status check by any branch-protection rule or ruleset at the recorded revision, per the findings above."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - ".github/workflows/launchpad-pr-check.yml"
      - ".github/workflows/launchpad-security-audit.yml"
      - ".github/workflows/launchpad-adr-check.yml"
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "This repository's own root `CLAUDE.md` states: 'Commit with `git commit -s`. The required DCO Check fails any PR with a commit missing a `Signed-off-by` trailer.' That sentence sits above the file's own banner, 'Everything above this line is upstream's contributor guide,' so the file itself presents that DCO-check claim as upstream `block/buzz`'s stated contributor practice, not as a description of this fork's own verified branch-protection configuration."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "No status check whose name contains the substring 'DCO' appears among the 39 distinct status-check names observed across the 30 most recently created pull requests sampled against launchpad-26/buzz (mixed open/closed/merged state) at the recorded revision."
    entry_class: FACT
    evidence:
      - "gh_pr_list(state='all', limit=30, repo='launchpad-26/buzz') -> 39 distinct statusCheckRollup names observed, none containing 'DCO'"
  - statement: "Taken together -- no branch protection, no repository or organization ruleset, no merge queue, and no observed DCO-named check on any sampled pull request -- CLAUDE.md's 'required DCO Check' does not currently describe an enforced, merge-blocking gate on launchpad-26/buzz's `launchpad` branch; nothing in this fork's own configuration is currently in a position to fail a PR over a missing `Signed-off-by` trailer at the recorded revision, whatever DCO enforcement upstream `block/buzz` itself may or may not have."
    entry_class: INFERENCE
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404"
      - "gh_api('repos/launchpad-26/buzz/rules/branches/launchpad') -> []"
      - "gh_pr_list(state='all', limit=30, repo='launchpad-26/buzz') -> no 'DCO' check name observed"
      - "CLAUDE.md"
    confidence: 0.8
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: corpus-standard-test-references
---

# Required checks for merging into `launchpad` -- test contract

## Purpose and boundary

This node documents exactly one obligation: **which GitHub-enforced checks, if any, are
actually required in order to merge a pull request into launchpad-26/buzz's default
branch, `launchpad`** -- as distinct from which checks merely *run* on a pull request
and post a result. It covers that question only. It does not evaluate whether any
individual CI job's own logic is correct, whether the cohort *should* add required
checks (a policy question ADR-0019/ADR-0052 already own), or upstream `block/buzz`'s own
branch-protection configuration on a different repository.

## Obligation

> As of the recorded revision, **zero** GitHub-enforced checks are required in order to
> merge a pull request into launchpad-26/buzz's default branch (`launchpad`): every
> check that runs on a pull request there -- lint, tests, corpus validation, security
> audit, ADR-boundary check, or any other -- is informational only, and a pull request
> carrying one or more FAILURE conclusions can still be merged.

This is deliberately a negative obligation. The question this node exists to answer is
"which checks actually gate a merge," and the honest, verified answer at this revision
is "none of them" -- stating that plainly is the obligation, not a workaround for one.

## Verifying command(s)

This obligation describes GitHub platform *configuration*, not application behavior, so
there is no repository-committed test file that exercises it the way a Rust or
Playwright test exercises code. The verifying procedure is a reproducible sequence of
`gh` commands run directly against the live repository and its pull-request history:

```bash
# 1. Confirm the default branch and that no classic branch-protection rule exists.
gh api repos/launchpad-26/buzz --jq .default_branch
gh api repos/launchpad-26/buzz/branches/launchpad/protection   # expect: 404 Not Found

# 2. Confirm no repository-level ruleset exists.
gh api repos/launchpad-26/buzz/rulesets --jq .                 # expect: []

# 3. Confirm no rule -- repository or organization level -- currently applies to the
#    branch. Per GitHub's own docs this endpoint covers both levels.
gh api repos/launchpad-26/buzz/rules/branches/launchpad --jq . # expect: []

# 4. Confirm no merge queue is configured for the branch.
gh api graphql -f query='query {
  repository(owner: "launchpad-26", name: "buzz") {
    mergeQueue(branch: "launchpad") { id }
  }
}'                                                              # expect: mergeQueue: null

# 5. Empirically confirm PRs with failing checks have actually merged.
gh pr list --repo launchpad-26/buzz --state merged --limit 10 \
  --json number,baseRefName,statusCheckRollup \
  --jq '.[] | select(.baseRefName=="launchpad") |
        select([.statusCheckRollup[]?.conclusion] | any(. == "FAILURE")) |
        {number, failing: [.statusCheckRollup[] | select(.conclusion=="FAILURE") | .name]}'
```

Step 1's 404, steps 2-4's empty/null results, and step 5 returning at least one merged
PR with a FAILURE conclusion are jointly what "verified" means below. Any one of them
coming back non-empty (a real ruleset, a real branch-protection object, a real merge
queue) would falsify the obligation as stated and this node would need to move to
`status: flagged` or be rewritten, not quietly reworded.

## Current enforcement status

**Verified**, as of commit `473205a7457b208455f188847bfb27b01aa83cac` (checked
2026-09-01). All five checks in the command sequence above were run directly against
`launchpad-26/buzz` and returned the results the obligation predicts, and the finding
is independently corroborated by two accepted decision records that measured the same
GitHub configuration on different dates: ADR-0020 (2026-08-21: "`required_status_checks`
on `launchpad` returns 404 -- not configured") and ADR-0052 (2026-08-28:
"`required_status_checks` is empty ... on both trunks"). This is a **deliberate,
decided-on deferral**, not an oversight discovered here for the first time --
ADR-0019/ADR-0052 defer enforcement until `launchpad-26/buzz-infrastructure`#105 (the
CI/CD pipeline programme) lands, with a stated revisit date of 2026-09-05.

Because this obligation is about live platform configuration rather than code frozen at
a commit, "verified" here has a shorter shelf life than a code-behavior FACT: a
repository administrator could add branch protection, a ruleset, or a merge queue at any
time without any commit to this repository at all, and this node's `status: draft` would
then be stating something no longer true until re-checked. See Limits.

## Limits

- **This node proves absence of enforcement at one point in time, not a permanent
  property.** Branch protection, rulesets and merge queues are repository settings, not
  files under version control here; they can change without a corresponding commit, so
  a reader relying on this node after 2026-09-01 (or after `launchpad-26/buzz-infrastructure`#105
  lands, per ADR-0052's own revisit trigger) should re-run the command sequence above
  rather than trust this node's `status: draft` snapshot indefinitely.
- **The organization-level ruleset listing (`GET /orgs/launchpad-26/rulesets`) could not
  be queried directly**, because the authenticated token lacks the `admin:org` scope.
  The per-branch "rules for a branch" query (step 3) is relied on instead; GitHub's own
  documentation states it surfaces rules from both levels, but that specific claim was
  checked against GitHub's docs, not against a live org-level ruleset in this
  organization, because none exists here to test it against.
- **The PR samples are samples, not a full history.** The "merged despite FAILURE"
  finding used the 10 most recently merged PRs; the "no DCO-named check observed"
  finding used the 30 most recently created PRs in any state. Neither claim is a
  statement about every PR ever opened against this repository.
- **Local pre-commit/pre-push hooks (lefthook) are a different gate from the one this
  node covers.** Root `AGENTS.md` documents pre-push hooks that run clippy, typechecking
  and fast unit tests before a `git push` succeeds from a contributor's own machine --
  that is a client-side gate a contributor can choose to bypass (`--no-verify`,
  a fresh clone without hooks installed, or a push from a CI identity that never ran
  `just setup`). This node covers only GitHub's own server-side merge gate; it says
  nothing about whether any given contributor's local hooks actually ran.
- **Upstream `block/buzz`'s own branch-protection/ruleset configuration was not
  queried.** It is a different repository from `launchpad-26/buzz`, and CLAUDE.md's DCO
  paragraph may accurately describe upstream's own enforcement; this node makes no claim
  about that repository either way.
- **Whether any of the four repository admins (`joshuavial`, `baradev`, `tucktuck101`,
  `jatin-puri-coder`, per ADR-0019) would in practice choose to add required checks
  before `#105` lands is a decision this node does not track**; ADR-0052 is the
  authoritative record of that decision and this node only cites its measurement, not
  its rationale in full.

## Scope and omissions

**Covered:** whether a merge-blocking, GitHub-enforced required status check currently
exists for launchpad-26/buzz's `launchpad` branch, checked against classic branch
protection, repository rulesets, organization-level rules (as surfaced through the
per-branch rules endpoint), and merge queue configuration; empirical confirmation via
actual merge history; and the specific discrepancy between root `CLAUDE.md`'s DCO-check
claim and this fork's own observed configuration.

**Not covered here, named as gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whether required checks *should* be added, and what may gate a merge in principle | ADR-0019, ADR-0052 |
| The CI/CD pipeline programme that will eventually add enforcement | `launchpad-26/buzz-infrastructure`#105 |
| The correctness of any individual CI job's own logic (lint rules, test assertions, corpus validator's own checks) | Each job's own workflow file / owning subsystem |
| Local pre-commit/pre-push hook behavior on a contributor's machine | Root `AGENTS.md` "Quality Gates" section |
| Upstream `block/buzz`'s own branch-protection/ruleset configuration | Not tracked by this fork's corpus |
| General evidence-classification rules and the tool-result/graph-edge citation shapes in the abstract | `launchpad/docs/corpus/standards/evidence.md`, `standards/test-references.md` |

**Expected but not verified when this node was written:**

- **Whether `#105` (the CI/CD pipeline programme) has already landed on
  `launchpad-26/buzz-infrastructure`** was not checked -- that is a different
  repository, and this node's obligation is about `launchpad-26/buzz`'s current
  configuration regardless of that programme's status. ADR-0052's 2026-09-05 revisit
  date is the trigger a reader should check against.
- **Whether any GitHub App (beyond a possible DCO app) posts a status/check-run this
  node's PR samples did not happen to surface** was not exhaustively ruled out; the
  39-name sample is what two PR-history queries returned, not a claim that no other
  check name has ever appeared.
