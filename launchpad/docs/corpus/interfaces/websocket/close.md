---
id: interfaces-websocket-close
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c703ddf33fcda09e2a8399480061c4bda08bf162."
    entry_class: FACT
    evidence:
      - "commit c703ddf33fcda09e2a8399480061c4bda08bf162"
  - statement: "node.schema.json's type enum encodes the corpus's combined interfaces/events surface as the single value interfaces-events, and the merged interface template (corpus-template-interface) states that an interface-shaped instance node carries this value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "ClientMessage::Close(String) is the parsed representation of a client CLOSE frame; ClientMessage::parse's \"CLOSE\" arm requires a two-element array whose second element is a JSON string (the subscription id), returning RelayError::InvalidMessage if the array has fewer than two elements or the second element is not a string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:26-27"
      - "crates/buzz-relay/src/protocol.rs:146-159"
  - statement: "Unlike REQ and COUNT, the CLOSE parse arm does not check the subscription id against MAX_SUB_ID_LENGTH (256 bytes) or reject an empty string; only REQ (line 80-90) and COUNT (line 120-129) enforce those NIP-11-advertised limits."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:8-9"
      - "crates/buzz-relay/src/protocol.rs:74-90"
      - "crates/buzz-relay/src/protocol.rs:113-129"
      - "crates/buzz-relay/src/protocol.rs:146-159"
  - statement: "RelayMessage::closed(sub_id, message) formats the relay's acknowledgement as the JSON array [\"CLOSED\", sub_id, message]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:208-211"
  - statement: "handle_close removes the subscription id from the connection's own subscriptions map and from the shared sub_registry, releases the connection's pubsub topic reservation (global or per-channel) if a registered subscription was actually removed, and then unconditionally sends a CLOSED acknowledgement with an empty message -- the same acknowledgement is sent whether or not the subscription id existed, so closing an unknown or already-closed subscription id is not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:10-35"
  - statement: "Because an absent subscription id is a silent no-op rather than an error path in handle_close, sending CLOSE twice for the same subscription id, or for an id that was never opened, is idempotent from the caller's perspective: both cases receive the identical [\"CLOSED\", sub_id, \"\"] acknowledgement."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:10-35"
    confidence: 0.85
  - statement: "The relay's message dispatch match arm for ClientMessage::Close calls handlers::close::handle_close directly and awaits it inline on the connection's own receive task, unlike the Event, Req and Count arms, which first acquire a permit from state.handler_semaphore and run the handler on a spawned task with its own tracing span."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:560-641"
  - statement: "handle_text_message parses each incoming WebSocket text frame with ClientMessage::parse before dispatch; a parse failure (including a malformed CLOSE frame -- non-array, empty array, or non-string second element) sends RelayMessage::notice(\"invalid message: <error>\") to the client and returns without reaching the dispatch match, so a malformed CLOSE never produces a CLOSED reply."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:547-553"
  - statement: "enforce_ws_admission, called on every parsed message before dispatch, returns true immediately (skipping all per-principal rate-limit checks) for any message that is not ClientMessage::Event, ClientMessage::Req, or ClientMessage::Count -- CLOSE (and AUTH) are therefore exempt from the WebSocket admission/rate-limiting path that gates event submission and subscription/count requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:652-660"
  - statement: "Per-connection authentication is enforced at the connection level, not per message: an auth_timeout_task spawned when the connection is accepted cancels the whole connection if it is not in AuthState::Authenticated within AUTH_TIMEOUT of connecting, driven by NIP-42 AUTH rather than by any check inside the CLOSE dispatch path itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:249-268"
  - statement: "buzz-test-client's close_subscription(sub_id) helper sends the raw JSON array [\"CLOSE\", sub_id] as a WebSocket text frame, matching NIP-01's client-to-relay CLOSE shape exactly."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs:158-161"
  - statement: "The end-to-end test test_close_subscription_stops_delivery opens a subscription, waits for EOSE, sends CLOSE for that subscription id, then publishes a matching event and asserts the client never receives it (a timeout, or a non-EVENT message, is accepted; receiving the EVENT fails the test) -- demonstrating that a live subscription actually stops receiving fan-out after CLOSE is processed."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:539-585"
  - statement: "NIP-01 defines CLOSE (client to relay) as [\"CLOSE\", <subscription_id>], \"used to stop previous subscriptions\", and CLOSED (relay to client) as [\"CLOSED\", <subscription_id>, <message>], sent either when the relay refuses to fulfill a subscription request or when it terminates an active subscription before client disconnection."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/01.md"
  - statement: "Issue #1019 requires that exactly one hand-authored canonical corpus document is created for this task, with any other changed corpus file limited to deterministic generated output."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1019 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
  - type: part-of
    target: architecture-flows-websocket-connection
