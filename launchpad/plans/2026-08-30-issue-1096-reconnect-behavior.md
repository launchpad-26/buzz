# Plan: issue #1096 — Redis reconnect-behavior corpus node

Issue #1096 (launchpad-26/buzz), parent PRD #610 ("data and storage layer corpus
exists")

Stated size: single corpus document task, no explicit Size line in the issue body -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/layers/data/redis/reconnect-behavior.md` does not exist on
  `origin/launchpad` (confirmed: `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` lists only `architecture/containers/redis.md` under a Redis
  path, plus `test -f` in this worktree comes back absent).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 members and no
  dedicated "layers" sub-taxonomy; per this batch's disclosed precedent (connection-pool
  #1092, dedicated-pubsub-connection #1093, both read directly from PR #1878's branch
  `task/610-batch-7-data-storage`, commit `b3ba50fc59b00bdb8d37374bbe52bc0091b504fc`,
  neither merged), every `layers/data/...` node in this batch uses `type: layers`,
  overriding `templates/datastore.md`'s own worked reasoning that a real datastore
  instance takes `type: architecture`. This override is disclosed here and in the node's
  own evidence ledger, not silently applied.
- `launchpad/docs/corpus/architecture/containers/redis.md` (id
  `architecture-containers-redis`) is already merged on `origin/launchpad` and states, in
  its own evidence ledger, that the three subscriber loops "each reconnect with
  exponential backoff (1s to 30s) and run forever once spawned" — a valid `part-of`
  relationship target, since it already resolves in the corpus tree at the merge target.
- The sibling `dedicated-pubsub-connection.md` (#1093, unmerged PR #1878) already
  documents, in exhaustive per-connection detail, the three dedicated pub/sub
  connections' own reconnect-with-backoff loops (`BACKOFF_INITIAL_SECS = 1`,
  `BACKOFF_MAX_SECS = 30`, doubling, reset on clean disconnect) and their per-connection
  failure/backstop behavior (DB backstop for cache-invalidation and conn-control; no
  backstop found for the channel/global fan-out path). This was read directly from the
  PR branch this session, not assumed. Redocumenting that same connection-by-connection
  detail here would duplicate #1093's canonical content, which this node's own DoD
  ("links relevant ... neighboring corpus nodes without duplicating their canonical
  content") forbids.
- Direct inspection this session of `deadpool-redis` 0.23.0's vendored source
  (`.hermit/rust/registry/.../deadpool-redis-0.23.0/src/lib.rs`) and `deadpool` 0.13.0's
  vendored source (`.../deadpool-0.13.0/src/managed/{pool,config}.rs`) establishes a
  second, structurally different reconnect mechanism that neither #1092 nor #1093
  documents: the shared pooled connection has no background retry loop at all. Instead,
  `Manager::recycle` runs an `UNWATCH`+`PING` health check on every `Pool::get()`
  checkout; a failed recycle silently drops the connection and falls through to
  `Manager::create` (`client.get_multiplexed_async_connection()`), attempted fresh,
  inline, on that same caller's request. `PoolConfig::new(max_size)` (used verbatim in
  `crates/buzz-relay/src/main.rs`) sets `Timeouts::default()` — `create`/`recycle`/`wait`
  all `None` — so nothing in the pool itself bounds how long that inline reconnect
  attempt can take. This is the genuinely new, cross-cutting content this node exists to
  add: the pooled path's reconnect is a passive, no-backoff, per-request retry, unlike
  the dedicated connections' active background backoff loop.
- A direct `grep -rn "ConnectionManager"` across `crates/` this session found no use of
  `redis::aio::ConnectionManager` (the type the workspace's `redis = "1.0"` dependency's
  enabled `connection-manager` feature provides) anywhere in the codebase — every
  `ConnectionManager` hit is an unrelated, same-named `buzz-relay::state::ConnectionManager`
  (the WebSocket connection registry). This resolves a gap #1093's own "Expected but not
  verified" section left open ("whether `redis`'s `connection-manager` feature ... is
  actually in use on the pub/sub path specifically ... was not traced into the `redis`
  crate's own implementation") — traced here, for both the pooled and dedicated paths:
  neither uses it. The feature is enabled but dead at the workspace level.

STEP 1 — Draft the corpus node body and front matter [independent]

<- RUNS HERE

Write `launchpad/docs/corpus/layers/data/redis/reconnect-behavior.md` as the
general/cross-cutting reconnect node: what happens, across *all* of Buzz's Redis
connections (not just the three dedicated ones #1093 already covers in detail), when
Redis becomes unreachable and comes back. Structure: Purpose & scope (state explicitly
that this node is the cross-cutting synthesis, name #1092/#1093 as the two
connection-type-specific siblings it does not duplicate, per the batch dispatch note
that #1093 covers backstop behavior for two of the three dedicated connections but not a
pool-level story), Two reconnect mechanisms compared (pooled: passive/no-backoff/
per-request via `Manager::recycle`+`Manager::create`, sourced from the vendored
`deadpool-redis`/`deadpool` crate source read this session; dedicated: active/
exponential-backoff background loops, summarized at one level of abstraction and
cross-referenced to #1093 by name/path, not re-detailed), the resolved
`connection-manager`-feature gap (dead code path, both connection types), consequence
for callers (no pool-level timeout means an admission-critical `pool.get()` call in
`nip98_replay.rs`/`rate_limiter.rs` has no bound of its own; the readiness probe imposes
its own 2s `tokio::time::timeout` around `state.redis_pool.get()`, verified directly in
`crates/buzz-relay/src/router.rs`, but that bound is the caller's, not the pool's),
tenancy/security boundary (defer to `architecture-containers-redis` and the unmerged
`key-namespacing`/#1094 by name — this node's subject is connection recovery, not key
scoping), Links (schema/migrations/code/tests — Redis has no DDL; cite the vendored
crate source paths plus the Rust modules and tests already identified), and Scope and
omissions naming #1092/#1093/#1094/#1080 as neighbors by issue number, none merged, none
targetable as a `relationships` edge yet. Front matter: `id:
layers-data-redis-reconnect-behavior`, `type: layers` (disclosed override, see ALREADY
TRUE), `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator]`,
one `relationships` entry (`part-of` -> `architecture-containers-redis`), and an
`evidence` ledger citing only sources actually opened this session: the vendored
`deadpool-redis-0.23.0` and `deadpool-0.13.0` source files, `crates/buzz-relay/src/main.rs`,
`crates/buzz-relay/src/router.rs`, `crates/buzz-relay/src/admission.rs`,
`crates/buzz-pubsub/src/nip98_replay.rs`, `crates/buzz-pubsub/src/subscriber.rs`,
`crates/buzz-pubsub/src/cache_invalidation.rs`, `crates/buzz-pubsub/src/conn_control.rs`,
`Cargo.toml` (workspace), `Cargo.lock`, and
`launchpad/docs/corpus/architecture/containers/redis.md`. Cover every DoD bullet:
authoritative/derived/cache/transport classification (inherit and cite
`architecture-containers-redis`'s existing classification — transport/coordination, not
durable — rather than re-arguing it, since this node's own subject is connection
recovery, not data ownership), owned data/key access patterns/lifecycle/consistency
semantics (no data owned by a connection itself; consistency-after-reconnect differs by
mechanism — pool: a fresh connection carries no session state to reconcile; dedicated:
resubscription from local state, per #1093, referenced not repeated), tenancy/security
boundaries (named as out of scope, owned by `architecture-containers-redis` and
`key-namespacing`/#1094), and failure behavior (the core of this node: two distinct
recovery shapes, the no-timeout gap, and the resolved `connection-manager` question).

done when: the file exists at the target path, its YAML front matter parses, every DoD
bullet from the issue body is addressed by a labeled section or explicit
scope-and-omissions entry, and no paragraph restates #1093's own connection-by-connection
mechanics in the same depth #1093 already gives them.

STEP 2 — Validate against the schema [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree root.
Fix any reported error (schema violation, broken relationship target, duplicate id,
invalid source path) and re-run until it exits 0.

done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3 — Earn the commit gate and commit [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole, unpiped command in its own tool call and confirm `OK`. Then, in
a separate tool call, `git add` the plan file and the new corpus document and `git
commit -s` with message `docs(corpus): redis reconnect behavior concept (#1096)`.

done when: the unittest run reports `OK` and `git log -1` on the worktree branch shows
one new commit containing exactly the plan file and the target corpus document.

STEP 4 — Self-review against the DoD [needs 3]

Re-read `git diff origin/launchpad -- .` line by line against issue #1096's Definition
of Done checklist. Confirm every evidence entry's citation was actually opened this
session and supports its stated claim. Confirm no second hand-authored canonical corpus
document was created. Confirm the node does not silently duplicate #1093's
connection-by-connection content rather than referencing it in prose. Re-run
`validate.py` to confirm it still exits 0 after any fix made during review.

done when: the diff review is complete, `validate.py` still exits 0, and no second
canonical document exists in the diff.

PARALLEL

None of these steps parallelize — each depends on the previous step's artifact
(document -> schema validation -> gate-earning commit -> self-review of the committed
diff). This is a single-document, single-worktree task with no independent sub-tasks to
fan out.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit
  (STEP 2) and again after self-review (STEP 4).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must report `OK`, run bare and unpiped in its own tool call, before
  `git commit -s` (STEP 3) — this is the gate `verify-gate.sh` recognizes; `validate.py`
  alone does not earn the stamp.
- No push and no PR — this worktree stops at a committed, self-reviewed branch per the
  batch orchestration split (someone else bundles this branch with its siblings).

BUDGET

Single corpus document, roughly 150-220 lines of Markdown plus front matter — shorter
than #1092/#1093's ~250-450 lines, since this node is a synthesis that references its
siblings rather than re-deriving their per-connection detail. One commit. No code
changes; the `deadpool-redis`/`deadpool` vendored-source reads are research, not
modification.

OPEN

- Whether `architecture-containers-redis`'s own "each reconnects with exponential
  backoff (1s to 30s)" summary sentence should eventually link to this node once merged —
  left for a future editorial pass, not decided here (editing that already-merged node
  would itself be a second hand-authored canonical-document change, out of scope per the
  issue's own DoD).
- Whether the pool's absent create/recycle timeout is a deliberate choice or an
  unaddressed gap is not established by anything in the repository at the recorded
  revision — named as a real gap in the node's own Scope and omissions, not resolved by
  guessing.

LEFT OUT

- No relationship edges to `layers/data/redis/connection-pool` (#1092),
  `dedicated-pubsub-connection` (#1093), `key-namespacing` (#1094), or
  `layers/data/postgres/connection-pool` (#1080) — none exist on `origin/launchpad` at
  this node's authoring time; declaring an edge would validate locally (this worktree
  branched from a commit that does not carry any of them) but hard-fail CI against the
  real merge target. All four are named in prose instead.
- No redocumentation of the three dedicated connections' own backoff/resubscription/
  backstop mechanics at #1093's level of detail — cross-referenced by name and path
  instead, per this node's own duplication-avoidance DoD bullet.
- No edit to `architecture/containers/redis.md` — a second hand-authored canonical
  document is explicitly out of scope per the issue body's own "Out of scope" section.
- No promotion of `status` to `active` — an authoring agent does not self-promote a
  draft node; that is a human call made later.
- No push, no PR — explicitly deferred to the batch owner per this task's own
  instructions.
