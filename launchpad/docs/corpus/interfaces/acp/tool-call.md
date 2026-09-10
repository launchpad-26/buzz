---
id: interfaces-acp-tool-call
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
  - statement: "acp.rs's own module doc comment states that buzz-acp manages agent-subprocess communication 'over stdio using JSON-RPC 2.0 (newline-delimited / NDJSON)', and its lifecycle list names buzz-acp as the initiator of `initialize`, `session/new` and `session/prompt` -- i.e. buzz-acp is the ACP client and the spawned agent process (goose, codex-acp, claude-agent-acp, buzz-agent) is the ACP server for this connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
  - statement: "buzz-acp's README names the ACP spec at https://agentclientprotocol.com/ as the protocol every supported agent (goose, codex via codex-acp, claude code via claude-agent-acp) implements over stdio, and states the harness's minimum requirements for any ACP agent: accept `initialize`, accept `session/new` with `mcpServers`, accept `session/prompt` and stream `session/update` notifications, and return a `stopReason`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:12"
      - "crates/buzz-acp/README.md:325-330"
  - statement: "A tool call is reported to buzz-acp as a `session/update` notification whose `params.update.sessionUpdate` is `\"tool_call\"` (the initial report) or `\"tool_call_update\"` (a status change on an already-reported call, keyed by `toolCallId`); both are handled as match arms inside `handle_session_update`, which reads `title`/`kind` off `tool_call` and `toolCallId`/`status` off `tool_call_update` and otherwise only logs them -- neither arm executes anything on buzz-acp's side."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1748"
      - "crates/buzz-acp/src/acp.rs:1762-1782"
  - statement: "The Agent Client Protocol's own tool-calls page (fetched directly, not paraphrased from memory) defines a `ToolCall`'s fields as `toolCallId`, `title`, `kind` (one of read/edit/delete/move/search/execute/think/fetch/other), `status`, `content`, `rawInput`/`rawOutput` and `locations`; states status progresses through pending/in_progress/completed/failed; and states that a `ToolCallUpdate` may omit any field except `toolCallId`, since 'all fields except toolCallId are optional in updates'."
    entry_class: FACT
    evidence:
      - "https://agentclientprotocol.com/protocol/tool-calls"
  - statement: "acp.rs treats `kind` as an opaque string it only logs (`unwrap_or(\"unknown\")`), never matching against the spec's closed `kind` enum, and reads only two of the `ToolCall`/`ToolCallUpdate` fields the spec defines (`title`+`kind` on the initial report, `toolCallId`+`status` on the update) -- `content`, `rawInput`, `rawOutput` and `locations` are never read by this code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1762-1782"
  - statement: "A live-process test proves a `tool_call` session/update notification resets buzz-acp's idle timer: the test script emits one `tool_call` update, sleeps 80ms (under the configured 200ms idle timeout), then goes silent, and the test asserts the eventual idle timeout fires more than 200ms after the tool_call arrived -- i.e. strictly later than it would if the tool_call had not reset the timer."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3419-3452"
  - statement: "Before or during a tool call, the agent may send a `session/request_permission` JSON-RPC *request* (not a notification -- it carries an `id` and expects a reply); buzz-acp's `handle_permission_request` stores the pending request id, searches `params.options` for the entry whose `kind` field equals `\"allow_once\"` and replies selecting that option's `optionId`, falling back to the first `\"reject_once\"` entry if no `allow_once` entry exists, and returns `AcpError::Protocol` (propagated up through `?`, terminating the read loop with an error) if neither kind is present."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1934-1990"
  - statement: "The ACP spec's schema (fetched directly) defines `session/request_permission`'s request as carrying `sessionId`, `toolCall` and `options` (each option an `optionId`, a `name`, and a `kind` drawn from the closed enum `allow_once`, `allow_always`, `reject_once`, `reject_always`), and its response `outcome` as either `selected` (carrying the chosen `optionId`) or `cancelled`."
    entry_class: FACT
    evidence:
      - "https://agentclientprotocol.com/protocol/schema"
  - statement: "buzz-acp's permission-selection code only ever searches for the `kind` values `allow_once` and `reject_once` -- `allow_always` and `reject_always`, two of the spec's four defined kinds, never appear anywhere in acp.rs's search predicates -- so a permission is never granted or denied beyond the single tool call that requested it, even when the agent offers a standing option."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1957-1985"
  - statement: "This is a deliberate design choice to keep every permission grant single-use rather than an oversight, reasoned from the code's own emphasis ('**Critical:** Never hardcode `optionId` -- always find it dynamically by `kind`') on doing the *allow_once* lookup correctly, with no equivalent code path for the *_always* kinds anywhere in the crate; no commit message or comment states the reason directly, so this is inference rather than an opened statement of intent."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:1925-1934"
    confidence: 0.6
  - statement: "The response write and the `permission_responded` flag are deliberately ordered response-first: the code comment states the flag is set 'AFTER a successful write' because the previous flag-before-write ordering could leave `permission_responded=true` after a failed write, causing `cancel_with_cleanup` to skip sending a cancelled outcome and deadlock the agent waiting for a reply that never arrives."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1991-2007"
  - statement: "When a turn is cancelled (`cancel_with_cleanup_until`) while a `session/request_permission` request is still pending and unanswered, buzz-acp sends that pending request an `outcome: \"cancelled\"` response before sending `session/cancel`, so the agent is never left waiting on a permission reply that only a completed or cancelled turn would otherwise resolve."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1014-1040"
  - statement: "buzz-acp's `initialize()` always requests `protocolVersion: 2` (with a comment marking it 'an intentional temporary pin ... ahead of the upstream ACP RFD'), but the returned `protocolVersion` in the response is read only for logging/telemetry (`unwrap_or(1)` if absent) and is never compared against 2 or used to reject the connection -- there is no code path in this crate that fails or refuses to proceed based on a mismatched negotiated version."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:611-622"
      - "crates/buzz-acp/src/lib.rs:4703"
      - "crates/buzz-acp/src/lib.rs:4795"
  - statement: "The ACP spec (fetched directly) defines `protocolVersion` negotiation as: the client's `InitializeRequest.protocolVersion` is 'the latest protocol version supported by the client', and the agent's `InitializeResponse.protocolVersion` is 'the protocol version the client specified if supported by the agent, or the latest protocol version supported by the agent' -- i.e. the spec itself allows the agent to return a version other than the one requested, without that alone being a protocol violation."
    entry_class: FACT
    evidence:
      - "https://agentclientprotocol.com/protocol/schema"
  - statement: "buzz-acp's `build_client_capabilities()` advertises exactly two capability groups -- `auth.terminal: true` and a `_meta` object with goose's `customNotifications` flag and claude-agent-acp's `terminal-auth` flag -- and declares no `fs` or `terminal` client capability of the kind the ACP spec defines for a client that can read/write files or run commands on the agent's behalf."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:393-413"
  - statement: "Because no `fs`/`terminal` client capability is advertised, buzz-acp never executes a tool call itself -- every tool invocation this node describes is performed by the agent process and only *reported* to buzz-acp via `session/update`; buzz-acp's role is exclusively to observe that reporting and to answer `session/request_permission`."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:393-413"
      - "crates/buzz-acp/src/acp.rs:1762-1782"
    confidence: 0.85
  - statement: "Unit tests directly exercise the allow_once-by-kind and reject_once-fallback behavior: `find_allow_once_by_kind_not_by_option_id` asserts the search matches on `kind` even when a differently-ordered/named option list is given; `find_allow_once_returns_none_when_absent` asserts no match when only `reject_once` options exist; `find_reject_once_fallback_when_no_allow_once` asserts the fallback selects the `reject_once` option's own `optionId` rather than a hardcoded string."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:2400-2455"
  - statement: "Unit tests `permission_request_with_string_id` and `permission_cancelled_response_preserves_id_type` assert that a permission response echoes back the exact JSON-RPC `id` type (string or numeric) the agent's request used, per JSON-RPC 2.0's allowance of either -- a mismatched id type would leave the agent's own response-matching logic unable to correlate the reply."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:2659-2670"
      - "crates/buzz-acp/src/acp.rs:2688-2700"
  - statement: "buzz-dev-mcp (the shell/file-edit tool server the agent may separately call once a turn is underway) implements the Model Context Protocol via the `rmcp` crate dependency and imports `rmcp::{tool, tool_handler, tool_router, transport::stdio, ServerHandler, ...}` directly -- MCP is a distinct externally-specified protocol from ACP, with its own tool-call wire format that this node does not describe."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml:26"
      - "crates/buzz-dev-mcp/src/lib.rs:1-10"
  - statement: "`node.schema.json`'s `type` enum has thirteen members and no bare `interface` value; the combined surface for interface- and event-kind-shaped nodes is the single value `interfaces-events`, which this node carries."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "`launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`, merged and `status: active` on `origin/launchpad`) prescribes this node's required sections -- Interface description, Operations, Contract and stability, Boundary, Relationships, Scope and omissions -- and states a node built from it 'may declare `implements` toward this template node itself ... if the author wants the generated `implemented-by` edge'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "Issues #973-975 (the sibling protocol/message/session ACP interface nodes) are dispatched in parallel with this task and are not present in `origin/launchpad`'s corpus tree at the recorded revision, so none of their prospective ids is a valid `relationships[].target` today."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#976 dispatch instructions"
  - statement: "Issue #976's Definition of Done requires this node to define inputs/messages, outputs/responses and error/rejection behavior; authentication/authorization, versioning/compatibility and ordering/idempotency where applicable; a link to the authoritative machine/spec representation; and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#976 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# ACP tool-call reporting: interface

