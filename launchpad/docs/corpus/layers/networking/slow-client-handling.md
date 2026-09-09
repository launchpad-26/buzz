---
id: layers-networking-slow-client-handling
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
  - statement: "Config declares send_buffer_size: usize (documented as the per-connection outbound message buffer size, in messages) and slow_client_grace_limit: u8 (documented as the number of consecutive buffer-full events tolerated before cancelling a slow client), and Config::from_env reads them from BUZZ_SEND_BUFFER defaulting to 1_000 and BUZZ_SLOW_CLIENT_GRACE_LIMIT defaulting to 15."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "Both knobs are read with the silent std::env::var(..).ok().and_then(|v| v.parse().ok()).unwrap_or(default) shape rather than through the same module's validating positive_u64_from_env helper, which returns a ConfigError::InvalidValue for a non-positive integer — so an unparseable BUZZ_SEND_BUFFER or BUZZ_SLOW_CLIENT_GRACE_LIMIT falls back to its default without any error or warning, and a literal 0 parses successfully and is accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "handle_active_connection gives each accepted connection two independent outbound tokio mpsc channels: a data channel sized from state.config.send_buffer_size carrying EVENT/NOTICE/OK frames, and a separate fixed capacity-8 control channel for Pong and Close, whose comment states it exists so control frames stay deliverable even when the data buffer is full."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_active_connection constructs one backpressure_count: Arc<AtomicU8> per connection and passes the same Arc, together with state.config.slow_client_grace_limit, both into the ConnectionState it builds and into state.conn_manager.register, so the direct-send and fan-out paths increment and reset one shared counter rather than two."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "ConnectionState::send offers a text frame with a non-blocking try_send: on Ok it stores 0 into backpressure_count and returns true; on TrySendError::Full it does fetch_add(1) + 1 and, when that count is greater than or equal to grace_limit, logs a warning, increments the buzz_ws_backpressure_disconnects_total counter and calls self.cancel.cancel(), otherwise logging a warning naming count and grace and returning false without cancelling."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "ConnectionManager::try_send_ws_message, the shared body behind send_to and send_to_text_bytes that the fan-out path uses, performs the identical try_send / reset-to-zero / fetch_add / cancel-at-grace_limit sequence against the same per-connection counter and grace limit, incrementing the same buzz_ws_backpressure_disconnects_total counter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "Because both send sites store 0 into the counter on every successful try_send, the counter measures consecutive failures rather than cumulative ones: a single frame that fits returns the connection to full grace regardless of how many buffer-full events preceded it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "A TrySendError::Closed outcome is handled separately from Full at both send sites: it logs at debug level and returns false, leaving the backpressure counter untouched and cancelling nothing, because a closed channel means the connection is already tearing down rather than lagging."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "send_loop_inner's cancellation branch drains any control frames still queued, then sends disconnect_reason.borrow().map_or(WsMessage::Close(None), |reason| reason.close_message()) and breaks out of the writer loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "CommunityDisconnectReason has exactly one variant, CommunityDeleted, whose close_message is a CloseFrame carrying close_code::POLICY and the reason string \"community deleted\"; that watch channel is set only for a deleted community, so a backpressure cancellation leaves it None and the slow client receives WsMessage::Close(None) — a close frame with no status code and no reason text."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "A full control channel is terminal immediately and carries no grace of its own: heartbeat_loop cancels the connection when try_send of a Ping fails, and recv_loop breaks out of its receive loop when try_send of a Pong fails, both logging \"control channel full — cannot send Ping/Pong, closing\" and neither consulting backpressure_count or grace_limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "Four unit tests in buzz-relay's state module cover the counter's arithmetic against a setup_conn helper that registers its connection with a hardcoded grace_limit of 3: send_to_resets_grace_counter_on_success, send_to_increments_grace_counter_on_full, send_to_cancels_after_grace_limit, and shared_counter_between_direct_and_fanout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "The config crate's defaults_are_valid test asserts only that send_buffer_size and slow_client_grace_limit are greater than zero, not that they equal 1000 and 15, so the two default values documented here are not themselves pinned by any assertion."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: ".env.example contains 74 BUZZ_-prefixed occurrences, including a \"Relay (WebSocket server)\" section and commented tuning entries for BUZZ_REDIS_POOL_SIZE and BUZZ_DB_POOL_SIZE that name their defaults, but contains zero occurrences of either BUZZ_SEND_BUFFER or BUZZ_SLOW_CLIENT_GRACE_LIMIT."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "The merged architecture-flows-websocket-connection node states the slow-client rule as one row of its termination table and explicitly places \"the exact numeric values of max_frame_bytes, send_buffer_size, and slow_client_grace_limit\" outside its own scope as operator-configurable and unverified there, which is the boundary this node fills rather than crosses."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
  - statement: "The merged layers-configuration-relay-configuration node is the canonical owner of both variables as configuration: its environment-variable table carries a BUZZ_SEND_BUFFER row (integer, default 1000, \"Per-connection outbound message buffer size (messages)\") and a BUZZ_SLOW_CLIENT_GRACE_LIMIT row (integer, default 15, \"Consecutive buffer-full events tolerated before a slow client is cancelled\"), so this node cites those values as inputs to the mechanism rather than re-owning the configuration surface."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
  - statement: "The grace limit of 15 has a recorded motivation rather than being an arbitrary default: commit 142a5c909542f1e1d2119ca4562129d492aca94c (\"fix(relay): raise grace limit, add replay backpressure, and NOTICE on oversized frames (#1226)\") deleted a hardcoded const SLOW_CLIENT_GRACE_LIMIT: u8 = 3 whose own doc comment read \"Prevents transient read stalls from hard-disconnecting agents mid-inference\", and replaced it with the configurable Config::slow_client_grace_limit defaulting to 15 — so the raise from 3 to 15 was made because a limit of 3 was disconnecting agents during transient read stalls."
    entry_class: FACT
    evidence:
      - "git_show(142a5c909542f1e1d2119ca4562129d492aca94c, paths='crates/buzz-relay/src/config.rs crates/buzz-relay/src/connection.rs') -> removes 'const SLOW_CLIENT_GRACE_LIMIT: u8 = 3' and its 'Prevents transient read stalls from hard-disconnecting agents mid-inference' doc comment; adds 'slow_client_grace_limit' to Config and 'BUZZ_SLOW_CLIENT_GRACE_LIMIT ... unwrap_or(15)' to Config::from_env"
  - statement: "ADR-0018 records that the relay's production sizing decision was made \"without the measurements it named\" and that the relay is \"very likely running cluster-sized defaults\" naming BUZZ_SEND_BUFFER at 1,000 per connection among them, so the send-buffer default is explicitly documented as unmeasured against production load rather than as a tuned value."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md"
      - "launchpad/docs/corpus/verification/performance/relay.md"
  - statement: "Setting BUZZ_SLOW_CLIENT_GRACE_LIMIT to 0 disables grace entirely rather than disabling the disconnect, because the counter is read after its increment and so is at least 1 whenever the comparison runs, making count >= 0 true on the very first buffer-full event."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.9
  - statement: "The Close(None) frame is attempted rather than guaranteed: it is written with ws_send.send(close).await onto the same socket sink whose failure to drain caused the disconnect, so a client whose TCP receive window has genuinely stopped opening may be dropped without ever observing a close frame."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: layers-observability-metrics
  - type: references
    target: layers-lifecycle-concurrency
  - type: references
    target: layers-configuration-relay-configuration
  - type: references
    target: verification-performance-relay
