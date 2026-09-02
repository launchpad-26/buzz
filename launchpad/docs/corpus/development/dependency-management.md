---
id: development-dependency-management
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The repository declares dependencies in four separate ecosystems, each with its own manifest and its own committed lockfile: Rust (root Cargo.toml + Cargo.lock, and the separately-excluded desktop/src-tauri/Cargo.toml + desktop/src-tauri/Cargo.lock), Node via pnpm (pnpm-workspace.yaml + one root pnpm-lock.yaml), Flutter/Dart (mobile/pubspec.yaml + mobile/pubspec.lock), and Hermit-pinned developer tooling (bin/hermit.hcl plus ten bin/.<tool>-<version>.pkg marker files)."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "Cargo.lock"
      - "desktop/src-tauri/Cargo.toml"
      - "desktop/src-tauri/Cargo.lock"
      - "pnpm-workspace.yaml"
      - "pnpm-lock.yaml"
      - "mobile/pubspec.yaml"
      - "mobile/pubspec.lock"
      - "bin/hermit.hcl"
  - statement: "All four lockfiles are tracked in git, confirmed by `git ls-files` listing Cargo.lock, desktop/src-tauri/Cargo.lock, pnpm-lock.yaml and mobile/pubspec.lock."
    entry_class: FACT
    evidence:
      - "git_ls_files(repo root, filtered to lockfile names) -> Cargo.lock, desktop/src-tauri/Cargo.lock, mobile/pubspec.lock, pnpm-lock.yaml, plus bin/.<tool>-<version>.pkg, bin/hermit.hcl, patches/isomorphic-git.patch, patches/virtua@0.49.3.patch"
  - statement: "The root Cargo.toml's [workspace] members array lists 32 entries -- 30 crates under crates/, plus launchpad/crates/knowledge and examples/countdown-bot -- and its exclude key removes desktop/src-tauri from that workspace entirely, so desktop/src-tauri is a second, independent Cargo project with its own lockfile."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The root Cargo.toml carries a [workspace.dependencies] table of 62 entries which member crates consume by inheritance rather than by restating a version: crates/buzz-core/Cargo.toml, for example, writes `nostr = { workspace = true }` and `serde = { workspace = true }`, and every crate under crates/ except buzz-persona uses at least four such inherited entries."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-core/Cargo.toml"
      - "grep_count('workspace = true', crates/*/Cargo.toml) -> buzz-relay 58, buzz-test-client 30, buzz-push-gateway 27, buzz-acp 26, ... buzz-persona 0"
  - statement: "The root Cargo.toml ends with a [patch.crates-io] section holding exactly one entry -- aws-creds redirected to a git fork at rev c9fce3620dd434c1f810101d672cf384268dbb0f -- with an in-file comment stating it is a temporary fork pin adopting the aws-creds portion of durch/rust-s3#449 so the relay pod can read EKS Pod Identity credentials, to be reverted once that pull request lands upstream."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "rust-toolchain.toml pins channel 1.95.0 with profile default, while the root Cargo.toml's [workspace.package] declares rust-version = \"1.88.0\" as the crates' own minimum supported Rust version -- two different numbers serving two different purposes."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
      - "Cargo.toml"
  - statement: "pnpm-workspace.yaml lists exactly three packages -- desktop, web, admin-web -- and additionally carries an allowBuilds key (esbuild), an overrides key forcing @radix-ui/react-dismissable-layer to 1.1.19 and linkify-it to ^5.0.2, and a patchedDependencies key mapping isomorphic-git and virtua@0.49.3 to patch files under patches/."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
      - "patches/isomorphic-git.patch"
      - "patches/virtua@0.49.3.patch"
  - statement: "The comments in pnpm-workspace.yaml state why each override exists and the condition for removing it: the @radix-ui/react-dismissable-layer pin exists because two Radix packages resolved different versions and each copy kept its own module-level saved <body> pointer-events style, freezing the app (#1482), removable once every @radix-ui dependency converges naturally; the linkify-it pin covers GHSA-22p9-wv53-3rq4 and GHSA-v245-v573-v5vm, removable once markdown-it resolves linkify-it >= 5.0.2 on its own."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
  - statement: "The root package.json is a private workspace root named buzz-workspace that declares packageManager pnpm@11.4.0, one devDependency (@biomejs/biome) and one dependency (@tailwindcss/typography); the per-app dependency lists live in desktop/package.json, web/package.json and admin-web/package.json."
    entry_class: FACT
    evidence:
      - "package.json"
      - "desktop/package.json"
      - "web/package.json"
      - "admin-web/package.json"
  - statement: "Justfile defines desktop-install as plain `pnpm install` at the repository root and desktop-install-ci as `pnpm install --frozen-lockfile`, and defines mobile-install as `unset GIT_DIR GIT_WORK_TREE; cd mobile && flutter pub get`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Justfile's desktop version-bump path regenerates both JS and Rust lockfiles without a full build, using `pnpm install --lockfile-only` and `cargo update -p buzz-desktop --manifest-path desktop/src-tauri/Cargo.toml`; the relay version-bump path uses `cargo update -p buzz-relay` against the root lockfile."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "mobile/pubspec.yaml declares an sdk constraint of ^3.11.4, 35 entries under dependencies and 8 under dev_dependencies; every versioned entry is a caret range (for example hooks_riverpod ^3.0.3, nostr ^2.0.0, flutter_secure_storage ^10.0.0), and the two unversioned ones -- flutter and flutter_test -- resolve from the SDK rather than from pub.dev."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
  - statement: "bin/hermit.hcl is the only .hcl file in bin/ and sets exactly one option, manage-git = true; the actual version pins are carried by ten bin/.<tool>-<version>.pkg marker files (biome 2.4.7, cargo-deny 0.19.0, cmake 4.3.1, flutter 3.41.7, just 1.46.0, lefthook 2.1.10, node 24.15.0, pgschema 1.7.4, pnpm 11.4.0, rustup 1.28.2), so changing a pinned tool version means replacing a marker file, not editing the .hcl."
    entry_class: FACT
    evidence:
      - "bin/hermit.hcl"
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
  - statement: "bin/README.hermit.md states that the symlinks in bin/ are managed by Hermit and automatically download and install Hermit itself as well as packages, local to this environment -- it names no command for adding a package to the environment."
    entry_class: FACT
    evidence:
      - "bin/README.hermit.md"
  - statement: "The repository's dependency-update automation is Renovate, configured by a root renovate.json; there is no .github/dependabot.yml and no renovate configuration under .github/."
    entry_class: FACT
    evidence:
      - "renovate.json"
      - "ls(.github/) -> CODEOWNERS, ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE.md, hooks, scripts, workflows -- no dependabot.yml, no renovate.json"
  - statement: "renovate.json extends config:recommended and helpers:pinGitHubActionDigests, sets minimumReleaseAge to 3 days with minimumReleaseAgeBehaviour timestamp-required, sets internalChecksFilter strict, prCreation immediate, automerge true, rebaseWhen conflicted, recreateWhen always, separateMinorPatch true, and postUpdateOptions [\"cargo:updateLockfile\"]."
    entry_class: FACT
    evidence:
      - "renovate.json"
  - statement: "renovate.json's packageRules carry seven rules: major updates opt out of automerge and require human review; cargo-manager updates stay ungrouped with separateMinorPatch true and separateMultipleMinor false; Swatinem/rust-cache is held at <=2.9.1; evalexpr is held at <13 because v13 relicensed from MIT to AGPL-3.0; redis and deadpool-redis are grouped because deadpool-redis re-exports redis types; earshot is held at <1.2.0 pending a VAD threshold re-pick; and @tiptap/** is held at <3.23.0."
    entry_class: FACT
    evidence:
      - "renovate.json"
  - statement: "deny.toml configures three cargo-deny check families -- [advisories] with four ignored RUSTSEC ids each carrying a written reason, [licenses] with an 18-entry allow list plus seven [[licenses.clarify]] blocks and confidence-threshold 0.8, and [bans] with multiple-versions = \"warn\" and wildcards = \"allow\" -- and configures no [sources] section."
    entry_class: FACT
    evidence:
      - "deny.toml"
  - statement: ".github/workflows/ci.yml runs `cargo-deny check` as the single step of a job named Security, which is gated on the rust paths filter; that filter's globs include Cargo.toml, Cargo.lock, rust-toolchain.toml and deny.toml, so any Rust dependency change triggers the dependency-policy job."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: ".github/workflows/ci.yml enforces the pnpm lockfile against the manifests in two ways: the Web job runs `pnpm install --frozen-lockfile` directly, and four other job steps run `just desktop-install-ci`, which is the same command; the desktop paths filter includes pnpm-lock.yaml."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile"
  - statement: ".github/workflows/ci.yml's Mobile job installs Dart dependencies with `cd mobile && flutter pub get`, with no --enforce-lockfile flag, and keys its pub cache on hashFiles('mobile/pubspec.lock')."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "No `cargo build --locked`, `cargo --locked`, `--offline` or `flutter pub get --enforce-lockfile` invocation appears in Justfile, .github/workflows/ci.yml or lefthook.yml; the only lockfile-drift flag present anywhere in those three files is pnpm's --frozen-lockfile."
    entry_class: FACT
    evidence:
      - "grep('--locked|--frozen-lockfile|--offline', Justfile, .github/workflows/ci.yml, lefthook.yml) -> Justfile:130 'pnpm install --frozen-lockfile'; .github/workflows/ci.yml:942 'pnpm install --frozen-lockfile'; no other matches"
  - statement: "Because pnpm is the only ecosystem whose CI install command fails on a lockfile that disagrees with its manifests, a Rust or Dart change that edits a manifest without regenerating its lockfile can reach CI without that specific mismatch being detected -- Rust's mismatch surfaces indirectly, when cargo rewrites Cargo.lock during the build, and Dart's `flutter pub get` resolves and rewrites pubspec.lock silently."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile"
      - "grep('--locked|--frozen-lockfile|--offline', Justfile, .github/workflows/ci.yml, lefthook.yml) -> only pnpm's --frozen-lockfile"
    confidence: 0.75
  - statement: "launchpad/AGENTS.md's rule 'Never move or rename upstream files' lists its deliberate exceptions by name, and the only dependency-adjacent one is the Hermit lefthook pin, scoped exactly to bin/lefthook and bin/.lefthook-*.pkg with ADR-0017 as its record -- so every other manifest and lockfile in this repository is an upstream-owned file that this fork edits in place rather than overrides."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md"
  - statement: "launchpad/crates/knowledge is a cohort-owned crate listed in the upstream-owned root Cargo.toml's [workspace] members array, so adding a Rust dependency for cohort code edits an upstream file even though the crate itself lives under launchpad/."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "CONTRIBUTING.md's 'PRs We're Unlikely to Merge' section names 'Large refactors or dependency swaps without a prior issue agreeing on the direction' as its first listed kind, on the stated ground that such changes cannot be safely reviewed without prior discussion."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "launchpad/AGENTS.md's repository-structure listing names a launchpad/upstream-intel/ directory as 'upstream tracking tooling', but no such directory exists on disk at the recorded revision -- launchpad/ contains AGENTS.md, AGENT_PR_TEMPLATE.md, ARCHITECTURE.md, ENVIRONMENTS.md, README.md, REQUIREMENTS.md, Research, SECURITY-POSTURE.md, VISION.md, agents, crates, decisions, deploy, docs, labels.yml, plans, project-intelligence, review-agent, scripts, skills and sync-labels.sh."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "ls(launchpad/) -> AGENTS.md, AGENT_PR_TEMPLATE.md, ARCHITECTURE.md, ENVIRONMENTS.md, README.md, REQUIREMENTS.md, Research, SECURITY-POSTURE.md, VISION.md, agents, crates, decisions, deploy, docs, labels.yml, plans, project-intelligence, review-agent, scripts, skills, sync-labels.sh -- no upstream-intel"
  - statement: "Issue #857's Definition of Done requires this node to state its goal, prerequisites and allowed environment/scope; to provide ordered steps that are executable and project-specific; to define success verification and rollback/cleanup where relevant; and to link authoritative commands/config rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#857 definition of done"
  - statement: "Issue #857's Out of scope section excludes creating or materially editing a second hand-authored canonical corpus document, changing runtime product behavior, deciding unresolved ADR outcomes, and broad 'while here' documentation cleanup; its stated parent is Feature #619."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#857"
  - statement: "At the recorded revision, origin/launchpad's corpus tree carries four development/ nodes -- development/build.md (id corpus-development-build), development/debugging.md (id debugging), development/hermit.md (id development-hermit) and development/prerequisites.md (id development-prerequisites) -- plus templates/procedure.md (id corpus-template-procedure), and carries no file at development/dependency-management.md; all five ids are therefore valid relationship targets on the merge target and this node's own target path is unoccupied."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus/development') -> build.md, debugging.md, hermit.md, prerequisites.md; no dependency-management.md"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "development/hermit.md is the corpus's canonical reference for what Hermit pins in this repository, the two-hop symlink mechanism, activation, the ADR-0017 lefthook divergence, and how CI activates and caches Hermit -- so this node states only the act of changing a pin and defers the mechanism to that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/hermit.md"
  - statement: "launchpad/docs/corpus/standards/naming.md's MUST 3 prescribes stripping .md, lowercasing the stem, prefixing with corpus-, and inserting the subdirectory's singular form, which applied literally to development/dependency-management.md would give corpus-development-dependency-management; the two already-merged sibling nodes in the same directory carry development-hermit and development-prerequisites, without the corpus- prefix, and this node follows those siblings so the three ids in one directory stay mutually consistent."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: development-hermit
  - type: references
    target: corpus-development-build
