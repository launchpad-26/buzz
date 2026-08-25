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
community. ProjectMemory's persisted store MUST NOT live in the public
repository; the public repository contains only ProjectMemory's code and schemas.

That prohibition is scoped to ProjectMemory's persisted store and reaches no
other artefact. As #1407 records it: ProjectMemory is a runtime agent store, not
the documentation corpus, so the representation rule that lane owns does not
reach it. Corpus nodes carrying TEAM_KNOWLEDGE claims under
[ADR-0028](./ADR-0028-corpus-canonical-representation.md) are unaffected and
remain committed Markdown in this repository.

Reads and writes MUST use the caller's existing authenticated Buzz identity.
Every canonical record MUST retain its immutable entry ID and `provided_by`, and
MUST carry a recorded timestamp. There is no timestamp to retain today:
`MemoryEntry` in `launchpad/project-intelligence/memory.py` declares `id`,
`entry_class`, `statement`, `evidence`, `confidence`, `provided_by`,
`temporal_state`, and `superseded_by` — and nothing else — while its docstring
already claims a TEAM_KNOWLEDGE entry is "stored verbatim with who said it and
when". The timestamp is therefore a field #570's implementation MUST add, not one
it preserves.

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
- #570 must add a recorded-timestamp field to `MemoryEntry`, because the dataclass
  carries none today. This ADR mandates the property; it does not describe an
  existing one.
- Agents in the same community can consult one canonical body of TEAM_KNOWLEDGE.
- Relay availability becomes a dependency for canonical reads and writes; a local
  cache may improve availability but cannot replace the canonical store.
- The first implementation starts empty rather than fabricating knowledge from
  indirect evidence.
- Workspace- and crate-local persistence are not supported as canonical scopes.
- The scoping above keeps this record clear of the documentation corpus.
  `launchpad/docs/corpus/schema/node.schema.json` makes `TEAM_KNOWLEDGE` a
  first-class `entry_class` requiring `provided_by`, and
  `launchpad/docs/corpus/schema/fixtures/valid/node-full.md` already commits a
  `TEAM_KNOWLEDGE` claim to this public repository. A repository-wide prohibition
  would contradict ADR-0028, and that contradiction would not merely be untidy:
  under [ADR-0029](./ADR-0029-corpus-evidence-precedence.md) "the corpus author
  stops and records the contradiction rather than picking a side. The affected
  node stays unestablished/flagged until a human resolves it." Scoping the
  prohibition to ProjectMemory's persisted store means no corpus node stalls on
  this record.

## Security implications

TEAM_KNOWLEDGE records can disclose what named people said and can influence what
an agent treats as authoritative. Keeping ProjectMemory's canonical records
outside public Git history prevents irreversible publication. Requiring the
existing authenticated Buzz identity for reads and writes binds access to the
community's existing trust boundary rather than creating an unauthenticated
local-file authority.

This is a disclosure rule about ProjectMemory's runtime store, not a claim that
attributed statements can never be committed. A corpus node's TEAM_KNOWLEDGE
claim is authored deliberately and reviewed in the pull request that adds it,
which is the control ADR-0028 and ADR-0029 rely on; ProjectMemory writes are
recorded by an agent at runtime with no such review, which is why its store is
held outside the repository.

The relay-owned store is a new durable data surface. Its implementation must
preserve record attribution and immutable IDs, enforce community scoping, and
avoid treating a local cache as a source of truth.

## Supersedes

none — establishes the store boundary deferred by #570.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives and evidence remain in #1407.

Not verified in this document: whether the relay offers a durable
community-scoped store today. This record mandates one; no inspection of
`crates/buzz-*` was made to confirm the persistence surface already exists.
