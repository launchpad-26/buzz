---
id: layers-authentication-api-token
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The `api_tokens` table stores one row per token: `community_id` + `id` as primary key, a 32-byte `token_hash` (CHECK constraint enforces exactly 32 bytes — a SHA-256 digest), `owner_pubkey` foreign-keyed to `users (community_id, pubkey)`, a `name`, JSONB `scopes`, an optional JSONB `channel_ids`, `created_at`/`expires_at`/`last_used_at`/`revoked_at`/`revoked_by`, and a `created_by_self_mint` boolean, with a UNIQUE index on `(community_id, token_hash)`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`crates/buzz-db/src/api_token.rs` implements the token CRUD surface: `create_api_token`, an atomic `create_api_token_if_under_limit` that enforces a 10-active-token-per-(community, owner) quota via a conditional INSERT (no separate count-then-insert race), `get_api_token_by_hash_including_revoked`, `list_tokens_by_owner`, `revoke_token`, and `revoke_all_tokens` — every function takes `community_id` as an explicit parameter and scopes its query to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/api_token.rs"
  - statement: "The token lookup is keyed on `(community_id, token_hash)`, matching the storage-layer UNIQUE index, and two dedicated tests (`lookup_by_hash_is_scoped_to_community`, `active_lookup_by_hash_is_scoped_to_community`) insert the same 32-byte hash into two different communities and assert a community-scoped lookup returns only that community's row — proving a token minted in community A cannot resolve as valid in community B even under an adversarial same-hash collision."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/api_token.rs"
  - statement: "`crates/buzz-auth/src/scope.rs` defines the `Scope` enum a token's `scopes` array is drawn from — 16 known variants (e.g. `messages:read`, `files:write`, `admin:channels`) plus an `Unknown(String)` catch-all for forward compatibility — and its own test asserts `Scope::all_known().len() == 16` with no duplicates."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
  - statement: "`crates/buzz-relay/src/api/bridge.rs`'s `verify_bridge_auth_with_options` tries NIP-98 signed-event auth (`Authorization: Nostr <base64>`) first and, only when the `require_auth_token` config flag is false, falls back to an unauthenticated-signature `X-Pubkey` dev-mode header; `require_auth_token` gates that NIP-98-vs-dev-mode choice for the REST bridge (`/events`, `/query`, `/count`) and is unrelated to minting or consuming an `api_tokens` row, despite the similar name."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`crates/buzz-relay/src/router.rs` registers no `/tokens` or `/api/tokens` route, and `crates/buzz-relay/src/api/` contains no `tokens` module (its files are `admin/`, `bridge.rs`, `events.rs`, `git/`, `invites.rs`, `media.rs`, `mesh_demo.rs`, `mod.rs`, `nip05.rs`, `operator.rs`, `workflows.rs`) — there is no HTTP surface today by which a client can mint an API token bound to a community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Commit 0701f47f4a31a904ebcd9f360cbd6aadaff9d784 (PR #1444, \"fix(relay): remove media bearer-token auth\") deleted `resolve_upload_scopes` from `crates/buzz-relay/src/api/media.rs`, which had been the sole production consumer of an API token: it read the `X-Auth-Token: buzz_*` header, SHA-256-hashed it, called `get_api_token_by_hash_including_revoked`, checked revocation/expiry/owner-pubkey match, and derived upload `Scope`s from the stored `scopes` array. That commit replaced token-scope-based upload authorization with NIP-43 relay-membership authorization instead."
    entry_class: FACT
    evidence:
      - "commit 0701f47f4a31a904ebcd9f360cbd6aadaff9d784"
  - statement: "At the recorded revision, `get_api_token_by_hash` and `get_api_token_by_hash_including_revoked` have no callers anywhere in the repository outside `crates/buzz-db/src/api_token.rs` itself (their own unit tests) — confirmed by a repo-wide grep for both symbol names."
    entry_class: FACT
    evidence:
      - "grep_repo('get_api_token_by_hash', '*.rs') -> matches only in crates/buzz-db/src/api_token.rs (definitions and its own unit tests) and a stale doc-comment in crates/buzz-test-client/tests/conformance_multitenant.rs; no other .rs file in the repository calls either function"
  - statement: "`crates/buzz-test-client/tests/conformance_multitenant.rs`'s `api_tokens_nip98_replay::token_minted_in_a_does_not_authorize_in_b` test is deliberately doc-only, and its module comment states directly that \"the api_token mint surface does not exist on the wire in buzz-relay\" and cites the same router/module-listing facts as this node, while also citing a stale line reference (`media.rs:638`) to the consumer removed by PR #1444 — this node's own citations were re-verified against current `media.rs` rather than trusted from that comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "`crates/buzz-auth` implements two separate, currently-enforced signed-event authentication mechanisms: NIP-42 challenge/response (`verify_nip42_event`, `crates/buzz-auth/src/nip42.rs`, for WebSocket connections — kind:22242 AUTH events are never stored or logged because they may contain bearer tokens) and NIP-98 signed-HTTP-request auth (`verify_nip98_event`, called from `crates/buzz-relay/src/api/bridge.rs`'s `verify_bridge_auth_with_options`, for the REST bridge). Neither is a bearer token in the `api_tokens` sense — both derive from a signature over the specific request/challenge, not a stored shared secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The `created_by_self_mint` column and the atomic under-quota insert function (`create_api_token_if_under_limit`, guarding a 10-per-owner cap) suggest the schema was built anticipating a future self-service minting flow distinct from an operator/admin-issued path, though no route exercises either path today — this is reasoned from the shape of the schema and code, not read directly from a design document, so it is inference rather than fact."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/api_token.rs"
    confidence: 0.55
  - statement: "Issue #1023's Definition of Done requires that the document defines the term in one sentence, states boundaries/non-goals, links to related concepts/implementation/verification, and uses examples only to clarify — not to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1023 definition of done"
relationships:
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# API token

An **API token** is a data-model construct in Buzz for scoped, revocable,
community-bound bearer-style credentials — implemented end-to-end in the
storage layer, but, at the time of writing, wired to no HTTP route on
either end: nothing mints one, and nothing verifies one to authorize a
request.

## Definition

An API token is an opaque `buzz_`-prefixed secret string. The relay never
stores the raw value — only its SHA-256 digest, as a 32-byte `token_hash` in
the `api_tokens` table, alongside the owning Nostr pubkey, a human-readable
`name`, a JSON array of `Scope` strings (e.g. `files:read`, `messages:write`),
an optional list of `channel_ids` narrowing it further, and optional
`expires_at`/`revoked_at` timestamps. Every row also carries `community_id`,
and the table's unique index is `(community_id, token_hash)` — a token is a
property of one community, not a global credential, and the same hash may
validly exist in two different communities as two unrelated tokens.

**What it is not.** It is not Buzz's primary authentication mechanism. That
role belongs to Nostr signed events — NIP-42 challenge/response for
WebSocket connections and NIP-98 signed-request auth for HTTP, both
implemented in `crates/buzz-auth` — and an API token, where it was once
consumed, only ever supplemented that
signature-based identity with a *scope* narrower than "whatever this pubkey
can already do." It is also not the same thing as the `require_auth_token`
relay config flag: that flag decides whether the REST bridge accepts an
unauthenticated `X-Pubkey` dev-mode header instead of a real NIP-98 signature
— a question about *identity*, answered before any API token would ever be
looked up — and has no code path connecting it to `api_tokens` lookups.

**Current status: implemented, unconsumed.** The full CRUD surface exists in
`crates/buzz-db/src/api_token.rs` — create (with an atomic 10-token-per-owner
quota), community-scoped hash lookup (including a revoked-inclusive variant),
list, and revoke (single or all) — and the storage layer's community-scoping
guarantee is directly tested. But `crates/buzz-relay`'s router registers no
route to mint a token, and the one route that used to *consume* one — the
Blossom media-upload path's `X-Auth-Token: buzz_*` header check — was removed
in PR #1444 in favor of NIP-43 relay-membership authorization. As of the
recorded revision, `get_api_token_by_hash`/`get_api_token_by_hash_including_revoked`
have zero callers anywhere in the repository outside their own unit tests.

## Background

API tokens were originally consumed by the media-upload path: a client sent
Blossom auth (proving upload-hash intent) in `Authorization`, and an API
token in `X-Auth-Token`, and the extractor resolved the token's `scopes` to
decide whether the upload was permitted (`Scope::FilesWrite`). PR #1444
("remove media bearer-token auth") deleted that resolution function and
replaced the authority check with NIP-43 relay membership — whether the
Blossom-auth signer's Nostr pubkey belongs to the community — instead. The
`api_tokens` table, its CRUD functions, and their community-scoping tests
were left in place; only the consumer was removed. Nothing in the removal
commit or its history explains whether a token-scoped consumer is expected to
return, so this node states the current fact and does not speculate about
product direction.

## Use cases

A reader most needs this concept in two situations:

- **Reading code that references `api_tokens`, `ApiTokenRecord`, or
  `Scope`** and needing to know whether that code path is live. At the
  recorded revision, the honest answer for any relay request-handling code is
  *no* — trace back to `crates/buzz-db/src/api_token.rs`'s own unit tests
  before assuming a caller exists elsewhere.
- **Distinguishing "API token" from Buzz's actual bearer-style auth
  surfaces.** A NIP-98 signed event *is* effectively a short-lived bearer
  credential for one HTTP request, and could be confused with an API token by
  name alone; they are different mechanisms with different lifetimes, and
  only NIP-98/NIP-42 are enforced anywhere today.

## Comparison

| Mechanism | Scope | Lifetime | Enforced today? |
|---|---|---|---|
| NIP-42 (WebSocket) | Full scope set for the authenticated pubkey | Per-connection | Yes |
| NIP-98 (HTTP) | Full scope set for the authenticated pubkey | Per-request (signature covers method + URL + body) | Yes |
| API token (`api_tokens` row) | Narrowed to the token's stored `scopes`/`channel_ids` | Until revoked or `expires_at` | No — data layer only; no mint route, no consumer |

## Related resources

See the `relationships` in this node's front matter: `architecture-flows-media-upload`
(the flow whose history is this node's direct evidence for the "unconsumed"
claim) and `architecture-principles-community-is-security-boundary` (the
`(community_id, token_hash)` scoping is that principle's instance here).

## Scope and omissions

**This document covers** what an API token is as a Buzz data-model concept:
its stored shape, its community/pubkey/scope binding, its CRUD surface, and
its current unconsumed status, with the boundary against NIP-42/NIP-98 and
against the unrelated `require_auth_token` config flag.

**This document does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full NIP-98/NIP-42 authentication flows themselves | `architecture-flows-websocket-authentication`, and a future HTTP-authentication flow node if one is written |
| Whether or when a mint route or a new consumer will be added | A product decision not yet made at the recorded revision |
| The Blossom media-upload flow's current (NIP-43-based) authorization in full | `architecture-flows-media-upload` |
| The `Scope` enum's full member list and per-scope enforcement status elsewhere in the codebase (e.g. `repos:write` is enforced on WebSocket ingest but not on git HTTP push routes) | Not yet documented as its own corpus node |

**Expected but not verified when this node was written:** whether any
non-relay Buzz component (desktop, mobile, CLI) has client-side code
expecting to send or manage an API token — this node only traced the
relay-side (`crates/buzz-relay`, `crates/buzz-db`) surface, since that is
where the term is defined and where the removed consumer lived.
