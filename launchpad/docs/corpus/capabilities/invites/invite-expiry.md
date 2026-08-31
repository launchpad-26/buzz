---
id: capabilities-invites-invite-expiry
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "node.schema.json's type enum has no `flow` member, and launchpad/docs/corpus/templates/flow.md's own 'A note on type' section establishes the corpus precedent that a runtime-flow instance node carries type: architecture rather than type: capabilities, even when -- as here -- the node's file path groups it under a capabilities/ directory by topic rather than under architecture/flows/."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/flow.md"
  - statement: "Legacy v1 invite codes are stateless, HMAC-signed bearer tokens whose signed JSON payload embeds its own expiry as unix seconds (field `e`); the module's own doc comment states production minting now uses database-backed v2 codes and the v1 mint helper survives only #[cfg(test)] for compatibility testing, while v1 claim verification remains live for a compatibility drain window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs"
  - statement: "verify_invite (the v1 verifier) checks the HMAC signature first, deserializes the payload only after the MAC verifies, then checks payload.e against the current time before checking community and role -- an expired-but-validly-signed code is rejected with InviteError::Expired before either of those later checks runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs"
  - statement: "Invite TTL bounds are defined once in buzz-core and reused by both invite code generations: MIN_INVITE_TTL_SECS = 60 seconds, DEFAULT_INVITE_TTL_SECS = 72 hours, MAX_INVITE_TTL_SECS = 30 days."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/invite.rs"
  - statement: "The mint HTTP handler (POST /api/invites) defaults an omitted ttl_secs to DEFAULT_INVITE_TTL_SECS and rejects a request whose ttl_secs falls outside [MIN_INVITE_TTL_SECS, MAX_INVITE_TTL_SECS] with 400 Bad Request before any database call is made."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "mint_relay_invite (the v2 database-backed mint path) re-validates the same ttl_secs bounds at the storage layer via validate_mint_inputs, then computes expires_at = now + ttl_secs and persists it on the relay_invites row alongside the SHA-256 hash of the opaque code; the plaintext code is returned to the caller exactly once and never stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs"
      - "crates/buzz-core/src/invite.rs"
  - statement: "The relay_invites table defines expires_at as TIMESTAMPTZ NOT NULL with a supporting index (relay_invites_expires_at_idx), and its own migration comment records that max_uses is optional (NULL = unlimited) and use_count is unrelated to expiry."
    entry_class: FACT
    evidence:
      - "migrations/0025_relay_invites.sql"
  - statement: "claim_relay_invite locks the matching invite row with SELECT ... FOR UPDATE scoped to (community_id, token_hash), then checks expires_at <= Utc::now() before checking existing membership or the use-count budget; on a match it rolls back the transaction and returns ClaimOutcome::Expired without inserting membership or incrementing use_count. A source comment states this ordering is deliberate: an expired bearer must not authorize fresh join-policy-acceptance evidence even for an existing member, while an exhausted-but-live invite remains valid for an idempotent already-member retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs"
  - statement: "Because the invite lookup is scoped to (community_id, token_hash), a code minted for one community and presented to a different community returns ClaimOutcome::Invalid, never Expired or WrongCommunity conflated with it -- the expiry check and the tenant-scope check are independent code paths that cannot be confused with one another."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs"
  - statement: "The HTTP claim handler (POST /api/invites/claim) maps both ClaimOutcome::Expired (v2) and InviteError::Expired (v1) to the same response shape, HTTP 403 Forbidden with JSON body {\"error\": \"invite_expired\"}; a source comment on the v1 branch states this is deliberately more specific than the coarse invite_invalid response used for other v1 rejection reasons, because revealing Expired only happens after the HMAC signature has already verified and therefore does not help an attacker forge a code."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "Expired v2 invite rows are not deleted at expiry time. reap_expired_relay_invites deletes at most RETENTION_SWEEP_BATCH_SIZE (1000) rows per call, selecting rows whose expires_at is older than a caller-supplied cutoff and whose community currently passes community_write_allowed, ordered by expires_at so the oldest rows drain first."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs"
  - statement: "The relay calls reap_expired_relay_invites from inside run_usage_metrics_tick with a cutoff of now() minus 30 days, but only on the pod that currently holds the usage-metrics leader's Postgres advisory lock, so exactly one pod performs the deletion per tick; the surrounding tick's interval defaults to 300 seconds and is configurable via BUZZ_USAGE_METRICS_INTERVAL_SECS."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "A reap failure is caught, logged with tracing::warn!, and does not stop the same tick's subsequent run_storage_sweep_tick call from executing -- the leader-tick loop does not abort or demote leadership because a retention sweep failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "community_write_allowed excluding a community from the reap sweep means a quiescing or deleting tenant's expired invites are skipped rather than deleted while that tenant's deletion lifecycle is in progress; the test retention_sweep_skips_quiescing_tenant_while_active_bystanders_progress seeds three communities with equally-expired invites, quiesces one, and asserts the sweep reaps the other two while leaving the quiesced tenant's row untouched."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs"
  - statement: "Desktop and mobile clients both detect the literal invite_expired error string returned by the claim endpoint and render a distinct expired-invite message rather than a generic failure: desktop defines INVITE_EXPIRED_ERROR = \"invite_expired\" as a shared constant, and mobile's _friendlyInviteError checks message.contains('invite_expired') to return \"This invite has expired.\""
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/inviteHelpers.ts"
      - "mobile/lib/features/invites/invite_join_provider.dart"
  - statement: "Invite expiry is verified by both a Postgres-free unit test (v1, invite_token.rs::tests::rejects_expired, hand-mints an already-expired payload and asserts InviteError::Expired) and Postgres-backed integration tests marked #[ignore = \"requires Postgres\"] (relay_invite.rs::tests::expiry_and_tenant_scope_return_typed_failures, retention_sweep_deletes_only_invites_older_than_cutoff, and retention_sweep_skips_quiescing_tenant_while_active_bystanders_progress), the latter run via `just test` rather than `just test-unit`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs"
      - "crates/buzz-db/src/store/relay_invite.rs"
  - statement: "Per-code revocation (invalidating one specific still-unexpired invite on demand) is explicitly out of scope for the current implementation: invite_token.rs's own module documentation states revocation today is coarse -- rotate the relay keypair, or remove the member after the fact -- and that per-code revocation requires a future relay_invites table increment. This is a distinct mechanism from expiry and is not detailed by this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs"
  - statement: "Issue #759's own Definition of Done requires this document to state trigger, preconditions and termination/outcome; list ordered interactions and data/state movement; identify authentication/authorization/trust-boundary crossings where relevant; and document failure/abort/rollback behavior linked to representative verification -- the same category-specific tail already used by the merged architecture-flows-websocket-authentication node for the same issue category."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#759 definition of done"
