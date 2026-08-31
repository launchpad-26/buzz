# Corpus batch author

Take a list of pre-scoped, single-document corpus Task issues belonging to one Feature
and run each one through plan → build → verify → commit, N issues at a time, looping
until the list is exhausted — then integrate every issue's commits onto one shared
branch and open exactly **one** draft PR for the whole Feature. Written for the
overnight run against #608's 47 architecture-document tasks; nothing below is specific
to that Feature — any list of `type:task` issues that each name exactly one canonical
corpus document (per `launchpad/docs/corpus/AGENTS.md`) fits.

**One Feature, one PR.** Per-issue and per-batch worktrees/branches exist only for build
parallelism and are never pushed or opened as their own PR — see "Integrate into one
Feature PR" below. This replaced an earlier one-PR-per-batch default (see "Where this
came from") after Feature #612 needed a manual after-the-fact consolidation of 25 batch
PRs into one; doing that integration as this skill's own last phase, every time, means
no batch owner has to repeat that work again.

## When to use

A batch of corpus document tasks exists, all belonging to the same Feature, each already
fully DoD'd (objective, definition-of-done checklist, impacted-components, out-of-scope
— the shape every `corpus-plan:v2` issue carries), no cross-task ordering dependency,
and the person asking wants the whole Feature produced as one draft PR without a human
in the loop per document. Not for a single document (use `plan-issue` + `build-change`
directly) and not for a task whose DoD is ambiguous or contested — that gets a human
decision first, not a batch run.

## Why batches of N, not one big pipeline

Every implementer needs its own working tree — `build-change` is explicit that two
builders sharing one tree conflict — so parallel dispatch means one `git worktree add`
per issue. A batch boundary is a deliberate barrier, not a missed optimization: it
gives a natural checkpoint to notice a systemic failure (a broken assumption shared by
every task in this list) before it burns through the whole run unattended, and it keeps
the number of simultaneously-open worktrees bounded and legible. Batches are a build
checkpoint only now, not a PR boundary — see "Integrate into one Feature PR".

## Per-issue loop

One agent, one worktree, one branch, one commit — never pushed, never its own PR. In
order:

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
   throughput. Carry forward which verification actually ran (skill or self-review) to
   the integration phase — it goes in the one Feature PR's body, not a per-document one.

**7. Stop at the commit — do not push, do not open a PR.** The commit from step 5 stays
   local to this worktree's branch (`task/<n>-<slug>`). It is integrated into the one
   Feature PR later, in the integration phase below; a per-issue push or PR here would
   be immediately superseded and is wasted work (and, worse, a second thing a reviewer
   might mistakenly look at).

**8. Report** back to the orchestrating batch: issue number, worktree path, branch name
   and the commit SHA it ends on, or `BLOCKED` with why. Nothing else claimed — no PR
   URL, because none exists yet.

## Naming

`id`: `<parent-taxonomy-slug>-<category>-<topic>` from the target file's own path —
e.g. `launchpad/docs/corpus/architecture/containers/agent-runtime.md` becomes
`architecture-containers-agent-runtime`. Matches the precedent set by
`corpus-standard-confidence` and `corpus-readme` (slug mirrors the file's own
location, not the issue title).

## Batching protocol

Given an ordered list of issue numbers — all belonging to one Feature — and a batch
size N (default 5):

1. Take the next N issues.
2. Dispatch one isolated agent per issue, run in parallel, each following the loop
   above end to end.
3. **Wait for the whole batch** — every issue in it either has a local commit reported
   (per step 8) or is reported `BLOCKED` — before starting the next batch. This is a
   deliberate barrier: it is the checkpoint where a batch owner notices a shared
   failure (a wrong assumption about the schema, a broken command) before it repeats
   across the remaining issues unattended.
4. Log the batch's outcome (commits landed, anything blocked) before continuing.
5. Repeat from 1 until the list is empty.
6. Once every batch for the Feature is done, **integrate into one Feature PR** — see
   below. This step is not optional and is not deferred to "whoever reviews later";
   it is this skill's own last phase.

