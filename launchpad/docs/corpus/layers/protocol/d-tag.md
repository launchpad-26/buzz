---
id: layers-protocol-d-tag
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
  - statement: "kind.rs's is_parameterized_replaceable doc comment records that events in the 30000-39999 range 'are keyed by (pubkey, kind, d_tag) -- the latest created_at wins', and the range bounds are the named constants PARAM_REPLACEABLE_KIND_MIN and PARAM_REPLACEABLE_KIND_MAX."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's is_replaceable doc comment records that NIP-33 parameterized-replaceable kinds 'use a different replacement key (includes d-tag) and are handled separately via replace_parameterized_event', which is what distinguishes the two-part replaceable key from the three-part addressable one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "extract_d_tag returns None for any kind outside 30000-39999, and for kinds inside it returns the first d tag's value, defaulting to the empty string when no d tag is present, with the code comment recording that rule as NIP-33's ('Missing d tag -> empty string per NIP-33')."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Three unit tests in event.rs pin that behaviour directly: extract_d_tag_first_d_wins asserts a second d tag is ignored, extract_d_tag_missing_becomes_empty_string asserts a NIP-33 event with no d tag yields Some(\"\"), and extract_d_tag_empty_value_preserved asserts an explicitly empty d value is kept rather than treated as absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "D_TAG_MAX_LEN is 1024 bytes, documented in event.rs as a bound on short NIP-33 identifiers, and the relay's parameterized-replaceable ingest branch rejects a longer value with the message 'invalid: d tag too long' before any write is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "replace_parameterized_event_in_transaction_impl folds the d value's bytes into the transaction-scoped advisory lock key alongside community, kind and pubkey, then selects the live head with WHERE community_id AND kind AND pubkey AND d_tag AND deleted_at IS NULL ORDER BY created_at DESC, id ASC LIMIT 1, so the d value is part of both the concurrency key and the lookup key."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "An incoming event is treated as dominated -- and returned as Superseded rather than stored as the head -- when its created_at is older than the accepted head's, or equal to it and its event id sorts greater than or equal to the accepted id, so the coordinate's winner is deterministic rather than arrival-ordered."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "The relay pushes a REQ filter's #d values into SQL only when every kind named in that filter is parameterized-replaceable, because d_tag is NULL for all other kinds and an unconditional pushdown would silently exclude rows that match by tag; a single #d value becomes an equality predicate and multiple values become a set."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The test d_tag_pushdown_only_for_nip33_kinds asserts that pushdown activates for a NIP-33-only filter and stays inactive for a non-NIP-33 kind, a mixed-kind filter, a kindless filter, and a multi-value #d filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "NIP-09 deletion of an addressable event splits the a tag's value on ':' into three parts, takes the third part as the d value, and -- for any parameterized-replaceable kind -- soft-deletes the live row matching (kind, pubkey, d_tag), scoped to versions at or before the deletion event's own created_at."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The events table stores d_tag as a nullable TEXT column and indexes it through idx_events_parameterized, a non-unique partial index on (community_id, kind, pubkey, d_tag, created_at DESC, id) restricted to WHERE d_tag IS NOT NULL AND deleted_at IS NULL; no UNIQUE constraint over that coordinate exists on the events table."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "schema/schema.sql"
  - statement: "The only coordinate-shaped uniqueness declared anywhere in the schema is the PRIMARY KEY (community_id, kind, pubkey, d_tag) on the separate parameterized_event_watermarks table, introduced so replacement ordering survives without retaining the superseded event rows and their payloads -- its own migration describes it as 'a compact ordering watermark' retaining 'the only historical fact replacement needs'."
    entry_class: FACT
    evidence:
      - "migrations/0007_nip_rs_retention.sql"
      - "schema/schema.sql"
  - statement: "Because the events table declares no uniqueness over (community_id, kind, pubkey, d_tag), one-head-per-coordinate is upheld by the ingest path -- the advisory lock, the dominance comparison and the soft-delete of the previous head -- and not by a database constraint that would reject a second live row."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
      - "migrations/0001_initial_schema.sql"
      - "schema/schema.sql"
    confidence: 0.8
  - statement: "kind.rs defines the NIP-29 addressable group-state kinds 39000 (metadata), 39001 (admins), 39002 (members) and 39003 (roles), all inside the parameterized-replaceable range, and its own test asserts is_parameterized_replaceable(39000)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The relay's emit_group_discovery_events builds those group-state events with the channel's group id as the d tag value, so a Buzz channel's addressable state is coordinate-keyed by channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The desktop get_channels command resolves a user's channels by querying kind:39002 filtered on #p for the caller's own pubkey and then reading each returned event's d tag as the channel id, and fetches those channels' kind:39000 metadata with a #d filter over the ids it collected; no h tag participates in either step."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/channels/fetch.rs"
  - statement: "The relay's channel-scoping match arm excludes user-owned and parameterized-replaceable kinds from h-tag channel scoping, with repeated inline comments recording that these kinds are 'keyed by (pubkey, kind, d_tag)' and that 'a stray h tag must not channel-scope them'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "KIND_TEAM_CATALOG's doc comment records that ingest requires exactly one non-empty, bounded d tag because 'generic NIP-33 storage maps a missing d to the empty coordinate, which would collapse every team into one slot', naming the concrete failure the empty-d default produces when a kind expects a distinguishing identifier."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-RS, one of Buzz's own NIPs held in this repository, requires its kind:30078 read-state events to carry exactly one d tag of the form read-state:<slot-id> with the slot id being exactly 32 lowercase hex characters, and requires clients to ignore events with zero d tags, more than one d tag, or a d value not beginning with read-state:."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md"
  - statement: "NIP-RS states the shape is fixed rather than opaque so a relay 'can recognize a read-state coordinate structurally, from the d tag alone and without decrypting anything, and apply per-coordinate protections to it'."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md"
  - statement: "kind.rs records several other Buzz kinds whose d value carries a distinct kind-specific meaning: KIND_AGENT_ENGRAM is 'addressed by (pubkey_a, kind, d_tag), where d_tag is an HMAC over the agent-owner conversation key', KIND_PERSONA's d_tag is 'the plaintext persona slug', KIND_TEAM's is 'the team's stable id', KIND_MANAGED_AGENT's is 'the agent's pubkey', and KIND_DM_VISIBILITY is 'parameterized replaceable, d=viewer_pubkey'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The upstream NIP-01 and NIP-33 specification texts are not present anywhere in this repository -- docs/nips/ holds only Buzz's own two-letter NIPs (NIP-AA, NIP-AE, NIP-AP, NIP-DV, NIP-ER, NIP-IA, NIP-MP, NIP-RS and the rest) and contains no upstream numbered spec file."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Issue #1148's definition of done requires one hand-authored canonical document, schema-valid front matter with a stable node id, one independently maintainable idea with any second concept filed separately, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links rather than duplicated neighbouring content, a check against the recorded provenance revision, a clean validator run, a one-sentence definition before deeper explanation, stated boundaries, and examples that introduce no second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1148 definition of done"
  - statement: "Feature #609 splits the surrounding protocol subjects across separate sibling tasks -- parameterized-replaceable events (#1163), replaceable events (#1164), event tags in general (#1155) and the h tag (#1158) -- none of which were merged when this node was authored, so this node names them as boundaries rather than linking to them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#609 batch dispatch brief for this Feature"
