---
id: events-kinds-kind-40003-stream-message-edit
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
  - statement: "crates/buzz-core/src/kind.rs defines `pub const KIND_STREAM_MESSAGE_EDIT: u32 = 40003;` with the doc comment 'V1 used kind:10004 (replaceable range + NIP-51 collision — wrong).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's is_replaceable helper covers only kinds 0, 3, KIND_CHANNEL_METADATA and 10000..=19999; its is_parameterized_replaceable helper covers only 30000..=39999 (PARAM_REPLACEABLE_KIND_MIN/MAX); its is_ephemeral helper covers only 20000..=29999 (EPHEMERAL_KIND_MIN/MAX). None of the three includes 40003, and kind.rs defines no fourth helper for a 'regular' category."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-01 defines exactly four kind-number categories by numeric range: regular for `1000<=n<10000 || 4<=n<45 || n==1 || n==2` ('all expected to be stored by relays'), replaceable for `10000<=n<20000 || n==0 || n==3`, ephemeral for `20000<=n<30000` ('not expected to be stored by relays'), and addressable for `30000<=n<40000` ('addressable by their kind, pubkey and d tag value'). It also defines a tag's first two elements as the tag 'name/key' and 'value' respectively."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "40003 is outside all four of NIP-01's own numeric ranges (it is >= 40000, past the addressable ceiling), so no NIP-01 category applies to this kind by number alone; combined with its absence from all three of kind.rs's own range helpers, this kind's persistence and replacement behavior is Buzz-specific and not NIP-01-derived — this is this node's own reasoning from the two sources side by side, not a sentence either source states outright."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
    confidence: 0.85
  - statement: "A `grep` of docs/nips/*.md (16 proposal files at this revision) for '40003' or 'STREAM_MESSAGE_EDIT' returns exactly one hit — docs/nips/NIP-CW.md line 97 — which mentions kind:40003 only incidentally, as one of the aux-closure kinds a channel-window read may return, and does not itself specify kind 40003's own tag/content contract. No docs/nips/NIP-XX.md file exists that takes kind 40003 as its own subject."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-CW.md"
  - statement: "crates/buzz-sdk/src/builders.rs's build_edit constructs a kind:40003 event with exactly two tags — one `h` tag (channel UUID) and one `e` tag (the hex event id of the message being edited) — and content set to the caller-supplied new_content, rejecting content over 64*1024 bytes via check_content."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The buzz-sdk unit tests edit_happy_path and edit_content_too_large (crates/buzz-sdk/src/builders.rs, sign(build_edit(...))) assert the resulting event has kind.as_u16() == 40003, carries the expected `e` tag, and that content beyond 64*1024 bytes is rejected with SdkError::ContentTooLarge."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The desktop Tauri backend's events.rs::build_message_edit constructs a richer kind:40003 event on top of the same required `h`+`e` tags: zero or more deduplicated `p` tags (one per newly-mentioned pubkey, capped at MAX_MENTIONS=50, via mention_tags), zero or more `imeta` media tags, zero or more custom-emoji tags, and — only when a full mention-identity snapshot is supplied — mention-reference tags plus one `[\"buzz:mention-snapshot\"]` marker tag; an optional single `[\"link-preview\", \"none\"]` two-element tag suppresses link-preview generation for that edit. Content is capped at MAX_CONTENT_BYTES = 64*1024 bytes via check_content, the same numeric limit buzz-sdk enforces independently."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/events.rs"
  - statement: "The desktop edit_message Tauri command rejects an edit whose trimmed content is empty AND whose media_tags are empty, with the comment 'Empty text is allowed when the edit still carries imeta attachments (a media-only edit)' — so content may legitimately be an empty string when the edit only changes attachments."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's required_scope_for_kind maps KIND_STREAM_MESSAGE_EDIT (grouped with KIND_STREAM_MESSAGE, KIND_STREAM_MESSAGE_V2 and sibling stream-message kinds) to Scope::MessagesWrite; a submitter must hold that scope to have a kind:40003 event accepted at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's requires_h_channel_scope lists KIND_STREAM_MESSAGE_EDIT among the kinds that require an `h` tag for channel scoping, consistent with root AGENTS.md's statement that 'Channels use h tags (NIP-29 group tag), not e tags' for events inside a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "AGENTS.md"
  - statement: "ingest.rs explicitly skips its generic channel-membership gate for kind:40003 (alongside kind:9002/9005/9008 and the join/create-group kinds), with the comment 'per-kind validators are the authority; they individually enforce authorization and fail closed. Bypassing the generic member/open gate here lets the owning human act on private agent channels without being a member' — deferring authorization entirely to validate_edit_ownership for this kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's validate_edit_ownership requires exactly one `e` tag whose value is a 64-character hex event id; rejects the event if no event with that id exists in the same community, or if a resolved channel context on the edit disagrees with the target event's own channel_id; and then, using effective_message_author (which resolves relay/workflow-attributed events via an `actor` or `p` tag rather than trusting event.pubkey alone) to determine the target's real author, allows the edit only when either (a) the submitting actor IS that author AND is still a member of the target's channel or that channel's visibility is 'open', or (b) the submitting actor is NOT that author but is the registered agent-owner (is_agent_owner) of that author's pubkey — every other case is rejected with 'must be event author to edit'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "KIND_STREAM_MESSAGE_EDIT is absent from all four of kind.rs's named access-control sets — AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS and RESULT_GATED_KINDS — so, beyond the write-time checks above, a stored kind:40003 event is read like an ordinary stream message: visible to any reader authorized to read its channel, with no additional per-event read gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-search/src/lib.rs documents the events table's `search_tsv` column as `TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED` for every stored row, and kind.rs's P_GATED_KINDS doc comment states that only kinds in that set get the storage layer's NULL-tsvector override; since kind:40003 is not P_GATED, its content is included in NIP-50 full-text search like any other unrestricted stored kind's content, with no kind-40003-specific opt-out found in either crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-audit/src/action.rs defines a generic AuditAction::EventCreated variant (action string 'event_created'), and crates/buzz-relay/src/handlers/event.rs's enqueue_event_created_audit function — which builds a NewAuditEntry with that action — is not kind-gated in its own body (the kind is passed through only for enrichment, not as a filter); a kind:40003 event that reaches this call site is audited exactly like any other created event, with no kind-specific audit behavior found."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/action.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-relay/src/api/bridge.rs's WINDOW_AUX_KINDS constant lists KIND_STREAM_MESSAGE_EDIT alongside KIND_DELETION, KIND_REACTION and KIND_NIP29_DELETE_EVENT as one of four 'aux closure' kinds: a channel-window read fetches these by `e`-tag reference to the window's row ids as a first hop, in addition to the row events themselves, and docs/nips/NIP-CW.md's own prose (line 97) describes this same hop-1 behavior for 'edits (Buzz kind:40003)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "docs/nips/NIP-CW.md"
  - statement: "Desktop's formatTimelineMessages.ts builds one map entry per edited target id, keeping only the latest-by-created_at kind:40003 event for which isAuthorizedMessageEdit returns true (the edit's signer equals the target's resolved author, OR the signer equals that author's registered ownerPubkey from the profile lookup) — an unauthorized or superseded edit is discarded client-side even though the relay already stored and delivered it."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/formatTimelineMessages.ts"
  - statement: "formatTimelineMessages.ts's hasLinkPreviewSuppression treats an authorized edit carrying an exact two-element `[\"link-preview\", \"none\"]` tag as a monotonic marker: once any authorized edit on a target carries it, link-preview suppression for that target is treated as permanent, independent of which edit supplies the latest body text."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/lib/formatTimelineMessages.ts"
  - statement: "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs is an end-to-end test enumerating five authorization predicate sites for a human owner acting on their agent's content, the first of which it names explicitly as 'kind:40003 message edit (validate_edit_ownership)', exercised over a real relay connection with an owner→agent relationship established via NIP-OA."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs"
  - statement: "Issue #878's definition of done requires this node to state the kind number/name and persistence classification, define required/optional tags and validation rules, name producers/consumers/authorization/persistence/fanout/search/audit treatment, and link handler/registry plus conformance/tests — the section list this node's body is organized against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#878 definition of done"
