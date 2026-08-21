# Huddle join attribution: what the relay and clients emit today

**Title:** Does the huddle join path identify which member failed, and why
**Summary:** Walks all 17 failure exits and the one success marker on the relay's huddle-audio join path. The relay's logging is far better than expected — 8 exits carry the joiner's pubkey — but none of it reaches an OTLP collector, because the connection runs in a bare `tokio::spawn` with no active span and `tracing-opentelemetry` drops span-less events by design. The desktop client discards the relay's machine-readable error `code` and logs nothing locally; the web client has no huddle surface at all.
**Tags:** `observability` `opentelemetry` `huddle` `buzz-relay` `desktop` `tracing`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#314](https://github.com/launchpad-26/buzz/issues/314)

---

## Finding

Three answers, because the question has three surfaces.

1. **The relay: yes, in stdout logs — and better than the issue predicted.** The join path has an unambiguous success marker and 17 distinct failure exits. Sixteen emit something; **8 carry the joiner's pubkey**. This is not an under-instrumented path.
2. **As telemetry: no. None of it is exported.** The huddle connection body runs in a task spawned by axum with no active span, and `tracing-opentelemetry` explicitly ignores events that have no span. Every one of those 16 emissions lands in stdout JSON and nowhere else — and without `trace_id`/`span_id`, because there is no span context to inject.
3. **The desktop client: no.** It throws away the relay's structured error `code`, relabels every failure as an auth error, and writes nothing locally. The web client cannot join a huddle at all.

