---
id: events-kinds-kind-39002-channel-members
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
  - statement: "kind.rs defines `pub const KIND_NIP29_GROUP_MEMBERS: u32 = 39002;` under the comment block '// NIP-29 group state (addressable range 39000-39003)', with its own doc comment '/// NIP-29: Addressable group members list.', alongside sibling constants KIND_NIP29_GROUP_METADATA (39000), KIND_NIP29_GROUP_ADMINS (39001) and KIND_NIP29_GROUP_ROLES (39003)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:420-428"
  - statement: "KIND_NIP29_GROUP_MEMBERS is listed in ALL_KINDS."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:691"
  - statement: "is_parameterized_replaceable(kind) returns kind >= PARAM_REPLACEABLE_KIND_MIN (30000) && kind <= PARAM_REPLACEABLE_KIND_MAX (39999), so 39002 is classified parameterized-replaceable/addressable; is_replaceable(kind) matches only 0, 3, KIND_CHANNEL_METADATA and 10000..=19999, which does not include 39002, so kind.rs's own two classification helpers agree that 39002 is addressable and not NIP-01 'replaceable'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:451-454"
      - "crates/buzz-core/src/kind.rs:773-778"
      - "crates/buzz-core/src/kind.rs:780-785"
  - statement: "KIND_NIP29_GROUP_MEMBERS (39002) does not appear in any of AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS or SHARED_GATED_KINDS -- the relay's four named per-kind read-access-control sets -- so at the kind-classification level a stored kind:39002 event carries none of Buzz's special read-gating."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:159-169"
      - "crates/buzz-core/src/kind.rs:215"
  - statement: "NIP-29 documents group-membership state as its own addressable events with a `d` tag identifying the group, and Buzz's own docs/nips/ directory contains no NIP-XX proposal file naming kind 39002 or group membership -- confirmed by listing docs/nips/*.md, which enumerates only NIP-AA/AE/AM/AO/AP/CW/DV/ER/FI(-family)/GS/IA/MP/OA and similar labels, none for group membership -- so kind 39002 is documented as a direct NIP-29 conformer, not a Buzz custom-NIP extension."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
      - "shell(ls docs/nips/*.md) -> NIP-AA.md, NIP-AE.md, NIP-AM.md, NIP-AO.md, NIP-AP.md, NIP-CW.md, NIP-DV.md, NIP-ER.md, NIP-FI*.md, NIP-GS.md, NIP-IA.md, NIP-MP.md, NIP-OA.md -- none named for group membership"
  - statement: "group_members_tags builds the tag array for a kind:39002 event as exactly one `[\"d\", group_id]` tag (group_id is the channel's UUID as a string) followed by one `[\"p\", pubkey_hex, \"\", role]` tag per active member, with an inline comment stating the NIP-29 convention '[\"p\", pubkey, relay_url, role]' and that relay_url is left empty because the canonical relay is implicit in the event's own signature; no `h` tag is built anywhere in this function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1050-1060"
  - statement: "store_group_members_event builds the kind:39002 event with EventBuilder::new(Kind::Custom(KIND_NIP29_GROUP_MEMBERS as u16), \"\") -- an always-empty content string -- calls .allow_self_tagging() (needed because a relay-participant DM roster must keep the relay's own `p` tag, which nostr's default builder would otherwise strip), and signs with state.relay_keypair, so every kind:39002 event is authored by the relay's own keypair, never a client's."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1081-1096"
  - statement: "replace_member_event on LockedMemberSnapshot requires the incoming event's kind to equal exactly 39002 (returning DbError::InvalidData otherwise), requires the event's pubkey, and the (community_id, channel_id) pair, to match the snapshot's own locked coordinate, then soft-deletes (`deleted_at = NOW()`) any existing non-deleted row at that same (community_id, kind=39002, pubkey, channel_id) coordinate before inserting the new row -- an addressable/parameterized-replaceable supersede-then-insert pattern keyed by (community_id, kind, pubkey, channel_id) rather than a Nostr `d`-tag lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs:229-289"
  - statement: "emit_group_discovery_events emits kind:39000 (channel metadata) and kind:39001 (channel admins) via the shared emit_addressable_discovery_event helper, which calls the generic buzz-db replace_addressable_event; kind:39002 instead goes through a dedicated path -- state.db.lock_member_snapshot acquires a per-channel writer lock immediately before 'the authoritative 39002 replacement' (the function's own comment), then store_group_members_event calls replace_member_event on that locked snapshot -- so 39002's storage/replacement path is architecturally distinct from its 39000/39001 siblings, not merely a different call with the same underlying mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:998"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1041"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1119-1235"
  - statement: "emit_group_discovery_events's own doc comment states: 'Emit NIP-29 group discovery events (39000, 39001, 39002) signed by the relay keypair. Called after group creation, metadata changes, or membership changes. Events are stored channel-scoped (channel_id = Some(...)) so that existing access control applies -- private channel member lists are only visible to members.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1119-1123"
  - statement: "emit_group_discovery_events is called after every one of: DM-channel open (command_executor.rs), moderation-notice delivery to resurface a DM's discovery event (moderation_notices.rs), the channel-archival reaper's state update (main.rs), and several other join/leave/create/edit-metadata/create-invite handlers inside side_effects.rs itself -- confirmed by grepping every call site of the function across crates/buzz-relay/src."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:391"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs:150"
      - "crates/buzz-relay/src/main.rs:708"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1416"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1489"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1733"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1943"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2075"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2139"
  - statement: "reconcile_large_channel_member_snapshots repairs legacy kind:39002 snapshots truncated by a former 1,000-member database cap, using the same lock_member_snapshot / store_group_members_event / dispatch_group_members_event sequence as the ordinary membership-change path, scoped only to channels whose canonical roster exceeds LEGACY_ROSTER_LIMIT = 1_000."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:3197-3235"
  - statement: "required_scope_for_kind, the single function whose match arms decide the write scope required for every event kind ingested over both the HTTP POST /events path and the WebSocket EVENT path, has no match arm naming KIND_NIP29_GROUP_METADATA, KIND_NIP29_GROUP_ADMINS, KIND_NIP29_GROUP_MEMBERS or KIND_NIP29_GROUP_ROLES (39000-39003); any such kind falls through to its final catch-all arm `_ => Err(\"restricted: unknown event kind\")`, so a client-authored kind:39002 EVENT/POST is rejected before any tag or pubkey check runs -- an incidental consequence of the kind having no ingest-scope entry, not a purpose-built anti-spoofing rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:437-546"
  - statement: "store_group_members_event and reconcile_large_channel_member_snapshots build and sign kind:39002 events directly via EventBuilder and state.relay_keypair, then call replace_member_event -- neither path calls required_scope_for_kind or the HTTP/WebSocket ingest_event entry point at all, so the relay's own membership-publication path is architecturally separate from (not merely privileged within) the path that rejects client-authored kind:39002 events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1088-1097"
      - "crates/buzz-relay/src/handlers/side_effects.rs:3220-3234"
  - statement: "MemberRecord.role is documented as 'Role string (e.g. \"owner\", \"member\", \"bot\")', and the database's member_role enum type (created in migrations/0001_initial_schema.sql and mirrored in schema/schema.sql) is `ENUM ('owner', 'admin', 'member', 'guest', 'bot')`, so the `role` value embedded in each kind:39002 `p` tag is one of these five strings."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs:20-33"
      - "migrations/0001_initial_schema.sql:30"
      - "schema/schema.sql:30"
  - statement: "The events table's generated search_tsv column is `CASE WHEN kind IN (1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200) THEN NULL::tsvector ELSE to_tsvector('simple', content) END` -- 39002 is not in that exclusion list, so a stored kind:39002 row computes to_tsvector('simple', content) like any ordinary kind; since content is always the empty string for this kind (per store_group_members_event above), the resulting tsvector is empty and matches no NIP-50 search term in practice, even though nothing at the schema level specially excludes the kind from search."
    entry_class: FACT
    evidence:
      - "schema/schema.sql:203-227"
  - statement: "dispatch_persistent_event_inner resolves the pubsub/fan-out topic from the stored event's own channel_id column (EventTopic::Channel(channel_id) when Some, EventTopic::Global otherwise), publishes to Redis on that topic, and calls sub_registry.fan_out_scoped, which indexes live subscriber connections by (community_id, channel_id, kind) plus a per-channel kindless wildcard index -- so a live subscription already scoped to that specific channel (by channel_id and kind:39002, or a channel-wide wildcard) receives a new kind:39002 event as it is stored, even though the event itself carries no `h` tag; only an unscoped, global, kind-only filter such as `{kinds:[39002]}` misses it, matching emit_group_discovery_events's own NOTE about kind:39000 live discovery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:349-393"
      - "crates/buzz-relay/src/handlers/event.rs:396-439"
      - "crates/buzz-relay/src/subscription.rs:379-420"
  - statement: "dispatch_persistent_event enqueues a bounded audit record (enqueue_event_created_audit) on the awaited path before spawning the fan-out/pubsub work, so a stored kind:39002 event is audited via the same generic persistent-event audit path as any other stored event; no kind-39002-specific audit behavior exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:349-393"
  - statement: "The desktop Tauri backend's fetch_channels resolves 'the channels this identity belongs to' by querying `{\"kinds\": [39002], \"#p\": [my_pubkey]}`, extracting each matching event's `d` tag as a channel id, then batch-fetching kind:39000 metadata for those ids; it separately batch-fetches `{\"kinds\": [39002], \"#d\": all_channel_ids}` to compute member counts and rosters via collect_members_by_channel. The function's own doc comment labels this 'member-chain (kind:39002->kind:39000)'."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/channels/fetch.rs:181-193"
      - "desktop/src-tauri/src/commands/channels/fetch.rs:219-264"
      - "desktop/src-tauri/src/commands/channels/fetch.rs:386-393"
  - statement: "This repository's root AGENTS.md states: 'All event kind integers are defined in buzz-core/src/kind.rs. New features get new kind integers -- add them here first, then implement handling in the relay,' and separately: 'Channels use h tags (NIP-29 group tag), not e tags... Addressable events that describe a channel carry its id in their d tag instead: kind:39000 (metadata), kind:39001, kind:39002 (membership). get_channels resolves a user's channels from the d tag of their kind:39002 events, not from h.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "corpus-template-event-kind (launchpad/docs/corpus/templates/event-kind.md) is loadable in this worktree, which is a checkout of origin/launchpad, so an `implements` relationship targeting it resolves on the branch this node merges into."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "No other node under launchpad/docs/corpus/events/ exists at the recorded revision -- confirmed by the directory not existing at all before this node was created -- so this is the corpus's first event-kind instance node and no kind-39000 or kind-39001 sibling node exists yet to declare a `references` or `depends-on` relationship toward."
    entry_class: FACT
    evidence:
      - "shell(test -e launchpad/docs/corpus/events) -> DOES NOT EXIST, run against origin/launchpad HEAD before this file was written"
  - statement: "Issue #876's definition of done requires this node to state the event kind number/name and its persistent/replaceable/ephemeral classification, define required/optional tags/content and validation rules, name producers/consumers/authorization/persistence/fanout/search/audit treatment, and link the governing NIP/spec, handler/registry and conformance/tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#876 definition of done"