---

# Slow client handling: backpressure, grace, and disconnect

When the relay produces outbound frames faster than a connected WebSocket client
consumes them, the relay does not block, does not grow a queue without limit, and does
not drop the client on first contact. It absorbs the lag in a bounded per-connection
buffer, counts *consecutive* failures to enqueue, tolerates a configurable number of
them, and cancels the connection once that grace is exhausted. This node narrates that
sequence.

**Trigger.** A producer offers a frame to a connection whose writer task has not
drained the outbound buffer — the buffer is at capacity and the non-blocking `try_send`
returns `TrySendError::Full`.

**Preconditions.** The connection is established and registered: `handle_active_connection`
has acquired its semaphore permit, created the two outbound channels, and registered the
connection with the `ConnectionManager`. No authentication state is required — the
mechanism is on the write path and is indifferent to whether the socket has completed
NIP-42.

**Actors.** Two producers (`ConnectionState::send` for frames addressed at one
connection, and `ConnectionManager::send_to` / `send_to_text_bytes` for fan-out), the
bounded data channel, the shared `backpressure_count`, the `send_loop` writer task, the
`CancellationToken`, and the client's socket.

**Upstream boundary.** Where those frames come from is not this node's subject. The
live event fan-out — subscription matching, access revalidation, and the call into
`send_to_text_bytes` — is `architecture-flows-live-fanout`'s. This node picks the flow
up at the moment `try_send` returns `Full` and follows it to termination.