---

# Add, update or remove a dependency

Change what this repository depends on -- a Rust crate, a Node package, a Dart
package, or a Hermit-pinned tool -- so that the manifest, the lockfile and the
gates that read them all end up in agreement. This is the task a contributor
performs when a feature needs a library the repository does not yet carry, when a
pinned version has to move, or when a dependency is being taken back out.

Four ecosystems live in this repository and they do not share a procedure. Pick
the one your change belongs to; the sequences below are separate on purpose, not
one numbered list broken into parts.

## Before you start

- **The Hermit environment activated** (`. ./bin/activate-hermit`), so `cargo`,
  `pnpm`, `flutter`, `just`, `lefthook` and `cargo-deny` resolve to the versions
  this repository pins rather than to whatever is on your own `PATH`. What Hermit
  pins and how activation works is `development/hermit.md`'s subject, not this
  node's.
- **A branch, not `launchpad` directly.** Every manifest and lockfile named below
  is an upstream-owned file that this fork edits in place. `launchpad/AGENTS.md`
  names its deliberate upstream exceptions explicitly, and the only
  dependency-adjacent one is the Hermit `lefthook` pin (`bin/lefthook` and
  `bin/.lefthook-*.pkg`, recorded in ADR-0017). Nothing else on this page is an
  exception, so a dependency change here is a change to a file that will meet
  upstream again at the next merge.
