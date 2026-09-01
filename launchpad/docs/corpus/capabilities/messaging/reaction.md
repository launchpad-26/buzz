---
id: capabilities-messaging-reaction
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "Reactions are NIP-25 kind:7 events: `KIND_REACTION` is defined as `7` in the kind registry, and `buzz_sdk::build_reaction` builds a `Kind::Custom(7)` event carrying a single `[\"e\", <target-hex>]` tag and the emoji as its content."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:58"
      - "crates/buzz-sdk/src/builders.rs:474-483"
  - statement: "A reaction may also carry a NIP-30 custom emoji: `build_custom_emoji_reaction` normalizes the shortcode, sets the content to `:shortcode:`, and adds an `[\"emoji\", shortcode, url]` tag alongside the `e` tag; the relay's `validate_reaction_emoji` rejects any reaction whose content exceeds 64 characters unless it is a `:shortcode:`-wrapped form with a matching `emoji` tag and a normalized (canonical lowercase) shortcode, capped by `buzz_sdk::MAX_CUSTOM_EMOJI_REACTION_LEN`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:485-503"
      - "crates/buzz-relay/src/handlers/ingest.rs:160-188"
  - statement: "The relay's ingest pipeline handles kind:7 inline, before generic event storage: it extracts the target event id from the last `e` tag (rejecting the event if none resolves to a 64-hex-char id), resolves the reacting actor, defaults empty content to `\"+\"`, validates the emoji, and only then calls `Db::insert_reaction_event_with_thread_metadata`, which runs the reaction-row upsert and the kind:7 event insert inside one Postgres transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3014-3082"
      - "crates/buzz-db/src/store/reaction.rs:160-226"
  - statement: "Within that transaction, ordering is load-bearing: the target event's current row is looked up first (a missing or soft-deleted target returns `TargetMissing` and rolls back before any write), then the reaction row is upserted with `INSERT ... ON CONFLICT (community_id, event_created_at, event_id, pubkey, emoji) DO UPDATE ... WHERE reactions.removed_at IS NOT NULL`, and only if that upsert actually changed a row does the kind:7 event get inserted -- an already-active `(target, actor, emoji)` reaction returns `Duplicate` and never stores a second kind:7 event for the same reaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs:88-226"
  - statement: "The `reactions` table's primary key is `(community_id, event_created_at, event_id, pubkey, emoji)` -- one active row per user per emoji per target event per community -- and removal is a soft-delete (`removed_at` timestamp) rather than a row delete; a partial unique index `idx_reactions_source_event` additionally enforces that a reaction's source kind:7 event id is unique within a community whenever one is set."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:539-555"
  - statement: "A reaction event carries no `h` (channel) tag of its own; `derive_reaction_channel` resolves its channel by looking up the target event's stored `channel_id`, and this derivation runs both as a NIP-29 h-tag substitute during ingest validation and again when the reaction row is inserted -- a target event with `channel_id = NULL` (e.g. a global-scope event) yields a channel-less reaction, and a target that cannot be found at all is rejected with `invalid: reaction target event not found`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:563-604"
      - "crates/buzz-relay/src/handlers/ingest.rs:2391-2407"
  - statement: "A reaction is scoped to a community end to end: the target-event lookup, the reaction-row upsert, and every read/removal path all filter by `community_id`, so an identical `(event_id, pubkey, emoji)` shape in a different community is invisible and independently addable/removable -- a regression test (`reactions_are_scoped_to_community`) added for BUG-5 exercises the full add/read/remove cycle across two communities sharing the same event/pubkey/emoji shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs:1020-1148"
  - statement: "Once stored, a reaction event is fanned out through the same post-commit path as any other stored event -- published to the community's Redis pubsub topic (channel-scoped or global) and pushed to locally subscribed WebSocket connections via `dispatch_persistent_event` -- so a reaction added or removed is visible to other connected clients in real time, not only on the next poll."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3115-3122"
      - "crates/buzz-relay/src/handlers/event.rs:349-446"
  - statement: "Aggregation/counting is read-side, not stored as a running counter: `get_reactions` groups a target event's active reaction rows by emoji (one `ReactionGroup` per emoji with its member pubkeys), and `get_reactions_bulk` batch-fetches `(emoji, COUNT(*))` pairs per event for embedding emoji+count summaries into message-list responses; both filter on `removed_at IS NULL` so a soft-deleted reaction is excluded from every count."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs:364-509"
  - statement: "Removing a reaction over Nostr is a NIP-09 deletion (kind:5) targeting the reaction's own event id, not a second kind:7; `buzz_sdk::build_remove_reaction` builds that kind:5 event, and the relay's NIP-09 deletion handler for a reaction target tries `remove_reaction_by_source_event_id` first and falls back to deriving `(target, actor, emoji)` from the reaction event's own tags/content/pubkey if the source-id backfill was missed."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:505-509"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2359-2417"
  - statement: "`buzz-cli`'s `reactions` command group exposes this capability as three subcommands: `add` (build and submit a kind:7, optionally a NIP-30 custom-emoji reaction), `remove` (query the caller's own kind:7 reactions on the target event, match by emoji content, then build and submit the kind:5 removal), and `get` (query kind:7 reactions on an event and group them client-side into emoji/count/pubkeys summaries)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/reactions.rs:9-138"
  - statement: "`buzz-cli`'s container inventory lists `reactions` as one of 22 top-level `Cmd` subcommand groups, confirming the CLI surface is not this node's own claim but an already-documented fact about the CLI container."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "A workflow definition can trigger on a reaction being added: `reaction_added` is one of three channel-event `TriggerDef` variants matched by kind, and `should_fire_workflow` additionally narrows on an exact emoji match when the trigger definition specifies one, giving workflow authors an emoji-scoped automation entry point (e.g. react with a specific emoji to fire a workflow) built directly on this capability."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs"
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "The ACP agent harness is itself a consumer of this capability, not only a trigger source: it adds a 👀 (`REACTION_SEEN`) reaction when an event is queued and a 💬 (`REACTION_WORKING`) reaction before a prompt fires, both via `reaction_add`, which builds a kind:7 with `buzz_sdk::build_reaction` and submits it through the same `POST /events` path as any other client -- these are ordinary reactions from the relay's point of view, used here as ephemeral in-band status indicators rather than user sentiment."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4721-4753"
      - "crates/buzz-acp/src/pool.rs:4697-4698"
  - statement: "Every exit path of an agent turn -- normal completion, early return, or a panic recovered via `JoinSet` -- runs `ReactionGuard`'s `Drop` impl, which spawns best-effort removal of both the 👀 and 💬 reactions the turn placed; cleanup is fire-and-forget and a stale reaction left behind by a race is explicitly documented as a harmless cosmetic edge case, not a correctness concern for this capability's own dedup/aggregation guarantees."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4320-4364"
      - "crates/buzz-acp/src/pool.rs:4884-4930"
  - statement: "A separate, ephemeral kind exists for a different feature: `KIND_HUDDLE_REACTION` (24810) is documented in the kind registry as a 'huddle emoji reaction burst', channel-scoped to the ephemeral huddle-audio flow -- it is a distinct kind from `KIND_REACTION` (7) and is not covered by this node, which documents only the persistent, NIP-25-style reaction capability."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:470-472"
  - statement: "This capability is shipped, not merely designed: the ingest-time validation, transactional storage, cross-community isolation, real-time fan-out, CLI surface, and both consumers (workflow triggers and the ACP harness's own status reactions) all exist as running code with passing or `#[ignore]`d-pending-Postgres unit tests at the recorded revision, rather than as a proposal or partial stub."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/reaction.rs:739-1148"
      - "crates/buzz-relay/src/handlers/ingest.rs:3014-3129"
    confidence: 0.9
  - statement: "Issue #777's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- which is why this document follows the `templates/capability.md` shape (Capability statement / Maturity / Boundary / Relationships / Scope and omissions) rather than a general architecture narrative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#777 definition of done"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
  - type: references
    target: architecture-flows-agent-turn
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-containers-cli
---

