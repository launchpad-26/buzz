---
id: releases-mobile-candidate
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
  - statement: "Mobile is one of three independent release lanes (desktop, relay, mobile); unlike desktop and relay, it uses immutable release-candidate tags cut directly from remote main rather than a release pull request, and its entry point is scripts/mobile-release.sh candidate X.Y.Z, producing an exact mobile-vX.Y.Z-rc.N source identity as the artifact of record."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "scripts/mobile-release.sh candidate X.Y.Z validates a clean X.Y.Z semver with no leading zeros, requires a clean working tree, requires the git remote origin to point at the canonical block/buzz repository, and requires gh >= 2.87.0, all before doing anything else."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
      - "scripts/release-rulesets.sh"
  - statement: "The script resolves the exact current origin/main commit itself: it reads the advertised OID from git ls-remote, fetches that ref, and fails with 'origin/main moved while it was being resolved' if the fetched OID does not match the advertised one -- it never uses the operator's locally checked-out commit."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
  - statement: "The next candidate number for a given marketing version is computed by listing exact remote tags matching refs/tags/mobile-v<version>-rc.* and taking one more than the highest strictly-numeric (no leading zero) suffix found; tags with a leading-zero suffix (e.g. mobile-v1.2.3-rc.08) or a different marketing version do not match the regex and are ignored, so sequencing continues correctly across gaps and malformed siblings."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
      - "scripts/test-mobile-release-contract.sh"
  - statement: "Publication itself is not performed by the operator's script directly: mobile-release.sh dispatches the mobile-release-candidate.yml workflow via workflow_dispatch on block/buzz with version, candidate_number and target_sha inputs, requires exactly one https://github.com/block/buzz/actions/runs/<id> URL back from the dispatch (failing closed on zero, multiple, or a different-repository URL), and then blocks on gh run watch <id> --exit-status, failing the release if the workflow run fails."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
  - statement: "If the dispatch is rejected because the workflow lacks a workflow_dispatch trigger on main, mobile-release.sh reports 'merge the release-process change before publishing a candidate' rather than a generic dispatch failure."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh"
  - statement: "mobile-release-candidate.yml requires the dispatch ref to be exactly refs/heads/main (rejecting any other ref before checkout), requires the repository to be block/buzz, mints a short-lived GitHub App token via actions/create-github-app-token scoped to contents:write using the BUZZ_RELEASE_TAGGER_CLIENT_ID/BUZZ_RELEASE_TAGGER_PRIVATE_KEY App credentials, and runs scripts/publish-mobile-release-candidate.sh as that App identity; the job's own permissions block only grants contents:read."
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml"
  - statement: "The workflow's concurrency group is mobile-release-candidate-<version> with cancel-in-progress: false, so two dispatches for the same marketing version queue rather than one cancelling the other."
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml"
  - statement: "scripts/publish-mobile-release-candidate.sh independently re-validates every input (version format, candidate-number format, that target_sha is a full 40-character hex commit SHA, and that GITHUB_REPOSITORY is exactly block/buzz) rather than trusting the workflow's dispatch inputs, and calls require_release_tag_ruleset before doing anything else."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh"
  - statement: "require_release_tag_ruleset (scripts/release-rulesets.sh) checks GitHub ruleset 14378754 by ID: enforcement must be active, current_user_can_bypass must be exactly 'always', the rule-type set must be exactly creation,deletion,non_fast_forward,update, the ref_name include list must contain refs/tags/mobile-v*, and the exclude list must be empty -- any deviation fails the publisher closed."
    entry_class: FACT
    evidence:
      - "scripts/release-rulesets.sh"
  - statement: "Before creating a tag, the publisher re-fetches block/buzz's current main SHA via the GitHub API and fails with an explicit 'main moved from requested commit ... to ...' message if it no longer matches target_sha, guarding the same main-tip race the operator script also guards against."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh"
  - statement: "The publisher creates the candidate as a true annotated tag object (POST git/tags with an explicit message 'Buzz Mobile <version> release candidate <N>' and type=commit) and then creates the refs/tags/<tag> ref pointing at that object, rather than creating a lightweight tag ref directly."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh"
  - statement: "After creating the ref, the publisher re-reads it back from the API and independently verifies the published ref is an annotated tag object (not a lightweight tag) pointing at the tag object it just created, and that the tag object's own target is a commit equal to the requested target_sha -- both checks fail closed rather than trusting the create call's response."
    entry_class: FACT
    evidence:
      - "scripts/publish-mobile-release-candidate.sh"
  - statement: "scripts/test-mobile-release-candidate-publisher.sh exercises every one of the publisher's fail-closed branches against a scripted fake gh (ruleset disabled, bypass not 'always', incomplete rule types, ruleset excluding mobile tags, ruleset carrying exclusions, main having moved, a stale/already-used candidate number, a lightweight published tag, the wrong annotated-tag object, an annotated tag pointing at the wrong commit, leading-zero version or candidate numbers, and the wrong GITHUB_REPOSITORY) and asserts each one exits non-zero without publishing."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-candidate-publisher.sh"
  - statement: "scripts/test-mobile-release-contract.sh runs the real mobile-release.sh end to end against a local bare-repo fixture and a scripted fake gh, and asserts: publication from a stale operator clone still targets the exact current remote main (with the stale-checkout note printed to stderr); repeated candidates for the same version sequence monotonically and never move an already-published tag; a rejected or failed App-backed dispatch, a missing/ambiguous/wrong-repository run URL, or a lightweight published tag all fail closed without creating the candidate tag; a main-tip race during publication fails closed and reports the before/after SHAs; publication from a fork remote or with too-old gh is rejected before any dispatch; and a dirty tree or malformed version is rejected before publication."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-contract.sh"
  - statement: "The same test asserts, by name, that removed behavior stays removed: mobile-release.sh no longer accepts a start or finalize subcommand, no refs/heads/mobile-release/ branch is ever created, no stable mobile-vX.Y.Z alias tag (without an -rc.N suffix) is ever created, and none of mobile-release.sh, publish-mobile-release-candidate.sh or mobile-release-candidate.yml contain a gh release call, a mobile-release/ branch reference, or a finalize code path; it also asserts mobile/pubspec.yaml still pins the non-release fallback version 0.0.0+1 and that the Justfile carries no release-mobile, bump-mobile-version or get-current-mobile-version recipe."
    entry_class: FACT
    evidence:
      - "scripts/test-mobile-release-contract.sh"
  - statement: "The two mobile-release test scripts are wired into CI as an unconditional 'Mobile release contract' step inside the changes job of .github/workflows/ci.yml, which runs on every push and every pull request regardless of which paths changed -- this is a different gate from the separate path-filtered mobile (Flutter) and mobile-swift jobs, which only run when the 'mobile' paths-filter (covering mobile/**, the mobile-release scripts, and mobile-release-candidate.yml) reports a match."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Per RELEASING.md, building a candidate is a separate manual step from publishing it: the operator enters the published mobile-vX.Y.Z-rc.N tag as mobile_ref in the private Buzz mobile Buildkite pipeline (linked there as https://buildkite.com/runway/buzz-mobile-releases), because OSS CI in this repository deliberately cannot trigger that private pipeline; Flutter receives the clean marketing version X.Y.Z while Buildkite's own monotonically increasing build number supplies the platform build number."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "Per RELEASING.md, promotion is a third manual step, separate again from building: an already-built, already-signed artifact for each platform is promoted through its own store workflow, the exact candidate tag is recorded alongside the build or rollout record, and neither the source ref nor the build itself changes during promotion -- there is no separate 'finalize' step and no stable tag or GitHub Release is ever produced for mobile."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md states that iOS and Android artifacts for the same marketing version may legitimately come from different candidate tags (its own example: iOS shipping mobile-v0.5.0-rc.2 while Android ships mobile-v0.5.0-rc.3), and that there is intentionally no single selected or final candidate per marketing version -- unlike desktop and relay, mobile has no bump recipe and no release-metadata pull request; its only version authority is the exact published tag."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's own troubleshooting entries for mobile match the fail-closed behavior evidenced above: if commits land after a candidate is published, rerun scripts/mobile-release.sh candidate <version> rather than editing anything; if main moves mid-publication, do not move or delete whatever the App-backed workflow already published at the prior tip, inspect the reported run URL, and rerun for the new tip; if the wrong RC number is selected, inspect the exact remote mobile-v* tags rather than moving or deleting a tag, since candidate numbers are monotonically increasing remote identities; if publication is rejected by repository rules, confirm buzz-release-bot remains the ruleset's sole always-bypass actor and that its Actions credentials are available, rather than granting direct human creation or weakening the ruleset."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's prerequisites section states that mobile candidate publication requires workflow-dispatch access and the existing release App because strict tag protection denies direct human creation; the App must be installed on block/buzz with Contents write and Metadata read, must retain an 'always' bypass on the mobile-v* tag rules, and does not require GitHub Releases permission, repository Administration permission, or any mobile release-branch ruleset; the publisher validates the App token's own effective current_user_can_bypass value rather than reading the ruleset's separate hidden bypass-actor list -- both of which match require_release_tag_ruleset's actual checks in scripts/release-rulesets.sh."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - "scripts/release-rulesets.sh"
  - statement: "CLAUDE.md's ecosystem table names squareup/buzz-releases as the repo whose Buildkite pipelines turn this repo's source into Block-signed macOS and iOS builds, and separately describes it as producing 'desktop + mobile builds → Artifactory, GitHub, Mobile Releases' -- naming 'Mobile Releases' as a third publishing destination distinct from Artifactory and GitHub."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "What 'Mobile Releases' names as a system, and how it relates to the Buildkite 'Release Mobile' pipeline RELEASING.md links to, is not something this repository's source can establish -- squareup/buzz-releases is a separate, private repository this checkout cannot inspect."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md"
      - "RELEASING.md"
    confidence: 0.6
---

# Mobile release candidate

## Goal

Publish an immutable, verifiable `mobile-vX.Y.Z-rc.N` git tag at an exact
`block/buzz` `main` commit, so that a private downstream pipeline can build,
sign, and promote mobile artifacts from a source identity nobody can move
after the fact.

This is the **candidate** stage of the mobile release lane only: publishing
the tag. It is not the build step and not the store-promotion step, both of
which happen outside this repository (see Scope below).

## Prerequisites

- Write access to `block/buzz` and `gh` authenticated with permission to
  trigger `workflow_dispatch`.
- A clean working tree, and a git `origin` remote whose URL is exactly the
  canonical `block/buzz` repository (checked by
  `scripts/release-rulesets.sh`'s `require_canonical_repository`; a fork or
  mirror remote is rejected).
- `gh` CLI version `2.87.0` or newer.
- The GitHub Release tag ruleset (id `14378754`) active on `block/buzz`,
  scoped to `refs/tags/mobile-v*` (and `desktop-v*`) with no exclusions, and
  with the `buzz-release-bot` GitHub App as its sole `always`-bypass actor.
  Everything else about mobile candidate publication depends on this
  ruleset staying exactly this shape — see the Safety invariants section.
- The `BUZZ_RELEASE_TAGGER_CLIENT_ID` variable and
  `BUZZ_RELEASE_TAGGER_PRIVATE_KEY` secret configured for GitHub Actions,
  used by `mobile-release-candidate.yml` to mint the App token that actually
  creates the tag.

## Procedure

### 1. Publish the candidate

From a clean, up-to-date checkout whose `origin` is canonical `block/buzz`:

```sh
scripts/mobile-release.sh candidate X.Y.Z
```

This does not use your local checkout as the source commit. It resolves the
*exact current remote* `origin/main` commit itself, computes the next
`rc.N` for that marketing version from exact remote tags, and dispatches
`mobile-release-candidate.yml` with that version, candidate number, and
target commit. The workflow mints a short-lived `buzz-release-bot` App
token and runs `scripts/publish-mobile-release-candidate.sh`, which
re-validates everything (ruleset state, target SHA, tag shape) itself
before creating a true annotated tag object and its ref, then reads both
back from the API to confirm they are exactly what was requested. The
operator script blocks on the workflow run and fails closed if it fails,
if the run URL is missing/ambiguous/from another repository, or if
`origin/main` moved between resolution and publication.

If your local checkout is behind `origin/main`, the script still targets
the current remote tip and prints a note to stderr naming both SHAs — this
is expected, not an error.

### 2. Build the exact tag

Enter the published `mobile-vX.Y.Z-rc.N` tag as `mobile_ref` in the private
Buzz mobile Buildkite pipeline
(`https://buildkite.com/runway/buzz-mobile-releases`). This step is manual
because OSS CI in this repository cannot trigger that private pipeline.
Flutter receives the clean marketing version `X.Y.Z`; the platform build
number comes from Buildkite's own monotonically increasing counter, not
from this repository.

### 3. Promote tested artifacts

Once a platform's build is tested, promote the already-built, already-signed
artifact through that platform's own store workflow. Record the exact
candidate tag alongside the rollout record. Nothing in this step changes the
source ref or produces a new build.

iOS and Android artifacts for the same marketing version may legitimately
come from *different* candidate tags (for example, iOS from `rc.2` while
Android ships `rc.3`) — there is intentionally no single "final" candidate
per marketing version, no stable `mobile-vX.Y.Z` alias, and no mobile GitHub
Release.

## Safety invariants

These are enforced independently by the operator script, the App-backed
publisher, and the required tag ruleset — not by convention:

- **No direct human tag creation.** The `mobile-v*` ruleset denies direct
  pushes of matching tags; only `buzz-release-bot`, verified by its
  effective `current_user_can_bypass == always`, can create one, and the
  publisher checks that value itself rather than trusting the ruleset's
  static configuration.
- **Existing candidates never move.** Both scripts derive the next `rc.N`
  from the exact remote tags that exist right now; a stale local clone
  cannot cause an existing tag to be recreated or reused, and a race where
  `main` moves mid-publication fails the run rather than silently tagging
  the wrong commit.
- **Tags are annotated, not lightweight.** The publisher creates a tag
  object first and a ref second, then confirms the ref is an annotated tag
  pointing at that exact object and that the object's target commit is the
  one requested.
- **Only `block/buzz` can publish.** Both the workflow's dispatch-ref check
  and the publisher's `GITHUB_REPOSITORY` check reject anything else.
- **Removed lanes stay removed.** There is no `start`/`finalize` command, no
  `mobile-release/` branch, and no stable `mobile-vX.Y.Z` alias — a
  dedicated contract test greps the scripts and workflow for exactly this
  and fails if any of it reappears.

## CI enforcement

`scripts/test-mobile-release-contract.sh` and
`scripts/test-mobile-release-candidate-publisher.sh` run as an
**unconditional** "Mobile release contract" step inside the `changes` job of
`.github/workflows/ci.yml` — on every push and every pull request, regardless
of which files changed. This is a different, stricter gate than the
`mobile`/`mobile-swift` Flutter jobs in the same workflow, which only run
when the separate `mobile` paths-filter (covering `mobile/**` and the
mobile-release scripts/workflow) reports a match.

## Troubleshooting

| Symptom | Response |
|---|---|
| New commits land after a candidate is published | Rerun `scripts/mobile-release.sh candidate <version>`. It publishes a new RC at the new remote tip; keep referring to any already-tested artifact by its own exact tag. |
| Publication fails because `main` moved mid-run | The App-backed workflow may already have published the requested RC at the prior tip. Do not move or delete it. Inspect the reported run URL, then rerun for the new tip. |
| The wrong RC number gets selected | Inspect the exact remote `mobile-v*` tags. Do not move or delete a tag — candidate numbers are monotonically increasing remote identities. |
| Publication is rejected by repository rules | Confirm `buzz-release-bot` is still the ruleset's sole always-bypass actor and that its Actions credentials are configured. Do not grant direct human creation or weaken the ruleset. |

## Scope and omissions

**No template existed for the `release` node type at the recorded
revision.** `launchpad/docs/corpus/templates/` has no `release.md`, and a
search for an open corpus-template PR or issue for the `release` type
(`gh issue list --repo launchpad-26/buzz --search "corpus template for
release"`) found none. Per `AGENTS.md`'s "Creating a node" and "Scope and
omissions" sections, this node was hand-authored directly against
`node.schema.json` rather than scaffolded from a template, and is expected
to be reshaped once a `release` template lands.

**No relationships were added.** This is the first `release`-typed node in
the corpus (confirmed by enumerating every node id currently on
`origin/launchpad`). The two existing mobile-related nodes —
`architecture-containers-mobile` (the Flutter app's own architecture) and
`layers-configuration-mobile-configuration` (its runtime environment
variables and Android signing config) — describe the mobile *app*, not its
release process, so no `references` edge to either would be honest. Sibling
task #1295 (`releases/mobile-release.md`, the full/finalized release
process) is still an open, undrafted issue with nothing merged at that path,
so there is nothing there to link to either.

**Out of reach from this repository:** everything past the published
candidate tag — the Buildkite build pipeline's own steps, code signing, and
each platform's store-promotion workflow — lives in the private
`squareup/buzz-releases` repository (per `CLAUDE.md`'s ecosystem table) and
could not be inspected from this checkout. What "Mobile Releases," named
alongside Artifactory and GitHub as a publishing destination in that table,
concretely is, is likewise not established here — see the `INFERENCE` entry
above naming this explicitly as a gap rather than guessing at it.

**Not covered by this node:** the desktop and relay release lanes (each has
its own process, only summarized here for contrast), and the full mobile
release process once one exists at `releases/mobile-release.md`.

**What this node does not decide:** whether the "Mobile Releases"
destination named in `CLAUDE.md` should itself become a corpus node, and how
this node should relate to `releases/mobile-release.md` once that task
lands — both are for that later task, not this one.
