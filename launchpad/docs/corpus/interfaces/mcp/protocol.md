---
id: interfaces-mcp-protocol
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
  - statement: "buzz-dev-mcp is the MCP server side of this interface: it builds a rmcp #[tool_router]/#[tool_handler] server (struct DevMcp), serves it over rmcp's transport::stdio(), and its ServerHandler::get_info() advertises capabilities via ServerCapabilities::builder().enable_tools().build() (tools only — no resources or prompts capability) plus an Implementation identity of Implementation::new(\"buzz-dev-mcp\", env!(\"CARGO_PKG_VERSION\"))."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:3-9"
      - "crates/buzz-dev-mcp/src/lib.rs:23-37"
      - "crates/buzz-dev-mcp/src/lib.rs:126-136"
  - statement: "The server's run()/async_main() startup sequence is: dispatch on argv0 (multicall) for sync personalities before building any async runtime; for MCP-server mode, install a rustls crypto provider, initialize tracing to stderr only, install the Shim (session PATH + git config), construct SharedState, then DevMcp::new(state).serve(stdio()).await? followed by service.waiting().await? to block for the session's lifetime."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:138-186"
  - statement: "buzz-agent's mcp.rs is the MCP client side of this interface: it spawns each configured MCP server as a subprocess via rmcp's transport::TokioChildProcess, drives the session with ().serve(transport) under an init_timeout, then calls client.peer().list_all_tools() (also timeout-bounded) to populate the session's tool set."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:1-14"
      - "crates/buzz-agent/src/mcp.rs:730-805"
  - statement: "Before spawning, the client calls Command::env_clear() and repopulates the child's environment only from an explicit PASSTHROUGH_ENV allowlist (PATH, HOME, TERM, LANG/LC_ALL, TMPDIR, XDG_CONFIG_HOME, SSH agent vars, git helper/config overrides, proxy vars in both cases, TLS trust vars, and the Buzz identity vars NOSTR_PRIVATE_KEY/BUZZ_PRIVATE_KEY/BUZZ_RELAY_URL/BUZZ_AUTH_TAG/BUZZ_ACP_DISPLAY_NAME), plus each server's own declared env entries — the child process never inherits the parent's full environment by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:39-94"
      - "crates/buzz-agent/src/mcp.rs:736-750"
  - statement: "Despite NOSTR_PRIVATE_KEY surviving the client-side passthrough allowlist, buzz-dev-mcp's own Shim::install() reads and unconditionally removes NOSTR_PRIVATE_KEY from its process env immediately on startup, writing it to a 0600 keyfile instead and zeroizing the in-memory copy — so the raw key is present in the server process for only that installation step and is never visible to the shell tool's own child processes, which read the keyfile via ephemeral GIT_CONFIG_* env vars instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs:6-17"
      - "crates/buzz-dev-mcp/src/shim.rs:51-68"
      - "crates/buzz-dev-mcp/src/shell.rs:170"
  - statement: "The interface carries no MCP-level authentication or authorization handshake of its own — the MCP specification's initialize exchange (protocolVersion, capabilities, clientInfo/serverInfo) has no auth fields, and this repository does not add any. Trust is established entirely at the process-spawn boundary described in the two evidence entries above: which environment variables (and therefore which credentials) a spawned MCP server subprocess can see at all."
    entry_class: INFERENCE
    evidence:
      - "https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle"
      - "crates/buzz-agent/src/mcp.rs:39-94"
    confidence: 0.85
  - statement: "The root workspace Cargo.toml pins rmcp to \"1.1.0\" with features server, transport-io and macros; Cargo.lock resolves the dependency to 1.8.0 at this revision. Both buzz-dev-mcp (server) and buzz-agent (client) depend on this single rmcp version via the workspace, so the two sides of the transport cannot independently drift to incompatible rmcp releases within this repository."
    entry_class: FACT
    evidence:
      - "Cargo.toml:136"
      - "Cargo.lock:7946-7948"
      - "crates/buzz-dev-mcp/Cargo.toml"
  - statement: "Protocol-version negotiation itself (the initialize request/response protocolVersion exchange) is not hand-rolled anywhere in buzz-dev-mcp or buzz-agent; both sides construct their session through rmcp's own ServiceExt::serve()/service framework rather than composing the initialize handshake by hand, so version compatibility is delegated to whatever protocolVersion(s) the pinned rmcp release implements."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:183"
      - "crates/buzz-agent/src/mcp.rs:779"
    confidence: 0.75
  - statement: "The official MCP specification's stdio transport page states messages are individual newline-delimited JSON-RPC requests/notifications/responses that MUST NOT contain embedded newlines, that the server MAY write UTF-8 logging to stderr, and that the server MUST NOT write anything to stdout that is not a valid MCP message — matching this repository's own tracing_subscriber::fmt().with_writer(std::io::stderr) initialization, which keeps stdout reserved for the rmcp transport."
    entry_class: FACT
    evidence:
      - "https://modelcontextprotocol.io/specification/2025-06-18/basic/transports"
      - "crates/buzz-dev-mcp/src/lib.rs:174-177"
  - statement: "The specification's lifecycle page states the client MUST initiate the session with an initialize request carrying its supported protocolVersion, that the server MUST respond with the same version if supported or another version it supports otherwise, and that the client SHOULD disconnect if it does not support the server's returned version — this is the compatibility mechanism the interface relies on, not a Buzz-specific versioning scheme layered on top."
    entry_class: FACT
    evidence:
      - "https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle"
  - statement: "A tool call is made by qualifying each discovered tool's bare name as \"<server-name>__<bare-name>\" (SEP = \"__\"), rejecting any bare or server name containing \"__\" or exceeding length caps, capping tool count at MAX_TOOLS_PER_SESSION (128), qualified-name length at MAX_QNAME_LEN (64), and each tool's description/input-schema at MAX_DESCRIPTION_BYTES (1024) / MAX_SCHEMA_BYTES (4096 — oversize schemas are replaced with an empty object rather than rejected outright)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:19-27"
      - "crates/buzz-agent/src/mcp.rs:261-291"
      - "crates/buzz-agent/src/mcp.rs:878-887"
  - statement: "Before a call reaches the transport, arguments are validated to be either a JSON object or absent (null) — any other JSON shape (array, string, number, bool) is rejected locally with an AgentError::Mcp before any request is sent, because the transport can only carry an object or no arguments at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:807-828"
  - statement: "A tool call is issued as a ClientRequest::CallToolRequest carrying CallToolRequestParams{name, arguments} via client.peer().send_cancellable_request(...), and the response is read by polling the returned request handle's inner channel directly (rather than the blocking await_response helper) specifically so the call site can still own the handle and fire a cancellation on the other branch of a tokio::select!."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:596-630"
  - statement: "The client distinguishes two error classes on a tool call's response. A transport-level error (ServiceError::TransportSend, TransportClosed, Timeout, or UnexpectedResponse) is treated as the server itself being unhealthy: the client kills the server's process group, marks it Dead with a backoff-scheduled next_retry, and returns an AgentError to the caller. An application-level JSON-RPC error (for example code -32602, invalid params) is treated as the server correctly and healthily rejecting bad input: no process is killed, and the call instead returns a normal ToolResult with is_error: true and text \"Tool call rejected: {e}\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:632-658"
      - "crates/buzz-agent/src/mcp.rs:845-856"
  - statement: "A dead server is retried with exponential backoff (base/max durations from Config, doubled per attempt up to a shift cap, plus +/-20% jitter) up to mcp_max_restart_attempts; once exhausted the server is permanently dead for the session (next_retry pushed 24 hours out) and every qualified tool name routed to it becomes unavailable to the caller with an explicit \"exhausted\" error rather than silently disappearing."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:162-182"
      - "crates/buzz-agent/src/mcp.rs:668-727"
      - "crates/buzz-agent/src/mcp.rs:858-871"
  - statement: "Cancelling an in-flight call sends a best-effort notifications/cancelled message to the server (fire_and_forget_cancel, spawned rather than awaited) and immediately returns AgentError::Cancelled to the caller without waiting for the server's acknowledgement — matching the specification's own cancellation page, which calls this notification 'fire and forget' and states receivers MAY ignore it if the referenced request is unknown, already completed, or cannot be cancelled."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:611-624"
      - "crates/buzz-agent/src/mcp.rs:830-843"
      - "https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/cancellation"
  - statement: "A tool's CallToolResult content blocks are reassembled under two byte budgets (total and text-only): text is middle-elided (head and tail preserved, an elision marker inserted) rather than head- or tail-truncated, images pass through whole or are elided as a single marker if they would exceed the remaining budget, and audio/resource/resource-link content blocks are always collapsed to a short text placeholder rather than passed through structurally — so a caller cannot assume every content type MCP defines survives this client's result assembly unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:953-1035"
  - statement: "This repository imposes a hard cap of 16 configured MCP servers per session (MAX_MCP_SERVERS) and rejects a duplicate server name outright, both enforced before any subprocess for that batch is spawned."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:26"
      - "crates/buzz-agent/src/mcp.rs:207-235"
  - statement: "buzz-dev-mcp is one of the tool surfaces the architecture-containers-agent-runtime corpus node already documents as part of the agent-runtime container, describing it there as 'a developer MCP server exposing shell, file-edit and Buzz-CLI-backed tools to an agent process over MCP' reached over stdio via rmcp's transport-child-process."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "No corpus node for the individual buzz-dev-mcp tools (file-edit tools, the shell tool) is merged on origin/launchpad as of the recorded revision, so this node cannot yet declare a references or supersedes relationship toward them; those tool-specific nodes are tracked separately as issues #987 (file-edit tools) and #989 (shell tool)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#988 issue body (parallel sibling tasks #987/#989)"
