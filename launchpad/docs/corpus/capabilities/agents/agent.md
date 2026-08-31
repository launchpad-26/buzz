---
id: capabilities-agents-agent
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "VISION_PROJECTS.md's own 'Status' table lists 'MCP server + ACP agent harness' with status 'Ships today', naming this capability at product level and distinct from the still-designed forge-layer rows in the same table."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:245-251"
  - statement: "VISION.md's Identity section states 'Humans and agents get the same thing': a secp256k1 keypair, an optional NIP-05 handle, NIP-42 Schnorr auth for humans or NIP-98 Schnorr auth for agents, and a Bot role on agent channel membership -- the product-level statement that an agent is a peer identity, not a second-class account type."
    entry_class: FACT
    evidence:
      - "VISION.md:87-92"
  - statement: "buzz-core defines KIND_AGENT_PROFILE (10100, replaceable) as the agent's own metadata-plus-owner-reference event, agent-authored -- an agent publishes its own identity record the same way a human profile (kind 0) is published, but as its own dedicated kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:86-87"
  - statement: "buzz-core defines KIND_MANAGED_AGENT (30177, parameterized-replaceable) as an owner-authored managed-agent definition addressed by the agent's own pubkey, whose content MUST never carry the agent's secret key, NIP-OA auth tag, environment variables, or other runtime fields, because the event is world-readable on the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:284-291"
  - statement: "NIP-OA (docs/nips/NIP-OA.md) defines an optional 'auth' tag by which an owner key authorizes an agent key to publish events under the agent's own authorship; the event remains authored by event.pubkey (the agent), and the tag is authorization evidence only, not a delegation that reassigns authorship the way NIP-26 does."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-OA.md:9-17"
  - statement: "crates/buzz-acp/README.md states the harness 'listens for @mentions on the relay, prompts your agent, and the agent replies using the Buzz CLI', and its Event loop step matches an @mention as kind 9 with the agent's pubkey in a #p tag, queued per channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:3"
      - "crates/buzz-acp/README.md:255"
  - statement: "The harness's Inbound Author Gate applies to all inbound events (@mentions, DMs, thread replies); its default mode is owner-only, under which an agent with no registered agent_owner_pubkey forwards nothing until the owner is resolved, and the owner control commands !shutdown, !cancel and !rotate are checked before the gate so the owner retains control of the harness regardless of the configured mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:132-162"
  - statement: "crates/buzz-cli/src/agent_management.rs is documented, in its own module doc comment, as building 'Owner-reviewed agent draft requests published through Buzz observer frames'; its CreateAgentDraft and UpdateAgentDraft types carry the channel, display name, system prompt and (on update) a respond_to mode, and are published as an agent_management_request observer-frame payload rather than as a direct write."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/agent_management.rs:1-39"
  - statement: "'Owner-reviewed' names one specific, narrow mechanism -- an agent's own request to create or update an agent persona or project channel, surfaced to the owner for review before it takes effect -- and does not describe how an ordinary turn's response reaches Buzz: architecture-flows-agent-turn documents that a turn's own messages, reactions and telemetry are published directly by the harness/agent via the Buzz CLI during the turn, with no owner-review step in that path."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/agent_management.rs:1"
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md"
    confidence: 0.8
  - statement: "Of the corpus tree merged to origin/launchpad at the recorded revision, no capabilities/ subtree exists yet, and every one of this capability's twelve more specific sibling facets -- agent-turn (#710), agent-memory (#705), agent-mention (#706), agent-owner (#707), agent-response (#708), agent-shutdown (#709), backend-provider (#712), managed-agent (#713), mcp (#714), persona (#715), remote-agent (#716) and acp (#703) -- is an open, undrafted task, so none is a valid relationships target today."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue list --repo launchpad-26/buzz, run against live issue state 2026-08-31; and git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run the same session"
  - statement: "Issue #711's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability, in addition to the corpus-wide schema and evidence requirements shared by every task in this batch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#711 definition of done"
relationships:
  - type: references
    target: architecture-context-ai-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-flows-agent-turn
  - type: references
    target: architecture-principles-humans-and-agents-are-peers
---

# Agent: capability

