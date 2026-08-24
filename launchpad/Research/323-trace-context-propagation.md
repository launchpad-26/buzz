# Propagating trace context across a transport with no header surface

**Title:** Trace context propagation for Nostr-over-WebSocket in Buzz
**Summary:** The premise is half wrong in a useful way — Nostr WebSocket *messages* have no headers, but the WebSocket *handshake* is an ordinary HTTP request whose headers already reach the relay's handlers, so connection-level propagation needs no wire-format change. It splits by client, though: `tokio-tungstenite` on the desktop can set upgrade headers, the browser `WebSocket` constructor cannot. Per-message propagation would mean a signed, permanently-stored, publicly-readable trace id in a Nostr tag. For the huddle acceptance test, correlation on pubkey and time is probably sufficient.
**Tags:** `observability` `tracing` `context-propagation` `nostr` `websocket` `w3c-trace-context`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#323](https://github.com/launchpad-26/buzz/issues/323)

---

## Finding

**Nostr-over-WebSocket messages genuinely have no header surface — but the WebSocket handshake is an ordinary HTTP request, and its headers already reach the relay's handlers.** Connection-level trace context can therefore be propagated with no wire-format change at all.

That splits by client, and the split is a platform limit rather than a code choice:

- **Desktop** uses `tokio_tungstenite::connect_async`, which accepts a full `http::Request`. Upgrade headers are available.
- **Web** uses the browser `WebSocket` constructor, which cannot set request headers. Upgrade headers are unavailable, permanently.

Per-message propagation is the hard case. The accepted answer is an in-payload envelope correlated with **span links**, which for Nostr means a signed, permanently-stored, publicly-readable trace id in an event tag — a worse trade than it first appears.

**For criterion 3 none of it is strictly needed.** The huddle fault is a connection-establishment failure, so connection granularity is the right granularity, and correlation on identity and time may be sufficient on its own.

---
## Part 1 — What surface actually exists

Four transports, three of which can carry a header:

| Path | Header surface | Available today? |
|---|---|---|
| `POST /events`, `/query`, `/count` (HTTP bridge) | Full HTTP headers | **Yes** |
| WebSocket **handshake** (`GET /`, `GET /huddle/{id}/audio`) | Full HTTP headers on the upgrade request | **Yes** |
| WebSocket **messages** (`["EVENT", {...}]`, `["REQ", ...]`) | None — positional JSON arrays | No |
| Nostr **event tags** | Arbitrary tags, but inside the signed id | Only via a protocol change |

The handshake point is the one that matters and it is verifiable in the code — the audio WebSocket handler already takes the headers:

```
$ grep -n "headers: HeaderMap" crates/buzz-relay/src/audio/handler.rs
67:    headers: HeaderMap,
```

They are already being read for something else (the `Host` header, to bind the community). A `traceparent` on the same request needs no new plumbing to *reach* the relay.

**But nothing extracts it.** There is no propagator configured anywhere in the workspace:

```
$ grep -rn "traceparent\|TraceContextPropagator\|global::set_text_map_propagator" crates/
(no output)
```

So today even the plain HTTP bridge — which has had headers all along — does not join a caller's trace. That is a smaller gap than "the transport has no headers"; it is "nobody has wired the propagator".

## Part 2 — The two published approaches

### A. In-payload envelope, correlated with span links

This is OpenTelemetry's messaging semantic convention, and it is written to be transport-agnostic precisely because many messaging transports lack headers. The normative guidance:

> *"A producer SHOULD attach a message creation context to each message. If possible, the message creation context SHOULD be attached in such a way that it cannot be changed by intermediaries."*

Crucially, the default correlation mechanism is **span links, not parent-child**:

> *"These conventions use spans links as the default mechanism to correlate producers and consumer(s) because: It is the only consistent trace structure that can be guaranteed, given the many different messaging systems models available... It is the only option to correlate producer and consumer(s) in batch scenarios as a span can only have a single parent."*

**What Buzz would have to send:** a `traceparent` value inside the message. For a Nostr `EVENT`, the only structured place is a tag. **For a Nostr `REQ` or the huddle audio frames there is no place at all** without changing the wire format.

**What that costs, and it is worse than it looks.** Tags are part of the event id under NIP-01 — the id is a hash over `[0, pubkey, created_at, kind, tags, content]`. So a `traceparent` tag is:
- a change to the signed payload, i.e. a protocol change, in a format shared with the wider Nostr ecosystem;
- **permanently stored** in the event store alongside the event;
- **publicly readable** by every client that fetches the event, forever.

A trace id is not secret, but it is a correlation handle into the cohort's telemetry, published to everyone who can read the message. That is a strange thing to put in a signed, replicated, permanent record in exchange for tracing.

### B. Connection span plus per-message child spans

The WebSocket-specific pattern in the practitioner literature: a **long-lived connection span** established at the handshake, **child spans for individual messages**, manual context propagation in the payload where per-message linking is needed, and explicit handling of connection lifecycle events.

Half of this is free for Buzz and half is not. The connection span is free — the handshake carries headers, and `connection.rs` already builds per-operation spans carrying `conn_id`:

```
$ grep -n "info_span" crates/buzz-relay/src/connection.rs | head -3
563:            let span = tracing::info_span!("ws.auth", conn_id = %conn.conn_id);
609:            let span = tracing::info_span!("ws.req", conn_id = %conn.conn_id, sub_id = %sub_id);
630:            let span = tracing::info_span!("ws.count", conn_id = %conn.conn_id, sub_id = %sub_id);
```

There is already a connection identity to hang a client's trace on. What is missing is only that the client does not send a `traceparent` and the relay does not read one.

## Part 3 — What correlation with no propagation achieves

Worth stating plainly, because it is the option that costs nothing and it is very likely enough.

