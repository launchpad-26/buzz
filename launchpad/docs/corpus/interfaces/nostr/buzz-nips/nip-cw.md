---
id: interfaces-nostr-buzz-nips-nip-cw
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
  - statement: "docs/nips/NIP-CW.md defines the channel window as a relay-computed, cursor-paged view of a channel's top-level timeline, served as ordinary signed Nostr events through an extended NIP-01 filter, adding no new endpoint and no envelope; it is tagged draft, optional, relay, and depends on NIP-01, NIP-11, NIP-29, and NIP-98."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-CW.md:1-19"
  - statement: "docs/bridge-channel-window.md is an older engineering document for the same surface, and its own header states that NIP-CW is now the canonical, standalone specification and that this document remains only as the ratified engineering contract and internal design record, with NIP-CW governing where wording differs."
    entry_class: FACT
    evidence:
      - "docs/bridge-channel-window.md:1-8"
  - statement: "The relay's HTTP bridge POST /query route is registered in the fixed route table with the comment \"Nostr HTTP bridge (NIP-98 auth)\", so window requests share the same NIP-98-authenticated surface as every other bridge query."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:71-73"
  - statement: "handle_channel_window_filter in crates/buzz-relay/src/api/bridge.rs serves one top_level: true filter on the bridge /query path, appending in order row events, the aux closure (include_aux), kind:39005 thread-summary overlays (include_summaries), and exactly one kind:39006 window-bounds overlay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:480-489"
  - statement: "extract_channel_from_filter returns None unless the filter's #h generic tag carries exactly one value that parses as a UUID; handle_channel_window_filter rejects a None result with an HTTP 400 and the message \"top_level requires exactly one #h channel\", which is how zero or multiple channels are rejected without an error that distinguishes an inaccessible channel from a nonexistent one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:235-243"
      - "crates/buzz-relay/src/api/bridge.rs:497-503"
  - statement: "The composite request cursor (until, before_id) is parsed by extract_before_id, whose BeforeId enum keeps \"present but malformed\" distinct from \"absent\" specifically because NIP-CW's cursor grammar requires a malformed value to reject the request rather than silently demote it to a half cursor or a head request; handle_channel_window_filter returns 400 for BeforeId::Malformed, and separately returns 400 when exactly one of until/before_id is present."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:253-273"
      - "crates/buzz-relay/src/api/bridge.rs:508-536"
  - statement: "kind:39005 (KIND_THREAD_SUMMARY) and kind:39006 (KIND_WINDOW_BOUNDS) are declared as constants 39005 and 39006 in buzz-core's kind registry, both in the parameterized-replaceable range (30000-39999), with doc comments describing their tag/content shape matching NIP-CW's Overlay Event Formats section."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:430-439"
      - "crates/buzz-core/src/kind.rs:865-866"
  - statement: "The default and maximum row budget for a channel-window request are the constants BRIDGE_WINDOW_DEFAULT_LIMIT = 50 and BRIDGE_WINDOW_MAX_LIMIT = 200, and handle_channel_window_filter clamps the requested limit to that maximum and floors it at 1 -- matching NIP-CW's stated recommendation of \"default 50, maximum 200, minimum 1\" for Buzz specifically."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:388-389"
      - "crates/buzz-relay/src/api/bridge.rs:540-544"
  - statement: "buzz-db's get_channel_window_with_session (and its get_channel_window convenience wrapper) fetch top-level rows in (created_at DESC, id ASC) keyset order, computing has_more from an internal limit+1 probe evaluated after all predicates, with the sentinel row dropped before reaching the wire -- matching NIP-CW's Relay Processing Algorithm steps 1-3."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:582-594"
      - "crates/buzz-db/src/store/thread.rs:1008-1060"
  - statement: "The top-level predicate implemented in SQL is \"tm.depth IS NULL OR tm.depth = 0 OR (tm.depth = 1 AND tm.broadcast = true)\", which is Buzz's storage-fallback treatment of pre-index events (unknown depth counts as top-level) combined with NIP-CW's Top-level Classification rule (depth 0, or depth 1 when broadcast)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:649-654"
  - statement: "The aux closure (include_aux) queries reactions (kind 7), deletions (kinds 5 and 9005), and edits (kind 40003) targeting the returned rows by #e tag as hop 1, then deletions targeting hop-1 event ids as hop 2, deduplicating by event id and dropping events the requester cannot access -- matching NIP-CW's Relay Processing Algorithm step 4."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:570-608"
  - statement: "Thread-summary (39005) overlays are appended only for rows carrying a thread_summary, and the window-bounds (39006) overlay is appended exactly once per served response with has_more and next_cursor drawn directly from the window's computed fields -- matching NIP-CW's Relay Processing Algorithm steps 5-6 and its kind:39005/kind:39006 wire formats."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:625-668"
  - statement: "e2e_nostr_interop.rs contains test_channel_window_rows_overlays_and_exact_multiple_exhaustion, an ignored end-to-end test asserting rows stay free of replies, thread summaries and reactions ride along, and 39006's has_more/next_cursor correctly chain pages to exhaustion including an exact-multiple final page."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1771-1776"
  - statement: "The same test file contains test_channel_window_rejects_half_cursor_and_client_overlay_kinds, an ignored end-to-end test asserting a half cursor (until without before_id) returns HTTP 400, a malformed before_id with no until returns HTTP 400, and client-submitted kind:39005/39006 events are rejected at ingest."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1914-1971"
  - statement: "Both cited e2e tests carry the #[ignore] attribute, meaning neither runs under a default cargo test invocation; this node was authored by reading their assertions, not by executing them."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1775-1776"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1919-1920"
  - statement: "git log --oneline -- docs/nips/NIP-CW.md shows exactly one commit, 62bb9fe8c, titled \"GUI read-model overhaul: server-assembled channel windows (Correct(tm) pagination + relay-signed bounds) (#1500)\", which is the same PR number NIP-CW.md's own Overlay Trust section references as enforcing its MUST-level structural checks."
    entry_class: FACT
    evidence:
      - "git_log_oneline(path='docs/nips/NIP-CW.md') -> 62bb9fe8c GUI read-model overhaul: server-assembled channel windows (Correct™ pagination + relay-signed bounds) (#1500)"
  - statement: "NIP-CW's Overlay Trust section states that the SHOULD-level checks of its Client Behavior step 5 (exact tag cardinality, runtime field-type validation) and cryptographically binding overlay signatures to the advertised NIP-11 identity are future hardening to be applied uniformly across relay-signed reads, not a current guarantee, and that under Buzz's authenticated-transport profile \"relay-signed\" is a TLS-origin claim rather than a client-verified cryptographic one."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-CW.md:186-189"
  - statement: "No directory named interfaces/ exists anywhere under launchpad/docs/corpus/ prior to this node, so no sibling buzz-nips interface node or event-kind node for kind 39005/39006 exists on origin/launchpad to declare a resolving relationships[].target against."
    entry_class: FACT
    evidence:
      - "find_no_directory('launchpad/docs/corpus/interfaces', at_commit='650354eab8d41ab6ce1a71de079a6c6d95c69052') -> no such path in the tree"
  - statement: "Issue #995's Definition of Done requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative spec representation, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#995 definition of done"
