---
id: verification-e2e-agent
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "TESTING.md's 'ACP Harness (optional, end-to-end with a real agent)' section is this repository's own procedure for exercising an ACP-speaking agent connected to a live relay through buzz-acp end to end: build buzz-acp, start a real relay, mint an agent identity, add it as a member of a channel, launch buzz-acp against a real ACP agent (goose, codex, claude code, or buzz-agent), then, from a separate sender identity, @mention the agent and confirm its reply by manually running `buzz messages get`."
    entry_class: FACT
    evidence:
      - "TESTING.md:223-305"
  - statement: "TESTING.md names no automated CI job or single test command that runs the ACP-harness sequence; every step -- building the release binaries, starting the relay, minting keys, adding channel membership, launching buzz-acp, sending the mention, and reading the reply back -- is a manual shell command the operator runs and checks themselves."
    entry_class: FACT
    evidence:
      - "TESTING.md:223-305"
  - statement: "TESTING.md states explicitly that the automated `pool_lifecycle_state` coverage 'pins single-wake, retry/backoff, and stale-result behavior' but 'does not replace this real relay/process smoke test.'"
    entry_class: FACT
    evidence:
      - "TESTING.md:281-287"
  - statement: "crates/buzz-acp/src/pool_lifecycle.rs's own module doc-comment states that relay connection, subscription, and event buffering live outside that module, and that the state machine it defines owns only whether a deferred agent pool has not started, is waking, is ready, or is waiting to retry after a failed wake; crates/buzz-acp/tests/pool_lifecycle_state.rs compiles that module as an integration-test target with no relay connection or agent subprocess involved anywhere in it."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool_lifecycle.rs:1-5"
      - "crates/buzz-acp/tests/pool_lifecycle_state.rs"
  - statement: "crates/buzz-agent/tests/golden_transcripts.rs spawns the real buzz-agent binary as a subprocess and drives it over stdio through the ACP JSON-RPC protocol against a fake, locally-hosted OpenAI-compatible LLM server, exercising tool-call transcripts, permission prompts, protocol conformance and several edge cases (oversized lines, concurrent prompts, cancellation); it opens no relay connection and does not exercise buzz-acp's event-routing harness at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/tests/golden_transcripts.rs:1-42"
      - "crates/buzz-agent/tests/golden_transcripts.rs:205-233"
  - statement: "crates/buzz-test-client/tests/ contains one test file with 'agent' in its name that touches the relay, e2e_managed_agent.rs; its own module doc-comment states it verifies that the relay accepts and addresses kind:30177 managed-agent metadata events the same way it does personas, and that published content round-trips unchanged -- a NIP-33 event-storage contract, not a live agent process receiving an event and acting on it."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_managed_agent.rs:1-22"
  - statement: "buzz-acp's own README points readers to the root TESTING.md for 'the full integration testing guide -- automated test suites, multi-agent E2E testing via the ACP harness, and troubleshooting,' and names no test suite of its own beyond that pointer."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:334-336"
  - statement: "crates/sprig -- the all-in-one binary bundling buzz-acp, buzz-agent and buzz-dev-mcp -- contains exactly one Rust source file, crates/sprig/src/main.rs, and no test file at all; the three GitHub Actions workflows that mention buzz-acp (ci.yml, sprig.yml, sprig-image.yml) only cross-compile, bundle or publish the binary, and run no test against it."
    entry_class: FACT
    evidence:
      - "crates/sprig/src/main.rs"
      - ".github/workflows/ci.yml:1093-1097"
      - ".github/workflows/sprig.yml:3-6"
  - statement: "No automated test anywhere in this repository spawns a real ACP agent process, connects it via buzz-acp to a live relay over WebSocket, delivers it a channel event, and asserts on the agent's resulting action; the closest automated coverage (pool_lifecycle_state.rs and golden_transcripts.rs) each exercise one narrower piece of that path in isolation, and the only place the full path is exercised together is the manual procedure in TESTING.md. None of the seven files in crates/buzz-agent/tests/ mentions 'relay', 'buzz-acp' or a WebSocket anywhere in its source, which is the specific check that closes the gap between 'no dedicated agent-e2e test was found' and 'the crate's own tests do not even incidentally connect an agent process to a relay.'"
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/tests/pool_lifecycle_state.rs"
      - "crates/buzz-agent/tests/golden_transcripts.rs"
      - "crates/buzz-test-client/tests/e2e_managed_agent.rs"
      - "TESTING.md:223-305"
      - "crates/sprig/src/main.rs"
      - "grep('relay|buzz-acp|WebSocket|websocket', 'crates/buzz-agent/tests/*.rs') -> no matches"
    confidence: 0.8
  - statement: "Issue #1362's definition of done requires this node to name the verifying test(s) exactly, state how to run them including any gating, and state enforcement status honestly as verified, gated or pending -- and requires that if no dedicated agent e2e test exists yet, this node say so as 'pending' rather than inventing one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1362 definition of done"
