# Issue #678 — document architecture/flows/historical-query.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad` (commit a44cf52fc740ebebbdd671427480d14f0bce0115), and `launchpad/docs/corpus/architecture/flows/historical-query.md` does not exist yet.

STEP 1 — Gather evidence: read `crates/buzz-relay/src/handlers/req.rs` (`handle_req`, `filter_to_query_params`, `filter_fully_pushable`, the visibility gates), `crates/buzz-relay/src/api/bridge.rs` (`query_events`), `crates/buzz-auth/src/nip42.rs`, `crates/buzz-relay/src/handlers/auth.rs`, and the representative e2e tests in `crates/buzz-test-client/tests/e2e_relay.rs` and `e2e_long_form.rs`. RUNS HERE.

STEP 2 — Write front matter (id `architecture-flows-historical-query`, type `architecture`, status `draft`, origin `launchpad`, audiences `[agent, developer]`, no `relationships` — no other flow/architecture node is merged on `origin/launchpad` to point at) and the body: trigger/preconditions/termination, ordered interaction list covering both the WS REQ path and the HTTP `/query` bridge path, the NIP-42/NIP-98 auth and per-event authorization trust-boundary crossings, and failure/abort behavior (mid-loop DB error truncates delivery and still sends EOSE; auth/authorization failures close the subscription instead).

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root; fix and re-run until exit 0.

STEP 4 — Run the corpus unittest suite as the sole prior command, then commit the plan + document in a separate tool call.

PARALLEL: none — single file, single agent.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) must report OK to earn the commit verification stamp. `review-adjudicate` and the cross-model review pass are deferred to the batch owner's morning review — not run here.

BUDGET: single document, one commit, one draft PR. No code changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but the only other merged corpus nodes (`corpus-readme`, `corpus-agents`, `corpus-standard-confidence`, `corpus-standard-decision-references`) are all `governance`/`agent` nodes unrelated to this flow's subject matter — there is no sibling `architecture`/flow node yet to link. Per AGENTS.md's explicit warning against declaring an edge just because it would resolve, `relationships` is omitted rather than invented.

LEFT OUT: no second corpus node; no runtime/product code changes; no per-type template (none exists yet per AGENTS.md).
