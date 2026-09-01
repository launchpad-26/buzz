---
id: capabilities-notifications-endpoint-installation
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "NIP-PL's public-gateway profile section names the APNs token registered with the gateway the installation endpoint, states it never leaves gateway custody after enrollment, and its Base Protocol section (Lifecycle) separately normatively requires that platform-rotated endpoint tokens be re-published at an incremented generation rather than treated as a new installation."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md:267"
      - "docs/nips/NIP-PL.md:245"
  - statement: "NIP-PL's public-gateway HTTP section defines Installation enrollment as POST /v1/installations (App-Attest-verified attestation, producing an installation_handle) and defines endpoint rotation as a separate POST /v1/installations/endpoint call (App-Attest-verified assertion, requiring new_endpoint_epoch == endpoint_epoch + 1) against an existing installation_handle -- two distinct operations under one capability, not one operation."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md:301-320"
      - "docs/nips/NIP-PL.md:343-353"
  - statement: "The gateway's enroll handler (POST /v1/installations) validates wire version, that endpoint_epoch equals 1, that expires_at falls strictly between now and now + the configured max installation lifetime, and that the requested app_profile is in the configured enabled-profile set, before verifying an Apple App Attest attestation against a domain-prefixed (buzz.push.enroll.v1) ordered transcript and persisting a NewInstallation record with an AEAD-sealed token ciphertext and a profile-scoped SHA-256 token fingerprint."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:156-236"
  - statement: "The gateway's rotate_endpoint handler (POST /v1/installations/endpoint) requires new_endpoint_epoch to equal endpoint_epoch + 1 exactly, looks up the existing installation, verifies an App Attest assertion against a domain-prefixed (buzz.push.rotate-endpoint.v1) transcript and the installation's already-attested public key, then re-seals the new token and calls AuthorityStore::rotate_endpoint with the new ciphertext and fingerprint."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:382-446"
  - statement: "The gateway's revoke_installation handler (POST /v1/installations/revoke) requires the same incremented-epoch shape as rotation, verifies an App Attest assertion domain-prefixed buzz.push.revoke-installation.v1, then calls AuthorityStore::revoke_installation, whose in-memory implementation sets the installation's revoked flag and bumps its endpoint_epoch; the installation-lookup path used by every other installation-scoped route filters out any installation with revoked == true, which is the mechanism that makes a revoked installation stop resolving for delegation, rotation, or further revocation rather than an explicit per-delegation invalidation step."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:506-548"
      - "crates/buzz-push-gateway/src/authority.rs:256"
      - "crates/buzz-push-gateway/src/authority.rs:367-384"
  - statement: "Every installation-mutating route (enroll's attestation; rotate_endpoint's, revoke_installation's, and delegate's assertions) is bound to a server-issued, single-use, 300-second-lifetime challenge that verify_installation_assertion consumes via AuthorityStore::consume_challenge only after successful cryptographic verification, and every assertion route additionally requires the installation's App-Attest assertion counter to strictly increase (advance_assertion_counter), so a captured attestation or assertion cannot be replayed outside the request it was signed for or after a newer assertion has already advanced the counter."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:238-280"
      - "crates/buzz-push-gateway/src/authority.rs:261-280"
  - statement: "The gateway holds the raw APNs token only long enough to seal it: TokenKeyring::seal (used by both enroll and rotate_endpoint) encrypts the token with AES-256-GCM under a self-describing, key-id-tagged ciphertext scheme that supports decrypt-only predecessor keys during rotation, and the plaintext token is never itself part of the persisted NewInstallation/rotate_endpoint record -- only the ciphertext and a one-way SHA-256 fingerprint are stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/token.rs:1-13"
      - "crates/buzz-push-gateway/src/http.rs:208-221"
      - "crates/buzz-push-gateway/src/http.rs:428-439"
  - statement: "BUZZ_PUSH_MAX_INSTALLATION_LIFETIME_SECONDS bounds how far in the future an enrollment's requested expires_at may be set, and BUZZ_PUSH_ENABLED_PROFILES is a required, non-empty set of app_profile values gating which profile enroll will accept; the gateway refuses to start if either is missing, malformed, or (for the profile set) empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs:120-153"
  - statement: "As of the recorded revision, no test in this repository directly exercises the enroll, rotate_endpoint, or revoke_installation HTTP handlers; authority.rs's own #[cfg(test)] module (retry_releases_request_id_but_burns_auth_event, terminal_outcome_burns_request_id) covers only delivery-authorization/replay behavior against a pre-seeded installation/delegation fixture, not the enrollment, rotation, or revocation code paths themselves, and no crates/buzz-push-gateway/tests/ integration-test directory exists."
    entry_class: FACT
    evidence:
      - "grep_recursive('fn test_', path='crates/buzz-push-gateway/src/http.rs') -> no matches"
      - "crates/buzz-push-gateway/src/authority.rs:490-566"
      - "path_exists('crates/buzz-push-gateway/tests') -> false"
  - statement: "As of the recorded revision, no mobile (Flutter) or desktop (Tauri) client code in this repository creates, rotates, or revokes a push installation, or calls any /v1/installations* gateway route -- the client half of endpoint installation exists only as normative spec text in docs/nips/NIP-PL.md, not as shipped Buzz client code. This is the same finding already recorded independently by the merged architecture-flows-push-notification flow node."
    entry_class: FACT
    evidence:
      - "grep_recursive('30350|push_lease|PushLease|installation|App.?Attest|app_attest', paths='mobile/lib desktop/src') -> no matches"
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
  - statement: "VISION.md's root Status table marks the combined row 'Developer portal, push notifications, culture features' with the same 📋 marker used elsewhere in that table for designed-but-not-built roadmap items; VISION_PROJECTS.md's separate Capability|Status table does not list push notifications as a row at all."
    entry_class: FACT
    evidence:
      - "VISION.md:234"
      - "grep_case_insensitive('push notif', path='VISION_PROJECTS.md') -> no matches"
  - statement: "VISION.md's 📋 marker for push notifications reads as stale for the gateway's installation-enrollment surface specifically: the enroll/rotate_endpoint/revoke_installation handlers, App Attest verification, and encrypted token custody described above are real, merged, non-trivial server-side code, not only a design document -- but the entire client half (the only place a real device could actually perform an installation) is still unimplemented and untested end-to-end, so the capability as a whole is more accurately in progress on the server side and not yet started on the client side, rather than uniformly 'designed'."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:156-236"
      - "VISION.md:234"
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-flows-push-notification
  - type: references
    target: architecture-containers-push-gateway
