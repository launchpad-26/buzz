---
id: platforms-desktop-packaging
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum names platforms as its own corpus surface, distinct from architecture and implementation, and the already-merged architecture/containers/desktop.md node carries type: architecture matching its own directory -- the precedent this node follows by carrying type: platforms to match its own platforms/desktop/ directory."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "desktop/src-tauri/tauri.conf.json is the base Tauri bundler config: productName Buzz, identifier xyz.block.buzz.app, bundle.active true, bundle.targets \"all\", six externalBin sidecars (buzz-acp, buzz-agent, buzz-backend-kubernetes, buzz-dev-mcp, git-credential-nostr, buzz), an icon set including icon.icns/icon.ico, and a macOS-specific dmg block (background image, window size, app/Applications-folder icon positions) plus infoPlist/entitlements paths."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "desktop/src-tauri/tauri.windows.conf.json is a platform-specific override consumed by Tauri's own per-OS config-merging convention: it narrows bundle.externalBin to five sidecars, omitting buzz-backend-kubernetes, which is Linux/macOS-only per scripts/bundle-sidecars.sh."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.windows.conf.json"
  - statement: "desktop/scripts/set-version-from-tag.mjs validates a semver argument and writes it into three files in lockstep: desktop/package.json's version field, desktop/src-tauri/tauri.conf.json's version field, and desktop/src-tauri/Cargo.toml's version line -- the three manifests RELEASING.md names as desktop's version authority."
    entry_class: FACT
    evidence:
      - "desktop/scripts/set-version-from-tag.mjs"
      - "RELEASING.md:133"
  - statement: "desktop/scripts/build-release-config.mjs generates desktop/src-tauri/tauri.release.conf.json -- a release-only delta, not a full config -- containing bundle.macOS.minimumSystemVersion 10.15, bundle.createUpdaterArtifacts true, and plugins.updater.pubkey/endpoints sourced from the required BUZZ_UPDATER_PUBLIC_KEY and BUZZ_UPDATER_ENDPOINT environment variables (the script exits non-zero if either is missing). Its own source comment states Tauri merges --config on top of the base config via RFC 7396 and explicitly asserts the delta must never define bundle.externalBin, because a value there would replace the platform-specific sidecar list and null would silently delete it."
    entry_class: FACT
    evidence:
      - "desktop/scripts/build-release-config.mjs"
  - statement: "tauri.release.conf.json itself is not committed to the repository -- it is a build-time generated artifact written fresh by build-release-config.mjs in each release CI job -- confirmed by its absence from a repository-wide filename search while every release.yml build step still passes --config src-tauri/tauri.release.conf.json."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:138"
      - ".github/workflows/release.yml:576"
      - ".github/workflows/release.yml:720"
  - statement: "scripts/bundle-sidecars.sh stages the release-built sidecar binaries into desktop/src-tauri/binaries/ under the exact <name>-<target-triple>[.exe] filename Tauri's externalBin config expects, appends .exe and includes buzz-backend-kubernetes only when the target is not a Windows triple, and chmods the staged Unix binaries 755 because cp preserves a placeholder's non-executable mode on macOS."
    entry_class: FACT
    evidence:
      - "scripts/bundle-sidecars.sh"
  - statement: ".github/workflows/release.yml triggers only on pushes matching the desktop-v[0-9]* tag pattern, and its setup job re-validates the version is semver and calls scripts/verify-release-ref.sh to verify the tag-bound release source before any platform job runs."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:6-8"
      - ".github/workflows/release.yml:26-47"
  - statement: "release.yml runs four platform build jobs gated on the setup job: release (macOS arm64, runs-on macos-latest, pnpm tauri build --no-sign --features mesh-llm --config tauri.release.conf.json), release-macos-x64 (macOS Intel, the same command plus --target x86_64-apple-darwin), release-linux (runs inside a pinned ubuntu:24.04 container, pnpm tauri build --ci --bundles deb,appimage), and release-windows (runs-on windows-latest, pnpm tauri build --target x86_64-pc-windows-msvc --bundles nsis)."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:55-56"
      - ".github/workflows/release.yml:268-269"
      - ".github/workflows/release.yml:429-431"
      - ".github/workflows/release.yml:657-658"
      - ".github/workflows/release.yml:715-720"
  - statement: "Both macOS build jobs sign and notarize their unsigned DMG post-build via block/apple-codesign-action (reading OSX_CODESIGN_ROLE and CODESIGN_S3_BUCKET secrets and requiring id-token: write for OIDC), then re-sign the updater .tar.gz with pnpm tauri signer sign and verify the resulting app bundle with codesign --verify --deep --strict. Windows and Linux artifacts are never routed through that action -- the Windows NSIS installer is explicitly renamed with an _alpha-unsigned suffix before upload."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:60"
      - ".github/workflows/release.yml:173-217"
      - ".github/workflows/release.yml:347-386"
      - ".github/workflows/release.yml:749-753"
  - statement: "The release-linux job builds inside a digest-pinned ubuntu:24.04 container, installs a pinned appimagetool 1.9.1 and a pinned AppImage type2 runtime (both SHA256-verified) to avoid the tool's own mutable continuous tag, and after the Tauri build runs desktop/scripts/fix-appimage.sh on the produced AppImage before staging it."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:430"
      - ".github/workflows/release.yml:517-548"
      - ".github/workflows/release.yml:584-597"
  - statement: "desktop/scripts/fix-appimage.sh extracts the built AppImage, deletes a fixed set of bundled infra libraries (libwayland-*, libglib/gio/gobject/gmodule-2.0, libmount, libblkid, libselinux, libsystemd, libpcre2-8, libgst*, libzstd, libelf, libffi) that its own header comment documents as clashing with Mesa 25+/GLib 2.88 on newer host distros, installs a bash shim in front of the real buzz-desktop binary that strips bundle-pointing GST_PLUGIN_* environment overrides so the host's own GStreamer plugin search path is used, repacks the AppImage with the pinned appimagetool, and re-signs the AppImage (and any legacy .tar.gz sibling) with pnpm tauri signer sign when TAURI_SIGNING_PRIVATE_KEY is set. It fails loudly rather than silently no-op-ing if the bundler's file layout no longer matches its assumptions (missing libwayland-client, missing GST_PLUGIN_SYSTEM_PATH_1_0 reference in AppRun.wrapped, or a missing usr/bin/buzz-desktop binary)."
    entry_class: FACT
    evidence:
      - "desktop/scripts/fix-appimage.sh"
  - statement: "The assemble-manifest job in release.yml requires setup, release, release-macos-x64, release-linux and release-windows to all succeed, downloads every platform's staged artifacts, generates a single latest.json via desktop/scripts/generate-oss-latest-json.sh covering the four platform keys darwin-aarch64/darwin-x86_64/linux-x86_64/windows-x86_64, requires at least three of the four platforms to have succeeded, and creates or verifies a versioned desktop-v<version> GitHub Release (draft first, then published) carrying every staged installer/archive plus the generated updater-manifest.json."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:789-948"
  - statement: "RELEASING.md's Platform Support section states the release workflow builds two separate macOS DMGs (Apple Silicon and Intel, both codesigned and notarized), an unsigned Windows x64 NSIS installer (filename includes _alpha-unsigned), and Linux .deb and .AppImage packages; the .deb is explicitly noted elsewhere as not auto-updatable because Tauri's updater only supports AppImage on Linux, and the AppImage is post-processed by desktop/scripts/fix-appimage.sh, requiring the host to have GLib >= 2.72 (Ubuntu 22.04 or newer)."
    entry_class: FACT
    evidence:
      - "RELEASING.md:229-246"
      - ".github/workflows/release.yml:643"
  - statement: "RELEASING.md's 'What Gets Published' section states desktop publishes two separate GitHub releases: desktop-v<version> (the user-facing release carrying installers and the updater-manifest.json promotion candidate, whose publication alone does not expose it to in-app auto-update) and buzz-desktop-latest (the rolling auto-updater release, whose latest.json only changes through a separate manual 'Promote OSS Desktop Auto-Update' workflow that requires the new version to be strictly newer than the currently promoted one)."
    entry_class: FACT
    evidence:
      - "RELEASING.md:199-221"
  - statement: "RELEASING.md's desktop release lane is entered via just release-desktop <version>, which generates an immutable candidate PR from a clean main checkout; squash-merging that PR is the human authorization event, after which auto-tag-on-release-pr-merge verifies the merge against GitHub's PR identity and required-check provenance before creating the desktop-v<version> tag that triggers release.yml."
    entry_class: FACT
    evidence:
      - "RELEASING.md:17-23"
      - "RELEASING.md:48-69"
  - statement: "At the recorded revision, launchpad/docs/corpus/platforms/ does not exist on origin/launchpad's corpus tree, so this is the first node filed under that surface directory rather than an update to an existing sibling."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no platforms/ prefix present among the returned paths, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Because architecture/containers/desktop.md (id architecture-containers-desktop) already documents the desktop container as a whole -- including its bundle identifier and its externalBin sidecar list, drawn from the same tauri.conf.json this node cites -- and because relationships.schema.json defines part-of as 'source is a constituent section/child of target', this node's packaging/bundling mechanism is a constituent facet of that container rather than a sibling or superseding subject, so declaring part-of toward architecture-containers-desktop is the correct directionality among the schema's five relationship types."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
    confidence: 0.75
