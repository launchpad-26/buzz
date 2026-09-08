---
id: layers-protocol-event-kind
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
  - statement: "crates/buzz-core/src/kind.rs opens with a module doc calling itself the Buzz V2 kind number registry and 'the authoritative source for Buzz kind numbers', and states that all constants are u32 because 'NIP-01 specifies kind as an unsigned integer, and u32 covers the full range without truncation'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs declares four range-boundary constants -- EPHEMERAL_KIND_MIN = 20000 and EPHEMERAL_KIND_MAX = 29999, documented as 'Never stored', and PARAM_REPLACEABLE_KIND_MIN = 30000 and PARAM_REPLACEABLE_KIND_MAX = 39999, documented as the bounds of 'the NIP-33 parameterized replaceable range'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's is_ephemeral and is_parameterized_replaceable are pure range comparisons against those constants, but is_replaceable is not a range check at all: it is `matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999)`, an enumerated set of three individual kinds plus one range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs declares no is_regular predicate; the regular class is expressed only as the complement of the other three, asserted per kind at compile time -- for example the three assertions that KIND_AGENT_TURN_METRIC is not ephemeral, not replaceable and not parameterized replaceable, written below the comment 'Compile-time: KIND_AGENT_TURN_METRIC is a regular stored kind'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's test module contains replaceable_and_parameterized_are_disjoint, which iterates every kind in 0..=65535 and asserts no kind satisfies both is_replaceable and is_parameterized_replaceable, and parameterized_replaceable_range, which pins the 29999/30000 and 39999/40000 boundaries."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The kind an event carries selects its storage path at ingest: crates/buzz-relay/src/handlers/ingest.rs branches on is_replaceable to replace_addressable_event, then on is_parameterized_replaceable to replace_parameterized_event with the d tag, and otherwise falls through to a plain insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Ephemeral kinds are rejected below the storage layer rather than merely skipped: crates/buzz-db/src/store/event.rs returns DbError::EphemeralEventRejected for any kind satisfying is_ephemeral, alongside DbError::AuthEventRejected for KIND_AUTH."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "The kind also selects an authorization path before storage: crates/buzz-relay/src/handlers/event.rs requires the MessagesWrite scope specifically for kinds satisfying is_ephemeral, with the comment that persistent events skip this gate and rely on ingest_event's per-kind scope allowlist instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "required_scope_for_kind in crates/buzz-relay/src/handlers/ingest.rs is a per-kind match whose default arm is `_ => Err(\"restricted: unknown event kind\")`, and whose doc comment states 'Returns Err for unknown kinds -- the relay rejects them'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Although kind constants are declared u32, the effective ceiling is u16: event_kind_u32 reads a kind as `event.kind.as_u16() as u32`, and kind.rs carries compile-time assertions of the form `assert!(KIND_AUTH <= u16::MAX as u32)` pinning named constants below 65535."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs collects the registered constants into `pub const ALL_KINDS: &[u32]`, documented as 'All registered kind constants -- used for duplicate detection and iteration', and its no_duplicate_kind_values test inserts each into a HashSet and asserts every insert is new."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Buzz reserves its own numeric blocks above the NIP-33 range and labels them with bare block comments in kind.rs -- 'Direct messages (41000-41999)', 'Agent job protocol (43000-43999)', 'Forum / social (45000-45999)', 'Workflow engine (46000-46999)', 'User groups (47000-47999)', 'System / admin custom range (48000-48999)' and 'Media (49000-49999)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs records a deliberate refusal to reuse a standard allocation, in the comment above the agent job block: 'Not using NIP-90 kinds (5000-6999) -- Buzz requires auth chains (depth <= 3, breadth <= 10).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs records three V1 kind numbers as mistakes of range rather than of naming: KIND_STREAM_MESSAGE_V2 notes 'V1 used kind:10002 (replaceable range -- wrong)', KIND_STREAM_MESSAGE_EDIT notes 'V1 used kind:10004 (replaceable range + NIP-51 collision -- wrong)', and the forum block notes 'V1 used addressable range (30001-30003) -- wrong'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Buzz does not confine its own kinds to those reserved blocks: kinds needing replaceable or addressable semantics are placed inside the standard ranges on purpose, and kind.rs pins that placement with compile-time assertions -- assert!(is_replaceable(KIND_AGENT_PROFILE)) for 10100, and assert!(is_parameterized_replaceable(KIND_PERSONA)) for 30175, among others."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_CHANNEL_METADATA = 41 carries the doc comment 'NIP-01: Channel metadata (replaceable). Not used by Buzz today.', while NIP-29 addressable group metadata is KIND_NIP29_GROUP_METADATA = 39000 under the block comment 'NIP-29 group state (addressable range 39000-39003)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The kind 41 constant is nonetheless live in the classification logic rather than dead code: it appears in ALL_KINDS and as a named arm of is_replaceable's match, so a kind:41 event would be classified replaceable even though no Buzz feature publishes one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep_refs(pattern='KIND_CHANNEL_METADATA', scope='crates, desktop/src, web, mobile/lib', types='rs,ts,dart') -> three hits, all in crates/buzz-core/src/kind.rs: the declaration, the ALL_KINDS entry, and the is_replaceable match arm; zero hits in any client tree"
  - statement: "Because two of the three classification helpers are range comparisons and one is an enumerated set, a kind's number determines its storage class for the ephemeral and parameterized-replaceable cases by arithmetic alone, while membership of the replaceable class for kinds 0, 3 and 41 is a hand-maintained decision that a number outside 10000-19999 cannot express."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.9
  - statement: "The compile-time range assertions exist because choosing a kind number is choosing storage behavior rather than merely choosing a label, so a number placed in the wrong range would silently change how the event is persisted rather than fail visibly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.8
  - statement: "No upstream numbered NIP specification text is present in this repository; docs/nips/ contains only Buzz's own two-letter NIPs, so every claim above about what NIP-01, NIP-29, NIP-33, NIP-51 or NIP-90 requires is sourced from what the Buzz registry records about them, not from the upstream specification."
    entry_class: FACT
    evidence:
      - "find_upstream_nip_files(name_pattern='NIP-0*.md', root='.', probe='docs/nips/NIP-01.md') -> find printed no output and the ls probe reported no such file or directory; a listing of docs/nips shows only Buzz's own two-letter NIPs: NIP-AA, NIP-AE, NIP-AM, NIP-AO, NIP-AP, NIP-CW, NIP-DV, NIP-ER, NIP-FI and its four sub-documents, NIP-GS, NIP-IA, NIP-MP, NIP-OA, NIP-PL, NIP-PMA, NIP-RS, NIP-WP"
  - statement: "Channel scope and addressable identity are carried by tags rather than by the kind: crates/buzz-relay/src/handlers/ingest.rs glosses `h` tags as 'channel scope' while routing NIP-34 git kinds away from them, and extracts a `d` tag only on the parameterized-replaceable branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Issue #1153 requires this node to define the term in one sentence before deeper explanation, to state boundaries and what the concept must not be confused with, to link to related concepts, implementation and verification without duplicating them, and to use examples only to clarify rather than to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1153 definition of done"
