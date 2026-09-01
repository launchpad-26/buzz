---
id: layers-security-input-validation
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz_core::verification::verify_event checks a submitted event's ID (recomputed from pubkey, created_at, kind, tags and content) against the ID it arrived with, then checks its Schnorr signature, and is documented as CPU-bound so async callers must invoke it via tokio::task::spawn_blocking."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs:11-32"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's ingest_event function is the shared seam both the WebSocket EVENT handler and the HTTP POST /events bridge call after their respective transport-level authentication, so both transports run one validation pipeline rather than two independently maintained ones."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:608-792"
      - "crates/buzz-relay/src/api/bridge.rs:756-882"
  - statement: "Inside ingest_event, verify_event is called (wrapped in spawn_blocking, cloning the event via Arc to avoid a deep copy of up to 256 KB of content) before the timestamp, size, pubkey-match or scope checks run, so an event that fails signature/ID verification never reaches any later validation step."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1985-1999"
  - statement: "Immediately after signature verification, ingest_event rejects an event whose created_at timestamp differs from the server's current time by more than 900 seconds (MAX_TIMESTAMP_DRIFT_SECS, ±15 minutes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2005-2012"
  - statement: "ingest_event then rejects an event whose content field exceeds MAX_EVENT_CONTENT_BYTES, defined as 256 * 1024 (256 KiB), before any pubkey-match, scope or per-kind check runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2014-2020"
  - statement: "Several event kinds carry additional, stricter size and cardinality checks beyond the blanket 256 KiB content bound: kind:40008 diff events cap content at 61,440 bytes (60 KiB); buzz-db's D_TAG_MAX_LEN constant bounds any `d` tag to 1024 bytes; project events bound their `name` tag to PROJECT_NAME_MAX_LEN (256 bytes), `description` to PROJECT_DESCRIPTION_MAX_LEN (2048 bytes), and `buzz-channel`/`buzz-visibility` to PROJECT_METADATA_TAG_MAX_LEN (256 bytes each)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1274"
      - "crates/buzz-db/src/store/event.rs:155"
      - "crates/buzz-relay/src/handlers/ingest.rs:1533-1542"
      - "crates/buzz-relay/src/handlers/ingest.rs:1716-1753"
  - statement: "ingest.rs contains kind-specific structural validators that walk an event's raw tag list and reject it if required tags are missing, duplicated, or shaped wrong -- for example validate_engram_envelope requires exactly one `d` tag and exactly one `p` tag (rejecting zero or multiple of either), and further requires the `d` tag value be exactly 64 characters; validate_diff_event and the project-event validator apply comparable per-tag-name arity and shape rules."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1122-1152"
      - "crates/buzz-relay/src/handlers/ingest.rs:1055-1092"
      - "crates/buzz-relay/src/handlers/ingest.rs:1490-1540"
  - statement: "A raw tag is only inspected once it has at least two elements (tag name plus one value); ingest.rs's per-kind validators uniformly `continue` past any tag with fewer than two elements rather than treating it as a hard parse error, so a short tag is silently ignored rather than rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1122-1136"
      - "crates/buzz-relay/src/handlers/ingest.rs:1490-1497"
  - statement: "Before any of ingest_event's own checks run, both transports already reject input that does not parse into a well-typed event at all: the WebSocket path's ClientMessage::parse requires the raw frame to be a non-empty JSON array whose first element is a string, then deserializes the EVENT payload via serde into the `nostr` crate's typed Event struct (whose fields -- pubkey, id, sig -- are themselves hex/typed, so malformed hex or wrong-shaped JSON fails to deserialize); the HTTP bridge's submit_event_authed does the equivalent with serde_json::from_slice into the same typed Event after NIP-98 request authentication succeeds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:41-174"
      - "crates/buzz-relay/src/api/bridge.rs:756-882"
  - statement: "ClientMessage::parse additionally bounds REQ/COUNT subscription IDs to MAX_SUB_ID_LENGTH (256 bytes, matching the NIP-11 advertised max_subid_length) and bounds the number of filters per REQ/COUNT to MAX_FILTERS_PER_REQ (10), rejecting a message that exceeds either before any filter is evaluated against stored data."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:9-12"
      - "crates/buzz-relay/src/protocol.rs:41-174"
  - statement: "submit_event_authed's own comment states that a JSON parse error's Display string is deliberately never logged, because serde_json embeds the offending input verbatim in its error message and the router is documented there as allowing bodies up to 1 MiB, so logging the raw error would reflect attacker-controlled text of that size into a log line; the handler logs only the bounded, structured category/line/column instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:778-792"
  - statement: "The workflow webhook endpoint (POST /hooks/{id}) accepts an optional untyped JSON object as trigger context: if present, every top-level field's value is coerced to a string (via serde_json's Display for non-string values) and inserted into TriggerContext.webhook_fields with no documented size or field-count bound in that handler, in contrast to the bounded, typed validation ingest_event applies to Nostr events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1873-2047"
  - statement: "Media (Blossom) upload bytes are validated by a separate module, buzz-media's validation.rs, rather than by ingest_event's event-content pipeline, and the HTTP media routes carry their own tower_http RequestBodyLimitLayer sized from the relay's configured max_image_bytes/max_video_bytes -- a distinct enforcement point from the 256 KiB Nostr event-content bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/validation.rs"
      - "crates/buzz-relay/src/router.rs:34-46"
  - statement: "The size and structural limits documented here are exercised by unit tests colocated with the validators: verification.rs's own test module covers tampered-ID and tampered-signature rejection, and ingest.rs's test module includes boundary-value pairs such as project_envelope_rejects_name_too_long / project_envelope_accepts_name_at_max_length for PROJECT_NAME_MAX_LEN and the equivalent pair for PROJECT_DESCRIPTION_MAX_LEN."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs:34-71"
      - "crates/buzz-relay/src/handlers/ingest.rs:4959-4990"
  - statement: "The pipeline order documented here -- transport parse, then signature/ID verification, then timestamp drift, then content size, then structural/per-kind tag checks -- is this node's own reading of a single ~5,200-line function file rather than a rule stated anywhere as an explicit ordering contract, so a future refactor of ingest.rs could reorder these checks without violating any written invariant this node is aware of."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.7
