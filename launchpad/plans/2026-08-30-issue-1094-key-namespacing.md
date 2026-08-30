Issue #1094 — task: document layers/data/redis/key-namespacing.md
Stated size: none (no `Size` line in the issue body)  →  cap: 5 steps
(No `Size` line exists on this issue; the 5-step cap instead comes from the
corpus-batch-author dispatch brief for this scripted overnight task, which is
used in place of pausing to ask, per that brief's own explicit instruction.)

ALREADY TRUE  (verified against git and the repo, not notes)
  - `git rev-parse HEAD` on this worktree (branched from `origin/launchpad`) is
    338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5.
  - `launchpad/docs/corpus/layers/data/redis/key-namespacing.md` does not exist
    (`test -f` on that path, checked in this worktree).
  - No `layers/data/redis/*` node exists on `origin/launchpad` at all — the three
    named siblings (#1091 channel-pubsub, #1092 connection-pool, #1093
    dedicated-pubsub-connection) are not merged, confirmed via
    `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`.
  - `architecture-containers-redis` (`launchpad/docs/corpus/architecture/containers/redis.md`)
    **does** exist on `origin/launchpad`. Its own "Responsibility" table already
    documents, at one line per job, the same five `buzz:{community}:...` key
    patterns this node will describe in depth, and its own text states
    "`buzz-pubsub` owns every Redis access pattern and key-naming convention in
    this table" — so this new node is a legitimate `part-of` target zoom-in, not a
    duplicate: the container doc names *that* the convention exists per job, this
    node names the convention's own shape, encoding rules, and the one documented
    exception (operator-global IP keys).
  - `node.schema.json`'s `type` enum has no `layers/data/redis`-specific member;
    prior batch documents in this run used `type: layers` for every
    `layers/data/...` path regardless of which template's own worked example uses
    a different type — this node follows that same override, disclosed in its
    evidence ledger per `standards/taxonomy.md`.
  - The actual Redis key convention in code (verified by reading, not grep alone):
    `crates/buzz-pubsub/src/topic.rs` (`BUZZ_PREFIX = "buzz"`, `channel_key`/`global_key`,
    `EventTopicKey::redis_channel`/`parse_redis_channel`), `presence.rs`
    (`presence_key`, `PRESENCE_TTL_SECS = 180`), `conn_control.rs`
    (`conn_control_channel`, `CONN_CONTROL_PATTERN = "buzz:*:conn-control"`,
    `parse_conn_control_channel`), `cache_invalidation.rs`
    (`cache_invalidation_channel`, `CACHE_INVALIDATION_PATTERN`,
    `parse_cache_invalidation_channel`), plus `crates/buzz-auth/src/nip98_replay.rs`
    (`nip98_replay_key_for_scope`) and `crates/buzz-auth/src/rate_limit.rs`
    (`rate_limit_key`, `ip_rate_limit_key`) — the latter two build keys used by
    `buzz-pubsub`'s Redis-backed guard/limiter but are themselves defined in
    `buzz-auth`, a fact the container doc does not call out and this node will.
  - Two templates were read in full: `launchpad/docs/corpus/templates/datastore.md`
    (scoped to one whole running instance, e.g. "the Redis instance") and
    `templates/reference.md` (Diátaxis Reference form: a structured-entry catalogue,
    one row per fact). The issue's actual DoD bullets ("states whether the store is
    authoritative/derived/cache/transport," "describes owned data, key access
    patterns, lifecycle/retention and consistency semantics," "names
    tenancy/security boundaries and failure behavior") map one-to-one onto columns
    of a per-key-namespace row, not onto whole-instance facts already owned by
    `architecture-containers-redis` — `reference.md`'s structured-entries shape fits;
    `datastore.md` would duplicate the container doc's own scope.
  - `check-plan.sh` was located at `/home/serina/.claude/skills/plan-issue/check-plan.sh`
    (first match; reachable, no fallback search needed).

STEP 1  Draft front matter + evidence ledger for the new node        [independent]
        Build `id: layers-data-redis-key-namespacing`, `type: layers`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
        operator]`, and one evidence entry per FACT already gathered above (topic.rs,
        presence.rs, conn_control.rs, cache_invalidation.rs, nip98_replay.rs,
        rate_limit.rs, plus a commit citation for the recorded revision). No
        `relationships` entry may target #1091/#1092/#1093 (unmerged); the one
        legitimate target is `architecture-containers-redis` via `part-of`.
        done when: front matter is written to the target file and is valid YAML
        with every field `node.schema.json` requires present.

STEP 2  Write the body: convention shape + per-namespace reference table   [needs 1]  ← RUNS HERE
        Body follows `templates/reference.md`'s required sections: a Reference
        description paragraph naming the convention (`buzz:{scope}:{purpose}[:id...]`,
        `BUZZ_PREFIX = "buzz"`), a structured-entries table with one row per key
        namespace (channel routing, global routing, presence, conn-control,
        cache-invalidate, nip98 replay, per-pubkey rate limit, per-IP rate limit)
        columns: pattern, purpose, store classification (transport/cache/derived
        guard), tenancy scope, lifecycle/TTL, consistency semantics, owning
        module/crate; a Boundary section naming what it does not cover (container-level
        Redis facts owned by `architecture-containers-redis`; per-namespace
        operational depth like presence's own TTL rationale, already stated there);
        a Relationships section declaring `part-of: architecture-containers-redis`;
        and a Scope-and-omissions section naming the Typesense/typing-indicator gaps
        this node does not resolve (inherited caveat from the container doc) and
        anything expected but not verified (e.g. whether any Redis key outside
        `buzz-pubsub`/`buzz-auth` exists — not found in this session's search but not
        exhaustively proven absent).
        done when: the target file exists with all required reference-template
        sections present and every DoD bullet from the issue body addressed by a
        specific section.

STEP 3  Validate schema                                              [needs 2]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root; fix any reported error (bad relationship target, missing
        required evidence field, malformed YAML) and re-run until exit 0.
        done when: the command exits 0 and prints no error for the new file.

STEP 4  Earn the commit gate and commit                              [needs 3]
        Run, as the sole bare command in its own call:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        and confirm it reports OK (never piped through `tail`/`head` — the gate
        hook needs the suite's own exit code). Only then stage exactly the plan
        file and the new corpus doc and commit with `git commit -s`.
        done when: the unittest run reports OK and `git log -1` shows a new signed
        commit touching only those two files.

STEP 5  Self-review against the issue's own DoD checklist            [needs 4]
        Re-read `git diff origin/launchpad -- .` line by line against every DoD
        bullet in the issue body; confirm each evidence entry's citation is a path
        actually opened this session; confirm no second canonical document was
        created; re-run `validate.py` to confirm it still exits 0.
        done when: every DoD bullet has a corresponding, checkable section in the
        body, and `validate.py` exits 0 on the final diff.

PARALLEL  None of the five steps is independent of its predecessor in practice —
          step 1 must exist before step 2 can cite it in front matter, and steps
          3-5 are strictly sequential gates on the same file. Step 1 is tagged
          `[independent]` only in the sense that no other pending step in *this*
          plan touches the same file yet; there is nothing else running in this
          worktree to parallelize against.
GATES     No `review-*` skill applies — this is a single-document, non-code corpus
          change reviewed by this plan's own step 5 and by the batch orchestration
          step that later bundles this branch with its siblings. `qa` explore mode
          does not apply: there is no runtime interface to exercise, only a Markdown
          document and a schema/unit-test gate.
BUDGET    Step 2 (writing the reference table + evidence ledger) is most likely to
          eat the budget — it is the only step requiring cross-referencing six
          source files' exact key-format strings, TTL constants and parse functions
          against each table row without over- or under-claiming FACT status.
OPEN      The issue does not decide whether a `typing`-indicator Redis key pattern
          exists (the container doc already flags this as unverified/possibly
          removed) — this node does not resolve it either, and says so.
LEFT OUT  No relationship to the three unmerged `layers/data/redis/*` siblings
          (#1091-#1093), per the batch dispatch brief — added only once they merge.
          No attempt to document Redis operational tuning (eviction policy,
          ElastiCache sizing) — that is `architecture-containers-redis`'s own named
          gap, not this node's subject.