- **An agreed reason, for anything large.** `CONTRIBUTING.md` asks that large
  refactors or dependency swaps have a prior issue agreeing on the approach
  before the pull request exists.
- **Know which Rust project you are in.** The root workspace and
  `desktop/src-tauri` are two separate Cargo projects with two separate
  lockfiles -- see *Add or update a Rust crate* below.

## Add or update a Rust crate

The root `Cargo.toml` is a workspace of 32 members: 30 crates under `crates/`,
plus `launchpad/crates/knowledge` and `examples/countdown-bot`. Member crates do
not carry their own version numbers for shared dependencies -- they inherit from
the root's 62-entry `[workspace.dependencies]` table.

1. **Decide whether the crate is shared.** If more than one workspace member will
   use it, add it to `[workspace.dependencies]` in the root `Cargo.toml` with its
   version and feature list, then reference it from each member as
   `<crate> = { workspace = true }`. `crates/buzz-core/Cargo.toml` is the pattern
   to copy. If exactly one crate uses it and it is unlikely to spread, a plain
   version string in that crate's own `[dependencies]` is acceptable --
   `percent-encoding = "2.3"` in `buzz-core` is an existing example.
2. **Add the member-side line** in the consuming crate's `Cargo.toml`. Keep the
   feature list on the workspace entry, not duplicated per member; that is what
   inheritance is for.
