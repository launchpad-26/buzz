---
id: releases-relay-release
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
  - statement: "The corpus's merged content nodes overwhelmingly use a bare `<directory>-<stem>` (or `<stem>` with no directory qualifier) id, not the `corpus-`-prefixed form standards/naming.md's MUST 3 states — for example architecture/containers/redis.md carries id architecture-containers-redis, and development/hermit.md and development/prerequisites.md carry development-hermit and development-prerequisites respectively, with no corpus- prefix on any of the three."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "Issue #2029 documents this divergence directly: of 229 merged corpus nodes at the time it was filed, corpus- appears on exactly 50 ids and 49 of those are meta documents (templates/, standards/, schema/fixtures/, AGENTS.md, README.md); the remaining 179 content nodes omit the prefix. The issue was still open (not yet an accepted standards change) when this node was written, so its proposed fix to naming.md is not itself citable as settled policy -- only the observed practice it measures is."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2029 (issue body, open at time of writing)"
  - statement: "This node's own id (releases-relay-release, no corpus- prefix) was assigned by the task that dispatched this node's authoring, on the stated grounds that the bare-form convention is settled practice tracked at #2029, matching the dominant observed pattern above rather than standards/naming.md's still-current MUST 3 text."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "issue #1296 dispatching task instructions"
  - statement: "RELEASING.md documents three independent release lanes -- desktop, relay, mobile -- and states the relay lane's entry point is `just release-relay`, its artifact is a `ghcr.io/block/buzz` container image, and relay versions independently by reading `crates/buzz-relay/Cargo.toml` rather than desktop's manifests."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's own 'Relay' subsection states the three-step flow: (1) `just release-relay` runs locally on `main`, creates or updates a `relay-release/<version>` PR, bumps `crates/buzz-relay/Cargo.toml`, regenerates `Cargo.lock`, and updates the relay changelog; (2) merging the PR causes `auto-tag-on-release-pr-merge` to push a `relay-v<version>` tag; (3) the tag triggers `docker.yml`, which updates version aliases and `latest` for stable releases only (not prereleases) and additionally publishes a symbol-bearing image under matching `debug-` tags for native profiling. It further states every push to `main` publishes rolling relay `:main` and `:sha-<7>` tags plus matching `:debug-main`/`:debug-sha-<7>` variants."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "Justfile's `release-relay` recipe computes the next patch version via `get-next-relay-patch-version` when called with no argument or the literal argument `patch`, otherwise uses the given version, and then calls the shared `_release-pr relay <version>` recipe."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Justfile's shared `_release-pr` recipe requires the caller to be on branch `main` with a clean tree that is up to date with `origin/main`, refuses to proceed otherwise, and for lane `relay` specifically: uses branch prefix `relay-release`, runs `just bump-relay-version <version>`, regenerates `crates/buzz-relay/CHANGELOG.md` from commits since the last `relay-v[0-9]*` tag (excluding prerelease tags) scoped to crates/buzz-relay/, buzz-core/, buzz-db/, buzz-auth/, buzz-pubsub/, buzz-search/, buzz-audit/, buzz-media/, buzz-sdk/, buzz-workflow/, buzz-conformance/ and migrations/, stages crates/buzz-relay/Cargo.toml + Cargo.lock + crates/buzz-relay/CHANGELOG.md, commits as 'chore(release): release Buzz Relay version <version>', force-pushes the branch, and opens or updates a PR titled the same, with a body ending '**To release:** merge this PR. The tag and build will happen automatically.'"
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Justfile's `bump-relay-version` recipe rewrites only the `version = \"...\"` line in `crates/buzz-relay/Cargo.toml` via an in-place `perl` substitution (buzz-relay carries its own version rather than `version.workspace = true`), then runs `cargo update -p buzz-relay` to regenerate `Cargo.lock`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "At the recorded revision, crates/buzz-relay/Cargo.toml's version field is 0.2.1."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: ".github/workflows/auto-tag-on-release-pr-merge.yml triggers only on `pull_request: types: [closed], branches: [main]`, and only proceeds when `github.event.pull_request.merged == true` and the PR's head repo matches the current repository. For a merged PR whose head branch matches `relay-release/<v>`, it extracts VERSION from the branch name, sets the tag prefix to `relay-v` and the target SHA to the merge commit (`$GITHUB_SHA`), obtains a short-lived token via the dedicated `buzz-release-bot` GitHub App, and creates the tag through the GitHub API -- treating a tag that already exists at the exact expected SHA as a no-op success, and a tag that exists at any other SHA as a hard error rather than moving it."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "At the recorded revision, the copy of .github/workflows/docker.yml checked out on origin/launchpad triggers on `push: branches: [launchpad], tags: [\"relay-v[0-9]*\"]`, plus `pull_request` (restricted to a fixed path list, build validation only, never pushes) and `workflow_dispatch` (a manual rescue path requiring a semver `version` input, intended to be dispatched at the immutable tag ref itself)."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "At the recorded revision, .github/workflows/docker.yml on origin/launchpad hardcodes `IMAGE_NAME: ghcr.io/launchpad-26/buzz` with no override mechanism, and its `qualify` job's `Create deployment eligibility predicate` step writes `build_workflow` as the literal string `.github/workflows/docker.yml`, i.e. this same file."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "The copy of .github/workflows/docker.yml on origin/main (checked at the same recorded revision) differs from the origin/launchpad copy in exactly two relevant respects: its push trigger is `branches: [main]` rather than `[launchpad]`, and its `IMAGE_NAME` is `${{ vars.GHCR_IMAGE != '' && vars.GHCR_IMAGE || 'ghcr.io/block/buzz' }}` -- a repository-variable override defaulting to `ghcr.io/block/buzz` -- rather than a hardcoded `ghcr.io/launchpad-26/buzz`. Both copies are otherwise triggered identically by `tags: [\"relay-v[0-9]*\"]` and `workflow_dispatch`."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/main', path='.github/workflows/docker.yml') -> line 44 'branches: [main]'; line 79 \"IMAGE_NAME: ${{ vars.GHCR_IMAGE != '' && vars.GHCR_IMAGE || 'ghcr.io/block/buzz' }}\", compared against the origin/launchpad copy's 'branches: [launchpad]' and hardcoded 'IMAGE_NAME: ghcr.io/launchpad-26/buzz'"
  - statement: "origin/main and origin/launchpad both exist as real branches of this repository's origin remote (git@github.com:launchpad-26/buzz.git) at the recorded revision -- confirmed by `git ls-remote --heads origin main` and `git ls-remote --heads origin launchpad` each returning a ref -- so a `relay-v<version>` tag pushed at a commit reachable only from one of the two branches is evaluated against that branch's own copy of docker.yml, and the two copies are not identical (see the entry above)."
    entry_class: FACT
    evidence:
      - "git_ls_remote(origin, heads=[main, launchpad]) -> both refs present, at distinct commits"
  - statement: "Because Justfile's `_release-pr` recipe hard-refuses to run unless the caller's current branch is exactly `main` (git symbolic-ref --short HEAD), running `just release-relay` in this repository as checked out can only ever produce a `relay-release/<version>` PR against `main`, never against `launchpad` -- so the `relay-v<version>` tag that flow creates is anchored to a commit on `main`, and (per the entry above) `main`'s own copy of docker.yml -- defaulting to `ghcr.io/block/buzz` -- is the one whose trigger conditions apply to that tag, not the `launchpad` branch's hardcoded `ghcr.io/launchpad-26/buzz` copy."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - ".github/workflows/docker.yml"
    confidence: 0.6
  - statement: "GitHub Actions' exact rule for which commit's copy of a workflow file governs a tag-push event was not independently verified in this session (no test tag was pushed); the INFERENCE above rests on the documented general behavior that a workflow definition is evaluated from the ref that triggered the event, not from the repository's default branch, which was not exercised end-to-end here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "session's own investigation, stated as an open verification gap rather than attributed to any external source"
  - statement: "docker.yml's `build` job (skipped entirely when github.event_name == 'pull_request') builds two variants -- a stripped `runtime` target and a symbol-bearing `runtime-debug` target -- from the repository's own ./Dockerfile, once per architecture (linux/amd64 on ubuntu-24.04, linux/arm64 on ubuntu-24.04-arm, natively, deliberately avoiding QEMU), and pushes each per-architecture image to GHCR by digest rather than by tag."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's `qualify` job blocks on finding a successful `.github/workflows/ci.yml` run at the exact same commit SHA (polling up to 3900 seconds via the GitHub API and scripts/select-qualified-ci-run.jq), and also reads the deployable chart version from deploy/charts/buzz/Chart.yaml; its `merge` job (needs: [build, qualify]) then downloads all per-architecture digests and stitches them into two multi-arch manifests via `docker buildx imagetools create`, one for each of the release and debug variants, tagging each per docker/metadata-action's tag matrix, and attaches a Sigstore build-provenance attestation to both variants plus an additional deployment-eligibility attestation (predicate type https://buzz.block.xyz/attestations/deployment-eligibility/v1) to the release variant only."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's tag matrix (via docker/metadata-action, match=^relay-v(.*)$) publishes `:{version}`, `:{major}.{minor}}` and `:{major}` for a `relay-v<version>` tag, a full-commit-SHA tag (`sha-<40-hex>`) on every non-pull_request run, and adds `:latest` (and `:debug-latest` for the debug variant) only for a non-prerelease semver version because metadata-action's `flavor.latest=auto` default excludes prerelease versions and branch pushes from `:latest`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's own top-of-file comment states its `workflow_dispatch` input exists specifically 'for an operator to rerun publication manually at an immutable relay tag' when a normal tag-triggered run needs to be rescued, and that the workflow rejects a dispatch whose ref, checked-out HEAD, and relay-v tag do not resolve to one commit."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "RELEASING.md's 'Release Retry' section documents a retry procedure for the desktop lane only (rerunning a failed release.yml run for an existing desktop-v<version> tag); it contains no relay-specific retry or rollback prose, and its 'Internal Releases' section names private continuation pipelines for mobile and desktop only, with no relay entry."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "scripts/verify-release-ref.sh takes a tag prefix and version, requires the running workflow's GITHUB_REF to equal exactly refs/tags/<prefix><version>, and requires the checked-out HEAD commit to equal that tag's commit -- both release.yml (desktop-v prefix) and docker.yml (relay-v prefix) call it as a guard before doing any release work."
    entry_class: FACT
    evidence:
      - "scripts/verify-release-ref.sh"
  - statement: "launchpad/docs/corpus/development/build.md (merged) explicitly excludes 'building or packaging a distributable release artifact -- installers, signed binaries, container images, Helm charts' from its own scope, naming 'the release.yml, docker.yml, desktop-release-candidate.yml and helm-chart.yml workflows' as the owners instead -- this node is exactly that named gap for the relay/docker.yml pair, not a duplication of build.md's compile-from-source content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
  - statement: "The repository's top-level AGENTS.md (CLAUDE.md) names two private, external pipelines downstream of this repository's own relay release: squareup/sprout-oss, described as 'CI pipeline building the relay Docker image and pushing to internal ECR', and squareup/block-coder-tf-stacks, described as 'Terraform + ArgoCD deploying the relay to the staging Kubernetes cluster' -- both outside this repository and not inspectable in this session."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "launchpad/docs/corpus/templates/procedure.md (id corpus-template-procedure, merged, status active) is the corpus's Diátaxis how-to-shaped template this node is built against, and it recommends a node built from it declare an `implements` relationship targeting corpus-template-procedure once merged."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Issues #1299 (releases/release-tags.md) and #1301 (releases/versioning.md) were both open and unmerged at the time this node was checked, and git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no releases/ directory at all before this node's addition -- so neither is a valid relationship target, and this node's tag-naming and version-source statements above are stated directly from RELEASING.md/Justfile/docker.yml rather than deferred to either sibling task."
    entry_class: FACT
    evidence:
      - "gh_issue_view(repo='launchpad-26/buzz', number=1299) -> state OPEN, title 'task: document releases/release-tags.md'"
      - "gh_issue_view(repo='launchpad-26/buzz', number=1301) -> state OPEN, title 'task: document releases/versioning.md'"
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no releases/ directory present"
  - statement: "Issue #1296's own Definition of Done requires this node to state goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands/config rather than give generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1296 definition of done"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: corpus-development-build
---

# Release the relay

Cut and publish a new version of the Buzz relay container image -- the task run
once `buzz-relay` and its dependency crates are ready to ship, after
`development/build.md`'s compile step already confirms the workspace builds.

## Before you start

- Write access to push a branch and open/merge a pull request against this
  repository, with `gh` authenticated.
- A clean, up-to-date checkout of the `main` branch specifically -- the release
  recipe below refuses to run from any other branch, including `launchpad`.
- A local Rust toolchain (for the `cargo update -p buzz-relay` step the bump
  recipe runs).

## Cut and publish a relay release

1. From a clean, up-to-date `main` checkout, run `just release-relay` (or `just
   release-relay <X.Y.Z>` for an explicit version; without one, the next patch
   version is computed from the current `crates/buzz-relay/Cargo.toml`
   version). This bumps that file's `version` field, regenerates `Cargo.lock`,
   rewrites `crates/buzz-relay/CHANGELOG.md` from commits since the last
   `relay-v[0-9]*` tag touching the relay's own dependency crates and
   `migrations/`, and force-pushes a `relay-release/<version>` branch, opening
   or updating a PR titled `chore(release): release Buzz Relay version
   <version>`.
2. Review the PR's generated changelog block and let CI run against it.
3. Merge the PR into `main`. The merge is the authorization event:
   `auto-tag-on-release-pr-merge.yml` -- which only triggers for PRs closed
   against `main` -- recognizes the `relay-release/<version>` branch name and
   creates the immutable `relay-v<version>` tag at the merge commit, using a
   dedicated `buzz-release-bot` App token. Re-running this step is safe only
   if the tag would land at the identical commit; any other outcome is a hard
   error rather than a moved tag.
4. The `relay-v<version>` tag push triggers `docker.yml`. Its `build` job
   compiles both a stripped `runtime` image and a symbol-bearing
   `runtime-debug` image, once per architecture (`linux/amd64`, `linux/arm64`,
   each on its native runner), from the repository's own `Dockerfile`, and
   pushes each per-architecture image to GHCR by digest.
5. `docker.yml`'s `qualify` job blocks publication until a successful
   `ci.yml` run exists for that exact commit SHA (polling up to 65 minutes),
   then its `merge` job stitches the per-architecture digests into two
   multi-arch manifests -- tagged `:{version}`, `:{major}.{minor}`,
   `:{major}`, a full-commit-SHA tag, and (for a non-prerelease version only)
   `:latest`/`:debug-latest` -- and attaches a build-provenance attestation to
   both variants plus a deployment-eligibility attestation to the release
   (non-debug) variant.

## Which copy of docker.yml actually runs

This repository carries two long-lived branches, `main` and `launchpad`, each
with its own copy of `.github/workflows/docker.yml`. They differ in exactly
two respects: the `launchpad` copy hardcodes `IMAGE_NAME:
ghcr.io/launchpad-26/buzz` and triggers on push to `launchpad`; the `main`
copy defaults `IMAGE_NAME` to `ghcr.io/block/buzz` (overridable by a
`GHCR_IMAGE` repository variable) and triggers on push to `main`. Because
`just release-relay`'s preflight refuses to run from any branch but `main`,
every `relay-v<version>` tag this flow produces is anchored to a commit on
`main` -- so `main`'s copy of `docker.yml`, not `launchpad`'s, is the one
whose trigger conditions govern that tag. This session did not push a test
tag to confirm GitHub Actions' exact ref-resolution behavior end to end; see
*Scope and omissions*.

## Verify the release published

- Confirm the tag exists and points at the expected commit: `git ls-remote
  --tags origin relay-v<version>`.
- Confirm `docker.yml`'s run for that tag succeeded (its `merge` job's
  Summary step prints the merged digest, the qualifying CI run, and the exact
  verification commands): `gh run list --repo <owner>/buzz --workflow
  docker.yml`.
