---
id: capabilities-custom-emoji-custom-emoji
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Custom emoji is a NIP-30/NIP-51 parameterized-replaceable kind:30030 event, published per member and keyed by (pubkey, kind, d-tag = buzz:custom-emoji), rather than a single relay-owned emoji set."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "desktop/src/shared/api/customEmoji.ts"
  - statement: "The relay requires UsersWrite scope for kind:30030 (and the related kind:10030 emoji list), the same ownership class as other NIP-51 user-owned lists, rather than requiring channel-scoped write access."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The relay validates every `emoji` tag's shortcode through buzz_sdk::normalize_custom_emoji_shortcode, which requires ASCII letters, digits, hyphen or underscore, a maximum of 64 bytes, and folds the result to lowercase; ingestion rejects an event whose emoji tag fails this check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The relay separately validates a reaction event's own emoji payload against the same shortcode rule whenever its content exceeds 64 Unicode characters, and requires a matching `emoji` tag naming that same canonical lowercase shortcode."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The desktop client never persists a merged workspace palette: unionCustomEmoji computes it on read from every member's fetched kind:30030 event, with the most recently published set winning a shortcode collision and a lexicographic tie-break on equal timestamps so the same input events always yield the same palette."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
  - statement: "Adding or removing a custom emoji is a read-modify-write of the caller's own kind:30030 set only: setCustomEmoji and removeCustomEmoji fetch the caller's current set, mutate it, and republish the whole set signed as the caller, so a member can never remove or overwrite another member's emoji."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
  - statement: "The desktop Settings 'Custom emoji' card uploads an image through the existing media-upload flow, suggests a shortcode from the uploaded filename, and separates the caller's own editable 'My emoji' list from a read-only 'Community emoji' list of emoji owned by other members."
    entry_class: FACT
    evidence:
      - "desktop/src/features/custom-emoji/ui/CustomEmojiSettingsCard.tsx"
  - statement: "Custom emoji render inline in the message timeline through a remark plugin that matches only shortcodes present in the resolved set (case-insensitively, longest-match-first) and leaves any unmatched `:foo:` sequence as plain text, and separately as a selectable, deletable inline atom node in the composer via a matching Tiptap extension that still serializes back to `:shortcode:` on send."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/lib/remarkCustomEmoji.ts"
      - "desktop/src/features/messages/lib/customEmojiNode.ts"
  - statement: "Custom emoji also resolve as reaction images and as a user's status glyph, both consuming the same shortcode-to-URL resolution the picker and message renderer share; StatusEmoji's own comment states this resolution is unified across five display sites specifically so they cannot drift apart."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/customEmoji.ts"
      - "desktop/src/features/user-status/ui/StatusEmoji.tsx"
  - statement: "buzz-cli exposes the capability as a `buzz emoji` subcommand group (list, set, rm, export, import), where `list` reads the union of every member's set and `set`/`rm` read-modify-write only the caller's own set, mirroring the desktop client's own read-modify-write shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/src/commands/emoji.rs"
  - statement: "The capability is shipped, not merely designed: a dedicated event kind, relay-side ingest validation, a desktop management UI, timeline/composer/reaction/status rendering, and a CLI surface all exist in the current tree, alongside three Playwright end-to-end specs exercising the composer atom node, timeline rendering, and profile-status rendering."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "desktop/tests/e2e/custom-emoji.spec.ts"
      - "desktop/tests/e2e/custom-emoji-ui.spec.ts"
      - "desktop/tests/e2e/profile-custom-emoji-status.spec.ts"
  - statement: "VISION.md's own 'Culture Features' table separately lists 'Custom emoji — Tribal identity' under a section heading marked '(Planned design — not yet implemented)', which conflicts with the shipped state the code and test evidence above establishes."
    entry_class: FACT
    evidence:
      - "VISION.md"
  - statement: "This node treats the code and end-to-end test evidence as authoritative over VISION.md's stale marker for the capability's current maturity, per ADR-0029's rule that executable evidence outranks documentation for how a system currently behaves; VISION.md's culture-features table reads as not having been updated after the capability shipped, rather than as a considered decision to keep it unshipped."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "VISION.md"
    confidence: 0.8
  - statement: "No corpus node under type: capabilities, architecture, interfaces-events, or layers existed in origin/launchpad's corpus tree at the recorded revision, so this node declares no relationships to an architecture, interface, or flow node for custom emoji — none exist yet to point at."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/custom-emoji/custom-emoji.md"
---

# Custom emoji: capability

Buzz lets any community member publish their own custom emoji images — small,
named pictures usable anywhere a native Unicode emoji could go. Once
published, a custom emoji is available to the whole community (not just its
owner) by typing `:shortcode:` in a message, a reaction, or a status, and it
renders inline as an image everywhere the resolved shortcode is recognized:
the message timeline, the composer, reaction picker/display, and a member's
profile status. This is what VISION.md's Culture Features table calls "Custom
emoji — Tribal identity": a community-owned visual vocabulary layered on top
of standard emoji, not a per-channel or admin-curated asset.

