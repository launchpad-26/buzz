# Plan: issue #687 — corpus doc `architecture-flows-websocket-connection`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(confirmed at `a44cf52fc740ebebbdd671427480d14f0bce0115`); the target file
`launchpad/docs/corpus/architecture/flows/websocket-connection.md` does not
exist yet (confirmed with `test -f`).

STEP 1 (RUNS HERE): Gather evidence — read `crates/buzz-relay/src/router.rs`
(`nip11_or_ws_handler`), `crates/buzz-relay/src/connection.rs`
(`handle_connection`, `handle_active_connection`, `recv_loop`, `send_loop_inner`,
`heartbeat_loop`, `handle_text_message`, `enforce_ws_admission`, `ConnectionState`,
`AuthState`), `crates/buzz-relay/src/state.rs` (`run_registered_community_connection`,
`CommunityConnectionControl`, `CommunityDisconnectReason`, `disconnect_pubkey`,
`disconnect_community`), `crates/buzz-relay/src/handlers/auth.rs` (`handle_auth`,
`extract_auth_tag_json`), `crates/buzz-relay/src/admission.rs`, and locate
representative verification in `crates/buzz-test-client/tests/e2e_relay.rs`.

STEP 2: Write front matter (id, type: architecture, status: draft, origin: launchpad,
audiences, evidence ledger classifying each claim FACT/INFERENCE/TEAM_KNOWLEDGE with
real citations) and a body covering trigger, preconditions, ordered interactions,
trust-boundary crossings, failure/abort/rollback behavior, and verification links, per
issue #687's DoD plus the category:flows DoD tail.

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until it exits 0.

STEP 4: Earn the verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan and the new document together.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model review-final pass are deferred to the batch
owner's morning review — not run in this session.

BUDGET: single session, no live model spend beyond this authoring pass.

OPEN: the issue's DoD does not specify whether a `relationships` edge is expected;
per REPO FACTS, the only currently-merged corpus node with a stable id is
`corpus-agents` (plus the standards/schema-overview nodes), none of which this flow
node has a typed relationship to describe, so `relationships` is omitted rather than
invented — consistent with `AGENTS.md`'s instruction to enumerate what exists and give
the real reason rather than copy a stale justification.

LEFT OUT: no second canonical document; no runtime/product code changes; no template
authored (none exists yet per `AGENTS.md`); no resolution of the open provenance
question (#1321) about whether a recorded revision may stay put across edits.
