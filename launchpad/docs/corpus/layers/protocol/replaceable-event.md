---
id: layers-protocol-replaceable-event
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
  - statement: "is_replaceable is not a range check: its body is matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999), which is three individually enumerated kinds plus one range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Its two sibling predicates are pure two-sided range comparisons against named boundary constants: is_ephemeral tests kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX, and is_parameterized_replaceable tests kind >= PARAM_REPLACEABLE_KIND_MIN && kind <= PARAM_REPLACEABLE_KIND_MAX, where those constants are 20000/29999 and 30000/39999."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_CHANNEL_METADATA is 41 and carries the doc comment 'NIP-01: Channel metadata (replaceable). Not used by Buzz today.', so the predicate enumerates a kind the same file records as unused."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Named constants KIND_PROFILE = 0 and KIND_CONTACT_LIST = 3 both exist in the same file, yet the predicate writes the bare literals 0 and 3 while writing KIND_CHANNEL_METADATA by name."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Because a range cannot express membership of 0, 3 and 41 alongside 10000-19999, the enumerated form is forced by the class's own shape rather than chosen as a style, and kind 41's presence despite being unused is the clearest evidence of that."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.9
  - statement: "Two compile-time assertions pin the predicate's behaviour at both ends: assert!(is_replaceable(KIND_AGENT_PROFILE)) for 10100 and assert!(!is_replaceable(KIND_AGENT_TURN_METRIC)) for a regular stored kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The unit test replaceable_and_parameterized_are_disjoint iterates every kind in 0..=65535u32 and asserts no kind satisfies both is_replaceable and is_parameterized_replaceable, so disjointness is established exhaustively over the reachable kind space rather than by sampling."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "is_replaceable has exactly one production call site, in the relay ingest pipeline, where a true result routes the event to Db::replace_addressable_event and a parameterized-replaceable kind routes to replace_parameterized_event instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "replace_addressable_event keeps only the event with the highest created_at per (community_id, kind, pubkey, channel_id), soft-deletes the previously live row by setting deleted_at = NOW() rather than removing it, and serializes concurrent writers for the same tuple with a transaction-scoped pg_advisory_xact_lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "The tie-break is lowest event id wins: an incoming event is treated as dominated when created_at < existing_ts, or when created_at == existing_ts and the incoming id is greater than or equal to the existing id, so an incoming event with an equal timestamp supersedes only if its id sorts strictly lower."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "The same >= comparison also makes a resubmission of the identical event dominated, and the insert additionally uses ON CONFLICT DO NOTHING so that an already-present event id rolls the transaction back, preserving the previously live event and returning was_inserted = false."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "extract_d_tag returns None for any kind outside the parameterized-replaceable range, so a replaceable event's d_tag column is stored NULL and the absence of a d tag is a storage fact rather than only a convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Every replaceable kind Buzz names for client submission - KIND_PROFILE 0, KIND_CONTACT_LIST 3, KIND_MUTE_LIST 10000, KIND_PIN_LIST 10001, KIND_NIP65_RELAY_LIST_METADATA 10002, KIND_BOOKMARK_LIST 10003, KIND_EMOJI_LIST 10030 and KIND_AGENT_PROFILE 10100 - is listed in is_global_only_kind, so ingest forces channel_id = None for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "The kind registry documents kinds 10000, 10001, 10002 and 10003 as 'User-owned global state, keyed by (pubkey, kind)', matching the same ownership and scope shape it records for kind 3."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "is_global_only_kind carries a recorded limitation that a stray h tag remains on the stored event because Nostr events are signed and tags cannot be stripped without invalidating the signature, and that read-path filter matching treats explicit h tags as authoritative, so such an event can still match #h queries."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Two relay-signed kinds, KIND_NIP43_MEMBERSHIP_LIST 13534 and KIND_IA_ARCHIVED_LIST 13535, fall inside 10000-19999 and are therefore replaceable, but are not listed in is_global_only_kind; 13534 is additionally is_relay_only_kind, so client submission of it is rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "replace_addressable_event is also called directly, bypassing the predicate, for NIP-29 discovery state in the 39000-39002 range and for relay-signed global snapshots, so the function serves a wider set of kinds than is_replaceable selects."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "No test in crates/buzz-db/src/store/replaceable.rs exercises replace_addressable_event with a kind for which is_replaceable returns true: the only kinds constructed there are 39002 and 30023, both parameterized-replaceable, and all eleven database-backed tests in the file are annotated #[ignore = \"requires Postgres\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
      - "grep_o(pattern='Kind::Custom([0-9]*)', path='crates/buzz-db/src/store/replaceable.rs') -> 3 occurrences of Kind::Custom(39002) and 1 of Kind::Custom(30023); no is_replaceable kind among them"
  - statement: "No test asserts the membership of kinds 0, 3 or 41 in is_replaceable; the symbol appears five times in the whole crates/ tree, namely its definition, two compile-time assertions, the disjointness test and the single ingest call site."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep_r('is_replaceable(0)|is_replaceable(3)|is_replaceable(41)|is_replaceable(KIND_CHANNEL_METADATA)', include='*.rs', path='crates/') -> 0 matches, against 5 total matches for the bare symbol is_replaceable"
  - statement: "No upstream Nostr specification text is present in this repository, so no claim about what NIP-01 or NIP-16 requires can be cited to a file here; docs/nips/ holds only Buzz's own two-letter NIPs."
    entry_class: FACT
    evidence:
      - "find_name(path='.', patterns='NIP-01*,NIP-16*', exclude='./target') -> 0 matches; ls(docs/nips/) -> NIP-AA, NIP-AE, NIP-AM, NIP-AO, NIP-AP, NIP-CW, NIP-DV, NIP-ER, NIP-FI*, NIP-GS, NIP-IA, NIP-MP, NIP-OA, NIP-PL, NIP-PMA, NIP-RS, NIP-WP only"
  - statement: "The kind registry's own doc comments attribute the replaceable class to NIP-01 and the parameterized-replaceable class to NIP-33, and the replacement function's doc comment attributes the same-second deterministic ordering rule to NIP-16."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "Issue #1164 requires exactly one hand-authored canonical document that defines the term in one sentence before deeper explanation, states what the concept must not be confused with, and files any newly discovered second concept as a separate task rather than folding it in."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1164 definition of done"
  - statement: "The sibling parameterized-replaceable class is documented by its own task, issue #1163, which was not merged when this node was written, so this node disambiguates against that class in prose without declaring a relationship edge to it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1163 (open sibling task in Feature #609)"
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
    target: layers-data-data-lifecycle
  - type: references
    target: layers-data-authoritative-data
  - type: references
    target: layers-data-transaction-boundaries
