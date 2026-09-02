---
id: platforms-relay-invite-api
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "At the recorded revision, no `launchpad/docs/corpus/templates/platforms.md` exists, so this node is hand-authored directly against `node.schema.json` rather than a per-type template, per `AGENTS.md`'s documented no-template path; its body borrows `component.md`'s section shape (Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope and omissions) as the settled sibling-batch convention for `platforms/**` documents."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "Feature #614 batch task brief for issue #1274, naming the platforms/** type:platforms + component.md-shape convention as already settled by sibling nodes in this batch"
  - statement: "buzz-relay exposes a relay invite HTTP API in crates/buzz-relay/src/api/invites.rs, registered as five routes in the relay's Axum router: `POST /api/invites` (mint), `POST /api/invites/claim` (claim), `GET /api/join-policy` (public policy metadata), `GET /api/join-policy/terms` and `GET /api/join-policy/privacy` (standalone HTML policy pages), and `POST /api/invites/accept-policy` (policy acceptance receipt)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:106-123"
  - statement: "Every invite route requires NIP-98 HTTP signature authentication (no dev X-Pubkey fallback) and binds the tenant community from the Host header before doing anything else; this is implemented once in the shared `authenticate` helper and reused by both `mint_invite` and `claim_invite`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:228-261"
  - statement: "`POST /api/invites/claim` is deliberately exempt from the relay's general membership gate, because its entire purpose is admitting a pubkey that is not yet a member; NIP-98 proves control of the joining key, and the HMAC or database-backed proof on the invite code itself proves an admin authorized the join. This is stated in the module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:1-13"
  - statement: "`mint_invite` (`POST /api/invites`) requires the caller hold the `owner` or `admin` relay-member role in the tenant community, looked up via `state.db.get_relay_member`; any other role (including no membership row) is rejected with 403 before the request body is parsed for TTL/max-uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:285-300"
  - statement: "The mint request body (`MintInviteRequest`) accepts optional `ttl_secs` (defaulting to `DEFAULT_INVITE_TTL_SECS`, 72 hours, and bounded to `MIN_INVITE_TTL_SECS`..=`MAX_INVITE_TTL_SECS`, i.e. 60 seconds to 30 days) and optional `max_uses` (omitted or `null` means unlimited; when present must be an integer from 1 through `MAX_INVITE_USES`, 10,000); `validate_mint_request` enforces both bounds and returns 400 outside them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:48-87"
      - "crates/buzz-core/src/invite.rs:11-21"
  - statement: "A successful mint call always produces a v2, database-backed invite via `state.db.mint_relay_invite`, and returns JSON with `code`, `expires_at` (unix seconds), `max_uses`, `uses_remaining`, and a shareable `url` in the form `<scheme>://<tenant host>/invite/<code>`, where the scheme is `https` when the relay's configured URL is `wss://` and `http` otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:315-348"
  - statement: "A v2 invite code is the literal prefix `v2.` followed by the unpadded base64url encoding of a 32-byte random secret (`V2_SECRET_LEN`); `validate_v2_code` rejects any non-canonical encoding (wrong length, padded, or otherwise non-canonical) by decoding and re-encoding for an exact match, and `hash_v2_code` (SHA-256 of the complete code string) is the only form ever persisted."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/invite.rs:23-57"
  - statement: "`buzz_db::store::relay_invite::mint_relay_invite` generates the 32-byte secret, hashes it, and inserts one row into `relay_invites` (community_id, token_hash, max_uses, expires_at, created_by) inside a transaction that also runs the same community-lifecycle write guard (`DeletionStore::guard_transaction`) used by other community-scoped writes, so a quiescing/archived community surfaces as a typed `AccessDenied` error rather than an opaque failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs:94-146"
  - statement: "The relay maps that guard's `AccessDenied` outcome to HTTP 503 (`community writes are temporarily unavailable`) rather than 500, and maps `InvalidData`/`DeletionSafety` to 400, in `map_mint_error`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:263-274"
  - statement: "`claim_invite` (`POST /api/invites/claim`) routes by exact code prefix with no fallback: a code starting with `v2.` goes to the database-backed redemption path (`validate_v2_code`, then `state.db.claim_relay_invite`); every other code goes to the stateless v1 HMAC verifier (`invite_token::verify_invite`). A malformed or unknown `v2.`-prefixed code is never re-tried against v1 verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:377-465"
  - statement: "`claim_relay_invite` executes the full v2 redemption in one PostgreSQL transaction: `SELECT ... FOR UPDATE` on the matching `(community_id, token_hash)` invite row, an expiry check, an existing-membership check, a use-budget check, the relay-member insert (role fixed to `member`, `added_by = 'invite'`), join-policy-acceptance evidence insert, and a `use_count` increment, all committing together; `FOR UPDATE` serializes concurrent claims so exactly one claimant wins the final slot of a bounded invite."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs:193-382"
  - statement: "`ClaimOutcome` is a typed enum with five variants the relay maps to distinct HTTP responses: `Joined` and `AlreadyMember` (both 200, distinguished by a `status` field in the JSON body), `Expired` (403 `invite_expired`), `Exhausted` (403 `invite_exhausted`), and `Invalid` (403 `invite_invalid`) — no invite outcome ever returns a generic 500."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs:31-57"
      - "crates/buzz-relay/src/api/invites.rs:412-452"
  - statement: "On a `Joined` outcome (v1 or v2 path), the relay publishes two NIP-43 side-effect events — a member-added delta and a refreshed membership list — via `publish_nip43_member_added`/`publish_nip43_membership_list`; publish failures are logged as warnings and do not fail the claim response, and these side effects are never published for `AlreadyMember`, `Expired`, `Exhausted`, or `Invalid` outcomes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:412-503"
  - statement: "The legacy v1 invite code format is `base64url(payload_json) + \".\" + base64url(hmac_sha256(key, payload_json))`, where `payload_json` carries community id (`c`), a role fixed to `\"member\"` (`r`), an expiry in unix seconds (`e`), and a random nonce (`n`); the HMAC key is derived as `sha256(relay_secret_key_bytes || \"buzz-invite-v1\")`, so rotating the relay's signing keypair invalidates every outstanding v1 invite. v1 codes are multi-use until expiry with no server-side 'used' bit — this is documented in the module's own doc comment as a deliberate, coarse-grained property, not an oversight."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:1-40"
      - "crates/buzz-relay/src/invite_token.rs:107-116"
  - statement: "`verify_invite` (the v1 path) checks the HMAC signature before trusting any field inside the payload, then checks expiry, then that the payload's community id matches the presenting tenant, then that the role is exactly `\"member\"` — rejecting a signed-but-elevated-role payload even though the mint route only ever signs `\"member\"`, as defense against a hypothetical future minting bug. Verification errors are deliberately coarse (`Malformed`, `BadSignature`, `WrongCommunity`, `InvalidRole` all collapse to a generic 403 `invite_invalid` at the HTTP layer; only `Expired` is distinguished) so the endpoint is a poor oracle for forging codes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:151-191"
      - "crates/buzz-relay/src/api/invites.rs:455-465"
  - statement: "buzz-relay's own module doc comment for invite_token.rs states production minting now uses database-backed v2 codes and calls the v1 `mint_invite` test helper (gated `#[cfg(test)]`) something to 'remove ... after the compatibility drain window', so v1 code is present today only to keep verifying codes minted before the v2 migration, not as an active minting path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:124-128"
  - statement: "An operator-configured join policy (`JoinPolicyConfig`: optional Terms/Privacy Markdown, an `age_attestation_required` flag, and a content-derived `version` string) gates both invite claim paths identically: if `state.config.join_policy` is set, a claim without a valid `policy_receipt` is rejected 403 `join_policy_required`, and the receipt must verify against the exact invite code and the current policy version."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:75-86"
      - "crates/buzz-relay/src/api/invites.rs:385-394"
      - "crates/buzz-relay/src/api/invites.rs:467-474"
  - statement: "`POST /api/invites/accept-policy` exchanges an explicit `{code, policy_version, age_confirmed}` acceptance for a short-lived (10 minute) signed receipt via `invite_token::mint_policy_acceptance`; the receipt binds a SHA-256 of the invite code and the policy version, and is rejected 400 if the submitted `policy_version` does not match the relay's current configured version or if age confirmation is required but not given."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:198-226"
      - "crates/buzz-relay/src/invite_token.rs:332-356"
  - statement: "`verify_policy_acceptance` checks the receipt's HMAC signature, its own expiry, and that its bound code-hash and policy version both match the current claim request, rejecting a receipt forged with a different key, bound to a different invite code, or bound to a stale policy version."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:358-389"
  - statement: "`GET /api/join-policy/terms` and `GET /api/join-policy/privacy` render the operator's configured Markdown as standalone, self-contained HTML pages (not JSON), returning 404 when no policy document is configured; raw HTML or inline HTML embedded in the operator's Markdown is escaped to text rather than rendered, so an operator-authored policy document cannot inject markup into the page."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:126-196"
  - statement: "Claim attempts are additionally rate-limited per (community, claimer pubkey) pair by a fixed 60-second sliding window capped at 10 attempts, backed by a bounded-capacity (10,000 distinct keys) moka cache; the comment on the constant explains the bound exists because NIP-98 proves key ownership but not that a key is costly to create, so an unbounded per-key cache would itself be a memory-exhaustion vector for a pre-membership caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:38-46"
      - "crates/buzz-relay/src/api/invites.rs:513-537"
      - "crates/buzz-relay/src/state.rs:37"
      - "crates/buzz-relay/src/state.rs:742-743"
  - statement: "The relay's test suite exercises the full invite API end to end (all gated `#[ignore = \"requires Postgres\"]` except pure-unit tests): owner-mint-then-new-pubkey-claim with idempotent second claim, v2 malformed/unknown code rejection without v1 fallback, side effects published only on `Joined`, mint TTL/max_uses bound validation, non-admin mint rejection, invalid-code claim rejection, cross-community code rejection, and a full join-policy gate walkthrough (missing receipt, forged receipt, cross-invite receipt, stale-version receipt, then a legitimate accept-policy-to-claim flow)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:764-1519"
  - statement: "launchpad/docs/corpus/architecture/containers/web.md (id architecture-containers-web) already documents the client-side half of this same invite flow — the /invite/<code> landing route and web/src/features/invite/invite-api.ts's POST {relay}/api/invites/claim call with a NIP-98 Authorization header and optional join-policy receipt — and does not describe the relay-side handler implementation, so this node references it rather than duplicating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
  - statement: "No architecture/flow node in the merged corpus at this revision covers the relay-side invite/community-provisioning flow; launchpad/docs/corpus/architecture/flows/git-push.md names that flow as an explicit, still-open gap owned by 'separate architecture/flow nodes, none of which exist in the merged corpus at this revision.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md:348"
