---
id: layers-data-transaction-boundaries
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
  - statement: "node.schema.json's type enum has thirteen members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and describes them as naming 'the corpus surface this node documents'; standards/taxonomy.md separately confirms neither node.schema.json nor schema/README.md defines what each individual value means beyond that one shared description. This node documents crates/buzz-db's write-transaction machinery -- the data-access layer -- so type: layers is chosen as the closest-fitting surface, overriding the templates/reference.md template's own worked example (type: governance, chosen there because that node documents the corpus's own authoring rules, not because reference-shaped nodes in general use governance). Which enum value is 'closest-fitting' is a judgment call the cited schema/taxonomy files do not make for this node themselves -- they establish that the thirteen values exist and are undefined beyond one shared description, not that layers is the right pick for write-transaction machinery specifically."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "launchpad/docs/corpus/templates/reference.md"
    confidence: 0.7
  - statement: "crates/buzz-db/src/lib.rs's connect_pool registers an after_connect hook that runs SHOW transaction_isolation on every new connection and fails the connection attempt with sqlx::Error::Configuration if the result is not exactly \"read committed\", so every connection the writer pool hands out already carries this session-level guarantee before any transaction on it begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "migrations/0029_community_deletion.sql defines community_write_allowed and assert_community_write_allowed, both of which open with `IF current_setting('transaction_isolation') <> 'read committed' THEN RAISE EXCEPTION 'community writes require READ COMMITTED isolation' USING ERRCODE = 'invalid_transaction_state'; END IF;` -- a second, database-level enforcement of the same invariant the connection-pool hook asserts at the session level, this time per write statement rather than per connection."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "migrations/0029_community_deletion.sql's enforce_community_write_fence trigger function calls assert_community_write_allowed on the relevant community_id(s) for every INSERT, UPDATE and DELETE, and the same file attaches that trigger via attach_community_write_fence to 30 named tables, including events, channels, channel_members, thread_metadata, relay_members, relay_invites, reactions, users and workflows -- so the READ COMMITTED requirement is enforced by a row-level trigger on essentially every community-scoped table, not merely documented as a convention application code is expected to follow."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-db/src/lib.rs's proved_reader method opens the one documented exception to the READ COMMITTED default: a read-only replica request transaction via sqlx::Transaction::begin with the literal statement \"BEGIN ISOLATION LEVEL REPEATABLE READ, READ ONLY\", whose doc comment states REPEATABLE READ is chosen because it is 'the strongest isolation a hot standby supports' and READ ONLY 'documents intent and rejects accidental writes'; this transaction never reaches the write-fence trigger above because it commits no writes."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/event.rs's soft_delete_event_and_update_thread opens one sqlx transaction via pool.begin(), issues an UPDATE events SET deleted_at = NOW() ... followed conditionally by UPDATE thread_metadata statements decrementing reply_count and descendant_count, and commits all of them together with tx.commit(); its own doc comment states this exists so 'a crash between them cannot leave counters permanently inflated.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs"
  - statement: "crates/buzz-db/src/thread.rs's insert_thread_metadata wraps its INSERT INTO thread_metadata and the parent/root reply_count and descendant_count UPDATE statements (plus a stub-row INSERT for a not-yet-materialized parent) in one pool.begin()/tx.commit() transaction, using ON CONFLICT DO NOTHING and result.rows_affected() to skip the counter bumps on a duplicate insert; its doc comment names this requirement 'F9.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/thread.rs"
  - statement: "crates/buzz-db/src/lib.rs's insert_event_with_serving_write_guard opens one transaction covering a deletion-guard check (guard_transaction_with_serving_lease) and the event insert (event::insert_event_with_thread_metadata_tx), commits it, and only afterward -- outside that transaction, on the plain pool -- calls insert_mentions, logging a warning (tracing::warn!) on failure rather than propagating an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "insert_event_with_serving_write_guard carries no doc comment of its own explaining why mention insertion sits outside the transaction. Reading the shape of the code -- commit first, then a separately-pooled call whose only failure handling is a log line -- mention rows read as a best-effort side effect the author chose not to make transactional, rather than something simply forgotten; but this is an inference from the code's structure, not a stated intent the codebase asserts anywhere."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/lib.rs"
    confidence: 0.6
  - statement: "crates/buzz-db/src/lib.rs's replace_addressable_event and replace_parameterized_event each open one transaction, immediately execute SELECT pg_advisory_xact_lock($1) with a lock key derived from event_replacement_lock_key(community_id, kind, pubkey, discriminator), then read the current newest live row and conditionally replace it, all before commit; their comments state the advisory lock is 'transaction-scoped -- released on commit/rollback' and serializes 'all writers for the same (kind, pubkey, channel_id) tuple' (or, for replace_parameterized_event, the same (kind, pubkey, d_tag) tuple)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/lib.rs's publish_nip43_membership_locked opens one transaction, takes the same event_replacement_lock_key-derived pg_advisory_xact_lock before reading relay_members rows and building/writing the NIP-43 snapshot event, and its doc comment states this 'prevents the stale-snapshot race where a concurrent publication reads older state and overwrites a newer snapshot by arrival order' -- the identical read-build-write-under-lock shape as the two replace_* functions, applied to a relay-authored snapshot rather than a user-submitted event."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/channel.rs defines a CHANNEL_MEMBERSHIP_LOCK_NAMESPACE advisory-lock key and an acquire_channel_membership_lock helper whose doc comment requires it be 'the first statement in the transaction that then reads roles/owner counts and writes membership'; both add_member and remove_member call it immediately after pool.begin(), and the const's own comment explains an advisory key was chosen over SELECT ... FOR UPDATE on the channel row because 'membership is its own contention domain and must not serialize against unrelated channel metadata writers.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "crates/buzz-db/src/relay_members.rs's transfer_ownership opens one transaction, takes SELECT pg_advisory_xact_lock($1) keyed on the transferee pubkey, then SELECT pubkey FROM relay_members WHERE ... role = 'owner' FOR UPDATE to lock and read the current owner row(s), and calls tx.rollback() explicitly on each business-logic failure branch (NoOwner, OwnerConflict, AlreadyOwner, LimitReached) rather than relying on drop -- combining an advisory lock (serializing on the transferee) with a row lock (serializing on the current owner) inside the same transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "crates/buzz-db/src/relay_invite.rs's module doc states 'claim_relay_invite executes the full redemption in one PostgreSQL transaction: SELECT FOR UPDATE on the invite row, membership insert, join-policy evidence insert, and use_count increment all commit together,' and the function itself opens one transaction, runs a SELECT ... FOR UPDATE on the relay_invites row scoped by (community, token_hash), then performs the remaining inserts/updates before commit."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_invite.rs"
  - statement: "crates/buzz-db/src/push.rs's enqueue_wakes opens one transaction and locks every distinct requested (author, installation_id) push_leases row in one SELECT ... FOR UPDATE statement, sorted and deduplicated first so the lock is acquired in one deterministic (author, installation_id) order; its doc comment states this ordering exists so that 'concurrent batches and replace_active_lease (single-row lock) acquire in a consistent order,' and names the requirement 'T2b.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/push.rs"
  - statement: "crates/buzz-db/src/deletion.rs's approve method (inventoried to approved stage transition) opens one transaction and its first statement is SELECT community_id, inventory_digest, inventory_manifest FROM community_deletion_requests WHERE id = $1 AND stage = 'inventoried' AND blocked_at IS NULL FOR UPDATE -- locking the single request row for the duration of the stage-transition transaction; other deletion.rs stage-transition methods (begin_quiescing and others, grepped at the recorded revision) follow the same FOR UPDATE-row-first shape, and separate methods take SELECT pg_advisory_xact_lock(community_deletion_lock_key($1)) (exclusive) or pg_advisory_xact_lock_shared(...) (shared) to coordinate the whole deletion lifecycle against concurrent schema migration and against other deletion-pipeline readers."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "Grepping crates/buzz-db/src for FOR UPDATE ... SKIP LOCKED at the recorded revision finds it used for queue-style dequeue in crates/buzz-db/src/push.rs (push_match_queue, push_wake_outbox) and crates/buzz-db/src/deletion.rs (the deletion request queue), distinct from the plain FOR UPDATE used elsewhere in this document's structured entries for single-row or small-set locking where blocking (not skipping) concurrent claimants is the intended behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/push.rs"
      - "crates/buzz-db/src/deletion.rs"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md (id architecture-containers-postgres, merged and status: draft on origin/launchpad) states in its own words that it 'does not restate the schema's table-by-table contents or the migration runner's full transaction/locking proof -- read the files above for that; this node exists to name the container's boundary and its neighbors, not to duplicate their detail,' naming exactly the gap this node fills for write-transaction boundaries specifically."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "Issue #1101's Definition of Done requires that the document define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts/implementation/verification without duplicating their canonical content, and use examples only to clarify -- not to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1101 definition of done"
  - statement: "An earlier batch of this same corpus-authoring effort produced launchpad/docs/corpus/layers/data/consistency-model.md (id presumed layers-data-consistency-model, issue #1061) on an unmerged branch/PR (#1872) covering LWW and replica-fence read consistency at a higher level than this node's Postgres BEGIN/COMMIT-statement scope; that document does not exist on origin/launchpad at this node's recorded revision, so no relationships entry can target it, and it is referenced only in this node's prose boundary section, not linked."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch context for this overnight corpus-authoring run (Feature #610), naming issue #1061 and PR #1872"
relationships:
  - type: references
    target: architecture-containers-postgres
---

# Postgres transaction boundaries in buzz-db

**A transaction boundary, in this document, is the span between one `pool.begin()`
call and its matching `tx.commit()` (or `tx.rollback()`, explicit or via drop) in
`crates/buzz-db`** -- the set of SQL statements PostgreSQL either applies together or
not at all, and, where a lock is taken inside that span, the set of statements that
lock serializes against concurrent transactions. This document catalogues where
`buzz-db` draws that boundary for real write paths, which locking primitive each one
uses inside it, and the one isolation-level invariant every writer transaction is
built on.

## Reference description

`buzz-db` is Buzz's Postgres data-access layer (`crates/buzz-db/Cargo.toml`:
"Postgres event store and data access layer for Buzz"). Every multi-statement write
that must succeed or fail as one unit goes through `sqlx::Transaction<'_, Postgres>`,
obtained from `PgPool::begin()`. This document is a reference catalogue of that
mechanism as it is actually used in the codebase today: the writer pool's isolation
guarantee, the locking primitives used inside a transaction to serialize concurrent
writers, and a representative set of the write paths that combine multiple
statements into one atomic unit. It is linked from, and does not restate,
`architecture-containers-postgres` (the Postgres container's existence and one-line
responsibility) and does not restate `layers-data-consistency-model` (#1061, not yet
merged) -- the read-side snapshot and LWW-replica-fence consistency story.

