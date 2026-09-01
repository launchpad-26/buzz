---
id: interfaces-nostr-buzz-nips-nip-rs
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
  - statement: "NIP-RS (docs/nips/NIP-RS.md) is Buzz's own custom, draft/optional Nostr protocol extension defining a scheme for synchronizing a user's own per-context read state across that user's own client instances, using encrypted kind:30078 events; it explicitly is not a read-receipt protocol and does not expose what another user has read."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:1-33"
  - statement: "The kind constant KIND_READ_STATE = 30078 is declared once in buzz-core and registered in the shared kind list; desktop and mobile each declare their own client-side constant carrying the same numeric value (30078)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:75"
      - "crates/buzz-core/src/kind.rs:731"
      - "desktop/src/shared/constants/kinds.ts:47"
      - "mobile/lib/shared/relay/nostr_models.dart:28"
  - statement: "Kind 30078 (NIP-78 application-specific data) is shared by several unrelated desktop features besides read-state -- channel sections, channel mutes, channel stars, channel sort, project-sidebar membership, and community theme -- all distinguished only by their `d` tag namespace, not by kind number."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.ts:44-53"
  - statement: "The wire event/content shape NIP-RS defines -- `d` tag `read-state:<32-hex-slot-id>`, exactly one `t:read-state` tag, and a NIP-44-encrypted content field carrying `{v, client_id, contexts}` -- is implemented client-side in desktop's readStateFormat.ts (validation and sanitization: isValidBlob, sanitizeContexts, isValidReadStateDTag) and readStateIdentity.ts (client_id/slot_id generation and localStorage persistence)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/readState/readStateFormat.ts"
      - "desktop/src/features/channels/readState/readStateIdentity.ts"
      - "docs/nips/NIP-RS.md:36-116"
  - statement: "Desktop's ReadStateManager class implements the client protocol end to end: initialize() (fetch, merge, and start the live subscription), markContextRead/advanceContext (local frontier advance), getEffectiveTimestamp (the hierarchical frontier resolution NIP-RS.md:141-167 defines for channel/thread/message contexts), fetchAndMerge/mergeEvents (horizon-bounded fetch plus CvRDT max-merge), startLiveSubscription/handleIncomingEvent (live convergence and debounced re-publish), and publish/publishOneSlot/publishSplitSlots (read-before-write, debounced, multi-slot budget splitting)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/readState/readStateManager.ts:307"
      - "desktop/src/features/channels/readState/readStateManager.ts:334"
      - "desktop/src/features/channels/readState/readStateManager.ts:375"
      - "desktop/src/features/channels/readState/readStateManager.ts:435"
      - "desktop/src/features/channels/readState/readStateManager.ts:456"
      - "desktop/src/features/channels/readState/readStateManager.ts:531"
      - "desktop/src/features/channels/readState/readStateManager.ts:556"
      - "desktop/src/features/channels/readState/readStateManager.ts:645"
  - statement: "mobile/lib/shared/read_state/read_state_manager.dart's ReadStateManager class mirrors the same operation set for the Flutter client under different method names: initialize, markContextRead, getEffectiveTimestamp, _fetchAndMerge, _mergeEvents, _startLiveSubscription, _handleIncomingEvent, _publish."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/read_state/read_state_manager.dart:94"
      - "mobile/lib/shared/read_state/read_state_manager.dart:118"
      - "mobile/lib/shared/read_state/read_state_manager.dart:92"
      - "mobile/lib/shared/read_state/read_state_manager.dart:203"
      - "mobile/lib/shared/read_state/read_state_manager.dart:224"
      - "mobile/lib/shared/read_state/read_state_manager.dart:270"
      - "mobile/lib/shared/read_state/read_state_manager.dart:294"
      - "mobile/lib/shared/read_state/read_state_manager.dart:381"
  - statement: "The relay recognizes a NIP-RS coordinate structurally -- kind 30078, exactly one `d` tag matching `read-state:<32 lowercase hex chars>`, exactly one `t:read-state` tag -- via the `is_nip_rs` check in buzz-db's parameterized-replace path, and when true, hard-deletes the previously-live row for that coordinate on replacement instead of soft-tombstoning it. This is the relay-side implementation of the spec's claim that a recognizable coordinate lets a relay 'replace superseded versions outright instead of retaining a tombstone row per publish'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/replaceable.rs:151-167"
      - "docs/nips/NIP-RS.md:70"
  - statement: "A dedicated migration guard in buzz-db's runtime migration path blocks proceeding on a pre-existing database containing kind:30078 rows matching the read-state `d` tag pattern with ambiguous `d`/`t` tag cardinality, and its own error message names the condition 'NIP-RS migration blocked'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:110-169"
  - statement: "No buzz-cli subcommand, HTTP endpoint, or new event kind is dedicated to NIP-RS beyond the shared kind:30078 registration -- a repository search of crates/buzz-cli/src for read-state/30078/NIP-RS references returned zero matches -- consistent with the spec's own Backwards Compatibility section, which states it 'introduces no changes to existing event kinds and adds no new kind, wire message, or relay-stored read-state logic.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:784-788"
      - "grep_repo('read-state|read_state|ReadState|nip-rs|NIP-RS|30078', path='crates/buzz-cli/src') -> zero matches, verified at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "Content is NIP-44 v2 encrypt-to-self ciphertext (conversation key computed from the user's own private key and public key), and the one-live-event-per-coordinate, last-write-wins-by-created_at/id replacement mechanics are NIP-33 parameterized-replaceable-event semantics, not a NIP-RS invention."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:78-92"
      - "docs/nips/NIP-RS.md:402"
  - statement: "The frontier merge rule is a grow-only max-register state-based CvRDT with an associative, commutative, idempotent join; clients MUST NOT lower a read timestamp, only advance it."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:381-391"
  - statement: "The spec defines an explicit Content Validation list of MUST-discard/MUST-ignore conditions (invalid JSON, missing/invalid client_id, missing/non-object contexts, oversized context ID, more than 10,000 context entries, malformed override groups, and others), and a separate Invalid Cases section giving concrete example payloads and the required handling for each (discard the entire event, discard one context entry, or ignore the event)."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:101-117"
      - "docs/nips/NIP-RS.md:747-758"
  - statement: "The spec provides a worked valid example -- two devices' blobs (desktop and mobile, each with an independent random slot id) merging via max() per context to one effective read-state map -- and a Ciphertext Test Vector, in addition to the Invalid Cases list, so both a valid example and failure examples already exist in the primary source."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:613-651"
      - "docs/nips/NIP-RS.md:710-729"
      - "docs/nips/NIP-RS.md:747-758"
  - statement: "The spec's Manual-Unread Override Layer (ov_s/ov_c/ov_b wire counters, the clear-wins tie policy, the full-state-load completeness procedure, and tombstone floors) is not implemented in any Buzz client or relay code at this revision; it exists only as a bounded-exhaustive formal model and 9-mutant harness under docs/formal/nip-rs-unread/, not as production code."
    entry_class: INFERENCE
    evidence:
      - "grep_repo('ov_s|ov_c|ov_b|fullStateLoad|manualUnread|override_active|overrideActive', paths='desktop/src,mobile/lib,crates/') -> zero true matches at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052 (one false-positive substring hit in crates/buzz-media/src/validation.rs's unrelated check_moov_before_mdat identifiers, confirmed unrelated to read state)"
      - "docs/formal/nip-rs-unread/model.py"
      - "docs/formal/nip-rs-unread/NOTE.md"
    confidence: 0.85
  - statement: "The spec itself scopes its own formal verification narrowly: the bounded model covers 'the CRDT register algebra, merge/compaction rules, per-context grouping atomicity, and escape/unescape bijection' but explicitly does NOT verify 'the single-primary rule, the full-state-load completeness procedure, the relay conformance requirements or the mutation fence it depends on, or the carry-forward rule.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md:611"
  - statement: "Relay-side authentication and authorization for publishing any event (including kind:30078 NIP-RS events) goes through the standard NIP-42 challenge/response pipeline (kind:22242 AUTH events), not a NIP-RS-specific mechanism; content-level privacy is instead provided by the NIP-44 encrypt-to-self scheme described above."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:1-7"
      - "docs/nips/NIP-RS.md:760-762"
  - statement: "node.schema.json's `type` enum has no literal 'interface' value; templates/interface.md states that a node documenting one interface/API boundary carries `type: interfaces-events`, the single combined value node.schema.json defines for both interface- and event-kind-shaped corpus subject matter."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
  - statement: "Issue #1004's Definition of done requires the node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative spec representation, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1004 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# NIP-RS: interface

NIP-RS ([`docs/nips/NIP-RS.md`](../../../../../docs/nips/NIP-RS.md)) is Buzz's
own custom, draft/optional Nostr protocol extension. It is not an interface a
caller calls synchronously; it is a **peer-to-peer sync boundary between a
single user's own client instances**, mediated entirely through Nostr relays.
Each client instance publishes and consumes NIP-44-encrypted `kind:30078`
events at its own `read-state:<slot-id>` coordinate(s), so that "I have read
channel/thread/message X up to timestamp T" propagates from a desktop app to a
mobile app (and back) without a read-receipt protocol and without any relay
needing to interpret read-state semantics itself.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish own read-state blob | NIP-RS.md "Writing" / "Read-Before-Write" (`docs/nips/NIP-RS.md:393-431`); `ReadStateManager.publish`/`publishOneSlot`/`publishSplitSlots` (`desktop/src/features/channels/readState/readStateManager.ts:645`); `ReadStateManager._publish` (`mobile/lib/shared/read_state/read_state_manager.dart:381`) | Fetch-merge-publish a `kind:30078` event at the client's primary (and, if budget-exceeded, additional) coordinate(s), debounced and read-before-write. |
| Fetch and merge read state | NIP-RS.md "Fetching" (`docs/nips/NIP-RS.md:299-320`); `ReadStateManager.fetchAndMerge`/`mergeEvents` (`readStateManager.ts:435`, `:456`); `_fetchAndMerge`/`_mergeEvents` (`read_state_manager.dart:203`, `:224`) | Horizon-bounded (default 7 days) fetch of the user's own `kind:30078`/`#t:read-state` events, decrypt, validate, and componentwise-max-merge into local effective state. |
| Live subscription and convergence | NIP-RS.md "Live Subscription and Convergence" (`docs/nips/NIP-RS.md:433-450`); `startLiveSubscription`/`handleIncomingEvent` (`readStateManager.ts:531`, `:556`); `_startLiveSubscription`/`_handleIncomingEvent` (`read_state_manager.dart:270`, `:294`) | Subscribe to the user's own `kind:30078`/`#t:read-state` events for live cross-device updates; merge and, if the merged result changed, schedule a debounced re-publish. |
| Advance a context's read frontier (mark read) | NIP-RS.md "Writing", "Read Context Schemes" (`docs/nips/NIP-RS.md:132-167`); `markContextRead`/`advanceContext` (`readStateManager.ts:334`, `346`); `markContextRead` (`read_state_manager.dart:118`) | Locally advance the max-register timestamp for a channel, `thread:<root-event-id>`, or `msg:<event-id>` context; local-only until the next debounced publish. |
| Resolve a context's effective read timestamp | NIP-RS.md "Hierarchical Frontier Rule" (`docs/nips/NIP-RS.md:169-291`); `getEffectiveTimestamp` (`readStateManager.ts:375`, comment at `:43` citing the spec by line); `getEffectiveTimestamp` (`read_state_manager.dart:92`) | `effective(ctx) = max(merged[ctx], effective(parent(ctx)))`, propagating a channel's frontier down to its threads and messages. |
| Relay-side coordinate recognition and replacement | `is_nip_rs` check, `hard_delete_superseded` (`crates/buzz-db/src/store/replaceable.rs:151-167`); spec "Recognizable coordinates" (`docs/nips/NIP-RS.md:70`) | The relay structurally recognizes a `read-state:<32-hex>` `d` tag plus a single `t:read-state` tag and, on replacement, hard-deletes the prior row instead of soft-tombstoning it. |
| Legacy-row migration guard | `crates/buzz-db/src/runtime/migration.rs:110-169` | Blocks a pre-migration-0007 database from proceeding if it contains kind:30078 rows matching the read-state `d` tag pattern with ambiguous `d`/`t` tag cardinality. |

## Contract and stability

**Versioning.** The decrypted content carries its own schema version `v`
(currently `1`); clients MUST ignore blobs with an unknown `v` value
(`docs/nips/NIP-RS.md:94`), so the wire format can grow without a kind change.

**Replaceable-event semantics (NIP-33), not NIP-RS's own.** Each
`read-state:<slot-id>` coordinate is a NIP-33 parameterized-replaceable event:
one live event per coordinate, resolved last-write-wins by `created_at`
(ties broken by lowest event id). NIP-RS layers a client-clock-skew rule on
top -- if a client's local clock would produce a `created_at` at or below the
maximum `created_at` seen across fetched blobs for the same `d` tag, it MUST
publish at `max_fetched_created_at + 1` instead (`docs/nips/NIP-RS.md:452-454`).

**Ordering and idempotency.** The frontier merge rule is a grow-only
max-register CvRDT: `effective[context] = max(timestamp)` across all merged
blobs, an associative, commutative, idempotent join (`docs/nips/NIP-RS.md:381-391`).
Re-merging the same event twice, or merging events out of arrival order,
converges to the same result -- clients MUST NOT lower a read timestamp, only
advance it. Publishing follows read-before-write (fetch, merge, then publish)
to reduce the window for a concurrent-write race (`docs/nips/NIP-RS.md:408-431`).

**Error and rejection behavior.** Malformed or invalid input is handled by
*discarding the offending unit*, not by an error response the publisher
observes: an event whose content fails to decrypt, or whose `client_id`/`v`
field is missing or invalid, is discarded in full; an individual context
entry with an out-of-range timestamp or an oversized context ID is dropped
while the rest of the blob is still processed; a blob exceeding 10,000
context entries is rejected outright (`docs/nips/NIP-RS.md:101-117`,
`:747-758`). There is no synchronous failure signal to the publisher --
correctness depends on every consuming client applying the same validation
rules independently.

**Authentication and authorization.** Publishing any event, including a
NIP-RS `kind:30078` event, goes through the relay's standard NIP-42
challenge/response AUTH flow (`crates/buzz-auth/src/nip42.rs:1-7`) -- there is
no NIP-RS-specific authorization check. Content confidentiality (who can read
the plaintext) is instead a property of the NIP-44 encrypt-to-self scheme:
the conversation key is derived from the user's own keypair with itself as
both parties, so only that user's own signing key can decrypt the blob
(`docs/nips/NIP-RS.md:78-92`, `:760-762`).

## Boundary

This node does not describe:

- **A single event kind's own wire contract in general.** Kind `30078` is a
  generic NIP-78 application-data kind reused by several unrelated desktop
  features (channel sections, mutes, stars, sort, project-sidebar membership,
  community theme) -- this node documents only the `read-state:` `d`-tag
  namespace's contract, not kind 30078 as a whole. No corpus node for kind
  30078 itself exists yet; if one is created, this node should `references`
  it rather than restate its generic semantics.
- **The Manual-Unread Override Layer as implemented behavior.** The spec's
  `ov_s`/`ov_c`/`ov_b` counters, clear-wins tie policy, full-state-load
  completeness procedure, and tombstone-floor durability rules are real,
  formally modeled (`docs/formal/nip-rs-unread/`), and normative in the spec
  text -- but this session's repository search found no client or relay code
  implementing them. Treat every claim above about the override layer as a
  description of the *specification*, not of Buzz's shipped behavior, until
  an implementation lands and a future revision of this node (or a follow-up
  issue) can cite it.
- **NIP-33, NIP-44, or NIP-78 themselves.** Their wire formats, guarantees,
  and encryption schemes are external protocols this node cites, not
  redefines.
- **Field-by-field, domain-expert-depth API-parameter cataloguing.** This
  node lists operations and their contract; it is not a reference-depth
  parameter catalogue.

## Relationships

- `implements`: `corpus-template-interface` (this node is drafted from that
  template).
- No `references` edges are declared. The natural targets -- a kind:30078
  event-kind node, and a node for the Manual-Unread Override Layer once (or
  if) it is implemented -- do not exist in `origin/launchpad`'s corpus tree at
  this revision; both are named by filename above rather than by relationship
  edge, per the instruction that unmerged sibling nodes must not be declared
  as relationship targets.

## Scope and omissions

**This node covers** the NIP-RS base frontier-sync protocol as actually
implemented: the `kind:30078` wire event and content shape, the desktop and
mobile client managers that publish/fetch/merge/subscribe, the relay's
structural recognition and hard-delete-on-replace behavior for read-state
coordinates, the migration guard protecting pre-existing data, the
CvRDT/NIP-33/NIP-44 contract guarantees, and the spec's own worked valid and
invalid examples.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 30078's generic wire contract across its other (non-read-state) uses | No corpus node yet |
| The Manual-Unread Override Layer's implementation, if and when it ships | No corpus node yet; the layer is currently spec-only (see Boundary) |
| NIP-33 / NIP-44 / NIP-78's own wire formats | Their own specifications, cited above, not restated |
| Field-by-field API-parameter cataloguing | A reference-depth node, if the corpus ever builds one |

**Expected but not verified when this node was written:**
- Whether every desktop `readState/` and mobile `read_state/` unit test
  (`readStateManager.test.mjs`, `readStateFormat.test.mjs`,
  `readStateStorage.test.mjs`) currently passes was not re-run in this
  session -- their existence was confirmed by listing, not by executing them.
- Whether any other client (a hypothetical third Buzz client, or a
  non-Buzz Nostr client) implements NIP-RS was not investigated; this node
  only confirms Buzz's own desktop, mobile, and relay code.