relationships:
  - type: part-of
    target: capabilities-invites-invite
---

# Flow: Invite Expiry

How a Buzz relay invite code stops being redeemable once its time-to-live elapses,
across both the legacy stateless (v1) and current database-backed (v2) invite code
generations, and how a long-expired v2 row is eventually deleted.

## Trigger, preconditions, and termination

**Trigger.** Expiry is not itself an active event -- nothing fires the instant an
invite's clock runs out. It is observed at one of two later moments:

1. A joining pubkey presents the code to `POST /api/invites/claim` after its expiry
   time has passed.
2. The relay's leader-only periodic tick reaches its retention-sweep step and finds a
   v2 invite row whose `expires_at` is more than 30 days in the past.

**Preconditions.**

- The code was minted with a `ttl_secs` (or the omitted-request default) inside
  `[MIN_INVITE_TTL_SECS, MAX_INVITE_TTL_SECS]` -- 60 seconds to 30 days, defaulting to
  72 hours -- validated once at the HTTP mint handler and again at the database mint
  function before any row is written.
- **v1 (stateless):** the code's signed payload carries its own expiry (`e`, unix
  seconds); there is no server-side row, so nothing but the signature and the payload
  itself determines expiry.
- **v2 (database-backed):** a `relay_invites` row exists with a persisted
  `expires_at TIMESTAMPTZ NOT NULL`, keyed by `(community_id, token_hash)`.

