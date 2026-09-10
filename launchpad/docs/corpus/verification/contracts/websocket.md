---
id: verification-contracts-websocket
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-ws-client's NostrWsConnection is the shared client half of the relay's WebSocket protocol: connect() opens the socket, authenticate() waits for the relay's NIP-42 AUTH challenge and answers it, and send_event()/next_event() carry EVENT/OK and REQ/EVENT/EOSE traffic; crates/buzz-test-client's BuzzTestClient wraps this same NostrWsConnection rather than reimplementing the protocol."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
      - "crates/buzz-test-client/src/lib.rs:13-14"
      - "crates/buzz-test-client/src/lib.rs:85"
      - "crates/buzz-test-client/src/lib.rs:98"
  - statement: "buzz-relay/src/protocol.rs defines ClientMessage::parse for the five inbound NIP-01/NIP-42/NIP-45 message types (EVENT, REQ, CLOSE, COUNT, AUTH) and a RelayMessage formatter for the six outbound types (AUTH challenge, EVENT, NOTICE, EOSE, OK, CLOSED, COUNT), all as JSON arrays; REQ and COUNT additionally enforce a 256-byte subscription-id limit and a 10-filter-per-request limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:8-12"
      - "crates/buzz-relay/src/protocol.rs:16-217"
  - statement: "protocol.rs's own in-crate unit tests (parse_valid_messages, parse_req_multiple_filters, parse_invalid_messages, parse_req_sub_id_too_long_is_rejected, parse_req_too_many_filters_is_rejected, parse_req_exactly_max_filters_is_accepted, format_relay_messages) exercise ClientMessage::parse and RelayMessage's formatters entirely in-process, with no socket and no live relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:237-283"
      - "crates/buzz-relay/src/protocol.rs:286-303"
      - "crates/buzz-relay/src/protocol.rs:306-324"
      - "crates/buzz-relay/src/protocol.rs:327-335"
      - "crates/buzz-relay/src/protocol.rs:338-354"
      - "crates/buzz-relay/src/protocol.rs:357-372"
      - "crates/buzz-relay/src/protocol.rs:378-457"
  - statement: "A new WebSocket connection has AUTH_TIMEOUT = 5 seconds to complete NIP-42 authentication; connection.rs spawns a timer task that cancels the connection if AuthState is not Authenticated when the timer fires."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:29"
      - "crates/buzz-relay/src/connection.rs:251-270"
  - statement: "handlers::event::handle_event reads conn.auth_state before doing anything else with an EVENT message; when it is not AuthState::Authenticated, the handler sends OK(event_id, false, \"auth-required: not authenticated\") and returns without persisting or fanning out the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:608"
      - "crates/buzz-relay/src/handlers/event.rs:634-654"
  - statement: "handlers::req::handle_req reads conn.auth_state before registering a REQ subscription; when it is not AuthState::Authenticated, the handler sends NOTICE(\"auth-required: authenticate before subscribing\") followed by CLOSED(sub_id, \"auth-required: not authenticated\") and returns without registering the subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:50-93"
  - statement: "handlers::close::handle_close removes the subscription from the connection's local map, deregisters it from the fan-out sub_registry (releasing any pub/sub topic that subscription held), and sends CLOSED(sub_id, \"\") -- with no auth_state check at all, so a CLOSE is honored regardless of the connection's authentication state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's own module doc-comment states these are end-to-end tests against a running relay, marked #[ignore] by default so plain `cargo test` does not fail when no relay is available, run via `cargo test --test e2e_relay -- --ignored`, with the target relay overridable via the RELAY_URL environment variable (default ws://localhost:3000)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1-19"
      - "crates/buzz-test-client/tests/e2e_relay.rs:30-32"
  - statement: "test_connect_and_authenticate connects a fresh client and asserts BuzzTestClient::connect (NostrWsConnection::connect + authenticate) succeeds, then disconnects cleanly."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:210-221"
  - statement: "test_send_event_and_receive_via_subscription has one authenticated client REQ-subscribe on a channel-scoped filter and drain to EOSE, then has a second authenticated client publish an EVENT and asserts the relay's OK response is accepted, then asserts the first client receives that same event as a live EVENT message on its subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:358-415"
  - statement: "test_close_subscription_stops_delivery subscribes, drains to EOSE, sends CLOSE for that subscription id, then publishes a matching event and asserts no EVENT is delivered to the closed subscription within a bounded wait, while the publish itself is still accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:537-588"
  - statement: "test_unauthenticated_rejected connects without completing NIP-42 authentication and asserts that a subsequent attempt to publish an event either returns OK with accepted=false, or fails because the relay closed the connection, or times out waiting for a response -- explicitly treating an accepted publish as the one disqualifying outcome."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:590-625"
  - statement: ".github/workflows/ci.yml's only two invocations of the e2e_relay test binary select the `invite` and `nip43_membership_snapshots_are_rejected` test-name filters; no CI job runs test_connect_and_authenticate, test_send_event_and_receive_via_subscription, test_close_subscription_stops_delivery, or test_unauthenticated_rejected, so these four tests currently execute only when a developer invokes them directly against a running relay."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:893"
      - ".github/workflows/ci.yml:894"
  - statement: "Justfile's test-unit recipe runs buzz-relay's --lib suite scoped to a nextest filter of test(/^api::admin::/) (minus two named exclusions) rather than the crate's full --lib target, and its own comment states this scoping is deliberate because nothing in CI runs `cargo test --workspace`; protocol::tests does not match that filter and is therefore not selected by this recipe."
    entry_class: FACT
    evidence:
      - "Justfile:361-383"
      - "Justfile:384-385"
  - statement: "scripts/run-tests.sh's unit and integration modes enumerate cargo test/nextest invocations package-by-package and never pass -p buzz-relay in either mode; its 'workspace integration tests' step runs `cargo test --test '*'`, which selects integration-test binaries (files under a crate's tests/ directory) and does not execute a #[cfg(test)] module compiled into a library target such as protocol::tests."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:78-124"
      - "scripts/run-tests.sh:128-142"
  - statement: "lefthook.yml's pre-push rust-tests hook runs exactly `just test-unit`, so the pre-push gate inherits the same api::admin::-scoped filter and does not execute protocol::tests either; no other lefthook.yml hook runs a Rust test command."
    entry_class: FACT
    evidence:
      - "lefthook.yml:98-101"
  - statement: "Because protocol::tests is excluded from every automated selection identified above, it is not #[ignore]d and would pass if invoked, but its current execution depends on a developer running it directly (`cargo test -p buzz-relay --lib protocol::tests` or an equivalent nextest filter) rather than on any CI job, `just ci`, `just test`, or pre-push hook."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/protocol.rs:219-236"
      - "Justfile:384-385"
      - "scripts/run-tests.sh:78-124"
      - "lefthook.yml:98-101"
    confidence: 0.8
  - statement: "just setup starts the Docker-based Postgres/Redis services and applies migrations, and just relay (or just relay-release) starts a relay binary that advertises ws://localhost:3000 by default, matching the RELAY_URL default e2e_relay.rs itself falls back to."
    entry_class: FACT
    evidence:
      - "TESTING.md:33"
      - "TESTING.md:311"
      - "TESTING.md:318"
  - statement: "ADR-0020 records that every test in this repository needing a live relay is marked #[ignore], specifically so a plain `cargo test` invocation never executes them, and TESTING.md documents this repository's live multi-agent E2E testing practice against a real relay built from the same source tree."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "TESTING.md"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: corpus-standard-test-references
