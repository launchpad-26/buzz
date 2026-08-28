---
id: layers-authentication-authentication
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
  - statement: "buzz-auth's own module documentation states Buzz supports two authentication paths -- NIP-42 (WebSocket, challenge/response over a signed kind:22242 event) and NIP-98 (HTTP, a signed kind:27235 event carried in an Authorization: Nostr header) -- and states as security invariants that AUTH events are never stored or logged, that every successful path produces an AuthContext bound to the connection, and that there is no JWT validation, no token management, and no IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "buzz-core defines KIND_AUTH = 22242 (the NIP-42 AUTH event kind) and KIND_HTTP_AUTH = 27235 (the NIP-98 HTTP Auth event kind) as the two event kinds these paths sign."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "AuthContext (buzz-auth::lib.rs) is the one shared result type both authentication paths produce: it carries the authenticated pubkey, a granted Vec<Scope>, an optional channel_ids restriction (reserved for future per-channel access control), which AuthMethod (Nip42 or Nip98) produced it, and an optional NIP-OA agent_owner_pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "AuthError enumerates the rejection reasons common to both cryptographic verification paths -- InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired, Nip98Invalid, Nip98Replay, PubkeyMismatch -- plus the separate authorization-layer variants InsufficientScope and ChannelAccessDenied, and a catch-all Internal; its doc comment states variants are designed to be safe to return to callers without leaking internal implementation details."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "Scope is a closed set of authorization capabilities (paired read/write scopes for messages, channels, users, jobs, subscriptions, files, plus AdminChannels and AdminUsers) stored as TEXT[] with an Unknown(String) variant preserved for forward compatibility; Scope::all_known() and Scope::all_non_admin() exist specifically for the dev-mode X-Pubkey path, which grants scopes without a real token to derive them from, and exclude admin scopes from the non-admin variant even in dev mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
  - statement: "require_scope, check_read_access and check_write_access (buzz-auth::access) enforce authorization as a check distinct from authentication itself: read/write access requires both a granted Scope and community-scoped channel membership via the ChannelAccessChecker trait, whose doc comment states every implementation MUST scope its query by TenantContext::community() to avoid a cross-community existence oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
  - statement: "AuthService::verify_auth_event, the NIP-42 entry point, performs pure cryptographic verification with no network call, no JWT, and no token lookup; both its own doc comment and buzz-auth's module documentation state this as a design invariant rather than an incidental implementation detail."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "On the relay's HTTP bridge surface (POST /events, /query, /count), verify_bridge_auth_with_options tries NIP-98 first (an Authorization: Nostr <base64> header) and falls back to a raw X-Pubkey header only when the community's require_auth_token configuration is false; the dev-mode fallback returns a zero event ID because its own comment states it carries no replay concern."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "buzz-db's api_token module (create_api_token, create_api_token_if_under_limit, get_api_token_by_hash_including_revoked, list_tokens_by_owner, revoke_token, revoke_all_tokens) stores API tokens hashed and scoped to (community_id, token_hash), each carrying an owner pubkey, a name, a Scope list, an optional channel_id restriction, and an optional expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/api_token.rs"
  - statement: "buzz-relay's Blossom media-upload authorization comment states explicitly that the relay-membership (NIP-43) gate is 'the only upload authority', independent of bearer-token / api_tokens storage and of the require_auth_token setting -- i.e. API-token-based auth is documented in that comment as a separate mechanism from the media path, not as something the media path itself consumes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs documents, as evidence for a conformance test row, that no self-service API-token-minting HTTP route exists in buzz-relay (router.rs's full route list has no /tokens route; crates/buzz-relay/src/api/ has no tokens module), and separately asserts that API tokens are consumed by a handler at crates/buzz-relay/src/api/media.rs:638 via an 'X-Auth-Token: buzz_*' header."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "That consumption claim does not match this repository at the recorded revision: the literal string \"X-Auth-Token\" occurs in exactly one place in the whole crates/ tree -- the test comment cited above -- and nowhere in any non-test source file; crates/buzz-relay/src/api/media.rs line 638 at this revision calls authenticate_media_read, which performs Blossom/NIP-98 signature verification, not API-token header parsing. get_api_token_by_hash_including_revoked and create_api_token_if_under_limit likewise have no callers anywhere in buzz-relay or buzz-cli at this revision -- their only callers are their own buzz-db::Db wrapper methods. Whether the test comment describes a since-refactored prior state, a not-yet-landed follow-on, or was inaccurate when written was not established; it is recorded here as an open discrepancy rather than resolved."
    entry_class: FACT
    evidence:
      - "grep(pattern='X-Auth-Token', scope='crates/') -> 1 match, in a comment in crates/buzz-test-client/tests/conformance_multitenant.rs; 0 matches in any non-test source file"
      - "crates/buzz-relay/src/api/media.rs"
      - "grep(pattern='get_api_token_by_hash_including_revoked|create_api_token_if_under_limit', scope='crates/') -> callers limited to crates/buzz-db/src/lib.rs's own Db wrapper methods and the doc-comment in conformance_multitenant.rs; no call sites in crates/buzz-relay or crates/buzz-cli"
  - statement: "The corpus already documents the NIP-42 WebSocket authentication round trip in full, as architecture-flows-websocket-authentication (launchpad/docs/corpus/architecture/flows/websocket-authentication.md): the challenge/response mechanics, the connection state machine, the ban/allowlist/membership gates, NIP-OA delegation, and per-message-type enforcement. This document does not restate that flow's step-by-step mechanics."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "type: layers is chosen over architecture because, by the one precedent merged so far, architecture is used for nodes about the relay's own internal structure and flows -- the sibling architecture-flows-websocket-authentication node lives under architecture/flows/ and documents exactly one connection-level flow -- while this node's subject is a cross-cutting concept spanning WebSocket, HTTP, and token-based access, matching both the issue's own target path under layers/authentication/ and layers being the closer-named surface among node.schema.json's 13 enum values for a category-level concept that is not itself a single architectural flow."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
    confidence: 0.6
  - statement: "Issue #1026's Definition of Done requires this document to define the term in one sentence before deeper explanation, state boundaries/non-goals or what the concept must not be confused with, link the concept to related concepts/implementation/verification without duplicating their canonical content, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1026 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# Authentication

