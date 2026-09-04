---
name: "update-page"
description: "Rewrite one stale section of an existing page — only that section — after its cited source has changed, grounded in a real diff rather than a full re-read-and-guess."
---

# Updating one stale section, and only that section

This skill exists because the original single-skill build had no update mechanism at
all — it could only draft whole new pages. Every `scan-repo` `stale` entry names one
page and one section; this skill's job is to rewrite that section's markdown span
(its heading through the next heading of the same or shallower level) and leave the
rest of the page untouched, byte for byte.

## 0. Resolve the target and the pack root, and load the entry

Same target resolution as `scan-repo`/`draft-page` (§0 in each) — including
confirming `$PROFESSOR_PACK_ROOT` is set (`draft-page` §0 has the exact fail-loud
message; every `<pack-root>` reference below, steps 3 and 5, means this variable).
Take the `stale` entry: page path, section anchor, `old_commit`, `new_commit`.

## 1. Diff, don't re-read-and-guess

Run `git diff <old_commit>..<new_commit> -- <path>` against the target's checkout for
every `sources[].path` entry the section's provenance record names (`provenance-log`
`read` mode, `latest` view — §8 has the exact shape; this is an array of `{repo, path,
commit, ...}` objects, not a flat `source_paths` list). This is the
evidence the rewrite is grounded in — a diff shows exactly what changed, which is a
narrower and more reliable basis for an update than reading the whole current file and
trying to guess what's different from a page drafted against an earlier version you
no longer have open. If the diff is empty for every cited path (the section's
provenance said stale but nothing in the actual diff touches what the section claims),
say so plainly rather than rewriting for the sake of rewriting — a section can be
correctly marked "cited commit is behind HEAD" while still being accurate, if the
change was elsewhere in the file and didn't touch the claimed behaviour.

## 2. Rewrite the section against the diff

Apply the same claim-tagging discipline `draft-page` §3 uses — behaviour claims cited,
opinion claims attributed to `author`, never both. The rewrite should read as if
drafted fresh against the current source, not as a patch note ("this used to do X, now
it does Y") — a reader who never saw the old version shouldn't be able to tell this
section was ever different, unless the change itself is the point being documented.

Identify the section's exact span precisely: its own heading, through (but not
including) the next heading at the same or a shallower level. Confirm the rest of the
page — everything outside that span — is unchanged before calling this step done; a
"section-scoped" update that accidentally touches neighboring prose isn't one.

## 3. Re-pin the citation, capture who changed the code and when, and re-confirm an
   external one still exists

Same rule as `draft-page` §4: a target-repo path gets its new commit, author, date,
and PR (if any) from one combined
`git log -1 --format="%H%x1f%aI%x1f%an <%ae>%x1f%s" -- <path>`, split on `\x1f` —
never just the bare commit. This matters more here than in `draft-page`: an update
exists specifically *because* the code changed, so the new `commit_author`/
`commit_at`/`pr` are the whole reason this section is worth re-reading, not an
afterthought to log alongside the commit. An external path gets the same four fields
from one call to `<pack-root>/tools/professor.py resolve-pin <repo> <ref>` via Bash,
which returns `{"commit": "...", "commit_author": "...", "commit_at": "...", "pr":
<int|null>}` (keeping them from the GitHub API response rather than discarding them,
per §9 Phase 1) —
**and then, same as `draft-page` §5, confirm the path with
`<pack-root>/tools/professor.py path-exists-at <repo> <commit> <path>`**. An external
citation can go stale in a way a target-repo one cannot: the upstream path itself can
be deleted or moved, not just changed, and nothing about re-resolving a pin catches
that on its own — only `path-exists-at` does. Skipping this check here (it does not
apply to the common, target-repo case) would leave update-page less careful about
external citations than `draft-page` is, for no reason tied to the actual risk.

## 4. Replace the section's inline provenance marker, then write to an isolated
   scratch copy of the page — not the target library yet

Same as `draft-page` §6: **replace this section's inline provenance comment now**,
using step 3's fresh `sources`, before either gate runs — the old marker described
the old commit and is wrong the moment the section text changes. This is what lets
`check-page` (step 5) verify the rewritten section's marker matches its content, the
same way it does for a first draft; a version of this step that deferred the marker
update to after publication would hand the gate a page whose marker still describes
stale sources, which `check-page` should treat as a defect and couldn't, since
nothing would have flagged it yet.

Both gates below need the complete page (with the section rewritten, marker
included) as a file argument, so write the whole page to a scratch path first, never
straight over the real file. The scratch copy is discarded once both gates have run;
only a clean pass writes back to the real path.

## 5. Run the contract gate

Resolve which gate to run in the same order as `draft-page` §7:
`<target-root>/.professor/check-page` if it exists and is executable, else
`<pack-root>/tools/professor.py check-page`. Run it against the **scratch copy of the
whole page**, not just the rewritten section — a section-scoped edit can still break
a page-level contract rule (e.g. a citation the edit removed was the only one backing
a claim elsewhere). Fix every finding (in the scratch copy) before moving on.

## 6. Hand off

Same as `draft-page` §8: the scratch copy goes to `screen-sensitive`, only after step
5 is clean (a stale section being refreshed can just as easily pick up something
sensitive from the new source as a freshly drafted one can — this gate is not only
for first drafts). Only a `pass`/`redact` result overwrites the real file; a `block`
leaves the real file untouched and discards the scratch copy. Once the real file is
updated (marker already correct, from step 4), `provenance-log` in `write` mode
**appends** one new line for *only* this section — passing step 3's full `sources`
(`commit_author`/`commit_at`/`pr` included, not just the new commit) — every other
section's provenance on the page stays exactly as it was; an update to one section is
not licence to append a line for every other section too, as if everything on the
page just changed. Same retry-safety note as `draft-page` §8: the file write and this
append are not one atomic operation, but appending is safe to retry (a duplicate line
is cheap to detect and ignore; a lost one is not), so an interruption between the two
is a recoverable state, not a corrupted one.

## Summary checklist

- [ ] `$PROFESSOR_PACK_ROOT` confirmed set before anything else ran
- [ ] The rewrite is grounded in a real `git diff` between the two recorded commits,
      not a full re-read of current source compared against memory of the old draft
- [ ] The section's span is exact — nothing outside it changed
- [ ] The section's inline provenance marker was replaced with the new `sources`
      **before** the scratch write — not left describing the old commit until after
      publication
- [ ] The re-pinned commit, author, date, and PR (if any) all came from the one
      combined `git log -1` call (target-repo case) or `resolve-pin` +
      `path-exists-at` (external-citation case — both, not just the pin), never
      memory, and never just the bare commit with the other three left out
- [ ] The whole page was written to a scratch copy before either gate ran
- [ ] The contract gate resolved a target override before falling back to the bundled
      subcommand, and reported no findings against the scratch copy of the whole page
      before `screen-sensitive` ever saw it
- [ ] `screen-sensitive` ran against the scratch copy before the real file was
      overwritten
- [ ] `provenance-log` updated only this section's entry, not the whole page's
