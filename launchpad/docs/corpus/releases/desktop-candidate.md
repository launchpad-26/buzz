---
id: releases-desktop-candidate
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
  - statement: "Buzz has three independent release lanes -- desktop, relay, mobile -- and the desktop lane's entry point is `just release-desktop <version>`, producing a packaged desktop app (signed/notarized macOS, unsigned Windows, and Linux); the desktop lane uses an immutable generated candidate PR, distinct from relay's metadata PR and from mobile's tag-only flow."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "The `release-desktop` Justfile recipe resolves the target version by calling `get-next-patch-version` when no argument or the literal argument `patch` is given, otherwise uses the given argument verbatim, and then runs `scripts/prepare-desktop-release.sh \"$VERSION\"`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "`scripts/prepare-desktop-release.sh` fetches `origin/main` and existing `v*`/`desktop-v*` tags, checks out (or reuses) a branch named `version-bump/<version>` from the fetched `origin/main` tip, runs `just bump-desktop-version <version>`, then `scripts/desktop_release.py generate <version> --base <base_sha>` to rewrite `CHANGELOG.md` and write `.release/desktop-candidate.json`, stages exactly `.release/desktop-candidate.json`, `CHANGELOG.md`, `desktop/package.json`, `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`, `desktop/src-tauri/Cargo.lock`, and `pnpm-lock.yaml`, commits with `git commit -s` and a `Co-authored-by` trailer, runs `scripts/desktop_release.py validate` against that commit, and (in `publish` mode) force-pushes only that branch and creates or updates a pull request against `main`."
    entry_class: FACT
    evidence:
      - "scripts/prepare-desktop-release.sh"
  - statement: "`scripts/desktop_release.py`'s `CANDIDATE_FILES` set -- `.release/desktop-candidate.json`, `CHANGELOG.md`, `desktop/package.json`, `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`, `desktop/src-tauri/Cargo.lock`, `pnpm-lock.yaml` -- is the complete allow-list of paths a candidate commit may touch, and its `REQUIRED_CANDIDATE_FILES` subset (all of the above except the two lockfiles) must all be present; `validate()` raises if the candidate's `git diff-tree` changed set contains anything outside `CANDIDATE_FILES` or omits anything in `REQUIRED_CANDIDATE_FILES`."
    entry_class: FACT
    evidence:
      - "scripts/desktop_release.py"
  - statement: "`desktop_release.py validate()` additionally requires: the candidate commit has exactly one parent and that parent equals the `base_sha` recorded in `.release/desktop-candidate.json` (i.e. the candidate is exactly one commit directly above the frozen `main` tip it was cut from); the version strings in `desktop/package.json`, `desktop/src-tauri/tauri.conf.json`, and `desktop/src-tauri/Cargo.toml` all equal the target version; the commit carries exactly one `Signed-off-by` trailer matching its author and at least one `Co-authored-by` trailer."
    entry_class: FACT
    evidence:
      - "scripts/desktop_release.py"
  - statement: "`desktop_release.py validate()` also requires the changelog to contain exactly one `## v<version>` block, deterministically re-rendered from the recorded `base_sha` and the previous release's ledger (splitting commits into a \"Desktop and shared changes\" section -- paths under `desktop/`, `crates/buzz-core/`, `crates/buzz-persona/`, `crates/buzz-sdk/`, `crates/buzz-agent/`, `crates/buzz-media/` -- and an \"Other repository changes\" section), matching byte-for-byte, and every commit SHA named in that block must appear exactly once and match the deterministically computed commit set."
    entry_class: FACT
    evidence:
      - "scripts/desktop_release.py"
  - statement: "The `Desktop Release Candidate` GitHub Actions workflow triggers on `pull_request` to `main` and, only when the PR's head ref starts with `version-bump/`, re-runs `scripts/desktop_release.py validate --candidate HEAD --version \"$VERSION\"` (with `VERSION` taken from the branch name) as its sole check step."
    entry_class: FACT
    evidence:
      - ".github/workflows/desktop-release-candidate.yml"
  - statement: "RELEASING.md instructs squash-merging the desktop candidate PR only after all protected-branch checks and the `Desktop Release Candidate` check pass, states the merge is \"the human authorization event\" (an authorized owner/admin bypass is treated the same way), and states unrelated changes later reaching `main` do not invalidate the reviewed candidate."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "For a merged PR whose head ref matches `version-bump/<version>`, `.github/workflows/auto-tag-on-release-pr-merge.yml` runs `scripts/verify-desktop-release-merge.sh`, which: re-fetches the PR from the GitHub API and asserts its `merged`, `head.sha`, `head.ref`, `head.repo.full_name`, `base.ref`, `merge_commit_sha`, and `merged_at` fields all match the values carried on the workflow's own closed-PR event, rather than trusting the event alone; requires the candidate commit to have exactly one parent and that parent to be an ancestor of `origin/main`; extracts `scripts/desktop_release.py` and `scripts/required-check-succeeded.jq` from that parent commit (not from the candidate itself, so a release PR cannot alter the code that validates it) and reruns `desktop_release.py validate` against the candidate using that extracted copy."
    entry_class: FACT
    evidence:
      - "scripts/verify-desktop-release-merge.sh"
  - statement: "`scripts/verify-desktop-release-merge.sh` further requires a fixed list of 14 required checks (naming both a display name and an integration/App id, e.g. `Desktop Release Candidate:15368` and `DCO Check:1455659`) to have succeeded at the candidate SHA, read via `gh api ... check-runs?filter=latest`; the script's own comment states `filter=latest` is deliberate because GitHub exposes no per-rerun creation time, so an ordinary check rerun after merge replaces the visible attempt and is treated as not having succeeded at merge time."
    entry_class: FACT
    evidence:
      - "scripts/verify-desktop-release-merge.sh"
  - statement: "After `scripts/verify-desktop-release-merge.sh` succeeds, `.github/workflows/auto-tag-on-release-pr-merge.yml` requests a short-lived installation token for the dedicated `buzz-release-bot` GitHub App and uses it to create the tag `desktop-v<version>` at the PR's `head.sha` (not the squash merge commit) via the GitHub refs API; a pre-existing tag at the same SHA is treated as a benign concurrent-retry race and skipped, while a pre-existing tag at any other SHA is a hard `::error::` failure."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "RELEASING.md states the `desktop-v<version>` tag triggers `release.yml`, which builds and stages all platform artifacts and publishes the versioned release only after the complete set succeeds, updating the rolling auto-updater manifest last, and only for stable (non-prerelease) versions -- this node treats `release.yml`'s own build/publish/promotion behavior as out of scope, owned by the sibling full-release node (see Boundary)."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Troubleshooting section states that a stale or unmergeable desktop candidate must not be fixed by manually updating the branch or weakening the ruleset; the fix is to re-run `just release-desktop <version>` from current `main`, which regenerates the candidate, reruns CI, and requires a fresh trusted approval on the new head, and that the post-merge verifier refuses to tag a squash whose parent differs from the recorded candidate base or whose tree differs from the validated PR head."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Prerequisites section lists, for the desktop release lane: write access to `block/buzz`; an `origin` remote configured to the canonical `block/buzz` repository; a `gh` CLI authenticated with permission to push the candidate branch and open its pull request; the default `main` ruleset configured for squash-only merging, strict required checks, stale-review dismissal, and the `Desktop Release Candidate` check; release tag ruleset `14378754` active for `desktop-v*` and `mobile-v*` with `buzz-release-bot` as its sole always-bypass actor; the `buzz-release-bot` App's credentials configured for GitHub Actions; and the GitHub Actions variables/secrets `BUZZ_RELEASE_TAGGER_CLIENT_ID`, `BUZZ_RELEASE_TAGGER_PRIVATE_KEY`, `OSX_CODESIGN_ROLE`, `CODESIGN_S3_BUCKET`, `BUZZ_UPDATER_PUBLIC_KEY` or `SPROUT_UPDATER_PUBLIC_KEY`, `TAURI_SIGNING_PRIVATE_KEY`, and `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Internal Releases section states that a Block-internal desktop build is cut by starting the private \"Release Desktop\" Buildkite pipeline (`buildkite.com/runway/sprout-releases`) and entering the exact public source tag as `desktop_ref=desktop-v<version>`, that a generic `v<version>` tag is intentionally rejected, and that the rest of that private pipeline's contract is documented in the `buzz-releases` repository's own README rather than in this repository."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "This repository's own contributor guide states that the separate `squareup/buzz-releases` repository runs Buildkite pipelines producing Block-signed macOS and iOS builds carrying a `-block` desktop version suffix, and that this repository (`block/buzz`) is the OSS source those pipelines consume -- `buzz-releases` is not checked out here and its pipeline internals could not be inspected as part of authoring this node."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Issue #1292's own alias comment and Objective both name the target path `launchpad/docs/corpus/releases/desktop-candidate.md`, and at this node's recorded revision the `launchpad/docs/corpus/releases/` directory does not exist on `origin/launchpad` -- confirmed by requesting that path from `origin/launchpad` and getting a `fatal: path ... does not exist` error, not assumed."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/launchpad', path='launchpad/docs/corpus/releases') -> fatal: path 'launchpad/docs/corpus/releases' does not exist in 'origin/launchpad'"
  - statement: "Sibling issue #1293 (`task: document releases/desktop-release.md`) targets `launchpad/docs/corpus/releases/desktop-release.md` as the canonical node for the full release -- from the `desktop-v<version>` tag through `release.yml`'s build, publish, and auto-update promotion -- and was open and unmerged at the time this node was authored, so it is not yet a valid `relationships` target."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1293 issue body"