relationships:
  - type: implements
    target: corpus-template-interface
  - type: part-of
    target: architecture-containers-agent-runtime
---

# MCP protocol: interface

This node documents the overall Model Context Protocol (MCP) transport and session
contract as `buzz-dev-mcp` (server) and `buzz-agent` (client) implement it in this
repository — the boundary itself: how a session is established, how a tool call travels
across it, how errors and cancellation are signaled, and what a caller may rely on
staying true across a call. It does **not** document any individual tool's own
input/output contract (`shell`, `read_file`, `str_replace`, `view_image`, `todo`,
`_Stop`, `_PostCompact`) — those are `#989` and `#987`'s subject matter, tracked
separately per the *Boundary* section below.

## Interface description

Two Rust binaries in this repository exchange calls across an externally specified
protocol, MCP, rather than a Buzz-invented wire format. `buzz-dev-mcp` is the MCP
**server**: a `rmcp`-based `#[tool_router]`/`#[tool_handler]` service (`DevMcp`) served
over `rmcp`'s stdio transport, spawned as a subprocess per agent session.
`buzz-agent` is the MCP **client**: it spawns that subprocess via `rmcp`'s
`TokioChildProcess` transport, drives the session lifecycle, and issues tool calls on
the agent's behalf. Both sides are mediated entirely by the `rmcp` crate (the Rust MCP
SDK) rather than by a hand-rolled JSON-RPC implementation — contrast `buzz-acp`, whose
own ACP wire format *is* hand-rolled JSON-RPC 2.0 over stdio in this repository's code.
Everything this interface carries — the message framing, the `initialize` handshake,
tool discovery, tool invocation, cancellation — is therefore governed by the pinned
`rmcp` version plus the MCP specification it implements, not by a Buzz-specific
protocol document.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Session establishment (`initialize`/`initialized`) | `rmcp`'s `ServiceExt::serve()` on both sides — server: `crates/buzz-dev-mcp/src/lib.rs:183`; client: `crates/buzz-agent/src/mcp.rs:779` | Client spawns the server subprocess and negotiates `protocolVersion` + capabilities before any other request may be sent, per the MCP specification's lifecycle. |
| Capability advertisement | `crates/buzz-dev-mcp/src/lib.rs:126-136` (`ServerHandler::get_info`) | Server advertises `tools` only (`enable_tools()`), plus its `Implementation` identity and `bootstrap_instructions` text returned as the session's `instructions`. |
| Tool discovery (`tools/list`) | `crates/buzz-agent/src/mcp.rs:789` (`client.peer().list_all_tools()`) | Client enumerates the server's tool set once per (re)spawn; results become the qualified `server__tool` names available for the session. |
| Tool invocation (`tools/call`) | `crates/buzz-agent/src/mcp.rs:596-630` (`CallToolRequestParams` via `send_cancellable_request`) | Client sends a qualified tool's bare name plus a JSON-object-or-null argument payload; server dispatches to the matching `#[tool]`-annotated method in `DevMcp`. |
| Cancellation (`notifications/cancelled`) | `crates/buzz-agent/src/mcp.rs:830-843` | Client-initiated, best-effort, fire-and-forget per the MCP specification's cancellation page; the client does not wait for acknowledgement. |
| Restart/backoff on transport failure | `crates/buzz-agent/src/mcp.rs:668-727` | Not an MCP-defined operation — a `buzz-agent`-side resilience mechanism layered on top of the transport, described under *Contract and stability*. |

