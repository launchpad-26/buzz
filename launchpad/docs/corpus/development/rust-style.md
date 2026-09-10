---
id: development-rust-style
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "No rustfmt configuration file is tracked anywhere in the repository: `git ls-files` filtered for `rustfmt.toml`, `.rustfmt.toml`, `clippy.toml` and `.clippy.toml` returns no rows, and the only two Rust-toolchain-adjacent config files it does return are `deny.toml` and `rust-toolchain.toml`. Formatting is therefore whatever rustfmt's own compiled-in defaults produce, not a style this repository states."
    entry_class: FACT
    evidence:
      - "git_ls_files(filter='(^|/)(\\.?rustfmt\\.toml|clippy\\.toml|\\.clippy\\.toml|rust-toolchain(\\.toml)?|deny\\.toml)$', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> deny.toml, rust-toolchain.toml"
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's Code Style section states 'We use `rustfmt` with default settings', gives `cargo fmt --all` and `cargo fmt --all -- --check` as the format and check commands, and documents the clippy invocation as `cargo clippy --all-targets --all-features -- -D warnings`."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The Justfile recipe CI and `just check` actually run is `clippy: cargo clippy --workspace --all-targets -- -D warnings` -- scoped by `--workspace` and carrying no `--all-features` flag -- which is not the invocation CONTRIBUTING.md documents; `fmt` is `cargo fmt --all` and `fmt-check` is `cargo fmt --all -- --check`."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "CONTRIBUTING.md"
  - statement: "The Justfile's aggregate `check` recipe is `check: fmt-check clippy desktop-check desktop-tauri-fmt-check desktop-tauri-clippy web-check mobile-check security-review-check file-size-check`, so `just check` is the single local entry point that runs both the Rust format check and workspace clippy."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "rust-toolchain.toml pins `channel = \"1.95.0\"` with `profile = \"default\"`, while Cargo.toml's `[workspace.package]` separately declares `edition = \"2021\"` and `rust-version = \"1.88.0\"`; the first is the toolchain every contributor and CI job actually runs, the second is the crates' declared minimum supported version, and CONTRIBUTING.md's prerequisites table lists 'Rust 1.88+' matching the latter."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
      - "Cargo.toml"
      - "CONTRIBUTING.md"
  - statement: "No `[lints]` or `[workspace.lints]` table exists in any Cargo.toml in the repository, and no manifest carries `lints.workspace`: a recursive grep across every tracked Cargo.toml for those three strings returns no matches, so there is no manifest-level lint policy and every crate-level lint decision is an inner attribute in Rust source instead."
    entry_class: FACT
    evidence:
      - "grep_recursive(pattern='\\[lints\\]|\\[workspace.lints\\]|lints.workspace', include='Cargo.toml', root=repo, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> no matches, exit status 1"
      - "Cargo.toml"
  - statement: "Of the 30 directories under crates/, 17 contain at least one `unsafe_code` lint attribute and 13 contain none; the 13 without are buzz-backend-kubernetes, buzz-cli, buzz-datastore-tracing, buzz-media, buzz-pair-relay, buzz-pairing-cli, buzz-persona, buzz-push-gateway, buzz-relay-mesh, buzz-voice, git-credential-nostr, git-sign-nostr and sprig."
    entry_class: FACT
    evidence:
      - "grep_recursive(pattern='unsafe_code', include='*.rs', root='crates/', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> 17 of 30 crate directories match; the 13 non-matching are buzz-backend-kubernetes, buzz-cli, buzz-datastore-tracing, buzz-media, buzz-pair-relay, buzz-pairing-cli, buzz-persona, buzz-push-gateway, buzz-relay-mesh, buzz-voice, git-credential-nostr, git-sign-nostr, sprig"
      - "crates/buzz-core/src/lib.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "CONTRIBUTING.md's 'No Unsafe Code' section asserts 'All crates enforce `#![deny(unsafe_code)]`', which does not hold at this revision: 13 of the 30 crate directories carry no such attribute at all, and two of the 17 that do use a different strength or form -- crates/buzz-agent/src/lib.rs uses `#![forbid(unsafe_code)]` and crates/buzz-dev-mcp/src/lib.rs uses a platform-split pair, `#![cfg_attr(not(windows), forbid(unsafe_code))]` plus `#![cfg_attr(windows, deny(unsafe_code))]`."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "crates/buzz-agent/src/lib.rs"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "Exactly 12 of the 26 crates/*/src/lib.rs files carry `#![warn(missing_docs)]`: buzz-audit, buzz-auth, buzz-conformance, buzz-core, buzz-db, buzz-deletion, buzz-pubsub, buzz-relay, buzz-sdk, buzz-search, buzz-test-client and buzz-workflow. The other 14 -- including buzz-cli, the agent-facing CLI -- carry no missing_docs lint, so no tool checks whether their new public items are documented."
    entry_class: FACT
    evidence:
      - "grep_l(pattern='warn(missing_docs)', paths='crates/*/src/lib.rs', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> 12 files: buzz-auth, buzz-search, buzz-db, buzz-conformance, buzz-audit, buzz-test-client, buzz-core, buzz-deletion, buzz-relay, buzz-sdk, buzz-pubsub, buzz-workflow; ls(crates/*/src/lib.rs) -> 26 files"
      - "crates/buzz-core/src/lib.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "No clippy lint that would machine-enforce the no-unwrap/no-expect rule is configured anywhere: a recursive grep for `unwrap_used`, `expect_used`, `panic_used` and `clippy::pedantic` across every .rs, .toml, .yml and .yaml file in the repository (excluding node_modules and target/) exits with status 1 and prints nothing."
    entry_class: FACT
    evidence:
      - "grep_recursive(pattern='unwrap_used|expect_used|panic_used|clippy::pedantic', include='*.rs,*.toml,*.yml,*.yaml', root=repo, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> no matches, exit status 1"
      - "Cargo.toml"
      - "Justfile"
  - statement: "CONTRIBUTING.md's Error Handling section states the rules that nothing in the toolchain checks: use `thiserror` for library error types, use `anyhow` for binary/application-level error propagation, and do not use `unwrap()` or `expect()` in production code paths -- `unwrap()` is stated to be acceptable in tests. Both crates are declared in Cargo.toml's `[workspace.dependencies]` (`thiserror = \"2\"`, `anyhow = \"1\"`)."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "Cargo.toml"
  - statement: "CONTRIBUTING.md's Logging and Tracing section requires the `tracing` crate for all instrumentation and prefers structured fields over string interpolation, showing `tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\")` as the good form and the interpolated string as the form to avoid; `tracing = \"0.1\"` is declared in Cargo.toml's `[workspace.dependencies]`."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "Cargo.toml"
  - statement: "CONTRIBUTING.md instructs that a clippy warning believed to be a false positive be silenced with a targeted `#[allow(...)]` carrying a comment explaining why, rather than by relaxing the global invocation."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "lefthook.yml's pre-commit stage runs a `rust-fmt` lane globbed to `crates/**` and `examples/countdown-bot/**` whose command is `just fmt` with `stage_fixed: true`, so formatting is auto-applied and re-staged at commit time rather than reported as a failure."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook.yml's pre-push stage contains no workspace-clippy lane: its Rust-globbed lanes are `rust-tests` (running `just test-unit`) and `desktop-tauri-checks` (running `just desktop-tauri-clippy && just desktop-tauri-test`), and the Justfile's `test-unit` recipe runs cargo-nextest and cargo test, never clippy. Workspace clippy and the Rust format check therefore run only in CI, or locally when a developer invokes `just check` / `just ci` by hand."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "Justfile"
  - statement: ".github/workflows/ci.yml defines a `rust-lint` job named 'Rust Lint' whose three steps are `just fmt-check`, `just desktop-tauri-fmt-check` and `just clippy`, gated on `github.event_name == 'push' || needs.changes.outputs.rust == 'true' || needs.changes.outputs.desktop-rust == 'true'`; a separate `security` job runs `cargo-deny check`, gated on the `rust` filter alone."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The repository's 1000-line file-size ceiling does not reach crates/: `just file-size-check` runs only the desktop, web and mobile checkers plus a core unit test, and the desktop checker's Rust rules are rooted at `src-tauri/src` and `src-tauri/crates` relative to `desktop/`, so no rule covers the root `crates/` tree."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "desktop/scripts/check-file-sizes.mjs"
  - statement: "The largest single Rust source file under crates/ is crates/buzz-acp/src/pool.rs at 10,039 lines -- ten times the 1000-line ceiling the desktop, web and mobile trees are held to -- with crates/buzz-acp/src/lib.rs (8,837), crates/buzz-agent/src/llm.rs (7,967) and crates/buzz-relay/src/api/admin/mod.rs (7,651) next; there are 388 .rs files under crates/ in total."
    entry_class: FACT
    evidence:
      - "wc_l(find='crates/**/*.rs', revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> 10039 crates/buzz-acp/src/pool.rs; 8837 crates/buzz-acp/src/lib.rs; 7967 crates/buzz-agent/src/llm.rs; 7651 crates/buzz-relay/src/api/admin/mod.rs; 388 files total"
      - "crates/buzz-acp/src/pool.rs"
  - statement: ".cargo/config.toml sets `[profile.dev] debug = \"line-tables-only\"` and an `[env]` entry `CMAKE_POLICY_VERSION_MINIMUM = \"3.5\"`; it sets no `rustflags`, so it carries no lint or style policy."
    entry_class: FACT
    evidence:
      - ".cargo/config.toml"
  - statement: "deny.toml is dependency policy rather than source style: it holds an `[advisories] ignore` list of four RUSTSEC ids, a `[licenses] allow` list with `confidence-threshold = 0.8` plus seven `[[licenses.clarify]]` blocks, and a `[bans]` table setting `multiple-versions = \"warn\"` and `wildcards = \"allow\"`."
    entry_class: FACT
    evidence:
      - "deny.toml"
  - statement: "Because `just clippy` passes `-D warnings` to the compiler driver, a warn-level lint set by a crate attribute is promoted to a hard error in that invocation -- so `#![warn(missing_docs)]` behaves as a deny in CI for the 12 crates that declare it, while producing no signal at all in the 14 that do not."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "crates/buzz-core/src/lib.rs"
      - ".github/workflows/ci.yml"
    confidence: 0.9
  - statement: "Root AGENTS.md's Quality Gates section states three additional rules as a bare list -- 'No `unsafe` code', 'Do not introduce new `unwrap()` or `expect()` in production paths -- use `?` and proper error types', 'New public API must have doc comments' -- and separately warns that 'Clippy passing does not mean fmt passes; run both'. AGENTS.md is the file CLAUDE.md symlinks to, so both names resolve to the same document."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Root AGENTS.md's Quality Gates section states that pre-push hooks run 'clippy (workspace + Tauri)', which lefthook.yml does not do: its pre-push stage has a `desktop-tauri-checks` lane running `just desktop-tauri-clippy` but no lane running the workspace `just clippy` recipe."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "lefthook.yml"
  - statement: "Issue #868 requires that the node be structured for lookup rather than narrative teaching, contain only facts supported by current source, label generated versus authored values, define scope and omissions, and link authoritative source/schema/config."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#868 definition of done"
  - statement: "Issues #854 and #870 own the sibling dart-style and typescript-style corpus nodes for this directory, so the per-language style rules for Flutter/Dart and for the desktop and web TypeScript trees are out of scope here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#868 dispatch brief, naming #854 development/dart-style.md and #870 development/typescript-style.md"
