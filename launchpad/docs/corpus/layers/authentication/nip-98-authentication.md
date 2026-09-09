---
id: layers-authentication-nip-98-authentication
type: layers
status: draft
origin: upstream
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Kind 27235 is Buzz's KIND_HTTP_AUTH constant, documented in the kind registry as 'NIP-98: HTTP auth event (used in nip98.rs, not stored)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-auth's verify_nip98_event(event_json, expected_url, expected_method, body) performs, in order: (1) parse the event JSON, (2) reject any kind other than 27235, (3) verify the Schnorr signature and event-id hash via buzz_core::verify_event, (4) reject a created_at more than a fixed TIMESTAMP_TOLERANCE_SECS (60 seconds) away from server time, (5) require a single-letter `u` tag whose normalized value matches the normalized expected_url, (6) require a `method` tag matching expected_method case-insensitively, and (7) if a `payload` tag is present and a request body was supplied, require the tag's hex value to equal the body's SHA-256 hash; on success it returns the event's pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "verify_nip98_event's normalize_url helper lowercases scheme and host and strips a trailing slash from the path, but deliberately does not alias loopback hosts: localhost, 127.0.0.1 and ::1 are treated as three distinct hosts, a property exercised directly by the loopback_aliases_are_distinct_hosts unit test."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "A NIP-98 credential is carried as an HTTP request header of the form `Authorization: Nostr <base64(JSON-serialized kind:27235 event)>`; buzz-relay's verify_bridge_auth_with_options decodes and verifies this header for the generic Nostr HTTP bridge (POST /events, /query, /count)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "verify_bridge_auth_with_options falls back to an unsigned `X-Pubkey` header only when its require_auth_token parameter is false (a dev-mode path); that fallback returns a zero event id, so it carries no NIP-98 replay concern."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Git smart HTTP (crates/buzz-relay/src/api/git/transport.rs) authenticates each request through the same verify_nip98_event, but its inline comments state two deliberate deviations from the generic bridge path: the event's own `method` tag is compared against itself rather than the request's real HTTP method, because git's credential helper signs once with GET and reuses the token for the POST that follows, and event-id replay dedup is intentionally not applied to git routes, because the same credential-helper token is reused across the info_refs GET and the following upload-pack/receive-pack POST within one git operation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The same git/transport.rs comments state that, with the method check and replay dedup relaxed for git routes, the remaining security properties are the ±60-second timestamp window, the request URL being locked into the signed `u` tag, HTTPS in production, and the repository's pre-receive hook enforcing push authorization separately."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "buzz-cli's sign_nip98 helper is a client-side NIP-98 signer: it builds a kind:27235 event with `u` (full request URL), `method`, and — when a body is supplied — `payload` (hex SHA-256 of the body) tags, plus a client-generated `nonce` tag documented as preventing replay rejection between rapid-fire requests that would otherwise share an identical signed tuple; verify_nip98_event does not read or require this `nonce` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "NIP-98 verification is structurally complete but stateless about repetition: buzz-auth's own nip98_replay.rs module states directly that verify_nip98_event does not check whether an event id has already been used, and that replay protection requires the separate Nip98ReplayGuard trait, backed in production by a shared, community-scoped Redis seen-set using an atomic set-if-absent operation."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "Nip98ReplayGuard's contract requires marking to happen only after verification succeeds ('verify first, then mark'), requires callers to fail closed (reject the request) on a guard error such as Redis being unreachable, and fixes DEFAULT_REPLAY_TTL_SECS at 120 seconds as a floor (twice the ±60s timestamp tolerance) and MAX_REPLAY_TTL_SECS at 3600 seconds as a ceiling that implementations must clamp down to."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "Buzz's media/Blossom upload and download endpoints authenticate with a structurally similar but distinct event: verify_blossom_auth_event_for_verb checks a kind:24242 event's Schnorr signature, its `t` verb tag, an `expiration` tag in the future, a `created_at` in the past, and (when present) that the request's serving domain appears in a `server` tag — this is not a NIP-98 kind:27235 event and is not verified by verify_nip98_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "docs/multi-tenant-conformance.md's per-surface table records that, for the generic API/media/git HTTP surfaces, host-derived community binding depends on the NIP-98 `u` tag's URL host agreeing with the request's resolved community (`req.community`), alongside the token's own stamped community for API tokens and the Blossom auth event's host binding for media."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "WebSocket connections authenticate through a separate mechanism, NIP-42 (kind:22242, handled by extract_auth_tag_json and the AUTH message handler in crates/buzz-relay/src/handlers/auth.rs), not NIP-98; the corpus already documents that flow as architecture-flows-websocket-authentication."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# NIP-98 Authentication

