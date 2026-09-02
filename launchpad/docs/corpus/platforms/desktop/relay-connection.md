---
id: platforms-desktop-relay-connection
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The desktop Rust backend resolves the relay WebSocket URL through relay_ws_url_with_override, whose own doc comment states the precedence workspace override, then env vars, then build-time vars, then default; relay_ws_url itself checks BUZZ_RELAY_URL, then the BUZZ_DESKTOP_BUILD_RELAY_URL build-time constant, then falls back to the ws://localhost:3000 default, and workspace_relay_override reads AppState.relay_url_override."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/relay.rs"
  - statement: "desktop/src-tauri/Cargo.toml declares a path dependency on buzz-ws-client, aliased to the Rust import name buzz_ws_client_pkg, with no version pin."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:111"
  - statement: "The desktop backend maintains its own relay WebSocket session distinct from the app's main chat connection: native_relay_client.rs's own doc comment states this session 'reconnects on drop with exponential backoff and resubscribes the current desired set', built on buzz-ws-client's NostrWsConnection and its connect_authenticated entry point, for backend features needing live subscriptions independent of the UI (archive sync, persona catalog, unread catch-up)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client.rs"
  - statement: "native_relay_client.rs's run_session reconnect loop starts each attempt at RECONNECT_BASE_DELAY (500ms), doubles the delay after every failed attempt via `delay = (delay * 2).min(RECONNECT_MAX_DELAY)`, caps it at RECONNECT_MAX_DELAY (30 seconds), and resets to the base delay on a successful authenticated connect; a source comment states the 30-second ceiling deliberately matches the frontend renderer session's own ceiling, so a relay outage produces one shared retry cadence rather than two independently-tuned ones."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client.rs"
  - statement: "buzz-ws-client's own NostrWsConnection (crates/buzz-ws-client/src/connection.rs) implements no reconnection or backoff logic itself: connect() opens one socket via tokio_tungstenite::connect_async, connect_authenticated() chains connect() and authenticate() once, and disconnect() closes it, with no retry loop anywhere in the file -- every reconnect/backoff policy documented in this node is implemented by a caller of this crate, not by the crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "The desktop app's main chat connection is not opened through buzz-ws-client at all. desktop/src/shared/api/relayClientSession.ts's RelayClient.connect() opens it by calling invoke(\"plugin:websocket|connect\", { url, onMessage, config }) from @tauri-apps/api/core, against a custom in-repo Tauri plugin (desktop/src-tauri/src/native_websocket.rs, tauri::plugin::Builder::new(\"websocket\")) whose #[tauri::command] async fn connect opens the real socket in the Rust process via tokio_tungstenite::connect_async and relays frames to the webview over a Tauri IPC Channel."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
      - "desktop/src-tauri/src/native_websocket.rs"
  - statement: "RelayClient's reconnect backoff (relayClientSession.ts) starts at RECONNECT_BASE_DELAY_MS (1,000ms, defined in relayClientTimings.ts), applies +/-25% jitter, doubles on each failure up to RECONNECT_MAX_DELAY_MS (30,000ms), and resets to the base delay once the connection has stayed up for BACKOFF_RESET_STABLE_MS -- an independent implementation from native_relay_client.rs's backend backoff, not shared code, with a different base delay (1,000ms vs. the backend's 500ms) despite both citing the same 30-second ceiling."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
      - "desktop/src/shared/api/relayClientTimings.ts"
  - statement: "relayClientSession.ts exposes two distinct re-engagement entry points beyond the ordinary backoff loop: preconnect() (used on app boot and community switch) clears the terminal-failure latch and the AUTH-rejection streak and bypasses any pending backoff, while resumeReconnect() (wired from online/focus/visibility browser events via useRelayResumeTriggers.ts) bypasses a pending backoff timer but preserves the terminal latch."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
  - statement: "relayReconnectController.ts's own module doc comment describes a three-phase reconnect strategy surfaced to the UI: (1) an optimistic preconnect() fast path bounded by fastPathTimeoutMs, (2) escalation to a build-time-configured transport-recovery hook only when the fast path fails and a hook is configured, and (3) waiting on the session's own background exponential-backoff loop up to a backstopMs ceiling; DEFAULT_RECONNECT_TIMING_POLICY sets fastPathTimeoutMs to 11,000ms and backstopMs to 120,000ms."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayReconnectController.ts"
  - statement: "The phase-2 escalation hook is exposed to the frontend as the Tauri commands relay_reconnect_hook_configured and relay_reconnect_hook, and the Rust source states this hook is an internal-build-only VPN/transport-recovery mechanism that is a pure no-op in this OSS checkout when its configuring env var is unset."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/relay_reconnect.rs"
  - statement: "A relay CLOSED response to one live subscription is retried independently of the whole-connection backoff above, on its own base/ceiling: relayClosedRecovery.ts defines RETRY_BASE_DELAY_MS = 1,000 and RETRY_MAX_DELAY_MS = 30,000 with exponential growth (RETRY_BASE_DELAY_MS * 2 ** attempt, capped), and native_relay_client.rs's own CLOSED_RETRY_BASE_DELAY (1 second) and CLOSED_RETRY_MAX_DELAY (30 seconds) are commented as deliberately matching those two TypeScript constants."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClosedRecovery.ts"
      - "desktop/src-tauri/src/native_relay_client.rs"
  - statement: "Switching the active community tears down and re-establishes the main relay connection through a five-step chain: (1) resetCommunityState() in useCommunityInit.ts calls relayClient.disconnect() first, which nulls this.relayUrl, closes the current socket via closeWebSocket(this.wsId, \"community switch\"), and sets the connection-state emitter to \"idle\"; (2) useCommunityInit then calls applyCommunity(...), which invokes the Tauri command apply_workspace; (3) apply_workspace (desktop/src-tauri/src/commands/workspace.rs) writes the new relay URL into AppState.relay_url_override, a Mutex<Option<String>> field (desktop/src-tauri/src/app_state.rs); (4) once applyCommunity resolves, App.tsx re-renders <AppReady key={communityKey}>, and the changed key (derived from the active community id, a reinit counter, the current pubkey, and a signer epoch) forces React to unmount and remount the entire community-scoped subtree; (5) the freshly-mounted AppShell's useAppShellLifecycleEffects.ts runs an effect with an empty dependency array that calls relayClient.preconnect(), which re-fetches the relay URL (now reflecting the new override) and opens a fresh socket via the same plugin:websocket|connect call."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts"
      - "desktop/src-tauri/src/commands/workspace.rs"
      - "desktop/src-tauri/src/app_state.rs"
      - "desktop/src/app/App.tsx"
      - "desktop/src/app/useAppShellLifecycleEffects.ts"
  - statement: "CLAUDE.md's own 'Community Switching' section states that switching communities does not reload the page and instead uses React key-based remounting via <AppReady key={communityKey} />, and that resetCommunityState() in useCommunityInit.ts is the canonical inventory of community-scoped singletons that must be reset on switch -- relayClient is one of those singletons."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: "The desktop frontend's NIP-42 AUTH event is not built by buzz-ws-client's build_auth_event. armRelayAuthentication (desktop/src/shared/api/relayAuthPolicy.ts), invoked from RelayClient.connect(), orchestrates waiting for the challenge and the OK reply, while the actual kind:22242 event is constructed and signed by the Tauri command create_auth_event (desktop/src-tauri/src/commands/identity.rs), which builds an EventBuilder::new(Kind::Custom(22242), \"\") with relay/challenge tags -- a separate implementation of the same NIP-42 event shape buzz-ws-client's build_auth_event constructs, not a shared call into it."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayAuthPolicy.ts"
      - "desktop/src-tauri/src/commands/identity.rs"
  - statement: "buzz-ws-client's connect_authenticated IS used elsewhere in the desktop backend: the huddle (voice channel) audio signaling socket in desktop/src-tauri/src/huddle/relay_api.rs calls it (via a similarly-named connect_authenticated_audio_socket wrapper) for its own, separate connection, independent of both the native background session and the main chat connection this node documents."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/relay_api.rs"
  - statement: "No Rust-emitted Tauri event surfaces general relay connection status to the frontend; connection state for the main chat connection is tracked entirely in the frontend's own RelayConnectionStateEmitter (idle/connecting/connected/reconnecting/stalled) and read via relayClient.getConnectionState()/subscribeToConnectionState(), not pushed from the Rust side as a Tauri event."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
  - statement: "Because the desktop app's own connection resolves the relay URL through a workspace-configurable override chain (relay_ws_url_with_override) rather than a single build-time value, and because that same override is the mechanism community switching uses to redirect the connection, this component is downstream of and constrained by the desktop container's own technology and interface boundary already documented in architecture-containers-desktop -- making that node's claims a precondition for this one's, which is why this node declares a part-of relationship to it rather than restating its container-level content."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/relay.rs"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
    confidence: 0.75
  - statement: "Issue #1246's Definition of Done, read together with its category-specific tail ('states responsibility and well-defined interface/boundary', 'names dependencies and collaborators', 'links source implementation and tests', 'explains only component-level behavior, not the entire containing platform'), requires this node to document one platform-integration component rather than desktop's whole architecture, which architecture-containers-desktop already covers at the container level."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1246 definition of done and its category-specific DoD tail"
  - statement: "No platforms-surface template exists in launchpad/docs/corpus/templates/ at the recorded revision (the templates directory holds architecture-*, capability, component, and other shapes, but none named for the platforms surface), so this node follows the component.md template's shape -- responsibility, public interface, dependencies, boundary, relationships, scope and omissions -- as the closest existing analog, rather than inventing an unreviewed structure."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "desktop/src-tauri/src/native_relay_client_tests.rs contains a unit test named retry_delay_grows_and_stops_at_the_ceiling, alongside sibling tests covering CLOSED-message classification and rate-limit retry hints, exercising the backend background session's reconnect-delay growth and ceiling this node documents."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_relay_client_tests.rs"
  - statement: "desktop/src/shared/api/relayReconnectPolicy.test.mjs contains unit tests named 'baseline scenario schedules a reconnect', 'terminal session refuses to schedule (Max's auth-rejection scenario)', and 'pending reconnect timer suppresses scheduling another', covering the decision logic for when RelayClient schedules a reconnect attempt."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayReconnectPolicy.test.mjs"
  - statement: "desktop/src/shared/api/relayReconnectController.test.mjs contains unit tests named 'escalation fires only when fast path fails and hook is configured', 'escalation skipped when hook not configured', and 'backstop fires onBackstop, not onSuccess, and resets state', covering the three-phase fast-path/escalation/backstop sequence this node describes."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayReconnectController.test.mjs"
  - statement: "desktop/src/features/communities/relayProbe.test.mjs covers a one-shot raw browser WebSocket reachability probe (relayProbe.ts) used by the add/edit-community form, which is a separate, short-lived socket from the two persistent relay connections (backend background session and frontend main chat session) this node otherwise documents."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/relayProbe.test.mjs"
      - "desktop/src/features/communities/relayProbe.ts"
relationships:
  - type: part-of
    target: architecture-containers-desktop
  - type: implements
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-websocket-connection
---

# Desktop: relay connection

How the Buzz desktop app (Tauri 2 + Rust backend, React 19 frontend) opens,
authenticates, and maintains its own WebSocket connection(s) to a Buzz relay,
and how switching the active community redirects that connection to a new
relay. This is one platform-integration component of the `architecture-containers-desktop`
container (see *Relationships*) -- it does not restate that container's whole
technology boundary, and it does not restate the relay-side NIP-42/WebSocket
protocol already documented in `architecture-flows-websocket-connection` and
`architecture-flows-websocket-authentication`.

## Responsibility

Desktop resolves a relay URL, opens an authenticated WebSocket connection to
it, keeps that connection alive across drops with its own retry policy, and
re-points the connection at a different relay when the user switches their
active community -- all without a full page reload
(`desktop/src-tauri/src/relay.rs`, `desktop/src/shared/api/relayClientSession.ts`).

**There are two independent relay connections in the desktop process**, each
with its own, separately-implemented (but numerically coordinated)
reconnect policy:

1. **The main chat connection** -- owned by the frontend
   (`desktop/src/shared/api/relayClientSession.ts`'s `RelayClient` class),
   used for channel history, live subscriptions, publishing, and presence.
2. **A backend-owned background session** -- owned by the Rust backend
   (`desktop/src-tauri/src/native_relay_client.rs`), used for features that
   need live subscriptions independent of the UI (archive sync, persona
   catalog, unread catch-up).

A third, separate connection exists for huddle (voice channel) audio
signaling (`desktop/src-tauri/src/huddle/relay_api.rs`) -- named here only to
be excluded; see *Boundary*.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `relay_ws_url_with_override` | Rust fn | Resolves the relay WebSocket URL: workspace override, then `BUZZ_RELAY_URL` env var, then the `BUZZ_DESKTOP_BUILD_RELAY_URL` build-time constant, then `ws://localhost:3000` | `desktop/src-tauri/src/relay.rs` |
| `AppState.relay_url_override` | Rust field (`Mutex<Option<String>>`) | The workspace-level override community switching writes to and connection resolution reads from | `desktop/src-tauri/src/app_state.rs` |
| `apply_workspace` | Tauri command | Frontend entry point that sets `relay_url_override` for the newly-selected community | `desktop/src-tauri/src/commands/workspace.rs` |
| `plugin:websocket\|connect` / `\|send` / `\|disconnect` | Custom Tauri plugin commands | Opens/uses/closes the real OS-level socket in the Rust process (`tokio_tungstenite::connect_async`), relaying frames to the webview over an IPC `Channel` | `desktop/src-tauri/src/native_websocket.rs` |
| `RelayClient.connect()` / `.disconnect()` / `.preconnect()` / `.resumeReconnect()` | TypeScript class methods | Frontend connection lifecycle: open, tear down, re-engage bypassing backoff, resume after an environment signal | `desktop/src/shared/api/relayClientSession.ts` |
| `relayClient` (module singleton) | TypeScript export | The one `RelayClient` instance the rest of the frontend uses; reset on community switch | `desktop/src/shared/api/relayClient.ts` |
| `create_auth_event` | Tauri command | Builds and signs desktop's own kind:22242 NIP-42 AUTH event (`Kind::Custom(22242)` with `relay`/`challenge` tags) | `desktop/src-tauri/src/commands/identity.rs` |
| `armRelayAuthentication` | TypeScript function | Frontend-side AUTH-challenge/OK orchestration invoked from `RelayClient.connect()` | `desktop/src/shared/api/relayAuthPolicy.ts` |
| `relay_reconnect_hook_configured` / `relay_reconnect_hook` | Tauri commands | Phase-2 escalation hook for `relayReconnectController.ts`; a no-op unless an internal build configures it | `desktop/src-tauri/src/commands/relay_reconnect.rs` |
| `NostrWsConnection::connect_authenticated` | Rust fn (`buzz-ws-client`) | Single-shot connect-then-authenticate helper used by the backend background session and by huddle audio -- **not** by the main chat connection | `crates/buzz-ws-client/src/connection.rs` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-ws-client` crate | Backend background session (`native_relay_client.rs`) and huddle audio (`huddle/relay_api.rs`) both build their connections on `NostrWsConnection` | `desktop/src-tauri/Cargo.toml:111` |
| `@tauri-apps/api/core` (`invoke`, `Channel`) | The frontend's main-chat connection is opened, driven, and torn down entirely through Tauri IPC (`plugin:websocket|*`), never a browser-native `WebSocket` | `desktop/src/shared/api/relayClientSession.ts` |
| `tokio-tungstenite` | The actual OS-level WebSocket transport for both the custom `websocket` Tauri plugin and `buzz-ws-client` | `desktop/src-tauri/src/native_websocket.rs`, `crates/buzz-ws-client/src/connection.rs` |
| `buzz-relay`'s NIP-42/WebSocket connection handling | Both desktop connections are clients of the protocol `architecture-flows-websocket-connection` and `architecture-flows-websocket-authentication` document server-side | see *Relationships* |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| Community switching (`useCommunityInit.ts`) | Calls `relayClient.disconnect()` then `applyCommunity(...)` as the first two steps of redirecting the app to a new community's relay | `desktop/src/features/communities/useCommunityInit.ts` |
| `AppShell`'s lifecycle effects | `useAppShellLifecycleEffects.ts` calls `relayClient.preconnect()` on every fresh mount of the community-scoped subtree | `desktop/src/app/useAppShellLifecycleEffects.ts` |
| Channel history, live subscriptions, publishing, presence | All frontend features that talk to the relay go through the single `relayClient` singleton this node documents | `desktop/src/shared/api/relayClientSession.ts` |

## Reconnection policy (both connections, compared)

| | Backend background session (`native_relay_client.rs`) | Frontend main chat session (`relayClientSession.ts`) |
|---|---|---|
| Base delay | `RECONNECT_BASE_DELAY` = 500ms | `RECONNECT_BASE_DELAY_MS` = 1,000ms (`relayClientTimings.ts`) |
| Growth | doubles each failed attempt | doubles each failed attempt, with +/-25% jitter |
| Ceiling | `RECONNECT_MAX_DELAY` = 30s | `RECONNECT_MAX_DELAY_MS` = 30,000ms |
| Reset | on next successful authenticated connect | after the connection has stayed up for `BACKOFF_RESET_STABLE_MS` |
| Per-subscription CLOSED retry | `CLOSED_RETRY_BASE_DELAY` 1s / `CLOSED_RETRY_MAX_DELAY` 30s | `RETRY_BASE_DELAY_MS` 1,000ms / `RETRY_MAX_DELAY_MS` 30,000ms (`relayClosedRecovery.ts`) |

A source comment on the backend's `RECONNECT_MAX_DELAY` states the 30-second
ceiling deliberately matches the frontend's, "so a relay outage produces one
retry cadence across the app rather than two competing ones" -- but the base
delay is not likewise matched (500ms vs. 1,000ms); only the ceiling and the
CLOSED-retry base/ceiling pair are commented as intentionally coordinated.
Both loops are separately implemented, not shared code -- `buzz-ws-client`
itself has no retry logic at all (see *Public interface*).

The frontend additionally layers a three-phase strategy on top of its own
backoff loop, implemented in `relayReconnectController.ts`: an optimistic
`preconnect()` fast path (bounded by `fastPathTimeoutMs`, 11s in production),
escalation to a build-time-configured transport-recovery hook only if that
fails and a hook is configured (a no-op in this OSS checkout --
`relay_reconnect_hook_configured` / `relay_reconnect_hook`), and finally
waiting on the background exponential-backoff loop up to a `backstopMs`
ceiling (120s in production).

## Community switching triggers a reconnect

Switching the active community does not reload the page (per `CLAUDE.md`'s
own "Community Switching" section); it redirects the relay connection through
five steps:

1. `resetCommunityState()` (`useCommunityInit.ts`) calls `relayClient.disconnect()`
   first -- this nulls the client's cached `relayUrl`, closes the current
   socket, and sets connection state to `"idle"`.
2. `useCommunityInit` calls `applyCommunity(...)`, invoking the `apply_workspace`
   Tauri command.
3. `apply_workspace` (`desktop/src-tauri/src/commands/workspace.rs`) writes the
   new relay URL into `AppState.relay_url_override`.
4. Once `applyCommunity` resolves, `App.tsx` re-renders `<AppReady key={communityKey}>`;
   the changed key forces React to unmount and remount the entire
   community-scoped subtree.
5. The freshly-mounted `AppShell`'s lifecycle effect
   (`useAppShellLifecycleEffects.ts`, empty dependency array, so it fires on
   every remount) calls `relayClient.preconnect()`, which re-fetches the relay
   URL -- now reflecting the new override from step 3 -- and opens a fresh
   socket.

There is no separate "connection singleton" distinct from `relayClient`
itself: it is both the thing disconnected in step 1 and the thing reconnected
in step 5, and `useCommunityInit.ts`'s own `resetCommunityState()` names it
as the canonical example of a community-scoped singleton that must be reset
on every switch.

## Representative verification

- **Backend reconnect backoff:** `retry_delay_grows_and_stops_at_the_ceiling`
  and the neighboring CLOSED-retry tests in
  `desktop/src-tauri/src/native_relay_client_tests.rs` exercise the delay
  growth and ceiling this node describes for the backend background session.
- **Frontend reconnect scheduling policy:** `relayReconnectPolicy.test.mjs`
  (e.g. "baseline scenario schedules a reconnect", "terminal session refuses
  to schedule", "pending reconnect timer suppresses scheduling another")
  covers the decision logic around when `RelayClient` schedules a reconnect
  attempt at all.
- **Frontend three-phase reconnect controller:**
  `relayReconnectController.test.mjs` (e.g. "escalation fires only when fast
  path fails and hook is configured", "escalation skipped when hook not
  configured", "backstop fires onBackstop, not onSuccess") covers the
  fast-path/escalation/backstop sequence described in *Reconnection policy*.
- **Per-subscription CLOSED retry:** `relayClosedRecovery.test.mjs` and
  `relayClosedPolicy.test.mjs` cover the retry base/ceiling this node compares
  against the backend's matching constants.
- **Community-switch relay reachability probe (adjacent, not this node's main
  path):** `desktop/src/features/communities/relayProbe.test.mjs` covers the
  one-shot raw-`WebSocket` reachability check used by the add/edit-community
  form -- a separate, short-lived socket from the two this node documents,
  named here only because it lives beside the community-switch code path in
  *Community switching triggers a reconnect*.

These are unit tests exercising the policy/decision logic in isolation
(no live relay); this node makes no claim about end-to-end coverage of a real
reconnect against a running relay.

## Boundary

This node does not describe:
- The relay-side WebSocket connection lifecycle and NIP-42 authentication
  protocol themselves (admission gates, challenge generation, ban/allowlist/
  membership checks) -- see `architecture-flows-websocket-connection` and
  `architecture-flows-websocket-authentication`, which this node `implements`/
  `references` rather than restates.
- The desktop container's full technology and interface boundary (frontend
  stack, IPC surface, managed-agent subprocess spawning, identity storage,
  media proxy, deployment) -- see `architecture-containers-desktop`, of which
  this component is `part-of`.
- The huddle (voice channel) audio signaling socket
  (`desktop/src-tauri/src/huddle/relay_api.rs`) -- a separate connection that
  also uses `buzz-ws-client`'s `connect_authenticated`, but is out of scope
  for this single-idea node.
- The internal-build-only VPN/transport-recovery hook's own implementation --
  named here only as the reconnect controller's phase-2 escalation step; it
  is a no-op in this OSS checkout.
- NIP-98 HTTP authentication used by desktop's `/query` and `/events` HTTP
  bridge calls (`relay.rs`'s `build_nip98_auth_header`) -- a separate,
  non-WebSocket auth path.

## Relationships

- `part-of`: `architecture-containers-desktop` -- this component is a
  constituent part of the desktop container; its own claims (URL resolution,
  connection lifecycle) are downstream of and constrained by that container's
  already-documented technology and interface boundary.
- `implements`: `architecture-flows-websocket-authentication` -- desktop's
  frontend independently reimplements the same NIP-42 challenge/response
  shape that node documents (its own AUTH event construction, not a shared
  call into `buzz-ws-client`'s equivalent), making this node a concrete
  client-side realization of that flow.
- `references`: `architecture-flows-websocket-connection` -- supporting
  context on the relay-side connection lifecycle desktop's connections are a
  client of; no ownership or currency dependency is implied, since that node
  describes server-side behavior this node's claims do not depend on staying
  unchanged.

Both targets were confirmed present in `origin/launchpad`'s corpus tree at the
recorded revision (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`),
not merely in this task's own worktree.

## Scope and omissions

**This node covers** how the desktop app resolves a relay URL, opens and
authenticates its own WebSocket connection(s) to a relay, retries on failure,
and redirects that connection when the active community changes -- as one
platform-integration component of the desktop container.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay-side connection lifecycle and NIP-42 protocol | `architecture-flows-websocket-connection`, `architecture-flows-websocket-authentication` |
| The desktop container's full architecture | `architecture-containers-desktop` |
| Huddle audio's own signaling protocol | Not yet in this corpus |
| NIP-98 HTTP auth for the `/query`/`/events` HTTP bridge | Not yet in this corpus |
| The internal-build VPN/transport-recovery hook's own behavior | Not yet in this corpus; it is closed-source and a no-op in this OSS checkout |
| Whether a `platforms`-surface template should exist, and what shape it should require | A future corpus-standards task; this node follows `component.md`'s shape as the closest existing analog |

**Expected but not verified when this node was written:**

- **Whether the 500ms-vs-1,000ms base-delay mismatch between the backend and
  frontend reconnect loops is intentional or an oversight.** Both files
  comment that the 30-second *ceiling* and the CLOSED-retry base/ceiling pair
  are deliberately matched; neither file's comments address the base delay
  itself, so this node reports the discrepancy as observed rather than
  explaining it.
- **Why desktop maintains two independently-implemented client connections
  (and two independently-implemented NIP-42 AUTH-event builders) instead of
  having the frontend's main chat connection call into `buzz-ws-client`
  directly, the way the backend background session and huddle audio do.**
  A plausible reason -- the frontend session needs a browser-callable IPC
  surface that a Rust-native `NostrWsConnection` does not provide directly --
  was not confirmed against any design document or issue discussion.
- **Numeric precision of the reconnect timing constants beyond what was read
  directly** (e.g. whether `AUTH_TIMEOUT_MS` = 25,000ms in
  `relayClientTimings.ts` interacts with the relay's own auth timeout as
  documented in `architecture-flows-websocket-authentication`) was not cross-
  checked against that node's own numbers.
