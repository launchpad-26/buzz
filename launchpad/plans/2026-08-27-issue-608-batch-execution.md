# #608 batch execution — overnight run, 2026-08-27

Dispatch order and tracking for running all 47 of #608's child document tasks through
`.claude/skills/corpus-batch-author` (plan → build → verify → draft PR), 5 issues at a
time, looping until the list is exhausted. Companion to
`2026-08-27-issue-608-architecture-corpus.md`, which covers *what* the 47 documents
are; this covers *how* tonight's run executes them.

## Scope confirmed with Serina

- Batches of 5, one isolated worktree/agent per issue within a batch.
- Wait for a batch's PRs (or `BLOCKED` reports) before starting the next batch.
- PRs land as **drafts** — she takes them out of draft herself in the morning.
- `review-adjudicate` and the cross-model (Codex) pass are **not** run per document
  tonight — deferred to her own review pass across the accumulated drafts. Each PR
  body says so explicitly (see the skill's PR template).
- `status: draft` in every document's own front matter too — promoting a node to
  `active` is a human call, not this run's.

## Dispatch order (10 batches, sequential #652–#698)

All 47 are mutually independent — different files, no shared dependency — so the
grouping below is dispatch order for legibility, not a correctness requirement.

| Batch | Issues | Category (for reference) |
|---|---|---|
| 1 | #652–#656 | containers |
| 2 | #657–#661 | containers |
| 3 | #662–#666 | context (662–667) |
| 4 | #667–#671 | context tail (667) + deployment (668–671) |
| 5 | #672–#676 | deployment tail (672–674) + flows (675–676) |
| 6 | #677–#681 | flows |
| 7 | #682–#686 | flows |
| 8 | #687–#691 | flows tail (687–688) + principles (689–691) |
| 9 | #692–#696 | principles |
| 10 | #697–#698 | principles tail (2 issues only) |

## Progress

Update after each batch completes. `PR` = draft PR number; `BLOCKED` = reported with
reason, not retried silently within the run.

- [ ] Batch 1 — #652 #653 #654 #655 #656
- [ ] Batch 2 — #657 #658 #659 #660 #661
- [ ] Batch 3 — #662 #663 #664 #665 #666
- [ ] Batch 4 — #667 #668 #669 #670 #671
- [ ] Batch 5 — #672 #673 #674 #675 #676
- [ ] Batch 6 — #677 #678 #679 #680 #681
- [ ] Batch 7 — #682 #683 #684 #685 #686
- [ ] Batch 8 — #687 #688 #689 #690 #691
- [ ] Batch 9 — #692 #693 #694 #695 #696
- [ ] Batch 10 — #697 #698

## Known operational risk

`verify-gate.sh`'s commit stamp did not write reliably for a brand-new worktree
running `check-plan.sh` alone during this same session (traced to a gap in
`post-bash.sh`'s path-invoked-suite detection, not a real verification failure — see
the commit on `task/608-architecture-corpus-plan`). The batch skill's step 5 works
around this by using the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`) as the dedicated stamp-earning command, which matches the stamp
writer's pattern directly rather than through the filename heuristic that missed. If
an agent still reports a commit blocked with no stamp after running that suite as the
sole prior command, that is a real finding for the morning review, not something the
agent should route around.

## Morning follow-up (not part of tonight's run)

- Review each draft PR: adjudicate any findings, run the cross-model pass, confirm
  `status: draft` → `active` is warranted before flipping it.
- Any `BLOCKED` issue from the progress list above needs a human look before
  re-dispatching.
- `just corpus-validate` once against the full merged `architecture/` tree, per the
  content plan's STEP 6, once enough of the 47 have actually merged.
