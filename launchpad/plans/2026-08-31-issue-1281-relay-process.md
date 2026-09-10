# Plan: issue #1281 — document platforms/relay/process.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/process.md` does not exist yet on
  `origin/launchpad` (confirmed: `test -f` and `git ls-tree` both miss it).
- `launchpad/docs/corpus/architecture/containers/relay.md` (id
  `architecture-containers-relay`, `status: draft`) already exists on
  `origin/launchpad` and documents the relay as a C4 *container*: its
  responsibility, listeners/routes, outbound connections, deployment and
  graceful-shutdown behavior. That node already cites `main.rs:1248-1405`
  for the listener table and the shutdown budget.
- No `type: platforms` template is merged (`templates/` has no
  `platforms.md`); per `AGENTS.md`'s documented no-template path and
  finding #4 from the batch brief, sibling `platforms/**` nodes borrow
  `templates/component.md`'s section shape (Responsibility / Public
  interface / Dependencies / Boundary / Relationships / Scope) without
  claiming `type: implementation` — this task uses `type: platforms`,
  the schema's own enum value for this corpus surface.
- No existing corpus node documents `main()`'s own startup composition
  (the containers/relay.md node covers listener addresses and the
  shutdown budget, but not the phase order inside `main()` — config load,
  datastore bootstrap, service construction, `AppState` assembly, optional
  seams, background worker spawn, router build — before `serve()` is
  called).
- Issue #1271 (graceful shutdown) is out of scope here per the issue body
  and the task brief: it is committed to a local branch, not merged to
  `origin/launchpad`, so it cannot be a relationship target and its
  content (the `serve()` SIGTERM/drain sequence) is deliberately excluded
  from this node's claims beyond noting that `main()` hands off to it.

## STEP 1 — Read the issue and confirm scope

Read issue #1281's body (done): its DoD requires one hand-authored node,
schema-valid front matter, FACT/INFERENCE/TEAM_KNOWLEDGE discipline,
"states responsibility and well-defined interface/boundary," "names
dependencies and collaborators," "links source implementation and
tests," and "explains only component-level behavior, not the entire
containing platform." No `--kinds`-style surprises here; this is a
docs-only task.

## STEP 2 — Read `crates/buzz-relay/src/main.rs` in full and extract the
composition phases

Read the file (2194 lines). Identified phase order inside `async fn
main()`: crypto-provider install → tracing/logging init → config load +
keypair → metrics install → Postgres connect + migration gate + fence
checks → multi-tenant community bootstrap (idempotent) → subsystem
service construction (audit, redis/pubsub, auth, search, workflow,
media) → `AppState::new` assembly → optional seams (mesh boot, git
conformance probe) → consistency reconciliation → ~23 `tokio::spawn`
background workers → `build_router`/`build_health_router` → `serve(...)`
(hands off to #1271's scope) → post-`serve` teardown (audit drain, OTEL
flush). Counted 23 `tokio::spawn` call sites via grep to cite the
background-worker claim precisely rather than eyeballing it.

## STEP 3 — Cross-check `architecture-containers-relay` to avoid
duplication

Read that node in full. It already owns: listener addresses/ports,
route table, outbound connected systems, deployment image/chart facts,
graceful-shutdown budget (35s worst case), health-probe wiring, and the
`BUZZ_AUTO_MIGRATE` gate. This node will not restate those — it will
`references` that node and focus on the *order and composition* of
`main()`'s startup, which that node does not describe.

## STEP 4 — Write the node

Front matter: `id: platforms-relay-process`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. Evidence: one FACT per phase claim, each citing the real
line range read in `main.rs` (and `state.rs:782` / `router.rs:33`,
`router.rs:294` / `config.rs:541` for the collaborator signatures). One
`references` relationship to `architecture-containers-relay` (confirmed
present on `origin/launchpad` above). No relationship to any #1271
content since it is unmerged. Body: Purpose/scope, Responsibility,
Composition phases (ordered table + prose), Dependencies/collaborators,
Boundary (explicitly excluding graceful shutdown, container-level
facts, and full protocol handling), Relationships, Scope and omissions
(gaps: exact behavior of each of the 23 spawned workers is not itemized
individually — component-level phase description only, per DoD's own
"not the entire containing platform" bullet).

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`, as its own sole Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 with the new file present, and must show the identical FAIL set as a clean `origin/launchpad` checkout when the new file is removed/stashed (zero new FAILs contributed).
- `git commit -s` must succeed with a verification stamp; if blocked, retry the test+commit pair exactly once more before reporting BLOCKED.

## OPEN

- Whether a `platforms` template should exist is unresolved (tracked
  somewhere in #1307–#1351 per `AGENTS.md`'s own table) — this node is
  written against `node.schema.json` directly, borrowing
  `component.md`'s shape by convention, and says so in its own body.
- Exact per-worker behavior of all 23 background tasks spawned in
  `main()` is not itemized — named as a class with a citation to the
  grep count, not individually documented; a future node could cover
  any one worker in more depth if it becomes its own maintainable idea.

## LEFT OUT

- The `serve()` function's SIGTERM/drain sequence (#1271's scope) —
  referenced only as "main() hands off to serve(), which binds
  listeners and manages graceful shutdown," not described further.
- Anything already covered by `architecture-containers-relay`
  (listener addresses, route table, deployment/chart facts,
  shutdown budget numbers) — referenced, not duplicated.
- Push/reserved for a future task if it becomes its own concept.