---

# Desktop platform: packaging and bundling

How the Buzz desktop app is turned from source into distributable,
platform-specific installers -- the Tauri bundler configuration, the
per-platform CI build/sign/notarize pipeline, and how the resulting artifacts
are published and (for updater-capable platforms) promoted to auto-update.
This node documents the packaging mechanism itself, not the desktop
container's overall architecture (`architecture-containers-desktop`) or the
human-facing release procedure narrated end-to-end in `RELEASING.md`, though
it cites both.

## Responsibility

Packaging turns a built desktop frontend/backend pair into the artifacts end
users install: two macOS `.dmg` files (Apple Silicon and Intel, both signed
and notarized), an unsigned Windows NSIS `.exe` installer, and Linux `.deb`
and `.AppImage` packages -- plus, for every platform except `.deb`, a signed
updater archive `buzz-desktop-latest`'s `latest.json` can point at. The base
shape (bundle targets, sidecars, icons, macOS DMG layout) is declared once in
`desktop/src-tauri/tauri.conf.json`; the pieces that must differ per platform
or per build kind (Windows' narrower sidecar list, the release-only updater
and minimum-OS-version overrides) are layered on top of it rather than
duplicated.

## Base bundler configuration

`desktop/src-tauri/tauri.conf.json` is the one base config every build reads.
Its `bundle` block sets `active: true` and `targets: "all"`, names six
`externalBin` sidecars (`buzz-acp`, `buzz-agent`, `buzz-backend-kubernetes`,
`buzz-dev-mcp`, `git-credential-nostr`, `buzz`), lists the app icon set
(including `icon.icns` for macOS and `icon.ico` for Windows), and carries a
macOS-only `dmg` block controlling the installer window's background image,
size, and the fixed pixel positions of the app icon and the
`Applications`-folder shortcut inside it. `macOS.infoPlist` and
`macOS.entitlements` point at `Info.plist` and `Entitlements.plist` alongside
it.

