---
id: events-kinds-kind-45003-forum-comment
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
  - statement: "crates/buzz-core/src/kind.rs defines `pub const KIND_FORUM_COMMENT: u32 = 45003;` with the doc comment \"A comment reply on a forum post,\" inside a `// Forum / social (45000–45999)` block that also defines KIND_FORUM_POST (45001) and KIND_FORUM_VOTE (45002), and that same block carries the line `// V1 used addressable range (30001–30003) — wrong.` directly above the three constants."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:547-554"
  - statement: "kind.rs's module doc comment states this file 'is the authoritative source for Buzz kind numbers' and that every constant is `u32` because 'NIP-01 specifies kind as an unsigned integer, and u32 covers the full range without truncation.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:1-5"
  - statement: "kind.rs's `is_ephemeral` (20000–29999), `is_replaceable` (kinds 0, 3, 41, 10000–19999), and `is_parameterized_replaceable` (30000–39999) each evaluate to false for 45003, since it falls in none of those numeric bands."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:768-785"
  - statement: "NIP-01 defines only four numeric categories by kind value -- regular (1000<=n<10000 || 4<=n<45 || n==1 || n==2), replaceable (10000<=n<20000 || n==0 || n==3), ephemeral (20000<=n<30000), and addressable (30000<=n<40000) -- and 45003 falls outside all four explicitly-numbered bands, since NIP-01 does not enumerate any rule for n>=40000."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "Because kind.rs's own is_ephemeral/is_replaceable/is_parameterized_replaceable helpers all return false for 45003, and because no fourth helper or set anywhere in kind.rs treats it as anything other than a plain stored event, Buzz classifies KIND_FORUM_COMMENT as a regular (persistent, non-replaceable, non-addressable) event -- the same residual category NIP-01's own \"regular\" band names for kind values it does not explicitly enumerate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:768-785"
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
    confidence: 0.75
  - statement: "No file named docs/nips/NIP-*.md governs the 45000-45999 forum/social kind range at the recorded revision; `ls docs/nips/*.md` lists 21 proposal files, none with a forum-related name or topic, so kind 45003's only present specification is the inline kind.rs doc comment."
    entry_class: FACT
    evidence:
      - "shell(ls docs/nips/*.md) -> NIP-AA.md, NIP-AE.md, NIP-AM.md, NIP-AO.md, NIP-AP.md, NIP-CW.md, NIP-DV.md, NIP-ER.md, NIP-FI-CONF.md, NIP-FI-DELEG.md, NIP-FI-EDGE.md, NIP-FI-LIFECYCLE.md, NIP-FI-MODEL.md, NIP-FI.md, NIP-GS.md, NIP-IA.md, NIP-MP.md, NIP-OA.md, NIP-PL.md, NIP-PMA.md, NIP-RS.md, NIP-WP.md -- none forum-named"
  - statement: "buzz-relay's `requires_h_channel_scope` function lists KIND_FORUM_COMMENT among the kinds that require an `h` tag for channel scoping, and a dedicated test, `channel_scoped_content_kinds_require_h_tags`, asserts this for KIND_FORUM_COMMENT alongside KIND_FORUM_POST and KIND_FORUM_VOTE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:704-718"
      - "crates/buzz-relay/src/handlers/ingest.rs:3657-3672"
  - statement: "buzz-sdk's `build_forum_comment` function (kind.rs's Kind::Custom(45003)) always pushes an `h` tag first, then calls `thread_tags`, which pushes a single `[\"e\", <root-hex>, \"\", \"reply\"]` tag when replying directly to the forum post (root==parent), or two tags -- `[\"e\", <root-hex>, \"\", \"root\"]` then `[\"e\", <parent-hex>, \"\", \"reply\"]` -- for a nested reply, then optional `[\"p\", <pubkey-hex>]` mention tags (deduplicated, capped at buzz-sdk's MENTION_CAP = 50) and optional `imeta` tags built from raw tag vectors."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:300-316"
      - "crates/buzz-sdk/src/builders.rs:178-214"
      - "crates/buzz-sdk/src/mentions.rs:38"
  - statement: "`ThreadRef` (the struct `thread_tags` consumes) is defined in buzz-sdk's crate root with two required fields, `root_event_id` and `parent_event_id`, both `nostr::EventId`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs:28-34"
  - statement: "`build_forum_comment` calls `check_content(content, 64 * 1024)` before building the event, which returns `SdkError::ContentTooLarge` if `content.len()` exceeds 65536 bytes; content itself is passed through as plain text (the event's `content` field), not JSON-wrapped or encrypted."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:307-308"
      - "crates/buzz-sdk/src/builders.rs:35-41"
  - statement: "buzz-cli's `messages send` command maps `--kind 45003` to `build_forum_comment`, and requires `--reply-to` at the CLI layer for that kind specifically, returning `CliError::Usage(\"--reply-to is required for forum comments (kind 45003)\")` when it is absent; the immediate parent supplied by `--reply-to` is resolved to a full `ThreadRef` (root derived from the parent's own NIP-10 tags) via `resolve_thread_ref` before the builder is called."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:668-700"
  - statement: "buzz-relay's `required_scope_for_kind` maps KIND_FORUM_COMMENT (with KIND_FORUM_POST and KIND_FORUM_VOTE) to `Scope::MessagesWrite`, the same write-authorization scope as ordinary stream messages."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:470-484"
  - statement: "`validate_forum_vote_target`, invoked for kind:45002 votes, requires the vote's `e` tag to reference an existing event whose kind is KIND_FORUM_POST or KIND_FORUM_COMMENT, and requires that target event to belong to the same channel as the vote (rejecting a mismatched or missing channel) -- making KIND_FORUM_COMMENT a valid vote target alongside KIND_FORUM_POST."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1219-1269"
  - statement: "KIND_FORUM_COMMENT (45003) is not a member of any of kind.rs's four named access-control sets -- AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS, or RESULT_GATED_KINDS -- confirmed by reading each set's full literal member list."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:159-168"
      - "crates/buzz-core/src/kind.rs:215"
  - statement: "P_GATED_KINDS's own doc comment states that for stored (non-ephemeral) kinds in that set, the storage layer additionally writes a NULL `search_tsv` so the event is unsearchable through NIP-50 full-text search; since KIND_FORUM_COMMENT is not a member of P_GATED_KINDS, this NULLing does not apply to it, so a stored forum comment gets an ordinary (non-NULL) search_tsv under the same storage path as any other non-p-gated persistent kind."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:144-158"
    confidence: 0.7
  - statement: "No file under crates/buzz-search or crates/buzz-audit contains the string \"forum\" or \"FORUM\" at the recorded revision, so kind 45003 has no dedicated search-ranking or audit-log code path beyond the generic FTS/storage behavior implied by its absence from P_GATED_KINDS."
    entry_class: FACT
    evidence:
      - "shell(grep -rln 'forum' crates/buzz-search crates/buzz-audit) -> no output"
  - statement: "No occurrence of `reply_count` or `descendant_count` anywhere in the repository mentions FORUM, so the root AGENTS.md thread-counter convention (reply_count/descendant_count materialized on thread-root events) is not wired to KIND_FORUM_COMMENT; forum threading is carried entirely by the `e`-tag root/reply pair `thread_tags` builds, with no relay-maintained counter."
    entry_class: FACT
    evidence:
      - "shell(grep -rn 'reply_count|descendant_count' --include=*.rs crates/ | grep -i forum) -> no output"
  - statement: "buzz-db's Home-feed `query_mentions` SQL includes KIND_FORUM_COMMENT (with KIND_FORUM_POST and several other kinds) in its mention-notification kind filter, and a dedicated test, `mentions_query_includes_stream_message_kind`, asserts KIND_FORUM_COMMENT membership in that kind list."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs:37-41"
      - "crates/buzz-db/src/store/feed.rs:105-109"
      - "crates/buzz-db/src/store/feed.rs:848-874"
  - statement: "desktop/src/shared/constants/kinds.ts mirrors `KIND_FORUM_COMMENT = 45003` and includes it in `CHANNEL_MESSAGE_EVENT_KINDS` (the unread-trigger set feeding sidebar badges and Home-feed mentions), but its own comment states forum kinds (45001/45003) are deliberately excluded from `CHANNEL_TIMELINE_CONTENT_KINDS` because \"forum channels use a different query path, not this timeline\" -- consumed instead through desktop's dedicated forum feature (ForumThreadPanel.tsx, ForumComposer.tsx, shared/api/forum.ts)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.ts:32-33"
      - "desktop/src/shared/constants/kinds.ts:90-95"
      - "desktop/src/shared/constants/kinds.ts:131-149"
  - statement: "AGENTS.md (repo root) states 'All event kind integers are defined in buzz-core/src/kind.rs. New features get new kind integers -- add them here first, then implement handling in the relay,' which is the convention KIND_FORUM_COMMENT follows."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "The AGENTS.md governing launchpad/docs/corpus states that one node is one independently maintainable idea, and that a newly discovered second concept is filed as its own task rather than folded in; this node accordingly documents only kind 45003 and treats KIND_FORUM_POST (45001) and KIND_FORUM_VOTE (45002) as prose context rather than as sibling nodes or relationship targets, since neither has a corpus node yet to link to."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Issue #881's own definition of done requires this node to state the kind number/name, its persistent/replaceable/ephemeral classification, required/optional tags and content validation rules, producers/consumers/authorization/persistence/fanout/search/audit treatment, and links to the governing NIP/spec, handler/registry, and conformance/tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#881 definition of done"