---

# Endpoint installation: capability

Buzz lets a client (today, specced only for the iOS/APNs public-gateway
profile) register a push endpoint with `buzz-push-gateway` -- proving it is a
genuine app installation via Apple App Attest, and receiving back a stable
`installation_handle` the client subsequently uses to rotate that endpoint
when the platform issues a new token, or to revoke the installation
entirely. This is the enrollment step that makes the rest of NIP-PL's push
lease machinery possible: a relay can only mint a delivery capability
(`endpoint_grant`) against an installation that has already completed this
capability's enrollment, and a client cannot receive a wake at all until it
has done so.

## Maturity

**In progress, and unevenly so.** The gateway-side implementation --
`POST /v1/installations` (enroll), `POST /v1/installations/endpoint` (rotate),
and `POST /v1/installations/revoke` (revoke), each App-Attest-verified and
backed by AEAD-sealed token custody -- is real, merged code, not only design
prose. But no client in this repository (`mobile/lib` or `desktop/src`) has
any code that performs App Attest enrollment or calls any of these routes,
and no test in the repository exercises the enroll/rotate/revoke handlers
themselves. VISION.md's root Status table marks the whole "push
notifications" line 📋 (designed); that marker is accurate for the missing
client half but understates the gateway half, which has already shipped.
Treat this capability as **gateway-implemented, client-unbuilt, and
handler-level-untested** rather than as a single uniform maturity state.

## Behavior and constraints

Endpoint installation has three variants, all scoped to one
`installation_handle` once enrollment succeeds:

- **Enroll.** A client proves genuine-app-installation status via an Apple
  App Attest attestation over a domain-prefixed transcript, and registers
  its APNs token (`endpoint`) at `endpoint_epoch: 1` for one of the
  operator-enabled `app_profile` values. The gateway rejects an expiry
  outside `(now, now + max_installation_lifetime_seconds]` and a profile not
  in `BUZZ_PUSH_ENABLED_PROFILES`.
- **Rotate.** When the platform reissues a token, the client re-registers it
  under the *same* `installation_handle` with `new_endpoint_epoch` required
  to equal `endpoint_epoch + 1` exactly -- a gap or non-increment is
  rejected. Authorization is by App Attest *assertion* (not a fresh
  attestation) against the key established at enrollment.
- **Revoke.** The same epoch-increment shape invalidates the installation
  outright; because every other installation-scoped route looks the
  installation up through a query that filters out `revoked == true`, a
  revoked installation stops resolving for further rotation, delegation, or
  re-revocation without a separate cascade step.

**Constraints that hold across all three:** every assertion-authenticated
call is bound to a single-use, 300-second-lived, server-issued challenge,
consumed only after cryptographic verification succeeds; the installation's
App Attest assertion counter must strictly increase call over call, so a
captured assertion cannot be replayed once a newer one has landed; and the
raw APNs token is never persisted -- only an AEAD ciphertext (decryptable
under key rotation) and a one-way fingerprint are stored, so a database
compromise does not expose live device tokens without the separate token
keyring's key material.

## Boundary

This node does not describe:
- **How the gateway container is built** (its technology, deployment,
  security boundaries, and connected systems as a whole) -- see the
  architecture node for `architecture-containers-push-gateway`.
- **The full push-notification flow** (event ingest, matching, wake
  enqueue, delivery, and retry/failure handling) that endpoint installation
  is a precondition for -- see the flow node for
  `architecture-flows-push-notification`. That node's own step 1 already
  narrates installation enrollment as one precondition of the larger flow;
  this node is the capability-level detail behind that one step.
- **The full NIP-PL wire protocol** (exact request/response JSON shapes,
  every closed error body, transcript byte construction) -- `docs/nips/NIP-PL.md`
  is canonical for that; this node states what the capability lets a client
  do, not its byte-level contract.
- **Delegation issuance, delivery, or lease matching** -- those are
  downstream of a completed installation and are the flow/gateway-container
  nodes' territory, not this one's.

## Relationships

- references: `architecture-flows-push-notification` -- the broader flow this
  capability's enrollment step is a precondition of.
- references: `architecture-containers-push-gateway` -- the container that
  implements this capability's HTTP surface as part of its own
  responsibility.

## Scope and omissions

**This node covers** what a client can do because endpoint installation
exists: register a new installation (enroll), replace its registered
endpoint when the platform rotates the underlying token (rotate), and
permanently invalidate the installation (revoke) -- each authenticated by
Apple App Attest and protected by a single-use challenge and a
strictly-increasing assertion counter, with the raw APNs token never
persisted in plaintext.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The gateway container's full responsibility, deployment, and security model | `architecture-containers-push-gateway` |
| The end-to-end push-notification flow this capability is a precondition of | `architecture-flows-push-notification` |
| The NIP-PL wire protocol byte-for-byte | `docs/nips/NIP-PL.md` |
| Delegation issuance and delivery | Not yet a dedicated corpus node |

**Expected but not verified when this node was written:**
- **No client implementation exists to verify against.** Every claim about
  what a client does when installing an endpoint is sourced from the
  gateway's server-side validation and from NIP-PL's normative text, not
  from observing an actual mobile or desktop client performing enrollment,
  because no such client code exists in this repository yet.
- **No handler-level test exists for enroll, rotate_endpoint, or
  revoke_installation.** The behavior described above is read directly from
  the handler and `AuthorityStore` implementations, not confirmed by a
  passing test that exercises those specific code paths end to end.
- **FCM/UnifiedPush endpoint installation is out of scope entirely.** NIP-PL
  registers only the iOS/APNs profile as conforming in v1; this node
  describes that profile only, per the same scoping the flow and container
  nodes already record.
