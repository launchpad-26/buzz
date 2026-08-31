---
id: platforms-desktop-updater
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
  - statement: "node.schema.json's type enum names platforms as its own corpus surface, and the already-merged architecture/containers/desktop.md node carries type: architecture matching its own directory -- sibling node platforms-desktop-packaging (issue #1244, drafted but not yet merged into origin/launchpad) already follows the precedent of carrying type: platforms to match its own platforms/desktop/ directory, and this node follows the same convention for consistency."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "desktop/src-tauri/Cargo.toml declares tauri-plugin-updater version 2 as a dependency, and desktop/package.json declares @tauri-apps/plugin-updater ^2.10.0 as the corresponding JS binding."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:80"
      - "desktop/package.json:57"
  - statement: "desktop/src-tauri/build.rs reads BUZZ_UPDATER_PUBLIC_KEY and BUZZ_UPDATER_ENDPOINT, trims and filters them to non-empty, and emits cargo:rustc-cfg=buzz_updater_enabled only when both are present; the build script also declares the buzz_updater_enabled check-cfg and re-run triggers for both env vars."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/build.rs:13-14"
      - "desktop/src-tauri/build.rs:21"
      - "desktop/src-tauri/build.rs:107-118"
  - statement: "desktop/src-tauri/src/lib.rs registers the tauri_plugin_updater plugin on the Tauri builder only under #[cfg(buzz_updater_enabled)], and even then only when cfg!(debug_assertions) is false -- so the plugin is present at compile time solely in release builds where both updater env vars were set, and is omitted entirely from local/debug builds regardless of those env vars."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:208-214"
  - statement: "desktop/src-tauri/src/commands/updater.rs defines the is_auto_update_supported Tauri command, which on Linux returns whether the APPIMAGE environment variable is set (true only when running from a mounted AppImage) and unconditionally returns true on macOS and Windows; its doc comment states that Tauri's updater can find but not apply an update to a non-AppImage Linux install (e.g. a .deb), producing an 'invalid binary format' error at install time if that check is skipped."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/updater.rs"
  - statement: "is_auto_update_supported is registered in the Tauri invoke_handler list in lib.rs and exposed to the frontend via the isAutoUpdateSupported wrapper in desktop/src/shared/api/tauri.ts, which invokes the is_auto_update_supported command."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:853"
      - "desktop/src/shared/api/tauri.ts:1105-1107"
  - statement: "desktop/src/features/settings/hooks/use-updater.ts's useUpdater hook runs an initial background update check on mount and then re-checks every 6 hours (BACKGROUND_UPDATE_CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000) via window.setInterval, skipping a background check entirely while status is checking, available, downloading, installing, installing, ready, or manual-required (BACKGROUND_BLOCKED_STATES)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/use-updater.ts:23-31"
      - "desktop/src/features/settings/hooks/use-updater.ts:212-223"
  - statement: "use-updater.ts's runUpdateCheck calls check() from @tauri-apps/plugin-updater with a Cache-Control: no-cache header; when an update is found it calls isAutoUpdateSupported() before exposing any actionable state, setting status to available (and immediately starting a download) when auto-update is supported, or to manual-required with a GitHub releases URL and no retained update handle when it is not."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/use-updater.ts:124-176"
  - statement: "use-updater.ts exposes downloadUpdate (calls update.download(), sets status to ready) and installAndRelaunch (calls update.install(), then relaunch() from @tauri-apps/plugin-process), both guarded by in-flight refs so a second call while one is running is a no-op; an unavailable-plugin error (message containing 'plugin updater not found' or 'not initialized') is distinguished from a genuine up-to-date result and surfaced as status unavailable rather than error."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/use-updater.ts:39-44"
      - "desktop/src/features/settings/hooks/use-updater.ts:79-122"
      - "desktop/src/features/settings/hooks/use-updater.ts:177-200"
  - statement: "UpdaterProvider (desktop/src/features/settings/hooks/UpdaterProvider.tsx) wraps useUpdater() in a single React context, and desktop/src/main.tsx mounts exactly one UpdaterProvider around the whole App tree, so every consumer shares one check/download/install state machine and one 6-hour poll rather than each mounting its own."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/UpdaterProvider.tsx"
      - "desktop/src/main.tsx:95-98"
  - statement: "Three UI surfaces read the shared updater context: UpdateChecker.tsx (a Settings panel with a manual 'Check for Updates' button and per-state copy for every UpdateStatus variant), UpdateIndicator.tsx (a toolbar icon button shown only for available/downloading/installing/manual-required/ready, actionable only for ready and manual-required), and SidebarUpdateCard.tsx (a dismissible sidebar card shown only for ready, installing, or manual-required per shouldShowSidebarUpdateCard, with a manual-required variant linking to GitHub and a ready/installing variant that calls installAndRelaunch)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/UpdateChecker.tsx"
      - "desktop/src/features/settings/UpdateIndicator.tsx"
      - "desktop/src/features/settings/SidebarUpdateCard.tsx"
      - "desktop/src/features/settings/sidebarUpdateCardVisibility.ts"
  - statement: "desktop/src/features/settings/sidebarUpdateCardVisibility.test.mjs unit-tests shouldShowSidebarUpdateCard's state-to-visibility mapping, and desktop/tests/e2e/sidebar.spec.ts (around line 680) drives the mock Tauri bridge to inject an available update and asserts the observed command order is plugin:updater|download before plugin:updater|install, and that the sidebar card and toolbar copy update through checking, ready, and installing states."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/sidebarUpdateCardVisibility.test.mjs"
      - "desktop/tests/e2e/sidebar.spec.ts:680-764"
  - statement: "No dedicated unit test exists for use-updater.ts's own state machine (the check/download/install hook itself) or for the Rust is_auto_update_supported command; the only automated coverage found is the visibility-mapping unit test and the mock-bridge E2E spec listed above, both of which exercise the hook indirectly through UI surfaces rather than calling it or the Rust command directly."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='useUpdater|is_auto_update_supported', scope='desktop/src/**/*.test.*;desktop/src-tauri/src/**') -> no direct unit test found for either symbol, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "desktop/scripts/build-release-config.mjs writes plugins.updater.pubkey and plugins.updater.endpoints (a single-element array) into the release-only tauri.release.conf.json delta from the required BUZZ_UPDATER_PUBLIC_KEY and BUZZ_UPDATER_ENDPOINT environment variables, exiting non-zero if either is unset; this is the same env-var pair build.rs reads to decide whether to compile the updater plugin in at all."
    entry_class: FACT
    evidence:
      - "desktop/scripts/build-release-config.mjs:27-53"
  - statement: "desktop/scripts/generate-oss-latest-json.sh builds the manifest the updater plugin's endpoint serves: a JSON object with version, notes, pub_date, and a platforms map of platform-key to {signature, url} pairs assembled from CLI triples of platform-key:sig-file:archive-url, with no platform key hardcoded into the script itself."
    entry_class: FACT
    evidence:
      - "desktop/scripts/generate-oss-latest-json.sh"
  - statement: "scripts/promote-oss-desktop-release.sh validates a candidate updater-manifest.json (exact version match, all four expected platform keys present, non-empty string signatures, and URLs anchored to the exact desktop-v<version> release) before uploading it as latest.json onto the rolling buzz-desktop-latest GitHub release, refuses same-version promotion unless the manifest content is byte-identical, refuses any version downgrade, and re-verifies the currently-served manifest immediately before and after the single upload so a concurrent promotion cannot be silently clobbered."
    entry_class: FACT
    evidence:
      - "scripts/promote-oss-desktop-release.sh:35-46"
      - "scripts/promote-oss-desktop-release.sh:53-77"
  - statement: "RELEASING.md states that publishing the desktop-v<version> release does not by itself expose it to in-app auto-update, and that buzz-desktop-latest's latest.json -- the file the updater plugin's configured endpoint serves -- changes only through the manually dispatched Promote OSS Desktop Auto-Update workflow, which requires the version being promoted to be strictly newer than the one currently live; RELEASING.md's own troubleshooting section for \"Auto-updater reports 'no update available'\" says to verify that release exists with a manifest covering all four platform keys."
    entry_class: FACT
    evidence:
      - "RELEASING.md:199-221"
      - "RELEASING.md:333-338"
  - statement: "RELEASING.md's release-lane prerequisites table lists BUZZ_UPDATER_PUBLIC_KEY (or SPROUT_UPDATER_PUBLIC_KEY) and TAURI_SIGNING_PRIVATE_KEY as required GitHub Actions secrets for the desktop release lane -- the public key is embedded into the release build via build-release-config.mjs, and the private key signs the updater archive Tauri produces when bundle.createUpdaterArtifacts is true."
    entry_class: FACT
    evidence:
      - "RELEASING.md:273-274"
  - statement: "Because architecture-containers-desktop already documents the desktop container as a whole (including the tauri.conf.json-derived bundle identifier and sidecar list) and relationships.schema.json defines part-of as 'source is a constituent section/child of target', this node's client-side update-check-and-apply mechanism is a constituent facet of that container rather than a sibling or superseding subject, so declaring part-of toward architecture-containers-desktop is the correct directionality among the schema's five relationship types -- the same directionality sibling node platforms-desktop-packaging already declares toward the same target."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
    confidence: 0.75
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Desktop platform: auto-updater