---

# Replaceable event

A **replaceable event** is a Nostr event whose kind is one of a fixed set — kind 0,
kind 3, kind 41, or anything in 10000–19999 — for which the relay keeps only the
newest event per author, discarding the one it replaces. One author holds at most one
live event of that kind at a time.

## Definition

Buzz decides membership with one function, `is_replaceable` in
`crates/buzz-core/src/kind.rs`. Its body is the whole definition:

```rust
matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999)
```

**That is an enumerated set, not a range check**, and the distinction is the single
most load-bearing fact about this class. Read the two predicates that sit beside it
in the same file:

| Predicate | Form | Kinds |
|---|---|---|
| `is_ephemeral` | `kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX` | 20000–29999 |
| `is_parameterized_replaceable` | `kind >= PARAM_REPLACEABLE_KIND_MIN && kind <= PARAM_REPLACEABLE_KIND_MAX` | 30000–39999 |
| `is_replaceable` | `matches!(kind, 0 \| 3 \| KIND_CHANNEL_METADATA \| 10000..=19999)` | 0, 3, 41, 10000–19999 |

Both siblings are two-sided comparisons against named boundary constants. Only
`is_replaceable` enumerates. It has to: three of its four members are individual kinds
that predate the range convention and sit nowhere near it, so no pair of bounds can
express the set.

