# Plan: issue #1296 — document releases/relay-release.md

## Issue

launchpad-26/buzz#1296, parent Feature #619. DoD: create
`launchpad/docs/corpus/releases/relay-release.md` as the single canonical
procedure node for the relay release flow, schema-valid, evidence-honest,
validated.

## Evidence gathered before drafting

- `RELEASING.md` (repo root) — the Relay lane's documented flow: `just
  release-relay` on `main` → `relay-release/<version>` PR → merge → tag →
  `docker.yml`.
- `Justfile` — `release-relay`, `bump-relay-version`,
  `get-next-relay-patch-version`, and the shared `_release-pr` engine (branch
  naming, changelog generation, PR body, push).
- `.github/workflows/auto-tag-on-release-pr-merge.yml` — resolves
  `relay-release/<v>` branch → pushes immutable `relay-v<v>` tag; trigger is
  `pull_request: types: [closed], branches: [main]`.
- `.github/workflows/docker.yml` (as checked out on `origin/launchpad`) —
  builds and publishes the relay image; `IMAGE_NAME=ghcr.io/launchpad-26/buzz`
  hardcoded, triggers on push to `launchpad` + `relay-v[0-9]*` tags +
  `pull_request` (build-only) + `workflow_dispatch` (rescue).
- `.github/workflows/docker.yml` on `origin/main` (compared for divergence) —
  same file, but `IMAGE_NAME` defaults to `ghcr.io/block/buzz` via a
  `vars.GHCR_IMAGE` override, and the branch trigger is `branches: [main]`
  instead of `[launchpad]`. Two diverged copies of the same workflow exist in
  this repository across its two long-lived branches.
- `scripts/verify-release-ref.sh` — the tag-bound-source guard both
  `release.yml` (desktop) and `docker.yml` (relay) call.
- `crates/buzz-relay/Cargo.toml`, `crates/buzz-relay/CHANGELOG.md` — the
  version source and changelog `just release-relay` writes to.
- `launchpad/docs/corpus/development/build.md` (merged) — explicitly
  disclaims release-artifact building as `release.yml`/`docker.yml`'s
  territory; this node fills that named gap without duplicating build.md's
  compile steps.
- `launchpad/docs/corpus/templates/procedure.md` (merged) — the how-to
  template this node is built against.
- Top-level `AGENTS.md` ecosystem table — names `squareup/sprout-oss` (relay
  Docker image → internal ECR) and `squareup/block-coder-tf-stacks`
  (Terraform/ArgoCD → staging cluster) as the external, private continuation
  this session cannot inspect.
- `gh issue view 1296/1293/1299/1301` — DoD text, and confirmation that
  #1299 (release-tags.md) and #1301 (versioning.md) are open/unmerged, so no
  relationship may target them.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` —
  confirms no `releases/` directory exists yet on the merge target.

## Steps

1. **Scaffold front matter by hand** (no `scaffold.py` needed — schema is
   simple and `releases/` is a new directory): `id:
   releases-relay-release`, `type: release`, `status: draft`, `origin:
   launchpad`, `audiences: [agent, developer, operator]`, one provenance
   FACT citing `git rev-parse HEAD`.
2. **Write the body against `templates/procedure.md`**: Overview, Before you
   start, the three-stage numbered flow (bump/PR → merge/tag → image
   build+publish), See also, Boundary, Relationships, Scope and omissions —
   each step's evidence entry citing the file actually read.
3. **State the branch-divergence finding explicitly** in the body (not just
   the ledger): `docker.yml` differs between `origin/launchpad` and
   `origin/main`, and `just release-relay`'s own preflight requires being on
   `main`, not `launchpad` — name this as unresolved/unverified rather than
   asserting which copy an actual cohort relay release would exercise.
4. **Validate**: `python3 launchpad/project-intelligence/corpus/validate.py`
   must exit 0.
5. **Commit gate**: run the corpus unittest suite bare and unpiped as its own
   command, confirm OK, then stage the node + this plan and commit with
   `git commit -s`.

## Out of scope

- `releases/release-tags.md` (#1299) and `releases/versioning.md` (#1301) —
  open, unmerged; no relationship may target them.
- Desktop and mobile release lanes (`releases/desktop-release.md` is #1293,
  a separate task).
- Compiling the relay from source (`development/build.md`, merged).
- The private `sprout-oss` / `block-coder-tf-stacks` pipelines — named as
  external and uninspectable, not documented step-by-step.
- Resolving which of the two diverged `docker.yml` copies actually executes
  for a real cohort-initiated relay release — named as an open gap.
