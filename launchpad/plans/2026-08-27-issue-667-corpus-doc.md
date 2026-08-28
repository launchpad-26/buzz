# Plan: issue #667 — corpus doc `architecture/context/relay-operator.md`

ALREADY TRUE: `node.schema.json` is merged and authoritative, `launchpad/docs/corpus/AGENTS.md`
says write against the schema with no per-type template yet, and
`launchpad/docs/corpus/architecture/context/relay-operator.md` does not exist at
`origin/launchpad` tip (`a44cf52fc740ebebbdd671427480d14f0bce0115`).

STEP 1 — Gather evidence for the relay-operator boundary: read `buzz-admin` (crates/buzz-admin),
`deploy/compose/run.sh` + `.env.example`, `launchpad/deploy/run.sh` + `ADR-0005`, the relay's
health/metrics surface (`crates/buzz-relay/src/router.rs`, `config.rs`, `main.rs`), and the
root `AGENTS.md` ecosystem table (buzz-releases / sprout-oss / block-coder-tf-stacks /
sprout-backend-blox). RUNS HERE.

STEP 2 — Write schema-valid front matter (id `architecture-context-relay-operator`, type
`architecture`, status `draft`, origin `launchpad`, audiences `operator`+`developer`) and a
body: boundary statement, actor/system table with each one's relationship to Buzz, a Mermaid
context diagram, and a scope-and-omissions section naming what is left to
container/component-level nodes. RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
against the full tree including the new file. RUNS HERE.

STEP 4 — Commit: earn the verification stamp via
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then stage+commit the plan and the doc together. RUNS HERE.

PARALLEL: none — single hand-authored file, no fan-out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus
unittest suite must report OK before the commit hook accepts the stamp. `review-adjudicate`
and any cross-model review pass are explicitly **deferred** to the batch owner's morning
review — not run in this worktree.

BUDGET: single document, single commit, one draft PR. No code changes, no schema changes.

OPEN: the issue's DoD does not say whether "relay operator" means the Launchpad-fork VPS/
Compose operator (`launchpad/deploy/run.sh` → `deploy/compose/run.sh` → `buzz-admin`), the
upstream Block-operated staging path (`block-coder-tf-stacks` + ArgoCD, a separate repo this
checkout does not contain), or both as instances of one generic role. This document covers
both as named actors reachable from this repository's own evidence, and says so explicitly
rather than silently picking one — a real ambiguity in the issue, not resolved here.

LEFT OUT: `relationships` front matter — at `origin/launchpad` tip no other `architecture`-type
node is merged yet (only `corpus-agents`, `corpus-readme`,
`corpus-standard-confidence`, `corpus-standard-decision-references`, all `governance`/`agent`
nodes about the corpus itself), so there is no existing sibling node to point at. Left for a
later pass once siblings land, per `AGENTS.md`'s own guidance to give the real reason rather
than a boilerplate one. Container/component-level detail of `buzz-admin`, `buzz-relay`
internals, and the Compose/Terraform manifests themselves — out of scope for a context-level
node per the issue's own category tail.
