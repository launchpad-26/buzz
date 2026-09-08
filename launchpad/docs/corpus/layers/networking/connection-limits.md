---
id: layers-networking-connection-limits
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0."
    entry_class: FACT
    evidence:
      - "commit 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0"
  - statement: "The relay's connection-shaped bounds are configured in Config as max_connections (default 10000, BUZZ_MAX_CONNECTIONS), max_concurrent_handlers (default 1024, BUZZ_MAX_CONCURRENT_HANDLERS), send_buffer_size (default 1000, BUZZ_SEND_BUFFER), max_frame_bytes (default DEFAULT_MAX_FRAME_BYTES, BUZZ_MAX_FRAME_BYTES) and slow_client_grace_limit (default 15, BUZZ_SLOW_CLIENT_GRACE_LIMIT)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "DEFAULT_MAX_FRAME_BYTES is declared as 512 * 1024, so the default inbound WebSocket frame ceiling is 524288 bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "max_connections and max_concurrent_handlers are turned into capacity at startup as two tokio Semaphores held on AppState: conn_semaphore is Semaphore::new(max_connections) and handler_semaphore is Semaphore::new(max_concurrent_handlers)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "handle_active_connection acquires a conn_semaphore permit with try_acquire_owned after the WebSocket upgrade has already completed, and on failure logs 'Connection limit reached, rejecting {addr}' and returns without sending the client any NOTICE, CLOSE reason or other protocol message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The huddle-audio WebSocket route draws on the same state.conn_semaphore, but checks the permit before the upgrade and refuses with HTTP 503 SERVICE_UNAVAILABLE and the body 'relay: connection limit reached'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Because both the Nostr WebSocket route and the huddle-audio route acquire permits from the same conn_semaphore, the max_connections budget is shared across the two socket kinds rather than being a per-route cap."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
    confidence: 0.9
  - statement: "The frame ceiling is applied twice: limit_relay_websocket sets max_message_size and max_frame_size on the upgrade so tungstenite refuses oversized payloads before assembly, and recv_loop re-checks text and binary frame length against state.config.max_frame_bytes, sending a NOTICE naming both the observed size and the limit and then breaking out of the receive loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "EVENT, REQ and COUNT each take a handler_semaphore permit before spawning their handler task, and a failed acquisition is answered with 'rate-limited: too many concurrent requests' -- delivered as CLOSED against the subscription id for REQ and as NOTICE for EVENT and COUNT."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_req enforces a per-connection cap of MAX_SUBSCRIPTIONS = 1024 by rejecting a REQ whose subscription id is not already registered once the connection holds that many subscriptions, answering CLOSED with 'error: too many subscriptions'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "ClientMessage::parse enforces MAX_SUB_ID_LENGTH = 256 bytes and MAX_FILTERS_PER_REQ = 10 for both REQ and COUNT, returning RelayError::InvalidMessage before any filter is deserialized."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "handle_req additionally bounds the aggregate number of explicit #h channel values in one request to MAX_EXPLICIT_CHANNEL_VALUES = 128, answering CLOSED with 'restricted: too many explicit channels'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A filter's own limit field is not rejected when it exceeds the advertised ceiling: query_events clamps it to EventQuery::max_limit or, absent that, to DEFAULT_MAX_PAGE_LIMIT, which is declared as 1000."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "The NIP-11 limitation block the relay serves advertises max_message_length from config.max_frame_bytes, max_subscriptions 1024, max_filters 10, max_limit buzz_db::DEFAULT_MAX_PAGE_LIMIT, max_subid_length 256, auth_required true, payment_required false and restricted_writes true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "Every numeric ceiling the NIP-11 limitation block advertises has a corresponding enforcement site in this repository -- max_message_length in router.rs and connection.rs, max_subscriptions in handlers/req.rs, max_filters and max_subid_length in protocol.rs, and max_limit in buzz-db's query_events -- so the advertised document describes bounds that are actually applied rather than aspirational ones."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-db/src/store/event.rs"
    confidence: 0.9
  - statement: "Per-principal admission runs before message dispatch: enforce_ws_admission checks a WsEvents budget for every EVENT, REQ and COUNT from an authenticated connection, and an additional Messages budget for EVENT, skipping both entirely when the connection is not yet authenticated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The WebSocket-events budget is derived from limits.human_ws_events_per_sec unconditionally, while the Messages budget branches on whether the authenticated context carries an agent_owner_pubkey and selects agent_standard_messages_per_min or human_messages_per_min -- so the per-second WebSocket ceiling is tier-blind while the per-minute message ceiling is not, and the elevated and platform agent tiers are not consulted on this path at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "ws_admission_budget converts the configured per-second WebSocket rate into a 5-second fixed window multiplied by that rate (WS_BURST_WINDOW_SECS = 5), preserving the average rate while permitting a bounded startup burst."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
  - statement: "RateLimitConfig's defaults are 60 human messages per minute, 30 GIF searches per minute, 300 human API calls per minute, 10 human WebSocket events per second, 120 and 600 for standard-tier agent messages and API calls, 300 for elevated-tier agent messages and 600 for platform-tier agent messages."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "Admission fails closed: check_principal maps a limiter error to AdmissionError::Unavailable, and send_admission_result rejects the request with 'rate-limited: shared admission unavailable' while incrementing buzz_admission_rejections_total with reason='unavailable', distinct from the reason='quota' counter used for a genuine quota breach."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "LimitType includes an IpConnections variant with the Redis key suffix 'conn', and the RateLimiter trait declares check_ip_connection as an operator-global, deliberately non-tenant-scoped fence."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "The merged corpus node layers-data-redis-ttl-policy already records that a repository-wide grep for the literal invocation '.check_ip_connection(' finds zero call sites, so the per-IP connection fence is implemented but unwired; this node links to that finding rather than restating it as its own."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/data/redis/ttl-policy.md"
  - statement: "The RateLimiter doc comment warns that the fixed-window algorithm used by the Redis implementation allows up to a 2x burst at window boundaries and that a sliding window or token bucket is needed for strict per-second limiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "The huddle-audio route applies its own frame ceiling of MAX_TEXT_FRAME_BYTES = 8192 bytes rather than the relay-wide max_frame_bytes, and its unit tests assert acceptance at exactly that size and rejection at one byte above it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/handler.rs"
  - statement: "Test coverage for these bounds is uneven at the recorded revision: protocol.rs unit-tests the filter-count boundary at exactly and above MAX_FILTERS_PER_REQ, config.rs asserts the default and configured values of max_frame_bytes, handlers/req.rs has req_filter_limit_clamps_to_advertised_nip11_max_limit, and audio/handler.rs tests its own frame boundary -- while the end-to-end subscription-cap test test_subscription_limit_enforced carries #[ignore] and so does not run in a default test invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The relay's e2e NIP-11 test asserts limitation.max_subscriptions is 1024 and limitation.auth_required is true, pinning two of the advertised values against the served document."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The eight BUZZ_RATE_LIMIT_* admission variables are documented with their defaults in .env.example, but BUZZ_MAX_CONNECTIONS, BUZZ_MAX_CONCURRENT_HANDLERS, BUZZ_MAX_FRAME_BYTES, BUZZ_SEND_BUFFER and BUZZ_SLOW_CLIENT_GRACE_LIMIT are read by config.rs and appear nowhere in that file."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The shared Redis-backed admission path was introduced by commit 73fc0ec6cf, '[codex] Enforce shared relay admission limits (BUZZ-SEC-019) (#1917)', which is the most recent commit touching crates/buzz-relay/src/admission.rs."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git log --oneline -5 -- crates/buzz-relay/src/admission.rs, run while authoring this node"
  - statement: "Issue #1123's definition of done requires exactly one hand-authored canonical corpus document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links rather than duplicated neighbour content, a check against the recorded provenance revision, a clean validator run, a one-sentence definition before deeper explanation, an explicit boundary statement, and examples that introduce no second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1123 definition of done"
