# Plan: issue #708 — document capabilities/agents/agent-response.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/agents/agent-response.md` does not exist yet (confirmed via
  `test -f` in the worktree).
- `launchpad/docs/corpus/templates/capability.md` exists and is the template to follow: required
  sections are Capability statement, Maturity, Boundary, Relationships, Scope and omissions,
  `type: capabilities`.
- `origin/launchpad`'s corpus tree currently has zero `capabilities/` nodes — this will be the
  first. It does have `architecture/flows/agent-turn.md` (`id: architecture-flows-agent-turn`),
  which explicitly excludes "The Buzz CLI surface the agent subprocess calls during a turn ...
  that is the CLI's own contract, not the harness's turn mechanics" — this is exactly the gap
  `agent-response` fills, and it is a valid `references` target since it is merged.
- Evidence gathered from reading source directly:
  - `crates/buzz-agent/README.md` (Reply Guard section) — an agent's generated text is invisible
    to humans; only actions (tool calls) are Buzz-visible, and Reply Guard reminds a model whose
    turn is about to end with no recognized `messages send`/`reactions add` call.
  - `crates/buzz-cli/src/commands/mod.rs` (`parse_write_response`) and
    `crates/buzz-cli/src/client.rs` (`normalize_write_response`, `publish_ephemeral_event`) — the
    standard write-response shape `{event_id, accepted, message}`, and a `duplicate`/`duplicate:`
    message maps to `CliError::Conflict` (exit 5).
  - `crates/buzz-cli/src/agent_management.rs` (`build_create`, `build_update`) and
    `crates/buzz-cli/src/commands/agents.rs` (`AgentsCmd::DraftCreate`/`DraftUpdate` dispatch) —
    `buzz agents draft-create`/`draft-update` build a NIP-OA-encrypted observer frame
    (kind:24200), and the CLI response is the *relay's* ephemeral-publish response
    (`{event_id, accepted, message}`) with `request_id`, `action`, and `saved: false` merged in,
    plus a fixed message that nothing changes until the owner saves it.
  - `desktop/src-tauri/src/managed_agents/nest_skill.md` — states the same output-contract split
    in prose: "Write commands: all return `{event_id, accepted, message}`. ... Agent draft
    commands add `{request_id, action, saved: false}` because they only open an owner-reviewed
    Desktop draft."
  - `desktop/src/features/agents/agentManagement.ts` and `useAgentManagement.ts` — desktop parses
    the decrypted observer payload into a typed `AgentManagementRequest` and surfaces it as an
    editable create/update persona form; nothing is created/changed until the owner submits that
    form.
  - `crates/buzz-cli/README.md` — CLI-wide exit codes (0 ok, 1 user error, 2 network, 3 auth,
    4 other, 5 write conflict) apply uniformly, including to draft responses.
  - Checked and ruled out: `VISION_PROJECTS.md`'s "Approval gates" Status-table row is the
    software-forge PR-merge approval gate (kind:46011), an unrelated capability — not cited as
    evidence for this node.

## STEP 1 — Confirm scope and target id

Re-confirm no second corpus node already covers this (checked: no `capabilities/` directory
exists at all yet). Front matter: `id: capabilities-agents-agent-response`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`.
Done-when: confirmed via `git ls-tree` above; no further action needed.

## STEP 2 — Draft the document body

Follow `templates/capability.md`'s skeleton: Capability statement, Maturity, Boundary,
Relationships, Scope and omissions. Cite every substantive claim as `path:line`/`path:start-end`
(no `#symbol=`/`#line=` fragments). Add one `references` relationship to
`architecture-flows-agent-turn` (exists on `origin/launchpad`).
Done-when: file written at
`launchpad/docs/corpus/capabilities/agents/agent-response.md`.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root. Confirm zero new
FAIL entries beyond the known 21 pre-existing ones (issue #1951).
Done-when: validator output diffed against baseline shows no new failures for this file.

## STEP 4 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then `git add` the new doc + this plan file and
`git commit -s -m "docs(corpus): document capabilities/agents/agent-response (#708)"`.
Done-when: commit created; `git status` clean for these paths.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `unittest discover` on corpus tests prints `OK`.
- Commit succeeds without touching the stamp file or using `--no-verify`.

## BUDGET

Single-file doc + this plan. No code changes. ~1 commit.

## OPEN

- Whether `capabilities/agents/` should eventually get a sibling index node — out of scope here;
  not decided.

## LEFT OUT

- Any change to `buzz-cli`, `buzz-relay`, or desktop runtime behavior.
- Documenting the full CLI command surface (that is an interface-shaped node, not this
  capability node) or the full agent-turn lifecycle (already covered by
  `architecture-flows-agent-turn`).
