---
id: corpus-development-build
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
  - statement: "Justfile defines a `build` recipe as exactly `cargo build --workspace`, and a `build-release` recipe as exactly `cargo build --workspace --release`, each a single line with no other flags."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The root Cargo.toml's [workspace] members array lists 30 entries -- 29 crates under crates/ plus examples/countdown-bot -- and separately excludes desktop/src-tauri from that workspace via its own [workspace] exclude key."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "crates/buzz-voice/Cargo.toml depends directly on the sherpa-onnx crate (version 1.12), whose sys-crate dependency sherpa-onnx-sys resolves to 1.13.4."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/Cargo.toml"
  - statement: "Running `cargo build --workspace` at repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, from a clean target/ directory, fails during compilation of buzz-voice's build dependency sherpa-onnx-sys v1.13.4: its build script attempts to download a prebuilt native archive over HTTPS from github.com/k2-fsa/sherpa-onnx and panics with 'Connection Failed: tls connection init failed: invalid peer certificate: UnknownIssuer', which fails the whole workspace build with exit code 101 for that one build script."
    entry_class: FACT
    evidence:
      - "cargo_build(--workspace, cwd=repo root, revision=338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) -> error: failed to run custom build command for `sherpa-onnx-sys v1.13.4`; Caused by: process didn't exit successfully (exit code: 101); stderr: 'Downloading sherpa-onnx libs from https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.13.4/sherpa-onnx-v1.13.4-win-x64-static-MT-Release-lib.tar.bz2' then 'thread main panicked at .../sherpa-onnx-sys-1.13.4/build.rs:40:9: Failed to download sherpa-onnx archive ...: Connection Failed: tls connection init failed: invalid peer certificate: UnknownIssuer'"
  - statement: "Running `cargo build --workspace --exclude buzz-voice` at the identical revision (338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5), from the same clean target/ directory, compiles the other 29 workspace members with no error, printing 'Finished `dev` profile [unoptimized + debuginfo] target(s) in 2m 09s' and producing a compiled .exe for each binary crate (buzz-relay.exe, buzz-admin.exe, buzz-cli.exe, and the rest) under target/debug/."
    entry_class: FACT
    evidence:
      - "cargo_build(--workspace --exclude buzz-voice, cwd=repo root, revision=338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) -> Finished `dev` profile [unoptimized + debuginfo] target(s) in 2m 09s"
      - "ls(target/debug) -> buzz-relay.exe, buzz-admin.exe, buzz-acp.exe, buzz-agent.exe, buzz-cli.exe, buzz-backend-kubernetes.exe, buzz-dev-mcp.exe, buzz-pair-relay.exe, buzz-push-gateway.exe, and others present"
  - statement: "Because every other workspace member compiles cleanly from the same source tree at the same revision, the sherpa-onnx-sys failure is a download/network-egress problem specific to this checking environment rather than a defect in buzz-voice's or any other crate's source; whether it reproduces for a contributor with unrestricted access to github.com's release CDN was not established here."
    entry_class: INFERENCE
    evidence:
      - "cargo_build(--workspace, revision=338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) -> fails only inside sherpa-onnx-sys's build script, at the download step, with a TLS/certificate error"
      - "cargo_build(--workspace --exclude buzz-voice, revision=338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) -> succeeds for all 29 remaining members"
    confidence: 0.85
  - statement: "pnpm-workspace.yaml lists exactly three packages -- desktop, web, admin-web -- sharing one pnpm workspace and one root-level pnpm-lock.yaml."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
  - statement: "Justfile's desktop-install recipe runs plain `pnpm install` at the repository root; desktop-install-ci runs `pnpm install --frozen-lockfile` for a reproducible install; desktop-build runs `cd desktop && pnpm build`; web-build runs `cd web && pnpm build`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Justfile's mobile-build-android recipe runs ./scripts/mobile-worktree-overrides.sh, then (with GIT_DIR and GIT_WORK_TREE unset) `cd mobile && flutter build apk --debug --no-pub`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The CI workflow .github/workflows/ci.yml runs `just desktop-build`, `just web-build` and `just mobile-build-android` as real job steps, the same commands this node documents for a local build, not local-only convenience wrappers."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Justfile's clean recipe runs `cargo clean` for the root workspace and then `cargo clean --manifest-path desktop/src-tauri/Cargo.toml` for the Tauri backend's separate Cargo project, removing both target/ directories; it defines no equivalent clean step for the desktop/web pnpm build output or the mobile Flutter build output."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "rust-toolchain.toml pins channel = \"1.95.0\" with profile = \"default\", and this is the toolchain rustup resolves for any cargo/rustc invocation inside this repository."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
  - statement: "launchpad/docs/corpus/standards/naming.md's MUST 3 states that a document's id must be recognizable, on sight, as its filename, and that for a document one level below the corpus root inside a purpose-named subdirectory this means: strip .md, lowercase the stem, prefix with corpus-, and insert that subdirectory's singular form before the stem."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
  - statement: "Applying naming.md's MUST 3 literally to development/build.md -- one level below the corpus root, subdirectory development already singular -- gives the id corpus-development-build; this differs from the convention observed on already-merged two-levels-deep nodes such as architecture/containers/redis.md (id architecture-containers-redis, no corpus- prefix, plural subdirectory name kept), a depth naming.md's MUST 3 text does not itself address, so the two conventions are not read here as contradictory, only as covering different depths."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
      - "launchpad/docs/corpus/architecture/containers/redis.md"
    confidence: 0.7
  - statement: "node.schema.json's type enum includes development as one of the thirteen corpus-surface values, reused from PRD #602's own enumerated surface list."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #846's Definition of Done requires this node to state its goal, prerequisites and allowed environment/scope; to provide ordered, executable, project-specific steps; to define success verification and rollback/cleanup where relevant; and to link authoritative commands/config rather than give generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#846 definition of done"
  - statement: "Sibling child issues of parent Feature #619 include #859, titled 'task: document development/hermit.md', and #860, titled 'task: document development/prerequisites.md' -- both still open at the time this node was checked, and neither yet a corpus node -- so toolchain-installation content this node's Before you start section gestures at (Hermit, general prerequisites) is those tasks' subject, not this one's."
    entry_class: FACT
    evidence:
      - "gh_issue_view(repo='launchpad-26/buzz', number=859) -> title 'task: document development/hermit.md'"
      - "gh_issue_view(repo='launchpad-26/buzz', number=860) -> title 'task: document development/prerequisites.md'"
  - statement: "git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run immediately before finalizing this node's front matter, lists no development/ directory and no file at launchpad/docs/corpus/development/build.md -- confirming this task's target document does not already exist on the merge target -- and lists the architecture/deployment nodes (docker-compose.md, hosted-topology.md, kubernetes.md, local-development.md, multi-community.md, multi-relay.md, single-relay.md) among the corpus's existing content, none of them typed development and none of them documenting a source build procedure."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus', run before finalizing front matter) -> no development/ subdirectory; architecture/deployment/{docker-compose,hosted-topology,kubernetes,local-development,multi-community,multi-relay,single-relay}.md present; no file at development/build.md"
  - statement: "launchpad/docs/corpus/templates/procedure.md (id corpus-template-procedure) is merged on origin/launchpad and is the corpus's template for a Diátaxis how-to-shaped node -- goal-oriented, sequenced instruction for an already-competent reader -- which this node's build task fits rather than information-oriented reference or understanding-oriented explanation content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