# Reaction: capability

A member (human or agent) can attach a lightweight emoji reaction -- a stock emoji or
a workspace custom emoji -- to any existing Buzz event, see who else reacted and with
what, and remove their own reaction later. This is the capability behind the "react to
a message" affordance a chat client or an agent building on the Buzz CLI relies on: one
reaction per person per emoji per target, aggregated into emoji/count summaries, and
visible to other connected clients in real time.

Two other parts of the platform are built directly on this same primitive rather than
alongside it: a workflow can trigger on a reaction being added (optionally scoped to one
exact emoji), and the ACP agent harness places and clears its own reactions (👀/💬) as
in-band status indicators for a running turn.

## Maturity

**Shipped.** The full path -- ingest-time validation, one-transaction storage with
dedup/reactivate semantics, community isolation, real-time fan-out, a three-subcommand
CLI surface, a workflow trigger, and the ACP harness's own reaction usage -- is running
code at the recorded revision, not a design or partial stub. See the `INFERENCE`
evidence entry above for what specifically was checked to reach that conclusion, and
*Scope and omissions* for what was not.

## Behavioral rules, constraints and variants

- **Identity of a reaction.** One active reaction per `(community, target event, actor
  pubkey, emoji)` tuple. Reacting again with the same emoji on the same event is a
  no-op (`Duplicate`); reacting with a different emoji adds a second, independent
  reaction. Removal is a soft-delete (`removed_at`), not a row delete, and a later
  identical reaction reactivates the same row rather than inserting a new one.
- **Emoji content.** A stock emoji/short string, or a NIP-30 custom emoji written as
  `:shortcode:` with a matching `[\"emoji\", shortcode, url]` tag; anything over 64
  characters that isn't a validly-tagged, canonically-lowercased custom-emoji shortcode
  is rejected at ingest. Empty content defaults to `\"+\"` (a plain "+1"-style reaction).
- **Channel derivation.** A reaction carries no `h` tag of its own -- its channel (if
  any) is derived from the target event's own stored channel at ingest time. A missing
  target is rejected outright; a target with no channel yields a channel-less reaction.