The correction that matters: the relay does not need join instrumentation. **It needs a span.** One span wrapping `handle_audio_connection` would make all 16 existing emissions exportable and correlated at once. That is a materially smaller change than instrumenting a path, and it generalises — see [Part 3](#part-3--this-is-not-a-huddle-problem).

---

## Part 1 — The relay's join path, exit by exit

`join.rs` is the cross-pod mesh and owner-dial machinery. The joiner's own admission sequence is `handle_audio_connection` in `handler.rs`. Every emission in the module:

```
$ grep -rn "trace!\|debug!\|info!\|warn!\|error!\|info_span!\|debug_span!\|#\[instrument" crates/buzz-relay/src/audio/
crates/buzz-relay/src/audio/mesh.rs:217:            debug!(
crates/buzz-relay/src/audio/mesh.rs:235:            warn!(%session_id, "empty media datagram payload — dropping");
crates/buzz-relay/src/audio/mesh.rs:278:                debug!(%to, "remote peer datagram send failed: {e}");
crates/buzz-relay/src/audio/mesh.rs:281:        debug!(%to, "remote peer sink closed");
crates/buzz-relay/src/audio/room.rs:444:                tracing::warn!(
crates/buzz-relay/src/audio/handler.rs:93:            warn!(channel_id = %channel_id, "Connection limit reached, rejecting audio WebSocket");
crates/buzz-relay/src/audio/handler.rs:199:                        warn!(channel_id = %channel_id, "auth text frame too large — dropping");
crates/buzz-relay/src/audio/handler.rs:216:            debug!(channel_id = %channel_id, "audio auth timeout or disconnect");
crates/buzz-relay/src/audio/handler.rs:232:            warn!(channel_id = %channel_id, "audio auth failed: {e}");
crates/buzz-relay/src/audio/handler.rs:258:        warn!(channel_id = %channel_id, pubkey = %pubkey_hex, "audio: relay membership denied");
crates/buzz-relay/src/audio/handler.rs:281:            warn!(channel_id = %channel_id, pubkey = %pubkey_hex, "audio membership denied: {e}");
crates/buzz-relay/src/audio/handler.rs:341:                    warn!(
crates/buzz-relay/src/audio/handler.rs:363:                debug!(
crates/buzz-relay/src/audio/handler.rs:396:            debug!(channel_id = %channel_id, "channel archived before room join");
crates/buzz-relay/src/audio/handler.rs:410:            warn!(channel_id = %channel_id, "pre-join channel check failed (fail-closed): {e}");
crates/buzz-relay/src/audio/handler.rs:423:            warn!(
crates/buzz-relay/src/audio/handler.rs:481:                warn!(channel_id = %channel_id, pubkey = %pubkey_hex, "huddle owner rejected registration: {reason:?}");
crates/buzz-relay/src/audio/handler.rs:493:                warn!(channel_id = %channel_id, pubkey = %pubkey_hex, "huddle owner registration failed: {e}");
crates/buzz-relay/src/audio/handler.rs:521:            warn!(channel_id = %channel_id, "audio room full (255 peers exhausted)");
crates/buzz-relay/src/audio/handler.rs:531:            debug!(channel_id = %channel_id, "room ended before admission");
crates/buzz-relay/src/audio/handler.rs:541:            info!(channel_id = %channel_id, pubkey = %pubkey_hex, pinned, requested, "audio: protocol version mismatch — upgrade required");
crates/buzz-relay/src/audio/handler.rs:556:    info!(
crates/buzz-relay/src/audio/handler.rs:597:                    error!(
```

**There is no `info_span!`, no `debug_span!` and no `#[instrument]` anywhere in `crates/buzz-relay/src/audio/`.** That absence is the whole of Part 2.

### The table

Line numbers are `crates/buzz-relay/src/audio/handler.rs`. "Exported at default filter" assumes `BUZZ_OTEL_FILTER`'s documented default, `buzz_relay=info,buzz_datastore=info`, and is answered on level alone — Part 2 then removes all of them for a different reason.

| # | Line | Exit condition | Level | Member id? | Passes default filter? |
|---|---|---|---|---|---|
| 1 | 79–86 | Host maps to no community — 404 before upgrade | **none** | — | **no emission at all** |
| 2 | 93 | Connection semaphore exhausted | `warn` | no — pre-auth | yes |
| 3 | 199 | Auth text frame oversized | `warn` | no — pre-auth | yes |
| 4 | 216 | Auth timeout (5 s) or disconnect | `debug` | no | **no** |
| 5 | 232 | NIP-42 `verify_auth_event` failed | `warn` | **no** — see below | yes |
| 6 | 258 | Relay membership denied | `warn` | **yes** `pubkey` | yes |
| 7 | 281 | Channel membership denied | `warn` | **yes** `pubkey` | yes |
| 8 | 341 | Mesh fence rejected the join | `warn` | **yes** `pubkey` | yes |
| 9 | 363 | `huddle_audio_available=false` under horizontal scaling | `debug` | **yes** `pubkey` | **no** |
| 10 | 396 | Channel archived between membership check and room join | `debug` | no | **no** |
| 11 | 410 | Pre-join channel lookup failed (fail-closed) | `warn` | no | yes |
| 12 | 423 | Client requested unsupported protocol version | `warn` | **yes** + `requested_version`, `current` | yes |
| 13 | 481 | Huddle owner rejected registration | `warn` | **yes** + `reason` | yes |
| 14 | 493 | Huddle owner unreachable | `warn` | **yes** `pubkey` | yes |
| 15 | 521 | Room full — 255 peer indices exhausted | `warn` | no | yes |
| 16 | 531 | Room ended before admission | `debug` | no | **no** |
| 17 | 541 | Room pinned to a different protocol version | `info` | **yes** + `pinned`, `requested` | yes |
| ✅ | 556 | **Success** — `"audio peer joined"` | `info` | **yes** + `peer_index` | yes |

**17 failure exits. 16 emit; 1 is silent. 8 carry the pubkey. 4 are `debug` and invisible at the default filter.** At that filter: 12 visible failure exits, 7 of them member-attributable.

The success marker is directly comparable to the failures, which is what makes a differential diagnosis possible in principle:

```rust
// handler.rs:556
info!(
    channel_id = %channel_id,
    pubkey = %pubkey_hex,
    peer_index,
    "audio peer joined"
);
```

### The auth blind spot is the one that matters

At line 232 the pubkey is genuinely not yet available — `pubkey_hex` is derived at line 245, *after* `verify_auth_event` succeeds. But the client's auth event carries a claimed pubkey which is simply never logged. A member whose NIP-42 auth fails produces:

```
audio auth failed: <err>
```

…with a `channel_id` and no identity, indistinguishable from any other member's auth failure on the same channel. **This is a plausible shape for the motivating fault in [#289](https://github.com/launchpad-26/buzz/issues/289), and it is the one exit that cannot be attributed to a member.**

---

## Part 2 — Why none of it reaches a collector

There *is* an ambient HTTP span, and the huddle route is inside the layer that creates it:

```
$ grep -n "http_trace_layer" crates/buzz-relay/src/router.rs
199:        .layer(http_trace_layer())
203:fn http_trace_layer() -> TraceLayer<HttpMakeClassifier, fn(&Request<Body>) -> tracing::Span> {
522:            .layer(http_trace_layer())
```

```rust
// router.rs:207 — the only span covering /huddle/{channel_id}/audio
fn make_http_span(request: &Request<Body>) -> tracing::Span {
    tracing::info_span!(
        target: "buzz_relay", "http.request",
        otel.kind = "server",
        http.request.method = %request.method(),
    )
}
```

That span covers the **upgrade request**, which completes at the 101 response. The connection body runs in a task axum spawns with nothing attached — `axum 0.8.9`, the version pinned in `Cargo.lock`, at `src/extract/ws.rs:359`:

```rust
    pub fn on_upgrade<C, Fut>(self, callback: C) -> Response
    ...
        tokio::spawn(async move {
            let upgraded = match on_upgrade.await { ... };
            ...
            callback(socket).await;
        });
```

A bare `tokio::spawn` — no `.instrument(Span::current())`. Tokio does not propagate the tracing current-span across a spawn, so `handle_audio_connection` runs with no active span.

And `tracing-opentelemetry 0.33` drops span-less events by design. From the vendored source at `~/.cargo/registry/src/index.crates.io-*/tracing-opentelemetry-0.33*/src/layer.rs`:

```rust
    fn on_event(&self, event: &Event<'_>, ctx: Context<'_, S>) {
        if INSIDE_TRACING.with(|inside| inside.get()) {
            // Ignore reentrant calls.
            return;
        }
        // Ignore events that are not in the context of a span
        if let Some(span) = event.parent().and_then(|id| ctx.span(id)).or_else(|| {
            event
                .is_contextual()
                .then(|| ctx.lookup_current())
                .flatten()
        }) {
```

The comment is the library's own. Consequence: every row in the Part 1 table reaches stdout JSON and nothing else. Per `crates/buzz-relay/src/telemetry.rs`'s `TraceContextJson`, those stdout lines also carry no `trace_id`/`span_id`, because there is no valid span context to inject — so they cannot even be joined to a trace after the fact.

---

## Part 3 — This is not a huddle problem

Every WebSocket route that goes through `on_upgrade` has this structure. The main relay path *does* export, but only because `connection.rs` re-creates per-operation spans by hand inside the spawned task:

```
$ grep -n "span!\|instrument\|info_span" crates/buzz-relay/src/connection.rs | head
563:            let span = tracing::info_span!("ws.auth", conn_id = %conn.conn_id);
565:                .instrument(span)
582:            let span = tracing::info_span!(
593:                .instrument(span),
609:            let span = tracing::info_span!("ws.req", conn_id = %conn.conn_id, sub_id = %sub_id);
615:                .instrument(span),
630:            let span = tracing::info_span!("ws.count", conn_id = %conn.conn_id, sub_id = %sub_id);
636:            .instrument(span),
```

The huddle path never does. Generalised: **relay work inside a spawned task is currently invisible to OTLP however well it is logged**, and only the paths that happen to build their own spans escape that. For scale, the whole workspace contains exactly one `#[instrument]`:

```
$ grep -rn "#\[instrument" crates/*/src | wc -l
       1
```

---

## Part 4 — The clients

### Desktop: three defects, all at one place

The audio socket is opened in Rust, not TypeScript — `desktop/src-tauri/src/huddle/relay_api.rs:56`. Its join-result handling, lines 146–160:

```rust
                        Some("error") => {
                            break Err(format!("audio relay auth error: {}", v["message"]));
                        }
                        _ => continue,
                    }
                }
                Some(Ok(WsMsg::Close(_))) | None => {
                    break Err("connection closed before joined".into());
                }
...
    .map_err(|_| "timeout waiting for joined from relay".to_string())?
```

1. **The relay's `code` is discarded.** The relay sends `{"type":"error","code":"room_full" | "upgrade_required" | "huddle_owner_unreachable" | "join_rejected" | "huddle_audio_unavailable" | "room_ended" | "unsupported_version", "message":…}`. Only `v["message"]` is read. The machine-readable discriminator dies at the client boundary.
2. **Every failure is mislabelled `"audio relay auth error"`.** A room-full rejection, a version mismatch and an unreachable owner all reach the user as an auth error — actively misleading for a bug report.
3. **Nothing is emitted locally.** No `eprintln!` and no `tracing::` call on any of the three error breaks. The string returns to the Tauri command and becomes a toast via `desktop/src/features/huddle/lib/huddleError.ts`, which special-cases only `huddle_audio_unavailable` and otherwise passes the message through. Once dismissed there is no local record — [#289](https://github.com/launchpad-26/buzz/issues/289)'s witnessed problem, in the exact code path of its own acceptance test.

### Web: not applicable

```
$ grep -rni "huddle\|opus\|/audio" web/src | head
$ ls web/src/features
invite
repos
```

No matches. The web client has no huddle surface and cannot be a participant in the acceptance test.

---

## What this means for #289

1. **Criterion 3's relay-side gap is a missing span, not missing instrumentation.** One span around `handle_audio_connection` carrying `channel_id` and `pubkey` makes 16 existing emissions exportable and correlated. It is a change to an upstream file, so it needs an entry in [#273](https://github.com/launchpad-26/buzz/issues/273)'s divergence register.
2. **The scope is wider than huddles.** Any relay work in a spawned task is currently unexportable. Whatever the PRD does about spans should be assessed against that, not against one path.
3. **Two concrete blockers for criterion 3, both nameable:** the auth-failure exit cannot attribute a member (line 232), and the desktop drops the error `code`. Neither is "insufficient instrumentation".
4. **The default filter silently discards a member-attributable rejection.** Exit 9 (`huddle_audio_unavailable`) carries the pubkey at `debug`. Whatever `BUZZ_OTEL_FILTER` becomes should be chosen against the Part 1 table rather than inherited.
5. **The web client is out of the acceptance test**, though it stays in scope for the PRD generally.

---

## Confidence, and what was not checked

**High confidence** on the emission table, the desktop code path and web having no huddle surface: all direct reads of files at `678008ea4`, quoted above.

**High confidence but from reading, not running,** on "nothing is exported". It chains three reads — axum's bare `tokio::spawn`, tokio not propagating the current span across a spawn, and `tracing-opentelemetry`'s own "ignore events that are not in the context of a span". Each link is quoted from source. **It was not observed.** A single run with an OTLP collector and one huddle join would settle it, and that run has not been done.

**Not checked:** no relay was run and no huddle joined; no test in `audio/` was read; the `{e}` interpolations at lines 232, 281 and 410 may carry more than the call site shows, because what `enforce_relay_membership` and `ensure_membership` emit internally was not traced; `room.rs:444` and the post-join emissions from line 597 onward were out of scope; mobile was not examined.

**One open sub-question:** whether `verify_auth_event` in `crates/buzz-auth/` logs the claimed pubkey before rejecting. If it does, exit 5's blind spot is narrower than stated here.
