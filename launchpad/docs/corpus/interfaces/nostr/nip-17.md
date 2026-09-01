---
id: interfaces-nostr-nip-17
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
  - statement: "buzz-core/src/kind.rs declares KIND_GIFT_WRAP = 1059 with the doc comment 'NIP-17: Outer envelope for private DMs — hides sender, content, timestamp,' and lists it in ALL_KINDS."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:59-60"
      - "crates/buzz-core/src/kind.rs:650"
  - statement: "kind.rs's P_GATED_KINDS constant includes KIND_GIFT_WRAP among kinds whose stored events have '#p-bound read access — readable only by subscribers whose pubkey appears in the event's #p tag,' enforced at the filter layer by p_gated_filters_authorized and, for stored kinds, by a NULL search_tsv at the storage layer."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:144-167"
  - statement: "buzz-relay's ingest_event_inner (the shared ingest path for both WebSocket and HTTP transports) rejects kind:1059 (and kind:KIND_PRESENCE_UPDATE) submitted over HTTP with 'invalid: kind {kind_u32} is only accepted via WebSocket' — gift wraps may only be submitted over the WebSocket transport."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2192-2196"
  - statement: "ingest_event_inner computes is_gift_wrap = kind_u32 == KIND_GIFT_WRAP and exempts gift wraps from the rule that the event's pubkey must equal the authenticated identity's pubkey ('if event.pubkey != *auth.pubkey() && !is_gift_wrap'), with a comment noting the classification is based on the authenticated principal rather than the envelope signer because 'NIP-59 gift wraps deliberately use an unrelated ephemeral pubkey.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2109-2111"
      - "crates/buzz-relay/src/handlers/ingest.rs:2242-2243"
  - statement: "The WebSocket connection entry point handle_event in handlers/event.rs performs the identical pubkey-mismatch exemption ('if event.pubkey != auth_pubkey && !is_gift_wrap') before delegating persistent events into ingest_event, with a comment that this early check 'must run before both ephemeral and persistent branches' since ephemeral events bypass ingest_event entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:655-660"
  - statement: "ingest.rs's required_scope_for_kind maps KIND_GIFT_WRAP (alongside KIND_DELETION, KIND_REACTION and several stream/forum kinds) to Scope::MessagesWrite, so a caller's auth token must carry that scope to submit a gift wrap."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:462-484"
  - statement: "event.rs's post-store dispatch explicitly excludes kind:1059 from workflow-engine triggering ('!buzz_core::kind::is_workflow_execution_kind(kind_u32) && ... && kind_u32 != KIND_GIFT_WRAP'), so a stored gift wrap never fires a community workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:526-531"
  - statement: "req.rs's p_gated_filters_authorized rejects a REQ filter that can match a P_GATED_KINDS member (including kind:1059) unless the filter's #p tag values are non-empty and every value equals the authenticated reader's own pubkey hex; an ids-present filter loses this #p requirement only for kinds not in an explicit no-exemption list, which does not include KIND_GIFT_WRAP."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1182-1210"
  - statement: "push_runtime.rs's push_filter_authorized_for_event re-applies the same #p ownership check at push-lease match time specifically for kind:1059, with a doc comment stating it is the 'match-time counterpart of REQ's filter-level #p authorization gate' because 'kind 1059 is globally stored and leaks recipient activity through wake timing, so a lease may only match gift wraps addressed to its own author.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs:317-334"
  - statement: "buzz-search's fts_integration.rs test excluded_kinds_are_storage_level_unsearchable inserts a kind:1059 event and asserts it does not surface via NIP-50 FTS search, with a comment that the migration's generated search_tsv column 'emits NULL for excluded kinds' so 'a search_tsv @@ query probe never matches' — a storage-level, not merely filter-level, privacy guarantee."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs:1149-1173"
      - "crates/buzz-search/tests/fts_integration.rs:1192-1199"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs's module doc comment states its coverage includes 'NIP-50 search, NIP-10 threads, NIP-17 gift wraps, and DM discovery,' and its four test_nip17_* tests exercise: acceptance despite an ephemeral signing key different from the auth key (test_nip17_gift_wrap_accepted), CLOSED rejection of a kinds:[1059] subscription with no #p filter (test_nip17_gift_wrap_requires_p_filter), successful delivery of a gift wrap to the recipient named in its #p tag (test_nip17_gift_wrap_recipient_receives), and non-appearance of a stored gift wrap in a NIP-50 search result (test_nip17_gift_wrap_not_searchable)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:1-2"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:589-611"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:622-667"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:677-750"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs:971-1044"
  - statement: "buzz-db's store/event.rs states 'Deduplication is application-layer: ON CONFLICT DO NOTHING' and insert_event_on's INSERT statement carries that clause keyed on the event's id; this is the generic, kind-agnostic idempotency mechanism that also covers kind:1059 — resubmitting the identical signed gift wrap (same id) is a no-op rather than a duplicate row, with no gift-wrap-specific ordering or replay logic layered on top."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:5"
      - "crates/buzz-db/src/store/event.rs:295-327"
  - statement: "NIP-17 itself (upstream Nostr Implementation Possibility 17, 'Private Direct Messages') is not vendored, copied, or re-described anywhere in this repository; grepping the crates and docs trees for 'nip.?17' surfaces only this repository's own kind.rs doc comment, code comments, and test names referencing the number, never the specification's own encryption-construction prose (seal/rumor/gift-wrap layering)."
    entry_class: INFERENCE
    evidence:
      - "grep_repo('nip.?17|gift.?wrap|giftwrap|seal|rumor', crate='crates') -> matches only code declaring/handling KIND_GIFT_WRAP=1059 and its p-gating, plus unrelated 'seal' hits in buzz-push-gateway/buzz-auth token/JWKS sealing, never NIP-17's own encryption steps"
    confidence: 0.85
