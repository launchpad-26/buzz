# Plan: issue #651 — task: document agents/stale-documentation.md

## ALREADY TRUE

- Worktree `__worktrees/task-651-agents-stale-documentation` exists, branch
  `task/651-agents-stale-documentation` off `origin/launchpad`
  (`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`).
- `launchpad/docs/corpus/AGENTS.md` (id `corpus-agents`), `templates/policy.md`
  (id `corpus-template-policy`), `standards/provenance.md`
  (id `corpus-standard-provenance`), `standards/deprecation.md`
  (id `corpus-standard-deprecation`) and `agents/invariants.md`
  (id `agents-invariants`) are all merged on `origin/launchpad` and have been
  read in full.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` has
  been enumerated; none of Feature #620's siblings (`agents/*.md`,
  `ingestion/*.md`) are merged, including `agents/documentation-update.md`
  (#646, local-only in a sibling worktree — read for boundary only, no edge).
- Searched `gh issue list` for "stale" — found #556 (extend staleness
  *detection tooling* to canonical corpus nodes, open, unimplemented) and #904
  (generate `generated/stale-docs.md` index, unbuilt) as related-but-distinct,
  out-of-scope tasks; no existing corpus node already owns this policy gap.
- `node.schema.json` and `relationships.schema.json` read; `validate.py`
  grepped to confirm the commit-citation regex and `EXCLUDED_TOP_LEVEL_DIRS`.

## STEP 1 — Draft `launchpad/docs/corpus/agents/stale-documentation.md`

Policy-shaped node (`templates/policy.md`'s six sections), `type: agent`
(matches sibling `agents/invariants.md` and `agents/documentation-update.md`
reasoning: subject is the `agents/` corpus surface, not the `standards/`/
`templates/` governance surface).

Subject: staleness is a whole-ledger, detectable-vs-suspected distinction —
(a) a file-naming citation shows drift via `AGENTS.md`'s
`git diff --name-only <recorded-sha> -- <path>` technique (mechanically
checkable, narrow); (b) a claim rests on an unreachable citation shape
(commit/graph-edge/tool-result/URL) or on real-world drift no diff can see
(mechanically unverifiable, must not be assumed fresh). State MUST rules for:
what counts as stale-suspect, what a finder MUST do (never silently pass it;
record it), what MUST NOT be assumed (an unreachable citation is not "fresh"
merely because nothing flagged it), and who is on the hook when staleness
surfaces during unrelated review. Explicitly distinguish from
`standards/provenance.md` (governs an author already mid-edit deciding
whether the revision moves) and `standards/deprecation.md` (governs an
author's deliberate decision that a node is no longer current) — this node
governs the passive-drift case nobody has started editing yet.

Relationships: `depends-on: corpus-agents` (detection technique is drawn
directly from its "Checking whether cited files moved" section),
`depends-on: corpus-standard-provenance` (reuses its route classification of
which citation shapes are diff-reachable), `implements: corpus-template-policy`,
`references: corpus-standard-deprecation` (boundary: cites it as the
neighboring-but-distinct policy). All four resolve on `origin/launchpad`
(verified above). No edge to `agents/documentation-update.md` or
`agents/invariants.md`'s siblings under #620 — unmerged siblings excluded per
`AGENTS.md` step 9, `agents-invariants` I5.

## STEP 2 — Validate front matter and evidence honesty

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root; fix schema errors, unresolved relationship targets, and
malformed citations until exit 0. Re-check every `FACT` entry cites a source
actually opened in this session (AGENTS.md, provenance.md, deprecation.md,
node.schema.json, relationships.schema.json, validate.py — all read directly
above) rather than a second-hand paraphrase.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`, run as the sole command in its own tool call, before commit.
- Self-review (or `review-code`/`serina:review-code`) against issue #651's DoD line by line.

## BUDGET

2 steps, one document, no runtime/tooling code changes (`corpus/stale.py`
belongs to #556, out of scope here per issue #651's own Out of scope list).

## OPEN

- Whether #556, once built, will declare a relationship back toward this node
  — not decided here; #556 is a tooling task, not a corpus node, so it has no
  `id` to target yet.

## LEFT OUT

- Building `corpus/stale.py` or any detection tooling (#556).
- Building `generated/stale-docs.md` (#904).
- Editing `AGENTS.md`, `provenance.md`, or `deprecation.md` to cross-link back
  to this node — out of scope for this task; those files belong to other
  tasks/authors.
- Deciding whether a stale-suspect node should block a PR mechanically — no
  such check exists today (`validate.py` never runs `git diff`) and inventing
  one is #556's territory, not this policy node's.
