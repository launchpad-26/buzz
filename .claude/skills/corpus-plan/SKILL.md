---
name: corpus-plan
description: Turn a validated corpus manifest into real GitHub document tasks, safely — dry-run first, exact-title duplicate guards, idempotent resume. Use when the manifest (issue #626) is ready and tasks need to exist on GitHub. Not for authoring or reviewing a node's content.
allowed-tools:
  - Read
  - Bash
---

# corpus-plan — turn a manifest into GitHub tasks, safely

Consumes the outputs of two already-built, already-tested tools —
`launchpad/project-intelligence/corpus/manifest.py` (issue #626) and
`launchpad/project-intelligence/corpus/issue_plan.py` (issue #627) — and
orchestrates them into one safe procedure for creating the document tasks the
rest of the corpus effort depends on. **This skill does not decide what
documents the corpus needs.** That decision — the plan itself, as a list of
dicts matching `manifest.build_manifest`'s required fields — is handed to you;
this skill's job starts once that plan exists.

## Why dry-run is not optional

`issue_plan.apply` creates real GitHub issues. A mistake in the plan — a
wrong parent feature, a typo'd template name, a priority that doesn't match
the project's real option values — is cheap to catch in a dry run and
expensive to catch after forty issues exist with the wrong metadata.

**Never call `apply` before you have shown a human the `dry_run` output for
the same rows and gotten explicit go-ahead.** This is the skill's one
non-negotiable rule; everything else below serves it.

## Procedure

1. **Build the manifest.** Load your plan (list of dicts) and call
   `manifest.build_manifest(plan)`. If this raises `ManifestValidationError`,
   stop and fix the plan — do not work around a validation failure by
   dropping the offending row silently.

2. **Dry-run first, always.**
   ```python
   result = issue_plan.dry_run(manifest.rows)
   print(result.to_json())
   ```
   Show this to whoever is directing the work. Read every proposed title,
   parent, and blocker yourself before asking for go-ahead — a plausible-
   looking dry run can still carry a wrong parent_feature or a blocker
   pointing at an alias that doesn't exist in this plan at all.

3. **Apply only after explicit go-ahead**, and always pass the accumulated
   ledger back in on a second or later run:
   ```python
   result = issue_plan.apply(manifest.rows, port, repo, alias_ledger=previous_ledger)
   ```
   `apply` is idempotent by design (a title-search guard, not just the
   ledger, per issue #627) — but idempotent means "safe to re-run," not
   "safe to run without dry-running first." Every apply call still needs
   step 2 to have happened for these exact rows.

4. **Report what actually happened, not what you intended.** After `apply`
   returns, report the four separate result buckets by name:
   - `result.created` — issues genuinely created this run
   - `result.already_existed` — issues that existed before this run (from
     the ledger or found by title search); **not a problem, but distinct
     from `created`**, and conflating the two hides whether apply is
     actually idempotent
   - `result.manual_actions` — project fields the port could not write;
     hand these to a human verbatim, do not silently skip them
   - `result.unresolved_blockers` — blocker relationships not yet applied,
     either because the target doesn't exist yet or the port can't apply
     blocked-by relationships at all (`set_blocked_by` always returns
     `False` in this repo's port today — see issue #627's PR). Report these
     as an explicit list a human can act on, not as a caveat buried in prose.

5. **Link sub-issues, and verify the link, not just the call.**
   ```python
   linked = issue_plan.link_sub_issue(port, repo, parent_number, child_number)
   ```
   `link_sub_issue` already re-reads the parent's child list after linking —
   trust its return value, not the absence of an exception. If it returns
   `False`, the child is not actually linked under the parent no matter what
   the link call itself reported; add it to your own manual-action report.

## One document, one task — and what that means for you

`manifest.build_manifest` already rejects a plan where one document path is
assigned to two tasks, or one task owns two documents (issue #626). By the
time a manifest reaches this skill, that invariant already holds — **you are
not re-checking it, you are relying on it.** What IS yours to hold: never
construct a `PlannedIssue` or a raw `gh issue create` call outside
`plan_from_manifest`'s output. A hand-written issue bypasses every guarantee
the manifest gave you.

**Parent/sub-issue structure** mirrors the manifest's `parent_feature`
field: every document task is a sub-issue of the Feature issue named there.
Do not invent a different parent from context — if `parent_feature` names an
issue number that does not exist yet on GitHub, that is `apply`'s
`unresolved_blockers`-shaped problem (the parent doesn't exist), not
something to paper over with a guess.

**Blockers** are the manifest row's `blockers` list — other document paths
this one depends on. `apply` resolves a blocker alias to a live issue number
only if that alias is already in the ledger; a blocker on a document not yet
planned in this same run is correctly unresolved, not a bug.

## Resolving aliases to live issue numbers

An **alias** is a manifest row's `path` — stable, unique per document
(issue #626 guarantees this), and never a GitHub issue number, because the
number doesn't exist until `apply` creates it. After `apply` runs, the
alias→number mapping lives in `result.created | result.already_existed` —
**that dict is the resolution.** Persist it (a human decides where — this
skill does not invent a ledger file location) so a later `corpus-author` run
can look up "given this document's path, what issue am I working against?"
without re-deriving it from GitHub search.

**If an alias cannot be resolved** — it's not in the ledger, and
`find_issue_by_title` also finds nothing — the document has not been planned
yet. Do not guess an issue number. Say so and stop.

## Stop on ambiguous scope

Do not resolve any of the following by guessing; surface it and ask:

- A manifest row's `parent_feature` names an issue that doesn't obviously
  match its subject (e.g. a capability document parented under a platforms
  Feature).
- Two rows in the same plan look like they describe the same document under
  different paths.
- A blocker alias is spelled differently from any path actually in this
  plan (a likely typo, not a real forward reference).

None of these are `manifest.build_manifest`'s job to catch — its validation
is structural (paths, titles, counts), not semantic. Semantic plausibility
is why a human reviews the dry run in step 2.

## Never

- Never call `apply` for rows that haven't been dry-run and confirmed.
- Never construct an issue body or title by hand instead of through
  `plan_from_manifest`.
- Never report `result.manual_actions` or `result.unresolved_blockers` as
  if they were empty when they aren't — a short report that drops a
  non-empty list is worse than a longer one that includes it.
- Never treat "the apply call didn't raise" as proof a sub-issue link
  succeeded — only `link_sub_issue`'s return value does.
- Never invent a parent Feature, template name, or priority value not
  already present in the manifest row.

## Where this came from

Written for issue #628, after issues #626 (manifest) and #627 (issue-plan
helper) established the guarantees this skill relies on rather than
re-implements: one-document-one-task, idempotent resume via ledger + title
search, and honest reporting of what a `GitHubPort` could and could not do
automatically.
