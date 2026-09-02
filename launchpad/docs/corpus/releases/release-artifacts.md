---
id: releases-release-artifacts
type: release
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "node.schema.json's type enum includes release, the surface this node documents, and reference.md is the merged template for this node's body shape (Reference description / structured entries / optional Commands / Boundary / Relationships / Scope and omissions)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/reference.md"
  - statement: "At this revision, launchpad/docs/corpus/releases/ does not exist on origin/launchpad -- this is the first node in that directory, so there are no sibling release nodes yet to declare a relationship toward or check for duplicated content against."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no releases/ prefix present among the listed paths, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: ".github/workflows/release.yml, triggered by a push of a desktop-v[0-9]* tag, gates its setup, release (macOS arm64), release-macos-x64 and release-linux jobs on `if: github.repository == 'block/buzz'`; the release-windows job carries no such condition, and the assemble-manifest job is gated separately to require all four platform jobs plus `github.ref == format('refs/tags/desktop-v{0}', ...)`."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: "release-windows `needs: setup`, and setup is one of the four jobs gated to block/buzz only; GitHub Actions' documented default is that a job skips when a job named in its own `needs` did not run to success (no `if: always()` or similar override is present on release-windows), so release-windows has no artifact path to run in a fork whose repository is not block/buzz even though its own job header carries no explicit repository gate."
    entry_class: INFERENCE
    confidence: 0.75
    evidence:
      - ".github/workflows/release.yml"
  - statement: "The release job (macOS arm64) locates a signed/notarized DMG and a re-signed updater archive (Buzz_<version>_aarch64.app.tar.gz) plus its .sig, and stages them as the desktop-release-macos-arm64 workflow artifact; release-macos-x64 does the same for Buzz_<version>_x64.app.tar.gz; release-linux stages a .deb, an AppImage, and an AppImage-based updater archive+.sig as desktop-release-linux-x64 (the .deb is explicitly noted as not auto-updatable); release-windows stages an NSIS installer .exe (renamed with an _alpha-unsigned marker) plus its .sig as desktop-release-windows-x64."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: "The assemble-manifest job downloads all four staged platform artifact sets, flattens them (failing on any basename collision), generates a single unified latest.json (desktop/scripts/generate-oss-latest-json.sh) that becomes both the GitHub Release's updater-manifest.json asset and the Tauri auto-updater's manifest, then creates or verifies a versioned draft GitHub Release named desktop-v<version> (target commit pinned to the tag-verified source SHA, notes sliced out of CHANGELOG.md's matching ## v<version> block), uploads every staged file to it, and publishes it by clearing --draft."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: ".github/workflows/docker.yml's `build` job publishes a multi-arch relay image to IMAGE_NAME, which this fork's workflow hardcodes to ghcr.io/launchpad-26/buzz with the comment \"Launchpad publication must never fall back to the upstream Block package\" -- unlike sprig-image.yml and helm-chart.yml (see below), this destination is not conditional on a repo variable, it is the literal value in this checked-out file."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's build job runs on `push` to the launchpad branch (producing :launchpad and :sha-<commit> tags) and on relay-v[0-9]* tags (adding the semver family :{version}/:{major.minor}/:{major}, plus :latest for non-prerelease semver only), each in a release variant (Dockerfile target `runtime`) and a debug variant (target `runtime-debug`, tag-prefixed debug-); the merge job stitches per-arch digests into one multi-arch manifest per variant and pushes it, gated on `qualify` finding a successful same-SHA CI run first."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's merge job attests build provenance (actions/attest-build-provenance, verifiable via `gh attestation verify oci://<image>@<digest> --owner launchpad-26`) for both the release and debug manifest variants, and additionally attests a custom `deployment-eligibility` predicate (predicate-type https://buzz.block.xyz/attestations/deployment-eligibility/v1) for the release variant only, embedding the qualifying CI run id/attempt/URL and the compatible Helm chart version read from deploy/charts/buzz/Chart.yaml."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
      - "scripts/create-deployment-eligibility-predicate.jq"
  - statement: "docker.yml's push-gateway-build and push-gateway-merge jobs, which publish ghcr.io/block/buzz-push-gateway, are both gated `if: github.repository == 'block/buzz'` with the comment \"Launchpad does not operate the separate APNs gateway\" -- this fork does not build or publish that image."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "helm-chart.yml's publish job packages deploy/charts/buzz with `helm package` and pushes it via `helm push` to CHART_REPO, which defaults to oci://ghcr.io/block/buzz/charts but is overridable per-repository by a GHCR_CHART_REPO repository variable (comment: \"forks pushing to their own namespace without editing this file\"); it fires on a chart-v[0-9]* tag push or a workflow_dispatch rescue with a version input, and carries no repository-identity gate at all -- unlike the relay image jobs, it would run identically in any fork with a matching tag and Chart.yaml version."
    entry_class: FACT
    evidence:
      - ".github/workflows/helm-chart.yml"
  - statement: "push-gateway-helm-chart.yml's publish job packages deploy/charts/buzz-push-gateway and pushes it to a CHART_REPO hardcoded to oci://ghcr.io/block/buzz/charts, with no GHCR_CHART_REPO-style override and no repository-identity gate -- unlike docker.yml's push-gateway image jobs (gated to block/buzz), this chart-publish job is not restricted to the upstream repository even though the image it charts is."
    entry_class: FACT
    evidence:
      - ".github/workflows/push-gateway-helm-chart.yml"
  - statement: "sprig.yml builds two static Linux tarballs (x86_64-unknown-linux-musl and aarch64-unknown-linux-musl, via `cross`) bundling buzz-acp, buzz-agent and buzz-dev-mcp as one multicall binary, each uploaded as a workflow artifact alongside a .sha256; on push to main it updates a rolling `sprig-latest` prerelease GitHub Release (title \"Sprig (rolling)\"), and on a sprig-v* tag push it creates a new versioned GitHub Release (Sprig v<version>) with the same two tarballs attached. Neither the build nor either publish job carries a repository-identity gate."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml"
  - statement: "sprig-image.yml publishes a multi-arch agent container image to IMAGE_NAME, which defaults to ghcr.io/block/buzz-sprig but is overridable by a GHCR_SPRIG_IMAGE repository variable (mirroring docker.yml's override pattern, per its own comment); it fires on push to main (paths-filtered), on sprig-v[0-9]* tags (sharing one tag with sprig.yml's binary release), on pull_request (build-only, no push), and on workflow_dispatch, and attests build provenance for the merged manifest. This job also carries no repository-identity gate."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig-image.yml"
  - statement: "mobile-release-candidate.yml does not build or upload any binary artifact. Its one job requires `github.ref == 'refs/heads/main'` and `github.repository == 'block/buzz'` (hard-failing otherwise), then runs scripts/publish-mobile-release-candidate.sh to push an annotated `mobile-v<version>-rc.<candidate_number>` git tag at an operator-supplied target_sha, using a short-lived GitHub App token. The workflow's own header comment states a human hands that exact tag to the private buzz-releases Buildkite pipeline, which performs the actual mobile build; auto-tag-on-release-pr-merge.yml's header comment gives the reason: \"OSS block/buzz CI must not trigger CI in the private buzz-releases repo.\""
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml"
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "promote-oss-desktop-release.yml also builds nothing. Its one `promote` job is gated `if: github.repository == 'block/buzz'`, additionally requires dispatch from refs/heads/main, and runs scripts/promote-oss-desktop-release.sh to validate and promote an already-published desktop-v<version> release's exact manifest to become the live auto-update target."
    entry_class: FACT
    evidence:
      - ".github/workflows/promote-oss-desktop-release.yml"
  - statement: "desktop-release-candidate.yml (runs on pull_request to main, validates an immutable version-bump/* candidate via scripts/desktop_release.py) and desktop-release-cache-proof.yml (workflow_dispatch-only, gated to block/buzz, proves Rust build-cache visibility at a cache-proof-* tag) both produce no release artifact of any kind -- the first is a PR gate, the second a cache-warming diagnostic -- and are excluded from the artifact catalogue below for that reason."
    entry_class: FACT
    evidence:
      - ".github/workflows/desktop-release-candidate.yml"
      - ".github/workflows/desktop-release-cache-proof.yml"
  - statement: "auto-tag-on-release-pr-merge.yml is the one place all four PR-driven release lanes converge: merging a version-bump/<v>, relay-release/<v>, chart-release/<v> or push-chart-release/<v> branch (or any internal PR that bumps deploy/charts/buzz/Chart.yaml's version) into main creates the corresponding immutable desktop-v<v>, relay-v<v>, chart-v<v> or push-chart-v<v> tag using a short-lived buzz-release-bot GitHub App token, which is what actually triggers release.yml / docker.yml / helm-chart.yml / push-gateway-helm-chart.yml's publish paths described above."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "The root AGENTS.md ecosystem table names three private repositories that receive release artifacts this checkout cannot inspect: squareup/buzz-releases (Buildkite pipelines producing Block-signed macOS + iOS builds with a -block desktop version suffix, feeding Artifactory, GitHub Releases and Mobile Releases), squareup/sprout-oss (CI building the relay Docker image and pushing to internal ECR), and squareup/block-coder-tf-stacks (Terraform + ArgoCD deploying the relay to the staging Kubernetes cluster from that Helm chart)."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "The relay Docker image is versioned independently of the desktop app via its own relay-v* tags tracking crates/buzz-relay/Cargo.toml (version 0.2.1 at this revision), not desktop's CHANGELOG.md-tracked version; the main Helm chart's version comes from deploy/charts/buzz/Chart.yaml (0.1.8 at this revision) and the push-gateway chart's from deploy/charts/buzz-push-gateway/Chart.yaml (0.1.0 at this revision) -- three independent version numbers for three independently tagged artifacts, per docker.yml's and helm-chart.yml's own comments."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "deploy/charts/buzz/Chart.yaml"
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
      - ".github/workflows/docker.yml"
      - ".github/workflows/helm-chart.yml"
  - statement: "This task's own GitHub issue (#1297) and every one of its ten releases/ sibling tasks (#1291-#1296, #1298-#1301) carry an Objective sentence reading '...as the single canonical procedure node for <subject>' and a Definition of Done tail matching a procedure/how-to checklist (states goal/prerequisites/scope, provides ordered executable steps, defines success verification and rollback, links authoritative commands/config) verbatim across all eleven issues regardless of subject -- the same boilerplate-copy pattern the reference.md template's own evidence ledger documents for issue #1346 (Feature #605's actual acceptance bar, not the per-issue DoD boilerplate, is what a template task is built against). Because 'what artifacts are produced and where they land' is a lookup catalogue rather than a sequence of operator actions, and because #1292/#1293 already separately exist as this Feature's dedicated procedure tasks (desktop-candidate.md, desktop-release.md) for the actual cut-a-release steps, this node is built as reference-shaped rather than against the copied procedure-shaped DoD text."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "gh_issue_view(1297) -> Objective: 'Create `launchpad/docs/corpus/releases/release-artifacts.md` as the single canonical procedure node for release artifacts.'"
      - "gh_issue_view(1291..1301) -> identical 'single canonical procedure node for <subject>' Objective sentence and identical goal/prerequisites/steps/verification/rollback Definition of Done tail on all eleven issues"
      - "launchpad/docs/corpus/templates/reference.md"
---

# release-artifacts: reference

This node catalogues **what artifact each Buzz release-triggering event actually
builds, and where that artifact is uploaded or pushed to** -- read directly from
this repository's own GitHub Actions workflow YAML at the recorded revision,
rather than from a prose summary. It also states, per surface, whether the
**launchpad-26 fork of this repository** can produce that artifact at all: several
jobs are hard-gated to `github.repository == 'block/buzz'` and never run here,
while others carry no such gate and run identically in any fork. This is a
build-topology lookup, not a walkthrough of how to cut a release -- see
*Boundary* below for the task-shaped documents this node deliberately does not
duplicate.

## Release surfaces and the artifacts they produce

| Trigger | Workflow (job) | Artifact(s) produced | Destination | Runs in the launchpad-26 fork? |
|---|---|---|---|---|
| Push tag `desktop-v[0-9]*` | `release.yml` (`setup`, `release`, `release-macos-x64`, `release-linux`) | macOS arm64 signed/notarized `.dmg` + updater `Buzz_<version>_aarch64.app.tar.gz` + `.sig`; macOS x64 equivalents (`_x64`); Linux `.deb` + `.AppImage` + AppImage-based updater archive + `.sig` | Staged as workflow artifacts, later uploaded to a GitHub Release | **No** -- all four jobs carry `if: github.repository == 'block/buzz'` |
| Same tag | `release.yml` (`release-windows`) | Windows NSIS installer `.exe` (renamed with an `_alpha-unsigned` marker) + `.sig` | Staged as a workflow artifact, later uploaded to the same GitHub Release | **No, in effect** -- the job carries no explicit gate itself, but `needs: setup`, and `setup` is gated to `block/buzz`; a job whose `needs` target does not run to success is skipped by GitHub Actions' default behavior (INFERENCE, not executed here) |
| Same tag, all four platform jobs succeeded | `release.yml` (`assemble-manifest`) | Unified `latest.json` (Tauri auto-updater manifest, copied into the release as `updater-manifest.json`); versioned GitHub Release `desktop-v<version>` (draft created/verified, all staged files uploaded, then published) | `gh release create/upload/edit` against this repository; release notes sliced from `CHANGELOG.md`'s matching `## v<version>` block | **No** -- requires all four gated jobs to have succeeded first |
| Push to the `launchpad` branch, or tag `relay-v[0-9]*` | `docker.yml` (`build`, `qualify`, `merge`) | Multi-arch relay Docker image, release variant (`Dockerfile` target `runtime`) and debug variant (target `runtime-debug`, `debug-` tag prefix) | `ghcr.io/launchpad-26/buzz` (hardcoded `IMAGE_NAME` in this fork's copy of the file, "must never fall back to the upstream Block package") | **Yes** -- no repository-identity gate on `build`, `qualify` or `merge` |
| Same, `merge` job | `docker.yml` (`merge`) | Sigstore build-provenance attestation (both variants); a custom `deployment-eligibility` predicate attestation (release variant only, embeds qualifying CI run + compatible Helm chart version) | Pushed to the registry alongside the image manifest | **Yes**, wherever the image publish above runs |
| Push to `launchpad`/`relay-v*` tag (upstream only) | `docker.yml` (`push-gateway-build`, `push-gateway-merge`) | Multi-arch `ghcr.io/block/buzz-push-gateway` image | GHCR, `block/buzz-push-gateway` namespace | **No** -- both jobs gated `if: github.repository == 'block/buzz'` ("Launchpad does not operate the separate APNs gateway") |
| Push tag `chart-v[0-9]*`, or `workflow_dispatch` rescue | `helm-chart.yml` (`publish`) | Packaged main Helm chart `buzz-<version>.tgz` | `oci://ghcr.io/block/buzz/charts` by default; overridable per-fork via a `GHCR_CHART_REPO` repository variable | **Yes** -- no repository-identity gate; destination depends on whether this fork sets `GHCR_CHART_REPO` (not verified here) |
| Push tag `push-chart-v[0-9]*`, or `workflow_dispatch` | `push-gateway-helm-chart.yml` (`publish`) | Packaged push-gateway Helm chart `buzz-push-gateway-<version>.tgz` | `oci://ghcr.io/block/buzz/charts` (hardcoded, no override variable) | **Yes** -- no repository-identity gate, unlike the image this chart deploys |
| Push to `main`, or tag `sprig-v*`, or `workflow_dispatch` with `publish: true` | `sprig.yml` (`build`, `publish`, `publish-tag`) | Two static Linux tarballs (`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`) bundling `buzz-acp` + `buzz-agent` + `buzz-dev-mcp` as one multicall binary, each with a `.sha256` | A rolling `sprig-latest` prerelease GitHub Release (main pushes) or a versioned `sprig-v<version>` GitHub Release (tag pushes), both on this repository | **Yes** -- no repository-identity gate |
| Push to `main` (paths), tag `sprig-v[0-9]*`, `pull_request` (build-only), or `workflow_dispatch` | `sprig-image.yml` (`build`) | Multi-arch agent container image + build-provenance attestation | `ghcr.io/block/buzz-sprig` by default; overridable via a `GHCR_SPRIG_IMAGE` repository variable | **Yes** -- no repository-identity gate; destination depends on whether this fork sets `GHCR_SPRIG_IMAGE` (not verified here) |
| `workflow_dispatch` only | `mobile-release-candidate.yml` | **No artifact built.** Publishes one annotated git tag `mobile-v<version>-rc.<candidate_number>` at an operator-supplied `target_sha` | The tag lives on this repository; a human then hands it to the private `buzz-releases` Buildkite pipeline, which performs the actual mobile build | **No** -- the job hard-fails unless `github.repository == 'block/buzz'` and the dispatch ref is `main` |
| `workflow_dispatch` only | `promote-oss-desktop-release.yml` | **No artifact built.** Validates and promotes an already-published `desktop-v<version>` release's exact manifest to become the live auto-update target | Mutates the existing GitHub Release/auto-update pointer on this repository | **No** -- gated `if: github.repository == 'block/buzz'`, plus `main`-only dispatch |

### Convergence point: what actually creates the release tags

None of the tag-triggered rows above fire on their own -- `auto-tag-on-release-pr-merge.yml`
is the one workflow that creates the `desktop-v*`, `relay-v*`, `chart-v*` and
`push-chart-v*` tags, by detecting a merged `version-bump/*`, `relay-release/*`,
`chart-release/*` or `push-chart-release/*` branch (or, for the chart, any
internal PR that bumped `deploy/charts/buzz/Chart.yaml`'s version) and pushing
the matching immutable tag with a short-lived `buzz-release-bot` GitHub App
token. Mobile candidate tags are the deliberate exception: they are never
produced by a merged PR, only by an operator running the mobile-release-candidate
dispatch (or, per that workflow's own header comment, `scripts/mobile-release.sh`
directly) -- "OSS `block/buzz` CI must not trigger CI in the private `buzz-releases`
repo."

## Excluded from this table

`desktop-release-candidate.yml` (a `pull_request`-triggered validation gate for
an immutable `version-bump/*` candidate) and `desktop-release-cache-proof.yml`
(a `workflow_dispatch`-only Rust build-cache visibility proof, gated to
`block/buzz`) both build and publish no artifact at all. They are excluded from
the table above rather than listed with an empty artifact column.

## Boundary

This node does not describe:

- **How to cut a release** -- the branch-naming convention, the PR review flow,
  or the operator steps behind `version-bump/*` / `relay-release/*` /
  `chart-release/*` / `push-chart-release/*`. That is #1292 (desktop-candidate)
  and #1293 (desktop-release)'s job as this Feature's dedicated procedure nodes.
  **Neither exists yet in `origin/launchpad`'s corpus tree at this node's recorded
  revision** (see *Scope and omissions*), so this node cannot yet declare a
  `references` relationship toward them.
- **What each release tag format means**, or the semver/rc numbering scheme --
  `release-tags.md` (#1299).
- **Version-bump policy** (what triggers a major vs. minor vs. patch bump) --
  `versioning.md` (#1301).
- **How to verify or consume the attestations** this node only names as
  produced (build-provenance, deployment-eligibility) -- `release-provenance.md`
  (#1298). This node states that they exist and what they embed; it does not
  give the verification procedure, even though `docker.yml`'s own `Summary`
  step already prints a ready-to-run `gh attestation verify` command for both.
- **Rollback** -- `rollback.md` (#1300).
- **Auto-update mechanics** beyond "this workflow produces `latest.json`" --
  `auto-update.md` (#1291).
- **What the three private downstream repositories actually do** with an
  artifact once it is handed to them (`squareup/buzz-releases`,
  `squareup/sprout-oss`, `squareup/block-coder-tf-stacks`) -- this checkout
  cannot inspect those repositories, so their contents are named as a gap, not
  guessed at.
- This is not an API reference; it is a build-topology catalogue.

## Relationships

None declared. `launchpad/docs/corpus/releases/` does not exist on
`origin/launchpad` at this node's recorded revision -- this is the first node
in that directory, so there is no sibling release node yet to point `part-of`
or `references` toward, and no procedure node for #1292/#1293 yet exists to
receive a `references` edge from this node's *Boundary* section above.

## Scope and omissions

**This node covers** which GitHub Actions workflow in this repository builds
which concrete artifact, on which trigger, and where that artifact is
uploaded or pushed to, as of the recorded revision -- explicitly distinguishing
artifacts this launchpad-26 fork can actually produce (no upstream-only
repository gate) from ones gated to `block/buzz` only.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Release process: branch naming, PR flow, review gates | #1292 / #1293 (not yet merged at this revision) |
| Tag format semantics | `release-tags.md` (#1299) |
| Version-bump / semver policy | `versioning.md` (#1301) |
| Attestation verification procedure | `release-provenance.md` (#1298) |
| Rollback procedure | `rollback.md` (#1300) |
| Auto-update mechanics beyond manifest production | `auto-update.md` (#1291) |
| Exact behavior of `squareup/buzz-releases`, `squareup/sprout-oss`, `squareup/block-coder-tf-stacks` once handed a candidate tag or image | Private repositories, not inspectable from this checkout |

**Expected but not verified when this node was written:**

- Whether the `launchpad-26/buzz` repository has the `GHCR_SPRIG_IMAGE` and/or
  `GHCR_CHART_REPO` repository variables set. If unset, `sprig-image.yml` and
  `helm-chart.yml` push to the upstream `ghcr.io/block/...` namespaces by
  default rather than a launchpad-26 namespace -- unlike `docker.yml`'s relay
  image, whose `IMAGE_NAME` is hardcoded to `ghcr.io/launchpad-26/buzz` in this
  fork's copy of the file with no variable indirection at all.
- Whether `release-windows` in `release.yml` actually no-ops in this fork at
  runtime when `setup` is skipped. This node states GitHub Actions' documented
  default (a job depending on a skipped job is itself skipped) as an
  INFERENCE, not something observed by running the workflow.
- Whether `push-gateway-helm-chart.yml`'s chart-push step would succeed against
  `oci://ghcr.io/block/buzz/charts` using this fork's own `GITHUB_TOKEN` (a
  cross-organization package write). This node only establishes that the
  workflow carries no repository-identity gate preventing the *attempt* --
  not that the push would succeed.
