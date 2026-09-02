---
id: releases-release-provenance
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
  - statement: "The relay Docker image (both the release and debug variants, since the merge job's matrix includes both and the attestation step carries no variant-restricting `if`) gets a Sigstore-signed in-toto build-provenance attestation via `actions/attest-build-provenance`, pushed to the registry alongside the image and independently verifiable with `gh attestation verify oci://ghcr.io/launchpad-26/buzz:<tag> --owner launchpad-26`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "The relay's release-variant image additionally gets a second, custom attestation — predicate type `https://buzz.block.xyz/attestations/deployment-eligibility/v1` — binding the image digest to the exact source commit SHA, the qualifying CI run's id/attempt/URL, and the compatible Helm chart version, verifiable with `gh attestation verify oci://<image>@<digest> --repo block/buzz --signer-workflow block/buzz/.github/workflows/docker.yml --predicate-type https://buzz.block.xyz/attestations/deployment-eligibility/v1 --source-digest <source_sha>`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "Before any relay image manifest is merged and published, the `qualify` job requires a same-SHA GitHub Actions `ci.yml` run against that exact source commit to have completed successfully (checked via `scripts/select-qualified-ci-run.jq` against the GitHub API), polling up to 65 minutes and failing the publish outright if no successful run exists — this is what the deployment-eligibility attestation's qualification fields (run id/attempt/URL) actually certify."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "The merged relay manifest also carries plain OCI annotations (`org.opencontainers.image.revision`, `xyz.block.buzz.build.id`, `xyz.block.buzz.qualification.ci-run-id`/`ci-run-attempt`/`ci-conclusion`, `xyz.block.buzz.helm-chart.version`) set via `docker buildx imagetools create --annotation`, readable without any attestation tooling via `docker buildx imagetools inspect <ref> --format '{{json .Manifest}}'`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "The separate `ghcr.io/block/buzz-push-gateway` image gets its own independent `actions/attest-build-provenance` attestation in the same workflow, but that job is gated `if: github.repository == 'block/buzz'`, so this fork does not build or publish it."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "Every desktop platform job in `release.yml` re-verifies, via `scripts/verify-release-ref.sh`, that the checked-out commit is exactly the commit the `desktop-v<version>` tag points at before building anything — a mismatch fails the job outright rather than building from an unexpected ref."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - "scripts/verify-release-ref.sh"
  - statement: "The `desktop-v<version>` tag itself is only created after `auto-tag-on-release-pr-merge.yml` confirms the closed pull request's own GitHub API state (merged, exact head/base/repo/merge SHA) matches the webhook event, checks out a verifier script (`scripts/desktop_release.py`) from the candidate's frozen parent commit rather than from the candidate itself (so a release PR cannot alter the code that validates it), and confirms every one of a fixed list of required checks succeeded — matched by GitHub App/check-suite integration ID, not display name, and no later than the PR's `merged_at` timestamp so a post-merge rerun cannot retroactively satisfy it — before pushing the tag through the dedicated `buzz-release-bot` GitHub App."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
      - "scripts/verify-desktop-release-merge.sh"
  - statement: "The `desktop-v*`/`mobile-v*` tag namespace is additionally protected by repository ruleset 14378754, enforcing creation/update/deletion/non-fast-forward protection with `buzz-release-bot` as its sole always-bypass actor, so no other identity can create or move either tag family directly."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "Both macOS desktop DMGs (Apple Silicon and Intel) are code-signed and notarized via `block/apple-codesign-action`, then verified in the same job with `codesign --verify --deep --strict --verbose=2` and `spctl --assess --type execute --verbose=4` before being staged as release artifacts — a signature any macOS Gatekeeper check can independently re-verify after download."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: "The Windows desktop installer is explicitly built and shipped unsigned — `release.yml` renames it with an `_alpha-unsigned` marker before upload, and RELEASING.md states this plainly as a platform-support fact, not a defect being tracked elsewhere in this evidence set."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - "RELEASING.md"
  - statement: "The Linux `.deb` carries no OS-level package signature, and the `.AppImage` is only re-signed by `desktop/scripts/fix-appimage.sh` as part of producing the Tauri updater artifact (`AppImage.sig`), not as an independent Linux-native signature a package manager would check."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - ".github/workflows/release.yml"
  - statement: "Every desktop platform's updater archive (macOS `.app.tar.gz`, the Linux AppImage, the Windows NSIS installer) is signed with `TAURI_SIGNING_PRIVATE_KEY` via `pnpm tauri signer sign` / Tauri's own bundler signing, producing a detached `.sig` file that Tauri's built-in updater verifies client-side against the public key baked into the release config at build time (`BUZZ_UPDATER_PUBLIC_KEY` / `SPROUT_UPDATER_PUBLIC_KEY`) — this is the one provenance check that runs automatically, inside the app, on every update, rather than requiring a reader to run a command by hand."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - "RELEASING.md"
  - statement: "No step in `release.yml`, `desktop-release-candidate.yml`, `mobile-release-candidate.yml`, or `promote-oss-desktop-release.yml` produces a GitHub-native build-provenance attestation (`actions/attest-build-provenance` or equivalent), a SLSA provenance statement, or a published checksum/SHA256SUMS file for any desktop or mobile artifact — the relay's attestation mechanism has no counterpart on either of those two lanes in this repository."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - ".github/workflows/desktop-release-candidate.yml"
      - ".github/workflows/mobile-release-candidate.yml"
      - ".github/workflows/promote-oss-desktop-release.yml"
  - statement: "Mobile publishes only an immutable, annotated `mobile-vX.Y.Z-rc.N` git tag from the exact remote `main` commit, created solely through the `buzz-release-bot` GitHub App (workflow-dispatch restricted to `block/buzz`, ref must be `main`); the tag itself, not a build artifact, is the source-of-record this repository can verify, and the actual platform build/signing happens in the private Buildkite pipeline this repository cannot reach."
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml"
      - "RELEASING.md"
  - statement: "Android release builds sign with a CI-vended \"upload keystore\" (Google Play App Signing model: Play re-signs with its own retained app-signing key before distribution to devices) by default, or — when `BUZZ_ANDROID_RELEASE_SIGNING=external` — produce a deliberately unsigned bundle for Block's internal Cashkite APK Signer service; no keystore material is permitted inside the repository in either mode."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "The iOS Xcode project uses `CODE_SIGN_STYLE = Automatic` across its build configurations, deferring signing-identity selection to whatever Apple developer/distribution account and provisioning profile the actual build environment supplies — the repository itself carries no signing certificate or identity."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner.xcodeproj/project.pbxproj"
  - statement: "The private `squareup/buzz-releases` Buildkite pipeline produces Block-signed macOS and iOS builds carrying a `-block` desktop version suffix, distinct from the OSS artifacts this repository's own workflows build and publish."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Whether the private `buzz-releases`/Buildkite pipeline attaches any additional provenance mechanism (its own attestation, checksum manifest, or signing-transparency log) to the Block-signed desktop/mobile artifacts it produces was not established here — that pipeline's definition lives in a separate private repository this checkout cannot open."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "buzz/AGENTS.md ecosystem table (repo boundary: squareup/buzz-releases is a separate private repository)"
  - statement: "As of this node's recorded revision, no other release-surface corpus node (releases/desktop-candidate.md, releases/mobile-candidate.md, releases/release-artifacts.md, releases/release-tags.md — tracked by issues #1292, #1294, #1297, #1299, all open) is merged on `origin/launchpad`, and the `launchpad/docs/corpus/releases/` directory does not exist there yet, so this node declares no `relationships`."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no releases/ subtree present at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
