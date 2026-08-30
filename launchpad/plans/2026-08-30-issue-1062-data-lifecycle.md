Issue #1062 — task: document layers/data/data-lifecycle.md
Stated size: no Size line in the issue body (single small document, no code); the corpus-batch-author orchestration that dispatched this task fixed the cap directly instead of asking interactively  →  cap: 5 steps

ALREADY TRUE  (verified against git and the repository, not notes)
  Issue #1062 read directly via `gh issue view 1062 --repo launchpad-26/buzz`.
  Objective: create `launchpad/docs/corpus/layers/data/data-lifecycle.md` as the
  single canonical concept node for data lifecycle. Parent PRD is #610.

  `launchpad/docs/corpus/layers/data/data-lifecycle.md` does not exist — confirmed
  with `ls`; `launchpad/docs/corpus/layers/` does not exist at all on this branch
  (forked from `origin/launchpad` at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5).

  `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is: architecture,
  layers, capabilities, platforms, implementation, interfaces-events, verification,
  operations, development, release, governance, agent, ingestion. Every existing
  node follows path-derived id/type (e.g. `architecture/containers/relay.md` →
  `id: architecture-containers-relay`, `type: architecture`), so this node takes
  `id: layers-data-data-lifecycle`, `type: layers`.

  `launchpad/docs/corpus/templates/concept.md` matches this node's shape — a
  phased-lifecycle idea to be understood, not a field catalogue (reference) or a
  numbered how-to (procedure). Required sections per that template: Definition
  (not optional), Use cases (not optional), Scope and omissions (required by
  AGENTS.md step 8); intro, visual aid, Background, Comparison, Related resources
  are optional there and treated the same way here.

  `launchpad/docs/corpus/AGENTS.md` read and governs: evidence classes
  (FACT/INFERENCE/TEAM_KNOWLEDGE) and their required fields, the six citation
  shapes plus the two URL forms, the one-node-one-idea rule, and the
  relationships merge-target rule (a target must resolve on `origin/launchpad`,
  not the working branch).

  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
  node under `layers/` yet — every content node so far is under `architecture/`,
  `standards/`, or is `AGENTS.md`/`README.md`. No relationship target for a
  sibling data-layer node exists, so this node declares no `relationships`.

  Lifecycle mechanics were inspected directly this session (exact paths/symbols
  become the node's own evidence citations, not restated here): event ingestion
  and ephemeral-kind rejection (`crates/buzz-db/src/event.rs::insert_event`,
  `crates/buzz-core/src/kind.rs::is_ephemeral`); per-event soft-deletion on
  NIP-09 kind:5 / NIP-29 kind:9005
  (`crates/buzz-db/src/event.rs::soft_delete_event`,
  `crates/buzz-relay/src/handlers/side_effects.rs::handle_delete_event_side_effect`);
  parameterized-replaceable supersession
  (`crates/buzz-db/src/lib.rs::replace_parameterized_event`) with a narrow
  hard-delete-on-supersede exception for exactly two high-churn coordinate kinds,
  matched by a hard-purge-after-soft-delete trigger for the same two kinds
  (`migrations/0019_mesh_status_retention.sql`,
  `migrations/0009_nip_rs_database_guards.sql` — confirmed exactly these two by
  grepping `migrations/` for `purge_soft_deleted`, not assumed); ephemeral-channel
  TTL refresh and reaping (`migrations/0022_event_ttl_refresh.sql`,
  `crates/buzz-db/src/channel.rs::reap_expired_ephemeral_channels`, the reaper
  task in `crates/buzz-relay/src/main.rs`); the durable whole-community deletion
  lifecycle (`crates/buzz-db/src/deletion.rs`, its `DeletionStage` enum); and the
  audit log surviving per-event deletion but not whole-community purge
  (`crates/buzz-audit/src/lib.rs`,
  `deletion.rs::PURGE_SCOPED_TABLES` including `audit_log`).
  `crates/buzz-relay/src/storage_sweep.rs` was read and confirmed to be an hourly
  S3 usage-*metrics* listing job, not a deletion mechanism — excluded from the
  lifecycle's deletion phase on that basis rather than assumed relevant.

STEP 1  Draft the front matter and body of the concept node at             [independent]
        `launchpad/docs/corpus/layers/data/data-lifecycle.md` (creating the
        `layers/` and `layers/data/` directories), following `templates/concept.md`'s
        section shape and citing every substantive claim against the sources
        already inspected above.
        done when: the file exists at the target path; front matter has exactly
        the seven schema-legal keys (id, type, status, origin, audiences,
        evidence, and no relationships) correctly typed; the body contains a
        Definition, a Use cases, and a Scope-and-omissions section.

STEP 2  Run the corpus validator and fix whatever it reports.              [needs 1]  ← RUNS HERE
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0.

STEP 3  Run the corpus unit test suite as the sole command in its own step [needs 2]
        (the commit gate).
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`.

STEP 4  Stage and commit the plan file and the new corpus document with    [needs 3]
        `git commit -s`.
        done when: `git log --oneline origin/launchpad..HEAD` shows exactly one
        commit, and `git show --stat HEAD` lists only the plan file and the
        corpus document.

PARALLEL  None of these four steps can run as independent subagents — steps 2-4
          each depend on the file step 1 produces, and step 4 depends on step 3's
          gate having already passed. Step 1 is tagged `[independent]` only in
          the sense that it touches no file any other pending step touches yet;
          in practice it still runs first because nothing downstream has
          anything to validate, test, or commit before it exists.

GATES     No `review-*` skill applies — this is a single documentation node, not
          code. The commit gate is `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (step 3),
          run alone in its own step per the outer task's instructions, before any
          `git add`/`git commit`. `qa` explore mode does not apply — there is no
          runtime interface to exercise; this is a docs-only change.

BUDGET    Step 1 (drafting) is the step most likely to overrun: the lifecycle
          spans several subsystems (event soft-delete, parameterized-replaceable
          supersession, channel TTL reaping, whole-community deletion, audit-log
          retention) and the one-node-one-idea rule means describing the shared
          *shape* of the lifecycle without drifting into a second document about
          any single subsystem's own mechanics.

OPEN      None. The type enum value, the template to follow, and the absence of
          any resolvable relationship target were all confirmed directly against
          `node.schema.json`, `templates/concept.md`, and `origin/launchpad`'s
          actual tree rather than assumed.

LEFT OUT  Any second corpus document (e.g. a `datastore`-typed node for the
          `events` table schema, or a `procedure`-typed node for running a
          whole-community deletion) — issue #1062's own out-of-scope section
          forbids a second hand-authored canonical document; those are separate,
          unfiled tasks if the corpus batch wants them.
          Reworking `templates/concept.md` or `node.schema.json` — both are
          read-only inputs here.
          Any generated index or projection derived from this node — none exists
          yet for the `layers/` surface, and none is created by this task.
