# Issue #1028 — layers/authentication/nip-42-authentication.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, and `launchpad/docs/corpus/templates/concept.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/layers/authentication/nip-42-authentication.md` does not exist yet (`launchpad/docs/corpus/layers/` does not exist at all). `launchpad/docs/corpus/architecture/flows/websocket-authentication.md` (id `architecture-flows-websocket-authentication`) is already merged and documents the step-by-step WebSocket AUTH round trip in detail — this node must not re-derive that flow; it explains the NIP-42 *concept* (what it is, why it exists, its boundary) and links to the flow node rather than duplicating its steps.

STEP 1  Gather evidence: open `crates/buzz-auth/src/nip42.rs` (challenge generation, `verify_nip42_event`), `crates/buzz-core/src/kind.rs` (`KIND_AUTH = 22242`), `crates/buzz-auth/src/lib.rs` (module doc: NIP-42 vs NIP-98 auth paths, security invariants), `crates/buzz-auth/src/error.rs` (`AuthError` variants), `crates/buzz-auth/src/nip98.rs` (the HTTP-auth sibling, for the boundary section), and `crates/buzz-relay/src/{connection.rs,handlers/auth.rs,nip11.rs}` (where the concept is consumed). Record `git rev-parse HEAD`. Confirm the DoD's concept-shaped bullets (one-sentence definition, boundaries/non-goals, links to related concepts/implementation/verification, examples that don't introduce a second concept) map to `templates/concept.md`'s required sections. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-authentication-nip-42-authentication`, type `layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, `references` relationships to `architecture-flows-websocket-authentication` (the merged flow node this concept underlies) and `architecture-principles-signed-events` (the merged architecture principle NIP-42's own security property depends on) — both exist merged on `origin/launchpad`; no other merged node is a legitimate target) and the body against `templates/concept.md`'s required sections: Definition (one sentence, FACT-cited to `nip42.rs`/`kind.rs`), Use cases, Boundary against NIP-98 HTTP Auth and against the already-merged flow node, Scope and omissions.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review — not run here.

BUDGET: small — one document, no code changes, evidence gathering scoped to ~7 source files already located.

OPEN: Whether `layers` is the correct `type` for a concept about an authentication mechanism (as opposed to `architecture`, which the sibling flow node uses) is decided from `node.schema.json`'s description ("the corpus surface this node documents") plus the issue's own literal target path (`layers/authentication/...`) and title — `layers` is used because the issue itself places this node on that surface, not because the concept template mandates any particular `type`.

LEFT OUT: No re-derivation of the WebSocket AUTH state machine, message-by-message sequence, or failure table — `architecture-flows-websocket-authentication` already owns that and is linked instead. No new concept node for NIP-98 HTTP Auth (out of scope; named only as a boundary/comparison, not documented in depth here). No relationships beyond the flow-node and signed-events links — no other merged corpus node is a legitimate target for an authentication concept at the recorded revision.