**On a `BLOCKED` result:** do not retry it silently inside the same batch, and do not
let one blocked issue stall the others in its batch — they are independent worktrees.
Carry it forward to the integration phase as unresolved, with what was tried, and note
its issue number as excluded when the Feature PR is opened.

## Integrate into one Feature PR

After every issue in the Feature's list has either landed a local commit or been
reported `BLOCKED`:

1. **Create one integration branch off the Feature's base**, fresh —
   `git fetch origin <base> -q && git worktree add __worktrees/feature-<n>-integration
   -b feature/<n>-<slug> origin/<base>`.
2. **Bring in every issue's commits, in issue order** — `git merge --no-ff
   origin/task/<n>-<slug>` per branch if you pushed intermediate refs, or
   `git cherry-pick <range>` straight from each worktree's local branch if you did not
   (either is fine; do not squash — a reviewer benefits from the per-document commit
   boundary same as the per-document DoD did). Stop and resolve if two issues' commits
   conflict — that itself is a finding (two tasks scoped to overlap) worth surfacing,
   not silently taking one side.
3. **Re-run the full corpus validator against the assembled branch — do not trust any
   individual issue's earlier `validate.py` run.** This is the step Feature #612's
   manual consolidation found necessary the hard way: batches built early in a long
   run can cite code that a later, unrelated upstream merge then restructures, so a
   citation that was correct when its own issue was built can be broken by the time
   the whole Feature is assembled, with no single issue's build having done anything
   wrong. Run:
   ```
   python3 launchpad/project-intelligence/corpus/validate.py
   ```
   from the integration worktree's root. Any break this surfaces gets the same
   treatment as evidence: re-open the cited claim's *current* location, re-confirm it
   still holds, and only then repoint the citation — never a blind path substitution.
   If a claim no longer holds at all, leave the citation broken and say so explicitly
   rather than inventing one.
4. **Re-earn the commit gate** the same way step 5 of the per-issue loop does (the
   corpus unittest suite, as the sole command in its own tool call, then `git commit -s`
   in a separate call) before committing any citation fixes from step 3.
5. **Push once, open exactly one draft PR** for the whole Feature:
   ```
   git push -u origin feature/<n>-<slug>
   gh pr create --draft --repo <owner>/<repo> \
     --title "docs(corpus): <Feature's own title> (Feature #<n>)" \
     --body "..."
   ```
   Body must state: `Closes #<n>` (the Feature issue) plus every child issue number
   closed (and any left `BLOCKED` and excluded, named explicitly, matching the
   convention `gh pr view 1944 --repo launchpad-26/buzz` shows for Feature #612's own
   consolidated PR); that `validate.py` and the corpus test suite both passed on the
   assembled branch; which verification actually ran per document in step 6 of the
   per-issue loop; and the one explicit line: **"Draft — adjudicate/cross-model pass
   deferred to the batch owner's review before merge."**

## What this skill does not do

- **Open more than one PR per Feature.** Per-issue and per-batch branches exist only
  to isolate builds; they are never pushed and never get their own PR.
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

Originally shipped one PR per document; Feature #610's overnight run (2026-08-30)
moved to one PR per batch of N after Serina picked that tradeoff explicitly (fewer PRs
to manage, a bad batch doesn't stall the rest, review chunks stay readable). Feature
#612's 25 batches (2026-08-31) then needed a manual, after-the-fact integration into
one PR — 25 separate reviews of one Feature was more overhead than the batch boundary
was meant to buy, and reassembling them surfaced 118 evidence citations broken by an
unrelated upstream `crates/buzz-db` restructure that landed partway through the batch
run, invisible to any single batch's own (by-then-stale) CI. Serina's direction
afterward: every Feature run through this skill produces exactly one PR going forward.
Batch-of-N stays as the build-parallelism/checkpoint mechanism; the integration phase
above is what turns N batches back into one review.