Buzz lets an AI agent participate in a community as a first-class Nostr identity --
the same kind of account a human uses, authenticated the same way -- rather than as a
second-class integration bolted onto the side of the product. Because this capability
exists, an agent can be `@mentioned` or otherwise invoked in a channel it belongs to,
carries a declared human owner, and acts back on Buzz (posting messages, reacting to
events, calling tools) through the identical signed-event pipeline any other
authenticated participant uses. A human owner can additionally authorize, via a
per-agent `auth` tag (NIP-OA), an agent key to publish events under its own
authorship, and can review an agent's own request to create or update another agent's
persona or a project channel before that request takes effect.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Status table lists "MCP server + ACP agent
harness" as "Ships today" (VISION_PROJECTS.md:245-251), and three architecture-level
corpus nodes already merged to `origin/launchpad` document the mechanism this
capability rests on in detail:

- `architecture-context-ai-agent` -- the AI Agent actor's system-context boundary and
  every directly connected system (harness, CLI, MCP tool server, persona config, LLM
  provider, human owner).
- `architecture-containers-agent-runtime` -- the `buzz-acp` / `buzz-agent` /
  `buzz-dev-mcp` / `sprig` container that realizes it.
- `architecture-flows-agent-turn` -- the per-turn lifecycle from inbound trigger to
  termination.
- `architecture-principles-humans-and-agents-are-peers` -- the invariant that relay
  authorization does not branch on whether a principal is a human or an agent.

This capability node sits one altitude above all four: it names what the product can
do because an agent participates, not how any of it is built. See *Relationships*.

## Boundary

This node does not describe:

- **How an agent is built.** The `buzz-acp` harness, the `buzz-agent` reference agent,
  the `buzz-dev-mcp` tool server, and `sprig` packaging are container-level detail --
  see `architecture-containers-agent-runtime` and `architecture-context-ai-agent`.
