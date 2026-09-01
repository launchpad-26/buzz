---
id: interfaces-nostr-nip-10
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "`crates/buzz-core/src/nip10.rs` is the single shared parser for NIP-10 `root`/`reply` markers on `e` tags. It is documented as consumed by the relay ingest resolver (`resolve_nip10_thread_meta`) and the workflow `trigger_is_reply` predicate 'so every consumer reads ancestry the same way', explicitly to prevent 'a second hand-rolled copy' from drifting on marker semantics and id-validity."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:1-11"
  - statement: "`ThreadMarkers` holds `root: Option<String>` and `reply: Option<String>`, each populated only from an `e` tag with at least 4 parts whose second element is exactly 64 ASCII-hex characters (`is_event_id_hex`); the last valid occurrence of each marker wins on a single linear pass over the tags."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:13-24"
      - "crates/buzz-core/src/nip10.rs:47-81"
  - statement: "`ThreadMarkers::resolve()` collapses the two markers into an optional `(root_id, parent_id)` pair with three cases: `root`+`reply` present -> `(root, reply)` (nested reply); `reply` only -> `(reply, reply)` (a direct reply to the root, where the reply target IS the root); `root` only or neither -> `None` (top-level, not a reply) — this exact three-way rule is asserted by its own unit tests (`resolve_root_and_reply_keeps_both`, `resolve_reply_only_is_direct_reply_to_root`, `resolve_root_only_is_top_level`, `resolve_no_markers_is_top_level`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:26-45"
      - "crates/buzz-core/src/nip10.rs:151-181"
  - statement: "An `e` tag with fewer than 4 parts (no marker), or with a marker but a malformed (non-64-hex) event id, is ignored entirely by the parser and produces no marker — verified by the unit tests `bare_e_tag_without_marker_is_ignored` and `malformed_id_is_ignored_for_both_markers`. Buzz's parser therefore never falls back to NIP-10's deprecated positional convention (first `e` tag = root, last = reply by tag order alone); only explicitly marked tags are read."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:53-59"
      - "crates/buzz-core/src/nip10.rs:122-137"
  - statement: "The relay's ingest handler resolves NIP-10 ancestry only for event kinds that `requires_h_channel_scope` returns true for — the NIP-29 channel-message family (`KIND_STREAM_MESSAGE` = kind 9, `KIND_STREAM_MESSAGE_V2` = 40002, plus edit/pin/bookmark/scheduled/reminder/diff variants), plus canvas and forum kinds and most NIP-29 admin kinds. A global kind:1 note built via `buzz-sdk`'s `build_note` is explicitly documented as using 'a flat reply model' with 'Full NIP-10 threading (root + reply + p-tags) ... deferred' rather than the channel-scoped root/reply/depth/counter machinery below."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:704-730"
      - "crates/buzz-core/src/kind.rs:479-493"
      - "crates/buzz-sdk/src/builders.rs:743-758"
  - statement: "`resolve_nip10_thread_meta` (relay ingest, client-submitted path) parses the incoming event's markers, resolves them to `(root_hex, parent_hex)`, decodes and looks up the parent event by id, rejects with a string error if the parent is not found, if the parent belongs to a different channel, or if the parent has no channel association, and otherwise reconciles the client-claimed root against either the parent's own persisted `thread_metadata.root_event_id` (if the parent already has thread metadata) or an ancestry re-derived from the parent's own tags (`derive_ancestry_from_parent_tags`) when it does not — rejecting with 'root tag does not match thread ancestry' on any mismatch, and with 'thread depth limit exceeded' once resolved depth exceeds 100."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:812-916"
      - "crates/buzz-relay/src/handlers/ingest.rs:931-959"
  - statement: "A rejection from `resolve_nip10_thread_meta` is wrapped as `IngestError::Rejected(format!(\"invalid: {msg}\"))` at its one call site inside the ingest pipeline, gated behind `requires_h_channel_scope(kind_u32)` and a resolved channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2987-2997"
  - statement: "`IngestError` has exactly three variants with a documented transport mapping: `Rejected` (client error/bad event) maps to WebSocket `OK false` and HTTP 400; `AuthFailed` (auth/scope error) maps to WebSocket `OK false` and HTTP 401/403; `Internal` (server error) maps to WebSocket `OK false` and HTTP 500. All three NIP-10 rejection paths above (`parent not found`, wrong-channel, no-channel, root mismatch, depth limit) are `Rejected`, i.e. client-visible `OK false` / HTTP 400, never silently dropped or treated as a server fault."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:383-392"
  - statement: "`resolve_relay_reply_thread_meta` is the parallel resolver for replies the relay itself builds (the workflow path), taking a known `parent_hex` directly rather than validating a client-supplied root/reply pair, and returning a `ReplyAncestry` whose `root_hex()`/`parent_hex()` are the exact hex strings a caller emits back onto the wire as `[\"e\", <id>, \"\", \"root\"]` / `[\"e\", <id>, \"\", \"reply\"]` tags — enforcing the same same-channel invariant and the same depth-100 limit as the client path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:961-1039"
  - statement: "`buzz-db`'s `insert_thread_metadata` inserts one `thread_metadata` row per event and, when the event has a `parent_event_id`, increments the parent's `reply_count` (direct children only) and — always, including when root == parent — the root's `descendant_count` (all descendants at every nesting level), with the insert and every counter update wrapped in a single transaction 'so a crash between them cannot leave reply_count / descendant_count inconsistent with the actual number of reply rows'. `decrement_reply_count` mirrors this exactly, with a floor at 0, when a reply is soft-deleted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:112-120"
      - "crates/buzz-db/src/store/thread.rs:246-297"
  - statement: "`get_thread_replies` returns replies under a root in `(event_created_at ASC, event_id ASC)` order using a composite keyset-pagination cursor (an 8-byte big-endian seconds timestamp followed by the raw event-id bytes), documented as required because 'thread replies routinely share a created_at second (bursty threads)' and a timestamp-only cursor 'silently drops every tied reply past the page limit'; a bare 8-byte cursor is still accepted for backward compatibility but paginates on timestamp alone, 'unsafe across same-second ties'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:336-349"
  - statement: "`buzz-sdk`'s `thread_tags` (the outbound tag builder consumed by `build_message` for channel-scoped messages) emits a single `[\"e\", <id>, \"\", \"reply\"]` tag when `ThreadRef.root_event_id == ThreadRef.parent_event_id` (a direct reply to the root), and two tags — `[\"e\", <root>, \"\", \"root\"]` then `[\"e\", <parent>, \"\", \"reply\"]` — for a nested reply. This mirrors `ThreadMarkers::resolve()`'s read-side rule exactly: what ingest reads as 'reply marker alone means direct reply to root' is what the SDK writes for that same case."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:177-190"
      - "crates/buzz-sdk/src/builders.rs:216-239"
  - statement: "`buzz-cli`'s `messages send` (and `patches send`, `social publish-note`) exposes a `--reply-to <event-id>` flag documented as 'Event ID to reply to (creates a thread)'; `buzz-cli`'s `messages` module resolves the full `ThreadRef` for that flag by fetching the named parent event via `POST /query` and re-deriving its root through the same shared `buzz_core::nip10::parse_thread_markers_from_parts` parser, 'so id-validity, marker selection, and top-level classification cannot drift' from the relay's own reading."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:386-388"
      - "crates/buzz-cli/src/commands/messages.rs:15-93"
  - statement: "Root `AGENTS.md` documents a `buzz messages thread --link '<buzz://message?...>'` CLI operation whose 'selected message ID is authoritative: messages thread verifies its channel and derives its containing root', with an optional `thread` parameter accepted only when it matches that derived root, plus an explicit `--channel <uuid> --event <hex>` form."
    entry_class: FACT
    evidence:
      - "AGENTS.md:213-219"
  - statement: "`buzz-workflow`'s `event_is_reply` predicate — the source of the `trigger_is_reply` boolean available to a workflow's `evalexpr` condition (e.g. `trigger_is_reply == false` to select only top-level messages) — is defined as `buzz_core::nip10::parse_thread_markers(&event.tags).reply.is_some()`, i.e. it agrees with the relay ingest resolver's own top-level/reply classification (a `root`-only or malformed-marker event is never counted as a reply) by construction, sharing the same parser rather than a second implementation."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1005-1016"
      - "crates/buzz-workflow/src/executor.rs:308-314"
  - statement: "`crates/buzz-test-client/tests/e2e_nostr_interop.rs` contains a valid-case test, `test_nip10_thread_reply_creates_metadata`, that sends a root message over REST, sends a WebSocket reply carrying a single `[\"e\", <root>, \"\", \"reply\"]` tag, asserts the relay's `OK` response has `accepted == true`, then queries the thread via `POST /query`'s `depth_limit` extension and asserts the reply is returned with its recorded `reply` e-tag pointing at the root, and that the root itself is never returned as one of its own thread replies."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:435-500"
  - statement: "The same test file contains two rejection-case tests: `test_nip10_unknown_parent_rejected` sends a reply e-tagged to a random nonexistent 64-hex id and asserts the relay's `OK` response has `accepted == false` with a message containing 'not found'; `test_nip10_root_mismatch_rejected` sends a real parent but tags a different random id as `root`, asserting `accepted == false` with a message containing 'root' — matching the 'reply parent not found' and 'root tag does not match thread ancestry' rejection strings in `resolve_nip10_thread_meta`."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:502-583"
  - statement: "These three NIP-10 tests are marked `#[ignore]` (the file's live-relay convention throughout) and were not executed as part of authoring this node — they were read as source evidence for the interface's documented valid/failure behavior, not run against a live Postgres/Redis-backed relay."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:437-438"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:504-505"
    confidence: 0.95
  - statement: "Upstream NIP-10 (`nostr-protocol/nips`, file `10.md`) defines `kind:1` text-note threading and states that marked `e` tags take the form `[\"e\", <event-id>, <relay-url>, <marker>, <pubkey>]` with markers `\"reply\"` (the direct reply target) and `\"root\"` (the thread root), and states as its own guideline that 'a direct reply to the root of a thread should have a single marked e tag of type root'. It also documents a deprecated positional convention (unmarked tags, first = root, last = direct reply) kept only for backward compatibility."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/10.md"
  - statement: "Buzz's own convention deviates from that specific upstream guideline: for a direct reply to the thread root, Buzz's parser (`ThreadMarkers::resolve()`) and outbound builder (`thread_tags`) both use a lone `\"reply\"`-marked tag, never a lone `\"root\"`-marked tag as upstream's own text recommends for that exact case. Buzz also never implements the deprecated positional (unmarked) convention upstream keeps for backward compatibility, and does not auto-populate `p` tags for ancestor authors along a reply chain — `buzz-sdk`'s mention tags (`mention_tags`) are a separate, explicit, deduplicated, capped-at-50 mechanism unrelated to thread ancestry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:26-45"
      - "crates/buzz-sdk/src/builders.rs:177-190"
      - "crates/buzz-sdk/src/builders.rs:192-205"
  - statement: "Issue #1008's Definition of Done requires that the node link 'the authoritative machine/spec representation' and define 'inputs/messages, outputs/responses and error/rejection behavior', 'authentication/authorization, versioning/compatibility and ordering/idempotency where applicable', and include 'at least one valid example and one failure example'."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1008 definition of done"
  - statement: "At repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052, `origin/launchpad`'s corpus tree contains no `interfaces/` subtree and no other `type: interfaces-events` node, so this is the corpus's first interface-shaped instance node; none of the merged nodes (architecture/*, standards/*, templates/*, AGENTS.md, README.md) is a legitimate `relationships` target for NIP-10 subject matter, and no `relationships` are declared here."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no interfaces/ path present, at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
