---
id: verification-formal-multi-tenant-auth
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
  - statement: "docs/multi-tenant-conformance.md's 'Row zero' section states that the URL host is the authoritative community selector, that unknown or unmapped hosts fail closed with a generic rejection and never fall through to a default tenant, that NIP-98/API-token/community stamps may narrow or authenticate authority but never override the host-derived community (a disagreeing stamp is rejected), and that a client-supplied `h` tag is adversarial input that must resolve to a channel inside req.community."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:12-36"
  - statement: "docs/multi-tenant-conformance.md's conformance-table row 'API tokens and NIP-98 replay' states that token hash uniqueness/lookup must be scoped to (community_id, token_hash), that channel claims on a token must reference channels in the same community, that the NIP-98 replay seen-set key must be (community_id, event_id) in shared storage, and that the NIP-98 `u` URL host must match req.community."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:44"
  - statement: "docs/multi-tenant-conformance.md's conformance-table row 'Relay membership, pubkey allowlist, archived identities' states that relay_members, pubkey_allowlist and archived_identities must gain community_id with primary/unique keys and indexes of (community_id, pubkey), that membership errors must stay generic, and that identity-archive requests must not be able to hide/archive a key in another community."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:45"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's own file-level doc comment describes itself as the executable form of the conformance contract, mirroring docs/multi-tenant-conformance.md one module per row; states that the A/B cross-community isolation tests require a live two-host relay and are `#[ignore]` by default, selected with `--ignored` and the `RELAY_URL_A`/`RELAY_URL_B` environment variables; and states that a row not yet backed by a landed lane is `todo!()`-stubbed via the file's own `pending_lane` helper so a green run can never be faked by an empty test body."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1-38"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:63-69"
  - statement: "conformance_multitenant.rs's `row_zero_host_binding::unmapped_host_fails_closed_generically` is a `#[tokio::test]` marked `#[ignore]` that asserts three wire-observable properties against a live two-host relay: an unmapped host returns 404 while a mapped host does not on the same non-`nostr+json` door; the unmapped-host rejection body echoes neither the host authority nor the host label; and a raw WebSocket handshake to the unmapped host is rejected at the upgrade rather than accepted and bound to a default tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:114-191"
  - statement: "conformance_multitenant.rs's `row_zero_host_binding::client_supplied_community_cannot_override_host` is a `#[tokio::test]` marked `#[ignore]` that creates an open channel that exists only in community B, confirms it is genuinely postable in B as a positive control, then asserts that a kind:9 event `#h`-tagging that channel and posted via community A's connection is rejected, that the rejection carries the exact `IngestError::Rejected` reason string \"restricted: not a channel member\" (ruling out an earlier incidental gate), and that the rejection body does not echo the B-only channel UUID."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:257-338"
  - statement: "crates/buzz-relay/src/tenant.rs's `bind_community` normalizes the raw host, fails closed on an empty/whitespace host before any resolver lookup, and on an unmapped host or a resolver error returns a `BindError` rather than a default `TenantContext`; its own doc comment states 'There is deliberately no path that yields a default or fallback community.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:61-92"
  - statement: "crates/buzz-relay/src/router.rs's `nip11_or_ws_handler` calls `bind_community` before the WebSocket upgrade is attempted, and on any bind error returns HTTP 404 with the fixed body string \"relay: no community is configured for this host\" -- the same string regardless of whether the host is unmapped or the lookup errored, and never the raw host itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:336-355"
  - statement: "crates/buzz-relay/src/tenant.rs carries a non-`#[ignore]`, infra-free unit-test suite for the same fail-closed property asserted on the wire by row zero: `tests::unmapped_host_fails_closed`, `tests::lookup_error_fails_closed_not_default_tenant`, and `tests::redteam_attack2::empty_raw_host_fails_closed_even_if_db_has_empty_host_row`, `::whitespace_only_raw_host_fails_closed_even_if_db_has_empty_host_row` and `::non_empty_unmapped_host_still_fails_closed_after_fix`, none of which carry an `#[ignore]` attribute at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:244-251"
      - "crates/buzz-relay/src/tenant.rs:260-334"
  - statement: "Justfile's `test-unit` recipe comment states explicitly, of its own `cargo nextest run -p buzz-relay --lib` invocation, that it is scoped to `test(/^api::admin::/)` only and that 'just test-unit did not enumerate buzz-relay --lib' as a whole; scripts/run-tests.sh, the script `just test` runs, contains no invocation of the `buzz-relay` package at all; and no `.github/workflows/*.yml` job in this repository invokes `tenant::tests` or an unscoped `buzz-relay --lib` run either -- so the tenant.rs unit-test suite cited above is not executed by any test command this repository runs."
    entry_class: FACT
    evidence:
      - "Justfile:360-385"
      - "run_command('grep -n \"buzz-relay\" scripts/run-tests.sh') -> no output (no match)"
      - "run_command('grep -rn \"conformance_multitenant|RELAY_URL_A|-- --ignored\" .github/workflows/') -> matches only unrelated buzz-test-client e2e_persona/e2e_media/e2e_relay --ignored invocations, none naming conformance_multitenant, tenant::tests, or an unscoped buzz-relay --lib run"
  - statement: "conformance_multitenant.rs's `api_tokens_nip98_replay::token_minted_in_a_does_not_authorize_in_b` is a plain `#[test]` (not `#[ignore]`) whose entire body is a comment stating it is a 'compile-time anchor' with no assertions, because -- per the same module's doc comment -- buzz-relay exposes no HTTP route to mint an API token, so the 'mint in A, present to B' precondition this row's obligation describes has no wire entry point to test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:564-642"
  - statement: "At this revision, no route registered in `crates/buzz-relay/src/router.rs`'s `build_router` names a token-minting path, and neither `Db::get_api_token_by_hash_including_revoked` nor `Db::get_api_token_by_hash` (defined in crates/buzz-db/src/store/api_token.rs) is called from any non-test source file in this workspace; the sole production reference to api_tokens in crates/buzz-relay is a comment in crates/buzz-relay/src/api/media.rs stating that Blossom upload authority is 'independent of bearer-token / api_tokens storage.'"
    entry_class: FACT
    evidence:
      - "run_command('grep -rn \"\\\"/token\\|/tokens\\\"\\|mint.*token\\|create_api_token\" crates/buzz-relay/src/') -> no output (no match)"
      - "run_command('grep -rln \"get_api_token_by_hash_including_revoked\\b\" --include=\"*.rs\" crates/') -> crates/buzz-test-client/tests/conformance_multitenant.rs (doc comment only), crates/buzz-db/src/store/api_token.rs (definition and its own tests) -- no caller in crates/buzz-relay"
      - "run_command('grep -rln \"get_api_token_by_hash\\b\" --include=\"*.rs\" crates/') -> crates/buzz-test-client/tests/conformance_multitenant.rs (doc comment only), crates/buzz-db/src/store/api_token.rs (definition and its own tests) -- no caller in crates/buzz-relay"
      - "crates/buzz-relay/src/api/media.rs:204-210"
  - statement: "crates/buzz-db/src/store/api_token.rs's `lookup_by_hash_is_scoped_to_community` (`#[tokio::test]`, `#[ignore = \"requires Postgres\"]`) inserts an identical 32-byte token hash into two communities and asserts a lookup scoped to each community returns only that community's row, and returns None for a third, unrelated community; `active_lookup_by_hash_is_scoped_to_community` mirrors the same property for the non-revoked lookup variant. Both connect to a hardcoded `TEST_DB_URL` of `postgres://buzz:buzz_dev@localhost:5432/buzz`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/api_token.rs:628-762"
      - "crates/buzz-db/src/store/api_token.rs:767-802"
  - statement: "scripts/run-tests.sh's own comment states that the Postgres-backed buzz-db tests are `#[ignore]`d and that 'nothing here (or in integration mode below, which runs `cargo test -p buzz-db` without --ignored) runs them' -- i.e. neither this repository's unit test mode nor its integration test mode executes `lookup_by_hash_is_scoped_to_community` or `active_lookup_by_hash_is_scoped_to_community`."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:93-100"
      - "scripts/run-tests.sh:125-133"
  - statement: "crates/buzz-auth/src/nip98_replay.rs's `tests::key_isolates_communities_for_same_event_id` is a plain `#[test]` (no `#[ignore]`, no I/O) that builds the seen-set key via `nip98_replay_key` for the same event id under two distinct `TenantContext`s and asserts the two keys differ; its own comment names the property 'belt-and-suspenders' for an artificial same-event-id collision across communities."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:178-192"
  - statement: "Justfile's `test-unit` recipe runs `cargo nextest run -p buzz-core -p buzz-auth --lib` unconditionally (no infra guard), which by package/target scope includes crates/buzz-auth/src/nip98_replay.rs's `tests` module; this is the same recipe `just ci` composes into its own dependency list."
    entry_class: FACT
    evidence:
      - "Justfile:312-321"
  - statement: "conformance_multitenant.rs's `api_tokens_nip98_replay::nip98_replay_seenset_is_shared_and_community_scoped` is a `#[tokio::test]` marked `#[ignore]` that, against a live two-host relay, posts a NIP-98-authenticated event to community A twice and asserts the second POST is rejected with HTTP 401 and a body naming \"replay\", then posts an independent NIP-98 event to community B and asserts it succeeds even though a nonce was already spent in A."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:727-851"
  - statement: "conformance_multitenant.rs's `membership_allowlist::archive_in_a_does_not_affect_b` is a `#[tokio::test]` marked `#[ignore]` whose entire body is the single call `pending_lane(\"buzz-auth\", \"archived_identities (community_id, pubkey) -- A's archive invisible to B\")`, which the file's `pending_lane` helper implements as an unconditional `todo!()` panic naming the obligation; no assertion logic for this obligation exists in this file at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:899-912"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:63-69"
  - statement: "crates/buzz-relay/src/api/mod.rs's `enforce_relay_membership` takes a `CommunityId` parameter and is the function crates/buzz-relay/src/api/media.rs calls to gate Blossom uploads by relay membership, confirming that production membership-check call sites already thread a community identifier through -- distinct from, and not itself proof of, the community-scoping of `archived_identities`/`pubkey_allowlist` that the pending obligation above names."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:126-147"
      - "crates/buzz-relay/src/api/media.rs:211-219"
  - statement: "This node did not execute any Rust test in the environment it was authored in -- no `cargo` toolchain was available (`cargo --version` failed after activating this repository's own Hermit environment) -- so every enforcement-status claim above rests on reading each test's current source (its `#[ignore]`/`todo!()` state and whether a test-running script or CI workflow enumerates it), which AGENTS.md names as acceptable executable evidence for enforcement status, not on a personally observed pass/fail result."
    entry_class: FACT
    evidence:
      - "run_command('cargo --version') -> command not found, exit 127, after sourcing ./bin/activate-hermit"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Because none of the wire-level A/B isolation tests (row zero's two tests, the NIP-98 replay wire test) or the buzz-db storage-layer token tests is invoked by any script or CI workflow this node's author found in this repository, each of those obligation facets is presently 'gated' rather than 'verified' under this template's three-way classification -- the tests exist and are constructed to prove the property, but no automated process in this repository has been shown to run them, so their current pass/fail state is unconfirmed by anything but a manual, out-of-band invocation."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:114-191"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:257-338"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:727-851"
      - "crates/buzz-db/src/store/api_token.rs:628-802"
      - "scripts/run-tests.sh:93-133"
      - "Justfile:360-385"
    confidence: 0.6
  - statement: "The API-token community-scoping obligation's only living enforcement at this revision is the gated storage-layer test, because the production consumer path conformance_multitenant.rs's own doc comment describes (media.rs looking up a token by community-scoped hash) has been removed from the code the relay currently ships -- media.rs's own comment states upload authority is independent of api_tokens, and no other production call site of either lookup function exists in this workspace."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/media.rs:204-210"
      - "run_command('grep -rln \"get_api_token_by_hash\" --include=\"*.rs\" crates/') -> no non-test caller in crates/buzz-relay"
    confidence: 0.8
  - statement: "Issue #1370's definition of done requires this node to state preconditions/context, action/event and observable expected outcome; to name negative/error cases when they are part of the contract; to link the actual automated/formal/manual verification implementing the contract; and to not claim coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1370 definition of done"
  - statement: "Issue #1371, the sibling task under the same parent PRD #617, is titled 'task: document verification/formal/multi-tenant-relay.md' with the objective of creating that file as 'the single canonical test contract node for multi tenant relay' -- a separate, general-relay-conformance scope from this node's authentication/authorization-specific scope, which is why this node defers the remaining docs/multi-tenant-conformance.md rows (NIP-11, users/profiles, channel-less events, channels-as-data-isolation, workflows, search, pub/sub, media, git, mesh/agents/CLI, audit) to #1371 rather than covering them here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1371 title and objective, compared against #1370's own objective"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: implements
    target: corpus-template-test-contract
---

# Multi-tenant authentication and authorization -- test contract

## Purpose and boundary

`docs/multi-tenant-conformance.md` lists many conformance obligations for
multi-tenant Buzz, most of which are about scoping *data* (channels, search
results, workflow runs, media, audit rows) to a `community_id`. This node
covers only the subset of that table that is specifically about
**authentication and authorization**: who or what is allowed to act, and
under which community's authority, before any data-scoping question is even
reached. Precisely, this node covers three named rows of that table --
**"Row zero: request community binding"**, **"API tokens and NIP-98
replay"**, and **"Relay membership, pubkey allowlist, archived
identities"** -- and the tests in this repository that verify (or attempt
to verify) each of them.

