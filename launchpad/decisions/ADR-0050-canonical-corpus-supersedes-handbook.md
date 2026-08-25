---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#1408
decided_in: launchpad-26/buzz#1408
supersedes: ADR-0001, ADR-0002, ADR-0003, ADR-0004
---

# ADR-0050 — Canonical documentation corpus supersedes the handbook

## Decision

The canonical documentation corpus supersedes the handbook as the authority for
cohort system knowledge. New canonical documentation MUST be authored in the
corpus belonging to the system it documents: the Buzz corpus for Buzz-owned
knowledge and the Buzz Infrastructure corpus for infrastructure-owned knowledge.

Existing handbook information MAY be reused when it remains accurate and passes
the destination corpus's provenance, disclosure, and validation requirements. It
is source material, not an authority. The handbook is retired and MUST NOT receive
new canonical documentation.

ADR-0001, ADR-0002, ADR-0003, and ADR-0004 are superseded. Their decisions about
the handbook's repository location, source scope, provenance contract, and
staleness detection no longer govern canonical system knowledge. Each destination
corpus owns the equivalent requirements for its own content.

Material restricted from its destination repository's disclosure class MUST NOT
be migrated there. A source's existence does not authorize publication of its
contents. The retired handbook may remain as a non-authoritative archive while
migration is assessed.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

ADR-0001 through ADR-0004 establish a private, organisation-restricted handbook
as PRD #4's knowledge layer. PRD #602 establishes a new canonical documentation
corpus and anticipates that it replaces separately authored documentation. Keeping
both as authorities would impose permanent precedence and drift management on the
same knowledge domain.

The corpus is not a blank-slate rewrite. Accurate handbook material can accelerate
it, but reuse must not preserve the handbook as a parallel source of truth or
bypass the destination corpus's publication rules.

## Consequences

- The Buzz and Buzz Infrastructure corpora become the only canonical homes for
  their respective system knowledge.
- #602 and its implementation tree can proceed without maintaining a separate
  handbook authority.
- Existing handbook material may be migrated selectively after destination-level
  provenance and disclosure review.
- The handbook stops accumulating new canonical pages and becomes a
  non-authoritative archive during transition.
- The destination corpus must define and enforce its own provenance, staleness,
  and validation requirements; superseding the handbook records does not remove
  those needs.

## Security implications

The handbook's former private publication target did not make its content safe to
copy into a public repository. Every migration must respect the destination
repository's disclosure class. Private-source contents, secrets, live private
infrastructure data, member information, and other restricted material MUST NOT
be published merely because it appears in a retired handbook.

The canonical corpus is responsible for keeping its source provenance,
disclosure boundaries, and stale-content detection inspectable. A retired archive
is not a bypass around those controls.

## Supersedes

ADR-0001, ADR-0002, ADR-0003, and ADR-0004 — canonical knowledge no longer lives
in the handbook; their handbook-specific location, scope, provenance, and
staleness rules are superseded for canonical system knowledge.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives and evidence remain in #1408.