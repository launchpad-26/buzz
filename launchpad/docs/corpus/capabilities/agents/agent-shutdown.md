---
id: capabilities-agents-agent-shutdown
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum carries no flow member; the merged flow template establishes that a flow-shaped instance node -- one narrating an ordered runtime interaction -- carries type: architecture instead, extending the same precedent the C4 architecture triad set, and architecture-flows-agent-turn.md is a real merged instance node following exactly that precedent."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/architecture/flows/agent-turn.md"
  - statement: "An owner triggers a graceful shutdown by sending a kind:9 stream-message event whose trimmed content is exactly \"!shutdown\" and which mentions the agent's own pubkey in a tag; is_owner_control_command checks kind, content and mention, and the harness separately requires the sending pubkey to equal the resolved owner before sending on the shutdown channel -- a message containing \"!shutdown\" from a non-owner falls through to ordinary prompt handling instead of being dropped or triggering shutdown."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2737-2760"
      - "crates/buzz-acp/src/lib.rs:3641-3650"
  - statement: "A configured whole-harness inactivity bound also triggers the same shutdown path: on each inactivity_reaper timer tick, if inactivity_expired is true (the bound has elapsed since last_activity with no turn or heartbeat in flight and the bound is non-zero), the harness logs and sends on the identical shutdown_tx channel the owner !shutdown command uses. The bound is zero (disabled) unless configured via --exit-after-inactivity / BUZZ_ACP_EXIT_AFTER_INACTIVITY."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3008-3026"
      - "crates/buzz-acp/src/lib.rs:1613-1620"
  - statement: "Ctrl-C (SIGINT) and, on Unix, SIGTERM are each independently wired to the same shutdown_tx channel via a dedicated tokio signal-handling task spawned at harness startup, so an operator's terminal interrupt and an orchestrator's terminate signal both drive the identical graceful-shutdown sequence as the owner !shutdown command and the inactivity timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2315-2332"
  - statement: "A crashed agent subprocess is detected reactively, not proactively: the NDJSON stdout reader yielding None (end of stream) is read as AcpError::AgentExited at two call sites in the ACP transport; no code anywhere in the crate inspects a child's ExitStatus or calls .success() on one, so a crash and a clean process exit are indistinguishable by exit code -- only by the stdout pipe closing outside of an explicit shutdown() call."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1199-1200"
      - "crates/buzz-acp/src/acp.rs:1519"
  - statement: "AcpClient::shutdown is the sole per-agent kill path: it sends SIGKILL to the agent subprocess's entire process group (the child was spawned with process_group(0) on Unix so its PID equals its PGID, and with kill_on_drop(true)), falling back to a direct start_kill() on non-Unix or once the child has already been polled to completion, then waits a bounded 5 seconds for the process to be reaped before logging a warning and abandoning the wait -- there is no SIGTERM-then-SIGKILL grace ladder for the agent subprocess itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:422-444"
  - statement: "The agent subprocess is spawned in its own process group specifically so that a SIGKILL to that group does not propagate to the harness's own process group; kill_on_drop(true) additionally makes a best-effort kill happen if an AcpClient is dropped without shutdown() ever being called, though the doc comment on shutdown() states callers MUST still call it for guaranteed cleanup."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:468-470"
      - "crates/buzz-acp/src/acp.rs:519-523"
  - statement: "Once shutdown_tx fires by any trigger, the harness runs one fixed graceful-shutdown sequence, in order: re-send the shutdown signal (to cancel any in-flight lazy-pool wake task); drain wake tasks under a 30-second timeout, aborting and tearing down any pool that finished waking late; drain in-flight prompt tasks under a separate 30-second grace period, calling AcpClient::shutdown on every agent the drain returns; if that grace period expires, abort remaining prompt tasks and still shut down whatever they return; explicitly shut down any agents still idle in pool slots and drop the pool; abort in-flight respawn tasks and shut down whatever they return; cancel the presence-heartbeat task; publish a presence \"offline\" event (best-effort, bounded to 2 seconds); abort the relay-observer publisher task; call relay.shutdown() (a graceful WebSocket close); then log \"buzz-acp stopped\" and return Ok(())."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3420-3541"
  - statement: "relay.shutdown() sends a Shutdown command over an internal channel and waits for the background WebSocket task's own join handle to complete, so the relay connection is closed with an actual WebSocket close frame rather than the connection being aborted outright."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs:959-980"
  - statement: "Presence is published as an ephemeral kind:20001 (KIND_PRESENCE_UPDATE) Nostr event whose content is a bare status string (\"online\"/\"away\"/\"offline\"); the relay stores this in Redis and synthesizes it back on presence queries, so the durable side effect of the harness's own \"offline\" publish during shutdown lands in the relay's Redis state, not in a database write the harness itself performs."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:74-91"
      - "crates/buzz-acp/src/lib.rs:3518-3530"
  - statement: "On AcpError::AgentExited specifically, classify_control_cancel_failure sets invalidate_all = true, clearing every ACP session tracked for that agent and forcing a fresh session/new on next use; every other classified failure (idle timeout, cancel-drain timeout, a bounded hard-timeout translated defensively into cancel-drain-timeout, or any other error) invalidates only the one session whose turn triggered it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:3708-3756"
  - statement: "A crash (AgentExited or an equivalent respawn-triggering outcome) and a task panic both feed the same per-slot circuit breaker: SlotCircuit::record_crash opens the circuit after CIRCUIT_BREAKER_THRESHOLD (3) crashes within a CIRCUIT_BREAKER_WINDOW of 60 seconds, holds it open for a CIRCUIT_BREAKER_COOLDOWN of 300 seconds (5 minutes), then allows one half-open probe respawn; while a slot's circuit is open it is left empty rather than respawned, and respawn backoff otherwise starts at RESPAWN_BASE_DELAY (1 second) and is capped at RESPAWN_MAX_DELAY (30 seconds)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:1389-1398"
      - "crates/buzz-acp/src/lib.rs:4412-4428"
  - statement: "A run_prompt_task that panics is recovered through the JoinSet rather than crashing the harness: recover_panicked_agent clears any wedged in-flight channel or heartbeat state, emits an \"agent_panic\" observer event carrying outcome \"panic\", and then feeds the same record_crash/circuit-breaker decision an ordinary stdout-EOF crash would, per its own comment that panics count as crashes for the circuit breaker."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:4349-4428"
  - statement: "No Postgres, sqlx or diesel usage appears anywhere in buzz-acp's own source; the only externally visible state changes this node describes -- the offline presence event and the relay WebSocket close -- are effected as Nostr events and a protocol-level close over the harness's relay connection, not as a direct database write the harness performs itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/lib.rs:74-91"
      - "crates/buzz-acp/src/relay.rs:959-980"
    confidence: 0.75
  - statement: "Representative test coverage of this node's subject is partial: inactivity_tests (zero_disables_expiry_and_in_flight_turns_defer_it, dispatched_activity_restarts_the_inactivity_bound) and idle_pool_sleep_tests cover the inactivity/idle-sleep trigger-decision logic in isolation, and owner_control_command_tests's owner_control_command_requires_kind_content_and_agent_mention covers is_owner_control_command's kind/content/mention gate -- but that test does not exercise the separate owner-pubkey-equality check that gates the actual shutdown_tx send, and no test in the crate directly asserts on AcpClient::shutdown's process-group SIGKILL-and-5-second-wait behavior or on the whole-harness graceful-shutdown sequence end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:1650-1691"
      - "crates/buzz-acp/src/lib.rs:5217-5265"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-flows-agent-turn
