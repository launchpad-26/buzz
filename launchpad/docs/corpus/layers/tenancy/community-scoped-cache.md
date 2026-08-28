---
id: layers-tenancy-community-scoped-cache
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`launchpad/docs/corpus/templates/concept.md` is the merged template this node follows: its required sections are a one-sentence definition that also states scope/boundaries, optional background, use cases, an optional comparison, and a scope-and-omissions close, and it explicitly prefers a typed `relationships` edge over a prose link whenever the target is itself a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
  - statement: "`CommunityId` is an opaque UUID newtype and `TenantContext` is the resolved tenant of an in-flight request; both live in `buzz-core` specifically so the DB, auth, pub/sub, search, audit, media, and relay-wiring layers name a community the same way. A `TenantContext` is documented as constructible only from a completed host resolution (`TenantContext::resolved`), never deserialized from client input, and every scoped cache or channel in this node is keyed from it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "Redis pub/sub channel names for ordinary event fan-out are community-scoped by construction: `EventTopicKey::redis_channel` builds `buzz:{community_id}:channel:{channel_id}` for a single channel and `buzz:{community_id}:global` for community-global events, and a test (`same_channel_in_two_communities_has_different_topics`) asserts the same channel id in two communities produces two distinct Redis keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "The pub/sub topic module states its own limits explicitly: Redis topics are a routing/performance boundary, not an authorization boundary — `TenantContext` still gates the publish/retain paths, and the relay re-checks access before local fan-out rather than trusting channel scoping alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
  - statement: "Presence is stored in Redis under a community-scoped key, `buzz:{community}:presence:{pubkey_hex}`, with a 180-second TTL (3x the 60s heartbeat interval), and a test (`same_pubkey_in_two_communities_has_different_presence_keys`) asserts the same pubkey in two communities produces two distinct presence keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "Pubkey-scoped Redis rate-limit keys are community-scoped (`buzz:{community}:ratelimit:{pubkey_hex}:{suffix}`), while IP-scoped rate-limit keys are deliberately left operator-global (`buzz:ratelimit:ip:{ip}:conn`) rather than per-community, per the doc comment on `RedisRateLimiter`."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "Two further Redis pub/sub channel families are community-scoped the same way: cache-invalidation messages on `buzz:{community}:cache-invalidate`, and connection-control commands (e.g. live-disconnecting a banned pubkey) on `buzz:{community}:conn-control`. Each relay pod subscribes with the wildcard patterns `buzz:*:cache-invalidate` / `buzz:*:conn-control` so one subscriber connection still receives every community's messages, with the community id recovered per-message by parsing the channel name."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "The connection-control channel is deliberately kept separate from cache-invalidation: a cache-key drop is documented as 'a pure, idempotent hint (the DB is re-read on the next access)', whereas a disconnect is 'an imperative, non-idempotent action on a live socket', and folding the two together would break cache-invalidation's own stated invariant of carrying only pure cache-key drops. This module's subject (a live-socket command, not a cache) is out of this node's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/conn_control.rs"
  - statement: "`buzz-relay`'s `AppState` holds several process-local, in-memory `moka` caches keyed by tuples that include `CommunityId` as their first element: `local_event_ids: (CommunityId, [u8; 32])`, `membership_cache: (CommunityId, Uuid, Vec<u8>)`, `accessible_channels_cache: (CommunityId, Vec<u8>)`, `channel_visibility_cache: (CommunityId, Uuid)`, `observer_owner_cache: (CommunityId, Vec<u8>, Vec<u8>)`, and `author_type_cache: (CommunityId, Vec<u8>)`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "The doc comment on `local_event_ids` states the reason `CommunityId` is part of that key explicitly: the same Nostr event id can legitimately exist in two different communities, so keying on the bare event id would let a local publish in community A suppress delivery of a distinct same-id event arriving via Redis for community B — named in the comment as 'a cross-community non-interference violation'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "`AppState::invalidate_membership` (and the sibling `invalidate_all_accessible_channels`, `invalidate_channel_visibility`, `invalidate_channel_deleted`) each drop the local moka entry immediately, then spawn a fire-and-forget publish of the same drop to `buzz:{community}:cache-invalidate` so every other pod converges without waiting out the cache's own TTL; a pod that receives such a message calls `apply_cache_invalidation`, which dispatches to the same `*_local` drop functions so a received drop is never re-published."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "Community-scoped invalidation of a keyed-by-tuple cache uses moka's `invalidate_entries_if` predicate (matching only the `community_id` field of the key) rather than a full clear. If the predicate call itself fails, the code logs an error and falls back to `invalidate_all()` (dropping every community's entries) rather than silently leaving stale entries, with an inline comment stating the preference to 'over-invalidate' over serving stale access state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "`buzz-core::tenant`'s own module doc names the invariant every mechanism in this node ultimately rests on: a request's community is resolved from the connection host by the server, never supplied or influenced by the client, and it states plainly that this is 'a lint-and-review fence, not a compiler fence' — `TenantContext::resolved` and `CommunityId::from_uuid` are `pub` so host resolution can call them, so the guarantee depends on review/lint discipline outside this module, not on the type system alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "Taken together, the Redis-side key-namespacing (topic, presence, rate-limit, cache-invalidation, conn-control channels) and the process-local moka caches keyed on `CommunityId` implement one property: no relay pod's cached state for community A can be read, invalidated, or refreshed by an operation scoped to community B, because every key that reaches Redis or a local cache carries the resolved `CommunityId` and every invalidation path (`*_local` fn, predicate, and Redis-broadcast) is threaded through the same identifier. This is a synthesis across the FACT entries above rather than one file's single stated claim, so it is classified INFERENCE."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/topic.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-relay/src/state.rs"
    confidence: 0.85
  - statement: "The desktop app's `resetCommunityState()` (invoked on community switching) is a real, separate mechanism in the codebase: it resets client-side, module-level singletons that survive React's key-based remount when a user switches between communities in one running desktop process. It is not the same mechanism as this node's subject — the relay's server-side Redis/moka caches — and this node does not describe it further."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: "Confusing the relay's server-side community-scoped caching with the desktop's client-side `resetCommunityState()` singleton reset is a named risk for this specific document: the repository's own root `CLAUDE.md` states the desktop mechanism explicitly and separately from relay-side concerns, which is why this node states the boundary as its own non-goal rather than leaving it implicit."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1185 task brief, relayed via the corpus-plan dispatch for this task"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-deployment-multi-community
