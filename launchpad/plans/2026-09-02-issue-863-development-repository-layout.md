# Plan — issue #863: document `development/repository-layout.md`

Target: `launchpad/docs/corpus/development/repository-layout.md`
Shape: reference node, modelled on `launchpad/docs/corpus/templates/reference.md`
Branch: `task/863-development-repository-layout` off `origin/launchpad` @ `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`

## ALREADY TRUE

- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` returns 233
  paths; **no** `development/repository-layout.md` among them. The target does not
  exist. `ls launchpad/docs/corpus/development/` returns exactly four files:
  `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`.
- `development/workspace.md` (#871) is **OPEN** and is not a node — confirmed by both
  the `ls` above and `gh issue view 871`. So the boundary against it must be stated as
  a forward-looking gap, not as a link.
- The corpus template `templates/reference.md` (`corpus-template-reference`) is merged
  on `origin/launchpad` and prescribes: Reference description, structured entries,
  optional Commands, Boundary, Relationships, Scope and omissions.
- `crates/` holds 30 directories; the root `Cargo.toml` `[workspace] members` array
  holds 32 entries — those same 30, plus `launchpad/crates/knowledge` and
  `examples/countdown-bot` — and `exclude = ["desktop/src-tauri"]`. Verified by a
  script that set-differences the two, both directions empty.
- 158 content nodes on `origin/launchpad` (corpus tree minus `schema/`, `standards/`,
  `templates/`, `AGENTS.md`, `README.md`); 157 carry an unprefixed
  `<directory>-<stem>` id, 1 (`development/build.md`) carries `corpus-`. Measured, not
  assumed.
- `launchpad/AGENTS.md:69` lists an `upstream-intel/` directory; `ls
  launchpad/upstream-intel` reports no such file. Already filed as #2033 — record it,
  do not re-file, and do not reproduce the error in the layout table.

## STEP 1 — derive the layout from the tree, not from prose

`git ls-tree HEAD` for top level (mode column distinguishes tree/blob/symlink), then
`git ls-tree --name-only HEAD <dir>/` one level down for every directory the issue
brief names plus every one the top-level listing actually returns. Never copy
`AGENTS.md`'s crate table.

**done-when**: every row in the eventual table traces to a `git ls-tree` line I ran.

## STEP 2 — establish the upstream/fork boundary from primary sources

Read `AGENTS.md`'s fenced `launchpad-26 fork` block, `LAUNCHPAD.md`, and
`launchpad/AGENTS.md` §3 "Where cohort files go" including its named exception list.
Cross-check the exceptions against the tree (`.github/ISSUE_TEMPLATE/`, `bin/lefthook`
pin, the five deployment-provenance files, `.mcp.json`, cohort crates in the root
workspace, `desktop/src/launchpad/`).

**done-when**: the boundary statement names both the general rule and every exception I
verified on disk, and flags the one documented directory that does not exist.

## STEP 3 — draft the node

Front matter: `id: development-repository-layout`, `type: development`,
`status: draft`, `origin: launchpad`, audiences developer + agent. Provenance ledger:
first entry pins revision `aef93f2c2…`; one entry per substantive claim, FACT only
where I opened the source, INFERENCE with `confidence` where I reasoned, TEAM_KNOWLEDGE
with `provided_by` for issue-sourced statements.

Body: one `#` heading; reference-shaped tables for top level and one level down;
explicit Boundary and Scope-and-omissions; label every count as derived-by-command.

**done-when**: file written, under 1000 lines, exactly one `#` heading.

## STEP 4 — relationships

Only ids confirmed by `git show origin/launchpad:<path>`. Candidates:
`corpus-development-build`, `development-hermit`, `development-prerequisites`.
Declare only what genuinely holds; none is a valid answer.

**done-when**: every declared target verified against `origin/launchpad`, not the
worktree.

## STEP 5 — validate, re-verify, commit

`python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
Then re-open every citation and re-run every count **before** committing —
`git commit --amend` is blocked, so there is one clean shot.
Then the unittest gate bare and unpiped, then `git add` doc + plan, then
`git commit -s`.

**done-when**: validator PASS, unittest OK, one signed commit. **STOP** — no push, no PR.

## PARALLEL

Steps 1 and 2 are independent evidence-gathering and were run as batched tool calls.
3–5 are strictly sequential.

## GATES

| Gate | Command |
|---|---|
| Corpus schema + citations | `python3 launchpad/project-intelligence/corpus/validate.py` |
| Commit gate (bare, unpiped, sole command) | `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` |
| Relationship targets resolve on merge target | `git show origin/launchpad:<path>` per target |

## BUDGET

One document, one plan, one commit. No other file touched.

## OPEN

- `standards/naming.md` MUST 3 prescribes a `corpus-` prefix; 157 of 158 merged content
  nodes do not use one. Tracked in #2029 — noted in the node, **not** re-filed.
- Whether `desktop/src/launchpad/` should appear in `launchpad/AGENTS.md` §3's
  exception list (it is ADR-granted but not listed there) is not this node's to settle.

## LEFT OUT

- What each crate *does* — that is the `architecture/containers/*` nodes' subject.
- How to build any of it — `development/build.md` owns that.
- Cargo workspace mechanics in depth — #871 `development/workspace.md` owns that.
- Any second hand-authored corpus document.
