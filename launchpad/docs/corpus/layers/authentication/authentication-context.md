---
id: layers-authentication-authentication-context
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-auth defines AuthContext as 'the result of a successful authentication, bound to a connection,' carrying pubkey, scopes, channel_ids, auth_method, and agent_owner_pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "buzz-auth's own module documentation states as a security invariant that every successful auth path (NIP-42 or NIP-98) produces an AuthContext bound to the connection, with no JWT validation, no token management, and no IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "AuthContext exposes a has_scope method that checks membership in its scopes vector; this is exercised directly by the auth_context_scope_check unit test."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "buzz-relay's ConnectionState wraps a RwLock<AuthState>, and AuthState is an enum with exactly three variants -- Pending{challenge}, Authenticated(AuthContext), and Failed -- so an AuthContext exists only inside the Authenticated variant, never standing on its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "ConnectionState also carries a separate `tenant: TenantContext` field, resolved from the connection host before any frame is read and independent of `auth_state` -- a connection's community/tenant scope and its authentication context are two distinct fields on the same struct, not the same concept."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The already-merged corpus flow node architecture-flows-websocket-authentication states explicitly, in its own trigger section, that the tenant binding 'is fixed for the connection's lifetime and is not part of the auth flow itself.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "buzz-relay's event-ingestion handler defines a second, transport-neutral IngestAuth enum, documented in its own doc comment as 'Authentication context for event ingestion -- transport-neutral,' with two variants: Nip42{pubkey, scopes, channel_ids, conn_id} for WebSocket connections and Http{pubkey, scopes, auth_method} for HTTP requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "IngestAuth::Nip42 is constructed by copying an already-established connection AuthContext's pubkey, scopes, and channel_ids fields, plus the connection id, at the point a WebSocket EVENT message is submitted for ingestion."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "IngestAuth::Http is constructed at the HTTP `POST /events` bridge handler after NIP-98 verification and relay-membership enforcement succeed, granting Scope::all_known() in pure-Nostr mode with auth_method set to HttpAuthMethod::Nip98."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "IngestAuth's principal_pubkey_bytes method returns the authenticated pubkey's bytes and is documented as the pubkey 'used for principal-scoped accounting and policy lookups' -- distinct from any event-content signer, such as a NIP-17 gift-wrap envelope's ephemeral signing key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The accounting_uses_authenticated_principal_pubkey unit test asserts principal_pubkey_bytes() returns the authenticated principal's key bytes even when a distinct envelope-signer keypair exists, confirming the accounting boundary is the authenticated context, not the event's own signature."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The ingest_auth_is_http_returns_true_for_http_variant and ingest_auth_is_http_returns_false_for_nip42_variant unit tests confirm IngestAuth::is_http() correctly distinguishes the two transport-specific variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "IngestAuth::channel_ids() is documented as 'Token-level channel restriction (WS connections with scoped tokens -- legacy)' and its own doc comment states that in pure Nostr mode it always returns None, because channel access is enforced via NIP-29 membership checks instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A source comment in command_executor.rs records that the relay's older REST handlers ensured the authenticated user existed via a function named extract_auth_context, and that the command executor (built later, on top of the ingest pipeline) must now perform the equivalent user-existence step explicitly rather than relying on that helper."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs"
  - statement: "AuthContext and IngestAuth are two independent Rust types with no shared trait and no From/Into conversion between them -- IngestAuth::Nip42 is built by hand-copying AuthContext's fields at each call site rather than through a defined conversion, so a field added to AuthContext is not guaranteed to propagate to IngestAuth without a matching manual edit at both construction sites."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/lib.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.75
  - statement: "Issue #1024's definition of done, combined with its document-type-specific DoD tail, requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link the concept to related concepts/implementation/verification, and use examples only to clarify it -- never to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1024 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# Concept: Authentication Context

An **authentication context** is the small, transport-bound bundle of proven
identity and granted permission that Buzz attaches to a connection or request
once cryptographic authentication succeeds -- not a token, not a session, and
not the same thing as which community the connection belongs to.

## Definition

An authentication context is the record of *who this connection or request has
proven itself to be, and what it is allowed to do*, produced the moment a
NIP-42 (WebSocket) or NIP-98 (HTTP) signature check succeeds, and consulted by
every later handler that needs to know the caller's identity or permissions
instead of re-verifying a signature. Buzz's code carries this concept as two
related but distinct types, not one:

- **`buzz_auth::AuthContext`** -- the connection-scoped shape. Fields: `pubkey`
  (the authenticated Nostr public key), `scopes` (permission scopes granted),
  `channel_ids` (an optional token-level channel restriction), `auth_method`
  (`Nip42` or `Nip98`), and `agent_owner_pubkey` (the NIP-OA-proven owner
  pubkey, when the caller authenticated as an agent acting for an owner). It
  lives inside `buzz-relay`'s `AuthState::Authenticated` variant, one per
  WebSocket connection, for the life of that connection.
- **`handlers::ingest::IngestAuth`** -- the event-ingestion shape, explicitly
  documented as "transport-neutral." It has two variants, `Nip42 { pubkey,
  scopes, channel_ids, conn_id }` and `Http { pubkey, scopes, auth_method }`,
  and is built fresh for each event submitted through the shared WS+HTTP
  ingestion pipeline (`ingest_event`) rather than being reused across events.

Both shapes exist because two different consumers need the concept in two
different lifetimes: a WebSocket connection authenticates once and reuses the
resulting `AuthContext` for every subsequent frame on that socket, while the
ingestion pipeline needs one uniform "who is submitting this event, over
which transport" value regardless of whether that event arrived over
WebSocket or HTTP `POST /events`. `IngestAuth::Nip42` is constructed by
copying the connection's already-established `AuthContext` fields (plus the
connection id) at the moment an `EVENT` message reaches ingestion;
`IngestAuth::Http` is constructed directly at the HTTP bridge handler, after
NIP-98 verification and relay-membership enforcement succeed.