**Termination / outcome.** The flow ends in one of two shapes depending on which
trigger fired:

- **Claim-time (soft) expiry.** The presented code is rejected: `ClaimOutcome::Expired`
  (v2) or `InviteError::Expired` (v1). No membership is created, no use budget is
  consumed, and -- for v2 -- the claim transaction is rolled back entirely. The invite
  row itself (v2) is untouched and remains queryable/expired; the code holder gets a
  distinct `invite_expired` response rather than a generic rejection.
- **Retention-sweep (hard) deletion.** A v2 row whose `expires_at` is more than 30 days
  old is permanently removed by the periodic sweep. There is no equivalent for v1,
  which has no server-side row to delete.

## Ordered interactions and data/state movement

**Mint-time bound enforcement (both generations share these constants):**

1. A caller (owner/admin) sends `POST /api/invites`, optionally with `ttl_secs`.
   `validate_mint_request` defaults an omitted value to `DEFAULT_INVITE_TTL_SECS` (72h)
   and rejects anything outside `[MIN_INVITE_TTL_SECS, MAX_INVITE_TTL_SECS]` with 400
   before touching the database. (`crates/buzz-relay/src/api/invites.rs`)
2. `Db::mint_relay_invite` re-validates the same bounds via `validate_mint_inputs` as a
   storage-layer defense, computes `expires_at = now() + ttl_secs`, and inserts the
   `relay_invites` row (hash of the code, not the code itself) inside a transaction
   guarded by the community's deletion lifecycle (`DeletionStore::guard_transaction`).
   (`crates/buzz-db/src/store/relay_invite.rs`)

**Claim-time expiry check, v2 (database-backed) path:**

3. The caller sends `POST /api/invites/claim` with the code. `claim_relay_invite` locks
   the matching row with `SELECT ... FOR UPDATE` scoped to `(community_id,
   token_hash)`. (`crates/buzz-db/src/store/relay_invite.rs`)
4. `expires_at <= Utc::now()` is checked **before** the existing-membership check and
   before the use-count/exhaustion check. A match rolls the transaction back and
   returns `ClaimOutcome::Expired`; nothing is written. (`crates/buzz-db/src/store/relay_invite.rs`)
5. The HTTP layer maps `ClaimOutcome::Expired` to `403 Forbidden`, body
   `{"error": "invite_expired"}`. (`crates/buzz-relay/src/api/invites.rs`)

**Claim-time expiry check, v1 (stateless) path -- compatibility drain window only:**

6. `verify_invite` decodes the code, verifies the HMAC signature first, and only then
   deserializes the payload. It checks `payload.e < now_unix()` next, ahead of the
   community and role checks, returning `InviteError::Expired` on a match.
   (`crates/buzz-relay/src/invite_token.rs`)
7. The HTTP layer maps `InviteError::Expired` to the same `403 Forbidden`,
   `{"error": "invite_expired"}` shape used by the v2 path -- deliberately more
   specific than the `invite_invalid` response used for every other v1 rejection
   reason. (`crates/buzz-relay/src/api/invites.rs`)

**Retention sweep (v2 only, no v1 equivalent):**

8. Every usage-metrics tick (default interval 300s, `BUZZ_USAGE_METRICS_INTERVAL_SECS`),
   the pod holding the usage-metrics leader's Postgres advisory lock calls
   `reap_expired_relay_invites(cutoff = now() - 30 days)`.
   (`crates/buzz-relay/src/main.rs`)
9. The sweep deletes at most 1,000 rows per call, oldest `expires_at` first, and only
   for communities where `community_write_allowed(community_id)` is currently true --
   a quiescing or deleting community's expired invites are left alone rather than
   reaped. (`crates/buzz-db/src/store/relay_invite.rs`)
