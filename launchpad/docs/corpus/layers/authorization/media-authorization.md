---
id: layers-authorization-media-authorization
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
  - statement: "PR #1444 ('fix(relay): remove media bearer-token auth', merged 2026-07-01 as commit 0701f47f4a31a904ebcd9f360cbd6aadaff9d784, present in this repository) states in its own body that it removed the media upload `X-Auth-Token`/`api_tokens` authorization path and replaced it with Blossom kind:24242 (BUD-11) hash/server validation plus the existing NIP-43 relay membership check, giving the rationale 'Buzz media auth should be Nostr-native, not bearer tokens' and noting that relay endpoints parse NIP-98 `Authorization: Nostr`, never `Authorization: Bearer`."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1444 pull request body"
  - statement: "At the recorded revision, no `X-Auth-Token` or bearer-token check exists anywhere in `crates/buzz-relay/src/api/media.rs` or `crates/buzz-media/src/auth.rs`; the only authorization inputs the upload and read paths read are the `Authorization: Nostr <event>` header (a Blossom kind:24242 event) and, for relay-membership admission, an optional `X-Auth-Tag` header carrying a NIP-OA delegation tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-media/src/auth.rs"
  - statement: "`verify_blossom_auth_event_for_verb` in `buzz-media::auth` is the shared Blossom (BUD-11) auth-event verifier for both verbs: it checks the event's Schnorr signature, requires `kind == 24242` with non-empty `content`, requires a `t` tag equal to the caller-supplied verb (`upload` or `get`), requires an `expiration` tag whose value is still in the future, requires `created_at` to be no more than 5 seconds in the future and no older than a caller-supplied `max_age_secs` window, and — only if the event carries one or more `server` tags — requires at least one to match the request's bound tenant host under `buzz_core::tenant::normalize_host`, failing closed (`ServerMismatch`) if the bound host is unknown rather than skipping the check."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "`verify_blossom_upload_auth` additionally requires at least one `x` tag on the event to equal the uploaded content's SHA-256 hex digest (BUD-11 §6); `verify_blossom_get_auth` additionally requires either a matching `x` tag or a `server` tag matching the bound host, rejecting an event with neither as `InsufficientScope` — BUD-01's permitted 'blob-scoped or server-scoped' authorization split."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "A `verify_blossom_get_auth` pass on server-scoped authorization (a matching `server` tag with no matching `x` tag) grants read access to every blob on the host until the event's expiration, not just the specific blob requested — the function's own doc comment states callers 'must still apply relay membership after this verifier returns', naming relay membership as a necessary second gate rather than a redundant one for the get path."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "For uploads, the `AuthenticatedUpload` Axum extractor (`FromRequestParts` impl in `crates/buzz-relay/src/api/media.rs`) runs, in order: Host-header tenant binding (fail-closed 404 on an unmapped host); `verify_blossom_auth_event` against the bound host; a required, well-formed `X-SHA-256` request header that must match an `x` tag already verified on the auth event; then `crate::api::relay_members::enforce_relay_membership` for the auth event's pubkey against the bound community; then per-(community, pubkey) rate-limit and concurrency-permit checks — the extractor returns before any request body is read if any step rejects."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "For reads, `authenticate_media_read` in the same file runs: `bind_media_read_tenant` (Host-header tenant binding, fail-closed 404), `extract_blossom_auth` plus `verify_blossom_get_auth` against the bound host, then `enforce_relay_membership` for the auth event's pubkey against the bound community — identical relay-membership gate to the upload path, called with the same function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "`extract_blossom_auth` reads the `Authorization` header, requires a `Nostr ` scheme prefix, base64-decodes the remainder (URL-safe-no-pad first, then standard as a fallback), and parses the result as a signed Nostr event — failing with distinct `MediaError` variants (`MissingAuth`, `InvalidAuthScheme`, `InvalidBase64`, `InvalidAuthEvent`) at each step, all of which are folded into the same generic 401 response by `MediaError::into_response`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "`buzz-relay::api::mod::relay_members::check_relay_membership` is the single relay-membership decision function shared by media, `bridge.rs`, `git/transport.rs`, and `audio/handler.rs` (per its own module doc comment: 'Relay membership enforcement — single gate for all authenticated entry points'). It returns `OpenRelay` immediately (no check performed) when `state.config.require_relay_membership` is `false`; otherwise it looks up the pubkey in `relay_members` for the bound community, returns `Member` on a direct hit, and — only when `state.config.allow_nip_oa_auth` is `true` and an `X-Auth-Tag` header is present — falls back to verifying a NIP-OA delegation tag and checking whether the *owner* pubkey it names is a relay member, returning `ViaOwner(owner_pubkey)` on success or `Denied` otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "`enforce_relay_membership` wraps `check_relay_membership` and converts `Denied` into an HTTP 403 body `{\"error\": \"relay_membership_required\", \"message\": \"You must be a relay member to access this relay\"}`; `OpenRelay` and `Member` both map to `Ok(None)` (admitted, no delegation), and `ViaOwner` maps to `Ok(Some(owner_pubkey))` (admitted via NIP-OA delegation)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "`require_relay_membership` defaults to `false` (an explicit unit test, `config.rs`'s own test module, asserts this default) and is documented as: when `false`, the membership check is a no-op and every authenticated caller is admitted 'regardless of auth method (API token, NIP-42)'. `allow_nip_oa_auth` also defaults to `false` and, per its own doc comment, only controls whether NIP-OA delegation can grant membership *on a closed relay* — on an open relay, owner extraction for agent-to-owner backfill happens unconditionally because the NIP-OA signature is self-proving."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`require_auth_token` ('Whether REST API requests must present a valid token') is a config field documented as independent of the media authorization path: its own doc comment scopes it to the generic REST API, and the `AuthenticatedUpload` extractor's inline comment states relay membership is 'the only upload authority: independent of bearer-token / api_tokens storage and of `require_auth_token` (which governs the REST API, not media)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "`MediaError::into_response` groups every authentication-shaped failure (missing/malformed/invalid auth header or event, bad signature, wrong kind/verb, expired or out-of-window timestamp, hash mismatch, server-tag mismatch, missing tag, revoked/mismatched token) into one generic 401 response with the fixed body `authentication failed`, by explicit in-source design ('to prevent oracle enumeration'); `InsufficientScope` (BUD-01 get-scope failure) and `RelayMembershipRequired` are both mapped separately to 403, on the stated reasoning that they are authorization failures reachable only after a valid signed identity is already established, so distinguishing them does not create an authentication oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/error.rs"
  - statement: "`buzz-media::auth`'s own unit test suite exercises this contract directly: a valid upload/get event passes; a `server`-tag mismatch is rejected with `ServerMismatch`, including when the bound host is `None` (fail-closed); an `x`-tag/claimed-hash mismatch is rejected with `HashMismatch`; a wrong `kind` is rejected with `InvalidAuthKind`; a `get`-scoped request with neither a matching `x` tag nor a matching `server` tag is rejected with `InsufficientScope`; and a `server` tag is matched against the bound tenant host after normalization (default port, trailing dot, case, full URL) so a non-primary tenant's correctly server-tagged client is not incorrectly rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "`crates/buzz-test-client/tests/e2e_media.rs` exercises the composed authorization path end to end at the HTTP layer: `test_unauthenticated_reads_are_rejected` and the upload-side 401 assertions (`test_upload_hash_mismatch_returns_400`, which despite its name asserts HTTP status 401, matching the `error.rs` grouping) confirm a request with no `Authorization` header, or with a hash-mismatched auth event, is rejected before any blob is served or stored; `test_get_nonexistent_returns_404` confirms an authenticated, authorized request against a hash that was never uploaded still returns 404, proving the relay-membership and Blossom-auth checks run and pass before storage existence is even consulted."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs"
  - statement: "This node's boundary against `layers-authorization-authorization` (issue #1031) is an inference rather than a confirmed fact: that overview node's own deferred-layers table (community membership/role, channel membership, channel role, action-specific/event authorization) does not list a media layer, and it is unmerged (open PR #1796) at this node's authoring time, so whether the batch intends media authorization to be treated as a fifth sibling layer of that overview, or as a structurally separate authorization mechanism outside its scope (because it gates a Blossom HTTP door rather than a NIP-29 channel/event operation), was not settled by either document and is left to the batch owner's review."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/pull/1796"
    confidence: 0.6
  - statement: "Issue #1036 requires this node to represent one independently maintainable knowledge node distinct from the architecture flow documents, to link rather than duplicate related implementation/verification/corpus nodes, and to check the draft against the repository revision recorded in provenance and against relevant Git history (PR #1444) and issues (#1027) where they explain current behavior or rationale."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1036 definition of done, and its dispatching task brief citing #1027"
  - statement: "At the checked revision, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists `architecture/flows/media-upload.md` (id `architecture-flows-media-upload`) and `architecture/flows/media-download.md` (id `architecture-flows-media-download`) as merged, and lists no file under `launchpad/docs/corpus/layers/` at all — so `layers-authorization-authorization` (issue #1031, open PR #1796) does not resolve to a loaded node and is not a valid `relationships` target, while the two flow-node ids are."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> architecture/flows/media-upload.md, architecture/flows/media-download.md present; no layers/ directory; run at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-flows-media-upload
  - type: references
    target: architecture-flows-media-download