---

# Input validation

Input validation is the set of checks Buzz applies to untrusted data --
Nostr event fields, WebSocket protocol frames, and HTTP request bodies --
before that data is trusted enough to authorize, store, or act on. It answers
"is this well-formed and within bounds," a narrower question than
authentication ("who sent this") or authorization ("are they allowed to").

## Boundaries -- what this node is not

This node does **not** cover:

- **Authentication and authorization.** NIP-42 WebSocket auth, NIP-98 HTTP
  request signing, and scope/membership checks are separate concerns that
  happen to run adjacent to (and in the shared ingest pipeline, after)
  validation. They belong to their own security corpus nodes.
- **Rate limiting / admission control.** `enforce_http_admission` and similar
  gates decide *whether this sender may act at all right now*, not whether
  the payload they sent is well-formed.
- **Media (Blossom) content validation.** Uploaded file bytes are validated
  by `buzz-media/src/validation.rs` under a separate body-size layer
  (`tower_http::limit::RequestBodyLimitLayer`, sized from the relay's
  `max_image_bytes`/`max_video_bytes` config) -- a distinct enforcement point
  from the Nostr event-content pipeline this node describes.
- **Git smart-HTTP and Blossom-specific protocol validation** -- out of scope
  here; those surfaces have their own request shapes.

A second concept discovered while writing this node -- the workflow
webhook's unbounded, untyped JSON body -- is recorded below as a boundary
observation, not folded into a claim about Nostr event validation.

## Where validation happens: the shared ingest seam

Both transports Buzz accepts events over -- the WebSocket `EVENT` message and
the HTTP `POST /events` bridge -- authenticate the *transport* first (NIP-42
for WebSocket, NIP-98 for HTTP), then call the same function,
`ingest_event` in `crates/buzz-relay/src/handlers/ingest.rs`, to validate and
admit the *event*. One pipeline, not two independently maintained ones.

Before `ingest_event` is even reached, each transport already requires the
raw input to parse into a well-typed structure:

- **WebSocket:** `ClientMessage::parse` requires a non-empty JSON array whose
  first element is a message-type string, then deserializes the event
  payload via `serde` into the `nostr` crate's typed `Event` struct. Malformed
  hex in `pubkey`/`id`/`sig`, or a wrong-shaped tag array, fails to
  deserialize at this step -- it never reaches `ingest_event` at all. `REQ`
  and `COUNT` messages are additionally bounded here: subscription IDs may
  not exceed `MAX_SUB_ID_LENGTH` (256 bytes, matching the relay's advertised
  NIP-11 `max_subid_length`), and a single `REQ`/`COUNT` may not carry more
  than `MAX_FILTERS_PER_REQ` (10) filters.