relationships:
  - type: references
    target: layers-data-postgres-events-table
  - type: references
    target: layers-data-postgres-indexes
  - type: references
    target: capabilities-channels-channel-metadata
  - type: references
    target: capabilities-channels-channel-membership
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-db
---

# The `d` tag

## Definition

The **`d` tag** is the identifier tag an event carries to distinguish itself from the
other events the same author publishes at the same kind — it is the third and final
component of an addressable event's coordinate, `(pubkey, kind, d)`.

That is the whole idea. Without a `d` value, an author has one slot per kind. With one,
they have as many slots as they have distinct `d` values, and each slot independently
holds exactly one live event: the newest one published to it.

`crates/buzz-core/src/kind.rs` states this in its own words. `is_parameterized_replaceable`
— true for kinds 30000–39999 — carries the doc comment *"These events are keyed by
`(pubkey, kind, d_tag)` — the latest `created_at` wins."* Its neighbour `is_replaceable`
draws the contrast from the other side: NIP-33 kinds *"use a different replacement key
(includes `d`-tag) and are handled separately via `replace_parameterized_event`."*

**What this node does not mean by "the `d` tag."** It does not mean the *class* of events
that use one, and it does not mean the tag system those events are expressed in. Those
are separate subjects with their own nodes (see *Scope and omissions*). This node is
about the identifier itself: where its value comes from, what Buzz does when it is
missing or malformed, and what the value is actually used for once it has been read.

