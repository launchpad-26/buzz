---
name: "library-index"
description: "Own a target repo's documentation library as a whole: where pages go, the contents/index page, and the library's health — duplication, orphaned pages, broken cross-references."
---

# Bootstrapping and maintaining the library

This skill replaces the original build's hardcoded `list_categories()` — one repo's
`mkdocs.yml` `nav:` list — with something that works for a target repo that has no
navigation config at all, which is the common case. It runs in three modes.

## `bootstrap` mode — once per target, on first `scan-repo` run

1. **Detect an existing convention** before assuming one needs to be created. Look
   for a `docs/` directory, a `wiki/` the repo links to, or any directory a
   `README.md` points at as "see the docs." If found, adopt it — the library lives
   where the repo already expects documentation to live, never in a second location
   competing with the first.
2. **If nothing is found**, create `docs/professor-library/` at the target's root,
   with `index.md` as the contents page (a flat list to start; categories accumulate
   as `place` mode resolves them).
3. **If an existing convention *was* found (step 1) and it already has pages**, index
   what's already there before treating `library.json` as empty. For each existing
   page: record `{category, page}` in `library.json` against that page's topic — the
   category from its actual location (which directory it's already filed under), the
   `page` field its real path — and check whether it has a
   `.professor/provenance/<page-slug>.jsonl` log. **A page with no log predates this
   suite. Create one now, rather than leaving the page with nothing for `scan-repo` to
   read** — one line per section actually in the page,
   `{"section": "<anchor>", "event": "unknown-pre-existing", "at": null, "by": null,
   "sources": []}`. This is a real log entry, at the same per-section granularity
   every other page's log uses (never a page-level flag in `library.json` alone —
   `scan-repo` §3 reads `.jsonl` logs section by section, and a page-level marker
   would give it nothing to find there), just one whose fields are `null` because
   nobody here generated the content or knows its origin. Don't fabricate a
   commit/contributor for it, and don't crash or skip the page instead. `scan-repo`
   §3 adds every `unknown-pre-existing` section to its `needs_baseline` list (fixed
   2026-09-05 — an earlier version of this text said these sections just wait for a
   future citation check to fail, which can never happen against an empty `sources`
   array with nothing to check; `needs_baseline` routes them to `draft-page`'s
   baseline mode instead, which is what actually gets them a real citation and out of
   this state).
4. **Only once step 3's indexing is done** (or immediately, if step 1 found nothing),
   write/confirm `.professor/library.json`. Don't pre-populate categories for topics
   nothing documents yet by guessing at a taxonomy; let new ones emerge as `place`
   mode resolves them.

## `place` mode — called by `draft-page` for every new page, *before* the page exists

**This mode only ever runs once `draft-page` has committed to writing a page** — never
during `scan-repo`'s existence check, which reads `library.json` directly instead
(see that skill's own text for why calling `place` from a read-only check would be
wrong: it mutates the map for a unit that might never actually get drafted).

1. Check `.professor/library.json` for a topic that already matches (same
   documentable-unit family — e.g. two CLI subcommands under the same parent command
   belong in the same category). If found, return that entry's `category`.
2. If not found, resolve a new category from the unit's own place in the target
   repo's structure (a crate's own name, a top-level module's directory name) rather
   than inventing a taxonomy independent of how the code itself is organized — the
   library should read as a map of the repo, not a separate abstraction over it.
3. Write `{category, page: null}` for the new topic to `library.json` — `page` stays
   `null` at this point because the page doesn't exist yet (`place` runs before
   `draft-page`'s gates; the page might still be blocked). Return the category so
   `draft-page` can finish drafting.
