---
id: layers-security-cryptographic-boundary
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "verify_event checks that an event's id is the correct hash of its own fields and that its signature is a valid Schnorr signature, returning VerificationError::InvalidId or VerificationError::InvalidSignature when either check fails; it is CPU-bound and its own doc comment states it must be called via tokio::task::spawn_blocking in async contexts."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
  - statement: "compute_hash computes a SHA-256 digest over an audit entry's fields in a fixed order: community_id first, then seq, created_at (normalized through to_storage_precision), action, actor_pubkey (with a presence tag distinguishing Some(empty) from None), object_id (same presence-tag treatment), detail (serialized via canonical_json with sorted keys for determinism), and finally prev_hash (or the fixed GENESIS_HASH sentinel for a community's first entry). Its own doc comment states field order is fixed because changing it invalidates all existing chains, and that hashing community_id first means an entry cannot be lifted out of one community's chain and re-verified inside another."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:26-73"
  - statement: "AuditService::verify_chain reads one community's rows in a given [from_seq, to_seq] range (scoped by a WHERE community_id = $1 clause, so it can never read another community's rows), then for each row in sequence order recomputes compute_hash and compares it to the row's stored hash (returning AuditError::HashMismatch on mismatch), and checks that the row's own prev_hash equals the previous row's recomputed hash (returning AuditError::ChainViolation on mismatch). Returns Ok(false) for an empty range and Ok(true) only if every row in the range passed both checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:159-215"
  - statement: "NewAuditEntry, the input type AuditService::log accepts, carries actor_pubkey as a caller-supplied Option<Vec<u8>>. Its own doc comment establishes a provenance guarantee for community_id (typed as CommunityId specifically so it can only come from host resolution or a server-scoped DB row, never client input) but makes no equivalent claim for actor_pubkey — nothing in buzz-audit itself checks that a supplied actor_pubkey corresponds to a signature-verified action; the crate records whatever the caller passes."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/entry.rs"
  - statement: "Grepping crates/ for verify_chain finds exactly one call site outside buzz-audit's own module: crates/buzz-relay/src/handlers/event.rs's audit_chain_is_isolated_per_tenant_through_relay_ingest, a plain #[tokio::test] (not #[ignore]) that soft-skips at runtime (eprintln! + early return) when Postgres/Redis are unreachable via its own audit_state() helper. buzz-audit's own verify_chain-exercising tests in crates/buzz-audit/src/service.rs (chain_links_within_one_community, chains_are_independent_per_community, verify_detects_tampering_within_a_community, cross_community_row_does_not_verify, verify_empty_range_is_false) are all explicitly #[ignore = \"requires Postgres\"], selected only by `cargo test -p buzz-audit -- --ignored`. No non-test call site anywhere under crates/ invokes verify_chain; there is no admin/operator command in crates/buzz-admin or crates/buzz-cli that runs it."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='verify_chain', path='crates/') -> matches only crates/buzz-audit/src/hash.rs (a comment), crates/buzz-audit/src/service.rs (definition + its own #[ignore]-gated tests), crates/buzz-relay/src/handlers/event.rs:1979-1985 (one #[tokio::test], not #[ignore]), and crates/buzz-test-client/tests/conformance_multitenant.rs (a doc comment referencing it, not a call), verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "crates/buzz-audit/src/service.rs:331-384"
      - "crates/buzz-relay/src/handlers/event.rs:1847-1876"
  - statement: "PairingSession::build_event serializes a PairingMessage to JSON and encrypts it with nip44::encrypt(secret_key, peer_pubkey, plaintext, nip44::Version::V2) before wrapping it in a signed kind:24134 event; PairingSession::decrypt_message calls nip44::decrypt(secret_key, event.pubkey, event.content) to reverse it, after first rejecting any content field outside NIP-44's 132-87472 character range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:603-628"
      - "crates/buzz-core/src/pairing/session.rs:634-663"
  - statement: "NIP-AB.md states the content field of a pairing event is always encrypted using NIP-44 version 2, with the conversation key derived from the sender's ephemeral private key and the recipient's ephemeral public key via ECDH; implementations MUST use NIP-44 v2 and MUST reject events whose NIP-44 version byte is not 0x02, and MUST NOT silently fall back to an older version. Its Relay Compromise subsection states a compromised relay 'cannot: Read the payload (NIP-44 encrypted with ECDH keys the relay does not possess)' or 'Forge events (events are signed by ephemeral keys; signatures are validated before processing)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "NIP-AB.md's Security Considerations section states the defense against a QR-code-racing MITM attacker is 'user verification against their physical device, not cryptographic impossibility' -- the SAS (Short Authentication String) comparison is a human out-of-band check gating whether sas-confirm and the payload are sent at all, not itself a cryptographic proof of the peer's identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "Issue #1169's definition of done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain scope and the states/operations to which it applies, name enforcement points and observable failure behavior, and link at least one verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1169 definition of done"
  - statement: "Because AuditEntry's hash covers actor_pubkey as an opaque byte string and AuditService itself performs no signature check against it, the hash chain's cryptographic guarantee is that a stored row has not been altered since AuditService::log wrote it (tamper-evidence of the recorded field values), not that the actor_pubkey field is itself an authentic claim about who acted -- that second property, if it holds at all, depends entirely on whatever verified the actor's signature at the call site before constructing the NewAuditEntry, a discipline the audit chain itself does not enforce or check."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-audit/src/entry.rs"
      - "crates/buzz-audit/src/hash.rs:26-73"
    confidence: 0.75
---

# Cryptographic boundary: what Buzz proves versus what it trusts

## The invariant

Buzz cryptographically verifies exactly three properties, each independently
enforced by its own mechanism, and **nothing else in the system carries a
cryptographic proof** — every other claim about an event, an audit-log entry, or
a pairing session **MUST** be treated as trusted or assumed by whoever relies on
it, not as cryptographically established, unless a future revision of this node
documents a fourth mechanism.

1. **Event authenticity.** Every event's `id` **MUST** be the correct hash of its
   own fields, and its `sig` **MUST** be a valid Schnorr signature over that `id`
   under the key named in its own `pubkey` — enforced by `verify_event`
   (`crates/buzz-core/src/verification.rs`). Full enforcement-point detail for
   this property is `architecture-principles-signed-events`'s subject, not
   restated here; this node cites it only for scope.
2. **Audit-log entry integrity.** Every row appended to a community's audit chain
   **MUST** recompute, via `compute_hash`, to the digest stored alongside it, and
   its `prev_hash` **MUST** equal the previous row's recomputed digest —
   verifiable by `AuditService::verify_chain` (`crates/buzz-audit/src/hash.rs`,
   `crates/buzz-audit/src/service.rs`).
3. **Pairing-payload confidentiality and integrity.** The `content` of a
   `kind:24134` NIP-AB pairing event **MUST** be a valid NIP-44 v2 ciphertext,
   decryptable only by the party holding the ECDH private key that pairs with
   the sender's ephemeral public key — enforced by `nip44::encrypt` /
   `nip44::decrypt` in `crates/buzz-core/src/pairing/session.rs`, per the NIP-AB
   specification (`crates/buzz-core/src/pairing/NIP-AB.md`).

These three are related only in that each is *the* place in the codebase where a
cryptographic primitive (Schnorr signature, SHA-256 hash chain, NIP-44
authenticated encryption) is the thing standing between an accepted claim and a
forged or tampered one. They do not share a call path, a data type, or a single
enforcement point — this node's job is to say where that line falls across all
three, and, symmetrically, to name what falls outside it.

## Scope: what this governs

**Applies to:**

- Every event a client submits through the relay's ingestion surface (property
  1) — see `architecture-principles-signed-events` for the full per-surface
  enforcement table.