---

# Event kind 40003 — stream message edit

`KIND_STREAM_MESSAGE_EDIT` (`crates/buzz-core/src/kind.rs`), integer **40003**. A
Buzz custom kind: a client publishes a kind:40003 event to change the effective
display content (and/or attachments) of an earlier stream message, rather than
mutating the original event, which is immutable once signed.

## Referenced specification

No Nostr Improvement Proposal governs this kind, and Buzz has not written a
`docs/nips/NIP-XX.md` proposal for it either — a `grep` of all 16 files
currently under `docs/nips/` finds kind 40003 mentioned only once, incidentally,
in `docs/nips/NIP-CW.md`'s description of channel-window aux-closure fanout, not
as that kind's own specification. `crates/buzz-core/src/kind.rs` is the only
authoritative source for this kind's shape, and its doc comment records why the
number is what it is: an earlier version of this kind used `10004`, inside
NIP-01's replaceable range, which was wrong for two reasons — it asserted
per-`(pubkey, kind)` last-write-wins replacement semantics Buzz does not want
for an edit trail, and it collided with NIP-51's own use of numbers in that
neighborhood. Per this template's own *Referenced NIP* guidance, a kind with no
mapped NIP is a signal that a proposal document may be owed, not a license to
improvise one here; this gap is named rather than filled.

