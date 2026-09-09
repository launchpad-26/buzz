---
id: platforms-cli-environment-injection
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "At the recorded revision, `architecture-containers-cli` is the only merged corpus node under `launchpad/docs/corpus/architecture/containers/`, and no `platforms/` subtree exists yet under `launchpad/docs/corpus/` on origin/launchpad."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, standards/**, schema/**, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844; no platforms/ entries"
  - statement: "`buzz-acp`'s `CliArgs` binds `--relay-url` to env `BUZZ_RELAY_URL` (default `ws://localhost:3000`) and `--private-key` to env `BUZZ_PRIVATE_KEY` (`hide_env_values = true`) via clap's `env =` attribute; there is no corresponding clap-bound field for `BUZZ_AUTH_TAG` on this struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:240-267"
  - statement: "`BUZZ_AUTH_TAG` is read directly from the process environment with `std::env::var(\"BUZZ_AUTH_TAG\")` at three separate call sites in `buzz-acp` (owner resolution from NIP-OA attestation, the relay membership-delegation tag, and `build_mcp_servers`), rather than through a clap-bound `Config` field."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:142-153"
      - "crates/buzz-acp/src/acp.rs:2001-2044"
      - "crates/buzz-acp/src/lib.rs:5099-5108"
  - statement: "`build_mcp_servers(config)` returns an empty `Vec<McpServer>` when `config.mcp_command` is empty; otherwise it returns exactly one `McpServer` whose `env` unconditionally includes `BUZZ_RELAY_URL` (`config.relay_url`) and `BUZZ_PRIVATE_KEY` (the configured secret key, bech32-encoded), and additionally includes `BUZZ_AUTH_TAG` and `BUZZ_ACP_DISPLAY_NAME` only when those are present as non-empty values in `buzz-acp`'s own process environment at build time."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5069-5124"
  - statement: "Unit tests in `build_mcp_servers_tests` (using a fixed `test_config()` with a non-empty `mcp_command`) assert: the built `McpServer` always carries `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY`; `BUZZ_AUTH_TAG` is present with the expected value when the process env var is set to a non-empty string; and `BUZZ_AUTH_TAG` is absent from `env` when the process env var is set to an empty string."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:6785-6890"
  - statement: "`McpServer`/`EnvVar` (defined in `acp.rs`) are documented in their own doc comment as \"An MCP server configuration passed to `session/new`\", stated to correspond to the `McpServerStdio` variant of the ACP schema, with all four `McpServer` fields (`name`, `command`, `args`, `env`) required by that schema even when `args`/`env` are empty arrays."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:25-42"
  - statement: "`build_mcp_servers(&config)`'s result is assigned once, at session-pool startup, to `PromptContext.mcp_servers`, which is later read at each new session rather than rebuilt per session."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:2193-2196"
  - statement: "Before each `session/new` call, `mcp_servers_with_git_origin` clones `ctx.mcp_servers` and appends one additional `EnvVar` to every server's `env`: `BUZZ_GIT_ORIGIN_CHANNEL_ID` when the channel type is `\"stream\"`, or `BUZZ_GIT_ORIGIN_AGENT_NAME` (from a non-empty agent/session-title name) for other channel types with a channel id present; neither is appended when no channel id is available."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:1367-1393"
  - statement: "The per-session `Vec<McpServer>` produced by `mcp_servers_with_git_origin` is passed directly into `agent.acp.session_new_full(...)`, which sends it to the freshly spawned agent process as part of the ACP `session/new` JSON-RPC request."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:1138-1158"
  - statement: "`AcpClient::spawn` launches the agent binary via `tokio::process::Command::new(command)` and, before calling `cmd.spawn()`, applies two more env layers in order: `crate::config::default_agent_env(command)` entries (added only if the key is absent from `buzz-acp`'s own process env, via `std::env::var_os(key).is_none()`), then `extra_env` (the caller-supplied `&[(String, String)]`, same operator-wins guard, with `CODEX_CONFIG` handled separately by `build_codex_config_env` when a generated Codex config is active)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:454-517"
  - statement: "`AcpClient::spawn`'s body contains no call to `Command::env_clear` anywhere before `cmd.spawn()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:454-537"
  - statement: "`default_agent_env(command)` returns `[(\"HERMES_ACP_SKIP_CONFIGURED_MCP\", \"1\")]` only when the normalized agent command identity is `hermes`, `hermes-agent`, or `hermes-acp`, and an empty slice for every other agent identity; its own doc comment explains the default exists to skip Hermes's normally-automatic startup of every profile-configured MCP server, which can otherwise exhaust the ACP host's startup budget."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:740-757"
  - statement: "`codex_network_env(agent_command, relay_url)` returns `Some((\"CODEX_CONFIG\", \"{\\\"sandbox_workspace_write\\\":{\\\"network_access\\\":true}}\"))` only for agent identities normalizing to `codex`/`codex-acp` and only when `relay_url` parses with a host; it returns `None` (skipping injection rather than widening the sandbox) for every other agent identity or an unparseable relay URL. Its own doc comment states the purpose: without it, Codex's macOS Seatbelt sandbox blocks the outbound network `buzz-cli` (running as an MCP subprocess) needs to reach the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:759-809"
  - statement: "`codex_network_env`'s result, when `Some`, is pushed into `persona_env_vars` during `Config` construction from CLI args, and `persona_env_vars` is passed as the `extra_env` argument at the call site that invokes `AcpClient::spawn` for a newly started agent."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:1076-1148"
      - "crates/buzz-acp/src/lib.rs:4646-4787"
  - statement: "Neither `default_agent_env` nor the `persona_env_vars` built at `Config` construction time (limited to the Codex network-access entry at this revision) sets `BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, or `BUZZ_AUTH_TAG` for the spawned agent binary; those three names are set only in the `session/new`-declared `McpServer.env` path described above."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:740-757"
      - "crates/buzz-acp/src/config.rs:1076-1148"
  - statement: "Given `AcpClient::spawn` never calls `env_clear`, and `std::process::Command` (which `tokio::process::Command` wraps) is documented to inherit the parent process's full environment by default, the spawned agent binary itself inherits `buzz-acp`'s own process environment — including `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` whenever `buzz-acp`'s own process carries them — as a second, passive path distinct from the explicit `McpServer.env` declaration."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:454-537"
      - "crates/buzz-acp/src/config.rs:740-757"
    confidence: 0.6
  - statement: "`CLAUDE.md` (this repository's root contributor guide) states that `BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, and `BUZZ_AUTH_TAG` are \"auto-injected by the ACP harness into managed agent subprocesses,\" and that in local development they must be set manually; this wording does not itself distinguish the explicit `McpServer.env` declaration from the passive environment-inheritance path, both of which this node documents separately."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "The merged `architecture-component` corpus template reasons that a node documenting one container's internal building blocks should set `type: architecture`, because `node.schema.json`'s `type` enum offers no member finer-grained than `architecture` to distinguish a component-level node from a container- or context-level one."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/architecture-component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
---

# buzz-cli / buzz-acp: environment injection component view

This node decomposes one facet of the `architecture-containers-cli` container
(`buzz-cli`): how `BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, and
the smaller related variables actually reach a `buzz-cli`/`buzz-dev-mcp`
process running inside an ACP-managed agent session. The container node
summarizes this in one paragraph plus one `INFERENCE`; this node answers the
question that summary leaves open: which concrete code paths set which
variables, in what order, and with what precedence, when `buzz-acp` (the ACP
harness, `crates/buzz-acp`) starts a managed agent.

## Notation legend

| Shape | Meaning |
|---|---|
| Rectangle inside "buzz-acp process" | A function/struct living inside `buzz-acp`'s own process |
| Rectangle outside that boundary | A different OS process (parent shell, spawned agent, spawned MCP server) |
| Solid arrow | An explicit environment assignment (`Command::env`, or a field written into a declarative `McpServer.env` payload) |
| Dashed arrow | Passive inheritance — no `env_clear` call removes it |

## Component diagram

```mermaid
flowchart LR
    subgraph ACP["buzz-acp process"]
        CliArgs["CliArgs (clap)\nBUZZ_RELAY_URL / BUZZ_PRIVATE_KEY"]
        Config["Config\nrelay_url, keys, persona_env_vars"]
        BuildMcp["build_mcp_servers()"]
        GitOrigin["mcp_servers_with_git_origin()"]
        SessionNew["session_new_full()\n(sends session/new)"]
        Spawn["AcpClient::spawn()\n(launches agent binary)"]
    end

    ParentEnv["Parent process environment\n(shell / launcher of buzz-acp)"]
    AgentProc["Agent subprocess\n(claude / codex / goose / hermes ...)"]
    McpProc["MCP server subprocess\n(buzz-dev-mcp, spawned by the agent/adapter)"]

    ParentEnv -->|"clap env= reads BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY"| CliArgs
    ParentEnv -->|"std::env::var(BUZZ_AUTH_TAG), read ambiently"| BuildMcp
    CliArgs --> Config
    Config --> BuildMcp
    BuildMcp -->|"McpServer.env: BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, +BUZZ_AUTH_TAG?, +BUZZ_ACP_DISPLAY_NAME?"| GitOrigin
    GitOrigin -->|"+ BUZZ_GIT_ORIGIN_CHANNEL_ID or _AGENT_NAME"| SessionNew
    SessionNew -->|"declares MCP servers over ACP session/new"| AgentProc
    AgentProc -->|"agent/adapter spawns using declared command/args/env"| McpProc
    Config -->|"persona_env_vars (CODEX_CONFIG, ...)"| Spawn
    Spawn -->|"Command::env: default_agent_env then extra_env, operator-wins"| AgentProc
    ParentEnv -.->|"no env_clear: full inheritance"| AgentProc
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| `CliArgs` env bindings | Read `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` from the process environment via clap's `env =` attribute into `buzz-acp`'s own `Config`. `BUZZ_AUTH_TAG` has no field here. | `clap::Parser` derive | `crates/buzz-acp/src/config.rs:240-267` |
| `build_mcp_servers` | Builds the one declarative `McpServer` entry (when `mcp_command` is configured): unconditional `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`, conditional `BUZZ_AUTH_TAG`/`BUZZ_ACP_DISPLAY_NAME` pass-through from `buzz-acp`'s own process env. | `fn(&Config) -> Vec<McpServer>` | `crates/buzz-acp/src/lib.rs:5069-5124`; tests `crates/buzz-acp/src/lib.rs:6785-6890` |
| `McpServer` / `EnvVar` | Typed, serializable payload shape carried in the ACP `session/new` request; documented as corresponding to the ACP schema's `McpServerStdio` variant. | `#[derive(serde::Serialize)]` structs | `crates/buzz-acp/src/acp.rs:25-42` |
| `mcp_servers_with_git_origin` | Per-session enrichment: appends a channel/agent-identifying env var to every declared MCP server immediately before each `session/new` call. | `fn(&[McpServer], Option<Uuid>, Option<&str>, Option<&str>) -> Vec<McpServer>` | `crates/buzz-acp/src/pool.rs:1367-1393` |
| `session_new_full` (`AcpClient`) | Sends the enriched MCP server list to the just-spawned agent process as part of the ACP `session/new` JSON-RPC request. | ACP JSON-RPC over the agent's stdio pipes | `crates/buzz-acp/src/pool.rs:1138-1158`; `crates/buzz-acp/src/acp.rs:692` |
| `AcpClient::spawn` | Launches the agent binary itself via `tokio::process::Command`, applying `default_agent_env` then `extra_env` with operator-wins precedence (skip if already set in `buzz-acp`'s own env); no `env_clear` call. | `tokio::process::Command` | `crates/buzz-acp/src/acp.rs:454-537` |
| `default_agent_env` / `codex_network_env` (`persona_env_vars`) | Per-runtime env defaults applied at spawn time: `HERMES_ACP_SKIP_CONFIGURED_MCP=1` for Hermes-family agents; `CODEX_CONFIG` (forces sandbox `network_access:true`) for Codex-family agents, derived from the configured relay URL. Neither sets any `BUZZ_*` credential. | `fn(&str) -> &'static [(&'static str, &'static str)]` / `fn(&str, &str) -> Option<(String, String)>` | `crates/buzz-acp/src/config.rs:740-809`, `:1076-1148` |

## Boundary

This node does not describe:

- `buzz-cli`'s own command surface, HTTP/WS transport, retry policy, or exit
  codes — see `architecture-containers-cli` for the container-level view, and
  the sibling `platforms/cli/*` tasks (command model, exit codes, output
  contract, authentication) for those facets specifically.
- External actors talking to the CLI, the relay, or the ACP harness — see the
  architecture-context nodes.
- Class/function-level design inside `buzz-acp` beyond what is needed to cite
  each building block's existence — an implementation-reference node's
  concern, if one is ever written for `buzz-acp`.
- Relay-side or `buzz-auth` handling of these credentials once they arrive at
  the relay (NIP-98 signing, NIP-OA attestation verification) — that is
  `buzz-cli`'s and the relay's own concern, only summarized (not decomposed)
  in `architecture-containers-cli`.
- Manual, non-ACP-managed developer setup of these same variables (`CLAUDE.md`
  documents that path separately as "in development, set... manually") — this
  node covers only the ACP-managed injection mechanism.

## Relationships

- part-of: architecture-containers-cli

## Scope and omissions

**This node covers** the concrete mechanism by which `buzz-acp` gets
`BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, and the smaller related
variables (`BUZZ_ACP_DISPLAY_NAME`, `BUZZ_GIT_ORIGIN_CHANNEL_ID` /
`BUZZ_GIT_ORIGIN_AGENT_NAME`, `CODEX_CONFIG`, `HERMES_ACP_SKIP_CONFIGURED_MCP`)
into a managed agent session: the declarative `McpServer.env` payload sent
over ACP `session/new`, the direct `Command::env` calls made on the spawned
agent binary itself, and the passive environment-inheritance path created by
never calling `env_clear`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-cli`'s own container-level responsibility, technology, and interfaces | `architecture-containers-cli` |
| `buzz-cli`'s command model, exit codes, output contract, authentication | Sibling `platforms/cli/*` tasks (#1236, #1238, #1239, #1235) |
| Whether the agent/adapter that receives `session/new` actually honors the declared `McpServer.env` and spawns `buzz-dev-mcp` with it | Not verified here — ACP-protocol behavior outside this repository (see below) |
| Relay-side authentication/authorization these credentials enable once used | `buzz-auth`, `buzz-relay` container nodes (not yet written) |
| `buzz-dev-mcp`'s own non-`buzz` personalities and their env needs | `buzz-dev-mcp`'s own container node (not yet written) |

**Expected but not verified when this node was written:**

- **Whether an ACP-managed agent subprocess actually receives
  `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` via environment inheritance from
  `buzz-acp`**, as opposed to only the explicit `McpServer.env` declaration
  this node confirmed as `FACT`. Confirmed only that no `env_clear` call
  removes that possibility (this node's `INFERENCE` entry); no live ACP
  session was run to observe the spawned child's actual environment. This
  mirrors the identical, still-open caveat already recorded on
  `architecture-containers-cli`.
- **Whether every ACP adapter (Claude, Codex, Goose, Hermes, ...) spawns its
  declared MCP servers using exactly the `command`/`args`/`env` given in
  `session/new`.** This node relies on `buzz-acp`'s own doc comment naming the
  ACP schema's `McpServerStdio` variant as the contract; no adapter's own
  source was read to confirm it honors that contract.
- **Whether `CLAUDE.md`'s summary wording is imprecise or describes a
  different code path than either mechanism found here.** Its single sentence
  ("auto-injected... into managed agent subprocesses") does not distinguish
  the two mechanisms this node separates; this was flagged rather than
  resolved with whoever last edited that document.
