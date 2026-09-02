---
id: releases-rollback
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
  - statement: "The launchpad-26 fork operates Buzz rather than developing it: the relay, desktop app and mobile app are upstream's product, and the cohort's own work is deploying, running and documenting that product."
    entry_class: FACT
    evidence:
      - "launchpad/README.md:16"
  - statement: "ADR-0005 records that Launchpad deploys through a wrapper under launchpad/deploy/ that delegates unchanged to upstream's deploy/compose/run.sh, and that only five files are sanctioned to diverge from upstream to make that wrapper reach a Launchpad-built image: deploy/compose/compose.yml, .github/workflows/docker.yml, deploy/compose/.env.example, Dockerfile, and deploy/compose/README.md."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md:18"
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md:26-30"
  - statement: "deploy/compose/README.md documents the relay rollback procedure directly: replace only BUZZ_IMAGE in the local .env with the new verified digest or full commit-SHA tag, run ./launchpad/deploy/run.sh check, back up state, and run ./launchpad/deploy/run.sh upgrade to move forward; to roll back, restore the previous immutable BUZZ_IMAGE value and run the same check and upgrade commands."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md:91-98"
  - statement: "The same README states an image-only rollback is safe only when intervening database migrations are backward-compatible, and otherwise requires restoring the matching pre-upgrade database and object/git snapshots as a coordinated recovery, not just swapping the image back."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md:96-98"
  - statement: "launchpad/deploy/run.sh refuses to start or upgrade unless BUZZ_IMAGE resolves to ghcr.io/launchpad-26/buzz, and treats only an image digest (@sha256:<64 hex>) or a full 40-character commit-SHA tag (:sha-<40 hex>, optionally debug-prefixed) as immutable; any other value is rejected unless the operator explicitly sets BUZZ_ALLOW_FLOATING_IMAGE=true."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/run.sh:94-118"
  - statement: ".github/workflows/docker.yml publishes a full 40-character commit-SHA tag (type=sha,prefix=sha-,format=long) on every build with no enable= gate -- deliberately, so that a workflow_dispatch rescue still produces a commit-pinned tag that launchpad/deploy/run.sh's guard will accept -- and this tag is produced on every ordinary push to the launchpad branch, not only on a relay-v release tag."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:19-20"
      - ".github/workflows/docker.yml:228-249"
  - statement: "Because every push to launchpad publishes an immutable ghcr.io/launchpad-26/buzz:sha-<full-commit> tag that satisfies launchpad/deploy/run.sh's own immutability check, an operator can roll the deployed relay back to any prior commit's published image without needing a relay-v semver release to exist for that commit."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/docker.yml:19-20"
      - ".github/workflows/docker.yml:228-249"
      - "launchpad/deploy/run.sh:94-118"
      - "deploy/compose/README.md:91-98"
    confidence: 0.85
  - statement: "deploy/compose/run.sh's upgrade command runs docker compose pull then up -d --wait; restart force-recreates only the relay and does not pull; start does not explicitly pull and may reuse an already-present tag -- so upgrade, not restart, is the command that actually picks up a changed BUZZ_IMAGE."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:69-74"
      - "deploy/compose/run.sh:92-116"
  - statement: "deploy/compose/.env.example ships BUZZ_AUTO_MIGRATE=true, but compose.yml itself defaults the same variable to false, and a hardening audit finding states that with it true, ./run.sh upgrade (compose pull then up) can apply schema migrations to the production database as a side effect of pulling a newer image, with no backup gate, no dry run, and no rollback, and that restart: unless-stopped means an unattended container restart can trigger the same migration."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/runbooks/hardening-spec.md:315-325"
  - statement: "The workflow_dispatch trigger on docker.yml is documented as a manual relay-tag rescue: an operator reruns image publication at an already-immutable relay-v tag or commit, rejecting any dispatch whose ref, checked-out HEAD and tag do not resolve to one commit -- it republishes a build, it does not revert a running deployment to an older state."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:26-36"
      - ".github/workflows/docker.yml:66-70"
      - ".github/workflows/docker.yml:196-202"
  - statement: "RELEASING.md's own Release Retry section states that release.yml (desktop) has no manual dispatch and cannot build from main or another caller-selected ref; if a run for an existing immutable desktop-v<version> tag fails, the fix is to rerun that failed workflow (gh run rerun --failed), which repairs the versioned draft without promoting it to the auto-updater and without moving or recreating the tag."
    entry_class: FACT
    evidence:
      - "RELEASING.md:171-184"
  - statement: "Every job in .github/workflows/release.yml (the desktop release pipeline) is gated if: github.repository == 'block/buzz', and .github/workflows/promote-oss-desktop-release.yml carries the same gate on its only job -- so this fork does not, and cannot, run desktop release publication or auto-update promotion at all; both are entirely upstream-operated."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:17"
      - ".github/workflows/release.yml:54"
      - ".github/workflows/release.yml:267"
      - ".github/workflows/release.yml:428"
      - ".github/workflows/promote-oss-desktop-release.yml:21"
  - statement: "scripts/promote-oss-desktop-release.sh independently hardcodes the same restriction (REPOSITORY must equal block/buzz, or the script fails) and separately refuses to promote a lower version than the one already promoted, failing with 'refusing downgrade from $current_version to $VERSION'."
    entry_class: FACT
    evidence:
      - "scripts/promote-oss-desktop-release.sh:12"
      - "scripts/promote-oss-desktop-release.sh:59"
  - statement: "RELEASING.md states that a same-version retry succeeds only with an identical manifest, that downgrades are rejected, that withholding promotion leaves existing clients on the previous version, and that recovery from a bad promoted release is to ship and promote a higher patch version -- changing the manifest to an older version does not downgrade clients that already updated."
    entry_class: FACT
    evidence:
      - "RELEASING.md:209-221"
  - statement: ".github/workflows/mobile-release-candidate.yml requires the dispatching repository to equal block/buzz before it will create a candidate tag, failing with 'Mobile candidate publication is restricted to block/buzz' otherwise -- so this fork cannot publish a mobile release candidate through this repository's own automation, upstream-operated or not."
    entry_class: FACT
    evidence:
      - ".github/workflows/mobile-release-candidate.yml:46-51"
  - statement: "No workflow, script, or documentation file in this repository describes a rollback, halt, or revert mechanism for a mobile release already promoted through its platform store (App Store Connect / Play Console); RELEASING.md's own Mobile section stops at 'promote the already-built signed artifact for each platform through its store workflow', with no failure-recovery step after that."
    entry_class: FACT
    evidence:
      - "RELEASING.md:92-128"
  - statement: "Whether launchpad-26/buzz's own relay-release/<version> PR-driven flow (auto-tag-on-release-pr-merge.yml, triggered on pull_request.closed against branches: [main]) actually fires for this cohort's own PRs, which merge into launchpad rather than main, was not established here -- this node's relay rollback procedure is grounded instead in the commit-SHA tag every ordinary push to launchpad already produces, which does not depend on that question's answer."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gap identified while authoring this node against launchpad-26/buzz#1300; not resolved, recorded as an open question in Scope and omissions below"
