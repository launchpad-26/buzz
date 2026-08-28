---
id: architecture-flows-live-fanout
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The relay only accepts an EVENT frame from a WebSocket connection whose auth state is AuthState::Authenticated; unauthenticated connections are rejected before any fan-out logic runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "handle_event branches on event kind before fan-out: kind:22242 (AUTH) is rejected outright, kind:44100-range agent observer frames and gift-wrap events take their own paths, ephemeral kinds are handled entirely inline by handle_ephemeral_event, and every other kind is handed to ingest_event for persistent storage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "For a persistent event, ingest_event returns an early 'duplicate:' acceptance without calling dispatch_persistent_event when the insert-or-ignore write found the event id already stored, so a duplicate submission never triggers a live fan-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "dispatch_persistent_event is the single post-commit dispatch point for every persistently stored event, called after the database insert has already committed, from ingest_event (client-submitted events) and also from side_effects.rs, workflow_sink.rs, and moderation_notices.rs (relay-generated side-effect, workflow-output, and moderation events)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/workflow_sink.rs"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "dispatch_persistent_event awaits only the bounded audit enqueue before returning, then spawns the remaining work (Redis publish, local fan-out, workflow triggering) on a separate tokio task; the NIP-01 OK the client receives therefore confirms durable storage only, not that any live subscriber has received the event yet."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Inside the spawned dispatch, the relay first calls state.mark_local_event to record the event id in a 60-second moka TTL cache keyed by (community_id, event_id), then calls buzz_pubsub::publish_event to PUBLISH the event's JSON to a Redis pub/sub channel scoped by community and by EventTopic::Channel(id) or EventTopic::Global."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "If the Redis publish fails, the relay invalidates the local_event_ids entry it just set and logs a warning, but does not retry the publish and continues on to local delivery; a Redis publish failure only prevents delivery to subscribers connected to other relay pods, never to subscribers on the pod that accepted the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Local delivery on the accepting pod runs SubscriptionRegistry::fan_out_scoped to find matching (connection, subscription) pairs from community-and-channel-scoped indexes (or, for channel-less events, from per-p-tag, per-kind and wildcard global indexes), then filter_fanout_by_access to revalidate delivery access before any frame is written."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "fan_out_scoped enforces a symmetric scoping invariant: channel-scoped subscriptions are indexed separately from global (channel-less) ones, so a channel subscription never matches a global event and a global subscription never matches a channel-scoped event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "filter_fanout_by_access is the single chokepoint shared by the in-process fan-out path, the cross-node Redis fan-out path, and (with one extra DM-visibility-owner step layered on top) the post-commit persistent-event path; it re-derives access at send time rather than trusting a previously registered subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "dispatch_persistent_event_inner adds one further recipient-side gate beyond filter_fanout_by_access: for kind:30622 (DM visibility) and kind:44200 (agent turn metric) events, delivery is additionally narrowed to the connection whose authenticated pubkey matches the event's own p-tagged owner, so a kindless ids:[] subscription cannot pick these up."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Delivery to each matched connection goes through ConnectionManager::send_to_text_bytes, which does a non-blocking try_send on that connection's outbound channel; a full channel is tracked per-connection as backpressure and, once the count reaches the connection's grace_limit, the relay cancels that connection outright rather than continuing to buffer for a slow client."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "send_to_cancels_after_grace_limit is a passing unit test that exercises the grace-limit disconnect path: three consecutive full-buffer sends against a connection configured with grace_limit=3 result in the connection being cancelled."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "For cross-node delivery, every relay pod runs a background task that subscribes to the pubsub broadcast channel and calls fan_out_pubsub_event for every ChannelEvent received; on RecvError::Lagged(n) it logs a warning and a metric and keeps consuming, but on RecvError::Closed it logs an error and the loop exits, after which that pod stops receiving any further cross-node fan-out until the process restarts."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "fan_out_pubsub_event de-duplicates local echo before delivering: if the incoming event id is already present in local_event_ids for that community, it invalidates the entry and returns without a second local delivery, because the accepting pod already delivered it synchronously in the post-commit path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "global_presence_pubsub_event_fans_out_to_local_subscribers, local_echo_presence_pubsub_event_is_not_delivered_twice, and global_membership_pubsub_event_fans_out_by_p_tag are passing unit tests in crates/buzz-relay/src/handlers/event.rs that exercise fan_out_pubsub_event's matching and echo-dedup behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "channel_less_event_passes_through, open_channel_event_passes_through_unfiltered, and channel_less_event_must_drop_recipient_in_different_community are passing unit tests in crates/buzz-relay/src/handlers/event.rs that exercise filter_fanout_by_access, including the community-boundary fail-closed check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "filter_fanout_by_access resolves private-channel visibility with a fail-closed default: if the visibility lookup itself errors, the function logs a warning and returns no recipients rather than guessing the channel is open."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Ephemeral events (e.g. presence, typing, pairing) follow the same publish-then-locally-fan-out shape as persistent events but run entirely inline inside handle_ephemeral_event rather than through dispatch_persistent_event, and they skip audit enqueue and workflow triggering, which are persistent-event-only steps."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "AUTHOR_ONLY_KINDS events (NIP-ER reminders) are filtered to the event's own author before any channel-membership check, and this gate is shared by both the in-process and the Redis cross-node fan-out paths through filter_fanout_by_access, so no fan-out route can bypass it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "is_shared_gated_kind events fan out to every matched connection only when the event carries a [\"shared\",\"true\"] tag; otherwise only the author's own connections receive it, mirroring the read-path REQ semantics for the same kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Because Redis publish failure is logged and not retried, and because the local moka echo-dedup cache expires after 60 seconds, a cross-node subscriber can permanently miss a live event with no automatic recovery in the fan-out path itself; the connected client's own catch-up/backfill query, not the fan-out path, is the only route back to consistency for that miss."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/state.rs"
    confidence: 0.75
  - statement: "No unit or integration test in this repository was found exercising the Redis-publish-failure warning path in dispatch_persistent_event_inner or handle_ephemeral_event, nor the RecvError::Closed break-and-stall path in the multi-node fan-out consumer task in main.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/main.rs"
