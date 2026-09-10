# Plan: issue #916 — buzz-acp implementation reference

Issue #916, child of Feature #615, parent PRD #602.

Stated size: single hand-authored corpus document  ->  cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-916-buzz-acp` exists, branch `task/916-buzz-acp` off
  `origin/launchpad` at `1ed55e980b0043f92d9c652e6a39a8e49345389c`.
- Target file `launchpad/docs/corpus/implementation/crates/buzz-acp.md` does not
  exist yet (confirmed via `ls`); `implementation/` has no subtree at all in the
  corpus yet — this is genuinely the first `implementation-reference`-templated node.
- `launchpad/docs/corpus/templates/implementation-reference.md` (required sections:
  Realization statement, Target, Implementation surface, Divergences, Verification,
  Relationships, Scope and omissions) and `launchpad/docs/corpus/AGENTS.md`
  (evidence classes, id rules, relationship-resolves-against-origin/launchpad rule)
  have both been read in full.
- `launchpad/docs/corpus/schema/node.schema.json` and `relationships.schema.json`
  read; front-matter contract and the five relationship types (with `part-of` =
  "source is a constituent section/child of target") are understood.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
  `architecture-containers-agent-runtime`, status `draft`) exists on
  `origin/launchpad`, already documents buzz-acp extensively at container level,
  and lists it as one of three crates ("Container: Agent Runtime" table) — a
  verified, real `part-of` target.
- Crate investigated directly: `crates/buzz-acp/Cargo.toml`, `src/lib.rs`
  (module list, `pub fn run()` is the crate's only public function besides
  `pub use usage::TurnUsage`), `src/{acp,config,pool,pool_lifecycle,queue,filter,
  relay,observer,setup_mode,usage,engram_fetch,prompt_project,prompt_framing}.rs`
  (doc comments + structure), `README.md`, `tests/pool_lifecycle_state.rs`.
- Confirmed real dependents: only `crates/sprig/Cargo.toml` has a real path
  dependency on buzz-acp; `buzz-relay`/`buzz-cli` Cargo.tomls only *mention*
  buzz-acp in rustls-provider comments, not as a dependency (grepped directly).
- Confirmed a real divergence: `README.md`'s configuration table documents
  `BUZZ_ACP_IDLE_TIMEOUT` default `620`; `config.rs`'s
  `DEFAULT_IDLE_TIMEOUT_SECS` constant is `900` (doc comment explains the 900s
  sizing rationale). No third value overrides this at the call site
  (`Config::from_cli`'s idle-timeout resolution).
- Confirmed buzz-acp partially realizes three NIP documents that exist in this
  repo but carry no corpus node id yet: NIP-AM (`docs/nips/NIP-AM.md`, kind
  44200 turn-usage metric published from `pool.rs`), NIP-AE (`docs/nips/NIP-AE.md`,
  core-engram fetch in `engram_fetch.rs`), NIP-MP (`docs/nips/NIP-MP.md`,
  project-home parsing in `prompt_project.rs`). Per `AGENTS.md` step 9 / the
  template's *Relationships* rule, no `implements` edge to any of them — they
  are named by path in prose only.
- Representative test citations gathered: `crates/buzz-acp/src/pool_lifecycle.rs`
  (`mod tests`, e.g. `retry_backoff_doubles_and_caps_at_five_minutes`),
  `crates/buzz-acp/src/queue.rs` (`test_fifo_fairness_picks_oldest_channel`),
  `crates/buzz-acp/src/filter.rs` (`test_filter_error_fails_closed_no_fallthrough`),
  `crates/buzz-acp/src/pool.rs` (NIP-AM emit-hook tests, e.g.
  `acp_stop_to_core` coverage), `crates/buzz-acp/tests/pool_lifecycle_state.rs`
  (external `#[path]` re-inclusion of `pool_lifecycle.rs` as its own test target).
- Worked-example rigor bar read: `launchpad/docs/corpus/architecture/containers/postgres.md`.

STEP 1: Draft the node body and front matter [independent]

<- RUNS HERE

Write `launchpad/docs/corpus/implementation/crates/buzz-acp.md`:
- Front matter: `id: implementation-crates-buzz-acp`, `type: implementation`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  one `evidence` entry per substantive claim (commit citation for the recorded
  revision `1ed55e980b0043f92d9c652e6a39a8e49345389c`; FACT entries for every
  opened-source claim; the idle-timeout mismatch as its own FACT; INFERENCE only
  where genuinely reasoned, with `confidence`), `relationships: [{type: part-of,
  target: architecture-containers-agent-runtime}]`.
