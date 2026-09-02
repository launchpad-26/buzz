---
id: events-kinds-kind-40002-stream-message-v2
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
  - statement: "crates/buzz-core/src/kind.rs defines pub const KIND_STREAM_MESSAGE_V2: u32 = 40002, under a 'Stream messaging' section header, with the doc comment 'V1 used kind:10002 (replaceable range — wrong).', and the module's own doc comment states the file 'is the authoritative source for Buzz kind numbers.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-01, at commit dabfcb2aaecf4fa374eda8b1232ab303a03f60ba, defines exactly four numeric kind categories by range — regular (1000<=n<10000 || 4<=n<45 || n==1 || n==2), replaceable (10000<=n<20000 || n==0 || n==3), ephemeral (20000<=n<30000), and addressable (30000<=n<40000) — and states of everything else only that 'these are just conventions and relay implementations may differ,' mandating no default classification for a kind number outside all four ranges."
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/nostr-protocol/nips/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "40002 falls above NIP-01's own addressable ceiling of 40000 and outside every one of its four stated ranges, so NIP-01 itself assigns kind 40002 no explicit category."
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/nostr-protocol/nips/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "kind.rs's own is_replaceable (matches only 0, 3, KIND_CHANNEL_METADATA, and 10000..=19999), is_parameterized_replaceable (PARAM_REPLACEABLE_KIND_MIN..=MAX, i.e. 30000..=39999), and is_ephemeral (EPHEMERAL_KIND_MIN..=MAX, i.e. 20000..=29999) helpers all return false for 40002, so Buzz's own code likewise assigns kind 40002 none of NIP-01's three special categories, leaving only the residual 'regular, stored, never replaced' treatment its ingest dispatch actually gives it (see the ingest.rs FACT below)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Kind 40002 is a member of none of kind.rs's four named read-gating sets — AUTHOR_ONLY_KINDS ([KIND_EVENT_REMINDER, KIND_PUSH_LEASE, KIND_PRIVATE_MANAGED_AGENT]), RESULT_GATED_KINDS ([KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC]), P_GATED_KINDS ([KIND_AGENT_OBSERVER_FRAME, KIND_MEMBER_ADDED_NOTIFICATION, KIND_MEMBER_REMOVED_NOTIFICATION, KIND_GIFT_WRAP, KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC]), or SHARED_GATED_KINDS ([KIND_PERSONA, KIND_TEAM_CATALOG]) — nor does is_relay_only_kind's match arm list it (that arm names KIND_NIP43_MEMBERSHIP_LIST, KIND_CHANNEL_SUMMARY, KIND_PRESENCE_SNAPSHOT, KIND_DM_VISIBILITY, KIND_THREAD_SUMMARY, and KIND_WINDOW_BOUNDS)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's required_scope_for_kind maps KIND_STREAM_MESSAGE_V2 to Scope::MessagesWrite, in the same match arm as KIND_STREAM_MESSAGE, KIND_STREAM_MESSAGE_EDIT, KIND_STREAM_MESSAGE_PINNED, KIND_STREAM_MESSAGE_BOOKMARKED, KIND_STREAM_MESSAGE_SCHEDULED, KIND_STREAM_REMINDER, KIND_STREAM_MESSAGE_DIFF, KIND_FORUM_POST, KIND_FORUM_VOTE, and KIND_FORUM_COMMENT."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's requires_h_channel_scope function lists KIND_STREAM_MESSAGE_V2 among the kinds that require an h tag for channel scoping, and its is_global_only_kind function does not list KIND_STREAM_MESSAGE_V2 among the kinds forced to channel_id = NULL — together meaning a kind-40002 event must be channel-scoped via h and is never treated as a global event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's main storage dispatch routes a kind on the three-way split is_replaceable / is_parameterized_replaceable(kind_u32) / else; since both are false for 40002 (per the kind.rs FACT above), a kind-40002 event falls into the else branch, calling state.db.insert_event_with_thread_metadata — the same plain accumulate-forever insert path (never replaced, keyed by event id) used for ordinary regular events, carrying thread metadata when thread_meta is Some."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs resolves NIP-10 thread ancestry for any kind satisfying requires_h_channel_scope (which includes KIND_STREAM_MESSAGE_V2) via resolve_nip10_thread_meta when the event has a channel_id, storing the result as ThreadMetadataOwned and passing it into insert_event_with_thread_metadata's thread_meta parameter; a successful insert of a reply event increments the parent thread's reply_count/descendant_count via crates/buzz-db/src/store/event.rs's insert_event_with_thread_metadata_tx, in the same transaction as the event insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "crates/buzz-core/src/nip10.rs defines the shared NIP-10 marker parser: a valid marker is an e tag with at least four elements and a 64-ASCII-hex event id in the second position, with the third position ignored (a relay-hint slot) and the fourth being the literal marker string 'root' or 'reply'; ThreadMarkers::resolve() collapses root+reply into (root, reply), a reply-only marker into (reply, reply), and root-only or no markers into None (top-level, not a reply)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs"
  - statement: "ingest.rs enforces one relay-wide content-size cap on every event kind, MAX_EVENT_CONTENT_BYTES = 256 * 1024 (256 KB), rejecting any event (including a kind-40002 event) whose content exceeds it with 'invalid: content exceeds maximum size of {max} bytes'; no kind-40002-specific content-size check exists anywhere in ingest.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "migrations/0008_fresh_install_search_allowlist.sql defines the events table's generated search_tsv column as CASE WHEN kind IN (0, 9, 40002, 45001, 45003) THEN to_tsvector('simple', content) ELSE NULL::tsvector END, so a kind-40002 event's content is NIP-50 full-text-search indexed as plain text — one of only five kinds Buzz indexes for search at all — and crates/buzz-db/src/runtime/migration.rs's own fresh-install test (test_fresh_install_search_allowlist, verified by reading the assertion directly) asserts this exact expression against a freshly migrated database."
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "crates/buzz-db/src/store/push.rs's backfill_push_match_jobs enqueues push-match jobs for recent events with 'AND kind IN (9, 40002, 45001, 45003)', documented as mirroring 'the trigger allowlist' — the same set of kinds eligible for push notification delivery, with kind 40002 included alongside kind 9."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs"
  - statement: "crates/buzz-db/src/store/feed.rs's mentions-feed query (the SQL built for a user's @-mention feed) filters 'AND e.kind IN ({KIND_STREAM_MESSAGE}, {KIND_STREAM_MESSAGE_V2}, {KIND_TEXT_NOTE}, {KIND_FORUM_POST}, {KIND_FORUM_COMMENT}, ...)', joined against the event_mentions table on a matching p-tag pubkey — kind 40002 is a first-class member of Buzz's mention-detection surface, identically to kind 9."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs"
  - statement: "crates/buzz-acp/src/pool.rs builds a thread-context filter querying .kinds([Kind::Custom(KIND_STREAM_MESSAGE as u16), Kind::Custom(KIND_STREAM_MESSAGE_V2 as u16)]) scoped by #e=root and #h=channel, to fetch recent thread replies (including the agent's own newest reply) when assembling an agent's conversational context for a turn — the agent harness (buzz-acp) is a real in-repository consumer of kind-40002 events, treating it as interchangeable with kind 9 for thread-reply retrieval."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs"
  - statement: "crates/buzz-sdk/src/builders.rs's build_message function — the SDK's one function for constructing a user-facing stream chat message — hard-codes EventBuilder::new(Kind::Custom(9), content), i.e. kind 9 (KIND_STREAM_MESSAGE), never kind 40002; no function in builders.rs constructs a Kind::Custom(40002) event anywhere in this file."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "crates/buzz-cli/src/commands/messages.rs's cmd_send_message only accepts --kind values None, Some(9), Some(45001), or Some(45003) (returning a usage error 'is not supported' for anything else), and its Some(9) branch calls buzz_sdk::build_message — the same kind-9-only builder from the FACT above. The buzz-cli message-sending surface therefore has no path that emits a kind-40002 event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "desktop/src-tauri/src/commands/messages.rs's outgoing-message command defaults kind_num to buzz_core_pkg::kind::KIND_STREAM_MESSAGE (9) when no explicit kind is supplied, and its thread/reply guard explicitly requires kind_num == KIND_STREAM_MESSAGE for a threaded send — the desktop app's own message-composition path is likewise kind-9-only for ordinary user-authored messages."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages.rs"
  - statement: "No file under crates/, desktop/src, desktop/src-tauri, or mobile/lib in this repository constructs an outgoing event with kind 40002 (searched for 'Kind::Custom(40002)', 'Kind::Custom(KIND_STREAM_MESSAGE_V2', and 'kind: 40002' as a value being set rather than filtered on) outside of test fixtures — every occurrence of kind 40002 found in application code is either a query/filter input (a kind this code is willing to read) or a UI-display/classification lookup (a kind this code knows how to render), never a construction of a new such event to submit."
    entry_class: FACT
    evidence:
      - "shell(grep -rn '40002' crates/ desktop/src desktop/src-tauri mobile/lib) -> every non-test hit is a read-side filter, constant list, or display label; no construction site found"
  - statement: "desktop/src/features/local-archive/ui/localArchiveKinds.ts labels kind 40002 as 'Stream messages v2 (kind 40002)' in its local-archive kind-to-label mapping, alongside kind 9's own label, confirming the desktop app's own UI vocabulary already distinguishes 'v1' (kind 9) from 'v2' (kind 40002) stream messages as two named variants of the same concept."
    entry_class: FACT
    evidence:
      - "desktop/src/features/local-archive/ui/localArchiveKinds.ts"
  - statement: "mobile/lib/shared/relay/nostr_models.dart defines static const channelMessageEventKinds = [streamMessage, streamMessageV2, forumPost, forumComment], documented as 'Event kinds that represent user-visible channel messages' — kind 40002 (streamMessageV2) is grouped with kind 9 as an equally valid, user-visible channel message kind from the mobile client's own read-side classification, not a distinct or lesser category."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
  - statement: "Commit 124047ef88e1919f6134a347de3d9559395bfe75 ('feat: NIP-29 native compatibility — standard nostr clients can chat on Sprout (#63)') changed KIND_STREAM_MESSAGE from 40001 to 9 specifically so that standard NIP-29 Nostr clients could chat on the relay, per its own diff comment 'NIP-29 group chat message kind. V1 used kind:10001 (replaceable range — wrong), then 40001.' The same commit's diff left KIND_STREAM_MESSAGE_V2 unchanged at 40002 — this renumbering event touched only the sibling kind-9 constant, not kind 40002."
    entry_class: FACT
    evidence:
      - "git_show(124047ef88e1919f6134a347de3d9559395bfe75, path='crates/sprout-core/src/kind.rs') -> diff shows KIND_STREAM_MESSAGE changed 40001 -> 9 with an added NIP-29 doc comment; KIND_STREAM_MESSAGE_V2 line is unchanged context"
  - statement: "mobile/lib/shared/relay/nostr_models.dart's channelEventKinds list includes the bare integer 40001 with the inline comment '// legacy pre-migration stream messages', confirming 40001 (KIND_STREAM_MESSAGE's own discarded historical number, per the FACT above) survives only as a dead/legacy read-compatibility entry, not as a currently assignable kind."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
  - statement: "Because no kind-40002-specific tag or content validator exists anywhere in ingest.rs (only the generic 256KB content cap and the generic requires_h_channel_scope/required_scope_for_kind membership apply), and every consumer surface found (feed.rs mentions, push.rs eligibility, the search_tsv allowlist, buzz-acp's thread-context filter, desktop's and mobile's message-kind groupings) treats kind 40002 as tag-shape- and content-shape-compatible with kind 9 rather than defining any independent shape for it, kind 40002 most plausibly shares kind 9's tag vocabulary (h channel tag, optional NIP-10 e-tag root/reply markers, optional p mention tags, optional broadcast tag, optional imeta media tags) and plaintext content — but this is this node's own generalization from the absence of a distinct kind-40002 producer or validator, not a shape read directly off any kind-40002-specific source."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-sdk/src/builders.rs"
    confidence: 0.65
  - statement: "The combination of (a) zero in-repository producers of a kind-40002 event outside tests, (b) uniform, unconditional inclusion of kind 40002 alongside kind 9 in every read-path kind list found, and (c) the desktop UI already carrying a distinct 'v2' label for it, is most consistent with kind 40002 being a reserved/forward-provisioned second message format that every consumer was built to accept defensively, rather than one that is either actively emitted today or genuinely dead code — but no commit message, code comment, issue, or PR found while authoring this node states which of these it is, so this remains this node's own reasoned reading of the evidence, not a documented product decision."
    entry_class: INFERENCE
    evidence:
      - "shell(grep -rn '40002' crates/ desktop/src desktop/src-tauri mobile/lib) -> zero non-test construction sites, universal read-side inclusion"
    confidence: 0.55
  - statement: "crates/buzz-relay/src/handlers/event.rs's fan_out_pubsub_event receives a channel_event from Redis pub/sub (topic Channel(id) for a channel-scoped event, Global for a channel-less one), converts it to a StoredEvent, and dispatches it toward matching live subscriptions; its sibling filter_fanout_by_access enforces the receiver's community label and — for gated kinds — author/p-tag/shared-tag visibility before delivery. Because kind 40002 belongs to none of kind.rs's gated-kind sets (per the FACT above), a live kind-40002 event fans out to any connection subscribed to its channel with no kind-specific narrowing beyond ordinary channel membership, the same generic path any other regular channel-scoped event uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "This repository's root AGENTS.md states: 'All event kind integers are defined in buzz-core/src/kind.rs. New features get new kind integers -- add them here first, then implement handling in the relay,' and separately: 'Channels use h tags (NIP-29 group tag), not e tags.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "launchpad/docs/corpus/templates/event-kind.md (corpus-template-event-kind) is the merged, sanctioned template for a node documenting one Nostr event kind, requiring nine sections (title/kind identity, referenced NIP, kind range and delivery classification, tag shape, content-field semantics, access control and storage model, worked example, versioning and supersession, relationships) and stating that a realized instance most plausibly carries type: interfaces-events and should declare an implements relationship targeting corpus-template-event-kind itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries no events/ subtree at all (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no path under events/), so no sibling event-kind node — including the five drafted on unmerged task/872-876 branches — resolves as a relationships target in the corpus this node is actually validated against; corpus-template-event-kind is the only existing node this document can legitimately point at."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no events/ path present"
