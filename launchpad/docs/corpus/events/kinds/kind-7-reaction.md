---
id: events-kinds-kind-7-reaction
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
relationships:
  - type: implements
    target: corpus-template-event-kind
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "crates/buzz-core/src/kind.rs defines `pub const KIND_REACTION: u32 = 7;` with the doc comment 'NIP-25: Content is emoji char or `+`/`-`.', and KIND_REACTION is a member of the ALL_KINDS registry array."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:57-58"
      - "crates/buzz-core/src/kind.rs:649"
  - statement: "NIP-25 states 'There MUST be always an `e` tag set to the `id` of the event that is being reacted to' and 'There SHOULD be a `p` tag set to the `pubkey` of the event being reacted to'; it also states a reaction MAY include a `k` tag with the stringified kind number of the reacted event, and that when multiple `e`/`p` tags are present the target event id / pubkey should be the last of its kind."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/25.md"
  - statement: "NIP-25 states 'A reaction with `content` set to `+` or an empty string MUST be interpreted as a \"like\" or \"upvote\"' and 'A reaction with `content` set to `-` MUST be interpreted as a \"dislike\" or \"downvote\"', with other content values (including a NIP-30 `:shortcode:` custom emoji reference) following separate conventions."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/25.md"
  - statement: "kind.rs's is_replaceable (matches kind against 0 | 3 | 41 | 10000..=19999), is_parameterized_replaceable (30000-39999) and is_ephemeral (20000-29999) helpers each evaluate false for kind 7, so Buzz's own classification helpers treat kind 7 as a plain regular (persistent, non-replaceable, non-ephemeral) event, consistent with NIP-01's own regular-kind range (1000<=n<10000 || 4<=n<45 || n==1 || n==2, which 7 satisfies)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:769-778"
      - "crates/buzz-core/src/kind.rs:783-785"
  - statement: "KIND_REACTION is absent from all four of kind.rs's named read-gate sets: AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS and SHARED_GATED_KINDS, so a stored kind:7 event carries no special per-kind read restriction beyond ordinary channel membership."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:159-169"
      - "crates/buzz-core/src/kind.rs:215"
  - statement: "required_scope_for_kind in the relay's ingest handler maps KIND_REACTION (grouped with KIND_DELETION, KIND_GIFT_WRAP and the stream/forum message kinds) to Scope::MessagesWrite, so submitting a reaction requires the same write scope as an ordinary message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:470-484"
  - statement: "requires_h_channel_scope, the function that lists kinds requiring a client-supplied `h` tag for channel scoping, does not include KIND_REACTION; this is confirmed by a dedicated unit test, reactions_do_not_require_h_tag, which asserts `!requires_h_channel_scope(KIND_REACTION)`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:704-733"
      - "crates/buzz-relay/src/handlers/ingest.rs:3705-3708"
  - statement: "derive_reaction_channel derives a reaction's channel_id by scanning the event's tags in reverse for the last `e` tag whose content is a 64-character hex string, decoding it, and looking up the target event's own stored channel_id in the database; if no such `e` tag is found it returns NoTarget, and if the target row's channel_id is NULL it returns NoChannel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:572-608"
  - statement: "The main ingest dispatch branch for kind_u32 == KIND_REACTION re-extracts the last valid 64-hex `e` tag and rejects the event with 'invalid: reaction must reference a target event via e tag' if none is present; there is no equivalent extraction, validation, or requirement of a `p` tag anywhere in this branch or elsewhere in crates/buzz-relay, so Buzz does not enforce NIP-25's own (non-mandatory, SHOULD-level) p-tag convention at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3016-3039"
  - statement: "After the e-tag is extracted, ingest calls insert_reaction_event_with_thread_metadata, which first checks that the target event id exists (querying `created_at` from `events` for that id, excluding soft-deleted rows) and returns ReactionEventInsertOutcome::TargetMissing if it does not; the ingest handler maps that outcome to the rejection 'invalid: reaction target event not found', so a reaction to an unknown event id is rejected fail-closed rather than stored as an orphaned reaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs:166-191"
      - "crates/buzz-relay/src/handlers/ingest.rs:3057-3075"
  - statement: "Empty reaction content is treated as '+' before validation and storage (`let emoji = if event.content.is_empty() { \"+\" } else { &event.content };`), matching NIP-25's like/upvote convention for empty content, though Buzz does not itself branch on '+' vs '-' vs any other value semantically anywhere in the ingest or storage path — the like/dislike interpretation is left entirely to consuming clients."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3044-3049"
  - statement: "validate_reaction_emoji accepts any content whose character count is 64 or fewer outright, regardless of whether it is a single emoji, '+', '-', or an arbitrary short string; content longer than 64 characters is accepted only if it is a `:shortcode:`-wrapped NIP-30 custom emoji reference (canonical-lowercase shortcode, total length <= MAX_CUSTOM_EMOJI_REACTION_LEN which is 66) matched by an `[\"emoji\", shortcode, url]` tag on the same event, and is otherwise rejected with 'invalid: reaction emoji exceeds 64 characters'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:160-192"
      - "crates/buzz-sdk/src/builders.rs:123-126"
  - statement: "kind.rs's own module doc comment on KIND_REACTION ('Content is emoji char or `+`/`-`') describes a stricter contract than what validate_reaction_emoji actually enforces at ingest (any string up to 64 characters passes, not only a single emoji character or `+`/`-`); this is a real, checked discrepancy between the code comment and the code's own runtime behavior, not a restatement of one from the other."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:57-58"
      - "crates/buzz-relay/src/handlers/ingest.rs:160-192"
    confidence: 0.85
  - statement: "Three unit tests in ingest.rs exercise the custom-emoji shortcode boundary of validate_reaction_emoji: reaction_validation_accepts_wrapped_max_shortcode, reaction_validation_rejects_mixed_case_max_shortcode, and reaction_validation_rejects_case_mismatched_tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3345-3394"
  - statement: "crates/buzz-sdk/src/builders.rs provides three typed builders for this kind: build_reaction (sets one `e` tag targeting the reacted event and the emoji string as content, rejecting content over 64 characters before it ever reaches ingest), build_custom_emoji_reaction (sets one `e` tag plus one `[\"emoji\", shortcode, url]` tag with content `:shortcode:`), and build_remove_reaction (builds a kind:5 NIP-09 deletion event tagging the reaction event's own id, with empty content) — Buzz has no direct 'un-react' verb; removing a reaction is deleting the reaction event."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:474-483"
      - "crates/buzz-sdk/src/builders.rs:485-503"
      - "crates/buzz-sdk/src/builders.rs:505-509"
  - statement: "crates/buzz-cli implements a `reactions` subcommand tree (add, remove, get) dispatched from ReactionsCmd; cmd_add_reaction builds via buzz_sdk::build_custom_emoji_reaction or build_reaction and submits it, cmd_remove_reaction queries the caller's own kind:7 reactions on the target event ({\"kinds\":[7],\"#e\":[event_id],\"authors\":[my_pk]}) to find the matching reaction event id and then calls build_remove_reaction, and cmd_get_reactions queries all kind:7 reactions on an event and groups them by emoji content into {emoji, count, pubkeys}."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/reactions.rs:9-32"
      - "crates/buzz-cli/src/commands/reactions.rs:34-78"
      - "crates/buzz-cli/src/commands/reactions.rs:80-125"
      - "crates/buzz-cli/src/lib.rs:2104"
  - statement: "Thread counters (reply_count/descendant_count) are never touched by a reaction insert: thread_meta is computed as None whenever requires_h_channel_scope(kind) is false, which is always true for KIND_REACTION, and insert_event_with_thread_metadata_tx only increments those counters when thread_meta is Some — reaction inserts always call it with thread_meta = None."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2987-2997"
      - "crates/buzz-db/src/store/event.rs:1213-1320"
  - statement: "An end-to-end integration test sends one reply and one reaction against the same thread root and asserts the channel-window summary's reply_count equals 1 (counting only the reply) while the reaction appears solely in the 'aux closure' rows, confirming reactions do not participate in thread-counter materialization."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "The relay's read-path `#h` filter matching falls back to the stored event's channel_id specifically when the event carries no `h` tags at all — the comment names kind:7 (reactions) and kind:5 (deletions) as the motivating case, since both derive channel from their target rather than carrying their own `h` tag — and a dedicated test, h_tag_fallback_uses_stored_channel_id, exercises this for a reaction event with no h tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:78-100"
      - "crates/buzz-core/src/filter.rs:210"
  - statement: "The channel-window bridge API's WINDOW_AUX_KINDS constant (reactions, NIP-09/NIP-29 deletions, stream-message edits) includes KIND_REACTION, meaning reactions are delivered to bridge clients as part of a channel window's 'aux closure' overlay rather than as ordinary row events, and do not consume the window's row budget."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:391-397"
  - statement: "NIP-09 (standard kind:5) deletion processing special-cases a deleted target that is itself a reaction: handle_standard_deletion_event checks if the deleted target's kind equals KIND_REACTION, and if so first attempts remove_reaction_by_source_event_id, falling back to deriving the (target, actor, emoji) tuple from the reaction event's own tags/content/author if the direct removal misses (documented as a best-effort backfill gap)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:2359-2404"
  - statement: "crates/buzz-workflow treats KIND_REACTION as a first-class workflow trigger: TriggerDef::ReactionAdded matches events whose kind equals KIND_REACTION, and build_trigger_context exposes the reaction's content as an `emoji` field and resolves `message_id` to the reacted-to event's id (the last 64-hex `e` tag) rather than the reaction event's own id, specifically for reaction-kind events."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:942-990"
      - "crates/buzz-workflow/src/lib.rs:1039-1042"
  - statement: "Searching crates/buzz-search and crates/buzz-audit for any case-insensitive occurrence of \"reaction\" returns zero matches in both crates, so kind:7 events receive no dedicated full-text-search indexing treatment (NIP-50 FTS query paths are kind-agnostic and reactions are not in the P_GATED-style NULL-tsvector carve-out, since they are not P_GATED) and no dedicated audit-log entry type."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-audit/src/lib.rs"
      - "crates/buzz-audit/src/action.rs"
  - statement: "No docs/nips/NIP-25.md file exists in this repository (docs/nips/ contains only Buzz's own custom-NIP proposals for kinds with no existing community NIP); the primary in-repo protocol reference for kind:7 reactions is NOSTR.md at the repository root, which documents the feature status table row, the channel-derivation note (target's `#e` tag, client `#h` ignored), the security note ('Reactions to unknown events are rejected (fail-closed)'), and a troubleshooting entry for the 'invalid: reaction target event not found' rejection message."
    entry_class: FACT
    evidence:
      - "NOSTR.md:50"
      - "NOSTR.md:192-198"
      - "NOSTR.md:349"
      - "NOSTR.md:363"
  - statement: "No code in this repository reads or validates a `k` tag on a kind:7 event anywhere (searched crates/buzz-relay/src/handlers/ingest.rs and crates/buzz-sdk/src/builders.rs for a `\"k\"` tag-kind check specific to reactions), so NIP-25's optional k-tag convention is unimplemented by Buzz today."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "Issue #882's Definition of Done requires this node to state the event kind number/name and persistence classification, define required/optional tags/content and validation rules, name producers/consumers/authorization/persistence/fanout/search/audit treatment, and link the NIP/spec, handler/registry and conformance/tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#882 definition of done"
  - statement: "crates/buzz-acp/src/pool.rs implements best-effort agent-side reaction helpers: reaction_add builds a reaction via buzz_sdk::build_reaction, signs it and submits it via POST /events, and reaction_remove builds a removal via buzz_sdk::build_remove_reaction the same way; both are documented in code as 'best-effort... reactions are cosmetic' and swallow errors (log-and-return) rather than propagate them."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4721-4744"
      - "crates/buzz-acp/src/pool.rs:4804"