3. **Regenerate the lockfile** by running any `cargo` command that resolves --
   `cargo build --workspace` (`just build`) or `cargo check`. `Cargo.lock` is
   committed, so the resulting change is part of your diff.
4. **If the crate belongs to the desktop app's Rust backend instead**, edit
   `desktop/src-tauri/Cargo.toml` and regenerate `desktop/src-tauri/Cargo.lock`.
   The root workspace's `exclude = ["desktop/src-tauri"]` means no root `cargo`
   command touches it -- pass `--manifest-path desktop/src-tauri/Cargo.toml`, the
   way `just bump-desktop-version` does when it runs
   `cargo update -p buzz-desktop --manifest-path desktop/src-tauri/Cargo.toml`.
5. **Bump an existing crate in place** with `cargo update -p <crate>` rather than
   hand-editing `Cargo.lock`. The version-bump recipes in `Justfile` use exactly
   this form.
6. **Check the licence and advisory policy before opening the pull request** by
   running `cargo-deny check` locally -- the same command CI's Security job runs.
   `deny.toml` decides the verdict; see *Verify the change* below for what a
   failure means and what changing that file implies.

**When the new crate needs a fork or an unreleased fix**, the root
`Cargo.toml`'s `[patch.crates-io]` section is where that goes. It currently holds
one entry -- `aws-creds` redirected to a git fork at a pinned `rev`, with an
in-file comment giving the reason (EKS Pod Identity credentials, adopting the
`aws-creds` portion of `durch/rust-s3#449`) and the removal condition (revert
once that pull request lands upstream). A new patch entry is expected to carry
the same two things: why it exists, and what makes it removable.

