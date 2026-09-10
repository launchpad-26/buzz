---
id: verification-contracts-acp
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
  - statement: "buzz-acp's own Cargo.toml describes it as 'ACP harness that bridges Buzz events to AI agents,' building both a library (buzz_acp) and a binary (buzz-acp); acp.rs's own module doc-comment states the client manages communication with an AI agent subprocess over stdio using JSON-RPC 2.0, newline-delimited (NDJSON)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-acp/src/acp.rs:1-9"
  - statement: "AcpClient::read_until_response (the message loop send_request uses to await a plain request's reply) treats an incoming JSON-RPC message as the response to the outstanding request only when the message's id equals the expected id AND the message carries no method field; its own comment states a method field means the message is an agent-initiated request, not a response, even when the id happens to coincide."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1239-1244"
      - "crates/buzz-acp/src/acp.rs:1122"
  - statement: "AcpClient::read_until_response_with_idle_timeout (the message loop session_prompt_with_idle_timeout uses while a turn is in flight) independently re-implements the same guard: a message's id is only compared against expected_id for prompt-response purposes inside a block already gated on msg.get(\"method\").is_none(), so a message carrying a method field is never treated as the awaited response in this function either, and the same 'no method field' condition also gates matching a message to a pending steer request's id."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1571-1572"
      - "crates/buzz-acp/src/acp.rs:1677-1688"
  - statement: "The two functions above are separate code paths with no shared helper implementing the id/method discrimination: each defines its own match arm over msg.get(\"id\") and msg.get(\"method\"), so the guard is duplicated rather than centralized."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1239-1244"
      - "crates/buzz-acp/src/acp.rs:1571-1572"
  - statement: "acp.rs's own #[cfg(test)] mod tests carries agent_request_with_matching_id_not_consumed_as_response, a #[tokio::test] (not #[ignore]d) that spawns a bash script sending an agent-initiated request whose id equals the id read_until_response_with_idle_timeout is waiting on, followed by the real matching response, and asserts the call returns Ok with the real response's result rather than treating the agent-initiated request as the answer."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:3258-3283"
  - statement: "Running `cargo test -p buzz-acp --lib acp::tests::agent_request_with_matching_id_not_consumed_as_response -- --exact` at the recorded revision compiled the crate and reported `test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 829 filtered out`."
    entry_class: FACT
    evidence:
      - "cargo_test('-p buzz-acp --lib acp::tests::agent_request_with_matching_id_not_consumed_as_response -- --exact', at_commit='473205a7457b208455f188847bfb27b01aa83cac') -> test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 829 filtered out"
  - statement: "Every mention of buzz-acp across every GitHub Actions workflow in .github/workflows/ (ci.yml, release.yml, linux-canary.yml, macos-intel-canary.yml, signed-macos-canary.yml, windows-canary.yml, sprig.yml, sprig-image.yml) is a `cargo build`/`cargo build --release` invocation naming the -p buzz-acp package, or descriptive text about the sprig multicall binary; none invokes `cargo test` or `cargo nextest run` against the buzz-acp package."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:1095"
      - ".github/workflows/release.yml:94"
      - ".github/workflows/linux-canary.yml:189"
      - ".github/workflows/macos-intel-canary.yml:86"
      - ".github/workflows/signed-macos-canary.yml:118"
      - ".github/workflows/windows-canary.yml:144"
      - ".github/workflows/sprig.yml:4"
      - ".github/workflows/sprig-image.yml:112"
  - statement: "Justfile's test-unit recipe (the unit-test lane just ci and CI's own local-checks job run) enumerates cargo nextest run/cargo test invocations package-by-package (buzz-core, buzz-auth, buzz-voice, buzz-cli, buzz-db, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent, buzz-relay) and does not name buzz-acp anywhere in that list; three of its own inline comments state directly that 'nothing in CI runs `cargo test --workspace`' and that 'workspace membership alone buys clippy/check, not a single executed test.'"
    entry_class: FACT
    evidence:
      - "Justfile:316-386"
  - statement: "Justfile's `check` recipe (fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check, file-size-check) and the `ci` recipe that composes `check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test` together run static checks and the test-unit lane above; neither runs a workspace-wide `cargo test`, so buzz-acp's own #[cfg(test)] suite is not exercised by `just ci` either."
    entry_class: FACT
    evidence:
      - "Justfile:96"
      - "Justfile:305"
  - statement: "architecture-containers-agent-runtime, already merged on origin/launchpad, documents buzz-acp as one of the three crates composing the agent runtime container and cites CLAUDE.md's 'Agent surface' grouping and the sprig multicall binary; this node narrows into one wire-protocol obligation inside that same crate rather than restating its architecture-level description."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# ACP response/request discrimination — test contract

