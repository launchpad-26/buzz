---
id: layers-data-postgres-events-table
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "migrations/0001_initial_schema.sql defines the events table (lines 190-235) as PARTITION BY RANGE (created_at), with primary key (community_id, created_at, id) rather than a single globally unique id column."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-235"
  - statement: "The events table's columns are community_id UUID NOT NULL REFERENCES communities(id), id BYTEA NOT NULL, pubkey BYTEA NOT NULL, created_at TIMESTAMPTZ NOT NULL, kind INT NOT NULL, tags JSONB NOT NULL, content TEXT NOT NULL, search_tsv TSVECTOR GENERATED ALWAYS AS (...) STORED, sig BYTEA NOT NULL, received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), channel_id UUID, deleted_at TIMESTAMPTZ, d_tag TEXT, not_before BIGINT, delivered_at BIGINT."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-235"
  - statement: "search_tsv is generated/stored from content via to_tsvector('simple', content), except for a fixed list of privacy-sensitive kinds (1059 gift wrap, 30300 event reminder, 30622 DM visibility, 44100/44101 membership-change notifications) which get NULL::tsvector instead, per the column's own migration comment, so those kinds are storage-level unsearchable rather than merely filtered at query time."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-224"
  - statement: "events carries nine indexes (idx_events_community_id, idx_events_community_channel_created, idx_events_community_pubkey_kind_created, idx_events_community_kind_created, idx_events_community_deleted, idx_events_addressable, idx_events_parameterized, idx_events_not_before, idx_events_search_tsv), every btree one community_id-leading, per the migration's own comment that community scoping is supplied by the community-leading btree filters."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:250-278"
  - statement: "crates/buzz-db/src/event.rs's module doc states: 'AUTH events (kind 22242) are never stored — they carry bearer tokens. Ephemeral events (kinds 20000–29999) are never stored — Redis pub/sub only. Deduplication is application-layer: ON CONFLICT DO NOTHING.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:1-5"
  - statement: "insert_event (crates/buzz-db/src/event.rs:273-329) rejects KIND_AUTH and any ephemeral kind before writing, then INSERTs with ON CONFLICT DO NOTHING against the table's primary key, so a duplicate (community_id, created_at, id) tuple is silently dropped rather than erroring; the returned was_inserted flag is result.rows_affected() > 0, telling the caller whether the row was new."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:273-329"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_AUTH = 22242 (line 77); is_ephemeral (lines 769-771) for the range 20000-29999; is_replaceable (lines 776-778, kinds 0, 3, KIND_CHANNEL_METADATA, 10000-19999) whose own doc comment states NIP-33 parameterized-replaceable kinds (30000-39999) 'use a different replacement key (includes d-tag) and are handled separately via replace_parameterized_event'; and is_parameterized_replaceable (lines 783-785) whose doc comment states 'These events are keyed by (pubkey, kind, d_tag) — the latest created_at wins.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:769-785"
      - "crates/buzz-core/src/kind.rs:77"
  - statement: "crates/buzz-db/src/lib.rs defines replace_addressable_event (line 4829) and replace_parameterized_event (line 5156) — the two functions kind.rs's own doc comment names as the separate replacement path for NIP-01/NIP-33 replaceable and parameterized-replaceable kinds, distinct from insert_event's plain-id-conflict dedup path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:4829"
      - "crates/buzz-db/src/lib.rs:5156"
  - statement: "soft_delete_event (crates/buzz-db/src/event.rs:788-807) sets deleted_at = NOW() by (community_id, id) and returns whether a live row was found; soft_delete_by_coordinate (838-862) does the same by the NIP-33 coordinate (community_id, kind, pubkey, d_tag), guarded by created_at <= the deletion event's own created_at so a tombstone cannot erase a version newer than itself; soft_delete_event_and_update_thread (869-919ish) wraps a delete with a thread reply-counter decrement in one transaction so a crash between the two cannot leave counters inflated."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:788-862"
      - "crates/buzz-db/src/event.rs:869-919"
  - statement: "Every live-row read in crates/buzz-db/src/event.rs (query_events, count_events, get_event_by_id, get_latest_global_replaceable, get_events_by_ids, get_last_message_at, and more) filters deleted_at IS NULL; get_event_by_id_including_deleted (line 1037) is the one function in the file documented as the exception to that filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:335-401"
      - "crates/buzz-db/src/event.rs:981-1037"
  - statement: "crates/buzz-core/src/event.rs defines StoredEvent (lines 9-51) as 'a Nostr event with relay-assigned metadata': a nostr::Event plus received_at, channel_id (Option<Uuid>, doc comment 'None for global/DM events'), and a private verified flag — the relay's in-process wrapper around one row, not the row's own persisted shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/event.rs:9-51"
  - statement: "migrations/0001_initial_schema.sql defines event_mentions (lines 286-294), primary-keyed (community_id, pubkey_hex, event_id), used for #p-tag fan-out; the migration's own comment (lines 280-284) warns 'The join to events MUST carry the community tuple (e.community_id = m.community_id AND e.id = m.event_id) — bare e.id = m.event_id would leak cross-community mentions.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:280-294"
  - statement: "query_due_reminders (crates/buzz-db/src/event.rs:1417-1436) documents its own predicate as 'not_before <= now, deleted_at IS NULL, delivered_at IS NULL', confirming not_before and delivered_at are used together to schedule and mark delivery of reminder-kind events stored as ordinary rows in this same table, not a separate scheduling table."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:1417-1436"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md carries id architecture-containers-postgres, type: architecture, status: draft — the container-level node for the Postgres instance the events table is physically stored in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "A full walk of launchpad/docs/corpus at origin/launchpad HEAD 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 contains no layers/ subtree and no other data-entity or datastore instance node; the only merged, substantively related content is the architecture/containers/postgres.md container-level node named above."
    entry_class: FACT
    evidence:
      - "find(launchpad/docs/corpus, type=f) -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no layers/ path present at origin/launchpad HEAD 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The events table is Buzz's single most central data-entity: every other domain concept this corpus's data layer will eventually document (channels, threads, reactions, and more) is either one or more event kinds persisted as rows in this same table, or a server-derived projection populated from those rows — so this node's Identity/Attributes/Invariants sections describe the row shape every Nostr-sourced entity in Buzz ultimately shares, distinct from any one entity's own kind-specific meaning, which is out of this node's scope."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:190-235"
      - "crates/buzz-core/src/kind.rs:769-785"
    confidence: 0.75
  - statement: "This batch's overnight corpus-batch-author dispatch brief for Feature #610 directs every layers/data/... document to carry type: layers, overriding the data-entity template's own worked reasoning that a real instance 'most plausibly takes type: implementation' — this node follows that batch-level precedent rather than the template's own suggestion, and discloses the override here per standards/taxonomy.md's 'say so in the node's own scope-and-omissions section' rule."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "overnight corpus-batch-author dispatch brief for Feature #610 (task-1081-events-table batch instructions)"
  - statement: "layers-data-authoritative-data's pull request (launchpad-26/buzz#1872) is open and unmerged as of this session (gh pr view 1872 --repo launchpad-26/buzz -> state: OPEN, mergedAt: null), so it is not a valid relationships target under AGENTS.md step 9 and no edge to it is declared here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1872, read directly via gh pr view"
  - statement: "Issue #1081's definition of done requires this node to define identity/key and semantic ownership, summarize fields by meaning without duplicating generated schema detail, define relationships/lifecycle/invariants, and link authoritative migration/schema and read/write code paths, in addition to the generic one-document, schema-valid, evidence-traceable, non-duplicating, revision-checked, validate.py-clean requirements shared by every corpus task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1081 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Data entity: the `events` table

