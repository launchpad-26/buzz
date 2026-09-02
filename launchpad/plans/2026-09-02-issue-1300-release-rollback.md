# Issue #1300 — releases/rollback.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, and `launchpad/docs/corpus/templates/procedure.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/releases/rollback.md` and the `releases/` directory do not exist yet — no sibling `releases/*` node (including issue #1291's `auto-update.md`) is merged, so none is a valid relationship target. `RELEASING.md` documents the desktop/relay/mobile release lanes but not what to do when one goes bad.

STEP 1  Gather evidence: read `RELEASING.md` fully. Open the actual workflow/script sources rather than trusting that prose — `.github/workflows/release.yml`, `promote-oss-desktop-release.yml`, `docker.yml`, `helm-chart.yml`, `mobile-release-candidate.yml`, `auto-tag-on-release-pr-merge.yml`, `scripts/promote-oss-desktop-release.sh`, `scripts/mobile-release.sh` — to find each surface's actual recovery/rescue/rollback mechanism (or its absence). Separately check the fork's own operated deployment path (`launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md`, `deploy/compose/README.md`, `launchpad/deploy/run.sh`, `deploy/compose/run.sh`, `launchpad/deploy/runbooks/hardening-spec.md` finding B6) — this fork operates the relay only; desktop and mobile release/promotion jobs are gated `if: github.repository == 'block/buzz'` and are not something this fork runs. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `releases-rollback`, type `release`, status `draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, `relationships: [{type: references, target: architecture-deployment-docker-compose}]` — confirmed merged on `origin/launchpad`) and the body, using the procedure template's required sections (Overview, one numbered task sequence per surface, See also, Boundary, Relationships, Scope and omissions). Content per surface:
  - **Relay (fork-operated):** the documented image-only rollback in `deploy/compose/README.md` — restore the previous immutable `BUZZ_IMAGE` value, `./launchpad/deploy/run.sh check`, back up state, `./launchpad/deploy/run.sh upgrade` — explicitly caveated as safe only when intervening DB migrations are backward-compatible (hardening-spec.md B6: `BUZZ_AUTO_MIGRATE` has no backup gate, dry run, or rollback), otherwise requiring a coordinated Postgres/object-storage snapshot restore.
  - **Desktop:** state plainly that the fork does not operate desktop release/promotion (both gated to `block/buzz`); note upstream's own two mechanisms found in STEP 1 (failed `desktop-v*` publish → rerun via `gh run rerun --failed`, no ref/tag change; a bad *promoted* auto-update version cannot be downgraded — `scripts/promote-oss-desktop-release.sh:59` hard-refuses a lower version — recovery is to ship and promote a newer patch) as upstream facts, not fork-operated procedure.
  - **Mobile:** same framing — candidate publication is hardcoded to `block/buzz` (`mobile-release-candidate.yml`); no rollback mechanism of any kind was found for mobile in this repository; store-side halt/rollback is outside this repo's visibility, stated as a gap rather than invented.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it reports PASS.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) bare and alone as the verification stamp, confirm OK, then commit the plan + document together with `git commit -s` in a separate call. Stop there — no push, no PR.

PARALLEL: none — single file, single task, no dependent work.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must pass as the sole prior command before commit. `review-adjudicate` and cross-model final review are deferred to the batch owner — not run here.

BUDGET: small-to-medium — one document, no code changes; evidence gathering spans roughly a dozen workflow/script/doc files across two release surfaces (CI-published and fork-operated).

OPEN: Whether the fork intends to ever operate its own desktop/mobile release+rollback story, or permanently defers both to upstream, is a product decision this node does not make — it records the current (no) state and cites the hardcoded `block/buzz` gates as the reason.

LEFT OUT: No relationship to issue #1291's `releases/auto-update.md` or any other `releases/*` sibling — none are merged on `origin/launchpad`. No attempt to design or propose a new rollback mechanism for any surface that lacks one; the absence is recorded, not fixed. No change to `RELEASING.md`, the workflows, or `deploy/compose/README.md` themselves.