relationships:
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-auth
  - type: references
    target: implementation-crates-buzz-pubsub
  - type: references
    target: layers-configuration-relay-configuration
  - type: references
    target: layers-data-redis-ttl-policy
  - type: references
    target: layers-lifecycle-concurrency
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: verification-contracts-websocket
  - type: references
    target: layers-observability-metrics
  - type: references
    target: layers-data-postgres-connection-pool
  - type: references
    target: layers-data-redis-connection-pool
---

# Connection limits

**Connection limits are the bounds the relay places on a client's use of a
WebSocket connection — how many sockets exist at once, how large a frame may be,
how many subscriptions and filters a connection may hold, and how fast a
principal may send — together with the specific rejection each bound produces
when it is crossed.**

## Definition and scope

A connection limit in Buzz is a *ceiling with a named breach behaviour*. Every
bound below has two halves that must be read together: the value, and what the
relay does to the client that exceeds it. The second half is the part that
varies most and the part most easily assumed wrong — three different bounds on
the same connection produce a silent socket drop, a `NOTICE`, and a `CLOSED`
respectively.

**What counts as a connection limit here.** Bounds that shape a *client's*
WebSocket session with the relay: the relay-wide socket budget, the in-flight
handler budget, the inbound frame ceiling, the per-connection subscription and
filter caps, the parse-time subscription-id length cap, the per-request explicit
channel cap, the filter `limit` clamp, and the per-principal admission budgets
that gate EVENT/REQ/COUNT.

