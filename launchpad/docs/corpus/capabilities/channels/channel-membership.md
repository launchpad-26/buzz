---
id: capabilities-channels-channel-membership
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-core's channel.rs defines a MemberRole enum with a linear permission hierarchy Owner (4) > Admin (3) > Member (2) > Guest (1), plus a separate Bot designation that always returns permission level 0 and is documented as not part of the hierarchy; MemberRole::is_elevated() is true only for Owner and Admin, and has_at_least() compares numeric permission_level() rather than enum ordering."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "buzz-core's channel.rs also defines ChannelVisibility (Open | Private), whose canonical string values (\"open\", \"private\") match the database enum and the Nostr tag convention used elsewhere in the membership flow."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "migrations/0001_initial_schema.sql defines member_role as a Postgres enum ('owner','admin','member','guest','bot') and the channel_members table with primary key (community_id, channel_id, pubkey), columns role, joined_at, invited_by, removed_at and removed_by, and a foreign key to channels(community_id, id) with ON DELETE CASCADE; membership is therefore removed by setting removed_at rather than deleting the row, and invited_by/removed_by keep an audit trail of who actioned each change. The same migration defines channel_add_policy as an enum ('anyone','owner_only','nobody')."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "buzz-core's kind.rs defines the event kinds that mutate channel membership: KIND_NIP29_PUT_USER = 9000 (add or change a member's role), KIND_NIP29_REMOVE_USER = 9001 (remove a member), KIND_NIP29_JOIN_REQUEST = 9021 (self-join) and KIND_NIP29_LEAVE_REQUEST = 9022 (self-leave), all in the NIP-29 admin/action kind ranges."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-core's kind.rs defines three relay-signed, addressable NIP-29 group-state kinds in the 39000-39003 range: KIND_NIP29_GROUP_METADATA = 39000, KIND_NIP29_GROUP_ADMINS = 39001 and KIND_NIP29_GROUP_MEMBERS = 39002, each doc-commented as relay-signed discovery/snapshot state rather than a user-submitted mutation."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-core's kind.rs also defines KIND_MEMBER_ADDED_NOTIFICATION = 44100 and KIND_MEMBER_REMOVED_NOTIFICATION = 44101, relay-signed events used to notify a specific pubkey that it was added to or removed from a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-db's channel.rs add_member() enforces: a private channel requires invited_by naming an existing active member (with a bootstrap exception letting the channel's own creator add themselves as the first member), an open channel lets anyone self-join but restricts granting an elevated (owner/admin) role to an existing owner/admin inviter, and changing an *active* member's role in either direction (including demotion) additionally requires the acting inviter to currently hold an elevated role -- keyed on the target's live (non-removed) role so a soft-removed owner cannot resurrect their own authority by rejoining. The write is wrapped in a Postgres advisory transaction lock (acquire_channel_membership_lock) and the INSERT uses ON CONFLICT ... DO UPDATE, making re-adding an already-active member at the same role idempotent."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "buzz-db's channel.rs add_member() and remove_member() both refuse a role change or removal that would leave a channel with zero active owners, counting rows with role = 'owner' AND removed_at IS NULL under the same advisory lock used for the rest of the write, and remove_member() additionally allows a member's own agent-owner (not only a channel owner/admin) to remove that member via crate::user::is_agent_owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "buzz-db's channel.rs is_member(), get_members(), get_members_bulk() and get_member_count() all filter on cm.removed_at IS NULL joined against a non-deleted channel row, so a soft-removed membership row is excluded from every read path even though it remains on disk."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-relay/src/handlers/side_effects.rs validates kind:9000 (PUT_USER) before storage: an absent role tag preserves an existing member's current role rather than defaulting to Member (to avoid a bare PUT_USER silently demoting an owner/admin), a private channel requires the actor to already be an active member, granting or changing to an elevated role requires the actor to already be elevated, demoting the last owner is rejected, self-add is always allowed, and a third-party add targeting an agent pubkey is additionally gated by that agent's stored channel_add_policy ('owner_only' restricts the add to the agent's own owner, 'nobody' refuses every third-party add, 'anyone' or an unrecognized value allows it)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The same file validates kind:9001 (REMOVE_USER): removing oneself requires being an active member and is refused if the actor is the channel's last owner; removing another pubkey requires the acting pubkey to hold an elevated role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "handle_join_request() (kind:9021) requires the channel's visibility to be 'open' -- a private channel refuses self-join with 'channel is private -- request an invitation' -- is a no-op if the caller is already an active member (checked via a cache, failing closed on a DB error), and otherwise calls add_member() with role MemberRole::Member and invited_by = None."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "handle_leave_request() (kind:9022) is described in its own comment as functionally identical to a self-targeted kind:9001, independently re-checks that the departing pubkey is not the channel's last owner before calling remove_member(), and -- unlike a third-party removal via kind:9001 -- also evicts the departing pubkey's live channel subscriptions and disables workflows scoped to that departed member."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "handle_put_user() and handle_remove_user() -- the side-effect handlers that run after kind:9000/9001 pass validation -- each call the corresponding buzz-db function, invalidate the membership cache for the affected pubkey, emit a channel system message describing the change (member_joined / member_left / member_removed), call emit_group_discovery_events() to regenerate the channel's discovery snapshot, and emit a KIND_MEMBER_ADDED_NOTIFICATION or KIND_MEMBER_REMOVED_NOTIFICATION addressed to the affected pubkey; handle_remove_user() additionally evicts live subscriptions and disables workflows for the removed pubkey, the same side effects handle_leave_request() performs for a self-leave."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "emit_group_discovery_events() re-reads the channel and its current member list and republishes, relay-signed, all three NIP-29 discovery kinds for that channel: kind:39000 with the channel's name/visibility/type/topic/purpose/archived/ttl tags, kind:39001 with a `p` tag per member whose role is owner or admin, and kind:39002 with a `p` tag per active member (built by the local group_members_tags() helper) -- so every add, remove, role change, join or leave described above ends by republishing a fresh membership snapshot rather than leaving clients to diff individual mutation events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "buzz-sdk's builders.rs maps four typed event builders onto these kinds: build_add_member -> Kind::Custom(9000), build_remove_member -> Kind::Custom(9001), build_join -> Kind::Custom(9021) and build_leave -> Kind::Custom(9022); buzz-cli's commands/channels.rs exposes cmd_add_channel_member, cmd_remove_channel_member, cmd_join_channel and cmd_leave_channel, each building the corresponding event with the SDK builder, signing it, and submitting it through BuzzClient."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-cli/src/commands/channels.rs"
  - statement: "buzz-cli's cmd_list_channel_members() queries kind:39002 filtered by the channel's UUID on the `#d` tag (limit 1) and extracts the roster from that single addressable event's `p` tags, rather than querying the channel_members table or any per-mutation event directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs"
  - statement: "Root AGENTS.md states that channels are scoped by `h` tags for events inside a channel, that addressable events describing a channel instead carry its id in a `d` tag (naming kind:39000, kind:39001 and kind:39002 for metadata, and -- by the surrounding sentence -- membership), and that `get_channels` resolves a user's channels from the `d` tag of their kind:39002 events rather than from `h`."
    entry_class: FACT
    evidence:
      - "AGENTS.md:173-174"
  - statement: "VISION_PROJECTS.md's own Status table marks the row 'Channels, forums, DMs, canvases' as 'Ships today', naming the surface this capability is part of as shipped rather than in-progress or designed."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "crates/buzz-db/src/channel.rs's own test module includes regression tests naming the exact authorization failures this node describes -- kicked_owner_rejoins_as_member_not_owner (a removed owner self-rejoining via join-request semantics lands as Member, not a resurrected Owner), repro_unprivileged_member_can_demote_owner, repro_private_channel_member_can_demote_owner and unprivileged_member_cannot_demote_a_co_owner (an unprivileged actor must not be able to demote an owner), and membership_writes_serialize_on_the_shared_channel_lock plus remove_member_rejects_an_actor_demoted_while_it_waited (concurrent membership writes on one channel serialize behind the advisory lock, and a demotion that lands mid-wait is honored rather than raced)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs contains end-to-end coverage of the notification side effect described above -- test_membership_notification_emitted_on_add and test_membership_notification_emitted_on_remove connect a real WebSocket client, subscribe to kind:44100/44101 filtered by the agent's own `p` tag, trigger a kind:9000 add over HTTP, and assert the notification arrives -- plus filter-shape tests (test_membership_notification_requires_p_filter, test_membership_notification_requires_own_p_filter, test_membership_notification_wildcard_filter_rejected, test_membership_notification_multi_p_rejected, test_membership_notification_mixed_filter_rejected) and test_client_submitted_nip43_membership_snapshots_are_rejected, which is about the separate relay-wide membership system named in the Boundary section below, not this node's channel-membership snapshots."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "crates/buzz-db/src/relay_members.rs implements a second, separate membership system -- relay/community-wide membership (is_relay_member, add_relay_member, remove_relay_member, list_relay_members, claim_relay_membership, has_join_policy_acceptance) -- keyed on NIP-43 kinds RELAY_ADMIN_ADD_MEMBER/REMOVE_MEMBER/CHANGE_ROLE (9030-9032), KIND_NIP43_MEMBERSHIP_LIST (13534) and KIND_NIP43_LEAVE_REQUEST (28936), all defined in buzz-core's kind.rs distinctly from the per-channel kinds this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs"
      - "crates/buzz-core/src/kind.rs"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-event-ingestion
---

# Channel membership: capability

Buzz lets a channel's owners, admins and members control who belongs to that
channel and what they may do there. Membership is an explicit, per-channel
roster (owner, admin, member, guest, or the separate bot designation) rather
than implicit visibility: a user reads and writes in a channel because a
`channel_members` row says so, that row was created either by self-join (an
open channel) or by an existing member's invite (a private channel), and it
can be changed -- role granted, role revoked, or removed entirely -- by
whoever the authorization rules below say may change it. Every change to the
roster republishes a fresh, relay-signed snapshot of the channel's current
members and admins, so any client or agent can always ask "who is in this
channel right now" without replaying history.

**Primary actors:** the channel member acting on their own membership
(joining an open channel, leaving any channel), and a channel owner or admin
acting on someone else's membership (inviting into a private channel, adding
with a specific role, changing a role, removing a member). An agent's own
owner is a third actor with a narrower power: removing that agent from a
channel, independent of the agent's own role there. **Primary outcomes:** a
channel's `channel_members` roster reflects who may currently read and write
in it, gates that roster against unauthorized escalation or a channel being
left without an owner, and keeps every client's view of "who's in this
channel" current through relay-signed discovery events.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Status table marks "Channels, forums,
DMs, canvases" as shipped ("Ships today"), and every mechanism described
below -- the `channel_members` table, the event kinds, the authorization
logic and the discovery-event side effects -- was read directly from merged
code in `buzz-core`, `buzz-db`, `buzz-relay`, `buzz-cli` and `buzz-sdk`, not
from a design document describing intended behavior.