## Add or update a Node package

`pnpm-workspace.yaml` covers three packages -- `desktop`, `web` and `admin-web`
-- against a single root `pnpm-lock.yaml`. The root `package.json` is a private
workspace root (`buzz-workspace`) that pins `packageManager` to `pnpm@11.4.0` and
carries only Biome and the Tailwind typography plugin; product dependencies live
in each app's own `package.json`.

1. **Add the dependency to the app that uses it** -- `desktop/package.json`,
   `web/package.json` or `admin-web/package.json` -- not to the root
   `package.json`, unless it genuinely applies to every workspace package the way
   Biome does.
2. **Install from the repository root**, not from inside the app directory:
   `just desktop-install` runs `pnpm install` at the root, which resolves all
   three packages together and writes the single shared `pnpm-lock.yaml`.
3. **Commit `pnpm-lock.yaml` with the manifest change.** CI installs with
   `pnpm install --frozen-lockfile` -- directly in the Web job, and via
   `just desktop-install-ci` in the desktop-side jobs -- and that command fails
   rather than silently re-resolving when the lockfile disagrees with the
   manifests. A manifest change without its lockfile change is a red build.
4. **If a transitive version has to be forced**, add it under `overrides` in
   `pnpm-workspace.yaml` rather than pinning the direct dependency that pulls it
   in. Both existing overrides model what an override entry is expected to carry:
   `@radix-ui/react-dismissable-layer: 1.1.19` records the duplicate-copy
   `pointer-events` freeze it fixes (`#1482`) and states it is removable once the
   Radix packages converge naturally; `linkify-it: "^5.0.2"` names the two
   advisories it covers (`GHSA-22p9-wv53-3rq4`, `GHSA-v245-v573-v5vm`) and states
   it is removable once `markdown-it` resolves the fixed version itself.
5. **If upstream source has to be modified**, use pnpm's patch mechanism rather
   than vendoring: `patchedDependencies` in `pnpm-workspace.yaml` maps
   `isomorphic-git` and `virtua@0.49.3` to patch files under `patches/`, both
   committed.

## Add or update a Flutter/Dart package

1. **Add the package to `mobile/pubspec.yaml`** under `dependencies` (or
   `dev_dependencies` for test/lint-only packages), as a caret range matching the
   file's existing style -- every versioned entry is a caret range, and the SDK
   constraint is `^3.11.4`. `flutter` and `flutter_test` resolve from the SDK
   rather than pub.dev and take no version.
2. **Resolve and lock** with `just mobile-install`, which runs
   `flutter pub get` inside `mobile/` (with `GIT_DIR`/`GIT_WORK_TREE` unset so it
   behaves correctly inside a git worktree).
3. **Commit `mobile/pubspec.lock`.** It is tracked, and CI keys its pub cache on
   that file's hash. Note that CI's install step is a plain `flutter pub get`
   with no `--enforce-lockfile`, so an unregenerated lockfile is not itself
   caught -- see *Verify the change*.
4. **Run the mobile checks** before pushing: `just mobile-check` (lint plus
   format check) and `just mobile-test`.

## Change a Hermit-pinned tool

Hermit pins developer tooling rather than product dependencies -- the compiler
toolchain, `pnpm`, `flutter`, `just`, `lefthook`, `cargo-deny`, `biome`,
`cmake`, `pgschema`. `bin/hermit.hcl` is the only `.hcl` file in `bin/` and sets
exactly one option (`manage-git = true`); the version pins are carried by ten
`bin/.<tool>-<version>.pkg` marker files, so **changing a pinned version means
replacing a marker file, not editing the `.hcl`**.

