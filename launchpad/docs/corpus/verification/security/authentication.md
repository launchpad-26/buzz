---
id: verification-security-authentication
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
  - statement: "buzz-auth's nip42 module implements NIP-42 challenge/response WebSocket authentication, and its own module doc-comment states that AUTH events (kind:22242) are never stored or logged because they may carry bearer tokens."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:1-7"
  - statement: "verify_nip42_event returns AuthError::InvalidSignature for a wrong event kind or a Schnorr-signature failure, AuthError::ChallengeMismatch for a missing or mismatched challenge tag, AuthError::RelayUrlMismatch for a missing or mismatched (post-normalization) relay tag, and AuthError::EventExpired when created_at is more than 60 seconds from server time -- performing no database or network access in any of these checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:47-86"
  - statement: "nip42.rs's own #[cfg(test)] mod tests contains wrong_challenge_rejected, wrong_kind_rejected, expired_event_rejected, and wrong_relay_rejected, each constructing a deliberately invalid AUTH event and asserting verify_nip42_event returns the matching Err variant; none of these tests is #[ignore]-gated."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:88-183"
  - statement: "Justfile's test-unit recipe runs `cargo nextest run -p buzz-core -p buzz-auth --lib`, and .github/workflows/ci.yml's unit-tests job runs `just test-unit` whenever a pull request or push changes a Rust file -- so nip42.rs's four rejection unit tests run unconditionally, without any live relay, Postgres, or Redis, on every Rust-touching pull request."
    entry_class: FACT
    evidence:
      - "Justfile:316-321"
      - ".github/workflows/ci.yml:122-146"
  - statement: "On a new WebSocket connection, buzz-relay's connection.rs stores AuthState::Pending{challenge} on the connection before sending the AUTH challenge frame, and a background task races a 5-second sleep (the AUTH_TIMEOUT constant) against the connection's cancellation token, cancelling (closing) the connection and incrementing buzz_ws_auth_timeouts_total if the connection has not reached AuthState::Authenticated when the sleep elapses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:29"
      - "crates/buzz-relay/src/connection.rs:182-195"
      - "crates/buzz-relay/src/connection.rs:251-272"
  - statement: "handle_auth's state-machine guard rejects a second AUTH message on a connection whose AuthState is already Authenticated or already Failed with an immediate OK-false reply (\"auth-required: already authenticated\" / \"auth-required: authentication already failed\") and returns before any re-verification is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:43-68"
  - statement: "The EVENT, REQ, and COUNT message handlers each independently read the connection's AuthState inside their own function and reject with an \"auth-required: ...\" message (REQ additionally sends a CLOSED frame) when it is not AuthState::Authenticated; there is no single shared authentication gate upstream of all three."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:634-654"
      - "crates/buzz-relay/src/handlers/req.rs:57-94"
      - "crates/buzz-relay/src/handlers/count.rs:24-39"
  - statement: "For an EVENT submitted on an already-authenticated connection, the relay rejects it with \"invalid: event pubkey does not match authenticated identity\" unless event.pubkey equals the connection's authenticated pubkey, except for kind:1059 gift-wrap events; this check runs before both the ephemeral and persistent event branches."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:656-668"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs contains test_unauthenticated_rejected (connects without completing AUTH, sends a message, and treats an OK-false reply, a closed connection, or a timeout as equally acceptable relay behaviour), test_auth_event_kind_rejected (submits a signed kind:22242 event via an ordinary EVENT message rather than AUTH, and asserts OK-false with a message mentioning \"invalid\" or \"auth\"), and test_pubkey_mismatch_rejected (authenticates as one keypair, then sends an event signed by a second keypair on the same connection, and asserts OK-false) -- all three functions are annotated #[ignore], per the file's own module doc-comment, because they require a running relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1-19"
      - "crates/buzz-test-client/tests/e2e_relay.rs:591-625"
      - "crates/buzz-test-client/tests/e2e_relay.rs:846-871"
      - "crates/buzz-test-client/tests/e2e_relay.rs:1007-1030"
  - statement: "The .github/workflows/ci.yml relay-e2e job's \"Relay E2E tests\" step runs cargo test against e2e_relay filtered to only the `invite` and `nip43_membership_snapshots_are_rejected` test names (plus separate, differently-named suites for other files); it names no filter that selects test_unauthenticated_rejected, test_auth_event_kind_rejected, or test_pubkey_mismatch_rejected, so CI does not execute these three tests."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:890-896"
  - statement: "scripts/run-tests.sh's run_integration_tests function (invoked by `just test` in its default/all mode) runs the workspace's integration tests as `cargo test --test '*' -- --nocapture`, passing no `--ignored` flag; because cargo test's documented default behaviour is to skip any test annotated #[ignore] unless `--ignored` is passed, this command does not execute test_unauthenticated_rejected, test_auth_event_kind_rejected, or test_pubkey_mismatch_rejected either -- combined with the CI finding above, no automated command in this repository currently runs these three tests, and they must be invoked manually with an explicit `--ignored <test-name>` filter against a live relay, Postgres, and Redis."
    entry_class: INFERENCE
    evidence:
      - "scripts/run-tests.sh:127-145"
      - "Justfile:312-313"
      - ".github/workflows/ci.yml:890-896"
      - "https://doc.rust-lang.org/book/ch11-02-running-tests.html#ignoring-some-tests-unless-specifically-requested"
    confidence: 0.8
  - statement: "crates/buzz-relay/src/connection.rs's own #[cfg(test)] mod tests (the file's final section) contains only tests of send_loop's batching, flush-ordering, and close-frame behaviour (send_loop_batches_queued_data_frames_into_one_flush and seven sibling tests); no test in this module exercises the AUTH_TIMEOUT cancellation path described above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:740-1111"
  - statement: "crates/buzz-relay/src/handlers/auth.rs's own #[cfg(test)] mod tests (single_auth_tag_extracted_verbatim, no_auth_tag_returns_none, duplicate_auth_tags_return_none) covers only the extract_auth_tag_json NIP-OA tag-extraction helper, not handle_auth's already-Authenticated/already-Failed state-machine guard described above, and no other file in this repository names a test for that guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:296-350"
  - statement: "nip42.rs's own test suite exercises only the AUTH-specific checks layered on top of the shared Schnorr verifier (event kind, challenge, relay URL, timestamp); none of its tests construct an AUTH event with the correct kind and a genuinely tampered or forged signature, so a forged-signature rejection specific to this obligation is exercised only via the shared buzz_core::verify_event call, whose own test coverage this node does not establish."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:47-56"
      - "crates/buzz-auth/src/nip42.rs:88-183"
  - statement: "launchpad/docs/corpus/architecture/flows/websocket-authentication.md (id: architecture-flows-websocket-authentication) is an existing, merged corpus node describing this same NIP-42 flow architecturally; its own Verification section names test_connect_and_authenticate, test_unauthenticated_rejected, test_auth_event_kind_rejected, and test_pubkey_mismatch_rejected as representative coverage, explicitly stating they are #[ignore]-gated and are linked \"as representative coverage rather than asserting they were executed as part of authoring it\" -- a narrower claim than this node's own finding above that neither CI nor `just test` currently selects those three tests at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "Issue #1383's definition of done requires naming negative/error cases when they are part of the contract and not claiming coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1383 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# Authentication (NIP-42 WebSocket) -- test contract

