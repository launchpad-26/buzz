Issue #1119: document layers/lifecycle/resource-cleanup.md (child of Feature #611)

Stated size: issue body carries no explicit Size field (single hand-authored corpus node, no code change, same as sibling batch issues #1115-#1120) -> cap: 2 steps.

ALREADY TRUE

- Parent Feature #611 exists; sibling tasks in the same `layers/lifecycle/` batch
  are #1115 (background-workers), #1116 (cancellation), #1117 (concurrency), #1118
  (graceful-shutdown, committed on its own worktree branch, not yet merged), #1120
  (startup, committed on its own worktree branch, not yet merged).
- `launchpad/docs/corpus/layers/lifecycle/resource-cleanup.md` does not exist yet
  (confirmed via `test -f` on the target path).
- `origin/launchpad`'s corpus tree carries no `layers/` node yet (`git ls-tree -r
  --name-only origin/launchpad -- launchpad/docs/corpus` returns nothing under
  `layers/`) — #1118 and #1120 are readable only from their own unmerged
  worktrees, not from `origin/launchpad`, so this node cannot declare a
  `relationships` edge to either without adopting their id by naming convention
  only, not by a target that actually resolves today.
- `node.schema.json`'s `type` enum has no `flow`/`dynamic` member; `layers` is the
  enum member #1118 and #1120 both already chose (independently re-derived, not
  copied, per their own "A note on `type`" sections) for this same
  `layers/lifecycle/` directory family. This task follows the same precedent
  rather than re-deriving it a third time from scratch.
- `launchpad/docs/corpus/templates/flow.md` is the template both #1118 and #1120
  built their body shape from (Flow statement, Sequence, Diagram, Outcome,
  Boundary, Relationships, Scope and omissions); no dedicated resource-cleanup
  template exists, so this node follows the same flow template, with
  `type: layers` per the precedent above.
- Real, opened evidence for this node's actual subject (resource teardown, not
  shutdown sequencing) already gathered from this worktree at commit
  338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5:
  - `crates/buzz-relay/src/api/git/hydrate.rs` — `HydratedRepo` owns a
    `tempfile::TempDir`; its doc comment states dropping it cleans up
    (lines 21-23, 47-60). `materialize_manifest` (lines 289-376) creates the
    `TempDir` before any fallible step, so an early `?`-return during pack
    hydration drops it and deletes the temp workspace with no ref/HEAD ever
    written — cleanup-via-ownership on a failure path, not an explicit
    catch/cleanup block.
  - `crates/buzz-relay/src/api/git/pack_cache.rs` — `GitPackCache` owns a
    session-scoped `tempfile::TempDir` (`_session_dir`, line 67) plus a periodic
    heartbeat file; `impl Drop for GitPackCache` (lines 420-425) aborts the
    heartbeat task, and the session tempdir's own `Drop` deletes it — but only
    on a normal unwind. `cleanup_stale_sessions`/`cleanup_sessions_older_than`
    (lines 482-509) is the fallback for a crashed/SIGKILLed process whose Drop
    never ran: on the next `GitPackCache::new` (line 126), any `session-*`
    directory whose `.heartbeat` mtime is older than `STALE_SESSION_AGE` (10
    minutes, line 21) is swept via `remove_dir_all`, verified by the test
    `abandoned_sessions_are_removed_after_grace_period` (lines 561-572).
    `PopulationPermit`/`FlightParticipant` (`impl Drop`, lines 91-103) release a
    concurrency-limiting semaphore permit and decrement/remove an in-flight
    population's refcount on every exit path from `materialize_pack`.
  - `crates/buzz-relay/src/api/git/transport.rs` — `StreamingGit` (struct at
    line 1509, `impl Drop` at ~line 1637) holds the response's `Child`
    (`kill_on_drop(true)`, reaping the git subprocess and closing its pipes) and
    the `HydratedRepo` alive together, aborting the detached stdin-pump task on
    drop — ordered release across a child process, its file handles, and a temp
    workspace, all driven by one struct's `Drop`.
  - `crates/buzz-relay/src/state.rs` — `CommunityConnectionGuard` (`impl Drop`,
    ~lines 172-179) removes a WebSocket connection's registry entry "on every
    handler exit path" (its own doc comment) — the same RAII-guard pattern
    applied to a non-filesystem resource (a `DashMap` registration).
  - `crates/buzz-relay/src/api/media.rs` — `UploadPermit` (`impl Drop`, ~lines
    74-85) releases a global upload semaphore permit and decrements/removes a
    per-pubkey in-flight-upload counter, held for the lifetime of one upload
    request via the `AuthenticatedUpload` extractor.
  - `crates/buzz-db/src/lib.rs` — production code (e.g. line 1107) acquires
    connections via `sqlx::pool::PoolConnection` (`self.pool.acquire()`), sqlx's
    own RAII guard type that returns a Postgres connection to the pool when the
    guard drops; tests call `pool.close()` explicitly (e.g. lines 6944, 7999,
    8324, 8779, 8904, 8920-8921, 8997-8999) for an eager, deliberate pool-wide
    teardown, distinct from a single connection's per-use release.

STEP 1 [independent] <- RUNS HERE
Draft `launchpad/docs/corpus/layers/lifecycle/resource-cleanup.md` using the
`flow.md` template shape (`type: layers`, following #1118/#1120's precedent),
with body sections: A note on `type`, Flow statement, Sequence (the RAII/Drop
pattern narrated across the five Buzz-owned guard types listed above, in one
coherent order: temp-directory ownership -> child-process/file-handle ownership
-> concurrency-permit ownership -> connection-registry ownership -> the
crash-fallback sweep that exists precisely because Drop cannot run on SIGKILL),
Diagram (a Mermaid `sequenceDiagram` showing scope-exit -> Drop -> resource
released, plus the separate crash -> stale-sweep-on-next-start path), Outcome
(normal-exit release vs. the crash/orphan case `cleanup_stale_sessions` exists to
handle), Boundary (excludes #1118's shutdown signal/drain sequencing,
#1115/#1116/#1117's own subjects, and general container structure),
Relationships (re-check `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` immediately before finalizing front matter; declare none
if it still shows no `layers/*` node, since naming #1118/#1120's ids as targets
would be a hard `validate.py` error once this branch's commit lands on a merge
base that still lacks them), Scope and omissions. Every `evidence` entry cites a
real, opened path/line/test from this worktree at the recorded commit; no
fabricated symbol, no invented line range.
done when: the file exists with schema-shaped front matter and all seven
required body sections, satisfying every bullet in issue #1119's own DoD
checklist, and `python3 launchpad/project-intelligence/corpus/validate.py` (run
from repo root) ends with `PASS`.

STEP 2 [needs 1]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` alone in its own tool call, confirm it prints `OK`, then in a
separate tool call `git add` the new document plus this plan file and
`git commit -s` with message `docs(corpus): document resource cleanup (#1119)`.
Never combine the verify and commit calls; never pass `--no-verify`.
done when: the unittest run prints `OK` and the commit exists in `git log`
with a `Signed-off-by` trailer.

PARALLEL
None — STEP 2 needs STEP 1's file to exist and its own validation to have
already passed before the test suite and commit are meaningful.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root
  must end with `PASS` (pre-existing `UNVERIFIED` noise elsewhere is expected
  and not this task's to fix).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must print `OK`, run alone in its own tool call.
- `git commit -s` only after both gates pass, in a separate tool call from the
  verification commands — never combined, never `--no-verify`.

BUDGET

One document (`layers/lifecycle/resource-cleanup.md`) plus this plan file. No
runtime code changes. Single commit, no push, no PR (batch owner cherry-picks
later per the task brief).

OPEN

- Whether `type: layers` is the schema's best long-term fit for this whole
  `layers/lifecycle/` family is Feature #611's own open question, already
  flagged `INFERENCE` by both merged-precedent siblings (#1118, #1120) — this
  node repeats that same disclosed judgment call rather than re-litigating it.
- Whether the five Buzz-owned Drop-guard examples chosen here are the most
  representative set, versus e.g. `AcpClient`'s or `HarnessRelay`'s own `Drop`
  impls (already narrated by #1118 for the shutdown angle) — this node
  deliberately picks request/connection-scoped examples that recur many times
  per process lifetime, to stay distinct from #1118's process-exit-scoped
  narration.

LEFT OUT

- Any change to runtime code, tests, or the guard types themselves.
- Re-narrating #1118's shutdown drain/backstop sequencing, or #1120's startup
  ordering — both already cover process-lifetime teardown/boot; this node
  covers the shorter-lived, per-request/per-connection resource release that
  happens continuously within a running process's lifetime.
- A `relationships` edge to `layers-lifecycle-graceful-shutdown` or
  `layers-lifecycle-startup` unless a re-check at commit time shows either
  actually resolves on `origin/launchpad`.