**A note on where the rules come from.** The upstream Nostr specifications that define
the `d` tag are not in this repository — `docs/nips/` holds only Buzz's *own* NIPs, all
of them two-letter codes. Every statement below about "what NIP-33 says" is therefore
stated as what a Buzz source *records* about it, cited to that source, never to an
upstream file this repository does not have.

## Reading the value: the four rules Buzz applies

`extract_d_tag` in `crates/buzz-db/src/store/event.rs` is the shared function every path
— relay ingest, the command executor, the stores, the CLI — calls to read a `d` value off
an event, and it settles four questions a wire event can raise:

| Question | What the code does |
|---|---|
| Kind outside 30000–39999? | Returns `None`. The column stays `NULL` — a `d` tag on a non-addressable kind is not a coordinate. |
| No `d` tag at all? | Returns `Some("")`. The comment records this as NIP-33's rule: *"Missing d tag → empty string per NIP-33."* |
| Two or more `d` tags? | The **first** one wins; the rest are discarded silently. |
| An explicitly empty `d` value? | Preserved as `""` — indistinguishable from the missing case, by design. |

Each of those is pinned by a named unit test in the same file
(`extract_d_tag_first_d_wins`, `extract_d_tag_missing_becomes_empty_string`,
`extract_d_tag_empty_value_preserved`), so they are behaviour, not incidental.

The empty-string default is the rule that surprises people, and `kind.rs` names the
concrete damage it can do. `KIND_TEAM_CATALOG`'s doc comment explains why its ingest
path demands exactly one non-empty, bounded `d` tag rather than accepting the default:
*"generic NIP-33 storage maps a missing `d` to the empty coordinate, which would collapse
every team into one slot."* A kind whose identity depends on the `d` value must enforce
its own presence — the generic path will not do it.

One length bound applies to every kind. `D_TAG_MAX_LEN` is 1024 bytes, and the relay's
parameterized-replaceable ingest branch rejects anything longer with
`invalid: d tag too long` before attempting a write.

## What the value is used for

**It keys replacement.** `replace_parameterized_event_in_transaction_impl`
(`crates/buzz-db/src/store/replaceable.rs`) folds the `d` bytes into the
transaction-scoped advisory lock key alongside community, kind and pubkey, then reads the
live head with a predicate on all four. So the `d` value is both the concurrency key and
the lookup key — two writes to *different* `d` values under one author and kind do not
serialise against each other, and neither can displace the other.

Which event wins a contested coordinate is decided, not raced. An incoming event is
*dominated* — returned as `Superseded` rather than stored — when its `created_at` is
older than the accepted head's, or equal to it and its event id sorts at or above the
accepted id. Same-second collisions therefore resolve by event id, identically on every
replica.

**It keys deletion.** A NIP-09 deletion of an addressable event names its target through
an `a` tag, and `crates/buzz-relay/src/handlers/side_effects.rs` splits that value on `:`
into three parts, taking the third as the `d` value. For any parameterized-replaceable
kind it then soft-deletes the live row matching `(kind, pubkey, d_tag)`, scoped to
versions at or before the deletion event's own `created_at` so a replayed tombstone
cannot erase a newer head. The `a`-tag coordinate form itself is not this node's subject;
what matters here is that the `d` value is the part of it that selects the slot.

**It keys queries.** A REQ filter can name `#d` values, and
`crates/buzz-relay/src/handlers/req.rs` pushes them into SQL — but only when *every*
kind in the filter is parameterized-replaceable. The reasoning is in the code: `d_tag` is
`NULL` for every other kind, so an unconditional `AND d_tag = $n` would silently drop
rows that legitimately match by tag. A single `#d` value becomes an equality predicate;
several become a set. The test `d_tag_pushdown_only_for_nip33_kinds` asserts pushdown
stays *off* for a non-NIP-33 kind, a mixed-kind filter, a kindless filter and a
multi-value filter alike.

