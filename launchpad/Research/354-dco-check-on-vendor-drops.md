# The DCO check and upstream commits on a vendor drop

**Title:** Whether this fork's DCO check accepts upstream commits and automation-authored merge commits
**Summary:** Establishes that `launchpad-26/buzz` runs **no DCO check at all** — the "required DCO Check" described in the root `AGENTS.md` belongs to `block/buzz`, and `launchpad/AGENTS.md` repeats the claim incorrectly. Sign-off is enforced locally by a lefthook `commit-msg` hook, not by CI. Records what a DCO check *would* do if the cohort adopted one: 66 of the 67 backlog commits already carry a sign-off, one revert does not, and GitHub's own merge commits never do.
**Tags:** `upstream-sync` `vendor-drop` `dco` `ci` `process` `documentation-drift`
**Established:** 2026-08-22 · **Answers:** [#354](https://github.com/launchpad-26/buzz/issues/354) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**The question's premise is void: there is no DCO check in this repository.** A vendor drop carrying 67 unmodified upstream commits and an automation-authored merge commit cannot be blocked by a DCO check here, because none runs.

This is not a gap in coverage that someone forgot to close — it is a **documentation defect in two normative files**, one of them the cohort's own.

Three consequences, in order of how much they matter:

1. **No prerequisite exists.** #299 and the drop workflow do not need a DCO remedy, an allowlist, or app configuration. That item can come off the critical path.
2. **`launchpad/AGENTS.md` asserts something false about this fork.** Lines 251–252 state "The DCO check fails any commit without a `Signed-off-by` trailer." No such check exists here. Agents and contributors are being told a CI gate enforces what is in fact enforced only by a local git hook they can bypass with `--no-verify` — which PR #216 did.
3. **If the cohort ever adopts one, it is nearly free.** 66 of 67 upstream backlog commits are already signed off. The two things that would fail are a single upstream revert commit and GitHub's own merge commit.

---

## Evidence

### No DCO check runs here

Scanned every check on the last 40 pull requests in this repository:

```
$ gh pr list --repo launchpad-26/buzz --state all --limit 40 --json number --jq '.[].number' \
  | while read p; do gh pr view $p --repo launchpad-26/buzz \
      --json statusCheckRollup --jq '.statusCheckRollup[]? | (.name // .context)'; done \
  | sort -u | grep -iE 'dco|sign|licen'
   NONE found in 40 PRs
```

The 36 checks that *do* run on the most relevant specimen — PR #216, the 113-commit / 981-file upstream sync — contain nothing resembling DCO:

```
$ gh pr view 216 --repo launchpad-26/buzz --json statusCheckRollup \
    --jq '.statusCheckRollup[] | [(.name // .context), (.conclusion // .state)] | @tsv' | sort -u
adr-boundary                          SUCCESS
Backend Integration (relay e2e)       SUCCESS
Build (linux/amd64)                   SUCCESS
Build (linux/arm64)                   SUCCESS
check                                 SUCCESS
Dead Token Reference Guard            SUCCESS
Desktop                               SUCCESS
Desktop Build (macOS)                 SUCCESS
Desktop Core                          SUCCESS
Desktop E2E Integration               SUCCESS
Desktop E2E Relay                     SUCCESS
Desktop Smoke E2E (1)…(4)             SUCCESS
Detect Changed Paths                  SUCCESS
lint + unittest + render matrix       SUCCESS
Mobile                                SUCCESS
Relay E2E                             SUCCESS
Relay-Driven Mesh Lifecycle Smoke     SUCCESS
Rust Lint                             SUCCESS
scripts                               SUCCESS
Security                              SUCCESS
Server Cross-Compile (×2)             SUCCESS
Unit Tests                            SUCCESS
Web                                   SUCCESS
Windows Rust (x86_64-pc-windows-msvc) SUCCESS
```

### The check exists — on `block/buzz`

```
$ gh pr list --repo block/buzz --state merged --limit 3 --json number --jq '.[].number' \
  | while read p; do gh pr view $p --repo block/buzz \
      --json statusCheckRollup --jq '.statusCheckRollup[]? | (.name // .context)' \
      | grep -iE 'dco|sign'; done
DCO Check
DCO Check
DCO Check
```

So the root `AGENTS.md:134` claim — *"The required **DCO Check** fails any PR with a commit missing a `Signed-off-by` trailer"* — is **correct for upstream and wrong for this fork.** That file is upstream's contributor guide, so this is expected drift, and `launchpad/AGENTS.md` §1 already warns that the root guide is "wrong, not merely irrelevant" for cohort work.

### But the cohort's own guide repeats it

```
$ grep -n -iE 'dco|signed-off|commit -s' launchpad/AGENTS.md
246:git commit -s                          # -s is required: DCO check
251:- **`git commit -s` every time.** The DCO check fails any commit without a
252:  `Signed-off-by` trailer.
```

This one is not inherited drift. It is a claim the fork makes about itself that is not true.

### What actually enforces sign-off

A lefthook `commit-msg` hook, locally:

```
$ grep -n -A4 '^commit-msg' lefthook.yml
44:commit-msg:
45-  commands:
46-    signoff:
47-      run: 'git interpret-trailers --if-exists doNothing --trailer "Signed-off-by: $(git var GIT_COMMITTER_IDENT | sed ''s/ [0-9]* [+-][0-9]*$//'')" --in-place {1}'
```

And nothing in the fork's own PR gate looks at trailers:

```
$ grep -n -iE 'sign|dco' .github/workflows/launchpad-pr-check.yml launchpad/scripts/pr_body_check.py
.github/workflows/launchpad-pr-check.yml:92:      # and executes repository source by design, from the fork's own commit. The
launchpad/scripts/pr_body_check.py:37:unusual place. The fence stripping below is therefore best-effort by design, and
```

Both hits are unrelated prose. A hook is bypassable — `git commit --no-verify`, and `git rebase` / `git cherry-pick` do not run `commit-msg` at all, which `lefthook.yml:14-15` documents.

### What a DCO check would find if one were adopted

Upstream signs off almost everything:

```
$ MB=f8692fa9b52ddcfeb4b95fb4862109983509f131
$ for c in $(git rev-list $MB..upstream/main); do
    git log -1 --format='%B' $c | grep -qi '^Signed-off-by:' || echo "UNSIGNED: $(git log -1 --format='%h %s' $c)"
  done
UNSIGNED: 08eb46ef3 Revert "fix(acp): gate relay-signed workflow messages on their attributed author" (#6311)

signed=66 unsigned=1   (of 67)
```

One commit, and it is a revert — GitHub's revert button does not add a trailer. Some upstream sign-offs use Buzz-generated identities, e.g. `Duncan <dcfd242e…@buzz.block.builderlab.xyz>`, which satisfies a trailer-presence check but would fail a stricter author-match check.

GitHub's merge commits are unsigned, and the previous drop's is:

```
$ git log -1 --format='%h %an%n%B' de1c127fbe7b12bf862e461986e41f1059963228
de1c127fb tucktuck101
Merge pull request #216 from launchpad-26/sync-upstream-2026-08-18

chore: sync launchpad with upstream block/buzz main (113 commits)
```

No `Signed-off-by`. It merged, because nothing checked.

---

## What this means for #273

**Remove the DCO prerequisite from the drop design.** There is nothing to configure, no allowlist to request, and no reason to add a squash or rebase step to work around it. That matters beyond convenience: squashing a drop is rejected by ADR-0021, so a DCO problem that did exist would have pushed the design toward a mechanism the fork has already ruled out.

**Two documentation fixes are now owed, and one of them is a correctness issue.** `launchpad/AGENTS.md:251-252` tells every contributor and agent that a CI gate enforces sign-off. It does not. Either the sentence is corrected to describe the local hook, or the check is adopted so the sentence becomes true. **This is a decision, not a documentation edit** — adopting a DCO check on a fork whose whole purpose is to merge someone else's commits has a real consequence, namely that upstream reverts and GitHub merge commits will fail it. Recommend it be raised against #273 rather than fixed in passing.

**A note on how this was nearly missed.** The instruction that produced this investigation asserted, in passing, that "`-s` is required — the DCO check fails any commit without a sign-off." That is the same claim, from a third source. It is a good illustration of the class of defect #363 is about: a statement that is true upstream, inherited into a fork, repeated in the fork's own normative file, and repeated again by everyone who reads either — with nothing in CI to contradict it. `git commit -s` remains the right practice here and `launchpad/AGENTS.md` still requires it; what is untrue is that anything stops you.

---

## Confidence and limits

**High confidence** that no DCO check runs on pull requests in this repository: the check-name scan covers 40 PRs including every recent sync and ADR PR, and the contrast against `block/buzz` is direct.

**Not checked.** I could not enumerate installed GitHub Apps — `GET /orgs/launchpad-26/installations` needs `admin:org`, which this token lacks — so I cannot rule out a DCO app installed but not configured to report on pull requests. I checked 40 PRs, not all 216. I did not test the behaviour empirically by pushing a branch with an unsigned commit and opening a draft PR, which is what #354's own definition of done asked for; the check-name evidence is strong enough that I judged an extra throwaway PR unwarranted, but it is inference from absence rather than observation of acceptance. I did not check whether branch protection on `launchpad` lists a DCO context as required — it lists none at all, which #358 covers. I did not verify that the Buzz-generated sign-off identities correspond to real people.
