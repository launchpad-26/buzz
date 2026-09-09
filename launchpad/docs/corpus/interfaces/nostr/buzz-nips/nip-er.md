---
id: interfaces-nostr-buzz-nips-nip-er
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
  - statement: "NIP-ER (Event Reminder) defines `kind:30300` as an addressable event, keyed by `(pubkey, kind, d)`, whose content is NIP-44 ciphertext encrypted to the author's own public key; a public `not_before` tag tells supporting relays when the reminder is due, while the reminder target, note, and lifecycle status stay encrypted, so the relay learns *that* an author has a reminder due at a time but not what it is about."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md"
  - statement: "`node.schema.json`'s `type` enum has no separate `interface` value; interface-shaped and event-kind-shaped corpus subject matter share the single combined value `interfaces-events`, per PRD #602's success criteria and the interface template's own note on `type`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "`buzz-core::kind` declares `KIND_EVENT_REMINDER = 30300` and includes it in `AUTHOR_ONLY_KINDS`, the list of kinds whose stored events the relay must never reveal (existence, count, tags, content, schedule, or search matches) to anyone but the authenticated author."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:96-133"
  - statement: "`buzz-relay`'s ingest path parses a `not_before` tag as a decimal Unix-timestamp string containing only ASCII digits, with no sign, whitespace, decimal point, or leading zero except the literal `\"0\"`, using an exact integer parse (`u64::from_str`, never lossy float conversion) bounded to `0..=9_007_199_254_740_991` (`Number.MAX_SAFE_INTEGER`) -- matching the spec's own bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1949-1974"
      - "docs/nips/NIP-ER.md"
  - statement: "`validate_event_reminder` additionally rejects a `kind:30300` event with zero, more than one, or an empty `d` tag; rejects more than one `not_before` tag; rejects a `not_before` scheduled beyond a configurable horizon (`SPROUT_MAX_NOT_BEFORE_DELTA`, default 31,536,000 seconds / 1 year); and, when both `not_before` and an optional NIP-40 `expiration` tag are present, rejects `expiration <= not_before`. This function is wired into the generic ingest dispatch specifically for `KIND_EVENT_REMINDER`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1976-2050"
      - "crates/buzz-relay/src/handlers/ingest.rs:2770-2772"
  - statement: "A unit-test block in `ingest.rs` exercises `validate_not_before` and `validate_event_reminder` directly: accepting `\"0\"`, a typical timestamp, and exactly `9007199254740991`; rejecting a value one above that bound, a leading-zero string, an empty string, non-digit characters, and a `u64`-overflowing string; and, for full events, accepting a single valid `not_before`, accepting a missing `not_before` (terminal/bookmark form), accepting `expiration` strictly after `not_before`, and rejecting a missing/duplicate/empty `d` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:4416-4500"
  - statement: "On the WebSocket read path, `handle_req` closes any subscription attempted before NIP-42 authentication with `auth-required: not authenticated`; once authenticated, a filter that targets *only* author-only kinds (e.g. `{\"kinds\":[30300]}`) must carry `authors` containing solely the requester's own pubkey, or the subscription is closed with `restricted: author-only kinds require authors=[self]` (`author_only_filters_authorized`); for a mixed-kind filter that passes this gate, `is_author_only_event`/`event_visible_to_reader` silently omit any `kind:30300` event whose `pubkey` is not the requester's own from historical delivery and live fan-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:83-93"
      - "crates/buzz-relay/src/handlers/req.rs:211-241"
      - "crates/buzz-relay/src/handlers/req.rs:1339-1410"
  - statement: "The HTTP bridge's `/query` and `/count` endpoints require NIP-98 request signing and apply the same `author_only_filters_authorized` gate as the WebSocket path before executing a filter that targets only author-only kinds, so kind:30300 reads are equally author-gated over HTTP and WebSocket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1-4"
      - "crates/buzz-relay/src/api/bridge.rs:1037-1088"
      - "crates/buzz-relay/src/api/bridge.rs:1564-1607"
  - statement: "`buzz-relay`'s NIP-11 relay information document advertises this draft extension via `supported_extensions: [\"nip-er\", ...]` (never in `supported_nips`, since NIP-ER has no assigned upstream integer number), and advertises `limitation.due_delivery_mode: \"push\"` plus `limitation.max_not_before_delta` sourced from the same `SPROUT_MAX_NOT_BEFORE_DELTA` environment variable the ingest horizon check reads."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:100-141"
      - "crates/buzz-relay/src/nip11.rs:190-209"
  - statement: "`buzz-db`'s `extract_not_before` materializes a reminder's `not_before` tag into a dedicated `not_before` column on the `events` table at write time (`None` for any non-reminder event or a reminder with no `not_before` tag), which `query_due_reminders` then selects on directly: `DISTINCT ON (community_id, pubkey, d_tag)` ordered `created_at DESC, id ASC` (NIP-01 replacement ordering) where `not_before <= now`, `deleted_at IS NULL`, and `delivered_at IS NULL`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:192-204"
      - "crates/buzz-db/src/store/reminder.rs:38-88"
  - statement: "Due-reminder delivery is claimed atomically per event via `claim_due_reminder_with_stamp` (compare-and-set on `delivered_at`, scoped by `community_id` so the same Nostr event id across two communities cannot cross-claim) and rolled back via `release_due_reminder` if the subsequent publish side effect fails, giving cross-pod exactly-once-attempt delivery semantics."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reminder.rs:90-160"
  - statement: "`buzz-relay`'s `main.rs` runs a background scheduler loop (default 10-second interval via `SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS`, default 100-row batch via `SPROUT_REMINDER_SCHEDULER_BATCH_LIMIT`) that polls `query_due_reminders`, claims each row before publishing (claim-before-publish), and publishes the reminder event onto the resolved community's global Redis pub/sub topic for cross-pod fan-out to the author's own live WebSocket subscription -- the concrete implementation of the spec's push-mode due-time delivery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:769-891"
  - statement: "`crates/buzz-test-client/tests/e2e_event_reminder.rs` is an end-to-end test suite (30+ `#[tokio::test]` functions) exercising: acceptance and rejection of `not_before`/`expiration`/`d`-tag variants over the real ingest path; author-only query and count over both HTTP and WebSocket, including a same-request denial for a non-author caller; NIP-01 replacement semantics for a reminder address; and fan-out isolation confirming a non-author connection never receives another author's reminder event."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_event_reminder.rs:161-950"
  - statement: "The relay's concrete behavior matches the spec's push-mode profile rather than its lazy alternative: NIP-11 hardcodes `due_delivery_mode: \"push\"` and a background scheduler proactively publishes due reminders on a fixed interval, rather than only surfacing them on a later authenticated query."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs:140"
      - "crates/buzz-relay/src/main.rs:769-891"
      - "docs/nips/NIP-ER.md"
    confidence: 0.9
  - statement: "Issue #997 (this task) requires that inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency, a link to the authoritative spec, and at least one valid and one failure example are all present in the drafted node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#997 definition of done"
  - statement: "`crates/buzz-core/src/kind.rs` also declares an unrelated `KIND_STREAM_REMINDER = 40007`, a similarly-named but structurally distinct kind with no connection to NIP-ER's `kind:30300`; this node deliberately does not describe it, to keep the node to NIP-ER's own one concept."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:491"
