---
id: interfaces-nostr-buzz-nips-nip-pl
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "NIP-PL (Push Leases) defines kind:30350 as a stored, installation-scoped, expiring authorization asking a push executor to keep a constrained Nostr filter active after a client's socket closes and to wake a specific installation through a platform push transport when the filter matches; the push payload is a fixed transport-authored reconnect signal that never carries relay-supplied bytes, event ids, content, or URLs, and the client fetches authoritative events over ordinary authenticated REQ after waking."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "kind:30350 (KIND_PUSH_LEASE) is registered in the relay's kind table and included in AUTHOR_ONLY_KINDS, the set of kinds whose stored events the relay must never reveal (existence, count, tags, content) to anyone but the authenticated author."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:104-133"
  - statement: "The relay's push_lease module validates a kind:30350 event's public tags (exactly d, expiration, exec, optional alt; each with one value) and lifetime bounds in validate_envelope, decrypts and parses the NIP-44 plaintext with parse_plaintext (rejecting duplicate keys and unknown fields), and validates the plaintext schema/size/filter rules in validate_plaintext, all ahead of any persistence."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:84-147"
      - "crates/buzz-relay/src/handlers/push_lease.rs:150-244"
  - statement: "The accept() function runs the full acceptance sequence for one kind:30350 event in order: a push_enabled config check, validate_envelope, an executor-key-id equality check against the configured push_executor_key_id, NIP-44 decryption of .content under the relay keypair, parse_plaintext/validate_plaintext against a LeaseLimits built from server-side config (app profile buzz-ios-dogfood/apns, push kinds, and numeric quota bounds matching the NIP's descriptor defaults), and finally an atomic persist through state.db.accept_push_lease_event with the source event, computed LeaseVersion (generation, expires_at), and (for an active lease) endpoint hash, endpoint grant, max subscription class, and subscriptions JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:464-565"
  - statement: "The relay's ingest handler dispatches every kind:30350 event to push_lease::accept() and maps its Result to relay OK-message rejection reasons: AcceptError::Validation(reason) becomes \"invalid: <reason>\"; a successful AcceptLeaseOutcome other than Accepted becomes one of \"invalid: stale replacement\", \"invalid: stale generation\", \"invalid: endpoint already leased\", \"invalid: lease quota exceeded\", or \"invalid: source event collision\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2918-2944"
      - "crates/buzz-relay/src/handlers/ingest.rs:425-432"
  - statement: "AcceptLeaseOutcome (Accepted, StaleEvent, StaleGeneration, EndpointAlreadyLeased, LeaseQuotaExceeded, SourceEventCollision) is computed inside one atomic database routine in buzz-db, which is where the NIP's two-ordering replacement check (NIP-01 addressable-event ordering, and a strictly-increasing generation watermark) and the endpoint-uniqueness/quota checks are actually enforced, not merely described in prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs:197-209"
      - "crates/buzz-db/src/store/push.rs:280-419"
  - statement: "The relay's REQ/COUNT handling enforces author-only visibility for kind:30350 in code: a unit test (push_lease_requires_self_author_filter_and_count_fallback) asserts that a push-lease filter is authorized only when it carries an author tag equal to the requester, that a filter naming a different author is rejected, and that a bare kind-only filter (no author) is rejected -- matching NIP-PL's 'no existence, count, tag, or content leakage' requirement rather than only stating it in the spec."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:2111-2131"
  - statement: "buzz-push-gateway's public HTTP router registers exactly the seven POST routes NIP-PL's Public APNs Gateway Profile section names: /v1/installations/challenges, /v1/installations, /v1/delegations, /v1/delegations/revoke, /v1/installations/endpoint, /v1/installations/revoke, and /v1/deliveries/apns."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs:780-800"
  - statement: "architecture-flows-push-notification and architecture-containers-push-gateway are corpus nodes already merged on origin/launchpad that document the wake/reconnect flow and the buzz-push-gateway container respectively; neither documents kind:30350's own write/read interface contract (acceptance sequence, REQ/COUNT ACL, rejection vocabulary), so this node is a distinct, non-duplicating subject."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
      - "launchpad/docs/corpus/architecture/containers/push-gateway.md"
  - statement: "node.schema.json's type enum has no separate 'interface' value; PRD #602's success criteria list interface and event-kind documentation as one combined corpus surface, and the schema encodes that as the single value interfaces-events, which templates/interface.md's own template-instance guidance confirms a node built from it should carry."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "This draft NIP has no upstream NIP number yet; executors advertise it as \"nip-pl\" in NIP-11 supported_extensions rather than in supported_nips, following the NIP-ER precedent the spec itself names."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
---

# NIP-PL (Push Leases): interface