The single Postgres table holding every Nostr event Buzz persists — the physical
row shape and access surface behind almost every domain concept the corpus's data
layer will eventually document. This node covers the `events` table itself: its
identity, its column shape, the invariants the code enforces about it, and how it
relates to the smaller tables built alongside it. It does not cover what any one
event *kind*'s tags or content mean (that is each kind's own event-kind node's job)
or Postgres's own operational profile (that is a future datastore node's job).

## Identity

A row's identity is the composite primary key `(community_id, created_at, id)` —
not `id` alone. `id` is the 32-byte Nostr event id (`BYTEA`), unique *within* a
community by construction (it is a hash over signed content), but the table's own
key additionally leads with `community_id` and `created_at` because the table is
`PARTITION BY RANGE (created_at)`: Postgres requires every partitioned table's
primary key to include the partition key, and `community_id` leads so every
community-scoped index and query stays partition- and tenant-scoped in the same
stroke. A second `idx_events_community_id (community_id, id, created_at DESC)`
index exists specifically because the primary key's column order can't serve a
bare `WHERE community_id = $ AND id = $` lookup — `created_at` sits between the two
in the key, so that lookup pattern needed its own index to stay index-served rather
than falling back to a partition scan.

`insert_event`'s `ON CONFLICT DO NOTHING` targets exactly this primary key: a
second insert of the same `(community_id, created_at, id)` tuple is a silent
no-op, and the caller learns whether its own call was the one that landed via
`rows_affected() > 0`. This is the identity-level meaning of "duplicate" for this
table — application-layer deduplication resting on the database's own conflict
detection, not a separate existence check before every insert.