---

# NIP-ER (Event Reminder): interface

This node documents Buzz's own custom NIP-ER extension: the `kind:30300` addressable
Nostr event that represents an encrypted, author-only reminder, plus the relay-side
enforcement and delivery machinery Buzz builds around it. Two sides exchange the
reminder across this boundary -- a Nostr client (author) and Buzz's relay -- over the
same WebSocket (NIP-01/NIP-42) and HTTP-bridge (NIP-98) surfaces every other event kind
uses; NIP-ER only narrows *who* may read the event and adds one scheduling behavior on
top. The wire format is a signed Nostr event; the authoritative machine-readable
description of that format is the spec document itself, `docs/nips/NIP-ER.md`, not this
node -- see *Boundary* below.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish/replace a reminder (`kind:30300`) | `docs/nips/NIP-ER.md` §Event/§Content; `KIND_EVENT_REMINDER` in `crates/buzz-core/src/kind.rs:102`; ingest validation in `crates/buzz-relay/src/handlers/ingest.rs:1976-2050` (`validate_event_reminder`) | Author publishes/replaces the addressable event `(pubkey, 30300, d)`. The relay validates only the public tag envelope (`d`, `not_before`, `expiration`); it never decrypts `.content`. |
| Subscribe to own reminders (WS `REQ`) | `crates/buzz-relay/src/handlers/req.rs:211-241` (`author_only_filters_authorized`), `:1339-1410` (`is_author_only_event`, `event_visible_to_reader`) | `{"kinds":[30300],"authors":["<own-pubkey>"]}`. Requires prior NIP-42 auth; any filter targeting only kind:30300 must have `authors=[self]`; a mixed-kind filter instead has non-author `kind:30300` rows silently omitted per event. |
| Query/count own reminders (HTTP `/query`, `/count`) | `crates/buzz-relay/src/api/bridge.rs:1037-1088`, `:1564-1607` | Same `author_only_filters_authorized` gate as the WS path, behind NIP-98 request signing instead of NIP-42. |
| Relay capability discovery | `crates/buzz-relay/src/nip11.rs:100-141`, `:190-209` | `GET /` with `Accept: application/nostr+json` returns a NIP-11 document with `supported_extensions` containing `"nip-er"`, plus `limitation.due_delivery_mode` (`"push"`) and `limitation.max_not_before_delta`. |
| Due-time delivery (relay-initiated) | `crates/buzz-db/src/store/reminder.rs:38-160` (`query_due_reminders`, `claim_due_reminder_with_stamp`, `release_due_reminder`); scheduler loop in `crates/buzz-relay/src/main.rs:769-891` | A background loop polls for reminders whose `not_before` has passed, atomically claims each one, and publishes it as a normal `EVENT` message to the author's own live subscription via Redis pub/sub fan-out. This is a due *signal*, not a new event -- it replays the same signed event that was stored. |
| Hard deletion | `docs/nips/NIP-ER.md` §State (NIP-09) | `kind:5` deletion event with an `a` tag `30300:<pubkey>:<d>` and `k` tag `30300`, handled by Buzz's existing generic NIP-09 deletion path (not NIP-ER-specific code). |

