---
id: platforms-agents-buzz-agent
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "crates/buzz-agent/Cargo.toml describes the crate as 'Minimal, unbreakable ACP-compliant agent. Non-streaming. Tool-calls-as-output.', builds one library (buzz_agent, src/lib.rs) and one binary (buzz-agent, src/main.rs), plus a test-only fake-mcp binary built unconditionally for integration tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/Cargo.toml"
  - statement: "crates/buzz-agent/src/lib.rs carries no crate-level `//!` doc comment; its first line is `#![forbid(unsafe_code)]` followed directly by module declarations. No item in the crate has a `///` doc comment on its module-level declarations either — only individual struct fields and enum variants inside config.rs/types.rs carry `///` comments."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs"
  - statement: "crates/buzz-agent/README.md opens by stating the crate is a 'Minimal, unbreakable ACP-compliant LLM agent. Stdio in, tool calls out. Non-streaming. No persistence. No cleverness,' and its 'What It Is' section states the agent loops: call the LLM, get tool calls, run them via MCP, feed results back, repeat, terminating when the LLM stops requesting tools, the round cap is hit, or the client cancels."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:1-30"
  - statement: "lib.rs's public module surface is: `pub mod auth`, `pub mod catalog`, `pub mod config`, `pub mod model_capabilities`, `pub mod types`, plus re-exports `pub use catalog::{discover_databricks_models, ModelEntry}`, `pub use config::Provider`, `pub use types::AgentError`. `agent`, `builtin`, `handoff`, `hints`, `mcp`, `permission` and `wire` are private (`mod`, no `pub`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs"
  - statement: "lib.rs exposes `pub fn run() -> Result<(), Box<dyn std::error::Error>>`, the entry point src/main.rs calls (`buzz_agent::run()`), and `pub async fn authenticate_databricks(host: &str) -> Result<(), AgentError>`, used by the `buzz-agent auth databricks` subcommand."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs"
      - "crates/buzz-agent/src/main.rs"
  - statement: "config.rs defines `pub enum Provider { Anthropic, OpenAi, Databricks, DatabricksV2, OpenRouter }`, `pub struct Config` (the crate's central environment-derived configuration, with `pub fn from_env() -> Result<Self, String>`), `pub struct DatabricksModelFilter`, `pub enum OpenAiApi`, `pub enum HookServers`, and public constants including `PROTOCOL_VERSION`, `MAX_PROMPT_BYTES`, `MAX_SYSTEM_PROMPT_BYTES`, `MAX_TOOL_RESULT_BYTES`, `MAX_TOOL_CALLS_PER_TURN`, `HANDOFF_MAX_OUTPUT_TOKENS` and related handoff-budget constants."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "types.rs defines `pub enum AgentError { InvalidParams, Llm, LlmAuth, LlmModelNotFound, LlmContextExceeded, UnsupportedImageInput, Mcp, Cancelled }` with a `pub fn json_rpc_code(&self) -> i32` mapping each variant to a JSON-RPC error code, plus the wire/session types `ToolCall`, `ToolResult`, `LlmResponse`, `PricingIdentity`, `ProviderStop`, `ToolDef`, `CacheTotalState`, `TurnTotalState`, `TurnIOState`, `SessionUsageBaseline` and `StopReason`, all `pub`."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/types.rs"
  - statement: "catalog.rs defines `pub struct ModelEntry { pub id: String, pub name: String }` and `pub async fn discover_databricks_models(cfg: &Config) -> Result<Vec<ModelEntry>, AgentError>`, both re-exported at the crate root."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/catalog.rs"
  - statement: "auth.rs defines `pub trait TokenSource`, `pub struct StaticTokenSource`, `pub struct PkceOAuthConfig`, and `pub struct PkceOAuthTokenSource` with `pub fn new(cfg: PkceOAuthConfig) -> Result<Arc<Self>, AgentError>` and `pub async fn interactive_login(&self) -> Result<(), AgentError>`, implementing OAuth 2.0 PKCE for Databricks (and, per its own module comment, future browser-auth providers)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/auth.rs"
  - statement: "model_capabilities.rs defines `pub enum ThinkingMode`, `pub enum DatabricksV2Route`, `pub enum NormalizationPolicy`, `pub struct CapabilityResult`, `pub fn resolve(provider: &str, raw_model_id: &str) -> CapabilityResult`, `pub fn databricks_v2_known_models() -> &'static [String]` and `pub fn databricks_registry_label(raw_model_id: &str) -> Option<&'static str>`."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/model_capabilities.rs"
  - statement: "crates/buzz-agent/Cargo.toml's [dependencies] table lists only external crates -- tokio, serde, serde_json, serde_yaml, reqwest, rmcp, arc-swap, getrandom, tracing, tracing-subscriber, async-trait, axum, base64, hex, sha2, url, urlencoding, webbrowser, dirs, and (cfg(unix) only) nix -- with no path dependency on any other crate in this repository's workspace."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/Cargo.toml"
  - statement: "Exactly one crate in this repository's workspace, crates/sprig/Cargo.toml, declares `buzz-agent = { path = \"../buzz-agent\" }`; crates/sprig/src/main.rs dispatches to `buzz_agent::run()` when invoked as `buzz-agent` (argv0 or subcommand)."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "crates/sprig/src/main.rs"
  - statement: "crates/buzz-acp/Cargo.toml carries no path dependency on buzz-agent; buzz-acp spawns buzz-agent (or any other ACP-compliant agent binary) as a subprocess over stdio rather than linking it as a library, per the already-merged architecture-containers-agent-runtime node's own evidence."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "The README's 'Providers' section documents `Provider` as a Rust enum with one match arm per provider inside `Llm::complete`, states there is no trait, no `Box<dyn>` and no async-trait for provider dispatch, and that adding a provider means one match arm plus one body/parse pair in llm.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:262"
  - statement: "The README's 'Security Model' section states the crate's trust boundary is the operator who launched the agent -- the harness, MCP server binaries and API keys are trusted, while model output, tool results and prompts are untrusted and bounded by a documented table of mechanisms: single-consumer stdout channel, an MCP-child environment whitelist, process-group teardown via setpgid/killpg on transport break, dead-server lazy-restart with backoff, frame/response/tool-result size caps, and biased-select cancellation at every loop boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:295-329"
  - statement: "The README's 'What This Is NOT' section states the agent is non-streaming (one HTTP POST per round), non-persistent (in-memory per-process, no SQLite, context handoff on overflow instead of external storage), has no session/load support, and performs no agent-to-agent orchestration -- one model, one loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:331-344"
  - statement: "The README's 'Testing' section states the test strategy is real subprocess, no mocks: tests/fake_llm.rs spins up a real tokio::net::TcpListener to serve scripted LLM responses, tests/bin/fake_mcp.rs is a separate real binary controlled by env vars to simulate MCP fault paths, and regressions.rs test names each document the bug they lock down (e.g. assistant_text_preserved_across_prompts, mcp_init_timeout_kills_child, oversize_line_kills_connection)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:375-386"
  - statement: "src/main.rs is exactly `fn main() { if let Err(e) = buzz_agent::run() { eprintln!(...); std::process::exit(1); } }` -- the binary's entire body is a call into the library's `run()` function, so the library crate (`buzz_agent`) carries the whole implementation and the binary is a thin process entry point."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/main.rs"
  - statement: "The already-merged architecture-containers-agent-runtime node names buzz-agent as one of three crates composing the agent-runtime container, states buzz-agent's stated responsibility as 'a minimal, non-streaming ACP-compliant agent,' and explicitly excludes from its own scope 'the agent's exact LLM-provider selection and model-capability logic' (pointing at crates/buzz-agent/src/model_capabilities.rs and src/catalog.rs) and 'agent loop, security model, size limits' (pointing at crates/buzz-agent/README.md) -- the deeper, component-level detail this node supplies."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "launchpad/docs/corpus/templates/component.md is the merged template for a standalone software-component corpus node; it directs authors to set `type: implementation`, requires Responsibility/Public interface/Dependencies/Boundary/Relationships/Scope-and-omissions sections, and states a `part-of` relationship toward an architecture-component node's building-block table is optional, never required for the node's own validity."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "Because crates/buzz-agent/src/lib.rs carries no crate-level `//!` doc comment (the industry-model anchor launchpad/docs/corpus/templates/component.md's Evidence expectations section names first), this node's Responsibility claim is grounded instead in the crate's README.md opening lines and Cargo.toml `description` field, which is the template's own named fallback when no crate-level comment exists."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-agent/src/lib.rs"
      - "crates/buzz-agent/README.md:1-9"
      - "crates/buzz-agent/Cargo.toml"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.8
  - statement: "No architecture-component instance node (as distinct from the architecture-component template) exists in this corpus decomposing the agent-runtime container with a building-block table naming buzz-agent as a row; the closest existing, merged, resolvable target for this node's part-of relationship is architecture-containers-agent-runtime itself, whose own Technology table already lists buzz-agent as one of the container's constituent crates -- functionally the same containment relationship the component template's Relationships guidance describes, applied to the one container-level node that actually exists."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
      - "launchpad/docs/corpus/templates/architecture-component.md"
    confidence: 0.65