---

# Cutting a desktop release candidate

How to produce and land an immutable, reviewed desktop release candidate --
from running `just release-desktop <version>` through the moment the
`desktop-v<version>` git tag exists. What happens after the tag exists
(building, publishing, and promoting artifacts) is a separate node; see
Boundary below.

## Before you start

- A clean, up-to-date checkout of `main` in the canonical `block/buzz`
  repository, with `origin` configured to that repository.
- `gh` CLI authenticated with permission to push a `version-bump/<version>`
  branch and open or update its pull request.
- Write access to `block/buzz`, since `just release-desktop` runs locally
  under the operator's own GitHub permissions (candidate branch creation is
  deliberately **not** delegated to the release App -- see Prerequisites,
  below).

## Prerequisites (platform state)

Operating this flow at all depends on repository configuration that is set up
once, not per release:

- The default `main` branch ruleset configured for squash-only merging,
  strict required checks, stale-review dismissal, and the **Desktop Release
  Candidate** check as required.
- Release tag ruleset `14378754`, active for `desktop-v*` and `mobile-v*`,
  with creation/update/deletion/non-fast-forward protection and the
  `buzz-release-bot` GitHub App as its sole always-bypass actor.
- The `buzz-release-bot` App's credentials available to GitHub Actions, plus
  the GitHub Actions variables/secrets `BUZZ_RELEASE_TAGGER_CLIENT_ID`,
  `BUZZ_RELEASE_TAGGER_PRIVATE_KEY`, `OSX_CODESIGN_ROLE`,
  `CODESIGN_S3_BUCKET`, `BUZZ_UPDATER_PUBLIC_KEY` (or
  `SPROUT_UPDATER_PUBLIC_KEY`), `TAURI_SIGNING_PRIVATE_KEY`, and
  `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`.

