---
id: implementation-crates-buzz-auth
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-auth's crate-level doc comment describes it as 'Authentication and authorization for the Buzz relay' with two auth paths -- NIP-42 over WebSocket (challenge/response, client signs kind:22242) and NIP-98 over HTTP (signed kind:27235 event in an Authorization: Nostr header) -- and states three security invariants: AUTH events (kind:22242) are NEVER stored or logged; every successful path produces an AuthContext bound to the connection; there is no JWT validation, token management, or IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "buzz-auth's module tree (declared in lib.rs) is access, error, nip42, nip98, nip98_replay, nip_fi, rate_limit, and scope; crates/buzz-auth has no README.md, unlike buzz-acp, buzz-agent, buzz-cli, buzz-pairing-cli, git-credential-nostr, and git-sign-nostr, which each ship one."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
      - "crates/buzz-acp/README.md"
      - "crates/buzz-agent/README.md"
      - "crates/buzz-cli/README.md"
      - "crates/buzz-pairing-cli/README.md"
      - "crates/git-credential-nostr/README.md"
      - "crates/git-sign-nostr/README.md"
  - statement: "AuthService::verify_auth_event performs pure cryptographic verification of a NIP-42 event (kind, Schnorr signature, challenge match, relay-URL match, +/-60s timestamp window, via verify_nip42_event run inside spawn_blocking) and, in pure Nostr mode, grants the resulting AuthContext every scope in Scope::all_known() -- per-channel access is deferred to NIP-29 membership checks made elsewhere, not enforced by this method."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "nip98.rs's module doc states NIP-98 is stateless HTTP auth (no WebSocket session) whose verification steps are: parse the Authorization: Nostr header as a kind:27235 event, verify the Schnorr signature via buzz_core::verify_event, verify created_at is within +/-60 seconds, verify the [\"u\", <url>] tag matches the expected URL (case-insensitive scheme/host, trailing slash stripped), and verify the method tag; it does not check whether the same event id was already used."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "nip98_replay.rs's module doc states NIP-98 verification is structurally complete but does not check event-id reuse, so replay protection needs shared state; the required shape is Redis-backed atomic set-if-absent with TTL >= 120 seconds, keyed per community via nip98_replay_key, and the crate's own convention is verify-then-mark (marking before verifying would let an attacker who knows a victim's future event id burn their replay-guard slot as a denial-of-service)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "RedisNip98ReplayGuard in crates/buzz-pubsub/src/nip98_replay.rs is the production implementation of buzz-auth's Nip98ReplayGuard trait, and RedisRateLimiter in crates/buzz-pubsub/src/rate_limiter.rs is the production implementation of buzz-auth's RateLimiter trait; rate_limit.rs's own module doc states the Redis-backed implementation 'lives in buzz-relay / buzz-pubsub' and warns the fixed-window algorithm allows up to 2x burst at window boundaries."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-auth/src/rate_limit.rs"
  - statement: "access.rs defines the ChannelAccessChecker trait plus check_read_access, check_write_access, and require_scope so buzz-auth can enforce scope-and-membership access without depending on buzz-db directly; its doc comment states every method must scope by ctx.community() because the channels table's primary key is (community_id, id), so a bare id-only lookup would be a cross-community existence oracle. A grep of the workspace for ChannelAccessChecker found no implementer or caller outside buzz-auth itself (only MockAccessChecker, gated behind the test/test-utils feature, exists)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
  - statement: "Scope::ReposRead and Scope::ReposWrite carry doc comments stating they are only partially enforced today: ReposRead is 'reserved for future use, not currently enforced by git HTTP routes -- those use NIP-98 auth directly'; ReposWrite is 'enforced for kind:30617/30618 events via WebSocket ingest, but NOT enforced by git HTTP push routes (which use NIP-98 + owner check)'; both note full enforcement is deferred to a v2 collaborator model."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
  - statement: "The nip_fi module's own doc comment describes it as 'the closed, provider-neutral contract layer at the root of the NIP-FI dependency graph' (Phase A, PR 1), stating it has no dependency on other NIP-FI PRs and defines no database schema, migration, runtime JWKS fetching, binding resolution, enrollment, or request/proof binding. A grep of crates/buzz-relay/src for nip_fi and FederatedAssertionVerifier found no matches -- this module is not wired into the relay at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip_fi/mod.rs"
  - statement: "buzz-auth's Cargo.toml is declared as a workspace dependency by buzz-relay, buzz-pubsub, and buzz-admin; grepping for buzz_auth:: usage found live call sites in buzz-relay/src (handlers/auth.rs, handlers/event.rs, connection.rs, admission.rs, api/bridge.rs, api/admin/auth.rs, api/admin/mod.rs, api/git/transport.rs, api/invites.rs, api/operator.rs, config.rs, main.rs, and more) and in buzz-pubsub/src (rate_limiter.rs, nip98_replay.rs), but no buzz_auth:: usage in buzz-admin/src -- buzz-admin declares the dependency without a confirmed live call site."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "crates/buzz-relay/src/handlers/auth.rs calls AuthService::verify_auth_event for the NIP-42 WebSocket handshake and reads buzz_auth::AuthMethod::Nip42 when deciding whether to apply the pubkey-allowlist gate; crates/buzz-relay/src/api/bridge.rs, api/admin/auth.rs, and api/git/transport.rs each call buzz_auth::verify_nip98_event for their respective HTTP surfaces."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/admin/auth.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "error.rs's AuthError enum enumerates InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired, Nip98Invalid(String), Nip98Replay, PubkeyMismatch, InsufficientScope{required, have}, ChannelAccessDenied, and Internal(String); its own doc comment states variants are designed to be safe to return to callers and must never include raw token values, database contents, or stack traces."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "Counting #[test] and #[tokio::test] attributes separately per file gives: nip42.rs 8 sync/0 async, lib.rs 1 sync/3 async, nip98.rs 14 sync/0 async, nip98_replay.rs 6 sync/1 async, scope.rs 5 sync/0 async, access.rs 0 sync/5 async, rate_limit.rs 5 sync/1 async, nip_fi/verifier/tests.rs 64 sync/0 async, error.rs 0/0 -- a mix of plain and tokio-async unit tests, all runnable via `just test-unit` with no external infrastructure, in contrast to the ignored, infrastructure-requiring end-to-end tests in buzz-test-client that exercise this crate indirectly over the wire."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-auth/src/lib.rs"
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-auth/src/scope.rs"
      - "crates/buzz-auth/src/access.rs"
      - "crates/buzz-auth/src/rate_limit.rs"
      - "crates/buzz-auth/src/nip_fi/verifier/tests.rs"
      - "crates/buzz-auth/src/error.rs"
  - statement: "The corpus node architecture-flows-websocket-authentication (launchpad/docs/corpus/architecture/flows/websocket-authentication.md) cites crates/buzz-auth/src/nip42.rs, crates/buzz-auth/src/error.rs, and crates/buzz-auth/src/lib.rs directly in its own evidence ledger as the source of its NIP-42 verification claims, so a references edge from this node to that one names real supporting context rather than an incidental link."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs contains a #[tokio::test], #[ignore]-gated conformance test named nip98_replay_seenset_is_shared_and_community_scoped that posts the same NIP-98-signed event twice, wire-only via POST /events with an Authorization: Nostr header, to assert within-community replay rejection and cross-community independence; its doc comment cites crates/buzz-auth/src/nip98_replay.rs:103 and :163 directly as the behavior it targets, and a sibling stub in the same file's membership_allowlist module (archive_in_a_does_not_affect_b) calls pending_lane(\"buzz-auth\", ...) rather than asserting anything, per that file's own documented pending-lane convention. No test in this file, or elsewhere in crates/buzz-test-client/tests, does a literal `use buzz_auth` or `buzz_auth::` crate import."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# buzz-auth: implementation reference