1. **Read `development/hermit.md` first.** It is the corpus's canonical account of
   what is pinned, at which version, and how the symlink chain resolves. This node
   does not restate it.
2. **Let Hermit rewrite `bin/` rather than hand-editing symlinks.** `bin/` is
   Hermit-managed, per `bin/README.hermit.md`; a hand-made symlink that Hermit did
   not create is indistinguishable in the diff from one it did, and no check in
   this repository will tell you which you have.
3. **Expect the diff to change the mobile CI cache key.** `.github/workflows/ci.yml`
   hashes every file under `./bin` to key its Hermit package cache, so any pin
   change invalidates that cache by design.
4. **Treat `bin/lefthook` and `bin/.lefthook-*.pkg` as special.** They are a named,
   recorded divergence from upstream's pin (ADR-0017), listed in
   `launchpad/AGENTS.md` as a standing exception. Changing them is a change to that
   record, not a routine bump.

Two related pins are **not** Hermit's and are edited directly:
`rust-toolchain.toml` (`channel = "1.95.0"`, `profile = "default"`), which decides
which Rust toolchain `rustup` resolves inside the repository, and the root
`Cargo.toml`'s `[workspace.package] rust-version = "1.88.0"`, which declares the
crates' own minimum supported Rust version. They are different numbers answering
different questions; moving one does not move the other.

## Let Renovate do the routine updates

Routine version bumps are automated, so a hand-written bump pull request usually
duplicates work Renovate would have done. The configuration is the root
`renovate.json` -- there is no `.github/dependabot.yml` and no Dependabot
configuration anywhere in `.github/`.

What that configuration establishes, read from the file:

- **A three-day cooldown.** `minimumReleaseAge: "3 days"` with
  `minimumReleaseAgeBehaviour: "timestamp-required"` and
  `internalChecksFilter: "strict"`.
- **Automerge on, except for majors.** `automerge: true` globally, with a
  `packageRules` entry turning it off for `matchUpdateTypes: ["major"]` because
  major bumps often require code changes.
- **Rust lockfile maintenance.** `postUpdateOptions: ["cargo:updateLockfile"]`.
- **Cargo updates deliberately ungrouped**, with `separateMinorPatch: true` and
  `separateMultipleMinor: false`, because 0.x minor releases often carry breaking
  changes.
- **Four hard version holds, each with its stated reason:**
  `Swatinem/rust-cache` at `<=2.9.1` (its v2.9.2 cleanup can poison warm caches),
  `evalexpr` at `<13` (v13 relicensed MIT to AGPL-3.0), `earshot` at `<1.2.0`
  (quantized re-implementation regresses the huddle VAD at its calibrated
  threshold), and `@tiptap/**` at `<3.23.0` (editor lifecycle breaks under real
  relay latency).
- **One grouping rule:** `redis` and `deadpool-redis` move together, because
  `deadpool-redis` re-exports `redis`'s types.

Adding a hold or a group means adding a `packageRules` entry, and every existing
entry carries a `description` saying why it is there and, where applicable, what
would let it be removed. Match that.

## Verify the change

- **Rust.** `cargo build --workspace` (`just build`) resolves and, if the
  manifests moved, rewrites `Cargo.lock`; a clean exit plus a `Cargo.lock` diff
  that matches your manifest edit is the signal. Then run `cargo-deny check` --
  the exact command CI's Security job runs as its only step. That job is gated on
  the `rust` paths filter, whose globs include `Cargo.toml`, `Cargo.lock`,
  `rust-toolchain.toml` and `deny.toml`, so it fires on any Rust dependency
  change. `deny.toml` configures three check families: `[advisories]` (four
  ignored RUSTSEC ids, each with a written reason), `[licenses]` (an 18-entry
  allow list, seven `[[licenses.clarify]]` blocks, `confidence-threshold = 0.8`),
  and `[bans]` (`multiple-versions = "warn"`, `wildcards = "allow"`). A new crate
  under a licence not on the allow list fails there.
- **Node.** Run `pnpm install --frozen-lockfile` (`just desktop-install-ci`)
  locally before pushing. It reproduces CI's install exactly and is the only
  lockfile-drift check any of the four ecosystems enforces: it fails outright if
  `pnpm-lock.yaml` does not satisfy the manifests. Follow with
  `just desktop-check` / `just web-check` and the relevant build.
- **Flutter.** `just mobile-install`, then `just mobile-check` and
  `just mobile-test`.
