---
name: "provenance-log"
description: "Read or write the per-section provenance ledger for a page — who or what contributed a section, which commit it rests on, and when — so every doc section's origin is checkable, not asserted."
---

# Recording and answering provenance

This skill is a ledger, not a drafting step. `draft-page` and `update-page` call it;
you generally don't invoke it cold unless someone is asking "what does this section
actually rest on?"

Two representations of the same fact, kept in sync by giving each exactly one owner
rather than by writing both from the same place: the inline HTML comment above a
section's heading is content, and `draft-page`/`update-page` write it themselves, as
part of the draft, *before* either gate runs (their own §6/§4 explain why: `check-page`
needs to see it to check it, and it can't see something this skill hasn't written yet
if this skill only runs after publication). **This skill never writes the inline
comment.** Its `write` mode owns exactly one thing: appending to the `.jsonl` ledger,
after the page is already published. Two writers for the same marker was the earlier,
now-corrected version of this design — restated here because it's an easy mistake to
reintroduce by habit if the inline-comment step (`draft-page` §6, `update-page` §4)
isn't read first.

The ledger is an **append-only log**, not a snapshot — `.professor/provenance/<page-slug>.jsonl`,
one line per event, per section, forever. `write` mode always *appends* a line; it
never opens the file to rewrite or delete an earlier one, even when correcting a
mistake (correct forward, with a new event, the way you would in accounting — never
edit history). This is the redesign document's §8 recommendation ("Snapshot vs.
append-only log"), not the original two-slot design — if you're extending an older
draft of this pack that still describes a single rewritten JSON object per page,
that shape is superseded.

## `write` mode

Called with: page path, section anchor, `sources` (an array of `{repo, path, commit,
ref?, commit_author, commit_at, pr}` — `repo: "self"` for a target-repo-local
citation, the real `owner/repo` plus `ref` for an external one; `commit_author`/
`commit_at`/`pr` describe the **code change**, not the doc edit — see the redesign
doc §8 for the exact shape, why `sources` is an array rather than a single shared
commit over a flat path list, and why the code-provenance fields are kept separate
from this mode's own `by`/`at` below), and a contributor (an agent name plus
session/task reference — e.g. `the-professor` plus whatever identifies the current
run — or a human's identity, when step 1 below finds one).

1. **Check for a hand-edit first.** A hand-edit means: a human, working directly in
   the target repo (not through this pack), changed a section's text since this
   skill last recorded a "who wrote this" answer for it — a real scenario this
   design has to recognize, not just the case where nobody touched anything.
   **The discriminator is a recognizable identity for this pack's own writes, not a
   guess from blame alone**: every commit that carries a page this pack wrote should
   be identifiable as such — a dedicated commit author/email this pack's write path
   always uses (e.g. a bot identity), or a trailer in the commit message (e.g.
   `Generated-by: the-professor`) — settled once, concretely, as part of Phase 1
   (§9), not invented ad hoc per call. Given that identity, find the section's
   *current* line range in the page (its heading through the next heading of the
   same or shallower level) and run `git blame -L <start-line>,<end-line> --
   <page-path>` — not `git log` with a line range, which answers a different
   question (full history over a range, not "who last touched each line now"). If
   the blamed range's most recent commit does **not** carry that identity, that's a
   human edit, and the contributor for the event you're about to append should
   reflect that commit's real author instead of the caller-supplied one. **If the
   content hasn't been committed yet** (a fresh draft or rewrite, still sitting in
   the working tree when this mode runs), there is no commit to blame yet — skip
   this check for that call; it only ever applies to a page that already has commit
   history to compare against, which the very first `write` for a brand-new page by
   definition does not.
2. **Append one line** to `.professor/provenance/<page-slug>.jsonl` —
   `{"section": "<anchor>", "event": "added"|"updated", "at": "<ISO 8601>", "by":
   "<contributor>", "sources": [...]}`. `event` is `"added"` only for a section's very
   first line ever, `"updated"` for every line after — this is how "who created it"
   stays recoverable without a separate `added_by` field: it's just the earliest
   `"added"` line for that section, read back out by `read` mode's `history` view
   (below). Never open this file to edit or remove an existing line, including to fix
   a mistake — append a corrective event instead, the same way you would in
   accounting, not by rewriting the record. **Do not also write the inline
   comment here** — `draft-page`/`update-page` already wrote it, as content, before
   either gate ran (their own §6/§4); this mode's only output is the ledger line.

