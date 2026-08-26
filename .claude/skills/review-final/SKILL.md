---
name: review-final
description: Review a whole branch once, before merge — whether it does what the issue asked, whether its steps drifted from each other, and which deferred findings must be fixed first. Use after the per-artefact reviewers and the adjudicator have run. Not for reviewing a single diff, and not for finding what they already covered.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Review — the whole branch, once

Answer the questions a diff-scoped reviewer structurally cannot, and triage what earlier
rounds deferred.

## Why this skill exists, and why it is the ONLY place branch breadth belongs

Four reviewers have already read this work, each scoped to one artefact and one diff.
The adjudicator has already confirmed, refuted and ranked what they found. **Repeating
any of that at branch scale is the expensive mistake, not thoroughness.**

Upstream measured exactly this. Their per-task quality reviewer inherited a
merge-readiness prompt, and their own write-up says:

> *"That frame licenses branch-level breadth on a one-task diff."*

Quality reviewers then cost **4–8× what spec reviewers cost** on the same tasks. The
fix was to scope per-task reviews tightly and keep **one** independent broad review at
the end. **You are that one.** So branch-level breadth is correct here and nowhere
else, and the corollary is that you must not re-do the narrow work.

## What only you can see

A reviewer reading one step's diff cannot answer any of these. They are your subject.

**1. Does the branch, as a whole, do what the issue asked?** Read the issue and the
plan, then ask what a reader of the issue would expect to be true now. A branch where
every step passed and the issue is still unmet is the failure this question exists for.

**2. Did the steps drift from each other?** The highest-value category, because it is
invisible per-diff by construction. Two commits can each be internally correct and
mutually inconsistent — one function throws where the next assumes a null return, one
step names a field the next spells differently, one adds a rule the next quietly
contradicts. **Trace one value or convention across every commit in the range**, not
each commit in isolation.

**3. Did the plan's `OPEN` items stay open?** The plan reserved decisions. Check that
nothing in the branch quietly answers one — in code, in a test fixture, or in prose. A
decision resolved sideways is still resolved.

**4. Was anything from `LEFT OUT` built anyway?** Scope creep is visible only against
the plan, and only at branch scale.

**5. Are steps reported `BLOCKED` genuinely still blocked?** A step blocked at build
time may have been unblocked by a later step. If so the branch is incomplete in a way
nobody noticed.

**6. Does the commit history tell the truth?** A commit message describing two files
whose diff touches three is a signal. So is a step's work landing in a commit named
for a different step.

**7. Was every step actually gated?** Run `check-ledger.sh` (below) first. A step that
was built and never reviewed is not a step with a small risk — it is a step with an
unknown one, and it is invisible to every reviewer including you unless someone counts.

**8. Does every field added to a shared contract have a consumer?** For each new field,
key or column this branch adds to something more than one component reads — a snapshot,
a JSON payload, a config schema, a database row — **name the code that reads it, or
report it as unused.** Grep for it; do not reason about it.

A producer with no consumer is invisible per-diff, because the diff that adds the field
is correct on its own terms. It is exactly the shape a step boundary hides: the step
ends at "the value is produced," and nothing owns "the value is used."

On the Loom build this was the single largest cluster of defects. Seven fields —
`refresh_error`, `collected`, `gh_cached_at`, `last_commit`, `flags`, `last_good`,
`generated_at` — were each produced with care and read by nothing. The consequence was
not tidiness: the dashboard rendered a green "live" badge over frozen data forever,
because the field carrying the error had no reader. **One `grep` per new field would
have found all seven.**

## Run the ledger check before you read anything

```bash
.claude/skills/review-final/check-ledger.sh PLAN_FILE [LEDGER_FILE]
```

Exit 0 means every task in the plan has a `Task N: complete` line. Exit 1 names the
tasks that do not, and any whose fix loop was left open.

**A failure is a Blocker regardless of how good the code looks**, because it means
nobody knows whether that code was reviewed.

### If the branch has no plan, this check does not apply — say so and move on

Issue-driven work has no SDD plan and no tasks, so the question "was every task
gated?" has no answer, and `check-ledger.sh` cannot be run at all: with no plan
argument it exits 1 saying `no PLAN_FILE given`. **That exit is not a Blocker. It is
an inapplicable check reporting that it is inapplicable.**

