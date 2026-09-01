---
id: interfaces-acp-protocol
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "buzz-acp's acp.rs module doc comment states it 'manages communication with an AI agent subprocess over stdio using JSON-RPC 2.0 (newline-delimited / NDJSON)', and no agent-client-protocol (or similarly named) crate appears in crates/buzz-acp/Cargo.toml's dependency list — the wire protocol is implemented directly in this repository's own code, not via an external ACP crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
      - "crates/buzz-acp/Cargo.toml"
  - statement: "crates/buzz-acp/README.md documents the external protocol this interface implements ('speaks ACP over stdio', linking https://agentclientprotocol.com/) and states the minimal requirements an ACP-speaking agent binary must satisfy: accept initialize and return a result; accept session/new with mcpServers and return a sessionId; accept session/prompt with a text message and stream session/update notifications; return a stopReason."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:12"
      - "crates/buzz-acp/README.md:325-330"
  - statement: "README.md's own ASCII diagram places buzz-acp as the middle hop between the Buzz relay (WebSocket) and the agent subprocess (stdio) — this node documents only the stdio/ACP half of that bridge, not the relay-facing WebSocket half."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:5-10"
  - statement: "Every outbound line is a single complete JSON value terminated by a newline; the reader side is a tokio_util FramedRead over LinesCodec::new_with_max_length(MAX_LINE_SIZE), with MAX_LINE_SIZE set to 10_000_000 bytes, so a line exceeding 10MB is rejected at the read level rather than growing the buffer unbounded."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:21-23"
      - "crates/buzz-acp/src/acp.rs:146-149"
      - "crates/buzz-acp/src/acp.rs:551"
      - "crates/buzz-acp/src/acp.rs:1196-1210"
  - statement: "A request is built as {\"jsonrpc\":\"2.0\",\"id\":<u64>,\"method\":<str>,\"params\":<value>}; a notification is the same shape with the \"id\" key omitted entirely — the absence of \"id\" is JSON-RPC 2.0's own distinguisher between a request awaiting a reply and a notification that gets none."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1096-1109"
      - "crates/buzz-acp/src/acp.rs:1160-1179"
  - statement: "Request ids are assigned from a single per-AcpClient monotonically increasing counter (next_id, starting at 0), and the harness only ever emits numeric ids; incoming ids are compared as serde_json::Value against json!(expected_id) so that an agent replying with either a numeric or a string id (both legal under JSON-RPC 2.0) is still matched correctly."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:150-152"
      - "crates/buzz-acp/src/acp.rs:1101-1102"
      - "crates/buzz-acp/src/acp.rs:1242-1243"
  - statement: "An incoming message counts as the response to an in-flight request only when its \"id\" equals the expected id AND it carries no \"method\" field; a message with a matching id but a method field is treated as an agent-initiated request instead, so an agent that happens to reuse an id value for its own request is never mistaken for the awaited response."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1239-1249"
  - statement: "A JSON-RPC error object on a response is converted into AcpError::AgentError{code, message} by agent_error_from_json, preserving the numeric code (defaulting to -32000 if absent) and falling back to the full JSON object's string form as the message when the error's own \"message\" field is missing or non-string, so provider-specific detail (e.g. a \"data\" field) is not silently lost."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:112-124"
  - statement: "AcpError enumerates ten distinct failure shapes a caller can match on: Io, Json, AgentExited, IdleTimeout, HardTimeout, CancelDrainTimeout, Timeout, WriteTimeout, Protocol(String), and AgentError{code, message} — the last two carry the two kinds of protocol-level rejection (a locally detected framing/shape violation, versus an error object the agent itself sent back)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:80-111"
  - statement: "When the read loop receives an agent-initiated message whose method is not one of the three it recognizes (session/update, _goose/unstable/session/update, session/request_permission) and that message carries an \"id\", the harness writes back a JSON-RPC error response {\"jsonrpc\":\"2.0\",\"id\":<id>,\"error\":{\"code\":-32601,\"message\":\"Method not found: <method>\"}} rather than staying silent, because silence would leave the agent hanging on a reply that never arrives."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1260-1279"
  - statement: "A stdout line that fails to parse as JSON is not treated as a protocol failure that ends the connection; it is logged at warn level, emitted to the local observer as an \"acp_parse_error\" event, and skipped so the read loop continues to the next line."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1219-1236"
  - statement: "Writes to the agent's stdin are bounded by a 30-second WRITE_TIMEOUT (surfaced as AcpError::WriteTimeout on expiry); non-prompt request/response round trips (e.g. initialize, session/new) are bounded by a 60-second REQUEST_TIMEOUT constant (surfaced as AcpError::Timeout), so a stuck non-prompt call fails after roughly 90 seconds worst case rather than blocking forever."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1068-1085"
      - "crates/buzz-acp/src/acp.rs:1092-1126"
  - statement: "session/prompt is bounded differently: an idle deadline that resets on every valid stdout line (firing AcpError::IdleTimeout on silence) runs alongside an absolute wall-clock hard_deadline passed in by the caller (firing AcpError::HardTimeout), so a continuously-chatty-but-stuck agent is still bounded even though the idle timer alone would never fire for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1284-1322"
      - "crates/buzz-acp/src/acp.rs:1349-1370"
  - statement: "AcpClient::initialize always sends {\"protocolVersion\": 2, \"clientCapabilities\": ..., \"clientInfo\": {\"name\": \"buzz-acp\", \"version\": env!(\"CARGO_PKG_VERSION\")}}, and the initialize function's own comment states this is 'an intentional temporary pin -- we are squatting on ACP v2 ahead of the upstream ACP RFD', to be revisited once that RFD merges."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:126-135"
      - "crates/buzz-acp/src/acp.rs:611-614"
  - statement: "The harness does not reject an agent that reports a protocolVersion other than 2 in its initialize response; call sites read init_result[\"protocolVersion\"].as_u64().unwrap_or(1), defaulting to 1 when the field is absent, and proceed rather than failing the handshake."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:4795"
  - statement: "pool.rs gates two specific optional behaviors -- which transport carries the system prompt on session/new, and whether standing (non-turn) context is included in a prompt -- on protocol_version >= 2 versus < 2, with one named per-adapter exception: an agent identified by the package name \"@agentclientprotocol/claude-agent-acp\" is treated as supporting the v2-style _meta.systemPrompt transport even when it reports protocolVersion: 1, because that capability landed in that adapter's v0.6.0 before the package rename and is therefore a reliable capability signal independent of the reported version number."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:240-279"
      - "crates/buzz-acp/src/pool.rs:1685-1699"
  - statement: "The combination of always requesting the harness's own preferred protocol version, tolerating a lower version the agent actually reports, and gating individual optional features on the reported version (with narrow, explicitly-named per-adapter capability exceptions) is this interface's versioning/compatibility contract: capability-gated tolerance rather than a hard version match requirement."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:126-135"
      - "crates/buzz-acp/src/lib.rs:4795"
      - "crates/buzz-acp/src/pool.rs:240-279"
    confidence: 0.85
  - statement: "The client's initialize params advertise clientCapabilities including {\"auth\": {\"terminal\": true}} and {\"_meta\": {\"terminal-auth\": true, \"goose\": {\"customNotifications\": true}}}; the code comment states adapters decide which auth methods to expose from this signal and that 'Buzz does not hardcode vendor login commands from this capability.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:393-414"
  - statement: "The agent's initialize response may carry an authMethods array (each entry with an id and name); buzz-acp's own auth-methods and authenticate CLI subcommands read that array via extract_auth_methods, list the advertised methods, and (for authenticate) confirm the requested methodId is one of them before sending an authenticate request with {\"methodId\": <id>} and awaiting the adapter's own result."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:624-630"
      - "crates/buzz-acp/src/lib.rs:4816-4914"
  - statement: "Authentication/authorization for this interface is delegated entirely to the adapter: buzz-acp's own role is to advertise that it can hand a user to a terminal login flow, discover which named methods the adapter offers, and forward a chosen methodId to the adapter's authenticate handler -- it implements no credential exchange of its own."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:393-414"
      - "crates/buzz-acp/src/acp.rs:624-630"
      - "crates/buzz-acp/src/lib.rs:4816-4914"
    confidence: 0.8
  - statement: "session/cancel is sent as a JSON-RPC notification (no \"id\" field, no response expected for the notification itself); the code comment states the agent will eventually respond to the separate, already in-flight session/prompt request with stopReason: \"cancelled\" instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:841-854"
  - statement: "A scripted-subprocess test (goose_system_prompt_request_uses_set_contract) demonstrates one valid request/response round trip end to end: the harness writes a JSON-RPC request, the scripted agent echoes the received method and params back inside its result object, and the harness's returned value carries exactly the method name and parameter fields the harness sent."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3493-3514"
  - statement: "A companion scripted-subprocess test (goose_system_prompt_preserves_method_not_found_for_fallback) demonstrates the failure path: the scripted agent replies with {\"error\":{\"code\":-32601,\"message\":\"Method not found\"}}, and the harness call returns Err(AcpError::AgentError{code: -32601, ..}) rather than panicking or silently discarding the error."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3516-3530"
  - statement: "This node's scope is the boundary/protocol layer only -- JSON-RPC framing, versioning, ordering, error and auth-capability contract -- and deliberately excludes the message-content, session-lifecycle and tool-call/permission contracts, which are separate corpus nodes being authored in parallel for this same interface (tracked as launchpad-26/buzz#973, #975 and #976 respectively) and are unmerged at the time this node was written, so they are named here by issue number and filename only, never as a relationships target."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz Feature #616 corpus batch dispatch instructions for issue #974"
