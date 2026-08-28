---
id: architecture-flows-push-notification
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "kind:30350 is the NIP-PL push lease event kind, registered in the relay's kind table."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:109"
  - statement: "NIP-PL defines the push lease as a stored, installation-scoped, expiring authorization that lets a push executor keep a constrained filter active after the client's socket closes and wake the client through a platform push transport; the push payload is a fixed transport-authored reconnect signal, never relay-supplied content, and the client fetches authoritative events over ordinary authenticated REQ after waking."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "buzz-push-gateway is a standalone service (built via Dockerfile.push-gateway) that holds APNs credentials and encrypted device-token custody; relays are never given APNs credentials and hold only opaque delivery capabilities."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "The relay's push_lease handler (crates/buzz-relay/src/handlers/push_lease.rs) validates a kind:30350 event's public tags and NIP-44-encrypted plaintext against a server-resolved descriptor policy (LeaseLimits) before calling accept(), which persists the lease atomically."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
  - statement: "A Postgres AFTER INSERT trigger on the events table (enqueue_push_match_job) enqueues a push_match_queue row for every accepted event whose kind is in the push-eligible allow-list (7, 9, 1059, 40007, 46010); this runs inside the same transaction as event insertion, so every durable producer is covered, including internal paths that bypass live in-process dispatch."
    entry_class: FACT
    evidence:
      - "migrations/0018_push_match_queue.sql"
  - statement: "A later migration narrowed the trigger (T1b push gate) to skip the push_match_queue insert entirely for communities with no active, endpoint-enabled, unexpired push lease, using a per-community advisory lock to close a lost-wake race against concurrent lease activation."
    entry_class: FACT
    evidence:
      - "migrations/0023_push_match_gate.sql"
  - statement: "The relay's matcher (run_matcher in push_runtime.rs) continuously claims due push_match_queue batches, evaluates each event's filter matches against the community's active leases and self-#p gift-wrap authorization, and enqueues wake requests; it also periodically reaps exhausted/poisoned match jobs on a separate interval off the claim path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "The relay's delivery worker (run_delivery_worker in push_runtime.rs) continuously claims due wakes per community and calls deliver_one, which re-validates the wake (active lease, expiration, endpoint generation, current read authorization) twice -- once before and once after a membership check -- before sending, closing a race between membership I/O and lease replacement."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "Before transport, deliver_one acquires a community-scoped serving-write guard from buzz_deletion and suppresses delivery if that guard cannot be acquired or verified, so a community mid-deletion cannot have a push delivered on its behalf."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "The relay authenticates each delivery request to the gateway with a NIP-98 signed HTTP Authorization header over the relay's own signing key, matching the NIP-PL spec's requirement that the gateway verify a NIP-98 event whose pubkey is the relay identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "docs/nips/NIP-PL.md"
  - statement: "The gateway's delivery route (POST /v1/deliveries/apns) is one of nine HTTP routes the gateway exposes: installation challenge issuance, installation enrollment, relay delegation/capability issuance, endpoint rotation, delegation revocation, installation revocation, delivery, and liveness/readiness probes."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "The gateway's delivery request/response wire types carry no application content: DeliveryRequest is {v, endpoint_grant, request_id, expires_at}, and DeliveryResponse is one of Accepted, InvalidEndpoint{generation, invalid_at}, or Retry{retry_after_seconds}."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
  - statement: "The gateway sends one compiled-in APNs reconnect payload constant for every delivery; the relay never supplies, and the gateway never derives, per-message notification text, event ids, or content, matching NIP-PL's fixed-payload requirement for the APNs transport profile."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
      - "docs/nips/NIP-PL.md"
  - statement: "Installation enrollment and endpoint/delegation mutations are authenticated to the gateway using Apple App Attest: each route signs a domain-prefixed, order-fixed JSON transcript, and the gateway's http.rs verifies the resulting attestation or assertion (verify_installation_assertion) before accepting challenge, enroll, delegate, rotate_endpoint, revoke_delegation, or revoke_installation requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "docs/nips/NIP-PL.md"
  - statement: "The gateway persists installation and delegation authority, replay reservations, and endpoint quotas in six Postgres tables it owns exclusively (push_gateway_challenges, push_gateway_installations, push_gateway_delegations, push_gateway_endpoint_quotas, push_gateway_delivery_auth_replays, and a delivery-request replay table), separate from relay community tenancy."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
  - statement: "Reads of kind:30350 (REQ/COUNT) must be NIP-42-authenticated and are scoped to events whose author equals the authenticated pubkey; lease acceptance itself requires the connection to be NIP-42-authenticated with the authenticated pubkey equal to the event's pubkey."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "On a successful gateway delivery (200 Accepted) the relay marks the wake complete; on a permanent-invalid-endpoint response (410, matching the wake's current lease generation) the relay disables that endpoint generation and fails the wake without touching sibling leases; on a transient response (503 Retry, 429 Too Many Requests, or a connect/timeout error) the relay retries with capped exponential backoff up to a fixed attempt ceiling, after which the wake is failed terminally; a 404 on a retried (attempt > 1) delivery is treated as a successful replay of an already-delivered request and the wake is completed rather than retried again."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "The three push-eligible kind allow-lists -- the relay's validated NIP-PL descriptor constant, the Postgres trigger's inline allow-list, and a dedicated relay test -- are required to agree, and a test explicitly asserts the trigger's allow-list matches the relay's advertised PUSH_KINDS constant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "migrations/0023_push_match_gate.sql"
  - statement: "The gateway currently registers only iOS APNs application profiles (buzz-ios-production, buzz-ios-sandbox); an FCM profile and UnifiedPush are both explicitly documented as not conforming v1 public-gateway profiles pending a separately registered fixed payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/model.rs"
      - "docs/nips/NIP-PL.md"
  - statement: "As of the recorded revision, no mobile (Flutter) or desktop (Tauri) client code in this repository creates, rotates, or revokes a push lease, performs App Attest enrollment, or references kind:30350 -- the client half of this flow exists only as normative spec text in docs/nips/NIP-PL.md, not as shipped Buzz client code."
    entry_class: FACT
    evidence:
      - "grep_recursive('30350|push_lease|PushLease|kind_push_lease|NIP-PL|nip-pl', paths='mobile/lib desktop/src') -> no matches"
  - statement: "The relay-side matcher and delivery worker (push_runtime.rs) shipped in commit bffbc5f22 (\"feat(push): deliver accepted relay events as wakes\", 2026-07-14 16:13 -0400), which lands after commit 1c006822e (\"feat(push): add public APNs gateway\", same day 11:17 -0400) and after docs/formal/nip-pl/NOTE.md's last edit (also 2026-07-14 11:17 -0400, the same commit as the gateway); the formal note's caveat that the relay matcher/worker is \"not-yet-shipped\" therefore predates and is superseded by the matcher/worker's own shipping commit, and is stale as of the recorded revision."
    entry_class: INFERENCE
    evidence:
      - "git_log_last_commit('docs/formal/nip-pl/NOTE.md') -> 2026-07-14 11:17:21 -0400 1c006822e feat(push): add public APNs gateway (#1770)"
      - "git_log_last_commit('docs/push-gateway-deployment.md') -> 2026-07-14 16:13:04 -0400 bffbc5f22 feat(push): deliver accepted relay events as wakes (#1866)"
      - "docs/formal/nip-pl/NOTE.md"
    confidence: 0.85
  - statement: "Representative automated verification for this flow includes: push_lease.rs's envelope/plaintext/generation/quota validation tests, a gift-wrap self-#p authorization test and a gateway-retry idempotency test in push_runtime.rs, and the standalone formal models (acceptance.py, mutation_test.py, delivery.py, delivery_mutation.py, fixed_payload.py, fixed_payload_mutation.py) that bounded-exhaustively check lease-acceptance ordering, gateway delivery authority, and the fixed-APNs-payload invariant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-relay/src/push_runtime.rs"
      - "docs/formal/nip-pl/NOTE.md"
