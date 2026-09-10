---
id: layers-data-authoritative-data
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "docs/multi-tenant-relay.md states the shared store holds three tiers: one canonical message log L (an append-only table keyed by (community_id, created_at, id)), a tenant-scoped relational control plane (channels, channel_members, api_tokens, workflows, audit entries, kept relational because authorization needs synchronous current state), and disposable projections (mentions, thread metadata, reactions, full-text search), each community_id-keyed, rebuildable from L, and stated explicitly as 'never authoritative'."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:76-87"
  - statement: "migrations/0001_initial_schema.sql defines events as a monthly-range-partitioned, append-only table keyed by community_id, id, pubkey, created_at, kind, tags and content -- the canonical message log docs/multi-tenant-relay.md calls L."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-197"
      - "migrations/0001_initial_schema.sql:237-252"
  - statement: "The same migration defines thread_metadata (with reply_count and descendant_count columns), reactions and event_mentions as separate tables keyed off an event's community_id and event_id rather than as columns on events itself; each is populated from event rows rather than carrying any fact events does not already carry."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:512-528"
      - "migrations/0001_initial_schema.sql:539-549"
      - "migrations/0001_initial_schema.sql:286-294"
  - statement: "events.search_tsv is a generated, STORED tsvector column (`TSVECTOR GENERATED ALWAYS AS (...) STORED`) populated from the content column at write time -- its migration comment states this makes it 'a single source of truth -- no sidecar indexer to keep coherent' -- and privacy-sensitive kinds are excluded from it by a CASE expression yielding NULL rather than by omitting the row, so the column itself carries no fact absent from content and kind."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:198-226"
  - statement: "ARCHITECTURE.md describes buzz-db as the Postgres event store crate owning insert_event, query_events and get_event_by_id, and states of buzz-pubsub (the Redis pub/sub crate) explicitly: 'Does NOT: implement the rate limiter. Does NOT store events.'"
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:394"
      - "ARCHITECTURE.md:402"
      - "ARCHITECTURE.md:460"
  - statement: "ARCHITECTURE.md states the relay is the single source of truth, that all reads and writes flow through it, and names persisting events among its core responsibilities alongside fanning out to subscribers, indexing for search, and triggering automation."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:7"
  - statement: "docs/git-on-object-storage.md states a separate, narrower authority claim scoped to git repository storage specifically: the implementation has 'no authoritative per-repo filesystem state,' because every request hydrates an ephemeral working tree from a published manifest and drops it on scope exit."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md:54"
  - statement: "This node's tier-level distinction (which persisted structures inside the shared store are canonical versus rebuildable) does not duplicate architecture-principles-relay-is-source-of-truth's own claim, because that node's stated scope is the relay as a whole logical service being the sole authority for Buzz state relative to clients and other components, and it does not itself enumerate which structures within that state are canonical versus derived."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md"
    confidence: 0.75
  - statement: "crates/buzz-db/src/store/thread.rs's increment_reply_count runs an UPDATE against thread_metadata.reply_count keyed on the parent event's community_id and event_id -- the projection's count is recomputed by code reacting to an insert into events, not written independently of it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:256-291"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's test_reply_ingest_pushes_live_thread_summary integration test asserts reply_count is 1 after a reply event is ingested and 0 again after that reply is removed, verifying end-to-end that the projection tracks the canonical log rather than carrying independently authored state."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:2579"
      - "crates/buzz-test-client/tests/e2e_relay.rs:2644"
      - "crates/buzz-test-client/tests/e2e_relay.rs:2659"
relationships:
  - type: references
    target: architecture-principles-relay-is-source-of-truth
---

# Authoritative data

How Buzz's shared Postgres store separates the data that is a primary record from
the data that only exists to make a primary record queryable.

## Definition

**Authoritative data is the subset of Buzz's persisted state that is the one place
a given fact lives**, as opposed to derived data that exists solely to make some
other, already-authoritative record queryable or fast to query, and that can
always be regenerated from it without losing information. In the shared Postgres
store, that boundary falls along the three tiers `docs/multi-tenant-relay.md`
names: the canonical message log and the tenant-scoped control plane are
authoritative; every "disposable projection" -- mentions, thread metadata,
reactions, full-text search -- is `community_id`-keyed, rebuildable from the
canonical log, and, in that document's own words, "never authoritative."

