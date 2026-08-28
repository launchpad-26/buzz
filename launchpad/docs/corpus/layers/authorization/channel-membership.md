---
id: layers-authorization-channel-membership
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
  - statement: "channel_members is a table keyed on the composite primary key (community_id, channel_id, pubkey), carrying role, joined_at, invited_by, removed_at and removed_by columns, with a foreign key to channels(community_id, id) ON DELETE CASCADE."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:132-145"
  - statement: "kind:39002 is defined as KIND_NIP29_GROUP_MEMBERS = 39002, in the NIP-29 addressable group-state range 39000-39003, alongside KIND_NIP29_GROUP_METADATA (39000) and KIND_NIP29_GROUP_ADMINS (39001)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:420-426"
  - statement: "is_member(pool, community_id, channel_id, pubkey) returns true only when a channel_members row exists for that exact (community_id, channel_id, pubkey) with removed_at IS NULL, joined to a channels row with deleted_at IS NULL."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:643-661"
  - statement: "get_accessible_channel_ids(pool, community_id, pubkey) returns the UNION of two sets: channel_ids where the pubkey has an active (removed_at IS NULL) channel_members row on a non-deleted channel, and channel_ids of every non-deleted channel in the community whose visibility is 'open' -- so an open channel is accessible to every community member without any channel_members row existing for them."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:754-782"
  - statement: "add_member requires an inviter for a private channel (with a bootstrap exception letting a channel's creator add themselves as its first member), and gates granting or changing to an elevated role behind the inviter or acting member already holding an elevated role; demoting an active member out of 'owner' is blocked if it would leave the channel with zero active owners."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:382-539"
  - statement: "remove_member performs a soft delete (sets removed_at/removed_by rather than deleting the row), requires the actor to be an active owner/admin, the agent's owner, or the member removing themselves, and refuses to remove the channel's last active owner regardless of caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:560-640"
  - statement: "buzz-auth defines a ChannelAccessChecker trait (accessible_channel_ids, can_access) that every method takes a TenantContext for, with a doc comment stating implementations MUST scope every query by ctx.community() because the channels primary key is (community_id, id) and an unscoped query would be a cross-community existence oracle; check_read_access and check_write_access each require both a Scope (MessagesRead/MessagesWrite) and passing membership via can_access."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs:1-101"
  - statement: "AppState.get_accessible_channel_ids_cached wraps get_accessible_channel_ids behind a cache keyed on (community_id, pubkey), documented as a 10-second cache, falling back to the database on a cache miss."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1231-1249"
  - statement: "handle_req builds accessible_channels from the cached lookup, then for every explicitly requested channel id it is not already in, it queries state.db.is_member directly (bypassing the cache) and, via resolve_request_local_access, pushes that channel into the request-local vector only if the DB confirms active membership -- repairing a stale cache-negative for the rest of that request without ever letting a repair happen when a scoped auth token's channel allow-list already excludes the channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:108-187"
      - "crates/buzz-relay/src/handlers/req.rs:526-545"
  - statement: "If a REQ names one or more explicit channels and none of them survive authorization (none are in the resolved accessible_channels), handle_req closes the subscription with 'restricted: not a channel member' rather than registering a subscription that can never receive anything; channels present in an OR filter that are simply not authorized are instead silently omitted, preserving NIP-01 OR semantics for the channels that are."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:189-209"
  - statement: "emit_group_discovery_events builds the kind:39002 event's tags via group_members_tags: one 'd' tag set to the channel's UUID string, then one 'p' tag per row returned by get_members (every active member, any role) in the form [\"p\", pubkey_hex, \"\", role]; the resulting event is stored channel-scoped (channel_id = Some(...)) specifically so existing access control applies and a private channel's member roster is only visible to that channel's own members."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1040-1059"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1134-1165"
  - statement: "kind:39001 (KIND_NIP29_GROUP_ADMINS) is built from the same member roster but filtered to only owner/admin roles, while kind:39002 (KIND_NIP29_GROUP_MEMBERS) carries every active member regardless of role -- the two addressable events are different views over the same underlying channel_members roster, not two independent membership stores."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1134-1165"
  - statement: "AGENTS.md (the top-level Buzz contributor guide) states that channels use 'h' tags (NIP-29 group tag) rather than 'e' tags for events inside a channel, and that addressable events describing a channel carry its id in a 'd' tag instead, naming kind:39000, kind:39001 and kind:39002 (membership) as that category."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "An open channel needs no explicit channel_members row for a community member to read or write to it because get_accessible_channel_ids computes open-channel access structurally, from the channel's own visibility column, rather than by materializing one channel_members row per community member per open channel; a private channel has no such structural shortcut; is_member's positive path is always a literal row."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/channel.rs:754-782"
      - "crates/buzz-db/src/channel.rs:643-661"
    confidence: 0.75
  - statement: "CLAUDE.md's 'Relay queries must specify kinds' gotcha and buzz-relay's p_gated_filters_authorized are a related but distinct authorization mechanism from channel membership: the p-gate governs whether a #p-tagged (pubkey-addressed) kind may be read at all, independent of any channel, whereas membership governs which #h-scoped channels a REQ, COUNT or event may touch."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1237"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Channel membership

