---
id: platforms-mobile-release-candidate
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
  - statement: "scripts/mobile-release.sh's `candidate` subcommand validates its X.Y.Z argument as a clean semver, requires a clean git working tree, requires the origin remote to be canonical block/buzz, and requires gh >= 2.87.0 before resolving anything."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:111-117"
      - "scripts/mobile-release.sh:46-55"
  - statement: "The `candidate` subcommand resolves the exact current commit of origin/main (never the operator's own checked-out HEAD) and derives the next release-candidate number by scanning existing remote mobile-vX.Y.Z-rc.* tags for that marketing version, taking the highest existing number plus one."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:94-107"
      - "scripts/mobile-release.sh:119-131"
  - statement: "The subcommand then dispatches the mobile-release-candidate.yml GitHub Actions workflow with the resolved version, candidate_number, and target_sha, and blocks on `gh run watch --exit-status` until that run completes."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:131-152"
  - statement: "After the workflow run succeeds, the subcommand re-fetches origin/main and the newly published tag and fails loudly if origin/main moved during publication or if the published tag does not resolve to exactly the requested commit, rather than silently trusting the workflow's own success."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:154-165"
  - statement: "RELEASING.md documents this same flow in prose: publish a candidate with scripts/mobile-release.sh candidate X.Y.Z, enter the exact resulting tag as mobile_ref in the private Buzz mobile Buildkite pipeline (OSS CI cannot trigger that private pipeline), then promote the already-built signed artifact per platform through its store workflow -- and states plainly that mobile has no release branch, stable tag alias, finalization step, or mobile GitHub Release."
    entry_class: FACT
    evidence:
      - "RELEASING.md:92-120"
  - statement: "The mobile-release-candidate.yml workflow refuses to run unless it was dispatched from refs/heads/main and unless the repository is exactly block/buzz, then mints a release-tagger GitHub App token scoped to Contents:write before delegating the actual tag creation to scripts/publish-mobile-release-candidate.sh."
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml:32-53"
      - ".github/workflows/mobile-release-candidate.yml:55-69"
  - statement: "scripts/publish-mobile-release-candidate.sh does not trust its own caller's inputs: it independently re-resolves block/buzz's live main SHA and rejects a mismatch against target_sha, independently re-derives the next candidate number from live matching-refs and rejects a mismatch against the requested candidate_number, and only then creates the annotated tag object and its ref through the GitHub API."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh:27-47"
      - "scripts/publish-mobile-release-candidate.sh:49-64"
  - statement: "After creating the ref, the publisher script verifies through a second, independent GitHub API read that the published ref is a true annotated tag object (not a lightweight tag) and that the annotated tag object points directly at the requested commit, before reporting success."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh:66-78"
  - statement: "Both scripts/mobile-release.sh and scripts/publish-mobile-release-candidate.sh source scripts/release-rulesets.sh, whose require_release_tag_ruleset confirms GitHub ruleset 14378754 is 'active', scoped to exactly refs/tags/mobile-v* with no exclusions, enforcing creation/deletion/non_fast_forward/update, and that the calling GitHub App token's current_user_can_bypass is reported as 'always'."
    entry_class: FACT
    evidence:
      - "scripts/release-rulesets.sh:24-54"
      - "scripts/mobile-release.sh:20-21"
      - "scripts/publish-mobile-release-candidate.sh:9-10"
  - statement: "RELEASING.md's Prerequisites section states mobile candidate publication requires workflow-dispatch access and the buzz-release-bot App (Contents write, Metadata read, an always-bypass on the mobile-v* tag ruleset) because strict tag protection denies direct human tag creation, and explicitly states it does NOT require GitHub Releases permission, repository Administration permission, or a mobile release-branch ruleset."
    entry_class: FACT
    evidence:
      - "RELEASING.md:277-284"
  - statement: ".github/workflows/ci.yml's changed-paths filter names a `mobile` group covering mobile/**, scripts/mobile-release.sh, scripts/publish-mobile-release-candidate.sh, scripts/release-rulesets.sh, the two mobile release test scripts, and the mobile-release-candidate.yml workflow file itself; when any of those change, the 'Mobile release contract' step runs scripts/test-mobile-release-contract.sh and scripts/test-mobile-release-candidate-publisher.sh."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:63-74"
      - ".github/workflows/ci.yml:85-88"
  - statement: "scripts/test-mobile-release-contract.sh exercises the full operator command end-to-end against real local git remotes and a stubbed gh: it asserts publication from a stale local clone still targets the exact current remote main tip; candidate numbers sequence monotonically from the highest existing exact remote RC tag while ignoring gaps, zero-padded, and other-version tags; a failed, URL-less, wrong-repository, or multi-URL workflow dispatch fails closed and creates no tag; a main-tip race during publication is detected and fails rather than misreporting the stale tag as current; a non-canonical origin and an unsupported gh version are both rejected before any dispatch; and a dirty working tree or malformed version is rejected before publication."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-contract.sh:130-150"
      - "scripts/test-mobile-release-contract.sh:166-219"
      - "scripts/test-mobile-release-contract.sh:225-268"
  - statement: "The same test file asserts, by name, that the removed `start` and `finalize` subcommands are rejected, that no refs/heads/mobile-release/ branch is ever created, that no stable refs/tags/mobile-v1.2.3 alias is ever created, and greps mobile-release.sh, publish-mobile-release-candidate.sh, and the workflow file to confirm none of them contain `gh release`, a `mobile-release/` branch reference, or `finalize` logic."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-contract.sh:106-114"
      - "scripts/test-mobile-release-contract.sh:270-289"
  - statement: "scripts/test-mobile-release-candidate-publisher.sh exercises scripts/publish-mobile-release-candidate.sh directly against a stubbed gh, asserting it rejects an App token without an always-bypass, a disabled or incomplete tag ruleset, a ruleset that excludes or fails to scope to mobile-v* tags, a moved main branch, a stale candidate number, a lightweight or wrongly-targeted published tag, a nested annotated tag object, a leading-zero version or candidate number, and a non-canonical repository -- while accepting correct sequencing from the highest exact existing candidate even across numeric gaps."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-candidate-publisher.sh:77-136"
      - "scripts/test-mobile-release-candidate-publisher.sh:137-155"
  - statement: "mobile/pubspec.yaml pins version: 0.0.0+1, which RELEASING.md and the mobile release contract test both treat as a valid non-release placeholder that release jobs overwrite, not a version this component bumps in place."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml:4"
      - "RELEASING.md:122-125"
      - "scripts/test-mobile-release-contract.sh:296"
  - statement: "The current operator script, App-backed workflow, publisher script, tag-ruleset guard, and their test coverage are all most recently touched by a single commit."
    entry_class: FACT
    evidence:
      - "git_log(paths='scripts/mobile-release.sh;scripts/publish-mobile-release-candidate.sh;.github/workflows/mobile-release-candidate.yml', ref=131b02f989684117d9ab1dd426f1673fa638e523) -> 21573b6cb 'chore(mobile): lighter-weight release process (#2144)', at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Issue #1260's own Definition of Done requires this node to state responsibility and a well-defined interface/boundary, name dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire containing mobile platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1260 definition of done"
  - statement: "Sibling documents authored under launchpad/docs/corpus/platforms/** for parent Feature #614 use type: platforms as a working convention, even though no platforms-specific corpus template exists yet to formally prescribe that value."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#614 batch dispatch brief for the platforms/** task set"
  - statement: "This node sets type: platforms to follow that sibling convention rather than the merged templates/component.md template's own type: implementation recommendation, because node.schema.json's closed type enum has no member specific to a single platform-lane component and no platforms-specific template exists yet to override the convention with a documented rule."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.55