## Sequence

1. A producer calls `try_send` on the connection's data channel — a bounded tokio
   `mpsc` sized from `Config::send_buffer_size`, default `1000` messages, read from
   `BUZZ_SEND_BUFFER`. (`crates/buzz-relay/src/connection.rs`,
   `crates/buzz-relay/src/config.rs`)
2. **If the send succeeds**, the producer stores `0` into the connection's
   `backpressure_count`. Any single successful frame restores full grace, so the counter
   tracks a consecutive run and never a lifetime total.
   (`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/state.rs`)
3. **If the buffer is full**, the producer does `fetch_add(1)` and reads back the
   incremented count. Both producers share one `Arc<AtomicU8>`, handed to `ConnectionState`
   and to `ConnectionManager::register` from the same construction site, so a connection
   lagging on fan-out and on direct sends alike converges on one number.
   (`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/state.rs`)
4. **Below the limit**, the producer logs a warning naming the current count and the
   configured grace, returns `false`, and drops that frame. The frame is not retried and
   not queued elsewhere — the client has lost it.
   (`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/state.rs`)
5. **At or above the limit** — `count >= grace_limit`, from
   `Config::slow_client_grace_limit`, default `15`, read from
   `BUZZ_SLOW_CLIENT_GRACE_LIMIT` — the producer logs "sustained backpressure — closing
   slow client", increments the `buzz_ws_backpressure_disconnects_total` counter, and
   calls `cancel.cancel()` on the connection's token.
   (`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/state.rs`,
   `crates/buzz-relay/src/config.rs`)
6. The writer task's `select!` takes its `cancel.cancelled()` branch, drains any control
   frames still queued so a reason frame queued just before cancellation still reaches
   the client, then sends the connection's close message and breaks.
   (`crates/buzz-relay/src/connection.rs`)
7. That close message is `WsMessage::Close(None)` for this path. The only populated
   alternative comes from `CommunityDisconnectReason`, which has a single variant
   (`CommunityDeleted`, close code `POLICY`, reason `"community deleted"`) and is never
   set by the backpressure path. **The slow client therefore receives a bare close
   frame: no status code, no reason string.**
   (`crates/buzz-relay/src/state.rs`, `crates/buzz-relay/src/connection.rs`)
8. `handle_active_connection`'s ordinary cleanup follows — subscription removal, pubsub
   topic release, deregistration, gauge decrement, presence clearing — the same path
   every other termination reason converges on. That cleanup is
   `architecture-flows-websocket-connection`'s subject, not this node's.
   (`crates/buzz-relay/src/connection.rs`)

**A parallel, ungraced escalation.** The connection's *control* channel is separate and
fixed at capacity 8, deliberately so Pong and Close stay deliverable while the data
buffer is full. If that channel also fills, the writer is stalled outright rather than
merely lagging, and the code treats it as terminal with no grace at all: `heartbeat_loop`
cancels the connection when a `Ping` cannot be enqueued, and `recv_loop` breaks out when
a `Pong` cannot be. Neither consults `backpressure_count` or `grace_limit`.
(`crates/buzz-relay/src/connection.rs`)

