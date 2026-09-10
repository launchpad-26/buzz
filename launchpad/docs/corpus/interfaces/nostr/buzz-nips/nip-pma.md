---
id: interfaces-nostr-buzz-nips-nip-pma
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
  - statement: "docs/nips/NIP-PMA.md defines kind 30179 as an owner-authored, addressable, owner-readable aggregate for one runnable managed agent, coordinate (owner pubkey, 30179, agent pubkey), and states the document's own status as draft — protocol/codec reservation only — with relays required to reject the kind until privacy, transactional CAS, backup/restore, revocation and capability gates are deployed."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PMA.md:1-15"
  - statement: "The signed outer envelope permits exactly four two-element tags — d (agent pubkey, exactly once), g (CAS generation, exactly once), prev (predecessor event id, exactly once after generation 1 and absent at generation 1), and state (active|deleted, exactly once) — with bounded NIP-44 v2 ciphertext content encrypted owner-to-owner."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PMA.md:17-30"
  - statement: "crates/buzz-core/src/kind.rs declares KIND_PRIVATE_MANAGED_AGENT = 30179 and includes it in AUTHOR_ONLY_KINDS, the list of kinds whose stored events the relay must never reveal (existence, content, or search matches) to anyone but the authenticated author."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:118"
      - "crates/buzz-core/src/kind.rs:129-133"
  - statement: "crates/buzz-core/src/private_managed_agent.rs implements the full inert wire codec for this kind: an Envelope type and validate_envelope function that check the signed outer tags before any decryption, a Payload type carrying format/version/agent_pubkey/owner_pubkey/generation/previous_event_id/state plus an optional ActivePayload or deleted_at, and build_event/validate_and_decrypt functions that encrypt-and-sign or decrypt-and-cross-check a candidate event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:69"
      - "crates/buzz-core/src/private_managed_agent.rs:212"
      - "crates/buzz-core/src/private_managed_agent.rs:243"
      - "crates/buzz-core/src/private_managed_agent.rs:262"
      - "crates/buzz-core/src/private_managed_agent.rs:341"
      - "crates/buzz-core/src/private_managed_agent.rs:378"
  - statement: "validate_payload (and the validate_active helper it calls for the Active state) enforces format/version equality, canonical hex pubkeys, the generation/prev pairing rule, RFC3339 timestamps, namespaced extension keys, definition/instance projection bindings against kind 30175 and kind 30177, that the packaged agent nsec derives the agent pubkey, and that any auth_tag is an unconditional owner-to-agent attestation naming a distinct agent key — returning a typed Error on any violation rather than partially accepting a payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:415-540"
  - statement: "A unit test builds a payload, signs it with build_event, and decrypts/validates it with validate_and_decrypt for the same owner keys, asserting the round-tripped payload is identical and the envelope reports generation 1 and State::Active — the valid-path example for this interface."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:887-898"
  - statement: "A second unit test asserts that validate_and_decrypt returns Err(Error::InvalidEnvelope) both when a non-owner key attempts to decrypt a correctly-built event and when the ciphertext of an otherwise-valid event is tampered with by appending one byte — the failure-path example for this interface."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/private_managed_agent.rs:925-940"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's required_scope_for_kind classifies KIND_PRIVATE_MANAGED_AGENT as requiring Scope::UsersWrite, the same scope as kind 30175 (persona) and kind 30177 (managed agent), and a separate list in the same file exempts it (alongside those sibling kinds) from h-tag channel scoping as owner-authored global state; a unit test asserts both properties plus that the kind is a global-only, non-channel-scoped kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:437-448"
      - "crates/buzz-relay/src/handlers/ingest.rs:650-660"
      - "crates/buzz-relay/src/handlers/ingest.rs:3841-3849"
  - statement: "No dedicated ingest-time rejection branch for kind 30179 exists anywhere under crates/buzz-relay/ — the only references to KIND_PRIVATE_MANAGED_AGENT in that crate are the scope classification, the h-tag-scoping exemption, and the test asserting both — so a well-formed kind:30179 event is currently accepted through the same generic owner-scoped write path as kind 30175/30177, not rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:31"
      - "crates/buzz-relay/src/handlers/ingest.rs:437-448"
      - "crates/buzz-relay/src/handlers/ingest.rs:650-660"
      - "crates/buzz-relay/src/handlers/ingest.rs:3841-3849"
  - statement: "This currently-accepts behavior is a deliberate, already-shipped change, not an oversight: crates/buzz-relay/CHANGELOG.md records 'feat(relay): accept kind:30179 private managed-agent events at ingest' against PR #5133."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/CHANGELOG.md:7"
  - statement: "The spec's own normative 'Relays MUST reject this kind' line and the relay's current unconditional acceptance of the kind at ingest describe two different moments of the same feature's rollout — the spec states the target/safe state before the privacy and CAS work lands, while the shipped code already accepts the kind through the ordinary owner-write path — and this is reported here as an open discrepancy rather than resolved, because reconciling the spec text or gating ingest is runtime behavior change out of this task's scope."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-PMA.md:1-5"
      - "crates/buzz-relay/CHANGELOG.md:7"
      - "crates/buzz-relay/src/handlers/ingest.rs:437-448"
    confidence: 0.75
  - statement: "migrations/0033_private_managed_agent_fts.sql and crates/buzz-db/src/runtime/migration.rs's migration-index test confirm kind 30179 is excluded from full-text-search tokenization (its search_tsv column is generated NULL for that kind), matching the spec's required-deployment-order step 2 ('verification that the positive FTS allowlist continues to exclude 30179')."
    entry_class: FACT
    evidence:
      - "migrations/0033_private_managed_agent_fts.sql:1-15"
      - "crates/buzz-db/src/runtime/migration.rs:892-902"
      - "docs/nips/NIP-PMA.md:99-104"
  - statement: "crates/buzz-relay/src/handlers/req.rs's is_author_only_event and a chokepoint filter in crates/buzz-relay/src/handlers/event.rs both consult AUTHOR_ONLY_KINDS to silently omit an author-only event (which includes kind 30179) from historical delivery, live fan-out, and REQ/COUNT results to any reader other than the event's own author — the relay-side authorization boundary for this interface, independent of and prior to the NIP-44 owner-to-owner encryption that makes the content itself unreadable to anyone but the owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:1280"
      - "crates/buzz-relay/src/handlers/req.rs:1342-1344"
      - "crates/buzz-relay/src/handlers/req.rs:1401"
      - "crates/buzz-relay/src/handlers/event.rs:139"
  - statement: "launchpad/docs/corpus/templates/interface.md (id corpus-template-interface) is merged on origin/launchpad and is the corpus's own template for interface-shaped nodes; it prescribes required sections (interface description, operations, contract and stability, boundary, relationships, scope and omissions) and states that a node built from it carries type: interfaces-events, the enum's single combined value for interfaces and event kinds."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md:1-33"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
  - statement: "At repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052, git ls-tree of origin/launchpad's corpus tree contains no interfaces/ subtree and no other buzz-nips sibling node, so corpus-template-interface is the only existing node this document can legitimately target with a relationships entry."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> architecture/**, schema/**, standards/**, templates/**, AGENTS.md, README.md; no interfaces/ subtree, checked at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
relationships:
  - type: implements
    target: corpus-template-interface
---

# NIP-PMA: private managed-agent aggregate — interface

This node documents Buzz's own custom NIP extension, NIP-PMA (`docs/nips/NIP-PMA.md`):
the owner-encrypted Nostr kind `30179` boundary across which a community owner's
device and the relay exchange one runnable AI agent's complete private
configuration as a single addressable, encrypted aggregate. The two sides are the
owner's authoring device (which builds, signs and NIP-44-encrypts the event) and
the relay (which stores, scopes, and — per the wire codec's own author-only
classification — refuses to reveal the event to anyone but that owner). This is a
whole self-contained protocol extension (a signed outer envelope plus a versioned
decrypted payload schema, its own generation/predecessor chain, and a staged
deployment plan), not one event kind's bare tag/content shape in isolation, which
is why it is documented as an interface rather than deferred to a single
event-kind node.

## Interface description

A `kind:30179` event is authored and signed by the community owner. Its four
permitted outer tags (`d`, `g`, `prev`, `state`) expose only the routing/CAS
metadata a relay needs to store and scope the event; its `content` is NIP-44 v2
ciphertext encrypted from the owner's key to the owner's own key, so only the
owner (not even the agent whose identity it describes) can decrypt it. The
decrypted plaintext is a versioned JSON payload (`format`, `version`,
`agent_pubkey`, `owner_pubkey`, `generation`, `previous_event_id`, `state`,
`updated_at`, and either an `active` body or `deleted_at`) that repeats every
outer field so a mismatch between the signed tags and the decrypted content is
detectable corruption, not silent drift.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Build and sign a candidate event | `crates/buzz-core/src/private_managed_agent.rs#build_event` (line 341) | Validates a `Payload`, serializes and NIP-44-v2-encrypts it to the owner's own key, attaches the four outer tags, and signs with the owner's keys. |
| Validate the signed outer envelope | `crates/buzz-core/src/private_managed_agent.rs#validate_envelope` (line 262) | Checks kind, author, event id/signature, ciphertext length, exact tag grammar (no duplicates, no unknown tags), and the generation/`prev` pairing rule — before any decryption is attempted. |
| Decrypt and cross-check a payload | `crates/buzz-core/src/private_managed_agent.rs#validate_and_decrypt` (line 378) | Runs `validate_envelope`, NIP-44-decrypts as the owner, strict-parses the JSON (rejecting duplicate/unknown fields), and asserts the decrypted payload's routing fields exactly match the outer envelope. |
| Validate decrypted payload semantics | `crates/buzz-core/src/private_managed_agent.rs#validate_payload` (line 415) | Format/version check, canonical pubkey parsing, generation/`prev` rule, RFC3339 timestamps, namespaced `extensions` keys, and (for `Active` payloads) definition/instance projection bindings, agent-nsec-derives-`d` check, and optional `auth_tag` attestation validation. |
| Relay ingest classification | `crates/buzz-relay/src/handlers/ingest.rs#required_scope_for_kind` (line 437) | Currently classifies `kind:30179` as an ordinary `Scope::UsersWrite`, global (non-channel-scoped) write — see *Contract and stability* below for what this does and does not enforce today. |
| Relay read authorization | `crates/buzz-relay/src/handlers/req.rs#is_author_only_event` (line 1342), `crates/buzz-relay/src/handlers/event.rs` (line 139) | Silently omits the event from any reader other than its own author, across historical REQ/COUNT and live fan-out. |

## Contract and stability

**Versioning.** The decrypted payload is namespaced by `FORMAT =
"buzz-private-managed-agent"` and `VERSION = 1` (`private_managed_agent.rs:24,26`);
`validate_payload` rejects any payload whose `format`/`version` do not match
exactly. Forward-compatible data is confined to namespaced `extensions` entries
(non-empty key, `:`-namespaced, ≤128 bytes); core semantics never depend on an
extension (`docs/nips/NIP-PMA.md:33-36`).

**Ordering / idempotency.** Aggregates form a hash-chained CAS sequence: `g` is a
canonical positive decimal generation, `prev` names the exact predecessor event
id, and `prev` is required after generation 1 and forbidden at generation 1
(`validate_envelope`, `private_managed_agent.rs:262-320`). A `deleted` payload
still advances generation from its predecessor and adds `deleted_at` — it is a
tombstone in the same chain, not a separate deletion mechanism
(`docs/nips/NIP-PMA.md:60-63`). The spec is explicit that ordinary NIP-33
last-write-wins is **not** sufficient anti-resurrection protection for this kind;
that guarantee is deferred to a future transactional CAS contract this reservation
does not yet implement (`docs/nips/NIP-PMA.md:60-63`, `99-112`).

**Authentication / authorization.** Two independent boundaries apply. First,
content confidentiality: the payload is NIP-44 v2 ciphertext encrypted
owner-to-owner, so no relay, agent, or third party can read it regardless of
delivery. Second, relay-enforced read authorization: `kind:30179` is listed in
`AUTHOR_ONLY_KINDS` (`kind.rs:118,129-133`), and both the historical/COUNT path
(`req.rs:1280,1342-1344,1401`) and the live-fan-out chokepoint
(`event.rs:139`) omit the event from any reader whose pubkey does not match the
event's author — even a reader who already knows the event id. This is stricter
than kind 30175's shared-tag opt-in model (`kind.rs:180-196`): there is no
`shared` escape hatch for kind 30179.

**Error / rejection behavior.** The codec fails closed and returns a typed
`Error` rather than partially accepting malformed input:
`Error::InvalidEnvelope` (malformed/mismatched signed tags, wrong-owner
decryption attempt, or ciphertext tampering — proven by the failure example
below), `Error::Decrypt` (ciphertext does not authenticate, deliberately
redacted detail), `Error::InvalidPayload` (schema, cross-check, or semantic
violation), `Error::Encrypt`/`Error::Sign` (local build failures)
(`private_managed_agent.rs:48-64`).

**Ingest status — an open discrepancy, reported not resolved.** The spec's own
opening line states relays **MUST** reject this kind until privacy, transactional
CAS, backup/restore, revocation and capability gates are deployed
(`docs/nips/NIP-PMA.md:1-5`), and lists this codec/kind reservation as only the
*first* of eight required deployment-order steps (`docs/nips/NIP-PMA.md:99-112`).
However, no dedicated ingest-time rejection branch for `kind:30179` exists
anywhere under `crates/buzz-relay/` today — the kind is classified identically to
already-deployed owner-scoped kinds 30175/30177 (`ingest.rs:437-448,650-660`),
and `crates/buzz-relay/CHANGELOG.md:7` records this as an intentional, already
merged change ("accept kind:30179 private managed-agent events at ingest," PR
#5133), not a bug. This node does not attempt to reconcile the two — whether the
spec text is stale or ingest genuinely needs a rejection gate before step 2 of
the deployment order is a product decision this documentation task is explicitly
out of scope to make (see *Boundary*).

## Valid example

`owner_self_round_trip_binds_outer_and_inner` (`private_managed_agent.rs:887-898`):
builds a payload for a generated owner/agent keypair, signs it with `build_event`,
then decrypts and validates it with `validate_and_decrypt` using the same owner
keys. The round-tripped payload is asserted identical to the original, and the
returned `Envelope` reports `generation == 1` and `state == State::Active`.

## Failure example

`wrong_owner_and_tampering_fail_closed` (`private_managed_agent.rs:925-940`):
builds a valid event for one owner, then asserts `validate_and_decrypt` returns
`Err(Error::InvalidEnvelope(_))` when a different, unrelated key attempts the
decrypt (author-mismatch), and again when one byte is appended to the same
event's ciphertext after building it (tamper detection) — both fail closed rather
than partially succeeding.

## Boundary

This node does not describe:
- **The transactional CAS, privacy-gate, or aggregate-submission contract** the
  spec's later deployment-order steps depend on (`docs/nips/NIP-PMA.md:87-112`)
  — none of that is implemented yet; this node documents the codec/kind
  reservation that exists today, step 1 of 8.
- **Field-by-field cataloguing of every `PrivateConfig`/`ActivePayload` member**
  for domain-expert readers — the corpus's reference-depth template (if and when
  one is adopted) is the right home for that, not this interface node.
- **Kind 30175 (persona) or kind 30177 (managed agent)'s own wire contracts.**
  This node cites them only as the definition/instance projections a NIP-PMA
  aggregate binds to (`private_managed_agent.rs:102-123`); their own tag/content
  shape is out of scope here.
- **The Desktop `ManagedAgentRecord` field-classification fixture** the spec
  itself says this reservation "does not yet depend on the Desktop type" for
  (`docs/nips/NIP-PMA.md:82-85`) — that is a future Desktop-side compile-time
  guard, not part of the relay/wire contract this node covers.
- **Whether the spec-vs-ingest discrepancy above should be fixed by changing the
  spec text or by adding a relay-side rejection gate.** Reported as a gap;
  resolving it is runtime product behavior change explicitly outside this
  corpus-authoring task's scope.

## Relationships

- **implements**: `corpus-template-interface` — this node is an instance of the
  corpus's merged interface template.
- No `references` or `part-of` edges are declared. No other `buzz-nips/*`
  interface node, and no kind-30175/30177 event-kind node, exists on
  `origin/launchpad` at the recorded revision (`git ls-tree` check above) — the
  only schema-legal target is the template itself. The natural moment to add
  `references` edges toward kind-30175/30177 nodes (once they exist) or toward
  sibling `buzz-nips/*` nodes is when the first of those merges.

## Scope and omissions

**This node covers** the signed outer envelope's tag grammar, the decrypted
payload's schema and versioning, the codec functions that build/validate/decrypt
it, the relay's current ingest classification and read-authorization enforcement
for this kind, one valid and one failure example drawn from the codec's own unit
tests, and the currently-shipped FTS-exclusion migration — all as they exist at
the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The future transactional CAS / aggregate-submission contract | `docs/nips/NIP-PMA.md`'s own later deployment-order steps (not yet implemented) |
| Kind 30175 / kind 30177's own wire contracts | Their own future event-kind or interface nodes |
| Domain-expert field-by-field parameter cataloguing | The corpus's reference-depth template, if and when adopted (`#1346`/`#1532`, per `templates/interface.md`) |
| The Desktop `ManagedAgentRecord` classification fixture | Future Desktop-side implementation work; not yet built per the spec's own admission |
| Whether ingest should gain a rejection branch, or the spec text should be corrected | A separate, explicitly out-of-scope implementation/spec decision |

**Expected but not verified when this node was written:**
- **No live relay was exercised.** All ingest/read-authorization claims above are
  read from `crates/buzz-relay` source and its own unit tests, not from running
  the relay against a hand-crafted `kind:30179` event over a real WebSocket
  connection.
- **PR #5133's own diff was not opened** — its existence and description are
  taken from the `buzz-relay` CHANGELOG entry citing it, not from reading the
  pull request itself.
- **Whether any other code path (outside `crates/buzz-relay/`, for example a
  desktop-side pre-flight check) independently blocks publishing a `kind:30179`
  event before it reaches the relay was not investigated** — this node's ingest
  claims are scoped to the relay crate only.
