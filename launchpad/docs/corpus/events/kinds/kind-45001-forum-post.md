---
id: events-kinds-kind-45001-forum-post
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a8b5021efb92264e724366d08b47b2a3839eb90a."
    entry_class: FACT
    evidence:
      - "commit a8b5021efb92264e724366d08b47b2a3839eb90a"
  - statement: "kind.rs defines KIND_FORUM_POST as the u32 constant 45001, under a 'Forum / social (45000–45999)' custom-range heading, doc-commented as 'A forum post (thread root).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The comment immediately preceding the Forum / social range in kind.rs reads '// V1 used addressable range (30001–30003) — wrong.', naming the prior, superseded numbering for this same concept."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "No file under docs/nips/ names kind 45001, 45002, or 45003 anywhere in its text — a full listing and search of the 16 Markdown files there returns no match — so kind 45001 is a Buzz-custom kind with no dedicated NIP-XX.md specification document and no external community NIP."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md"
      - "docs/nips/NIP-AE.md"
      - "docs/nips/NIP-AM.md"
      - "docs/nips/NIP-AO.md"
      - "docs/nips/NIP-AP.md"
      - "docs/nips/NIP-CW.md"
      - "docs/nips/NIP-DV.md"
      - "docs/nips/NIP-ER.md"
      - "docs/nips/NIP-FI.md"
      - "docs/nips/NIP-GS.md"
      - "docs/nips/NIP-IA.md"
      - "docs/nips/NIP-MP.md"
      - "docs/nips/NIP-OA.md"
      - "docs/nips/NIP-PL.md"
      - "docs/nips/NIP-PMA.md"
      - "docs/nips/NIP-RS.md"
      - "docs/nips/NIP-WP.md"
  - statement: "kind.rs's own is_ephemeral (20000–29999), is_replaceable (0, 3, 41, 10000–19999), and is_parameterized_replaceable (30000–39999) helpers each return false for 45001, so under Buzz's own classification 45001 is a plain regular, persistent, non-replacing stored kind — it falls into none of the three special ranges those helpers test."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_FORUM_POST is absent from every one of kind.rs's own named access-control sets: AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS, and RESULT_GATED_KINDS list their members explicitly and none of the four lists 45001."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-relay's ingest handler maps KIND_FORUM_POST (with KIND_FORUM_VOTE and KIND_FORUM_COMMENT) to Scope::MessagesWrite in its per-kind scope allowlist, and separately lists KIND_FORUM_POST in requires_h_channel_scope, meaning an h tag is mandatory and channel-scoped MessagesWrite authorization (not an admin-only scope) is what ingest requires to accept the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A unit test in ingest.rs, channel_scoped_content_kinds_require_h_tags, asserts requires_h_channel_scope(KIND_FORUM_POST) is true, and a companion test in event.rs re-asserts the same fact for the fan-out path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-sdk's build_forum_post constructs the event as Kind::Custom(45001) with content passed through check_content(content, 64 * 1024) (a 64 KiB byte-length cap enforced client-side, returning SdkError::ContentTooLarge on overflow), tags = [an 'h' tag holding the channel UUID, then zero or more deduplicated 'p' mention tags via mention_tags, then zero or more raw 'imeta' tags via imeta_tags], and .allow_self_tagging() set so the author's own pubkey may appear as a mention. It does not call thread_tags, so no 'e' tag is emitted — this is the thread root, not a reply."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "mention_tags rejects more than crate::mentions::MENTION_CAP (= 50) entries with SdkError::TooManyMentions, deduplicates by lowercased hex before emitting each surviving pubkey as its own ['p', pubkey_hex] tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-sdk/src/mentions.rs"
  - statement: "imeta_tags parses each element of the media_tags argument as a raw tag vector via Tag::parse without imposing its own shape beyond what Tag::parse accepts; the CLI's own build_imeta_tag helper (client.rs) is the producer that actually populates that vector, emitting ['imeta', 'url <url>', 'm <mime_type>', 'x <sha256>', 'size <bytes>'] plus optional 'dim', 'blurhash', 'thumb', and 'duration' elements when a BlobDescriptor carries them."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-cli/src/client.rs"
  - statement: "buzz-sdk unit tests forum_post_happy_path and forum_post_content_too_large directly exercise build_forum_post: the former asserts the signed event's kind is 45001 and carries the expected h tag; the latter asserts a 64 KiB + 1 byte content string is rejected with SdkError::ContentTooLarge."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "buzz-relay's own ingest pipeline enforces a second, independent, generic content-length ceiling — const MAX_EVENT_CONTENT_BYTES: usize = 256 * 1024 — applied to every kind's content regardless of any kind-specific client-side cap, rejecting oversized content with 'invalid: content exceeds maximum size of {} bytes'. This is a relay-wide floor, not a forum-post-specific rule, and it is looser than the SDK's own 64 KiB cap for this kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "schema.sql's events.search_tsv generated column is NULL for kinds {1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200} and to_tsvector('simple', content) for every other kind; 45001 is not in that NULL list, so a stored forum-post event's content is indexed into NIP-50 full-text search like any other non-gated kind."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "buzz-cli's messages.rs post command dispatches Some(45001) to buzz_sdk::build_forum_post directly (passing the CLI's assembled content, deduplicated mention refs, and any uploaded-media imeta tags), making 'buzz messages post --kind 45001 ...' the CLI-facing producer path for this kind; the sibling Some(45003) arm requires --reply-to and calls build_forum_comment instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "buzz-db's feed.rs includes KIND_FORUM_POST in two separate feed query kind-lists: the p-tag mentions query (event_mentions join, alongside KIND_STREAM_MESSAGE, KIND_STREAM_MESSAGE_V2, KIND_TEXT_NOTE, KIND_FORUM_COMMENT, and the git-activity kinds) and the activity-feed query (alongside KIND_STREAM_MESSAGE, KIND_STREAM_MESSAGE_V2, and the agent-job kinds), each asserted directly by a dedicated unit test (mentions_query_includes_stream_message_kind, activity_query_includes_agent_job_kinds)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs"
  - statement: "buzz-relay's validate_forum_vote_target function requires a kind:45002 vote's single 'e' tag to resolve to a stored event whose kind is exactly KIND_FORUM_POST or KIND_FORUM_COMMENT, rejecting any other vote target with 'vote target must be a forum post or comment' — the one place ingest validates a cross-reference to kind 45001 by identity rather than by tag shape alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "No file under crates/buzz-audit/, migrations/, or schema/ names 'forum' as a dedicated audit or storage concern beyond the generic events table and the Forum/social kind-range comment in schema.sql and migrations/0001_initial_schema.sql; forum-post creation itself writes no KIND_AUDIT_ENTRY (48001) record, and any audit trail for a forum post arises only from a generic moderation action (e.g. a kind:9005 delete) applied to it, not from a forum-specific audit hook."
    entry_class: INFERENCE
    evidence:
      - "schema/schema.sql"
      - "migrations/0001_initial_schema.sql"
    confidence: 0.7
  - statement: "The exact PR/commit that renumbered this kind from the V1 addressable range (30001–30003) to the current custom range (45001–45003) was not identified by this node's author — `git log -S \"45001\" --oneline -- crates/buzz-core/src/kind.rs` returns only the repository's sprout-to-buzz rename commit (d99ad131f), meaning 45001 was already the value at every point kind.rs existed under its current name and path; the renumbering itself predates that rename and its originating commit was not located."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "git log -S \"45001\" --oneline -- crates/buzz-core/src/kind.rs, run directly while authoring this node"
  - statement: "launchpad/docs/corpus/templates/event-kind.md (id corpus-template-event-kind, status: active) is a validated corpus node — only the top-level schema/ directory is excluded from validate.py's checks — so it is a legitimate target for this node's own implements relationship, per that template's §9 guidance that a real instance should mark itself as a realized instance of the template via a typed implements edge rather than restating the template's requirements in prose."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
      - "launchpad/project-intelligence/corpus/validate.py"
