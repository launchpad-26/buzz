---
name: corpus-author
description: Gather evidence first, then draft exactly one schema-valid corpus node from its task's manifest row and template. Use when a document task from corpus-plan is ready to be written. Not for planning tasks (corpus-plan) or reviewing a drafted node (corpus-review).
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Edit
---

# corpus-author — one task, one node, evidence before prose

Drafts exactly one corpus node from one document task, using
`launchpad/project-intelligence/corpus/evidence.py` (issue #625) to gather
evidence before writing anything and
`launchpad/project-intelligence/corpus/scaffold.py` (issue #632) to create a
schema-valid starting file. Read
`launchpad/docs/corpus/AGENTS.md` in full before your first use of this
skill — it is this repository's own governing procedure for corpus nodes,
resolved as the nearest `AGENTS.md` for every change under
`launchpad/docs/corpus/`, and this skill does not repeat what it already
says. Where the two disagree, `AGENTS.md` wins; fix this skill.

## One task, one document — checked, not assumed

Before drafting anything, confirm this task does not already own a
canonical document: check whether the task's target path already exists
under `launchpad/docs/corpus/`, and check open PRs against this task's
branch/issue for an in-flight draft. **If either is true, stop.** Authoring
a second document into an existing task's scope is exactly the failure
issue #629 exists to prevent — file the second document as its own task
(see "When you discover a second concept" below) rather than folding it in
here.

## Procedure

1. **Start from task metadata, not from a blank idea.** You need: the
   task's manifest row (path, template, purpose, audiences,
   source_start_points — from `corpus-plan`'s ledger) and the live issue
   number. If you cannot resolve the task to a manifest row, stop and ask —
   do not invent purpose or audiences from the issue title alone.

2. **Gather evidence before drafting anything.** Use `evidence.py`'s
   `collect_code_evidence` / `collect_adr_evidence` / `collect_commit_evidence`
   / `collect_pr_review_evidence` / `collect_issue_discussion_evidence`
   against the row's `source_start_points`, and build a bundle with
   `evidence.build_bundle`. Check `bundle.conflicts` before drafting a single
   claim — a non-empty conflict list means two sources disagree about the
   same thing, and per `AGENTS.md`'s citation of ADR-0029, **that is
   recorded and left flagged for a human, not resolved by you.** Do not
   pick a side.

3. **Record the repository revision.** `git rev-parse HEAD` — this is the
   `revision` `scaffold_node` needs, and it is also the FACT `AGENTS.md`'s
   "Creating a node" step 3 requires you to record before drafting.

4. **Resolve the template — real, provisional, or absent, and say which.**
   Check `launchpad/docs/corpus/templates/<row.template>.md`:
   - **Merged and present** → apply its structure and acceptance profile.
   - **Not merged, but an open PR exists for it** (issue #605's templates
     track — check `gh pr list --repo launchpad-26/buzz --search
     "<template> in:title"` if unsure) → you may use it, but say so
     explicitly in the node's body, naming the PR number, since its content
     could still change under review before it merges.
   - **Absent altogether** → `AGENTS.md`'s own words: *"Until the standards
     land there is no per-type template to follow: write the node against
     `node.schema.json` and the rules above, and expect a later task to
     reshape it."* Do exactly that, and say in the node's body (its scope
     section, per `AGENTS.md`'s "Creating a node" step 8) that it was
     written with no template because none existed yet at the recorded
     revision — this is not a workaround, it's the documented path.

   In every branch, `scaffold.py`'s `_known_templates` check is the
   ground truth for "merged and present" — if it raises `ScaffoldError`
   naming an unknown template, the template is not merged, full stop, no
   matter what you believe about an open PR.

5. **Scaffold the file — branching the way step 4 already did.**

   **Merged, or provisional via an open PR:**
   ```python
   scaffold.scaffold_node(root, row, node_type=..., origin=..., revision=revision)
   ```
   This gives you schema-valid front matter with exactly one evidence entry
   — the provenance citation. Everything from here is yours to add, never
   the scaffold's.

   **Absent altogether: do not call `scaffold_node`.** `_known_templates`
   returns an empty frozenset while `templates/` doesn't exist, so the call
   raises `ScaffoldError` on every invocation, and step 8 below treats a
   `ScaffoldError` as ground truth to stop on rather than something to work
   around — so calling it here would be a dead end, not a scaffold.
   Instead, hand-author the frontmatter yourself, directly against
   `launchpad/docs/corpus/schema/node.schema.json`: write the seven
   required fields, including one evidence entry recording the FACT from
   step 3 (the same provenance citation `scaffold_node` would otherwise
   have written), and say in the node's body — its scope section, per
   `AGENTS.md`'s "Creating a node" step 8 — that it was written with no
   template because none existed yet at the recorded revision. This
   continues step 4's "Absent altogether" branch; it is not a new
   decision.

6. **Classify every claim honestly.** Three classes, and this skill adds
   nothing to `AGENTS.md`'s own explanation of what they're for — read it
   there. The mechanical check this skill DOES add: **every evidence bundle
   entry from step 2 carries a `fact_eligible` flag, computed structurally
   by `evidence.py`, never by you.** `pr_review`, `pr_comment` and
   `issue_discussion` entries are always `fact_eligible=False` — if you are
   about to write `entry_class: FACT` for a claim whose only bundled
   evidence is one of those three classes, stop. That is exactly "issue
   discussion treated as an accepted decision," the failure this DoD item
   names, and `evidence.py`'s flag exists specifically so you don't have to
   re-derive the judgment by eye every time.

7. **Write the body.** Follow `AGENTS.md`'s "Creating a node" steps 7-9:
   one evidence entry per substantive claim, a scope section naming both
   what the node doesn't cover and what you expected to verify and
   couldn't, and relationships only to nodes that exist on the branch
   you're merging INTO (check `git ls-tree -r --name-only origin/launchpad
   -- launchpad/docs/corpus`, not your own worktree).

8. **Validate before proposing completion.**
   ```bash
   python3 launchpad/project-intelligence/corpus/validate.py
   ```
   Exit 0 is required, not advisory, before you report this task done. A
   non-zero exit is not something to characterize in prose — fix what it
   names, or stop and report you couldn't.

## When you discover a second concept

`AGENTS.md`: *"If a second concept, contract or procedure turns up while you
are writing, it does not get folded in. File it as its own task and link to
it."* Do this the moment you notice, not at the end after you've already
drafted both. File the new task, do not draft its content here, and add a
`references` relationship (never `depends-on` unless the node you're writing
genuinely cannot be understood without it) from this node to the new one —
only if the new task's node already exists on the merge-target branch; if it
does not exist yet, name the gap in your scope section instead of adding a
relationship that would fail validation.

## Never

- Never draft a second canonical document into a task that already has one
  — file it as a new task instead.
- Never write `entry_class: FACT` for a claim whose evidence is only
  `pr_review`/`pr_comment`/`issue_discussion` — `evidence.py`'s
  `fact_eligible=False` on those classes is not a suggestion.
- Never invent a template's structure when none is merged — use
  `AGENTS.md`'s documented no-template path instead, and say you did.
- Never propose the task complete without a clean `validate.py` run.
- Never silently resolve an `evidence.build_bundle` conflict by picking one
  side — record it, per ADR-0029, and flag the node's `status` as
  `flagged` if the conflict touches a claim central to the node.
- Never add a `relationships` entry targeting a node that does not exist on
  the branch you're merging into, even if it exists in your own worktree.

## Where this came from

Written for issue #629. The templates-gap handling (step 4) resolves a real
gap this Feature's own plan (`launchpad/plans/2026-08-27-issue-606-corpus-
tooling.md`) left open: at the time steps #624-#627 were built, zero corpus
templates were merged onto `origin/launchpad`. Rather than invent a fallback,
this skill defers to `AGENTS.md`'s own already-published answer to exactly
this situation.