---

# Media authorization

## Definition

**Media authorization** is the pair of checks Buzz's relay applies to every Blossom
media request — `PUT /upload` (and its legacy `/media/upload` alias), and
`GET`/`HEAD /media/{sha256_ext}` — before it will store or serve a blob: a
Blossom (BUD-11) kind:`24242` signed authorization event proving *who* is asking and
*what they are authorized to do*, followed by a **NIP-43 relay-membership check**
deciding *whether that identity may use this community's media store at all*. Both
checks are Nostr-native; there is no bearer-token, API-key, or session-cookie path
into media upload or download at the checked revision.

This node is the category-level description of that composed mechanism — the two
layers, their order, what each one actually establishes, and how a failure of each
is reported. It is not a walkthrough of the surrounding HTTP flow (buffering,
streaming, storage pipelines, range requests, content-type resolution); that belongs
to the two flow nodes this node references and does not duplicate.

## Not to be confused with

**The `require_auth_token` REST-API gate.** `buzz-relay`'s `require_auth_token` config
field governs whether the *generic* REST API requires a token. It is documented, and
the upload extractor's own source comment states explicitly, as **independent** of
media authorization — relay-membership enforcement is "the only upload authority,"
regardless of `require_auth_token`'s value.

**The removed bearer-token path.** Before PR #1444 (merged 2026-07-01), media upload
also accepted an `X-Auth-Token` header checked against an `api_tokens` table. That path
was removed in favor of the Blossom-plus-NIP-43 composition this node describes,
because — per the PR's own rationale — relay endpoints parse `Authorization: Nostr`,
never `Authorization: Bearer`, so a bearer-token branch was dead code for this path in
practice. No `X-Auth-Token` or `api_tokens` check exists anywhere in the current media
code.

