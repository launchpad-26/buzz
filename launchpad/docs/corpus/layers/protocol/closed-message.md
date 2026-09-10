---
id: layers-protocol-closed-message
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
  - statement: "RelayMessage::closed(sub_id, message) serialises the three-element JSON array [\"CLOSED\", sub_id, message], and its own doc comment describes it as indicating that a subscription was terminated by the relay; the enclosing RelayMessage struct is documented as helpers for formatting NIP-01 relay-to-client messages."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "handlers/close.rs sends CLOSED with an empty message string as the acknowledgement of a client CLOSE, after removing the subscription from the connection map and deregistering it from the fan-out registry, so an empty reason is the one CLOSED that reports success rather than a failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "The REQ handler emits CLOSED with the reasons \"auth-required: not authenticated\", \"error: too many subscriptions\", \"error: database error\", \"error: mixed search and non-search filters not supported\", \"restricted: insufficient scope\", \"restricted: too many explicit channels\", \"restricted: not a channel member\", \"restricted: p-gated events require #p matching your pubkey\", \"restricted: agent-engram reads require authors=[self] or #p=[self]\", and \"restricted: author-only kinds require authors=[self]\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The COUNT handler emits CLOSED with the reasons \"auth-required: not authenticated\", \"error: database error\", \"restricted: too many explicit channels\", \"restricted: p-gated kinds require #p tag matching your pubkey\" (worded differently from the REQ handler's equivalent), \"restricted: agent-engram reads require authors=[self] or #p=[self]\", \"restricted: author-only kinds require authors=[self]\", \"restricted: count filter requires narrower constraints\" when a post-filter fallback exceeds its candidate bound, and a dynamic \"error: {e}\" carrying the underlying database error text."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "connection.rs's request_rejection_message chooses the frame by whether a subscription id is in scope: with one it returns RelayMessage::closed(sub_id, reason), without one a NOTICE — and it carries the three rate-limited: reasons (\"too many concurrent requests\", \"quota exceeded; retry in {n}s\", \"shared admission unavailable\"), asserted by its own unit test req_rejections_are_subscription_scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handlers/side_effects.rs sends CLOSED(\"restricted: channel access revoked\") to a connection whose live channel subscription was removed because its access was revoked, which is the relay's one unsolicited CLOSED — no client message triggers it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "buzz-ws-client's parse_relay_message maps the \"CLOSED\" first element to RelayMessage::Closed { subscription_id, message }, erroring if the subscription id is absent or not a string but defaulting the reason to an empty string when element 2 is missing."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "The desktop client's classifyRelayClosed sorts a received CLOSED reason into retryable, rate-limited or terminal by lowercase prefix, treating auth-required: as retryable on purpose because a REQ can race the AUTH handshake after a reconnect, and treating restricted:, blocked:, invalid:, pow:, duplicate:, unsupported:, \"error: mixed search\" and \"error: too many subscriptions\" as terminal."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClosedPolicy.ts"
  - statement: "relayClosedRecovery.ts acts on that classification: terminal deletes the live subscription outright, retryable re-sends the REQ on exponential backoff capped at 30 seconds, and rate-limited additionally arms the shared rate-limit gate and waits out the gate's remaining time rather than its own backoff."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClosedRecovery.ts"
  - statement: "relayRateLimitGate.ts parses the relay's \"retry in Ns\" hint out of a CLOSED reason with the same regex it uses for HTTP 429 bodies, clamps it to MAX_HINT_SECONDS = 300, and falls back to a 10-second window when the reason carries no hint."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayRateLimitGate.ts"
  - statement: "relayClosedPolicy.test.mjs asserts the three-way classification directly, including that an empty reason string classifies as retryable."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClosedPolicy.test.mjs"
  - statement: "The desktop unsubscribe path deletes the subscription from its map before sending CLOSE, so the empty-reason CLOSED that acknowledges that CLOSE finds no entry in handleRelayClosed and is dropped rather than being treated as a retryable failure."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
      - "desktop/src/shared/api/relayClosedRecovery.ts"
  - statement: "The browser web client treats any CLOSED matching its subscription id as a rejection, rejecting the pending query promise with an Error carrying the relay's reason text, with no prefix classification and no retry."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
  - statement: "e2e_relay.rs asserts CLOSED behaviour against a live relay in test_subscription_limit_enforced (the 1025th REQ is CLOSED with a reason containing \"too many\", while a rate-limited: CLOSED is retried rather than accepted as the cap) and in the membership-notification and p-gate tests, which assert a CLOSED carrying \"restricted\" for the subscription id that was rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The prefixes invalid: and duplicate: are used by the relay on the event-ingest rejection path in command_executor.rs, whose IngestError::Rejected is reported to the client as an OK-false reply in handlers/event.rs, not as a CLOSED."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "The desktop's terminal-prefix list is deliberately wider than the set of prefixes the relay is observed to emit on a CLOSED, because blocked:, pow:, duplicate:, unsupported: and invalid: appear at no RelayMessage::closed call site in the tree, so the client is coding defensively against the standard's whole prefix vocabulary rather than against this relay's current behaviour."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/shared/api/relayClosedPolicy.ts"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
    confidence: 0.75
  - statement: "buzz-pair-relay, the ephemeral NIP-AB device-pairing sidecar, is a second independent relay implementation that builds its own CLOSED frame via a local make_closed helper rather than reusing buzz-relay's RelayMessage, and its rejection reasons use the error: and invalid: prefixes."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "NIP-01 is the upstream Nostr specification that defines CLOSED and the machine-readable colon-terminated reason-prefix convention that auth-required:, restricted:, rate-limited: and error: come from; its text is not present in this repository, whose docs/nips/ directory holds only Buzz's own two-letter NIPs."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "NIP-01, nostr-protocol/nips — cited by name in crates/buzz-relay/src/protocol.rs but not vendored into this repository"