- **Everything.** `just ci` runs the full local gate; `just check` runs the
  formatting, lint and static half without the builds and tests.

**One asymmetry worth knowing before you trust a green run.** pnpm's
`--frozen-lockfile` is the only lockfile-drift enforcement in this repository. No
`cargo --locked`, no `--offline`, and no `flutter pub get --enforce-lockfile`
appears in `Justfile`, `.github/workflows/ci.yml` or `lefthook.yml`. For Rust,
a stale `Cargo.lock` surfaces only indirectly, when a build rewrites it; for
Dart, `flutter pub get` re-resolves and rewrites `pubspec.lock` without
complaint. So on the Rust and Dart sides, **committing the regenerated lockfile
is a discipline, not something a gate will catch for you.**

## Roll back or clean up

- **Remove a Rust crate** by deleting its member-side line, then deleting the
  `[workspace.dependencies]` entry if no member still inherits it, then running a
  `cargo` command to prune `Cargo.lock`. A `[workspace.dependencies]` entry with
  no remaining consumer is dead configuration, not harmless.
- **Remove a Node package** by deleting it from the app's `package.json` and
  running `pnpm install` from the repository root so the shared lockfile is
  pruned. If the package was the reason an `overrides` or `patchedDependencies`
  entry existed in `pnpm-workspace.yaml`, remove that entry too, and delete the
  now-orphaned file under `patches/`.
- **Remove a Dart package** by deleting it from `mobile/pubspec.yaml` and running
  `just mobile-install` to rewrite `mobile/pubspec.lock`.
- **Abandon a change entirely** with `git checkout -- <manifest> <lockfile>` for
  the pair you touched, remembering that Rust has two independent pairs (root and
  `desktop/src-tauri`) and that reverting only one of them leaves the tree
  inconsistent in a way no check reports.
- **Retire a workaround when its condition is met.** The `[patch.crates-io]`
  entry, both `pnpm-workspace.yaml` overrides, the four `renovate.json` version
  holds and the four `deny.toml` advisory ignores each state, in their own
  comment or `description`, what would make them removable. Removing one when its
  condition is met is part of this task, not a separate cleanup project.

## See also

- `development/hermit.md` (`development-hermit`) -- what Hermit pins, at which
  version, and how the pin mechanism resolves. The canonical account; this node
  covers only the act of changing a pin.
- `development/prerequisites.md` (`development-prerequisites`) -- the toolchain a
  contributor needs before any of the commands above will run.
- `development/build.md` (`corpus-development-build`) -- compiling the workspace
  and each frontend, the step that consumes a dependency change and the place a
  bad one usually surfaces.
- `CONTRIBUTING.md` -- the prior-issue expectation for large dependency swaps.
- `launchpad/AGENTS.md` and
  `launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md` --
  the fork's upstream-file rule and its one dependency-adjacent exception.

## Boundary

This node does not describe:

- **A reference listing of what the repository depends on.** The set of crates,
  packages and Dart libraries, their versions and their purposes is lookup
  content; the manifests and lockfiles are the authority, and no reference-shaped
  corpus node exists for them.
- **How to acquire the underlying skill** of working in a Rust/pnpm/Flutter
  monorepo from scratch -- that would be a tutorial, a form the corpus has no
  template for.
- **Why the repository is split across four ecosystems**, or why the Tauri backend
  sits outside the root Cargo workspace. That is concept/explanation content; this
  node states the split as read from the manifests and stops there.
- **Responding to a disclosed vulnerability in a dependency.** Adding an advisory
  ignore to `deny.toml` is mentioned here only as something `cargo-deny check`
  reads; triage, severity assessment and the decision to accept an exposure are a
  different task and belong in their own node.
- **Resolving lockfile conflicts when merging from upstream.** No corpus node and
  no in-repository document covers it at this revision -- `launchpad/AGENTS.md`
  names an `upstream-intel/` directory for upstream tracking tooling, but that
  directory does not exist on disk here.
- **What Hermit is and how its symlink chain works** -- `development-hermit`
  covers that, and this node deliberately does not restate its pin table.

## Relationships

Three edges are declared, and all three targets were confirmed present on
`origin/launchpad` at the recorded revision, not merely in this worktree:

- `implements` -> `corpus-template-procedure`. This node takes the how-to shape
  that template prescribes; the template's own *Relationships* section names
  `implements` as the correct edge for a template instance, in preference to the
  weaker `references`.
