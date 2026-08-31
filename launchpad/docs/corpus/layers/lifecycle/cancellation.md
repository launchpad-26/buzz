---
id: layers-lifecycle-cancellation
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "tokio_util::sync::CancellationToken is imported and used as the cooperative-cancellation primitive in multiple, unrelated parts of the codebase, including crates/buzz-relay/src/connection.rs, crates/buzz-relay/src/audio/join.rs, crates/buzz-relay/src/audio/handler.rs, and crates/buzz-dev-mcp/src/shell.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:12"
      - "crates/buzz-relay/src/audio/join.rs:49"
      - "crates/buzz-relay/src/audio/handler.rs:12"
      - "crates/buzz-dev-mcp/src/shell.rs:14"
  - statement: "docs.rs's own reference documentation for tokio_util::sync::CancellationToken states of cancel(): 'Cancel the CancellationToken and all child tokens which had been derived from it. This will wake up all tasks which are waiting for cancellation,' and of cancelled(): 'Returns a Future that gets fulfilled when cancellation is requested... will complete immediately if the token is already cancelled when this method is called' -- the cooperative pattern every call site cited in this node follows: hold a clone or child of a shared token, and race cancelled() against the work in a select!."
    entry_class: FACT
    evidence:
      - "https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html"
  - statement: "docs.rs's reference documentation for child_token() states: 'Unlike a cloned CancellationToken, cancelling a child token does not cancel the parent token,' while cancelling the parent still cancels every child derived from it -- a directed, one-way propagation distinct from a plain .clone(), where cancelling any clone cancels every other clone (they are the same token)."
    entry_class: FACT
    evidence:
      - "https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html"
  - statement: "ConnectionState carries one CancellationToken field (cancel), documented in its own doc comment as the 'Token used to signal graceful shutdown of this connection's tasks,' created once per WebSocket connection in handle_connection and cloned into every task that must observe it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:79-80"
      - "crates/buzz-relay/src/connection.rs:132"
  - statement: "ConnectionState::send cancels its own connection's token directly (self.cancel.cancel()) once a slow client's outbound buffer has been full for grace_limit consecutive sends, logging 'sustained backpressure — closing slow client' first -- a self-contained, per-connection trigger with no external signal or process-wide event involved."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:95-118"
  - statement: "handle_active_connection spawns a dedicated auth-timeout task that races tokio::time::sleep(AUTH_TIMEOUT) against the same connection's auth_timeout_cancel.cancelled() in one tokio::select!; if the sleep wins and the connection is still unauthenticated, the task itself calls auth_timeout_cancel.cancel() to close the connection, logging 'NIP-42 auth timeout — closing connection' -- a second, independent trigger on the identical token, sourced from a locally-owned deadline rather than an externally observed condition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:251-272"
  - statement: "After recv_loop returns (the connection's own read side reached EOF, a protocol error, or a client-initiated close), handle_active_connection explicitly calls cancel.cancel() before awaiting the send, heartbeat, and auth-timeout tasks' join handles -- demonstrating a third trigger shape: an orderly local exit path proactively cancelling every sibling task rather than one of them cancelling in reaction to a condition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:274-286"
  - statement: "handle_active_connection derives send_cancel via cancel.child_token() and hands it only to the spawned send task, while heartbeat_cancel and auth_timeout_cancel are cancel.clone() -- plain clones, not child tokens -- handed to the heartbeat and auth-timeout tasks respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:233"
      - "crates/buzz-relay/src/connection.rs:244"
      - "crates/buzz-relay/src/connection.rs:252"
  - statement: "state.rs's drain_all() (synchronous, the default when BUZZ_DRAIN_JITTER_MS is unset or zero) and drain_all_jittered() (delayed close spread across a configured jitter window) both call entry.cancel.cancel() on every registered connection as one step of queueing that connection's restart-close frame -- the same per-connection token this node documents is also the one process-wide graceful shutdown uses as one of several triggers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:418-431"
      - "crates/buzz-relay/src/state.rs:465"
  - statement: "buzz-dev-mcp's shell tool handler passes context.ct -- a CancellationToken field on rmcp::service::RequestContext<rmcp::service::RoleServer>, the rmcp MCP SDK's own per-request context type -- directly into shell::run, which accepts it as its own ct: CancellationToken parameter."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:44-50"
      - "crates/buzz-dev-mcp/src/shell.rs:130-134"
  - statement: "This node did not open rmcp's own source (not vendored in this repository's dependency cache at the checked revision) to confirm the precise client-side action that populates RequestContext.ct; the claim that it reflects an MCP notifications/cancelled message for that request is the well-known public contract of the Model Context Protocol's cancellation notification, not something this node verified by reading rmcp's implementation directly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml:26"
      - "Cargo.toml:132"
    confidence: 0.6
  - statement: "shell::run races ct.cancelled() against tokio::time::timeout(timeout_dur, child.wait()) in one biased tokio::select! -- whichever fires first is treated as the same kind of interruption: the cancellation branch kills the process group immediately (kill_group.kill_immediate()) and returns a 'cancelled' error, while the timeout branch kills it via a graceful-then-forced sequence (kill_group.kill_graceful()) and reports a timeout instead -- two different trigger origins (an external MCP cancellation vs. a self-imposed deadline) converging on structurally parallel, but not identical, cleanup paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:218-274"
  - statement: "Both branches of that select! call stdout_handle.abort() and stderr_handle.abort() on the two spawned reader tasks -- JoinHandle::abort(), not a CancellationToken -- and the timeout branch's own later join is itself bounded by a further tokio::time::timeout(Duration::from_secs(5), ...), calling .abort() again if that bound also expires."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:235-236"
      - "crates/buzz-dev-mcp/src/shell.rs:280-295"
  - statement: "docs.rs's reference documentation for tokio::task::JoinHandle::abort() states: 'Abort the task associated with the handle,' and that 'Awaiting a cancelled task might complete as usual if the task was already completed at the time it was cancelled, but most likely it will fail with a cancelled JoinError' -- the calling task does not need to check anything itself for abort() to take effect, unlike a CancellationToken, which only stops a task that itself awaits cancelled() or checks is_cancelled()."
    entry_class: FACT
    evidence:
      - "https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html"
  - statement: "HuddleOwnerEntry (the per-huddle-room owner lease) carries three separate CancellationToken fields -- lost ('cancelled by the renewer on fenced loss'), draining ('cancelled by drain so peers close with Goodbye(Draining) rather than the fenced-loss StaleGeneration path'), and cancel ('cancelled by release on room-empty ... and by drain after the drain signal') -- each documented in its own doc comment as answering a different question about why the room's owner lease is ending, rather than one token overloaded for all three."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/join.rs:588-605"
  - statement: "Issue #1116's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link the concept to related concepts/implementation/verification, and use examples only to clarify rather than to introduce a second canonical concept -- the concept.md template's Definition/Use cases/Relationships/Scope-and-omissions shape, not the flow.md Sequence/Diagram/Outcome shape sibling tasks #1118 and #1120 used for their own layers/lifecycle/*.md documents."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1116 definition of done"
  - statement: "node.schema.json's type enum includes layers as one of thirteen closed values, described only as 'the corpus surface this node documents,' with no further per-value elaboration in node.schema.json or schema/README.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "This node uses type: layers, mirroring the same independently-derived reasoning sibling layers/lifecycle/*.md tasks in this batch (#1118, #1120) each disclosed in their own body: parent Feature #611 organizes its whole task set under a layers/lifecycle/ directory taxonomy, a cross-cutting technical-behavior grouping distinct from the architecture/ subtree's C4 diagram family that flow.md's own worked skeleton defaults to (type: architecture). Per standards/taxonomy.md's Choosing a value step 2, layers is the enum member whose plain-English name most concretely names this node's primary subject. Read directly from the two sibling worktrees' own files for precedent (both unmerged, so cited as precedent read directly rather than as an authoritative merged source)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.7
  - statement: "architecture-containers-relay and architecture-containers-agent-runtime are both present as merged node ids on origin/launchpad at the time this node was authored, confirmed via git show origin/launchpad:launchpad/docs/corpus/architecture/containers/{relay,agent-runtime}.md, and architecture-containers-agent-runtime's own evidence ledger names buzz-dev-mcp as one of the three crates composing the agent runtime container -- making both valid relationships targets for this node's two worked examples (the relay's connection cancellation, and buzz-dev-mcp's shell-tool cancellation)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md:1-2"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:1-11"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-agent-runtime
---

# Cancellation

## A note on `type`

`node.schema.json`'s `type` enum lists thirteen closed values, and `layers` is one of
them, described only as naming "the corpus surface this node documents," with no
further elaboration distinguishing it from its neighbors. `launchpad/docs/corpus/
templates/flow.md`'s own worked skeleton defaults an instance of that template to
`type: architecture`, reasoning that a flow node is a fourth member of the C4 model's
diagram family. This node departs from that default and uses `type: layers` instead,
for the same reason sibling tasks in this batch (`#1118`, `#1120`) each independently
disclosed in their own bodies: this node's parent, Feature `#611`, organizes its entire
task set under a `layers/lifecycle/` directory taxonomy — a cross-cutting
technical-behavior grouping (lifecycle, concurrency, cancellation, background work,
resource cleanup, startup) distinct from the structural C4 architecture family the
`architecture/` subtree already houses. Neither sibling's branch is merged to
`origin/launchpad` at this node's checked revision, so their reasoning was read
directly from their own worktrees as precedent, not cited as an authoritative merged
source, and is restated here independently rather than copied. Per
`standards/taxonomy.md` step 5, `type` may be revised later without touching this
node's permanent `id`.

Unlike `#1118` and `#1120` — each narrating one ordered, real sequence
(`layers/lifecycle/graceful-shutdown.md`, `layers/lifecycle/startup.md`) and so built
against `templates/flow.md`'s Sequence/Diagram/Outcome shape — this node's subject is
a mechanism used identically across several unrelated contexts, not one sequence. Its
own issue (`#1116`)'s definition of done asks for a one-sentence definition,
boundaries/non-goals, links to related concepts, and examples used only to clarify —
`templates/concept.md`'s Definition/Use cases/Relationships/Scope-and-omissions shape,
which this node follows instead.

## Definition

**Cancellation** is the mechanism Buzz's own code uses to stop in-flight asynchronous
work before it would otherwise complete on its own — closing a WebSocket connection
mid-session, killing a shell command a caller no longer wants, or tearing down a
huddle-audio owner lease — rather than waiting for that work to finish or fail
naturally. Two distinct primitives implement it, and telling them apart matters more
than either one alone:

- **Cooperative cancellation**, via `tokio_util::sync::CancellationToken`: a shared
  signal a task must itself observe, typically by racing `token.cancelled()` against
  its own work inside a `tokio::select!`. A task that never checks the token is never
  stopped by it.
- **Preemptive cancellation**, via `tokio::task::JoinHandle::abort()`: the runtime
  stops the task on the caller's behalf, whether or not that task's own code checks
  anything. `docs.rs`'s reference documentation states plainly that awaiting an
  aborted task "most likely will fail with a cancelled `JoinError`" — the task does
  not get a vote.

Every cancellation site this node examined uses one or the other of exactly these two
primitives; no third cancellation mechanism was found in the code paths cited below.

## Visual aid

```mermaid
flowchart TB
    subgraph "Cooperative: CancellationToken"
        A["Owner creates token\n(CancellationToken::new())"] --> B["Cloned or child-tokened\ninto every task that must react"]
        B --> C["Each task: tokio::select! {\n  _ = token.cancelled() => stop\n  _ = its_own_work() => ...\n}"]
        D["Some trigger calls\ntoken.cancel()"] --> C
    end
    subgraph "Preemptive: JoinHandle::abort()"
        E["Caller holds the task's\nJoinHandle"] --> F["Caller calls handle.abort()"]
        F --> G["Runtime stops the task\n(no cooperation required)"]
    end
```

Both shapes appear together at one real call site (`crates/buzz-dev-mcp/src/shell.rs`,
see *Use cases*): a `CancellationToken` is raced against the command's own timeout,
and whichever fires first leads to `JoinHandle::abort()` calls on the two reader
tasks that were never going to check any token themselves.

## Use cases

**Per-WebSocket-connection cancellation (`crates/buzz-relay/src/connection.rs`).**
`ConnectionState` carries one `CancellationToken` (`cancel`), documented in its own
comment as the "Token used to signal graceful shutdown of this connection's tasks,"
created once per connection and cloned or child-tokened into every task the
connection spawns (`connection.rs:79-80,132`). Three genuinely different things
trigger it on the same field:

1. **Sustained backpressure.** `ConnectionState::send` cancels its own connection
   directly once a slow client's outbound buffer has stayed full for `grace_limit`
   consecutive sends, protecting server memory from an unbounded queue
   (`connection.rs:95-118`).
2. **A locally-owned deadline.** A dedicated auth-timeout task races
   `tokio::time::sleep(AUTH_TIMEOUT)` against `auth_timeout_cancel.cancelled()`; if the
   sleep wins and the connection is still unauthenticated (NIP-42), the task cancels
   itself (`connection.rs:251-272`).
3. **Orderly local exit.** Once `recv_loop` returns on its own (EOF, protocol error, or
   a client-initiated close), `handle_active_connection` explicitly calls
   `cancel.cancel()` before awaiting its sibling tasks' join handles — the reverse
   direction from the two triggers above: a task finishing normally proactively
   cancels the others, rather than one of them cancelling in reaction to a bad
   condition (`connection.rs:274-286`).

The same call site also demonstrates the token-hierarchy distinction: `send_cancel`
is a *child* token (`cancel.child_token()`, `connection.rs:233`), while
`heartbeat_cancel` and `auth_timeout_cancel` are plain *clones*
(`connection.rs:244,252`). Per `docs.rs`, cancelling a child does not cancel its
parent, while cancelling the parent still cancels every child — a one-way
propagation a plain clone does not have (a clone *is* the same token, so cancelling
it cancels every other clone too).

This same per-connection token is also what process-wide graceful shutdown uses as
one of its own triggers: `state.rs`'s `drain_all()` and `drain_all_jittered()` both
call `entry.cancel.cancel()` on every registered connection while queueing that
connection's restart-close frame (`state.rs:418-431,465`). This node documents the
token and its per-connection triggers; the shutdown sequence that also happens to
call it is `layers/lifecycle/graceful-shutdown.md`'s own subject (see *Scope and
omissions*), not re-narrated here.

**Per-MCP-request cancellation (`crates/buzz-dev-mcp/src/shell.rs`).** The `shell`
tool handler forwards `context.ct` — a `CancellationToken` field on
`rmcp::service::RequestContext<RoleServer>`, the `rmcp` MCP SDK's own per-request
context — into `shell::run` as its own `ct: CancellationToken` parameter
(`lib.rs:44-50`, `shell.rs:130-134`). `shell::run` races that token against the
command's own timeout in one `tokio::select!`:

```rust
tokio::select! {
    biased;
    _ = ct.cancelled() => { /* kill_group.kill_immediate(); reap; abort readers */ }
    r = tokio::time::timeout(timeout_dur, child.wait()) => { /* graceful kill on timeout */ }
}
```

(`shell.rs:218-274`, structure paraphrased for brevity — see the cited lines for the
exact code.) Both branches call `stdout_handle.abort()` and `stderr_handle.abort()`
on the two spawned reader tasks (`shell.rs:235-236,280-295`) — `JoinHandle::abort()`,
the preemptive primitive from the *Definition* section, used here because the reader
tasks themselves hold no `CancellationToken` and have no other way to be told to
stop reading from pipes that may still be open. This is the one call site this node
found where both primitives appear together, driven by two different trigger
origins (an external MCP cancellation vs. a self-imposed timeout) that converge on
structurally parallel, but not identical, cleanup.

**Per-huddle-owner-lease cancellation (`crates/buzz-relay/src/audio/join.rs`), cited
as a third, differently-shaped example rather than narrated in depth.**
`HuddleOwnerEntry` carries three separate tokens on one lease — `lost` ("cancelled by
the renewer on fenced loss"), `draining` ("cancelled by drain so peers close with
`Goodbye(Draining)`"), and `cancel` ("cancelled by release on room-empty ... and by
drain after the drain signal") — each answering a different question about *why* the
lease is ending, rather than one token overloaded for three meanings
(`join.rs:588-605`). This node cites the pattern (multiple independently-named
tokens on one unit of work) without narrating the room's full lifecycle, which risks
duplicating `#1119` (resource cleanup)'s subject; see *Scope and omissions*.

