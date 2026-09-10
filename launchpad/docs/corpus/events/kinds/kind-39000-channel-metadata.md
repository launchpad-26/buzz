---
id: events-kinds-kind-39000-channel-metadata
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a8b5021efb92264e724366d08b47b2a3839eb90a."
    entry_class: FACT
    evidence:
      - "commit a8b5021efb92264e724366d08b47b2a3839eb90a"
  - statement: "crates/buzz-core/src/kind.rs defines the constant KIND_NIP29_GROUP_METADATA: u32 = 39000, in a section commented 'NIP-29 group state (addressable range 39000-39003)', and the module's own doc comment states the file 'is the authoritative source for Buzz kind numbers'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's own unit test suite asserts is_parameterized_replaceable(39000) with the inline comment '// NIP-29 group metadata', and PARAM_REPLACEABLE_KIND_MIN/MAX are defined as 30000 and 39999 respectively, so kind 39000 falls inside Buzz's own parameterized-replaceable classification."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-01, at commit dabfcb2aaecf4fa374eda8b1232ab303a03f60ba, states under its Kinds section that 'for kind n such that 30000 <= n < 40000, events are addressable by their kind, pubkey and d tag value', which is the specification-level basis for calling 39000 addressable/parameterized-replaceable rather than regular, replaceable, or ephemeral."
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/nostr-protocol/nips/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "kind.rs's is_replaceable helper matches only kinds 0, 3, KIND_CHANNEL_METADATA (41), and 10000-19999, so 39000 is classified addressable/parameterized-replaceable rather than NIP-16 'replaceable' by Buzz's own code, consistent with the NIP-01 range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "39000 does not appear in kind.rs's AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS, or SHARED_GATED_KINDS arrays, and is_relay_only_kind's match arms list KIND_NIP43_MEMBERSHIP_LIST, KIND_CHANNEL_SUMMARY, KIND_PRESENCE_SNAPSHOT, KIND_DM_VISIBILITY, KIND_THREAD_SUMMARY, and KIND_WINDOW_BOUNDS but not KIND_NIP29_GROUP_METADATA, so none of Buzz's per-kind read-gating or relay-only-kind sets name kind 39000."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's event-submission path rejects a small explicit set of kinds by name (KIND_AUTH, KIND_MEMBER_ADDED_NOTIFICATION/KIND_MEMBER_REMOVED_NOTIFICATION as 'relay-signed only') and separately rejects any kind for which is_relay_only_kind returns true with 'restricted: relay-only kind'; kind 39000 matches neither of those checks, so nothing in the ingest handler itself refuses a client-signed kind-39000 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's generic write-path branch for a client-submitted event routes on is_replaceable / is_parameterized_replaceable / else; since is_parameterized_replaceable(39000) is true and is_replaceable(39000) is false, a client-submitted kind-39000 event would fall into the 'NIP-33 parameterized replaceable' branch, which extracts the d tag via buzz_db::event::extract_d_tag, rejects it only if the d-tag value exceeds D_TAG_MAX_LEN (1024 bytes) with 'invalid: d tag too long', and otherwise stores it via replace_parameterized_event keyed by (kind, pubkey, d_tag) -- a different call and a different replacement key than the relay's own emission path, which calls replace_addressable_event directly, keyed by (kind, pubkey, channel_id)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "crates/buzz-db/src/store/event.rs's extract_d_tag doc comment and implementation state that for parameterized replaceable kinds (30000-39999) it 'returns the first d tag's value, or \"\" if no d tag is present (per NIP-33 spec)'; a dedicated test, extract_d_tag_nip29_group_metadata, constructs a kind-39000 event carrying a d tag and asserts the value is extracted correctly, confirming kind 39000 is exercised by this generic NIP-33 extraction path specifically, not only by range."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "In practice Buzz's only observed producer of kind-39000 events is the relay itself: crates/buzz-relay/src/handlers/side_effects.rs's emit_group_discovery_events function is documented as emitting 'NIP-29 group discovery events (39000, 39001, 39002) signed by the relay keypair', called 'after group creation, metadata changes, or membership changes'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "emit_group_discovery_events builds the kind-39000 event's tags in this order: a d tag holding the channel's UUID as a string; a name tag from the channel's name; an about tag from the channel's description when non-empty; either a private tag (channel.visibility == \"private\") or an explicit public tag otherwise, with a code comment stating the public tag 'complements NIP-29's absence-of-\"private\" convention'; a hidden tag plus one p tag per member (pubkey only) when channel_type == \"dm\"; an unconditional closed tag, with a comment noting 'Buzz channels always require explicit membership'; a t tag holding the channel's channel_type; an optional topic tag; an optional purpose tag; an archived tag with value \"true\" when the channel has been archived; and optional ttl / ttl_deadline tags for ephemeral channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The tags emit_group_discovery_events writes for kind 39000 do not include NIP-29's restricted, picture, banner, livekit, or supported_kinds tags, none of which appear anywhere in that function's tag-construction block."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "NIP-29, at commit dabfcb2aaecf4fa374eda8b1232ab303a03f60ba, defines the kind-39000 group-metadata tag vocabulary as name, picture, banner and about ('basic metadata for the group for display purposes'), private ('only members can read group messages', with absence meaning anyone can read), restricted ('only members can write messages to the group', with absence meaning anyone can send), hidden ('relays should hide group metadata from non-members'), closed ('join requests are ignored'), livekit (LiveKit-powered media room support), and supported_kinds (a list of stringified kind numbers)."
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/nostr-protocol/nips/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "The shared helper emit_addressable_discovery_event, which emit_group_discovery_events calls for the 39000 tag set, signs the event with EventBuilder::new(Kind::Custom(kind as u16), \"\").tags(tags)...sign_with_keys(&state.relay_keypair), so a kind-39000 event's content field is always the empty string in Buzz's own emission path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "emit_addressable_discovery_event stores the signed event via state.db.replace_addressable_event(tenant.community(), &event, Some(channel_id)), i.e. with channel_id set rather than None."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "crates/buzz-db/src/store/replaceable.rs's replace_addressable_event doc comment states it atomically replaces 'NIP-16 kinds (0, 3, 41, 10000-19999) and NIP-29 discovery state (39000-39002, called from side_effects.rs)', keeping 'only the event with the highest created_at per (kind, pubkey, channel_id)', with 'same-second ties... broken by lowest event id (NIP-16 deterministic ordering)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "emit_group_discovery_events's own doc comment states that events are 'stored channel-scoped (channel_id = Some(...)) so that existing access control applies -- private channel member lists are only visible to members', and separately notes that channel-scoped storage means a live global subscription such as {kinds:[39000]} 'won't receive these events via fan-out' and that 'Clients discover groups via historical REQ queries', calling live push for open-channel discovery 'a future enhancement'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Because channel-scoped storage is what gates a kind-39000 event's visibility (per the FACT above) rather than any of kind.rs's AUTHOR_ONLY_KINDS/P_GATED_KINDS/SHARED_GATED_KINDS sets, a private channel's kind-39000 metadata is readable only by that channel's members through the same access-control path as any other channel-scoped event, not through a kind-specific gate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.75
  - statement: "crates/buzz-acp/src/relay.rs builds a filter with .kind(Kind::Custom(buzz_core::kind::KIND_NIP29_GROUP_METADATA as u16)) and .custom_tags(d_tag, d_values) to fetch kind-39000 metadata for a set of discovered channel UUIDs, as step 2 of a channel-discovery flow, immediately followed by a comment 'Fetch metadata (kind:39000) for discovered channels.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
  - statement: "crates/buzz-acp/src/pool.rs's fetch_channel_info_once function queries the same kind, KIND_NIP29_GROUP_METADATA, filtered by a single d tag equal to the channel UUID, documented as fetching 'the current kind-39000 metadata with one bounded request' for 'prompt-turn refreshes when cached metadata is already available as a graceful fallback'."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs"
  - statement: "This repository's root AGENTS.md states: 'Channels use h tags (NIP-29 group tag), not e tags... Addressable events that describe a channel carry its id in their d tag instead: kind:39000 (metadata), kind:39001, kind:39002 (membership).'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's test_nip29_standard_client_flow queries Filter::new().kind(Kind::Custom(39000)) after creating a channel, asserts a matching event is found by its d tag, and asserts that event carries a name tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs's test_dm_discovery_events_emitted subscribes to Kind::Custom(39000) for a DM channel and asserts the received event's tags include both hidden and private."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "No comment or constant in kind.rs records a prior kind number that KIND_NIP29_GROUP_METADATA (39000) replaced or was renumbered from, unlike several other Buzz-custom kinds in the same file (e.g. KIND_STREAM_MESSAGE_V2's comment 'V1 used kind:10002 -- wrong') that do carry such a history."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "launchpad/docs/corpus/templates/event-kind.md (corpus-template-event-kind) is the merged, sanctioned template for a node documenting one Nostr event kind, requiring nine sections (title/kind identity, referenced NIP, kind range and delivery classification, tag shape, content-field semantics, access control and storage model, worked example, versioning and supersession, relationships) and stating that a realized instance most plausibly carries type: interfaces-events and should declare an implements relationship targeting corpus-template-event-kind itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "corpus-template-event-kind is loadable from origin/launchpad at the revision this node records (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists launchpad/docs/corpus/templates/event-kind.md with id corpus-template-event-kind), and no other node under launchpad/docs/corpus/events/ exists yet, so an implements edge to it is the only relationship target available for this node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
relationships:
  - type: implements
    target: corpus-template-event-kind
---

# Event kind 39000: channel metadata (NIP-29 group metadata)

## 1. Title and kind identity

**Kind 39000**, constant `KIND_NIP29_GROUP_METADATA` in `crates/buzz-core/src/kind.rs`.
Buzz uses it to publish the discoverable metadata for one channel — the
NIP-29 "group metadata" event. This is implemented and shipping today; it is
not a proposed kind.

## 2. Referenced NIP

[NIP-29](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md)
("Relay-based Groups"), the group-metadata event (kind `39000`). This
repository's root `AGENTS.md` cites the same NIP as the basis for Buzz's
channel scoping (`h` tags for in-channel events, `d` tags for the addressable
events — including this one — that describe a channel).

## 3. Kind range and delivery classification

39000 falls in NIP-01's addressable/parameterized-replaceable range
(`30000 <= n < 40000`, "events are addressable by their kind, pubkey and d
tag value"). Buzz's own `is_parameterized_replaceable` helper agrees — a
dedicated unit test asserts `is_parameterized_replaceable(39000)` — and
39000 is absent from `is_replaceable`'s match arms (which cover kinds 0, 3,
41, and 10000-19999) and outside the ephemeral range (20000-29999). So it is
**addressable / parameterized-replaceable**, not regular, NIP-16 replaceable,
or ephemeral. It is stored (never dropped), and superseded per `d` tag rather
than accumulated as a stream of events.

## 4. Tag shape

Buzz's own producer, `emit_group_discovery_events` in
`crates/buzz-relay/src/handlers/side_effects.rs`, builds these tags for every
kind-39000 event, in this order:

| Tag | Cardinality | Value |
|---|---|---|
| `d` | exactly one | the channel's UUID, as a string — this is the addressing key |
| `name` | exactly one | the channel's display name |
| `about` | zero or one | the channel's description, only when non-empty |
| `private` | zero or one | present when the channel's visibility is `"private"` |
| `public` | zero or one | present when the channel is not private — Buzz's own explicit complement to NIP-29's "absence of `private` means public" convention |
| `hidden` | zero or one | present only when `channel_type == "dm"` |
| `p` (pubkey only) | zero or more | one per member, only when `channel_type == "dm"` — lets clients resolve DM participant names without a separate kind-39002 fetch |
| `closed` | exactly one | always present — "Buzz channels always require explicit membership" |
| `t` | exactly one | the channel's `channel_type` (e.g. `stream`, `forum`, `dm`) |
| `topic` | zero or one | present when the channel has a non-empty topic |
| `purpose` | zero or one | present when the channel has a non-empty purpose |
| `archived` | zero or one | value `"true"`, present when the channel has been archived |
| `ttl` | zero or one | seconds, present for ephemeral channels with a TTL |
| `ttl_deadline` | zero or one | RFC 3339 timestamp, present alongside `ttl` |

**No `h` tag.** Per this repository's own `AGENTS.md`, an addressable event
that *describes* a channel carries the channel's id in its `d` tag instead of
scoping into the channel via `h`.

**Divergence from NIP-29's own tag vocabulary.** NIP-29 additionally defines
`picture`, `banner`, `restricted`, `livekit`, and `supported_kinds` for
kind-39000 group metadata. None of these appear in Buzz's tag-construction
code. This is recorded as a gap below (*Scope and omissions*), not resolved
here — whether Buzz should emit them is a product question this node does
not decide.

**Validation rules.** No kind-39000-specific tag validator exists. What does
apply is the generic NIP-33 machinery every parameterized-replaceable kind
shares: `extract_d_tag` returns the first `d` tag's value, or `""` if none is
present ("per NIP-33 spec") — a missing `d` tag is not rejected, it is stored
as an empty-string key — and a dedicated test,
`extract_d_tag_nip29_group_metadata`, exercises this specifically for kind
39000. The only hard rejection at ingest is a `d`-tag value longer than
`D_TAG_MAX_LEN` (1024 bytes): `"invalid: d tag too long"`.

## 5. Content field semantics

**Always the empty string.** The shared emission helper,
`emit_addressable_discovery_event`, constructs the event as
`EventBuilder::new(Kind::Custom(kind as u16), "")` — every field this kind
carries lives in tags, none in `content`.

## 6. Access control and storage model

**Stored, addressable, keyed by `(kind, pubkey, channel_id)`.**
`replace_addressable_event`'s own doc comment states it covers "NIP-16 kinds
... and NIP-29 discovery state (39000-39002)", keeping only the event with
the highest `created_at` per `(kind, pubkey, channel_id)`, with same-second
ties broken by lowest event id (NIP-16 deterministic ordering).

**No kind-specific read gate.** Kind 39000 is a member of none of
`AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`, or the
`is_relay_only_kind` set. Visibility instead follows **channel-scoped
storage**: `emit_group_discovery_events`'s own doc comment states events are
"stored channel-scoped (`channel_id = Some(...)`) so that existing access
control applies — private channel member lists are only visible to members."
The reasoning that this therefore gates a private channel's kind-39000
metadata the same way is this node's own inference (see the `INFERENCE`
entry above, confidence 0.75) rather than a sentence read directly off one
source.