---

# Mobile release candidate

This node documents one component of Buzz's mobile release lane: the
operator-facing `scripts/mobile-release.sh candidate X.Y.Z` command and the
App-backed publishing pipeline behind it, which together publish an immutable
`mobile-vX.Y.Z-rc.N` git tag from the exact current `origin/main` commit. It
answers what this one component is responsible for, what other components it
calls through, and what depends on it -- not how the mobile app itself is
built, signed, or shipped once a tag exists.

## Responsibility

Publish the next `mobile-vX.Y.Z-rc.N` annotated tag on `block/buzz`, always
from the exact current remote `origin/main` commit, never from the operator's
own checked-out state, and never by moving an existing tag. The mobile lane
has no bump recipe, no release-metadata pull request, and no release branch;
the published tag is simultaneously the source-commit record and the version
record for whichever platform artifact is later built from it.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `scripts/mobile-release.sh candidate X.Y.Z` | CLI subcommand | Operator entry point. Validates a clean `X.Y.Z` semver, a clean working tree, a canonical `block/buzz` origin, and `gh >= 2.87.0`; resolves the exact current `origin/main` commit; dispatches and blocks on the publishing workflow; verifies the result. | `scripts/mobile-release.sh:109-166` |
| `mobile-release-candidate.yml` (`workflow_dispatch`) | GitHub Actions workflow | Inputs: `version`, `candidate_number`, `target_sha`. Runs only when dispatched from `refs/heads/main` on `block/buzz`; mints a `Contents: write` App token; delegates tag creation to the publisher script. | `.github/workflows/mobile-release-candidate.yml:1-69` |
| `scripts/publish-mobile-release-candidate.sh VERSION N SHA` | Internal script, not a direct operator entry point | Re-verifies every input against the live GitHub API rather than trusting its caller, then creates the annotated tag object and its ref. | `scripts/publish-mobile-release-candidate.sh:12-80` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `scripts/release-rulesets.sh` | Supplies `require_canonical_repository` (used by `mobile-release.sh`) and `require_release_tag_ruleset` (used by both scripts) as shared guard logic. | `scripts/release-rulesets.sh:10-54`; `scripts/mobile-release.sh:20-21`; `scripts/publish-mobile-release-candidate.sh:9-10` |
| GitHub repository ruleset `14378754` | The immutability enforcement (`creation,deletion,non_fast_forward,update`) scoped to `refs/tags/mobile-v*` that both scripts verify before publishing. | `scripts/release-rulesets.sh:24-54`; `RELEASING.md:259-263` |
| `buzz-release-bot` GitHub App | The sole actor with an always-bypass on the tag ruleset; mints the `Contents: write` token the workflow uses to create the tag, since strict tag protection denies direct human tag creation. | `.github/workflows/mobile-release-candidate.yml:55-61`; `RELEASING.md:277-284` |
| `gh` CLI, version `>= 2.87.0` | Resolves remote refs and tags, dispatches the workflow, and blocks on `gh run watch --exit-status` for it. | `scripts/mobile-release.sh:23-44` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| RELEASING.md's documented Mobile release flow | Names this exact command as the first of its three operator steps. | `RELEASING.md:92-101` |
| The private Buzz mobile Buildkite pipeline (`buzz-mobile-releases`) | Consumes the resulting `mobile-vX.Y.Z-rc.N` tag as its `mobile_ref` build input; this OSS repository cannot trigger it directly. | `RELEASING.md:102-109`; `RELEASING.md:188-195` |
| `.github/workflows/ci.yml`'s `mobile` changed-paths lane | Runs this component's own test coverage whenever it, or any of its direct dependencies, changes. | `.github/workflows/ci.yml:63-74`; `.github/workflows/ci.yml:85-88` |

