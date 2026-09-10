---
id: releases-versioning
type: release
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The root Cargo.toml's [workspace.package] table sets version = \"0.1.0\" and rust-version = \"1.88.0\"; every workspace member that writes version.workspace = true and rust-version.workspace = true inherits both values."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "crates/buzz-relay/Cargo.toml hardcodes its own version = \"0.2.1\" rather than inheriting the workspace version, while still inheriting rust-version.workspace = true for the MSRV field; RELEASING.md names crates/buzz-relay/Cargo.toml as the relay release lane's version authority."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "RELEASING.md"
  - statement: "crates/buzz-persona/Cargo.toml, crates/sprig/Cargo.toml, and examples/countdown-bot/Cargo.toml each hardcode version = \"0.1.0\" as a literal string rather than version.workspace = true, so their version happens to match the workspace default today but will not move if the workspace version is bumped."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/Cargo.toml"
      - "crates/sprig/Cargo.toml"
      - "examples/countdown-bot/Cargo.toml"
  - statement: "Every other workspace member crate, including launchpad/crates/knowledge, declares version.workspace = true and so tracks the root Cargo.toml's workspace.package version automatically."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/Cargo.toml"
      - "crates/buzz-cli/Cargo.toml"
      - "launchpad/crates/knowledge/Cargo.toml"
  - statement: "rust-toolchain.toml pins channel = \"1.95.0\" (profile = \"default\"), a higher version than the workspace's declared rust-version = \"1.88.0\" MSRV floor; no ADR or other decision record under launchpad/decisions/ addresses the relationship between the two numbers."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
      - "Cargo.toml"
  - statement: "The CI Windows job's own comment states its Rust toolchain (1.95.0, with clippy via profile = default) comes from the repo-root rust-toolchain.toml, confirming that CI builds against the pinned channel and not against the 1.88.0 MSRV floor declared in Cargo.toml."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:1117-1118"
  - statement: "A repository-wide search for cargo-semver-checks or a semver-checks-class tool finds no match in any Cargo.toml, GitHub Actions workflow, or the Justfile; every other 'semver' hit is either a GitHub Actions docker/metadata-action tag pattern (type=semver,pattern=...) or a shell regex validating that an input string is well-formed semver, never a check of API/source compatibility between versions."
    entry_class: FACT
    evidence:
      - "grep(pattern='semver', paths='.github/workflows/*.yml Justfile') -> matches only in docker.yml/sprig-image.yml/helm-chart.yml metadata-action patterns and format-validation regexes in linux-canary.yml/windows-canary.yml/signed-macos-canary.yml/release.yml/helm-chart.yml; zero matches for cargo-semver-checks"
  - statement: "desktop/package.json, desktop/src-tauri/tauri.conf.json, and desktop/src-tauri/Cargo.toml all carry version 0.5.20 at the recorded revision, independent of the Rust workspace's own 0.1.0 version."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "desktop/src-tauri/tauri.conf.json"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The Justfile's bump-desktop-version recipe updates desktop/package.json, desktop/src-tauri/tauri.conf.json, and the first version line of desktop/src-tauri/Cargo.toml together, then regenerates pnpm-lock.yaml and Cargo.lock, keeping the three desktop manifests in sync as one unit; bump-relay-version performs the equivalent single-file update for crates/buzz-relay/Cargo.toml. Neither the Justfile nor RELEASING.md defines a bump-mobile-version recipe."
    entry_class: FACT
    evidence:
      - "Justfile:823"
      - "Justfile"
      - "RELEASING.md"
  - statement: "RELEASING.md's Version Sources table states the release version authority for each lane: desktop/package.json and synchronized desktop manifests for desktop, crates/buzz-relay/Cargo.toml for relay, and the exact mobile-vX.Y.Z-rc.N remote git tag for mobile — and states plainly that mobile has no bump recipe or release-metadata PR."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "mobile/pubspec.yaml's version field reads 0.0.0+1 at the recorded revision."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
  - statement: "mobile/pubspec.yaml previously carried real, incrementing marketing versions (0.4.5+1 through 0.4.11+1 across a sequence of commits) until commit 21573b6cb9695b46c11885cfb63bc548bbcd55de, \"chore(mobile): lighter-weight release process (#2144)\", reset it to 0.0.0+1 in the same change that removed the Justfile's get-current-mobile-version, get-next-mobile-patch-version, bump-mobile-version, and release-mobile recipes and introduced the mobile-release-candidate.yml workflow and scripts/publish-mobile-release-candidate.sh."
    entry_class: FACT
    evidence:
      - "git_log(path='mobile/pubspec.yaml', follow=true) -> version bumped through six prior commits (0.4.5+1, 0.4.6-rc.1+1, 0.4.7+1, 0.4.8+1, 0.4.9+1, 0.4.11+1), then commit 21573b6cb9695b46c11885cfb63bc548bbcd55de changed it to 0.0.0+1"
      - "commit 21573b6cb9695b46c11885cfb63bc548bbcd55de"
  - statement: "RELEASING.md states that mobile/pubspec.yaml keeps 0.0.0+1 only as a valid, visibly non-release fallback for local development and validation builds, that release jobs always inject both version fields, and that Flutter receives the clean marketing version X.Y.Z from the candidate tag while Buildkite's monotonically increasing build number supplies the platform build number."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "scripts/publish-mobile-release-candidate.sh validates its version argument against a strict X.Y.Z semver-shaped regex, validates the candidate number as the next sequential rc.N for that version by listing existing mobile-vX.Y.Z-rc.* tags via the GitHub API, and creates an annotated tag named mobile-v<version>-rc.<candidate_number> at an exact, externally-supplied commit SHA."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh"
  - statement: ".github/workflows/auto-tag-on-release-pr-merge.yml's own header comment states the branch-prefix-to-tag-prefix mapping for PR-driven release lanes: version-bump/<v> to tag desktop-v<v>, relay-release/<v> to tag relay-v<v>, chart-release/<v> to tag chart-v<v>, and push-chart-release/<v> to tag push-chart-v<v>; mobile candidate tags are explicitly stated as not coming from merged PRs."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "The root AGENTS.md's ecosystem table states that squareup/buzz-releases produces 'Block-signed macOS + iOS builds with -block desktop version suffix'; this checkout has no access to the private squareup/buzz-releases repository, so the exact mechanism that applies the -block suffix is not independently verifiable from within block/buzz."
    entry_class: FACT
    evidence:
      - "AGENTS.md:37"
