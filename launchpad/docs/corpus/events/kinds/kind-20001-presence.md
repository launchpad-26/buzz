---
id: events-kinds-kind-20001-presence
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
  - statement: "crates/buzz-core/src/kind.rs declares `pub const KIND_PRESENCE_UPDATE: u32 = 20001;` with the doc comment 'Ephemeral: user presence update (online/away/offline).', under the file's own `// Ephemeral events (20000–29999) — Redis pub/sub only, never stored.` section header."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's module doc comment states it 'is the authoritative source for Buzz kind numbers,' and every constant is `u32` because NIP-01 specifies kind as an unsigned integer."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines `EPHEMERAL_KIND_MIN: u32 = 20000` and `EPHEMERAL_KIND_MAX: u32 = 29999`, documented 'Never stored', and `pub const fn is_ephemeral(kind: u32) -> bool { kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX }`. 20001 falls inside that inclusive range, so `is_ephemeral(KIND_PRESENCE_UPDATE)` evaluates to `true` by direct arithmetic on the constants as written -- no compile-time `assert!` pins this specific kind, unlike several other kinds in the same file, so this is read from the range function's own logic rather than from a dedicated assertion."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_PRESENCE_UPDATE is listed in the file's ALL_KINDS array, and a dedicated test, no_duplicate_kind_values, asserts every value in ALL_KINDS is unique -- so 20001 is confirmed not to collide with any other constant in the registry."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_PRESENCE_UPDATE is not a member of any of kind.rs's four named access-control sets -- AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS, RESULT_GATED_KINDS -- nor of is_relay_only_kind's match arms or is_command_kind's match arms, confirmed by reading each set's literal membership list directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "No file under docs/nips/ discusses presence; `ls docs/nips/*.md` lists 22 NIP-proposal files (NIP-AA through NIP-WP) and none is presence-related, and a case-insensitive grep for 'presence' across docs/nips/ returns zero matches. Kind 20001 therefore has no Buzz custom-NIP proposal document and no numbered community NIP governs it -- its only specification is kind.rs's doc comment plus the relay implementation itself."
    entry_class: FACT
    evidence:
      - "shell(ls docs/nips/*.md) -> 22 files, none presence-related"
      - "shell(grep -rli presence docs/nips/) -> no matches"
  - statement: "crates/buzz-relay/src/handlers/event.rs's handle_event dispatches on `is_ephemeral(kind_u32)`: ephemeral kinds (including 20001) are handled entirely inside handle_ephemeral_event and, per the function's own comment, 'bypass the pipeline entirely' -- they never reach ingest_event() (the persistent-event path in ingest.rs) or its scope allowlist, database write, or audit-logging calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Inside handle_ephemeral_event, a special-cased block keyed on `event_kind_u32(&event) == KIND_PRESENCE_UPDATE` parses `event.content`: if the raw content starts with '{', it is parsed as JSON and the `status` field is extracted (falling back to the raw string on parse failure); otherwise, if the raw content exceeds 128 bytes, it is truncated to the nearest UTF-8 character boundary at or before byte 128; otherwise the raw content is used as-is as the status string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "After extracting the status string, handle_ephemeral_event calls `state.pubsub.clear_presence(&conn.tenant, &auth_pubkey)` when the status equals the literal string 'offline', and `state.pubsub.set_presence(&conn.tenant, &auth_pubkey, &status)` for every other status value (including values outside the curated online/away/offline set -- both branches ignore the `Result` with `let _ =`, so a Redis failure here does not fail the WS EVENT acknowledgement)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-core/src/presence.rs's own doc comment states that its PresenceStatus enum (Online/Away/Offline, lowercase-serialized) is 'the curated set for structured APIs' and explicitly notes 'The WebSocket path (kind:20001) accepts arbitrary status strings for forward-compatibility' -- i.e. this enum constrains other (REST/MCP) surfaces, not the kind:20001 wire format itself, which accepts any string handle_ephemeral_event extracts."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/presence.rs"
  - statement: "A dedicated test in event.rs's test module, non_channel_kinds_do_not_require_h_tags, asserts `!requires_h_channel_scope(KIND_PRESENCE_UPDATE)` with the comment 'presence updates are global/ephemeral' -- confirming kind 20001 carries no channel/group-scoping (`h`) tag requirement, and requires_h_channel_scope's own match arms in ingest.rs list only stream-message, canvas, forum, NIP-29 admin, and huddle-lifecycle kinds, none of which include KIND_PRESENCE_UPDATE."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "handle_ephemeral_event calls `super::ingest::extract_channel_id(&event)` and branches on the result: since a kind:20001 event carries no `h` tag, extract_channel_id returns None, so presence updates always take the 'channel-less ephemeral events' branch -- publishing to `EventTopic::Global` via Redis pub/sub (using a nil-UUID sentinel routing key on the wire, per the function's own comment, that is converted back to `None` on the receiving relay node and never reaches the database) and fanning out directly to local WS subscribers via fan_out_event_to_local_subscribers with `channel_id: None`, with no channel-membership check performed for this branch (check_channel_membership is only called in the `Some(ch_id)` branch)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Neither branch of handle_ephemeral_event calls dispatch_persistent_event_inner, AuditService::log, or any function that writes to the audit_log table or a Postgres events table; those calls exist elsewhere in event.rs (used by the persistent-event dispatch path and exercised by unit tests that happen to reuse the KIND_PRESENCE_UPDATE constant as an arbitrary example kind for testing that generic dispatch/audit machinery), but that code path is never invoked for a kind:20001 event delivered over its actual WS ephemeral route."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
    confidence: 0.85
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's ingest_event rejects kind:20001 (and kind:GIFT_WRAP) submitted over HTTP transport with `IngestError::Rejected(\"invalid: kind {kind_u32} is only accepted via WebSocket\")`, via the check `if auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE)`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest.rs's required_scope_for_kind, whose own doc comment states it 'Returns Err for unknown kinds -- the relay rejects them,' has no match arm for KIND_PRESENCE_UPDATE and therefore falls through to that Err branch; two dedicated tests, ephemeral_kinds_not_in_scope_allowlist and presence_update_not_in_scope_allowlist, both assert `required_scope_for_kind(KIND_PRESENCE_UPDATE, ...).is_err()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "required_scope_for_kind is called only from within ingest_event (the persistent-event path), which kind:20001 never reaches per the FACT above about handle_event's is_ephemeral dispatch; the real authorization gate a kind:20001 WS submission passes through instead is handle_event's own `is_ephemeral(kind_u32)` branch, which rejects the EVENT with 'restricted: insufficient scope for ephemeral events' only when the connection's token scopes are non-empty AND do not contain Scope::MessagesWrite -- an unscoped (full-access) NIP-42 session is never blocked by this check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "handle_event requires the connection to be in AuthState::Authenticated before either the ephemeral or persistent branch runs (an unauthenticated EVENT is rejected with 'auth-required: not authenticated'), and separately requires `event.pubkey == auth_pubkey` unless the kind is KIND_GIFT_WRAP -- so a kind:20001 event must be self-signed by the authenticated connection's own key; a client cannot submit presence on another pubkey's behalf."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-pubsub/src/presence.rs's module doc comment states 'Presence tracking -- online/away status with TTL' and 'TTL is 3x the 60s heartbeat interval so a single missed heartbeat doesn't clear presence'; it defines `pub const PRESENCE_TTL_SECS: u64 = 180;`, and a dedicated test, presence_ttl_is_three_one_minute_heartbeat_windows, asserts `PRESENCE_TTL_SECS == 180` and `PRESENCE_TTL_SECS == 3 * 60`."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "set_presence issues a Redis `SET <presence_key> <status> EX 180` command (tenant- and pubkey-scoped key via presence_key), and clear_presence issues a Redis `DEL <presence_key>` command, documented 'Call on clean disconnect.' Neither function touches Postgres or any other durable store; presence state exists only in Redis and expires automatically after 180 seconds without a fresh update."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "No file under crates/buzz-search or crates/buzz-audit references KIND_PRESENCE_UPDATE, PRESENCE, or Presence at all (a case-sensitive grep for those tokens across both crates returns zero matching files) -- consistent with presence never being persisted, since buzz-search's Postgres full-text index and buzz-audit's hash-chain log both operate over stored events."
    entry_class: FACT
    evidence:
      - "shell(grep -rln PRESENCE crates/buzz-search crates/buzz-audit) -> no matching files"
  - statement: "crates/buzz-relay/src/api/bridge.rs's synthesize_presence intercepts a POST /query (or /count) request only when every filter in the request names exactly one kind, that kind is KIND_PRESENCE_UPDATE (20001) or KIND_PRESENCE_SNAPSHOT (40902), and the filter carries a non-empty `authors` list; it looks up Redis via `pubsub.get_presence_bulk(tenant, &all_pubkeys)` and, for each pubkey with a live entry, synthesizes a *new* event: `EventBuilder::new(Kind::Custom(KIND_PRESENCE_UPDATE as u16), status)` with a single `[\"p\", <pubkey_hex>]` tag, `created_at` set to the current time, signed with the relay's own keypair (`relay_keypair`) -- not the original submitter's key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Because presence is never persisted, a client querying for kind:20001 events never receives the original client-signed event back; every kind:20001 event returned from a query is a relay-signed synthetic snapshot of current Redis state, or the query returns nothing (synthesize_presence returns `Some(Ok(Vec::new()))` for pubkeys with no live entry, and a Redis lookup failure surfaces as an error response rather than a false-empty result, per the function's own comment about not letting a Redis outage look like an authoritative all-offline snapshot)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.9
  - statement: "KIND_PRESENCE_SNAPSHOT (40902) is a distinct kind constant in kind.rs, documented 'Bulk presence state (relay-signed sidecar)' and listed in is_relay_only_kind's match arms (client submission of this kind is rejected) -- it is a separate protocol citizen from kind:20001 and is not documented by this node, which covers kind:20001 only, per the corpus's one-node-one-idea rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Issue #872's Definition of done requires this node to state the event kind number/name, its persistent/replaceable/ephemeral classification, its required/optional tags and content and validation rules, its producers/consumers/authorization/persistence/fanout/search/audit treatment, and links to its NIP/spec, handler/registry, and conformance/tests -- the section structure of this node's body is built directly against that checklist."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#872 definition of done"
  - statement: "launchpad/docs/corpus/templates/event-kind.md (merged, id corpus-template-event-kind) requires an event-kind instance node to state `type: interfaces-events` explicitly in required section 1, and states that relationships.schema.json's `implements` type is the mechanism 'targeting corpus-template-event-kind itself, marking the node as a realized instance of this template.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "At the recorded revision, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists launchpad/docs/corpus/templates/event-kind.md (and no events/kinds/* files at all, confirming this is the first node in that subtree), so the `implements` edge to corpus-template-event-kind targets an id that is loadable on the branch this change will merge into, not merely on this worktree."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes templates/event-kind.md; no events/ subtree present"
relationships:
  - type: implements
    target: corpus-template-event-kind
---

# Event kind 20001: presence update

What a Nostr `kind:20001` event means in Buzz, who may send and receive one, and
what the relay does with it — for a reader implementing or reviewing code that
produces or consumes presence updates.

## 1. Kind identity

- **Name:** presence update.
- **Number:** `20001`.
- **Constant:** `KIND_PRESENCE_UPDATE` in `crates/buzz-core/src/kind.rs`
  (`pub const KIND_PRESENCE_UPDATE: u32 = 20001;`).
- **Type of this node:** `interfaces-events`, per `node.schema.json`'s corpus-surface
  enum and the event-kind template's own required section 1.
- **Shipped, not proposed.** The constant, its dedicated relay handling, and its unit
  tests already exist at the recorded revision; this is not a proposal for a kind
  that does not yet exist.

## 2. Referenced NIP

There is no numbered Nostr community NIP for presence, and no Buzz custom-NIP
proposal document exists under `docs/nips/` either — a directory listing of all 22
`docs/nips/NIP-*.md` files and a case-insensitive search for "presence" across that
directory both come back empty. Kind 20001 is a Buzz-only convention whose only
specification is `kind.rs`'s own doc comment plus the relay implementation this node
documents. If a formal specification is ever wanted, `docs/nips/NIP-AM.md` is this
repository's own worked example of the shape such a document would take.

## 3. Kind range and delivery classification

**Ephemeral**, per NIP-01's numeric ranges and `kind.rs`'s own `is_ephemeral`
helper: `EPHEMERAL_KIND_MIN..=EPHEMERAL_KIND_MAX` is `20000..=29999`, and 20001
falls inside it. `kind.rs`'s section comment above the constant states this
explicitly: "Ephemeral events (20000–29999) — Redis pub/sub only, never stored."
Ephemeral events are never persisted to Postgres and never gain a NIP-33-style
replacement key; each submission is a point-in-time signal.

## 4. Tag shape

**No tags are required.** Kind 20001 is channel-less: it carries no `h` (NIP-29
group) tag, and `requires_h_channel_scope(KIND_PRESENCE_UPDATE)` returns `false`
(asserted directly by the `non_channel_kinds_do_not_require_h_tags` test in
`crates/buzz-relay/src/handlers/event.rs`, with the comment "presence updates are
global/ephemeral"). The relay's own *response* to a presence query synthesizes a
single `["p", "<pubkey-hex>"]` tag naming the subject pubkey (see §6), but that tag
is added by the relay when answering a query — it is not required, or even
inspected, on the client-submitted event itself.

## 5. Content field semantics

`content` is a **plain string status**, extracted by
`handle_ephemeral_event` in `crates/buzz-relay/src/handlers/event.rs` as follows:

1. If the raw content starts with `{`, it is parsed as JSON and the `status`
   field's string value is used (falling back to the raw content if parsing or
   field extraction fails). This exists for a legacy JSON content shape,
   `{"status": "<value>"}`.
2. Otherwise, if the raw content is longer than 128 bytes, it is truncated to the
   nearest UTF-8 character boundary at or before byte 128.
3. Otherwise the raw content is used verbatim as the status string.

**Any string is accepted at the wire level** — `crates/buzz-core/src/presence.rs`'s
own doc comment is explicit that "The WebSocket path (kind:20001) accepts arbitrary
status strings for forward-compatibility," distinguishing it from the curated
`PresenceStatus` enum (`Online` / `Away` / `Offline`) that constrains Buzz's
*structured* REST/MCP presence APIs, not this event kind.

**One value is special-cased:** the literal string `"offline"` clears the presence
entry (see §6); every other value — including `"online"`, `"away"`, or any
forward-compatible custom string — sets it.

## 6. Access control and storage model

- **Producer authorization.** The submitting WebSocket connection must be
  `AuthState::Authenticated` (an unauthenticated `EVENT` is rejected with
  `auth-required: not authenticated`), and the event's `pubkey` must equal the
  authenticated connection's own pubkey — kind 20001 gets no gift-wrap-style
  exception, so a client can only publish presence for itself.
- **Scope requirement.** Ephemeral kinds (including 20001) are authorized by
  `handle_event`'s own blanket check, not by `ingest_event`'s per-kind scope
  allowlist: a connection whose token carries a *non-empty* scope set must include
  `Scope::MessagesWrite`, or the `EVENT` is rejected with `restricted: insufficient
  scope for ephemeral events`. An unscoped (full-access) session is never blocked
  by this check. Kind 20001 has no entry in `required_scope_for_kind`'s match arms
  at all — that function is part of `ingest_event`, the *persistent*-event pipeline,
  which ephemeral kinds never reach (`handle_event` dispatches on `is_ephemeral`
  before either path runs, and ephemeral events "bypass the pipeline entirely," per
  that dispatch code's own comment). Two tests, `ephemeral_kinds_not_in_scope_allowlist`
  and `presence_update_not_in_scope_allowlist`, both confirm
  `required_scope_for_kind(KIND_PRESENCE_UPDATE, ..)` returns `Err` — this documents
  that kind 20001 is absent from that allowlist, not that it is unreachable in
  practice; it is simply authorized by the other, ephemeral-specific gate instead.
- **Transport.** WebSocket **only**. `ingest_event` (the HTTP/persistent path)
  explicitly rejects kind 20001 (and `KIND_GIFT_WRAP`) with `invalid: kind 20001 is
  only accepted via WebSocket` whenever the request arrived over HTTP.
- **Storage.** Redis only, never Postgres. `set_presence` issues `SET
  <tenant+pubkey key> <status> EX 180`; `clear_presence` issues `DEL <key>`.
  `PRESENCE_TTL_SECS = 180` — three times the 60-second client heartbeat interval,
  so one missed heartbeat does not clear presence. There is no historical record: a
  presence value that is not refreshed within 180 seconds simply expires.
- **Fan-out.** Because the event carries no `h` tag, `extract_channel_id` returns
  `None` and the event always takes the channel-less branch: it is published to the
  Redis `EventTopic::Global` topic (using a nil-UUID sentinel routing key on the
  wire that other relay nodes translate back to "no channel" and that never reaches
  the database) and fanned out directly to local WebSocket subscribers with no
  channel-membership check — unlike a channel-scoped ephemeral event, which does
  check membership before fan-out.
- **Search and audit.** Neither `crates/buzz-search` nor `crates/buzz-audit`
  references presence at all. Because the event is never persisted, it is not
  indexed for full-text search and never appears in the audit hash-chain; the
  code paths that write to `audit_log` (exercised in some unit tests that reuse the
  `KIND_PRESENCE_UPDATE` constant purely as a convenient example kind for testing
  the unrelated persistent-dispatch/audit machinery) are not on the route a real
  kind:20001 WebSocket submission takes.
- **Read path is a live projection, not event replay.** A `POST /query` (or
  `/count`) request whose filters each name exactly one kind — `20001` or `40902`
  (`KIND_PRESENCE_SNAPSHOT`, the separate relay-signed bulk sidecar kind, out of
  this node's scope) — plus a non-empty `authors` list is intercepted by
  `synthesize_presence` in `crates/buzz-relay/src/api/bridge.rs`. It reads current
  Redis state via `get_presence_bulk` and constructs a **new, relay-signed** event
  per pubkey with a live entry: `content` is the current status string, tags are a
  single `["p", "<subject-pubkey-hex>"]`, `created_at` is "now," and the event is
  signed with the relay's own keypair — never the original submitter's signature.
  A pubkey with no live Redis entry is simply absent from the results (not
  returned as "offline"), and a Redis lookup failure surfaces as an error response
  rather than a false-empty result.

## 7. Worked example

A client publishing "online" over an authenticated WebSocket connection:

```json
{
  "id": "…",
  "pubkey": "3f0b...e2ac",
  "created_at": 1735689600,
  "kind": 20001,
  "tags": [],
  "content": "online",
  "sig": "..."
}
```

Clearing presence on clean disconnect:

```json
{
  "id": "…",
  "pubkey": "3f0b...e2ac",
  "created_at": 1735689610,
  "kind": 20001,
  "tags": [],
  "content": "offline",
  "sig": "..."
}
```

The legacy JSON content form, still accepted:

```json
{
  "id": "…",
  "pubkey": "3f0b...e2ac",
  "created_at": 1735689600,
  "kind": 20001,
  "tags": [],
  "content": "{\"status\":\"away\"}",
  "sig": "..."
}
```

A relay-synthesized response to `POST /query` with
`{"kinds":[20001],"authors":["3f0b...e2ac"]}` (illustrative; the relay's own
keypair signs this, not the original submitter's):

```json
{
  "id": "…",
  "pubkey": "<relay-pubkey>",
  "created_at": 1735689650,
  "kind": 20001,
  "tags": [["p", "3f0be2ac..."]],
  "content": "online",
  "sig": "..."
}
```

## 8. Versioning and supersession

None. Kind 20001 has not been renumbered; `kind.rs` records no prior number for it
(contrast `KIND_STREAM_MESSAGE_V2`'s comment recording its own history through
kinds 10002 then 40002 — presence carries no such note).

## 9. Relationships

This node declares one typed relationship: `implements` targeting
`corpus-template-event-kind` — this node is the realized instance of that merged
template, per `relationships.schema.json`'s definition of the type ("source is the
concrete realization of target"). No `depends-on` or `references` edge is declared
to any sibling event-kind or interface node: this is the first document under
`launchpad/docs/corpus/events/`, confirmed by `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus` showing no `events/` subtree at all at
the recorded revision, so no such sibling id exists to resolve against.

## Boundary

**Kind `40902` (`KIND_PRESENCE_SNAPSHOT`)** is a separate, relay-signed "bulk
presence state" sidecar kind — `is_relay_only_kind` rejects any client attempt to
submit it — and is named here only because `synthesize_presence` handles both
kinds together in one function. It is a distinct protocol citizen with its own
number, its own relay-only authorship rule, and (per the corpus's one-node-one-idea
rule) its own future corpus node, not this one.

**Consumer-facing operations built on top of kind 20001** (a `buzz-cli`
subcommand, a desktop presence indicator, an SDK builder) belong to an interface
node, which should reach this node with a `depends-on` relationship rather than
restating §§3–6 above.

## Scope and omissions

**This document covers** kind 20001's identity, classification, tag and content
shape, access control, storage, fan-out, and read-path behavior, grounded in
`crates/buzz-core/src/kind.rs`, `crates/buzz-relay/src/handlers/event.rs`,
`crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-pubsub/src/presence.rs`,
and `crates/buzz-relay/src/api/bridge.rs` at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 40902 (`KIND_PRESENCE_SNAPSHOT`), the relay-signed bulk-presence sidecar kind | Not yet filed as its own corpus task at the recorded revision |
| Any client-facing presence API surface (REST/MCP `PresenceStatus`, a CLI subcommand, a UI indicator) | A future interface-typed corpus node, per the event-kind template's own boundary section |
| The heartbeat client behavior that keeps a 180-second TTL alive in practice | Not inspected for this node — only the server-side TTL constant and its rationale comment were read |

**Expected but not verified when this node was written:**

- **No live WebSocket session was exercised end-to-end.** Every claim above is
  read from source and from the cited unit tests, not observed by running the
  relay and a client against each other.
- **Whether any client (desktop, mobile, CLI) actually sends the legacy
  `{"status":"..."}` JSON content form today, versus only the bare string, was not
  checked** — only that the relay still accepts both.
- **Whether `crates/buzz-test-client`'s conformance and E2E suites exercise these
  behaviors was not checked in depth.** `e2e_relay.rs` and
  `conformance_multitenant.rs` both reference `KIND_PRESENCE_UPDATE` (per a
  repository-wide search), but neither was opened deeply enough to cite
  individual test names beyond the ones already cited from `event.rs` and
  `ingest.rs`; a reader wanting end-to-end conformance coverage should open
  those two files directly.