---

# Build the Buzz workspace

Compile the Rust workspace and each platform frontend from source, and confirm each
build actually produced its output -- the task a developer or agent runs after
cloning, after pulling changes that touch source, or before exercising a binary that
a dev script does not build for you on its own.

## Before you start

- A working Rust toolchain matching `rust-toolchain.toml`'s pinned channel (`1.95.0`,
  `profile = "default"`) -- `rustup` resolves this automatically on the first
  `cargo`/`rustc` invocation inside the repository.
- For the desktop and web frontend builds: Node.js and `pnpm`, with dependencies
  installed once via `just desktop-install` (`pnpm install` at the repository root --
  `pnpm-workspace.yaml` covers `desktop`, `web` and `admin-web` from one lockfile)
  before the first `pnpm build`.
- For the mobile Android build: a working Flutter SDK on `PATH`.
- Installing those toolchains in the first place (Hermit, Docker, Node, Flutter) is
  `just bootstrap`'s job and `development/hermit.md`'s and
  `development/prerequisites.md`'s subject, not this node's -- see *Boundary*.

## Build the Rust workspace

1. From the repository root, run `cargo build --workspace` (the `just build` recipe).
   This compiles every crate the root `Cargo.toml`'s `[workspace]` `members` array
   lists -- 29 crates under `crates/` plus the `examples/countdown-bot` example, 30
   members total -- with the toolchain `rust-toolchain.toml` pins.