Authoritative is not a synonym for important or frequently read. A disposable
projection can be read on every page load and still carry no fact of its own: if
every projection table were dropped and rebuilt from the canonical log and the
control plane, no fact about a message, a channel, a membership, a token or a
workflow would be lost -- only the convenience of not recomputing it on demand.

## Comparison

| Tier | Authoritative? | Example structures | Why |
|---|---|---|---|
| Canonical message log | Yes | `events` -- signed Nostr events, append-only, partitioned by month, `ON CONFLICT (community_id, created_at, id) DO NOTHING` | Each row is the one place a message's existence, author, kind, tags and content live. Nothing else in the store can regenerate a signed event's content if this row is lost. |
| Tenant-scoped control plane | Yes | `channels`, `channel_members`, `api_tokens`, `workflows`, audit entries | ACID-managed operational state that authorization needs synchronous current answers about (is this pubkey a member, is this token valid). Not itself derivable from the event log. |
| Disposable projections | No -- derived, rebuildable | `thread_metadata` (`reply_count`, `descendant_count`), `reactions`, `event_mentions`, `events.search_tsv` | Each is keyed off event ids (or, for `search_tsv`, generated from the same row's `content` at write time) and populated from event rows. Per `docs/multi-tenant-relay.md`, projections are "rebuildable from L, never authoritative." |

`events.search_tsv` sits inside the `events` row itself rather than in a
separate table, but it is still a projection in this sense: it is generated
from `content`, carries no fact `content` and `kind` do not already carry, and
`docs/multi-tenant-relay.md` groups full-text search with the other disposable
projections rather than with the canonical log.

## Use cases

**Deciding what a new persisted structure needs.** When a change adds new
server-side state, this distinction is the first question to answer: can this
be recomputed from the canonical log plus the control plane? If yes, it is a
projection -- it does not need independent durability guarantees, a bug that
corrupts it is recoverable by replaying events, and it can be rebuilt rather
than restored from backup. If no -- if it captures a fact no other row
records -- it must live in the canonical log or the control plane and be
treated as a primary record from day one.

**Reasoning about consistency bugs.** If `thread_metadata.reply_count` for a
root event disagrees with a direct count of replies in `events`, the bug is in
the code that updates the counter on insert, never in `events` itself --
`events` is authoritative by definition, so it is never the side a
projection-consistency bug is attributed to. `increment_reply_count`
(`crates/buzz-db/src/store/thread.rs:256-291`) is the implementation that keeps the
projection in step, and `test_reply_ingest_pushes_live_thread_summary`
(`crates/buzz-test-client/tests/e2e_relay.rs:2579`) is the verification that
it does: it asserts `reply_count` goes from 0 to 1 when a reply is ingested
and back to 0 when that reply is removed, end to end.

**Reasoning about failure and restore.** Losing a disposable projection is a
rebuild job scoped to how long recomputing it takes. Losing a row in the
canonical log or the control plane is data loss with no recomputation path.
This is the distinction a backup or disaster-recovery procedure needs before
it can decide what has to be backed up at all.

## Scope and omissions

**This node covers** the boundary between authoritative and derived data
within Buzz's shared Postgres store, at the granularity of the three tiers
`docs/multi-tenant-relay.md` names, with concrete current-schema examples of
each.

**Boundaries and non-goals -- what this must not be confused with:**

- It does not restate or extend `architecture-principles-relay-is-source-of-truth`'s
  claim that the relay, as a whole logical service, is the sole authority for
  Buzz state relative to clients and other workspace components. That is a
  coarser-grained claim (the relay versus everything outside it); this node's
  subject is the finer-grained question of which persisted structures *inside*
  the relay's own store are canonical versus derived. See that node via the
  `references` relationship above rather than a restatement here.
- It does not cover the git-on-object-storage manifest pointer's own narrower
  claim that the git implementation has "no authoritative per-repo filesystem
  state" (`docs/git-on-object-storage.md:54`) -- a separate invariant about git
  repository storage specifically, out of scope here.
- It does not define or prescribe a backup or disaster-recovery procedure. It
  only establishes the distinction such a procedure would need to reason from.
- It does not enumerate every table in the schema. The Comparison table above
  is illustrative -- one or two examples per tier -- not exhaustive.

**Expected but not verified.** Whether every table added to the schema since
this node's recorded revision has been classified into one of these three
tiers was not audited row by row; a later migration may introduce a table
these examples do not cover.
