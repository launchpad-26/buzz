---
id: capabilities-channels-channel-metadata
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
  - statement: "buzz-core defines KIND_NIP29_GROUP_METADATA as 39000, an addressable (parameterized-replaceable) NIP-29 group-metadata kind in the 39000-39003 group-state range, and a unit test in the same file asserts 39000 is treated as parameterized-replaceable."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The `channels` table (created in the initial schema migration) carries name, channel_type, visibility, description, canvas, topic, topic_set_by/at, purpose, purpose_set_by/at, ttl_seconds and ttl_deadline columns alongside created_by/created_at/updated_at/archived_at/deleted_at, with a CHECK constraint rejecting the nil UUID as an id and unique partial indexes on (community_id, nip29_group_id) and (community_id, participant_hash)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`buzz_db::channel::create_channel` rejects a `created_by` pubkey that is not exactly 32 bytes, canonicalizes the supplied name through `canonical_channel_name` (stripping leading `#`/whitespace and trailing whitespace), and rejects an empty-after-canonicalization name with `DbError::InvalidData`, before inserting the channel row and bootstrapping the creator as the sole `owner` member in the same transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs"
  - statement: "`buzz_core::channel::canonical_channel_name` strips leading `#` characters and surrounding whitespace so the stored name is prefix-free (clients render the leading `#` themselves), and its own unit tests show a name made entirely of hashes/whitespace canonicalizes to an empty string."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "`buzz_db::channel::update_channel` takes a `ChannelUpdate{name, description, visibility, ttl_seconds}` struct where every field is optional, rejects a call with all four fields absent (`DbError::InvalidData`, \"at least one field must be provided for update\"), re-canonicalizes and rejects an empty `name` the same way `create_channel` does, and builds a dynamic `UPDATE channels SET ...` statement that only touches the columns actually provided."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs"
  - statement: "A TTL change in `update_channel` resets `ttl_deadline` to `NOW() + ttl_seconds` (or clears both `ttl_seconds` and `ttl_deadline` when the caller passes `Some(None)`), and takes a per-channel Postgres advisory transaction lock (`pg_advisory_xact_lock(hashtextextended('buzz_channel_ttl:<community>:<channel>', 0))`) before the UPDATE, documented in-line as a repair for a race with migration 0024's per-channel advisory-locked TTL fast path in the event-insert trigger."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs"
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
  - statement: "`buzz-relay`'s admin-kind dispatcher routes kind:9002 (`KIND_NIP29_EDIT_METADATA`, value 9002) to `handle_edit_metadata`, which reads the `h`-tagged channel id and, per tag present on the event, calls `update_channel` for a `name` tag, `update_channel` for an `about` tag, `set_topic` for a `topic` tag, `set_purpose` for a `purpose` tag, `update_channel` for a `visibility` tag, `update_channel` for a `ttl` tag, and `archive_channel`/`unarchive_channel` for an `archived` tag of `\"true\"`/`\"false\"`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "`validate_admin_event`'s kind:9002 branch runs before storage and requires at least one of the recognized tags (`name`, `about`, `archived`, `topic`, `purpose`, `visibility`, `ttl`); rejects an `archived` tag whose value is not exactly `\"true\"` or `\"false\"`; rejects a `name` tag whose value canonicalizes to an empty string; rejects a `visibility` tag whose value is not exactly `\"open\"` or `\"private\"`; and rejects a `ttl` tag whose value is neither the empty string (clear) nor a positive integer, with a comment stating the parse failure must reject rather than silently clearing the TTL."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Within the same kind:9002 validation branch, a `name`, `about`, `archived`, `visibility` or `ttl` tag requires the actor to hold the `owner` or `admin` role on the channel (or, failing that, to be the NIP-OA owning human of an active owner-role agent in the channel), while a `topic` or `purpose` tag only requires active membership -- an explicit two-tier authorization split within one event kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A mutation on an already-archived channel is rejected by `validate_admin_event` before it reaches any per-kind branch, with one carve-out: a kind:9002 event carrying `[\"archived\", \"false\"]` (an unarchive request) is let through so an archived channel can be restored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A visibility change processed by `handle_edit_metadata` invalidates the tenant's cached accessible-channel lists and the channel's cached visibility, and, specifically on an open-to-private transition, eagerly evicts non-members' live WebSocket subscriptions to that channel on the handling node -- documented in-line as an immediate best-effort measure, with the fan-out access filter named as the cluster-wide correctness backstop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`handle_edit_metadata` emits a channel system message describing the change (`name_changed`-shaped events are not emitted for name/about, but `topic_changed`, `purpose_changed`, `visibility_changed`, `ttl_changed`, `channel_archived` and `channel_unarchived` system messages are, each naming the acting pubkey) as each recognized tag is processed, and after the tag loop finishes calls `emit_group_discovery_events` to republish the channel's kind:39000/39001/39002 discovery events with the now-current state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`emit_group_discovery_events` builds the kind:39000 event's tags directly from the current `ChannelRecord`: a `d` tag (the channel UUID), a `name` tag, an `about` tag when `description` is non-empty, a `private` tag when visibility is `\"private\"` or an explicit `public` tag otherwise, a `hidden` tag plus one `p` tag per member for `dm`-type channels, an unconditional `closed` tag (Buzz channels always require explicit membership), a `t` tag naming the channel type, `topic`/`purpose` tags when set, an `archived` tag when `archived_at` is set, and `ttl`/`ttl_deadline` tags when an ephemeral TTL is set -- then signs and stores this event with the relay's own keypair, channel-scoped, so existing access control governs who can read it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`emit_group_discovery_events` is also called after channel creation, after a DM is opened, and after membership changes (member added/removed), so the same kind:39000 projection is kept current on every event that can change the fields it derives from, not only on an explicit kind:9002 edit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "`buzz-sdk::build_update_channel` builds a kind:9002 event from optional name/about/visibility/ttl arguments, rejects a call where all four are absent, rejects a visibility value other than `\"open\"`/`\"private\"`, canonicalizes and rejects an empty name client-side (the same rule `update_channel` enforces server-side), and represents `ttl: Some(None)` as an explicit empty-string `[\"ttl\", \"\"]` tag distinct from `ttl: None` (no tag at all, meaning unchanged); separate builders `build_set_topic` and `build_set_purpose` each construct their own single-tag kind:9002 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "Unit tests in buzz-sdk's builders module (`update_channel_name_and_about`, `update_channel_strips_all_leading_hashes_from_name`, `update_channel_rejects_hash_only_name`, `update_channel_visibility_and_ttl`, `update_channel_clears_ttl`) exercise `build_update_channel`'s tag construction, name canonicalization/rejection, and the `ttl` set-vs-clear distinction."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "An end-to-end relay test, `test_unarchive_emits_member_added_notification`, sends a real signed kind:9002 event with `h` and `archived` tags over the WebSocket connection and asserts the relay accepts it (`ok.accepted`), then asserts the archive->unarchive cycle fans out a membership-feed notification to the owner -- live verification that a kind:9002 metadata mutation is accepted end to end, not only validated in isolation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "`buzz-cli`'s `channels update` subcommand (`cmd_update_channel`) requires at least one of `--name`/`--description`/`--visibility`/`--ttl`/`--no-ttl`, validates a supplied `--ttl` as a positive integer, builds the kind:9002 event via `buzz_sdk::build_update_channel`, signs it, and submits it through the same relay ingest path as any other event; `channels get` (`cmd_get_channel`) reads current metadata back by querying `{\"kinds\":[39000],\"#d\":[channel_id],\"limit\":1}` and extracting the `name`/`about` tags from the returned event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs"
  - statement: "Root VISION_PROJECTS.md's Status table marks \"Channels, forums, DMs, canvases\" as \"Ships today\", the product-level maturity marker this capability -- channel metadata specifically -- is grounded against, since no channel-specific VISION status line exists separately from the broader channels/forums/DMs/canvases row."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md"
  - statement: "Channel metadata's kind:39000 discovery projection is a read-only, relay-computed mirror of the `channels` table plus its member list, not a second independent store -- an agent or client that only ever reads kind:39000 cannot observe a metadata field the `channels` table does not carry, and conversely a metadata field the table carries but `emit_group_discovery_events` does not map to a tag (there is none such today; every metadata column reachable through `ChannelUpdate`, `set_topic`, `set_purpose`, `archive_channel`/`unarchive_channel` has a corresponding tag) would be invisible to Nostr-only consumers."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-db/src/store/channel.rs"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-postgres