relationships:
  - type: references
    target: architecture-flows-agent-turn
  - type: implements
    target: corpus-template-interface
---

# ACP protocol/transport: interface

This node documents the overall Agent Client Protocol (ACP) wire contract that
`buzz-acp` (the ACP harness bridging Buzz relay events to AI agent subprocesses)
implements: a JSON-RPC 2.0 request/notification/response exchange, carried as
newline-delimited JSON (NDJSON) over an agent subprocess's stdin/stdout pipes. One
`AcpClient` (`crates/buzz-acp/src/acp.rs`) owns one agent subprocess and speaks this
protocol to it directly, in this repository's own code — no external
`agent-client-protocol` crate is a dependency of `crates/buzz-acp`. `buzz-acp`'s own
`README.md` states the harness supports any agent that speaks the externally owned
[ACP spec](https://agentclientprotocol.com/) over stdio (goose, codex via
`codex-acp`, and Claude Code via `claude-agent-acp`), and gives the minimal
requirements an adapter must satisfy. This node describes that transport-level
contract; it is the middle "stdio" hop of the harness's own diagram
(`README.md:5-10`), not the WebSocket hop to the Buzz relay on the other side.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `initialize` | `crates/buzz-acp/src/acp.rs` (`AcpClient::initialize`, `build_initialize_params`) | Protocol version + capability negotiation. Must be called exactly once, before any other method. |
| `authenticate` | `crates/buzz-acp/src/acp.rs` (`AcpClient::authenticate`) | Invoke one adapter-advertised auth method, named by `methodId` from `initialize`'s `authMethods`. |
| `session/new` | `crates/buzz-acp/src/acp.rs` (`AcpClient::session_new_full`) | Create a session. Parameter/response shape is out of scope here — see the sibling session-contract node (#975). |
| `session/prompt` | `crates/buzz-acp/src/acp.rs` (`AcpClient::session_prompt_blocks_with_idle_timeout`) | Send a turn's prompt content. Content-block shape is out of scope here — see the sibling message-contract node (#973). |
| `session/cancel` | `crates/buzz-acp/src/acp.rs` (`AcpClient::session_cancel`) | Notification (no `id`) requesting the agent stop the in-flight `session/prompt`. |
| `session/update` | `crates/buzz-acp/src/acp.rs` (`read_until_response`'s `"session/update"` arm) | Agent-to-client notification stream during a turn. Notification kinds are out of scope here — see #973. |
| `session/request_permission` | `crates/buzz-acp/src/acp.rs` (`handle_permission_request`) | Agent-to-client request for tool-call approval. Option/outcome semantics are out of scope here — see the sibling tool-call-contract node (#976). |
| *(unrecognized agent-initiated request)* | `crates/buzz-acp/src/acp.rs` (`read_until_response`'s `other =>` arm) | Answered with a JSON-RPC `-32601` error rather than left unanswered, so the agent is never left hanging on a reply. |

## Contract and stability

**Framing.** Every message is exactly one JSON value on one line, terminated by a
newline (NDJSON). The reader enforces a 10MB (`MAX_LINE_SIZE`) bound per line via
`LinesCodec::new_with_max_length`; a line exceeding it is a protocol error, not a
silently truncated read.

**Message shape.** A request is
`{"jsonrpc":"2.0","id":<u64>,"method":<str>,"params":<value>}`. A notification is
the same shape with `"id"` omitted entirely — JSON-RPC 2.0's own distinguisher
between "expects a reply" and "does not."

**Ordering and response matching.** Request ids come from one per-`AcpClient`
monotonically increasing counter; the harness only ever emits numeric ids, but
compares incoming ids as `serde_json::Value` so an agent replying with a string id
(legal under JSON-RPC 2.0) still matches. A message counts as *the* response to an
in-flight request only when its `id` matches **and** it carries no `method` field —
otherwise it is treated as an agent-initiated request that happens to reuse that id
value, never as the awaited response.

**Error contract.** A JSON-RPC error object on a response becomes
`AcpError::AgentError{code, message}`, preserving the numeric code (defaulting to
`-32000` if absent) and falling back to the whole error object's JSON text as the
message when `message` itself is missing or non-string, so provider-specific detail
is never silently dropped. `AcpError` also carries distinct variants for I/O,
deserialization, unexpected process exit, three flavors of timeout, and a generic
`Protocol(String)` for locally detected shape violations — callers can match the
protocol-level failure they actually need to handle differently from a transport
failure.

**Never-answered agent-initiated requests, and malformed lines.** An
agent-initiated request naming a method the harness does not recognize gets an
explicit `-32601 Method not found` JSON-RPC error reply rather than silence (silence
would hang the agent). A stdout line that fails to parse as JSON at all is logged
and skipped rather than ending the connection.

**Timeouts.** Writes to the agent's stdin are bounded to 30 seconds
(`AcpError::WriteTimeout`). Non-prompt request/response round trips (`initialize`,
`session/new`, etc.) are bounded to 60 seconds (`AcpError::Timeout`) — worst case
roughly 90 seconds wall clock. `session/prompt` instead runs an idle deadline (reset
on every valid stdout line, firing `AcpError::IdleTimeout` on silence) alongside an
absolute hard wall-clock deadline (`AcpError::HardTimeout`), so a continuously
chatty but stuck agent is still bounded.

**Versioning/compatibility.** `initialize` always requests `protocolVersion: 2` — a
deliberate temporary pin the code's own comment describes as "squatting on ACP v2
ahead of the upstream ACP RFD," to be revisited once that RFD merges. The harness
does not hard-fail on a different reported version: it reads
`init_result["protocolVersion"]`, defaulting to `1` when the field is absent, and
proceeds. Higher-level code (`pool.rs`) then gates two specific optional behaviors —
which transport carries the system prompt on `session/new`, and whether standing
context rides along in a prompt — on `protocol_version >= 2` versus `< 2`, with one
named per-adapter exception: an agent identified as
`@agentclientprotocol/claude-agent-acp` by package name is treated as supporting the
v2-style transport even when it reports `protocolVersion: 1`, because that
capability shipped in that adapter's v0.6.0 release before its package rename and is
therefore a more reliable signal than the version number for that one adapter. The
net contract is capability-gated tolerance, not a hard version match.

**Authentication/authorization.** The client advertises capabilities in
`initialize`'s params — `clientCapabilities.auth.terminal: true` and
`_meta.terminal-auth: true` — signaling it can hand a user to a terminal-native
login flow; the code's own comment states "Buzz does not hardcode vendor login
commands from this capability." The agent's `initialize` response may carry an
`authMethods` array (`id`/`name` pairs); `buzz-acp`'s `auth-methods` and
`authenticate` CLI subcommands read that array, and `authenticate` sends
`{"methodId": <id>}` naming one of the advertised methods. The adapter owns the
actual credential exchange end to end — this interface only discovers and invokes
it.

## Boundary

This node does not describe:
- `session/new`'s parameter shape, `session/prompt`'s content-block/system-prompt
  encoding, or `session/update`'s notification kinds and payloads — the
  message-level contract, owned by the sibling node for `launchpad-26/buzz#973`
  (unmerged at the time this node was written).
- The session lifecycle in depth — creation, model/config selection, mid-turn
  steering (`_goose/unstable/session/steer`, `_session/steering`) — owned by the
  sibling node for `launchpad-26/buzz#975` (unmerged at the time this node was
  written).
- The tool-call/permission contract in depth — `session/request_permission`'s
  option `kind`s, the `allow_once`/`reject_once` auto-approval policy and its
  `outcome` values — owned by the sibling node for `launchpad-26/buzz#976`
  (unmerged at the time this node was written).
- A full parameter-by-parameter API-reference catalogue for domain experts —
  inherited from `templates/interface.md`'s own boundary against `#1346`/`#1532`.

## Relationships

- `references: architecture-flows-agent-turn` — that merged node describes the
  system-level turn flow (mention → prompt → reply) this protocol is the wire
  contract underneath; a loose, supporting-context pointer per
  `relationships.schema.json`'s stated directionality for `references`, not an
  ownership or currency dependency.
- `implements: corpus-template-interface` — this node is an instance of that merged
  template, per the template's own documented convention for this optional
  self-link.
- No relationship targets the sibling `#973`/`#975`/`#976` nodes: they are unmerged
  on `origin/launchpad` at the time this node was written, so any id guessed at
  them would be a hard validation error the moment it landed on the wrong side of a
  merge race. They are named above only in prose, by issue number and filename.

## Scope and omissions

**This node covers** the ACP protocol/transport contract `buzz-acp` implements over
an agent subprocess's stdio: JSON-RPC 2.0 / NDJSON framing, the request/notification
message shapes, id-based ordering and response matching, the error-object contract,
timeout behavior, version negotiation and per-adapter compatibility gating, and the
authentication-capability-advertisement contract. It gives one valid and one failure
example, both drawn from this repository's own scripted-subprocess tests.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `session/new` / `session/prompt` / `session/update` payload contract | `launchpad-26/buzz#973` (unmerged at time of writing) |
| Session lifecycle — creation, config/model selection, mid-turn steering | `launchpad-26/buzz#975` (unmerged at time of writing) |
| Tool-call / permission-request contract | `launchpad-26/buzz#976` (unmerged at time of writing) |
| Full parameter-by-parameter API-reference-depth catalogue | `#1346`/`#1532` (undecided, per `templates/interface.md`'s own boundary) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **The upstream ACP specification document at
  `https://agentclientprotocol.com/` was not fetched or read directly.** This node
  cites this repository's own implementation (`crates/buzz-acp/src/acp.rs`) and its
  `README.md` instead, per `templates/interface.md`'s own guidance to prefer the
  concrete implementing code over restating an externally owned protocol's spec
  from memory.
- **Whether goose, `codex-acp` and `claude-agent-acp` each actually honor every
  contract point above was not verified by running each adapter live.** Only the
  harness-side code and its scripted-subprocess unit tests (which stand in for a
  real adapter with a bash script) were inspected; a real adapter's own conformance
  to the ACP spec is outside this node's evidence.
- **Whether "one request in flight at a time" holds across concurrent higher-level
  calls (e.g. `pool.rs` juggling several sessions on one `AcpClient`) was not traced
  end-to-end.** This node's ordering claims are about one `AcpClient`'s own
  request/response bookkeeping, not about every caller's concurrency discipline
  above it.
