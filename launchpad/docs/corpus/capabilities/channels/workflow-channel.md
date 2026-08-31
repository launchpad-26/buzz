---
id: capabilities-channels-workflow-channel
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
  - statement: "buzz-core's ChannelType enum has four variants -- Stream, Forum, Dm, Workflow -- and the Workflow variant's own doc comment describes it as 'Internal workflow execution channel', with canonical string representation 'workflow' used for both display and round-trip parsing (FromStr)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "Migration 0001_initial_schema.sql defines the Postgres channel_type enum as ('stream', 'forum', 'dm', 'workflow') and the channels table's channel_type column DEFAULT is 'stream', not 'workflow' -- a channel is stream-typed unless something explicitly requests otherwise."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "The relay's kind:9007 (create channel) ingest handler reads an optional channel_type tag, defaults it to 'stream' when the tag is absent, and parses whatever string is present through ChannelType::from_str with no allow-list narrower than the four registered enum values -- a signed event explicitly tagging channel_type=workflow parses successfully and is passed to create_channel_with_id exactly like any other type, with only unparseable strings rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Neither of the two first-party client surfaces that create channels offers 'workflow' as a selectable channel type: buzz-cli's own ChannelType clap enum (crates/buzz-cli/src/lib.rs) lists only Stream and Forum as value-enum variants, and the desktop app's ChannelType TypeScript union (desktop/src/shared/api/types.ts) is 'stream' | 'forum' | 'dm', omitting 'workflow' entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "desktop/src/shared/api/types.ts"
  - statement: "A repository-wide, case-sensitive search for the literal ChannelType::Workflow found only its own enum definition and match arms inside crates/buzz-core/src/channel.rs (the Self::Workflow arms in as_str and from_str); no other .rs file in the workspace constructs a channel with this type."
    entry_class: FACT
    evidence:
      - "grep_repo('ChannelType::Workflow', glob='**/*.rs') -> matches only crates/buzz-core/src/channel.rs's own enum definition and match arms, run at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The workflows table's channel_id column is a plain nullable foreign key to channels(community_id, id) with no channel_type constraint at all, and command_executor.rs's only channel_type comparisons (excluding DM channels from two other command kinds) are unrelated to workflow-channel binding -- a workflow definition binds to whichever channel hosted the kind:30620 command that created it, of any channel_type, not specifically one typed 'workflow'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-relay/src/handlers/command_executor.rs"
  - statement: "get_accessible_channels's own doc comment and its ORDER BY clause state the accessible-channel listing is ordered stream -> forum -> dm via array_position against ARRAY['stream','forum','dm']::text[]; that array omits 'workflow' entirely, while the same query's WHERE clause special-cases only 'dm' (excluding memberships the user has hidden) and does not exclude channel_type='workflow' rows from the result set."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
  - statement: "Because Postgres's default ascending ORDER BY places NULL last, a workflow-typed channel visible to a querying user -- whose array_position lookup against ['stream','forum','dm'] evaluates to NULL because 'workflow' is absent from that array -- would sort after every dm channel in get_accessible_channels's result rather than being excluded from it or erroring."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/channel_members.rs"
    confidence: 0.75
  - statement: "The relay's fleet-wide usage metric usage_channel_counts defines its own recognized-channel-type allowlist as CHANNEL_TYPES: &[&str] = &['stream', 'forum', 'dm', 'workflow'], zero-filling and reporting 'workflow' as a first-class type alongside the other three -- unlike get_accessible_channels's ordering array, this list does include it, so the two code paths disagree on whether 'workflow' is one of the channel_type's enumerated cases."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The already-merged corpus flow node architecture-flows-workflow-execution documents how a workflow definition's three trigger paths (channel event, schedule, webhook) execute once the definition is bound to a channel, but its own Scope statement does not mention channel_type as a concept at all, and nowhere does it state that a workflow's bound channel must, or must not, carry channel_type='workflow' -- the two subjects (how workflows execute, and what a workflow-typed channel is) are documented independently of each other in the current codebase."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "crates/buzz-core/src/channel.rs's own #[cfg(test)] module contains exactly one test, covering canonical_channel_name; no test anywhere in the crate, and no test found by the repository-wide ChannelType::Workflow search above, exercises the Workflow variant's Display/FromStr round trip or any behavior distinguishing a workflow-typed channel from any other type -- this capability has no dedicated automated verification today."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
  - type: implements
    target: corpus-template-capability
---

# Workflow channel: capability

Buzz's channel model recognizes a fourth `channel_type` value, `workflow`, alongside
the ordinary `stream`, `forum`, and `dm` types a user or agent can select when
creating a channel. `buzz-core`'s own doc comment names its purpose: an "internal
workflow execution channel." A product stakeholder reading the schema would expect
this to mean workflows execute inside a channel type reserved for that purpose,
separate from the channels people actually chat in.

## Maturity

