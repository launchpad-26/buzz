---
id: layers-protocol-parameterized-replaceable-event
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "buzz-core defines the parameterized-replaceable range as the constants PARAM_REPLACEABLE_KIND_MIN = 30000 and PARAM_REPLACEABLE_KIND_MAX = 39999, and is_parameterized_replaceable is a pure inclusive range check over those two bounds with no tag, content or registry lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The doc comment on is_parameterized_replaceable states that these events are keyed by (pubkey, kind, d_tag) and that the latest created_at wins."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The sibling class is defined in the same file as is_replaceable, matching kinds 0, 3, KIND_CHANNEL_METADATA and 10000-19999, and its doc comment states that parameterized-replaceable kinds use a different replacement key that includes the d-tag and are handled separately via replace_parameterized_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "A unit test named replaceable_and_parameterized_are_disjoint asserts that no kind satisfies both is_replaceable and is_parameterized_replaceable, and a second test named parameterized_replaceable_range asserts the boundaries directly: 29999 false, 30000 true, 39999 true, 40000 false."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "extract_d_tag returns None for any kind outside the parameterized-replaceable range, and for a kind inside it returns the first d tag's second element, defaulting to the empty string when no d tag with a value is present."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "The relay's ingest path tests is_replaceable first and is_parameterized_replaceable second, and on the parameterized branch extracts the d tag, rejects it with 'invalid: d tag too long' when it exceeds D_TAG_MAX_LEN, and otherwise calls replace_parameterized_event with the community, event, d tag and channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "D_TAG_MAX_LEN is 1024 bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Every SQL predicate in the parameterized replacement path scopes on community_id in addition to kind, pubkey and d_tag, so the coordinate is community-scoped inside the store even though the protocol-level key is (pubkey, kind, d_tag)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "channel_id is deliberately excluded from the parameterized replacement key; the doc comment on soft_delete_by_coordinate states that NIP-33 replacement is global per the spec and that channel_id is stored for query scoping, not identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "The live head at a coordinate is selected by SELECT created_at, id FROM events WHERE community_id, kind, pubkey and d_tag match AND deleted_at IS NULL ORDER BY created_at DESC, id ASC LIMIT 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "The dominance comparison rejects an incoming event when created_at < accepted_ts, or when created_at == accepted_ts and the incoming 32-byte event id compares byte-lexicographically greater than or equal to the accepted id, so on a same-second tie the numerically lower event id wins."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "ParameterizedReplaceStatus enumerates exactly six outcomes -- Inserted, Duplicate, Superseded, RevisionMissing, RevisionMismatch and ReplayOnlyMiss -- and only Inserted causes replace_parameterized_event to commit its transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "ParameterizedReplacePrecondition offers three structural preconditions on a write -- Unconditional, ExpectedRevision holding a validated event id the live head must match, and ExactReplayOnly which performs no mutation and returns ReplayOnlyMiss unless the event is already the accepted one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "Concurrent writers at one coordinate are serialized by pg_advisory_xact_lock on a transaction-scoped key derived by FNV-1a hashing of the community UUID, the kind's little-endian bytes, the pubkey and the d tag, and the function's own doc comment states that hash collisions only add serialization because the SQL predicates still determine which rows are read or changed."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "Supersession is by default a soft delete -- UPDATE events SET deleted_at = NOW() over the live rows at the coordinate -- with a physical DELETE used only when the event matches one of two narrow opt-in shapes recognised in the same function."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "The insert that follows supersession uses ON CONFLICT DO NOTHING, and a zero-row result rolls the savepoint back and reports Duplicate, so a replayed event id cannot destroy the previously live head."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "idx_events_parameterized is a non-unique partial index declared as CREATE INDEX ... ON events (community_id, kind, pubkey, d_tag, created_at DESC, id) WHERE d_tag IS NOT NULL AND deleted_at IS NULL, in both the desired-state schema and migration 0001."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "migrations/0001_initial_schema.sql"
  - statement: "No UNIQUE index or UNIQUE constraint over the parameterized coordinate exists on the events table anywhere in the desired-state schema or the migrations."
    entry_class: FACT
    evidence:
      - "grep_r('CREATE UNIQUE INDEX ... ON events | UNIQUE (... d_tag)', path='schema/schema.sql;migrations/*.sql') -> 0 matches on events; the only coordinate-shaped uniqueness found is the PRIMARY KEY (community_id, kind, pubkey, d_tag) of the separate parameterized_event_watermarks table"
      - "schema/schema.sql"
  - statement: "The events table is declared PARTITION BY RANGE (created_at) with PRIMARY KEY (community_id, created_at, id)."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "Because PostgreSQL requires a partitioned table's unique constraint to include every partition-key column, a UNIQUE constraint over (community_id, kind, pubkey, d_tag) alone is not expressible on this table without also carrying created_at, which would defeat its purpose -- so the absence of database-enforced coordinate uniqueness is a structural consequence, not an oversight."
    entry_class: INFERENCE
    evidence:
      - "schema/schema.sql"
    confidence: 0.75
  - statement: "When the store reports that the event did not become the live head, the relay still answers accepted: true with the message 'duplicate:'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "buzz-cli converts an accepted response whose message equals 'duplicate' or begins with 'duplicate:' into CliError::Conflict, with an inline comment in notes.rs stating this exists so a NIP-33 write dominated by a newer or same-second head is not printed as a success."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs"
      - "crates/buzz-cli/src/commands/notes.rs"
  - statement: "CliError::Conflict maps to process exit code 5 and to the label 'conflict'."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "A Postgres-backed test named concurrent_parameterized_replacement_keeps_deterministic_head races two events sharing a coordinate and a created_at, asserts the surviving live head is whichever has the lower event id, and further asserts that replaying the winner and submitting an older event both fail to insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "That test is marked #[ignore = \"requires Postgres\"], and CI reaches it through a nextest filter of package(buzz-db) and test(/tests::(parameterized_|concurrent_parameterized_)/) rather than through a default cargo test run."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
      - ".github/workflows/ci.yml"
  - statement: "A NIP-09 a-tag deletion against the same coordinate is handled by soft_delete_by_coordinate, whose predicate adds created_at <= the deletion event's own created_at so a delayed tombstone cannot erase a version newer than itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "No upstream numbered NIP specification text is present in this repository; docs/nips holds only Buzz's own two-letter NIPs."
    entry_class: FACT
    evidence:
      - "ls_dir('docs/nips/') -> 22 .md files, all two-letter Buzz NIPs (NIP-AA, NIP-AE, NIP-AP, NIP-RS, ...); 0 files matching ^NIP-[0-9]"
  - statement: "Issue #1164 covers plain replaceable events as a separate corpus node, so this node disambiguates against that class rather than documenting it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1164, relayed via the Feature #609 batch dispatch"
