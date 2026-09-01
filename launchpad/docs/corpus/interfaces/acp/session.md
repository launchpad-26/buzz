---
id: interfaces-acp-session
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "acp.rs's own module doc comment states it 'manages communication with an AI agent subprocess over stdio using JSON-RPC 2.0 (newline-delimited / NDJSON)' and lists the session lifecycle as spawn -> initialize -> session_new -> session_prompt_with_idle_timeout -> session_cancel/cancel_with_cleanup."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
  - statement: "AcpClient::spawn launches the agent binary as a child process with piped stdin/stdout, applies per-persona and per-runtime environment defaults (operator-set env always wins), and on Unix puts the child in its own process group so a later SIGKILL doesn't propagate to the harness's own group."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:454-567"
  - statement: "AcpClient::initialize sends the ACP `initialize` request with a hardcoded `protocolVersion: 2` and a code comment stating this is 'an intentional temporary pin -- we are squatting on ACP v2 ahead of the upstream ACP RFD', to be revisited once that RFD merges; the response's `_meta.steering.supported` flag is parsed here once, not at each call site."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:126-135"
      - "crates/buzz-acp/src/acp.rs:611-622"
  - statement: "build_client_capabilities declares two client-side capabilities at initialize time: `auth.terminal: true` (Buzz can hand a user to a terminal-native auth flow) and `_meta.goose.customNotifications` / `_meta.terminal-auth` (adapter-specific extensions ignored by other adapters)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:393-414"
  - statement: "AcpClient::session_new_full sends `session/new` with `cwd` (must be absolute), `mcpServers`, an optional `systemPrompt` or `_meta.systemPrompt` transport, and an optional `_meta.sessionTitle`; it extracts `sessionId` from the JSON-RPC result as a plain string and returns it plus the raw result inside a SessionNewResponse. Callers use its `session_new` convenience wrapper when only the id is needed."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:632-703"
      - "crates/buzz-acp/src/acp.rs:2123-2130"
  - statement: "If the `session/new` JSON-RPC result has no string `sessionId` field, session_new_full returns Err(AcpError::Protocol(\"session/new response missing sessionId\")) rather than a partially-populated session -- there is no fallback or generated id on the client side."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:677-680"
  - statement: "A test (session_new_full_includes_system_prompt_when_some) exercises the full request/response round trip against a scripted subprocess and asserts the returned session_id equals the scripted `sessionId` value and that `systemPrompt` rode in the request params -- confirming the wire shape acp.rs's own comment claims."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3458-3491"
  - statement: "A session_id, once created, is opaque to buzz-acp: it is stored and re-sent as a plain string in every subsequent per-session request (`session/prompt`, `session/cancel`, `session/set_config_option`, `session/set_model`, the goose-specific system-prompt-set method) and is never parsed or validated for shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:706-749"
      - "crates/buzz-acp/src/acp.rs:849-854"
  - statement: "AcpError::AgentError{code, message} is built from any JSON-RPC error object returned for a session-scoped request; when the object's `message` field is missing or non-string, the full JSON object is used as the message instead so provider-specific detail (e.g. a `data` field) is not silently dropped."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:80-124"
  - statement: "cancel_with_cleanup_until's own precondition check returns Err(AcpError::Protocol(\"cancel_with_cleanup called with no in-flight prompt\")) before any side effect (no permission response, no cancel notification is written) when called against a session with no active turn -- a documented, code-enforced rejection distinct from an agent-side JSON-RPC error."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1014-1024"
  - statement: "session_cancel sends `session/cancel` as a JSON-RPC *notification* (no `id` field, no response expected); a unit test pins the exact wire shape -- method `session/cancel`, params `{sessionId}`, and asserts the message carries no `id` key."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:841-854"
      - "crates/buzz-acp/src/acp.rs:2643-2652"
  - statement: "cancel_with_cleanup (and its grace/deadline variants cancel_with_cleanup_grace / cancel_with_cleanup_until) first answer any pending session/request_permission with outcome 'cancelled' if one is outstanding and unanswered, then send session/cancel, then keep reading until the in-flight session/prompt response arrives carrying stopReason 'cancelled' -- returning that StopReason to the caller rather than leaving the turn's response unconsumed."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:945-1062"
  - statement: "AcpClient::shutdown kills the entire OS process group the agent subprocess was spawned into (falling back to killing only the direct child on non-Unix, or if the child was already reaped) and waits up to 5 seconds for it to exit; this is the only operation that terminates a session at the wire/process level -- Drop alone only issues a best-effort start_kill() without waiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:416-444"
  - statement: "No `session/end`, `session/delete` or `session/close` JSON-RPC method is ever constructed or sent anywhere in buzz-acp's ACP client or pool code."
    entry_class: FACT
    evidence:
      - "grep_repo('session/end|session/delete|session/close', path='crates/buzz-acp/src/', types='rs') -> zero matches, verified 2026-09-01 against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "Above the wire client, pool.rs's SessionState holds a channel_id -> session_id map (`sessions`), per-channel turn counters (`turn_counts`), a separate single heartbeat session slot, and per-channel delivery/canvas/core-prompt caches keyed the same way -- one AcpClient (one spawned agent subprocess) can therefore hold several concurrently live ACP sessions, one per Buzz channel plus at most one heartbeat session."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:110-139"
  - statement: "SessionState::invalidate_channel removes a channel's session_id, turn_count, core/canvas sections and delivery state together (never partially), and SessionState::invalidate_all clears every one of those maps plus the heartbeat session in one call; both are pure in-memory bookkeeping operations -- neither one sends any ACP request to the agent subprocess telling it a session ended."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:141-176"
  - statement: "The per-channel/per-heartbeat prompt dispatch path resolves session_id by first checking SessionState's existing map; only on a miss does it call session/new (via create_session_and_apply_model), insert the returned id into the map, and call notify_session_spawned to seed a zero usage baseline -- so a session is created lazily, at most once per channel until invalidated, not eagerly at agent startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:2107-2232"
  - statement: "If session creation returns AcpError::AgentExited, the caller invalidates every session on that agent (invalidate_all) rather than only the one channel that was creating a session, because the underlying subprocess is gone and every session it held is unreachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:2149-2160"
  - statement: "After a successful turn, the dispatcher proactively rotates (invalidates) the session when the turn's StopReason was MaxTokens or MaxTurnRequests, OR when a configured per-channel/heartbeat turn counter reaches `max_turns_per_session` (0 = disabled, the flag's default) -- both cases call SessionState::invalidate on that PromptSource so the next turn creates a fresh session rather than continuing the old one."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:2805-2835"
      - "crates/buzz-acp/src/config.rs:376-380"
  - statement: "invalidate_channel_sessions is called when an agent is removed from a channel, explicitly so a stale session for that channel is never reused by an idle agent; a checked-out (in-flight) agent's active session is deliberately left alone by this path and is only invalidated on its next natural resolution."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:946-964"
  - statement: "switch_idle_agent_model invalidates an idle agent's channel session as part of an explicit model switch, so the next turn's session/new is created under the newly selected model rather than mutating a live session's model mid-flight."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:966-1013"
  - statement: "ACP-level authentication (the `authenticate` request and the adapter-advertised `authMethods` array parsed from `initialize`'s result) is exercised by buzz-acp only through a standalone CLI path (`buzz-acp auth-methods` to list them, and an authenticate flow that spawns the agent, calls initialize, checks the requested method_id is in authMethods, calls authenticate, then shuts the process down) -- entirely separate from, and prior to, any session/new call. session/new itself carries no credential or auth field in its request params."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:624-630"
      - "crates/buzz-acp/src/lib.rs:4821-4924"
  - statement: "No `agent-client-protocol` crate dependency exists in buzz-acp's own Cargo.toml -- the ACP JSON-RPC wire format (including every session/* method this node describes) is hand-implemented directly in acp.rs rather than generated from or checked against an external ACP schema crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
  - statement: "Issue #975's Definition of Done, inherited from the corpus-wide interface template shape, requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to any authoritative machine/spec representation, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#975 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# ACP session: interface