---

# WebSocket CLOSE: interface

This node documents the relay's handling of the NIP-01 **CLOSE** client message --
the WebSocket frame a connected client sends to stop a subscription it previously
opened with REQ. The boundary is the relay's WebSocket message-dispatch surface
(`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/protocol.rs`,
`crates/buzz-relay/src/handlers/close.rs`); the two sides are a Nostr client
(human client, agent, or test harness) and the Buzz relay, exchanging plain-text
JSON-array frames over an already-established, already-or-not-yet-authenticated
WebSocket connection.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Client sends `["CLOSE", <subscription_id>]` | `ClientMessage::Close` / `ClientMessage::parse`'s `"CLOSE"` arm (`crates/buzz-relay/src/protocol.rs:26-27,146-159`); NIP-01 | Requests that the relay stop an active subscription previously opened by REQ on the same connection. |
| Relay processes CLOSE | `handlers::close::handle_close` (`crates/buzz-relay/src/handlers/close.rs:10-35`), invoked synchronously from the dispatch match (`crates/buzz-relay/src/connection.rs:639-641`) | Removes the subscription from the connection's own subscription map and the shared `sub_registry`, releases the connection's pub/sub topic reservation if one was held, then replies. |
| Relay sends `["CLOSED", <subscription_id>, <message>]` | `RelayMessage::closed` (`crates/buzz-relay/src/protocol.rs:208-211`); NIP-01 | Acknowledges the CLOSE. For a client-initiated CLOSE this always carries an empty `message`; the same `CLOSED` frame shape is also used elsewhere in the relay to terminate a subscription server-side (a different operation, not covered here -- see *Boundary*). |

## Contract and stability

- **Idempotent by construction.** `handle_close` removes-if-present rather than
  requiring the subscription id to exist; sending CLOSE for an unknown or
  already-closed subscription id returns the identical
  `["CLOSED", sub_id, ""]` acknowledgement as a successful close, never an error
  (`crates/buzz-relay/src/handlers/close.rs:10-35`).
- **No admission/rate-limit gate.** `enforce_ws_admission` only rate-limits
  `EVENT`, `REQ` and `COUNT`; it returns `true` immediately for every other
  message type, so CLOSE cannot be rejected for exceeding a per-principal
  WebSocket rate limit the way REQ/COUNT/EVENT can
  (`crates/buzz-relay/src/connection.rs:652-660`).
- **No per-message authentication check.** Authentication is a connection-wide
  invariant enforced by a timeout task that cancels the whole connection if it
  never reaches `AuthState::Authenticated` within `AUTH_TIMEOUT` of connecting;
  there is no additional authentication or authorization check inside the CLOSE
  path itself beyond that connection-level gate
  (`crates/buzz-relay/src/connection.rs:249-268`). A client may only ever close
  subscriptions recorded in its own connection's subscription map, so CLOSE
  cannot reference another connection's subscription id.
- **Malformed input is a NOTICE, not a CLOSED.** A CLOSE frame that fails to
  parse (not a two-element array, or a non-string second element) never reaches
  `handle_close`; `handle_text_message` sends
  `["NOTICE", "invalid message: <parse error>"]` and stops
  (`crates/buzz-relay/src/connection.rs:547-553`).