## Contract and stability

**Versioning.** NIP-ER is an unassigned Buzz-authored draft (`docs/nips/NIP-ER.md`
header: `draft` `optional` `relay`). The relay never advertises it in NIP-11
`supported_nips` -- only in `supported_extensions` as the string `"nip-er"`
(`crates/buzz-relay/src/nip11.rs:190-209`). If this draft ever receives an upstream
NIP number, the spec itself says implementations SHOULD migrate discovery to
`supported_nips` for that number; that migration is not implemented and is not
promised by any code cited here.

**Ordering/idempotency.** Reminder state follows ordinary NIP-01 addressable-event
replacement: the winning event for `(pubkey, 30300, d)` is the one with the highest
`created_at`, ties broken by lowest lexicographic `id`. `query_due_reminders`
(`crates/buzz-db/src/store/reminder.rs:43-88`) selects exactly that winner via
`DISTINCT ON (community_id, pubkey, d_tag) ... ORDER BY created_at DESC, id ASC`.
Due-time delivery is idempotent under retry across pods: `claim_due_reminder_with_stamp`
performs a compare-and-set write scoped to `community_id` so only one pod's publish
attempt proceeds per due row, and `release_due_reminder` rolls the claim back (using
the same caller-supplied stamp) if the publish side effect itself fails, allowing a
later tick to retry (`crates/buzz-db/src/store/reminder.rs:90-160`).

