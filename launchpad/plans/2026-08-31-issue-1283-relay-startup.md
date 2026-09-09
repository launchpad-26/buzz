# Plan: issue #1283 — document platforms/relay/startup.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/startup.md` does not exist on
  `origin/launchpad` (repo revision `131b02f989684117d9ab1dd426f1673fa638e523`).
- `launchpad/docs/corpus/templates/` has no `platforms`-specific template.
  Sibling unmerged node `platforms/relay/graceful-shutdown.md` (issue #1271,
  branch `task/1271-relay-graceful-shutdown`) already established the local
  convention for this gap: write directly against `node.schema.json`, borrow
  `templates/component.md`'s section shape (Responsibility, Public interface,
  Dependencies, Boundary, Relationships, Scope and omissions), and use
  `type: platforms` instead of that template's `type: implementation`.
- Sibling issue #1281 (`platforms/relay/process.md`) has a local worktree
  (`__worktrees/task-1281-relay-process`) and branch
  (`task/1281-relay-process`) but **no content has been committed or drafted
  there** — `git diff origin/launchpad task/1281-relay-process` is empty and
  the worktree has no uncommitted changes. There is nothing to read for the
  process/startup boundary; the distinction has to be inferred from the two
  issues' filenames and DoD text alone (see OPEN below).
- `crates/buzz-relay/src/main.rs`'s `main()` (lines 97–1160) runs a long,
  strictly sequential chain of fallible initialization steps — crypto
  provider install, logging/OTEL init, `Config::from_env()`, metrics
  install, Postgres pool creation (`Db::new`), conditional migration
  (`BUZZ_AUTO_MIGRATE`), partition/fence/roster verification, Redis
  pool + pub/sub, auth/search/media service construction, `AppState::new`,
  optional mesh boot, optional git-conformance probe, and finally spawning
  ~10 background workers — before calling `serve()` at line 1142, which is
  the first point any listener (including the health/liveness listener) is
  bound.
- `platforms/relay/graceful-shutdown.md` already documents `serve()`'s own
  internals (listener binding order, the shutdown watch channel, the drain
  call, the hard-shutdown timer) as *that* node's Responsibility/Public
  interface. Duplicating those specifics here would violate this issue's own
  DoD bullet ("does not duplicate... canonical content").

## STEP 1 — Confirm the process/startup boundary from the issue text alone