How a party interacting with a Buzz relay -- a human client, a desktop/mobile app, an
agent, or an automated integration -- proves its identity, and what that proof does and
does not grant it. This is the category-level concept node for authentication in Buzz;
it defines the shared shape and states the boundary against the specific mechanisms and
flows that implement it, rather than duplicating their mechanics.

## Definition

**Authentication in Buzz is proof of control over a Nostr keypair, established by a
Schnorr signature over a purpose-built event, with no password, session cookie, JWT, or
external identity provider involved at any point.** A party authenticates by signing an
event of a kind reserved for that purpose (kind:22242 for NIP-42, kind:27235 for
NIP-98) with the private key matching the pubkey it claims, and the relay verifies that
signature -- and a small set of freshness and binding checks alongside it -- before
admitting the connection or request. `buzz-auth`'s own module documentation states this
explicitly as a security invariant: no JWT validation, no token management, no IdP
runtime dependency.

**What authentication proves, and what it does not.** A successful authentication
proves *who signed*, nothing more. It answers "which pubkey is this." It does not by
itself decide whether that pubkey may read a given channel, write to it, or perform an
administrative action -- those are authorization questions, answered separately by
`Scope` grants and by community/channel membership checks that run after
authentication succeeds, not as part of it. Conflating the two is the boundary this
document exists to draw: a valid signature is a necessary condition for access, never
a sufficient one.

