# Plan — issue #1125: document `layers/networking/heartbeat.md`

Feature #609 (protocol and networking layer corpus). One concept node, node id
`layers-networking-heartbeat`, template `launchpad/docs/corpus/templates/concept.md`.

Base: `origin/launchpad` at `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`.
Worktree: `__worktrees/task-1125-heartbeat`, branch `task/1125-heartbeat`.

## ALREADY TRUE

Established by reading the code before drafting, not assumed:

- The relay runs a real transport-level heartbeat. `crates/buzz-relay/src/connection.rs`
  spawns `heartbeat_loop` per connection: a 30-second `tokio::time::interval` that
  increments a shared `missed_pongs` counter, cancels the connection once three ticks
  have passed without an inbound Pong, and sends its Ping through the priority control
  channel. `recv_loop` resets the counter on Pong and answers an inbound Ping with a
  Pong on the same control channel.
- A **second, independent implementation of the same policy** exists for the huddle
  audio socket: `crates/buzz-relay/src/audio/handler.rs` has its own `heartbeat_loop`
  with `HEARTBEAT_INTERVAL = 30s` and `MAX_MISSED_PONGS = 3`, expressed with different
  arithmetic (`fetch_add(..) + 1 >= 3` vs `fetch_add(..) >= 2`) that resolves to the
  same behaviour.
- Client behaviour is asymmetric and per-client:
  - `crates/buzz-ws-client/src/connection.rs` never initiates a Ping; it answers one
    and otherwise bounds each operation by a caller-supplied `timeout_dur`.
  - `mobile/lib/shared/relay/relay_socket.dart` sets `IOWebSocketChannel`'s
    `pingInterval` to 30 seconds — the only client that pings.
  - Desktop is deliberately passive: `desktop/src/shared/api/relayStallWatchdog.ts`
    writes nothing to the socket and treats any inbound frame as liveness, with
    `STALL_CHECK_INTERVAL_MS = 10_000` and `STALL_IDLE_TIMEOUT_MS = 60_000` from
    `desktop/src/shared/api/relayClientTimings.ts`.
  - `desktop/src-tauri/src/native_websocket.rs`'s `outbound_message` forwards Ping and
    Pong frames to JS alongside Text, which is what makes the passive watchdog work.
- **The name collides three ways.** `capabilities-presence-presence-heartbeat` is
  merged on `origin/launchpad` and documents the *application-level* kind:20001
  presence republish; it already names the transport heartbeat as explicitly out of its
  scope. `crates/buzz-acp/src/config.rs` adds two more: `heartbeat_interval_secs`
  (`BUZZ_ACP_HEARTBEAT_INTERVAL`, agent self-prompting) and `turn_liveness_secs`
  (desktop crash backstop), and its own doc comment distinguishes those two.
- `architecture-flows-websocket-connection` (merged) already narrates `heartbeat_loop`
  inside the relay's four-task connection lifecycle, including a *Keepalive* section.
  This node must link to it, not restate it.
- Tests exist on the client side only: `mobile/test/shared/relay/relay_socket_liveness_test.dart`
  and `desktop/src/shared/api/relayStallWatchdog.test.mjs`. `connection.rs`'s `#[cfg(test)]`
  module covers `send_loop` and REQ scoping, not `heartbeat_loop`.
- Legal relationship targets confirmed against the merged-id index:
  `architecture-flows-websocket-connection`, `capabilities-presence-presence-heartbeat`,
  `implementation-crates-buzz-relay`, `implementation-crates-buzz-ws-client`,
  `verification-contracts-websocket`.

## STEP 1 — write the front matter

`id: layers-networking-heartbeat`, `type: layers`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator]` (operator earns its place: the interval and
the miss threshold are hardcoded, so an operator diagnosing disconnects has no dial).
Evidence ledger built from the ALREADY TRUE list, one provenance FACT only, INFERENCE
entries carrying `confidence`, GitHub history as TEAM_KNOWLEDGE with `provided_by`.

**Done when:** front matter matches `schema/node.schema.json` — seven permitted fields,
FACT with no `confidence`/`provided_by`, INFERENCE with both `evidence` and
`confidence`, TEAM_KNOWLEDGE with `provided_by` and no `confidence`.

## STEP 2 — write the body against `templates/concept.md`'s required sections

Title + intro, **Definition** (carrying the mandatory disambiguation of the three
"heartbeat" meanings), Use cases, a Comparison table of the per-side implementations,
Related resources routed through `relationships`, Scope and omissions.

**Done when:** every required section from the template's *Required sections* block is
present, and the Definition section names the presence-heartbeat collision explicitly
rather than leaving the reader to infer it.

## STEP 3 — Scope and omissions carries both halves

Half one: what this node does not cover and who owns it (the per-connection lifecycle
narrative → `architecture-flows-websocket-connection`; presence liveness →
`capabilities-presence-presence-heartbeat`; ACP heartbeat/turn-liveness → neither,
unowned). Half two: what was expected and could not be verified.

**Done when:** the section contains both an ownership table and a separate
"expected but not verified" list.

## STEP 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py`

**Done when:** exit 0.

## STEP 5 — stamp, then commit

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as a sole, unpiped, foreground command; confirm `OK`; then `git add` + `git commit -s`
in a separate call.

**Done when:** the commit exists on `task/1125-heartbeat` and nothing is pushed.

## GATES

- `validate.py` exits 0.
- The corpus unittest suite reports `OK`.
- Every `relationships[].target` appears in the merged-id index; no sibling from
  Feature #609 is targeted.
- Exactly one hand-authored corpus document changed.

## BUDGET

5 steps, one new corpus file plus this plan. No code changes. No push, no PR.

## OPEN

- Whether the duplicated relay-side heartbeat policy (main socket vs huddle audio
  socket) should be deduplicated into one shared helper is an implementation question
  this node records but does not decide.
- Whether tungstenite's automatic Pong reply on the desktop native transport means the
  desktop *does* answer relay Pings without any application code was not confirmed from
  this repository; it is recorded as unverified rather than asserted.

## LEFT OUT

- The ACP heartbeat prompt (`BUZZ_ACP_HEARTBEAT_INTERVAL`) and ACP turn-liveness
  (`turn_liveness_secs`). Both are agent-session concerns, not transport keepalive.
  Named for disambiguation only; reported to the orchestrator as candidate follow-up
  tasks, not folded in.
- Reconnection and backoff policy (`relayReconnectPolicy.ts`, `RECONNECT_*` timings) —
  what happens *after* a heartbeat failure tears a connection down is a separate idea.
- The relay's 5-second `AUTH_TIMEOUT` and graceful-drain close path, both already
  covered by `architecture-flows-websocket-connection`.