`desktop/src-tauri/tauri.windows.conf.json` is a Tauri-native per-OS
override: on a Windows build it narrows `bundle.externalBin` to five
sidecars, dropping `buzz-backend-kubernetes` -- a Linux/macOS-only sidecar per
`scripts/bundle-sidecars.sh`'s own target-triple branch.

## Version and release-config generation

Two generated-at-build-time steps run before any platform's Tauri build:

1. **`desktop/scripts/set-version-from-tag.mjs <version>`** validates the
   argument is semver and writes it into `desktop/package.json`,
   `desktop/src-tauri/tauri.conf.json`, and `desktop/src-tauri/Cargo.toml` in
   lockstep -- the three manifests `RELEASING.md` names as desktop's version
   authority.
2. **`desktop/scripts/build-release-config.mjs`** writes
   `desktop/src-tauri/tauri.release.conf.json`, a release-only *delta* (not a
   full config) containing `bundle.macOS.minimumSystemVersion: "10.15"`,
   `bundle.createUpdaterArtifacts: true`, and `plugins.updater.pubkey` /
   `.endpoints` sourced from the required `BUZZ_UPDATER_PUBLIC_KEY` and
   `BUZZ_UPDATER_ENDPOINT` environment variables -- the script fails if
   either is unset. This file is never committed; every release CI job
   regenerates it fresh, and every `pnpm tauri build` invocation in
   `release.yml` passes it via `--config`. Its own source comment documents
   why it must never set `bundle.externalBin`: Tauri merges `--config` over
   the base/platform config via RFC 7396, so a value there would silently
   replace the platform's sidecar list.