---

# Verify a released Buzz artifact's provenance: how-to

How to check that a specific released binary, container image, or app bundle actually
came from this repository's CI at the commit it claims — not from somewhere else —
using the mechanism that artifact class actually has, since the three release lanes
(relay, desktop, mobile) do not share one.

## Before you start

- Know which artifact class you have: relay container image, desktop installer
  (macOS/Windows/Linux), or mobile app (Android/iOS). The verification steps differ
  per class and do not compose.
- For the relay steps: the GitHub CLI (`gh`) authenticated against `github.com`, since
  `gh attestation verify` calls GitHub's attestation API.
- For the desktop macOS steps: a macOS machine — `codesign` and `spctl` are
  macOS-native tools with no cross-platform equivalent shipped here.
- This guide verifies origin (did this specific artifact come from this repository's
  CI at this commit), not integrity-in-transit or that the artifact is malware-free.
  Those are different questions the mechanisms below only partly answer.

## Verify a relay image's provenance

1. Identify the image reference you want to check — a tag (`:launchpad`,
   `:sha-<full-commit>`, a semver tag) or, for the strongest guarantee, a digest
   (`@sha256:<digest>`). A tag can be moved later; a digest cannot.
2. Run the build-provenance check:
   ```
   gh attestation verify oci://ghcr.io/launchpad-26/buzz:<tag-or-digest> --owner launchpad-26
   ```
   A successful verification confirms a Sigstore-signed in-toto statement exists
   tying that exact image digest to a `docker.yml` run in this repository, without
   telling you anything about whether the underlying source passed CI.
