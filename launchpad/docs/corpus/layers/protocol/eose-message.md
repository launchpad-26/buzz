---
id: layers-protocol-eose-message
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
  - statement: "RelayMessage::eose builds the wire frame as the two-element JSON array [\"EOSE\", <sub_id>], carrying the subscription id and nothing else -- no count, no cursor, no timestamp."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "The relay emits EOSE from exactly four sites, all inside handlers/req.rs: the end of normal historical delivery, a mid-scan database error that aborts the remaining filters, the end of a NIP-50 search response, and an immediate short-circuit when a search request resolves to no accessible channel scope at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "handle_req registers the subscription -- inserting it into the connection's subscription map, registering it with the shared sub_registry, and retaining its pubsub topic -- BEFORE it constructs or executes any historical database query, and sends EOSE only after every filter's rows have been post-processed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A NIP-50 search REQ is diverted before subscription registration into handle_search_req, whose doc comment states that search subscriptions are one-shot and that no persistent subscription is registered, so its EOSE terminates the subscription's entire output rather than opening a live phase."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "A database error on any one filter's historical query causes handle_req to log the failure server-side, send EOSE, and return without processing the remaining filters, so a truncated result set and a genuinely empty tail reach the client as the identical frame sequence."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The historical/EOSE path and the live fan-out path reach the socket through two different functions but one shared sender: ConnectionState::send_tx and ConnEntry::tx are clones of the same mpsc::Sender created at connection setup, and ConnEntry's backpressure_count field carries the doc comment 'Shared with ConnectionState -- both direct sends and fan-out broadcasts track the same consecutive-full counter.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "Because the subscription is live for the entire duration of the historical scan, an event published during that scan is fanned out onto the same outbound sender the pending EOSE will later use, so a client can receive a live event before EOSE and cannot tell it apart from a replayed one on the wire."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
    confidence: 0.8
  - statement: "An event committed to storage after the subscription registers but before the historical query reads can be returned by that query AND pushed by fan-out, and the handler's seen_ids deduplication set covers only rows returned within the historical scan, so it cannot suppress the fan-out copy."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
    confidence: 0.7
  - statement: "buzz-ws-client parses the frame into RelayMessage::Eose { subscription_id }, whose doc comment names it the 'End-of-stored-events marker for a subscription'; the client type preserves only the subscription id, discarding nothing because the frame carries nothing else."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "buzz-test-client's collect_until_eose accumulates every EVENT frame bearing the matching subscription id and returns that accumulated vector the moment the matching EOSE arrives, so it classifies whatever arrived first as the stored set without any independent check that those events were in fact stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs"
  - statement: "e2e_relay.rs's test_stored_events_returned_before_eose asserts that an event published before a subscription opens is present in the set collected up to EOSE, and test_eose_sent_for_empty_subscription asserts that a subscription matching nothing still receives EOSE with zero events; both are marked #[ignore] and require a live relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "No test in crates/buzz-test-client/tests asserts that the main relay sends EOSE before any live EVENT on a subscription; a grep across that directory for the ordering assertions used elsewhere in the repository returned no matches."
    entry_class: FACT
    evidence:
      - "grep_rn(pattern='first message must be EOSE\\|EOSE first\\|before any EVENT', path='crates/buzz-test-client/tests/') -> no output, exit status 1"
  - statement: "The ephemeral pairing sidecar takes the opposite ordering deliberately: buzz-pair-relay sends EOSE before pushing the subscription onto its registry, both under the same lock, and its integration suite asserts that the first frame a subscriber receives must be EOSE."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
      - "crates/buzz-pair-relay/tests/integration.rs"
  - statement: "NIP-RS states a normative 'delivery barrier' requirement: before a relay sends end-of-stored-events for a query, every event it accepted before that query read its stored events, and which matches an open subscription on the same connection, MUST already have been delivered to that subscription."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-RS.md"
  - statement: "NIP-ER's worked AUTH-gated read transcript shows EOSE terminating the stored phase of an ordinary REQ and a later EVENT arriving on the same subscription id afterwards, illustrating the marker's two-phase role rather than a subscription-ending role."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md"
  - statement: "No upstream numbered Nostr specification is present in this repository: docs/nips/ contains only Buzz's own two-letter NIPs, and a listing filtered for a numbered NIP filename returned nothing."
    entry_class: FACT
    evidence:
      - "ls_grep(path='docs/nips/', pattern='NIP-[0-9]') -> no output, exit status 1"
  - statement: "Issue #1150 requires this node to define the term in one sentence before deeper explanation, to state boundaries and what the concept must not be confused with, and to link rather than duplicate neighbouring implementation and verification nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1150 definition of done"
relationships:
  - type: references
    target: architecture-flows-historical-query
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: verification-contracts-nostr
---

# The EOSE message

