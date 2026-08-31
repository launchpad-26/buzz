# Plan: issue #691 — document architecture/principles/fail-closed-boundaries.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/architecture/principles/fail-closed-boundaries.md` does not yet exist.

STEP 1 — Gather evidence for the fail-closed row-zero host-binding contract and its sibling gates (pubkey allowlist, ban check, restriction-state check), the ADR-0026 fail-open contrast, and the TLA+ `Inv_HostBindingFence` / `Inv_ResolutionFence` / `Inv_NoTenantContextFailsClosed` conformance invariants. RUNS HERE.

STEP 2 — Write front matter (id `architecture-principles-fail-closed-boundaries`, type `architecture`, status `draft`, origin `launchpad`) and body stating the invariant as one MUST/MUST-NOT property, its scope, enforcement points, observable failure behavior, and verification links, per issue #691's DoD and its category tail.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4 — Commit (plan + doc) and open a draft PR against `launchpad`.

PARALLEL: none — single file, single author.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and the cross-model review pass are deferred to the batch owner's morning review of issue #608's overnight batch, not run here.

BUDGET: single session, no rebuild loops beyond validator fix-ups; one background `cargo test -p buzz-relay --lib tenant::tests` run for evidence corroboration only (not required for the corpus stamp).

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but no other `architecture`- or `principles`-typed node is merged on `origin/launchpad` yet (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), so `relationships` is omitted per `AGENTS.md`'s own instruction rather than resolved silently.

LEFT OUT: this node does not attempt to catalogue every fail-closed call site in the relay (there are dozens); it states the invariant once, cites the row-zero host-binding contract as its canonical enforcement point, and cites three sibling auth/ingest gates as corroborating instances of the same pattern rather than an exhaustive audit.
