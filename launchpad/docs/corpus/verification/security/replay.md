---
id: verification-security-replay
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The word 'replay' names at least three distinct mechanisms in this repository: (1) NIP-98 HTTP Auth event replay -- an attacker re-submitting a previously-valid signed event to obtain a second admission; (2) buzz-conformance's trace-replay checker, which replays a recorded JSONL execution trace through check_trace to verify it against the multi-tenant specification, a testing-methodology sense unrelated to an attack; (3) a Postgres trigger-level 'exact replay' guard for NIP-RS parameterized watermark events, which treats a byte-identical duplicate event as an idempotent no-op rather than an attack to reject."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-conformance/tests/replay_fixtures.rs"
      - "migrations/0010_nip_rs_exact_replay_guard.sql"
  - statement: "This node documents sense (1), NIP-98 HTTP Auth event replay, because this node's path is launchpad/docs/corpus/verification/security/ -- the parent directory names a security concern, and re-submission of a previously-valid signed credential to gain unauthorized re-admission is the security-attack-resistance meaning of 'replay', not the trace-replay testing methodology or the DB-level duplicate-event idempotency sense."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-conformance/tests/replay_fixtures.rs"
    confidence: 0.8
  - statement: "verify_nip98_event (buzz-auth's NIP-98 HTTP Auth verifier) checks signature, kind, a +/-60 second timestamp window, the `u` (URL) and `method` tags, and an optional body-hash `payload` tag, but its own module documents that it does NOT check whether the same event id has already been used -- that requires shared state external to the stateless verifier."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-auth/src/nip98_replay.rs:1-9"
  - statement: "buzz-auth/src/nip98_replay.rs defines the Nip98ReplayGuard trait as the required shape for NIP-98 replay protection: an atomic set-if-absent claim per event id, scoped per community, with a documented floor of DEFAULT_REPLAY_TTL_SECS = 120 seconds (matching the doubled +/-60s verifier tolerance) and a ceiling of MAX_REPLAY_TTL_SECS = 3600 seconds; the trait's doc comment states that callers MUST fail closed (reject) on any Err from try_mark."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:40-104"
  - statement: "RedisNip98ReplayGuard, in buzz-pubsub, is the production implementation of Nip98ReplayGuard: it issues a single Redis `SET key 1 NX EX <ttl>` per claim, returning Ok(true) only on the first claim (Redis reply `OK`) and Ok(false) on every subsequent claim of the same key within the TTL (Redis reply `nil`), which is what the caller must treat as a replay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs:1-99"
  - statement: "crates/buzz-relay/src/api/bridge.rs wires the guard into the live HTTP bridge auth path: check_nip98_replay / check_nip98_replay_with_guard is called after NIP-98 signature and host-binding verification succeed, maps Ok(false) from the guard to a 401 response whose body contains the string 'replay detected', and maps any Err from the guard to a 401 as well (fail-closed), rather than admitting the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:136-172"
  - statement: "The wire-level obligation -- a NIP-98 event posted twice to the same community over `POST /events` must be rejected on the second attempt, while the same event id posted to a different community is still admitted -- is asserted end to end by crates/buzz-test-client/tests/conformance_multitenant.rs::api_tokens_nip98_replay::nip98_replay_seenset_is_shared_and_community_scoped (line 729), which is marked #[ignore] and, per that file's own module doc-comment, requires RELAY_URL_A and RELAY_URL_B pointed at the same running multi-tenant relay process."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1-30"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:555-812"
  - statement: "The guard-level replay-rejection assertion (a second try_mark call for the same community and event id returns Ok(false) after the first returns Ok(true)) is asserted by crates/buzz-pubsub/src/nip98_replay.rs::tests::first_claim_succeeds_replay_fails (line 129) and by crates/buzz-relay/src/api/bridge.rs::tests::nip98_replay_guard_rejects_same_pod_same_community_replay (line 2731) and ::nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path (line 2702); all three are marked `#[ignore = \"requires Redis\"]` or `#[ignore]` and require a reachable Redis instance."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs:127-142"
      - "crates/buzz-relay/src/api/bridge.rs:2695-2757"
  - statement: "crates/buzz-relay/src/api/bridge.rs::tests::nip98_replay_check_fails_closed_when_guard_errors (line 2758) asserts the fail-closed path (a guard that always returns Err yields a 401, not an admitted request) using an in-process fake guard, and carries no #[ignore] attribute, so it does not require Redis."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2758-2790"
  - statement: "The unit tests inside crates/buzz-auth/src/nip98_replay.rs itself (key_includes_community_prefix, key_isolates_communities_for_same_event_id, key_components_are_lowercase, default_ttl_meets_gate_floor, ttl_floor_below_ceiling, max_ttl_fits_in_redis_signed_ex, always_fresh_returns_true) run unconditionally and are selected by `just test-unit`'s `cargo nextest run -p buzz-core -p buzz-auth --lib` step, but none of them exercises actual replay rejection against a real backing store: always_fresh_returns_true exercises AlwaysFreshReplayGuard, which is documented to always return Ok(true) and is explicitly for test code that does not exercise the replay path itself."
    entry_class: FACT
    evidence:
      - "Justfile:316-390"
      - "crates/buzz-auth/src/nip98_replay.rs:123-249"
  - statement: "At the recorded revision, none of `.github/workflows/ci.yml`, `Justfile`, or `scripts/run-tests.sh` contains any reference to `conformance_multitenant`, to the package name `buzz-pubsub`'s test targets, or to the three ignored bridge/pubsub replay tests named above, so no currently defined CI job or `just` recipe selects them (e.g. via `--ignored` / `--run-ignored`); the only `just` recipe that scopes tests to buzz-relay's `api::` modules (`admin-check`, and `test-unit`'s explicit selector) is restricted to `api::admin` and `router::tests`, which excludes `api::bridge::tests` entirely."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile:307-390"
      - "Justfile:511-517"
      - "scripts/run-tests.sh"
  - statement: "A second, related replay-resistance obligation exists for NIP-42 WebSocket AUTH and is NOT the subject of this node: crates/buzz-relay/src/connection.rs generates a fresh CSPRNG challenge per connection via generate_challenge() (line 167, calling buzz_auth::nip42::generate_challenge, a 32-byte random hex string per crates/buzz-auth/src/nip42.rs), verify_nip42_event rejects an AUTH event whose challenge tag does not exactly match the connection's own challenge, and crates/buzz-relay/src/handlers/auth.rs::handle_auth (lines 43-68) only accepts one AUTH transition per connection (a connection already Authenticated or Failed rejects any further AUTH message without re-verifying it) -- so a captured AUTH event replayed on a new connection is rejected by challenge mismatch, a property asserted at the unit level by crates/buzz-auth/src/nip42.rs::tests::wrong_challenge_rejected (line 120), rather than by a dedicated seen-set of the kind NIP-98 uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:167"
      - "crates/buzz-auth/src/nip42.rs:35-86"
      - "crates/buzz-relay/src/handlers/auth.rs:43-68"
      - "crates/buzz-auth/src/nip42.rs:119-128"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree contains no node under launchpad/docs/corpus/verification/ at all (this is the first node in that surface), and in particular no node with id verification-security-authentication or any other id resolving a NIP-42/NIP-98 authentication contract exists to declare a relationship toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no path under launchpad/docs/corpus/verification/ at this revision"