How the installed desktop app checks whether a newer version exists,
downloads it, and applies it -- the Tauri updater plugin, the build-time
gating that decides whether it is even compiled in, the client-side
check/download/install state machine, and the Linux AppImage-only constraint
on which builds can auto-update at all. This node documents the *client-side*
mechanism: how a running app discovers and applies an update. It does not
document how the update artifacts and the manifest it fetches are *built and
published* -- that is `platforms/desktop/packaging.md`'s subject (issue
#1244, a sibling task in this same batch, not yet merged into
`origin/launchpad` at the time this node was written).

## Responsibility

The updater's job is narrow: periodically ask a configured endpoint whether a
newer signed build exists, and if the current install can apply one in
place, download and install it without the user needing to find and run a
new installer manually. It has no say over what goes into a release or how
artifacts are signed -- it only consumes the manifest and archives that the
release pipeline (`platforms/desktop/packaging.md`'s subject) already
produced and published.

## Build-time gating: whether the plugin exists at all

The updater is not present in every build. Three layers decide whether it is
compiled in:

1. **`desktop/src-tauri/build.rs`** reads `BUZZ_UPDATER_PUBLIC_KEY` and
   `BUZZ_UPDATER_ENDPOINT` from the build environment, trims each to a
   non-empty string, and emits `cargo:rustc-cfg=buzz_updater_enabled` only
   when *both* are present. Local/dev builds normally have neither set, so
   the cfg flag is absent.
2. **`desktop/src-tauri/src/lib.rs`** registers
   `tauri_plugin_updater::Builder::new().build()` on the app builder only
   inside `#[cfg(buzz_updater_enabled)]`, and even then only when
   `cfg!(debug_assertions)` is `false` -- so the plugin is compiled into the
   binary solely for release builds built with both env vars set. A debug
   build never carries the plugin, regardless of the env vars.
3. **`desktop/scripts/build-release-config.mjs`** is what actually supplies
   `BUZZ_UPDATER_PUBLIC_KEY`/`BUZZ_UPDATER_ENDPOINT` during a real release
   build: it writes `plugins.updater.pubkey` and `plugins.updater.endpoints`
   (a one-element array) into the release-only `tauri.release.conf.json`
   config delta from those same two environment variables, and fails the
   build outright if either is unset. This is the same script
   `platforms/desktop/packaging.md` documents for its `bundle.createUpdaterArtifacts`
   and version-generation responsibilities; here it is cited only for the
   `plugins.updater` block it also writes.

The practical effect: `is_auto_update_supported` and the whole check/download
UI can run in any build (they are always compiled), but the underlying
`@tauri-apps/plugin-updater` JS calls only succeed against a real plugin in a
release build that had both secrets available. `use-updater.ts` treats a
missing plugin as an expected `unavailable` state (see below), not a crash.

## Client-side check, download, and install flow

`desktop/src/features/settings/hooks/use-updater.ts`'s `useUpdater` hook is
the single state machine every UI surface reads. Its `UpdateStatus` union has
nine states: `idle`, `checking`, `up-to-date`, `unavailable`, `available`,
`downloading`, `installing`, `ready`, `error`, and `manual-required` (which
also carries the target version and a GitHub releases URL).

- **When it checks.** One check runs on mount, and again every 6 hours
  (`BACKGROUND_UPDATE_CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000`) via
  `window.setInterval`. A background check is skipped outright while status
  is any of `checking`, `available`, `downloading`, `installing`, `ready`, or
  `manual-required` (`BACKGROUND_BLOCKED_STATES`), so a poll never interrupts
  an in-progress or already-surfaced update. A manual check (the Settings
  "Check for Updates" button) always runs, even mid-background-check, and
  requests that the background check's result be shown once it resolves.
- **The check itself.** `check({ headers: { "Cache-Control": "no-cache" } })`
  from `@tauri-apps/plugin-updater` queries the configured endpoint. If it
  returns an update, `isAutoUpdateSupported()` (the Tauri command backed by
  `is_auto_update_supported`) is checked *before* any actionable state is
  exposed -- the hook's own comment notes this ordering exists specifically
  so a Linux `.deb` install never briefly shows an "available" state a click
  could act on before the unsupported path takes over.
- **Two branches on that result.** If auto-update is supported, status
  becomes `available` and a download starts immediately
  (`downloadUpdate()` -> `update.download()` -> status `ready`). If not, the
  update handle is discarded (no install handle is retained for a build that
  will never install in-app) and status becomes `manual-required` with a
  link to `https://github.com/block/buzz/releases/latest`.
- **Applying it.** `installAndRelaunch()` calls `update.install()` then
  `relaunch()` from `@tauri-apps/plugin-process`. Both `downloadUpdate` and
  `installAndRelaunch` are guarded by in-flight refs, so a repeated call
  while one is already running is a no-op rather than a second concurrent
  attempt.
- **Distinguishing "no plugin" from "no update".** An error whose message
  contains `"plugin updater not found"` or `"not initialized"` is treated as
  `unavailable` (the plugin was never compiled in -- see *Build-time gating*
  above) rather than as a generic `error`, and is logged with
  `console.warn` for diagnosis. Any other thrown error becomes `error` with
  its message attached.

## Linux AppImage-only constraint

`is_auto_update_supported` (`desktop/src-tauri/src/commands/updater.rs`)
returns `true` unconditionally on macOS and Windows. On Linux it returns
whether the `APPIMAGE` environment variable is set -- present only when the
running binary was launched from a mounted AppImage. A `.deb` install has no
such variable, so Tauri's updater could locate a newer version but cannot
swap the binary in place, which the source comment says otherwise surfaces
as an "invalid binary format" error at install time. `use-updater.ts`'s
`manual-required` branch exists specifically to keep that failure from ever
being triggered.

## UI surfaces

Three components consume the one shared `UpdaterProvider` context (mounted
once, in `desktop/src/main.tsx`, wrapping the whole `<App />` tree):

| Component | Where | Shown when | Action |
|---|---|---|---|
| `UpdateChecker` | Settings panel | always (per-state copy for all nine statuses) | manual "Check for Updates" / "Retry" button; "Update Now" when `ready` |
| `UpdateIndicator` | Toolbar icon | `available`, `downloading`, `installing`, `manual-required`, `ready` only | clickable only for `ready` (install) and `manual-required` (open GitHub) |
| `SidebarUpdateCard` | Sidebar, dismissible | `ready`, `installing`, `manual-required` only (`shouldShowSidebarUpdateCard`) | "Click to update" / GitHub download link |

`shouldShowSidebarUpdateCard`
(`desktop/src/features/settings/sidebarUpdateCardVisibility.ts`) is a small,
independently unit-tested pure function; the sidebar/indicator components
themselves are covered end-to-end by
`desktop/tests/e2e/sidebar.spec.ts` (around line 680), which drives the mock
Tauri bridge to inject an available update and asserts the observed command
order is `plugin:updater|download` before `plugin:updater|install`, and that
the sidebar card and toolbar text progress through checking, ready, and
installing states as expected.

## Manifest and promotion (boundary with packaging)

The `latest.json` manifest `check()` fetches from the configured endpoint is
built by `desktop/scripts/generate-oss-latest-json.sh` (version, notes,
`pub_date`, and a `platforms` map of platform-key to `{signature, url}`) and
is not the same file as the per-release `updater-manifest.json` candidate
attached to a `desktop-v<version>` release. Per `RELEASING.md`, publishing
`desktop-v<version>` does **not** by itself expose that candidate to
in-app auto-update: a separate, manually dispatched **Promote OSS Desktop
Auto-Update** workflow (`scripts/promote-oss-desktop-release.sh`) validates
the candidate manifest (exact version, all four platform keys present,
non-empty signatures, URLs anchored to the exact release) and only then
overwrites `latest.json` on the rolling `buzz-desktop-latest` release --
refusing any version downgrade, and re-verifying the served file immediately
before and after its one write. Until that promotion runs, every already
installed client keeps polling the *previous* `latest.json` and reports
`up-to-date`. Building and publishing those artifacts in the first place is
`platforms/desktop/packaging.md`'s subject, not this node's; this node cites
the promotion script and manifest generator only for the shape and gating
the client-side `check()` call depends on.

## Boundary

This node does not describe:

- **How update artifacts are built, signed, and published** -- the Tauri
  bundler config, the four-platform CI build/sign/notarize matrix, and the
  two-release (`desktop-v<version>` / `buzz-desktop-latest`) publishing
  model are `platforms/desktop/packaging.md`'s subject (issue #1244, not yet
  merged at the time this node was written); this node cites its
  `build-release-config.mjs`, `generate-oss-latest-json.sh`, and
  promotion-script facts only where they bear on what the client fetches and
  when.
