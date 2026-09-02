# Plan — issue #869: document `development/setup.md`

Repository revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`origin/launchpad`).
Worktree: `__worktrees/task-869-development-setup`, branch `task/869-development-setup`.

Target: `launchpad/docs/corpus/development/setup.md` — confirmed absent
(`ls launchpad/docs/corpus/development/` lists exactly `build.md`, `debugging.md`,
`hermit.md`, `prerequisites.md`).

Shape: procedure node, modelled on `launchpad/docs/corpus/templates/procedure.md`
(Diátaxis How-to). ID `development-setup`, type `development`, status `draft`,
origin `launchpad`.

## ALREADY TRUE

- The worktree exists and is branched from `origin/launchpad` at the revision above.
- Four sibling `development/` nodes are merged on `origin/launchpad`, with ids
  `development-prerequisites`, `development-hermit`, `corpus-development-build`,
  `debugging` (confirmed with `git show origin/launchpad:<path> | grep '^id:'`).
- `corpus-template-procedure` and `corpus-template-reference` are merged, so both
  are legal relationship targets.
- `prerequisites.md` already names `development/setup.md` as a deliberate exclusion
  from its own scope, so the boundary is being drawn from that side already.
- Two defects in merged siblings are known going in (#2030): `hermit.md` claims the
  `Justfile` contains no Hermit reference and that `just bootstrap` pre-downloads
  every pinned tool. Neither is to be inherited.

## STEP 1 — read the real setup machinery, not the prose about it

Open and record: `Justfile` (`bootstrap`, `setup`, `hooks`, `_ensure-services`,
`_ensure-migrations`, `corpus-validate`), `scripts/dev-setup.sh`,
`scripts/ensure-local-relay-key.sh`, `scripts/seed-local-community.sh`,
`lefthook.yml`, `.env.example`, `bin/*.pkg`, plus the three prose sources that
describe the path (`CONTRIBUTING.md` § First-Time Setup, `AGENTS.md` § Getting
Started, `README.md` § Quick start).

Done when the true order of operations is written down from the recipe bodies, and
`just bootstrap`'s actual pre-download behaviour is established from `Justfile`
rather than from any document that describes it.

## STEP 2 — establish the boundaries against the three merged siblings

Read `prerequisites.md`, `hermit.md` and `build.md` bodies (Boundary, Scope,
Relationships). Setup is the connective procedure between them; state where each
line falls rather than restating their content.

Done when each sibling has one sentence saying what it owns that this node defers to,
and no sibling's content is duplicated.

## STEP 3 — write the node

Front matter against `schema/node.schema.json`; first FACT records the revision as a
commit citation; every other FACT cites a file opened in STEP 1; INFERENCE carries
`confidence`; anything resting only on a GitHub issue is `TEAM_KNOWLEDGE` with
`provided_by`, per `AGENTS.md`'s rule that an issue is not an openable file.

Body follows the procedure template: one level-1 `#` heading; goal; *Before you
start*; ordered project-specific steps; success verification; rollback/cleanup; *See
also*; *Boundary*; *Relationships*; *Scope and omissions* carrying both the
ownership boundary and the expected-but-not-verified disclosure.

Relationships declared only against the five ids confirmed present on
`origin/launchpad` in ALREADY TRUE.

Done when the file exists, is under 1000 lines, and reads as a procedure rather than
a description of one.

## STEP 4 — validate and re-verify

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root until it reports PASS. Then re-open every citation in the ledger and re-check
each statement against the file it names, before committing — `git commit --amend`
is blocked by the safety hook, so re-verification cannot happen afterwards.

Done when validate.py passes and every FACT has been re-read at this revision.

## STEP 5 — commit

Run the corpus unit tests bare and unpiped as their own command:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then `git add` the document and this plan, and `git commit -s`.
No `--no-verify`. Stop at the commit — no push, no PR.

## PARALLEL

STEP 1 and STEP 2 are independent reads and can be done in one pass. STEP 3 depends
on both. STEP 4 depends on STEP 3. STEP 5 depends on STEP 4.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
- Every declared `relationships[].target` resolves against `origin/launchpad`, not
  against this worktree.
- Exactly one hand-authored corpus file changed.

## BUDGET

One document, one plan, one commit. Five steps. No second corpus node; anything that
turns out to be a second idea is named as a finding and left for a separate task.

## OPEN

- Whether `just setup` completes end-to-end on a clean machine cannot be established
  here without running Docker and a full toolchain download, which would couple the
  evidence to one particular local environment. The node states the steps from the
  recipe bodies and discloses that the sequence was not executed.
- `scripts/dev-setup.sh` calls `lefthook` unqualified while calling `bin/just` and
  `bin/cargo` by absolute path. What that does on a shell without Hermit activated is
  reasoned about, not executed, so it is an INFERENCE with a confidence rating.

## LEFT OUT

- Running any component after setup (relay, desktop, web, mobile) — issues #865,
  #866, #867 and their siblings.
- Rust style and code conventions — #868.
- Compiling the workspace — `corpus-development-build`.
- Toolchain mechanism and version floors — `development-hermit`,
  `development-prerequisites`.
- Filing issues for anything found. Findings are reported, not filed.