**What is deliberately not a connection limit here**, even though the words
overlap:

- **Datastore pool sizes.** `BUZZ_DB_POOL_SIZE` and `BUZZ_REDIS_POOL_SIZE` bound
  the relay's own outbound connections to Postgres and Redis. They are a
  different direction of travel and are owned elsewhere in this corpus.
- **Slow-client and backpressure handling.** `send_buffer_size` and
  `slow_client_grace_limit` are read by the same `Config`, but they govern what
  happens when a client cannot *keep up with* delivery, not what happens when it
  *exceeds a ceiling*. See the boundary table.
- **Transport-level limits on non-WebSocket surfaces** — git pack size, media
  upload concurrency — which bound HTTP requests, not sockets.

## The bounds, and what each breach looks like

| Bound | Value at the recorded revision | Enforced in | On breach |
|---|---|---|---|
| Concurrent WebSocket connections, relay-wide | 10 000 (`BUZZ_MAX_CONNECTIONS`) | `conn_semaphore` in `state.rs`, acquired in `connection.rs` | Nostr route: a log line and the socket dropped — **no protocol message at all**. Audio route: HTTP 503 before the upgrade |
| Concurrently executing message handlers | 1024 (`BUZZ_MAX_CONCURRENT_HANDLERS`) | `handler_semaphore`, acquired per EVENT/REQ/COUNT | `rate-limited: too many concurrent requests` — `CLOSED` for REQ, `NOTICE` for EVENT and COUNT |
| Inbound frame size | 512 KiB (`BUZZ_MAX_FRAME_BYTES`) | `limit_relay_websocket` at upgrade, re-checked in `recv_loop` | `NOTICE` naming observed size and limit, then the receive loop breaks — the connection ends |
| Subscriptions per connection | 1024 | `handlers/req.rs` | `CLOSED` with `error: too many subscriptions` |
| Filters per REQ or COUNT | 10 | `protocol.rs`, at parse time | `RelayError::InvalidMessage`, surfaced as an `invalid message` `NOTICE` |
| Subscription-id length | 256 bytes | `protocol.rs`, at parse time | `RelayError::InvalidMessage` |
| Explicit `#h` channel values per request | 128 | `handlers/req.rs` | `CLOSED` with `restricted: too many explicit channels` |
| Filter `limit` value | clamped to 1000 | `buzz-db`'s `query_events` | **Silently clamped, not rejected** |
| Per-principal WebSocket events | 10/s, admitted as 50 per 5 s window; tier-blind | `admission.rs` + `enforce_ws_admission` | `rate-limited: quota exceeded; retry in Ns` |
| Per-principal messages (EVENT only) | 60/min human, 120/min standard-tier agent | same | same shape |
| Audio-route frame size | 8 192 bytes | `audio/handler.rs` | route-local, independent of `max_frame_bytes` |