## Comparison

| | `CancellationToken` (cooperative) | `JoinHandle::abort()` (preemptive) |
|---|---|---|
| Who must act | The task itself, at an await point (`token.cancelled()` or `token.is_cancelled()`) | The runtime, on the caller's behalf — the task does nothing |
| A task that never checks it | Runs to completion, unaffected | Still stopped |
| Shareable across many tasks | Yes — clone or `child_token()` into as many tasks as needed | No — one `JoinHandle` per spawned task, one caller |
| Hierarchical | Yes — `child_token()` gives one-way parent-to-child propagation | No such concept |
| Seen in this node's examples | `connection.rs`'s per-connection token; `shell.rs`'s per-request token; `join.rs`'s per-lease tokens | `shell.rs`'s two reader tasks, which hold no token of their own |

Both primitives commonly appear side by side, as `shell.rs` shows: a
`CancellationToken` carries the *signal* that cancellation was requested, while
`abort()` is reached for when the thing that needs to stop (a task reading from a
pipe) was never given a token to check in the first place.

## Relationships

- `references`: `architecture-containers-relay` — the container `connection.rs` and
  `audio/join.rs`'s cancellation examples run inside.
- `references`: `architecture-containers-agent-runtime` — the container
  `buzz-dev-mcp` (the `shell.rs` example) is one of the three crates composing.