- **The desktop container's overall architecture** -- its Rust/React
  structure, relay-connection logic, and bundled sidecar processes -- is
  `architecture-containers-desktop`'s subject.
- **The end-to-end human release procedure** -- `just release-desktop`, the
  candidate PR and squash-merge gate, required secrets and rulesets -- is
  `RELEASING.md`'s subject; this node cites it only for the facts that bear
  on the updater mechanism itself.
- **Relay or mobile update mechanisms** -- out of scope for a desktop
  platform node; mobile has no equivalent in-app auto-updater per
  `RELEASING.md`.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the build-time env-var gating that decides whether the
updater plugin is compiled in, the plugin's registration in `lib.rs`, the
client-side check/download/install state machine in `use-updater.ts` and its
nine-state status model, the Linux AppImage-only auto-update constraint and
its `is_auto_update_supported` implementation, the three UI surfaces that
consume the shared updater state, and the manifest-and-promotion boundary
that separates this node from `platforms/desktop/packaging.md`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Building, signing, and publishing update artifacts; the two-release publishing model | `platforms/desktop/packaging.md` (issue #1244, sibling task, not yet merged) |
| The desktop container's overall architecture | `architecture-containers-desktop` |
| The end-to-end human release and promotion procedure, required secrets/rulesets | `RELEASING.md` |
| Relay and mobile release/update lanes | `RELEASING.md`'s own Relay/Mobile sections; not this node's subject |

**Expected but not verified when this node was written:**

- **No corpus node yet exists for `platforms/desktop/packaging.md`** on
  `origin/launchpad`. It is drafted locally (issue #1244, branch
  `task/1244-desktop-packaging`) and is cited here by name and by the source
  files it also inspects, but no `relationships` edge is declared toward it
  because it does not yet resolve on the branch this node targets.
- **`use-updater.ts`'s own state machine and the Rust
  `is_auto_update_supported` command have no dedicated unit test.** The only
  automated coverage found is `sidebarUpdateCardVisibility.test.mjs` (a pure
  visibility-mapping function, not the hook) and the mock-bridge E2E spec in
  `desktop/tests/e2e/sidebar.spec.ts`, both of which exercise the hook
  indirectly through UI rather than testing it or the Rust command in
  isolation.
- **No literal `BUZZ_UPDATER_ENDPOINT` value was found in the repository.**
  It is supplied as a CI secret/variable at release-build time
  (`RELEASING.md:273-274` names `BUZZ_UPDATER_PUBLIC_KEY`/
  `SPROUT_UPDATER_PUBLIC_KEY` and `TAURI_SIGNING_PRIVATE_KEY` as the
  corresponding secrets), so this node documents the gating mechanism rather
  than asserting a specific endpoint URL.
- **Whether a real desktop release has been checked, downloaded, and
  installed end-to-end via this exact code path outside of the mocked E2E
  spec was not checked** -- this node is grounded in the checked-in source
  and workflow definitions, not in an observed live update.
