# Issue #652 — corpus doc: architecture/containers/agent-runtime.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on `launchpad`; `launchpad/docs/corpus/architecture/containers/agent-runtime.md` does not exist yet.

STEP 1 — gather evidence: read buzz-acp, buzz-agent, buzz-dev-mcp, buzz-persona, sprig source/READMEs/Cargo manifests, desktop's managed_agents spawn path, docs/remote-agents.md, and the sprig/sprig-image CI workflows to ground every claim in code actually opened. RUNS HERE.

STEP 2 — write front matter (id `architecture-containers-agent-runtime`, type `architecture`, status `draft`, origin `launchpad`, audiences `developer`+`operator`+`reviewer`) and a body covering: container responsibility/technology/ownership boundary, inbound/outbound interfaces and directly-connected containers, deployment/data/security implications, and links to implementation without duplicating it — satisfying issue #652's DoD checklist plus the containers category tail.

STEP 3 — run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0 against the full tree.

STEP 4 — commit (plan + doc) once the corpus unittest suite reports OK, then push and open a draft PR against `launchpad`.

PARALLEL: none — single hand-authored file, one worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK to earn the commit verification stamp. review-adjudicate and the cross-model final-review pass are explicitly deferred to the batch owner's morning review — not run in this worktree.

BUDGET: single document, no code changes, no test changes — small.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but REPO FACTS states a relationship target naming an id no loaded node carries is a hard validation error, and 0 of 26 architecture-track nodes are merged yet (per PRD #605 progress) — so no valid target exists at this revision. This node declares no `relationships`, following the precedent set by `corpus-standard-confidence` and `corpus-readme`, both of which made the same choice for the same reason and left it to the first sibling that merges. This is a real ambiguity in the DoD text left unresolved here, not silently decided.

LEFT OUT: no template exists yet for `type: architecture` (0 of 26 merged per PRD #605), so this node is written directly against node.schema.json per launchpad/docs/corpus/AGENTS.md's explicit instruction, and may be reshaped by a later per-type template task. Corpus generated indexes are not touched — none exist yet to regenerate.
