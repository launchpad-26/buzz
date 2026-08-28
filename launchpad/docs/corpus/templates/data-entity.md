---
id: corpus-template-data-entity
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision -- AGENTS.md excepted, which is type: agent -- uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "schema/README.md and schema/COMPATIBILITY.md were both read in full while choosing this node's type, and neither names a template-specific or policy-specific value beyond what node.schema.json's own field table already states."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "This node is a meta-document about how to author a data-entity node, not itself a domain-model description, so governance is chosen by the same reasoning corpus-readme and every sibling template so far already record for their own type choices, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A corpus node instance actually written from this template -- a real domain entity such as Channel or Thread, documented as it is concretely implemented -- most plausibly takes type: implementation, distinct from type: interfaces-events (already claimed, for a different reason, by the sibling event-kind template) and from type: architecture (already substantially used by the architecture-container and deployment templates for structural/topology views). An entity node's subject is neither a wire contract nor a structural view; it is the concept as it is actually built -- a Rust type plus its storage projection -- which is the closer fit to node.schema.json's implementation value among the surfaces PRD #602 enumerates."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.5
  - statement: "Issue #1337's corpus-template-event-kind pull request (#1542, open) states that a real instance of the event-kind template -- documenting one actual Buzz event kind -- would most plausibly take node.schema.json's interfaces-events type, 'since that is the enum's own dedicated value for the corpus's protocol/interface surface,' and explicitly notes its own template document is not such an instance and does not decide the choice on the instance's behalf."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1542 (open PR, corpus-template-event-kind), read directly via gh pr view"
  - statement: "Issue #1327's architecture-container template pull request (#1529, open) states a real instance of that template 'takes type: architecture, because that value is one of PRD #602's enumerated corpus surfaces and this template's subject (containers) sits under it'; issue #1336's deployment template pull request (#1536, open) independently reaches the same type: architecture conclusion for its own real instances, reasoned through against type: operations and type: platforms in its own ledger."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1529 and launchpad-26/buzz#1536 (open PRs), read directly via gh pr view / gh pr diff"
  - statement: "Relationships must resolve against the corpus tree on the branch being merged into, and at the recorded revision origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is present but excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of the four existing content nodes has data modeling, entities, schemas or domain types as its subject, so no relationships.target among them would be a substantive edge rather than a citation duplicate of what this node's evidence ledger already cites directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "NIP-01 states the only object type on the wire is the event, with fields id, pubkey, created_at, kind, tags, content and sig; id is '32-bytes lowercase hex-encoded sha256 of the serialized event data,' computed by serializing a fixed-order structure of [0, pubkey, created_at, kind, tags, content] to UTF-8 JSON and hashing it; and 'the first element of the tag array is referred to as the tag name or key and the second as the tag value.'"
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "buzz-core/src/kind.rs's own module doc comment states it 'is the authoritative source for Buzz kind numbers,' and every constant is typed u32 because 'NIP-01 specifies kind as an unsigned integer.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-core/src/event.rs defines StoredEvent, documented as 'a Nostr event with relay-assigned metadata,' wrapping a nostr::Event together with received_at (wall-clock receive time), channel_id (Option<Uuid>, 'None for global/DM events') and a private verified flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/event.rs"
  - statement: "buzz-core/src/channel.rs's module doc states its enums (ChannelVisibility, ChannelType, etc.) 'live in buzz-core (zero I/O deps) so both the SDK (client-side) and the DB layer (server-side) can use the same types without pulling in sqlx/tokio' -- one canonical Rust vocabulary for a domain concept shared across a client crate and a server crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "migrations/0001_initial_schema.sql defines a channels table (community_id, id, name, channel_type, visibility, description, canvas, created_by, timestamps, nip29_group_id, topic/purpose fields, ttl fields) under a comment reading 'Conformance: \"Channels and channel membership\". community_id immutable,' with primary key (community_id, id) rather than a globally unique id."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0001_initial_schema.sql defines a thread_metadata table (community_id, event_id, channel_id, parent_event_id, root_event_id, depth, reply_count, descendant_count, last_reply_at, broadcast, primary key (community_id, event_created_at, event_id)) under a comment reading 'Conformance: thread lookups filter by community before event matching,' and crates/buzz-db/src/thread.rs's own module doc states this table 'Tracks parent/root relationships, depth, and reply counts for infinitely nested threads' and 'is populated when events are ingested and updated as replies arrive or are deleted.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/thread.rs"
  - statement: "Root CLAUDE.md's 'Thread counters' entry states reply_count and descendant_count 'are materialized on thread root events' and that 'any code that inserts replies must update these counters.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "migrations/0001_initial_schema.sql's users table includes a capabilities column typed JSONB alongside its scalar columns (nip05_handle, display_name, agent_type, etc.)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "json-schema.org's specification page states the current JSON Schema dialect is 2020-12, which superseded 2019-09; its overview page defines JSON Schema itself as 'a declarative language for defining structure and constraints for JSON data.'"
    entry_class: FACT
    evidence:
      - "https://json-schema.org/specification"
      - "https://json-schema.org/overview/what-is-jsonschema"
  - statement: "This corpus's own node.schema.json declares $schema: https://json-schema.org/draft/2020-12/schema -- the corpus already commits to JSON Schema 2020-12 to describe the shape of its own front matter, so this template reuses that same convention for describing a data entity's attribute shape rather than introducing a second, independent schema language."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Peter Chen's 1976 paper 'The Entity-Relationship Model -- Toward a Unified View of Data' (ACM Transactions on Database Systems), the primary source for entity/attribute/relationship terminology, is paywalled at its canonical ACM Digital Library location: a direct fetch of that page returned HTTP 403 Forbidden. No search for a mirrored free copy was attempted, so this is a checked block at the canonical source, not a claim that no free copy exists anywhere."
    entry_class: FACT
    evidence:
      - "webfetch(https://dl.acm.org/doi/10.1145/320434.320440) -> HTTP 403 Forbidden"
  - statement: "Because Chen 1976 could not be read, this template does not cite the classical entity-relationship model as its adapted industry model, and does not attribute the ordinary-English words 'entity,' 'attribute' or 'relationship' used below to that source -- they are used as this repository's own working vocabulary (matching how thread.rs and channel.rs already talk about the same concepts), the same treatment issue #1348's specification template gives ISO/IEC/IEEE 29148 when its primary source is unreadable."
    entry_class: INFERENCE
    evidence:
      - "webfetch(https://dl.acm.org/doi/10.1145/320434.320440) -> HTTP 403 Forbidden"
      - "crates/buzz-db/src/thread.rs"
      - "crates/buzz-core/src/channel.rs"
    confidence: 0.7
  - statement: "Issue #605 (parent PRD) states the real acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts -- distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1333 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD), opened directly via gh issue view"
  - statement: "Issue #1333's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1333 definition of done, opened directly via gh issue view"
  - statement: "Issue #1334 (the sibling task in this same batch, corpus-template-datastore, open and unstarted at the time this node was written) is scoped by its own issue body to launchpad/docs/corpus/templates/datastore.md, and this node's Scope section states the entity/datastore boundary independently rather than asserting what #1334's eventual content says, since #1334 had not been drafted yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1334, opened directly via gh issue view"
  - statement: "Issue #1467 records that the cross-model (Codex) review provider is currently unavailable -- the Codex workspace is out of credits, confirmed twice including with a trivial read-only prompt, and no other external-model CLI (gemini, agy, pi, llm, ollama, cursor-agent, opencode) is installed -- so a same-model adversarial self-review is the substitute this node's own review pass used."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1467, opened directly via gh issue view"