**Schema-level: shipped.** The Postgres `channel_type` enum and the `ChannelType`
Rust enum both carry `workflow` as a registered value, and the relay's kind:9007
create-channel ingest handler will accept and store a channel explicitly tagged
`channel_type=workflow` — nothing in the validation path treats it as invalid or
internal-only.

**As a distinct, reachable capability: not built.** No first-party client offers
`workflow` as a creatable channel type — not `buzz-cli`'s own `ChannelType`
value-enum (Stream/Forum only) and not the desktop app's `ChannelType` union
(`stream` | `forum` | `dm`). No code path anywhere in the Rust workspace constructs
`ChannelType::Workflow`; the only occurrences of that variant are its own
definition and string round-trip in `channel.rs`. And the mechanism a reader would
expect to depend on this type — a workflow's binding to "its" channel — does not:
`workflows.channel_id` is an unconstrained foreign key to any channel, and a
workflow binds to whatever channel hosted the `kind:30620` command that created it,
typically an ordinary stream or forum channel. The already-merged
`architecture-flows-workflow-execution` node, which documents workflow triggers and
execution in detail, never mentions `channel_type` at all — because nothing in that
flow depends on it.

**Internally inconsistent even where it is referenced.** The two backend code paths
that do enumerate the four `channel_type` values disagree with each other:
`usage_channel_counts` (relay metrics) treats `workflow` as a first-class,
recognized type; `get_accessible_channels`'s ordering `array_position` lookup
omits it, which — while it does not exclude a workflow-typed channel from the
result set — leaves its display order unspecified in a way the query's own doc
comment does not disclose.

## Boundary

This node does not describe:

- **How a workflow trigger fires and a run executes once bound to a channel** —
  that is fully specified by `architecture-flows-workflow-execution`, which this
  node `references` rather than restating. That flow's own scope note confirms it
  treats *any* bound channel identically regardless of `channel_type`.
- **The interface a channel is created through** — the `kind:9007` Nostr event
  shape, `buzz-cli`'s command surface, or the desktop creation dialog. No interface
  node exists yet for channel creation to point at.
- **The step-by-step path a user or agent takes to create or use a channel** — no
  flow node for channel creation exists yet to point at.
- **How the running system is operated** — this is not a deployment or monitoring
  concern.
- **Why `ChannelType::Workflow` was added with no construction site anywhere in the
  workspace.** No git history, PR, or issue was traced for this — see *Scope and
  omissions*.

## Verification

**No automated verification exists for this capability today.** `channel.rs`'s own
`#[cfg(test)]` module contains exactly one test (`canonical_channel_name`'s
whitespace/hash-trimming rules), and it does not touch `ChannelType` at all. The
repository-wide search for `ChannelType::Workflow` construction sites (see
*Maturity*) found no test — unit or integration — anywhere in the workspace that
round-trips the `Workflow` variant's `Display`/`FromStr` implementation, or that
exercises any behavior distinguishing a workflow-typed channel from a stream or
forum channel. The closest thing to verification is the implementation itself: the
ingest handler's generic `ChannelType::from_str` parse (which accepts `"workflow"`
identically to any other registered value) and `main.rs`'s metrics allowlist
(which names it explicitly). Neither is a test asserting workflow-channel
behavior; both are the production code this node already cites as evidence, read
directly rather than exercised by a passing check.

## Relationships

- references: `architecture-flows-workflow-execution` — the flow that executes once
  a workflow definition is bound to a channel, independent of that channel's
  `channel_type`.
- implements: `corpus-template-capability` — this node is an instance of that
  template.

## Scope and omissions

**This node covers** what the `workflow` value of `channel_type` is, where it is
defined and recognized in the schema and backend code, which surfaces do and do not
expose it as a creatable option, that no code path currently constructs a channel
with it, that the workflow engine's own channel binding does not depend on it, one
concrete inconsistency between two backend code paths that enumerate
`channel_type`'s values, and that no automated test verifies any of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a workflow trigger fires and a run executes once bound to a channel | `architecture-flows-workflow-execution` |
| The boundary contract for creating a channel (Nostr event shape, CLI, desktop dialog) | an interface node, not yet drafted |
| The step-by-step path a user or agent takes to create or use a channel | a flow node, not yet drafted |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether any code outside the Rust workspace** (desktop's Tauri/Rust backend
  bridge calls, or the Flutter mobile app) references or special-cases
  `channel_type='workflow'` — the construction-site search was scoped to `**/*.rs`
  only.
- **Whether a signed `kind:9007` event with `channel_type=workflow` was actually
  submitted end-to-end against a running relay.** This node establishes only that
  the ingest handler's parsing logic would accept and store it, from reading the
  code — not that this was exercised live.
- **Why `ChannelType::Workflow` exists with no construction site.** Git blame or PR
  history for the variant's introduction in `crates/buzz-core/src/channel.rs` was
  not traced, so whether it is a placeholder for planned work, a removed feature's
  leftover, or an intentionally schema-only reservation is unknown.