---

# Agent shutdown: flow

One **shutdown** is the ordered termination, graceful or otherwise, of the agent
subprocess(es) a `buzz-acp` harness owns, together with the harness-level cleanup and
Nostr-visible state change that accompanies it. This node describes that termination end
to end, as implemented in `crates/buzz-acp/src/{lib,acp,pool,relay}.rs`. It sits beside
`architecture-flows-agent-turn` (the per-turn round trip a shutdown must drain) rather than
duplicating it -- this node covers what happens to that turn's agent when the harness
itself is stopping, not the turn's own lifecycle.

## Trigger

A shutdown starts from exactly one of five sources, all of which converge on sending a
value into the same `shutdown_tx` watch channel:

1. **Owner `!shutdown` command.** A kind:9 stream-message event whose trimmed content is
   exactly `!shutdown`, mentioning the agent, from a pubkey equal to the resolved owner.
2. **Configured inactivity bound.** An `inactivity_reaper` timer tick finds the configured
   bound elapsed with no turn or heartbeat in flight (disabled by default; zero means never).
3. **SIGINT (Ctrl-C).** Caught by a dedicated signal-handling task at startup.
4. **SIGTERM (Unix only).** Caught by a second, parallel signal-handling task.
5. **Individual agent-subprocess crash or panic**, which does not by itself stop the
   harness -- it drives a *per-slot* respawn/circuit-breaker decision, described under
   *Failure, abort, and rollback behavior* below, distinct from the whole-harness shutdown
   the first four triggers start.