---

# Event kind 7 — Reaction

## Kind identity

- **Kind number:** `7`
- **Name:** Reaction (NIP-25)
- **Rust constant:** `KIND_REACTION` — `crates/buzz-core/src/kind.rs:58`, `pub const KIND_REACTION: u32 = 7;`
- **Registered:** yes, in `ALL_KINDS` (`crates/buzz-core/src/kind.rs:649`) — this is a fully implemented, shipping kind, not a proposed one.
- **`type: interfaces-events`** — this node's own front-matter type, per `node.schema.json`'s dedicated enum value for the protocol/interface surface.

## Referenced specification

**NIP-25** (`nostr-protocol/nips`, `25.md`, pinned at commit
[`dabfcb2aaecf4fa374eda8b1232ab303a03f60ba`](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/25.md)).
NIP-25 defines kind 7 as "used to indicate user reactions to other events," with:

- `e` tag: **MUST** be present, set to the id of the reacted-to event.
- `p` tag: **SHOULD** be present, set to the reacted-to event's author pubkey.
- `k` tag: **MAY** be present, the stringified kind of the reacted-to event.
- `content` of `+` or empty: **MUST** be interpreted as a like/upvote.
- `content` of `-`: **MUST** be interpreted as a dislike/downvote.
- Any other content follows separate conventions, including a NIP-30 `:shortcode:` custom-emoji reference.