- **Looser input validation than its siblings.** REQ and COUNT reject a
  subscription id over 256 bytes (`MAX_SUB_ID_LENGTH`) or an empty string; the
  CLOSE parse arm applies neither check, accepting any JSON string as the
  subscription id (`crates/buzz-relay/src/protocol.rs:8-9,74-90,113-129,146-159`).
  This is reported here as an observed asymmetry in current behavior, not as an
  endorsed contract -- no claim is made about whether it is intentional.
- **Ordering/versioning.** CLOSE carries no protocol version or sequence
  number; NIP-01 defines its shape as a fixed two-element array and this
  relay's parser enforces exactly that shape. There is no compatibility
  variant to negotiate.

## Examples

Valid CLOSE and its acknowledgement:

```json
["CLOSE", "sub1"]
```
```json
["CLOSED", "sub1", ""]
```

Malformed CLOSE (missing subscription id) and the resulting failure:

```json
["CLOSE"]
```
```json
["NOTICE", "invalid message: CLOSE requires sub_id"]
```

## Boundary

This node does not describe:
- **REQ, EVENT, COUNT or AUTH's own wire contracts.** Each is `ClientMessage`'s
  own variant with its own parse arm and handler
  (`crates/buzz-relay/src/protocol.rs`); they are named above only to place
  CLOSE among its siblings (e.g. which of them share the admission gate CLOSE
  is exempt from), not documented in their own right here.
- **The server-initiated CLOSED path.** The relay also sends `["CLOSED", ...]`
  frames it did not receive a CLOSE for -- for example to refuse a REQ that
  violates a NIP-11 limit (`crates/buzz-relay/src/connection.rs` overflow and
  restricted-subscription paths) or when a community is deleted
  (`crates/buzz-relay/src/state.rs`). That is relay-initiated subscription
  termination, a different operation from the client-initiated CLOSE this node
  documents, even though both use the same `RelayMessage::closed` formatter.
- **A single Nostr event kind's own wire contract.** CLOSE operates on a
  subscription id, not an event; it has no associated event kind.
- **A field-by-field, domain-expert-depth API-parameter catalogue.** The
  Operations table above is the complete operation list for this narrow
  interface, not a reference-depth cataloguing exercise.

## Relationships

- `implements: corpus-template-interface` -- this node is an instance of the
  merged interface template.
- `part-of: architecture-flows-websocket-connection` -- CLOSE is one message
  in the broader WebSocket connection lifecycle that node documents.

## Scope and omissions

**This node covers** the client-initiated CLOSE message: its wire shape, the
relay code that parses and handles it, its idempotency, its exemption from
per-principal rate limiting, how authentication and malformed input are
handled around it, and its NIP-01 authority.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| REQ, EVENT, COUNT and AUTH's own operations and contracts | Future corpus tasks for each, if not already covered |
| The relay-initiated (server-side) CLOSED path used for NIP-11 limit rejection and community deletion | A future corpus task on subscription lifecycle / server-initiated termination, if one is created |
| A single Nostr event kind's wire contract | `#1337`'s event-kind template, not applicable here since CLOSE has no associated kind |
| Field-by-field API-reference-depth cataloguing | `#1346`/`#1532` (reference / API Reference gap, undecided corpus-wide) |

**Expected but not verified when this node was written:**
- **Whether the CLOSE-vs-REQ/COUNT subscription-id validation asymmetry
  (no length/emptiness check on CLOSE) is a known, intentional gap or an
  oversight.** No issue, comment, or test was found addressing it either way;
  it is reported in *Contract and stability* as an observed fact about current
  code, not resolved here, and no code change is made to address it (out of
  this task's scope per issue #1019's own exclusions).
- **Whether NIP-11's advertised limits document anything specific to CLOSE.**
  This repository's NIP-11 implementation was not re-inspected beyond the
  `MAX_SUB_ID_LENGTH`/`MAX_FILTERS_PER_REQ` constants already cited above,
  which are applied to REQ/COUNT, not CLOSE.