## Purpose and boundary

This node documents one security obligation: that a Buzz relay WebSocket
connection can only ever act with an authenticated identity if it has
completed valid NIP-42 challenge/response verification for that specific
requester. It covers the obligation and the tests that verify its rejection
paths only -- not the NIP-42 flow's full architecture (already documented at
`architecture-flows-websocket-authentication`), not NIP-98 HTTP Auth, and not
the ban/allowlist/relay-membership authorization checks that run immediately
after a successful cryptographic verification. Those are named explicitly in
*Scope and omissions* below rather than folded in here.

## Obligation

> A message on a Buzz relay WebSocket connection is processed as
> authenticated only if that connection has completed valid NIP-42
> challenge/response verification for the exact requester sending it; a
> connection whose AUTH attempt fails verification, that has not yet
> authenticated, or that submits a persistent/ephemeral event signed by a
> pubkey other than the one it authenticated with, is rejected rather than
> processed as authenticated.

## Verifying test(s)

**Unit tests (unconditional, no infrastructure required):**

- `crates/buzz-auth/src/nip42.rs` -- `tests::wrong_challenge_rejected`,
  `tests::wrong_kind_rejected`, `tests::expired_event_rejected`,
  `tests::wrong_relay_rejected` -- each builds a deliberately invalid AUTH
  event (wrong challenge value, wrong event kind, timestamp 120s stale, wrong
  relay tag) and asserts `verify_nip42_event` returns the corresponding
  `AuthError` variant rather than `Ok(())`.