**This node does not cover** the remaining rows of that table (NIP-11 relay
info, users/profiles/NIP-05, channel-less global events and DMs, channels
and channel membership as a *data*-isolation surface, workflows, search/FTS,
Redis pub/sub and presence, media/Blossom, git hosting, mesh/agents/CLI, and
the audit log) or the general N=1/A-B parity harness those rows share. That
broader relay-conformance surface belongs to the sibling task, issue #1371,
which targets `launchpad/docs/corpus/verification/formal/multi-tenant-relay.md`.
It also does not cover NIP-42 WebSocket AUTH's own challenge-response
protocol (see `architecture-flows-websocket-authentication`), except insofar
as WebSocket connections share the host-derived-community-binding
precondition row zero asserts.

## Obligation

> In multi-tenant Buzz, every authentication and authorization decision on
> the relay's externally reachable surface -- host-derived community
> binding, NIP-98/API-token identity verification and replay rejection, and
> relay-membership/pubkey-allowlist/archived-identity gating -- is scoped by
> `community_id`, such that: **(a)** a request against an unmapped host is
> rejected generically rather than falling through to a default tenant;
> **(b)** a client-supplied community-ish claim (an `#h` channel tag, an API
> token, or a NIP-98 `u`-host) may narrow or authenticate *within* the
> host-derived community but can never override it; and **(c)** a
> credential, replay-seen-set entry, membership grant, or archived-identity
> record established in one community is never honored, spent, or
> observable when the same request is made against a different community on
> the same relay deployment.

