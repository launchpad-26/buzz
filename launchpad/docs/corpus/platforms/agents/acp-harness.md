---
id: platforms-agents-acp-harness
type: implementation
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "buzz-acp is a standalone binary crate whose Cargo.toml describes it as an 'ACP harness that bridges Buzz events to AI agents,' and CLAUDE.md's repo structure map groups it under the 'Agent surface' heading with the same one-line description, 'ACP harness bridging Buzz events to AI agents.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "CLAUDE.md:70"
  - statement: "crates/buzz-acp/src/lib.rs carries no crate-level (//!) doc comment; the file opens directly with #![deny(unsafe_code)] followed by its module declarations, so the crate's own source names no single authored responsibility statement at the crate-doc level."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:1-16"
  - statement: "crates/buzz-acp/README.md states the harness listens for @mentions on the relay, prompts the agent, and the agent replies using the Buzz CLI, diagrammed as 'Buzz Relay --WS--> buzz-acp --stdio--> Your Agent -> Buzz CLI (send_message, etc.)', and names three supported agents that speak ACP over stdio: goose, codex (via codex-acp), and claude code (via claude-agent-acp)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:1-12"
  - statement: "lib.rs exposes exactly two items outside the crate — pub fn run() (the function main.rs's sole line calls as buzz_acp::run()) and pub use usage::TurnUsage — while every other module (acp, config, engram_fetch, filter, observer, pool, pool_lifecycle, prompt_framing, prompt_project, queue, relay, setup_mode, usage) is declared as a private `mod`, so any `pub` item inside them is visible within the buzz_acp crate but is not part of its external API."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3-17"
      - "crates/buzz-acp/src/lib.rs:1897"
      - "crates/buzz-acp/src/main.rs"
  - statement: "crates/sprig/Cargo.toml declares buzz-acp as a path dependency, and crates/sprig/src/main.rs dispatches to it by calling buzz_acp::run() when the multicall binary is invoked as 'buzz-acp' — the one real inbound dependency on this crate found in the workspace."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "crates/sprig/src/main.rs:17"
  - statement: "crates/buzz-acp/Cargo.toml declares three internal workspace dependencies — buzz-core, buzz-sdk, and buzz-persona (a path dependency) — alongside external crates for the Nostr protocol (nostr), the async runtime (tokio), WebSocket transport (tokio-tungstenite, rustls), HTTP (reqwest), and CLI parsing (clap)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
  - statement: "No `buzz_persona::` reference exists anywhere under crates/buzz-acp/, despite the Cargo.toml dependency on buzz-persona; the persona-related behavior actually present in the source (acp.rs's CODEX_CONFIG merge logic, which layers a 'persona base' object from an environment variable under Buzz-generated keys) is driven entirely by environment variables passed into the process, not by calling the buzz_persona crate's own API."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-acp/src/acp.rs:251-263"
      - "grep_repo(pattern='buzz_persona', scope='crates/buzz-acp/**') -> no matches, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "AcpClient (declared `pub struct AcpClient` in acp.rs) and the CLI/config types (`pub struct CliArgs`, `pub struct Config`, `pub enum RespondTo`, `pub enum SubscribeMode`, etc. in config.rs) are declared `pub` but are never re-exported from lib.rs, because `mod acp` and `mod config` are private module declarations — making them visible only within the buzz_acp crate, not part of its external API."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:3-4"
      - "crates/buzz-acp/src/acp.rs:141"
      - "crates/buzz-acp/src/config.rs:95"
      - "crates/buzz-acp/src/config.rs:245"
  - statement: "README.md's Core configuration table documents the harness's environment-variable/CLI-flag surface: BUZZ_PRIVATE_KEY (required, no default), BUZZ_RELAY_URL (default ws://localhost:3000), BUZZ_ACP_AGENT_COMMAND (default goose), BUZZ_ACP_AGENT_ARGS (default acp), BUZZ_ACP_MCP_COMMAND, BUZZ_ACP_IDLE_TIMEOUT (default 620 seconds), BUZZ_ACP_MAX_TURN_DURATION (default 7200 seconds), and BUZZ_API_TOKEN — every variable additionally exposed as a matching CLI flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:105-120"
  - statement: "config.rs declares `pub enum RespondTo`, and README.md documents the inbound author gate it drives as four modes — owner-only (default), allowlist, anyone, nobody — controlling which authors' events the harness forwards to the agent, with owner control commands !shutdown, !cancel, and !rotate checked before the gate applies."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:95"
      - "crates/buzz-acp/README.md:132-160"
  - statement: "README.md documents that the harness can run N parallel agent subprocesses (1-32, default 1) via --agents/BUZZ_ACP_AGENTS, that all N agents authenticate as the same Nostr bot identity, and that the event queue guarantees a given channel is never processed by two agents simultaneously (cross-channel ordering is not guaranteed when N>1)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:122-127"
      - "crates/buzz-acp/README.md:204-206"
  - statement: "queue.rs's module doc describes an event-queue state machine that tracks per-channel in-flight state and, when the harness is ready to prompt the agent, drains ALL pending events for a channel into a single batched prompt; it also documents a configurable dedup mode, default Drop, under which new events for a channel already in flight are silently dropped."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/queue.rs:1-13"
  - statement: "relay.rs's module doc describes HarnessRelay as connecting to the Buzz relay over NIP-01 WebSocket, authenticating via NIP-42, discovering channels through the relay's REST API, and reconnecting with a `since` filter on disconnect specifically to avoid missing events."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs:1-21"
  - statement: "acp.rs's module doc describes AcpClient's lifecycle in five steps: spawn (launch the agent subprocess), initialize (ACP protocol version negotiation), session_new (create a session with MCP server configuration), session_prompt_with_idle_timeout (send a prompt with idle and hard-deadline timeouts), and session_cancel / cancel_with_cleanup (cancel an in-flight turn)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:1-9"
  - statement: "crates/buzz-acp/src/lib.rs declares `#![deny(unsafe_code)]` as the crate's first line."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:1"
  - statement: "The crate carries a dedicated integration test, tests/pool_lifecycle_state.rs, which compiles src/pool_lifecycle.rs directly via a #[path] attribute to exercise the lazy agent-pool lifecycle state machine as a standalone contract, separate from the numerous #[cfg(test)]-gated unit test modules embedded across the crate's own source files (13 of buzz-acp's 15 source files carry inline tests)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/tests/pool_lifecycle_state.rs:1-4"
  - statement: "README.md's Bring Your Own Harness (BYOH) section documents a three-tier system letting Buzz Desktop register any ACP-speaking agent tool without a PR: tier-1 compiled-in runtimes (goose, claude, codex, buzz-agent) with reserved ids; tier-2 a static preset catalog defined as `HarnessDefinition` entries in desktop/src-tauri/src/managed_agents/discovery.rs; and tier-3 user-authored custom-harness JSON files validated against the id set in desktop/src-tauri/src/managed_agents/custom_harnesses.rs. Both cited source files exist in the repository."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:264-321"
      - "desktop/src-tauri/src/managed_agents/discovery.rs"
      - "desktop/src-tauri/src/managed_agents/custom_harnesses.rs"
  - statement: "The existing corpus node architecture-containers-agent-runtime documents buzz-acp as one of three crates (with buzz-agent and buzz-dev-mcp) composing the agent-runtime container, citing the same CLAUDE.md 'Agent surface' grouping used above."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Root TESTING.md is the harness's own pointer for integration and multi-agent E2E testing guidance; README.md's Testing section names it directly rather than duplicating its content."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:334-336"
      - "TESTING.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/component.md, which was already merged on origin/launchpad at the recorded revision and directs a node built from it to carry type: implementation, a Responsibility/Public interface/Dependencies/Boundary/Relationships/Scope-and-omissions body shape, and a rustdoc-grounded evidence standard."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "Issue #1229's Definition of Done tail ('states responsibility and well-defined interface/boundary,' 'names dependencies and collaborators,' 'links source implementation and tests,' 'explains only component-level behavior') matches the component template's Required Sections verbatim, and the identical tail appears on sibling issues #1230 and #1231 for the same platforms/agents/ batch — the basis for choosing that template over inventing a structure."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1229, #1230, #1231 definitions of done"