None of these are steps an operator performs per release; they are named here
because a failure caused by one of them missing looks like a broken release
flow rather than a configuration gap.

## Cut the candidate

1. From a clean, up-to-date `main` checkout, run `just release-desktop
   <version>` (or `just release-desktop patch`/`just release-desktop` with no
   argument, which computes the next patch version automatically). This runs
   `scripts/prepare-desktop-release.sh`.
2. The script fetches `origin/main` and existing tags, checks out a
   `version-bump/<version>` branch from the fetched `main` tip, bumps the
   desktop version manifests, and runs `scripts/desktop_release.py generate`
   to rewrite `CHANGELOG.md` and write `.release/desktop-candidate.json` (the
   candidate's `base_sha`, the previous release's tag/base/merge SHAs, the
   target tag, and a commit count).
3. The script stages exactly the candidate file set — `.release/desktop-candidate.json`,
   `CHANGELOG.md`, `desktop/package.json`,
   `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`,
   `desktop/src-tauri/Cargo.lock`, `pnpm-lock.yaml` — commits with `git commit
   -s` plus a `Co-authored-by` trailer, and self-validates with
   `scripts/desktop_release.py validate` before pushing anything.
4. In `publish` mode (the `just release-desktop` default), the script
   force-pushes only the `version-bump/<version>` branch and creates or
   updates a pull request against `main` recording the frozen base, the
   reviewed candidate SHA, the previous desktop release, and the proposed
   `desktop-v<version>` tag.