relationships:
  - type: references
    target: architecture-deployment-docker-compose
  - type: implements
    target: corpus-template-procedure
---

# Roll back or recover from a bad Buzz release

What to do when a published Buzz release turns out to be bad, per surface, for an
operator of the launchpad-26 fork -- covering what this fork actually runs (the
relay) and what it does not (desktop and mobile release/promotion, which stay
upstream's problem even though this repository's workflow files mention them).

## Before you start

- Know which surface is affected -- relay, desktop, or mobile -- since the three
  have unrelated release pipelines and this fork operates only one of them.
- For a relay rollback, you need shell access to the deployment host and to
  `deploy/compose/.env` there; know whether the bad release included a database
  migration (see Step 2 below).
- Read `deploy/compose/README.md`'s "Image lifecycle and traceability" section
  once, in full, before your first real rollback -- this procedure assumes that
  background rather than re-deriving it.

## Roll back the relay (fork-operated)

1. Identify the previous known-good relay reference. Run, on the deployment host:

   ```bash
   cd deploy/compose
   docker compose config --images
   container_id=$(docker compose ps -q relay)
   docker inspect --format 'configured={{.Config.Image}} image_id={{.Image}}' "$container_id"
   ```

   The workflow run that built the currently-running image records its full
   `sha-<40-character-commit>` tag and digest in its run summary; use that record,
   or an earlier one, to name the target reference.
2. Decide whether this is an **image-only** rollback or needs a **coordinated
   data restore**:
   - **2a. Image-only** -- safe only if no database migration ran between the
     target commit and the bad release. `BUZZ_AUTO_MIGRATE` applies schema
     changes automatically on container start with no backup gate, dry run, or
     rollback of its own, so confirm no migration landed in that window before
     treating this as safe.
   - **2b. Migration involved** -- an image swap alone does not undo a schema
     change. Restore the matching pre-upgrade Postgres and object/git snapshots
     first (see `deploy/compose/run.sh backup-hint` for what to have captured),
     then proceed with the image change below against the restored state.
3. Edit `deploy/compose/.env` and replace the `BUZZ_IMAGE` value with the prior
   immutable reference -- either the image digest (`@sha256:<64 hex>`) or the
   full 40-character commit-SHA tag (`:sha-<40 hex>`, or `:debug-sha-<40 hex>`).
   `launchpad/deploy/run.sh` rejects anything else (a floating tag such as
   `:launchpad`) unless `BUZZ_ALLOW_FLOATING_IMAGE=true` is set, which is not
   appropriate for a rollback.
4. Validate, then apply:

   ```bash
   ./launchpad/deploy/run.sh check
   ./launchpad/deploy/run.sh upgrade
   ```

   `upgrade` is the command that actually pulls the newly-configured image and
   restarts; `restart` alone does not pull, so it will not pick up the edited
   `BUZZ_IMAGE`.