A message merely containing the text `!shutdown` from a non-owner pubkey is not dropped
and does not trigger shutdown -- it falls through to ordinary prompt handling.

## Preconditions

- For the owner-command trigger, the harness must already have resolved an
  `agent_owner_pubkey` (via NIP-OA attestation or the `--agent-owner` configuration) --
  `is_owner_control_command`'s kind/content/mention check and the separate
  owner-pubkey-equality check are both evaluated against whatever owner value is
  currently cached; a harness with no resolved owner cannot recognize the command as a
  shutdown trigger it is authorized to honor.
- For the inactivity trigger, `config.exit_after_inactivity_secs` must be configured
  non-zero; the check is a no-op (never expires) at its default of zero.
- The five triggers are independent and any one firing is sufficient -- no combination or
  ordering among them is required.

## Ordered interactions and data movement

1. **Trigger fires** by one of the five routes above, each independently sending `()` into
   the shared `shutdown_tx` watch channel.
2. **Re-send the signal** once more inside the shutdown sequence itself, so that an
   in-flight lazy-pool "wake" task (spawned to refill an idle pool) observes it and cancels
   promptly rather than being aborted mid-spawn.
3. **Drain wake tasks**, bounded to a 30-second timeout; on timeout the remaining wake
   tasks are aborted instead, and any pool a wake task finished spawning just before being
   aborted is torn down explicitly.
4. **Drain in-flight prompt tasks**, bounded to a separate 30-second grace period (chosen
   deliberately shorter than `max_turn_duration`, so a slow turn cannot make shutdown hang
   for up to an hour): every agent a completing prompt task returns has `AcpClient::shutdown`
   called on it, reaping its subprocess. On grace-period expiry the remaining prompt tasks
   are aborted, and any results that still arrive afterward are drained and shut down too.
5. **Shut down idle agents** still sitting in unused pool slots, then drop the pool.
6. **Abort in-flight respawn tasks** (mid-backoff-sleep or mid-`spawn_and_init`) so no new
   agent subprocess is spawned after the shutdown sequence has begun; any respawn result
   that already completed just before the abort is drained and shut down too.
7. **Cancel the presence-heartbeat task**, then **publish a presence "offline" event**
   (kind:20001, best-effort, bounded to a 2-second timeout) if presence is enabled.
8. **Abort the relay-observer publisher task.**
9. **Call `relay.shutdown()`**, which sends a `Shutdown` command internally and waits for
   the relay's background WebSocket task to finish closing the connection with a real close
   frame.
10. **Log `"buzz-acp stopped"` and return `Ok(())`**, ending the harness process.

## Diagram