Channel membership is the authorization fact the relay checks before letting a
pubkey read or write events scoped to a given channel — whether that pubkey has
an active row in `channel_members` for that channel, or the channel is open to
the whole community by visibility alone. This node documents how membership is
stored, computed and enforced; it does not document role-based permissions
(owner/admin escalation), channel creation, or channel *visibility* as a
standalone concept.

## Definition

**Channel membership is the answer to one question: is this pubkey allowed to
see or send events scoped to this channel, right now?** The relay resolves that
question in one of two ways, both grounded in the `channel_members` table
(`community_id`, `channel_id`, `pubkey`, `role`, `joined_at`, `invited_by`,
`removed_at`, `removed_by` — primary key on the first three columns; migrations/
0001_initial_schema.sql:132-145):

- **Private channels** require a literal, active row: `is_member` returns true
  only when a `channel_members` row exists for that exact
  `(community_id, channel_id, pubkey)` with `removed_at IS NULL`, joined to a
  non-deleted channel (crates/buzz-db/src/channel.rs:643-661).
- **Open channels** need no such row for a member of the community: the
  relay's `get_accessible_channel_ids` query unions the explicit-row set above
  with every non-deleted, `open`-visibility channel in the community
  (crates/buzz-db/src/channel.rs:754-782). Community membership itself, not a
  per-channel row, is what grants access.

**What this is not.** Membership is not the same thing as *role* — a member row
carries a `role` (`member`, `admin`, `owner`, ...), and role governs
*escalated* actions (granting elevated roles, demoting an owner, removing
another member) rather than whether the pubkey can see the channel at all;
`add_member`'s and `remove_member`'s role-escalation guards
(crates/buzz-db/src/channel.rs:382-539, 560-640) are a related but separate
concept, out of scope here. Membership is also not the same thing as the
`#p`-tag "p-gate" that guards certain event kinds independent of any channel
(crates/buzz-relay/src/handlers/req.rs:1182-1237) — see *Scope and omissions*.

## How the relay enforces it

```mermaid
flowchart TD
    A["REQ / COUNT arrives, authenticated pubkey known"] --> B["get_accessible_channel_ids_cached\n(10s cache, DB fallback)"]
    B --> C{"Filter names explicit\nchannel id(s)?"}
    C -->|No| D["Use cached accessible_channels\nas-is for this request"]
    C -->|Yes| E{"Channel id already\nin accessible_channels?"}
    E -->|Yes| F["Allowed, no DB call"]
    E -->|No — cache miss| G["state.db.is_member\n(uncached DB confirm)"]
    G -->|Member| H["resolve_request_local_access:\npush into vector, allow"]
    G -->|Not a member| I["Channel omitted from\nauthorized set"]
    D --> J["accessible_channels drives\nsubscription registration,\nhistorical delivery, search, COUNT"]
    F --> J
    H --> J
    I --> K{"Any requested channel\nsurvived authorization?"}
    K -->|No| L["CLOSED: restricted — not a channel member"]
    K -->|Yes| J
```

`buzz-auth`'s `ChannelAccessChecker` trait (`accessible_channel_ids`,
`can_access`) formalizes the same check as a tenant-scoped interface:
`check_read_access` and `check_write_access` both require a scope
(`MessagesRead`/`MessagesWrite`) **and** passing membership before allowing an
operation, and the trait's own doc comment states every implementation MUST
scope by `ctx.community()` — otherwise, because `channels`' primary key is
`(community_id, id)`, an unscoped membership query becomes a cross-community
existence oracle (crates/buzz-auth/src/access.rs:1-101).

On a multi-pod relay, `AppState.get_accessible_channel_ids_cached` wraps the DB
query in a 10-second cache (crates/buzz-relay/src/state.rs:1231-1249). A
request that explicitly names a channel not already in that cached vector does
not simply trust the cache's absence as a denial: `handle_req` confirms
against the database directly and, on a positive result,
`resolve_request_local_access` pushes the channel into the request-local
vector so every downstream consumer of that one request (subscription
registration, historical delivery, NIP-50 search scoping, COUNT) sees the
repaired, not the stale, answer (crates/buzz-relay/src/handlers/req.rs:108-187,
526-545). If no requested channel survives authorization, the subscription is
closed with `restricted: not a channel member` rather than registered with
nothing it can ever deliver (crates/buzz-relay/src/handlers/req.rs:189-209).

## How membership is published: kind:39002