## Scope and omissions

**This node covers** `tokio_util::sync::CancellationToken` and
`tokio::task::JoinHandle::abort()` as Buzz's two task/request-cancellation
primitives, their cooperative-versus-preemptive distinction, the token-hierarchy
distinction between `.clone()` and `.child_token()`, and three worked examples of
where and why they are actually triggered in this codebase: per-connection
cancellation (backpressure, auth timeout, orderly exit), per-MCP-request
cancellation (an external client cancellation racing a self-imposed timeout), and
per-huddle-lease cancellation (multiple independently-named tokens on one unit of
work).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Process-wide graceful shutdown sequencing — even though `drain_all()`/`drain_all_jittered()` call the exact per-connection token this node documents | `#1118` (`layers/lifecycle/graceful-shutdown.md`) |
| Background-worker start/stop lifecycle in general | `#1115` (`layers/lifecycle/background-workers.md`) |
| General concurrency coordination — semaphores, locks, task pools, ordering between concurrent tasks that are not being cancelled | `#1117` (`layers/lifecycle/concurrency.md`) |
| Resource cleanup and Drop-based teardown, including `shell.rs`'s own `KillGroup` last-resort drop-guard | `#1119` (`layers/lifecycle/resource-cleanup.md`) |
| Process startup | `#1120` (`layers/lifecycle/startup.md`) |
| The full huddle-audio owner-lease lifecycle (acquire, renew, release, fenced hand-off) beyond the one cited token structure | Not yet a corpus node |
| `rmcp`'s own internal implementation of `RequestContext.ct` and exactly what client message populates it | Not established by this node (see the INFERENCE entry in the evidence ledger); not yet a corpus node either |

**Expected but not verified when this node was written:**

- **`rmcp`'s source was not opened.** This repository's local dependency cache did not
  contain a vendored copy at the checked revision, so the claim that `RequestContext.ct`
  reflects an MCP `notifications/cancelled` message rests on the Model Context
  Protocol's well-known public contract, not on code this node's author read directly —
  marked `INFERENCE` in the evidence ledger accordingly, not `FACT`.
- **Whether any other subsystem uses a third cancellation mechanism** (a custom
  `AtomicBool` flag checked manually, for instance, distinct from both primitives named
  here) **was not exhaustively searched for.** The three examples in *Use cases* were
  found via a targeted `grep` for `CancellationToken` across `crates/`; a channel-based
  or flag-based cancellation idiom elsewhere in the codebase would not have surfaced
  from that search.
- **Whether `HuddleOwnerRegistry`'s `is_draining()` `AtomicBool` (`join.rs:585,625-627`)
  is itself a fourth cancellation-adjacent primitive, or purely a read-only gate distinct
  from the three `CancellationToken`s on the same struct, was not resolved here** — it
  is named in the *Use cases* citation range but not analyzed on its own terms, since
  doing so risks the same resource-cleanup/lifecycle overlap named above.
