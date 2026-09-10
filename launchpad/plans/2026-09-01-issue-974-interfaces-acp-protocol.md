Issue: launchpad-26/buzz#974 (interfaces-acp-protocol corpus node)
Stated size: issue body has no explicit Size line -> cap: 5 steps (single hand-authored document; dispatch instructions cap this task at 5 steps)

ALREADY TRUE

- Worktree `__worktrees/task-974-interfaces-acp-protocol` exists on branch
  `task/974-interfaces-acp-protocol`, forked from `origin/launchpad` at commit
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`.
- `launchpad/docs/corpus/interfaces/acp/protocol.md` does NOT exist yet (confirmed:
  `test -f` reported absent). No `launchpad/docs/corpus/interfaces/` directory exists
  at all on `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` lists no `interfaces/` prefix).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `interface`
  value; the correct value for an interface-shaped instance node is the combined
  `interfaces-events` member (confirmed directly in the schema file, and confirmed
  again by `templates/interface.md`'s own "A note on `type`" section, which states
  an instance node built from that template "carries `type: interfaces-events`").
- `launchpad/docs/corpus/templates/interface.md` exists and is merged to
  `origin/launchpad` (`corpus-template-interface`, `type: governance`). It supplies
  the required-sections skeleton (Interface description, Operations, Contract and
  stability, Boundary, Relationships, Scope and omissions) this task's target
  document will follow. No per-node-type standard beyond this template was found.
- `crates/buzz-acp/src/acp.rs` is the sole implementation of the ACP JSON-RPC 2.0 /
  NDJSON stdio wire protocol in this repo (no `agent-client-protocol` crate
  dependency in `crates/buzz-acp/Cargo.toml`); `crates/buzz-acp/README.md` documents
  the external spec link (`https://agentclientprotocol.com/`) and the minimal
  requirements list (README.md:325-330) an adapter must satisfy.
- `launchpad/docs/corpus/architecture/flows/agent-turn.md` (`id:
  architecture-flows-agent-turn`) is already merged to `origin/launchpad` and
  describes the system-level flow this protocol node is the wire contract for —
  a legitimate `references` target, confirmed present in the merge-target tree.
- `corpus-template-interface` (the template file itself) is also merged to
  `origin/launchpad`, so it is a legitimate optional `implements` target per its own
  documented convention.
- Sibling nodes for #973 (messages), #975 (session), #976 (tool-call) are being
  authored in parallel on unmerged branches and MUST NOT be named in
  `relationships` (they will not resolve on `origin/launchpad`); any mention of them
  is prose-only, by filename.

STEP 1 [independent]

Read issue #974's Definition of Done (already done during dispatch: no relay
query/message/tool-call scope; this task documents only the protocol/transport
layer — JSON-RPC 2.0 framing, initialize/version negotiation, request/notification/
response shape, error objects, ordering, auth capability advertisement) and confirm
against `crates/buzz-acp/src/acp.rs`, `crates/buzz-acp/src/lib.rs`, `crates/buzz-acp/
src/pool.rs` and `crates/buzz-acp/README.md` which evidence entries back each DoD
bullet: inputs/messages (initialize/session/new/session/prompt/session/cancel
requests and notifications), outputs/responses (result values, `stopReason`,
JSON-RPC error objects), error/rejection behavior (`AcpError` variants,
`agent_error_from_json`, harness-side `-32601` for unrecognized agent-initiated
requests, malformed-line skip, `MAX_LINE_SIZE` rejection), auth (client
capabilities `auth.terminal`/`_meta.terminal-auth`, `initialize` response's
`authMethods`, the `authenticate` request/`methodId`), versioning/compatibility
(harness always requests `protocolVersion: 2`; tolerates a lower reported version;
`pool.rs`'s `protocol_version >= 2` / `< 2` capability gates, with the
`claude-agent-acp` exception), ordering (monotonic `next_id`, response matched by
`id` not by arrival order, notifications carry no `id`).
done when: a written list (this plan's evidence table, built while drafting the
node in Step 2) maps every DoD bullet to at least one opened source path/line
range.

STEP 2 [needs 1] <- RUNS HERE

