---
id: implementation-crates-buzz-agent
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
  - statement: "buzz-agent's Cargo.toml describes it as \"Minimal, unbreakable ACP-compliant agent. Non-streaming. Tool-calls-as-output.\", ships two [[bin]] targets (buzz-agent at src/main.rs, and a test-only fake-mcp at tests/bin/fake_mcp.rs built unconditionally because Cargo cannot gate a bin on cfg(test)), and declares zero internal buzz-* path dependencies -- its [dependencies] table lists only external crates (tokio, serde, serde_json, serde_yaml, reqwest, rmcp, arc-swap, getrandom, tracing, tracing-subscriber, async-trait, axum, base64, hex, sha2, url, urlencoding, webbrowser, dirs, plus a unix-only nix dependency for process-group signal handling)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/Cargo.toml"
  - statement: "src/main.rs is a 6-line entry point that calls buzz_agent::run() and exits the process with status 1 on error; lib.rs opens with #![forbid(unsafe_code)], declares the module tree (mod agent, pub mod auth, mod builtin, pub mod catalog, pub mod config, mod handoff, mod hints, mod llm, mod mcp, pub mod model_capabilities, mod permission, pub mod types, mod wire), and re-exports discover_databricks_models and ModelEntry from catalog, Provider from config, and AgentError from types as its public library surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/main.rs"
      - "crates/buzz-agent/src/lib.rs:1-18"
  - statement: "lib.rs's pub fn run (the process entry point) and its handle_request JSON-RPC method-dispatch match arm route six inbound methods to handlers: the five standard ACP methods \"initialize\", \"session/new\", \"session/prompt\" (spawned onto its own task via spawn_prompt), \"session/set_model\", and \"session/cancel\", plus one goose-compatible non-standard extension, \"_goose/unstable/session/steer\" (documented in-line as mirroring goose's own steer wire contract); any other method name falls through to a METHOD_NOT_FOUND wire response."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs:149"
      - "crates/buzz-agent/src/lib.rs:286-324"
  - statement: "crates/sprig/Cargo.toml depends on buzz-agent as a path dependency (path = \"../buzz-agent\"), and crates/sprig/src/main.rs's argv0 dispatch calls buzz_agent::run() when invoked as \"buzz-agent\"."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "crates/sprig/src/main.rs"
  - statement: "desktop/src-tauri/Cargo.toml also depends on buzz-agent as a path dependency, aliased buzz_agent_pkg -- checked across every crates/*/Cargo.toml plus desktop/src-tauri/Cargo.toml, these two (sprig and the desktop Tauri backend) are the only in-workspace dependents. Desktop uses it for two distinct purposes, neither of which spawns the buzz-agent binary as a subprocess: (1) desktop/src-tauri/src/managed_agents/git_bash.rs reads buzz_agent_pkg::WINDOWS_SHELL_RESOLUTION_ENV to resolve the same Windows Git Bash environment keys buzz-agent's own MCP-child spawner (spawn_one()) forwards, keeping the two allowlists in sync by sharing the constant; (2) desktop/src-tauri/src/commands/agent_models_databricks.rs calls buzz_agent_pkg::discover_databricks_models, ::authenticate_databricks, ::config::Config::for_discovery, ::config::DatabricksModelFilter, ::config::Provider and ::AgentError directly, so Desktop's own model-picker UI can list and authenticate against Databricks model catalogs without spawning a buzz-agent process at all."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:108"
      - "desktop/src-tauri/src/managed_agents/git_bash.rs:116-136"
      - "desktop/src-tauri/src/commands/agent_models_databricks.rs:99-226"
  - statement: "The merged corpus node architecture-containers-agent-runtime names buzz-agent as one of three crates composing the agent-runtime container, and its own evidence ledger records that buzz-acp depends on buzz-persona directly while buzz-agent's Cargo.toml carries no such dependency, and that neither buzz-acp, buzz-agent, buzz-dev-mcp nor sprig depends on buzz-db or buzz-search -- i.e. persona-pack resolution, Buzz-CLI-backed tool execution, and durable Postgres/search access are harness- or MCP-server-side responsibilities this crate does not own."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "crates/buzz-agent/README.md documents the agent's own loop (\"call the LLM -> get tool calls -> run them via MCP -> feed results back -> repeat\"), its non-streaming single-HTTP-POST-per-round LLM call, its ACP transcript (initialize, session/new, session/prompt, with session/update tool_call/tool_call_update notifications), its full environment-variable configuration surface (README's Configuration table), its provider dispatch across Anthropic/OpenAI-compatible/OpenRouter/Databricks endpoints, its MCP-server spawning and server__tool namespacing, its Security Model and Bounded Everything tables, and an explicit \"What This Is NOT\" boundary list."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md"
  - statement: "README's \"What This Is NOT\" section states nine explicit non-goals: not a framework (no plugins/recipes/slash commands/modes beyond advisory, fail-open, budget-bounded MCP hook tools), not streaming, not persistent (in-memory per-process, no SQLite, context handoff instead of external persistence), not an SDK (a binary with a stdin/stdout protocol seam), not a UI, not authenticated (API keys come from environment only), not networked MCP (stdio transport only, no HTTP/SSE), not load-able (no session/load, advertises loadSession: false), and not a router (no agent-to-agent, no fan-out, no orchestration -- one model, one loop)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md"
  - statement: "Each module's own doc-comment header states a distinct, non-overlapping responsibility: auth.rs owns LLM request bearer-token sourcing (StaticTokenSource and a PKCE OAuth 2.0 engine for Databricks with on-disk cache); mcp.rs owns the stdio MCP client registry and server__tool namespacing; llm.rs owns the per-provider HTTP request/response shape as one Rust enum with one match in Llm::complete (no trait, no Box<dyn>); handoff.rs owns context-handoff/summarization when the token budget is exceeded; permission.rs owns the whole session/request_permission correlation lifecycle (process-wide admission semaphore, abort-safe cleanup, claim-before-wake delivery); hints.rs owns AGENTS.md/skill discovery from .agents/skills, .goose/skills and .claude/skills; builtin.rs owns the in-process load_skill tool that bypasses MCP; catalog.rs owns Databricks model-catalog discovery without triggering a browser OAuth flow; config.rs owns environment-variable parsing including the ThinkingEffort enum; wire.rs owns JSON-RPC 2.0 framing types and error codes; model_capabilities.rs owns the runtime interpreter for the embedded scripts/model-capabilities.json six-axis model-capability manifest; agent.rs owns RunCtx, the tool-call loop, and per-turn budget enforcement (MAX_PROMPT_BYTES, MAX_TOOL_CALLS_PER_TURN, MAX_TOOL_RESULT_BYTES)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/auth.rs:1-16"
      - "crates/buzz-agent/src/mcp.rs:1-27"
      - "crates/buzz-agent/src/llm.rs:1-25"
      - "crates/buzz-agent/src/handoff.rs:1-25"
      - "crates/buzz-agent/src/permission.rs:1-25"
      - "crates/buzz-agent/src/hints.rs:1-24"
      - "crates/buzz-agent/src/builtin.rs:1-13"
      - "crates/buzz-agent/src/catalog.rs:1-14"
      - "crates/buzz-agent/src/config.rs:1-3"
      - "crates/buzz-agent/src/wire.rs:1-18"
      - "crates/buzz-agent/src/model_capabilities.rs:1-25"
      - "crates/buzz-agent/src/agent.rs:1-25"
  - statement: "The test suite is real-subprocess, no-mock per README's own Testing section: tests/common/mod.rs's Harness spawns the actual compiled binary via env!(\"CARGO_BIN_EXE_buzz-agent\") and tokio::process::Command; tests/fake_llm.rs binds a real tokio::net::TcpListener rather than an HTTP mocking library; tests/bin/fake_mcp.rs is a separate real subprocess controlled by fault-injection env vars (FAKE_MCP_HANG_INIT, FAKE_MCP_TOOL_DELAY, FAKE_MCP_SPAWN_GRANDCHILD). Representative tests: assistant_text_preserved_across_prompts, mcp_init_timeout_kills_child, cancel_leaves_history_valid_for_next_prompt, and hook_stop_budget_exhausted in tests/regressions.rs (3583 lines); test_full_tool_call_transcript and test_session_new_rejects_relative_cwd in tests/golden_transcripts.rs; skills_loaded_from_agents_skills_dir and symlinked_skill_dir_is_discovered in tests/hints_integration.rs; and the permission-broker request/response flow exercised in tests/permission_boundary.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md"
      - "crates/buzz-agent/tests/common/mod.rs:105-116"
      - "crates/buzz-agent/tests/regressions.rs"
      - "crates/buzz-agent/tests/golden_transcripts.rs"
      - "crates/buzz-agent/tests/hints_integration.rs"
      - "crates/buzz-agent/tests/permission_boundary.rs"
  - statement: "README's Configuration table and its Bounded Everything table both state BUZZ_AGENT_MAX_HISTORY_BYTES defaults to 1048576 (1 MiB, \"Old turns are evicted past this\" / \"History window\"), but config.rs's actual default at the parse_env call site is 16 * 1024 * 1024 (16 MiB) -- a real, sixteen-fold divergence between the documented default and the code's actual default, not a rounding difference."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:166"
      - "crates/buzz-agent/README.md:317"
      - "crates/buzz-agent/src/config.rs:722"
  - statement: "README's BUZZ_AGENT_MAX_TOOL_RESULT_TEXT_BYTES default (51200 / 50 KiB) matches config.rs's DEFAULT_TOOL_RESULT_TEXT_BYTES constant (50 * 1024 = 51200) exactly -- checked as a second env-var default alongside the divergent one above, to establish the divergence found is not evidence of the whole table being stale."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md:167"
      - "crates/buzz-agent/src/config.rs:390"
      - "crates/buzz-agent/src/config.rs:723-726"
  - statement: "No file under launchpad/decisions/ mentions buzz-agent (checked directly), and no ACP or MCP specification document is checked into this repository under docs/ (only docs/MCP_DRIVEN_HOOKS.md exists, and it documents this repository's own hook-tool convention, not the ACP or MCP protocols themselves) -- buzz-agent's realization target is therefore its own README's documented self-contract, not an ADR, NIP, or repository-local specification file, and the ACP/MCP protocols it implements are external specifications (agentclientprotocol.com, modelcontextprotocol.io) with no corpus node id."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/README.md"
      - "docs/MCP_DRIVEN_HOOKS.md"