relationships:
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: development-event-kind-changes
  - type: references
    target: corpus-template-event-kind
  - type: references
    target: layers-data-postgres-events-table
  - type: references
    target: architecture-principles-event-driven-extension
  - type: references
    target: architecture-flows-event-ingestion
---

# The event kind

An **event kind** is the unsigned integer field on a Nostr event that declares what the
event means and, by the numeric range it falls in, how the relay must store it.

## Definition

Every event in Buzz carries a `kind`. That one number does three jobs at once, and they
are worth separating before anything else, because conflating them is where most
confusion about kinds starts:

1. **It names the event's meaning.** Kind `40002` is a stream message; kind `43001` is an
   agent job request. Nothing else in the event says which it is — not the tags, not the
   content shape. The kind is the discriminator.
2. **It selects the event's storage semantics.** Whether the relay appends the event
   forever, replaces a previous one, or refuses to store it at all is decided by which
   numeric class the kind falls into, not by anything the publisher asks for.
3. **It gates acceptance.** An event whose kind is not registered is rejected. Kind
   numbers are not an open extension point that clients may invent into.

**What a kind is not.** It is not a message type in the ordinary sense of a field a
client may set freely — the relay's `required_scope_for_kind` is a per-kind match whose
default arm returns `restricted: unknown event kind`, so an unregistered number is
refused rather than stored as an opaque blob. It is also not a routing address: which
channel an event belongs to is carried by its `h` tag, and which addressable resource it
replaces is carried by its `d` tag. And it is not a version number — where a Buzz kind's
meaning changed incompatibly, the registry allocated a *new* number and kept the old one
recorded, rather than redefining the original.

## The four storage classes

A kind belongs to exactly one of four classes. The first three have a predicate in
`crates/buzz-core/src/kind.rs`; the fourth is the complement of the other three and has
no predicate at all.

| Class | Which kinds | What the relay does |
|---|---|---|
| Ephemeral | `is_ephemeral` — the range 20000–29999 | Never stored. `buzz-db` returns `EphemeralEventRejected` rather than writing a row. |
| Replaceable | `is_replaceable` — kinds `0`, `3`, `41`, and the range 10000–19999 | Latest event per `(pubkey, kind)` wins, via `replace_addressable_event`. |
| Parameterized-replaceable | `is_parameterized_replaceable` — the range 30000–39999 | Latest event per `(pubkey, kind, d_tag)` wins, via `replace_parameterized_event`. |
| Regular | Everything else | Appended. Plain insert; no replacement. |

