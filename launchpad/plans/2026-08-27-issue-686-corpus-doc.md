# Issue #686 — corpus doc: architecture/flows/websocket-authentication.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `launchpad`; `launchpad/docs/corpus/architecture/flows/websocket-authentication.md` does not exist yet.

STEP 1 — Gather evidence: read the NIP-42 challenge/response implementation (`buzz-auth/src/nip42.rs`, `buzz-auth/src/lib.rs`, `buzz-auth/src/error.rs`), the relay-side connection lifecycle and AUTH handler (`buzz-relay/src/connection.rs`, `buzz-relay/src/handlers/auth.rs`), the per-handler auth gates (`event.rs`, `req.rs`, `count.rs`), the client-side round trip (`buzz-ws-client/src/connection.rs`, `message.rs`), the kind constants (`buzz-core/src/kind.rs`), and representative e2e coverage (`buzz-test-client/tests/e2e_relay.rs`). RUNS HERE.

STEP 2 — Write front matter (id `architecture-flows-websocket-authentication`, type `architecture`, status `draft`, origin `launchpad`, audiences `developer`+`agent`) and body: trigger/preconditions/outcome, ordered interaction sequence with data movement, trust-boundary crossings (challenge/response, pubkey-binding of subsequent events, ban/allowlist/membership gates), failure/abort/rollback behavior, links to representative verification.

STEP 3 — Validate: run `validate.py` against the full corpus tree; fix and re-run until it exits 0.

STEP 4 — Earn the verification stamp via the corpus unittest suite (sole command in its own tool call), then commit the plan + document together.

PARALLEL: none — single document, single file.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK to earn the commit verification stamp. review-adjudicate and the cross-model review pass are deferred to the batch owner's morning review — not run here.

BUDGET: single document, ~1-2 hours of agent time; no code changes, no new dependencies.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but no other flow/architecture node ids are confirmed merged in the current corpus tree to safely target (a relationship to a nonexistent id is a hard validation error) — this document omits `relationships` rather than guessing a target.

LEFT OUT: no second corpus document, no runtime/product behavior changes, no template creation, no resolution of any open ADR.
