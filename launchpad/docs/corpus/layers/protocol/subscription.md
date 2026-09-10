---
id: layers-protocol-subscription
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
  - statement: "A subscription's identifier is the client-supplied string carried on a REQ message, aliased in the relay as SubId, and the registry keys it beneath a per-connection ConnId, so the same identifier string on two different connections names two unrelated subscriptions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "The registry's authoritative store is a DashMap from ConnId to a HashMap from SubId to a SubEntry tuple of filters, the server-resolved CommunityId, and a SubscriptionScope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "SubscriptionScope is server-resolved, not client-declared, and is either Global or Channels holding the authorized channel UUIDs the subscription was registered under."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "A live subscription is held in two places at once: the connection's own subscriptions field, typed ConnectionSubscriptions as an Arc<Mutex<HashMap<String, Vec<Filter>>>>, and the relay-wide SubscriptionRegistry that the fan-out path reads."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "The per-connection subscription cap is MAX_SUBSCRIPTIONS, defined in the REQ handler as 1024, and it is evaluated against the connection's own subscriptions map rather than against any relay-wide total."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The cap guard is conditioned on the identifier being absent, reading `if !subs.contains_key(&sub_id) && subs.len() >= MAX_SUBSCRIPTIONS`, so a REQ that reuses an identifier already held by the connection replaces the existing subscription and is never charged against the cap."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A REQ rejected for exceeding the cap is answered with a CLOSED frame carrying `error: too many subscriptions` and no NOTICE, unlike the unauthenticated and insufficient-scope paths in the same handler which send a NOTICE alongside their CLOSED."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The relay's NIP-11 document advertises max_subscriptions as Some(1024), matching the MAX_SUBSCRIPTIONS constant the REQ handler enforces."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The end-to-end test that opens 1024 subscriptions and asserts the next REQ is answered with a CLOSED containing `too many`, test_subscription_limit_enforced, carries an #[ignore] attribute and therefore does not run in a default cargo test invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "Registration is remove-then-insert: register_with_scope calls remove_subscription for the same identifier first, then inserts unconditionally, and returns the displaced subscription's community and scope as a RemovedSubscription so the caller can release what it retained."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "The REQ handler acts on that return value by calling release_subscription_topics for the replaced subscription's scope before retaining the new subscription's topics."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The registry's own doc comment records that replacing any existing subscription carrying the same sub_id is NIP-01 behaviour."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "Registering a subscription retains a pubsub topic per authorized channel for a channel-scoped subscription, or the single Global topic for a global one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The CLOSE handler removes the subscription from the connection map and from the registry, then releases exactly the topics the removed subscription's scope named, and only afterwards sends the CLOSED acknowledgement."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "retain_topic increments a local desired refcount and only asks the subscriber task to SUBSCRIBE on the zero-to-one transition; release_topic decrements and only on the one-to-zero transition removes the entry and schedules an UnsubscribeIfIdle command after a debounce delay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "The subscriber task re-checks that the desired refcount is still zero when it processes UnsubscribeIfIdle before issuing the Redis unsubscribe, so a retain arriving inside the debounce window cancels the pending unsubscribe."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "When a connection ends, handle_active_connection — the run closure handle_connection hands to run_registered_community_connection — calls sub_registry.remove_connection with the connection's id after recv_loop returns and the send, heartbeat and auth-timeout tasks are joined, then releases the Global or Channel topics named by each RemovedSubscription it returns."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "remove_connection removes the connection's whole entry from the registry, unwires each subscription from every fan-out index it was placed in, and decrements the buzz_subscriptions_active gauge by the number removed in one step."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "Disconnect cleanup is reached by straight-line control flow rather than by a Drop guard: run_registered_community_connection installs a guard only for the community-connection registry, so subscription cleanup depends on handle_active_connection running to completion after recv_loop returns rather than on unwinding."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
    confidence: 0.75
  - statement: "A subscription can also be narrowed or ended by authorization change rather than by the client: remove_channel_subscriptions_scoped drops one revoked channel from each matching subscription's scope, re-indexing multi-channel subscriptions with what remains and removing entirely those left with no channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "A NIP-50 search REQ never becomes a living subscription: the search branch of handle_req returns before the connection's subscriptions map is written and before any registry registration occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A REQ whose explicitly requested channels are all inaccessible is rejected with a CLOSED rather than registered, because a subscription that can never produce an event or a terminal notice is treated as worse than an outright refusal."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The registry exposes total_subscriptions, total_connections and per_community_subscriptions, and snapshots per-community counts specifically to avoid gauge drift from mismatched increments and decrements across communities."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "A subscription that was never authorized is never created at all: an unauthenticated connection's REQ is answered with a NOTICE and a CLOSED and returns before any registration."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "No upstream numbered Nostr specification text is present in this repository, so a claim about what NIP-01 requires cannot be cited to a repository path; docs/nips holds only Buzz's own alphabetic NIP codes."
    entry_class: FACT
    evidence:
      - "ls(docs/nips/) -> 24 entries, all alphabetic Buzz codes spanning NIP-AA.md to NIP-WP.md, including NIP-FI-* variants and two NIP-MP JSON fixtures; grep -cE 'NIP-[0-9]' over that listing returns 0"
  - statement: "Issue #1167 requires that this node define the term in one sentence before deeper explanation, state its boundaries and what it must not be confused with, and link to related concepts, implementation and verification rather than duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1167 definition of done"