**The asymmetry in that table is the single most load-bearing detail about kinds, and it
is easy to state wrongly.** Two of the three predicates are pure arithmetic on the range
constants: `is_ephemeral` compares against `EPHEMERAL_KIND_MIN`/`MAX`, and
`is_parameterized_replaceable` against `PARAM_REPLACEABLE_KIND_MIN`/`MAX`. The third is
not. `is_replaceable` is an enumerated `matches!` — three individually named kinds (`0`,
`3`, and `KIND_CHANNEL_METADATA` = 41) plus the range 10000–19999. So "Buzz classifies
kinds by range" is true of ephemeral and parameterized-replaceable and **false** of plain
replaceable, whose three low-numbered members are a hand-maintained list that no
arithmetic rule could express.

The regular class has no positive test. A kind is regular by not matching the other
three, and where that matters the registry pins it per kind at compile time — three
assertions establish that `KIND_AGENT_TURN_METRIC` is not ephemeral, not replaceable and
not parameterized-replaceable, under the comment naming it "a regular stored kind".

The two replaceable classes are provably disjoint rather than assumed to be: the
`replaceable_and_parameterized_are_disjoint` test iterates every kind in `0..=65535` and
asserts no number satisfies both.

## The numeric ceiling

Kind constants are declared `u32`, and the module doc gives the reason: NIP-01 specifies
kind as an unsigned integer, and `u32` covers it without truncation. But the effective
ceiling is `u16`. `event_kind_u32` reads a kind off an event as `event.kind.as_u16() as
u32`, so the wire type is 16-bit, and the registry pins named constants below that limit
with compile-time assertions such as `assert!(KIND_AUTH <= u16::MAX as u32)`. The
disjointness test iterating exactly `0..=65535` reflects the same bound.

The practical consequence: the usable kind space is 0–65535, and the four class ranges
consume 20000–39999 of it.

## How Buzz allocates its own kinds

Buzz's allocation policy is not "use a private range" — it is **pick the range whose
storage semantics you actually need, and only fall back to a Buzz-reserved block when
what you need is plain append-only storage.**

Where a Buzz-specific capability needs replacement semantics, its kind is deliberately
placed *inside* a standard range and the placement is pinned at compile time:
`KIND_AGENT_PROFILE` = 10100 is asserted replaceable, `KIND_PERSONA` = 30175 asserted
parameterized-replaceable. Where a capability needs ordinary append-only storage, it goes
in one of the blocks Buzz reserves for itself above the addressable range, each labelled
by a bare block comment in the registry: direct messages 41000–41999, agent jobs
43000–43999, forum and social 45000–45999, the workflow engine 46000–46999, user groups
47000–47999, system and admin 48000–48999, media 49000–49999.

The registry also records the two ways this policy has been applied deliberately against
the obvious alternative:

- **A refusal to reuse a standard allocation.** The agent job block carries the note
  "Not using NIP-90 kinds (5000–6999) — Buzz requires auth chains (depth ≤ 3, breadth ≤
  10)." Reusing NIP-90 would have meant inheriting semantics Buzz's authorization model
  cannot honour.
- **Three recorded corrections of range, not of name.** `KIND_STREAM_MESSAGE_V2` notes
  that V1 used kind 10002, "replaceable range — wrong"; `KIND_STREAM_MESSAGE_EDIT` notes
  V1's 10004 was "replaceable range + NIP-51 collision — wrong"; the forum block notes V1
  used "addressable range (30001–30003) — wrong". In each case the number was moved and
  the mistake left in the comment. A stream message is append-only, so it could not live
  in a replaceable range without the relay silently overwriting message history.

Those corrections are the clearest available evidence of why this concept matters at all:
**choosing a kind number is choosing behaviour.** A number in the wrong range does not
produce a type error or a rejected event — it produces an event the relay stores
differently than intended.

## Where the registry lives, and what it guarantees

`crates/buzz-core/src/kind.rs` is the authoritative registry, by its own module doc. It
collects the registered constants into `ALL_KINDS`, documented as "used for duplicate
detection and iteration", and a `no_duplicate_kind_values` test inserts each into a
`HashSet` and asserts every insert is new.

**This node deliberately does not reproduce the registry.** A catalogue of kind numbers
is reference content that would be stale the day after it was written; the registry is
one file away and is the only copy that cannot drift from itself. Read it directly.