**Disambiguation.** "Auth" in this corpus and in the Buzz source tree is used loosely
for both authentication and authorization; this document is about the *authentication*
half only -- proving identity. The `AuthError` enum in `buzz-auth` mixes both kinds of
rejection in one type (`InvalidSignature` is an authentication failure;
`InsufficientScope` and `ChannelAccessDenied` are authorization failures), which is a
useful signal that the codebase itself treats them as one error surface even though
they are conceptually distinct gates.

```mermaid
flowchart LR
    subgraph paths["Authentication paths (prove identity)"]
        nip42["NIP-42\nWebSocket AUTH\nkind:22242"]
        nip98["NIP-98\nHTTP Authorization: Nostr\nkind:27235"]
        devx["X-Pubkey header\n(dev-mode only,\nrequire_auth_token = false)"]
    end
    paths --> ctx["AuthContext\npubkey + scopes + auth_method"]
    ctx --> authz["Authorization gates\n(Scope, channel membership,\nban, community membership)"]
```

## Background

Buzz's authentication design deliberately excludes the machinery most web systems
default to: no password store, no session table, no JWT issuance or refresh, no
external identity provider to depend on at runtime. `buzz-auth`'s module documentation
states this as a design invariant, not merely a current limitation. The reasoning
visible in the code is that a Nostr keypair is already the identity primitive every
other part of Buzz depends on (events are signed, pubkeys are the actor identity in
every kind), so authentication reuses that same primitive rather than introducing a
second identity system alongside it.

Two mechanisms exist because the relay has two distinct transports that each need
their own binding of a signature to a request: WebSocket connections are long-lived and
benefit from a challenge (preventing a captured signature from being replayed against a
different session), while individual HTTP requests are naturally per-request and NIP-98
binds the signature to the specific method, URL, and (optionally) body hash instead of
a server-issued challenge. A third path -- a raw `X-Pubkey` header -- exists but is
explicitly gated to development mode only, active exclusively when a community's
`require_auth_token` setting is `false`; it grants broad scopes (`Scope::all_known()`
or `Scope::all_non_admin()`) precisely because there is no real credential to derive
narrower ones from.

A fourth surface, API tokens, exists at the storage layer in `buzz-db` -- hashed,
community-scoped, with owner pubkey, name, granted scopes, optional channel
restriction, and optional expiry -- but at the recorded revision this document could
not confirm a request-time consumer of that table anywhere in `buzz-relay`'s HTTP
handlers (see *Scope and omissions* below for the specific discrepancy found and left
unresolved).

## Use cases

A reader needs this document when:

- **Adding a new HTTP or WebSocket handler** and needing to know which authentication
  state to check, and where authentication ends and authorization begins, before
  writing an access check.
- **Reviewing a diff that touches auth** and needing the shared vocabulary --
  `AuthContext`, `AuthMethod`, `Scope`, the fail-closed convention on database errors
  during ban/allowlist/membership checks -- without re-deriving it from source each
  time.
- **Onboarding to Buzz's security model** and needing the one-paragraph answer to "how
  does Buzz know who I am" before diving into either transport's specific flow.
- **Deciding where a new claim belongs**: whether it is about authentication itself
  (this node and its siblings) or about authorization/access control (a different,
  not-yet-written concept node) -- the *Definition* section above is the boundary to
  check against.

## Comparison

| Mechanism | Transport | Event kind | Freshness binding | Availability |
|---|---|---|---|---|
| NIP-42 | WebSocket | kind:22242 | Relay-issued challenge, +/-60s window | Always, on every WS connection |
| NIP-98 | HTTP | kind:27235 | Signed `created_at` (+/-60s), optionally a body-hash `payload` tag | Always, on the HTTP bridge and Blossom media surfaces |
| X-Pubkey header | HTTP | none (no signature) | none | Dev mode only, gated by `require_auth_token = false` |
| API token | HTTP (intended) | none (opaque hashed token) | Token expiry, not per-request freshness | Storage layer exists (`buzz-db`); no confirmed request-time consumer at the recorded revision |

## Related resources