relationships:
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: implementation-crates-buzz-pair-relay
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: verification-contracts-websocket
  - type: references
    target: verification-e2e-relay
---

# The `CLOSED` message

`CLOSED` is how a Buzz relay tells one client that one of its subscriptions is
over. It is the only relay-to-client frame that ends a subscription's life, and
its third element carries a machine-readable reason prefix that decides whether
the client should retry, back off, or give up. This node defines the message,
enumerates the reasons this relay actually emits, and describes what the shipped
clients do when they receive one.

## Definition

`CLOSED` is a relay-to-client WebSocket text frame, encoded as the three-element
JSON array `["CLOSED", <subscription_id>, <message>]`. `<subscription_id>`
identifies exactly one of the sending connection's subscriptions; `<message>` is
a human-readable reason that conventionally begins with a machine-readable,
colon-terminated prefix. Receiving it means the named subscription no longer
exists on the relay: no further `EVENT` frames will arrive for that id, and the
client must send a fresh `REQ` if it wants the stream back.

Three things share a name with this message and are **not** it.

**`CLOSE` is a different message travelling the other way.** `CLOSE` is
client-to-relay and asks the relay to end a subscription the client no longer
wants. `CLOSED` is relay-to-client and reports that a subscription has ended.
They are not a request/response pair in general — most `CLOSED` frames this relay
sends were never asked for by a `CLOSE`. The one place they meet is the
acknowledgement: the relay's `CLOSE` handler replies with a `CLOSED` whose reason
is the **empty string**, which is the sole `CLOSED` that reports success rather
than a failure. `CLOSE` itself is documented separately; this node does not cover
its parsing, its handler, or the fan-out deregistration it performs.

**The WebSocket close frame is a different layer.** A transport-level WebSocket
close frame tears down the whole connection and every subscription on it at once. `CLOSED` is an application-layer text frame that ends exactly one
subscription and leaves the socket open and authenticated. A client that conflates
them will either reconnect when it only needed to re-`REQ`, or leave a dead
subscription in its map after the socket has actually gone. Transport-level close
is a separate concern and is not covered here.

**`OK` is the rejection frame for publishing, not for subscribing.** An event that
the relay refuses to store is rejected with `["OK", <event_id>, false, <message>]`,
whose reason uses the *same* prefix vocabulary. Two prefixes in that vocabulary —
`invalid:` and `duplicate:` — are used by this relay only on the ingest path and
reach the client as `OK`, never as `CLOSED`. A reader grepping for a prefix string
therefore has to check which frame carries it.

## Background

`CLOSED` exists because a subscription can fail *after* the relay has accepted the
socket and authenticated the peer. Without it, a relay refusing a `REQ` has only
two bad options: send `NOTICE`, which is connection-scoped and does not say which
subscription died, or drop the socket, which kills every other subscription too.
`CLOSED` is subscription-scoped, so one rejected `REQ` costs one subscription.

That scoping is visible in the relay's own code as a deliberate branch.
`request_rejection_message` in `connection.rs` takes an `Option<&str>`
subscription id and returns a `CLOSED` when one is present and a `NOTICE` when it
is not — the *same* rate-limit reason, routed to whichever frame can carry it.
Its unit test asserts exactly that pairing.

