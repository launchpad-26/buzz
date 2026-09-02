---
id: events-kinds-kind-39001-channel-admins
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
  - statement: "Kind 39001 is Buzz's constant KIND_NIP29_GROUP_ADMINS, defined as `pub const KIND_NIP29_GROUP_ADMINS: u32 = 39001;` with the doc comment 'NIP-29: Addressable group admins list.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's module doc comment states it 'is the authoritative source for Buzz kind numbers,' so KIND_NIP29_GROUP_ADMINS = 39001 is the canonical registry entry for this kind, not one of several competing definitions."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines PARAM_REPLACEABLE_KIND_MIN = 30000 and PARAM_REPLACEABLE_KIND_MAX = 39999, and `is_parameterized_replaceable(kind)` returns `kind >= PARAM_REPLACEABLE_KIND_MIN && kind <= PARAM_REPLACEABLE_KIND_MAX`; 39001 lies within that inclusive range, so `is_parameterized_replaceable(39001)` evaluates `true` by direct arithmetic on the function's own definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's own inline unit test asserts `is_parameterized_replaceable(39000)` and a value of 39999 are both `true`, and `is_parameterized_replaceable(29999)` and `40000` are both `false`, directly bracketing 39001 inside the tested true range rather than leaving it to an untested extrapolation of the boundary values alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's `is_replaceable(kind)` matches only `0 | 3 | KIND_CHANNEL_METADATA(41) | 10000..=19999`, and `is_ephemeral(kind)` matches only `20000..=29999`; 39001 matches neither pattern, so kind 39001 is parameterized-replaceable/addressable only — not NIP-16-replaceable and not ephemeral."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "39001 is a member of ALL_KINDS (Buzz's registered-kind list, used by the `no_duplicate_kind_values` test to guard against two constants sharing one integer), placing it under that duplicate-detection check alongside every other registered kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-01 defines the addressable/parameterized-replaceable category (30000 <= n < 40000) as keyed by `(pubkey, kind, d-tag)`, with only the latest `created_at` retained per key, which is the external specification kind.rs's own `is_parameterized_replaceable` range implements for 39001."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "NIP-29 documents kind 39001 in its own group-metadata-events section as the list of group admins, giving each admin an entry as a `p` tag carrying the admin's pubkey followed by the admin's roles."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "This repository's root AGENTS.md states that addressable events describing a channel carry the channel's id in their `d` tag rather than an `h` tag, and names kind:39001 explicitly alongside kind:39000 and kind:39002 as this category."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Buzz's producer of kind 39001 is `emit_group_discovery_events`, a public async function in side_effects.rs whose own doc comment states it emits 'NIP-29 group discovery events (39000, 39001, 39002) signed by the relay keypair,' called 'after group creation, metadata changes, or membership changes.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Within `emit_group_discovery_events`, the kind 39001 event's tags are built as exactly one `[\"d\", <channel-id-string>]` tag followed by zero or more `[\"p\", <pubkey-hex>, <role>]` tags, one per channel member whose role is `\"owner\"` or `\"admin\"` (members with any other role are excluded from the tag list), and the event's content is the empty string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The relay's `MemberRole` enum (crates/buzz-core/src/channel.rs) defines exactly five roles — Owner, Admin, Member, Guest, Bot — with canonical string forms \"owner\", \"admin\", \"member\", \"guest\", \"bot\"; only the first two ever appear as a `p` tag's role value in a kind 39001 event, per the `role == \"owner\" || role == \"admin\"` filter in side_effects.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`buzz-admin`'s `reconcile_channels` subcommand independently builds and republishes a kind 39001 event using the identical tag shape (one `d` tag plus one `p` tag per owner/admin member) as a relay-signed backfill/repair path, separate from `emit_group_discovery_events`."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "`emit_group_discovery_events` is called (directly or via a wrapping handler) from `handle_put_user`, `handle_remove_user`, `handle_edit_metadata`, `handle_create_group`, `handle_join_request`, and `handle_leave_request` in side_effects.rs; from `handle_dm_open` and `handle_dm_add_member` in command_executor.rs; from `send_moderation_notice` in moderation_notices.rs; and from `publish_nip43_delta` in side_effects.rs — so a kind 39001 refresh follows NIP-29 group-state changes, DM-channel creation/membership changes, moderation-notice DM setup, and NIP-43 relay-membership deltas alike."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "kind 39001 is stored via `Db::replace_addressable_event`, whose own doc comment states it handles 'NIP-16 kinds (0, 3, 41, 10000-19999) and NIP-29 discovery state (39000-39002, called from side_effects.rs),' keeping only the event with the highest `created_at` per `(kind, pubkey, channel_id)` — same-second ties broken by lowest event id — and passed `channel_id: Some(...)` for every 39001 write, so a stored 39001 event is always channel-scoped rather than global."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs"
  - statement: "39001 is not a member of any of kind.rs's four named read-gate sets — `AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, `P_GATED_KINDS`, and `SHARED_GATED_KINDS` — each of which was read directly and does not list KIND_NIP29_GROUP_ADMINS or 39001 among its members."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "`emit_group_discovery_events`'s own doc comment states its events 'are stored channel-scoped (`channel_id = Some(...)`) so that existing access control applies — private channel member lists are only visible to members,' and separately notes that channel-scoped storage means a live global subscription such as `{kinds:[39000]}` will not receive these events via fan-out, so clients discover them via historical REQ queries scoped to the channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Because 39001 carries no kind-specific entry in any of the four named gate sets, read access to a stored 39001 event is governed entirely by the channel's own membership-based access control (world-readable for a public channel, member-only for a private one) rather than by a 39001-specific rule — this is a generalization from the absence of a dedicated gate plus the doc comment above, not a claim traced through the private-channel membership-check code path itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
    confidence: 0.75
  - statement: "Every persistent event dispatched through `dispatch_persistent_event` — the function `emit_group_discovery_events` uses for a newly inserted 39001 event — unconditionally calls `enqueue_event_created_audit` before scheduling fan-out, so a stored kind 39001 event is written into the hash-chain audit log the same as any other stored event, with no kind-based exclusion in that code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "`dispatch_persistent_event_inner` fans a newly stored 39001 event out on `EventTopic::Channel(channel_id)` (never `EventTopic::Global`, since `stored_event.channel_id` is always `Some(...)` for this kind), reaching only subscribers already live-subscribed to that channel — consistent with, and the mechanism behind, the doc comment's claim that a global kind-only live subscription does not receive these events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "No file under `desktop/src`, `web/src`, `mobile/lib`, `crates/buzz-cli/src`, or `crates/buzz-sdk/src` references the literal `39001` or the name `GROUP_ADMINS`, so no client-side consumer of kind 39001 exists in this repository at the recorded revision."
    entry_class: FACT
    evidence:
      - "shell(grep -rn \"39001\\|GROUP_ADMINS\" desktop/src web/src mobile/lib crates/buzz-cli/src crates/buzz-sdk/src) -> no matches"
  - statement: "No test in the repository — under `crates/buzz-relay/tests`, `crates/buzz-test-client`, or any inline `#[cfg(test)] mod tests` — references `KIND_NIP29_GROUP_ADMINS` or the literal `39001`, so kind 39001 has no dedicated conformance or integration test coverage today; it is exercised only incidentally, if at all, by any test that happens to trigger `emit_group_discovery_events`."
    entry_class: FACT
    evidence:
      - "shell(grep -rn \"KIND_NIP29_GROUP_ADMINS\\|39001\" crates/buzz-relay/tests crates/buzz-test-client) -> no matches"
  - statement: "Whether any test indirectly exercises kind 39001 by asserting on the side effects of a NIP-29 put-user/remove-user/edit-metadata/create-group/join-request/leave-request event (rather than asserting on the 39001 event itself) was not checked line-by-line against every test in `crates/buzz-relay`'s test modules — this node states the absence of a 39001-specific assertion as fact, and leaves open whether an indirect, unasserted exercise of the code path exists."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "self-review while authoring this node, recorded as a named gap rather than resolved by an exhaustive read of every test module"