- Body sections exactly per the template skeleton: Realization statement,
  Target (NIP-AM/AE/MP named by path, no `implements` edge — none has a corpus
  id), Implementation surface (table: module/symbol -> what it realizes,
  e.g. `acp.rs::AcpClient` -> ACP JSON-RPC lifecycle, `pool.rs` -> agent
  subprocess supervision + NIP-AM kind:44200 publish, `queue.rs` -> per-channel
  FIFO event queue, `filter.rs` -> evalexpr subscription matching, `relay.rs` ->
  NIP-42 WS auth + REST channel discovery, `config.rs` -> CLI/env/TOML config,
  `setup_mode.rs` -> desktop-driven not-ready listener, `engram_fetch.rs` ->
  NIP-AE core memory, `prompt_project.rs` -> NIP-MP project home), Divergences
  (the idle-timeout 620-vs-900 mismatch, cited both ways), Verification (unit
  tests per module + the `tests/pool_lifecycle_state.rs` external target; no
  integration/E2E test specific to buzz-acp found beyond `TESTING.md`'s
  multi-agent guide, say so), Relationships, Scope and omissions (does NOT own:
  the agent LLM loop itself (`buzz-agent`), the MCP tool surface
  (`buzz-dev-mcp`), persona-pack resolution logic (`buzz-persona`, only
  consumed), the relay-side workflow engine, Desktop's managed-agent launch
  code — table these against their owning crates/nodes).

done when: the file exists, contains all seven required sections, and every
evidence-array claim is backed by a source actually opened during
investigation (no invented citations).

STEP 2: Validate against the schema [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root of this worktree. Fix any reported error (broken relationship target,
malformed front matter, missing required field) and re-run.

done when: the command exits 0.

STEP 3: Line-by-line DoD check against issue #916 [needs 2]

Re-read the drafted node against every Definition of Done bullet in issue
#916's body (one hand-authored doc; schema-valid front matter with stable id/
type/status/origin/audiences/evidence/relationships; one independently
maintainable node; FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links without
duplicating; checked against the recorded revision; validate.py clean; states
responsibility and non-ownership; names public interfaces and dependencies;
links owned source paths and representative tests; avoids restating
capability/layer/interface semantics not yet in the corpus). Fix any gap found.

done when: every DoD bullet is satisfied and re-verified by re-reading the
committed prose against the bullet, not just the section headings.

STEP 4: Unit tests, then commit [needs 3]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call; confirm `OK`. Then, in a separate
tool call, `git add` the two new files and
`git commit -s -m "docs(corpus): add buzz-acp implementation reference (#916)"`.

done when: the unittest run reports `OK` and `git log -1` shows the new
commit with both files staged; if the commit gate refuses with no stamp
found, stop and report BLOCKED rather than touching the stamp or using
`--no-verify`.

STEP 5: Final self-review [needs 4]

Diff the commit against issue #916's DoD checklist one more time; confirm every
citation resolves to a real, opened file/symbol/test; re-run `validate.py` to
confirm it is still clean post-commit. Attempt the `review-code` skill; if
unreachable in this session, say so explicitly and rely on this self-review.

done when: a terse final report is produced (issue number, worktree path,
branch, commit SHA, which verification ran, residual concerns or BLOCKED).

PARALLEL

None — this is a single sequential document-authoring task with no
independent parallel tracks; each step depends on the previous one's output.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (Step 2) and again after commit (Step 5).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK`, run as the sole command in its own tool call (Step 4).
- The commit must be created with `git commit -s`; if the repo's commit gate
  hook refuses, that is a BLOCKED finding, not a `--no-verify` occasion.

BUDGET

One document (~150-250 lines of Markdown), one plan file, one commit. No code
changes, no test changes, no other corpus files touched. Do not push, do not
open a PR — this batch integrates 37 documents into one Feature-level draft
PR later.

OPEN

- Whether `implements` edges toward NIP-AM/NIP-AE/NIP-MP should be added once
  those specs get their own corpus node ids — left for whoever authors those
  nodes, not decided here (no such node exists on `origin/launchpad` today).
- Whether `buzz-workflow`'s relay-side kind:46010 producer deserves a
  `references` edge from this node — `agent-runtime.md` itself left this as a
  follow-up; not added here without a target node id.

LEFT OUT

- Editing `crates/buzz-acp/README.md` to fix the 620-vs-900 idle-timeout
  mismatch — that is a product/doc fix with its own review path, out of scope
  per issue #916's own "Out of scope: changing runtime product behavior".
  This node records the divergence as evidence instead.
- A second corpus node for any of NIP-AM/AE/MP — each is plausibly its own
  future `implementation-reference` or `interfaces-events` node; not folded
  into this one per the one-node-one-idea rule.
- Editing `architecture-containers-agent-runtime.md` to add an inbound
  `has-part` edge — that inverse is schema-generated, not hand-authored.
