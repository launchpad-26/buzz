---
id: layers-authorization-scopes
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
  - statement: "`Scope` is a Rust enum with 16 named variants covering messages, channels, users, jobs, subscriptions, files and repos (each typically split into a `*Read`/`*Write` pair, plus `AdminChannels` and `AdminUsers`), plus an `Unknown(String)` variant that preserves any scope string this build does not recognise."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs:16-61"
  - statement: "Each known variant has a canonical wire-format string produced by `Scope::as_str()` and `Display` (e.g. `MessagesRead` -> `\"messages:read\"`, `AdminChannels` -> `\"admin:channels\"`); `Scope::from_str` is infallible (`Err = std::convert::Infallible`) and maps any string it does not recognise to `Scope::Unknown(string)` rather than rejecting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs:113-135"
      - "crates/buzz-auth/src/scope.rs:143-167"
  - statement: "`scope.rs`'s own module doc-comment and the doc-comment on `Scope` itself both assert scopes are 'stored as `TEXT[]` in the database'."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs:1-14"
  - statement: "The actual schema disagrees with that comment: `migrations/0001_initial_schema.sql`'s `api_tokens` table declares `scopes JSONB NOT NULL`, not a Postgres `TEXT[]` array, and `buzz_db::api_token::create_api_token` serializes its `scopes: &[String]` parameter with `serde_json::to_value` before binding it as that JSONB column."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:472-489"
      - "crates/buzz-db/src/store/api_token.rs:18-60"
  - statement: "The `TEXT[]` comment describes a storage shape this build does not use; JSONB is what the DDL and the insert code actually implement, so a reader should trust the migration and `create_api_token`, not the comment, for the on-disk representation."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:478"
      - "crates/buzz-db/src/store/api_token.rs:18-60"
      - "crates/buzz-auth/src/scope.rs:12-14"
    confidence: 0.9
  - statement: "`AuthContext` (the result of a successful authentication, bound to a connection) carries `scopes: Vec<Scope>` and a `has_scope(&self, scope: &Scope) -> bool` method that checks containment."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:62-87"
  - statement: "`AuthService::verify_auth_event` (the NIP-42 WebSocket challenge/response path) grants every successfully authenticated connection `Scope::all_known()` unconditionally — the full 16-variant set — with the doc-comment explaining that in 'pure Nostr mode' per-channel access is enforced separately by NIP-29 membership, not by narrowing scopes."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:115-143"
  - statement: "`crates/buzz-relay/src/api/bridge.rs`'s `submit_event` handler (the `POST /events` HTTP bridge path, authenticated via NIP-98) builds its `IngestAuth::Http` with `scopes: buzz_auth::Scope::all_known()` too, with the same 'Pure Nostr: full scopes, channel access via membership' comment — so both live authentication paths in this build grant the full scope set unconditionally, not a token- or grant-derived subset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:832-837"
  - statement: "`buzz_auth::access::require_scope(scopes, required)` returns `Err(AuthError::InsufficientScope { required, have })` unless `scopes.contains(&required)`; `check_read_access` requires `Scope::MessagesRead` before checking channel membership, and `check_write_access` requires `Scope::MessagesWrite` the same way — scope and channel membership are two separate, both-must-pass gates, not one merged check."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs:59-101"
  - statement: "`crates/buzz-relay/src/handlers/ingest.rs`'s `required_scope_for_kind(kind, event)` maps every event kind this relay ingests to the single `Scope` required to submit it (e.g. text notes and long-form posts require `MessagesWrite`, NIP-29 group create/edit requires `ChannelsWrite` or `AdminChannels` depending on tag content, relay membership admin commands require `AdminUsers`), and returns `Err` for any kind it does not recognise, which the caller treats as a rejection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:344-452"
  - statement: "`crates/buzz-relay/src/handlers/event.rs` also checks scopes directly (outside `required_scope_for_kind`) for two cases: ephemeral event kinds require `Scope::MessagesWrite` before further processing, and `KIND_AGENT_OBSERVER_FRAME` requires `Scope::MessagesWrite` before dispatch to its own handler — both checks are skipped only when the connection's scope list is empty (dev-mode/no-token connections), not bypassed for a populated-but-insufficient list."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:679-710"
  - statement: "`buzz-db`'s `api_token` module implements full CRUD for API tokens (`create_api_token`, `create_api_token_if_under_limit`, `get_api_token_by_hash`, `get_api_token_by_hash_including_revoked`, `list_tokens_by_owner`, `revoke_token`, `revoke_all_tokens`) against the `api_tokens` table, and its own two community-scoping unit tests (`lookup_by_hash_is_scoped_to_community`, `active_lookup_by_hash_is_scoped_to_community`) pass against that table today."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/api_token.rs:18-60"
      - "crates/buzz-db/src/store/api_token.rs:72-129"
      - "crates/buzz-db/src/store/api_token.rs:147-306"
      - "crates/buzz-db/src/store/api_token.rs:706"
      - "crates/buzz-db/src/store/api_token.rs:769"
  - statement: "Neither `create_api_token` nor `get_api_token_by_hash`/`get_api_token_by_hash_including_revoked` has any call site inside `crates/buzz-relay` at this revision (repo-wide grep for both symbols across `crates/` returns matches only inside `buzz-db` itself and its own doc-comments), and `crates/buzz-relay/src/router.rs`'s full route list — `/`, `/info`, `/.well-known/nostr.json`, `/health`, `/_liveness`, `/_readiness`, `/events`, `/query`, `/count`, `/hooks/{id}`, plus the media/git/git-policy sub-routers — has no `/tokens` route."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:62-90"
  - statement: "Because no route mints a token and no handler looks one up, the `api_tokens.scopes` mechanism — the one place a caller could legitimately hold fewer than all 16 scopes — has no live entry point in this build; every real authenticated connection is granted `Scope::all_known()` regardless of what the `api_tokens` table could in principle store."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:835"
      - "crates/buzz-auth/src/lib.rs:115-143"
      - "crates/buzz-relay/src/router.rs:62-90"
    confidence: 0.85
  - statement: "`crates/buzz-test-client/tests/conformance_multitenant.rs`'s doc-comment for `token_minted_in_a_does_not_authorize_in_b` states that API tokens ARE consumed (not minted) 'by the Blossom upload path at `crates/buzz-relay/src/api/media.rs:638`, which extracts the `X-Auth-Token: buzz_*` header' and looks up the token by hash."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "crates/buzz-test-client/tests/conformance_multitenant.rs, doc-comment on token_minted_in_a_does_not_authorize_in_b (unattributed prior author)"
  - statement: "That specific claim does not match this revision's code: `crates/buzz-relay/src/api/media.rs` contains no `X-Auth-Token` handling and no call to `get_api_token_by_hash*` at all (grepped directly, zero matches), and a repository-wide grep for the literal string `X-Auth-Token` across `crates/` matches only the conformance test's own comment. The comment's separate claim — that no HTTP route exists for minting a token — is independently confirmed accurate by `router.rs`'s route list, so only the media-consumption half of the comment is stale, not the whole paragraph."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/router.rs:62-90"
    confidence: 0.8
  - statement: "`Scope::all_non_admin()` returns all 14 non-admin scope variants (excluding `AdminChannels` and `AdminUsers`) and its doc-comment says it is 'used in dev mode ... where `X-Pubkey` header auth grants access without a real token,' but a repo-wide grep for `all_non_admin` finds it called only from its own definition site's tests in `scope.rs` — no production call site exists in this build, so the dev-mode path its comment describes is not (yet) wired to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs:89-111"
  - statement: "`AuthError::InsufficientScope { required: String, have: Vec<String> }` is the typed failure `require_scope` returns when a scope check fails; its `Display` renders `\"insufficient scope: required {required}, have {have:?}\"`."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs:44-49"
  - statement: "Issue #1040 (parent PRD #607) is the task that requested this node; at this revision, sibling task #1035 (`layers/authorization/event-authorization.md`) targets the same directory but has not merged to `origin/launchpad` — `launchpad/docs/corpus/layers/authorization/` does not exist on that branch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1040, launchpad-26/buzz#1035 (issue bodies, read directly while authoring this node)"
