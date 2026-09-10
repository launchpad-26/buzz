---
id: interfaces-websocket-count
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c703ddf33fcda09e2a8399480061c4bda08bf162."
    entry_class: FACT
    evidence:
      - "commit c703ddf33fcda09e2a8399480061c4bda08bf162"
  - statement: "A client sends a COUNT message as the JSON array [\"COUNT\", <subscription_id>, <filter>...], parsed by ClientMessage::parse into ClientMessage::Count { sub_id, filters }; the subscription id must be non-empty and at most 256 bytes (MAX_SUB_ID_LENGTH), and at most 10 filters (MAX_FILTERS_PER_REQ) are accepted, both enforced identically to REQ."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:8-12"
      - "crates/buzz-relay/src/protocol.rs:108-145"
  - statement: "connection.rs dispatches a parsed ClientMessage::Count to handlers::count::handle_count on a spawned task guarded by the same handler_semaphore concurrency permit REQ uses; if the permit cannot be acquired the connection receives a NOTICE (not a per-subscription CLOSED), because request_rejection_message only attaches a sub_id for the Req arm."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:618-638"
      - "crates/buzz-relay/src/connection.rs:645-650"
  - statement: "Before dispatch, enforce_ws_admission applies the same per-principal WsEvents rate-limit check to COUNT as to REQ; on rejection, request_rejection_message is called with sub_id=None for COUNT specifically (its match arm only extracts sub_id for ClientMessage::Req), so a rate-limited COUNT gets a bare NOTICE while a rate-limited REQ gets a CLOSED naming its subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:652-688"
  - statement: "handle_count requires an authenticated connection: if conn.auth_state is not AuthState::Authenticated, it sends CLOSED <sub_id> \"auth-required: not authenticated\" and returns before running any filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:18-39"
  - statement: "After auth, handle_count runs the same three gate checks WS REQ uses, in order: p_gated_filters_authorized (p-gated kinds -- gift wraps, member notifications, observer frames -- require the caller's own pubkey in a #p tag), engram_filters_authorized (agent-engram reads require authors=[self] or #p=[self]), and author_only_filters_authorized (author-only kinds require authors=[self]); each failure sends CLOSED <sub_id> with a \"restricted: ...\" message naming the specific rule and returns without executing the count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:41-64"
      - "crates/buzz-relay/src/handlers/req.rs:1182"
      - "crates/buzz-relay/src/handlers/req.rs:1239"
      - "crates/buzz-relay/src/handlers/req.rs:1395"
  - statement: "A COUNT whose filters name more than MAX_EXPLICIT_CHANNEL_VALUES (128) distinct #h channel values across all filters is rejected with CLOSED <sub_id> \"restricted: too many explicit channels\", via extract_channel_ids_from_filters_limited."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:42"
      - "crates/buzz-relay/src/handlers/req.rs:1099-1113"
      - "crates/buzz-relay/src/handlers/count.rs:66-81"
  - statement: "Channel scoping for COUNT mirrors WS REQ: the relay first computes the caller's accessible channels (state.get_accessible_channel_ids_cached), then narrows that set to the authenticated token's own channel_ids scope when the token is scoped, before counting -- so a scoped token cannot inflate a count with channels outside its own scope even though the underlying pubkey may be a member of more channels."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:83-102"
  - statement: "For each filter, handle_count chooses between an exact SQL-pushdown count (state.db.count_events_routed) and a bounded fallback (query + in-process post-filter) depending on whether the filter is fully representable in SQL, whether it can match author-only, shared-gated (kinds 30175/30178) or result-gated (kinds 44200/30622) kinds requiring per-event authorization the fast path cannot apply -- the same authorization-safety logic WS REQ's filter execution uses, so a fast COUNT never returns a number that includes an event the caller could not otherwise read."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:104-123"
      - "crates/buzz-relay/src/handlers/count.rs:169-240"
      - "crates/buzz-relay/src/handlers/count.rs:242-314"
  - statement: "The fallback (post-filter) path is bounded by COUNT_FALLBACK_CANDIDATE_LIMIT = 5000 candidate rows; if the candidate page returned by query_events_routed_bounded exceeds that limit, handle_count sends CLOSED <sub_id> \"restricted: count filter requires narrower constraints\" and increments the buzz_count_fallback_rejections_total metric instead of returning an inexact or partial count -- the relay never silently truncates a count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:828-840"
      - "crates/buzz-relay/src/handlers/count.rs:206-223"
      - "crates/buzz-relay/src/handlers/count.rs:280-297"
  - statement: "On success, the relay replies with the single frame [\"COUNT\", <sub_id>, {\"count\": <u64>}], produced by RelayMessage::count; on any database error mid-loop it instead sends CLOSED <sub_id> \"error: <db error>\" and stops processing remaining filters, so a COUNT reply is either one complete count frame or one CLOSED failure frame, never a partial count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:214-215"
      - "crates/buzz-relay/src/handlers/count.rs:199-205"
      - "crates/buzz-relay/src/handlers/count.rs:273-279"
  - statement: "This repository's own community/tenant-boundary threat model states the COUNT observation explicitly: 'O.WS.COUNT(sub_id, n) -- NIP-45 count (protocol.rs:213). n is a numeric channel: even under row confinement, a count touching non-B rows leaks A's cardinality. The rule: n is the count of B-labeled rows matching the filter, full stop.' -- i.e. the returned count is contractually scoped to the resolved community/tenant, not merely to channel membership within one community."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:237-258"
  - statement: "NIP-45 (event count queries), the protocol this message implements, is not present in buzz-relay's own advertised SUPPORTED_NIPS list (&[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]) served in the NIP-11 relay information document, even though the COUNT verb is implemented and reachable over the WebSocket connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
  - statement: "The upstream nostr-protocol/nips repository publishes NIP-45 ('Event Counts') as 45.md, confirmed present at the same pinned commit this corpus already cites elsewhere for NIP-01/NIP-29 (dabfcb2aaecf4fa374eda8b1232ab303a03f60ba) -- the authoritative machine/spec representation this WebSocket-transport framing implements."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/45.md"
  - statement: "A valid round trip exists in the integration test suite: test_persona_count_excludes_foreign_unshared connects as a foreign user, sends [\"COUNT\", sid, {kinds:[30175], authors:[author]}] as a raw WS frame, and asserts it receives RelayMessage::Count{count,..} with the unshared persona event excluded from the total -- exercising the fallback (shared-gated) path end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_persona.rs:782-847"
  - statement: "A failure example exists in the integration test suite: test_ws_count_returns_zero_for_other_users_reminders sends a COUNT filtered to an author-only kind (30300, event reminders) naming another user as author, and asserts the relay responds with CLOSED <sid> containing \"restricted:\" rather than a count -- exercising the author_only_filters_authorized rejection path."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_event_reminder.rs:1005-1055"
  - statement: "Ordering/idempotency: COUNT is a stateless, non-subscribing request -- unlike REQ it never opens a live subscription and the relay never pushes further messages for a COUNT sub_id after its single reply, so there is no ordering guarantee to state beyond 'one request produces at most one reply frame.' This is reasoned from reading every return path in handle_count (each branch returns immediately after its one COUNT or CLOSED send, and no branch registers a subscription), rather than from a single explicit doc comment stating the non-subscribing property."
    entry_class: INFERENCE
    confidence: 0.8
    evidence:
      - "crates/buzz-relay/src/handlers/count.rs:18-317"
