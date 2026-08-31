Issue: launchpad-26/buzz#1116 — task: document layers/lifecycle/cancellation.md
Parent: Feature #611 (compute observability, configuration and lifecycle corpus), PRD #602

Stated size: no explicit Size line on #1116; dispatch prompt caps at 5 steps (single small document)  ->  cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-1116-cancellation` exists, branched from
  `origin/launchpad` at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, on branch
  `task/1116-cancellation`.
- `launchpad/docs/corpus/layers/lifecycle/cancellation.md` does not exist yet
  (confirmed: `ls` reports no such directory). No BLOCKED condition.
- `launchpad/docs/corpus/layers/lifecycle/` does not yet exist at all on
  `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` lists no `layers/*` path) — this is the first node
  in that sub-surface to merge. Two sibling tasks in this same dispatch
  (#1118 graceful-shutdown, #1120 startup) have already drafted
  `layers/lifecycle/*.md` in their own unmerged worktrees
  (`__worktrees/task-1118-graceful-shutdown`,
  `__worktrees/task-1120-startup`) — both read directly from disk for
  precedent, not copied from `origin/launchpad` (neither is a valid
  `relationships` target per `AGENTS.md` step 9 until merged).
- The issue's own DoD checklist (not the flow.md-shaped checklist #1118/#1120
  carried) uses concept-template language verbatim: "Defines the term in one
  sentence before deeper explanation," "States boundaries/non-goals,"
  "Links the concept to related concepts, implementation and verification,"
  "Uses examples only to clarify the concept." This maps directly onto
  `launchpad/docs/corpus/templates/concept.md`'s required sections
  (Definition, Use cases, Related resources/Relationships, Scope and
  omissions), not `flow.md`'s Sequence/Diagram/Outcome shape #1118/#1120
  used — cancellation is a cross-cutting mechanism used in several unrelated
  contexts, not one ordered sequence, which is exactly the concept-vs-flow
  distinction `concept.md`'s own "Boundary against reference/procedure"
  section describes from the flow side too.