## Verifying test(s)

| Facet | Test | Location |
|---|---|---|
| (a) unmapped host fails closed, wire-level | `row_zero_host_binding::unmapped_host_fails_closed_generically` | `crates/buzz-test-client/tests/conformance_multitenant.rs:114-191` |
| (a) same property, unit-level | `tests::unmapped_host_fails_closed`, `tests::lookup_error_fails_closed_not_default_tenant`, `tests::redteam_attack2::{empty_raw_host_fails_closed_even_if_db_has_empty_host_row, whitespace_only_raw_host_fails_closed_even_if_db_has_empty_host_row, non_empty_unmapped_host_still_fails_closed_after_fix}` | `crates/buzz-relay/src/tenant.rs:244-334` |
| (b) `#h` claim cannot override host | `row_zero_host_binding::client_supplied_community_cannot_override_host` | `crates/buzz-test-client/tests/conformance_multitenant.rs:257-338` |
| (c) API tokens, wire-level anchor only | `api_tokens_nip98_replay::token_minted_in_a_does_not_authorize_in_b` | `crates/buzz-test-client/tests/conformance_multitenant.rs:564-642` |
| (c) API tokens, storage-level | `store::api_token::tests::{lookup_by_hash_is_scoped_to_community, active_lookup_by_hash_is_scoped_to_community}` | `crates/buzz-db/src/store/api_token.rs:704-802` |
| (c) NIP-98 replay, unit-level (key shape) | `tests::key_isolates_communities_for_same_event_id` | `crates/buzz-auth/src/nip98_replay.rs:178-192` |
| (c) NIP-98 replay, wire-level (live seen-set) | `api_tokens_nip98_replay::nip98_replay_seenset_is_shared_and_community_scoped` | `crates/buzz-test-client/tests/conformance_multitenant.rs:727-851` |
| (c) membership/allowlist/archived-identity | `membership_allowlist::archive_in_a_does_not_affect_b` | `crates/buzz-test-client/tests/conformance_multitenant.rs:899-912` |