relationships:
  - type: references
    target: development-hermit
  - type: references
    target: corpus-development-build
---

# Rust style: what this repository enforces, and by what

The Rust style rules that apply to code under `crates/` and
`desktop/src-tauri/`, catalogued one rule at a time with the mechanism that
actually holds each one. The organising distinction is **machine-enforced**
(a tool fails and the change cannot land) versus **review-enforced** (only a
human reading the diff will catch it) — several rules this repository states
as absolutes are in the second category, and two of them are stated in
`CONTRIBUTING.md` in terms that current source does not support.

Look a rule up in the table below; the sections after it give the
configuration inventory the table's "Enforced by" column points at.

## Rule-by-rule enforcement

"Machine" means a command exits non-zero when the rule is broken. "Review"
means nothing in the toolchain reports it.

| # | Rule | Enforced by | Where it runs | Class |
|---|---|---|---|---|
| 1 | Source is rustfmt-formatted | `cargo fmt --all -- --check` (`just fmt-check`); `cargo fmt --all` (`just fmt`) auto-fixes | CI `rust-lint` job; lefthook **pre-commit** `rust-fmt` lane (auto-fix + `stage_fixed`); `just check` | **Machine** |
| 2 | No clippy warnings | `cargo clippy --workspace --all-targets -- -D warnings` (`just clippy`) | CI `rust-lint` job; `just check`; **not** any pre-push lane | **Machine** (CI + manual local) |
| 3 | No `unsafe` code | `#![deny(unsafe_code)]` / `#![forbid(unsafe_code)]` inner attributes, promoted to error by rule 2's `-D warnings` | Only in the 17 of 30 `crates/` directories that declare the attribute | **Machine, partial** — 13 crates unguarded |
| 4 | New public API has doc comments | `#![warn(missing_docs)]`, promoted to error by rule 2's `-D warnings` | Only in the 12 of 26 `crates/*/src/lib.rs` that declare it | **Machine, partial** — 14 crates unguarded, `buzz-cli` among them |
| 5 | No new `unwrap()` / `expect()` in production paths; use `?` and proper error types | *Nothing.* No `unwrap_used` / `expect_used` / `panic_used` lint is configured in any tracked file | — | **Review only** |
| 6 | `thiserror` for library error types, `anyhow` for binary/application error propagation | Nothing | — | **Review only** |
| 7 | `tracing` for all instrumentation, structured fields over string interpolation | Nothing | — | **Review only** |
| 8 | A clippy false positive is silenced with a targeted `#[allow(...)]` plus a comment, not by relaxing the global invocation | Nothing (rule 2 fails either way; only review distinguishes a justified `#[allow]` from an unjustified one) | — | **Review only** |
| 9 | Toolchain version | `rust-toolchain.toml` `channel = "1.95.0"`, applied by rustup on every cargo invocation | Everywhere cargo runs | **Machine** |
| 10 | Dependency licences and advisories | `cargo-deny check` against `deny.toml` | CI `security` job | **Machine** (dependency policy, not source style — see *Boundary*) |
| 11 | 1000-line file ceiling | `just file-size-check` — desktop, web and mobile checkers only | `desktop/src-tauri/src`, `desktop/src-tauri/crates`; **not** the root `crates/` tree | **Machine for `desktop/src-tauri`, absent for `crates/`** |

