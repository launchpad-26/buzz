# Plan: issue #657 — corpus doc `architecture-containers-postgres`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad` (checked at commit a44cf52fc740ebebbdd671427480d14f0bce0115); `launchpad/docs/corpus/architecture/containers/postgres.md` does not exist yet.

STEP 1 — Gather evidence: read `crates/buzz-db` (Cargo.toml, lib.rs pool/config code, migration.rs), `crates/buzz-relay/src/main.rs` startup sequence (DbConfig wiring, BUZZ_AUTO_MIGRATE gate, audit pool, search pool), `.env.example`, `docker-compose.yml` postgres service, and `migrations/0001_initial_schema.sql`. RUNS HERE.

STEP 2 — Write front matter (id `architecture-containers-postgres`, type `architecture`, status `draft`, origin `launchpad`, audiences `[developer, operator]`, no `relationships` — no sibling architecture/containers node is merged yet to point at) and body covering: container responsibility/technology/ownership boundary, inbound/outbound interfaces and directly connected containers, deployment/data/security implications, and links to implementation paths without duplicating their detail.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.

STEP 4 — Commit: run the corpus unittest suite as the sole prior command to earn the verification stamp, then stage and commit the plan + document.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0). `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must report OK, run alone to earn the commit stamp). review-adjudicate and the cross-model final-review pass are explicitly deferred to the batch owner's morning review — not run in this task.

BUDGET: small — one document, no code change, target under ~1-2 hours of agent time.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node" but no sibling `architecture/containers/*` or other node this document would naturally reference is merged on `origin/launchpad` yet (checked via `find launchpad/docs/corpus/architecture -type f`, which does not exist). A `relationships[].target` naming an unmerged id is a hard validation error per the schema's own rule and per `corpus-standard-confidence.md`'s precedent (it omitted relationships for the identical reason). This document therefore omits `relationships` rather than inventing a target; the batch owner should add edges once sibling architecture nodes land. Also open: `AGENTS.md`'s top-level repo-structure comment says migrations are "auto-applied on relay startup," but `crates/buzz-relay/src/main.rs` only runs them when `BUZZ_AUTO_MIGRATE` is truthy (default off) — the document records the code behavior as FACT and notes the discrepancy rather than resolving which source is stale.

LEFT OUT: no per-type template exists for `architecture`/containers nodes (0 of 26 merged per `AGENTS.md`), so this document is written directly against `node.schema.json` and is expected to be reshaped by a later templating task, per the issue's own instruction. No second canonical document is created. No runtime/product behavior is changed.
