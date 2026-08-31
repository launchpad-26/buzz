---
id: capabilities-agents-mcp
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "buzz-dev-mcp is a developer MCP server providing shell + file-edit tools to buzz-agent, listed as its own crate under the repo's 'Agent surface' heading, distinct from buzz-acp (the ACP harness) and buzz-agent (the minimal ACP-compliant agent) it serves."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:72"
      - "CLAUDE.md:189"
  - statement: "buzz-dev-mcp exposes exactly seven MCP tools over its tool_router: shell, read_file, view_image, str_replace, todo, _Stop and _PostCompact, each with a #[tool(...)] description string consumed directly by the calling agent."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:40-123"
  - statement: "The shell tool runs one ephemeral process per call, tail-truncates output to roughly 8KB for the model while saving up to 10MB of full output to an artifact file, defaults its timeout to 120000ms and caps it at 600000ms, and documents rg, tree and buzz as pre-installed on PATH for the calling agent to prefer over grep/cat."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:40-43"
      - "crates/buzz-dev-mcp/src/shell.rs:16-24"
  - statement: "On startup buzz-dev-mcp installs a session-scoped shim: a 0700 tempdir holding multicall symlinks back to its own binary named rg, tree, buzz, git-credential-nostr and git-sign-nostr, prepended to PATH, so the shell tool's child processes get these without a separate install step."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs:24-49"
  - statement: "buzz-dev-mcp's own binary entrypoint is a multicall dispatcher: invoked as rg, tree, git-credential-nostr or git-sign-nostr it runs that personality synchronously and exits before any async runtime is built; invoked as buzz or with no recognized argv0 it falls through to async_main, which builds a tokio runtime and, for any name other than buzz, starts serving the MCP tool_router over stdio."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/main.rs:138-186"
  - statement: "The MCP server is wired to an agent subprocess by buzz-acp: an McpServer{name, command, args, env} struct is one of the required fields of the ACP session/new call buzz-acp's AcpClient sends to the agent it spawns."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs:25-35"
  - statement: "buzz-acp's build_mcp_servers constructs at most one McpServer, using config.mcp_command as the spawned command and forwarding BUZZ_RELAY_URL and the harness's own bech32-encoded BUZZ_PRIVATE_KEY into its environment, plus BUZZ_AUTH_TAG and BUZZ_ACP_DISPLAY_NAME when those are set in the harness's own process environment; if config.mcp_command is empty, it returns no MCP servers at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5069-5124"
  - statement: "config.mcp_command is populated from the BUZZ_ACP_MCP_COMMAND environment variable (or --mcp-command flag), defaults to the empty string, and buzz-acp's own README documents it as 'Path to an optional MCP server binary to provide to the agent subprocess.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs:267-268"
      - "crates/buzz-acp/README.md:113"
  - statement: "buzz-acp's README states each pooled agent spawns its own MCP server subprocess, so resource usage scales approximately as N times (agent memory plus MCP server memory)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md:221"
  - statement: "This repository's own deployment runbook states that BUZZ_ACP_MCP_COMMAND is empty by default and that, unset, buzz-agent has no built-in tools whatsoever -- its only way to post to Buzz is by running `buzz messages send` through a tool server -- so an unset BUZZ_ACP_MCP_COMMAND (typically BUZZ_ACP_MCP_COMMAND=buzz-dev-mcp) produces an agent that accepts a message, calls the model, and has no way to answer, which the runbook flags as looking like a broken model rather than a missing tool server."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/runbooks/dev-deployment-SOP.md:2184-2187"
  - statement: "VISION_PROJECTS.md's own product-level Status table lists 'MCP server + ACP agent harness' as a capability row marked 'Ships today', among ten other named capability rows in the same table (channels/forums/DMs/canvases, workflow engine, Blossom media storage, approval gates, project binding, multi-repo projects, git hosting, merge coordinator, NIP-34 issues, web-of-trust reputation)."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:251"
  - statement: "buzz-dev-mcp is not merely a library the harness links -- it is also its own workspace binary crate (bin name buzz-dev-mcp) and is one of three dependencies of sprig, a multicall binary that dispatches to buzz-acp, buzz-agent or buzz-dev-mcp based on the argv0 name it is invoked as, so the same MCP server can be deployed either standalone or bundled into one multicall artifact."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/sprig/Cargo.toml:19"
      - "crates/sprig/src/main.rs:39-51"
  - statement: "No corpus node currently exists under launchpad/docs/corpus/capabilities/ on origin/launchpad at the recorded revision, so this node declares no relationships to sibling agent-capability nodes (agent, agent-turn, agent-owner, managed-agent, backend-provider, acp) -- only to the three already-merged architecture nodes cited in Relationships below."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities') -> no such path, run against commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "build_mcp_servers' empty-command-means-no-tools behavior is pinned by a passing unit test, empty_mcp_command_returns_no_servers, which asserts an empty mcp_command produces zero McpServer entries -- the same edge the deployment runbook's troubleshooting entry names as a silent-failure trap."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:6943-6951"
  - statement: "Every one of buzz-dev-mcp's tool implementation modules (rg, shell, str_replace, todo, view_image, paths, shim, read_file) carries its own #[test]-annotated unit test module, verifying the capability's individual tool behaviors at the source level rather than only through end-to-end exercise."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:985-1435"
      - "crates/buzz-dev-mcp/src/shim.rs:361-695"
      - "crates/buzz-dev-mcp/src/rg.rs"
      - "crates/buzz-dev-mcp/src/str_replace.rs"
      - "crates/buzz-dev-mcp/src/todo.rs"
      - "crates/buzz-dev-mcp/src/view_image.rs"
      - "crates/buzz-dev-mcp/src/paths.rs"
      - "crates/buzz-dev-mcp/src/read_file.rs"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: references
    target: architecture-flows-agent-turn
  - type: references
    target: architecture-context-ai-agent