---

# Replay-attack resistance (NIP-98 HTTP Auth) -- test contract

## Purpose and boundary

This node documents one obligation: **a previously-valid, fully-verified NIP-98
HTTP Auth event (kind 27235) must not be honored a second time against the
same community.** It covers that obligation only.

Three unrelated things in this repository are also called "replay," and this
node deliberately does not cover any of them: `buzz-conformance`'s trace-replay
checker (replaying a recorded execution trace through `check_trace` to verify
it against the multi-tenant specification -- a testing-methodology term, not
an attack); the Postgres trigger-level "exact replay" guard for NIP-RS
parameterized watermark events (`migrations/0010_nip_rs_exact_replay_guard.sql`),
which treats a byte-identical duplicate event as an idempotent no-op rather
than something to reject; and NIP-42 WebSocket AUTH's own, structurally
different replay resistance, named as a second obligation in *Scope and
omissions* below rather than folded into this node. This node's location under
`launchpad/docs/corpus/verification/security/` is what selects the
attack-resistance sense of "replay" over the other two: a directory named
`security/` is naming a threat to defend against, and re-admission on a
previously-spent credential is the threat that phrase names in this codebase.

## Obligation

> A NIP-98 HTTP Auth event that has already been accepted once for a given
> community must be rejected -- with a 401 response naming replay -- on every
> subsequent presentation of the same event id to that same community, for at
> least `DEFAULT_REPLAY_TTL_SECS` (120) seconds after first acceptance; the
> same event id presented to a *different* community is unaffected.

