---
id: capabilities-channels-dm-channel
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
  - statement: "buzz-db's own module doc for DM persistence states: 'DMs are channels with channel_type='dm' and visibility='private'. Participant sets are immutable -- adding a member creates a NEW DM.' A DM is therefore not a separate storage concept from a regular channel; it is a channel row distinguished by its channel_type and visibility columns."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/dm.rs:1-4"
  - statement: "root VISION_PROJECTS.md's own Capability/Status table lists 'Channels, forums, DMs, canvases' as 'Ships today', its top maturity marker, alongside the workflow engine, MCP/ACP harness, Blossom media and git hosting."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:245-259"
  - statement: "buzz-core/src/channel.rs's ChannelType enum has a dedicated Dm variant (canonical string 'dm'), alongside Stream, Forum and Workflow, shared by both the SDK (client-side event building) and the DB layer (server-side persistence) so both sides agree on the same four-way channel taxonomy without pulling sqlx/tokio into the SDK."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-100"
  - statement: "buzz-core/src/kind.rs defines a dedicated 41000-41999 event-kind range for direct messages: KIND_DM_OPEN=41010 ('Open/create DM, p-tags = participants'), KIND_DM_ADD_MEMBER=41011 ('Add member to group DM'), KIND_DM_HIDE=41012 ('Hide DM from sidebar'), and KIND_DM_CREATED=41001 ('A new direct-message conversation was created')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:505-513"
  - statement: "buzz-relay's command_executor dispatches KIND_DM_OPEN, KIND_DM_ADD_MEMBER and KIND_DM_HIDE to handle_dm_open, handle_dm_add_member and handle_dm_hide respectively, and each handler persists the triggering command event and calls the corresponding buzz-db mutation (open_dm / open_dm / hide_dm) inside the same database transaction, committing both together or neither."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:66-68"
      - "crates/buzz-relay/src/handlers/command_executor.rs:370-501"
      - "crates/buzz-relay/src/handlers/command_executor.rs:503-638"
      - "crates/buzz-relay/src/handlers/command_executor.rs:640-711"
  - statement: "handle_dm_open requires 1-8 additional participants named in p tags (9 total with the caller), always includes the caller in the final participant set even if the caller omitted their own pubkey, and rejects a request naming more than 8 others before any database call is made."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:380-406"
  - statement: "buzz-db's create_dm additionally enforces, at the database layer, that a DM has 2-9 participants and that every participant pubkey is exactly 32 bytes, independent of and in addition to the relay handler's own 1-8-others check."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/dm.rs:101-124"
  - statement: "A DM's identity is a stable SHA-256 fingerprint of its sorted, deduplicated participant pubkey set (compute_participant_hash), stored in a nullable channels.participant_hash column guarded by a partial unique index on (community_id, participant_hash) WHERE participant_hash IS NOT NULL -- so at most one DM channel can exist per distinct participant set per community, and opening a DM with the same participants (in any order) is idempotent and returns the existing channel rather than creating a duplicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/dm.rs:43-58"
      - "crates/buzz-db/src/dm.rs:126-155"
      - "migrations/0001_initial_schema.sql:94"
      - "migrations/0001_initial_schema.sql:104-105"
  - statement: "Because a DM's participant set is content-addressed by compute_participant_hash and channels.participant_hash is immutable once set, adding a participant cannot mutate an existing DM's row -- handle_dm_add_member instead computes the expanded participant set and calls the same open_dm path, which creates a brand-new DM channel for that larger set (or returns an existing one with that exact expanded set) rather than adding a member to the original conversation in place."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:503-587"
      - "crates/buzz-db/src/dm.rs:1-4"
  - statement: "Hiding a DM is per-member and reversible: hide_dm sets channel_members.hidden_at for the caller only (leaving their membership row otherwise intact), and open_dm automatically clears hidden_at for the caller whenever they re-open a DM with the same participant set, so a hidden DM reappears the next time any participant messages it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/dm.rs:356-449"
      - "migrations/0001_initial_schema.sql:132-145"
  - statement: "On first creation (was_created = true), handle_dm_open publishes a channel system message of type 'dm_created' naming the actor and participants, emits NIP-29-style group discovery events, and sends a membership-added notification to every participant; on re-open of an already-existing DM (was_created = false) it instead republishes only the caller's own NIP-DV visibility snapshot, so a returning participant's sidebar updates without re-notifying everyone else."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:433-487"
  - statement: "emit_group_discovery_events publishes a kind:39000 (NIP-29 group metadata) event for every channel, and specifically for a channel_type=='dm' channel it adds a 'hidden' tag (so DMs are hinted away from public group listings) and one 'p' tag per participant pubkey directly in that metadata event, plus a 't' tag carrying the channel_type ('dm') so clients can distinguish a DM from a stream/forum channel without a separate lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1060-1130"
  - statement: "KIND_DM_CREATED (kind:41001) is declared in buzz-core/src/kind.rs and buzz-cli's cmd_list_dms queries the relay with exactly {\"kinds\":[41001], \"#p\":[my_pubkey]} to list a user's DM conversations, but a repository-wide search of crates/ found no site where the relay actually constructs or publishes a kind:41001 event -- the discovery mechanism this node found in code is the kind:39000 group-metadata event described above, not kind:41001."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/dms.rs:1-46"
      - "grep_recursive('KIND_DM_CREATED', path='crates/') -> only crates/buzz-core/src/kind.rs (the constant's own definition); zero emission sites in buzz-relay, run against this node's recorded revision"
  - statement: "Because no kind:41001 emission site was found, buzz-cli's 'dms list' command -- which queries only kind:41001 -- is likely querying for events the relay never publishes, at this recorded revision; the DM discovery clients actually receive is the kind:39000 group-metadata event."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/commands/dms.rs:8-24"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1060-1130"
    confidence: 0.7
  - statement: "buzz-cli exposes an agent-facing 'buzz dms' subcommand group (List, Open, AddMember, Hide) whose Open variant accepts 1-8 --pubkey flags, and cmd_open_dm builds and signs a kind:41010 event client-side (using the SDK's own EventBuilder/Kind/Tag types plus a client-generated 'd' tag for local tracking, since build_dm_open itself attaches no 'd' tag) before submitting it through the same submit_event path used for every other channel command."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:803-832"
      - "crates/buzz-cli/src/commands/dms.rs:47-72"
      - "crates/buzz-sdk/src/builders.rs:1674-1689"
  - statement: "buzz-sdk provides typed event builders build_dm_open(pubkeys) (kind 41010, validates 1-8 hex pubkeys) and build_dm_add_member(channel_id, pubkey) (kind 41011, tags an 'h' channel reference plus the new participant's 'p' tag) as the SDK-level construction path for the two DM mutation kinds a client signs directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1674-1696"
  - statement: "The desktop app implements a dedicated DM compose surface (NewMessageScreen, described in its own doc comment as a 'conversation-shaped compose surface for starting a direct message') built on a useOpenDmMutation hook, plus separate DM-specific sidebar sorting (dmSidebarSort.ts) and channel-label formatting (channelLabels.ts) distinct from ordinary channel rendering."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/NewMessageScreen.tsx:1-29"
      - "desktop/src/features/sidebar/lib/dmSidebarSort.ts"
      - "desktop/src/features/sidebar/lib/channelLabels.ts"
  - statement: "The mobile Flutter app implements DM-specific display-name formatting distinct from ordinary channel names -- isGenericDmChannelName recognizes auto-generated DM/group-DM names ('DM', 'Direct Message(s)', 'Group DM (n)'), and formatDmParticipantDisplayName renders a truncated, '+n more'-style participant list for a DM's display name -- confirming this capability ships on the mobile client as well as desktop, the relay and the CLI."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/dm_channel_labels.dart:1-20"
  - statement: "A case-insensitive search of web/ (the browser-based repo/community client) for DM-related identifiers (dm_channel, DmChannel, open dm, direct message) returned zero matches, so at this recorded revision the DM capability is not exposed through the web client -- only through the relay's own protocol surface, buzz-cli, desktop and mobile."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('dm_channel|DmChannel|open.dm|direct message', path='web/') -> zero matches, run against this node's recorded revision"
  - statement: "KIND_GIFT_WRAP (kind:1059) is documented in buzz-core/src/kind.rs as the 'NIP-17: Outer envelope for private DMs -- hides sender, content, timestamp', a distinct end-to-end-encrypted delivery mechanism used elsewhere in the relay (owner-pubkey-mismatch allowance in the EVENT handler, and gating logic in the push-notification worker); it is never referenced by handle_dm_open, handle_dm_add_member, handle_dm_hide or buzz-db's dm.rs, so the DM-channel capability this node documents is a plaintext, channel-scoped conversation model, not the gift-wrapped NIP-17 ciphertext model."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:59-60"
      - "crates/buzz-relay/src/handlers/event.rs:659-668"
      - "crates/buzz-relay/src/push_runtime.rs:297"
  - statement: "The only automated test coverage found for this capability's own logic is buzz-db's pure compute_participant_hash unit tests (order-independence, deduplication, differing-sets, output-length); no integration or end-to-end test exercising handle_dm_open, handle_dm_add_member, handle_dm_hide, or buzz-db's create_dm/open_dm/hide_dm against a real Postgres instance was found under crates/buzz-relay, crates/buzz-db or crates/buzz-test-client at this recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/dm.rs:519-557"
      - "grep_recursive('open_dm|create_dm|hide_dm|handle_dm', path='crates/buzz-test-client/tests/') -> zero matches, run against this node's recorded revision"