`["EOSE", <subscription_id>]` is the relay→client frame that marks the end of
the stored-event phase of one subscription: after it, the relay has finished
replaying what it already had, and anything further on that subscription id is
a newly published event.

## Definition

The frame is two elements and nothing more. `RelayMessage::eose` in
`crates/buzz-relay/src/protocol.rs` builds it as
`["EOSE", <sub_id>]` — a literal type tag and the subscription id the client
chose in its `REQ`. There is no count, no cursor, no timestamp, and no status.
Everything EOSE communicates, it communicates by *position in the stream*: the
frames before it were the answer to a question about the past, the frames after
it are notifications about the present.

**Scope of this node.** It covers what the marker means, when the relay emits
it, and — the part that actually bites — what its position does and does not
guarantee. It does not cover the two flows on either side of it. The historical
scan that precedes it is `architecture-flows-historical-query`; the live
delivery that follows it is `architecture-flows-live-fanout`. Both are merged
corpus nodes and are linked as `references` rather than summarised here.

**What it must not be confused with.** EOSE is not a terminator. A subscription
that has EOSEd is still open and still registered; `CLOSE` from the client, or
`CLOSED` from the relay, ends it. Nor is EOSE a success signal — see *A marker,
not a verdict* below.

## Use cases

A client needs the marker for exactly one reason: **the two phases require
different handling and look identical on the wire.** An `EVENT` frame replayed
from storage and an `EVENT` frame pushed live are byte-identical in shape; only
their position relative to EOSE distinguishes them. So a client that wants to

- render a scrollback before showing "live" state,
- resolve a request/response query and stop waiting,
- or establish a mutation fence before reading a full state,

has no other signal to key on. `crates/buzz-ws-client/src/message.rs` parses the
frame into `RelayMessage::Eose { subscription_id }` and its doc comment names it
the "End-of-stored-events marker for a subscription" — the client type carries
only the id, because the frame carries only the id.

Every consumer in this repository uses the marker positionally.
`collect_until_eose` in `crates/buzz-test-client/src/lib.rs` accumulates every
`EVENT` bearing the matching subscription id and returns that accumulation the
instant the matching `EOSE` lands. Note what it does *not* do: it never
independently establishes that those events were stored. It calls whatever
arrived first the stored set. That is the ordinary reading of the marker, and
the next section is about where that reading is thinner than it looks.

## Is there a race around the boundary?

This is the question the marker's position actually raises, and `handle_req` in
`crates/buzz-relay/src/handlers/req.rs` settles the important half of it
directly.

**The subscription is registered before the historical query runs.** In source
order, `handle_req` inserts the subscription into the connection's map,
registers it with the shared `sub_registry` (channel-scoped or global), and
retains its pubsub topic — and only *then* builds the per-filter `EventQuery`
values, executes them, post-processes the rows, and finally sends EOSE.

**So an event cannot be missed.** There is no interval in which the subscription
is not yet live but the historical scan has already read past the event.
`architecture-flows-historical-query` records this same ordering as a deliberate
step and states the reason; that is its claim to own, and this node relies on it
rather than re-arguing it.

**The cost is paid on the other side of the trade.** Registration-first buys
the no-gap guarantee by accepting the opposite hazard, and two consequences
follow for the marker specifically:

1. **A live event can arrive before EOSE.** The two paths reach the socket
   through different functions — `ConnectionState::send` in
   `crates/buzz-relay/src/connection.rs` for the historical rows and the EOSE,
   `ConnectionManager::send_to_text_bytes` in `crates/buzz-relay/src/state.rs`
   for fan-out — but onto **one** bounded sender. `ConnectionState::send_tx` and
   the connection registry's `ConnEntry::tx` are clones of the same
   `mpsc::Sender`, created together at connection setup; `ConnEntry`'s own doc
   comment records the consequence, noting that its backpressure counter is
   "shared with `ConnectionState`" because "both direct sends and fan-out
   broadcasts" go through it. So an event published while the scan is still
   running is fanned out to the already-registered subscription and its frame is
   queued ahead of the EOSE that has not been sent yet. On the wire it is
   indistinguishable from a replayed one. "Everything before EOSE is history" is
   therefore a very good approximation and not an invariant.

2. **The same event can be delivered twice.** An event committed after
   registration but before the scan reads is eligible for both paths. The
   handler's `seen_ids` set deduplicates only across the filters of one
   historical scan — it has no knowledge of what fan-out sent — so it cannot
   suppress the second copy. Deduplicating by event id is the client's job, and
   it is a job the client cannot skip.

Both of those are the honest shape of the trade, not defects: a duplicate is
recoverable by a client that keys on event id, and a gap is not recoverable at
all.

**The contrast that proves it is a choice.** `crates/buzz-pair-relay/src/lib.rs`
— the ephemeral pairing sidecar — does the opposite, sending EOSE *before*
pushing the subscription onto its registry, both under one lock, and its
integration suite asserts that the first frame a subscriber sees must be EOSE.
That relay stores nothing, so it has no historical phase to lose an event
inside, and the strict ordering costs it nothing. Two relays in one repository,
two orderings, each correct for its own storage model.

