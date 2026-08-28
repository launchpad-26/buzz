---
id: architecture-flows-agent-turn
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "On startup the harness spawns N agent subprocesses, sends ACP `initialize` to each, and connects to the relay authenticating via NIP-42, before entering its event loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/relay.rs:591-658"
  - statement: "The harness discovers channels by querying the relay REST API scoped to the agent's own membership (GET /api/channels?member=true by default) and subscribes to each."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "A turn is triggered by a kind:9 event carrying the agent's pubkey in a `#p` tag (an @mention), by a configured heartbeat interval firing on an idle agent, or by an owner control command (`!rotate`) that forces the next event in a channel to start a fresh session."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "Inbound events are subject to an Inbound Author Gate before they reach subscription rules; the default mode is owner-only, and an agent with no registered agent_owner_pubkey drops all events until the owner is resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "Owner control commands (`!shutdown`, `!cancel`, `!rotate`) are checked before the Inbound Author Gate, so the owner can manage the harness regardless of the configured gate mode, and must be kind:9 stream messages from the owner mentioning the agent with a `p` tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "Each channel has at most one prompt in flight at a time; while dedup_mode is Drop (the default), new events for an in-flight channel are silently dropped rather than queued."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/queue.rs:230-252"
  - statement: "flush_next() selects the in-flight-eligible channel with the oldest queued event and drains up to MAX_BATCH_EVENTS (50) of its queued events into one FlushBatch, marking the channel in-flight with an expiry deadline."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/queue.rs:24"
      - "crates/buzz-acp/src/queue.rs:27"
      - "crates/buzz-acp/src/queue.rs:114-124"
      - "crates/buzz-acp/src/queue.rs:260"
  - statement: "run_prompt_task is the core async function spawned per prompt; its documented lifecycle is: (1) resolve or create a session, (2) send an initial message on new channel sessions if configured, (3) fetch conversation context if needed, (4) build the prompt text from the batch plus context, (5) send the prompt with a turn timeout, (6) handle all error paths while always returning the agent via result_tx, including on panic (recovered through the JoinSet)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:1477-2602"
  - statement: "On a new channel session, NIP-AE owner-scoped core memory and channel canvas metadata are fetched once (never mid-session) and folded into the system prompt before session/new is sent, each bounded by its own timeout (3s for core) and failing open (inject nothing) rather than crash or block on relay slowness."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:1477-2602"
      - "crates/buzz-acp/src/engram_fetch.rs"
  - statement: "The assembled prompt is sent to the agent subprocess over the ACP JSON-RPC wire as a session/prompt request, and the agent is expected to use the Buzz CLI (send_message, get_messages, etc.) to act on Buzz while the turn is in flight."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/acp.rs:777-839"
  - statement: "A turn terminates with one of five StopReason values reported by the agent: EndTurn (normal completion), Cancelled (via session/cancel), MaxTokens, MaxTurnRequests, or Refusal -- and a refused turn is dropped from the agent's own history."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:48-60"
  - statement: "At the run_prompt_task level, a turn's outcome is one of six PromptOutcome variants: Ok(StopReason), Error(AcpError), AgentExited, Timeout(TimeoutKind), Cancelled (intentional, via !cancel or interrupt -- no respawn), or CancelDrainTimeout (agent did not stop within its grace window after session/cancel -- treated as poisoned and respawned)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:479-497"
  - statement: "TimeoutKind distinguishes Idle (no ACP wire activity for idle_timeout seconds) from Hard (the turn ran the full max_turn_duration wall-clock budget), and Hard additionally records whether the agent was recently active within a 60-second window before the hard cap fired."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:468-475"
      - "crates/buzz-acp/src/pool.rs:47"
  - statement: "On idle or hard timeout, cancel_with_cleanup_until responds to any pending permission request as cancelled, sends a session/cancel notification, then reads for up to a fixed 30-second cleanup-idle window (bounded by the original hard_deadline) before parsing whatever final response arrives into a StopReason."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1014-1062"
  - statement: "Mid-turn, the main loop can deliver a ControlSignal of Cancel (drop the batch), Interrupt (stop and requeue as a superseding re-prompt), or Steer (stop and requeue as a continuation, the default MultipleEventHandling::Steer path for a message arriving while the agent is already working); a capacity-1 SteerRequest channel additionally allows non-cancelling mid-turn delivery when the agent's transport supports it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:318-339"
      - "crates/buzz-acp/src/pool.rs:377-385"
      - "crates/buzz-acp/src/queue.rs:65-73"
  - statement: "A batch that failed to process is requeued at the front of its channel's queue (preserving fairness position via the original received_at) with exponential backoff (base 5s, capped at 300s); after MAX_RETRIES (10) attempts the batch is dead-lettered -- logged at ERROR and returned to the caller instead of requeued, discarding its events, and retry_after/retry_counts for the channel are cleared so fresh traffic is not throttled by the discarded poison batch."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/queue.rs:411-498"
      - "crates/buzz-acp/src/queue.rs:29"
  - statement: "post_failure_notice publishes a signed Buzz message event into the triggering thread (or channel root) reporting a dead-lettered batch, bounded by a 5-second submit timeout and logging a warning rather than failing the harness if the submit errors or times out."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4244-4276"
  - statement: "Every exit path of run_prompt_task -- normal completion, early return, timeout, or panic recovered via JoinSet -- runs a ReactionGuard (Drop impl) that best-effort clears the 👀/💬 reactions placed on the triggering events, and a TurnCompletionGuard (Drop impl) that emits a turn_completed observer event; the completion guard is declared after the liveness guard specifically so Rust's reverse-drop order stops liveness ticks before the turn is marked terminal."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:3819-3848"
      - "crates/buzz-acp/src/pool.rs:3975-4010"
      - "crates/buzz-acp/src/pool.rs:1477-2602"
  - statement: "On successful completion with usage data and a configured agent_owner_pubkey, the harness publishes a kind:44200 (KIND_AGENT_TURN_METRIC) event whose payload is NIP-AM encrypted to the owner's pubkey, tagged with both the owner (`p`) and the agent's own pubkey (`agent`), bounded by a 3-second submit timeout, and best-effort (a failure only logs a warning)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:4093-4180"
      - "crates/buzz-core/src/kind.rs:545"
  - statement: "kind:44200 (KIND_AGENT_TURN_METRIC) is a compile-time-asserted regular stored kind (not ephemeral, not replaceable, not parameterized-replaceable) and is one of two kinds relay queries gate to the requester's own results."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:545"
      - "crates/buzz-core/src/kind.rs:883-887"
  - statement: "The relay observer bus assigns each turn a local turn_id and, once known, an ACP session_id, and stamps every observer frame for that turn (turn_started, turn_liveness ticks, turn_completed) with the same context so a turn's activity can be correlated end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/observer.rs"
      - "crates/buzz-acp/src/pool.rs:1477-2602"
  - statement: "If the agent subprocess crashes, the harness respawns it; if the relay connection drops, the harness reconnects using a `since` filter so it does not miss events that arrived during the disconnection."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "On restart, the harness replays all unprocessed @mentions since its last run, which can produce a burst of turns if stale events accumulated in a channel while the harness was down."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
  - statement: "Representative tests exercise the turn lifecycle's rollback and ordering guarantees: standing conversational context and per-session delivery state are committed only after ACP reports success, a merged cancel+re-prompt deduplicates all rendered event IDs across the interrupted and superseding batches, a late-arriving successful steer acknowledgement is excluded from the next channel-level wire prompt so it is not double-delivered, and a batch is requeued (not dead-lettered) for the first MAX_RETRIES attempts and only dead-lettered on the (MAX_RETRIES + 1)th failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:5626"
      - "crates/buzz-acp/src/pool.rs:5719"
      - "crates/buzz-acp/src/pool.rs:5837"
      - "crates/buzz-acp/src/pool.rs:6007"
      - "crates/buzz-acp/src/queue.rs:3107"
  - statement: "Whether the ACP subprocess boundary (agent code running as a locally spawned process, communicating over stdio JSON-RPC rather than a network trust boundary) is itself documented anywhere in the corpus as a named trust boundary was not established while writing this node -- no corpus node currently covers it, and it is called out below as a scope gap rather than asserted here."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/pool.rs:1477-2602"
    confidence: 0.7
