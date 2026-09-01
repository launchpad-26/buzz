---
id: capabilities-agents-agent-mention
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
  - statement: "Sending a message with resolved mention pubkeys emits one `p` tag per pubkey via `mention_tags`, called from `build_message`; duplicate pubkeys (case-insensitively) are deduplicated before the tag is pushed."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:193-205"
      - "crates/buzz-sdk/src/builders.rs:224-237"
  - statement: "The buzz-acp harness's own contributor documentation states its event loop listens for @mention events (kind 9, with the agent's pubkey in a `#p` tag), queues them per channel, and drains queued events into a batched ACP `session/prompt` call when no prompt is already in flight for that channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:251-262"
  - statement: "`KIND_STREAM_MESSAGE`, the NIP-29 group chat message kind an @mention is delivered as, is the integer 9."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:479"
  - statement: "`match_event` implements the mention check itself: when a subscription rule's `require_mention` is true, the event must carry a `p` tag whose second element equals the agent's own hex pubkey, checked via `tag.as_slice()` rather than the tag kind's `Display` impl; any other rule condition (channel scope, kind, optional evalexpr filter) is independent of this check."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/filter.rs:368-399"
  - statement: "`require_mention` defaults to true unless disabled: it is computed as `!config.no_mention_filter`, so the harness's default `subscribe=mentions` behavior is mention-gated, and forum-style channels that don't @mention agents must explicitly opt out with `--no-mention-filter` (or, per channel, `require_mention = false`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:1304"
      - "crates/buzz-acp/src/config.rs:1409"
      - "crates/buzz-acp/README.md:223-249"
  - statement: "A matched event is queued with a `prompt_tag` and, once accepted, triggers a fire-and-forget 👀 reaction; the harness's dispatch loop drops any event that matches no subscription rule (including a `require_mention` rule with no matching `p` tag) before it ever reaches the agent."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2898-2927"
  - statement: "The inbound author gate (`--respond-to`, default `owner-only`) is checked before subscription-rule matching and applies uniformly to @mentions, DMs, thread replies and any other inbound event; owner control commands (`!shutdown`, `!cancel`, `!rotate`) are exempt from that gate but must still be kind:9 stream messages that `p`-tag-mention the agent, and are consumed by the harness rather than forwarded to the agent as a prompt."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:132-162"
  - statement: "buzz-acp's own base system prompt instructs the agent to use the addressee's exact display name for a notifying `@mention`, never to mention purely narratively, to `@mention` the delegator when finishing delegated work (not merely to acknowledge an assignment), and to respond promptly to @mentions it receives."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/base_prompt.md:56-68"
  - statement: "The desktop composer's `agent-address` `mention` tag (marker `\"agent-address\"`) is UI display metadata for reconstructing the address-tray state on render, not the delivery mechanism; the code comment directly above it states the ordinary `p` tag remains the notification mechanism."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/agentAddressMention.mjs:1-9"
  - statement: "Agent-mention wake-on-`p`-tag is exercised by a passing unit test that asserts an event without a matching `p` tag produces no match while an otherwise-identical event with one does, under a rule with `require_mention: true`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/filter.rs:639-666"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-flows-agent-turn
  - type: references
    target: architecture-containers-agent-runtime
---

# Agent mention: capability

Any Buzz user or agent can `@mention` an agent in a channel message and have that
mention wake the agent: the harness treats an inbound Nostr event carrying a `p` tag
naming the agent's own pubkey as a trigger to queue that event and, in due course, run
one ACP prompt turn against it. This is the mechanism by which a human or another
agent gets an agent's attention inside an otherwise-passive listening process — the
agent does not poll; it is woken by being named.

## Maturity

**Shipped.** The desktop composer builds the outbound `p` tag from resolved mention
pubkeys (`crates/buzz-sdk/src/builders.rs:193-205`, called from `build_message` at
`:224-237`), the buzz-acp harness's own contributor documentation describes the
mention-triggered event loop end to end (`crates/buzz-acp/README.md:251-262`), the
match logic that checks for the `p` tag is implemented and covered by a passing unit
test (`crates/buzz-acp/src/filter.rs:368-399`, test at `:639-666`), and the harness's
dispatch loop wires a successful match into the ACP prompt queue
(`crates/buzz-acp/src/lib.rs:2898-2927`).