The boundary between `buzz-acp` (the ACP harness bridging Buzz channels to AI
agent subprocesses) and one spawned agent subprocess, scoped to **session
lifecycle**: how a session is created, identified, kept alive across turns,
proactively rotated, and terminated. The two sides exchange JSON-RPC 2.0
requests and notifications over the agent's stdin/stdout pipes
(newline-delimited JSON, i.e. NDJSON) — the Agent Client Protocol (ACP), a
protocol buzz-acp implements directly in its own code rather than through an
external `agent-client-protocol` crate dependency. On the Buzz side, a session
is not the whole `AcpClient`/subprocess: one spawned agent process can hold
several concurrently live sessions, one per Buzz channel it is currently
serving, plus at most one dedicated heartbeat session.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Spawn | `AcpClient::spawn` (`crates/buzz-acp/src/acp.rs:454-567`) | OS-level process creation, not itself an ACP method — launches the agent binary, wires stdio pipes, applies env defaults, and (Unix) puts the child in its own process group. |
| `initialize` | `AcpClient::initialize` (`crates/buzz-acp/src/acp.rs:611-622`) | Must be called exactly once, before any other ACP method. Negotiates `protocolVersion` (buzz-acp requests `2`) and exchanges capabilities; response is parsed for `_meta.steering.supported`. |
| `session/new` | `AcpClient::session_new_full` / `session_new` (`crates/buzz-acp/src/acp.rs:632-703`) | Creates one session under an initialized client. Params: `cwd` (absolute path), `mcpServers`, optional `systemPrompt`/`_meta.systemPrompt`, optional `_meta.sessionTitle`. Returns the agent-assigned `sessionId`. |
| `session/set_config_option` | `AcpClient::session_set_config_option` (`crates/buzz-acp/src/acp.rs:723-736`) | Stable-path per-session config change (e.g. permission mode, reasoning effort) against an existing `sessionId`. |
| `session/set_model` | `AcpClient::session_set_model` (`crates/buzz-acp/src/acp.rs:738-749`) | Unstable-path per-session model change against an existing `sessionId`. |
| `_goose/unstable/session/system-prompt/set` | `AcpClient::session_set_goose_system_prompt` (`crates/buzz-acp/src/acp.rs:705-721`) | Goose-specific extension to replace the session's system prompt after creation; not part of the stable ACP surface. |
| `session/cancel` | `AcpClient::session_cancel` (`crates/buzz-acp/src/acp.rs:849-854`) | JSON-RPC *notification* (no response) asking the agent to stop the in-flight turn on a session; does not itself end the session. |
| Cancel + drain | `AcpClient::cancel_with_cleanup` / `cancel_with_cleanup_grace` / `cancel_with_cleanup_until` (`crates/buzz-acp/src/acp.rs:945-1062`) | Composite: answers any pending permission request, sends `session/cancel`, then reads until the turn's `session/prompt` response arrives with `stopReason: "cancelled"`. |
| Local invalidation | `SessionState::invalidate_channel` / `invalidate_all` / `invalidate_channel_sessions` (`crates/buzz-acp/src/pool.rs:141-176`, `946-964`) | Buzz-side bookkeeping only — drops the `channel_id -> session_id` mapping (and its turn count / delivery / prompt-context caches) so the next turn creates a fresh session. Sends nothing to the agent. |
| Process termination | `AcpClient::shutdown` (`crates/buzz-acp/src/acp.rs:416-444`) | Kills the agent's whole OS process group (bounded 5s wait), ending every session that process held at once. The only operation that ends a session at the wire/process level. |
| `authenticate` | `AcpClient::authenticate` (`crates/buzz-acp/src/acp.rs:624-630`), driven by `buzz-acp auth-methods` / an authenticate CLI flow (`crates/buzz-acp/src/lib.rs:4821-4924`) | A standalone, pre-session flow: spawn, `initialize`, read `authMethods`, `authenticate`, shut down. Not part of the per-turn session surface `session/new` participates in. |