- Every row written to `audit_log` via `AuditService::log`, and any later read
  through `AuditService::verify_chain` (property 2).
- Every `kind:24134` message exchanged during a NIP-AB device-pairing session
  between two ephemeral keypairs (property 3).

**Does not govern (these are the boundary, not gaps in it):**

- **The transport connection itself.** TLS/WebSocket transport security was not
  inspected for this node; whatever guarantee it provides is a separate,
  unexamined layer beneath all three properties above, not part of this node's
  claim.
- **Host-derived community binding.** `architecture-principles-community-is-
  security-boundary` documents a fail-closed *server-side resolution* rule
  (`bind_community`) that is not itself a cryptographic check — nothing proves
  cryptographically that a request actually originated from the host it claims;
  the boundary is enforced by the relay's own connection-time logic, referenced
  here for contrast, not restated.
- **`created_at` timestamps.** No mechanism described here or in
  `architecture-principles-signed-events` independently verifies that an
  event's or a pairing message's self-reported timestamp reflects real wall-clock
  time; it is signed (as part of the event) or encrypted (as part of a pairing
  payload) along with everything else, but a signature proves the signer wrote
  that value, not that the value is true.
- **An audit entry's `actor_pubkey` as an honest claim.** Property 2's hash
  chain proves a stored row has not been altered since `AuditService::log` wrote
  it. It does **not** prove `actor_pubkey` names the party that actually
  performed the action — `NewAuditEntry` accepts `actor_pubkey` as a
  caller-supplied byte string with no independent signature check inside
  `buzz-audit` itself. Whether every call site only ever passes a pubkey already
  authenticated by property 1 (a verified event's own `pubkey`) or an
  equivalent check is call-site discipline this node did not audit end to end;
  see *Scope and omissions*.
- **The MITM defense in NIP-AB pairing.** Property 3 proves *confidentiality and
  integrity* of the payload against a relay that lacks the ephemeral private
  key. It does **not**, by itself, prove which physical device the user is
  actually pairing with — NIP-AB's own security considerations name that
  defense explicitly as the user's SAS comparison against their physical
  device, "not cryptographic impossibility."

## Enforcement points and observable failure behavior

| Property | Enforcement point | Failure behavior |
|---|---|---|
| Event authenticity | `verify_event` (`crates/buzz-core/src/verification.rs`), called from the relay's ingestion handlers | NIP-01 `OK` with `accepted=false`, message prefixed `"invalid: "` — see `architecture-principles-signed-events` for the full table |
| Audit-log entry integrity | `compute_hash` (`crates/buzz-audit/src/hash.rs`) recomputed and compared inside `AuditService::verify_chain` (`crates/buzz-audit/src/service.rs:159-215`) | `Err(AuditError::HashMismatch { seq })` on a digest mismatch, `Err(AuditError::ChainViolation { seq })` on a broken `prev_hash` link, `Ok(false)` on an empty queried range |
| Pairing-payload confidentiality/integrity | `nip44::decrypt` inside `PairingSession::decrypt_message` (`crates/buzz-core/src/pairing/session.rs:634-663`), after a `content`-length range check | `Err(PairingError::Nip44(..))` on decryption failure (wrong key, tampered ciphertext, or wrong version byte); `Err(PairingError::UnexpectedMessage { .. })` if `content` falls outside NIP-44's 132-87472 character range before decryption is even attempted |

## Verification

**Property 1 (event authenticity).** See `architecture-principles-signed-events`'s
own *Verification* section — unit-tested at the `buzz-core` level; no wire-level
integration test found for the rejection path at that node's recorded revision.

**Property 2 (audit-log integrity).** `crates/buzz-audit/src/service.rs` carries
five tests exercising `verify_chain` directly (`chain_links_within_one_community`,
`chains_are_independent_per_community`, `verify_detects_tampering_within_a_community`,
`cross_community_row_does_not_verify`, `verify_empty_range_is_false`), all marked
`#[ignore = "requires Postgres"]` and selected only via `cargo test -p buzz-audit
-- --ignored`. `crates/buzz-relay/src/handlers/event.rs`'s
`audit_chain_is_isolated_per_tenant_through_relay_ingest` exercises the same
function through the relay's own dispatch path, as a plain `#[tokio::test]` that
soft-skips (rather than failing) when Postgres/Redis are unavailable.

**Verification recorded as missing, not merely unmentioned:** `verify_chain` has
**no caller anywhere in production code** — no admin CLI command
(`crates/buzz-admin`), no `buzz-cli` subcommand, and no background job invokes it
against a live database. The function exists and is exercised by tests, but
nothing in a running relay deployment currently re-verifies the audit chain's
integrity on any schedule or on operator demand. This gap was checked by
grepping `crates/` for `verify_chain` and confirming every match is either the
definition, a test, or a comment (see the evidence ledger above); it is not
tracked by an existing issue at this revision.

**Property 3 (pairing-payload encryption).** `crates/buzz-core/src/pairing/NIP-AB.spthy`
is a formal (Tamarin) model of the NIP-AB protocol, and `NIP-AB.md`'s own
*Formal Verification* section describes proofs including that the target never
decrypts a payload before dual consent. This node did not re-run that model or
independently audit `nostr::nips::nip44`'s own implementation (see *Scope and
omissions*); what is verified above is that `session.rs` calls the NIP-44 v2
functions the specification requires, read directly from the source.

