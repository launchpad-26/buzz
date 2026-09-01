---
id: architecture-flows-event-ingestion
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The WebSocket EVENT handler (`handle_event`) requires an authenticated connection, rejects a mismatched event/auth pubkey (gift wraps excepted), refuses client-submitted AUTH events, and routes agent-observer-frame and ephemeral kinds through their own scope checks before any persistent-storage kind reaches the shared ingest pipeline."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Both the WebSocket EVENT handler and the HTTP `POST /events` bridge (`submit_event`/`submit_event_authed`) construct a transport-specific `IngestAuth` and then call the same `ingest_event()` function in `crates/buzz-relay/src/handlers/ingest.rs` -- one shared validation/storage/fan-out pipeline for both transports."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "`ingest_event_inner` first checks the community's durable write fence (`buzz_deletion::store(&state.db).is_serving_active(tenant.community())`), which queries whether the community row is not archived, not deleted, and has `deletion_state = 'active'`; a fenced/tombstoned/archived community fails the write with a `restricted:` reason before any other check runs, and a lookup error fails closed with an `error:`/internal result rather than admitting the write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "After the write fence, ingest rejects client-submitted AUTH events (kind 22242) and relay-signed-only membership notifications outright, rejects gift-wrap and presence-update kinds when the transport is HTTP, and rejects any kind classified `is_relay_only_kind` -- all before the event's signature is checked."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Signature and event-id verification happens via `buzz_core::verification::verify_event`, which recomputes the event id (SHA-256 over the canonical serialization per NIP-01) and independently checks the Schnorr signature; it is CPU-bound and is dispatched via `tokio::task::spawn_blocking` from the async ingest path so it cannot block the relay's async executor."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "After signature verification, ingest rejects events whose timestamp drifts more than 900 seconds (15 minutes) from server time in either direction, and rejects content exceeding 256 KB."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The event's `pubkey` must equal the authenticated principal's pubkey unless the event is a NIP-59 gift wrap (kind 1059), which deliberately carries an unrelated ephemeral signing key; this check is re-asserted inside `ingest_event_inner` even though the WebSocket handler also checks it earlier, because the HTTP transport reaches `ingest_event_inner` without going through `handle_event` at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`required_scope_for_kind` maps the event's kind to one of buzz-auth's permission scopes (e.g. `Scope::UsersWrite` for profiles/contact-lists/personas, `Scope::MessagesWrite` for text notes/long-form/reports), and ingest rejects the event with `IngestError::AuthFailed` if the authenticated principal's scopes do not contain the required scope; an unrecognized kind falls through this match with no arm and is rejected as an error, not silently admitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Relay-admin commands (kind 9030-9033) and NIP-43 leave requests are further restricted to global (non-channel-scoped) auth tokens even when the event itself carries no `h` tag, closing a gap where a channel-scoped token could otherwise issue a relay-wide administrative command."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Command kinds are dispatched to `command_executor::handle_command` only after signature verification, timestamp/content checks, pubkey/auth match, and scope validation have all passed -- never before."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Product-feedback events (kind for `KIND_PRODUCT_FEEDBACK`) and NIP-56 reports (`KIND_REPORT`) are sidecarred into their own private tables (a deployment-feedback table and the moderation report queue respectively) and never enter ordinary event storage or subscriber fan-out; community moderation commands (kinds 9040-9044) are likewise direct mutations that are never stored or fanned out as ordinary events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Before storage, ingest re-checks the authoring pubkey's durable moderation-restriction state (ban/timeout) even on an already-authenticated connection -- a durable backstop for the case where a live disconnect broadcast is missed by a banned member's still-open socket; a banned pubkey is refused with `blocked:`, a timed-out pubkey with `restricted: you are timed out until <ts>`, and a restriction-lookup error fails closed as an internal error rather than admitting the write. Moderation-command and relay-admin kinds are exempted from this specific gate because their own handlers enforce the ban themselves, so a timed-out admin can still lift the timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Channel scoping is resolved per kind: reactions derive their channel from their reaction target, kind:5 standard deletions derive it from the deleted event's stored `channel_id`, gift wraps are always global, kinds classified `is_global_only_kind` always clear `channel_id` to `None` even if a stray `h` tag is present, and kinds classified `requires_h_channel_scope` are rejected outright if no channel could be resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "For a channel-scoped, non-membership-exempt kind, `check_channel_membership` enforces that the authenticated pubkey is either a channel member or the channel has open visibility; the verdict is recorded through the conformance tracer as an `AuthCheck` step (Allow/Deny) alongside the claimed community from the event's own `h` tag and the server-resolved tenant community, so a claimed-vs-resolved-community mismatch is observable in the trace even though the verdict itself is always computed against the server-resolved tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A channel-scoped auth token cannot publish a global (channel-less) event, and conversely a channel-scoped token's channel access is checked against the event's resolved `channel_id` via `check_token_channel_access` -- this token-level restriction is legacy for WebSocket connections carrying a scoped token; in pure-Nostr mode channel access is enforced through NIP-29 membership instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Roughly thirty kind-specific structural validators run in the persistent path after the generic gates above and before storage -- for example `validate_edit_ownership` (kind:40003 edits), `validate_forum_vote_target` (kind:45002), `validate_diff_event` (kind:40008), `validate_engram_envelope` (kind:30174), `validate_agent_turn_metric_envelope` plus an async ownership check (kind:44200), `validate_event_reminder` (kind:30300), `validate_persona_envelope` (kind:30175), `validate_team_catalog_envelope` (kind:30178), and `validate_project_envelope` (kind:30621) -- each enforcing that kind's own tag-shape and cross-reference rules; a channel that is archived also rejects new channel-scoped events unless the event itself is an unarchive edit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "kind:9007 (create-group) pre-creates its channel row inside the ingest pipeline before the event itself is stored, and if the subsequent event insert then fails, ingest compensates by soft-deleting that pre-created channel so no orphaned channel row survives the failed write; a duplicate create (the target UUID already exists) is reported back as `accepted: false, message: \"duplicate: channel already exists\"` without erroring the connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Non-replaceable persistent events are stored via `insert_event_with_thread_metadata`, which runs inside a single Postgres transaction: an `INSERT ... ON CONFLICT DO NOTHING` into `events` (the id-uniqueness dedupe -- a resubmitted event with an identical id is a no-op, not an error), and, only when a new row was actually inserted and NIP-10 thread metadata was resolved, an `INSERT ... ON CONFLICT DO NOTHING` into `thread_metadata` followed by `UPDATE thread_metadata SET reply_count = reply_count + 1, last_reply_at = NOW()` against the parent and (separately) the root event -- so a duplicate event's thread counters are never double-incremented, and dedupe and the counter update are part of the same atomic transaction as the row insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Replaceable (NIP-16) and parameterized-replaceable (NIP-33) kinds skip `insert_event_with_thread_metadata` entirely and instead call `replace_addressable_event` / `replace_parameterized_event`, which perform an atomic replace with stale-write protection rather than a plain insert; a NIP-33 `d` tag longer than `D_TAG_MAX_LEN` is rejected before either path runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "If the underlying database insert itself fails (not a duplicate -- a genuine `DbError`), ingest returns `IngestError::Internal` (or, for the one AUTH-specific `DbError::AuthEventRejected` case, `IngestError::Rejected`) after running the kind:9007 channel-compensation step described above; no partial event row or thread-metadata row is left behind because the failure happens inside the same transaction that would have written them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "On successful, non-duplicate storage, ingest runs any kind-specific side effects (`handle_side_effects`, logged at `error!` rather than `warn!` if they fail, because the event was already accepted and the relay is now in a state the client does not know about), pushes a fresh relay-signed kind:39005 live-thread-summary event for the affected thread when NIP-10 metadata was resolved, and then calls `dispatch_persistent_event`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`dispatch_persistent_event` first enqueues an `EventCreated` audit entry onto a bounded (capacity 1000) async channel using `.send().await` -- backpressure propagates to the caller if the audit DB is overloaded, rather than silently dropping the entry or accumulating unbounded in-memory state -- recording the authenticated actor's pubkey (not necessarily the event's own `pubkey`, so relay-signed events still attribute to the human who triggered them), the event id, kind, and channel id. It then spawns a background task that publishes the event to Redis pub/sub (`state.pubsub.publish_event`), fans it out to this node's local WebSocket subscribers through the same access-filtering chokepoint (`filter_fanout_by_access`) used by the cross-node Redis-fed fan-out path, and -- unless the kind is a workflow-execution kind, a command kind, a relay-signed workflow message, or a gift wrap -- triggers the workflow engine (`workflow_engine.on_event`) in its own spawned task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "`filter_fanout_by_access` is the single chokepoint that revalidates delivery access at send time regardless of how a recipient's subscription came to exist: it drops recipients whose connection is bound to a different community than the event, restricts author-only kinds (NIP-ER reminders) to the event's own author, restricts `SHARED_GATED_KINDS` events to the author unless the event carries `[\"shared\",\"true\"]`, and -- for a channel-scoped event on a channel whose current visibility is `private` -- drops any recipient who is not a current member, resolved through a fresh membership lookup rather than trusting the subscription's original registration; a visibility-lookup failure fails closed (drops every recipient) rather than leaking a possibly-private channel's events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "`ingest_event`'s outer wrapper (as distinct from `ingest_event_inner`) arms an `EmitGuard` around the conformance tracer before calling into the inner logic; if the inner logic exits through any path that never calls `emit(...)` with a terminal trace action, the guard's `Drop` records an `ImplBug` step that the conformance checker treats as a coverage breach -- a fail-closed structural guarantee that no exit path from the ingest pipeline can silently skip trace recording, backed by `docs/spec/MultiTenantRelay.tla`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/conformance/mod.rs"
  - statement: "Rejections are sanitized before being sent back to the client: `IngestError::Rejected`/`AuthFailed` messages are forwarded as-is (they are already client-safe, prefixed `invalid:`/`restricted:`/`blocked:`/`auth-required:`), but `IngestError::Internal` is always replaced with the fixed string `\"error: internal server error\"` on the wire so no database or system detail leaks to the client; the WebSocket transport reports every outcome (accept or reject) as a NIP-01 `OK` message on the same subscription/connection, while the HTTP bridge maps the same three `IngestError` variants onto HTTP 400 (Rejected), 401/403 (AuthFailed), and 500 (Internal)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Representative test coverage of this flow exists in `crates/buzz-test-client/tests/e2e_relay.rs`, including `test_send_event_and_receive_via_subscription` (accept + live fan-out), `test_auth_event_kind_rejected` (client-submitted AUTH events refused), `test_ephemeral_event_not_stored` (ephemeral kinds bypass persistent storage), and `test_reply_ingest_pushes_live_thread_summary` (thread-counter/kind:39005 side effect); unit coverage of the scope allowlist, global/channel-scoped classification, and per-kind envelope validators lives in `crates/buzz-relay/src/handlers/ingest.rs`'s own `#[cfg(test)] mod tests`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The roughly thirty per-kind structural validators inside `ingest_event_inner` are not individually documented by this node; grouping them under one flow node rather than splitting each into its own node is a scoping choice for this pass, not a claim that no further decomposition is warranted."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.7
