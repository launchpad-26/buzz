---
id: capabilities-channels-channel-types
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
  - statement: "buzz-core's ChannelType enum has exactly four variants -- Stream ('linear message stream (the default)'), Forum ('threaded forum-style discussion'), Dm ('direct message conversation'), and Workflow ('internal workflow execution channel') -- with canonical lowercase string forms via as_str/Display/FromStr that round-trip ('stream', 'forum', 'dm', 'workflow')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:57-100"
  - statement: "Postgres persists the same four-value closed set as a native enum type, `CREATE TYPE channel_type AS ENUM ('stream', 'forum', 'dm', 'workflow')`, and the channels table's channel_type column is NOT NULL DEFAULT 'stream', indexed by (community_id, channel_type)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:28"
      - "migrations/0001_initial_schema.sql:76"
      - "migrations/0001_initial_schema.sql:106"
  - statement: "ARCHITECTURE.md's own buzz-db section independently states 'Channel types: Stream, Forum, Dm, Workflow', corroborating buzz-core's enum rather than diverging from it."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:413"
  - statement: "Root VISION_PROJECTS.md's Status table marks 'Channels, forums, DMs, canvases' as '✅ Ships today', which is this capability's maturity evidence -- a product-level status marker, not the corpus node's own draft front-matter status."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:249"
  - statement: "NOSTR.md documents kind:9007 group creation (NIP-29) as accepting a `name` tag plus optional `visibility` and `channel_type` tags; buzz-core defines KIND_NIP29_CREATE_GROUP as 9007."
    entry_class: FACT
    evidence:
      - "NOSTR.md:53"
      - "crates/buzz-core/src/kind.rs:343"
  - statement: "Both of the relay's kind:9007 create-group code paths (the pre-storage validation in ingest.rs and the side-effect handler in handlers/side_effects.rs and command_executor.rs's handle_create_group) read an event's `channel_type` tag content, default to \"stream\" when the tag is absent, and parse it into buzz_db::channel::ChannelType via FromStr, rejecting an unparseable value with 'invalid channel_type: {value}'; neither site restricts the accepted value to a subset of the four enum strings."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2595-2649"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1765-1810"
  - statement: "buzz-cli's own ChannelType clap enum, used by its channel-creation subcommand, exposes only `stream` and `forum` as user-selectable creation values -- `dm` and `workflow` are not offered as creatable channel types through that CLI surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:101-116"
  - statement: "DM channels are created and joined through a dedicated command path, not the generic kind:9007 create-group flow: kind:41010 (KIND_DM_OPEN) is routed to handle_dm_open, which calls buzz-db's open_dm; buzz-db/src/dm.rs's own module doc states 'DMs are channels with channel_type=\"dm\" and visibility=\"private\". Participant sets are immutable -- adding a member creates a NEW DM,' and participant identity is computed by compute_participant_hash, a SHA-256 digest over the sorted, deduplicated set of participant pubkeys."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:507"
      - "crates/buzz-relay/src/handlers/command_executor.rs:66"
      - "crates/buzz-relay/src/handlers/command_executor.rs:370-427"
      - "crates/buzz-db/src/dm.rs:1-4"
      - "crates/buzz-db/src/dm.rs:40-56"
  - statement: "command_executor.rs's DM-scoped command handlers (handle_dm_open's sibling participant-expansion handler and the hide/unhide handlers) each explicitly load the target channel and reject the command with an error unless the loaded channel's channel_type equals \"dm\", so a DM-specific command run against a non-DM channel id fails rather than silently operating on the wrong channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:535-541"
      - "crates/buzz-relay/src/handlers/command_executor.rs:665-671"
  - statement: "A literal-text search of every .rs file in this repository for the constructor expression `ChannelType::Workflow` finds it only inside `#[cfg(test)]`-gated modules (for example buzz-db/src/channel.rs's own `mod tests`, confirmed at line 1533) and nowhere in a non-test relay, workflow-engine, or CLI code path that was inspected for this node."
    entry_class: FACT
    evidence:
      - "grep_literal('ChannelType::Workflow', scope='**/*.rs') -> matches confined to #[cfg(test)] modules, e.g. crates/buzz-db/src/channel.rs:1533,1749"
  - statement: "Because the ingest.rs and side_effects.rs create-group parsers accept any of the four FromStr-recognized channel_type strings uniformly (see the evidence entry above), a client-authored kind:9007 event could in principle set channel_type to \"dm\" or \"workflow\" through the generic create-group path -- no restriction confining that tag's accepted values to a subset was found at either call site during this review; whether some other layer (event validation earlier in the pipeline, or a check this review did not reach) narrows this is not established one way or the other."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2595-2649"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1765-1810"
    confidence: 0.55
  - statement: "Sibling corpus tasks #728 (dm-channel.md), #729 (forum-channel.md), #730 (stream-channel.md), and #731 (workflow-channel.md) each name one of these four channel types as their own single-document scope, run in the same batch as this task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#728, #729, #730, #731 issue titles (read via gh issue view; per this task's own dispatch instructions, none of the four sibling documents' ids are confirmed to exist in origin/launchpad yet, so this node declares no relationships toward them)"