Three asymmetries in that table are worth carrying away, because each has bitten
somebody's mental model:

1. **The relay-wide connection cap is the only bound with no client-visible
   explanation.** The permit is taken *after* the WebSocket upgrade has already
   succeeded, so the client observes a socket that opens and then closes with
   nothing on it. The audio route, which checks its permit *before* the upgrade,
   can and does return an honest 503. Same semaphore, two very different
   experiences.
2. **The `limit` filter field is clamped, not refused.** A client asking for
   5 000 events receives 1 000 and no error. Everything else in the table
   rejects; this one silently narrows.
3. **The connection budget is shared, not per-route.** Huddle-audio sockets and
   Nostr sockets draw permits from the same semaphore, so audio load consumes
   protocol capacity and vice versa.

## Advertisement: the NIP-11 `limitation` block

The relay publishes several of these ceilings so a client can adapt rather than
discover them by rejection. The served `limitation` object carries
`max_message_length` (taken from the live `config.max_frame_bytes`, so it tracks
the deployment rather than the default), `max_subscriptions: 1024`,
`max_filters: 10`, `max_limit` (the same `DEFAULT_MAX_PAGE_LIMIT` constant the
REQ path clamps to), `max_subid_length: 256`, and the booleans
`auth_required: true`, `payment_required: false`, `restricted_writes: true`.

Each of those numbers has a real enforcement site in this repository, so the
advertisement describes applied bounds rather than intentions. `max_limit` is
the strongest case: `nip11.rs` deliberately reads the same `buzz_db` constant the
query path clamps against, with a named unit test cited in its own doc comment,
so the advertised ceiling and the enforced one cannot drift apart.

## Admission: the rate-shaped limits

The count-and-size bounds above are structural. The admission bounds are
*temporal*, and they behave differently in three ways that matter:

- **They only apply to an authenticated connection.** `enforce_ws_admission`
  reads the auth state first and returns `true` — admitting the message —
  whenever the connection is not yet `Authenticated`. Pre-auth traffic is
  governed by the structural bounds and by the auth handshake, not by the
  per-principal budget.
- **They are burst-shaped, not strictly per-second.** The configured per-second
  rate is converted into a 5-second fixed window carrying five times the rate, so
  a desktop client establishing several subscriptions at startup is not punished
  for it. The `RateLimiter` documentation is explicit that a fixed window admits
  up to a 2x burst at window boundaries.
- **Only one of the two is tier-aware.** The per-second WebSocket-events budget
  is taken from the *human* setting whatever the principal is; only the
  per-minute message budget branches on whether the authenticated context
  carries an agent owner, and it chooses between the human and *standard*-tier
  agent values. The elevated and platform agent tiers are not consulted on this
  path at all.
- **They fail closed.** If the shared limiter is unreachable, the request is
  rejected with `rate-limited: shared admission unavailable`, and the rejection
  is counted under a distinct `reason` label so an operator can tell a real quota
  breach from an infrastructure outage.

`LimitType` also defines an `IpConnections` variant and the `RateLimiter` trait
declares `check_ip_connection` as a deliberately operator-global (non
tenant-scoped) fence. That fence is implemented but has no call site — a finding
already recorded by `layers-data-redis-ttl-policy`, which this node references
rather than restates.

