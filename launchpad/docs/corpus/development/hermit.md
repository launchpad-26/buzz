---
id: development-hermit
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "This repository uses Hermit (cashapp/hermit) to pin toolchain versions in bin/; it is activated once per shell with `. ./bin/activate-hermit`, each pinned tool is downloaded on first invocation and cached thereafter, and `just bootstrap` (which `just setup` calls automatically) can pre-download every pinned tool upfront instead of waiting for lazy per-tool downloads."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "AGENTS.md"
  - statement: "Using Hermit is optional but recommended: CONTRIBUTING.md's First-Time Setup labels the activation step '(optional but recommended)' and states that a contributor who does not use it must instead ensure their own toolchain meets the minimum versions listed in its prerequisites table by hand."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "Root AGENTS.md instructs agents specifically to activate the Hermit environment before running Git or hooks, and explicitly forbids rewriting hook commands to compensate for an unconfigured shell PATH instead."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "launchpad/AGENTS.md separately instructs activating Hermit before any git command performed within that subtree, stating that hooks otherwise fail on PATH."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/docs/corpus/AGENTS.md states that `just corpus-validate` needs the Hermit environment activated first (`. ./bin/activate-hermit`), while running `python3 launchpad/project-intelligence/corpus/validate.py` directly does not."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "bin/README.hermit.md states that the bin/ directory's contents are Hermit-managed symlinks which automatically download and install Hermit itself plus its packages, local to this environment."
    entry_class: FACT
    evidence:
      - "bin/README.hermit.md"
  - statement: "At the recorded revision, bin/ pins exactly ten tools, each via its own `.<tool>-<version>.pkg` marker file: biome 2.4.7, cargo-deny 0.19.0, cmake 4.3.1, flutter 3.41.7, just 1.46.0, lefthook 2.1.10, node 24.15.0, pgschema 1.7.4, pnpm 11.4.0, and rustup 1.28.2."
    entry_class: FACT
    evidence:
      - "bin/.biome-2.4.7.pkg"
      - "bin/.cargo-deny-0.19.0.pkg"
      - "bin/.cmake-4.3.1.pkg"
      - "bin/.flutter-3.41.7.pkg"
      - "bin/.just-1.46.0.pkg"
      - "bin/.lefthook-2.1.10.pkg"
      - "bin/.node-24.15.0.pkg"
      - "bin/.pgschema-1.7.4.pkg"
      - "bin/.pnpm-11.4.0.pkg"
      - "bin/.rustup-1.28.2.pkg"
  - statement: "Each of the ten `.<tool>-<version>.pkg` marker files in bin/ is itself a symlink whose target is the literal string 'hermit', and every command name a developer actually invokes (for example cargo, rustc, node, pnpm, just, lefthook, cmake, flutter, dart, biome, pgschema, plus several rust-toolchain aliases such as clippy-driver, rust-analyzer, rustfmt and rustdoc) is a symlink pointing at one of those marker files -- so invoking any pinned tool resolves, through one or two symlink hops, to the single bin/hermit executable, which is the one real (non-symlink, mode 100755) generated script in the directory. `git ls-tree HEAD bin/` shows the mode-120000 (symlink) entries and which ones share a blob hash; `git cat-file -p` on each distinct hash was used to read the actual target strings."
    entry_class: FACT
    evidence:
      - "bin/hermit"
      - "bin/cargo"
      - "bin/rustc"
      - "bin/node"
      - "bin/pnpm"
      - "bin/just"
      - "bin/lefthook"
      - "bin/cmake"
      - "bin/flutter"
      - "bin/biome"
      - "bin/pgschema"
      - "bin/.rustup-1.28.2.pkg"
      - "bin/.node-24.15.0.pkg"
      - "bin/.lefthook-2.1.10.pkg"
  - statement: "bin/activate-hermit is a generated file (marked 'THIS FILE IS GENERATED; DO NOT MODIFY') that must be sourced, not executed directly -- run as `$0` it exits with status 33 and an error telling the caller to source it instead. Sourced, it runs `hermit noop` as a readiness check, then `eval`s the output of `hermit activate <bin-dir>/..` to modify the calling shell's environment, runs `hash -r` under bash/zsh to clear the shell's command-path cache, and finally prints a confirmation message built from `hermit env HERMIT_ENV`."
    entry_class: FACT
    evidence:
      - "bin/activate-hermit"
  - statement: "bin/hermit.hcl, the per-repository Hermit configuration file, sets exactly one option: `manage-git = true`."
    entry_class: FACT
    evidence:
      - "bin/hermit.hcl"
  - statement: "ADR-0017 (accepted 2026-08-18) documents that bin/lefthook and bin/.lefthook-*.pkg are pinned to lefthook 2.1.10 -- newer than upstream's pin -- because lefthook 2.1.3's `@{push}`-unavailable fallback crashes every pre-push command on this fork's first push, since the fork's default branch is named `launchpad` and collides with the top-level `launchpad/` directory; the ADR states this is a standing, not temporary, divergence from upstream, bounded to those two files."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md"
  - statement: "launchpad/AGENTS.md lists the Hermit lefthook pin as one of its named deliberate exceptions to the 'never move or rename upstream files' rule, scoped exactly to bin/lefthook and bin/.lefthook-*.pkg, and cites ADR-0017 for the reasoning."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "`.github/workflows/ci.yml` activates Hermit in most jobs via the pinned third-party action `cashapp/activate-hermit@cea9af7913204a965fd488637a8d1811bba2e616` (tagged v1 at that SHA), used as a step immediately after checkout in the great majority of the workflow's jobs (rust checks, desktop, web, mobile/Flutter, integration tests, dependency policy, and more)."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "One CI job in `.github/workflows/ci.yml` -- a dedicated Windows Rust job with env `TARGET: x86_64-pc-windows-msvc` -- runs on a real Windows runner and does not include the `cashapp/activate-hermit` step; an inline comment there states that MSVC needs windows.h (for crates such as aws-lc-sys) and that Hermit, used by the Linux jobs, does not provide MSVC, so that job instead relies on the runner's preinstalled rustup honoring the repo-root `rust-toolchain.toml`."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "`.github/workflows/ci.yml`'s mobile/Flutter job computes a cache key by hashing every file under `./bin` with `openssl sha256`, then restores and, on a cache miss, saves `~/.cache/hermit/pkg` under that key -- caching Hermit's own downloaded package store across CI runs instead of re-downloading every pinned tool on every run."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The repository's Justfile contains no reference to Hermit anywhere in its text; `just` recipes rely on the shell PATH that `. ./bin/activate-hermit` establishes rather than invoking `hermit` directly, which is consistent with root AGENTS.md's instruction to activate Hermit before running hooks rather than rewriting hook commands to compensate for an unconfigured PATH."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "AGENTS.md"
  - statement: "The two-hop symlink chain (tool name -> version-pinned marker file -> hermit) most likely exists so that the single generated `bin/hermit` binary can inspect the path or name it was invoked as (its argv[0]) to determine which tool and version to lazily fetch and exec on first use, matching CONTRIBUTING.md's description of each pinned tool being 'fetched once on first invocation and cached thereafter.' No Hermit source or design document was opened to confirm this mechanism directly; it is reasoned from the observed file structure and the documented lazy-download behavior."
    entry_class: INFERENCE
    evidence:
      - "bin/hermit"
      - "bin/cargo"
      - "bin/.rustup-1.28.2.pkg"
      - "CONTRIBUTING.md"
    confidence: 0.7
  - statement: "Issue #859 requires this node to be the single canonical hand-authored reference document at launchpad/docs/corpus/development/hermit.md: structured for lookup rather than narrative teaching, containing only facts supported by current source with generated-versus-authored values labeled, defining its own scope and omissions, and linking authoritative source/schema/config rather than duplicating it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#859 definition of done"
  - statement: "Issue #859's stated parent PRD is #619 ('feature: development release and governance corpus exists'), and its 'Out of scope' section excludes creating or materially editing a second hand-authored canonical corpus document, changing runtime product behavior, deciding unresolved ADR outcomes, and broad 'while here' documentation cleanup."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#859"
  - statement: "No #626-shaped manifest row or #627-shaped planned-issue record could be resolved for this task before drafting: launchpad/project-intelligence/corpus/manifest.py and issue_plan.py are both library-only modules with no CLI and no persisted ledger file anywhere in this repository, and issue #859's own body (marked `corpus-plan:v2` in an HTML comment) uses an Objective/Definition-of-done/Impacted-components/Out-of-scope shape rather than the Template/Audiences/Source-start-points shape that issue_plan.py's `plan_from_manifest` actually generates -- confirming the tool that produced this issue's body is not the version checked into this repository. This node's front matter and body were therefore authored directly against node.schema.json and the already-merged `reference` template (launchpad/docs/corpus/templates/reference.md, id corpus-template-reference), using issue #859's own Objective and Definition of Done as the task specification in place of a manifest row."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "investigation of launchpad/project-intelligence/corpus/manifest.py, issue_plan.py, and launchpad-26/buzz#859's body, performed while authoring this node"