---

# NIP-10 thread replies: interface

This node documents Buzz's implementation of standard Nostr **NIP-10** — the
`root`/`reply` `e`-tag marker convention that threads one event as a reply to
another. The boundary is the WebSocket/HTTP event-ingestion surface (any client
submitting a channel-scoped event via `POST /events` or the WebSocket `EVENT`
message) on one side, and the relay's thread-ancestry resolver plus the
`thread_metadata`-backed read path (`POST /query`'s thread/window views) on the
other. A single shared parser, `buzz-core/src/nip10.rs`, is the one place the
marker convention is read; every consumer below calls it rather than
re-implementing marker semantics.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Parse NIP-10 markers from an event's `e` tags | `crates/buzz-core/src/nip10.rs` — `parse_thread_markers` / `parse_thread_markers_from_parts`, `ThreadMarkers::resolve` | Collapses `root`/`reply` markers into an optional `(root_id, parent_id)` pair. The one shared implementation; every other operation below calls it. |
| Submit a channel-scoped reply (client -> relay) | `POST /events` or WebSocket `EVENT`, resolved by `crates/buzz-relay/src/handlers/ingest.rs` — `resolve_nip10_thread_meta` | Validates the submitted `e`-tag markers against the parent event and its existing thread ancestry; persists `thread_metadata` and increments counters on success. |
| Relay-authored reply (workflow-built) | `crates/buzz-relay/src/handlers/ingest.rs` — `resolve_relay_reply_thread_meta` | Computes root/depth from a known parent id rather than validating client-supplied markers, for replies the relay itself constructs (e.g. workflow actions). |
| Persist thread ancestry + counters | `crates/buzz-db/src/store/thread.rs` — `insert_thread_metadata`, `increment_reply_count`, `decrement_reply_count` | One `thread_metadata` row per event; `reply_count` (direct children) and `descendant_count` (all descendants) maintained transactionally. |
| Read replies under a root | `crates/buzz-db/src/store/thread.rs` — `get_thread_replies`, `get_thread_summary`; relay `POST /query` `depth_limit` extension | Keyset-paginated `(created_at, event_id)` ordering; `get_thread_summary` aggregates counts plus up to 10 participant pubkeys. |
| Build an outbound reply's `e` tags (client-side) | `crates/buzz-sdk/src/builders.rs` — `thread_tags`, used by `build_message` | Emits one `reply`-marked tag for a direct reply to root, or `root`+`reply`-marked tags for a nested reply. |
| CLI: send a reply | `buzz-cli` `messages send --reply-to <event-id>` (also `patches send --reply-to`, `social publish-note --reply-to`); resolved in `crates/buzz-cli/src/commands/messages.rs` | Fetches the named parent via `POST /query` and re-derives its root through the same shared parser before building the reply event. |
| CLI: view a thread | `buzz-cli` `messages thread --link '<buzz://message?...>'` or `--channel <uuid> --event <hex>` (documented in root `AGENTS.md`) | The selected message id is authoritative; the command verifies its channel and derives its containing root. |
| Workflow condition: is this event a reply? | `crates/buzz-workflow/src/lib.rs` — `event_is_reply`; exposed as the `trigger_is_reply` boolean in `evalexpr` conditions (`crates/buzz-workflow/src/executor.rs`) | `true` only when the event carries a valid `reply` marker per the shared parser — agrees with ingest's own reply/top-level classification by construction. |

## Contract and stability

- **Scope of applicability.** NIP-10 ancestry is resolved only for event kinds
  `requires_h_channel_scope` returns `true` for — the NIP-29 channel-message
  family (kind 9 `KIND_STREAM_MESSAGE`, kind 40002 `KIND_STREAM_MESSAGE_V2`,
  and its edit/pin/bookmark/scheduled/reminder/diff siblings), plus canvas,
  forum and most NIP-29 admin kinds. A global kind:1 note (`buzz-sdk`'s
  `build_note`) uses a deliberately simpler flat reply tag with no root
  distinction, no depth, and no `thread_metadata` persistence — see *Boundary*.
- **Marker validity.** An `e` tag counts as a thread marker only when it has at
  least 4 parts and its event-id part is exactly 64 ASCII-hex characters. A
  malformed id is ignored for that marker, never treated as a partial link.
  The last valid occurrence of `root` and of `reply` each win on a single
  linear pass.
- **Resolution rule.** `root`+`reply` present -> nested reply, `(root, reply)`.
  `reply` only -> direct reply to the root, `(reply, reply)`. `root` only, or
  neither marker present, -> not a reply (`None`); a lone `root` tag never
  anchors a reply.
- **Server-side validation on ingest.** The client-submitted path
  (`resolve_nip10_thread_meta`) does not trust the client's claimed root
  blindly: it looks up the parent event, requires the parent to exist and to
  belong to the same channel, and reconciles the claimed root against the
  parent's own persisted or re-derived ancestry. A mismatch is rejected, not
  silently corrected.
- **Depth limit.** Resolved thread depth is capped at 100; exceeding it is a
  rejection (`"thread depth limit exceeded"`), not a truncation.
- **Error/rejection behavior.** Every NIP-10-specific rejection
  (`"reply parent not found"`, `"parent event belongs to a different
  channel"`, `"parent event has no channel association"`, `"root tag does not
  match thread ancestry"`, `"thread depth limit exceeded"`, and invalid hex
  decode errors) is wrapped as `IngestError::Rejected`, which maps to
  WebSocket `OK false` (with the message as the human-readable reason) and
  HTTP 400. None of these is a server fault (`Internal`/500) or an
  authorization failure (`AuthFailed`/401/403) — they are client-input errors.
- **Authentication/authorization.** NIP-10 resolution runs after the event has
  already passed the relay's normal signature verification and community/
  channel-membership write gates (shared with every other event kind); this
  node does not restate that pipeline, only that thread resolution adds no
  *additional* auth requirement of its own beyond "the parent must be visible
  in the same channel."
- **Ordering and idempotency.** `insert_thread_metadata`'s row insert and its
  `reply_count`/`descendant_count` updates run inside one database
  transaction, so a crash between them cannot desynchronize the counters from
  the actual reply rows. Reads (`get_thread_replies`) are ordered
  `(event_created_at ASC, event_id ASC)` with a composite keyset cursor,
  specifically because same-second ties are routine in bursty threads and a
  timestamp-only cursor would silently drop tied replies past a page boundary.
  Re-submitting the identical signed event is governed by the relay's normal
  duplicate-event handling (unchanged by NIP-10 resolution); resolving the
  *same* reply's ancestry twice is deterministic — it depends only on the
  already-persisted parent and root, not on submission order of unrelated
  events.
- **Versioning/compatibility.** No version negotiation exists for the marker
  convention itself; a client either sends valid marked `e` tags or does not.
  Buzz's own compatibility guarantee is at the read side: `get_thread_replies`
  still accepts a bare 8-byte (timestamp-only) pagination cursor for
  backward compatibility, though the composite form is preferred.

## Boundary

This node does not describe:
- **A single Nostr event kind's own wire contract** (kind number, full tag
  shape, content semantics) — e.g. kind 9's own contract as a NIP-29 group
  chat message. This node describes the cross-cutting threading convention
  that kind 9 (and its siblings) carry, not kind 9's node in full; no
  event-kind node for kind 9 is merged in this corpus yet to `references`.
