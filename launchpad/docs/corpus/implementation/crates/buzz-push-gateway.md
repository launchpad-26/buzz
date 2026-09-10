---
id: implementation-crates-buzz-push-gateway
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-push-gateway's lib.rs re-exports http::{router, router_with_metrics, AppState} and declares thirteen source modules: apns, app_attest, authority, config, grant, http, metrics, model, postgres, strict_json (crate-private), token, plus lib.rs and main.rs; the crate builds both a library (buzz_push_gateway) and a binary (buzz-push-gateway)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/lib.rs"
      - "crates/buzz-push-gateway/Cargo.toml"
  - statement: "The crate's AppProfile enum (model.rs) has exactly one variant, BuzzIosDogfood, serializing to the wire string \"buzz-ios-dogfood\"; this is a narrowing from an earlier two-profile design, evidenced by migration 0002_application_profiles.sql (which deleted rows and renamed the allowed CHECK values from 'buzz-ios-production'/'buzz-ios-sandbox' to 'buzz-ios-dogfood'/'buzz-ios-app-store') and migration 0004_dogfood_only_profile.sql (which further deleted 'buzz-ios-app-store' rows and narrowed the CHECK constraint to 'buzz-ios-dogfood' only)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
      - "crates/buzz-push-gateway/migrations/0002_application_profiles.sql"
      - "crates/buzz-push-gateway/migrations/0004_dogfood_only_profile.sql"
  - statement: "docs/nips/NIP-PL.md's own \"Public APNs Gateway Profile\" section (line 267) states the registered app_profile value is buzz-ios-dogfood, so the current single-profile code and the current spec text agree with each other on this point; an earlier draft of the architecture-flows-push-notification corpus node (already merged) cites the now-superseded two-profile names and is stale against both, but correcting that node is not this task's job."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md:267"
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "config.rs's Config::from_map requires DATABASE_URL, BUZZ_PUSH_PUBLIC_DELIVERY_URL, BUZZ_PUSH_MAX_GRANT_LIFETIME_SECONDS, BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH, BUZZ_PUSH_GRANT_KEYS, BUZZ_PUSH_TOKEN_KEYS, and the profile-scoped BUZZ_PUSH_DOGFOOD_APP_ATTEST_APP_ID/BUZZ_PUSH_DOGFOOD_APNS_CERT_PATH/BUZZ_PUSH_DOGFOOD_APNS_TOPIC; BUZZ_PUSH_MAX_INSTALLATION_LIFETIME_SECONDS, BUZZ_PUSH_ENDPOINT_QUOTA_WINDOW_SECONDS, BUZZ_PUSH_ENDPOINT_QUOTA_MAX_DELIVERIES, BUZZ_PUSH_BIND_ADDR, BUZZ_PUSH_HEALTH_ADDR, and BUZZ_PUSH_DOGFOOD_APNS_ENVIRONMENT are optional with defaults; there is no BUZZ_PUSH_ENABLED_PROFILES, BUZZ_PUSH_APNS_KEY_ID, or BUZZ_PUSH_APNS_TEAM_ID variable in the current config surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "BUZZ_PUSH_PUBLIC_DELIVERY_URL is validated to be exactly https scheme, host push.buzz.xyz, no port, path /v1/deliveries/apns, and no query/fragment/username/password; a malformed or non-matching URL fails Config::from_map rather than being accepted loosely, and this exact rule is covered by the malformed_security_configuration_fails_startup test."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The crate holds two independently keyed AEAD (AES-256-GCM) keyrings -- GrantKeyring (grant.rs, BUZZ_PUSH_GRANT_KEYS) sealing opaque EndpointGrant delivery capabilities that leave the process toward relays, and TokenKeyring (token.rs, BUZZ_PUSH_TOKEN_KEYS) sealing APNs device tokens that never leave the process except to Apple -- and Config::from_map rejects startup if any grant key and token key share an id or key bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/grant.rs"
      - "crates/buzz-push-gateway/src/token.rs"
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "GrantKeyring::issue seals with the current (first-listed) key only; GrantKeyring::open selects the decrypting key by the key id encoded in the ciphertext's own prefix (id.base64url-payload), so predecessor keys are decrypt-only and support rotation; the encoded grant is additionally length-bounded to MAX_GRANT_BYTES (4096) at issue and rejected at open if the decoded payload is under 13 bytes (12-byte nonce + at least one ciphertext byte)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/grant.rs"
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "http.rs's router_with_metrics builds two independent axum Routers: a public router with seven POST routes (/v1/installations/challenges, /v1/installations, /v1/delegations, /v1/delegations/revoke, /v1/installations/endpoint, /v1/installations/revoke, /v1/deliveries/apns) under a ConcurrencyLimitLayer::new(256) and a 20-second TimeoutLayer, with the enrollment route additionally layered with a larger RequestBodyLimitLayer (MAX_ENROLL_REQUEST_BYTES) than the other six (MAX_REQUEST_BYTES); and a private health router with GET /_liveness, GET /_readiness, and -- only when a PrometheusHandle is supplied -- GET /metrics in Prometheus text format."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "The challenge handler (http.rs) issues a random 32-byte challenge with expires_at = now + 300 (a hardcoded 300-second lifetime), matching docs/nips/NIP-PL.md's statement that the challenge 'expires after 300 seconds'; the delegate handler independently rejects a request whose not_before exceeds now + 300."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "docs/nips/NIP-PL.md:292"
  - statement: "The enroll handler (http.rs) is idempotent under exact-request replay: before consuming the challenge or creating a new installation, it calls AuthorityStore::matching_installation with the verified App Attest key id, profile, endpoint fingerprint, epoch, and expiry, and if an existing live installation matches on every field including the recovered public key, it returns the same 201 response again without re-consuming the challenge or writing a second row; a match on key id/fingerprint/epoch/expiry but a different recovered public key is rejected (404 not_authorized) rather than silently accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/authority.rs"
  - statement: "AppAttestVerifier::new (app_attest.rs) pins the configured Apple App Attest root certificate PEM to a hardcoded SHA-256 digest at construction time -- an app_id or root cert that does not match the expected root fails immediately -- and verify_attestation additionally bounds the decoded CBOR attestation object to MAX_APP_ATTESTATION_BYTES before delegating to the appattest crate's verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "The AuthorityStore trait (authority.rs) is the crate's storage abstraction: fourteen async methods (ready, put_challenge, consume_challenge, create_installation, matching_installation, installation, advance_assertion_counter, upsert_delegation, rotate_endpoint, revoke_delegation, revoke_installation, authorize_delivery, finish_delivery, reap_expired) plus a three-variant AuthorityError (Rejected, RateLimited, Unavailable); PostgresAuthorityStore (postgres.rs) is the production implementation and MemoryAuthorityStore (authority.rs, in-file, default-derived, single-Mutex-serialized) is an executable reference model used by the crate's own conformance-style unit tests, not a production alternative."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/authority.rs"
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "The deliver handler (http.rs, POST /v1/deliveries/apns) verifies a NIP-98 signed HTTP Authorization header (nostr::nips::nip98::verify_auth_header) against the configured delivery URL before opening the grant; it then opens the EndpointGrant via GrantKeyring::open and rejects (404 invalid_grant) on a version mismatch, an invalid relay pubkey, a relay-pubkey mismatch against the NIP-98 signer, a non-positive endpoint_epoch/generation, or an already-expired grant/request -- all before calling AuthorityStore::authorize_delivery."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "After AuthorityStore::authorize_delivery returns a DeliveryPermit, the deliver handler additionally rejects (404 invalid_grant) if the admitted authority's profile does not equal the grant's own app_profile, and separately rejects (503 configuration_fault, disposition Retryable) if the admitted profile is not AppProfile::BuzzIosDogfood -- the second check is currently unreachable in production since the crate registers only that one profile, but it is live code, not a comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "The actual APNs send is detached into tokio::spawn after admission commits, so that request cancellation cannot leave admission committed with no matching finish_delivery call; the spawned task calls PushTransport::send, records push_gateway_apns_deliveries_total/push_gateway_apns_delivery_seconds via crate::metrics::record_apns_delivery, classifies the DeliveryOutcome into a DeliveryDisposition (Retry/ConfigurationFault -> Retryable; Accepted/InvalidEndpoint/PermanentRequestFault -> Terminal), and calls AuthorityStore::finish_delivery with that disposition before the handler maps the outcome to an HTTP response."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "apns.rs's ApnsTransport is a client-certificate (mTLS) HTTP/2 transport: ApnsTransport::certificate builds a reqwest::Identity from a combined PEM private key and certificate (config.rs's BUZZ_PUSH_DOGFOOD_APNS_CERT_PATH), selects a base URL from ApnsEnvironment (Production -> api.push.apple.com, Sandbox -> api.sandbox.push.apple.com), and PushTransport::send posts the fixed APNS_RECONNECT_PAYLOAD constant to POST {base_url}/3/device/{endpoint} with apns-id/apns-topic/apns-push-type/apns-priority/apns-expiration headers and no Authorization/Bearer header; a dedicated test (certificate_transport_sends_no_bearer_and_exact_body_for_every_attempt) asserts the outbound body equals the constant and no Authorization header is present."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "apns.rs's classify() function maps APNs HTTP status/reason pairs to a five-variant DeliveryOutcome (Accepted, InvalidEndpoint, Retry, ConfigurationFault, PermanentRequestFault); only a 410 with reason \"Unregistered\" produces InvalidEndpoint, while 400 BadDeviceToken/DeviceTokenNotForTopic and 403/429-TooManyProviderTokenUpdates deliberately map to ConfigurationFault rather than InvalidEndpoint so a deployment misconfiguration cannot mass-invalidate real device endpoints; this exact non-conflation is asserted by response_classes_do_not_massacre_endpoints_on_provider_faults."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "docs/nips/NIP-PL.md's normative \"Public APNs Gateway Profile\" section states (line 420): \"The gateway performs one APNs request, except that an APNs expired-provider-token response permits one credential refresh and one retry.\" The current apns.rs has no credential/JWT concept at all (ApnsTransport::certificate takes a PEM identity, not a provider key/key-id/team-id triple), DeliveryOutcome carries no RefreshCredential (or equivalent) variant, and PushTransport::send performs exactly one HTTP request per call with no internal retry loop -- the retry-on-expired-credential behavior the spec requires is not implemented in the current transport. This is a genuine, verified divergence between the code and its target, not a claim about which side is correct."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md:420"
      - "crates/buzz-push-gateway/src/apns.rs"
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "metrics.rs installs a Prometheus recorder (metrics_exporter_prometheus) with no HTTP listener of its own -- rendering is served only from http.rs's private health router's GET /metrics -- and emits seven series with closed-set label values: push_gateway_apns_send_attempts_total, push_gateway_apns_deliveries_total{outcome}, push_gateway_apns_delivery_seconds (11 fixed buckets), push_gateway_admissions_total{result}, push_gateway_delivery_errors_total{class}, push_gateway_reaper_failures_total, push_gateway_readiness_failures_total{cause}; there is no push_gateway_apns_credential_refreshes_total series in the current code."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "main.rs runs one authority.reap_expired call synchronously at startup, then spawns a reaper task whose tokio::time::interval(300s) is ticked once immediately (discarded) before the loop begins, so the effective cadence is startup-once plus every 300 seconds thereafter, each failure recorded via metrics::record_reaper_failure; graceful shutdown flips an AtomicBool (read by the /_readiness handler), stops the public listener with a 30-second bounded drain via tokio::time::timeout, then stops the health listener and aborts the reaper task."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs"
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "postgres.rs's own #[cfg(test)] suite (readiness_requires_migrated_schema_dml_and_no_ddl, reaper_deletes_active_child_of_retention_eligible_revoked_installation, concurrent_same_request_id_admits_exactly_once, concurrent_admissions_never_over_admit_past_quota_ceiling, duplicated_retryable_release_does_not_permanently_unfence_request_id, retryable_release_frees_request_id_on_real_postgres, and others) connects to a real PostgreSQL instance via a hardcoded TEST_DB_URL constant (postgres://buzz:buzz_dev@localhost:5432/buzz) with plain #[tokio::test] attributes, not #[ignore]; the Justfile's unit-test recipe runs `cargo nextest run -p buzz-push-gateway` (Justfile:346) under a comment stating Postgres-backed contract/race tests run in a dedicated CI job, but this task did not trace which CI job actually selects postgres.rs's tests, so which lane runs them is not independently confirmed here."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/postgres.rs"
      - "Justfile:346"
  - statement: "RepoQL's structural index of this crate (queried via mcp__repoql__read structure views) is stale against this worktree at the recorded revision: it reported a JWT-based ApnsTransport (fields signing_key/key_id/team_id/cached_jwt, a token() constructor), a RefreshCredential variant on DeliveryOutcome, a profile parameter on PushTransport::send, and a BUZZ_PUSH_ENABLED_PROFILES-shaped AppState.enabled_profiles field -- none of which exist in the actual on-disk source at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3; every claim in this node's evidence ledger was independently re-verified by direct Read/grep against the worktree files themselves, not taken from RepoQL's structure output."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/config.rs"
