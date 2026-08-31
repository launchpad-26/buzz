# Issue #1142 — corpus doc: layers/observability/prometheus.md

Stated size: no `Size` line on issue #1142 -> cap: 5 steps (per this task's own
briefing, which caps this batch's plans at 5 steps).

ALREADY TRUE: node.schema.json, AGENTS.md and the `concept.md` template are merged on
`launchpad`; `launchpad/docs/corpus/layers/` does not exist anywhere on `origin/launchpad`
yet (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`)
-- so none of the nine sibling observability docs (#1135-#1145) are merged, contrary to
this task's briefing that #1138/#1139 already landed; `git ls-tree` is the ground truth
used here, not the briefing. `crates/buzz-relay/src/metrics.rs` (`PrometheusBuilder`,
`install()`), `deploy/charts/buzz/templates/servicemonitor.yaml`, and `prometheus.yml`
(dev-compose scrape config) already implement and configure the exposition mechanism this
node documents.

STEP 1 [independent] Gather evidence: read `crates/buzz-relay/src/metrics.rs` in full
(recorder install, bucket config, `/metrics` middleware skip-list), `main.rs`'s
listener-4 doc block and `relay_metrics::install(...)` call site, `config.rs`'s
`BUZZ_METRICS_PORT` default, workspace `Cargo.toml` pins for
`metrics`/`metrics-exporter-prometheus`/`metrics-util`,
`deploy/charts/buzz/templates/service.yaml` + `servicemonitor.yaml` + `values.yaml`
(named `metrics` port, opt-in `serviceMonitor`), `deploy/compose/compose.dev.yml` +
root `prometheus.yml` (local scrape target), and `router.rs`'s reference to
`track_metrics`. ← RUNS HERE.
        done when: every claim planned for STEP 2's evidence ledger has a real
        path/line citation actually opened in this step (no citation invented from
        memory).

STEP 2 [needs 1] Write front matter (id `layers-observability-prometheus`, type
`layers`, status `draft`, origin `launchpad`, audiences `developer`+`operator`, no
`relationships` -- see OPEN) and a body following the `concept.md` template's
required sections (Definition, background, use cases, scope-and-omissions), scoped
strictly to exposition-format mechanics: the embedded Prometheus HTTP listener bound
by `PrometheusBuilder` (separate from the axum app router), the `GET /metrics` text
format it serves, the exporter crate/version pins, and scrape wiring (Helm
ServiceMonitor + dev-compose). Explicitly out of scope: the conceptual metrics
catalog (names, what each metric means) -- that is sibling #1140's territory, named
in prose only since no `relationships` target exists yet.
        done when: `launchpad/docs/corpus/layers/observability/prometheus.md` exists,
        every bullet in issue #1142's own DoD checklist is satisfied, and every
        substantive claim has an `evidence` entry classified FACT/INFERENCE/
        TEAM_KNOWLEDGE with real citations.

STEP 3 [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`;
fix and re-run until the new node produces zero FAIL-class errors (pre-existing
UNVERIFIED noise and up to ~21 pre-existing failures elsewhere are known and out of
scope).
        done when: the validator's output for this run names zero FAIL lines
        attributable to `layers/observability/prometheus.md`.

STEP 4 [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in one tool call; must print `OK`. In a separate tool call,
`git add` the new document + this plan and `git commit -s`. Do not push and do not
open a PR -- this ships as part of one combined PR for all 36 #611 children, per the
batch owner's plan change.
        done when: the unittest command's own output (not a summary of it) shows
        `OK`, and `git log -1` on this branch shows a new signed commit containing
        exactly the two files.

PARALLEL: none -- single hand-authored file, one worktree. Eight sibling agents are
drafting #1135/#1136/#1137/#1140/#1141/#1143/#1144/#1145 concurrently in their own
worktrees; no file overlap.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit clean for
this node. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report `OK` to earn the commit verification stamp. review-adjudicate and the
cross-model final-review pass are deferred to the batch owner's review of the combined
PR -- not run in this worktree. No push, no `gh pr create`.

BUDGET: one document, no code changes, no test changes -- small.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but
`AGENTS.md`'s node-creation step 9 requires a relationship target to exist on the
branch being merged into, checked via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` -- and that tree carries no `layers/` node at all yet, including
no `layers-observability-metrics` node for the conceptual-catalog sibling this document
would naturally reference. This node declares no `relationships`, following the
precedent already set by `corpus-readme`, `corpus-standard-confidence`, and the
`architecture-containers-agent-runtime` (#652) node, all of which made the same choice
for the same reason. A `references` edge to the metrics-catalog sibling is left for
whichever of the two nodes merges second, or a follow-up edit.

LEFT OUT: no per-type template exists for `type: layers` specifically (no `layers`-typed
node is merged to compare against), so this node is built directly against
`node.schema.json` + `AGENTS.md`'s creation steps, using the corpus's general-purpose
`concept.md` template (already merged, form-scoped rather than surface-scoped) for body
shape, and may be reshaped by a later per-type standard. Corpus generated indexes are
not touched -- none exist yet to regenerate.