---

# Channel Window (NIP-CW): interface

This node documents the **channel window** extension: a `POST /query` filter
extension (`top_level: true`) on Buzz's relay bridge that returns a
cursor-paged, top-level-only view of a channel's timeline, together with two
relay-signed overlay event kinds. Two sides exchange this: a client (desktop,
CLI, or any Nostr-aware HTTP caller) sends an extended NIP-01 filter over
Buzz's NIP-98-authenticated HTTP bridge, and the relay returns a flat JSON
array of ordinary signed Nostr events -- rows, then an optional aux closure,
then optional thread-summary overlays, then exactly one window-bounds
overlay. The extension adds no new endpoint and no new envelope: a client
that ignores it receives the relay's standard filter behavior.

The authoritative specification is
[`docs/nips/NIP-CW.md`](../../../../../../docs/nips/NIP-CW.md). An older
engineering document, [`docs/bridge-channel-window.md`](../../../../../../docs/bridge-channel-window.md),
covers the same surface but explicitly defers to NIP-CW where the two
disagree. This node summarizes both against the implementing code; it does
not restate NIP-CW's full normative text, per this template's own guidance
against re-encoding an externally specified wire format from memory.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Window request (`top_level: true` filter) | `docs/nips/NIP-CW.md` §Request; `crates/buzz-relay/src/api/bridge.rs:489` (`handle_channel_window_filter`) | A standard NIP-01 filter plus `top_level`, `include_summaries`, `include_aux`, `until`, `before_id` fields, submitted to `POST /query`. Selects the top-level-only view for exactly one `#h` channel. |
| `kind:39005` thread-summary overlay | `docs/nips/NIP-CW.md` §Overlay Event Formats; `crates/buzz-core/src/kind.rs:435` (`KIND_THREAD_SUMMARY`); `crates/buzz-relay/src/api/bridge.rs:625-648` | One relay-signed, parameterized-replaceable event per returned row that has replies, carrying `reply_count`, `descendant_count`, `last_reply_at`, and up to 10 `participants`. |
| `kind:39006` window-bounds overlay | `docs/nips/NIP-CW.md` §Overlay Event Formats; `crates/buzz-core/src/kind.rs:439` (`KIND_WINDOW_BOUNDS`); `crates/buzz-relay/src/api/bridge.rs:649-668` | Exactly one relay-signed, parameterized-replaceable event per served window response, carrying the authoritative `has_more` fact and `next_cursor` for the next page. |
| Top-level classification (server-side predicate) | `docs/nips/NIP-CW.md` §Top-level Classification; `crates/buzz-db/src/store/thread.rs:649-654` | Determines which stored events are eligible window rows: depth 0 (not a reply), or depth 1 when explicitly `broadcast`; unknown depth (pre-index events) is treated as top-level. |