---

# Push notification delivery flow

How Buzz wakes an installed iOS client through Apple Push Notification service
(APNs) when a message the client is authorized to read arrives while its
websocket is disconnected, under NIP-PL (Push Leases).

This node documents the **flow**: what triggers it, the ordered path an event
takes from relay ingest to a device wake, the trust boundaries it crosses, and
how it fails safely. It intentionally does not restate the full NIP-PL wire
protocol (`docs/nips/NIP-PL.md` is canonical for that) or gateway operations
(`docs/push-gateway-deployment.md` is canonical for deployment, secrets, and
alerting). Link to those; do not duplicate their content here.

## Trigger, preconditions, termination

**Trigger.** A relay accepts and durably stores an event whose `kind` is in
the push-eligible allow-list `{7, 9, 1059, 40007, 46010}` (reactions,
channel/DM messages, NIP-59 gift wraps, thread-adjacent kind, and an
approval-gate kind), for a community that currently has at least one active,
endpoint-enabled, unexpired push lease.

**Preconditions.**
- The event's community has at least one accepted `kind:30350` push lease
  (`active: true`, not expired, with an enabled endpoint) — otherwise the
  Postgres trigger skips enqueueing a match job for that community entirely,
  so the flow never starts.
- The relay has a configured, non-empty `BUZZ_PUSH_GATEWAY_DELIVERY_URL`
  (defaults to `https://push.buzz.xyz/v1/deliveries/apns`) — an operator can
  disable NIP-PL push relay-wide by setting this to an empty string.
