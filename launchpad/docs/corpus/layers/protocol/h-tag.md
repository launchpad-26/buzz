---
id: layers-protocol-h-tag
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
  - statement: "The repository's root contributor guide states that channels use `h` tags (the NIP-29 group tag) rather than `e` tags, and that filters and queries must scope to `h` tags when operating within a channel."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "CLAUDE.md"
  - statement: "An `h` tag's value is a channel UUID: `extract_channel_id` walks the event's tags, returns the first `h` tag whose content parses as a UUID, and returns None when no `h` tag is present or its value is not a valid UUID."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "Twenty-three kinds are listed in `requires_h_channel_scope` — the stream-message family, canvas, the forum kinds, six NIP-29 admin kinds, the huddle lifecycle kinds and huddle guidelines — and an event of one of those kinds that resolves to no channel is rejected at ingest with `invalid: channel-scoped events must include an h tag`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Forty-seven kinds are listed in `is_global_only_kind`, and ingest sets `channel_id = None` for them after channel extraction has already run, so an `h` tag on one of those kinds does not scope it to a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The `is_global_only_kind` list carries the same rationale comment repeated across its groups — that these kinds are user-owned or community-global state keyed by (pubkey, kind[, d_tag]) and that \"a stray `h` tag must not channel-scope them\" — including for the NIP-34 git kinds, which scope by `a` tag instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A unit test asserts across every kind value from 0 to 65535 that no kind is simultaneously global-only and channel-scoped, so the two lists are proven disjoint rather than merely intended to be."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Reactions (kind:7) and standard deletions (kind:5) carry no `h` tag; ingest derives their channel from the `e`-tagged target event's stored `channel_id`, and gift-wrapped events are always resolved to no channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`filter_match_one` applies an `#h` fallback that consults `StoredEvent.channel_id` only when the event carries no `h` tag at all; when the event does carry `h` tags they are authoritative and a non-matching value is a strict rejection."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "The test `h_tag_fallback_uses_stored_channel_id` covers the derived case in both directions, including the cross-channel leakage guard that an explicit `h` tag pointing elsewhere must not be overridden by a matching stored `channel_id`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "The channel resolved at ingest is persisted as a nullable `channel_id UUID` column on the partitioned `events` table and is carried in memory as `StoredEvent.channel_id: Option<Uuid>`, so \"global\" is represented as SQL NULL rather than as a sentinel channel."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-core/src/event.rs"
  - statement: "That column is indexed community-leading — `idx_events_community_channel_created` on (community_id, channel_id, created_at DESC, id) — so a channel timeline read is index-served within one community rather than scanning partitions."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "migrations/0001_initial_schema.sql"
  - statement: "On the read path the relay reads channel scope out of a request's `#h` filter values: a single-value `#h` filter collapses to one `EventQuery::channel_id`, a multi-value one keeps NIP-01 OR semantics and is applied as a channel set, a filter with no `#h` constraint makes the subscription community-global, and the aggregate number of `#h` values across a request is budget-capped before any UUID parsing or membership I/O."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "`is_global_only_kind`'s own doc comment records a known limitation: because Nostr events are signed, the stray `h` tag cannot be stripped from the stored event, and the read-path filter's treatment of explicit `h` tags as authoritative means such a tag can still match an `#h` query — an unresolved follow-up in the filter layer, not a settled contract."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Two NIP-29 kinds sit outside both lists: kind:9007 create-group treats the `h` tag as an optional client-chosen UUID because it creates the channel, and kind:9021 join-request reads the `h` tag through a separate open-only validation path rather than through `requires_h_channel_scope`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A resolved channel is checked against the connection's authorization before the event is accepted: `check_token_channel_access` rejects a channel-scoped token whose allowed set omits the channel, and a channel-scoped token publishing an event that resolves to no channel is rejected outright."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The merged principle node states that a client-supplied `#h` channel tag is checked against the host-derived community's own channel set and narrows which channel inside the already-resolved community is meant, and can never cause a different community to be resolved."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "No upstream numbered NIP specification text is present in this repository — docs/nips/ holds twenty-two Markdown files, all of them Buzz's own two-letter NIPs, and none matching the NIP-<number>.md form — so any claim about what upstream NIP-29 itself requires cannot rest on a file in this tree."
    entry_class: FACT
    evidence:
      - "list_dir(docs/nips/, pattern='NIP-[0-9]+.md') -> 0 matches out of 22 .md files present"
  - statement: "Issue #1158 requires that this node define the term in one sentence before deeper explanation, state what it must not be confused with, link rather than duplicate neighbouring nodes, and use examples only to clarify the concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1158 definition of done"
