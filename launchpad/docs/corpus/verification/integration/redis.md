---
id: verification-integration-redis
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-pubsub's PubSubManager::publish_event routes to publisher::publish_event, which issues a Redis PUBLISH to a community- and topic-scoped channel name and returns the subscriber count; PubSubManager::retain_topic/release_topic maintain a local desired-subscription refcount keyed by EventTopicKey and ask a background subscriber task to SUBSCRIBE/UnsubscribeIfIdle only when that refcount transitions to/from zero."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:192-245"
      - "crates/buzz-pubsub/src/lib.rs:307-329"
      - "crates/buzz-pubsub/src/publisher.rs"
  - statement: "EventTopicKey::redis_channel formats a per-community, per-topic Redis pub/sub channel name as buzz:{community_id}:channel:{channel_id} for a specific channel or buzz:{community_id}:global for community-wide events; the topic key is a routing label, not an isolation boundary, per publish_event's own doc comment, which states the actual author-only delivery boundary is enforced downstream in the relay, not by Redis routing."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/topic.rs:42-50"
      - "crates/buzz-pubsub/src/lib.rs:307-321"
  - statement: "presence.rs implements online/away presence as SET buzz:{community}:presence:{pubkey_hex} <status> EX 180 (set_presence), GET (get_presence), MGET (get_presence_bulk) and DEL (clear_presence) against a shared deadpool_redis::Pool; PRESENCE_TTL_SECS is a constant 180 (3x the 60s client heartbeat interval, per its own doc comment)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:16-71"
  - statement: "test_publish_and_subscribe_roundtrip (crates/buzz-pubsub/src/lib.rs:399-435) is marked #[ignore = \"requires Redis\"] and asserts that a signed Nostr event published via PubSubManager::publish_event to a channel-scoped topic is received, with matching community_id/topic/event id, by a local broadcast subscriber obtained from PubSubManager::subscribe_local after PubSubManager::retain_topic and a live run_subscriber task."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:399-435"
  - statement: "same_channel_id_in_two_communities_release_one_keeps_other_live (crates/buzz-pubsub/src/lib.rs:510-590) is marked #[ignore = \"requires Redis\"] and asserts that when two different TenantContext communities both retain interest in a topic built from the identical channel UUID, releasing one community's interest (driving its local refcount to zero and, after the configured debounce, an UnsubscribeIfIdle command) does not stop event delivery to the other community's still-live subscription against the same underlying Redis channel name shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:510-590"
  - statement: "test_presence_set_and_get, test_presence_bulk and test_presence_ttl (crates/buzz-pubsub/src/presence.rs:162-234) are each marked #[ignore = \"requires Redis\"] and assert, respectively: get/set/get/clear/get round-trips correctly through Redis SET/GET/DEL; get_presence_bulk returns only the pubkeys that were actually SET, keyed by hex pubkey; and a live TTL queried via the Redis TTL command is greater than zero and at most PRESENCE_TTL_SECS immediately after set_presence."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:162-234"
  - statement: "test_util::make_test_pool (crates/buzz-pubsub/src/lib.rs:369-376), the only Redis pool constructor these five tests use, hardcodes the connection string \"redis://127.0.0.1:6379\" rather than reading a REDIS_URL environment variable, so the tests cannot be pointed at a different Redis instance without editing this source."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:369-376"
  - statement: "docker-compose.yml defines a redis service (image redis:7-alpine, container_name buzz-redis) bound to 127.0.0.1:6379 with a redis-cli ping healthcheck, matching the hardcoded address the five ignored tests connect to; the just _ensure-services recipe starts it (and Postgres) via docker compose up -d and polls both containers' health status before returning."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "Justfile:184-197"
  - statement: "ADR-0020 records that the adopted upstream testing methodology's integration tier is invoked via just test with Postgres and Redis started automatically, distinct from the infrastructure-free unit tier."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "None of scripts/run-tests.sh's run_unit_tests, run_integration_tests, or just test-unit's explicit per-crate cargo nextest run invocations name buzz-pubsub anywhere; run_integration_tests' final workspace step runs cargo test --test '*' (compiled integration-test binaries under each crate's own tests/ directory only), which does not reach an in-source #[cfg(test)] module such as buzz-pubsub's, and buzz-pubsub has no crates/buzz-pubsub/tests/ directory at all."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
      - "Justfile:312-386"
  - statement: "just test-unit's own comment on the buzz-backend-kubernetes step states its packages are 'enumerated explicitly because nothing in CI runs cargo test --workspace — workspace membership alone buys clippy/check, not a single executed test,' confirming that a crate not named in an explicit per-package selector anywhere in this repository's test tooling is not exercised by any automated lane, regardless of whether its own tests are #[ignore]d or not."
    entry_class: FACT
    evidence:
      - "Justfile:346-354"
  - statement: "No GitHub Actions workflow file under .github/workflows/ contains the string buzz-pubsub; ci.yml's only cargo nextest archive step builds and archives exclusively -p buzz-db -p buzz-relay -p buzz-test-client --lib plus the e2e_event_reminder integration binary, and every cargo nextest run / cargo test invocation later in that workflow selects tests from that same fixed package set or from buzz-test-client/buzz-dev-mcp/the desktop Tauri crate, never from buzz-pubsub."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('buzz-pubsub', path='.github/workflows', ref='473205a7457b208455f188847bfb27b01aa83cac') -> zero matches"
      - ".github/workflows/ci.yml:373-380"
  - statement: "Because no lane in scripts/run-tests.sh, the Justfile's test-unit/test/test-integration recipes, or any .github/workflows/*.yml file selects buzz-pubsub by package name, buzz-pubsub's own test suite -- both its #[ignore]d Redis-dependent tests and its non-ignored, infrastructure-free unit tests in the same files -- is not executed by any automated lane in this repository today; it runs only when a developer invokes cargo test -p buzz-pubsub (optionally with -- --ignored) by hand."
    entry_class: INFERENCE
    evidence:
      - "scripts/run-tests.sh"
      - "Justfile:312-386"
      - "grep_case_insensitive('buzz-pubsub', path='.github/workflows', ref='473205a7457b208455f188847bfb27b01aa83cac') -> zero matches"
    confidence: 0.8
  - statement: "The corpus's typing-indicator capability node (capabilities-presence-typing-indicator) records, from reading the same lib.rs this node cites, that buzz-pubsub's crate- and module-level doc comments claim Redis-backed typing-indicator tracking but no dedicated typing module exists in the crate -- confirmed independently here by lib.rs's own module list (cache_invalidation, conn_control, error, nip98_replay, presence, publisher, rate_limiter, subscriber, topic), which contains no typing module -- so typing indicators have no Redis-backed state and are out of this node's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs:1-40"
  - statement: "This session did not start a live Redis instance (Docker was not running and starting it requires interactive sudo unavailable in this environment) and therefore did not execute cargo test -p buzz-pubsub --lib -- --ignored against a real Redis; whether the five tests named above currently pass is not established by this node beyond their well-formed, non-todo!()-stubbed source and their absence from any CI failure history checked."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "this node's own authoring session, recorded as a limit rather than asserted as a FACT"