---

# Hermit: reference

This node catalogues how [Hermit](https://cashapp.github.io/hermit/) pins and serves
this repository's development toolchain (Rust, Node, pnpm, Flutter, `just`,
`lefthook`, `cmake`, `biome`, `cargo-deny`, `pgschema`) from the `bin/` directory:
what is pinned and at which version, the symlink mechanism that makes a pinned
command resolve to a lazily-downloaded tool, where activation is required versus
optional, and how CI and this fork's own upstream-boundary exception relate to it.
It is linked from `AGENTS.md`, `CONTRIBUTING.md`, `launchpad/AGENTS.md` and
`launchpad/docs/corpus/AGENTS.md`, all of which instruct activating Hermit before
various tasks without themselves cataloguing what Hermit pins or how the pin
mechanism works.

## Pinned toolchain

Hermit pins each tool via a two-hop symlink chain: the command name a developer
types (`cargo`, `node`, `just`, ...) is a symlink to a version-specific marker file
(`.rustup-1.28.2.pkg`, `.node-24.15.0.pkg`, ...), and every marker file is itself a
symlink whose target is the literal string `hermit` -- so every pinned command
ultimately resolves to the single generated `bin/hermit` executable, which is the
only non-symlink entry among them. `bin/hermit.hcl` sets one repository-level
option, `manage-git = true`.

