---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#304
decided_in: launchpad-26/buzz#304
supersedes: none
---

# ADR-0021 — Upstream is adopted by merging; a decline is recorded, not withheld

## Decision

**The fork adopts upstream by merging the vendor drop. A decision not to take an upstream
change is recorded in the divergence ledger, not expressed by declining to merge.**

`launchpad-26/main` is a vendor branch — upstream pinned at a chosen point, advanced
deliberately. A drop is merged into `launchpad` in full. Where the cohort disagrees with
upstream's implementation, that disagreement is a **row in the ledger** stating the fork's
standing position and the mechanism that enforces it, not an omitted commit.

Two alternatives are rejected outright:

- **Cherry-pick only what is wanted.** Rejected because it is *decline-by-default*: to adopt
  anything you must positively evaluate everything. In the drop measured while this was
  decided, that is **67 commits across 796 files evaluated to protect 8**. Upstream's tempo
  being too fast for the cohort to keep up is the reason this work exists at all, so the
  posture that scales with total upstream churn rather than with contested files is the wrong
  one. It also never advances the merge-base, so the gap and the conflict surface grow
  monotonically, and adopted commits exist twice under different hashes — which progressively
  degrades the branch-to-branch comparison the vendor branch exists to provide.
- **Hybrid by scope** — merge outside a declared owned surface, cherry-pick within it.
  Rejected as **not expressible**: git has no per-path merge-base. Approximating it means a
  merge plus per-path overrides, which is this decision described less clearly.

**The load-bearing argument, and the reason this is not the one-way door it appears to be.**

The obvious objection to merging is that the merge-base advances, so git records every
declined commit as integrated and will never offer it again — the disagreement is recorded
once, invisibly, and cannot be revisited. That is true of git's merge machinery **considered
alone**. It is not true of this fork, because the vendor branch holds upstream's version at a
known point indefinitely:

```
git diff main launchpad -- <path>
```

shows exactly what was declined and exactly what adopting it later would cost. **The ledger
plus `main` is what makes the door two-way.** Git is not asked to remember the decision; the
ledger remembers the position and `main` remembers upstream's content. Neither alone is
sufficient — a ledger without the vendor branch records a position with nothing to compare it
against, and a vendor branch without a ledger preserves upstream's version with no record of
why the fork went the other way.

This is also the argument for keeping the two-stage design (`main` as vendor branch,
`launchpad` as the working branch) rather than merging `upstream/main` directly into a branch
off `launchpad`. Two earlier reviews recommended collapsing it on the grounds that `main` had
no consumer. Under this decision `main` **is** the consumer of record: it is the baseline that
makes a decline recoverable.

## Context

The fork carries deliberate divergence from `block/buzz` and expects it to grow. It does not
want to track upstream; it wants to adopt selectively, taking what it wants and deliberately
diverging where it disagrees with upstream's direction. PRD #273's original premise — "keep the
fork current" — was wrong, and correcting it surfaced this as the decision everything else
hangs from.

Measured on 2026-08-21 against merge-base `f8692fa9b` (2026-08-17):

| | Count |
|---|---|
| Files tracked on `upstream/main` | 4,294 |
| Upstream files the fork has modified | 48 (1.1%) |
| — fork-only additions, which cannot conflict | 21 |
| — deletions | 2 |
| — **true modifications of files upstream still owns** | **25** |
| Upstream commits not yet adopted | 67 |
| Upstream files those commits touch | 796 |
| **Of those 796, files the fork also touches** | **8** |
| Files conflicting on a test merge | 4 |

The asymmetry is the whole argument. **99% of what upstream did is uncontested** — the fork has
no opinion about it and never will. Any mechanism whose cost scales with total upstream churn
rather than with contested files is the wrong shape for this repository.

Two further options were considered and rejected as *standing* mechanisms, though either may be
right for an individual case:

- **Merge, then revert what is unwanted.** Uses only core git and leaves a readable record. But
  a revert is *content* on `launchpad`: it conflicts with any later upstream change to the same
  code, adoption after a revert is manual, and reverting a multi-file upstream commit takes down
  changes the fork actually wanted. Workable for a handful of clean, isolated declines; poor as
  the general rule.