---

# Versioning across Buzz's release surfaces

This node catalogues **what version number authority governs each independently
releasable surface in this repository** — Rust workspace crates, the relay's own
release lane, the desktop app, and the mobile app — plus the two Rust-toolchain
numbers (MSRV floor and pinned compiler channel) that sit alongside them but answer a
different question. It complements `RELEASING.md`, which this node does not
duplicate: `RELEASING.md` describes *how to cut a release* per lane; this node
describes *where each lane's version number actually lives* and *what currently
disagrees or is left unexplained* between surfaces. The step-by-step release
procedures for each lane are separate corpus nodes (`releases/desktop-release.md`,
`releases/mobile-release.md`, `releases/relay-release.md`) and are out of scope
here; so is the git tag-naming scheme in its own right (`releases/release-tags.md`).

## Version authority by surface

| Surface | Version lives in | Current value (at recorded revision) | Notes |
|---|---|---|---|
| Rust workspace crates (default) | `Cargo.toml` `[workspace.package] version`, inherited via `version.workspace = true` | `0.1.0` | Applies to every workspace member crate except the three named below. |
| `buzz-relay` (relay release lane) | `crates/buzz-relay/Cargo.toml` `version` (hardcoded, not `version.workspace = true`) | `0.2.1` | `RELEASING.md` names this file as the relay lane's release version authority. Still inherits `rust-version.workspace = true` for its MSRV field even though its release `version` is independent. |
| `buzz-persona` | `crates/buzz-persona/Cargo.toml` `version` (hardcoded literal) | `0.1.0` | Matches the workspace default today by coincidence, not inheritance — will not move with a workspace version bump. |
| `sprig` | `crates/sprig/Cargo.toml` `version` (hardcoded literal) | `0.1.0` | Same as above. |
| `examples/countdown-bot` | `examples/countdown-bot/Cargo.toml` `version` (hardcoded literal) | `0.1.0` | Same as above; this is an example crate, not a released artifact. |
| Rust MSRV floor | `Cargo.toml` `[workspace.package] rust-version` | `1.88.0` | The declared minimum supported Rust version. |
| Pinned CI/dev toolchain | `rust-toolchain.toml` `channel` | `1.95.0` | Higher than the MSRV floor. CI's own comments confirm builds actually use this pinned channel, not the MSRV floor — see *Open question* below. |
| Desktop app | `desktop/package.json`, `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml` (kept in sync as one unit) | `0.5.20` | Independent of the Rust workspace version. Release tag: `desktop-v<version>`. |
| Mobile app | No file-based authority — the exact `mobile-vX.Y.Z-rc.N` remote git tag is the sole version record | pubspec fallback shows `0.0.0+1` | `mobile/pubspec.yaml`'s `version:` field is a deliberate non-release placeholder — see *Mobile is tag-only, not file-based* below. |
| Block-signed desktop builds (private pipeline) | Unknown from this checkout | — | Root `AGENTS.md` states these carry a `-block` suffix on the desktop version; the private `squareup/buzz-releases` repo that implements this is not accessible here. |

