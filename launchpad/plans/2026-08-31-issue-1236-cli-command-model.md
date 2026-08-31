# Issue #1236 — document platforms/cli/command-model.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`;
  no `platforms/cli/*.md` node exists.
- `launchpad/docs/corpus/architecture/containers/cli.md` already documents
  `buzz-cli` at the container level (responsibility, tech, interfaces). This
  task must not restate that content — it documents one component inside
  that container: the command model (clap `Cli`/`Cmd` struct tree and
  dispatch), not the whole container.
- `launchpad/docs/corpus/templates/component.md` (merged) is the assigned
  template: its "Required sections" (Responsibility, Public interface,
  Dependencies, Boundary, Relationships, Scope and omissions) map directly
  onto the issue's DoD bullets (responsibility/interface-boundary,
  dependencies/collaborators, links to implementation/tests,
  component-level-not-platform-level). Front matter per the template:
  `type: implementation`.
- Repository revision recorded for this node: `cad6c375fdcc590158c1456c9fc7875f0f84a844`.

## STEP 1 — Confirm no existing/duplicate coverage

Checked: no `platforms/**` files on `origin/launchpad`; no open PR titled
around `command-model`; target file does not exist in this worktree.

## STEP 2 — Gather evidence from `crates/buzz-cli`

Read `src/lib.rs` (Cli/Cmd struct tree, `OutputFormat`, `run_from_args`,
`run()` dispatch match), `src/commands/mod.rs` (module list, shared
helpers), each `commands/*.rs`'s `dispatch` signature (which ones take
`&cli.format`), `src/error.rs` (`CliError`, exit codes), `src/validate.rs`
(input validators), `Cargo.toml` (clap dependency/features, crate identity).

## STEP 3 — Write the node

`launchpad/docs/corpus/platforms/cli/command-model.md`, `type: implementation`,
using `component.md`'s skeleton: Responsibility / Public interface /
Dependencies / Boundary / Relationships / Scope and omissions. No
`relationships` — no sibling `platforms/**` node exists yet on
`origin/launchpad` to target, and `architecture-containers-cli` is a
different node type (architecture, not implementation) documenting a
different scope (whole container) rather than a natural `part-of`/`depends-on`
target for this component-scoped node.

## STEP 4 — Validate

Run the corpus unittest suite, then `validate.py` isolation check (stash the
new file, confirm the same pre-existing 21 FAILs, restore).

## STEP 5 — Commit

Two separate Bash calls per the batch protocol: unittest alone, then
`git add` + `git commit -s`.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK
- `python3 launchpad/project-intelligence/corpus/validate.py` → adds zero new FAIL lines vs. the baseline 21

## OPEN

- Whether a future `architecture-component` node for the `cli` container
  (once that template and an instance exist) should list this command-model
  node as a building-block row — left for that later node to add, per
  `component.md`'s own guidance that the `part-of` edge is optional and
  should be added from the container-decomposition side.

## LEFT OUT

- Per-subcommand-group behavioral detail (all 22 groups) — that is each
  group's own implementation-reference/capability node, not this one.
- Authentication (env vars, NIP-98 signing) — `platforms/cli/authentication.md`
  (issue #1235) owns that.
- Retry/timeout policy and HTTP/WS transport details — already covered by
  `architecture-containers-cli.md`; this node only names the dependency on
  `client.rs`, not its internals.
