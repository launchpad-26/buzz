---
id: releases-mobile-release
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
  - statement: "node.schema.json's type enum includes release (singular), one of thirteen corpus-surface values reused from PRD #602's own enumerated list."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "launchpad/docs/corpus/templates/procedure.md is merged on origin/launchpad, and its own Boundary section uses 'cut a relay release' as the worked example distinguishing a procedure (a task the reader chooses to perform on their own schedule, sequenced in the order its steps must happen) from a runbook (a response to an already-firing operational condition) -- this node's subject fits the procedure shape."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "RELEASING.md states Buzz has three independent release lanes (desktop, relay, mobile); mobile 'uses immutable release-candidate tags cut directly from remote main' rather than a release pull request, and there is 'no mobile release branch, stable mobile tag alias, finalization step, or mobile GitHub Release'."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Mobile section states step 2, 'Build the exact tag,' as: enter the candidate tag as mobile_ref in the private Buzz mobile Buildkite pipeline, because 'OSS CI deliberately cannot trigger that private pipeline'; the tag supplies both source commit and release version, Flutter receives the clean marketing version X.Y.Z, and Buildkite's own monotonically increasing build number supplies the platform build number."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's Mobile section states step 3, 'Promote tested artifacts,' as: promote the already-built signed artifact for each platform through its store workflow, recording the exact tag with the build or rollout record, and that 'No source ref is changed and no final build is cut' for this step."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md states the iOS and Android artifacts for one marketing version may come from different RC tags of that version (its own example: iOS shipping mobile-v0.5.0-rc.2 while Android ships mobile-v0.5.0-rc.3), that each platform's exact candidate tag is its own source record, and that 'There is intentionally no single selected or final candidate for the marketing version.'"
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "mobile/pubspec.yaml's committed version field reads exactly '0.0.0+1', and RELEASING.md states this value is 'a valid, visibly non-release fallback for local development and validation builds' only, while 'Release jobs always inject both version fields' at build time rather than reading the committed value."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
      - "RELEASING.md"
  - statement: "RELEASING.md states mobile/CHANGELOG.md 'is retained as historical release data' but 'is not a release ledger for this flow'; the file itself is organized under per-tag headings such as 'mobile-v0.4.11' and 'mobile-v0.4.9', each listing merged PRs."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - "mobile/CHANGELOG.md"
  - statement: "RELEASING.md's 'What Gets Published' section states mobile 'publishes only annotated mobile-vX.Y.Z-rc.N git tags,' that 'Store artifacts and rollout records retain the exact tag they used,' and that mobile 'does not publish a GitHub Release or a stable mobile-vX.Y.Z alias' -- in contrast to desktop, which publishes two GitHub releases in the same section."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's 'Internal Releases' section directs triggering the private 'Release Mobile' pipeline at https://buildkite.com/runway/buzz-mobile-releases with an exact RC tag for the platform build being cut, and points to the buzz-releases README (https://github.com/squareup/buzz-releases#cutting-a-release) 'for the rest of the private pipeline contract.'"
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's 'Release Retry' section states 'Mobile intentionally has no branch or arbitrary-ref fallback. The private Buildkite pipeline accepts only an exact candidate tag.'"
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "scripts/mobile-release.sh and .github/workflows/mobile-release-candidate.yml, read in full while writing this node, implement and dispatch only the candidate-publication step (resolving origin/main, computing the next RC number, publishing the annotated tag via the buzz-release-bot App); neither file contains any build, store-promotion, or private-pipeline-trigger logic, confirming the build/promote steps this node documents happen entirely outside this repository."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
      - ".github/workflows/mobile-release-candidate.yml"
  - statement: "A repository-wide search for App Store / Google Play / TestFlight / Play Console / Fastlane terms across .github/workflows, scripts/, RELEASING.md, and mobile/ found no script, workflow, or config implementing a store build or promotion step in this repository -- the only hits outside this node's evidence above were mobile/README.md's App Store push-notification (APNs) profile section and two buzz-push-gateway migration files naming push 'application profiles,' both unrelated to release publishing."
    entry_class: FACT
    evidence:
      - "grep(pattern='app store|google play|testflight|play console|fastlane', paths=['.github/workflows', 'scripts', 'RELEASING.md', 'mobile', 'CLAUDE.md']) -> mobile/README.md (APNs push-profile section, unrelated); repo-wide re-run additionally surfaced SECURITY.md, crates/buzz-push-gateway/migrations/0002_application_profiles.sql, crates/buzz-push-gateway/migrations/0004_dogfood_only_profile.sql, launchpad/docs/Observability/current-state/web.md -- all push-notification/profile or unrelated content, none describing a store build or promotion step"
  - statement: "git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run while writing this node, lists no releases/ directory and no file at launchpad/docs/corpus/releases/mobile-release.md -- confirming this task's target document does not already exist on the merge target, and that the corpus has no release-typed node yet for this node to relate to."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus', run while writing this node) -> no releases/ subdirectory present"
  - statement: "Issue #1294 ('task: document releases/mobile-candidate.md') is OPEN, and its corresponding node exists only as an unpushed commit (56941259bc58aafebb33f775dca44ffb1721c435) on the local branch task/1294-release-mobile-candidate -- no pull request for that branch was found on launchpad-26/buzz -- so releases-mobile-candidate is not a valid relationship target from this node."
    entry_class: FACT
    evidence:
      - "gh_issue_view(repo='launchpad-26/buzz', number=1294) -> state OPEN, title 'task: document releases/mobile-candidate.md'"
      - "git_branch(--contains 56941259bc58aafebb33f775dca44ffb1721c435) -> task/1294-release-mobile-candidate (local only)"
      - "gh_pr_list(repo='launchpad-26/buzz', search='mobile-candidate', state='all') -> no PR for that branch"
  - statement: "Issue #1301 ('task: document releases/versioning.md') is OPEN and has no corpus node at this revision, so releases-versioning is likewise not a valid relationship target from this node."
    entry_class: FACT
    evidence:
      - "gh_issue_view(repo='launchpad-26/buzz', number=1301) -> state OPEN, title 'task: document releases/versioning.md'"
  - statement: "CLAUDE.md's ecosystem table names squareup/buzz-releases as 'Buildkite pipelines producing Block-signed macOS + iOS builds with a -block desktop version suffix,' and its ecosystem diagram states buzz-releases handles 'desktop + mobile builds -> Artifactory, GitHub, Mobile Releases' -- consistent with, but not itself proof of, squareup/buzz-releases being the private repository that performs the App Store Connect / Google Play Console publishing RELEASING.md's promote step describes, since that private repository could not be inspected from here."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md"
      - "RELEASING.md"
    confidence: 0.6
  - statement: "Issue #1295's Definition of Done requires this node to state goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands/config rather than give generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1295 definition of done"
  - statement: "Parent Feature #619 ('feature: development release and governance corpus exists') is the PRD this task and its sibling release/governance corpus tasks (including #1294 and #1301) are children of."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#619"
