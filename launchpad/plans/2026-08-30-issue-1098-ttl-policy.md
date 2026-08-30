Issue #1098 — task: document layers/data/redis/ttl-policy.md

Stated size: not specified in issue #1098 itself -> cap: 5 steps (per the
corpus-batch-author dispatch brief for this overnight run).

ALREADY TRUE  node.schema.json, launchpad/docs/corpus/AGENTS.md,
  launchpad/docs/corpus/standards/taxonomy.md and
  launchpad/docs/corpus/architecture/containers/redis.md (id
  architecture-containers-redis, status: draft) are merged on origin/launchpad
  (confirmed at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5). The target file
  launchpad/docs/corpus/layers/data/redis/ttl-policy.md does not exist, and no
  layers/ subtree exists on origin/launchpad at all — this is the first node under
  it. templates/datastore.md and templates/reference.md are both merged and were
  both read in full to choose between them. Per this batch's own precedent, every
  layers/data/... document uses type: layers regardless of what a chosen template's
  worked example suggests, and no layers/data/redis/* sibling is merged yet (several
  exist only in unmerged sibling PRs), so no relationship edge may target one.

STEP 1 [independent]  Gather evidence: grep the repository for actual Redis TTL/expiry call sites
        (EXPIRE, PEXPIRE, SET ... EX, TTL) and read each in full: presence.rs (SET EX
        180, PRESENCE_TTL_SECS), rate_limiter.rs + admission.rs (INCR + conditional
        EXPIRE Lua script, self-repair on missing TTL, fail-closed on Redis error),
        nip98_replay.rs in both buzz-pubsub and buzz-auth (SET NX EX,
        DEFAULT_REPLAY_TTL_SECS/MAX_REPLAY_TTL_SECS clamp, explicit fail-closed
        comments), tunnel/directory.rs (PEXPIRE via Lua, DEFAULT_LEASE_TTL,
        community-scoped key shape) and tunnel/reliable.rs (DEFAULT_RENEW_INTERVAL,
        the heartbeat that keeps a lease alive). Also read cache_invalidation.rs far
        enough to confirm its "10s TTL" is a local in-process moka cache, not a Redis
        key, so it can be explicitly scoped out. Cross-check fail-open vs fail-closed
        behavior at each call site (connection.rs, handlers/event.rs, admission.rs,
        api/bridge.rs) rather than assuming it from a module doc comment.
        done when: every claim the body will make has an opened source noted for its
        evidence entry.

STEP 2 [needs 1]  Write front matter (id: layers-data-redis-ttl-policy, type: layers — per the
        batch override, disclosed against standards/taxonomy.md's own disclosure
        requirement — status: draft, origin: launchpad, audiences: [agent, developer,
        operator, reviewer], one part-of relationship to architecture-containers-redis,
        no other relationships) and the body: purpose/scope naming this as an
        operational-characteristics drill-down (the TTL/retention slice of Redis,
        not the whole datastore, which architecture-containers-redis already covers
        at container depth), a table of every TTL-governed key namespace (owned
        data, key pattern, default/clamped duration, refresh mechanism), lifecycle/
        consistency semantics (what happens on expiry per namespace), tenancy/
        security boundaries (community-scoped vs. operator-global keys), a fail-open/
        fail-closed table per mechanism with citations, a links-not-DDL pointer to
        the actual source files/Lua scripts, and a scope-and-omissions section naming
        what this node does not cover (the Redis container's own existence/technology;
        the unrelated local moka cache TTL) plus what was expected but not verified
        (e.g. whether check_ip_connection's IP-scoped rate limit has any live call
        site — none was found).
        done when: every DoD bullet in issue #1098 has a corresponding body section.
        ← RUNS HERE

STEP 3 [needs 2]  Validate: python3 launchpad/project-intelligence/corpus/validate.py exits 0.
        Fix and re-run until clean.
        done when: exit code 0 against the full corpus tree including the new file.

STEP 4 [needs 3]  Run the corpus unittest suite as its own bare, unpiped command
        (python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py") and confirm OK, then commit the plan and the node together in
        a separate call. Do NOT push and do NOT open a PR — this worktree's branch is
        bundled by a later batch orchestration step.
        done when: `git log -1` shows both files staged in one signed-off commit, and
        the unittest run reported OK before that commit was made.

PARALLEL  None — one target file, one plan file, strictly sequential; no dependency
          on sibling layers/data/redis/* tasks running in other worktrees this same
          overnight batch.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (this session).
          python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
          -p "test_*.py" (this session, bare command, before commit).
          review-adjudicate and the cross-model final-review pass are deferred to the
          batch owner's later bundling/review step — not run here, per the overnight-
          batch instructions.

BUDGET    STEP 2 is where time goes: honestly separating FACT (opened and read) from
          INFERENCE (reasoned, needs confidence) for claims like "Redis's TTL-backed
          keys are non-authoritative/derived state" — that classification is drawn
          from several FACTs (Postgres holds the durable event/user/channel record;
          every Redis value here is either a heartbeat, a counter, a replay marker or
          a lease) but is itself a reasoned inference, not a fact in its own right.

OPEN      The issue's DoD checklist ("states whether the store is authoritative,
          derived, cache or transport... names tenancy/security boundaries and
          failure behavior") reads as boilerplate shared across this feature's
          layers/data/* tasks rather than written specifically for a cross-cutting
          TTL-policy document — the same stale-DoD pattern the datastore.md/
          reference.md/policy.md templates each already flagged for their own
          issues. This plan answers it as best fits a TTL-scoped node rather than
          treating the boilerplate as a literal per-field checklist for a full
          datastore document. Whether a future reviewer wants a separate
          layers/data/redis/datastore.md covering the full store profile (technology,
          attachment, complete schema/namespace inventory) is out of scope here and
          not resolved.

LEFT OUT  Any relationship edge to a layers/data/redis/* sibling — none is merged on
          origin/launchpad. Any attempt to reconcile or extend the
          #[datastore_span] Postgres-only tracing gap noted while reading
          buzz-datastore-tracing — pre-existing and out of scope per the issue's own
          "changing runtime product behavior" exclusion. Coverage of the local moka
          in-process cache TTL in cache_invalidation.rs beyond naming it as an
          explicit non-goal, since it is not a Redis key.