relationships:
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-db
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: layers-data-postgres-events-table
  - type: references
    target: layers-data-postgres-indexes
  - type: references
    target: capabilities-channels-channel-metadata
---

# Parameterized-replaceable events

A **parameterized-replaceable event** is a signed Nostr event whose kind falls in
the range **30000–39999**, and which is addressed not by its own event id but by
the **coordinate `(pubkey, kind, d_tag)`** — so that publishing a second event at
the same coordinate supersedes the first, leaving exactly one live event there.

The event id still exists and is still the thing that gets signed. What changes is
what the relay treats as the *identity of the resource*: two events with different
ids but the same coordinate are two **versions of one thing**, and only the winning
version stays queryable.

## Definition, and what this is not

`is_parameterized_replaceable` is the whole membership test, and it is a pure
inclusive range check between `PARAM_REPLACEABLE_KIND_MIN` (30000) and
`PARAM_REPLACEABLE_KIND_MAX` (39999) — nothing about the event's tags, content or
registration decides it. Its own doc comment in `crates/buzz-core/src/kind.rs`
states the key: *keyed by `(pubkey, kind, d_tag)` — the latest `created_at` wins.*

**Not the same as a plain replaceable event.** The two classes share the word
"replaceable" and nothing else about their key:

| | Plain replaceable | Parameterized-replaceable |
|---|---|---|
| Kinds | 0, 3, `KIND_CHANNEL_METADATA`, 10000–19999 | 30000–39999 |
| Predicate | `is_replaceable` | `is_parameterized_replaceable` |
| Key | `(pubkey, kind)` — no `d` tag participates | `(pubkey, kind, d_tag)` |
| Consequence | one live event per author per kind | **many** live events per author per kind, one per distinct `d` value |
| Store entry point | `replace_addressable_event` | `replace_parameterized_event` |

The classes are **disjoint by construction**, and `kind.rs` carries a unit test
(`replaceable_and_parameterized_are_disjoint`) asserting no kind satisfies both,
plus a boundary test pinning 29999 out, 30000 in, 39999 in, 40000 out.