---

# WebSocket protocol contract

## Purpose and boundary

This node documents one obligation: that the relay's primary NIP-01 WebSocket
transport -- the message-framing shapes it accepts/emits, the NIP-42
authentication gate, and the EVENT/REQ/EOSE/CLOSE message lifecycle built on
top of them -- behaves as a coherent, testable contract, and it names the
tests that currently exercise that contract and how each one is (or is not)
run today. It does not cover the WebSocket *upgrade* handshake itself
(host-to-community binding, the pre-upgrade 404/503 paths, connection-count
admission) -- that is `architecture-flows-websocket-connection`'s subject --
nor the cryptographic detail of NIP-42 verification (challenge generation,
signature/timestamp/relay-URL checks) -- that is
`architecture-flows-websocket-authentication`'s. This node starts from an
already-open, already-challenged connection and covers what a client can and
cannot do with NIP-01 messages over it.

## Obligation

> Over one WebSocket connection to the relay, a client that completes NIP-42
> AUTH before the connection's 5-second admission window elapses can publish
> an EVENT and receive a matching OK, open a REQ subscription and receive
> matching stored/live EVENT messages terminated by EOSE, and stop further
> delivery for that subscription with CLOSE -- while a client that has not
> completed AUTH has its EVENT rejected with `OK ... false` and its REQ
> rejected with `CLOSED`, both carrying an `auth-required:` reason, rather
> than being silently accepted or silently dropped.

