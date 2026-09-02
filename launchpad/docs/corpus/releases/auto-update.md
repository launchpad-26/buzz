---
id: releases-auto-update
type: release
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The checked-in desktop/src-tauri/tauri.conf.json sets plugins.updater.endpoints to an empty array, so the base config this repository ships carries no update endpoint by default."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json"
  - statement: "desktop/src-tauri/build.rs reads BUZZ_UPDATER_PUBLIC_KEY and BUZZ_UPDATER_ENDPOINT, trims and treats an empty value as absent, and emits the rustc cfg buzz_updater_enabled only when both are present and non-empty."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/build.rs"
  - statement: "desktop/src-tauri/src/lib.rs registers Tauri's updater plugin (tauri_plugin_updater::Builder::new().build()) only inside a #[cfg(buzz_updater_enabled)] block, and even then only when cfg!(debug_assertions) is false -- so the plugin is present in the running app only in a release build compiled with both updater env vars set."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs"
  - statement: "desktop/scripts/build-release-config.mjs exits 1 if either BUZZ_UPDATER_PUBLIC_KEY or BUZZ_UPDATER_ENDPOINT is unset, and otherwise writes desktop/src-tauri/tauri.release.conf.json with plugins.updater.pubkey and plugins.updater.endpoints set from those env vars plus bundle.createUpdaterArtifacts: true; its own comment states Tauri's --config flag merges this file on top of the base config, and that Apple codesigning/notarization happen post-build via a separate action rather than a signingIdentity emitted here."
    entry_class: FACT
    evidence:
      - "desktop/scripts/build-release-config.mjs"
  - statement: "Every platform release job in .github/workflows/release.yml runs `node scripts/build-release-config.mjs` with BUZZ_UPDATER_PUBLIC_KEY sourced from the BUZZ_UPDATER_PUBLIC_KEY or SPROUT_UPDATER_PUBLIC_KEY repository secret and BUZZ_UPDATER_ENDPOINT hardcoded to https://github.com/block/buzz/releases/download/buzz-desktop-latest/latest.json."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: "release.yml's \"Generate unified latest.json\" step builds a manifest via desktop/scripts/generate-oss-latest-json.sh from each successful platform job's signature and archive download URL, refuses to proceed with fewer than three of the four platforms, and copies the resulting file into the versioned draft release as updater-manifest.json; generate-oss-latest-json.sh itself emits the shape {version, notes, pub_date, platforms: {<platform-key>: {signature, url}}}."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - "desktop/scripts/generate-oss-latest-json.sh"
  - statement: "RELEASING.md states desktop publishes two GitHub releases -- desktop-v<version> (the user-facing release with installers and the exact updater-manifest.json promotion candidate, whose publication does not by itself expose it through in-app auto-update) and buzz-desktop-latest (the rolling auto-update release whose latest.json changes only through the manual promotion workflow)."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md documents running the \"Promote OSS Desktop Auto-Update\" workflow from main with the exact stable X.Y.Z version to move a tested release onto the rolling manifest, states the workflow requires the version to be newer than the currently promoted version, that a same-version retry succeeds only when the manifest is identical, and that a downgrade is rejected; it also states withholding promotion leaves existing clients on the previous version, and that a bad promoted release is fixed by shipping and promoting a higher patch version rather than editing the manifest to point at an older version, because already-updated clients do not downgrade."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Troubleshooting section states that an auto-updater reporting \"no update available\" is diagnosed by verifying the buzz-desktop-latest release exists with a valid latest.json covering all four platform keys (darwin-aarch64, darwin-x86_64, linux-x86_64, windows-x86_64), and that a missing platform entry usually means that platform's release job failed."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: ".github/workflows/promote-oss-desktop-release.yml is a workflow_dispatch-only workflow that runs only when github.repository == 'block/buzz', fails immediately unless dispatched with github.ref == refs/heads/main, and delegates all validation and promotion logic to scripts/promote-oss-desktop-release.sh \"$VERSION\"."
    entry_class: FACT
    evidence:
      - ".github/workflows/promote-oss-desktop-release.yml"
  - statement: "scripts/promote-oss-desktop-release.sh requires the target desktop-v<version> release to be neither a draft nor a prerelease, requires its tag and its release's targetCommitish to resolve to the same commit SHA, requires it to carry an updater-manifest.json asset, and validates that asset's version field matches the requested version, its platforms object's keys equal exactly [\"darwin-aarch64\",\"darwin-x86_64\",\"linux-x86_64\",\"windows-x86_64\"], every platform has a non-empty string signature and a url starting with https://github.com/block/buzz/releases/download/desktop-v<version>/, and every referenced url's asset actually exists among the release's own assets."
    entry_class: FACT
    evidence:
      - "scripts/promote-oss-desktop-release.sh"
  - statement: "The same script downloads the currently-served buzz-desktop-latest release's latest.json, rejects a requested version lower than the current one (sort -V comparison) as a downgrade, accepts a same-version request only when the candidate manifest is byte-identical to the current one (cmp -s), re-downloads latest.json immediately before uploading to confirm its SHA-256 has not changed since the earlier read (guarding against a race with a concurrent promotion), uploads the validated manifest with gh release upload ... --clobber, and re-downloads the served copy afterward to confirm its SHA-256 matches what was uploaded, failing with a retry instruction on any mismatch rather than assuming success."
    entry_class: FACT
    evidence:
      - "scripts/promote-oss-desktop-release.sh"
  - statement: "desktop/src-tauri/src/commands/updater.rs's is_auto_update_supported Tauri command returns true unconditionally on macOS and Windows, and on Linux returns whether the APPIMAGE environment variable is set, because Tauri's updater can swap the running binary only for an AppImage install, not a .deb/.rpm install; this command is registered in the app's invoke_handler list in desktop/src-tauri/src/lib.rs."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/updater.rs"
      - "desktop/src-tauri/src/lib.rs"
  - statement: "desktop/src/features/settings/hooks/use-updater.ts's useUpdater hook calls the updater plugin's check() on mount and again every six hours (BACKGROUND_UPDATE_CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000), skipping a background check while status is checking/available/downloading/installing/ready/manual-required; when check() finds an update it calls isAutoUpdateSupported() before exposing any actionable state, and if that returns true it sets state \"available\" and immediately starts downloadUpdate() (moving to \"ready\" on success), while if it returns false it discards the update handle and sets state \"manual-required\" with a releaseUrl of https://github.com/block/buzz/releases/latest instead of attempting an in-app install."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/use-updater.ts"
  - statement: "use-updater.ts treats a caught error whose message contains \"plugin updater not found\" or \"not initialized\" as an \"unavailable\" status rather than a genuine error -- the path taken in a debug build, or any build where buzz_updater_enabled was never set, because the updater plugin was never registered with Tauri in that binary."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/hooks/use-updater.ts"
  - statement: "desktop/src/shared/api/tauri.ts's isAutoUpdateSupported() is a thin wrapper invoking the Rust is_auto_update_supported command, documented in its own comment as returning true on macOS, Windows, and Linux AppImage installs, and false on Linux non-AppImage packages such as .deb."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/tauri.ts"
  - statement: "desktop/src/testing/e2eBridge.ts implements mock IPC handlers for plugin:updater|check, plugin:updater|download, and plugin:updater|install, gated on an E2E mock config's mock.updateAvailable/mock.updateVersion/mock.updateDownloadDelayMs fields; three E2E specs (desktop/tests/e2e/sidebar-snapshot.spec.ts, sidebar.spec.ts, project-cold-start.spec.ts) reference this mock, exercising the update-available UI state rather than the real network/signature-verification path."
    entry_class: FACT
    evidence:
      - "desktop/src/testing/e2eBridge.ts"
      - "desktop/tests/e2e/sidebar-snapshot.spec.ts"
      - "desktop/tests/e2e/sidebar.spec.ts"
      - "desktop/tests/e2e/project-cold-start.spec.ts"
  - statement: "No test file under desktop/ matching an \"updater\"/\"update\" filename search exercises use-updater.ts's check/download/install state machine or the Rust is_auto_update_supported command directly against a real or staged endpoint; the matches found (sidebarUpdateCardVisibility.test.mjs, inbox-live-update.spec.ts, resolveCommunityUpdateResult.test.mjs, providerEnvVarUpdates.test.mjs, agent_models_update_tests.rs) cover unrelated subjects or the mocked UI-visibility path already covered above."
    entry_class: FACT
    evidence:
      - "find_files(root='desktop', name_glob='*updat*') -> desktop/src/features/settings/sidebarUpdateCardVisibility.test.mjs, desktop/tests/e2e/inbox-live-update.spec.ts, desktop/src-tauri/src/commands/agent_models_update_tests.rs, desktop/src/features/communities/resolveCommunityUpdateResult.test.mjs, desktop/src/features/agents/ui/providerEnvVarUpdates.test.mjs, plus the source files already cited above"
  - statement: "layers-configuration-desktop-configuration records that this OSS checkout's tauri.conf.json configures plugins.updater.endpoints as an empty array and that whether an internal Block-signed build (squareup/buzz-releases) overlays plugins.updater.endpoints or other tauri.conf.json fields with real values was explicitly not checked there, because that pipeline lives in a separate repository this corpus does not ingest."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/desktop-configuration.md"
  - statement: "Whether the private squareup/buzz-releases Buildkite pipeline promotes Block-signed desktop builds through this same BUZZ_UPDATER_ENDPOINT/BUZZ_UPDATER_PUBLIC_KEY and promote-oss-desktop-release.sh mechanism, a variant of it, or an unrelated process was not checked for this node either -- consistent with the same gap layers-configuration-desktop-configuration already recorded, and for the same reason: that pipeline is not in this repository."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md"
      - ".github/workflows/release.yml"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: layers-configuration-desktop-configuration
  - type: implements
    target: corpus-template-procedure