relationships:
  - type: implements
    target: corpus-template-event-kind
---

# Event kind 45001: forum post

## 1. Kind identity

- **Name:** Forum post (thread root)
- **Number:** `45001`
- **Constant:** `KIND_FORUM_POST` in `crates/buzz-core/src/kind.rs`
- **Status:** Implemented and shipping today — not a proposal. `kind.rs`'s doc comment
  reads "A forum post (thread root)."
- **Corpus type:** `interfaces-events`, per `node.schema.json`'s dedicated value for the
  protocol/interface surface, matching this template's own instruction to state the
  choice explicitly rather than leave it to a reader's guess.

## 2. Referenced specification

Kind 45001 is a **Buzz-custom kind with no governing external Nostr community NIP**.
A search of every file under `docs/nips/` (16 Markdown proposal documents at this
revision) found no reference to 45001, 45002, or 45003. Unlike kind 44200
(`docs/nips/NIP-AM.md`) or kind 30300 (`docs/nips/NIP-ER.md`), forum post has no
dedicated `docs/nips/NIP-XX.md` spec — this corpus node, together with `kind.rs`'s
doc comment and the `buzz-sdk` builder function, *is* the closest thing to a written
specification that exists for this kind today. Whether one should eventually be
written is an open question this node does not resolve (see *Scope and omissions*).

## 3. Kind range and delivery classification

