---
id: capabilities-notifications-push-lease
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
  - statement: "kind:30350 is the NIP-PL push lease event kind, defined as a parameterized-replaceable, author-only kind whose source event carries endpoint-bearing NIP-44 ciphertext with effective delivery state held in dedicated push lease tables, not in the event itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:104-109"
  - statement: "NIP-PL's Abstract defines the push lease as a stored, installation-scoped, expiring authorization asking a push executor (usually the user's relay) to keep a constrained Nostr filter active after the client's socket closes and to wake one application installation through a platform push transport (APNs, FCM, optionally UnifiedPush) when the filter matches; the wake payload is a fixed, transport-authored reconnect signal carrying no relay-supplied bytes, event ids, content, URLs, or ciphertext, and the client fetches authoritative events over ordinary authenticated REQ after waking."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "NIP-PL states its design goals in order: the push path must not become a shadow feed (no event content transits Apple or Google); notification must be structurally non-amplifying (a lease can only match a narrow, authenticated slice of the stream); installations are sovereign (independently created, replaced, revoked, with no cross-device coupling); and multi-tenant executors preserve community isolation on the push path exactly as relays do on the read path."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "The relay's push_lease handler (crates/buzz-relay/src/handlers/push_lease.rs) exposes validate_envelope, parse_plaintext, validate_subscription, validate_plaintext against a caller-supplied LeaseLimits policy, and an async accept() function that performs this validation before persisting a lease, so a lease is only durable after passing envelope and plaintext policy checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
  - statement: "A Postgres AFTER INSERT trigger on the events table (enqueue_push_match_job, migration 0018_push_match_queue.sql) inserts a crash-safe push_match_queue row for every accepted event whose kind is in {7, 9, 1059, 40007, 46010}, in the same transaction as the event insert, keyed by (community_id, event_id) with ON CONFLICT DO NOTHING for idempotency."
    entry_class: FACT
    evidence:
      - "migrations/0018_push_match_queue.sql"
  - statement: "A later migration (0023_push_match_gate.sql) narrows that same trigger to first take a per-community advisory lock and check for an existing active, endpoint-enabled, unexpired push_leases row before inserting into push_match_queue, so a community with no qualifying lease pays no matcher cost at all; the migration's own comment states this closes a lost-wake race against concurrent lease activation by forcing a total order between the event's commit and a lease-eligibility-changing transaction."
    entry_class: FACT
    evidence:
      - "migrations/0023_push_match_gate.sql"
  - statement: "buzz-push-gateway's own Cargo.toml describes it as a 'Blind, capability-gated NIP-PL gateway for the Buzz mobile app' and its lib.rs module doc calls it a 'Stateful, capability-gated APNs last hop for NIP-PL' -- a standalone service, built and shipped separately from the relay, that is the sole holder of Apple Push Notification service (APNs) provider credentials in the system; relays receive only opaque delegation capabilities from it, never a raw APNs device token."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml:3"
      - "crates/buzz-push-gateway/src/lib.rs:1"
  - statement: "Representative automated verification for this capability's acceptance and delivery path includes push_lease.rs's own #[test] functions (mod tests, starting crates/buzz-relay/src/handlers/push_lease.rs:600) covering envelope/plaintext/generation/quota validation, and push_runtime.rs's gift_wrap_match_requires_self_p_filter_and_recipient (line 619) and gateway_retries_send_the_same_request_id_over_http (line 660) tests covering gift-wrap match authorization and delivery-retry idempotency."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:586-747"
      - "crates/buzz-relay/src/push_runtime.rs:619"
      - "crates/buzz-relay/src/push_runtime.rs:660"
  - statement: "A directory of standalone formal models (docs/formal/nip-pl/: acceptance.py, delivery.py, fixed_payload.py, and mutation-test counterparts mutation_test.py, delivery_mutation.py, fixed_payload_mutation.py) exists alongside the Rust implementation, independently bounded-exhaustively checking lease-acceptance ordering, gateway delivery authority, and the fixed-APNs-payload invariant."
    entry_class: FACT
    evidence:
      - "docs/formal/nip-pl/acceptance.py"
      - "docs/formal/nip-pl/delivery.py"
      - "docs/formal/nip-pl/fixed_payload.py"
  - statement: "As of the recorded revision, no code under mobile/lib or desktop/src references kind:30350, push_lease, PushLease, or NIP-PL/nip-pl in any form -- the client half of this capability (creating, rotating, or revoking a lease; enrolling with the push gateway via App Attest) exists only as normative spec text in docs/nips/NIP-PL.md, not as shipped Buzz client code."
    entry_class: FACT
    evidence:
      - "grep_extended_regex('30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl', paths='mobile/lib desktop/src') -> no matches, run against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-cli's command modules contain no reference to 30350, push_lease, or PushLease -- no agent-facing CLI subcommand exists to create, inspect, or revoke a push lease as of the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_extended_regex('30350|push_lease|PushLease', paths='crates/buzz-cli/src') -> no matches, run against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Root VISION.md's own product-status table marks 'Developer portal, push notifications, culture features' with the 📋 ('designed, not yet built') marker, the same table's least-mature status value, distinct from ✅ ('ships today') and 🚧 ('in active development') used elsewhere in the same table for other rows."
    entry_class: FACT
    evidence:
      - "VISION.md:234"
  - statement: "VISION.md's 📋 marker for 'push notifications' and the absence of any mobile/desktop client code referencing kind:30350 are consistent with each other rather than in conflict: the server-side lease-acceptance, matching, and delivery pipeline is merged and tested, but the end-to-end, user-visible push notification capability additionally requires a client that creates and holds a lease, which does not exist yet -- so the product-level capability is honestly 📋 even though its server-side half has shipped."
    entry_class: INFERENCE
    evidence:
      - "VISION.md:234"
      - "grep_extended_regex('30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl', paths='mobile/lib desktop/src') -> no matches"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "migrations/0018_push_match_queue.sql"
      - "migrations/0023_push_match_gate.sql"
    confidence: 0.8
  - statement: "buzz-push-gateway's AppProfile enum (crates/buzz-push-gateway/src/model.rs) has exactly two variants, BuzzIosProduction (\"buzz-ios-production\") and BuzzIosSandbox (\"buzz-ios-sandbox\") -- no FCM or UnifiedPush variant is defined in code, so only the iOS/APNs transport profile is implemented as of the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs:14-22"
