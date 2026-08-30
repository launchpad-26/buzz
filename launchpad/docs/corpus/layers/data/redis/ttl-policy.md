---
id: layers-data-redis-ttl-policy
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
  - statement: "node.schema.json's type enum has thirteen members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and no member specific to a cross-cutting operational convention such as TTL policy; layers is the closest concrete fit for a node documenting the data/storage layer's own internal behavior, per standards/taxonomy.md's own choosing-a-value guidance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "This task's own dispatch context (the corpus-batch-author overnight run for parent Feature #610) establishes that every layers/data/... document in this batch uses type: layers regardless of what a chosen template's own worked example independently suggests for a real instance node (templates/datastore.md's own evidence ledger, for example, reasons toward type: architecture for a real datastore instance), and that no layers/data/redis/* sibling exists on origin/launchpad yet because several such documents exist only in unmerged sibling PRs from this same overnight batch -- both facts taken as given context for this task rather than independently re-derived."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight dispatch brief for launchpad-26/buzz#1098 / parent Feature #610"
  - statement: "Issue #1098's own Objective section names the target path launchpad/docs/corpus/layers/data/redis/ttl-policy.md directly, and parent Feature #610's title is 'data and storage layer corpus exists' with outcome text naming 'Redis and object-storage behavior... documented with lifecycle, consistency and verification links' -- both read directly via gh issue view, confirming the surface this node documents is the data/storage layer rather than, for example, a governance or operations concern."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1098"
      - "https://github.com/launchpad-26/buzz/issues/610"
  - statement: "launchpad/docs/corpus/architecture/containers/redis.md (id architecture-containers-redis, status: draft) is merged on origin/launchpad at the recorded revision, and already documents Redis's existence, its owning crate (buzz-pubsub), its connected containers, and a one-line-per-mechanism summary of presence/rate-limiter/NIP-98-replay/cache-invalidation/conn-control key formats -- container depth, not the cross-cutting TTL-value/consistency/fail-behavior synthesis this node adds."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "architecture-containers-redis's own Scope and omissions section names 'the rate-limit tier design' and staging ElastiCache provisioning as explicit gaps, and separately states typing-indicator Redis delivery is unresolved (a stray doc comment references it but no typing module, file, or Redis key pattern exists in buzz-pubsub at its recorded revision) -- none of these gaps concern the mesh/tunnel session-lease mechanism this node documents, which architecture-containers-redis does not mention anywhere in its body (checked directly: no 'tunnel', 'lease', or 'mesh' text appears in the file)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "crates/buzz-pubsub/src/presence.rs's module doc states presence is 'Stored as SET buzz:{community}:presence:{pubkey_hex} \"online\" EX 180' and that 'TTL is 3x the 60s heartbeat interval so a single missed heartbeat does not cause presence flap'; PRESENCE_TTL_SECS is a pub const u64 = 180, and set_presence issues SET key status EX PRESENCE_TTL_SECS while clear_presence issues DEL, called on clean disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "crates/buzz-relay/src/handlers/event.rs (around the presence-update branch) and crates/buzz-relay/src/connection.rs (around WebSocket disconnect and deregistration) both call state.pubsub.set_presence / clear_presence with the result explicitly discarded via `let _ = ...`, rather than propagated as an error to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "crates/buzz-pubsub/src/rate_limiter.rs implements a fixed-window counter via a single Lua script (RATE_LIMIT_SCRIPT) that INCRs the key and conditionally EXPIREs it only on the first increment, explicitly to eliminate 'the crash window where a key could exist without a TTL'; run_rate_limit additionally detects a negative TTL (key exists with no expiry, from a pre-atomicity crash state) and repairs it with a fresh EXPIRE, logging a warning."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "crates/buzz-auth/src/rate_limit.rs's RateLimiter trait doc states, under a 'Tenant scoping' heading, that pubkey-keyed limits use a community-prefixed key (buzz:{community}:ratelimit:{pubkey}:{suffix}, built by rate_limit_key) while IP-keyed limits are 'operator-global by design' using buzz:ratelimit:ip:{ip}:conn (built by ip_rate_limit_key), explaining that IP-based admission happens before host-to-community resolution completes, so threading TenantContext through it would invert the order of operations; a unit test (rate_limit_key_isolates_communities_for_same_pubkey) pins the same pubkey in two communities to two distinct keys, citing this as the 'S1 cross-community isolation fence.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "crates/buzz-relay/src/admission.rs's check_principal maps a rate-limiter Err to AdmissionError::Unavailable (logging a warning), and both of its call sites -- connection.rs's send_admission_result and api/bridge.rs's HTTP handler -- treat AdmissionError::Unavailable as a rejection (the WebSocket request is refused with a 'shared admission unavailable' message; the HTTP call returns 503 Service Unavailable), not as a pass-through allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/admission.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "A repository-wide grep for check_ip_connection (the IP-keyed rate-limit method on the RateLimiter trait) finds only its trait definition and doc comment in crates/buzz-auth/src/rate_limit.rs; no call site was found in crates/buzz-relay or elsewhere at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_result('check_ip_connection', scope='crates/') -> crates/buzz-auth/src/rate_limit.rs only, trait definition and doc comment; no call site found in crates/buzz-relay or elsewhere"
  - statement: "crates/buzz-auth/src/nip98_replay.rs's module doc names this mechanism a '§5 hard gate' requiring 'shared state (Redis), atomic set-if-absent, TTL >= 120s' and 'community-scoped key'; it defines DEFAULT_REPLAY_TTL_SECS = 120 as the floor (matching '2x the ±60s NIP-98 clock-skew tolerance') and MAX_REPLAY_TTL_SECS = 3600 as the ceiling (to stay well inside Redis EX's signed-64-bit argument and avoid pathologically long-lived entries); the Nip98ReplayGuard::try_mark doc states implementations 'MUST clamp' both bounds rather than honoring an out-of-range value as given, and that 'on Err (Redis unreachable, etc.) callers MUST fail closed -- reject the request rather than admitting it.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "crates/buzz-pubsub/src/nip98_replay.rs's RedisNip98ReplayGuard clamps ttl_secs to [DEFAULT_REPLAY_TTL_SECS, MAX_REPLAY_TTL_SECS] before issuing SET key 1 NX EX <ttl>, treats a redis-rs Some(\"OK\") reply as a fresh claim (Ok(true)) and None as an existing key (Ok(false), i.e. replay), and maps any Redis error to Err(AuthError::Internal(...)) with a log line reading 'caller MUST fail closed' -- propagating the error rather than defaulting to allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "crates/buzz-auth/src/nip98_replay.rs's nip98_replay_key_for_scope builds keys as buzz:{scope}:nip98:{event_id_hex}, and the community-scoped wrapper nip98_replay_key passes ctx.community().to_string() as scope -- the same buzz:{community}:... convention used by presence and per-principal rate limits."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "crates/buzz-relay/src/tunnel/directory.rs's module doc states a 'Correctness law: mesh membership is only a routing hint. Redis is the arbiter for session ownership, and every session-bearing frame must validate its {session_id, generation, owner_runtime_id} fence against this directory before it is accepted or forwarded.' DEFAULT_LEASE_TTL is a const Duration = Duration::from_secs(30); the ACQUIRE_SCRIPT and RENEW_SCRIPT Lua scripts write the lease key with SET ... PX ttl_ms / PEXPIRE ... ttl_ms respectively, alongside a companion, non-expiring *:generation counter key that fences stale claims across a lease loss and re-acquisition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "SessionKeys::new in directory.rs builds lease/generation keys as buzz:{community_id}:tunnel:{session_id}:lease and buzz:{community_id}:tunnel:{session_id}:generation -- community-scoped, per the key_shape_is_community_scoped_and_separates_counter unit test that pins this exact format."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "SessionDirectory::acquire and ::renew in directory.rs propagate any Redis pool-acquisition or script-invocation error via `?` as a DirectoryError, with no fallback path that treats an error as 'no lease' or otherwise proceeds; renew additionally returns a distinct RenewResult::Lost variant when the stored owner/generation no longer matches the caller's, both of which the caller is required to treat as no-longer-owning rather than as still-holding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/directory.rs"
  - statement: "crates/buzz-relay/src/tunnel/reliable.rs defines const DEFAULT_RENEW_INTERVAL: Duration = Duration::from_secs(10), used by spawn_lease_renewer to drive a tokio::time::interval loop that calls directory.renew(&lease) on every tick -- a 10s renewal cadence against directory.rs's 30s DEFAULT_LEASE_TTL, the same 3x heartbeat-to-TTL ratio presence.rs documents for its own 60s heartbeat against a 180s TTL."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tunnel/reliable.rs"
  - statement: "crates/buzz-pubsub/src/cache_invalidation.rs's module doc states relay pods keep in-memory (moka) membership/visibility caches and that 'other pods would otherwise rely on the 10s TTL to expire stale entries' before this module's own cross-pod pub/sub key-drop mechanism takes over; that 10s TTL governs a local in-process moka cache entry, not a Redis key, and is therefore a distinct mechanism from every Redis-key TTL this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_TYPING_INDICATOR = 20002 with the doc comment 'Ephemeral: typing indicator for a channel'; a repository-wide grep for KIND_TYPING_INDICATOR shows it used only to build/publish an ephemeral Nostr event (in crates/buzz-acp/src/relay.rs) and in the kind registry, with no Redis SET/EXPIRE/TTL call site anywhere in the workspace at the recorded revision -- corroborating, from an independent starting point, architecture-containers-redis's own flagged-but-unresolved note that no typing-specific Redis key pattern exists in buzz-pubsub despite the crate's Cargo.toml description mentioning typing indicators."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep_result('KIND_TYPING_INDICATOR', scope='crates/', include='*.rs') -> crates/buzz-core/src/kind.rs, crates/buzz-acp/src/relay.rs, crates/buzz-acp/src/lib.rs, crates/buzz-acp/src/config.rs, crates/buzz-backend-kubernetes/src/wire.rs; no Redis call site among them"
  - statement: "Every Redis key this node documents backs state that is either reconstructable from a client's next heartbeat/request (presence, rate-limit counters), inherently time-bounded by design (the NIP-98 replay window), or actively fenced by a non-expiring companion counter (the mesh lease's *:generation key) -- none of it is the durable record of any Buzz entity, which architecture-containers-redis's own 'Data implications' section already states plainly ('Redis holds no durable Buzz data'). Classifying every TTL-governed key in this node's inventory as derived/ephemeral state rather than authoritative is this node's own synthesis across the five mechanisms, not a restatement of a single source, and is offered as reasoning rather than as an independently sourced fact."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
    confidence: 0.85
  - statement: "Issue #1098's own Definition of Done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1098 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-redis
---

# Redis TTL policy

How Buzz's Redis-backed mechanisms use key expiry (`EX`/`PX`/`EXPIRE`/`PEXPIRE`) as a
correctness and cleanup tool: which key namespaces carry a TTL, what duration and
refresh cadence each uses, what happens when a key expires or Redis becomes
unreachable, and which of those mechanisms are tenant-scoped versus operator-global.
This node is `part-of` `architecture-containers-redis`, which already establishes that
Redis exists, which crate owns it (`buzz-pubsub`), and a one-line-per-mechanism summary
of its key formats; this node adds the cross-cutting TTL-value, consistency, and
fail-behavior depth that container-level document deliberately keeps to one line each.

## Purpose and scope

**This node covers** every Redis key in this repository that carries an explicit
expiry, at the recorded revision: the presence key, the per-principal and per-IP
rate-limit counters, the NIP-98 replay marker, and the mesh/tunnel session lease (plus
its non-expiring companion generation counter). For each, it states the key shape,
the TTL/PTTL value and where it comes from, the refresh mechanism (if any), what a
reader or writer of the key should expect at and after expiry, and what happens to the
mechanism's callers if Redis itself is unreachable.

**It does not** document Redis's own existence, technology, or connection profile
(`architecture-containers-redis`'s job), the non-TTL pub/sub channels `buzz-pubsub`
also uses (cache-invalidation and connection-control broadcasts carry no stored key at
all), or the local in-process moka cache TTL in `cache_invalidation.rs` — a
same-numbered but unrelated mechanism, named explicitly in *Scope and omissions* to
head off confusing the two.

## Store classification

**Every key this node documents is derived/ephemeral state, never the authoritative
record of anything.** Postgres (`buzz-db`) holds Buzz's durable events, users,
channels, and moderation state; Redis's role here is either a rebuildable liveness
signal (presence, rate-limit counters — both regenerate from the next client
heartbeat or request) or a correctness fence with a naturally bounded lifetime (the
NIP-98 replay marker exists only to reject a duplicate inside a clock-skew window; the
mesh lease exists only while a runtime is actively serving a session and is designed to
be reclaimed the moment it stops renewing). None of the five mechanisms below is a
cache of Postgres data in the read-through sense — each is its own, self-contained
piece of transient state.

## Key namespace / TTL inventory

| Namespace | Key shape | TTL / PTTL | Refresh | Tenancy |
|---|---|---|---|---|
| Presence | `buzz:{community}:presence:{pubkey_hex}` | `EX 180` (`PRESENCE_TTL_SECS`), fixed | Re-`SET ... EX 180` on every ~60s client heartbeat; `DEL` on clean disconnect | Community-scoped |
| Rate limit (per-principal) | `buzz:{community}:ratelimit:{pubkey_hex}:{suffix}` | `EXPIRE <window_secs>`, caller-supplied per `LimitType` (observed: 5s WS-burst window, 60s per-minute `Messages` window) | Set once on the window's first `INCR`; not renewed mid-window, self-repaired if found missing | Community-scoped |
| Rate limit (per-IP) | `buzz:ratelimit:ip:{ip}:conn` | Same mechanism as above, caller-supplied window | Same as above | **Operator-global** — deliberately not community-scoped; see *Tenancy and security boundaries* |
| NIP-98 replay marker | `buzz:{community\|scope}:nip98:{event_id_hex}` | `EX <ttl>`, clamped to `[DEFAULT_REPLAY_TTL_SECS=120, MAX_REPLAY_TTL_SECS=3600]` | Not renewed — a single atomic `SET NX EX` claim per event id, by design | Community-scoped (or an explicit trusted scope for the non-default entry point) |
| Mesh session lease | `buzz:{community_id}:tunnel:{session_id}:lease` | `PX 30000` (`DEFAULT_LEASE_TTL = 30s`) | `PEXPIRE`d back to 30s on every 10s renewal tick (`DEFAULT_RENEW_INTERVAL`) | Community-scoped |
| Mesh session generation (fencing counter) | `buzz:{community_id}:tunnel:{session_id}:generation` | **None — non-expiring** | `INCR`ed only when a lease is newly acquired (no live lease found) | Community-scoped |

The per-IP rate-limit row is a definition, not a confirmed live path: a repository-wide
grep at the recorded revision found `check_ip_connection` only in its trait definition
and doc comment in `buzz-auth`, with no call site in `buzz-relay` or elsewhere — see
*Scope and omissions*.

## Lifecycle and consistency semantics

**Presence.** Expiry means "went offline without a clean disconnect" — a missed
heartbeat window, not necessarily a hard failure. The 180s TTL is deliberately 3x the
60s heartbeat interval specifically so *one* missed heartbeat cannot flap a still-online
user's presence to offline; only three consecutive misses do. A clean disconnect skips
the wait entirely via an explicit `DEL`.

**Rate-limit counters.** Expiry means the fixed window has closed and the quota fully
replenishes — this is a fixed-window algorithm, not sliding, so (per the module's own
doc comment) up to 2x the configured limit can pass at a window boundary. A crash
between the `INCR` and the `EXPIRE` that used to be two separate calls is now
structurally impossible (both run inside one Lua script); the code additionally treats
"key exists with a negative (no) TTL" as a detectable broken state from before that
atomicity fix and self-repairs it with a fresh `EXPIRE`, logging a warning rather than
leaving an immortal counter.

**NIP-98 replay marker.** Expiry is not a bug to guard against — it is the entire
point. The replay window only needs to outlive the NIP-98 verifier's own clock-skew
tolerance (±60s, doubled to a 120s floor); once a legitimate event's replay window has
closed, the same event id becoming claimable again is expected and harmless, since the
NIP-98 verifier itself will already reject a timestamp that old on its own timestamp-
window check. `SET NX EX` makes the claim atomic — no read-then-write race between two
concurrent requests for the same event id.

**Mesh session lease.** Expiry (an unrenewed lease) means the owning runtime has
stopped renewing — crashed, was rescheduled, or lost network — and the session becomes
available for another runtime to acquire via the same `ACQUIRE_SCRIPT` path. The
companion `*:generation` key never expires and is incremented only on a fresh
acquisition (no live lease found), so a stale frame carrying an old generation number
can be detected and rejected by any runtime even after the lease key itself has already
expired and been re-acquired by someone else — the generation counter is a fencing
token, not a duplicate of the lease's own liveness.

## Access-pattern summary and failure behavior

| Mechanism | Reader / writer | Redis error or missing-key handling |
|---|---|---|
| Presence | `buzz-relay`'s `handlers/event.rs` (status updates) and `connection.rs` (disconnect cleanup), via `buzz-pubsub::presence` | **Fail-open.** Both call sites discard the `Result` with `let _ = ...` — a Redis outage silently drops a presence update rather than blocking message handling or the WebSocket disconnect path. |
| Rate limit (per-principal, per-IP) | `buzz-relay`'s `admission.rs::check_principal`, called from `connection.rs` (WS) and `api/bridge.rs` (HTTP), via `buzz-pubsub::rate_limiter` | **Fail-closed.** A Redis error becomes `AdmissionError::Unavailable`; the WebSocket request is rejected with a "shared admission unavailable" message and the HTTP call returns `503 Service Unavailable`. Availability of the rate limiter is a precondition for admission, not an optional check. |
| NIP-98 replay marker | Callers of `buzz_auth::Nip98ReplayGuard::try_mark`, backed by `buzz-pubsub::RedisNip98ReplayGuard` | **Fail-closed**, explicitly: the trait's own doc comment states "on `Err` (Redis unreachable, etc.) callers MUST fail closed — reject the request rather than admitting it," and the Redis implementation's log line on error reads "caller MUST fail closed." |
| Mesh session lease | `crates/buzz-relay/src/tunnel/directory.rs`'s `SessionDirectory`, renewed by `tunnel/reliable.rs`'s lease-renewer task | **Fail-closed.** Every Redis error from `acquire`/`renew` propagates via `?` as a `DirectoryError` with no allow-on-error fallback, consistent with the module's own stated correctness law that "Redis is the arbiter for session ownership." A lease renewal that reports the lease as lost (owner/generation mismatch) is treated as no-longer-owning, not retried as still-owning. |

Presence is the one deliberately fail-open mechanism in this inventory: an online/away
status is a best-effort liveness signal, not a security or admission gate, so a dropped
update degrades UX (a stale presence dot) rather than availability or correctness. The
other four all gate either resource consumption (rate limits) or a security/ownership
invariant (replay protection, session-lease exclusivity), and all four choose to reject
work over risking a bypass when Redis cannot answer.

## Tenancy and security boundaries

**Community-scoped by default.** Presence, per-principal rate limits, the default
NIP-98 replay entry point, and the mesh session lease (plus its generation counter) all
prefix their Redis key with the resolved community id (`buzz:{community}:...`), so the
same pubkey or session id in two different communities never shares state — confirmed
directly for rate limits by `rate_limit_key_isolates_communities_for_same_pubkey`,
which `buzz-auth`'s own doc comment names the "S1 cross-community isolation fence."

**One deliberate exception.** The per-IP connection rate limit
(`buzz:ratelimit:ip:{ip}:conn`) is **operator-global**, not community-scoped, and the
trait doc comment explains why: IP-based admission happens at the network edge, before
host-to-community resolution has completed (or in place of it, on a resolution
failure) — threading a `TenantContext` through that check would invert the order of
operations. This is a documented design choice, not an oversight; the same doc comment
names the additive path (`LimitType` keyed on `(community, ip)`) a future per-tenant IP
fairness signal would need instead of retrofitting this one.

**No cross-tenant read path exists among these keys.** Every community-scoped key
namespace embeds the community id as a literal key segment rather than as a lookup
index, so there is no query shape that could return another community's presence,
rate-limit, replay, or lease state — isolation is structural to the key, not enforced
by a runtime check that could be skipped.

## Operational characteristics

**Self-repair (rate limiter).** A rate-limit key found with a value but no TTL (a
state that predates the current atomic Lua script, or a theoretical future bug) is
detected via a negative `TTL` reply and repaired with a fresh `EXPIRE`, with a warning
logged — the mechanism heals a broken key rather than leaving it immortal or erroring
out.

**Explicit clamping (NIP-98 replay).** `DEFAULT_REPLAY_TTL_SECS` (120s) and
`MAX_REPLAY_TTL_SECS` (3600s) are enforced as a floor and ceiling in the Redis
implementation itself, not merely documented as a convention callers are trusted to
follow — a caller-supplied value outside that range is silently clamped into it rather
than honored or rejected.

**A 3x heartbeat-to-TTL ratio recurs across two independently implemented
mechanisms.** Presence uses a 180s TTL against a 60s heartbeat; the mesh session lease
uses a 30s TTL against a 10s renewal interval. Both are the same ratio, and presence's
own doc comment states the reasoning explicitly ("TTL is 3x the ... heartbeat interval
so a single missed heartbeat does not cause ... flap") — the mesh lease code does not
restate that reasoning for its own choice, so this node treats the repetition as a real
convention two authors converged on independently rather than as a coincidence, without
asserting a written policy document requires it (none was found).

## Links (not copied)

Redis access code: `crates/buzz-pubsub/src/presence.rs`,
`crates/buzz-pubsub/src/rate_limiter.rs`, `crates/buzz-pubsub/src/nip98_replay.rs`,
`crates/buzz-relay/src/tunnel/directory.rs`,
`crates/buzz-relay/src/tunnel/reliable.rs`. Trait contracts (the caller-facing
MUST/MAY rules this node's failure-behavior table summarizes):
`crates/buzz-auth/src/rate_limit.rs`, `crates/buzz-auth/src/nip98_replay.rs`. Call
sites: `crates/buzz-relay/src/admission.rs`, `crates/buzz-relay/src/connection.rs`,
`crates/buzz-relay/src/handlers/event.rs`, `crates/buzz-relay/src/api/bridge.rs`. Tests
that pin the specific values and key shapes cited above:
`crates/buzz-pubsub/src/presence.rs`'s own `#[cfg(test)]` module (`PRESENCE_TTL_SECS`
== 180 == 3×60, and a live `TTL` check against a real Redis instance),
`crates/buzz-auth/src/rate_limit.rs`'s `rate_limit_key_includes_community_prefix` /
`rate_limit_key_isolates_communities_for_same_pubkey` / `ip_rate_limit_key_format`, and
`crates/buzz-relay/src/tunnel/directory.rs`'s
`key_shape_is_community_scoped_and_separates_counter`. This node does not inline any
Lua script or Rust function body — each is one open-file citation away in the evidence
ledger above.

## Scope and omissions

**This node covers** every Redis key in this repository that carries an explicit
`EX`/`PX`/`EXPIRE`/`PEXPIRE` expiry at the recorded revision, its duration and refresh
cadence, its consistency semantics at expiry, its tenancy scope, and what each
mechanism's callers do when Redis itself is unreachable.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's own existence, technology, connection profile, and non-TTL pub/sub channels | `architecture-containers-redis` |
| The local in-process moka cache's own unrelated 10s TTL in `cache_invalidation.rs` | Not a Redis key; not this node's or any corpus node's subject at the recorded revision |
| The `RateLimitConfig` tier design (the numeric limits themselves, as opposed to the mechanism enforcing whichever tier is configured) | `architecture-containers-redis`'s own scope-and-omissions section already excludes this as a `buzz-auth` concept, not a Redis one |
| Whether typing indicators have any Redis-backed mechanism at all | Unresolved by this node too — this node's own grep corroborates `architecture-containers-redis`'s existing flagged-but-unverified note (no Redis call site found for `KIND_TYPING_INDICATOR` anywhere in the workspace) without settling whether typing delivery exists elsewhere (e.g. `buzz-relay`-local, in-process only) |
| ElastiCache/production Redis operational tuning (eviction policy, maxmemory, failover) | `architecture-containers-redis`'s own scope-and-omissions section already excludes this; nothing in this repository documents it |

**Expected but not verified when this node was written:**

- **Whether `check_ip_connection` (the per-IP rate limiter) is wired into any live
  admission path.** A repository-wide grep found only its trait definition and doc
  comment; no call site was found in `crates/buzz-relay` or elsewhere. The per-IP row
  in the *Key namespace / TTL inventory* table above documents the mechanism as
  defined, not as confirmed-live.
- **Whether any environment currently runs a Redis version, `maxmemory-policy`, or
  persistence setting that could evict a not-yet-expired key early (e.g. under memory
  pressure with a non-`noeviction` policy).** Every TTL value and consistency claim in
  this node describes what the application code asks Redis to do, not what a specific
  deployed Redis instance's own eviction configuration guarantees it will honor before
  a key's TTL naturally elapses — that configuration is not visible from this
  repository, the same limit `architecture-containers-redis` already names for
  operational tuning generally.
- **No CI run has exercised this node**, and no cross-model review pass was run — both
  are deferred to this overnight batch's later bundling/review step, per this task's
  own dispatch instructions.