## Contract and stability

**Transport.** stdio only, per the MCP specification's stdio transport section:
newline-delimited JSON-RPC on stdin/stdout, stdout reserved exclusively for protocol
messages, stderr free for logging (`buzz-dev-mcp` initializes `tracing_subscriber` with
`with_writer(std::io::stderr)` specifically to honor this). No HTTP/SSE transport is
implemented or configured for this interface anywhere in this repository.

**Versioning/compatibility.** Both sides depend on one workspace-pinned `rmcp` version
(`Cargo.toml:136` pins `"1.1.0"`; `Cargo.lock` resolves `1.8.0`), so they cannot
independently drift to incompatible `rmcp` releases within this repository. Neither
side hand-rolls the `initialize` handshake or its `protocolVersion` negotiation — both
construct their session through `rmcp`'s own `ServiceExt::serve()`, so protocol-version
compatibility is delegated to whatever version(s) the pinned `rmcp` release implements,
not asserted by Buzz-specific code. The exact `protocolVersion` string the pinned
`rmcp` negotiates was not independently confirmed against `rmcp`'s own source for this
node (see *Scope and omissions*).

**Error/rejection behavior.** Two classes, handled differently by the client:
- *Transport-fatal* (`ServiceError::TransportSend`, `TransportClosed`, `Timeout`,
  `UnexpectedResponse`): the server subprocess is presumed unhealthy. Its process
  group is killed, it is marked `Dead` with an exponentially-backed-off `next_retry`
  (base/max/jitter), and the call returns an error to the caller. After
  `mcp_max_restart_attempts` failed restarts the server is permanently dead for the
  rest of the session.