## Verifying test(s)

- `crates/buzz-test-client/tests/conformance_multitenant.rs` --
  `api_tokens_nip98_replay::nip98_replay_seenset_is_shared_and_community_scoped`
  (line 729) -- the wire-level proof: two real HTTP `POST /events` requests
  carrying the same signed NIP-98 event to the same community, asserting the
  second is rejected 401 with "replay" in the body, plus a same-event-id,
  different-community request asserting it still succeeds.
- `crates/buzz-pubsub/src/nip98_replay.rs` -- `tests::first_claim_succeeds_replay_fails`
  (line 129) -- the guard-level proof, directly against a real Redis instance:
  `try_mark` returns `Ok(true)` on the first claim and `Ok(false)` on the
  second claim of the same `(community, event_id)` pair.
- `crates/buzz-relay/src/api/bridge.rs` --
  `tests::nip98_replay_guard_rejects_same_pod_same_community_replay` (line 2731)
  and `tests::nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path`
  (line 2702) -- the same guard-level proof exercised through
  `check_nip98_replay_with_guard`, the relay's own call site, including the
  cross-pod case (two independent `RedisNip98ReplayGuard` instances sharing
  one Redis pool, as two relay pods would).
- `crates/buzz-relay/src/api/bridge.rs` --
  `tests::nip98_replay_check_fails_closed_when_guard_errors` (line 2758) --
  covers the negative/error case: when the guard itself errors (e.g. Redis
  unreachable), the request MUST be rejected 401, never admitted. This is the
  fail-closed half of the obligation and is asserted with an in-process fake
  guard, not real Redis.

## How to run them

The wire-level test requires a running multi-tenant relay with two host
mappings on the same deployment:

```bash
RELAY_URL_A=http://a.localhost:3000 \
RELAY_URL_B=http://b.localhost:3000 \
cargo test -p buzz-test-client --test conformance_multitenant -- --ignored \
  api_tokens_nip98_replay::nip98_replay_seenset_is_shared_and_community_scoped
```

The guard-level tests require a reachable Redis (`REDIS_URL`, default
`redis://127.0.0.1:6379`):

```bash
cargo test -p buzz-pubsub --lib -- --ignored first_claim_succeeds_replay_fails
cargo test -p buzz-relay --lib -- --ignored \
  api::bridge::tests::nip98_replay_guard_rejects_same_pod_same_community_replay \
  api::bridge::tests::nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path
```

The fail-closed negative case needs no infrastructure and no `--ignored` flag:

```bash
cargo test -p buzz-relay --lib -- api::bridge::tests::nip98_replay_check_fails_closed_when_guard_errors
```

## Current enforcement status