---

# Mobile release: build and promote

Build the exact `mobile-vX.Y.Z-rc.N` candidate tag through the private Buzz
mobile Buildkite pipeline and promote the resulting signed per-platform
artifact to the app stores -- the task performed once a candidate tag
already exists, and before end users receive the new mobile build.

## Before you start

- An existing, immutable `mobile-vX.Y.Z-rc.N` tag already published on
  `block/buzz` (produced by the mobile release-candidate procedure -- see
  *See also*; cutting that tag is not this node's subject).
- Access to the private Buzz mobile Buildkite pipeline ("Release Mobile",
  `https://buildkite.com/runway/buzz-mobile-releases`), external to this OSS
  repository. Nothing in this repository's own CI can trigger it.

## Build and promote a mobile release

1. Enter the candidate tag as `mobile_ref` in the private "Release Mobile"
   Buildkite pipeline. OSS CI in this repository deliberately cannot trigger
   that private pipeline. The tag supplies both the source commit and the
   release version to the build.
2. The build derives Flutter's clean marketing version `X.Y.Z` from the tag
   itself; Buildkite's own monotonically increasing build number supplies
   the platform build number. `mobile/pubspec.yaml`'s committed
   `version: 0.0.0+1` is a placeholder for local development and validation
   builds only -- release jobs always inject both version fields at build
   time rather than reading the committed value.
3. Promote the already-built, signed artifact for each platform (iOS,
   Android) through that platform's own store workflow (App Store, Google
   Play). No source ref changes and no new build is cut for this step --
   promotion moves an already-tested artifact forward, it does not rebuild.
4. Record the exact `mobile-vX.Y.Z-rc.N` tag used with the store's build or
   rollout record. The iOS and Android artifacts for one marketing version
   may come from different RC tags of that version (for example, iOS
   shipping `-rc.2` while Android ships `-rc.3`); each platform's own exact
   candidate tag is its source record, and there is intentionally no single
   "final" candidate tag for a marketing version.

## Verify

Mobile publishes only annotated `mobile-vX.Y.Z-rc.N` git tags in this
repository -- never a GitHub Release and never a stable `mobile-vX.Y.Z`
alias tag. No script or workflow in this repository confirms a store
submission's status (TestFlight processing, Play Console review, rollout
percentage); that confirmation happens entirely inside the private
Buildkite pipeline and each store's own console, outside what this
repository can check -- see *Scope and omissions*.