- *Application-level JSON-RPC error* (for example `-32602` invalid params): the server
  is healthy and correctly rejected malformed input. No process is killed; the call
  returns a normal tool result with `is_error: true` and text `"Tool call rejected:
  {e}"`.

Before either class is reached, a call whose arguments are not a JSON object or `null`
is rejected locally — never sent to the transport at all.

**Ordering/idempotency.** The interface itself defines no cross-call ordering or
idempotency guarantee — a request/response pair correlates by JSON-RPC request id, and
concurrent calls to different tools (or the same tool) are independent requests. Where
this repository builds ordering on top, it is `buzz-agent`-side, not MCP-level: parallel
hook-tool fan-out (`_Stop`/`_PostCompact`-shaped calls across multiple configured
servers) is explicitly re-sorted into deterministic **registration order** before being
returned to the caller, specifically so the result does not depend on `HashMap`
iteration or task-completion order.

**Cancellation.** Best-effort and non-blocking on both the specification's terms and
this repository's implementation: the client fires `notifications/cancelled` and
returns control to its own caller immediately, without waiting for the server's
acknowledgement — matching the specification's statement that receivers "MAY ignore"
a cancellation notification for a request that is unknown, already completed, or
cannot be cancelled.

**Content assembly.** A `CallToolResult`'s content blocks are not guaranteed to survive
a round trip through `buzz-agent`'s client unchanged in *shape*, even though nothing is
silently dropped: text is middle-elided under a byte budget with an inline elision
marker (head and tail preserved, since tool output tends to put its conclusion at the
end), images pass through whole or are replaced by a text marker if oversize, and
audio/resource/resource-link blocks are always collapsed to a short text placeholder.

**Environment/trust boundary (not authentication).** The protocol carries no
authentication or authorization fields of its own — neither the MCP specification's
`initialize` exchange nor this repository's use of it defines one. Trust is instead
established entirely by which environment variables a spawned server subprocess can
see: the client calls `env_clear()` and repopulates only an explicit allowlist
(`PASSTHROUGH_ENV`) plus each server's own declared `env` entries, so a spawned MCP
server does not inherit the launching process's full environment by default. Within
that boundary, `buzz-dev-mcp` narrows further on its own: `NOSTR_PRIVATE_KEY` (present
in the allowlist, so the server process does receive it) is read once, written to a
0600 keyfile, and unconditionally stripped from the server's own process environment
before any shell child is ever spawned — the raw key is never visible past that one
installation step, even though the interface itself neither requires nor knows about
this handling.

## Boundary

This node does not describe:
- **Any individual tool's own input/output contract** — `shell`'s parameters and
  ephemeral-process semantics, `read_file`'s offset/limit windowing, `str_replace`'s
  atomic single/`replace_all` matching, `view_image`'s resize/transcode/auth-header
  behavior, or `todo`/`_Stop`/`_PostCompact`'s session-checklist semantics. Those are
  `#989` (shell tool) and `#987` (file-edit and other tools)'s subject matter — see
  *Relationships* below for why no `references` edge to them exists yet.
- **A field-by-field, parameter-by-parameter catalogue** of every tool's JSON schema
  for domain-expert readers — this node names schema-size *caps* the interface
  enforces (`MAX_DESCRIPTION_BYTES`, `MAX_SCHEMA_BYTES`), not each schema's own field
  list.
