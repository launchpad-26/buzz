# Existing tooling for vendor-drop automation and drop-report computation

**Title:** What off-the-shelf tools exist for this job, and what the bespoke baseline actually costs
**Summary:** The drop report's core computation is **two git commands running in 0.06 seconds**, reducing 80 commits and 912 files to **8 contested files and 14 commits to adjudicate**. A third — `git range-diff` — mechanically finds the one divergence that has converged with upstream, which is the termination check #361 recommended and it needs no ledger to work. **Copybara is the wrong shape** (one authoritative repository; this fork has two). **`wei/pull` is a live candidate nobody assessed** and could cover advancing `main`, opening the drop PR, and labelling conflicts with no code — at the cost of a third-party app holding write access. Also corrects #356: a relay-specific changelog **does** exist upstream, and it is stale and not relay-scoped.
**Tags:** `upstream-sync` `vendor-drop` `tooling` `copybara` `adr-0009` `prd-273`
**Established:** 2026-08-22 · **Answers:** [#368](https://github.com/launchpad-26/buzz/issues/368) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

**References are pinned.** Fork-side claims cite `launchpad-26/buzz` at
[`5d76799d6e44f2f76aa7bd78c5343d339af98f63`](https://github.com/launchpad-26/buzz/tree/5d76799d6e44f2f76aa7bd78c5343d339af98f63); upstream-side claims cite `block/buzz` at
[`025425591ed67518a63870316f1473ffd02dd520`](https://github.com/block/buzz/tree/025425591ed67518a63870316f1473ffd02dd520). Paths inside fenced blocks are command
*output* and are left unlinked deliberately. `.github/pull.yml` is `wei/pull`'s own configuration
filename, not a file in this repository, so it is named rather than linked.

---

## Finding

**The belief recorded when this question was filed — "the drop-report computation is three git commands and the rest is bespoke" — is correct, and the number is two.** But two of the dismissals in that same note were wrong: `wei/pull` is a serious candidate, and `git range-diff` does substantially more than expected.

| Tool | Verdict | Reason |
|---|---|---|
| **git pipeline (`diff --name-only` + `comm`)** | **Adopt — it is the baseline** | 2 commands, 0.06s, 912 files → 8 contested |
| **`git range-diff`** | **Adopt — better than expected** | Found the one converged divergence unaided |
| **`wei/pull`** | **Assess seriously** | Could cover `main`, the drop PR and conflict labelling with no code |
| GitHub `merge-upstream` API | Useful for `main` only | Covered in [#359](https://github.com/launchpad-26/buzz/issues/359); cannot express a chosen pin |
| **Copybara** | **Reject, with reasons** | One-authoritative-repository model; this fork has two |
| `git-subtree` / `git-subrepo` | Reject | For vendoring a subdirectory, not a whole-repo fork |
| Renovate / Dependabot | Reject for this purpose | Dependency manifests, not source vendoring; ADR-0007 already owns deps |
| Mergiraf | Orthogonal | Reduces conflict noise, expresses no position ([#366](https://github.com/launchpad-26/buzz/issues/366)) |

---

## The bespoke baseline, measured

```
$ MB=f8692fa9b52ddcfeb4b95fb4862109983509f131
$ time ( comm -12 <(git diff --name-only $MB launchpad/launchpad | sort) \
                  <(git diff --name-only $MB upstream/main | sort) )
8
( ... ) 0.00s user 0.00s system 9% cpu 0.063 total
```

**Two commands, 0.06 seconds, 912 files reduced to 8.** Then the adjudication list:

```
$ git log --oneline --no-merges $MB..upstream/main -- $(cat contested.txt)
cd0d33f08 fix(hooks): scope pre-push lanes to branch merge-base diff (#6423)
84c095f8b feat(cli): accept Buzz message links for thread reads (#6359)
2ce8df853 fix(models): curate Databricks alias-aware labels for 5 missing endpoints (#6360)
2a236e413 refactor(prompt): simplify Buzz agent guidance (#6340)
a9640c7cc Add Buzz-native collaboration benchmarks (#6264)
81567b76a chore: serialize mobile pre-push checks (#6322)
87f8ff82a feat(desktop): refine repository-aware project workspaces (#6003)
7e2651791 Add font size and conversation density preferences (#5644)
50a71137e feat(managed-agents): close five Claude Code agent-config gaps (#4557)
b74700daa chore(hooks): keep mobile analysis out of pre-commit (#6236)
cc8a8b0dc fix: bump h2 for RUSTSEC-2026-0258 (#6222)
6d45f9866 ci: make file-size policy a first-class gate (#6187)
f0234f144 fix(desktop): eliminate mounted-view CPU burn — ... (#6198)
ee992ff08 fix(desktop): restore release agent mentions (#6182)
--- count: 14
```

**80 commits → 14 to read.** That is the whole reduction #306 is trying to design, in three commands and no model.

## `git range-diff` does more than expected

Run against the two commit ranges, it pairs fork commits with upstream ones by similarity:

```
$ git range-diff --no-color $MB..launchpad/launchpad $MB..upstream/main
...
$ # summary rows containing a matched pair:
209:  765746534 !   6:  cc8a8b0dc fix: bump h2 0.4.14 -> 0.4.18 (RUSTSEC-2026-0258)
```

**One matched pair in the entire history, and it is exactly the right one.** `!` means matched-but-changed: the fork's `765746534` and upstream's `cc8a8b0dc` are the same logical change with different content — the fork went to h2 0.4.18, upstream to 0.4.16. That is precisely the convergent divergence [#352](https://github.com/launchpad-26/buzz/issues/352) identified in `Cargo.lock`, **found mechanically, with no ledger and no human judgement.**

This is the automated form of the termination check [#361](https://github.com/launchpad-26/buzz/issues/361) and [#364](https://github.com/launchpad-26/buzz/issues/364) both identified as the standard answer to obsolete divergence: *has upstream since done this themselves?* One command answers it for every fork commit at once.

The narrower cousin is exact rather than fuzzy:

```
$ git log --oneline --cherry-mark --left-right --no-merges launchpad/launchpad...upstream/main | grep '^='
(no output)
```

`--cherry-mark` uses patch-id equality, so it finds literal duplicates only — and correctly finds none, because no fork commit has been applied upstream verbatim. **Useful as a precise signal, useless for equivalent-but-different fixes**, which is exactly the h2 case `range-diff` caught. Both are worth having; they answer different questions.

## Copybara — assessed, not dismissed

Its purpose, from its own README: *"A tool for transforming and moving code between repositories"*, with the named use cases *"Importing sections of code from a confidential repository to a public repository"* and the reverse.

The decisive property is its model:

> "requires designating one of the repositories to be the authoritative repository, so that there is always one source of truth"

**This fork does not have one source of truth, by design.** Upstream owns 4,294 files; the fork owns 27 in-place edits, 21 additions, and 259 commits of its own work. ADR-0021's merge-based adoption is precisely a two-authority arrangement. Copybara models the destination as *derived from* the origin by transformation, and has no representation for a destination with independent history — which is what `launchpad` is.

It is worth saying what would be attractive if that mismatch did not exist. Copybara's transformations are chained `glob` and `replace` operations applied on migration — which is the transforming-merge-driver idea from [#362](https://github.com/launchpad-26/buzz/issues/362) at repository scale, declaratively, in one config file. If the fork's divergence were purely mechanical substitutions (the five ADR-0005 deployment-identity files are exactly that shape) Copybara would express it well.

Operational costs, for the record:
- *"Install JDK 11"* and *"Install Bazel"*. Prebuilt snapshots exist but come with an explicit disclaimer: *"released automatically without any manual testing, version compatibility or correctness guarantees."*
- State lives in the destination: *"it stores the state in the destination repository (As a label in the commit message)"* — meaning Copybara rewrites commit messages, which for a vendor branch whose purpose is to be a faithful mirror is a direct conflict with [#305](https://github.com/launchpad-26/buzz/issues/305)'s requirement.

**Reject.** Not because it is heavyweight — because the fork's shape is not the shape it models.

## `wei/pull` — the candidate I wrongly expected to dismiss

A GitHub App that *"keeps your forks up-to-date with upstream via automated pull requests"*, configured in `.github/pull.yml`, which *"regularly checks for upstream changes periodically"* and can be *"manually trigger[ed]"* via a URL.

What makes it relevant rather than naive is the configuration surface:

- `mergeMethod`: `merge` | `squash` | `rebase` | `hardreset` | `none`
- `conflictReviewers` and `conflictLabel` — reviewers and a label applied *when the sync conflicts*
- `assignees`, `reviewers`, `label`
- `mergeUnstable` — *"merge pull request even when the mergeable_state is not clean"*

**That maps onto three separate things #273 is designing:**

| #273 item | What `wei/pull` offers |
|---|---|
| Advancing `main` (#305/#298) | `mergeMethod: hardreset` on `main`, manual trigger — a fast-forward equivalent, no code |
| Opening the drop PR (#299) | The app opens it; `mergeMethod: merge` gives merge-based adoption per ADR-0021 |
| Escalation (#296/#297) | `conflictReviewers` + `conflictLabel` — routing a conflicting sync to named humans |

Its stated constraints hold here: *"Upstream must be in the same fork network"* — this repository is a fork of `block/buzz`, confirmed in [#359](https://github.com/launchpad-26/buzz/issues/359) — and *"Make a backup if you've made changes"*, which is a warning about `hardreset` and is why that method must never be pointed at `launchpad`.

**Two things stop this being a recommendation.**

**First, a belief I could not verify.** #299's premise is that a `GITHUB_TOKEN`-authored PR fires no `pull_request` workflows. A **GitHub App** installation token is a different actor, and I believe an App-authored PR *does* trigger workflows — which would dissolve #299 entirely. **I did not test this**, and it is the single most valuable thing to test next: one throwaway PR from an app-authored branch would settle it.

**Second, and this is not a technical objection.** `wei/pull` is a **third-party GitHub App with write access to a public repository**. This PRD's own non-goals record that *"the cohort has already lost a repository to an agent taking an irreversible action with legitimately granted privilege"*, and `mergeMethod: hardreset` is exactly an irreversible action. Adopting it is a supply-chain and privilege decision of the same class ADR-0015 and #103 govern, not a convenience choice. It belongs in front of whoever owns those.

## Correcting #356 on the relay changelog

[#356](https://github.com/launchpad-26/buzz/issues/356) concluded that the relay has *"no changelog section of its own"*. **That was wrong.** Three changelogs exist:

```
$ git ls-tree -r --name-only upstream/main | grep -i CHANGELOG
CHANGELOG.md
crates/buzz-relay/CHANGELOG.md
mobile/CHANGELOG.md
```

I looked only at the root one. ADR-0009 found [`crates/buzz-relay/CHANGELOG.md`](https://github.com/block/buzz/blob/025425591ed67518a63870316f1473ffd02dd520/crates/buzz-relay/CHANGELOG.md) on 2026-08-10 and I should have read that record before searching.

Two things qualify the correction, and both were already in ADR-0009:

- **It is stale.** Its newest section is `relay-v0.2.1` (2026-08-08), and it is **not** in the current drop — only the root [`CHANGELOG.md`](https://github.com/block/buzz/blob/025425591ed67518a63870316f1473ffd02dd520/CHANGELOG.md) changed. It updates when a relay tag is cut: three times in 44 days.
- **It is not relay-scoped.** ADR-0009 records that it *"already contains `feat(desktop)` and mobile entries under `relay-v0.2.1`"*. Confirmed — the file's `relay-v0.2.1` section contains `feat(desktop): adding rich link previews to messages` and `Polish mobile inbox and media flows`.

So the substance of #356's conclusion survives — there is no reliable relay-scoped signal — but the specific claim was false and the correction belongs on the record.

## What already exists under ADR-0009 / ADR-0010

**No implementation.** `launchpad/upstream-intel/` does not exist, and nothing in [`launchpad/scripts/`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/scripts) addresses upstream tracking. Both records decide scope only.

What they decide is worth carrying into #306 because it **independently agrees with [#355](https://github.com/launchpad-26/buzz/issues/355)**: ADR-0009 scopes upstream-intelligence Phase 1 to *"the relay only"*, on the ground that *"Relay is the only component the cohort operates and deploys"*. #355 reached the same boundary from the image build — 19 of 796 files. Two independent derivations of the same scope is the strongest signal in this whole PRD family that the operational surface is the right organising principle.

ADR-0009 also states the residue plainly: scoping to the relay *"narrows which release stream triggers a report, but does not by itself bound what content a relay report might touch — that's a separate reduction problem, not solved by this decision."* **The two-command pipeline above is a solution to exactly that reduction problem**, and #306 should note that ADR-0009 left it open rather than treating it as unaddressed.

---

## What this means for #273

*This section is my recommendation as the author, not a finding — including the rejection of Copybara and the suggestion that `wei/pull` be assessed. The measurements and quotations above are the evidence; what should be done about them is my judgement and carries no source reference.*

**#306 is much smaller than its framing.** The computation is three commands. What remains genuinely bespoke is presentation — and [#365](https://github.com/launchpad-26/buzz/issues/365) established that PR #216's body is already a worked template for that. So the largest work item under this PRD is closer to "wire three git commands into the shape of an existing PR body" than to "design an artifact".

**`git range-diff` should be part of the drop report, not just the ledger check.** It answers "which of our divergences has upstream converged on?" for every commit at once, and it got the h2 case right unaided. Combined with #361's `Upstream-Status` recommendation, that column can be *partly computed* rather than hand-maintained.

**#305 and #299 both have off-the-shelf options that nobody has weighed** — `wei/pull` for both, GitHub's `merge-upstream` for `main`. Neither is free of consequence, and the `wei/pull` privilege question is real, but "we assumed bespoke" is not a reason and it was the assumption in both issues.

**One test would settle #299.** Whether a GitHub App-authored PR triggers `pull_request` workflows. I believe it does; I did not verify it; it is one throwaway PR away.

---

## Revised for the fork's horizon (#357)

Added after @tucktuck101 decided on 2026-08-22 that the fork ends with the cohort project on
2026-09-17. Tool assessments are mostly judgements about operating cost over time, so this is the
document the decision touches most.

**The measurements are unchanged.** Two commands, 0.06 seconds, 912 files to 8, 80 commits to 14; and
`git range-diff` finding the h2 convergence unaided.

*The rest of this section is my recommendation as the author, not a finding.*

**The three-command pipeline gets stronger, and it was already the recommendation.** It needs no
installation, no credential, no standing privilege and no maintenance. Under a demonstrative target it
is close to ideal: it can be shown working in a terminal and it will still work on the last drop.

**Copybara's rejection is now overdetermined.** I rejected it on data-model grounds — one
authoritative repository against this fork's two — and that reason stands on its own. The horizon adds
a second: JDK, Bazel and a Starlark config are a setup cost amortised over future imports, and there
are at most a handful left to amortise against.

**My "assess `wei/pull` seriously" recommendation should be downgraded, and I am downgrading it.** Its
appeal was covering three separate #273 items with no code — worth real consideration for an ongoing
pipeline. For two or three remaining drops, a third-party GitHub App holding standing write access to
a public repository, with `hardreset` available, is a permanent privilege grant bought against a
handful of uses. One `POST /merge-upstream` call for `main` and one hand-opened PR per drop is
cheaper, needs no grant, and demonstrates the same thing. The privilege question I raised as
"not technical" is now decisive rather than a caveat.

**One item gets *more* worthwhile, not less.** The untested question — whether a GitHub App-authored
PR triggers `pull_request` workflows — is one throwaway PR and it settles #299 outright. Cheap facts
that close open decisions are exactly what is worth spending remaining time on.

**And one framing correction.** I wrote that "building bespoke tooling because nobody looked is the
most expensive available mistake in a fork with a hard end date". With the end date now known, the
sharper statement is the reverse: *adopting* infrastructure is the expensive mistake, because setup
cost is paid once and the payoff is collected per drop, and there are almost no drops left.

## Confidence and limits

**High** on the pipeline measurements, the `range-diff` result and the changelog correction — all pasted command output, reproducible.

**High** on Copybara's model and requirements — quoted verbatim from its own README.

**Medium on `wei/pull`.** Everything about it here comes from its own documentation. **I did not install it, configure it, or run it**, and I did not check its permission scopes, its maintenance status, or its incident history — all of which matter for a third-party app with write access and none of which I examined.

**Not verified, and it is the load-bearing gap in this answer:** whether a GitHub App-authored pull request triggers `pull_request` workflows. My belief that it does rests on the general distinction between the built-in Actions token and an App installation token, not on a test or a documentation quote. If it is wrong, the `wei/pull` case for #299 collapses.

**Also not checked.** I did not evaluate `git-subtree` or `git-subrepo` beyond their purpose — they vendor a subdirectory, and this fork forks a whole repository, so the mismatch is structural rather than something I tested. I did not look for distribution import scripts as reusable tools (Debian's and Yocto's are tightly coupled to their packaging formats). I did not fully parse `git range-diff`'s summary format: I counted matched pairs by grepping for `!` and `=` and verified the one hit by reading it, but my counts of ours-only and theirs-only rows were unreliable and I have not reported them. I did not measure the pipeline on a cold cache or a fresh clone, only in a warm worktree. I ran no builds and no `cargo` — disk on this machine is at 99% capacity with 5.2 GiB free, and nothing here needed a build.

## Sources

- [google/copybara README](https://github.com/google/copybara) — purpose, one-source-of-truth model, JDK 11 + Bazel, snapshot disclaimer, state-in-destination
- [Copybara examples](https://github.com/google/copybara/blob/bcf8c9164d5372d77546d64dbe47615a34ed8417/docs/examples.md) and [Basic Usage](https://deepwiki.com/google/copybara/2.3-basic-usage) — `copy.bara.sky`, Starlark, `glob`/`replace` transformations
- [wei/pull](https://github.com/wei/pull) — `.github/pull.yml`, `mergeMethod`, `conflictReviewers`, `conflictLabel`, fork-network constraint
- [git-range-diff(1)](https://git-scm.com/docs/git-range-diff) and [git-log(1)](https://git-scm.com/docs/git-log) — `--cherry-mark`, `--left-right`
- [`launchpad/decisions/ADR-0009-upstream-intel-phase-1-scope.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/decisions/ADR-0009-upstream-intel-phase-1-scope.md) — relay-only Phase 1, the relay changelog finding, the open reduction problem