---

# Agent turn

One **turn** is one round trip through the ACP harness (`buzz-acp`): an inbound trigger is
turned into a `session/prompt` request against a locally spawned agent subprocess, and the
subprocess's response (or its absence) is turned back into Buzz-visible effects -- messages,
reactions, an encrypted usage metric -- plus harness-internal bookkeeping. This node describes
that round trip end to end, as implemented in `crates/buzz-acp/src/{acp,pool,queue,observer}.rs`.

## Trigger

A turn starts from exactly one of three sources:

1. **@mention** -- a kind:9 event carrying the agent's pubkey in a `#p` tag, queued per channel.
2. **Heartbeat** -- an optional configured interval that prompts an idle agent when no events
   are pending; heartbeats are lower priority than queued events, are dropped (not queued) when
   all agents are busy, and at most one heartbeat is in flight harness-wide.
3. **Owner `!rotate`** -- forces the next event on that channel to start a fresh ACP session,
   independent of whether anything is currently queued.

Every inbound event -- @mentions, DMs, thread replies -- passes the **Inbound Author Gate**
before it can queue at all (see *Trust boundaries* below); events from disallowed authors never
reach the queue described in the next section.

## Preconditions

- The channel must already be one the harness is subscribed to (channel discovery happens at
  startup and on membership-notification events; see `crates/buzz-acp/README.md`).