5. Verify the rollback took effect by repeating Step 1's `docker inspect` /
   `docker image inspect` commands and confirming the running image's digest
   now matches the target reference, then check relay liveness:

   ```bash
   curl -fsS "http://127.0.0.1:$(grep -E '^BUZZ_HTTP_PORT=' deploy/compose/.env | cut -d= -f2-)/_liveness"
   ```

A `workflow_dispatch` run of `.github/workflows/docker.yml` is a **different**
tool for a different problem: it reruns image *publication* at an already-known
tag or commit when the automatic build failed, so a rollback candidate image
actually exists to point at. It does not touch a running deployment and is not
itself a rollback step.

## Desktop and mobile (upstream-operated, not this fork's to run)

This fork does not publish, promote, or roll back desktop or mobile releases:
every job in `release.yml` and `promote-oss-desktop-release.yml`, and the
canonical-repository check inside `mobile-release-candidate.yml`, refuse to run
outside `block/buzz`. What follows records upstream's own documented mechanisms
for awareness -- an operator here cannot execute them from this repository.

- **Desktop, failed publish.** If a run for an already-tagged, immutable
  `desktop-v<version>` fails, upstream reruns that failed workflow run rather
  than recreating or moving the tag. This repairs the versioned release draft;
  it does not promote anything.
- **Desktop, bad promoted auto-update.** The promotion tool refuses to move the
  rolling `buzz-desktop-latest` manifest to a lower version than is already
  promoted. There is no downgrade path for clients that already auto-updated;
  recovery is to ship and promote a newer patch version. Withholding promotion
  is the only lever over clients that have not yet updated.
- **Mobile.** Candidate publication is hardcoded to `block/buzz` and produces
  only immutable `mobile-vX.Y.Z-rc.N` tags; promotion beyond that point happens
  through each platform's own store workflow. No file in this repository
  describes a halt, revert, or rollback step for a build already promoted to a
  store -- that control, if it exists, lives entirely in App Store Connect or
  Play Console, outside this repository's visibility. This is a real gap, not
  an omission from this node.

## See also

- `deploy/compose/README.md` -- the full image-lifecycle reference this
  procedure's relay steps are built from.
- `RELEASING.md` -- the complete upstream release process for all three
  surfaces, including the parts this fork cannot run.
- `launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md` -- why the
  fork's deployment wrapper exists and exactly which five files it is allowed
  to diverge on.

## Boundary

This node does not describe:

- The fields, flags, or full command reference of `launchpad/deploy/run.sh` or
  `deploy/compose/run.sh` -- look those up in `deploy/compose/README.md` rather
  than here.
- How to acquire Docker Compose, VirtualBox, or general deployment skills from
  scratch -- see `launchpad/deploy/runbooks/dev-deployment-SOP.md` for that;
  this node assumes an existing, already-running deployment.
- Why the fork's deployment boundary is shaped the way it is (the wrapper
  design, the five-file exception list) -- see `ADR-0005` for that reasoning;
  this node only uses the resulting mechanism.
- A rollback mechanism for desktop or mobile that this fork could execute --
  none exists, because this fork does not operate either release pipeline.
  That is stated as fact above, not worked around here.

## Relationships

- `references`: `architecture-deployment-docker-compose` -- the reader is
  assumed to already understand what the Compose deployment bundle is and how
  it differs from the root development `docker-compose.yml`.
- `implements`: `corpus-template-procedure` -- this node is an instance of the
  how-to/procedure template.

## Scope and omissions

**This node covers** what to do, today, when a relay release deployed by this
fork turns out to be bad -- the documented image-only rollback and its
migration caveat -- and states plainly what is and is not possible for desktop
and mobile from within this repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A rollback mechanism for a bad desktop or mobile release | Not this fork -- entirely upstream (`block/buzz`), and no documented mechanism was found in this repository even for upstream's own use beyond "promote a newer version" |
| A rollback mechanism for a mobile build already promoted to an app store | Apple/Google's own store consoles -- outside this repository's visibility |
| Full command reference for `run.sh` / `deploy/compose/run.sh` | `deploy/compose/README.md` |
| The deployment-boundary design rationale | `launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md` |
| General Docker/Compose/VirtualBox skills | `launchpad/deploy/runbooks/dev-deployment-SOP.md` |

**Expected but not verified when this node was written:**

- Whether `auto-tag-on-release-pr-merge.yml`'s `relay-release/<version>` →
  `relay-v<version>` PR-merge flow actually fires for this cohort's own work,
  given that workflow triggers on PRs merged to `main` while this fork's
  working branch is `launchpad`. This node's relay procedure does not depend on
  the answer -- it is grounded in the commit-SHA tag every ordinary push to
  `launchpad` already publishes -- but the semver release flow's operability in
  this fork remains an open question.
- Whether `BUZZ_AUTO_MIGRATE` is actually set to `true` or `false` on the
  cohort's real deployment host today; this node states what the shipped
  example and the compose default disagree on and what happens if it is left
  `true`, not which value is currently live.
- Whether any deployment host currently exists to run this procedure against --
  this node was authored from the repository's tooling and documentation, not
  against a live rollback exercised on a running instance.