## Roles

A member holds exactly one role, defined once in `buzz-core::channel` and
mirrored by the `member_role` Postgres enum:

| Role | Permission level | Elevated? | Notes |
|---|---|---|---|
| Owner | 4 | yes | Full control -- can manage members and delete the channel. |
| Admin | 3 | yes | Can manage members and channel settings. |
| Member | 2 | no | Standard participant; the role a self-join always receives. |
| Guest | 1 | no | Read-only external participant. |
| Bot | 0 | no | Automated agent/integration -- deliberately outside the linear hierarchy; a bot never satisfies an elevated-role check regardless of what `permission_level` a comparison expects. |

Only Owner and Admin are "elevated" for authorization purposes
(`MemberRole::is_elevated`), and every privileged action below is gated on
holding an elevated role, not on a specific numeric threshold chosen ad hoc
per call site.

## Behavioral rules and variants

**Visibility decides who may self-join.** A channel is either `open` or
`private` (`ChannelVisibility`). Self-join (kind:9021, `POST` via
`buzz-cli channels join` / `buzz-sdk::build_join`) succeeds only against an
open channel, always grants `Member`, and is a no-op if the caller is
already an active member. Against a private channel it is refused outright
-- there is no self-join path into a private channel; membership there is
established only by an existing active member inviting the target (kind:9000
/ `PUT_USER`), with a bootstrap exception letting a channel's own creator add
themselves as its first member.