## Mobile is tag-only, not file-based

Every other surface above has a file a reader can open to find its current
version. Mobile does not, and this is a deliberate design, not an oversight:

- `mobile/pubspec.yaml` previously carried real, incrementing marketing versions
  (`0.4.5+1` through `0.4.11+1` across a run of ordinary commits). Commit
  `21573b6cb9695b46c11885cfb63bc548bbcd55de`, *"chore(mobile): lighter-weight
  release process (#2144)"*, reset it to `0.0.0+1` in the same change that
  deleted the Justfile's `get-current-mobile-version`, `get-next-mobile-patch-
  version`, `bump-mobile-version`, and `release-mobile` recipes, and added
  `.github/workflows/mobile-release-candidate.yml` plus
  `scripts/publish-mobile-release-candidate.sh`.
- `RELEASING.md` states this directly: `mobile/pubspec.yaml` keeps `0.0.0+1`
  only as a valid, visibly non-release fallback for local development and
  validation builds. Release jobs always inject both version fields — Flutter
  receives the clean marketing version `X.Y.Z` from the candidate tag, and
  Buildkite's monotonically increasing build number supplies the platform build
  number. So `0.0.0+1` is not "a version nobody set yet" — it is intentionally
  kept unreleasable so a local build can never be mistaken for a real one.
- The actual version authority is the annotated `mobile-v<version>-rc.<N>` git
  tag, created by `scripts/publish-mobile-release-candidate.sh`. That script
  validates its version argument against a strict `X.Y.Z` semver-shaped regex,
  resolves the next sequential `rc.N` for that version from existing
  `mobile-v<version>-rc.*` tags via the GitHub API, and creates the tag at an
  exact, externally supplied commit SHA — never the operator's local checkout.

## Commands

| Command | Description | Argument | Example |
|---|---|---|---|
| `just get-current-version` | Reads the current desktop version from `desktop/package.json` | none | `just get-current-version` |
| `just get-current-relay-version` | Reads the current relay version from `crates/buzz-relay/Cargo.toml` | none | `just get-current-relay-version` |
| `just get-next-minor-version` | Computes the next desktop minor version | none | `just get-next-minor-version` |
| `just get-next-patch-version` | Computes the next desktop patch version | none | `just get-next-patch-version` |
| `just get-next-relay-patch-version` | Computes the next relay patch version | none | `just get-next-relay-patch-version` |
| `just bump-desktop-version <version>` | Updates `desktop/package.json`, `desktop/src-tauri/tauri.conf.json`, and `desktop/src-tauri/Cargo.toml` together and regenerates lockfiles | `version` (X.Y.Z) | `just bump-desktop-version 0.5.21` |
| `just bump-relay-version <version>` | Updates `crates/buzz-relay/Cargo.toml` and regenerates `Cargo.lock` | `version` (X.Y.Z) | `just bump-relay-version 0.2.2` |
| `scripts/publish-mobile-release-candidate.sh` | Creates an annotated `mobile-v<version>-rc.<N>` tag at an exact commit SHA via the GitHub API | `version`, `candidate_number`, `target_sha` | invoked by `.github/workflows/mobile-release-candidate.yml`, not run directly |

There is intentionally no `bump-mobile-version` recipe — see *Mobile is tag-only,
not file-based* above.

## Open question: MSRV floor vs. pinned toolchain channel

`Cargo.toml` declares `rust-version = "1.88.0"` as the workspace's minimum
supported Rust version. `rust-toolchain.toml` pins `channel = "1.95.0"` — a
newer compiler than the declared floor. No ADR or other decision record under
`launchpad/decisions/` explains the relationship between the two numbers, and
CI's own comments (`.github/workflows/ci.yml:1117-1118`) confirm that builds
actually run against the pinned `1.95.0` toolchain, not against `1.88.0`. This
node records the discrepancy rather than resolving it: it is unclear from
current evidence whether `1.88.0` is a stale floor nobody has revisited, an
intentionally conservative lower bound with no enforcement mechanism, or
something else. No CI job in this repository builds specifically against the
`1.88.0` floor to verify it still compiles.

## No semantic-version compatibility tooling

A repository-wide search for `cargo-semver-checks` or an equivalent
API-compatibility checker finds none. Every other match for the word
`semver` in a workflow or the `Justfile` is one of two unrelated things: a
GitHub Actions `docker/metadata-action` tag pattern (for example
`type=semver,pattern={{version}},match=^relay-v(.*)$` in `docker.yml`), or a
shell regex confirming an input string is *well-formed* semver (for example
`.github/workflows/release.yml`'s `Invalid version ... Expected semver`
check). Neither of those establishes that a new version is *API-compatible*
with the previous one — this repository has no enforcement for that question
at all, for any of the Rust crates.

## Boundary

This node does not describe:

- **How to actually execute a release for any lane** — the ordered steps
  (branch, PR, merge, tag, build) belong to `releases/desktop-release.md`,
  `releases/mobile-release.md`, and `releases/relay-release.md`.
- **The git tag-naming scheme in its own right** (`desktop-v*`, `relay-v*`,
  `mobile-v*`, `chart-v*`, `push-chart-v*`, and their protection rules) —
  that is `releases/release-tags.md`'s subject. This node names the prefixes
  only where they are inseparable from a version authority claim (for
  example, the mobile tag *is* mobile's version authority).
- **What happens on rollback** — `releases/rollback.md`'s subject.
- **Release artifact or provenance attestation** — `releases/release-
  artifacts.md` and `releases/release-provenance.md`.
- **The exact mechanics of the `-block` desktop version suffix** — root
  `AGENTS.md` states it exists; the private `squareup/buzz-releases` repository
  that implements it is not accessible from this checkout, so this node
  reports the claim rather than verifying the mechanism.
- **Whether the MSRV/toolchain-channel divergence is intentional** — see
  *Open question* above; this node records the gap rather than resolving it.

## Relationships

None declared. `releases/` did not exist anywhere on `origin/launchpad` at the
recorded revision — this node was the first document in that directory to be
authored — and no other merged corpus node (checked via `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus`) documented
release-versioning subject matter that this node would `references`, `depends-on`,
or sit `part-of`. The sibling `releases/*` nodes named throughout this node have
since landed in this same integration, so the natural edges to them now resolve.
They are not added here: wiring them in now, under the pressure of a pre-merge fix
pass, risks the same kind of error this fix pass exists to catch. Adding them
belongs to a dedicated pass across the whole `development`/`governance`/`releases`
shelf once all 37 nodes are stable.

## Scope and omissions

**This node covers** the version-number authority for each independently
releasable surface in this repository (Rust workspace crates and their three
exceptions, the relay release lane, the desktop app, and the mobile app), the
two Rust-toolchain numbers that sit alongside them (MSRV floor and pinned
compiler channel) and their unresolved relationship, the commands that read or
bump those versions, and the absence of any semantic-version compatibility
enforcement tool.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Step-by-step release execution for desktop, mobile, relay | `releases/desktop-release.md`, `releases/mobile-release.md`, `releases/relay-release.md` |
| The git tag-naming scheme in its own right | `releases/release-tags.md` |
| Rollback procedure | `releases/rollback.md` |
| Release artifacts and provenance attestation | `releases/release-artifacts.md`, `releases/release-provenance.md` |
| Chart/push-gateway chart versioning (`chart-v*`, `push-chart-v*`) | Not investigated by this node; named only in the auto-tag workflow's own comment |
| The private `squareup/buzz-releases` `-block` suffix mechanism | Cross-repo, not accessible from this checkout |

**Expected but not verified when this node was written:**

- **Whether the MSRV floor (`1.88.0`) has ever actually been built against** —
  no CI job pins to it; this node reports the absence of such a job, not a
  test that the floor is genuinely still accurate.
- **This node was authored before any sibling `releases/` node had merged** —
  at the recorded revision `releases/` did not exist on `origin/launchpad` at
  all. All of the siblings this node's Boundary section names landed in the
  same integration as this node, so the Boundary table above points at real
  files rather than open issues; a future reader whose corpus has since
  drifted further should re-run `git ls-tree -r --name-only origin/launchpad
  -- launchpad/docs/corpus/releases` rather than trust this note indefinitely.
- **The exact `-block` suffix mechanism** — reported as an `AGENTS.md` claim
  above, not independently confirmed against the private pipeline that
  implements it.
- **Chart and push-gateway chart versioning** (`chart-v*`, `push-chart-v*`,
  `deploy/charts/buzz/Chart.yaml`) — noticed via the auto-tag workflow's own
  comment while gathering evidence for this node, but not independently
  investigated; excluded from scope rather than documented from a single
  glance.