---

# buzz-push-gateway: implementation reference

`crates/buzz-push-gateway` (binary `buzz-push-gateway`, library `buzz_push_gateway`)
is the standalone Rust/Axum/SQLx service that realizes the "Public APNs Gateway
Profile (Buzz, normative)" section of `docs/nips/NIP-PL.md` — the one gateway
profile that section registers for NIP-PL push leases. It holds Apple App Attest
verification, APNs provider credentials, delegation-capability issuance, and
encrypted device-token custody, so that relays (the NIP-PL executor role) never see
a raw APNs token. This node traces the crate's modules, handlers, and tests to the
specific normative clauses they realize, one layer below the architectural
container/flow description already in the corpus.

## Target

`docs/nips/NIP-PL.md`, section "Public APNs Gateway Profile (Buzz, normative)"
(roughly lines 261–330 at the recorded revision), plus the adjoining response-code
table and the "one APNs request... one credential refresh and one retry" clause at
line 420. This is a file path, not a corpus node id — no NIP-PL corpus node exists
yet in `launchpad/docs/corpus/`, so no `implements` relationship is declared (see
*Relationships* below). A reader can open `docs/nips/NIP-PL.md` directly; the
section is explicitly marked normative for any implementation that uses this
profile, distinguishing it from the surrounding non-normative base protocol text.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `model::AppProfile::BuzzIosDogfood` | NIP-PL.md:267, "The registered `app_profile` value is `buzz-ios-dogfood`" | Single-variant enum; code and spec agree at the recorded revision (see evidence ledger for the migration history that narrowed a two-profile design down to this). |
| `http::challenge` (300s `expires_at`) | NIP-PL.md:292, "single-use, expires after 300 seconds" | Hardcoded literal `300`, not a config value. |
| `http::enroll` + `AuthorityStore::matching_installation` | NIP-PL.md:330, exact-replay idempotency requiring "exact equality of attested key, profile, endpoint fingerprint, epoch, and expiration" | A mismatch on the recovered public key is rejected rather than silently treated as idempotent. |
| `app_attest::AppAttestVerifier` (pinned Apple root SHA-256, `MAX_APP_ATTESTATION_BYTES` bound) | NIP-PL.md's App Attest enrollment/assertion requirement (section around line 292–330) | Verification itself is delegated to the `appattest` crate; this module owns transcript construction, size bounding, and root pinning. |
| `http::deliver` NIP-98 check (`verify_auth_header`) then `grant::GrantKeyring::open` | NIP-PL.md "relay↔gateway" delivery authentication and the response-code table (`404 invalid_grant`, `401 invalid_auth`) | Order matters: auth header is verified before the grant is even opened, so a forged/missing NIP-98 header never reaches grant decryption. |
| `http::deliver` post-admission profile checks (`profile != grant.app_profile` → `404`; `profile != BuzzIosDogfood` → `503 configuration_fault`) | Implicit corollary of NIP-PL.md's single registered profile | The second check is currently dead in production traffic (only one profile is ever admitted) but is live, tested code, not a stub. |
| `apns::ApnsTransport` (client-certificate mTLS, `POST {base}/3/device/{endpoint}`) | NIP-PL.md's transport-profile requirement that "the application body is always the exact constant registered in the APNs transport profile" | Body-constancy is realized (`APNS_RECONNECT_PAYLOAD`, asserted by test); provider-authentication mechanism diverges from the spec text — see *Divergences*. |
| `apns::classify` | NIP-PL.md's response-code table (`200`/`410`/`503`/`400` mapping) | Deliberately keeps `BadDeviceToken`/`DeviceTokenNotForTopic`/`403` as `ConfigurationFault`, not `InvalidEndpoint`, so a misconfigured topic/environment cannot mass-invalidate real endpoints. |
| `metrics` module (7 series, closed label sets, private-router-only `GET /metrics`) | Corpus/deployment convention (`docs/push-gateway-deployment.md`, not re-cited here) that metrics never carry request-scoped identifiers | Verified structurally: every label in `metrics.rs` is a compile-time `&'static str` from a closed enum or fixed set. |
| `authority::AuthorityStore` trait + `postgres::PostgresAuthorityStore` | NIP-PL.md's requirement that the gateway "retains installation authority, encrypted APNs-token custody, relay delegations, replay reservations, and endpoint quotas" | `authority::MemoryAuthorityStore` is a same-crate reference model for tests, not a second production backend. |
| `main.rs` reaper (startup + 300s interval) and 30s bounded graceful-shutdown drain | No specific NIP-PL clause; operational hygiene for the durable state NIP-PL requires the gateway to retain | Cited here because it is concrete crate behavior, not because NIP-PL specifies a retention cadence. |

