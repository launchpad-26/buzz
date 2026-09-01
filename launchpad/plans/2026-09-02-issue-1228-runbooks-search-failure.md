Issue #1228: task: document operations/runbooks/search-failure.md

Stated size: one document (per corpus-batch-author dispatch brief for Feature #618) -> cap: 5 steps

ALREADY TRUE

- Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1228-runbooks-search-failure`
  and branch `task/1228-runbooks-search-failure` already exist, based on
  `origin/launchpad`. Confirmed with `git status` (clean, up to date with
  `origin/launchpad`) and `git branch --show-current`.
- `git rev-parse HEAD` at the start of this task: `473205a7457b208455f188847bfb27b01aa83cac`.
- The target file `launchpad/docs/corpus/operations/runbooks/search-failure.md`
  does not exist yet — confirmed with `ls launchpad/docs/corpus/operations/`
  (directory itself does not exist) and with
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which
  carries no `operations/` subtree at all yet.
- `launchpad/docs/corpus/templates/runbook.md` (id `corpus-template-runbook`) is
  merged on `origin/launchpad` and is the assigned template. Its Required
  sections are: Trigger, Severity and impact, Diagnosis, Mitigation and
  resolution, Escalation, Scope and omissions.
- Six `capabilities/search/*` nodes are already merged on `origin/launchpad`
  (`capabilities-search-full-text-search`, `-search-index`, `-search-query`,
  `-channel-scope`, `-privacy-filtering`, `-result-reauthorization`) and
  already document the FTS mechanism in depth (generated `search_tsv` column,
  channel scoping, privacy exclusions, post-hit reauthorization). This
  runbook's job is the operational decision tree, not a second copy of that
  mechanism — link to those nodes rather than restate their content.
- Issue #1224 (`document operations/runbooks/postgres-unavailable.md`) is a
  sibling task in the same Feature and is unmerged — its node id is unknown
  and must not be targeted by a `relationships` edge; it is named in prose
  only, as the dispatch brief directs.

STEP 1 — Gather evidence from the source tree [independent]

Read `crates/buzz-search/{lib.rs,query.rs,error.rs}`, the FTS-relevant
migrations (`0001`, `0005`, `0008`, `0014`, `0033`), the maintenance script
`scripts/maintenance/nip_rs_search_allowlist.sql`, the relay's two search
entry points (`handlers/req.rs`'s `handle_search_req`, `api/bridge.rs`'s
`handle_bridge_search` and `search_hit_accepted`), the relay's readiness
probe (`router.rs`), the dedicated search pool wiring (`main.rs`), the CLI's
`messages search` (`buzz-cli/src/commands/messages.rs`) and its error/exit-code
mapping (`buzz-cli/src/error.rs`), and `ARCHITECTURE.md`/`CONTRIBUTING.md`'s
search sections. <- RUNS HERE

done when: every fact the runbook body states is backed by a source actually
opened in this step, recorded in the evidence ledger.

STEP 2 — Write the plan (this file) and check it [needs 1]

done when: `bash /home/serina/.claude/skills/plan-issue/check-plan.sh
launchpad/plans/2026-09-02-issue-1228-runbooks-search-failure.md` reports no
blocking findings.

STEP 3 — Draft the corpus node [needs 1]

Write `launchpad/docs/corpus/operations/runbooks/search-failure.md` with
`id: operations-runbooks-search-failure`, `type: operations`,
`status: draft`, following `corpus-template-runbook`'s Required sections:
Trigger, Severity and impact, Diagnosis (index/trigger vs. query-shape vs.
permissions/scoping vs. Postgres-degraded), Mitigation and resolution (in
executable order), Escalation (naming the postgres-unavailable runbook by
name, not by link), and Scope and omissions (with the two distinct
subsections: what this node does not cover, and what was expected but could
not be verified).

done when: the file exists, every evidence entry classifies honestly (FACT
only for sources actually opened; commit-only FACT used exactly once), and
`relationships` targets only ids confirmed present on `origin/launchpad`.

STEP 4 — Validate and fix [needs 3]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repository root and fix anything it reports until it exits 0.

done when: the validator exits 0.

STEP 5 — Earn the commit gate and commit [needs 4]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call, confirm `OK`, then commit with
`git commit -s`.

done when: the commit exists on `task/1228-runbooks-search-failure` with a DCO
`Signed-off-by` trailer, and is not pushed.

PARALLEL

None — this is a single document authored by one agent; steps 2-5 are
strictly sequential (each `needs` the previous), and no sub-tasks run
concurrently.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit.
- The corpus test suite must print `OK`, run as a standalone Bash call (not
  piped, not chained with `cd`), before commit.
- `git commit -s` (DCO) is mandatory; no `--no-verify`.

BUDGET

One document (~250-400 lines), one plan file, no code changes. No sub-agents.

OPEN

- Whether `operations/runbooks/postgres-unavailable.md` (#1224) lands before
  or after this node — irrelevant to this task, since no edge to it is
  declared either way; it is named in prose only.
- Whether a future corpus review wants a `depends-on` edge from this node to
  `architecture-containers-postgres` — not declared here because this node's
  claims do not depend on that node's specific content being read.

LEFT OUT

- No second hand-authored corpus document. If evidence surfaces a second
  concept (e.g., a distinct "search index maintenance" procedure node), it is
  reported in the final self-review and filed as its own issue, not folded in.
- No code, script, or migration changes — this is a documentation-only task.
