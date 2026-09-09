---
id: interfaces-acp-message
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "buzz-acp's acp.rs states in its own module doc comment that it manages agent-subprocess communication over stdio using JSON-RPC 2.0 (newline-delimited / NDJSON), and is the only file in the crate implementing that wire format."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
  - statement: "A prompt turn's outbound message content is built by build_prompt_params, which wraps each prompt block as a `{\"type\": \"text\", \"text\": ...}` JSON object and returns `{\"sessionId\": ..., \"prompt\": [...]}`; no image, resource, or resource_link content-block variant is constructed anywhere in this crate — only the text block shape is ever sent."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:2044-2053"
  - statement: "session_prompt_blocks_with_idle_timeout sends the built params as a JSON-RPC 2.0 request with method `session/prompt`, a monotonically increasing numeric `id` taken from `next_id`, records that id in `last_prompt_id` before writing, and returns a `StopReason` parsed from the eventual response via `parse_prompt_response`/`parse_stop_reason`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:777-839"
      - "crates/buzz-acp/src/acp.rs:2034-2040"
  - statement: "A unit test constructs the literal `session/prompt` request JSON — `{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"session/prompt\",\"params\":{\"sessionId\":\"sess_abc123\",\"prompt\":[{\"type\":\"text\",\"text\":\"...\"}]}}` — and asserts the method name and the single text block's shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:2559-2577"
  - statement: "Slash-command pass-through sends the prompt as two separate text content blocks in one `session/prompt` request — the bare command first, a wrapped context block second — rather than one concatenated block, verified by a test asserting a two-element `prompt` array."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:2579-2595"
  - statement: "Inbound streamed message content arrives as `session/update` JSON-RPC notifications (no `id` field) dispatched by method name inside the core read loop; handle_session_update reads the discriminator field `sessionUpdate` (not `type`) from `params.update` and matches on it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1191-1282"
      - "crates/buzz-acp/src/acp.rs:1748-1854"
  - statement: "Of the `sessionUpdate` kinds handled, exactly two carry message text content — `agent_message_chunk` and `agent_thought_chunk` — both read from `update[\"content\"][\"text\"]`; the remaining kinds handled in the same match (`tool_call`, `tool_call_update`, `plan`, `available_commands_update`, `session_info_update`, `usage_update`, `keepalive`) carry tool-call, plan, session-metadata, or usage payloads instead of message text."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1755-1853"
  - statement: "A completed `session/prompt` response is a JSON-RPC result object whose `stopReason` field is one of `end_turn`, `cancelled`, `max_tokens`, `max_turn_requests`, or `refusal` (case-insensitively parsed by `StopReason::from_str`); a response missing `stopReason`, or carrying an unrecognized value, is rejected as `AcpError::Protocol` rather than silently defaulted."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:44-77"
      - "crates/buzz-acp/src/acp.rs:2034-2040"
  - statement: "A unit test drives the wire-level round trip by feeding the client the literal line `{\"jsonrpc\":\"2.0\",\"id\":42,\"result\":{\"stopReason\":\"end_turn\"}}` and asserts the parsed result's `stopReason` field equals `\"end_turn\"`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3216-3234"
  - statement: "A JSON-RPC error response (an object with `error.code`/`error.message` instead of `result`) is converted by `agent_error_from_json` into `AcpError::AgentError{code, message}`, preserving the numeric code; when `message` is missing or non-string it falls back to the full error object's string form so provider-specific detail (e.g. a `data` field) is not lost."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:81-124"
  - statement: "Two unit tests exercise the error path end to end: feeding the client the line `{\"jsonrpc\":\"2.0\",\"id\":0,\"error\":{\"code\":-32601,\"message\":\"Method not found\"}}` yields `Err(AcpError::AgentError{code: -32601, ..})`, and the line `{\"jsonrpc\":\"2.0\",\"id\":0,\"error\":{\"code\":-32602,\"message\":\"Invalid params\"}}` yields `Err(AcpError::AgentError{code: -32602, ..})`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3516-3546"
  - statement: "If an incoming JSON-RPC message carries an `id` but a method name this client does not recognize, the read loop writes back a JSON-RPC error response with code `-32601` (\"Method not found\") rather than staying silent, because silence would leave the agent hanging on a reply it expects."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1263-1280"
  - statement: "`has_in_flight_prompt` reports whether `last_prompt_id` is set, and `install_steer_rx` panics if a previous turn's steer receiver was not consumed, both documented as enforcing that exactly one `session/prompt` turn is in flight on a given `AcpClient` at a time — a second prompt is not dispatched concurrently on the same client/session."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:856-859"
      - "crates/buzz-acp/src/acp.rs:904-923"
  - statement: "Every JSON-RPC request's `id` is a numeric value drawn from a per-client monotonically increasing counter (`next_id`), and `read_until_response`/`read_until_response_with_idle_timeout` correlate a response to its request by comparing the incoming `id` against the expected numeric id (converted via `serde_json::json!`) — the interface has no separate request-ordering guarantee beyond this id correlation, and a resent identical message is dispatched as a new, distinct turn rather than being deduplicated."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1096-1126"
      - "crates/buzz-acp/src/acp.rs:1191-1249"
  - statement: "`session_cancel` sends `session/cancel` as a JSON-RPC notification (no `id` field), after which the agent is expected to eventually respond to the in-flight `session/prompt` with `stopReason: \"cancelled\"`; cancellation does not abort the message turn out-of-band, it changes the terminal `stopReason` of the same response the turn was already waiting on."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:841-854"
  - statement: "`initialize` sends the JSON-RPC `initialize` request with a `protocolVersion` field, and a comment on `initialize` states buzz-acp is \"requesting version 2\" as \"an intentional temporary pin — we are squatting on ACP v2 ahead of the upstream ACP RFD,\" to be revisited when that RFD merges; `authenticate` sends a separate `authenticate` request carrying a `methodId` for adapter-advertised auth methods. Both precede any `session/prompt` message exchange and are not re-negotiated per message."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:126-135"
      - "crates/buzz-acp/src/acp.rs:611-630"
  - statement: "buzz-acp's README describes the harness as working with any agent implementing \"the ACP spec\" linked to https://agentclientprotocol.com/, and states the same link in its own \"Supports any agent that speaks ACP\" line — this is the authoritative external specification this node's `session/prompt`/`session/update` message contract implements, not a Buzz-invented format."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:12"
      - "crates/buzz-acp/README.md:325"
  - statement: "Whether the upstream Agent Client Protocol specification defines additional message-shaped `session/update` kinds (for example, an echoed `user_message_chunk`) that this codebase's `handle_session_update` simply never receives or emits from the agents it currently supports (goose, codex-acp, claude-agent-acp) was not established by fetching agentclientprotocol.com directly — only this repository's own code was opened for this node."
    entry_class: INFERENCE
    confidence: 0.6
    evidence:
      - "crates/buzz-acp/src/acp.rs:1748-1854"
  - statement: "Issue #973's Definition of Done requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative machine/spec representation, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#973 definition of done"
