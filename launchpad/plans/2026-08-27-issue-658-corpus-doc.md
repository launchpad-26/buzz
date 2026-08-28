# Issue #658 — corpus doc: architecture/containers/push-gateway.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/architecture/containers/push-gateway.md` does not exist yet.

STEPS:
1. Gather evidence: read `crates/buzz-push-gateway/{main,lib,http,config,apns,grant,model}.rs`, its migration (`crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql`), `docs/push-gateway-deployment.md`, and the relay-side integration points (`crates/buzz-relay/src/{push_runtime,nip11}.rs`, `crates/buzz-relay/src/handlers/push_lease.rs`, `crates/buzz-relay/src/config.rs`). RUNS HERE.
2. Write front matter (id `architecture-containers-push-gateway`, type `architecture`, status `draft`, origin `launchpad`, audiences `developer`+`operator`, evidence ledger with FACT/INFERENCE entries only for what was actually opened) and the body against the category-containers DoD tail: responsibility/technology/ownership boundary, inbound/outbound interfaces and directly connected containers, deployment/data/security implications, and links to implementation without duplicating it.
3. Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
4. Commit the plan + doc together with a signed-off commit; push and open a draft PR.

PARALLEL: none — single file, single worktree.

GATES: `validate.py` must exit 0 locally before commit. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK (earns the commit verification stamp). review-adjudicate and the cross-model review pass are deferred to the batch owner's morning review — not run here.

BUDGET: single document, one sitting, no code changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but the only other merged corpus nodes (`corpus-readme`, `corpus-agents`, `corpus-standard-confidence`, `corpus-standard-decision-references`) are all `governance` nodes about the corpus itself, not architecture nodes this container doc would meaningfully link to — so `relationships` is omitted per REPO FACTS ("omit unless you can confirm the target id already exists in the merged corpus"), not resolved by inventing an edge.

LEFT OUT: no per-type template exists (0 of 26 merged) — the node is written directly against `node.schema.json` per `launchpad/docs/corpus/AGENTS.md`, and a later reshape task will apply whatever template lands. No relay-side event-kind corpus node is created even though push-gateway integration touches NIP-PL kind:30350 — that is a separate node's subject, not folded in here.
