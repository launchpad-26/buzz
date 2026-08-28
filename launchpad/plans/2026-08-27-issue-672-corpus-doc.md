# Plan: issue #672 — corpus doc `architecture/deployment/multi-community.md`

ALREADY TRUE: `node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on
`origin/launchpad` (verified at `a44cf52fc`), and
`launchpad/docs/corpus/architecture/deployment/multi-community.md` does not exist yet.

STEP 1 (RUNS HERE): gather evidence — read the row-zero host-binding seam
(`crates/buzz-relay/src/tenant.rs`), the `communities` table and its archival/deletion
migrations, the operator community-provisioning handler, the local dev topology
(`docker-compose.yml`), the production/GitOps Helm chart (`deploy/charts/buzz/`), the
relay's listener/shutdown diagram (`crates/buzz-relay/src/main.rs`), and the A/B
isolation conformance suite (`crates/buzz-test-client/tests/conformance_multitenant.rs`).
Note anything DoD asks for that this checkout cannot verify (the two private
deployment-automation repos named in the top-level `AGENTS.md` ecosystem table).

STEP 2 (RUNS HERE): write the node's front matter (schema-valid, `status: draft`,
`origin: launchpad`, no `relationships` — no other architecture/deployment node is
merged yet) and a body satisfying the issue's DoD checklist plus the category tail:
topology + execution nodes, container/service/data-store mapping, network/persistence/
trust boundaries without secrets, deployment automation as authority, failure/recovery.

STEP 3 (RUNS HERE): run `python3 launchpad/project-intelligence/corpus/validate.py`
from the repo root; fix and re-run until it exits 0.

STEP 4 (RUNS HERE): earn the commit verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan + the new node.

PARALLEL: none — one file, one worktree, no fan-out.

GATES: `validate.py` must exit 0 locally before commit. `review-adjudicate` and the
cross-model final review pass are deferred to the batch owner's morning review — not
run in this session.

BUDGET: single-session, single-document task; no code changes, no test suite beyond the
corpus unittest discovery required for the commit stamp.

OPEN: the issue's DoD asks the node to link "deployment automation/config as authority."
Two of the five ecosystem repos that own deployment automation
(`squareup/sprout-oss`, `squareup/block-coder-tf-stacks`) are private and not present in
this checkout, so their actual pipeline/Terraform content cannot be opened or cited as
FACT here — only their existence and role, per this repo's own `AGENTS.md` ecosystem
table, can be. The node states this as a named gap rather than inventing their content.
This is a real ambiguity in what "linking automation as authority" can mean from inside
this checkout, not something this plan resolves.

LEFT OUT: no second canonical document; no changes to `launchpad/docs/corpus/schema/`,
no per-type template (none exists yet, per `AGENTS.md`); no generated index files.
