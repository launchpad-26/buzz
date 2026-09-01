---
id: layers-authentication-bearer-token
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
  - statement: "buzz-auth's own module documentation tables two auth paths: NIP-42 over WebSocket (challenge/response, client signs a kind:22242 event) and NIP-98 over HTTP (a signed kind:27235 event carried in the `Authorization: Nostr` header), and states as a security invariant that no path involves JWT validation, token management, or an IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "`Kind::HttpAuth` is 27235 (`KIND_HTTP_AUTH`), and `nip98.rs`'s own module documentation states the scheme literally: the client signs a short-lived kind:27235 event and sends it as `Authorization: Nostr <base64(JSON-serialized-event)>`, described as 'stateless — no WebSocket session required.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "`verify_nip98_event` checks, in this order: the event parses as JSON, `kind == 27235`, the Schnorr signature (via `buzz_core::verify_event`), `created_at` within +/-60 seconds of server time, the `u` tag matches the expected request URL after normalization (case-insensitive scheme/host, trailing slash stripped, no loopback aliasing between `localhost`/`127.0.0.1`/`::1`), the `method` tag matches the expected HTTP method case-insensitively, and — only if a `payload` tag is present and a body was supplied — that `SHA-256(body)` equals the tag's hex value; on success it returns the event's `pubkey`."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "NIP-98 verification alone does not detect replay of the same signed event; `nip98_replay.rs`'s own module documentation states this is a required, separate hard gate under a horizontally-scaled ('any pod, any connection') deployment, because an in-process cache cannot carry the freshness proof across pods, and requires a shared, atomic, community-scoped seen-set (Redis `SET NX EX`) with a TTL of at least `DEFAULT_REPLAY_TTL_SECS` (120s, matching the doubled +/-60s timestamp tolerance) and at most `MAX_REPLAY_TTL_SECS` (3600s); a guard implementation MUST fail closed (reject) on any error checking or claiming the seen-set entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "`buzz-relay`'s HTTP bridge (`POST /events`, `/query`, `/count`) is authenticated via `verify_bridge_auth`, which first tries a `Authorization: Nostr <base64>` header and calls `buzz_auth::verify_nip98_event` against it; only when `require_auth_token` is `false` does it fall back to trusting a client-supplied `X-Pubkey` header with no signature check at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`require_auth_token` is populated from the `BUZZ_REQUIRE_AUTH_TOKEN` environment variable and defaults to `false` when unset; `main.rs` logs a warning at startup when it is `false`, stating explicitly that REST API requests bypass token auth in that mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "A source comment on the relay's NIP-11 `relay_limitation` builder states that `auth_required: true` (the WebSocket-side advertisement) is independent of `config.require_auth_token`, which it names 'the REST API token toggle' — the two auth surfaces (WebSocket NIP-42, REST NIP-98) are gated by separate configuration."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`docs/multi-tenant-relay.md` states directly that a connection is bound to an actor '(a pubkey, authenticated via NIP-42 on WebSocket or via a NIP-98-minted bearer token on REST)' — this repository's own architecture document names the NIP-98 signed event a 'bearer token' for the REST surface specifically, which is the term this node's id and path adopt."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "The relay's git smart-HTTP push handler (`POST /git/{owner}/{repo}/git-receive-pack`) documents its own authorization directly: 'Authorization: NIP-98 authenticates the pusher,' with ref-level authorization handled separately by a pre-receive hook's callback to an internal policy endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The relay's invite-code HTTP API (`POST /api/invites`, `POST /api/invites/claim`) is, per its own module documentation, 'both NIP-98 signed, outside the Nostr event data plane'; NIP-98 proves control of the joining pubkey while a separate HMAC embedded in the invite code proves an admin authorized the join — two different credentials doing two different jobs on the same endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "`buzz-core::kind::KIND_AUTH` (22242, the NIP-42 WebSocket AUTH event kind) carries the source comment 'never stored (carries bearer tokens)', and `buzz-db`'s own crate-level documentation repeats the same invariant: 'AUTH events (kind 22242) are never stored — they carry bearer tokens.' This is a second, different use of the phrase 'bearer token' from this node's own subject: it names an opaque credential that may ride *inside* a NIP-42 AUTH event's signed content (for example, to authenticate the connection onward to a third-party service), not the NIP-98 signed event itself acting as the credential. Neither source states what that embedded credential is used for or by whom; this node does not investigate it further, since doing so would be a second concept folded into this one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "`buzz-db` defines a persisted `api_tokens` table with full CRUD (`crates/buzz-db/src/store/api_token.rs`): `create_api_token` and a quota-checked `create_api_token_if_under_limit` (atomic, at most 10 active tokens per (community, owner) pair), a community-scoped hash lookup (`get_api_token_by_hash_including_revoked`, keyed on `(community_id, token_hash)` specifically to prevent a token minted in one community from authenticating in another), `list_tokens_by_owner`, and `revoke_token`/`revoke_all_tokens`. Each record carries an owner pubkey, a name, JSON-encoded scopes, an optional channel-id allowlist, and expiry/revocation timestamps — the same general shape (opaque, hashed, holder-presented, revocable) as the industry-standard bearer-token pattern this node's Definition describes, and structurally independent of the NIP-98 signed-event mechanism this node otherwise documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/api_token.rs"
  - statement: "A repository-wide search for `ApiTokenRecord`, `get_api_token_by_hash`, and `create_api_token` across `crates/`, `desktop/`, and `mobile/` at the recorded revision matches only `crates/buzz-db/src/store/api_token.rs`, `crates/buzz-db/src/lib.rs` (the `Db` methods that wrap the module), and `crates/buzz-test-client/tests/conformance_multitenant.rs` (a row-44 multi-tenancy conformance test exercising the lookup directly). No file under `crates/buzz-relay` or `crates/buzz-auth` calls any `api_token` function, so as of this revision no HTTP handler retrieves or verifies a caller-presented token against the `api_tokens` table — it is not part of any currently-live authentication path."
    entry_class: FACT
    evidence:
      - "grep(pattern='ApiTokenRecord|get_api_token_by_hash|create_api_token', scope='crates/,desktop/,mobile/') -> crates/buzz-db/src/store/api_token.rs, crates/buzz-db/src/lib.rs, crates/buzz-test-client/tests/conformance_multitenant.rs, run at revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`architecture-flows-websocket-authentication` (merged on `origin/launchpad`) documents the NIP-42 WebSocket flow this node contrasts against, and its own Scope and omissions section names 'NIP-98 HTTP Auth (crates/buzz-auth/src/nip98.rs, kind:27235) — the sibling auth path for the relay's HTTP surface' as a gap, stating it 'deserves its own node' and is 'not yet in this corpus' — this node is that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "`architecture-flows-http-event-submission` and `architecture-flows-git-push` (both merged on `origin/launchpad`) each independently document a concrete NIP-98-bearer-token consumer at the flow/procedure level of detail this concept node deliberately does not repeat: `POST /events`'s exact verification and replay-check sequence, and the git push handler's authorization boundary, respectively."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "Checked immediately before finalizing front matter: `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists `architecture/flows/websocket-authentication.md` (id `architecture-flows-websocket-authentication`), `architecture/flows/http-event-submission.md` (id `architecture-flows-http-event-submission`), and `architecture/flows/git-push.md` (id `architecture-flows-git-push`) as present, so all three `references` targets below resolve against the branch this change merges into; no `layers/` node exists yet on that branch, so this is the first node of `type: layers`."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes architecture/flows/websocket-authentication.md, architecture/flows/http-event-submission.md, architecture/flows/git-push.md; no layers/ directory present"
  - statement: "`nip98.rs`'s own `#[cfg(test)] mod tests` cover a valid event, a wrong kind, an expired timestamp, a URL mismatch, a method mismatch, correct and incorrect `payload`-hash matching, trailing-slash URL normalization, and that `localhost`/`127.0.0.1`/`::1` are treated as distinct hosts rather than aliased; `nip98_replay.rs`'s own `#[cfg(test)] mod tests` separately cover the replay key's community-scoping, its all-lowercase-ASCII shape, and that `DEFAULT_REPLAY_TTL_SECS` and `MAX_REPLAY_TTL_SECS` satisfy the gate's own stated floor and ceiling."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "`CHANGELOG.md` records a prior 'media bearer-token auth' mechanism as removed in commit 0701f47f4a31a904ebcd9f360cbd6aadaff9d784, 'fix(relay): remove media bearer-token auth ([#1444])', touching only `crates/buzz-relay/src/api/media.rs` and mobile media-upload code — the media path's current Blossom kind:24242 auth (see *Boundary and non-goals*) is not a survival of that older, now-deleted mechanism."
    entry_class: FACT
    evidence:
      - "CHANGELOG.md"
      - "commit 0701f47f4a31a904ebcd9f360cbd6aadaff9d784"
  - statement: "Issue #1027's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals or what the concept must not be confused with, link the concept to related concepts/implementation/verification, and use examples only to clarify the concept rather than introduce a second one — the category-specific tail for a concept-typed corpus document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1027 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-flows-git-push