## How to run it

**Wire-level A/B isolation suite** (row zero's two tests, the NIP-98 replay
wire test, and the membership-allowlist stub) requires a running
multi-tenant relay bound to two hosts against the same Postgres/Redis
backing, addressed by `Host` header alone:

```bash
RELAY_URL_A=http://a.localhost:3000 \
RELAY_URL_B=http://b.localhost:3000 \
RELAY_URL_UNKNOWN=http://unknown.localhost:3000 \
cargo test -p buzz-test-client --test conformance_multitenant -- --ignored
```

Running the full `--ignored` set will panic on
`membership_allowlist::archive_in_a_does_not_affect_b` via its
`pending_lane` stub -- that panic is load-bearing (it names the missing
lane), not a bug in the invocation; exclude it by name if only the
implemented rows are wanted.

**API-token wire-level anchor** (no infra, asserts nothing):

```bash
cargo test -p buzz-test-client --test conformance_multitenant token_minted_in_a_does_not_authorize_in_b
```

**API-token storage-level scoping** requires a local Postgres reachable at
the module's hardcoded `TEST_DB_URL`, `postgres://buzz:buzz_dev@localhost:5432/buzz`,
with the `communities`/`users`/`api_tokens` tables migrated:

```bash
cargo test -p buzz-db --lib -- --ignored lookup_by_hash_is_scoped_to_community active_lookup_by_hash_is_scoped_to_community
```