---

# Live fan-out

How one accepted Nostr event reaches connected WebSocket subscribers in
real time, across a single relay pod and across a fleet of pods behind
Redis pub/sub. This node covers delivery only — not event validation,
storage, or the historical `REQ` query path, which are separate concerns
documented elsewhere (see Scope and omissions).

## Trigger, preconditions, termination

**Trigger.** A NIP-01 `EVENT` frame arrives on a WebSocket connection, or
the relay itself produces an event as a side effect (a workflow post, a
moderation notice, a thread-counter update, or another relay-signed
message).

**Preconditions.**
- The submitting connection must already be `AuthState::Authenticated`
  (NIP-42) — `handle_event` rejects with `auth-required` before any
  fan-out logic runs for an unauthenticated connection.
- `kind:22242` (`AUTH`) events are rejected outright; they can never enter
  the fan-out path.
- For a *persistent* event, the database insert must have already
  committed. Fan-out is exclusively a post-commit action — there is no
  path that fans an event out before (or instead of) storing it.

**Termination / outcome.** Fan-out has three possible outcomes, and none
of them affect the `OK` response the submitting client already received:
1. Zero matched recipients (no live subscription covers the event) — the
   dispatch functions return early and nothing is sent.
2. One or more recipients matched and successfully written to their
   outbound WebSocket channel.
3. One or more recipients matched but not delivered, because their send
   buffer was full or their connection was already closing — this is
   logged, counted, and does not block delivery to the other recipients.

A **duplicate** submission (the insert-or-ignore write found the event id
already stored) short-circuits before dispatch is even called — no
fan-out happens for a duplicate, whether the duplicate arrives over the
same connection or a different one.

## Ordered interactions and data movement

1. **Ingress.** `handle_event` reads the connection's authenticated
   identity, then branches on event kind: `AUTH` is rejected; agent
   observer frames and gift-wrap events take their own paths; ephemeral
   kinds go to `handle_ephemeral_event` (step 2a below); everything else
   goes to `ingest_event` (step 2b below).
