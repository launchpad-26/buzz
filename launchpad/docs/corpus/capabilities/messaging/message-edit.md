---
id: capabilities-messaging-message-edit
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
  - statement: "kind:40003 (`KIND_STREAM_MESSAGE_EDIT`) is Buzz's own dedicated event kind for editing an already-sent stream message; a comment on the constant records that an earlier design used kind:10004 in the NIP-16 replaceable range and that this was wrong, before settling on 40003."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:480-483"
  - statement: "kind:40003 is neither a NIP-16 replaceable kind (`is_replaceable` matches only kinds 0, 3, `KIND_CHANNEL_METADATA`, and 10000-19999) nor a NIP-33 parameterized-replaceable kind (`is_parameterized_replaceable` matches only 30000-39999); it is an ordinary, independently-addressable client-submitted kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-core/src/kind.rs:452-454"
  - statement: "At storage time, ingest branches on `is_replaceable`/`is_parameterized_replaceable` and only those two branches call `replace_addressable_event`/`replace_parameterized_event`; every other kind, kind:40003 included, falls through to `insert_event_with_thread_metadata`, which inserts a brand-new row rather than replacing an existing one. An edit event is therefore stored as its own new, independently-addressable event; the target message's own stored row is never mutated or replaced by an edit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2911-2941"
  - statement: "`buzz_sdk::build_edit(channel_id, target_event_id, new_content)` constructs the kind:40003 event: an `h` tag naming the channel, an `e` tag naming the target message's event id, and the new message text as the event's own content (not a diff/patch against the old content); content is capped at 64 KiB via `check_content`, a client-side bound distinct from the relay's general 256 KB per-event content ceiling."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:388-400"
      - "crates/buzz-sdk/src/builders.rs:34-41"
  - statement: "`buzz-cli` exposes this as `buzz messages edit <event-id> <content>` (`MessagesCmd::Edit`); `cmd_edit_message` resolves the channel from the target event's own stored `h` tag, builds the kind:40003 event via `build_edit`, signs it, and submits it -- the agent does not need to already know or pass the channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:814-835"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "On ingest, kind:40003 is routed to `validate_edit_ownership` before storage, and the generic channel member-or-open-visibility gate that most channel-scoped kinds pass through is explicitly skipped for kind:40003 -- a code comment records this as the OQ1 decision that per-kind validators (`validate_edit_ownership` among them) are the sole authority for these kinds, not the generic gate, so that an owning human can act on a private agent channel without themselves being a member."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2293-2301"
      - "crates/buzz-relay/src/handlers/ingest.rs:2490-2494"
  - statement: "`validate_edit_ownership` requires a well-formed 64-hex-character `e` tag naming a target event that exists in the same community's store, and rejects the edit if the target event's stored `channel_id` differs from the edit event's own resolved channel, or if the edit is channel-scoped but the target has no channel at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:918-962"
  - statement: "Edit authorization succeeds in exactly two cases: the edit's signer equals the target event's 'effective author' (the target's own `pubkey`, or -- for a relay/workflow-attributed event whose `pubkey` is the relay's own key -- the pubkey named in that event's `actor` tag, falling back to its first `p` tag), or the signer is not that author but is recorded in `is_agent_owner` as the owning human of the agent that authored the target. Every other signer is rejected with \"must be event author to edit\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:884-916"
      - "crates/buzz-relay/src/handlers/ingest.rs:963-996"
  - statement: "When the signer is the target's own author and the target is channel-scoped, `validate_edit_ownership` additionally re-checks live channel membership (or the channel's open visibility) at edit time -- a deliberate re-gate, per its own comment, so that a member removed from a private channel after posting cannot still mutate their own older messages; a non-member of a non-open channel is rejected \"restricted: not a channel member\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:966-985"
  - statement: "`validate_edit_ownership`'s body performs no check of the target event's own kind -- it loads whatever event the `e` tag resolves to and applies the same author/owner and channel checks regardless of whether that target is itself an ordinary message, a prior kind:40003 edit, or any other stored kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:918-998"
  - statement: "The desktop client collapses possibly-multiple kind:40003 edits per target down to one: for each target message, it keeps only the authorized edit with the greatest `created_at`, discarding edits whose target was deleted or whose target-authorship check (`isAuthorizedMessageEdit`) fails; the rendered message's `edited` flag is set only when such an edit survives, its displayed body becomes the winning edit's content, and only the edit's `imeta` (attachment) tags are overlaid onto the target's other original tags."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/formatTimelineMessages.ts:255-298"
      - "desktop/src/features/messages/lib/formatTimelineMessages.ts:505-519"
  - statement: "`isAuthorizedMessageEdit` (the desktop client's own authorization check for whether to surface an edit) independently re-derives the target message's effective author -- including resolving an agent's owning human via a fetched profile's `ownerPubkey` -- rather than assuming every stored kind:40003 event the relay accepted is safe to display as an edit."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/formatTimelineMessages.ts:195-212"
  - statement: "Dedicated end-to-end coverage exists for this capability: `crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs` states in its own module doc comment that kind:40003 message edit (`validate_edit_ownership`) is one of five authorization predicate sites it exercises for a human owner acting on content authored by their agent, and names `test_owner_can_edit_agent_message`, `test_third_party_cannot_edit_agent_message`, `test_agent_can_self_edit_message`, `test_owner_can_edit_agent_message_in_private_channel`, and `test_removed_author_cannot_edit_own_message_in_private_channel` among its test functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:1-19"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:100"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:147"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:191"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:640"
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs:828"
  - statement: "`launchpad/docs/corpus/architecture/flows/event-ingestion.md` (merged, id `architecture-flows-event-ingestion`) already documents the single shared ingest pipeline every event kind passes through, and names `validate_edit_ownership` (kind:40003 edits) explicitly among the roughly thirty per-kind structural validators that run inside it as one step of that shared flow, rather than describing message edit's own authorization rule in the depth this node does."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: implements
    target: corpus-template-capability