---

# Event ingestion

How a signed Nostr event submitted by a client becomes a durably stored,
fanned-out event on a Buzz relay -- from the wire to storage, live delivery,
audit, and workflow triggering.

## Trigger, preconditions, and termination

**Trigger.** A client sends a signed Nostr event over one of two transports that
converge on the same pipeline:

- **WebSocket**: a NIP-01 `["EVENT", <event>]` frame on an already-authenticated
  (NIP-42) connection, handled by `handle_event` in
  `crates/buzz-relay/src/handlers/event.rs`.
- **HTTP**: a `POST /events` request authenticated by NIP-98 (or a dev-mode
  `X-Pubkey` header), handled by `submit_event`/`submit_event_authed` in
  `crates/buzz-relay/src/api/bridge.rs`.

Both transports construct a transport-specific `IngestAuth` (`IngestAuth::Nip42`
or `IngestAuth::Http`) and hand off to the single shared function
`ingest_event` in `crates/buzz-relay/src/handlers/ingest.rs`. Everything from
signature verification through storage and fan-out described below happens
inside that one function, run once per event regardless of which transport it
arrived on.

**Preconditions.**

- The connection/request is already authenticated -- the WebSocket handler
  requires `AuthState::Authenticated`; the HTTP bridge requires a valid NIP-98
  signature (or dev-mode header) before `ingest_event` is ever called.
