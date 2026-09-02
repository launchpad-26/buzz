---
id: capabilities-notifications-push-notification
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "NIP-PL's own abstract defines the push lease as a stored, installation-scoped, expiring authorization asking a push executor (usually the user's relay) to keep a constrained Nostr filter active after the client's socket closes, and to wake a specific application installation through a platform push transport when the filter matches; the wake payload is a fixed reconnect instruction authored entirely by the transport service, never relay-supplied bytes, event ids, event content, URLs, or ciphertext, and on wake the client reconnects and fetches authoritative events over normal REQ."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "NIP-PL's Motivation section states its design goals in order: (1) the push path must not become a shadow feed -- no event content transits Apple or Google; (2) notification must be structurally non-amplifying -- a lease can only match a narrow, authenticated slice of the stream; (3) installations are sovereign -- independently created, replaced, and revoked, with no cross-device coupling; (4) multi-tenant executors preserve community isolation on the push path exactly as relays do on the read path."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "kind:30350 is the NIP-PL push lease event kind, registered as KIND_PUSH_LEASE in the relay's kind table."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:109"
  - statement: "The relay side of this capability has shipped: crates/buzz-relay/src/handlers/push_lease.rs validates and persists kind:30350 lease events, and crates/buzz-relay/src/push_runtime.rs implements a continuously-running matcher (run_matcher) and delivery worker (run_delivery_worker) that turn a matching accepted event into a wake and a delivery attempt against the configured push gateway."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "buzz-push-gateway is a standalone binary crate (its own Cargo.toml and Dockerfile.push-gateway, separate from the relay image) that holds APNs credentials and encrypted device-token custody, so relays are never given APNs credentials and hold only opaque delivery capabilities."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml"
      - "Dockerfile.push-gateway"
      - "docs/push-gateway-deployment.md"
  - statement: "As of the recorded revision, neither mobile/lib nor desktop/src contains any code that creates, rotates, or revokes a push lease, performs Apple App Attest installation enrollment, or references kind:30350 -- the client half of this capability exists only as normative spec text in docs/nips/NIP-PL.md, not as shipped Buzz client code."
    entry_class: FACT
    evidence:
      - "grep_recursive('push.notif|pushNotif|30350|push_lease|PushLease', paths='desktop/src mobile/lib') -> no matches, run against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Root VISION.md's Status table marks 'Developer portal, push notifications, culture features' with the same not-yet-started marker (📋) used elsewhere in that table for work whose spec is in review but not built, distinct from the in-progress marker (🚧) used for the mobile client row and the shipped marker (✅) used for rows such as core relay and the desktop client."
    entry_class: FACT
    evidence:
      - "VISION.md:234"
      - "VISION.md:220"
      - "VISION.md:232"
  - statement: "VISION.md's not-yet-started marker for push notifications is stale relative to the relay- and gateway-side code: push_lease.rs, push_runtime.rs and the buzz-push-gateway crate are substantial shipped implementation, not a spec in review, but no client integrates them, so the capability is not yet reachable by any user through a shipped Buzz application -- the honest maturity statement is 'in progress' (backend built, client integration not started), not 'shipped' and not 'not yet started' in the sense the rest of that table's 📋 rows mean."
    entry_class: INFERENCE
    evidence:
      - "VISION.md:234"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-push-gateway/Cargo.toml"
    confidence: 0.85
  - statement: "The push-gateway's transport-profile enum (ApplicationProfile in crates/buzz-push-gateway/src/model.rs) currently defines exactly two variants, BuzzIosProduction and BuzzIosSandbox, both APNs; no FCM or UnifiedPush variant exists in that enum."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs:21-22"
  - statement: "NIP-PL's own FCM section states a future FCM profile MUST define one gateway-owned constant data message with identical noninterference semantics, and that until that constant and its wire tests are registered, FCM is not a conforming v1 public-gateway profile; its UnifiedPush section states UnifiedPush is not a conforming public-gateway profile in v1 because arbitrary distributor endpoints and message bodies do not meet the fixed-payload authority boundary."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "crates/buzz-relay/src/handlers/push_lease.rs contains unit tests (ten #[test] functions from line 612 onward) covering lease tag/plaintext/generation/quota validation, and crates/buzz-relay/src/push_runtime.rs contains gift_wrap_match_requires_self_p_filter_and_recipient and gateway_retries_send_the_same_request_id_over_http, exercising the gift-wrap authorization narrowing and delivery-retry idempotency this capability depends on."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:586-747"
      - "crates/buzz-relay/src/push_runtime.rs:619"
      - "crates/buzz-relay/src/push_runtime.rs:660"
  - statement: "docs/formal/nip-pl/ contains standalone formal models (acceptance.py, delivery.py, fixed_payload.py, and mutation-test counterparts mutation_test.py, delivery_mutation.py, fixed_payload_mutation.py) independent of the Rust test suite, bounded-exhaustively checking lease-acceptance ordering, gateway delivery authority, and the fixed-APNs-payload invariant."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/acceptance.py"
      - "docs/formal/nip-pl/delivery.py"
      - "docs/formal/nip-pl/fixed_payload.py"
      - "docs/formal/nip-pl/mutation_test.py"
      - "docs/formal/nip-pl/delivery_mutation.py"
      - "docs/formal/nip-pl/fixed_payload_mutation.py"
  - statement: "No corpus node under launchpad/docs/corpus/interfaces-events exists on origin/launchpad at the recorded revision -- the interfaces-events corpus surface is unpopulated, so this capability has no interface node it could reference for the kind:30350 event boundary."
    entry_class: FACT
    evidence:
      - "absent:launchpad/docs/corpus/interfaces-events@338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "launchpad/docs/corpus/architecture/flows/push-notification.md (id: architecture-flows-push-notification), launchpad/docs/corpus/architecture/containers/relay.md (id: architecture-containers-relay), and launchpad/docs/corpus/architecture/containers/push-gateway.md (id: architecture-containers-push-gateway) all exist on origin/launchpad at the recorded revision, each with status: draft, and are therefore valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/architecture') -> includes flows/push-notification.md, containers/relay.md, containers/push-gateway.md, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
