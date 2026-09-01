---
id: interfaces-nostr-nip-45
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f."
    entry_class: FACT
    evidence:
      - "commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "node.schema.json's type enum's single member covering both interface-shaped and event-kind-shaped corpus surfaces is interfaces-events, per PRD #602's combined 'interfaces/events' success-criteria item."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Upstream NIP-45 ('Event Counts') defines a client COUNT request as [\"COUNT\", <query_id>, <filters JSON>...] using NIP-01 filter syntax with multiple filters combined by OR, a relay COUNT response as [\"COUNT\", <query_id>, {\"count\": <integer>}], two optional response fields (approximate: a boolean flagging probabilistic counting, and hll: a 512-hex-character HyperLogLog register string for merging counts across relays), and states that a relay refusing a COUNT request returns [\"CLOSED\", <query_id>, <reason>]."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/3d71a4a78c376a5a71bf44708cd6b02c1773ae0b/45.md"
  - statement: "buzz-relay's protocol.rs parses a raw [\"COUNT\", sub_id, filter...] frame into ClientMessage::Count, rejecting a missing sub_id, a non-string sub_id, an empty sub_id, a sub_id over 256 bytes, and more than 10 filters — the identical limits and validation order REQ uses for its own sub_id and filter count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:108-145"
      - "crates/buzz-relay/src/protocol.rs:28-34"
  - statement: "buzz-relay's RelayMessage::count formats the relay's response as the JSON array [\"COUNT\", sub_id, {\"count\": count}], and emits no approximate or hll field — Buzz implements NIP-45's mandatory exact-count response only, not its optional HyperLogLog extension."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:213-216"
  - statement: "buzz-ws-client's parse_relay_message decodes a \"COUNT\" response into RelayMessage::Count { subscription_id, count }, reading only the count field of the response object and erroring via WsClientError::UnexpectedMessage if it is absent or not a u64 — confirming the client side of this contract reads no approximate/hll field either."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs:40-46"
      - "crates/buzz-ws-client/src/message.rs:147-162"
  - statement: "connection.rs dispatches ClientMessage::Count to handlers::count::handle_count inside a tokio task gated by AppState's handler_semaphore; when the semaphore is exhausted it sends a bare NOTICE (\"rate-limited: too many concurrent requests\") rather than the CLOSED-with-sub_id form the REQ path sends via request_rejection_message for the same condition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:618-638"
      - "crates/buzz-relay/src/connection.rs:645-650"
  - statement: "enforce_ws_admission treats ClientMessage::Count identically to ClientMessage::Req for admission purposes — both are checked against the same pubkey/is_agent admission path, distinct from ClientMessage::Event's separate path and from CLOSE, which skips admission entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:652-669"
  - statement: "handle_count requires the connection to be in AuthState::Authenticated before doing anything else, sending CLOSED(sub_id, \"auth-required: not authenticated\") and returning immediately otherwise — the same unconditional auth requirement NIP-11's relay_limitation.auth_required documents for REQ, EVENT, and COUNT alike."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:24-39"
      - "crates/buzz-relay/src/nip11.rs:120-123"
  - statement: "handle_count enforces p-gated, agent-engram, and author-only kind restrictions on every filter before executing any count, via the same p_gated_filters_authorized/engram_filters_authorized/author_only_filters_authorized helpers the WS REQ handler uses, closing the subscription with a restricted: ... reason on failure rather than silently omitting matching events from the count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:41-64"
  - statement: "handle_count narrows the caller's accessible channels to the authenticated token's own channel scope (when the token carries one) before counting, explicitly to prevent a scoped token from learning counts for channels outside its scope via the no-channel-filter SQL pushdown path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:83-102"
  - statement: "For each filter, handle_count chooses between a fast SQL COUNT pushdown (count_events_routed) when the filter is fully pushable and matches no shared-gated (30175, 30178) or result-gated (44200, 30622) kind needing per-event visibility checks, or a fallback path that queries a bounded candidate set via query_events_routed_bounded and post-filters per event with filters_match plus event_visible_to_reader — the same two-path shape and the same gated-kind exemptions the REQ handler applies to its own result stream."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:104-315"
  - statement: "The fallback path's candidate set is capped at COUNT_FALLBACK_CANDIDATE_LIMIT = 5,000 rows (apply_count_fallback_limit fetches 5,001); when count_fallback_exceeded finds more than 5,000 candidates, handle_count increments the buzz_count_fallback_rejections_total metric and closes the subscription with \"restricted: count filter requires narrower constraints\" instead of returning a partial or approximate count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:828"
      - "crates/buzz-relay/src/handlers/req.rs:831-840"
      - "crates/buzz-relay/src/handlers/count.rs:207-223"
      - "crates/buzz-relay/src/handlers/count.rs:280-296"
  - statement: "nip11.rs's SUPPORTED_NIPS constant lists 1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, and 56, and does not include 45, even though handle_count fully implements the NIP-45 COUNT command — the relay's NIP-11 self-description does not currently advertise COUNT support."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
  - statement: "relay_limitation() sets max_filters: Some(10) and max_subid_length: Some(256) in the advertised RelayLimitation, matching the exact numeric limits protocol.rs enforces for both REQ and COUNT parsing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:124-139"
      - "crates/buzz-relay/src/protocol.rs:9"
      - "crates/buzz-relay/src/protocol.rs:12"
  - statement: "buzz-relay's router.rs also registers POST /count on the HTTP bridge, handled by api::bridge::count_events / count_events_authed with NIP-98 request-signature auth instead of NIP-42 WebSocket auth, executing comparable channel-access-checked counting logic over HTTP; this is the same underlying count semantics exposed on a second transport, documented separately (see Boundary)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:74"
      - "crates/buzz-relay/src/api/bridge.rs:1499-1503"
  - statement: "A COUNT request's per-filter aggregation has no event ordering to guarantee (unlike REQ, which streams EVENT frames and terminates with EOSE) and handle_count performs no writes, so repeated identical COUNT calls are idempotent reads; this is reasoned from the handler's structure rather than from an explicit ordering/idempotency guarantee documented anywhere in code or NIP-45 itself."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:1-317"
  - statement: "launchpad/docs/corpus/templates/interface.md (id corpus-template-interface) is merged on origin/launchpad and prescribes this node's required sections (Interface description, Operations, Contract and stability, Boundary, Relationships, Scope and omissions) plus implements: corpus-template-interface as its preferred optional self-link."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "At this node's recorded revision, origin/launchpad's corpus tree carries no node under launchpad/docs/corpus/interfaces/ at all; the HTTP-count sibling node for issue #978 exists only on the unmerged branch task/978-interfaces-http-count, and no node for the WebSocket-count sibling task (issue #1020) exists anywhere in the corpus tree yet — so neither sibling id is a valid relationships[].target on the branch this node merges into."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/interfaces') -> no such path, at commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
      - "git_branch_contains(commit='2a2e2fef3b16775cb31c7b86c67e138ec05335bb') -> task/978-interfaces-http-count only, not origin/launchpad"
  - statement: "Issue #1015's Definition of done requires that inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, and ordering/idempotency (where applicable) all be defined in this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1015 definition of done"