- The installation previously completed gateway enrollment (App Attest) and
  relay delegation (`POST /v1/delegations`), producing an `endpoint_grant`
  capability, and that capability is embedded (not the raw APNs token) as the
  lease's encrypted `endpoint`.

**Termination / outcome.** The flow terminates in exactly one of: (a) the
gateway accepts an APNs send attempt and the relay marks the wake complete;
(b) the wake is judged not owed (expired lease, revoked lease, lost
membership, or a lease-generation mismatch) and is dropped without ever
reaching the gateway; (c) the gateway reports the endpoint permanently
invalid and the relay disables that endpoint generation; or (d) the wake
exhausts its retry budget against transient failures and is failed
terminally. None of these outcomes constitutes a delivery guarantee — NIP-PL
defines wake delivery as lossy and best-effort; the authoritative state is
always the event the client later fetches over `REQ`, never the wake itself.

## Ordered interactions and data/state movement

1. **Lease established (precondition, out of band).** An installation enrolls
   with the gateway via App Attest (`POST /v1/installations`), obtains a
   relay delegation capability (`POST /v1/delegations`), and the client
   publishes a `kind:30350` event whose NIP-44-encrypted content embeds that
   opaque `endpoint_grant` (never the raw APNs token) plus its subscription
   filters. The relay's `push_lease::accept` validates and atomically persists
   it.
2. **Event ingest.** A client publishes a push-eligible-kind event; the relay
   accepts and inserts it into `events` inside one transaction.
3. **Durable match enqueue (same transaction).** The `events_enqueue_push_match`
   trigger fires `AFTER INSERT`; if the community has a qualifying lease, it
   inserts one row into `push_match_queue` keyed by `(community_id,
   event_id)`. This makes the match job crash-safe with the event insert: a
   rolled-back event never gets a match job, and an accepted event always
   does, without depending on any in-process dispatch path.
4. **Matcher claim and evaluation.** `run_matcher` polls
   `claim_due_push_match_batch`, loads the community's active leases and
   channel-membership pairs, and evaluates each queued event against every
   lease's filters — including a gift-wrap-specific rule that a lease may
   only match `kind:1059` events whose outer `#p` tag is the lease's own
   author, since gift wraps are globally stored and an unrestricted match
   would leak recipient activity through wake timing.