---

# Channel metadata: capability

Buzz lets a channel's owners and admins name it, describe it, set its
visibility (open or invite-only), give it a short-lived topic and a longer
standing purpose, and cap its lifetime with an ephemeral TTL -- and lets any
member or any Nostr-aware client discover the channel's current metadata
without needing a Buzz-specific API. A human or agent with the right role can
change any of these fields at any time after the channel is created, and
every other member (and any external NIP-29 client following the same
relay) sees the update reflected in the channel's discovery event shortly
after.

## Maturity

Shipped. Root `VISION_PROJECTS.md`'s Status table marks "Channels, forums,
DMs, canvases" as "Ships today" (`VISION_PROJECTS.md`), and channel metadata
specifically is backed by a concrete, exercised code path: a `channels`
table with dedicated columns for every metadata field (`migrations/0001_initial_schema.sql`),
create/update functions that validate and persist them
(`crates/buzz-db/src/channel.rs`), a relay command handler that authorizes
and applies edits from a signed Nostr event
(`crates/buzz-relay/src/handlers/side_effects.rs`), an SDK builder and CLI
subcommand that construct that event (`crates/buzz-sdk/src/builders.rs`,
`crates/buzz-cli/src/commands/channels.rs`), unit tests on the builder
(`crates/buzz-sdk/src/builders.rs`), and a passing end-to-end relay test that
sends a real signed edit-metadata event over the wire
(`crates/buzz-test-client/tests/e2e_relay.rs`).