Five of the eleven rows are review-only or partial. That is the single most
useful fact in this node: a change that adds `unwrap()` to a relay handler,
or an undocumented public function to `buzz-cli`, passes every check this
repository runs.

## Configuration inventory

Every file that carries a Rust style or lint decision, and what is in it.

| File | What it decides | Authored or generated |
|---|---|---|
| `rust-toolchain.toml` | `[toolchain] channel = "1.95.0"`, `profile = "default"` | Authored (2 keys) |
| `Cargo.toml` `[workspace.package]` | `edition = "2021"`, `rust-version = "1.88.0"` | Authored |
| `Cargo.toml` `[workspace.dependencies]` | `thiserror = "2"`, `anyhow = "1"`, `tracing = "0.1"` — the crates rules 6 and 7 name | Authored |
| `.cargo/config.toml` | `[profile.dev] debug = "line-tables-only"`; `[env] CMAKE_POLICY_VERSION_MINIMUM = "3.5"`. **No `rustflags`** — it carries no lint policy | Authored |
| `deny.toml` | `[advisories]` ignore list (4 RUSTSEC ids), `[licenses]` allow list + `confidence-threshold = 0.8` + 7 `[[licenses.clarify]]` blocks, `[bans] multiple-versions = "warn"`, `wildcards = "allow"` | Authored |
| `Justfile` | `fmt`, `fmt-check`, `clippy`, `check`, `test-unit`, `file-size-check` recipes | Authored |
| `lefthook.yml` | Which lanes run at pre-commit and pre-push, and their globs | Authored |
| `.github/workflows/ci.yml` | `rust-lint` and `security` jobs and their path filters | Authored |
| `CONTRIBUTING.md` § Code Style | The prose rules — formatting, linting, no-unsafe, error handling, logging | Authored |
| `crates/*/src/lib.rs` line 1–2 | Per-crate `unsafe_code` and `missing_docs` attributes | Authored, per crate, inconsistently |