relationships:
  - type: part-of
    target: architecture-containers-agent-runtime
---

# Component: buzz-agent

`buzz-agent` (crate `crates/buzz-agent`, library name `buzz_agent`) is a single
Rust crate: a minimal, non-streaming, ACP-compliant LLM agent. This node
documents it as one standalone software component per
[`templates/component.md`](../../templates/component.md) — the crate's
responsibility, public interface, and real dependency edges — one level
below the agent-runtime container it lives inside
([`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)).
See [`node.schema.json`](../../schema/node.schema.json) for the front-matter
contract this satisfies and [`AGENTS.md`](../../AGENTS.md) for how this node
was authored and checked.

## Responsibility

`crates/buzz-agent/src/lib.rs` carries no crate-level `//!` doc comment, so
this responsibility statement is grounded in the crate's next-best authored
source: `Cargo.toml`'s `description` field — *"Minimal, unbreakable
ACP-compliant agent. Non-streaming. Tool-calls-as-output."* — and the
crate's `README.md`, which states the same thing at greater length: an agent
that receives an ACP `session/prompt` over stdio and loops — call the LLM,
get tool calls, run them via MCP, feed results back — until the LLM stops
requesting tools, a round cap is hit, or the client cancels. The binary
entry point (`src/main.rs`) is a two-line wrapper calling `buzz_agent::run()`
— the library crate carries the entire implementation.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `run` | fn (`lib.rs`) | Entry point; builds a multi-thread Tokio runtime and drives the stdin/stdout ACP loop or the `auth` subcommand. Called by `src/main.rs`. | `crates/buzz-agent/src/lib.rs` |
| `authenticate_databricks` | async fn (`lib.rs`) | Runs the Databricks OAuth 2.0 PKCE interactive login flow for the `buzz-agent auth databricks` subcommand. | `crates/buzz-agent/src/lib.rs` |
| `config::Provider` | enum (re-exported at crate root) | `Anthropic \| OpenAi \| Databricks \| DatabricksV2 \| OpenRouter` — selects the LLM wire dialect `Llm::complete` dispatches on. | `crates/buzz-agent/src/config.rs` |
| `config::Config` | struct + `from_env()` | Central environment-derived configuration (provider, model, size/timeout caps, hook servers, etc.). | `crates/buzz-agent/src/config.rs` |
| `types::AgentError` | enum (re-exported at crate root) | `InvalidParams \| Llm \| LlmAuth \| LlmModelNotFound \| LlmContextExceeded \| UnsupportedImageInput \| Mcp \| Cancelled`, each mapped to a JSON-RPC error code via `json_rpc_code()`. | `crates/buzz-agent/src/types.rs` |
| `catalog::ModelEntry`, `catalog::discover_databricks_models` | struct + async fn (re-exported at crate root) | `ModelEntry { id, name }`; discovers the Databricks model catalog for a configured host. | `crates/buzz-agent/src/catalog.rs` |
| `auth::TokenSource`, `StaticTokenSource`, `PkceOAuthConfig`, `PkceOAuthTokenSource` | trait + structs | OAuth 2.0 PKCE token acquisition/caching, used by the Databricks provider (and named as reusable for future browser-auth providers). | `crates/buzz-agent/src/auth.rs` |
| `model_capabilities::resolve`, `CapabilityResult`, `ThinkingMode`, `DatabricksV2Route`, `NormalizationPolicy` | fn + enums/struct | Per-model capability resolution (thinking/reasoning support, Databricks v2 wire routing, request-normalization policy). | `crates/buzz-agent/src/model_capabilities.rs` |
| `buzz-agent` binary | process | The crate's real external contract: ACP JSON-RPC 2.0 over stdio (`initialize`, `session/new`, `session/prompt`, `session/cancel`), documented in full in the crate README's ACP Transcript section. | `crates/buzz-agent/src/main.rs`, `crates/buzz-agent/README.md:68-130` |

`agent`, `builtin`, `handoff`, `hints`, `mcp`, `permission` and `wire` are
private modules (`mod`, not `pub mod`) — internal implementation, not part of
the crate's public interface.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `tokio` | Async runtime (multi-thread), stdin/stdout I/O, process spawning, timers, channels. | `crates/buzz-agent/Cargo.toml` |
| `reqwest` (rustls) | HTTPS client for LLM provider calls. | `crates/buzz-agent/Cargo.toml` |
| `rmcp` (client, transport-child-process) | MCP client — spawns and speaks to MCP server subprocesses over stdio. | `crates/buzz-agent/Cargo.toml` |
| `serde` / `serde_json` / `serde_yaml` | Wire (de)serialization for ACP JSON-RPC and config. | `crates/buzz-agent/Cargo.toml` |
| `axum` | Used by the Databricks OAuth 2.0 PKCE local-callback flow in `auth.rs`. | `crates/buzz-agent/Cargo.toml` |
| `nix` (cfg(unix) only) | Process-group signal/lifecycle control for MCP child teardown. | `crates/buzz-agent/Cargo.toml` |
| *(no internal Buzz crate)* | `buzz-agent`'s `[dependencies]` table names no other crate in this workspace — every dependency is an external crate. | `crates/buzz-agent/Cargo.toml` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `sprig` | Multicall binary; dispatches to `buzz_agent::run()` when invoked/linked as `buzz-agent`, bundling it with `buzz-acp` and `buzz-dev-mcp` into one deploy-anywhere artifact. | `crates/sprig/Cargo.toml`, `crates/sprig/src/main.rs` |

`buzz-acp` (the ACP harness) is **not** a build-time dependent: it spawns
`buzz-agent` as a subprocess over stdio, never links it as a library — the
container-level node
([`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md))
already establishes this distinction and it is not restated here as new
evidence, only cross-checked against `buzz-acp`'s own `Cargo.toml`.

## Boundary

This node does not describe:
- **The agent-runtime container's own decomposition, interfaces, deployment or
  security summary** — that is
  [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)'s
  subject; this node is the deeper detail it points at, not a replacement for it.
- **How this crate satisfies any spec, decision or contract** (ACP protocol
  conformance, NIP-AM usage-reporting shape, etc.) — that traceability question
  belongs to an `implementation-reference` node, per
  [`templates/component.md`](../../templates/component.md)'s own boundary, and
  none has been authored for this crate.
- **Install/usage/configuration instructions for a human running the crate** —
  `crates/buzz-agent/README.md` already covers this in depth (Quick Start,
  environment-variable table, provider dialects, MCP server wiring) and this
  node cites it rather than restating it.
- **The ACP wire protocol in full**, the reply-guard heuristic's exact
  substring-matching rules, or the MCP-driven-hooks contract (`_Stop`,
  `_PostCompact`) — all documented in the README and
  `docs/MCP_DRIVEN_HOOKS.md`, cited above, not duplicated here.

## Relationships

- `part-of`: [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)
  — `buzz-agent` is one of the three crates that container node's own
  Technology table names as constituents of the agent-runtime container. No
  dedicated `architecture-component` instance node exists yet for this
  container (only the template does); this node's own `INFERENCE` above
  records that the container node's Technology table is the closest existing,
  merged, resolvable target for the containment relationship
  [`templates/component.md`](../../templates/component.md) describes.

## Scope and omissions

**This node covers** `buzz-agent`'s responsibility, its public interface
(the crate's exported items and its real external contract — ACP over
stdio), its real dependency edges in both directions (cited to `Cargo.toml`,
never to a deployment manifest or process list), and its boundary against the
container-level node, an implementation-reference node, and its own README.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The agent-runtime container's full responsibility, interfaces and deployment implications | [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md) |
| Install/usage/configuration instructions, the full environment-variable table, ACP transcript, reply-guard rules, provider dialect details | `crates/buzz-agent/README.md` |
| MCP-driven hook tools (`_Stop`, `_PostCompact`) | `docs/MCP_DRIVEN_HOOKS.md` |
| How this crate's behavior satisfies the ACP specification or NIP-AM as a traceability artifact | Not yet authored (`implementation-reference` template exists; no instance for this crate) |
| The `buzz-acp` harness that spawns this agent as a subprocess | `crates/buzz-acp/README.md`, and the agent-runtime container node |

**Expected but not verified when this node was written:**

- **This is the first node authored from `templates/component.md`.** Whether
  its required sections and evidence expectations hold up for a second,
  differently-shaped component (e.g. one with internal Buzz-crate
  dependencies, or one with a crate-level `//!` doc comment) was not tested
  here.
- **Whether any consumer outside this repository's own workspace (a
  downstream fork, an external harness) links `buzz_agent` as a library was
  not checked.** Only this repository's own `Cargo.toml` files were searched
  for the `depended-on-by` direction.
- **Line-by-line correspondence between every README claim cited above and
  the current source was not re-derived independently for every line** —
  `model_capabilities.rs`, `catalog.rs`, `config.rs`, `types.rs` and `auth.rs`
  were read directly to confirm the public-interface table; the security,
  testing and "What This Is NOT" claims rely on the README text itself,
  cross-checked against `main.rs` and `lib.rs`'s module list but not against
  every internal implementation detail the README describes (e.g. the exact
  byte-cap enforcement sites).
