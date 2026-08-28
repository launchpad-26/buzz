# Issue #685 — corpus flow node: search-query

ALREADY TRUE: node.schema.json is merged and authoritative on `origin/launchpad`; `launchpad/docs/corpus/AGENTS.md` says write against it with no per-type template yet; `launchpad/docs/corpus/architecture/flows/search-query.md` does not exist on this branch or on `origin/launchpad`.

STEP 1 — Gather evidence: read `crates/buzz-search/src/query.rs`, the WS REQ search path (`crates/buzz-relay/src/handlers/req.rs`: `handle_req`'s search branch, `handle_search_req`), the HTTP bridge path (`crates/buzz-relay/src/api/bridge.rs`: `query_events`, `query_events_authed`, `handle_bridge_search`, `search_hit_accepted`, `verify_bridge_auth_with_options`), the FTS indexing migrations (`migrations/0001`, `0005`, `0008`, `0014`), `buzz-cli`'s `messages search` (`crates/buzz-cli/src/commands/messages.rs::cmd_search`, `client.rs::query`), and the representative e2e coverage (`crates/buzz-test-client/tests/e2e_nostr_interop.rs`). RUNS HERE.

STEP 2 — Write front matter (id `architecture-flows-search-query`, type `architecture`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`) with one evidence entry per claim, classified FACT/INFERENCE honestly, plus a commit-citation provenance entry. Write the body: trigger/preconditions/termination, ordered interactions across both WS REQ and HTTP `/query` entry points, the two-layer FTS-candidate-then-reauthorize design, auth/trust-boundary crossings (NIP-98 host binding, replay, relay membership, sensitive-kind gates run before the search branch), failure/abort behavior (empty query short-circuit, mixed-filter rejection, unmapped-host 404, search-error break), and a scope/omissions section naming the fresh-install-vs-brownfield FTS allowlist divergence as an open item for the batch owner.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root; fix and re-run until exit 0.

STEP 4 — Earn the verification stamp with `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole prior command, then commit the plan + node file in a separate call.

PARALLEL: none — single file, single worktree.

GATES: `validate.py` must exit 0 locally before commit. `review-adjudicate` and the cross-model final-review pass are deferred to the batch owner's morning review of the 47-issue overnight run — not run here.

BUDGET: single session, no code changes, read-only exploration plus one Markdown file.

OPEN: the issue's DoD does not say whether a flow node must reconcile the fresh-install vs. brownfield FTS-allowlist divergence (migrations 0001/0005/0008/0014) as one fact or flag it — the node documents both and leaves reconciliation to the reader rather than asserting one is "the" current behavior for an arbitrary deployment.

LEFT OUT: no `relationships` — no sibling architecture/flow node is merged on `origin/launchpad` yet (checked via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`); no per-type template exists to conform to; no runtime behavior change.
