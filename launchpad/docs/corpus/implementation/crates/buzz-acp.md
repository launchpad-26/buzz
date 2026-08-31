---
id: implementation-crates-buzz-acp
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-acp's Cargo.toml describes it as \"ACP harness that bridges Buzz events to AI agents\"; the crate builds one library (buzz_acp) and one binary (buzz-acp), the binary's entire main() body being `buzz_acp::run()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "crates/buzz-acp/src/main.rs"
  - statement: "buzz_acp::run() is the crate's only public function; the only other item re-exported from the crate root is `pub use usage::TurnUsage`. Every module (acp, config, engram_fetch, filter, observer, pool, pool_lifecycle, prompt_framing, prompt_project, queue, relay, setup_mode, usage) is declared as a private `mod`, not `pub mod`, so no downstream crate can reach into them directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
  - statement: "Within the workspace, only crates/sprig has a real Cargo path dependency on buzz-acp (`buzz-acp = { path = \"../buzz-acp\" }`), and its main.rs dispatches to `buzz_acp::run()` when invoked under the `buzz-acp` argv0 name. crates/buzz-relay and crates/buzz-cli each mention \"buzz-acp\" only in Cargo.toml comments explaining a mirrored rustls crypto-provider setup, not as a dependency — grepped directly and confirmed neither Cargo.toml declares buzz-acp as a dependency."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "crates/sprig/src/main.rs"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-cli/Cargo.toml"
  - statement: "buzz_acp::run() dispatches, before any long-running state is created, to one of three lightweight helper subcommands (models, auth-methods, authenticate, each parsed by its own clap::Parser struct in config.rs and requiring no relay connection) or falls through to the default path: parse Config::from_cli(), then branch into setup_mode::run_setup_listener() if BUZZ_ACP_SETUP_PAYLOAD is set, else initialize the agent pool and enter the main event loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
      - "crates/buzz-acp/src/config.rs"
  - statement: "acp.rs's own module doc comment states its five-step AcpClient lifecycle: AcpClient::spawn (launch the agent binary as a subprocess), AcpClient::initialize (protocol version negotiation), AcpClient::session_new (create a session, passing MCP server config), AcpClient::session_prompt_with_idle_timeout (send a prompt with idle/hard deadlines, return a stop reason), and AcpClient::session_cancel / AcpClient::cancel_with_cleanup (cancel an in-flight turn). Framing is newline-delimited JSON-RPC 2.0 over the subprocess's stdio, with a 10 MB MAX_LINE_SIZE cap on any single agent stdout line."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs"
  - statement: "pool.rs owns agent-subprocess supervision (AgentPool, OwnedAgent, SessionState) and, after each turn completes, maps the ACP StopReason to a NIP-AM StopReason (acp_stop_to_core) and best-effort publishes a kind:44200 NIP-AM agent-turn-metric event, NIP-44 encrypted to the agent's owner, built from a (turn, cumulative) TokenCounts pair that is never derived as a sum of input+output (the comment states this is a NIP-AM MUST-NOT)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs"
      - "docs/nips/NIP-AM.md"
      - "crates/buzz-core/src/kind.rs"
  - statement: "queue.rs implements a per-channel FIFO event queue (EventQueue, QueuedEvent, FlushBatch): at most one prompt is in flight per channel at a time, a channel's queued events are drained into one batched ACP session/prompt call, and channel dispatch order is oldest-channel-first across the queue as a whole."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/queue.rs"
  - statement: "filter.rs's own module doc comment states its three responsibilities: building an evalexpr context from a Nostr event, evaluating boolean filter expressions with a hard timeout, and matching events against ordered subscription rules (first match wins). A unit test named test_filter_error_fails_closed_no_fallthrough asserts that a filter expression error drops the event rather than falling through to a later, possibly-matching rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/filter.rs"
  - statement: "relay.rs (HarnessRelay, RelayEventPublisher, RestClient) owns the harness's two relay-facing surfaces: a WebSocket connection authenticated via NIP-42, and channel discovery over the relay's REST API (GET /api/channels?member=true by default), reused elsewhere in the crate (engram_fetch.rs's RestClient-based core-memory fetch) rather than each caller opening its own connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
      - "crates/buzz-acp/src/engram_fetch.rs"
  - statement: "config.rs's own module doc comment states the configuration model is CLI-first: every option is a CLI flag with an environment-variable fallback, plus an optional TOML config file for complex per-channel subscription rules. Its clap subcommand structs are ModelsArgs, AuthMethodsArgs, AuthenticateArgs (each flattening a shared AuthAgentArgs), and the default CliArgs."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "setup_mode.rs's module doc comment states a non-negotiable contract: when Buzz Desktop determines a managed agent is NotReady (missing provider, model, or credentials), it spawns buzz-acp with a BUZZ_ACP_SETUP_PAYLOAD env var; buzz-acp trusts that payload as the sole readiness source and does not re-derive readiness itself, and normal startup gains no second readiness path — the early branch is entered only when that variable is set."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/setup_mode.rs"
  - statement: "engram_fetch.rs's module doc comment states it fires one synchronous query for an agent's NIP-AE \"core\" engram head at new-session creation, renders a found body into a <core-memory> prompt section, emits an onboarding nudge when no body is found, and emits nothing on any transport/parse error so a relay outage is never mistaken for \"no core\" (which would otherwise invite the agent to overwrite real, unreachable memory)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/engram_fetch.rs"
      - "docs/nips/NIP-AE.md"
  - statement: "prompt_project.rs's module doc comment states it parses a channel's authoritative NIP-MP project home for the ACP [Context] prompt section, resolving PromptProjectInfo (name, slug, owner, coordinate, default repo owner/id) from a channel's member repository binding rather than from a project's own buzz-channel field, which the code comments describe as presentation metadata only."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/prompt_project.rs"
      - "docs/nips/NIP-MP.md"
  - statement: "None of docs/nips/NIP-AM.md, docs/nips/NIP-AE.md, or docs/nips/NIP-MP.md has a corpus node id: git ls-tree of origin/launchpad's launchpad/docs/corpus tree at this revision contains no node whose id or path corresponds to any of the three. Per AGENTS.md's node-creation step 9, this rules out declaring an `implements` relationship toward any of them; they are named by repository path in the Target section instead."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no node matching NIP-AM, NIP-AE or NIP-MP present, checked at commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "crates/buzz-acp/README.md's configuration table documents BUZZ_ACP_IDLE_TIMEOUT's default as 620 seconds. config.rs's DEFAULT_IDLE_TIMEOUT_SECS constant, used whenever neither --idle-timeout nor the deprecated --turn-timeout is supplied (Config::from_cli's own resolution comment states this precedence explicitly), is 900, with a doc comment explaining the 900s sizing rationale (300s of headroom above a 600s max shell timeout for slow sub-tool calls). No third value overrides DEFAULT_IDLE_TIMEOUT_SECS at the call site, so the README's documented default and the code's actual default disagree by 280 seconds."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/config.rs"
  - statement: "architecture-containers-agent-runtime (status draft, on origin/launchpad at this revision) names buzz-acp as one of three crates composing the \"Container: Agent Runtime\", in a table giving its role as \"The ACP harness: relay client, event router, agent-subprocess supervisor\" — the same three-part split (relay/event/pool) this node's own Implementation surface table documents at module grain."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Representative tests exist per module rather than as one crate-level suite: pool_lifecycle.rs carries its own #[cfg(test)] mod tests (e.g. retry_backoff_doubles_and_caps_at_five_minutes, stale_or_duplicate_wake_result_is_rejected) and is additionally compiled as a standalone integration-test target via crates/buzz-acp/tests/pool_lifecycle_state.rs, which re-includes the source file with #[path] rather than testing through the public API; queue.rs (e.g. test_fifo_fairness_picks_oldest_channel, test_in_flight_blocks_same_channel) and pool.rs (a dedicated \"NIP-AM emit-hook unit tests\" section, e.g. acp_stop_to_core coverage of every ACP stop reason) carry in-module unit tests of the same shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool_lifecycle.rs"
      - "crates/buzz-acp/tests/pool_lifecycle_state.rs"
      - "crates/buzz-acp/src/queue.rs"
      - "crates/buzz-acp/src/pool.rs"
---

# buzz-acp: implementation reference

`crates/buzz-acp` is the ACP harness that bridges Buzz relay events to any
agent process that speaks the [Agent Client Protocol](https://agentclientprotocol.com/)
over stdio. It claims to realize, in whole or in part, four separate
contracts that live in this repository but are not yet corpus nodes: the ACP
wire protocol itself (an external spec, not repository-owned), and three
Buzz-authored NIPs — NIP-AM (agent turn-usage metrics), NIP-AE (agent core
memory / engrams), and NIP-MP (project-home resolution). This node documents
the crate's realization of the two things a corpus reader can check today:
its own `README.md`'s documented contract, and the three NIPs' wire shapes,
against what the code in `crates/buzz-acp/src` actually does.

## Target

Four targets, none yet a corpus node:

- **The ACP spec** (external, `https://agentclientprotocol.com/`) — the
  JSON-RPC 2.0 stdio protocol `acp.rs`'s `AcpClient` speaks as a client to a
  spawned agent subprocess (`initialize`, `session/new`, `session/prompt`,
  `session/cancel`).
- **`docs/nips/NIP-AM.md`** — per-turn token-usage metrics, published as
  `kind:44200` events. `crates/buzz-core/src/kind.rs`'s
  `KIND_AGENT_TURN_METRIC` constant is the shared kind registry entry both
  sides (this crate as publisher, the relay as router) depend on.
- **`docs/nips/NIP-AE.md`** — agent "core" engram memory, fetched once per new
  ACP session by `engram_fetch.rs` and rendered into a `<core-memory>` prompt
  section.
- **`docs/nips/NIP-MP.md`** — project-home resolution, parsed by
  `prompt_project.rs` into the ACP `[Context]` prompt section.

None of the three NIP documents carries a corpus node id at this revision
(confirmed against `origin/launchpad`'s corpus tree) — no `implements` edge is
declared toward any of them; a future node documenting each NIP is the place
to add that edge.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/lib.rs` — `pub fn run()` | Crate entry point; the binary's `main()` is exactly `buzz_acp::run()` | Only public function in the crate besides `pub use usage::TurnUsage` |
| `src/lib.rs` — subcommand dispatch (`is_subcommand`, `tokio_main`) | Routes to `models` / `auth-methods` / `authenticate` helper subcommands, or falls through to `setup_mode` / the main pool+event loop | Subcommand parsing happens before any relay connection is opened |
| `src/config.rs` — `CliArgs`, `Config`, `ModelsArgs`, `AuthAgentArgs`, `AuthMethodsArgs`, `AuthenticateArgs` | CLI-flag/env-var/TOML configuration surface (module doc comment: "CLI-first: every option is a CLI flag with env var fallback") | `DEFAULT_IDLE_TIMEOUT_SECS = 900`, see *Divergences* |
| `src/acp.rs` — `AcpClient` | ACP JSON-RPC 2.0 client over the agent subprocess's stdio: `spawn`, `initialize`, `session_new`, `session_prompt_with_idle_timeout`, `session_cancel`/`cancel_with_cleanup` | NDJSON framing, 10 MB `MAX_LINE_SIZE` |
| `src/pool.rs` — `AgentPool`, `OwnedAgent`, `SessionState` | Agent-subprocess supervision, session lifecycle, per-turn NIP-AM kind:44200 metric publish (`acp_stop_to_core`, `TokenCounts` computation) | Also computes and publishes turn usage; never sums input+output as `total_tokens` (NIP-AM MUST NOT) |
| `src/pool_lifecycle.rs` — `PoolLifecycle<P>` | Lazy-pool wake/retry state machine (`--lazy-pool`): bounded exponential backoff between failed pool-initialization attempts | Compiled twice: as a crate module and, via `#[path]`, as its own integration-test target (`tests/pool_lifecycle_state.rs`) |
| `src/queue.rs` — `EventQueue`, `QueuedEvent`, `FlushBatch` | Per-channel FIFO event queue; at most one prompt in flight per channel; oldest-channel-first dispatch; batches a channel's queued events into one `session/prompt` | |
| `src/filter.rs` — `SubscriptionRule`, `evaluate_filter`, `match_event` | evalexpr-based subscription filtering: builds an evalexpr context from a Nostr event, evaluates boolean filter expressions under a hard timeout, matches events against ordered rules (first match wins), fails closed on evaluation error | |
| `src/relay.rs` — `HarnessRelay`, `RelayEventPublisher`, `RestClient` | NIP-42 authenticated WebSocket connection; REST channel discovery (`GET /api/channels?member=true` by default); event publish | `RestClient` reused by `engram_fetch.rs` |
| `src/observer.rs` — `ObserverHandle` | In-process, best-effort telemetry/replay bus (`ObserverEvent`) for local observability, independent of the relay | |
| `src/setup_mode.rs` — `SetupPayload`, `run_setup_listener` | Desktop-driven "not-ready agent" listener path, entered only when `BUZZ_ACP_SETUP_PAYLOAD` is set; trusts the Desktop's readiness determination without re-deriving it | Contract stated as "NON-NEGOTIABLE" in the module's own doc comment |
| `src/engram_fetch.rs` — `build_core_section` | NIP-AE core-engram fetch and prompt rendering at new-session creation | Emits nothing on transport/parse error, to avoid mistaking an outage for "no core" |
| `src/prompt_project.rs` — `PromptProjectInfo`, project resolution | NIP-MP project-home parsing for the ACP `[Context]` section | Resolves from a channel's member-repository binding, not a project's own `buzz-channel` field |
| `src/prompt_framing.rs` — `semantic_section`, `semantic_section_with_attributes` | Shared `<tag>...</tag>` framing helpers for standing prompt context, used by `engram_fetch.rs` and `prompt_project.rs` | |
| `src/usage.rs` — `TurnUsage`, `GooseSessionUpdateNotification` | Deserializes `_goose/unstable/session/update` notifications and computes per-turn token deltas from cumulative counters (goose and buzz-agent share this wire format) | `TurnUsage` is the crate's one re-exported public type; consumed inside the crate by `pool.rs`'s `TurnCompletionGuard`, not observed to be consumed by any other crate in this workspace |

## Divergences

- **`BUZZ_ACP_IDLE_TIMEOUT` default mismatch.** `crates/buzz-acp/README.md`'s
  configuration table documents the default as `620`. `config.rs`'s
  `DEFAULT_IDLE_TIMEOUT_SECS` constant — the value actually used by
  `Config::from_cli`'s idle-timeout resolution whenever neither
  `--idle-timeout` nor the deprecated `--turn-timeout` is supplied — is `900`,
  with an explicit doc comment justifying that value (300s of headroom above
  a 600s max shell timeout). No later override changes this at the call
  site. This is drift between documentation and code, not a documented
  intentional deviation; per the template's evidentiary-weight rule this is
  recorded as a `FACT`, both sides opened directly, not as a hedge.
- **No other divergence found** between `README.md`'s stated behavior (event
  loop steps, author-gate modes, heartbeat semantics, forum-channel opt-in)
  and the code in `src/lib.rs`, `src/config.rs`, and `src/filter.rs` that
  implements each — checked by reading `README.md`'s "How It Works",
  "Inbound Author Gate", "Heartbeat Semantics", and "Forum Channels"
  sections against the corresponding code paths in the modules listed in
  *Implementation surface* above. This is a narrower check than exhaustive:
  it covers the sections above, not every configuration flag documented in
  `README.md`.

## Verification

Verification is per-module unit tests, not one crate-level suite:
`pool_lifecycle.rs`, `queue.rs`, `filter.rs`, `pool.rs`, `config.rs`, and
every other module listed in *Implementation surface* carry their own
`#[cfg(test)] mod tests`. `pool_lifecycle.rs` is additionally compiled as a
standalone integration-test target, `crates/buzz-acp/tests/pool_lifecycle_state.rs`,
which re-includes the module source via `#[path]` rather than exercising it
through the crate's public API — this crate's only file under `tests/`. No
buzz-acp-specific end-to-end test was found in this crate; the repository's
multi-agent E2E guide (`TESTING.md`) covers the harness only as part of a
broader agent-integration scenario, not as a dedicated buzz-acp suite. `cargo
test -p buzz-acp` is the command that runs everything enumerated here;
`--lib` also runs the in-module suites without the separate integration
target.

## Relationships

- part-of: architecture-containers-agent-runtime

## Scope and omissions

**This node covers** what `crates/buzz-acp` is responsible for as a crate:
its public entry point, its module-level implementation surface, its
partial realization of the ACP spec and of NIP-AM/NIP-AE/NIP-MP, one
verified divergence between its own documentation and its code, and how its
behavior is checked today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent LLM-call-then-tool-call loop itself | `crates/buzz-agent` (a separate crate; `buzz-acp` spawns it as a subprocess but does not implement it) |
| The developer MCP tool surface (shell, file-edit, Buzz-CLI-backed tools) the spawned agent calls | `crates/buzz-dev-mcp` |
| Persona-pack format and merge rules | `crates/buzz-persona` (a direct dependency of `buzz-acp`, consumed not implemented here) |
| The relay-side workflow engine that produces `kind:46010` workflow-approval events this crate subscribes to | `crates/buzz-workflow`, compiled into `buzz-relay` |
| Buzz Desktop's managed-agent launch, access-policy, and BYOH catalog logic | `desktop/src-tauri/src/managed_agents/` |
| The container-level responsibility, ownership boundary, and cross-container interfaces of the agent runtime as a whole | `architecture-containers-agent-runtime` (this node's `part-of` target) |
| The full ACP wire protocol and NIP-AM/NIP-AE/NIP-MP specifications themselves | `docs/nips/NIP-AM.md`, `docs/nips/NIP-AE.md`, `docs/nips/NIP-MP.md`, and the external ACP spec |

**Expected but not verified when this node was written:**

- **Whether every configuration flag in `README.md`'s tables matches its
  code default.** Only the idle-timeout default was checked end-to-end
  (found to diverge); the remaining flags in the "Core", "Parallel Agents &
  Heartbeat", and "Inbound Author Gate" tables were read but not each
  individually traced to a `config.rs` constant.
- **Whether any consumer outside this repository imports `buzz_acp` as a
  library** (as opposed to running the `buzz-acp` binary or `sprig`'s
  multicall dispatch) — this node only checked dependents inside this
  repository's own Cargo workspace.
- **Runtime behavior of the ACP subprocess lifecycle under real agent
  binaries** (goose, codex-acp, claude-agent-acp) was not exercised; this
  node is a static-code reading, not a runtime observation.
