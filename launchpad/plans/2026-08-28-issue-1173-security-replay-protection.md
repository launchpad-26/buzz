# Plan: issue #1173 — document layers/security/replay-protection.md

Parent PRD #607. Repository revision recorded for this plan:
`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` (origin/launchpad, fetched at worktree
creation).

## ALREADY TRUE

- `launchpad/docs/corpus/layers/security/replay-protection.md` does not exist on
  disk (`launchpad/docs/corpus/layers/` has no `security/` subdirectory yet).
- No template named `replay-protection` or `layers` exists; the closest structural
  match is `launchpad/docs/corpus/templates/invariant.md`, which prescribes:
  Invariant statement, Scope, Enforcement today, Consequence of violation,
  Boundary, Relationships, Scope and omissions. Its own front matter uses
  `type: governance` only because it documents the corpus's own authoring rules —
  a real instance node picks `type` by subject matter. This node's path
  (`layers/security/...`) maps to `type: layers` per the existing corpus
  directory convention (`architecture/**` → `type: architecture`, etc.).
- `node.schema.json` requires `id, type, status, origin, audiences, evidence`;
  `relationships` is optional and, per `AGENTS.md`, every target must resolve
  against a node that exists on `origin/launchpad` right now.
- Strong evidence base already read and open:
  - `crates/buzz-auth/src/nip98_replay.rs` — `Nip98ReplayGuard` trait,
    `DEFAULT_REPLAY_TTL_SECS = 120`, `MAX_REPLAY_TTL_SECS = 3600`,
    `nip98_replay_key` (community-scoped Redis key), fail-closed contract,
    "verify first, then mark" ordering.
  - `crates/buzz-auth/src/nip98.rs` — `verify_nip98_event` is purely structural
    (sig, kind, timestamp, URL, method, optional body hash); it does **not**
    check for reuse of the same event id.
  - `crates/buzz-pubsub/src/nip98_replay.rs` — `RedisNip98ReplayGuard`, the
    production implementation, `SET NX EX` atomic set-if-absent.
  - `crates/buzz-relay/src/api/bridge.rs` — `check_nip98_replay` /
    `check_nip98_replay_with_guard`, the single enforcement point, fail-closed on
    guard error, skips the dev-mode zero-hash path.
  - `crates/buzz-relay/src/state.rs` — `AppState.nip98_replay: Arc<dyn
    Nip98ReplayGuard>`, wired to `RedisNip98ReplayGuard` in production.
  - Call sites: `crates/buzz-relay/src/api/invites.rs`,
    `crates/buzz-relay/src/api/workflows.rs`, and multiple sites inside
    `crates/buzz-relay/src/api/bridge.rs` itself (generic Nostr HTTP bridge,
    git-adjacent paths).
  - `crates/buzz-auth/src/nip42.rs` — `generate_challenge` (32 CSPRNG bytes,
    hex), `verify_nip42_event` (kind, signature, challenge match, relay-URL
    match, ±60s window). **No seen-set** — NIP-42 has no analog to
    `Nip98ReplayGuard`.
  - `crates/buzz-relay/src/connection.rs` — challenge generated fresh per
    connection at connection setup, stored as `AuthState::Pending { challenge }`.
  - `crates/buzz-relay/src/handlers/auth.rs` — `handle_auth`'s state-machine
    guard: an AUTH received while already `Authenticated` or `Failed` is
    rejected immediately with no re-verification — the structural reason a
    captured AUTH event cannot be replayed a second time on the *same*
    connection, combined with the per-connection random challenge meaning it
    cannot be replayed on a *different* connection either.
  - `launchpad/docs/corpus/architecture/flows/websocket-authentication.md`
    (id `architecture-flows-websocket-authentication`) — **exists on disk**,
    already documents the NIP-42 flow in full and explicitly names NIP-98's
    "separate replay-protection layer... deserves its own node. Not yet in
    this corpus" as a named gap. This is the node this task fills, and its
    `id` is a valid `references` target.
  - `launchpad/docs/corpus/layers/authentication/nip-98-authentication.md`
    (id `layers-authentication-nip-98-authentication`) does **not** exist on
    `origin/launchpad` — only in unmerged PR #1795 (issue #1029, sibling task).
    Not a valid relationship target; the gap will be named in Scope and
    omissions instead.
  - `crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql` +
    `crates/buzz-push-gateway/src/postgres.rs` define a **separate** replay
    mechanism (`push_gateway_delivery_auth_replays`,
    `push_gateway_delivery_request_replays`) for push-delivery auth between
    relay pods and the push gateway — a different subsystem, out of scope per
    the issue's explicit NIP-98/NIP-42 framing and the atomicity rule.

## STEP 1 — Confirm scope and no duplicate

Re-confirm no `layers/security/` directory exists yet and no other corpus file
declares `id: layers-security-replay-protection`. Done via the searches above
(ALREADY TRUE); re-check immediately before writing in STEP 2 since siblings in
this batch may land concurrently.

**Done when:** `find launchpad/docs/corpus -iname 'replay-protection*'` and a
grep for `layers-security-replay-protection` across the corpus both return
nothing.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/layers/security/replay-protection.md` following
the `invariant.md` template's required sections (Invariant statement, Scope,
Enforcement today, Consequence of violation, Boundary, Relationships, Scope and
omissions), adapted for a node with **two** enforcement mechanisms for one
threat class (message/event replay) rather than one:

- NIP-98 HTTP Auth: predicate-enforced via a shared, community-scoped Redis
  seen-set (`SET NX EX`), fail-closed on guard error.
- NIP-42 WebSocket Auth: structurally enforced via a fresh per-connection
  CSPRNG challenge plus a one-shot `AuthState` machine — no seen-set exists or
  is needed, because the challenge itself is unpredictable and single-use per
  connection.

Front matter: `id: layers-security-replay-protection`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator,
reviewer]` (operator included because the Redis-backed guard and its TTL are
an operational concern). One `references` relationship to
`architecture-flows-websocket-authentication` (confirmed present on disk).
Evidence entries per the ALREADY TRUE list above, classified FACT (all are
directly opened source) plus one INFERENCE for the "no seen-set needed for
NIP-42" reasoning, with confidence stated.

**Done when:** the file exists, is valid YAML+Markdown, and every required
template section is present.

## STEP 3 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py`, confirm exit
0. Run the corpus unittest suite as its own command, confirm `OK`.

**Done when:** both commands pass with no errors.

## STEP 4 — Commit, push, open draft PR

Commit with `-s`. Push the branch. Open a draft PR against `launchpad` stating
`Closes #1173`, that validation and tests passed, that this is self-review
only, and the standard batch-owner deferral line.

**Done when:** PR URL is returned by `gh pr create`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — exit 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — `OK`, run as the sole command in its own tool call (commit-gate stamp requirement).

## OPEN

- Whether `layers-authentication-nip-98-authentication` (PR #1795, unmerged)
  should eventually gain a reciprocal `references` edge toward this node once
  both are merged — left for a follow-up, not this task, since PR #1795's node
  isn't a valid target from here today.

## LEFT OUT

- Any edit to `nip-98-authentication.md`'s content (it doesn't exist on
  `origin/launchpad` yet, and even if it did, editing a second hand-authored
  node is out of scope for this task).
- Push-gateway delivery-auth/request replay tables — a distinct subsystem,
  named only as a boundary exclusion, not documented in depth here.
- Any runtime/behavior change. This is documentation only.