- Verify provenance on the published image: `gh attestation verify
  oci://<image>@<digest> --owner <owner>` (the exact image and owner depend
  on which branch's copy ran -- see the note above).
- For the release (non-debug) variant, verify deployment eligibility:
  `gh attestation verify oci://<image>@<digest> --repo block/buzz
  --signer-workflow block/buzz/.github/workflows/docker.yml --predicate-type
  https://buzz.block.xyz/attestations/deployment-eligibility/v1
  --source-digest <source-sha>`.

## Recovering from a failed or partial publish

If `docker.yml`'s run for an already-created `relay-v<version>` tag fails or
only partially completes, do not delete or move the tag -- it is immutable by
design, and `scripts/verify-release-ref.sh` requires the workflow to run at
exactly that tag ref with a matching checked-out HEAD. Instead, dispatch the
workflow manually at the tag itself with the same version, using the
`workflow_dispatch` rescue path `docker.yml` documents in its own top-of-file
comment (`gh workflow run docker.yml --ref relay-v<version> -f
version=<version>`). RELEASING.md documents an equivalent retry procedure for
the desktop lane only; it states no relay-specific retry or rollback
procedure beyond this rescue dispatch, and none was found elsewhere in this
repository -- see *Scope and omissions*.

## See also

- `launchpad/docs/corpus/development/build.md` -- compiling the Rust
  workspace from source, which this node assumes already succeeds before a
  release is cut.
- No reference-shaped or concept/explanation-shaped corpus node exists yet
  for the relay's Docker build (`Dockerfile`) itself, or for why the release
  is versioned independently of desktop.

## Boundary

This node does not describe:

- **Compiling the relay from source** -- `launchpad/docs/corpus/development/
  build.md` (merged) owns `cargo build --workspace` / `--release`; this node
  assumes that step already succeeds.
- **The desktop or mobile release lanes** -- RELEASING.md documents both
  separately; `releases/desktop-release.md` is issue #1293, a distinct task.
- **Detailed tag-naming or version-source conventions beyond what this flow
  needs** -- `releases/release-tags.md` (#1299) and `releases/versioning.md`
  (#1301) are open, unmerged tasks for that depth; both were checked and
  confirmed not yet corpus nodes, so no relationship targets them.
- **What happens after the image reaches GHCR** -- `squareup/sprout-oss`
  (building the relay Docker image for internal ECR) and
  `squareup/block-coder-tf-stacks` (Terraform/ArgoCD deployment to the
  staging cluster) are private, external pipelines this session cannot
  inspect; they are named, not documented step-by-step.
- **Acquiring the underlying skill of operating CI/CD from scratch**, for a
  newcomer -- a tutorial, which has no corpus template as of this writing.
- **Why the relay versions independently of desktop, or why the release flow
  is shaped this way** -- a concept/explanation node, if one is later
  written, would own that; this node only states the mechanism as read from
  the cited files.

## Relationships

- `implements: corpus-template-procedure` -- this node is a how-to-shaped
  instance of that merged template.
- `references: corpus-development-build` -- the compile-from-source
  procedure this release flow assumes as a precondition, per the Boundary
  above. Checked against `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` before finalizing: no `releases/`-typed sibling node
  exists yet to relate to, and `releases-relay-release`'s two possible
  DoD-adjacent siblings (`releases/release-tags.md` #1299,
  `releases/versioning.md` #1301) are both unmerged, so neither is declared.

## Scope and omissions

**This node covers** the relay's own release flow as encoded in this
repository: bumping `crates/buzz-relay/Cargo.toml` and its changelog via `just
release-relay`, the `relay-release/<version>` PR, the merge-triggered
`relay-v<version>` tag, and the `docker.yml`-driven multi-arch image build,
CI-qualification gate, and publish-with-attestation -- plus the recorded
divergence between this repository's `main`- and `launchpad`-branch copies of
`docker.yml`, and the rescue dispatch for a failed publish.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Compiling the relay from source | `launchpad/docs/corpus/development/build.md` (merged) |
| The desktop release lane | RELEASING.md's Desktop section; `releases/desktop-release.md` is issue #1293 |
| The mobile release lane | RELEASING.md's Mobile section; no corpus task identified for it at this revision |
| Detailed tag-naming conventions across all lanes | `releases/release-tags.md`, issue #1299, open |
| Version-source conventions across all lanes | `releases/versioning.md`, issue #1301, open |
| The private `sprout-oss` relay-image-for-ECR pipeline | External; not inspectable in this session |
| The private `block-coder-tf-stacks` Terraform/ArgoCD deployment | External; not inspectable in this session |
| A reference-shaped listing of every `docker.yml` job's inputs/outputs | No reference-shaped corpus node exists yet for this |
| Why the relay versions independently of desktop | No concept/explanation node exists yet for this |

**Expected but not verified when this node was written:**

- **No relay release was actually run in this session.** Every step above is
  read from `RELEASING.md`, `Justfile`, and the two workflow files, not
  exercised end to end; whether `just release-relay` succeeds cleanly from a
  real `main` checkout, and whether the resulting tag's `docker.yml` run
  completes as described, is unverified here.
- **Which branch's copy of `docker.yml` GitHub Actions actually evaluates for
  a `relay-v<version>` tag was not confirmed by pushing a test tag.** The
  INFERENCE in the ledger and the *Which copy of docker.yml actually runs*
  section above reason from the two files' visible differences and from
  `_release-pr`'s `main`-only preflight, not from an observed run.
  `#1321`-style provenance caveats aside, this is a live open question for
  whoever next cuts a relay release in this fork.
- **No relay-specific rollback or "undo a bad publish" procedure was found
  anywhere in this repository** beyond the `workflow_dispatch` rescue path,
  which reruns the same immutable tag's build rather than reversing a
  published image. Whether cohort practice expects a follow-up patch release
  instead (as RELEASING.md states explicitly for the desktop lane) was not
  stated anywhere for relay, so this node does not assert it.
- **The private `sprout-oss` and `block-coder-tf-stacks` pipelines' own
  triggers, inputs, and relationship to the GHCR image this node's flow
  publishes** were not established -- both are named only from this
  repository's own top-level `AGENTS.md`/`CLAUDE.md`, not inspected directly.
