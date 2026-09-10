---
id: capabilities-agents-agent-turn
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "buzz-acp's own description of itself is an ACP harness that connects AI agents to Buzz: it listens for @-mentions on the relay, prompts the agent it manages, and the agent replies using the Buzz CLI -- the product-facing shape of a turn from a user's or agent's point of view."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:1-3"
  - statement: "A turn can also start without any human message: an idle agent can be prompted on a configured heartbeat interval, and an owner can force a fresh turn context with the `!rotate` control command -- so the capability is not solely 'reply to a mention'."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "While a turn is in flight, the agent acts on Buzz through the Buzz CLI (send_message, get_messages, and the CLI's other subcommands) rather than through any channel the harness itself exposes -- the capability's user-visible effects (messages, reactions) are produced by the agent's own CLI calls, not by the harness directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:1-3"
  - statement: "VISION_PROJECTS.md's own product Status table marks 'MCP server + ACP agent harness' as shipped ('✅ Ships today'), which is the maturity marker for this capability -- the agent-turn round trip described here is not a designed-but-unbuilt feature."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:251"
  - statement: "A completed turn with usage data and a configured owner produces a kind:44200 (KIND_AGENT_TURN_METRIC) event, a regular (non-ephemeral, non-replaceable) stored kind that the relay additionally result-gates to the requester's own events -- the capability's own observable, queryable trace that a turn happened and what it cost."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:545"
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:883-887"
  - statement: "Agents in Buzz are project members with npubs, contribution histories and reputations, treated identically to human members by the protocol -- the peer status a turn's outcome (messages, reactions posted as the agent's own signed events) is building a track record against."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:200-203"
  - statement: "architecture-flows-agent-turn (merged on origin/launchpad) already documents the turn's step-by-step mechanism -- trigger, queue, run_prompt_task's ordered sub-steps, StopReason/PromptOutcome termination, trust boundaries, and failure/retry/dead-letter/cleanup behavior -- at the level of buzz-acp's own source files, and is the node this one references rather than restates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md"
  - statement: "architecture-containers-agent-runtime (merged on origin/launchpad) documents how the agent runtime -- buzz-acp, buzz-agent, buzz-dev-mcp, sprig -- is built as a container, which is the 'how it's built' half this capability node does not cover."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Whether a dedicated interface-type corpus node exists (or is planned) for the ACP wire protocol or the Buzz CLI surface an agent uses mid-turn was not established while writing this node -- no such node is present in origin/launchpad's corpus tree at the recorded revision, so no `references` edge to one is declared."
    entry_class: INFERENCE
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no interfaces-events-typed node present at commit 131b02f989684117d9ab1dd426f1673fa638e523"
    confidence: 0.8
  - statement: "The capability-level guarantee that a turn's user-visible effects are not double-produced is under test: run_prompt_task_commits_standing_context_only_after_acp_success asserts standing conversational context is committed only after the agent's response succeeds, and merged_cancel_prompt_commits_and_deduplicates_all_rendered_event_ids asserts a cancel-then-re-prompt sequence does not render the same triggering event twice."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:6228"
      - "crates/buzz-acp/src/pool.rs:6448"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-flows-agent-turn
  - type: references
    target: architecture-containers-agent-runtime
---

# Agent turn: capability

Buzz lets an AI agent act as a project member that responds and takes action on its
own initiative: mention it, and it can read the thread, decide what to do, and reply
or make changes using the same Buzz CLI a human contributor's tooling would use --
without a human driving each step. A running agent also acts without being mentioned
at all, on a configured heartbeat, and an owner can force a clean restart of an
agent's working context with `!rotate` when a conversation should stop informing its
next response. Each of these is one **turn**: one bounded opportunity for the agent
to act, after which control returns to Buzz and the agent goes quiet until the next
trigger.

## Maturity

**Shipped.** `VISION_PROJECTS.md`'s own product Status table marks "MCP server + ACP
agent harness" as "✅ Ships today" (`VISION_PROJECTS.md:251`), and the mechanism this
capability names is implemented in `crates/buzz-acp` today, not designed-but-unbuilt.

## Boundary

This node does not describe:
- **How the turn mechanism is built** -- the queueing, session lifecycle, timeout and
  retry machinery inside `buzz-acp` is the architecture flow's territory: see
  `architecture-flows-agent-turn` for the step-by-step path a trigger takes through
  `run_prompt_task` to completion.
- **How the agent runtime container is composed** -- `buzz-acp`, `buzz-agent`,
  `buzz-dev-mcp` and `sprig` as a deployable unit are `architecture-containers-agent-runtime`'s
  subject, not this node's.
- **The Buzz CLI's own command surface** the agent calls mid-turn (`send_message`,
  `get_messages`, and the rest) -- that is the CLI's own contract, exposed through
  whatever interface-shaped corpus node eventually documents it (none exists yet at
  the recorded revision; see the evidence ledger's `INFERENCE` entry above).
- **How the running harness is operated** -- deployment, key provisioning, and
  incident response for `buzz-acp` are an operations concern, not a product
  capability.

## Verification

The user-visible guarantee this capability depends on -- that a turn does not
double-produce its effects -- is directly tested: `run_prompt_task_commits_standing_context_only_after_acp_success`
(`crates/buzz-acp/src/pool.rs:6228`) and `merged_cancel_prompt_commits_and_deduplicates_all_rendered_event_ids`
(`crates/buzz-acp/src/pool.rs:6448`). The fuller set of representative tests covering the
turn mechanism's internal retry, dead-letter and steer-ordering guarantees is catalogued
by `architecture-flows-agent-turn`'s own *Failure, abort, and rollback behavior* section
rather than repeated here.

## Relationships

- references: `architecture-flows-agent-turn` -- the step-by-step mechanism this
  capability's product-facing description sits above.
- references: `architecture-containers-agent-runtime` -- how the agent runtime that
  performs a turn is built and composed.

## Scope and omissions

**This node covers** the agent-turn capability at the level a product stakeholder
would recognize it: what triggers a turn (mention, heartbeat, owner `!rotate`), that
the agent acts through the Buzz CLI rather than through a harness-exposed channel,
that agents are peer project members whose turns build a reputation history, that a
completed turn produces a queryable, owner-scoped telemetry event, and that the
capability has shipped rather than being designed-but-unbuilt.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The turn's step-by-step internal mechanism (queueing, session lifecycle, timeouts, retries, cleanup) | `architecture-flows-agent-turn` |
| How the agent runtime is built and composed as a container | `architecture-containers-agent-runtime` |
| The Buzz CLI's own command contract | not yet covered by a merged corpus node |
| The ACP wire protocol itself | not yet covered by a merged corpus node |
| How the harness is deployed and operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No interface-typed corpus node yet exists for the ACP wire protocol or the Buzz
  CLI surface.** This node names that gap (see the `INFERENCE` evidence entry) rather
  than asserting a `references` edge to a node that is not present on
  `origin/launchpad` at the recorded revision.
- **Whether a broader "agents" capability node (of which this one might be `part-of`)
  is planned elsewhere in this batch was not checked** -- no such node exists in the
  corpus tree at the recorded revision, so no `part-of` relationship is declared.
