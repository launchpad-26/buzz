# Plan: issue #1298 — corpus node `releases-release-provenance`

ALREADY TRUE: `launchpad/docs/corpus/releases/` does not exist on `origin/launchpad`
(confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
No release-surface node is merged yet — #1292 (desktop-candidate), #1294
(mobile-candidate), #1297 (release-artifacts), #1299 (release-tags) are all still open,
so no `relationships` target exists. The issue's DoD tail (goal, prerequisites, ordered
steps, success verification, rollback/cleanup, authoritative commands) is the
`procedure` (Diátaxis how-to) shape, not `reference`; `node.schema.json`'s `type` enum
confirms `release` (singular) is a valid surface value.

STEP 1 — Gather evidence. Read `.github/workflows/release.yml`, `docker.yml`,
`auto-tag-on-release-pr-merge.yml`, `desktop-release-candidate.yml`,
`mobile-release-candidate.yml`, `promote-oss-desktop-release.yml`,
`scripts/verify-release-ref.sh`, `scripts/verify-desktop-release-merge.sh`,
`RELEASING.md`, and `mobile/android/app/build.gradle.kts` for every mechanism that ties
a released artifact back to a specific commit/CI run: relay's
`actions/attest-build-provenance` + custom deployment-eligibility attestation, desktop's
code signing/notarization + Tauri updater signature + tag-bound merge verification
chain, and mobile's tag-as-source-record + Android upload-keystore/external-signing
split. Note what is NOT present (no build-provenance attestation for desktop or mobile
artifacts) as findings, not gaps to fill. RUNS HERE.

STEP 2 — Write front matter (id `releases-release-provenance`, type `release`, status
`draft`, origin `launchpad`, no `relationships` — no sibling release-surface node is
merged yet) and the body using `templates/procedure.md`'s required sections: Overview,
Before you start, one numbered task sequence per artifact class (relay image / desktop
macOS / desktop Windows+Linux / mobile) — forked per Diátaxis's explicit allowance
since each class's verification mechanism genuinely differs — See also, Boundary
(not #1299 release-tags.md, not #1297 release-artifacts.md), Relationships, Scope and
omissions. RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0. RUNS HERE.

STEP 4 — Run the commit-gate test suite alone
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`), confirm OK, then commit plan + node together. RUNS HERE.

PARALLEL: none — single file, single worktree, no fan-out.

GATES: `validate.py` must exit 0 before commit. The unittest suite is run once, alone,
in its own tool call to earn the commit verification stamp. No push, no PR — this
session stops at the commit per the dispatching brief.

BUDGET: one file, one commit, no PR. No code changes, no generated-index
regeneration expected (none exist yet to regenerate).

OPEN: whether the private `buzz-releases`/Buildkite pipeline (mobile signing, Block
`-block` desktop re-signing) adds any provenance mechanism beyond what's visible in
this OSS repo is out of reach from here — recorded as an unverified gap, not assumed
either way.

LEFT OUT: no `relationships` entries (no release-surface sibling node merged yet);
per-artifact download/build instructions belonging to #1297's scope; the tag-format
contract belonging to #1299's scope; any change to workflow YAML or scripts — this
task documents existing provenance mechanisms, it does not add or change any.