**End-to-end tests (`#[ignore]`-gated, require a live relay, Postgres, and
Redis):**

- `crates/buzz-test-client/tests/e2e_relay.rs` --
  `test_unauthenticated_rejected` -- connects without completing AUTH and
  attempts to send a message; covers the "never authenticated" branch of the
  obligation.
- `crates/buzz-test-client/tests/e2e_relay.rs` --
  `test_auth_event_kind_rejected` -- submits a signed kind:22242 AUTH event
  through an ordinary `EVENT` message instead of an `AUTH` message; covers
  that an AUTH-shaped event cannot be smuggled in as authenticated content.
- `crates/buzz-test-client/tests/e2e_relay.rs` --
  `test_pubkey_mismatch_rejected` -- authenticates as one keypair, then sends
  an event signed by a second keypair on the same connection; covers the
  pubkey-binding half of the obligation (identity spoofing after a
  successful AUTH).

## How to run them

Unit tests, no infrastructure needed:

```bash
cargo test -p buzz-auth --lib nip42::tests -- --nocapture
```

This is the same target `just test-unit` runs (via `cargo nextest run -p
buzz-core -p buzz-auth --lib`), which CI's `unit-tests` job runs on every
pull request that touches a Rust file.

End-to-end tests, against a live relay with Postgres and Redis running
(e.g. via `just relay` / `docker-compose up`, or `./scripts/start-relay-for-tests.sh`
as CI's own relay-e2e job does):

```bash
RELAY_URL=ws://localhost:3000 \
  cargo test -p buzz-test-client --test e2e_relay -- --ignored \
  test_unauthenticated_rejected test_auth_event_kind_rejected test_pubkey_mismatch_rejected \
  --nocapture
```

Neither `just test` nor CI currently invokes this filtered `--ignored`
selection automatically -- see *Current enforcement status*.

## Current enforcement status

**Mixed -- this obligation's sub-claims are not enforced uniformly, and
averaging them into one label would misdescribe half of it:**

| Rejection path | Test(s) | Status |
|---|---|---|
| Wrong challenge, wrong kind, expired timestamp, wrong relay URL (pure crypto/protocol layer) | `nip42.rs` unit tests | **Verified.** Run unconditionally, no `#[ignore]`, exercised by CI's `unit-tests` job on every Rust-touching pull request. |
| Never authenticated, then attempts to send | `test_unauthenticated_rejected` | **Gated, and not currently run by any automated command.** The test exists and is `#[ignore]`-gated for legitimate infrastructure reasons, but neither CI's `relay-e2e` job (which filters to `invite` and `nip43_membership_snapshots_are_rejected` only) nor `just test` (which runs `cargo test --test '*'` without `--ignored`) selects it. |
| AUTH-kind event submitted as ordinary EVENT | `test_auth_event_kind_rejected` | **Gated, and not currently run by any automated command.** Same reasoning as above. |
| Pubkey mismatch after successful AUTH | `test_pubkey_mismatch_rejected` | **Gated, and not currently run by any automated command.** Same reasoning as above. |
| Second AUTH message after already-Authenticated or already-Failed | `handle_auth`'s own state-machine guard | **Pending -- no test found.** Neither `handlers/auth.rs`'s own unit tests nor any e2e test in this repository exercises this branch. |
| Connection that never sends any AUTH at all (the 5-second `AUTH_TIMEOUT`) | the background timeout task in `connection.rs` | **Pending -- no test found.** Neither `connection.rs`'s own unit tests nor any e2e test exercises this branch; the only executable evidence of its existence is the source code and the `buzz_ws_auth_timeouts_total` metric it increments. |

A reader relying on "these tests exist, therefore this is checked in CI" would
be wrong for four of the six rows above. That is the specific failure this
section exists to prevent.

## Limits

**What is actually exercised, and how:**

- The pure-verification layer (`verify_nip42_event`) is exercised for four of
  its five rejection reasons: wrong kind, wrong challenge, wrong relay URL,
  expired timestamp. It is **not** exercised for a genuinely forged or
  tampered Schnorr signature on an otherwise well-formed kind:22242 event --
  every unit test in `nip42.rs` either uses a validly-signed event or fails
  earlier on the kind check, so the `AuthError::InvalidSignature` branch
  triggered by `buzz_core::verify_event` failing is never reached by a test
  in this file. Whether `buzz_core::verify_event`'s own signature-failure
  path is tested elsewhere in `crates/buzz-core` was not established here.
- Neither `verify_nip42_event`'s missing-`challenge`-tag nor
  missing-`relay`-tag branches (the `.ok_or(...)` calls, as distinct from a
  tag present with the *wrong* value) has a dedicated test; only the
  wrong-value cases are covered.
- **Replay is not tested.** No test reuses a challenge that was already
  consumed by a different connection, or resubmits a previously-accepted AUTH
  event a second time. The obligation as stated does not claim replay
  resistance, and this node makes no such claim either -- this is named as a
  gap, not as a failure of the stated obligation.
- The `test_unauthenticated_rejected` end-to-end test itself accepts three
  different outcomes (an `OK false` reply, the connection being closed, or a
  timeout) as equally passing. It proves *some* form of rejection happens,
  not which specific one, so it cannot be read as pinning the relay to one
  particular rejection behaviour for an unauthenticated send.
- The two state-machine branches with no test at all -- a second AUTH after
  `Authenticated`/`Failed`, and the 5-second `AUTH_TIMEOUT` closing a
  connection that never authenticates -- are real code paths (cited above)
  but their behaviour is currently established only by reading the source,
  not by any executable check.
- Even where the end-to-end tests exist and would exercise real gaps (an
  unauthenticated connection, an AUTH-kind event smuggled in, a post-auth
  pubkey mismatch), **no CI job and no `just` recipe currently runs them.**
  A green CI run or a clean `just test` on this repository says nothing
  about whether these three specific behaviours still hold; only running the
  `--ignored`-filtered command in *How to run them* against a live relay
  does.

## Scope and omissions

**This node covers** the NIP-42 WebSocket authentication obligation stated
above, its unit- and end-to-end-level verifying tests, and each test's actual
(as opposed to assumed) execution status in this repository's CI and `just`
recipes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Where it belongs |
|---|---|
| NIP-98 HTTP Auth (`crates/buzz-auth/src/nip98.rs`, kind:27235) -- the relay's HTTP-surface authentication path, with its own extensive rejection unit-test suite (wrong kind, expired timestamp, URL/method mismatch, duplicate tags, payload-hash mismatch, loopback-alias rejection) | A separate future test-contract node; `architecture-flows-websocket-authentication` already names this as a distinct, not-yet-documented flow, and this node does not duplicate that scoping decision, only reuses it |
| The ban, pubkey-allowlist, and relay-membership checks that run immediately after a successful NIP-42 verification | These are authorization/community-scoping decisions layered on top of a proven identity, not the authentication step itself; `architecture-flows-websocket-authentication`'s "Trust-boundary and authorization crossings" section names them |
| NIP-OA agent-to-owner delegation and its attestation format | `architecture-flows-websocket-authentication`, which also marks this as not yet in the corpus |
| The full architecture of the WebSocket authentication flow (ordered interactions, trust-boundary crossings, connection lifecycle) | `architecture-flows-websocket-authentication`, an existing merged corpus node this document references rather than restates |
| Whether `buzz_core::verify_event`'s own Schnorr-verification-failure path is covered by tests in `crates/buzz-core` | Not established by this node; named as a limit above |

**Relationships.** This node declares one `references` edge to
`architecture-flows-websocket-authentication`, which is loadable from
`origin/launchpad`'s corpus tree at the recorded revision and already
describes the flow this obligation is drawn from. No other corpus node under
`launchpad/docs/corpus/` at the recorded revision is specific to this
obligation's subject, so no further relationships are declared.

**Expected but not verified when this node was written:**

- Whether `crates/buzz-core`'s own test suite covers a forged/tampered
  Schnorr signature independently of `nip42.rs` was not checked; this node
  states only that `nip42.rs` itself does not cover it.
- Whether the `buzz_ws_auth_timeouts_total` metric is scraped or alerted on
  in any deployed environment was not checked; only that the counter exists
  in source.
- This node's "gated, and not currently run by any automated command"
  finding for the three named e2e tests was established by reading
  `.github/workflows/ci.yml` and `scripts/run-tests.sh` at the recorded
  revision, not by executing `just test` or the CI workflow itself end to
  end.