**Kind 41 is the proof.** `KIND_CHANNEL_METADATA` is 41, and the registry entry
directly above it reads *"NIP-01: Channel metadata (replaceable). Not used by Buzz
today."* The predicate enumerates a kind the same file records as unused — which is
exactly what an enumerated set does and a range cannot. A reader who mentally
simplifies this predicate to "10000–19999" gets kinds 0, 3 and 41 wrong, and a
reader who assumes it must therefore be dead code gets 41 wrong in the other
direction.

A smaller tell in the same line: `KIND_PROFILE = 0` and `KIND_CONTACT_LIST = 3` both
exist as named constants in that file, yet the predicate writes the bare literals `0`
and `3` while writing `KIND_CHANNEL_METADATA` by name.

### What this must not be confused with

**Parameterized-replaceable events (30000–39999).** These are the class documented
separately, and they are keyed differently: `(pubkey, kind, d_tag)`, so one author may
hold many live events of one kind, distinguished by the `d` tag. A replaceable event
has **no `d` tag**, and that absence is enforced in storage rather than left to
convention — `extract_d_tag` in `crates/buzz-db/src/store/event.rs` returns `None` for
any kind outside the parameterized range, so the `d_tag` column is written NULL. The
two classes are also proved disjoint: the test
`replaceable_and_parameterized_are_disjoint` iterates every kind in `0..=65535u32` and
asserts no kind satisfies both predicates, which is exhaustive over the reachable kind
space rather than a sample.

**Ephemeral events (20000–29999).** Not replaced — not stored at all.

**Deletion.** Supersession soft-deletes the prior row, which is a different operation
from a NIP-09 deletion request. That distinction belongs to the data layer's own
nodes, linked below.

## How supersession works

The predicate has exactly one production call site, in the relay's ingest pipeline
(`crates/buzz-relay/src/handlers/ingest.rs`), which routes a replaceable kind to
`Db::replace_addressable_event` in `crates/buzz-db/src/store/replaceable.rs`.

That function keeps the event with the highest `created_at` per
**`(community_id, kind, pubkey, channel_id)`**. Note that Buzz's storage key is wider
than the conceptual `(pubkey, kind)`: it carries the community for tenancy and the
channel for scope. In practice the channel dimension collapses for client-submitted
kinds — see *Scoping* below.

Around that rule sit four behaviours worth knowing:

- **Serialization.** Concurrent writers for the same tuple are ordered by a
  transaction-scoped `pg_advisory_xact_lock`, so two simultaneous updates cannot both
  read the same predecessor.
- **Soft delete.** The superseded row is updated with `deleted_at = NOW()`, not
  removed. The old event stays on disk and stops being live.
- **Stale writes are rejected, not queued.** An event that loses returns
  `was_inserted = false`, and callers skip fan-out for it.
- **Atomicity with the mention index.** The replacement and its denormalized mention
  rows commit together; an indexing failure rolls back the new event and restores the
  previously live one.

### The tie-break

`created_at` is second-resolution, so two events from one author can legitimately
carry the same timestamp. The tie-break is **lowest event id wins**. The incoming
event is treated as dominated when:

```
created_at < existing_ts  ||  (created_at == existing_ts && incoming_id >= existing_id)
```

So on an equal timestamp the incoming event supersedes only if its id sorts strictly
lower. Because ids are content hashes, every relay reaches the same answer without
coordinating — which is the point of choosing id order rather than arrival order.

The `>=` does double duty: it also makes a resubmission of the *identical* event
dominated. Belt and braces, the insert then uses `ON CONFLICT DO NOTHING`, and a
conflict rolls the transaction back so the soft-delete does not strand the author with
no live event at all.

## Scoping

Every replaceable kind Buzz names for client submission — 0, 3, 10000, 10001, 10002,
10003, 10030 and 10100 — appears in `is_global_only_kind`, so ingest forces
`channel_id = None` for it. The registry describes 10000–10003 as *"User-owned global
state, keyed by `(pubkey, kind)`"*, the same shape it records for kind 3. For these
kinds the four-part storage key therefore collapses to `(community_id, kind, pubkey)`,
matching the conceptual key.

