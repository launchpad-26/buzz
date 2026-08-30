# Issue #1092: docs(corpus) — layers/data/redis/connection-pool.md

Stated size: issue #1092 states no explicit step/size limit of its own.  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`). `launchpad/docs/corpus/architecture/containers/redis.md`
(id `architecture-containers-redis`) is also merged there and documents the full Redis
container (technology, five job areas, deployment/data/security implications) — this
node zooms into one axis that document deliberately keeps to one line: the shared
`deadpool_redis::Pool` itself. No `layers/` directory exists anywhere on
`origin/launchpad` yet — this is the first node under it. The target file
`launchpad/docs/corpus/layers/data/redis/connection-pool.md` does not exist. Sibling
tasks in this same batch — `layers/data/redis/channel-pubsub.md` (#1091),
`dedicated-pubsub-connection.md` (#1093), `key-namespacing.md` (#1094) — and the
Postgres analogue `layers/data/postgres/connection-pool.md` (#1080) are being authored
in parallel isolated worktrees and are **not** present on `origin/launchpad`, so no
`relationships[].target` may name any of their ids. `node.schema.json`'s `type` enum has
no dedicated "layer" member finer than `architecture`; this batch's own precedent
overrides `templates/datastore.md`'s own guidance (a real instance takes
`type: architecture`) to `type: layers` for every `layers/data/...` document — this will
be disclosed as an explicit override in the new node's scope-and-omissions section, per
`standards/taxonomy.md`'s requirement to disclose an imperfect or overridden fit rather
than pick silently.

STEP 1 [independent] — gather evidence (already done in this session, recorded here for
the record): read `crates/buzz-relay/src/main.rs` (pool construction at
`deadpool_redis::Config`, subscriber spawns, pool-metrics gauge loop and its
`BUZZ_POOL_METRICS_INTERVAL_SECS` poll), `crates/buzz-relay/src/config.rs`
(`redis_pool_size`/`redis_url` fields and the `BUZZ_REDIS_POOL_SIZE` env
parse-and-fallback, plus its own unit test), `crates/buzz-relay/src/state.rs`
(`AppState.redis_pool` wiring into `RedisNip98ReplayGuard`/`RedisRateLimiter`),
`crates/buzz-relay/src/router.rs` (`readiness_handler`'s 2s-timeout three-way check),
`crates/buzz-relay/src/admission.rs` and its callers in `crates/buzz-relay/src/api/bridge.rs`
and `crates/buzz-relay/src/connection.rs` (fail-closed behavior on `AdmissionError::Unavailable`),
`crates/buzz-pubsub/src/lib.rs` (`PubSubManager`'s pooled vs. dedicated-connection split,
module doc diagram), `crates/buzz-pubsub/src/rate_limiter.rs` and `nip98_replay.rs` (both
acquire from the shared pool and propagate pool-acquire failure as an error, with
`nip98_replay.rs` carrying an explicit "MUST fail closed" comment), `crates/buzz-pubsub/Cargo.toml`,
root `Cargo.toml` (`redis`/`deadpool-redis` crate versions), `.env.example`, and
`docker-compose.yml`.
done when: every source path above has been opened and its relevant lines identified for
citation (confirmed complete in this session).

STEP 2 [needs 1] — write front matter (id `layers-data-redis-connection-pool`, type `layers`,
status `draft`, origin `launchpad`, audiences `agent`/`developer`/`operator`) and one
evidence-ledger entry per substantive claim, classified honestly (FACT for opened
source, INFERENCE with confidence for reasoned synthesis, TEAM_KNOWLEDGE with
`provided_by` for the issue's own DoD requirements), plus exactly one commit-only FACT
recording the revision. RUNS HERE.
done when: the front-matter block parses as YAML, every required schema field is
present, and every evidence entry's `entry_class` combination matches the schema's
required/forbidden fields for that class.

STEP 3 [needs 2] — write the body: purpose/scope naming this as the connection-pool axis of the
already-merged `architecture-containers-redis` node (and explicitly out of scope for the
not-yet-existing channel-pubsub/dedicated-pubsub-connection/key-namespacing siblings);
technology & attachment profile (`deadpool_redis` 0.23, `redis` 1.0, `REDIS_URL`/`BUZZ_REDIS_POOL_SIZE`,
default size 16 vs. deadpool's own `CPU_COUNT * 2` default); pooled-vs-dedicated consumer
split (rate limiter, replay guard, presence/publish/cache-invalidation/conn-control
PUBLISH all draw from the pool; the three long-running SUBSCRIBE loops each open their
own non-pooled connection because a pooled connection cannot hold subscribe state);
lifecycle/health/metrics (startup failure is fatal to relay boot; `readiness_handler`'s
2s-timeout `pool.get()` check; the `buzz_redis_pool_*` gauges polled every
`BUZZ_POOL_METRICS_INTERVAL_SECS`, default 10s); classification of the store the pool
fronts as coordination/transport rather than authoritative/durable (citing
`architecture-containers-redis`'s own TTL/fire-and-forget evidence directly, opened
independently rather than merely re-cited); tenancy/security boundary (every pool-drawn
command operates on community-prefixed keys except the deliberately operator-global IP
rate limiter; `rediss://` TLS via the `rustls` crypto-provider install in staging/prod);
failure behavior (fail-closed on `RedisNip98ReplayGuard`/`RedisRateLimiter` pool-acquire
failure, traced through to the WebSocket and HTTP admission call sites returning 503/
rejection rather than allowing the request through); and a scope-and-omissions section
disclosing the `type: layers` override, the three sibling-task boundaries, and what was
expected but not verified (e.g., ElastiCache-side pool/connection limits, which this
repository's own code does not configure).
done when: every DoD bullet in issue #1092's body has a corresponding section or
sentence in the document, and every substantive claim in the body has a matching
evidence-ledger entry.

STEP 4 [needs 3] — validate: run
`python3 launchpad/project-intelligence/corpus/validate.py`, fix any reported error, and
re-run until it exits 0.
done when: the command's exit status is 0.

STEP 5 [needs 4] — commit: run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call to earn the verification stamp, then in a separate
call stage and commit this plan file and the new document with `git commit -s`.
done when: the unittest run reports OK and `git log -1` shows the new commit on
`task/1092-redis-connection-pool` containing exactly the plan file and the one new
corpus document.

PARALLEL: none — single file, single task, run serially in this isolated worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report OK, run bare and unpiped, to earn the commit hook's verification stamp.
review-adjudicate and any cross-model review pass are deferred to the batch owner's
bundling/review step — not run here.

BUDGET: single document, no code or test changes, evidence already gathered in this
session before this plan was written.

OPEN: whether `squareup/block-coder-tf-stacks` or a separate stack configures
ElastiCache's own connection/backlog limits is not established anywhere in this
repository (the same gap `architecture-containers-redis` already names) — recorded as a
scope-and-omissions gap, not resolved here. Whether the `BUZZ_POOL_METRICS_INTERVAL_SECS`
default (10s) or the `BUZZ_REDIS_POOL_SIZE` default (16) were deliberately sized against
any measured load, versus chosen as a reasonable starting point, is not established from
the code alone and is not claimed as more than what the source states.

LEFT OUT: no runtime/product code change; no second canonical document; no
`relationships[].target` naming any of the three same-batch sibling tasks or the
Postgres analogue (#1080), none of which exist on `origin/launchpad`; a `part-of` edge
to the already-merged `architecture-containers-redis` **is** in scope and will be added,
per `templates/datastore.md`'s own relationships guidance for an instance-to-container
edge once the container node exists; no per-type `layers` template exists yet, so this
node is written against `node.schema.json` plus the closest-fitting existing template
(`templates/datastore.md`) rather than a template built for `type: layers` specifically —
disclosed, not silently assumed away.