- The target community must be write-serving: `is_serving_active` must return
  true for the tenant the request resolved to (see *Trust-boundary crossings*
  below).
- Ephemeral kinds (NIP-16) and the small set of relay-only/admin/handled-inline
  kinds never reach this document's storage path at all -- ephemeral kinds are
  diverted to a separate ephemeral-event handler by the WebSocket layer before
  `ingest_event` is called (HTTP never accepts them), and several other kinds
  (relay-admin, NIP-43 leave, product feedback, NIP-56 reports, moderation
  commands) are handled and terminated inside `ingest_event_inner` itself,
  before reaching ordinary storage.

**Termination and outcome.** Every call to `ingest_event` terminates in exactly
one of:

1. **Accepted and stored** -- `IngestResult { accepted: true, message: "" }`.
   The event is durably persisted, and post-commit dispatch (fan-out, audit,
   workflow triggering) is scheduled.
2. **Accepted as duplicate** -- `IngestResult { accepted: true, message:
   "duplicate:" }`. The event id already exists; no new row, no counter
   update, no fan-out.
3. **Rejected** -- `IngestError::Rejected(reason)`, mapped to a client-safe
   `invalid:`/`restricted:` message (WS: `OK false`; HTTP: 400).
4. **Auth-failed** -- `IngestError::AuthFailed(reason)`, mapped to a
   client-safe `restricted:`/`blocked:`/`auth-required:` message (WS: `OK
   false`; HTTP: 401/403).