- `references` -> `development-hermit`. The *Change a Hermit-pinned tool* sequence
  above assumes that node's account of what is pinned and how; it defers to it
  rather than duplicating it.
- `references` -> `corpus-development-build`. The build task is what consumes a
  dependency change and where a bad one usually appears; the two nodes are
  adjacent without either owning the other.

`debugging` and `development-prerequisites` are also merged and were considered.
Neither is targeted: `debugging` is about diagnosing a running relay, and this
node's dependency on `development-prerequisites` is the same ambient
"you need a toolchain" assumption every node in this directory shares, which is
not a claim-level dependency worth an edge.

## Scope and omissions

**This node covers** how a contributor adds, updates or removes a dependency in
each of this repository's four ecosystems -- Rust (root workspace and the
excluded `desktop/src-tauri` project), Node via the three-package pnpm workspace,
Flutter/Dart in `mobile/`, and Hermit-pinned developer tooling -- which manifest
and lockfile each change touches, how the pnpm override and patch mechanisms are
used here, what Renovate automates and what it deliberately holds, how
`cargo-deny` and `deny.toml` gate a Rust dependency, how to verify each change,
and how to roll one back.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What Hermit pins, and how its symlink/lazy-download mechanism works | `development/hermit.md` (`development-hermit`) |
| The toolchain a contributor needs installed before any command here runs | `development/prerequisites.md` (`development-prerequisites`) |
| Compiling the workspace and the frontends after a dependency change | `development/build.md` (`corpus-development-build`) |
| A reference listing of the repository's actual dependency set | The manifests and lockfiles directly; no corpus node exists |
| Triaging and responding to a disclosed vulnerability in a dependency | No corpus node found at this revision |
| Resolving lockfile conflicts on an upstream merge | Nothing found at this revision: no corpus node, and the `upstream-intel/` directory `launchpad/AGENTS.md` names does not exist on disk |
| Why the repository is split across four ecosystems | No concept/explanation node exists for this |

**Expected but not verified when this node was written:**

- **No dependency change was actually made and no install command was executed.**
  Every command above is cited to `Justfile`, `.github/workflows/ci.yml` or the
  manifest that defines it, read at the recorded revision -- not to a run. The
  procedure template this node implements asks that a step's evidence cite having
  exercised the workflow where practical; that bar is not met here, and the
  entry classes in this node's front matter say so rather than dressing a read
  command up as a tested one. Read the provenance ledger for what backs each
  claim: every `FACT` there cites a file opened at the recorded revision, and the
  one commit-only citation is the revision entry itself.
- **`cargo-deny check` was not run.** `deny.toml`'s three configured sections were
  read directly; which check families `cargo-deny check` runs *by default*, and
  therefore whether the absent `[sources]` section is checked with defaults or
  skipped, was not established from `cargo-deny`'s own documentation.
- **Whether the Renovate GitHub App is installed on `launchpad-26/buzz` could not
  be established from the repository.** `renovate.json` is present and is
  upstream-maintained (`git log` on the file shows only upstream-numbered pull
  requests), but a configuration file does not prove the bot runs against this
  fork. Treat the *Let Renovate do the routine updates* section as a description
  of the configured intent; confirm the bot is live before relying on it here.
- **The claim that a stale `Cargo.lock` or `pubspec.lock` can reach CI undetected
  is an `INFERENCE`, not a tested result.** It rests on the absence of any
  `--locked`/`--enforce-lockfile` flag in `Justfile`,
  `.github/workflows/ci.yml` and `lefthook.yml`; no run was constructed to
  demonstrate the gap. Other workflow files beyond `ci.yml` were not exhaustively
  searched for such a flag.
- **No `hermit install`-shaped command is documented anywhere in this
  repository.** `bin/README.hermit.md` states only that the symlinks are
  Hermit-managed. The instruction above to let Hermit rewrite `bin/` rather than
  hand-editing it follows from that statement; the exact command to add or bump a
  package was not found in-repo and is not asserted here.
- **The `id` follows the sibling nodes, not `standards/naming.md`'s MUST 3 read
  literally.** MUST 3 would give `corpus-development-dependency-management`; the
  two already-merged nodes in this directory carry `development-hermit` and
  `development-prerequisites`. This node matches its siblings so that three ids in
  one directory stay consistent. Which convention is correct corpus-wide is not
  resolved here, and no issue was filed for it as part of this task.