---

# Promote a desktop release to auto-update

This guide walks a release operator through promoting an already-published,
complete `desktop-v<version>` GitHub Release onto the rolling
`buzz-desktop-latest` auto-update release so existing Buzz desktop installs'
background updater offers it, and through confirming the promotion actually
reached clients.

## Before you start

- **The target `desktop-v<version>` release is already published**, not a
  draft and not a prerelease, and carries all four platform archives
  (`darwin-aarch64`, `darwin-x86_64`, `linux-x86_64`, `windows-x86_64`) plus an
  `updater-manifest.json` asset. Building and publishing that release is the
  subject of the sibling desktop-candidate/desktop-release nodes, not this
  one — this procedure only consumes it.
- **The build that produced it already ran with `BUZZ_UPDATER_PUBLIC_KEY` and
  `BUZZ_UPDATER_ENDPOINT` set.** Those two env vars are what make
  `desktop/src-tauri/build.rs` emit the `buzz_updater_enabled` compile-time
  flag, which is what makes `desktop/src-tauri/src/lib.rs` register Tauri's
  updater plugin in the compiled release binary — a debug build never
  registers it regardless of the env vars. Every job in `release.yml` already
  sets both (public key from the `BUZZ_UPDATER_PUBLIC_KEY` or
  `SPROUT_UPDATER_PUBLIC_KEY` secret; endpoint hardcoded to
  `https://github.com/block/buzz/releases/download/buzz-desktop-latest/latest.json`),
  so this is a property of how the release was built, not something this
  procedure sets up.
