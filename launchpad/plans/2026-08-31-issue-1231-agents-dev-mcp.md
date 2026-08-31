# Plan: issue #1231 — platforms/agents/dev-mcp.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/agents/dev-mcp.md` does not exist (confirmed by `find`).
- `launchpad/docs/corpus/templates/component.md` (`corpus-template-component`) already exists and
  is a close, non-diagram, standalone-component template (`type: implementation`), distinct from
  `templates/architecture-component.md` (which requires a container to decompose and a diagram —
  wrong fit here since dev-mcp is one crate, not a container being decomposed).
- Issue #1231's DoD tail ("states responsibility and well-defined interface/boundary", "names
  dependencies and collaborators", "links source implementation and tests", "explains only
  component-level behavior, not the entire containing platform") maps directly onto
  `templates/component.md`'s required sections (Responsibility, Public interface, Dependencies,
  Boundary).
- `crates/buzz-dev-mcp` is a real crate: lib (`buzz_dev_mcp`) + bin (`buzz-dev-mcp`), 11 source
  files, no crate-level `//!` doc comment on `lib.rs` (gap to disclose), inline `#[cfg(test)]`
  unit tests in 8 of 11 files, no dedicated `tests/` directory, no crate README.
- Repository revision for this task: `cad6c375fdcc590158c1456c9fc7875f0f84a844`.

## STEP 1 — Confirm type and id

Use `type: implementation` (per `corpus-template-component`'s own precedent/reasoning) and
`id: platforms-agents-dev-mcp` (taxonomy-path form, per issue's own example). No existing
corpus node targets this id.

## STEP 2 — Gather evidence

Read `crates/buzz-dev-mcp/{lib,main,paths,read_file,shell,str_replace,todo,tree,rg,view_image,
shim}.rs`, `Cargo.toml`; cross-crate usage in `crates/buzz-acp/src/{acp.rs,config.rs,pool.rs}`,
`crates/buzz-backend-kubernetes/src/env.rs`, `crates/sprig/{Cargo.toml,src/main.rs}`,
`crates/buzz-agent/src/agent.rs`; repo root `AGENTS.md`. All already read this session.

## STEP 3 — Write the node

Follow `templates/component.md`'s skeleton: Responsibility, Public interface (7 MCP tools +
multicall personalities), Dependencies (depends on / depended on by, cited to Cargo.toml),
Boundary, Relationships (none — no architecture-component/container node exists in the corpus
yet to target), Scope and omissions (including the missing crate-doc-comment gap and untested
`view_image`/`shell` edge cases not directly verified).

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix until exit 0.

## STEP 5 — Gate and commit

Run the unittest suite standalone, then commit in a separate call, per the harness contract.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether a future `architecture-component` node for the agent-runtime container will want a
  `part-of` edge from this node — deferred; no such node exists yet in the corpus.

## LEFT OUT

- Any second hand-authored corpus document.
- Any change to `crates/buzz-dev-mcp` runtime behavior.
- Deciding whether `buzz-dev-mcp` should grow a crate-level `//!` doc comment (flagged as a gap
  in the node's own Scope and omissions, not fixed here).
