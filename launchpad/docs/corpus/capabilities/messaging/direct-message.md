---
id: capabilities-messaging-direct-message
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
  - statement: "buzz-core defines exactly two event kinds that carry message content -- KIND_STREAM_MESSAGE (kind 9) and KIND_STREAM_MESSAGE_V2 (kind 40002) -- and neither constant, nor any other kind constant in the module, is scoped to a particular channel_type; a message inside a `dm`-typed channel and a message inside a `stream`-typed channel are the identical event kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:479"
      - "crates/buzz-core/src/kind.rs:481"
  - statement: "buzz-sdk's build_message (the builder both the CLI's `messages send` and the desktop/mobile send paths ultimately construct their event from) takes only a channel_id, content, optional NIP-10 thread_ref, mentions, a broadcast flag and media tags -- it has no channel_type parameter or branch, caps content at 64 KiB via check_content, and tags the event with only an `h` channel-scope tag (plus optional thread/mention/broadcast/imeta tags) before signing it as kind 9."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:216-245"
  - statement: "buzz-relay's ingest pipeline requires the identical MessagesWrite authorization scope for KIND_STREAM_MESSAGE and KIND_STREAM_MESSAGE_V2 as it does for every other channel-scoped content kind (forum posts, canvases, stream edits), and required_scope_for_kind has no channel_type-conditional branch anywhere in its match arms -- the scope check that gates a message write cannot distinguish a DM from a stream channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:370-389"
  - statement: "requires_h_channel_scope, the function the ingest pipeline calls to decide whether an event must carry an `h` channel-scope tag and get NIP-10 thread resolution, returns true for KIND_STREAM_MESSAGE and KIND_STREAM_MESSAGE_V2 through the same match arm as every other channel-scoped content kind, with no channel_type distinction; its own unit test asserts this for KIND_STREAM_MESSAGE directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:612-641"
      - "crates/buzz-relay/src/handlers/ingest.rs:3382-3396"
  - statement: "buzz-db's insert_event_with_thread_metadata and thread.rs's insert_thread_metadata / increment_reply_count -- the functions that materialize a message's reply_count and descendant_count -- take a channel_id and thread metadata but never a channel_type, and operate inside one transaction with the event insert regardless of what kind of channel that channel_id belongs to; a DM message's thread counters are produced by the identical code path a stream message's are."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs:1308-1321"
      - "crates/buzz-db/src/thread.rs:116-141"
      - "crates/buzz-db/src/thread.rs:251-287"
  - statement: "A case-insensitive, recursive grep of crates/buzz-db/src/dm.rs and crates/buzz-relay/src/handlers/command_executor.rs (the DM channel's own persistence and command-dispatch modules) for KIND_GIFT_WRAP found zero matches at this recorded revision, while KIND_GIFT_WRAP (kind 1059, NIP-17's encrypted-DM envelope) is defined and used elsewhere in the relay -- the message capability documented here is the plaintext, channel-scoped conversation model, not NIP-17 gift-wrapped ciphertext."
    entry_class: FACT
    evidence:
      - "grep_recursive('KIND_GIFT_WRAP', path='crates/buzz-db/src/dm.rs;crates/buzz-relay/src/handlers/command_executor.rs') -> zero matches, run against this node's recorded revision"
      - "crates/buzz-core/src/kind.rs:60"
  - statement: "buzz-cli's `dms` command module (crates/buzz-cli/src/commands/dms.rs) exposes exactly four operations -- cmd_list_dms, cmd_open_dm, cmd_hide_dm, cmd_add_dm_member -- and none of them sends a message; buzz-cli's own live-testing runbook sends a message into a channel with the ordinary `buzz messages send --channel <channel-id> --content ...` command, the same command used against a stream channel's UUID, naming no DM-specific variant."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/dms.rs:8"
      - "crates/buzz-cli/src/commands/dms.rs:51"
      - "crates/buzz-cli/src/commands/dms.rs:96"
      - "crates/buzz-cli/src/commands/dms.rs:112"
      - "crates/buzz-cli/TESTING.md:192-213"
  - statement: "The mobile Flutter client's messageMentionPubkeys helper -- called from the single, channel-type-agnostic SendMessage.call() used for every outgoing message -- states in its own doc comment that 'in a DM, every current recipient is also addressed with a p tag without inserting visible @mentions into the composer; non-DM channels remain explicit-only,' and its implementation branches specifically on `channel.isDm` to append every DM participant pubkey to the mention/p-tag set only when the target channel is a DM."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/message_mention_pubkeys.dart:1-25"
      - "mobile/lib/features/channels/send_message_provider.dart:39-68"
  - statement: "The desktop client's own messageMentionPubkeys helper carries the identical rule in its doc comment -- 'Stream messages notify only explicit mentions. A DM addresses every other participant, so it must carry recipient p tags even when the composer text contains no @mention' -- and its implementation branches on `channel.channelType === \"dm\"` to include every channel.memberPubkeys / channel.participantPubkeys entry as an implicit recipient, corroborating the mobile client's identical behavior independently in a separate codebase."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/messageMentionPubkeys.ts:1-30"
  - statement: "buzz-sdk's builders test module exercises build_message directly with message_happy_path, message_content_too_large, message_max_content_ok, message_direct_reply, message_nested_reply, message_broadcast_flag, message_mentions_deduped and message_too_many_mentions -- unit tests in the same crate as the builder, covering the exact construction path a DM message goes through, but written against the builder generically and asserting nothing DM-specific."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2381-2571"
  - statement: "A recursive grep of crates/buzz-test-client/tests/ for open_dm, dm_open, ChannelType::Dm or channel_type.*dm found zero matches at this recorded revision, so no integration or end-to-end test was found that sends a message inside a channel actually created as a DM; the message-send code path's generality across channel types is established here by reading the source (the citations above), not by an executable test that exercises a DM specifically."
    entry_class: FACT
    evidence:
      - "grep_recursive('open_dm|dm_open|ChannelType::Dm|channel_type.*dm', path='crates/buzz-test-client/tests/') -> zero matches, run against this node's recorded revision"
  - statement: "Root VISION_PROJECTS.md's own 'Capability | Status' table marks the row 'Channels, forums, DMs, canvases' as 'Ships today', the same maturity marker this node's code-level evidence (a working, tested build_message path reachable from a DM channel via buzz-cli, desktop and mobile) independently corroborates for the message-send capability specifically, not only for DM channel creation."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "A case-insensitive, recursive grep of web/ for dm_channel, DmChannel, 'direct message' or 'open dm' found zero matches at this recorded revision, so at this revision the message-send capability documented here has no reachable path through the browser-based web client, only through the relay protocol, buzz-cli, the desktop app and the mobile app."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('dm_channel|DmChannel|direct message|open dm', path='web/') -> zero matches, run against this node's recorded revision"
  - statement: "As of this recorded revision, no `capabilities/`-typed corpus node exists on origin/launchpad (the corpus tree contains only architecture/, standards/, schema/ and templates/), so the DM-channel capability node (creation, membership, participant identity) that this node's Boundary section refers to is not yet a valid relationship target -- it exists only in the still-open, unmerged PR #1914 (launchpad-26/buzz), not on origin/launchpad."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus (run directly against this node's recorded revision) and gh pr view 1914 --repo launchpad-26/buzz (state: OPEN, mergedAt: null, read directly)"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-cli
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-mobile
---

# Direct message: capability

Inside a private conversation between community members -- a DM -- a member or agent
can send a text message, reply into a thread, and have that message delivered,
persisted and counted exactly the way a message in any other Buzz channel is: the
same event kinds, the same content limit, the same authorization scope, and the same
thread-counter mechanism. The one behavior specific to a DM is that every current
participant is implicitly addressed as a recipient the moment a message is sent, even
if the sender's text contains no `@mention` -- so notification and agent-observer
plumbing that keys off recipient tags reaches every participant in a DM by default,
which is not true in an ordinary stream or forum channel. This capability ships today,
per root `VISION_PROJECTS.md`'s own Capability/Status table ("Channels, forums, DMs,
canvases -- Ships today"), and the code-level evidence above establishes that maturity
claim specifically for the message-send path, not only for opening a DM.

## Maturity

**Shipped.** `VISION_PROJECTS.md`'s Status table marks "Channels, forums, DMs,
canvases" as shipping today. At the code level: `buzz-core` defines the two message
kinds (9, 40002) used uniformly across channel types; `buzz-sdk`'s `build_message` is
exercised by eight unit tests covering its happy path, size cap, threading and
mention behavior; `buzz-relay`'s ingest pipeline enforces the same scope and
channel-scoping rules for those kinds regardless of `channel_type`; and both the
desktop and mobile clients ship a DM-specific mention rule on top of the same
generic send path, confirming the capability is reachable and behaviorally
differentiated (not merely theoretically available) on both first-party clients.

## Behavioral rules and constraints

- **No DM-specific message event kind exists.** A message sent into a `dm`-typed
  channel is `KIND_STREAM_MESSAGE` (9) or `KIND_STREAM_MESSAGE_V2` (40002) -- the
  identical kinds used in a `stream`-typed channel. `buzz-core`'s kind registry
  carries no third, DM-only message kind.
- **Content is capped at 64 KiB**, enforced by `buzz-sdk`'s `build_message` via
  `check_content`, with no separate or larger limit for DM content.
- **Authorization and channel-scoping do not distinguish DM from stream.**
  `buzz-relay`'s `required_scope_for_kind` requires the same `MessagesWrite` scope,
  and `requires_h_channel_scope` requires the same `h` channel-scope tag, for both
  message kinds regardless of `channel_type`.
- **Plaintext, not gift-wrapped.** `KIND_GIFT_WRAP` (1059, NIP-17's encrypted-DM
  envelope) is never referenced by the DM channel's own persistence
  (`buzz-db::dm`) or command-dispatch (`command_executor`'s DM handlers) code --
  confirmed independently by grep for this node, not inherited from another
  document. A DM message is a plaintext, channel-scoped event like any other.
- **Threading and reply counters are the generic mechanism.** `buzz-db`'s
  `insert_event_with_thread_metadata`, `insert_thread_metadata` and
  `increment_reply_count` operate on a `channel_id` and thread metadata with no
  `channel_type` branch, so a DM message's `reply_count`/`descendant_count` are
  produced by the same transaction-guarded path a stream message's are.
- **No DM-specific send command exists in `buzz-cli`.** The `buzz dms` subcommand
  group covers only `list`, `open`, `add-member` and `hide`; sending a message into
  a DM uses the ordinary `buzz messages send --channel <dm-channel-id> --content
  ...` command, identical to sending into a stream channel.
- **DM messages implicitly address every participant, uniquely to DMs.** Both the
  desktop (`messageMentionPubkeys.ts`) and mobile (`message_mention_pubkeys.dart`)
  clients carry a rule, stated near-identically in each codebase's own doc
  comments, that a DM message adds every current participant as a recipient `p`
  tag even when the sender wrote no `@mention` -- while a stream or forum message
  notifies only explicitly-mentioned pubkeys. This is the one message-send
  behavior this node found that is conditioned on `channel_type == dm`
  specifically, corroborated independently in two separate client codebases.

## Verification

- `crates/buzz-sdk/src/builders.rs`'s own test module exercises `build_message`
  directly: `message_happy_path`, `message_content_too_large`,
  `message_max_content_ok`, `message_direct_reply`, `message_nested_reply`,
  `message_broadcast_flag`, `message_mentions_deduped` and
  `message_too_many_mentions` are unit tests in the same crate as the builder a DM
  message is constructed with -- but they are channel-agnostic, asserting nothing
  DM-specific.
- `crates/buzz-relay/src/handlers/ingest.rs`'s
  `channel_scoped_content_kinds_require_h_tags` test asserts `KIND_STREAM_MESSAGE`
  requires the same `h`-tag channel scoping as forum posts and canvases.
- **Gap, stated rather than silenced:** no integration or end-to-end test sending a
  message into a channel actually created as a DM was found under
  `crates/buzz-test-client/tests/` at this recorded revision. This node's claim
  that message-send behaves identically inside a DM rests on reading the
  channel-type-agnostic source paths cited above, not on an executable test that
  exercises a DM specifically.

## Boundary

This node does not describe:

- **DM channel creation, membership or identity.** Opening a DM, adding a
  participant, hiding a conversation, and the participant-hash-based identity
  scheme that makes opening the same DM idempotent are a separate capability --
  drafted as `capabilities-channels-dm-channel` in the still-open, unmerged PR
  #1914 (launchpad-26/buzz), not yet present on `origin/launchpad` at this
  recorded revision. No `relationships` entry targets it here because it does not
  yet resolve; a future edit should add one once it merges (see *Scope and
  omissions*).
- **How the capability is built.** The relay's ingest/authorization pipeline, the
  CLI's command structure, the desktop and mobile send paths, and Postgres's
  event/thread-metadata schema are the architecture family's territory -- see
  `relationships` below for the merged nodes that own that content.
- **The interface contract this capability is exposed through.** The exact
  `buzz messages send` flag surface and the relay's kind 9/40002 wire protocol are
  an interface-level contract; no `interfaces-events`-typed corpus node exists yet
  on `origin/launchpad` for this node to reference.
- **The step-by-step flow of sending one message.** The exact sequence from a
  client composing a message through to it appearing in every participant's
  timeline is a flow-level document; no message-send flow node exists yet under
  `launchpad/docs/corpus/architecture/flows/` at this recorded revision.
- **How the running system is operated.** Deployment, monitoring or incident
  response for the relay/Postgres processes that carry this capability is the
  `operations` corpus surface's territory, not this node's.
- **Gift-wrapped (NIP-17) private messaging.** `KIND_GIFT_WRAP` is a separate,
  end-to-end-encrypted delivery mechanism this node found no reference to inside
  the DM channel's own code paths; it is not part of the capability described here.
- **The web client.** A search of `web/` found no DM-related code at this recorded
  revision; this capability is reachable through the relay protocol, `buzz-cli`,
  the desktop app and the mobile app, but not the browser-based web client.

## Relationships

- `references: architecture-containers-relay` -- owns the ingest pipeline
  (`required_scope_for_kind`, `requires_h_channel_scope`) that authorizes and
  validates every message this capability sends, DM or otherwise.
- `references: architecture-containers-postgres` -- owns the event and
  thread-metadata schema (`buzz-db`'s `event.rs`/`thread.rs`) this capability's
  persistence and reply-counting are built on.
- `references: architecture-containers-cli` -- owns `buzz messages send`, the
  agent-facing entry point a DM message is sent through, identical to a stream
  message.
- `references: architecture-containers-desktop` -- owns the desktop send path and
  its DM-specific implicit-recipient rule (`messageMentionPubkeys.ts`).
- `references: architecture-containers-mobile` -- owns the mobile send path and
  its independently-implemented, behaviorally-identical DM implicit-recipient rule
  (`message_mention_pubkeys.dart`).

**Not declared:** `references` or `part-of` toward the DM-channel capability node
(participant/identity/membership) that this capability's Boundary section names,
because that node does not exist on `origin/launchpad` at this recorded revision --
only in the unmerged PR #1914. Per `AGENTS.md`'s own rule, a relationship target
must resolve on the branch being merged into, not the author's own worktree or
another open PR's branch. No `interfaces-events` or flow node exists yet either, for
the same reason.

## Scope and omissions

**This node covers** the message-send/receive capability as it behaves specifically
inside a direct-message conversation: which event kinds and content limits apply,
that authorization and channel-scoping do not distinguish a DM from any other
channel, that DM messages are plaintext rather than NIP-17 gift-wrapped, that no
DM-specific send command exists in `buzz-cli`, that threading and reply counters use
the generic mechanism, and the one message-send behavior this node found that is
genuinely DM-specific -- implicit recipient addressing of every participant,
corroborated independently in both the desktop and mobile clients.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| DM channel creation, membership, participant identity and hiding | a future `capabilities-channels-dm-channel` node (drafted, unmerged as PR #1914 at this recorded revision) |
| How the relay, CLI, desktop, mobile and Postgres containers are built | `architecture-containers-relay`/`-cli`/`-desktop`/`-mobile`/`-postgres` |
| The `buzz messages send` CLI contract and the relay's kind 9/40002 wire protocol as an interface | a future `interfaces-events` node (none merged yet) |
| The step-by-step flow of sending one message | a future flow node (none merged yet) |
| How the running system is operated | the `operations` corpus surface |
| Gift-wrapped (NIP-17) private messaging (`KIND_GIFT_WRAP`) | a separate capability node, not this one |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **No integration or end-to-end test exercising message-send inside an actual
  DM-typed channel was found**, only unit tests of the channel-agnostic builder and
  ingest logic (see *Verification*). This node's core claim -- that message-send
  behaves identically inside a DM -- is a source-reading conclusion, not an
  executable proof against a real DM channel.
- **Reaction behavior (`KIND_REACTION`, kind 7) inside a DM was not investigated in
  depth.** This node's evidence establishes only the message-send/thread path; a
  reader relying on reactions, edits, pins, bookmarks or scheduled-message
  behavior specifically inside a DM should treat that as unverified by this node.
- **Whether desktop's and mobile's implicit-recipient rule actually changes
  delivered notifications end-to-end (push, in-app, or agent-observer routing) was
  not exercised at runtime** -- this node cites the rule's construction of
  recipient tags from source and doc comments, not a runtime observation of a
  notification actually arriving.
- **Whether any Block-internal (`squareup/*`) deployment path changes this
  capability's behavior** was not checked; per this fork's own `AGENTS.md`, that
  infrastructure is outside this repository's visible source.