A short reference for how Buzz authenticates plain HTTP requests without a
WebSocket session, using the Nostr NIP-98 HTTP Auth event.

## Definition

**NIP-98 HTTP Auth is the stateless, per-request signed Nostr event (kind
27235, Buzz's `KIND_HTTP_AUTH`) that Buzz's relay verifies to authenticate an
HTTP request.** The client signs a short-lived kind:27235 event carrying the
exact request URL (`u` tag), the HTTP method (`method` tag), and optionally a
SHA-256 hash of the request body (`payload` tag), then sends it as an
`Authorization: Nostr <base64(JSON event)>` header. `verify_nip98_event` in
`crates/buzz-auth/src/nip98.rs` is the one function that performs this
check: it confirms the kind, the Schnorr signature and event-id hash, a
±60-second timestamp window, the `u` and `method` tags against the actual
request, and the optional body-hash tag — returning the signer's public key
on success.

**What it is not.** It is not a session or a cookie: a fresh event must be
signed for (in general) every request, since the `u` tag binds the signature
to one exact URL and the timestamp window is only ±60 seconds. It is not the
mechanism WebSocket connections use — those authenticate with NIP-42
(kind:22242), a separate challenge/response flow documented in the corpus as
`architecture-flows-websocket-authentication`. And it is not the event Buzz's
own Blossom media endpoints check: those verify a structurally similar but
distinct kind:24242 event (`verify_blossom_auth_event_for_verb`), not a
kind:27235 NIP-98 event.

```mermaid
sequenceDiagram
    participant Client
    participant Relay as Buzz relay (HTTP)

    Client->>Client: Build kind:27235 event<br/>u=request URL, method=HTTP verb,<br/>payload=sha256(body)?
    Client->>Client: Sign with Nostr keypair
    Client->>Relay: Authorization: Nostr base64(event JSON)
    Relay->>Relay: verify_nip98_event(json, url, method, body)
    alt kind/signature/timestamp/u/method/payload all check out
        Relay-->>Client: 200 — request handled as event.pubkey
    else any check fails
        Relay-->>Client: 401 Unauthorized
    end
```

## Use cases

A reader needs this node when they are implementing or reviewing an HTTP
client or server path that authenticates with a signed Nostr event instead
of a WebSocket session:

- **The generic Nostr HTTP bridge** — `POST /events`, `POST /query`,
  `POST /count` — verified by `verify_bridge_auth_with_options` in
  `crates/buzz-relay/src/api/bridge.rs`. In non-production configurations
  where `require_auth_token` is false, an unsigned `X-Pubkey` header may
  substitute for a NIP-98 event.
- **Git smart HTTP** (clone/push through the git credential helper) — also
  verified through `verify_nip98_event`, but with the `method` check and
  event-id replay dedup deliberately relaxed, because the credential
  helper signs one token with `GET` and reuses it for the following `POST`.
  See *Scope and omissions* for what still secures that path.
- **Writing a client that calls either surface** — `crates/buzz-cli/src/client.rs`'s
  `sign_nip98` is a working example of building the `u`/`method`/`payload`
  tags client-side (plus a `nonce` tag the server does not require, used to
  keep otherwise-identical rapid requests from colliding).

## Comparison

| Mechanism | Kind | Transport | Where verified |
|---|---|---|---|
| NIP-98 HTTP Auth (this node) | 27235 | Plain HTTP, one event per request | `crates/buzz-auth/src/nip98.rs` |
| NIP-42 AUTH | 22242 | WebSocket challenge/response, one event per connection | `crates/buzz-relay/src/handlers/auth.rs` (see `architecture-flows-websocket-authentication`) |
| Blossom media auth | 24242 | Plain HTTP (media upload/get) | `crates/buzz-media/src/auth.rs` |
| Dev-mode `X-Pubkey` | n/a — unsigned header | Plain HTTP, only when `require_auth_token` is false | `crates/buzz-relay/src/api/bridge.rs` |

## Replay protection is a separate concern

`verify_nip98_event` itself does not check whether an event id has been seen
before — `crates/buzz-auth/src/nip98_replay.rs` states this directly and
supplies the `Nip98ReplayGuard` trait instead: an atomic, community-scoped
Redis set-if-absent seen-set, marked only *after* verification succeeds, with
a 120-second TTL floor (twice the verifier's ±60s window) and a 3600-second
ceiling. A guard error (e.g. Redis unreachable) must fail closed — the
request is rejected, not admitted. Git routes are the one documented
exception: they do not apply this dedup at all, relying instead on the
timestamp window, URL locking, HTTPS, and the repository's pre-receive hook
(see *Use cases* above).

## Multi-tenant host binding

Under multi-tenant deployment, the `u` tag's URL host is one of the
mechanisms the relay's community-isolation boundary depends on:
`docs/multi-tenant-conformance.md`'s per-surface table records that the
generic HTTP bridge, git hosting, and media all require the NIP-98 (or
Blossom) auth event's URL host to agree with the request's host-derived
community. This is also why `normalize_url` treats `localhost`, `127.0.0.1`
and `::1` as three distinct hosts rather than aliasing them — collapsing them
would let an event signed for one host authenticate a request resolved to a
different community.

## Scope and omissions

**This document covers** the NIP-98 event shape and the mechanics
`verify_nip98_event` checks, the two HTTP surfaces in this repository that
use it (the generic bridge and git smart HTTP) and how each differs, its
relationship to the separate replay-protection layer, and its boundary
against NIP-42 (WebSocket), Blossom's kind:24242 auth, and the unsigned
dev-mode `X-Pubkey` fallback.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| The general "bearer token" authentication pattern this event is one instance of | A sibling task (issue #1027) is scoped to that angle; at the time this node was written, `launchpad/docs/corpus/layers/authentication/bearer-token.md` did not yet exist on disk, so no `relationships` edge is added — a future edit should add one once that node merges. |
| The full NIP-42 WebSocket AUTH flow | Owned by the existing `architecture-flows-websocket-authentication` node, linked above via `references` rather than duplicated here. |
| Blossom's kind:24242 auth event in detail | Only contrasted here (see *Comparison*); its own verification rules belong to a node scoped to media/Blossom auth. |
| Rate limiting and admission control applied after authentication (`enforce_http_admission` in `crates/buzz-relay/src/api/bridge.rs`) | A separate concern layered on top of, not part of, NIP-98 verification itself. |

**Expected but not verified when this node was written:**

- Every call site of `sign_nip98`-shaped client code was not enumerated —
  `crates/buzz-cli/src/client.rs` was opened and confirmed as one concrete
  client, but whether `crates/buzz-agent/src/auth.rs`, `crates/buzz-acp/src/relay.rs`,
  or `crates/git-credential-nostr/src/lib.rs` construct NIP-98 events through
  the same or different code paths was not individually checked line by
  line; `git-credential-nostr/src/lib.rs`'s own module comment states it
  signs a kind:27235 event, which is consistent with this node's claims but
  was not traced further.
- Whether any deployment currently runs with `require_auth_token = false`
  (enabling the dev-mode `X-Pubkey` fallback) in a reachable environment was
  not checked; this node only establishes that the code path exists.
