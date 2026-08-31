# Plan: issue #1271 — platforms/relay/graceful-shutdown corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/graceful-shutdown.md` does not exist
  on `origin/launchpad` (repo revision `131b02f989684117d9ab1dd426f1673fa638e523`).
- No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`;
  `node.schema.json`'s enum includes `platforms` but `AGENTS.md` documents a
  no-template path: write directly against the schema.
- Sibling task #1267 (`platforms/relay/connection-manager.md`, local branch
  `task/1267-relay-connection-manager`, not yet on `origin/launchpad`) has
  already established the working convention for this batch: `type:
  platforms`, borrowing `templates/component.md`'s section shape (Purpose,
  Responsibility, Public interface, Dependencies, Boundary, Relationships,
  Scope and omissions) without adopting its `type: implementation`. This node
  follows the same convention for consistency, per the task brief's finding
  #4, but does **not** declare a `relationships` edge toward
  `platforms-relay-connection-manager` since that id does not resolve on
  `origin/launchpad` yet.
- `architecture-flows-websocket-connection` exists on `origin/launchpad` and
  documents the connect → authenticate → terminate request/response
  sequence; it is not the shutdown orchestration this node covers, so no
  relationship to it is needed (shutdown is not a step inside that flow's own
  documented sequence).
- `crates/buzz-relay/src/main.rs`'s `serve()` function already carries a
  detailed doc comment (lines 1244–1287) describing the shutdown budget
  (5s grace + 30s hard-drain backstop = 35s worst case), which is primary,
  citable evidence for this node's core claims.
- Sibling #1267's node already documents `ConnectionManager::drain_all` /
  `drain_all_jittered` (the per-connection close mechanics) in full; this
  node scopes itself to process-level orchestration — signal handling,
  listener shutdown fan-out, the hard-shutdown timer, audit-worker drain,
  and OTEL flush — and references the drain functions only by name where the
  orchestration calls them, not their internals.

## STEP 1 — Confirm scope boundary against #1267 and existing flow nodes

Re-read `crates/buzz-relay/src/main.rs`'s `serve()`, `shutdown_signal()`, and
`main()`'s post-`serve()` cleanup (audit drain, OTEL tracer shutdown). Confirm
this node documents: signal handling (SIGTERM/Ctrl+C), the `shutting_down`
flag and its two consumers (readiness probe, new-connection refusal), the
5s grace + 30s hard-drain budget, the listener-shutdown fan-out (health/TCP/
UDS `axum::serve` `with_graceful_shutdown` futures via a `watch` channel), the
hard-shutdown timer's `std::process::exit(1)` escape hatch, the audit-worker
drain, the OTEL tracer flush, and the community-revalidator cancellation —
without restating `ConnectionManager::drain_all`/`drain_all_jittered`'s own
internals (owned by #1267) or the WebSocket request/response sequence (owned
by `architecture-flows-websocket-connection`).

Done when: a clear before/after boundary list exists for the Boundary section.

## STEP 2 — Gather evidence with real line citations

Read and cite: `main.rs` `serve()` (lines ~1244–1446), `shutdown_signal()`
(~1448–1463), `main()`'s post-`serve()` cleanup (~1142–1160), the
`community_revalidator_cancel` field/wiring (`state.rs:652`, `:872`,
`main.rs:962-963`, `:1143`), `AuditShutdownHandle` and its `drain()` method
(`state.rs:1320-1343`), `router.rs`'s readiness handler and the WS-upgrade
shutdown check (`router.rs:366`, `:410-419`), `config.rs`'s
`MAX_DRAIN_JITTER_MS` and `drain_jitter_ms` (`config.rs:114`, `:143`), and
`deploy/charts/buzz/values.yaml`'s `terminationGracePeriodSeconds: 60`
(line 192). Note as FACT that no explicit Postgres/Redis pool `.close()` call
exists anywhere in the shutdown path — pools are dropped implicitly, and the
hard-shutdown timeout path calls `std::process::exit(1)`, which skips Rust
drop glue entirely (an explicit gap worth stating, not silently omitting).

Done when: every claim in the draft traces to an opened file/line.

## STEP 3 — Draft the document

Front matter: `id: platforms-relay-graceful-shutdown`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [developer, operator,
agent]`. Body follows `component.md`'s borrowed shape per the batch
convention: Responsibility, Public interface (functions/consts involved in
orchestration), Dependencies, Boundary, Relationships (none declared —
`platforms-relay-connection-manager` doesn't resolve on `origin/launchpad`
yet), Scope and omissions (mesh subsystem's own separate drain watcher in
`mesh_boot.rs`, gated behind `BUZZ_MESH`, named as a related-but-out-of-scope
gap; the `std::process::exit(1)` drop-glue gap named as expected-but-not-
verified in production; the `#1267` boundary named explicitly).

Done when: every DoD bullet from the issue is satisfied by a section of the
document.

## STEP 4 — Validate

Run the unittest suite (step 5a of the task loop). Run `validate.py` twice —
once with the new file present, once with it stashed — and diff the FAIL
counts to confirm zero new FAILs are introduced.

Done when: unittest suite reports `OK` and the FAIL set is unchanged.

## STEP 5 — Commit

Stage the corpus doc and this plan file; commit with `-s` and the message
`docs(corpus): document platforms/relay/graceful-shutdown (#1271)`.

Done when: the commit exists locally on `task/1271-relay-graceful-shutdown`.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- `validate.py`'s FAIL set is identical with and without the new file.
- Every evidence citation was opened and read; every `path:A-B` citation
  points to a real file.
- No `relationships` entry targets an id that doesn't resolve on
  `origin/launchpad`.

## OPEN

- Whether the mesh subsystem's own drain watcher (`mesh_boot.rs`, gated
  behind `BUZZ_MESH`) should eventually get its own corpus node or a
  `references` edge from this one, once mesh-related nodes exist in the
  corpus. Not resolved here.

## LEFT OUT

- Per-connection drain mechanics (`ConnectionManager::drain_all` /
  `drain_all_jittered` internals) — owned by #1267.
- The WebSocket connect/authenticate/terminate request/response sequence —
  owned by `architecture-flows-websocket-connection`.
- The mesh subsystem's `BUZZ_MESH`-gated drain watcher — adjacent but
  out of scope; named as a gap in Scope and omissions.