```mermaid
sequenceDiagram
    participant Owner as Owner (Nostr pubkey)
    participant OS as OS signal / timer
    participant Main as buzz-acp main loop
    participant Pool as AgentPool
    participant Acp as AcpClient (agent subprocess)
    participant Relay as Relay connection

    alt owner command
        Owner->>Main: kind:9 "!shutdown" (mentions agent)
    else inactivity / SIGINT / SIGTERM
        OS->>Main: inactivity_reaper tick / SIGINT / SIGTERM
    end
    Main->>Main: shutdown_tx.send(())
    Main->>Pool: drain wake tasks (30s bound)
    Main->>Pool: drain in-flight prompt tasks (30s grace)
    Pool->>Acp: AcpClient::shutdown()
    Acp->>Acp: SIGKILL process group, wait up to 5s
    Main->>Pool: shut down idle slots, drop pool
    Main->>Pool: abort respawn tasks
    Main->>Relay: publish presence "offline" (2s bound)
    Main->>Relay: relay.shutdown()
    Relay-->>Main: WebSocket close frame sent
    Main->>Main: log "buzz-acp stopped", return Ok(())
```

## Outcome

**Success (graceful path).** Every agent subprocess the harness owned has had
`AcpClient::shutdown()` called on it (SIGKILL to its process group, reaped or abandoned
after a bounded 5-second wait); no respawn or wake task remains outstanding; a presence
"offline" event has been published (best-effort) if presence was enabled; the relay
WebSocket connection has been closed with a close frame; and the harness process returns
`Ok(())` after logging `"buzz-acp stopped"`.

**Failure path: an individual agent subprocess crashes or its task panics**, independent
of a whole-harness shutdown. The crash is observed as `AcpError::AgentExited` (stdout EOF)
or, for a panic, recovered through the `JoinSet`. `AgentExited` invalidates every ACP
session tracked for that agent; a panic additionally clears wedged in-flight
channel/heartbeat bookkeeping and emits an `"agent_panic"` observer event. Both then feed
the same circuit breaker: under the crash threshold, the slot is respawned (with
exponential backoff between 1 and 30 seconds); once the circuit opens (3 crashes within 60
seconds), the slot is left empty for 5 minutes before one half-open probe respawn is
allowed. This node does not establish what happens when every slot's circuit is open
simultaneously -- see *Scope and omissions*.

**Failure path: a bounded step inside graceful shutdown times out.** Three of the ten
ordered steps above are individually bounded (wake-task drain at 30s, prompt-task drain at
30s, presence-offline publish at 2s) and a timeout on any of them does not abort the whole
sequence -- it logs a warning and the sequence proceeds to abort/drain whatever remains,
continuing through to `relay.shutdown()` and the final log line regardless.

## Trust boundaries

- **Owner authorization on the shutdown trigger itself.** `is_owner_control_command`
  checks only kind, exact content, and agent mention -- it performs no authorization
  check. The separate, second condition -- the sending pubkey equals the harness's
  resolved `owner_cache` value -- is what actually gates whether the event is honored as
  a shutdown command; a `!shutdown` message from any other pubkey is treated as an
  ordinary chat message, not silently dropped and not honored.
- **The owner-pubkey cache is resolved once per harness process, at startup**, not
  re-verified per respawn or per shutdown attempt. This node makes no claim about
  whether a respawned agent subprocess re-establishes owner trust beyond the ACP
  protocol handshake -- see *Scope and omissions*.
- **The agent-subprocess boundary itself** (a locally spawned process communicating over
  stdio, not a network peer) is not established as a named trust boundary by this node;
  `architecture-flows-agent-turn` already names this same gap for the per-turn flow, and
  it applies identically here.

## Failure, abort, and rollback behavior

- **Individual agent crash or panic never aborts the whole-harness shutdown sequence** --
  the two are independent. A crash mid-shutdown is reaped the same way any other agent is
  during the prompt-task and idle-slot drain steps; a panic recovered via `JoinSet` during
  normal (non-shutdown) operation instead runs `recover_panicked_agent` and the
  circuit-breaker respawn decision described under *Outcome* above.
- **Every bounded step inside the graceful sequence fails open, not closed.** A timed-out
  wake-task drain, prompt-task drain, or presence-offline publish each logs a warning and
  the sequence continues to its next step rather than halting -- there is no rollback of
  steps already completed, and the sequence always reaches `relay.shutdown()` and the
  final log line.
