# Plan: issue #1239 — platforms/cli/output-contract corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/cli/output-contract.md` does not exist; no
  `platforms/` directory exists anywhere in the corpus yet on `origin/launchpad`.
- `architecture-containers-cli` (`launchpad/docs/corpus/architecture/containers/cli.md`)
  is already merged on `origin/launchpad`, so a `part-of` edge to it resolves.
- The `component.md` template (`corpus-template-component`, `type: implementation`)
  fits issue #1239's DoD tail best: responsibility, well-defined interface/boundary,
  dependencies/collaborators, links to implementation and tests, and an explicit
  "not the whole platform" boundary are exactly its five required-plus-boundary
  sections — closer than `architecture-component.md` (requires a Mermaid
  container-decomposition diagram, not asked for here) or `reference.md`
  (Diátaxis reference form, catalog-shaped, not a responsibility/interface node).
- Real source read and verified in `crates/buzz-cli/src/`: `client.rs`
  (`normalize_events`, `normalize_write_response`, `create_response_with_id_if_accepted`,
  `extract_relay_response_field`), `error.rs` (`exit_code`, `print_error`,
  `is_retryable_error`), `lib.rs` (`Cli.format` as a top-level clap field, `OutputFormat`
  enum), `commands/mod.rs` (`parse_write_response`, duplicate → `Conflict`),
  `commands/feed.rs` / `commands/messages.rs` (3-key compact projection of raw events),
  `commands/users.rs` / `commands/channels.rs` (compact/json built from a
  domain-reshaped object, not the raw 7-field event — root CLAUDE.md's "canonical
  7-field event on reads" claim does not hold uniformly across every read command).

## STEP 1 — Draft `launchpad/docs/corpus/platforms/cli/output-contract.md`

Use the `component.md` skeleton. `id: platforms-cli-output-contract` (matches the
issue's own alias and the un-prefixed `architecture-<segment>-<segment>` id
convention `architecture-containers-cli` already established for this same
architecture/platforms tree, rather than the governance-node `corpus-` prefix).
`type: implementation`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`. Body: Responsibility (normalization +
exit-code mapping, cited to the real functions), Public interface (table:
`normalize_events`, `normalize_write_response`, `create_response_with_id_if_accepted`,
`parse_write_response`, `exit_code`, `print_error`, the `--format` flag), Dependencies
(depends on: `serde_json`, `clap`, `thiserror`, `reqwest` via `Cargo.toml`; depended on
by: every `commands/*.rs` read/write path), Boundary (not the whole CLI container, not
per-command business logic, not the relay's own response shape), Relationships
(`part-of: architecture-containers-cli`), Scope and omissions.

## STEP 2 — Cite every claim to an opened source

One evidence entry per body claim; FACT only where the file was actually read (all of
the above). Bare repo-relative paths, no `:line`/`:start-end` unless a range is load-bearing,
and never `#line=`/`#symbol=`. Exactly one commit-only FACT for provenance
(`git rev-parse HEAD` at draft time).

## STEP 3 — Validate isolation

Temporarily move the new file out, run `validate.py`, confirm the same 21
pre-existing FAILs, restore the file, run again, confirm zero *new* FAILs
(an UNVERIFIED notice on the provenance commit citation is expected).

## STEP 4 — Run the corpus unit tests (gate 5a) and commit (gate 5b)

Exactly as specified in the batch runbook — two separate tool calls, no chaining.

## STEP 5 — Verify against the issue's DoD checklist line by line, re-open every cite

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAILs.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — OK, as its own sole Bash call.
- `git commit -s` succeeds (fresh gate stamp).

## OPEN

- Whether `platforms/cli/*` sibling nodes from other in-flight worktrees in this
  same Feature will later want a `references` edge to this node — not decided here,
  since those worktrees are invisible to this one per the batch's own isolation rule.

## LEFT OUT

- Any change to `crates/buzz-cli` runtime behavior — this is documentation only.
- A second corpus node for any other CLI concern (auth, retry policy, agent
  management) — those are separate tasks if/when filed.
