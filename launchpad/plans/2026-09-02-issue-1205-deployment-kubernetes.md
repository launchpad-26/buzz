# Issue #1205 — corpus doc: operations/deployment/kubernetes.md

Stated size: dispatch brief for Feature #618's batch caps this task at 5 steps -> cap: 5 steps

ALREADY TRUE: `node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
`launchpad/docs/corpus/templates/procedure.md`,
`launchpad/docs/corpus/architecture/deployment/kubernetes.md`, and
`launchpad/docs/corpus/layers/observability/{readiness,liveness}.md` are merged on
origin/launchpad. No `launchpad/docs/corpus/operations/` directory exists yet in the
corpus tree (confirmed via `find`) — `operations/deployment/kubernetes.md` does not
exist. Sibling issue #1204 (`operations/deployment/helm.md`) is open and unmerged, so
its target id is not a valid `relationships` target and its path must not be linked in
prose.

STEP 1 [independent] — gather evidence: read
`deploy/charts/buzz/{README.md,values.yaml,Chart.yaml,templates/*.yaml,examples/*.yaml}`,
`launchpad/docs/corpus/architecture/deployment/kubernetes.md`,
`launchpad/docs/corpus/layers/observability/{readiness,liveness}.md`, and the buzz
`CLAUDE.md` ecosystem table, to ground cluster-side prerequisites (namespace, secret,
ingress/Gateway API, storage class, metrics-server/custom-metrics adapter), the
workloads the chart renders, probe behaviour, and the ArgoCD staging boundary in
sources actually opened. done when: every claim planned for the body has an opened
source I can cite by repository-relative path. [Already done in this session before
writing this plan.]

STEP 2 [needs 1] — write front matter + body at
`launchpad/docs/corpus/operations/deployment/kubernetes.md`: `id
operations-deployment-kubernetes`, `type operations`, `status draft`, `origin
launchpad`, `audiences [operator, developer, reviewer]`, one evidence entry per
substantive claim (FACT for opened sources, INFERENCE with confidence where reasoning
goes beyond what a source states, TEAM_KNOWLEDGE with `provided_by` only if an
uncorroborated GitHub source is used). `relationships`: `references`
`architecture-deployment-kubernetes`, `references` `layers-observability-readiness`,
`references` `layers-observability-liveness`, `implements`
`corpus-template-procedure` — all four ids are present in
`<SCRATCH>/existing-node-ids.txt`, i.e. merged on `origin/launchpad`. Body follows
`templates/procedure.md`'s Required sections (Overview, Before you start, one numbered
task sequence, See also, Boundary, Relationships, Scope and omissions), drawing the
boundary against #1204's Helm-mechanics scope in prose only, since
`operations/deployment/helm.md` does not exist yet and must not be linked as a path.
done when: the file exists, every Required section from the template is present, and
no bracketed template placeholder remains.

STEP 3 [needs 2] — RUNS HERE: validate with
`python3 launchpad/project-intelligence/corpus/validate.py` run from the worktree
root; fix whatever it names and re-run until it exits 0. done when: the command's own
exit status is 0.

STEP 4 [needs 3] — commit: run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own Bash call (not piped, not chained with `cd`) to earn
the verify-gate stamp, and confirm the printed result is `OK`. Then, in a separate
Bash call, `git add -A && git commit -s -m "docs(corpus): document
operations/deployment/kubernetes.md (#1205)"`. done when: `git log -1 --format=%B`
shows a `Signed-off-by` trailer and `git status` reports a clean working tree.

PARALLEL: none — single file, single worktree, no fan-out. #1204
(`operations/deployment/helm.md`) is a sibling task running in a different worktree
against a different target file; the two share no file this plan touches.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
commit. The corpus unittest suite must print `OK`, run as its own uninterrupted
command, before the verify-gate will stamp the commit — per the dispatch brief's
process note. `review-adjudicate` and any cross-model review pass are deferred to the
batch owner's later integration pass over the assembled Feature branch, not run here.

BUDGET: small — one hand-authored corpus document plus this plan file; no source code
changes; no test suite beyond the existing corpus validator and its unittest suite.

OPEN: whether Block's private `squareup/block-coder-tf-stacks` staging pipeline
overrides any cluster-side default this node describes (ingress class, storage class,
autoscaling prerequisites) cannot be checked from this checkout — the architecture
node this document references already records that boundary as unverified, and this
node inherits the same limit rather than re-deciding it with a guess.

LEFT OUT: Helm install/upgrade command mechanics and a field-by-field `values.yaml`
walkthrough — sibling issue #1204's `operations/deployment/helm.md`, unmerged, and
therefore not linked as a path anywhere in this node's prose. A live-cluster
validation run — no Kubernetes cluster is available in this environment, and the
scope-and-omissions section says so explicitly rather than silently. Any change to
`deploy/charts/buzz` itself.
