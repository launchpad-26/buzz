---
name: "scan-repo"
description: "Scan a target repo for documentable units with no page, doc sections whose cited source has moved on since their recorded provenance commit, and doc sections citing paths that no longer exist — the gap report every other skill in this pack works from."
---

# Scanning a target repo for documentation gaps

This is where every run against a new target starts, and where every scheduled run
(`launchpad/Research/the-professor-skill-suite-redesign.md` §7) re-enters. It produces
a gap report; it never drafts or rewrites a word of documentation itself — that's
`draft-page` and `update-page`'s job, once this skill tells them what needs doing.

## 0. Resolve the target, every time

`PROFESSOR_TARGET` names the repo: a local path (default — the checkout the session
is already in, or an explicit `--target <path>`) or `owner/repo` when scanning a repo
this session hasn't checked out (mainly the scheduled-scan hook, running from outside
the target). Everything below assumes a local path; if you were given `owner/repo`
instead, resolve it to a local checkout first (clone it) rather than trying to run
`git log`/`Grep` against a repo you're not sitting in — this whole skill is local-only
by design, and local means a real checkout on disk, not a remote name.

Do not hardcode a repo name anywhere in this procedure. If you find yourself about to
type one in, stop — that's exactly the mistake this redesign exists to undo (see the
design document's §1, "Bug B").

## 1. Load prior scan state, if any

Read `.professor/scan-state.json` at the target's root. If it exists, it has a
`last_scanned_commit` — everything from step 2 onward is scoped to
`git diff --name-status <last_scanned_commit>..HEAD`, not the whole tree. If it
doesn't exist, this is a first run: scope to the whole tree, and say so plainly in
your output rather than silently treating a first run like an incremental one.

**Also load `pending`**, if the file has one — entries a prior run's step 5 couldn't
finish. Add every one of them to this run's report unconditionally, on top of
whatever the diff-scoped or full-tree scan below finds — they don't get re-detected
by the diff (the commit that would have surfaced them may already be older than
`last_scanned_commit`), so nothing else in this procedure will find them again on its
own. Deduplicate against what step 2/3 finds fresh in this same run before finalizing
the report in step 4, so an entry that's both still-pending and freshly-detected
again doesn't appear twice.

## 2. Inventory documentable units

A "documentable unit" is whatever the target repo organizes itself into — a crate, a
package, a top-level module, a public API surface, a CLI command. Don't guess a
generic definition; read the target's own structure (`Cargo.toml` workspace members,
`package.json` workspaces, a `crates/`/`packages/`/`cmd/` convention, whatever is
actually there) and use its own unit of organization. This mirrors the persona's own
rule: read what's actually there, never assume a shape from a different repo you've
seen before.

For each unit, check whether it already has a page: read `.professor/library.json`
directly (a plain file read, not a `library-index` call) for a topic entry whose
`page` field is a real path (not `null` — a `null` `page` means a category was
reserved but the draft never completed, which is not "already has a page"). **Do not
call `library-index` in `place` mode here** — `place` mode *creates* a category
mapping as a side effect, and merely checking during a scan must not mutate anything.
A unit whose draft later gets blocked by `screen-sensitive` would otherwise leave
behind a mapping and (if `place` also touched `index.md`) an index entry for a page
that never actually got written. No topic entry, or one with `page: null` →
candidate for the `new` list. `place` mode is only ever called later, by
`draft-page`, once a page is actually about to be written.

## 3. Check existing pages against their provenance

