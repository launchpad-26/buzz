# Plan: issue #810 — document capabilities/projects/project-channel.md

## ALREADY TRUE

- Worktree `__worktrees/task-810-project-channel` exists on branch
  `task/810-project-channel`, forked from `origin/launchpad` at
  `cad6c375fdcc590158c1456c9fc7875f0f84a844`.
- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad`;
  no sibling capability node (`capabilities-projects-*`) is merged, so no
  `relationships` target resolves and none will be declared.
- A `capability` template already exists at
  `launchpad/docs/corpus/templates/capability.md` (not under `schema/templates/`
  as originally guessed) — required sections: Capability statement, Maturity,
  Boundary, Relationships, Scope and omissions.
- Code investigation is complete: a Buzz project (`kind:30621`, NIP-MP) carries
  an optional single `buzz-channel` tag naming its home/discussion channel
  (`docs/nips/NIP-MP.md`, `crates/buzz-core/src/kind.rs`,
  `crates/buzz-cli/src/commands/projects.rs`). Separately, an agent may request
  an *additional* channel scoped to that project via
  `buzz projects add-channel`, gated on the project owner's approval in Buzz
  Desktop, recorded as repeatable `buzz-related-channel` tags distinct from the
  single home-channel tag (`crates/buzz-cli/src/agent_management.rs`,
  `desktop/src/features/projects/*`).

## STEP 1 — Write the corpus node

Create `launchpad/docs/corpus/capabilities/projects/project-channel.md` with
`type: capabilities`, following the template's required sections. Cite every
claim as `path:line`/`path:start-end` (no `#symbol=`/`#line=` fragments — those
don't resolve in `validate.py`, per a prior batch run's finding recorded in
`corpus-agents`'s own evidence ledger). No `relationships` — nothing to point
at yet.

Done when: file exists, front matter is schema-shaped, body has all five
required sections.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Baseline is 21 pre-existing FAIL entries (issue #1951, unrelated to this
capability). Confirm this node adds zero new FAIL entries.

Done when: FAIL count is unchanged from baseline.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`.

Done when: test run prints `OK`.

## STEP 4 — Commit locally

`git add` the new document and this plan file; `git commit -s` with message
`docs(corpus): document capabilities/projects/project-channel (#810)`. Do not
push, do not open a PR — a later integration phase folds this commit into one
Feature #613 PR.

Done when: commit exists on `task/810-project-channel`, working tree clean.

## STEP 5 — Self-review

Re-read the diff against issue #810's DoD line by line. Re-open every cited
source to confirm it says what the statement claims. Confirm no second
canonical document was created and no new `validate.py` FAIL entries. Note
that `review-code`/`review-adjudicate` were not run (deferred per batch mode).

Done when: every DoD bullet is checked off against the actual diff.

## PARALLEL

None — single file, single commit, no dependency on sibling tasks (#809, #811,
#812) since no relationships are declared toward them.

## GATES

- `validate.py` exits 0 with no new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`.
- Commit-msg hook adds `Signed-off-by` (via `-s`).

## BUDGET

One file (~150-220 lines), one commit. No code changes, no test changes.

## OPEN

- Whether the desktop "related channel" convention (`buzz-related-channel`)
  will eventually be folded into NIP-MP itself, or stay a client-only
  convention riding on NIP-MP's "ignore unrecognized tags" rule — left as an
  open question in the node's own Scope and omissions, not resolved here.

## LEFT OUT

- Documenting `#809` (branch-as-room / per-branch channels), `#811`
  (project-repository membership) and `#812` (project, the overall
  capability) — explicitly out of scope, each is its own task.
- Any change to runtime product behavior.
