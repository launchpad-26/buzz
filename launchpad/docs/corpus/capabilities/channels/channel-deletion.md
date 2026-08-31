---
id: capabilities-channels-channel-deletion
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
  - statement: "kind:9008 is the NIP-29 'Delete a group' event, named KIND_NIP29_DELETE_GROUP, and is one of the kinds registered in the crate's kind registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:344-345"
      - "crates/buzz-core/src/kind.rs:667"
  - statement: "buzz-sdk's build_delete_channel constructs a kind:9008 event with empty content and a single h tag naming the channel's UUID; the desktop Tauri backend's own build_delete_channel (events.rs) constructs the identical shape independently."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:738-741"
      - "desktop/src-tauri/src/events.rs:213-217"
  - statement: "buzz-sdk carries a unit test asserting build_delete_channel(cid) produces an event whose kind is 9008 and which carries an h tag equal to the channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:3162-3166"
  - statement: "buzz-cli exposes 'buzz channels delete --channel <uuid>', documented in its own clap help text as 'Delete a channel permanently'; its handler (cmd_delete_channel) builds the event via buzz_sdk::build_delete_channel, signs it, and submits it."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:666-671"
      - "crates/buzz-cli/src/commands/channels.rs:957-967"
      - "crates/buzz-cli/src/lib.rs:1170"
  - statement: "The desktop app exposes channel deletion from the Channel Management sheet's moderation actions: canDeleteChannel is computed as selfRole === 'owner' || canManageOwnedAgentChannel, and confirming the AlertDialog (title 'Delete channel?', body 'Delete {channelName} from the community list. This action cannot be undone.') calls the deleteChannel Tauri command."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/ui/ChannelManagementModerationActions.tsx:87"
      - "desktop/src/features/channels/ui/ChannelManagementModerationActions.tsx:111-146"
      - "desktop/src/shared/api/tauriChannels.ts:205-206"
  - statement: "The desktop Tauri command delete_channel builds a kind:9008 event via the backend's own build_delete_channel, signs and submits it through the same relay-write path as every other channel-admin action; useDeleteChannelMutation optimistically removes the channel from the cached channel list and drops its detail-query cache on success."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/channels.rs:875-878"
      - "desktop/src/features/channels/hooks.ts:708-728"
  - statement: "The relay requires an h tag for kind:9008 (requires_h_channel_scope), gates it under Scope::AdminChannels in the auth-scope mapping, and exempts it from the generic membership/open-visibility gate so that only the kind's own per-kind validator decides authorization -- a deliberate 'OQ1 decision' documented inline to let a channel's owning human act on an owner-role agent's channel without being a member themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:393-395"
      - "crates/buzz-relay/src/handlers/ingest.rs:611-641"
      - "crates/buzz-relay/src/handlers/ingest.rs:2290-2303"
  - statement: "The relay's per-kind admin-event validator authorizes kind:9008 only for a channel member whose role is 'owner', or -- diverging intentionally from kind:9001's own check, per the validator's own comment -- the human who owns any active owner-role agent in the channel, even when that human is not a channel member; every other caller is rejected with 'only owner can delete group'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:721-738"
  - statement: "handle_delete_group (the kind:9008 side-effect handler) soft-deletes the channel via db.soft_delete_channel, treats 'not deleted' (already gone or never existed) as a warning rather than a failure, soft-deletes the channel's NIP-29 discovery events, invalidates the community's membership and accessible-channels caches, and emits a relay-signed system message into the channel with JSON body {\"type\": \"channel_deleted\", \"actor\": <hex pubkey>}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1888-1938"
  - statement: "soft_delete_channel executes 'UPDATE channels SET deleted_at = NOW() WHERE community_id = $1 AND id = $2 AND deleted_at IS NULL' and returns whether a row was updated -- deletion is a soft delete guarded to be idempotent, not a hard delete of the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs:695-709"
  - statement: "Every channel-read query in buzz-db's channel module filters on 'deleted_at IS NULL' (get_channel, list/search variants, membership joins), so once a channel is soft-deleted it stops appearing in any subsequent read through those queries without the row itself being removed."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel.rs:281"
      - "crates/buzz-db/src/store/channel_members.rs:765"
      - "crates/buzz-db/src/store/channel.rs:348"
      - "crates/buzz-db/src/store/channel_members.rs:990"
  - statement: "The channels table's deleted_at TIMESTAMPTZ column is defined in the repository's initial schema migration, confirming the soft-delete column is part of the base schema rather than a later, separately-tracked addition."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:84"
  - statement: "invalidate_channel_deleted evicts every membership-cache and accessible-channels-cache entry scoped to the channel's community (not only the deleted channel's own id), with an inline comment explaining that a stale is_member=true cache entry would otherwise bypass the database's own deleted_at guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:1064-1090"
  - statement: "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs contains a kind:9008 DELETE_GROUP section with four #[ignore]'d live-relay integration tests read directly: test_owner_can_delete_agent_channel and test_owner_can_delete_private_agent_channel (an owning human who is not a channel member can delete an owner-role agent's channel, accepted), test_third_party_cannot_delete_agent_channel (an unrelated third party's kind:9008 is rejected), and test_agent_can_self_delete_channel (the owning agent itself can still delete its own channel)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:519-556"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:557-588"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:760-788"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:790-816"
  - statement: "These four tests are marked #[tokio::test] and #[ignore], meaning they require a running relay (plus Postgres/Redis) and are not executed by a plain `cargo test` -- they are part of the e2e/live-integration suite `just test` and TESTING.md describe, not of the default unit-test run."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:521-525"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:790-793"
  - statement: "The relay's ingest-handler unit test nip29_admin_kinds_require_h_tags asserts requires_h_channel_scope(KIND_NIP29_DELETE_GROUP) is true, and this test runs under a plain `cargo test` (no #[ignore]), unlike the live-relay tests above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3398-3413"
  - statement: "kind:9002 (KIND_NIP29_EDIT_METADATA) with an 'archived' tag is the relay's separate channel-archival path (Scope::AdminChannels when the archived tag is present, Scope::ChannelsWrite otherwise), distinct from kind:9008 deletion -- archiving sets/clears archived_at rather than deleted_at, and buzz-cli exposes it as separate 'archive'/'unarchive' subcommands rather than folding it into 'delete'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:414-419"
      - "crates/buzz-cli/src/lib.rs:655-665"
      - "crates/buzz-db/src/store/channel.rs:609-689"
  - statement: "At the data level, deletion is reversible in principle (deleted_at is a nullable timestamp column set, not a row removal, and no code path clears it back to NULL was found), but the desktop UI's own confirmation dialog tells the end user the action 'cannot be undone', and no CLI or desktop affordance to reverse a kind:9008 deletion exists in the surfaces inspected for this node -- so the capability is undo-able at the storage layer only in a sense no exposed interface currently acts on."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/channel.rs:695-709"
      - "desktop/src/features/channels/ui/ChannelManagementModerationActions.tsx:111-117"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-containers-relay