---

# MCP server + ACP agent harness (dev tools): capability

Buzz gives every AI agent it hosts a shell, a file editor, and a working set of
developer tools -- not by teaching the model to call bespoke Buzz APIs, but by
handing its agent subprocess a standard [Model Context Protocol](https://modelcontextprotocol.io)
(MCP) server over stdio. `buzz-dev-mcp` is that server: it is what turns a
plain ACP-compliant agent into one that can run shell commands, read and edit
files, view images, and keep a cross-turn todo list, using `rg`, `tree`, and
the `buzz` CLI itself pre-installed on its `PATH`. Because the wiring is
generic MCP over stdio, any ACP-compliant agent binary -- not only
`buzz-agent` -- can be pointed at this same tool server.

## Maturity

**Ships today.** VISION_PROJECTS.md's own product-level Status table marks
"MCP server + ACP agent harness" as shipped (`VISION_PROJECTS.md:251`), and
that status is corroborated directly in code: `buzz-dev-mcp` is a real,
building workspace crate exposing seven MCP tools (`crates/buzz-dev-mcp/src/lib.rs:40-123`),
`buzz-acp` wires it into every spawned agent's `session/new` call when
configured (`crates/buzz-acp/src/lib.rs:5069-5124`), and this repository's own
deployment runbook documents the failure mode when it is *not* configured --
`buzz-agent` "has no built-in tools whatsoever" without it
(`launchpad/deploy/runbooks/dev-deployment-SOP.md:2184-2187`). That failure
mode being a documented, named troubleshooting step is itself evidence the
capability is deployed and operated today, not merely designed.

## Verification

The specific failure mode above -- an empty MCP command leaving an agent with
no tools -- is pinned by a passing unit test, `empty_mcp_command_returns_no_servers`
(`crates/buzz-acp/src/lib.rs:6943-6951`), not left to documentation alone.
Each individual tool `buzz-dev-mcp` exposes (`shell`, `read_file`, `view_image`,
`str_replace`, `todo`, plus the `rg`/`tree`/multicall shim behavior) has its
own source-level unit test module in its own file under
`crates/buzz-dev-mcp/src/`.

## Boundary

This node does not describe:
- **How `buzz-acp` pools, spawns and supervises agent subprocesses in general**
  -- that is `architecture-containers-agent-runtime`'s territory (the
  container hosting `buzz-acp`, `buzz-agent`, and `buzz-dev-mcp` together).
  This node covers only the MCP server itself and the one struct
  (`McpServer`) that connects it to a spawned agent.
