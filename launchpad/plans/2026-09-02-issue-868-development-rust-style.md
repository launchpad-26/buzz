# Issue #868 — development/rust-style.md

ALREADY TRUE: `launchpad/docs/corpus/development/rust-style.md` does not exist (`ls launchpad/docs/corpus/development/` → `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md` only). Working revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`git rev-parse HEAD` in the isolated worktree, branched from `origin/launchpad`). Four sibling `development/` nodes are merged on `origin/launchpad` with ids confirmed by `git show origin/launchpad:<path>`: `corpus-development-build`, `development-hermit`, `development-prerequisites`, `debugging`.

STEP 1  Gather evidence from the real enforcement surfaces, not from prose: `rust-toolchain.toml`, `Cargo.toml` (`[workspace.package]`, absence of `[workspace.lints]`), `deny.toml`, `.cargo/config.toml`, `Justfile` (`fmt`, `fmt-check`, `clippy`, `check`, `test-unit`, `file-size-check`), `lefthook.yml` (pre-commit + pre-push lanes), `.github/workflows/ci.yml` (`rust-lint`, `security` jobs), `CONTRIBUTING.md` § Code Style, and every crate-level `#![...]` inner attribute under `crates/` and `desktop/src-tauri/src`. Confirm by search that no `rustfmt.toml`, `.rustfmt.toml` or `clippy.toml` is tracked, and that no `unwrap_used`/`expect_used`/`panic_used` lint is configured anywhere. ← RUNS HERE

STEP 2  [needs 1] Count, do not assume: how many of the 26 `crates/*/src/lib.rs` carry `#![warn(missing_docs)]`, how many crates carry an `unsafe_code` attribute, and which named crates carry neither. Establish the machine-vs-review split per rule, and measure the one concrete counter-example that shows the 1000-line file ceiling does not reach `crates/` (largest `.rs` file under `crates/`).

STEP 3  [needs 2] Write the node: schema-valid front matter (id `development-rust-style`, type `development`, status `draft`, origin `launchpad`, audiences `[developer, agent, reviewer]`, evidence ledger with the revision as the first FACT), plus `relationships` naming only ids confirmed present on `origin/launchpad`. Body in reference form: a per-rule enforcement table (rule → enforced by → where it runs → machine or review), config inventory, named gaps, boundary against `#854` (dart-style) and `#870` (typescript-style), and scope-and-omissions.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it reports PASS.

STEP 5  [needs 4] Re-verify every DoD bullet and re-open every citation BEFORE committing (`git commit --amend` is blocked by `git-safety.sh`). Then run the corpus unittest suite bare and unpiped as the sole command in its own call, and commit plan + document with `git commit -s` in a separate call. Stop at the commit — no push, no PR.

PARALLEL: none — one file, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK, run bare and unpiped as the sole command in its tool call. Review passes are deferred to the batch owner.

BUDGET: small — one document, no code change. Evidence gathering is roughly a dozen config/workflow files plus one repo-wide attribute sweep.

OPEN:
- `CONTRIBUTING.md` states "All crates enforce `#![deny(unsafe_code)]`", but only 17 of the 30 directories under `crates/` carry any `unsafe_code` attribute. Reported as a measured gap in the node body; fixing `CONTRIBUTING.md` is not this task.
- `CONTRIBUTING.md` documents the clippy invocation as `cargo clippy --all-targets --all-features -- -D warnings`, while `Justfile`'s `clippy` recipe — the one CI and `just check` actually run — is `cargo clippy --workspace --all-targets -- -D warnings`, with no `--all-features`. Reported, not fixed.
- Root `AGENTS.md` § Quality Gates states pre-push hooks run "clippy (workspace + Tauri)", but `lefthook.yml`'s pre-push stage has no lane running the workspace `just clippy` recipe — only `just desktop-tauri-clippy`. Reported as a fourth drift row in the node.
- Nothing machine-enforces the "no `unwrap()`/`expect()` in production paths" rule: no `unwrap_used`/`expect_used`/`panic_used` clippy lint is configured in any tracked file. Named as a gap in the node.
- `CONTRIBUTING.md`'s prerequisites table says "Rust 1.88+" and `[workspace.package].rust-version` is `1.88.0`, while `rust-toolchain.toml` pins `1.95.0`. These are a floor and a pin respectively, so they are recorded as two distinct facts rather than as a contradiction.
- Whether the node should carry `relationships` toward `development-hermit` and `corpus-development-build`: both ids are confirmed on `origin/launchpad`, so both edges are declared.

LEFT OUT:
- Dart/Flutter style (`#854`) and TypeScript/Biome style (`#870`) — sibling tasks; this node states the boundary and does not restate their rules.
- Any change to `CONTRIBUTING.md`, `Justfile`, `lefthook.yml`, `deny.toml` or crate attributes. Every drift found is reported in the node, not repaired here.
- `deny.toml`'s advisory/licence policy beyond naming that `cargo-deny check` is the CI job that runs it — dependency policy is a distinct subject from source style and would be a second node.
- Any claim about how clippy behaves on a crate that was not opened, and any count derived from a truncated listing.
