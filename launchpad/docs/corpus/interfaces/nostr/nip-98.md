---
id: interfaces-nostr-nip-98
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f."
    entry_class: FACT
    evidence:
      - "commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "`crates/buzz-auth/src/nip98.rs`'s module doc comment states NIP-98 is 'the standard Nostr HTTP Auth pattern used by Nostr.build, Blossom, and other Nostr HTTP services', is 'stateless -- no WebSocket session required', and lists eight verification steps: parse JSON, verify kind==27235, verify Schnorr signature, verify created_at within +-60s, verify the `u` tag matches the expected URL (normalised), verify the `method` tag matches (case-insensitive), and -- if a `payload` tag is present and a body was supplied -- verify SHA-256(body) equals the tag's hex value, then return the event's pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:1-24"
  - statement: "`verify_nip98_event(event_json, expected_url, expected_method, body) -> Result<nostr::PublicKey, AuthError>` is the shared verifier every call site in this repository uses; it rejects a `u` or `method` tag count other than exactly one, and rejects more than one `payload` tag (closing a find()-accepts-first-and-ignores-second bypass its own comment names), while payload-tag *presence* is not required by the shared function itself -- callers that need body-integrity binding enforce that per-consumer before calling in."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:55-178"
  - statement: "`normalize_url` lowercases scheme/host and strips a trailing slash from the path, but deliberately does NOT alias loopback hosts: `localhost`, `127.0.0.1`, and `::1` are treated as three distinct hosts, because the `u`-tag host is the row-zero community binding under multi-tenant and collapsing them would be a host-binding side door."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:180-200"
      - "crates/buzz-auth/src/nip98.rs:461-488"
  - statement: "`AuthError::Nip98Invalid(String)` covers any NIP-98 verification failure (signature, timestamp, URL, method, tag-count, payload-hash) with a message documented as safe for server logs but not for forwarding verbatim to clients; `AuthError::Nip98Replay` is a distinct variant for a structurally valid event whose id has already been seen within the replay window."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs:26-37"
  - statement: "`buzz-core/src/kind.rs` defines `KIND_HTTP_AUTH: u32 = 27235` with the comment 'NIP-98: HTTP auth event (used in nip98.rs, not stored)', and separately defines `KIND_BLOSSOM_AUTH: u32 = 24242` with the comment 'BUD-01: Blossom upload auth (used in upload.rs, not stored)' -- two distinct kind constants for two distinct authentication schemes."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:79"
      - "crates/buzz-core/src/kind.rs:83"
  - statement: "`buzz-auth/src/lib.rs`'s own module doc table lists exactly two auth paths -- NIP-42 over WebSocket (challenge/response, kind:22242) and NIP-98 over HTTP (signed kind:27235 event in an `Authorization: Nostr` header) -- confirming NIP-98 is this crate's dedicated HTTP auth mechanism, sibling to but distinct from the WebSocket path."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:1-16"
  - statement: "`nip98_replay.rs`'s module doc states NIP-98 verification is 'structurally complete' but does not by itself check whether an event id has already been used, and that this requires shared state because, per the rewrite architecture's 'any pod, any connection' model, an in-process cache does not carry a freshness proof across relay pods."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:1-31"
  - statement: "The `Nip98ReplayGuard` trait's `try_mark`/`try_mark_in_scope` contract requires an atomic set-if-absent claim (never read-then-write), requires callers to fail closed on an `Err` (Redis unreachable, etc.) rather than admit the request, and states the production implementation lives in `buzz-pubsub` as a Redis `SET NX EX`."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:63-104"
  - statement: "`DEFAULT_REPLAY_TTL_SECS = 120` is documented as the floor, matching the doubled +-60s timestamp-tolerance window; `MAX_REPLAY_TTL_SECS = 3600` is documented as the ceiling, both to stay well inside Redis `EX`'s signed 64-bit argument and because any TTL past an hour is implausible given the verifier's own timestamp window; implementations must clamp up to the floor and down to the ceiling rather than honor an out-of-range value as-given."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:40-57"
  - statement: "The replay seen-set key format is `buzz:{community}:nip98:{event_id_hex}` -- community-prefixed so a same-id replay across two communities consults two distinct Redis rows even though content-addressed event ids make natural cross-community collision implausible."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:106-121"
  - statement: "`buzz-relay/src/api/bridge.rs`'s `verify_bridge_auth_with_options` is the shared HTTP-bridge entry point: it tries `Authorization: Nostr <base64(event)>` first, decodes it, and calls `buzz_auth::verify_nip98_event(&event_json, url, method, body)`; only when no such header is present, and only when `require_auth_token` is false, does it fall back to a dev-mode `X-Pubkey` header with a zero event id (no replay concern)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:62-128"
  - statement: "`check_nip98_replay`/`check_nip98_replay_with_guard` skip replay checking entirely for the dev-mode zero event id, otherwise call `Nip98ReplayGuard::try_mark` and return 401 both on an explicit `Ok(false)` (replay detected) and on any guard `Err` (logged as a warning and rejected fail-closed, 'without the shared SET NX EX proof, a stateless worker cannot admit the NIP-98 request safely')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:130-176"
  - statement: "`nip98_expected_url(config_relay_url, tenant, path)` builds the `u`-tag comparison URL from the per-request resolved `TenantContext`'s host, not from the deployment's static `config.relay_url`, specifically to close a cross-community host-binding hole documented in the function's own comment: using the static config host would let an event signed for community A's host pass verification against community B, or reject every legitimate request on a multi-tenant deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:178-206"
  - statement: "The bridge's NIP-98 path authenticates `POST /events`, `POST /query`, and `POST /count`: each handler builds its expected URL via `nip98_expected_url` and calls `check_nip98_replay` before proceeding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:725"
      - "crates/buzz-relay/src/api/bridge.rs:858"
      - "crates/buzz-relay/src/api/bridge.rs:996"
      - "crates/buzz-relay/src/api/bridge.rs:1049"
      - "crates/buzz-relay/src/api/bridge.rs:1525"
      - "crates/buzz-relay/src/api/bridge.rs:1576"
  - statement: "The invites, gifs, and workflows HTTP APIs reuse the same `bridge::nip98_expected_url` and `bridge::check_nip98_replay` helpers rather than re-implementing NIP-98 verification or replay handling, so all bridge-style HTTP endpoints share one auth and one replay-prevention implementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:249"
      - "crates/buzz-relay/src/api/invites.rs:258"
      - "crates/buzz-relay/src/api/gifs.rs:140"
      - "crates/buzz-relay/src/api/gifs.rs:150"
      - "crates/buzz-relay/src/api/workflows.rs:64"
      - "crates/buzz-relay/src/api/workflows.rs:68"
  - statement: "The deployment-admin API (`crates/buzz-relay/src/api/admin/auth.rs`) authenticates every mutating and read request the same way: `Authorization: Nostr <base64 event>`, verified for signature/timestamp/`u`-tag/`method`-tag/payload-hash, with the authenticated pubkey then resolved to an `AdminPrincipal` (Operator via config or DB row, Moderator via DB row, or none -> 403, never a fall-through role); `ADMIN_API_PREFIX = \"/api/admin/v1\"` is re-added when constructing the canonical URL because axum strips it before the handler runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:1-45"
  - statement: "Git smart-HTTP auth (`GitAuth` in `crates/buzz-relay/src/api/git/transport.rs`) also decodes an `Authorization: Nostr <base64>` header and calls `buzz_auth::nip98::verify_nip98_event`, but deliberately differs from the bridge path in two ways documented in its own inline comments: (1) it does not enforce the `method` tag against the actual HTTP method -- it passes the event's own signed method back into the verifier so the check is tautological, because git's credential helper signs once with GET (`info/refs`) and reuses the token for a later POST (pack data); and (2) it does NOT run NIP-98 replay/event-id dedup at all, because the same signed token is legitimately reused across multiple requests in one clone/push session. Both gaps are stated as accepted for v1, with the repo-scoped `u` tag, the +-60s timestamp window, and HTTPS transport named as the compensating controls; body-payload hashing is also skipped here because streaming pack data cannot be buffered to compute a hash."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:62-77"
      - "crates/buzz-relay/src/api/git/transport.rs:144-199"
  - statement: "`crates/buzz-relay/src/api/media.rs`'s Blossom upload/download auth (`extract_blossom_auth`, `buzz_media::auth::verify_blossom_auth_event`) is a structurally separate scheme: it decodes an `Authorization: Nostr <base64(kind:24242 event)>` header (BUD-01/BUD-11), not a kind:27235 NIP-98 event, and calls `buzz_media::auth::verify_blossom_auth_event` rather than `buzz_auth::verify_nip98_event` -- Blossom media authorization is not part of this NIP-98 interface."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:172-178"
      - "crates/buzz-relay/src/api/media.rs:309-311"
      - "crates/buzz-relay/src/api/media.rs:983-996"
  - statement: "Root `SECURITY.md` states in prose: 'REST endpoints authenticate via NIP-98 HTTP Auth -- the client signs a kind:27235 event containing the request URL and method. The relay verifies the Schnorr signature and extracts the pubkey', linking to the upstream spec at `https://github.com/nostr-protocol/nips/blob/master/98.md` (an unpinned, non-FACT-grade reference here since it targets a mutable ref)."
    entry_class: FACT
    evidence:
      - "SECURITY.md:60-63"
  - statement: "This corpus already cites the upstream `nostr-protocol/nips` repository pinned to commit `dabfcb2aaecf4fa374eda8b1232ab303a03f60ba` for NIP-01 and NIP-29 (in `templates/data-entity.md` and `templates/event-kind.md`), establishing the pin this node reuses for the NIP-98 spec file rather than introducing a second, differently-pinned reference to the same upstream repository."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md:44"
      - "launchpad/docs/corpus/templates/data-entity.md:62"
  - statement: "No corpus node under `launchpad/docs/corpus/interfaces/` exists on `origin/launchpad` at the recorded revision -- the `interfaces/` directory itself does not exist yet -- so no `interfaces-http-media` node (tracked separately as issue #984) or any other interface-shaped node is a valid `relationships` target for this node today."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no interfaces/ entry, checked at commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "`templates/interface.md` (the governing template for this node's shape) requires a node built from it to carry `type: interfaces-events` -- the schema's single combined value for the corpus's interface-and-event-kind surface -- and to include an Interface description, an Operations table, a Contract-and-stability section, a Boundary statement, Relationships, and Scope and omissions."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md:216-334"
  - statement: "Issue #1017's Definition of Done requires the drafted node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative upstream spec, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1017 definition of done"
  - statement: "NIP-98 itself defines no version negotiation or protocol-evolution mechanism (no version tag, no capability negotiation) beyond the single kind:27235 event shape; this repository's own extensions to it -- the shared replay-prevention floor/ceiling, and the per-consumer choice of whether to require a `payload` tag -- are Buzz-side additions layered on top of, not amendments to, the upstream NIP."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip98.rs:1-24"
      - "crates/buzz-auth/src/nip98_replay.rs:1-57"
    confidence: 0.75