---

# NIP-17 gift-wrap envelope: interface

This node documents the boundary at which Buzz's relay (`crates/buzz-relay`)
accepts, authorizes, stores, and delivers **kind:1059 gift-wrap events** — the
outer envelope upstream [NIP-17](https://github.com/nostr-protocol/nips/blob/master/17.md)
("Private Direct Messages") defines for carrying an encrypted, sender-anonymized
private message between two Nostr keypairs. The exchange happens over the
existing WebSocket + Nostr-event transport (`EVENT`/`REQ`/`CLOSED`/push-lease
delivery) that every other event kind uses; NIP-17 does not introduce a new
wire transport, only a new kind with relay-observable authorization rules
layered on top of the ordinary event-submission and subscription surface.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Submit a kind:1059 event over `EVENT` (WebSocket only) | `crates/buzz-relay/src/handlers/event.rs#handle_event`, `crates/buzz-relay/src/handlers/ingest.rs#ingest_event_inner` | Accepted even when the event's `pubkey` (an ephemeral key, per NIP-59) differs from the authenticated caller's identity; rejected outright over HTTP. Requires `Scope::MessagesWrite`. |
| Subscribe via `REQ` for kind:1059 | `crates/buzz-relay/src/handlers/req.rs#p_gated_filters_authorized` | A filter that can match kind:1059 must carry a `#p` tag whose every value equals the authenticated reader's own pubkey; otherwise the relay sends `CLOSED`. |
| Push-notification delivery | `crates/buzz-relay/src/push_runtime.rs#push_filter_authorized_for_event` | A push lease may only be woken for a gift wrap addressed (`#p`) to that lease's own author — the same ownership check as the `REQ` gate, re-applied at wake time. |
| Full-text search (NIP-50) | `crates/buzz-search` storage layer (generated `search_tsv` column) | Never matches: kind:1059 rows are written with a NULL `search_tsv`, so no search query can surface them regardless of filter authorization. |

## Contract and stability

- **Transport restriction.** Kind:1059 is accepted only over the WebSocket
  `EVENT` path; the same shared ingest function rejects it over HTTP with
  `"invalid: kind 1059 is only accepted via WebSocket"` (`ingest.rs:2192-2196`).
- **Pubkey-mismatch exemption.** Every other kind requires the signed event's
  `pubkey` to equal the authenticated caller's own pubkey; kind:1059 is
  explicitly exempted at both the WebSocket entry point (`event.rs:655-660`)
  and the shared ingest path (`ingest.rs:2242-2243`), matching NIP-59's design
  of signing the wrapper with a throwaway key.
- **Mandatory `#p` read gate.** Any subscription filter capable of matching
  kind:1059 must name exactly the reader's own pubkey in `#p`, or the relay
  closes the subscription (`req.rs:1182-1210`). An `ids`-based filter does not
  bypass this for kind:1059 — the `ids` exemption in `p_gated_filters_authorized`
  is withheld for kinds on an explicit no-exemption list, and while kind:1059
  is not itself on that narrower list (only `KIND_DM_VISIBILITY` and
  `KIND_AGENT_TURN_METRIC` are), it is still subject to the outer `#p`
  requirement whenever the filter's `kinds` can match it and no bare-`ids`
  filter is present.
- **Write scope.** Submitting a gift wrap requires `Scope::MessagesWrite` on
  the caller's auth token, the same scope ordinary text notes require
  (`ingest.rs:462-484`).
- **No workflow triggering.** A stored gift wrap never triggers the community
  workflow engine (`event.rs:526-531`) — it is treated purely as private,
  addressed content, not an event other automation should react to.
- **Storage-level unsearchability.** Kind:1059 rows are written with a NULL
  `search_tsv`, a guarantee enforced at the database schema/migration level,
  not merely by filter authorization — a defense-in-depth layer beyond the
  `#p` gate (`fts_integration.rs:1149-1199`).
- **Push-delivery ownership.** A push lease can only be woken by a gift wrap
  addressed to that lease's own author, mirroring the `REQ`-time `#p` gate
  (`push_runtime.rs:317-334`).
- **Ordering and idempotency.** No gift-wrap-specific ordering guarantee
  exists; kind:1059 relies on the same generic, kind-agnostic mechanism every
  stored event uses — `insert_event`'s `ON CONFLICT DO NOTHING` keyed on the
  event id, so resubmitting an identical signed gift wrap is idempotent rather
  than duplicated (`buzz-db/src/store/event.rs:5,295-327`).
- **Versioning.** No version or compatibility note for this kind exists
  anywhere in the evidence gathered; the contract above is inferred from
  current code, not from a stated stability promise.

## Boundary

This node does not describe:
- **NIP-17's own client-side cryptographic construction** — the seal (kind:13,
  NIP-44-encrypted rumor signed by the sender's real key) and rumor (the
  unsigned inner event) layering that produces the ciphertext carried in a
  gift wrap's `content`. That construction happens entirely on the client and
  is not implemented anywhere in this repository's relay or core crates; this
  node covers only what the relay observes and enforces about the outer
  kind:1059 envelope (authorization, transport, storage, delivery), per
  `templates/interface.md`'s guidance to cite an externally owned protocol's
  specification rather than re-describing it from memory.
