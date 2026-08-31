---
id: capabilities-agents-agent-response
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "A Buzz agent's generated text is not shown to anyone; the agent's real output is its tool calls, which are what become Buzz-visible."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:32"
      - "crates/buzz-agent/README.md:178-180"
  - statement: "Every relay write command in the Buzz CLI returns a normalized JSON envelope of the shape {event_id, accepted, message}, produced by normalize_write_response and consumed by parse_write_response to distinguish an accepted write from a rejected or duplicate one."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs:80-98"
      - "crates/buzz-cli/src/client.rs:1451-1463"
  - statement: "Publishing an ephemeral event (used by the owner-reviewed draft commands) returns the same {event_id, accepted, message} envelope, built directly from the relay's OK response rather than from normalize_write_response, and turns a non-accepted OK into a CliError::Relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1094-1117"
  - statement: "The Buzz CLI maps every response outcome to one of six process exit codes (0 ok, 1 user/not-found, 2 network/relay, 3 auth, 4 other, 5 write conflict) and, on error, emits a JSON object on stderr carrying an error category, a human-readable message, and a retryable flag computed per error variant."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md:25"
      - "crates/buzz-cli/src/error.rs:87-108"
      - "crates/buzz-cli/src/error.rs:110-135"
  - statement: "buzz agents draft-create and buzz agents draft-update require BUZZ_AUTH_TAG (the caller's NIP-OA owner attestation); without it the command fails with CliError::Auth rather than publishing anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:172-177"
  - statement: "buzz agents draft-create and draft-update do not write the agent directly: they build an owner-encrypted request via agent_management::build_create/build_update, publish it as a kind:24200 ephemeral event (KIND_AGENT_OBSERVER_FRAME, the observer-telemetry frame), then merge request_id, the literal action name, saved: false, and a fixed message ('Draft sent to Buzz Desktop for owner review. Nothing changes until the owner saves it.') into the relay's own publish response before printing it."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:14-44"
      - "crates/buzz-cli/src/commands/agents.rs:46-86"
      - "crates/buzz-cli/src/agent_management.rs:102-165"
      - "crates/buzz-cli/src/agent_management.rs:167-216"
      - "crates/buzz-core/src/kind.rs:469"
  - statement: "buzz projects add-channel follows the identical response pattern for a different consequential action: it requires BUZZ_AUTH_TAG, builds an owner-encrypted project-channel request via agent_management::build_project_channel, publishes it the same way, and merges request_id, action: \"add-channel\", saved: false, and a fixed owner-review message into the response -- the same three-field addition and the same build() helper as the agent-draft commands, not a one-off."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:35-76"
      - "crates/buzz-cli/src/agent_management.rs:218-252"
  - statement: "The draft request event is tagged to the owner's pubkey (a 'p' tag) and the agent's own pubkey (the OBSERVER_AGENT_TAG), and its decrypted payload carries a request_id, an action, and the typed request body -- verified directly by a round-trip test that builds a create draft and decrypts it back with the owner's key."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/agent_management.rs:261-307"
  - statement: "Desktop's own agent-facing skill documentation states the same output-contract split in prose: ordinary write commands return {event_id, accepted, message}, while agent draft commands add {request_id, action, saved: false} 'because they only open an owner-reviewed Desktop draft', and BUZZ_AUTH_TAG is required for draft-create/draft-update specifically because those commands send owner-reviewed Desktop drafts."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/nest_skill.md:18"
      - "desktop/src-tauri/src/managed_agents/nest_skill.md:33"
      - "desktop/src-tauri/src/managed_agents/nest_skill.md:56"
  - statement: "Buzz Desktop decrypts and parses the observer-frame payload into a narrowly typed AgentManagementRequest (create or update, with an explicit allow-list of permitted request fields) and uses it to pre-fill an editable create/update-persona form; the agent or persona is not created or changed by this parsing step itself, only by whatever the owner later submits through that form."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agents/agentManagement.ts:1-33"
      - "desktop/src/features/agents/useAgentManagement.ts:36-58"
  - statement: "A corpus flow node already documents the ACP harness's per-turn lifecycle end to end and explicitly excludes the Buzz CLI's own response contract from its scope, naming it as a separate document's territory rather than restating it: 'The Buzz CLI surface the agent subprocess calls during a turn (send_message, get_messages, etc.) -- that is the CLI's own contract, not the harness's turn mechanics.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md:272-273"
  - statement: "The same build() helper and {request_id, action, saved: false} envelope already back two independently call sites (agent draft-create/draft-update and project add-channel) for two unrelated consequential actions, which is read here as evidence of a deliberate general mechanism for gating a consequential write behind owner review rather than a special case built once for agent creation and not intended to generalize further."
    entry_class: INFERENCE
    confidence: 0.75
    evidence:
      - "crates/buzz-cli/src/agent_management.rs:102-142"
      - "crates/buzz-cli/src/commands/agents.rs:14-44"
      - "crates/buzz-cli/src/commands/projects.rs:35-76"
