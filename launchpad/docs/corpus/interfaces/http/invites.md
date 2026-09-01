---
id: interfaces-http-invites
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
  - statement: "The relay's HTTP invites surface registers six JSON/HTML routes plus one SPA landing-page path in the router: POST /api/invites (mint_invite), GET /api/join-policy (join_policy), GET /api/join-policy/terms (join_policy_terms), GET /api/join-policy/privacy (join_policy_privacy), POST /api/invites/accept-policy (accept_policy), POST /api/invites/claim (claim_invite), and GET /invite/{code} matched by is_invite_landing_path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:106-123"
      - "crates/buzz-relay/src/router.rs:238-244"
  - statement: "POST /api/invites mints an invite code. The caller must authenticate via NIP-98 (tenant-bound to the request's Host header) and must hold the owner or admin role in that community, or the handler returns 403 FORBIDDEN with body {\"error\":\"only relay owners and admins can create invites\"}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:280-300"
  - statement: "MintInviteRequest accepts an optional ttl_secs (default 72h via DEFAULT_INVITE_TTL_SECS, must fall between MIN_INVITE_TTL_SECS=60s and MAX_INVITE_TTL_SECS=30 days) and an optional max_uses (1..=MAX_INVITE_USES=10000, omitted/null meaning unlimited); validate_mint_request rejects out-of-range values with 400 BAD_REQUEST before any database write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:48-87"
      - "crates/buzz-core/src/invite.rs:11-25"
  - statement: "A successful mint returns 200 with JSON {code, expires_at (unix seconds), max_uses, uses_remaining, url}, where url is a shareable {scheme}://{tenant-host}/invite/{code}, https when the deployment's relay_url starts with wss://, else http."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:316-348"
  - statement: "POST /api/invites/claim redeems a code and is deliberately exempt from the relay-membership gate applied elsewhere, since the joining caller is by definition not yet a member; NIP-98 proves control of the joining pubkey and the invite code's own signature/hash proves an admin authorized the join."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:1-13"
      - "crates/buzz-relay/src/api/invites.rs:351-362"
  - statement: "Claim requests are routed by exact code prefix: a code starting with buzz_core::invite::V2_PREFIX (\"v2.\") uses the database-backed opaque-token path (validate_v2_code, hash_v2_code, Db::claim_relay_invite); every other code is verified as a legacy v1 stateless HMAC token via invite_token::verify_invite. A v2.-prefixed code that fails v2 validation is never fallen back to v1 verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:377-465"
      - "crates/buzz-core/src/invite.rs:11-58"
  - statement: "A claim is idempotent for an already-joined pubkey: the v2 path's ClaimOutcome::AlreadyMember and the v1 path's was_inserted=false both return 200 with {\"status\":\"already_member\"} rather than an error, and the NIP-43 side-effect publications (publish_nip43_member_added, publish_nip43_membership_list) fire only on a genuinely new join, never on a repeat claim of the same code by the same pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:412-452"
      - "crates/buzz-relay/src/api/invites.rs:476-510"
  - statement: "Claim failure modes map to distinct error strings in a 403 FORBIDDEN JSON body's error field: invite_invalid (malformed, unknown, or bad-signature code), invite_expired, invite_exhausted (v2 max_uses reached), and join_policy_required (operator-configured join policy has no matching acceptance receipt); a rate-limited caller instead receives 429 TOO_MANY_REQUESTS before the code is even parsed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:443-473"
      - "crates/buzz-relay/src/api/invites.rs:364-369"
  - statement: "A v1 code minted for one community fails claim verification when presented against a different community's host (InviteError::WrongCommunity), confirmed end-to-end by the test code_minted_for_one_community_fails_on_another."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:81-101"
      - "crates/buzz-relay/src/api/invites.rs:1443-1486"
  - statement: "Claim attempts are rate-limited per (community, claimer pubkey) pair to CLAIM_RATE_LIMIT=10 attempts per CLAIM_RATE_WINDOW=60-second fixed window, backed by a capacity-bounded (CLAIM_RATE_CACHE_CAPACITY=10,000 entries) in-process cache so a pre-membership caller who can cheaply mint fresh Nostr keypairs cannot turn the limiter itself into an unbounded-memory vector."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:38-46"
      - "crates/buzz-relay/src/api/invites.rs:513-537"
  - statement: "GET /api/join-policy returns the operator-configured join policy (terms/privacy Markdown, whether age attestation is required, and a version string) or {} if none is configured, and requires no authentication."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:111-124"
  - statement: "GET /api/join-policy/terms and GET /api/join-policy/privacy render the configured Markdown as standalone HTML pages, with any raw or inline HTML events in that Markdown escaped to plain text before rendering (so an operator authors a policy document, not injectable markup), returning 404 NOT_FOUND when no such document is configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:126-196"
  - statement: "POST /api/invites/accept-policy exchanges an explicit acceptance (code, policy_version, optional age_confirmed) for a short-lived receipt bound to that code and policy version, returning 400 BAD_REQUEST if the submitted policy_version does not match the operator's current version or if age confirmation was required but not given."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:99-109"
      - "crates/buzz-relay/src/api/invites.rs:198-226"
  - statement: "When an operator-configured join policy exists, both the v1 and v2 claim paths require a policy_receipt in the claim body, verified against the code and current policy version via invite_token::verify_policy_acceptance, and reject with 403 join_policy_required otherwise -- a receipt minted by accept-policy is required, a bare checkbox flag in the claim body is not accepted as a substitute."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:385-394"
      - "crates/buzz-relay/src/api/invites.rs:467-474"
  - statement: "Every /api/invites* endpoint authenticates through a shared authenticate() helper: it binds the tenant community from the request's Host header, then requires a NIP-98 Authorization: Nostr <base64 event> header with no X-Pubkey dev-mode fallback and a payload tag covering the POST body's SHA-256 hash, then checks the event ID for replay against a Redis-backed seen-set scoped to that tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:230-261"
      - "crates/buzz-relay/src/api/bridge.rs:72-135"
  - statement: "The URL a NIP-98 signature must cover is derived per-tenant (nip98_expected_url substitutes the request's bound tenant host, not the deployment's static config.relay_url), closing a cross-host token-reuse hole the function's own doc comment names; scheme is https when the deployment's relay_url starts with wss://, else http."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:190-206"
  - statement: "Mint authorization (owner/admin role required) mirrors the authorization already enforced for kind:9030 (RELAY_ADMIN_ADD_MEMBER, the Nostr-event admin add-member command) rather than defining a separate authorization model for the HTTP surface -- the module doc comment and the handler's own comment both state this explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:1-11"
      - "crates/buzz-relay/src/api/invites.rs:286-300"
      - "crates/buzz-core/src/kind.rs:389"
  - statement: "A successful claim publishes two NIP-43 side-effect events into the community -- KIND_NIP43_MEMBER_ADDED (8000) and KIND_NIP43_MEMBERSHIP_LIST (13534), both defined in buzz-core's kind registry -- so realtime WebSocket subscribers observe the new member without polling the HTTP surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:412-427"
      - "crates/buzz-core/src/kind.rs:398"
      - "crates/buzz-core/src/kind.rs:400"
  - statement: "GET /invite/{code} is not a JSON API call; on the public (non-admin) host, when the deployment has a configured web_dir and the path matches is_invite_landing_path (exactly one non-empty, slash-free segment after /invite/), the router's SPA fallback serves the web bundle's index.html regardless of whether serve_git_web_gui is enabled. Without a configured web_dir, or on the admin host, the same path resolves to 404."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:155-201"
      - "crates/buzz-relay/src/router.rs:238-244"
  - statement: "No Nostr Implementation Possibility (NIP) defines an invite-code event or endpoint; searching this repository's own invite-related source turns up NIP-98 (HTTP Auth, already implemented and reused here for request authentication) as the only externally specified protocol this interface's operations point to, with the invite code format itself (payload shape, HMAC/opaque-token construction) being a Buzz-specific contract documented only in this repository's own module doc comments."
    entry_class: INFERENCE
    confidence: 0.75
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:1-38"
      - "crates/buzz-core/src/invite.rs:1-6"
  - statement: "Root AGENTS.md documents the relay's HTTP surface as deliberately narrow and directs new feature work toward a Nostr event kind rather than a new HTTP endpoint; the invites surface predates that guidance's application here and is treated in this node as an existing exception rather than a template for future HTTP additions."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "AGENTS.md (repository root), section 'Prefer Nostr events over new HTTP endpoints'"
