# Plan — issue #1226: `operations/runbooks/redis-unavailable.md`

Issue #1226 — task: document operations/runbooks/redis-unavailable.md

Stated size: one hand-authored corpus document, per parent Feature #618's batch dispatch  ->  cap: 5 steps

ALREADY TRUE

- Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1226-runbooks-redis-unavailable`
  exists, branch `task/1226-runbooks-redis-unavailable`, based on and up to date with
  `origin/launchpad` at `473205a7457b208455f188847bfb27b01aa83cac` (confirmed via
  `git rev-parse HEAD` and `git status`).
- `launchpad/docs/corpus/operations/` does not exist yet in this worktree (confirmed:
  `ls launchpad/docs/corpus/operations` reports no such directory); the target file
  `launchpad/docs/corpus/operations/runbooks/redis-unavailable.md` does not exist.
- The template `launchpad/docs/corpus/templates/runbook.md` (id `corpus-template-runbook`)
  is merged and defines six required sections: Trigger, Severity and impact, Diagnosis,
  Mitigation and resolution, Escalation, Scope and omissions.
- `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
  are read; the seven legal front-matter keys and the FACT/INFERENCE/TEAM_KNOWLEDGE
  contract are understood.
- `<SCRATCH>/existing-node-ids.txt` lists 204 merged node ids on `origin/launchpad`,
  including `corpus-template-runbook`, `architecture-containers-redis`,
  `architecture-deployment-single-relay`, and `architecture-deployment-multi-relay`.
  No `operations-*` id exists yet anywhere in that list.
- Sibling issue #1219 (`operations/reliability/redis-failure.md`, a reference node for
  Redis failure modes) is unmerged and not present in the existing-node-ids list; its
  path must not be linked from this document.
- Source evidence has already been gathered by opening (not assumed):
  `crates/buzz-pubsub/src/{rate_limiter,nip98_replay,presence,conn_control,lib}.rs`,
  `crates/buzz-relay/src/{admission,connection,mesh_boot,main,router,config}.rs`,
  `crates/buzz-relay/src/handlers/{event,side_effects}.rs`,
  `crates/buzz-relay/src/api/bridge.rs`, `crates/buzz-relay-mesh/src/{registry,runtime}.rs`,
  `deploy/charts/buzz/{values.yaml,templates/deployment.yaml,templates/_validate.tpl}`,
  `docker-compose.yml`, `.env.example`, `Dockerfile`, `Justfile`, `prometheus.yml`, and
  the merged corpus standards (`atomicity`, `code-references`, `evidence`, `linking`).

STEP 1 — Write the corpus node [independent]

Create `launchpad/docs/corpus/operations/runbooks/redis-unavailable.md` with id
`operations-runbooks-redis-unavailable`, `type: operations`, `status: draft`,
`origin: launchpad`, `audiences: [operator, agent, developer]`. <- RUNS HERE
Body follows the runbook template's six required sections, split into the DoD's named
parts: trigger and symptom, prerequisites, severity and impact, diagnosis, mitigation
and resolution (ordered, environment-specific), verification of recovery, rollback and
escalation, evidence to preserve, and scope and omissions (naming the #1219 boundary in
prose only, no link to its unmerged path). `relationships` declares `implements`
against `corpus-template-runbook` and `references` against
`architecture-containers-redis`, `architecture-deployment-single-relay`, and
`architecture-deployment-multi-relay` — all four resolve on `origin/launchpad` today.

done when: the file exists, front matter parses, every claim has an evidence entry
classed honestly (one commit-only FACT for provenance, one FACT for the template), and
the body's headings map 1:1 to the issue's DoD tail bullets.

STEP 2 — Validate [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root. Fix any reported error (broken citation, schema violation, unresolved
relationship target) and re-run until exit 0.

done when: the validator exits 0 and its output is re-read for `UNVERIFIED` notices
attached to any `FACT` other than the provenance entry (there should be none).

STEP 3 — Check the plan [independent]

Run `bash /home/serina/.claude/skills/plan-issue/check-plan.sh
launchpad/plans/2026-09-02-issue-1226-runbooks-redis-unavailable.md` and fix anything
it reports.

done when: the checker reports no defects, or any defect it reports is fixed and it is
re-run clean.

STEP 4 — Self-review against the issue's DoD [needs 2]

Re-read the diff bullet by bullet against issue #1226's Definition of Done, including
the four type-specific tail bullets. Confirm no second concept was folded in (redis
failure-mode taxonomy stays with #1219; this document does not restate it).

done when: every DoD bullet is checked off with a specific section/sentence that
satisfies it, or is named as unsatisfied in the final report.

STEP 5 — Earn the commit gate and commit [needs 4]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own Bash call (no `cd` chained, no output
piped) and confirm `OK`. Then, in a separate call, `cd` into the worktree and run
`git add -A && git commit -s -m "docs(corpus): add redis-unavailable runbook (#1226)"`.

done when: the test suite reports `OK`, the commit succeeds with a `Signed-off-by`
trailer, and `git log -1` shows the new commit on `task/1226-runbooks-redis-unavailable`.

PARALLEL

None — this is a single hand-authored document with no independent sub-tasks. Steps 1
and 3 may run in either order relative to each other; steps 2, 4 and 5 are sequential.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK`, run alone in its own Bash call, before commit (repo verify-gate).
- No file exceeds 1000 lines (repo-wide `just file-size-check` gate).

BUDGET

One document, one plan file. Estimated 1 commit, no PR (orchestrator integrates later).

OPEN

- Whether a runbook may itself specify or trigger `buzz-workflow` automation rather
  than only describing manual steps is unresolved by the template itself and is not
  decided here either.
- No alerting rule (PrometheusRule or equivalent) exists in this repository that fires
  on Redis unavailability for the main relay chart — confirmed by searching
  `deploy/charts/buzz/**/*.yaml` for "redis", which returns no `prometheusrule.yaml`
  match. The trigger in this document is therefore the readiness probe and the Redis
  pool gauges, not a named alert.

LEFT OUT

- The Redis failure-mode taxonomy (causes, blast radius across kinds of Redis outage)
  is issue #1219's document, not this one — this runbook names the boundary in prose
  and does not restate or link its (unmerged) path.
- Any change to runtime behavior, alerting configuration, or the Helm chart's Redis
  validation guard — this task documents current behavior, it does not add an alert
  or change `_validate.tpl`.