`crates/buzz-auth` is the crate that authenticates and authorizes every Buzz
relay connection. It claims to realize two Nostr specifications directly --
[NIP-42](https://github.com/nostr-protocol/nips/blob/master/42.md)
(`["AUTH", ...]` challenge/response over WebSocket) and
[NIP-98](https://github.com/nostr-protocol/nips/blob/master/98.md)
(signed-event HTTP Auth) -- plus a third, not-yet-integrated federated-identity
contract (`nip_fi`, tracking `docs/nips/NIP-FI.md` and its companion documents).
It also defines the authorization primitives (`Scope`, `ChannelAccessChecker`,
`RateLimiter`, `Nip98ReplayGuard`) that the relay and `buzz-pubsub` build on,
without itself depending on `buzz-db` or holding any database connection.

## Target

- **NIP-42** ("Authentication of clients to relays"), a Nostr Implementation
  Possibility. No corpus node exists for it yet -- it is referenced here by
  its well-known spec name; `crates/buzz-auth/src/nip42.rs`'s module doc
  paraphrases the three-step handshake it implements.
- **NIP-98** ("HTTP Auth"), likewise a Nostr NIP with no corpus node yet,
  paraphrased in `crates/buzz-auth/src/nip98.rs`'s module doc.
- **NIP-FI** (federated identity), documented in this repository at
  `docs/nips/NIP-FI.md` plus `NIP-FI-CONF.md`, `NIP-FI-DELEG.md`,
  `NIP-FI-EDGE.md`, `NIP-FI-LIFECYCLE.md`, and `NIP-FI-MODEL.md`. No corpus
  node exists for it yet either. `crates/buzz-auth/src/nip_fi/mod.rs`
  documents itself as "Phase A, PR 1" of that contract -- the closed,
  provider-neutral verifier layer only, with no runtime JWKS fetch, binding
  resolution, enrollment, or database schema.
- The corpus node `architecture-flows-websocket-authentication` documents the
  NIP-42 round trip end to end (relay + client + this crate together); it is
  not itself the specification, so this node does not `implements` toward it
  -- see *Relationships* below for why `references` is the correct edge
  instead.

None of these targets carries a corpus node id at the time of writing, so no
`implements` edge is declared, per the template's own rule that an edge to a
nonexistent id is a hard validation failure worse than no edge.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `AuthService::verify_auth_event`, `nip42::verify_nip42_event`, `nip42::generate_challenge` (`src/lib.rs`, `src/nip42.rs`) | NIP-42 challenge/response | Pure cryptographic check -- kind, Schnorr signature, challenge match, relay-URL match (with localhost/trailing-slash normalization), +/-60s timestamp window. No DB or network call. |
| `nip98::verify_nip98_event` (`src/nip98.rs`) | NIP-98 HTTP Auth | Parses the `Authorization: Nostr` header, verifies kind:27235, signature, timestamp window, `u` tag, method, and optional body hash. Stateless -- does not itself detect a replayed event id. |
| `Nip98ReplayGuard` trait + `nip98_replay_key`/`nip98_replay_key_for_scope` (`src/nip98_replay.rs`); implemented in production by `RedisNip98ReplayGuard` (`crates/buzz-pubsub/src/nip98_replay.rs`) | The replay-protection half of NIP-98 that `verify_nip98_event` deliberately leaves out | Verify-then-mark ordering; community-scoped Redis key, TTL >= 120s. |
| `RateLimiter` trait, `LimitType`, `RateLimitConfig`, `RateLimitResult` (`src/rate_limit.rs`); implemented in production by `RedisRateLimiter` (`crates/buzz-pubsub/src/rate_limiter.rs`) | Per-connection/per-IP rate limiting | Fixed-window counter; the module doc itself flags up to 2x burst at window boundaries as a known limitation. |
| `Scope` enum, `parse_scopes`, `Scope::all_known`/`all_non_admin` (`src/scope.rs`) | Authorization scopes granted to an authenticated connection | In pure-Nostr mode every NIP-42-authenticated connection is granted `all_known()`; `ReposRead`/`ReposWrite` are declared but only partially enforced today (see *Divergences*). |
| `ChannelAccessChecker` trait, `check_read_access`, `check_write_access`, `require_scope` (`src/access.rs`) | Scope-plus-membership channel access checking, decoupled from `buzz-db` | No production implementer exists in this workspace at the recorded revision (see *Divergences*); only `MockAccessChecker`, gated behind `#[cfg(any(test, feature = "test-utils"))]`. |
| `AuthError` (`src/error.rs`) | The safe-to-return error surface for every path above | Ten variants; doc comment states raw token values, DB contents, and stack traces must never appear in a message. |
| `nip_fi` module (`src/nip_fi/{mod,assertion,config,denial,verifier}.rs`) | The closed verifier/contract layer of NIP-FI, Phase A only | Present in the crate but not called from `buzz-relay` at the recorded revision -- see *Scope and omissions*; deliberately not detailed row-by-row here (atomicity -- a large, separate concept). |

## Divergences

Two real, verified divergences between what the crate defines and what the
rest of the workspace actually uses, found by grepping for each symbol's
callers/implementers outside `buzz-auth` itself -- not drift nobody noticed,
but gaps the code's own comments already name:

1. **`ChannelAccessChecker` and its helpers are unused.** `access.rs` exists,
   is exported from `lib.rs`, and is exercised by `buzz-auth`'s own unit
   tests via `MockAccessChecker` -- but no crate in this workspace implements
   the trait for real, and `check_read_access`/`check_write_access` have no
   caller outside `access.rs` itself. Per-channel access is instead enforced
   today through NIP-29 membership checks elsewhere in `buzz-relay`, exactly
   as `AuthService::verify_auth_event`'s own comment says ("Per-channel
   access is enforced by the relay's membership checks (NIP-29)"). This
   trait reads as forward-looking infrastructure for a finer-grained access
   model that has not been wired in yet, not as an abandoned dead end --
   this node does not judge which.
2. **`Scope::ReposRead`/`ReposWrite` are partially enforced.** `ReposWrite`
   is enforced for `kind:30617`/`30618` events over WebSocket ingest but not
   by the git HTTP push routes (NIP-98 + owner check instead); `ReposRead`
   is not enforced by git HTTP routes at all. Both gaps are stated directly
   in the scope's own doc comments as deferred to a "v2 collaborator model,"
   so this is a documented, accepted gap rather than silent drift -- but it
   is still a real divergence between "this scope exists" and "this scope is
   checked everywhere its name implies."

No other divergence was found between the NIP-42 and NIP-98 verification
logic itself and the two specifications' commonly known requirements, based
on the checks enumerated in *Implementation surface* above; a claim of full
protocol-level conformance would require line-by-line comparison against the
NIP-42/NIP-98 spec text, which this node's evidence does not extend to (see
*Scope and omissions*).

## Verification

- **Unit tests, in-crate:** `nip42.rs` (8 tests: challenge shape/uniqueness,
  valid event, wrong challenge/kind/relay, expiry, localhost and
  trailing-slash normalization), `lib.rs` (4 tests, including
  `AuthService::verify_auth_event`'s happy path and two rejection cases),
  `nip98.rs` (14 tests), `nip98_replay.rs` (7 tests), `scope.rs` (5 tests),
  `access.rs` (5 tests), `rate_limit.rs` (6 tests), and
  `nip_fi/verifier/tests.rs` (64 tests) -- all runnable via `just test-unit`
  with no external infrastructure.
- **End-to-end, via `architecture-flows-websocket-authentication`:** that
  node names `test_connect_and_authenticate`, `test_unauthenticated_rejected`,
  `test_auth_event_kind_rejected`, and `test_pubkey_mismatch_rejected` in
  `crates/buzz-test-client/tests/e2e_relay.rs` as representative end-to-end
  NIP-42 coverage; this node does not re-derive that list, only points at it.
- **NIP-98 replay, wire-level:** `nip98_replay_seenset_is_shared_and_community_scoped`
  in `crates/buzz-test-client/tests/conformance_multitenant.rs` is a
  `#[tokio::test]`, `#[ignore]`-gated conformance test that posts the same
  NIP-98-signed event twice within one community (expecting the second
  attempt to be rejected as a replay) and once each to two different
  communities (expecting no cross-community leak), driving the seen-set that
  `nip98_replay.rs` defines and `RedisNip98ReplayGuard` implements entirely
  from the wire (`POST /events` with `Authorization: Nostr ...`), never by
  importing the `buzz-auth` crate. Its doc comment cites
  `crates/buzz-auth/src/nip98_replay.rs:103` and `:163` directly as the
  behavior under test. No test in this file or elsewhere in
  `crates/buzz-test-client/tests` does a literal `use buzz_auth` /
  `buzz_auth::` crate import -- every case exercises this crate only
  indirectly, over the wire.
- **A second, unfinished case in the same file is a stub, not coverage:**
  `archive_in_a_does_not_affect_b` (same file, `membership_allowlist` module)
  calls `pending_lane("buzz-auth", ...)`, which the file's own convention
  marks as a named-but-not-yet-implemented obligation lane, not an assertion
  that runs.
- **`nip_fi`'s 64 tests are the only verification found for that module** --
  no integration or end-to-end coverage exists because nothing in this
  workspace calls it yet.

## Relationships

- references: `architecture-flows-websocket-authentication` -- that node's
  own evidence ledger cites `crates/buzz-auth/src/nip42.rs`,
  `crates/buzz-auth/src/error.rs`, and `crates/buzz-auth/src/lib.rs`
  directly as the source of its NIP-42 claims, so this crate is real
  supporting context for that flow, not an incidental mention. `references`
  is the correct edge (per `relationships.schema.json`: "source cites target
  as supporting context; no ownership or currency dependency implied") --
  not `implements`, because this node's target is the crate's realization of
  external specifications (NIP-42/NIP-98/NIP-FI), none of which are corpus
  nodes yet, and the flow node is not one of those specifications either.
- No `part-of` edge: no broader `implementation`-typed node (for example, a
  crate-of-crates "relay" implementation-reference) is merged on
  `origin/launchpad` at the recorded revision for this node to sit under.
- No `implements` edge: NIP-42, NIP-98, and NIP-FI have no corpus node id at
  the recorded revision. Declaring one against a nonexistent id is a hard
  validation failure, not a soft placeholder, per the template and
  `AGENTS.md`.

## Scope and omissions

**This node covers** what `buzz-auth` is responsible for (NIP-42 WebSocket
auth, NIP-98 HTTP auth plus its replay guard, rate limiting, scope
definitions, and a not-yet-integrated NIP-FI contract layer), its public
entry points, its important dependencies (`buzz-core` for event
verification, `jsonwebtoken`/`sha2`/`rand`/`hex` for the crypto and
token-shape primitives NIP-FI's assertion verifier needs), representative
tests, and where it plugs into the wider relay and `buzz-pubsub`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-42 flow's full step-by-step mechanics, connection state machine, ban/allowlist/membership gates, and failure table | `architecture-flows-websocket-authentication` (already merged; this node references it rather than duplicating it) |
| The NIP-98 HTTP Auth flow's own step-by-step mechanics as a corpus node | Not yet in this corpus -- `websocket-authentication.md`'s own *Scope and omissions* names this same gap |
| `nip_fi`'s internal contracts (`AssertionPolicyId`, `TransportContractId`, `FederatedAssertionVerifier`, `DenialClass`, issuer policy/config, key sources) | Not detailed here, deliberately -- a large, currently-unwired subsystem with its own 64-test verifier suite; documenting it in full is a second, independently maintainable concept per the corpus's atomicity rule, and is better done once it is actually called from `buzz-relay` |
| Line-by-line conformance of `verify_nip42_event`/`verify_nip98_event` against the published NIP-42/NIP-98 spec text | Not verified here -- this node compared the code's own stated checks against what it does, not against the external spec documents word for word |
| Whether `buzz-admin`'s declared `buzz-auth` dependency (Cargo.toml) is dead weight or reached through a path this task's grep missed (e.g. a re-export, macro, or build script) | Not resolved -- reported honestly as "declared but no confirmed call site found," not asserted either way |
| Production Postgres/Redis topology, and whether `BUZZ_AUDIT_ENABLED`/community-scoped configuration affects any of this crate's behavior | `architecture-containers-postgres` and future Redis/relay container nodes |

**Expected but not verified when this node was written:**

- **Whether `docs/nips/NIP-FI*.md` will themselves become corpus nodes**, and
  if so under what id -- not decided here; this node names the real paths in
  *Target* instead of inventing an edge.
- **Whether `buzz-admin`'s `buzz-auth` dependency is genuinely unused** or
  reached by a mechanism this task's `grep buzz_auth::` search does not
  catch (for example, a re-exported macro) was not resolved beyond the grep
  itself.