## Reasons this relay emits

Every `RelayMessage::closed` call site in the tree was read to build this table.
Four prefixes are in use, plus the empty reason.

| Prefix | Emitted where | Meaning |
|---|---|---|
| *(empty)* | `handlers/close.rs` | Acknowledgement of a client `CLOSE`. The subscription ended because the client asked. Not a failure. |
| `auth-required:` | `handlers/req.rs`, `handlers/count.rs` | The connection is not `Authenticated`. `REQ` additionally sends a `NOTICE` alongside. |
| `restricted:` | `handlers/req.rs`, `handlers/count.rs`, `handlers/side_effects.rs` | The authenticated peer may not read what the filter asks for: insufficient scope, not a channel member, too many explicit `#h` values, a p-gated / agent-engram / author-only kind requested without the required self-scoping, a COUNT whose filter needs narrowing, or channel access revoked underneath a live subscription. |
| `error:` | `handlers/req.rs`, `handlers/count.rs` | The request is well-formed but the relay cannot serve it. A database failure produces `error: database error` from both handlers; the 1024-subscription cap and mixed search / non-search filters are `REQ`-only; COUNT adds a dynamic `error: {e}` carrying the underlying database error text verbatim. |
| `rate-limited:` | `connection.rs` | Back-pressure: the handler semaphore is exhausted, a per-principal admission quota is spent (`retry in {n}s`), or the shared admission store is unavailable. |

Two properties of that table matter more than the individual strings.

**Only one of these is unsolicited.** Every other `CLOSED` is a reply to a
`REQ`, a `COUNT` or a `CLOSE` the client just sent. The
`restricted: channel access revoked` frame from `side_effects.rs` arrives with no
client message in flight, when a membership change removes a live subscription's
right to exist. A client that only handles `CLOSED` inside a request/response
correlation will miss it.

**`auth-required:` is not permanent.** It is emitted whenever the connection is
not yet `Authenticated`, which includes the window in which a `REQ` races the
NIP-42 handshake after a reconnect. The handshake itself — the challenge, the
kind:22242 response, the 5-second timeout, the per-handler auth checks — is
documented by `architecture-flows-websocket-authentication` and is not restated
here.

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Relay
    C->>R: REQ sub-1 [filters]
    alt subscription accepted
        R-->>C: EVENT sub-1 …
        R-->>C: EOSE sub-1
        Note over C,R: later, membership revoked
        R-->>C: CLOSED sub-1 "restricted: channel access revoked"
    else subscription refused
        R-->>C: CLOSED sub-1 "auth-required: | restricted: | error: | rate-limited: …"
    end
    C->>R: CLOSE sub-1
    R-->>C: CLOSED sub-1 ""
