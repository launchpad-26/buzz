---
id: layers-security-relay-boundary
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The general API router caps every HTTP request body at 1 MiB (`RequestBodyLimitLayer::new(1024 * 1024)`) as the last layer applied to `api_router` before it is merged with the other sub-routers; the media router carries its own, larger limit sized to `max(config.media.max_image_bytes, config.media.max_video_bytes)`, applied only to its own routes via a separate `RequestBodyLimitLayer` instance."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "WebSocket frame/message size is bounded by two independent layers using the same configured value, `config.max_frame_bytes` (default `DEFAULT_MAX_FRAME_BYTES = 512 * 1024`, overridable via `BUZZ_MAX_FRAME_BYTES`): `limit_relay_websocket` sets `max_message_size`/`max_frame_size` on the `WebSocketUpgrade` before tungstenite ever assembles a frame, and `recv_loop` separately re-checks the decoded `Text`/`Binary` payload length against the same value after upgrade and disconnects (not merely warns) if it is exceeded — the function comment names this pairing 'defense in depth', and a passing test, `relay_websocket_parser_rejects_oversized_messages_before_handler_reads_them`, asserts a message at the limit reaches the handler while one byte over does not."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The relay identifies a connection's peer IP solely from axum's `ConnectInfo<SocketAddr>`, populated by `into_make_service_with_connect_info::<std::net::SocketAddr>()` over the raw TCP listener bound in `main.rs`'s `serve`; a repository-wide grep for `x-forwarded-for`, `forwarded_for`, `real.ip`, and `x-real-ip` (case-insensitive) across `crates/buzz-relay/src`, `crates/buzz-auth/src`, and `crates/buzz-pubsub/src` returns no matches, so no client-supplied header is parsed or trusted as an alternate IP source anywhere in this call chain."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/router.rs"
      - "grep(pattern=\"x-forwarded-for|forwarded_for|real\\.ip|x-real-ip\", scope=\"crates/buzz-relay/src crates/buzz-auth/src crates/buzz-pubsub/src\", flags=case-insensitive) -> no matches"
  - statement: "`buzz-auth::rate_limit::RateLimiter::check_ip_connection` and its `IpConnections` limit type exist specifically for this boundary: the trait's own doc comment states IP-keyed limits are 'operator-global by design... gate connection acceptance at the network edge, before host->community resolution has completed (or, on resolve failure, instead of it)', deliberately taking no `TenantContext` so as not to invert that ordering."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "`check_ip_connection` is implemented twice — `RedisRateLimiter` in `crates/buzz-pubsub/src/rate_limiter.rs` (a real, atomic Redis INCR/EXPIRE Lua script keyed by `ip_rate_limit_key`) and `AlwaysAllowRateLimiter` in `crates/buzz-auth/src/rate_limit.rs` (test-only) — but a repository-wide grep for `check_ip_connection` outside those two implementations and their own doc comments finds exactly one remaining call site, `crates/buzz-relay/src/admission.rs`'s own `StubLimiter` in `#[cfg(test)] mod tests`, which is a mock implementation of the trait, not a caller of it. No production code path in `buzz-relay` invokes `check_ip_connection`, and no `RateLimitConfig` field or `BUZZ_*` environment variable configures a window or limit for it — confirmed by grep for `ip_connections`/`ip_conn` across `crates/buzz-relay/src/config.rs`, `crates/buzz-auth/src/rate_limit.rs`, and `crates/buzz-pubsub/src/rate_limiter.rs`, which matches only the `LimitType::IpConnections` enum variant and its key-suffix mapping, never a configuration field."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-auth/src/rate_limit.rs"
      - "grep(pattern=\"check_ip_connection\", scope=\"crates/\") -> matches only the two trait implementations, the trait/doc-comment definition, and admission.rs's test-only StubLimiter"
      - "grep(pattern=\"ip_connections|ip_conn\", scope=\"crates/buzz-relay/src/config.rs crates/buzz-auth/src/rate_limit.rs crates/buzz-pubsub/src/rate_limiter.rs\") -> matches only the LimitType::IpConnections enum variant and its \"conn\" key-suffix arm"
  - statement: "`build_health_router`'s own doc comment states it is deliberately unauthenticated: 'No metrics middleware, no auth, no CORS, no body limit.' It is a second, independent axum `Router` bound to its own listener (`0.0.0.0:{config.health_port}` in `main.rs`'s `serve`) exposing `/_liveness`, `/_readiness`, `/_status`, and `/_mesh`, entirely separate from the main app router's listener and middleware stack."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "`build_cors_layer` returns `CorsLayer::permissive()` (any origin, any method, any header) whenever `BUZZ_CORS_ORIGINS` is unset or empty; when the variable is set but every entry fails to parse as a valid header value, the function explicitly refuses to fall back to permissive, instead logging an error and returning a bare `CorsLayer::new()` (which allows nothing), so a misconfiguration fails toward no cross-origin access rather than toward wide-open access."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`nip11_or_ws_handler` checks `api::admin::is_admin_host(&state, &headers)` before any content negotiation or WebSocket-upgrade attempt runs; when the connecting Host matches the configured admin authority, the handler short-circuits to either the admin SPA index or a `404`, and never reaches the public NIP-11 document or the WebSocket upgrade path for that request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/admin/mod.rs"
      - "crates/buzz-relay/src/api/admin/auth.rs"
  - statement: "Once `state.shutting_down` is set (on SIGTERM, before the graceful-drain sleep begins), `nip11_or_ws_handler` refuses a new WebSocket upgrade with `503 Service Unavailable` and the body `relay restarting`; this check runs after `WebSocketUpgrade::from_request` succeeds but before `on_upgrade` hands the socket to `handle_connection`, so an in-flight upgrade during the shutdown grace window is rejected rather than accepted onto a draining pod."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "tower_http's `RequestBodyLimitLayer` is documented and widely used to reject an oversized body with `413 Payload Too Large` before the wrapped handler runs; this repository's own hand-rolled body-limit checks for the same failure condition, in `crates/buzz-relay/src/api/git/transport.rs` and documented in `crates/buzz-relay/src/api/git/hydrate.rs` ('Resource-limit failures map to 413'), return the identical `StatusCode::PAYLOAD_TOO_LARGE`, which is corroborating but not a substitute for reading the pinned `tower_http` crate's own source at this revision, which this node did not do."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/hydrate.rs"
    confidence: 0.7
  - statement: "Issue #1172's definition of done requires the invariant be stated as one unambiguous property using MUST/MUST NOT only where normative, with scope, enforcement points, observable failure behavior, and at least one verification/conformance mechanism named or its absence recorded explicitly."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1172 definition of done"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Layer: the relay's network-edge boundary