relationships:
  - type: implements
    target: corpus-template-event-kind
---

# Kind 39002 — NIP-29 channel members list

The addressable Nostr event that carries the current, relay-authoritative membership
roster of one Buzz channel: who belongs to it and in what role. This node documents the
wire contract and relay behavior of `kind:39002` as Buzz implements it today.

## Scope

This node covers `kind:39002` (`KIND_NIP29_GROUP_MEMBERS`) itself: its identity, NIP,
addressable/parameterized-replaceable classification, tag and content shape, and its
access-control, storage, fan-out, search and audit treatment. It does not document
`kind:39000` (channel metadata) or `kind:39001` (channel admins) — each is NIP-29's own
distinct addressable kind with its own tag shape, and, per `AGENTS.md`'s one-node-one-idea
rule, a separate corpus task if one is wanted. It does not document a consumer-facing
operation surface (a `buzz-cli` subcommand or a typed `buzz-sdk` builder) built on top of
this kind — that is an "interface" node's subject, not this one's, per
`corpus-template-event-kind`'s own stated boundary against `#1342`.

## 1. Title and kind identity

- **Name**: NIP-29 group members list (Buzz calls its channels "groups" at the protocol
  level, per NIP-29's own vocabulary).
- **Kind number**: `39002`.
- **Constant**: `KIND_NIP29_GROUP_MEMBERS` in `crates/buzz-core/src/kind.rs:426`.
- **Status**: implemented and in active use today — not merely proposed. It is emitted by
  the relay on channel creation and every membership change (see §6).

## 2. Referenced NIP

[NIP-29](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md),
the relay-based groups specification. Kind 39002 conforms directly to NIP-29's own group
membership addressable-event convention; Buzz has no `docs/nips/NIP-XX.md` custom-NIP
proposal for this kind, because none is needed — NIP-29 already governs it in full.

## 3. Kind range and delivery classification

`39002` falls in the NIP-33/NIP-01 parameterized-replaceable (addressable) range,
`30000`–`39999`. `crates/buzz-core/src/kind.rs`'s own `is_parameterized_replaceable`
helper classifies it as such (`kind >= 30000 && kind <= 39999`), and its `is_replaceable`
helper — which matches only kinds `0`, `3`, the channel-metadata kind and `10000..=19999`
— does not include it, so the two helpers agree: `39002` is addressable, not "replaceable"
in NIP-01's narrower sense, and not ephemeral (`kind.rs`'s ephemeral range is
`20000`–`29999`, disjoint from `39002`).