## Kind range and delivery classification

NIP-01 defines exactly four numeric categories — regular (`1000<=n<10000` plus
a few singletons), replaceable (`10000<=n<20000` plus `0`/`3`), ephemeral
(`20000<=n<30000`), and addressable (`30000<=n<40000`). **40003 falls outside
all four** — it is past the addressable ceiling of 40000. `kind.rs`'s own three
range helpers agree with that gap: `is_replaceable`, `is_parameterized_replaceable`
and `is_ephemeral` each return `false` for 40003, and no fourth "is_regular"
helper exists to assert the remaining case affirmatively.

In practice, Buzz treats kind 40003 as an ordinary stored, append-only event:
every edit is a new event with its own id, never overwriting or replacing a
prior one at the storage layer (there is no `(pubkey, kind[, d])` replacement
key for it, unlike a NIP-01 replaceable or NIP-33 addressable kind). "Latest
edit wins" is a **client-side read-time convention** — see *Consumers* below —
not a relay-enforced replacement rule. This placement outside NIP-01's own
ranges, and the absence of a `kind.rs` helper for it, is this node's own
inference from reading the two sources side by side; `kind.rs` never states in
so many words that 40003 is "regular."

## Tag shape

| Tag | Cardinality | Meaning |
|---|---|---|
| `h` | exactly one | Channel UUID — NIP-29 group-tag convention (`AGENTS.md`: "Channels use `h` tags ... not `e` tags"). Required for ingest (`requires_h_channel_scope`). |
| `e` | exactly one | Hex event id of the message being edited. Required by `validate_edit_ownership`; missing or malformed (not 64 hex chars) is rejected. |
| `p` | zero or more | One per newly-mentioned pubkey, deduplicated, capped at 50 (`MAX_MENTIONS`). Desktop-only; the bare `buzz-sdk` builder never adds these. |
| `imeta` | zero or more | Media attachment metadata. Desktop-only. |
| emoji tag | zero or more | Custom emoji used in the edited content. Desktop-only. |
| mention-reference tags + `["buzz:mention-snapshot"]` | zero, or a full set + one marker | Present only when the composer supplies a complete mention-identity snapshot rather than a partial add-only mention list. Desktop-only. |
| `["link-preview", "none"]` | zero or one | Exactly two elements. Suppresses link-preview generation for this edit; monotonic client-side once any authorized edit on a target carries it. |

The `buzz-sdk` builder (`build_edit`, used by non-desktop producers such as
`buzz-cli`) emits only the two required tags (`h`, `e`). The desktop Tauri
backend's `build_message_edit` is a superset adding every optional row above.
Both share the same required core.

