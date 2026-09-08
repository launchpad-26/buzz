---
id: layers-protocol-ephemeral-event
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "buzz-core's kind registry defines EPHEMERAL_KIND_MIN as 20000 and EPHEMERAL_KIND_MAX as 29999, and is_ephemeral is a pure inclusive range test over those two constants with no per-kind table, allowlist or registration step."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Nine declared kinds fall inside the range at this revision, and they split into two groups the registry declares in separate blocks: five relay-fanned-out ephemeral events (KIND_PRESENCE_UPDATE 20001, KIND_TYPING_INDICATOR 20002, KIND_PAIRING 24134, KIND_AGENT_OBSERVER_FRAME 24200, KIND_HUDDLE_REACTION 24810) and four authorization or proof credentials whose doc comments each say they are not stored (KIND_AUTH 22242, KIND_BLOSSOM_AUTH 24242, KIND_NOSTR_IDENTITY_BINDING 24243, KIND_HTTP_AUTH 27235)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Because is_ephemeral consults only the two bounds, all nine satisfy it and so does any undeclared integer in the range, which is why KIND_AUTH is rejected by a dedicated kind equality check placed before the is_ephemeral branch in both the relay's EVENT handler and buzz-db's insert paths rather than being allowed to fall through as an ephemeral event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-db/src/store/event.rs"
  - statement: "The storage layer refuses an ephemeral event at three separate call sites, each applying the same is_ephemeral range test and returning DbError::EphemeralEventRejected, whose message text is \"ephemeral events (kind {0}) must not be stored\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
      - "crates/buzz-db/src/error.rs"
  - statement: "One buzz-db test, reaction_single_tx_event_insert_failure_rolls_back_reaction, uses a kind-20000 event as its vehicle for forcing an insert failure and asserts the resulting error is DbError::EphemeralEventRejected(20000); it is marked #[ignore = \"requires Postgres\"], and its own subject is transaction rollback rather than ephemerality."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs"
  - statement: "The relay's WebSocket EVENT handler branches on is_ephemeral before the persistent path and routes the event to handle_ephemeral_event, which returns to the caller without ever reaching the ingest_event call that the same function makes for every non-ephemeral kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "handle_ephemeral_event verifies the signature, applies presence-specific Redis state updates for kind 20001 only, then publishes to Redis on EventTopic::Channel for an event carrying an h tag or EventTopic::Global for a channel-less one, and separately fans the event out to local WebSocket subscribers, so delivery involves no database read or write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "The ephemeral WebSocket path applies its own two gates before publishing: a scope check requiring MessagesWrite, and a community lifecycle check that refuses with \"restricted: community writes are fenced\" when the community is not serving."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "The relay's only transport-conditioned kind gate is `auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE)`, which names two specific kinds rather than testing a range."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "KIND_GIFT_WRAP is 1059 and KIND_PRESENCE_UPDATE is 20001, so that transport gate blocks one non-ephemeral kind and exactly one of the five declared fanned-out ephemeral kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The remaining in-range kinds are refused on the shared ingest path by a different mechanism entirely: required_scope_for_kind ends in a default arm returning Err(\"restricted: unknown event kind\"), ingest_event rejects on that Err, and no ephemeral kind appears anywhere in the allowlist that precedes it; kind 22242 is the one exception, refused earlier still by a dedicated AUTH equality check that precedes both the transport gate and the allowlist."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "grep_in_line_range(path='crates/buzz-relay/src/handlers/ingest.rs', lines='437-547', pattern='PRESENCE|TYPING|PAIRING|OBSERVER|HUDDLE_REACTION') -> no output, exit status 1"
  - statement: "is_replaceable covers kinds 0, 3, KIND_CHANNEL_METADATA (41) and 10000-19999 while is_parameterized_replaceable covers 30000-39999, and both describe events that are stored under a replacement key, so neither range overlaps the ephemeral one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "ingest_event is the single shared submission path for both transports, called by the HTTP bridge and by the WebSocket EVENT handler, so its allowlist is not HTTP-specific and ephemeral kinds escape it over WebSocket only because the ephemeral branch returns before it is reached."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The merged corpus node implementation-crates-buzz-ws-client carries a FACT stating that \"the relay rejects ephemeral event kinds (20000-29999) over its HTTP surface\", citing crates/buzz-cli/src/client.rs, whose doc comment on publish_ephemeral_event does state \"The relay rejects ephemeral kinds (20000–29999) over HTTP\"."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/implementation/crates/buzz-ws-client.md"
      - "crates/buzz-cli/src/client.rs"
  - statement: "That claim's stated mechanism is wrong even though its outcome coincidentally holds: no range-based HTTP gate exists, the transport gate that does exist would also block non-ephemeral kind 1059, and kinds 20000 and 20002-29999 are refused over HTTP by the transport-agnostic scope allowlist rather than by anything conditioned on HTTP."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
      - "launchpad/docs/corpus/implementation/crates/buzz-ws-client.md"
    confidence: 0.9
  - statement: "The refusal texts differ by mechanism, which is how the three paths can be told apart from the wire: kind 20001 over HTTP gets \"invalid: kind 20001 is only accepted via WebSocket\", kind 20002 gets \"restricted: unknown event kind\", and kind 22242 gets \"invalid: AUTH events cannot be submitted\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A second merged corpus node, architecture-flows-http-event-submission, already describes the same gate correctly as rejecting kind 1059 and kind 20001 specifically under auth.is_http(), so the two merged nodes disagree with each other and the relay source is the authority between them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "NIP-AO, one of Buzz's own NIPs in this repository, records that kind 24200 falls in the ephemeral range 20000-29999 defined by NIP-01, and states an ephemerality contract under which relays MUST NOT persist the kind to durable storage, MUST NOT include it in search indexes, MUST NOT include it in audit logs, SHOULD fan it out only via in-memory pub/sub, and under which historical replay is not supported."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "NIP-PL states that ephemeral kinds (20000-29999), presence and typing MUST NOT be push-eligible, so a push-notification filter cannot name an ephemeral kind."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md"
  - statement: "The P_GATED_KINDS doc comment records that ephemeral kinds are included in that set for filter-layer enforcement only, because they are never stored and so the storage-layer NULL search_tsv defense that protects persistent p-gated kinds does not apply to them."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "Because every insert path refuses the kind, a REQ filter naming an ephemeral kind can return only events published live while the subscription is open, never a historical backlog."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "docs/nips/NIP-AO.md"
    confidence: 0.9
  - statement: "The end-to-end test that would demonstrate that behaviour against a running relay, test_ephemeral_event_not_stored, exists and publishes kind 20001 then asserts a subsequent subscription collects nothing, but it is marked #[ignore] and therefore does not run in the default test pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "No upstream numbered NIP specification text is present anywhere in this repository, so NIP-01's own definition of the ephemeral range cannot be cited to a file here."
    entry_class: FACT
    evidence:
      - "find_files_by_name(root='.', iname_any='NIP-0*.md;NIP-1*.md;NIP-42*.md', prune='./target') -> no output; the same session's directory listing of docs/nips shows only two-letter Buzz NIPs: NIP-AA, NIP-AE, NIP-AM, NIP-AO, NIP-AP, NIP-CW, NIP-DV, NIP-ER, NIP-FI, NIP-GS, NIP-IA, NIP-MP, NIP-OA, NIP-PL, NIP-PMA, NIP-RS, NIP-WP"
  - statement: "Issue #1151 requires that this node define the term in one sentence before deeper explanation, state boundaries and what the concept must not be confused with, link to related concepts, implementation and verification without duplicating them, and use examples only to clarify rather than to introduce a second concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1151 definition of done"
