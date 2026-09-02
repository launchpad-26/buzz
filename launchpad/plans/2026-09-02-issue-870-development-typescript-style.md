# Issue #870 — development/typescript-style.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/templates/reference.md` are merged on `origin/launchpad`. `launchpad/docs/corpus/development/typescript-style.md` does not exist (`ls launchpad/docs/corpus/development/` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` returns exactly `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`). Sibling language-style tasks #854 (`dart-style.md`) and #868 (`rust-style.md`) are not present in that listing either, so this node covers TypeScript/React only and names the other two as boundaries.

STEP 1  Gather evidence from primary sources only — never from a doc's claim about a gate. Open `biome.json`, `desktop/biome.json`, `web/biome.json`, `desktop/tsconfig.json`, `web/tsconfig.json`, `admin-web/tsconfig.json`, the four `package.json` script blocks, `Justfile` (`check`, `ci`, `desktop-check`, `desktop-typecheck`, `web-check`, `web-typecheck`, `file-size-check`, `admin-check`), `lefthook.yml`, `.github/workflows/ci.yml`, `scripts/check-px-text-core.mjs`, `desktop/scripts/check-px-text.mjs`, `scripts/check-file-sizes-core.mjs`, `desktop|web/scripts/check-file-sizes.mjs`, `desktop/scripts/check-pubkey-truncation.mjs`, `desktop/tailwind.config.js`, `desktop/src/shared/styles/globals/typography.css`, `CONTRIBUTING.md` §Code Style. For every rule, establish the invoking command chain end-to-end before calling it machine-enforced. ← RUNS HERE

STEP 2  [needs 1] Classify each rule as SCRIPT-ENFORCED (a named command fails on violation), COMPILER-ENFORCED (`tsc` flag), or REVIEW-ONLY (prose in `AGENTS.md` with no gate), and record for each the exact invoking surface (`pnpm check` / `just check` / lefthook lane / CI job). Where `AGENTS.md` asserts an enforcement detail, diff that assertion against the script and record any falsification as a FACT.

STEP 3  [needs 2] Write front matter (id `development-typescript-style`, type `development`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, relationships only to ids confirmed with `git show origin/launchpad:<path>`) and the reference-shaped body per `templates/reference.md`: description, structured enforcement tables, commands table, boundary, relationships, scope-and-omissions.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it reports PASS.

STEP 5  [needs 4] Run the corpus unittest suite bare and unpiped as the sole command in its own call, then in a separate call `git add` the document plus this plan and `git commit -s`. Stop at the commit.

PARALLEL: none — one document, one file.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK, run bare as the sole command in its own tool call. No push, no PR — review is the batch owner's.

BUDGET: small — one reference node, no code changes, evidence scoped to ~18 configuration/script/workflow files already enumerated in STEP 1.

OPEN: `admin-web/` is a fourth TypeScript surface with its own `tsconfig.json` and `package.json` but no `biome.json`, no lefthook lane, no entry in `just check` or `just ci`, and no job in any file under `.github/workflows/`. That is recorded in the node as a fact about current coverage; deciding whether it *should* be gated is not this task's to settle. `AGENTS.md`'s claim that px-text overrides are "allowlisted by `path:line`" is contradicted by the script itself and is recorded as a falsified documentation claim rather than repeated.

LEFT OUT: Dart style (#854) and Rust style (#868) — separate nodes, named only as boundaries. No accessibility, testing, or Playwright-spec conventions. No edit to `AGENTS.md`, `CONTRIBUTING.md`, or any config to close a coverage gap found while drafting — this is a documentation task, and a gate change would need its own issue.
