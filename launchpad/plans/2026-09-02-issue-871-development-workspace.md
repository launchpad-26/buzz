# Issue #871 — development/workspace.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/templates/reference.md` are merged on `origin/launchpad`. `launchpad/docs/corpus/development/workspace.md` does not exist (`ls launchpad/docs/corpus/development/` returns `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md` only). `development/repository-layout.md` (#863) is **not** on `origin/launchpad` — confirmed against `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, so it is not a legitimate relationship target however the sibling branch stands.

STEP 1  Gather evidence by running commands, not by reading prose: count the root `Cargo.toml` `[workspace] members` block with `awk '/^members = \[/,/^\]/' Cargo.toml | grep -c '^\s*"'` and the `crates/` subset with the same pipeline; diff the `crates/` member set against `ls -d crates/*/`; read `exclude`, `[workspace.package]`, `[workspace.dependencies]`; open `desktop/src-tauri/Cargo.toml`, `pnpm-workspace.yaml`, root `package.json`, `mobile/pubspec.yaml`, `launchpad/crates/knowledge/Cargo.toml`, `examples/countdown-bot/Cargo.toml`, `rust-toolchain.toml`, `launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md`, `launchpad/AGENTS.md` §3, and the `Justfile` recipes that cross a workspace boundary. Do **not** inherit any count from `development/build.md`. ← RUNS HERE

STEP 2  [needs 1] Write schema-valid front matter — id `development-workspace`, type `development`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]` — with the first FACT recording the revision as a commit citation, and one ledger entry per substantive body claim, classed FACT / INFERENCE (with `confidence`) / TEAM_KNOWLEDGE (with `provided_by`, no `confidence`). Declare only relationships whose target id is confirmed with `git show origin/launchpad:<path>`.

STEP 3  [needs 2] Write the body on the `templates/reference.md` shape — reference description, structured entries (tables of members, shared keys, workspace units), a "how something works" prose layer where entries would otherwise be illegible, an explicit boundary against `corpus-development-build` (which owns compiling) and against the unmerged repository-layout node, relationships, and scope-and-omissions carrying both the boundary and the expected-but-not-verified list.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0. Re-open every citation and re-run every count against the recorded revision before committing.

STEP 5  [needs 4] Run the corpus unittest suite bare and unpiped as the sole command in its own call, confirm `OK`, then in a separate call `git add` the document and this plan and `git commit -s`. Stop at the commit — no push, no PR.

PARALLEL: none — one document, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK`, run bare and unpiped. Never `--no-verify`; never `git commit --amend` (blocked by `git-safety.sh`), so re-verify before committing rather than after.

BUDGET: small — one Markdown document plus this plan, no code changes. Evidence is roughly a dozen manifests and config files plus two decision records.

OPEN: `development/build.md` (merged, `corpus-development-build`) states the workspace has "30 entries — 29 crates under `crates/` plus `examples/countdown-bot`". That is wrong at HEAD (32 / 30) and was already wrong at its own recorded revision `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, where the block held 31 entries — 30 under `crates/` plus `examples/countdown-bot`. Filed at #2030; this node states its own independently produced count and cites the command that produced it, and does not correct or restate `build.md`. `desktop/src-tauri` turns out to be a second workspace **root** (`[workspace] members = ["crates/buzz-terminal"]`), not merely an excluded package — that is documented here as structure, not as a defect.

LEFT OUT: Build and compile commands, their exit codes and their failure modes — `corpus-development-build` owns those and this node does not restate them. Toolchain provisioning — `development-hermit` owns it. What lives in which directory — that is #863's `repository-layout.md`, unmerged, and this node states the boundary rather than pre-empting it. No edit to `development/build.md`, to the root `Cargo.toml`, or to any manifest.