10. On success with `deleted > 0`, the count is logged at `info`. On failure, the error
    is logged at `warn` and the same tick's subsequent `run_storage_sweep_tick` call
    still runs. (`crates/buzz-relay/src/main.rs`)

**Client surfacing:**

11. Desktop and mobile both special-case the literal `invite_expired` string from the
    claim response to show "This invite has expired" instead of a generic error.
    (`desktop/src/shared/api/inviteHelpers.ts`, `mobile/lib/features/invites/invite_join_provider.dart`)

## Trust-boundary and authorization crossings

- **Signature verified before expiry is trusted (v1).** `verify_invite` checks the
  HMAC signature before it ever deserializes or reads the payload's `e` field. An
  attacker cannot manufacture a "not yet expired" claim without first producing a
  valid signature over the whole payload.
- **Expiry checked before membership, deliberately (v2).** `claim_relay_invite`
  evaluates `expires_at` ahead of the existing-membership lookup. The code comment
  states the reason: an expired bearer must not be able to mint fresh join-policy
  acceptance evidence even for a user who is already a member, whereas an
  exhausted-but-still-live invite is allowed to serve an idempotent already-member
  retry. Expiry and exhaustion are therefore checked in a specific, security-relevant
  order, not an arbitrary one.
- **Tenant scoping is independent of expiry.** Because the lookup key is
  `(community_id, token_hash)`, a code presented to the wrong community returns
  `Invalid`, never `Expired` -- the two checks cannot be confused, and expiry status
  is never revealed for a code that fails the tenant-scope check first.
- **Deletion-lifecycle boundary, asymmetric between mint and reap.** Minting a v2
  invite runs inside `DeletionStore::guard_transaction`, which hard-rejects
  (`AccessDenied`) a mint attempt against a quiescing community. The reap sweep, by
  contrast, does not error on a quiescing community -- it simply excludes that
  community's rows from the batch (`community_write_allowed` filter), leaving its
  expired invites in place until the community either resumes or is fully removed.
- **Expired-vs-invalid distinction is a deliberate, narrow oracle exception.** The v1
  claim path otherwise returns a coarse `invite_invalid` for every rejection reason so
  the endpoint is a poor oracle for forgery attempts. `Expired` is the one exception,
  and it is safe only because it is revealed *after* the MAC has already verified --
  it tells a legitimate-but-late holder why they were rejected without helping an
  attacker who has not yet produced a valid signature.

## Failure, abort, and rollback behavior

| Scenario | Detected by | State change | Client-visible signal |
|---|---|---|---|
| v2 claim on an expired invite | `claim_relay_invite`'s `expires_at <= Utc::now()` check | Transaction rolled back; no membership row, no `use_count` increment, invite row untouched | `403 Forbidden`, `{"error": "invite_expired"}` |
| v1 claim on an expired code | `verify_invite`'s `payload.e < now_unix()` check | Stateless -- nothing to roll back | `403 Forbidden`, `{"error": "invite_expired"}` |
| v2 claim on a wrong-tenant code | `(community_id, token_hash)` lookup finds no row | No state change | `403 Forbidden`, `{"error": "invite_invalid"}` (not conflated with `invite_expired`) |
| Retention sweep's `DELETE` fails | `reap_expired_relay_invites` returns `Err` | No rows removed that tick; leadership is not demoted | Logged at `warn`; the same tick's storage sweep still runs |
| Retention sweep runs against a quiescing community | `community_write_allowed` filter in the sweep's own `WHERE` clause | That community's expired rows are left in place, not deleted | No client-visible effect; observed only via the `deleted` count in relay logs |
| Mint attempted against a quiescing community | `DeletionStore::guard_transaction` inside `mint_relay_invite` | No row inserted | Mint request fails with a typed `AccessDenied` error, mapped to `503 Service Unavailable` |

