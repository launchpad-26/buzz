---
id: platforms-relay-close-handler
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "At the recorded revision, no launchpad/docs/corpus/platforms directory exists on origin/launchpad, and no platforms-specific template exists in launchpad/docs/corpus/templates/ (the enumerated templates are architecture-component, architecture-container, architecture-context, capability, component, concept, configuration, data-entity, datastore, decision-reference, deployment, event-kind, flow, generated-index, glossary-term, implementation-reference, interface, invariant, policy, procedure, reference, runbook, specification, test-contract, test-strategy, threat-model)."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no platforms/** entries, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "Because no platforms-specific template is merged, this node is hand-authored against node.schema.json per AGENTS.md's documented no-template path, borrowing launchpad/docs/corpus/templates/component.md's section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) since this node's subject -- one message handler's responsibility, interface and collaborators -- matches that template's intent more closely than any other merged template, while setting front matter type: platforms because node.schema.json's type enum defines platforms as the corpus surface for this subject (the relay is a named platform surface) rather than implementation, which component.md itself directs authors toward for its own type value."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
  - statement: "The CLOSE command is handled by handle_close(sub_id, conn, state) in crates/buzz-relay/src/handlers/close.rs, which is dispatched from the connection's message-handling match statement as ClientMessage::Close(sub_id) => handlers::close::handle_close(sub_id, Arc::clone(&conn), Arc::clone(&state)).await."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:10-35"
      - "crates/buzz-relay/src/connection.rs:639-640"
  - statement: "handle_close performs three effects in order: (1) removes the subscription id from the connection's own subscriptions map, (2) deregisters it from the shared SubscriptionRegistry via remove_subscription -- which, for a subscription that had a global or per-channel routing scope, calls buzz_pubsub's release_topic once per retained topic -- and (3) sends a CLOSED acknowledgement frame back to the client; a code comment states the ordering is deliberate so no new fan-out message is routed to the subscription after CLOSED has been (or is about to be) sent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:10-35"
  - statement: "SubscriptionRegistry::remove_subscription(conn_id, sub_id) removes the entry from the per-connection subscription map, cleans up the fan-out index via remove_from_index, decrements the buzz_subscriptions_active gauge, and returns Some(RemovedSubscription { community_id, scope }) naming the subscription's server-resolved routing scope, or None if no such subscription existed for that connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:238-267"
      - "crates/buzz-relay/src/subscription.rs:66-73"
  - statement: "buzz_pubsub::PubSub::release_topic decrements a reference count in a desired_topics map keyed by tenant and topic; only when the count reaches zero does it schedule (after a configured debounce delay, on a spawned task) an UnsubscribeIfIdle command, rather than unsubscribing from the Redis channel immediately on the calling task."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "RelayMessage::closed(sub_id, message) formats the NIP-01 CLOSED frame as the JSON array [\"CLOSED\", sub_id, message]; handle_close always calls it with an empty message string, regardless of whether the sub_id it is closing was actually found in either the connection's map or the shared registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:208-211"
      - "crates/buzz-relay/src/handlers/close.rs:32"
  - statement: "ClientMessage::parse's \"CLOSE\" arm requires the frame to be a JSON array of at least two elements whose second element is a string, and otherwise returns RelayError::InvalidMessage; unlike the REQ and COUNT arms in the same match statement, it does not check that the sub_id string is non-empty and does not check it against MAX_SUB_ID_LENGTH (256, the constant both REQ and COUNT enforce as the NIP-11 advertised max_subid_length)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:8-9"
      - "crates/buzz-relay/src/protocol.rs:68-90"
      - "crates/buzz-relay/src/protocol.rs:108-129"
      - "crates/buzz-relay/src/protocol.rs:146-159"
  - statement: "handle_close's own effects are idempotent and never surface an error to the client for an unknown sub_id: conn.subscriptions.lock().await.remove(&sub_id) is a no-op if the key is absent, remove_subscription returns None (skipping the release_topic loop entirely) if the registry has no matching entry, and the function still sends a CLOSED acknowledgement in every case, including for a sub_id the relay never registered."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs:10-34"
  - statement: "crates/buzz-relay/src/handlers/close.rs contains no #[cfg(test)] module of its own; the only test exercising this handler's observable behavior found in this repository is the end-to-end test test_close_subscription_stops_delivery, which subscribes, waits for EOSE, calls close_subscription, then asserts that an event published afterward on a matching filter is not delivered to the closed subscription. That test is marked #[ignore] (requires a live relay) rather than run as a fast unit test."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs:538-576"
      - "crates/buzz-test-client/src/lib.rs:159-161"
  - statement: "A disconnect-triggered teardown path exists separately from the client-initiated CLOSE command: after a connection's receive loop ends (for any reason -- client disconnect, cancellation, or error), handle_active_connection calls state.sub_registry.remove_connection(conn.conn_id), which removes every remaining subscription for that connection and runs the same per-topic release_topic cleanup handle_close runs per-subscription. This corpus already documents that path in architecture-flows-websocket-connection; this node's Boundary section defers to it rather than re-describing it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:288-301"
      - "crates/buzz-relay/src/subscription.rs:270-284"
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
---

# Relay CLOSE handler

This node documents `handle_close`, the relay's handler for a NIP-01 `CLOSE`
command -- a client asking the relay to cancel one of its own active `REQ`
subscriptions. It answers: what effects does receiving `CLOSE` have, in what
order, and what happens for a `sub_id` the relay does not recognize.

## Responsibility

`handle_close(sub_id, conn, state)` in
`crates/buzz-relay/src/handlers/close.rs` is the single place a client's
`CLOSE` command is acted on. Its own doc comment states its job plainly:
*"remove the subscription and send CLOSED acknowledgement."* It performs
three effects, in this order:

1. Removes `sub_id` from the connection's own `subscriptions` map
   (`ConnectionState.subscriptions`, a `Mutex`-guarded map the connection's
   own `REQ`/`CLOSE` handlers share).
2. Deregisters the subscription from the shared `SubscriptionRegistry`
   (`state.sub_registry.remove_subscription`), which also cleans up the
   fan-out index and, for every topic (community-global and/or per-channel)
   the subscription had retained, releases that topic via
   `buzz_pubsub::release_topic`.
3. Sends a `CLOSED` acknowledgement frame back to the client.

The ordering is deliberate: a code comment at the call site states the
registry deregistration happens *"before sending CLOSED so no new messages
are routed to this sub after the client's CLOSE is acknowledged."*

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `handle_close(sub_id: String, conn: Arc<ConnectionState>, state: Arc<AppState>)` | async fn | Removes the named subscription (connection-local map + shared registry + retained pub/sub topics) and always replies with a `CLOSED` frame, whether or not the subscription existed. | `crates/buzz-relay/src/handlers/close.rs:10-35` |
| `ClientMessage::Close(String)` | enum variant | The parsed form of a `["CLOSE", sub_id]` client frame. Requires the frame to be a 2+-element JSON array whose element 1 is a string; unlike `Req`/`Count` parsing, does **not** reject an empty `sub_id` or one longer than `MAX_SUB_ID_LENGTH` (256). | `crates/buzz-relay/src/protocol.rs:27, 146-159` |
| `RelayMessage::closed(sub_id: &str, message: &str) -> String` | fn | Formats the NIP-01 `["CLOSED", sub_id, message]` reply. `handle_close` always calls it with an empty `message`. | `crates/buzz-relay/src/protocol.rs:208-211` |
| `SubscriptionRegistry::remove_subscription(conn_id, sub_id) -> Option<RemovedSubscription>` | fn | Removes one subscription's index entries and returns its server-resolved routing scope, or `None` if the connection had no such subscription. | `crates/buzz-relay/src/subscription.rs:238-267` |

## Dependencies

**Depends on** (this handler requires these to do its job):

| Component | Why | Evidence |
|---|---|---|
| `ConnectionState.subscriptions` | Per-connection subscription-id map the handler removes the closed id from first. | `crates/buzz-relay/src/connection.rs:60-72` |
| `AppState.sub_registry` (`SubscriptionRegistry`) | Shared fan-out index the handler deregisters the subscription from, and the source of the routing scope used to release pub/sub topics. | `crates/buzz-relay/src/subscription.rs:238-267` |
| `buzz_pubsub::PubSub::release_topic` | Reference-counted, debounced release of a Redis pub/sub topic subscription once no local subscription still wants it. | `crates/buzz-pubsub/src/lib.rs` |
| `RelayMessage::closed` / `ConnectionState::send` | Formats and enqueues the outbound `CLOSED` frame. | `crates/buzz-relay/src/protocol.rs:208-211`, `crates/buzz-relay/src/connection.rs:89-118` |

**Depended on by** (what relies on this handler running):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/connection.rs`'s per-connection dispatch loop | Routes every parsed `ClientMessage::Close` frame to this handler; it is the only caller. | `crates/buzz-relay/src/connection.rs:639-640` |
| `crates/buzz-test-client`'s `close_subscription` helper, and the e2e test that calls it | Exercises this handler's client-visible contract (subscription no longer receives matching events after `CLOSE`). | `crates/buzz-test-client/src/lib.rs:159-161`, `crates/buzz-test-client/tests/e2e_relay.rs:538-576` |

## Behavior notes

- **Idempotent, never errors on an unknown `sub_id`.** Both the connection-
  local map removal and the registry removal are no-ops if the id is not
  present (`Option`-returning / silently-absent-key removal); the handler
  still sends `CLOSED` in every case. A client closing a `sub_id` it never
  opened, or closing the same `sub_id` twice, observes the same successful
  acknowledgement as closing a live subscription.
- **Parsing asymmetry with `REQ`/`COUNT`.** The `CLOSE` arm of
  `ClientMessage::parse` does not enforce the empty-string or
  `MAX_SUB_ID_LENGTH` (256-byte, NIP-11-advertised) checks that the `REQ`
  and `COUNT` arms in the same `match` both apply to their `sub_id`. Given
  the idempotent behavior above, an out-of-bounds `sub_id` on `CLOSE` cannot
  affect an existing subscription either way, but the asymmetry itself is
  an observed fact about the code, not a claim about whether it is
  intentional -- see *Scope and omissions*.

## Boundary

This node does not describe:
- **Disconnect-triggered subscription teardown** -- when a connection's
  receive loop ends for any reason (client disconnect, cancellation,
  error), `remove_connection` sweeps every remaining subscription for that
  connection through the same per-topic `release_topic` cleanup this
  handler runs per-subscription. That path is already documented in
  `architecture-flows-websocket-connection` (see *Relationships*).
- **`REQ` subscription creation**, historical delivery, or `EOSE` --
  owned by `crates/buzz-relay/src/handlers/req.rs`, not this node.
- **Partial, channel-scoped unsubscription** --
  `remove_channel_subscriptions_scoped` (used when a channel is revoked from
  a still-open multi-channel subscription) is a related but distinct
  removal path this node does not cover.
- **The Redis pub/sub subscribe/unsubscribe state machine itself** --
  `release_topic`'s reference counting and debounce are named here only as
  this handler's collaborator; `buzz-pubsub`'s own internal behavior is not
  this node's subject.

## Relationships

- references: architecture-flows-websocket-connection

## Scope and omissions

**This node covers** the relay's `CLOSE` command handler (`handle_close`):
its three ordered effects, its collaborators, its idempotent handling of an
unknown `sub_id`, and its parsing-time contract including the observed
asymmetry against `REQ`/`COUNT` sub_id validation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Disconnect-triggered subscription teardown (`remove_connection`) | `architecture-flows-websocket-connection` |
| `REQ` subscription creation and historical delivery | Not yet a corpus node at this revision; `crates/buzz-relay/src/handlers/req.rs` is the source |
| Channel-scoped partial unsubscription (`remove_channel_subscriptions_scoped`) | Not yet a corpus node at this revision |
| `buzz-pubsub`'s topic reference-counting/debounce mechanics in general | Not yet a corpus node at this revision |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether the `CLOSE` sub_id validation asymmetry (no empty/length check,
  unlike `REQ`/`COUNT`) is intentional or an oversight was not established.**
  Given the handler's idempotent, no-op-on-unknown-id behavior, it has no
  observed effect on correctness, but no commit message, ADR, or NIP-01 spec
  citation was found explaining the omission either way.
- **Whether `type: platforms` is the durable, corpus-wide convention for a
  `platforms/**`-scoped node, or a placeholder a later corpus-standards
  issue reshapes, was not settled here** -- no `platforms`-specific template
  exists yet at the recorded revision, and no other `platforms/**` node
  exists on `origin/launchpad` to check this choice against.
- **No fast (non-`#[ignore]`) unit test exercising `handle_close` directly
  was found.** The only test found is the live-infra e2e test cited above;
  whether a unit-level test exists elsewhere in the workspace under a name
  not searched for was not exhaustively ruled out beyond the searches
  performed for this node.
