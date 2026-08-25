---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#1407
decided_in: launchpad-26/buzz#1407
supersedes: none
---

# ADR-0049 — ProjectMemory uses shared relay-owned community storage

## Decision

ProjectMemory persists TEAM_KNOWLEDGE in one shared, relay-owned store per Buzz
community. The public repository contains only code and schemas; it MUST NOT
contain persisted TEAM_KNOWLEDGE records.

Reads and writes MUST use the caller's existing authenticated Buzz identity.
Every canonical record MUST retain its immutable entry ID, `provided_by`, and
recorded timestamp.

The canonical scope is a community, not a workspace or crate. A workspace selects
its ProjectMemory store through its configured relay.

Implementations MAY maintain a local cache for performance. Cache loss MUST NOT
lose canonical knowledge, and a local cache MUST NOT become an authority.

No prior persistent store exists. The implementation begins with an empty store
and MUST NOT infer TEAM_KNOWLEDGE from commits, source code, or prior process
memory.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

ProjectMemory currently loses TEAM_KNOWLEDGE at process exit. TEAM_KNOWLEDGE is
verbatim knowledge supplied by a named developer, with attribution, and cannot be
re-derived from code or silently removed by absence of corroboration.

A committed JSON file would make that knowledge reviewable, but it would also put
verbatim attributed statements in permanent public Git history. A gitignored local
file avoids disclosure but makes supposedly shared knowledge depend on the
contributor machine that happened to record it. Both conflict with the required
combination of durability, shared authority, and controlled disclosure.

## Consequences

- #570 can implement durable ProjectMemory load and save without creating a
  public corpus of attributed developer statements.
- Agents in the same community can consult one canonical body of TEAM_KNOWLEDGE.
- Relay availability becomes a dependency for canonical reads and writes; a local
  cache may improve availability but cannot replace the canonical store.
- The first implementation starts empty rather than fabricating knowledge from
  indirect evidence.
- Workspace- and crate-local persistence are not supported as canonical scopes.

## Security implications

TEAM_KNOWLEDGE records can disclose what named people said and can influence what
an agent treats as authoritative. Keeping canonical records outside public Git
history prevents irreversible publication. Requiring the existing authenticated
Buzz identity for reads and writes binds access to the community's existing trust
boundary rather than creating an unauthenticated local-file authority.

The relay-owned store is a new durable data surface. Its implementation must
preserve record attribution and immutable IDs, enforce community scoping, and
avoid treating a local cache as a source of truth.

## Supersedes

none — establishes the store boundary deferred by #570.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives and evidence remain in #1407.