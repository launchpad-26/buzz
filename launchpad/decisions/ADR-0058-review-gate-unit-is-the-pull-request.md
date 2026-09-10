---
status: Accepted
date: 2026-09-10
issue: launchpad-26/buzz#574
decided_in: launchpad-26/buzz#574
supersedes: none
---

# ADR-0058 — The review gate's unit is a pull request's own scope, not a whole plan

## Decision

The review gate asks whether **the work in this pull request** was reviewed, not whether the plan
it belongs to is finished. The answer ships in two parts, sequenced, and the first is explicitly
temporary.

**Part 1 — now, and labelled interim.** `check-ledger.sh` gains a way for a branch to declare
which STEPs it covers, and gates only those. A branch landing STEPs 4, 6, 7 and 8 of a
twelve-step plan is then declarable as reviewed for what it actually contains, truthfully,
without a ledger asserting that STEPs 9–12 are done. The declared scope is **cross-checked
against commit subjects**, which already carry `(#118 STEP 8)`, so the claim is not pure
self-assertion — the weakness `check-ledger.sh:15` exists to distrust.

**Part 2 — the real answer, under #154.** N distinct review verdicts posted on the pull request
itself become required status checks, evaluated server-side by branch protection.

Part 1 is not a design. It is scaffolding with a stated demolition date, recorded below.

## Context

`check-ledger.sh` states its own purpose in line 2 — *"Does the SDD ledger account for every task
in the plan?"* — and enforces exactly that. Reproduced 2026-09-10 against a three-STEP plan with
two steps recorded complete:

```
PASS  plan declares 3 task(s): 1 2 3
PASS  ledger found: ./.superpowers/sdd/2026-09-10-fake-plan/progress.md
FAIL  task(s) 3 have NO 'Task N: complete' line in the ledger. Either they were never gated,
      or they were gated and not recorded — both mean the branch cannot be declared done.
      (recorded: 1 2)
exit=1
```

That is a correct answer to "is this plan finished?" and the wrong answer to "may this pull
request merge?" — and the second is the question being asked at the moment the gate fires. Every
intermediate pull request in a multi-STEP plan is therefore unmergeable through the gate, which
is most of what this cohort opens.

Two claims from #574's original filing (2026-08-24) no longer hold and are recorded here so this
decision is not read against a stale picture. A READY verdict is no longer unreachable:
`verdict.sh record ready --issue N` skips the ledger check explicitly rather than faking it, and
still runs the test gate; and `build-change/record-step.sh` now writes
`.superpowers/sdd/<plan>/progress.md` per completed step. The reachability half of that issue is
solved. What survives is the unit-of-gating question this ADR answers.

### The constraint that decides it

**A local hook cannot see the web UI.** `pr-gate.sh` runs on a contributor's machine. GitHub's
"Ready for review" and "Merge" buttons do not touch it. Pull requests #261, #566 and #2057 all
became non-draft or merged through that path with no recorded verdict — #2057 merged on
2026-09-06 with its own verdict still reading `NOT_READY`.

So Part 1 fixes what the gate *asks*. It cannot fix what the gate *reaches*. Only a required
status check closes that, because GitHub evaluates it rather than a hook on one laptop. That is
why Part 1 is interim and Part 2 is the decision's real content, and why any framing of Part 1 as
"the fix" is wrong.

This also matches the direction already standing for this cohort: review becomes required CI
checks, built as committed scripts, and **no model verdict may turn a check green.**

### Retirement condition for Part 1

Stated as a condition rather than an intention, because the known failure mode of a sequenced
answer is that the interim becomes the design.

- Part 1's implementation carries, in the script itself and in this ADR, that it is superseded by
  #154.
- Part 1's local gate is **demoted to advisory the day a posted-review status check is required
  on `launchpad`.** It is not removed before then, and it is not retained as a second enforcement
  path afterwards.
- If #154 has not shipped a required check by the close of this cohort's next PRD, that is the
  signal to reopen this decision — not to let Part 1 quietly become permanent.

## Consequences

**Good.** An intermediate pull request can be declared reviewed for its own contents, honestly,
without either fabricating a ledger or bypassing the gate. That restores the gate's ability to
distinguish reviewed work from unreviewed work in the common case, which an unsatisfiable gate
had destroyed.

**Good.** Cross-checking declared scope against commit subjects means the branch cannot simply
assert its own coverage. Forging it requires forging history that is already in the diff.

**Bad, and the reason Part 2 exists.** Part 1 remains local and remains bypassable by a button.
Anyone who wants past it still gets past it. This decision does not claim otherwise, and a reader
who takes Part 1 as enforcement has misread it.

**Bad.** Commit subjects are convention, not contract. A mislabelled commit changes the
cross-check's answer. This is accepted for an interim and is one more reason not to keep it.

**Neutral, stated for the next reader.** Implementing Part 1 means opening a pull request through
the gate this ADR calls mis-scoped. The honest route is `record ready --issue 574` — issue-driven
work, no plan, ledger recorded as not-applicable rather than faked — or being the first branch to
use the new PR-scope path against its own plan. Whichever is chosen belongs in that pull
request's body, not left for a reader to infer.

## What this does not settle

- **The mechanism for declaring scope** — a flag, a plan-file field, or derivation purely from
  commit subjects. Part 1's implementation chooses and justifies it; that is a build detail
  inside this decision, not a second decision.
- **How many verdicts, and from whom**, in Part 2. That is #154's, and the overlap between #574
  and #154 was flagged when #574 was first filed.
- **A lead that should be settled before Part 1 is built.** `check-ledger.sh` warns when a
  ledger's first line does not name its plan file — *"may be another plan's ledger, whose
  completions would falsely satisfy this check"* — and `record-step.sh` writes no such header;
  its first write is a `Task N: complete` line. Observed on a synthetic fixture only, **not**
  against a real `record-step.sh`-built ledger, so it may be wrong. If it is right, the supported
  tool produces a ledger the checker distrusts, and Part 1 touches that same checker.

## Security implications

No credential, permission, or exposure change. The risk this decision governs is the integrity of
review rather than confidentiality: a gate believed to be unsatisfiable is routed around, and
once bypassing is routine the gate stops being evidence that anything was reviewed. That is the
condition `check-ledger.sh:9-15` records as the reason it was written — something was once
*"merged — with NO review round and NO ledger entry"*, and *"the ledger is written by the same
agent that is supposed to obey it."*

Part 1 narrows that exposure without closing it. Part 2 closes it, by moving the decision off the
machine of the person it governs. Until Part 2 ships, this repository should be understood as
having an advisory review gate, not an enforced one.

## Provenance

Decided by Serina McFall, 2026-09-10, from four candidate options carried forward from #574's
original filing plus a fifth (PR-scope argument) that became available once the reachability half
was solved.

The issue resurfaced by accident rather than by review: `pr-gate.sh` blocked an unrelated pull
request (#2156) citing a twelve-day-old `NOT_READY` verdict belonging to #148. Clearing that
leftover surfaced the verdict on `task/571-explain-depth-rendering`, whose recorded reason was
that the branch *was* reviewed — review-code, an independent Codex pass, review-adjudicate,
review-final and review-tests all ran — but that no mechanism existed to record the fact in the
format the gate checks. Its pull request merged anyway. Three branches hit the same wall before
anyone connected them: #148, #571, and the #2153 branch that started the search.

Full evidence, the reproduction, and the option costings are in #574.