---

# Push lease: capability

Push lease is the capability that lets an installed Buzz mobile client keep
receiving timely notice of new activity in a community even after its
websocket connection closes -- normally impossible on mobile operating
systems, which terminate background sockets within seconds. A client
authorizes this once, by publishing a signed, expiring, revocable `kind:30350`
event (the lease) naming which events it cares about; the relay then watches
on the client's behalf and, when a matching event arrives, wakes the specific
installation through a platform push transport (Apple Push Notification
service today). The wake itself carries no message content -- it is a fixed
reconnect signal -- so the client always re-fetches the real event over an
ordinary authenticated subscription. A user or agent operating a lease-holding
installation therefore gets near-real-time notification of new channel
messages, DMs, and other lease-eligible activity without needing to keep a
socket open continuously.

## Behavior and constraints

NIP-PL states four design goals that bound how this capability may behave,
and the implementation is built to hold them:

- **No shadow feed.** The wake payload is a fixed, transport-authored
  reconnect signal -- never relay-supplied bytes, event ids, event content,
  URLs, or ciphertext. No message content ever transits Apple's (or any
  future provider's) infrastructure; the client always re-fetches the real
  event over an ordinary authenticated `REQ` after waking.
- **Structurally non-amplifying.** A lease can only match a narrow,
  authenticated slice of the event stream (the installation's own
  subscriptions), so a lease cannot be turned into a bulk notification
  channel for arbitrary content.
- **Sovereign installations.** Each `(installation, origin)` pair is its own
  addressable `kind:30350` event, independently created, replaced, and
  revoked, with no cross-device coupling -- losing or rotating one
  installation's lease has no effect on another.
- **Multi-tenant isolation.** A multi-tenant executor (relay) preserves
  community isolation on the push path the same way it does on the read
  path; matching and delivery are scoped per community.

**Delivery is lossy and best-effort, by design.** Duplicate and missed wakes
are both valid outcomes -- the relay's own durable event store, not the wake
signal, is the single source of truth, and the client is expected to
reconcile by re-fetching rather than trusting the wake as a delivery
guarantee.

**Variant: transport profile.** The capability is defined against multiple
platform push transports (APNs, FCM, optionally UnifiedPush) at the protocol
level, but only the iOS/APNs profile is implemented today --
`buzz-push-gateway`'s `AppProfile` enum defines exactly two variants,
`buzz-ios-production` and `buzz-ios-sandbox`, with no FCM or UnifiedPush
variant in code.