- **`architecture-flows-websocket-authentication`** (linked via this node's
  `relationships`) -- the full NIP-42 challenge/response round trip: connection admission,
  the challenge, the client's signed response, the ban/allowlist/membership gates, NIP-OA
  delegation, and per-message-type enforcement. Read that node for WebSocket mechanics;
  this node does not repeat them.
- **NIP-98 HTTP Auth** -- not yet a corpus node. `crates/buzz-auth/src/nip98.rs` and
  `crates/buzz-auth/src/nip98_replay.rs` are its implementation; this document names it
  as an expected sibling node rather than describing its mechanics here, per this task's
  own instruction not to fold a second mechanism's detail into the category-level
  document.
- **API tokens** -- not yet a corpus node. `crates/buzz-db/src/api_token.rs` is its
  storage-layer implementation; see *Background* and *Scope and omissions* for the
  specific consumption-path discrepancy this document found and left open rather than
  resolving.
- **Bearer-token presentation of API tokens** -- not yet a corpus node, and, per the
  discrepancy recorded above, not yet confirmed wired into any HTTP handler at the
  recorded revision either. Expected to become its own sibling node once (or if) that
  wiring exists to document.
- **NIP-29 channel membership and moderation** -- not yet a corpus node. The
  relay-membership gate that follows authentication (see the linked flow node's *Trust-
  boundary crossings* section) is part of authorization, not authentication, and is out
  of this node's scope.

## Scope and omissions

**This document covers** what authentication means in Buzz across all its current
mechanisms, the shared result type (`AuthContext`) and shared invariants (no JWT/session/
IdP, fail-closed authorization checks, authentication proves identity but not access),
and the boundary against authorization. It intentionally stays at the category level.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-42 WebSocket challenge/response step-by-step mechanics | `architecture-flows-websocket-authentication` (already in the corpus) |
| NIP-98 HTTP Auth verification mechanics (timestamp tolerance, URL normalization, replay protection) | An expected future sibling node (not yet in the corpus) |
| API token lifecycle (minting, rotation, revocation) and its HTTP presentation | An expected future sibling node (not yet in the corpus) -- see the discrepancy below |
| NIP-29 channel membership, moderation, and the ban/allowlist gates that run after authentication | A separate authorization-focused node, not yet in the corpus |
| NIP-OA agent-to-owner delegation as an attestation format | Named but not detailed in the linked flow node; not yet its own corpus node |

**A discrepancy found and deliberately left open, not resolved:**
`crates/buzz-test-client/tests/conformance_multitenant.rs` asserts, in a doc comment
supporting a conformance test row, that API tokens are consumed at
`crates/buzz-relay/src/api/media.rs:638` via an `X-Auth-Token: buzz_*` header. At the
recorded revision that claim does not match the source: the string `X-Auth-Token`
appears nowhere outside that one comment, line 638 in `media.rs` is
`authenticate_media_read` (a Blossom/NIP-98 call, not API-token parsing), and the
`buzz-db` functions that would look up an API token by hash have no callers in
`buzz-relay` or `buzz-cli`. This document does not decide whether the comment is stale,
describes an unlanded follow-on, or was simply inaccurate when written -- per this
corpus's evidence discipline (`AGENTS.md`, `ADR-0029`), a conflict between what a test's
own commentary asserts and what the referenced source actually shows is recorded, not
silently resolved in either direction.

**Expected but not verified when this node was written:**

- **Whether a bearer-token HTTP consumer for API tokens exists anywhere outside
  `crates/`** (for example in `desktop/` or `mobile/` client code, or in infrastructure
  configuration) was not checked; this document's search was scoped to the Rust
  workspace.
- **Whether `type: layers` will still read as the best-fitting enum value once more
  `layers`-typed sibling nodes exist** to compare against -- at the recorded revision
  this is the first node under `launchpad/docs/corpus/layers/`, so there is no sibling
  precedent within that surface to check consistency against, only the cross-surface
  comparison against `architecture` recorded in the evidence ledger above.
