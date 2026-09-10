---
id: layers-protocol-notice-message
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
  - statement: "RelayMessage::notice formats a NOTICE as the two-element JSON array [\"NOTICE\", message] whose only payload is a human-readable string, while every sibling formatter in the same impl block that answers a specific client action -- ok, closed, eose and count -- takes an identifier argument (an event id or a subscription id) that the emitted frame then carries."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "At the recorded revision the relay crate emits NOTICE from eight production sites: six through RelayMessage::notice (parse failure, EVENT semaphore exhaustion, COUNT semaphore exhaustion and the request_rejection_message fallback in connection.rs; insufficient scope and unauthenticated REQ in handlers/req.rs) and two as raw JSON literals for oversized text and binary frames in connection.rs; the seventh RelayMessage::notice occurrence is inside protocol.rs's own #[cfg(test)] module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/protocol.rs"
      - "grep_r('RelayMessage::notice(', include='*.rs', path='crates/') -> 7 matches: connection.rs x4, handlers/req.rs x2, protocol.rs x1 inside #[cfg(test)]"
  - statement: "The two oversized-frame NOTICEs are built as raw JSON string literals rather than through RelayMessage::notice, and each is immediately followed by a break that ends the receive loop, so the frame is never parsed and the connection closes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "request_rejection_message(sub_id, reason) returns CLOSED(sub_id, reason) when a subscription id is available and NOTICE(reason) when it is not, and the unit test req_rejections_are_subscription_scoped asserts both branches produce exactly those two frames for the same reason string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_text_message maps any ClientMessage::parse error to NOTICE(\"invalid message: {e}\") and returns, and ClientMessage::parse rejects a REQ or COUNT whose subscription id exceeds MAX_SUB_ID_LENGTH or whose filter list exceeds MAX_FILTERS_PER_REQ by returning RelayError::InvalidMessage before the parsed message value is constructed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "Because parse aborts before binding the subscription id into a ClientMessage::Req value, an over-limit REQ is answered with an uncorrelated NOTICE even though the wire frame did contain a usable subscription id, and no test in the repository exercises that composed emit path."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/protocol.rs"
      - "grep_r('\"invalid message', include='*.rs', path='crates/') -> 1 match, the emit site in crates/buzz-relay/src/connection.rs; no occurrence in any test"
    confidence: 0.8
  - statement: "handle_req sends NOTICE(\"restricted: insufficient scope\") and NOTICE(\"auth-required: authenticate before subscribing\") each immediately followed by a CLOSED on the same subscription id, so those two NOTICEs are advisory companions to a correlated frame rather than the only response the client receives."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "The desktop relay session acts on an inbound NOTICE only by string-prefix match -- notice.startsWith(\"rate-limited:\") arms the rate-limit gate -- and parseRateLimitHint extracts seconds from the pattern /retry in (\\d+)s/i, returning null when no such hint is present so the gate falls back to its ten-second default."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
      - "desktop/src/shared/api/relayRateLimitGate.ts"
  - statement: "The ACP harness logs every NOTICE at warn level and prefix-matches \"rate-limited:\" to arm its own gate, and because -- in its own words -- \"the relay's rate-limit NOTICE does not carry an event ID\" and \"NOTICE has no event ID\", requeue_observer_in_flight moves every unacknowledged observer frame back onto the pending queue rather than only the frame that was actually rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
  - statement: "The web client parses NOTICE and deliberately does nothing with it, commenting \"Informational notice from relay -- ignore for now\"; the interactive test client prints it to stdout; and buzz-ws-client parses it into the RelayMessage::Notice variant that no other module in that crate consumes."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
      - "crates/buzz-test-client/src/main.rs"
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "Both Rust relay-message parsers default a missing message element to the empty string via unwrap_or(\"\"), so a bare [\"NOTICE\"] frame parses as a Notice carrying an empty message rather than as an error, and a unit test in crates/buzz-acp/src/relay.rs asserts exactly that for its copy of the parser."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
      - "crates/buzz-acp/src/relay.rs"
  - statement: "NIP-AA, a Buzz-authored NIP held in this repository, states that when an AUTH payload is too malformed to yield a parseable event id the relay MUST close the WebSocket connection \"optionally preceded by a NOTICE message\", and names this an explicit exception to NIP-42's requirement that AUTH messages be answered with OK because that requirement \"is impossible to satisfy without a parseable event id to reference\"."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AA.md"
  - statement: "No upstream numbered NIP text is present in this repository, so no claim in this node about what NIP-01 itself requires can rest on a file here."
    entry_class: FACT
    evidence:
      - "ls(docs/nips/) -> 24 entries (22 .md, 2 .json), every NIP code alphabetic (NIP-AA through NIP-WP); zero files match ^NIP-[0-9]+.md$"
  - statement: "The desktop native WebSocket batcher's test only_the_auth_challenge_bypasses_the_batch_window asserts that a [\"NOTICE\",\"AUTH required\"] frame must not force a flush, so a NOTICE rides the ordinary batch window rather than being delivered out of band."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/native_websocket_batch.rs"
  - statement: "The merged node verification-contracts-websocket records as explicitly unestablished whether relay reason strings are stable API surface a client should match on \"versus free-form NOTICE text that may change\", noting that nothing in the repository documents these strings as a versioned contract."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/verification/contracts/websocket.md"
  - statement: "The rate-limited: prefix is therefore a de-facto client-visible contract -- two independent clients branch on it and change their queueing behaviour as a result -- that no test, schema or document in the repository declares as versioned."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/verification/contracts/websocket.md"
      - "desktop/src/shared/api/relayClientSession.ts"
      - "crates/buzz-acp/src/relay.rs"
    confidence: 0.7
  - statement: "crates/buzz-relay/src/handlers/moderation_notices.rs defines a ModerationNotice type whose values are moderation messages delivered to users as Nostr events, sharing the word notice with but bearing no relation to the NIP-01 NOTICE wire frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "buzz-pair-relay, the ephemeral NIP-AB pairing sidecar, carries its own make_notice helper with seven call sites emitting [\"NOTICE\", ...] frames independently of buzz-relay's RelayMessage."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "Issue #1160's definition of done requires exactly one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links rather than duplicated content, a check against the recorded provenance revision, a clean validator run, a one-sentence definition before deeper explanation, and an explicit statement of boundaries and of what the concept must not be confused with."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1160 definition of done"
relationships:
  - type: references
    target: verification-contracts-websocket
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: implementation-crates-buzz-acp
---

# The `NOTICE` message

A **`NOTICE`** is a relay-to-client frame of the form `["NOTICE", <message>]` whose
entire payload is one human-readable string, and it is the only relay response in
Buzz's WebSocket vocabulary that carries **no correlation handle** — nothing in the
frame identifies the event, subscription or request that provoked it.

That absence is the whole concept. Everything else about `NOTICE` — where the relay
emits it, what a client can do about it, why two clients ended up parsing English
prose to react to it — follows from the fact that the frame has one field and that
field is prose.

## Definition

`RelayMessage::notice` in `crates/buzz-relay/src/protocol.rs` builds the frame as a
two-element JSON array: the literal `"NOTICE"`, then a message string. The formatters
around it in the same `impl` block tell the story by contrast. Every sibling that
answers a *specific* client action takes an identifier argument and puts it on the
wire: `ok` takes an event id, `closed` and `eose` take a subscription id, `count`
takes a subscription id. `notice` takes only text.

So a client receiving a `NOTICE` knows *something* happened at the relay. It does
not know to what.

**What a `NOTICE` is not:**

- **It is not an error response to a request.** It has no request to attach to. A
  relay that answers a specific frame usually has a correlated form available and
  uses it; `NOTICE` is what is left when it does not.
- **It is not the moderation notice.** `crates/buzz-relay/src/handlers/moderation_notices.rs`
  defines a `ModerationNotice` type — bans, timeouts, report resolutions — delivered
  to users as Nostr *events*, not as this frame. The two share only a word.
- **It is not owned solely by `buzz-relay`.** `buzz-pair-relay`, the ephemeral NIP-AB
  pairing sidecar, has its own `make_notice` helper with seven call sites. This node
  describes the main relay's frame; the sidecar's is a separate implementation of the
  same protocol shape.
- **It is not specified here.** No upstream numbered NIP text lives in this
  repository — `docs/nips/` holds only Buzz's own alphabetic-coded NIPs. Every claim
  below is about what *Buzz* does, read out of Buzz's source.

## Where the relay emits one

At the recorded revision there are **eight production emit sites**, all in
`crates/buzz-relay`. Six go through `RelayMessage::notice`; two are raw JSON string
literals.

| Trigger | Message | Where | Then what |
|---|---|---|---|
| Text frame exceeds `max_frame_bytes` | `error: frame too large (N bytes, limit M)` | `connection.rs` (raw literal) | `break` — receive loop ends, connection closes; the frame is never parsed |
| Binary frame exceeds `max_frame_bytes` | `error: binary frame too large (…)` | `connection.rs` (raw literal) | `break` — same |
| `ClientMessage::parse` fails | `invalid message: <parse error>` | `connection.rs` | Return; connection stays open |
| EVENT rejected by the handler semaphore | `rate-limited: too many concurrent requests` | `connection.rs` | Return |
| COUNT rejected by the handler semaphore | `rate-limited: too many concurrent requests` | `connection.rs` | Return |
| Admission quota or shared-limiter failure with no subscription id in hand | `rate-limited: quota exceeded; retry in Ns` / `rate-limited: shared admission unavailable` | `connection.rs`, via `request_rejection_message` | Return |
| REQ from a principal without the `MessagesRead` scope | `restricted: insufficient scope` | `handlers/req.rs` | Followed by a `CLOSED` on the same subscription id |
| REQ on an unauthenticated connection | `auth-required: authenticate before subscribing` | `handlers/req.rs` | Followed by a `CLOSED` on the same subscription id |

The seventh occurrence of `RelayMessage::notice` in the tree is inside
`protocol.rs`'s own `#[cfg(test)]` module and emits nothing.

Two things are worth reading out of that table.

**The last two rows are not really uncorrelated.** `handle_req` sends the `NOTICE`
*and* a `CLOSED` naming the subscription. The `NOTICE` there is an advisory
duplicate; a client that ignores `NOTICE` entirely still learns what happened, from
the `CLOSED`. Those are the rows where `NOTICE` is a courtesy rather than the only
channel available.

**The fallback row is where the concept is written down explicitly.**
`request_rejection_message(sub_id, reason)` returns `CLOSED(sub_id, reason)` when a
subscription id is available and `NOTICE(reason)` when it is not — the same reason
string, degraded to the uncorrelated form purely because there is nothing to correlate
against. The unit test `req_rejections_are_subscription_scoped` in `connection.rs`
pins both branches. That function is the clearest single statement in the codebase of
what `NOTICE` is *for*: it is the response of last resort.

## The parse-failure case, where a handle exists but is unreachable

`handle_text_message` maps any `ClientMessage::parse` error to
`NOTICE("invalid message: …")`. `ClientMessage::parse` rejects a REQ or COUNT whose
subscription id exceeds `MAX_SUB_ID_LENGTH`, or whose filter list exceeds
`MAX_FILTERS_PER_REQ`, by returning before the parsed message value is built.

The consequence is worth stating plainly: **a REQ that names a perfectly good
subscription id but carries eleven filters is answered with a `NOTICE`, not a
`CLOSED`.** The correlation handle was on the wire. It never reached the code that
had to respond, because parsing aborted first. A client that opened three
subscriptions and gets back `["NOTICE","invalid message: REQ contains 11 filters,
maximum is 10"]` must work out for itself which of the three it just lost.

This is the sharpest illustration of the concept, and it is also the least tested:
the string `"invalid message"` appears exactly once in the whole `crates/` tree — at
the emit site — and in no test at all.

## What clients actually do with one

Nothing, mostly. Where they do act, they act on **prose**.

| Client | Behaviour on `NOTICE` |
|---|---|
| Desktop (`desktop/src/shared/api/relayClientSession.ts`) | `notice.startsWith("rate-limited:")` arms the rate-limit gate; `parseRateLimitHint` pulls seconds out of `retry in Ns` and returns `null` otherwise, falling back to a ten-second default. Anything not starting with that prefix is dropped. |
| ACP harness (`crates/buzz-acp/src/relay.rs`) | Logs every `NOTICE` at `warn`, then prefix-matches `rate-limited:` to arm its own gate. |
| Web (`web/src/shared/lib/nostr-client.ts`) | Parses it, then deliberately nothing — "Informational notice from relay — ignore for now". |
| `buzz-ws-client` (`crates/buzz-ws-client/src/message.rs`) | Parses into `RelayMessage::Notice`; no other module in the crate consumes the variant. |
| Test client (`crates/buzz-test-client/src/main.rs`) | Prints it. |

Both parsers default a missing second element to the empty string, so a bare
`["NOTICE"]` is a `Notice` with an empty message rather than an error.

And the ACP harness pays the concept's cost in code. Its own comments name the
reason — *"the relay's rate-limit NOTICE does not carry an event ID"*, *"NOTICE has
no event ID"* — and its response is to give up on precision:
`requeue_observer_in_flight` pushes **every** unacknowledged observer frame back onto
the pending queue, not the one that was actually rejected, because it cannot tell
which one that was. An `OK`-correlated rejection would requeue one frame. A `NOTICE`
requeues all of them.

The desktop batcher, meanwhile, treats `NOTICE` as ordinary traffic:
`only_the_auth_challenge_bypasses_the_batch_window` asserts that a
`["NOTICE","AUTH required"]` frame must *not* force a flush.

## Why the shape is like this

`docs/nips/NIP-AA.md` — one of Buzz's own NIPs, and a real file in this repository —
reasons about exactly this situation from the other direction. It states that when an
AUTH payload is too malformed to yield a parseable event id, the relay MUST close the
connection, *"optionally preceded by a `NOTICE` message"*, and calls this an explicit
exception to NIP-42's requirement that AUTH be answered with `OK`, because that
requirement *"is impossible to satisfy without a parseable event id to reference."*

That is the general rule in miniature. The correlated forms all require an identifier
the relay has successfully extracted. When extraction is what failed, the correlated
form is unavailable by construction, and `NOTICE` is the only thing left to say.

## Consequences worth knowing

- **A `NOTICE` cannot be routed.** A client with several in-flight requests cannot
  attribute it, and must either ignore it or apply it connection-wide. Both real
  consumers chose connection-wide.
- **Acting on one means parsing English.** The `rate-limited:` prefix is a de-facto
  client-visible contract: two independent clients branch on it and change their
  queueing behaviour as a result. Nothing in the repository declares it as versioned.
  `verification-contracts-websocket` recorded this as unestablished — whether reason
  strings are stable API surface "versus free-form NOTICE text that may change" — and
  the evidence here does not settle it either; it only shows the dependency is real.
- **Two `NOTICE`s mean the connection is already gone.** The oversized-frame pair
  `break` the receive loop immediately after sending, so those are farewell messages,
  not diagnostics on a live connection.

## Scope and omissions

**This node covers** what a `NOTICE` frame is, the property that distinguishes it
from every other relay response, the complete set of places `buzz-relay` emits one at
the recorded revision, and what each client does on receipt.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `OK` message and its acknowledgement semantics | Its own node, drafted under Feature #609 and not merged at this revision |
| The `CLOSED` message and subscription-termination semantics | Its own node, drafted under Feature #609 and not merged at this revision |
| `buzz-pair-relay`'s independent `make_notice` emitter and the pairing flow it serves | `implementation-crates-buzz-pair-relay` and the NIP-AB pairing surface |
| `ModerationNotice` — the moderation DM body, a different concept sharing the word | `crates/buzz-relay/src/handlers/moderation_notices.rs`; no corpus node at this revision |
| Whether relay reason strings are versioned API surface | Unresolved; recorded as unestablished by `verification-contracts-websocket` |
| The admission and rate-limiting model that produces the `rate-limited:` reasons | The admission/rate-limiting surface, not this frame |

**No relationship to the `OK` or `CLOSED` nodes.** Both are drafted under this
Feature and neither is merged on `origin/launchpad` at the recorded revision, so an
edge to either would be a hard validation error in CI. The contrast drawn above rests
on `protocol.rs`'s formatter signatures, read directly, not on those nodes' content.
Those edges belong in a later pass once the Feature merges.

**Expected but not verified when this node was written:**

- **No test anywhere exercises the parse-failure emit path.** `"invalid message"`
  occurs once in `crates/`, at the emit site. The claim that an over-limit REQ is
  answered with `NOTICE` rather than `CLOSED` is composed from two code paths that
  were each read directly, and is classified `INFERENCE` for that reason — it is not
  backed by a passing test, and no test was run while authoring this node.
- **No test covers a client's `NOTICE` handling end to end.** The desktop rate-limit
  gate has unit tests for `parseRateLimitHint`, but nothing was found that drives a
  real `NOTICE` frame through `relayClientSession.ts` or the ACP harness and asserts
  the gate arms. The E2E relay tests treat `NOTICE` only as noise to tolerate
  (`e2e_relay.rs`, `e2e_nostr_interop.rs`, `nip42_host_binding_live.rs` all skip past
  it), so no end-to-end evidence of client reaction exists.
- **The empty-message default was verified by test only in `buzz-acp`'s parser.**
  `buzz-ws-client`'s `parse_relay_message` uses the identical `unwrap_or("")`, read
  directly, but no equivalent test for it was located in that crate.
- **`max_frame_bytes` was not traced to its configured default.** The oversized-frame
  rows above are stated in terms of the config value, not a number, because the
  configuration surface was not opened.
- **No relay was run.** Every claim here comes from reading source at the recorded
  revision; no `NOTICE` frame was observed on a live connection.