---

# NIP-98 HTTP Auth: interface

This node documents Buzz's implementation of the upstream Nostr **NIP-98 HTTP Auth**
protocol -- a stateless authentication scheme in which an HTTP client proves
control of a Nostr keypair by signing a short-lived `kind:27235` event describing
the exact request (URL, method, optional body hash) and sending it as an
`Authorization: Nostr <base64(event)>` header. The two sides of the boundary are
an HTTP client (a human's browser/CLI, `buzz-cli`, `git-credential-nostr`, or an
agent) and the Buzz relay's narrow HTTP surface. Verification is entirely
stateless per NIP-98 itself; Buzz layers a shared, community-scoped replay-prevention
store (Redis, via `buzz-pubsub`) on top because a stateless per-pod cache cannot
detect a reused event id once a deployment runs multiple relay pods.

## Operations

NIP-98 is not itself a set of distinct RPC operations -- it is a single auth
mechanism reused across every HTTP route that needs one. The table below lists
where it gates a request, not a menu of NIP-98-specific calls.

| Operation (gated route/surface) | Defined in | Summary |
|---|---|---|
| Shared verifier | `crates/buzz-auth/src/nip98.rs::verify_nip98_event` | Parses the event, checks kind==27235, Schnorr signature, +-60s timestamp, single `u` tag, single `method` tag, at-most-one `payload` tag with optional SHA-256 body-hash check; returns the authenticated pubkey. |
| Shared replay guard | `crates/buzz-auth/src/nip98_replay.rs::Nip98ReplayGuard` | Community-scoped, atomic `try_mark`; production impl is a Redis `SET NX EX` in `buzz-pubsub`. |
| `POST /events` | `crates/buzz-relay/src/api/bridge.rs` (`verify_bridge_auth_with_options`, line ~725/858) | Generic Nostr event submission over HTTP. |
| `POST /query` | `crates/buzz-relay/src/api/bridge.rs` (line ~996/1049) | Nostr REQ filters over HTTP. |
| `POST /count` | `crates/buzz-relay/src/api/bridge.rs` (line ~1525/1576) | Nostr COUNT filters over HTTP. |
| Invite claim/creation routes | `crates/buzz-relay/src/api/invites.rs` | Reuses `bridge::nip98_expected_url`/`check_nip98_replay`. |
| GIF search/proxy routes | `crates/buzz-relay/src/api/gifs.rs` | Reuses the same bridge helpers. |
| Workflow webhook/management routes | `crates/buzz-relay/src/api/workflows.rs` | Reuses the same bridge helpers. |
| Deployment-admin API (`/api/admin/v1/...`) | `crates/buzz-relay/src/api/admin/auth.rs` | Resolves the authenticated pubkey to an `AdminPrincipal` (Operator/Moderator/none); own URL-prefix re-addition (`ADMIN_API_PREFIX`). |
| Git smart HTTP (`GET .../info/refs`, `POST .../git-upload-pack`, `POST .../git-receive-pack`) | `crates/buzz-relay/src/api/git/transport.rs::GitAuth` | Same verifier, with method-binding and replay dedup intentionally disabled -- see *Contract and stability*. |

