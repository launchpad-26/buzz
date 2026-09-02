# Plan: issue #1294 — document releases/mobile-candidate.md

## Issue

launchpad-26/buzz#1294, parent PRD #619. Objective: create
`launchpad/docs/corpus/releases/mobile-candidate.md` as the single canonical
procedure node for the mobile release-candidate process.

## Confirmed target

- Path: `launchpad/docs/corpus/releases/mobile-candidate.md` (issue body's
  `corpus-plan:v2 alias:DOC:releases/mobile-candidate.md` header; confirmed no
  `releases/` directory exists yet under `launchpad/docs/corpus/`).
- `id`: `releases-mobile-candidate` (directory-stem convention, no `corpus-`
  prefix per the #2029 correction).
- `type: release` — present in `node.schema.json`'s enum.
- No merged or open-PR template exists for the `release` type (checked
  `launchpad/docs/corpus/templates/` and `gh issue list --search "corpus
  template for release"` — no hit). Per `AGENTS.md`'s "Creating a node" +
  "Scope and omissions", write directly against `node.schema.json`, no
  scaffold call, and say so in the node's own scope section.
- No `release`-typed node exists in the corpus yet, so no sibling to link and
  no relationship to add for that reason.
- Sibling task #1295 (`releases/mobile-release.md`, the full/finalized
  release) is still OPEN — nothing merged there either, confirmed via
  `gh issue view 1295`.

## Steps

1. **Gather evidence** (done during planning): read
   `scripts/mobile-release.sh`, `scripts/publish-mobile-release-candidate.sh`,
   `scripts/release-rulesets.sh`, `scripts/test-mobile-release-contract.sh`,
   `scripts/test-mobile-release-candidate-publisher.sh`,
   `.github/workflows/mobile-release-candidate.yml`, `.github/workflows/ci.yml`
   (paths-filter + job gating), and `RELEASING.md`'s Mobile sections.
2. **Hand-author front matter** against `node.schema.json`: `id`, `type:
   release`, `status: draft`, `origin: launchpad`, `audiences`, one FACT
   evidence entry recording the revision (`git rev-parse HEAD`).
3. **Write the body**: goal, prerequisites/scope, the publish → build →
   promote procedure with exact commands, the safety invariants the scripts
   enforce (evidenced by the two test scripts), what CI actually gates
   (`changes` job runs the two mobile-release test scripts unconditionally;
   the `mobile` Flutter job is separately gated on the `mobile` paths-filter
   output), and a scope section naming what's out of reach from this repo
   (signing/Buildkite promotion in `squareup/buzz-releases`) and no-template
   disclosure.
4. **Validate**: `python3 launchpad/project-intelligence/corpus/validate.py`
   must exit 0.
5. **Commit gate**: run the corpus unittest suite bare/unpiped as its own
   command, confirm OK, then stage the node + this plan and `git commit -s`.
   Stop at the commit — no push, no PR.