Both #1281 and #1283 carry byte-identical boilerplate DoD checklists; neither
issue body states an explicit distinction. Per the task brief's own
narrowest-defensible-reading instruction, this plan treats:
- **startup** (#1283, this node) = the ordered sequence of initialization
  steps `main()` runs, in the order it runs them, including which are
  fail-fast and which are non-fatal, ending at the call to `serve()`.
- **process** (#1281, not drafted) = presumably the overall binary
  composition / what `main()`'s existence and shape mean at a higher level
  (out of scope for this node; noted as an open boundary risk below, not
  invented as fact).

Done when: this boundary statement is written into the node's own Boundary
section, naming #1281 by number, so a future #1281 author sees exactly what
this node already claims.

## STEP 2 — Re-read the fallible sequence in `main()` end-to-end with line numbers

Re-confirm every citation against the actual file rather than relying on the
above skim: crypto provider (98–104), telemetry/logging (106–150),
`Config::from_env` (152–166), metrics install (168–177), `Db::new`
(179–199), conditional `db.migrate()` (201–211), `ensure_future_partitions`
(213–215, non-fatal), `validate_deletion_serving_catalog` (217–221,
fail-fast), `spawn_fence_probe` (223–241, non-fatal), NIP-43 membership
config checks (243–265, fail-fast when enforced), deployment-community
resolution (267–310), allowlist backfill (312–333), owner bootstrap
(335–358), d_tag backfill (360–366, non-fatal), audit service (368–380,
conditional), Redis pool + pubsub (382–412, fail-fast) plus 3 spawned
subscriber tasks, auth/search/media construction (414–444), `AppState::new`
(446–458), mesh boot (460–487, conditional fail-fast), git conformance probe
(489–525, conditional fail-fast), channel-roster-fence verification
(527–537, fail-fast), remaining reconciliation + ~10 background-worker spawns
(539–1140, best-effort / non-blocking), `serve()` call (1142).

Done when: every line range cited in the drafted document has been opened
and read in this session (not carried over from memory of the sibling node).

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/startup.md` following
`graceful-shutdown.md`'s established shape: Responsibility, Public interface
table (`main`, `Config::from_env`, `buzz_auto_migrate_enabled`, `Db::new`,
`Db::migrate`, `AppState::new`, the `serve()` call boundary), Dependencies
(depends-on: buzz-db, buzz-auth, buzz-search, buzz-pubsub, buzz-audit,
buzz-media, buzz-workflow, rustls; depended-on-by: the health/readiness
listener and Kubernetes' `startupProbe`, which cannot observe *any* liveness
signal until this entire sequence completes), Boundary (explicitly excluding
`serve()`'s own listener/shutdown internals — owned by
`platforms-relay-graceful-shutdown` — and excluding whatever #1281 turns out
to cover), Relationships, Scope and omissions.

Cite `buzz_auto_migrate_is_opt_in` and `relay_keypair_from_config`'s two unit
tests (`crates/buzz-relay/src/main.rs:2090-2103`, `:2105-2120`) as the DoD's
required test link. Cite `deploy/charts/buzz/values.yaml`'s `startupProbe`
(`failureThreshold: 60`, `periodSeconds: 2` → 120s budget) as the deployment
context the sequence's total fail-fast/non-fatal shape is sized against.

Done when: the file exists, front matter validates against
`node.schema.json`'s shape, and every evidence entry cites a path the author
opened this session.

## STEP 4 — Gate and commit

Run the corpus unit tests (sole content of the Bash call), then stage and
commit with `-s` (sole content of the Bash call). Verify zero new
`validate.py` FAIL lines by temporarily stashing the new file and re-running,
per the batch's documented gate.

Done when: `python3 -m unittest discover` reports `OK` and the commit
succeeds (or is retried once per the batch's documented gate quirk).

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `validate.py` new-FAIL-count delta is zero (stash-diff method).
- Every evidence citation points to a file this session actually opened;
  line-range citations use `path:A-B`, not `path#line=A,B`.
- No `relationships` entry unless its target resolves on `origin/launchpad`.

## OPEN

- **#1281/#1283 boundary is inferred, not confirmed.** Issue #1283's own DoD
  text is identical boilerplate to #1281's; nothing in either issue body
  distinguishes "process" from "startup" beyond the filename. #1281 has no
  drafted content anywhere to check against. This node takes the narrowest
  defensible reading of its own filename and the task brief's hint (config
  load, migration check, pool creation, etc.) — the ordered sequence of
  initialization steps in `main()` up to `serve()` — and states this
  assumption explicitly in its own Boundary section so a future #1281 author
  is not surprised by what this node already claims. If #1281 is later
  drafted to cover exactly the same sequence, one of the two nodes will need
  to be narrowed or merged; that is a call for whoever authors #1281, not
  this task.
- Whether Postgres pool creation's `after_connect` floor-guard / isolation
  assertion (`crates/buzz-db/src/runtime/mod.rs:514-543`) belongs in this
  node's own citations or is purely `platforms-relay-connection-manager`-
  adjacent detail was judged in favor of a brief mention only (it is part of
  *how* the pool is created, which is squarely this node's "pool creation"
  scope per the task brief's own example).

## LEFT OUT

- Full per-worker internal behavior of every background task spawned during
  startup (ephemeral reaper, reminder scheduler, pool-metrics poller, usage
  metrics poller, admin outbox/action workers, pub/sub consumers) — each is
  named as "a worker gets spawned here" for sequencing purposes only; their
  own logic is out of scope for a startup-sequence node and does not have
  its own corpus node yet at this revision.
- `serve()`'s own listener-binding order and shutdown orchestration —
  already `platforms-relay-graceful-shutdown`'s subject (#1271, unmerged).
- Whatever #1281 (`process.md`) will eventually claim — not yet drafted, so
  nothing to duplicate or cross-reference against on `origin/launchpad`.