relationships:
  - type: implements
    target: corpus-template-event-kind
---

# Event kind 40002: stream message v2

## 1. Title and kind identity

**Kind 40002**, constant `KIND_STREAM_MESSAGE_V2` in `crates/buzz-core/src/kind.rs`. It
is defined and enforced today — Buzz's ingest pipeline actively classifies, scopes,
and stores events of this kind — but (see *Scope and omissions* below) no code path
in this repository currently constructs and submits one. It is not a proposed or
future kind; it is a live, reachable one with an unusual absence of a producer.

## 2. Referenced NIP

No single external NIP governs kind 40002 by number. Buzz's `KIND_STREAM_MESSAGE`
(kind 9) is documented in `kind.rs` as "NIP-29 group chat message kind," and NIP-29
("Relay-based Groups") is the specification this repository's own `AGENTS.md` cites
as the basis for Buzz's `h`-tag channel scoping, which kind 40002 also uses (see
*Tag shape* below). But `kind.rs` carries no comment naming a NIP for
`KIND_STREAM_MESSAGE_V2` itself, and no `docs/nips/NIP-*.md` proposal file for it was
found. This kind is best understood as Buzz's own custom extension of the same
channel-message concept NIP-29 governs for kind 9, not as its own independently
specified protocol surface — a gap named explicitly below rather than papered over.

