---
id: interfaces-http-git
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "`git_router` in transport.rs registers exactly three client-facing routes: `GET /git/{owner}/{repo}/info/refs` (handled by `info_refs`), `POST /git/{owner}/{repo}/git-upload-pack` (handled by `upload_pack`), and `POST /git/{owner}/{repo}/git-receive-pack` (handled by `receive_pack`), each layered under a `RequestBodyLimitLayer` bound to `state.config.git_max_pack_bytes`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`git_policy_router` in `mod.rs` registers a fourth route, `POST /internal/git/policy` (handled by `policy::hook_policy_check`), mounted behind `require_localhost` middleware that rejects any request whose connection is not from a loopback address; this is the pre-receive hook's internal callback, not a route a git client ever calls directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "transport.rs's own module doc comment states the auth model in one line: \"Auth: NIP-98 on all routes (clone + push). No public repos for v1.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:1-9"
  - statement: "`GitAuth`, an axum `FromRequestParts` extractor, is required on every client-facing route; a request with no `Authorization` header, or one not prefixed `Nostr `, or not valid base64/UTF-8 JSON, is rejected with 401 and a `WWW-Authenticate: Nostr realm=\"buzz\", method=\"<method>\"` header before any repository work starts."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The request's `Host` header is bound to a server-resolved tenant via `crate::tenant::bind_community` before the signed event's `u` (URL) tag is checked, so the URL-scoping half of NIP-98 verification is anchored to a server-resolved community, never to a client-supplied `Host` or `config.relay_url`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "NIP-98 event verification itself — kind 27235, Schnorr signature, a ±60-second timestamp window, and the `u`/`method` tag checks — is delegated to `buzz_auth::nip98::verify_nip98_event`, whose own module doc comment enumerates these eight verification steps; the call passes `body: None` because streaming pack data cannot be buffered to hash against an optional `payload` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:1-60"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The HTTP method is deliberately not checked against the live request method: git's credential protocol signs one NIP-98 event with `method=GET` for the initial `info/refs` request and reuses the same token for the following POST, so `GitAuth` passes the event's own `method` tag value back into `verify_nip98_event`, making that check tautological by design rather than a security boundary — the code comments this explicitly as \"SECURITY: method intentionally not verified for git routes.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "NIP-98 event-ID replay is intentionally not deduplicated on git routes, for the same reason: one signed token is reused across the `info/refs` GET and the following pack-transfer POST within a push/clone session, and rejecting a repeated event ID would break that normal sequence."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "After NIP-98 verification, `GitAuth` additionally enforces a NIP-43 relay-membership gate via `enforce_relay_membership`, reading the caller's NIP-OA auth-tag attestation from either a tag on the signed event or an `x-auth-tag` header (git's credential protocol has no way to carry a standalone header from a plain `git push`/`git clone`); a non-member is denied 403 \"restricted: not a relay member\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Every git HTTP request additionally re-reads a durable moderation-ban state per request (`deny_banned_git_principal`), cascading a ban from a proven NIP-OA owner down to the agent pubkey making the request, because git traffic runs outside the WebSocket session lifecycle where a ban would otherwise be caught at connect time; a restriction-store outage fails closed with 503 rather than being reported as an allow or a false 403 ban."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`validate_repo_id` requires the `{owner}` path segment to be exactly 64 lowercase hex characters and the `{repo}` segment (after stripping an optional trailing `.git`) to be a bounded `[a-zA-Z0-9._-]{1,64}` token with no leading dot and no `..`; either malformed segment is rejected with 400 before any hydration or subprocess work begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Reads (`info_refs`, `upload_pack`) are additionally gated by `authorize_git_read`, which requires the caller's *current active* membership in the repo's bound channel — resolved fresh from the repo's live kind:30617 announcement's `buzz-channel` tag on every request, not cached — and fails closed (denying even the announcing owner) on a missing announcement, an unbound or malformed channel binding, or an unrecognized/absent membership role; every denial returns a generic 404 \"repository not found\" so membership cannot be probed through the git endpoints, with one documented carve-out: a never-bound repo read by its own announcing author gets a 404 whose body names the `buzz repos bind` remediation command, because the author already knows the repo exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Push-time ref-level authorization is not enforced inline in `receive_pack`; it is delegated to a pre-receive hook that calls back to the loopback-only `/internal/git/policy` endpoint, which resolves channel role, protection-rule overrides, and channel archival state independently of anything the git request itself asserts. That callback's HMAC binding, channel-role matrix, and ref-update classification are `architecture-flows-git-push`'s own subject, not restated here — see *Boundary*."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "The status-code catalog observable at this interface's boundary is: 400 (malformed owner/repo/service parameter), 401 (missing/malformed/invalid NIP-98 auth), 403 (not a relay member, or banned), 404 (repository not found — including every read-gate denial and a genuinely absent repo, generically, by design), 409 (push lost the object-store CAS race — `architecture-flows-git-push`'s subject), 413 (`info/refs` advertisement or a hydrated repo exceeds configured resource limits), 500 (git subprocess or hydration failure), 503 with `Retry-After: 5` (the bounded `git_semaphore` has no spare permit)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Four independent byte-size limits bound request/response bodies at this interface: the router-level `RequestBodyLimitLayer` at `state.config.git_max_pack_bytes` (compressed bytes), a 64 MiB cap on the *decoded* `upload-pack` want/have negotiation body (`UPLOAD_PACK_MAX_DECODED_BYTES`, guarding against a gzip bomb since the router layer only bounds compressed size), a 4 MiB cap on subprocess-path `info/refs` output (`INFO_REFS_MAX_OUTPUT_BYTES`), and a 1 MiB cap on `receive-pack` status output (`RECEIVE_PACK_MAX_OUTPUT_BYTES`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "A gzip-`Content-Encoding` request body is transparently inflated before being piped to the `git` subprocess's stdin (git's smart-HTTP client compresses want/have negotiation once it grows large enough); any other non-identity encoding is passed through unchanged rather than rejected, and the subprocess surfaces a real mismatch as an in-band protocol error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "For a branches-only repository (no `refs/tags/*`, and `HEAD` resolving to an advertised ref), the `GET .../info/refs?service=git-upload-pack` response is built directly from the published manifest (`build_upload_pack_advertisement`) — no hydrate, no subprocess, no `git_semaphore` permit; any repo with a tag, or an ineligible/unverifiable manifest, falls back to hydrating an ephemeral workspace and shelling out to `git upload-pack --advertise-refs`, which is also the only path taken for a `git-receive-pack` advertisement (a different, non-reproduced capability set)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The fast-path advertisement's capability offer is a fixed, conservative string including `object-format=<sha1|sha256>` (derived from the stored oid's hex width, never hardcoded) and `agent=buzz-git`; the client re-negotiates the real capability set against the actual `upload-pack` subprocess in its follow-up POST, so this offer only needs to be a safe subset of what that subprocess supports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "kind:27235 is the Nostr NIP-98 HTTP-Auth event kind this interface's bearer token carries; kind:30617 is the repo announcement event whose `buzz-channel` tag both the read gate and the push policy resolve; kind:30618 is the relay-signed ref-state event a successful push derives — all three are `buzz-core`'s own kind constants, not invented for this document."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The client-side credential helper, `git-credential-nostr`, answers git's credential-protocol prompt by building and signing a NIP-98 kind:27235 event over the request URL and method with the user's Nostr key, then handing git the base64 token to retry with `Authorization: Nostr <token>`; its own README states it requires git 2.46+ for the credential protocol's `authtype` capability."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
  - statement: "Signing git commit/tag *objects* with a Nostr key (NIP-GS, via the separate `git-sign-nostr` program and git's `gpg.x509.program` signing-backend interface) is an independent, optional concern from this interface's transport authentication: NIP-98 authenticates the HTTP request carrying a push or clone, while NIP-GS is a signature over the git objects themselves that this interface neither requires nor inspects. NIP-GS's own specification states it \"does not require relay changes\" and defines no new git transport."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "docs/nips/NIP-GS.md"
  - statement: "`launchpad/docs/corpus/architecture/flows/git-push.md` (id `architecture-flows-git-push`) is a merged corpus node, present in this worktree's `origin/launchpad`-based checkout at the recorded revision, that documents the full push authentication/authorization/CAS-publish/derived-event flow this interface's `git-receive-pack` route triggers, in the ordered-interaction depth this node deliberately does not restate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "`crates/buzz-test-client/tests/e2e_git.rs` exercises this interface end-to-end: `git_clone_push_fetch_force_roundtrip` drives a real clone, two pushes, a force-push, and a tag push against a live relay and MinIO; `git_concurrent_push_one_wins_and_repo_recovers` races 8 concurrent pushers at the same branch tip. Both are marked `#[ignore = \"requires live relay + MinIO + git\"]`, so they were read as source, not executed, while authoring this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "This interface has no explicit version parameter, path segment, or negotiated protocol-version field beyond git's own smart-HTTP capability advertisement (`multi_ack`, `thin-pack`, `side-band`, `object-format=...`, `agent=buzz-git`, and the subprocess's own re-negotiated set); compatibility is therefore governed by that capability string plus the fixed three-route table, not by a Buzz-specific version scheme."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
    confidence: 0.8
  - statement: "There is no per-repo lock serializing concurrent pushes to the same repository; each push hydrates an independent ephemeral workspace and the object-store compare-and-swap at publish time is the sole ordering/idempotency mechanism, so a losing concurrent push observes 409 and its work is discarded rather than merged or queued. The full mechanism (parent-state snapshot, CAS predicate, derived kind:30618 emission) is `architecture-flows-git-push`'s subject."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "`docs/git-on-object-storage.md` is a formal specification (`## Protocol` §Read, §Push; `## Safety Theorems`) for the read/push protocol this interface's `info_refs`/`upload_pack`/`receive_pack` handlers implement, and `receive_pack`'s own doc comment cites it directly by name (\"Push flow (spec §Push steps 1-8)\"), making it the authoritative machine/spec representation for this interface's read and push behavior — not this node's own restatement of the wire format."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-relay/src/api/git/transport.rs"