relationships:
  - type: references
    target: architecture-containers-redis
  - type: references
    target: capabilities-presence-typing-indicator
  - type: implements
    target: corpus-template-test-contract
---

# Redis integration tests (buzz-pubsub) — test contract

## Purpose and boundary

This node documents one obligation: that `buzz-pubsub`'s Redis-backed event
fan-out and presence-tracking behavior — the code paths that actually issue
Redis `PUBLISH`/`SUBSCRIBE`/`SET`/`GET`/`DEL` commands rather than exercising
pure in-process logic — are covered by a named set of integration tests that
run against a real Redis instance, and states honestly what those tests
currently prove and what nothing in this repository currently proves about
them. It covers only `buzz-pubsub`'s own Redis-dependent test suite; it does
not cover Redis as infrastructure generally, `buzz-pubsub`'s pure-logic unit
tests, or any other Redis-backed subsystem's tests (cache invalidation,
connection control, NIP-98 replay, or rate limiting) — see *Scope and
omissions*.

## Obligation

> `buzz-pubsub`'s Redis-backed integration tests, run against a live Redis
> instance, verify (a) that a Nostr event published via
> `PubSubManager::publish_event` to a community- and channel-scoped Redis
> topic is delivered to a local subscriber of that same topic, including
> that releasing one community's subscription interest in a channel UUID
> shared with a second community does not interrupt delivery to that second
> community's still-live subscription; and (b) that Redis-backed presence
> status set via `presence::set_presence` round-trips through
> `get_presence`/`get_presence_bulk` and is removed by `clear_presence`,
> with a bounded TTL enforced by Redis itself rather than by application code.