2a. **Ephemeral path (inline).** `handle_ephemeral_event` verifies the
    signature, applies any ephemeral-kind-specific handling (e.g.
    presence status normalization), checks channel membership when the
    event carries a channel, marks the event id as locally originated
    (`state.mark_local_event`), publishes it to the scoped Redis channel,
    and immediately calls the guarded local delivery helper
    (`fan_out_event_to_local_subscribers`) — all inline, on the request
    task, with no audit enqueue and no workflow trigger.
2b. **Persistent path (post-commit, spawned).** `ingest_event` validates
    and inserts the event. If the insert was a no-op duplicate, it returns
    immediately with no dispatch. Otherwise, after the insert has
    committed, it calls `dispatch_persistent_event`, which awaits only a
    bounded audit-log enqueue and then spawns the remainder onto its own
    tokio task:
    - `state.mark_local_event` records `(community_id, event_id)` in a
      60-second TTL cache, so this pod recognizes its own event coming
      back through Redis and does not deliver it twice.
    - `buzz_pubsub::publish_event` does a Redis `PUBLISH` to a channel
      keyed by community and by `EventTopic::Channel(id)` or
      `EventTopic::Global`. On failure this is logged and the just-set
      local-echo entry is invalidated, but the publish is **not**
      retried — cross-pod delivery for this event is lost, while
      same-pod delivery (the next step) still proceeds.
    - `SubscriptionRegistry::fan_out_scoped` looks up matching
      `(connection, subscription)` pairs from channel-and-kind or
      channel-wildcard indexes (channel-scoped events) or from
      per-p-tag, per-kind, and wildcard indexes (channel-less/global
      events). Channel-scoped and global indexes are disjoint by
      construction.
    - `filter_fanout_by_access` re-validates every match (detailed in
      the next section) before anything is sent.
    - For `kind:30622` (DM visibility) and `kind:44200` (agent turn
      metric), one further filter narrows delivery to the single
      connection whose authenticated pubkey matches the event's `p`-tag
      owner.
    - Matched connections receive the serialized `EVENT` frame via
      `ConnectionManager::send_to_text_bytes` (non-blocking `try_send`).
    - If the event is a stored reply, a relay-signed live thread-summary
      event (`kind:39005`) is emitted through the same fan-out shape,
      best-effort.
    - If the kind is not a workflow-execution/command kind, not a
      relay-signed workflow message, and not a gift wrap, the workflow
      engine's `on_event` is triggered on a further spawned task.
3. **Cross-node delivery.** Every relay pod runs a background task
   holding a `broadcast::Receiver<ChannelEvent>` fed by the pod's Redis
   pub/sub subscriber. For every event received, it calls
   `fan_out_pubsub_event`, which:
   - Checks `local_event_ids` for the same `(community_id, event_id)` key
     set in step 2b/2a above; if present, it invalidates the entry and
     returns — this is the local-echo suppression that prevents the
     originating pod from delivering its own event twice.
   - Otherwise runs the same `fan_out_scoped` → `filter_fanout_by_access`
     → serialize → send sequence as the in-process path, so a
     different pod's subscribers receive an event that originated on
     another pod.

## Trust-boundary crossings

- **Client → relay (NIP-42 AUTH).** The WebSocket connection must be
  authenticated before `handle_event` will process an `EVENT` frame at
  all; this is the outermost gate and runs before any fan-out code.
- **Community/tenant boundary.** `filter_fanout_by_access` re-checks that
  every matched connection's resolved community equals the event's
  community before anything else, independent of what the (possibly
  stale, possibly cross-pod) subscription index says. This is a fail-closed
  re-check at the send chokepoint, not a trust of the index.
- **Private-channel membership.** For a channel-scoped event whose channel
  is `private`, delivery is narrowed to connections whose pubkey is a
  cached or freshly looked-up member of that channel; a visibility- or
  membership-lookup error fails closed (no recipients), never open.
- **Author-only and DM/metric-owner-only kinds.** `AUTHOR_ONLY_KINDS`
  (NIP-ER reminders) and the `kind:30622`/`kind:44200` owner-only gate
  each narrow a match set down to one identity, independent of what
  subscription filter a connection registered.