5. **Internal error** -- `IngestError::Internal(_)`, always reported to the
   client as the fixed string `"error: internal server error"` regardless of
   the underlying cause (WS: `OK false`; HTTP: 500), so no database or system
   detail is ever echoed back.

The outer `ingest_event` wrapper arms a conformance-tracer `EmitGuard` around
the whole call: any exit path that fails to emit a terminal trace action is
caught by the guard's `Drop`, so termination is structurally guaranteed to be
observable even for a future code path the pipeline's author forgot to
instrument.

## Ordered interactions and data/state movement

The steps below describe the common path through `ingest_event_inner` for an
ordinary persistent (non-ephemeral, non-replaceable-only-handled-elsewhere)
event. Rejections at any step stop the pipeline immediately and return the
outcome described above; nothing after a failed step runs.

1. **Community write fence.** `buzz_deletion::store(&state.db)
   .is_serving_active(tenant.community())` -- a fenced/archived/deleted
   community rejects with `restricted:`; a lookup error fails closed as
   `error:`.
2. **Categorically-rejected kinds.** Client-submitted AUTH events,
   relay-signed-only membership notifications, HTTP-submitted gift-wrap/
   presence-update kinds, and any kind classified `is_relay_only_kind` are
   rejected here, before signature verification.
3. **Signature and id verification.** `verify_event` (in
   `crates/buzz-core/src/verification.rs`) recomputes the NIP-01 event id and
   checks the Schnorr signature, off the async executor via
   `spawn_blocking`. Failure returns `invalid: <reason>`.
4. **Timestamp and size bounds.** Event timestamp must be within ±900 seconds
   of server time; content must be ≤256 KB.
5. **Pubkey/auth match.** `event.pubkey` must equal the authenticated
   principal's pubkey, unless the event is a NIP-59 gift wrap.
6. **Scope check.** `required_scope_for_kind` resolves the kind to a required
   `buzz_auth::Scope`; the authenticated principal must hold it. An
   unrecognized kind has no match arm and is rejected. Relay-admin and
   NIP-43-leave kinds additionally require a global (non-channel-scoped)
   token.
7. **Command-kind dispatch.** Command kinds are routed to
   `command_executor::handle_command` and terminate here -- but only after
   steps 3-6 have all passed.
8. **Sidecar-only kinds.** Product feedback and NIP-56 reports are written to
   their own private tables and never enter ordinary storage or fan-out;
   moderation commands (9040-9044) mutate moderation state directly and are
   likewise never stored as ordinary events.
9. **Ban/timeout write-block.** The authoring pubkey's durable moderation
   restriction state is re-checked even on an already-authenticated
   connection (the backstop for a missed live-disconnect broadcast). Banned
   -> `blocked:`; timed out -> `restricted: you are timed out until <ts>`;
   lookup error -> fails closed as `error:`. Moderation-command and
   relay-admin kinds are exempt here because their own handlers enforce the
   ban themselves.
10. **Channel resolution.** `channel_id` is derived per kind (reaction target,
    deletion target's stored channel, gift wrap -> always global,
    `h`-tag extraction otherwise), then forced to `None` for
    `is_global_only_kind` kinds, then required to be present for
    `requires_h_channel_scope` kinds.