## Verifying test(s)

- `crates/buzz-pubsub/src/lib.rs` — `tests::test_publish_and_subscribe_roundtrip`
  (lines 399-435) — publish-then-receive roundtrip for a single community's
  channel-scoped topic.
- `crates/buzz-pubsub/src/lib.rs` —
  `tests::same_channel_id_in_two_communities_release_one_keeps_other_live`
  (lines 510-590) — the multi-tenancy-relevant case: two communities sharing
  one channel UUID, one releasing interest, the other's delivery must
  continue unaffected.
- `crates/buzz-pubsub/src/presence.rs` — `tests::test_presence_set_and_get`
  (lines 162-183) — set/get/set/get/clear/get status round-trip.
- `crates/buzz-pubsub/src/presence.rs` — `tests::test_presence_bulk`
  (lines 185-210) — `get_presence_bulk` returns only pubkeys actually set.
- `crates/buzz-pubsub/src/presence.rs` — `tests::test_presence_ttl`
  (lines 212-234) — a live Redis `TTL` query on the presence key is positive
  and at most `PRESENCE_TTL_SECS` (180) immediately after `set_presence`.

All five are marked `#[ignore = "requires Redis"]` in source.

## How to run it

A live Redis reachable at `redis://127.0.0.1:6379` is required — the test
pool constructor (`test_util::make_test_pool`, `lib.rs:369-376`) hardcodes
that address and is not configurable via `REDIS_URL` or any other
environment variable.

```bash
# Start Postgres + Redis (docker-compose.yml's `redis` service, container
# buzz-redis, redis:7-alpine on 127.0.0.1:6379):
just _ensure-services   # or: docker compose up -d

# Run only the Redis-dependent buzz-pubsub tests:
cargo test -p buzz-pubsub --lib -- --ignored

# Run buzz-pubsub's full test binary (ignored + non-ignored) explicitly:
cargo test -p buzz-pubsub --lib -- --include-ignored
```

`just test` (`scripts/run-tests.sh all`) does **not** run either of the
commands above — see *Current enforcement status*.

## Current enforcement status

**Gated, and not selected by any automated lane in this repository.**

The tests exist, are not stubbed or `todo!()`-panicking, and are correctly
marked `#[ignore = "requires Redis"]` — the standard Rust idiom for a test
that needs infrastructure the default `cargo test`/`cargo nextest run`
invocation does not provide. That much matches "gated" as this template
defines it: a real test exists, conditionally skipped, with the condition
named in source.

What is not honest to also claim is that CI (or any of this repository's own
test recipes) currently runs these tests in a gated/`--run-ignored` lane the
way several other `#[ignore]`d suites in this repository are: `buzz-db`,
`buzz-relay`, and `buzz-test-client` each have Postgres- or infrastructure-
gated tests that CI selects explicitly via `cargo nextest run -E '...'
--run-ignored ignored-only` in dedicated steps (see `.github/workflows/ci.yml`,
the "Backend Integration" job's per-suite steps). `buzz-pubsub` has no
equivalent step anywhere: it is absent from `scripts/run-tests.sh`'s unit and
integration functions, absent from `Justfile`'s `test-unit` recipe's explicit
per-package list, and absent — by name, checked with a case-insensitive
search — from every file under `.github/workflows/`. Its **non-ignored**
unit tests (e.g. `presence::tests::test_presence_key_format`,
`lib.rs::tests::retain_release_refcounts_and_debounces_last_release`) are
equally unexercised by any automated lane, not only the five Redis-gated
ones this node's obligation concerns.

So the accurate status is: **gated in source, but currently exercised by no
CI job and no top-level test recipe** — only by a developer invoking
`cargo test -p buzz-pubsub` directly. This node does not assert the five
tests currently pass; see *Limits*.

## Limits

- **This node did not execute the tests.** No live Redis was started during
  this node's authoring session (see the `TEAM_KNOWLEDGE` ledger entry
  above). The claim that the five tests currently pass against a real Redis
  is therefore not established here — only that they are real,
  non-stubbed, source-committed tests whose assertions this node has read
  and summarized correctly.
- **A green run of these five tests would not prove tenant isolation is
  airtight** — `same_channel_id_in_two_communities_release_one_keeps_other_live`
  is the only isolation-relevant case, and it exercises exactly one scenario
  (two communities, one shared channel UUID, one release). It does not
  exercise three-or-more communities, concurrent publishes racing a release,
  or Redis connection loss/reconnect mid-test (the reconnect-with-backoff
  logic `run_subscriber`'s own doc comment describes is not exercised by any
  test this node found).