relationships:
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-pubsub
  - type: references
    target: verification-contracts-websocket
---

# Subscription

A **subscription** is a named standing query held for the lifetime of one WebSocket
connection: a client-chosen identifier bound to a set of filters and a server-resolved
delivery scope, which the relay keeps in memory so that every subsequently accepted
event matching those filters is pushed to that connection under that identifier.

## Definition

Three parts make one subscription, and all three are needed before it is a thing that
exists:

| Part | What it is | Who decides it |
|---|---|---|
| Identifier | An arbitrary string the client supplies on `REQ`, aliased `SubId` | The client |
| Filters | The query the standing subscription stands for | The client |
| Scope | `SubscriptionScope::Global`, or `Channels` holding authorized channel UUIDs | The **server** |

The third is the one that surprises people. A client may *ask* for channels in its
filters, but the scope stored against the subscription is the set the relay resolved and
authorized — a `Channels` scope, or `Global` when no channel was requested. Scope is not
a restatement of the filters; it is the routing decision the relay made about them, kept
alongside them so that removal and topic release can be done in one lookup rather than
re-derived.

**Identity is per connection, never relay-wide.** The registry is keyed
`ConnId → SubId → (filters, community, scope)`. The identifier `"sub1"` on connection A
and `"sub1"` on connection B are two unrelated subscriptions; neither can observe or
displace the other. Every operation in the registry — register, remove, fan-out
candidate lookup — takes a `ConnId` first.

**A subscription lives in two maps simultaneously.** The connection owns
`ConnectionSubscriptions`, an `Arc<Mutex<HashMap<String, Vec<Filter>>>>` holding just
identifier and filters; the relay owns the `SubscriptionRegistry`, which additionally
holds community, scope, and the fan-out indexes. The cap below is counted against the
first; delivery is driven from the second. A reader chasing a subscription-lifetime bug
needs to know both exist, because a change that touches only one of them leaves the pair
disagreeing.

### What a subscription is not

- **It is not the `REQ` that created it, nor the `CLOSE` that ends it.** Those are wire
  messages; the subscription is the object they act on, and it outlives the frame that
  created it.
- **It is not the filters it carries.** Filters are the query; the subscription is the
  standing registration of that query against one connection, with a scope the filters
  do not contain.
- **It is not a durable or resumable entity.** Nothing about a subscription survives its
  connection. There is no identifier a reconnecting client can present to resume one.
- **It is not a NIP-50 search.** A search `REQ` is answered and finished; the search
  branch of the handler returns before the connection map is written and before any
  registration happens, so no subscription object is ever created for it.

## The cap, and what replacement does to it

The per-connection ceiling is `MAX_SUBSCRIPTIONS`, **1024**, defined in the `REQ`
handler and matched by the `max_subscriptions` value the relay advertises in its NIP-11
document. It bounds one connection's map, not the relay's total.

The guard is conditioned on absence:

```rust
if !subs.contains_key(&sub_id) && subs.len() >= MAX_SUBSCRIPTIONS {
```

So **reusing an identifier is free**. A connection sitting at exactly 1024 subscriptions
can keep issuing `REQ`s indefinitely, provided each reuses an identifier it already
holds — each such `REQ` replaces rather than adds, and the cap is never consulted. Only
a genuinely new identifier can be refused.

Refusal is a **`CLOSED` frame** carrying `error: too many subscriptions`, with no
accompanying `NOTICE`. That is deliberate asymmetry within the same handler: the
unauthenticated and insufficient-scope paths send a `NOTICE` *and* a `CLOSED`, while the
cap path sends only the `CLOSED`. A client watching only for `NOTICE` will not see the
cap being hit.

**Replacement is remove-then-insert, and it is not free of side effects.**
`register_with_scope` removes any subscription already under that identifier, then
inserts unconditionally, returning the displaced subscription's community and scope as a
`RemovedSubscription`. The `REQ` handler uses that return value to release the replaced
subscription's pubsub topics *before* retaining the new one's — so replacing a
channel-scoped subscription with a global one correctly gives up the channel topic. The
registry's own doc comment records that same-identifier replacement is NIP-01 behaviour;
this repository holds no upstream NIP text to cite for that requirement directly (see
*Scope and omissions*).

## Topic retention: a subscription is a refcount holder

Registering a subscription **retains** a pubsub topic — one `Channel` topic per
authorized channel, or the single `Global` topic. Closing it **releases** the same set.
The subscription is therefore not only a delivery target but a claim on a Redis
subscription that the relay pod holds on its behalf.

`retain_topic` and `release_topic` maintain a local desired refcount, and the Redis
`SUBSCRIBE`/`UNSUBSCRIBE` calls ride only on its edges:

- **0 → 1** on retain asks the subscriber task to `SUBSCRIBE`. Every later retain only
  increments.
- **1 → 0** on release removes the entry and schedules an `UnsubscribeIfIdle` after a
  debounce delay. The subscriber re-checks that the refcount is *still* zero when it
  processes that command, so a retain arriving inside the debounce window silently
  cancels the pending unsubscribe.

The practical consequence for an operator: the last subscription on a channel leaving is
what stops the pod consuming that channel's Redis topic, and it does so on a short delay
rather than instantly — which is what stops a reconnect storm from churning
`SUBSCRIBE`/`UNSUBSCRIBE` pairs. How events then travel from that topic to a client is
`architecture-flows-live-fanout`'s subject, not this node's.

## Lifetime: the four ways a subscription ends

1. **`CLOSE` from the client.** The handler removes it from the connection map and the
   registry, releases the topics its scope named, and only then sends the `CLOSED`
   acknowledgement — ordered that way so no event can be routed to the subscription
   after the client has been told it is gone.
2. **Replacement.** A `REQ` reusing the identifier ends the old subscription and starts a
   new one under the same name, with the old one's topics released.
3. **Authorization change.** `remove_channel_subscriptions_scoped` drops one revoked
   channel from every matching subscription's scope. A multi-channel subscription is
   re-indexed with the channels that remain and survives; one left with no channels is
   removed outright. This is the only ending a client neither requested nor caused.
4. **The connection ending.** `handle_active_connection` — the run closure
   `handle_connection` hands to `run_registered_community_connection` — calls
   `remove_connection` for the connection's id after `recv_loop` returns and the send,
   heartbeat and auth-timeout tasks are joined. That removes the connection's whole registry entry, unwires each
   subscription from every fan-out index it sat in, decrements
   `buzz_subscriptions_active` by the count in one step, and returns each removed
   subscription so its topics can be released.

**How guaranteed is that fourth path?** It is reached by ordinary sequential control
flow in `handle_active_connection`, not by a `Drop` guard — the only guard installed
around the
connection is `run_registered_community_connection`'s, and that one covers the
community-connection registry, not the subscription registry. So cleanup holds for every
way `recv_loop` returns (client close, cancellation, read error, backpressure
disconnect), because all of them are returns; it is not established here that it holds
if the connection task unwinds or is aborted before those lines run. That distinction is
recorded as an inference, not a fact, and is not something this node tested.