## Contract and stability

**Inputs / messages.** Every session-scoped request after `session/new`
carries the agent-assigned `sessionId` as an opaque string parameter
(`crates/buzz-acp/src/acp.rs:706-749`, `849-854`) — buzz-acp never parses,
validates, or derives structure from it. `session/new` itself requires an
absolute `cwd`; `mcpServers` may be empty but the field is always present.

**Outputs / responses.** `session/new`'s success response is captured as a
`SessionNewResponse { session_id: String, raw: serde_json::Value }`
(`crates/buzz-acp/src/acp.rs:2123-2130`) — the full raw JSON result is kept
alongside the extracted id so callers can pull model-configuration fields out
of it without a second round trip. `session/prompt` (the per-turn operation,
out of this node's scope — see *Boundary*) responds with a `stopReason` this
node's rotation logic consumes but does not itself define.

**Error / rejection behavior.** Three distinct failure shapes exist, and this
node's evidence ledger cites a concrete example of each:

1. **Malformed success response.** A `session/new` result missing a string
   `sessionId` is rejected client-side as `AcpError::Protocol("session/new
   response missing sessionId")` (`acp.rs:677-680`) — there is no
   fallback id.
2. **Agent-reported JSON-RPC error.** Any JSON-RPC error object for a
   session-scoped request becomes `AcpError::AgentError { code, message }`
   (`acp.rs:80-124`); when `message` is absent or non-string the whole error
   object is kept as the message rather than discarded.
3. **Client-side precondition violation.** Calling the cancel-and-drain path
   with no in-flight prompt on that session fails fast, before any write,
   as `AcpError::Protocol("cancel_with_cleanup called with no in-flight
   prompt")` (`acp.rs:1014-1024`).

A fourth, coarser failure — `AcpError::AgentExited` — is not a
session-specific error at all: it means the whole subprocess died, and every
session that client held is invalidated together
(`pool.rs:2149-2160`), not just the one in flight.

**Authentication / authorization.** ACP's own `authenticate` exchange
(advertised via `initialize`'s `authMethods`) is not a per-session concern in
this codebase: buzz-acp only drives it through a standalone CLI path that
spawns an agent, authenticates, and shuts back down before any
`session/new` call is ever made (`acp.rs:624-630`, `lib.rs:4821-4924`).
`session/new`'s own request carries no credential field. The one
capability buzz-acp does declare at `initialize` time is `auth.terminal:
true` — permission to hand a user to a terminal-native login flow
(`acp.rs:393-414`) — a capability negotiation, not a per-session credential.

**Versioning / compatibility.** buzz-acp pins `protocolVersion: 2` in every
`initialize` call, and the code comment states this is "an intentional
temporary pin — we are squatting on ACP v2 ahead of the upstream ACP RFD"
(`acp.rs:126-135`, `611-622`), to be revisited once that RFD lands. There is
no per-session version negotiation beyond the one client-wide `initialize`
call; every session created on a given `AcpClient` shares that negotiated
version.

**Ordering / idempotency.** `initialize` must run exactly once, before any
`session/new` (module doc comment, `acp.rs:1-9`). Within one `AcpClient`,
`session_cancel` asserts (via `install_steer_rx`'s sibling invariant and the
cancel-drain precondition) that at most one turn is in flight per client at a
time — a fresh `session/new` for a *different* channel while another
channel's turn is in flight is not itself an ACP-level operation this client
serializes; `pool.rs`'s dispatcher is what decides how concurrent per-channel
prompt tasks share one `AcpClient`. `session/new` is not idempotent: calling
it twice for the same channel produces two distinct sessions on the agent
side; `pool.rs`'s session map is exactly the mechanism that prevents this by
only calling `session/new` on a map miss (`pool.rs:2107-2232`).

**Authoritative representation.** No independent specification document
(OpenAPI, AsyncAPI, or an ACP schema file) exists in this repository for this
surface — `buzz-acp/Cargo.toml` carries no `agent-client-protocol` dependency,
so `crates/buzz-acp/src/acp.rs` itself, plus the external Agent Client
Protocol the module doc comment names, is the authoritative representation of
the wire shape this node describes.

## Boundary

This node does not describe:

- **The base JSON-RPC/NDJSON transport mechanics** (framing, line-length
  bounding via `LinesCodec::new_with_max_length`, request-id counters,
  read-loop dispatch) — that is the sibling ACP **protocol** node (issue
  #973)'s subject. This node only names which session-scoped methods exist
  and what they promise, not how a line of NDJSON becomes a parsed
  JSON-RPC message.
- **`session/prompt`'s own message/content-block framing** (prompt block
  shapes, slash-command pass-through, `StopReason` variants themselves) —
  that is the sibling ACP **message** node (issue #974)'s subject. This node
  only says that a `stopReason` value drives session rotation, not what each
  value means or how prompt content is built.
- **`session/request_permission` and tool-call handling** — that is the
  sibling ACP **tool-call** node (issue #976)'s subject. This node mentions
  it only insofar as `cancel_with_cleanup` must answer a pending permission
  request before it can cancel a turn.
- **A domain-expert, field-by-field parameter catalogue** for every
  session-scoped method — this node names each operation's defining source
  and its lifecycle contract, not an exhaustive schema of every field
  (`templates/interface.md`'s own stated depth limit).
- Any `relationships` edge to the #973/#974/#976 sibling nodes above: none of
  those nodes is merged to `origin/launchpad` as of this node's recorded
  revision, and a `relationships[].target` naming an id no loaded node
  carries is a hard validation error (`AGENTS.md` step 9). A later edit
  should add `references` edges to them once they exist.

## Relationships

- `implements` -> `corpus-template-interface`: this node is a concrete
  instance of the interface template (`launchpad/docs/corpus/templates/interface.md`),
  which is merged to `origin/launchpad` at this node's recorded revision.
- No `references` edges are declared. The plausible targets — ACP protocol
  (#973), ACP message (#974), and ACP tool-call (#976) — are all being
  authored in parallel on unmerged branches at this node's recorded revision
  and are not valid targets yet; see *Boundary* above.

## Scope and omissions

**This node covers** how one ACP session is created (`session/new`), how its
`sessionId` is held and re-used across turns within `buzz-acp`'s own
in-memory `SessionState`, how a session is proactively rotated (stop-reason-
or turn-count-driven), how a turn on a session is cancelled, and the two
distinct ways a session's life actually ends in this codebase: local
invalidation (buzz-acp forgets the id; nothing is sent to the agent) versus
subprocess shutdown (the whole agent process, and every session it held, is
killed at once).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| JSON-RPC/NDJSON transport framing | Sibling ACP protocol node, issue #973 (unmerged) |
| `session/prompt` message/content-block framing and `StopReason` semantics | Sibling ACP message node, issue #974 (unmerged) |
| `session/request_permission` and tool-call handling | Sibling ACP tool-call node, issue #976 (unmerged) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| The interface template's own required-sections rationale | `launchpad/docs/corpus/templates/interface.md` |

**Expected but not verified when this node was written:**

- **No live agent subprocess was spawned to observe this exchange
  end-to-end during this task.** Every claim above is grounded in reading
  `crates/buzz-acp/src/acp.rs` and `pool.rs`'s source and their own unit
  tests (which script a fake subprocess), not in running a real Claude/Codex/
  Goose adapter against a live `buzz-acp` process.
- **Whether every current ACP adapter (claude-agent-acp, codex-acp, goose,
  buzz-agent) actually implements every operation in the table above
  identically was not cross-checked against each adapter's own source** —
  only against buzz-acp's client-side expectations of them.
- **Whether the upstream ACP RFD that `protocolVersion: 2`'s pin is waiting
  on has since published or changed the session lifecycle this node
  describes was not checked** — the code comment names the pin as temporary
  but this node does not track the RFD's own status.
- **The `agent-client-protocol` crate's own upstream specification text was
  not fetched or read** — its absence as a dependency was confirmed via
  `Cargo.toml`, not by comparing buzz-acp's implementation against that
  crate's or ACP's own specification document.