Buzz's own reference for this kind (there is no `docs/nips/NIP-25.md` — that directory holds only Buzz's own custom-NIP
proposals for kinds with no existing community NIP) is **`NOSTR.md`** at the repository root: the feature table
(line 50), the channel-derivation note (lines 192-198), the security note (line 349), and the troubleshooting
entry for the target-not-found rejection (line 363).

## Kind range and delivery classification

Kind 7 falls outside all three of `kind.rs`'s special ranges — `is_replaceable` (`0 | 3 | 41 | 10000..=19999`),
`is_parameterized_replaceable` (`30000..=39999`), and `is_ephemeral` (`20000..=29999`) — so it is a plain
**regular, persistent, non-replaceable** event, consistent with NIP-01's own regular-kind range. Every accepted
reaction is stored (subject to the target-existence and deduplication rules below) and is never overwritten by a
later reaction from the same author the way a replaceable kind would be; a second reaction from the same author
targeting the same event is instead handled as a **duplicate** (see *Persistence* below), not a replacement.

## Tag shape

| Tag | Cardinality (Buzz-enforced) | Purpose |
|---|---|---|
| `e` | **Exactly one required** (the *last* valid 64-character-hex `e` tag on the event is used; earlier `e` tags, if any, are ignored) | The reacted-to event's id. Ingest rejects the event with `invalid: reaction must reference a target event via e tag` if none is found, and with `invalid: reaction target event not found` if the id does not resolve to a stored, non-deleted event. |
| `p` | **Not read, validated, or required anywhere in Buzz** | NIP-25 recommends (`SHOULD`) a `p` tag naming the reacted-to event's author; Buzz's ingest and SDK builders never set or check one. This is a real gap against the spec's own recommendation, not an oversight this node is asserting without having checked — the omission was confirmed by reading the full ingest reaction branch and both SDK builders. |
| `h` | **Never required, and not authoritative for channel routing even when present** | Reactions are explicitly excluded from `requires_h_channel_scope` (backed by the `reactions_do_not_require_h_tag` unit test). Channel is instead *derived* from the target event's own stored `channel_id` via `derive_reaction_channel`. A client-supplied `h` tag remains on the signed event (tags cannot be stripped without invalidating the signature) and is still matched directly by `#h` filters if present — the fallback to `StoredEvent.channel_id` only engages when the event carries **no** `h` tag at all. |
| `k` | **Not implemented** | NIP-25's optional `k` tag (stringified kind of the reacted event) has no reader or writer anywhere in this repository. |
| `emoji` | **Exactly one, required only for the long-form custom-emoji path** | `["emoji", shortcode, url]`, required when `content` is a `:shortcode:` reference longer than 64 characters; the shortcode must match the `content` value exactly (case-sensitive, canonical lowercase). |