There is a fifth thing that is emphatically *not* an ending: nothing expires a
subscription on time. No idle timeout, no TTL, no age-based reaper appears on any path
read for this node. A subscription persists until one of the four events above.

## Why this matters to a reader

- **Debugging "my client stopped receiving events."** The question decomposes into
  which of the four endings fired. Ending 3 in particular produces no client-initiated
  trace at all — a membership revocation elsewhere can silently narrow or remove a
  subscription.
- **Writing a client.** Identifier reuse is a supported, uncharged way to change a
  standing query in place. Watching for `CLOSED` rather than `NOTICE` is what surfaces
  the cap.
- **Operating a relay.** `buzz_subscriptions_active` and the per-community snapshot are
  the observable side of this object, and the topic refcount edges explain why Redis
  subscription counts lag connection counts by a debounce interval.

## Related corpus nodes

The messages that create and end a subscription, the marker in its stream, and the
filters it carries are documented as their own protocol nodes in this layer; this node
does not restate them. Adjacent merged nodes:

- `architecture-flows-live-fanout` — how an accepted event reaches the subscribers this
  registry identifies.
- `architecture-flows-historical-query` — the backfill a `REQ` performs after
  registration.
- `architecture-flows-websocket-connection` — the connection whose lifetime bounds every
  subscription on it.
- `implementation-crates-buzz-relay`, `implementation-crates-buzz-pubsub` — the crates
  that own the registry and the topic refcount respectively.
- `verification-contracts-websocket` — the protocol contract and the tests that exercise
  subscription lifecycle end to end.

## Scope and omissions

**This node covers** the subscription as a living object: its three-part identity, its
per-connection keying, the two maps that hold it, the 1024 cap and the replacement
semantics that sidestep it, the pubsub topic refcount it holds, and the four ways it
ends.

**It does not cover, and these are boundaries rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `REQ` message that creates a subscription | Its own protocol node (#1165) |
| The `CLOSE` message that ends one | Its own protocol node (#1146) |
| The `EOSE` marker separating backfill from live delivery | Its own protocol node (#1150) |
| The `CLOSED` frame used for both refusal and termination | Its own protocol node (#1147) |
| Filters — their structure, semantics and matching | Its own protocol node (#1157) |
| How a matched event is delivered to a connection | `architecture-flows-live-fanout` |
| The historical backfill a `REQ` performs after registering | `architecture-flows-historical-query` |
| Connection admission, authentication and teardown | `architecture-flows-websocket-connection` |

None of the sibling protocol nodes named above were merged on `origin/launchpad` at the
recorded revision, so they appear here as prose rather than as typed `relationships`
edges — a `relationships[].target` naming an unmerged id is a hard validation error.

**Expected but not verified when this node was written:**

- **Whether the cap can be exceeded under concurrency was not established.** The guard
  reads the connection's map early in `handle_req` and the insert happens later, after
  several `await` points, so the check and the write are not a single critical section.
  Whether concurrent `REQ`s on one connection can therefore land above 1024 was not
  tested, and no test exercising that race was found. It is named here as an open
  question, not asserted as a defect.
- **The 1024 cap has no test running in a default suite.**
  `test_subscription_limit_enforced` exists and asserts exactly the behaviour described
  above, but it is `#[ignore]`-gated and needs a live relay, so the cap is unguarded by
  any check that runs unattended.
- **No upstream NIP text is available in this repository to cite.** `docs/nips/` holds
  24 entries, all Buzz's own alphabetic NIP codes; nothing matching `NIP-<digit>`
  exists. Every
  NIP-01 claim above is therefore worded as what a Buzz source *records* about NIP-01,
  and is evidenced by that source, not by the specification.
- **Whether disconnect cleanup survives a panic or task abort was not tested.** The
  straight-line-versus-`Drop`-guard reading is recorded as an inference from the two
  files read; no test was found that kills a connection task mid-flight and then asserts
  the registry is clean.
- **The relay-wide consequence of the cap being per connection was not quantified.** The
  registry has no total ceiling that was found, so 1024 is a per-connection bound and
  aggregate subscription load is bounded only by the connection cap, which belongs to
  the connection-admission subject rather than to this one.
