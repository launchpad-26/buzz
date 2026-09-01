Issue #1197 — task: document operations/databases/backup.md

Stated size: one hand-authored corpus document (issue body DoD's first bullet)  ->  cap: 5 steps

ALREADY TRUE

- Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1197-databases-backup` and
  branch `task/1197-databases-backup` already exist, based on `origin/launchpad`
  (confirmed: `git status` reports "up to date with 'origin/launchpad'", working tree
  clean). No new worktree or branch is created by this plan.
- `launchpad/docs/corpus/operations/` does not exist yet in this worktree (confirmed
  via `find`); `launchpad/docs/corpus/operations/databases/backup.md` does not exist
  (confirmed via `test -f`). This is a new node, not an update.
- Issue #1197's Definition of Done has been read in full (`gh issue view 1197`) and is
  the spec this plan satisfies, including the type-specific tail bullets: structured
  for lookup, facts only with generated/authored labelling, scope-and-omissions, and
  links to authoritative source/schema/config.
- Governing documents read in full: `launchpad/docs/corpus/AGENTS.md`,
  `launchpad/docs/corpus/templates/reference.md` (the assigned template),
  `launchpad/docs/corpus/schema/node.schema.json`,
  `launchpad/docs/corpus/schema/relationships.schema.json`, and the standards
  `evidence.md`, `linking.md`, `naming.md`, `atomicity.md`, `code-references.md`.
- Evidence already gathered by opening, in this worktree: `docker-compose.yml`,
  `deploy/compose/compose.yml`, `deploy/compose/compose.caddy.yml`,
  `deploy/compose/README.md`, `deploy/compose/run.sh` (the `backup_hint` function and
  its `case` wiring), `deploy/charts/buzz/values.yaml`, `deploy/charts/buzz/README.md`
  (`## Backups`), `deploy/charts/buzz/templates/NOTES.txt`, the full
  `deploy/charts/buzz/templates/` directory listing (no backup/cronjob template
  exists), `launchpad/deploy/run.sh`, `launchpad/deploy/runbooks/hardening-spec.md`
  (Part E, and its own "Status: specification only. Nothing here is implemented."
  header), `.env.example` (`BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_GIT_REPO_PATH`), and the
  merged corpus nodes `architecture/containers/postgres.md`,
  `architecture/containers/redis.md`, `architecture/containers/object-storage.md`,
  `architecture/deployment/single-relay.md`.
- The repository revision has been recorded: `git rev-parse HEAD` ->
  `473205a7457b208455f188847bfb27b01aa83cac`.
- `<SCRATCH>/existing-node-ids.txt` has been read; no `operations-*` id exists yet on
  `origin/launchpad`, and the container/deployment nodes this draft may link to
  (`architecture-containers-postgres`, `architecture-containers-redis`,
  `architecture-deployment-docker-compose`, `architecture-deployment-kubernetes`) are
  present in that list.

STEP 1 — Write the node [independent]

Create `launchpad/docs/corpus/operations/databases/backup.md` <- RUNS HERE with
`id: operations-databases-backup`, `type: operations`, `status: draft`, `origin:
launchpad`, following `templates/reference.md`'s required sections (Reference
description; Structured entries; Boundary statement; Relationships; Scope and
omissions — Commands section omitted, this subject has no CLI surface of its own to
tabulate). Content: which stores hold durable state (Postgres, object
storage/Blossom+git, relay/owner keys, `.env` secrets) versus which do not (Redis —
cite `architecture-containers-redis`'s own TTL/transient finding rather than
re-deriving it); what this repository actually ships for backing them up
(`deploy/compose/run.sh`'s `backup_hint`, a printed checklist with no automation; the
Helm chart's `NOTES.txt`/README `## Backups` list, likewise printed-only, backed by
PVCs with no backup CronJob/Job in `templates/`); and what it explicitly does not ship
(no scheduled snapshot job, no Object Lock/immutability, no restore automation —
`hardening-spec.md` Part E proposes exactly this gap and states its own status is
"specification only. Nothing here is implemented."). State the boundary against
restore (#1202) and disaster recovery (#1216) explicitly rather than describing
either procedure.

done when: the file exists at the assigned path; front matter has exactly the seven
schema-legal keys with `id`/`type`/`status`/`origin` as specified; every substantive
claim has a ledger entry classed `FACT`, `INFERENCE`, or `TEAM_KNOWLEDGE` per what was
actually opened; relationship targets (if any) are drawn only from
`<SCRATCH>/existing-node-ids.txt`; the body's Boundary and Scope-and-omissions
sections name both what this node does not cover (and who owns it) and what was
expected but could not be verified, as two distinct lists.

STEP 2 — Validate [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root. Fix any reported error (unresolved relationship target, bad citation shape,
schema violation) and re-run until it exits 0. `UNVERIFIED` notices on the
commit-only provenance `FACT` are expected and not a failure; a second `FACT` must
not rest solely on an `UNVERIFIED` citation.

done when: `validate.py` exits 0, and a manual re-read confirms no `FACT` in the new
node rests only on an `UNVERIFIED` citation besides the single provenance entry.

STEP 3 — Earn the commit gate and commit [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own Bash call. Confirm `OK`. In a separate
call, stage and commit with `git add -A && git commit -s -m "docs(corpus): document
operations/databases/backup.md (#1197)"`.

done when: the test run reports `OK`; the commit exists locally on
`task/1197-databases-backup` with a `Signed-off-by` trailer (DCO); nothing is pushed
and no PR is opened.

PARALLEL

None. This is a single-document task with a strictly sequential write -> validate ->
test -> commit path; no step here can run concurrently with another in this plan.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
  commit (Step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must report `OK`, run alone in its own Bash call, before commit
  (Step 3).
- `git commit -s` (DCO) is mandatory; no `--no-verify`, no editing the stamp file if
  the gate refuses — that is a finding to report, not to route around.

BUDGET

One document (~150-250 lines of body content is the expected range for a reference
node of this scope) plus this plan file. No code changes. No second corpus document.

OPEN

- Whether `squareup/block-coder-tf-stacks` or `sprout-oss` (both private, not in this
  checkout) provision any backup automation for the managed staging/production
  Postgres, Redis, or S3 instances is unknown from this repository and will be named
  as a gap rather than guessed at.
- Whether the CloudPirates Postgres/Redis subcharts the Helm chart depends on ship
  their own backup mechanism (as opposed to just `persistence.enabled` PVCs) was not
  investigated — those subcharts are external dependencies, not vendored into this
  repository, and are out of scope for what this node can verify.

LEFT OUT

- Restore procedure — a sibling task, issue #1202. This node names what exists to
  back up and what backs it up; it does not walk through recovering from a backup.
- Disaster recovery (multi-failure, RTO/RPO targets, drills) — issue #1216.
  `hardening-spec.md` Part E's proposed Object Lock/credential-separation/timed-drill
  properties are mentioned only as "not implemented today," not specified here.
- Any change to `deploy/compose/run.sh`, the Helm chart, or `hardening-spec.md`
  itself. This task documents the repository; it does not extend it.