## Divergences

One verified divergence was found between the code and the target spec:

- **APNs provider-credential refresh is specified but not implemented.**
  `docs/nips/NIP-PL.md:420` states normatively: "The gateway performs one APNs
  request, except that an APNs expired-provider-token response permits one
  credential refresh and one retry." The current `apns::ApnsTransport` is a
  client-certificate (mTLS) transport built from a combined PEM identity
  (`ApnsTransport::certificate`, `config::AppProfileConfig::apns_cert_path`) — it
  has no provider-JWT, key-id, or team-id concept to expire, `DeliveryOutcome` has
  no refresh-and-retry variant, and `PushTransport::send` issues exactly one HTTP
  request with no internal retry. Whichever side is "correct" — the spec clause
  describing an earlier or intended JWT-based design, or the code having moved to
  certificate auth without the spec being updated — was not determined during this
  task; both are cited as directly-read fact, and adjudicating between them is out
  of this node's scope (see the plan's *OPEN* note).

No other divergence was found between the implementation surface rows above and
the target spec text they cite; each row's spec citation and code citation were
both opened directly before being paired.

## Verification

- **Unit tests, infra-free.** `cargo nextest run -p buzz-push-gateway` (wired into
  the repository's unit-test lane at `Justfile:346`) runs every `#[cfg(test)]`
  module across the crate's 13 source files except `postgres.rs`'s Postgres-backed
  suite (see below). Representative coverage: `apns.rs`'s
  `certificate_transport_sends_no_bearer_and_exact_body_for_every_attempt` and
  `response_classes_do_not_massacre_endpoints_on_provider_faults`; `config.rs`'s
  `dogfood_profile_requires_server_owned_identity_and_certificate` and
  `cross_keyring_id_or_material_reuse_fails_startup`; `grant.rs`'s
  `current_issues_and_predecessor_opens_after_rotation`; `metrics.rs`'s
  `recorder_renders_sanitized_bounded_series`; `authority.rs`'s
  `retry_releases_request_id_but_burns_auth_event` and
  `terminal_outcome_burns_request_id` (against the in-crate
  `MemoryAuthorityStore` reference model).
- **Postgres-backed tests.** `postgres.rs`'s own suite (concurrency/admission-fence
  tests such as `concurrent_admissions_never_over_admit_past_quota_ceiling`,
  reaper/retention tests, and a readiness/role-grant test) connects to a real
  PostgreSQL at a hardcoded `TEST_DB_URL`, with plain `#[tokio::test]` attributes
  (no `#[ignore]`). Which CI job selects these specifically was not independently
  confirmed this session (see *Scope and omissions*).