relationships:
  - type: part-of
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: architecture-flows-websocket-authentication
---

# WebSocket COUNT: interface

This node documents the WebSocket-transport framing of the relay's NIP-45 COUNT
message -- the client-to-relay `["COUNT", <subscription_id>, <filter>...]` request
and the relay's `["COUNT", <subscription_id>, {"count": n}]` (or `["CLOSED", ...]`
rejection) reply, exchanged over the same authenticated WebSocket connection REQ and
EVENT use. It is distinct from `interfaces/nostr/nip-45.md` (the protocol-level NIP-45
specification itself, tracked separately as issue #1015) and from
`interfaces/http/count.md` (the `POST /count` HTTP bridge endpoint that accepts the
same filter shape over HTTP instead of WebSocket, tracked as issue #978). At the time
this node was drafted, neither sibling node exists on `origin/launchpad` yet, so
`relationships` cannot target them; readers should cross-reference those files by
path once they merge.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Parse `["COUNT", sub_id, filter...]` | `crates/buzz-relay/src/protocol.rs:108-145` (`ClientMessage::parse`, `COUNT` arm) | Validates a non-empty `sub_id` (≤256 bytes) and at most 10 filters; produces `ClientMessage::Count { sub_id, filters }`. |
| Dispatch a parsed COUNT | `crates/buzz-relay/src/connection.rs:618-638` | Acquires a `handler_semaphore` permit and spawns `handlers::count::handle_count`. |
| Execute a COUNT | `crates/buzz-relay/src/handlers/count.rs:18` (`handle_count`) | Auth check, gate checks, channel-scope resolution, per-filter exact-or-fallback counting, single reply. |
| Format a success reply | `crates/buzz-relay/src/protocol.rs:214-215` (`RelayMessage::count`) | `["COUNT", sub_id, {"count": n}]`. |
| Format a rejection reply | `crates/buzz-relay/src/protocol.rs:209-210` (`RelayMessage::closed`) | `["CLOSED", sub_id, "<reason>: <detail>"]`. |
| Protocol this message implements | [NIP-45](https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/45.md) (event count queries) | Not in `buzz-relay`'s advertised `SUPPORTED_NIPS` (see evidence ledger) despite being implemented. |

## Contract and stability

- **Inputs.** `sub_id`: non-empty string, ≤256 bytes. `filters`: 0-10 NIP-01 filter
  objects (same shape REQ accepts), each optionally carrying an `#h` (channel) tag;
  the total `#h` values across all filters in one COUNT must not exceed 128
  (`MAX_EXPLICIT_CHANNEL_VALUES`).
- **Authentication/authorization.** COUNT requires an authenticated connection
  (NIP-42 AUTH already completed on this connection) -- an unauthenticated COUNT is
  rejected outright, never silently counted as zero. Beyond that, every
  authorization gate WS REQ enforces also applies to COUNT: p-gated kinds, engram
  reads, author-only kinds, and channel-membership/token-scope narrowing. A count is
  never permitted to reveal the *existence* of events the caller could not otherwise
  read -- shared-gated and result-gated kinds force the slower per-event fallback
  path specifically to preserve this property. The relay's own tenant-boundary threat
  model further scopes the returned number to the resolved community: `n` counts only
  rows labeled to the caller's community, "full stop."
- **Error/rejection behavior.** Every rejection is `CLOSED <sub_id> "<category>: <detail>"`
  with one exception: admission-rate-limit rejection on COUNT sends a bare `NOTICE`
  with no `sub_id`, because `enforce_ws_admission`'s rejection-message helper only
  attaches `sub_id` for the `Req` message arm, not `Count`. Rejection categories
  observed: `auth-required: not authenticated`, `restricted: p-gated kinds require #p
  tag matching your pubkey`, `restricted: agent-engram reads require authors=[self] or
  #p=[self]`, `restricted: author-only kinds require authors=[self]`, `restricted: too
  many explicit channels`, `restricted: count filter requires narrower constraints`
  (fallback candidate budget exceeded), and `error: <database error>`.
- **Exactness.** A COUNT reply is either a fully accurate `SQL COUNT(*)` (when the
  filter is fully SQL-pushable and needs no per-event authorization check) or an
  exact in-process count over a bounded candidate page (≤5,000 rows,
  `COUNT_FALLBACK_CANDIDATE_LIMIT`). If more than 5,000 candidate rows would be
  needed to compute an exact fallback count, the relay refuses to answer rather than
  return an approximate or truncated number.
- **Reply shape.** At most one success reply (`COUNT` frame with the summed total
  across all filters in the request) or one failure reply (`CLOSED`) per COUNT
  message; processing stops at the first database error.
- **Ordering/idempotency.** COUNT does not open a subscription -- unlike REQ it never
  produces further pushed messages after its single reply, so repeating an identical
  COUNT is idempotent in the sense that it re-executes the same read against current
  state and returns independently of any prior COUNT (INFERENCE; see evidence
  ledger).
- **Versioning/compatibility.** No COUNT-specific versioning scheme exists beyond
  NIP-45 itself; the message shape (`["COUNT", sub_id, filter...]` in,
  `["COUNT", sub_id, {"count": n}]` or `["CLOSED", ...]` out) is the same NIP-01-style
  envelope REQ and CLOSE use, and any change to it would be a breaking wire-protocol
  change to every NIP-45-aware client, not merely an internal refactor.

## Boundary

This node does not describe:
- NIP-45's own protocol-level specification (query semantics as defined by the NIP
  itself, independent of this relay's implementation) -- that is `interfaces/nostr/nip-45.md`
  (issue #1015), not yet merged.
- The `POST /count` HTTP bridge endpoint, which accepts the same filter shape but
  over HTTP rather than this WebSocket transport -- that is `interfaces/http/count.md`
  (issue #978), not yet merged.
- The WS REQ message's own contract (live subscriptions, EOSE, event delivery) --
  covered by `architecture-flows-websocket-connection` and the (not yet drafted)
  WS REQ interface node; COUNT shares its authorization plumbing but is a distinct,
  non-subscribing operation.
- A parameter-by-parameter catalogue of every NIP-01 filter field COUNT accepts --
  that is NIP-01's own specification, referenced rather than restated here.

## Relationships

- `part-of`: `architecture-containers-relay` -- this interface is one operation
  the relay container exposes.
- `references`: `architecture-flows-websocket-connection` -- the WebSocket
  connection lifecycle this message rides on.
- `references`: `architecture-flows-websocket-authentication` -- the NIP-42
  authentication flow this message's auth-required gate depends on.
- Not declared: `interfaces-nostr-nip-45` and `interfaces-http-count` -- both are
  drafted on unmerged branches (issues #1015 and #978 respectively) and do not yet
  resolve as ids on `origin/launchpad`; per `AGENTS.md`'s rule that relationship
  targets must resolve against the merge-target branch, this node prose-links them
  by filename above instead and should gain the edges once they merge.

## Scope and omissions

**This node covers** the WebSocket-transport COUNT message end to end: parsing,
dispatch, the auth-required gate, the three filter-authorization gates it shares
with WS REQ, channel-scope narrowing, the exact-vs-bounded-fallback counting
strategy and its 5,000-row exactness budget, the community-boundary scoping rule,
success/failure reply shapes, and one valid and one failure example drawn from the
integration test suite.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-45's own protocol-level specification | `interfaces/nostr/nip-45.md` (#1015, unmerged) |
| The HTTP `POST /count` bridge endpoint | `interfaces/http/count.md` (#978, unmerged) |
| The WS REQ message's own full contract | `architecture-flows-websocket-connection` + a future WS REQ interface node |
| Per-field NIP-01 filter catalogue | NIP-01 itself |

**Expected but not verified when this node was written:**
- Whether NIP-45's absence from `nip11.rs`'s `SUPPORTED_NIPS` list is a known,
  intentional gap or an oversight was not resolved by this task -- it is recorded
  as a FACT in the evidence ledger, not adjudicated here.
- Load/performance characteristics of the fallback path near its 5,000-row budget
  (e.g. typical latency) were not measured for this node; only the code's stated
  bound was verified.