## Purpose and boundary

`buzz-acp` is the ACP (Agent Client Protocol) harness that bridges Buzz relay
events to an AI agent subprocess over stdio, using newline-delimited JSON-RPC
2.0 (NDJSON). This node documents **one** obligation of that wire protocol:
that the client's response-matching logic cannot be fooled by an
agent-initiated request whose `id` happens to collide with the `id` of a
request the client is currently waiting on. It covers that obligation only —
see *Scope and omissions* for the much larger surface of `buzz-acp` this node
does not address.

## Obligation

> A JSON-RPC message read from the ACP agent subprocess's stdout is consumed
> as the response to an outstanding request if and only if its `id` matches
> the expected id **and** the message carries no `method` field. A message
> whose `id` matches but which also carries a `method` field is dispatched as
> an agent-initiated request (or notification) instead, and the read loop
> keeps waiting for the real response.

This matters because JSON-RPC 2.0 gives requests and responses the same `id`
namespace: nothing in the wire format itself stops an agent (or a malicious
or buggy adapter) from emitting a request whose `id` happens to equal one the
client is already waiting on. Without the `method`-field guard, such a
message would be misread as the awaited response — silently completing a
`session/prompt` or `initialize` call with the wrong payload — while the
agent-initiated request itself would either hang unanswered (the agent
blocks waiting for a reply that never comes) or be dropped without the
`-32601` "method not found" reply `read_until_response`'s dispatch loop is
supposed to send it.

## Verifying test(s)

- `crates/buzz-acp/src/acp.rs` — `acp::tests::agent_request_with_matching_id_not_consumed_as_response`
  (line 3259) — spawns a fake agent (a bash script) that first emits
  `{"id":0,"method":"test/method","params":{}}` — an agent-initiated request
  whose `id` (`0`) is the same id the harness is waiting on — then, after
  the harness's `-32601` reply is read back by the script, emits the real
  response `{"id":0,"result":{"ok":true}}`. The test calls
  `read_until_response_with_idle_timeout` directly and asserts the call
  returns `Ok` carrying `{"ok": true}` — proving the id-colliding request was
  not mistaken for the response.

The obligation is guarded twice in the source (`read_until_response` at
`acp.rs:1239-1244`, used by `send_request`/`initialize`/`session/new`/
`authenticate`; `read_until_response_with_idle_timeout` at `acp.rs:1571-1688`,
used by prompt turns), but only the idle-timeout variant has a test naming
this exact scenario — see *Limits*.

## How to run it

```bash
cargo test -p buzz-acp --lib acp::tests::agent_request_with_matching_id_not_consumed_as_response -- --exact
```

No `#[ignore]` gate, no external infrastructure (Postgres/Redis/a live relay)
required — the "agent" is a bash script spawned as a real subprocess. This
command was run in this worktree at the recorded revision and returned
`test result: ok. 1 passed; 0 failed; 0 ignored`.

## Current enforcement status

**Gated — not by `#[ignore]`, but by omission from every CI lane.** The test
is not annotated `#[ignore]` and runs unconditionally under a plain
`cargo test -p buzz-acp` or `cargo test --workspace`. But no GitHub Actions
workflow in this repository invokes `cargo test` or `cargo nextest run`
against the `buzz-acp` package at any point — every workflow reference to
`buzz-acp` is a release/canary `cargo build` step producing the binary, never
a test run. `Justfile`'s `test-unit` recipe (the unit-test lane `just ci` and
the local-checks CI job run) enumerates ten other packages by name and
explicitly does not include `buzz-acp`; three of its own comments state that
nothing in CI runs `cargo test --workspace`, so workspace membership alone
does not cause this test — or any other test in `buzz-acp`'s 829-test
`#[cfg(test)]` suite — to execute anywhere in the pipeline. The test is real,
passes today, and would be caught by `cargo test --workspace` if anyone ran
it, but as of the recorded revision nothing in this repository's CI actually
does.

## Limits

- **Only one of the two guarded code paths is exercised.** The test drives
  `read_until_response_with_idle_timeout` (the prompt-turn loop). The
  sibling function `read_until_response` (used by `send_request`, and
  therefore by `initialize`, `session/new`, `authenticate`, and the
  request-shaped half of `session/cancel`) re-implements the identical
  `id`+`method` guard independently at `acp.rs:1239-1244`, but no test in
  this scenario's shape targets that function directly — a regression
  introduced only in `read_until_response` (for example, dropping its
  `msg.get("method").is_none()` check) would not be caught by this test.