| Pinned tool(s) | Version | Marker file | Notes |
|---|---|---|---|
| `cargo`, `cargo-clippy`, `cargo-fmt`, `cargo-miri`, `clippy-driver`, `rls`, `rust-analyzer`, `rust-gdb`, `rust-gdbgui`, `rust-lldb`, `rustc`, `rustdoc`, `rustfmt`, `rustup` | 1.28.2 (rustup) | `.rustup-1.28.2.pkg` | Rust toolchain, dispatched through rustup |
| `biome` | 2.4.7 | `.biome-2.4.7.pkg` | Desktop/web JS/TS lint and format |
| `cargo-deny` | 0.19.0 | `.cargo-deny-0.19.0.pkg` | Dependency policy check |
| `ccmake`, `cmake`, `cmake-gui`, `cpack`, `ctest` | 4.3.1 | `.cmake-4.3.1.pkg` | Native build tooling |
| `dart`, `flutter` | 3.41.7 | `.flutter-3.41.7.pkg` | Mobile app toolchain |
| `just` | 1.46.0 | `.just-1.46.0.pkg` | Task runner |
| `lefthook` | 2.1.10 | `.lefthook-2.1.10.pkg` | Git hooks; pinned ahead of upstream -- see *Fork divergence* below |
| `corepack`, `node`, `npm`, `npx` | 24.15.0 (node) | `.node-24.15.0.pkg` | Node.js and its bundled package-manager shims |
| `pgschema` | 1.7.4 | `.pgschema-1.7.4.pkg` | Postgres schema tooling |
| `pnpm` | 11.4.0 | `.pnpm-11.4.0.pkg` | JS/TS package manager |