- **The presence tests check TTL bounds, not TTL renewal semantics.**
  `test_presence_ttl` asserts a fresh TTL is in range immediately after
  `set_presence`; no test here exercises repeated `set_presence` calls
  (i.e., simulated heartbeats) refreshing that TTL over time, nor the
  "single missed heartbeat should not flap presence" property the 3x-margin
  constant is designed for.
- **The pub/sub topic key is explicitly documented as a routing label, not
  an authorization boundary** (`lib.rs:307-321`); this node's obligation is
  about delivery and isolation of Redis routing, not about the relay's
  separate `filter_fanout_by_access` authorization check downstream of it,
  which is out of scope here.
- **No negative/error case is part of this obligation.** All five verifying
  tests assert successful round-trips against a reachable Redis; none
  asserts behavior under a Redis outage or partial failure. A real
  connection-failure test exists in the same file
  (`presence::tests::get_presence_bulk_surfaces_connection_failure_as_error`,
  `presence.rs:112-130`) and is deliberately **not** one of this node's
  verifying tests — it points its pool at a closed port instead of at a live
  Redis instance and is not `#[ignore]`d, so it belongs to a different
  obligation (error propagation without infrastructure) than the one this
  node documents.

## Relationships

- `references: architecture-containers-redis` — the architecture node
  describing Redis as a directly-connected system and `buzz-pubsub`'s use of
  it (topic key format, presence key format, cache-invalidation channel);
  this node narrows that description to the specific claim that named tests
  verify a subset of it.
- `references: capabilities-presence-typing-indicator` — that node
  independently establishes, from the same source this node cites, that
  `buzz-pubsub` has no dedicated Redis-backed typing module despite its own
  doc comments; this node relies on that finding to justify excluding typing
  indicators from its obligation.
- `implements: corpus-template-test-contract` — this node is built from that
  template's required-sections shape.

## Scope and omissions

**This node covers** the obligation stated above and the five named tests
that verify it, how to run them, their actual (not aspirational) enforcement
status in this repository's test tooling and CI, and the specific scenarios
they do and do not exercise.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Cache-invalidation Redis roundtrip (`tests::test_cache_invalidation_roundtrip`, `lib.rs:437-473`, also `#[ignore = "requires Redis"]`) | a separate, not-yet-drafted test-contract node — a distinct obligation about cross-pod cache-key drops, not fan-out or presence |
| Connection-control (`conn_control.rs`), NIP-98 replay (`nip98_replay.rs`), and rate-limiting (`rate_limiter.rs`) Redis-backed behavior | separate, not-yet-drafted test-contract nodes; none of their tests are `#[ignore]`d on a Redis requirement at the recorded revision, but they are still Redis-dependent code this node does not characterize |
| Typing indicators | out of scope entirely — `buzz-pubsub` has no dedicated typing module despite its own doc comments' claim, per the FACT entry above and the corpus's `capabilities-presence-typing-indicator` node; typing indicators ride the relay's generic ephemeral-event fan-out, which this node's obligation touches only incidentally through the same Redis topic mechanism `test_publish_and_subscribe_roundtrip` exercises for ordinary events |
| Redis as deployed infrastructure — sizing, persistence, failover, the container/image itself | `architecture-containers-redis` |
| Whether this repository's CI *should* gate buzz-pubsub's Redis tests the way it gates buzz-db's and buzz-relay's | not decided here; this node reports the current gap rather than proposing a fix |
| `buzz-pubsub`'s non-ignored, infrastructure-free unit tests (topic-key formatting, config defaults, refcount arithmetic, etc.) | not this node's obligation, though the same CI-absence finding above applies to them too |

**Expected but not verified when this node was written:**

- **Whether the five named tests currently pass against a live Redis** — not
  run in this session; see *Limits*.
- **Whether `buzz-pubsub`'s absence from every test lane is deliberate or an
  oversight** — no issue, PR, or design document was found explaining it;
  it is reported here only as an observed gap in the code and CI
  configuration, the same posture the corpus's evidence standard requires
  when no source settles a claim beyond what was directly read.
- **Reconnect-after-disconnect behavior for the dedicated pub/sub connection**
  (`run_subscriber`'s exponential-backoff doc comment) — not exercised by
  any test found, ignored or not.
