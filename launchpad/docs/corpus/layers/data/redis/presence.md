---
id: layers-data-redis-presence
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum has no member specific to a data/storage layer topic narrower than layers itself; this node uses type: layers rather than the type: governance an earlier-read sibling datastore template records for itself, following the same override every launchpad/docs/corpus/layers/data/... document in this batch uses, disclosed here per the batch dispatch brief rather than left implicit."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight dispatch brief for the layers/data/redis/* task set (Feature #610)"
  - statement: "presence.rs's own module doc states presence is 'Stored as SET buzz:{community}:presence:{pubkey_hex} \"online\" EX 180' and that 'TTL is 3x the 60s heartbeat interval so a single missed heartbeat does not cause presence flap. Clean disconnect deletes immediately.' presence_key builds exactly that key shape from TenantContext::community() and PublicKey::to_hex()."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "presence.rs's own const PRESENCE_TTL_SECS is 180, and its test presence_ttl_is_three_one_minute_heartbeat_windows asserts PRESENCE_TTL_SECS == 3 * 60 directly, matching the module doc's stated rationale rather than merely repeating it in prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "presence.rs exposes exactly four operations: set_presence (Redis SET key status EX PRESENCE_TTL_SECS), clear_presence (Redis DEL key), get_presence (Redis GET key, returning Option<String>), and get_presence_bulk (Redis MGET across a batch of keys, returning a pubkey_hex -> status HashMap that silently omits any pubkey with no live key -- expired or never set)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "presence.rs's own test same_pubkey_in_two_communities_has_different_presence_keys asserts presence_key(&community_a, &pubkey) != presence_key(&community_b, &pubkey) for the same pubkey, proving the key is community-scoped rather than global per pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "crates/buzz-pubsub/src/lib.rs's PubSubManager exposes set_presence/clear_presence/get_presence/get_presence_bulk as thin pass-throughs to the presence module's own functions, called against self.pool -- the same deadpool_redis::Pool shared with every other request-path Redis command in the crate (PUBLISH, rate-limit INCR, the NIP-98 replay SET), not a dedicated connection the way the PubSubManager's own SUBSCRIBE/PSUBSCRIBE loops require."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "buzz-core/src/kind.rs defines KIND_PRESENCE_UPDATE as u32 = 20001 (inside the 20000-29999 ephemeral-kind range) and KIND_PRESENCE_SNAPSHOT as u32 = 40902."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/event.rs's handle_ephemeral_event special-cases event_kind_u32(&event) == KIND_PRESENCE_UPDATE: it accepts either a bare status string or a legacy {\"status\": ...} JSON object as content, truncates an over-128-byte value to the nearest UTF-8 char boundary, then calls state.pubsub.clear_presence(&conn.tenant, &auth_pubkey) when the resulting status is exactly \"offline\", or state.pubsub.set_presence(&conn.tenant, &auth_pubkey, &status) for any other value -- both calls are awaited with `let _ = ...`, discarding any PubSubError. The event then falls through to the normal channel-less ephemeral publish/fan-out path so other relay pods observe the same live delta."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-relay/src/connection.rs's WebSocket-close path calls state.conn_manager.connection_ids_for_pubkey_in_community(conn.tenant.community(), auth_ctx.pubkey...) after deregistering the closing connection, and only calls state.pubsub.clear_presence(&conn.tenant, &auth_ctx.pubkey) (again via `let _ = ...`) when that call returns an empty list -- i.e. only once every WebSocket connection for that pubkey in that community has closed, not on every individual disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "crates/buzz-relay/src/state.rs's own doc comment on connection_ids_for_pubkey_in_community states callers use it 'for tenant-visible cleanup such as presence clearing and subscription eviction, so a connection in B must not keep A's derived state alive' -- naming presence clearing as the specific reason this per-community lookup exists rather than a global one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "crates/buzz-relay/src/api/bridge.rs's synthesize_presence function, documented in its own doc comment as intercepting a REQ/query filter set when 'all filters target kind:20001 or kind:40902 with authors,' calls state.pubsub.get_presence_bulk(tenant, &all_pubkeys) (defaulting to an empty map with .unwrap_or_default() on any Redis error) and, for each returned pubkey_hex/status pair, synthesizes a relay-signed kind:20001 event (content = status, a single p-tag naming the subject, created_at = current time, signed with state.relay_keypair) -- explicitly because 'ephemeral events are never stored, and kind:40902 snapshots are relay-generated on demand,' so this path never touches Postgres at all for a presence-shaped query."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "crates/buzz-core/src/tenant.rs's own module doc states the whole multi-tenant safety story rests on the invariant that 'a request's community is resolved from the connection host by the server, never supplied or influenced by the client,' and that TenantContext deliberately has 'no Default, no Deserialize, and no way to parse a community from client input' -- TenantContext::resolved is documented as callable 'only from the host-resolution path.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "crates/buzz-pubsub/src/error.rs's PubSubError enum has no presence-specific variant; a failed presence operation surfaces only as one of the crate's generic Redis(RedisError) or Pool(PoolError) variants, indistinguishable at the type level from a failure in any other Redis operation this crate performs."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/error.rs"
  - statement: "Neither presence write call site (handlers/event.rs's handle_ephemeral_event, connection.rs's disconnect cleanup) inspects, logs, or retries the Result returned by set_presence/clear_presence -- both discard it with `let _ = ...`, so a Redis pool exhaustion or command failure during a presence write is silently swallowed at both of this store's only two write paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "launchpad/docs/corpus/architecture/containers/redis.md (id architecture-containers-redis, merged/draft on origin/launchpad) already catalogues presence as one of five distinct buzz-pubsub jobs the Redis container performs (SET/GET/DEL on buzz:{community}:presence:{pubkey_hex}, 180s TTL) and separately carries an INFERENCE, at confidence 0.8, that every Redis write path in buzz-pubsub -- presence included -- is either TTL-bounded or a transient pub/sub PUBLISH, 'consistent with the crash-safety comments in publish_cache_invalidation and publish_conn_control describing a durable Postgres backstop for both' -- a backstop that node's own table does not claim for presence specifically, since presence has no Postgres row to fall back on at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "crates/buzz-datastore-tracing/src/lib.rs's #[datastore_span] macro rejects any system value other than \"postgresql\" at compile time, and crates/buzz-pubsub does not import or use datastore_span anywhere in its source -- presence, like every other buzz-pubsub Redis access pattern, carries no datastore-tracing instrumentation at the recorded revision, a gap already established at the container level in architecture-containers-redis rather than a new finding of this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Presence is best classified as the sole live representation of a pubkey's online/away status -- not a cache of a durably-stored value (no Postgres table records current or historical presence at all, so there is nothing else to be a cache of) and not merely transport (a SET writes state at rest, unlike the pure-PUBLISH channel-pubsub mechanism) -- but it is deliberately non-durable by design: a client's next heartbeat (or the relay's own kind:40902 on-demand synthesis) fully reconstructs it from scratch, so its loss is never treated as data loss anywhere in the call sites inspected."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.75
  - statement: "Issue #1095's Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1095 definition of done"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus contains no launchpad/docs/corpus/layers/ path at all -- no connection-pool.md, channel-pubsub.md, dedicated-pubsub-connection.md, key-namespacing.md or role.md sibling is merged yet, even though several are being authored in the same overnight batch, so none is a valid relationships target for this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no launchpad/docs/corpus/layers/ prefix present at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# presence: layers/data/redis

This node catalogues the Redis-backed mechanism that tracks a pubkey's live
online/away status in Buzz. It is one of the five distinct jobs
`architecture/containers/redis.md` (`architecture-containers-redis`) already
catalogues for the Redis container as a whole — "presence" — and this node is the
zoomed-in view of that one job: its key shape, the commands it issues, its
lifecycle and consistency semantics, and its tenancy and failure behavior. It does
not describe Redis's other four jobs (event fan-out, cross-pod cache invalidation,
cross-pod connection control, shared admission state), which stay in the parent
container document.