## Diagram

```mermaid
sequenceDiagram
    participant P as Producer (direct send / fan-out)
    participant C as backpressure_count (shared AtomicU8)
    participant B as Data channel (bounded, send_buffer_size)
    participant W as send_loop writer task
    participant K as CancellationToken
    participant Cl as Slow client

    P->>B: 1. try_send(frame)
    B-->>P: 2. Ok — frame queued
    P->>C: store(0) — grace fully restored
    W->>Cl: writer drains and flushes batches

    Note over B,Cl: client stops draining; buffer reaches capacity

    P->>B: 3. try_send(frame)
    B-->>P: TrySendError::Full
    P->>C: fetch_add(1) -> count
    alt count < grace_limit (default 15)
        P->>P: 4. warn "send buffer full — grace count/limit"; frame dropped
    else count >= grace_limit
        P->>P: 5. warn "sustained backpressure — closing slow client"
        P->>P: buzz_ws_backpressure_disconnects_total += 1
        P->>K: cancel()
        K->>W: 6. cancelled branch — drain queued control frames
        W->>Cl: 7. Close(None) — no code, no reason
        W->>W: break; cleanup path runs
    end
```

## Outcome

**Recovery path.** A client that catches up before the counter reaches the limit keeps
its connection. The first successful `try_send` stores `0`, and the connection is
indistinguishable from one that never lagged. What it does **not** get back is the
frames dropped while the buffer was full: steps 4 and 5 return `false` and discard the
frame with no retry and no replay, so a client that survives a backpressure episode has
a gap in its live stream. Recovering that gap is a client-side concern — a fresh `REQ`
against the historical read path — not something this mechanism does.

**Disconnect path.** The connection is cancelled, `buzz_ws_backpressure_disconnects_total`
is incremented, a warning naming the connection id and count is logged, and the writer
attempts a bare `Close(None)`. The client learns only that the socket closed, not why:
there is no `NOTICE`, no close code, and no reason string distinguishing a
backpressure disconnect from any other cancellation. Operators can distinguish it — from
the metric and the log line — but the client cannot.

**A caveat on that close frame.** It is attempted, not guaranteed. The close is written
onto the same sink whose failure to drain caused the disconnect in the first place. A
client that is merely slow will likely receive it; a client whose receive window has
genuinely stopped opening may be dropped without ever seeing it. This is reasoning from
the code's structure rather than an observed behaviour, and is recorded as an
`INFERENCE` at confidence 0.7 in the ledger rather than asserted as fact.

**Representative verification.** Four unit tests in `crates/buzz-relay/src/state.rs`
cover the counter arithmetic against a helper registering `grace_limit = 3`:
`send_to_resets_grace_counter_on_success` (success zeroes the counter),
`send_to_increments_grace_counter_on_full` (first and second overflow increment without
cancelling), `send_to_cancels_after_grace_limit` (the third overflow cancels), and
`shared_counter_between_direct_and_fanout` (the two send sites share one counter). They
exercise the arithmetic against a deliberately unread channel; none of them drives a
real socket.

## Configuration

Two settings shape this flow: `BUZZ_SEND_BUFFER` (`Config::send_buffer_size`, default
`1000` messages) sets how much lag a connection may absorb before any frame is refused,
and `BUZZ_SLOW_CLIENT_GRACE_LIMIT` (`Config::slow_client_grace_limit`, default `15`) sets
how many consecutive refusals are tolerated before cancellation.

**The variables themselves are `layers-configuration-relay-configuration`'s**, which
carries the canonical environment-variable table including both rows and their defaults.
This section does not restate that table; it records only what is specific to this
mechanism.