**Row-zero unit-level suite** (infra-free, not `#[ignore]`d, but not wired
into any script -- see *Current enforcement status*):

```bash
cargo test -p buzz-relay --lib tenant::tests
```

**NIP-98 replay unit-level key test** (infra-free, part of this
repository's own enumerated unit lane):

```bash
cargo nextest run -p buzz-core -p buzz-auth --lib -E 'test(key_isolates_communities_for_same_event_id)'
```

## Current enforcement status

| Facet | Test | Status | Basis |
|---|---|---|---|
| (a) unmapped host fails closed, wire | `unmapped_host_fails_closed_generically` | **GATED** | `#[ignore]`; needs a live two-host relay; no script or CI workflow in this repository invokes `conformance_multitenant` with `--ignored` |
| (a) same property, unit | `tenant::tests::*` (5 functions) | **UNWIRED** | Not `#[ignore]`d and infra-free, but Justfile's own comment states `test-unit` "did not enumerate `buzz-relay --lib`" as a whole, and neither `scripts/run-tests.sh` nor any `.github/workflows/*.yml` job invokes it either |
| (b) `#h` claim cannot override host | `client_supplied_community_cannot_override_host` | **GATED** | Same basis as the row above |
| (c) API tokens, storage | `lookup_by_hash_is_scoped_to_community`, `active_lookup_by_hash_is_scoped_to_community` | **GATED** | `#[ignore = "requires Postgres"]`; `scripts/run-tests.sh`'s own comment states both its unit and integration modes exclude these |
| (c) API tokens, wire | `token_minted_in_a_does_not_authorize_in_b` | **DOC-ONLY / NOT APPLICABLE** | Empty body, a compile-time anchor by design; additionally, this node's own research found the production consumer path it cites no longer exists -- `media.rs` authorizes uploads independent of `api_tokens` at this revision |
| (c) NIP-98 replay, unit (key shape) | `key_isolates_communities_for_same_event_id` | **VERIFIED** | Not `#[ignore]`d, no `todo!()` stub, pure function with no I/O, and enumerated unconditionally in Justfile's `test-unit` recipe (`cargo nextest run -p buzz-core -p buzz-auth --lib`), which `just ci` composes in |
| (c) NIP-98 replay, wire (live seen-set) | `nip98_replay_seenset_is_shared_and_community_scoped` | **GATED** | `#[ignore]`; needs a live two-host relay; not invoked anywhere in this repository |
| (c) membership/allowlist/archived-identity | `archive_in_a_does_not_affect_b` | **PENDING** | Entire body is a `pending_lane(...)` call implemented as `todo!()`; no assertion logic exists |

"VERIFIED" above rests on the test's current source shape (no gate, no
stub) and its enumeration in this repository's own unit-test recipe, per
`AGENTS.md`'s allowance that a test file's current state is acceptable
executable evidence for enforcement status -- it is not a personally
executed pass observed while authoring this node; no Rust toolchain was
available in this authoring environment (see the provenance entry above).

