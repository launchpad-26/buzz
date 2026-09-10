Issue #975 (Feature #616 child) — interfaces-acp-session corpus node

Stated size: issue #975's body has no explicit Size line; dispatching task instructions say "cap at 5 steps -- this is a small single-document task" -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/acp/session.md` does not exist anywhere in
  this worktree (`test -f` on the path fails). Confirmed directly, not assumed.
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
  `type: governance`) already exists and is merged to `origin/launchpad` — the
  worktree was created directly from `origin/launchpad` at commit
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`, so this is a valid `implements`
  relationship target. The dispatching brief's premise ("no template exists
  yet") is stale; the template landed since that brief was written.
- `node.schema.json`'s `type` enum has 13 members and no plain `interface`
  value; the interface-shaped value is the single hyphenated token
  `interfaces-events` (confirmed in `node.schema.json` and independently in
  `templates/interface.md`'s own "A note on `type`" section and in
  `standards/taxonomy.md`).
- `crates/buzz-acp/src/acp.rs` (5030 lines) contains the ACP session wire
  calls: `AcpClient::spawn`, `initialize`, `session_new_full`/`session_new`,
  `session_set_goose_system_prompt`, `session_set_config_option`,
  `session_set_model`, `session_prompt_with_idle_timeout` /
  `session_prompt_blocks_with_idle_timeout`, `session_cancel`,
  `cancel_with_cleanup` / `cancel_with_cleanup_grace`, and `shutdown`. No
  `agent-client-protocol` crate dependency exists in
  `crates/buzz-acp/Cargo.toml` — the wire format is hand-implemented.
- `crates/buzz-acp/src/pool.rs` (10039 lines) owns session *state* above the
  wire client: `SessionState` (channel_id -> session_id map, turn counters,
  delivery state), `invalidate_channel` / `invalidate_all` /
  `invalidate_channel_sessions`, and the rotation decision in the prompt
  result handler (`should_rotate` on `StopReason::MaxTokens` /
  `MaxTurnRequests`, or `turn_counts >= max_turns_per_session`).
- No `session/end`, `session/delete` or `session/close` wire call exists
  anywhere in `crates/buzz-acp/src/acp.rs` or `pool.rs` (grep for all three
  returns zero matches). Session "termination" is local bookkeeping only —
  `SessionState` drops its `channel_id -> session_id` entry; no message is
  ever sent to the agent subprocess to end that session specifically. Only
  `AcpClient::shutdown` (kill the whole subprocess) ends a session at the
  wire/process level.
- `git rev-parse HEAD` in the worktree is
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`.

STEP 1 — Draft launchpad/docs/corpus/interfaces/acp/session.md [independent]

<- RUNS HERE