**Gated.** All four tests above exist, are correctly shaped for the obligation
they name, and (per direct code reading) currently pass when run with their
required infrastructure -- but three of the four (all but the fail-closed
negative case) are `#[ignore]`d, requiring Redis and/or a live multi-tenant
relay, and **none of the four is currently selected by any CI job or `just`
recipe** at the recorded revision. `.github/workflows/ci.yml`, `Justfile` and
`scripts/run-tests.sh` were each read and grepped for `conformance_multitenant`,
for the package name `buzz-pubsub`, and for each ignored test's name; none
appears. The only `just` recipes that scope tests to `buzz-relay`'s `api::`
modules (`test-unit`'s explicit nextest selector, and `admin-check`) both
restrict to `api::admin` and `router::tests`, which excludes `api::bridge::tests`
by name. So the mechanism this obligation depends on -- a shared, atomic,
fail-closed, community-scoped seen-set wired into the live HTTP bridge auth
path -- is real, implemented, and unit-tested for its structural properties
(key format, TTL bounds, fail-closed error mapping, all of which run
unconditionally under `just test-unit`'s `cargo nextest run -p buzz-auth --lib`
step) -- but the specific behavioral claim this obligation makes, "a replayed
event id is actually rejected," is proven only by tests nothing in this
repository's automation currently runs. Calling this obligation "verified"
would overclaim; "gated" is the honest word, and the gap between "gated" and
"exercised in CI" is itself worth a reader's attention (see *Limits*).

## Limits

- **What is proven when the gated tests are run manually.** Within-community
  replay of an identical, already-admitted NIP-98 event over `POST /events`
  is rejected; the same event id in a different community is unaffected;
  two independent guard instances sharing one Redis pool (simulating two
  relay pods) agree on the same seen-set; a guard error is mapped to
  rejection, never admission.
- **What is not exercised by any of the four tests.** Replay against a route
  other than `/events` (`/query`, `/count`, or any other NIP-98-authenticated
  surface) is not separately tested; the obligation statement above and the
  wire-level test both use `/events` only, and per-route behaviour is
  inferred, not independently proven, to be identical (the guard is called
  from the same shared `check_nip98_replay` helper regardless of route,
  per `crates/buzz-relay/src/api/bridge.rs:136-142`, but no test posts a
  replay to a second route to confirm it).
- **TTL expiry is not tested.** No test waits out `DEFAULT_REPLAY_TTL_SECS`
  (120s) to confirm the seen-set entry actually expires and the same event id
  becomes replayable again after the window -- only that it is rejected
  within the window.
- **Clock skew / near-boundary timing is not tested against the replay guard.**
  The `+/-60s` timestamp tolerance in `verify_nip98_event` is unit-tested on
  its own (`crates/buzz-auth/src/nip98.rs::tests::expired_timestamp_rejected`),
  but no test combines a near-boundary timestamp with a replay attempt.
  Nothing in the code shows a value/TTL interaction that would risk this; it
  is simply an untested combination.
- **This node's evidence for "currently passes" is source reading, not an
  executed run.** The commit-recorded revision was read; the four tests were
  not executed against live Redis or a live multi-tenant relay while
  authoring this node. `#[ignore]`-vs-not and the absence from CI/`just`
  selectors are directly observable from the source and were confirmed by
  grep; whether the ignored tests currently pass when actually run was not
  independently re-verified here.

## Scope and omissions

**This node covers** NIP-98 HTTP Auth event replay resistance: the obligation,
its implementation seam (`Nip98ReplayGuard` in `buzz-auth`, `RedisNip98ReplayGuard`
in `buzz-pubsub`, the call site in `buzz-relay`'s HTTP bridge), its four
verifying tests, and their current enforcement status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Where it lives instead |
|---|---|
| NIP-42 WebSocket AUTH replay resistance -- structurally different (per-connection unpredictable challenge plus a single-AUTH-per-connection state machine, rather than a seen-set), verified today only indirectly via `crates/buzz-auth/src/nip42.rs::tests::wrong_challenge_rejected` and the timestamp-window test `expired_event_rejected` | A separate test-contract node, not yet written, is the right home; noted here per this task's own instruction rather than folded into this node or filed as a new issue |
| NIP-RS parameterized watermark events' "exact replay is a durable no-op" trigger-level idempotency (`migrations/0010_nip_rs_exact_replay_guard.sql`) -- a duplicate-suppression contract, not an attack-resistance one | Whatever corpus node eventually documents the NIP-RS watermark/read-state contract |
| `buzz-conformance`'s trace-replay checker (`crates/buzz-conformance/tests/replay_fixtures.rs`, `check_trace`) -- a different sense of "replay" (replaying a recorded trace against a specification to prove the checker itself works), unrelated to any attack surface | Whatever corpus node documents the multi-tenant conformance gate itself |
| NIP-98 replay resistance for any HTTP route other than `/events` | Named as an untested gap above, not established either way |
| Whether the corpus verification/security surface should eventually gain a `verification-security-authentication` node covering NIP-42/NIP-98 verification generally (kind, signature, timestamp checks) as distinct from replay specifically | Not decided here; this node cites only the replay-specific slice of each verifier |

**Relationships.** None declared. `git ls-tree -r --name-only origin/launchpad
-- launchpad/docs/corpus` was run at the recorded revision and returns no path
under `launchpad/docs/corpus/verification/` at all -- this is the first node
in that surface, so no `verification-security-authentication` id or any other
plausible neighbor exists yet to target. `relationships[].target` naming an id
no loaded node carries is a hard validation error per `node.schema.json`, so
none is declared rather than guessed at. The first sibling verification node
that lands is the moment to revisit this.

**Expected but not verified when this node was written:**

- Whether the three `#[ignore]`d tests actually pass today when run against
  real Redis and a real multi-tenant relay was not re-executed here; the
  claim rests on reading the assertions, not on a fresh run.
- Whether any not-yet-written CI job is planned to pick up `--ignored`
  selection for `conformance_multitenant.rs` or `buzz-pubsub`'s tests was not
  investigated; only their current absence from `.github/workflows/ci.yml`,
  `Justfile`, and `scripts/run-tests.sh` was established.
- Per-route replay behavior beyond `/events`, and TTL-expiry behavior, as
  named in *Limits* above.