---

# ACP message: interface

This documents the **message** exchanged inside one Agent Client Protocol (ACP)
`session/prompt` turn between `buzz-acp` (the client) and an agent subprocess (goose,
codex-acp, or claude-agent-acp) over stdio, using JSON-RPC 2.0 framed as newline-delimited
JSON (NDJSON). Two payload directions exist on this one boundary: the **outbound** prompt
content the harness sends to start or extend a turn, and the **inbound** streamed message
content (`session/update` notifications) and terminal result (the `session/prompt` response)
the agent sends back. The wire format is owned by the external Agent Client Protocol
specification (linked below), not invented by this repository; `crates/buzz-acp/src/acp.rs`
implements it directly rather than through a dependency on an external ACP crate.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `session/prompt` (request, outbound) | `crates/buzz-acp/src/acp.rs#build_prompt_params`, `session_prompt_blocks_with_idle_timeout` | Sends one or more text content blocks (`{"type": "text", "text": ...}`) for a session; only the text variant is built anywhere in this crate. |
| `session/update` (notification, inbound, message-carrying kinds) | `crates/buzz-acp/src/acp.rs#handle_session_update`, cases `"agent_message_chunk"` and `"agent_thought_chunk"` | Streamed agent reply text and streamed agent "thinking" text, each read from `update["content"]["text"]`. |
| `session/prompt` (response, inbound) | `crates/buzz-acp/src/acp.rs#parse_stop_reason` | Terminal result of the turn: a `stopReason` value, parsed via `StopReason::from_str`. |
| `session/cancel` (notification, outbound) | `crates/buzz-acp/src/acp.rs#session_cancel` | Requests the in-flight turn end early; the agent still answers the same `session/prompt` response, with `stopReason: "cancelled"`. |

