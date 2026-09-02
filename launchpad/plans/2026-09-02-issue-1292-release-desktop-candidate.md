# Issue #1292 — releases/desktop-candidate.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; the `launchpad/docs/corpus/releases/` directory does not exist yet on `origin/launchpad` (confirmed: `git show origin/launchpad:launchpad/docs/corpus/releases` fails). Sibling task #1293 (`releases/desktop-release.md`, full release from tag onward) is open and unmerged — not a valid relationship target.

STEP 1  Gather evidence: read `RELEASING.md`'s Desktop section end to end, `Justfile`'s `release-desktop`/`get-next-patch-version`/`bump-desktop-version` recipes, `scripts/prepare-desktop-release.sh`, `scripts/desktop_release.py` (`generate`/`validate`), `.github/workflows/desktop-release-candidate.yml`, `.github/workflows/auto-tag-on-release-pr-merge.yml`, `scripts/verify-desktop-release-merge.sh`, and repo-root `AGENTS.md`'s ecosystem table (Block-signed `-block`-suffixed builds owned by `squareup/buzz-releases`, external, uninspectable here). Scope is candidate-cutting only: `just release-desktop <version>` through the `desktop-v<version>` tag being created — everything after the tag exists (`release.yml` builds/publishes) is issue #1293's node, not this one. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `releases-desktop-candidate`, type `release`, status `draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, no `relationships` — no merged node on `origin/launchpad` is a legitimate target, same reasoning precedent as issue #698's node) and the body against the `procedure` template (`launchpad/docs/corpus/templates/procedure.md`, closest merged fit — this is a goal-oriented how-to for a task the operator chooses to run, not a runbook triggered by an incident): Overview, Before you start (prerequisites from RELEASING.md), the numbered candidate-cutting sequence (generate → review → squash-merge → auto-tag verification → tag creation), the version-only-diff and single-parent-commit invariants `desktop_release.py validate` enforces, the required-checks list `verify-desktop-release-merge.sh` checks, the Internal Releases handoff to the private `buzz-releases`/Buildkite pipeline (named as external/uninspectable, not guessed at), See also, Boundary (explicitly against #1293's full-release scope), Relationships, Scope and omissions.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) bare and unpiped as the sole prior command to earn the verification stamp, then in a separate call `git add` the document and this plan and `git commit -s`.

STEP 5  [needs 4] Verify the finished document against issue #1292's DoD checklist line by line, re-opening every citation. Stop at the commit — no push, no PR, no other branch.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must pass as a bare, unpiped command before committing. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner — not run here.

BUDGET: small-to-medium — one document, no code changes, evidence gathering scoped to ~7 files already read (RELEASING.md, Justfile excerpt, 3 scripts, 2 workflow files) plus repo-root AGENTS.md's ecosystem table.

OPEN: Whether `releases-desktop-candidate` should eventually declare `references` toward `architecture-containers-desktop` (the Tauri container node) is left unresolved — the two documents describe different subjects (what the desktop app is vs. how its release candidate is cut) closely enough that a future reviewer may want the edge, but adding it here would be inventing a connection neither node's own text currently draws.

LEFT OUT: No relationships in front matter (`releases/` is empty on `origin/launchpad`, and #1293's sibling node is unmerged). No description of `release.yml`'s build/publish behavior, the Signed macOS Canary workflow, or the Promote-to-auto-update flow — those are the tag-triggered full-release surface #1293 owns. No attempt to inspect or describe `squareup/buzz-releases`' actual Buildkite pipeline contents — named as external and out of reach, per this repo's own ecosystem table, rather than guessed at.