- **HTTP:** `submit_event_authed` verifies the NIP-98 request signature
  first, then parses the body with `serde_json::from_slice` into the same
  typed `Event`. A parse failure is reported back to the caller with a
  bounded, structured `category`/`line`/`column` -- the handler deliberately
  never logs `serde_json`'s own error `Display` string, because that string
  embeds the offending input verbatim and the route is documented as
  accepting bodies up to 1 MiB.

## The ingest_event pipeline, in order

Once a well-typed `Event` reaches `ingest_event`, validation runs in this
sequence (read directly from the function body; see the INFERENCE evidence
entry above for the caveat that this ordering is observed, not a stated
contract):

1. **Kind gating.** Relay-signed-only kinds (e.g. `AUTH`, membership
   notifications) and relay-only kinds are rejected outright before any
   cryptographic work is spent on them.
2. **Signature and ID verification.** `buzz_core::verification::verify_event`
   recomputes the event ID from `pubkey`, `created_at`, `kind`, `tags` and
   `content`, rejects a mismatch, then verifies the Schnorr signature. This
   is CPU-bound, so `ingest_event` runs it inside
   `tokio::task::spawn_blocking`, sharing the event via `Arc` rather than
   deep-cloning up to 256 KB of content into the blocking task.
3. **Timestamp drift.** The event's `created_at` must be within 900 seconds
   (`MAX_TIMESTAMP_DRIFT_SECS`, ±15 minutes) of the server's clock.
4. **Content size.** The event's `content` field must not exceed
   `MAX_EVENT_CONTENT_BYTES` (256 KiB). This is the blanket bound; several
   kinds apply a stricter one (below).
5. **Pubkey match.** The event's `pubkey` must match the authenticated
   identity, except for gift-wrap events (which carry a different pubkey by
   design).
6. **Scope / authorization** (out of scope for this node, noted only for
   ordering: it runs after, not instead of, the checks above).
7. **Per-kind structural validation.** Kind-specific functions walk the raw
   tag list and enforce shape rules -- see below.

## Size and cardinality limits

| Bound | Value | Applies to |
|---|---|---|
| `MAX_EVENT_CONTENT_BYTES` | 256 KiB | Every event's `content`, blanket bound |
| Diff event content cap | 61,440 bytes (60 KiB) | kind:40008 diff events |
| `D_TAG_MAX_LEN` | 1024 bytes | Any event's `d` tag |
| `PROJECT_NAME_MAX_LEN` | 256 bytes | Project event `name` tag |
| `PROJECT_DESCRIPTION_MAX_LEN` | 2048 bytes | Project event `description` tag |
| `PROJECT_METADATA_TAG_MAX_LEN` | 256 bytes | Project event `buzz-channel`/`buzz-visibility` tags |
| `MAX_SUB_ID_LENGTH` | 256 bytes | WS `REQ`/`COUNT` subscription IDs |
| `MAX_FILTERS_PER_REQ` | 10 | Filters per WS `REQ`/`COUNT` message |

## Tag structural validation

Beyond size, several kinds require specific tags to exist, exist exactly
once, and have a specific shape. For example, `validate_engram_envelope`
requires an agent-engram event to carry exactly one `d` tag and exactly one
`p` tag (rejecting both the absent and the duplicated case), and further
requires the `d` tag's value be exactly 64 characters. `validate_diff_event`
and the project-event validator apply comparable per-tag-name arity rules for
their own kinds.

A tag with fewer than two elements (no value after the tag name) is not
treated as a parse error by these validators -- it is silently skipped
(`continue`) rather than rejected. A caller relying on a tag being present
because the event round-tripped through `ingest_event` should not assume a
short or empty-valued tag was rejected; it may simply have been ignored.

## A boundary worth naming: the workflow webhook body

The workflow webhook endpoint (`POST /hooks/{id}`) accepts an optional
untyped JSON object as trigger context. If present, every top-level field's
value is coerced to a string and inserted into `webhook_fields`, with no
size or field-count bound documented in that handler -- unlike the bounded,
typed pipeline above. This is recorded here as an observed boundary of the
Nostr event-validation pipeline, not as a claim about the webhook surface's
own design, which would be its own node's concern.

## See also

- `crates/buzz-core/src/verification.rs` -- signature/ID verification.
- `crates/buzz-relay/src/handlers/ingest.rs` -- the shared ingest pipeline.
- `crates/buzz-relay/src/protocol.rs` -- WebSocket frame parsing and limits.
- `crates/buzz-relay/src/api/bridge.rs` -- HTTP bridge (`/events`, `/hooks/{id}`).
- `crates/buzz-media/src/validation.rs` -- media upload validation (separate surface).