---

# Community-scoped cache

A **community-scoped cache** is any Redis key, Redis pub/sub channel, or process-local
in-memory cache entry in the Buzz relay whose key includes the resolved `CommunityId` of
the request or event it belongs to, so that two communities never read, invalidate, or
overwrite each other's cached state even though they share the same relay process, the
same Redis instance, and — for values like channel ids or Nostr event ids — sometimes the
same literal identifier.

## Why this exists

Buzz is multi-tenant: one relay deployment, one Redis instance, and one Postgres database
can serve many communities at once, distinguished only by the `Host` header a connection
resolves against (`architecture-principles-host-selects-community`). Every durable
per-community boundary the corpus already documents is a database-level concern — rows
scoped by a `community_id` column. Caching introduces a second, faster-changing surface
that the database boundary alone does not cover: a Redis key, a Redis pub/sub channel, or
a value held in a relay process's own memory. If any of those were keyed without the
community, a value read, invalidated, or published for one community could leak into or
suppress delivery for another — the same failure mode
`architecture-principles-community-is-security-boundary` names for the request path, but
applied to a cache entry instead of a request.

## The two mechanisms

**Redis-side key namespacing.** Every Redis key or pub/sub channel this node covers is
built from `buzz:{community_id}:...`: event topics (`channel:{channel_id}` /
`global`), presence (`presence:{pubkey_hex}`), pubkey-scoped rate limits
(`ratelimit:{pubkey_hex}:{suffix}`), cache-invalidation broadcasts
(`cache-invalidate`), and connection-control commands (`conn-control`). A subscriber that
needs every community's messages on one connection uses a wildcard pattern
(`buzz:*:cache-invalidate`, `buzz:*:conn-control`) and recovers the specific community id
per-message by parsing the channel name back apart. IP-scoped rate limits are the one
deliberate exception: they stay operator-global (`buzz:ratelimit:ip:{ip}:conn`), because
an IP is not itself a tenant-scoped identity.