## Limits

- **Only one line of this ledger (the NIP-98 replay key-shape unit test) is
  both unconditional and enumerated in a lane this repository's own CI
  composes.** Everything else that would prove this obligation on the wire
  -- row zero's two tests and the NIP-98 replay live-seen-set test -- is
  `#[ignore]`d and, as far as this node's research found, has never been
  run against a real two-host relay in this repository's CI. A test
  existing and being well-constructed is not the same claim as the
  obligation currently holding in a running deployment.
- **The row-zero unit-test suite in `tenant.rs` is real, passing-if-run,
  and infra-free, but has no operational backstop today.** It is not
  `#[ignore]`d, yet no script or CI job this node found invokes it, so a
  regression there would not be caught by `just ci`. This is a distinct
  failure mode from `#[ignore]`-gating: nothing marks the test as
  conditional, but nothing runs it either.
- **The API-token storage-layer tests, even when manually run against
  Postgres and passing, do not currently correspond to a reachable
  production code path.** This node's own search of the workspace found no
  non-test caller of either community-scoped lookup function; the
  wire-level consumer fence the conformance test's own doc comment
  describes has been removed from `media.rs`. Passing these tests proves
  the SQL `WHERE` clause behaves correctly in isolation, not that anything
  in the shipped relay currently depends on it.
- **The `key_isolates_communities_for_same_event_id` unit test proves only
  that a cache-key *string* differs by community for an artificially
  colliding event id.** Per its own comment, natural wire traffic already
  produces distinct event ids per community because the NIP-98 `u` tag is
  part of the signed canonical bytes, so this test is a belt-and-suspenders
  check on a scenario "content-addressing makes implausible" -- it does not
  exercise the live Redis-backed seen-set, the `check_nip98_replay`
  middleware, or a real two-community deployment. That end-to-end property
  is exactly what the `#[ignore]`d wire test is for, and it has not been
  run.
