---
id: capabilities-channels-channel-administrators
type: capabilities
status: draft
origin: upstream
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "A channel member's role is one of Owner, Admin, Member, Guest or Bot, with a strict linear hierarchy Owner > Admin > Member > Guest for permission checks (Bot is a separate designation outside that hierarchy, always at permission level 0); `MemberRole::is_elevated` returns true only for Owner and Admin, and `MemberRole::has_at_least` compares numeric `permission_level()` values (Owner=4, Admin=3, Member=2, Guest=1, Bot=0)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "`is_admin_kind` classifies the NIP-29 group-admin event range 9000-9022 as needing pre-storage validation, and `crates/buzz-relay/src/handlers/ingest.rs`'s ingest pipeline calls `is_admin_kind`/`validate_admin_event` on every event in that range before it is stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`buzz_core::kind` defines the NIP-29 group-admin kind constants a channel administrator's actions are built from: KIND_NIP29_PUT_USER=9000 (add member / change role), KIND_NIP29_REMOVE_USER=9001 (remove member), KIND_NIP29_EDIT_METADATA=9002 (channel settings), KIND_NIP29_DELETE_EVENT=9005 (delete a message), KIND_NIP29_CREATE_GROUP=9007, KIND_NIP29_DELETE_GROUP=9008 (delete the channel), plus the addressable KIND_NIP29_GROUP_ADMINS=39001 and KIND_NIP29_GROUP_MEMBERS=39002 discovery events."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "For kind:9000 (PUT_USER), `validate_admin_event` requires the acting pubkey to already be an active member of a private channel before it may add anyone; granting an elevated role (Owner or Admin) to the target requires the actor's own role to already be elevated; and changing an existing active member's role in either direction requires the actor to be Owner or Admin, with an additional guard that refuses to demote the channel's last remaining Owner (\"cannot demote the last owner — transfer ownership first\") so a channel can never be left without one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "For kind:9001 (REMOVE_USER), an actor may always remove themselves unless they are the channel's last remaining Owner (\"cannot remove the last owner\"); removing a different member requires the actor to hold role Owner or Admin, or -- for a Bot target specifically -- to be recorded as that agent's owning human via `is_agent_owner`; a non-member actor is rejected outright, including for their own bot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "For kind:9002 (EDIT_METADATA), changing name, about, archived, visibility or ttl requires the actor to hold role Owner or Admin (or to be the owning human of an active Owner-role agent in the channel), while changing topic or purpose only requires the actor to be any active member -- two different privilege tiers folded into one event kind, distinguished by which tags the event carries."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "For kind:9005 (DELETE_EVENT), the event's own author may delete their own message while still an active member or while the channel is Open; deleting someone else's message, or an author's own message after losing membership in a Private channel, requires the actor to hold role Owner or Admin in the target's channel, or to be the owning human of the message's agent author."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "For kind:9008 (DELETE_GROUP), only a member with role Owner may delete the channel -- an Admin cannot, and a non-owner actor is rejected with the literal message \"only owner can delete group\" -- unless the actor is the owning human of an active Owner-role agent in the channel. This is the one channel-admin action this repository's own code restricts to Owner and deliberately excludes Admin from, diverging from kind:9001's Owner-or-Admin rule by the comment's own account (\"diverges from kind:9001 intentionally\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "After any membership-affecting admin command is applied, the relay re-materializes the channel's kind:39001 addressable \"group admins\" event by filtering the channel's current member list to only those rows whose role is `owner` or `admin`, and tagging each with a `p` tag carrying that pubkey and its role string -- kind:39001 is, structurally, the queryable list of a channel's administrators."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`buzz-sdk`'s `build_add_member`, `build_remove_member`, `build_update_channel` and `build_delete_channel` construct kind:9000, kind:9001, kind:9002 and kind:9008 events respectively; `build_add_member` accepts an optional `MemberRole` that is written as a `role` tag on the kind:9000 event, which is how a role (including `admin`) is granted through the SDK."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`buzz-cli`'s `channels add-member --role <owner|admin|member|guest|bot>`, `channels remove-member`, `channels update` (name/about/visibility/ttl) and `channels delete` subcommands are the agent-facing surface for these admin actions; `cmd_add_channel_member` validates `--role` against exactly those five strings before building the underlying kind:9000 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs"
  - statement: "Integration test `test_private_channel_admin_can_invite` demonstrates that a member granted role Admin by the channel Owner can subsequently add a new member to a Private channel, and `test_private_channel_member_cannot_grant_admin` demonstrates that a non-elevated regular member's attempt to grant the Admin role to someone else is rejected by the relay with a message referencing elevated roles/owner/admin -- both exercising `validate_admin_event`'s kind:9000 rules end to end over a live relay connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "Integration test `test_nip29_relay_rejects_last_owner_self_demotion` demonstrates that a channel's sole Owner attempting to demote themselves to Member via a kind:9000 event is rejected by the relay (not silently accepted and then failed downstream), and that the actor's stored role remains `owner` afterward -- exercising the last-owner-demotion guard end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The tests cited above (`crates/buzz-test-client/tests/e2e_relay.rs`) are marked `#[ignore]` by default, per the file's own module documentation, because they require a running relay instance; they are run explicitly with `cargo test --test e2e_relay -- --ignored` rather than as part of a default `cargo test` invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "Root VISION_PROJECTS.md's Status table marks the parent capability row \"Channels, forums, DMs, canvases\" as \"Ships today\", which this node treats as corroborating evidence that the channel capability family (including its administrator role model) is shipped product behavior rather than a designed-but-unbuilt feature, distinct from and secondary to the code- and test-level evidence above which demonstrates the administrator behavior directly."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md"
  - statement: "Channels are scoped in Nostr events with an `h` tag (the NIP-29 group tag) rather than an `e` tag, and this repository's own root AGENTS.md states that filters and queries operating within a channel must scope to that `h` tag -- the same tag every admin-command event cited above (`h`, `p`, `role`, etc.) carries to identify which channel the action targets."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-event-ingestion
---

# Channel administrators: capability

A channel's Owner can promote one or more of its members to the Admin role,
and having done so, those Admins can manage the channel's membership and
settings on the Owner's behalf without needing Owner-level control over the
channel itself. In practice this means an Admin can invite and remove
ordinary members and guests, change the channel's name, description,
visibility and message-retention (`ttl`) settings, delete other members'
messages, and — through the relay's own addressable `kind:39001` "group
admins" event — be discoverable by any client as one of the channel's current
administrators alongside its Owner(s). The primary actors are the channel's
Owner (who grants and revokes the Admin role, and who alone can permanently
delete the channel), the Admin (who exercises delegated management authority
day to day), and ordinary Members, Guests and Bots (who are the subjects of
an Admin's actions but hold no admin authority themselves). The outcome this
capability exists to produce is delegation without abdication: an Owner can
share the operational burden of running an active channel while keeping sole
authority over the channel's existence and its ownership succession.

## Maturity

Shipped. `buzz-core::channel::MemberRole` defines the Owner/Admin/Member/
Guest/Bot hierarchy and its permission-comparison helpers; `buzz-relay`'s
`validate_admin_event` enforces Owner/Admin-gated authorization for every
NIP-29 group-admin event kind (9000, 9001, 9002, 9005, 9008) before the event
is stored; `buzz-sdk` and `buzz-cli` expose the corresponding builders and
subcommands; and `crates/buzz-test-client/tests/e2e_relay.rs` carries
integration tests that exercise the admin-grant, admin-invite, and
last-owner-protection paths against a live relay. Root `VISION_PROJECTS.md`'s
own Status table separately marks the parent "Channels, forums, DMs,
canvases" capability row "Ships today".

## Rules and constraints

- **Role hierarchy and elevation.** Owner > Admin > Member > Guest is a
  strict numeric hierarchy (`permission_level()` 4/3/2/1); Bot sits outside
  it at level 0 and can never satisfy an elevated-role check on its own
  account. Only an actor whose own role is already Owner or Admin
  (`MemberRole::is_elevated`) may grant Owner or Admin to someone else, or
  change an existing active member's role at all, in either direction.
- **The last-Owner invariant.** A channel can never be left with zero
  Owners: `validate_admin_event` refuses to demote the sole Owner via
  kind:9000, refuses to remove the sole Owner via kind:9001, and refuses the
  sole Owner's own kind:9022 leave-request — all three rejected with the
  event kept out of storage rather than accepted and left to fail silently
  downstream.
- **Two privilege tiers inside one event kind.** kind:9002 (EDIT_METADATA)
  gates `name`/`about`/`archived`/`visibility`/`ttl` changes to Owner/Admin,
  but leaves `topic`/`purpose` open to any active member — the same event
  kind carries both a channel-administration action and an ordinary-member
  action, distinguished only by which tags it carries.
- **Owner-only carve-out.** Deleting the channel itself (kind:9008,
  DELETE_GROUP) is the one admin-shaped action Admin does **not** unlock —
  it is Owner-only by explicit design (the code comment calls this out as an
  intentional divergence from kind:9001's Owner-or-Admin rule), aside from
  the agent-owner variant below.
- **Agent-owner variant.** For a Bot member, the Bot's registered owning
  human can act with admin-equivalent authority over that specific Bot's
  membership (kind:9001) or over the channel it owns (kind:9008), even when
  that human is not themself a channel member — a narrower delegation than
  full Admin, scoped to the one Bot they own.
- **Message moderation is admin-shaped but per-message.** kind:9005 (delete
  another member's message) is gated the same way as membership
  management — Owner/Admin, or the owning human of the message's agent
  author — rather than requiring the deleting admin to also be the message's
  author.
- **Discoverability.** After any membership change, the relay re-emits
  kind:39001 listing every current Owner/Admin pair — a channel's
  administrator set is a live, queryable NIP-29 addressable event, not
  something a client has to infer from the full member list.

## Boundary

This node does not describe:
- **How the relay is built.** The Rust/Axum service, its deployment and its
  broader responsibilities are `architecture-containers-relay`'s territory;
  this node only cites the specific admin-authorization logic that container
  hosts.
- **The step-by-step path an admin action takes through the system.** The
  general event-validate-store-fan-out sequence every event (admin or not)
  goes through is `architecture-flows-event-ingestion`'s territory; this
  node cites it for where `is_admin_kind`/`validate_admin_event` are called,
  not to re-describe the pipeline.
- **The interface contract of `buzz-cli` or `buzz-sdk` as boundary
  surfaces.** No interface-type corpus node exists yet for either at the
  time this node was written (only `launchpad/docs/corpus/templates/
  interface.md`, a template, exists); this node cites the specific
  admin-related commands/builders directly as evidence of the capability's
  exposure rather than pointing to a node that does not yet exist.
- **Relay-level (community-wide) moderation** — banning, timing out, or
  resolving reports against a pubkey across an entire community
  (kind:9040-9044, `buzz-relay/src/handlers/moderation_commands.rs`) or
  relay-membership administration (kind:9030-9033,
  `buzz-relay/src/handlers/relay_admin.rs`). Those operate above the level
  of a single channel and are a different capability from the one this node
  documents.
- **How the running system is operated day to day** (deployment, monitoring,
  incident response) — the `operations` corpus surface's territory, not
  this one.

## Relationships

- references: `architecture-containers-relay` — the container hosting
  `validate_admin_event` and the rest of the admin-authorization logic cited
  above.
- references: `architecture-flows-event-ingestion` — the ingest pipeline
  every admin-command event passes through before `is_admin_kind`/
  `validate_admin_event` run.

## Scope and omissions

**This node covers** the channel-level Owner/Admin role hierarchy, the
NIP-29 group-admin event kinds (9000, 9001, 9002, 9005, 9008) an
administrator's actions are built from and the per-kind authorization rules
`validate_admin_event` enforces for each, the last-Owner invariant, the
Owner-only carve-out for deleting a channel, the agent-owner delegation
variant, the addressable kind:39001 admin-discovery event, and the
`buzz-sdk`/`buzz-cli` surfaces that expose these actions.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay container is built and deployed | `architecture-containers-relay` |
| The general event ingest/validate/store/fan-out pipeline | `architecture-flows-event-ingestion` |
| The `buzz-cli`/`buzz-sdk` boundary contract as an interface | not yet drafted (only `templates/interface.md` exists) |
| Relay-wide (cross-channel) moderation: bans, timeouts, report resolution | `crates/buzz-relay/src/handlers/moderation_commands.rs` (kind:9040-9044) |
| Relay-membership administration (distinct from channel membership) | `crates/buzz-relay/src/handlers/relay_admin.rs` (kind:9030-9033) |
| The step-by-step user/agent flow of promoting someone to Admin | not yet drafted as a flow-type node |

**Expected but not verified when this node was written:**
- **The desktop and mobile client UI for granting/revoking the Admin role**
  was not inspected — this node verifies the relay-side authorization and
  the `buzz-cli`/`buzz-sdk` surfaces only, not whether or how the Tauri
  desktop app or the Flutter mobile app exposes role management in its UI.
- **The `buzz-test-client` integration tests cited above were read but not
  executed** as part of authoring this node (they require a running relay
  and are `#[ignore]`d by default); their assertions were verified by
  reading the test bodies, not by observing a passing run.
- **kind:9007 (CREATE_GROUP) was not analyzed for admin-specific rules**
  beyond confirming `validate_admin_event` skips h-tag extraction for it —
  channel creation establishes the first Owner but was judged out of scope
  for a node about administering an *existing* channel.
