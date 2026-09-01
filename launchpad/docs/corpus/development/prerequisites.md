---
id: development-prerequisites
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "CONTRIBUTING.md's 'Prerequisites' table states: Rust 1.88+ (via rustup), Node.js 24+ (required for desktop app commands and `just ci`), pnpm 10+ (required for desktop app commands and `just ci`), Flutter 3.41+ (required for the mobile app), Docker 24+ (for Postgres, Redis, MinIO), `just` at the latest version (`cargo install just`), `lefthook` 2.1.10 as a Hermit-pinned tool auto-installed by `just hooks` with no manual install needed, and that sqlx migrations are a workspace crate applied by `just migrate` from embedded migrations in `migrations/`."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md states this repository uses Hermit for toolchain pinning, activated once per shell session with `. ./bin/activate-hermit`; that Hermit pins Rust, `just`, Node, pnpm and other tools to the versions in `bin/`, downloading each on first use; and that `just bootstrap` (which `just setup` calls automatically) pre-downloads all required tools upfront."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "README.md's Quick start section states the same floor independently: 'You'll need Docker and Hermit (or Rust 1.88+, Node 24+, pnpm 10+, `just`).'"
    entry_class: FACT
    evidence:
      - "README.md"
  - statement: "Cargo.toml declares the workspace's `rust-version` as \"1.88.0\", the minimum supported Rust version (MSRV), matching the floor CONTRIBUTING.md's Prerequisites table states for Rust."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "rust-toolchain.toml pins `channel = \"1.95.0\"` with `profile = \"default\"` -- the exact Rust toolchain that rustup installs and that CI's Windows job explicitly reads from this same file -- which is a higher, exact version than the 1.88.0 MSRV floor Cargo.toml and CONTRIBUTING.md state."
    entry_class: FACT
    evidence:
      - "rust-toolchain.toml"
      - ".github/workflows/ci.yml"
  - statement: "Hermit's bin/node shim resolves to the pinned package file .node-24.15.0.pkg, i.e. Hermit pins Node.js to 24.15.0, above CONTRIBUTING.md's stated 24+ floor."
    entry_class: FACT
    evidence:
      - "bin/node"
  - statement: "Hermit's bin/pnpm shim resolves to the pinned package file .pnpm-11.4.0.pkg, i.e. Hermit pins pnpm to 11.4.0, above CONTRIBUTING.md's stated 10+ floor."
    entry_class: FACT
    evidence:
      - "bin/pnpm"
  - statement: "Hermit's bin/just shim resolves to the pinned package file .just-1.46.0.pkg, i.e. Hermit pins `just` to 1.46.0."
    entry_class: FACT
    evidence:
      - "bin/just"
  - statement: "Hermit's bin/lefthook shim resolves to the pinned package file .lefthook-2.1.10.pkg, matching CONTRIBUTING.md's stated 2.1.10 Hermit-pinned version exactly."
    entry_class: FACT
    evidence:
      - "bin/lefthook"
  - statement: "Hermit's bin/flutter shim resolves to the pinned package file .flutter-3.41.7.pkg, i.e. Hermit pins Flutter to 3.41.7, above CONTRIBUTING.md's stated 3.41+ floor."
    entry_class: FACT
    evidence:
      - "bin/flutter"
  - statement: "Hermit's bin/rustc shim resolves to the pinned package file .rustup-1.28.2.pkg -- Hermit manages the Rust toolchain by pinning rustup itself (version 1.28.2), which in turn honors rust-toolchain.toml's channel pin, rather than pinning a specific rustc build directly."
    entry_class: FACT
    evidence:
      - "bin/rustc"
  - statement: "mobile/pubspec.yaml constrains the Dart SDK to `^3.11.4` for the Flutter mobile app, in addition to the Flutter SDK version itself."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
  - statement: "CONTRIBUTING.md's 'Linux: Tauri system libraries' section states that Hermit pins language toolchains but not system libraries, and that on Linux the desktop app's Rust crates link against GTK and WebKitGTK, so `just ci` (and any `just desktop-tauri-*` recipe) needs an explicit apt-get install of: build-essential, curl, file, libasound2-dev, libayatana-appindicator3-dev, libgtk-3-dev, librsvg2-dev, libssl-dev, libwebkit2gtk-4.1-dev, libxdo-dev, patchelf, wget -- stated as the same list CI installs."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: ".github/workflows/ci.yml's Linux Tauri-dependency install step runs `sudo apt-get install -y --no-install-recommends` for exactly the packages build-essential, curl, file, libasound2-dev, libayatana-appindicator3-dev, libgtk-3-dev, librsvg2-dev, libssl-dev, libwebkit2gtk-4.1-dev, libxdo-dev, patchelf, wget -- confirming CONTRIBUTING.md's claim that its documented list matches CI's list."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "CONTRIBUTING.md states that without those Linux system libraries, `just ci` fails partway through `just check` with a pkg-config error of the form \"The system library `gdk-pixbuf-2.0` required by crate `gdk-pixbuf-sys` was not found\", and that a contributor touching only the relay, CLI, or other server-side crates can skip installing them and run the narrower recipes `just fmt-check`, `just clippy`, `just test-unit` and `just test` instead, none of which need GTK."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "Justfile's `bootstrap` recipe checks `command -v docker` after triggering Hermit's Rust/Node/pnpm downloads, and exits with \"Error: Docker is required but not installed\" plus a pointer to https://docs.docker.com/get-docker/ if Docker is absent -- Docker is a required prerequisite that Hermit does not pin or install."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "README.md's 'Windows prerequisites' section states that Buzz's agent shell tool runs commands under bash, already present on macOS and Linux; that on Windows a contributor needs to install Git for Windows, which ships Git Bash and 'is what buzz resolves at runtime'; and that `BUZZ_SHELL` can instead be set to the path of a different bash-compatible shell, with the agent's tool description updating automatically to reflect whichever shell is active."
    entry_class: FACT
    evidence:
      - "README.md"