## Content field semantics

Plaintext (not JSON, not encrypted) — the new message body text, up to 64KB
(`64*1024` bytes; enforced independently by both `buzz-sdk`'s `check_content`
and the desktop backend's `MAX_CONTENT_BYTES`/`check_content`, at the same
numeric limit). Content **may be an empty string** when the edit only changes
attachments (media-only edit) — the desktop `edit_message` command rejects the
edit only when *both* trimmed content and `media_tags` are empty.

## Access control and storage model

**Write path (ingest).** A submitter needs `Scope::MessagesWrite`
(`required_scope_for_kind`). The generic channel-membership gate is
deliberately bypassed for this kind (`ingest.rs`'s `skip_membership` list,
alongside kind:9002/9005/9008) — its own comment states the reason: per-kind
validators are the authority, so the owning human can act on private
agent-owned channels without themselves being a member. `validate_edit_ownership`
is that per-kind validator, and it enforces, in order:

1. Exactly one `e` tag resolving to a real event in the same community.
2. If the edit itself carries channel context, it must agree with the target
   event's own `channel_id`.
3. Authorization branches on the target's **effective author** — resolved via
   `effective_message_author`, which follows an `actor`/`p` tag instead of
   trusting `event.pubkey` for relay- or workflow-attributed messages:
   - **Actor is that author:** allowed only if the actor is still a member of
     the target's channel, or that channel's visibility is `"open"`. This
     re-gates a *self*-edit so a removed private-channel member cannot mutate
     their own old messages after access is revoked.
   - **Actor is not that author:** allowed only if the actor is the
     *registered agent-owner* of that author (`is_agent_owner`) — the "owning
     human edits their agent's messages" case. Every other actor is rejected
     with `"must be event author to edit"`.

**Read path (storage/fanout/search/audit).** Kind 40003 belongs to none of
`kind.rs`'s four named access-control sets (`AUTHOR_ONLY_KINDS`,
`P_GATED_KINDS`, `SHARED_GATED_KINDS`, `RESULT_GATED_KINDS`), so a stored edit
is readable like an ordinary stream message — no extra per-event read gate
beyond ordinary channel-read authorization. It is persisted (append-only,
looked up by id via `get_event_by_id`), included in NIP-50 full-text search
because it is not in `P_GATED_KINDS` (only that set gets the storage layer's
NULL-`search_tsv` override), and audited generically: `enqueue_event_created_audit`
records an `AuditAction::EventCreated` entry for every created event, kind 40003
included, with no kind-specific audit branch found.

**Fanout.** A channel-window read's aux-closure hop
(`crates/buzz-relay/src/api/bridge.rs::WINDOW_AUX_KINDS`) fetches kind:40003
events by `e`-tag reference to the window's row ids, alongside reactions and
deletions — `docs/nips/NIP-CW.md` documents this same behavior in prose.

## Producers and consumers

**Producers.** `buzz-sdk::builders::build_edit` (used by non-desktop clients,
e.g. `buzz-cli`) and the desktop Tauri backend's `events::build_message_edit`
(invoked by the `edit_message` command, itself driven by
`desktop/src/features/messages/ui/submitMessageEdit.ts`).

**Consumers.** `desktop/src/features/messages/lib/formatTimelineMessages.ts`
applies edits at read time: for each target message id, it keeps only the
*latest-by-`created_at`* kind:40003 event for which `isAuthorizedMessageEdit`
returns true (signer is the target's effective author, or is that author's
registered agent-owner) — an edit the relay stored but that fails this
client-side check is silently ignored. "Latest wins" is therefore enforced by
the reader, not by relay-side replacement.

## Worked example

Minimal form (what `buzz-sdk::build_edit` produces):

```json
{
  "id": "...",
  "pubkey": "<editor-pubkey-hex>",
  "created_at": 1735689600,
  "kind": 40003,
  "tags": [
    ["h", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["e", "b1f8e2c9a4d6..."]
  ],
  "content": "corrected message text",
  "sig": "..."
}
```

Richer desktop-authored form, adding an optional mention and link-preview
suppression:

```json
{
  "id": "...",
  "pubkey": "<editor-pubkey-hex>",
  "created_at": 1735689601,
  "kind": 40003,
  "tags": [
    ["h", "3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ["e", "b1f8e2c9a4d6..."],
    ["p", "<newly-mentioned-pubkey-hex>"],
    ["link-preview", "none"]
  ],
  "content": "corrected message text, now mentioning @someone",
  "sig": "..."
}
```

## Versioning and supersession

`kind.rs`'s own doc comment records the history: an earlier iteration used
`10004` (NIP-01's replaceable range), which was wrong both semantically (it
implied last-write-wins replacement, which this kind does not want) and
practically (it collided with NIP-51's own use of numbers nearby). The kind
was renumbered to 40003 and has not changed since, at the recorded revision.

## Conformance and tests

- `crates/buzz-sdk/src/builders.rs`: `edit_happy_path` (asserts `kind == 40003`
  and the `e` tag round-trips) and `edit_content_too_large` (asserts the
  64*1024-byte cap is enforced).
- `crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs`: a live,
  relay-backed end-to-end test naming "kind:40003 message edit
  (`validate_edit_ownership`)" as one of five owner-editing-agent-content
  authorization predicate sites it exercises.

## Relationships

None declared. No corpus node currently merged on `origin/launchpad` is a
plausible target: `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` at the recorded revision shows only governance and
template nodes (`corpus-agents`, `corpus-readme`, the standards and templates
subtrees) — none about Buzz's architecture, flows, or any other event kind.
The most likely future edges are `depends-on` (or `references`) targeting a
sibling `kind-40002-*`/`kind-40004-*` node once one exists (this kind only
makes sense pointed at a stream-message target) and an `implements` edge
targeting `corpus-template-event-kind`, per that template's own suggested
convention for a realized instance — neither target exists yet.

## Scope and omissions

**This document covers** kind 40003's number, classification, tag and content
shape, its write-time authorization (`validate_edit_ownership`), its default
(unrestricted) read-time access model, its storage/search/audit/fanout
treatment, and how the desktop client applies it at read time.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Sibling stream-message kinds (40001 unused/reserved, 40002 `KIND_STREAM_MESSAGE_V2`, 40004 pinned, 40005 bookmarked, 40006 scheduled, 40007 reminder, 40008 diff) | their own corpus tasks, not filed as relationships here per *Relationships* above |
| Whether `messages search`'s CLI-level kind allowlist (root `AGENTS.md` gotcha #3) includes kind 40003 | not traced to `buzz-cli` source in this task; `buzz-search` itself applies no kind-level restriction (`SearchQuery.kind: None = no kind constraint`), so this is a possible caller-side restriction this node did not check |
| Whether every Buzz-proposed kind requires a `docs/nips/NIP-XX.md` file before a corpus event-kind node may be written | unsettled — the event-kind template itself names this as an open gap, not yet filed as its own issue at the recorded revision |
| The interfaces-events vs. a future "interface" node boundary for this kind (a `buzz-sdk`/desktop *consumer-facing* edit operation, as distinct from the kind's own wire contract documented here) | the event-kind template's own *Boundary against interface* section, which names this as a real, unresolved overlap risk with an as-yet-unwritten interface template |

**Expected but not verified when this node was written:**

- **The desktop backend's exact `MAX_CONTENT_BYTES` enforcement path was read
  as a constant and a call site, not exercised against a running relay** — no
  test asserting the desktop-side 64KB rejection (as distinct from the
  `buzz-sdk` one, which does have a unit test) was found or run.
- **Whether the relay itself re-enforces a content-size cap on kind:40003 at
  ingest, independent of the two client-side builders, was not checked** —
  `validate_edit_ownership` was read in full and contains no length check; a
  broader relay-wide content-size gate, if one exists, was not searched for.
- **No live relay run was performed.** All ingest-side and client-side
  behavior above is read from source, not observed end-to-end in this task;
  the cited e2e test (`e2e_human_edit_agent_content.rs`) is `--ignored` by
  default and requires a running relay, which was not started here.
