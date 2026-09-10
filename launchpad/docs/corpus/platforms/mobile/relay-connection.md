---
id: platforms-mobile-relay-connection
type: platforms
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
  - statement: "No platforms-specific corpus template exists in launchpad/docs/corpus/templates/ at the recorded revision, so this node borrows the required-sections shape of the merged architecture-component.md template (C4 Component diagram + arc42 Building Block View) while using type: platforms rather than that template's own type: architecture, per this Feature's settled platforms/** convention."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz batch dispatch convention for Feature #614 platforms/** documents (no platforms-specific template issue has landed as of this revision)"
  - statement: "RelaySocket (mobile/lib/shared/relay/relay_socket.dart) is documented in its own file comment as the low-level websocket connection handling connect, NIP-42 challenge/response authentication, and send/receive of JSON frames, and explicitly states it does NOT handle reconnection, which is RelaySessionNotifier's job."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_socket.dart"
  - statement: "RelaySocket.connect() opens an IOWebSocketChannel to the configured wsUrl, awaits channel.ready, transitions to SocketState.authenticating, and completes only after an AUTH challenge/response round trip succeeds or an 8-second timer (_authTimeout) fires; any channel-open failure disconnects immediately and reports it via onDisconnected."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_socket.dart"
  - statement: "On receiving an AUTH challenge, RelaySocket decodes the bech32 nsec to a hex private key, builds a kind:22242 event (EventKind.auth) tagged ['relay', wsUrl] and ['challenge', challenge], signs it with nostr.Event.from, and sends it back as an AUTH frame; the relay's OK response for that specific event id completes or fails the pending auth completer, and a non-nsec or invalid-nsec state fails auth immediately without contacting the relay."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_socket.dart"
      - "mobile/lib/shared/relay/nostr_models.dart"
  - statement: "RelaySessionNotifier.build() auto-connects (via Future.microtask(() => _connect(config))) whenever the watched authProvider reports AuthStatus.authenticated and the watched relayConfigProvider has a non-null nsec, and otherwise leaves the session in SessionStatus.disconnected."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "RelaySessionNotifier owns all reconnection: after a disconnect (other than an explicit RelayAuthRejectedException) it schedules a retry via a timer starting at a 1000ms base delay and doubling on each successive attempt up to a 30000ms ceiling, resetting the delay back to the base once a connection succeeds; an auth-rejected disconnect cancels any pending reconnect timer and leaves the session in SessionStatus.disconnected instead of retrying."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "A successful (re)connection replays every currently-registered live subscription, each re-sent with its filter's `since` shifted back by a 5-second skew from the last event it saw (to catch events missed during the outage), in batches of 8 with a 50ms delay between batches, and the most recently registered visible-channel owner's subscriptions are sorted to the front of the replay order."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "A relay CLOSED message is classified by classifyRelayClosed into rate-limited (message prefix 'rate-limited:'), terminal (prefixes including 'restricted:', 'auth-required:', 'blocked:', 'invalid:', 'pow:', 'duplicate:', 'unsupported:', and two specific 'error:' messages), or retryable (anything else); a terminal CLOSED removes the subscription and invokes its onClosed callback without retrying, while a retryable or rate-limited CLOSED schedules a per-subscription retry with exponential backoff (base delay doubling per attempt, capped at the same 30000ms ceiling used for socket reconnection) and, for rate-limited CLOSEDs, additionally arms the shared RelayRateLimitGate."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_closed_policy.dart"
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "RelayRateLimitGate is a session-owned backpressure gate: activate(retryInSeconds) extends its expiry but never shortens an already-active window, parses the relay's 'retry in Ns' hint capped at 300 seconds, falls back to a 10-second default window when no hint is parseable, and treats an explicit non-positive hint (e.g. 'retry in 0s') as opening no window at all rather than the previous behavior of forcing the default window regardless; callers await wait() before sending further REQ/query traffic while the gate is active."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_rate_limit_gate.dart"
  - statement: "RelayConfig derives both the websocket URL (wsUrl) and the HTTP base URL (baseUrl) from a single stored origin sourced from the active Community's relayUrl, falling back to a compile-time Env.relayUrl (default http://localhost:3000, overridable via --dart-define=BUZZ_RELAY_URL) when no community is active; baseUrl canonicalizes a stored ws/wss scheme to http/https so every HTTP-consuming caller (query bridge, media upload, Blossom auth) sees a consistent origin regardless of which onboarding path (device pairing vs. invite link) persisted it."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "The relay session's one-shot HTTP query bridge (RelaySessionNotifier.queryRelay, POST /query) authorizes each request with a NIP-98-style header built by buildNip98AuthHeader (mobile/lib/shared/relay/relay_session_auth.dart, a part file of relay_session.dart): a kind:27235 event tagged with the URL, HTTP method, a SHA-256 payload hash, and a random nonce, base64-encoded into an `Authorization: Nostr <...>` header -- a separate authentication mechanism from the websocket's kind:22242 NIP-42 AUTH challenge/response."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session_auth.dart"
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "RelaySessionNotifier exposes onAppPaused()/onAppResumed()/reconnect() as public methods that a caller drives; AppLifecycleNotifier (mobile/lib/shared/relay/app_lifecycle_provider.dart) is the current caller, translating Flutter's AppLifecycleState transitions and connectivity_plus network-restore events into calls to those methods, but that translation logic -- which lifecycle states map to which call, and the app-lifecycle transition behavior itself -- is a separate concern from the connection/auth/reconnect mechanics this node documents."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/app_lifecycle_provider.dart"
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "Issue #1259's sibling task, launchpad-26/buzz#1253, is titled 'document platforms/mobile/application-lifecycle.md' and targets the same mobile/lib/shared/relay/ area for the app's own lifecycle-transition behavior, so this node's boundary excludes AppLifecycleNotifier's internal state-transition logic to avoid duplicating that task's scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1253 (sibling task title and target path, read via gh issue view)"
  - statement: "Automated test coverage exists for this area as separate files: mobile/test/shared/relay/relay_session_test.dart, mobile/test/shared/relay/relay_socket_liveness_test.dart, mobile/test/shared/relay/relay_closed_policy_test.dart, mobile/test/shared/relay/relay_rate_limit_gate_test.dart, and mobile/test/shared/relay/relay_config_test.dart; their existence was confirmed by directory listing, not read in full detail."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/relay/relay_session_test.dart"
      - "mobile/test/shared/relay/relay_socket_liveness_test.dart"
      - "mobile/test/shared/relay/relay_closed_policy_test.dart"
      - "mobile/test/shared/relay/relay_rate_limit_gate_test.dart"
      - "mobile/test/shared/relay/relay_config_test.dart"
  - statement: "The architecture-containers-mobile corpus node (launchpad/docs/corpus/architecture/containers/mobile.md), present on origin/launchpad, names mobile/lib/shared/relay/ under its own 'Implementation paths' section as 'relay WebSocket connection, session/reconnect handling, Nostr event/model definitions (EventKind), Blossom media upload/auth', making it the container-level node this component-level node decomposes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
