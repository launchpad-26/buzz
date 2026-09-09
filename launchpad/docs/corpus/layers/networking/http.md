---
id: layers-networking-http
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "AGENTS.md states that Buzz's primary API is NIP-29 over WebSocket and that the relay additionally exposes a 'narrow HTTP surface' — NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, workflow webhooks at /hooks/{id}, Blossom media, git smart HTTP, git policy hooks, and health probes — whose paths 'all preserve the same host-derived community boundary.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md instructs contributors to model new operations as Nostr event kinds rather than endpoint-specific JSON APIs, and reserves HTTP for things that 'genuinely need an HTTP-only surface': media upload/download, webhooks, git smart HTTP, NIP-11/NIP-05 metadata, health checks, and the generic Nostr bridge endpoints."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CLAUDE.md at the repository root is a symbolic link to AGENTS.md, so the two names address one file and the 'prefer Nostr events over new HTTP endpoints' position has a single source rather than two agreeing copies that could drift."
    entry_class: FACT
    evidence:
      - "list_directory_long('CLAUDE.md') -> CLAUDE.md is a symlink whose target is AGENTS.md"
      - "AGENTS.md"
  - statement: "build_router composes the relay's whole HTTP surface from five parts — an api_router of individually registered routes, a media_router, git_router, git_policy_router, and an optional admin_router — merged into one axum Router, with an SPA fallback_service attached when either bundle directory is configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The same axum route table serves both the HTTP surface and the WebSocket upgrade: '/' is registered as a normal GET route whose handler, nip11_or_ws_handler, content-negotiates between an admin SPA document, a NIP-11 JSON document, and a WebSocket upgrade depending on the Host and Accept headers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Request body limits are applied per sub-router rather than once for the whole surface: api_router takes a flat 1 MiB RequestBodyLimitLayer, media_router takes the larger of the configured max_image_bytes and max_video_bytes, git_router takes config.git_max_pack_bytes, and git_policy_router takes 1 MiB."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "Three cross-cutting layers are applied once over the merged router, in the order metrics then trace then CORS: middleware::from_fn(track_metrics), http_trace_layer(), and build_cors_layer(&state.config.cors_origins)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "build_cors_layer returns CorsLayer::permissive() when the configured origins list is empty, and when the list is non-empty but no entry parses as a HeaderValue it logs an error and returns a bare CorsLayer::new() rather than falling back to permissive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The origins list is read from the BUZZ_CORS_ORIGINS environment variable, comma-split, trimmed, with empty entries filtered out, so an unset variable yields an empty list."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "track_metrics labels each request with the matched axum route pattern rather than the raw URI, and returns early without recording anything when the matched path starts with '/_', equals '/health' or '/metrics', or when no route matched at all — the stated reason being that unmatched scanner traffic would otherwise create unbounded label cardinality."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "Every request that track_metrics does record increments http_requests_total and observes http_request_latency_ms under the same three labels: code (exact HTTP status), caller (from the Istio x-envoy-downstream-service-cluster header, validated to at most 64 alphanumeric/hyphen/underscore bytes and otherwise 'unknown'), and action (the matched route pattern)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "http_trace_layer builds a tower_http TraceLayer whose span factory, make_http_span, opens an info-level span named 'http.request' on target buzz_relay with otel.kind='server' and the request method as a field."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "build_health_router is a second, separate Router carrying /_liveness, /_readiness, /_status and /_mesh, and its doc comment states it has 'No metrics middleware, no auth, no CORS, no body limit.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay's serve() function binds the health router on config.health_port as its own TCP listener, separate from the main surface bound on config.bind_addr, and on Unix additionally serves a clone of the same main router over a Unix domain socket at config.uds_path when configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The Prometheus scrape endpoint is not a route on either router: relay_metrics::install opens its own HTTP listener on config.metrics_port via PrometheusBuilder::with_http_listener."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "The main router's TCP listener is served with into_make_service_with_connect_info::<SocketAddr>, while the Unix-domain-socket listener is served with plain into_make_service, so a ConnectInfo extension is present on TCP requests and absent on UDS requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "git_policy_router layers a require_localhost middleware that rejects any request whose ConnectInfo peer address is not loopback with 403 'internal endpoint: localhost only', and treats a missing ConnectInfo extension as non-loopback."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "Because require_localhost reads its verdict from the ConnectInfo extension and defaults to false when that extension is absent, /internal/git/policy is rejected on the Unix-domain-socket listener — which is served without connect info — as well as from any non-loopback TCP peer."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.75
  - statement: "The SPA fallback checks the admin host first and returns 404 for anything on that host outside a fixed allowlist of document and asset paths, so an admin-host request can never fall through to the public web bundle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Documents and assets served on the admin host carry a fixed Content-Security-Policy constant, and a unit test asserts that constant never contains 'unsafe-inline' or 'unsafe-eval'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Unit tests in router.rs exercise the surface's routing predicates and header behaviour directly through build_router — that admin-host documents and assets carry the admin CSP, that the public host's responses do not, that the admin bundle directory is not browsable, and that the invite landing path is always served while the git web GUI requires opt-in."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "A router.rs test asserts that a datastore span opened inside a handler shares the trace id of the surrounding http.request span and names it as its parent, so the HTTP trace layer is the root of the per-request trace rather than a sibling of it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay's HTTP surface is deliberately not a general-purpose REST API but a set of narrow, purpose-specific doors, because AGENTS.md both states the reservation rule and gives the standing reason — a Nostr event kind grants realtime fan-out, NIP-29 scoping and the existing auth pipeline that a bespoke endpoint would each have to re-earn."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "Issue #1127's definition of done requires the node to define the term in one sentence before deeper explanation, state boundaries and non-goals, link to related concepts, implementation and verification without duplicating their canonical content, and use examples only to clarify rather than to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1127 definition of done"
  - statement: "Thirteen sibling tasks under Feature #609 own the rest of the networking layer — among them #1134 (websocket), #1133 (tls), #1131 (request-routing), #1126 (host-routing) and #1124 (external-webhooks) — so the boundaries this node draws against those subjects name real filed issues rather than hypothetical ones; none is merged on origin/launchpad at the recorded revision, so none may be a relationship target."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue list --repo launchpad-26/buzz --search 'layers/networking in:title', run while authoring this node"