## Behavioral rules and variants

- **Default is mention-gated.** A subscription rule's `require_mention` flag defaults
  to true (`!config.no_mention_filter`), so out of the box an agent only wakes on
  events that name its pubkey in a `p` tag — it does not react to every message in a
  channel it is a member of.
- **Forum-style channels opt out explicitly.** Because forum posts don't `@mention`
  agents, a channel or global config must disable the gate (`--no-mention-filter`, or
  per channel `require_mention = false`) for an agent to see that traffic at all.
- **The author gate runs first, unconditionally.** `--respond-to` (default
  `owner-only`) is checked before any subscription rule, including the mention check,
  and applies to every inbound event class alike (@mentions, DMs, thread replies).
  A mention from a disallowed author never reaches `match_event`.
- **Owner control commands ride the same `p`-tag mechanism but bypass the author
  gate.** `!shutdown`, `!cancel`, and `!rotate` must still be kind:9 messages that
  mention the agent, but they are intercepted and consumed by the harness rather than
  forwarded to the agent as a prompt.
- **A mention is a real notification, not free-standing UI state.** The composer's
  `agent-address` tag persists which pubkeys were addressed via the tray, but the
  wake trigger the harness actually checks is the plain `p` tag on the event.
- **The agent's own base prompt sets etiquette expectations on top of the mechanism**
  — use exact display names, never mention narratively, and `@mention` back when
  delegated work completes — none of which the harness itself enforces; these are
  conventions given to the agent, not gate conditions.

## Boundary

This node does not describe:
- the harness's full per-channel event loop, subprocess lifecycle, or queuing and
  batching mechanics beyond the single dispatch point where a mention match is turned
  into a queued event — see `architecture-flows-agent-turn`
- the buzz-acp/buzz-agent/buzz-dev-mcp container composition that runs the harness —
  see `architecture-containers-agent-runtime`
- the step-by-step sequence of one full agent turn once it has been woken (tool calls,
  ACP session lifecycle, response delivery) — that is a flow node's territory, not a
  capability statement
- how mentions of ordinary (non-agent) users are ranked, autocompleted, or rendered in
  the desktop composer UI — that is a desktop feature concern, not this capability

## Relationships

- references: architecture-flows-agent-turn — the harness event loop this capability's
  wake trigger feeds into
- references: architecture-containers-agent-runtime — the container that runs the
  subscription-rule matching and ACP dispatch this capability depends on

## Scope and omissions

**This node covers** what causes an agent to wake and take a turn because it was
`@mentioned`: how the outbound `p` tag is built, how the harness checks for it, that
the check is on by default and how it is disabled for non-mention traffic, how it
composes with the inbound author gate and the owner control-command convention, and
that display-tray metadata is distinct from the actual notification mechanism.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full per-channel event loop and queuing/batching mechanics | `architecture-flows-agent-turn` |
| The container composition running the harness | `architecture-containers-agent-runtime` |
| The step-by-step sequence of one agent turn once woken | a future flow node (not yet drafted) |
| The CLI/HTTP surface used to send a mention (`buzz messages send --mention`) | a future interface node (not yet drafted) |
| Mention autocomplete, ranking, and highlight rendering in the desktop composer | out of this capability's scope — a desktop UI concern |

**Expected but not verified when this node was written:**
- The mobile client's own mention-composition path was not read; this node's evidence
  is scoped to the desktop composer and `buzz-cli`/`buzz-sdk` paths actually traced.
- Whether every ACP-compliant third-party harness (Tier-2/Tier-3 custom harnesses,
  per `crates/buzz-acp/README.md`'s Bring Your Own Harness section) implements the same
  `require_mention` gate, or reimplements mention detection independently, was not
  checked — this node describes buzz-acp's own reference implementation only.