---

# Git smart-HTTP transport: interface

The boundary between a git client (`git`, via a standard `git clone`/`fetch`/
`push` invocation configured with the `git-credential-nostr` credential
helper) and the Buzz relay's git-hosting subsystem, crossed over plain HTTP
using git's own Smart HTTP protocol, authenticated per-request by a NIP-98
Nostr signed-event bearer token rather than a username/password or OAuth
flow. The relay speaks git's wire protocol by hydrating an ephemeral
workspace from an object-store-backed manifest and, on the dominant clone
path, by serving the ref advertisement directly from that manifest with no
subprocess involved at all.

**Authoritative machine/spec representation:** `docs/git-on-object-storage.md`
is a formal specification for the read and push protocol these handlers
implement (`## Protocol` §Read, §Push, plus its `## Safety Theorems`);
`receive_pack`'s own doc comment cites it directly by section number. This
node points at that specification rather than re-deriving its protocol
steps.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `GET /git/{owner}/{repo}/info/refs?service=git-upload-pack\|git-receive-pack` | `crates/buzz-relay/src/api/git/transport.rs::info_refs` | Ref advertisement — the first step of both clone and push negotiation. |
| `POST /git/{owner}/{repo}/git-upload-pack` | `crates/buzz-relay/src/api/git/transport.rs::upload_pack` | Clone/fetch: client sends wants/haves, relay streams pack data back. |
| `POST /git/{owner}/{repo}/git-receive-pack` | `crates/buzz-relay/src/api/git/transport.rs::receive_pack` | Push: client sends ref updates and pack data; relay applies, authorizes, and publishes. |
| `POST /internal/git/policy` (loopback-only; not client-facing) | `crates/buzz-relay/src/api/git/policy.rs::hook_policy_check`, mounted by `crates/buzz-relay/src/api/git/mod.rs::git_policy_router` | The pre-receive hook's internal authorization callback for one push — see *Boundary*. |