Two negative/error cases are part of this contract and named explicitly:

- **Unauthenticated EVENT**: rejected via `OK(event_id, false, "auth-required:
  not authenticated")`, never persisted or fanned out
  (`crates/buzz-relay/src/handlers/event.rs:634-654`).
- **Unauthenticated REQ**: rejected via `NOTICE` followed by
  `CLOSED(sub_id, "auth-required: not authenticated")`, the subscription is
  never registered (`crates/buzz-relay/src/handlers/req.rs:50-93`).

CLOSE is deliberately *not* a negative case here: `handle_close` performs no
auth check at all, so a CLOSE is honored regardless of authentication state
(`crates/buzz-relay/src/handlers/close.rs`). That asymmetry is part of what
this node documents, not an omission.

## Verifying test(s)

Message-framing shapes (in-process, no relay):

- `crates/buzz-relay/src/protocol.rs` -- `protocol::tests::parse_valid_messages`,
  `parse_req_multiple_filters`, `parse_invalid_messages`,
  `parse_req_sub_id_too_long_is_rejected`,
  `parse_req_too_many_filters_is_rejected`,
  `parse_req_exactly_max_filters_is_accepted`, `format_relay_messages` --
  cover `ClientMessage::parse` accepting EVENT/REQ/CLOSE/AUTH and rejecting
  malformed or oversized REQ/COUNT input, and `RelayMessage`'s formatters for
  AUTH/EVENT/NOTICE/EOSE/OK/CLOSED.

Full lifecycle against a live relay (`crates/buzz-test-client/tests/e2e_relay.rs`):

- `test_connect_and_authenticate` (line 212) -- connect + NIP-42 AUTH round
  trip succeeds; clean disconnect.
- `test_send_event_and_receive_via_subscription` (line 360) -- REQ subscribe
  + EOSE, EVENT publish + OK from one authenticated client, live EVENT
  delivery to a second authenticated client's open subscription.
- `test_close_subscription_stops_delivery` (line 539) -- CLOSE a subscription,
  then confirm a matching publish no longer delivers to it (the publish
  itself is still accepted).
- `test_unauthenticated_rejected` (line 592) -- a connection that never
  completes AUTH has its publish rejected, its connection closed, or its
  request time out; an accepted publish is the one outcome that fails the
  test.

## How to run it

Message-framing unit tests -- no infrastructure needed:

```bash
cargo test -p buzz-relay --lib protocol::tests -- --nocapture
# or, with nextest:
cargo nextest run -p buzz-relay --lib -E 'test(/^protocol::tests::/)'
```

Full-lifecycle tests -- need a running relay backed by Postgres and Redis:

```bash
just setup   # starts Postgres/Redis via Docker, runs migrations
just relay   # starts a relay advertising ws://localhost:3000

# in another shell:
cargo test -p buzz-test-client --test e2e_relay -- --ignored \
  test_connect_and_authenticate \
  test_send_event_and_receive_via_subscription \
  test_close_subscription_stops_delivery \
  test_unauthenticated_rejected
```

`RELAY_URL` overrides the target relay if it is not at the default
`ws://localhost:3000` (see `TESTING.md`).

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`, and gated in two
different ways that are worth telling apart:

| Verifying test(s) | Gate | What actually runs it today |
|---|---|---|
| `protocol::tests::*` | Not `#[ignore]`d, but excluded from every automated selection: `just test-unit`'s `buzz-relay --lib` invocation is scoped to `test(/^api::admin::/)` only, `scripts/run-tests.sh` never passes `-p buzz-relay`, and the pre-push hook runs exactly `just test-unit`. | Only a developer invoking the test directly. |
| `test_connect_and_authenticate`, `test_send_event_and_receive_via_subscription`, `test_close_subscription_stops_delivery`, `test_unauthenticated_rejected` | `#[ignore]`d by the file's own convention (needs a live relay); CI's two `e2e_relay` invocations filter on `invite` and `nip43_membership_snapshots_are_rejected` only, so none of these four names are selected. | Only a developer invoking them directly with `-- --ignored <name>` against a running relay. |

