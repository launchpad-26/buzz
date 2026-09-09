# Issue #973 — interfaces/acp/message.md

Stated size: issue #973's body has no Size line; the dispatching task's own instructions state a cap directly  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
and `launchpad/docs/corpus/templates/interface.md` are merged on `origin/launchpad`.
`launchpad/docs/corpus/interfaces/` does not exist on `origin/launchpad` at all yet (`git
ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists only `AGENTS.md`,
`README.md`, `schema/**`, `standards/**`, `architecture/**`, `templates/**`); no sibling
ACP node (`#974` protocol, `#975` session, `#976` tool-call) is merged, so `message.md` has
zero legitimate `relationships` targets right now. `node.schema.json`'s `type` enum has no
`interfaces` or `interfaces-acp` value — the only interface/event-shaped member is the single
combined token `interfaces-events` (confirmed by reading the schema directly and by
`corpus-template-interface`'s own "A note on `type`" section, which states the same enum
member is used for both interface-shaped and event-kind-shaped nodes).

STEP 1  [independent] Gather evidence from `crates/buzz-acp/src/acp.rs` (the only file implementing the ACP
JSON-RPC wire format per its own module doc comment): the `session/prompt` request shape
(`build_prompt_params`, `session_prompt_blocks_with_idle_timeout`), the content-block shape
actually sent (`{"type":"text","text":...}` only — no image/resource blocks are built anywhere
in this crate), the inbound `session/update` message-carrying kinds handled in
`handle_session_update` (`agent_message_chunk`, `agent_thought_chunk` — as distinct from the
tool-call kinds `tool_call`/`tool_call_update` and the session-lifecycle kinds
`session_info_update`/`usage_update`/`available_commands_update`/`plan`/`keepalive`), the
terminal response shape (`stopReason` parsed by `parse_stop_reason`/`StopReason::from_str`),
and the JSON-RPC error shape (`agent_error_from_json`, `AcpError::AgentError{code,message}`,
the `-32601`/`-32602` codes exercised by existing tests at `acp.rs:3516-3546`). Also read
`crates/buzz-acp/README.md`'s ACP spec link (`https://agentclientprotocol.com/`) for the
external authoritative reference, and `initialize()`/`authenticate()` (`acp.rs:611-630`) for
the protocol-version-negotiation and auth context a single message turn sits inside (cited,
not restated). done when: every claim listed above has been traced to a specific `acp.rs`
line range or the README, noted for use in STEP 2's evidence ledger. ← RUNS HERE

STEP 2  [needs 1] Write the front matter: `id: interfaces-acp-message`, `type:
interfaces-events` (the only schema-legal interface-shaped value — see ALREADY TRUE),
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, no
`relationships` (no sibling ACP node or any other legitimate target is merged on
`origin/launchpad` yet), and one `evidence` entry per substantive claim (FACT for everything
opened directly in `acp.rs`/README in STEP 1, TEAM_KNOWLEDGE with `provided_by` naming the
issue for anything sourced only from issue text, INFERENCE with `confidence` for any reasoned
extrapolation). done when: the YAML front matter is written and every claim in it traces to a
source gathered in the prior step.

STEP 3  [needs 2] Write the body against `templates/interface.md`'s required sections
(Interface description; Operations table pointing at code symbols, never restating them;
Contract and stability — versioning/error/ordering; Boundary statement; Relationships;
Scope and omissions), scoped tightly to the **message** exchanged inside one `session/prompt`
turn: outbound content blocks, inbound `agent_message_chunk`/`agent_thought_chunk` streamed
updates, and the terminal `stopReason` response — explicitly excluding tool-call updates and
session lifecycle (`session/new`/`session/cancel`) as neighboring, not-yet-written sibling
nodes' territory, named by filename in prose only (`interfaces/acp/session.md`,
`interfaces/acp/tool-call.md`, `interfaces/acp/protocol.md`), never as an unresolvable
`relationships` edge. Cover every issue DoD bullet: inputs/messages, outputs/responses,
error/rejection (JSON-RPC error object → `AcpError::AgentError`), auth/versioning (prose-link
to `initialize`/`authenticate` and the pinned `protocolVersion: 2`, not restated in depth —
that is `protocol.md`'s subject), ordering (single in-flight prompt per session via
`has_in_flight_prompt`/monotonic `next_id` request correlation), the authoritative spec link
(`https://agentclientprotocol.com/`), one valid example (the `session_prompt_request_format`
test's request JSON plus a matching `{"stopReason":"end_turn"}` result), and one failure
example (a JSON-RPC error object, e.g. `{"code":-32602,"message":"Invalid params"}`, exercised
by `goose_system_prompt_preserves_invalid_params_as_error`). done when: the body file exists
at `launchpad/docs/corpus/interfaces/acp/message.md` with all required template sections
present.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repo root. Compare the FAIL-line count/names against the 21 known pre-existing failures
(architecture-containers-postgres, architecture-context-human-user,
architecture-flows-event-ingestion, architecture-flows-workflow-execution,
architecture-principles-community-is-security-boundary, and the `corpus-template-*` nodes —
tracked as issue #1951) to confirm this new node introduces zero additional failures. Fix and
re-run until the only failures present are the 21 pre-existing ones. done when: validate.py's
FAIL set is exactly the pre-existing 21 (or a subset, never more).

STEP 5  [needs 4] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call and confirm it prints `OK` — this is the commit-gate stamp. Only after that, in a separate call, `git add` the plan file and the new corpus doc and `git commit -s`. done when: the gate prints `OK` and the commit exists with both files staged.

PARALLEL: none — one document, one plan, sequential single-file task; no independent branch
of work exists to run alongside it.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must introduce zero new FAIL
lines beyond the 21 pre-existing ones (issue #1951). The corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
must print `OK` before the commit is made, per the task's own commit-gate instruction — no
`--no-verify`, no manual stamp editing if the gate refuses.

BUDGET: small — one corpus document (~150-250 lines of Markdown), evidence gathering scoped to
one source file (`crates/buzz-acp/src/acp.rs`, plus its README) already read in full during
planning; no code changes, no second document.

OPEN: Whether `agent_message_chunk`/`agent_thought_chunk` are the complete ACP-spec set of
message-shaped `session/update` kinds, or whether upstream ACP also defines a
`user_message_chunk` kind this codebase simply never emits/receives, was not resolved by
fetching the external ACP spec (`https://agentclientprotocol.com/`) directly — only this
repository's own code was opened. The body states this as an explicit "expected but not
verified" gap rather than asserting completeness against the external spec.

LEFT OUT: `session/new`, `session/cancel`, and session lifecycle generally
(`interfaces/acp/session.md`'s subject, `#975`, unmerged). `tool_call`/`tool_call_update`
session-update kinds and permission requests (`interfaces/acp/tool-call.md`'s subject, `#976`,
unmerged). The JSON-RPC 2.0 envelope, `initialize`/`authenticate`, and protocol-version
negotiation in depth (`interfaces/acp/protocol.md`'s subject, `#974`, unmerged) — referenced
in prose only, not restated. No `relationships` entries to any of the three sibling nodes or
to `capabilities/agents/acp.md` (`#703`) or `implementation/crates/buzz-acp.md` (`#916`) since
none is merged on `origin/launchpad` yet — the first sibling node to merge is the natural
moment to add those edges, per `AGENTS.md`'s own relationship-target rule.
