# Issue #653 — corpus doc: architecture/containers/cli.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad` (confirmed at commit a44cf52fc740ebebbdd671427480d14f0bce0115); `launchpad/docs/corpus/architecture/containers/cli.md` does not exist yet, and no other `architecture-containers-*` node is merged to link via `relationships`.

STEP 1 (RUNS HERE): Gather evidence for `buzz-cli` — crate structure (`crates/buzz-cli/src/{lib,client,error,validate,links,agent_management,main}.rs`, `src/commands/*.rs`), env-driven config (`BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG`), the relay HTTP surface it calls (`POST /events`, `/query`, `/count`, `/upload`, WS ephemeral), how `buzz-acp` injects those env vars into spawned agent subprocesses and into the `buzz-dev-mcp` server env, and how `buzz-dev-mcp` embeds `buzz-cli` as a library (multicall dispatch to `buzz_cli::run_from_args` when invoked as `buzz`) rather than shelling out to a separate binary.

STEP 2: Write the front matter (id `architecture-containers-cli`, type `architecture`, status `draft`, origin `launchpad`, audiences `[agent, developer]`) and the body — responsibility, technology, ownership boundary, inbound/outbound interfaces, connected containers, deployment/data/security implications, and links to implementation without duplicating it — against `node.schema.json` and `AGENTS.md`, no `relationships` block (nothing merged to point at yet).

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py` and fix until it exits 0 against the full tree including the new file.

STEP 4: Earn the commit stamp with `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole prior command, then commit the plan + doc together.

PARALLEL: none — single file, single task.

GATES: `validate.py` must exit 0 locally before commit. `review-adjudicate` and the cross-model `review-final` pass are deferred to the batch owner's morning review of the full 47-issue run; not run here.

BUDGET: single work session, no infra/tests to stand up — read-and-write task against the current repo tree only.

OPEN: the issue's own DoD asks for "typed relationships appropriate to the node," but at this branch point (`origin/launchpad` tip a44cf52f) no other `architecture-containers-*` sibling is merged, so there is nothing a `relationships` edge could validly target yet — recorded as an explicit, revisit-later omission per `AGENTS.md`'s own guidance on this exact situation, not resolved by guessing a target id.

LEFT OUT: reshaping this node against a future per-type container template (none exists yet, 0/26 merged per `AGENTS.md`); adding `relationships` edges to sibling container nodes (they don't exist on this branch yet); any change to `buzz-cli` runtime behavior.