**Authentication versus authorization, within this same mechanism.** The Blossom
kind:24242 event's *signature* is the authentication proof (the request really comes
from the pubkey it claims). Everything else the event's tags encode — verb, hash
scope, server scope, expiration — is itself already an *authorization* claim ("this
signer authorizes exactly this action"), and it is still not sufficient on its own:
relay membership is a second, independent authorization decision layered on top of a
validly signed and correctly scoped event, not a formality.

**The generic NIP-29 channel/community authorization layers.** A separate, broader
overview node — expected id `layers-authorization-authorization` (issue #1031, open
PR #1796 at the time this node was written, not yet merged) — describes the layered
shape of authorization for ordinary channel/event operations: scope, community
membership/role, channel membership/role, and action-specific (moderation) checks.
That node's own deferred-layers table does not list a media layer, and whether media
authorization is meant to sit alongside those four as a fifth layer of the same
overview, or is a structurally separate mechanism (it gates an HTTP Blossom door, not
a NIP-29 channel/event operation, and shares only relay membership — not scope,
channel membership, or channel role — with that layered shape) is not settled by
either document; see the front-matter `INFERENCE` entry above. No `relationships`
edge is declared toward it because it is unmerged.

## The two-layer composed shape

Both the upload path (`AuthenticatedUpload`, an Axum extractor) and the read path
(`authenticate_media_read`) run the same two authorization layers, in the same order,
after first binding the request to a community from its `Host` header (fail-closed
404 on an unmapped host — a separate, prior concern this node does not restate; see
`architecture-principles-community-is-security-boundary`).

1. **Blossom (BUD-11) authorization-event verification — `buzz-media::auth`.**
   `verify_blossom_auth_event_for_verb` checks, for both verbs:
   - A valid Schnorr signature over a `kind:24242` event with non-empty `content`.
   - A `t` tag matching the verb being performed (`upload` or `get`) — an event
     minted for one verb cannot authorize the other.
   - An `expiration` tag still in the future, and a `created_at` no more than 5
     seconds ahead of the relay's clock and no older than a per-call `max_age_secs`
     window (600s for buffered uploads, up to the caller's window for video, 3600s
     for reads) — bounding how long a signed event stays replayable.
   - If the event carries any `server` tag, at least one must match the request's
     *bound tenant host* (not a single process-global domain) under the shared
     `normalize_host` rule — and this **fails closed** if the bound host is somehow
     unknown, rather than skipping the check.

   On top of that shared check, each verb adds its own scope requirement:
   - **Upload** (`verify_blossom_upload_auth`): at least one `x` tag must equal the
     uploaded content's SHA-256 — the signer is authorizing *this exact byte
     content*, not uploads in general. The HTTP extractor separately requires a
     matching `X-SHA-256` header before the body is even read.
   - **Get** (`verify_blossom_get_auth`): either a matching `x` tag (this specific
     blob) **or** a matching `server` tag (every blob on this host, until
     expiration) satisfies BUD-01's scope requirement; an event with neither is
     rejected as `InsufficientScope`. Server-scoped read authorization is
     deliberately broad — the function's own doc comment states callers "must
     still apply relay membership after this verifier returns," which is exactly
     layer 2 below.

2. **Relay-membership check (NIP-43) — `buzz-relay::api::mod::relay_members`.**
   `check_relay_membership`/`enforce_relay_membership` is described in its own
   module doc comment as "the single gate for all authenticated entry points" and is
   shared, unmodified, by media, the Nostr HTTP bridge, git smart-HTTP, and huddle
   audio — media authorization does not reimplement or fork this check.
   - When `require_relay_membership` is `false` (the default), the check is a no-op:
     every signer who passed layer 1 is admitted, regardless of community
     membership. This is Buzz's "open relay" mode.
   - When `true`, the signer's pubkey must be a row in `relay_members` for the
     *bound* community (never cross-community), **or** — only if `allow_nip_oa_auth`
     is also `true` and the request carries an `X-Auth-Tag` header — the pubkey must
     be a registered NIP-OA agent whose named owner *is* a relay member. A
     signer that is neither is rejected with a 403 `relay_membership_required`
     error, before any blob I/O occurs.

Both layers must pass for either upload or read to proceed; there is no code path
that skips layer 1 for either verb, and no code path that skips layer 2 when it is
configured on.

## Failure reporting

`MediaError::into_response` deliberately collapses every layer-1 (Blossom
authentication/authorization-event) failure — missing or malformed header, bad
signature, wrong kind or verb, expired or out-of-window timestamp, hash mismatch,
server-tag mismatch, missing required tag — into one generic HTTP 401 with a fixed
body, explicitly to avoid giving a caller an oracle that would let it learn *which*
check failed. `InsufficientScope` (the get-verb BUD-01 scope failure) and
`RelayMembershipRequired` (layer 2's denial) are each mapped separately to 403, on
the stated reasoning that both are reachable only once a validly signed identity is
already established, so distinguishing them from each other — and from the 401
group — does not itself leak identity information to an unauthenticated caller.

## Scope and omissions

**This node covers** the two-layer media-authorization mechanism itself: what the
Blossom kind:24242 event must contain and how it is verified per verb, what NIP-43
relay membership (with NIP-OA owner delegation) adds on top of it, the configuration
that turns each layer's strictness on or off, and how each layer's failure is
reported over HTTP.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full upload HTTP flow — body sniffing, buffered vs. streaming pipelines, idempotency, rate/concurrency limits, the deletion-fence lease, storage/sidecar writes | `architecture-flows-media-upload` (referenced, not restated) |
| The full download HTTP flow — path validation, sidecar content-type resolution, range requests, security response headers | `architecture-flows-media-download` (referenced, not restated) |
| The generic NIP-29 channel/community authorization layers (scope, community membership/role, channel membership/role, action-specific/moderation checks) | expected id `layers-authorization-authorization`, issue #1031 (unmerged; see *Not to be confused with*) |
| How a client (desktop, mobile, CLI, or the stock `buzz` CLI) actually constructs and signs a Blossom kind:24242 event | Not inspected for this node; only the relay-side verification contract is in scope, matching both referenced flow nodes' own stated scope |
| The removed `api_tokens` table's schema and any remaining non-media callers of it | Named as a deliberate follow-up in PR #1444's own description ("remove/deprecate `api_tokens` DB/schema/helpers/docs after migration/backcompat review"); not inspected here |
| The exact BUD-01/BUD-11 Blossom specification text | This node states what Buzz's code enforces and cites the code, not the external spec text, which was not opened for this node |

**Expected but not verified when this node was written:**

- **Whether any other HTTP door in this repository still accepts a bearer/API token
  for anything media-adjacent** beyond the two files inspected
  (`crates/buzz-relay/src/api/media.rs`, `crates/buzz-media/src/auth.rs`) was not
  swept repo-wide; PR #1444's own description states a `rg` sweep of
  `crates/buzz-relay mobile/lib mobile/test` for `X-Auth-Token|apiToken` found no
  matches at merge time, but that sweep was not re-run for this node.
- **Live execution of the flow** (a running relay against a real Blossom client) was
  not performed for this node; the claims above rest on reading source and the
  existing unit/integration test assertions, matching the same caveat both
  referenced flow nodes already state about themselves. The three
  `crates/buzz-test-client/tests/e2e_media.rs` functions cited above are each marked
  `#[ignore]` and call a live `relay_http_url()`, meaning they require a running
  relay and do not execute under a plain `cargo test` — their assertions were read
  directly from source, not observed passing in a run performed for this node.
- **Whether `layers-authorization-authorization` (#1031/PR #1796) will, once merged,
  add media as a fifth layer or leave it structurally separate** is explicitly
  unresolved — see the front-matter `INFERENCE` entry and *Not to be confused with*
  above.