- **A field-by-field, domain-expert-depth catalogue** of every tag or byte
  Any given implementation's gift wrap might carry — this node states the
  relay-enforced contract, not an exhaustive parameter reference.
- **NIP-59 (the underlying "Gift Wrap" kind mechanism)** and **kind:30622
  (`KIND_DM_VISIBILITY`)**, both referenced in code comments alongside
  kind:1059 and both sharing parts of the same `P_GATED_KINDS` machinery, as
  their own separate subjects — each is independently maintainable and, if
  documented, belongs in its own corpus node rather than folded into this one.

## Relationships

Declared: none. The corpus tree on `origin/launchpad` at the recorded revision
contains no interface- or event-kind-shaped sibling node (only `architecture`
and `governance`-typed nodes plus this task's own template are merged), so
there is no legitimate `relationships.target` to name yet — per `AGENTS.md`'s
rule that a target naming an id no loaded node carries is a hard validation
error. The natural future edges, once such nodes exist, are a `references`
toward an event-kind node for kind:1059 itself (if `#1337`'s template produces
one) and toward nodes for NIP-59 and kind:30622 noted in *Boundary* above.

## Scope and omissions

**This node covers** the relay-enforced contract for kind:1059 gift-wrap
events: transport restriction to WebSocket, the pubkey-mismatch exemption for
the signing key, the mandatory `#p` read-authorization gate on subscriptions
and its `CLOSED` failure mode, the required write scope, the exclusion from
workflow triggering, the storage-level unsearchability guarantee, and the
matching push-delivery ownership check — each grounded in the relay code and
in `crates/buzz-test-client/tests/e2e_nostr_interop.rs`'s four `test_nip17_*`
end-to-end tests.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-17's own seal/rumor encryption construction | Upstream NIP-17 specification (client-side, not implemented in this repository) |
| NIP-59's own gift-wrap kind mechanism as an independent subject | A future, separate corpus node, if one is created |
| kind:30622 (`KIND_DM_VISIBILITY`) as an independent subject | A future, separate corpus node, if one is created |
| Front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **The four `test_nip17_*` tests are all marked `#[ignore]`** (they require a
  running relay against Postgres/Redis per the crate's integration-test
  convention) — their assertions were read and cited, but the tests were not
  executed as part of authoring this node.
- **No client-side implementation of NIP-17 sealing/unwrapping** was located
  anywhere in this repository (desktop, mobile, or CLI) to confirm the relay's
  contract is actually exercised by a first-party client today; this is a gap
  in what was checked, not a claim that no client exists.
- **Whether any deployed client sends real seal/rumor-wrapped content** versus
  the tests' placeholder ciphertext (`"encrypted-content"`) was not verified —
  the relay's contract is agnostic to `content` shape and this does not affect
  the claims above, but it is noted as unverified.