**Process-local moka caches, invalidated cross-pod over Redis.** `buzz-relay`'s
`AppState` also holds several short-TTL, in-memory `moka` caches — membership,
accessible-channel-ids, channel-visibility, local-event-id dedup, observer-owner, and
author-type — each keyed by a tuple whose first element is `CommunityId`. These caches
exist because they sit on a hot path (e.g. per-event membership checks) where a Postgres
round-trip on every access would be wasteful; the short TTL (10 seconds for most of them)
already bounds staleness, but a write on one relay pod must not leave every *other* pod
serving a stale entry for up to that TTL. The relay solves this by dropping its own local
entry immediately, then publishing the same drop as a `CacheInvalidation` message on that
community's `cache-invalidate` channel; every pod's subscriber receives it and applies the
identical local-only drop function, so a change converges across the whole pod fleet
without ever exposing the invalidation as a cross-community signal — a predicate
invalidation (`invalidate_entries_if`) matches only entries for the affected
`community_id`, falling back to a full clear (logged as an error) only if the predicate
call itself is unavailable.

## Boundaries and non-goals

**This node is not about database-row tenancy.** Postgres-level `community_id` column
scoping, and how a connection's community is resolved from its `Host` header in the first
place, are `architecture-principles-community-is-security-boundary` and
`architecture-principles-host-selects-community`'s subjects, not this one's. This node
covers only the caching layer built on top of that already-resolved identity.

**This node is not about Redis or deployment topology in general.** `Redis` as a
container/dependency is `architecture-containers-redis`'s subject; how multiple
communities are provisioned and routed across relay pods and Redis at the deployment
level is `architecture-deployment-multi-community`'s subject. This node covers the
specific caching and invalidation mechanisms those deployments run, not the topology
itself.

**This node does not cover connection-control.** `conn-control` messages share the same
Redis pub/sub transport shape as cache-invalidation and are community-scoped the same
way, but they carry an imperative "disconnect this socket" command, not a cache-key drop
— the code's own module doc is explicit that folding the two together would break
cache-invalidation's stated invariant of being a pure, idempotent hint. It is named here
only to mark the boundary, not described further.

**This node does not cover the desktop app's `resetCommunityState()`.** The desktop app
resets client-side, module-level singletons on community switch so stale data from a
previous community doesn't leak into the newly selected one after a React remount. That
is a real mechanism, but it runs in a different process, on a different tier (client, not
server), for a different reason (surviving a React remount, not bounding cache staleness
across a pod fleet). A reader looking for that mechanism should look at
`desktop/src/features/communities/useCommunityInit.ts` directly; this node does not
attempt to unify the two under one concept, because doing so would fold two independently
maintainable ideas into one document.

**This node does not cover buzz-search's or buzz-audit's own caching, if any.** Evidence
for this node was gathered from `buzz-pubsub` and `buzz-relay` (specifically `AppState`);
whether `buzz-search` or `buzz-audit` maintain their own community-scoped caches was not
investigated and is not claimed here either way.

## Scope and omissions

**This document covers** the Redis-side key-namespacing convention and the process-local
moka-cache-plus-cross-pod-invalidation mechanism the Buzz relay uses to keep per-community
cached state from leaking across communities, and states the boundary against the
sibling concerns (database tenancy, deployment topology, connection-control, and the
desktop's unrelated client-side singleton reset) a reader might otherwise conflate this
with.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Database-row `community_id` scoping | `architecture-principles-community-is-security-boundary` |
| How a connection resolves to a community from its `Host` header | `architecture-principles-host-selects-community` |
| Redis as a deployed container/dependency | `architecture-containers-redis` |
| Multi-community deployment topology | `architecture-deployment-multi-community` |
| Connection-control (live disconnect/ban enforcement) | Not yet a corpus node at this revision |
| The desktop client's `resetCommunityState()` singleton reset | Not yet a corpus node at this revision; see `desktop/src/features/communities/useCommunityInit.ts` directly |

**Expected but not verified when this node was written:** whether `buzz-search` or
`buzz-audit` hold any community-scoped cache of their own was not investigated. Whether
the formal conformance model (`docs/spec/MultiTenantRelay.tla`, referenced from
`buzz-core::tenant`'s module doc) states any property specific to cache entries, as
opposed to requests, was not checked — this node's claims are drawn from the Rust source
and its own doc comments and tests, not from the TLA+ model.