11. **Token/channel access and membership.** A channel-scoped token's access is
    checked against the resolved channel; a global event cannot be published
    by a channel-scoped token. For channel-scoped, non-membership-exempt
    kinds, `check_channel_membership` enforces member-or-open-visibility, and
    the verdict is recorded via the conformance tracer's `AuthCheck` step.
12. **Handled-inline kinds.** Relay-admin kinds and NIP-43 leave requests
    mutate `relay_members`/roster state directly and terminate here without
    being stored as ordinary events; NIP-43 announcement events they trigger
    are published fire-and-forget.
13. **Kind-specific structural validation.** Archived-channel rejection
    (unless unarchiving), NIP-09 deletion single-target enforcement, and the
    per-kind envelope validators (edit ownership, forum-vote target, diff
    metadata, engram envelope, agent-turn-metric envelope plus ownership,
    event-reminder tags, persona/team-catalog/project envelopes, and others)
    run here. kind:9007 (create-group) pre-creates its channel row at this
    step.
14. **Storage.** Replaceable and parameterized-replaceable kinds go through
    `replace_addressable_event`/`replace_parameterized_event` (atomic replace
    with stale-write protection). Everything else goes through
    `insert_event_with_thread_metadata`, a single Postgres transaction that
    inserts the event row (`ON CONFLICT DO NOTHING` -- the id-uniqueness
    dedupe), and, only if a new row was actually inserted, inserts/updates
    `thread_metadata` and increments `reply_count` on the parent and root
    events. A duplicate event is reported as accepted with message
    `"duplicate:"` and none of the counter/thread-metadata work runs.
15. **Post-storage side effects.** `handle_side_effects` runs kind-specific
    side effects (channel creation follow-through, git repo seeding, etc.),
    logging failure at `error!` because the event was already accepted; a
    fresh relay-signed kind:39005 live-thread-summary event is pushed if
    NIP-10 thread metadata was resolved.
16. **Post-commit dispatch.** `dispatch_persistent_event` enqueues an
    `EventCreated` audit entry on a bounded channel (backpressure, not silent
    drop), then spawns a background task that publishes to Redis pub/sub,
    fans out to local WebSocket subscribers through `filter_fanout_by_access`,
    and (for most kinds) triggers the workflow engine.

## Authentication/authorization/trust-boundary crossings

- **Transport authentication is the outer boundary.** WebSocket requires
  NIP-42 auth on the connection; HTTP requires NIP-98 signature verification
  (or a dev-mode header) per request. `ingest_event` itself trusts the
  `IngestAuth` its caller constructed -- it does not re-verify the transport's
  own authentication, only the event's internal consistency with it.
- **Tenant/community boundary.** The HTTP bridge binds a community from the
  request's `Host` header before any tenant-scoped write; an unmapped host
  fails closed with a generic 404 rather than falling back to a default
  tenant. The community write fence (step 1) and every downstream DB call are
  scoped to that resolved `tenant.community()`, not to any community claimed
  inside the event's own tags.
- **Claimed vs. resolved community.** The channel-membership `AuthCheck` trace
  step records the community claimed by the event's own `h` tag alongside the
  server-resolved tenant community, but the actual authorization verdict is
  always computed against the server-resolved community -- the claimed value
  is observability only, never a second source of authority.
- **Scope boundary.** `required_scope_for_kind` + the auth context's
  `scopes()` gate every kind against a specific `buzz_auth::Scope`
  (`MessagesWrite`, `UsersWrite`, etc.); relay-admin and NIP-43-leave kinds
  add a further global-token-only restriction on top of scope.
- **Channel membership/visibility boundary.** `check_channel_membership` at
  ingest time and `filter_fanout_by_access` at delivery time are two
  independent enforcement points for the same boundary: passing the former
  only gets an event stored, and every subsequent delivery -- live fan-out and
  cross-node Redis-fed fan-out alike -- revalidates membership/visibility
  fresh rather than trusting that an event was accepted.
- **Moderation boundary.** Ban/timeout state is checked both here (a durable
  write-block backstop) and, for command/admin kinds, inside their own
  handlers -- deliberately overlapping so a timed-out admin can still lift
  the timeout while an ordinary timed-out member cannot write.

## Failure, abort, and rollback behavior

- **Any rejection before storage leaves no trace.** Steps 1-13 above return an
  error directly; nothing is written to `events`, `thread_metadata`, or any
  side table, and no fan-out or audit entry is scheduled.