`kind:30350` is Buzz's own draft Nostr extension (unnumbered upstream; advertised
as `"nip-pl"` in NIP-11 `supported_extensions`) defining a **push lease**: a
signed, addressable, NIP-44-encrypted authorization letting an installation ask
its relay (the **executor**) to keep a narrow filter alive after the client's
socket closes and wake it through a platform push transport when that filter
matches. The two sides of this boundary are (1) an installation (mobile client)
and its relay, exchanging the lease itself as an ordinary signed Nostr event
over the same WebSocket/HTTP event-submission and REQ/COUNT surface every other
kind uses, and (2) the relay and the optional public Buzz APNs gateway
(`buzz-push-gateway`), exchanging a narrow set of HTTP routes that carry no
relay-supplied application content. The full normative text lives at
`docs/nips/NIP-PL.md`; this node describes the interface's shape and cites the
code that implements it rather than re-deriving the spec from memory.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Submit/replace a lease (`kind:30350` event via `POST /events` or WebSocket `EVENT`) | `crates/buzz-relay/src/handlers/push_lease.rs#accept` (`crates/buzz-relay/src/handlers/push_lease.rs:464-565`); dispatched from `crates/buzz-relay/src/handlers/ingest.rs:2918-2944` | Validates envelope + plaintext, decrypts under the executor key, and atomically persists an active or inactive (tombstone/revocation) lease. |
| Read own leases (`REQ`/`COUNT` filtered to `kinds:[30350]`) | `crates/buzz-relay/src/handlers/req.rs` (author-only enforcement; see `push_lease_requires_self_author_filter_and_count_fallback`, `crates/buzz-relay/src/handlers/req.rs:2111-2131`); `AUTHOR_ONLY_KINDS` in `crates/buzz-core/src/kind.rs:129-133` | Author-only: a filter without an `authors`/`#p` match to the requester is rejected before any lease is returned, matching NIP-PL's "no existence, count, tag, or content leakage" rule. |
| Wake delivery (relay → APNs, via the public gateway profile) | `docs/nips/NIP-PL.md` §"Public APNs Gateway Profile"; routes registered at `crates/buzz-push-gateway/src/http.rs:780-800` | Seven `POST` routes: challenge, installation enrollment, relay delegation, endpoint rotation, delegation/installation revocation, and `POST /v1/deliveries/apns`. Every accepted APNs attempt sends the one fixed reconnect body constant from NIP-PL's APNs transport profile; no route accepts relay-supplied notification content. |
| Executor discovery | NIP-11 `supported_extensions: ["nip-pl"]` plus a `push` descriptor object (origin, keys, app profiles, push kinds, limits) — `docs/nips/NIP-PL.md` §"Executor Discovery" | Clients read this descriptor to learn the executor's encryption key, supported app profiles/classes, and numeric limits before constructing a lease. |

## Contract and stability

**Versioning.** The lease plaintext carries its own schema version (`v`) and a
strictly-increasing per-address `generation`; `crates/buzz-relay/src/handlers/push_lease.rs`'s
`LeasePlaintext` struct uses `#[serde(deny_unknown_fields)]`, so schema
evolution is a version bump, never silent field addition. `docs/nips/NIP-PL.md`
states this in prose ("schema evolution happens by version bump, not by silent
extension"); the `deny_unknown_fields` attribute is where that promise is
actually enforced in code.

**Ordering and idempotency.** A lease address `(pubkey, 30350, d)` holds
exactly one effective lease. Replacement requires winning **both** NIP-01
addressable-event ordering (`created_at`, tie-broken by event id) and a
strictly-increasing `generation` watermark — implemented as
`AcceptLeaseOutcome::StaleEvent` / `AcceptLeaseOutcome::StaleGeneration` in
`crates/buzz-db/src/store/push.rs:197-209,280-419`, computed inside one atomic
routine so a losing replacement never disturbs the stored winner. Endpoint
uniqueness (`AcceptLeaseOutcome::EndpointAlreadyLeased`) and per-pubkey lease
quota (`AcceptLeaseOutcome::LeaseQuotaExceeded`) are enforced in that same
transaction.

**Authentication/authorization.** Lease submission requires the event's
`pubkey` to match the authenticated NIP-42 connection (ordinary relay
write-auth) plus the executor-key check in `accept()`
(`crates/buzz-relay/src/handlers/push_lease.rs:479-481`). Reads are
author-only: `crates/buzz-core/src/kind.rs`'s `AUTHOR_ONLY_KINDS` list and the
`req.rs` test cited above confirm a bare or foreign-author filter over
`kind:30350` is rejected before matching, not merely filtered after the fact.

**Error/rejection vocabulary.** Every rejection path returns an `invalid:
<reason>` string via `IngestError::Rejected`; `map_push_accept_error`
(`crates/buzz-relay/src/handlers/ingest.rs:425-432`) and the
`AcceptLeaseOutcome` match arm (`crates/buzz-relay/src/handlers/ingest.rs:2922-2944`)
enumerate the full set: free-form validation reasons from `accept()` (e.g.
"lease already expired", "lease ttl too long", "unknown executor key",
"invalid encrypted content" — sourced from `validate_envelope`/`parse_plaintext`/`validate_plaintext`
in `push_lease.rs`), plus the fixed outcome strings `invalid: stale
replacement`, `invalid: stale generation`, `invalid: endpoint already leased`,
`invalid: lease quota exceeded`, and `invalid: source event collision`.

**Push-transport non-interference.** The gateway profile's contract is that
the application payload sent to APNs is a fixed byte constant independent of
any relay-supplied request field; `docs/nips/NIP-PL.md`'s APNs Transport
Profile section states the exact constant and the invariant. This node does
not re-verify that invariant against the gateway's delivery code path; see
*Scope and omissions*.

## Boundary

This node does not describe:
- **`kind:30350`'s full tag-by-tag and plaintext-field-by-field wire catalogue**
  as a standalone event-kind reference — that depth belongs to an
  event-kind-shaped node (per `templates/interface.md`'s own boundary against
  its `#1337` sibling template), should one be drafted. This node cites
  `docs/nips/NIP-PL.md` and `push_lease.rs`'s `LeasePlaintext`/`Subscription`/`Suppress`
  structs rather than restating every field.
- **The gateway's App Attest transcript construction, HTTP body-size ceilings,
  and per-route request/response JSON shapes field-by-field** — a
  domain-expert-depth API reference, which `docs/nips/NIP-PL.md`'s own
  "Public APNs Gateway Profile" section already documents at that depth and
  which this node does not duplicate.
- **The wake/reconnect flow's cross-subsystem sequencing** (dispatch seam,
  Redis pub/sub precedent, `event_mentions` as a matching primitive) — that is
  `architecture-flows-push-notification`'s subject; this node `references` it
  rather than restating it.