- **Manual/live-only.** One `apns.rs` test
  (`live_sandbox_probe_reports_literal_status_and_body`) is `#[ignore]`d and
  requires `BUZZ_PUSH_LIVE_APNS_CERT_PATH`/`BUZZ_PUSH_LIVE_APNS_TOPIC` pointed at a
  real dogfood identity — it is not part of any automated gate.
- **No automated check for the Divergences finding above.** The credential-refresh
  gap is not asserted against by any test found in this crate; it surfaced only
  from reading the spec and code side by side.

## Relationships

- **implements:** none declared. The target (`docs/nips/NIP-PL.md`'s Public APNs
  Gateway Profile section) has no corpus node id yet — per the
  `implementation-reference` template and `AGENTS.md` step 9, an edge to a
  nonexistent id is a hard validation error, not a soft placeholder.
- **references / part-of:** none declared toward `architecture-containers-push-gateway`
  or `architecture-flows-push-notification`, even though both are merged and both
  are about this same crate. Both documented nodes carry claims already shown
  stale against the current worktree (JWT/provider-token APNs auth,
  `BUZZ_PUSH_ENABLED_PROFILES`, two app profiles, an eight-metric list including a
  credential-refresh counter that no longer exists) — declaring `part-of` or
  `references` toward them would assert this node sits underneath or supports
  claims this node's own evidence ledger contradicts. Once those two nodes are
  refreshed against current code, a `references` edge from this node (implementation
  detail) toward them (architectural container/flow) would be a natural fit; adding
  it now is left to whoever does that refresh.

