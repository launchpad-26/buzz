---
id: layers-data-redis-key-namespacing
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
  - statement: "crates/buzz-pubsub/src/topic.rs declares pub const BUZZ_PREFIX: &str = \"buzz\"; and builds EventTopicKey::redis_channel as buzz:{community}:channel:{channel_id} for EventTopic::Channel and buzz:{community}:global for EventTopic::Global, exposed via the channel_key and global_key helper functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "topic.rs's EventTopicKey::parse_redis_channel splits a channel name on ':', requires the first segment to equal BUZZ_PREFIX exactly, the second segment to parse as a UUID (the community id), the third segment to be the literal channel or global, and rejects any channel with a trailing extra segment or a malformed UUID; its own unit test rejects strings such as buzz:00000000-0000-0000-0000-00000000aaaa:presence:abc precisely because presence is not a recognized topic scope for this parser."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "crates/buzz-pubsub/src/presence.rs builds presence_key as buzz:{community}:presence:{pubkey_hex} (pubkey.to_hex(), lowercase per the nostr crate's hex encoding, confirmed by the module's own test_presence_key_format asserting the suffix is 64 ASCII-hex characters), sets it via SET ... EX PRESENCE_TTL_SECS (180, documented as 3x the 60s heartbeat interval so one missed heartbeat does not flap presence), and deletes it immediately on clean disconnect via clear_presence's DEL."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "crates/buzz-pubsub/src/conn_control.rs builds conn_control_channel as buzz:{community}:conn-control (CONN_CONTROL_SUFFIX = \"conn-control\"), is subscribed to across every community on one pod via the pattern buzz:*:conn-control (CONN_CONTROL_PATTERN), and parse_conn_control_channel enforces the same three-segment-exact-match shape topic.rs's parser enforces, rejecting a trailing extra segment or non-UUID community."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "crates/buzz-pubsub/src/cache_invalidation.rs builds cache_invalidation_channel as buzz:{community}:cache-invalidate (CACHE_INVALIDATION_SUFFIX = \"cache-invalidate\"), subscribed cross-community via the pattern buzz:*:cache-invalidate (CACHE_INVALIDATION_PATTERN), with parse_cache_invalidation_channel enforcing the identical exact-segment-count shape; the module's own doc comment states the published payload is 'a pure cache-key drop... never an evict payload' because the next read re-fetches authoritative state from Postgres."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "crates/buzz-auth/src/nip98_replay.rs's nip98_replay_key_for_scope builds buzz:{scope}:nip98:{event_id_hex} as a plain format! literal (buzz-auth does not depend on buzz-pubsub and does not reference its BUZZ_PREFIX constant), and crates/buzz-pubsub/src/nip98_replay.rs's RedisNip98ReplayGuard::try_mark_in_scope issues a single SET buzz:{community}:nip98:{event_id_hex} 1 NX EX <ttl> against that key, where ttl_secs is clamped to [DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS] before the call; NX makes the write atomic set-if-absent, so a second claim within the TTL window returns None (surfaced as Ok(false), i.e. replay)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "crates/buzz-auth/src/rate_limit.rs's rate_limit_key builds buzz:{community}:ratelimit:{pubkey_hex}:{suffix} (also a plain format! literal, not importing buzz-pubsub's BUZZ_PREFIX) and its sibling ip_rate_limit_key builds buzz:ratelimit:ip:{ip}:conn with no community segment at all -- the rate_limit_key doc comment states this is deliberate: 'Operator-global by design', because an abusive IP is not a per-community property, unlike every other key pattern in this ledger which is community-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "crates/buzz-pubsub/src/rate_limiter.rs's RedisRateLimiter runs both key families through the same RATE_LIMIT_SCRIPT, a Lua script that atomically INCRs the key and, only on the first increment (count == 1), sets EXPIRE to window_secs; if a subsequent TTL read comes back negative (a key surviving without an expiry, from a crash between INCR and EXPIRE in a hypothetical non-atomic implementation) run_rate_limit repairs it with a fresh EXPIRE and logs a warning, and its own module doc comment states fixed windows allow up to 2x burst at window boundaries as a known, unresolved limitation."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "crates/buzz-relay/src/tunnel/directory.rs's SessionKeys::new builds a base of buzz:{community_id}:tunnel:{session_id}, then a lease key ({base}:lease) and a generation key ({base}:generation); SessionDirectory issues these directly against a redis::Script (ACQUIRE_SCRIPT/RENEW_SCRIPT/RELEASE_SCRIPT/VALIDATE_SCRIPT) without going through buzz-pubsub, and buzz-relay/Cargo.toml lists redis and deadpool-redis as its own direct dependencies rather than routing Redis access through the buzz-pubsub crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "directory.rs's ACQUIRE_SCRIPT sets the lease key with SET ... PX ttl_ms (default DEFAULT_LEASE_TTL = 30 seconds, renewed on RENEW_SCRIPT via PEXPIRE), but the generation key is only ever created via INCR inside ACQUIRE_SCRIPT and is never the target of any EXPIRE, PEXPIRE or DEL call across all four Lua scripts in the file -- it is a durable, un-TTL'd monotonic counter for the lifetime of the community, in contrast to the lease key it sits beside; SessionLease's own doc comment states the generation is 'Never derived from expiring lease state.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "crates/buzz-deletion/src/lib.rs's publish_disconnect_community issues PUBLISH directly against buzz:{community}:conn-control (the same channel conn_control.rs defines and subscribes to), and purge_redis_namespace / verify_redis_absence both operate on the wildcard pattern buzz:{community}:* via Redis SCAN, with purge_redis_namespace following each SCAN page with UNLINK on the returned keys and verify_redis_absence running two complete SCAN passes before accepting absence, with a comment stating 'SCAN is weakly consistent... two complete empty passes ensure a cursor rollover or concurrent expiry cannot make one sparse pass look absent.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "crates/buzz-deletion/Cargo.toml lists redis and deadpool-redis as direct dependencies, and buzz-deletion does not depend on buzz-pubsub -- confirming purge_redis_namespace and publish_disconnect_community issue their Redis commands directly rather than through buzz-pubsub's PubSubManager."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/Cargo.toml"
  - statement: "architecture-containers-redis's own Ownership boundary paragraph states 'buzz-pubsub owns every Redis access pattern and key-naming convention in this table -- nothing outside that crate issues a Redis command directly,' but that claim does not hold at this node's recorded revision: crates/buzz-deletion/src/lib.rs and crates/buzz-relay/src/tunnel/directory.rs both issue Redis commands directly (PUBLISH, SCAN, UNLINK, and four Lua scripts respectively) against keys under the same buzz: prefix, neither routing through buzz-pubsub's PubSubManager nor its Redis-backed guard types -- named here as a real, evidence-backed discrepancy against the container node rather than smoothed over, and not resolved by this node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "The wildcard pattern buzz:{community}:* that buzz-deletion's purge/verify functions scan against is structural proof that every Redis key this repository writes under the buzz: prefix is expected to nest under its community's UUID segment as the complete boundary of that community's Redis footprint -- a whole-community deletion sweep would silently leave orphaned data behind for any key that violated the {prefix}:{community}:... shape, so the sweep's own correctness depends on universal adherence to the convention documented in this node's structured-entries table."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
    confidence: 0.75
  - statement: "The operator-global rate-limit key buzz:ratelimit:ip:{ip}:conn is the one key pattern in this ledger that the buzz:{community}:* deletion sweep cannot reach, because it carries no community segment; deleting a community therefore cannot and does not clear per-IP connection counters, which is consistent with those counters being about the IP, not about any one community's data."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
      - "crates/buzz-deletion/src/lib.rs"
    confidence: 0.7
  - statement: "No Redis key-building call site outside crates/buzz-pubsub, crates/buzz-auth, crates/buzz-relay/src/tunnel and crates/buzz-deletion was found in this session's search of every format!(\"buzz:... occurrence across the crates/ tree; this is a search result at the recorded revision, not a proof of completeness, and is named as a gap in this node's own scope-and-omissions section rather than asserted as exhaustive."
    entry_class: INFERENCE
    evidence:
      - "grep_format_buzz_prefix(pattern='format!(\"buzz:', scope='crates/', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> matches confined to buzz-pubsub, buzz-auth, buzz-relay/src/tunnel, buzz-deletion; buzz-cli/src/links.rs matches are unrelated buzz:// CLI deep-link URIs, not Redis keys"
    confidence: 0.6
  - statement: "crates/buzz-pubsub/src/lib.rs carries a doc comment 'Redis pub/sub fan-out, presence tracking, and typing indicators' and crates/buzz-pubsub/src/error.rs documents errors 'in pub/sub, presence, and typing operations,' but no typing module, file, or buzz:...:typing... key pattern exists anywhere in crates/buzz-pubsub/src/ at the recorded revision -- the same gap architecture-containers-redis's own scope-and-omissions section already names; this node does not add a typing-indicator row for the same reason and does not re-resolve the question."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/error.rs"
  - statement: "Issue #1094's Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1094 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis key namespacing (reference)