relationships:
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: verification-contracts-http
  - type: references
    target: capabilities-git-smart-http
  - type: references
    target: capabilities-media-blossom
  - type: references
    target: layers-observability-metrics
  - type: references
    target: layers-configuration-relay-configuration
---

# HTTP as a networking-layer surface

**HTTP is the relay's secondary transport: one merged `axum` route table, served
beside the WebSocket upgrade on the same listener, carrying the small set of
operations that genuinely cannot be a Nostr event.** Everything else on this page
follows from that one sentence — why the surface is small, what is on it, and which
properties every path on it shares whether or not the endpoint's author thought
about them.

This node is about the surface *as a surface*. Individual endpoints have their own
canonical nodes and this one does not restate them; see **Boundary and non-goals**
below for the split, which is deliberate and precise.

## Definition

The HTTP surface is the set of routes `build_router` assembles in
`crates/buzz-relay/src/router.rs`, plus the two listeners that deliberately sit
outside it. `build_router` merges five parts — an `api_router` of individually
registered routes, a `media_router`, a `git_router`, a `git_policy_router`, and an
`admin_router` present only when admin configuration exists — and attaches an SPA
`fallback_service` when a bundle directory is configured. Three layers are then
applied once over the merged whole, in order: metrics, tracing, CORS.

**What it is not.** It is not a REST API for Buzz's domain. `AGENTS.md` states the
rule plainly: model new operations as Nostr event kinds, and reserve HTTP for what
"genuinely need[s] an HTTP-only surface". The surface exists because a handful of
things cannot be expressed as a signed event on a socket — a browser fetching
metadata before it can open a socket, `git` speaking its own wire protocol, a blob
that will not fit in a frame, a third-party service POSTing a webhook, a
Kubernetes probe. The category, not the convenience, is the admission criterion.