Neither half of this obligation is exercised by any CI job, `just ci`, `just
test`, or the pre-push hook today. All six tests would pass if run directly
at the recorded revision -- that claim rests on reading the tests and their
call sites, not on an executed run recorded in this ledger, and is why the
"excluded from selection" statement above is an `INFERENCE` rather than a
`FACT`.

## Limits

- **Framing tests prove shape, not the live protocol.** `protocol::tests`
  proves `ClientMessage::parse`/`RelayMessage`'s formatters round-trip
  correctly in-process. It says nothing about what happens once those
  messages travel over a real socket, through `AuthState`, admission, and the
  handler dispatch in `connection.rs` -- that is what the e2e tests are for.
- **The e2e tests cover one channel-scoped, two-client happy path plus one
  rejection path.** They do not exercise COUNT, multiple concurrent
  subscriptions on one connection, NIP-45 count filters, or CLOSE racing a
  live delivery. `test_multiple_concurrent_clients` and
  `test_subscription_filters_by_kind` exist in the same file and touch
  adjacent ground but are not claimed here as verifying *this* obligation's
  statement.
- **The unauthenticated-rejection test asserts an outcome set, not one
  specific response.** `test_unauthenticated_rejected` accepts `OK
  {accepted:false}`, a closed connection, or a timeout as equally valid --
  it does not pin down which of those three the relay actually produces at
  the recorded revision, only that an *accepted* publish would fail it.
- **Nothing here re-executed the tests.** Every claim about what a test does
  is a reading of its source, not a recorded run; the citations above are
  code the author opened, not a `cargo test` transcript. See *Current
  enforcement status* for exactly what that limits about the `FACT`/
  `INFERENCE` split above.
- **The 5-second `AUTH_TIMEOUT` and the `auth-required:` message strings are
  cited from source, not observed on the wire.** No test in this ledger
  asserts on the timeout firing or captures the literal string a client
  receives; `format_relay_messages`'s `ok_rejected` case exercises the `OK`
  formatter with an arbitrary rejection string, not this specific one.

## Scope and omissions

**This node covers** the message-framing shapes for EVENT/REQ/CLOSE/COUNT/AUTH
and the outbound relay-message formatters, the NIP-42-gated accept/reject
behavior for EVENT and REQ, CLOSE's lack of an auth gate, the tests that
exercise each of those, and — as a first-class part of this node, not an
aside — the current, precise gap between "a test exists and would pass" and
"a test is actually executed by any automated lane."

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The WebSocket upgrade handshake: host-to-community binding, pre-upgrade 404/503, connection-count admission | `architecture-flows-websocket-connection` |
| NIP-42 challenge generation and verification internals (signature, timestamp window, relay-URL normalization) | `architecture-flows-websocket-authentication` |
| COUNT (NIP-45), multiple concurrent subscriptions per connection, rate-limiting/admission behavior on the WS path | Not yet a corpus node at this revision |
| Whether this repository's test-selection gaps (protocol::tests unselected; the four e2e tests unselected by CI) should be closed, and how | Not decided here; this node reports the gap, it does not propose or own the fix |
| The generic mechanics of citing a test as evidence (shapes, flakiness, staleness) | `corpus-standard-test-references` |

**Expected but not verified when this node was written:**

- **None of the six named tests was actually executed while authoring this
  node.** Every claim about pass/fail behavior is derived from reading the
  test source and the handler code it exercises, not from a recorded run —
  consistent with the `FACT`/`INFERENCE` split in the ledger above, and named
  again here per `AGENTS.md`'s own creation checklist.
- **Whether the exact string `"auth-required: not authenticated"` (or any of
  its siblings) is stable API surface a client should match on, versus
  free-form NOTICE text that may change, was not established.** Nothing in
  the repository documents these strings as a versioned contract.
- **Whether `test_multiple_concurrent_clients` or
  `test_subscription_filters_by_kind` (both in the same file, both
  `#[ignore]`d, both also unselected by CI's `e2e_relay` filters) should be
  folded into this obligation's verifying-test list was considered and
  declined** — they exercise adjacent behavior (concurrency, kind filtering)
  rather than the connect/auth/EVENT/REQ/CLOSE lifecycle this node states,
  and folding them in would widen the obligation past one testable sentence.
