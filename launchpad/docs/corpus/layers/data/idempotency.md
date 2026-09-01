---
id: layers-data-idempotency
type: layers
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-db's event.rs states its deduplication model in its own module doc: \"Deduplication is application-layer: ON CONFLICT DO NOTHING,\" and both insert_event and insert_event_with_thread_metadata insert new events with `INSERT ... ON CONFLICT DO NOTHING`, returning a `was_inserted: bool` derived from `rows_affected() > 0`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:5"
      - "crates/buzz-db/src/store/event.rs:271"
      - "crates/buzz-db/src/store/event.rs:320-336"
      - "crates/buzz-db/src/store/event.rs:1160-1195"
  - statement: "The `events` table's primary key is `(community_id, created_at, id)`, where `id` is the Nostr event id -- a hash derived from the event's own content -- so resubmitting byte-identical event content collides on the same primary key and the `ON CONFLICT DO NOTHING` insert is a guaranteed no-op at the database layer, not merely an application convention."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-233"
  - statement: "When `insert_event_with_thread_metadata` reports `was_inserted == false`, the relay's WebSocket/HTTP ingest path returns `IngestResult { accepted: true, message: \"duplicate:\" }` immediately, before reaching the `is_side_effect_kind` dispatch that follows -- so a retried submission of an already-stored event is accepted without re-running fan-out, notifications, or other side effects."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2937-2979"
  - statement: "The existing corpus node documenting the event-ingestion flow independently describes this same behavior: \"Duplicate storage is a no-op, not a rollback ... a resubmitted event with an identical id simply does not re-run the counter/thread-metadata logic; it is reported `accepted: true, message: \\\"duplicate:\\\"`, which is a deliberate idempotent-retry behavior, not a failure path.\""
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md:327-331"
  - statement: "Inside the same transaction, thread-metadata counter updates (reply_count increments on parent/root rows) are gated behind the event insert's own `was_inserted` flag, so a duplicate event submission cannot double-count a reply even though the surrounding function is re-run in full on retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:1206-1230"
  - statement: "Buzz's media (Blossom) upload handler applies the same idea in an independent subsystem: uploaded bytes are keyed by their own `sha256` hash, and `process_buffered_upload` short-circuits the blob PUT -- explicitly commented \"Idempotent: short-circuit only if BOTH sidecar and blob exist\" -- when a matching sidecar and blob are already stored, re-uploading identical bytes without re-performing the write."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs:54"
      - "crates/buzz-media/src/upload.rs:94-98"
  - statement: "A short-circuited re-upload in that same handler still writes a fresh upload-event record (via `record_upload_event`) even though no blob PUT occurs, because the moderation pipeline's scan trigger is upload-event-driven and an invisible re-upload would let a previously-scanned blob's re-submission by a new uploader go unscanned."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/upload.rs:100-114"
      - "crates/buzz-media/src/upload_record.rs:4-8"
  - statement: "NIP-33 parameterized-replaceable events use a different mechanism from idempotent deduplication: `replace_parameterized_event` keys replacement on `(kind, pubkey, d_tag)` -- not on the event id -- and applies last-write-wins ordering by `created_at`, so a second event with new content at the same coordinate deliberately overwrites the first rather than being treated as a no-op duplicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs:546-582"
  - statement: "NIP-98 HTTP-auth replay protection takes the opposite response to a superficially similar problem: it rejects a reused event id outright via a TTL-scoped, community-scoped Redis seen-set (`try_mark`), rather than accepting the retry as a harmless no-op, because the property it protects is authentication freshness, not storage convergence."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs:1-27"
  - statement: "relationships.schema.json defines `references` as: \"source cites target as supporting context; no ownership or currency dependency implied,\" with an authored inverse edge `referenced-by`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json:40-44"
  - statement: "At the recorded revision, `architecture-flows-event-ingestion` is the only other corpus node under `origin/launchpad`'s `launchpad/docs/corpus` tree whose content substantively discusses idempotency; no node covering NIP-33 replaceable-event semantics, NIP-98 replay protection, or a `layers/data` overview exists yet, so no relationship targets those subjects."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md:327-331"
  - statement: "The media upload idempotency behavior is exercised by an integration test, `test_upload_idempotent`, which uploads identical bytes under two different signing keys and asserts the returned `sha256` and `url` are identical across both uploads."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs:212-253"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