relationships:
  - type: references
    target: architecture-flows-agent-turn
---

# Agent harness end-to-end — test contract

## Purpose and boundary

This node documents one obligation: that an AI agent process, running as an
ACP-speaking subprocess under the `buzz-acp` harness, can connect to a live
Buzz relay, receive a channel event that mentions it, and act on that event
end to end. It covers that obligation only.

It does not cover the ACP protocol conformance of the `buzz-agent` binary in
isolation, the `buzz-acp` agent-pool lifecycle state machine in isolation, or
the relay's acceptance and storage of managed-agent metadata events. Those
are real, narrower, already-automated pieces of the surrounding system, named
below as adjacent coverage rather than folded into this obligation.

## Obligation

> An ACP-speaking agent process, connected to a live Buzz relay through the
> `buzz-acp` harness and added as a member of a channel, receives a channel
> event that `@mentions` its pubkey and produces an observable reply (a
> `kind:9` event published from the agent's own pubkey) in that channel.

## Verifying test(s)

**No automated test currently verifies this obligation end to end.** The
only procedure that exercises the full path — a real relay, a real
`buzz-acp` process, and a real ACP agent subprocess, driven by a live event
and checked by reading the relay back — is the manual runbook in
`TESTING.md`, section "ACP Harness (optional, end-to-end with a real agent)"
(`TESTING.md:223-305`). It is not a test file and has no single invocation;
it is a sequence of shell steps a person runs, ending in a person reading a
CLI response.

Automated coverage exists for three narrower, adjacent pieces of the same
system, none of which alone or together constitutes this obligation:

- `crates/buzz-acp/tests/pool_lifecycle_state.rs` (compiling
  `crates/buzz-acp/src/pool_lifecycle.rs`'s `#[cfg(test)] mod tests`) — the
  agent-pool wake/retry/backoff/stale-result state machine, in isolation
  from any relay connection or agent subprocess. The module's own
  doc-comment states that relay connection, subscription and event
  buffering live outside it.
- `crates/buzz-agent/tests/golden_transcripts.rs` — spawns the real
  `buzz-agent` binary and drives it over stdio through the ACP protocol
  against a fake, locally-hosted LLM server, checking tool-call transcripts,
  permission handling, and protocol conformance. No relay is involved
  anywhere in this file or its six sibling files in the same directory.
- `crates/buzz-test-client/tests/e2e_managed_agent.rs` — exercises the
  relay's acceptance, storage, and NIP-33 replacement semantics of
  `kind:30177` managed-agent metadata events. This is a claim about event
  storage, not about a running agent process receiving and acting on an
  event.

## How to run it

There is no single command for the obligation itself. To run the manual
procedure (condensed from `TESTING.md:223-305`; see that section for the
full sequence including key-minting and env-var details):

```bash
# Terminal 1 — build and start a real relay
. ./bin/activate-hermit
just bootstrap && just setup
cargo build --release -p buzz-relay -p buzz-cli -p buzz-admin
export PATH="$PWD/target/release:$PATH"
set -o allexport; source .env; set +o allexport
buzz-relay

# Terminal 2 — mint an agent identity, add it to a channel, launch buzz-acp
cargo build --release -p buzz-acp
export PATH="$PWD/target/release:$PATH"
# ... mint AGENT_SK/AGENT_PUBKEY, `buzz channels add-member`, set
#     BUZZ_PRIVATE_KEY/BUZZ_RELAY_URL/BUZZ_ACP_RESPOND_TO — TESTING.md:238-264
buzz-acp

# Terminal 3 (a different, sender identity) — trigger a turn and read the reply
buzz messages send --channel "$CHANNEL" --content "Hey agent, reply PONG only."
buzz messages get --channel "$CHANNEL" --limit 5 | jq '.[] | {pubkey, content}'
```

The adjacent automated pieces run unconditionally, with no live-relay gate,
under the ordinary unit-test command:

```bash
just test-unit
# or narrower:
cargo test -p buzz-acp --test pool_lifecycle_state
cargo test -p buzz-agent --test golden_transcripts
```

`e2e_managed_agent.rs` is gated behind a live relay and `--ignored`, exactly
as `TESTING.md`'s automated-E2E section documents for the whole
`buzz-test-client` suite:

```bash
RELAY_URL=ws://localhost:3000 cargo test --test e2e_managed_agent -- --ignored
```

## Current enforcement status

**Pending.** No automated test connects a real ACP agent through `buzz-acp`
to a real relay, delivers it a channel event, and asserts on the agent's
resulting action. The obligation is currently verified only by a human
following the manual runbook in `TESTING.md`, which the document itself
labels optional and which produces no CI signal. `buzz-acp`'s own README
defers entirely to that same manual guide and names no automated coverage of
its own beyond the pool-lifecycle state machine. The three GitHub Actions
workflows that mention `buzz-acp` (`ci.yml`, `sprig.yml`, `sprig-image.yml`)
only cross-compile, bundle or publish the binary — none of them runs a test
against it.

## Limits

What the existing automated tests establish, and no more:

- `pool_lifecycle_state.rs` establishes only that the pool wake/retry state
  machine transitions correctly in isolation. It proves nothing about
  whether a real relay connection, a real subprocess, or a real event ever
  reaches that state machine in production.
- `golden_transcripts.rs` establishes that the `buzz-agent` binary
  implements the ACP protocol correctly against a fake LLM, including tool
  calls, permission prompts, and several edge cases. It proves nothing about
  `buzz-acp`'s event routing, relay connectivity, channel-membership
  gating, or the Inbound Author Gate — none of that is in its process tree.
- `e2e_managed_agent.rs` establishes that the relay stores and returns
  `kind:30177` metadata events correctly. It proves nothing about an agent
  process actually running, receiving a mention, or replying.
- The manual `TESTING.md` runbook, when someone runs it, demonstrates the
  real path once, on one machine, for whichever ACP agent (`goose`,
  `codex`, `claude code`, or `buzz-agent`) happened to be configured that
  session. It leaves no artifact, is not re-run automatically on every
  change, and a regression introduced between one person's manual run and
  the next is invisible to CI.

## Scope and omissions

**This node covers** the end-to-end obligation of an agent connecting to a
live relay via `buzz-acp`, receiving a mention, and acting on it — and
states honestly that no automated test currently verifies it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ACP protocol conformance of the `buzz-agent` binary against a fake LLM | `crates/buzz-agent/tests/golden_transcripts.rs` |
| The agent-pool wake/retry/backoff state machine | `crates/buzz-acp/src/pool_lifecycle.rs`, tested by `crates/buzz-acp/tests/pool_lifecycle_state.rs` |
| The relay's storage/replacement semantics for managed-agent metadata events (`kind:30177`) | `crates/buzz-test-client/tests/e2e_managed_agent.rs` |
| The `agent-turn` flow's own architecture — discovery, the Inbound Author Gate, dedup/batching | `architecture-flows-agent-turn` |
| Whether any one of the adjacent pieces above should itself become a live-relay automated e2e assertion | left as a future task; not filed here, per this node's own one-obligation scope |

**Expected but not verified when this node was written:**

- Whether `crates/sprig`, the bundled all-in-one harness, is exercised by any
  test outside this repository (for example in a downstream deployment
  pipeline) was not checked; only this repository's own tree and workflow
  files were searched.
- Whether the manual `TESTING.md` procedure has actually been run recently
  against current `HEAD` was not established here — this node only confirms
  the procedure exists and is described as manual, not that it currently
  succeeds.