**Two other identities exist beside the primary key, and the code treats them as
distinct concepts:**

- **Replaceable (NIP-01) identity** — kinds `0`, `3`, `41` (`KIND_CHANNEL_METADATA`),
  and `10000`-`19999`: the latest event for a `(pubkey, kind)` pair is the live
  one, handled by `replace_addressable_event`, a different write path from
  `insert_event`'s plain conflict-on-primary-key semantics.
- **Parameterized-replaceable (NIP-33) identity** — kinds `30000`-`39999`: the
  latest event for a `(pubkey, kind, d_tag)` triple is the live one, handled by
  `replace_parameterized_event`. `d_tag` is stored in its own column
  specifically to make this coordinate queryable and indexable
  (`idx_events_parameterized`), not left buried in the `tags` JSONB.

A row's primary-key identity therefore answers "is this exactly the same signed
event as one already stored," while the replaceable and parameterized-replaceable
notions answer a different question — "which stored row is currently the live
version of this logical (pubkey, kind[, d_tag]) resource" — and the two must not
be conflated when reading this table's invariants below.

## Attributes and shape

Scalar and structural columns, cited to `migrations/0001_initial_schema.sql` rather
than restated as a second, independently-maintained copy of the schema:

| Column | Meaning not already obvious from its name/type |
|---|---|
| `id`, `pubkey`, `sig` | Raw `BYTEA`, not hex text — the wire-hex encoding NIP-01 describes is a client/JSON-serialization concern; the stored row keeps the decoded bytes. |
| `tags` | `JSONB`, the full Nostr tag array (NIP-01 shape: array-of-arrays, first element the tag name). Not decomposed into columns — `event_mentions` (below) is the one derived exception, for `#p`-tag fan-out specifically. |
| `search_tsv` | Generated/`STORED`, not written by application code — Postgres computes it from `content` on every insert, `NULL` for the fixed privacy-sensitive kind list (see evidence ledger), so those events are unsearchable at the storage level rather than merely filtered post-query. |
| `channel_id` | Nullable `UUID`; `NULL` means a global or DM event, per `StoredEvent`'s own doc comment for the in-process equivalent of this column. |
| `deleted_at` | Nullable `TIMESTAMPTZ`; non-`NULL` means soft-deleted (see Invariants). Never actually removes the row. |
| `d_tag` | Nullable `TEXT`; populated only for kinds that carry a NIP-33 `d` tag, and is the column `idx_events_parameterized` and `replace_parameterized_event` key off, not a generic denormalization of every tag. |
| `not_before`, `delivered_at` | Both nullable `BIGINT` (Unix seconds); together they schedule and mark delivery of reminder-kind events (`KIND_EVENT_REMINDER`) stored as ordinary rows in this table rather than in a separate scheduling table — `query_due_reminders`' own predicate (`not_before <= now, deleted_at IS NULL, delivered_at IS NULL`) is the citable proof. |
| `received_at` | Relay wall-clock receive time, defaulted `NOW()` at insert — distinct from `created_at`, which is the event's own client-signed timestamp and fully attacker-controlled within Nostr's rules. |