relationships:
  - type: part-of
    target: architecture-containers-mobile
---

# Mobile relay connection: component view

This node decomposes one part of the `architecture-containers-mobile`
container: the WebSocket connection the mobile app maintains to its active
community's Buzz relay -- how it connects, authenticates, reconnects, and
recovers from back-pressure and subscription failures. It answers the
question "how does the mobile app actually stay connected to its relay, and
what happens when that connection breaks?" It does not describe the app's
lifecycle-transition policy (when to pause/resume the connection based on
foreground/background state) -- see *Boundary* below.

No `platforms`-specific corpus template exists yet at the recorded revision
(see the `TEAM_KNOWLEDGE` evidence entry above). This node's shape borrows
the *required sections* of the merged `architecture-component.md` template
(C4 Component diagram + arc42 §5 Building Block View), substituting
`type: platforms` for that template's own `type: architecture`, per this
Feature's settled convention for documents under `platforms/**`.

## Notation legend

| Shape | Meaning |
|---|---|
| Rounded box | A building block documented in this node |
| Rectangle | An external system or a collaborator outside this node's scope |
| Solid arrow | Direct call / data flow |
| Dashed arrow | Callback / event notification |

## Component diagram

```mermaid
flowchart TB
    subgraph RelaySessionNotifier["RelaySessionNotifier (relay_session.dart)"]
        direction TB
        Reconnect["reconnect scheduling\n(exponential backoff)"]
        Replay["subscription replay\n(on reconnect / CLOSED retry)"]
        ClosedPolicy["CLOSED classification\n(relay_closed_policy.dart)"]
        RateGate["RelayRateLimitGate\n(relay_rate_limit_gate.dart)"]
    end

    Socket("RelaySocket\n(relay_socket.dart)")
    Config("RelayConfig /\nRelayConfigNotifier\n(relay_provider.dart)")
    Nip98["buildNip98AuthHeader\n(relay_session_auth.dart)"]
    Lifecycle["AppLifecycleNotifier\n(app_lifecycle_provider.dart)"]
    Relay[["Buzz relay\n(WebSocket + HTTP /query)"]]

    Config -- "wsUrl, nsec" --> RelaySessionNotifier
    RelaySessionNotifier -- "owns / (re)creates" --> Socket
    Socket -- "connect, NIP-42 AUTH\n(kind:22242)" --> Relay
    Relay -. "onConnected / onDisconnected /\nonMessage" .-> Socket
    Socket -. "onConnected / onDisconnected" .-> RelaySessionNotifier
    RelaySessionNotifier --> Reconnect
    RelaySessionNotifier --> Replay
    RelaySessionNotifier --> ClosedPolicy
    RelaySessionNotifier --> RateGate
    RelaySessionNotifier -- "POST /query\n+ NIP-98 header" --> Nip98
    Nip98 --> Relay
    Lifecycle -- "onAppPaused / onAppResumed" --> RelaySessionNotifier
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| `RelaySocket` | Owns the raw WebSocket lifecycle: connect, NIP-42 (kind:22242) challenge/response auth, send/receive JSON frames, disconnect. Explicitly does not reconnect. | `connect()`, `send(payload)`, `disconnect()`, `dispose()`, plus `onMessage`/`onConnected`/`onDisconnected` callbacks supplied by its owner | `mobile/lib/shared/relay/relay_socket.dart` |
| `RelaySessionNotifier` | Orchestrates the session: owns the current `RelaySocket`, decides when to (re)connect, replays live subscriptions after an outage, tracks pending publishes/history requests, and exposes the app-facing `SessionState`. | `queryRelay`, `fetchHistory`, `subscribe`/`subscribeWithStatus`, `publish`, `reconnect()`, `onAppPaused()`/`onAppResumed()`; state via `relaySessionProvider` | `mobile/lib/shared/relay/relay_session.dart` |
| `RelayConfig` / `RelayConfigNotifier` | Derives the WebSocket URL and HTTP base URL the session connects to, from the active `Community` (or a compile-time `Env.relayUrl` fallback), canonicalizing `ws(s)`/`http(s)` schemes. | `relayConfigProvider` (Riverpod), `RelayConfig.wsUrl`/`baseUrl` | `mobile/lib/shared/relay/relay_provider.dart` |
| CLOSED classification (`classifyRelayClosed`, `parseRateLimitRetrySeconds`) | Classifies a relay `CLOSED` message as retryable, rate-limited, or terminal, and extracts a `retry in Ns` hint when present, so `RelaySessionNotifier` knows whether and how long to back off a given subscription. | `classifyRelayClosed(message)`, `parseRateLimitRetrySeconds(message)` | `mobile/lib/shared/relay/relay_closed_policy.dart` |
| `RelayRateLimitGate` | Session-owned back-pressure gate: activates a window when the relay signals rate-limiting, never shrinks an active window, and lets callers `await wait()` before sending further REQ/query traffic. | `activate(retryInSeconds)`, `wait()`, `isActive`, `remainingMs()`, `reset()` | `mobile/lib/shared/relay/relay_rate_limit_gate.dart` |
| `buildNip98AuthHeader` | Builds the NIP-98-style (kind:27235) `Authorization` header for the one-shot HTTP `/query` bridge -- a separate auth mechanism from the WebSocket's NIP-42 AUTH. | `buildNip98AuthHeader({method, url, bodyBytes, nsec})` | `mobile/lib/shared/relay/relay_session_auth.dart` |

## Boundary

This node does not describe:
- The mobile container's own deployment topology, ownership boundary, or its
  other subsystems (media upload/download, deep links, crypto, community
  storage) -- see the `architecture-containers-mobile` node for the
  container as a whole.
- App-lifecycle-transition behavior itself: which `AppLifecycleState`
  transitions map to which of `RelaySessionNotifier`'s public calls, and any
  policy around when the app chooses to pause or resume the connection. That
  is `AppLifecycleNotifier`'s own logic and is sibling task
  `launchpad-26/buzz#1253`'s scope (`platforms/mobile/application-lifecycle.md`),
  not this node's.