- **Squashed vendor drops** — import each drop as a single commit and discard upstream's
  individual history. The classic vendor-branch pattern, and it makes the drop-to-drop diff the
  natural review artifact. Rejected because it destroys upstream authorship and `git blame`
  across 4,294 files, and the fork already holds upstream's real history for free.

A mechanism note that constrains how declines are enforced, recorded here because it is easy to
assume otherwise: **`rerere` is a labour-saver, not a durability mechanism.** It matches on a
hash of the conflict preimage, so when upstream evolves the code surrounding a declined hunk the
preimage changes and the replay silently stops firing — precisely when upstream is most active,
which is the case a vendor fork most needs it for. A merge driver is durable but only
file-granular. Neither alone can hold a position such as "upstream wins on all of `lefthook.yml`
except one line", which is the actual shape of one of the fork's existing divergences. Ledger
rows therefore carry a mechanism as well as a position; that is #294's subject, not this record's.

## Consequences

**Good.** Uncontested upstream arrives free. The merge-base advances every drop, so the gap does
not accumulate, and `git diff main launchpad` narrows to the cohort's actual divergence rather
than divergence plus unadopted upstream work. Curation cost tracks the contested surface, which
is the small number.

**Good.** Declines are revisitable rather than lost, for the reason above. A cohort that changes
its mind about a past decline has a one-command way to see what it would cost.

**Bad.** The ledger stops being documentation and becomes a **control surface**. A missing row is
now a lost decision, not merely an undocumented one — the file silently gets default treatment
and nothing reports that a position was dropped. This raises the stakes on whether the ledger is
machine-checked (#301) and on what a row must contain (#294).

**Bad, and true under every option considered.** No mechanism makes permanent disagreement inside
a *shared* file cheap. The cost is proportional to how much upstream keeps changing code the fork
has overridden, and nothing in this decision controls that. The only real lever is expressing
disagreement as a fork-owned file rather than an edit to upstream's, which is a separate open
decision (#307).

**Bad.** The first drop is the expensive one — 67 commits, 8 contested files, 4 live conflicts,
and no recorded resolutions to draw on. The mechanism should not be judged by how that drop feels.

**Bad, and accepted.** Merging means the fork takes upstream content it has not read. That is
already true of how the fork relates to upstream and is not a new exposure, but this decision
makes it policy rather than habit. What is reviewed per drop is settled separately in ADR-0022.

## Security implications

A durable decline is durable **against upstream security fixes too**. If a ledger row is enforced
by a merge driver, upstream's fix to that file is silently discarded on every future drop, with
nothing reporting it. Two row-groups in the current ledger are exactly this shape: `bin/lefthook`
and `bin/.lefthook-*.pkg` select the binary that executes on every commit and push, and
`Dockerfile` and `deploy/compose/compose.yml` determine which image the fork deploys — #141 was
the failure of unknowingly running someone else's build. ADR-0017's position for the lefthook pin
is "whichever version is newer", which is neither side and is precisely the shape that keeps
upstream's fixes flowing; that is the pattern to prefer for security-relevant rows. Any row whose
mechanism is "fork always wins, automatically" must be flagged in the ledger as requiring review
at each drop rather than trusted to hold itself.

Merging also means ~788 uncontested files per drop enter the fork unread. That is the accepted
posture, bounded by ADR-0022, and it is stated there rather than assumed here.

## Provenance

Decided by @tucktuck101 in conversation on 2026-08-22, after a recommendation.

**His call:** merge-based adoption over cherry-picking, and the two rejections — cherry-pick-only
as decline-by-default, and hybrid-by-scope as inexpressible.

**The recommendation:** merge with declines enforced from the ledger at whatever granularity each
file needs, drafted as option A in #304 by an AI agent (Claude Opus 5) on 2026-08-22, together
with the ledger-plus-`main` two-way-door argument and the 8-of-796 measurement that the decision
turned on. The agent drafted the options and the evidence; it did not choose between them.

**Why the reasoning is recorded and not only the rule.** The objection this decision has to answer
— that merging makes a decline permanent and invisible — is correct on its face and will be raised
again by anyone who has run a vendor branch before. The answer is not "merging is fine"; it is
that the ledger and the vendor branch together restore what git alone forgets. A record that
stated the rule without that argument would be re-litigated at the first drop that declines
something anyone cares about.