2. For an optimized build, run `cargo build --workspace --release` (`just
   build-release`) instead. It builds the same 30 members under the `release`
   profile, producing binaries under `target/release/` rather than `target/debug/`.
3. Before either step, note that the root `Cargo.toml` explicitly excludes
   `desktop/src-tauri` from `[workspace] members`. Neither command above touches the
   desktop app's Rust (Tauri) backend -- that is a separate Cargo project built by
   the `desktop-tauri-*` recipes against `desktop/src-tauri/Cargo.toml`, and is part
   of the platform frontend build below, not this section.

## Build a platform frontend

The Rust workspace build above produces no runnable desktop app, web bundle, or
mobile package. Each platform frontend is its own build with its own tool, forked
here rather than numbered as one sequence because the three do not share steps:

4a. **Desktop.** `just desktop-build` runs `pnpm build` inside `desktop/`, producing
    the desktop frontend's static assets. Run `just desktop-install` first if
    `desktop/node_modules` does not exist yet.

4b. **Web.** `just web-build` runs `pnpm build` inside `web/`, producing the web
    frontend's static assets. It shares the same root `pnpm-workspace.yaml` and
    lockfile as desktop, so the same `just desktop-install` install step covers both.

4c. **Mobile (Android).** `just mobile-build-android` first runs
    `scripts/mobile-worktree-overrides.sh` (a worktree-local debug identity, so
    multiple checkouts do not collide), then runs `flutter build apk --debug
    --no-pub` inside `mobile/`, producing an unsigned debug APK.

## Verify the build succeeded

- **Rust workspace.** `cargo build --workspace` exits `0` and prints a final
  `Finished` line naming the profile; a compiled binary for each binary crate
  appears under `target/debug/<crate>.exe` (`target/release/` for the release
  profile). At the revision this node was checked, `cargo build --workspace`
  against the *full* member list fails inside `buzz-voice`'s build dependency
  `sherpa-onnx-sys`, whose build script downloads a prebuilt native archive over
  HTTPS and, in the environment this node was checked in, could not complete a TLS
  handshake with the download host. `cargo build --workspace --exclude buzz-voice`
  at the identical revision compiled the other 29 members cleanly, confirming the
  gap is isolated to that one crate's download step rather than a wider compilation
  problem -- see the evidence ledger for exactly what each run printed, and *Scope
  and omissions* for what was not established about it.
- **Desktop / web.** `pnpm build` exits non-zero on a build error, naming the
  failing file in its own output. This node's evidence does not include an executed
  run of either -- see *Scope and omissions*.
- **Mobile.** `flutter build apk` exits non-zero on a build error and, on success,
  reports the built APK's path under `mobile/build/`. This node's evidence does not
  include an executed run -- no Flutter SDK was available in the environment this
  node was checked against.

## Clean up

`just clean` runs `cargo clean` for the root workspace, then `cargo clean
--manifest-path desktop/src-tauri/Cargo.toml` for the Tauri backend's separate
project, removing both `target/` directories. It defines no equivalent step for the
desktop/web `pnpm build` output or the mobile `flutter build` output -- clearing
those means deleting each package's own build directory by hand, or using that
tool's own clean command.

## See also

- `launchpad/docs/corpus/architecture/deployment/local-development.md` -- running
  the local development environment these built binaries are exercised against.
  Building does not depend on that environment being up; running what you built
  usually does.
- `development/hermit.md`, `development/prerequisites.md` -- toolchain installation
  (not yet corpus nodes; see the evidence ledger for the open issues that own them).

## Boundary

This node does not describe:

- **a command's full flag or option reference** -- no reference-shaped corpus node
  for `cargo`, `pnpm`, `flutter` or `just` exists yet to defer to; this node cites
  only the flags the build task actually uses.
- **acquiring the underlying skill of working in a Rust/pnpm/Flutter monorepo from
  scratch**, for a newcomer -- a tutorial, which has no corpus template as of this
  writing.
