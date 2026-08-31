# Issue #738: document capabilities/custom-emoji/custom-emoji.md

Parent: PRD #613. Repo: launchpad-26/buzz. Base: origin/launchpad @
cad6c375fdcc590158c1456c9fc7875f0f84a844.

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet — this is the
  first capability-shaped instance node in the corpus.
- `launchpad/docs/corpus/templates/capability.md` (`corpus-template-capability`,
  merged) defines the required shape: Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions.
- Sibling issue #739 (`capabilities/custom-emoji/emoji-resolution.md`) owns the
  union/precedence *algorithm*; not opened for content, only its title/DoD read
  to confirm the boundary. It is an unmerged sibling, so it cannot be a
  `relationships` target regardless.
- No other capability node exists in `origin/launchpad`'s corpus tree, so this
  node also declares no `references`/`part-of` edges to sibling capability
  nodes (all authored in parallel with this one).
- Code confirms the capability is **shipped**, not "planned" — this contradicts
  `VISION.md`'s own "Culture Features" table, which lists "Custom emoji" as
  "(Planned design — not yet implemented)". Per ADR-0029, executable evidence
  (code + tests) outranks documentation for current-behavior claims, so the
  node's Maturity section states "shipped" from code/tests and notes the stale
  VISION.md marker as a scope-and-omissions gap, not a silent override.

## STEP 1 — Evidence gathering (done during planning)

Inspected, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844:
- `crates/buzz-core/src/kind.rs:44-52` — `KIND_EMOJI_SET = 30030` (NIP-30/51,
  parameterized-replaceable, user-owned per pubkey+d-tag).
- `crates/buzz-relay/src/handlers/ingest.rs:145-192,455-469` — scope
  (`Scope::UsersWrite`), shortcode tag validation, reaction-emoji validation.
- `crates/buzz-sdk/src/builders.rs:123-155` — shortcode normalization rules
  (ASCII alnum/-/_, ≤64 bytes, case-folded).
- `desktop/src/shared/api/customEmoji.ts` — client union/read-modify-write
  logic, `KIND_EMOJI_SET`, `CUSTOM_EMOJI_SET_D_TAG`.
- `desktop/src/features/custom-emoji/ui/CustomEmojiSettingsCard.tsx` — upload +
  management UI ("My emoji" vs read-only "Community emoji").
- `desktop/src/shared/lib/remarkCustomEmoji.ts`,
  `desktop/src/features/messages/lib/customEmojiNode.ts` — rendering in
  timeline (react-markdown) and composer (tiptap inline atom node).
- `crates/buzz-cli/src/lib.rs:145-151,767-807`,
  `crates/buzz-cli/src/commands/emoji.rs` — `buzz emoji {list,set,rm,export,
  import}` CLI surface.
- `desktop/tests/e2e/custom-emoji.spec.ts`,
  `desktop/tests/e2e/custom-emoji-ui.spec.ts`,
  `desktop/tests/e2e/profile-custom-emoji-status.spec.ts` — E2E verification
  (composer atom node, timeline rendering, profile-status use).
- `VISION.md:187` — stale "planned" marker, noted as a conflict.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/custom-emoji/custom-emoji.md`
against `node.schema.json` and `templates/capability.md`'s required sections:
Capability statement, Maturity (FACT, code+tests), Boundary (excludes
resolution algorithm → #739, architecture/container docs, interface docs,
flow docs, operations), Relationships (none — no merged sibling to point at),
Scope and omissions.

Front matter: `id: capabilities-custom-emoji-custom-emoji`, `type:
capabilities`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`, evidence ledger with one commit-pinned provenance
entry plus one FACT/INFERENCE/TEAM_KNOWLEDGE entry per substantive claim.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Confirm zero new FAIL entries beyond the 21 pre-existing ones tracked in
issue #1951.

## STEP 4 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK` before staging/committing anything.

## GATES

- `validate.py` exit 0, zero new FAILs.
- `unittest discover` prints `OK`.
- Every DoD bullet in issue #738 satisfied line by line (self-review, step 6
  of the outer process).

## BUDGET

5 steps max (this plan uses 4). No second hand-authored corpus document.

## OPEN

- Whether `type: capabilities` nodes conventionally get a `references` edge to
  the interface/architecture docs that expose/build them — not yet, because
  none of those sibling nodes are merged to `origin/launchpad` at this
  revision. Left for a later pass once they land.

## LEFT OUT

- The emoji-resolution/union/precedence algorithm itself (#739's scope).
- Any runtime behavior change — this is documentation only.
- Reconciling `VISION.md`'s stale "planned" marker — noted as a gap in Scope
  and omissions, not silently corrected (out of scope per issue's own "Out of
  scope" list: no broad while-here cleanup).