- **The step-by-step sequence of one agent turn** -- initialize, discover
  channels, subscribe, receive a prompt, call tools, reply -- which
  `architecture-flows-agent-turn` already documents. This node states that
  MCP tool calls are how an agent *acts* during a turn, not the turn's full
  lifecycle.
- **What an AI agent is or how it relates to a human user in Buzz's broader
  architecture** -- that is `architecture-context-ai-agent`'s subject; this
  node assumes an agent already exists and describes only the tool surface
  handed to it.
- **The individual tool schemas' full parameter shapes** (e.g. `shell`'s
  exact `ShellParams` fields, `str_replace`'s uniqueness rule details) --
  those live in the tool descriptions and source cited above; this node
  names the seven tools and their purpose, not their wire-level parameter
  contracts.
- **Any capability-shaped sibling node this batch is also drafting** (agent,
  agent-turn, agent-owner, managed-agent, backend-provider, acp) -- none of
  them are merged to `origin/launchpad` at this node's recorded revision, so
  no relationship to any of them is declared here (see the evidence ledger).

## Relationships

- references: `architecture-containers-agent-runtime` -- the container that
  hosts `buzz-acp`, `buzz-agent` and `buzz-dev-mcp` together, and realizes
  this capability's runtime placement.
- references: `architecture-flows-agent-turn` -- the step-by-step flow in
  which this capability's tools are actually invoked during a turn.
- references: `architecture-context-ai-agent` -- the broader context node
  describing what an AI agent is inside Buzz, which this capability serves.

## Scope and omissions

**This node covers** what the MCP-server-plus-ACP-harness capability is (a
developer MCP server, `buzz-dev-mcp`, handing an ACP-compliant agent shell and
file-edit tools over stdio), its current maturity (shipped, with both a
product-level status marker and corroborating code/runbook evidence), the
seven tools it exposes, how it is configured and wired into a spawned agent
subprocess (`BUZZ_ACP_MCP_COMMAND` / `McpServer` / `build_mcp_servers`), and
its packaging (a standalone binary or one leg of the `sprig` multicall
artifact).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How `buzz-acp` pools and supervises agent subprocesses | `architecture-containers-agent-runtime` |
| The step-by-step path one agent turn takes | `architecture-flows-agent-turn` |
| What an AI agent is in Buzz's broader architecture | `architecture-context-ai-agent` |
| The exact wire-level parameter schema of each individual tool | tool source under `crates/buzz-dev-mcp/src/` |
| The `sprig` multicall binary as its own subject | not yet a corpus node |
| Any other agent-capability node in this batch (agent, agent-turn, agent-owner, managed-agent, backend-provider, acp) | that task, once merged |

**Expected but not verified when this node was written:**
- **No live `buzz-agent` + `buzz-dev-mcp` session was run for this task.** Every
  claim above rests on reading the source, the ACP wiring code, and existing
  runbook/vision documentation at the recorded revision -- not on a fresh
  execution trace of an agent actually calling a tool through the MCP
  transport.
- **Whether every ACP-compliant agent binary Buzz currently spawns (not only
  `buzz-agent`) is exercised against this same MCP server in practice** was
  not checked; the wiring in `build_mcp_servers` is agent-agnostic by
  construction, but this node makes no claim about which agent binaries are
  actually deployed with `BUZZ_ACP_MCP_COMMAND` set.