## Boundary

This node does not describe:
- **How the underlying containers are built.** The relay process that hosts
  the edit-metadata handler, and the Postgres instance that stores the
  `channels` table, are the architecture layer's territory -- see
  `architecture-containers-relay` and `architecture-containers-postgres`.
- **The generic event-ingestion pipeline.** Signature verification, the
  community write fence, and the shared validate/store/fan-out path every
  Nostr event (including the kind:9002 edit-metadata event this capability
  is built on) passes through are documented once, generically, by
  `architecture-flows-event-ingestion`, and are not re-described here.
- **The step-by-step flow of one metadata edit.** The order of validation,
  persistence, system-message emission and discovery re-publication
  described under *Behavioral rules* above is stated at the level needed to
  establish the capability exists and behaves as claimed; a dedicated flow
  node narrating one interaction end to end (per the corpus's `flow` node
  type) does not yet exist for this capability.
- **How the running system is operated.** Deployment, monitoring and
  incident response for the relay that hosts this capability are the
  `operations` corpus surface's territory, not this node's.
- **Channel membership, administration, or deletion.** Who can join, be
  removed, or hold which role; and how a channel is archived/deleted as a
  distinct lifecycle action, are sibling capabilities under
  `capabilities/channels/` (channel-membership, channel-administrators,
  channel-deletion, per Feature #612's own task breakdown) and are not
  restated here beyond the two-tier authorization rule that governs which
  roles may change which metadata field.
- **The NIP-29 protocol itself.** This node describes Buzz's specific choice
  to project channel metadata onto NIP-29's addressable kind:39000 (and to
  layer Buzz-specific tags like `ttl`, `ttl_deadline`, `topic` and `purpose`
  onto it), not NIP-29 as a general specification.

## Behavioral rules and variants