- Per the same `type: layers` reasoning #1118 and #1120 both independently
  derived (from `standards/taxonomy.md`'s *Choosing a value* step 2: "pick
  the enum member whose plain-English name most concretely names the node's
  primary subject... not where the node currently happens to live"), and
  because parent Feature #611 organizes this whole task set under a
  `layers/lifecycle/` directory taxonomy: `type: layers` is the deliberate,
  disclosed choice here too, re-derived independently (their branches are
  unmerged, so their body text was read as precedent but not cited as an
  authoritative source).
- Direct investigation in this worktree has located three genuinely
  different cancellation trigger sites sharing one primitive
  (`tokio_util::sync::CancellationToken`), scoped tightly to task/request
  cancellation and deliberately excluding process-wide shutdown sequencing
  (#1118's subject):
  - `crates/buzz-relay/src/connection.rs`: one `CancellationToken` per
    WebSocket connection (`ConnectionState.cancel`, created at
    `connection.rs:132`), cloned into the send/heartbeat/auth-timeout tasks
    and checked via `tokio::select! { _ = cancel.cancelled() => ... }`
    (`connection.rs:270,380,461,542`). Three independent triggers observed:
    sustained backpressure protecting server memory
    (`connection.rs:95-118`, `self.cancel.cancel()` at line 107), a NIP-42
    auth timeout racing its own `sleep` against the same token
    (`connection.rs:251-272`), and natural `recv_loop` completion
    explicitly cancelling sibling tasks afterward (`connection.rs:283-286`).
    `send_cancel = cancel.child_token()` (`connection.rs:233`) demonstrates
    the parent/child token relationship: cancelling the child stops only the
    send loop, not its siblings, while parent cancellation still propagates
    down.
  - `crates/buzz-dev-mcp/src/shell.rs::run` (`shell.rs:130-296`): a
    request-scoped `CancellationToken` supplied by the caller
    (`crates/buzz-dev-mcp/src/lib.rs:44-50`, `context.ct` — the `rmcp` MCP
    SDK's own per-request token, populated when an MCP client sends
    `notifications/cancelled` for that request id — a different origin
    from both connection-level and process-wide cancellation). A `tokio::
    select! { biased; _ = ct.cancelled() => ..., r = tokio::time::timeout(...)
    => ... }` (`shell.rs:218-274`) races the external cancellation against
    the command's own timeout; both branches converge on the same
    process-group kill + bounded reap, and both call
    `stdout_handle.abort()` / `stderr_handle.abort()` on the two reader
    tasks (`shell.rs:235-236,283,291`) — `JoinHandle::abort()` is a second,
    non-cooperative primitive: it preempts a task at its next await point
    regardless of whether that task ever observes a `CancellationToken`,
    used here as a hard bound on cleanup rather than as the primary signal.
  - `crates/buzz-relay/src/audio/join.rs` and `audio/handler.rs`: per-huddle
    -session `cancel`/`lost`/`draining` tokens (`join.rs:591-614`) triggered
    by owner loss or session drain — read far enough to confirm the same
    `CancellationToken` primitive and child-token-free independent-tokens
    pattern, but this subsystem's full session lifecycle is left as a
    supporting example only (one citation), not narrated in depth, since its
    session-teardown ordering risks duplicating #1119 (resource-cleanup)'s
    subject rather than this node's own (the cancellation signal itself).
- `graceful-shutdown.md` (read directly from
  `__worktrees/task-1118-graceful-shutdown`) already documents
  `drain_all()`/`drain_all_jittered()` calling `.cancel()` on every
  registered connection's token as one step of process-wide shutdown
  (`state.rs:418-431,465-507`) — confirming this node's connection-level
  token is the same primitive #1118's shutdown sequence uses as one of
  several triggers, not a competing mechanism. This node cites that overlap
  explicitly in its Boundary/Scope-and-omissions rather than re-narrating
  shutdown's own sequencing.
- Candidate `relationships` targets confirmed to exist on `origin/launchpad`
  (`git show origin/launchpad:launchpad/docs/corpus/architecture/containers/
  {relay,agent-runtime}.md`): `architecture-containers-relay` (the
  connection/audio examples run inside it) and
  `architecture-containers-agent-runtime` (confirmed by that node's own
  evidence ledger to include `buzz-dev-mcp`, the shell-tool example's
  crate) — both natural `references` targets, no ownership implied.

STEP 1 [independent]

Write `launchpad/docs/corpus/layers/lifecycle/cancellation.md` using the
`concept.md` template shape: front matter (`id: layers-lifecycle-cancellation`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, operator, reviewer]`, `evidence`, `relationships: [{type:
references, target: architecture-containers-relay}, {type: references,
target: architecture-containers-agent-runtime}]`), body sections: a short "A
note on `type`" section (mirroring #1118/#1120's disclosed reasoning,
independently re-derived); Definition (one-sentence definition of
cancellation as the mechanism for stopping in-flight work before natural
completion, then the two-primitive distinction: cooperative
`CancellationToken` vs. preemptive `JoinHandle::abort()`); a Mermaid diagram
showing the generic pattern (create token -> clone into tasks -> select! races
cancellation against work -> cleanup); Use cases (the three real trigger
sites: connection backpressure/auth-timeout, MCP request cancellation, audio
session loss/drain, each cited); a Comparison table (CancellationToken vs.
abort() — cooperative vs. preemptive, checked at await points vs. immediate,
who uses which and why); Relationships; Scope and omissions (explicitly
excluding: process-wide graceful shutdown sequencing (#1118, even though it
triggers the same connection token as one of several callers); background
worker start/stop lifecycle (#1115); general concurrency coordination —
semaphores, locks, task pools (#1117); resource cleanup / Drop-based teardown
including `KillGroup`'s own drop-guard (#1119); startup (#1120); the full
huddle-audio session lifecycle beyond the one cited example).

<- RUNS HERE

done when: the file exists, front matter parses as valid YAML, and every
cited claim names a real file path (and line/line range where relevant) this
agent directly opened in this worktree.

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and fix every reported error (schema violations, broken node
IDs, invalid source paths, duplicate IDs) until it exits 0.

done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3 [needs 2]

Self-review: re-read the drafted node against #1116's own Definition-of-Done
checklist line by line (one hand-authored canonical document; schema-valid
front matter with stable id/type/status/origin/audiences/evidence/
relationships; one independently maintainable node; FACT/INFERENCE/
TEAM_KNOWLEDGE not conflated; links without duplicating; checked against the
recorded revision; validation passes; defines the term in one sentence;
states boundaries/non-goals; links to related concepts, implementation and
verification; uses examples only to clarify, not to introduce a second
concept). Confirm no second hand-authored canonical document exists
(`git show --stat HEAD` after commit should show only the corpus doc and the
plan file).

done when: each DoD bullet is confirmed satisfied by a specific section of
the drafted file, or a gap is explicitly named in the final report as a
finding rather than silently left.

STEP 4 [needs 3]

Run the verify-gate stamp command as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then, in a separate tool call, commit with
`git commit -s -m "docs(corpus): document cancellation (#1116)"`.

done when: the unittest run reports `OK` and the commit exists on
`task/1116-cancellation` (`git log -1 --oneline`), with no push and no PR
opened (per the dispatch prompt's explicit instruction — this task's commit
is integrated into a shared batch PR by a separate later process).

PARALLEL

None. Steps 1-4 are a strict chain (each step's output gates the next); there
is no independent second workstream inside this single-document task.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (Step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK` before commit (Step 4) — this is the verify-gate stamp
  command; it must be the sole command in its own tool call, per the dispatch
  prompt.
- No push, no `gh pr create` — this task's commit lands in a later shared
  batch PR.

BUDGET

Single document. Remaining work is drafting (Step 1, the bulk of the effort,
grounded in the `connection.rs`/`shell.rs`/`join.rs`/`handler.rs` reads
already done during planning), one validator fix loop (Step 2, expected 0-2
iterations), a line-by-line DoD self-review (Step 3), and the
stamp-then-commit sequence (Step 4). No code changes, no new dependencies, no
new tests beyond the existing corpus validator/test suite.

OPEN

- Whether `type: layers` (this plan's choice, mirroring sibling #1118/#1120,
  itself mirroring #1043) is the better fit than `type: architecture` is a
  judgment call per `standards/taxonomy.md` step 5 ("a node's type MAY be
  revised later") — left to reviewer confirmation, not decided unilaterally
  as unrevisable. The node's own text discloses the reasoning either way.
- Whether the huddle-audio `lost`/`draining` tokens deserve a fuller worked
  example or stay a single supporting citation is a drafting judgment made
  in Step 1 — the goal is illustrating the shared primitive across genuinely
  different trigger contexts, not an exhaustive tour of every subsystem that
  uses `CancellationToken`.

LEFT OUT

- Drafting nodes for the other `layers/lifecycle/*` siblings named in the
  dispatch prompt (background-workers #1115, concurrency #1117,
  graceful-shutdown #1118 already committed, resource-cleanup #1119,
  startup #1120 already committed) — each is its own task.
- Re-narrating process-wide graceful-shutdown sequencing, even the specific
  step where it calls `.cancel()` on every connection token
  (`state.rs:418-431,465-507`) — already documented by #1118; this node
  cites the overlap without repeating the sequencing.
- Documenting `KillGroup`'s own Drop-based last-resort reaping in
  `shell.rs` in depth — a resource-cleanup concern layered on top of
  cancellation, #1119's subject, not this node's.
- Filing a follow-up issue for any second concept discovered while
  drafting — none identified in planning that rises to "a second
  concept/contract/procedure" distinct from the one mechanism being
  defined; if one surfaces during Step 1 it will be named as a candidate
  follow-up in the final report instead of being folded in, per #1116's own
  DoD bullet.
