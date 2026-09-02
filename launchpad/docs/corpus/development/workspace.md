---
id: development-workspace
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The root Cargo.toml's [workspace] members array holds exactly 32 entries: 30 paths under crates/, plus launchpad/crates/knowledge, plus examples/countdown-bot."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "shell(awk '/^members = \\[/,/^\\]/' Cargo.toml | grep -c '^\\s*\"') -> 32"
      - "shell(awk '/^members = \\[/,/^\\]/' Cargo.toml | grep -c '^\\s*\"crates/') -> 30"
      - "shell(awk '/^members = \\[/,/^\\]/' Cargo.toml | grep '^\\s*\"' | grep -v '^\\s*\"crates/') -> \"launchpad/crates/knowledge\", \"examples/countdown-bot\""
  - statement: "The 30 crates/ member paths are exactly the 30 directories present under crates/, with no directory unlisted and no listed path absent."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "shell(diff <(ls -d crates/*/ | sed 's#/$##' | sort) <(awk '/^members = \\[/,/^\\]/' Cargo.toml | grep -o '\"crates/[^\"]*\"' | tr -d '\"' | sort)) -> no output, exit status 0"
  - statement: "The root [workspace] table sets exclude = [\"desktop/src-tauri\"] and resolver = \"2\" alongside its members array."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "The root [workspace.package] table declares five inheritable keys -- version = \"0.1.0\", edition = \"2021\", rust-version = \"1.88.0\", license = \"Apache-2.0\", repository = \"https://github.com/block/sprout\"."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "Inheritance from [workspace.package] is opt-in per key rather than automatic: 29 of the 30 manifests under crates/ carry version.workspace = true and 27 of the 30 carry edition.workspace = true, with crates/buzz-persona/Cargo.toml declaring version = \"0.1.0\" and edition = \"2021\" as literals instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/Cargo.toml"
      - "shell(grep -l 'version.workspace = true' crates/*/Cargo.toml | wc -l) -> 29; shell(grep -l 'edition.workspace = true' crates/*/Cargo.toml | wc -l) -> 27; shell(ls crates/*/Cargo.toml | wc -l) -> 30"
  - statement: "The root Cargo.toml carries a [workspace.dependencies] table that pins third-party versions and features centrally and additionally declares 14 internal crates as path dependencies, so a member writes serde = { workspace = true } rather than repeating a version."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "examples/countdown-bot/Cargo.toml"
      - "shell(awk '/^\\[workspace.dependencies\\]/,/^\\[profile/' Cargo.toml | grep -c 'path = \"crates/') -> 14"
  - statement: "launchpad/crates/knowledge/Cargo.toml inherits all five [workspace.package] keys (version, edition, rust-version, license, repository) with the .workspace = true form, whereas examples/countdown-bot/Cargo.toml declares version and edition as literals while still taking seven of its dependencies from [workspace.dependencies] with { workspace = true }."
    entry_class: FACT
    evidence:
      - "launchpad/crates/knowledge/Cargo.toml"
      - "examples/countdown-bot/Cargo.toml"
  - statement: "ADR-0045 is Accepted, records option B selected by a named human on 2026-08-27, and grants cohort Rust crates under launchpad/crates/ membership of the upstream root Cargo workspace via an append-only addition to the root Cargo.toml members list, leaving upstream's crates/ directory untouched."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md"
  - statement: "ADR-0045 names Cargo.lock, not the members line, as the divergence most likely to conflict on an upstream sync, because a lockfile conflict is resolved by regenerating rather than by reading; it also records that this is a recurring risk rather than a certainty, since git merges the lockfile cleanly when the changed segments do not overlap."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md"
  - statement: "launchpad/AGENTS.md's section 3 exception list carries the matching bullet naming the root Cargo.toml members list and Cargo.lock as a permitted upstream divergence, so the decision record and the governing instructions agree rather than diverging."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "desktop/src-tauri/Cargo.toml opens with its own [workspace] table declaring members = [\"crates/buzz-terminal\"], so desktop/src-tauri is a second Cargo workspace root rather than merely a standalone package excluded from the first."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The comment above that members line records that membership must not be inferred from the path-dependency edge, because with a bare [workspace] and no members, cargo test/check --workspace expands to a set that excludes the crate and its gates pass green-and-empty over a real defect."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The two Cargo workspaces resolve into two separate lockfiles: Cargo.lock at the repository root and desktop/src-tauri/Cargo.lock, of 11881 and 13945 lines respectively."
    entry_class: FACT
    evidence:
      - "Cargo.lock"
      - "desktop/src-tauri/Cargo.lock"
      - "shell(wc -l Cargo.lock desktop/src-tauri/Cargo.lock) -> 11881 Cargo.lock, 13945 desktop/src-tauri/Cargo.lock"
  - statement: "desktop/src-tauri/Cargo.toml depends on seven root-workspace crates by relative path -- buzz-core, buzz-persona, buzz-sdk, buzz-agent, buzz-voice, buzz-ws-client and buzz-media, each under ../../crates/ -- so the source dependency edge crosses the workspace boundary even though membership does not."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The string buzz-terminal does not appear anywhere in the root Cargo.toml, so the Tauri workspace's own member is reachable only through the desktop/src-tauri manifest."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "shell(grep -c 'buzz-terminal' Cargo.toml) -> 0"
  - statement: "Upstream's AGENTS.md records as gotcha 5 that the desktop crate is excluded from the root workspace, that cargo test at the repository root does NOT run desktop tests, and that cargo test --manifest-path desktop/src-tauri/Cargo.toml is required instead."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "CLAUDE.md"
  - statement: "ADR-0045 independently states that desktop/src-tauri is excluded from the root workspace and therefore not covered by a root cargo test, and contrasts that hazard with cohort crates, which stay inside the root workspace so root cargo commands do reach them."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md"
  - statement: "The Justfile crosses the Cargo workspace boundary explicitly in every recipe that must reach the Tauri project: desktop-tauri-clippy and desktop-tauri-check pass --manifest-path desktop/src-tauri/Cargo.toml, desktop-tauri-test runs cd desktop/src-tauri && cargo test --workspace, and the clean recipe runs cargo clean once for the root workspace and again with --manifest-path for the Tauri project."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "A Justfile comment inside the unit-test recipe reads verbatim 'nothing in CI runs `cargo test --workspace` -- workspace membership alone buys clippy/check, not a single executed test', which is why individual packages are enumerated with cargo nextest run -p."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "pnpm-workspace.yaml lists exactly three packages -- desktop, web and admin-web -- and additionally carries allowBuilds, overrides and patchedDependencies keys that apply across those packages."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
  - statement: "Exactly one pnpm lockfile exists in the repository, pnpm-lock.yaml at the root, and no package-lock.json or yarn.lock exists at any depth up to three directories."
    entry_class: FACT
    evidence:
      - "pnpm-lock.yaml"
      - "shell(find . -name pnpm-lock.yaml -not -path '*/node_modules/*') -> ./pnpm-lock.yaml; shell(find . -maxdepth 3 \\( -name package-lock.json -o -name yarn.lock \\) -not -path '*/node_modules/*') -> no output"
  - statement: "The root package.json is itself the workspace root package: name buzz-workspace, private true, packageManager pnpm@11.4.0, with a single check script defined as pnpm -r check that recurses into the member packages."
    entry_class: FACT
    evidence:
      - "package.json"
  - statement: "The three pnpm member packages are named buzz (desktop/), buzz-web (web/) and buzz-admin-web (admin-web/), and all three are marked private."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "web/package.json"
      - "admin-web/package.json"
  - statement: "None of the three pnpm member packages declares a dependency on another using pnpm's workspace: protocol, so they share the workspace for a single install, a single lockfile and shared tooling rather than for cross-package imports."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "web/package.json"
      - "admin-web/package.json"
      - "shell(grep -n 'workspace:' desktop/package.json web/package.json admin-web/package.json) -> no matches"
  - statement: "mobile/ belongs to neither workspace: it carries pubspec.yaml (name buzz, publish_to 'none', Dart SDK constraint ^3.11.4) and its own pubspec.lock, and contains no package.json and no Cargo.toml."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
      - "mobile/pubspec.lock"
      - "shell(ls mobile/package.json mobile/Cargo.toml) -> No such file or directory for both"
  - statement: "rust-toolchain.toml pins the toolchain channel to 1.95.0 with profile default, which is a different value from the 1.88.0 that [workspace.package] declares as rust-version."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
      - "Cargo.toml"
  - statement: "Membership in the root workspace buys a member reachability from root-level cargo --workspace commands, entry in the single root lockfile, and the option to inherit shared package keys and dependency pins -- but not test execution, because the Justfile enumerates packages individually and records that no CI lane runs cargo test --workspace."
    entry_class: INFERENCE
    evidence:
      - "Cargo.toml"
      - "Justfile"
    confidence: 0.85
  - statement: "Because the root workspace and the Tauri workspace resolve independently, a dependency common to both can in principle lock to different versions in the two lockfiles; the two versions sampled here agree, so the divergence is a structural possibility rather than an observed condition at this revision."
    entry_class: INFERENCE
    evidence:
      - "Cargo.lock"
      - "desktop/src-tauri/Cargo.lock"
      - "shell(grep -A1 '^name = \"tokio\"$' Cargo.lock) -> version = \"1.52.3\"; shell(grep -A1 '^name = \"tokio\"$' desktop/src-tauri/Cargo.lock) -> version = \"1.52.3\"; same command for axum -> 0.8.9 in both"
    confidence: 0.7
  - statement: "Issue #871's definition of done requires that the document be structured for lookup rather than narrative teaching, contain only facts supported by current source, label generated versus authored values, define its scope and omissions, and link authoritative source, schema and configuration."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#871 definition of done"
  - statement: "Issue #871's definition of done requires that the node represent one independently maintainable knowledge node, and that any newly discovered second concept be filed as a separate task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#871 definition of done"