3. For the additional guarantee that the image was built from a commit that passed
   this repository's own CI (not merely built successfully), verify the
   deployment-eligibility attestation instead, supplying the source commit SHA you
   expect:
   ```
   gh attestation verify oci://ghcr.io/block/buzz@<digest> \
     --repo block/buzz \
     --signer-workflow block/buzz/.github/workflows/docker.yml \
     --predicate-type https://buzz.block.xyz/attestations/deployment-eligibility/v1 \
     --source-digest <source_sha>
   ```
   The `merge` job that runs this step carries no `github.repository` gate, so this
   fork's own `ghcr.io/launchpad-26/buzz` images get this attestation too whenever
   `docker.yml` runs on a push to `launchpad` or a `relay-v*` tag — substitute
   `--owner launchpad-26` and drop `--repo block/buzz` if you are checking one of
   this fork's own images rather than upstream's.
4. To read the plain annotations without any attestation tooling:
   ```
   docker buildx imagetools inspect ghcr.io/launchpad-26/buzz:<tag> --format '{{json .Manifest.Annotations}}'
   ```
   Look for `org.opencontainers.image.revision` (source commit) and the
   `xyz.block.buzz.*` build/qualification annotations. Unlike the attestations
   above, these are unsigned metadata — trust them only as far as you trust whoever
   could have pushed to the registry.

**Success looks like:** `gh attestation verify` exits 0 and prints the attestation's
subject digest and signer workflow, matching what you expected.

## Verify a desktop macOS artifact's provenance

1. Download the `.dmg` from the `desktop-v<version>` GitHub release (not
   `buzz-desktop-latest`, which is the rolling auto-updater pointer, if you want a
   specific version).
2. Mount it and locate `Buzz.app`, then check the code signature and notarization:
   ```
   codesign --verify --deep --strict --verbose=2 /Volumes/Buzz/Buzz.app
   spctl --assess --type execute --verbose=4 /Volumes/Buzz/Buzz.app
   ```
   Both must succeed. This proves Apple notarized the exact binary you have — it does
   not by itself prove which commit built it.
3. To tie the artifact back to a source commit, rely on the release tag: the
   `desktop-v<version>` GitHub release's tag only exists because
   `auto-tag-on-release-pr-merge.yml` verified the merged PR's required checks and
   pushed it via `buzz-release-bot` at the exact reviewed PR head. There is no
   independent per-artifact signature or attestation binding the DMG itself to that
   commit beyond the tag-to-release association GitHub already shows you on the
   release page.

**Success looks like:** `codesign --verify` prints nothing and exits 0; `spctl
--assess` reports the app is accepted.

## Verify a desktop Windows or Linux artifact's provenance

There is no reader-facing verification step for these two platforms today:

1. The Windows NSIS installer is shipped unsigned — its filename literally carries
   an `_alpha-unsigned` marker. There is no OS-level signature to check.
2. The Linux `.deb` carries no package signature either. The `.AppImage` is re-signed
   only as a Tauri *updater* artifact (`.AppImage.sig`), which the desktop app's
   internal auto-update logic verifies against `BUZZ_UPDATER_PUBLIC_KEY` when
   *checking for updates* — this is not something a reader can invoke by hand against
   a downloaded file, and it says nothing about a fresh manual download.
3. For both platforms, the only provenance anchor available to a reader is the same
   tag-and-required-checks chain described in the macOS section's step 3: trusting
   `desktop-v<version>` means trusting `auto-tag-on-release-pr-merge.yml`'s
   verification of the PR that produced it, not a signature on the file itself.

**This is a real gap, not an oversight to route around:** treat a downloaded Windows
or Linux desktop artifact as attested only as strongly as the GitHub release page's
tag association, and no more.

## Verify a mobile artifact's provenance

1. Confirm the exact `mobile-vX.Y.Z-rc.N` tag the store build or rollout record
   references — this is the entire source-of-record this repository publishes for
   mobile; there is no signed artifact, checksum, or attestation checked into or
   produced by this repository's own CI for either platform.
2. Recognize that whatever signing happened next — Android's upload-keystore (Google
   Play App Signing) or external Cashkite path, iOS's automatic code-signing —
   happened in the private Buildkite pipeline this repository cannot reach, using
   credentials this repository never holds. Verifying that signing chain, if you need
   to, means trusting the app store's own integrity checks (Play Protect / App Store
   code-signing verification at install time), not anything this repository's CI
   emits.
3. A version whose desktop or mobile artifact was produced by the private
   `buzz-releases` pipeline (Block-signed, `-block` suffix) is outside this
   repository's own provenance chain entirely — that pipeline's own guarantees, if
   any beyond signing, are not established here.