relationships:
  - type: references
    target: architecture-containers-web
---

# Relay invite HTTP API

This node documents the relay's invite HTTP API — the mint and claim
endpoints, and the associated join-policy acceptance surface — implemented in
`crates/buzz-relay/src/api/invites.rs`, `crates/buzz-relay/src/invite_token.rs`
and `crates/buzz-db/src/store/relay_invite.rs`. It answers: what routes exist,
what each request/response contract is, how tokens are minted and verified,
and how the relay decides who may mint an invite and who may join through
one.

## Responsibility

The invite API lets a relay owner or admin mint a shareable, expiring code
that admits a new pubkey into a NIP-29 community as a `member`, and lets a
joining pubkey redeem that code — deliberately bypassing the relay's general
membership gate, since the whole point is admitting someone who is not yet a
member. NIP-98 proves control of the joining key; the invite code itself (an
HMAC in the legacy v1 format, or a database-backed opaque secret in the
current v2 format) proves an admin authorized the join. An optional
operator-configured join policy (Terms/Privacy acceptance, optional age
attestation) can additionally gate a claim behind a short-lived acceptance
receipt.

## Public interface

| Route | Method | Auth | Contract | Evidence |
|---|---|---|---|---|
| `/api/invites` | POST | NIP-98, caller must be `owner`/`admin` | Mint a v2 invite; body `{ttl_secs?, max_uses?}`; returns `{code, expires_at, max_uses, uses_remaining, url}` | `crates/buzz-relay/src/api/invites.rs:276-349` |
| `/api/invites/claim` | POST | NIP-98, membership-gate exempt | Claim an invite; body `{code, policy_receipt?}`; returns `{status: "joined"\|"already_member", community_id, host, role}` or a 403 error body | `crates/buzz-relay/src/api/invites.rs:351-511` |
| `/api/join-policy` | GET | none | Returns the tenant's configured join policy (Terms/Privacy Markdown, age-attestation flag, version), or `{}` if none configured | `crates/buzz-relay/src/api/invites.rs:111-124` |
| `/api/join-policy/terms` | GET | none | Terms of Service as a standalone HTML page; 404 if unconfigured | `crates/buzz-relay/src/api/invites.rs:126-138` |
| `/api/join-policy/privacy` | GET | none | Privacy Policy as a standalone HTML page; 404 if unconfigured | `crates/buzz-relay/src/api/invites.rs:141-147` |
| `/api/invites/accept-policy` | POST | NIP-98 | Exchange explicit `{code, policy_version, age_confirmed}` acceptance for a 10-minute signed receipt; 400 on version mismatch or missing age confirmation | `crates/buzz-relay/src/api/invites.rs:198-226` |