relationships:
  - type: references
    target: corpus-development-build
  - type: references
    target: corpus-template-reference
---

# Workspace structure: reference

Buzz's repository is not one build unit. It is **three**, and they do not nest: a
Cargo workspace rooted at the repository root, a pnpm workspace rooted at the same
directory, and a Flutter/pub package under `mobile/` that belongs to neither. A
fourth unit sits inside the first's directory tree but outside its membership — the
Tauri project under `desktop/src-tauri`, which is a Cargo workspace root of its own.

This node catalogues those units: which paths each one claims, what a member gets
from belonging, and where a command aimed at one unit silently fails to reach
another. It is the lookup surface behind the single most consequential build fact in
this repository — that `cargo test` at the root does not run the desktop tests.

**Scope boundary, stated up front.** This node describes *how the build tooling
groups the tree*. It does not describe *what lives where* (a repository-layout node,
issue #863, owns that and is not merged on `origin/launchpad` at this revision), and
it does not describe *how to compile anything* (`development/build.md`, merged, owns
compile commands, their flags, their exit codes and their failure modes). See
*Boundary* below for the full split.

## The four build units

| Unit | Root manifest | Tool | Lockfile | Claims |
|---|---|---|---|---|
| Root Cargo workspace | `Cargo.toml` | cargo | `Cargo.lock` | 32 member paths (see below) |
| Tauri Cargo workspace | `desktop/src-tauri/Cargo.toml` | cargo | `desktop/src-tauri/Cargo.lock` | itself (`buzz-desktop`) + `crates/buzz-terminal` |
| pnpm workspace | `pnpm-workspace.yaml` + `package.json` | pnpm | `pnpm-lock.yaml` | `desktop`, `web`, `admin-web` |
| Flutter package | `mobile/pubspec.yaml` | flutter / pub | `mobile/pubspec.lock` | `mobile/` only |

`desktop/` appears in two rows and that is not a mistake: the directory holds a
pnpm package (the React frontend) *and* a Cargo project (the Tauri backend), each
belonging to a different workspace.

## Root Cargo workspace

### Membership

`Cargo.toml`'s `[workspace]` table declares an explicit `members` array — no globs,
so every member is spelled out and adding a crate is an edit to this file.

**The array holds 32 entries at the recorded revision.** Authored count, produced by
running the command rather than read from any document:

```bash
awk '/^members = \[/,/^\]/' Cargo.toml | grep -c '^\s*"'        # -> 32
awk '/^members = \[/,/^\]/' Cargo.toml | grep -c '^\s*"crates/' # -> 30
```

| Group | Count | Paths |
|---|---|---|
| Under `crates/` | 30 | `crates/buzz-relay`, `crates/buzz-core`, `crates/buzz-conformance`, `crates/buzz-push-gateway`, `crates/buzz-db`, `crates/buzz-pubsub`, `crates/buzz-auth`, `crates/buzz-search`, `crates/buzz-audit`, `crates/buzz-acp`, `crates/buzz-agent`, `crates/sprig`, `crates/buzz-test-client`, `crates/buzz-ws-client`, `crates/buzz-admin`, `crates/buzz-deletion`, `crates/buzz-workflow`, `crates/buzz-media`, `crates/buzz-cli`, `crates/buzz-pairing-cli`, `crates/buzz-sdk`, `crates/buzz-persona`, `crates/git-credential-nostr`, `crates/git-sign-nostr`, `crates/buzz-pair-relay`, `crates/buzz-relay-mesh`, `crates/buzz-dev-mcp`, `crates/buzz-voice`, `crates/buzz-backend-kubernetes`, `crates/buzz-datastore-tracing` |
| Cohort crate | 1 | `launchpad/crates/knowledge` |
| Example | 1 | `examples/countdown-bot` |

The `crates/` member list and the `crates/` directory listing are **identical sets** —
`diff` between the two produces no output. So at this revision "a directory under
`crates/`" and "a root workspace member under `crates/`" mean the same thing. That is
a property of the current file, not a rule the tooling enforces; a new directory
under `crates/` is not a member until someone adds the line.

> **Do not carry a member count over from another document.** Counts here are
> reproduced by the commands shown above, at the revision in the ledger. A merged
> sibling node states a different, smaller figure; that discrepancy is tracked
> separately and is not restated or corrected here.

### What the workspace shares

**`[workspace.package]` — inheritable package metadata.** Five keys:

| Key | Value |
|---|---|
| `version` | `0.1.0` |
| `edition` | `2021` |
| `rust-version` | `1.88.0` |
| `license` | `Apache-2.0` |
| `repository` | `https://github.com/block/sprout` |

Inheritance is **opt-in per key**, not automatic. A member takes a value by writing
`version.workspace = true`; a member that writes a literal keeps the literal. Uptake
across the 30 `crates/` manifests is uneven and deliberately observable:

| Key | Members inheriting | Exception |
|---|---|---|
| `version` | 29 of 30 | `crates/buzz-persona` declares `version = "0.1.0"` literally |
| `edition` | 27 of 30 | — |

`launchpad/crates/knowledge` inherits all five keys. `examples/countdown-bot`
inherits none of them — it declares `version = "0.1.0"` and `edition = "2021"`
literally, plus `publish = false` — while still drawing seven dependencies from the
workspace. The two forms of sharing are independent.

**`[workspace.dependencies]` — centralized version and feature pinning.** Members
write `tokio = { workspace = true }` and inherit both the version and the feature
set chosen once at the root. The table also declares **14 internal crates as path
dependencies** (`buzz-core = { path = "crates/buzz-core" }` and similar), so a
member depends on a sibling through the same `{ workspace = true }` form rather than
by spelling a relative path.

**One lockfile.** `Cargo.lock` at the repository root covers all 32 members. There is
no second lockfile inside the root workspace.

### The cohort member

`launchpad/crates/knowledge` is the one member outside both `crates/` and
`examples/`. It is there by decision, not by drift: **ADR-0045** (Accepted,
option B, selected by a named human on 2026-08-27) places cohort-authored Rust
crates under `launchpad/crates/` and registers them in the upstream root
`Cargo.toml` `members` list by append-only addition, leaving upstream's `crates/`
directory untouched. `launchpad/AGENTS.md` §3 carries the matching exception bullet,
so the decision record and the governing instructions agree.

ADR-0045 also names the real cost, and it is not the members line: **`Cargo.lock` is
the divergence most likely to conflict on an upstream sync**, because a lockfile
conflict is resolved by regenerating rather than by reading. The record is careful to
call that a recurring risk rather than a certainty — git merges the lockfile cleanly
whenever the changed segments do not overlap.

Membership is the whole point of option B: cohort crates stay inside the root
workspace, so root `cargo` commands reach them. ADR-0045 draws that contrast against
`desktop/src-tauri` explicitly.

### What membership does and does not buy

| Membership grants | Membership does not grant |
|---|---|
| Reachability from root `cargo --workspace` commands | Test execution |
| An entry in the single root `Cargo.lock` | Automatic inheritance of `[workspace.package]` keys (opt-in per key) |
| The option to inherit shared dependency pins | Anything in the Tauri workspace or the pnpm workspace |

The test row is the one that surprises people, and the `Justfile` says so in its own
words: *"nothing in CI runs `cargo test --workspace` — workspace membership alone
buys clippy/check, not a single executed test."* That is why the unit-test recipe
enumerates packages one at a time with `cargo nextest run -p <package>`. Adding a
crate to `members` therefore puts it under lint and type-check coverage automatically
and under test coverage not at all — the enumeration is a separate, manual edit.

## The Tauri Cargo workspace

`desktop/src-tauri` is **excluded from the root workspace and is a workspace root of
its own**. Both halves are declared explicitly:

| Where | Declaration |
|---|---|
| `Cargo.toml` (root) | `exclude = ["desktop/src-tauri"]` |
| `desktop/src-tauri/Cargo.toml` | `[workspace]` with `members = ["crates/buzz-terminal"]` |

The second declaration carries a comment recording why `members` is spelled out
rather than left bare: with a bare `[workspace]` and no `members`, `cargo
test/check --workspace` expands to a set that **excludes the crate**, and its gates
then pass green-and-empty over a real defect. The explicit list is a guard against a
silently empty test set.

**Two edges cross the boundary in opposite directions, and only one of them is a
membership edge.**

- *Source depends across the line.* `desktop/src-tauri/Cargo.toml` declares seven
  root-workspace crates as relative path dependencies — `buzz-core`,
  `buzz-persona`, `buzz-sdk`, `buzz-agent`, `buzz-voice`, `buzz-ws-client`,
  `buzz-media`, each under `../../crates/`. The Tauri backend compiles root
  workspace source.
- *Membership does not.* `buzz-terminal` appears **zero times** in the root
  `Cargo.toml`. The Tauri workspace's own member is reachable only through the
  `desktop/src-tauri` manifest.

**Two lockfiles follow from two workspace roots**: `Cargo.lock` (11,881 lines) and
`desktop/src-tauri/Cargo.lock` (13,945 lines), resolved independently. Two shared
dependencies were sampled at this revision — `tokio` and `axum` — and both agree
across the two files (`1.52.3` and `0.8.9`). Divergence is therefore a structural
possibility of the two-lockfile shape, not an observed condition here.

### Crossing the boundary in commands

Every recipe that must reach the Tauri project says so explicitly. These are listed
as evidence of *where the boundary sits*; `development/build.md` owns what the build
commands do.

| `Justfile` recipe | How it crosses |
|---|---|
| `desktop-tauri-clippy` | `cargo clippy --manifest-path desktop/src-tauri/Cargo.toml --workspace ...` |
| `desktop-tauri-check` | `cargo check --manifest-path desktop/src-tauri/Cargo.toml` |
| `desktop-tauri-test` | `cd desktop/src-tauri && cargo test --workspace` |
| `clean` | `cargo clean` for the root workspace, then `cargo clean --manifest-path desktop/src-tauri/Cargo.toml` |

Note the `--workspace` flag in the clippy and test rows: it is meaningful there
precisely because `desktop/src-tauri` **is** a workspace, so the flag expands to the
Tauri package plus `buzz-terminal`.

**The consequence, stated once.** `cargo test` at the repository root does not run
the desktop tests. Upstream's `AGENTS.md` records this as gotcha 5 and gives the
remedy — `cargo test --manifest-path desktop/src-tauri/Cargo.toml` — and ADR-0045
independently states the same exclusion when contrasting it against cohort crates.
Two authoritative sources, agreeing.

## The pnpm workspace

`pnpm-workspace.yaml` claims **three** packages:

| Path | `name` | Private |
|---|---|---|
| `desktop` | `buzz` | yes |
| `web` | `buzz-web` | yes |
| `admin-web` | `buzz-admin-web` | yes |

The root `package.json` is itself the workspace root package — `name:
buzz-workspace`, `private: true`, `packageManager: pnpm@11.4.0` — and defines a
single script, `check`, as `pnpm -r check`, which recurses into the members.

**One lockfile, at the root.** `pnpm-lock.yaml` is the only lockfile of its kind in
the repository; no `package-lock.json` and no `yarn.lock` exists. The workspace
therefore resolves all three packages' dependencies together.

`pnpm-workspace.yaml` also carries three cross-cutting keys that apply across the
whole workspace rather than to one package: `allowBuilds`, `overrides` (forcing
single copies of specific transitive packages) and `patchedDependencies`. Those
values are the reason the workspace matters beyond convenience — a version override
declared here binds every member.

**These packages do not import each other.** None of the three declares a dependency
on another using pnpm's `workspace:` protocol. They share the workspace for one
install, one lockfile and shared tooling — not for cross-package source imports.

## `mobile/` — neither workspace

`mobile/` is a Flutter/pub package and is claimed by no Cargo or pnpm workspace:

| Signal | Value |
|---|---|
| `mobile/pubspec.yaml` | present — `name: buzz`, `publish_to: 'none'`, Dart SDK `^3.11.4` |
| `mobile/pubspec.lock` | present — its own resolution, independent of both other lockfiles |
| `mobile/package.json` | absent |
| `mobile/Cargo.toml` | absent |
| Listed in `pnpm-workspace.yaml` | no |
| Listed in root `Cargo.toml` `members` | no |

So neither a root `cargo` command nor a root `pnpm -r` command reaches `mobile/`
under any flag. It is reached only by the Flutter toolchain, invoked against that
directory.

## Toolchain values

Two version numbers describe the Rust workspace and they are not the same number:

| File | Key | Value |
|---|---|---|
| `Cargo.toml` `[workspace.package]` | `rust-version` | `1.88.0` |
| `rust-toolchain.toml` | `channel` | `1.95.0` |

Both are recorded here as observed values. Reconciling them — whether the gap is a
deliberate minimum-supported-version floor beneath a newer pinned toolchain, or
drift — is not established by this node; see *Expected but not verified*.
Toolchain provisioning itself is `development/hermit.md`'s subject.

## Generated versus authored

| Value | Authored or generated | By what |
|---|---|---|
| `Cargo.toml` `members`, `exclude`, `[workspace.package]`, `[workspace.dependencies]` | **Authored** | hand-edited; membership is an explicit list with no globs |
| `desktop/src-tauri/Cargo.toml` `[workspace] members` | **Authored** | hand-edited, deliberately explicit per its own comment |
| `pnpm-workspace.yaml` `packages`, `overrides`, `patchedDependencies` | **Authored** | hand-edited |
| `mobile/pubspec.yaml` | **Authored** | hand-edited |
| `Cargo.lock` | **Generated** | cargo, from the root workspace's manifests |
| `desktop/src-tauri/Cargo.lock` | **Generated** | cargo, from the Tauri workspace's manifests |
| `pnpm-lock.yaml` | **Generated** | pnpm, from the three member `package.json` files |
| `mobile/pubspec.lock` | **Generated** | pub, from `mobile/pubspec.yaml` |
| Every count and set comparison in this node | **Generated by the author's commands**, transcribed | the `awk`/`grep`/`diff`/`wc` invocations recorded in the ledger |

The last row is the one to read carefully: the counts above are not copied from any
document. Each was produced by running the command shown next to it, at the revision
in the ledger, and each is re-runnable.

## Boundary

This node does not describe:

- **How to compile anything.** `cargo build --workspace`, its release variant, the
  frontend builds, their exit codes, their observed failure modes and their timings
  belong to `development/build.md` (`corpus-development-build`), which is merged.
  This node names workspace-crossing commands only as evidence of *where a boundary
  sits*, never as build instructions.
- **What lives in which directory, and why the crate boundaries fall where they
  do.** That is repository layout — issue #863's node, which is **not present on
  `origin/launchpad`** at this revision. Layout answers "where is the media code";
  this node answers "which build unit claims that path". The two questions have
  different answers for `desktop/`, which is why the split is worth stating.
- **Toolchain installation and version management.** `development/hermit.md` owns
  Hermit and the pinned toolchain; `development/prerequisites.md` owns what must be
  installed first.
- **Why the topology is the way it is.** The rationale for excluding
  `desktop/src-tauri`, or for the crate decomposition, is explanation rather than
  reference; ADR-0045 covers only the cohort-crate half of it. No concept node for
  workspace topology exists at this revision.
- **CI job structure and which lane runs which package.** The `Justfile` comment
  about `cargo test --workspace` is cited here for what it establishes about
  membership; the shape of the CI pipeline itself is not this node's subject.

## Relationships

Declared, both verified present on `origin/launchpad` with `git show
origin/launchpad:<path>` before being written:

- `references` → `corpus-development-build` — the merged node that owns compiling.
  Per `relationships.schema.json`, `references` implies supporting context with no
  ownership or currency dependency, which is the correct strength: this node's
  structural facts stay true regardless of what happens to that node's build
  commands.
- `references` → `corpus-template-reference` — the template this node's body shape
  follows.

Not declared, and why:

- **No edge to a repository-layout node.** It is not on `origin/launchpad` at this
  revision, and `AGENTS.md` is explicit that a target must resolve on the branch
  being merged into, not on the author's own branch. A target that resolves locally
  and not in CI is a hard validation error there.
- **No edge to `development-hermit`, `development-prerequisites` or `debugging`.**
  All three are merged and would resolve, but each is a neighbouring *procedure*
  rather than context this reference material rests on; naming them here would
  assert a relationship the content does not have.

## Scope and omissions

**This node covers** the four build units the repository is divided into; the root
Cargo workspace's membership list and the commands that reproduce its counts; what
`[workspace.package]` and `[workspace.dependencies]` share and how opt-in
inheritance actually behaves across members; the cohort member and the decision that
authorizes it; `desktop/src-tauri` as a second workspace root, its two lockfiles and
the direction of the edges that cross its boundary; the pnpm workspace's three
packages and single lockfile; `mobile/` as a unit neither workspace claims; and
which values in all of that are authored versus generated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Compiling the workspace, build flags, exit codes, failure modes | `development/build.md` (`corpus-development-build`) |
| What lives where in the tree, and the crate decomposition | Repository layout, issue #863 — not on `origin/launchpad` at this revision |
| Toolchain installation and pinning mechanics | `development/hermit.md` (`development-hermit`) |
| Prerequisites that must exist before any of this works | `development/prerequisites.md` (`development-prerequisites`) |
| Why the topology was chosen (explanation, not reference) | No concept node exists for this at this revision; ADR-0045 covers the cohort-crate half only |
| The front-matter contract this node's own metadata obeys | `launchpad/docs/corpus/schema/node.schema.json` |

**Expected but not verified when this node was written:**

- **`cargo metadata` was not run.** It would have been the tool's own authoritative
  enumeration of workspace members, cross-checking the manifest counts from a second
  direction. It failed to produce output in this environment (cargo was not
  resolvable without an activated Hermit shell), so every count here rests on reading
  and counting the manifest text rather than on cargo's own resolution. The two
  methods agree only if the manifest is well-formed, which was not independently
  confirmed.
- **No cargo, pnpm or flutter command was executed to observe the boundaries in
  action.** The claim that a root `cargo test` misses the desktop tests rests on two
  documentary sources (upstream `AGENTS.md` gotcha 5 and ADR-0045) plus the two
  manifest declarations — not on a run that demonstrated an empty test set.
- **Only two shared dependencies were sampled across the two Cargo lockfiles.**
  `tokio` and `axum` agree; the remaining shared graph was not audited, so no claim
  is made about whether the two lockfiles agree in general.
- **The `rust-version` 1.88.0 versus `rust-toolchain.toml` 1.95.0 gap was not
  resolved.** Both values are reported as read. Whether the difference is an
  intentional MSRV floor or drift was not established, and no source was found in
  this pass that states the intent.
- **Whether every `crates/` directory is *required* to be a member** was not
  established. The two sets are identical at this revision, which is an observation
  about the current file, not evidence of an enforced rule; no check was found that
  would fail if a new directory were added without a `members` line.