- **Fields.** `name` (required, non-empty after canonicalization -- leading
  `#` characters and surrounding whitespace are stripped), `description`
  (`about` on the wire; optional, free text), `visibility` (`"open"` or
  `"private"`, no other value accepted), `topic` (short, free text, no
  emptiness rule enforced at this layer), `purpose` (longer free text, same),
  `ttl_seconds`/`ttl_deadline` (optional; a positive-integer TTL sets both a
  duration and a computed deadline, an empty TTL clears both, making the
  channel permanent again), and `archived_at` (set/cleared via the
  `archived` tag's `"true"`/`"false"` value, exclusively -- reachable through
  the same kind:9002 wire path as the other metadata fields even though this
  node's *Boundary* leaves channel lifecycle to a sibling node).
- **Two-tier authorization.** Changing `name`, `about` (`description`),
  `visibility`, `ttl`, or `archived` requires the actor to hold the `owner`
  or `admin` role on the channel, or to be the NIP-OA owning human of an
  active owner-role agent in the channel. Changing `topic` or `purpose`
  requires only active membership. Both tiers are enforced by the same
  kind:9002 pre-storage validation before any database write happens.
  Mutating an already-archived channel is rejected outright, except an
  `["archived", "false"]` unarchive request, which is deliberately let
  through.
  variant: enforced within one Nostr event kind (9002), by tag, not by a
  separate event kind per field.
- **Validation happens before storage, not just at the database layer.**
  `validate_admin_event`'s kind:9002 branch independently re-checks name
  emptiness, visibility's closed set, and TTL's positive-integer-or-empty
  shape ahead of `update_channel`'s own equivalent checks -- a change that
  would fail one layer is rejected before the other is reached, and both
  layers agree on the rules rather than one being a formality.
- **Every accepted metadata change re-derives the whole kind:39000 event
  from current state**, rather than patching individual tags -- the relay
  reads the channel record fresh and rebuilds the full tag set (`name`,
  `about`, visibility, `closed`, channel-type `t`, `topic`, `purpose`,
  `archived`, `ttl`/`ttl_deadline`, plus DM-only `hidden`/`p` tags) every
  time, so a metadata read is always self-consistent even though the write
  path can touch one field at a time.
  variant: this republication also happens on channel creation, DM open, and
  membership changes -- not only on an explicit metadata edit -- because
  those events change fields (`d`/`p` tags, member-derived `hidden`) the same
  kind:39000 event carries.
- **Live-subscription side effect on visibility.** An open-to-private
  transition additionally invalidates cached accessible-channel/visibility
  state and evicts non-members' live subscriptions to the channel on the
  handling relay node, on top of the metadata write itself -- a
  visibility-specific effect no other metadata field triggers.
- **Discovery is read-only and channel-scoped.** The kind:39000 (and
  39001/39002) events are stored with the channel as their access-control
  scope, so only members of a private channel can read its discovery event
  -- there is no separate, unscoped kind:39000 feed a non-member could poll
  to learn a private channel's metadata.

## Relationships

- references: `architecture-flows-event-ingestion` (the generic
  validate/store/fan-out pipeline the kind:9002 edit-metadata event flows
  through, like every other event)
- references: `architecture-containers-relay` (the process hosting the
  edit-metadata handler and discovery-event emission)
- references: `architecture-containers-postgres` (the datastore backing the
  `channels` table this capability reads and writes)

## Scope and omissions

**This node covers** what channel metadata is (name, description,
visibility, topic, purpose, TTL, archived state), how a client changes it
(a signed kind:9002 event, validated and authorized per field, applied to
the `channels` table), how a client or external NIP-29 consumer discovers
current metadata (the relay-signed, channel-scoped kind:39000 event,
re-derived from current state on every relevant change), and the
two-tier owner/admin-vs-member authorization split that governs which
fields which role may change.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay and Postgres containers that implement this are built | `architecture-containers-relay`, `architecture-containers-postgres` |
| The generic Nostr event-ingestion pipeline every event (including kind:9002) passes through | `architecture-flows-event-ingestion` |
| The step-by-step flow of one metadata edit, narrated as a flow | not yet drafted (no flow node exists for this capability at the time of writing) |
| Channel membership, roles, and administration | sibling capability nodes under `capabilities/channels/` (not yet merged at the time of writing) |
| Channel archival/deletion as its own lifecycle capability | sibling capability nodes under `capabilities/channels/` (not yet merged at the time of writing) |
| How the running relay is deployed, monitored, or operated | the `operations` corpus surface |
| The NIP-29 specification itself, as opposed to Buzz's projection onto it | out of this corpus's scope; see `docs/nips/` and the upstream NIP-29 text |

**Expected but not verified when this node was written:**
- **No sibling `capabilities/channels/*.md` node was read**, because none has
  merged to `origin/launchpad` yet at the recorded revision (confirmed by
  listing that path there before drafting) -- this node's *Boundary* section
  names the expected sibling capabilities (membership, administrators,
  deletion) from Feature #612's own task breakdown rather than from reading
  their drafted content, since they may exist only on other, unmerged
  branches.
- **The desktop and mobile client UI for editing channel metadata was not
  inspected.** This node verifies the relay/SDK/CLI path end to end; whether
  the desktop or mobile app exposes every field this capability supports
  (for example, TTL) through its own UI was not checked, and is a gap in
  this node's coverage of "the capability" as a whole rather than only its
  server-side contract.
- **The INFERENCE claim above (kind:39000 as a complete mirror of the
  `channels` table's metadata columns) was reasoned from reading both sides
  of the mapping once, not from an automated diff between the schema and
  the tag-emission code** -- a future migration adding a metadata column
  without a matching tag in `emit_group_discovery_events` would silently
  invalidate it.