With no propagation at all, a human or an agent joins on **pubkey + channel + timestamp**. For the huddle acceptance test that is a strong join, because:

- the relay's join path already logs `pubkey` on 8 of its 17 failure exits and on the success marker ([#314](https://github.com/launchpad-26/buzz/issues/314));
- the comparison criterion 3 asks for is between a handful of members over a window of seconds, not across thousands of interleaved requests;
- the failing and succeeding members are distinguished by *identity*, which is exactly the field already present.

Where it breaks down is high-volume, high-concurrency message flows where two events from the same pubkey in the same second cannot be told apart. That is not the acceptance test.

---

## What this means for #289

1. **Connection-level propagation is the cheap, correct target for the desktop — and it is not blocked by the transport.** A `traceparent` header on the WebSocket upgrade, extracted into the connection's span, joins a client's trace to the relay's. No wire-format change, no protocol change, no signed tag. **It does not extend to the web client** — see Part 4.
2. **It is blocked by something else, though: the huddle path has no span at all.** [#314](https://github.com/launchpad-26/buzz/issues/314) found `handle_audio_connection` runs in a bare `tokio::spawn` with no active span, so there is currently nothing for an extracted context to attach to. **#314's span is a prerequisite for this**, and the two should be done together.
3. **Per-message propagation should be rejected for now, on the evidence rather than on effort.** It requires a signed, permanent, publicly-readable trace id in the Nostr event, for a granularity the acceptance test does not need.
4. **Wire the propagator on the HTTP bridge while you are there.** `POST /events`, `/query` and `/count` have had full headers all along and extract nothing. That is a one-line configuration gap, not a design problem.
5. **Do not let "no propagation" be dismissed.** For criterion 3 it is probably sufficient, and it is available the moment the relay's spans are exported at all. It is a reasonable first milestone, with propagation as a second.

---

## Confidence and what is still unknown

**High confidence** on the surfaces: the header availability, the absent propagator, and the existing `conn_id` spans are all direct greps quoted above.

**High confidence** on the semantic-convention guidance, quoted from the specification.

**Moderate confidence** on the NIP-01 id-computation claim.** I did not find the id computation in `crates/buzz-core/src/event.rs` — Buzz uses the `nostr` crate's event types rather than defining its own — so "tags are covered by the signed id" is stated from the NIP-01 specification rather than from Buzz's code. It is a well-established property of the format, but I did not verify it in this codebase and someone should before acting on point 3.

**Not verified:** nothing was run. No `traceparent` was sent, no propagator was configured, and no correlation was observed end to end. The client header capability was flagged as the most important unchecked fact and then checked — Part 4 records the result, which changed a recommendation rather than confirming it.

**Not researched:** whether any Nostr NIP already reserves a tag for correlation or tracing; whether the mesh datagram path between relay pods needs its own propagation story; W3C Baggage as distinct from Trace Context; and what other Nostr implementations do about tracing, which would be the most relevant prior art and which I did not find.

## Part 4 — The client asymmetry, checked

Both desktop sockets use `tokio_tungstenite::connect_async`, whose argument is `IntoClientRequest` — a bare URL today, but it accepts a full `http::Request` with arbitrary headers:

```
$ grep -n "tungstenite\|connect_async" desktop/src-tauri/src/native_websocket.rs | head -4
7:use tokio_tungstenite::{
8:    connect_async,
132:        result = tokio::time::timeout(CONNECT_TIMEOUT, connect_async(url)) => result

$ grep -n "connect_async\|tungstenite" desktop/src-tauri/src/huddle/relay_api.rs | head -3
15:use tokio_tungstenite::{connect_async, tungstenite::Message as WsMsg};
68:    let (ws_stream, _) = connect_async(&ws_url)
```

The web client cannot do the same:

```
$ grep -rn "new WebSocket" web/src --include='*.ts'
web/src/shared/lib/nostr-client.ts:45:    const ws = new WebSocket(wsUrl);
```

The browser `WebSocket` constructor takes a URL and an optional subprotocol list. It cannot set request headers, by design — there is no API and no workaround.

For the web client the remaining options are a **query parameter** (works, but the trace id then appears in relay access logs and any intervening proxy, and nothing extracts it automatically), the **subprotocol field** (settable, but it is a negotiation list and stuffing a trace id into it is an abuse a strict server would reject), the **same-origin telemetry path** from [#321](https://github.com/launchpad-26/buzz/issues/321) (browser telemetry reaches the relay over ordinary HTTP carrying a `traceparent`, while the WebSocket carries none, and the relay joins the two because it sees both), or **no propagation**.

The same-origin option is the one that composes — it is the conclusion #321 reached from the browser-security direction, arriving again from the propagation direction. Two independent questions pointing at one design is worth noticing.

---

## Sources

- [Semantic conventions for messaging spans — OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/) — creation context, "cannot be changed by intermediaries", span links as the default correlation mechanism
- [OTEP 0205 — messaging semantic conventions: context propagation](https://github.com/open-telemetry/oteps/blob/main/text/trace/0205-messaging-semantic-conventions-context-propagation.md) — the design rationale behind the above
- [Context propagation — OpenTelemetry](https://opentelemetry.io/docs/concepts/context-propagation/) — propagators and the general model
- [How to Trace WebSocket Message Flows with Per-Message OpenTelemetry Context Propagation — OneUptime](https://oneuptime.com/blog/post/2026-02-06-websocket-message-context-propagation-opentelemetry/view) — the connection-span-plus-child-spans pattern and the message-envelope approach
- [How to Trace WebSocket Connections and Real-Time Events with OpenTelemetry — OneUptime](https://oneuptime.com/blog/post/2026-02-06-trace-websocket-connections-realtime-events-opentelemetry/view) — connection lifecycle handling