All six routes are registered in the relay's Axum router at
`crates/buzz-relay/src/router.rs:106-123`.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-core` (`invite` module) | Shared invite constants (TTL/use bounds, v2 code encode/validate/hash) used by both the relay and the database layer | `crates/buzz-relay/Cargo.toml`; `crates/buzz-core/src/invite.rs` |
| `buzz-db` (`store::relay_invite`) | v2 opaque invite persistence and the atomic claim transaction | `crates/buzz-relay/Cargo.toml`; `crates/buzz-db/src/store/relay_invite.rs` |
| `buzz-auth` | NIP-98 signature verification and replay-guard checking (`bridge::verify_bridge_auth_with_options`, `bridge::check_nip98_replay`) used by the shared `authenticate` helper | `crates/buzz-relay/src/api/invites.rs:228-261` |
| `nostr` | Pubkey/keypair types and HMAC key material derivation source (`nostr::Keys`) | `crates/buzz-relay/src/invite_token.rs:111-116` |
| `moka` | Bounded, expiring per-pubkey claim rate-limit cache | `crates/buzz-relay/src/state.rs:742-743` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `web` (desktop-adjacent browser client) | `web/src/features/invite/invite-api.ts` calls `POST /api/invites/claim` from the `/invite/<code>` landing page | `launchpad/docs/corpus/architecture/containers/web.md` |

## Boundary

This node does not describe:
- The client-side invite landing page or its call into this API — see
  `architecture-containers-web` (`launchpad/docs/corpus/architecture/
  containers/web.md`), which already documents that surface.
- The relay-wide NIP-29 membership model, roles, or the kind:9030
  add-member event path this API's mint-authz mirrors — that is a separate,
  broader concern than one HTTP API surface.
- The `relay_invites` table's SQL schema/migration as its own artifact — no
  second hand-authored canonical corpus document is created here, per issue
  #1274's own out-of-scope note.
- Install/usage instructions for a human running the relay — the relay has
  no dedicated crate `README.md` for this surface at this revision.

## Relationships

- references: `architecture-containers-web` — the client-side half of the
  same invite flow, so this node's Dependencies table above links to it
  rather than restating its content.
- No `part-of` or `depends-on` target exists yet: no architecture-component
  or flow-level corpus node covering relay-side invite/community-provisioning
  is present on `origin/launchpad` at this revision (confirmed against
  `launchpad/docs/corpus/architecture/flows/git-push.md`'s own open-gap note
  naming exactly this absence).

## Scope and omissions

**This node covers** the relay's invite HTTP API surface: its six routes,
request/response contracts, the v1 HMAC and v2 database-backed token
formats, mint authorization, claim exemption from the membership gate, the
join-policy acceptance-receipt gate, per-pubkey claim rate limiting, and the
NIP-43 side effects a successful claim publishes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The web client's invite landing page and its call into this API | `architecture-containers-web` (`launchpad/docs/corpus/architecture/containers/web.md`) |
| The relay-wide NIP-29 membership/role model this API's authz mirrors | Not yet a corpus node at this revision |
| The relay-side invite/community-provisioning flow as an end-to-end sequence | Not yet a corpus node; named as an open gap by `architecture/flows/git-push.md` |
| The `relay_invites` table's SQL schema/migration | Out of scope for this task (issue #1274) |

**Expected but not verified when this node was written:**
- Whether any operator-facing documentation (outside this corpus) describes
  configuring `JoinPolicyConfig` was not checked — this node cites the struct
  and its consuming code only, not any deployment guide.
- The precise removal timeline for the v1 HMAC compatibility path was not
  found beyond the "drain window" language in `invite_token.rs`'s own doc
  comment; no issue or ADR pinning a removal date was located.