**Success looks like:** you can name the exact `mobile-v*` tag associated with the
build you have. Beyond that, this repository has nothing further to check.

## See also

- No merged `#1346`-shaped reference node for the release-tag format exists yet
  (tracked as issue #1299, `releases/release-tags.md`) — it would be the natural link
  for "what does a valid `desktop-v<version>` / `relay-v<version>` /
  `mobile-vX.Y.Z-rc.N` tag look like," which this node deliberately does not restate.
- No merged reference node for what each lane actually publishes and where exists yet
  either (tracked as issue #1297, `releases/release-artifacts.md`).
- `RELEASING.md` (repository root) is the authoritative source this node draws its
  procedural detail from and is the first place to check if a step above stops
  matching current behavior.

## Boundary

This node does not describe:

- **The release tag format itself** — `desktop-v<version>`, `relay-v<version>`,
  `mobile-vX.Y.Z-rc.N` naming and versioning rules are `#1299`'s
  (`releases/release-tags.md`) territory, not restated here beyond using tag names as
  examples.
- **What gets published and where, in general** — the full artifact/location
  inventory for each lane is `#1297`'s (`releases/release-artifacts.md`) territory;
  this node only names an artifact when its provenance mechanism needs it as context.
- **How to acquire the underlying skill of running a release from scratch** — that is
  a tutorial, and no corpus template for that Diátaxis form exists as of this writing
  (`templates/procedure.md` notes the same gap, tracked as `#1538`).
- **Why the three lanes are shaped so differently** (PR-driven vs. tag-cut-from-main,
  attestation vs. code-signing vs. nothing) — that is an explanation/concept
  discussion this node does not attempt; `RELEASING.md`'s own prose is the closest
  existing source.
- **Any node-specific exclusion beyond the above:** this node does not evaluate
  whether the private `buzz-releases` pipeline's signing is trustworthy, only that
  this repository cannot verify it directly.

## Relationships

None declared. No release-surface sibling node (`releases-desktop-candidate`,
`releases-mobile-candidate`, `releases-release-artifacts`, `releases-release-tags`) is
merged on `origin/launchpad` at the recorded revision — all four are still open issues
(#1292, #1294, #1297, #1299) — so there is no valid `references` or `part-of` target
yet. The first of those siblings to merge is the natural moment to add a `references`
edge back and forth with this node.

## Scope and omissions

**This node covers** how a released Buzz artifact's origin is verifiable today, per
lane: the relay's dual GitHub attestation (build provenance + deployment eligibility)
and its same-SHA CI qualification gate; desktop's code signing/notarization on macOS,
its explicit absence on Windows, its near-absence on Linux, its Tauri updater
signature on all three, and the tag-verification chain (`verify-release-ref.sh` +
`auto-tag-on-release-pr-merge.yml` + ruleset `14378754`) that anchors the
`desktop-v<version>` tag itself to a reviewed, checks-passed merge; and mobile's
tag-as-sole-source-record model, with Android/iOS signing detail sufficient to show
that signing happens outside this repository's reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The release tag format and versioning rules | `#1299`, open, not yet merged |
| The full published-artifact/location inventory per lane | `#1297`, open, not yet merged |
| How to run a release end-to-end (a tutorial) | no corpus template for this Diátaxis form exists; tracked as `#1538` |
| Why the three lanes differ structurally (an explanation) | no corpus concept/explanation template merged yet (`#1331`) |
| Whether the private `buzz-releases` pipeline adds its own provenance mechanism | unverifiable from this repository; see the TEAM_KNOWLEDGE evidence entry above |

**Expected but not verified when this node was written:**

- **`gh attestation verify oci://ghcr.io/launchpad-26/buzz:launchpad --owner
  launchpad-26` was attempted from this session** — the stronger, execution-based
  evidence `templates/procedure.md`'s own evidence expectations ask for where
  practical — **and failed with "remote registry authorization failed"**, because
  this environment holds no `ghcr.io` registry credentials, not because the
  attestation is absent. Every other command in this node is grounded in reading the
  workflow files that produce the attestations/signatures, not in a successful live
  run; re-attempting with a `docker login ghcr.io` session that can read
  `ghcr.io/launchpad-26/buzz` is the gap a follow-up pass could close.
- **Whether `docker.yml` still emits both attestations exactly as read here** was
  checked only at this node's recorded revision, for the workflow file shared by
  this fork and upstream; either could diverge from what this node describes.
- **No desktop DMG, Windows installer, Linux package, or mobile build was downloaded
  and inspected** to confirm the signing/signature behavior described actually
  produces the claimed result on a real artifact, rather than only being what the
  workflow source says it should do.