---

# Channel deletion: capability

Channel deletion is the product capability that lets a channel's owner -- or the
human who owns an agent holding the owner role in that channel -- permanently
remove a channel from the community's channel list. Once a deletion request is
accepted, the channel and its NIP-29 discovery metadata stop appearing anywhere a
member, agent, or client subsequently reads the community's channels, and the
channel's remaining members receive a system message recording that it happened.
The primary actor is a human or agent with the owner role (or the human who owns
an owner-role agent, even while not a member themselves); the outcome is a channel
that no longer exists from every caller's point of view, whether they reach it
through `buzz-cli`, the desktop app, or a raw relay query.

## Maturity

**Shipped.** The event kind, both client builders, both client-facing commands
(CLI and desktop), the relay's authorization and side-effect handling, and four
live-relay integration tests exercising the authorization boundary are all present
in this checkout: `crates/buzz-core/src/kind.rs:345` (kind registration),
`crates/buzz-sdk/src/builders.rs:738-741` and
`desktop/src-tauri/src/events.rs:213-217` (event construction, two independent
client paths converging on the same event shape),
`crates/buzz-cli/src/commands/channels.rs:957-967` and
`desktop/src/features/channels/ui/ChannelManagementModerationActions.tsx:87-146`
(user-facing entry points), `crates/buzz-relay/src/handlers/side_effects.rs:721-738`
and `:1888-1938` (authorization and side effects), and
`crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:519-816` (behavioral
coverage of the owner/agent/third-party authorization matrix).

## Behavioral rules, constraints and variants

- **Who may delete.** Only a channel member whose role is `owner`, or the human
  who owns any active owner-role agent in the channel -- checked even when that
  human is not themselves a member. This diverges intentionally from the
  equivalent check on kind:9001, per the relay's own inline comment, precisely so
  a human can delete a channel their agent owns without first joining it.
  Everyone else's kind:9008 is rejected with `"only owner can delete group"`.
- **Scope and shape.** Submitting kind:9008 requires `Scope::AdminChannels`. The
  event must carry an `h` tag naming the channel (`requires_h_channel_scope`
  includes kind:9008), and content is conventionally empty in both client
  builders.
- **Membership-gate bypass.** kind:9008 is one of the kinds explicitly exempted
  from the relay's generic member-or-open-channel gate; its own per-kind
  validator is the sole authority. This is what makes the owner-of-agent path
  above reachable on a private channel the human never joined.
