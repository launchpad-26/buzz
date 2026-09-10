# Plan — issue #864: document `development/run-desktop.md`

Target: `launchpad/docs/corpus/development/run-desktop.md`
Shape: procedure node, modelled on `launchpad/docs/corpus/templates/procedure.md`
Branch: `task/864-development-run-desktop` off `origin/launchpad` @ `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`

## ALREADY TRUE

- The worktree exists at `__worktrees/task-864-development-run-desktop`, branched from
  `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`.
- `launchpad/docs/corpus/development/run-desktop.md` does **not** exist
  (`ls` returns "No such file or directory").
- `launchpad/docs/corpus/development/` holds exactly four nodes on `origin/launchpad`:
  `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`. No `run-*.md` sibling
  exists yet, so nothing can be claimed about #865/#866/#867's output.
- Every recipe this node documents has been read from `Justfile` directly:
  `dev` (530), `desktop-standalone` (592), `staging` (620), `production` (655),
  `desktop-dev` (690), `desktop-install` (125), `desktop-screenshot` (450),
  `setup` (49), `bootstrap` (26), `_ensure-services` (185), `_ensure-migrations` (211),
  `_ensure-sidecar-stubs` (168), `down` (74), `reset` (70), `clean` (792).
- `scripts/instance-env.sh`, `scripts/dev-setup.sh`, `desktop/src/main.tsx`,
  `desktop/package.json`, `desktop/playwright.config.ts`, `desktop/vite.config.ts`,
  `desktop/README.md` and `docker-compose.yml` have all been opened.
- Relationship targets confirmed to resolve on `origin/launchpad` by
  `git show origin/launchpad:<path>`: `corpus-development-build`,
  `development-prerequisites`, `development-hermit`, `debugging`,
  `architecture-containers-desktop`, `architecture-deployment-local-development`,
  `layers-configuration-desktop-configuration`, `corpus-template-procedure`.

## STEP 1 — Draft the front matter and provenance ledger

Write `id: development-run-desktop`, `type: development`, `status: draft`,
`origin: launchpad`, `audiences: [developer, agent]`. First ledger entry is the FACT
recording revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`. Every other entry cites a
file actually opened above. INFERENCE entries carry `confidence`; TEAM_KNOWLEDGE entries
carry `provided_by` and no `confidence`.

**Done when:** the ledger has one entry per substantive body claim and no entry cites a
file that was not opened in this session.

## STEP 2 — Draft the body against the procedure template

Sections, in the template's order: single `#` heading; overview line; *Before you start*;
the four run paths as separate labelled sequences (they fork — the template explicitly
permits per-branch numbering rather than one flattened list); *Verify it is running*;
*Stop and clean up*; *See also*; *Boundary*; *Relationships*; *Scope and omissions*.

**Done when:** every DoD bullet in #864 maps to a named section, exactly one level-1
heading exists, and the file is under 1000 lines.

## STEP 3 — Declare relationships

Declare only ids confirmed in ALREADY TRUE. Planned:
`implements: corpus-template-procedure`, `references: corpus-development-build`,
`references: development-prerequisites`, `references: architecture-containers-desktop`,
`references: layers-configuration-desktop-configuration`,
`references: architecture-deployment-local-development`.

**Done when:** each declared target was resolved with
`git show origin/launchpad:launchpad/docs/corpus/<path>` in this session, not from the
worktree alone.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` and read its output.

**Done when:** it reports PASS. `UNVERIFIED` notices on the commit citation are expected
and non-fatal.

## STEP 5 — Re-verify, then commit once

Re-read #864's DoD line by line against the draft and re-open every citation **before**
committing — `git commit --amend` is blocked by `git-safety.sh`, so there is one shot.
Run the corpus unit suite bare and unpiped, then `git add` document + plan and
`git commit -s`.

**Done when:** `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` reports OK and the commit exists.

## PARALLEL

None. Steps 1–5 are strictly sequential: the ledger constrains the body, the body
constrains the relationships, and validation gates the commit.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  → OK, run bare and unpiped as the sole command in its tool call.
- Pre-commit/pre-push hooks run unmodified. Never `--no-verify`.

## BUDGET

One document plus this plan. Two files changed, one commit, no push, no PR.

## OPEN

- The `id` prefix conflict: `standards/naming.md` MUST 3 prescribes a `corpus-` prefix,
  but 157 of 160 merged content nodes use `<directory>-<stem>`. Tracked in #2029.
  This node follows measured practice (`development-run-desktop`) per the dispatch brief
  and does **not** file a new issue.
- No desktop run path was executed in this environment (no Docker daemon, no Tauri
  toolchain, no display). Every step is FACT-cited to the recipe source, not to a run —
  which the procedure template flags as weaker than executed evidence. This is disclosed
  in *Scope and omissions* rather than papered over.

## LEFT OUT

- Building the desktop app from source — `development/build.md` (`corpus-development-build`)
  is merged and canonical for that. This node links it and states the boundary.
- Installing toolchains — `development-prerequisites`, `development-hermit`.
- Running the relay, mobile app, or web client standalone — #866, #865, #867 own those;
  no such node exists on `origin/launchpad` today.
- Debugging a desktop app that started and then misbehaved — `debugging`.
- Packaging or releasing a desktop build — `desktop-release-build`, `RELEASING.md`.