`StoredEvent` (`crates/buzz-core/src/event.rs`) is **not** this table's row shape
— it is the relay's in-process wrapper around one `nostr::Event` plus a subset of
this table's columns (`received_at`, `channel_id`) and a `verified` flag that is
never persisted at all. Anyone reading `StoredEvent` as "the events table's
schema" is reading the wrong artifact; it is the boundary between this data-entity
node's job and `buzz-core`'s own in-memory representation.

## Invariants

- **A stored row's `(community_id, created_at, id)` triple is immutable once
  written.** No code path in `crates/buzz-db/src/event.rs` updates `created_at` or
  `id` after insert; `soft_delete_by_coordinate`'s own doc comment leans on this
  directly, reasoning that because "`events.created_at` is immutable per row," a
  deletion's `created_at <=` guard can never be defeated by a row's own timestamp
  changing out from under it.
- **Deletion is soft, never a `DELETE`.** Every deletion path in
  `crates/buzz-db/src/event.rs` (`soft_delete_event`,
  `soft_delete_by_coordinate`, `soft_delete_event_and_update_thread`) is an
  `UPDATE ... SET deleted_at = NOW()`. No function in that file issues a `DELETE
  FROM events`. A "deleted" event therefore still occupies its partition and its
  indexes; readers must apply `deleted_at IS NULL` themselves, which every
  live-row query function in the file already does except the one explicitly
  named exception (`get_event_by_id_including_deleted`).
- **A NIP-33 tombstone cannot erase a version newer than itself.**
  `soft_delete_by_coordinate`'s `created_at <= $deletion_created_at` guard,
  combined with the immutability invariant above, is what makes this hold even
  under a race between a replacement and its own deletion — the function's own
  doc comment states the two possible outcomes (deletion wins, or the replacement
  survives) are both valid Nostr orderings, not a correctness bug either way.
- **AUTH and ephemeral kinds never reach this table at all.**
  `insert_event` rejects `KIND_AUTH` (22242) and any kind in the ephemeral range
  (20000-29999) before the `INSERT` runs, per the module's own header comment —
  this is an ingest-time invariant enforced in Rust, not a table constraint
  Postgres itself checks.
- **Cross-table counters can drift if a caller bypasses the paired helper.**
  `soft_delete_event_and_update_thread` exists specifically because a bare
  `soft_delete_event` call on a thread reply, without the accompanying
  `thread_metadata` counter decrement, would leave `reply_count`/
  `descendant_count` inflated — the same class of invariant root `CLAUDE.md`'s
  "Thread counters" entry warns about generally. This is a cross-entity
  invariant involving `thread_metadata`, named here because it is enforced at
  this table's own deletion call sites, but the counter's own home is
  `thread_metadata`'s eventual data-entity node, not this one.

## Relationships to other entities

- **`event_mentions`** — a derived table keyed `(community_id, pubkey_hex,
  event_id)`, populated for `#p`-tag fan-out. The migration's own comment warns
  that any join back to `events` "MUST carry the community tuple
  (`e.community_id = m.community_id AND e.id = m.event_id`)" — a bare
  `e.id = m.event_id` join would leak mentions across communities, because `id`
  alone is not a safe cross-community join key even though it is
  content-address-unique within one. This is a foreign-key-shaped relationship
  in code (no formal `FOREIGN KEY` constraint declared on `event_id`, checked
  directly against the migration), not yet a corpus `relationships` edge, since
  `event_mentions` has no data-entity node of its own yet.
- **`thread_metadata`** — a separate, already-corpus-documented-by-`CLAUDE.md`
  (not yet by a corpus node) table populated from reply events stored in this
  table; see the cross-entity invariant above. No corpus `relationships` edge
  declared for the same reason.
- **Kind-specific event-kind nodes** (event-kind template, not yet instanced) —
  every row's `kind` column selects which kind-specific wire contract applies to
  its `tags`/`content`. This node deliberately does not enumerate kinds; that is
  each kind's own future `interfaces-events`-typed node's job.