relationships:
  - type: references
    target: architecture-containers-agent-runtime
---

# buzz-acp — the ACP harness

`buzz-acp` is the standalone Rust binary crate that bridges Buzz relay events
to AI agent subprocesses over the [Agent Client Protocol](https://agentclientprotocol.com/)
(ACP). It is the "platform" surface an operator stands up to make an AI agent
a first-class Buzz participant: it owns relay connectivity, agent process
lifecycle, event queuing/batching, and the inbound-author gate, while the
actual reasoning and tool use happen in the agent subprocess it spawns. This
node answers: what does this one component do, what does it expose, and what
does it depend on — not how the containing agent-runtime platform as a whole
is composed (see *Boundary*).

## Responsibility

`crates/buzz-acp/src/lib.rs` carries no crate-level (`//!`) doc comment — the
file opens directly with `#![deny(unsafe_code)]` and its module list. The
crate's authored responsibility statement instead lives in two other places
that agree with each other: `Cargo.toml`'s `description` field, "ACP harness
that bridges Buzz events to AI agents," and `README.md`'s opening line and
diagram, which describe the harness listening for @mentions on the relay,
prompting the agent, and the agent replying through the Buzz CLI. `CLAUDE.md`'s
repository structure map independently corroborates the same one-line
description under its "Agent surface" heading.

Concretely, per the module-level doc comments actually present in the source:

- **Relay connectivity** (`relay.rs`) — `HarnessRelay` connects over NIP-01
  WebSocket, authenticates via NIP-42, discovers channels through the relay's
  REST API, and reconnects with a `since` filter on disconnect to avoid
  missing events.
- **Agent process lifecycle** (`acp.rs`) — `AcpClient` spawns the agent
  subprocess, negotiates the ACP protocol version, creates a session with MCP
  server configuration, sends prompts with idle/hard-deadline timeouts, and
  cancels in-flight turns.
- **Event queuing** (`queue.rs`) — a per-channel event queue that batches all
  pending events for a channel into one prompt when the harness is ready,
  with a configurable dedup mode (default `Drop`: new events for an
  already-in-flight channel are silently dropped).
- **Inbound author gate** (`config.rs`'s `RespondTo` enum, documented in
  `README.md`) — four modes (`owner-only` default, `allowlist`, `anyone`,
  `nobody`) deciding which authors' events reach the agent, with owner
  control commands (`!shutdown`, `!cancel`, `!rotate`) checked ahead of the
  gate.
- **Parallel agents** — up to 32 agent subprocesses share one Nostr identity;
  the queue guarantees a channel is never processed by two agents at once.

## Public interface

The crate's *Rust*-level public interface is deliberately thin, because
`buzz-acp` is consumed as a binary, not as a library dependency graph:

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `pub fn run()` | fn (lib.rs) | The crate's sole external entry point; `main.rs`'s one line calls `buzz_acp::run()`. Propagates legacy env vars, then drives the async `tokio_main()`. | `crates/buzz-acp/src/lib.rs:1897`, `crates/buzz-acp/src/main.rs` |
| `pub use usage::TurnUsage` | re-export | The only other item visible outside the crate; carries per-turn token-usage figures derived from NIP-AM agent turn metrics. | `crates/buzz-acp/src/lib.rs:17` |

Every other `mod` declaration in `lib.rs` (`acp`, `config`, `engram_fetch`,
`filter`, `observer`, `pool`, `pool_lifecycle`, `prompt_framing`,
`prompt_project`, `queue`, `relay`, `setup_mode`, `usage`) is private, so
`pub` items inside them — `AcpClient` (`acp.rs`), `CliArgs`/`Config`/
`RespondTo`/`SubscribeMode` (`config.rs`), and others — are visible within
the crate but are not part of its compiled public API.

The interface an **operator** actually programs against is the CLI/
environment-variable surface `README.md` documents in full: required
`BUZZ_PRIVATE_KEY`; `BUZZ_RELAY_URL` (default `ws://localhost:3000`);
`BUZZ_ACP_AGENT_COMMAND`/`BUZZ_ACP_AGENT_ARGS` (default `goose`/`acp`);
`BUZZ_ACP_MCP_COMMAND`; `BUZZ_ACP_IDLE_TIMEOUT` (default 620s);
`BUZZ_ACP_MAX_TURN_DURATION` (default 7200s); `BUZZ_API_TOKEN`; the
`--agents`/`--respond-to`/`--heartbeat-*` family; and the Bring Your Own
Harness (BYOH) tier-2/tier-3 registration surfaces
(`desktop/src-tauri/src/managed_agents/discovery.rs`'s `PRESET_HARNESSES`,
and user-authored custom-harness JSON files). This document does not restate
every flag's full table — `README.md` is the canonical, actively-maintained
source for that and this node cites it rather than duplicating it.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-core` | Nostr event kinds (`KIND_STREAM_MESSAGE`, etc.) and the observer payload encrypt/decrypt helpers used for owner-scoped telemetry frames. | `crates/buzz-acp/Cargo.toml`, `crates/buzz-acp/src/lib.rs:25-32` |
| `buzz-sdk` | Typed Nostr event builders. | `crates/buzz-acp/Cargo.toml` |
| `buzz-persona` | Declared as a path dependency, but no `buzz_persona::` reference exists anywhere in the crate's source — see *Scope and omissions* for why this is flagged as a gap rather than described further. | `crates/buzz-acp/Cargo.toml` |

Plus external crates for the Nostr protocol (`nostr`), the async runtime
(`tokio`), WebSocket transport (`tokio-tungstenite`, `rustls`), HTTP
(`reqwest`, for channel discovery), CLI parsing (`clap`), and filter
expressions (`evalexpr`) — enumerated in full in `Cargo.toml`, not restated
here.

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `sprig` | The all-in-one multicall binary depends on `buzz-acp` as a path dependency and calls `buzz_acp::run()` directly when invoked as `buzz-acp`, packaging the harness as part of one deploy-anywhere artifact alongside `buzz-agent` and `buzz-dev-mcp`. | `crates/sprig/Cargo.toml`, `crates/sprig/src/main.rs:17` |

No other crate in the workspace declares `buzz-acp` as a dependency; the
other matches for the string "buzz-acp" in sibling `Cargo.toml` files
(`buzz-relay`, `buzz-cli`, the root manifest) are code comments describing
shared rustls-provider setup or release-build packaging, not `[dependencies]`
entries.

## Boundary

This node does not describe:

- **The agent-runtime container's full composition.** `buzz-acp` is one of
  three crates (with `buzz-agent` and `buzz-dev-mcp`) making up the
  agent-runtime container documented by
  `launchpad/docs/corpus/architecture/containers/agent-runtime.md` — see
  *Relationships* below. This node covers `buzz-acp` alone.
- **How individual ACP-speaking agents (goose, codex, claude code) implement
  their own side of the protocol.** Those are external projects; this node
  describes only what `buzz-acp` requires of them and how it drives them.
- **The Buzz CLI's own command surface** (`buzz-cli`), which the spawned
  agent uses to act on Buzz. That crate has its own corpus surface.
- **Class/function-level design detail** beyond the module boundaries and
  the two crate-external public items named above. `buzz-acp`'s modules
  (`acp.rs`, `pool.rs`, `queue.rs`, etc.) are large (the crate totals
  ~46,000 lines); this node names what each module is responsible for, not
  every internal type or function.
- **Install/usage walkthroughs for a human running the harness.** `README.md`
  already carries a complete quick-start, configuration reference, and
  troubleshooting guide; this node cites it rather than reproducing it.

## Relationships

- `references`: `architecture-containers-agent-runtime` — the container node
  that documents `buzz-acp` as one of three crates composing the
  agent-runtime container. `part-of` was considered instead, but that
  relationship type is reserved (per the `component` template this node was
  built from) for the edge from a component to an *architecture-component*
  node whose building-block table names it, and no such node exists in the
  corpus yet for the agent-runtime container. `references` is used here for
  supporting context without asserting that undeclared edge.
- No `depends-on`/`implements`/`supersedes`/`part-of` edges are declared: no
  other corpus node currently exists for `buzz-core`, `buzz-sdk`,
  `buzz-persona`, or `sprig` (the real code-level dependencies named above)
  to target, and this task's own scope does not extend to authoring those.

## Scope and omissions

**This node covers** `buzz-acp`'s responsibility, its thin Rust-level public
interface versus its much larger operator-facing CLI/env-var surface, its
real dependency edges in both directions (cited to `Cargo.toml`, not to
deployment topology), and an explicit boundary against the agent-runtime
container, the agents it spawns, the Buzz CLI, and its own class/function
internals.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent-runtime container's full three-crate composition and diagram | `launchpad/docs/corpus/architecture/containers/agent-runtime.md` |
| A C4-style component decomposition of the agent-runtime container's internals, with a required diagram | Not yet authored — no `architecture-component` node exists in the corpus at the recorded revision |
| The Buzz CLI's own public command surface | `buzz-cli`'s own corpus node, not yet authored at the recorded revision |
| How `buzz-acp` satisfies any specific spec, decision, or contract (an `implements`-relationship traceability artifact) | Not yet authored — the `implementation-reference` template track (issue `#1341`, per `component.md`'s own citation) had not landed a worked example at the recorded revision |
| Full CLI flag/env-var reference | `crates/buzz-acp/README.md`, actively maintained and cited above rather than duplicated |

**Expected but not verified when this node was written:**

- **Why `buzz-persona` is declared as a Cargo dependency with no
  corresponding source reference was not established.** It may be an
  aspirational dependency for planned integration, dead weight from a
  refactor, or used only via a mechanism this grep-based check could not
  detect (e.g. a re-export chain through another crate). This node states
  the observed fact (dependency declared, no `buzz_persona::` usage found)
  without speculating further.
- **Whether every one of buzz-acp's 15 source files' inline `#[cfg(test)]`
  modules were individually read was not attempted** — this node's claims
  about module responsibilities are grounded in each file's authored
  module-level (`//!`) doc comment, not in a full read of every test.
- **The full BYOH custom-harness JSON schema and security guarantees**
  (documented in `README.md`'s BYOH section) were read from `README.md`
  itself, not independently re-verified against
  `desktop/src-tauri/src/managed_agents/custom_harnesses.rs`'s actual
  validation logic; this node only confirmed that file exists.
