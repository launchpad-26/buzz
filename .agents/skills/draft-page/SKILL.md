---
name: "draft-page"
description: "Draft a handbook page that satisfies the page contract's provenance rules, using this pack's tools for every fact instead of recalling it."
---

# Drafting a handbook page

This skill is the procedure for turning a topic into a handbook page that passes
the Provenance gate on the first pull request. The five tools on the
`professor-tools` MCP server (`read_contract`, `list_categories`, `resolve_pin`,
`path_exists_at`, `check_page`) exist because each one answers a question you
cannot reliably answer from memory — a commit SHA, a live category list, whether
a path still exists, whether a draft actually passes the gate. Call them; do not
guess and hope review catches it. A guess that happens to be right teaches you
nothing about which guesses are wrong.

## 1. Read the contract before you draft anything

Call `read_contract()` first, every time, even if you drafted a page an hour
ago. Follow what it actually says about frontmatter fields, the claim rule, and
the reference format — not this skill's summary of it, and not what you
remember from the last page you drafted. The contract is a living document in
`launchpad-26/handbook`; this skill's paraphrase of it is not. If the two ever
disagree, `read_contract()` is right and this file is stale.

Do not start writing frontmatter or prose until you have that output in front
of you.

## 2. Pick a real category

Call `list_categories()` and choose one of the categories it returns for the
page's `category` field. Do not assume the handbook has eleven categories, or
thirteen, or any other number you recall from a design doc or a past page —
the nav list is live and can change. `list_categories()` is the only source of
truth for what a current category name actually is.

## 3. Draft the claims, and tag each one by kind — never both

Every sentence in the body that asserts something is either:

- **A behaviour claim** — how a system actually works today. It gets tagged
  with an origin prefix (`[upstream]`, `[launchpad]`, `[cohort]`, or
  `[supporting]`) and a source reference. The prefix must match the repo the
  claim is actually about: a claim about `block/buzz` behaviour is
  `[upstream]`, a claim about a fork-specific convention is `[launchpad]`, and
  so on — pick the prefix from which repo the *claim* describes, not from
  which repo you happened to read the fact in.
- **An opinion claim** — what the cohort *should* do. It gets no origin prefix
  and no source reference. Instead it is attributed to the page's `author`
  frontmatter field, which is who is accountable for the page's judgement
  calls.

A claim is never both. If you find yourself wanting to write a behaviour
sentence and also credit it to `author`, split it: state the behaviour with its
prefix and citation, then state the recommendation as its own sentence
attributed to `author`. Mixing the two in one sentence is exactly the failure
mode the contract's claim rule exists to catch, and `check_page` (step 5) will
catch it too, but it is cheaper to get it right the first time than to untangle
it after a failed check.

`read_contract()`'s own text has the authoritative detail on where a prefix may
sit in the markdown (paragraph, list item, quote, and their nesting) and where
it deliberately does not count as a claim (fenced code blocks, bare
indentation) — re-read that section if a placement looks ambiguous, rather than
guessing.

## 4. Resolve every pin with the tool, never from memory

For every source you cite, call `resolve_pin(repo, ref)` to get the full
40-character commit SHA that goes in `sources[].commit`. Never type a SHA you
recall or infer from a shorter one you've seen — a hallucinated SHA is a valid
40-character hex string that looks exactly like a real one, and it will point
at the wrong commit (or none) silently. A visibly malformed SHA at least fails
loudly; a plausible-but-wrong one is the worse failure, because nothing about
its shape reveals the mistake. `resolve_pin` is the only way to get a SHA that
is actually correct rather than merely well-formed.

## 5. Confirm every cited path exists at that pin

For every path you list under `sources[].paths`, call
`path_exists_at(repo, commit, path)` before you cite it, using the exact commit
you just resolved in step 4. A `False` result means either the path is wrong or
you resolved the wrong ref — fix it before moving on, don't cite the path
anyway on the assumption it's probably fine. Confirming existence here is
cheaper than finding out from a failed `reference-unresolved` or
`pin-path-missing` gate finding later, and it's the same check the gate itself
will run.

List only the paths the page actually draws on. An extra unused path creates
false staleness later; a missing one creates a citation nothing backs.

## 6. Check the draft before declaring it done

Once the page (frontmatter and body together) is complete, call
`check_page(draft_content)` with the full draft text. This runs the handbook's
real provenance gate against your draft — the same script CI runs — so it is
the closest thing to a dress rehearsal for the actual pull request. Do not
declare the task done without having called it at least once against the final
draft.

Read the result carefully; it is not one pass/fail bit:

- **`findings`** — real defects in the page (e.g. `prefix-repo-mismatch`,
  `reference-not-pinned`, `pin-path-missing`). Fix every one and re-run
  `check_page` until this list is empty. Don't ship past a finding.
- **`unchecked`** — sources in repositories the check can't see (the private
  cohort repos). This is a permission boundary, not a defect — it blocks
  nothing, and there's nothing to "fix" about it.
- **`skipped`** — the page's frontmatter didn't parse, so no rule ran on it at
  all. This is worse than a finding, not better: it means the check verified
  nothing. Fix the frontmatter and re-run.
- **`page_index`** — a second, independent check of required frontmatter
  fields and pin shape. Treat `page_index.errors` the same as `findings`: fix
  and re-run.

**One exception, and it matters:** if calling `check_page` itself raises an
error whose message names a rate limit, an authentication problem, or a
network/subprocess failure (for example, `resolve_pin` or `path_exists_at`
raising about GitHub API status 401/403/429, or `check_page` failing to refresh
its handbook checkout), that is the *check* failing, not the *page*. Don't
"fix" the page in response to a message like that — there is nothing in the
draft to fix. Retry the call once the underlying problem (auth, rate limit,
connectivity) is resolved, and only act on an actual `findings`/`page_index`
entry as a real defect.

## Summary checklist

Before calling the draft done, confirm:

- [ ] `read_contract()` called this session, and its actual field list/claim
      rule followed (not recalled from a prior draft)
- [ ] `category` came from a fresh `list_categories()` call
- [ ] Every behaviour claim has a matching origin prefix + citation; every
      opinion claim is attributed to `author` instead; no claim has both
- [ ] Every `sources[].commit` came from `resolve_pin`, not memory
- [ ] Every `sources[].paths` entry passed `path_exists_at` at that commit
- [ ] `check_page` was run against the final draft, its `findings` and
      `page_index.errors` are both empty, and any tool error you saw was
      triaged as either a real defect or a check-itself failure before you
      decided what to do about it