**Granting or changing to an elevated role always requires an elevated
actor**, on every channel regardless of visibility, in every code path
(`add_member` in `buzz-db`, and independently again in the relay's
pre-storage `PUT_USER` validator). Demotion is treated exactly as
consequential as promotion: an owner cannot be demoted by anyone who is not
themselves currently elevated, and specifically not by the owner demoting
themselves via a bare re-add, because a bare `PUT_USER` with no `role` tag
preserves the target's current role rather than defaulting to `Member`.

**A channel may never be left with zero active owners.** Demoting the last
owner and removing the last owner are both refused, checked as a live count
of `role = 'owner' AND removed_at IS NULL` rows under the same advisory
transaction lock the rest of a membership write runs behind, so this
protection holds even against concurrent writers racing on the same channel.
A soft-removed owner's stored role is deliberately not treated as live
authority: rejoining via kind:9021 after being removed lands the pubkey back
as an ordinary `Member`, not a resurrected `Owner` -- otherwise a removed
owner could self-rejoin and silently reclaim ownership.

**Leaving and being removed share one mechanism with two entry points.**
Kind:9022 (leave) is, by the relay's own comment, functionally identical to
a self-targeted kind:9001 (remove) -- both refuse to strip a channel of its
last owner, and both, once they succeed, evict the departed pubkey's live
channel subscriptions and disable workflows scoped to them. A third party
removing someone else via kind:9001 requires an elevated role, **or** -- a
narrower, separate grant -- being that member's own registered agent owner,
independent of what role the agent itself holds in the channel.