- **You need dispatch access** to run a `workflow_dispatch` workflow on
  `block/buzz`'s `main` branch. The workflow itself is also gated: it runs
  only in the `block/buzz` repository and only when dispatched from
  `refs/heads/main`.
- **No local tooling is required.** `gh` and `jq` run inside the workflow's
  own runner, not on your machine.

## Promote the release

1. From `main`, dispatch **Promote OSS Desktop Auto-Update**
   (`.github/workflows/promote-oss-desktop-release.yml`) with the exact
   stable version — for example
   `gh workflow run promote-oss-desktop-release.yml --repo block/buzz -f version=X.Y.Z`
   — or use the Actions UI.
2. The workflow runs `scripts/promote-oss-desktop-release.sh`, which validates
   the target release before touching anything: `desktop-v<version>` must be
   published (not a draft, not a prerelease); its tag and its release's
   `targetCommitish` must resolve to the same commit; it must carry an
   `updater-manifest.json` asset whose `version` matches the requested
   version, whose `platforms` object has exactly the four expected keys,
   whose every platform carries a non-empty `signature` and a `url` pinned to
   that same release's own download path, and whose every referenced asset
   actually exists on the release.
3. The script downloads the currently-served `buzz-desktop-latest` release's
   `latest.json` and compares versions: a version lower than the one already
   promoted is rejected as a downgrade; the same version is accepted only if
   the new manifest is byte-identical to what is already live; a higher
   version proceeds.
4. Immediately before uploading, it re-downloads `latest.json` and checks its
   SHA-256 has not changed since the read in step 3, so a concurrent
   promotion cannot be silently overwritten. It then uploads the validated
   manifest to the `buzz-desktop-latest` release with `--clobber`, and
   re-downloads it once more to confirm the copy now being served hashes to
   exactly what was uploaded — any mismatch fails the run with an instruction
   to retry, rather than assuming success.
5. Read the run's job summary: a successful promotion reports the promoted
   version, the tag's commit, the previous version, the manifest's SHA-256,
   and the actor who ran it.

## Confirm clients receive the update

6. Fetch
   `https://github.com/block/buzz/releases/download/buzz-desktop-latest/latest.json`
   and confirm its `version` is the one just promoted and that `platforms`
   still has all four keys (`darwin-aarch64`, `darwin-x86_64`,
   `linux-x86_64`, `windows-x86_64`). A missing key means that platform's
   `release.yml` job failed at build time — `release.yml` only requires three
   of four platforms to succeed before it will generate a manifest at all, so
   a manifest can reach this promotion step already missing one platform;
   check that platform's build run rather than re-running the promotion.
