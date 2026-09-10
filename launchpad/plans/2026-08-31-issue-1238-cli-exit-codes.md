# Plan: issue #1238 — document platforms/cli/exit-codes.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/cli/exit-codes.md` does not exist (no `platforms/`
  directory exists at all on `origin/launchpad` yet).
- `launchpad/docs/corpus/architecture/containers/cli.md` (id `architecture-containers-cli`,
  `type: architecture`) already documents `buzz-cli` at container level and explicitly
  defers "full per-subcommand behavior" and deeper implementation-reference detail to
  other nodes — this task is exactly that deeper detail for one facet (the exit-code
  contract).
- `crates/buzz-cli/src/error.rs` is the sole place `CliError` is defined and mapped to a
  process exit code (`exit_code`) and a JSON stderr envelope (`print_error`).
- `crates/buzz-cli/README.md` and root `CLAUDE.md` both carry a one-line summary of the
  exit codes that is accurate but coarser than the real mapping (e.g. neither mentions
  that `NotFound` also maps to 1 or that `DeliveryUnknown` also maps to 2).
- `launchpad/docs/corpus/templates/reference.md` (Diátaxis Reference form) is merged and
  names "a status code's meaning" as its own worked example of Reference-shaped content
  — the closest template fit for a small, enumerable exit-code lookup table.

## STEP 1 — Confirm the CliError → exit-code → JSON mapping against source

Read `crates/buzz-cli/src/error.rs` in full (`CliError`, `exit_code`, `print_error`,
`is_retryable_error`), `crates/buzz-cli/src/lib.rs`'s `run_from_args` (clap-parse-failure
and `--help`/`--version` paths, which return 1 and 0 respectively without ever
constructing a `CliError`), and `crates/buzz-cli/src/main.rs` (the single
`std::process::exit(...)` call). Cross-check `crates/buzz-cli/README.md` and root
`CLAUDE.md`'s terse summaries and `crates/buzz-cli/TESTING.md`'s live-testing runbook
against the real mapping.

## STEP 2 — Write the node against the `reference` template

Front matter: `id: platforms-cli-exit-codes`, `type: platforms` (matches the file's own
corpus-surface directory; no `platforms`-typed sibling is merged yet to follow as
precedent, so this is recorded as an INFERENCE), `status: draft`, `origin: launchpad`,
`audiences: [agent, developer]`. One evidence entry per substantive claim, all opened and
read directly. `relationships: part-of -> architecture-containers-cli` (that node already
exists on `origin/launchpad` and explicitly reserves this depth of detail for a separate
node) plus an optional `references -> corpus-template-reference`.

Body: Reference description, a structured-entries table (exit code / `CliError`
variant(s) / JSON `error` category / condition / retryable), Boundary, Relationships,
Scope and omissions — naming as an explicit gap that `exit_code()` itself has no direct
unit test (only `is_retryable_error` and the JSON envelope shape do).

## STEP 3 — Validate in isolation

Run `validate.py` with the new file present, then with it stashed, and diff the FAIL
counts — must be identical (21 pre-existing) with the file present or absent.

## STEP 4 — Gate and commit

Run the corpus unittest suite as the sole content of one Bash call, then `git add` +
`git commit -s` as a separate call.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, and removing the
  new file reproduces the same 21 pre-existing FAILs (no new FAIL introduced).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Every Definition of Done bullet in issue #1238 is satisfied.

## OPEN

- Whether `type: platforms` is the corpus's eventual convention for CLI-surface reference
  nodes, versus some other enum member — no merged precedent exists yet; recorded as an
  INFERENCE in the node itself.

## LEFT OUT

- Any change to `crates/buzz-cli/src/error.rs`, `README.md`, or `CLAUDE.md` — this task
  documents current behavior, it does not change or "fix" the terser upstream summaries.
- Documenting `buzz-admin`'s (separate crate) exit-code behavior, if it has one — out of
  scope for this node, which is `buzz-cli` only.
- A second node for `buzz-cli`'s retry/backoff policy in `client.rs` — related but a
  separate concept, not folded in here.