relationships:
  - type: references
    target: capabilities-presence-presence
  - type: references
    target: capabilities-presence-typing-indicator
  - type: references
    target: layers-data-redis-presence
  - type: references
    target: layers-data-redis-typing-indicators
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: implementation-crates-buzz-core
---

# Ephemeral event

An **ephemeral event** is a Nostr event whose kind falls in the integer range
**20000–29999**, which Buzz's relay forwards live to matching subscribers and never
writes to durable storage.

## Definition

Ephemerality in Buzz is a property of the **kind integer**, not of the event's
content, its author, its tags or any flag it carries. `crates/buzz-core/src/kind.rs`
declares two constants — `EPHEMERAL_KIND_MIN = 20000` and
`EPHEMERAL_KIND_MAX = 29999` — and one predicate:

```rust
pub const fn is_ephemeral(kind: u32) -> bool {
    kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX
}
```

**The range is hardcoded, and it is a pure arithmetic test.** There is no per-kind
table of ephemeral kinds, no registration step and no opt-in: an integer is ephemeral
if and only if it lies between the two constants. A kind nobody has declared —
say 27000 — is ephemeral, and the relay and storage layer will treat it as such,
because nothing in the decision consults the kind registry beyond those two bounds.

**Nine** declared kinds fall in the range at the recorded revision, and the arithmetic
sweeps up more than the name suggests. The registry declares them in two separate
blocks, and only the first is what this node means by "ephemeral event":