Buzz's own storage layer does not, however, key `kind:39002`'s replacement the generic
NIP-33 way (by `d`-tag lookup against `replace_addressable_event`, the path its `39000`
and `39001` siblings use). Instead it is replaced through a dedicated,
writer-lock-guarded coordinate of `(community_id, kind=39002, pubkey=relay, channel_id)`
— see §6.

## 4. Tag shape

Built by `group_members_tags` (`crates/buzz-relay/src/handlers/side_effects.rs:1050-1060`):

- **`d`** — exactly one. Value is the channel's UUID, as a string. This is the
  addressing tag; per this repository's own `AGENTS.md`, `get_channels` resolves a
  user's channels from this `d` tag, not from an `h` tag.
- **`p`** — zero or more, one per active member. Shape: `["p", "<pubkey-hex>", "",
  "<role>"]`. The third element (relay URL, per NIP-29's own `["p", pubkey, relay_url,
  role]` convention) is always the empty string, because the canonical relay is implicit
  in the event's own signature. The fourth element is the member's role, one of the
  database's `member_role` enum values: `owner`, `admin`, `member`, `guest`, `bot`.
- **`h`** — never present. Unlike ordinary channel-scoped messages (which this
  repository's `AGENTS.md` documents as using `h` for NIP-29 group scoping), this
  addressable kind carries no `h` tag at all; its channel association is carried
  entirely by the `d` tag's value and, at the storage layer, by the row's own
  `channel_id` column.

## 5. Content field semantics

Always the empty string (`""`). `store_group_members_event` builds the event via
`EventBuilder::new(Kind::Custom(KIND_NIP29_GROUP_MEMBERS as u16), "")` — no JSON body, no
encryption. All member data lives in the `p` tags described above.

## 6. Access control and storage model

**Read access**: `kind:39002` is absent from every one of Buzz's four named per-kind
read-gating sets (`AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, `P_GATED_KINDS`,
`SHARED_GATED_KINDS`), so at the kind-classification level it carries none of Buzz's
special per-event read restrictions. Read access is instead governed entirely by
**channel-scoped storage**: `emit_group_discovery_events`'s own doc comment states these
events are "stored channel-scoped (`channel_id = Some(...)`) so that existing access
control applies — private channel member lists are only visible to members." A private
channel's roster is therefore only visible to a reader who already has read access to
that channel; there is no kind-specific gate layered on top of that.