---

# Kind 39001 — Channel Admins (NIP-29 Group Admins List)

## 1. Title and kind identity

**Kind 39001**, Buzz constant `KIND_NIP29_GROUP_ADMINS` (`crates/buzz-core/src/kind.rs`),
value `39001`. This node's `type` is `interfaces-events` — the corpus-surface value
`node.schema.json` reserves for the protocol/event surface, per
`launchpad/docs/corpus/templates/event-kind.md`'s own guidance for a real
event-kind instance.

This kind is implemented and shipping today, not proposed: `emit_group_discovery_events`
(see §6) actively produces it as part of ordinary channel and NIP-29 group-state
handling.

## 2. Referenced NIP

**NIP-29** (`nostr-protocol/nips`, `29.md`), the group/channel and moderation
specification. NIP-29 defines kind `39001` as the addressable admins list for a
group, with one `p` tag per admin carrying the admin's pubkey and role(s). This
repository's root `AGENTS.md` cites the same NIP-29 `h`-tag convention as the
basis for Buzz's channel scoping generally, and separately names kind `39001`
explicitly (alongside `39000` and `39002`) as one of the addressable events that
carry a channel's id in a `d` tag instead.

There is no `docs/nips/NIP-XX.md` proposal document for this kind, because it is
not a Buzz-invented protocol extension — NIP-29 is already its governing external
specification. This corpus node is the reference lookup for Buzz's own
implementation of that specification, not a substitute spec document.