- **why the workspace is laid out this way** -- the crate boundaries, or why
  `desktop/src-tauri` sits outside `[workspace] members` -- a concept/explanation
  node, if one is later written, would own that; this node only states the layout
  as read from `Cargo.toml`.
- **installing the toolchains themselves** (Hermit, Docker, Node, Flutter) -- `just
  bootstrap`'s job, and `development/hermit.md`'s and
  `development/prerequisites.md`'s subject once those tasks are written.
- **linting, formatting, or running tests** (`just check`, `just fmt-check`, `just
  clippy`, `just test`, `just test-unit`, `just test-integration`) -- related `just`
  recipes, each a different task from building, and not documented by this node.
- **building or packaging a distributable release artifact** -- installers, signed
  binaries, container images, Helm charts -- owned by the `release.yml`,
  `docker.yml`, `desktop-release-candidate.yml` and `helm-chart.yml` workflows and
  whatever task documents them, not this how-to.

## Relationships

Declared: none. `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`,
run immediately before finalizing this node's front matter, lists the corpus's
architecture nodes (containers, context, deployment, flows, principles) and its own
meta-documents (`AGENTS.md`, `README.md`, `schema/`, `standards/`, `templates/`), and
no `development`-typed node. The `architecture/deployment/*` nodes closest in subject
-- `local-development.md`, `docker-compose.md` -- document running and deploying the
system, not compiling it from source; this node's *See also* section points to
`local-development.md` in prose without an authored edge, because neither node's own
text presently depends on the other holding. No sibling `development/*` node exists
yet to relate to.

## Scope and omissions

**This node covers** compiling the Rust workspace (`cargo build --workspace` /
`--release`) and each platform frontend (desktop, web, mobile Android) from source on
a developer's or agent's own machine, what each build step produces, and how to tell a
build succeeded.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Installing the toolchains this node assumes (Hermit, Docker, Node, Flutter) | `just bootstrap`; `development/hermit.md`, `development/prerequisites.md` (open child issues of Feature #619, not yet corpus nodes) |
| Linting, formatting and static checks (`just check`, `just fmt-check`, `just clippy`) | Not this node |
| Running tests (`just test`, `just test-unit`, `just test-integration`) | Not this node |
| Running the local dev environment / Docker services the built binaries connect to | `launchpad/docs/corpus/architecture/deployment/local-development.md` |
| Building signed, distributable release artifacts (desktop installers, container images, Helm charts) | The `release.yml`, `docker.yml`, `desktop-release-candidate.yml` and `helm-chart.yml` workflows; no corpus node found documenting them at this revision |
| Why the workspace is laid out the way it is (crate boundaries, `desktop/src-tauri`'s exclusion) | No concept/explanation node exists yet for this |
| A reference-shaped listing of every `just` build-related recipe's flags | No reference-shaped corpus node exists yet for this |

**No relationships declared.** See *Relationships* above for what was checked and why
none of the corpus's existing nodes are a fit yet.

**Expected but not verified when this node was written:**

- **`just desktop-build` and `just web-build` were read from `Justfile`, not
  executed.** Both require a `pnpm install` this node did not run in the environment
  it was checked in; whether they succeed cleanly at the recorded revision, and what
  their build output directories actually contain, is unverified here.
- **`just mobile-build-android` was read from `Justfile`, not executed.** No Flutter
  SDK was present in the environment this node was checked against, so the mobile
  build step is FACT-cited to the recipe's source, not to a run.
- **`cargo build --workspace --release` (`just build-release`) was not executed.**
  Its command is cited directly from `Justfile`, by the same pattern as the executed
  debug build, not run separately; whether the release profile hits the same
  `sherpa-onnx-sys` download gap was not checked.
- **Whether the `sherpa-onnx-sys` download failure is specific to this checking
  environment's network egress, or reproduces for any contributor without direct
  access to `github.com`'s release CDN, was not established** -- only that excluding
  the one crate lets the other 29 workspace members build cleanly at this revision.
- **No node in this corpus was found describing `crates/buzz-voice` or the
  `sherpa-onnx` dependency's purpose** -- this node cites the crate only to explain
  the one build failure it hit, not as a claim about what the crate does.
