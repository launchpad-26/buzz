---
id: layers-data-derived-data
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
  - statement: "The `thread_metadata` table carries `reply_count` (direct children) and `descendant_count` (all nesting levels) as `INT NOT NULL DEFAULT 0` columns; neither is present on the underlying Nostr event, which is signed content plus tags."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:512-526"
  - statement: "`insert_thread_metadata` wraps the `thread_metadata` row insert and the parent's `reply_count`/root's `descendant_count` UPDATEs in a single Postgres transaction specifically so a crash between them cannot leave the counters inconsistent with the actual number of reply rows; the doc comment names this invariant \"F9\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:109-117"
      - "crates/buzz-db/src/store/thread.rs:120-244"
  - statement: "`decrement_reply_count` mirrors the increment path and floors both counters at 0 (`GREATEST(reply_count - 1, 0)`, `GREATEST(descendant_count - 1, 0)`), so the derived counters cannot go negative even under an unexpected delete ordering."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:297-331"
  - statement: "Buzz's own contributor guide names this exact case as a required pattern to preserve: \"Thread counters: reply_count and descendant_count are materialized on thread root events. Any code that inserts replies must update these counters — check existing reply handlers for the pattern.\""
    entry_class: FACT
    evidence:
      - "AGENTS.md:182-183"
  - statement: "The `events` table carries `search_tsv TSVECTOR GENERATED ALWAYS AS (...) STORED`, a value Postgres computes and stores from the row's own `content` and `kind` columns at write time; `buzz-search`'s module documentation states this was a deliberate choice so \"every row write *is* the index update — there is no separate indexer, no mpsc queue, no reindex job, no consistency window to reason about.\""
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:197-224"
      - "crates/buzz-search/src/lib.rs:3-10"
  - statement: "`search_tsv` is NULL for a fixed set of privacy-sensitive kinds (gift wraps, event reminders, DM-visibility markers, membership notices) via a `CASE WHEN kind IN (...)` inside the generated-column expression itself, and a NULL tsvector never matches the `@@` operator — the exclusion is enforced at the storage layer, not by a query-time filter that could be forgotten."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:210-224"
  - statement: "Both `thread_metadata` counters and `events.search_tsv` are read-only outputs of the primary event log in the sense that neither can be authored directly by a client: a Nostr event a client signs and submits carries no `reply_count`, `descendant_count`, or `search_tsv` field, so both are values the relay computes on the server side after the fact."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:512-526"
      - "migrations/0001_initial_schema.sql:197-224"
      - "crates/buzz-db/src/store/thread.rs:109-244"
    confidence: 0.8
  - statement: "`architecture-principles-relay-is-source-of-truth` documents that the relay's own event log, not any derived index or cache, is Buzz's authoritative record — derived data of both forms described here is downstream of that source, never a competing copy of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md"
  - statement: "`architecture-flows-event-ingestion` documents the ingestion path along which `thread_metadata` rows and counters are populated as replies arrive."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
relationships:
  - type: references
    target: architecture-principles-relay-is-source-of-truth
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-postgres
---

# Derived data

**Derived data** is any value Buzz computes and stores from the primary Nostr
event log rather than accepting directly from a client — it exists to answer a
question faster or more cheaply than recomputing it from the raw events every
time, and it is never itself the record of truth for what happened.

## Definition

A piece of derived data has two properties that distinguish it from an
ordinary column on a stored event: (1) no signed Nostr event a client submits
carries it directly — a client cannot set `thread_metadata.reply_count` or
`events.search_tsv` the way it sets `content` or `tags` — and (2) its value is
a deterministic function of other data already stored, computed either by the
relay's own write path or by the database engine itself. If a value can be
recomputed byte-for-byte from the events already on record, it is a candidate
for this category; if a client can supply it directly and the relay merely
stores what it was told, it is not.

**What this is not.** Derived data is not a cache in the sense of "may be
evicted and silently miss" — Buzz's two current instances (below) are both
kept continuously consistent with their source, one transactionally and one
by the database engine's own generated-column guarantee, so neither can drift
stale in the way an LRU cache can. It is also not the event log itself:
`architecture-principles-relay-is-source-of-truth` is Buzz's statement that
the relay's own event log is the authoritative record, and derived data is
downstream of that record by definition, never a second copy competing with
it for authority.

## Use cases

A reader reaches for this concept when:

- Adding a new feature that needs an aggregate or computed value read
  frequently but expensive to recompute from raw events on every request
  (a count, a rollup, a search index) — the two patterns below are the
  precedents to follow, not a new one to invent.
- Writing or reviewing code that inserts, deletes, or re-parents an event that
  has derived data attached to it, to check whether the derived value is kept
  in sync in the same transaction as the write that changes its inputs — the
  contributor guide's "Thread counters" gotcha exists precisely because this
  is easy to forget when adding a new reply-handling code path (`AGENTS.md`).
- Deciding whether a new computed value belongs on the database engine's own
  generated-column mechanism or needs application-level incremental
  maintenance — see the comparison below for the deciding factors Buzz's own
  two instances already show.

## Comparison

Buzz has two derivation mechanisms in production, not one, and they trade off
differently:

| | Application-maintained counter | Database-computed generated column |
|---|---|---|
| **Example** | `thread_metadata.reply_count`, `thread_metadata.descendant_count` | `events.search_tsv` |
| **Computed by** | Relay application code (`buzz-db::thread::insert_thread_metadata`), inside the same transaction as the write that changes it | PostgreSQL itself, via `GENERATED ALWAYS AS (...) STORED` |
| **Consistency mechanism** | Explicit transaction wrapping the base write and the derived UPDATE, so a crash between them cannot desynchronize them (doc comment names this "F9") | Structural — the column cannot be written directly and is recomputed by the engine on every row write, so there is no window where it can diverge from its inputs |
| **Update shape** | Incremental (`+1`/`-1` per reply insert/delete, floored at 0) | Full recomputation of the expression on every write to the row |
| **Can drift from source** | Only if a future write path bypasses `insert_thread_metadata`/`decrement_reply_count` and mutates `thread_metadata` some other way — a discipline problem, not a mechanism problem | No — enforced by Postgres; there is no code path that can write the column directly |
| **When Buzz chose it** | When the derived value is an aggregate across many rows (children, descendants) that a single-row expression cannot express | When the derived value is a pure function of that same row's own columns |

## Scope and omissions

**This document covers** what makes a value "derived" in Buzz's data layer,
the two derivation mechanisms currently in use, and when to reach for each.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full list of every column or table Buzz derives from primary events (an exhaustive catalogue) — that is reference-shaped content, not concept-shaped | Not yet filed as its own reference-typed corpus task at this revision |
| The event-ingestion flow that populates `thread_metadata` step by step | `architecture-flows-event-ingestion` |
| Why the relay's own event log, not any derived value, is the authoritative record | `architecture-principles-relay-is-source-of-truth` |
| Where both mechanisms physically live (Postgres, partitioned `events` table, `thread_metadata` table) | `architecture-containers-postgres` |
| Redis-backed ephemeral state (presence, typing indicators, pub/sub fan-out) in `buzz-pubsub` — whether that state fits this same concept or is a distinct one was not investigated for this node | Not yet filed as its own corpus task at this revision |

**Expected but not verified when this node was written:** whether any other
Buzz subsystem (beyond `buzz-db`'s thread counters and `buzz-search`'s
generated column) maintains a third derivation mechanism was not exhaustively
searched; the two forms documented here were sufficient to define the concept
and were the two most directly reachable from this task's own evidence
gathering.