## What kind of store this is

Presence is the **sole live representation** of a pubkey's online/away status —
not a cache of a durably-stored value, because no Postgres table records current
or historical presence at all, so there is nothing else for Redis to be caching
here. It is more than pure transport too: a `SET` writes state at rest (unlike the
sibling event-fan-out mechanism, which only ever `PUBLISH`es and stores nothing).
But it is deliberately **non-durable by design**, not merely non-durable by
accident of implementation: a client's next `KIND_PRESENCE_UPDATE` heartbeat, or
the relay's own on-demand `kind:40902` synthesis, fully reconstructs the value
from nothing, and every call site inspected treats its loss as an expected,
recoverable condition rather than data loss (INFERENCE, confidence 0.75 — see the
evidence ledger).

## Owned data

One key pattern, one value shape:

| Key | Value | TTL |
|---|---|---|
| `buzz:{community}:presence:{pubkey_hex}` | An application-defined status string (`"online"`, `"away"`, or any other short string a client sends — the relay does not validate it against a fixed enum) | `PRESENCE_TTL_SECS` = 180s (3× the 60s client heartbeat interval), reset on every `set_presence` write |

The key is built from `TenantContext::community()` (never client-supplied — see
*Tenancy boundary* below) and the subject pubkey's lowercase hex encoding. There
is no separate schema, namespace, or index beyond this one key family — `GET`/`SET`
on a scalar Redis value, not a hash, set, or sorted-set structure.

