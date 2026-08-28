# Issue #1030 — layers/authentication/websocket-challenge.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
are merged on `origin/launchpad`; `launchpad/docs/corpus/layers/authentication/websocket-challenge.md`
does not exist yet, and no `layers/` directory exists in the corpus yet either. The broader NIP-42 flow
is already documented at `architecture-flows-websocket-authentication`
(`launchpad/docs/corpus/architecture/flows/websocket-authentication.md`, merged, `status: draft`) — it
narrates the whole connection-to-authenticated round trip. This task is narrower: the challenge string
itself (generation, wire shape, verification, client-side handling), not the full handshake. The sibling
task #1028 (`layers/authentication/nip-42-authentication.md`) is being authored in parallel and does not
exist on `origin/launchpad` yet — no `relationships` edge to it is possible.

STEP 1  Gather evidence directly from source, not from the existing flow doc's prose: `generate_challenge`
and the `AuthState::Pending{challenge}` storage (`crates/buzz-auth/src/nip42.rs`,
`crates/buzz-relay/src/connection.rs`), the wire format (`RelayMessage::auth_challenge`,
`ClientMessage::Auth` in `crates/buzz-relay/src/protocol.rs`), `verify_nip42_event`'s challenge-specific
checks (`crates/buzz-auth/src/nip42.rs`), the client-side wait/parse/1024-byte-cap and
`build_auth_event`/`EventBuilder::auth` (`crates/buzz-ws-client/src/connection.rs`,
`crates/buzz-ws-client/src/message.rs`), and `KIND_AUTH = 22242` (`crates/buzz-core/src/kind.rs`). ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-authentication-websocket-challenge`, type
`layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, one `references`
relationship to `architecture-flows-websocket-authentication` since that node is merged on
`origin/launchpad`) and the body, shaped like the corpus's `concept` template (closest fit — no `layers`
template exists yet) per the issue's four concept-specific DoD bullets: one-sentence definition up front,
explicit boundary against the full handshake flow and against NIP-98/NIP-OA, a worked example, and a
scope/omissions section.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until
exit 0.

STEP 4  [needs 3] Run the corpus unittest suite as the sole prior command to earn the verification stamp,
then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task. (#1028 is a separate task in the same batch, authored in a
separate worktree; no shared state.)

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and
the cross-model final review pass are deferred to the batch owner's review — not run here.

BUDGET: small — one document, no code changes, evidence scoped to ~5 files already located.

OPEN: Whether `#1028`'s `nip-42-authentication.md` will end up being the more natural target for a
`references` edge once it merges (this node's subject is a strict subset of that one's). Left for a later
edit once #1028 lands, per `AGENTS.md`'s "add relationships only to nodes that exist on the branch you are
merging INTO."

LEFT OUT: No re-narration of the full connection lifecycle, ban/allowlist/membership gates, or NIP-OA
delegation — those are `architecture-flows-websocket-authentication`'s territory, referenced rather than
duplicated. No claim about NIP-98 HTTP auth (`crates/buzz-auth/src/nip98.rs`) beyond naming it as a
boundary. No relationship to `#1028`'s node — not merged yet.
