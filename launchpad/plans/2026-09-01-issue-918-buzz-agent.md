Issue #918 — corpus node: implementation/crates/buzz-agent.md
Stated size: no `Size` line in the issue body → cap: 5 steps (set by the batch-dispatch
instructions for this task, which explicitly cap it at 5 steps as a single-document task)

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
  and `launchpad/docs/corpus/templates/implementation-reference.md` are merged on
  `origin/launchpad` (confirmed via `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`).
  `launchpad/docs/corpus/architecture/containers/agent-runtime.md`
  (`id: architecture-containers-agent-runtime`, `status: draft`) is also merged and
  already documents `buzz-agent` at the container level, citing
  `crates/buzz-agent/README.md` and `crates/buzz-agent/Cargo.toml` directly.
  `launchpad/docs/corpus/implementation/crates/buzz-agent.md` does not exist yet
  (confirmed via `ls`). This is the first node authored from the
  implementation-reference template — no worked example exists to pattern-match
  against, only the template's own skeleton.

STEP 1  Finalize the evidence set for the ledger. [independent]
        Confirm citations for `crates/buzz-agent/Cargo.toml` (zero internal `buzz-*`
        crate dependencies), `crates/buzz-agent/src/lib.rs` (module list,
        `#![forbid(unsafe_code)]`, `pub fn run`, the JSON-RPC dispatch table for
        `initialize`/`session/new`/`session/prompt`/`session/set_model`/
        `session/cancel`), `crates/buzz-agent/src/main.rs`, `crates/buzz-agent/README.md`
        in full, each module's doc-comment header (`agent.rs`, `auth.rs`, `builtin.rs`,
        `catalog.rs`, `config.rs`, `handoff.rs`, `hints.rs`, `llm.rs`, `mcp.rs`,
        `model_capabilities.rs`, `permission.rs`, `types.rs`, `wire.rs`), and
        representative test names from `tests/regressions.rs`,
        `tests/permission_boundary.rs`, `tests/golden_transcripts.rs`,
        `tests/hints_integration.rs`. Record `git rev-parse HEAD`.
        done when: every claim planned for the evidence ledger has a real file path
        this task opened, and the commit SHA is recorded.

STEP 2  Decide the realization target, `type`, and relationships. [needs 1]
        Target = the crate's own documented self-contract in
        `crates/buzz-agent/README.md` (no separate ADR/NIP exists for it), so name it
        by path rather than inventing an `implements` edge. `type: implementation`
        (the template's own default; the crate is a concrete Rust binary/library, not
        itself a protocol/contract surface, so `interfaces-events` misfits). One
        `part-of` relationship toward `architecture-containers-agent-runtime`,
        verified merged and already naming `buzz-agent` as one of its three composing
        crates.
        done when: the target/type/relationship decision is written down (in this
        plan or directly into the draft front matter) before the body is drafted.

STEP 3  Write the full node to the target path. [needs 2] ← RUNS HERE
        Front matter plus all seven required template sections (Realization
        statement, Target, Implementation surface, Divergences, Verification,
        Relationships, Scope and omissions) to
        `launchpad/docs/corpus/implementation/crates/buzz-agent.md`, satisfying every
        DoD bullet in issue #918 including explicit "what it does NOT own" (no
        internal `buzz-*` dependency — no direct Buzz CLI, no persona resolution, no
        direct Postgres/relay access, those are `buzz-acp`'s and `buzz-dev-mcp`'s jobs
        per `agent-runtime.md`'s own evidence) and named public entry points
        (`buzz_agent::run`, the JSON-RPC method surface, the `pub use` re-exports
        `discover_databricks_models`, `ModelEntry`, `Provider`, `AgentError`).
        done when: the file exists on disk with YAML front matter (`id`, `type`,
        `status`, `origin`, `audiences`, `evidence`, optional `relationships`) and all
        seven required body sections present as `##` headings.

STEP 4  Validate structurally. [needs 3]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root. Fix and re-run until it exits 0.
        done when: the command's exit status is 0.

STEP 5  Earn the commit gate. [needs 4]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own tool call and confirm `OK`; then, in a
        separate call, `git add` the node and this plan and `git commit -s`. Do not
        push, do not open a PR — this document integrates into one later batch PR
        covering all 37 documents.
        done when: the unittest run reports `OK` and `git commit -s` succeeds,
        producing a commit SHA.

PARALLEL  None of the five steps may run as independent subagents relative to each
          other — steps 2-5 each depend on the previous step's output (decision →
          draft → validated file → committed file) and all touch the same target
          file or its validation state. Step 1 is independent of nothing else in
          this plan (it is the first step) but could in principle run before this
          plan exists; it does not benefit from parallel dispatch here since it is
          already substantially complete from this task's own investigation.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          after STEP 4. `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report
          `OK` after STEP 5, before the commit — this is what earns the commit
          hook's verification stamp for this worktree. `review-code` is applied to
          the diff as a self-review pass after commit (per the task brief), not
          gating the commit itself; `review-adjudicate` and the cross-model final
          review are deferred to the batch owner's later integration pass, not run
          in this session. `qa` explore mode does not apply — this is a docs-only
          change with no runtime interface to exercise.

BUDGET    STEP 3 (writing the full body against seven required template sections,
          each needing its own real citations) is the step most likely to eat the
          budget — the template is long, detailed, and this is the first node built
          from it, so there is no existing instance to copy structure from.

OPEN      The template's "A note on `type`" section permits `interfaces-events` as
          an alternative when "the realizing artifact is itself a protocol/contract
          surface." `buzz-agent` implements ACP and MCP client-side but does not
          itself define either protocol, so `implementation` is judged the better
          fit here — recorded explicitly rather than picked silently, since this is
          the first node setting precedent for later crate nodes (`buzz-acp`,
          `buzz-dev-mcp`) that will face the identical choice and may reasonably
          decide differently for a harness that speaks the protocol from the other
          side.

LEFT OUT  No `implements` edge to an ACP or MCP specification node — neither
          protocol has a corpus node id yet (they are external specs at
          agentclientprotocol.com and modelcontextprotocol.io, not repository
          ADRs/NIPs), and per the template's own rule an edge to a nonexistent id is
          a hard validation failure, so the target is named by URL in prose instead.
          No `references` edge to a verification/test-strategy node — the
          test-strategy template (`#1350`) has no instance yet in the merged corpus.
          No attempt to reconcile or expand `architecture-containers-agent-runtime`'s
          own content — this node links it and does not restate it, per the
          template's evidence-expectations rule against citing one node's content as
          a stand-in for another's.