---

# Authorization scopes

An **authorization scope** is a named permission — such as `messages:write`
or `admin:channels` — that a connection or API token must hold before the
relay will let it perform a given operation; Buzz represents each one as a
variant of the `Scope` enum (`crates/buzz-auth/src/scope.rs`), and every
authenticated request carries a list of the scopes it was granted.

## Definition

`Scope` is a closed, code-defined enum of 16 named permissions, plus one
escape hatch. Each known variant pairs a resource with an action —
`messages:read`/`messages:write`, `channels:read`/`channels:write`,
`users:read`/`users:write`, `jobs:read`/`jobs:write`,
`subscriptions:read`/`subscriptions:write`, `files:read`/`files:write`,
`repos:read`/`repos:write` — plus two administrative variants,
`admin:channels` and `admin:users`, that are deliberately excluded from the
"non-admin" convenience set. The escape hatch, `Scope::Unknown(String)`,
preserves any scope string a future relay build might introduce so an older
build does not choke on it — forward-compatibility without a schema
migration for the enum itself.

A connection's granted scopes live on its `AuthContext` (`scopes:
Vec<Scope>`), and `AuthContext::has_scope()` is the containment check every
enforcement point ultimately calls, whether directly or through the
`require_scope`/`check_read_access`/`check_write_access` helpers in
`buzz-auth::access`.

**A documentation/implementation mismatch worth knowing up front:**
`scope.rs`'s own comments describe scopes as "stored as `TEXT[]` in the
database," but the `api_tokens` table's `scopes` column is declared
`JSONB NOT NULL`, and `buzz-db::api_token::create_api_token` serializes its
scope list with `serde_json::to_value` before binding it there. The JSONB
migration and the serializing insert code are what actually runs; the
`TEXT[]` comment describes a shape this build does not use.

## How scopes are granted today

Both live authentication paths in this build grant the **full** scope set
unconditionally, not a caller-specific subset:

- **NIP-42** (WebSocket challenge/response): `AuthService::verify_auth_event`
  returns an `AuthContext` with `scopes: Scope::all_known()` for every
  successfully verified signature.
- **NIP-98** (the `POST /events` HTTP bridge path): `submit_event` builds its
  `IngestAuth::Http` with `scopes: buzz_auth::Scope::all_known()` too, with
  the same "pure Nostr: full scopes, channel access via membership" reasoning
  in the code comment.

In both cases, the code frames this as deliberate: in "pure Nostr mode,"
*which* channels a connection may read or write is enforced separately by
NIP-29 channel membership (see `check_read_access`/`check_write_access`,
which require a scope **and** call the membership checker), not by handing
out a narrower scope list per caller.

The `api_tokens` table and its full CRUD surface
(`create_api_token`/`get_api_token_by_hash*`/`revoke_token`/etc.) exist in
`buzz-db` — this is the layer that *could* grant a caller fewer than all 16
scopes — but at this revision nothing in `buzz-relay` calls any of those
functions, and `router.rs` has no `/tokens` route to mint one over HTTP.
Scope narrowing via API tokens is therefore a built but currently
disconnected mechanism, not a live path a caller can reach. (A test-client
conformance comment claims tokens are consumed by a Blossom media route with
an `X-Auth-Token` header; that specific claim does not match this revision's
`media.rs`, which contains no such header handling — see the evidence
ledger.)

## How scopes are enforced

Two independent mechanisms check scopes against a connection's `AuthContext`,
and a request must pass whichever one applies to it:

1. **Per-kind mapping.** `required_scope_for_kind()` in
   `buzz-relay::handlers::ingest` maps every event kind the relay accepts to
   the one `Scope` required to submit it (for example, `KIND_TEXT_NOTE`
   requires `MessagesWrite`; the NIP-29 "edit group metadata" kind requires
   `AdminChannels` or `ChannelsWrite` depending on whether the event carries
   an `archived` tag; relay-membership admin commands require `AdminUsers`).
   An unrecognised kind is rejected outright, not defaulted to any scope.
2. **Direct checks outside the per-kind map.** `handlers::event` separately
   requires `MessagesWrite` for ephemeral event kinds and for
   `KIND_AGENT_OBSERVER_FRAME`, before those events reach kind-specific
   handling at all.

Both mechanisms fail the same way: `require_scope` returns
`AuthError::InsufficientScope { required, have }` when the connection's
scope list does not contain what is needed, and callers surface that as a
rejection (e.g. `"restricted: insufficient scope for ..."` over the
WebSocket).

## Boundary — what this is not

**Not channel access control.** Holding `Scope::MessagesRead` proves a
connection is *allowed to attempt reads at all*; it says nothing about
*which* channels. `check_read_access`/`check_write_access` require the scope
**and** a passing NIP-29 membership check — two separate gates that must
both hold. The membership mechanism itself is a different corpus subject,
not this node's.

**Not a per-event-kind reference table.** `required_scope_for_kind`'s full
kind-to-scope mapping lives in, and is owned by,
`crates/buzz-relay/src/handlers/ingest.rs`. This node names the mechanism
and a few illustrative mappings; it does not restate the whole `match`.

**Not OAuth**, despite the crate-level doc-comment describing the module as
"OAuth scope parsing and enforcement." There is no OAuth authorization
server, token endpoint, or grant-type negotiation anywhere in this build —
`Scope` borrows OAuth's `resource:action` naming convention for its wire
strings and nothing else. Treat the resemblance as a naming choice, not a
protocol claim.

## Worked example

A WebSocket client completes NIP-42 auth and receives an `AuthContext` with
`scopes: Scope::all_known()` (16 entries). It sends a `kind:9002` (NIP-29
edit-group-metadata) event with no `archived` tag. `required_scope_for_kind`
maps that to `Scope::ChannelsWrite`; the client's scope list contains it, so
the scope gate passes, and the request proceeds to the separate NIP-29
membership check. If the same client instead sent the same kind *with* an
`archived` tag, the required scope becomes `Scope::AdminChannels` — still
present in `all_known()`, so it would also pass today, precisely because
every live auth path currently grants the full set. A future caller
authenticated through a scope-narrowed API token (once that path exists)
could hold `ChannelsWrite` without `AdminChannels` and would be rejected with
`AuthError::InsufficientScope` on the archived-tag variant specifically.

## Scope and omissions

**This document covers** the `Scope` enum's shape and wire format, how a
connection's scope list is granted under both live authentication paths, the
two mechanisms that enforce scopes, the storage-comment/schema mismatch, and
the current gap between the API-token scope-narrowing mechanism's storage
layer and its (absent) live entry point.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-29 channel membership mechanics (the second, separate gate `check_read_access`/`check_write_access` also enforce) | Not yet a corpus node at this revision |
| `required_scope_for_kind`'s complete kind-to-scope mapping | `crates/buzz-relay/src/handlers/ingest.rs` directly |
| NIP-42 and NIP-98 authentication mechanics themselves (signature verification, challenge issuance, replay protection) | `crates/buzz-auth/src/nip42.rs`, `nip98.rs`, `nip98_replay.rs` |
| Whether/when a `/tokens` HTTP route or CLI subcommand will connect `buzz-db`'s API-token CRUD to a live grant path | Not yet filed as its own issue at this revision |

**Expected but not verified when this node was written:**

- Whether the pre-rewrite `sprout-relay` self-service token-minting endpoint
  (`crates/sprout-relay/src/api/tokens.rs`, cited by the conformance test's
  doc-comment as deliberately not ported) still exists anywhere in this
  checkout, or in what form a future port might take, was not investigated —
  out of scope for documenting the current `Scope` mechanism.
- Whether any desktop, mobile, or CLI surface exposes a UI for a user to
  mint or view their own API tokens was not checked; this node covers the
  relay-side mechanism only.

**No `relationships` in this node's own front matter.** Checked before
deciding that: at this revision, `origin/launchpad`'s
`launchpad/docs/corpus/layers/authorization/` directory does not exist yet —
sibling authorization tasks (#1035–#1039) have not merged — so there is no
on-disk corpus node to target with a typed edge. The likeliest future edges
are `references` to a channel-membership/NIP-29 concept node and to whichever
node ends up documenting `required_scope_for_kind`'s full mapping, once
either exists on disk.