- Class/function-level design beyond the public interface named in the table
  above -- e.g. `RelaySessionNotifier`'s internal buffering/dedup fields are
  implementation detail, not a claim this node makes about the component's
  responsibility or interface.
- The wire-level Nostr event/filter model (`NostrEvent`, `NostrFilter`,
  `EventKind`) beyond the two kind numbers (`22242`, `27235`) this node's
  claims depend on directly.
- The relay-side implementation of NIP-42 auth, rate limiting, or the
  `/query` HTTP bridge -- owned by `buzz-relay`/`buzz-core` in this
  repository, not this container.

## Relationships

- part-of: architecture-containers-mobile

## Scope and omissions

**This node covers** the mobile app's own relay WebSocket connection
component: how `RelaySocket` connects and performs NIP-42 authentication, how
`RelaySessionNotifier` owns reconnection (exponential backoff, subscription
replay), how a relay `CLOSED` message is classified and retried per
subscription, how `RelayRateLimitGate` gates outbound traffic during
back-pressure, how `RelayConfig` derives the connection target, and how the
one-shot HTTP query bridge authenticates separately via NIP-98.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| App-lifecycle-transition policy (foreground/background → connect/disconnect decisions) | `launchpad-26/buzz#1253` (`platforms/mobile/application-lifecycle.md`, not yet authored at this revision) |
| The mobile container as a whole (technology, deployment, other subsystems) | `architecture-containers-mobile` (this node's `part-of` target) |
| Media upload/download, deep links, crypto, community storage | Other `platforms/mobile/*` sibling tasks under Feature `#614`, not yet all filed/authored at this revision |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| The relay-side (server) implementation of NIP-42 auth and rate limiting | `buzz-relay`/`buzz-core` (not a `platforms/mobile` concern) |

**Expected but not verified when this node was written:**

- The five test files cited above were confirmed to exist by directory
  listing but not read in full; this node describes what the production code
  does, not how completely the test suite exercises it.
- `buzz-relay`'s own NIP-42/rate-limit implementation was not opened -- the
  claims here describe only the mobile client's side of the protocol, which
  is this node's stated scope, not a verification that the two sides agree
  on every edge case (e.g. the exact set of `CLOSED` message prefixes the
  relay actually sends).
- Whether Mermaid's flowchart notation faithfully reproduces C4's own
  component-diagram visual conventions was not checked against a rendered
  C4 reference example; this is the same open item the
  `architecture-component.md` template itself flags for any node built from
  its shape.