---

# Agent response: capability

A Buzz agent communicates the outcome of its work not through the text it
generates -- which is not shown to anyone -- but through the actions it takes
against Buzz, and every one of those actions comes back to the agent as a
structured, machine-readable response rather than a bare success/failure flag.
An ordinary write (sending a message, reacting, editing a channel) is
acknowledged immediately with `{event_id, accepted, message}`, so the calling
agent or harness can tell an accepted write from a rejected or duplicate one
without guessing from prose. A smaller set of consequential actions --
creating or changing an agent persona, adding a project channel -- do not take
effect immediately at all: they are published as an owner-encrypted draft
request, acknowledged with `{request_id, action, saved: false}` plus an
explicit message that nothing has changed, and only become real once the
human owner reviews and saves the resulting form in Buzz Desktop. Either way,
the agent is told, in a shape it can act on, what actually happened to its
request.

## Maturity

**Shipped.** Both response shapes are live in `buzz-cli` today: the standard
write-response envelope is produced by every write command through
`normalize_write_response`/`parse_write_response`
(`crates/buzz-cli/src/commands/mod.rs:80-98`,
`crates/buzz-cli/src/client.rs:1451-1463`), and the owner-reviewed draft
variant is implemented for two independent actions -- `buzz agents
draft-create`/`draft-update` (`crates/buzz-cli/src/commands/agents.rs:14-86`)
and `buzz projects add-channel`
(`crates/buzz-cli/src/commands/projects.rs:35-76`) -- both routed through the
shared `agent_management::build()` helper
(`crates/buzz-cli/src/agent_management.rs:102-142`). A round-trip test signs a
draft, decrypts it with the owner's key, and asserts its shape
(`crates/buzz-cli/src/agent_management.rs:261-307`). Desktop's own
agent-facing skill documentation independently states the same output-contract
split in prose (`desktop/src-tauri/src/managed_agents/nest_skill.md:56`).

## Boundary

This node does not describe:

- **How a turn is built.** The ACP harness's inbound-trigger-to-termination
  lifecycle -- including that a turn's Buzz-visible effects come from actions
  the agent subprocess takes via the CLI while a `session/prompt` is in
  flight -- is `architecture-flows-agent-turn`'s territory, and that node
  explicitly names the CLI's own response contract as outside its own scope
  (`launchpad/docs/corpus/architecture/flows/agent-turn.md:272-273`). This
  node is the other half of that same boundary line.
- **The full `buzz-cli` command surface.** Every command group, subcommand,
  and flag is `crates/buzz-cli/README.md`'s own table, not restated here. This
  node covers the shape of the *response*, not an inventory of every action
  that can produce one.
- **The step-by-step sequence a human owner follows to review and save a
  draft in Buzz Desktop.** That UI flow -- opening the drafts list, editing
  the pre-filled form, submitting it -- is a flow-shaped subject in its own
  right, not narrated here; this node stops at what the *agent* receives back
  and what that response promises.
- **How the running relay or Desktop app is operated, deployed, or
  monitored.**

## Relationships

- references: architecture-flows-agent-turn

## Scope and omissions

**This node covers** the two response shapes a Buzz agent receives back for
an action it takes through `buzz-cli`: the immediate `{event_id, accepted,
message}` envelope every ordinary write returns, the CLI-wide exit-code and
stderr-error contract layered on top of it, and the owner-reviewed draft
variant (`{request_id, action, saved: false}`) that a smaller set of
consequential actions return instead of completing immediately -- currently
agent persona create/update and project-channel creation. It covers what the
response tells the agent and what it does not yet promise (namely, that
nothing changed until an owner acts), grounded in the code that produces both
shapes and in Desktop's own documentation of the same contract.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The ACP harness's per-turn lifecycle (trigger, queueing, termination) | `architecture-flows-agent-turn` |
| The full `buzz-cli` command/flag surface | `crates/buzz-cli/README.md`; a future interface-shaped corpus node |
| The step-by-step owner-review UI flow in Buzz Desktop | not yet drafted as its own corpus node |
| How the relay or Desktop app is deployed and operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **Whether any action besides agent draft-create/draft-update and project
  add-channel currently produces an owner-reviewed draft response.** A
  repository-wide search for the shared `build()` helper's call sites found
  exactly these two; a third could exist behind a differently named
  integration point that this search did not surface.
- **The relay-side handling of the kind:24200 observer frame once
  published** -- this node establishes only that the CLI builds, encrypts,
  and publishes it, and that Desktop decrypts and acts on it; the relay's own
  routing/fan-out of that ephemeral kind was not traced end to end for this
  node.