`kind.rs` defines three classification helpers, each evaluated against 45001:

| Helper | Range it tests | Result for 45001 |
|---|---|---|
| `is_ephemeral` | 20000–29999 | `false` |
| `is_replaceable` | `0 \| 3 \| 41 \| 10000..=19999` | `false` |
| `is_parameterized_replaceable` | 30000–39999 | `false` |

None match, so under Buzz's own classification 45001 is a **plain regular,
persistent, non-replacing stored event**: every published forum post is kept
indefinitely (subject to moderation deletion) and never silently overwritten by a
later event with the same `(pubkey, kind)` or `(pubkey, kind, d-tag)` pair, unlike a
replaceable or parameterized-replaceable kind.

This is a **deliberate correction**, not the original design: the comment
immediately preceding the "Forum / social (45000–45999)" heading in `kind.rs` reads
`// V1 used addressable range (30001–30003) — wrong.` — an earlier version of this
same concept lived in the 30000–39999 parameterized-replaceable range, which would
have made a forum post *replaceable by its own author* (keyed on `d`-tag), the wrong
model for a thread root. See §8 for what is and isn't known about when that changed.

## 4. Tag shape

From `crates/buzz-sdk/src/builders.rs`'s `build_forum_post`, the authoritative
producer of this kind:

| Tag | Cardinality | Meaning |
|---|---|---|
| `h` | exactly one, **required** | Channel UUID this post belongs to (NIP-29 group-tag convention, per this repo's channel scoping). `requires_h_channel_scope(KIND_FORUM_POST)` is `true` in `buzz-relay`'s ingest handler and is asserted directly by the test `channel_scoped_content_kinds_require_h_tags`. |
| `p` | zero or more | Mentioned pubkeys (hex), deduplicated by lowercased value, capped at `MENTION_CAP = 50` (`SdkError::TooManyMentions` beyond that). The author's own pubkey is permitted as a mention because the builder calls `.allow_self_tagging()`. |
| `imeta` | zero or more | Raw media-attachment tags, passed through from whatever the caller supplies. The CLI's producer path (`build_imeta_tag` in `crates/buzz-cli/src/client.rs`) shapes these as `["imeta", "url <url>", "m <mime_type>", "x <sha256>", "size <bytes>"]` plus optional `dim`, `blurhash`, `thumb`, `duration` elements. |

**No `e` tag.** A forum post is the thread root, so `build_forum_post` never calls
`thread_tags`. Contrast the sibling `build_forum_comment` (kind 45003), which always
adds one or two NIP-10-style `e` tags (`["e", root, "", "root"]` and/or
`["e", parent, "", "reply"]`) to reference the post or comment it replies to.

## 5. Content field semantics

`content` is **plaintext** — not JSON, not ciphertext. Two independent length limits
apply:

- **Client-side (SDK):** `check_content(content, 64 * 1024)` in `build_forum_post`
  rejects content over 64 KiB with `SdkError::ContentTooLarge`, verified directly by
  the unit test `forum_post_content_too_large`.
- **Server-side (relay, generic to every kind):** `buzz-relay`'s ingest handler
  enforces `MAX_EVENT_CONTENT_BYTES = 256 * 1024` (256 KB) on any event regardless of
  kind, rejecting with `"invalid: content exceeds maximum size of {} bytes"`. This is
  a relay-wide ceiling, not a forum-post-specific rule, and it is looser than the
  SDK's own cap — an event built by something other than `buzz-sdk` could in
  principle submit content between 64 KiB and 256 KB and still be accepted by the
  relay.

## 6. Access control and storage model

- **Stored:** yes — a regular, persistent event (see §3), not ephemeral.
- **Read access:** `KIND_FORUM_POST` is absent from every one of `kind.rs`'s named
  gated-read sets (`AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`,
  `RESULT_GATED_KINDS`). It carries no special per-event read restriction beyond
  ordinary channel-membership/visibility rules that apply to any channel-scoped
  event.
- **Write authorization:** `required_scope_for_kind` maps `KIND_FORUM_POST` to
  `Scope::MessagesWrite` — an ordinary channel-member write scope, not an
  admin-only scope.
- **Search:** included in NIP-50 full-text search — `schema.sql`'s `search_tsv`
  generated column is `NULL` only for a fixed list of kinds that does not include
  45001, so `to_tsvector('simple', content)` is computed and indexed for every
  stored forum post.
- **Feed/mentions/activity treatment:** `buzz-db/src/store/feed.rs` includes
  `KIND_FORUM_POST` in both its p-tag mentions query and its activity-feed query
  (each asserted by a dedicated unit test), so a forum post that mentions a user, or
  is posted at all, surfaces through those feed surfaces the same way a stream
  message does.
- **Vote cross-reference:** a `KIND_FORUM_VOTE` (45002) event's `e` tag is validated
  at ingest (`validate_forum_vote_target`) to resolve to a stored event whose kind is
  exactly `KIND_FORUM_POST` or `KIND_FORUM_COMMENT` — the one place ingest checks a
  reference *to* this kind by resolved identity rather than by tag shape alone.
- **Audit (inference, not directly read as an explicit hook):** no file under
  `crates/buzz-audit/`, `migrations/`, or `schema/` names a forum-specific audit
  concern; a forum post's creation does not itself write a `KIND_AUDIT_ENTRY`
  (48001) record. Any audit trail arises only from a generic moderation action
  (e.g. a `kind:9005` delete) applied afterward, the same as for any other
  content kind — this is inferred from the absence of a dedicated hook, not read
  from an explicit statement that none exists, so it is marked `INFERENCE` in the
  evidence ledger above rather than `FACT`.

## 7. Producers and consumers

- **Producer (CLI):** `buzz messages post --kind 45001 ...` in
  `crates/buzz-cli/src/commands/messages.rs` dispatches directly to
  `buzz_sdk::build_forum_post`, assembling final content (inlining any uploaded
  media as Markdown image/video links), resolved mention pubkeys, and imeta tags
  from uploaded files. The sibling `--kind 45003` arm requires `--reply-to` and
  calls `build_forum_comment` instead.
- **Producer (SDK):** any caller of `buzz_sdk::build_forum_post` directly (the
  function `buzz-cli` itself wraps).
- **Consumers:** any subscriber whose `REQ`/live-fanout filter matches the event's
  `h`-tagged channel and is authorized to read that channel — no additional
  per-event gate applies (§6). `buzz-db`'s feed queries (mentions, activity) are
  the two consumer-facing read paths that specifically special-case this kind
  rather than treating it as generic channel content.

## 8. Worked example

```json
{
  "id": "3b1e7f2a9c4d5e6f7081920a3b4c5d6e7f8091a2b3c4d5e6f7081920a3b4c5d",
  "pubkey": "7f8091a2b3c4d5e6f7081920a3b4c5d6e7f8091a2b3c4d5e6f7081920a3b4c5",
  "created_at": 1735689600,
  "kind": 45001,
  "tags": [
    ["h", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["p", "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd"],
    ["imeta", "url https://media.example.com/uploads/launch-screenshot.png", "m image/png", "x 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "size 245760"]
  ],
  "content": "Welcome to the forum! Let's use this thread to discuss the new release.\n\n![image](https://media.example.com/uploads/launch-screenshot.png)",
  "sig": "..."
}
```

This exercises every tag named in §4 (`h`, one `p` mention, one `imeta` media
attachment) and the plaintext content shape from §5. `sig` is illustrative —
redacted, not a real signature.

## 9. Versioning and supersession

Kind 45001 **replaces an earlier V1 numbering in the 30001–30003 addressable
range**, per `kind.rs`'s own comment: `// V1 used addressable range
(30001–30003) — wrong.` That range is NIP-33 parameterized-replaceable
(30000–39999), which would have made a forum post replaceable-by-`d`-tag under
its author — the wrong model for a thread root that must persist independently
of any later post by the same author. The current 45000–45999 "Forum / social"
range is a plain custom range with none of the three special-range behaviors
(§3).

**What is not known:** the exact commit or PR that performed this renumbering
was not identified while authoring this node. `git log -S "45001" --oneline --
crates/buzz-core/src/kind.rs` returns only the repository's sprout-to-buzz
rename commit (`d99ad131f`), meaning the value 45001 was already in place at
every point `kind.rs` existed under its current path and name — the rename
predates that commit and was not traced further back. This is recorded as
`TEAM_KNOWLEDGE` in the evidence ledger, not asserted as a dated fact.

## Scope and omissions

**This document covers** kind 45001's identity, classification, tag and content
shape, access-control model, and known producers/consumers, per the *Required
sections* of `corpus-template-event-kind.md`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 45002 (forum vote) and kind 45003 (forum comment) — each is its own kind and its own independently maintainable corpus node | Not yet authored; out of scope for issue #880 |
| Whether a `docs/nips/NIP-XX.md` proposal document should be written for kind 45001 | Not yet filed as its own issue at the recorded revision |
| The consumer-facing operation surface (the exact `buzz messages post`/`buzz messages thread` CLI contract) as its own reference document, versus this node's producer/consumer summary in §7 | The interface-template boundary `corpus-template-event-kind.md` itself names as unresolved against issue #1342 |
| Whether the forum-vote cross-reference validation in §6 should instead be documented as part of a kind:45002 node | Whichever task authors the kind-45002 node |
