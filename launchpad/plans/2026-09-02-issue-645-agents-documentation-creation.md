# Plan: issue #645 — agents/documentation-creation.md

## ALREADY TRUE

- Target file `launchpad/docs/corpus/agents/documentation-creation.md` does not exist
  (confirmed: `ls launchpad/docs/corpus/agents/` shows only `invariants.md`).
- `launchpad/docs/corpus/templates/` carries 26 template ids, all `status: active`,
  all resolvable on `origin/launchpad` (confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`). The chosen
  template, `corpus-template-procedure` (`templates/procedure.md`), is one of them.
- `AGENTS.md`'s "Creating a node" step 4/5 caveat ("Until the standards land there is
  no per-type template to follow ... expect a later task to reshape it") is stale —
  the templates catalog it anticipated is now complete. That staleness, and how to
  supersede it without duplicating AGENTS.md's 10 steps, is this node's reason to exist.
- Issue #645's own DoD (`gh issue view 645`) is a how-to-shaped checklist: goal,
  prerequisites, ordered executable steps, success verification/rollback, links to
  authoritative commands — this matches `templates/procedure.md`'s Required sections
  (Overview, Before you start, numbered task sequence, See also, Boundary, Relationships,
  Scope and omissions), confirmed by reading `templates/procedure.md` in full.
- `check-plan.sh` does not exist anywhere in this repo (per prior-batch finding in
  auto-memory; not re-verified by a fresh search here, per that memory's own note).
  Proceeding without it.
- Siblings #646 (`documentation-update.md`) and #647 (`documentation-validation.md`)
  are unmerged; only their titles are known. This node states the boundary against both
  by title only.

## STEP 1 — Draft front matter and evidence ledger

Record repository revision (`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`) as a commit
citation. Classify every claim honestly: FACT for AGENTS.md/schema/template text
actually opened, TEAM_KNOWLEDGE for issue #645/#620's own DoD/body text, INFERENCE for
the `type: agent` choice (same reasoning precedent as `agents-invariants`).

Done-when: front matter is valid YAML with `id: agents-documentation-creation`,
`type: agent`, `status: draft`, `origin: launchpad`, `audiences: [agent, reviewer]`.

## STEP 2 — Write the body per `templates/procedure.md`'s required sections

Overview (one line: creating a new corpus node today, template-aware) → Before you
start (prerequisites: read AGENTS.md once, git access to check `origin/launchpad`) →
numbered task sequence (the genuinely new content: distinguishing `type` [surface]
from template [form], picking from the 26-template catalog using each candidate's own
Boundary/Note-on-type sections, citing AGENTS.md's steps 1-3/4-5/6-7/9/10 by number
rather than restating them, reconciling a DoD-checklist mismatch per `procedure.md`'s
own "Note on Definition of Done" precedent) → See also → Boundary statement (not #646,
not #647, not AGENTS.md itself, not a tutorial) → Relationships → Scope and omissions.

Done-when: every required section from `templates/procedure.md` is present; the
numbered sequence stays within the 8-10-step guidance (split into sub-steps if not).

## STEP 3 — Add relationships and cite real evidence

`depends-on: corpus-agents` (this node's authority is derived from AGENTS.md, not
original). `implements: corpus-template-procedure` (this node is a how-to instance of
that template). `references` toward one or two templates cited as worked examples of
the boundary-reasoning technique (e.g. `corpus-template-concept`,
`corpus-template-reference`) if their content genuinely supports a claim made in the
body. All three ids confirmed present on `origin/launchpad`. No edge to `agents-invariants`,
`agents/documentation-update`, or `agents/documentation-validation` unless a specific
claim needs it and the target actually resolves on `origin/launchpad` — the latter two
do not exist there yet.

Done-when: every declared relationship target is confirmed via the `git ls-tree` output
already captured above, not re-guessed.

## STEP 4 — Validate and iterate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
root. Fix schema errors, unresolved relationship targets, and citation-shape errors
until exit 0.

Done-when: `validate.py` exits 0.

## STEP 5 — Gate, commit, self/agent-review

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call; confirm `OK`. Commit with `git commit -s`.
Then run `Skill(review-code)` or the `serina:review-code` subagent against the diff;
if unreachable, self-review line-by-line against issue #645's real DoD and re-run
`validate.py` after any fix.

Done-when: commit exists locally with a signed-off trailer; review completed or
documented as unreachable with a self-review substituted.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (schema/graph/
  citation-shape validation).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  reports `OK` (the commit gate).

## BUDGET

5 steps, one document, no code changes outside `launchpad/docs/corpus/agents/` and
this plan file.

## OPEN

- Whether `#646`/`#647` will, once merged, want a `references` edge back to this node —
  their call to make, not this node's.
- Whether the reviewer agrees the DoD-mismatch reconciliation is warranted at all,
  given issue #645's DoD is a closer fit to `procedure.md` than `#1345`'s was — this
  node states the comparison and lets the smaller mismatch be smaller, rather than
  manufacturing a bigger one for symmetry with the precedent.

## LEFT OUT

- No edit to `AGENTS.md`, `templates/procedure.md`, or any sibling task's file.
- No push, no PR — integration happens later per the batch's own instructions.