**Storage and indexing are a neighbour's subject.** The `d_tag` column and
`idx_events_parameterized` are already documented by `layers-data-postgres-events-table`
and `layers-data-postgres-indexes`; both are linked above. The one point worth stating
here, because it is about the identifier's guarantees rather than the table's shape: that
index is **not** unique, and the `events` table declares no `UNIQUE` constraint over
`(community_id, kind, pubkey, d_tag)` at all. One-live-head-per-coordinate is upheld by
the ingest path — lock, dominance comparison, soft-delete of the previous head — not by a
constraint that would reject a second live row. The only coordinate-shaped uniqueness in
the schema is the primary key of the separate `parameterized_event_watermarks` table,
which exists so replacement ordering survives the *purge* of superseded rows rather than
to police the live ones.

## Why this matters in Buzz specifically

Buzz leans on the `d` tag harder than a generic Nostr relay does, because its channel
model is built on it.

`kind.rs` defines the NIP-29 group-state kinds — 39000 metadata, 39001 admins, 39002
members, 39003 roles — all inside the addressable range, and the relay's
`emit_group_discovery_events` builds them with the channel's group id as the `d` value.
So a channel's addressable state is coordinate-keyed by channel id, and there is exactly
one live metadata event, one live member list and one live admin list per channel per
publishing key.

That is not a decorative detail. The desktop app's `get_channels`
(`desktop/src-tauri/src/commands/channels/fetch.rs`) resolves which channels an identity
belongs to by querying kind:39002 filtered on `#p` for the caller's own pubkey, then
reading **each returned event's `d` tag as the channel id**. It then fetches those
channels' kind:39000 metadata with a `#d` filter over exactly those ids. No `h` tag takes
part in either step. Channel membership discovery in Buzz is a `d`-tag traversal.

Both of those events' contents are owned elsewhere:
`capabilities-channels-channel-metadata` and `capabilities-channels-channel-membership`
are the canonical nodes and are linked above — this section names only the `d` tag's role
in them.

Several other Buzz kinds give the `d` value a distinct kind-specific meaning, recorded in
`kind.rs`'s own doc comments:

| Kind | What its `d` value is |
|---|---|
| `KIND_AGENT_ENGRAM` | An HMAC over the agent↔owner conversation key |
| `KIND_PERSONA` | The plaintext persona slug |
| `KIND_TEAM` | The team's stable id |
| `KIND_MANAGED_AGENT` | The agent's pubkey |
| `KIND_DM_VISIBILITY` | The viewer's pubkey |

`docs/nips/NIP-RS.md` — a Buzz NIP that *is* in this repository, so it can be quoted
directly — goes furthest, constraining the shape of the value rather than just its
meaning. Read-state events must carry exactly one `d` tag of the form
`read-state:<slot-id>`, where the slot id is exactly 32 lowercase hex characters; events
with zero `d` tags, more than one, or a value not beginning with `read-state:` must be
ignored. The spec explains why the shape is fixed rather than opaque: so a relay *"can
recognize a read-state coordinate structurally, from the `d` tag alone and without
decrypting anything, and apply per-coordinate protections to it."* A client that picks
another shape *"forfeits those protections silently."*

That is the generalisable lesson, and the reason this node is worth its own file: in Buzz
the `d` value is frequently **structured data a relay reads without opening the event**,
not an opaque author-chosen label.

## Use cases — when a reader needs this

- **Adding an addressable event kind.** You are choosing what its `d` value means, and
  that choice fixes how many live events an author can hold at that kind. Getting it
  wrong is the `KIND_TEAM_CATALOG` failure — every instance collapsing into one slot.
- **Writing a filter that is returning too little.** If a `#d` filter is being ignored,
  check whether the filter's `kinds` list is exclusively 30000–39999; pushdown is
  deliberately off otherwise.