A caveat is recorded in the source rather than discovered here: a stray `h` tag stays
on the stored event, because Nostr events are signed and tags cannot be stripped
without invalidating the signature, and read-path filter matching treats explicit `h`
tags as authoritative. Such an event can still match `#h` queries even though it was
stored globally.

Two kinds in the range are exceptions: `KIND_NIP43_MEMBERSHIP_LIST` (13534) and
`KIND_IA_ARCHIVED_LIST` (13535) are relay-signed and absent from
`is_global_only_kind`; 13534 is additionally relay-only, so client submission is
rejected outright.

`replace_addressable_event` is also called directly by relay-side code for NIP-29
discovery state in 39000–39002 and for relay-signed global snapshots. Those calls
bypass `is_replaceable` entirely, so the function serves more kinds than the predicate
selects — a useful thing to know before reading its tests.

## Use cases

Understanding this class matters when you are:

- **Adding a kind.** Whether it lands in 10000–19999 decides whether an author gets
  one live copy or an unbounded history, and that is not reversible once clients
  depend on it. If you need many live copies per author, you want the parameterized
  class, not this one.
- **Reading the predicate.** Any code that reimplements the kind test as a range
  comparison silently drops kinds 0, 3 and 41.
- **Debugging a "my update did not take" report.** Same-second submissions are the
  usual cause, and the id tie-break means the *later* event genuinely can lose.
- **Querying stored events.** Superseded events are still rows with `deleted_at` set,
  so a query that ignores `deleted_at IS NULL` returns history the protocol considers
  replaced.

## Related nodes

Typed `references` edges are declared in this node's front matter to the crates that
own the predicate (`buzz-core`), the replacement transaction (`buzz-db`) and the
ingest routing (`buzz-relay`), and to the data-layer nodes that own the row, its
lifecycle, its authority and its transaction boundaries. This node does not restate
their content.

## Scope and omissions

**This node covers** what makes an event replaceable in Buzz, the exact membership of
`is_replaceable` and why it is an enumerated set rather than a range, the supersession
rule and its same-second tie-break, and how the storage key relates to the conceptual
`(pubkey, kind)` key.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The parameterized-replaceable class (30000–39999, `d`-tag keyed) | launchpad-26/buzz#1163, unmerged at the recorded revision |
| The `events` table's columns, indexes and partitioning | `layers-data-postgres-events-table` |
| Soft-delete semantics, retention and what "live" means over time | `layers-data-data-lifecycle`, `layers-data-authoritative-data` |
| Advisory locking and transaction scope as a general pattern | `layers-data-transaction-boundaries` |
| NIP-09 deletion requests, which are a different operation from supersession | the data layer's deletion node |
| Ephemeral events (20000–29999) | not documented at the recorded revision |

**Expected but not verified when this node was written:**

- **No test exercises `replace_addressable_event` with a kind for which
  `is_replaceable` is true.** The only kinds constructed in that file's tests are
  39002 and 30023, both parameterized-replaceable, and all eleven database-backed
  tests there are annotated `#[ignore = "requires Postgres"]`. The supersession rule
  and tie-break above were established by reading the SQL and the comparison
  expression, **not** by observing a passing test for this class. No test was run for
  this node.
- **No test asserts that kinds 0, 3 or 41 are members.** The symbol appears five times
  in the whole `crates/` tree — its definition, two compile-time assertions covering
  10100 and a negative case, the disjointness sweep, and the ingest call site. The
  disjointness test does traverse 0, 3 and 41, but it only asserts they are not *also*
  parameterized-replaceable; it would pass unchanged if they were dropped from the
  predicate.
- **No upstream Nostr specification text exists in this repository.** `docs/nips/`
  holds only Buzz's own two-letter NIPs. Every attribution to NIP-01, NIP-16 or NIP-33
  above is reported as *what Buzz's own doc comments say*, and was not checked against
  the upstream specifications, which are not available here.
- **Kind 41's runtime status was not tested.** The registry says "Not used by Buzz
  today" and the predicate includes it; whether any client ever submits kind 41 to a
  live relay was not observed.