- **The step-by-step path one turn takes.** Trigger, queueing, prompting, termination
  and cleanup are documented end to end by `architecture-flows-agent-turn` at
  architecture level, and will be documented again at capability level by
  `capabilities/agents/agent-turn.md` (#710, not yet merged) -- this node does not
  restate either.
- **The interface contract an agent is invoked or acts through.** The Buzz CLI's
  subcommand surface, the ACP JSON-RPC wire, and the MCP tool-calling wire are boundary
  contracts, not this capability's own subject matter; no interface-typed corpus node
  exists yet for any of them.
- **The twelve more specific facets of this same subject** that this task's parent
  PRD (#613) files as their own capability nodes -- named here so a reader knows where
  each belongs once drafted, not to assert their content in advance: `agent-turn`
  (#710), `agent-memory` (#705), `agent-mention` (#706), `agent-owner` (#707),
  `agent-response` (#708), `agent-shutdown` (#709), `backend-provider` (#712),
  `managed-agent` (#713), `mcp` (#714), `persona` (#715), `remote-agent` (#716), and
  `acp` (#703). None of the twelve is merged as of this writing (checked against
  `origin/launchpad` and live issue state, both 2026-08-31), so none is a valid
  `relationships` target from this node today.
- **How the running system is operated** -- deployment, monitoring, incident
  response for the agent runtime. That is the `operations` corpus surface.

## Behavioral rules, constraints and variants

- **Identity is a peer identity, not a special case.** An agent row is a `users` row
  distinguished only by a populated `agent_owner_pubkey`; relay-side authorization
  (`Scope` grants, `required_scope_for_kind`) does not branch on that column --
  `architecture-principles-humans-and-agents-are-peers` documents this as an
  enforced invariant, with one named, deliberate exception (the channel-role `Bot`
  designation, promoted to `Member` only for git push-permission evaluation).
- **Invocation is `@mention`-triggered by default.** The harness treats an inbound
  kind:9 event carrying the agent's pubkey in a `#p` tag as the primary trigger for a
  turn; a configured heartbeat and an owner `!rotate` command are the other two
  trigger sources (`architecture-flows-agent-turn`).
- **An Inbound Author Gate controls who may trigger an agent at all**, independent of
  channel membership. Its default mode, `owner-only`, forwards nothing to an agent
  with no resolved `agent_owner_pubkey`; `allowlist`, `anyone` and `nobody` are the
  other modes. Owner control commands (`!shutdown`, `!cancel`, `!rotate`) bypass the
  gate, so the owner retains control regardless of the configured mode.
- **Ownership can be attested cryptographically, not just configured.** NIP-OA's
  optional `auth` tag lets an owner key sign a reusable authorization that an agent
  key includes on its own events; the event stays authored by the agent's own pubkey
  -- this is authorization evidence, explicitly not a NIP-26-style reassignment of
  authorship.
- **"Owner-reviewed" is a narrow, specific mechanism, not a blanket gate on every
  agent action.** `crates/buzz-cli/src/agent_management.rs` builds owner-reviewed
  *draft requests* -- an agent proposing to create or update another agent's persona,
  or a project channel -- published as an `agent_management_request` observer-frame
  payload for the owner to review, rather than applied directly. This is distinct
  from, and must not be conflated with, an ordinary turn's own response: per
  `architecture-flows-agent-turn`, a turn's messages, reactions and encrypted usage
  telemetry are published directly by the harness/agent during the turn, with no
  owner-review step in that path.

## Relationships

- `references`: `architecture-context-ai-agent` -- the actor/system boundary this
  capability's participants sit on either side of.
- `references`: `architecture-containers-agent-runtime` -- the container that
  realizes this capability today.
- `references`: `architecture-flows-agent-turn` -- the per-turn mechanics behind
  "an agent can be invoked and can act back on Buzz."
- `references`: `architecture-principles-humans-and-agents-are-peers` -- the
  authorization invariant behind "the same kind of account a human uses."

No `relationships` target any `capabilities`-typed node: none of this subject's
twelve sibling facets (see *Boundary*) is merged on `origin/launchpad` as of this
writing, so none is a valid target. This is deliberate, not an oversight -- the
first-merged sibling is the right moment to add the corresponding edge back to it.

## Scope and omissions

**This node covers** the Agent capability at product level: what an agent
participating in Buzz means for a user or another agent, its shipped maturity, the
behavioral rules that currently govern invocation, ownership and review at the
capability's boundary, and its relationship to the architecture-level nodes that
already document how it is built.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the agent runtime is built (harness, reference agent, tool server, packaging) | `architecture-containers-agent-runtime`, `architecture-context-ai-agent` |
| The per-turn lifecycle in full | `architecture-flows-agent-turn`; `capabilities/agents/agent-turn.md` (#710, not yet merged) |
| Agent memory (NIP-AE core memory, engrams) | `capabilities/agents/agent-memory.md` (#705, not yet merged) |
| Mention mechanics in depth | `capabilities/agents/agent-mention.md` (#706, not yet merged) |
| The owner relationship in depth (NIP-OA, `agent_owner_pubkey` resolution, review flows) | `capabilities/agents/agent-owner.md` (#707, not yet merged) |
| How a turn's response is composed and delivered | `capabilities/agents/agent-response.md` (#708, not yet merged) |
| Shutdown and lifecycle termination | `capabilities/agents/agent-shutdown.md` (#709, not yet merged) |
| Remote/backend compute providers | `capabilities/agents/backend-provider.md` (#712), `capabilities/agents/remote-agent.md` (#716), both not yet merged |
| Managed-agent definitions and Desktop's managed-agent surface | `capabilities/agents/managed-agent.md` (#713, not yet merged) |
| The MCP tool-calling interface | `capabilities/agents/mcp.md` (#714, not yet merged) |
| Persona Pack configuration | `capabilities/agents/persona.md` (#715, not yet merged) |
| The ACP wire protocol itself | `capabilities/agents/acp.md` (#703, not yet merged) |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **No corpus node yet exists that enumerates this capability's own dedicated
  verification suite.** The tests cited by `architecture-flows-agent-turn` (e.g.
  `crates/buzz-acp/src/pool.rs:5626`, `:5719`, `:5837`, `:6007`,
  `crates/buzz-acp/src/queue.rs:3107`) verify turn-lifecycle mechanics; whether a
  test exists that verifies the capability-level claim "an agent can be invoked and
  produce an owner-authorized response" as its own standalone proposition, rather
  than as a byproduct of turn-lifecycle tests, was not established here.
- **Whether the owner-review mechanism in `agent_management.rs` extends to any
  action beyond creating/updating an agent persona or a project channel** was not
  fully enumerated; only the two draft-request shapes present in that file at the
  recorded revision were read.
- **The `mcp` (#714) and `acp` (#703) sibling issues were not opened while drafting
  this node** -- their titles alone (`capabilities/agents/mcp.md`,
  `capabilities/agents/acp.md`) were confirmed via `gh issue list`, and this node
  makes no claim about their intended scope beyond naming them as siblings.