- **The front-matter contract or corpus authoring procedure** — `node.schema.json` and
  `AGENTS.md` govern those unconditionally for every node, this one included.
- **The Agent Client Protocol (ACP)** between `buzz-acp` and the agent subprocess —
  that is a separate, hand-rolled JSON-RPC 2.0 wire format documented (if at all) by a
  different corpus node; MCP and ACP are two distinct protocols this repository speaks
  on two different process boundaries.

## Examples

**Valid.** A `shell` tool call succeeds end to end: the client sends a
`CallToolRequest` naming `shell` with a JSON object of parameters (see
`crates/buzz-dev-mcp/src/shell.rs`'s `ShellParams`); the server executes it and returns
a `CallToolResult` whose content the client reassembles under its byte budgets; the
call returns a `ToolResult` with `is_error: false` (`crates/buzz-agent/src/mcp.rs:660-666`).

**Failure.** Two distinct failure shapes exist at this layer:
1. *Rejected before transport*: a caller passes a non-object, non-null `arguments`
   value (for example a bare string). `validate_arg_shape` returns an error and no
   request is ever sent to the server (`crates/buzz-agent/src/mcp.rs:817-828`).
2. *Rejected by the server, transport intact*: the server receives a well-formed
   request but rejects its parameters at the JSON-RPC level (for example `-32602`).
   The server process is left running; the caller receives `is_error: true` with text
   `"Tool call rejected: {e}"` rather than a killed connection
   (`crates/buzz-agent/src/mcp.rs:648-657`).

## Relationships

- **implements** `corpus-template-interface` — this node is an instance of the merged
  interface template, per that template's own stated preference for `implements` over
  `references` as the optional self-link (unsettled corpus-wide convention; see that
  template's own *Scope and omissions*).
- **part-of** `architecture-containers-agent-runtime` — the agent-runtime container
  node already names `buzz-dev-mcp`'s MCP tool surface as part of that container's
  technology and outbound-interface description; this node is the detailed interface
  documentation that container-level description points at.
- **No relationship declared toward #987 or #989's eventual nodes.** Neither is merged
  on `origin/launchpad` at the recorded revision, so neither has a valid node `id` to
  target — a `relationships[].target` naming an id no loaded node carries is a hard
  validation error. Once either merges, the natural edge is that tool-specific node
  declaring `references` back toward this one (the tool's contract depends on this
  session/transport contract), not this node declaring a forward edge to a subject it
  does not describe.

## Scope and omissions

**This node covers** the MCP session and transport contract shared by every tool
`buzz-dev-mcp` exposes: how a session is established and versioned, how a tool call is
named, shaped, sent, and its result reassembled, how transport failure differs from an
application-level rejection, how cancellation and restart/backoff behave, and the
process-environment trust boundary the protocol itself is silent on.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any individual tool's parameters, return shape or tool-specific semantics | `#989` (shell tool), `#987` (file-edit and other tools) |
| Field-by-field API-parameter cataloguing for domain experts | A future reference-depth node per `#1346`/`#1532`, if the corpus builds one |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| The Agent Client Protocol (`buzz-acp` <-> agent subprocess) | Not this node — a distinct protocol on a distinct process boundary |
| `buzz-workflow`'s hook-server allowlisting and hook-timeout kill policy beyond the generic restart/backoff mechanism described here | `crates/buzz-agent/src/mcp.rs`'s `call_hooks` (cited above only for its deterministic-ordering guarantee, not restated in full) |

**Expected but not verified when this node was written:**
- **The exact `protocolVersion` string the pinned `rmcp` 1.8.0 release negotiates** was
  not independently confirmed against `rmcp`'s own source or changelog — this node
  cites the specification's version-negotiation *rule* (client proposes, server
  confirms-or-counters) and this repository's delegation to `rmcp` for it, not a
  specific negotiated version string.
- **Whether every MCP capability `rmcp` 1.8.0 supports beyond `tools` (`resources`,
  `prompts`, `logging`, `completions`) is genuinely absent from `buzz-dev-mcp`, or
  merely unadvertised**, was checked only against `ServerCapabilities::builder()`'s
  call site (`enable_tools()` alone) — the underlying `rmcp` crate's own default
  capability surface was not independently audited.
- **Whether any deployment configures more than one simultaneous MCP server** (up to
  the `MAX_MCP_SERVERS` cap of 16) in practice, beyond `buzz-dev-mcp` being the
  conventional single choice per the agent-runtime container node, was not surveyed
  here.