Sibling `sessionUpdate` kinds that do **not** carry message text — `tool_call`,
`tool_call_update`, `plan`, `available_commands_update`, `session_info_update`,
`usage_update`, `keepalive` — are dispatched by the same `handle_session_update` match but
are out of scope here; see *Boundary* below.

## Contract and stability

**Versioning.** `initialize` sends a `protocolVersion` field; buzz-acp currently requests
version 2 as an explicitly stated temporary pin ahead of an upstream ACP RFD, to be revisited
once that RFD merges (`acp.rs:126-135,611-622`). A message turn does not renegotiate this —
`initialize` and `authenticate` happen once per agent subprocess, before any `session/prompt`
exchange, not per message.

**Errors and rejection.** A JSON-RPC error object (`{"error": {"code", "message"}}` in place
of `"result"`) on a `session/prompt` (or any) request is converted to
`AcpError::AgentError { code, message }`, preserving the numeric code (`acp.rs:81-124`). An
unrecognized inbound method carrying an `id` gets a synthesized `-32601` "Method not found"
error written back rather than silence, because an agent left waiting on a reply it never gets
would hang (`acp.rs:1263-1280`). A `session/prompt` response missing `stopReason`, or carrying
a value `StopReason::from_str` does not recognize, is rejected as `AcpError::Protocol` rather
than defaulted to any particular stop reason (`acp.rs:2034-2040`).

**Ordering and idempotency.** Requests carry a monotonically increasing numeric `id`; the read
loop correlates a response to its request by exact `id` match, and only one `session/prompt`
turn may be in flight per `AcpClient` at a time (`has_in_flight_prompt`, and
`install_steer_rx`'s panic if a previous turn's receiver was never consumed —
`acp.rs:856-859,904-923`). There is no deduplication of resent content: sending the same text
twice produces two separate `session/prompt` turns, each with its own `id` and its own
terminal `stopReason`. `session/cancel` does not create an out-of-band response — it changes
the `stopReason` the already-pending `session/prompt` response eventually carries
(`acp.rs:841-854`).

**Authentication.** `authenticate` is a separate request (`{"methodId": ...}`) sent for an
adapter-advertised auth method, prior to any message exchange; it is not carried per-message
and this node does not restate its mechanics beyond that it precedes, and is independent of,
the `session/prompt`/`session/update` contract described here.

**Authoritative spec.** The wire format documented here implements the Agent Client Protocol,
whose specification is published at <https://agentclientprotocol.com/> and is linked from
`crates/buzz-acp/README.md:12,325`. This node cites that specification rather than
re-encoding its schema a second time in Markdown; the concrete implementation in
`crates/buzz-acp/src/acp.rs` is the more precise, checkable source for any claim about how
buzz-acp actually behaves.

## Examples

**Valid: a one-block text prompt and its successful terminal response**, from
`crates/buzz-acp/src/acp.rs:2559-2577` (request) and `crates/buzz-acp/src/acp.rs:3216-3234`
(response, wire-level round trip):

```json
// outbound session/prompt request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123",
    "prompt": [
      { "type": "text", "text": "[Buzz @mention]\nChannel: test\nFrom: npub1...\nMessage: hello" }
    ]
  }
}
```

```json
// inbound terminal response
{ "jsonrpc": "2.0", "id": 2, "result": { "stopReason": "end_turn" } }
```

**Failure: a JSON-RPC error response**, from `crates/buzz-acp/src/acp.rs:3533-3546`:

```json
{ "jsonrpc": "2.0", "id": 0, "error": { "code": -32602, "message": "Invalid params" } }
```