## See also

- The mobile release-candidate procedure (produces the
  `mobile-vX.Y.Z-rc.N` tag this node's step 1 consumes) -- issue #1294,
  not yet a merged corpus node at this revision; no relationship declared,
  see *Relationships*.
- A mobile release-versioning reference (version-source semantics across
  lanes) -- issue #1301, not yet a merged corpus node at this revision.
- `RELEASING.md` -- the source this entire node is drawn from, including
  the desktop and relay lanes this node does not cover.

## Boundary

This node does not describe:

- **Cutting the candidate tag itself** -- resolving the exact `origin/main`
  commit, computing the next RC number, and publishing the annotated tag
  through `scripts/mobile-release.sh candidate` and the
  `mobile-release-candidate.yml` workflow. That is issue #1294's subject;
  both files were read in full while writing this node and contain no
  build or store-promotion logic, only the publish step.
- **What happens inside the private Buildkite pipeline**, or **App Store
  Connect / Google Play Console's own configuration and review process** --
  neither is present in this OSS repository. `CLAUDE.md`'s ecosystem table
  names `squareup/buzz-releases` as producing "Block-signed macOS + iOS
  builds" via Buildkite, which is consistent with it owning this step, but
  this repository holds no script, workflow, or config that performs or
  confirms it -- see *Scope and omissions*.
- **The desktop and relay release lanes** -- their own sections of
  `RELEASING.md`, not this node's subject.
- **Mobile version-source semantics in general** (how `X.Y.Z` and the RC
  suffix relate across lanes) -- issue #1301's subject, once written.
- **Acquiring the underlying skill of using Buildkite or a store console
  from scratch**, for a newcomer -- a tutorial, which has no corpus
  template as of this writing.
- **Why the mobile lane is shaped this way** (tags instead of a release
  branch, no finalization step) -- a concept/explanation node, if one is
  later written, would own that; this node only states the shape as read
  from `RELEASING.md`.

## Relationships

Declared: none. `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`, run while writing this node, lists no `releases/`
directory at all -- the corpus had no `release`-typed node yet for this
node to relate to at that time. Both `releases-mobile-candidate` and
`releases-versioning` have since landed in this same integration, so the
natural `references` edges to them now resolve. They are not added here:
wiring them in now, under the pressure of a pre-merge fix pass, risks the
same kind of error this fix pass exists to catch. Adding them belongs to a
dedicated pass across the whole `development`/`governance`/`releases` shelf
once all 37 nodes are stable.

## Scope and omissions

**This node covers** the mobile release process past the candidate stage:
entering the candidate tag into the private Buildkite pipeline, how the
build derives its version, and promoting an already-built signed artifact
through each platform's store workflow, as described in `RELEASING.md`'s
Mobile, Internal Releases, and What Gets Published sections.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Cutting the `mobile-vX.Y.Z-rc.N` candidate tag | `releases/mobile-candidate.md` |
| Mobile version-source semantics across lanes | `releases/versioning.md` |
| Desktop and relay release lanes | `releases/desktop-candidate.md`, `releases/desktop-release.md`, `releases/relay-release.md` |
| The private Buildkite pipeline's internal build steps | `squareup/buzz-releases` (per `CLAUDE.md`'s ecosystem table) -- not inspectable from this OSS repository |
| App Store Connect / Google Play Console's own publishing and review steps | Same private-pipeline boundary -- not inspectable from this OSS repository |
| Push-notification / APNs App Store profile configuration | `mobile/README.md` -- a different concern (runtime push config, not release publishing) |

**Expected but not verified when this node was written:**

- **No build or promotion was executed while writing this node.** Every
  claim above is read from `RELEASING.md` and the two candidate-stage
  source files (`scripts/mobile-release.sh`,
  `.github/workflows/mobile-release-candidate.yml`), not from running a
  real build/promote cycle -- this repository holds nothing to execute for
  those steps, since they run entirely inside the private Buildkite
  pipeline.
- **Whether `squareup/buzz-releases` is in fact what performs the App
  Store/Google Play steps** was not established directly -- only inferred
  from `CLAUDE.md`'s ecosystem table and diagram, at confidence 0.6 (see
  the evidence ledger). The private repository was not inspectable from
  here.
- **Whether any additional access, credentials, or setup is required to use
  the private Buildkite pipeline beyond what `RELEASING.md` states** was
  not established -- `RELEASING.md`'s Prerequisites section lists
  requirements for the desktop lane and for mobile candidate publication,
  but none specifically for the build/promote steps this node covers.
