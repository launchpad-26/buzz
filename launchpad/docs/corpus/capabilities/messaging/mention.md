---
id: capabilities-messaging-mention
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Buzz resolves an `@name` (or an inline `nostr:npub1…` URI) typed into a message, forum post or forum comment into a lowercase-hex pubkey and attaches it as a `p` tag on the signed event, capped at 50 deduplicated tags per event; a sender is never auto-tagged for mentioning themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/mentions.rs"
      - "crates/buzz-sdk/src/builders.rs:192-245"
  - statement: "`crates/buzz-sdk/src/builders.rs`'s `mention_tags` helper is shared by `build_message` (kind 9), `build_forum_post` (kind 45001) and `build_forum_comment` (kind 45003) -- the same p-tag pipeline backs a mention in a channel message, a forum post, and a forum reply."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:216-316"
  - statement: "Exceeding the 50-mention cap is a hard builder error (`SdkError::TooManyMentions`, message \"too many mentions (max 50)\"), not a silent truncation."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:103-104"
      - "crates/buzz-sdk/src/builders.rs:192-196"
  - statement: "`extract_at_mentions_with_known` resolves multi-word display names correctly (longest-known-name-first, word-boundary-checked) where the simpler `extract_at_names` would only capture the first word; both exclude email-address-shaped `user@host` text by requiring the `@` be preceded by whitespace or start-of-string."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/mentions.rs:53-158"
  - statement: "`extract_nostr_uris` additionally recognizes inline NIP-27 `nostr:npub1…` references as explicit mentions, skipping any that fall inside fenced or inline code (via `strip_code_regions`), and `merge_mentions` deduplicates these against name-resolved pubkeys before the cap is applied."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/mentions.rs:203-220"
      - "crates/buzz-sdk/src/mentions.rs:341-387"
  - statement: "Desktop's `shouldNotifyForEvent` checks whether the current user is `p`-tagged on an event (`hasMentionForEvent`) before it checks channel mute state, root mute state, thread participation, follow state or authorship -- a mention notifies even in a muted channel, and `isHighPriorityEventForUser` marks a mention (or a broadcast reply) as high priority on the same basis."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/lib/shouldNotify.ts"
  - statement: "The desktop message composer resolves `@` mentions through `useMentions`, which ranks candidates drawn from channel members, relay/managed agents, active personas, agent teams and (once the query is non-empty and agent directories are loaded) a global user search, then inserts the selected suggestion as `@DisplayName ` text and records the display-name-to-pubkey mapping used later to extract p-tag pubkeys from the composed text."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/useMentions.ts"
  - statement: "`extractMentionPubkeys` resolves ambiguity between a manually typed mention and a channel member whose name is a prefix of another matched name by keeping only the longest matching display name at each `@` offset in the composed text."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/extractMentionPubkeys.ts"
  - statement: "A mention target can be a `team` -- a saved group of agent personas -- in which case selecting it inserts `TeamName(@member1 @member2 …)` rather than a single `@name`, expanding one autocomplete selection into one explicit mention per resolved team member."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/mentionCandidates.ts:113-155"
  - statement: "`MentionAutocomplete`'s suggestion list surfaces a truncated npub next to the display name whenever two suggestions share the same name, because a vanity-ground key can wear any display name and the name alone is not a reliable way to tell two identities apart."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/MentionAutocomplete.tsx:67-74"
  - statement: "`getMentionOffsets` (used both to detect an already-typed mention for highlighting and to resolve pubkeys from composed text) matches `@Name` bounded by start-of-string, whitespace, an opening parenthesis, Markdown bold/italic delimiters or spoiler `||` markers, after masking fenced/indented/inline Markdown code so a mention-shaped string inside a code block is not matched."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/hasMention.ts"
  - statement: "On the relay, a `p` tag is one of the generic tags indexed for REQ filter matching; `crates/buzz-relay/src/subscription.rs`'s `event_p_tag_values` collects an event's deduplicated `p` values for exactly this indexing path, which is what lets a client subscribe with a `#p` filter on its own pubkey and receive events that mention it, including a mobile installation's push-wake matching in `push_runtime.rs::match_job`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:670-713"
      - "crates/buzz-relay/src/push_runtime.rs:220-287"
  - statement: "A mobile push-notification lease can configure `suppress.p_tags_max`, and `push_runtime.rs::match_job` skips waking that lease for any event whose `p`-tag count exceeds it -- a client-side opt-in cap against being woken by a message that mentions a very large group, validated server-side (`p_tags_max` must be positive) at lease-registration time."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs:252-266"
      - "crates/buzz-relay/src/handlers/push_lease.rs:56"
      - "crates/buzz-relay/src/handlers/push_lease.rs:257-258"
  - statement: "The relay's default agent-runtime subscription includes stream-message kind 9 specifically described as carrying '@mentions', and `buzz-acp`'s own five-step lifecycle description states it 'queue[s] inbound @-mention events per channel' and drains them into a single batched ACP `session/prompt` call -- an inbound mention is buzz-acp's primary trigger for starting or continuing an agent turn, not merely a notification to a human."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md"
  - statement: "VISION_PROJECTS.md's own capability status table has no dedicated row for mentions; the closest row is 'Channels, forums, DMs, canvases | ✅ Ships today', so mention maturity is established here from the shipped code and its test suite directly rather than from that table's row-level granularity."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-251"
  - statement: "VISION.md's own description of the Home Feed names '@mentions' as one of its assembled inputs alongside items needing action, channel activity and agent updates, corroborating that a mention is surfaced to the mentioned user through the Home Feed rather than only inline in the channel it was sent to."
    entry_class: FACT
    evidence:
      - "VISION.md:133"
  - statement: "The mobile app's own package/feature listing in the merged `architecture-containers-agent-runtime` sibling architecture work names `mentions` as one of its Dart package dependencies, which is the only mobile-side evidence opened for this node; the mobile mention UI and highlight/notification behavior in `mobile/lib` were not read."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md:128"