## Use cases

**Reading a client failure.** The rejection text is the fastest route to the
bound that produced it. `too many subscriptions` and `too many concurrent
requests` sound alike and are unrelated: the first is a per-connection structural
cap of 1024, the second is relay-wide handler saturation. A socket that opens and
immediately dies with no message at all is the relay-wide connection cap, and it
will only ever be visible in the relay's own logs.

**Sizing a deployment.** `max_connections` is a per-process semaphore, so the
value is per relay pod, not per cluster, and it is shared with huddle audio.

**Writing a client.** Read the NIP-11 `limitation` block rather than hardcoding:
`max_message_length` reflects the deployment's configured frame ceiling, which a
given relay may have lowered.

**Choosing where to add a new bound.** Parse-time caps (`protocol.rs`) reject
before any work happens; handler-time caps (`handlers/req.rs`) reject after
authentication is known. A bound that needs identity belongs in the second
place, and one that does not belongs in the first.

## Scope and omissions

**This node covers** the connection-shaped bounds listed above, their configured
values and defaults at the recorded revision, where each is enforced, the
rejection each produces, and how they relate to what the relay advertises in
NIP-11.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Slow-client backpressure, `send_buffer_size`, and the `slow_client_grace_limit` disconnect | The sibling slow-client node (launchpad-26/buzz#1132), not this one |
| The mechanics of relay configuration — precedence, parsing, validation of env values | `layers-configuration-relay-configuration` |
| Postgres and Redis pool sizing | `layers-data-postgres-connection-pool`, `layers-data-redis-connection-pool` |
| Whether `check_ip_connection` is wired anywhere | `layers-data-redis-ttl-policy`, which already records that it is not |
| Rate-limit key construction, TTL repair and tenant scoping in Redis | `implementation-crates-buzz-pubsub`, `layers-data-redis-ttl-policy` |
| HTTP-surface bounds — git pack/repo size, media upload concurrency | Not documented in this Feature |
| The NIP-42 handshake that decides whether admission applies at all | `architecture-flows-websocket-authentication` |

**Expected but could not verify when this node was written:**

- **No test was found exercising the relay-wide connection cap.** Searching for
  tests around `conn_semaphore` and the `Connection limit reached` log line
  turned up call sites and no assertion. The claim that exhaustion drops the
  socket without a protocol message rests on reading `handle_active_connection`,
  not on an observed run.
- **No test was found exercising the runtime `max_frame_bytes` rejection on the
  Nostr route.** `config.rs` tests that the value parses (default and
  configured); the audio route tests its own separate 8 192-byte boundary. The
  `recv_loop` path that emits `frame too large` and disconnects was not found
  covered.
- **The end-to-end subscription-cap test carries `#[ignore]`.**
  `test_subscription_limit_enforced` asserts the 1025th REQ is `CLOSED`, but is
  skipped by a default test run, so the 1024 cap is pinned by reading the
  constant rather than by a routinely executed test.
- **Five limit-bearing environment variables are undocumented in
  `.env.example`.** `BUZZ_MAX_CONNECTIONS`, `BUZZ_MAX_CONCURRENT_HANDLERS`,
  `BUZZ_MAX_FRAME_BYTES`, `BUZZ_SEND_BUFFER` and `BUZZ_SLOW_CLIENT_GRACE_LIMIT`
  are read by `config.rs` and appear nowhere in that file, while the eight
  `BUZZ_RATE_LIMIT_*` variables are documented there with their defaults. An
  operator reading `.env.example` alone would not know the first five exist.
  This node records the gap; correcting `.env.example` is a code change and is
  out of this task's scope.
- **No live relay was exercised.** Every value and behaviour above was read from
  source at the recorded revision. None was confirmed against a running relay,
  and no deployment's actual `BUZZ_MAX_*` overrides were inspected.