```

## Use cases

**Writing a client that will not spin.** The reason prefix is the whole signal.
The desktop client's `classifyRelayClosed` sorts it three ways — `terminal`
deletes the subscription, `retryable` re-sends the `REQ` on exponential backoff
capped at 30 seconds, and `rate-limited` arms a process-wide gate and waits out
its remaining window instead of the local backoff, so concurrent operations back
off together. Getting this wrong in either direction is expensive: classify a
`restricted:` as retryable and the client re-`REQ`s a filter that can never
succeed, forever; classify an `auth-required:` as terminal and a subscription
that lost one handshake race never comes back. The shipped policy takes the
second risk deliberately and treats `auth-required:` as retryable, relying on a
genuinely unauthenticated session latching terminal at the connection level.

**Reading a relay rejection without a stack trace.** When a `REQ` returns nothing,
the `CLOSED` reason is usually the only diagnostic. `restricted:` points at
authorization — membership, scope, or a self-scoping requirement on a gated kind.
`error: too many subscriptions` points at the client leaking subscriptions rather
than at the relay. `rate-limited:` points at admission, and its `retry in Ns` hint
is a real number the relay computed, parsed by the desktop's gate with the same
regex it uses for HTTP 429 bodies and clamped to 300 seconds.

**Knowing that an empty reason is not an error.** A naive prefix classifier maps
`""` to "no known prefix, therefore retry", which would make every ordinary
unsubscribe trigger a re-subscribe. The desktop avoids this by ordering rather
than by classification: it removes the subscription from its map *before* sending
`CLOSE`, so the acknowledging `CLOSED` finds nothing to recover and is dropped.
Its test suite pins the underlying classification of `""` as retryable, which
makes that ordering load-bearing rather than incidental.

**Consuming `CLOSED` from Rust.** `buzz-ws-client` parses the frame into
`RelayMessage::Closed { subscription_id, message }`, requiring the subscription id
to be present and a string but defaulting a missing reason to `""`. Client
implementations differ in what they do next: the browser web client applies no
classification at all and simply rejects the pending query promise with the
relay's reason text.

## Comparison — terminal-prefix vocabulary, client versus relay

| Prefix | This relay emits it on `CLOSED` | Desktop client treats it as |
|---|---|---|
| `auth-required:` | yes | retryable |
| `rate-limited:` | yes | rate-limited |
| `restricted:` | yes | terminal |
| `error:` | yes | retryable, except `error: mixed search` and `error: too many subscriptions`, which are terminal |
| `blocked:` | no | terminal |
| `pow:` | no | terminal |
| `unsupported:` | no | terminal |
| `invalid:` | no — used on the ingest/`OK` path only | terminal |
| `duplicate:` | no — used on the ingest/`OK` path only | terminal |

The client's list is the wider one. The five prefixes it treats as terminal but
never receives are the standard's vocabulary rather than this relay's behaviour —
defensive coding against a relay that might one day send them, or against a
different relay entirely. That reading is an inference from the two sources, not
a statement recorded anywhere in the code.

## Related resources

The typed `relationships` edges in this node's front matter are the canonical
links: `implementation-crates-buzz-relay` for the emitting crate,
`implementation-crates-buzz-ws-client` for the Rust parser,
`implementation-crates-buzz-pair-relay` for the second, independent relay
implementation, `architecture-flows-websocket-authentication` for the handshake
that `auth-required:` refers to, `architecture-flows-websocket-connection` for the
per-message admission path that produces `rate-limited:`, and
`verification-contracts-websocket` and `verification-e2e-relay` for the conformance
contract and the live-relay tests that exercise these frames.

## Scope and omissions

**Not covered, and who owns it.**

- `CLOSE`, the client-to-relay message — its parsing, its handler's fan-out
  deregistration, and its topic-release behaviour. A sibling node on the same
  protocol surface owns it; this node covers only the `CLOSED` that acknowledges
  it.
- The WebSocket close frame and connection teardown — transport layer, owned by a
  separate networking node.
- The `OK` message and the event-ingest rejection path, including the `invalid:`
  and `duplicate:` reasons that live there. Named here only to keep the prefix
  vocabularies apart.
- The NIP-42 handshake itself, owned by `architecture-flows-websocket-authentication`.
- The subscription registry, fan-out, and topic retain/release machinery that a
  `CLOSED` is the visible edge of.
- The full text of NIP-01. It is not in this repository, so what the standard
  *requires* is recorded here as `TEAM_KNOWLEDGE` attributed to the spec by name,
  never as a `FACT` on a repository path. What *Buzz* does is a `FACT` on Buzz
  source.
- `buzz-pair-relay`'s own `CLOSED` emission beyond the fact that it exists and is
  independently implemented. Its reason set was not enumerated.

**Expected to verify and could not.**

- **No unit test asserts the reason string at any individual relay emit site.**
  `protocol.rs` has one test that `RelayMessage::closed` produces a well-formed
  `["CLOSED", …]` array, and `connection.rs` has one asserting the
  `CLOSED`-versus-`NOTICE` branch. Beyond those, the reason literals in
  `req.rs`, `count.rs` and `side_effects.rs` are unpinned by any test in the
  crate — the e2e tests that check them assert substrings (`"too many"`,
  `"restricted"`) against a live relay and are `#[ignore]`d by default. So an
  edit to a reason string would not fail a default `cargo test` run.
- **No live relay was run.** Every claim about relay behaviour here is read from
  source, not observed on the wire. The `#[ignore]`d e2e tests in
  `crates/buzz-test-client/tests/e2e_relay.rs` were read but not executed; they
  require a running Postgres and Redis.
- **The negative claim in the comparison table is bounded by grep, not by
  proof.** "This relay never emits `blocked:` on a `CLOSED`" rests on reading
  every `RelayMessage::closed` call site at the recorded revision. The dynamic
  `error: {e}` reason in `count.rs` interpolates a database error whose text was
  not enumerated, so a reason string this node did not anticipate can reach a
  client through that one path.
- **Mobile client behaviour was not established.** Only the desktop and browser
  web clients and the Rust `buzz-ws-client` were read; whether the Flutter app
  classifies `CLOSED` reasons at all is unknown.