- **Single collision, not concurrent or repeated collisions.** The script
  sends exactly one id-colliding agent-initiated request, then the real
  response. Multiple colliding requests in a row, or a colliding request
  arriving after the real response, are not exercised.
- **The `-32601` reply path is exercised only incidentally.** The test's
  fake agent reads the harness's error reply (`read -t 2 _reply`) to
  synchronize timing before sending the real response, but the test makes no
  assertion about the reply's shape or content — it is not itself a
  verifying test for `read_until_response`'s "unknown method gets a
  `-32601` error" behavior, only for the fact that the colliding message was
  not treated as the awaited response.
- **A fake agent, not a real ACP adapter.** The scenario is constructed by a
  bash script emitting hand-written JSON-RPC text; no test in this scenario
  runs against a real agent binary (e.g. `claude-agent-acp`, `goose`) that
  might emit a colliding `id` under real conditions (or never do so in
  practice).
- **Passing the test proves the guard's current behavior, not its
  necessity in production.** Nothing establishes from source alone how
  often — if ever — a real agent adapter emits an `id` that collides with an
  in-flight request; the obligation is defensive but its real-world trigger
  rate was not measured for this node.

## Scope and omissions

**This node covers** one wire-protocol obligation of `buzz-acp`'s JSON-RPC
message loop: that an id-colliding agent-initiated request is never
misread as the response to an outstanding request. It does not cover, and
each is a candidate for its own future test-contract node rather than being
folded in here:

- **The `MAX_LINE_SIZE` (10 MB) NDJSON line-length guard** (`acp.rs:23`,
  enforced via `LinesCodec::new_with_max_length`) — a real, load-bearing
  protocol limit with no test found under `acp::tests` naming it directly at
  the recorded revision.
- **Protocol version negotiation in `initialize`** (`acp.rs:611-620`) — the
  harness pins protocol version `2` unconditionally with a comment noting
  this is "an intentional temporary pin" ahead of an upstream ACP RFD; there
  is a unit test (`initialize_request_format`) asserting the request shape,
  but no test asserts behavior if an agent responds with a different
  negotiated version.
- **Idle/hard-timeout enforcement** (`AcpError::IdleTimeout`,
  `AcpError::HardTimeout`) — has its own, separate family of tests
  (`idle_timeout_fires_on_silent_process`, `hard_timeout_fires_when_deadline_is_immediate`,
  and others) that would be the right basis for a dedicated node.
- **`StopReason::from_str`'s case-insensitive parsing of the five known
  `stopReason` values**, and its `None` fallback for anything else
  (`acp.rs:57-70`, tested by `stop_reason_parses_all_known_values`,
  `stop_reason_returns_none_for_unknown`, `stop_reason_is_case_insensitive`)
  — a clean, already-tested, already-passing candidate obligation that this
  node deliberately leaves for its own node rather than combining two
  obligations into one.
- **Steering (`session/steer`) ack semantics** and **usage tracking**
  (`usage.rs`) — large, separately-tested subsystems within the same crate,
  each with their own obligation(s) to state precisely rather than
  summarized here.
- **`buzz-agent`'s side of the same ACP handshake** — this node documents
  only the `buzz-acp` harness's client-side behavior; the minimal
  ACP-compliant agent in `crates/buzz-agent` is a distinct crate with its own
  obligations.

**Relationships.** `architecture-containers-agent-runtime` is loadable from
`origin/launchpad`'s corpus tree at the recorded revision and describes
`buzz-acp` at the container/architecture level; this node adds a
`references` edge to it rather than restating that description. No other
node in `origin/launchpad`'s corpus tree at the recorded revision is specific
to `buzz-acp`'s wire protocol, so no further relationships are declared.

**Expected but not verified when this node was written:**

- **Whether any other test elsewhere in the workspace (outside
  `crates/buzz-acp`) exercises this same discrimination behavior
  indirectly** — for example through `buzz-test-client`'s e2e suites driving
  a real agent turn — was not established; the `grep` performed for this
  node found no reference to `buzz-acp`/`buzz_acp` inside
  `crates/buzz-test-client/tests/`, but an indirect exercise through a
  shared harness process was not ruled out by that search alone.
- **Whether the omission of `buzz-acp` from `test-unit` was a deliberate
  choice or an oversight** — no issue, PR, or commit message explaining the
  omission was found or cited here; this node states the observed fact
  (the package is absent from every CI test invocation) without asserting a
  reason for it.
- **Historical CI configuration** — this node reflects the workflows and
  `Justfile` as they exist at the recorded revision only; it makes no claim
  about whether `buzz-acp` was ever included in a test lane in the past or
  is planned to be added in the future.
