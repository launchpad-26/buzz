# Plan — issue #867: `development/run-web.md`

Task: author exactly one corpus procedure node at
`launchpad/docs/corpus/development/run-web.md`, id `development-run-web`,
type `development`, status `draft`, origin `launchpad`.

Revision planned against: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`
(`origin/launchpad` at branch time).

## ALREADY TRUE

- The target does not exist. `ls launchpad/docs/corpus/development/` returns
  exactly `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md` — four
  files, no `run-web.md`, and no `run-desktop.md` / `run-mobile.md` /
  `run-relay.md` from siblings #864–#866 either.
- `web/` is a real pnpm workspace package (`pnpm-workspace.yaml` lists
  `desktop`, `web`, `admin-web`) with its own `package.json`, `vite.config.ts`,
  `playwright.config.ts` and `tests/e2e/smoke.spec.ts`.
- `Justfile` already carries a dedicated `web` run recipe plus `web-check`,
  `web-fix`, `web-typecheck`, `web-build`, `web-e2e-smoke`, and a separate
  `relay-web` recipe that builds the bundle and serves it from the relay.
- `development/build.md` (id `corpus-development-build`) is merged and owns
  `just web-build`. This node owns running, not building.
- `architecture/containers/web.md` (id `architecture-containers-web`) is merged
  and owns the container/architecture description of the web bundle.
- Corpus authoring rules, schema and validator are all in place and unchanged.

## STEP 1 — establish what "running the web client" actually is

Read, in the worktree, at the recorded revision:
`Justfile` (`web`, `relay-web`, `web-*`, `bootstrap`, `setup`),
`web/package.json`, `web/vite.config.ts`, `scripts/instance-env.sh`,
`scripts/dev-setup.sh`, `.env.example`, `web/src/shared/lib/relay-url.ts`,
`web/src/app/routes.ts`, `web/playwright.config.ts`,
`crates/buzz-relay/src/config.rs` (`BUZZ_WEB_DIR`) and
`crates/buzz-relay/src/router.rs` (`should_serve_spa`).

Done when: the two distinct run modes (Vite dev server vs relay-served bundle)
are each traced to their own recipe and their own route coverage, and the
difference between them is proven rather than assumed.

## STEP 2 — confirm boundaries and relationship targets

`ls launchpad/docs/corpus/development/` for sibling existence;
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` and
`git show origin/launchpad:<path>` for every id used in `relationships`.

Done when: every relationship target id has been read off `origin/launchpad`,
not off this branch.

## STEP 3 — write the node

Front matter to `node.schema.json`. Evidence ledger: first entry records the
revision as a commit citation; one entry per substantive claim; FACT only where
the source was opened; INFERENCE carries `confidence`; TEAM_KNOWLEDGE carries
`provided_by`.

Body, procedure shape: single level-1 heading; goal; prerequisites and allowed
environment/scope; ordered executable project-specific steps for both run
modes; success verification; rollback and cleanup; a table of authoritative
commands linked to the files that define them; explicit scope-and-omissions
carrying both the boundary and the "expected but could not verify" disclosure.

Done when: the file exists, is under 1000 lines, and every claim in the body
has a ledger entry.

## STEP 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py` reports PASS.
Then re-open every citation and re-check the DoD line by line — before
committing, because `git commit --amend` is blocked here.

Done when: validator exits 0 and the DoD walk is complete.

## STEP 5 — commit

Corpus unit tests bare and unpiped as their own command:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Then `git add` the node and this plan, and `git commit -s`. No push, no PR.

Done when: one signed commit exists on `task/867-development-run-web`.

## PARALLEL

Steps 1 and 2 are independent and were run interleaved. Steps 3–5 are strictly
sequential.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
- Repository pre-commit hooks run normally; never `--no-verify`.

## BUDGET

One hand-authored file plus this plan. No generated outputs, no product code,
no second corpus node.

## OPEN

- Whether `pnpm install` at the repository root fully populates `web/`'s
  dependencies is reasoned from `pnpm-workspace.yaml`, not executed here; it is
  recorded as INFERENCE with confidence, not as FACT.
- `just web` and `just relay-web` were not executed in this environment. All
  claims about them are read off the recipes and the code they invoke; the node
  says so in its omissions section rather than implying a live run.

## LEFT OUT

- Building the web bundle — `development/build.md` owns `just web-build`.
- Running desktop, mobile or the relay — siblings #864, #865, #866.
- The `admin-web` package beyond naming it as a separate bundle with its own
  `just admin` recipe, so a reader does not mistake it for part of this loop.
- The architecture of the web container — `architecture-containers-web` owns it.
- Deployment or production serving of the bundle.
