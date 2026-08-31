# Plan: issue #1244 — document platforms/desktop/packaging.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`);
  this is the first node under `platforms/`.
- `architecture/containers/desktop.md` (id `architecture-containers-desktop`,
  `type: architecture`) already documents the desktop container as a whole and
  exists on `origin/launchpad` — a valid `part-of` target.
- `node.schema.json`'s `type` enum already names `platforms` as its own corpus
  surface, distinct from `architecture`/`implementation`; the merged
  `architecture/containers/desktop.md` node's `type: architecture` matches its
  own directory, so `platforms/desktop/packaging.md` takes `type: platforms`
  by the same directory-matches-surface precedent.
- The real packaging/bundling mechanism (Tauri bundler config, per-platform
  overrides, version-patch and release-config-generation scripts, sidecar
  staging, the four-platform `release.yml` build matrix, AppImage
  post-processing, and `RELEASING.md`'s desktop lane narrative) was read
  directly — see evidence citations in the drafted node.

## STEP 1 — Confirm no existing node covers this subject

Enumerated `origin/launchpad`'s corpus tree; no `platforms/` node exists, so
this is a new node, not an update.

## STEP 2 — Investigate the real packaging/bundling mechanism

Read: `desktop/src-tauri/tauri.conf.json`, `tauri.windows.conf.json`,
`desktop/scripts/set-version-from-tag.mjs`, `build-release-config.mjs`,
`scripts/bundle-sidecars.sh`, `desktop/scripts/fix-appimage.sh`,
`.github/workflows/release.yml` (setup/release/release-macos-x64/
release-linux/release-windows/assemble-manifest jobs), and `RELEASING.md`.

## STEP 3 — Draft `launchpad/docs/corpus/platforms/desktop/packaging.md`

`id: platforms-desktop-packaging`, `type: platforms`, `status: draft`,
`origin: launchpad`. Body: responsibility, base/platform bundler config,
version+release-config generation, the four-platform CI build/sign/notarize
matrix, AppImage post-processing, publishing (`desktop-v<version>` vs
`buzz-desktop-latest`), boundary, relationships (`part-of` the desktop
container node), scope and omissions.

## STEP 4 — Validate

Run the corpus unit tests, then temporarily stash the new file and confirm
`validate.py` still reports the same pre-existing 21 FAILs before restoring it.

## STEP 5 — Commit

Per the batch's fixed two-call commit gate sequence.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- New node contributes zero *new* `validate.py` FAIL lines (`UNVERIFIED` notices expected/fine).
- Exactly one hand-authored canonical document created.

## OPEN

- Whether a `references` edge back to `corpus-template-component` or
  `corpus-template-architecture-component` is warranted is left undeclared:
  neither template's own guidance requires it, and this node does not
  strictly follow either template's skeleton (packaging is a platform-level
  mechanism, not a single crate or a container decomposition diagram).

## LEFT OUT

- The desktop app's other platform-level mechanisms (`tauri.md`, `react.md`,
  `updater.md`, `secure-key-storage.md`, etc.) are separate, already-filed
  sibling tasks (#1245, #1250, #1251, #1248, ...) — not folded into this node.
- Internal/private release infrastructure (Buildkite pipelines, Block-signed
  build suffixes) documented by `buzz-releases`/`sprout-oss` is out of scope;
  this node covers only what is visible and verifiable in this OSS repository.