- **Shared-gated kinds.** Kinds gated by `is_shared_gated_kind` fan out to
  every recipient only when explicitly tagged `["shared","true"]`;
  otherwise only the author's own connections receive them.
- **Relay ↔ Redis.** Publishing to and consuming from Redis pub/sub is an
  inter-process trust boundary inside the deployment (not
  end-user-authenticated); the channel key itself is scoped by
  community/tenant so a different tenant's Redis channel is never
  subscribed to or published on by another tenant's traffic.

## Failure, abort, and rollback behavior

- **Redis publish failure** (persistent or ephemeral path): logged as a
  warning, the just-set local-echo cache entry is invalidated, and the
  publish is not retried. Same-pod delivery still proceeds normally;
  other pods' subscribers do not receive the event for this publish
  attempt. There is no compensating retry elsewhere in the fan-out path.
- **Full or closed per-connection send buffer:** `send_to_text_bytes`
  does a non-blocking `try_send`; a full buffer increments that
  connection's backpressure counter and is logged, without failing the
  rest of the fan-out batch. Once the counter reaches the connection's
  configured `grace_limit`, the relay cancels that connection outright
  (`conn.cancel.cancel()`) rather than continuing to buffer for a slow
  client — verified by `send_to_cancels_after_grace_limit`
  (`crates/buzz-relay/src/state.rs`), which drives three consecutive
  full-buffer sends against a `grace_limit = 3` connection and asserts it
  is cancelled.
- **Multi-node consumer lag:** if the pod's internal broadcast receiver
  falls behind (`RecvError::Lagged(n)`), the consumer logs a warning,
  increments a lag metric, and keeps running — the `n` lagged messages
  are simply not delivered to that pod's local subscribers.
- **Multi-node consumer channel closed:** `RecvError::Closed` is logged as
  an error and the consumer loop exits (`break`), which stops that pod
  from receiving *any* further cross-node fan-out until the process is
  restarted. This is a fleet-wide-visible failure mode with no
  in-process self-healing.
- **No rollback path exists or is needed on the write side:** fan-out
  runs strictly after the persistent event's database insert has
  committed (or, for ephemeral events, after any Redis presence-state
  side effect), so a fan-out failure can never undo or invalidate the
  already-durable write. The NIP-01 `OK` the client already received is
  unaffected by anything described in this section.
- **What was expected but could not be verified:** no unit or
  integration test exercising the Redis-publish-failure warning path, or
  the `RecvError::Closed` consumer-stall path, was found in this
  repository at the recorded revision. `send_to_cancels_after_grace_limit`
  and the `fan_out_pubsub_event`/`filter_fanout_by_access` unit tests
  listed in the evidence ledger are the representative verification that
  does exist, for the parts of this flow they cover (echo dedup,
  community-boundary fail-closed, matching, backpressure disconnect).

## Scope and omissions

**Does not cover:** event *validation and storage* (`ingest_event`'s
schema/scope/kind-specific acceptance rules), the historical `REQ`/query
read path, presence/typing pub/sub beyond their role as ephemeral events
routed through this same fan-out shape, workflow *execution* semantics
once `workflow_engine.on_event` is invoked, or Blossom media delivery.
Those are separate, independently maintainable concerns and belong in
their own corpus nodes.

**Expected but not verified** (see also the failure-behavior section
above): whether any load or chaos test exists elsewhere in the ecosystem
(outside this repository) that exercises Redis unavailability or
broadcast-channel exhaustion under production-like fan-out volume was not
checked — that would live in `sprout-oss` or
`block-coder-tf-stacks`, which are out of scope for this node.

**Relationships.** No `relationships` entries are declared. At the
recorded revision, `launchpad/docs/corpus/` carries no other
`architecture`-typed node this one could correctly point at
(`AGENTS.md`, `README.md`, `schema/`, and `standards/` are the only
existing corpus content); per `launchpad/docs/corpus/AGENTS.md`, a
relationship target must already exist in the branch being merged into,
and none does yet for this node.