| Kind | Constant | What it carries |
|---|---|---|
| 20001 | `KIND_PRESENCE_UPDATE` | online / away / offline status |
| 20002 | `KIND_TYPING_INDICATOR` | per-channel typing signal |
| 24134 | `KIND_PAIRING` | NIP-AB device pairing |
| 24200 | `KIND_AGENT_OBSERVER_FRAME` | encrypted agent telemetry and control |
| 24810 | `KIND_HUDDLE_REACTION` | huddle emoji reaction burst |

The other four are **authorization or proof credentials**, not events the relay fans
out to subscribers. They are declared in a different block, each with a doc comment
saying it is not stored, and they satisfy `is_ephemeral` only as a side effect of
where their kind integers happen to sit:

| Kind | Constant | What it actually is |
|---|---|---|
| 22242 | `KIND_AUTH` | NIP-42 auth event — carries bearer tokens |
| 24242 | `KIND_BLOSSOM_AUTH` | BUD-01 media upload authorization |
| 24243 | `KIND_NOSTR_IDENTITY_BINDING` | one-time identity binding proof |
| 27235 | `KIND_HTTP_AUTH` | NIP-98 HTTP auth |

That overlap is load-bearing rather than trivia. Because `is_ephemeral(22242)` is
`true`, an `EVENT`-submitted AUTH event would otherwise fall into the ephemeral
publish path and be broadcast to subscribers. Both the relay's `EVENT` handler and
`buzz-db`'s insert paths therefore place a dedicated `kind == KIND_AUTH` equality
check **before** the `is_ephemeral` branch, so AUTH is refused outright rather than
fanned out. The lesson generalizes: satisfying `is_ephemeral` is not the same as being
an ephemeral event, and a new kind allocated in this range inherits the ephemeral
handling unless something earlier claims it.

**What this is not.** Ephemerality is *not* a short retention period, a TTL, or an
expiry policy — those describe data that is written and later removed. An ephemeral
event is never written at all. It is also not the same as *replaceable* (kinds 0, 3,
41 and 10000–19999) or *parameterized replaceable* (30000–39999); those ranges
describe events that **are** stored, with a newer event superseding an older one under
a replacement key. Ephemeral events have no stored predecessor to supersede.

## What follows from being ephemeral

**Storage refuses it, three times over.** `buzz-db` applies the same `is_ephemeral`
test at three independent insert call sites — two in `store/event.rs` and one in
`runtime/mod.rs` — each returning `DbError::EphemeralEventRejected`, whose message is
*"ephemeral events (kind {0}) must not be stored"*. This is a defence in the storage
layer itself, not a courtesy check in the relay: a caller that reaches an insert with
an ephemeral kind gets an error rather than a row.

