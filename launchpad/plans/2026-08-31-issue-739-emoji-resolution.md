# Plan: issue #739 — document capabilities/custom-emoji/emoji-resolution.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad` (confirmed via
  `find launchpad/docs/corpus -iname "*.md"`); this task creates the directory.
- No node currently exists at `launchpad/docs/corpus/capabilities/custom-emoji/emoji-resolution.md`.
- Sibling issue #738 (`capabilities/custom-emoji/custom-emoji.md`) is a separate, unmerged task —
  its scope is the upload/management capability (own kind:30030 set CRUD). This task's scope is
  narrower: the **resolution algorithm** — how a `:shortcode:` token becomes a rendered image,
  across the two scopes that exist in the code (community NIP-30 palette vs. the bundled
  emoji-mart "native"/unicode set) — and must not duplicate #738's content or create a second
  hand-authored node.
- `node.schema.json`'s `type` enum has no `capability`/`resolution`-specific value; `capabilities`
  (plural) is the correct enum member per PRD #602's own surface list.
- `templates/capability.md` exists and is the only template touching this surface, but it
  documents a *capability* (a named product-level thing, e.g. "Custom emoji"), not an internal
  *algorithm* sub-topic. Per `AGENTS.md`, no template exists yet for an algorithm/behavior-rule
  node at this granularity — this node is written directly against `node.schema.json` plus the
  general corpus rules in `AGENTS.md`, borrowing the capability template's *shape* (statement /
  behavior / boundary / relationships / scope-and-omissions) where it fits, since no closer
  template exists.
- Evidence gathered by reading (this session, at commit `cad6c375fdcc590158c1456c9fc7875f0f84a844`):
  - `desktop/src/shared/api/customEmoji.ts` — community palette union (per-member kind:30030,
    latest-wins by `created_at`, tie-break smallest URL).
  - `desktop/src/shared/lib/remarkCustomEmoji.ts` — timeline rendering: only shortcodes present in
    the *rendered message's own* resolved emoji map become images; unknown `:foo:` stays text.
  - `desktop/src/features/messages/lib/useMessageEmoji.ts` — the map passed to the renderer is
    built from the **message event's own NIP-30 `emoji` tags** (`customEmojiFromTags(tags)`), not a
    fresh live-community lookup at render time.
  - `desktop/src/shared/lib/customEmojiTags.ts` — at send time, `buildCustomEmojiTags` resolves
    `:shortcode:` occurrences in the outgoing body against the *current* community palette and
    bakes `["emoji", shortcode, url]` tags onto the outgoing event, making it self-contained.
  - `desktop/src/shared/api/customEmoji.ts#reactionEmojiUrl` — same resolve-then-tag pattern for
    kind:7 reactions (`buzz-sdk/src/builders.rs#build_custom_emoji_reaction`).
  - `desktop/src/shared/lib/emojiSearch.ts` / `desktop/src/shared/lib/emojiOnly.ts` — the "global"
    scope is `@emoji-mart/data`, a client-bundled unicode dataset identical across every
    community/relay, distinct from the per-community NIP-30 palette.
  - `crates/buzz-sdk/src/builders.rs#normalize_custom_emoji_shortcode` — canonical normalization
    (trim colons/whitespace, ASCII `[a-zA-Z0-9_-]` only, max 64 bytes, lowercased) enforced
    identically by the relay.
  - `crates/buzz-relay/src/handlers/ingest.rs#validate_custom_emoji_tags` /
    `#validate_reaction_emoji` — relay-side enforcement of the same shortcode contract at ingest.
  - `mobile/lib/shared/custom_emoji/custom_emoji.dart` — mirrors the desktop algorithm exactly
    (explicit doc comment: "Mirrors desktop's NIP-30 model").
- Corpus tree on `origin/launchpad` currently holds no capability-shaped or resolution-shaped
  node this could relate to; per `AGENTS.md`'s rule 9, relationship targets must resolve on the
  merge-target branch, not the author's own worktree — `custom-emoji` (id likely
  `capabilities-custom-emoji-custom-emoji`) is unmerged, so **no `relationships` entry is added**,
  matching the precedent `templates/capability.md` itself set for the same situation.

## STEP 1 — Draft the node

Create `launchpad/docs/corpus/capabilities/custom-emoji/emoji-resolution.md`:
- Front matter: `id: capabilities-custom-emoji-emoji-resolution`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer]`, `evidence: [...]`.
- Body: resolution statement, the two-scope algorithm (compose/send-time resolution against the
  live community palette → tags baked onto the event; render-time resolution reads only the
  event's own tags, never a fresh palette lookup; standard/global emoji bypass this path
  entirely and render as native unicode), behavioral rules (case-insensitivity + normalization,
  longest-shortcode-first matching, word-boundary guard, unknown-shortcode fallback to literal
  text), boundary (not upload/management — that's #738; not the picker UI), relationships (none,
  per ALREADY TRUE), scope and omissions.
- Done when: file exists, is schema-shaped, and every claim above has a citation.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root. Done when:
exit 0, and the only errors/notices present are the 21 pre-existing baseline failures already
tracked in #1951 (confirm by re-running against `origin/launchpad` if any ambiguity arises) —
zero *new* FAIL entries attributable to this node.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Done when: output ends `OK`.

## STEP 4 — Commit

`git add` the new node + this plan file; `git commit -s` with a message referencing #739. Done
when: commit created, no push, no PR.

## GATES

- `validate.py` exit 0, zero new FAIL entries beyond the tracked #1951 baseline.
- `unittest discover` on the corpus test suite prints `OK`.
- Exactly one hand-authored corpus `.md` file is added.

## BUDGET

Single session, no sub-agents needed — this is a documentation-only task with a bounded, already-
read evidence set.

## OPEN

- Whether `emoji-resolution` should later gain a `part-of` edge to `capabilities-custom-emoji-
  custom-emoji` once #738 merges — left for a future edit per AGENTS.md's own relationship rule.

## LEFT OUT

- Any change to `custom-emoji.md` (#738's file) or its scope.
- Any runtime/product code change.
- A `references` edge to architecture/interface nodes, since none exist yet in the merged corpus.
