---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#306
decided_in: launchpad-26/buzz#306
supersedes: none
---

# ADR-0022 — Curation covers the contested surface; the rest is adopted wholesale by policy

## Decision

**Per-drop adjudication covers only the contested surface: files the fork has modified that
upstream has also touched since the last vendor drop. Everything else upstream changed is
adopted wholesale, without per-change review, by stated policy.**

In the drop measured while this was decided, that is **8 files out of the 796 upstream
touched**. The remaining 788 are taken unreviewed — deliberately, as a recorded position, not
as an oversight.

This is premised on [ADR-0021](ADR-0021-merge-based-adoption-with-recorded-declines.md).
Under merge-based adoption there is a coherent "remainder" to adopt wholesale; under
cherry-picking there is no remainder, because nothing arrives unless it is chosen.

**Why, and not just what.** The alternative — adjudicating all 67 unadopted upstream commits,
or all 796 files they touch — is unaffordable at upstream's tempo, which is the reason PRD #273
exists. An artifact too long to read does not produce review; it produces skimming. **A skimmed
review is worse than an honest blanket policy, because it looks like review.** It carries the
same cost in attention, delivers none of the assurance, and leaves a record implying files were
examined when they were not. The cohort would rather state plainly that 99% of upstream is
adopted unread than maintain a ritual that claims otherwise.

The scope is computed, not curated by hand: the contested surface is the intersection of the
divergence ledger's rows with the files upstream changed in the drop.

## Context

The corrected premise of PRD #273 is that the change agent's job is curation — surface what
upstream changed since the last drop, propose adoption or decline per change, make the declines
durable. "Per change" left the unit open, and the unit determines whether the whole thing is
affordable.

Measured on 2026-08-21 against merge-base `f8692fa9b` (2026-08-17):

| Unit of adjudication | Items a human must consider |
|---|---|
| Per upstream commit | 67 |
| Per upstream file touched | 796 |
| **Per contested file** | **8** |

All three describe the same drop. The fork has modified 48 of upstream's 4,294 files (1.1%), of
which 27 can ever conflict; 8 of those 27 were touched by this drop and 4 conflicted.

There is a real tension in the requirement, and this record resolves it rather than leaving it
to be discovered. "Selectively adopt" sounds like reviewing everything and choosing. But
selective adoption is *more* expensive per change than wholesale merging, not less, and the
stated reason this work exists is that upstream's tempo is already too fast to keep up with. The
requirement is coherent **if and only if** curation is scoped to the surface the fork actually
has opinions about. Scoped that way it is affordable and honest. Scoped to everything it is
neither.

Three other options were considered:

- **Per-commit adjudication of all 67.** The most literal reading, and nothing passes unseen.
  Rejected for the skimming argument above.
- **Areas rather than files** — group by subsystem (relay, desktop, mobile, CI) and adjudicate
  per area. Closer to how the cohort thinks, and it scales as the contested surface grows.
  Rejected for now because the grouping has to be defined and maintained, and an area-level
  "adopt" hides file-level surprises; it remains available if the contested surface outgrows a
  per-file list.
- **No artifact — just `git diff main upstream/main`.** Complete by construction and free.
  Rejected: 796 files is a haystack, not a review artifact, and it carries none of the ledger
  context that makes a decline decidable.

**What this does not decide.** #306 asked more than the scope question, and the rest stays open:
the drop report's shape and format, how contested items are presented, whether a model writes any
part of it, and how the uncontested remainder is summarised. Those are still that issue's subject.
This record settles only which files are adjudicated and which are not.

## Consequences

**Good.** Curation becomes affordable — 8 items rather than 796 — which is the difference between
a practice that survives and one abandoned after two drops. The scope is computed from the ledger,
so it needs no separate maintenance.

**Good.** An unexamined habit becomes a stated policy that can be argued with. The fork already
adopts upstream largely unread; writing that down makes it reviewable rather than tacit.

**Bad, and the most important cost here: an upstream change to a file the fork does not currently
touch is taken unreviewed, and that is exactly how the worst hazard found so far arrives.**
Upstream's new `bin/.lefthookrc` sets `LEFTHOOK_BIN` to the Hermit-pinned `bin/lefthook` at 2.1.3
— the version ADR-0017 records as crashing every contributor's first push in this fork, because
the branch name `launchpad` collides with the top-level `launchpad/` directory. That file is not
in the ledger, does not conflict, and merges clean. Under this decision it is adopted without
review, reintroducing filed bug #196.

**This scope ruling does not solve that, and nothing in this record should be read as claiming it
does.** A clean merge is not evidence of a correct merge. Detecting this class of failure requires
building and testing the drop — `just ci` on the drop PR — which is blocked separately (#299) and
is not something curation scope can deliver. The honest statement of the residual risk is: the
contested surface catches disagreements the fork has already recorded, and catches nothing else.

**Bad.** The contested surface is computed from the ledger, so an incomplete ledger produces a
report that is *confidently* incomplete — it will not mention a file it does not know is
contested, and it will not look empty while doing so. That is a worse failure mode than an
obviously missing report, and it is the strongest argument for the ledger being machine-checked
(#301).

**Bad, and accepted.** A security fix upstream ships to an uncontested file is adopted unread on
the next drop, which is the desired outcome, but a security *regression* in the same file is
adopted just as silently. The compensating control is upstream awareness (#3), not curation.

## Security implications

This record formalises adopting roughly 99% of upstream's changes without per-change review. That
is the fork's existing posture — it runs upstream's code today — so the decision does not create
the exposure, but it does make it policy, and policy should be stated at its true strength: **the
cohort accepts externally-authored code into its deployed build without reading it, on every
drop.**

Two things bound that. First, the fork merges from a single upstream it already depends on
wholesale, not from many; the trust decision is one relationship, made once, not 796 decisions per
drop. Second, the vendor branch pins upstream at a chosen point rather than tracking HEAD
(ADR-0021), so the content adopted is a point somebody selected rather than whatever was pushed
that hour.

What is *not* bounded, and should not be presented as though it were: nothing in this decision
inspects the 788 unreviewed files for hostile or broken content, and the `bin/.lefthookrc` case
above demonstrates that a merge-clean upstream file can carry a defect with real local
consequences — in that instance, changing which binary executes on every commit and push. The
control for that is building and testing the drop before it merges, which is a different decision
and is currently unresolved.

## Provenance

Decided by @tucktuck101 in conversation on 2026-08-22, after a recommendation.

**His call:** that curation is scoped to the contested surface and the remainder is adopted
wholesale by policy, and that the reason — not merely the rule — be recorded.

**The recommendation:** the same scoping, drafted as option A in #306 by an AI agent (Claude Opus
5) on 2026-08-22, together with the affordability analysis, the 67 / 796 / 8 comparison, and the
argument that a skimmed review is worse than an honest blanket policy. The agent had raised the
tension in the requirement as a strain worth naming rather than working around; this decision
resolves it. The agent drafted the options and the evidence; it did not choose between them.

**Recorded against the agent's own finding.** The `bin/.lefthookrc` hazard in Consequences was
found by that agent while sweeping this PRD, and it is the clearest single argument *against* the
decision recorded here. It is written into the record deliberately, at the decider's instruction,
rather than left in an issue comment — a scope ruling whose known counter-example lives somewhere
else is a scope ruling nobody can evaluate.
