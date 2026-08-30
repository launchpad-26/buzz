# Plan: issue #1093 — Redis dedicated pub/sub connection corpus node

Issue #1093 (launchpad-26/buzz), parent PRD #610 ("data and storage layer corpus
exists")

Stated size: single corpus document task, no explicit Size line in the issue body -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/layers/data/redis/dedicated-pubsub-connection.md` does not
  exist on `origin/launchpad` (confirmed: `git ls-tree` of that path and a direct
  `test -f` in this worktree both come back empty/absent).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 members and no
  dedicated "layers" sub-taxonomy; per the batch's own precedent (channel-pubsub #1091,
  connection-pool #1092, key-namespacing #1094 — none merged yet), every
  `layers/data/...` node in this batch uses `type: layers`, not whichever type a
  template's own worked example suggests for a "real instance" (`datastore.md`'s own
  worked reasoning says `type: architecture` for a real datastore instance — this is a
  deliberate, disclosed override of that reasoning, not an oversight).
- `launchpad/docs/corpus/architecture/containers/redis.md` (id
  `architecture-containers-redis`) is already merged on `origin/launchpad` and already
  states, in one summary sentence, the exact mechanism this node exists to expand:
  "`PubSubManager`'s SUBSCRIBE/PSUBSCRIBE loops use their own dedicated (non-pooled)
  Redis connections rather than the shared pool, because a pooled connection cannot
  hold subscribe state." This is a valid `part-of` relationship target — it already
  resolves in the corpus tree at the merge target.
- `crates/buzz-pubsub/src/lib.rs`'s own module doc, `crates/buzz-pubsub/src/subscriber.rs`,
  `crates/buzz-pubsub/src/cache_invalidation.rs` and `crates/buzz-pubsub/src/conn_control.rs`
  confirm the dedicated-connection claim directly and go further: there are **three**
  independent dedicated (non-pooled) `redis::Client::open(...).get_async_pubsub()`
  connections spawned per relay pod (one per subscriber loop — channel/global event
  fan-out, cross-pod cache-invalidation, cross-pod conn-control), none constructed from
  `deadpool_redis::Pool`, each with its own reconnect-with-backoff loop
  (1s -> 2s -> 4s -> ... -> 30s max) and its own failure/backstop behavior. This was
  inspected directly in this worktree, not assumed from the issue body.
- No `layers/data/redis/*` sibling node (channel-pubsub, connection-pool,
  key-namespacing) exists on `origin/launchpad`, so no relationship may target any of
  them — the batch dispatch brief for #1093 states this explicitly and it was
  independently confirmed by `git ls-tree`.

STEP 1 — Draft the corpus node body and front matter [independent]

<- RUNS HERE

Write `launchpad/docs/corpus/layers/data/redis/dedicated-pubsub-connection.md` following
`launchpad/docs/corpus/templates/datastore.md`'s required-section shape (Purpose & scope,
Technology & attachment profile, Owned-data/access-pattern summary, Operational
characteristics/failure behavior, Evidence expectations, Scope and omissions), scoped
down to the one facet this node covers — the dedicated-connection pattern — not a full
Redis datastore inventory (that is `architecture-containers-redis`'s job, already merged,
which this node zooms into and does not duplicate). Front matter: `id:
layers-data-redis-dedicated-pubsub-connection`, `type: layers` (disclosed override, see
ALREADY TRUE), `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
operator]`, one `relationships` entry (`part-of` -> `architecture-containers-redis`), and
an `evidence` ledger citing only sources actually opened this session: `crates/buzz-pubsub/src/lib.rs`,
`crates/buzz-pubsub/src/subscriber.rs`, `crates/buzz-pubsub/src/cache_invalidation.rs`,
`crates/buzz-pubsub/src/conn_control.rs`, `crates/buzz-pubsub/src/error.rs`,
`crates/buzz-pubsub/Cargo.toml`, `crates/buzz-relay/src/main.rs`, `crates/buzz-relay/src/config.rs`,
`.env.example`, `docker-compose.yml`, `Cargo.toml` (workspace), and
`launchpad/docs/corpus/architecture/containers/redis.md` itself (for the container-level
summary this node expands). Mention channel-pubsub/connection-pool/key-namespacing by
name in prose (per the batch brief) without declaring relationship edges to them. Cover
every DoD bullet from the issue body: authoritative/derived/cache/transport
classification (Redis pub/sub here is transport, never authoritative — no durable state,
messages lost if no dedicated connection is subscribed at publish time), owned
data/key access patterns/lifecycle/consistency semantics (per-topic dynamic SUBSCRIBE vs.
fixed-pattern PSUBSCRIBE, local `desired_topics` refcount map as source of truth across
reconnects), tenancy/security boundaries and failure behavior (community-scoped channel
naming, exponential-backoff reconnect, no message buffering across a reconnect gap,
DB-backstopped fire-and-forget publishes for two of the three loops), and links to
schema/migrations/code/tests rather than copied DDL (Redis has no migrations; cite the
actual Rust modules and the `#[ignore = "requires Redis"]` integration tests in
`crates/buzz-pubsub/src/lib.rs`).

done when: the file exists at the target path, its YAML front matter parses, and every
DoD bullet from the issue body is addressed by a labeled section or explicit
scope-and-omissions entry.

STEP 2 — Validate against the schema [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree root.
Fix any reported error (schema violation, broken relationship target, duplicate id,
invalid source path) and re-run until it exits 0.

done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3 — Earn the commit gate and commit [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole, unpiped command in its own tool call and confirm `OK`. Then, in
a separate tool call, `git add` the plan file and the new corpus document and `git
commit -s` with message `docs(corpus): redis dedicated pubsub connection concept
(#1093)`.

done when: the unittest run reports `OK` and `git log -1` on the worktree branch shows
one new commit containing exactly the plan file and the target corpus document.

STEP 4 — Self-review against the DoD [needs 3]

Re-read `git diff origin/launchpad -- .` line by line against issue #1093's Definition
of Done checklist. Confirm every evidence entry's citation was actually opened this
session and supports its stated claim. Confirm no second hand-authored canonical corpus
document was created (only the plan file and the one target document should appear in
the diff, plus the target document should be the sole hand-authored doc under
`launchpad/docs/corpus/`). Re-run `validate.py` to confirm it still exits 0 after any
fix made during review.

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

Single corpus document, ~150-250 lines of Markdown plus front matter. One commit. No
code changes, no test changes beyond reading existing `#[ignore = "requires Redis"]`
tests as evidence (not adding new ones — this is a documentation task).

OPEN

- Whether `layers-data-redis-dedicated-pubsub-connection`'s eventual sibling nodes
  (channel-pubsub #1091, connection-pool #1092, key-namespacing #1094) will want
  `references` edges to this node once merged — left for whoever authors those, since
  none exists yet to declare an edge toward.
- Whether the container-level `architecture-containers-redis` node's own "Ownership
  boundary" paragraph should be trimmed once this node exists, to avoid the two nodes
  drifting apart on the same fact — left to a human editorial pass, not decided by this
  task (out of scope per the issue's own "no second hand-authored canonical document"
  DoD bullet, since editing `redis.md` would itself be a second hand-authored change to
  a different canonical node).

LEFT OUT

- No relationship edges to `layers/data/redis/*` siblings — none exist on
  `origin/launchpad` yet, per the batch brief and confirmed by `git ls-tree`; declaring
  one would validate locally but hard-fail CI against the real merge target.
- No edit to `architecture/containers/redis.md` — a second hand-authored canonical
  document is explicitly out of scope per the issue body's own "Out of scope" section.
- No promotion of `status` to `active` — an authoring agent does not self-promote a
  draft node; that is a human call made later, per `corpus-batch-author`'s own stated
  boundary.
- No push, no PR — explicitly deferred to the batch owner per this task's own
  instructions.