## The isolation-level invariant every writer transaction sits on

Every writer-pool connection is asserted to run under **`READ COMMITTED`** isolation
before it is ever handed out, and every write to a community-scoped table is
re-asserted against the same requirement at write time:

1. **Connection-level, once per connection.** `Db::connect_pool`'s `after_connect`
   hook runs `SHOW transaction_isolation` on every new connection and fails the
   connection attempt outright if the answer is not `"read committed"`.
2. **Statement-level, on (almost) every write.** `migrations/0029_community_deletion.sql`
   defines `assert_community_write_allowed`, which raises
   `community writes require READ COMMITTED isolation` (`ERRCODE =
   invalid_transaction_state`) if `current_setting('transaction_isolation')` is
   anything else, and an `enforce_community_write_fence` trigger calls it on every
   `INSERT`/`UPDATE`/`DELETE` against 30 attached tables (`events`, `channels`,
   `channel_members`, `thread_metadata`, `relay_members`, `relay_invites`,
   `reactions`, `users`, `workflows`, and more).

The two checks are redundant by design: the first stops a misconfigured connection
before it can run any transaction at all; the second stops a transaction that
somehow overrode its own isolation level (e.g. via an explicit `SET TRANSACTION
ISOLATION LEVEL`) from writing to a fenced table regardless. **The one documented
exception** is `Db::proved_reader`, which opens a read-only
`BEGIN ISOLATION LEVEL REPEATABLE READ, READ ONLY` transaction for replica-routed
reads -- it never reaches the write-fence trigger because it commits no writes, and
its own snapshot-consistency reasoning belongs to `layers-data-consistency-model`
(#1061), not this document.

## Locking primitives used inside a transaction boundary

| Primitive | Scope / release | Used for |
|---|---|---|
| `pg_advisory_xact_lock(key)` (exclusive, transaction-scoped) | Auto-released on commit or rollback; key is an arbitrary `bigint`, not tied to a specific row | Serializing writers that read one thing and write a *different* row than the one they read (LWW event replacement, channel membership check-then-write, NIP-43 snapshot publish, deletion-lifecycle coordination) -- cases where `SELECT ... FOR UPDATE` on a single row cannot express the contention domain |
| `pg_advisory_xact_lock_shared(key)` | Same release rule; shared, so concurrent holders on the same key do not block each other | Deletion-pipeline readers that must not block each other but must exclude the exclusive destructive-phase lock |
| `SELECT ... FOR UPDATE` | Row lock, held until the transaction ends | Locking a specific already-identified row (an invite, a relay-owner row, a deletion-request row, a set of push-lease rows) before reading and conditionally mutating it |
| `SELECT ... FOR UPDATE ... SKIP LOCKED` | Row lock, non-blocking on already-locked rows | Queue-style dequeue (`push_match_queue`, `push_wake_outbox`, the deletion request queue) where a concurrent worker already claiming a row should be skipped, not waited on |

The choice between an advisory lock and `FOR UPDATE` is deliberate, not
interchangeable: `channel.rs`'s `CHANNEL_MEMBERSHIP_LOCK_NAMESPACE` comment states
plainly that an advisory key was chosen over row-locking the channel row because
"membership is its own contention domain and must not serialize against unrelated
channel metadata writers." `relay_members::transfer_ownership` uses *both* inside one
transaction -- an advisory lock on the transferee (a value, not a row) and `FOR
UPDATE` on the current owner row(s) (an actual row) -- because the two checks
protect different resources.

## Representative write-transaction boundaries

Not every `pool.begin()` call site in `crates/buzz-db/src` is listed here (test
fixtures and lock-holder test helpers are excluded); this table covers production
write paths chosen to show the range of shapes the boundary takes.

| Function | What one transaction covers | Locking inside it | Notes |
|---|---|---|---|
| `event::soft_delete_event_and_update_thread` | Soft-delete one `events` row + decrement `thread_metadata.reply_count`/`descendant_count` on its parent and root | None (statement ordering only) | "a crash between them cannot leave counters permanently inflated" (function doc) |
| `thread::insert_thread_metadata` | Insert one `thread_metadata` row, a stub row for a not-yet-materialized parent, and the parent/root counter bumps | None; `ON CONFLICT DO NOTHING` + `rows_affected()` guards against double-counting a duplicate insert | Tagged requirement "F9" in the function doc |
| `Db::insert_event_with_serving_write_guard` | A deletion-guard check (`guard_transaction_with_serving_lease`) + the event insert + its thread metadata | None beyond the guard check itself | Mention-row insertion (`insert_mentions`) runs **after** `tx.commit()`, on the plain pool, best-effort (logged, not propagated) -- outside this boundary; no doc comment states this was deliberate, but the shape (commit first, then a separately-pooled call) reads that way |
| `Db::replace_addressable_event` | Read the newest live row for `(community, kind, pubkey, channel_id)`, then insert-or-replace it (NIP-16 replaceable kinds, NIP-29 discovery state) | `pg_advisory_xact_lock` on a key derived from the four-part natural key | Advisory lock is the transaction's first statement |
| `Db::replace_parameterized_event` | Same shape as above, keyed on `(community, kind, pubkey, d_tag)` instead of `channel_id` | Same lock primitive, different key derivation | Serves user-submitted NIP-33 kinds |
| `Db::publish_nip43_membership_locked` | Read current `relay_members` rows, build, and replace the prior kind:39002 snapshot event | Same `pg_advisory_xact_lock` key derivation as the two `replace_*` functions | Prevents a stale-snapshot race from a concurrent publication |
| `channel::add_member` / `channel::remove_member` | Role/owner-count check-then-write against `channel_members` | `pg_advisory_xact_lock` on a per-channel membership namespace key, taken first | Chosen over row-locking the channel because membership is a separate contention domain |
| `relay_members::transfer_ownership` | Read/lock current owner(s), enforce the transferee's ownership limit, upsert new owner, demote prior owners | `pg_advisory_xact_lock` on the transferee + `SELECT ... FOR UPDATE` on current owner row(s) | Explicit `tx.rollback()` on each business-logic failure branch rather than relying on drop |
| `relay_invite::claim_relay_invite` | Lock the invite row, insert membership, insert join-policy evidence, increment `use_count` | `SELECT ... FOR UPDATE` on the invite row, scoped by `(community, token_hash)` | Module doc: "all commit together" |
| `push::enqueue_wakes` | Lock and read every distinct requested `push_leases` row, then enqueue matching wake jobs | `SELECT ... FOR UPDATE`, rows locked in deterministic `(author, installation_id)` order | Ordering exists so concurrent batches acquire locks consistently and avoid deadlock; tagged "T2b" |
| `deletion::CommunityDeletionStore::approve` | Move one deletion request from `inventoried` to `approved` | `SELECT ... FOR UPDATE` on the request row (`stage = 'inventoried' AND blocked_at IS NULL`) | One of several `deletion.rs` stage-transition methods sharing this row-lock-first shape |

## Boundary

This node does not describe:

- **Read-side snapshot consistency, LWW conflict resolution, or the replica-fence
  proof** (`Db::proved_reader`'s `REPEATABLE READ, READ ONLY` transaction and its
  heartbeat/token mechanism) -- that is `layers-data-consistency-model`'s subject
  (#1061), referenced above but not restated, since that node is not yet merged and
  no relationship can target it today.
- **The Postgres container's existence, technology choice, or deployment topology**
  -- that is `architecture-containers-postgres`'s job; this node takes "Postgres
  exists and buzz-db is its data-access layer" as given and goes one level deeper,
  into the transaction/locking mechanics that container document explicitly says it
  does not restate.
- **The schema itself** (table-by-table column contents, migration ordering, the
  `SCHEMA_DESTRUCTION_LOCK_KEY` migration-vs-deletion exclusion lock) -- a datastore-
  or schema-shaped document's job, not this cross-cutting concern's.
- **Redis or object-storage transaction semantics.** `crates/buzz-db` is a Postgres
  crate; this node is scoped to it, per the issue's own objective sentence.
- **An exhaustive inventory of every `pool.begin()` call site.** The table above is
  representative, chosen to cover the range of locking shapes in use, not a complete
  enumeration; test-only fixtures and lock-holder test helpers are excluded.

## Relationships

- **references**: `architecture-containers-postgres` -- the Postgres container
  document this node goes one level deeper than, per that node's own stated
  boundary ("does not restate ... the migration runner's full transaction/locking
  proof"). `references`' directionality per `relationships.schema.json` is "source
  cites target as supporting context; no ownership or currency dependency implied,"
  which fits: this node stays accurate even if the container document's framing
  later changes.
- **Not declared**: any edge to `layers-data-consistency-model` (#1061) -- that node
  does not exist on `origin/launchpad` at this node's recorded revision (only on
  unmerged PR #1872), and a `relationships[].target` naming an id no loaded node
  carries is a hard validation error. It is named in prose only, per `AGENTS.md`'s
  rule to check against the merge-target branch, not the author's own worktree.

## Scope and omissions

**This node covers** the write-transaction boundary mechanism in `crates/buzz-db`:
the `sqlx::Transaction`/`pool.begin()`/`tx.commit()` primitive itself, the
`READ COMMITTED` isolation invariant enforced at both the connection-pool and
database-trigger level, the four locking primitives used inside a transaction
boundary and when each is chosen, and a representative catalogue of production
write paths showing the range of shapes those boundaries take.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Read-side snapshot consistency, LWW resolution, replica-fence proof | `layers-data-consistency-model` (#1061, unmerged) |
| The Postgres container's existence, technology, deployment topology | `architecture-containers-postgres` |
| Full schema/migration inventory | a datastore- or schema-shaped corpus document, not yet authored at this node's recorded revision |
| Redis and object-storage transaction/consistency semantics | out of scope for this Postgres-specific node |

**Expected but not verified when this node was written:**

- **No exhaustive count of every `pool.begin()` call site was taken.** The
  structured-entries table above is a representative sample across the locking
  shapes found by grepping `crates/buzz-db/src` for `.begin()`, `sqlx::Transaction`,
  `FOR UPDATE`, and `pg_advisory_xact_lock`; a full enumeration (including every
  `deletion.rs` stage-transition method, every test-only transaction fixture, and
  every call site in `crates/buzz-db/src/lib.rs` beyond the ones cited) was not
  produced.
- **Whether `squareup/block-coder-tf-stacks` or `squareup/sprout-oss` (private
  repositories not opened by this task) configure a Postgres deployment whose
  actual runtime `default_transaction_isolation` could differ from what the
  application-level and trigger-level checks assert** was not checked -- this node
  documents what the application and schema require and enforce, not independent
  confirmation of the underlying Postgres instance's configuration.
- **Whether every one of the 30 tables `attach_community_write_fence` covers is
  still the complete and current list** was read once, at the recorded revision, by
  grepping `migrations/0029_community_deletion.sql`; a later migration adding or
  removing a table from that list would not be reflected here without a re-check.