relationships:
  - type: part-of
    target: architecture-containers-agent-runtime
---

# buzz-agent: implementation reference

`crates/buzz-agent` is a minimal, non-streaming, reference-quality ACP-compliant
agent binary and library: it speaks the Agent Client Protocol (ACP) as JSON-RPC 2.0
over its own stdio to whatever client spawned it, calls one of several LLM provider
HTTP APIs, and executes the LLM's tool calls by spawning MCP servers as child
processes over stdio. It claims to realize its own documented self-contract in
`crates/buzz-agent/README.md` -- there is no separate ADR or NIP document this crate
implements; the README **is** the specification this node traces the code against.

## Target

The target is `crates/buzz-agent/README.md` itself: the crate's own README states,
in prose, what the agent must do (the ACP method surface, the provider dialects, the
security/trust boundary, the explicit "What This Is NOT" non-goals, and the full
environment-variable configuration contract) and is the closest thing this crate has
to a governing specification. No repository ADR under `launchpad/decisions/` mentions
`buzz-agent`, and no ACP or MCP protocol specification is checked into this
repository (only `docs/MCP_DRIVEN_HOOKS.md`, which documents this repository's own
hook-tool convention layered on top of MCP, not the MCP or ACP protocols
themselves). The ACP and MCP protocols this crate implements are external
specifications at [agentclientprotocol.com](https://agentclientprotocol.com) and
[modelcontextprotocol.io](https://modelcontextprotocol.io); neither has a corpus node
id, so this node declares no `implements` edge toward either, per
`implementation-reference`'s own rule against inventing an edge to a nonexistent id.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/main.rs` | README "Quick Start" — the binary entry point | 6 lines: calls `buzz_agent::run()`, exits 1 on error |
| `src/lib.rs`, `pub fn run` | README "ACP Transcript" — process startup, stdio framing loop | `#![forbid(unsafe_code)]` at the crate root |
| `src/lib.rs`, `handle_request` dispatch (`"initialize"`, `"session/new"`, `"session/prompt"`, `"session/set_model"`, `"session/cancel"`, plus the non-standard `"_goose/unstable/session/steer"`) | README's stated "Three request methods ... one inbound notification" (the five ACP-standard methods; the sixth is a documented goose-compatibility extension, not part of ACP proper) | `session/prompt` is spawned onto its own task (`spawn_prompt`) so one session's prompt cannot block another |
| `src/agent.rs` (`RunCtx`, the tool-call loop) | README's "The agent loops: call the LLM → get tool calls → run them via MCP → feed results back → repeat" | Also enforces `MAX_PROMPT_BYTES`, `MAX_TOOL_CALLS_PER_TURN`, `MAX_TOOL_RESULT_BYTES` |
| `src/llm.rs` (`Llm::complete`, one `Provider` enum, one `match`) | README's Providers table (Anthropic, OpenAI-compatible, OpenRouter, Databricks, Databricks v2) | README states explicitly: "There is no trait, no `Box<dyn>`, no async-trait" |
| `src/auth.rs` (`TokenSource`, `StaticTokenSource`, `PkceOAuthTokenSource`) | README's Databricks OAuth 2.0 PKCE flow description | On-disk token cache keyed by `sha256(discovery_url\|client_id\|scopes)` |
| `src/mcp.rs` (`McpRegistry`, `server__tool` namespacing) | README's "MCP Servers" section | Stdio transport only, per README's explicit non-goal "Not networked MCP" |
| `src/permission.rs` (`PermissionBroker`) | README's implicit `session/request_permission` correlation (the client-side permission ask referenced by the Security Model table's cancellation row) | Process-wide admission semaphore; abort-safe `Drop`-based cleanup |
| `src/handoff.rs` (`ContextRecovery`, `HandoffOutcome`) | README's "Not persistent ... the agent summarizes its own history and continues (context handoff)" | Governed by `BUZZ_AGENT_MAX_CONTEXT_TOKENS` / `BUZZ_AGENT_MAX_HANDOFFS` |
| `src/hints.rs`, `src/builtin.rs` (`SkillEntry`, `load_skill`) | README does not name this surface directly; it is the on-disk `AGENTS.md`/skill-directory discovery feeding the built-in `load_skill` tool | Searches `.agents/skills`, `.goose/skills`, `.claude/skills` |
| `src/catalog.rs` (`discover_databricks_models`, `ModelEntry`) | README's Databricks provider row | Never opens a browser; returns `Err(AgentError::LlmAuth)` on a cold PKCE cache |
| `src/config.rs` (`Config::from_env`, `ThinkingEffort`) | README's Configuration table (environment variables only, "No flags, no config files") | See *Divergences* below for one default that does not match the table |
| `src/wire.rs` (`WireMsg`, `Inbound`, JSON-RPC error codes) | README's stated wire framing ("Each line is one newline-terminated JSON value") | `PARSE_ERROR`/`INVALID_REQUEST`/`METHOD_NOT_FOUND`/`INVALID_PARAMS` per JSON-RPC 2.0 |
| `src/model_capabilities.rs` | Not documented in this crate's own README; realizes `scripts/model-capabilities.json`'s six-axis per-model capability manifest, shared with a TypeScript interpreter in `desktop/` | Embedded at compile time via `include_str!`, cached in a `OnceLock` |
| `src/types.rs` (`ToolResultContent`, `AgentError`, history/turn types) | Shared domain types referenced throughout the table above | `AgentError` is one of three symbols re-exported from `lib.rs`'s public surface |

**Direct library consumers, not just process spawners.** `crates/sprig` links `buzz-agent`
to dispatch to `buzz_agent::run()` when invoked as `buzz-agent` (the process-spawning
path README documents). Separately, and not documented in the README at all,
`desktop/src-tauri/Cargo.toml` also depends on this crate directly (aliased
`buzz_agent_pkg`) for two purposes that never spawn a `buzz-agent` process: reading
`WINDOWS_SHELL_RESOLUTION_ENV` to keep Desktop's own Windows Git Bash resolution in
sync with this crate's MCP-child env allowlist, and calling
`discover_databricks_models`/`authenticate_databricks`/`Config::for_discovery`/
`DatabricksModelFilter`/`Provider`/`AgentError` directly so Desktop's model-picker UI
can list and authenticate Databricks models without spawning the agent at all. `pub
async fn authenticate_databricks` (declared directly in `lib.rs`, not one of the three
`pub use` re-exports) is therefore also part of this crate's real public entry-point
surface, alongside `run()` and the re-exported items.

## Divergences

**One found, and it is real.** README's Configuration table and its separate Bounded
Everything table both state `BUZZ_AGENT_MAX_HISTORY_BYTES` defaults to `1048576`
(1 MiB) — but `config.rs`'s actual `parse_env("BUZZ_AGENT_MAX_HISTORY_BYTES", 16 *
1024 * 1024)` call defaults to 16 MiB, sixteen times larger than documented. This is
not a rounding artifact; it is a stale number in two places in the README against one
current number in the code. Per this crate's own AGENTS.md-inherited rule that
executable evidence outranks documentation for current behavior, the code's 16 MiB
default is the FACT this node records; the README is flagged as drifted rather than
silently corrected.

To check this was not a sign the whole Configuration table has rotted, a second
default (`BUZZ_AGENT_MAX_TOOL_RESULT_TEXT_BYTES`, 51200/50 KiB) was checked the same
way and found to match `config.rs`'s `DEFAULT_TOOL_RESULT_TEXT_BYTES` constant
exactly. The rest of the Configuration and Bounded Everything tables were not
individually re-verified against `config.rs` line by line beyond these two — see
*Scope and omissions* below.

No contradiction was found between the README's stated ACP method surface (the five
standard methods in its "ACP Transcript" section) and `lib.rs`'s actual dispatch: all
five are present, with matching names. `lib.rs`'s dispatch does carry one additional,
non-standard sixth arm (`_goose/unstable/session/steer`, see *Implementation
surface* above) that the README's ACP Transcript section does not mention — this is
an omission in an ACP-focused section documenting a non-ACP extension, not a
contradiction of anything the README claims. No divergence was found between the
README's "not networked MCP" claim and `mcp.rs`'s exclusive use of
`rmcp::transport::TokioChildProcess` (stdio only, no HTTP/SSE transport construction
found in the module).

## Verification

Automated, real-subprocess integration tests — not unit-test mocks. `cargo test -p
buzz-agent` runs the suite; `tests/common/mod.rs`'s `Harness` spawns the actual
compiled `buzz-agent` binary (`env!("CARGO_BIN_EXE_buzz-agent")`) as a real child
process and drives it over real stdio, `tests/fake_llm.rs` binds a real
`tokio::net::TcpListener` rather than mocking HTTP, and `tests/bin/fake_mcp.rs` is a
second real binary that simulates MCP-server fault paths via environment variables
(`FAKE_MCP_HANG_INIT`, `FAKE_MCP_TOOL_DELAY`, `FAKE_MCP_SPAWN_GRANDCHILD`). Per the
README's own framing, "regression tests are the changelog" — each test in
`tests/regressions.rs` is named for the bug it locks down. No CI-specific workflow
file dedicated to `buzz-agent` alone was found in this pass beyond the workspace-wide
`just ci`/`cargo test` gates and `sprig.yml`/`sprig-image.yml` (which build and
release the crate but do not themselves add test coverage).

## Relationships

- part-of: architecture-containers-agent-runtime
- references: (none — no test-strategy or verification-track corpus node exists yet
  to cite for the *Verification* section above)
- implements: (none — see *Target* above for why no edge is declared)

## Scope and omissions

**This node covers** what `buzz-agent` is responsible for as a crate: its public
entry points and library surface, its module-by-module implementation responsibility,
representative real-subprocess tests, one verified divergence between its own README
and its own code, and its place in the wider agent-runtime container.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full ACP wire protocol and per-provider LLM request/response shapes | `crates/buzz-agent/README.md` directly |
| The agent-runtime container's boundary, inbound/outbound interfaces, and its relationship to `buzz-acp`/`buzz-dev-mcp`/`sprig` | `launchpad/docs/corpus/architecture/containers/agent-runtime.md` |
| `buzz-acp`'s own harness responsibility (spawning this crate as a subprocess, routing relay events into it) | A future `implementation/crates/buzz-acp.md` node, not written by this task |
| `buzz-dev-mcp`'s own tool surface (the MCP server this crate's tool calls typically reach) | A future `implementation/crates/buzz-dev-mcp.md` node, not written by this task |
| `scripts/model-capabilities.json`'s full six-axis manifest contents | `src/model_capabilities.rs`'s own doc comment and the JSON file itself |
| The remaining ~25 environment variables in the README's Configuration and Bounded Everything tables not individually re-verified against `config.rs` beyond the two checked in *Divergences* | `crates/buzz-agent/src/config.rs`, `crates/buzz-agent/README.md` |
| Whether the `BUZZ_AGENT_MAX_HISTORY_BYTES` divergence found here is deliberate (a recent code change not yet reflected in the README) or accidental drift | Neither this node nor this task's git-history reading resolved intent; the divergence is recorded as a fact, not adjudicated |

**Expected but not verified when this node was written:**

- **Whether every one of the README's ~30 documented environment variables matches
  its actual `config.rs` default.** Two were spot-checked (one matched, one
  diverged); the rest were read in the README but not individually cross-checked
  against `parse_env` call sites line by line.
- **Whether `buzz-acp` (the harness) is the only real-world spawner of this binary in
  practice**, versus other ACP clients (Zed, JetBrains) spawning it directly. The
  README states ACP is a general client/agent protocol; this task did not verify
  which clients besides `buzz-acp` are exercised against `buzz-agent` in this
  repository's own tests or CI.
- **CI coverage specific to this crate beyond workspace-wide `just ci`.** No
  `buzz-agent`-specific GitHub Actions workflow (distinct from the `sprig`
  build/release workflows, which package rather than test it) was found in this
  pass; a targeted search of `.github/workflows/` for a per-crate test job was not
  performed.