**Write access — relay-only, and not by a purpose-built rule**: every `kind:39002` event
is built and signed by `state.relay_keypair` (`store_group_members_event`,
`side_effects.rs:1088-1096`), never by a client key. Separately and independently, a
client attempting to publish a `kind:39002` event directly (over `POST /events` or the
WebSocket `EVENT` message — both routes funnel through the same
`required_scope_for_kind` check) is rejected: that function's match arms name no kind in
the `39000`–`39003` range, so any such event falls to its final catch-all,
`Err("restricted: unknown event kind")`, before any tag or pubkey check runs. This is a
side effect of the kind having no ingest-scope entry, not a dedicated anti-spoofing
check — worth stating precisely rather than implying the relay defends this kind by
name.

**Storage — a dedicated path, not the generic addressable-event path**: `kind:39000` and
`kind:39001` are both replaced through the shared `emit_addressable_discovery_event` →
`replace_addressable_event` path. `kind:39002` instead goes through
`lock_member_snapshot` (acquiring a per-channel writer lock) and then
`store_group_members_event` → `LockedMemberSnapshot::replace_member_event`, which
requires the incoming event's kind to be exactly `39002`, requires its pubkey and
`(community_id, channel_id)` to match the already-locked coordinate, and then
soft-deletes the previous latest row at that coordinate before inserting the new one.
The relay's own comment at the call site names this "the authoritative 39002
replacement," distinguishing it explicitly from the metadata/admin snapshots' ordinary
behavior.

