# Desktop observability — current state

> Current-state documentation tracked by
> [issue #459](https://github.com/launchpad-26/buzz/issues/459).

This page uses three evidence labels. **Verified** means the cited research or pinned
source establishes the claim. **Verified limitation** means the current implementation
was shown not to provide the capability. **Unknown** means the completed work did not
settle the question; it is not an implementation proposal.

## Component scope and runtime

The desktop client has two in-process runtime surfaces:

- **Native Tauri process.** The `buzz-desktop` Rust executable owns application
  startup and shutdown, OS integration, secret and application-data access, Tauri
  commands and events, native relay WebSockets and HTTP requests, huddle audio/STT/TTS,
  and managed-agent process lifecycle.
- **Frontend runtime.** React runs inside Tauri webviews, including the main window and
  huddle companion windows. It owns rendered error boundaries and toasts, the webview
  console, relay-connection presentation, and frontend state. Tauri invoke calls,
  channels, and named events cross into the native process; they are not an
  observability pipeline.

Managed-agent subprocesses and bundled sidecars are separate processes. They are in
scope only where the native client captures their output or exposes their lifecycle;
their internal instrumentation is not desktop-client instrumentation. The relay is a
separate server runtime covered by the [relay deep dive](relay.md). Mobile is not in
scope.

This is a source-state boundary as well as a process boundary. Research
[#318](https://github.com/launchpad-26/buzz/issues/318) verified that this fork had
published no desktop release and observed one Block-signed upstream installation plus
local source-build data on one machine. The participating members' installed-build
inventory remains **unknown**. Consequently, the findings below describe this
repository and the source builds made from it; they do not imply that an already
installed upstream binary contains the same code.

## Instrumentation mechanisms

The current mechanisms are independent and do not converge:

1. Native code writes free-text diagnostics with `println!` and `eprintln!`. Research
   [#315](../../../Research/315-desktop-stdout-destination.md) counted 402 such source
   sites under `desktop/src-tauri/src`. Production messages commonly use a
   `buzz-desktop:` prefix; some huddle TTS messages add `stage=`, `status=`,
   `reason=`, and a desktop-local `route_id`. There is no common timestamp, severity,
   schema, or correlation envelope.
2. Eleven `tracing::warn!` sites describe managed custom-harness discovery failures.
   The desktop installs neither a `tracing` subscriber nor a Tauri log plugin, so those
   events have no active sink.
3. Frontend code uses `console.*` for developer diagnostics and Sonner `toast.error`
   for user-visible failures. Research
   [#316](../../../Research/316-frontend-error-retention.md) counted 193 console sites
   and 115 error-toast sites. The root React boundary catches render failures and calls
   `console.error`.
4. Tauri command results and named events carry operational errors and state between
   native code and the webviews. Examples include relay connection state, managed-agent
   runtime status, and `huddle-state-changed`. These are live product-state surfaces,
   not retained telemetry.
5. The managed-agent launcher is the one explicit file-log mechanism: it opens an
   app-data log per agent/relay runtime and directs that child process's stdout and
   stderr to the file. It does not redirect the desktop process's own output.

**Verified limitation:** no client-process metrics recorder/exporter, span creation,
trace subscriber/exporter, frontend telemetry SDK, or frontend-to-native console bridge
was found. OpenTelemetry packages present transitively in `Cargo.lock` do not constitute
desktop instrumentation.

## Emitted signals

| Signal | Current semantics and structure | Destination and persistence | Coverage limit |
|---|---|---|---|
| Native logs and errors | Free-text stdout/stderr records, usually prefixed `buzz-desktop:`; values can include errors, paths, pubkeys, event/channel context, or huddle TTS key-value fields. | In a normally launched packaged macOS app, both streams are `/dev/null` and do not enter the unified log. A terminal launch exposes them live in that terminal; nothing product-side retains them. | macOS was measured; Linux and Windows packaged destinations were not tested. A past macOS launch cannot be recovered. |
| Native `tracing` events | Eleven warning events for custom-harness discovery; no desktop spans were found. | Dropped because no subscriber is installed. | They cannot be queried, exported, or correlated in the current runtime. |
| Frontend console records | Browser-console calls with message arguments and, at many sites, arbitrary error objects or domain identifiers. | The attached webview inspector only; no bridge to native stdout, no file, and no after-exit record. | Requires live inspector access and does not capture an already dismissed or past failure. |
| Render and toast errors | The root boundary keeps an `Error` in React state but renders only fixed recovery text; Sonner renders toast text/description in the DOM. | Boundary state lasts only until reload/window destruction. Default toasts disappear after 4 seconds and leave no storage record. Toast text is selectable while present. | No `window.onerror` or `unhandledrejection` handler exists. The root boundary never renders the underlying error text. |
| Spans | **None verified for the desktop runtime.** The `tracing::warn!` calls are events, and no span sites or active subscriber were found. | No span destination or persistence. | There is no trace ID or span ID to join to another component. |
| Metrics | **None verified for client-process observability.** Product data such as archived agent-usage series is application data, not a process metrics surface. | No metrics listener, file, or exporter. | Current evidence cannot supply process rates, latency distributions, resource use, or error counts. |
| Live health/diagnostic state | Relay connection states (`idle`, `connecting`, `connected`, `reconnecting`, `stalled`, `disconnected`); huddle phase, channel IDs, participants, and enabled pipelines; managed-agent readiness plus lifecycle (`starting` through `failed`/`stopped`), PID, error, and log path. | Presented through in-memory frontend/native state and Tauri IPC/events. Managed-agent records can persist `last_error` in `managed-agents.json`; child logs persist separately in app data. | These report current feature state, not a client-wide liveness/readiness contract or historical telemetry. |
| Managed-agent subprocess logs | Plain-text narrative containing start markers and the child process's combined stdout/stderr. | On the measured macOS host: `~/Library/Application Support/xyz.block.buzz.app/agents/logs/`. Nine files (96 KiB) survived app quits and were still present after two days; no expiry was found. | Captures managed-agent subprocesses only, not the Tauri process or webview. Retention beyond the observation is unknown. |

## Export boundaries

**Verified:** the current desktop has no product telemetry exporter. It does not export
logs, errors, spans, or metrics through OTLP or another observability protocol.

Existing boundaries through which current signals or diagnostic state can leave their
origin are:

- the native process's stdout/stderr descriptors, which reach an invoking terminal in
  a terminal launch but `/dev/null` in the measured normal packaged macOS launch;
- the live webview developer console;
- app-data files for managed-agent subprocess logs and persisted managed-agent records;
- Tauri invoke results, channels, and named events between the webview and native
  process; and
- ordinary product network egress: native WebSocket frames, relay event submissions,
  native HTTP requests, and webview-allowed HTTP/WebSocket connections.

The network paths carry Buzz product traffic, not telemetry today. They nevertheless
mark the boundary at which a newly added diagnostic payload would leave the machine.
The current `ncryptsec` egress guard covers eight declared relay-bound product paths,
including all webview relay WebSocket frames, but does not discover an undeclared
telemetry path that contains no literal `/events` URL.

Research [#319](../../../Research/319-desktop-distribution-path.md) separately verified
that every workflow which bundles a desktop app was gated to `block/buzz`, the fork had
no Actions secrets, and its ungated desktop CI job built only the Vite frontend. Thus no
fork-produced packaged artifact was an existing collection source at the evidence
cutoff. This distribution fact does not change local source-build behavior.

## Health and monitorability

The strongest current monitorability surfaces are user-facing and session-local:

- The relay connection state distinguishes pre-connection, connect/auth in progress,
  authenticated connection, reconnect backoff, an open socket with no inbound frames,
  and terminal disconnection. Degraded transient states are delayed for two seconds
  before presentation; recovery and terminal disconnection are surfaced immediately.
- Huddle state distinguishes idle, creating, connecting, connected-but-awaiting
  frontend media confirmation, active, and leaving. Its live snapshot also carries
  parent/ephemeral channel IDs, the huddle thread event ID, participant and agent
  pubkeys, and transcription/TTS state.
- Managed-agent status exposes readiness gaps, runtime lifecycle, PID, current error,
  and a local log path. A child failure can also populate a persisted `last_error`, and
  the retained child log can be read after the desktop exits.
- The root error boundary establishes that React failed to render and offers reload,
  but deliberately exposes neither the exception nor component stack.

These surfaces can answer whether this running webview sees a degraded relay
connection, which huddle phase and participants the native process currently holds, or
whether a managed agent is ready/running/failed and where its child log is. They cannot
answer whether the whole client is healthy, whether a prior frontend/native operation
failed, how often or how slowly a path fails, whether the relay accepted a particular
operation without a domain identifier, or whether any diagnostic output was collected.
There is no client-wide health endpoint, durable incident list, process-uptime signal,
or export-health signal.

## Diagnostic use cases

For a single-user failure, current evidence supports only bounded investigations:

- **Managed-agent failure:** runtime status, persisted `last_error`, exit information,
  and the agent/relay-scoped child log can provide after-the-fact evidence.
- **Reproducible native failure on macOS:** quitting and launching the executable from
  a terminal can expose subsequent stdout/stderr live. It cannot recover the original
  occurrence.
- **Live relay or huddle degradation:** the connection and huddle state surfaces can
  identify the current phase and, for huddles, domain context. Their history is not
  retained as telemetry.
- **Frontend toast failure:** the text can be selected and copied during its four-second
  lifetime. Once dismissed, no application record remains.

An uncaught render failure is not diagnostically self-contained: the user sees static
recovery copy, while the underlying error and component info exist only in the
ephemeral console. A controlled built-frontend exercise raised a real unhandled
rejection and uncaught error; both reached the page error surface, but afterwards
neither string existed in the DOM, `localStorage`, or `sessionStorage`. The exercise did
not render the full Tauri-mocked UI, so it did not runtime-verify toast dismissal or the
root boundary.

## Correlation and context

Current correlation is based on domain data, not distributed trace context:

| Boundary | Available context | Where context is lost |
|---|---|---|
| Frontend ↔ native Tauri | Command name and returned error; named Tauri event; feature payloads such as relay URL, pubkey, event ID, channel ID, managed-agent runtime key, or huddle state. `huddle-state-changed` carries parent/ephemeral channel IDs and participant pubkeys. | No invoke/session request ID, trace ID, or common log envelope joins a console entry to a native print. |
| Desktop ↔ relay | Signed Nostr event IDs, author pubkeys, subscription IDs where present in the protocol, relay URL, channel/community IDs, and timestamps can support a manual data join. | The client sends no `traceparent`. Relay `conn_id`, `trace_id`, and `span_id` are not returned to or recorded by the desktop, so client and relay records are not one trace. |
| Huddle frontend ↔ native | Parent channel ID, ephemeral channel ID, huddle thread event ID, participant/agent pubkeys, phase, and live Tauri state events identify the same active huddle. Some native TTS lines use a local `route_id` to join TTS stages. | The huddle state is session memory, and `route_id` is not a relay correlation identifier. Most native huddle error lines do not carry all huddle identifiers. |
| Huddle desktop ↔ relay | Ephemeral channel ID, pubkey, event ID where emitted, and time can be compared with relay huddle records. | This is a manual domain join. The relay huddle path has no propagated client trace identity; some relay rejection exits also lack member attribution, as documented by the [relay deep dive](relay.md#correlation-and-context). |

The split destinations are themselves a correlation break: frontend console records,
native stdout/stderr, retained child logs, and relay records have no shared client
session identifier.

## Sensitive-data handling

**Verified current exposures and constraints:**

- Native diagnostics include full identity or agent pubkeys at some sites, plus error
  strings and filesystem paths. Frontend console sites frequently pass arbitrary error
  objects and sometimes domain identifiers.
- Managed-agent logs are persistent plain text. Their start markers include agent name
  and pubkey, and their body is unbounded child stdout/stderr. Research #315 deliberately
  did not quote the files because agent output can contain secrets.
- The root boundary's rendered recovery UI does not disclose the underlying exception,
  even though `console.error` receives it.
- The relay egress guard rejects lowercase or uppercase `ncryptsec1` substrings at its
  declared product egress boundaries. Its documented scope intentionally excludes raw
  `nsec`; the frontend has no equivalent guard.
- Research [#317](../../../Research/317-egress-guard-telemetry.md) found no current key
  leak in the key-related native print sites it checked. The two interpolated parsing
  errors were safe on the pinned `nostr` implementations because their display text
  does not echo key input. This was a bounded review, not proof over every print or
  console site.
- There is no current off-machine telemetry destination for these values. That does not
  remove the local disclosure surface of retained agent logs or live consoles.

**Verified limitation:** the egress inventory scans for `/events` and declared guard
calls. A telemetry exporter with neither would be absent from the inventory and pass
unchanged; raw `nsec` is outside the guard's match. No general client diagnostic
redaction or retention policy was established by the completed research, and none is
defined here.

## Known gaps

- **Verified limitation — packaged macOS loss:** native stdout/stderr is discarded and
  absent from the unified log; past app launches are unrecoverable.
- **Verified limitation — frontend loss:** render errors, uncaught errors, unhandled
  rejections, console records, and dismissed toasts have no durable application record.
- **Verified limitation — dropped tracing events:** eleven native warnings have no
  subscriber; no desktop spans exist.
- **Verified limitation — no metrics or export health:** no client-process metrics
  surface, telemetry exporter, or exporter-health signal exists.
- **Verified limitation — split correlation:** frontend, native, child-agent, relay, and
  huddle records share domain identifiers opportunistically but no session or trace
  identity.
- **Verified limitation — narrow egress guard:** the existing control covers declared
  `ncryptsec` relay egress, not an undeclared telemetry boundary or raw `nsec`.
- **Unknown — other packaged platforms:** stdout/stderr destination and survivability
  were not tested on Linux or Windows.
- **Unknown — installed client coverage:** #318 did not obtain a per-member build
  inventory; other members and internally distributed Block builds were not inspected.
- **Unknown — participating platforms:** [#320](https://github.com/launchpad-26/buzz/issues/320)
  measured one macOS 15.7.7 x86_64 host, but the rest of the contributor OS/architecture
  inventory was not collected.
- **Unknown — retention bounds:** managed-agent files survived for two observed days and
  no expiry was found; longer-term deletion behavior and maximum growth were not
  established.
- **Unknown — unreviewed disclosure paths:** #317 did not prove all native print
  interpolations, frontend errors, Tauri command error strings, or agent child output
  free of sensitive material.
- **Unknown — unexercised runtime paths:** the packaged app measurements covered one
  shipped macOS build; the error exercise did not render the full UI; Linux, Windows,
  release-vs-development differences, and representative huddle/client failures were
  not exercised.

## Evidence and verification metadata

- Repository revision:
  [`678008ea49e790ada52e84d54b47f47dd77c6b38`](https://github.com/launchpad-26/buzz/tree/678008ea49e790ada52e84d54b47f47dd77c6b38)
- Evidence cutoff date: 2026-08-22
- Verification methods: pinned source and dependency inspection; source-site
  inventories; a LaunchServices descriptor probe; direct descriptor, parent-process,
  and unified-log inspection of shipped `Buzz.app` 0.5.17 on macOS 15.7.7; inspection
  of persisted managed-agent files; a built-frontend browser exercise with real
  unhandled errors; bounded key-related print/error-display review; GitHub
  release/workflow/secrets and macOS code-signature inspection. No validation or new
  runtime experiment was performed for this deep dive.
- Research evidence:
  [stdout/stderr destination #315](../../../Research/315-desktop-stdout-destination.md),
  [frontend error retention #316](../../../Research/316-frontend-error-retention.md),
  [egress guard and telemetry #317](../../../Research/317-egress-guard-telemetry.md),
  [client-build inventory record #318](https://github.com/launchpad-26/buzz/issues/318),
  [desktop distribution path #319](../../../Research/319-desktop-distribution-path.md),
  and [machine inventory record #320](https://github.com/launchpad-26/buzz/issues/320).
- Pinned implementation evidence:
  [`lib.rs` Tauri runtime and IPC registration](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/lib.rs#L91-L200),
  [`main.tsx` frontend boundary](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src/main.tsx#L78-L132),
  [`RootErrorBoundary.tsx`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src/app/RootErrorBoundary.tsx#L22-L58),
  [`sonner.tsx`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src/shared/ui/sonner.tsx#L7-L28),
  [`native_websocket.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/native_websocket.rs#L124-L336),
  [`managed_agents/storage.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/managed_agents/storage.rs#L35-L104),
  [`managed_agents/runtime.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/managed_agents/runtime.rs#L184-L210),
  [`managed_agents/runtime_types.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/managed_agents/runtime_types.rs#L34-L105),
  [`huddle/state.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/huddle/state.rs#L34-L144),
  and [`egress_guard.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/desktop/src-tauri/src/egress_guard.rs#L1-L54).

Back to the [overview](overview.md). See also [relay](relay.md) and [web](web.md).
