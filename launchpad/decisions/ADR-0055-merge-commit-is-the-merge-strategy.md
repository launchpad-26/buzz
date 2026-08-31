---
status: Accepted
date: 2026-08-31
issue: launchpad-26/buzz#1960
decided_in: launchpad-26/buzz#1960
supersedes: none
---

# ADR-0055 — A pull request lands on `launchpad` as a merge commit, never a squash or rebase

## Decision

**Option A, selected by @tucktuck101 on 2026-08-31 in #1960.**

**Every pull request lands on `launchpad` as a merge commit.** Not a squash, not a rebase,
not a fast-forward tidy-up. `gh pr merge --merge` is the merge command; `--squash` and
`--rebase` are not available and are not to be requested.

**The per-child-Task commits on the branch are preserved by construction.** That is the
point of the choice: under `ADR-0054` (#1956) a whole Feature lands in one pull request of
any size, so those commits are the unit a reviewer walks and the granularity `git bisect`
gets. Keeping one commit per child Task stops being an interim hedge and becomes the
standing rule.

**A pushed branch is not rebased to tidy it.** When a branch falls behind, merge `launchpad`
into it. Rewriting commits a reviewer has already read — and that carry DCO sign-off — breaks
the correspondence between what was approved and what lands.

**The PR title is not the trunk commit subject, and `launchpad/AGENTS.md` §6 said otherwise.**
`merge_commit_title` is `MERGE_MESSAGE`, so the subject is `Merge pull request #N from
<branch>`; `merge_commit_message` is `PR_TITLE`, so the PR title lands in the message body.
Conventional commit titles are still required — on the branch commits, which now all survive
— but not on the premise that one of them becomes the subject on `launchpad`.

This settles the first of `ADR-0052`'s two open questions. This rejects **option B** (squash)
and **option C** (rebase).

## Context

`ADR-0052` left the question open in its own *Consequences*, and named the tension exactly:

> whether a batch squash-merges — collapsing ten Tasks into one commit loses per-Task
> history and coarsens `git bisect`, but merge commits break the convention that a PR title
> becomes the commit subject on `launchpad`.

`ADR-0054` removed the size cap, so one Feature — 15 to 41 child Tasks — now lands in one
pull request. That turned an open question into a live one: squashing such a batch discards
the per-Task commits that are the only thing making a 16,000-line review tractable.

**The platform had already decided it, and the documentation had not noticed.** Read from
`repos/launchpad-26/buzz` on 2026-08-31:

| Setting | Value |
|---|---|
| `allow_merge_commit` | `true` |
| `allow_squash_merge` | **`false`** |
| `allow_rebase_merge` | **`false`** |
| `merge_commit_title` | `MERGE_MESSAGE` |
| `merge_commit_message` | `PR_TITLE` |

History matches: **22 of the last 60 commits on `launchpad` have two parents** — e.g.
`131b02f98 Merge pull request #1910 from launchpad-26/task/1846-state-store`,
`cad6c375f Merge pull request #1945 from launchpad-26/task/skill-corpus-batch-author-one-pr`.

Meanwhile `launchpad/AGENTS.md` §6 told every contributor and agent *"We squash-merge, so
the **PR title** becomes the commit subject on `launchpad`."* Both halves were false: the
method has been merge-only, and the subject has been GitHub's own `Merge pull request #N`
line. A repository whose stated convention contradicts its own history teaches the wrong
thing to whoever reads it first, which is why the correction ships with this record rather
than after it.

**Squash was already unavailable for the largest merges.** `ADR-0021` rejects squashing
vendor drops outright, so option B would have produced two different merge strategies keyed
on the kind of pull request — a distinction nobody asked for.

**Rebase was rejected on recorded prior art**, not preference:
`launchpad/Research/361-long-lived-fork-prior-art.md` collects the documented failure modes
for rebase-the-stack maintenance of long-lived forks, including the kernel documentation's
*"History that has been exposed to the world beyond your private system should usually not be
changed"* and *"Do not rebase a branch that contains history created by others."*

## Consequences

- **Per-Task history survives to the trunk.** `git bisect` lands on a child Task, not on a
  41-Task Feature. This is what `ADR-0054` needs to be workable and is the reason the
  question could not stay open.
- **The first-parent history of `launchpad` is merge commits.** `git log --first-parent`
  reads as a list of merged pull requests; `git log` without it interleaves every Task
  commit. Anyone summarising the trunk wants `--first-parent`. Accepted knowingly: that is
  the shape the repository has had for months.
- **The PR-title-as-subject convention is gone, because it never held.** Conventional titles
  are now required for their own sake — on branch commits that all survive the merge — rather
  than as a mechanism for producing the trunk subject.
- **Merge commits carry no DCO sign-off.** `launchpad/Research/354-dco-check-on-vendor-drops.md`
  established both halves of why that is tolerable here: this repository runs **no DCO check
  at all** (sign-off is a local `commit-msg` hook), and GitHub's merge commits are unsigned
  by construction. Anyone proposing to adopt a DCO check in CI must decide what it does with
  merge commits first; this record does not adopt one.
- **Falling behind is resolved by merging, which produces branch-side merge commits too.** A
  long-lived Feature branch that merges `launchpad` in repeatedly accumulates them. Noisier
  than a rebase, and the trade deliberately taken: no rewriting of reviewed, signed commits.
- **`dismiss_stale_reviews` friction is unchanged and still open.** Merging `launchpad` into a
  Feature branch is a push, and every push dismisses the approval. `ADR-0052` flagged it,
  `ADR-0054` noted it worsens under one-PR-per-Feature, and this record does not fix it — it
  is the second of `ADR-0052`'s open questions and stays open.
- **No repository setting changes.** The merge methods were already `merge`-only; this record
  documents and binds that state rather than altering it. Nothing to configure, nothing to
  roll back.

## Security implications

**None directly.** Merge method determines the shape of history, not what anyone can reach,
read, or authorise. No permission, credential, gate, or boundary is touched, and no
repository setting is changed.

Two second-order effects, stated rather than implied:

- **Auditability improves.** Preserved per-Task commits mean the diff a reviewer read is
  identifiable in the trunk by hash. Squashing rewrites it into a commit nobody reviewed, and
  rebasing changes the hashes of commits that were reviewed and signed. For a public
  repository where the review record *is* the assurance, merge is the strongest of the three.
- **Sign-off coverage stays partial.** Merge commits are unsigned. That is the status quo —
  no DCO check runs here — but a record that mandates merge commits should say so plainly
  rather than let a future reader assume every commit on `launchpad` carries a trailer.

## Supersedes

none — this **answers an open question in `ADR-0052`** rather than replacing anything.
`ADR-0052` stays Accepted and in force; its *Consequences* now has one fewer open item.

## Amends

- **`launchpad/AGENTS.md` §6** — removes the false *"We squash-merge, so the PR title becomes
  the commit subject"* claim and the *"Open, and not decided by ADR-0052"* bullet, replacing
  them with the merge-commit rule, the one-commit-per-child-Task rule, what the merge subject
  and body actually contain, and the no-rebase-of-pushed-branches rule. Amended in this same
  pull request so the two documents do not disagree.

## Related

- **`ADR-0052` (#1765)** — the record that left this question open, and whose part A supplies
  the authority under which the *Decision outcome* on #1960 was recorded.
- **`ADR-0054` (#1956)** — one Feature, one PR, no size cap. The reason this question had to
  be settled now: it makes per-child-Task commits the review unit.
- **`ADR-0021`** — rejects squashing vendor drops, so squash was already unavailable for the
  largest merges in this repository.
- **`launchpad/Research/361-long-lived-fork-prior-art.md`** — the documented failure modes of
  rebase-based maintenance for long-lived forks, on which option C was rejected.
- **`launchpad/Research/354-dco-check-on-vendor-drops.md`** — that no DCO check runs here and
  that GitHub's merge commits are unsigned.

## Provenance

Decided by @tucktuck101 in a working session on 2026-08-31, instructing it explicitly. The
instruction is quoted verbatim in #1960's *Decision outcome* comment and is not tidied.

Every fact above was read rather than recalled: the merge-method and commit-title settings
from `gh api repos/launchpad-26/buzz`; the 22-of-60 two-parent count and the two named merge
commits from `git log launchpad/launchpad`; the false claim from `launchpad/AGENTS.md:376-381`
at `launchpad/launchpad`; the open question from `ADR-0052`'s *Consequences*; the rebase
failure modes and the DCO findings from the two Research documents cited above.

**Not verified:** no merge has been performed under this record — none was needed, because
the repository settings already permit only `merge`, which is itself the strongest evidence
the decision matches practice. The claim that per-Task commits make a large batch reviewable
is inherited from `ADR-0054` and remains unmeasured there. Whether the branch-side merge
commits from keeping long-lived Feature branches current become genuinely noisy is a
prediction, not a measurement.