- **Idempotent soft delete, not a hard delete.** The channel row is not removed;
  `deleted_at` is set once, guarded by `WHERE deleted_at IS NULL`, so a second
  kind:9008 against an already-deleted channel updates nothing and the handler
  logs a warning rather than failing the request. Every channel-read query in
  `buzz-db` filters on `deleted_at IS NULL`, which is the actual mechanism by
  which a deleted channel disappears from lists, lookups, and membership joins.
- **Side effects beyond the row.** The channel's own NIP-29 discovery events are
  also soft-deleted; the community's membership and accessible-channels caches
  are invalidated (community-wide, not just for the one channel, specifically so
  a stale cached membership entry cannot bypass the database's own guard); and a
  relay-signed system message (`{"type": "channel_deleted", "actor": <hex>}`) is
  posted into the channel recording who deleted it.
- **Distinct from archiving.** kind:9002 with an `archived` tag is a separate,
  already-existing capability (`archived_at`, not `deleted_at`; its own
  `archive`/`unarchive` CLI subcommands) and is not this node's subject.
- **Two independent client implementations, one event shape.** `buzz-cli` (via
  `buzz-sdk`) and the desktop app (via its own Tauri-side event builder) each
  construct the identical kind:9008/empty-content/single-`h`-tag event
  independently, rather than one calling into the other.
- **User-facing framing versus storage-level reversibility.** The desktop
  confirmation dialog tells the user deletion "cannot be undone." At the storage
  layer this node found `deleted_at` to be a nullable column that is only ever
  set, never cleared, by the code paths inspected -- so the two statements do not
  contradict each other, but no exposed interface (CLI or desktop) offers a way
  to reverse the deletion once accepted.

## Boundary

This node does not describe:
- **How the relay is built.** The Rust/Axum server that hosts kind:9008's
  authorization and side-effect handling is `architecture-containers-relay`
  (referenced below); this node cites specific files and line ranges inside it
  as evidence, but the container's own technology, ownership boundary, and
  deployment shape are that node's subject, not this one's.
- **The interface(s) channel deletion is exposed through.** `buzz channels
  delete` and the desktop Channel Management sheet are named here as entry
  points, but no interface-type corpus node yet exists for `buzz-cli`'s command
  surface or for the relay's NIP-29 admin-event surface to `reference` instead.
- **The step-by-step ingestion pipeline a kind:9008 event travels through.** No
  flow-type corpus node for channel deletion (or for NIP-29 admin-event
  ingestion generally) exists yet to `reference` in its place; this node
  narrates the rules the pipeline enforces, not the pipeline's own stage-by-stage
  path.
- **How the running system is operated** (backups, retention of soft-deleted
  rows, or any operational cleanup of `deleted_at` rows) -- not inspected for
  this node and not this capability's subject.

## Relationships

- `references`: `architecture-containers-relay` -- the relay is the container
  that owns kind:9008's authorization and side-effect handling cited throughout
  this node; the edge points at the container that realizes the capability
  without folding its own architecture into this document.

No `implements`, `part-of`, or `supersedes` edges were found to apply: no
interface- or flow-type node for this capability's surfaces exists yet on
`origin/launchpad` at the recorded revision to target instead.

## Scope and omissions

**This node covers** what channel deletion does, who may trigger it, the
authorization rule and its intentional divergence from the edit-metadata check,
the soft-delete/cache-invalidation/system-message side effects, how it differs
from archiving, the two independent client implementations, and the tests that
exercise the authorization boundary.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay itself is built (technology, deployment, ownership boundary) | `architecture-containers-relay` |
| The CLI's or the relay's NIP-29 admin surface as an interface contract | No interface-type node exists yet for either surface |
| The step-by-step ingestion pipeline a kind:9008 event travels through | No flow-type node exists yet for channel deletion or NIP-29 admin-event ingestion |
| Operational handling of soft-deleted rows (retention, backup, cleanup) | Not inspected for this node |

**Expected but not verified when this node was written:**
- **The four live-relay integration tests in `e2e_human_edit_agent_content.rs`
  were read, not executed.** They are `#[ignore]`d and require a running relay
  plus Postgres and Redis; this node cites their assertions as written in source,
  not as observed passing in a live run during authoring.
- **No code path clearing `deleted_at` back to `NULL` was found**, but the search
  was limited to `buzz-db`'s channel module and the relay handlers this node
  otherwise cites -- an undelete path elsewhere in the workspace was not
  exhaustively ruled out.
- **Whether any generated index, search surface, or workflow trigger observes a
  soft-deleted channel differently from the read paths cited here** was not
  checked -- this node verified the `buzz-db` channel-query layer only.