---

# Push notification: capability

Buzz can wake an installed client application through its platform's push
transport (currently Apple APNs) when a message or event that installation is
authorized to read arrives while its connection to the relay is closed. The
wake carries no relay content, ids, or ciphertext -- the client learns only
that *something* changed for it, reconnects, and fetches the authoritative
event over an ordinary authenticated `REQ`. This lets a person keep their
phone or laptop asleep, backgrounded, or offline without missing that a
message arrived, while the platform vendor delivering the wake never sees
what it was.

The primary actor is a human user of a mobile or desktop Buzz client, notified
through their operating system's own push surface. Behind that experience:
the client installation (which creates, rotates, and revokes the lease that
authorizes its own wakes), the relay (which accepts the lease, matches
incoming events against it, and requests delivery), the push gateway (which
holds the platform credentials and performs the actual send), and the
platform transport itself (Apple's APNs, external to Buzz).

## Maturity

**In progress: relay- and gateway-side infrastructure has shipped; no client
integrates it yet.** `crates/buzz-relay/src/handlers/push_lease.rs` (lease
acceptance) and `crates/buzz-relay/src/push_runtime.rs` (matching and
delivery) are real, tested relay code, and `buzz-push-gateway` is a shipped,
separately deployed binary crate holding APNs credentials. But as of the
recorded revision neither `mobile/lib` nor `desktop/src` creates, rotates, or
revokes a lease or performs the App Attest enrollment a client needs to
receive a wake -- so no shipped Buzz application can currently exercise this
capability end to end. Root `VISION.md`'s own Status table marks "push
notifications" with its not-yet-started marker; that undercounts the
relay/gateway work already merged, but is accurate about the capability as a
whole not yet being reachable by a user, because the piece a user actually
touches -- the client -- has not been built.

## Behavioral rules and constraints

- **The wake payload is fixed and content-free.** The gateway sends one
  compiled-in reconnect constant for every delivery; it is never derived from
  the matched event, and no relay-supplied byte, event id, or content ever
  enters it. This is a structural rule, not an operational default -- it is
  what keeps the push transport from becoming a second content channel that
  Apple or Google can read.
- **A lease authorizes only a narrow, authenticated slice of the stream.**
  Creating or reading a `kind:30350` lease requires NIP-42 connection
  authentication with the authenticated pubkey equal to the lease's own
  author; this bounds what any single lease can ever be matched against, so a
  compromised or malicious lease cannot be turned into a firehose.
- **Delivery is lossy and best-effort, by design, not by defect.** NIP-PL
  defines duplicate and missed wakes as both valid; the relay's event store
  remains the single source of truth, and the client's fetch after waking is
  what actually delivers content, not the wake itself.
- **Installations are sovereign.** A lease is scoped to one installation; the
  spec is explicit that installations are created, replaced, and revoked
  independently, with no cross-device coupling.
- **Multi-tenant isolation applies to the push path as it does to reads.**
  A push executor serving more than one community must preserve the same
  isolation the read path already guarantees.

## Platform variants

- **APNs (iOS) is the only conforming v1 transport profile.** The gateway's
  own transport-profile enum currently defines exactly two APNs variants
  (production and sandbox); this is the profile actually shipped.
- **FCM and UnifiedPush are named in the protocol but not conforming
  profiles.** NIP-PL reserves both as future transport profiles, but states
  explicitly that FCM needs its own registered fixed-payload constant and
  wire tests before it conforms, and that UnifiedPush's arbitrary
  distributor endpoints do not meet the fixed-payload authority boundary
  without a similarly registered profile. Neither exists in the gateway's
  code today.

## Verification

The two guarantees this capability rests on -- that a wake carries no relay
content, and that a lease can only ever be matched against a narrow,
authenticated slice of the stream -- are each backed by tests, not just
spec text: `push_lease.rs`'s validation tests cover lease tag, plaintext,
generation, and quota checks, and `push_runtime.rs`'s
`gift_wrap_match_requires_self_p_filter_and_recipient` and
`gateway_retries_send_the_same_request_id_over_http` cover the gift-wrap
narrowing and delivery-retry idempotency this capability depends on. The
fixed-payload and lease-acceptance invariants are additionally checked
independently of the Rust suite by standalone formal models under
`docs/formal/nip-pl/`. The step-by-step ordering these tests exercise is
catalogued in `architecture-flows-push-notification`; this node names them
only to show the capability's own guarantees are demonstrated, not to
re-narrate the flow.

## Boundary

This node does not describe:
- **How the capability is built.** The relay's lease-acceptance, matching,
  and delivery-worker implementation is `architecture-containers-relay`'s
  and `architecture-flows-push-notification`'s territory; the gateway's own
  design (APNs credential custody, App Attest verification, its six-table
  authority store) is `architecture-containers-push-gateway`'s.
- **The interface this capability is exposed through.** `kind:30350` is a
  Nostr event kind, not a CLI command group or HTTP route group, and no
  corpus interface node exists yet for it -- the `interfaces-events` surface
  is currently unpopulated in this corpus.
- **The step-by-step path one event takes from ingest to device wake.**
  That ordered sequence, its trust-boundary crossings, and its failure/abort
  behavior are `architecture-flows-push-notification`'s subject, not
  restated here.
- **How the gateway and relay are operated in production** -- deployment,
  secrets, and alerting live in `docs/push-gateway-deployment.md`; no corpus
  operations node covers this yet.
- **The client-side experience once a client exists.** Nothing in this
  repository yet defines what a user sees or configures on a mobile or
  desktop client for this capability, because no client implements it.

## Relationships

- references: architecture-flows-push-notification
- references: architecture-containers-relay
- references: architecture-containers-push-gateway

## Scope and omissions

**This node covers** what push notification lets a user experience (a
platform wake with no relay content, followed by a normal authenticated
fetch), who the primary actor and supporting parties are, the capability's
current product-level maturity, the behavioral rules and constraints NIP-PL
and the shipped code establish, and the platform-profile variants that do and
do not conform today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (relay, gateway architecture) | `architecture-containers-relay`, `architecture-containers-push-gateway` |
| The step-by-step flow from event ingest to device wake | `architecture-flows-push-notification` |
| The interface boundary for `kind:30350` | not yet drafted; `interfaces-events` is unpopulated in this corpus |
| Gateway/relay operations (deployment, secrets, alerting) | `docs/push-gateway-deployment.md`; no corpus operations node yet |
| The mobile/desktop client experience | not yet built in this repository |

**Expected but not verified when this node was written:**
- **No mobile or desktop client implementation exists to observe.** Every
  claim about what a user experiences is drawn from NIP-PL's normative text
  and the shipped relay/gateway code's behavior, not from exercising a real
  client wake -- there is no client to exercise.
- **VISION.md's Status table marker was read once, as of its own last
  commit at the recorded revision; it is a living document and may change
  independently of this node's recorded revision.**