## Maturity

**Shipped.** The capability has a dedicated Nostr event kind (`KIND_EMOJI_SET
= 30030`, NIP-30/NIP-51 parameterized-replaceable), relay-side ingest
validation of both the emoji-set tags and reaction payloads that reference a
shortcode, a desktop Settings management UI, rendering in four consuming
surfaces (message timeline, composer, reactions, user status), and a `buzz
emoji` CLI subcommand group with list/set/rm/export/import. Three Playwright
end-to-end specs exercise composer, timeline, and profile-status rendering.

This contradicts `VISION.md`'s own "Culture Features" table, which still
marks "Custom emoji" under a section headed "(Planned design — not yet
implemented)". Per ADR-0029, executable evidence (code, ingest validation,
end-to-end specs) outranks documentation for how the system *currently*
behaves, so this node's maturity claim rests on that evidence rather than on
the stale VISION.md marker. See *Scope and omissions* — reconciling
VISION.md's own table is out of this task's scope, not silently corrected
here.

## Boundary

This node does not describe:
- **The workspace-palette resolution algorithm** — how the client unions
  every member's own kind:30030 set into one palette, the recency/tie-break
  rule for a colliding shortcode, and how a shortcode resolves to an image at
  render time in detail. That is sibling task #739's node
  (`capabilities/custom-emoji/emoji-resolution.md`), not yet drafted at this
  revision and therefore not a valid `relationships` target here (see
  *Relationships*). This node states only enough of the union behavior
  (recency-wins, deterministic tie-break) to support its own capability and
  maturity claims, and defers the algorithm's full contract to that node.
- **How the relay, desktop, and CLI are built** — the containers, components,
  and Blossom media-upload path a custom emoji image travels through. That is
  architecture-family territory (component/container/context nodes for the
  relay, desktop, and media subsystems), none of which exist yet in this
  corpus.
- **The interface contract** a member interacts with — the `buzz emoji`
  CLI's exact flags and exit codes, or the relay's raw event/tag shapes. That
  belongs to an interface-family node, not yet drafted.
- **The step-by-step flow** of one interaction (e.g., uploading an image,
  naming a shortcode, and republishing a set). That belongs to a flow-family
  node, not yet drafted.
- **How the running system is operated** — relay deployment, monitoring, or
  incident response for the media store backing emoji images. That is the
  `operations` corpus surface, unrelated to this capability's product-level
  description.

## Relationships

None declared. Checked against `origin/launchpad`'s corpus tree at the
recorded revision: no `capabilities`, `architecture`, `interfaces-events`, or
other node type documenting custom emoji, its resolution algorithm, the
relay/desktop architecture, or a CLI interface exists there yet — this is the
first capability-shaped node in the corpus. `#739` (emoji-resolution) is this
node's obvious future `references` target once merged, but it is an unmerged
sibling authored in parallel with no ordering guarantee, so declaring an edge
to it now would resolve in this worktree and fail in CI on `origin/launchpad`.
The first later node (whichever of #739 or a future architecture/interface
node merges first) is the natural moment to add the edge.

## Scope and omissions

**This node covers** what the custom-emoji capability is, who can use it and
how (any member publishes their own set; the community palette is the
client-computed union), its current maturity with evidence, the relay-side
validation rules that bound it (shortcode charset/length, per-tag and
per-reaction validation, UsersWrite scope), and the four surfaces that
consume the resolved shortcode-to-image mapping (message timeline, composer,
reactions, user status).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The union/precedence resolution algorithm in full | `#739` (emoji-resolution, sibling task, not yet drafted) |
| How the relay/desktop/media subsystems are built | architecture-family nodes, not yet drafted |
| The CLI/event interface contract in full | an interface-family node, not yet drafted |
| The step-by-step flow through upload → publish → render | a flow-family node, not yet drafted |
| How the running system is operated | the `operations` corpus surface |
| Reconciling VISION.md's stale "planned" marker against the shipped code | not this task's scope (no broad while-here cleanup per issue #738's own "Out of scope") |

**Expected but not verified when this node was written:**
- **The three cited Playwright specs were read for what they assert, not
  executed at this revision.** Their existence and assertions are cited as
  designed verification of the capability, not as a confirmed passing CI run.
- **`buzz-sdk`'s reaction-event builder and `CustomEmoji` struct were not read
  beyond the shortcode-normalization helpers** (`normalize_custom_emoji_shortcode`,
  `MAX_CUSTOM_EMOJI_SHORTCODE_LEN`, `MAX_CUSTOM_EMOJI_REACTION_LEN`) cited
  above; the full reaction-builder implementation was not inspected.
- **Whether any other client (mobile, a third-party Nostr client) reads or
  writes kind:30030 against a Buzz community was not checked.** This node
  describes the desktop and CLI surfaces actually inspected.