**Delivery skips the database entirely.** The relay's WebSocket `EVENT` handler
branches on `is_ephemeral` and routes to `handle_ephemeral_event`, which returns
before the `ingest_event` call the same function makes for every persistent kind. That
handler verifies the signature, Redis-publishes the event (on the channel topic when
the event carries an `h` tag, on the global topic when it does not), and separately
fans it out to local WebSocket subscribers. The full publish-then-fan-out mechanism,
including the cross-node consumer loop and the local-event de-duplication that keeps a
Redis round-trip from double-delivering, is `architecture-flows-live-fanout`'s subject
and is not restated here.

**Subscribers see only what is published while they are listening.** Since no insert
path accepts the kind, a `REQ` naming an ephemeral kind has no historical backlog to
draw on — it can match only events published live during the subscription. `NIP-AO`
states the client-side consequence normatively for kind 24200: *"historical replay is
not supported"*, and advises subscribing with `since=<now>`.

**It is excluded from the derived surfaces that persistence feeds.** `NIP-AO` extends
the contract beyond storage — no search indexing, no audit-log entry, in-memory
pub/sub only. `NIP-PL` states that ephemeral kinds, presence and typing MUST NOT be
push-eligible. And the `P_GATED_KINDS` doc comment in `kind.rs` records that ephemeral
kinds sit in that set for **filter-layer** enforcement only, because the storage-layer
defence for p-gated kinds (writing a NULL `search_tsv` so the event is unsearchable)
has nothing to act on when no row is written.

## Ephemerality is not the same as WebSocket-only

These two properties are commonly conflated, including in this corpus, and they are
independent. The relay's only gate that is conditioned on transport is:

```rust
if auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE) {
    // "invalid: kind {kind_u32} is only accepted via WebSocket"
}
```

`KIND_GIFT_WRAP` is **1059** — not ephemeral — and `KIND_PRESENCE_UPDATE` is
**20001**. So that gate names two kinds, tests no range, blocks one non-ephemeral
kind, and leaves the other four declared ephemeral kinds untouched.

The rest of the range is nonetheless unreachable over HTTP, by a **separate and
transport-agnostic** mechanism: `required_scope_for_kind` ends in a default arm
returning `Err("restricted: unknown event kind")`, `ingest_event` rejects on that
`Err`, and no ephemeral kind appears in the allowlist above it. `ingest_event` is
shared by both transports — the HTTP bridge and the WebSocket handler both call it —
so ephemeral kinds escape that allowlist over WebSocket **only** because the ephemeral
branch returns before `ingest_event` is reached, not because the allowlist knows
anything about transports.

The practical outcome ("you cannot publish an ephemeral event over HTTP") is therefore
true, but it is produced by three unrelated refusals stacked in sequence, not by a
range check on the HTTP surface. The wire text is how you tell them apart:

| Kind submitted over HTTP | Refusal | Refused by |
|---|---|---|
| 20001 | `invalid: kind 20001 is only accepted via WebSocket` | the transport gate |
| 20002 | `restricted: unknown event kind` | the scope allowlist's default arm |
| 22242 | `invalid: AUTH events cannot be submitted` | a dedicated AUTH check, before either |

Only the first of those three is conditioned on the transport at all.

## Related nodes

Each of these owns a specific ephemeral capability or mechanism; this node defines the
class they belong to and deliberately does not restate them.

| For | See |
|---|---|
| Presence as a capability (kind 20001) | `capabilities-presence-presence` |
| Typing indicators as a capability (kind 20002) | `capabilities-presence-typing-indicator` |
| The Redis state backing presence, and its TTL | `layers-data-redis-presence` |
| The Redis pub/sub carrying typing indicators | `layers-data-redis-typing-indicators` |
| The publish-then-fan-out mechanism ephemeral events ride on | `architecture-flows-live-fanout` |
| The HTTP submission path and its transport gate | `architecture-flows-http-event-submission` |
| The kind registry that declares the range and its members | `implementation-crates-buzz-core` |

## Scope and omissions

### What this node does not cover, and who owns it