5. Review the PR: the exact candidate SHA, the generated changelog block, and
   CI, including the **Desktop Release Candidate** check, which independently
   reruns `desktop_release.py validate` against the PR head. Regenerating or
   re-pushing the branch produces a new candidate and requires checks to run
   again from scratch.
6. **Squash merge** the PR once every protected-branch check, including
   **Desktop Release Candidate**, passes. The merge is the human
   authorization event. Unrelated commits that land on `main` afterward do
   not invalidate the reviewed candidate.
7. On merge, `auto-tag-on-release-pr-merge.yml` runs
   `scripts/verify-desktop-release-merge.sh`, which independently re-reads
   the PR from the GitHub API (rather than trusting the workflow's own event
   payload), re-extracts and reruns the validator from the candidate's parent
   commit, and confirms a fixed list of required checks succeeded at the
   candidate SHA. If verification passes, the workflow mints a short-lived
   `buzz-release-bot` App token and creates the immutable tag
   `desktop-v<version>` at the PR's head SHA — not at the later squash
   commit.
8. Once the tag exists, the candidate-cutting task described by this node is
   complete. Confirm the tag with `git ls-remote origin
   refs/tags/desktop-v<version>` or `gh api
   repos/block/buzz/commits/desktop-v<version>`.

## Verification

- The **Desktop Release Candidate** check on the PR, and the independent
  re-validation `verify-desktop-release-merge.sh` performs at merge time, are
  the two points where the candidate's shape (version-only diff, single
  commit above a protected `main` ancestor, matching manifest versions, a
  deterministic changelog block, required trailers) is actually enforced —
  not merely documented.
- After the tag is created, confirm it points at the PR's head SHA (not the
  squash merge commit) via `gh api repos/block/buzz/commits/desktop-v<version>`.

## Rollback / recovery

- **Candidate branch is stale or cannot be squash-merged.** Do not update the
  branch manually and do not weaken the ruleset. Re-run `just release-desktop
  <version>` from current `main`; this regenerates the candidate, reruns CI,
  and requires a fresh trusted approval on the new head.
- **`just release-desktop` fails with "must be on main branch."** Switch to
  `main` and pull latest before running the recipe again.
- **`just release-desktop` fails with "working tree is dirty."** Commit or
  stash local changes first.
- **A rerun of a required check happens after merge.** `verify-desktop-release-merge.sh`
  reads check runs with `filter=latest`, so a post-merge rerun replaces the
  visible attempt and deliberately fails the tag-creation step closed rather
  than trusting a check that reran after the merge event it is meant to
  attest to. The recovery is a new candidate version, not a retry of the
  blocked tag.
- **Tag creation appears to fail but the tag already exists at the expected
  SHA.** The auto-tag workflow treats this as a benign concurrent-retry race
  and exits successfully rather than erroring.

## Internal (Block) handoff