There is no partial state between "not yet expired" and "expired" for either code
generation -- a v2 row's `expires_at` is a single fixed timestamp set at mint and never
extended, and a v1 payload's `e` field is immutable once signed. The only state a
successful claim before expiry produces is membership; the only state expiry itself
produces is a rejected claim (soft) or, eventually, a deleted row (hard, v2 only).

## Verification

- **Unit test, no database (v1):** `invite_token.rs`'s `#[cfg(test)] mod tests ::
  rejects_expired` hand-mints an already-expired payload and asserts
  `verify_invite` returns `Err(InviteError::Expired)`.
- **Unit test, no database (shared bounds):** `relay_invite.rs`'s
  `mint_validation_rejects_invalid_bounds_before_database_access` asserts
  `validate_mint_inputs` rejects a `ttl_secs` outside the shared bounds before any
  database access, run via `just test-unit`.
- **Integration test, requires Postgres:** `relay_invite.rs`'s
  `expiry_and_tenant_scope_return_typed_failures` mints a bounded invite, confirms a
  cross-tenant claim returns `Invalid`, then manually expires the row and confirms a
  same-tenant claim returns `Expired` without consuming a use.
- **Integration test, requires Postgres:** `relay_invite.rs`'s
  `retention_sweep_deletes_only_invites_older_than_cutoff` ages one invite past a
  cutoff and confirms only that row is deleted, leaving a more-recent invite intact.
- **Integration test, requires Postgres:** `relay_invite.rs`'s
  `retention_sweep_skips_quiescing_tenant_while_active_bystanders_progress` seeds three
  equally-expired invites across three communities, quiesces one, and confirms the
  sweep reaps the other two while leaving the quiesced community's row in place.

These Postgres-backed tests are marked `#[ignore]` and run via `just test`, not `just
test-unit` -- this document links them as representative coverage rather than
asserting they were executed while authoring this node.

## Scope and omissions

**This document covers** how an invite code's time-to-live is bounded and validated at
mint time, how expiry is evaluated at claim time for both the legacy v1 stateless and
current v2 database-backed code generations, the deliberate ordering of expiry against
membership/exhaustion/tenant checks, and the leader-only periodic sweep that
permanently deletes long-expired v2 rows.

**It does not cover, and these are gaps rather than silence:**

- **Invite minting's own authorization and request/response contract** (owner/admin
  role check, `max_uses`, the shareable landing-page URL) beyond the TTL bound it
  shares with expiry -- that belongs to the invite capability node (`capabilities/invites/invite.md`,
  issue #762), not yet in this corpus.
- **Redemption mechanics beyond expiry** -- membership insertion, use-count
  exhaustion, and already-member idempotency -- belong to the invite-redemption node
  (issue #760), not yet in this corpus.
- **The invite-token data entity itself** -- the v1 HMAC payload shape and the v2
  opaque-code encoding/hashing scheme -- belongs to the invite-token node (issue #761),
  not yet in this corpus.
- **Per-code revocation.** Explicitly a different mechanism from expiry: the source's
  own module documentation states revocation today is coarse (rotate the relay
  keypair, or remove the member after the fact) and that per-code revocation needs a
  future schema increment. Not detailed here.
- **Relay-keypair rotation as a v1 invalidation mechanism.** v1 codes are also
  invalidated wholesale if the relay's signing key is rotated (the HMAC key is derived
  from it); this is a distinct, coarser mechanism from per-code TTL expiry and is not
  detailed here.
- **The join-policy acceptance receipt's own 10-minute expiry**
  (`mint_policy_acceptance` / `verify_policy_acceptance`) -- a separate, shorter-lived
  artifact bound to an invite code when an operator has configured a join policy, not
  the invite code's own expiry. Not detailed here.

**No `relationships` in this node's front matter.** None of `capabilities-invites-invite`
(#762), the invite-redemption node (#760), or the invite-token node (#761) are merged
at the recorded revision, and a `relationships[].target` naming an id no loaded node
carries is a hard validation error. The natural future edges are `part-of` toward the
invite capability node and `references` toward the invite-token and invite-redemption
nodes, once any of them exist.