**Authentication/authorization.** Every `kind:30300` read, on both surfaces this repo
exposes, requires the requester to be the event's own author:
- WebSocket: NIP-42 AUTH is mandatory before any subscription opens at all
  (`auth-required: not authenticated`, `crates/buzz-relay/src/handlers/req.rs:83-93`);
  a filter naming only author-only kinds additionally requires `authors=[self]`
  (`restricted: author-only kinds require authors=[self]`,
  `crates/buzz-relay/src/handlers/req.rs:235-241`); a mixed-kind filter instead has
  unauthorized `kind:30300` rows silently dropped per-event
  (`crates/buzz-relay/src/handlers/req.rs:1339-1380`).
- HTTP: NIP-98 request signing is mandatory for `/query` and `/count`
  (`crates/buzz-relay/src/api/bridge.rs:1-4`), with the identical
  `author_only_filters_authorized` gate applied before filter execution
  (`crates/buzz-relay/src/api/bridge.rs:1037-1088`, `:1564-1607`).

This matches the spec's own requirement that supporting relays "MUST NOT reveal the
existence, count, tags, content, schedule, or search matches of a `kind:30300` event to
anyone except the authenticated event author" (`docs/nips/NIP-ER.md` §Relay behavior).

**Error/rejection behavior.** The ingest path (`validate_event_reminder`,
`crates/buzz-relay/src/handlers/ingest.rs:1976-2050`) rejects, before storage:
- a missing, duplicate, or empty `d` tag;
- a malformed `not_before` (non-digit characters, a disallowed leading zero, a value
  above `9007199254740991`, or more than one `not_before` tag on the event);
- a `not_before` scheduled further in the future than the configured horizon
  (`SPROUT_MAX_NOT_BEFORE_DELTA`, default one year);
- `expiration <= not_before` when both tags are present.

The relay never validates `.content` beyond confirming it decodes as a normal Nostr
event field -- decrypting and validating the NIP-44 plaintext (`target`, `status`,
`note` shape) is entirely a client-side responsibility per the spec, since the relay
by design cannot decrypt author-only content.

## Boundary

This node does not describe:
- **A different kind's own wire contract.** `kind:30300`'s own tag/content schema is
  fully specified in `docs/nips/NIP-ER.md` itself; this node cites that document and
  the code that enforces it rather than re-encoding the tag/content shape a second
  time. `KIND_STREAM_REMINDER = 40007` (`crates/buzz-core/src/kind.rs:491`) is an
  unrelated, similarly-named kind with no connection to NIP-ER and is out of scope for
  this node.
- **A full parameter-by-parameter API-reference catalogue.** The Operations table
  above points at defining sources; it does not enumerate every filter field or every
  possible relay `NOTICE`/`CLOSED` message string. See `#1346`/`#1532`'s
  reference/API-Reference gap (unresolved at the time this node was written) for that
  depth, should it ever exist.
- **The client-side decrypted content schema in depth.** `target`/`status`/`note` and
  their validity rules are specified in `docs/nips/NIP-ER.md` §Content; this node
  states only that the relay never sees them, not their internal shape.
- **The generic NIP-09 deletion mechanism itself.** Hard deletion of a reminder uses
  Buzz's existing generic deletion-request handling; that handling is not itself part
  of this interface and is not re-described here.

## Relationships

None declared. `origin/launchpad`'s corpus tree at the recorded revision contains no
interface-shaped or event-kind-shaped node this could `references` or sit `part-of`,
and this is the corpus's first `interfaces-events`-typed instance node, so there is no
sibling to point at either. A sibling, unmerged `buzz-nips` node documenting a
different NIP (for example NIP-GS, `docs/nips/NIP-GS.md`) may exist on another branch
in this same batch of tasks, but per `AGENTS.md`'s own rule a `relationships[].target`
must resolve against the branch being merged into, not the author's own worktree, so
that node is mentioned here by filename only, not as a relationship edge, until it is
actually merged.

## Scope and omissions