**Adding an agent as a third party is additionally policy-gated.** Each
agent pubkey carries its own `channel_add_policy` (`anyone`, `owner_only` or
`nobody`, a dedicated Postgres enum). Self-add always bypasses this gate; a
third party adding an agent it does not own is refused entirely under
`nobody`, restricted to the agent's own registered owner under `owner_only`,
and unrestricted under `anyone` or any value the gate does not recognize.

**Every successful membership change ends the same way.** A channel system
message describing the change is emitted, the channel's three NIP-29
discovery events (kind:39000 metadata, kind:39001 admins, kind:39002
members) are regenerated and republished relay-signed from the roster's
current state, and the affected pubkey receives a
`KIND_MEMBER_ADDED_NOTIFICATION` (44100) or `KIND_MEMBER_REMOVED_NOTIFICATION`
(44101) addressed to it via a `p` tag. A reader never has to diff mutation
events against each other to know the current roster -- the kind:39002
snapshot after any change already reflects it.

## Implementation surfaces

- **Data.** `channel_members` (defined in `migrations/0001_initial_schema.sql`),
  primary-keyed on `(community_id, channel_id, pubkey)`, soft-deleted via
  `removed_at`/`removed_by` rather than row deletion, and recording
  `invited_by` for audit. `buzz-db::channel` owns every read/write against it
  (`add_member`, `remove_member`, `is_member`, `get_members`,
  `get_member_count`, `membership_pairs`).
- **Protocol.** NIP-29-derived event kinds `9000`/`9001`/`9021`/`9022` for
  mutations and `39000`/`39001`/`39002` for relay-signed discovery snapshots,
  plus Buzz-specific notification kinds `44100`/`44101`, all defined in
  `buzz-core::kind`.
- **Platform.** Authorization is enforced twice on the write path: once in
  the relay's pre-storage validator (`crates/buzz-relay/src/handlers/side_effects.rs`,
  the `9000`/`9001` match arms) and again, independently, inside
  `buzz-db::channel::add_member`/`remove_member` themselves -- the DB layer is
  the defense-in-depth backstop for callers (for example the huddle bot-add
  path) that reach it without going through the relay's own event validator.
- **Interfaces.** `buzz-cli channels {join,leave,add-member,remove-member,list-members}`,
  backed by typed `buzz-sdk` event builders (`build_join`, `build_leave`,
  `build_add_member`, `build_remove_member`) for the four mutations, and a
  direct `kind:39002` query (filtered on `#d` = channel id) for reading the
  current roster.

## Boundary

This node does not describe:

- **How channels themselves are built, or the relay's broader architecture.**
  See the referenced `architecture-containers-relay` node for the container
  that hosts `buzz-db`/`buzz-relay`, and `architecture-flows-event-ingestion`
  for the ingestion pipeline that enforces membership as a *read/write access
  gate* on ordinary channel-scoped events (via `check_channel_membership` and
  `filter_fanout_by_access`) -- a related but distinct concern from the
  membership-roster mutations this node documents.
- **The CLI/SDK boundary as a formal interface contract.** The commands and
  builders named above are cited as this capability's implementation
  surface, not documented here as an interface node (no interface template
  instance exists yet in this corpus).
- **The step-by-step sequence of one join or leave interaction.** No flow
  node for channel membership exists yet in this corpus; this node states
  the rules a flow would walk through, not the walk itself.