7. An installed client on an older version picks the update up on its own:
   `useUpdater` checks in the background on launch and again every six
   hours, or immediately via the app's manual "Check for Update" action. On
   macOS, Windows, and a Linux AppImage install, a found update downloads and
   installs automatically (`is_auto_update_supported` returns `true`); on a
   Linux `.deb`/`.rpm` install it returns `false` and the app instead shows a
   manual-download prompt linking to
   `https://github.com/block/buzz/releases/latest`, because Tauri's updater
   cannot swap the running binary for a non-AppImage Linux package.

**If something is wrong after promoting:** do not edit `latest.json` to point
back at an older version — clients that already updated will not downgrade.
Ship and promote a higher patch version instead. Withholding promotion in the
first place (not running this procedure) simply leaves existing clients on
whatever they already have; nothing changes until step 1 runs.

## See also

- `RELEASING.md` — the full three-lane release process (desktop, relay,
  mobile) this procedure's prerequisite release comes from.
- `layers-configuration-desktop-configuration` — the static
  `tauri.conf.json`/`tauri.windows.conf.json` configuration surface,
  including the placeholder empty `updater.endpoints` this node explains the
  build-time override for.
- `architecture-containers-desktop` — the desktop container's place in the
  wider system and its own pointer to `RELEASING.md`.

## Boundary

This node does not describe:

- **Building or publishing `desktop-v<version>` itself** — the candidate
  build, versioned draft creation, per-platform code signing and
  notarization, and CHANGELOG-driven release notes are the sibling
  desktop-candidate/desktop-release nodes' subject, not this one.
- **The relay or mobile release lanes**, which use entirely separate tags,
  workflows, and — for mobile — a private Buildkite pipeline with no GitHub
  Release or auto-update mechanism of its own.
- **How Tauri's updater plugin works internally**, or the generic shape of a
  Tauri updater manifest in the abstract — Tauri's own documentation covers
  that; this node covers only how this repository configures and operates
  it.
- **Internal, Block-signed desktop builds published via the private
  `squareup/buzz-releases` Buildkite pipeline.** Whether that pipeline reuses
  this same endpoint/key/promotion mechanism, a variant of it, or something
  else entirely was not established here — see *Scope and omissions*.

## Relationships

- `references` → `architecture-containers-desktop`: the desktop container
  node this procedure's release artifacts belong to, and which already
  points readers at `RELEASING.md`.
- `references` → `layers-configuration-desktop-configuration`: the static
  `tauri.conf.json` configuration surface whose placeholder empty
  `updater.endpoints` this node explains the build-time override for,
  without restating that node's own content.
- `implements` → `corpus-template-procedure`: this node is a how-to-shaped
  instance of that template.

Checked against `origin/launchpad` immediately before finalizing front
matter: all three targets (`architecture-containers-desktop`,
`layers-configuration-desktop-configuration`, `corpus-template-procedure`)
are present in the corpus tree at the recorded revision.

## Scope and omissions

**This node covers:** how a desktop build becomes capable of auto-updating
at compile time (the `buzz_updater_enabled` gate and its two env vars), how a
published `desktop-v<version>` release is promoted onto the rolling
`buzz-desktop-latest`/`latest.json` auto-update manifest, exactly what the
promotion script validates and guarantees, how to confirm a promotion
succeeded and reached clients, and how the shipped client behaves once an
update is available or unavailable — including the Linux AppImage/`.deb`
split and the debug-build/no-endpoint fallback state.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Building/publishing `desktop-v<version>` itself | sibling desktop-candidate/desktop-release nodes (issues #1292/#1293) |
| The relay and mobile release lanes | `RELEASING.md`; not this node's surface |
| Tauri's updater plugin internals in the abstract | Tauri's own documentation |
| Internal Block-signed build promotion via `squareup/buzz-releases` | not ingested by this corpus |

**Expected but not verified when this node was written:**

- **No automated test was found that exercises the real `check()` /
  `download()` / `install()` flow against a live or staged endpoint.** Three
  E2E specs exercise the mocked `plugin:updater|*` IPC handlers in
  `e2eBridge.ts` for update-available UI states; none of them drive the
  network request, the signature verification Tauri's updater performs, or
  an actual binary swap.
- **Whether `squareup/buzz-releases`' internal pipeline promotes Block-signed
  builds through this same mechanism, a variant of it, or something else
  entirely was not checked** — that pipeline lives in a separate repository
  this corpus does not ingest, the same gap `layers-configuration-desktop-configuration`
  already recorded for the static config file.
- **Whether a promoted `latest.json` has ever been exercised end-to-end
  against a real installed client as part of CI** (as opposed to manual
  post-release verification) was not found one way or the other.