This node documents one boundary inside the Agent Client Protocol (ACP) connection
between `buzz-acp` (the ACP **client**) and the agent subprocess it spawns --
goose, codex (via `codex-acp`), Claude Code (via `claude-agent-acp`), or
`buzz-agent` itself (the ACP **server** for that connection). The boundary is
narrow: how the agent *reports* that it is invoking a tool, and how `buzz-acp`
*gates* that invocation when the agent asks for permission first. The wire
format is JSON-RPC 2.0 over newline-delimited stdio (NDJSON), the same
transport every ACP method in this connection uses. `buzz-acp` advertises no
`fs` or `terminal` client capability, so it never executes a tool call itself
-- every tool this node describes is run by the agent process; `buzz-acp`
only observes the report and answers the permission question when one is
asked.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `session/update` (`sessionUpdate: "tool_call"`) | `crates/buzz-acp/src/acp.rs:1762-1773` (`handle_session_update`); [ACP tool-calls spec](https://agentclientprotocol.com/protocol/tool-calls) | Notification (no reply expected) the agent sends when it begins a tool invocation. Carries `toolCallId`, `title`, `kind`, `status`, `content`, `rawInput`, `locations` per the spec; `buzz-acp` reads only `title` and `kind`, logs them, and resets the connection's idle timer. |
| `session/update` (`sessionUpdate: "tool_call_update"`) | `crates/buzz-acp/src/acp.rs:1774-1782`; [ACP tool-calls spec](https://agentclientprotocol.com/protocol/tool-calls) | Notification reporting a status change on an already-reported `toolCallId` (all fields but `toolCallId` optional, per spec). `buzz-acp` reads `toolCallId` and `status` and logs them; it does not reset the idle timer (only the initial `tool_call` does). |
| `session/request_permission` | `crates/buzz-acp/src/acp.rs:1934-2007` (`handle_permission_request`); [ACP schema](https://agentclientprotocol.com/protocol/schema) | JSON-RPC request (carries an `id`; a reply is required) the agent sends before or during a tool call that needs authorization. `buzz-acp` auto-approves: it finds the `options` entry whose `kind` is `allow_once` and replies `outcome: {outcome: "selected", optionId}`; if none exists it falls back to a `reject_once` entry; if neither exists it returns a protocol error instead of replying. |

## Contract and stability

**Selection is always single-use.** `buzz-acp` only ever searches
`options` for `kind == "allow_once"` or, failing that, `kind ==
"reject_once"` (`acp.rs:1957-1985`) -- the spec's other two kinds,
`allow_always` and `reject_always`, are never matched anywhere in this
crate. A caller cannot rely on `buzz-acp` ever granting a standing
permission across multiple tool calls, even when the agent offers one.

**A response is written before the pending-request state is cleared, never
after.** `acp.rs:1991-2007`'s comment states the ordering explicitly: an
earlier flag-before-write ordering risked a deadlock if the write itself
failed (e.g. `AcpError::WriteTimeout`) after the flag had already been set,
which would make `cancel_with_cleanup` skip sending a cancellation the
agent was still waiting on. The current ordering accepts a narrow
double-response window instead, bounded by one memory store, over an
unbounded deadlock.

**A cancelled turn always resolves a still-pending permission request.**
`cancel_with_cleanup_until` (`acp.rs:1014-1040`) checks for a pending,
unanswered `session/request_permission` before sending `session/cancel`,
and if one exists, answers it with `outcome: "cancelled"` first. The agent
is never left holding a permission request across a turn boundary.

**No suitable option is a hard error, not a silent default.** If
`handle_permission_request` finds neither `allow_once` nor `reject_once`
in `options`, it returns `AcpError::Protocol(...)`. That error propagates
through the caller's `?` in the read loop (`read_until_response` /
its idle-aware counterpart), ending the loop with an error rather than
guessing an option or leaving the agent's request unanswered.

**JSON-RPC id type is preserved exactly.** Permission responses echo back
the request's `id` value with its original JSON type (string or numeric),
per JSON-RPC 2.0's allowance of either (`acp.rs:2659-2700`); comparison
elsewhere in the read loop is by `serde_json::Value` equality, so a
numeric `id` never matches a string of the same digits.

**Protocol-version negotiation is logged, not enforced.** `buzz-acp`
requests `protocolVersion: 2` on every `initialize` call (a stated
temporary pin ahead of the upstream ACP RFD), but the version the agent
actually returns is read only for logging and telemetry
(`crates/buzz-acp/src/lib.rs:4703`, `:4795`) and defaults to `1` if
absent. Nothing in this crate rejects a connection over a mismatched
negotiated version -- which matches the spec's own definition of
negotiation: the agent may return the client's version "if supported ...
or the latest protocol version supported by the agent."

### Valid example

`tool_call_resets_idle_then_silence_times_out`
(`crates/buzz-acp/src/acp.rs:3419-3452`) drives a real subprocess that
emits one `session/update` `tool_call` notification, sleeps 80ms (under
the test's 200ms idle timeout), then falls silent. The test asserts the
resulting `AcpError::IdleTimeout` fires measurably later than 200ms after
the `tool_call` arrived, proving the notification reset the idle clock
rather than being ignored.

### Failure example

When an agent's `session/request_permission` request carries an `options`
array with neither an `allow_once` nor a `reject_once` entry (for
example, only `allow_always`/`reject_always` options),
`handle_permission_request` returns `AcpError::Protocol("no suitable
permission option found (neither allow_once nor reject_once)")`
(`acp.rs:1985-1990`) instead of guessing or leaving the request
unanswered; the caller's `?` propagates this out of the read loop as a
hard error for that turn.

## Boundary

This node does not describe:
- **A single Nostr event kind's own wire contract.** Tool-call reporting
  is pure ACP JSON-RPC over stdio; no Nostr event participates in it, so
  there is no event-kind node this document could reference without
  citing a kind that plays no part in the flow.
- **A full parameter-by-parameter catalogue of every `ToolCall`/
  `ToolCallUpdate` field for domain-expert readers.** The spec already
  owns that (linked above); this node names the fields `buzz-acp` itself
  reads and cites the spec for the rest rather than re-encoding it.
- **The ACP session-lifecycle methods `session/new`, `session/prompt` and
  `session/cancel`.** Those are `interfaces/acp/session.md` and
  `interfaces/acp/message.md`'s subject (issues #974 and #975, dispatched
  in parallel with this task and not yet merged) -- named here by
  filename rather than by relationship edge, since neither node's id
  resolves against `origin/launchpad` yet.
- **The MCP tool-call protocol `buzz-dev-mcp` implements** for the
  shell/file-edit tools an agent may separately invoke once a turn is
  underway. MCP is a distinct externally-specified protocol (the `rmcp`
  crate) from ACP's own tool-call reporting; a corpus node for it, if one
  is ever written, is not this one.
- **Any per-agent-adapter quirk** beyond what is already grounded above.
  `codex-acp`, `claude-agent-acp` and goose all speak the same
  `session/update`/`session/request_permission` shapes this node
  describes; adapter-specific deviations, if any exist, are out of scope
  here.

## Relationships

- **implements**: `corpus-template-interface` -- this node is drafted from
  that template's *Required sections* and *Template skeleton*.
- No `references` edges are declared. The sibling ACP interface nodes
  (`interfaces/acp/protocol.md`, `interfaces/acp/session.md`,
  `interfaces/acp/message.md` -- issues #973-975) are dispatched in
  parallel and are not present in `origin/launchpad`'s corpus tree at the
  recorded revision, so none of their ids is a valid
  `relationships[].target` yet. No event-kind node is referenced, for the
  reason given under *Boundary*.

## Scope and omissions

**This node covers** the `session/update` `tool_call`/`tool_call_update`
notifications and the `session/request_permission` request/response pair,
as `buzz-acp` (the ACP client) implements and observes them: which fields
it reads, what it guarantees about response ordering, cancellation, id
preservation and version negotiation, and one valid plus one failure
example grounded in this crate's own tests.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ACP session lifecycle (`session/new`, `session/prompt`, `session/cancel`) | `interfaces/acp/session.md` / `interfaces/acp/message.md` (issues #974/#975, unmerged) |
| The ACP protocol's own initialize/capability-negotiation handshake as a whole | `interfaces/acp/protocol.md` (issue #973, unmerged) |
| The MCP tool-call protocol `buzz-dev-mcp` implements | Not yet a corpus node |
| Field-by-field cataloguing of every `ToolCall`/`ToolCallUpdate` field the ACP spec defines | The ACP spec itself, linked above |
| The corpus front-matter contract and node creation/update/retirement procedure | `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **The ACP JSON Schema document itself was not downloaded and diffed
  field-by-field against `acp.rs`.** Two scoped queries against
  `agentclientprotocol.com`'s tool-calls and schema pages were fetched and
  read directly; a full schema document was not retrieved, so a field
  this node does not mention may exist in the spec without this node
  having checked for it.
- **Whether any of goose, codex-acp or claude-agent-acp diverges from the
  `tool_call`/`tool_call_update`/`session/request_permission` shapes
  described here was not independently tested against a live instance of
  each adapter** -- the evidence above is grounded in `buzz-acp`'s own
  handling code and its unit/integration tests, not in a recorded wire
  capture from each of the three adapters.
- **Why `buzz-acp` restricts itself to single-use permission kinds
  (`allow_once`/`reject_once`) and never the spec's `_always` variants**
  is recorded here as an inference from the code's shape, not from a
  comment, commit message, or issue stating the reason directly.
