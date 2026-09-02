# Plan: issue #1293 — corpus node `release-desktop-release`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, and the merged `corpus-template-procedure` template
node are present on `origin/launchpad`; no `releases/` subtree exists yet under
`launchpad/docs/corpus/` and `launchpad/docs/corpus/releases/desktop-release.md` does
not exist. Sibling tasks #1292 (`releases/desktop-candidate.md`), #1301
(`releases/versioning.md`), and #1299 (`releases/release-tags.md`) are all open and
undrafted — confirmed via `gh issue list`, not assumed.

STEP 1 — Gather evidence. Read `RELEASING.md` in full (primary source), the ecosystem
table in root `AGENTS.md`, `.github/workflows/release.yml`,
`.github/workflows/auto-tag-on-release-pr-merge.yml`,
`.github/workflows/promote-oss-desktop-release.yml`, `scripts/verify-release-ref.sh`,
`scripts/verify-desktop-release-merge.sh`, `scripts/promote-oss-desktop-release.sh`,
`desktop/package.json`, `CHANGELOG.md`, and the live `Release` tag ruleset
(`gh api repos/block/buzz/rulesets/14378754`) for the desktop release process from
squash-merge through tag, build, publish, and promote-to-auto-update. RUNS HERE.

STEP 2 — Write front matter (id `release-desktop-release`, type `release`, status
`draft`, origin `launchpad`, audiences `developer`/`operator`, one `relationships`
entry `{type: implements, target: corpus-template-procedure}` since that template node
is merged and this node is built against its required sections) and the body: overview,
prerequisites, the numbered merge→tag→build→publish sequence, the separate
promote-to-auto-update step, the release-retry branch, an explicit boundary against
sibling #1292/#1301/#1299 (undrafted, so named as a gap rather than linked), and scope
and omissions naming what could not be verified (the private `squareup/buzz-releases`
pipeline this session cannot inspect). RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0. RUNS HERE.

STEP 4 — Run the commit gate
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`) as a lone, unpiped command, confirm it passes, then commit the node and
this plan together with `git commit -s`. Stop at the commit — no push, no PR. RUNS
HERE.

PARALLEL: none — single file, single worktree, no fan-out.

GATES: `validate.py` exit 0 before commit. The unittest discover command run alone,
unpiped, as the commit-gate stamp. No adjudication or cross-model review pass in this
session — deferred to the batch owner.

BUDGET: one file (plus this plan), one commit, no push, no PR. No code changes.

OPEN: whether the `Release` tag ruleset's live conditions (`~ALL` plus a stale,
non-exhaustive list of named patterns that does not itself include `desktop-v*`) match
what `RELEASING.md`'s Prerequisites section describes is worth a documentation-drift
finding, not something this plan resolves — the node records the live API result as
`FACT` and separately quotes the doc's own text rather than reconciling them.

LEFT OUT: no `relationships` toward #1292/#1301/#1299-shaped nodes (none exist yet on
`origin/launchpad`); the private `squareup/buzz-releases` Buildkite pipeline's actual
signing/publishing steps (named as an explicit gap, not guessed); any change to
`RELEASING.md`, workflow YAML, or release scripts — this task documents the existing
process, it does not modify it.
