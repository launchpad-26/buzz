# Who can make a status check required, and are rulesets available

**Title:** Whether requiring a CI check on `launchpad` needs an org admin, and which checks are safe to require
**Summary:** Overturns a premise carried by four open decisions. **@tucktuck101 already holds repository admin**, so no org admin is needed — there are four repo admins and both mechanisms are available: branch protection (admin-only, live now) and repository rulesets (endpoint returns HTTP 200, org is on an enterprise plan). Separately establishes that only **4 of the 30** checks are safe to require today, because `ci.yml` is path-filtered and a required check that skips leaves a pull request permanently pending. (Originally measured as 5; corrected 2026-09-04 — see [#387](https://github.com/launchpad-26/buzz/issues/387).)
**Tags:** `ci` `branch-protection` `rulesets` `permissions` `prd-273` `adr-0022`
**Established:** 2026-08-22 · **Answers:** [#358](https://github.com/launchpad-26/buzz/issues/358) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**Nobody needs to be asked. The person who owns this work can require a check today.**

```
$ gh api repos/launchpad-26/buzz --jq '.permissions'
{"admin":true,"maintain":true,"pull":true,"push":true,"triage":true}
```

Four repository admins: **joshuavial, baradev, tucktuck101, jatin-puri-coder**. Eight further collaborators hold `maintain`, which is *not* enough — branch protection and rulesets are admin-only.

Both mechanisms are available:

| Mechanism | Available? | Who |
|---|---|---|
| Branch protection required status checks | Yes — protection already configured on `launchpad`, `required_status_checks: null` | Repository admin |
| Repository rulesets | Yes — `GET /rulesets` returns `HTTP 200` and `[]`; public repo, org on `enterprise` plan | Repository admin |

**The "needs an org admin, and admin latency is the long pole" framing in #154, #298, #299 and #301 is wrong.** It was assumed and never checked. Three sweeps on #273 repeated it.

**But there is a real obstacle nobody has named, and it is not permissions.** `ci.yml` gates its jobs on a changed-paths filter. A required check that does not run leaves a pull request pending forever, so **only 4 of the 30 checks can be required as things stand**:

```
adr-boundary
Dead Token Reference Guard
Detect Changed Paths
scripts
```

Those four ran green **on their first attempt** on both a two-file documentation PR (#308) and a 981-file upstream sync (#216) — no failure appears anywhere in their check-run history on either commit, across any rerun. Every interesting check — `Unit Tests`, `Rust Lint`, `Desktop Core`, `Mobile`, `Relay E2E` — skipped on the documentation PR. Requiring any of them today would deadlock every documentation PR in the repository.

**A fifth name, `check`, was originally counted here and is demoted.** It reported `success` on both PRs, but only after reruns: on PR #216's commit it failed on its first attempt (03:31:37Z) and again on a second attempt (03:38:55Z), and did not go green until a third attempt (03:59:27Z). The original derivation filtered on "did this name ever conclude `success`?", which absorbs that history and reads as "always green." It is not — it is *eventually* green, which is a different guarantee: a required check that goes red on its first run still blocks a merge until someone notices and reruns it. See "Which checks are safe to require" below for the corrected method and the distinction it draws.

---

## Evidence

### Permissions

```
$ gh api "repos/launchpad-26/buzz/collaborators?per_page=100" \
    --jq '.[] | "\(.login)  \(.role_name)  admin=\(.permissions.admin)"'
joshuavial          admin     admin=true
aespaldi            write     admin=false
gabriel-canaan      maintain  admin=false
baradev             admin     admin=true
benmitchell11       maintain  admin=false
tucktuck101         admin     admin=true
jatin-puri-coder    admin     admin=true
KelliherL           maintain  admin=false
hchristinasmith     maintain  admin=false
serina-mcfall       maintain  admin=false
ciaran-slow         maintain  admin=false
Specter-ui          maintain  admin=false
```

### Rulesets are available and unused

```
$ gh api repos/launchpad-26/buzz/rulesets -i | head -1
HTTP/2.0 200 OK
$ gh api repos/launchpad-26/buzz/rulesets --jq '.'
[]

$ gh api orgs/launchpad-26 --jq '{login,plan:.plan.name}'
{"login":"launchpad-26","plan":"enterprise"}
```

A `200` with an empty array is the feature responding, not refusing. The org-level ruleset endpoint returns 404 for this token, but that is a **scope** limitation rather than a feature one:

```
$ gh api orgs/launchpad-26/rulesets -i | head -1
HTTP/2.0 404 Not Found
gh: This API operation needs the "admin:org" scope.
```

### Current protection on both branches

```
$ gh api repos/launchpad-26/buzz/branches/launchpad/protection --jq '{...}'
{"approvals":1,
 "checks":null,
 "codeowners":false,
 "conversation":true,
 "dismiss":true,
 "enforce_admins":false,
 "linear":false,
 "restrictions":{"apps":[],"users":["joshuavial","gabriel-canaan","baradev","benmitchell11",
   "tucktuck101","jatin-puri-coder","KelliherL","hchristinasmith","serina-mcfall",
   "ciaran-slow","Specter-ui"]}}

$ gh api repos/launchpad-26/buzz/branches/main/protection --jq '{...}'
{"approvals":null,"checks":null,"del":false,"enforce_admins":false,"force":false,
 "fork_sync":false,
 "restrictions":{"users":["joshuavial"],"apps":[],"teams":[]}}
```

Three things worth pulling out:

- `checks: null` on both. No status check is required anywhere in this repository.
- **`enforce_admins: false` on both.** GitHub's documented meaning is that administrators are exempt from the configured restrictions. If that holds here, the four repo admins can already push to `main` despite `restrictions.users` naming only `joshuavial` — which would substantially collapse [#298](https://github.com/launchpad-26/buzz/issues/298). **I have not tested this and will not**, because the test is pushing to `main`. Flagged as belief, not fact.
- `launchpad`'s push restriction lists 11 of the 12 collaborators — `aespaldi` (write) is absent. Probably an oversight; noted rather than diagnosed.

### Which checks are safe to require

**Corrected 2026-09-04 ([#387](https://github.com/launchpad-26/buzz/issues/387)).** The method originally used here — `select(.conclusion=="success")` over each commit's full check-run history — counts a check as "safe" if that name *ever* concluded `success`, anywhere in its rerun history. That silently absorbs reruns: a check can fail on its first attempt, get manually rerun, and still pass the filter because a later attempt succeeded. That is "eventually green," not "always green," and the two carry different consequences once a check is actually required — an eventually-green check still blocks a merge on its first, red run until someone notices and reruns it.

The fix is to take, per check name per commit, the **first attempt only** (earliest `started_at` in the check-run history — GitHub gives every check run its own `id`/`started_at`, and reruns land as later entries with the same `name` on the same commit, so ordering by either recovers attempt order), then intersect the names whose first-attempt conclusion was `success` on both PRs:

```
$ for pr in 308 216; do
    sha=$(gh api repos/launchpad-26/buzz/pulls/$pr --jq .head.sha)
    gh api "repos/launchpad-26/buzz/commits/$sha/check-runs?per_page=100" --paginate \
      --jq '.check_runs[] | {name, id, started_at, conclusion}' > /tmp/rck$pr.jsonl
  done
PR 308 head=2f5c75ea1ac0177b443981b95865d09c777f61de
PR 216 head=43366affaa63ddbee010c9c24b1b7a81f278a908

$ for pr in 308 216; do
    jq -sr 'group_by(.name)
      | map({name: .[0].name, first: (sort_by(.started_at) | .[0])})
      | .[] | select(.first.conclusion=="success") | .name' /tmp/rck$pr.jsonl \
      | sort > /tmp/first$pr.txt
  done

$ comm -12 /tmp/first308.txt /tmp/first216.txt
Dead Token Reference Guard
Detect Changed Paths
adr-boundary
scripts
```

`check` is absent from this intersection. Its first-attempt history on PR #216's commit (`43366aff...`) is:

```
$ gh api repos/launchpad-26/buzz/commits/43366affaa63ddbee010c9c24b1b7a81f278a908/check-runs --paginate \
    --jq '.check_runs[] | select(.name=="check") | {id, conclusion, started_at}' | jq -s 'sort_by(.started_at)'
[
  {"id": 95586784357, "conclusion": "failure", "started_at": "2026-08-18T03:31:37Z"},
  {"id": 95588021110, "conclusion": "failure", "started_at": "2026-08-18T03:38:55Z"},
  {"id": 95591477097, "conclusion": "success", "started_at": "2026-08-18T03:59:27Z"}
]
```

Two failures, each from a distinct workflow run (`32095795201`, `32096230375`) on the same commit, before a third run went green. On PR #308's commit, `check` ran twice and both attempts succeeded — no failure anywhere in its history there. So `check` is not "always red" or generally flaky; it is specifically **not proven to run green on a first attempt**, which is the exact property "safe to require" needs. The other four names carry no failure in their history on either commit, across any rerun — their first attempt was `success` every time observed.

**Three different properties are in play here, and it matters which one "safe" means:**

1. *Ever succeeded, on both PRs* (the original filter) — `adr-boundary`, `check`, `Dead Token Reference Guard`, `Detect Changed Paths`, `scripts` (5 names). This is the weakest claim: it says nothing about how many attempts it took.
2. *Never ran red on a first attempt, on either PR* (the corrected filter above) — `adr-boundary`, `Dead Token Reference Guard`, `Detect Changed Paths`, `scripts` (4 names).
3. *Never ran red on any attempt at all, on either PR* — checking every conclusion in the raw check-run data (not just first attempts) for a `failure` anywhere: the only name with a `failure` conclusion anywhere in its history, on either commit, is `check` (two failures on PR #216, none on PR #308). So this strictest property also yields the same 4 names as (2), on this evidence.

Properties (2) and (3) happen to coincide here only because every observed failure on these two commits was also a first attempt — there is no case in this data of a check succeeding first and failing on a later, gratuitous rerun. They are not the same property in general: a check that passed on attempt 1 and then failed on a manually-triggered attempt 2 would satisfy (2) but not (3). `check` is excluded from both here because its failures on PR #216 (03:31:37Z and 03:38:55Z) were its first two attempts, before a third attempt (03:59:27Z) went green — it fails the weaker property (2) already, so the stricter property (3) does not need to do any further work to exclude it in this instance.

Note that even the aggregator jobs — `Desktop`, `Desktop E2E Integration` — are themselves path-filtered and skipped on the documentation PR, so they are not usable as always-running gates in their current form.

---

## What this means for #273

**Success criterion 6 is reachable without asking anyone for anything.** It has been treated across three sweeps as blocked on privilege. It is not. What it is blocked on is a change to `ci.yml` — an upstream-owned file — or a new always-running aggregator job in a `launchpad-*.yml` workflow that reports the CI outcome and can safely be required.

**That reframes #154 from a privilege request into a design question.** Two shapes, offered as input rather than as a recommendation:

- **Require only the four always-running checks.** Costs nothing, available today, and gives almost no assurance about a drop — none of the four compiles anything.
- **Add a `launchpad-ci-gate` job** that depends on the `ci.yml` jobs and succeeds when each either passed or was legitimately skipped, then require that one check. This is the standard answer to the path-filter/required-check conflict. It needs a new `launchpad-*.yml` workflow, which §3 of `launchpad/AGENTS.md` explicitly permits, and it touches no upstream file.

**It also changes #299's shape.** #299 asks what identity opens the drop PR, partly because a `GITHUB_TOKEN`-authored PR fires no `pull_request` workflows. Combined with #353's finding that a human-opened sync PR already gets the full green matrix, and this finding that a check can be required today, the human-opened path now dominates on every axis: it runs CI, it can be gated, and it needs no privilege grant.

**And it removes the stated reason for reading two decisions first.** An earlier sweep advised settling #298 and #299 first "because admin latency is the long pole". There is no admin latency. The reading order should be reconsidered on merit.

---

## Confidence and limits

**High confidence** on permissions, ruleset availability, current protection state, and the four-safe-checks result — all pasted REST output.

**One belief, explicitly not tested: that `enforce_admins: false` lets the four repo admins push to `main` despite `restrictions.users`.** This is GitHub's documented behaviour for that setting, and it would materially shrink #298. I did not test it, because the only test is pushing to `main`, which is not mine to do. Someone with admin can confirm it in one attempt on a throwaway branch pattern, or by reading the branch's settings page.

**Not checked.** I could not enumerate org-level rulesets or org-level branch-protection policy — `admin:org` scope missing, 404 pasted above — so an org policy could in principle constrain what a repo admin may configure; the repo-level `200` shows the feature is reachable, not that no org rule overrides it. I did not create a ruleset or modify any protection, so "a repo admin can create one" rests on GitHub's permission model rather than on an observed success. I compared two pull requests, not all 216, so the four-check intersection is a sound lower bound on "always runs green on a first attempt" rather than a proven invariant — a third PR shape (workflow-only, or mobile-only) could shrink it, and a check with no observed failure here could still be flaky on a shape not sampled. I did not check whether `audit` — which passed on #308 but not on #216 — is conditionally triggered or simply absent from that older run. I did not determine why `aespaldi` is missing from `launchpad`'s push-restriction list.

**A separate, narrower caveat, added 2026-09-04 ([#387](https://github.com/launchpad-26/buzz/issues/387)):** the "sound lower bound" caveat above is about *breadth* — comparing only two PR shapes out of 216. It does not cover *flakiness/reruns* — a check's history on a given commit can contain a first-attempt failure that a later, manual rerun overwrote with success, which the original `select(.conclusion=="success")` filter could not see. What is established for the four remaining names is "never ran red, on any attempt, on either of these two commits" (property 3 in "Which checks are safe to require" above) — stronger than "never ran red on a first attempt" turned out to require on this evidence, but only because no check here happened to pass first and fail on a later rerun; a future re-run of this method on different commits could see that case, and the two properties would then diverge. Neither property has been checked beyond these two commits, so "safe" still means "safe on this evidence," not "flake-proof everywhere."