Note also that the duplicate guarantee is exactly as wide as `ALL_KINDS` and no wider — a
constant declared but not listed there is invisible to the test.
`development-event-kind-changes` documents that gap and its current instances; this node
does not restate them.

## A note on kind 41

Kind 41 is a live example of the difference between "allocated" and "used", and it is
worth stating precisely because a summary of it circulates in shortened form.

`KIND_CHANNEL_METADATA` = 41 is NIP-01's channel metadata kind. Its doc comment reads
"NIP-01: Channel metadata (replaceable). Not used by Buzz today." Buzz's own channel
metadata is `KIND_NIP29_GROUP_METADATA` = 39000, in the NIP-29 addressable block
39000–39003 — a different kind, in a different class, with different replacement
semantics.

But 41 is not dead code. The constant appears twice beyond its declaration: as an entry
in `ALL_KINDS`, and as a named arm of `is_replaceable`'s match. It appears nowhere in the
desktop, web or mobile trees. So the accurate statement is that **no Buzz feature
publishes kind 41, while the relay would still classify a kind:41 event as replaceable if
one arrived** — which is why 41 is one of the three individually named kinds that make
`is_replaceable` an enumerated set rather than a range check. The two facts are the same
fact seen twice.

## Use cases

You need this concept before any of the following will make sense:

- **Reading the registry.** Knowing that the number encodes storage class turns
  `kind.rs`'s ranges and its compile-time assertions from noise into the enforcement they
  are.
- **Adding a capability.** Buzz's extension model is to add a kind rather than an
  endpoint. Which range you pick is a behavioural decision, taken before any code is
  written. The procedure itself belongs to `development-event-kind-changes`.
- **Reading a relay rejection.** `restricted: unknown event kind` is not a malformed-event
  error; it means the number is not registered.
- **Reasoning about what persists.** An event of an ephemeral kind leaves no row to query
  later, however successfully it was published.

## Scope and omissions

**This node covers** what an event kind is, the four storage classes and which of them are
decided by range versus by enumeration, the effective numeric ceiling, Buzz's own
allocation policy and the corrections recorded against it, and where the authoritative
registry lives.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The catalogue of individual kind numbers and their meanings | `crates/buzz-core/src/kind.rs` itself; this node points at it rather than copying it |
| How to add or change a kind — the ordered procedure, its registration steps and its rollback | `development-event-kind-changes` |
| How to document one particular kind as a corpus node | `corpus-template-event-kind` |
| The `events` table's row shape, columns, indexes and the SQL-side replacement identity | `layers-data-postgres-events-table` |
| Why a new capability must be an event rather than an HTTP endpoint | `architecture-principles-event-driven-extension` |
| What the relay does with an event after the kind has selected its path | `architecture-flows-event-ingestion` |
| The wire contract of an event as a whole — id, pubkey, sig, tags, content — of which `kind` is one field | No node exists on `origin/launchpad` at the recorded revision; a sibling task in this batch is drafting it |

**Expected but not verified when this node was written:**

- **No upstream NIP text is in this repository.** `ls docs/nips/NIP-01.md` reports no such
  file and `find . -name 'NIP-0*.md'` returns nothing; `docs/nips/` holds only Buzz's own
  two-letter NIPs. Every statement above about what NIP-01, NIP-29, NIP-33, NIP-51 or
  NIP-90 requires is therefore sourced from what the Buzz registry *records* about those
  specifications, not from the specifications themselves. Where the registry has
  misread upstream, this node inherits that misreading, and nothing in this repository
  would reveal it.
- **The four-class table was not exercised against a live relay.** It is read from the
  ingest branch order and the `buzz-db` rejection, both statically. No event of each class
  was published to a running relay to observe the resulting row (or absence of one).
- **No test was found that asserts the regular class end to end.** The compile-time
  assertions cover named kinds one at a time; no test enumerates the kind space and
  asserts that everything outside the three predicates takes the plain-insert path. That
  the fourth class has no predicate is stated above as an observation about the code, not
  as something a test guards.
- **`is_replaceable`'s three enumerated members were not traced to an upstream
  requirement.** That kinds 0, 3 and 41 are replaceable is recorded in the predicate's own
  doc comment as NIP-01's rule; with no upstream text in the tree, that attribution was
  not independently checked.
- **No merged verification node covers kind classification, so this node declares no
  verification edge.** `verification-contracts-nostr` was read before deciding that: its
  subject is NIP interop behaviour for gift wraps and p-gated subscriptions, not the
  range-to-storage-class mapping. The tests that do guard this concept —
  `replaceable_and_parameterized_are_disjoint`, `parameterized_replaceable_range` and
  `no_duplicate_kind_values` — live inside `kind.rs` itself and are cited directly in the
  evidence ledger rather than reached through a corpus edge.