## Boundary

This node does not describe:

- The full per-surface event-ingestion enforcement table for property 1 — see
  `architecture-principles-signed-events`.
- The host-derived community-binding mechanism — a server-side, non-cryptographic
  fail-closed rule — see `architecture-principles-community-is-security-boundary`.
- Whether NIP-42 (`buzz-auth`'s `verify_nip42_event`) or NIP-98 HTTP-auth
  signature checks belong to this same boundary; both are Schnorr-signature
  checks structurally similar to property 1, but neither was opened for this
  node and neither is claimed here.
- The cryptographic soundness of the underlying primitives themselves (`nostr`
  crate's Schnorr implementation, SHA-256, NIP-44's ChaCha20/HMAC-SHA256
  construction) — all three are treated as trusted external dependencies whose
  own correctness this node assumes rather than audits.

## Relationships

- references: architecture-principles-signed-events
- references: architecture-principles-community-is-security-boundary

## Scope and omissions

**This node covers** the three places in Buzz where a cryptographic primitive —
not a server-side check, not a convention, not a fail-closed default — is what
actually stands between an accepted claim and a forged or tampered one: event
signature/id verification, the audit-log hash chain, and NIP-AB pairing-payload
encryption. It states, for each, the property enforced, the function that
enforces it, and the observable failure. It also states explicitly which
adjacent, easily-confused properties are *not* cryptographically proven:
transport security, host-derived community binding, timestamp truthfulness, an
audit entry's `actor_pubkey` as an honest claim, and physical-device identity in
NIP-AB pairing.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Full per-surface event-ingestion enforcement detail | `architecture-principles-signed-events` |
| Host-derived community-binding mechanism and its own fail-closed guarantees | `architecture-principles-community-is-security-boundary` |
| NIP-42 (`buzz-auth::nip42`) and NIP-98 signature-check mechanisms | not yet documented by any corpus node at this revision |
| The `nostr` crate's own Schnorr/NIP-44 primitive implementations | not opened for this node; treated as a trusted dependency |
| Whether `verify_chain` should gain an operator-facing or scheduled caller | not tracked by an existing issue at this revision |

**Expected but not verified when this node was written:**

- **Whether every `AuditService::log` call site's `actor_pubkey` traces back to
  an event or request that passed property 1's (or an equivalent) signature
  check.** A sample was read (`crates/buzz-relay/src/api/media.rs` passes
  `auth.auth_event.pubkey`; `crates/buzz-relay/src/handlers/event.rs` passes a
  hex-decoded `actor_pubkey_hex`) but not every call site under
  `crates/buzz-relay` was audited exhaustively.
- **Whether NIP-AB's Tamarin proof (`NIP-AB.spthy`) currently re-runs clean
  against this revision.** The model's existence and its stated properties were
  read from `NIP-AB.md`'s own prose; the proof itself was not re-executed for
  this node.
- **Whether `verify_chain`'s complete absence of a production caller is a
  deliberate design choice or an unaddressed gap.** No commit message, ADR, or
  issue explaining that absence was found while writing this node.