## `read` mode

Called with: a page path, optionally narrowed to one section anchor, and a view:
`latest` (default) or `history`.

`latest`: return only the most recent line for each requested section, **read from
the active `.jsonl` only** — the "current state" read every other skill actually
needs (`scan-repo`'s staleness check, `draft-page`'s citation lookups), and cheap
precisely because it never has to touch the archive (see `archive` mode below: the
one hard rule that mode obeys is what makes this true). `history`: return every
line, in order — **read the archive file first, if one exists
(`.professor/provenance/<page-slug>.archive.jsonl`), then the active file, in that
order** — for a person or a future skill asking "who has touched this section,
ever," not for routine drafting/scanning work. A `history` read that skipped the
archive would silently return an incomplete answer once archiving has run even
once; this is why `history` is the one view that costs more than `latest`, not
because it's used more often. Either way, return what's on record as-is; don't
summarize or interpret — a question like "is this section stale" belongs to
`scan-repo` (which checks each `sources` entry against a live `git log`/
`git cat-file`, or `resolve-pin`/`path-exists-at` for an external one), not to this
skill.

## `archive` mode — keeps the active log small without ever losing history

Called with: a page path, and `--older-than <days>` (default `365`).

**The one rule this mode can never break: never archive the most recent event for
any section, no matter how old it is.** `latest` view's whole cost model — cheap,
because it never reads the archive — depends on the newest line for every section
always being in the active file. A section nobody has touched in three years still
has its one and only event exempt from archiving for exactly that reason: it's both
the oldest and the latest for that section, and "latest" wins.

1. Read the active `.jsonl`. Group lines by `section`. For each section, sort its
   lines by `at` and **hold out the single most recent one, unconditionally** — it
   never moves, regardless of age.
2. From what's left (every section's non-latest lines), select every line older
   than `--older-than` days.
3. **Append** those selected lines, in their original order, to
   `.professor/provenance/<page-slug>.archive.jsonl` (create it if it doesn't exist
   — this file is append-only too, same discipline as the active log: never
   rewritten, never reordered, never deleted).
4. **Only after step 3's append is confirmed on disk**, rewrite the active `.jsonl`
   to contain everything *except* what was just archived — the held-out latest
   lines from step 1, plus any non-latest line younger than the threshold. This is
   the one place in this skill that rewrites rather than appends a file, and it's
   safe specifically because step 3 already durably copied anything about to be
   removed — a failure between steps 3 and 4 leaves a duplicate (a line in both
   files), never a loss, and a duplicate is cheap to notice and clean up by hand.

Not called by `write` or `read` mode, and not triggered automatically on every
write — that would put pruning logic on the hot path of a simple append, and risk a
race between an in-progress write and an in-progress archive touching the same
file. Called on a schedule instead (§7's scan hook interval is the natural one to
reuse — see the scheduled-scan workflow template, which calls this alongside
`library-index sweep`) or on demand.

## Tools

This skill never calls `tools/professor.py` — reading/appending to a local `.jsonl`
file and running `git log`/`git blame` against the target's own checkout are both
plain, local operations. If you find yourself reaching for a script here, you've
picked up the wrong skill for the question you're actually answering.

## Summary checklist

- [ ] `write`: hand-edit check used a recognizable pack-write identity to decide
      human-vs-suite, not a bare "any commit at all" guess — and was skipped
      cleanly (not treated as a failure) when the content has no commit history yet
- [ ] `write`: a line was **appended**, never an existing line edited or removed —
      including when correcting a mistake
- [ ] `write`: the appended line's `sources` carries `commit_author`/`commit_at`/`pr`
      per entry, not just the bare commit
- [ ] `write`: this mode did **not** also write the inline comment — that already
      happened in `draft-page`/`update-page`, before either gate ran
- [ ] `read`: `latest` view returns only the most recent line per section, from the
      active file only; `history` reads the archive (if any) before the active file
      and returns the full sequence only when actually asked for
- [ ] `read`: returned the record(s) as recorded, with no staleness judgement layered
      on top of it
- [ ] `archive`: the most recent line for every section was held out, unconditionally
      — never archived regardless of age
- [ ] `archive`: selected lines were appended to the `.archive.jsonl` file and
      confirmed on disk **before** the active file was rewritten to remove them —
      never the other order