## Contract and stability

- **Auth is mandatory on every client-facing route; there are no public
  repos in this version.** A missing or malformed `Authorization` header is
  401 with `WWW-Authenticate: Nostr realm="buzz", method="<method>"`.
- **The signed URL is checked against a server-resolved tenant, never a
  client-supplied `Host`.** A client cannot authenticate against one
  community's host with a token signed for another's.
- **The HTTP method embedded in the signed event is not compared against
  the live request method**, by design: git signs once with `GET` for
  `info/refs` and reuses that token for the following POST. This is
  documented in-line in `transport.rs` as a deliberate, not accidental,
  relaxation.
- **NIP-98 event-ID replay is not deduplicated on these routes**, for the
  same reason — one token spans a GET and a POST in one session.
- **Reads require current, not historical, channel membership**, resolved
  fresh from the repo's live kind:30617 announcement on every request — an
  owner removed from the bound channel loses read access, with no
  repo-owner bypass. Every denial (missing announcement, unbound/broken
  channel binding, non-member, unrecognized role) returns the same generic
  404, except the one documented remediation carve-out for a never-bound
  repo's own announcing author.
- **Push ref-level authorization is not part of this interface's own
  contract** — it is delegated to the pre-receive hook and `/internal/git/policy`,
  whose role/protection-rule matrix and CAS-publish ordering guarantee are
  `architecture-flows-git-push`'s subject (see *Boundary*).