---

# DM channel: capability

Buzz lets any user or agent start a private conversation with one or more
other members of the same community without creating a named, discoverable
channel first. A **DM (direct message)** is a Buzz channel like any other --
messages, threads, reactions and the rest of the messaging surface all work
the same way inside it -- distinguished only by its `channel_type` ('dm'),
its `visibility` ('private'), and an immutable participant set that
identifies it. Opening a DM with the same set of people always returns the
same conversation; adding a participant to a group DM creates a new
conversation for the expanded set rather than mutating the original one.
This capability ships today, per root `VISION_PROJECTS.md`'s own
Capability/Status table ("Channels, forums, DMs, canvases -- Ships today").

## Maturity

**Shipped.** `VISION_PROJECTS.md`'s own Status table marks "Channels, forums,
DMs, canvases" as shipping today. That maturity claim is corroborated by
working code end to end at the recorded revision: `buzz-db`'s DM persistence
module (`create_dm`, `open_dm`, `hide_dm`, `list_dms_for_user`), `buzz-relay`
command handlers (`handle_dm_open`, `handle_dm_add_member`, `handle_dm_hide`)
wired into the event-ingestion dispatch table, a dedicated event-kind range
(41000-41999) in `buzz-core`, `buzz-sdk` event builders, a `buzz dms`
subcommand group in `buzz-cli`, a dedicated DM compose surface in the desktop
app, and DM-specific display-name handling in the mobile app.