---

# Idempotency

An operation is **idempotent** when performing it more than once, with the same
input, produces the same stored result as performing it exactly once, and does
not repeat the side effects (counters, fan-out, notifications, moderation
triggers) that a single successful run already produced. In Buzz's data layer,
idempotency is what lets a client, relay pod, or upstream retry a write after an
ambiguous failure (dropped connection, timeout, at-least-once delivery) without
worrying that the retry will duplicate data or double-fire anything downstream.

This is a property of specific write paths, not a blanket guarantee across the
whole data layer -- see *Comparison* below for two writes that look similar on
the surface but are deliberately **not** idempotent in this sense.

## Use cases

- **Safe client retry.** A client that submits an event and never receives (or
  times out waiting for) the relay's response cannot tell whether the write
  landed. Resubmitting the identical event is safe: the relay accepts it again
  (`accepted: true, message: "duplicate:"`) without creating a second copy or
  re-running reply-count updates.
- **At-least-once delivery from an upstream.** Any component that may redeliver
  a message it already sent (message queues, retried webhook calls, a reconnecting
  agent) can rely on the storage layer to absorb the duplicate rather than needing
  its own deduplication logic.
- **Content-addressed re-upload.** A media upload keyed by the content's own
  `sha256` hash is naturally idempotent: uploading the same bytes twice resolves
  to the same stored blob, and the handler short-circuits the second write while
  still recording the upload *event* so the moderation pipeline is not blinded to
  who resubmitted it. `test_upload_idempotent` verifies this at the integration
  level: two different signers uploading identical bytes get back the same
  `sha256` and `url`.

## Comparison

Three Buzz mechanisms respond to "I've seen something like this before" in three
different ways. Confusing one for another misdescribes what actually happens on
a retry:

| Mechanism | Trigger | Response | Where |
|---|---|---|---|
| Idempotent event/blob dedup (this node) | Identical event id, or identical content hash | Accept silently as a no-op; no re-run of side effects | `insert_event` / `insert_event_with_thread_metadata` (events), `process_buffered_upload` (media) |
| NIP-33 parameterized-replaceable events | Same `(kind, pubkey, d_tag)`, *new* content | Overwrite: last-write-wins by `created_at` | `replace_parameterized_event` |
| NIP-98 HTTP-auth replay protection | Same event id reused as an auth credential within the TTL window | Reject the request outright | `nip98_replay.rs` |

The first two both concern **storage of events already accepted as valid**; the
third concerns **whether to accept a request at all**. NIP-33 replacement is not
a duplicate-write no-op -- it deliberately changes stored state. NIP-98 replay
protection is not a dedup convenience -- it is a security control against reusing
a signed credential.

## Related resources

See the `references` relationship above to `architecture-flows-event-ingestion`,
which documents the full event-ingestion pipeline this node's event-layer
evidence is drawn from, including the transactional boundary around the
duplicate-detecting insert.

## Scope and omissions

**This document covers** what idempotency means for a write in Buzz's data
layer, the two concrete subsystems (event storage, media upload) that implement
it, and the boundary against two mechanisms it is easily confused with (NIP-33
replaceable-event last-write-wins, NIP-98 replay rejection).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-33 parameterized-replaceable-event semantics as their own concept | Not yet filed as its own corpus task at the recorded revision |
| NIP-98 replay protection as its own concept | Not yet filed as its own corpus task at the recorded revision |
| A `layers/data` overview or index node | Does not exist yet in the corpus |
| Idempotency guarantees (or their absence) in subsystems not inspected for this node -- e.g. push notification delivery, workflow webhook delivery, the audit hash-chain | Not verified when this node was written; flagged here rather than assumed |

**Expected but not verified when this node was written:** whether every
side-effect dispatch downstream of `insert_event_with_thread_metadata` (not only
the thread-metadata counters inspected directly) is itself gated on
`was_inserted`, versus only the specific `is_side_effect_kind` check cited above.
The ingest handler's early return before that dispatch point was verified by
reading the code directly; whether some other, less obvious side effect exists
elsewhere in the call graph was not exhaustively traced.