**Not present, and their absence is the decision:**

| Absent file | Consequence |
|---|---|
| `rustfmt.toml` / `.rustfmt.toml` | Formatting is rustfmt's own compiled-in defaults. The concrete style (line width, import grouping, brace placement) is **generated by the tool, not authored here** — this repository states no formatting preference of its own, and `CONTRIBUTING.md` says so explicitly: "rustfmt with default settings" |
| `clippy.toml` / `.clippy.toml` | The active lint set is clippy's default groups. No threshold, allow-list or deny-list is tuned |
| `[workspace.lints]` in any `Cargo.toml` | There is no manifest-level lint policy; every lint decision is an inner attribute in Rust source, which is why coverage is per-crate and uneven |

## Authored versus generated values

Rows in the tables above are one of three kinds, and conflating them is the
easiest way to misread this node:

- **Authored** — a literal written into a tracked file by a person. Every
  entry in the *Configuration inventory* table is authored, including the
  string `"1.95.0"` and the four RUSTSEC ids.
- **Generated by the tool, not this repository** — rustfmt's actual output
  style and clippy's actual lint set. Neither is enumerated anywhere in this
  tree; both come from the pinned toolchain's own defaults and would change
  if the pin moved. Do not cite this repository as the source of a specific
  formatting rule; cite rustfmt's defaults at the pinned version.