**What it is not.** An authentication context is not a JWT, bearer token, or
server-side session -- `buzz-auth`'s own module documentation states this as a
design invariant: no JWT validation, no token management, no IdP runtime
dependency. It also does not decide *which community* a connection belongs
to: that is `TenantContext`, resolved from the connection host before any
frame is read, held as a separate field on `ConnectionState` alongside (not
inside) `auth_state`, and fixed for the connection's whole lifetime
independently of whether or how authentication succeeds.

## Background

Before the shared `ingest_event` pipeline existed, the relay's REST handlers
apparently built their own authenticated-user bookkeeping through a helper
named `extract_auth_context` (a name that survives only as a comment in
`command_executor.rs`, not as a symbol in the current codebase). The command
executor built on top of `ingest_event` now performs the equivalent
user-existence step explicitly rather than relying on that removed helper --
a small trace of how the concept's plumbing has moved over time, from
several REST-handler-local extractions toward the two central shapes
(`AuthContext`, `IngestAuth`) documented here today.

## Use cases

- **Deciding whether an action is permitted.** `AuthContext::has_scope` and
  `IngestAuth::scopes()` are the paths every scope-gated operation consults
  instead of re-deriving permission from the raw signed event.
- **Binding every subsequent action to one proven identity.** Once a
  WebSocket connection reaches `AuthState::Authenticated`, every later
  `EVENT` on that connection is checked against the bound `AuthContext.pubkey`
  (except NIP-17 gift-wrap envelopes, whose outer signer is an ephemeral key
  by design) -- authentication is a standing fact about the connection, not a
  one-time gate.
- **Principal-scoped accounting and policy lookups that must not be spoofed
  by event content.** `IngestAuth::principal_pubkey_bytes()` is the pubkey
  used for accounting and policy decisions, deliberately independent of an
  event's own signer, which matters specifically for gift-wrap envelopes
  where the visible signer is not the accountable principal.
- **Choosing behavior by transport without re-deriving it.**
  `IngestAuth::is_http()` and `IngestAuth::conn_id()` let ingestion-pipeline
  code branch on WebSocket-vs-HTTP origin (e.g. whether a connection id
  exists to notify) without threading a separate transport flag alongside
  the auth value.
- **Agent-acting-for-owner authorization.** `AuthContext.agent_owner_pubkey`
  carries the NIP-OA-proven owner identity when a caller authenticated as an
  agent delegate, so downstream checks (bans, ownership) can consult the
  owner's identity, not only the agent's.

## Comparison: `AuthContext` vs `IngestAuth`

| | `buzz_auth::AuthContext` | `handlers::ingest::IngestAuth` |
|---|---|---|
| Scope of one value | One WebSocket connection, whole lifetime | One event being ingested |
| Transports covered | WebSocket only | WebSocket and HTTP, uniformly |
| Where it lives | Inside `ConnectionState.auth_state`'s `AuthState::Authenticated` variant | Passed as a parameter into `ingest_event` |
| Auth-method field | `auth_method: AuthMethod` (`Nip42`/`Nip98`) | `Http` variant's `auth_method: HttpAuthMethod` (`Nip98`/`DevPubkey`); the `Nip42` variant carries no separate field, since the variant tag itself states the method |
| Owner-delegation field | `agent_owner_pubkey: Option<PublicKey>` | Not carried -- not needed by the ingestion-pipeline consumers that read `IngestAuth` |
| Relationship between the two | -- | Built by copying `AuthContext`'s fields at each WS ingestion call site; no defined type-level conversion exists between them (see the INFERENCE evidence entry above) |

## Related resources

The **`references`** relationship above points to
`architecture-flows-websocket-authentication`, the corpus flow node
documenting the ordered NIP-42 challenge/response interactions that produce
an `AuthContext` in the first place -- this node defines what the concept
*is*; that node documents how one is *obtained*.

## Scope and omissions

**This document covers** what an authentication context is in Buzz, why the
codebase carries it as two related types (`AuthContext`, `IngestAuth`)
instead of one, its principal use cases, and its boundary against `AuthState`,
`TenantContext`, and token/session-based authentication.

**It does not cover, and these are gaps rather than silence:**

- **The mechanics of how an `AuthContext` is produced** (the NIP-42
  challenge/response round trip, its failure modes, and its trust-boundary
  crossings) -- covered by `architecture-flows-websocket-authentication`,
  linked above via `references`.
- **The NIP-98 HTTP Auth verification mechanics themselves**
  (`crates/buzz-auth/src/nip98.rs`) -- that flow's own dedicated corpus node
  does not yet exist; `architecture-flows-websocket-authentication`'s own
  scope section already names this as an open gap it does not cover either.
- **The full `Scope` enum and its per-operation meaning**
  (`crates/buzz-auth/src/scope.rs`) -- a reference-shaped catalogue of scope
  values belongs in a reference-typed node, not in this concept node, per
  `templates/concept.md`'s boundary against `reference`.
- **NIP-29 channel membership and moderation**, which is what actually
  enforces per-channel access in pure-Nostr mode once an authentication
  context exists -- a separate, larger surface, not yet in this corpus.

**Expected but not verified when this node was written:** whether any code
path outside `crates/buzz-relay` and `crates/buzz-auth` constructs or reads
an `AuthContext`/`IngestAuth` value directly (for example, `buzz-acp` or
`buzz-cli` client-side code) was not searched exhaustively; this node
describes the relay-side concept as verified in `buzz-auth` and `buzz-relay`
only.
