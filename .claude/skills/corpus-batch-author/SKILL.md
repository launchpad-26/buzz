# Corpus batch author

Take a list of pre-scoped, single-document corpus Task issues and run each one through
plan → build → verify → draft PR, N issues at a time, looping until the list is
exhausted. Written for the overnight run against #608's 47 architecture-document
tasks; nothing below is specific to that Feature — any list of `type:task` issues that
each name exactly one canonical corpus document (per `launchpad/docs/corpus/AGENTS.md`)
fits.

## When to use

A batch of corpus document tasks exists, each already fully DoD'd (objective,
definition-of-done checklist, impacted-components, out-of-scope — the shape every
`corpus-plan:v2` issue carries), no cross-task ordering dependency, and the person
asking wants them produced as draft PRs without a human in the loop per document. Not
for a single document (use `plan-issue` + `build-change` directly) and not for a task
whose DoD is ambiguous or contested — that gets a human decision first, not a batch run.

## Why batches of N, not one big pipeline

Every implementer needs its own working tree — `build-change` is explicit that two
builders sharing one tree conflict — so parallel dispatch means one `git worktree add`
per issue. A batch boundary is a deliberate barrier, not a missed optimization: it
gives a natural checkpoint to notice a systemic failure (a broken assumption shared by
every task in this list) before it burns through the whole run unattended, and it keeps
the number of simultaneously-open worktrees and draft PRs bounded and legible.

## Per-issue loop

One agent, one worktree, one branch, one draft PR. In order:

**1. Isolate.**
```
git fetch origin launchpad -q
git worktree add __worktrees/task-<n>-<slug> -b task/<n>-<slug> origin/launchpad
cd __worktrees/task-<n>-<slug>
```
`<slug>` from the issue title. `cd` once, then stay there for the rest of the loop —
every command below assumes it.

**2. Read the issue.** `gh issue view <n> --repo <owner>/<repo> --json body --jq
'.body'`. The DoD checklist in the body is the spec. Do not re-derive scope from the
parent Feature or PRD — the issue is the input, same as `plan-issue` insists.

**3. Plan.** Write `launchpad/plans/<date>-issue-<n>-<slug>.md` in the `plan-issue`
shape (`ALREADY TRUE` / `STEP N` / `PARALLEL` / `GATES` / `BUDGET` / `OPEN` / `LEFT
OUT`), sized off the issue's own DoD — these are small, so the cap is 5 steps. Verify
against the actual repo state (`launchpad/docs/corpus/schema/`,
`launchpad/docs/corpus/AGENTS.md`, whether the target file already exists — it must
not) rather than assuming. Run `check-plan.sh` from wherever `plan-issue` is installed
in this session; if it fails, fix the plan before building, same as any other use of
that skill.