## The invariant

**Every inbound connection the relay's application listener accepts — WebSocket or
HTTP — MUST have its request/message size bounded, and the relay MUST identify that
connection's IP solely from the transport-layer peer address, before any handler,
authentication check, or host→community resolution observes its content.** No
client-supplied header MUST ever be treated as an alternate or overriding source of
truth for a connection's size limits or its IP.

This is the boundary that runs *ahead of* the boundaries documented elsewhere in this
corpus: `architecture-principles-community-is-security-boundary` governs what happens
once a Host header is resolved to a community, and `architecture-principles-fail-closed-boundaries`
governs what happens once an authentication or authorization lookup runs. This node
covers what the relay does — and does not — enforce on a connection before either of
those steps begins: how large a message it will accept, what it trusts as the
connection's identity for network-level admission, and which surfaces are reachable
with no such gate at all.

## Scope: what this governs

**Applies to:** the main application listener (`config.bind_addr`, TCP, and the
optional Unix domain socket at `config.uds_path`) and every route served from
`build_router` — the WebSocket/NIP-11 door, the REST bridge, media upload, git Smart
HTTP, workflow webhooks, and the admin/web SPA fallback. Concretely, at this revision:
HTTP body-size caps (`RequestBodyLimitLayer`, two independent limits — 1 MiB general,
a larger media-specific limit), WebSocket frame/message-size caps (`max_frame_bytes`,
enforced twice), peer-IP sourcing (`ConnectInfo<SocketAddr>` only), CORS policy
(`build_cors_layer`), and the deliberately-unauthenticated health listener.

**Does not govern:** host→community resolution itself (`bind_community`, covered by
`architecture-principles-community-is-security-boundary`); NIP-42/NIP-98
authentication and the moderation/allowlist gates that run once a connection is
already accepted (covered by `architecture-principles-fail-closed-boundaries`); or
the per-pubkey/per-community throughput limits (`LimitType::Messages`, `ApiCalls`,
`WsEvents`) enforced inside an already-established, already-bound connection. This
node's boundary is specifically the admission surface a caller meets *before* any of
those identity-scoped decisions run.

**Applies once per connection, not once per message:** the WebSocket size caps are
set at upgrade time (`limit_relay_websocket`) and re-checked per frame in `recv_loop`;
the HTTP body caps apply per request, since each HTTP request on this router is its
own connection-scoped event from the middleware's point of view.

## Enforcement points