## CI build matrix

`.github/workflows/release.yml` triggers only on a `desktop-v[0-9]*` tag
push. A `setup` job re-validates the version is semver and verifies the
tag-bound release source before any platform job starts. Four platform jobs
then build in parallel, each invoking `set-version-from-tag.mjs`,
`build-release-config.mjs`, and `scripts/bundle-sidecars.sh` before its own
`pnpm tauri build --config src-tauri/tauri.release.conf.json`:

| Job | Runner | Bundles built | Notes |
|---|---|---|---|
| `release` | `macos-latest` | DMG (arm64) | `--no-sign --features mesh-llm`; signed/notarized post-build |
| `release-macos-x64` | `macos-latest` | DMG (Intel) | same, plus `--target x86_64-apple-darwin` |
| `release-linux` | `ubuntu:24.04` container | `deb`, `appimage` | AppImage post-processed by `fix-appimage.sh` |
| `release-windows` | `windows-latest` | `nsis` | unsigned; renamed with `_alpha-unsigned` suffix |

Both macOS jobs run their unsigned DMG through `block/apple-codesign-action`
(reading the `OSX_CODESIGN_ROLE` and `CODESIGN_S3_BUCKET` secrets, requiring
`id-token: write` for OIDC), replace the unsigned DMG with the signed and
notarized one, re-sign the updater `.tar.gz` with `pnpm tauri signer sign`,
and verify the resulting `.app` bundle with
`codesign --verify --deep --strict`. Windows and Linux artifacts never go
through that action; the Windows NSIS installer is explicitly renamed with an
`_alpha-unsigned` marker before upload.

## Linux AppImage post-processing

The `release-linux` job runs inside a digest-pinned `ubuntu:24.04` container
and installs a pinned `appimagetool` (release `1.9.1`) plus a pinned AppImage
type2 runtime, both SHA256-verified, to avoid depending on that tool's own
mutable `continuous` tag. After the Tauri build, it runs
`desktop/scripts/fix-appimage.sh` on the produced AppImage. (`RELEASING.md`'s
own "Platform Support" prose says this job "builds inside a `ubuntu:22.04`
container for broad GLIBC compatibility" -- the workflow file itself pins
`ubuntu:24.04`, so that one sentence in `RELEASING.md` has drifted from the
executable definition; this node follows `release.yml`, per this corpus's own
rule that current-behavior claims defer to executable evidence over
documentation.) That script:

- extracts the AppImage and deletes a fixed set of bundled infra libraries
  (`libwayland-*`, glib/gio/gobject/gmodule, `libmount`, `libblkid`,
  `libselinux`, `libsystemd`, `libpcre2-8`, `libgst*`, `libzstd`, `libelf`,
  `libffi`) that its own header comment documents as clashing with Mesa
  25+/GLib 2.88 on newer host distros;
- installs a bash shim in front of the real `buzz-desktop` binary that strips
  bundle-pointing `GST_PLUGIN_*` overrides so the host's own GStreamer
  plugin search path is used instead of an empty in-bundle one;
- repacks the AppImage with the pinned `appimagetool`, and re-signs the
  AppImage (and any legacy `.tar.gz` sibling) with `pnpm tauri signer sign`
  when `TAURI_SIGNING_PRIVATE_KEY` is set;
- fails loudly, rather than silently no-op-ing, if the bundler's file layout
  no longer matches its assumptions (a missing `libwayland-client`, a missing
  `GST_PLUGIN_SYSTEM_PATH_1_0` reference in `AppRun.wrapped`, or a missing
  `usr/bin/buzz-desktop` binary).

As a result, the shipped Linux AppImage relies on the host's own
Wayland/GStreamer/graphics stack and requires GLib >= 2.72 (Ubuntu 22.04 or
newer). The `.deb` package is not post-processed this way and, per
`RELEASING.md`, is not auto-updatable at all -- Tauri's updater supports only
the AppImage format on Linux.

## Publishing and auto-update promotion