- **The observable status-code catalog** is 400 (malformed
  owner/repo/service), 401 (auth), 403 (membership/ban), 404 (not
  found/read-denied, deliberately generic), 409 (CAS conflict on push —
  covered in depth by `architecture-flows-git-push`), 413 (resource
  limits), 500 (subprocess/hydration failure), 503 with `Retry-After: 5`
  (no spare `git_semaphore` permit).
- **Four independent byte limits** bound what a client can send or
  receive: the router body-limit layer (`git_max_pack_bytes`, compressed),
  a 64 MiB decoded-body cap on upload-pack negotiation, a 4 MiB cap on
  subprocess-path `info/refs` output, and a 1 MiB cap on `receive-pack`
  status output.
- **No explicit interface version.** Compatibility rides on git's own
  smart-HTTP capability negotiation (`multi_ack`, `thin-pack`, `side-band`,
  `object-format=sha1|sha256`, `agent=buzz-git`) plus the fixed three-route
  table, not a Buzz-specific version parameter — see the evidence ledger's
  `INFERENCE` entry.
- **Idempotency/ordering**: no per-repo lock exists; the object-store CAS
  at publish time is the sole serialization point, so a losing concurrent
  push is cleanly discarded (409) rather than merged or queued. The full
  mechanism belongs to `architecture-flows-git-push`.

## Authentication / authorization

1. **Client-side signing** (`git-credential-nostr`): on a 401 challenge,
   git invokes the configured credential helper, which signs a NIP-98
   kind:27235 event over the request URL and method with the user's Nostr
   key and hands git the base64 token. Requires git 2.46+ for the
   credential protocol's `authtype` capability.
2. **Server-side verification** (`GitAuth` in `transport.rs`): tenant
   binding from `Host` first, then `buzz_auth::nip98::verify_nip98_event`
   (kind check, Schnorr signature, ±60s timestamp window, `u`-tag match
   against the server-resolved URL; method check is a no-op by design;
   body hash is skipped because pack data streams and cannot be buffered).
3. **Relay membership (NIP-43)**: the caller's NIP-OA auth-tag attestation,
   carried on the signed event or an `x-auth-tag` header, is checked
   against the target community's membership; failure is 403.
4. **Durable ban re-check**: every request independently re-reads
   moderation-ban state and cascades a ban from a proven NIP-OA owner to
   the requesting agent key, because git traffic bypasses the WebSocket
   connect-time ban check entirely.
5. **Channel-membership read gate** (`authorize_git_read`): reads
   additionally require current active channel membership, resolved from
   the repo's live kind:30617 `buzz-channel` tag — see *Contract and
   stability* above.
6. **Push-time ref authorization** happens outside this interface's own
   request/response cycle, in the pre-receive hook's callback to
   `/internal/git/policy` — see *Boundary*.
7. **Object signing (NIP-GS) is a separate, orthogonal concern.** A commit
   or tag may additionally be signed with a Nostr key via `git-sign-nostr`
   and `git config gpg.x509.program`; this interface neither requires nor
   inspects that signature. NIP-GS's own specification states it defines
   no new git transport and requires no relay changes.

## Boundary

