---
id: layers-security-replay-protection
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
  - statement: "verify_nip98_event (NIP-98 HTTP Auth, kind:27235) checks signature, kind, timestamp window, URL, method and optional body hash, but does not check whether the same event id has already been used; nip98_replay.rs's own module documentation states this explicitly and names it a §5 hard gate because an in-process cache would not carry the freshness proof across relay pods under the 'any pod, any connection' architecture."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "The Nip98ReplayGuard trait (crates/buzz-auth/src/nip98_replay.rs) requires an atomic set-if-absent claim per event id, community-scoped via nip98_replay_key (format buzz:{community}:nip98:{event_id_hex}); ttl_secs MUST be clamped up to DEFAULT_REPLAY_TTL_SECS (120, matching the doubled ±60s NIP-98 timestamp tolerance) and down to MAX_REPLAY_TTL_SECS (3600, sized to fit Redis's signed 64-bit EX argument); on Err the caller MUST fail closed (reject) rather than admit the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "The production implementation, RedisNip98ReplayGuard (crates/buzz-pubsub/src/nip98_replay.rs), issues a single Redis SET key 1 NX EX <ttl> per claim: NX makes the operation atomic set-if-absent, Some(\"OK\") means first claim (admit), None means the key already existed (reject as replay), and any other reply or a pool/command error is surfaced as an internal error which the caller in turn treats as fail-closed."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
  - statement: "check_nip98_replay / check_nip98_replay_with_guard (crates/buzz-relay/src/api/bridge.rs) is the single enforcement point: it skips the replay check only for the dev-mode zero-hash X-Pubkey path, otherwise calls try_mark and maps Ok(true) to Ok(()), Ok(false) to 401 'NIP-98: replay detected', and Err(_) to 401 'NIP-98: replay check unavailable' -- an explicit fail-closed mapping, not a default-open one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "check_nip98_replay is called from the generic Nostr HTTP bridge (multiple sites in bridge.rs, covering POST /events and related bridge paths), from crates/buzz-relay/src/api/invites.rs, and from crates/buzz-relay/src/api/workflows.rs (webhook auth) -- every NIP-98-authenticated HTTP surface that isn't the dev-mode X-Pubkey shortcut runs through the same guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/workflows.rs"
  - statement: "AppState.nip98_replay is typed Arc<dyn Nip98ReplayGuard> and is constructed in production as Arc::new(RedisNip98ReplayGuard::new(redis_pool.clone())); the guard is wired once at state construction, not created per-request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "NIP-42 WebSocket Auth (kind:22242) has no equivalent to Nip98ReplayGuard: crates/buzz-auth/src/nip42.rs's verify_nip42_event checks kind, Schnorr signature, that the event's challenge tag equals the expected challenge, that the event's relay tag matches this relay's URL (normalized), and that created_at is within +/-60s -- there is no seen-set lookup and no shared-state call in this function at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "generate_challenge (crates/buzz-auth/src/nip42.rs) produces the NIP-42 challenge as 32 CSPRNG bytes (rand::random), hex-encoded to 64 characters, and a unit test asserts two successive calls return distinct values."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "The challenge is generated fresh per WebSocket connection inside handle_connection (crates/buzz-relay/src/connection.rs), stored as AuthState::Pending { challenge } on that connection's own ConnectionState, and sent as the first frame (['AUTH', '<challenge>']) before the connection is even registered with the connection manager -- the challenge is therefore scoped to one connection's lifetime, not drawn from any shared or predictable pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_auth (crates/buzz-relay/src/handlers/auth.rs) reads the connection's current AuthState before doing any verification work: if it is already Authenticated, the handler replies OK false ('already authenticated') and returns without re-verifying; if it is already Failed, it replies OK false ('authentication already failed') and returns without re-verifying. Only a connection still in AuthState::Pending has its AUTH event actually checked against verify_auth_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "A captured, valid NIP-42 AUTH event cannot be replayed on the connection that produced it (the state-machine guard above rejects any second AUTH once that connection is Authenticated or Failed) and cannot be replayed on a different connection either, because that connection was issued its own independently random challenge and verify_nip42_event requires the event's challenge tag to equal the specific challenge that connection issued -- the captured event's challenge will not match."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
    confidence: 0.85
  - statement: "Blossom kind:24242 media auth (crates/buzz-media/src/auth.rs, BUD-11) uses a third, distinct replay-mitigation shape: it requires an expiration tag in the future and separately bounds created_at to at most max_age_secs in the past (a source comment states this explicitly bounds the replay window even though the expiration tag alone could allow a longer-lived token), but implements no seen-set and no per-connection challenge -- a captured, not-yet-expired Blossom auth event remains valid for any request matching its verb/scope tags until it expires."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/auth.rs"
  - statement: "buzz-push-gateway defines its own, separate replay-prevention tables (push_gateway_delivery_auth_replays, push_gateway_delivery_request_replays), used from crates/buzz-push-gateway/src/postgres.rs, for push-delivery auth between relay pods and the push gateway -- a distinct subsystem and threat model from HTTP/WebSocket client authentication, not documented in depth by this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
      - "crates/buzz-push-gateway/src/postgres.rs"
  - statement: "launchpad/docs/corpus/architecture/flows/websocket-authentication.md (id architecture-flows-websocket-authentication) exists on origin/launchpad and already documents the NIP-42 challenge/response flow end to end; its own Scope and omissions section names NIP-98's 'separate replay-protection mechanism (nip98_replay.rs)' as a gap that 'deserves its own node. Not yet in this corpus' -- the node this task creates fills that named gap."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "launchpad/docs/corpus/layers/authentication/nip-98-authentication.md (id layers-authentication-nip-98-authentication) does not exist on origin/launchpad; it exists only in open, unmerged PR #1795 (issue #1029), so it is not a valid relationships target from this node today."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz PR #1795 (open at authoring time, issue #1029)"
  - statement: "Issue #1173's Definition of done requires: exactly one hand-authored canonical document; schema-valid front matter with typed relationships appropriate to the node; one independently maintainable knowledge node with any second concept filed separately; every substantive claim traceable and FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links to relevant implementation/verification/specification/neighboring nodes without duplicating their content; checked against the recorded revision; passing corpus validation; the invariant stated as one unambiguous property using MUST/MUST NOT only where normative; scope and applicable states/operations explained; enforcement points and observable failure behavior named; and at least one verification/conformance mechanism linked or its absence recorded."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1173 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# Replay Protection

How Buzz prevents a captured, structurally-valid authentication event from
being honored more than once. This node covers the relay's two
protocol-facing authentication surfaces -- NIP-98 HTTP Auth (kind:27235) and
NIP-42 WebSocket Auth (kind:22242) -- which solve the same threat with two
different mechanisms, and names the two related-but-separate mechanisms
elsewhere in the codebase (Blossom kind:24242, the push-gateway delivery
auth tables) that this node does not cover in depth.

## Invariant statement

A signed authentication event that has already been honored to authorize one
request or connection MUST NOT be honored a second time to authorize another.

- **NIP-98 HTTP Auth:** no two accepted HTTP requests within a community may
  share the same `kind:27235` event id inside that event's replay-prevention
  window (at least 120 seconds).
- **NIP-42 WebSocket Auth:** a given `kind:22242` AUTH event can succeed at
  most once, because it is verifiable only against the single, unpredictable
  challenge issued to the one connection that produced it, and a connection
  accepts at most one successful AUTH in its lifetime.

## Scope

**NIP-98.** Binds every HTTP endpoint that authenticates via NIP-98 and calls
`check_nip98_replay`: the generic Nostr HTTP bridge (`POST /events` and
related bridge paths in `bridge.rs`), community invites (`invites.rs`), and
workflow webhook auth (`workflows.rs`). Does not bind the dev-mode `X-Pubkey`
auth shortcut, which carries a zero event-id hash and is explicitly exempted
from the replay check. Only a *structurally valid* NIP-98 event (passed
`verify_nip98_event`) is ever marked in the seen-set -- verification runs
before marking, so a forged or malformed event never consumes a legitimate
event id's slot, and a rejected forgery attempt can be retried indefinitely
without being auto-blocked by the replay layer itself.

**NIP-42.** Binds every WebSocket connection's `AuthState` machine, from
connection setup (`handle_connection` issuing the challenge) through
`handle_auth`'s state-guarded verification to the terminal `Authenticated` or
`Failed` state. The invariant holds at the connection level, not the process
level: it says nothing about two *different* connections independently
authenticating as the same pubkey with two different, freshly-issued
challenges -- that is ordinary re-authentication, not replay.

## Enforcement today

**NIP-98: predicate-enforced, shared state.** `Nip98ReplayGuard::try_mark`
issues an atomic set-if-absent claim (`Redis SET NX EX`) against a
community-scoped key. This is a query-level guard, not a type-system or
purely structural one: nothing in the type system stops a future call site
from authenticating a NIP-98 request without calling
`check_nip98_replay` first -- the invariant holds only because every current
HTTP call site does call it, and any error from the guard fails closed
(rejects) rather than defaulting to admit.

**NIP-42: structurally enforced, no shared state.** No seen-set exists for
NIP-42, and none is needed by the same argument that motivates NIP-98's:
NIP-42's "one card" is a 32-byte CSPRNG value generated fresh per connection
and never reused, held only in that connection's own `ConnectionState`, so
there is no cross-pod state to synchronize in the first place. Replay is
prevented by the conjunction of three structural facts, not a single
enforced barrier: (1) the challenge's unpredictability, (2) its storage
scoped to one connection, and (3) `handle_auth`'s state-machine guard, which
refuses to re-verify an AUTH once the connection is `Authenticated` or
`Failed`. A code change that made the challenge predictable, shared it across
connections, or removed the state-machine guard would each independently
reopen a replay window -- there is no test asserting cross-connection replay
is rejected end to end (see *Verification*), so this tier should be read as
structurally enforced, not test-enforced.

## Consequence of violation

**NIP-98.** Without the seen-set (or if it silently failed open), an attacker
who observes one `Authorization: Nostr <event>` header -- via a logging
system, a compromised intermediary, or network capture on an unencrypted hop
-- could resubmit the identical request repeatedly within the event's ±60s
validity window, each resubmission accepted as if freshly authenticated. The
NIP-98 event itself only asserts URL, method and (optionally) a body hash, so
a bare replay only repeats the exact request the attacker already observed --
but that is precisely the guarantee NIP-98's "one-shot" design is meant to
provide, and losing it turns a intercepted single request into a repeatable
one for the length of the window.

**NIP-42.** If the challenge were ever predictable or the state-machine guard
were removed, a captured AUTH event could be replayed against a fresh
connection to hijack a WebSocket session under the victim's identity --
because NIP-42 authentication is a one-time gate that then binds every
subsequent `EVENT` on that connection to the authenticated pubkey (see
`architecture-flows-websocket-authentication`), a successful replay would
grant the attacker the full authenticated capability of that connection, not
merely one request.

## Boundary

This node does not cover:

- **Blossom kind:24242 media auth** (`crates/buzz-media/src/auth.rs`) -- a
  third, distinct mechanism (a bounded `created_at`-to-`expiration` validity
  window, no seen-set, no per-connection challenge) for BUD-11 media
  requests. Named here as a related pattern, not documented in depth.
- **Push-gateway delivery auth replay tables**
  (`push_gateway_delivery_auth_replays`, `push_gateway_delivery_request_replays`)
  -- a separate subsystem protecting relay-pod-to-push-gateway delivery
  requests, a different threat model from client authentication.
- **The rest of the NIP-42 WebSocket authentication flow** (ban/allowlist/
  membership gates, NIP-OA delegation, per-message-type auth enforcement) --
  fully covered by `architecture-flows-websocket-authentication`, which this
  node `references` rather than duplicates.
- **The full NIP-98 verification steps and its HTTP call sites' request
  shapes** -- covered by `crates/buzz-auth/src/nip98.rs` itself and (once
  merged) `layers-authentication-nip-98-authentication`
  (PR #1795, not yet on `origin/launchpad`); this node covers only the
  replay-freshness layer, not the rest of NIP-98 verification.
- **General Nostr event deduplication at ingest** (storing an event once by
  its content-addressed id) -- a storage-layer concern, not an
  authentication-freshness one, and out of scope here.

## Relationships

- `references`: `architecture-flows-websocket-authentication` -- that node
  documents the full NIP-42 challenge/response flow this node's NIP-42
  section summarizes; this node adds the replay-specific analysis
  (why no seen-set exists, and why the structural mechanism suffices) rather
  than duplicating the flow's own steps.
- No `references` toward `layers-authentication-nip-98-authentication`: that
  node does not yet exist on `origin/launchpad` (see the TEAM_KNOWLEDGE
  evidence entry above). A future edge in that direction is natural once
  PR #1795 merges.

## Verification

- **NIP-98 replay guard, unit + integration:** `crates/buzz-auth/src/nip98_replay.rs`'s
  `mod tests` cover the community-scoped key format, cross-community
  isolation, lowercase key components, and the TTL floor/ceiling constants.
  `crates/buzz-pubsub/src/nip98_replay.rs`'s `mod tests` (marked `#[ignore =
  "requires Redis"]`, run via `just test`) cover first-claim-succeeds/
  replay-fails, cross-community isolation against real Redis, and TTL
  clamping at both the floor and the ceiling.
- **NIP-98 replay guard, wired through the enforcement point:**
  `crates/buzz-relay/src/api/bridge.rs`'s test module includes
  `nip98_replay_guard_rejects_cross_pod_replay_on_bridge_path` (two
  independent `RedisNip98ReplayGuard` instances sharing one Redis pool,
  modeling two relay pods, asserting the second pod rejects a replay the
  first pod already claimed), `nip98_replay_guard_rejects_same_pod_same_community_replay`,
  and `nip98_replay_check_fails_closed_when_guard_errors` (an always-erroring
  guard still produces a 401, not a pass-through).
- **NIP-42 challenge/response, unit:** `crates/buzz-auth/src/nip42.rs`'s
  `mod tests` include `challenge_is_64_hex_chars_and_unique`, which is the
  test directly backing the "challenge is fresh and non-repeating" half of
  this node's NIP-42 argument.
- **NIP-42 replay across connections:** no test in this repository exercises
  "capture one connection's signed AUTH event, present it on a second,
  freshly-opened connection, and assert it is rejected." The INFERENCE
  evidence entry above reasons to this conclusion from the challenge's
  randomness and per-connection scoping rather than citing a test that
  proves it end to end -- an expected-but-not-verified gap, named below.

## Scope and omissions

**This node covers** the replay-freshness invariant for Buzz's two primary
client-authentication surfaces (NIP-98 HTTP Auth and NIP-42 WebSocket Auth):
the invariant each is meant to hold, which tier of enforcement actually holds
it today, what breaks if it doesn't, and the boundary against Blossom's and
the push-gateway's separate replay-mitigation mechanisms.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full NIP-42 flow (ban/allowlist/membership gates, NIP-OA delegation) | `architecture-flows-websocket-authentication` |
| The full NIP-98 verification contract and its HTTP call sites | `crates/buzz-auth/src/nip98.rs`, and `layers-authentication-nip-98-authentication` once PR #1795 merges |
| Blossom kind:24242 media-auth replay mitigation | not yet in this corpus |
| Push-gateway delivery-auth replay tables | not yet in this corpus |
| General event-id deduplication at ingest (storage layer) | not this node's subject |

**Expected but not verified when this node was written:**
- No end-to-end test captures a real NIP-42 AUTH event and replays it against
  a second, independently-challenged connection to directly demonstrate
  rejection; the "no cross-connection replay" claim above is an INFERENCE
  from the challenge's randomness and connection-scoped storage, not a cited
  passing test.
- Whether Blossom's kind:24242 auth event ever needs (or is planned to gain)
  a seen-set of its own, given it currently relies solely on a bounded
  `created_at`-to-`expiration` window, was not investigated beyond confirming
  the current mechanism has no seen-set.