| Point | What it does |
|---|---|
| `RequestBodyLimitLayer` on `api_router` (`crates/buzz-relay/src/router.rs`) | Rejects any general HTTP request body over 1 MiB before any handler runs. |
| `RequestBodyLimitLayer` on `media_router` (`crates/buzz-relay/src/router.rs`) | A separate, larger limit — `max(config.media.max_image_bytes, config.media.max_video_bytes)` — scoped only to the media upload/download routes. |
| `limit_relay_websocket` (`crates/buzz-relay/src/router.rs`) | Sets `max_message_size`/`max_frame_size` on the `WebSocketUpgrade` to `config.max_frame_bytes` before tungstenite assembles a frame. |
| `recv_loop` (`crates/buzz-relay/src/connection.rs`) | Re-checks decoded text/binary length against the same `max_frame_bytes` after upgrade and disconnects on violation — documented defense-in-depth alongside the parser-level cap above. |
| `into_make_service_with_connect_info::<SocketAddr>()` (`crates/buzz-relay/src/main.rs`) | The sole source of a connection's IP for every downstream use (e.g. the unwired IP-connection fence below); no proxy header is read anywhere in the call chain. |
| `build_cors_layer` (`crates/buzz-relay/src/router.rs`) | Permissive by default when unconfigured; an explicit allow-list once `BUZZ_CORS_ORIGINS` is set, refusing to silently widen back to permissive on a malformed value. |
| `build_health_router` (`crates/buzz-relay/src/router.rs`, listener in `main.rs`) | A second, separate listener and router carrying no auth, CORS, or body-limit middleware — deliberately unauthenticated, not an oversight. |
| Shutdown-refusal check in `nip11_or_ws_handler` (`crates/buzz-relay/src/router.rs`) | Rejects a new WebSocket upgrade with `503` once `state.shutting_down` is set, after the handshake succeeds but before the socket reaches the connection handler. |
| Admin-host short-circuit in `nip11_or_ws_handler` (`crates/buzz-relay/src/router.rs`, `crates/buzz-relay/src/api/admin/`) | Runs before content negotiation or WebSocket upgrade, so the admin authority never falls through to the public NIP-11/WS surface. |

## Observable failure behavior

An oversized HTTP request body is rejected by `RequestBodyLimitLayer` before the
handler executes (the repository's own hand-rolled equivalents for the same failure
class return `413 Payload Too Large` — see the INFERENCE entry in the evidence
ledger for why this node does not assert that status code as a directly-verified
`FACT` for the `tower_http`-provided layer itself). An oversized WebSocket frame is
rejected at the parser (`limit_relay_websocket`) before a message is ever assembled,
or — if a message somehow reached the handler with an oversized payload —
`recv_loop` sends a `NOTICE` naming the byte count and the configured limit and then
disconnects the socket. A connection attempting to reach the admin authority through
the public surface, or a WebSocket upgrade attempted during the shutdown grace
window, is rejected before `handle_connection` (and therefore before host binding)
ever runs.

## Verification

**No dedicated conformance suite or formal model targets this boundary as a whole at
this revision.** The strongest direct evidence is the unit test
`relay_websocket_parser_rejects_oversized_messages_before_handler_reads_them`
(`crates/buzz-relay/src/router.rs`), which asserts the WebSocket frame-size fence
specifically: a message at the configured limit reaches the handler, one byte over
does not. The HTTP body-size layers, the CORS fallback behavior, the health-router
isolation, the admin-host short-circuit, and the shutdown-refusal check are verified
in this node only by reading their source directly — none of them was found to have
its own dedicated test asserting the boundary behavior by name.

**This node's most consequential finding is a verification gap, not a passing
check.** `RateLimiter::check_ip_connection` — the trait method whose own doc comment
describes it as the mechanism that "gate[s] connection acceptance at the network
edge, before host->community resolution" — is fully implemented against Redis
(`RedisRateLimiter` in `crates/buzz-pubsub/src/rate_limiter.rs`) but is called at no
production site in this repository, and no configuration field supplies it a window
or limit. The network edge currently has no IP-based connection-rate fence in force,
despite the plumbing existing to build one. Nothing in the corpus checker or CI
catches this: `python3 launchpad/project-intelligence/corpus/validate.py` confirms
only that this node's front matter and citations are structurally well-formed, never
that the relay actually enforces what this node describes.

## Scope and omissions

**This node covers:** the network-edge admission properties enforced on every
inbound WebSocket/HTTP connection before auth or host→community resolution runs —
size limits (HTTP body, WS frame/message), peer-IP sourcing, CORS policy, and the
listener-level surfaces (health router, admin-host short-circuit, shutdown refusal)
that sit ahead of or alongside those checks.

**This node does not cover, and these are gaps rather than silence:**

- **The metrics listener** (port 9102, built via `PrometheusBuilder` per `main.rs`'s
  own topology comment) was not inspected for its own auth/body-limit posture; this
  node makes no claim about it.
- **The Unix domain socket listener** (`config.uds_path`) shares the same `router`
  (and therefore the same middleware stack) as the main TCP listener per `serve`'s
  code, but this was read from the wiring, not independently tested against a live
  UDS connection.
- **Whether an operator-level reverse proxy or load balancer sits in front of the
  relay in any given deployment**, and if so, whether it forwards a proxy header
  this relay would need to parse to see a real client IP, is a deployment-topology
  question this node does not answer — see the `architecture/deployment/` nodes for
  that. This node states only what the relay's own code does with the connection it
  receives: it trusts the transport-layer peer address and nothing else.
- **The IP-connection-rate gap named above is a fact about this revision, not a
  recommendation.** Whether wiring `check_ip_connection` into `nip11_or_ws_handler`
  is the right fix, and what its window/limit defaults should be, is implementation
  work for a linked issue, not a decision this documentation node makes.
- **No per-type `layers` template exists yet** (`launchpad/docs/corpus/AGENTS.md`
  §"Scope and omissions" lists per-type templates as still-owned by #1307–#1351), so
  this node's structure follows `node.schema.json` directly, mirroring the shape
  used by the merged `architecture`/`principles` nodes it references, rather than an
  established `layers` template.