## A marker, not a verdict

EOSE says the stored phase is over. It does not say the stored phase succeeded.

`handle_req` emits EOSE from four sites, and only one of them is the ordinary
end of a complete scan:

| Emission site | What the client sees |
|---|---|
| End of normal historical delivery | Complete stored set, then EOSE |
| Mid-scan database error on any one filter | Rows from filters that had already finished, then EOSE — remaining filters are never run |
| End of a NIP-50 search response | Search hits, then EOSE, and no live phase at all |
| Search resolving to no accessible channel scope | EOSE immediately, zero events |

The second row is the one to hold onto: a truncated result set and a genuinely
empty tail arrive as the identical frame sequence, with the error visible only
in the relay's own logs. `architecture-flows-historical-query` owns that failure
shape and documents it as such; it is named here because it is a limit on what
this marker can be read to mean, which is this node's subject.

The third and fourth rows are a different limit. A search `REQ` is diverted into
`handle_search_req` *before* registration, and that function's own doc comment
states search subscriptions are one-shot with no persistent subscription
registered. So for a search, EOSE is the end of the output, not the start of a
live phase — the two-phase reading of the marker simply does not apply.
`verification-contracts-nostr` holds the test contract for that search-lane
behaviour.

## Buzz's own normative requirement on the marker

`docs/nips/NIP-RS.md` states a **delivery barrier** in terms of
end-of-stored-events: before a relay sends it for a query, every event the relay
accepted before that query read its stored events, and which matches an open
subscription on the same connection, MUST already have been delivered to that
subscription. NIP-RS's reasoning is that push delivery alone promises only
eventual arrival, and the barrier is what places the arrival *before* the
verdict that depends on it.

That is a requirement on the ordering discussed above, written down inside this
repository, and it is the strongest statement available here about what EOSE
must mean. Whether the relay actually satisfies it is a separate question this
node could not answer — see the omissions below.

`docs/nips/NIP-ER.md` carries a worked AUTH-gated read transcript showing the
ordinary two-phase shape end to end: `EVENT`, then `EOSE`, then a later `EVENT`
on the same subscription id.

## Scope and omissions

**This node covers** the EOSE frame's shape, its meaning, the four sites the
relay emits it from, and what its position in the stream does and does not
guarantee.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The historical scan that precedes the marker — authorization, query construction, per-event visibility, failure shapes | `architecture-flows-historical-query` |
| The live fan-out that follows it, including send-time access re-derivation | `architecture-flows-live-fanout` |
| The `REQ` message itself, subscription lifecycle, and filter semantics | Sibling tasks under Feature #609, none merged at the recorded revision |
| The relay crate's broader responsibilities | `implementation-crates-buzz-relay` |
| The WebSocket client's message handling generally | `implementation-crates-buzz-ws-client` |
| The NIP-50 search lane's test contract | `verification-contracts-nostr` |

**No upstream Nostr specification is cited as a repository path**, because none
is present. `docs/nips/` holds only Buzz's own two-letter NIPs; a directory
listing filtered for a numbered NIP filename returns nothing. Where this node
states a normative requirement about the marker, it cites `NIP-RS.md`, which is
Buzz's own and is a real openable file here.

**Expected but not verified when this node was written:**

- **Whether NIP-RS's delivery barrier actually holds in `buzz-relay`.** The
  requirement is written down; no test, assertion, or code comment tying the
  implementation to it was found. Registration-before-scan is a necessary
  condition and clearly deliberate, but the historical query is also clamped to
  a page limit and bounded by any `until` the filter carries, so an event
  accepted just before the read could in principle be pushed off the returned
  page. Whether fan-out then closes that hole before EOSE depends on the
  interleaving of two independent tokio tasks, which was not traced to a
  conclusion and is not asserted anywhere. Treat the barrier as stated intent,
  not as established behaviour.
- **No test asserts EOSE precedes any live event on the main relay.** A grep
  across `crates/buzz-test-client/tests/` for the ordering assertions used in
  the pair-relay suite returned no matches. The two EOSE tests that do exist —
  `test_stored_events_returned_before_eose` and
  `test_eose_sent_for_empty_subscription` in `e2e_relay.rs` — assert presence
  and emptiness respectively, not exclusion of live frames, and both are
  `#[ignore]`-gated behind a live relay.
- **Duplicate delivery around the boundary was reasoned about, not observed.**
  The claim rests on reading the two code paths and the shared send channel; no
  test exercises it and no relay was run for this node. It is classified
  `INFERENCE` in the ledger for that reason.
- **No unit test in `req.rs` covers EOSE.** The only EOSE assertion inside the
  relay crate is `protocol.rs`'s own serialization test, which checks the two
  array elements and nothing about when the frame is sent.