- **`architecture-containers-postgres`** — declared below as `part-of`: this
  table is one structural piece of the Postgres container that node already
  inventories at the container level.
- **`layers-data-authoritative-data`** (issue #1060, PR #1872) — discusses the
  `events` table at a conceptual, cross-cutting level (what "authoritative"
  means for Buzz's data). Not declared as a corpus relationship here because its
  PR is open and unmerged at the revision this node was checked against;
  see the evidence ledger and the plan's OPEN note. This node is the concrete
  data-entity counterpart that document's own scope defers to for schema,
  keys and invariants — the two are complementary once #1872 merges, not
  duplicates.

## Provenance

The `events` table's canonical form **is** the Nostr events themselves — every
row is a signed Nostr event as received, decoded into columns. There is no
separate "authoritative" representation this table derives from; unlike
`thread_metadata` (a pure server-derived projection with no event of its own),
`events` rows are themselves the source of truth NIP-01 describes, merely
persisted relationally instead of held only in memory or on the wire. The one
partial exception is `search_tsv`, a `GENERATED ALWAYS ... STORED` column
Postgres computes from `content` — derived, but derived synchronously by the
database itself at write time, not by a separate asynchronous indexer that could
drift out of sync the way `thread_metadata`'s counters can.

## Storage pointer, not storage description

Postgres, table `events` (partitioned; current partitions and partitioning scheme
are `migrations/0001_initial_schema.sql`'s own concern, not restated here). The
container this table lives inside is documented at
`launchpad/docs/corpus/architecture/containers/postgres.md`
(`architecture-containers-postgres`), linked via this node's own `part-of`
relationship below. No datastore-level node (migration mechanism, connection
pooling, replication) exists yet for Postgres as a whole; once one does, this
node's storage pointer should additionally `references` it rather than restate
its content here.

## Scope and omissions

**This document covers** the `events` table's identity, column-level attribute
shape, the invariants the code enforces about individual rows and about the
table's relationship to `event_mentions`/`thread_metadata`, and where the table is
physically stored.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What any one event kind's `tags`/`content` mean | That kind's own future event-kind (`interfaces-events`) node |
| Postgres's own migration mechanism, connection/pooling profile, replication, partition-maintenance operations | A future Postgres datastore node (none merged yet) |
| `event_mentions` and `thread_metadata` as their own data entities | Future data-entity nodes for those tables (out of this task's scope per issue #1081's "Out of scope" list) |
| The corpus's cross-cutting notion of "authoritative data" | `layers-data-authoritative-data` (issue #1060, PR #1872, unmerged at this node's revision) |
| The evidence-class contract, `confidence`'s meaning, decision-reference citation | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/confidence.md`, `launchpad/docs/corpus/standards/decision-references.md` |

**`type: layers` is a disclosed override, not the data-entity template's own
suggestion** — see the TEAM_KNOWLEDGE evidence entry above. The data-entity
template's own reasoning would point at `type: implementation`; this node
follows this batch's precedent instead.

**No `references` edge to `layers-data-authoritative-data`.** Its PR (#1872) is
open and unmerged at this node's checked revision, so declaring the edge now
would validate in this worktree but hard-fail once this branch is checked
against `origin/launchpad`, per `AGENTS.md`'s node-creation step 9. Add the edge
in a follow-up edit once #1872 merges.

**Expected but not verified when this node was written:**

- **Whether `event_id` in `event_mentions` carries a formal `FOREIGN KEY`
  constraint back to `events` was checked directly against the migration and
  found absent** — the relationship is enforced in application-level query
  discipline (the community-tuple join warning) rather than by the database
  schema itself. Whether a later migration adds the constraint was not checked.
- **The partition-maintenance mechanism** (how new monthly partitions past
  `events_p_future` get created) was not located in this session's reading and
  is left to the future Postgres datastore node.
- **Whether any code path outside `crates/buzz-db/src/event.rs` and
  `crates/buzz-db/src/lib.rs` also writes to this table directly** was not
  exhaustively checked; the functions cited here are the ones this session's
  evidence gathering located, not a claimed complete inventory of every
  call site.