This node does not describe:
- **The pre-receive hook's push-authorization contract** — the
  `/internal/git/policy` HMAC binding, the channel-role/protection-rule
  matrix, ref-update classification (create/fast-forward/non-fast-forward/
  delete), the object-store CAS predicate and conflict handling, and the
  derived kind:30618 emission. All of that is `architecture-flows-git-push`'s
  subject; this node only names that the delegation exists and where it is
  mounted.
- **NIP-GS commit/tag object signing** (`git-sign-nostr`) — an optional,
  independent signature over git objects, not this interface's transport
  authentication. See `crates/git-sign-nostr/README.md` and
  `docs/nips/NIP-GS.md`.
- **A domain-expert, field-by-field parameter catalogue** of every git
  smart-HTTP wire detail (pkt-line framing internals, the exact
  subprocess-fallback decision tree) — those live in `transport.rs` itself
  as the authoritative source; this node names the operations and the
  contract a caller may rely on, not a restatement of the wire format.
- **The object-store CAS algorithm's internals** (pointer format, manifest
  canonicalization, pack/idx storage) — `crates/buzz-relay/src/api/git/{cas_publish,manifest,store}.rs`.

## Relationships

- references: architecture-flows-git-push

## Scope and omissions

**This node covers** the git smart-HTTP interface's client-facing route
table (`info/refs`, `git-upload-pack`, `git-receive-pack`), its NIP-98 +
NIP-43 + ban-cascade authentication/authorization stack, the fail-closed
channel-membership read gate, the observable status-code and byte-limit
contract, the fast-path manifest-served advertisement, the absence of an
explicit version scheme, and the pointer to NIP-GS as an orthogonal signing
concern.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Push ref-level authorization, the CAS publish algorithm, and the derived kind:30618 event | `architecture-flows-git-push` |
| NIP-GS commit/tag object signing | `crates/git-sign-nostr/README.md`, `docs/nips/NIP-GS.md` |
| The object-store CAS internals (pointer format, manifest canonicalization) | `crates/buzz-relay/src/api/git/{cas_publish,manifest,store}.rs` |
| Repo creation from a kind:30617 announcement and channel-binding/provisioning | No merged corpus node yet, per `architecture-flows-git-push`'s own scope table |

**Expected but not verified when this node was written:**
- **Neither e2e test in `e2e_git.rs` was executed.** Both are
  `#[ignore]`-gated behind a live relay, MinIO, and `git`; every claim
  about observable clone/push behavior above a live wire is sourced from
  reading the production code path and the test's assertions, not from a
  passing run.
- **NIP-98's own upstream specification text was not fetched directly**;
  its eight verification steps are sourced from `buzz-auth`'s own module
  doc comment (`crates/buzz-auth/src/nip98.rs`), which states it implements
  that spec, rather than from `nostr-protocol/nips`' primary text.

### Example: a valid clone

1. `git clone https://relay.example.com/git/<owner-64hex>/<repo>.git`
   triggers git's own credential-protocol 401 dance: an unauthenticated
   `GET .../info/refs?service=git-upload-pack` gets 401 with
   `WWW-Authenticate: Nostr ...`, `git-credential-nostr` signs a kind:27235
   event, and git retries with `Authorization: Nostr <token>`.
2. `GitAuth` verifies the token, `authorize_git_read` confirms current
   channel membership, and — for a branches-only repo — `info_refs` serves
   the advertisement straight from the manifest (`build_upload_pack_advertisement`),
   with no hydrate and no subprocess.
3. The client's follow-up `POST .../git-upload-pack` reuses the same
   token; `upload_pack` hydrates an ephemeral workspace and streams pack
   data back.
4. Representative verification: `crates/buzz-test-client/tests/e2e_git.rs::git_clone_push_fetch_force_roundtrip`
   (read, not executed — see *Scope and omissions*).

### Example: a failure — missing authentication

A request to any client-facing route with no `Authorization` header (for
example, a `git clone` run without the `git-credential-nostr` helper
configured, or a raw `curl` against `info/refs`) is rejected by `GitAuth`
before any repository, tenant, or membership work happens: **401**, body
`"missing Authorization header"`, and a `WWW-Authenticate: Nostr
realm="buzz", method="<method>"` response header telling a NIP-98-aware
client how to retry.
