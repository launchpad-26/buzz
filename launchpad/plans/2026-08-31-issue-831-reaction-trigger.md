# Plan: issue #831 -- document capabilities/workflows/reaction-trigger.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/reaction-trigger.md` does not exist on
  `origin/launchpad` or in this worktree before this change.
- `crates/buzz-workflow` implements `TriggerDef::ReactionAdded` (`schema.rs:46-53`),
  its kind-only match in `trigger_matches_event` (`lib.rs:1038-1047`), its emoji/filter
  narrowing in `should_fire_workflow` (`lib.rs:883-931`), and its reaction-specific
  `TriggerContext` derivation in `build_trigger_context` (`lib.rs:942-1021`), all with
  dedicated unit tests already in the tree.
- `architecture-flows-workflow-execution` is merged to `origin/launchpad` and already
  documents the shared executor, SEC-006 authority recheck, and terminal run states
  every trigger path (including `reaction_added`) feeds into.
- Sibling issue #830 (`reaction-action.md`, the opposite direction -- a workflow adding
  a reaction) is not yet drafted; no branch or corpus node exists for it, so this node
  declares no relationship to it.

## STEP 1: Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/reaction-trigger.md` with
schema-valid front matter (`id: capabilities-workflows-reaction-trigger`,
`type: architecture` following the one merged flow-shaped precedent's own type choice,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer]`) and a body
covering: trigger/preconditions/termination, ordered interactions and data movement,
trust-boundary crossings, and failure/abort/rollback behavior with representative
verification -- the four bullets issue #831's DoD adds beyond the corpus-wide baseline.
Declare one relationship (`part-of` -> `architecture-flows-workflow-execution`) since
that node is merged and this node's own scope explicitly defers the shared
executor/authority/finalization content to it rather than duplicating it.

**Done when:** the file exists with every FACT evidence entry backed by a citation this
session actually opened, and the body's four required sections are each present and
scoped to the `reaction_added` trigger specifically (not the whole workflow-execution
flow, which the referenced sibling node already owns).

## STEP 2: Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.

**Done when:** the run adds zero new FAIL entries relative to the known 21 pre-existing
baseline failures tracked in issue #1951 (confirmed by running the same command against
`origin/launchpad` and diffing the FAIL count/names).

## STEP 3: Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`

**Done when:** the suite reports `OK`.

## STEP 4: Commit

`git add` the new corpus node and this plan file; commit with
`git commit -s -m "docs(corpus): document capabilities/workflows/reaction-trigger (#831)"`.

**Done when:** the commit exists on `task/831-reaction-trigger`, nothing is pushed, and
no PR is opened (a later integration phase folds this commit into Feature #613's PR).

## GATES

- `validate.py` clean (no new FAILs).
- `unittest discover` on the corpus test suite reports `OK`, run alone, no pipe/redirect.
- No second hand-authored canonical corpus document created.

## BUDGET

One file, one plan document, one commit. No code changes.

## OPEN

- Whether `type: architecture` is the best long-term fit for a narrower,
  single-trigger-condition node (as opposed to the whole-flow shape
  `architecture-flows-workflow-execution` uses) is disclosed as an `INFERENCE`
  (confidence 0.75) in the node's own evidence ledger, not resolved here.

## LEFT OUT

- Drafting sibling issue #830 (`reaction-action.md`) -- separate task, separate node.
- Editing `architecture-flows-workflow-execution` to point back at this new node --
  out of scope per issue #831 ("no second hand-authored canonical corpus document"),
  and it is not this task's node to edit.