**Client-signed submission is not rejected by kind, and would take a
different storage path than the relay's own.** Ingest's explicit per-kind
rejections (`KIND_AUTH`, the two membership-notification kinds) and its
`is_relay_only_kind` check do not name 39000, so nothing at the ingest
handler itself refuses a client-signed kind-39000 event on the basis of its
kind alone. Were one submitted, ingest's generic write-path routing
(`is_replaceable` / `is_parameterized_replaceable` / else) would send it into
the parameterized-replaceable branch — `replace_parameterized_event`, keyed
by `(kind, pubkey, d_tag)` — which is a **different function and a different
replacement key** than `replace_addressable_event`'s `(kind, pubkey,
channel_id)` keying that the relay's own `emit_group_discovery_events` path
uses directly. In practice, though, the only observed producer is the relay
itself, signing with its own keypair after channel creation, metadata
changes, or membership changes; whether these two paths could ever produce
two live rows for the same channel is not established here (see *Scope and
omissions*).

**No live fan-out to a global subscription.** Because storage is
channel-scoped, a subscription such as `{kinds:[39000]}` with no channel
scope will not receive these events live. Clients discover channels via
historical `REQ` queries instead; the relay's own comment calls live push
for open-channel discovery "a future enhancement."

**Not P-gated, not search-indexed specially.** No FTS/search-tsv treatment
specific to kind 39000 was found, and none is expected — it is not a member
of `P_GATED_KINDS`, which is the set that forces a null `search_tsv`.

**Audit.** No audit-log-specific handling for kind 39000 was found or
searched for beyond the ordinary persistent-event dispatch path
(`dispatch_persistent_event`, called from `emit_addressable_discovery_event`);
this is named as a gap rather than a confirmed absence, see *Scope and
omissions*.

**Producers.** The relay, via `emit_group_discovery_events` /
`emit_addressable_discovery_event`, signed with the relay keypair.

**Consumers.** `crates/buzz-acp/src/relay.rs` (channel-discovery flow: query
kind 39000 by `d` tag for a batch of discovered channel UUIDs) and
`crates/buzz-acp/src/pool.rs`'s `fetch_channel_info_once` (per-agent-turn
channel-info refresh, one bounded request filtered by a single `d` tag).
Both are internal to the agent-harness surface (`buzz-acp`); no other
in-repository consumer was found.

## 7. Worked example

A public, non-DM stream channel, no topic/purpose/TTL set, not archived:

```json
{
  "id": "...",
  "pubkey": "<relay pubkey, hex>",
  "kind": 39000,
  "content": "",
  "created_at": 1735689600,
  "tags": [
    ["d", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["name", "engineering"],
    ["public"],
    ["closed"],
    ["t", "stream"]
  ],
  "sig": "..."
}
```

A private DM channel between two members:

```json
{
  "id": "...",
  "pubkey": "<relay pubkey, hex>",
  "kind": 39000,
  "content": "",
  "created_at": 1735689600,
  "tags": [
    ["d", "9c858901-8a57-4791-81fe-4c455b099bc9"],
    ["name", "alice, bob"],
    ["private"],
    ["hidden"],
    ["p", "<alice pubkey, hex>"],
    ["p", "<bob pubkey, hex>"],
    ["closed"],
    ["t", "dm"]
  ],
  "sig": "..."
}
```

Both examples are illustrative — assembled from the tag-construction rules
in *Tag shape* above and the `d`-tag/query shape confirmed by
`test_nip29_standard_client_flow` and `test_dm_discovery_events_emitted` —
not copied from a captured wire event.

## 8. Versioning and supersession

No evidence of a prior kind number for channel metadata was found. Unlike
several other Buzz-custom kinds in the same file (for example
`KIND_STREAM_MESSAGE_V2`'s comment recording that "V1 used kind:10002 —
wrong"), `KIND_NIP29_GROUP_METADATA`'s declaration and surrounding comments
carry no renumbering history. Not applicable.

## 9. Relationships

This node declares `implements: corpus-template-event-kind` — it is a
realized instance of the event-kind template, not an independent
restatement of that template's required sections. No other node under
`launchpad/docs/corpus/events/` exists yet on `origin/launchpad` at the
recorded revision to link as a sibling (kind 39001 group-admins and kind
39002 group-members are the natural `references` targets once their own
nodes are authored — see *Scope and omissions*).

## Scope and omissions

**This node covers** kind 39000 as a protocol-and-registry citizen: its
number, its NIP-29 basis, its NIP-01 range classification, the exact tag
shape Buzz's own code constructs, its content-field semantics, its storage
and access-control model, its producers and consumers in this repository,
and its existing conformance coverage.

**It does not cover:**

| Not covered here | Owned by |
|---|---|
| Kind 39001 (group admins) and kind 39002 (group members) — each is its own event kind and its own corpus node | separate, not-yet-filed corpus tasks |
| Any consumer-facing operation surface built on top of kind 39000 (a `buzz-cli` subcommand, a typed `buzz-sdk` builder) | an "interface"-typed node, per `corpus-template-event-kind`'s own *Boundary against interface* section |
| Why Buzz does not emit NIP-29's `restricted`, `picture`, `banner`, `livekit`, or `supported_kinds` tags | not established here — named as a gap, not a product decision this node makes |
| Whether any audit-log-specific handling exists for kind 39000 beyond the ordinary persistent-event dispatch path | not searched for beyond `dispatch_persistent_event`; named as a gap below |

**Expected but not verified when this node was written:**

- **Whether a kind-39000 event is ever actually submitted client-side (as
  opposed to only relay-signed) was not tested against a running relay** —
  the claim that ingest does not reject one by kind is read directly from
  `ingest.rs`'s source, not confirmed by submitting one and observing the
  outcome.
- **The `INFERENCE` in *Access control and storage model*, that private-channel
  kind-39000 visibility is enforced purely through channel-scoped storage
  rather than any additional kind-specific check, was not traced through the
  full read path** (REQ historical delivery, live fan-out, COUNT, the
  `ids`-lookup gate) the way `P_GATED_KINDS`' own doc comment states its
  enforcement points explicitly; it rests on `emit_group_discovery_events`'s
  doc comment plus the absence of 39000 from every named gating set.
- **Whether any generated corpus view or knowledge-crate serialization
  consumes this node's `relationships` edge was not tested** — no such
  consumer was found to test against, matching the same gap the event-kind
  template itself names for its own `implements`-targeting guidance.
- **Whether a client-submitted kind-39000 event (routed through
  `replace_parameterized_event`, keyed by `d_tag`) and the relay's own
  discovery event for the same channel (routed through
  `replace_addressable_event`, keyed by `channel_id`) could ever coexist as
  two live rows for one channel was not tested.** Both paths were read from
  source; no integration test exercising a client-submitted kind-39000 event
  was found or run.
