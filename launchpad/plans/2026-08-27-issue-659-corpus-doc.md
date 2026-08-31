Plan: issue #659 -- corpus doc for architecture/containers/redis.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged and
authoritative on `launchpad` at a44cf52fc740ebebbdd671427480d14f0bce0115; the target file
launchpad/docs/corpus/architecture/containers/redis.md does not exist yet.

STEP 1 (RUNS HERE): gather evidence -- read buzz-pubsub's crate (lib.rs, presence.rs,
topic.rs, conn_control.rs, nip98_replay.rs, rate_limiter.rs, cache_invalidation.rs),
buzz-relay's wiring in main.rs and state.rs (redis pool construction, PubSubManager,
readiness handler), .env.example, docker-compose.yml, Justfile, TESTING.md, and
ARCHITECTURE.md's existing Redis section for cross-reference (not duplication).

STEP 2: write front matter (id: architecture-containers-redis, type: architecture,
status: draft, origin: launchpad, audiences: [agent, developer, operator]) plus a body
covering: container responsibility/technology/ownership boundary; inbound/outbound
interfaces and directly connected containers; deployment/data/security implications;
links to implementation paths without duplicating their detail; a scope-and-omissions
section naming what was expected but not verified.

STEP 3: run python3 launchpad/project-intelligence/corpus/validate.py against the full
corpus tree (including the new file) until it exits 0.

STEP 4: run python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py" as the sole prior command to earn the commit verification stamp, then
commit the plan + new document in a separate tool call.

PARALLEL: none -- single file, single worktree.

GATES: validate.py must exit 0 locally before commit. review-adjudicate and the
cross-model final-review pass are explicitly deferred to the batch owner's morning
review of the 47-issue overnight batch (#608) and are not run in this task.

BUDGET: single document, one sitting -- no multi-session budget needed.

OPEN: ARCHITECTURE.md line 390 currently claims "No Redis-backed rate limiter exists
anywhere in the codebase," but crates/buzz-pubsub/src/rate_limiter.rs's
`RedisRateLimiter` implements buzz-auth's `RateLimiter` trait and is wired into
`AppState.admission_rate_limiter` in state.rs -- that reference doc has drifted from
current code. Per corpus precedence (ADR-0029), executable evidence (the code) outranks
the stale prose, so the new node states the current wired behavior and cites the code
directly rather than ARCHITECTURE.md for that specific claim. This drift is not this
task's to fix in ARCHITECTURE.md; it is noted here and in the new node's evidence rather
than silently resolved elsewhere. No other real ambiguity in the issue's DoD was found.

LEFT OUT: no `relationships` entries -- no other architecture/containers sibling node is
merged on `launchpad` yet (0 of 26 templates merged per the batch context), so there is
no id to point at; the first sibling to merge is the moment to add edges, per
AGENTS.md's own guidance and the precedent set by corpus-standard-confidence.md. No
change to ARCHITECTURE.md's stale claim (out of scope for this task, per the issue's own
"Out of scope" list barring "while here" cleanup).