relationships:
  - type: references
    target: corpus-template-reference
---

# Development prerequisites: reference

This node catalogues the tools and minimum versions a contributor or agent needs
installed before building or running Buzz from source, and the exact versions this
repository's own toolchain-pinning tool (Hermit) resolves them to today. It is linked
from `CONTRIBUTING.md`'s "Setting Up the Development Environment" section and from
`README.md`'s "Quick start", both of which state the same floor versions this node
catalogues, and both of which point a reader here for the authoritative table rather
than restating it. It does not cover how to run the setup commands themselves --
see *Boundary* below.

## Required tools and versions

CONTRIBUTING.md states each tool's minimum supported version; where this repository
also pins an exact version through Hermit (`bin/`), that pin is a stricter, current
snapshot of the same requirement, not a separate one. Docker and, on Windows, Git
Bash are required but are not Hermit-managed at all.

| Tool | Minimum (CONTRIBUTING.md) | Hermit-pinned version today | Notes |
|---|---|---|---|
| Rust | 1.88+ (`rustup`; also Cargo.toml's `rust-version = "1.88.0"`, the workspace MSRV) | `rustup` 1.28.2, which honors `rust-toolchain.toml`'s `channel = "1.95.0"` (`profile = "default"`) | 1.88.0 is a floor (MSRV); the toolchain actually installed by Hermit's pinned `rustup` is 1.95.0, a higher exact version. |
| Node.js | 24+ | 24.15.0 | Required for desktop app commands and `just ci`. |
| pnpm | 10+ | 11.4.0 | Required for desktop app commands and `just ci`. |
| Flutter | 3.41+ | 3.41.7 | Required for the mobile app. `mobile/pubspec.yaml` additionally constrains the Dart SDK to `^3.11.4`. |
| Docker | 24+ | Not Hermit-managed. `just bootstrap` checks `command -v docker` and exits with an install pointer if missing. | Runs Postgres, Redis, MinIO and the other local-dev services. |
| `just` | latest | 1.46.0 | Task runner. Install via `cargo install just` if not using Hermit. |
| `lefthook` | 2.1.10 (Hermit-pinned) | 2.1.10 | Git hooks. Auto-installed by `just hooks` -- no manual install needed. |
| sqlx migrations | workspace crate (no separate version prerequisite) | n/a | `just migrate` applies embedded migrations from `migrations/`. |
| Git Bash (Windows only) | Not in CONTRIBUTING.md's table; from README.md's "Windows prerequisites" | n/a | Buzz's agent shell tool runs commands under bash. macOS/Linux already have one; on Windows, install Git for Windows for Git Bash, or set `BUZZ_SHELL` to a different bash-compatible shell's path. |

Activating Hermit (`. ./bin/activate-hermit`) is what puts the pinned versions in the
table's middle column on `PATH`; without it, only the CONTRIBUTING.md floor in the
left column is enforced, by whatever toolchain is already on the contributor's
machine.

## Commands

Linux only, and only when building or checking anything that touches the desktop
Tauri app (`just ci`, any `just desktop-tauri-*` recipe). Not needed for
`just fmt-check`, `just clippy`, `just test-unit`, or `just test` on relay/CLI/
server-side crates alone.

```bash
sudo apt-get install -y --no-install-recommends \
  build-essential curl file libasound2-dev libayatana-appindicator3-dev \
  libgtk-3-dev librsvg2-dev libssl-dev libwebkit2gtk-4.1-dev libxdo-dev \
  patchelf wget
```

This is the exact list `.github/workflows/ci.yml`'s Linux Tauri-dependency step
installs. Other Linux distributions ship the same libraries under different package
names -- see the [Tauri prerequisites](https://tauri.app/start/prerequisites/) page
for the equivalents; that mapping is not re-derived here.

## Boundary

This node does not describe:
- Why these specific version floors were chosen, or the history behind them -- no
  concept/explanation node for this subject exists yet in this corpus.
- The step-by-step first-time setup procedure (`git clone`, `. ./bin/activate-hermit`,
  `just setup`, `just hooks`, what `just setup` does with `.env.example` and Docker
  services) -- that is `development/setup.md`'s subject (issue #868), not yet
  authored at the time this node was written.
- How Hermit itself works as a toolchain-pinning tool -- activation, its package
  cache, `bin/hermit.hcl`'s configuration -- that is `development/hermit.md`'s
  subject (issue #859), not yet authored at the time this node was written. This
  node only states which versions Hermit currently resolves each pinned tool to.
- Running any individual component (relay, desktop, mobile, web) once prerequisites
  are met -- those are `development/run-relay.md`, `development/run-desktop.md`,
  `development/run-mobile.md` and `development/run-web.md` (issues #865-#867, #869),
  none authored yet at the time this node was written.
- An API Reference for any of these tools' own CLIs.

## Relationships

- `references`: `corpus-template-reference` -- this node's shape (reference
  description / structured entries / optional Commands) follows that template.

No other relationships are declared. `development/setup.md` and `development/hermit.md`
would be the natural `references` targets for the two exclusions named above, but
neither exists as a corpus node on `origin/launchpad` at the recorded revision --
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` at commit
338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 shows no `development/` subtree at all, so a
`references` edge to either would be a hard validation error. This is a gap to close
once those sibling nodes merge, not a permanent absence.

## Scope and omissions

**This node covers** the tools and minimum versions required to build or run Buzz
from source (Rust, Node.js, pnpm, Flutter, Docker, `just`, `lefthook`, sqlx
migrations, and Windows-only Git Bash), the exact versions this repository's Hermit
pin currently resolves each of them to, and the Linux-only system libraries the
desktop Tauri build additionally needs.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The first-time setup procedure (`just setup`, `.env.example`, Docker services) | `development/setup.md`, issue #868, not yet authored |
| Hermit's own activation and pinning mechanism | `development/hermit.md`, issue #859, not yet authored |
| Running the relay, desktop, mobile or web app individually | `development/run-relay.md`, `development/run-desktop.md`, `development/run-mobile.md`, `development/run-web.md`, issues #865-#867 and #869, not yet authored |
| The Rust workspace / crate layout | `development/repository-layout.md` and `development/workspace.md`, issues #863 and #871, not yet authored |
| Non-Hermit-managed per-distribution Linux package name mappings | [Tauri's own prerequisites page](https://tauri.app/start/prerequisites/) |

**Expected but not verified when this node was written:**

- No formal manifest ledger row (per `corpus-plan`'s process, issues #626-#628) was
  found for this task anywhere in the repository -- `manifest.py` has no CLI and no
  persisted ledger file exists under this Feature (#619). `path`, `template`, `type`
  and `audiences` above were therefore derived directly from issue #860's own body
  (its DoD, and the `<!-- corpus-plan:v2 alias:DOC:development/prerequisites.md -->`
  marker naming the path) and from `node.schema.json`'s `type` enum, cross-checked
  against the reference template's own required-sections list, rather than read from
  a ledger row. This is a process gap in how this task was handed off, not a claim
  about the document's subject matter.
- Whether `pnpm 10+` in CONTRIBUTING.md's stated floor and Hermit's pinned `11.4.0`
  reflect a deliberate gap (Hermit intentionally ahead of the documented floor) or an
  undocumented drift was not resolved here -- both facts are stated as read, with no
  claim about why they differ.
- macOS-specific prerequisites beyond what CONTRIBUTING.md and README.md already
  state (which name no macOS-only tool beyond the shared floor) were not
  independently investigated.