## Scope and omissions

**This node covers** what `buzz-push-gateway` is responsible for at the
module/handler/test level, which parts of its code realize `docs/nips/NIP-PL.md`'s
Public APNs Gateway Profile section, the one verified divergence between the code
and that spec text, and how the realization is checked today (automated unit
tests, Postgres-backed tests, and one manual-only live probe).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The gateway's architectural responsibility, ownership boundary against the relay, deployment/data/security implications, and directly-connected-container interfaces | `architecture-containers-push-gateway` (merged, but see the staleness note under *Relationships*) |
| The end-to-end trigger-to-wake flow across the relay and the gateway together | `architecture-flows-push-notification` (merged, same staleness caveat) |
| The full NIP-PL wire protocol, base-protocol lease semantics, and every transport profile besides the Buzz APNs one | `docs/nips/NIP-PL.md` itself |
| Operator procedure: every environment variable, key rotation, Helm chart release mechanics, alerting thresholds | `docs/push-gateway-deployment.md` |
| The relay-side half of the relay↔gateway boundary (`push_runtime.rs`, `handlers/push_lease.rs`) | A future implementation-reference node for `buzz-relay`'s push runtime, not written here |
| Whether `architecture-containers-push-gateway` and `architecture-flows-push-notification`'s now-stale claims (JWT/provider-token APNs auth, `BUZZ_PUSH_ENABLED_PROFILES`, two app profiles, the credential-refresh metric) get corrected | Whoever owns those two nodes; out of this task's scope per issue #934's own "no broad while-here cleanup" boundary |

**Expected but not verified when this node was written:**

- **Which CI job actually selects and runs `postgres.rs`'s Postgres-backed test
  suite.** `Justfile:346`'s comment states these run in "the dedicated CI job
  below," but the workflow file(s) implementing that lane were not traced for
  this node.
- **Whether the credential-refresh divergence (see *Divergences*) reflects an
  intentional design change the spec text simply hasn't caught up with, or an
  unnoticed implementation gap.** Both readings are consistent with the evidence
  opened for this node; adjudicating between them was out of scope (see the
  authoring plan's *OPEN* note, `launchpad/plans/2026-09-01-issue-934-buzz-push-gateway.md`).
- **Whether every field-level validation branch in `http.rs`'s six non-`deliver`
  handlers (`rotate_endpoint`, `revoke_delegation`, `revoke_installation`, etc.) was
  traced.** `challenge`, `enroll`, `delegate`, and `deliver` were read in full;
  the remaining three mutation handlers were confirmed to exist, be routed, and
  follow the same `verify_installation_assertion` pattern, but were not
  exhaustively re-derived field-by-field for this node.