| Not covered here | Owned by |
|---|---|
| Presence semantics, heartbeat cadence and expiry | `capabilities-presence-presence`, `capabilities-presence-presence-heartbeat`, `capabilities-presence-presence-expiry` |
| Typing-indicator semantics and lifetime | `capabilities-presence-typing-indicator` |
| Redis key shapes, TTL values and namespacing | `layers-data-redis-presence`, `layers-data-redis-typing-indicators`, `layers-data-redis-key-namespacing`, `layers-data-redis-ttl-policy` |
| The ordered fan-out flow, cross-node delivery and failure behaviour | `architecture-flows-live-fanout` |
| The HTTP event-submission flow end to end | `architecture-flows-http-event-submission` |
| Event kinds as a general concept, and the replaceable and parameterized-replaceable ranges | Sibling tasks in Feature #609, unmerged at this revision and therefore not linked |
| NIP-AB device pairing, NIP-AO agent observer frames and huddle reactions as capabilities | `docs/nips/` and their own capability nodes; only their kind integers are used here |
| Whether the range bounds should be configurable, or the unclaimed integers in the range reserved | Not filed as an issue at the recorded revision |

### Expected to verify and could not

- **Every test touching this behaviour was read, not run.** Two exist and both are
  `#[ignore]`. `test_ephemeral_event_not_stored`
  (`crates/buzz-test-client/tests/e2e_relay.rs`) publishes kind 20001 and asserts a
  following subscription collects nothing, but it needs a live relay with Postgres and
  Redis. `reaction_single_tx_event_insert_failure_rolls_back_reaction`
  (`crates/buzz-db/src/store/reaction.rs`) asserts
  `DbError::EphemeralEventRejected(20000)`, but is marked
  `#[ignore = "requires Postgres"]` and its own subject is transaction rollback, with
  the ephemeral kind used only as a convenient way to force an insert failure. So no
  test dedicated to the never-stored invariant runs in a default pass, and none was
  run here — the invariant is established from the source, not from a green suite.

- **The four in-range credential kinds were identified from the registry alone.** That
  22242, 24242, 24243 and 27235 satisfy `is_ephemeral` is arithmetic and certain, and
  the `KIND_AUTH` guard ordering was read directly. What was *not* traced is whether
  `KIND_BLOSSOM_AUTH`, `KIND_NOSTR_IDENTITY_BINDING` or `KIND_HTTP_AUTH` can reach the
  relay's `EVENT` path at all — their doc comments place them in `upload.rs` and
  `nip98.rs` as request credentials, which suggests they never do, but that path was
  not followed and no claim above depends on it.

- **The historical-replay consequence is reasoned, not observed.** That a `REQ` for an
  ephemeral kind returns no backlog follows from every insert path refusing the kind,
  and `NIP-AO` states it normatively for kind 24200. No query path was traced to
  confirm the relay has no separate cache or replay buffer that could serve one, and
  no live subscription was run. The claim is classified `INFERENCE` for that reason.

- **A merged corpus node is wrong about this node's subject, and fixing it is not this
  task.** `implementation-crates-buzz-ws-client` states as a `FACT` that "the relay
  rejects ephemeral event kinds (20000-29999) over its HTTP surface". Its outcome
  coincidentally holds, but no such range gate exists; the transport gate names kinds
  1059 and 20001, and everything else in the range is refused by the transport-agnostic
  scope allowlist (or, for 22242, by the AUTH check before it). The error originates
  upstream of that node, in the doc comment on
  `publish_ephemeral_event` in `crates/buzz-cli/src/client.rs`, which the node quoted
  faithfully. A third merged node, `architecture-flows-http-event-submission`, already
  states the gate correctly, so two merged nodes disagree. Correcting either the node
  or the doc comment is out of scope here and is reported for separate filing; this
  node's `status` is `draft` rather than `flagged` because the conflict is between
  documentation and code, not between two authoritative sources of the same claim type,
  and `ADR-0029` resolves that case in favour of the code.

- **NIP-01's own text could not be cited.** No upstream numbered NIP specification
  exists anywhere in this repository — `docs/nips/` holds only Buzz's own two-letter
  NIPs. The attribution of the 20000–29999 range to NIP-01 is therefore taken from
  `docs/nips/NIP-AO.md`, which records it, rather than from the upstream spec itself.
