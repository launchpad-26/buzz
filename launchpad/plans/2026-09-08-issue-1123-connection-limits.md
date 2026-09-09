# Plan — issue #1123: document `layers/networking/connection-limits.md`

Feature: #609 (protocol and networking layer corpus)
Base: `origin/launchpad` at `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`
Branch: `task/1123-connection-limits`
Worktree: `/home/serina/Launchpad/buzz/__worktrees/task-1123-connection-limits`

## ALREADY TRUE

- `launchpad/docs/corpus/layers/networking/` does not exist on `origin/launchpad`;
  a grep of the merged-id index for `layers/networking` returns zero rows, so this
  node is the first on that surface and may target no sibling from #609.
- The limits themselves already exist in code and were read before drafting:
  - `crates/buzz-relay/src/config.rs` — `max_connections` (default 10 000, env
    `BUZZ_MAX_CONNECTIONS`), `max_concurrent_handlers` (1024,
    `BUZZ_MAX_CONCURRENT_HANDLERS`), `max_frame_bytes`
    (`DEFAULT_MAX_FRAME_BYTES` = 512 KiB, `BUZZ_MAX_FRAME_BYTES`),
    `send_buffer_size` (1000), `slow_client_grace_limit` (15).
  - `crates/buzz-relay/src/state.rs` — both counts become `tokio::sync::Semaphore`
    permits (`conn_semaphore`, `handler_semaphore`).
  - `crates/buzz-relay/src/connection.rs` — permit acquisition, frame-size check
    in `recv_loop`, per-principal admission in `enforce_ws_admission`.
  - `crates/buzz-relay/src/protocol.rs` — `MAX_SUB_ID_LENGTH` 256,
    `MAX_FILTERS_PER_REQ` 10, enforced at parse time.
  - `crates/buzz-relay/src/handlers/req.rs` — `MAX_SUBSCRIPTIONS` 1024,
    `MAX_EXPLICIT_CHANNEL_VALUES` 128.
  - `crates/buzz-relay/src/nip11.rs` — the advertised `limitation` block.
  - `crates/buzz-auth/src/rate_limit.rs` — `RateLimitConfig` tier defaults.
  - `crates/buzz-relay/src/audio/handler.rs` — the audio route's own frame cap
    and its *different* rejection shape on the shared connection semaphore.
- `origin/launchpad` already carries nine merged ids this node can legally target
  (all verified against the merged-id index, none from #609).

## STEP 1 — Fix the node's boundary before writing a word

Connection limits (this node) vs slow-client/backpressure handling (#1132, a
sibling). `slow_client_grace_limit` and `send_buffer_size` are read here only to
name them as #1132's, not to explain them.

**Done when:** the drafted Scope section names #1132 as owner of backpressure and
slow-consumer disconnect, and the body makes no claim about either mechanism.

## STEP 2 — Write the evidence ledger first

One entry per substantive claim, classified per `AGENTS.md`. Exactly one
commit-only FACT (the provenance entry). Every FACT cites a bare repo-relative
path that was actually opened above. The "advertised but untested at runtime"
claims are INFERENCE with honest confidence, not FACT.

**Done when:** every ledger entry maps to a source read in ALREADY TRUE, and no
entry cites a file this plan did not open.

## STEP 3 — Write the body against `templates/concept.md`

Required sections from that template: definition (with explicit scope), use
cases, comparison table of the limit classes, related resources as typed
`relationships`, and Scope and omissions carrying both a boundary table and a
separate "expected but could not verify" list.

**Done when:** the file exists at
`launchpad/docs/corpus/layers/networking/connection-limits.md` with front matter
`id: layers-networking-connection-limits`, `type: layers`, `status: draft`,
`origin: launchpad`.

## STEP 4 — Validate

**Done when:** `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

## STEP 5 — Stamp and commit

**Done when:** `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`, and a
separate `git commit -s` records the node and this plan.

## GATES

- Validator exit 0.
- Corpus unit tests `OK` before the commit, as a separate tool call.
- Every `relationships[].target` present in the merged-id index for
  `origin/launchpad`; zero targets from #609.
- Exactly one hand-authored corpus document added.

## BUDGET

Five steps. One new corpus file plus this plan. No code changes.

## OPEN

- `check_ip_connection` / `LimitType::IpConnections` exist but have no call site.
  `layers-data-redis-ttl-policy` already records that; this node links rather
  than restates it.
- `BUZZ_MAX_CONNECTIONS`, `BUZZ_MAX_CONCURRENT_HANDLERS`, `BUZZ_MAX_FRAME_BYTES`,
  `BUZZ_SEND_BUFFER` and `BUZZ_SLOW_CLIENT_GRACE_LIMIT` are read by `config.rs`
  but absent from `.env.example`. Reported as a candidate follow-up, not fixed
  here — this task adds documentation only.

## LEFT OUT

- Slow-client backpressure and the grace-limit disconnect (#1132).
- HTTP-surface body/pack limits (`BUZZ_GIT_MAX_PACK_BYTES`,
  `BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS`) — a different transport.
- Postgres and Redis pool sizing — already owned by
  `layers-data-postgres-connection-pool` and `layers-data-redis-connection-pool`.
- Any change to `.env.example` or to runtime behaviour.