---

# HTTP invites: interface

This node documents the relay's HTTP invites surface -- the boundary across which a
relay owner/admin (the minting side) and a not-yet-a-member joining client (the
claiming side) exchange invite codes and, optionally, join-policy acceptance, over
HTTP + JSON (plus one HTML landing page), authenticated by NIP-98. It is a
Buzz-specific HTTP contract layered on top of NIP-98, not a document generated from
or validated against any external interface specification -- no OpenAPI or AsyncAPI
document exists in this repository (per `corpus-template-interface`'s own evidence
ledger, unchanged at this node's recorded revision).

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /api/invites` | `crates/buzz-relay/src/api/invites.rs#mint_invite` (router: `crates/buzz-relay/src/router.rs:107`) | Owner/admin mints an invite code (`ttl_secs`, `max_uses` optional); returns `{code, expires_at, max_uses, uses_remaining, url}`. |
| `GET /api/join-policy` | `crates/buzz-relay/src/api/invites.rs#join_policy` (router: `router.rs:108`) | Unauthenticated read of the operator's configured join policy, or `{}`. |
| `GET /api/join-policy/terms` | `crates/buzz-relay/src/api/invites.rs#join_policy_terms` (router: `router.rs:111-114`) | Terms of Service rendered as a standalone HTML page; 404 if unconfigured. |
| `GET /api/join-policy/privacy` | `crates/buzz-relay/src/api/invites.rs#join_policy_privacy` (router: `router.rs:115-118`) | Privacy Policy rendered as a standalone HTML page; 404 if unconfigured. |
| `POST /api/invites/accept-policy` | `crates/buzz-relay/src/api/invites.rs#accept_policy` (router: `router.rs:119-122`) | Exchanges explicit policy acceptance for a short-lived, code-bound receipt. |
| `POST /api/invites/claim` | `crates/buzz-relay/src/api/invites.rs#claim_invite` (router: `router.rs:123`) | Joining pubkey redeems a code (plus `policy_receipt` if required); returns `{status, community_id, host, role}`. |
| `GET /invite/{code}` | `crates/buzz-relay/src/router.rs#is_invite_landing_path`, `should_serve_spa` (`router.rs:155-201`, `238-244`) | Static SPA landing page (not JSON); the client-side app reads `{code}` from the path and drives the mint/claim calls above. |

Token format, HMAC key derivation and the v1/v2 code split are owned by
`crates/buzz-relay/src/invite_token.rs` and `crates/buzz-core/src/invite.rs`; this
node cites, but does not restate, their wire format.

## Contract and stability

- **Authentication.** Every `/api/invites*` route requires NIP-98 (`Authorization:
  Nostr <base64 event>`), tenant-bound to the request's `Host` header, with no
  `X-Pubkey` dev-mode fallback and a mandatory `payload` tag covering the POST
  body's hash; requests are additionally checked for replay against a
  tenant-scoped Redis seen-set. `GET /api/join-policy{,/terms,/privacy}` require no
  authentication -- they serve operator-authored public policy text.
- **Authorization.** `POST /api/invites` (mint) requires the caller hold `owner` or
  `admin` role in the tenant community, mirroring the authorization already
  enforced for kind:9030 (`RELAY_ADMIN_ADD_MEMBER`). `POST /api/invites/claim` is
  deliberately open to any NIP-98-authenticated pubkey -- membership is exactly
  what a successful claim grants, so gating claim on membership would be
  circular.
- **Idempotency.** A claim of a code the caller has already redeemed returns
  `200 {"status":"already_member"}` rather than an error, and does not re-publish
  the NIP-43 side-effect events. A claim can be retried safely by a client that is
  unsure whether an earlier attempt succeeded.
- **Ordering.** A successful new join publishes `KIND_NIP43_MEMBER_ADDED` (8000)
  then `KIND_NIP43_MEMBERSHIP_LIST` (13534) as side effects of the same request; a
  failure to publish either is logged (`tracing::warn!`) but does not roll back the
  membership grant or fail the HTTP response -- the HTTP response's success is
  authoritative over the WebSocket fan-out's success.
- **Versioning/compatibility.** Claim codes carry their own version inside the code
  string: a `v2.`-prefixed code always uses the current database-backed path, and
  every other code is treated as the legacy v1 HMAC format -- there is no
  fallback from an invalid `v2.` code to v1 verification. No explicit
  request/response schema-versioning scheme (e.g. an API version header) was
  found for the JSON bodies themselves; new optional fields (`ttl_secs`,
  `max_uses`, `policy_receipt`) are added with `#[serde(default)]`, which is
  additive-compatible but not a documented contract -- see *Scope and omissions*.
- **Error semantics.** Validation errors are `400 BAD_REQUEST`; authorization
  failures are `403 FORBIDDEN` (mint) or a coarse `403 FORBIDDEN` with an
  `invite_invalid`/`invite_expired`/`invite_exhausted`/`join_policy_required`
  `error` code (claim -- deliberately coarse so the endpoint is a poor oracle for
  guessing which failure mode occurred); rate limiting is `429 TOO_MANY_REQUESTS`;
  unconfigured policy documents are `404 NOT_FOUND`; unexpected/database errors
  are `500`-class via `internal_error`.

## Boundary

This node does not describe:
- The v1/v2 invite code's own wire format, HMAC construction, or database
  persistence -- that is `crates/buzz-relay/src/invite_token.rs` and
  `crates/buzz-core/src/invite.rs`'s own documented contract, cited above but not
  restated.
- The wire contract of `KIND_NIP43_MEMBER_ADDED` (8000) or
  `KIND_NIP43_MEMBERSHIP_LIST` (13534) themselves (tag shape, content semantics) --
  no event-kind-shaped corpus node exists for either at this node's recorded
  revision; this node only notes that a successful claim publishes them.
- Field-by-field, domain-expert-depth API parameter cataloguing for every JSON
  body -- per `corpus-template-interface`'s own boundary, that depth (if the
  corpus ever builds it) belongs to a reference-shaped node, not this one.