- **Measured at the recorded revision** — the counts (17 of 30, 12 of 26,
  10,039 lines, 388 files) are census results, not values anyone wrote down.
  They drift with every crate added, so re-run the census rather than quoting
  these numbers as policy.

## Where each check runs

| Stage | Rust checks that run | Rust checks that do **not** |
|---|---|---|
| lefthook **pre-commit** | `just fmt` on `crates/**` and `examples/countdown-bot/**`, auto-fixing and re-staging | clippy, tests |
| lefthook **pre-push** | `just test-unit`; `just desktop-tauri-clippy && just desktop-tauri-test` | **Workspace `just clippy`**; `just fmt-check` |
| CI `rust-lint` | `just fmt-check`, `just desktop-tauri-fmt-check`, `just clippy` | — |
| CI `security` | `cargo-deny check` | — |
| `just check` (manual) | `fmt-check`, `clippy`, plus the desktop/web/mobile and policy lanes | — |

The pre-push gap is worth stating plainly: **workspace clippy is a
CI-only gate.** A local push does not run it, so a clippy failure surfaces
after the push, not before it.

## Known drift between stated rules and current source

Four statements in the repository's own guidance do not match what the
source shows at the recorded revision. They are recorded here as findings,
not repaired — this node documents, it does not change the rules.

| Stated | Actual | Where stated |
|---|---|---|
| "All crates enforce `#![deny(unsafe_code)]`" | 13 of 30 crate directories carry no `unsafe_code` attribute; of the 17 that do, `buzz-agent` uses `forbid` and `buzz-dev-mcp` uses a platform-split `cfg_attr` pair (`forbid` off Windows, `deny` on it) | `CONTRIBUTING.md` § No Unsafe Code |
| `cargo clippy --all-targets --all-features -- -D warnings` | The recipe CI runs is `cargo clippy --workspace --all-targets -- -D warnings` — `--workspace`, and no `--all-features` | `CONTRIBUTING.md` § Linting vs `Justfile` |
| "New public API must have doc comments" | Enforced in 12 of 26 library crates; the other 14, including `buzz-cli`, have no `missing_docs` lint | root `AGENTS.md` § Quality Gates vs `crates/*/src/lib.rs` |
| Pre-push hooks run "clippy (workspace + Tauri)" | `lefthook.yml`'s pre-push stage runs `just desktop-tauri-clippy` only; no lane runs the workspace `just clippy` recipe | root `AGENTS.md` § Quality Gates vs `lefthook.yml` |

A fourth apparent conflict is not one: `CONTRIBUTING.md` says "Rust 1.88+"
and `[workspace.package].rust-version` is `1.88.0`, while
`rust-toolchain.toml` pins `1.95.0`. The first pair is the declared minimum
supported version; the second is the toolchain everyone actually runs. A
floor and a pin are different claims and both hold.

## Boundary

This node does not describe:

- **Dart or Flutter style** — `#854` owns `development/dart-style.md`.
- **TypeScript, Biome or the desktop/web lint surface** — `#870` owns
  `development/typescript-style.md`. Rule 11's file-size ceiling is named
  here only to mark that it stops at `desktop/src-tauri` and does not reach
  `crates/`; the TypeScript-side rules are that node's.
- **How to run the checks**, step by step. `just check`, `just fmt`,
  `just clippy` and `just ci` are named as the mechanisms that hold each
  rule, not walked through as a procedure. Build and test invocation is
  `corpus-development-build`'s subject; toolchain activation is
  `development-hermit`'s.
- **Dependency policy.** `deny.toml` appears in the tables because
  `cargo-deny check` is a Rust CI gate, but advisory ignores, licence
  allow-lists and version bans are a distinct subject from source style and
  would be a separate node.
- **Whether any rule is right.** Rules 5 through 8 being review-only is
  reported as a measured fact; whether they *should* be machine-enforced is
  a decision this node does not make and no accepted decision record
  currently settles.
- **Per-file or per-crate compliance audits.** The counts here are censuses
  of lint *declarations*, not of violations. No crate was checked for
  whether it actually contains `unwrap()` in a production path.

