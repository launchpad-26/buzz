# Plan — issue #862: document `development/public-api-changes.md`

Issue: launchpad-26/buzz#862 (parent PRD #619)
Target: `launchpad/docs/corpus/development/public-api-changes.md`
Branch: `task/862-development-public-api-changes`
Base revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`origin/launchpad`)

## ALREADY TRUE

- The worktree exists on `task/862-development-public-api-changes`, branched from
  `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`.
- The target file does not exist:
  `ls launchpad/docs/corpus/development/public-api-changes.md` -> `No such file or directory`.
  `launchpad/docs/corpus/development/` contains exactly `build.md`, `debugging.md`,
  `hermit.md`, `prerequisites.md`.
- `launchpad/docs/corpus/templates/procedure.md` exists on `origin/launchpad` with
  `id: corpus-template-procedure`, and prescribes the body shape: Overview, optional
  *Before you start*, ordered task sequence, *See also*, *Boundary*, *Relationships*,
  *Scope and omissions*.
- `launchpad/docs/corpus/architecture/containers/cli.md` exists on `origin/launchpad`
  with `id: architecture-containers-cli` and already carries the CLI's exit-code table
  as a FACT — so this node must link it rather than restate it.
- There is no `governance/` directory in the corpus. `#908`
  (`task: document governance/compatibility-policy.md`) and `#911`
  (`task: document governance/deprecation-policy.md`) are both OPEN and unmerged.
- `#861` (`development/protocol-changes.md`) and `#858`
  (`development/event-kind-changes.md`) are both OPEN and unmerged.
- Evidence already gathered (sources opened, not merely located):
  `AGENTS.md:152`, `CONTRIBUTING.md` §§ Linting / What a Good PR Looks Like /
  Architecture Overview / How to Add a New Event Kind / How to Add a New API Endpoint,
  `Cargo.toml`, `Justfile` (`check`, `clippy`, `ci`, `test-unit`),
  `.github/workflows/ci.yml` (`rust-lint` job), `crates/buzz-cli/src/lib.rs`,
  `crates/buzz-cli/src/error.rs` (incl. its `#[cfg(test)] mod tests`),
  `crates/buzz-cli/README.md`, `crates/buzz-sdk/src/lib.rs`,
  `crates/buzz-sdk/Cargo.toml`, `crates/buzz-auth/src/nip_fi/verifier.rs`,
  `crates/buzz-auth/src/nip_fi/config.rs`, `crates/buzz-relay/src/router.rs`.

## STEP 1 — settle the node's boundary and id

- `id: development-public-api-changes` (`<directory>-<stem>`), matching
  `development-hermit` / `development-prerequisites`. `standards/naming.md` MUST 3
  prescribes a `corpus-` prefix; content-node practice does not follow it, and the
  divergence is already tracked. Note in the report, do not deviate, do not file.
- Boundary to state explicitly in the body: this node owns **procedure** for changing a
  Rust/CLI/HTTP public surface. It does not own the wire protocol (#861), event kinds
  (#858), compatibility **policy** (#908), or deprecation **policy** (#911) — each
  named with its verified open/unmerged state.

**done-when:** boundary and id written down; every issue number re-verified with
`gh issue view`, not recalled.

## STEP 2 — finish the enforcement evidence

- Confirm empirically that `#![warn(missing_docs)]` plus `-D warnings` is what turns the
  `AGENTS.md` doc-comment rule into a gate, and confirm the crate-by-crate coverage
  (12 of 26 lib crates carry the attribute; `buzz-cli` does not, `buzz-sdk` does).
- Confirm no test pins `buzz_cli::error::exit_code`'s mapping, and that `error` is a
  private module in `crates/buzz-cli/src/lib.rs` so no integration test could.

**done-when:** each enforcement claim is either a FACT with an opened source or an
INFERENCE with a confidence, and the unverifiable ones are named in *Scope and
omissions*.

## STEP 3 — draft the node

Body per `templates/procedure.md`: one `#` heading; *What counts as a public surface
here*; *Before you start*; one ordered, executable, project-specific task sequence
covering doc comments, tests, docs-that-must-move, and the gate; *Verify*; *Roll back*;
*See also*; *Boundary*; *Relationships*; *Scope and omissions*.

Front matter: `id: development-public-api-changes`, `type: development`,
`status: draft`, `origin: launchpad`, audiences, provenance ledger with the base
revision as the first FACT, relationships only to ids confirmed via
`git show origin/launchpad:<path>`.

Spell "front matter"; call `evidence` the "provenance ledger"; under 1000 lines.

**done-when:** `python3 launchpad/project-intelligence/corpus/validate.py` reports PASS.

## STEP 4 — re-verify against the DoD, then commit

Walk the issue's eleven DoD bullets against the drafted file, re-open every citation,
then run the corpus unit tests bare and unpiped, then `git add` + `git commit -s`.
No amend is available, so all re-verification happens before the commit.

**done-when:** `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
reports OK, and the commit exists.

## PARALLEL

Steps 1 and 2 are independent and were gathered concurrently. Step 3 depends on both.
Step 4 depends on step 3.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` -> PASS
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` -> OK
- Every `relationships[].target` resolves in
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
- Exactly one level-1 heading; "front matter" two words; "provenance ledger"
- Under 1000 lines (repository-wide `just file-size-check` ceiling)

## BUDGET

One hand-authored document plus this plan. Two files, one commit. No push, no PR.

## OPEN

- Whether the `corpus-` prefix divergence between `standards/naming.md` MUST 3 and
  content-node practice resolves toward the standard or toward practice. Out of scope
  here; the brief settles the id for this node.
- Whether `cargo clippy --workspace --all-targets -- -D warnings` actually fails on a
  missing doc comment was verified only for one crate's current clean state, not by
  deliberately introducing an undocumented public item.

## LEFT OUT

- Any second hand-authored corpus document.
- Compatibility policy and deprecation policy prose (#908, #911 own those).
- Wire-protocol and event-kind procedure (#861, #858 own those).
- Filing issues for findings; they go in the report only.
- Any change to product code, `AGENTS.md`, `CONTRIBUTING.md`, or the naming standard.