## Content field semantics

`content` is a plain UTF-8 string, not JSON and not encrypted. Buzz's actual ingest validation
(`validate_reaction_emoji`, `crates/buzz-relay/src/handlers/ingest.rs:160-192`) is looser than `kind.rs`'s own doc
comment ("Content is emoji char or `+`/`-`") suggests:

- Any content of **64 characters or fewer** is accepted outright — a single emoji, `+`, `-`, or any other short
  string, with no semantic check that it is actually a single emoji glyph or one of `+`/`-`.
- Content **longer than 64 characters** is accepted only as a NIP-30 custom-emoji reference: a `:shortcode:`
  string (canonical lowercase, total length up to 66 characters — `MAX_CUSTOM_EMOJI_REACTION_LEN`,
  `crates/buzz-sdk/src/builders.rs:123-126`) whose shortcode matches an `["emoji", shortcode, url]` tag on the
  same event; otherwise it is rejected as `invalid: reaction emoji exceeds 64 characters`.
- **Empty content is normalized to `"+"`** before validation and storage
  (`crates/buzz-relay/src/handlers/ingest.rs:3044-3049`), matching NIP-25's like/upvote convention for empty
  content — but Buzz itself never branches on `+` vs `-` vs any other value semantically; the like/dislike
  interpretation is left entirely to consuming clients.