- **The membership/allowlist/archived-identity obligation has zero test
  coverage today, gated or otherwise.** `enforce_relay_membership` already
  threading a `CommunityId` parameter through production code (cited above)
  is supporting context that the surrounding wiring is community-aware, not
  evidence that `archived_identities`/`pubkey_allowlist` are themselves
  correctly scoped -- no test claims that, and this node does not either.
- **Scope of scenarios, even for tests that do run:** exactly two named
  communities (A, B) plus one unmapped host. No test cited here covers more
  than two communities simultaneously, concurrent binding under contention,
  or host-aliasing/wildcard-host configurations beyond the empty- and
  whitespace-host branches the `tenant.rs` unit suite exercises.

## Scope and omissions

**This node covers** the current, honestly-stated verification status of
three authentication/authorization-specific rows of
`docs/multi-tenant-conformance.md` -- request community binding (row zero),
API tokens and NIP-98 replay, and relay membership/pubkey
allowlist/archived identities -- as of the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The remaining `docs/multi-tenant-conformance.md` rows (NIP-11, users/profiles/NIP-05, channel-less global events/DMs, channels-as-data-isolation, workflows, search/FTS, pub/sub/presence, media/Blossom, git hosting, mesh/agents/CLI, audit log) and the shared N=1/A-B parity harness | Issue #1371, `launchpad/docs/corpus/verification/formal/multi-tenant-relay.md` |
| NIP-42 WebSocket AUTH's own challenge-response protocol | `architecture-flows-websocket-authentication` |
| Whether `docs/multi-tenant-conformance.md`'s migration gates (its own "Migration gates" section) have been satisfied as a whole | Not assessed by this node; it covers only the three named rows' own tests |
| Deciding whether `buzz-relay` should grow an HTTP token-minting route (which would make the `token_minted_in_a_does_not_authorize_in_b` row wire-testable) | A product/security-surface decision, per the test file's own doc comment, not this node |

**A second, distinct finding surfaced while drafting this node, and is
recorded here rather than folded into the obligation above or filed as a
new task:** at this revision, no production code path in `buzz-relay`
calls either community-scoped API-token lookup function --
`media.rs`'s own comment states Blossom upload authority is now
"independent of bearer-token / api_tokens storage." The conformance test
file's own doc comment, written earlier, still describes `media.rs` as the
consumer fence for token lookups. That description is stale relative to
current source. This node cites the current, verified state (no production
caller) rather than repeating the stale claim, and leaves any correction to
the conformance test's own comment, or a decision about whether the
api_tokens table and its lookups are still wanted, to whoever owns that
code -- this node's scope is documenting the test contract's current
status, not proposing or making that change.

**Expected but not verified when this node was written:**

- **No test cited in this ledger was executed by this node's author.** No
  Rust toolchain was available in this authoring environment. Every
  enforcement-status claim rests on reading each test's current source
  (path, `#[ignore]`/`todo!()` state) and on reading which scripts/CI
  workflows enumerate it -- not on an observed pass or fail.
- **Whether a live two-host relay, if stood up and pointed at by
  `RELAY_URL_A`/`RELAY_URL_B`, would actually pass the four `#[ignore]`d
  wire tests cited here was not established.** Their construction was read
  and found sound; their outcome against a real deployment is unknown.
- **Whether any other production code path outside `crates/buzz-relay`
  (for example a CLI or admin tool) consumes the community-scoped API-token
  lookup functions was checked across the whole workspace (`crates/`) but
  not beyond it** -- `desktop/src-tauri`, `mobile/`, and any Block-internal
  (`squareup/*`) caller outside this repository's visible source were not
  searched.