The relay publishes its own view of channel membership as a signed, relay-keypair
Nostr event: `KIND_NIP29_GROUP_MEMBERS = 39002`
(crates/buzz-core/src/kind.rs:420-426), one of the NIP-29 group-state kinds
`AGENTS.md`/`CLAUDE.md` describes as carrying a channel's id in a `d` tag rather
than an `h` tag (CLAUDE.md). `emit_group_discovery_events` builds this event's
tags via `group_members_tags`: a `d` tag set to the channel UUID, then one `p`
tag per active member (any role) in the form `["p", pubkey_hex, "", role]`
(crates/buzz-relay/src/handlers/side_effects.rs:1040-1059, 1134-1165). The
sibling `KIND_NIP29_GROUP_ADMINS` (39001) event is built from the same roster
filtered to owner/admin roles only — 39001 and 39002 are two views over one
`channel_members` table, not two independent membership stores
(crates/buzz-relay/src/handlers/side_effects.rs:1134-1165). Crucially, the
kind:39002 event itself is stored **channel-scoped** (`channel_id = Some(...)`),
so the same access control that gates the channel's own messages gates its
member-roster snapshot: a private channel's roster is visible only to that
channel's own members (crates/buzz-relay/src/handlers/side_effects.rs:1052-1059).

## Use cases

- **An agent or client deciding what a REQ subscription will actually return**
  needs to know that an `#h`-scoped filter for a channel it does not belong to
  will not silently return nothing forever — it is refused outright
  (`restricted: not a channel member`), while a filter mixing an authorized and
  an unauthorized channel id returns only the authorized one's events.
- **A developer debugging "why did my just-added member not see the channel
  immediately"** needs to know the 10-second accessible-channels cache exists
  and that an explicit-channel request repairs itself request-locally rather
  than waiting out the TTL — but only for requests that name the channel
  explicitly, not for a bare community-wide subscription.
- **A developer reasoning about open vs. private channels** needs to know an
  open channel's accessibility is structural (derived from `channels.visibility`)
  rather than backed by one `channel_members` row per community member, which
  is why `get_accessible_channel_ids`'s query shape (a `UNION`, not a single
  table scan) is the right place to look, not `channel_members` alone.
- **A client author resolving a channel's member list for display** needs to
  know kind:39002 is a relay-signed, channel-scoped snapshot rebuilt from
  `channel_members` on every membership change, not a client-maintained cache
  independent of the relay's own authorization state.

## Comparison: open vs. private channel membership resolution

| | Open channel | Private channel |
|---|---|---|
| Needs an explicit `channel_members` row to read/write? | No — visibility alone grants access to any community member | Yes — `is_member` requires an active row |
| Path in `get_accessible_channel_ids` | The `visibility = 'open'` half of the `UNION` | The `channel_members` half of the `UNION` |
| Who can add a member | Any active member may self-join; only an existing owner/admin may grant an elevated role | Requires an inviter who is an active member (or the channel's own creator, bootstrap-only) |
| kind:39002 still published? | Yes — the roster still reflects whoever has an active `channel_members` row (e.g. anyone who has ever explicitly joined), even though visibility alone would already grant them access | Yes — this is the only way a private roster becomes visible, and only to existing members |

## Related resources

Channel membership is one instance of the corpus's community-boundary
principle applied one level down, inside a single community: see the
`references` relationship below rather than a duplicated explanation of why a
security boundary exists at all.

## Scope and omissions

**This document covers** what a `channel_members` row means, how open-channel
access differs structurally from private-channel access, how the relay
resolves and caches "is this pubkey allowed to touch this channel" for REQ/COUNT
authorization, and how that same roster is published as kind:39002.

**It does not cover:**

- **Role-based authorization** (what an `owner` vs. `admin` vs. `member` role
  permits beyond bare channel access — grant/demote rules, last-owner
  protection mechanics as a topic in their own right). `add_member` and
  `remove_member`'s role-escalation logic was read as evidence for *this*
  node's membership-lifecycle claims, but a full treatment of role semantics
  is a separate concept and, per this corpus's one-node-one-idea rule, belongs
  in its own node if one is later commissioned.
- **Channel creation and visibility as a standalone concept** (why a channel
  is created `open` vs. `private`, and whether that choice can later change).
- **DM-channel membership peculiarities** — `channel_type == "dm"` channels are
  visible in `emit_group_discovery_events`'s kind:39000 handling (participant
  pubkeys embedded directly) but that special-casing was not investigated
  beyond noting its existence.
- **The `#p`-tag p-gate** (`p_gated_filters_authorized`) — a related but
  independent authorization mechanism for certain event kinds, not a channel
  membership check; named here only to draw the boundary, not explained.

**Expected but not independently verified when this node was written:** the
cross-pod cache-invalidation path that `state.rs`'s own doc comments describe
for the 10-second `accessible_channels` cache (i.e., what actively invalidates
the cache on other pods when a membership change happens, versus merely
waiting out the TTL) was read as a comment, not traced through a running
multi-pod deployment or its invalidation-publishing code path.

## Relationships