Plain replaceable semantics are a separate corpus node (#1164) and are not
documented here beyond that contrast.

**Not the same as a non-replaceable event.** Kinds outside both ranges are
inserted and deduplicated by event id alone; they have no coordinate and no
supersession.

**`d` is not optional in effect, only in form.** `extract_d_tag` returns the first
`d` tag's value for an in-range kind, and **the empty string** when no `d` tag with
a value is present. So an event in the range without a `d` tag does not escape the
mechanism — it lands on the coordinate whose `d` component is `""`, alongside every
other `d`-less event of that kind from that author.

## The coordinate as the store actually keys it

The protocol-level key is `(pubkey, kind, d_tag)`. Inside `buzz-db`, every
predicate additionally scopes on `community_id`, because one relay serves many
communities — so the effective row key is
`(community_id, kind, pubkey, d_tag)`.

`channel_id` is **deliberately not** part of the key. The doc comment on
`soft_delete_by_coordinate` states the reasoning directly: NIP-33 replacement is
global per the spec, and `channel_id` is stored for query scoping, not identity. A
parameterized-replaceable event published in one channel therefore replaces the
same author's same-`d` event of the same kind published in another.

Where the `d_tag` column and its index physically live is the
`layers-data-postgres-events-table` and `layers-data-postgres-indexes` nodes'
subject, not restated here.

## Supersession: the exact rule

Every write at a coordinate runs inside a transaction that first takes
`pg_advisory_xact_lock` on a key derived by FNV-1a hashing the community UUID, the
kind, the pubkey and the `d` tag together. That serializes concurrent writers at
one coordinate; the function's doc comment notes hash collisions only add
serialization, since the SQL predicates still decide which rows are touched.

It then reads the current live head:

```sql
SELECT created_at, id FROM events
WHERE community_id = $1 AND kind = $2 AND pubkey = $3 AND d_tag = $4
  AND deleted_at IS NULL
ORDER BY created_at DESC, id ASC LIMIT 1
```

and compares the incoming event against it. (For the two narrow opt-in shapes noted
below, a persisted watermark row is compared under the same rule as well; on the
general path there is no watermark and the live head is the only comparand.)
**The dominance rule, exactly:** the incoming event is rejected as `Superseded`
when

- its `created_at` is strictly **less than** the accepted head's, **or**
- its `created_at` **equals** the accepted head's **and** its 32-byte event id
  compares byte-lexicographically **greater than or equal to** the accepted id.

**So the tie-break on an equal `created_at` is: the lower event id wins.** The
comparison is `incoming_id >= accepted_id → dominated`, over raw id bytes, which
is a total order and identical on every relay that implements it — which is the
point of having a tie-break at all. `created_at` is second-resolution, so ties are
not exotic; two writes from the same author in the same second reach it routinely.

Note the `ORDER BY created_at DESC, id ASC` in the head query is the same ordering
read from the other direction: newest first, and among equals, lowest id first.

If the incoming event is *not* dominated, the live rows at the coordinate are
superseded — by default an `UPDATE events SET deleted_at = NOW()`, a soft delete —
and the new event is inserted with `ON CONFLICT DO NOTHING`. A zero-row insert
means that event id already existed, so the savepoint rolls back and the outcome is
`Duplicate` rather than a coordinate left empty.

### The six outcomes

`ParameterizedReplaceStatus` names every way a write can land:

| Status | Meaning |
|---|---|
| `Inserted` | the incoming event became the coordinate's live head |
| `Duplicate` | this exact event was already accepted |
| `Superseded` | a newer, or a same-second lower-id, event already dominates it |
| `RevisionMissing` | a revision precondition was given but the coordinate has no live head |
| `RevisionMismatch` | the live head is not the revision the caller required |
| `ReplayOnlyMiss` | an exact replay was required and this event is not the live head |

Only `Inserted` commits; every other status rolls the transaction back.

A caller may also constrain the write structurally via
`ParameterizedReplacePrecondition` — `Unconditional` for plain NIP-33 ordering,
`ExpectedRevision` to require a specific live head (compare-and-swap), or
`ExactReplayOnly` to check idempotently without mutating anything.

## What is *not* enforced by the database

**One live head per coordinate is an ingest-path invariant, not a database
constraint.** `idx_events_parameterized` is a plain `CREATE INDEX` — non-unique,
and partial (`WHERE d_tag IS NOT NULL AND deleted_at IS NULL`). There is no
`UNIQUE` index and no `UNIQUE` constraint over `(community_id, kind, pubkey,
d_tag)` on `events` anywhere in the desired-state schema or the migrations.

The invariant rests entirely on three things holding together in the ingest path:
the advisory lock serializing writers, the dominance comparison rejecting stale
writes, and the soft delete of prior heads inside the same transaction. Any code
path that inserts a 30000–39999 event **without** going through
`replace_parameterized_event` can leave two live rows at one coordinate, and
nothing in Postgres will object. The head query's own comment acknowledges this
shape: its `ORDER BY … LIMIT 1` is described as defensive against historical data
where prior bugs left multiple live rows.

This is structural rather than accidental. `events` is `PARTITION BY RANGE
(created_at)` with primary key `(community_id, created_at, id)`, and PostgreSQL
requires a partitioned table's unique constraint to include every partition-key
column — so a unique constraint on the coordinate would have to carry `created_at`
too, which is exactly the column that varies between versions.

## Use cases — why an agent or developer needs this

**Writing a 30000–39999 kind.** Choose the `d` value deliberately: it *is* the
resource identity. Reusing a `d` value means replacing; changing it means creating
a second resource. A `d` tag longer than `D_TAG_MAX_LEN` (1024 bytes) is rejected
at ingest with `invalid: d tag too long`.

**Reading a write result and not being fooled by it.** When the store reports the
event did not become the live head, the relay still answers **`accepted: true`**
with the message `"duplicate:"`. Accepted-but-not-live is the normal shape of a
losing NIP-33 write, and treating `accepted: true` alone as success is wrong.
`buzz-cli` handles this by converting any accepted response whose message is
`duplicate` or begins with `duplicate:` into `CliError::Conflict`, which exits
**5** ("conflict") — an inline comment in `notes.rs` states this exists precisely
so a dominated write is not printed as a success.

**Reasoning about concurrent publishers.** Two clients writing the same coordinate
in the same second do not produce a race whose winner depends on arrival order.
The lower event id wins, deterministically, on every relay. The Postgres-backed
test `concurrent_parameterized_replacement_keeps_deterministic_head` asserts
exactly that, and also that replaying the winner and submitting an older event
both correctly fail to insert.

**Deleting one.** A NIP-09 `a`-tag deletion targets the coordinate, handled by
`soft_delete_by_coordinate`, whose predicate adds `created_at <=` the deletion
event's own `created_at` so a delayed or replayed tombstone cannot erase a version
newer than itself.

## Scope and omissions

**This node covers** what makes a kind parameterized-replaceable, what the
coordinate is and is not, the exact dominance and tie-break rule, the six write
outcomes and three preconditions, where the one-live-head invariant actually comes
from, and how a losing write surfaces to a caller.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Plain replaceable events keyed `(pubkey, kind)` | launchpad-26/buzz#1164 (drafted, not merged at the recorded revision) |
| The `events` table's full column list and index catalogue | `layers-data-postgres-events-table`, `layers-data-postgres-indexes` |
| Kind 39000 channel metadata as a capability | `capabilities-channels-channel-metadata` |
| The two narrow hard-delete opt-ins (NIP-RS read-state, buzz-mesh member status) and the `parameterized_event_watermarks` table that backs the first | a distinct concept; not filed as its own task at the recorded revision |
| NIP-09 deletion semantics in general | not located as a merged corpus node at the recorded revision |
| Which crate owns which part of the pipeline | `implementation-crates-buzz-core`, `implementation-crates-buzz-db`, `implementation-crates-buzz-relay` |

**Expected but not verified when this node was written:**

- **No upstream NIP text was consulted, because none is in this repository.**
  `docs/nips/` holds 22 Markdown files, all of them Buzz's own two-letter NIPs;
  zero match `^NIP-[0-9]`. Every claim above about "NIP-33" is therefore a claim
  about what **Buzz's own source says** NIP-33 requires — read from doc comments in
  `kind.rs`, `replaceable.rs` and `event.rs` — not a reading of the upstream
  specification. Where Buzz has drifted from upstream NIP-33, this node would
  document the drift and not notice it.
- **No test was executed.** `concurrent_parameterized_replacement_keeps_deterministic_head`
  and its siblings are `#[ignore = "requires Postgres"]`; the tie-break claim is
  read from the comparison expression in `replaceable.rs` and corroborated by the
  test's assertions, not by a run. No Postgres instance was available.
- **The absence of coordinate uniqueness was established by searching the schema
  and migrations, not by inspecting a live database catalog.** A constraint added
  outside those files — by `scripts/reconcile-schema-after-pgschema.sql` or by hand
  on a running relay — would not have been found. That script was not read.
- **No search was made for a code path that writes a 30000–39999 event bypassing
  `replace_parameterized_event`.** The claim above is that such a path *would* break
  the invariant, not that one exists.
