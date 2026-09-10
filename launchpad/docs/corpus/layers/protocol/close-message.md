---
id: layers-protocol-close-message
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "protocol.rs declares ClientMessage::Close(String) with the doc comment 'A CLOSE message cancelling an active subscription', and its parse function's \"CLOSE\" arm returns that variant carrying the subscription id taken from the array's second element."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "The \"CLOSE\" arm rejects exactly two shapes: an array shorter than two elements, with InvalidMessage(\"CLOSE requires sub_id\"), and a second element that is not a JSON string, with InvalidMessage(\"CLOSE sub_id must be a string\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "Unlike the REQ and COUNT arms in the same parse function, the CLOSE arm applies neither the empty-string rejection nor the MAX_SUB_ID_LENGTH limit of 256 bytes that protocol.rs declares as the NIP-11 advertised max_subid_length."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "protocol.rs's module documentation records its subject as 'NIP-01 client/relay message parsing and formatting', which is where this node's association of CLOSE with NIP-01 comes from rather than from any copy of the NIP-01 text."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "handle_close removes the subscription id from the connection's own subscriptions map, then calls state.sub_registry.remove_subscription for the same connection and id, and only if that returns Some does it call pubsub.release_topic for the removed subscription's global scope and for each of its channel ids."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "handle_close sends RelayMessage::closed(&sub_id, \"\") unconditionally, outside the Some branch, so a CLOSE naming a subscription id the relay never held is acknowledged with the same empty-reason CLOSED as one naming a live subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "close.rs carries an inline comment stating that deregistration from the fan-out index happens before the CLOSED is sent so that no new messages are routed to the subscription after the client's CLOSE is acknowledged."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "remove_subscription returns None when the connection has no entry in the registry or the connection's map has no such subscription id, and decrements the buzz_subscriptions_active gauge only on the path where a subscription was actually removed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "connection.rs's handle_text_message dispatches ClientMessage::Close by awaiting handlers::close::handle_close directly, whereas the Event, Req and Count arms each first try_acquire_owned a permit from state.handler_semaphore and spawn their handler, replying with a rate-limited message when no permit is available."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "enforce_ws_admission returns true immediately for any message that is not Event, Req or Count, so a CLOSE is never charged against the WsEvents admission budget that guards the other three."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "When ClientMessage::parse returns an error, handle_text_message replies with RelayMessage::notice formatted as 'invalid message: {e}' and returns, so a malformed CLOSE produces a NOTICE and never a CLOSED."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "RelayMessage::closed formats the relay-to-client array [\"CLOSED\", sub_id, message], and its doc comment describes it as indicating a subscription was terminated by the relay -- a distinct message from the client-to-relay CLOSE this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "ClientMessage::parse matches exactly five message types -- EVENT, REQ, COUNT, CLOSE and AUTH -- and returns InvalidMessage(\"unknown message type: {other}\") for anything else, so there is no CLOSED arm and a relay never parses one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "A WebSocket Close frame is handled on a different path entirely: connection.rs's receive loop matches Some(Ok(WsMessage::Close(_))) alongside a closed stream and breaks out of the loop with the log 'WebSocket closed by client', never reaching ClientMessage::parse."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_req consults the same conn.subscriptions map that handle_close removes from, and replies with CLOSED carrying 'error: too many subscriptions' when the map does not already contain the requested id and its length has reached MAX_SUBSCRIPTIONS, so a successful CLOSE is what returns a subscription slot to the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "A REQ reusing an id the connection already holds is not charged against the subscription limit -- handle_req's guard is conditioned on the id being absent from the map -- and handle_req then inserts the id and filters into that map unconditionally, so re-sending REQ under an existing id replaces the subscription rather than requiring a CLOSE first."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "release_topic decrements a per-topic refcount held in desired_topics, removes the key and records a became_zero transition when the count reaches zero, and logs a warning and returns early when called for a topic that was never retained."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Three first-party clients send the CLOSE wire message: BuzzTestClient::close_subscription sends [\"CLOSE\", sub_id]; the desktop native relay client's reconcile pass sends [\"CLOSE\", id] for each open subscription no longer in the desired set; and the mobile relay session sends ['CLOSE', subId]."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs"
      - "desktop/src-tauri/src/native_relay_client.rs"
      - "mobile/lib/shared/relay/relay_session.dart"
  - statement: "protocol.rs's parse unit test asserts that the raw frame [\"CLOSE\", \"sub1\"] parses to ClientMessage::Close carrying \"sub1\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "e2e_relay.rs's test_close_subscription_stops_delivery subscribes, waits for EOSE, closes the subscription, publishes a further event and asserts that no EVENT is delivered for it; the test carries #[ignore] and so does not run in the default cargo test invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "This repository contains no upstream numbered NIP specification; docs/nips holds only Buzz's own two-letter NIPs, so no claim about what NIP-01 mandates can rest on a repository path here."
    entry_class: FACT
    evidence:
      - "ls(docs/nips) -> NIP-AA.md, NIP-AE.md, NIP-AM.md, NIP-AO.md, NIP-AP.md, NIP-CW.md, NIP-DV.md, NIP-ER.md, NIP-FI*.md, NIP-GS.md, NIP-IA.md, NIP-MP.md, NIP-OA.md and further two-letter codes; no NIP-01.md"
  - statement: "Because the CLOSED acknowledgement is sent outside the Some branch that proves a subscription was removed, a client cannot distinguish from the reply alone between having closed a live subscription, having closed one the relay had already terminated, and having named an id that never existed."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
      - "crates/buzz-relay/src/subscription.rs"
    confidence: 0.9
  - statement: "Awaiting handle_close inline rather than spawning it under a handler_semaphore permit means subscription teardown cannot be shed when the relay is saturated, which is the condition under which shedding it would be most costly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/close.rs"
    confidence: 0.6
  - statement: "Upstream NIP-01 defines CLOSE as the client-to-relay message [\"CLOSE\", <subscription_id>] used to stop a previous subscription, and CLOSED as a separate relay-to-client message; that specification text is not present in this repository and this node does not treat it as a repository fact."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "nostr-protocol/nips NIP-01, relayed via the Feature #609 dispatch brief; no copy of the specification exists in this repository"
  - statement: "The consequence of release_topic's refcount reaching zero -- that it is what drives the Redis UNSUBSCRIBE -- is documented by a sibling corpus node under issue #1128, not here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1128 (sibling corpus task, committed and not yet merged at the recorded revision)"
  - statement: "The relay-to-client CLOSED message is issue #1147's subject and the WebSocket transport close frame is issue #1122's subject, so both are named as boundaries here rather than documented."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1147 and #1122 (sibling corpus tasks under Feature #609)"
  - statement: "Issue #1146's definition of done requires one hand-authored canonical document with schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, a definition in one sentence before deeper explanation, explicit boundaries against what the concept must not be confused with, links rather than duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1146 definition of done"
relationships:
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-pubsub
  - type: references
    target: verification-contracts-nostr
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: verification-e2e-relay
---

# The CLOSE message

## Definition

**`CLOSE` is the client-to-relay message `["CLOSE", <subscription_id>]` by which a client
ends a subscription it previously opened with `REQ`.** It is a single verb with a single
argument: the client's own subscription id. It carries no filters, no reason and no
payload beyond that id.

Three things share the word "close" on this connection, and confusing them is the most
common way to misread the relay's behaviour. This node documents **only the first**.

| Name | Direction | What it is | Owned by |
|---|---|---|---|
| **`CLOSE`** | client → relay | Ends one subscription. The subject of this node. | here |
| **`CLOSED`** | relay → client | Tells a client that one of its subscriptions has been terminated, with a reason string. | issue #1147 |
| **WebSocket close frame** | transport level | A frame ending the whole connection, and with it every subscription on it. | issue #1122 |

The distinction is not merely nominal — the three travel different code paths. `CLOSE`
is a JSON text frame parsed by `ClientMessage::parse` into `ClientMessage::Close`.
`CLOSED` is a string the relay *formats* with `RelayMessage::closed`; the parser has no
arm for it, because a relay never receives one. A WebSocket close frame never reaches
`ClientMessage::parse` at all: `connection.rs`'s receive loop matches
`WsMessage::Close(_)` alongside an exhausted stream and simply breaks out of the loop,
logging "WebSocket closed by client".

A further asymmetry is worth stating plainly, because the names invite the wrong
inference: **the relay's reply to a `CLOSE` is a `CLOSED`.** `handle_close` finishes by
sending `RelayMessage::closed(&sub_id, "")` — a `CLOSED` with an empty reason. So a
`CLOSED` on the wire does *not* imply the relay terminated the subscription on its own
initiative; it may equally be the acknowledgement of the client's own `CLOSE`. What
distinguishes them is the reason string, and interpreting that string is #1147's
subject, not this node's.

**Out of scope of the term itself.** `CLOSE` does not disconnect, does not authenticate,
does not accept filters, and does not carry a reason. A client that wants to *change* a
subscription does not need to `CLOSE` it first: `handle_req` inserts the id and its
filters into the connection's map unconditionally, and its subscription-limit guard is
conditioned on the id being *absent*, so re-sending `REQ` under an existing id replaces
the subscription without being charged against the limit.

## What the relay does with one

`crates/buzz-relay/src/handlers/close.rs` is thirty-five lines and does four things, in
this order:

1. Removes the id from the connection's own `subscriptions` map.
2. Removes it from the shared `sub_registry` fan-out index, which returns
   `Some(removed)` only if a subscription was actually there.
3. **Only inside that `Some`**, releases the pubsub topics the removed subscription had
   retained — the global topic if its scope was global, and one per channel id in its
   scope.
4. **Outside that `Some`**, unconditionally sends the `CLOSED` acknowledgement.

Step 3 before step 4 is deliberate, and `close.rs` says so in a comment: deregistering
from the fan-out index before acknowledging means no further messages are routed to that
subscription after the client has been told it is gone.

The consequence of the release in step 3 — that a topic's refcount falling to zero is
what drives the Redis `UNSUBSCRIBE` — belongs to the pubsub fan-out node under issue
#1128, not here. What matters at this layer is only that a `CLOSE` is the event that
decrements the count.

## Its edges

**A malformed `CLOSE` gets a `NOTICE`, not a `CLOSED`.** The parser rejects exactly two
shapes — an array shorter than two elements (`"CLOSE requires sub_id"`) and a
non-string second element (`"CLOSE sub_id must be a string"`). Either produces a
`RelayError::InvalidMessage`, and `handle_text_message` turns any parse error into
`["NOTICE", "invalid message: …"]` and returns. The handler is never reached, so no
`CLOSED` is sent and the subscription id — whatever it was — is untouched.

**An unknown subscription id gets a `CLOSED` anyway.** Because the acknowledgement sits
outside the `Some` branch, a syntactically valid `CLOSE` naming an id the relay never
held removes nothing, releases no topic, decrements no gauge, and still receives
`["CLOSED", "<that id>", ""]`. A client therefore cannot tell from the reply alone
whether it closed a live subscription, closed one the relay had already terminated, or
named an id that never existed. Treat a `CLOSED` in response to a `CLOSE` as an
acknowledgement that the id is now closed, not as evidence it was ever open.

**`CLOSE`'s subscription id is validated more loosely than `REQ`'s or `COUNT`'s.** Both
of those arms reject an empty id and enforce `MAX_SUB_ID_LENGTH` (256 bytes, which
`protocol.rs` names as the NIP-11 advertised `max_subid_length`). The `CLOSE` arm applies
neither. `["CLOSE", ""]` parses cleanly and is answered with `["CLOSED", "", ""]`.

| | `REQ` / `COUNT` sub id | `CLOSE` sub id |
|---|---|---|
| Must be a string | yes | yes |
| Rejected when empty | yes | **no** |
| Length capped at 256 bytes | yes | **no** |

**`CLOSE` is exempt from two load controls the other verbs carry.**
`enforce_ws_admission` returns `true` immediately for anything that is not `EVENT`,
`REQ` or `COUNT`, so a `CLOSE` is never charged against the `WsEvents` admission budget.
And where the `EVENT`, `REQ` and `COUNT` arms each take a `handler_semaphore` permit and
spawn their handler — replying "rate-limited: too many concurrent requests" when none is
available — the `Close` arm simply awaits `handle_close` inline. Subscription teardown
cannot be shed under load. That reads as intentional: shedding a `CLOSE` would leave the
relay holding a subscription the client believes it has released, precisely when the
relay is most in need of releasing it.

## Why it matters

**It frees a subscription slot.** `handle_req` reads the same `conn.subscriptions` map
`handle_close` removes from, and answers a `REQ` for a *new* id with
`CLOSED "error: too many subscriptions"` once the map has reached `MAX_SUBSCRIPTIONS`. A
long-lived client that opens subscriptions under fresh ids and never closes them will hit
that ceiling; `CLOSE` is what gives the slot back.

**It is how a reconciling client converges.** The desktop native relay client's reconcile
pass sends `["CLOSE", id]` for every open subscription no longer in its desired set,
before re-opening what is desired. The mobile relay session sends `['CLOSE', subId]` on
cleanup. `BuzzTestClient::close_subscription` is the same message for tests. All three
are the same one-line wire frame.

**It stops delivery, and that is what the test asserts.**
`test_close_subscription_stops_delivery` subscribes, waits for `EOSE`, closes, publishes
a further matching event, and asserts nothing is delivered. It is `#[ignore]`-gated —
it needs a running relay — so it does not run in a default `cargo test`.

## Related nodes

The typed `relationships` edges above carry the links: `implementation-crates-buzz-relay`
for the crate that parses and handles this message,
`architecture-flows-websocket-connection` for the connection whose receive loop dispatches
it, `implementation-crates-buzz-pubsub` for the topic release it triggers,
`verification-contracts-nostr` for the wire contract it belongs to, and
`verification-e2e-relay` for the end-to-end suite the delivery-stops test lives in.

## Scope and omissions

**This node covers** what the `CLOSE` message is, what the relay's parser accepts and
rejects, what `handle_close` does in what order, how `CLOSE` differs from `CLOSED` and
from a WebSocket close frame, how its sub-id validation and load-control exposure differ
from `REQ`'s and `COUNT`'s, and which first-party clients send it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay-to-client `CLOSED` message and how to read its reason string | #1147 |
| The WebSocket transport close frame and connection teardown | #1122 |
| The `REQ` message and how a subscription is opened, scoped and replaced | its own sibling node under Feature #609 |
| The pubsub fan-out machinery — how a refcount reaching zero drives the Redis `UNSUBSCRIBE` | #1128 |
| The subscription registry's index structures and how `remove_from_index` unwinds them | not filed as its own task at the recorded revision |
| The per-connection `max_subscriptions` limit itself, as opposed to the fact that `CLOSE` frees a slot against it | not filed as its own task at the recorded revision |
| Whether the missing empty/length guards on `CLOSE`'s sub id are a defect worth fixing | a product question, not a documentation one; not filed at the recorded revision |

**Expected but not verified when this node was written:**

- **No unit test exercises `handle_close` itself.** Searched the whole `crates/` tree for
  the symbol: it appears exactly twice, at its own definition and at the dispatch site in
  `connection.rs`. The only `CLOSE`-specific coverage found is the parser unit test in
  `protocol.rs` and the `#[ignore]`-gated end-to-end test. So the unknown-subscription-id
  behaviour described above rests on reading the handler, not on a test that pins it.
- **The end-to-end test was not run.** It requires a live relay with Postgres and Redis.
  Its assertions were read, not observed.
- **Upstream NIP-01's own wording was not checked against Buzz's parser**, because no copy
  of NIP-01 exists in this repository — `docs/nips/` holds only Buzz's own two-letter
  NIPs. Every claim above about NIP-01 is either quoted from `protocol.rs`'s own module
  documentation or classified `TEAM_KNOWLEDGE`. Whether Buzz's looser sub-id validation on
  `CLOSE` conforms to the standard is therefore **not established here**.
- **The client survey may be incomplete.** Three senders were found by searching for the
  `CLOSE` literal across `crates/`, `desktop/`, `web/` and `mobile/`. A client that builds
  the frame without that literal — by string concatenation, or from a constant — would not
  have appeared. No such construction was looked for.
- **`web/` was searched and no `CLOSE` sender was found**, but the web client's
  subscription lifecycle was not read to confirm it genuinely never closes a subscription
  rather than doing so by some other means.