---

# NIP-45 COUNT: interface

This node documents the boundary between a Nostr client (any WebSocket-connected
Nostr client, or `buzz-ws-client`'s typed decoder on Buzz's own clients) and
`buzz-relay`, across which the client sends a `COUNT` request and the relay
returns an aggregate event count, per upstream
[NIP-45](https://github.com/nostr-protocol/nips/blob/3d71a4a78c376a5a71bf44708cd6b02c1773ae0b/45.md)
("Event Counts"). The transport is the same WebSocket connection REQ and EVENT
use, carrying JSON-encoded Nostr protocol message arrays.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| COUNT request parse | `crates/buzz-relay/src/protocol.rs` `ClientMessage::parse`, `"COUNT"` arm (lines 108-145) | Parses `["COUNT", sub_id, filter...]` into `ClientMessage::Count { sub_id, filters }`, validating sub_id type/non-emptiness/length (max 256 bytes) and filter count (max 10). |
| COUNT dispatch | `crates/buzz-relay/src/connection.rs` (lines 618-638, 652-669) | Routes `ClientMessage::Count` to `handlers::count::handle_count` under a bounded concurrency semaphore, admitted through the same path as REQ. |
| COUNT handling | `crates/buzz-relay/src/handlers/count.rs` `handle_count` (whole file) | Requires NIP-42 auth, enforces gated-kind and channel-membership restrictions identical to the REQ handler, then aggregates per-filter counts via SQL COUNT pushdown or a bounded fallback scan. |
| COUNT response format | `crates/buzz-relay/src/protocol.rs` `RelayMessage::count` (lines 213-216) | Emits `["COUNT", sub_id, {"count": N}]`. |
| Client-side COUNT decode | `crates/buzz-ws-client/src/message.rs` (lines 40-46, 147-162) | `parse_relay_message` decodes a `"COUNT"` response into `RelayMessage::Count { subscription_id, count }`. |
| HTTP bridge (contrast, not this node) | `crates/buzz-relay/src/router.rs:74`, `crates/buzz-relay/src/api/bridge.rs:1499-1503` | `POST /count` exposes the same underlying count semantics over HTTP + NIP-98 auth instead of a WebSocket subscription — see `interfaces/http/count.md` (issue #978, not yet merged to `origin/launchpad`). |

## Contract and stability

- **Authentication.** NIP-42 WebSocket auth is required unconditionally.
  An unauthenticated `COUNT` gets `CLOSED(sub_id, "auth-required: not
  authenticated")` before any filter is inspected. NIP-11's advertised
  `relay_limitation.auth_required` documents this as always `true` for REQ,
  EVENT, and COUNT alike, independent of the separate REST API token toggle.
- **Authorization.** Gated-kind and channel-membership enforcement mirrors
  the REQ handler exactly: p-gated, agent-engram, and author-only kinds are
  checked per filter before any counting happens; shared-gated (30175,
  30178) and result-gated (44200, 30622) kinds bypass the fast SQL pushdown
  and go through per-event visibility checks instead, so a caller cannot use
  COUNT to learn about the existence of events REQ would hide from them. A
  caller's accessible channel set is narrowed to their auth token's own
  channel scope before counting.
- **Limits.** Max 10 filters and a 256-byte subscription ID, identical to
  REQ's limits and matching NIP-11's advertised `max_filters`/
  `max_subid_length`.
- **Fallback bound.** When a filter cannot be fully pushed to SQL `COUNT`,
  the relay scans at most `COUNT_FALLBACK_CANDIDATE_LIMIT` (5,000) candidate
  rows and post-filters them; exceeding that bound returns
  `CLOSED(sub_id, "restricted: count filter requires narrower constraints")`
  rather than a partial or approximate count.
- **Response shape.** Buzz implements only NIP-45's mandatory
  `{"count": <integer>}` response. It emits no `approximate` or `hll`
  field, so this relay does not support NIP-45's optional HyperLogLog
  probabilistic/mergeable counting extension; a caller should not expect
  those fields to appear.
- **Ordering/idempotency.** A COUNT response is a single aggregate with no
  event delivery order to guarantee (unlike REQ's EVENT-stream-then-EOSE
  shape); the handler performs no writes, so repeated identical COUNT calls
  are idempotent reads (an inference from the handler's structure, not an
  explicit documented guarantee — see the evidence ledger).
- **Versioning.** `buzz-relay`'s NIP-11 `SUPPORTED_NIPS` constant does not
  list 45, even though `handle_count` fully implements it — reported here
  as a fact about the relay's self-description, not as a defect to fix in
  this task (see *Scope and omissions*).

## Boundary

This node does not describe:
- A single Nostr event kind's own wire contract (kind number, tag shape,
  content semantics) — counted events are whatever kind a filter selects;
  individual kinds get their own event-kind-template node.
- The HTTP `/count` bridge endpoint's own contract (NIP-98 request-signature
  auth flow, HTTP status/error codes) — that is `interfaces/http/count.md`
  (issue #978), cited above for contrast only and not duplicated here. It
  is not yet merged to `origin/launchpad`, so no `relationships` edge to it
  is declared.
- A dedicated WebSocket-count node under issue #1020 — no such node exists
  in the corpus yet; if one is later scoped separately from this NIP-level
  document, that is a decision for that task, not this one.
- Field-by-field cataloguing of every gated-kind exemption inside
  `handlers/req.rs`'s helper functions — those are cited above to support
  the authorization claim, not exhaustively catalogued here.

## Relationships

- `implements: corpus-template-interface`

## Scope and omissions

**This node covers** the WebSocket NIP-45 `COUNT` command's request and
response shapes, its authentication/authorization requirements, its
sub_id/filter limits, the SQL-pushdown-versus-bounded-fallback counting
strategy and its rejection path, the absence of HyperLogLog support, and
the `SUPPORTED_NIPS` advertisement gap.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The HTTP `/count` bridge endpoint's own contract | `interfaces/http/count.md` (issue #978, unmerged) |
| A WebSocket-count-specific interface node, if one is later scoped separately from this NIP-level document | issue #1020 |
| Whether `SUPPORTED_NIPS`' omission of 45 is intentional or a drift bug | unresolved; no linked issue owns it as of this writing |
| A single event kind's own wire contract | the relevant event-kind-template node, once drafted |

**Expected but not verified when this node was written:**
- The upstream NIP-45 text was retrieved and summarized through a fetch
  step rather than the raw Markdown being quoted verbatim in this working
  session; the pinned GitHub link in the evidence ledger is the citation of
  record for anyone re-verifying the summary directly against the source.
- Whether any Buzz client (desktop, mobile, CLI) actually issues `COUNT`
  requests in production was not traced beyond confirming
  `buzz-ws-client` can decode the response — no call site invoking a COUNT
  request was located during this task's evidence pass.
