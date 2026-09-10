# Plan: issue #1269 — platforms/relay/event-handler corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (checked at commit 131b02f989684117d9ab1dd426f1673fa638e523) — this is the
  first node under `platforms/relay/`.
- `launchpad/docs/corpus/architecture/flows/event-ingestion.md`
  (`architecture-flows-event-ingestion`) already documents the shared
  `ingest_event`/`ingest_event_inner` pipeline in `crates/buzz-relay/src/
  handlers/ingest.rs` in depth — the community write fence, signature
  verification, scope checks, storage, and post-commit dispatch
  (`dispatch_persistent_event`, `filter_fanout_by_access`). Its own *Scope and
  omissions* section explicitly names ephemeral-kind handling
  (`handle_ephemeral_event`) as **out of scope**, calling it "a distinct,
  unstored delivery-only flow."
- No template exists yet for `type: platforms` documents. Per the batch
  convention (finding #4 in the dispatch brief), this node borrows
  `templates/component.md`'s section shape (Responsibility, Public interface,
  Dependencies, Boundary, Relationships, Scope and omissions) with
  `type: platforms` instead of `type: implementation`.
- `crates/buzz-relay/src/handlers/event.rs` (2497 lines) contains `handle_event`
  (the WS EVENT dispatcher), `handle_ephemeral_event`, `handle_agent_observer_event`,
  and the fan-out helpers (`filter_fanout_by_access`, `fan_out_event_to_local_subscribers`,
  `fan_out_pubsub_event`, `dispatch_persistent_event`) — all read directly from
  the worktree.
- `crates/buzz-relay/src/connection.rs:568-595` shows `handle_event` is invoked
  from the WS message loop after `ClientMessage::Event(event)` has already been
  parsed, gated by `state.handler_semaphore` (a concurrency permit), and spawned
  in its own tracing span — i.e. parsing/framing happens upstream of this
  handler, not inside it.

## STEP 1 — Scope the node against the existing flow doc

Read `architecture-flows-event-ingestion` in full (done) and `crates/buzz-relay/
src/handlers/event.rs` in full (done) to fix the boundary: this node documents
`handle_event`'s own WS-dispatch mechanics (auth-required check, gift-wrap
pubkey exception, AUTH-kind rejection, agent-observer-frame routing, ephemeral
routing) and the two branches the ingest flow doc explicitly excludes
(`handle_ephemeral_event`, `handle_agent_observer_event`) — not the persistent
`ingest_event` pipeline itself, which is `references`d rather than restated.

Done when: a one-paragraph boundary statement is drafted distinguishing this
node from `architecture-flows-event-ingestion`.

## STEP 2 — Verify shared helpers and test coverage

Confirm (via grep, done) that `extract_channel_id`, `requires_h_channel_scope`,
and `check_channel_membership` in `ingest.rs` are reused by
`handle_ephemeral_event`, and locate representative test coverage
(`crates/buzz-test-client/tests/e2e_relay.rs::test_ephemeral_event_not_stored`,
plus the in-file `#[cfg(test)] mod tests` covering fan-out frame construction,
observer routing, rate limiting, and cache scoping).

Done when: every dependency/test claim in the draft cites a file actually
opened.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/event-handler.md` with front
matter (`id: platforms-relay-event-handler`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [developer, agent]`,
`evidence`, `relationships: [{type: references, target:
architecture-flows-event-ingestion}]`) and a body covering: purpose/scope,
responsibility (WS EVENT dispatch), the three-way routing logic inside
`handle_event`, the ephemeral-event path, the agent-observer-frame path, the
NIP-01 `OK` response contract, dependencies (ingest.rs helpers, connection.rs
caller, protocol.rs `RelayMessage::ok`), boundary (explicitly not the ingest
pipeline, not the REQ/subscription read path, not the fan-out access-filter
internals beyond what's needed to explain delivery), and scope/omissions.

Done when: every DoD bullet from issue #1269 is satisfied and every citation
uses `path:A-B` / bare-path form.

## STEP 4 — Validate and commit

Run the corpus unit tests, confirm `OK`; run `validate.py`, confirm no new
FAIL lines beyond the 21 pre-existing ones (verified by temporarily moving the
new file aside and re-running); commit both files with `-s`.

Done when: commit exists on `task/1269-relay-event-handler` and the diff is
re-checked against the DoD checklist.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`, run as the sole content of its own Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` must show the same 21 FAIL lines with the new file removed as with it present (zero new FAILs).
- Every evidence citation must point to a file actually opened in this session.

## OPEN

- Whether a future `platforms.md` template will formalize `type: platforms`
  section shape — this node borrows `component.md`'s shape as an inference,
  per the batch's settled convention, not a confirmed template.
- Whether the roughly-thirty per-kind ingest validators interact with the
  ephemeral/observer paths documented here — they do not (ephemeral and
  observer frames never reach `ingest_event_inner`), confirmed by reading
  `handle_event`'s branching before any call to `ingest_event`.

## LEFT OUT

- Re-documenting the `ingest_event`/`ingest_event_inner` pipeline, the ~30
  per-kind structural validators, or the workflow engine's internals — all
  owned by `architecture-flows-event-ingestion` or explicitly named as its own
  gaps.
- The REQ/subscription read path and `filter.rs`'s NIP-29 scoping — a separate
  flow, not touched by `handle_event`.
- Full byte-level fan-out serialization/caching internals
  (`fanout_frame_cache`, `send_fanout_frames`) beyond what's needed to explain
  delivery — these are private helper functions with no external contract.