## Contract and stability

**Inputs/messages.** A window request is a standard bridge filter plus
extension fields: `kinds` (optional row-kind restriction), `#h` (required,
exactly one channel), `limit` (row budget only -- overlays and aux never
count against it), `top_level: true` (selects the window path; any other
value serves the filter as a normal filter), `include_summaries`,
`include_aux` (both boolean opt-ins, defaulting to `false` when absent or
non-boolean per `extension_flag`, `crates/buzz-relay/src/api/bridge.rs:285-286`),
and the composite request cursor `until` + `before_id` (both present or both
absent). `offset`/page-number pagination is never honored on this path.

**Outputs/responses.** The bridge's ordinary flat array of signed events:
rows first in keyset order, then the aux closure (if requested and
non-empty), then thread summaries (if requested), then exactly one bounds
overlay. Clients partition by `kind`, never by array position beyond row
ordering.

**Error/rejection behavior.** Zero or more than one `#h` channel: HTTP `400`
("top_level requires exactly one #h channel"), from `extract_channel_from_filter`
returning `None` for anything but a single parseable UUID
(`crates/buzz-relay/src/api/bridge.rs:235-243, 497-503`). A malformed
`before_id` (not exactly 64 hex characters): HTTP `400`, never silently
demoted to a head request (`crates/buzz-relay/src/api/bridge.rs:253-273,
508-521`). Exactly one of `until`/`before_id` present: HTTP `400`
(`crates/buzz-relay/src/api/bridge.rs:524-536`). An inaccessible or
nonexistent channel: no error at all -- the handler returns `Ok(())` with no
rows and no overlays appended (`crates/buzz-relay/src/api/bridge.rs:501-503`),
matching NIP-CW's §Access Scoping rule that an inaccessible channel must be
indistinguishable from a nonexistent one.

**Authentication/authorization.** `POST /query` is NIP-98-authenticated
(`crates/buzz-relay/src/router.rs:71-73`), the same bridge surface every
other query uses. Access scoping is evaluated before rows or overlays are
computed for any given channel.

**Versioning/compatibility.** Every extension field is additive to a
standard NIP-01 filter. NIP-CW's §Degradation states that a tolerant filter
parser serves the plain `kinds` + `#h` query when it does not recognize the
extension fields, and a strict parser may reject the filter outright --
both are safe, since neither produces a wrong-but-plausible top-level
timeline. `kind:39005`/`kind:39006` are relay-only at ingest: client-submitted
events of either kind are rejected (asserted by
`test_channel_window_rejects_half_cursor_and_client_overlay_kinds`, `crates/buzz-test-client/tests/e2e_nostr_interop.rs:1975` onward).

**Ordering/idempotency.** Rows are served in `(created_at DESC, id ASC)`
keyset order (`crates/buzz-db/src/store/thread.rs:582-594`). `has_more` is
computed from a `limit + 1` probe evaluated after every predicate
(deletion, top-level, kind filter), and is the *only* exhaustion authority --
NIP-CW and the implementing code both state row count proves nothing on an
exact-multiple final page. Overlays are synthesized per query and never
stored, so re-requesting the same cursor is idempotent at the row level but
regenerates overlays fresh each time.

