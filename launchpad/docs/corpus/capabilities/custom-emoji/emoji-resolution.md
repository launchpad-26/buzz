---
id: capabilities-custom-emoji-emoji-resolution
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Two independent shortcode-resolution scopes exist in Buzz: a per-community NIP-30 custom-emoji palette (client-side union of every member's own kind:30030 set) and a client-bundled global/native unicode set (@emoji-mart/data) that is identical across every community and never resolved from relay events."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
      - "desktop/src/shared/lib/emojiOnly.ts"
  - statement: "The community custom-emoji palette is computed by unioning every member's own kind:30030 event under d-tag `buzz:custom-emoji`, collapsing to one entry per shortcode; when two members' sets disagree on a shortcode's URL, the most recently published set (by `created_at`) wins, and equal timestamps tie-break to the lexicographically-smallest URL, making the union deterministic and fetch-order-independent."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
  - statement: "At compose/send time (messages) and react time (kind:7 reactions), the client resolves a `:shortcode:` against the current live community palette and bakes the resolved `[\"emoji\", shortcode, url]` tag directly onto the outgoing event, so the event is self-contained for any NIP-30 client to render without a further lookup."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/customEmojiTags.ts"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "At render time, the shortcode-to-URL map used to turn `:shortcode:` text into an inline image is derived only from the message (or reaction) event's own NIP-30 `emoji` tags via `customEmojiFromTags`, not from a fresh live-community-palette lookup — a message keeps rendering the shortcode/URL pairing it was sent with even if the community palette later changes."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMessageEmoji.ts"
      - "desktop/src/shared/api/customEmoji.ts"
  - statement: "Because render-time resolution reads only the event's own tags rather than re-querying the live palette, an already-received message continues displaying the image URL it was tagged with at send time even if the emoji's owner later republishes a different URL under the same shortcode — a consequence of the self-contained-event design the source comments describe, not a behavior asserted directly by any single line of code."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/shared/lib/customEmojiTags.ts"
      - "desktop/src/features/messages/lib/useMessageEmoji.ts"
    confidence: 0.75
  - statement: "Shortcode normalization is one contract enforced on both sides: trim surrounding colons and whitespace, require the result to be non-empty ASCII letters/digits/hyphen/underscore only, cap length at 64 bytes, and lowercase the result. The desktop client implements this in `normalizeShortcode` and the relay enforces the equivalent rule authoritatively via `buzz_sdk::normalize_custom_emoji_shortcode` at ingest, so a client-side pass cannot substitute for relay acceptance."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A NIP-25 reaction whose content is a colon-wrapped custom-emoji shortcode longer than 64 unicode chars total is rejected by the relay unless its content is exactly a canonical-lowercase `:shortcode:` matching one of the event's own `[\"emoji\", shortcode, url]` tags and the total length does not exceed `MAX_CUSTOM_EMOJI_REACTION_LEN` (66)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "Matching `:shortcode:` occurrences in message text is case-insensitive and longest-known-shortcode-first (so a longer shortcode is never shadowed by a shorter one that is a prefix of it), resolves to the canonical lowercase palette entry, and only fires for shortcodes already present in the resolved set — an unrecognized `:foo:` sequence is left as literal text rather than becoming a broken image."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/remarkCustomEmoji.ts"
  - statement: "The composer's live-typing input rule additionally applies a word-boundary guard: a `:shortcode:` immediately preceded by a word character (letter, digit, or underscore) does not resolve into an emoji, so occurrences glued inside another word or inside a URL like `http://x:y:buzz:` stay plain text."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/customEmojiNode.ts"
  - statement: "The global/native emoji scope is a client-bundled emoji-mart unicode dataset (package `@emoji-mart/data`), built once into an in-memory index and used both for autocomplete/search and for detecting whether a grapheme cluster is a recognized native emoji; this dataset ships with the client and is identical for every community, in contrast to the per-community NIP-30 palette which is fetched from relay events."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/emojiOnly.ts"
      - "desktop/src/shared/lib/emojiSearch.ts"
  - statement: "The mobile (Flutter) client implements the identical resolution algorithm to desktop: the same shortcode normalization regex, the same NIP-30 tag parsing, the same per-shortcode union/tie-break rule for the community palette, and the same per-event (not live-palette) resolution when rendering a message or reaction — its own source comment states it mirrors desktop's model."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/custom_emoji/custom_emoji.dart"
  - statement: "This node's scope is deliberately narrower than sibling issue #738's `capabilities/custom-emoji/custom-emoji.md`: #738 covers the upload/management capability (publishing, editing and removing a member's own kind:30030 set), while this node covers only the resolution algorithm — how an already-known or already-tagged `:shortcode:` becomes a rendered image across the community and global scopes — per the batch dispatch instruction for issue #739."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#739 task description (batch dispatch note distinguishing #739 from sibling #738)"
  - statement: "The resolution algorithm's core client-side behaviors are covered by unit tests: a known shortcode becoming an emoji node with the correct `src`/`alt` and an unknown shortcode staying plain text (`remarkCustomEmoji.test.mjs`), and a message's `customEmoji`/`emojiOnly` derivation from its own event tags (`useMessageEmoji.test.mjs`). The relay's normalization and reaction-length enforcement are covered by ingest handler unit tests, including one asserting a mixed-case long shortcode is rejected and one asserting a case-mismatched `emoji` tag is rejected."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/remarkCustomEmoji.test.mjs"
      - "desktop/src/features/messages/lib/useMessageEmoji.test.mjs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
---

# Emoji resolution: capability

Buzz lets a user or agent type, paste, or select a `:shortcode:` — in a channel message, a
thread reply, or a reaction — and see it rendered as an image or a native unicode glyph
consistently for every other member of the community, regardless of which client (desktop
or mobile) they use. This resolution happens across two independent scopes: a **community**
scope (custom emoji published by community members, resolved from NIP-30 `kind:30030` sets)
and a **global** scope (a fixed, client-bundled unicode emoji dataset that needs no relay
round-trip and is identical for every community). This node documents how a shortcode crosses
from typed text to a rendered image in each scope, not how a member manages their own custom
set (see *Boundary*).

## How resolution works

**Community scope (custom emoji).**

1. Each member publishes their own emoji as one signed, parameterized-replaceable `kind:30030`
   event under `d`-tag `buzz:custom-emoji`, carrying one `["emoji", shortcode, url]` tag per
   shortcode they own.
2. Every client computes the **community palette** as the client-side union of every member's
   latest `kind:30030` set, collapsed to one URL per shortcode. When two members disagree on a
   shortcode, the most recently published set wins; equal `created_at` values tie-break to the
   lexicographically smallest URL, so the same set of relay events always yields the same
   palette regardless of fetch order.
3. **At compose or react time**, the client resolves each `:shortcode:` the user types (or
   selects from the picker) against the *current* community palette and bakes the resolved
   `["emoji", shortcode, url]` tag directly onto the outgoing message or reaction event before it
   is signed and published. The event is therefore self-contained: any NIP-30-aware client can
   render it correctly without knowing the community palette at all.
4. **At render time**, the client does not re-resolve against the live community palette. It
   reads the shortcode-to-URL map directly off the event's own `emoji` tags and uses that to turn
   `:shortcode:` occurrences in the body into inline images. This means a message keeps rendering
   the image it was tagged with at send time even if the palette changes afterward (see the
   `INFERENCE` entry in the evidence ledger).
5. A shortcode that is not already known — not present in the community palette at compose time,
   or not carried in an incoming event's own tags — is never invented at render time; it is left
   as the literal `:shortcode:` text.

**Global scope (standard/unicode emoji).** A separate, client-bundled dataset
(`@emoji-mart/data`) supplies the picker's standard categories, autocomplete search, and the
"emoji-only" large-render detection. This scope needs no relay lookup, is identical for every
community and every member, and never intersects with the community palette's shortcode
namespace at the data level — a native unicode glyph the user selects is inserted directly as
text, never turned into a custom-emoji tag.

## Behavioral rules and constraints

- **Normalization is one contract, enforced twice.** A shortcode is trimmed of surrounding
  colons/whitespace, must be non-empty ASCII letters/digits/hyphen/underscore only, capped at 64
  bytes, and lowercased. The client applies this locally for immediate feedback; the relay
  enforces the identical rule authoritatively at ingest, so a client-side pass is never a
  substitute for what the relay will accept.
- **Reaction payload cap.** A `kind:7` reaction whose content is a colon-wrapped custom-emoji
  shortcode is capped at 66 characters total (64-byte shortcode + 2 colons) and must exactly
  match a canonical-lowercase shortcode carried in the event's own `emoji` tag — the relay rejects
  anything longer or mismatched.
- **Case-insensitive matching, canonical-lowercase resolution.** `:Party_Parrot:` and
  `:party_parrot:` both resolve to the same palette entry; the canonical form stored and re-sent
  is always lowercase.
- **Longest-shortcode-first matching.** When one known shortcode is a prefix of another, the
  longer one wins, so a shorter shortcode can never shadow a longer one that contains it.
  Matching only fires for shortcodes already known to the current palette or event.
  Unrecognized `:foo:` sequences render as plain text, never as a broken image.
- **Word-boundary guard (composer only).** A `:shortcode:` immediately glued to a preceding word
  character does not resolve while typing, so a shortcode embedded inside another word or a URL
  is left alone.
- **Platform parity.** Desktop and mobile implement the same normalization, tag-parsing,
  union/tie-break, and per-event render-time resolution rules; mobile's implementation
  explicitly documents itself as mirroring desktop's.

## Verification

This algorithm is exercised by unit tests rather than only described here:
- `desktop/src/shared/lib/remarkCustomEmoji.test.mjs` — known shortcode → emoji node with
  correct `src`/`alt`; unknown shortcode stays plain text.
- `desktop/src/features/messages/lib/useMessageEmoji.test.mjs` — a message's `customEmoji`/
  `emojiOnly` derivation from its own event tags.
- `crates/buzz-relay/src/handlers/ingest.rs` (`reaction_validation_accepts_wrapped_max_shortcode`,
  `reaction_validation_rejects_mixed_case_max_shortcode`,
  `reaction_validation_rejects_case_mismatched_tag`,
  `emoji_set_validation_enforces_shortcode_boundary`) — relay-side normalization and
  reaction-length enforcement.

## Boundary

This node does not describe:
- **Uploading, editing, or removing a member's own custom emoji set** — that is sibling issue
  `#738`'s capability node (`capabilities/custom-emoji/custom-emoji.md`), covering the
  read-modify-write publish flow against the member's own `kind:30030` event.
- **The emoji picker UI** (search ranking beyond the shortcode-matching rules stated above,
  category layout, or the "emoji burst" reaction animation) as its own subject matter.
- **How the running system operates** the relay or storage backing these events — that is the
  `operations` corpus surface, not this capability.
- **The step-by-step path** a single message-send or reaction interaction takes end to end — a
  flow-shaped node, not yet drafted in this corpus (see `AGENTS.md`'s own noted gap for the
  `flow` node type).

## Relationships

None declared. The natural targets — a `capabilities-custom-emoji-custom-emoji` node (sibling
issue `#738`) and any architecture/interface node for the relay's NIP-30 handling — do not yet
exist in the corpus tree merged to `origin/launchpad` at the time this node was authored, and
`AGENTS.md`'s rule for creating a node requires every relationship target to resolve against the
merge-target branch, not the author's own worktree. Adding `part-of` (toward `custom-emoji`) or
`references` (toward a future relay/NIP-30 architecture node) is the right next edit once those
nodes merge.

## Scope and omissions

**This node covers** the resolution algorithm for a NIP-30 custom-emoji `:shortcode:` and for a
standard/global unicode emoji: the two independent scopes, the resolve-at-send-time /
read-from-event-at-render-time split for the community scope, the normalization contract shared
by client and relay, the reaction-length constraint, the matching rules (case-insensitivity,
longest-first, word-boundary guard, unknown-shortcode fallback), and the unit tests that
demonstrate these behaviors.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Publishing, editing, or removing a member's own custom emoji set | `#738` (`capabilities/custom-emoji/custom-emoji.md`) |
| The picker UI, search ranking beyond shortcode matching, and reaction-burst animation | not yet a corpus node |
| The relay's NIP-30 ingest/storage architecture as its own subject | not yet a corpus node (architecture family) |
| The step-by-step flow of one send/react interaction | not yet a corpus node (`flow` type, per `AGENTS.md`'s noted gap) |

**Expected but not verified when this node was written:**
- **The web client** (`web/`) was not inspected for an equivalent implementation; this node's
  claims are backed by desktop, mobile, and the relay/SDK only.
- **Live behavior against a running relay** was not exercised — every claim above is backed by
  reading source, not by observing a resolved message end to end in a live community.