- **The global kind:1 flat-reply model.** `buzz-sdk`'s `build_note` emits a
  single unmarked-semantics `["e", <id>, "", "reply"]` tag with no root
  distinction, no depth tracking, and no `thread_metadata` row — explicitly
  documented in code as a deferred, simpler mechanism, not full NIP-10
  threading.
- **A full parameter-by-parameter API catalogue** of every field on every
  request/response shape touched (`POST /query`'s complete filter grammar,
  the full `thread_metadata` row schema) for domain-expert readers — this
  node names the operations and their contract, not an exhaustive reference.
- **Community/channel membership and write-gate authorization** — that
  pipeline runs before NIP-10 resolution and is shared by every event kind;
  it is not re-described here.

## Relationships

None declared. At the recorded revision, `origin/launchpad`'s corpus tree
contains no `interfaces/` subtree and no other node documenting an interface
or a specific event kind — the merged nodes (`architecture/*`, `standards/*`,
`templates/*`, `AGENTS.md`, `README.md`) are all architecture-principle,
corpus-governance, or template documents, not NIP-10-adjacent subject matter
this node could legitimately `references`, `implements`, or sit `part-of`.
This is the corpus's first `interfaces-events`-typed instance node. A future
kind-9 (NIP-29 group chat message) event-kind node, once merged, is the
natural target for a `references` edge from this node — not added here
because it does not exist yet.