---

# Bearer token (REST HTTP authentication)

What a "bearer token" is in Buzz, which concrete mechanism realizes it, where it is
and is not used, and the two other things this repository's own text calls by a
similar name that this node is deliberately *not* about.

## Definition

**A bearer token is a self-contained, time-boxed credential that a caller presents
with a request, and that the receiving server accepts as sufficient proof of the
caller's identity for that one request, on the strength of possessing and presenting
it — no prior handshake, no server-held session, no shared secret exchanged in
advance.** In Buzz, the one bearer-token mechanism actually wired into a live
authentication path is **NIP-98 HTTP Auth (Nostr kind:27235)**: a short-lived,
Schnorr-signed Nostr event, base64-encoded and sent as `Authorization: Nostr
<base64(event)>`, verified per request against the target URL, HTTP method, and
(optionally) a hash of the request body, with a shared replay-protection gate
closing the one thing signature verification alone cannot catch — a captured,
still-valid token being replayed. `docs/multi-tenant-relay.md` names this pattern
directly: an actor is authenticated "via NIP-42 on WebSocket or via a NIP-98-minted
bearer token on REST." That sentence is where this node's own name comes from.

**A note on the literal header scheme.** The `Authorization` header's scheme token
in Buzz's own code is the literal string `Nostr`, not `Bearer` — `Authorization:
Nostr <base64>`, checked with `.strip_prefix("Nostr ")` everywhere this pattern is
consumed. "Bearer token" here names the *authentication pattern* — whoever holds
and presents a valid, unexpired token is trusted, with no further identity check —
using the vocabulary this repository's own architecture document already chose for
it (`docs/multi-tenant-relay.md`, cited above), not a literal `Authorization:
Bearer ...` header. Searching the codebase for the header string `Bearer` will not
find this mechanism. This node does not cite any external bearer-token
specification (e.g. RFC 6750) as a source, since none was opened while authoring
it; the definition above is grounded in Buzz's own primary sources only.

## Use cases

A caller reaches for the NIP-98 bearer-token pattern whenever it needs to make a
single, stateless HTTP request to the relay and prove its Nostr identity for that
request alone, without first opening and maintaining a WebSocket connection. At the
recorded revision this covers:

- **The Nostr-HTTP bridge** — `POST /events`, `/query`, and `/count` — the HTTP-only
  path onto the same event data plane the WebSocket protocol serves
  (`crates/buzz-relay/src/api/bridge.rs`).
- **Structured workflow reads** — run and approval state exposed over HTTP
  (`crates/buzz-relay/src/api/workflows.rs`, gated through the same
  `verify_bridge_auth`).
- **Git smart-HTTP push** — `POST /git/{owner}/{repo}/git-receive-pack` names NIP-98
  as what "authenticates the pusher," separately from the ref-level authorization a
  pre-receive hook enforces afterward (`crates/buzz-relay/src/api/git/transport.rs`).
- **Relay invites** — minting and claiming an invite code are both NIP-98-signed
  requests, proving control of the acting pubkey; the invite code's own HMAC is a
  second, unrelated credential proving an admin authorized the join
  (`crates/buzz-relay/src/api/invites.rs`).

A caller does **not** use this pattern for a WebSocket connection (NIP-42's
connection-bound challenge/response covers that instead — see *Related resources*),
and, at this revision, cannot use it to authenticate against the `api_tokens` table
described under *Boundary and non-goals* below, because nothing yet checks a
request against that table.

## Comparison

| Mechanism | Transport | Credential | Session state | Wired to a live auth path? |
|---|---|---|---|---|
| NIP-42 | WebSocket | Signed kind:22242 event, answering a per-connection server challenge | Yes — `AuthState` on the connection | Yes |
| **NIP-98 (this node)** | HTTP | Signed kind:27235 event, self-contained per request | No — stateless per request | Yes |
| `api_tokens` (`buzz-db`) | HTTP (no consumer yet) | Opaque token, SHA-256-hashed at rest, minted/revoked via CRUD | No — designed to be stateless like NIP-98 | No — CRUD exists, no handler verifies against it |

NIP-98 and `api_tokens` share the bearer-token shape (holder-presented,
per-request, no session); they are not the same mechanism, and only NIP-98 is
currently checked by any request handler.

## Boundary and non-goals

**Not NIP-42 WebSocket authentication.** NIP-42 is connection-bound
challenge/response, not a bearer token: the server issues a fresh, unpredictable
challenge per connection, and the client's signed reply is meaningless replayed
against a different connection or a different challenge. `architecture-flows-
websocket-authentication` (linked below) is the canonical node for that mechanism.

**Not the embedded-token meaning of "bearer token" elsewhere in this repository.**
`buzz-core`'s `KIND_AUTH` (22242) constant and `buzz-db`'s crate documentation both
say NIP-42 AUTH events are "never stored" because "they carry bearer tokens" —
naming an opaque credential that may ride *inside* a NIP-42 AUTH event's own signed
content, not the AUTH event itself acting as one. What that embedded credential is,
or who consumes it, is not established by either source and is out of this node's
scope.

**Not `api_tokens`, as currently implemented.** `buzz-db` defines a complete,
schema-backed, revocable API-token store with the same holder-presented shape this
node defines — but as of the recorded revision, no relay handler retrieves or
verifies a caller-presented token against it (see the evidence ledger's grep
result). Describing it as a working authentication mechanism would overstate
current behavior; it is named here as a structurally related, not-yet-wired
adjacent feature; whether or how it becomes one is out of this node's scope.

**Not JWTs, OAuth access tokens, or any IdP-issued credential.** `buzz-auth`'s own
module documentation states plainly that no auth path involves JWT validation,
token management, or an IdP runtime dependency. Buzz's bearer-token pattern is
self-signed and self-verifying, not issued by a third party.

**Not replay protection's own mechanics in detail.** This node states that replay
protection is a required property of the pattern and names the shared-seen-set
shape `nip98_replay.rs` requires; the exact Redis key scheme, TTL clamping rules,
and per-pod correctness argument belong to `architecture-flows-http-event-
submission`, which documents one concrete request path through it end to end.

## Related resources

- `architecture-flows-websocket-authentication` — the NIP-42 sibling mechanism this
  node contrasts against.
- `architecture-flows-http-event-submission` — a full step-by-step trace of NIP-98
  verification and replay-checking for one concrete endpoint (`POST /events`).
- `architecture-flows-git-push` — a second concrete NIP-98-bearer-token consumer,
  layered under a different authorization model (channel role / protection rules)
  once the transport-level check passes.

**Verification.** `crates/buzz-auth/src/nip98.rs`'s own `#[cfg(test)] mod tests`
cover a valid event, a wrong kind, an expired timestamp, a URL mismatch, a method
mismatch, correct and incorrect payload-hash matching, trailing-slash URL
normalization, and — specifically — that `localhost`/`127.0.0.1`/`::1` are treated
as distinct hosts rather than aliased. `crates/buzz-auth/src/nip98_replay.rs`'s own
test module separately covers the replay key's community-scoping, its
all-lowercase-ASCII shape, and that the default and maximum TTL constants satisfy
the gate's own stated bounds. Endpoint-level, end-to-end verification of this
pattern belongs to the flow nodes linked above, not to this one.