**This node covers** the `kind:30300` NIP-ER interface's operations (publish/replace,
author-only WS/HTTP read, capability discovery, relay-initiated due-time delivery,
hard deletion), its contract (versioning/draft status, NIP-01 ordering and cross-pod
delivery idempotency, author-only authentication/authorization on both surfaces, and
ingest-side rejection behavior), and its explicit boundary against the spec's own
content schema, the unrelated `KIND_STREAM_REMINDER` kind, and reference-depth
cataloguing.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The reminder's decrypted content schema (`target`/`status`/`note`) | `docs/nips/NIP-ER.md` §Content |
| Field-by-field, domain-expert-depth API-parameter cataloguing | `#1346`/`#1532` (reference / API Reference gap, undecided) |
| `KIND_STREAM_REMINDER` (40007) | not documented by this node; unrelated subject |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **Client-side behavior was not exercised end to end.** This node verifies the
  relay's own validation, authorization, and delivery code and its test suite; it does
  not verify any actual Buzz client (desktop/mobile/CLI) implementing the spec's
  client-behavior section (local `not_before` enforcement, the stateless notification
  profile, deduplication by event id and address). No such client-side reminder UI was
  found or searched for in this session.
- **The Redis pub/sub fan-out step itself was read, not executed.** The scheduler's
  publish call (`crates/buzz-relay/src/main.rs:858-887`) and the E2E fan-out-isolation
  test were both read; no live multi-pod deployment was stood up to observe cross-pod
  delivery directly in this session.
- **Whether an upstream NIP number has since been assigned to this draft** was not
  checked against the upstream `nostr-protocol/nips` repository; only this
  repository's own `docs/nips/NIP-ER.md` copy was read.

## Worked examples

**Valid: creating a pending reminder.** From `docs/nips/NIP-ER.md` §Worked Examples --
a `kind:30300` event with a fresh `d` tag, a valid `not_before`, and NIP-44 ciphertext
content. This event passes `validate_event_reminder` (exactly one non-empty `d` tag,
exactly one well-formed `not_before`, no `expiration` to compare against it) and is
accepted by the ingest path:

```jsonc
{
  "kind": 30300,
  "pubkey": "<author-pubkey>",
  "created_at": 1769990000,
  "tags": [
    ["d", "a3f8c2e1b4d79600e5d2f1a8c3b6094d"],
    ["not_before", "1770000000"],
    ["alt", "Encrypted reminder"]
  ],
  "content": "<nip44-ciphertext>",
  "id": "<event-id>",
  "sig": "<signature>"
}
```

**Failure: duplicate `not_before` tag.** `crates/buzz-relay/src/handlers/ingest.rs`'s
`validate_event_reminder` treats a second `not_before` tag on the same event as
malformed, mirroring the spec's own instruction (NIP-ER line 69) to collapse invalid
and duplicate `not_before` into one rejection reason. The relay rejects with
`invalid: malformed not_before` rather than storing either value; this is exercised
directly by `test_reminder_rejected_duplicate_not_before` in
`crates/buzz-test-client/tests/e2e_event_reminder.rs:193-215`:

```jsonc
{
  "kind": 30300,
  "pubkey": "<author-pubkey>",
  "created_at": 1769990000,
  "tags": [
    ["d", "a3f8c2e1b4d79600e5d2f1a8c3b6094d"],
    ["not_before", "1770000000"],
    ["not_before", "1770086400"],
    ["alt", "Encrypted reminder"]
  ],
  "content": "<nip44-ciphertext>",
  "id": "<event-id>",
  "sig": "<signature>"
}
```

**Failure: unauthorized read.** A caller who is not the event's author cannot observe
it at all -- neither its content nor its existence. Over WebSocket, a filter
`{"kinds":[30300],"authors":["<other-pubkey>"]}` issued by an authenticated-but-wrong
caller is closed with `restricted: author-only kinds require authors=[self]`
(`crates/buzz-relay/src/handlers/req.rs:235-241`), exercised by
`test_other_user_subscription_closed_for_author_only_kind_ws`
(`crates/buzz-test-client/tests/e2e_event_reminder.rs:629-678`); the equivalent HTTP
case is `test_other_user_cannot_query_reminders_http`
(`crates/buzz-test-client/tests/e2e_event_reminder.rs:492-528`).