## 3. Kind range and delivery classification

**Addressable / parameterized-replaceable** (NIP-01's 30000–39999 range), keyed
by `(pubkey, kind, d-tag)` per NIP-01, with only the latest `created_at` retained.
`kind.rs`'s `is_parameterized_replaceable` implements exactly this range check,
and 39001 falls inside it — directly verified against the function's own
definition and cross-checked against `kind.rs`'s inline unit test, which asserts
`true` at both 39000 and 39999 (the range immediately surrounding 39001) and
`false` just outside that range at 29999 and 40000.

It is **not** a NIP-16 replaceable kind (`is_replaceable` matches only `0`, `3`,
`41`, and `10000..=19999` — 39001 matches none of those) and **not** ephemeral
(`is_ephemeral` matches only `20000..=29999`).

## 4. Tag shape

| Tag | Cardinality | Shape |
|---|---|---|
| `d` | exactly one | `["d", "<channel-id>"]` — the channel's UUID as a string, matching NIP-33's addressing-tag convention. |
| `p` | zero or more | `["p", "<pubkey-hex>", "<role>"]` — one entry per current channel member whose role is `owner` or `admin`. `role` is exactly `"owner"` or `"admin"`; members with any other role (`member`, `guest`, `bot`) are omitted entirely, not included with a different role string. |

Buzz's `MemberRole` enum (`crates/buzz-core/src/channel.rs`) defines five roles
in total — `owner`, `admin`, `member`, `guest`, `bot` — but only the first two
ever appear in a kind 39001 `p` tag, by the explicit role filter in the code
that builds this event.

No `h` tag is present: per the root `AGENTS.md`, addressable channel-state
events use the `d` tag for channel identity instead of the `h`-tag scoping used
by in-channel events like chat messages.

## 5. Content field semantics

**Always the empty string.** Every code path that builds a kind 39001 event
(`emit_group_discovery_events` in `buzz-relay`, and the independent backfill
path in `buzz-admin`'s `reconcile_channels`) constructs it with an empty
`content` field. All admin-list information lives in the `p` tags described
above — there is no JSON body to parse.

## 6. Access control and storage model

**Producers.** Kind 39001 is always **relay-signed**, never client-authored.
The primary producer is `emit_group_discovery_events`
(`crates/buzz-relay/src/handlers/side_effects.rs`), whose own doc comment
states it emits "NIP-29 group discovery events (39000, 39001, 39002) signed by
the relay keypair," called "after group creation, metadata changes, or
membership changes." Concretely, it is invoked from:

- `handle_put_user`, `handle_remove_user`, `handle_edit_metadata`,
  `handle_create_group`, `handle_join_request`, `handle_leave_request` — the
  NIP-29 group-state and membership handlers in `side_effects.rs`.
- `handle_dm_open`, `handle_dm_add_member` — DM-channel creation and membership
  changes, in `command_executor.rs`.
- `send_moderation_notice` — moderation-notice DM channel setup, in
  `moderation_notices.rs`.
- `publish_nip43_delta` — NIP-43 relay-membership delta publication, in
  `side_effects.rs`.

`buzz-admin`'s `reconcile_channels` subcommand additionally builds and
republishes a kind 39001 event directly (same tag shape) as an operator-run
backfill/repair path, independent of `emit_group_discovery_events`.

**Consumers.** No client code in this repository — searched across
`desktop/src`, `web/src`, `mobile/lib`, `crates/buzz-cli/src`, and
`crates/buzz-sdk/src` — reads or references kind 39001 today. This is a real gap
rather than an oversight in this document: the kind is produced on every
relevant channel/membership change, but nothing in this repository's clients yet
consumes the resulting admin list.

**Persistence.** Stored via `Db::replace_addressable_event`
(`crates/buzz-db/src/store/replaceable.rs`), whose own doc comment names it as
the store for "NIP-16 kinds ... and NIP-29 discovery state (39000-39002, called
from side_effects.rs)." It keeps only the event with the highest `created_at`
per `(kind, pubkey, channel_id)`, breaking same-second ties by lowest event id.
Every 39001 write passes `channel_id: Some(...)`, so a stored 39001 event is
always channel-scoped, never global.

**Fan-out.** A newly inserted 39001 event is dispatched through
`dispatch_persistent_event`, which unconditionally records it in the hash-chain
audit log (`enqueue_event_created_audit`) before scheduling fan-out. Live
fan-out publishes on `EventTopic::Channel(channel_id)` — never
`EventTopic::Global` — so only subscribers already live-subscribed to that
specific channel receive it in real time; a subscription scoped only to
`{kinds:[39001]}` with no channel filter will not. `emit_group_discovery_events`'s
own doc comment states clients are expected to discover these events via
historical REQ queries rather than global live discovery.

**Read gating.** 39001 is not a member of any of `kind.rs`'s four named
read-gate sets (`AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, `P_GATED_KINDS`,
`SHARED_GATED_KINDS`). Combined with the channel-scoped storage described
above, this means (by inference, not a traced read-path check) that a stored
39001 event's visibility follows the containing channel's own membership-based
access control — world-readable for a public channel, member-only for a
private one — rather than any kind-specific rule.

**Search / conformance.** No search-indexing or conformance-emit logic in this
repository special-cases kind 39001 by name; it is not a member of any
kind-specific exclusion set found during this review. Because its `content` is
always empty, full-text search over it would have nothing but tag data to match
regardless.

## 7. Worked example

Illustrative only — the pubkeys and signature below are placeholders, not real
keys:

```json
{
  "id": "0000000000000000000000000000000000000000000000000000000000000000",
  "pubkey": "aaaa0000000000000000000000000000000000000000000000000000000001",
  "created_at": 1735689600,
  "kind": 39001,
  "tags": [
    ["d", "550e8400-e29b-41d4-a716-446655440000"],
    ["p", "bbbb0000000000000000000000000000000000000000000000000000000002", "owner"],
    ["p", "cccc0000000000000000000000000000000000000000000000000000000003", "admin"]
  ],
  "content": "",
  "sig": "..."
}
```

Here `pubkey` is the relay's own signing key (this event is always relay-signed),
`d` is the target channel's UUID, and the two `p` tags list one owner and one
admin. A channel with no owner or admin members yet would still carry the `d`
tag but zero `p` tags.

## 8. Versioning and supersession

Not applicable. No prior kind number for this concept was found in `kind.rs`'s
comments (unlike, for example, a documented V1-to-V2 renumbering elsewhere in
that file); 39001 is the only number this concept has used in this repository's
history at the recorded revision.

## 9. Relationships

None declared. No sibling `events/kinds/*` corpus node (e.g. for kind 39000 or
39002) exists on `origin/launchpad` at the recorded revision, and no `interfaces`
or `implements`-target node exists either — declaring a `relationships` entry
against an id nothing in the merged corpus carries is a hard validation error,
not thoroughness. The most likely future edges are `depends-on` or `references`
relationships to future kind-39000 and kind-39002 nodes (39001, 39000, and 39002
are emitted together by the same function and describe the same channel) and a
`references` edge to a future kind-9021/9022 (NIP-29 join/leave request) node,
once those nodes exist.

## Scope and omissions

**This document covers** kind 39001's identity, governing spec, NIP-01 delivery
classification, tag shape, content semantics, producers, the absence of any
current consumer, persistence and fan-out behavior, and read-access reasoning,
each grounded in `crates/buzz-core/src/kind.rs`, `crates/buzz-relay`, and
`crates/buzz-db` as they exist at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 39000 (channel metadata) | A future, separate `events/kinds/kind-39000-*.md` node |
| Kind 39002 (channel membership) | A future, separate `events/kinds/kind-39002-*.md` node |
| The NIP-29 put-user/remove-user/edit-metadata/create-group/join-request/leave-request *interface* surface that triggers a 39001 refresh as a side effect | A future interface-typed corpus node, per `templates/event-kind.md`'s own boundary against `#1342`-style interface nodes |
| Any future client feature that consumes kind 39001 | Not yet designed or filed at the recorded revision |

**Expected but not verified when this node was written:**

- **The exact private-channel read-path check** that enforces "member-only" for
  a private channel's stored events was not traced line-by-line; §6's read-gating
  claim beyond the absence from the four named gate sets is stated as
  `INFERENCE` with `confidence: 0.75`, not `FACT`.
- **Whether any existing test indirectly exercises kind 39001** by asserting on
  the broader side effects of a NIP-29 handler (rather than asserting on the
  39001 event itself) was not checked exhaustively against every test module in
  `crates/buzz-relay`; only the absence of a name/literal match for
  `KIND_NIP29_GROUP_ADMINS` / `39001` was confirmed.
- **Whether a client is expected to consume kind 39001 in the near future** is
  not addressed by any specification or decision record found during this
  review; its absence today is recorded as a fact, not evaluated as a product
  gap.