This is a documented gap, not a silent one: **the module doc comment describes a stricter contract than the code
enforces.** A future change tightening `validate_reaction_emoji` to match the doc comment, or relaxing the doc
comment to match the code, would be a runtime-behavior change outside this documentation task's scope.

## Access control and storage model

Kind 7 is absent from all four of `kind.rs`'s named read-gate sets — `AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`,
`P_GATED_KINDS`, `SHARED_GATED_KINDS` — so a stored reaction carries **no special per-kind read restriction**
beyond ordinary channel membership (world-readable to anyone who can read the channel the target event belongs
to). `required_scope_for_kind` requires `Scope::MessagesWrite` to submit one, the same scope an ordinary message
requires.

**Persistence.** Reactions are stored, client-authored events (not relay-authored, not ephemeral). Storage is
atomic and transactional: `insert_reaction_event_with_thread_metadata` first confirms the target event exists
(rejecting with `invalid: reaction target event not found` if not — fail-closed), then upserts a `reactions` row
keyed to dedupe (`ON CONFLICT`) before storing the kind:7 event itself, so an active duplicate reaction from the
same author is detected and the event is **not** re-stored (`ReactionEventInsertOutcome::Duplicate`).

**Fanout.** Reactions do not carry or require an `h` tag, so the relay's `#h` filter fallback treats a tagless
reaction's stored `channel_id` as authoritative for channel-scoped delivery. In the channel-window bridge API,
reactions are delivered as part of the **aux closure** (`WINDOW_AUX_KINDS`, alongside deletions and stream-message
edits) rather than as ordinary window rows, and do not consume the window's row budget.

**Removal.** Buzz has no direct "un-react" verb. Removing a reaction is a NIP-09 kind:5 deletion of the reaction
event itself (`build_remove_reaction`). `handle_standard_deletion_event` special-cases a deleted target that is a
reaction: it first attempts `remove_reaction_by_source_event_id`, falling back to deriving the
`(target, actor, emoji)` tuple from the reaction event's own tags/content/author if that direct lookup misses
(documented in code as a best-effort backfill case).

**Thread counters.** Reactions never increment `reply_count`/`descendant_count` on a thread root: `thread_meta` is
computed as `None` for any kind excluded from `requires_h_channel_scope`, which includes every reaction, and the
counter-increment code path only runs when `thread_meta` is `Some`. An end-to-end test confirms this directly: one
reply and one reaction against the same root produce `reply_count == 1` (only the reply counted), with the
reaction visible solely in the aux closure.

**Search and audit.** Zero references to "reaction" exist in `crates/buzz-search` or `crates/buzz-audit` — kind:7
events get no dedicated full-text-search indexing behavior beyond the ordinary kind-agnostic NIP-50 FTS path, and
no dedicated audit-log entry type.

**Workflow triggers.** `crates/buzz-workflow` treats reactions as a first-class trigger: `TriggerDef::ReactionAdded`
matches on `kind == KIND_REACTION`, and `build_trigger_context` exposes the reaction's content as an `emoji`
field and resolves `message_id` to the *reacted-to* event's id (from the last hex `e` tag), not the reaction
event's own id — the one place in the codebase where a reaction's `e`-tag target is surfaced under a name other
than "channel derivation."