buzz-acp converts this into `Err(AcpError::AgentError { code: -32602, message: "Invalid
params".into() })`, propagated to the caller of the request that produced it — the same
conversion path a `session/prompt` request's error response takes.

## Boundary

This node does not describe:
- **Session lifecycle** — `session/new`, `session/cancel`'s session-creation counterpart, and
  the broader session state machine. That is `interfaces/acp/session.md`'s subject (issue
  #975, not yet merged); this node only notes that `session/cancel` changes the terminal
  `stopReason` of an already-pending message response, without describing session creation or
  teardown itself.
- **Tool-call updates** — the `tool_call`/`tool_call_update` `sessionUpdate` kinds, and the
  `session/request_permission` flow they trigger. That is `interfaces/acp/tool-call.md`'s
  subject (issue #976, not yet merged).
- **The JSON-RPC envelope and protocol negotiation in depth** — `initialize`,
  `authenticate`, and `protocolVersion` negotiation beyond the one-line note above that they
  precede and are independent of a message turn. That is `interfaces/acp/protocol.md`'s
  subject (issue #974, not yet merged).
- **A full parameter-by-parameter catalogue** of every field the ACP specification defines
  for these methods, for a domain-expert reader — this node names the operations and their
  defining source, per `templates/interface.md`'s own boundary against reference-depth
  cataloguing, and does not restate the specification's field list.

## Relationships

Declared: none. The three sibling ACP interface nodes this node would naturally `references`
(`interfaces/acp/session.md` #975, `interfaces/acp/tool-call.md` #976,
`interfaces/acp/protocol.md` #974) and the two related nodes one level up
(`capabilities/agents/acp.md` #703, `implementation/crates/buzz-acp.md` #916) are none of them
merged on `origin/launchpad` at the recorded revision — `launchpad/docs/corpus/interfaces/`
does not exist there at all yet. Per `AGENTS.md`'s rule that a `relationships[].target`
naming an id no loaded node carries is a hard validation error, and that targets must resolve
against the merge-target branch rather than the author's own worktree, none of those five are
added here. The first of those siblings to merge is the natural moment to add the
corresponding `references` edges back to this node.

## Scope and omissions

**This node covers** the message content exchanged inside one ACP `session/prompt` turn:
the outbound text content-block shape, the inbound `agent_message_chunk`/
`agent_thought_chunk` streamed updates, the terminal `stopReason` response, JSON-RPC error
handling for that exchange, and how versioning, authentication, and ordering/idempotency
relate to (without restating) that message contract.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Session creation, lifecycle, and `session/new` | `interfaces/acp/session.md` (#975, unmerged) |
| Tool-call updates and permission requests | `interfaces/acp/tool-call.md` (#976, unmerged) |
| The JSON-RPC envelope and protocol/version negotiation in depth | `interfaces/acp/protocol.md` (#974, unmerged) |
| The capability of running an ACP-speaking agent at all | `capabilities/agents/acp.md` (#703, unmerged) |
| `buzz-acp` crate-level implementation detail beyond this wire contract | `implementation/crates/buzz-acp.md` (#916, unmerged) |
| Full parameter-by-parameter API-reference cataloguing | reference-depth node, not yet proposed for ACP |

**Expected but not verified when this node was written:**
- **The upstream Agent Client Protocol specification (agentclientprotocol.com) was not
  fetched directly.** Every claim above is grounded in this repository's own code
  (`crates/buzz-acp/src/acp.rs`) and its README, not in the external spec text itself. Whether
  ACP defines additional message-shaped `session/update` kinds this codebase's three supported
  agents (goose, codex-acp, claude-agent-acp) simply never emit or receive — for example, an
  echoed `user_message_chunk` — is unknown from this evidence alone.
- **No corpus node instance from `templates/interface.md` had previously been drafted**,
  since this is (per the recorded revision's `git ls-tree`) the first node created anywhere
  under `launchpad/docs/corpus/interfaces/`; whether every required section of that template
  fits this specific message-shaped subject as cleanly as it did in the template's own
  self-review is confirmed only by this node's own `validate.py` pass, not by precedent.