## Commands

| Command | Direction | Purpose | Call site |
|---|---|---|---|
| `SET key status EX 180` | relay → Redis | Record (or refresh) a pubkey's presence, resetting the TTL on every call | `crates/buzz-pubsub/src/presence.rs` (`set_presence`) |
| `DEL key` | relay → Redis | Immediately clear a pubkey's presence on explicit "offline" or clean disconnect | `crates/buzz-pubsub/src/presence.rs` (`clear_presence`) |
| `GET key` | relay → Redis | Read one pubkey's current status, or `None` if unset/expired | `crates/buzz-pubsub/src/presence.rs` (`get_presence`) — no call site outside the crate's own tests was found at the recorded revision |
| `MGET key...` | relay → Redis | Batch-read many pubkeys' status in one round trip, silently omitting any with no live key | `crates/buzz-pubsub/src/presence.rs` (`get_presence_bulk`), called from `crates/buzz-relay/src/api/bridge.rs`'s `synthesize_presence` |

All four go through `PubSubManager`'s shared `deadpool_redis::Pool` — the same
pool every other request-path Redis command in the crate uses — not a dedicated
connection. See `architecture-containers-redis` for why the crate's
SUBSCRIBE/PSUBSCRIBE loops, unlike this store, need one.

## Access pattern, lifecycle and consistency semantics

**Write paths (two, both fire-and-forget).**

- `crates/buzz-relay/src/handlers/event.rs`'s `handle_ephemeral_event` special-cases
  `kind:20001` (`KIND_PRESENCE_UPDATE`, inside the ephemeral 20000–29999 range —
  never stored in Postgres): it accepts a bare status string or a legacy
  `{"status": ...}` JSON body, truncates anything over 128 bytes to a UTF-8 char
  boundary, then calls `clear_presence` for status `"offline"` or `set_presence`
  for any other value. The event still falls through to the normal channel-less
  ephemeral publish/fan-out path afterward, so other relay pods observe the same
  live delta through the event-fan-out mechanism, not through Redis presence
  replication.
- `crates/buzz-relay/src/connection.rs`'s WebSocket-close handler calls
  `clear_presence` only after confirming, via
  `connection_ids_for_pubkey_in_community`, that **no other live connection**
  remains for that pubkey in that community — a multi-tab or multi-device client
  does not flicker to "offline" the moment one tab closes.

**Read path (one, batch-only, bypassing Postgres entirely).**
`crates/buzz-relay/src/api/bridge.rs`'s `synthesize_presence` intercepts a
REQ/query filter set when every filter targets `kind:20001` or `kind:40902`
(`KIND_PRESENCE_SNAPSHOT`) with `authors`, calls `get_presence_bulk` once for the
deduplicated author set, and synthesizes a relay-signed `kind:20001` event per
live entry — because ephemeral events are never stored and `kind:40902` snapshots
are relay-generated on demand, this is the *only* path that can answer such a
query at all; there is no Postgres fallback to synthesize from.

**Consistency is per-pod-shared, single-writer-per-key, TTL-healing.** Every relay
pod reads and writes the same shared Redis instance (per
`architecture-containers-redis`), so there is no cross-pod propagation delay the
way the event-fan-out mechanism's PUBLISH/SUBSCRIBE has — a write from any pod is
immediately visible to a read from any other pod, ordinary single-instance Redis
consistency. A missed `clear_presence` (crash, dropped connection without a clean
close) self-heals within at most 180 seconds via TTL expiry rather than requiring
any reconciliation process.

## Tenancy and security boundary

**Every key is community-scoped**, built from `TenantContext::community()`, which
`buzz-core`'s own module doc states is "resolved from the connection host by the
server, never supplied or influenced by the client" — the same server-resolved
fence every other tenant-scoped Redis key in this crate relies on (per
`architecture-containers-redis`). The crate's own test
(`same_pubkey_in_two_communities_has_different_presence_keys`) proves the same
pubkey in two communities never collides on one key. There is no
operator-global exception in this store, unlike the IP-keyed connection-rate
limiter `architecture-containers-redis` documents for a different job.