For every existing doc page's sections, read `.professor/provenance/<page-slug>.jsonl`
(via `provenance-log` in `read` mode, `latest` view). A section whose latest line has
`"event": "unknown-pre-existing"` (a page `library-index` `bootstrap` adopted rather
than generated — see that skill's own text for how that line gets created) has an
empty `sources` array, nothing to compare against for `stale`/`removed` handling.
**Fixed 2026-09-05, a review found the original text left these permanently stuck**:
add every such section to a new `needs_baseline` list instead of silently skipping it
— "skip it, it only enters real handling once something else touches it first" was
never true, because nothing in this design ever *did* touch it first. `needs_baseline`
entries are handed to `draft-page` in baseline mode (that skill's own text), not
`update-page` — there's no prior commit to diff against, only existing prose that
needs real citations established for the first time. Once that runs, the section gets
a real `"added"` line and re-enters normal `stale`/`removed` handling on every scan
after.

For every section that does have a real record, check **each entry in its `sources`
array separately** — a section citing one local path and one external path needs both
checked, by different means, and a result for one is never evidence about the other.

**For a `repo: "self"` entry** (the common case — a citation inside the target repo):
check existence first, separately from checking history — the two are different
questions and one cannot substitute for the other.

```
git cat-file -e HEAD:<path>          # existence at HEAD — exit 0 means it exists
```

A non-zero exit means the path is gone at `HEAD`. **This is not the same check as
`git log -- <path>` returning something or not** — `git log` returns a deleted
file's history right up to the commit that deleted it; it does not go quiet just
because the file is gone now. Using `git log`'s output alone to detect deletion
misclassifies every removed citation as merely stale, because there's always a log
to show. Add a path that fails the existence check to the `removed` list.

**Known limitation, not solved here:** this is not rename-aware. A file moved with
`git mv` reports `removed` at its old path — correctly, by this check's own
definition — and, if a fresh scan of the tree doesn't already have a page for its new
location, the moved unit separately reports `new`. Nothing here recognizes those two
as one event. `library-index`'s `sweep` mode is where that pair gets reconciled by a
human, not silently lost — don't try to add rename-detection here to avoid that
hand-off; that's scope creep into a harder problem this design doesn't need to solve
to be correct about the simpler one.

For a path that still exists, only then check whether it changed:

```
git log -1 --format=%H -- <path>
```

**For any other `repo` value** (an external citation): `scan-repo` does not verify
these itself — checking an external source means a network call
(`resolve-pin`/`path-exists-at`), and this skill is deliberately kept network-free so
a scheduled scan over a large repo stays cheap regardless of how many pages exist
(§4's design). Instead, add any section with at least one non-`self` source straight
to the `stale` list unconditionally, tagged `"needs_external_check": true` in that
entry, and let `update-page` (which already calls both subcommands per its own §3)
resolve whether it's actually current, actually stale, or the citation is actually
gone. This trades a small amount of unnecessary `update-page` work (it may find
nothing changed) for keeping `scan-repo` itself free of network calls — a deliberate
scope choice, not an oversight, and named here so it doesn't read as one.

If that commit differs from that `sources[]` entry's recorded `commit`, the section is
stale — add it to the `stale` list with both commits, so `update-page` has the exact
range to diff. A section citing multiple paths where some are removed and others are
merely stale goes on both lists, once per affected path — don't collapse a mixed case
into whichever list you checked first.

## 4. Write the gap report

```json
{
  "scanned_at": "<ISO 8601>",
  "since_commit": "<last_scanned_commit, or null on a first run>",
  "new": [{"unit": "...", "paths": ["..."]}],
  "stale": [{"page": "...", "section": "...", "old_commit": "...", "new_commit": "..."},
            {"page": "...", "section": "...", "old_commit": "...", "needs_external_check": true}],
  "removed": [{"page": "...", "section": "...", "missing_path": "..."}],
  "needs_baseline": [{"page": "...", "section": "..."}],
  "carried_over_from_pending": ["<entries from the prior run's pending list, folded into",
                                 " new/stale/removed above, listed again here only so",
                                 " it's visible that they came from a prior run, not this one's own scan>"]
}
```

Print it. **Do not write `.professor/scan-state.json` yet** — see step 5's ordering
rule first.

## 5. Hand off, then advance the bookmark only for what actually completed

- Every `new` entry → `draft-page`, one at a time.
- Every `stale` entry → `update-page`, one at a time.
- Every `removed` entry → `library-index` (sweep mode), for a human-reviewed decision
  about whether the page needs trimming, the citation needs replacing, or the whole
  page is now orphaned.
- Every `needs_baseline` entry → `draft-page`, in baseline mode (fixed 2026-09-05 —
  see that skill's own text; the existing content stays, only real citations get
  established where none existed).

**"Handed off" is not the same as "succeeded."** A `new` entry whose `draft-page` run
gets blocked by `screen-sensitive`, or a `stale` entry `update-page` couldn't resolve,
did not complete — it needs to be seen again on the next scan, not silently dropped.
So: track which entries actually finished (a page was written, or a section was
rewritten, or a removed-citation was reconciled) versus which didn't. Advance
`last_scanned_commit` to the current `HEAD` **only if every entry in this run's
report completed**. If any entry is still outstanding, write `scan-state.json` with
`last_scanned_commit` unchanged and a `pending` list naming exactly the entries that
didn't finish — the next scan re-checks those specifically (in addition to whatever
`HEAD` has moved to since), rather than either silently losing them or re-scanning
the entire tree from scratch every time something fails.

## Summary checklist

- [ ] `PROFESSOR_TARGET` resolved to a local checkout before anything else ran
- [ ] Scoped to `.professor/scan-state.json`'s last commit if one existed; scoped to
      the whole tree, explicitly stated as a first run, if not
- [ ] Any prior `pending` list was loaded and folded into this run's report — not
      silently dropped because the diff scope wouldn't have surfaced it again
- [ ] Documentable units inventoried using the target's *own* organizing convention,
      not an assumed generic shape
- [ ] Existing-page check for each unit was a plain read of `library.json`/`index.md`
      — never a `library-index` `place`-mode call, which would mutate state for a
      unit that might not end up drafted
- [ ] Existence checked (`git cat-file -e HEAD:<path>`) before history, for every
      cited path — never inferred from whether `git log` returned anything
- [ ] Gap report printed with `new`/`stale`/`removed` all present (even if empty)
- [ ] `scan-state.json`'s `last_scanned_commit` advanced only if every entry in this
      run's report actually completed; a `pending` list records anything that didn't
