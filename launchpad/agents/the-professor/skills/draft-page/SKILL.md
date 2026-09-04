---
name: "draft-page"
description: "Draft a documentation page for one gap-report entry from a target repo's own source, against whichever contract resolves for that repo, using tools for every fact instead of recalling it."
---

# Drafting a page from a target repo's own source

This skill turns one `scan-repo` `new` entry — a documentable unit with no existing
page — into a drafted page. It reads the target's own code as primary evidence; it
does not draft claims about other repositories unless the unit being documented
genuinely wraps or depends on one (an external citation — step 4 covers that case
specifically, as the exception, not the default it was originally built around).

**Everything here is one section of the redesign document's tool design
(`launchpad/Research/the-professor-skill-suite-redesign.md` §4).** Read that section
once before running this for the first time — the short version: `tools/professor.py`
is a plain script, no MCP involved, and its network subcommands
(`resolve-pin`/`path-exists-at`) are needed only for the narrow slice of work that
touches a repo you don't have checked out. Nothing here requires them for the common
case.

## 0. Resolve the target, the pack root, and the contract

`PROFESSOR_TARGET` names the repo (see `scan-repo` §0 for the same resolution — reuse
it, don't re-derive it). **Also confirm `$PROFESSOR_PACK_ROOT` is set before doing
anything else in this skill** — every `<pack-root>` reference below (steps 4, 5, 6)
means "read this environment variable," per the redesign document's Open Questions
item 6. If it's unset, stop immediately and fail loud with a specific message —
`PROFESSOR_PACK_ROOT is not set; see this pack's README for how to configure it` — not
a generic error from whichever step first tries to use it. This check costs nothing
when the variable is set (which is the common case) and saves a confusing failure
three steps later when it isn't.

Then resolve the contract in the order the redesign document's §3 specifies:

1. `<target-root>/.professor/contract.md`, if it exists — that repo's own standard.
2. `tools/contract/page-contract.md` in this pack, otherwise — the suite default.

Read whichever one applies, live, every time — never from memory of a previous draft,
even one drafted minutes ago against the same target. A quoted contract goes stale
silently; a read one cannot.

## 1. Read the unit's own source

`Read`/`Grep` the paths `scan-repo` listed for this unit. This is the evidence the
page is drafted from. Don't stop at the first file that looks relevant — a module's
public surface is usually more than its entry point; check what it actually exports,
calls, and is called by, within the unit's own boundary.

## 2. Resolve where the page belongs

Call `library-index` in `place` mode with the unit's topic. It returns a category
(from `.professor/library.json` if the target already has one recorded, or a newly
resolved one, written back so the next unit on the same topic doesn't re-derive it).
Do not assume a fixed category list — the original build's `list_categories()` read
one hardcoded repo's `mkdocs.yml`; this pack has no equivalent fixed list, by design.

## 3. Draft the claims, and tag each one by kind — never both

Every sentence in the body that asserts something is either:

- **A behaviour claim** — how the unit actually works today, per the source you just
  read. It carries a citation: at minimum the source path; the exact commit comes
  from step 4. Use whatever prefix vocabulary the resolved contract specifies (the
  persona's own text has more on why this is no longer a fixed four-way scheme).
- **An opinion claim** — what should be true, or what's worth watching. It gets no
  citation. Instead it is attributed to the page's `author` frontmatter field.

A claim is never both. If you find yourself wanting to state a behaviour and also
credit it to `author`, split it — state the behaviour with its citation, then state
the recommendation as its own sentence attributed to `author`. This is the same
discipline `screen-sensitive` and the resolved contract's own gate (once §9's gate
script exists) will both check; getting it right the first time is cheaper than
untangling it after a failed check.

## 4. Pin every citation to a real commit — and capture who wrote that code, and when

Every source needs more than just a commit: the redesign document's §8 draws a firm
line between *who drafted this doc section* (you, or a human editor — that's
`provenance-log`'s `added_by`/`updated_by`) and *who wrote the code change the
section describes* (someone else entirely, possibly long before this page existed —
`commit_author`/`commit_at`/`pr` on the source itself). Get both, not just the first.

For a path inside the target repo (the common case): run one combined command, not
two — `git log -1 --format="%H%x1f%aI%x1f%an <%ae>%x1f%s" -- <path>` against the
target's local checkout, and split the result on the `\x1f` separator into commit,
author date, `"Name <email>"`, and subject. This is plain `git`, nothing more, and
it's the only correct source for all four fields, because the target is checked out
locally and its own history is authoritative without asking anything external. Parse
`pr` from the subject's trailing `(#NNNN)` if present (GitHub's default squash-merge
format) — if it isn't there, `pr` is `null`, not guessed at.

For a path in a *different* repo (the unit genuinely wraps or cites an external
source — the exception, not the default): run
`<pack-root>/tools/professor.py resolve-pin <repo> <ref>` via Bash. Never write a SHA
you recall or infer — a hallucinated SHA is a valid-looking 40-character hex string
that points at the wrong commit, or none, silently. `resolve-pin` returns
`{"commit": "...", "commit_author": "...", "commit_at": "...", "pr": <int|null>}` —
one structured object, not a bare SHA string (§9, Phase 1 — the subcommand keeps the
author/date/message the underlying GitHub API call already returns, rather than
discarding them the way the original `resolve_pin` did, and parses `pr` from the
message the same way the local `git log` case parses it from `%s`), so this is still
one call, not a second round-trip to get what step 4 needs for the local case.

## 5. Confirm every cited path exists at that commit

For a target-repo path: it does, by construction — you just read it and just resolved
its commit from the same checkout in the same step. Nothing to confirm.

For an external path (step 4's exception case): run
`<pack-root>/tools/professor.py path-exists-at <repo> <commit> <path>` via Bash. A
`false` result means the path or the resolved ref was wrong; fix it before citing it,
don't cite it anyway on the assumption it's probably fine.

## 6. Embed the inline provenance markers, then write the draft to an isolated scratch
   file — not the target library yet

**Add each section's inline provenance comment now, before either gate runs** —
`<!-- professor:section sources="..." updated_by=... updated_at=... -->` directly
above its heading, built from step 4's `sources` (§8 has the exact format). This is
content, not a separate ledger write: it's why `check-page` (step 7) can legitimately
require every section to carry one (page-contract.md's own "Provenance" section
explains the distinction) — the marker exists in the draft itself from this point on,
whereas the `.jsonl` ledger append only happens later, in step 8, once the page is
actually published. Getting this ordering right matters: a version of this skill that
deferred the inline marker to step 8 (alongside the ledger append) would hand
`check-page` a scratch file with no markers to check, making its own provenance
requirement impossible to satisfy — don't reintroduce that by moving this step later.

Both gates below (`check-page`, then `screen-sensitive`) need the complete draft —
markers included — as a file argument, so write it to a fresh temp path first
(mirroring the original `check_page()`'s own pattern: an isolated scratch location
holding nothing else, never the real target library). **This is not the write §7
forbids** — the section of `screen-sensitive`'s own text that says "never write
flagged content anywhere" is about the *real* target location and any logs, not about
this scratch file, which is the thing being screened in the first place and gets
deleted once both gates have run, pass or fail.

## 7. Run the contract gate

Resolve which gate implementation to run, same order as the contract itself (§3):

1. `<target-root>/.professor/check-page`, if it exists and is executable — the
   target's own gate takes precedence.
2. `<pack-root>/tools/professor.py check-page`, otherwise — the suite default.

Run whichever applies against the scratch file from step 6:
`<the resolved command> <scratch-file> --target <target-root>` — the mechanical
check of everything the resolved contract (step 0) requires: every required
frontmatter field present, every citation's path actually resolves, no sentence reads
as both a behaviour claim and an opinion claim. Fix every finding it reports (editing
the scratch file, then re-running) until the findings list is empty; don't hand a
draft to `screen-sensitive` (step 8) that this gate would reject — a page that fails
the contract gate doesn't become safe by also passing the sensitivity gate.

## 8. Hand off to the sensitivity gate — never write to the target library before it runs

The scratch file goes to `screen-sensitive`, only after step 7 is clean. This is not
optional and not something judgement decides case by case — see that skill's own
text for why. Only after it returns `pass` or `redact` does the page get written to
its real path in the target's library; a `block` result means the draft doesn't ship
in its current form, full stop, and the scratch file is discarded without its content
appearing anywhere else — no log, no retry-with-the-same-content, nothing.

Once written to its real path (inline provenance markers already in it, from step 6),
two more things need to happen — not guaranteed atomic with each other or with the
page write itself (this is a plain filesystem, not a transaction: a crash between
these steps is possible, and this design accepts that rather than building a rollback
protocol for it), but ordered so a partial failure is always safe to retry rather
than silently wrong:

1. Hand the page to `provenance-log` (`write` mode) to **append** the ledger event
   for every section — passing the full `sources` array from step 4,
   `commit_author`/`commit_at`/`pr` included per entry, not just the bare commits.
   Appending is idempotent-safe to retry: if this step fails and the whole hand-off
   re-runs, appending the same event again produces a duplicate line, not corruption
   — a cheap-to-detect problem (matching consecutive lines), unlike a lost write
   would be.
2. Update `library-index`'s `library.json` entry for this topic (still `page: null`
   from step 2's `place` call) to the page's real path, and add it under its category
   in `index.md`.

Skipping step 2 once a page is actually written is exactly the orphan condition
`library-index`'s `sweep` mode exists to catch — don't create it here by treating
step 2's category resolution as the whole job. Skipping step 1 (the ledger append) is
what `library-index sweep` should also treat as a defect once it exists to check for
it (a page whose provenance markers have no matching ledger entry) — not designed
further here, named so it isn't lost.

## Summary checklist

- [ ] `$PROFESSOR_PACK_ROOT` confirmed set before anything else ran — failed loud with
      the specific message if not, never a generic error from a later step
- [ ] Contract resolved live, in the target-override-then-suite-default order, not
      recalled from a prior draft
- [ ] Category came from a fresh `library-index` `place` call
- [ ] Every behaviour claim cites a real path in the target repo (the default case) or
      an external source resolved via `tools/professor.py resolve-pin` (the exception);
      every opinion claim is attributed to `author` instead; no claim has both
- [ ] Every target-repo citation's commit came from a live `git log -1`, not memory
- [ ] Every external citation's commit came from `tools/professor.py resolve-pin`, and
      its path was confirmed with `tools/professor.py path-exists-at`
- [ ] Every section's inline provenance marker was embedded in the draft **before**
      the scratch write — not deferred to the ledger-append step
- [ ] Draft was written to an isolated scratch file before either gate ran, never
      straight to the target library
- [ ] The contract gate resolved a target override (`.professor/check-page`) before
      falling back to the bundled `tools/professor.py check-page`, and reported no
      findings against the scratch file before `screen-sensitive` ever saw it
- [ ] `screen-sensitive` ran against the scratch file and returned `pass` or `redact`
      before the page was written to its real path — never `block`
- [ ] `provenance-log` ran in `write` mode for every section once the page existed at
      its real path
- [ ] `library.json`'s entry for this topic was updated from `page: null` to the real
      path, and the page was added to `index.md` under its category