relationships:
  - type: references
    target: capabilities-channels-channel
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-core
---

# The `h` tag

## Definition

**The `h` tag is the NIP-29 group tag Buzz uses to say which channel an event belongs
to, and its value is that channel's UUID.** It is the routing directive of the protocol
layer: the relay reads it at ingest, resolves it to a channel, and stores the result as
the event's `channel_id`. Everything downstream that means "in this channel" — timeline
reads, live fan-out topics, membership checks, token scoping — reads that resolved
value, not the tag directly.

The repository's root contributor guide states the rule in one line: channels use `h`
tags, not `e` tags, and filters and queries must scope to `h` tags when operating within
a channel. `e` tags reference *another event* (a thread parent, a reaction target); an
`h` tag references a *container*.

**What it is not.** The `h` tag is **not** the security boundary. Buzz's security
boundary is the community, resolved solely from the connection's Host header —
`architecture-principles-community-is-security-boundary` is the canonical statement of
that, and it names the `#h` tag explicitly as one of the client-supplied signals that
must never override the host-derived binding. The relationship between the two is
containment, not competition: the community is resolved first and from a source the
client does not control, and the `h` tag then *narrows* within that already-resolved
community, choosing which of its channels is meant. A channel UUID from another
community does not widen anything — it simply fails to resolve against the bound
community's channel set. Reading the `h` tag as "the thing that keeps data separate" is
the error this section exists to prevent; it is the thing that keeps data *organized*
inside a separation that was already established.

It is also not the only tag that scopes an event. NIP-34 git kinds scope by `a` tag,
addressable kinds are keyed by `d` tag, and `p` tags address people. Those are their own
nodes.

## The tag is honoured per kind, not universally

The single most important thing to understand about the `h` tag is that **carrying one
does not make an event channel-scoped.** Whether the relay honours it is decided by the
event's kind, in three groups.

| Group | How the channel is resolved | Size |
|---|---|---|
| Requires an `h` tag | From the tag; an event resolving to no channel is rejected | 23 kinds |
| Always global | Forced to no channel *after* extraction has already run | 47 kinds |
| Derived or special | From another event, or by a kind-specific path | the rest |

**Requires an `h` tag** (`requires_h_channel_scope`) — the stream-message family, canvas,
the forum kinds, six NIP-29 admin kinds, and the huddle lifecycle kinds plus huddle
guidelines. Publishing one
of these without a resolvable channel fails with `invalid: channel-scoped events must
include an h tag`.

**Always global** (`is_global_only_kind`) — profiles, text notes, contact lists, the
NIP-51 lists and sets, the NIP-34 git kinds, personas and team definitions, the
moderation and relay-admin command kinds, and more. Ingest extracts the channel first
and *then* overwrites it with none for these kinds. The list's own comments repeat the
reason at each group: this is user-owned or community-global state keyed by
`(pubkey, kind[, d_tag])`, and **a stray `h` tag must not channel-scope it**. That
phrasing is the tell — the code is defending against a client that attaches an `h` tag
to a kind where it has no business being, not merely declining to look for one.

The two lists are proven disjoint by an exhaustive test over every kind value from 0 to
65535, so "both channel-scoped and global-only" is not a state a kind can reach.

**Derived or special.** Reactions (kind:7) and standard deletions (kind:5) carry no `h`
tag at all; the relay looks up their `e`-tagged target event and takes *its* stored
`channel_id`. Gift-wrapped events always resolve to no channel. Two NIP-29 kinds sit
outside both lists deliberately: kind:9007 create-group treats the `h` tag as an
optional client-chosen UUID, because it is the event that brings the channel into
existence, and kind:9021 join-request reads the tag through a separate open-only
validation path.

## The read path reads the tag back

Because two of those three groups produce events with no `h` tag on the wire but a real
`channel_id` in storage, the filter layer cannot match `#h` on tags alone. `filter.rs`
carries a fallback for exactly this: when an `#h` filter finds no matching tag, it
consults the stored `channel_id` — **but only when the event carries no `h` tags at
all.** If the event does carry `h` tags, those are authoritative and a mismatch is a
strict rejection. That asymmetry is the leakage guard: an event whose tag says channel A
and whose stored `channel_id` says channel B must not be delivered to a subscriber
asking for B. A unit test covers all four corners of it, including that guard.