Write the node with front matter `id: interfaces-acp-session`,
`type: interfaces-events`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`, one `relationships` entry
(`implements` -> `corpus-template-interface`, confirmed mergeable per
ALREADY TRUE), and an `evidence` ledger citing only paths/symbols/tests
actually opened in `crates/buzz-acp/src/acp.rs` and `pool.rs` during this
task (a commit-citation provenance entry for
`650354eab8d41ab6ce1a71de079a6c6d95c69052`, plus FACT entries with file:line
citations for: `AcpClient::spawn`/`initialize`/`session_new_full` creation
flow, the `SessionNewResponse` shape, `session_cancel`/`cancel_with_cleanup`
termination-of-turn calls, `shutdown` process-level termination,
`SessionState`'s channel-keyed session map and invalidation methods, the
rotation trigger in `pool.rs`, and the absence of any wire-level
session-end call).

Body follows `templates/interface.md`'s required sections (Interface
description, Operations, Contract and stability, Boundary, Relationships,
Scope and omissions) adapted to this task's own Definition-of-done bullets
from the issue: inputs/messages, outputs/responses, error/rejection
behavior, auth/authorization, versioning/compatibility, ordering/idempotency
where applicable, a link to the authoritative spec (none is authoritative
here — buzz-acp hand-implements the wire format, so the "authoritative
representation" is the code itself, stated as such), and one valid + one
failure example.

Scope: session lifecycle only (creation via `session/new`, id assignment,
in-memory state, turn-count/stop-reason rotation, and termination) —
explicitly excludes the base JSON-RPC/NDJSON transport (issue #973),
message/prompt content framing (issue #974), and tool-call handling
(issue #976), each named in the Boundary section as owned by its sibling
node/issue, not yet resolvable as a `relationships` target since those
nodes are unmerged.

done when: `launchpad/docs/corpus/interfaces/acp/session.md` exists,
parses as YAML front matter + Markdown body, and every Definition-of-done
bullet from issue #975 is addressed by a named section in the body.

STEP 2 — Validate the node [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repo root.

done when: the command exits 0. Any `FAIL` line not caused by this task's
own new node is treated as a fresh finding for the final report, not
silently patched around; any `UNVERIFIED` notice is acceptable (non-fatal
per `AGENTS.md`'s own documented checker behavior).

STEP 3 — Earn the commit gate and commit [needs 2]

Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as its own
command and confirm it prints `OK`. Then, in a separate command,
`git add` the node and this plan file and `git commit -s` with the message
`docs(corpus): document ACP session interface (#975)`.

done when: the unittest run prints `OK` and `git log -1 --format=%H` shows
a new commit on `task/975-interfaces-acp-session` whose tree contains both
added files. If the commit is rejected for a missing gate stamp, that
rejection itself is the done-when outcome to report — no stamp file is
touched and `--no-verify` is not used.

STEP 4 — Self-review against the issue checklist [needs 3]

Re-read the committed diff line by line against issue #975's
Definition-of-done checklist and re-run `validate.py` once more to confirm
it still exits 0 post-commit.

done when: every checklist bullet has a corresponding body section
identified by name, no second hand-authored canonical corpus document was
created, and `validate.py` exits 0 on the final tree.

PARALLEL

None of these steps run in parallel with each other — this is a single
sequential document-drafting task with no independent workstream, matching
the dispatching brief's own instruction to keep this small. Sibling nodes
for protocol/message/tool-call (issues #973/#974/#976) are being written in
parallel by other tasks/agents but are out of this plan's scope entirely —
no coordination beyond the Boundary section's prose mention is needed since
no `relationships` target can resolve to them yet.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (Step 2, re-confirmed in Step 4).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` must print `OK` before the commit gate will accept the
  commit (Step 3).
- The repository's commit-msg hook / gate stamp requirement applies to the
  commit in Step 3; per the dispatching instructions, a rejected commit is
  reported as a finding, not routed around.

BUDGET

One document (~150-250 lines of Markdown), one plan file, one commit. No
code changes, no test changes, no CI/workflow changes. Expected total: under
30 minutes of agent time, well inside a "small single-document task."

OPEN

- Whether `interfaces-acp-session` should later gain `references` edges to
  the sibling protocol/message/tool-call nodes (#973/#974/#976) once those
  merge — deliberately deferred, per `AGENTS.md`'s own relationship-target
  rule, to whichever of those PRs merges last, not decided here.
- Whether ACP protocol version 2 (the "intentional temporary pin ... ahead of
  the upstream ACP RFD" noted in `acp.rs`'s own comment) will change before
  the upstream RFD merges — noted in the node's own Scope and omissions as
  expected-but-unverified, not resolved by this task.

LEFT OUT

- Rewriting or correcting `crates/buzz-acp` source code — this is a
  documentation-only task; any drift found between code and comments is
  recorded as a citation, not fixed.
- Creating the sibling interface nodes for protocol/message/tool-call
  (#973/#974/#976) — explicitly owned by parallel issues, not this one.
- Adding a `references`/`implements` edge to those sibling nodes — they are
  unmerged on `origin/launchpad` at this task's recorded revision, and
  `AGENTS.md` step 9 makes an edge to an unmerged node a hard CI error.
- Resolving whether `interfaces-events` is a satisfying fit for an
  interface-only (non-event) node — flagged transparently in the node's own
  body per `standards/taxonomy.md`'s guidance for an imperfect enum fit,
  not escalated as a schema-change proposal in this task.
