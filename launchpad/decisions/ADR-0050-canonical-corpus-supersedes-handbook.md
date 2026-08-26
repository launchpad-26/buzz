---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#1408
decided_in: launchpad-26/buzz#1408
supersedes: ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0015
---

# ADR-0050 — Canonical documentation corpus supersedes the handbook

## Decision

The canonical documentation corpus supersedes the handbook as the authority for
cohort system knowledge. New canonical documentation MUST be authored in the
corpus belonging to the system it documents: the Buzz corpus for Buzz-owned
knowledge and the Buzz Infrastructure corpus for infrastructure-owned knowledge.

Existing handbook information MAY be reused only after it passes the destination
corpus's provenance, disclosure, and validation requirements. That is #1408's
accepted wording and this record does not add to it; an earlier revision inserted
an independent accuracy gate that no human settled, and it is withdrawn. Handbook material is source material, not an authority. The handbook
is retired and MUST NOT receive new canonical documentation.

ADR-0001, ADR-0002, ADR-0003, ADR-0004, and ADR-0015 are superseded. Their
decisions about the handbook's repository location, source scope, provenance
contract, staleness detection, and page authoring mode no longer govern canonical
system knowledge. Each destination corpus owns the equivalent requirements for
its own content, except where this record says otherwise below.

Material restricted from its destination repository's disclosure class MUST NOT
be migrated there. A source's existence does not authorize publication of its
contents. The retired handbook may remain as a non-authoritative archive while
migration is assessed.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

ADR-0001 through ADR-0004 establish a private, organisation-restricted handbook
as PRD #4's knowledge layer, and ADR-0015 prescribes how its pages are drafted
and reviewed. PRD #602 establishes a new canonical documentation corpus and
anticipates that it replaces separately authored documentation. Keeping both as
authorities would impose permanent precedence and drift management on the same
knowledge domain.

The corpus is not a blank-slate rewrite. Accurate handbook material can accelerate
it, but reuse must not preserve the handbook as a parallel source of truth or
bypass the destination corpus's publication rules.

**The Buzz Infrastructure corpus is named here but not established here.** The
phrase is carried from #1408's accepted outcome, and no record in this repository
establishes such a corpus — `Infrastructure corpus` appears nowhere else under
`launchpad/`. This record therefore names the destination for infrastructure-owned
knowledge without establishing it; where that corpus lives and what governs it
needs its own record in the repository that owns it. Until then, only the Buzz
corpus under `launchpad/docs/corpus/` is an established destination.

## Consequences

- The Buzz and Buzz Infrastructure corpora become the only canonical homes for
  their respective system knowledge, once each is established.
- #602 and its implementation tree can proceed without maintaining a separate
  handbook authority.
- Existing handbook material may be migrated selectively after destination-level
  provenance and disclosure review.
- The handbook stops accumulating new canonical pages and becomes a
  non-authoritative archive during transition.
- The destination corpus must define and enforce its own provenance, staleness,
  and validation requirements; superseding the handbook records does not remove
  those needs.