5. **Wake enqueue.** Matching (lease, event) pairs become `WakeRequest`s,
   flushed set-wise for the whole batch into a durable wake outbox.
6. **Delivery claim and re-validation.** `run_delivery_worker` polls due wakes
   per community and, for each, `deliver_one` re-validates the wake (active
   lease, expiration, endpoint generation) via `revalidate_push_wake`; if the
   wake names a channel, it re-checks the lease author's current channel
   membership — read authorization is re-checked at delivery time, not
   trusted from match time, because membership can change in between. A
   second `revalidate_push_wake` call runs immediately before transport to
   close a race between the membership check and a concurrent lease
   replacement.
7. **Community-deletion fence.** The worker acquires a community-scoped
   serving-write guard before sending; if the community is mid-deletion, the
   guard cannot be acquired or verified and the wake is failed rather than
   delivered.
8. **Relay → gateway delivery request.** The relay POSTs `{v, endpoint_grant,
   request_id, expires_at}` to the configured gateway delivery URL,
   authenticated with a NIP-98 signed HTTP header keyed to the relay's own
   signing identity. `request_id` is the relay's durable wake job id and
   becomes the stable idempotency key (APNs `apns-id`) for the whole attempt,
   including retries.
9. **Gateway admission and send.** The gateway decrypts and validates the
   `endpoint_grant` (signer, installation/delegation liveness, endpoint
   epoch/generation, expiry), reserves the request id for replay protection,
   charges endpoint quota, and — only if all of that holds — sends the one
   fixed, compiled-in reconnect payload constant to APNs. No relay-supplied
   byte, event id, or content ever enters that payload.
10. **Client wake and resync.** APNs delivers the fixed reconnect
    notification to the device. On receipt the client reconnects and fetches
    authoritative events through ordinary authenticated `REQ` against its
    configured relay(s) — the wake carries no event data, so this fetch is
    the only way new content actually reaches the client.

## Trust boundary and authentication crossings

- **Client → relay (event publish, lease publish/REQ).** NIP-42 connection
  authentication; `kind:30350` acceptance additionally requires the connected
  pubkey to equal the event's `pubkey`, and reads of `kind:30350` are
  restricted to the authenticated author — to any other querier the kind
  behaves as if no such events exist.
- **Client → gateway (enrollment, delegation, rotation, revocation).** Apple
  App Attest: every mutating route verifies a domain-prefixed, order-fixed
  signed transcript (attestation at enrollment, assertions thereafter), not
  the raw request bytes.
- **Relay → gateway (delivery).** NIP-98 signed HTTP request over the relay's
  own Nostr signing key; the gateway treats the relay as the caller identity
  sealed into the `endpoint_grant`, and a capability minted for one relay
  pubkey cannot be redeemed by another.
- **Gateway → APNs.** Standard Apple provider-token / topic credentials,
  configured only on the gateway; the relay never holds APNs credentials.
- **Community isolation.** Push match jobs, leases, and quotas are scoped by
  `community_id`; the gateway's installation/delegation authority is
  deliberately outside relay community tenancy (an installation may delegate
  to more than one relay), but per-delivery admission still confines a
  capability to the signer, epoch, and generation it was sealed to.
- **Executor decrypts leases, never message content.** The relay decrypts a
  lease's NIP-44 content because the lease is addressed to it, but never
  decrypts the NIP-44/NIP-59 content of the events it matches — matching uses
  only the accepted event's outer envelope and relay-local authorization
  state.

## Failure, abort, and rollback behavior

- **No qualifying lease.** The event trigger's `EXISTS` check against
  `push_leases` short-circuits before any `push_match_queue` row is written —
  the common case (`most communities`) pays no matcher cost at all.
- **Match job crash/poison recovery.** `run_matcher` periodically calls
  `reap_exhausted_push_matches` off the claim path so a stuck or
  crash-abandoned match job does not permanently starve its event.
- **Membership lost between match and delivery.** `deliver_one` fails the
  wake (does not retry) if the lease author is no longer a member of the
  target channel at delivery time — a zombie lease left over from a channel
  the author has since left cannot deliver.