Not an operation of this interface: Blossom media upload/download
(`crates/buzz-relay/src/api/media.rs`), which authenticates with a structurally
different `kind:24242` event (BUD-01/BUD-11) via `buzz_media::auth::verify_blossom_auth_event`,
never `buzz_auth::verify_nip98_event`. See *Boundary*.

## Contract and stability

- **Inputs.** An HTTP request whose `Authorization` header is `Nostr <base64(JSON-serialized kind:27235 event)>`. The event must carry exactly one `u` tag (the request URL, compared host/scheme-normalised with the trailing slash stripped) and exactly one `method` tag (compared case-insensitively); at most one `payload` tag (SHA-256 hex of the body) is allowed, and a second, contradictory `payload` tag is rejected rather than resolved by taking the first.
- **Outputs.** On success, the caller's `nostr::PublicKey`, which the calling handler then uses for authorization decisions (channel membership, admin role resolution, git push/pull authorization) -- this node covers authentication only, not what each caller does with the resulting identity.
- **Errors/rejection.** `AuthError::Nip98Invalid(String)` for any structural or content failure (bad JSON, wrong kind, bad signature, timestamp outside the +-60s window, URL/method mismatch, bad payload hash, wrong tag cardinality); `AuthError::Nip98Replay` for a structurally valid event whose id was already claimed within the replay window. Bridge-family callers translate both to HTTP 401. The inner error string is documented as safe for server logs but not for verbatim forwarding to clients.
- **Authentication/authorization.** NIP-98 verification establishes *authentication* (which pubkey signed this exact request) only; authorization (may this pubkey do this) is a separate, per-endpoint decision made by the calling handler after verification succeeds (e.g. admin role resolution in `admin/auth.rs`, channel membership checks elsewhere, git's pre-receive hook for push).
- **Timestamp window.** +-60 seconds (`TIMESTAMP_TOLERANCE_SECS` in `nip98.rs`) is fixed in code, not configurable per deployment.
- **Replay prevention.** Not part of NIP-98 itself; Buzz's addition. `DEFAULT_REPLAY_TTL_SECS = 120` is a floor (twice the timestamp window) and `MAX_REPLAY_TTL_SECS = 3600` is a ceiling; the shared guard's contract requires atomic set-if-absent and fail-closed behavior on any storage error -- a caller must reject rather than admit the request when the guard errors. This applies to the bridge family (`/events`, `/query`, `/count`, invites, gifs, workflows) and to the admin API. **It does not apply to git smart HTTP**, which intentionally skips replay dedup because git's own credential protocol reuses one signed token across a clone/push session (info/refs GET, then upload-pack/receive-pack POST) -- rejecting the second use would break normal git operations. The compensating controls named in `transport.rs` for that gap are the +-60s timestamp window, the repo-scoped `u` tag, and HTTPS transport.
- **Method binding.** Bridge-family and admin routes verify the `method` tag against the real HTTP method. Git smart HTTP does not: it deliberately passes the event's own signed method back into the verifier (a tautological check), because git's helper signs once with GET and reuses the token for a later POST; the URL lock plus timestamp window are the stated compensating controls there.
- **Host binding.** Every call site constructs its expected `u`-tag URL from the per-request, server-resolved tenant host (`TenantContext`), never from the deployment's static configured relay URL -- closing a documented cross-community host-binding hole under multi-tenant deployments.
- **Versioning/compatibility.** NIP-98 upstream defines no version tag or negotiation mechanism; this is a single, fixed event shape (kind:27235, `u`/`method`/optional `payload` tags). Buzz's replay-prevention floor/ceiling and per-consumer payload-required policy are local additions layered on top, not part of the upstream contract, and changing the fixed +-60s window or the `u`/`method` tag semantics would be a breaking change to every caller listed above.
- **Ordering/idempotency.** A given signed event is verified independently per request; the shared replay guard turns "verify" into an idempotent-once-per-id operation everywhere it is enabled (bridge family, admin), but git smart HTTP explicitly opts out, so the same signed event may be legitimately reused there within its validity window.

## Boundary

This node does not describe:
- **A single Nostr event kind's own full wire contract.** `kind:27235`'s tag
  shape is summarized above only as needed to state the auth contract; a
  dedicated event-kind node (per `templates/event-kind.md`) would be the place
  for an exhaustive per-tag catalogue, and none exists yet for kind:27235.
- **Blossom media authorization (`kind:24242`, BUD-01/BUD-11).** Despite surface
  similarity (`Authorization: Nostr <base64(event)>`, used to gate the same
  relay's HTTP surface), Blossom auth is verified by
  `buzz_media::auth::verify_blossom_auth_event` against a different kind and a
  different tag/hash contract, and is out of scope here. A future
  `interfaces-http-media` node (tracked as issue #984, not yet merged on
  `origin/launchpad`) would own that scheme.
- **Authorization decisions made after authentication succeeds** (channel
  membership, admin role resolution, git push authorization via the
  pre-receive hook) -- those are each their own contract, owned by the crate
  that implements them, not by this shared verifier.
- **Field-by-field, domain-expert-depth parameter cataloguing** of every HTTP
  route this interface gates -- see each route's own handler/tests for that
  depth.

## Relationships

None declared. `origin/launchpad`'s corpus tree carries no `interfaces/` node at
this node's recorded revision, so there is no other interface-shaped or
event-kind node yet for this node to legitimately `references`, `implements`,
or sit `part-of`. The natural first edge -- toward an `interfaces-http-media`
node once issue #984 merges, or toward a future kind:27235 event-kind node --
should be added when that target exists, per `AGENTS.md`'s rule that a
`relationships.target` naming an id no loaded node carries is a hard
validation error.

## Scope and omissions

**This node covers** the shared NIP-98 verifier and replay guard in
`buzz-auth`, and every HTTP call site in `buzz-relay` that authenticates with
it (the generic bridge endpoints `/events`/`/query`/`/count`, invites, gifs,
workflows, the deployment-admin API, and git smart HTTP) -- what each accepts,
rejects, and the deliberate differences between call sites (git's skipped
method-binding and replay dedup).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Blossom media auth (kind:24242, BUD-01/BUD-11) | A future `interfaces-http-media` node (issue #984, unmerged) |
| Kind:27235's own exhaustive tag-by-tag wire contract | A future event-kind node, if one is written |
| Per-endpoint authorization after authentication (channel membership, admin roles, git push policy) | Each owning crate's own contract |
| NIP-42 WebSocket auth (the sibling scheme for the WebSocket surface) | Not in scope; briefly contrasted above only |

**Expected but not verified when this node was written:**
- The upstream NIP-98 specification text itself (`nostr-protocol/nips`,
  `98.md`) was not fetched from GitHub directly; this node's description of the
  wire format is verified against this repository's own implementation
  (`nip98.rs`'s doc comment and code) and against the pinned link this corpus
  already uses for sibling NIPs, not against a freshly-read copy of `98.md`.
- Whether `buzz-cli`, `git-credential-nostr`, or the desktop/mobile clients
  construct NIP-98 events through a single shared builder or independently was
  not traced in this pass -- this node describes the relay-side verifier
  contract, which is uniform, not each client's signing code path.

## Example: valid request (bridge `/events`)

A client signs a `kind:27235` event with `u = "https://relay.example.com/events"`
and `method = "POST"`, base64-encodes it, and sends
`POST /events` with header `Authorization: Nostr <base64>` and a JSON body.
`verify_bridge_auth_with_options` decodes the header, calls
`verify_nip98_event` (which checks kind, signature, timestamp, `u`, `method`,
and, if present, the `payload` hash against the body), then `check_nip98_replay`
claims the event id in the community-scoped Redis seen-set. Both succeed ->
the handler proceeds as the authenticated pubkey (`crates/buzz-auth/src/nip98.rs`
tests: `valid_event_returns_pubkey`; `crates/buzz-relay/src/api/bridge.rs` test:
`verify_bridge_auth_accepts_nip98_event_signed_for_matching_host`).

## Example: failure (cross-community host binding + replay)

An event is signed with `u` bound to community A's host but the request
arrives at community B's host: `nip98_expected_url` builds B's own host into
the expected URL, `normalize_url` treats A's and B's hosts as unequal, and
`verify_nip98_event` returns `AuthError::Nip98Invalid` (URL mismatch) rather
than accepting a token signed for a different tenant
(`crates/buzz-relay/src/api/bridge.rs` test:
`verify_bridge_auth_rejects_nip98_event_signed_for_wrong_communitys_host`).
Separately, replaying the *same* valid event id a second time against the same
community is rejected with `AuthError::Nip98Replay` / HTTP 401 by
`check_nip98_replay`, even though the event itself would still pass
`verify_nip98_event` on its own
(`crates/buzz-relay/src/api/bridge.rs` test:
`nip98_replay_guard_rejects_same_pod_same_community_replay`).

## Authoritative specification

Upstream: [NIP-98 -- HTTP Auth](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/98.md),
pinned to the same commit this corpus already cites for NIP-01 and NIP-29.
