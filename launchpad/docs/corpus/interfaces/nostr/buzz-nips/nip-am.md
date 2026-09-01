---
id: interfaces-nostr-buzz-nips-nip-am
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
  - statement: "docs/nips/NIP-AM.md is a draft, optional, relay-scoped Buzz-custom Nostr Implementation Possibility defining kind:44200 (\"Agent Turn Metric\"): a durable, regular (append-only, never-replaced), NIP-44-v2-encrypted event an agent publishes once per completed turn so its owner can account for token usage and estimated cost across harnesses without the relay learning what the agent did or what it cost."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AM.md:1-13"
  - statement: "buzz-core/src/kind.rs declares KIND_AGENT_TURN_METRIC as the constant 44200, with a doc comment restating the same tag contract (exactly one p tag for the owner, one agent tag equal to event.pubkey, no h tag, global storage, owner-scoped p-gated reads) as the spec and pointing back at docs/nips/NIP-AM.md."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:538-545"
  - statement: "buzz-core/src/agent_turn_metric.rs implements AgentTurnMetricPayload, TokenCounts, StopReason and PricingIdentity as the decrypted content-field payload, matching the spec's field set (harness, model, channelId, sessionId, turnId, turnSeq, timestamp, turn, cumulative, deltaReliable, stopReason, pricingIdentity); StopReason's custom Deserialize maps any unrecognized string to Unknown per the spec's forward-compatibility rule, and validate() rejects a non-finite or negative costUsd in either turn or cumulative before encryption and after decryption."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/agent_turn_metric.rs:17-224"
  - statement: "encrypt_agent_turn_metric and decrypt_agent_turn_metric use the shared NIP-44 v2 helpers (encrypt_observer_payload / decrypt_observer_payload) already used for NIP-AO telemetry, keyed on (agent_keys, owner_pubkey), and both call payload.validate() so an invalid costUsd cannot be published or accepted as decrypted."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/agent_turn_metric.rs:193-224"
  - statement: "buzz-relay's ingest handler validates the public (unencrypted) envelope of a kind:44200 event before touching ciphertext: exactly one p tag of 64 lowercase hex chars, exactly one agent tag of 64 lowercase hex chars, and no h tag, rejecting violations with an `invalid: ...` message from IngestError::Rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1873-1929"
  - statement: "After the envelope check, ingest.rs performs an async ownership lookup (state.db.is_agent_owner(community, agent_pubkey, owner_pubkey)) and rejects the event with IngestError::AuthFailed(\"restricted: agent-turn-metric `p` tag must be the registered owner of this agent\") when the p tag does not name the event's registered owner -- tag matching alone is not sufficient, matching the spec's explicit warning."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2733-2767"
  - statement: "A unit test (agent_turn_metric_is_global_only_and_in_scope_allowlist) asserts kind:44200 is a global-only kind (is_global_only_kind true), does not require an h-tag channel scope, and requires Scope::MessagesWrite -- confirming the ingest-side authorization contract in code, not only in the spec's prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3930-3946"
  - statement: "Read-side gating is enforced by reader_authorized_for_event (called from event_visible_to_reader, which every read surface -- WS REQ/COUNT/fan-out and the HTTP bridge -- is documented to call) and by filter_can_match_result_gated_kinds / result_gated_count_safe_for_pushdown, which force the COUNT handler onto a per-event fallback for kind:44200 so an existence count cannot leak private event activity to a non-owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1300-1376"
  - statement: "A unit test (agent_turn_metric_requires_p_tag_even_with_ids) confirms that an explicit {kinds:[44200], ids:[...]} filter is denied for a non-owner even when the event id is known, that the kindless-ids exemption still applies at the filter-authorization gate but is closed at the result level by reader_authorized_for_event, and that a filter scoped by #p to the authenticated owner (with or without ids) is allowed -- matching the spec's requirement that knowing an event id MUST NOT grant access to kind:44200."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1914-1972"
  - statement: "An unauthenticated WebSocket subscriber is rejected with the notice text \"auth-required: authenticate before subscribing\" and a CLOSED message reading \"auth-required: not authenticated\" -- the actual wire prefix is lowercase auth-required:, not the literal string \"AUTH required\" the spec's prose uses to describe the same NIP-42 requirement."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:83-89"
  - statement: "The relay's search-tsv generated column and its migration exclude kind 44200 from full-text indexing: migration.rs asserts schema.sql's generated column contains \"kind IN (1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200)\", and an integration test (excluded_kinds_are_storage_level_unsearchable) inserts a kind:44200 event with a unique search token and asserts it never surfaces in a search_tsv match, unlike a kind:9 control event."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:895-902"
      - "crates/buzz-search/tests/fts_integration.rs:1150-1264"
  - statement: "buzz-acp's pool.rs implements the publisher: publish_agent_turn_metric builds an AgentTurnMetricPayload from harness-reported TurnUsage, encrypts it, and publishes a kind:44200 event tagged with p (owner) and agent (agent pubkey); it is a best-effort operation that returns silently when usage or the configured owner pubkey is absent, and logs (never propagates) an encryption failure, matching the spec's Publisher Behavior section (one event per completed turn, no publish when no usage was observed)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4602-4665"
  - statement: "node.schema.json's type enum has no dedicated 'interface' value; its closed enum member for both interface- and event-kind-shaped corpus nodes is the single combined value interfaces-events, per Feature #602's success criteria listing 'interfaces/events' as one item."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
  - statement: "No corpus node exists yet anywhere under launchpad/docs/corpus/interfaces/ on origin/launchpad, and no other buzz-nip corpus node (e.g. for NIP-AO, NIP-FI, NIP-PMA) is merged there either, so this node declares no relationships and instead prose-links its closest sibling, NIP-AO, by filename."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no interfaces/ path present at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "The relay does not implement a kind-44200-specific rate limiter distinct from any general per-connection/per-kind limiting; the spec's 60-events/minute-per-agent-pubkey figure is stated as a SHOULD recommendation, and no code path enforcing that specific figure for kind 44200 was found."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-AM.md:248-249"
      - "grep_repo('44200', paths='crates/buzz-relay/src/**/*.rs') -> no match combining '44200' with rate-limit logic, verified against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
    confidence: 0.7