- The triggering author must pass the Inbound Author Gate, or the event is silently dropped
  before queuing.
- At most one prompt may be in flight per channel. Under the default `Drop` dedup mode, a new
  event for a channel that already has a prompt in flight is discarded rather than queued;
  under `Queue` mode it accumulates for the next flush.
- `flush_next()` only selects a channel that is not already in-flight and whose `retry_after`
  backoff (if any) has elapsed.

## Ordered interactions and data movement

1. `EventQueue::push` enqueues the triggering event(s) on the channel's `VecDeque`, capped at
   500 pending events per channel (oldest dropped on overflow).
2. `EventQueue::flush_next` picks the in-flight-eligible channel with the oldest queued event,
   drains up to 50 events into one `FlushBatch`, and marks the channel in-flight with an
   auto-expiring deadline.
3. `run_prompt_task` is spawned for the batch (or for a heartbeat, with no batch). It:
   a. Emits a `turn_started` observer event and starts a liveness ticker.
   b. Resolves the channel's existing ACP session, or creates one. On a **new** channel session
      only, it fetches and folds in NIP-AE owner-scoped core memory and channel canvas metadata
      (each independently timeout-bounded and fail-open), building the system prompt.
   c. Optionally sends a configured initial message on a brand-new session.
   d. Fetches conversation context (thread replies or DM history) when the trigger needs it.
   e. Builds the final prompt text from the batch's events plus fetched context.
   f. Sends `session/prompt` over the ACP JSON-RPC wire to the agent subprocess, tracking an
      idle timeout and a hard per-turn deadline.
   g. The subprocess acts on Buzz via the Buzz CLI (`send_message`, `get_messages`, etc.) while
      the prompt is in flight; the harness only sees ACP wire traffic, not those CLI calls
      directly.
   h. The subprocess's `session/prompt` response is parsed into a `StopReason` (and, for
      standard-adapter agents, into recorded token usage).
   i. On success with usage data and a configured owner, an NIP-AM-encrypted kind:44200 turn
      metric is published, tagged to both the owner and the agent.
   j. `EventQueue::mark_complete` releases the channel's in-flight state; the agent (`OwnedAgent`)
      is always returned to the pool via `result_tx`, including on panic (recovered through the
      `JoinSet`/`task_map`).
4. `TurnCompletionGuard` (a `Drop` impl) emits `turn_completed` on every exit path, and
   `ReactionGuard` (a `Drop` impl) best-effort clears the 👀/💬 reactions placed on the
   triggering events -- both run regardless of how the turn ended.

## Termination and outcome