- The Nostr community/channel membership model in general (`crates/buzz-core/src/tenant.rs`,
  relay-membership gating elsewhere in the relay) -- this node covers only the
  invite-specific HTTP surface that grants membership, not membership's full
  lifecycle.

## Relationships

None declared. At this node's recorded revision, `origin/launchpad`'s corpus tree
contains no `interfaces-events`-typed instance node and no event-kind node for
kind:8000 or kind:13534 to `references`, and no broader capability/architecture
node was identified as an unambiguous `part-of` target for this specific surface.
The first event-kind node drafted for either NIP-43 side-effect kind, or the first
sibling interface node, is the natural moment to add a `references` edge back to
this one.

## Scope and omissions

**This node covers** the relay's HTTP invites surface: the six `/api/invites*` and
`/api/join-policy*` JSON/HTML routes plus the `/invite/{code}` SPA landing path,
their authentication (NIP-98) and authorization (owner/admin for mint, open for
claim) requirements, request/response shapes, idempotency and ordering guarantees,
the v1/v2 code-format split at the routing level (without restating the format
itself), rate limiting, and the NIP-43 side effects a successful claim triggers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The v1/v2 invite code's own wire format and persistence | `crates/buzz-relay/src/invite_token.rs`, `crates/buzz-core/src/invite.rs` |
| `KIND_NIP43_MEMBER_ADDED` / `KIND_NIP43_MEMBERSHIP_LIST` wire contracts | not yet a corpus node (none exists at this node's recorded revision) |
| Domain-expert-depth, field-by-field JSON parameter cataloguing | a future reference-shaped node, per `corpus-template-interface`'s own boundary (unresolved corpus-wide, see `#1346`/`#1532`) |
| General relay-membership gating and tenant/community binding beyond what invites use | `crates/buzz-core/src/tenant.rs` and the relay's broader auth/membership code, not documented as their own corpus node here |

**Expected but not verified when this node was written:**
- **No explicit, documented API-versioning policy for these JSON bodies was
  found.** New optional request fields are added additive-compatibly
  (`#[serde(default)]`), and this node infers that as the working practice, but no
  code comment or standard states a versioning contract the way `buzz-cli`'s exit
  codes are documented in root `AGENTS.md`.
- **Whether any NIP anywhere defines an invite-style event was not exhaustively
  checked against the full NIP corpus** (`nostr-protocol/nips` on GitHub) -- the
  claim that none does rests on this repository's own code and doc comments
  finding no such reference, not on reading every NIP directly, so it is recorded
  as `INFERENCE`, not `FACT`.
- **No corpus node yet exists to `references` for the NIP-43 side-effect kinds**
  this interface publishes into (8000, 13534) -- confirmed absent at the recorded
  revision, but this node was not re-checked against a later revision where one
  might have since merged.