### Fork divergence: the lefthook pin

`bin/lefthook` and `bin/.lefthook-*.pkg` are a named, deliberate exception to
`launchpad/AGENTS.md`'s "never move or rename upstream files" rule. ADR-0017 records
why: lefthook 2.1.3's `@{push}`-unavailable fallback crashed every pre-push command
on this fork's first push (this fork's default branch is named `launchpad`, which
collides with the top-level `launchpad/` directory), so the pin was bumped to
2.1.10 ahead of upstream's own version. The ADR calls this a standing divergence --
not one expected to resolve itself -- bounded to exactly these two files.

### Activation

Hermit is activated once per shell session with `. ./bin/activate-hermit`
(`bin/activate-hermit.fish` for fish shells). The script must be *sourced*, not
executed -- run directly it exits with status 33. Sourcing it runs `hermit noop` as
a readiness check, `eval`s the output of `hermit activate bin/..` to set the calling
shell's environment, clears the shell's command hash under bash/zsh, and prints a
confirmation using `hermit env HERMIT_ENV`.

Activation is optional but recommended, not mandatory: CONTRIBUTING.md's
First-Time Setup labels it "(optional but recommended)" and states that a
contributor who skips it must independently match the minimum tool versions in its
own prerequisites table. Each pinned tool downloads lazily on first invocation and
is cached thereafter; `just bootstrap` (called automatically by `just setup`)
pre-downloads every pinned tool up front instead.

Two places in this repository instruct activating Hermit specifically for agents,
not only human contributors: root `AGENTS.md` says to activate it before running
Git or hooks and not to work around an unconfigured PATH by rewriting hook
commands, and `launchpad/AGENTS.md` repeats the instruction for any git command run
under `launchpad/`. `launchpad/docs/corpus/AGENTS.md` adds one more case: `just
corpus-validate` needs Hermit activated first, while running
`python3 launchpad/project-intelligence/corpus/validate.py` directly does not.

### Continuous integration

`.github/workflows/ci.yml` activates Hermit via the pinned action
`cashapp/activate-hermit@cea9af7913204a965fd488637a8d1811bba2e616` (v1) as a step
in the great majority of its jobs. One job is the deliberate exception: a
dedicated Windows Rust job (`TARGET: x86_64-pc-windows-msvc`) runs on a real
Windows runner without that step, because Hermit -- used by the Linux jobs --
does not provide an MSVC toolchain; that job instead relies on the runner's
preinstalled rustup honoring the repo-root `rust-toolchain.toml`. Separately, the
mobile/Flutter job hashes every file under `bin/` to key a cache of
`~/.cache/hermit/pkg`, so Hermit's own downloaded package store is reused across
CI runs rather than re-fetched every time.

The repository's `Justfile` never references Hermit directly; `just` recipes
depend on the PATH that `. ./bin/activate-hermit` establishes in the calling
shell, rather than invoking `hermit` themselves.

## Commands

| Command | Description | Argument | Example (as used in `bin/activate-hermit`) |
|---|---|---|---|
| `hermit noop` | Readiness check; `activate-hermit` only proceeds to activate the environment if this succeeds | none | `"${BIN_DIR}/hermit" noop` |
| `hermit activate <dir>` | Emits a shell snippet, consumed via `eval`, that sets the calling shell's environment for the Hermit environment rooted at `<dir>` | `<dir>`: the environment root (the repository root, passed as `bin/..`) | `eval "$("${BIN_DIR}/hermit" activate "${BIN_DIR}/..")"` |
| `hermit env <name>` | Prints the value of one named Hermit environment variable | `<name>`: the variable name | `"${HERMIT_ENV}"/bin/hermit env HERMIT_ENV` |