## Maturity

**Server-side (relay + gateway): shipped and tested.** The full acceptance,
matching, and delivery pipeline exists in merged code: `kind:30350` is
registered as a NIP-PL event kind (`crates/buzz-core/src/kind.rs:109`), the
relay's `push_lease` handler validates and persists leases
(`crates/buzz-relay/src/handlers/push_lease.rs`), a Postgres trigger enqueues
a crash-safe match job for every eligible event in the same transaction as
its insert (`migrations/0018_push_match_queue.sql`), a later migration gates
that trigger to skip communities with no qualifying lease
(`migrations/0023_push_match_gate.sql`), and a standalone `buzz-push-gateway`
service holds the APNs provider credentials and performs the actual send
(`crates/buzz-push-gateway/Cargo.toml`, `src/lib.rs`). Representative tests
exist at the unit level (`push_lease.rs`'s validation tests,
`push_runtime.rs`'s gift-wrap and retry-idempotency tests) and independently
as bounded-exhaustive formal models (`docs/formal/nip-pl/`).

**Client-facing capability: not yet operational.** As of the recorded
revision, no code under `mobile/lib` or `desktop/src` creates, rotates, or
revokes a lease, or performs the App Attest enrollment the gateway requires --
confirmed by a direct grep for `30350`, `push_lease`, `PushLease`, and
`NIP-PL`/`nip-pl` across both trees, which returned no matches. `buzz-cli`
likewise has no subcommand referencing a push lease. This matches root
`VISION.md`'s own product-status table, which marks "push notifications"
with its least-mature status marker (📋, "designed"), one step behind 🚧
("in active development"). A reader should not infer from the server-side
maturity above that push notifications are end-to-end usable today: the
protocol and its executor-side implementation are done; the client half that
would actually let a user hold a lease is not written yet.

## Boundary

This node does not describe:
- **How the capability is built.** The push gateway's internal design --
  its two AEAD keyrings, App Attest verification, PostgreSQL authority
  store, and deployment/security posture -- is covered by the architecture
  container node for it (`architecture-containers-push-gateway`), not
  restated here.
- **The step-by-step flow through this capability.** The ordered path an
  event takes from relay ingest through matching, delivery-worker
  re-validation, gateway admission, and APNs send -- including every
  failure/retry/abort branch -- is covered by the architecture flow node
  for it (`architecture-flows-push-notification`), not restated here.
- **The full NIP-PL wire protocol.** Exact JSON schemas for the lease
  plaintext, subscription/priority-class semantics, and transport-profile
  details live in `docs/nips/NIP-PL.md`, which is canonical for that and is
  cited above, not duplicated.
- **Gateway deployment, secrets, and operational procedure.** Environment
  variables, key rotation, and the Helm release process are covered by
  `docs/push-gateway-deployment.md`.
- **How the running system is operated day to day** (monitoring, incident
  response) -- outside this capability node's scope; see the `operations`
  corpus surface once populated.

## Relationships

- references: architecture-containers-push-gateway
- references: architecture-flows-push-notification

## Scope and omissions

**This node covers** what the push lease capability lets a user or agent do,
its current maturity split between a shipped/tested server side and a
not-yet-built client side, and its boundary against the architecture,
protocol, and deployment documents that describe how it is built, how one
event flows through it, and how it is operated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the push gateway and relay are built internally | `architecture-containers-push-gateway` |
| The step-by-step event-to-wake flow, including failure/retry behavior | `architecture-flows-push-notification` |
| The full NIP-PL wire protocol | `docs/nips/NIP-PL.md` |
| Gateway deployment, secrets, and operational procedure | `docs/push-gateway-deployment.md` |
| FCM and UnifiedPush transport profiles | Not yet built; the gateway registers only iOS APNs profiles today (per the architecture flow node's own evidence, not independently re-verified here) |
| A CLI or client surface for creating/inspecting/revoking a lease | Does not exist in this repository as of the recorded revision |

**Expected but not verified when this node was written:**
- **Whether a mobile or desktop client implementation has since been
  started on an unmerged branch.** Only the merged tree at the recorded
  revision was checked; an in-progress client PR would not appear in this
  node's evidence.
- **Line-level correctness of the advisory-lock ordering argument** in
  `migrations/0023_push_match_gate.sql`'s own comment (the lost-wake race
  closure). The comment was read and cited as the migration's stated
  rationale; the concurrency proof itself was not independently re-derived
  for this node.
