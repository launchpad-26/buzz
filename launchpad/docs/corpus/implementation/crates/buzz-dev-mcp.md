---
id: implementation-crates-buzz-dev-mcp
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-dev-mcp's Cargo.toml names the package buzz-dev-mcp, a library crate buzz_dev_mcp (src/lib.rs) and a binary crate buzz-dev-mcp (src/main.rs), and declares path dependencies on buzz-cli, git-credential-nostr and git-sign-nostr alongside the rmcp (MCP SDK), schemars, similar, tempfile, ignore, tracing, rustls, reqwest, base64 and image crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
  - statement: "The crate's #[tool_router] impl on the DevMcp struct exposes exactly seven MCP tools: shell, read_file, view_image, str_replace, todo, and the two lifecycle hooks _Stop and _PostCompact; ServerHandler::get_info reports server name 'buzz-dev-mcp' and forwards SharedState::bootstrap_instructions as MCP server instructions."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:23-136"
  - statement: "main.rs is a two-line entry point that calls buzz_dev_mcp::run(); all multicall dispatch logic lives in lib.rs::run(), which inspects argv0's file stem and, before building any tokio runtime, dispatches the synchronous personalities rg, tree, git-credential-nostr and git-sign-nostr; any other name (including no match) falls through to a tokio current-thread runtime running async_main, which further dispatches 'buzz' to buzz_cli::run_from_args and anything else to MCP-server-over-stdio mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/main.rs"
      - "crates/buzz-dev-mcp/src/lib.rs:138-186"
  - statement: "buzz-agent (a separate crate) connects to buzz-dev-mcp as a subprocess, not as a linked library: crates/buzz-agent/src/mcp.rs spawns each configured MCP server (buzz-dev-mcp among them) via rmcp::transport::TokioChildProcess and speaks the MCP client protocol to it over stdio; buzz-dev-mcp has no crate dependency on buzz-agent and buzz-agent has no crate dependency on buzz-dev-mcp."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:1-122"
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-agent/Cargo.toml"
  - statement: "buzz-agent namespaces tool names as '<mcp-server-name>__<tool-name>' (SEP = \"__\" in crates/buzz-agent/src/mcp.rs), and its own tests exercise this directly against the server name 'buzz-dev-mcp' (e.g. is_reply_shaped(\"buzz-dev-mcp__shell\", ...) in crates/buzz-agent/src/agent.rs, and a McpServer test fixture with command: \"buzz-dev-mcp\" in crates/buzz-acp/src/pool.rs)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs:19"
      - "crates/buzz-agent/src/agent.rs:1504-1508"
      - "crates/buzz-acp/src/pool.rs:4920-4927"
  - statement: "buzz-acp's build_mcp_servers() only includes an MCP server in the ACP session/new call when Config.mcp_command (env BUZZ_ACP_MCP_COMMAND, default empty string) is non-empty; when set, it derives the server's advertised name from the command's file stem and forwards BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, and (when present in the harness's own process env) BUZZ_AUTH_TAG and BUZZ_ACP_DISPLAY_NAME as that server's env vars."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5069-5124"
      - "crates/buzz-acp/src/config.rs:266-267"
  - statement: "The Desktop app's managed-agents runtime table (desktop/src-tauri/src/managed_agents/discovery.rs) sets mcp_command: Some(\"buzz-dev-mcp\") for exactly two of its four known ACP runtimes — codex and buzz-agent — and mcp_command: None for goose and claude; buzz-agent's entry additionally sets mcp_hooks: true while codex's sets mcp_hooks: false."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/discovery.rs:93"
      - "desktop/src-tauri/src/managed_agents/discovery.rs:128-129"
      - "desktop/src-tauri/src/managed_agents/discovery.rs:161-162"
      - "desktop/src-tauri/src/managed_agents/discovery.rs:195-196"
  - statement: "desktop/src-tauri/tauri.conf.json bundles \"binaries/buzz-dev-mcp\" as an external sidecar binary, and .github/workflows/ci.yml cross-compiles buzz-dev-mcp alongside buzz-relay, buzz-acp, buzz-agent, git-credential-nostr and git-sign-nostr for release targets (lines 1093-1099) and creates a buzz-dev-mcp sidecar placeholder for the Windows Tauri compile-check job (line 1135)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:59"
      - ".github/workflows/ci.yml:1093-1099"
      - ".github/workflows/ci.yml:1135"
  - statement: "CI runs a dedicated 'Test (buzz-dev-mcp)' step on the Windows Rust job (cargo test -p buzz-dev-mcp --target $env:TARGET -- --test-threads=1), commented as gating the crate's Windows-only bash resolver and run single-threaded because its windows_resolver tests mutate process-global env vars (BUZZ_SHELL, GIT_BASH, SystemRoot) that SharedState::new reads."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:1142-1147"
  - statement: "buzz-dev-mcp is a member of the root Cargo workspace (unlike the Tauri desktop crate, which is excluded), so its inline #[cfg(test)] tests also run under a plain workspace-wide `cargo test` invocation, not only the dedicated Windows CI step."
    entry_class: FACT
    evidence:
      - "Cargo.toml:29"
  - statement: "Counting #[test] attributes directly in each source file gives 114 inline unit tests across the crate: paths.rs 13, read_file.rs 8, rg.rs 6, shell.rs 21, shim.rs 22, str_replace.rs 7, todo.rs 25, view_image.rs 12; lib.rs, main.rs and tree.rs carry none of their own."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/paths.rs"
      - "crates/buzz-dev-mcp/src/read_file.rs"
      - "crates/buzz-dev-mcp/src/rg.rs"
      - "crates/buzz-dev-mcp/src/shell.rs"
      - "crates/buzz-dev-mcp/src/shim.rs"
      - "crates/buzz-dev-mcp/src/str_replace.rs"
      - "crates/buzz-dev-mcp/src/todo.rs"
      - "crates/buzz-dev-mcp/src/view_image.rs"
  - statement: "paths.rs::resolve_path's own doc comment states it performs 'No containment enforcement — the resolved path may land anywhere on the filesystem (consistent with the shell tool's posture)'; this is pinned directly by tests named resolve_path_allows_outside_workspace (paths.rs) and run_allows_path_outside_workspace (str_replace.rs), so file-tool path resolution deliberately does not sandbox to a workdir."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/paths.rs:1-55"
      - "crates/buzz-dev-mcp/src/str_replace.rs"
  - statement: "shim.rs's Shim::install() creates an owner-only (0700) session tempdir, symlinks rg/tree/buzz/git-credential-nostr/git-sign-nostr back to the running binary and prepends that dir to PATH for shell children; when NOSTR_PRIVATE_KEY is set it writes an owner-only (0600) keyfile, derives ephemeral GIT_CONFIG_* env vars for nostr-based git auth/signing, then removes NOSTR_PRIVATE_KEY from its own process env and zeroizes the in-memory copy so child processes never see the raw secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs:1-75"
  - statement: "buzz-dev-mcp does not implement git identity/signing or NIP-98 git-credential exchange itself, nor buzz relay operations itself; those live in the separate git-sign-nostr, git-credential-nostr and buzz-cli crates respectively, which buzz-dev-mcp depends on and reaches via its multicall argv0 dispatch (git-credential-nostr, git-sign-nostr) or its shim-installed 'buzz' symlink dispatching to buzz_cli::run_from_args."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-dev-mcp/src/lib.rs:148-171"
      - "crates/buzz-dev-mcp/src/shim.rs:32-40"
  - statement: "buzz-dev-mcp has no README.md of its own, unlike buzz-acp, buzz-agent, buzz-cli, buzz-pairing-cli, git-credential-nostr and git-sign-nostr, which each ship one; its documented description lives instead in the repository root README.md and AGENTS.md."
    entry_class: FACT
    evidence:
      - "find(path='crates/buzz-dev-mcp', type='f') -> Cargo.toml, src/lib.rs, src/main.rs, src/paths.rs, src/read_file.rs, src/rg.rs, src/shell.rs, src/shim.rs, src/str_replace.rs, src/todo.rs, src/tree.rs, src/view_image.rs (no README.md among them)"
  - statement: "Root README.md describes buzz-dev-mcp in the 'Agent surface' line as '(shell + file-edit tools)', and root AGENTS.md's repo-structure comment and its 'Agent-facing operations go in buzz-cli' paragraph both describe it as 'shell + file tools for buzz-agent'; both descriptions predate (or at least omit) the todo/_Stop/_PostCompact session-checklist tools, the view_image tool, and the desktop-managed codex runtime pairing, none of which are 'shell' or 'file-edit' tools narrowly read, and the AGENTS.md phrase 'for buzz-agent' undercounts against the discovery.rs evidence above showing codex also gets mcp_command: Some(\"buzz-dev-mcp\")."
    entry_class: FACT
    evidence:
      - "README.md:230"
      - "AGENTS.md:72"
      - "AGENTS.md:189"
  - statement: "The Model Context Protocol (MCP) itself — the wire contract buzz-dev-mcp's binary realizes via the rmcp crate (rmcp::tool, rmcp::tool_router, rmcp::ServerHandler, rmcp::transport::stdio) — has no corpus node id at this revision, so no `implements` edge can be declared toward it without violating AGENTS.md's rule against inventing a relationship target that does not exist."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/** (no implementation/ subtree and no node documenting MCP itself) at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
    confidence: 0.9
  - statement: "architecture-containers-agent-runtime (launchpad/docs/corpus/architecture/containers/agent-runtime.md) is a merged corpus node on origin/launchpad that already documents buzz-dev-mcp as one of the three crates composing the agent-runtime container, and its own citations (crates/buzz-agent/src/mcp.rs, crates/buzz-acp/src/lib.rs and src/config.rs) independently corroborate the subprocess-over-stdio wiring re-verified directly in this node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "Issue #928's Definition of Done requires stating implementation responsibility and what it deliberately does not own, naming public interfaces/entry points and important dependencies, linking owned source paths and representative tests, and avoiding restating domain semantics already canonical in capability/layer/interface nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#928 (issue body, Definition of done)"
---

# buzz-dev-mcp: implementation reference

`crates/buzz-dev-mcp` is the developer MCP server that exposes shell execution,
file-editing, image-viewing and cross-turn session-checklist tools to an AI agent
process over the Model Context Protocol (MCP), realized via the third-party `rmcp`
crate. It is not linked into `buzz-agent` or any other agent-runtime crate; it is
built as a standalone binary and spoken to as a subprocess over stdio by whichever
MCP client configures it — conventionally `buzz-agent` (via `buzz-acp`'s
`BUZZ_ACP_MCP_COMMAND`) or, on the Desktop app, the `codex` and `buzz-agent`
runtime profiles in `managed_agents::discovery`.

## Target

The realized target is the **Model Context Protocol tool-server contract** — a
third-party specification, not a repository artifact — implemented through the
`rmcp` crate's server-side API: `#[tool_router]`/`#[tool]` macros build a
`ToolRouter<DevMcp>`, `#[tool_handler]` wires it into `ServerHandler`, and
`rmcp::transport::stdio()` serves the protocol over stdin/stdout
(`crates/buzz-dev-mcp/src/lib.rs:1-136`). At this revision, neither the MCP
specification itself nor an ADR/NIP describing buzz-dev-mcp's specific tool
contract has a corpus node id — a reader wanting the protocol's own definition
should consult the upstream MCP specification directly, and a reader wanting the
Buzz-specific consumer contract should read
`launchpad/docs/corpus/architecture/containers/agent-runtime.md`, which already
documents how the ACP harness and the Desktop app decide when to spawn this
server. No `implements` edge is declared here for that reason, per
`AGENTS.md`'s rule against inventing a target that carries no id.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-dev-mcp/src/lib.rs` — `DevMcp::{shell, read_file, view_image, str_replace, todo, stop_hook, post_compact_hook}` (`#[tool_router]` impl) | The seven-tool MCP surface: `shell`, `read_file`, `view_image`, `str_replace`, `todo`, `_Stop`, `_PostCompact` | `_Stop`/`_PostCompact` are internal lifecycle hooks, not general-purpose tools |
| `crates/buzz-dev-mcp/src/lib.rs` — `run()`, `async_main()` | Multicall argv0 dispatch (`rg`, `tree`, `git-credential-nostr`, `git-sign-nostr` synchronously; `buzz` and MCP-server mode asynchronously) | `main.rs` itself is a two-line call into `buzz_dev_mcp::run()` |
| `crates/buzz-dev-mcp/src/shell.rs` — `SharedState`, `shell::run` | The `shell` tool: ephemeral per-call process spawn, output tail-truncation with artifact spill, resolved-once shell discovery | 21 inline tests |
| `crates/buzz-dev-mcp/src/paths.rs` — `resolve_path`, `read_text_file` | Shared path resolution (MSYS translation, `~` expansion, canonicalization) for `read_file`/`str_replace`/`view_image` | Deliberately unsandboxed — see Divergences |
| `crates/buzz-dev-mcp/src/read_file.rs` | The `read_file` tool | 8 inline tests |
| `crates/buzz-dev-mcp/src/str_replace.rs` | The `str_replace` tool (atomic find/replace, unified diff) | 7 inline tests |
| `crates/buzz-dev-mcp/src/view_image.rs` | The `view_image` tool (path/URL/data-URL image loading, resize/transcode) | 12 inline tests |
| `crates/buzz-dev-mcp/src/todo.rs` — `TodoState` | The `todo` tool and the `_Stop`/`_PostCompact` hooks (in-memory, per-process session checklist) | 25 inline tests |
| `crates/buzz-dev-mcp/src/shim.rs` — `Shim::install` | Session-scoped multicall PATH shim plus ephemeral nostr-git identity setup for shell children | 22 inline tests |
| `crates/buzz-dev-mcp/src/rg.rs`, `src/tree.rs` | Multicall CLI personalities (`rg`, `tree`) reachable on the shim PATH from shell children — not MCP tools themselves | `rg.rs` 6 inline tests; `tree.rs` 0 |

## Divergences

Two divergences were found by checking the crate's actual tool surface and
consumer wiring against its own repository documentation, not merely restating
the documentation:

- **Root `README.md:230` and `AGENTS.md:72,189` both describe buzz-dev-mcp as
  "shell + file(-edit) tools [for buzz-agent]."** The crate's actual
  `#[tool_router]` surface also includes `view_image` (neither shell nor
  file-edit) and the `todo`/`_Stop`/`_PostCompact` session-checklist hooks
  (session state, not file or shell I/O) — a coverage gap in the short
  description, not a functional defect. "for buzz-agent" specifically
  undercounts: Desktop's `managed_agents::discovery` also pairs buzz-dev-mcp
  with the `codex` runtime (`mcp_command: Some("buzz-dev-mcp")`,
  `mcp_hooks: false`), so buzz-agent is not the only real consumer.
- **No sandboxing divergence, because none was ever documented as required.**
  `paths.rs`'s own doc comment is explicit that `resolve_path` performs no
  containment enforcement and a path may resolve anywhere on the filesystem;
  this matches the `shell` tool's own posture (arbitrary command execution) and
  is pinned by `resolve_path_allows_outside_workspace` and
  `run_allows_path_outside_workspace`. Checked against every other corpus
  node or ADR reachable from `AGENTS.md`'s own index for a stated sandboxing
  requirement — none was found — so this is documented, deliberate, and
  internally consistent rather than a divergence from an unmet target.

## Verification

Automated: 114 inline `#[cfg(test)]` unit tests across `paths.rs`, `read_file.rs`,
`rg.rs`, `shell.rs`, `shim.rs`, `str_replace.rs`, `todo.rs` and `view_image.rs`
(counted directly; `lib.rs`, `main.rs` and `tree.rs` carry none of their own).
Because the crate is a plain root-workspace member (not excluded the way the
Tauri desktop crate is), these run under a workspace-wide `cargo test` as part of
`just ci`'s Rust test step. CI additionally runs a crate-specific
`cargo test -p buzz-dev-mcp --target $env:TARGET -- --test-threads=1` step on the
Windows Rust job, single-threaded because its Windows bash-resolver tests mutate
process-global environment variables (`.github/workflows/ci.yml:1142-1147`), and
cross-compiles the crate's release binary for every shipping target alongside
`buzz-relay`, `buzz-acp`, `buzz-agent`, `git-credential-nostr` and `git-sign-nostr`
(`.github/workflows/ci.yml:1093-1099`). No integration test exercising the MCP
protocol surface end-to-end (a real client driving `shell`/`read_file`/etc. over
stdio) was found in this crate; `crates/buzz-agent/tests/regressions.rs` and
`crates/buzz-agent/src/agent.rs`'s unit tests exercise the *consumer* side
(tool-name namespacing, reply shaping) against a fixture, not a live
buzz-dev-mcp subprocess.

## Relationships

- part-of: architecture-containers-agent-runtime

No `implements` edge (see *Target* above — the MCP specification itself carries
no corpus node id at this revision). No `references` edge — no
`verification`-typed corpus node exists yet for this crate's test suite to point
at.

## Scope and omissions

**This node covers** what `crates/buzz-dev-mcp` is responsible for (the MCP tool
server binary: its seven-tool surface, its multicall CLI personalities, its
session-scoped shim and ephemeral git-identity setup), how it is actually reached
by an agent process (subprocess over stdio via `rmcp`, never a linked-library
call), its owned source paths and representative tests, and where its own
documentation undercounts its real surface and consumers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Git identity/event signing over Nostr | `git-sign-nostr` (separate crate, path dependency) |
| NIP-98 git-credential exchange for push/fetch auth | `git-credential-nostr` (separate crate, path dependency) |
| Buzz relay operations (`buzz` multicall personality: channels, messages, etc.) | `buzz-cli` (path dependency; buzz-dev-mcp only dispatches to it) |
| Deciding whether and how to spawn buzz-dev-mcp, session/new construction, MCP-server env-var forwarding | `buzz-acp` (`crates/buzz-acp/src/lib.rs::build_mcp_servers`) |
| The agent's LLM tool-calling loop, MCP client lifecycle, tool-name namespacing/reply-shape validation | `buzz-agent` (`crates/buzz-agent/src/mcp.rs`, `src/agent.rs`) |
| Per-runtime decision of which agents get buzz-dev-mcp wired in on Desktop | `desktop/src-tauri/src/managed_agents/discovery.rs` |
| The container-level architecture narrative (deployment topology, security implications of the agent runtime as a whole) | `architecture-containers-agent-runtime` (this node's `part-of` target) |
| The Model Context Protocol specification itself | not a corpus node at this revision |

**Expected but not verified when this node was written:**

- **No end-to-end integration test driving a real buzz-dev-mcp subprocess over
  MCP was found.** The crate's 114 tests are all unit-level (calling `run`/tool
  functions directly against in-process `SharedState`); whether any workspace
  test spawns the actual compiled binary and speaks MCP to it was not
  confirmed beyond `crates/buzz-agent/tests/regressions.rs`, which was opened
  but exercises consumer-side logic, not a live buzz-dev-mcp process.
- **Whether buzz-dev-mcp is the MCP server every real deployment configures**
  was not independently re-verified beyond the two Desktop runtime profiles
  (`codex`, `buzz-agent`) and buzz-acp's optional `BUZZ_ACP_MCP_COMMAND` —
  `architecture-containers-agent-runtime` names the same open question and it
  is not resolved here either.
- **Whether `rmcp` itself fully and correctly implements the MCP
  specification's normative requirements** is out of this node's scope; it is
  treated as the realization mechanism buzz-dev-mcp depends on, not
  independently audited.