4. **Once `draft-page` actually writes the page** (after both gates pass), it — or
   `provenance-log` on its behalf — updates that same `library.json` entry's `page`
   field to the real path, and adds the page to `index.md` under its category
   (creating the category's heading in `index.md` if this is its first page). A page
   that exists but isn't reachable from `index.md`, or a `library.json` entry whose
   `page` is still `null` for a page that actually got written, is exactly the orphan
   condition `sweep` mode exists to catch — don't create that condition here by
   skipping this step once the write actually succeeds.

## `sweep` mode — on the same schedule as the scan hook, or on demand

Reads the whole library, five checks (extended 2026-09-05 — the last two are new,
added alongside two decisions the redesign doc's §6.6 already specified but this
file hadn't caught up to yet), none auto-fixed:

1. **Duplicate-topic pages** — two or more pages whose content (or, cheaply, whose
   title/first-heading and cited source paths) overlap heavily enough to be about the
   same thing. Report them as merge candidates; don't merge automatically — which
   version is more accurate, or whether they cover genuinely distinct angles of the
   same topic, is a judgement call for a human reviewer, same caution the original
   design gives for anything an agent could self-certify.
2. **Orphaned pages** — any page under the library root not reachable by following
   links from `index.md` (directly, or transitively through a category page). A page
   that exists on disk but that no reader could find by browsing from the front page
   is functionally lost.
3. **Broken cross-references** — every relative link inside every library page,
   resolved against the filesystem; report any that don't resolve to a real path.
   External (`http(s)://`) links are out of scope for this check — verifying the
   living internet is a different problem than verifying the library's own internal
   consistency.
4. **Contradicting claims** — group every section's `sources[]` entries across the
   whole library by `{repo, path, commit}` **and overlapping `span`** (corrected
   2026-09-05 — grouping by `{repo, path, commit}` alone, without `span`, would
   compare two claims about different, unrelated lines of the same file, which the
   redesign doc's own §6.6 never intended; two spans overlap when their line ranges
   intersect, or when either entry's `span` is `null` — a whole-file claim can
   contradict a line-specific one about that same file). Within a group of more than
   one section, compare the actual claim sentences for disagreement (a fresh,
   isolated check per group — same discipline as `verify-claims`, not a
   self-comparison). Report disagreeing pairs; two sections citing unrelated code, or
   non-overlapping lines of the same file, are never compared, which is what keeps
   this bounded instead of an all-pairs comparison over the whole library.
5. **Published pages with no matching provenance ledger entry** — corrected
   2026-09-05, an earlier version of this check was circular (it read a ledger's
   latest line to decide whether the ledger had one, which is always true if a line
   exists to read at all). The actual check: for every section heading found in a
   published page (by anchor, reading the page directly), confirm
   `.professor/provenance/<page-slug>.jsonl` has **any** entry for that anchor at
   all, real or `"unknown-pre-existing"`. A section with **zero** entries — not
   created by `bootstrap` (§3 above), and never drafted or updated since — is the
   actual failure mode this check exists to catch: a page written or edited entirely
   outside this suite's own flow, after the library already existed, that neither
   `bootstrap` (a one-time pass) nor a normal scan ever saw. This is the check
   `check-page` explicitly cannot do at draft time (`page-contract.md`'s own
   "Provenance" section — no ledger entry exists yet for a not-yet-published scratch
   file); `sweep` is where it happens instead, against pages that are already
   published and therefore should already have one.

Also reconciles `scan-repo`'s `removed` entries here: a section citing a path that no
longer exists gets surfaced as part of this report (as a sixth category, "stale
citations needing a source or removal"), rather than silently left for the next
person to notice by reading the page.

Report all findings together; act on none of them without review. This mirrors
`screen-sensitive`'s `block` reporting shape deliberately — one consistent findings
format across every gate in this pack.

## Tools

Local throughout — `Glob`/`Grep`/`Read` over the target repo's own tree, and
`Read`/`Write` on `.professor/library.json` and the library's own markdown files. This
skill has no cross-repo dimension in any mode, so it never calls `tools/professor.py`.

## Summary checklist

- [ ] `bootstrap`: an existing docs convention was checked for before creating a new
      one; if found with existing pages, those were indexed (with
      `unknown-pre-existing` provenance where no sidecar exists) before treating
      `library.json` as empty
- [ ] `place`: `library.json` checked for an existing match before resolving a new
      category; the new mapping and the `index.md` entry were both written, not just
      one
- [ ] `sweep`: all five checks (duplicates, orphans, broken cross-refs, contradicting
      claims, missing provenance records) ran, plus the
      `removed`-entries reconciliation, and every finding was reported rather than
      silently fixed
