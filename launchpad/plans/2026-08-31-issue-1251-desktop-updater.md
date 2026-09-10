# Plan: issue #1251 — corpus node platforms/desktop/updater.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist on `origin/launchpad` at
  `131b02f989684117d9ab1dd426f1673fa638e523` except for the sibling task
  branches (`task/1244-desktop-packaging`, etc.) that have not yet merged.
  `platforms-desktop-packaging` (issue #1244) is drafted locally on branch
  `task/1244-desktop-packaging` but is **not** on `origin/launchpad`, so it is
  not a valid `relationships` target for this node yet.
- `architecture-containers-desktop` (`launchpad/docs/corpus/architecture/containers/desktop.md`)
  **is** on `origin/launchpad` and documents the desktop container as a whole.
  Sibling node `platforms-desktop-packaging` already declares
  `part-of: architecture-containers-desktop`; this node follows the same
  precedent since it also decomposes one facet of that container.
- No `platforms` template exists yet (per `AGENTS.md`'s own "Scope and
  omissions" table, per-type templates are somewhere in #1307-#1351,
  unlanded). Sibling node `platforms-desktop-packaging` used `type: platforms`
  with a component-shaped body (Responsibility / Boundary / Relationships /
  Scope and omissions) as its own convention in the absence of a template.
  This node follows that same convention for consistency, matching this
  issue's DoD language ("States responsibility and well-defined
  interface/boundary", "Names dependencies and collaborators", "Links source
  implementation and tests", "Explains only component-level behavior").
- The mechanism itself is real and located:
  - `desktop/src-tauri/Cargo.toml:80` — `tauri-plugin-updater = "2"`.
  - `desktop/package.json:57` — `@tauri-apps/plugin-updater` JS binding.
  - `desktop/src-tauri/build.rs:107-118` — emits `cargo:rustc-cfg=buzz_updater_enabled`
    only when both `BUZZ_UPDATER_PUBLIC_KEY` and `BUZZ_UPDATER_ENDPOINT` are set.
  - `desktop/src-tauri/src/lib.rs:208-214` — registers the updater plugin only
    under `#[cfg(buzz_updater_enabled)]` and only in release builds
    (`cfg!(debug_assertions)` short-circuits it out locally).
  - `desktop/src-tauri/src/commands/updater.rs` — `is_auto_update_supported`,
    a Tauri command gating the Linux AppImage-only auto-update path.
  - `desktop/src/features/settings/hooks/use-updater.ts` — the client-side
    check/download/install state machine (`check()` from
    `@tauri-apps/plugin-updater`, 6-hour background poll, `manual-required`
    branch for non-AppImage Linux).
  - `desktop/src/features/settings/hooks/UpdaterProvider.tsx`,
    `desktop/src/main.tsx:95-98` — single app-wide provider instance.
  - `desktop/src/features/settings/UpdateChecker.tsx`,
    `UpdateIndicator.tsx`, `SidebarUpdateCard.tsx`,
    `sidebarUpdateCardVisibility.ts` (+ its unit test) — the three UI surfaces
    consuming the shared state.
  - `desktop/scripts/build-release-config.mjs` — writes
    `plugins.updater.pubkey`/`.endpoints` into the release-only Tauri config
    delta.
  - `desktop/scripts/generate-oss-latest-json.sh`,
    `scripts/promote-oss-desktop-release.sh` — how the `latest.json` manifest
    the updater plugin fetches is built and promoted.
  - `desktop/tests/e2e/sidebar.spec.ts` (around line 680) — the one real E2E
    test exercising the check → download → install flow through the mock
    Tauri bridge.
  - No dedicated unit test exists for `use-updater.ts` itself or for the Rust
    `is_auto_update_supported` command — confirmed by search, not assumed.

## STEP 1 — Draft front matter and provenance

Front matter: `id: platforms-desktop-updater`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
operator]`, one commit-citation FACT for the recorded revision, then one
evidence entry per substantive claim (build-time gating, plugin registration,
client state machine, manifest shape/promotion, AppImage-only Linux
constraint, UI surfaces, test coverage gap). `relationships: [{type: part-of,
target: architecture-containers-desktop}]`.

**Done when:** front matter validates against `node.schema.json`'s shape by
inspection (required fields present, no extra fields, evidence entries
correctly classified).

## STEP 2 — Write the body

Sections: title, Responsibility, Build-time gating (env vars → cfg flag →
plugin registration), Client-side check/download/install flow, Manifest
shape and promotion (linking to the packaging node's territory without
duplicating it), Linux AppImage-only constraint, UI surfaces, Boundary,
Relationships, Scope and omissions (including the untested `use-updater.ts`
gap as "expected but not verified").

**Done when:** every DoD bullet in issue #1251 is satisfied and every claim
traces to a file actually opened this session.

## STEP 3 — Run the corpus test suite, then commit

Run the unittest command as its own sole Bash call, then `git add` + `git
commit -s`.

**Done when:** tests report `OK` and the commit succeeds (or the documented
retry-once-then-BLOCKED path is followed).

## STEP 4 — Verify

Re-diff against the DoD checklist, re-open every cited file, confirm removing
the new file and re-running `validate.py` reproduces the identical
pre-existing FAIL set (no new FAILs introduced).

**Done when:** the diff is re-read once end-to-end and the FAIL-set diff is
empty.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` must contribute zero *new* FAIL lines vs. the file-removed baseline.
- Commit must carry a verification stamp (retry once per finding #5 if refused).

## OPEN

- Whether `BUZZ_UPDATER_ENDPOINT`'s actual URL (e.g. pointing at the
  `buzz-desktop-latest` release's `latest.json`) is documented anywhere
  in-repo as a literal value — not found; it is env/secret-injected at build
  time, so the node states the mechanism, not a literal endpoint URL.

## LEFT OUT

- The packaging/bundling mechanism itself (Tauri bundler config, CI build
  matrix, codesign/notarize, AppImage post-processing) — owned by sibling
  task `platforms/desktop/packaging.md` (issue #1244), not yet merged.
- The end-to-end human release procedure (`just release-desktop`, candidate
  PR, tag ruleset) — owned by `RELEASING.md`, cited but not restated.
- Any relay/mobile update mechanism — out of scope for a desktop platform
  node.