---

# Kind 45003: forum comment

A comment reply on a forum post (kind 45001) or another forum comment,
addressed to a channel of type `forum`.

## Kind identity

| Field | Value |
|---|---|
| Kind number | `45003` |
| Name | Forum comment |
| Constant | `KIND_FORUM_COMMENT` in `crates/buzz-core/src/kind.rs:554` |
| Sibling kinds | `KIND_FORUM_POST` (45001, thread root), `KIND_FORUM_VOTE` (45002, vote on a post or comment) -- documented elsewhere, not by this node |

## Referenced specification

No numbered `nostr-protocol/nips` NIP and no Buzz custom-NIP proposal document
(`docs/nips/NIP-*.md`) governs kind 45003 at the recorded revision. The only
present specification is `kind.rs`'s own inline doc comment ("A comment reply
on a forum post") and the block-level note directly above the three forum
constants ("V1 used addressable range (30001–30003) — wrong"). Whether a
`docs/nips/NIP-*.md` proposal should exist for this kind range is an open gap,
not answered here — see *Scope and omissions*.

## Kind range and delivery classification

Kind 45003 is outside every numeric band NIP-01 explicitly enumerates
(regular, replaceable, ephemeral, addressable all top out below 40000 or are
otherwise numerically disjoint from 45003). Buzz's own three classification
helpers in `kind.rs` — `is_ephemeral` (20000–29999), `is_replaceable` (0, 3,
41, 10000–19999), and `is_parameterized_replaceable` (30000–39999) — each
evaluate `false` for 45003. No fourth helper or set treats it specially. Buzz
therefore treats kind 45003 as a plain **regular, persistent, non-replaceable**
event: append-only, one row per event, never replaced by a later event with
the same `(pubkey, kind)` or `(pubkey, kind, d_tag)` key.

