# Plan — issue #1210: document operations/observability/dashboards.md

Issue #1210, parent Feature #618. No explicit "Size" line in the issue body; this
is a single-document corpus-authoring task with a hard cap of 5 steps set by the
dispatch brief itself.

Stated size: dispatch brief caps this task at 5 steps  ->  cap: 5 steps

ALREADY TRUE: Worktree
`/home/serina/Launchpad/buzz/__worktrees/task-1210-observability-dashboards` exists,
is on branch `task/1210-observability-dashboards`, tracks `origin/launchpad`, and is
clean at `git rev-parse HEAD` = `473205a7457b208455f188847bfb27b01aa83cac`.
`launchpad/docs/corpus/operations/` does not exist yet in this worktree — confirmed
by `ls` failing. The target file
`launchpad/docs/corpus/operations/observability/dashboards.md` does not exist. The
reference template (`launchpad/docs/corpus/templates/reference.md`), the
instruction node (`launchpad/docs/corpus/AGENTS.md`), the schema
(`launchpad/docs/corpus/schema/node.schema.json`), and the relevant standards
(evidence, provenance, linking, atomicity, naming, normative-language,
code-references, test-references) have been read in full. Evidence gathered by
opening: `docs/admin/README.md`, `crates/buzz-relay/src/api/admin/{mod.rs,auth.rs}`,
`admin-web/src/App.tsx`, `deploy/charts/buzz/templates/servicemonitor.yaml`,
`deploy/charts/buzz/values.yaml`,
`deploy/charts/buzz-push-gateway/templates/podmonitor.yaml`,
`deploy/charts/buzz-push-gateway/values.yaml`, `deploy/compose/compose.dev.yml`,
`Justfile` (the `admin`/`admin-seed`/`admin-check` recipes),
`launchpad/docs/Observability/current-state/{overview,relay,coverage}.md`,
`launchpad/docs/corpus/layers/observability/prometheus.md`,
`launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md`, and
confirming, by repo-wide grep, zero occurrences of "grafana" in any Helm chart,
compose file, or values file, and zero dashboard-JSON files anywhere in the
repository. `<SCRATCH>/existing-node-ids.txt` lists the 204 ids that resolve on
`origin/launchpad`; it contains no `operations-observability-*` id, and it does
contain `layers-observability-prometheus`, `layers-observability-metrics`,
`capabilities-moderation-operator-dashboard`, and
`architecture-context-relay-operator`.

STEP 1 [independent] — Draft the node body and front matter. Write
`launchpad/docs/corpus/operations/observability/dashboards.md` against the
reference template's required sections (Reference description, Structured
entries, Commands, Boundary, Relationships, Scope and omissions). Content: this
repository ships no dashboard-as-code (no Grafana JSON, no dashboard directory);
the one surface actually called a "dashboard" in-repo is the private,
deployment-scoped admin console (`docs/admin/README.md`,
`crates/buzz-relay/src/api/admin/`, `admin-web/`) for moderation reports and
product feedback, not an observability/metrics dashboard; and the substrate an
observability dashboard would be built from (relay `/metrics` Prometheus
exposition, the Helm chart's opt-in `ServiceMonitor`/`PodMonitor`) exists but no
dashboard definition consumes it in this repository — that work is explicitly
routed to the separate `buzz-infrastructure` repository per PRD #289 / exclusion
row X05 in `launchpad/docs/Observability/current-state/coverage.md`. RUNS HERE.
done when: the file exists, follows the template's required sections, and every
substantive claim has a corresponding `evidence` entry classified FACT,
INFERENCE, or TEAM_KNOWLEDGE per the rules in `AGENTS.md` and
`standards/evidence.md`.

STEP 2 [needs 1] — Validate. Run
`python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.
Fix any reported error (unresolved relationship target, non-resolving citation,
schema violation) and re-run until exit 0.
done when: the validator exits 0.

STEP 3 [needs 2] — Self-review against the issue DoD. Re-read the drafted node
against every Definition of Done bullet in issue #1210, confirm each citation was
actually opened and supports its statement, confirm the scope-and-omissions
section carries both what the node excludes (and who owns it) and what was
expected but could not be verified, and confirm no second hand-authored concept
was folded in.
done when: every DoD bullet is checked off or explicitly named as unsatisfied in
the final report.

STEP 4 [needs 3] — Earn the commit gate. Run, as the sole command in its own Bash
call, from inside the worktree, the corpus test suite (command reproduced
verbatim from the dispatch brief):

<!-- COPY -->
```
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```

Confirm `OK`.
done when: the suite reports `OK` and the verify-gate stamp is recorded.

STEP 5 [needs 4] — Commit locally.

<!-- COPY -->
```
git add -A && git commit -s -m "docs(corpus): document operations/observability/dashboards reference node (#1210)"
```

done when: `git log -1` shows the new commit with a `Signed-off-by` trailer, and
`git status` is clean. Do not push; do not open a PR.

PARALLEL: None — this is a single-document task with no independent parallel
tracks; all five steps are a strict chain.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
before commit. The corpus test suite (Step 4) must report `OK`, run as a
standalone Bash call, before commit. Repo-wide file-size gate: the new file must
stay under 1000 lines (expected — this is a single reference node, not a batch).

BUDGET: One document, one plan file, no code changes. Expected size: comparable
to the already-merged sibling reference/standard nodes (300-450 lines).

OPEN: Whether the admin-web deployment dashboard (`admin-web/` +
`crates/buzz-relay/src/api/admin/`) deserves its own `capabilities`-type corpus
node (parallel to the already-merged `capabilities-moderation-operator-dashboard`,
which covers the *community*-level moderation panel, not this *deployment*-level
one) is not decided by this task and is named in the final report as a candidate
second concept.

LEFT OUT: Documenting Prometheus metrics exposition mechanics in depth — that is
`layers-observability-prometheus`'s subject, already merged; this node references
it rather than restating it. Documenting the metrics catalog, logs, traces, or
alerting — those are sibling tasks (#1212, #1211, #1213, #1209) in the same
Feature, drafted in parallel and unmerged; this node names the boundary in prose
without declaring relationships to them. Any change to `crates/buzz-relay`,
`deploy/charts/`, or `admin-web/` — this task is documentation-only.