- **Reasoning about "why did my event not replace the old one".** The dominance rule
  (older `created_at`, or equal with a higher-sorting id) explains a `Superseded` result
  that arrival order does not.
- **Tracing channel membership in the clients.** The chain runs through `d`, not `h`.

## Contrast: `d` versus `h`

Both are single-letter tags carrying a channel id in Buzz, which is exactly why they get
confused. They answer different questions:

| | `d` | `h` |
|---|---|---|
| Question answered | *Which slot of mine is this?* | *Which channel does this belong to?* |
| Applies to | Addressable kinds (30000–39999) | Events published inside a channel |
| Effect on storage | Part of the replacement coordinate | Channel scoping |

Buzz treats mixing them as a defect to guard against, not a harmless overlap. The relay's
channel-scoping match arm explicitly excludes user-owned and parameterized-replaceable
kinds, with the same comment repeated down the list: these are *"keyed by `(pubkey, kind,
d_tag)`"*, and *"a stray `h` tag must not channel-scope them."*

The `h` tag itself is a sibling subject, not this node's — see below.

## Scope and omissions

**This node covers** what the `d` tag is, how Buzz reads its value off the wire (the
first-tag-wins, empty-default, length-bounded rules), what the value keys (replacement,
deletion, queries), and the Buzz-specific meanings the value carries.

**It does not cover, and these are boundaries rather than silence:**

| Not covered here | Owned by |
|---|---|
| Parameterized-replaceable events as a class — their lifecycle and semantics | Feature #609 sibling task #1163 |
| Replaceable events (the two-part `(pubkey, kind)` key) | Feature #609 sibling task #1164 |
| Event tags in general — the tag array, single-letter indexing, tag conventions | Feature #609 sibling task #1155 |
| The `h` tag and channel scoping | Feature #609 sibling task #1158 |
| The `a`-tag coordinate form as a subject in its own right | Not filed as its own task at the recorded revision |
| The `d_tag` column, its index, and table shape | `layers-data-postgres-events-table`, `layers-data-postgres-indexes` |
| Channel metadata and membership event contents | `capabilities-channels-channel-metadata`, `capabilities-channels-channel-membership` |

None of the four sibling tasks above was merged when this node was authored, so they are
named by subject rather than linked — a `relationships[].target` naming an unmerged id is
a hard validation error on the branch this merges into.

**No `verification`-typed edge is declared, and that is a finding rather than an
oversight.** `launchpad/docs/corpus/verification/contracts/nostr.md` is merged and was
searched for `d tag`, `d_tag`, `NIP-33` and `parameterized`: zero hits. No merged
verification node covers the `d` tag's contract, so an edge to one would assert supporting
context that does not exist.

**Expected but not verified when this node was written:**

- **No test was found that exercises the `d`-tag length rejection end to end.** The
  1024-byte bound and its rejection message were read in `event.rs` and `ingest.rs`
  respectively, and `D_TAG_MAX_LEN` was grepped across every crate: the only other hits
  are a second enforcement of the same check, with the same message, in
  `crates/buzz-relay/src/handlers/command_executor.rs`, and a doc-comment mention in
  `crates/buzz-test-client/tests/e2e_team.rs`. No test asserting that an over-length `d`
  value is rejected was located. The bound is verified as written code, not as covered
  behaviour, and whether the two enforcement sites can drift apart was not investigated.
- **The claim that no `UNIQUE` constraint over the coordinate exists was established by
  reading `migrations/0001_initial_schema.sql` and `schema/schema.sql`, not by inspecting
  a live database.** `migrations/` was grepped for `d_tag`, returning six files; `0001`
  and `0007` were read directly and `0009`/`0011` in the regions naming the coordinate,
  while `0010` and `0019` were not opened. A constraint added by a migration not
  reflected in `schema/schema.sql` would not have been seen.
- **The NIP-RS `d`-shape rules were read from the specification document, not observed
  being enforced.** `docs/nips/NIP-RS.md` states clients MUST ignore malformed
  coordinates; whether every Buzz client does was not traced.
- **The upstream NIP-01/NIP-33 texts could not be consulted at all**, because they are
  not in this repository. Every claim above about the standard is a claim about what a
  Buzz source records, and is worded that way deliberately.