Create `launchpad/docs/corpus/interfaces/acp/protocol.md` following
`templates/interface.md`'s required-sections skeleton, with front matter
`id: interfaces-acp-protocol`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Populate the
`evidence` ledger with one entry per substantive claim (FACT for anything opened
directly in `crates/buzz-acp/`, `crates/buzz-acp/README.md` and the ACP spec URL;
INFERENCE with `confidence` for reasoned conclusions; no TEAM_KNOWLEDGE expected,
since no issue/PR/human statement is the sole source of anything here). Include: a
provenance commit citation for `650354eab8d41ab6ce1a71de079a6c6d95c69052`; the
Interface description, Operations table (`initialize`, `authenticate`,
`session/new`, `session/prompt`, `session/cancel`, `session/update`,
`session/request_permission`, agent-initiated method fallback), Contract and
stability (versioning tolerance, timeouts, error-object shape, ordering-by-id,
`MAX_LINE_SIZE` framing bound), Boundary (explicitly excludes the message-content
contract of #973, the session-lifecycle detail of #975, and the tool-call contract
of #976 — named by filename/id only, never as a `relationships` target), one valid
example (a request/response round trip drawn from an existing test transcript) and
one failure example (a JSON-RPC error surfaced as `AcpError::AgentError`, drawn
from an existing test transcript), Relationships (`references:
architecture-flows-agent-turn`; optionally `implements: corpus-template-interface`;
none toward #973/#975/#976), and Scope and omissions (what this node does not
cover, plus anything expected-but-not-verified, e.g. the ACP spec's own document
was not fetched, only this repo's code and README were).
done when: `launchpad/docs/corpus/interfaces/acp/protocol.md` exists, is the only
new hand-authored corpus file in the diff, and `python3 launchpad/project-
intelligence/corpus/validate.py` exits 0 with no FAIL lines.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as a lone command and confirm it prints `OK`.
done when: the command's output contains `OK` and its exit code is 0.

STEP 4 [needs 3]

Stage exactly the two files (`launchpad/docs/corpus/interfaces/acp/protocol.md`,
this plan file) and commit with `git commit -s -m "docs(corpus): document ACP
protocol interface (#974)"`. If the commit gate rejects for a missing stamp, stop
and report it rather than bypassing with `--no-verify` or touching any stamp file.
done when: `git log -1 --format=%H` names a new commit whose diff contains only
those two files, or the specific gate-rejection reason is captured verbatim for
the final report.

STEP 5 [needs 4]

Self-review: re-read the committed diff line by line against issue #974's
Definition of Done checklist, confirm every evidence entry's cited path/line still
supports its statement, confirm no second hand-authored canonical corpus document
was created, and re-run `python3 launchpad/project-intelligence/corpus/validate.py`
to confirm it still exits 0.
done when: each DoD bullet has a named corresponding section/evidence entry in the
committed file, and `validate.py`'s exit code is 0.

PARALLEL

None of these steps can run concurrently with each other — this is a single
document authored in one pass, and the commit (Step 4) must follow validation
(Step 2) and the test-suite gate (Step 3) in strict order. No other in-flight
sibling task (#973/#975/#976) shares a file with this one, so there is no
cross-task file collision to sequence against.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (Step 2,
  re-confirmed Step 5) before committing.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must print `OK` (Step 3) before committing — this is the commit
  gate the repo's hook enforces; do not route around a rejection.
- No `relationships[].target` may name `interfaces-acp-messages`,
  `interfaces-acp-session`, `interfaces-acp-tool-call` or any other id from
  #973/#975/#976 — those branches are unmerged and the ids are guesses, not
  confirmed. Prose mentions by filename only.

BUDGET

One document (~150-250 lines including front matter), one plan file, one commit.
No code changes, no changes to `crates/buzz-acp/` itself, no second corpus file.
Evidence-gathering reads are bounded to `crates/buzz-acp/src/acp.rs`,
`crates/buzz-acp/src/lib.rs` (grep-scoped sections), `crates/buzz-acp/src/pool.rs`
(grep-scoped sections), `crates/buzz-acp/README.md`, `crates/buzz-acp/Cargo.toml`,
plus the corpus schema/template/AGENTS files already read during planning.

OPEN

- Whether a future `interfaces-acp-messages`/`-session`/`-tool-call` node (once
  #973/#975/#976 merge) should gain a `depends-on` or `part-of` edge back to this
  node is not decided here — this node declares no forward-looking edge to an id
  that does not yet exist, per `AGENTS.md`'s merge-target rule.
- Whether `implements: corpus-template-interface` is added is a judgement call at
  draft time (Step 2), not fixed by this plan — the template states it is optional
  either way.

LEFT OUT

- The individual wire contract of `session/new`'s parameters, `session/prompt`'s
  content-block shape, and `session/update`'s notification kinds — that is
  #973/#975's subject matter, not this node's. This node names those methods only
  in the Operations table, pointing at the code, without restating their payload
  shape.
- The tool-call permission/approval contract in depth (`session/request_permission`
  option kinds, `allow_once`/`reject_once` semantics) — that is #976's subject;
  this node mentions the method exists and points at the code.
- Any change to `crates/buzz-acp/` itself. This is a documentation-only task.
- Reconciling this node's `type: interfaces-events` choice against a hypothetical
  future dedicated `interface` enum value — no such value exists today, and adding
  one is a schema-change decision this task does not own (per
  `standards/taxonomy.md`'s own scope).