**Valid example.** A head request for channel `<uuid>` with summaries and
aux enabled:

```jsonc
{
  "kinds": [9],
  "#h": ["<channel-id>"],
  "limit": 50,
  "top_level": true,
  "include_summaries": true,
  "include_aux": true
}
```

This shape, exercised end to end across multiple pages including an
exact-multiple final page, is what
`test_channel_window_rows_overlays_and_exact_multiple_exhaustion`
(`crates/buzz-test-client/tests/e2e_nostr_interop.rs:1776`) asserts: replies
stay out of rows, `kind:39005` and reactions ride along, and
`kind:39006.has_more`/`next_cursor` correctly chain pages to exhaustion.

**Failure example.** A half cursor -- `until` present without `before_id` --
on an otherwise valid window filter:

```jsonc
{
  "kinds": [9],
  "#h": ["<channel-id>"],
  "limit": 2,
  "top_level": true,
  "until": 1751500000
}
```

`crates/buzz-relay/src/api/bridge.rs:524-536` rejects this with HTTP `400`
("top_level cursor requires both until and before_id, or neither"), asserted
by `test_channel_window_rejects_half_cursor_and_client_overlay_kinds`
(`crates/buzz-test-client/tests/e2e_nostr_interop.rs:1920`), which also
covers a malformed `before_id` with no `until` and client-submitted overlay
kinds being rejected at ingest.

## Boundary

This node does not describe:
- **Kind 39005's or kind 39006's full independent wire contract**, as if
  each were its own event-kind node. No event-kind corpus node (per the
  `#1337` template) exists yet for either kind; this interface node
  describes them only as this window's overlays. Once such nodes exist,
  this node would `references` them rather than duplicate their content.
- **Thread reading.** NIP-CW is explicit that replies never appear as
  window rows and that fetching a thread's contents is out of scope; the
  existing `thread_cursor` bridge surface (see `docs/bridge-channel-window.md`
  §Client obligations) is a different interface, undocumented as its own
  corpus node as of this revision.
- **Changes to ingest, storage, or fan-out.** NIP-CW states this
  explicitly as a non-goal: rows are ordinary stored events, and overlays
  are computed per query and never stored.

## Relationships

Declared: none. `launchpad/docs/corpus/interfaces/` does not exist on
`origin/launchpad` at the revision this node was authored against, so no
sibling `buzz-nips` interface node and no event-kind node for kind
39005/39006 exists to be a valid `relationships[].target`. Per
`launchpad/docs/corpus/AGENTS.md` step 9, a target must resolve on the
branch being merged into, not merely in this worktree, so declaring an
edge to a node that does not yet exist there would be a hard validation
error in CI. The first sibling `buzz-nips` or event-kind node to merge is
the natural moment to add `references` edges back to this node.

## Scope and omissions

**This node covers** the channel-window filter extension on Buzz's HTTP
bridge (`top_level`, `include_summaries`, `include_aux`, the composite
cursor), its two relay-signed overlay kinds (39005, 39006), the top-level
classification predicate, and the request/response/error/auth/versioning/
ordering contract, grounded in NIP-CW's normative text and the implementing
Rust code.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 39005's / kind 39006's independent event-kind wire contract | A future event-kind node (per the `#1337` template), not yet drafted |
| The `thread_cursor` thread-reading interface | A future interface node, not yet drafted |
| Field-by-field, domain-expert-depth parameter cataloguing of the bridge's full filter surface | `#1346`/`#1532` (reference / API Reference gap), unresolved corpus-wide |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **Neither cited e2e test was executed.** Both
  `test_channel_window_rows_overlays_and_exact_multiple_exhaustion` and
  `test_channel_window_rejects_half_cursor_and_client_overlay_kinds` carry
  `#[ignore]` and do not run under a default `cargo test` invocation; this
  node was authored by reading their assertions against the relay code, not
  by running them against a live relay and Postgres/Redis.
- **NIP-CW's SHOULD-level Overlay Trust hardening is not yet a guarantee.**
  NIP-CW's own §Overlay Trust section states that exact tag-cardinality and
  runtime field-type validation, plus cryptographically binding overlay
  signatures to the advertised NIP-11 identity, are future hardening to be
  applied uniformly across relay-signed reads -- not a current guarantee --
  and that Buzz's authenticated-transport profile treats "relay-signed" as
  a TLS-origin claim rather than a client-verified cryptographic one. This
  node reports that distinction rather than treating the hardening as
  already shipped.