Cutting the public `desktop-v<version>` tag does not, by itself, produce a
Block-signed internal build. A Block operator separately starts the private
**Release Desktop** Buildkite pipeline
(`buildkite.com/runway/sprout-releases`) and enters the exact tag as
`desktop_ref=desktop-v<version>`; a generic `v<version>` tag is intentionally
rejected. That pipeline lives in the separate `squareup/buzz-releases`
repository, which is not part of this checkout and was not inspected while
writing this node — this node records only that the handoff exists and what
this repository's own documentation says about it (an exact-tag input,
Block-signed macOS and iOS builds with a `-block` desktop version suffix),
not the pipeline's internal steps. The rest of that private pipeline's
contract is documented in the `buzz-releases` repository's own README, per
this repository's own pointer to it.

## See also

- `RELEASING.md` — the authoritative source this node summarizes into
  ordered steps; read it directly for the relay and mobile lanes, which this
  node does not cover.
- `releases/desktop-release.md` — the sibling full-release node for what happens
  after the `desktop-v<version>` tag exists (`release.yml`'s build, publish, and
  auto-update promotion); see Boundary.

## Boundary

This node covers only candidate-cutting: generating the candidate commit,
review, squash merge, and the tag being created. It does not cover:

- **What happens once the tag exists** — `release.yml`'s builds, the
  versioned GitHub release, or the separate manual **Promote OSS Desktop
  Auto-Update** workflow that updates `buzz-desktop-latest`/`latest.json`.
  That is `releases/desktop-release.md`'s subject (see the provenance
  ledger for this node's own authoring-time state).
- **The relay and mobile release lanes.** Both are documented in
  `RELEASING.md` alongside desktop but are structurally different (a
  metadata PR for relay; immutable tags cut directly from `main` with no PR
  at all for mobile) and are out of scope here.
- **The Signed macOS Canary workflow.** It builds an unsigned-for-distribution,
  short-lived test artifact from `main` and has no release permissions; it is
  not part of the candidate-cutting flow this node documents.
- **The private `buzz-releases` Buildkite pipeline's internal steps.** Named
  as an external handoff target only; its contents were not, and could not
  be, inspected from this checkout.

## Relationships

None declared. `launchpad/docs/corpus/releases/` does not exist on
`origin/launchpad` at this node's recorded revision, so there is no merged
sibling node in this subject area to point at yet. The natural future edges
are a `references` (or `part-of`) pair with the sibling full-release node
once issue #1293 merges, and possibly a `references` edge toward
`architecture-containers-desktop` (what the desktop container is) — left
undeclared here rather than invented, per this corpus's own rule that a
`relationships[].target` naming an id no loaded node carries is a hard
validation error.

## Scope and omissions

**This node covers** the desktop release-candidate procedure: running `just
release-desktop`, what `scripts/prepare-desktop-release.sh` and
`scripts/desktop_release.py generate`/`validate` do, what the **Desktop
Release Candidate** CI check and `scripts/verify-desktop-release-merge.sh`
each independently enforce, how the `desktop-v<version>` tag is created, the
platform prerequisites the flow depends on, and the documented (but not
internally inspected) handoff to Block's private Buildkite pipeline.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `release.yml`'s build/publish/promotion behavior after the tag exists | `releases/desktop-release.md` |
| The relay release lane | `releases/relay-release.md` |
| The mobile candidate and release lanes | `releases/mobile-candidate.md`, `releases/mobile-release.md` |
| The Signed macOS Canary workflow | `RELEASING.md` directly; no corpus node yet |
| The private `buzz-releases` Buildkite pipeline's internal contract | the `buzz-releases` repository's own README (external, per this repository's own ecosystem table) |

**Expected but not verified when this node was written:**

- **No end-to-end run of `just release-desktop` was performed while
  authoring this node.** Every claim above is grounded in reading the
  scripts and workflow YAML that implement the flow, not in having executed
  it against a real `main` tip and observed the tag actually appear.
- **Whether the 14 required-check names and integration IDs hardcoded in
  `scripts/verify-desktop-release-merge.sh` currently match the repository's
  live branch protection configuration** was not independently queried
  against GitHub's ruleset/branch-protection API — only the script's own
  source was read.
- **Whether `architecture-containers-desktop` is the right eventual
  `references` target**, versus no cross-reference at all, was not resolved
  — flagged in *Relationships* above as a future decision, not settled here.
