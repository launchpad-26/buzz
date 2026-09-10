# Plan: issue #1234 — platforms/agents/sprig corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/agents/sprig.md` does not exist yet (confirmed with `test -f`).
- `launchpad/docs/corpus/templates/component.md` (merged on `origin/launchpad`) is the fitting
  template — one software component, standing alone, `type: implementation`, sections
  Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope and
  omissions. Sibling in-flight tasks (#1229, #1230) for the same platform used it successfully.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
  `architecture-containers-agent-runtime`, `type: architecture`, merged on `origin/launchpad`)
  already documents `sprig` at length: names it a multicall binary bundling `buzz-acp`,
  `buzz-agent`, `buzz-dev-mcp`; a Technology table row; the two release pipelines
  (`sprig.yml`, `sprig-image.yml`); and states none of the runtime crates touch Postgres
  directly. This is a valid `part-of` relationship target (confirmed present in
  `git ls-tree origin/launchpad`).
- `crates/sprig/src/main.rs` (53 lines, no `lib.rs`, no crate-level doc comment) is the entire
  implementation: `dispatch()` matches on `argv0`'s basename to `buzz_acp::run()`,
  `buzz_agent::run()`, sprig's own `-V`/`-h` handling, or falls through to `buzz_dev_mcp::run()`.
  `crates/sprig/Cargo.toml` depends only on `buzz-acp`, `buzz-agent`, `buzz-dev-mcp` (all
  path deps) — no external crates of its own. Nothing in the workspace depends on `sprig`
  (it is the top-level bundling binary).
- `Dockerfile.sprig` builds `sprig` under `[profile.sprig]` (workspace `Cargo.toml`) and
  symlinks all personality names to it; `scripts/sprig-entrypoint.sh` always execs `buzz-acp`
  as the container's default personality.

## STEP 1 — Draft front matter

`id: platforms-agents-sprig`, `type: implementation`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`, one commit-citation FACT for provenance, plus one
evidence entry per substantive claim (dispatch logic, Cargo.toml deps, profile, Dockerfile,
entrypoint, CI release pipelines). `relationships: [{type: part-of, target:
architecture-containers-agent-runtime}]` — confirmed resolvable in `origin/launchpad`'s corpus
tree. No relationships toward sibling `platforms-agents-*` ids — none of those branches are
merged into `origin/launchpad` yet.

## STEP 2 — Write the body against `templates/component.md`'s required sections

Purpose/scope paragraph; Responsibility (cited to `Cargo.toml` description + `main.rs`, since
there is no crate-level `//!` comment); Public interface (the `sprig` binary's argv0-dispatch
contract — there is no `pub` Rust API to cite, only the process personality surface); Dependencies
both directions (`Cargo.toml` for depends-on; nothing internal depends on `sprig`, only
`Dockerfile.sprig`/CI consume the built artifact); Boundary (not architecture-component, not
implementation-reference, not a duplicate of the container node or of `buzz-acp`/`buzz-agent`/
`buzz-dev-mcp`'s own component nodes); Relationships; Scope and omissions.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root; fix any
reported errors; confirm the 21 pre-existing FAILs are unchanged with the new file stashed out.

## STEP 4 — Earn the commit gate

Run the corpus unittest suite as its own sole-content command, confirm `OK`, then commit in a
second, separate command.

## STEP 5 — Verify

Re-read the diff against issue #1234's Definition of Done line by line; re-open every cited
file/line; confirm exactly one new hand-authored file plus this plan; re-run validate.py.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, contributing zero new
  FAIL lines beyond the pre-existing 21.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether `architecture-containers-agent-runtime`'s Technology table counts as the
  "architecture-component node's building-block table" the component template's `part-of`
  guidance literally names — no dedicated `architecture-component` instance node exists yet for
  this container. Read as the closest available, resolvable fit, matching the precedent set by
  the in-flight `buzz-agent`/`acp-harness` sibling nodes.
- No node has yet merged from `templates/component.md` for a binary-only crate with no `lib.rs`
  and no public Rust API — `sprig`'s "public interface" is necessarily the argv0 dispatch
  contract and CLI surface rather than exported items, which is a variant this template's own
  Scope-and-omissions section had flagged as untested.

## LEFT OUT

- Any second concept (a dedicated node for the multicall-dispatch pattern itself, or for
  `Dockerfile.sprig`/the release pipelines as their own deployment node) — those stay separate
  tasks per `AGENTS.md`'s one-node-one-idea rule.
- Editing `architecture/containers/agent-runtime.md` — out of scope per issue #1234's own
  "Out of scope" list (no second hand-authored canonical document).
- Documenting `buzz-acp`, `buzz-agent`, or `buzz-dev-mcp` as components in their own right —
  those are issues #1229/#1230/#1231's subjects, not this one's.