- **ADR-0003's claim-origin vocabulary must be restated under corpus authority.**
  Of the two available resolutions — carving the vocabulary out of this
  supersession, or requiring the corpus to restate it as its own — this record
  chooses restatement, so that no live artefact sources a rule from a superseded
  ADR. Four live artefacts cite that vocabulary today rather than owning it:
  `launchpad/docs/corpus/schema/README.md` and
  `launchpad/docs/corpus/schema/node.schema.json` both describe `origin` as
  reusing ADR-0003's per-claim origin prefixes; and ADR-0028 justifies the corpus's
  document shape partly by precedent, noting that handbook pages "used the same
  shape (ADR-0003's provenance-contract front matter)". Those two schema files are
  the load-bearing cases — they define a live enum by reference to a superseded
  record; ADR-0028's is a precedent citation rather than a borrowed rule.

  **ADR-0029 is deliberately not in that group, and its own citation is wrong.**
  ADR-0029 rests on "the classification ADR-0003 and
  `launchpad/project-intelligence/CONTRACT.md` already establish", but ADR-0003
  contains no mention of `FACT`, `INFERENCE` or `TEAM_KNOWLEDGE` at all — it
  defines a behaviour-versus-opinion claim rule and the `[upstream]`,
  `[launchpad]`, `[cohort]`, `[supporting]` origin prefixes. That enum is defined
  by `launchpad/project-intelligence/CONTRACT.md`. So ADR-0029 does not depend on
  ADR-0003 for the classification it names, and superseding ADR-0003 does not
  strand it. ADR-0029's attribution is a separate pre-existing error, recorded
  here so it is not lost, and not corrected by this record.
  The corpus schema MUST restate the `origin` enum and the per-claim
  origin prefixes as its own normative vocabulary, and those citations MUST be
  updated to point at it. Until that lands, ADR-0003's superseded text remains
  the only written definition those artefacts resolve against — a documentation
  debt this record creates and names rather than leaves implicit.
- **ADR-0016's open security gate is now made against this record.** ADR-0016
  requires that "Any future implementation must re-confirm the private-repository
  exposure boundary already settled for the handbook (ADR-0001, ADR-0003) before
  it indexes or executes against private sources — that re-confirmation is not
  done by this ADR and remains a gate on implementation". Both records it names
  are superseded here, so the gate is re-pointed: the re-confirmation is made
  against this record's Security implications together with the destination
  corpus's own disclosure requirements. The gate remains open — this record
  re-points it, it does not satisfy it.
- **ADR-0010 must be withdrawn or re-scoped.** It is still `status: Proposed` and
  its decision reads that upstream-intelligence reports "may flag handbook pages
  for refresh, and they do it by reading **the published page index**". This
  record retires the handbook and supersedes ADR-0004's staleness mechanism, so
  ADR-0010's mechanism no longer has a subject. It is left untouched here,
  because a Proposed record is withdrawn or re-scoped by its own decision, not by
  a superseding one.
- **ADR-0015 is superseded, not merely stranded.** #1408's Affected components
  names it alongside ADR-0001 to ADR-0004. Its Decision prescribes that "Every
  handbook page is hybrid. An agent (The Professor, #9) drafts, the provenance
  gate (#8) checks, and a human reviews and merges every page", with a review
  floor until the corpus reaches 30 pages. That pipeline governs an authority
  this record retires, so leaving it Accepted would leave an accepted policy for
  a retired surface. The destination corpus must decide its own authoring and
  review mode; nothing in ADR-0015 carries over automatically, including its
  30-page sampling threshold.
- **ADR-0049 and this record are complementary, not conflicting.** ADR-0049
  prohibits ProjectMemory's persisted store from living in the public repository,
  scoped to that runtime store alone; it explicitly leaves corpus nodes carrying
  TEAM_KNOWLEDGE claims under ADR-0028 unaffected. So the public
  `launchpad/docs/corpus/` remaining canonical for cohort knowledge, including
  its TEAM_KNOWLEDGE claims, is consistent with ADR-0049.

## Security implications

The handbook's former private publication target did not make its content safe to
copy into a public repository. Every migration must respect the destination
repository's disclosure class. Private-source contents, secrets, live private
infrastructure data, member information, and other restricted material MUST NOT
be published merely because it appears in a retired handbook.

This record is now the authority the ADR-0016 gate re-confirms against for the
private-repository exposure boundary, since ADR-0001 and ADR-0003 are superseded.
The substance of that boundary is unchanged by this record: what changes is which
record states it, and that the destination corpus's own disclosure requirements
apply on top. Any implementation that indexes or executes against private sources
still owes that re-confirmation before it runs.

The canonical corpus is responsible for keeping its source provenance,
disclosure boundaries, and stale-content detection inspectable. A retired archive
is not a bypass around those controls.

## Supersedes

ADR-0001, ADR-0002, ADR-0003, and ADR-0004 — canonical knowledge no longer lives
in the handbook; their handbook-specific location, scope, provenance, and
staleness rules are superseded for canonical system knowledge.

ADR-0015 — its handbook page authoring and review pipeline governs a retired
authority; the destination corpus decides its own authoring mode. Named as
affected by #1408's accepted outcome.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives and evidence remain in #1408.

Not verified in this document: whether a Buzz Infrastructure corpus exists in
`launchpad-26/buzz-infrastructure` — only this repository was searched; and
whether the organisation-restricted Pages deployment ADR-0001 describes is live,
a gap #1408 flags itself.