## Tag shape

Built exclusively by `buzz-sdk::build_forum_comment`. In order:

1. **`h`** — exactly one. The channel UUID (string form), per Buzz's
   `h`-tag channel-scoping convention (NIP-29's group tag, repurposed).
   Required; enforced at ingest by `requires_h_channel_scope`.
2. **`e`** — one or two, depending on nesting:
   - Direct reply to the forum post itself (`root_event_id == parent_event_id`):
     exactly one tag, `["e", <root-hex>, "", "reply"]`.
   - Nested reply (replying to another comment): exactly two tags, in order —
     `["e", <root-hex>, "", "root"]` then `["e", <parent-hex>, "", "reply"]`.
   Both forms are required; a comment always carries a thread reference. The
   relay derives which case applies from whether the CLI/SDK caller supplied
   equal or distinct root/parent ids — it is not itself re-derived server-side
   at ingest for 45003 the way NIP-10 root inference sometimes is for other
   kinds (see *Scope and omissions* for what was not independently verified
   about ingest-side re-validation of this tag pair).
3. **`p`** — zero or more mention tags, one per mentioned pubkey (deduplicated,
   lowercased, capped at 50 — `MENTION_CAP`). Optional.
4. **`imeta`** — zero or more, one per attached media item, built from raw
   tag vectors supplied by the caller (e.g. after an upload). Optional.

## Content field semantics

`content` is plain UTF-8 text (Markdown-capable at the client layer, like
other Buzz message kinds), capped at 65536 bytes (64 KiB) by
`build_forum_comment`'s `check_content` call; exceeding the cap is a
builder-level `SdkError::ContentTooLarge` before the event is even signed.
Content is not JSON-wrapped and not encrypted.

## Access control and storage model

- **Producers**: `buzz-sdk::build_forum_comment`, invoked directly by
  `buzz-cli`'s `messages send --kind 45003 --reply-to <parent>` (the CLI
  requires `--reply-to` for this kind specifically and resolves it to a full
  `ThreadRef` before calling the builder), and presumably by the desktop
  forum composer (`desktop/src/features/forum/ui/ForumComposer.tsx`) via the
  same wire shape — the desktop composer's own call path into an SDK-equivalent
  builder was not independently opened for this node (see *Scope and
  omissions*).