---

# NIP-AM Agent Turn Metric: interface

This node documents Buzz's own custom Nostr Implementation Possibility, NIP-AM,
and its concrete implementation: the durable, owner-encrypted `kind:44200`
event agent harnesses publish once per completed turn to record token usage
and estimated cost. The two sides of this boundary are an **agent process**
(publisher, over the relay's WebSocket ingest path) and the **owner's client**
(subscriber/reader, over the relay's WebSocket or HTTP `/query` read paths),
exchanging one NIP-44-v2-encrypted Nostr event per turn. The authoritative
specification is [`docs/nips/NIP-AM.md`](../../../../../../docs/nips/NIP-AM.md)
in this repository; this node cites and confirms it against the concrete
implementation rather than restating its prose as a second, unchecked
description.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish one turn metric | `crates/buzz-acp/src/pool.rs#publish_agent_turn_metric` (`:4602-4665`) | Best-effort, at most one `kind:44200` event per completed turn; silently no-ops when no usage was observed or no owner pubkey is configured. |
| Encrypt/decrypt the payload | `crates/buzz-core/src/agent_turn_metric.rs#encrypt_agent_turn_metric` / `#decrypt_agent_turn_metric` | NIP-44 v2, `(agent_keys, owner_pubkey)`; both validate numeric fields and reject a negative/non-finite `costUsd`. |
| Ingest-time envelope + ownership validation | `crates/buzz-relay/src/handlers/ingest.rs#validate_agent_turn_metric_envelope` (`:1884`) and the ownership check at `:2733-2767` | Tag-shape check (exactly one `p`, one `agent`, no `h`) followed by an async `is_agent_owner` DB lookup; either failure rejects the publish. |
| Owner read (WebSocket REQ or HTTP `/query`) | `crates/buzz-relay/src/handlers/req.rs#event_visible_to_reader` / `#reader_authorized_for_event` (`buzz-core/src/filter.rs`) | Every read surface calls the same per-event gate; a non-owner reader never receives the event, `ids`-only filters included. |
| Owner read (COUNT) | `crates/buzz-relay/src/handlers/req.rs#filter_can_match_result_gated_kinds` / `#result_gated_count_safe_for_pushdown` (`:1300-1337`) | Forces the per-event fallback path for `kind:44200` COUNT filters unless the filter is already scoped to the authenticated reader's own `#p`, so an existence count cannot leak. |
| Kind allowlist / scope requirement | `crates/buzz-relay/src/handlers/ingest.rs` (test at `:3930-3946`) | `kind:44200` is global-only (no `h` tag), requires `Scope::MessagesWrite`. |

## Contract and stability

- **Wire format ownership**: the event kind, tag shape and content encryption
  scheme are owned by `docs/nips/NIP-AM.md` and `buzz-core/src/kind.rs` /
  `buzz-core/src/agent_turn_metric.rs`; this node does not re-derive them, it
  cites them.
- **Versioning/compatibility**: consumers MUST ignore unknown fields in the
  decrypted payload (forward compatibility per the spec and the payload
  struct's own doc comments), and an unrecognized `stopReason` value MUST be
  treated as `Unknown` rather than rejected — enforced in code by
  `StopReason`'s custom `Deserialize` impl
  (`crates/buzz-core/src/agent_turn_metric.rs:66-78`), which maps any
  unmatched string to `Unknown` instead of erroring.
- **Ordering/idempotency**: within one `sessionId`, `cumulative` values are
  ordered by `turnSeq`, not by `created_at` (only second-precision and
  ambiguous for same-second turns). A publisher that loses its `turnSeq`
  counter (e.g. harness restart) MUST start a new `sessionId` rather than
  reuse the old one with a reset counter. This node's evidence confirms the
  payload's shape carries the fields this ordering rule depends on
  (`sessionId`, `turnSeq`) but the ordering *discipline itself* (a consumer
  correctly refusing to diff across `sessionId`s) lives in consumer code
  outside this repository's relay/agent boundary and was not independently
  verified here — see *Scope and omissions*.
- **Error/rejection behavior**: publish-time rejections are synchronous
  `invalid: ...` (envelope shape) or `restricted: ...` (ownership) messages
  from the relay's ingest path; an unauthenticated publish or subscribe
  attempt is rejected with the relay's standard `auth-required: ...` NIP-42
  notice/CLOSED text, not the literal string `"AUTH required"` the spec's
  prose uses — the underlying NIP-42 authentication requirement is the same,
  the exact wire string differs from the spec's paraphrase.
- **Authentication/authorization**: publish requires the publishing pubkey to
  equal the `agent` tag and the DB-verified owner of that agent
  (`is_agent_owner`); read requires an authenticated (NIP-42) connection whose
  pubkey equals the event's `p` tag, enforced on every read path including
  explicit `ids` filters — verified by the `agent_turn_metric_requires_p_tag_even_with_ids`
  test.
- **Storage/search**: `kind:44200` is stored durably (regular event,
  append-only, never replaced) but deliberately excluded from full-text
  search indexing at the storage layer (`search_tsv` generated column),
  verified by both the migration assertion and a dedicated integration test.

## Example: valid publish and owner read

A completed turn with observed usage, published by the agent and later read
back by its owner:

```json
// Published event (ciphertext elided)
{
  "kind": 44200,
  "pubkey": "<agent_pubkey>",
  "created_at": 1751400663,
  "content": "<NIP-44 v2 ciphertext>",
  "tags": [["p", "<owner_pubkey>"], ["agent", "<agent_pubkey>"]],
  "sig": "..."
}
```

The owner recovers usage history with a `#p`-scoped filter, per the spec's
Client Behavior section and mirrored by the relay's own COUNT-pushdown-safety
check: `{"kinds": [44200], "#p": ["<owner_pubkey>"], "since": <window_start>}`.
Decrypted, the content resolves to an `AgentTurnMetricPayload` with `harness`
and `timestamp` required and every other field optional/nullable per
`crates/buzz-core/src/agent_turn_metric.rs:106-160`.

## Example: rejected publish (envelope and ownership failures)

- **Envelope shape failure**: an event carrying an `h` tag, more than one `p`
  tag, or an `agent` tag not equal to `event.pubkey` is rejected by
  `validate_agent_turn_metric_envelope` before any DB lookup runs, with an
  `invalid: ...`-prefixed message
  (`crates/buzz-relay/src/handlers/ingest.rs:1884-1929`).
- **Ownership failure**: an otherwise well-formed event whose `p` tag names a
  pubkey that is not the registered owner of `event.pubkey` is rejected with
  `restricted: agent-turn-metric \`p\` tag must be the registered owner of
  this agent` (`crates/buzz-relay/src/handlers/ingest.rs:2762-2767`).
- **Unauthorized read**: a filter `{"kinds": [44200], "ids": ["<id>"]}` from a
  reader who is not the event's `p`-tagged owner is denied even though the
  `ids` exemption applies to other p-gated kinds — verified by
  `agent_turn_metric_requires_p_tag_even_with_ids`
  (`crates/buzz-relay/src/handlers/req.rs:1917-1941`).

## Boundary

This node does not describe:
- A field-by-field, domain-expert-depth catalogue of every
  `AgentTurnMetricPayload` field's exact JSON shape beyond what is needed to
  confirm the spec against code — the full field list lives in
  `docs/nips/NIP-AM.md` and the struct doc comments in
  `crates/buzz-core/src/agent_turn_metric.rs`, which this node cites rather
  than re-encodes.
- NIP-AO (`kind:24200`, ephemeral session telemetry) or NIP-FI (agent
  delegation) — related but distinct Buzz-custom NIPs. NIP-AM shares its
  encryption and tag-scoping approach with NIP-AO but is durable rather than
  ephemeral, and MUST NOT carry conversation content or tool-call frames (per
  `docs/nips/NIP-AM.md`'s Relationship to Other NIPs section). A corpus node
  for NIP-AO, if one is drafted, is this node's natural sibling; none is
  merged as of this node's recorded revision, so it is referenced here by
  filename (`docs/nips/NIP-AO.md`) rather than by a corpus `relationships`
  edge.
- The upstream, non-Buzz-authored Nostr protocol NIPs this spec builds on
  (NIP-01 event/signature format, NIP-42 relay authentication, NIP-09
  deletion, NIP-40 expiration, NIP-44 encryption) — those are external
  protocol specifications this repository implements but does not own or
  vendor under `docs/nips/`, and are out of scope for a node about Buzz's own
  custom extension.

## Relationships

Declared: none. Checked against `origin/launchpad`'s corpus tree at the
recorded revision (`650354eab8d41ab6ce1a71de079a6c6d95c69052`): no
`launchpad/docs/corpus/interfaces/**` node exists to link, and the four nodes
that are merged there (`corpus-agents`, `corpus-readme`,
`corpus-standard-confidence`, `corpus-standard-decision-references`) are all
governance/agent nodes about the corpus's own authoring rules, not
interface-shaped subject matter this node would `references`, `implements`,
or sit `part-of`. Sibling Buzz-custom NIP nodes (NIP-AO, NIP-FI, etc.) are not
merged either, so they are prose-linked by filename above rather than by a
`relationships` edge that would fail validation against `origin/launchpad`.

## Scope and omissions

**This node covers** the `kind:44200` wire contract (tags, encryption,
decrypted payload shape) as confirmed against both `docs/nips/NIP-AM.md` and
its concrete Rust implementation; publish-time and read-time authorization and
rejection behavior; storage and search-exclusion behavior; and the publisher
side in `buzz-acp`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A future dedicated event-kind-shaped corpus node for `kind:44200` (if the corpus later splits interface documentation from event-kind documentation) | Undecided — no such split exists in the corpus yet; see *OPEN* in this task's plan |
| NIP-AO, NIP-FI and other Buzz-custom NIP corpus nodes | Their own future tasks |
| The corpus's own front-matter contract and node lifecycle procedure | `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **Consumer-side ordering discipline** (a reader correctly refusing to diff
  `cumulative` values across different `sessionId`s, and correctly treating a
  decreasing counter as unknown rather than negative usage) is a MUST on
  consumers per the spec, but no consumer implementation in this repository
  was located and exercised end-to-end against that specific rule; the
  server/relay side (storage, gating, search exclusion) was verified, the
  client-side recomputation discipline was not.
- **The 60-events/minute-per-agent-pubkey rate-limit recommendation** in the
  spec's Relay Behavior section is a SHOULD, and no `kind:44200`-specific
  rate-limiting code path was found in `crates/buzz-relay`; whether a general
  per-connection or per-kind limiter elsewhere in the relay happens to cover
  this case was not independently confirmed.
- **NIP-42's own specification text** was not fetched from its upstream
  source in this task; the authentication behavior described above is
  confirmed from this repository's own code (the `auth-required:` notice
  text), not from re-reading NIP-42 itself.