## Boundary

This node does not describe:
- The private Buzz mobile Buildkite pipeline's own build, code-signing, or
  Flutter version-injection steps, or the manual store-promotion step after
  a candidate is tested -- those happen in `squareup/buzz-releases`, a
  private repository outside this OSS corpus's reach.
- The desktop or relay release lanes (`just release-desktop`, `just
  release-relay`), which are separate components with their own release
  PRs, tags, and workflows.
- The mobile app's own runtime architecture (Riverpod state management,
  feature-module layout, widget composition) -- this node is about the
  release pipeline, not the application it releases.
- Whether a formal `platforms`-specific corpus template will later
  standardize this document's section shape; that shape is currently
  borrowed from the merged `templates/component.md` template as the closest
  structural fit, per this node's own `INFERENCE` above.

## Relationships

No relationships are declared. Checked: `launchpad/docs/corpus/platforms/`
does not exist on `origin/launchpad` at the recorded revision, so there is no
merged sibling `platforms/**` node, `architecture-component` instance, or
`component` instance yet to target with `part-of`, `depends-on`, or
`references`. The four nodes that do exist on `origin/launchpad`
(`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references`) are procedural meta-documents about
the corpus itself, not subject matter this node's release-pipeline content
would relate to. The first `platforms/**` sibling to merge, or the first
architecture-level mobile-platform node, is the natural moment to revisit
this section.

## Scope and omissions

**This node covers** the responsibility, public interface, and real
dependency edges (both directions) of the mobile release-candidate
publishing component: `scripts/mobile-release.sh candidate`, the
`mobile-release-candidate.yml` workflow it dispatches, and
`scripts/publish-mobile-release-candidate.sh`, which performs the actual
tag creation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Desktop and relay release lanes | `RELEASING.md`'s Desktop and Relay sections; not this issue's scope |
| The private Buildkite pipeline's build/sign/promote steps | `squareup/buzz-releases` (private repository) |
| The mobile app's own runtime architecture | A future mobile-platform architecture corpus node, not yet filed |
| A formal `platforms`-type corpus template | Not yet filed as of this writing; this node follows the working `type: platforms` convention only |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **The private `buzz-mobile-releases` Buildkite pipeline's actual
  configuration was not inspected.** `RELEASING.md` documents that it
  consumes the published tag as `mobile_ref`, but that pipeline lives in the
  private `squareup/buzz-releases` repository, which is outside this OSS
  checkout's reach.
- **Whether other `platforms/**` sibling nodes authored in parallel for
  Feature #614 converge on identical section headings under `type:
  platforms` was not checked**, since `AGENTS.md`'s relationship-resolution
  rule requires checking only `origin/launchpad`, where `platforms/` does
  not yet exist at the recorded revision.