An `assemble-manifest` job requires all four platform jobs (plus `setup`) to
succeed, downloads every platform's staged artifacts, and generates one
unified `latest.json` (via `desktop/scripts/generate-oss-latest-json.sh`)
covering the four platform keys `darwin-aarch64`, `darwin-x86_64`,
`linux-x86_64`, and `windows-x86_64` -- requiring at least three of the four
platforms to have succeeded before it will proceed. It then creates or
verifies a versioned `desktop-v<version>` GitHub Release (draft first,
published once every staged artifact plus the generated
`updater-manifest.json` is uploaded).

Per `RELEASING.md`, this is one of *two* GitHub releases in the desktop lane:

- **`desktop-v<version>`** -- the user-facing release with installers and the
  `updater-manifest.json` promotion candidate. Publishing it does **not**
  expose it to in-app auto-update.
- **`buzz-desktop-latest`** -- the rolling auto-updater release. Its
  `latest.json` changes only through a separate, manually triggered
  **Promote OSS Desktop Auto-Update** workflow, which requires the version
  being promoted to be strictly newer than the one currently live.

The lane is entered via `just release-desktop <version>` from a clean `main`
checkout, which opens an immutable candidate PR; squash-merging that PR is
the human authorization event, after which `auto-tag-on-release-pr-merge`
verifies the merge against GitHub's PR identity and required-check
provenance before creating the `desktop-v<version>` tag that triggers the
build matrix described above.

## Boundary

This node does not describe:

- **The desktop container's overall architecture** -- its Rust/React
  structure, its relay-connection logic, its bundled sidecar *processes* as
  runtime concerns -- which is `architecture-containers-desktop`'s subject,
  not this node's. This node cites that node's own `tauri.conf.json`-derived
  facts only where packaging and container architecture overlap
  (`externalBin`, the app identifier).
- **The end-to-end human release procedure** -- when to run
  `just release-desktop`, how the candidate PR and squash-merge gate work,
  what the required GitHub Actions secrets and rulesets are, and the internal
  Buildkite promotion pipeline documented in `buzz-releases`. `RELEASING.md`
  is the canonical source for that procedure; this node cites it for the
  facts that bear on the packaging mechanism itself and does not restate its
  full contents.
- **The auto-update client-side mechanics** -- how the installed Tauri app
  checks `latest.json` and applies an update -- which is a separate desktop
  platform concern (`platforms/desktop/updater.md`, a sibling task in this
  same batch) from how an update artifact is *built and published* in the
  first place.
- **Relay-side or mobile release lanes** (`just release-relay`,
  `scripts/mobile-release.sh`) and Block's internal, privately hosted
  signing/build infrastructure (`buzz-releases`, Buildkite) -- out of scope
  for an OSS-repository-grounded node, and not inspected while drafting this
  one.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the Tauri bundler configuration (base and per-platform),
the version-patch and release-config-generation scripts that run before every
release build, the four-platform CI build/sign/notarize matrix in
`release.yml`, the Linux AppImage post-processing pipeline, and how the
resulting artifacts are published across the two-release
(`desktop-v<version>` / `buzz-desktop-latest`) publishing model.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The desktop container's overall architecture | `architecture-containers-desktop` |
| The end-to-end human release procedure, required secrets/rulesets, and internal Buildkite promotion | `RELEASING.md` |
| Client-side auto-update mechanics (checking and applying `latest.json`) | `platforms/desktop/updater.md` (sibling task, not yet drafted at time of writing) |
| Relay and mobile release lanes | `RELEASING.md`'s own Relay/Mobile sections; not this node's subject |
| Block's internal, privately hosted signing/build infrastructure (`buzz-releases`, Buildkite) | Outside this OSS repository; not inspected |

**Expected but not verified when this node was written:**

- **No corpus node yet exists for `platforms/desktop/updater.md`, `tauri.md`,
  or any other sibling in this batch.** The boundary statements above name
  them as the intended owners of adjacent subjects based on this batch's own
  filed issue titles, not on a merged node's actual content.
- **Whether `desktop/scripts/generate-oss-latest-json.sh`'s exact `latest.json`
  schema matches what the Tauri updater plugin expects at runtime was not
  independently checked against Tauri's own updater documentation** -- this
  node cites the script's role in the pipeline (from `release.yml`'s own
  usage) rather than verifying its output format against an external
  specification.
- **Whether a real desktop release has been produced and successfully
  installed end-to-end since this exact pipeline shape was last changed was
  not checked** -- this node is grounded in the checked-in configuration and
  workflow definitions, not in an observed release run's logs or artifacts.