## Authoritative sources

If this node and any of these disagree, **they win** — this one has drifted.

| For | Read |
|---|---|
| Toolchain pin | `rust-toolchain.toml` |
| Edition, MSRV, shared dependency versions | `Cargo.toml` `[workspace.package]`, `[workspace.dependencies]` |
| The commands each rule is enforced by | `Justfile` (`fmt`, `fmt-check`, `clippy`, `check`) |
| When each check runs locally | `lefthook.yml` |
| When each check runs in CI | `.github/workflows/ci.yml` (`rust-lint`, `security` jobs) |
| The prose rules, including the review-only ones | `CONTRIBUTING.md` § Code Style |
| Agent-facing restatement of the same rules | root `AGENTS.md` § Quality Gates |
| Dependency advisory and licence policy | `deny.toml` |
| Per-crate lint attributes | `crates/<crate>/src/lib.rs`, lines 1–2 |
| Cargo profile and environment overrides | `.cargo/config.toml` |
| File-size rule roots | `desktop/scripts/check-file-sizes.mjs` |

## Relationships

Declared: `references` → `development-hermit`, `references` →
`corpus-development-build`. Both ids were confirmed present on
`origin/launchpad` with `git show origin/launchpad:launchpad/docs/corpus/development/hermit.md`
and `git show origin/launchpad:launchpad/docs/corpus/development/build.md`
before being declared, per `AGENTS.md` step 9.

- `development-hermit` — the pinned toolchain that supplies the `rustfmt`,
  `clippy-driver` and `cargo-deny` binaries every machine-enforced rule above
  runs through. Rule 9's `1.95.0` pin is only effective because Hermit and
  rustup resolve it.
- `corpus-development-build` — the `cargo build` / `Justfile` surface these
  checks share. That node owns build invocation; this one owns the style
  rules layered on it.

Not declared: `development-prerequisites` and `debugging`, both merged and
both checked. `development-prerequisites` covers what to install rather than
what the source must look like, and `debugging` covers fault investigation;
neither is supporting context a reader of this table needs, so no edge was
invented to fill the field.

## Scope and omissions

**This node covers** the Rust style rules in force at revision
`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`, the mechanism holding each one,
whether that mechanism is a tool or a reviewer, which configuration files
carry which decision, which configuration files are deliberately absent,
where each check runs in the commit/push/CI sequence, and the three places
where stated guidance and current source disagree.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Dart / Flutter style rules | `#854`, `development/dart-style.md` |
| TypeScript / Biome style rules | `#870`, `development/typescript-style.md` |
| Build and test invocation | `corpus-development-build` |
| Toolchain installation and activation | `development-hermit`, `development-prerequisites` |
| Dependency advisory / licence policy in `deny.toml` beyond naming its CI job | no corpus node at this revision |
| Whether rules 5–8 should be machine-enforced | undecided; no accepted decision record found |
| Actual `unwrap()` / `expect()` occurrences in production paths | not measured — see below |

**Expected but not verified when this node was written:**

- **No check was executed.** `just fmt-check`, `just clippy` and
  `cargo-deny check` were read from `Justfile`, `lefthook.yml` and
  `ci.yml`, not run. Every claim about what a command does rests on its
  written definition; that a green run actually follows was not observed.
- **Rule 5's real violation count is unknown.** Establishing whether
  `unwrap()` appears in production paths requires separating `#[cfg(test)]`
  modules and `tests/` targets from production code, which a text search
  cannot do reliably. Only the *absence of a lint* was verified, not the
  presence or absence of violations. The node states no compliance figure
  because it has none.
- **`desktop/src-tauri` was surveyed only for inner attributes and file-size
  roots.** It is a separate cargo workspace, excluded from the root
  `[workspace]` via `exclude = ["desktop/src-tauri"]`, and its own manifest
  was not opened; whether it declares lints the root workspace does not was
  not established.
- **The interaction between `-D warnings` and per-crate `warn` attributes was
  reasoned, not observed.** It is recorded as an `INFERENCE` at confidence
  0.9 rather than as a fact, because no run was performed that removed a doc
  comment and watched CI fail.
- **`launchpad/crates/knowledge`** is a workspace member outside `crates/`.
  Its `src/lib.rs` was checked and carries no inner lint attributes, but it
  is excluded from the 30-directory and 26-lib.rs censuses above, which are
  scoped to `crates/` exactly as stated.