## Producers and consumers

**Producers.**
- `buzz-sdk` (`crates/buzz-sdk/src/builders.rs`): `build_reaction` (one `e` tag, emoji content, rejects content
  over 64 chars client-side before ingest even sees it), `build_custom_emoji_reaction` (one `e` tag plus one
  `emoji` tag, content `:shortcode:`), `build_remove_reaction` (kind:5 deletion of the reaction event id).
- `buzz-cli` (`crates/buzz-cli/src/commands/reactions.rs`): a `reactions` subcommand tree — `add` (builds and
  submits via the two builders above depending on whether `--emoji-url` is given), `remove` (queries the caller's
  own matching kind:7 event via `{"kinds":[7],"#e":[...],"authors":[...]}` and deletes it), `get` (queries all
  kind:7 reactions on an event and groups them by emoji into `{emoji, count, pubkeys}`).
- `buzz-acp` agent-pool helpers (`crates/buzz-acp/src/pool.rs`): `reaction_add`/`reaction_remove` build and
  submit reactions the same way as the CLI (via `buzz_sdk::build_reaction`/`build_remove_reaction`), documented
  in code as best-effort/cosmetic — errors are logged and swallowed rather than surfaced to the caller.

**Consumers.** Any subscriber with channel read access (world-readable, no gating set); the relay itself (aux
closure delivery, live thread-summary badge pushes on deletion, `buzz-workflow` triggers).

## Worked example

A reaction liking a message, with the relay-derived channel (no `h` tag on the wire):

```json
{
  "id": "3f2b...",
  "pubkey": "a1b2...",
  "created_at": 1735689600,
  "kind": 7,
  "tags": [
    ["e", "d4c9f1e2a3b4c5d6e7f8091a2b3c4d5e6f7081920a1b2c3d4e5f60718293a4b5"]
  ],
  "content": "+",
  "sig": "..."
}
```

A NIP-30 custom-emoji reaction, exercising the long-content path:

```json
{
  "id": "9a8b...",
  "pubkey": "a1b2...",
  "created_at": 1735689601,
  "kind": 7,
  "tags": [
    ["e", "d4c9f1e2a3b4c5d6e7f8091a2b3c4d5e6f7081920a1b2c3d4e5f60718293a4b5"],
    ["emoji", "party_parrot", "https://media.example.com/emoji/party_parrot.gif"]
  ],
  "content": ":party_parrot:",
  "sig": "..."
}
```

## Versioning and supersession

None. Kind 7 has not been renumbered or superseded in this codebase; it maps directly and only to the external
NIP-25 kind number, with no Buzz-specific predecessor.

## Scope and omissions

**This document covers** kind 7's wire contract as implemented by this relay: tag shape, content validation,
access control, persistence, dedup, and fanout behavior, and its producers (`buzz-sdk`, `buzz-cli`) and consumers
(read access, workflow triggers, the channel-window bridge). It does not describe any UI feature built on top of
reactions (e.g. desktop/mobile reaction-picker components) — per the event-kind/interface boundary the template
for this node type draws, that belongs to a future interface-typed node, which should reach this one with a
`depends-on` relationship rather than restating this node's tag/content rules.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any desktop/mobile/web UI surface for adding or viewing reactions | A future interface-typed corpus node (none merged yet) |
| Whether Buzz should tighten `validate_reaction_emoji` to match `kind.rs`'s own doc comment, or relax the comment to match the code | Not filed as its own issue at the time this node was written |
| Whether Buzz should implement NIP-25's `p` tag (author) or `k` tag (kind) conventions | Not filed as its own issue at the time this node was written |

**Expected but not verified when this node was written:** this node describes `pool.rs`'s `reaction_add`/
`reaction_remove` as best-effort/cosmetic per their own doc comments and error-swallowing behavior, but does not
verify from which specific agent-workflow call sites they are invoked or under what UI/product conditions an
agent decides to react at all — that is downstream product behavior, not part of this kind's own wire contract.