**Disambiguation.** "HTTP" here means the relay's inbound HTTP surface. It is not
the transport underneath the WebSocket upgrade (that handshake is HTTP, but the
resulting connection is #1134's subject), and it is not the relay's outbound HTTP
calls to third-party services.

## What is on it

Grouped by why each group is here rather than by route. Route-by-route detail is in
`router.rs` itself, which is short enough to read and is the only inventory that
cannot drift.

| Group | Why it cannot be an event |
|---|---|
| NIP-11 / NIP-05 metadata, `/info` | A client reads them *before* it has a relay connection. |
| The Nostr bridge — `POST /events`, `/query`, `/count` | Callers without a socket need the same operations; the bridge is the exception AGENTS.md names as generic rather than endpoint-specific. |
| Blossom media upload and download | Blob bytes, not frames. |
| Git smart HTTP | An unmodified `git` client speaks its own protocol. |
| Webhook trigger | An external service initiates; `router.rs` marks the route "secret-authenticated, no NIP-98". |
| Health probes | Orchestrator probes are HTTP GETs, not Nostr clients. |
| Operator, invite, moderation, workflow-run and admin routes | Browser-originated management traffic. |
| SPA and static asset serving | A browser must be handed documents before it can run any client code. |

The one route worth naming individually is `/`, because it is where the two
transports meet: `nip11_or_ws_handler` is registered as an ordinary `GET` and
content-negotiates between an admin SPA document, a NIP-11 JSON document, and a
WebSocket upgrade, based on `Host` and `Accept`. Registering `/` explicitly is also
what keeps it away from the SPA fallback.

## Shared properties

These are the properties a new route inherits whether or not its author considered
them — the reason this node exists as a layer concept rather than as a list.

**Body limits are per sub-router, not per surface.** `api_router` gets a flat 1 MiB;
`media_router` gets the larger of the configured image and video maxima; `git_router`
gets `git_max_pack_bytes`; `git_policy_router` gets 1 MiB. A route added to
`api_router` silently inherits 1 MiB, which is correct for a JSON endpoint and wrong
for anything streaming bytes — that is the choice each new group is really making
when it picks which sub-router to join.

**One CORS layer, and its failure mode is worth knowing.** `build_cors_layer` returns
a permissive layer when `BUZZ_CORS_ORIGINS` is unset or empty. When the variable is
set but *no* entry parses as a header value, it logs an error and returns a bare
`CorsLayer::new()` — it refuses to fall back to permissive. A misconfigured origins
list therefore fails closed and looks like broken browser clients, not like an open
relay.

**One metrics middleware, with a deliberate blind spot.** `track_metrics` labels by
the *matched route pattern*, never the raw URI, and skips recording entirely for
`/_*`, `/health`, `/metrics`, and any request that matched no route. The stated
reason is label cardinality: 404 scanner traffic would otherwise mint a new series
per probed path. The consequence to hold onto is that **unmatched traffic is
invisible in `http_requests_total`** — the counter answers "how is each known route
performing", not "what is hitting this relay". `layers-observability-metrics` owns
the metrics layer itself.

**One trace root.** `make_http_span` opens an `http.request` server span per request,
and a test in `router.rs` asserts a datastore span opened inside a handler inherits
that span's trace id and names it as its parent. Anything a handler instruments
lands under the HTTP span rather than beside it.

**Not everything HTTP is on this surface.** Two listeners are outside it by design:
`build_health_router` serves `/_liveness`, `/_readiness`, `/_status` and `/_mesh` on
`health_port` with — in its own words — "No metrics middleware, no auth, no CORS, no
body limit", and the Prometheus scrape endpoint is not a route at all but a listener
`relay_metrics::install` opens on `metrics_port`. A probe or a scrape reaching the
main port is not the same request as one reaching its own port, and only the latter
is what the deployment is configured to use.

**A third listener changes request context.** On Unix, the same router is also served
over a Unix domain socket. The TCP listener is served with
`into_make_service_with_connect_info::<SocketAddr>`; the UDS listener is served with
plain `into_make_service`. Any code reading `ConnectInfo` therefore sees a peer
address on TCP and nothing on UDS. `require_localhost`, which gates
`/internal/git/policy`, treats a missing `ConnectInfo` as non-loopback and rejects —
so that endpoint is unreachable over UDS as well as from remote TCP peers. That
consequence is recorded as an INFERENCE rather than a FACT: it follows from two files
read separately and no test exercises the UDS path.

```mermaid
flowchart TB
  subgraph main["bind_addr (+ optional UDS) — one merged router"]
    direction TB
    L["CORS → trace → metrics"] --> R
    subgraph R["merged routes"]
      A["api_router (1 MiB)"]
      M["media_router (image/video max)"]
      G["git_router (git_max_pack_bytes)"]
      P["git_policy_router (1 MiB, loopback only)"]
      D["admin_router (optional)"]
      F["SPA fallback: admin host first"]
    end
  end
  subgraph out["deliberately outside"]
    H["health_port — no metrics, no CORS, no body limit"]
    Pm["metrics_port — its own listener, not a route"]
  end
```

## Why this matters to a reader

- **Adding an endpoint.** The question is not "where does the route go" but "is this
  in one of the categories HTTP is reserved for". If it is not, `AGENTS.md`'s answer
  is an event kind. If it is, the sub-router chosen decides the body limit inherited.
- **Reading a metric or a trace.** `http_requests_total` covers matched routes only;
  health and metrics traffic is on other ports entirely. Both facts change what an
  absence in a dashboard means.
- **Operating the relay.** Three or four listeners exist, not one, and
  `BUZZ_CORS_ORIGINS` fails closed rather than open when it is malformed.

## Boundary and non-goals

Several merged nodes already own pieces of this surface. **This node is the layer
concept — the surface as a whole and its shared properties — and does not restate
any of their canonical claims.**

| Owned elsewhere | Owner |
|---|---|
| The `POST /events` request lifecycle end to end — tenant binding, NIP-98 auth, replay, admission, ingest, status mapping | `architecture-flows-http-event-submission` |
| The community-boundary test obligation on `POST /events`, its verifying test, and its gated enforcement status | `verification-contracts-http` |
| The git smart-HTTP transport's wire mechanics — `info/refs` negotiation, pkt-line encoding, content types, streaming | `capabilities-git-smart-http` |
| What Blossom media storage lets a user do, and its maturity against BUD-01/02/11 | `capabilities-media-blossom` |
| The relay crate's internal structure | `implementation-crates-buzz-relay` |
| The relay as a deployed container | `architecture-containers-relay` |
| The metrics layer itself — what is emitted, scraped and dashboarded | `layers-observability-metrics` |
| How relay configuration is loaded, defaulted and validated | `layers-configuration-relay-configuration` |

Sibling networking-layer subjects, all filed under Feature #609 and none merged at
the recorded revision, so none is a relationship target here:

| Not covered here | Owned by |
|---|---|
| The WebSocket transport that shares this listener | #1134 |
| TLS termination | #1133 |
| Request routing | #1131 |
| Host-to-community binding, the boundary AGENTS.md says every HTTP path preserves | #1126 |
| The `/hooks/{id}` webhook door and its middleware slice specifically | #1124 |

This node also does not attempt an endpoint-by-endpoint catalogue. That is reference
material, and `router.rs` already is it — a second copy would drift the moment a
route is added, which is exactly the failure a layer concept is supposed to avoid.

## Scope and omissions

**This node covers** why a Nostr-first relay has an HTTP surface at all, what
categories are on it and why each cannot be an event, and the properties every path
shares: per-sub-router body limits, the single CORS layer and its fail-closed
misconfiguration behaviour, the metrics middleware and its cardinality blind spot,
the trace root, the deliberately separate health and metrics listeners, and the way
the UDS listener changes what `ConnectInfo`-dependent middleware sees.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `POST /events` lifecycle — tenant binding, NIP-98, replay, admission, ingest, status mapping | `architecture-flows-http-event-submission` |
| The test obligation on `POST /events` and its gated status | `verification-contracts-http` |
| Blossom media internals — BUD maturity, upload and download semantics | `capabilities-media-blossom` |
| Git smart HTTP — pkt-line framing, `info/refs` negotiation, content types | `capabilities-git-smart-http` |
| The relay crate's overall structure and its NIP-11 document | `implementation-crates-buzz-relay` |
| The admin host's security boundary — the fixed `ADMIN_CSP`, the asset allowlist, the non-browsable bundle, admin-host-first ordering | Not filed as its own task at this revision; see *A second concept found and not folded in* below |
| The `/hooks/{id}` webhook surface as a subject in its own right | A sibling task in Feature #609, unmerged at this revision and therefore carrying no relationship edge |
| Host resolution, connection admission, the WebSocket transport, TLS termination, and in-band Nostr verb dispatch | Sibling tasks in Feature #609 (#1126, #1121, #1134, #1133, #1131), all unmerged at this revision |

**Expected but not verified when this node was written:**

- **Nothing was run.** No relay was started, no request was issued, and no test was
  executed. `router.rs` was read in full and the middleware, config and `main.rs`
  serving code were read at the cited paths; the unit tests in `router.rs` were read
  for their assertions, not run.
- **The UDS consequence for `/internal/git/policy` was not observed.** It is an
  INFERENCE composed from `require_localhost`'s missing-extension default and the two
  different `into_make_service*` calls in `main.rs`. No test in the repository
  exercises a request over the Unix domain socket, so nothing confirms the composition
  holds at runtime.
- **No test was found asserting the body-limit values themselves.** The four limits
  were read from the four `RequestBodyLimitLayer` constructions; a search of
  `router.rs`'s own test module found tests for the routing predicates, the admin
  CSP, the trace parenting and the WebSocket frame limit, but none that issues an
  oversized HTTP body against any sub-router.
- **`build_cors_layer`'s three branches are untested.** The permissive, parsed-list
  and refuse-to-fall-back branches were read from source; no test constructs a router
  with a malformed `BUZZ_CORS_ORIGINS` and asserts the resulting layer.
- **Git history was not consulted.** Every claim above rests on the source as it
  stands at the recorded revision. Issues were consulted (the #609 sibling list and
  #1127's own definition of done, both recorded as `TEAM_KNOWLEDGE` above), but no
  commit, pull request or blame was read to establish *why* any of these choices was
  made — so the rationale offered for the surface's narrowness is `AGENTS.md`'s
  stated position plus one `INFERENCE`, not a reconstructed decision history.
- **Deployment reality was not checked.** Whether `health_port`, `metrics_port` and
  `bind_addr` are actually exposed differently in the staging Kubernetes deployment
  was not verified against the deployment repositories — only against the relay's own
  `serve()`.

**A second concept found and not folded in.** The admin host's fixed
Content-Security-Policy, its allowlisted document and asset paths, and the
"admin host is checked first and can never fall through to the public bundle"
property are a coherent security-boundary subject with its own tests. They are noted
here only as evidence that the fallback is host-aware; the boundary itself is a
candidate for its own node and was not written into this one.
