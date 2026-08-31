# Plan: issue #1273 — document platforms/relay/ingest-handler.md

## ALREADY TRUE

- `crates/buzz-relay/src/handlers/ingest.rs` (5249 lines) is registered as `pub mod ingest;`
  in `crates/buzz-relay/src/handlers/mod.rs` and opens with a crate-doc comment: "Transport-neutral
  event ingestion pipeline. Both WebSocket `["EVENT", ...]` and HTTP `POST /events` feed into
  `ingest_event` — two doors, one room."
- Two existing corpus flow nodes already document this module's *behavior* exhaustively:
  `architecture-flows-event-ingestion` (the shared `ingest_event`/`ingest_event_inner` pipeline,
  16 ordered steps, trust boundaries, failure/rollback) and `architecture-flows-http-event-submission`
  (the full `POST /events` request lifecycle: router, NIP-98, replay guard, admission, then handoff
  into the same shared pipeline). Both exist on `origin/launchpad` today.
- Issue #1269 (sibling, unmerged) targets `platforms/relay/event-handler.md` — the WS side
  (`crates/buzz-relay/src/handlers/event.rs`). Not a valid relationship target yet.
- No `platforms/` directory exists yet in the corpus tree; this is the first node under it.
  No architecture-component node exists for the relay container, so no `part-of` target exists.
- `crates/buzz-relay` has no `README.md` (only 6 of 30 crates do, and buzz-relay is not one).
- No other crate in the workspace declares `buzz-relay` as a dependency — it is the top-level
  relay binary, not a library other crates build on.

## STEP 1 — Confirm scope against the two existing flow nodes

Read `architecture-flows-event-ingestion` and `architecture-flows-http-event-submission` in full.
Both already narrate the pipeline's ordered steps, trust boundaries, and failure modes down to
specific line-level behavior. A third document repeating that would violate DoD's "one
independently maintainable idea" and "without duplicating canonical content" bullets.
**Done when:** the genuinely uncovered ground is identified — the module's own responsibility
statement, its public interface as a contract table, and its real cross-module dependency edges
inside `buzz-relay` (who calls in, what it calls out to) — none of which either flow doc states
as such.

## STEP 2 — Extract the public interface

Read `crates/buzz-relay/src/handlers/ingest.rs` top-to-bottom for every `pub`/`pub(crate)` item:
`HttpAuthMethod`, `IngestAuth` (+ its `pubkey`/`scopes`/`conn_id`/`channel_ids`/`is_http` methods),
`IngestResult`, `IngestError`, `reject_with_transport`, `ingest_event`, plus the `pub(crate)`
helpers other modules actually call (`extract_channel_id`, `check_channel_membership`,
`requires_h_channel_scope`, `resolve_relay_reply_thread_meta`, `effective_message_author`).
**Done when:** every interface-table row cites a real declaration line, not a description.

## STEP 3 — Map real dependency edges, both directions

`grep` every file in `crates/buzz-relay/src/**` for `ingest::`/`super::ingest`/`handlers::ingest`
references to find every module that depends on `ingest.rs` (found: `handlers/event.rs`,
`api/bridge.rs`, `handlers/command_executor.rs`, `workflow_sink.rs`, `handlers/side_effects.rs`,
`conformance/mod.rs`). Cross-check `crates/buzz-relay/Cargo.toml` for the crate-level dependencies
`ingest.rs`'s own imports actually draw on (`buzz-auth`, `buzz-core`, `buzz-db` via `state`, `nostr`,
`uuid`, `chrono`, `tracing`, `metrics`).
**Done when:** both directions are cited to real source (not Cargo.toml alone, since this is a
module inside a crate, not a separate crate — state that scoping choice as an `INFERENCE`).

## STEP 4 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/ingest-handler.md` using `component.md`'s section
shape (per the Feature #614 sibling-node convention for `platforms/**`), `type: platforms`,
`status: draft`, `origin: launchpad`. Include a `references` relationship to both flow nodes
(supporting context, not a currency dependency — matches `relationships.schema.json`'s stated
directionality for `references`) and no `part-of` (no architecture-component node exists to
target). State outright in a Boundary section that pipeline ordering, HTTP request lifecycle,
and per-kind validators are the two flow docs' territory, not restated here.
**Done when:** every DoD bullet in #1273 is satisfied and every citation opens something real.

## STEP 5 — Gate and commit

Run the corpus unit test suite (must print `OK`), commit, verify zero new `validate.py` FAIL
lines by temporarily stashing the new file and re-running, then restore it.
**Done when:** commit exists and the before/after FAIL set is identical.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` introduces zero new FAIL lines.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- Every evidence citation opens a real file this session actually read.

## OPEN

- Whether a future `architecture-component` node for the relay container should declare
  `part-of` back to this node once one exists — not this task's call to make.

## LEFT OUT

- Re-narrating `ingest_event_inner`'s 16 ordered steps, its trust-boundary crossings, or its
  failure/rollback behavior — owned by `architecture-flows-event-ingestion`.
- The HTTP `POST /events` request lifecycle (tenant binding, NIP-98, replay guard, admission) —
  owned by `architecture-flows-http-event-submission`.
- The ~30 per-kind structural validators inside `ingest_event_inner` — both flow docs already
  name this as an open question they don't settle; this node doesn't settle it either.
- Documenting `crates/buzz-relay/src/handlers/event.rs` (the WS side) — issue #1269's subject.