**Security implications are the same "transport inside the relay trust domain"
boundary the container document already states**, applied to a store rather than
to pub/sub: nothing outside `buzz-relay` ever opens a Redis connection, so no
external party reads or writes a presence key directly, and a leaked presence
value discloses only "this pubkey is currently online/away," never message
content or any other tenant data.

## Failure behavior

- **A `SET`/`DEL` call fails** (Redis pool exhaustion, command error): both write
  call sites (`handlers/event.rs`, `connection.rs`) discard the `Result` with
  `let _ = ...` — the failure is silent, unlogged, and unretried at either of this
  store's only two write paths. This is a real, checked gap named here rather than
  smoothed over; it means a Redis outage during a presence write leaves stale
  state for up to `PRESENCE_TTL_SECS` (or forever, on a failed `clear_presence`
  from a pod that never retries), not an immediate visible error to any caller.
- **A `GET`/`MGET` call fails**: `synthesize_presence` (the only production read
  call site) falls back to `.unwrap_or_default()`, i.e. an empty presence map —
  a Redis outage on the read path produces "nobody is online" rather than an
  error surfaced to the REQ/query client.
- **A key expires or was never set**: `get_presence` returns `None`,
  `get_presence_bulk` simply omits that pubkey from its returned map — expiry and
  "never online" are indistinguishable to every caller, by design.
- **No presence-specific error variant exists** in `PubSubError` — every failure
  above surfaces only as the crate's generic `Redis`/`Pool` variant, so a caller
  cannot distinguish a presence-store failure from any other Redis operation
  failing without inspecting the call site itself.

## Boundary

This node does not describe:

- **Redis's other four jobs** (event fan-out, cross-pod cache invalidation,
  cross-pod connection control, shared admission state) or Redis's own
  deployment, technology version, or security implications as a whole container —
  see `architecture/containers/redis.md` (`architecture-containers-redis`), which
  this node is `part-of`.
- **Connection-pool sizing and limits** (`deadpool_redis::Pool`,
  `BUZZ_REDIS_POOL_SIZE`) beyond naming that presence shares the crate's one pool —
  a separate `layers/data/redis/connection-pool.md` task in this same batch, not
  yet merged.
- **General Redis key-namespacing conventions** beyond this one key family — a
  separate `layers/data/redis/key-namespacing.md` task in this same batch, not yet
  merged.
- **The domain meaning of "online"/"away"** as a user-facing concept, or the
  client-side heartbeat cadence itself — no data-entity-shaped corpus node for
  presence-as-a-domain-concept is merged yet to link to.
- **What `kind:40902` (`KIND_PRESENCE_SNAPSHOT`) means as a wire event** beyond
  naming that it triggers this store's read path — a wire-contract description
  belongs to an `interfaces-events`-typed node, not this datastore-layer one, and
  none is merged yet.

## Relationships

- `part-of`: `architecture-containers-redis` — presence is one of that node's own
  five catalogued jobs, zoomed in.

## Scope and omissions

**This node covers** the presence key shape and TTL, the four Redis commands this
store issues and their call sites, its two write paths and one read path with
their lifecycle and consistency semantics, its tenancy and security boundary, and
its failure behavior at each of the points named above.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's other four jobs and the container as a whole | `architecture-containers-redis` (merged) |
| Connection-pool sizing and limits | `layers/data/redis/connection-pool.md` (this batch, not yet merged) |
| General Redis key-namespacing conventions | `layers/data/redis/key-namespacing.md` (this batch, not yet merged) |
| The domain meaning of online/away status, and client heartbeat cadence | No data-entity-shaped node merged yet |
| `kind:20001`/`kind:40902`'s own wire contract | No `interfaces-events`-shaped node merged yet |

**Expected but not verified when this node was written:**

- **No production or staging telemetry was inspected** for how often the
  silently-swallowed write failures named in *Failure behavior* actually occur, or
  how long stale presence typically persists in practice beyond the 180s TTL
  worst case reasoned from code.
- **`get_presence` (the single-pubkey read) has no production call site** found
  anywhere outside the crate's own tests at the recorded revision — whether it is
  dead code, reserved for a future caller, or used by a path this search missed
  was not established.
- **The `type: layers` override recorded in this node's evidence ledger has not
  been checked against a later, corpus-authored `layers`-type standard**, because
  none is merged at the recorded revision — see the disclosed `TEAM_KNOWLEDGE`
  entry above.
- **Whether Redis presence should be classified "cache" outright, rather than the
  more qualified framing this node uses**, is disclosed as an `INFERENCE` at
  confidence 0.75 rather than settled — a reviewer may reasonably read it either
  way, and the ledger states the reasoning rather than asserting a flat answer.