- **Community deletion in flight.** Delivery is suppressed and the wake
  failed if the community-scoped serving-write guard cannot be acquired,
  verified, or held for the send.
- **Gateway-reported permanent invalid endpoint (`410`).** The relay disables
  only that specific endpoint generation, and only if the response's
  generation still matches the wake's current lease generation — it never
  revokes the author's lease or affects sibling leases/installations.
- **Gateway-reported transient failure (`503 Retry`, `429`) or a network
  timeout/connect error.** The relay retries with exponential backoff
  (`delay * 2^(attempt-1)`, capped) up to a fixed attempt ceiling
  (`MAX_ATTEMPTS`); exceeding the ceiling fails the wake terminally.
- **Replayed terminal attempt (`404` on a retried delivery).** Because the
  request id is reused across retries of the same wake, a timed-out terminal
  attempt's replay is indistinguishable from "grant not found"; the relay
  treats a `404` on attempt > 1 as a successful replay and completes the wake
  rather than retrying again, to avoid double-delivery.
- **Push delivery is never a read grant.** Every failure mode above degrades
  toward "no notification," never toward exposing event content or
  authorization state the client did not already have through normal `REQ`
  access — the wake signal itself carries no event data, so a dropped or
  suppressed wake has no confidentiality consequence, only a latency one
  (the client still converges once it reconnects, on its own or via another
  route).
- **Representative verification.** `push_lease.rs`'s validation tests (tag,
  plaintext-schema, generation, and quota checks) and `push_runtime.rs`'s
  `gift_wrap_match_requires_self_p_filter_and_recipient` and
  `gateway_retries_send_the_same_request_id_over_http` tests exercise these
  paths directly; the standalone formal models under `docs/formal/nip-pl/`
  (`acceptance.py`, `delivery.py`, and their mutation-test counterparts)
  bounded-exhaustively check lease-acceptance ordering, gateway delivery
  authority, and the fixed-APNs-payload invariant independently of the Rust
  test suite.

## Scope and omissions

**This node covers** the end-to-end trigger-to-wake flow for the shipped
iOS/APNs profile: relay-side lease acceptance, the durable match-and-deliver
pipeline, the relay↔gateway boundary, and documented failure/retry/abort
behavior.

**It does not cover, and these are gaps rather than silence:**

- **No mobile or desktop client implementation exists in this repository.**
  As of the recorded revision, neither `mobile/lib` nor `desktop/src` contains
  any code that creates, rotates, or revokes a push lease, or performs App
  Attest enrollment — the client side of this flow is normative spec text
  only (`docs/nips/NIP-PL.md`), not shipped Buzz client behavior. A reader
  should not infer from this node that push notifications are currently
  end-to-end operational for a real user; server-side plumbing is complete
  and tested, the client half is not yet written.
- **FCM and UnifiedPush transport profiles.** Both are explicitly documented
  as not-yet-conforming v1 public-gateway profiles; this node describes only
  the shipped APNs path.
- **The full NIP-PL wire protocol** (exact JSON schemas, HTTP route request/
  response bodies, quota parameters, key rotation mechanics) — see
  `docs/nips/NIP-PL.md`.
- **Gateway deployment, secrets, metrics, and alerting** — see
  `docs/push-gateway-deployment.md`.
- **Coalescing of multiple matched subscriptions/leases into one wake**,
  priority-class resolution, and suppression (`ignore`/`p_tags_max`) are
  specified in `docs/nips/NIP-PL.md` but were not independently traced
  through relay code for this node; treat those mechanics as spec-only until
  a future revision verifies them against `push_runtime.rs`.
- **No relationships** to other corpus nodes are declared: at the recorded
  revision no other node exists in the merged corpus for this flow to point
  at (confirmed via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`, which lists only `AGENTS.md`, `README.md`, and the
  two `standards/` nodes). Revisit once sibling `architecture/` nodes land.
