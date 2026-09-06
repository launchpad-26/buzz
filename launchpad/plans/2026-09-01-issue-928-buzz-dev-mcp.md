# Issue #928 — corpus doc: implementation/crates/buzz-dev-mcp.md

Stated size: issue #928 carries no explicit Size label (labels are type:task, area:docs, by:agent only), and the dispatching task explicitly caps this plan -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/schema/node.schema.json`
are merged on `origin/launchpad`. `launchpad/docs/corpus/implementation/crates/buzz-dev-mcp.md`
does not exist yet (confirmed via `ls`). `launchpad/docs/corpus/architecture/containers/agent-runtime.md`
(id `architecture-containers-agent-runtime`) is merged and already documents, with
opened-and-cited evidence, that buzz-dev-mcp is a developer MCP server spawned as a
child process by buzz-agent's MCP client (`crates/buzz-agent/src/mcp.rs`, `rmcp::transport::TokioChildProcess`)
and wired in via `buzz-acp`'s optional `BUZZ_ACP_MCP_COMMAND` (`crates/buzz-acp/src/lib.rs:5069-5124`,
`crates/buzz-acp/src/config.rs:266-267`) — confirmed independently in this session by
reading `crates/buzz-dev-mcp/src/lib.rs`, `crates/buzz-dev-mcp/src/{paths,shim,shell}.rs`,
and the same buzz-acp/buzz-agent source. No `implementation/` directory exists in the
corpus yet, so this is the first node built from the implementation-reference template.

STEP 1 [independent] — gather evidence: read `crates/buzz-dev-mcp/Cargo.toml`, every
file under `crates/buzz-dev-mcp/src/` (lib.rs, main.rs, paths.rs, shell.rs, shim.rs,
read_file.rs, str_replace.rs, todo.rs, rg.rs, tree.rs, view_image.rs), confirm inline
`#[cfg(test)]` coverage per file, and cross-check the buzz-agent/buzz-acp subprocess
wiring already cited in `architecture-containers-agent-runtime`. Record `git rev-parse
HEAD`. RUNS HERE.
done when: every claim destined for the node's evidence ledger has been read at its
source in this worktree, and the commit SHA is recorded.

STEP 2 [needs 1] — write the front matter (`id: implementation-crates-buzz-dev-mcp`,
`type: implementation`, `status: draft`, `origin: launchpad`, `audiences:
[agent, developer, reviewer]`, one `evidence` entry per substantive claim
classified FACT/INFERENCE/TEAM_KNOWLEDGE per `AGENTS.md`, `relationships: [{type:
part-of, target: architecture-containers-agent-runtime}]` — no `implements` edge,
since the MCP protocol/`rmcp` crate contract buzz-dev-mcp realizes has no corpus
node id yet and inventing one is a hard validation error per `AGENTS.md`).
done when: the front matter parses as valid YAML and every field matches
`node.schema.json`'s constraints by inspection.

STEP 3 [needs 2] — write the body using the implementation-reference template's
required sections (Realization statement / Target / Implementation surface /
Divergences / Verification / Relationships / Scope and omissions), satisfying issue
#928's DoD: state implementation responsibility and what it deliberately does not own
(the `buzz-cli`, `git-credential-nostr`, `git-sign-nostr` logic it multicalls/shims
rather than reimplements), name public interfaces/entry points (the 7 `#[tool]`
MCP functions in `lib.rs` plus the multicall CLI personalities) and important
dependencies, link owned source paths and representative tests, and avoid
restating domain semantics already canonical in `architecture-containers-agent-runtime`.
done when: every required section from the template is present and every substantive
claim in the body has a matching evidence-ledger entry citing an opened source.

STEP 4 [needs 3] — validate: run `python3 launchpad/project-intelligence/corpus/validate.py`
from the repo root; fix and re-run until it reports zero FAIL entries for this
node (a pre-existing ~21-failure baseline on `origin/launchpad` is expected and
not this node's concern — confirmed by diffing against a stash if the exit code
is nonzero).
done when: `validate.py` produces no FAIL line whose node is
`implementation-crates-buzz-dev-mcp`.

STEP 5 [needs 4] — earn the commit gate and commit: run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call and confirm `OK`; then, in a separate
call, `git add` the plan and the new corpus doc and `git commit -s` with a
`docs(corpus):` message referencing #928. Do not push and do not open a PR —
this batch integrates all 37 documents into one Feature-level draft PR later.
done when: the unittest run reports `OK` and `git log -1` on this branch shows the
new commit containing exactly the plan file and the corpus doc.

PARALLEL: none — single hand-authored file, one worktree, no other document in
this batch is touched.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report
zero FAIL entries for this node. `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK` to
earn the commit-gate stamp. `corpus-review` (or a careful self-review, named as
such, if the skill is unreachable) runs after the commit, per the dispatching
task's Verify step — not a precondition of the commit itself.
review-adjudicate and cross-model final review are explicitly deferred to the
batch owner's later integration phase, not run in this worktree.

BUDGET: single document, no code changes, no test changes — small.

OPEN: whether `type: implementation` or an alternative surface value (e.g.
`interfaces-events`, since buzz-dev-mcp's realizing artifact is itself an MCP
protocol surface) is the better fit is a genuine judgment call the template
flags explicitly ("A note on `type`"); this plan defaults to `type: implementation`
as the enum's own named value for this content and the more literal fit (a crate,
not a wire-level event contract), but does not treat that as settled beyond this
node. Whether a future MCP-protocol-spec corpus node should exist for a real
`implements` edge to eventually target is left for whoever authors that node,
not decided here.

LEFT OUT: no `implements` relationship is declared — the template requires one
only "once the target itself carries a corpus node id," and neither the MCP
specification nor any ADR/NIP for buzz-dev-mcp's tool contract has one today; the
*Target* section names the real target in prose instead, per the template's own
instruction not to invent a placeholder edge. No `references` edge to a
verification/test-strategy node is declared — no `verification`-typed corpus node
exists yet for buzz-dev-mcp's test suite to point at. Corpus generated indexes are
not touched — none exist yet to regenerate.