**Reference description.** This node catalogues the naming convention every Redis
key and pub/sub channel this repository writes actually follows: the segment shape
`{prefix}:{scope}:{purpose}[:identifier...]`, what each segment encodes, and which
namespaces exist at the recorded revision. `architecture-containers-redis`
(`launchpad/docs/corpus/architecture/containers/redis.md`) already states, at one
line per job, *that* Redis holds five (in that node's telling) distinct
responsibilities and *which* module owns each; this node is the zoom-in that
document's own text defers to — the convention's exact shape, its encoding rules,
its one documented tenancy exception, and the modules that actually build each key,
including two (`buzz-relay`'s tunnel session directory and `buzz-deletion`'s
whole-community purge) the container node's "nothing outside `buzz-pubsub` issues a
Redis command directly" claim misses. This node does not restate what Redis is *for*
(the container node's job) or the domain meaning of any identifier embedded in a key
(a data-entity node's job, none of which exists in this corpus yet for Redis-held
identifiers).

## Convention shape

Every pattern below is one of two shapes:

- **Tenant-scoped:** `buzz:{community_id}:{purpose}[:identifier...]` — the second
  segment is always the resolved community's UUID (`TenantContext::community()`'s
  `Display`), which is the tenancy fence: the same identifier under two different
  communities always produces two different keys, and every namespace below except
  one is built this way.
- **Operator-global:** `buzz:ratelimit:ip:{ip}:conn` — the one documented exception.
  No community segment exists at all; `rate_limit.rs`'s own doc comment states this
  is deliberate because an abusive IP is not a per-community property.

The literal prefix `buzz` is not a single shared constant: `buzz-pubsub::topic`
declares it once as `BUZZ_PREFIX` and every pattern in that crate is built from it,
but `buzz-auth::nip98_replay` and `buzz-auth::rate_limit` each format the literal
`"buzz:"` independently, since `buzz-auth` has no dependency on `buzz-pubsub`.
Identifiers are rendered lowercase throughout: community and channel/session ids as
UUID `Display`, pubkeys as lowercase hex (`PublicKey::to_hex()`) — `rate_limit.rs`
carries a dedicated unit test (`rate_limit_key_components_are_lowercase`) pinning
this specifically, because a future uppercase-emitting change anywhere in that chain
would silently double a principal's effective quota by splitting it across two keys.

## Namespace inventory

| Pattern | Purpose | Classification | Tenancy scope | Lifecycle / TTL | Owning module(s) |
|---|---|---|---|---|---|
| `buzz:{community}:channel:{channel_id}` | Event routing for one exact channel | Transport (pub/sub) | Community-scoped | No storage — PUBLISH/SUBSCRIBE only | `buzz-pubsub::topic` |
| `buzz:{community}:global` | Community-wide event routing | Transport (pub/sub) | Community-scoped | No storage — PUBLISH/SUBSCRIBE only | `buzz-pubsub::topic` |
| `buzz:{community}:presence:{pubkey_hex}` | Online/away status | Cache (ephemeral derived state) | Community-scoped | `SET ... EX 180`; explicit `DEL` on clean disconnect | `buzz-pubsub::presence` |
| `buzz:{community}:conn-control` | Cross-pod disconnect/ban enforcement | Transport (pub/sub) | Community-scoped (subscribed via pattern `buzz:*:conn-control`) | No storage — PUBLISH/SUBSCRIBE only | `buzz-pubsub::conn_control` (subscriber); also published directly by `buzz-deletion` |
| `buzz:{community}:cache-invalidate` | Cross-pod local-cache key drops | Transport (pub/sub) | Community-scoped (subscribed via pattern `buzz:*:cache-invalidate`) | No storage — PUBLISH/SUBSCRIBE only | `buzz-pubsub::cache_invalidation` |
| `buzz:{community}:nip98:{event_id_hex}` | NIP-98 HTTP-auth replay-seen marker | Derived guard state (dedup) | Community-scoped | `SET ... NX EX <ttl>`, `ttl` clamped to `[DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS]` | Key: `buzz-auth::nip98_replay`. Writer: `buzz-pubsub::nip98_replay` (`RedisNip98ReplayGuard`) |
| `buzz:{community}:ratelimit:{pubkey_hex}:{suffix}` | Per-principal rate-limit counter | Derived guard state (counter) | Community-scoped | Atomic Lua `INCR` + `EXPIRE(window_secs)` on first increment; self-repaired with a fresh `EXPIRE` if found without one | Key: `buzz-auth::rate_limit`. Writer: `buzz-pubsub::rate_limiter` (`RedisRateLimiter`) |
| `buzz:ratelimit:ip:{ip}:conn` | Per-IP connection rate-limit counter | Derived guard state (counter) | **Operator-global** (no community segment) | Same atomic Lua `INCR` + `EXPIRE` mechanism | Key: `buzz-auth::rate_limit`. Writer: `buzz-pubsub::rate_limiter` |
| `buzz:{community}:tunnel:{session_id}:lease` | Mesh tunnel session ownership lease | Derived guard state (ownership fence) | Community-scoped | `SET ... PX <ttl_ms>` (default 30s), renewed via `PEXPIRE`, released via `DEL` | `buzz-relay::tunnel::directory` (`SessionDirectory`, direct `redis::Script`, not via `buzz-pubsub`) |
| `buzz:{community}:tunnel:{session_id}:generation` | Monotonic fencing counter for a tunnel session | Derived guard state (durable counter) | Community-scoped | `INCR` only — **never expired or deleted** by any of the four Lua scripts that touch it | `buzz-relay::tunnel::directory` |

No row in this table is **authoritative**: the durable system of record for every
domain fact these keys route around, guard, or cache is Postgres, per
`architecture-containers-redis`'s own INFERENCE that Redis is "a volatile
coordination and rate-limiting layer rather than a system of record." This node's
own classification column narrows that to per-pattern granularity: five transport
rows carry no stored state at all, one is an explicitly ephemeral cache, and four
are derived guard state a caller consults to make a decision (admit/deny, own/don't
own) that Postgres or the caller's own logic ultimately backstops.

## Consistency semantics and failure behavior

**Transport rows (channel, global, conn-control, cache-invalidate).** Delivery is
at-most-once per currently-subscribed pod; nothing is persisted, so a subscriber
that is down or reconnecting simply misses the message. `cache-invalidate` and
`conn-control` are both explicitly fire-and-forget at their publish call sites, and
both document a durable Postgres-backed fallback for a dropped message: a missed
cache-invalidation is bounded by the per-event access gate re-reading authoritative
state on the next request, and a missed disconnect is bounded by the durable ban row
still refusing the banned principal's next auth attempt even if live disconnection
was missed on some pod.

**The presence row** fails toward "offline," not toward a stale "online": TTL expiry
without a heartbeat renewal removes the key, so a crashed connection reads as absent
rather than as indefinitely online. `PRESENCE_TTL_SECS` (180s) is deliberately 3x the
60s heartbeat interval specifically so one missed heartbeat does not cause presence
to flap.

**The NIP-98 replay row** is fail-closed by construction: the atomic `SET NX`
primitive is the freshness proof itself — a `RedisError` from the pool or the command
is surfaced as `AuthError::Internal` and the guard's own doc comments require the
caller to fail closed on that error, per this node's own citation of
`try_mark_in_scope`'s error-path comments.

**The two rate-limit rows** share one atomicity guarantee (a single Lua script
combining `INCR` and `EXPIRE` so a crash between the two calls cannot leave a
key without a TTL) and one known, undocumented-as-fixed limitation: fixed windows
allow up to 2x burst at a window boundary, per the module's own top-of-file comment.
A key found with a negative TTL (evidence of a pre-atomicity-fix crash state) is
self-repaired with a fresh `EXPIRE` rather than left broken.

**The tunnel lease/generation pair** is a fencing primitive, not a cache: `lease`
answers "who currently owns this session" (TTL-bounded, so a crashed owner's lease
expires and the session becomes acquirable again), while `generation` answers "which
attempt is this" and is deliberately never expired — `SessionLease`'s own doc comment
states the generation is "never derived from expiring lease state," so a session's
fencing counter cannot silently reset just because its lease TTL lapsed. A frame
carrying a stale generation is rejected as `MeshError::OwnerMismatch` regardless of
whether the lease itself is still held.

## Tenancy and security boundaries

Every row except one nests under the resolved community's UUID as its second
segment, which is the tenancy fence: two communities holding what would otherwise be
an identical identifier (a pubkey, a channel id, a session id) always produce
distinct keys, confirmed directly for four of the patterns above by dedicated unit
tests asserting inequality across two synthetic communities for the same identifier.
The one exception, `buzz:ratelimit:ip:{ip}:conn`, is deliberately *not*
community-scoped, per its own doc comment, because an abusive IP address is a
property of the network origin, not of any one community.

This convention is not merely descriptive: `buzz-deletion`'s whole-community erasure
path treats `buzz:{community}:*` as the entire boundary of a community's Redis
footprint, both to purge it (`SCAN` + `UNLINK` in `purge_redis_namespace`) and to
prove its absence afterward (`verify_redis_absence`, run as two full `SCAN` passes
specifically because `SCAN` is weakly consistent and a single sparse pass cannot
distinguish a rollover from genuine emptiness). Any key ever written under the
`buzz:` prefix without a community segment as its second component — like the
operator-global IP rate-limit key, by design — is invisible to that sweep and is not
cleared by deleting a community. Every key *with* the community segment, including
the un-TTL'd tunnel generation counter, is within the sweep's reach and is the only
mechanism (short of natural TTL expiry, which the generation key never gets) that
reclaims it.

`buzz-pubsub`, `buzz-auth`, `buzz-relay::tunnel::directory` and `buzz-deletion` each
issue Redis commands directly against this shared key space; none of the four
crates enforces the convention structurally (there is no shared key-builder type
across all of them — `buzz-pubsub` and `buzz-auth` each format their own `"buzz:"`
literal independently, as noted above). The convention holds at the recorded
revision only because every call site was written to match it, not because anything
prevents a new call site from drifting.

## Boundary

This node does not describe:

- **What Redis is for, or why it exists as a container in Buzz's architecture** —
  that is `architecture-containers-redis`'s subject; this node assumes that context
  and zooms into the naming convention alone.
- **The domain meaning of any identifier embedded in a key** (what a channel, a
  Nostr event id, or a mesh session actually represents) — no data-entity corpus
  node exists yet for any of these identifiers to link to; this is named as a gap,
  not resolved here.
- **Redis operational tuning** (ElastiCache sizing, eviction policy, failover) —
  `architecture-containers-redis` already names this as its own out-of-scope gap,
  and this node inherits that boundary rather than re-arguing it.
- **Step-by-step instructions for building a new key pattern** — that would be a
  procedure/how-to node's shape, not this reference catalogue's.

## Relationships

- `part-of`: `architecture-containers-redis` — this node zooms into one structural
  facet (the key-naming convention) of the container that document already
  inventories at one line per job.

No relationship is declared toward the three sibling `layers/data/redis/*` tasks
named in this batch's dispatch brief (#1091 channel-pubsub, #1092 connection-pool,
#1093 dedicated-pubsub-connection): none is merged to `origin/launchpad` at the
recorded revision (confirmed via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), so none is
a valid `relationships[].target` yet, per `AGENTS.md`'s own merge-target rule.

## Scope and omissions

**This node covers** the Redis key- and channel-naming convention this repository's
code actually implements at the recorded revision: the two segment shapes (tenant-
scoped and operator-global), the encoding rules for each segment, the full namespace
inventory with its classification, tenancy scope, and lifecycle per row, the
consistency/failure-mode behavior grouped by classification, and the load-bearing
role the convention plays in whole-community Redis deletion.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What Redis is for and its container-level ownership boundary | `architecture-containers-redis` |
| The domain meaning of channel/session/event identifiers embedded in keys | A future data-entity node; none exists yet for these identifiers |
| ElastiCache operational tuning, eviction policy, failover | `architecture-containers-redis`'s own named gap |
| Whether a typing-indicator Redis key pattern is planned, removed, or never built | Unresolved by either this node or `architecture-containers-redis` |
| Sibling `layers/data/redis/*` documents (channel-pubsub #1091, connection-pool #1092, dedicated-pubsub-connection #1093) | Not yet authored at this node's writing time |

**Expected but not verified when this node was written:**

- **Completeness of the namespace inventory is a search result, not a proof.** This
  node's own INFERENCE entry above states the search covered every `format!("buzz:`
  call site found across `crates/` at the recorded revision, confined to
  `buzz-pubsub`, `buzz-auth`, `buzz-relay::tunnel`, and `buzz-deletion` — a fifth,
  unfound call site building a `buzz:`-prefixed key elsewhere in the workspace
  (desktop, mobile, or a script outside `crates/`) would not be caught by this
  search and is not ruled out.
  - **Whether the `architecture-containers-redis` ownership-boundary claim this node
  contradicts should itself be corrected** was not decided here — this node states
  the discrepancy with citations and leaves the correction to whoever next revises
  that container node.
- **Whether any environment configuration or infrastructure repository (outside this
  one) imposes additional Redis key conventions** — e.g. an operator tool reading
  `buzz:` keys directly — was not checked; this node's evidence is confined to what
  this repository's own source contains.