## Behavioral rules and constraints

- **A DM is a channel, not a separate entity.** Storage, membership and
  message delivery reuse the same `channels`/`channel_members` tables and
  pipeline as every other channel type; only `channel_type='dm'` and
  `visibility='private'` mark it as a DM.
- **Participant count:** 2-9 total participants. The relay handler rejects a
  request naming zero or more than 8 *other* participants before any
  database call; `buzz-db`'s `create_dm` independently re-enforces 2-9 total
  and a 32-byte pubkey length for every participant.
- **Identity is the participant set, not a name.** A DM's identity is
  `compute_participant_hash` -- SHA-256 over the sorted, deduplicated
  participant pubkeys -- stored in `channels.participant_hash` under a
  partial unique index per community. Opening a DM is therefore idempotent:
  the same set of people (in any order) always resolves to the same channel.
- **Participant sets are immutable.** "Adding a member" does not mutate the
  original DM's row. `handle_dm_add_member` computes the expanded
  participant set and calls the same `open_dm` path used to create a DM,
  which creates (or returns) the channel keyed to that *larger* set --
  leaving the original, smaller-set conversation untouched and still
  addressable on its own.
- **Hiding is per-member and reversible.** `hide_dm` sets
  `channel_members.hidden_at` for the caller only; re-opening a DM with the
  same participants automatically clears it for that caller, so the
  conversation reappears in their sidebar without re-notifying anyone else.
- **Discovery is via NIP-29 group metadata, not a bespoke DM event.**
  `emit_group_discovery_events` publishes a kind:39000 metadata event for
  every channel; for a DM it tags the event `hidden` (steering it away from
  public group listings), embeds every participant as a `p` tag, and tags
  `t: dm` so a client can distinguish a DM from a stream/forum channel
  without an extra lookup.
- **Two delivery paths exist for the caller's own commands.** First creation
  of a DM triggers a system message, discovery events and a
  membership-notification per participant; re-opening an existing DM instead
  only republishes the caller's own NIP-DV visibility snapshot (kind:30622),
  which is why re-opening does not re-notify the other participants.
- **A defined-but-unused event kind exists in this area.** `KIND_DM_CREATED`
  (kind:41001) is declared and `buzz-cli`'s `dms list` command queries
  exactly that kind, but no code path in this repository was found that
  publishes a kind:41001 event -- see the `INFERENCE` evidence entry above.
  A reader building against this capability should not assume kind:41001 is
  live traffic without checking the relay version in use.

## Boundary

This node does not describe:

- **How the capability is built.** The container-level shape of the relay
  (`buzz-relay`), the CLI (`buzz-cli`), the desktop app, the mobile app and
  Postgres (`buzz-db`'s schema) that jointly realize this capability is the
  architecture family's territory -- see the `references` relationships
  below for the merged nodes that own that content. This node cites their
  files only as evidence that the capability exists and behaves as
  described, not to duplicate their own descriptions.
- **The interface(s) the capability is exposed through.** The `buzz dms`
  CLI subcommand group's exact flags/output shape, and the relay's
  kind:41010/41011/41012 wire protocol, are an interface-level contract; no
  `interfaces-events`-typed corpus node exists yet at this recorded revision
  for this node to `references`.
- **The step-by-step flow through this capability.** The exact sequence of
  frames/events from a client pressing "New message" through to the DM
  appearing in every participant's sidebar is a flow-level document, not
  covered here structurally (see *Behavioral rules* above for the rules
  that flow would narrate).
- **How the running system is operated.** Nothing here covers deployment,
  monitoring or incident response for the channels/DM tables or the relay
  process that serves them.
- **Gift-wrapped (NIP-17) private messaging.** `KIND_GIFT_WRAP` (kind:1059)
  is a separate, end-to-end-encrypted delivery mechanism used elsewhere in
  the relay (push-notification gating, an owner-pubkey-mismatch allowance in
  the EVENT handler) and carries no reference to the DM-channel handlers or
  `buzz-db::dm` this node documents. The DM channel capability is a
  plaintext, channel-scoped conversation, not gift-wrapped ciphertext.
- **The web client.** A search of `web/` found no DM-related code; at this
  recorded revision the capability is reachable through the relay protocol,
  `buzz-cli`, the desktop app and the mobile app, but not the browser-based
  web client.

## Relationships

- references: `architecture-containers-relay` -- owns the command-dispatch
  and side-effect code (`handle_dm_open`/`handle_dm_add_member`/
  `handle_dm_hide`, `emit_group_discovery_events`) that implements this
  capability's server-side behavior.
- references: `architecture-containers-postgres` -- owns the
  `channels`/`channel_members` schema (`participant_hash`, `hidden_at`,
  `max_members`) this capability's persistence model is built on.
- references: `architecture-containers-cli` -- owns the `buzz dms`
  subcommand group, the primary agent-facing entry point to this capability.
- references: `architecture-containers-desktop` -- owns the DM compose
  surface, DM-specific sidebar sorting and channel-label formatting for
  human users of this capability.
- references: `architecture-containers-mobile` -- owns the Flutter DM
  display-name formatting confirming the capability also ships on mobile.

**Not declared:** `part-of` a broader "channels" capability node, or
`references`/`implements` toward an interface or flow node for this
capability -- none of those sibling nodes exist in `origin/launchpad`'s
corpus tree at the recorded revision (verified via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`; no
`capabilities/` or `interfaces*`/`flows`-typed sibling node for DMs or
channels was present). A future pass should add those edges once the
sibling nodes this batch is producing in parallel are actually merged, per
`AGENTS.md`'s own rule that a relationship target must resolve on the branch
being merged into, not the author's own worktree.

## Verification

- **Unit tests:** `crates/buzz-db/src/dm.rs`'s own test module covers only
  the pure `compute_participant_hash` function -- order-independence,
  deduplication, differing participant sets producing different hashes, and
  a fixed 32-byte output length.
- **Gap, stated rather than silenced:** no integration or end-to-end test
  exercising `handle_dm_open`, `handle_dm_add_member`, `handle_dm_hide`, or
  `buzz-db`'s `create_dm`/`open_dm`/`hide_dm` against a real Postgres
  instance was found under `crates/buzz-relay`, `crates/buzz-db` or
  `crates/buzz-test-client` at this recorded revision. A reader relying on
  this capability for anything safety-critical should treat the
  handler-level behavior described above as read from source, not as
  proven by an executable test at this revision.

## Scope and omissions

**This node covers** the DM channel capability as a product-level thing
Buzz can do: what a DM is (a channel distinguished by type/visibility/
immutable participant set), its participant-count and identity rules, its
create/add-member/hide/list behavior, its NIP-29-based discovery mechanism,
which clients expose it today, and the one internal inconsistency
(`KIND_DM_CREATED` defined but apparently unused) this node's own source
reading turned up.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, CLI, desktop, mobile and Postgres containers are built | `architecture-containers-relay`/`-cli`/`-desktop`/`-mobile`/`-postgres` |
| The `buzz dms` CLI contract and the relay's kind:41010/41011/41012 wire protocol as an interface | a future `interfaces-events` node (none merged yet) |
| The step-by-step flow of opening/using a DM | a future flow node (none merged yet) |
| How the channels/DM tables and the relay process are operated in production | the `operations` corpus surface |
| Gift-wrapped (NIP-17) encrypted private messaging (`KIND_GIFT_WRAP`) | a separate capability node, not this one |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether `KIND_DM_CREATED` (kind:41001) is dead code, a work-in-progress
  feature, or emitted by a code path this search missed** was not
  established beyond the negative grep result recorded above; only that
  `buzz-cli`'s `dms list` command queries a kind this search could not find
  the relay emitting.
- **Whether desktop's `useOpenDmMutation` and the sidebar helpers actually
  render correctly end-to-end against a live relay** was not exercised --
  this node cites their existence and stated purpose from source and doc
  comments, not a runtime observation.
- **Whether any Block-internal (`squareup/*`) deployment path changes this
  capability's behavior** was not checked; per this fork's own `AGENTS.md`,
  that infrastructure is outside this repository's visible source.