**Why 15.** The limit is not arbitrary. It was raised from a hardcoded `3` in commit
`142a5c9095` ("fix(relay): raise grace limit, add replay backpressure, and NOTICE on
oversized frames", #1226), which deleted a `const SLOW_CLIENT_GRACE_LIMIT: u8 = 3` whose
doc comment read *"Prevents transient read stalls from hard-disconnecting agents
mid-inference"* and replaced it with the configurable default. A grace of 3 was
disconnecting agents during transient read stalls; the same change made the value tunable.

**The `1000` is explicitly unmeasured.** `ADR-0018` ratifies the relay's production
sizing "without the measurements it named" and records that the relay is "very likely
running cluster-sized defaults", naming `BUZZ_SEND_BUFFER` at 1,000 per connection among
them. `verification-performance-relay` owns that gap. Treat the send-buffer default as
a value nobody has load-tested, not as a tuned one.

Two operational cautions, both read from `crates/buzz-relay/src/config.rs`:

- **Neither is validated.** Both use the silent
  `.ok().and_then(|v| v.parse().ok()).unwrap_or(default)` pattern rather than the same
  module's `positive_u64_from_env` helper, which rejects a non-positive integer with a
  `ConfigError`. A typo'd or out-of-range value falls back to the default with no error
  and no warning — the relay starts, and the setting is silently not in effect.
- **`0` is accepted and means no grace.** `slow_client_grace_limit` is a `u8` with no
  lower bound applied. Because the count is read after its increment, it is at least `1`
  whenever the comparison runs, so a limit of `0` cancels on the first buffer-full event.
  This is derived from the arithmetic rather than stated anywhere, and is recorded as an
  `INFERENCE` at confidence 0.9.

Neither variable appears in `.env.example`, which otherwise documents 74 `BUZZ_`
settings including commented tuning entries for the Redis and Postgres pool sizes — so
an operator working from that file alone would not know either setting exists. See
*Scope and omissions*.

## Boundary

This node does not describe:

- **Where the frames come from.** Subscription matching, access revalidation and the
  post-commit dispatch that produces the fan-out this mechanism disposes of are
  `architecture-flows-live-fanout`'s.
- **The connection lifecycle around this termination path.** Upgrade, NIP-42
  authentication, the auth timeout, and the shared cleanup every termination converges
  on are `architecture-flows-websocket-connection`'s. That node states the slow-client
  rule as one row of its termination table and explicitly excludes the numeric values;
  this node is the expansion of that row, not a restatement of the lifecycle.
- **How many connections are admitted in the first place.** The connection semaphore
  and `max_connections` are a separate admission-side limit, deliberately left to the
  connection-limits node (task #1123, not merged at the recorded revision and therefore
  not a relationship target here).
- **Heartbeat liveness.** The three-missed-pong disconnect in `heartbeat_loop` is a
  distinct mechanism with its own counter (`missed_pongs`) and its own 30-second
  interval. It detects a client that has stopped *responding*; this node covers a client
  that has stopped *reading*. The two meet only where a full control channel makes the
  heartbeat's `try_send` fail.
- **The two environment variables as configuration.** Their types, defaults, and place
  in the relay's full variable table belong to
  `layers-configuration-relay-configuration`. This node explains what they *do* to the
  flow, not what the configuration surface is.
- **Whether the defaults are the right values.** Load testing, measured ceilings and the
  absence of both are `verification-performance-relay`'s, which already records the
  send-buffer default as unmeasured.
- **The relay's metric catalogue.** What shape `buzz_ws_backpressure_disconnects_total`
  is and how metrics are exposed is `layers-observability-metrics`'.
- **The writer task's concurrency design.** `send_loop_inner`'s biased `select!`,
  its control-frame priority drain, and its `MAX_WS_SEND_BATCH` batching are
  `layers-lifecycle-concurrency`'s subject; this node cites the cancellation branch only.

## Relationships

- `references` `architecture-flows-live-fanout` — the upstream flow producing the frames
  this mechanism refuses.
- `references` `architecture-flows-websocket-connection` — the lifecycle this is one
  termination path within, and which explicitly defers the numeric values to here.
- `references` `implementation-crates-buzz-relay` — the crate owning `connection.rs`,
  `state.rs` and `config.rs`.
- `references` `layers-observability-metrics` — the catalogue the disconnect counter
  belongs to.
- `references` `layers-lifecycle-concurrency` — the bounded-`mpsc` and writer-loop
  primitives this flow runs on.
- `references` `layers-configuration-relay-configuration` — the canonical owner of both
  environment variables as configuration.
- `references` `verification-performance-relay` — the node recording that the
  send-buffer default is unmeasured against production load.

Each target was confirmed present on `origin/launchpad` before being written. The
sibling networking node covering connection admission and limits (#1123) is authored but
unmerged at the recorded revision, so it is named in *Boundary* as prose and is
deliberately **not** a relationship target — an edge to it would resolve locally and be a
hard error in CI.

## Scope and omissions

**This node covers** what happens to a WebSocket client that cannot keep up with the
frames the relay is sending it: the bounded per-connection buffer, the shared
consecutive-failure counter and its reset semantics, the two producer sites that drive
it, the configurable grace limit and its two environment variables — their effect on the
flow, the recorded reason the grace limit was raised from 3 to 15, and their lack of
validation — the ungraced control-channel escalation, the metric and
log lines emitted, the bare `Close(None)` the client finally receives, and the unit
tests covering the counter arithmetic.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The fan-out that produces the frames | `architecture-flows-live-fanout` |
| The surrounding connection lifecycle and shared cleanup | `architecture-flows-websocket-connection` |
| Connection admission and `max_connections` | `layers/networking/connection-limits.md` (task #1123, not merged at the recorded revision) |
| Heartbeat/missed-pong liveness detection | not yet written; no merged node claims it |
| Both environment variables as configuration (types, defaults, full variable table) | `layers-configuration-relay-configuration` |
| Whether the defaults are correctly sized; load testing and measured ceilings | `verification-performance-relay` |
| The relay's metric catalogue and exposition | `layers-observability-metrics` |
| The writer loop's batching and select design | `layers-lifecycle-concurrency` |
| Client-side recovery from a dropped frame | not yet written; the historical `REQ` read path is the mechanism, and no merged node documents recovery-after-backpressure |

**Expected but not verified when this node was written:**

- **No integration or end-to-end test exercises a real slow socket.** The four cited
  unit tests drive `ConnectionManager` against a deliberately undrained channel; a
  repository-wide search for a test naming a slow client or exercising backpressure
  against a live WebSocket found none in `crates/buzz-relay` (which has no `tests/`
  directory) or in `crates/buzz-test-client`. The whole-path behaviour — including
  whether the `Close(None)` reaches a genuinely stalled peer — is therefore unproven by
  any test in this repository.
- **The default values are not pinned by any assertion.** `defaults_are_valid` asserts
  only that `send_buffer_size` and `slow_client_grace_limit` are greater than zero, not
  that they equal `1000` and `15`. The defaults documented here were read from
  `config.rs` directly; nothing would fail if a future edit changed them.
- **Neither knob is documented in `.env.example`.** The file carries 74 `BUZZ_`
  occurrences and a "Relay (WebSocket server)" section, and documents `BUZZ_REDIS_POOL_SIZE`
  and `BUZZ_DB_POOL_SIZE` with their defaults, but a grep for `BUZZ_SEND_BUFFER` and
  `BUZZ_SLOW_CLIENT_GRACE_LIMIT` returns nothing (exit status 1). An operator working
  from that file alone would not know either setting exists. This is recorded here as a
  finding, not fixed — changing `.env.example` is a product change outside this
  documentation task's scope.
- **The two defaults have unequal provenance, and neither is measured.** The `15` has a
  recorded motivation — commit `142a5c9095` raised it from `3` because a limit of `3` was
  disconnecting agents during transient read stalls — but no measurement is attached to
  `15` specifically rather than any other larger number. The `1000` has an explicit
  disclaimer instead: `ADR-0018` records it as a cluster-sized default ratified without
  the load measurements the decision itself named. **A search for a benchmark or load
  test establishing either number found none**, and `verification-performance-relay`
  independently owns that gap. Treat both as unvalidated operating values.
- **The relay was not run.** Every claim in this node is read from source at the
  recorded revision. No relay was started, no client was stalled, and no metric or log
  line was observed being emitted.