**A related historical fact.** A distinct, now-removed "media bearer-token auth"
mechanism once existed on the media-upload path and was deleted in favor of the
Blossom kind:24242 signed-event scheme described under *Boundary and non-goals*;
`CHANGELOG.md` records the change as "fix(relay): remove media bearer-token auth."
This confirms Blossom's current auth is not a survival of an older literal
bearer-token mechanism, and that no other bearer-token path was removed from
media in its place.

## Scope and omissions

**This document covers** what "bearer token" means as a security pattern, which
concrete mechanism in Buzz realizes it (NIP-98 HTTP Auth, kind:27235), the surface
area that currently checks it (the HTTP bridge, workflow reads, git push, invites),
the one config toggle that governs whether it is enforced at all
(`BUZZ_REQUIRE_AUTH_TOKEN` / `require_auth_token`), and the boundary against three
other things this repository's own text calls by a similar name.

**It does not cover, and these are gaps rather than silence:**

- **The byte-by-byte verification and replay-check sequence** for any one endpoint —
  that is `architecture-flows-http-event-submission`'s and `architecture-flows-git-
  push`'s level of detail, not this node's.
- **What an embedded bearer token inside a NIP-42 AUTH event's content is used for,
  or by whom.** Named under *Boundary and non-goals*, not investigated further.
- **Whether, or when, `api_tokens` becomes a live authentication path.** This node
  reports what a repository-wide search found (no consumer) at the recorded
  revision; it does not speculate about roadmap or intent, and no `type:task` or
  `type:adr` issue describing that work was found to cite.
- **The dev-mode `X-Pubkey` fallback's own security posture** beyond noting it
  exists and is gated by the same `require_auth_token` toggle — a caller relying on
  it is not presenting a bearer token at all, since nothing is verified.

**Expected but not verified when this node was written:**

- **Whether any client (desktop, mobile, `buzz-cli`, or an external integrator)
  actually constructs and sends a NIP-98 request today**, as opposed to the server
  side accepting one. `crates/buzz-ws-client` implements the NIP-42 client half
  directly; no equivalent NIP-98 client-side builder was located during authoring,
  so client-side usage of this pattern is inferred from the server accepting it,
  not observed from a caller emitting it.
- **Whether Blossom media upload's kind:24242 auth event (`crates/buzz-relay/src/
  api/media.rs`, BUD-11) should be considered a fourth instance of this same
  pattern.** It shares the identical `Authorization: Nostr <base64(event)>` header
  shape and is verified per-request with no session, but is a different event kind
  under a different specification (BUD-11, not NIP-98), with its own extractor
  (`extract_blossom_auth`) rather than `buzz_auth::verify_nip98_event`. It is
  mentioned here only to flag the boundary question, per `AGENTS.md`'s instruction
  that a second concept discovered while writing is filed rather than folded in;
  `architecture-flows-media-upload` (not read in full during this task) may already
  be the right home for a fuller treatment.
