Issue #1222 — task: document operations/runbooks/migration-failure.md
Stated size: not stated in the issue body; treated as ≤30 minutes (one hand-authored corpus document, no code changes) → cap: 5 steps

ALREADY TRUE  (verified against git and the worktree, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1222-runbooks-migration-failure`
  exists, is on branch `task/1222-runbooks-migration-failure`, tracks `origin/launchpad`,
  and `git status` shows a clean working tree.
  `git rev-parse HEAD` = `473205a7457b208455f188847bfb27b01aa83cac`.
  The target file `launchpad/docs/corpus/operations/runbooks/migration-failure.md` does
  NOT exist — confirmed by `ls` on both `operations/` and `operations/runbooks/`, neither
  of which exists yet.
  `launchpad/docs/corpus/templates/runbook.md` (id `corpus-template-runbook`) is merged
  on `origin/launchpad` and was read in full: Required sections are Trigger, Severity and
  impact, Diagnosis, Mitigation and resolution, Escalation, Scope and omissions.
  `AGENTS.md` and the evidence/provenance/linking/atomicity/naming/normative-language/
  code-references/test-references standards were all read.
  `<SCRATCH>/existing-node-ids.txt` lists 204 merged ids as of dispatch, including
  `corpus-template-runbook`, `architecture-containers-postgres`, `layers-lifecycle-startup`,
  `architecture-deployment-kubernetes`, `architecture-deployment-single-relay`,
  `architecture-deployment-multi-community`, `architecture-context-relay-operator`.
  Evidence already gathered by direct file reads this session: the migration runner
  (`crates/buzz-db/src/runtime/migration.rs`), the advisory-lock key
  (`crates/buzz-db/src/store/deletion.rs`), the `BUZZ_AUTO_MIGRATE` gate and fail-fast exit
  (`crates/buzz-relay/src/main.rs`), the manual `buzz-admin migrate` path
  (`crates/buzz-admin/src/main.rs`), the Compose restart policy and backup checklist
  (`deploy/compose/compose.yml`, `deploy/compose/run.sh`, `deploy/compose/README.md`), and
  the Helm chart's migration/backup guidance (`deploy/charts/buzz/README.md`). No down
  migration files, no rollback subcommand in `buzz-admin`, and no down/revert Justfile
  recipe for schema migrations were found by direct `find`/`grep` in this worktree.

STEP 1 — Write the node                                                [independent]
        Create `launchpad/docs/corpus/operations/runbooks/migration-failure.md`, id
        `operations-runbooks-migration-failure`, type `operations`, status `draft`,
        origin `launchpad`, audiences `[operator, developer, reviewer]`, all six
        Required sections from `templates/runbook.md`, plus a Prerequisites subsection
        (issue DoD names it separately from severity/impact). Declare `relationships`:
        `implements -> corpus-template-runbook`, `references ->
        architecture-containers-postgres`, `references -> layers-lifecycle-startup` —
        all three confirmed present in `<SCRATCH>/existing-node-ids.txt`. Every `FACT`
        cites a file opened this session; one commit-only `FACT` records the revision;
        one final `FACT` names the template.
        done when: the file exists at the assigned path with schema-shaped front matter
        and a body carrying all six Required sections plus Prerequisites.

STEP 2 — Validate                                            [needs 1]  ← RUNS HERE
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
        root; fix any reported error and re-run until exit 0.
        done when: `validate.py` exits 0 and the ledger holds exactly one commit-only
        `FACT`.

STEP 3 — Self-review against the issue's DoD                          [needs 2]
        Re-read the drafted node against issue #1222's Definition of Done line by line,
        including the four type-specific tail bullets (trigger/symptom + severity/impact
        + prerequisites; diagnosis-then-mitigation in executable order; verification +
        rollback/escalation + evidence to preserve; no secret values, link automation
        instead of copying credentials). Confirm no second concept was folded in.
        done when: every DoD bullet is checked off against a named section of the body.

STEP 4 — Earn the commit gate and commit                              [needs 3]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own Bash call, confirm `OK`, then in a
        separate call run `git add -A && git commit -s -m "docs(corpus): add operations
        runbook for migration failure (#1222)"`.
        done when: the test suite reports `OK` and the commit exists with a
        `Signed-off-by` trailer, with no stamp file edited and no `--no-verify` used.

STEP 5 — Report                                                        [needs 4]
        Report issue number, branch, worktree path, commit SHA, target file path and
        line count, which DoD bullets are satisfied, anything expected but not verified,
        and any second concept discovered. No PR is opened.
        done when: the report names every item above explicitly.

PARALLEL  None. Every step depends on the file the previous step wrote or validated —
this is a single document with no independent sub-tasks to fan out across subagents.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
commit (step 2). The corpus unit test suite must report `OK`, run alone in its own Bash
call, to earn the verify-gate commit stamp (step 4). `git commit -s` is mandatory (DCO);
never `--no-verify`. No `review-*` skill applies — this produces documentation, not code
or tests, and no runtime interface exists to exercise, so `qa` explore mode does not
apply either.

BUDGET    One document (~250-400 lines of body prose, under the repo-wide 1000-line
file-size gate) and one plan file. No code changes. Step 1 (drafting, with citations
checked one by one) is the step most likely to eat the budget.

OPEN      Whether a Kubernetes pre-upgrade migration Job (`migrate.preUpgradeJob`) ever
lands is out of this task's control — the Helm chart README states the values knob is
reserved but unimplemented; the node describes today's behavior, not the roadmap item.
Whether `docs/multi-tenant-conformance.md` (migration 0001's own stated governing
contract) bears further on migration-failure recovery was not explored beyond confirming
an already-merged sibling node cites it; re-verifying it is out of this task's scope.

LEFT OUT  Any second hand-authored corpus document (a general Postgres-ops runbook, or a
"how migrations are authored" development-surface node) — out of scope per the issue's
own Out-of-scope list. Editing `architecture-containers-postgres.md` or
`layers-lifecycle-startup.md` to add a `relationships` edge back to this new node —
inbound edges from already-merged nodes are not this task's to add.