---

# @-mention: capability

A user (or an AI agent) writes `@name` in a channel message, a forum post, or a forum
comment, and Buzz resolves that name -- against channel membership, known agents and
teams, and, once the query is non-empty, a global user search -- to a Nostr pubkey,
attaching it as a `p` tag on the event the sender signs. The mentioned party is
guaranteed to be notified: a mention overrides channel and thread mute state and is
surfaced through the Home Feed, regardless of whether the recipient participates in,
follows, or authored the thread the mention appears in. The same mechanism also
addresses an AI agent (an inbound `@mention` is `buzz-acp`'s trigger for starting or
continuing an agent turn) and a saved "team" of agent personas, which expands one
selection into one explicit mention per resolved team member.

## Maturity

**Shipped.** `crates/buzz-sdk/src/mentions.rs` and `crates/buzz-sdk/src/builders.rs`
implement name and NIP-27 URI extraction, profile matching, deduplication, the 50-tag
cap, and p-tag emission for kind 9, 45001 and 45003 events, each covered by unit tests
in the same files. The desktop composer's mention autocomplete, highlighting and
pubkey-extraction pipeline (`desktop/src/features/messages/lib/useMentions.ts`,
`hasMention.ts`, `extractMentionPubkeys.ts`, `mentionCandidates.ts`, and the
`MentionAutocomplete` component) is likewise merged code with its own test files.
VISION_PROJECTS.md's capability status table has no row naming "mentions" specifically
-- the closest is "Channels, forums, DMs, canvases | ✅ Ships today" -- so this
maturity claim rests on the code and its tests directly rather than on that table's
coarser granularity.

## Boundary

This node does not describe:
- **How `buzz-acp` is built or deployed** -- the container that bridges relay
  `@mention` events to an AI agent subprocess over ACP. See
  `architecture-containers-agent-runtime`, `architecture-context-ai-agent` and
  `architecture-context-buzz-platform` for that architecture.
- **The step-by-step flow an inbound `@mention` triggers inside `buzz-acp`** --
  queueing, batching into one ACP `session/prompt` call, and replay-on-restart. See
  `architecture-flows-agent-turn`.
- **The interface contract a mention is exposed through** -- no interface-shaped
  corpus node exists yet for `buzz-cli`'s message subcommands or the relay's REST
  surface; this is a gap, not a decision to omit it.
- **How the relay's push infrastructure is operated or scaled.** `push_runtime.rs`'s
  `p_tags_max` suppression is described here only as a behavioral variant of the
  mention capability (a receiver-side opt-out from being woken by a mass mention), not
  as an operations topic.
- **Mobile (Flutter) mention UX in detail.** Only one dependency-listing citation
  (`mentions` among the mobile app's Dart packages) was opened for this node; see
  *Scope and omissions* below.

## Relationships

- references: architecture-flows-agent-turn
- references: architecture-context-ai-agent
- references: architecture-containers-agent-runtime
- references: architecture-context-buzz-platform

## Scope and omissions

**This node covers** how a Buzz `@-mention` is produced (name/URI extraction, profile
resolution, deduplication, the 50-tag cap, p-tag emission shared across message/forum
post/forum comment builders), how it is consumed for notification purposes (mute-state
override, high-priority classification, Home Feed inclusion, relay-side `#p` filter
indexing and mobile push-wake matching with its `p_tags_max` suppression variant), and
the desktop composer's autocomplete/highlight/extraction UI that produces and displays
mentions, including the team-mention expansion variant.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How `buzz-acp` is built (containers, components) | `architecture-containers-agent-runtime`, `architecture-context-ai-agent` |
| The step-by-step path an inbound mention takes through an agent turn | `architecture-flows-agent-turn` |
| The CLI/HTTP interface surface a mention is created or read through | not yet a corpus node |
| Operating or scaling the relay's push infrastructure | the `operations` corpus surface |
| Mobile (Flutter) mention UI and notification behavior in detail | not yet a corpus node; `mobile/lib` was not read for this node |

**Expected but not verified when this node was written:**
- **Mobile mention handling was not inspected beyond one dependency listing.** Whether
  the Flutter app applies the same mute-override/high-priority notification rule as
  desktop's `shouldNotifyForEvent` was not checked against `mobile/lib` source.
- **Whether the relay enforces any server-side cap on `p`-tag count at ingest time**
  (as opposed to the client-side 50-tag cap in `buzz-sdk`, and the receiver-side
  `p_tags_max` push-wake suppression) was searched for and not found in
  `crates/buzz-relay/src/handlers/ingest.rs`; its absence here is a search result, not
  a confirmed guarantee that no such limit exists elsewhere in the relay.
- **The accessibility of `MentionAutocomplete`'s suggestion popup** (keyboard
  navigation beyond Arrow/Tab/Enter/Escape handling already read in `useMentions.ts`,
  ARIA roles for the suggestion list) was not audited as part of this capability-level
  node.