- **Storage is one atomic transaction.** Target-resolution, the reaction-row
  upsert/reactivate, and the kind:7 event insert happen together; an active duplicate
  short-circuits before the kind:7 event is ever stored, so no target event accumulates
  duplicate kind:7 rows for the same tuple.
- **Removal is a real Nostr deletion, not a toggle event.** A client removes a reaction
  by publishing a kind:5 (NIP-09) deletion targeting the reaction's own event id; the
  relay resolves that back to the reaction row primarily by the reaction event's stored
  id, falling back to deriving `(target, actor, emoji)` from the reaction event's own
  tags if the id backfill was missed.
- **Aggregation is computed at read time.** There is no running counter column;
  emoji/count/user-list summaries are grouped from the active `reactions` rows on
  demand, both for a single event (`get_reactions`) and in bulk across a message list
  (`get_reactions_bulk`).
- **Community isolation.** Every operation -- add, read, remove -- is scoped by
  `community_id`; an identical `(event, pubkey, emoji)` shape in a different community
  is a wholly independent row.
- **Two consuming variants beyond direct user reactions:**
  - A workflow's `reaction_added` trigger fires on this same kind:7 path, optionally
    narrowed to one exact emoji -- an automation entry point built on top of this
    capability, not a separate one.
  - The ACP harness adds and clears its own 👀/💬 reactions as turn-status indicators,
    using the identical add/remove mechanics a human client would use; a stale 👀 or 💬
    left behind by a cleanup race is a documented, harmless cosmetic edge case.
- **Out of scope by kind.** `KIND_HUDDLE_REACTION` (24810) is a distinct, ephemeral
  "reaction burst" kind for the huddle-audio feature and is not this capability.

## Boundary

This node does not describe:
- **How it is built.** Postgres schema, transaction internals, and the relay's ingest
  pipeline are architecture's territory -- see `architecture-flows-event-ingestion` and
  `architecture-flows-http-event-submission` in *Relationships*, not repeated here.
- **The interfaces it is exposed through beyond naming them.** `buzz-cli`'s `reactions`
  subcommand group and the relay's generic `POST /events`/`POST /query` bridge are the
  two surfaces this capability is reached through; their own request/response contracts
  belong to an interface node, not this one.
- **The step-by-step flow of one interaction through it.** No flow node for "add a
  reaction" exists yet in the merged corpus; this node names the capability and its
  rules, not a narrated sequence of steps.
- **How the running system is operated.** Deployment, monitoring, or incident response
  for the relay's reaction path is the `operations` corpus surface, not this one.

## Relationships

- `references: architecture-flows-workflow-execution` -- the `reaction_added` trigger
  variant is built directly on this capability's kind:7 path.
- `references: architecture-flows-agent-turn` -- `ReactionGuard`'s 👀/💬 lifecycle is a
  second, harness-internal consumer of the same add/remove mechanics.
- `references: architecture-flows-event-ingestion` -- documents the shared per-kind
  channel-resolution step (including the reaction-derives-from-target-event rule) this
  node cites rather than re-describing in full.
- `references: architecture-flows-http-event-submission` -- documents the generic
  `POST /events` storage path's duplicate-upsert behavior for kind:7 that this node's
  add/dedup rules build on.
- `references: architecture-containers-cli` -- documents the `buzz-cli` container's
  full 22-group command surface, of which `reactions` is one group.

## Scope and omissions

**This node covers** the reaction capability itself: what a reaction is (NIP-25 kind:7,
optionally NIP-30 custom emoji), its identity/dedup/soft-delete rules, how its channel is
derived, how it is aggregated for display, how it is removed, its real-time visibility to
other clients, the CLI surface it is reached through, and its two built-on-top consumers
(workflow triggers, the ACP harness's own status reactions).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Postgres schema and ingest pipeline internals in full | `architecture-flows-event-ingestion`, `architecture-flows-http-event-submission` |
| The `buzz-cli reactions` and relay HTTP request/response contracts | an interface node (none merged yet for this surface) |
| The step-by-step path through adding/removing a reaction | a flow node (none merged yet for this surface) |
| Huddle audio's ephemeral `KIND_HUDDLE_REACTION` (24810) burst mechanism | the huddle-audio flow/capability, not this node |
| How the relay operates or is monitored in production | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- Whether the desktop or mobile clients render reaction affordances, and if so how they
  call the underlying add/remove/get paths, was not checked -- this node verifies the
  relay, `buzz-db`, `buzz-sdk`, `buzz-cli`, and `buzz-acp` sides only.
- Whether any corpus node yet documents the `buzz-cli reactions` command group or the
  relay's generic event-bridge endpoints as their own interface node was checked
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, at the
  recorded revision: no `interfaces-events`-typed node exists in the merged corpus at
  all) -- there is nothing yet to `references` for that surface, which is why no such
  relationship is declared above.
- Whether a `reaction_removed`-shaped workflow trigger exists was not checked beyond
  what `architecture-flows-workflow-execution` already documents (`reaction_added` is
  the only reaction-shaped trigger variant that node names).
