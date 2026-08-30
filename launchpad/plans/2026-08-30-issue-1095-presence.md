# Issue #1095 — layers/data/redis/presence.md

Stated size: none given (single corpus document, batch task)  →  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md`, and
`launchpad/docs/corpus/architecture/containers/redis.md` (id `architecture-containers-redis`,
type `architecture`, status `draft`) are present at `origin/launchpad` HEAD
(338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5). `launchpad/docs/corpus/layers/data/redis/presence.md`
does not exist yet. No `layers/data/redis/*` sibling node (channel-pubsub, connection-pool,
dedicated-pubsub-connection, key-namespacing, role) is merged on `origin/launchpad` — those
exist only on local/unmerged branches (per batch precedent) — so none is a valid
`relationships` target. Prior batch precedent (already-merged/in-flight `layers/data/redis/*`
docs) fixes `type: layers` for this whole subtree, overriding `templates/datastore.md`'s own
worked-example type (`architecture`, reasoned for a real datastore instance in general); this
override is disclosed in the evidence ledger per `standards/taxonomy.md`'s step-4 disclosure
rule (pick the closer fit, name the gap in scope-and-omissions).

STEP 1  [independent] Gather evidence: read `crates/buzz-pubsub/src/presence.rs` in full (key format
        `buzz:{community}:presence:{pubkey_hex}`, `SET ... EX 180`/`GET`/`DEL`/`MGET`,
        `PRESENCE_TTL_SECS = 180 = 3×60s heartbeat`). Trace every caller: `buzz-relay`'s
        `handle_ephemeral_event` (kind:20001 `KIND_PRESENCE_UPDATE`, `handlers/event.rs`
        ~L813-847 — "online"/"away" → `set_presence`, "offline" → `clear_presence`),
        `connection.rs` ~L303-314 (clean-disconnect `clear_presence`, only when no other
        connection remains for that pubkey in the community), and `api/bridge.rs`'s
        `synthesize_presence` (~L2049-2119 — intercepts REQ/query filters for kind:20001 or
        kind:40902 `KIND_PRESENCE_SNAPSHOT` with `authors`, calls `get_presence_bulk`, and
        signs synthetic relay events instead of hitting Postgres, because ephemeral events are
        never stored). Cross-check against `architecture-containers-redis`'s existing
        one-line presence row and its INFERENCE that every `buzz-pubsub` Redis write is
        TTL-bounded or transient (no durable backstop for presence specifically — unlike
        cache-invalidation/conn-control, a missed `clear_presence` self-heals only via the
        180s TTL, not a Postgres fallback). Check `buzz-core::TenantContext` for the
        community-scoping mechanism the key format relies on. Confirm no `#[datastore_span]`
        instrumentation exists on this path (established already for the whole crate in
        `architecture-containers-redis`'s evidence ledger). ← RUNS HERE
        done when: every claim below is backed by an actual line read in `presence.rs`,
        `event.rs`, `connection.rs`, or `api/bridge.rs` — not inferred from a name alone.

STEP 2  [needs 1] Write front matter: id `layers-data-redis-presence`, type `layers`
        (override, disclosed), status `draft`, origin `launchpad`, audiences
        `[agent, developer, operator, reviewer]`, one `relationships` entry —
        `part-of` → `architecture-containers-redis` (the only merged, on-topic target) —
        and no other edges (siblings unmerged per ALREADY TRUE). Follow
        `templates/datastore.md`'s required-section shape, adapted to the issue's own DoD
        bullets: purpose/scope naming this as one row of `architecture-containers-redis`'s
        table; authoritative/derived/cache/transport classification (derived+cache — Redis
        is not the source of truth; online/offline status is reconstructable from live
        connection state, and REQ synthesis reads it as a fast-path cache rather than
        Postgres); owned data (one key pattern, no schema/namespace inventory beyond it);
        key access pattern (SET EX/GET/DEL/MGET, who calls each and why); lifecycle/retention
        (180s TTL = 3× heartbeat, explicit clear on offline/disconnect); consistency
        semantics (per-pod eventual — no cross-pod invalidation push unlike cache-invalidate/
        conn-control, each pod's Redis client reads the same shared instance); tenancy
        boundary (community-scoped key segment, cites `presence_key`); security boundary
        (transport-only, same trust-domain framing `architecture-containers-redis` already
        states, cites the crate-level relay-trust-domain doc comment); failure behavior (pool
        error surfaces as `PubSubError`, callers `let _ =` swallow it at both write sites —
        name this explicitly as a real, checked gap, not smoothed over); links to
        `presence.rs`, `event.rs`, `connection.rs`, `bridge.rs`, and the ignored
        `#[ignore = "requires Redis"]` integration tests instead of copying their bodies.
        done when: `launchpad/docs/corpus/layers/data/redis/presence.md` exists with
        schema-required fields present and every DoD bullet from the issue body addressed
        in the file's own sections.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        `/home/serina/Launchpad/buzz/__worktrees/task-1095-presence`; fix and re-run until
        exit 0.
        done when: the command exits 0.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own call (bare, unpiped) to earn the commit
        gate; confirm OK. Then, in a separate call, `git add` the plan + document and
        `git commit -s`.
        done when: the discover command reports OK and a signed commit exists containing
        exactly the plan file and the corpus document.

PARALLEL: none — single file, single task, isolated worktree.

GATES: `validate.py` must exit 0. The unittest discover command must report OK, run bare
       and unpiped, as its own tool call, before any commit. No push, no PR — bundling into
       a batch PR is a later step owned by someone else. `review-adjudicate` and cross-model
       final review are deferred to the batch owner.

BUDGET: small — one document, no code changes, evidence scoped to `presence.rs` plus four
        call sites already located (`handlers/event.rs`, `connection.rs`, `api/bridge.rs`,
        `buzz-relay/src/state.rs` if it needs a citation for `AppState.pubsub`).

OPEN: Whether Redis presence should be called "cache" or "derived" is a judgement call —
      resolved as INFERENCE with confidence in the document itself (there is no durable
      Postgres backstop for presence the way cache-invalidation/conn-control state, so
      "cache" alone slightly overstates recoverability; "derived from live connection state,
      cached with a TTL" is the more precise framing, disclosed rather than asserted flatly).
      Whether `.env.example`'s `BUZZ_REDIS_POOL_SIZE` and pooling detail belong in this
      presence-scoped node or only in the container-level `architecture-containers-redis`
      node — resolved by linking, not repeating (this node states presence uses the crate's
      one shared pool, not a dedicated connection, and cites the container node for the
      pool's own construction).

LEFT OUT: No relationships to unmerged `layers/data/redis/*` siblings (channel-pubsub,
          connection-pool, dedicated-pubsub-connection, key-namespacing, role) — none exists
          on `origin/launchpad`. No edit to `architecture-containers-redis` itself (already
          merged/draft, out of this task's scope; it already carries the one-line presence
          row this node zooms into). No attempt to fix the swallowed-error gap in
          `handle_ephemeral_event`/`connection.rs` — named as a real gap in the document,
          not resolved as a code change. No claim about typing indicators, cache-invalidation,
          conn-control, rate-limiting, or NIP-98 replay — those are separate `buzz-pubsub`
          modules with their own eventual `layers/data/redis/*` nodes, out of scope here.