## 3. Kind range and delivery classification

NIP-01 assigns kind 40002 **no explicit category at all**: its four numeric ranges
top out at addressable/parameterized-replaceable for `30000 <= n < 40000`, and 40002
sits above that ceiling. NIP-01's own text says only that kinds outside its four
ranges are governed by convention ("these are just conventions and relay
implementations may differ"), with no default assumed.

Buzz's own code agrees there is no special classification here, by omission: `kind.rs`'s
`is_replaceable`, `is_parameterized_replaceable`, and `is_ephemeral` helpers all
return `false` for 40002. Cross-checked against `crates/buzz-relay/src/handlers/ingest.rs`'s
storage dispatch (`is_replaceable` / `is_parameterized_replaceable(kind_u32)` / else),
this means a kind-40002 event falls through to the **else** branch:
`insert_event_with_thread_metadata` — the same plain, accumulate-forever storage path
regular events use, keyed by event id and never replaced. So kind 40002 is, by Buzz's
own behavior, a **regular, persistent event** — not replaceable, not
parameterized-replaceable, not ephemeral — even though NIP-01's text does not use the
word "regular" to describe it explicitly (NIP-01's own "regular" range likewise stops
at 9999). This cross-check found no mismatch between `kind.rs`'s classification and
its actual storage-dispatch behavior for this kind.

## 4. Tag shape

`kind.rs` and `ingest.rs` are authoritative for **what the relay requires and how it
routes**, but neither carries a kind-40002-specific tag validator, and no in-repository
code builds one to inspect directly (see *Scope and omissions*). What is directly
verifiable:

| Tag | Cardinality | Source of the requirement |
|---|---|---|
| `h` | exactly one, required | `requires_h_channel_scope` lists `KIND_STREAM_MESSAGE_V2`; ingest rejects/derives `channel_id` from it via `extract_channel_id` |
| `e` (NIP-10 marker) | zero, one, or two | Any event satisfying `requires_h_channel_scope` (kind 40002 included) has its thread ancestry resolved by `resolve_nip10_thread_meta` via `nip10::parse_thread_markers`; a marker tag is shaped `["e", <64-hex-event-id>, <relay-hint-or-empty>, "root"\|"reply"]`. `root`+`reply` = nested reply; `reply` only = direct reply to root; neither = top-level |

**Everything below this line is this node's own INFERENCE (see the corresponding
evidence entry, confidence 0.65), not a shape read directly from a kind-40002-specific
source**, because no producer or validator names it directly:

- `p` mention tags (deduplicated pubkeys), by analogy to `buzz-sdk`'s `build_message`
  (kind 9's own builder)
- `["broadcast", "1"]`, by the same analogy
- `imeta` media tags, by the same analogy

No compile-time or runtime test in this repository asserts a kind-40002 event's tag
shape one way or the other; this table's second half is a plausibility argument, not
a verified contract.

## 5. Content field semantics

**Plaintext, indexed as searchable text.**
`migrations/0008_fresh_install_search_allowlist.sql` defines the `events` table's
generated `search_tsv` column as `to_tsvector('simple', content)` for kind 40002
(alongside kinds 0, 9, 45001, 45003) — Postgres's plain-text search normalizer, which
only makes sense applied to human-readable text, not ciphertext or an opaque binary
blob. No encryption, no JSON-body convention, and no distinct "diff"/structured
payload convention (unlike `KIND_STREAM_MESSAGE_DIFF`, kind 40008, which validates a
git-diff-specific tag set) applies to kind 40002 anywhere in `ingest.rs`.

The only enforced size limit is the relay-wide generic cap: `MAX_EVENT_CONTENT_BYTES
= 256 * 1024` (256 KB), applied to every event kind at ingest, not a kind-40002-specific
number. `buzz-sdk`'s kind-9 `build_message` caps client-side content at 64 KiB before
that generic relay cap is ever reached, but that check lives in the kind-9 builder,
not in anything that constructs a kind-40002 event (none exists — see below).

## 6. Access control and storage model

**Stored, regular/persistent, never replaced.** As established in *Kind range and
delivery classification*, kind 40002 falls into ingest's generic `insert_event_with_thread_metadata`
storage path: stored once, accumulated, never superseded by a later event of the
same kind/author.

**Required scope: `MessagesWrite`.** `required_scope_for_kind` maps
`KIND_STREAM_MESSAGE_V2` to `Scope::MessagesWrite`, in the same match arm as kind 9
and every other stream/forum message kind — an authenticated actor needs the same
write scope kind 9 needs, no more and no less.

**Channel-scoped, never global.** `requires_h_channel_scope` requires an `h` tag;
`is_global_only_kind` does not list this kind, so (unlike, say, `KIND_PROFILE` or
`KIND_TEAM`) a kind-40002 event is never forced to `channel_id = NULL` — it is always
associated with one channel.

**No kind-specific read gate.** Kind 40002 is absent from all four of `kind.rs`'s
named access-control sets (`AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, `P_GATED_KINDS`,
`SHARED_GATED_KINDS`) and from `is_relay_only_kind`'s match arm. Read visibility
therefore follows the same **ordinary channel-membership gate** every regular
channel-scoped message uses — world-readable to channel members (or to anyone, for
an open-visibility channel), with no additional per-event author/p-tag restriction.

**Search-indexed.** One of only five kinds (0, 9, 40002, 45001, 45003) whose content
is indexed into `search_tsv` for NIP-50 full-text search — confirmed by
`migrations/0008_fresh_install_search_allowlist.sql`'s generated-column expression
and cross-checked against `crates/buzz-db/src/runtime/migration.rs`'s own
fresh-install assertion of that exact expression.

**Push-eligible.** `crates/buzz-db/src/store/push.rs`'s backfill query includes kind
40002 in its push-match-job eligibility set (`kind IN (9, 40002, 45001, 45003)`),
documented as mirroring the database trigger's own allowlist.

**Mention-detection-eligible.** `feed.rs`'s mentions-feed query includes kind 40002
in its `kind IN (...)` filter, so a `p`-tag mention inside a kind-40002 event would
surface in a mentioned user's feed exactly as a kind-9 mention does.

**Fan-out: ordinary, no kind-specific narrowing.** `event.rs`'s `fan_out_pubsub_event`
delivers a stored event to matching live subscriptions via `filter_fanout_by_access`,
which enforces per-kind gating only for kinds in the gated sets above. Since kind
40002 is in none of them, a live kind-40002 event reaches any connection subscribed
to its channel through the same generic path any other regular channel-scoped event
uses — no additional narrowing beyond ordinary channel membership.

**No audit-log-specific handling was found or searched for** beyond the ordinary
persistent-event dispatch path; named as a gap, not a confirmed absence.

**Producers.** None found in this repository. `buzz-sdk`'s `build_message` (the SDK's
one stream-chat-message builder), `buzz-cli`'s `cmd_send_message` (which only accepts
`--kind 9`, `45001`, or `45003`), and desktop's own Tauri message-send command (which
defaults to and, for threaded replies, requires kind 9) all construct kind 9 events,
never kind 40002. No file searched under `crates/`, `desktop/src`, `desktop/src-tauri`,
or `mobile/lib` constructs an outgoing kind-40002 event outside test fixtures.

**Consumers.** `crates/buzz-acp/src/pool.rs` queries kinds 9 and 40002 together when
assembling an agent's thread-reply context for a turn. Desktop
(`desktop/src/shared/constants/kinds.ts`, `desktop/src-tauri/src/commands/*`) and
mobile (`mobile/lib/shared/relay/nostr_models.dart`) both include kind 40002
alongside kind 9 in every "channel message," "search," "push-eligible," "mention,"
and "local-archive" kind list found — treating it as a fully valid, equally
first-class timeline-content kind for display, notification, and archival purposes,
even though nothing currently produces one.

## 7. Worked example

Illustrative only — assembled from the *Tag shape* table above (the `h` tag and NIP-10
markers are verified; the `p`/`broadcast`/`imeta` tags are this node's own INFERENCE
by analogy to kind 9, not copied from a captured wire event, since no producer of
this kind was found to capture one from):

A top-level channel message:

```json
{
  "id": "...",
  "pubkey": "<author pubkey, hex>",
  "kind": 40002,
  "content": "Cutting the v2 release branch now.",
  "created_at": 1735689600,
  "tags": [
    ["h", "3fa85f64-5717-4562-b3fc-2c963f66afa6"]
  ],
  "sig": "..."
}
```

A direct reply (root and reply marker collapse to the same parent):

```json
{
  "id": "...",
  "pubkey": "<author pubkey, hex>",
  "kind": 40002,
  "content": "Same here, following along.",
  "created_at": 1735689650,
  "tags": [
    ["h", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["e", "<64-hex root/parent event id>", "", "reply"]
  ],
  "sig": "..."
}
```

## 8. Versioning and supersession

**This constant's own prior number.** `kind.rs`'s comment on `KIND_STREAM_MESSAGE_V2`
reads only "V1 used kind:10002 (replaceable range — wrong)" — recording that this
specific constant was previously numbered 10002 (inside NIP-01's *replaceable* range,
which the comment calls a mistake) before settling at its current 40002.

**A separate, adjacent renumbering that did not touch this kind.** Kind 9
(`KIND_STREAM_MESSAGE`) has its own, different numbering history: it was originally
40001, and commit `124047ef8` ("NIP-29 native compatibility — standard nostr clients
can chat on Sprout") renumbered it down to 9 specifically so that standard NIP-29
Nostr clients could interoperate. That same commit's diff left
`KIND_STREAM_MESSAGE_V2` untouched at 40002. Mobile's own `channelEventKinds` list
still carries the bare integer `40001` labeled `// legacy pre-migration stream
messages` — confirming 40001 (kind 9's discarded former number) survives only as a
dead read-compatibility entry today, distinct from and not to be confused with 40002.

**What "V2" means here is not settled by any source found.** The desktop app's own
local-archive UI already labels kind 40002 "Stream messages v2," and every consumer
list found groups it with kind 9 as an equally valid message kind — but whether
40002 is a forward-provisioned richer format awaiting a producer, or a leftover from
an earlier design that every read path still defensively humors, is not stated
anywhere this node found. See *Scope and omissions*.

## 9. Relationships

This node declares `implements: corpus-template-event-kind` — it is a realized
instance of the event-kind template, not an independent restatement of that
template's required sections. No sibling event-kind node exists in the corpus this
node validates against: `origin/launchpad` carries no `events/` subtree at all at the
recorded revision, so the five sibling kind documents drafted in parallel (kinds
20001, 22242, 39000, 39001, 39002) are not legitimate `relationships` targets yet,
even though their own branches exist. The most natural future edges — a `references`
to kind 9's own eventual corpus node, and a `depends-on`-shaped link from kind
40003's (message-edit) eventual node back to this one — are left for whichever of
those nodes merges second, per `AGENTS.md`'s own guidance to check the actual merge
target rather than the author's own branch.

## Scope and omissions

**This node covers** kind 40002 as a protocol-and-registry citizen: its number, its
absence of NIP-01 range classification, Buzz's own regular/persistent treatment of
it, its verified `h`-tag and NIP-10 requirements, its content and size rules, its
access-control model (or rather, the absence of any kind-specific restriction), its
search/push/mention eligibility, and every producer and consumer found in this
repository.

**It does not cover:**

| Not covered here | Owned by |
|---|---|
| Kind 9 (`KIND_STREAM_MESSAGE`, the actual NIP-29 chat-message kind and this repository's only current message producer) | a separate, not-yet-filed corpus node |
| Kind 40003 (message edit), 40004 (pinned), 40005 (bookmarked), 40006 (scheduled), 40007 (reminder), 40008 (diff) — each is its own event kind and its own corpus node | separate, not-yet-filed corpus tasks |
| Any consumer-facing operation surface built on top of kind 40002 (a `buzz-cli` subcommand, a typed `buzz-sdk` builder) — none currently exists for this kind specifically | an "interface"-typed node, per `corpus-template-event-kind`'s own *Boundary against interface* section, if and when one is built |
| Why no producer of a kind-40002 event exists in this repository, and whether one is planned | not established here — named as a real, unresolved gap, not a product decision this node makes |

**Expected but not verified when this node was written:**

- **Whether a kind-40002 event has ever actually been submitted to a running relay
  (by an external NIP-29-compatible client, for instance) was not tested.** Every
  claim about its handling is read directly from `ingest.rs`/`kind.rs`/`nip10.rs`
  source, not confirmed by observing a live kind-40002 event accepted and stored.
  Because no in-repository client constructs one, this gap could only be closed by
  testing against an external, non-Buzz Nostr client.
- **The *Tag shape* table's `p`/`broadcast`/`imeta` rows are this node's own
  INFERENCE (confidence 0.65), not a verified contract** — see the corresponding
  evidence entry. A kind-40002 event that omitted or reshaped any of these would not
  be rejected by anything found in `ingest.rs`, so this table describes a
  plausible convention, not an enforced one.
- **Why kind 40002 exists at all, separately from kind 9, was not established from
  any commit message, PR, issue, or code comment found while authoring this node**
  — see the *Versioning and supersession* section and the corresponding INFERENCE
  entry (confidence 0.55). This is named as an open question, not answered by
  extrapolation.
- **Whether `docs/nips/NIP-XX.md` is expected for a Buzz-custom kind like this one,
  versus the corpus node alone being sufficient, is unresolved corpus-wide** —
  `corpus-template-event-kind`'s own scope table names this exact question as not
  yet filed as its own issue, and this node does not decide it either.
- **Whether any generated corpus view or knowledge-crate serialization consumes this
  node's `relationships` edge was not tested** — no such consumer was found to test
  against.