A turn's ACP-level result is one of five `StopReason` values the agent itself reports:
`EndTurn`, `Cancelled`, `MaxTokens`, `MaxTurnRequests`, `Refusal` (a refused turn is dropped
from the agent's own history by the agent, not by the harness).

At the harness level, `run_prompt_task` classifies the whole attempt into one of six
`PromptOutcome` variants: `Ok(StopReason)`, `Error(AcpError)`, `AgentExited`,
`Timeout(TimeoutKind)`, `Cancelled` (intentional -- `!cancel` or interrupt mode, agent
considered healthy, no respawn), or `CancelDrainTimeout` (agent did not stop within its grace
window after `session/cancel` -- agent process is considered poisoned and respawned, but the
triggering batch's fate still follows its `CancelReason`, not the hard-cap dead-letter path).

## Trust boundaries

- **Relay authentication (NIP-42).** The harness authenticates its own relay connection via
  NIP-42 before it can discover channels or receive events at all.
- **Inbound Author Gate.** Controls which authors' events are even eligible to trigger a turn.
  Default mode is `owner-only`; an agent with no resolved `agent_owner_pubkey` forwards nothing
  until the owner is known. `allowlist`, `anyone`, and `nobody` are the other modes.
- **Owner control commands cross the gate first.** `!shutdown`, `!cancel`, and `!rotate` are
  checked *before* the Inbound Author Gate is applied, so the owner retains control regardless
  of the configured mode -- they must still be kind:9 stream messages mentioning the agent.
- **Owner-scoped encrypted context in.** NIP-AE core memory fetched into the system prompt is
  scoped to the configured `agent_owner_pubkey`.
- **Owner-scoped encrypted telemetry out.** The kind:44200 turn metric is NIP-AM-encrypted to
  the owner's pubkey and tagged to both owner and agent, so only the owner (and the agent that
  produced it) can read it; `KIND_AGENT_TURN_METRIC` is also one of the kinds the relay
  result-gates to the requester's own events.
- **Agent subprocess boundary.** Not established by this node -- see the INFERENCE evidence
  entry above and *Scope and omissions*.

## Failure, abort, and rollback behavior

- **Idle/hard timeout.** `cancel_with_cleanup_until` responds to any pending permission request
  as cancelled, sends `session/cancel`, then drains for a fixed 30-second cleanup window bounded
  by the original hard deadline before resolving a final `StopReason`.
- **Mid-turn control signals.** `ControlSignal::Cancel` drops the triggering batch;
  `Interrupt`/`Steer` stop the turn and requeue the batch as a merged re-prompt, framed as a
  supersede (`Interrupt`) or a continuation (`Steer`, the default for a message arriving while
  the agent is already working). A capacity-1 `SteerRequest` channel additionally allows
  non-cancelling mid-turn delivery when supported.
- **Retry and dead-lettering.** A batch that failed to process is requeued at the front of its
  channel's queue (preserving its original fairness position) with exponential backoff (5s base,
  300s cap). After `MAX_RETRIES` (10) attempts it is dead-lettered: logged at `ERROR`, its
  events discarded, and `post_failure_notice` publishes a signed failure message into the
  triggering thread (5-second submit timeout, best-effort).
- **Cleanup guarantees.** `ReactionGuard` and `TurnCompletionGuard` run on every exit path
  (success, error, timeout, or panic recovered via `JoinSet`), so reaction cleanup and the
  `turn_completed` observer signal are not skippable by any single failure mode.
- **Representative verification:**
  - `crates/buzz-acp/src/pool.rs:5626` (`run_prompt_task_commits_standing_context_only_after_acp_success`)
    and `crates/buzz-acp/src/pool.rs:5719` (`channel_prompt_commits_delivery_state_only_after_acp_success`)
    -- state is committed only after ACP reports success, not before.
  - `crates/buzz-acp/src/pool.rs:5837` (`merged_cancel_prompt_commits_and_deduplicates_all_rendered_event_ids`)
    -- a cancel+merge re-prompt does not double-render events.
  - `crates/buzz-acp/src/pool.rs:6007` (`late_successful_steer_ack_excludes_event_from_next_channel_wire_prompt`)
    -- a late steer ack cannot cause double delivery.
  - `crates/buzz-acp/src/queue.rs:3107` (`test_requeue_dead_letters_after_max_retries`) --
    the retry/dead-letter threshold is exact.

## Scope and omissions

**Covers:** the `buzz-acp` harness's per-turn lifecycle from inbound trigger through
`session/prompt` to termination, cleanup, and telemetry, as implemented today.

**Does not cover:**
- The Buzz CLI surface the agent subprocess calls during a turn (`send_message`,
  `get_messages`, etc.) -- that is the CLI's own contract, not the harness's turn mechanics.
- The ACP wire protocol itself (JSON-RPC method/response shapes) beyond what a turn's
  lifecycle touches.
- Per-adapter differences (goose vs. Codex vs. Claude Code vs. a custom BYOH harness) beyond
  what is common to all of them at the `AcpClient` level.
- Session rotation policy (proactive rotation by turn count) and model-switching mid-session --
  both touch `SessionState` but are not part of a single turn's own lifecycle.
- The full NIP-AE/NIP-AM wire formats -- only that a turn fetches/publishes through them and
  what boundary each crosses.

**Expected but not verified when this node was written:**
- Whether the ACP agent-subprocess boundary (a locally spawned process over stdio, not a
  network peer) is documented anywhere in the corpus as a named trust boundary in its own
  right. No existing merged node covers it; this node names the gap rather than asserting an
  answer, per the INFERENCE evidence entry above.
- No corpus node currently exists under `architecture/` or elsewhere in the merged corpus that
  this node's `relationships` could point at (checked against `origin/launchpad` at the
  revision recorded above: `corpus-readme`, `corpus-agents`,
  `corpus-standard-decision-references`, `corpus-standard-confidence`); `relationships` is
  therefore omitted, not decided to be permanently empty.