- **Relay/community-wide membership.** A second, separate membership system
  exists in this codebase: `buzz-db::relay_members` and the NIP-43 kinds
  (`RELAY_ADMIN_ADD_MEMBER`/`REMOVE_MEMBER`/`CHANGE_ROLE` = 9030-9032,
  `KIND_NIP43_MEMBERSHIP_LIST` = 13534, `KIND_NIP43_LEAVE_REQUEST` = 28936)
  govern who may connect to a relay/community at all, independent of which
  channels within it they belong to. That is a different capability from the
  per-channel roster this node documents, and is out of scope here.
- **Community-wide moderation (bans/timeouts).** `KIND_MODERATION_BAN` and
  related 9040-series commands restrict a pubkey's ability to write at all;
  they are enforced during event ingestion alongside, but are not part of,
  the per-channel membership roster and its role hierarchy.
- **How the desktop or mobile client surfaces membership actions in its UI.**
  Only the CLI/SDK/relay/DB layers were inspected; no desktop or mobile
  membership UI code was opened while drafting this node.

## Relationships

- `references`: `architecture-containers-relay` -- the container hosting the
  relay handlers (`side_effects.rs`, `ingest.rs`) that implement the
  authorization and side-effect logic this node describes.
- `references`: `architecture-flows-event-ingestion` -- the flow that
  enforces active channel membership as an access gate on ordinary
  channel-scoped events, a direct consumer of the roster this node's
  capability maintains.

Checked against `origin/launchpad`'s corpus tree at the recorded revision
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`):
both targets are present (`architecture/containers/relay.md`,
`architecture/flows/event-ingestion.md`). No `capabilities`-type sibling node
exists yet in this corpus to declare a `part-of` or `implements` edge
toward, and no interface or flow node for channel membership specifically
has merged, so no edge is declared to either.

## Verification

- `crates/buzz-db/src/channel.rs`'s own test module: regression tests naming
  the exact failure modes this node describes --
  `kicked_owner_rejoins_as_member_not_owner`,
  `repro_unprivileged_member_can_demote_owner`,
  `repro_private_channel_member_can_demote_owner`,
  `unprivileged_member_cannot_demote_a_co_owner`,
  `membership_writes_serialize_on_the_shared_channel_lock` and
  `remove_member_rejects_an_actor_demoted_while_it_waited`.
- `crates/buzz-test-client/tests/e2e_relay.rs`: end-to-end coverage of the
  notification side effect (`test_membership_notification_emitted_on_add`,
  `test_membership_notification_emitted_on_remove`) and of the filter
  restrictions on subscribing to another pubkey's membership notifications.

## Scope and omissions

**This node covers** the per-channel membership roster: the role hierarchy,
the event kinds that mutate and announce it, the authorization rules
governing self-join, invite, role change and removal (including the
last-owner and agent-add-policy guards), the discovery-event side effect
that republishes the roster after every change, and the CLI/SDK/DB surfaces
that implement all of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, `buzz-db` and the other subsystem crates are architected | `architecture-containers-relay` |
| How ingestion enforces membership as a read/write access gate on ordinary events | `architecture-flows-event-ingestion` |
| The CLI/SDK channel-membership commands as a formal interface contract | no interface node yet drafted for this corpus |
| The step-by-step sequence of one join/leave/add/remove interaction | no flow node yet drafted for this corpus |
| Relay/community-wide membership (NIP-43, `relay_members`) | a separate capability, not documented here |
| Community-wide moderation (bans/timeouts) | a separate capability, not documented here |
| Desktop/mobile client UI for membership actions | not inspected while drafting this node |

**Expected but not verified when this node was written:**

- **No desktop or mobile client code was opened.** Whether either client
  exposes join/leave/invite/role-change UI beyond the CLI/SDK surfaces
  documented here, and whether it calls the same event kinds or a different
  path, is unknown.
- **No huddle-audio "join" code (`crates/buzz-relay/src/audio/join.rs`) was
  read beyond noticing it exists.** Its "join" is audio-room presence, a
  different concept from the channel membership documented here; this node
  makes no claim about how, or whether, the two interact.
- **The workflow-disabling side effect on departure
  (`disable_departed_member_workflows`) was named from `side_effects.rs`'s
  call site but its own implementation was not opened**, so this node
  states only that it runs on leave/removal, not the detail of what it
  disables or how.