- **Consumers**: desktop's dedicated forum feature
  (`ForumThreadPanel.tsx`, `shared/api/forum.ts`), not the main channel
  timeline — `desktop/src/shared/constants/kinds.ts` explicitly excludes kind
  45003 from `CHANNEL_TIMELINE_CONTENT_KINDS` with the comment "forum channels
  use a different query path." It does participate in
  `CHANNEL_MESSAGE_EVENT_KINDS` (unread/sidebar-badge trigger set) and the
  Home-feed mentions query (`buzz-db`'s `query_mentions`, mirrored by
  `HOME_MENTION_EVENT_KINDS` client-side).
- **Authorization (write)**: `Scope::MessagesWrite`, the same scope ordinary
  stream messages require — no elevated or forum-specific scope exists.
- **Authorization (read)**: kind 45003 is a member of none of `kind.rs`'s four
  named access-control sets (`AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`,
  `SHARED_GATED_KINDS`, `RESULT_GATED_KINDS`). Read access is therefore
  ordinary channel-membership access — the same model as a regular stream
  message in the same channel — with no additional per-event gate.
- **Persistence**: stored (regular, append-only; see *Kind range* above).
- **Search**: `P_GATED_KINDS`'s own doc comment states its persistent members
  get a NULLed `search_tsv` to keep them out of NIP-50 full-text search; since
  kind 45003 is not a member, a stored forum comment is inferred to get an
  ordinary (non-NULL, searchable) `search_tsv` under the same storage path as
  any other non-p-gated persistent kind. No file under `crates/buzz-search`
  mentions "forum" by name, so this is inferred from the gating set's absence
  rather than read directly off a forum-specific code path.
- **Audit**: no file under `crates/buzz-audit` mentions "forum" by name —
  kind 45003 has no dedicated audit-log treatment beyond whatever generic
  hash-chain coverage (if any) applies to stored events without being
  kind-specific. This was not further verified; see *Scope and omissions*.
- **Vote target**: kind 45003 (like 45001) is a valid target for a kind:45002
  forum vote — `validate_forum_vote_target` requires the vote's `e` tag to
  resolve to an existing event of kind 45001 or 45003 in the *same channel*
  as the vote, rejecting any other target kind or a cross-channel target.
- **Thread counters**: the root AGENTS.md convention that `reply_count` and
  `descendant_count` are materialized on thread-root events does not apply to
  kind 45003 — no code path ties forum comments to that counter machinery.
  Forum threading is carried entirely by the `e`-tag root/reply pair.

## Worked example

Nested reply (comment-on-comment) carrying one mention, illustrative only —
signature and ids are not real:

```json
{
  "id": "1111111111111111111111111111111111111111111111111111111111111111",
  "pubkey": "2222222222222222222222222222222222222222222222222222222222222222",
  "created_at": 1735689600,
  "kind": 45003,
  "tags": [
    ["h", "9c6a2f0e-6b3a-4e9a-9b7a-2f6a1c8e4d2b"],
    ["e", "3333333333333333333333333333333333333333333333333333333333333333", "", "root"],
    ["e", "4444444444444444444444444444444444444444444444444444444444444444", "", "reply"],
    ["p", "5555555555555555555555555555555555555555555555555555555555555555"]
  ],
  "content": "Good point — I hadn't considered that edge case.",
  "sig": "..."
}
```

A direct reply to the forum post itself (root == parent) instead carries a
single `e` tag: `["e", "<post-id-hex>", "", "reply"]`.

## Versioning and supersession

The block comment directly above the three forum/social constants in
`kind.rs` — "V1 used addressable range (30001–30003) — wrong" — sits above all
three constants (45001, 45002, 45003) as a group, and the three old numbers
(30001–30003) and three new numbers (45001–45003) are the same count in the
same declared order. From that positional correspondence, kind 45003 most
plausibly renumbers a prior `30003` (parameterized-replaceable range) to its
current regular-range number — but no commit message, PR, or second comment
was found that states the specific 30003→45003 mapping explicitly, so this
is recorded as an inference rather than a fact, and the *reason* the V1
addressable range was "wrong" (i.e., why comments should not be
parameterized-replaceable) is not stated anywhere found either.

## Relationships

None declared. No corpus node exists yet for `KIND_FORUM_POST` (45001) or
`KIND_FORUM_VOTE` (45002), so a typed `depends-on`/`references` edge from this
node to either would not resolve — per `launchpad/docs/corpus/AGENTS.md`'s
step 9, a relationship target must already exist on the branch being merged
into. The forum-vote-target relationship (45003 as a legal `KIND_FORUM_VOTE`
target) and the post/comment sibling relationship are instead stated as prose
above (*Access control and storage model*, *Kind identity*). Once a
`kind-45001-forum-post.md` and/or `kind-45002-forum-vote.md` node exists, this
node should gain `references` edges to both, and `corpus-template-event-kind`
is the likely target for an `implements` edge once that template's own
in-repo precedent is checked against a real instance (this is the first such
instance, so that check has not happened yet either).

## Scope and omissions

**This document covers** kind 45003's number, classification, tag and content
shape, access-control and storage model, its role as a forum-vote target, and
a worked example, grounded in `crates/buzz-core/src/kind.rs`,
`crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-sdk/src/builders.rs`,
`crates/buzz-sdk/src/lib.rs`, `crates/buzz-sdk/src/mentions.rs`,
`crates/buzz-cli/src/commands/messages.rs`, `crates/buzz-db/src/store/feed.rs`,
and `desktop/src/shared/constants/kinds.ts`, all read directly for this node.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Reason |
|---|---|
| A `kind-45001-forum-post.md` or `kind-45002-forum-vote.md` corpus node | Out of this task's scope (issue #881 documents only 45003); each is its own task |
| Whether a `docs/nips/NIP-*.md` proposal should exist for the forum/social kind range | Not settled by any source found at this revision |
| The exact 30001–30003 → 45001–45003 renumbering mapping and its rationale | No commit, PR, or second code comment stating it was found; recorded as an inference in *Versioning and supersession* |
| Whether desktop's forum composer builds its event through an SDK-equivalent path identical to `buzz-sdk::build_forum_comment`, or a parallel TypeScript implementation | `ForumComposer.tsx`'s own build path was not opened for this node |
| Whether the relay re-validates the `e`-tag root/reply pair's internal consistency at ingest (e.g. that a claimed "root" tag's target is actually a forum post) beyond `validate_forum_vote_target`'s vote-specific check | Not independently verified; `validate_forum_vote_target` covers only kind 45002's vote target, not 45003's own tag consistency |
| Any dedicated audit-log (`buzz-audit`) treatment of forum comments | No forum-specific code path found; only the negative (absence) was confirmed |
| Conformance/test coverage beyond the two `requires_h_channel_scope` tests and the one Home-feed mentions test cited above | A broader test-suite survey for kind 45003 was not performed |
