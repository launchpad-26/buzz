Issue #1132 — task: document layers/networking/slow-client-handling.md
Stated size: no `Size` line on the issue; scope stated unambiguously as exactly one
hand-authored canonical corpus document  ->  cap: 5 steps

ALREADY TRUE  (verified against the worktree at HEAD `29ca9b189bd3f639ba09c972b57c70538c0860c6`,
by direct read, not from notes)

  `launchpad/docs/corpus/layers/networking/slow-client-handling.md` does not exist —
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` carries no
  `layers/networking/slow-client-handling.md`.

  The two knobs the dispatch brief named are real and carry the stated defaults.
  `crates/buzz-relay/src/config.rs` declares `pub send_buffer_size: usize` and
  `pub slow_client_grace_limit: u8` on `Config`, and `Config::from_env` reads
  `BUZZ_SEND_BUFFER` defaulting to `1_000` and `BUZZ_SLOW_CLIENT_GRACE_LIMIT`
  defaulting to `15`. Both use the silent
  `std::env::var(..).ok().and_then(|v| v.parse().ok()).unwrap_or(default)` shape —
  neither routes through the crate's own validating `positive_u64_from_env` helper, so
  an unparseable value falls back to the default without a warning and a literal `0`
  parses and is accepted.

  The mechanism is a per-connection bounded tokio mpsc channel plus a shared
  consecutive-failure counter, not a rate limiter.
  `crates/buzz-relay/src/connection.rs` builds `mpsc::channel::<WsMessage>(state.config.send_buffer_size)`
  for data frames and a separate fixed capacity-8 `ctrl_tx` for Pong/Close, constructs
  `backpressure_count: Arc<AtomicU8>` and stores `grace_limit` from config on
  `ConnectionState`, and passes the *same* `Arc` and grace limit into
  `state.conn_manager.register(...)`.

  Two send sites share that one counter. `ConnectionState::send`
  (`crates/buzz-relay/src/connection.rs`) and `ConnectionManager::try_send_ws_message`
  (`crates/buzz-relay/src/state.rs`, behind `send_to` and `send_to_text_bytes`) each
  `try_send`, reset the counter to 0 on `Ok`, and on `TrySendError::Full` do
  `fetch_add(1) + 1`, warn, and — at `count >= grace_limit` — increment
  `buzz_ws_backpressure_disconnects_total` and call `cancel.cancel()`. The counter is
  *consecutive*: any success resets it.

  The close the client actually receives is bare. `send_loop_inner`'s
  `cancel.cancelled()` branch drains queued control frames, then sends
  `disconnect_reason.borrow().map_or(WsMessage::Close(None), |reason| reason.close_message())`.
  `CommunityDisconnectReason` (`crates/buzz-relay/src/state.rs`) has exactly one
  variant, `CommunityDeleted`, so on a backpressure cancel the watch holds `None` and
  the client gets `Close(None)` — no status code, no reason string.

  Four unit tests in `crates/buzz-relay/src/state.rs` cover the counter's arithmetic:
  `send_to_resets_grace_counter_on_success`, `send_to_increments_grace_counter_on_full`,
  `send_to_cancels_after_grace_limit`, `shared_counter_between_direct_and_fanout`, all
  against `setup_conn`'s hardcoded `grace_limit` of 3.

  `.env.example` (74 `BUZZ_` occurrences, including a "Relay (WebSocket server)"
  section and documented `BUZZ_REDIS_POOL_SIZE` / `BUZZ_DB_POOL_SIZE` tuning entries)
  contains zero occurrences of `BUZZ_SEND_BUFFER` or `BUZZ_SLOW_CLIENT_GRACE_LIMIT` —
  grep exit status 1.

  Merged, greppable relationship targets confirmed present on `origin/launchpad`:
  `architecture-flows-live-fanout`, `architecture-flows-websocket-connection`,
  `implementation-crates-buzz-relay`, `layers-lifecycle-concurrency`,
  `layers-observability-metrics`, `verification-contracts-websocket`.
  The sibling `layers-networking-connection-limits` (#1123) is committed but NOT merged
  and is therefore not a legal target.

STEP 1  Write the front matter for                                          [independent]
        `launchpad/docs/corpus/layers/networking/slow-client-handling.md` with
        `id: layers-networking-slow-client-handling`, `type: layers` (per the batch
        brief's resolved decision 1 — `node.schema.json`'s `type` enum has no `flow`
        member and names the corpus surface, and this node's surface is `layers`),
        `status: draft`, `origin: launchpad`, audiences `agent`/`developer`/`operator`
        (operator earns its place: both knobs are relay-runtime environment variables),
        one provenance `FACT` citing `commit 29ca9b189bd3f639ba09c972b57c70538c0860c6`
        and no second commit-only FACT, and one evidence entry per substantive claim
        drawn only from the ALREADY TRUE block above — every `FACT` citing a bare
        repo-relative path I opened, no line numbers.
        done when: the file's front matter parses as YAML, carries exactly the seven
        schema-permitted keys or fewer, and every `FACT` entry's `evidence` array names
        a path that `test -f` confirms.

STEP 2  Write the flow body per `launchpad/docs/corpus/templates/flow.md`'s   [after 1]
        *Required sections*: Flow statement (trigger = a frame is offered to a
        connection whose writer has not drained; actors = producer, ConnectionState /
        ConnectionManager, the bounded channel, send_loop, the client), Sequence with
        every step cited, a Mermaid `sequenceDiagram`, Outcome covering both the
        recovery path (a single successful `try_send` zeroes the counter) and the
        disconnect path (counter reaches `grace_limit`, metric increments, token
        cancels, `Close(None)` is attempted), and a Boundary paragraph.
        done when: all seven of the template's required sections are present as
        headings, no Sequence step is uncited, and the failure path is narrated as
        explicitly as the success path.

STEP 3  Write Relationships and Scope and omissions.                          [after 2]
        Relationships name only ids re-confirmed by grepping the merged-ids list;
        `architecture-flows-live-fanout` is named in the body as the upstream boundary
        that produces the frames this node's flow disposes of. Scope and omissions
        carries the two distinct things AGENTS.md step 8 requires: (a) what this node
        does not cover and who owns it — connection admission/limits (#1123, unmerged),
        heartbeat liveness (3 missed pongs, a distinct mechanism), the fan-out that
        produces the frames; and (b), separately, what I expected to verify and could
        not — no integration or E2E test exercises a real slow socket end to end,
        `defaults_are_valid` asserts only `> 0` rather than the literal 1000/15, whether
        `ws_send.send(close).await` can complete against a genuinely stalled socket was
        not exercised, and `.env.example` omits both variables.
        done when: every relationship target appears in the merged-ids list, and the
        Scope section visibly separates the ownership boundary from the
        could-not-verify disclosure.

STEP 4  Run `python3 launchpad/project-intelligence/corpus/validate.py`       [after 3]
        from the worktree root and fix whatever it names.
        done when: the command exits 0.

STEP 5  Run the verify-gate stamp as the sole foreground command with a       [after 4]
        600000 ms timeout:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`,
        confirm the final line is `OK` (the mid-run
        `FAIL corpus root does not exist: .../does-not-exist-anywhere` line is a
        negative fixture's own stdout, not a failure), then `git add` + `git commit -s`
        in a separate tool call.
        done when: the suite ends `OK` and `git log -1` shows the commit with a
        `Signed-off-by` trailer.

RISKS
  The recorded revision differs from the batch brief's stated base
  (`96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`) because `origin/launchpad` advanced to
  `29ca9b189bd3f639ba09c972b57c70538c0860c6` before the worktree was cut; `96782d1` is
  an ancestor of HEAD. The provenance entry records the revision the claims were
  actually checked against, which is HEAD — recording the brief's older SHA would
  assert a check that was not made.

  A `FACT` citing a real file that does not support its statement validates cleanly.
  Mitigation: every path cited in this node was opened in this session, and no claim
  is carried over from the dispatch brief without independent re-verification —
  including the two default values the brief said a sibling had already confirmed.

  Atomicity: the heartbeat/missed-pong disconnect and the capacity-8 control-channel
  escalation are adjacent mechanisms. The control channel is folded in (it is the same
  phenomenon — the same stalled writer — and its terminal handling is meaningless
  without the graced data-channel path beside it); the heartbeat is not, and is named
  as a boundary plus reported as a candidate follow-up task.
