# What actually permits a fast-forward of `launchpad-26/main`

**Title:** Which mechanism lets the vendor branch be advanced, given `main`'s push restriction
**Summary:** `main` has `enforce_admins: false`, and GitHub documents that "people and apps with admin permissions to a repository are always able to push to a protected branch". So the **four repository admins can already advance `main` today** — the `restrictions.users: ["joshuavial"]` list does not bind them. Separately identifies the genuinely minimal grant, which nobody has considered: `allow_fork_syncing`, a per-branch protection setting whose documented purpose is to "pull changes from the upstream repository while preventing other contributions to the fork's branch" — precisely the vendor-branch case. It is currently `false`.
**Tags:** `vendor-branch` `branch-protection` `fork-syncing` `permissions` `prd-273`
**Established:** 2026-08-22 · **Answers:** [#359](https://github.com/launchpad-26/buzz/issues/359) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**Three mechanisms could advance `main`. Two of them already work or are one toggle away, and the one #298 is built around is the widest of the three.**

| Mechanism | State today | What it grants |
|---|---|---|
| **Admin bypass** | **Already available** — `enforce_admins: false`, four repo admins | Everything. Admins bypass all branch protection on `main`. |
| **`allow_fork_syncing`** | `false` — one protection toggle | *Only* pulling from upstream. Documented as preventing other contributions. |
| Adding actors to `restrictions` | The assumption in #298 | Unrestricted push to `main` for whoever is added |

**The live defect in #305 — `main` pinned eleven days behind `launchpad`'s merge-base — is fixable right now by any of four people, with no grant, no request and no waiting.** #298's premise that "nobody else can advance it by hand" is false.

And if the cohort wants a mechanism that is *not* "trust an admin not to push anything else", `allow_fork_syncing` is strictly narrower than every option #298 lists, and no sweep has mentioned it.

---

## Evidence

### `main`'s protection, in full

```
$ gh api repos/launchpad-26/buzz/branches/main/protection \
    --jq '{enforce_admins:.enforce_admins.enabled,
           approvals:.required_pull_request_reviews.required_approving_review_count,
           checks:.required_status_checks,
           restrictions:{users:[.restrictions.users[].login],
                         apps:[.restrictions.apps[].slug],
                         teams:[.restrictions.teams[].slug]},
           force:.allow_force_pushes.enabled,
           del:.allow_deletions.enabled,
           fork_sync:.allow_fork_syncing.enabled}'
{"approvals":null,
 "checks":null,
 "del":false,
 "enforce_admins":false,
 "force":false,
 "fork_sync":false,
 "restrictions":{"users":["joshuavial"],"apps":[],"teams":[]}}
```

`enforce_admins: false` is the line that matters and no prior sweep read it.

### Who holds admin

```
$ gh api "repos/launchpad-26/buzz/collaborators?per_page=100" \
    --jq '.[] | select(.permissions.admin) | .login'
joshuavial
baradev
tucktuck101
jatin-puri-coder
```

### What GitHub documents about admin bypass

From [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches):

> "By default, the restrictions of a branch protection rule do not apply to people with admin permissions to the repository or custom roles with the 'bypass branch protections' permission."

and, specifically on the push-restriction setting:

> "People and apps with admin permissions to a repository are always able to push to a protected branch."

The second quote is the direct answer. `restrictions.users` constrains non-admins; `enforce_admins` is what would extend it to admins, and it is off.

### What `allow_fork_syncing` is for

From the same page:

> "By default, a forked repository does not support syncing from its upstream repository. You can enable 'Allow fork syncing' to pull changes from the upstream repository while preventing other contributions to the fork's branch."

That is a description of the vendor-branch requirement in GitHub's own words: advance from upstream, and nothing else. It is an independent per-branch setting that composes with push restrictions rather than replacing them.

This repository is a fork of the right parent, and `main` is in the pure fast-forward case, so the mechanism applies cleanly:

```
$ gh api repos/launchpad-26/buzz --jq '{fork,parent:.parent.full_name}'
{"fork":true,"parent":"block/buzz"}
$ git rev-list --left-right --count launchpad/main...upstream/main
0	228
```

Zero ahead means a sync is a fast-forward, not a merge.

### The sync endpoint and its failure modes

`POST /repos/{owner}/{repo}/merge-upstream` is the API behind the UI's "Sync fork" button and `gh repo sync`. Per [the REST reference](https://docs.github.com/en/rest/branches/branches#sync-a-fork-branch-with-the-upstream-repository), it returns `merge_type` of `merge`, `fast-forward` or `none`, and documents two failures: **409** — "The branch could not be synced because of a merge conflict" — and **422** — "The branch could not be synced for some other reason".

For `main` at 0-ahead the expected result is `merge_type: "fast-forward"`. The 409 case is what would happen if someone ever committed directly to `main`, which is the failure the vendor-branch design wants to be loud.

---

## What this means for #273

**#305's live defect is unblocked and always was.** `main` is pinned to 2026-08-06 while `launchpad`'s merge-base with upstream is 2026-08-17, so `git diff main launchpad` currently reports eleven days of upstream's own work as cohort divergence. Four people can fix that today. What still needs deciding is *what point to advance it to* — which is #305's actual question, and is untouched by this.

**#298 should be re-scoped, not answered as written.** It asks "who may advance `main`, and how" against a model where nobody can. Under the real configuration the question becomes a genuine and much better one: **should advancing `main` depend on admin bypass, or on a mechanism that permits only upstream syncing?** Those differ in a way that matters for a public repository — admin bypass means the control on `main` is "an admin chose not to push anything else", while `allow_fork_syncing` makes "only upstream content" a property GitHub enforces.

**The recommendation implied by the fork's own security posture is the narrow one.** This PRD's non-goals record that "the cohort has already lost a repository to an agent taking an irreversible action with legitimately granted privilege". A setting that structurally cannot push anything but upstream's own commits is a better fit for that posture than four standing bypasses — and it is a toggle, not a grant.

**One thing this does not resolve.** `allow_fork_syncing` says who may sync, not *when* or *to what*. It permits a sync to upstream's current tip. If #305 chooses a pin criterion other than "latest upstream" — a `relay-v*` tag, say — then fork syncing cannot express it, and advancing `main` to a chosen historical point still needs a push. So the two mechanisms are not interchangeable, and which one suffices depends on #305's outcome. That dependency is worth stating in #298 rather than discovering later.

---

## Confidence and limits

**High confidence** on the configuration — pasted API output — and on the documented semantics, quoted verbatim with links.

**The admin-bypass conclusion is documentation plus configuration, not an observed push.** I did not test it, and will not: the only test is pushing to `main`. The two doc quotes are unambiguous and the configuration is unambiguous, but a reader should know the difference between "GitHub documents this and the settings match" and "someone did it and it worked". Any of the four admins can settle it in one attempt.

**Not checked.** Whether an organisation-level ruleset or policy overrides repository branch protection here — `admin:org` scope is missing, so org rulesets return 404, and an org rule could in principle re-impose restrictions on admins. Whether `allow_fork_syncing` on a branch with `restrictions` set permits a *non-admin* with write access to sync, or only removes the fork-syncing block for those who could already push: GitHub's documentation describes the setting's purpose but does not state its permission model, and the two search results I read both stopped short of it. That gap matters, because it decides whether the narrow mechanism actually widens access beyond the four admins or merely constrains what they can do. I did not call `merge-upstream`, because it would advance `main` — a real change to a shared branch, and a decision, not an investigation. I did not check whether `gh repo sync` uses that endpoint or a different path.