---

# Template: data-entity

How to write a corpus node whose subject is a **data entity** -- one domain concept
Buzz's system knows about (a channel, a message thread, a user, an agent memory
record) -- described as a concept: its identity, its attributes and their shape,
the invariants that must hold about it, and its relationships to other entities.
This node is the template itself, not an instance of one: it states what a
data-entity node must contain, not a description of any one real Buzz entity.

## Scope and authority

**This node covers** the purpose of a data-entity document, the sections it must
contain, what evidence each section needs, and the industry convention it adapts
(JSON Schema 2020-12, read together with a documented, checked rejection of the
classical entity-relationship model as a citable primary source). It does not
itself document any real Buzz entity beyond one small, explicitly scoped
illustration.

**A note on this issue's own definition of done.** Issue #1333's checklist carries
a MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
-- documents whose subject is a normative policy. This node's subject is a
template, and the parent PRD (#605) states the acceptance bar that actually
applies to a template task: *every template states its purpose, required
sections, evidence expectations and the industry model/standard it adapts.* This
document is built against that sentence. The rest of #1333's checklist -- one
hand-authored document, schema-valid front matter, one independently maintainable
idea, traceable claims, links instead of duplication, a check against the
recorded revision, a clean validator run -- is generic to any corpus node and is
honoured below regardless. This is the same note the sibling deployment and
event-kind templates (#1336/#1337) record for the identical stale-checklist
problem.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `standards/confidence.md`
and `standards/decision-references.md` are the two evidence-mechanics standards
merged so far. This document adds nothing to any of those. What it adds is the
part none of them can: what a *data-entity-scoped* node must say, and where that
shape comes from.

**A note on this template's own `type`, versus a real instance's.** This document
is `type: governance` because it is a meta-document about how to author a node,
not a data entity itself -- the same reasoning `corpus-readme` and every sibling
template already apply to themselves. A real instance written *from* this
template -- an actual entity like Channel or Thread -- most plausibly takes
`type: implementation` instead, reasoned through in this node's own evidence
ledger against `type: interfaces-events` (the value the sibling event-kind
template, #1337, independently claims for a real event-kind instance -- a
different subject: one kind's wire contract, not the broader domain concept) and
`type: architecture` (already substantially used by the architecture-container
and deployment templates for structural/topology views, not for one entity's
shape). That reasoning lives in the ledger rather than being re-argued here in
prose a second time.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The wire-contract sibling this node's boundary is drawn against | `launchpad-26/buzz#1542` (event-kind template) |
| The storage-technology sibling this node's boundary is drawn against | `launchpad-26/buzz#1334` (datastore template, this batch) |
| JSON Schema, primary source | `https://json-schema.org/specification`, `https://json-schema.org/overview/what-is-jsonschema` |
| NIP-01, primary source for the event envelope every Buzz entity ultimately rides on | `https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md` |

If this file and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Purpose

A data-entity node exists to answer one question for a reader who does not yet
know the shape of a domain concept: ***what is this thing, what identifies one
instance of it, what must always be true about it, and how does it relate to
other things Buzz knows about?*** It is not a storage document (which engine
holds the rows, how it is backed up, what its replication topology is -- that is
`#1334`/datastore's job) and it is not a wire-protocol document (what one Nostr
kind's tags and content mean on the wire -- that is `#1337`/event-kind's job,
already claimed for `type: interfaces-events`). A reader should come away able to
name an entity's identity (what makes two records the same thing), its
attributes and their shape, any invariant that must hold about it regardless of
which code path touches it, and which other entities it points to or is pointed
to by -- without being told anything about the SQL engine underneath it or the
exact bytes one particular event kind puts on the wire.

**The failure this template exists to prevent.** Left unscoped, a data-entity
document drifts in one of three directions: down into storage mechanics
(column types, indexes, partitioning -- `#1334`'s territory), out into a single
wire contract (one kind's tag semantics -- `#1337`'s territory, and too narrow a
lens for an entity that several kinds can touch over its lifetime), or sideways
into system-wide correctness rules that are not specific to one entity (the
kind of cross-cutting condition `#1343`/invariant covers). A data-entity node
sits between those three: it names the concept, not the column, the kind, or the
system-wide rule.

**Why this boundary matters concretely in this repository.** A single entity in
Buzz commonly has *two* representations that must agree: the Nostr events that
are its source of truth on the wire, and a derived, materialized projection
maintained alongside them. `thread_metadata` is the clearest example already in
this codebase -- its own module doc states the table "Tracks parent/root
relationships, depth, and reply counts for infinitely nested threads" and "is
populated when events are ingested and updated as replies arrive or are deleted,"
and root `CLAUDE.md`'s own "Thread counters" entry warns that `reply_count` and
`descendant_count` "are materialized on thread root events" and that "any code
that inserts replies must update these counters." A data-entity node for
"message thread" would need to say both things are the *same entity* -- one
source-of-truth representation (the reply events themselves) and one derived
representation that can drift out of sync if a code path forgets to update it.
Neither the event-kind template (which describes one kind's wire shape) nor the
datastore template (which describes a Postgres table's storage mechanics) has
a natural place to say that the two must agree; a data-entity node does.

## The industry model this adapts

**JSON Schema 2020-12** (`https://json-schema.org/specification`,
`https://json-schema.org/overview/what-is-jsonschema`, versioned, superseded
2019-09). The primary source defines JSON Schema as "a declarative language for
defining structure and constraints for JSON data." This template adopts it as
the language for a data-entity node's **Attributes and shape** section for two
concrete, checked reasons rather than by default: first, this corpus already
commits to JSON Schema 2020-12 for its own canonical front matter --
`node.schema.json` itself declares `$schema:
https://json-schema.org/draft/2020-12/schema` -- so reusing it here adds no new
dependency, only a second use of a convention this repository has already
adopted. Second, Buzz's own entities are frequently JSON-shaped in practice, not
purely relational: `users.capabilities` is a `JSONB` column sitting alongside
scalar columns in the same table, and every Nostr event's `content` and `tags`
fields are themselves arbitrary JSON whose shape is meaningful but not
enforced by the SQL schema. A row/column notation describes the storage
projection; JSON Schema describes the shape a reader (or a validator) actually
needs to check against.

**The classical entity-relationship model was checked and set aside, not
ignored.** Peter Chen's 1976 paper, "The Entity-Relationship Model -- Toward a
Unified View of Data" (*ACM Transactions on Database Systems*), is the usual
primary reference for "entity," "attribute" and "relationship" as technical
terms, and was the first source checked while writing this template. It is
paywalled at its canonical ACM Digital Library location: a direct fetch of that
page returned HTTP 403 Forbidden. No search for a mirrored free copy was
attempted, so this is a checked block at the canonical source, not a claim
that no free copy exists anywhere. This template therefore does
not cite Chen 1976 as an adapted industry model, and where the words "entity,"
"attribute" or "relationship" appear below, they are this repository's own
working vocabulary -- the same words `thread.rs` and `channel.rs` already use in
their own doc comments -- not a citation of a source that was never actually
read. This is the same treatment issue #1348's specification template gives
ISO/IEC/IEEE 29148 when its own primary source is unreadable: name what was
checked, say plainly that it was not read, and do not force a secondhand
citation into its place.

**NIP-01 grounds the one representation every Buzz entity shares.** Whatever an
entity's own shape, if it is ever mutated by a client, that mutation arrives as
a Nostr event: NIP-01 states the wire's only object type is the event, with
fields `id, pubkey, created_at, kind, tags, content, sig`, where `id` is "32-bytes
lowercase hex-encoded sha256 of the serialized event data" over a fixed-order
structure of `[0, pubkey, created_at, kind, tags, content]`, and "the first
element of the tag array is referred to as the tag name or key and the second as
the tag value." A data-entity node does not restate this envelope -- every
instance shares it, so restating it per entity would be exactly the duplication
`AGENTS.md` warns against -- but a **Provenance** section (below) must say
whether the entity's canonical form *is* one or more event kinds, is a purely
server-derived projection with no event of its own (like `thread_metadata`), or
both.

## Required sections for a real data-entity instance

A node written from this template documents one entity and covers, at minimum:

1. **Identity.** What makes two records the same instance of this entity. In
   this repository that is very often a composite key scoped by
   `community_id` rather than a single globally unique id -- `channels` is
   primary-keyed `(community_id, id)` specifically because, per its own schema
   comment, "channel UUIDs stay valid wire identifiers, but they are NOT
   globally unique." Say explicitly whether the entity's identity is
   community-scoped, global, or something else, and cite the constraint that
   proves it (a primary key, a unique index, a schema comment).

2. **Attributes and shape.** The entity's fields and what values they may
   hold, expressed as JSON Schema where the entity (or the JSON-shaped parts
   of it) is JSON-native -- content, tags, a `JSONB` column -- and as plain
   prose with a cited type where it is a scalar column or a Rust field with no
   natural JSON projection. Do not restate a type the code already declares;
   cite the struct or column and describe what is not already obvious from
   its name (nullability semantics, what an enum value *means*, not just that
   it exists).

3. **Invariants.** Conditions that must hold about this specific entity
   regardless of which code path touches it -- for example, that a thread
   root's `reply_count` and `descendant_count` must equal the actual count of
   child replies, per root `CLAUDE.md`'s own gotcha. A condition that applies
   across *many* entities, not specific to this one, belongs in
   `#1343`/invariant instead; name that boundary explicitly if a candidate
   invariant could plausibly go either way rather than silently picking one.

4. **Relationships to other entities.** What this entity points to, and what
   points to it -- both as corpus `relationships` (to other entity nodes, once
   they exist) and, separately, as the concrete mechanism in code (a foreign
   key, a Nostr tag reference, an application-level lookup). These are not the
   same claim: a corpus `relationships` edge says two *documents* are related;
   a foreign key says two *rows* are related. State both, and do not let one
   stand in for the other.

5. **Provenance.** Whether this entity's canonical form is one or more Nostr
   event kinds (name them, and link to their `#1337`/event-kind nodes once
   they exist, via a `references` edge -- not `implements`, which
   `relationships.schema.json` reserves for a node's relationship to the
   template it was instanced from, a different direction of edge than one
   sibling instance pointing at another), a purely server-derived projection
   with no event of its own, or both -- as `thread_metadata` is, alongside the
   reply events it is derived from. If both, state which one is the source of
   truth and which is derived, and name the code path responsible for keeping
   them in sync.

6. **Storage pointer, not storage description.** Name where the entity is
   physically held (a table, a Redis key pattern) and link to its
   `#1334`/datastore node, once one exists, via a `references` relationship.
   Do not describe column types, indexes or partitioning here -- that
   duplicates the datastore node's job, and `AGENTS.md`'s "links instead of
   duplicating" rule applies exactly here.

## A small worked illustration, not a real node

To make the boundary above concrete rather than abstract, here is how the
sections above would sort claims about the **thread** entity, at the level of
detail this template requires -- not a real `corpus-thread` node, which would
need its own full evidence ledger:

- **Identity**: a reply's identity is its Nostr event id; a *thread's* identity
  is its root event id, and `thread_metadata` is primary-keyed
  `(community_id, event_created_at, event_id)` per its own schema, not by
  `root_event_id` alone -- every row, including the root's own, carries a
  `root_event_id` pointer.
- **Attributes and shape**: `depth`, `reply_count`, `descendant_count`,
  `last_reply_at`, `broadcast` -- scalar columns, cited to
  `migrations/0001_initial_schema.sql`, not JSON Schema, because
  `thread_metadata` itself is a relational projection, not a JSON-shaped
  attribute.
- **Invariant**: `reply_count`/`descendant_count` must equal the real count of
  child replies, per `CLAUDE.md`'s "Thread counters" gotcha -- one entity's
  own invariant, not a system-wide rule.
- **Relationships**: a reply's `parent_event_id`/`root_event_id` point at
  other thread rows (and, transitively, at other events); this is a
  foreign-key-shaped relationship in code today, expressed in the corpus as a
  `references` edge to a future `corpus-thread`-adjacent node, not (yet) a
  `depends-on` edge, since nothing about a thread's own claims depends on
  another node being current.
- **Provenance**: `thread_metadata` has no event of its own -- it is a
  server-derived projection populated from the reply events that *are* the
  source of truth, updated on ingest and on delete.
- **Storage pointer**: Postgres, table `thread_metadata` -- link to
  `#1334`/datastore's eventual node for how that table is actually operated
  (partitioning, retention), not restated here.

## Scope and omissions

**This document covers** the purpose of a data-entity node, the sections it
must contain, what evidence each section needs, and the industry convention it
adapts (JSON Schema 2020-12), plus a documented, checked rejection of the
classical entity-relationship model as an unreadable primary source.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A single Nostr kind's wire contract -- tag semantics, content shape, delivery classification | `#1337`/event-kind (PR #1542, open) |
| The storage technology holding an entity -- engine, schema mechanics, partitioning, retention, replication | `#1334`/datastore (this batch) |
| System-wide invariants not specific to one entity | `#1343`/invariant (this batch) |
| Any real Buzz entity's own corpus node -- Channel, Thread, User, Agent Memory Record and the rest are not created by this template document itself | future tasks, once scheduled |
| The corpus-standard evidence and citation mechanics this document reuses | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |

**Expected but not verified when this node was written:**

- **No real data-entity instance has been authored from this template yet.**
  The `implementation`-type reasoning above, and the section list, are this
  template's own design; whether they hold up against a first real instance
  (Channel is the most likely candidate, given it already has a dedicated
  `buzz-core` module) is untested. The deployment template (#1336) records the
  identical caveat for its own first-instance risk.
- **Whether a JSON Schema fragment belongs inline in a data-entity node's body
  or as a separate generated artifact was not resolved.** Per `AGENTS.md`, every
  non-`.md` file under the corpus root is rejected until #1316's
  generated-artifact mechanism lands, so today a JSON Schema fragment can only
  be authored as a fenced code block inside the Markdown body -- the same
  constraint the sibling deployment template records for Mermaid diagrams.
- **Whether `relationships.schema.json`'s five relationship types are
  sufficient for entity-to-entity edges** (a foreign key is closer to
  `depends-on` than to `references` in some cases, e.g. an entity whose own
  validity depends on its parent still existing) was not settled here; the
  worked illustration above picks `references` for the thread-reply case as
  the more conservative reading, not as a general rule.

**No `relationships` in this node's own front matter.** None of the four
existing corpus content nodes has data modeling as its subject (checked
directly, not assumed), and the batch-4 siblings and the open event-kind/
deployment templates are unmerged and therefore not valid targets per
`AGENTS.md`'s relationship rule. The absence is deliberate, not an oversight --
the first real data-entity instance node is the moment to add an `implements`
edge back at this template (the schema's own directionality: "source is the
concrete realization of target," e.g. a template instance of a standard) and
`references` edges toward `#1337`/`#1334`'s templates once merged.