**4. Build.** Follow the plan's own steps. Concretely, for one corpus document:
   - Front matter: `id` (kebab-case, see naming below), `type` (per the corpus's
     top-level taxonomy — check `launchpad/docs/corpus/schema/node.schema.json`'s
     `type` enum, do not invent a value), `status: draft` (an authoring agent does not
     self-promote to `active` — that is a human call), `origin`, `audiences`,
     `evidence`. No `relationships` unless a target id you can confirm already exists
     in the loaded corpus resolves — an unresolvable target is a hard validation
     error.
   - Evidence: real citations — source paths/symbols, tests, migrations, config,
     commits, PRs, issues actually inspected. Never a citation to something not opened.
     FACT and INFERENCE both require `evidence`; INFERENCE additionally requires
     `confidence` and forbids nothing else; TEAM_KNOWLEDGE requires `provided_by` and
     forbids `confidence`.
   - No template exists yet for most node types (0 of 26 merged as of this writing).
     `AGENTS.md` says explicitly to write against `node.schema.json` and expect a
     later task to reshape the document — do not invent a template's structure, and do
     not block waiting for one.
   - Satisfy every bullet in the issue's own DoD checklist, not only the schema
     fields — each document type (container, context, deployment, flow, principle,
     standard, ...) carries its own tail of type-specific bullets in the issue body.
   - `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.

**5. Earn the commit gate correctly.** `verify-gate.sh` requires a fresh stamp from a
   real suite run, as the sole command in its own tool call, in this worktree
   specifically (each worktree stamps separately). **Use the corpus test suite, not
   `validate.py` alone and not `check-plan.sh`**:
   ```
   python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
   ```
   This is a real suite invocation the stamp writer is built to recognize (it matches
   on `python3 -m unittest` directly, not on a filename heuristic). Run it, confirm
   `OK`, and only then commit — in a **separate** tool call, `git commit -s`. If the
   gate still refuses with no stamp found, that is a finding to report, not something
   to route around — do not touch the stamp file yourself and do not add `--no-verify`.

**6. Verify.** Run `review-code` on the diff if the skill is reachable from this
   session; if it is not, perform the same read yourself and say so plainly rather than
   silently skipping it: re-read the diff against the issue's DoD checklist line by
   line, check every evidence entry actually supports its claim, confirm no second
   canonical document was created, confirm `validate.py` still exits 0 after any fix.
   **`review-adjudicate` and a cross-model pass are deliberately not run per document
   in this batch mode** — they are expensive per-document and this run trades them for
   throughput. Say so in the PR body (template below) so the deferral is visible, not
   silent.

**7. Open the PR, as a draft.**
   ```
   git push -u origin task/<n>-<slug>
   gh pr create --draft --repo <owner>/<repo> \
     --title "docs(corpus): <what this document is> (#<n>)" \
     --body "..."
   ```
   Body must state: which issue this closes (`Closes #<n>`), that `validate.py` and
   the corpus test suite both passed, which verification actually ran in step 6 (skill
   or self-review), and the one explicit line: **"Draft — adjudicate/cross-model pass
   deferred to the batch owner's review before merge."**

**8. Report** back to the orchestrating batch: issue number, PR URL or `BLOCKED` with
   why, nothing else claimed.

## Naming

`id`: `<parent-taxonomy-slug>-<category>-<topic>` from the target file's own path —
e.g. `launchpad/docs/corpus/architecture/containers/agent-runtime.md` becomes
`architecture-containers-agent-runtime`. Matches the precedent set by
`corpus-standard-confidence` and `corpus-readme` (slug mirrors the file's own
location, not the issue title).

## Batching protocol

Given an ordered list of issue numbers and a batch size N (default 5):

1. Take the next N issues.
2. Dispatch one isolated agent per issue, run in parallel, each following the loop
   above end to end.
3. **Wait for the whole batch** — every issue in it either has a draft PR or is
   reported `BLOCKED` — before starting the next batch. This is a deliberate barrier:
   it is the checkpoint where a batch owner notices a shared failure (a wrong
   assumption about the schema, a broken command) before it repeats across the
   remaining issues unattended.
4. Log the batch's outcome (PRs opened, anything blocked) before continuing.
5. Repeat from 1 until the list is empty.

**On a `BLOCKED` result:** do not retry it silently inside the same batch, and do not
let one blocked issue stall the others in its batch — they are independent worktrees.
Carry it forward in the final report as unresolved, with what was tried.

## What this skill does not do

- **Decide `status: active` for anyone.** Every document this loop produces is
  `status: draft` — promoting it is a human's call, made when they take it out of
  draft.
- **Run `review-adjudicate` or a cross-model pass per document.** Named above as a
  deliberate deferral, not an oversight.
- **Merge anything.** Drafts stay drafts until the batch owner reviews them.
- **Resolve an ambiguous DoD.** An issue whose checklist does not resolve cleanly
  against the current schema/`AGENTS.md` is reported, not guessed at, and should not
  have been in the batch list to begin with — that is a screening question for
  whoever assembles the list, per `plan-issue`'s own "ambiguity is surfaced, not
  resolved" rule.

## Where this came from

Written 2026-08-27 for the #608 architecture-corpus overnight batch (47 documents,
batches of 5), generalized past that Feature because nothing in the loop is specific
to it. The stamp-earning command in step 5 is called out explicitly because a live run
against a brand-new worktree found `check-plan.sh` alone did not reliably earn the
verify-gate stamp for reasons upstream of this skill (see verify-gate.sh /
post-bash.sh's own commentary on path-invoked suite detection) — the corpus unittest
suite is the one substitution confirmed to match the stamp writer's pattern directly,
not through the filename heuristic that missed.