---

# Message edit: capability

Buzz lets a user or agent correct the content of a message they already sent, by
publishing a new signed event that names the original message and carries its
replacement text. The product surfaces this as "editing" a message in place: the
timeline shows the corrected text with an "edited" indicator, not two separate
messages. The person who may correct a message is not limited to its literal
signer -- the human who owns an agent may also correct a message that agent sent,
including inside a private channel the human is not themself a member of, so an
owner can clean up after their own agent without needing standing membership
everywhere the agent participates.

## Maturity

**Shipped.** Every layer of the path is implemented and wired together: the
dedicated event kind (`KIND_STREAM_MESSAGE_EDIT` = 40003), the SDK builder
(`buzz_sdk::build_edit`), the CLI surface (`buzz messages edit`), the relay-side
authorization rule (`validate_edit_ownership`), the desktop client's rendering of
the resulting "edited" message, and a dedicated end-to-end test suite exercising
owner/agent/third-party authorization scenarios. See the evidence ledger above
for each layer's citation.

## Boundary

This node does not describe:

- **How the shared ingest pipeline is built.** The community write-fence, scope
  checks, signature verification, storage transaction, and fan-out that every
  event kind -- including kind:40003 -- passes through are documented by
  `architecture-flows-event-ingestion`, which already names `validate_edit_ownership`
  as one of its roughly thirty per-kind validator steps. This node covers only
  what that one validator does and why, not the pipeline around it.
- **The interface(s) message edit is exposed through.** No corpus interface node
  exists yet for `buzz-cli`'s `messages` command group or for the generic
  `POST /events` bridge both the CLI and the desktop client submit an edit
  through -- this is a gap, not a decision that none exists.
- **The step-by-step flow of one edit interaction.** No corpus flow node walks a
  single edit end to end (compose -> sign -> submit -> relay validation ->
  fan-out -> client re-render); this node states that the capability exists and
  what its rules are, not the sequence a user or agent experiences.
- **How the running relay is operated.** Nothing here concerns deployment,
  monitoring, or incident response for the ingest path that enforces this
  capability.
- **Whether editing an edit is an intentional design choice.** `validate_edit_ownership`
  performs no check of the target event's own kind, so nothing in the code stops
  a kind:40003 edit from targeting a prior kind:40003 edit rather than the
  original message. No design document was found stating whether this is
  deliberate or simply unconsidered; see *Scope and omissions* below.

## Relationships

- references: `architecture-flows-event-ingestion` -- the shared ingest pipeline
  that `validate_edit_ownership` runs inside, already documented at the flow
  level.
- implements: `corpus-template-capability` -- this node is drafted from that
  template's required sections (capability statement, maturity, boundary,
  relationships, scope and omissions).

## Scope and omissions

**This node covers** what the message-edit capability lets a user or agent do,
which event kind and code paths implement it end to end, the exact authorization
rule (self-edit, agent-owner-edit, and the live re-check of channel membership
for a self-edit in a channel the author may have since left), how an edit is
stored (as its own new event, never a replacement of the original), how the
desktop client resolves and displays the winning edit when more than one exists,
and the existing end-to-end test coverage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The shared ingest pipeline's own mechanics (write-fence, scope, signature checks, storage transaction, fan-out) | `architecture-flows-event-ingestion` |
| The boundary contract (CLI command group / HTTP route) message edit is exposed through | no corpus interface node exists yet |
| The step-by-step path one edit interaction takes | no corpus flow node exists yet |
| How the relay is operated in production | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether editing an edit is intentional.** `validate_edit_ownership` applies
  the same author/owner rule to a target regardless of the target's own kind,
  so a kind:40003 event may itself be edited. No VISION document or design
  record was found that states this is deliberate rather than an unconsidered
  side effect of not checking the target's kind.
- **Whether prior (superseded) edits remain queryable as edit history anywhere
  in the product surface.** The relay never deletes or replaces a superseded
  edit event -- each is stored as its own row, per the evidence above -- but no
  CLI subcommand, HTTP endpoint, or desktop UI surfacing a message's past edits
  (as opposed to only the current winning one) was found while writing this
  node. Whether that history is reachable through the generic `POST /query`
  Nostr bridge (filtering on the target's `e` tag) was not tested against a
  running relay.
- **Whether an edit can be independently deleted (kind:5 / kind:9005) without
  affecting the original message**, and vice versa. `effective_message_author`
  and the deletion-authorization code paths were not read in this pass beyond
  what the evidence ledger cites; only edit-specific ownership was verified.
