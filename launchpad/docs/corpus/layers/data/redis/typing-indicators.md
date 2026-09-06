---
id: layers-data-redis-typing-indicators
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "This node's `type` is `layers`, an explicit override of `templates/datastore.md`'s own worked example, which directs a real datastore instance node to `type: architecture` on the grounds that node.schema.json offers no finer-grained member for a container-, component-, or datastore-level structural view. Earlier documents in this same overnight batch (Feature #610, 'data and storage layer corpus exists') established `type: layers` as the working convention for every `layers/data/...` node instead, and this node follows that batch precedent rather than the template's own example, disclosing the deviation here per `standards/taxonomy.md`'s 'when the fit is imperfect, say so' guidance rather than silently picking one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight batch dispatch brief for Feature #610 (2026-08-30 run), naming the `layers/data/...` type-override precedent from earlier documents authored in the same batch"
  - statement: "Issue #1099's Definition of Done requires: exactly one hand-authored canonical document; schema-valid front matter with a stable id, type, status, origin, audiences, evidence and typed relationships; one independently maintainable knowledge node; every substantive claim traceable to current code/test/spec/decision/migration/config or attributed GitHub evidence with FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links to implementation/verification/specification/neighboring nodes without duplicating their content; a check against the recorded provenance revision and Git history/PRs/issues where they explain behavior or rationale; a clean local `validate.py` run; and that the document states whether the store is authoritative, derived, cache or transport, describes owned data/key access patterns/lifecycle/retention/consistency semantics, names tenancy/security boundaries and failure behavior, and links schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1099 definition of done"
  - statement: "`crates/buzz-core/src/kind.rs` defines `KIND_TYPING_INDICATOR: u32 = 20002` with the doc comment 'Ephemeral: typing indicator for a channel', inside the ephemeral event range 20000-29999 (`EPHEMERAL_KIND_MIN`/`EPHEMERAL_KIND_MAX`), and its own module comment states that range is 'Never stored.' `is_ephemeral(kind)` is a `const fn` returning `kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "`crates/buzz-pubsub/Cargo.toml` describes the crate as 'Redis pub/sub fan-out, presence, and typing indicators for Buzz' and depends on the `redis` and `deadpool-redis` crates; `crates/buzz-pubsub/src/lib.rs`'s own module-level doc comment repeats the same three-part description ('Redis pub/sub fan-out, presence tracking, and typing indicators')."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "At the recorded revision, `crates/buzz-pubsub/src/lib.rs` declares exactly nine public modules (`cache_invalidation`, `conn_control`, `error`, `nip98_replay`, `presence`, `publisher`, `rate_limiter`, `subscriber`, `topic`) and no `typing` module; the on-disk file listing of `crates/buzz-pubsub/src/*.rs` confirms no `typing.rs` file exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "A `pub mod typing;` module existed at `crates/buzz-pubsub/src/typing.rs` (then `crates/sprout-pubsub/src/typing.rs`) providing `PubSubManager::set_typing`/`get_typing`, backed by a Redis `ZADD`-based sorted set keyed by `typing::typing_key(channel_id)` and scored by Unix timestamp, with a 5-second staleness window pruned on each write. Commit 90192d8d48949ab198c8ca9ece3387e41fbdbc93 ('chore: remove verified dead code (#745)', 2026-05-25) deleted `crates/sprout-pubsub/src/typing.rs` in full (153 lines) and removed the `pub mod typing;` declaration, `set_typing`/`get_typing` methods, and their test, but its diff shows the `/// Typing indicator tracking in Redis.` doc comment immediately above the deleted `pub mod typing;` line was left in place, now dangling directly above `pub use error::PubSubError;` with no module of its own — a verified stale doc-comment artifact of that removal, not a planned-but-unbuilt feature."
    entry_class: FACT
    evidence:
      - "git_show(90192d8d48949ab198c8ca9ece3387e41fbdbc93, path=crates/sprout-pubsub/src/lib.rs) -> removes pub mod typing;, set_typing, get_typing, and test_typing_set_and_prune; leaves the preceding doc comment in place"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "`crates/buzz-relay/src/handlers/event.rs`'s `handle_ephemeral_event` special-cases `KIND_PRESENCE_UPDATE` only (parsing status, then calling `state.pubsub.set_presence`/`clear_presence`); the file imports `KIND_AGENT_OBSERVER_FRAME`, `KIND_GIFT_WRAP` and `KIND_PRESENCE_UPDATE` from `buzz_core::kind` but never imports or references `KIND_TYPING_INDICATOR`. A typing-indicator event therefore falls straight into the same generic branch every other channel-scoped ephemeral event takes: channel-membership check, local-event marking, `state.pubsub.publish_event(...)`, and direct local WS fan-out — no Redis command specific to typing runs anywhere in this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "`crates/buzz-pubsub/src/publisher.rs`'s `publish_event` function issues exactly one Redis command, `PUBLISH <channel-key> <event-json>`, over a pooled connection, and returns the subscriber count Redis reports; it holds no Redis key of its own and reads none back."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "`crates/buzz-pubsub/src/topic.rs`'s `EventTopicKey::redis_channel` formats the PUBLISH/SUBSCRIBE channel name as `buzz:{community_id}:channel:{channel_id}` for a channel-scoped topic or `buzz:{community_id}:global` for the community-global topic; `handle_ephemeral_event` routes a typing indicator's `h`-tagged channel id through `EventTopic::Channel(ch_id)`, so its channel key is the same `buzz:{community}:channel:{id}` topic every persistent channel event in that channel also publishes on — there is no typing-specific channel or key namespace."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "By contrast, `crates/buzz-pubsub/src/presence.rs`'s own module doc states presence is 'Stored as `SET buzz:{community}:presence:{pubkey_hex} \"online\" EX 180`', a named, keyed, TTL'd Redis value read back by `get_presence`/`get_presence_bulk`. No equivalent keyed value, read-back function, or TTL exists anywhere in `buzz-pubsub` for typing indicators at the recorded revision — the only Redis interaction a typing indicator causes is the one `PUBLISH` call cited above."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "Because a typing indicator's only Redis footprint is a single fire-and-forget `PUBLISH` with no key written or read back, Redis holds no state for typing indicators at any point — it carries the message from publisher to subscribers and then has none of it left. This makes Redis's role for typing indicators transport, not an authoritative store, a derived projection, or a cache of anything."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/presence.rs"
    confidence: 0.9
  - statement: "`crates/buzz-relay/src/handlers/event.rs`'s `handle_event` gates every ephemeral-range kind (via `is_ephemeral(kind_u32)`, which includes 20002) on the connection's scopes containing `buzz_auth::Scope::MessagesWrite` when any scope is set, and separately checks `buzz_deletion::store(&state.db).is_serving_active(conn.tenant.community())`, rejecting with 'restricted: community writes are fenced' if the community's writes are fenced — both checks run before a typing indicator (or any other ephemeral event) reaches `handle_ephemeral_event`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "For a channel-scoped ephemeral event (any event whose tags yield a channel id via `extract_channel_id`, which a typing indicator's `h` tag does), `handle_ephemeral_event` calls `super::ingest::check_channel_membership(&conn.tenant, &state, ch_id, &pubkey_bytes, None)` before publishing, and rejects (via the `?`-propagated `Err` return) if the authenticated pubkey is not a member of that channel; `extract_channel_id` and `check_channel_membership` are both defined in `crates/buzz-relay/src/handlers/ingest.rs`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Pub/sub topic scoping is a routing/performance boundary, not an authorization boundary — `crates/buzz-pubsub/src/topic.rs`'s own module doc states this directly, and the community id embedded in every Redis channel key (`buzz:{community_id}:...`) comes from `TenantContext`, resolved server-side per connection, not from client input."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "`crates/buzz-acp/src/relay.rs`'s `RelayHandle::build_typing_event` constructs a kind:20002 event with an `h` tag naming the channel id and, when a parent/root thread reply target is known, `e` tags for `root`/`reply`; the doc comment on the neighboring `try_publish_event` states it is 'suitable for ephemeral commands like typing indicators where dropping the event on a full command channel is acceptable' — the client-side send path is fire-and-forget by design, matching the transport classification above."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
  - statement: "`crates/buzz-acp/src/lib.rs` arms a `typing_refresh` interval of `Duration::from_secs(3)` when `config.typing_enabled`, and republishes a typing event per actively-typing channel on each tick via `try_publish_event`; this is the agent-side (buzz-acp) typing-liveness mechanism, independent of any relay- or Redis-side expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
  - statement: "`desktop/src/features/messages/useTypingBroadcast.ts` throttles outgoing typing publishes to at most once per `TYPING_SEND_INTERVAL_MS = 3_000` (3 seconds) per channel, calling `relayClient.sendTypingIndicator`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/useTypingBroadcast.ts"
  - statement: "`desktop/src/features/messages/useChannelTyping.ts` computes each received typing entry's local expiry as `event.created_at * 1000 + TYPING_INDICATOR_TTL_MS` (`TYPING_INDICATOR_TTL_MS = 8_000`, 8 seconds), discards events already past that expiry on arrival, and prunes expired entries from local state every `TYPING_PRUNE_INTERVAL_MS = 1_000` (1 second) via a client-side interval timer — all liveness/expiry logic for a typing indicator lives in the subscribing client, not in Redis or the relay."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/useChannelTyping.ts"
  - statement: "`crates/buzz-test-client/tests/conformance_multitenant.rs`'s `pubsub_presence_typing` module defines `subscribe_typing`/`publish_typing` helpers against `KIND_TYPING_INDICATOR = 20002` and asserts, in a REQ against that kind, that zero historical events return with the comment 'typing is ephemeral and should not return historical events' — confirming at the integration-test level that a typing indicator leaves no queryable trace after it is delivered live."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "That same test module's tenant-fence test publishes distinct typing content in two different communities on live subscriptions sharing the same channel UUID and asserts each side receives exactly its own community's typing content and never the other's — the community-scoped Redis channel key (`buzz:{community}:channel:{id}`) is exercised, not merely declared, by this test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "`launchpad/docs/corpus/architecture/containers/redis.md` (id `architecture-containers-redis`) is a validated node merged on `origin/launchpad`, and its own evidence ledger already documents `buzz-pubsub` as 'Redis pub/sub fan-out, presence, and typing indicators for Buzz' at the container level."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "No `layers/data/redis/*` sibling document exists on `origin/launchpad` at the recorded revision (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/layers` returns no results), including no presence-tracking node from issue #1095, even though such a node may exist in an unmerged sibling worktree in this same overnight batch — per `AGENTS.md` step 9's rule that a relationship target must exist on the branch being merged into, not the author's own branch, this node declares no edge to it."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/layers') -> no entries"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Typing indicators (Redis)

How Buzz's channel typing indicator — kind:20002, an ephemeral Nostr event —
uses Redis: what Redis actually stores for it (nothing, at rest), how the
event is carried from publisher to subscribers, what gates a client before
one is accepted, and what happens when a publish is lost.

## Purpose & scope statement

This node documents the **typing indicator** feature (`KIND_TYPING_INDICATOR
= 20002`) specifically, at the datastore-usage level: what Redis is asked to
do for a typing indicator, and what it is not. It zooms into one row of the
already-merged `architecture-containers-redis` container document — the fact
that a Redis instance exists and that `buzz-pubsub` is its accessor — and
adds the axis that document deliberately keeps to one line. It is not a
domain-model description of what a typing indicator *means* to a channel's
UI (that belongs to a data-entity-shaped node, not yet written), and it is
not an environment/deployment document (Redis's own deployment shape is
`architecture-containers-redis`'s and `architecture/deployment/*`'s
concern). It is scoped to typing indicators only — **presence tracking**
(`KIND_PRESENCE_UPDATE`, kind:20001) is a related but distinct Redis-backed
feature in the same `buzz-pubsub` crate, with its own keyed, TTL'd Redis
state (`SET ... EX 180`, cited below only for contrast), and is not
restated here.

## Technology & attachment profile

Redis (the same instance `architecture-containers-redis` documents), reached
through `buzz-pubsub`'s `deadpool_redis::Pool` for command execution and one
dedicated `redis::aio::PubSub` connection for the subscriber side (per
`buzz-pubsub`'s own crate-level architecture diagram). A typing indicator
uses only the pooled-connection side: `publisher::publish_event` acquires a
connection from the pool and issues one `PUBLISH` command per event. There is
no dedicated attachment surface for typing indicators beyond the one
`buzz-pubsub` already uses for every other channel event.

## Owned data ("schema" — none at rest)

**Typing indicators own no data in Redis.** The only Redis interaction a
typing indicator causes is a single `PUBLISH <channel-key> <event-json>`
call; nothing is written to a key, and nothing is read back. This is a
structural fact, not an oversight found by omission: an earlier
implementation *did* keep Redis-resident state for typing — a `ZADD`-backed
sorted set (`typing::typing_key(channel_id)`, scored by Unix timestamp, with
a 5-second staleness window) exposed as `PubSubManager::set_typing`/
`get_typing` — and it was deliberately deleted as verified dead code (commit
`90192d8d48949ab198c8ca9ece3387e41fbdbc93`, PR #745) once the ephemeral
kind:20002 + generic pub/sub fan-out path below became the production
mechanism. That removal's diff also shows exactly how the crate ended up
with a currently-dangling doc comment: `/// Typing indicator tracking in
Redis.` sat directly above the deleted `pub mod typing;` declaration, and the
commit removed the module line but left the comment in place, where it now
sits immediately above an unrelated `pub use error::PubSubError;` in
`crates/buzz-pubsub/src/lib.rs`. Both facts are cited in the evidence ledger
above; the second is also named again in *Scope and omissions* as a stale
artifact this node does not itself fix.

The channel name a typing indicator's `PUBLISH` targets — `buzz:{community_id
}:channel:{channel_id}` — is not a typing-specific namespace. It is the exact
same Redis pub/sub channel every persistent event in that channel also
publishes on. Redis draws no distinction between a typing indicator and a
stored chat message on the wire; the distinction (store it or don't) is made
entirely by `buzz-relay`, before Redis is ever touched.

## Migration / schema-versioning mechanism

Not applicable. There is no schema, key, or namespace for typing indicators
to version — see *Owned data*, above. If a future change gives typing
indicators their own Redis-resident state again, that state would need its
own migration/versioning story; none exists today.

## Access-pattern summary

**Publishers** (both send a signed kind:20002 event over the client's
existing authenticated WebSocket connection to `buzz-relay`, which is the
only path that ever calls `publisher::publish_event`):

- `buzz-acp` (the agent harness), via `RelayHandle::build_typing_event` +
  `try_publish_event` — a non-blocking, fire-and-forget send — on a 3-second
  refresh timer per actively-typing channel while `config.typing_enabled`.
- The desktop client, via `useTypingBroadcast`'s `relayClient.sendTypingIndicator`,
  throttled client-side to at most one send per 3 seconds per channel.

**The relay** (`crates/buzz-relay/src/handlers/event.rs`) is the only writer
to Redis for this feature. `handle_event` gates the incoming event
(`MessagesWrite` scope when scopes are set; community writes not fenced,
checked via `buzz_deletion::store(...).is_serving_active`), then
`handle_ephemeral_event` checks channel membership
(`ingest::check_channel_membership`) and calls
`state.pubsub.publish_event(&conn.tenant, EventTopic::Channel(ch_id), &event)`
— the one Redis `PUBLISH`. It also fans the event out directly to same-pod
local WebSocket subscribers, independent of Redis, so same-pod delivery does
not depend on the Redis round trip succeeding.

**Subscribers** are every relay pod with an active `SUBSCRIBE` on that
channel's topic (via `buzz-pubsub`'s dedicated pub/sub connection and
`run_subscriber`'s `broadcast::channel`), which then fan the received event
out to their own locally-connected WebSocket clients — this is the
cross-pod delivery path a same-pod client does not need. No instrumentation
policy applies: this path is not covered by `buzz-datastore-tracing`'s
`#[datastore_span]` macro, which `buzz-pubsub` does not import at all.

## Operational characteristics

**No TTL, retention, or expiry exists at the Redis or relay layer for
typing indicators**, because nothing is stored there to expire. All
liveness semantics are enforced independently by each client:

- `buzz-acp` re-sends every 3 seconds while a channel is actively being
  typed in, and stops re-sending (implicitly expiring, from a receiver's
  point of view) once the channel is removed from its local typing set.
- The desktop client treats a received typing event as valid for 8 seconds
  from its `created_at` timestamp (`TYPING_INDICATOR_TTL_MS`), independently
  pruning expired entries from local UI state once per second.

This means the "5 seconds" staleness window the deleted `ZADD`-based
implementation once enforced in Redis itself has no direct successor: the
current 3-second (send) / 8-second (client expiry) pair is enforced
independently by two different client codebases, not by any single shared
mechanism, and the two values are not identical to each other or to the
old Redis-side window. No consistency guarantee ties these numbers together
beyond convention.

**No replication, backup, or durability posture applies.** A typing
indicator that Redis's `PUBLISH` fails to deliver (because no subscriber
was listening, because Redis was briefly unreachable, or because a
subscriber's `broadcast::channel` had already lagged — see
`PubSubError::BroadcastLagged`) is simply gone. It is never retried,
queued, or replayed, by design: `crates/buzz-acp/src/relay.rs`'s own
comments describe typing indicators as the canonical example of an
"ephemeral" publish where "dropping the event on a full command channel is
acceptable," and the client-side refresh timers (3 seconds in both
`buzz-acp` and the desktop client) are the feature's actual resilience
mechanism — a dropped indicator is superseded by the next periodic resend,
not recovered.

## Tenancy / security boundaries and failure behavior

**Tenancy.** The Redis channel key embeds the server-resolved
`community_id` from `TenantContext`, never client-supplied input, so one
community's typing traffic cannot be published onto or subscribed from
another community's channel key. `buzz-pubsub/src/topic.rs`'s own doc
states this is "a routing/performance boundary, not an authorization
boundary" — the relay re-checks channel membership and access on every
event, on both the publish side (`check_channel_membership`) and the local
fan-out side, rather than trusting topic scoping alone.

**Security/authorization.** A typing indicator, like every ephemeral event,
requires the connection to hold `MessagesWrite` scope (when the connection
carries any scopes at all) and requires the community's writes not be
fenced (`is_serving_active`). A channel-scoped typing indicator additionally
requires the authenticated pubkey to be a member of the target channel,
checked before the Redis `PUBLISH` runs.

**Failure behavior.** Every failure mode is fail-silent from Redis's own
point of view: a pool-acquisition failure, a `PUBLISH` command error, or a
lagged broadcast receiver all surface only as a `tracing::warn!` on the
relay side (`"Ephemeral publish failed: {e}"`) — the publishing client
receives no `OK`-style rejection for a downstream Redis failure the way it
would for an auth or scope rejection, because the WS-level accept/reject
handshake completes based on the event's own validity, before Redis is
touched. A client that never receives its own typing indicator delivered
back has no relay-level signal that anything went wrong; the 3-second
resend is the only recovery path.

## Links instead of duplicated content

- Container-level existence of the Redis instance and `buzz-pubsub`'s role
  as its accessor: `architecture-containers-redis`
  (`launchpad/docs/corpus/architecture/containers/redis.md`), this node's
  `part-of` target.
- Event-kind definition: `crates/buzz-core/src/kind.rs`
  (`KIND_TYPING_INDICATOR`, `is_ephemeral`).
- Relay-side handling: `crates/buzz-relay/src/handlers/event.rs`
  (`handle_event`, `handle_ephemeral_event`) and
  `crates/buzz-relay/src/handlers/ingest.rs` (`extract_channel_id`,
  `check_channel_membership`).
- Redis transport: `crates/buzz-pubsub/src/publisher.rs`,
  `crates/buzz-pubsub/src/topic.rs`.
- Client publish/receive: `crates/buzz-acp/src/relay.rs`
  (`build_typing_event`, `try_publish_event`),
  `desktop/src/features/messages/useTypingBroadcast.ts`,
  `desktop/src/features/messages/useChannelTyping.ts`.
- Integration coverage: `crates/buzz-test-client/tests/conformance_multitenant.rs`
  (`pubsub_presence_typing` module).

No DDL, schema, or key format is copied into this document beyond the one
channel-name format cited directly above and in the evidence ledger — there
is no DDL to copy, since typing indicators own no stored schema.

## Scope and omissions

**This node covers** whether Redis is authoritative, derived, cache or
transport for typing indicators (transport, and only transport); what data
Redis owns for them (none, at rest); the migration/versioning story (not
applicable); who accesses Redis for this feature and how; the operational
characteristics Redis itself provides (none — no TTL, no durability
guarantee); and the tenancy, security, and failure-behavior boundaries
around the feature.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Redis container's own existence, technology, and deployment shape | `architecture-containers-redis` |
| Presence tracking (`KIND_PRESENCE_UPDATE`, kind:20001) — a distinct Redis-backed feature in the same crate, with its own keyed `SET ... EX 180` state | A separate `layers/data/redis/*` node (issue #1095), not yet merged on `origin/launchpad` at this node's authoring time — no relationship edge is declared to it, per `AGENTS.md` step 9 |
| The domain/UI meaning of a typing indicator (what the desktop or agent UI does with one) | Not documented in the corpus at this node's authoring time |
| Whether `type: layers` or `type: architecture` is the more correct long-term classification for this and its `layers/data/redis/*` siblings | Left to a later corpus-wide pass across the batch, per the disclosed override in this node's evidence ledger |
| Fixing the dangling `/// Typing indicator tracking in Redis.` doc comment in `crates/buzz-pubsub/src/lib.rs` | Not this node's job — named as a verified, resolved-in-explanation-but-not-in-code artifact of PR #745's cleanup; an implementation task, not a corpus-authoring one |

**Expected but not verified when this node was written:**

- **Whether any relay-fleet metric or dashboard tracks dropped/lagged
  typing publishes specifically** (as opposed to the generic
  `PubSubError::BroadcastLagged` case) was not checked — this node
  describes the code path's failure behavior, not live operational data
  about how often it actually triggers.
- **Whether the 3-second and 8-second client-side timing constants were
  chosen deliberately to relate to each other**, or independently by
  whoever wrote each client, was not established from any commit message,
  issue, or code comment found while drafting this node.