## 7. Worked example

Illustrative — signature and identifiers are not real. A channel with one owner and one
member:

```json
{
  "id": "5b4f...redacted...",
  "pubkey": "b0dd...relay-pubkey-hex...",
  "created_at": 1735689600,
  "kind": 39002,
  "tags": [
    ["d", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["p", "aa11bb22cc33dd44ee55ff66aa11bb22cc33dd44ee55ff66aa11bb22cc33dd44", "", "owner"],
    ["p", "bb22cc33dd44ee55ff66aa11bb22cc33dd44ee55ff66aa11bb22cc33dd44ee55", "", "member"]
  ],
  "content": "",
  "sig": "..."
}
```

## 8. Versioning and supersession

Not applicable. No prior kind number for this data was found or inferred while writing
this node — see *Not verified* below for what that claim rests on.

## 9. Relationships

Declares `implements: corpus-template-event-kind` (this node is a realized instance of
that template). No `references` or `depends-on` edge to a `kind:39000`/`kind:39001`
sibling node is declared, because no such node exists yet in this corpus — this is the
first event-kind instance node authored here.

## Producers, consumers, fan-out, search and audit — summary

- **Producers**: the relay only, via `emit_group_discovery_events` /
  `store_group_members_event`, called after channel creation, membership changes
  (join/leave/put-user/remove-user), metadata edits, DM-channel open, moderation-notice
  delivery, channel archival, and legacy-roster reconciliation
  (`reconcile_large_channel_member_snapshots`, for channels whose roster exceeds the
  former 1,000-row cap).
- **Consumers**: any client resolving its channel list or a channel's roster — the
  desktop Tauri backend's `fetch_channels` is the concretely inspected example, querying
  `{"kinds":[39002],"#p":[my_pubkey]}` to discover membership and
  `{"kinds":[39002],"#d":[...]}` to batch-resolve member counts/rosters.
- **Persistence**: stored, channel-scoped (`channel_id` column set), replaced via the
  dedicated lock-guarded coordinate described in §6 — never deleted outright, only
  superseded.
- **Fan-out**: live fan-out is channel-scoped (indexed by `(channel_id, kind)` plus a
  per-channel wildcard), so a subscription already scoped to the channel receives a new
  snapshot immediately; an unscoped, global, kind-only filter (e.g. `{"kinds":[39002]}`
  with no channel scope) does not, matching the relay's own documented caveat for its
  `39000` sibling.
- **Search**: not excluded from the generated `search_tsv` column's kind exclusion list,
  but its content is always empty, so no NIP-50 full-text match is possible in practice.
- **Audit**: enqueued through the same generic `enqueue_event_created_audit` path as any
  other persisted event; no kind-specific audit behavior exists.

## Not verified

- **No automated test naming kind 39002 or `replace_member_event` was located and
  opened.** `crates/buzz-db/src/store/channel_members.rs` contains unit tests exercising
  `get_members` past a 1,000-row roster and the roster-reconciliation query, but this
  node did not open or name a test that asserts `replace_member_event`'s
  supersede-then-insert behavior directly, or an end-to-end test that publishes a
  channel and reads back its `kind:39002` roster. This is a gap in *conformance/tests*
  linkage the issue's own DoD asks for, named honestly rather than papered over with an
  invented citation.
- **Whether kind 39002 (or the 39000-39003 range generally) was ever assigned a
  different number before its current one** was not established from any source opened
  while writing this node — §8 states "not applicable" on the absence of contrary
  evidence, not on a search that affirmatively ruled it out.
- **Mobile (`mobile/`) and `buzz-cli`'s own kind:39002 consumers**, if any, were not
  inspected; only the desktop Tauri backend's `fetch_channels` was opened as the
  concrete consumer example.
