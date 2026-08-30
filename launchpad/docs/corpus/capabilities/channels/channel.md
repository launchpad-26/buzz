---
id: capabilities-channels-channel
type: capabilities
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
  - statement: "buzz-core defines four channel types -- Stream ('linear message stream, the default'), Forum ('threaded forum-style discussion'), Dm ('direct message conversation') and Workflow ('internal workflow execution channel') -- as a closed Rust enum with canonical string forms 'stream', 'forum', 'dm', 'workflow' shared by both directions of the FromStr/Display conversion."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "buzz-core defines exactly two visibility states for a channel -- Open ('searchable; anyone can join without an invite') and Private ('hidden; requires an invite to join') -- as a closed enum with canonical strings 'open' and 'private'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "buzz-core's MemberRole doc comment states the permission hierarchy for authorization checks as Owner > Admin > Member > Guest, and states that Bot 'is a separate designation -- it is not part of the linear hierarchy'; permission_level() returns 4/3/2/1 for Owner/Admin/Member/Guest and 0 for Bot, and has_at_least() compares only on that numeric level, so a Bot never satisfies any role requirement through the hierarchy."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "The channels table (migrations/0001_initial_schema.sql) stores channel_type and visibility as Postgres enums defaulting to 'stream' and 'open', carries a community_id foreign key, and a BEFORE UPDATE trigger (channels_community_id_immutable) raises an exception if community_id changes on an existing row -- the migration's own comment states this enforces that 'a channel can never be re-tenanted.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:72-127"
  - statement: "The channels table carries a unique index on (community_id, nip29_group_id) where nip29_group_id is not null, and a separate unique index on (community_id, participant_hash) where participant_hash is not null -- both scoped uniqueness constraints, not global ones, per the migration's own comment 'nip29 group id and DM participant hash are unique WITHIN a community, not globally.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:101-105"
  - statement: "The channels table also carries topic/topic_set_by/topic_set_at, purpose/purpose_set_by/purpose_set_at, canvas, max_members, topic_required, and ttl_seconds/ttl_deadline columns -- attributes of a channel as a persisted entity that exist independent of any one channel type."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:72-99"
  - statement: "The channel_members table keys on a composite primary key (community_id, channel_id, pubkey) with a foreign key to channels(community_id, id) ON DELETE CASCADE, and carries role (defaulting to 'member'), joined_at, invited_by, removed_at, removed_by and hidden_at columns -- membership is per-(channel, pubkey), not a separate identity."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:132-145"
  - statement: "buzz-core's kind registry defines the NIP-29 addressable group-state range 39000-39003 as KIND_NIP29_GROUP_METADATA=39000, KIND_NIP29_GROUP_ADMINS=39001, KIND_NIP29_GROUP_MEMBERS=39002 and KIND_NIP29_GROUP_ROLES=39003, and separately defines KIND_CHANNEL_METADATA=41 with the doc comment 'NIP-01: Channel metadata (replaceable). Not used by Buzz today.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Root AGENTS.md states that channels are scoped by h tags (the NIP-29 group tag), not e tags, for filters and queries operating on events inside a channel; that this applies to events inside a channel, while addressable events describing the channel itself carry its id in a d tag instead across kind:39000 (metadata), kind:39001, and kind:39002 (membership); and that a user's channel list is resolved ('get_channels') from the d tag of their kind:39002 events, not from h."
    entry_class: FACT
    evidence:
      - "AGENTS.md:169-174"
  - statement: "buzz-cli's channel-listing path implements exactly the two-step resolution AGENTS.md describes: to list the caller's own channels it first queries kind:39002 filtered by #p on the caller's pubkey and extracts each result's d tag as a channel id, then queries kind:39000 filtered by #d on those collected channel ids to fetch metadata; listing all channels (not just the caller's) instead queries kind:39000 with no membership filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:25-65"
  - statement: "buzz-core's NIP-01 filter matcher treats an event's own h tags as authoritative when present -- an event carrying h tags that don't match the filter's #h values is rejected outright -- and only falls back to the event's stored channel_id association when the event carries no h tag at all, which the code's own comment attributes to kind:7 reactions and kind:5 deletions deriving their channel from the target event rather than carrying an h tag themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:68-100"
  - statement: "buzz-db's replace_addressable_event keys its replacement key on channel_id specifically because it serves 'relay-signed NIP-29 group metadata (kind 39000-39002) where the relay is the author and channel_id distinguishes groups', in explicit contrast to replace_parameterized_event, which keys ordinary user-submitted NIP-33 replaceable events on (pubkey, d_tag) globally with no channel_id in the replacement key -- the code comment states this pair of functions exists precisely because channel-describing events and ordinary addressable events replace under different keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:5145-5162"
  - statement: "VISION_PROJECTS.md's own Capability | Status table marks the row 'Channels, forums, DMs, canvases' as 'Ships today'."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "The invariants this node states are exercised by real tests, not merely asserted: buzz-db/src/channel.rs carries unit tests including test_unarchive_expired_ephemeral_channel_renews_ttl_deadline (the TTL/archival behavior), and crates/buzz-test-client/tests/e2e_relay.rs carries end-to-end tests over a real relay connection including test_valid_channel_survives_malformed_or_empty_h_sibling (the h-tag scoping fallback), test_private_channel_admin_can_invite, test_private_channel_any_member_can_invite, test_private_channel_non_member_cannot_invite, and test_private_channel_member_cannot_grant_admin (visibility and role-hierarchy enforcement)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "Both client codebases carry a dedicated channels feature module with real, non-stub source: the desktop app's desktop/src/features/channels/channelSnapshot.ts (channel state projection) and the mobile app's mobile/lib/features/channels/channel.dart (channel model), each accompanied by sibling files for membership, actions, and providers/hooks in the same directory."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/channelSnapshot.ts"
      - "mobile/lib/features/channels/channel.dart"
  - statement: "A channel therefore names one persisted conversational/collaboration space, identified by a UUID that is stable across its Postgres row (channels.id), its NIP-29 group state (the d tag on kind:39000/39001/39002), and every message event scoped into it (the h tag) -- three different mechanisms converging on the same id is what lets a channel be addressed identically whether the caller is Buzz's own stack or an external NIP-29 client."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:72-99"
      - "crates/buzz-core/src/kind.rs"
      - "AGENTS.md:169-174"
    confidence: 0.85
  - statement: "Issue #727's parent Feature #612 batches this task alongside sibling issues #721-726 (channel administrators, deletion, membership, metadata, templates and types) and #728-731 (dm-channel, forum-channel, stream-channel, workflow-channel), scoping this node to the channel-capability overview and taxonomy shared by every channel type, and directing that this node not re-derive the depth those siblings own nor add relationships to their ids since none of them are merged into origin/launchpad's corpus yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch instructions for issue #727 (Feature #612), naming the sibling issue split and the resulting scope boundary"
  - statement: "At the recorded revision, origin/launchpad's corpus tree carries no node under a capabilities/ or interfaces-events/ path -- every merged node outside schema/ is under architecture/, standards/, templates/, AGENTS.md or README.md -- so this node is the corpus's first capabilities-typed instance and no interface or flow node yet exists for channel-driven capabilities to reference."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> architecture/**, schema/**, standards/**, templates/**, AGENTS.md, README.md only, no capabilities/ or interfaces-events/ path present, checked at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Channels: capability

Buzz organizes every conversation, thread, canvas, and workflow run inside a
**channel** — a named, persisted space that a set of members (human users,
agents, and bots) belong to, post into, and are scoped by. A channel is what a
human user picks from the sidebar, what a NIP-29-aware external client joins as
a group, and what an agent's every `buzz` CLI call is scoped against. Creating a
channel gives a community a durable place for messages, threads, canvases, and
(for the workflow variant) an internal execution context; joining one is what
lets a member read and post into it and what a workflow or approval gate
addresses when it needs a place to report back to. The primary actors are the
channel's members (by role: owner, admin, member, guest, or the separate bot
designation) and the relay, which is the sole author of the channel's own
NIP-29 group-state events; the outcome a channel exists to produce is a
consistent, addressable scope that every other Buzz capability — messaging,
threads, canvases, workflows, search — can be built against without each
reinventing what "which conversation is this" means.

## Behavioral rules and constraints

- **One channel, one persisted identity, three converging representations.**
  A channel is one row in Postgres (`channels.id`, a UUID), one NIP-29 group
  (its metadata/admins/members state at kind:39000/39001/39002, keyed by that
  same UUID as the `d` tag), and one scoping value on every message inside it
  (the `h` tag on kind:9/40002-class events). All three resolve to the same
  id, which is what lets Buzz's own stack and an external NIP-29 client agree
  on what "this channel" means.
- **`community_id` is immutable.** A channel can never be re-tenanted to a
  different community once created — enforced by a database trigger that
  raises on `UPDATE`, not merely a convention.
- **Group-state events are relay-signed, not member-authored.** kind:39000
  (metadata), kind:39001 (admins), and kind:39002 (membership) are produced
  and replaced by the relay itself as the channel's state changes; they are
  not ordinary user-submitted NIP-33 events, and the database layer keys
  their replacement on `channel_id` for exactly that reason, distinct from
  the `(pubkey, d_tag)` key ordinary addressable events replace on.
- **Scoping is directional: `h` inside, `d` for the descriptor.** Filters and
  queries for events happening *inside* a channel scope on its `h` tag; the
  addressable events that *describe* the channel (its metadata, admin list,
  member list) instead carry the channel id in their own `d` tag. A caller's
  own channel list is resolved from the `d` tag of their kind:39002 events,
  never by scanning `h` tags.
- **`h`-tag matching falls back to a stored association only when an event
  carries no `h` tag of its own.** Reactions and deletions derive their
  channel from the event they target rather than carrying an `h` tag
  themselves, so the filter matcher's channel check falls back to the
  stored `channel_id` only for that narrow case; any event that does carry
  explicit `h` tags is matched strictly against them.
- **Membership is scoped per channel, not global.** A member's role, join
  time, and removal state are recorded per `(community, channel, pubkey)`;
  the same pubkey can hold different roles in different channels.
- **Two identifiers are unique per community, not globally**: a channel's
  NIP-29 group id and a DM channel's participant hash. The same values could
  in principle repeat across two different communities without conflict.
- **Optional per-channel policy, not required by every variant**: a topic/
  purpose pair with who-set-it/when-set-it provenance, a `topic_required`
  flag forcing posts to declare a topic, an optional member cap
  (`max_members`), and an optional TTL/deadline pair for a channel that
  auto-archives if no message arrives before its deadline.

## Variants

Every channel carries exactly one `channel_type` from a closed set of four,
and exactly one `visibility` from a closed set of two — these two axes are
independent of each other:

- **stream** — a linear message stream; the default type for an ordinary
  channel.
- **forum** — threaded, forum-style discussion.
- **dm** — a direct-message conversation between a fixed participant set,
  identified by a per-community-unique participant hash rather than a
  chosen name.
- **workflow** — an internal channel a workflow run executes inside, not a
  general-purpose conversation space.

Each of the four variants, plus the cross-cutting concerns of who administers
a channel, how membership works, what its metadata contains, how it can be
templated, and how it is deleted, is documented as its own capability node —
see *Boundary* below. This node states what every variant has in common, not
how any one of them differs from the others.

Independently, every channel — regardless of type — is either **open**
(searchable, anyone can join without an invite) or **private** (hidden,
invite-only).

## Maturity

**Shipped.** VISION_PROJECTS.md's own Capability | Status table marks
"Channels, forums, DMs, canvases" as "Ships today," and the schema, kind
registry, relay-side replacement logic, and both the desktop and mobile
client feature modules cited above are real, exercised code at the recorded
revision — not a design sketched but not yet built. That "exercised" claim
is not just asserted: `buzz-db/src/channel.rs`'s own unit tests cover TTL
expiry/archival behavior, and `buzz-test-client/tests/e2e_relay.rs`'s
end-to-end tests exercise `h`-tag scoping fallback and private-channel
visibility/role enforcement over a real relay connection — see the
verification evidence entry above for the specific test names.

## Boundary

This node does not describe:
- **How each specific channel type behaves** (stream, forum, dm, workflow)
  — each is its own capability node (planned: dm-channel, forum-channel,
  stream-channel, workflow-channel), not yet merged at the recorded
  revision. This node states only the invariants every type shares.
- **Administration, membership management, metadata editing, channel
  templates, and channel deletion** as their own procedures — each is its
  own planned capability node (channel-administrators, channel-membership,
  channel-metadata, channel-templates, channel-deletion), not yet merged.
  This node names the shared data shape (role hierarchy, membership table,
  metadata columns) only to the extent needed to state what a channel *is*.
- **How a channel is built** — the relay's event-ingestion pipeline, the
  Postgres schema in full, and the WebSocket/HTTP surfaces that expose it.
  See the architecture nodes in *Relationships* for that.
- **The step-by-step path one interaction through a channel takes** (for
  example, joining one, or a message traversing ingestion to fan-out) — a
  flow node's territory, not this one's.
- **How the running relay operates a channel in production** (deployment
  topology, monitoring) — the `operations` corpus surface, not this one.

## Relationships

- `references: architecture-containers-relay` — the relay is the sole
  author of a channel's NIP-29 group-state events and the component that
  enforces `h`-tag scoping on every other event.
- `references: architecture-flows-event-ingestion` — the pipeline a
  channel-scoped event travels through on submission.
- `references: architecture-flows-live-fanout` — the pipeline that delivers
  a channel-scoped event to its members in real time.
- `references: architecture-principles-community-is-security-boundary` — a
  channel exists inside exactly one community, and `community_id`
  immutability is this node's own database-level expression of that
  principle.

No `part-of`, `implements`, or `depends-on` edges are declared. The four
sibling capability nodes this node's *Boundary* section names by task title
(dm-channel, forum-channel, stream-channel, workflow-channel, plus the
administrators/deletion/membership/metadata/templates nodes) are not merged
into `origin/launchpad`'s corpus at the recorded revision, so none of their
ids are valid relationship targets yet — per `AGENTS.md`'s rule to resolve
every declared target against the merge branch, not the author's own
worktree. The split between this node and those is stated in prose above
instead.

## Scope and omissions

**This node covers** what a channel fundamentally is in Buzz: its persisted
identity across Postgres, NIP-29 group state, and event scoping; the
invariants every channel shares regardless of type (immutable community,
relay-authored group state, `h`-tag-inside/`d`-tag-for-the-descriptor
scoping, per-channel membership); the four closed `channel_type` variants
and the two `visibility` states; and its current shipped maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the stream/forum/dm/workflow variants each specifically behave | the planned per-type capability nodes (not yet merged) |
| Channel administration and permission enforcement in depth | the planned channel-administrators node (not yet merged) |
| Membership add/remove/invite procedures in depth | the planned channel-membership node (not yet merged) |
| Metadata (name/topic/purpose/canvas) editing rules | the planned channel-metadata node (not yet merged) |
| Channel templates | the planned channel-templates node (not yet merged) |
| Channel deletion and archival procedure | the planned channel-deletion node (not yet merged) |
| The step-by-step flow through joining or messaging in a channel | a flow-typed node, not yet drafted for this capability |
| The CLI/HTTP/protocol surface a channel is exposed through | an interface-typed node, not yet drafted; today only `buzz-cli`'s `channels.rs` and the relay's WebSocket/HTTP handlers are cited directly as evidence |
| How the relay is deployed and operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No corresponding template exists for `type: capabilities` instance nodes
  beyond `templates/capability.md` itself**, which this node follows; whether
  its *Required sections* (Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions) fit a capability with this many shared
  cross-cutting invariants as cleanly as they fit a single-purpose capability
  was not established elsewhere before this node — it is this node's own
  first test of that template in practice.
- **The exact runtime behavior of `ChannelType::Workflow` channels** (how a
  workflow run's internal channel differs operationally from an ordinary
  stream channel beyond the type tag) was not traced through
  `buzz-workflow` for this node — it is left to the planned workflow-channel
  node.
- **Whether any of the ten sibling capability nodes named in *Boundary* have
  since merged** was checked only against `origin/launchpad` at the recorded
  revision (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`); a later reader should
  re-check before assuming the "not yet merged" statements above still hold.
