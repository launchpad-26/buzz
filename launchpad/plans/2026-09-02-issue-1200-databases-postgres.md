Issue #1200: task: document operations/databases/postgres.md

Stated size: issue body has no explicit Size line; dispatch brief for Feature #618 caps this task  ->  cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/operations/databases/postgres.md` does not exist yet
  (checked: `ls launchpad/docs/corpus/operations/databases/` on this worktree
  returns nothing under that path today).
- `launchpad/docs/corpus/architecture/containers/postgres.md` exists, is
  merged-shaped (id `architecture-containers-postgres`), and already covers
  Postgres's container-level responsibility, ownership split between
  `buzz-db`/`buzz-relay`, connection pooling internals, migration gating, and
  partitioning — this task must link it rather than restate it.
- `launchpad/docs/corpus/templates/reference.md` (id `corpus-template-reference`)
  is the assigned template and is `status: active`.
- Node ids that resolve on `origin/launchpad` today are listed in
  `<SCRATCH>/existing-node-ids.txt`; no `operations-*` id exists yet, so no
  sibling operations node (migrations #1198, backup #1197, restore #1202,
  database-failure #1215) can be a `relationships[].target` — they are named
  in prose only. `architecture-deployment-docker-compose` and
  `architecture-deployment-kubernetes` do exist and are valid targets.
- The worktree's branch (`task/1200-databases-postgres`) is up to date with
  `origin/launchpad` and the working tree is clean.

STEP 1 — Gather and pin evidence [independent]

Record `git rev-parse HEAD`. Open and read, in this worktree: `crates/buzz-db/src/lib.rs`,
`crates/buzz-db/src/runtime/mod.rs` (`ping`, `pool_stats`), `crates/buzz-db/src/store/partition.rs`
(`ensure_future_partitions`), `crates/buzz-relay/src/config.rs` (env var parsing),
`crates/buzz-relay/src/router.rs` (`readiness_handler`, `liveness_handler`),
`crates/buzz-search/src/lib.rs`, `migrations/0001_initial_schema.sql` (pgcrypto
extension, `search_tsv`/GIN index), `.env.example`, `docker-compose.yml`,
`deploy/compose/compose.yml` + `.env.example`, `deploy/charts/buzz/values.yaml`,
`deploy/charts/buzz/templates/secret-chart.yaml`, `deploy/charts/buzz/README.md`,
`crates/buzz-admin/src/main.rs` (`Migrate` command), `Justfile` (`_ensure-services`).
<!-- CONTEXT -->
```
git -C /home/serina/Launchpad/buzz/__worktrees/task-1200-databases-postgres rev-parse HEAD
```
done when: every file above has been opened in this session and the revision
is recorded for use in the front matter.

STEP 2 — Write the node [needs 1]

Create `launchpad/docs/corpus/operations/databases/postgres.md` with schema-valid
front matter (`id: operations-databases-postgres`, `type: operations`,
`status: draft`, `origin: launchpad`, `audiences: [operator, developer, agent]`)
and one `evidence` entry per substantive body claim, classified FACT/INFERENCE/
TEAM_KNOWLEDGE per `launchpad/docs/corpus/standards/evidence.md`. Body follows
the reference template's required sections: reference description, structured
entries (a configuration/operational-knob table), a Commands section
(`buzz-admin migrate`, compose/helm invocations), a boundary statement, a
scope-and-omissions section naming the sibling operations nodes (#1197 backup,
#1198 migrations, #1202 restore, #1215 database-failure) as owners of what this
node does not cover, and the two things step 3 of AGENTS.md requires kept
separate (what the node excludes vs. what was expected but could not be
verified — e.g. staging/production pipeline configuration in the private
`squareup/block-coder-tf-stacks` and `squareup/sprout-oss` repos).
<!-- RUNS HERE -->
done when: the file exists at the target path with front matter that parses
as valid YAML and a body containing every required-sections heading from
`launchpad/docs/corpus/templates/reference.md`.

STEP 3 — Validate [needs 2]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repository root inside the worktree. Fix any reported error (unresolved
relationship target, bad citation shape, non-`.md` file) and re-run until
exit 0.
done when: the command exits 0.

STEP 4 — Self-review against the DoD [needs 3]

Re-read the drafted node against every Definition of Done bullet in issue
#1200 and re-open every FACT citation to confirm the source actually says
what the statement claims (not merely that the path resolves).
done when: each DoD bullet is confirmed satisfied or explicitly named as
unmet in the final report; no FACT rests on a citation that was not reopened
during this pass.

STEP 5 — Earn the commit gate and commit [needs 4]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call and confirm `OK`. Then, in a
separate tool call, `git add -A && git commit -s -m "docs(corpus): ..."`.
Do not push and do not open a PR.
done when: the test suite reports `OK` and `git log -1` on the branch shows a
new commit with a `Signed-off-by` trailer, with nothing pushed.

PARALLEL

Nothing in this plan runs in parallel — one document, one author, one
worktree; steps are strictly sequential (each `[needs N]` on the previous).

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (step 3).
- The corpus test suite
  (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
  must report `OK`, run alone in its own tool call, before the commit is made
  (step 5) — this is the "verify gate" the dispatch brief names; do not edit
  the stamp file and do not use `--no-verify` if it refuses.
- `git commit -s` is mandatory (DCO); an unsigned commit fails the required
  DCO check later.

BUDGET

One hand-authored corpus document (plus this plan file, which is expected
alongside it per merged precedent). No code changes. No second corpus
document. Evidence-gathering is read-only (no crate, migration, or config
file is modified).

OPEN

- Whether `squareup/block-coder-tf-stacks` / `squareup/sprout-oss` actually
  set `BUZZ_AUTO_MIGRATE` and what Postgres topology they provision for
  staging/production is not answerable from this repository — the node must
  say so as a named gap, not guess.
- Whether the Helm chart's `migrate.autoMigrate: true` default and the
  self-hosted `deploy/compose` `.env.example`'s `BUZZ_AUTO_MIGRATE=true`
  default are deliberately more eager than the relay binary's own off-by-default
  is a genuine cross-source discrepancy this node records rather than resolves
  (per evidence-standard MUST 10, a same-claim-type conflict between two
  configuration sources is not this author's to adjudicate away).

LEFT OUT

- Restating `architecture-containers-postgres.md`'s pool-sizing internals,
  crate ownership boundary, or replica-fence mechanism — that node is
  canonical for those claims; this node links it.
- Backup procedure, restore procedure, and migration-authoring procedure —
  owned by sibling issues #1197, #1202, #1198 respectively, none of which
  exist as corpus nodes yet on `origin/launchpad`, so no `relationships` edge
  to them is declared; they are named in prose only.
- Database-failure/incident response — owned by #1215, same reasoning.
- Any change to runtime product behaviour, `BUZZ_AUTO_MIGRATE` defaults, or
  the Helm chart's values — this is a documentation-only task.
