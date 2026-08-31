# Plan: issue #1246 — document platforms/desktop/relay-connection.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (commit `131b02f989684117d9ab1dd426f1673fa638e523`) — no conflict, no
  duplicate to update instead of create.
- Sibling architecture nodes already merged and readable: `architecture-containers-desktop`
  (container-level desktop doc), `architecture-flows-websocket-connection` and
  `architecture-flows-websocket-authentication` (relay-side NIP-42/connection
  protocol). This node must not duplicate their content — it documents the
  **desktop app's own** wiring of that protocol (Rust + TS), not the protocol
  itself.
- No `platforms`-type template exists yet; closest fit for shape/required
  sections is `launchpad/docs/corpus/templates/component.md` (responsibility,
  public interface, dependencies, boundary) even though its own `type`
  recommendation (`implementation`) doesn't apply here — this node's path and
  the batch's own PRD (#614 "runtime platform corpus exists") dictate
  `type: platforms`.

## STEP 1 — Confirm scope and non-duplication

Read issue #1246 DoD, `node.schema.json`, `AGENTS.md`, `standards/naming.md`,
`standards/code-references.md`, and the `component.md` template. Confirm
target path is free. Done.

## STEP 2 — Investigate real source

Read `desktop/src-tauri/src/relay.rs` (URL resolution), `native_relay_client.rs`
(backend buzz-ws-client session + backoff), `native_websocket.rs` (custom
Tauri WS plugin), `desktop/src/shared/api/relayClientSession.ts` +
`relayClientTimings.ts` + `relayReconnectController.ts` (frontend connection/
reconnect/auth orchestration), `desktop/src/features/communities/useCommunityInit.ts`
+ `commands/workspace.rs` + `app_state.rs` (community-switch reconnect chain),
and `crates/buzz-ws-client/src/connection.rs` (confirm it has no
reconnect/backoff of its own). Done — all citations below were opened
directly, not inferred from a sub-agent summary alone.

## STEP 3 — Write the node

`launchpad/docs/corpus/platforms/desktop/relay-connection.md`, `type: platforms`,
`id: platforms-desktop-relay-connection`, using the `component.md` template's
shape (responsibility / interface / dependencies / boundary / relationships /
scope-and-omissions) since no `platforms` template exists. Central finding to
convey accurately: desktop has **two independent relay connections** with
independently-implemented (numerically coordinated, not shared-code) backoff —
a Rust-owned background session (`native_relay_client.rs`, via `buzz-ws-client`)
and the TypeScript-owned main chat session (`relayClientSession.ts`, via a
custom Tauri plugin, NOT `buzz-ws-client`). Declare `depends-on` toward
`architecture-containers-desktop` and `references` toward the two websocket
flow nodes (both exist on `origin/launchpad` at the recorded revision).

## STEP 4 — Validate

Run `validate.py` with and without the new file to confirm zero new FAIL
lines (only the pre-existing 21).

## STEP 5 — Commit

Per the batch's fixed two-call gate sequence.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — new file adds
  zero new FAIL lines beyond the pre-existing 21.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK.

## OPEN

- No `platforms`-surface template exists yet (owned by a future corpus-standards
  task) — this node follows `component.md`'s shape as the closest analog and
  says so in its own body, rather than inventing an unreviewed template.

## LEFT OUT

- The relay-side WebSocket/NIP-42 protocol itself (owned by the two existing
  `architecture/flows/websocket-*` nodes — linked, not restated).
- The huddle/audio signaling socket (`huddle/relay_api.rs`) — a separate
  connection with its own node candidate, out of scope for this task's
  single-idea rule.
- The internal-build-only VPN/transport-recovery hook's own implementation
  (`relay_reconnect_hook`) — named as an escalation phase, not documented in
  depth, since it is a no-op in this OSS checkout.
