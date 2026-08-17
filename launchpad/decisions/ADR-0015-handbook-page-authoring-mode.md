---
status: Accepted
date: 2026-08-10
issue: launchpad-26/buzz#58
decided_in: launchpad-26/buzz#58
supersedes: none
---

# ADR-0015 — Handbook page authoring mode: hybrid for everything, human-reviewed until 30 pages

## Decision

**Every handbook page is hybrid.** An agent (The Professor, #9) drafts, the provenance
gate (#8) checks, and **a human reviews and merges every page.** No page ships purely
handwritten or purely automatic, and no per-page or per-category authoring mode is
recorded in frontmatter — the mixture is deliberate and uniform, not an emergent property
of who happened to write which page first.

**v1 review floor: 100% human review, no sampling.** The switch to sampling begins at
whichever comes first — the corpus reaching 30 pages, or a second author starting to
write — because both are proxies for the same limit: the point past which reviewing
everything stops being something one person can do attentively.

## Context

#4 (prd-02) asked which handbook pages should be handwritten, synthesized, or produced
through a hybrid workflow, and left the question open. Its sub-issues built the machinery
on both sides without answering it: #9 defines The Professor, the agent that drafts pages;
#8 adds a provenance gate run by a different model from the one that wrote the page; #7
defines the contract every page's claims must satisfy, including a named `author`
accountable for opinion claims; #10 writes the first content set and requires "every page
was reviewed and merged by a human." Left undecided, the mixture would have been set by
precedent — whichever page shipped first — rather than by a recorded policy, which is the
failure `launchpad/AGENTS.md` §4 warns about for open questions generally.

Two constraints ruled out the pure options. Fully automatic synthesis contradicts #10's
review requirement outright and leaves #7's opinion claims with no accountable human
`author` — the provenance gate explicitly does not block on correctness, so it cannot
stand in for review. Handwritten-only for v1 is safe but strands #9's persona and #8's
gate, both of which are built on the assumption that agent-drafted pages are coming.

Hybrid was chosen over the finer-grained alternative — a per-page `authoring` frontmatter
field, decided page by page — because the corpus draws on five source repositories and the
value of the handbook layer is reducing that fragmentation. Hand-writing every page keeps
the fragmentation and lets pages go stale privately instead of publicly, and a page
answering "what does this mean in our Buzz environment" is closer to opinion than to
extraction, which is exactly the kind of claim #7's contract requires an `author` behind.

**What makes this enforceable rather than aspirational:** the provenance gate (#8) already
blocks a merge on nine decidable rules, so "an agent gate checks" is a required status
check, not an intention. Human review is the part no gate can supply, and deliberately so —
the gate can prove a claim carries a source, never that the synthesis is *good*.

## Consequences

**Good.** #10 becomes sizeable, since page cost is dominated by how a page is produced and
reviewed rather than left as an unknown. #9's `temperature` choice gets a stated purpose:
tuning for synthesis and tuning for voice are no longer competing uses of one persona
without a policy deciding between them.

**Bad, stated honestly.** At 30 pages the review policy changes, and nothing currently
*reminds* anyone that threshold was crossed — it is written down here and in #10's design,
not enforced by any check. If the corpus reaches 30 pages without the policy being
revisited, this decision quietly becomes "sample from the start" by default rather than by
choice. A recorded authoring mode also invites the wrong inference if one is later added —
that handwritten pages need less checking. They do not: the gate's secret scan and #7's
claim rule apply identically regardless of who wrote the page.

**Deferred, not decided here.** An explicit `authoring: handwritten | synthesized | hybrid`
frontmatter field was raised as a way to make this decision checkable per page rather than
only stated in this record. It is worth its own issue, with the provenance gate as the
thing that would enforce it — this ADR does not require it to close, and none exists yet.

## Security implications

Authoring mode determines what leaves the trust boundary. An agent-drafted page means the
contents of its source repositories are sent to a model provider, and two of the five
sources #10 draws on — `launchpad-26/launchpad` and `launchpad-26/skills` — are private.
Hybrid-for-everything makes that exposure uniform and visible rather than something a
per-category or per-page policy could obscure by exempting some pages from drafting.

This decision does not create a class of page that bypasses the provenance gate. #8's
secret scan fails closed and escalates to the page's `author` regardless of whether that
author is human or an agent's draft under human review — a human author is as capable of
pasting a live hostname as an agent is, and the same line holds for every page: no live
hostnames, keys, tokens, `.env` bodies, or member rosters.

## Provenance

Decided by Serina on 2026-08-10 while working the open questions of #4, before this ADR
issue existed. #58 was filed afterward, by an agent on behalf of @tucktuck101, to give the
decision a home on the board — the same retrospective-filing pattern used for
[ADR-0004](./ADR-0004-handbook-staleness-detection-mechanism.md). The decision as recorded
here reproduces the comment posted directly on #58 on 2026-08-11, which states it is
ratifying an existing decision rather than opening a new one. `issue` and `decided_in` both
point to #58 because no more specific originating thread is named.

Not verified independently in this document: whether any handbook page has yet been
drafted, reviewed, or merged under this policy, and whether the 30-page or second-author
sampling trigger has been implemented anywhere as an enforced check.