## Boundary

This node does not describe:
- **Why the two-hop symlink/lazy-download design exists at Hermit's own
  implementation level.** The *Pinned toolchain* section's mechanism is described
  from what is observable in this repository's `bin/` directory; no Hermit source
  or design document was opened, and the reasoning about *why* it is shaped this
  way is recorded as an `INFERENCE` in the evidence ledger above, not stated as
  fact.
- **Step-by-step first-time machine setup.** That is `development/setup.md`'s
  scope (issue #869, open and not yet drafted at the time this node was written)
  and, until it lands, CONTRIBUTING.md's own "First-Time Setup" section directly.
- **Non-Hermit minimum toolchain versions for a contributor who opts out of
  Hermit entirely.** That is `development/prerequisites.md`'s scope (issue #860,
  open and not yet drafted) and, until it lands, CONTRIBUTING.md's prerequisites
  table directly.
- **The full structure of `.github/workflows/ci.yml`** beyond where and how it
  activates or caches Hermit; the workflow file itself is the authority for
  everything else it does.

## Relationships

None declared. The sibling document tasks this node would most naturally link to
-- `development/setup.md` (#869) and `development/prerequisites.md` (#860) -- are
both open and undrafted, and `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` at the recorded revision carries no node under
`development/` at all (this is the first). Per `launchpad/docs/corpus/AGENTS.md`'s
own rule, a `relationships[].target` must resolve on the branch being merged into,
not on this working branch, and none of the candidate targets exist there yet.

## Scope and omissions

**This node covers** what Hermit pins in this repository and at which version, the
symlink mechanism that resolves a pinned command to `bin/hermit`, where and how
activation is required or optional (for human contributors, for agents, and for
`just corpus-validate` specifically), this fork's lefthook-pin divergence from
upstream (ADR-0017), and how CI activates, exempts, and caches Hermit.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Step-by-step first-time setup instructions | `development/setup.md` (#869, open, not yet drafted) |
| Non-Hermit toolchain minimum-version requirements | `development/prerequisites.md` (#860, open, not yet drafted) |
| `.github/workflows/ci.yml`'s full job structure beyond Hermit activation/exemption/caching | `.github/workflows/ci.yml` directly |
| The ADR-0017 upstream-boundary-exception decision itself, including its rejected alternatives | `launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No Hermit command that would trigger a package download was run.** `hermit
  noop`, `hermit activate`, and the tool-fetch behavior CONTRIBUTING.md describes
  were read from source and documentation, not executed, to avoid a live network
  side effect as part of authoring documentation.
- **This node was authored from a Windows (win32) checkout of the repository.**
  `git ls-tree` confirms `bin/lefthook`, `bin/cargo` and the other tool-name
  entries are recorded as mode-120000 (symlink) git objects, but on this checkout
  they materialize on disk as plain-text files containing the target string
  rather than functioning OS symlinks -- which is how their contents were
  actually read for this node's evidence. Whether they resolve identically as
  real symlinks on a Linux or macOS checkout (the platforms CI and most
  contributors use) was not independently exercised in this session.
- **Whether every rust-toolchain alias in `bin/` (`rls`, `rust-gdb`,
  `rust-gdbgui`, `rust-lldb`, and similar) is still a live, working Hermit
  binding** as opposed to a stale symlink was not exercised end-to-end -- only
  their symlink targets were read.
- **No manifest row (#626/#627-shaped) exists for this task**, per the
  `TEAM_KNOWLEDGE` entry in the ledger above; whether one should have existed, or
  whether `corpus-plan:v2` persists its planning data somewhere outside this
  repository, was not established.