## Scope and omissions

**This node covers** the NIP-10 `root`/`reply` marker convention as Buzz
implements it for channel-scoped messages: the shared parser and its
validity/resolution rules, the relay's client-submitted and relay-authored
ingest resolvers and their rejection taxonomy, the `thread_metadata` counters
and paginated read path, the outbound tag builder, the CLI operations that
send and view threaded replies, and the workflow condition variable derived
from reply status. It also documents one concrete point where Buzz's own
convention deviates from upstream NIP-10's own recommended text.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 9's (or any other threaded kind's) own full wire contract | A future event-kind node, not yet created |
| The global kind:1 flat-reply mechanism in full | Out of scope per this node's own Boundary section |
| Community/channel write-gate authorization preceding NIP-10 resolution | The relay's general auth pipeline, undocumented as a corpus node at this revision |
| Whether the `"reply"`-marker-for-direct-reply-to-root deviation from upstream's own recommended text should itself become a separate corpus decision/concept node | Not this issue's call — reported as fact, not escalated |

**Expected but not verified when this node was written:**
- The three NIP-10-specific tests in `e2e_nostr_interop.rs`
  (`test_nip10_thread_reply_creates_metadata`,
  `test_nip10_unknown_parent_rejected`, `test_nip10_root_mismatch_rejected`)
  are marked `#[ignore]` and were read as source evidence, not executed
  against a live Postgres/Redis-backed relay, during authoring.
- Whether any other consumer beyond the ones enumerated above (relay ingest,
  `buzz-workflow`, `buzz-cli`) reads NIP-10 markers through a path other than
  `buzz-core::nip10` was not exhaustively re-verified beyond the grep-based
  survey performed while gathering evidence for this node.
