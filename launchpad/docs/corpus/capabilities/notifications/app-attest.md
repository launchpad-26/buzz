---
id: capabilities-notifications-app-attest
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-push-gateway authenticates its six client-facing installation/delegation routes (challenge issuance, enrollment, delegation, endpoint rotation, delegation revocation, installation revocation) with Apple App Attest rather than a Nostr key, while the seventh route (relay-facing delivery) is authenticated with NIP-98 -- App Attest is the client-to-gateway trust boundary, distinct from the relay-to-gateway boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "App Attest verification is implemented by delegating to the third-party crate `appattest` (version 0.1.1), not by a from-scratch cryptographic implementation in this repository; buzz-push-gateway's own app_attest.rs module is a narrow wrapper around that crate's Attestation and Assertion types."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml"
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "Enrollment (first use) requires a fresh attestation: the gateway issues a random 32-byte challenge good for 300 seconds (POST /v1/installations/challenges), the client signs a canonical JSON transcript over that challenge plus every authority-bearing enrollment field (key id, app profile, endpoint, endpoint epoch, expiry) with the device's App Attest key, and AppAttestVerifier::verify_attestation checks the resulting CBOR attestation against the app id and a pinned Apple App Attest root certificate before the gateway will create an installation row."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "Every subsequent authority-changing call (delegate, rotate_endpoint, revoke_delegation, revoke_installation) re-authenticates with a fresh App Attest assertion rather than the original attestation: verify_installation_assertion loads the stored installation, verifies a new per-request signed transcript against the installation's stored public key and previously stored assertion counter via AppAttestVerifier::verify_assertion, then consumes the challenge and advances the counter -- so each mutating request is its own attested event, not a session token presented repeatedly."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "A challenge is single-use and time-boxed: consume_challenge deletes the row identified by challenge id, a SHA-256 hash of the challenge value, and an expiry check in one statement, and treats anything other than exactly one deleted row as rejection -- so a replayed, mismatched, or expired challenge value fails closed rather than being silently accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "The assertion counter is strictly monotonic and enforced with an optimistic-concurrency guard: advance_assertion_counter rejects outright if the new counter is not greater than the previous one, and its SQL UPDATE additionally matches on the previous counter value, so a stale or replayed assertion (same or lower counter, or a concurrent racing update) cannot advance the installation's state."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "The verifier is constructed once at startup and refuses to build if the configured app id is empty or if the configured Apple root certificate's SHA-256 digest does not match a compiled-in constant -- the trust anchor is pinned in the binary, not merely read from operator-supplied configuration at face value."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "The gateway requires BUZZ_PUSH_APP_ATTEST_APP_ID and BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH at startup and refuses to start without them, and a unit test (malformed_security_configuration_fails_startup) explicitly asserts that an empty BUZZ_PUSH_APP_ATTEST_APP_ID fails Config::from_map."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "Attestation and assertion payloads are size-bounded before any decoding is attempted -- 16 KiB for an attestation, 1 KiB for an assertion -- and CBOR/base64 decode failures, an out-of-range payload, or a malformed authenticatorData map (the assertion counter extractor accepts only a closed two-key {authenticatorData, signature} CBOR map with a 37-byte authenticatorData value) all fail closed to the same opaque 'invalid app attestation or assertion' error, so no parser-internal detail is exposed to a caller probing the boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/app_attest.rs"
  - statement: "As of the recorded revision, no code under mobile/lib or desktop/src creates an App Attest attestation or assertion, calls any of the six App Attest-authenticated gateway routes, or otherwise performs installation enrollment -- a case-insensitive search for 'attest', 'push_lease', and '30350' across both trees matches only an unrelated NIP-OA 'owner attestation' concept and an unrelated 'age attestation' join-policy field, never Apple App Attest or push installation code -- so App Attest verification is shipped on the gateway side with no shipped Buzz client that invokes it yet."
    entry_class: FACT
    evidence:
      - "grep_recursive_case_insensitive('attest|push_lease|30350', paths='mobile/lib desktop/src') -> matches only mobile/lib/shared/crypto/nip_oa.dart (NIP-OA 'Owner Attestation') and five desktop files using 'ageAttestationRequired' (join-policy age gate), zero App Attest or push-installation matches, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "No dedicated automated test in buzz-push-gateway directly exercises AppAttestVerifier::verify_attestation or verify_assertion (app_attest.rs itself carries no #[test] functions); the only App Attest-adjacent test coverage found is config.rs's startup-validation test for an empty app id and postgres.rs's own tests for unrelated delivery-replay behavior -- the challenge single-use property and the counter-monotonicity property are established by reading consume_challenge and advance_assertion_counter's SQL, not by an automated test asserting either directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/app_attest.rs"
      - "crates/buzz-push-gateway/src/config.rs"
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "The gateway currently enables only iOS APNs application profiles, and FCM/UnifiedPush are documented elsewhere as not-yet-conforming v1 profiles pending a separately registered fixed payload -- App Attest itself is an Apple-only device-attestation mechanism with no analogous device-integrity check wired up for a non-Apple profile in this repository."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
---

# App Attest: capability

Buzz's push-notification gateway (`buzz-push-gateway`) can cryptographically confirm
that a party calling its installation-management routes is a genuine instance of the
Buzz iOS app running on genuine Apple hardware, using Apple's App Attest service,
before it will create, delegate, rotate, or revoke a push installation. This is what
lets the gateway hold Apple Push Notification service (APNs) device tokens and issue
delivery capabilities to relays without accepting an installation claim from an
arbitrary caller — the capability a product stakeholder would recognize as "only real
app installs on real devices can register for push," independent of how any single
route is wired.

## Maturity

**Shipped on the server side; not yet reachable from a shipped Buzz client.**
`buzz-push-gateway`'s `app_attest.rs` and `http.rs` implement attestation verification
(enrollment) and assertion verification (every subsequent authority-changing call) in
production code, gated by required startup configuration
(`BUZZ_PUSH_APP_ATTEST_APP_ID`, `BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH`) that fails
closed if missing or malformed. However, no code under `mobile/lib` or `desktop/src`
in this repository creates an attestation, creates an assertion, or calls any of the
six App Attest-authenticated routes — confirmed by a direct search of both trees at
the recorded revision. The capability is real and enforced on the gateway; nothing in
this repository yet drives it from a client.

## Boundary

This node does not describe:
- **How the push gateway is built as a container** — its technology, its ownership
  boundary against the relay, its full inbound/outbound interface list, and its
  deployment/data/security posture. See `architecture-containers-push-gateway`.
- **The end-to-end push-notification flow** this capability is a precondition for —
  trigger, ordered interactions from event ingest to device wake, and failure/rollback
  behavior for delivery itself. See `architecture-flows-push-notification`.
- **The full installation/delegation/enrollment wire protocol** — exact request/
  response JSON shapes for every route, endpoint epochs, quota parameters. That detail
  belongs to a future interfaces-events corpus node, not written yet, and to
  `crates/buzz-push-gateway/src/http.rs` itself as the source of truth in the meantime.
- **NIP-98**, the separate relay-to-gateway trust boundary used only for the delivery
  route (`POST /v1/deliveries/apns`). App Attest and NIP-98 authenticate two different
  callers (client vs. relay) on two different route groups within the same container;
  this node covers only the App Attest half.
- **Apple's own App Attest service or the `appattest` crate's internal cryptographic
  verification correctness.** This node covers how Buzz *uses* App Attest — which
  routes require it, what is checked before an installation exists or changes, and
  what is enforced closed by default — not Apple's attestation format or the
  third-party crate's own implementation, which are outside this repository.

## Behavioral rules, constraints, and variants

- **Two distinct proofs, one mechanism.** *Attestation* (enrollment only, first use of
  a device's App Attest key against this app) and *assertion* (every later
  authority-changing call) are verified by different `AppAttestVerifier` methods, but
  both are anchored to the same pinned Apple App Attest root certificate and app id
  set once at process startup.
- **Attestation is checked against a full enrollment transcript.** The signed
  transcript covers every authority-bearing enrollment field (challenge, key id, app
  profile, endpoint, endpoint epoch, expiry) — not just the challenge — so an attacker
  who captures a valid attestation for one set of enrollment parameters cannot replay
  it against different parameters.
- **Assertions are per-request, not session tokens.** Each mutating call after
  enrollment signs its own fresh transcript and its own fresh challenge; there is no
  reusable bearer credential issued to the client for repeated authority-changing
  calls.
- **Challenges are single-use and short-lived.** A challenge is good for 300 seconds
  from issuance and is consumed atomically (id + value hash + expiry, in one
  statement) the moment it is used successfully; a mismatched, reused, or expired
  challenge is rejected, never silently accepted.
- **The assertion counter enforces anti-replay via strict monotonicity.** A stale or
  replayed assertion whose counter is not strictly greater than the installation's
  stored counter is rejected; the update additionally matches on the previous counter
  value as an optimistic-concurrency guard against a concurrent racing request.
- **The trust anchor is pinned in the binary, not merely operator-configured.** The
  verifier refuses to construct unless the configured Apple root certificate hashes to
  a compiled-in SHA-256 constant, so a misconfigured or substituted root certificate
  fails startup rather than being trusted at face value.
- **Payloads are bounded and failures are opaque.** Attestation and assertion payloads
  are size-capped (16 KiB / 1 KiB) before decoding, and every failure mode — bad
  base64, bad CBOR, an out-of-range size, a malformed authenticator-data map, a failed
  cryptographic check — collapses to the same generic invalid-attestation error, so a
  caller probing the boundary learns nothing about which check failed.
- **Variant: platform is Apple-only today.** App Attest is an Apple-specific
  mechanism; the gateway's other enabled/planned push profiles (FCM, UnifiedPush) are
  documented elsewhere as not yet conforming v1 profiles, and neither has an analogous
  device-integrity check wired up in this repository. There is no cross-platform
  variant of this capability yet — it is App Attest or nothing.

## Relationships

- references: architecture-containers-push-gateway
- references: architecture-flows-push-notification

## Scope and omissions

**This node covers** what App Attest authenticates within `buzz-push-gateway` (six
client-facing installation/delegation routes, distinct from the relay-facing NIP-98
route), the two-proof attestation/assertion shape, the challenge single-use and
counter-monotonicity anti-replay properties, root-certificate pinning, startup
configuration enforcement, payload bounds and opaque failure behavior, and the
capability's current maturity (shipped server-side, not yet driven by any shipped
Buzz client).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the push gateway is built as a container (technology, ownership boundary, full interface list, deployment/data/security posture) | `architecture-containers-push-gateway` |
| The end-to-end push-notification flow this capability is a precondition for | `architecture-flows-push-notification` |
| The full installation/delegation wire protocol (exact request/response shapes, quota parameters) | A future interfaces-events corpus node — not written yet |
| NIP-98, the relay-to-gateway trust boundary | Not this node — a different authentication mechanism on a different route |
| Apple's App Attest service internals or the third-party `appattest` crate's own cryptographic correctness | Outside this repository |
| Whether this fork (launchpad-26/buzz) operates a live push-gateway deployment | Not verified here — consistent with the gap already recorded in `architecture-containers-push-gateway` |

**Expected but not verified when this node was written:**
- **No dedicated automated test exercises `AppAttestVerifier::verify_attestation` or
  `verify_assertion` directly.** `app_attest.rs` carries no `#[test]` functions of its
  own; the challenge single-use and counter-monotonicity properties described above
  are established by reading `consume_challenge` and `advance_assertion_counter`'s SQL
  in `postgres.rs`, not by an automated test asserting either property in isolation.
  The only App Attest-adjacent test found is `config.rs`'s startup-validation test for
  an empty app id.
- **Real Apple App Attest attestation/assertion payloads were not exercised.** This
  node describes the verification code path and its enforced constraints from reading
  the implementation; it does not certify interoperability against a real device's
  App Attest output, which would require a real enrolled iOS installation this
  repository does not yet have.
