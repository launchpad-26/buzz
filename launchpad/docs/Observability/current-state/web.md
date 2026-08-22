# Web observability — current state

This page records the web client's verified state at the evidence revision. It
describes existing browser signals and boundaries; it does not select a
telemetry destination, transport, policy, or future architecture.

## Component scope and runtime

**Verified boundary.** The component is the Vite-built React single-page
application running in a user's browser tab. The boundary includes:

- application code on the browser main thread, React and TanStack Query error
  handling, and browser-native `fetch`, `WebSocket`, Web Crypto, and IndexedDB
  use;
- the NIP-07 extension interface used for public-key lookup and event signing,
  while the extension itself remains outside the component;
- outbound HTTP, Git smart-HTTP, and Nostr-over-WebSocket calls up to the point
  where the browser hands them to the network.

The relay begins on the server side of those requests and is covered by the
[relay deep dive](relay.md). Browser internals, extensions, proxies, collectors,
the desktop client, and mobile clients are outside this page. The relay can
serve the built SPA from `BUZZ_WEB_DIR`; absent `VITE_RELAY_URL`, the client
derives its relay URL from `window.location`, so that deployment is same-origin
([client URL selection](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/shared/lib/relay-url.ts#L12-L24),
[relay static serving](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/router.rs#L152-L195)).

## Instrumentation mechanisms

The current client has no observability SDK or initialization path. Its
dependency manifest contains React, TanStack Query, Nostr, and UI packages but
no OpenTelemetry, Faro, Sentry, or equivalent library
([manifest](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/package.json#L19-L52)).
The entry point configures React, TanStack Query, theme, tooltip, and toast
providers only
([entry point](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/main.tsx#L1-L36)).

Existing diagnostic mechanisms are local and application-specific:

1. **Browser console:** one app-authored `console.error` call writes the prefix
   `[git-browse]` and the raw tree-or-commit browsing error
   ([source](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/features/repos/ui/RepoDetailPage.tsx#L227-L241)).
   There is no shared logger, event schema, severity configuration, or
   application-added timestamp or correlation field.
2. **Promise and query errors:** transport helpers reject `Error` objects;
   React/TanStack Query consumers turn selected failures into toasts, inline
   banners, or alert text. These are user-facing state, not an exported error
   stream.
3. **Browser-native inspection:** DevTools can display console output, Fetch
   requests, and WebSocket frames for the open tab. The application does not
   persist or forward that inspection data.

Targeted source inspection found no global error boundary, `window.onerror`,
`unhandledrejection` handler, Performance Observer, beacon sender, trace
propagator, or metrics API in `web/src`.

## Emitted signals

| Signal | Verified current semantics and structure | Verified limitation |
|---|---|---|
| Logs | A single raw console error, `"[git-browse]", browseError`, on repository tree or commit-list failure. | No stable fields, levels beyond the console method, session/build identity, export, or coverage of other client operations. |
| Errors | The Nostr query helper rejects named messages for a 10-second timeout, signing/authentication failure, relay `CLOSED`, and WebSocket failure. Invite claim parses relay `error` text or falls back to `HTTP <status>`. UI code displays selected query and invite errors. | WebSocket `error` is collapsed to `"WebSocket connection failed"`; malformed frames and `NOTICE` are ignored; a close before `EOSE` resolves the events accumulated so far. Uncaught render/runtime errors have no app-level capture. |
| Spans | None are created in the web client. | There are no browser span names, timings, attributes, parent context, or exporter. Relay spans are not browser spans. |
| Metrics | None are recorded by the web client. | There are no counters, histograms, gauges, Web Vitals, resource timings, or client-side aggregation/export. |
| Health/diagnostics | Loading/error UI, toast/alert text, and the live browser console/network panels expose local symptoms. | There is no web-client health endpoint, heartbeat, readiness state, diagnostics bundle, or fleet/session status signal. |

The error behavior above is visible in the
[Nostr query implementation](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/shared/lib/nostr-client.ts#L26-L174),
[invite HTTP implementation](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/features/invite/invite-api.ts#L13-L50),
and [invite alert mapping](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/features/invite/ui/InvitePage.tsx#L27-L38).

## Export boundaries

**Current signal export:** none. The client has no telemetry exporter,
collector URL, telemetry endpoint, beacon, or observability-specific request.
Its network traffic is product traffic rather than a logs, traces, or metrics
pipeline.

**Same-origin product boundary.** By default, the WebSocket URL is derived from
the page scheme and host; HTTP relay URLs are derived from that WebSocket URL.
The relay-hosted SPA can therefore use same-origin HTTP and WebSocket requests.
Same-origin Fetch does not require a CORS grant. This available HTTP surface is
not currently a telemetry ingest route.

**Cross-origin product boundary.** `VITE_RELAY_URL` can instead select another
relay origin. HTTP calls derived from it are then subject to browser CORS. At
the evidence revision, the relay uses permissive CORS when
`BUZZ_CORS_ORIGINS` is empty, an explicit origin list when it is valid, and no
allowed origins when a configured list parses to none
([relay CORS implementation](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/router.rs#L438-L462)).
That is a deployment-dependent product API boundary, not evidence that a
cross-origin telemetry receiver exists.

The browser `WebSocket` constructor used by the client accepts no arbitrary
upgrade headers. Consequently the web client cannot put `traceparent` in the
WebSocket handshake. Nostr WebSocket messages are positional JSON arrays with
no header surface, and the current messages contain no trace context
([client construction and messages](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/shared/lib/nostr-client.ts#L33-L103),
[#323 research](../../../Research/323-trace-context-propagation.md#part-4--the-client-asymmetry-checked)).
Ordinary HTTP Fetch requests can carry request headers, but the current client
does not add W3C Trace Context.

For any separate cross-origin browser destination, the completed delivery
research establishes two constraints without making that destination current:
the destination would need browser-compatible CORS (and any deployed
`connect-src` policy would have to permit it), while CORS and a browser-visible
static API key do not authenticate a non-browser writer
([#321 research](../../../Research/321-browser-otlp-delivery.md#finding)).
No repository-defined SPA `connect-src` policy was found; headers added by a
deployment proxy were not inspected.

## Health and monitorability

The relay exposes `/health`, `/_liveness`, and `/_readiness`, but the web client
does not call them and they report relay rather than browser health
([relay routes](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/router.rs#L62-L74)).
Current monitorability is therefore one-tab, interactive diagnosis:

| Current surface | Questions it can answer | Questions it cannot answer |
|---|---|---|
| Inline errors, alerts, and toasts | Did this visible invite or repository operation report a failure, and what message reached its UI handler? | How often does it fail, which build/browser is affected, whether hidden/background operations failed, or whether other users see it. |
| Browser console | Did the repository browse path emit its one diagnostic call; what raw error object existed in this tab? | Client-wide error rate, historical failures after the tab closes, or failures from paths with no console call. |
| DevTools Fetch/WS inspection | Did a request connect, what HTTP status/timing was observed, and which Nostr frames crossed this open socket? | Persistent monitoring, server-side execution after receipt, cross-user comparison, or an automatic join to relay logs/spans. |
| React Query loading/error state | Is a represented query currently loading or failed from the component's perspective? | Overall application readiness, event-loop/resource health, Web Vitals, memory pressure, or a fleet-level health state. |

## Diagnostic use cases

Current evidence can support a user reproducing a repository browse failure and
sharing its banner, console object, or network exchange. It can distinguish
some invite failures through relay sentinel text, a query timeout from the
generic WebSocket error, and an explicit relay subscription rejection from a
successful `EOSE`.

It cannot, from application signals alone:

- detect or aggregate uncaught JavaScript/render failures;
- reconstruct navigation and user actions preceding an error;
- separate DNS, TLS, proxy, relay, and downstream-store causes hidden behind
  the generic WebSocket error;
- quantify latency, error rate, availability, or browser performance;
- determine whether a silent malformed/`NOTICE` frame or early socket close
  caused incomplete query results; or
- compare one browser's operation with relay and peer activity through a
  shared trace.

These are current coverage limits, not implementation proposals.

## Correlation and context

The client has operational identifiers, but no end-to-end observability
identifier:

- Nostr queries create a tab-local subscription id of
  `q-<Date.now().toString(36)>`; the id is present in `REQ`, `EVENT`, `EOSE`, and
  `CLOSED` frames, but is not included in the sole console log or an exported
  record.
- NIP-42 authentication carries a signed event id and public key. Nostr events
  also carry event ids, public keys, and timestamps.
- NIP-98 HTTP authorization signs the URL and method; requests with bodies also
  include a payload digest and random nonce
  ([NIP-98 helper](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/shared/lib/nip98.ts#L18-L47)).
- The relay creates its own connection id and WebSocket server spans
  ([relay WebSocket spans](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/connection.rs#L560-L637)),
  but the browser neither receives that connection id as diagnostic context
  nor sends a `traceparent`. The relay's HTTP request span records the method
  but does not extract browser trace context
  ([relay HTTP span](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/router.rs#L203-L214)).

Thus browser-to-transport association is possible while inspecting a live
request or subscription. Browser-to-relay association is only a manual join on
available identity, channel/subscription context, and time; completed research
found that useful for a small, low-concurrency incident window but ambiguous
for concurrent events from the same identity
([#323 findings](../../../Research/323-trace-context-propagation.md#part-3--what-correlation-with-no-propagation-achieves)).
There is no verified web-to-relay parent/child trace or span link.

## Sensitive-data handling

No telemetry pipeline means there is also no web telemetry redaction,
attribute allowlist, sampling, or retention implementation to describe.
Current diagnostic and product surfaces nevertheless contain data that could
be disclosed if copied, captured, or later collected:

- routes contain invite codes, repository ids, and repository file paths
  ([route definitions](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/app/routes.ts#L3-L9));
- Nostr frames and signed authentication carry public keys, event ids,
  signatures, filters, timestamps, and potentially event content;
- NIP-98 authorization contains a signed event encoding the request URL and
  method, plus a body digest and nonce for body-bearing calls;
- the one console call emits a raw third-party Git browsing error object rather
  than a constrained set of fields, and UI errors can display relay-provided
  strings.

The browser signer keeps its fallback secret key in JavaScript memory for the
page lifetime; durable membership requires NIP-07, whose interface returns a
public key and signed event to the page
([signer boundary](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/web/src/shared/lib/nostr-signer.ts#L20-L105)).
Browser-delivery research verifies the broader browser constraint: a static
credential shipped to page code is visible to that page, and XSS, extensions,
or a compromised dependency can read or modify browser telemetry or use an
ingest endpoint as an exfiltration channel. CORS restricts browser origins; it
does not stop a non-browser client from writing
([#321 failure modes](../../../Research/321-browser-otlp-delivery.md#known-failure-modes-from-the-sources-rather-than-reasoned)).
No new redaction or retention policy is defined here.

## Known gaps and unknowns

### Verified gaps

- No web logs/errors/spans/metrics exporter or observability endpoint exists.
- Error capture is path-specific: one raw console call, selected UI states, no
  global runtime/rejection capture, and silent handling of some WebSocket
  conditions.
- No browser health, Web Vitals, resource, build/version, session, or
  application-readiness signal is emitted.
- No `traceparent`, propagator, shared trace id, or automatic browser-to-relay
  correlation exists. Browser WebSocket upgrade headers are unavailable
  through the platform API.
- No application-defined telemetry filtering, redaction, sampling, retention,
  payload limit, or ingest-authentication behavior exists because there is no
  telemetry pipeline.

### Unknown at the evidence cutoff

- Production values of `VITE_RELAY_URL`, `BUZZ_CORS_ORIGINS`, and any
  proxy-supplied Content Security Policy vary outside the checked-in source and
  were not observed.
- The exact fields exposed by third-party Git errors and browser-specific
  WebSocket failures were not captured in a runtime experiment.
- Browser/extension versions, production build identity, and user/session
  context are not recorded by current signals, so their effect on incidents is
  unknown from those signals.
- No end-to-end browser delivery or trace-correlation behavior was run; the
  completed research was a source and literature survey.

## Evidence and verification metadata

- **Repository revision:** [`678008ea49e790ada52e84d54b47f47dd77c6b38`](https://github.com/launchpad-26/buzz/tree/678008ea49e790ada52e84d54b47f47dd77c6b38)
- **Evidence cutoff date:** 2026-08-22
- **Verification methods:** static inspection of the pinned dependency
  manifest, browser entry point, URL selection, Fetch/WebSocket/authentication
  helpers, user-visible error paths, and relay routing/CORS/span boundaries;
  targeted source searches for logging, telemetry, tracing, metrics,
  performance, global error capture, beacon export, health calls, and CSP;
  review of the completed research below. No browser session, network capture,
  collector, or new telemetry experiment was run.
- **Completed research:** [issue #321](https://github.com/launchpad-26/buzz/issues/321)
  and its [checked-in browser-delivery artifact](../../../Research/321-browser-otlp-delivery.md);
  [issue #323](https://github.com/launchpad-26/buzz/issues/323) and its
  [checked-in trace-context artifact](../../../Research/323-trace-context-propagation.md).

Back to the [overview](overview.md). See also [relay](relay.md) and
[desktop](desktop.md).