On the request side, the relay reads channel scope out of a subscription's `#h` filter
values. One value collapses to a single-channel database query; several keep NIP-01's OR
semantics and become a channel set; a filter with no `#h` constraint makes the whole
subscription community-global. The aggregate number of `#h` values in a request is
budget-capped *before* any UUID parsing or membership I/O, so a request cannot spend
relay work by naming thousands of channels.

## What the resolved value becomes

The channel resolved from the tag is persisted as a nullable `channel_id UUID` column on
the partitioned `events` table, and carried in memory as
`StoredEvent.channel_id: Option<Uuid>`. **Global is represented as SQL NULL**, not as a
sentinel channel — which is why the "always global" group above is expressed as an
overwrite to `None` rather than as a redirect. That column is indexed community-leading
(`idx_events_community_channel_created`), so reading one channel's timeline is
index-served inside one community.

The resolved value is also what authorization is checked against: a channel-scoped token
is rejected if the resolved channel is outside its allowed set, and rejected again if
the event resolves to no channel at all — otherwise a channel-restricted token could
publish global events and escape its own restriction.

## Why this matters to a reader

- **Writing a client or an agent:** know which group your kind falls in before adding an
  `h` tag. Adding one to a global-only kind is silently ignored for scoping purposes and
  is not a way to make user-owned state channel-local.
- **Writing a query:** a `#h` filter is the only way to scope a read to a channel, and
  it works for reactions and deletions only because of the stored-`channel_id` fallback
  — not because those events carry the tag.
- **Adding a new kind:** the disjointness test will catch a kind added to both lists, but
  nothing catches a kind added to *neither*. That kind will be scoped by whatever `h`
  tag a client happens to send, with no requirement and no prohibition.

## Scope and omissions

**This node covers** what the `h` tag is, that its value is a channel UUID, how ingest
resolves it into a stored `channel_id`, which kinds honour it and which ignore it, how
the read path matches `#h` including the derived-channel fallback, and the boundary
between the `h` tag as a scoping mechanism and the community as the security boundary.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What a channel *is* as a product capability — types, membership, metadata, deletion | `capabilities-channels-channel` and its siblings |
| The community security boundary itself and its enforcement points | `architecture-principles-community-is-security-boundary` |
| The `d`, `e`, `p` tags and the tag vocabulary as a whole | sibling protocol-layer nodes, unmerged at this revision |
| The full kind registry and each kind's meaning | `crates/buzz-core/src/kind.rs` |
| Live fan-out topic construction from a resolved channel | `implementation-crates-buzz-relay`, and the pubsub crate's own node |
| Whether the stray-`h`-tag read-path limitation should be closed, and how | unresolved in the code; see below |

**An unresolved item, left explicit.** `is_global_only_kind`'s doc comment records that
because Nostr events are signed, a stray `h` tag cannot be stripped from the stored
event, and that the read-path filter's treatment of explicit `h` tags as authoritative
therefore lets such a tag still match an `#h` query. The comment calls this a known
limitation affecting all global-only kinds and says it *should be addressed in the
filter layer as a follow-up*. This node reports that as the code's own open question and
does not resolve it.

**Expected but not verified when this node was written:**

- **No test was run.** Every claim here comes from reading source at the recorded
  revision. The unit tests cited (`global_only_and_channel_scoped_are_disjoint`,
  `h_tag_fallback_uses_stored_channel_id`, and the create-group and join-request
  assertions) were read, not executed, and no live relay was exercised.
- **No end-to-end test was found that publishes a stray `h` tag on a global-only kind
  and then queries `#h` for it** — the exact scenario the limitation above describes. Its
  practical reach is therefore recorded from the doc comment's own words, not measured.
- **The `h` tag's behaviour against upstream NIP-29's text was not checked**, because no
  upstream numbered NIP specification exists in this repository: `docs/nips/` holds
  twenty-two Markdown files and every one of them is a Buzz-authored two-letter NIP.
  Every claim above is therefore about what *Buzz* does, verified against Buzz's own
  source, and none of it should be read as a statement about what upstream NIP-29
  requires.
- **The desktop, mobile and CLI clients were not surveyed** for how they construct `h`
  tags. This node describes the relay's contract; whether every client honours it
  consistently was not established.