- **The `buzz-push-gateway` container's deployment topology, credential
  custody, and private health/metrics surface** — that is
  `architecture-containers-push-gateway`'s subject; this node `references` it
  rather than restating it.

## Examples

**Valid lease (abridged from `docs/nips/NIP-PL.md`'s own worked example).** An
installation submits a `kind:30350` event with tags
`[["d","<random-128-bit-id>"],["expiration","1769990000"],["exec","2026-06"]]`
and NIP-44-encrypted content decrypting to
`{"v":1,"origin":"wss://relay.example","app_profile":"buzz-ios-dogfood","transport":"apns","endpoint":"<opaque grant>","generation":1,"active":true,"subscriptions":[{"filter":{"kinds":[9],"#p":["<self>"]},"class":"default"}]}`.
`accept()` runs the full sequence in
`crates/buzz-relay/src/handlers/push_lease.rs:464-565`, persists it via
`state.db.accept_push_lease_event`, and the relay returns `OK true`.

**Failure example.** A second event at the same `(pubkey, 30350, d)` address
carries a `generation` equal to or lower than the already-accepted lease's
generation. `crates/buzz-db/src/store/push.rs`'s acceptance routine returns
`AcceptLeaseOutcome::StaleGeneration`; `ingest.rs:2927-2929` maps that to
`IngestError::Rejected("invalid: stale generation")`, and the stored event,
effective push state, and generation watermark are left unchanged, per
`docs/nips/NIP-PL.md`'s requirement that a failing replacement never disturb
the prior valid lease.

## Relationships

- references: architecture-flows-push-notification
- references: architecture-containers-push-gateway

## Scope and omissions

**This node covers** the `kind:30350` write/read interface contract between an
installation, its relay (executor), and the optional public APNs gateway: what
operations exist, where each is implemented, the versioning/ordering/idempotency
and auth guarantees a caller may rely on, the rejection-reason vocabulary, and
one valid and one failure example grounded in the actual acceptance code path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `kind:30350`'s full field-by-field wire catalogue | A future event-kind-shaped node, if drafted (none exists yet) |
| The gateway's App Attest transcripts and per-route request/response schemas at domain-expert depth | `docs/nips/NIP-PL.md` §"Public APNs Gateway Profile" directly |
| The wake/reconnect flow's cross-subsystem dispatch sequencing | `architecture-flows-push-notification` |
| The `buzz-push-gateway` container's deployment/credential topology | `architecture-containers-push-gateway` |
| NIP-46 remote-signer interaction for lease creation/rotation | `docs/nips/NIP-PL.md` §"Remote Signers" directly; not separately verified against code here |
| FCM and UnifiedPush transport profiles | Not conforming v1 public-gateway profiles per the spec itself; no Buzz code implements either today |

**Expected but not verified when this node was written:**
- **The gateway's actual APNs delivery code path** (`crates/buzz-push-gateway/src/http.rs`'s
  `deliver` handler body) was located by line but not read in full to confirm
  every claim the spec makes about the fixed-body invariant; the claim above is
  sourced from the spec text and the route table's existence, not from a
  line-by-line read of `deliver`'s body.
- **Whether any integration or unit test exercises the full `accept()` sequence
  end-to-end** (as opposed to the `req.rs` author-only-filter unit test cited
  above) was not searched for; this node cites the implementation, not test
  coverage of it.
- **Whether `references` or `part-of` is the corpus-wide convention** for an
  interface node pointing at adjacent architecture-flow/container nodes is not
  settled anywhere in `launchpad/docs/corpus/standards/`; this node picked
  `references` per its stated directionality ("no ownership or currency
  dependency implied"), consistent with `templates/interface.md`'s own guidance
  for pointing at related-but-not-owned nodes.