Read it as a Blocker and this skill produces a false blocking verdict on every
issue-driven branch — including, when this paragraph was missing, the branch that
added the paragraph.

`verdict.sh` already draws exactly this distinction and is the authority on it:

```bash
verdict.sh record ready --issue N     # no plan; records ledger as not-applicable
verdict.sh record ready PLAN_FILE     # plan-driven; runs the ledger check for real
```

It records `"ledger": "not-applicable: issue-driven, no SDD plan exists for this
branch"` rather than faking a pass, so a reader can tell the two apart later. Do the
same in your report: state that no plan exists, that the ledger check was therefore
skipped rather than passed, and that you are not treating its absence as evidence of
anything.

**`--issue` is not a way around the ledger on plan-driven work.** If a plan exists for
this branch, run the check. It records a different claim, and the difference is
visible to whoever reads the verdict.

### A third case: a plan exists, but no SDD ledger does

`launchpad-26/buzz`'s own `serina:plan-issue` skill writes plans with plain-text
`STEP N` markers (not `### Task N:` headings) and never produces the
`.superpowers/sdd/<plan>/progress.md` ledger `check-ledger.sh` looks for — that
repo's review methodology gates each step through `serina:review-code` /
`serina:review-tests` / a scoped re-review instead, with no ledger file as the
record. `check-ledger.sh` recognises `STEP N` headings (so the vacuity guard does
not misreport "found NO task headings" on a plan that plainly has structure), but
recognising the heading does not manufacture a ledger: `record ready PLAN_FILE`
correctly still refuses, now for the true reason ("no readable ledger at
.superpowers/sdd/.../progress.md") rather than a misleading one.

This is neither the "no plan" case (a plan exists) nor a case `--issue` may
honestly claim (claiming "no plan exists" would be false). Until this repo's
review methodology has its own ledger-equivalent — which is a design decision for
a human to make, not something to invent unprompted inside a review — a
`serina:plan-issue`-driven branch cannot self-record `READY` through this script.
State that plainly in your report (plan exists, ledger check correctly
inapplicable to this methodology, human marks the PR ready) rather than treating
the refusal as a defect in the branch under review.

### Where a clean result goes

Not into your findings block — that block has one row per defect, and a passing check
is not one. Put it in the closing section where you name what you looked for and did
not find. Stating it there is evidence; forcing it into the findings format means
either inventing a severity for good news or dropping the instruction.

Why this is mechanical rather than left to you: on the Loom build, tasks 11 and 12 were
dispatched, verified in conversation, and merged with **no review round and no ledger
entry**. Nothing noticed, because *the ledger is written by the same agent that is
supposed to obey it*. The gap surfaced by luck — a reviewer happened to read the ledger.
Luck is not a gate.

## What you must NOT do

- **Do not re-review the code, the tests, or the accessibility.** `review-code`,
  `review-tests` and `review-a11y` own those. If you find yourself checking a boundary
  condition or an ARIA attribute, you have drifted into their work — stop, and trust
  that it was done.
- **Do not re-litigate an adjudicated finding.** `CONFIRMED` and `REFUTED` are settled.
  If you believe a refutation was wrong, say so as one line in your prose and leave the
  verdict alone; it is not yours to overturn.
- **Do not hunt for new defects of the kinds already covered.** Your value is the
  cross-cutting view, and time spent duplicating is time not spent on it.
- **Do not decide whether to merge.** You report readiness; the human decides.

## Triage — the second half of your job

Earlier rounds left two lists behind: findings **deferred as Minor**, and findings
**parked with a ruling** when a fix loop hit its cap. Both were deliberately not fixed.

**Nobody has yet asked whether they should be fixed before this merges.** That is
yours.

For each item, one line: **must-fix-before-merge** or **defer again**, and why. Two
things make a deferred Minor into a must-fix:

- **It compounds.** Three deferred items in one file stop being cosmetic together.
- **The branch made it load-bearing.** Something new now depends on the thing that was
  merely untidy.

A roll-up nobody reads is a silent discard. If a list was handed to you, every item on
it gets a line.

## Constraints on your findings

- **Read the whole range, not the last commit.** `HEAD~1` silently drops every commit
  but one of a multi-step branch.
- **For a drift finding, cite both sides.** One file:line where the convention is set,
  one where it is broken. A drift claim with one citation is half an argument.
- **Check the issue, not your memory of it.** Read it.
- **A step the plan marked `BLOCKED` is not a defect.** It is a reported status. Only
  say something if it should now be unblocked.
- **Set severity from what merging would cost**, not from how much work the fix is.
- **Lead with your strongest evidence.**

## Categorise by harm, not by tidiness

| | |
|---|---|
| **Blocker** | merging this makes something wrong now — the issue is unmet, or two steps contradict each other in a way that breaks at runtime |
| **High** | merging leaves a contradiction that will break as soon as the next planned work lands |
| **Medium** | it works, and a maintainer reading the branch will draw a wrong conclusion from it |
| **Low** | it could read better |

Severity comes from **what merging costs**. A drift between two steps that no current
caller exercises is High, not Blocker — it is wrong the moment someone uses it, which
is not yet.

## What is not a review

- **Approving.** You report readiness; you do not grant it.
- **Praising a clean branch.** A short report is a good outcome, and "no cross-cutting
  findings" is a real result worth one line.
- **Restating the adjudicator's ranking.**
- **Scoring, grading, or counting commits.**
- **Hedging.** No "consider whether". Report nothing you cannot cite twice.

## Output

Findings, most severe first. For each:

- **`file:line` — take the line number from the diff's left gutter.** The package
  annotates every line with its number in the SOURCE file, so there is nothing to
  derive. Removed lines show `----`. For a drift finding, give **both** locations.
- Severity
- What is wrong, in one sentence
- **The concrete failure merging it lets through** — a specific caller, input or reader,
  and what goes wrong for them. Not "this is inconsistent"; name who breaks.
- The change you would make

Then, as its own section, **`## Triage`** — every deferred and parked item, one line
each, must-fix-before-merge or defer again, with the reason.

Then **`## Merge readiness`** — one paragraph. What a reader of the issue would find
true, what they would find missing, and what you could not check. **No verdict, no
recommendation to merge or not.** That is hers.

Close with:

- what you specifically looked for and did **not** find — name the questions above you
  answered negatively, because a negative answer to question 2 is a real result
- **the tools you actually have, by name** — a subagent's `tools:` list can only narrow
  the dispatching session's pool and a name outside it is dropped silently, so the same
  definition yields different capability in different sessions. A branch review without
  `Grep` cannot trace a convention across commits, and the reader must know that
- a plain statement of whether you are independent of the work under review

Then end the report with a fenced block the gate can parse: its opening line is three
backticks immediately followed by `findings`, with nothing else on that line, and it
closes on its own line with three backticks and nothing else — no worked example inside
it. One row per finding, most severe first. Each row has three fields, in order —
severity, `file:line`, one-line summary — separated by a **tab**, not spaces: a summary
contains spaces, so a space-separated parse would mis-split it. A single row reads, for
example, `High<TAB>src/store.ts:14<TAB>throws where src/load.ts:9 expects null`, where
`<TAB>` is a placeholder for a real tab character, not the two characters `\` and `t`.

For a drift finding, put the **primary** location in `file:line` and name the second in
the summary, as that example does.

**A severity here is a proposal, not a verdict.** The adjudicator re-rates every finding
and its rating is the one the gate reads — including yours. You are a reviewer, not the
last word.

Immediately after that block, end the report with the line `REVIEW COMPLETE` on its own.
A report without it is treated as truncated and fails the gate: a reviewer that runs out
of turns stops mid-branch, and a partial report reads exactly like a finished one, so
this line is the only signal that the review actually completed.

## Where this came from

Written 2026-07-30, after the per-artefact reviewers existed and the stage that reads a
whole branch did not.

Its scope discipline is the direct lesson of upstream's cost measurement: they found
that a merge-readiness frame on a narrow diff licensed branch-level breadth and cost
4–8×, and their remedy was to keep exactly one broad review, at the end,
**independent**. Every constraint above about not re-doing the narrow work exists so
that remedy holds here too.

The triage half exists because two lists — deferred Minors and parked findings — were
being produced with nothing downstream ever asking whether they should block a merge.
A roll-up nobody reads is a silent discard.