---

# Channel types: capability

Buzz organizes every conversation -- a project workspace, a threaded discussion board,
a private one-to-one or group message, and an agent workflow's own output stream --
as one thing: a **channel**, distinguished by a `channel_type`. A user or agent never
has to reason about a separate DM subsystem or a separate forum subsystem; membership,
roles, message posting, search, and moderation are all built once, against the channel
abstraction, and `channel_type` is what makes a stream read linearly, a forum thread,
or a DM stay locked to its original participant set.

## Channel types

Four types exist, as a closed set on both sides of the wire: the Rust `ChannelType`
enum and the Postgres `channel_type` enum agree on the same four lowercase strings.

| Type | What it is | How it is created |
|---|---|---|
| `stream` | Linear message stream -- the default type, and the shape most channels (project workspaces, team rooms) take. | User-creatable via the generic kind:9007 create-group event or `buzz-cli`'s channel-creation command; the default when no `channel_type` tag is sent. |
| `forum` | Threaded, forum-style discussion (thread roots, votes, comment replies). | User-creatable the same way as `stream`, by setting `channel_type=forum`; `buzz-cli` offers it as a second explicit creation option. |
| `dm` | Direct message conversation, one-to-one or group, with an immutable participant set identified by a SHA-256 hash of the sorted participant pubkeys. | Not offered as a `buzz-cli` creation option. Created and reopened through a dedicated command, kind:41010 (`KIND_DM_OPEN`), which resolves to buzz-db's `open_dm` -- adding a participant to an existing DM opens a *new* DM channel rather than mutating the old one's membership. |
| `workflow` | Internal workflow execution channel. | Declared in both enums and named in `ARCHITECTURE.md`'s own channel-types list, but no non-test code path inspected for this node actually constructs `ChannelType::Workflow` for a real channel -- see the evidence ledger and *Scope and omissions* below. |

**A capability-level behavioral rule that cuts across all four types:** the relay's
own create-group code (both the pre-storage validator and the side-effect handler)
treats `channel_type` as one flat, FromStr-parsed string with no per-type creation
guard beyond "is this one of the four known strings" -- it is `buzz-cli`'s own
narrower `ChannelType` enum, not the relay, that limits *interactive* channel
creation to `stream`/`forum`. DM channels have their own dedicated command path
(`KIND_DM_OPEN`) with participant-hash identity and immutable membership, enforced
separately from generic channel creation: DM-scoped commands additionally check that
the target channel's `channel_type` is actually `dm` before proceeding, rejecting the
command otherwise.

## Maturity

**Shipped.** Root `VISION_PROJECTS.md`'s own Status table marks "Channels, forums,
DMs, canvases" as "✅ Ships today", and the four-way `ChannelType` split, its
Postgres-enum backing, and the create-group/DM-open code paths described above are
all live in `crates/buzz-core`, `crates/buzz-db`, and `crates/buzz-relay` at the
recorded revision -- this is a capability-level maturity claim about the *product*,
independent of this document's own `status: draft` front matter.

## Boundary

This node does not describe:

- **How each individual channel type behaves in depth** -- message shape, roles,
  moderation, and type-specific UI. That is each sibling instance document's own
  scope: `dm-channel.md`, `forum-channel.md`, `stream-channel.md`, and
  `workflow-channel.md` (issues #728-#731 in this same batch) each own one type's
  full depth, and this node deliberately stays at the taxonomy level -- naming the
  four types, how each is created, and the one cross-cutting rule above -- rather
  than re-explaining any one type's full behavior. None of those four documents'
  node ids are confirmed to exist in `origin/launchpad` at this revision, so this
  node declares no `relationships` toward them (see the evidence ledger); a later
  pass should add `references` edges once they merge.
- **How channels are built** -- `AppState`, the relay's connection/routing internals,
  or the Postgres schema beyond the one enum and column cited above. That is the
  architecture family's territory (container/component/context nodes); the closest
  merged neighbor today is `architecture-containers-relay`, which documents the
  relay container as a whole and does not itself break out channel types.
- **The interface(s) a channel type is exposed through** -- `buzz-cli`'s subcommands,
  the WebSocket NIP-29 wire protocol, or the REST bridge. This node cites specific
  call sites as evidence of how creation is gated, not as a full interface
  catalogue.
- **The step-by-step flow of creating or using a channel** -- for example the full
  kind:9007 ingestion pipeline or the DM-open command's transaction/commit sequence.
  That is flow-node territory; this node states that the two paths exist and where,
  not their full sequencing.
- **How the running system operates channels** -- monitoring, incident response, or
  operational runbooks are out of scope here.

## Relationships

Declared: none. `origin/launchpad`'s corpus tree at the recorded revision has no
merged capability-shaped node this document could `implements`, `references`, or
sit `part-of` for channel-type subject matter specifically, and this task's own
dispatch instructions direct omitting edges to the four sibling channel-type
documents (`dm-channel.md`, `forum-channel.md`, `stream-channel.md`,
`workflow-channel.md`) because their ids are not confirmed to exist on the merge
target yet. The capability template itself (`corpus-template-capability`) is merged
at this revision, but this node does not declare `implements` toward it -- its own
shape (Channel types / Maturity / Boundary / Relationships / Scope and omissions)
already follows that template directly, and the template states that edge is
optional. The first future pass that lands the sibling channel-type documents, or an
architecture node describing the channels subsystem's own container/component shape,
is the natural moment to add `references` edges from here.

## Scope and omissions

**This node covers** the four-value `channel_type` taxonomy shared by
`crates/buzz-core`, `crates/buzz-db`'s Postgres schema, and `ARCHITECTURE.md`; how
each type is created (or, for `workflow`, the absence of an observed non-test
creation path); the one cross-cutting behavioral rule about create-group's flat
validation versus `buzz-cli`'s narrower creation surface and DM's separately
enforced command path; and this capability's shipped maturity per
`VISION_PROJECTS.md`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Each type's full behavior, roles, and UI | `dm-channel.md`, `forum-channel.md`, `stream-channel.md`, `workflow-channel.md` (issues #728-#731) |
| How the channels subsystem is built (containers/components) | the architecture family, once a channels-specific node is drafted |
| The interface(s) exposing channel operations | an interface-shaped corpus node, not yet drafted |
| The step-by-step creation/DM-open flow | a flow-shaped corpus node, not yet drafted |

**Expected but not verified when this node was written:**

- **Whether a client-authored kind:9007 event can actually set `channel_type=dm` or
  `channel_type=workflow` through the generic create-group path, and what happens if
  it does.** The code at the two call sites cited in the evidence ledger applies no
  per-type restriction beyond "is this one of the four known strings," but this
  review did not trace every layer an inbound EVENT frame passes through before
  reaching those handlers, and did not attempt to construct and submit such an event
  against a running relay. This is recorded as an `INFERENCE`, not a `FACT`, for
  exactly that reason.
- **Whether any real `workflow`-typed channel is ever created at runtime.** Every
  construction of `ChannelType::Workflow` found in this repository's `.rs` files sits
  inside a `#[cfg(test)]` module; whether the workflow engine, or some other path not
  covered by this grep-based review, constructs one outside tests is left to
  `workflow-channel.md` (#731) to establish directly.
- **Whether `dm-channel.md`, `forum-channel.md`, `stream-channel.md`, and
  `workflow-channel.md` (#728-#731) land with the ids this node assumes** (a
  `capabilities-channels-*` naming pattern mirroring this node's own path-derived
  id) -- this node was written without reading any of those four documents' drafts,
  since none exist on `origin/launchpad` yet.
