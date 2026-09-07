# Plan: issue #1295 — document releases/mobile-release.md

## Issue

launchpad-26/buzz#1295, parent PRD #619. Objective: create
`launchpad/docs/corpus/releases/mobile-release.md` as the single canonical
procedure node for the mobile release process **past the candidate stage** —
building the exact `mobile-vX.Y.Z-rc.N` tag through the private Buildkite
pipeline and promoting the resulting signed artifacts through each
platform's store workflow.

## Confirmed target

- Path: `launchpad/docs/corpus/releases/mobile-release.md` (issue body's
  `corpus-plan:v2 alias:DOC:releases/mobile-release.md` header; confirmed no
  `releases/` directory exists yet under `launchpad/docs/corpus/` on
  `origin/launchpad`).
- `id`: `releases-mobile-release` (directory-stem convention, no `corpus-`
  prefix, per the #2029 correction — matches the unmerged sibling
  `releases-mobile-candidate`'s convention).
- `type: release` — present in `node.schema.json`'s enum (singular).
- Template: `launchpad/docs/corpus/templates/procedure.md` is merged on
  `origin/launchpad` and applies — it is a how-to-shaped node, and its own
  Boundary section uses "cut a relay release" as the worked example
  distinguishing a procedure (chosen-schedule task) from a runbook
  (triggered-by-failure response). Use `scaffold.scaffold_node` (merged
  branch) rather than the no-template hand-authoring path.
- Sibling #1294 (`releases/mobile-candidate.md`) exists only as an unpushed
  local commit on branch `task/1294-release-mobile-candidate` — no PR, issue
  #1294 still OPEN, and it is **absent from `origin/launchpad`**
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  lists no `releases/` directory at all). No relationship may target
  `releases-mobile-candidate`; the boundary against it is stated in prose
  only, and the gap (no relationship possible yet) is named in Scope and
  omissions.
- Sibling #1301 (`releases/versioning.md`) is also OPEN, unmerged, no PR —
  same treatment.
- `RELEASING.md`'s "Mobile" section splits three steps: (1) publish a
  candidate — `scripts/mobile-release.sh candidate X.Y.Z`, entirely
  #1294's territory, confirmed by reading that script and
  `.github/workflows/mobile-release-candidate.yml`, both of which contain no
  build/promote/store logic; (2) build the exact tag on the private Buzz
  mobile Buildkite pipeline (`mobile_ref` input) — this node's territory;
  (3) promote the already-built signed per-platform artifact through its
  store workflow — this node's territory.
- No workflow, script, or config in this OSS repo performs the build or
  promote step — confirmed by grepping `.github/workflows`, `scripts/`,
  `RELEASING.md`, and `mobile/` for App Store/Google Play/TestFlight/Play
  Console/Fastlane terms (only hit: `mobile/README.md`'s unrelated APNs
  push-profile section). The private `squareup/buzz-releases` pipeline is
  the only place this executes; state that as an explicit gap rather than
  invent its steps, per this run's standing lesson about unverifiable
  publishing pipelines.

## Steps

1. **Gather evidence** (done during planning): read `RELEASING.md`'s Mobile,
   Internal Releases, What Gets Published, Version Sources, and Release Retry
   sections; `scripts/mobile-release.sh`,
   `.github/workflows/mobile-release-candidate.yml` (to confirm they are
   candidate-only, not build/promote); `mobile/pubspec.yaml` and
   `mobile/CHANGELOG.md` (version-source claims); `CLAUDE.md`'s ecosystem
   table/diagram for the `squareup/buzz-releases` row; confirm via `gh issue
   view` that #1294 and #1301 are open and via `git ls-tree` that
   `releases/` does not exist on `origin/launchpad`.
2. **Scaffold** the node with `scaffold.scaffold_node` against
   `node.schema.json`, `id: releases-mobile-release`, `type: release`,
   `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
   operator]`, one FACT evidence entry recording the revision.
3. **Write the body** on `templates/procedure.md`'s required sections:
   Overview, Before you start, one numbered task sequence (build → promote),
   See also, Boundary (vs #1294 candidate-cutting, vs desktop/relay lanes,
   vs the private pipeline's internal steps), Relationships (none — sibling
   nodes unmerged), Scope and omissions (naming the private-pipeline gap and
   the App Store/Google Play step as unverifiable from this repo).
4. **Validate**: `python3 launchpad/project-intelligence/corpus/validate.py`
   must exit 0.
5. **Commit gate**: run the corpus unittest suite bare/unpiped as its own
   command, confirm OK, then stage the node + this plan and `git commit -s`.
   Stop at the commit — no push, no PR.
