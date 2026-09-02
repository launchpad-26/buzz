# Issue #1299 — releases/release-tags.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md` and `templates/reference.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/releases/` does not exist yet (siblings #1292/#1293/#1294 are still open, not merged).

STEP 1  Gather evidence: read `RELEASING.md`, `.github/workflows/auto-tag-on-release-pr-merge.yml`, `release.yml`, `docker.yml`, `helm-chart.yml`, `push-gateway-helm-chart.yml`, `sprig.yml`, `sprig-image.yml`, `scripts/mobile-release.sh`, `scripts/release-rulesets.sh` and `crates/sprig/Cargo.toml` for every tag naming scheme this repo's automation creates or reacts to. Independently query the live upstream Release tag ruleset (`gh api repos/block/buzz/rulesets` and `.../rulesets/14378754`) and `gh api repos/block/buzz/tags` to check `RELEASING.md`'s ruleset-scope claim and find historical schemes, rather than trusting the doc's prose. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `releases-release-tags`, type `release`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, `relationships: references` toward the three merged container nodes — `architecture-containers-desktop`, `architecture-containers-mobile`, `architecture-containers-relay` — and `layers-compute-sprig-runtime`, all four confirmed present on `origin/launchpad` and already stating a tag-format fact for their own lane) and the body using the **reference** template's required sections (reference description, structured entries table, boundary, relationships, scope and omissions), not the copied-over procedure-shaped DoD tail #1299 shares verbatim with #1292–#1294 — explain that departure in a "Note on Definition of Done" section, the same move `corpus-template-reference` itself makes.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call. Stop at the commit — no push, no PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review — not run here.

BUDGET: small-to-medium — one document, no code changes, but evidence spans ~10 workflow/script files plus two live GitHub API lookups (ruleset + tag list) to check a documentation-vs-platform drift claim.

OPEN: `RELEASING.md`'s Prerequisites section states the Release tag ruleset (14378754) is "active for `desktop-v*` and `mobile-v*`". The ruleset's own measured `conditions.ref_name.include` is `~ALL, refs/tags/v*, refs/tags/relay-v*, refs/tags/mobile-v*, refs/tags/chart-v*, refs/tags/push-chart-v*, refs/tags/sprig-v*` — no `desktop-v*` entry; desktop-v* is covered only by the blanket `~ALL`. This is recorded as fact in the node's body (with both sources cited) rather than silently resolved — a documentation-accuracy gap in `RELEASING.md`, not something this task owns fixing. Similarly, no producer script/workflow step was found for `sprig-v*` tags — recorded as unverified rather than invented.

LEFT OUT: No relationships toward `releases/desktop-candidate.md`, `desktop-release.md` or `mobile-candidate.md` (#1292–#1294) — none exist on `origin/launchpad` yet. No restatement of any lane's step-by-step release procedure (owned by `RELEASING.md` and those three tasks once merged). No attempt to fix `RELEASING.md`'s ruleset-scope claim or file an issue about it — out of scope for this node.
