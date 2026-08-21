# Who can make a status check required, and are rulesets available

**Title:** Whether requiring a CI check on `launchpad` needs an org admin, and which checks are safe to require
**Summary:** Overturns a premise carried by four open decisions. **@tucktuck101 already holds repository admin**, so no org admin is needed — there are four repo admins and both mechanisms are available: branch protection (admin-only, live now) and repository rulesets (endpoint returns HTTP 200, org is on an enterprise plan). Separately establishes that only **5 of the 30** checks are safe to require today, because `ci.yml` is path-filtered and a required check that skips leaves a pull request permanently pending.
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

**But there is a real obstacle nobody has named, and it is not permissions.** `ci.yml` gates its jobs on a changed-paths filter. A required check that does not run leaves a pull request pending forever, so **only 5 of the 30 checks can be required as things stand**:

```
adr-boundary
check
Dead Token Reference Guard
Detect Changed Paths
scripts
```

Those five ran and passed on both a two-file documentation PR (#308) and a 981-file upstream sync (#216). Every interesting check — `Unit Tests`, `Rust Lint`, `Desktop Core`, `Mobile`, `Relay E2E` — skipped on the documentation PR. Requiring any of them today would deadlock every documentation PR in the repository.

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

Compared the successful checks on a documentation-only PR against a 981-file upstream sync, via REST:

```
$ for pr in 308 216; do
    sha=$(gh api repos/launchpad-26/buzz/pulls/$pr --jq .head.sha)
    gh api "repos/launchpad-26/buzz/commits/$sha/check-runs?per_page=100" --paginate \
      --jq '.check_runs[] | select(.conclusion=="success") | .name' | sort -u > /tmp/rck$pr.txt
  done
PR 308 head=2f5c75ea1ac0177b443981b95865d09c777f61de success-checks=6
PR 216 head=43366affaa63ddbee010c9c24b1b7a81f278a908 success-checks=30

$ comm -12 /tmp/rck308.txt /tmp/rck216.txt
adr-boundary
check
Dead Token Reference Guard
Detect Changed Paths
scripts

$ comm -13 /tmp/rck308.txt /tmp/rck216.txt
Backend Integration (relay e2e)      Desktop Smoke E2E (1)…(4)
Build (linux/amd64)                  lint + unittest + render matrix
Build (linux/arm64)                  Mobile
Desktop                              Relay E2E
Desktop Build (macOS)                Relay-Driven Mesh Lifecycle Smoke
Desktop Core                         Rust Lint
Desktop E2E Integration              Security
Desktop E2E Integration (1/2),(2/2)  Server Cross-Compile (×2)
Desktop E2E Relay                    Unit Tests
                                     Web
                                     Windows Rust (x86_64-pc-windows-msvc)
```

Note that even the aggregator jobs — `Desktop`, `Desktop E2E Integration` — are themselves path-filtered and skipped on the documentation PR, so they are not usable as always-running gates in their current form.

---

## What this means for #273

**Success criterion 6 is reachable without asking anyone for anything.** It has been treated across three sweeps as blocked on privilege. It is not. What it is blocked on is a change to `ci.yml` — an upstream-owned file — or a new always-running aggregator job in a `launchpad-*.yml` workflow that reports the CI outcome and can safely be required.

**That reframes #154 from a privilege request into a design question.** Two shapes, offered as input rather than as a recommendation:

- **Require only the five always-running checks.** Costs nothing, available today, and gives almost no assurance about a drop — none of the five compiles anything.
- **Add a `launchpad-ci-gate` job** that depends on the `ci.yml` jobs and succeeds when each either passed or was legitimately skipped, then require that one check. This is the standard answer to the path-filter/required-check conflict. It needs a new `launchpad-*.yml` workflow, which §3 of `launchpad/AGENTS.md` explicitly permits, and it touches no upstream file.

**It also changes #299's shape.** #299 asks what identity opens the drop PR, partly because a `GITHUB_TOKEN`-authored PR fires no `pull_request` workflows. Combined with #353's finding that a human-opened sync PR already gets the full green matrix, and this finding that a check can be required today, the human-opened path now dominates on every axis: it runs CI, it can be gated, and it needs no privilege grant.

**And it removes the stated reason for reading two decisions first.** An earlier sweep advised settling #298 and #299 first "because admin latency is the long pole". There is no admin latency. The reading order should be reconsidered on merit.

---

## Confidence and limits

**High confidence** on permissions, ruleset availability, current protection state, and the five-safe-checks result — all pasted REST output.

**One belief, explicitly not tested: that `enforce_admins: false` lets the four repo admins push to `main` despite `restrictions.users`.** This is GitHub's documented behaviour for that setting, and it would materially shrink #298. I did not test it, because the only test is pushing to `main`, which is not mine to do. Someone with admin can confirm it in one attempt on a throwaway branch pattern, or by reading the branch's settings page.

**Not checked.** I could not enumerate org-level rulesets or org-level branch-protection policy — `admin:org` scope missing, 404 pasted above — so an org policy could in principle constrain what a repo admin may configure; the repo-level `200` shows the feature is reachable, not that no org rule overrides it. I did not create a ruleset or modify any protection, so "a repo admin can create one" rests on GitHub's permission model rather than on an observed success. I compared two pull requests, not all 216, so the five-check intersection is a sound lower bound on "always runs" rather than a proven invariant — a third PR shape (workflow-only, or mobile-only) could shrink it. I did not check whether `audit` — which passed on #308 but not on #216 — is conditionally triggered or simply absent from that older run. I did not determine why `aespaldi` is missing from `launchpad`'s push-restriction list.
