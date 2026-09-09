# Plan: issue #1229 — document platforms/agents/acp-harness.md

## ALREADY TRUE

- Target file `launchpad/docs/corpus/platforms/agents/acp-harness.md` does not exist
  on `origin/launchpad` (confirmed: not in `git ls-tree -r origin/launchpad --
  launchpad/docs/corpus`) and does not exist in this worktree.
- `launchpad/docs/corpus/templates/component.md` is merged on `origin/launchpad`
  (present at the branch point, commit `cad6c375fdcc590158c1456c9fc7875f0f84a844`).
  Its Required Sections (Responsibility, Public interface, Dependencies, Boundary,
  Relationships, Scope and omissions) and its `type: implementation` directive match
  this issue's DoD tail bullets verbatim ("States responsibility and well-defined
  interface/boundary", "Names dependencies and collaborators", "Links source
  implementation and tests", "Explains only component-level behavior") — confirmed
  identical across sibling issues #1230/#1231 (same DoD tail, different subject),
  so this is the assigned template for the `platforms/agents/*` batch, not an
  invented fit.
- `crates/buzz-acp/src/lib.rs` has no crate-level `//!` doc comment (starts at
  `#![deny(unsafe_code)]`); `Cargo.toml`'s `description` field and `README.md`
  carry the crate's authored responsibility statement instead.
- The crate's only items visible outside `buzz_acp` are `pub fn run()`
  (lib.rs:1897) and `pub use usage::TurnUsage` (lib.rs:17) — every `mod` (acp,
  config, engram_fetch, filter, observer, pool, pool_lifecycle, prompt_framing,
  prompt_project, queue, relay, setup_mode, usage) is private, so `pub` items
  inside them (e.g. `config::CliArgs`, `acp::AcpClient`) are crate-internal only.
- `crates/sprig/Cargo.toml` depends on `buzz-acp` and `crates/sprig/src/main.rs`
  calls `buzz_acp::run()` directly — the one real inbound dependency edge.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
  `architecture-containers-agent-runtime`) exists on `origin/launchpad` and
  already documents buzz-acp as one of three crates composing the agent-runtime
  container — a safe `references` target (not `part-of`: no
  `architecture-component` node decomposing that container exists yet, and the
  component template reserves `part-of` for that specific relationship).

## STEP 1 — Confirm evidence set from real source

Read `crates/buzz-acp/{Cargo.toml,README.md,src/lib.rs,src/acp.rs,src/config.rs,
src/relay.rs,src/filter.rs,src/queue.rs,src/pool.rs,src/pool_lifecycle.rs,
src/setup_mode.rs,src/usage.rs,src/observer.rs,src/engram_fetch.rs,
src/prompt_framing.rs,src/prompt_project.rs,src/main.rs,tests/pool_lifecycle_state.rs}`
module-doc-comment level (done). Record `git rev-parse HEAD` for provenance.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/platforms/agents/acp-harness.md` against
`component.md`'s Required Sections: Purpose/scope, Responsibility, Public
interface (both the thin Rust API and the operational CLI/env-var/owner-command
surface, since this is a binary-first crate), Dependencies (depends-on /
depended-on-by, cited to `Cargo.toml`), Boundary, Relationships (`references:
architecture-containers-agent-runtime`), Scope and omissions. `type:
implementation`, `status: draft`, `origin: launchpad`.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root;
fix anything it names.

## STEP 4 — Gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as a sole command; confirm `OK`. Then commit with `git commit -s`.

## STEP 5 — Verify

Re-read the diff against every DoD bullet; re-open every cited path/symbol to
confirm it supports its claim; confirm exactly one canonical document was added.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether `platforms` (directory-derived) or `implementation` (template-mandated)
  is the "correct" `type` value is not settled by any single authoritative
  source read for this task — resolved here in favor of the template's explicit
  instruction plus DoD-bullet correspondence, since Feature #614's acceptance
  criteria requires every node to "use the assigned template."

## LEFT OUT

- No second corpus document. No `architecture-component` node for the
  agent-runtime container (that's a separate, unfiled task — noted as a gap in
  Scope and omissions, not created here).
- No changes to `crates/buzz-acp` source.