- **Representative verification** (partial -- see *Scope and omissions* for what is not
  covered by any existing test):
  - `crates/buzz-acp/src/lib.rs:1650-1691` (`inactivity_tests`) -- the inactivity-bound
    trigger-decision logic (`inactivity_expired`) in isolation, including that a bound of
    zero disables expiry and an in-flight turn defers it.
  - `crates/buzz-acp/src/lib.rs:5217-5265` (`owner_control_command_requires_kind_content_and_agent_mention`)
    -- `is_owner_control_command`'s kind/content/mention gate, though not the separate
    owner-pubkey-equality check that actually authorizes the shutdown.
  - No test was found exercising `AcpClient::shutdown`'s process-group SIGKILL-and-5-second-wait
    mechanics, nor the whole-harness graceful-shutdown sequence end to end.

## Boundary

This node does not describe:
- **The standing structure of the `buzz-acp` harness or the agent subprocess it spawns** --
  see the architecture node `architecture-containers-agent-runtime` for that.
- **A turn's own lifecycle** -- resolving a session, building a prompt, dispatching
  `session/prompt`, and classifying its `StopReason`/`PromptOutcome` -- see the flow node
  `architecture-flows-agent-turn`. This node only describes what happens to a turn that is
  still in flight when shutdown begins (drained under the 30-second grace period).
- **The interface contract a shutdown command crosses** (the ACP JSON-RPC wire, or the
  relay's kind:9 stream-message surface) in general, durable terms independent of this one
  scenario -- no interface-typed corpus node exists yet to reference for either surface, so
  the gap is named here rather than a node guessed at.
- **The wire contract of kind:9 (stream message) or kind:20001 (presence update)** as
  Nostr event kinds in their own right -- no event-kind-typed corpus node exists yet to
  reference for either.
- **How the harness starts up or spawns its initial agent pool** -- only how it stops.

## Relationships

- `references` → `architecture-containers-agent-runtime`: the container whose subprocess
  this node's every step acts on.
- `references` → `architecture-flows-agent-turn`: the sibling flow whose in-flight
  instances this shutdown sequence drains, and whose `AgentExited`/panic outcome
  vocabulary this node's failure-path section reuses rather than re-deriving.

## Scope and omissions

**This node covers** what triggers a `buzz-acp` harness shutdown (owner command,
inactivity, SIGINT, SIGTERM), the harness's fixed ten-step graceful-shutdown sequence, the
per-agent SIGKILL-and-bounded-wait kill mechanics, the Nostr-visible state change
(presence "offline", relay WebSocket close), and how an individual agent crash or panic is
distinguished in effect (session invalidation, circuit breaker) from a whole-harness
shutdown.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The standing structure of the harness and agent-subprocess containers | `architecture-containers-agent-runtime` |
| A turn's own request/response lifecycle | `architecture-flows-agent-turn` |
| The ACP wire protocol's own contract | Not yet a corpus node (interface-typed, unassigned) |
| Nostr kind:9 and kind:20001's own wire contracts | Not yet corpus nodes (event-kind-typed, unassigned) |
| How the harness starts up and spawns its initial pool | Not yet a corpus node |

**Expected but not verified when this node was written:**

- **What happens when every agent slot's circuit breaker is simultaneously open** (all
  agents dead, none mid-respawn) was referenced from log-message text found while reading
  the circuit-breaker code (`"all agents dead — exiting"`), but the exact code path and
  conditions for a whole-harness exit triggered purely by every slot being dead were not
  independently traced and confirmed line-by-line, so no citation for that specific
  behavior is included above.
- **Whether the whole-harness graceful-shutdown sequence has any dedicated end-to-end
  test** was checked by reading the crate's test modules named around shutdown/inactivity
  behavior; none was found that exercises the ten-step sequence itself (as opposed to its
  individual trigger-decision predicates), and none was found asserting on
  `AcpClient::shutdown`'s SIGKILL/process-group/5-second-wait mechanics directly.
- **Whether a new agent-subprocess respawn after a crash re-establishes any owner
  authorization beyond the ACP protocol handshake** (for example, re-verifying a NIP-OA
  attestation) was not established; the owner-pubkey cache used to authorize `!shutdown`
  is resolved once per harness process at startup, not per subprocess respawn, but this
  node makes no claim about respawn-time re-authentication because that behavior was not
  directly traced for this node's own subject.