- **Storage is transactional.** `insert_event_with_thread_metadata` wraps the
  event insert, the `thread_metadata` insert, and the parent/root
  `reply_count` updates in one Postgres transaction (`pool.begin()` /
  `tx.commit()`); a failure partway through rolls back the whole transaction,
  so a reply can never be stored without its counter update landing, and vice
  versa.
- **Duplicate storage is a no-op, not a rollback.** `ON CONFLICT DO NOTHING`
  means a resubmitted event with an identical id simply does not re-run the
  counter/thread-metadata logic; it is reported `accepted: true, message:
  "duplicate:"`, which is a deliberate idempotent-retry behavior, not a
  failure path.
- **kind:9007 channel pre-creation has explicit compensation.** If the event
  insert that follows a create-group channel pre-creation then fails, ingest
  soft-deletes the pre-created channel row so no orphaned channel survives a
  failed write, and invalidates the relevant channel-deleted cache entry.
- **A genuine database error surfaces as `IngestError::Internal`**, sanitized
  to the fixed client-facing string `"error: internal server error"` --
  callers never see the underlying `DbError`.
- **Post-commit dispatch failures do not roll back storage.** Once storage
  succeeds, the event is durably accepted regardless of what happens next:
  a Redis publish failure only logs a warning and invalidates the local-echo
  dedupe cache entry (so the event is not incorrectly suppressed if it comes
  back over Redis); a fan-out serialization failure is logged and drops that
  delivery; a workflow-trigger failure is logged and does not retry. The NIP-01
  `OK` response the client already received is not revised by any of these
  later failures -- "accepted" only ever describes durable storage, never
  delivery or side effects.
- **Representative verification.** `crates/buzz-test-client/tests/
  e2e_relay.rs`'s `test_send_event_and_receive_via_subscription`,
  `test_auth_event_kind_rejected`, `test_ephemeral_event_not_stored`, and
  `test_reply_ingest_pushes_live_thread_summary` exercise accept/fan-out,
  AUTH-kind rejection, ephemeral bypass, and the thread-counter side effect
  respectively. Unit tests in `crates/buzz-relay/src/handlers/ingest.rs`'s
  own `#[cfg(test)] mod tests` cover the scope allowlist, global/channel-scoped
  classification, and individual per-kind envelope validators.

## Scope and omissions

**This document covers** the common-path pipeline a persistent Nostr event
travels through from either transport (WebSocket `EVENT` or HTTP `POST
/events`) to durable storage, live/cross-node fan-out, audit logging, and
workflow triggering -- including its ordering, its authorization boundaries,
and its failure/rollback behavior.

**It deliberately does not enumerate** the roughly thirty per-kind structural
validators inside `ingest_event_inner` (persona, project, engram,
event-reminder, team-catalog, diff, forum-vote-target, edit-ownership,
push-lease, and others) one by one -- each is a self-contained tag-shape/
cross-reference check for one event kind, named in *Ordered interactions*
step 13 as a category, not itemized here. Whether some of these deserve their
own corpus nodes (e.g. a NIP-MP project-envelope node, given it already has a
dedicated fixture oracle) is a real open question this document does not
settle.

**Also out of scope, named as gaps:**

- Ephemeral-kind handling (`handle_ephemeral_event`) -- ephemeral events never
  reach the persistent storage/fan-out path this document describes; they are
  a distinct, unstored delivery-only flow.
- The full per-kind side-effect catalog in
  `crates/buzz-relay/src/handlers/side_effects.rs`.
- The workflow engine's own trigger-matching and execution semantics
  (`buzz-workflow`) -- this document covers only that ingest *calls*
  `workflow_engine.on_event`, not what happens inside it.
- The subscription/`REQ` read path and `filter.rs`'s NIP-29-scoping caveat
  for stray `h` tags on global-only kinds -- ingest only *writes* the tag as
  signed; how the read path matches it is a separate flow.
- Cross-node replication mechanics of Redis pub/sub itself (`buzz-pubsub`) --
  this document covers only that ingest publishes to it and that
  `fan_out_pubsub_event` consumes it through the same access filter.

**Expected but not verified when this node was written:** whether every one of
the ~30 per-kind validators listed in step 13 is exhaustively enumerated
above, versus this document naming only the ones encountered while reading
the file top-to-bottom -- the source file is large (over 5,000 lines) and was
read in sections rather than confirmed line-by-line complete.
