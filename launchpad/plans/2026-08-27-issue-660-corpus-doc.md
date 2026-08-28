# Plan: issue #660 — corpus doc `architecture/containers/relay.md`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(commit a44cf52fc740ebebbdd671427480d14f0bce0115); the target file
`launchpad/docs/corpus/architecture/containers/relay.md` does not exist.

STEP 1 — Gather evidence: read `ARCHITECTURE.md` (system diagram, crate
dependency hierarchy, "buzz-relay — The Server" section), `crates/buzz-relay/`
source (`main.rs`, `router.rs`, `state.rs`, `config.rs`, `mesh_boot.rs`,
`push_runtime.rs`), `Dockerfile`, `.github/workflows/docker.yml`,
`deploy/charts/buzz/values.yaml`, and `migrations/`. RUNS HERE.

STEP 2 — Write front matter (id `architecture-containers-relay`, type
`architecture`, status `draft`, origin `launchpad`, audiences
`[developer, operator, reviewer]`, evidence ledger citing only paths actually
opened in Step 1) and body covering the issue's DoD checklist plus the
category-containers tail (responsibility/tech/ownership boundary, inbound and
outbound interfaces, deployment/data/security links, implementation-path
links without duplicating detail).

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
must exit 0 against the full tree including the new file. Fix and re-run
until clean.

STEP 4 — Commit: earn the verification stamp via
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then stage and commit the plan file and the new
node.

PARALLEL: none — single file, single writer.

GATES: `validate.py` only. `review-adjudicate` and the cross-model final
review pass are deferred to the batch owner's morning review, not run in this
worktree.

BUDGET: single-document task; no multi-step build, no code changes, no test
suite beyond the corpus validator/unittest gate above.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node"
but also warns that a `relationships[].target` naming an id no loaded node
carries is a hard validation error. At this revision no sibling
`architecture/containers/*` or other corpus node with a plausible target id
(e.g. a deployment or data-store node) is merged, so this node omits
`relationships` entirely rather than guessing at an id that may not exist —
same posture `standards/confidence.md` documents taking for the same reason.
This is left as a real ambiguity, not silently resolved: a later pass, once
sibling nodes land, should add the edges (implements/references to any
deployment, data-store, or security-boundary nodes that get created).

LEFT OUT: no second canonical document; no changes to `crates/buzz-relay`
source, `deploy/charts/buzz/`, or CI workflows; no attempt to describe the
Block-internal (`squareup/*`) deployment pipeline in detail — only what this
document's own evidence (chart, Dockerfile, workflow file, all in this repo)
supports is claimed, and the internal-org pipelines are linked to at the
level `AGENTS.md`'s ecosystem table already documents, not re-derived.
