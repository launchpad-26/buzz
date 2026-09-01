---
id: interfaces-mcp-shell-tool
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "buzz-dev-mcp's tool_router registers a tool named `shell`, whose description states it runs a shell command (bash by default, overridable via `BUZZ_SHELL`), is an ephemeral process per call, tail-truncates output to ~8KB with full output (first 10MB) saved to an artifact file, defaults `timeout_ms` to 120000 and caps it at 600000, and lists `rg`, `tree` and `buzz` as available on PATH."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:40-50"
  - statement: "The tool's input parameters are exactly `command: String` (required), `workdir: Option<String>` (defaults to the server's own cwd) and `timeout_ms: Option<u64>` (defaults to 120000ms/2min, capped at 600000ms/10min), declared as `ShellParams` and derived into a JSON Schema via `schemars::JsonSchema`."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:119-128"
  - statement: "`run()` rejects a command longer than `MAX_COMMAND_BYTES` (1,000,000 bytes) with an `invalid_params` error before spawning anything, and rejects a `workdir` that does not exist or is not a directory the same way."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:135-159"
  - statement: "The resolved shell is computed once at `SharedState::new` (server startup) via `resolve_bash`, stored as `Result<(PathBuf, String), String>`, and every `run()` call reads that same stored resolution -- so the shell used to spawn a command is identical, call to call, to the one named in the server's bootstrap instructions. On Unix `resolve_bash` returns `bash` on PATH unless `BUZZ_SHELL` is set (absolute path must exist as a file; bare name is scanned on PATH); on Windows it probes `BUZZ_SHELL`, then `GIT_BASH`, then `bash.exe` on PATH (excluding System32 and the WindowsApps alias directory to avoid resolving WSL's launcher), then a Git-for-Windows install derived from `git.exe`, then standard Program Files locations, then the `GitForWindows` registry key, erroring with an actionable message if none is found."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:40-63"
      - "crates/buzz-dev-mcp/src/shell.rs:363-389"
  - statement: "The command string is passed to the resolved shell with a dialect-specific flag chosen by `shell_flag`: `-c` for bash/zsh/sh, `/C` for cmd.exe, `-Command` for powershell/pwsh."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:336-347"
  - statement: "The spawned child's stdin is `Stdio::null()`; stdout and stderr are captured separately via `read_capped`, which caps total retained bytes at `CAPTURE_CAP` (10 MiB) per stream while still counting `total_bytes` produced beyond that cap."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:175-177"
      - "crates/buzz-dev-mcp/src/shell.rs:867-892"
  - statement: "The JSON response body (returned as the tool result's single text content block) has the shape `{exit_code, stdout, stderr, timed_out, duration_ms, stdout_truncated, stderr_truncated, stdout_artifact, stderr_artifact, notes}`; `exit_code` is the child's real exit code, or 124 on timeout, or -1 if the exit status could not be determined."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:130-324"
  - statement: "`finalize_stream` truncates a stream's returned text when its captured size exceeds `MAX_BYTES` (50KB), its line count exceeds `MAX_LINES` (2000), or the 10MiB capture cap was hit; when truncated, it writes the full captured bytes (up to the 10MiB cap) to an artifact file under the session's `artifacts/` directory and returns only the last `TAIL_BYTES` (8KiB) of the stream, aligned to a UTF-8 character boundary, prefixed with a notice naming the artifact path and the discarded byte/line counts."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:894-957"
  - statement: "Artifact files are named `{call_id:06}.{stdout|stderr}.txt` under a per-session tempdir's `artifacts/` subdirectory, and a ring buffer (`rotate_artifacts`, capacity `ARTIFACT_RING_SIZE` = 8) deletes the oldest artifact file once more than 8 are held, so only the most recent 8 truncated stdout/stderr artifacts across a session survive at any time."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:971-982"
      - "crates/buzz-dev-mcp/src/shim.rs:355-359"
  - statement: "On timeout, `run()` sends SIGTERM to the whole process group, sleeps 200ms, then SIGKILL (`KillGroup::kill_graceful` on Unix); on cancellation (the MCP call's `CancellationToken` firing) it sends SIGKILL immediately (`kill_immediate`) with a bounded 1-second reap, returning a tool-error result with the text `\"cancelled\"` rather than the normal JSON body. On Windows the equivalent primitive is a Job Object created with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, terminated via `TerminateJobObject` with exit code 137 for both the graceful and immediate paths (a Job Object has no SIGTERM analogue)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:130-324"
      - "crates/buzz-dev-mcp/src/shell.rs:694-841"
  - statement: "`KillGroup`'s `Drop` implementation is a last-resort reaper: on Unix it re-sends SIGKILL to the process group; on Windows, closing the last handle to the Job Object triggers `KILL_ON_JOB_CLOSE`, killing anything still in it. Both are disarmed (`disarm()`) once the child has already been reaped explicitly, so the Drop-time kill is a safety net, not the normal path."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:694-841"
  - statement: "A spawn failure (the shell binary could not be executed) is returned as a tool-error `CallToolResult` with text `\"failed to spawn shell: {e}\"`, distinct from the `invalid_params` `ErrorData` returned for an oversized command or a missing/non-directory `workdir`, and distinct again from the normal-success JSON body returned even when the executed command itself exits non-zero."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:135-159"
      - "crates/buzz-dev-mcp/src/shell.rs:161-164"
      - "crates/buzz-dev-mcp/src/shell.rs:183-190"
  - statement: "`Shim::install` creates a 0700-permission per-session temp directory containing multicall symlinks (`rg`, `tree`, `buzz`, `git-credential-nostr`, `git-sign-nostr`) back to the `buzz-dev-mcp` binary itself, prepends that directory to a copy of the process `PATH`, and this shimmed `path_env` -- not the raw inherited `PATH` -- is what every spawned shell command actually receives via `cmd.env(\"PATH\", &state.shim.path_env)`."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs:24-76"
      - "crates/buzz-dev-mcp/src/shell.rs:169"
  - statement: "`Shim::install` reads `NOSTR_PRIVATE_KEY` from the process environment, writes it to a 0600 keyfile inside the shim directory if present and valid, builds ephemeral `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` env vars pointing git's nostr credential/signing helpers at that keyfile, and unconditionally removes `NOSTR_PRIVATE_KEY` from the process's own environment afterward -- so the raw key is never itself passed to a spawned shell command, only the keyfile path and the git config that references it."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs:24-76"
      - "crates/buzz-dev-mcp/src/shim.rs:170-171"
  - statement: "`BUZZ_PRIVATE_KEY` is, by contrast, intentionally inherited by every spawned shell command unmodified -- the code comment on the spawn call states this explicitly, because the `buzz` CLI (symlinked into the shim PATH) needs it to authenticate its own relay calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:170-171"
  - statement: "The MCP server process itself is spawned per agent session by `buzz-acp`'s `build_mcp_servers`, which constructs exactly one `McpServer{command: config.mcp_command, ...}` entry (a non-test call site; the crate's only other `McpServer{...}` constructions are in its own unit tests) with an `env` list always containing `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY` (the bech32-encoded session key), and conditionally `BUZZ_AUTH_TAG` (NIP-OA owner attestation, forwarded from the harness's own process env when non-empty) and `BUZZ_ACP_DISPLAY_NAME` (forwarded from the harness's own process env when non-empty)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:5069-5124"
  - statement: "Root AGENTS.md documents this same env-injection contract from the operator's side: \"Auth env vars (BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, BUZZ_AUTH_TAG) are auto-injected by the ACP harness into managed agent subprocesses. In development, set BUZZ_PRIVATE_KEY and BUZZ_RELAY_URL in your environment manually.\""
    entry_class: FACT
    evidence:
      - "AGENTS.md:203-206"
  - statement: "No authentication or authorization check of any kind exists inside `shell::run` itself, and no MCP-protocol-level auth/capability negotiation was found in `lib.rs`'s `ServerHandler`/`tool_router` wiring; the tool executes any `command` string it is given, for any caller able to speak MCP stdio to the process, with the OS-level privileges of the process itself. The only scoping mechanisms found are process-boundary ones: a fresh subprocess per MCP server (started once per agent session, not per tool call), the shimmed `PATH` and stripped `NOSTR_PRIVATE_KEY`/keyfile substitution described above, and the process's own filesystem/OS permissions -- there is no sandbox, container, or per-call permission gate inside the tool."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:130-324"
      - "crates/buzz-dev-mcp/src/lib.rs:126-136"
    confidence: 0.85
  - statement: "No MCP protocol version pin, tool schema version field, or any other versioning/compatibility marker for the `shell` tool's own contract was found anywhere in `buzz-dev-mcp` or its `Cargo.toml`; the crate carries only `version.workspace = true` (workspace version 0.1.0), which versions the compiled binary as a whole, not this tool's input/output schema specifically."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml:1-8"
  - statement: "buzz-dev-mcp depends on `rmcp` (workspace-pinned to version 1.1.0 with the `server`, `transport-io` and `macros` features), the Rust SDK for the externally specified Model Context Protocol, and derives the tool's JSON Schema from `ShellParams` via the `schemars` crate rather than hand-authoring or checking in a separate schema document -- so the authoritative machine-readable representation of the tool's input contract is the `ShellParams` struct definition itself, read live by any MCP client via the protocol's own `tools/list` capability."
    entry_class: FACT
    evidence:
      - "Cargo.toml:136"
      - "crates/buzz-dev-mcp/src/shell.rs:119-128"
  - statement: "Each `shell` tool call spawns an entirely independent ephemeral process with its own fresh stdout/stderr/exit-code, and nothing in `run()` sequences one call against another (no shared working state beyond the `SharedState`'s fixed `cwd`, the shim, and the monotonically incrementing `next_call_id` used only to name artifact files) -- so the interface offers no ordering or idempotency guarantee across calls, only within a single call's own process lifetime."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:130-324"
      - "crates/buzz-dev-mcp/src/shell.rs:65-72"
    confidence: 0.9
  - statement: "`basic_echo` is a passing unit test that calls `run()` with `command: \"echo hello\"`, no `workdir`, `timeout_ms: 5000`, and asserts `exit_code == 0`, `stdout == \"hello\\n\"`, `timed_out == false`."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:1005-1024"
  - statement: "`timeout_fires` is a unit test that calls `run()` with `command: \"sleep 5\"` and `timeout_ms: 150`, and asserts `timed_out == true` and `exit_code == 124`, exercising the timeout-kill path described above end to end."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:1026-1049"
  - statement: "Sibling MCP interface nodes for buzz-dev-mcp's MCP transport/protocol wiring (issue #987) and its file-edit (`str_replace`) tool (issue #988) are being authored in parallel worktrees at the time this node was written and are not merged, so this node does not declare `relationships` edges to them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#989 dispatching task instructions"
relationships:
  - type: implements
    target: corpus-template-interface
  - type: part-of
    target: architecture-containers-agent-runtime
---

# buzz-dev-mcp `shell` tool: interface

This node documents the `shell` tool exposed by `buzz-dev-mcp` (also reachable via the
`sprig` multicall binary) over the Model Context Protocol (MCP): an agent process
connected to `buzz-dev-mcp` as an MCP server invokes `tools/call` with tool name
`shell`, and the tool runs the given command string in a resolved system shell as an
ephemeral child process, returning a structured JSON result over the same MCP
tool-call response channel. The boundary is entirely local-process: both sides run on
the same host, connected over the MCP server's stdio transport, with no network hop
of the tool call itself.

## Operations

This interface exposes one operation.

| Operation | Defined in | Summary |
|---|---|---|
| `shell` tool call | `crates/buzz-dev-mcp/src/lib.rs` `DevMcp::shell` (`#[tool(name = "shell", ...)]`), delegating to `crates/buzz-dev-mcp/src/shell.rs` `run()` | Runs `command` in a resolved shell (`bash` by default; `BUZZ_SHELL` overrides), as one ephemeral child process, with an optional `workdir` and `timeout_ms`. |

**Inputs** (`ShellParams`, `crates/buzz-dev-mcp/src/shell.rs`):

| Field | Type | Default / cap |
|---|---|---|
| `command` | `String`, required | Rejected above `MAX_COMMAND_BYTES` (1,000,000 bytes) with `invalid_params`. |
| `workdir` | `Option<String>` | Defaults to the MCP server's own process `cwd`. Rejected with `invalid_params` if the path does not exist or is not a directory. |
| `timeout_ms` | `Option<u64>` | Defaults to `DEFAULT_TIMEOUT_MS` = 120000 (2 min); capped at `MAX_TIMEOUT_MS` = 600000 (10 min) via `.min()`, so a caller-supplied value above the cap is silently clamped, not rejected. |

**Outputs**: a single JSON text content block with the shape
`{exit_code, stdout, stderr, timed_out, duration_ms, stdout_truncated, stderr_truncated,
stdout_artifact, stderr_artifact, notes}`. `exit_code` is the real process exit code, or
`124` on timeout, or `-1` if the child's exit status could not be read at all.
`stdout`/`stderr` are UTF-8-lossy-decoded text (`String::from_utf8_lossy` fallback);
when a stream's captured bytes exceed `MAX_BYTES` (50 KB), its line count exceeds
`MAX_LINES` (2000), or the 10 MiB total capture cap (`CAPTURE_CAP`) was hit, the
returned text is replaced with a `[truncated: ...]` notice plus only the last
`TAIL_BYTES` (8 KiB) of that stream, and the full captured bytes (up to the 10 MiB cap)
are written to an artifact file under the session's `artifacts/` directory, named in
`stdout_artifact`/`stderr_artifact`. Artifacts rotate: only the most recent
`ARTIFACT_RING_SIZE` (8) truncated-stream artifacts across a session are kept before
the oldest is deleted (`rotate_artifacts`).

## Contract and stability

- **Ephemeral, one process per call.** Every `shell` tool call spawns a brand-new
  child process; there is no persistent shell session, so `cd` in one call does not
  affect a later call -- callers are told to pass `workdir` per call instead (this is
  stated directly in the tool's own bootstrap instructions, `build_bootstrap` in
  `shell.rs`).
- **Timeout is enforced, not advisory.** A command still running at `timeout_ms`
  is killed (process-group SIGTERM, 200ms grace, then SIGKILL on Unix; a Windows Job
  Object `TerminateJobObject` with no graceful/immediate distinction) and the response
  reports `timed_out: true`, `exit_code: 124`. Verified end to end by the
  `timeout_fires` unit test (`command: "sleep 5"`, `timeout_ms: 150"`).
- **Cancellation is distinct from timeout.** If the MCP call's own
  `CancellationToken` fires (caller-initiated cancellation, not a timeout), the tool
  returns a tool-error result with text `"cancelled"` instead of the normal JSON body,
  after an immediate process-group kill and a bounded 1-second reap.
- **Three distinct failure shapes**, not one: (1) `ErrorData::invalid_params` for an
  oversized `command` or a bad `workdir`, returned as a genuine MCP protocol error;
  (2) a tool-error `CallToolResult` with a plain-text message (`"failed to spawn
  shell: {e}"`, or the resolved-shell error message when no shell could be found, or
  `"cancelled"`) -- these are successful MCP responses carrying an error payload, not
  protocol-level errors; (3) the normal-success JSON body, returned even when the
  *executed command itself* exits non-zero -- a non-zero `exit_code` inside a
  successful tool response is the expected way command failure is reported, and is
  not conflated with tool-invocation failure.
- **Output is capped, never silently dropped without notice.** Any truncation is
  both signalled (`stdout_truncated`/`stderr_truncated: true`, a `[truncated: ...]`
  notice) and recoverable (an artifact file, while the rotation ring holds it).
- **Command dialect follows the resolved shell.** The command string is interpreted
  by whatever shell `resolve_bash` resolved (bash/zsh/sh with `-c`, `cmd.exe` with
  `/C`, powershell/pwsh with `-Command`), which is resolved once at server startup and
  reused for both the caller-facing bootstrap hint and every actual spawn -- so the
  dialect a caller is told to write in and the dialect actually executing are
  guaranteed to agree.
- **No tool-contract versioning found.** No MCP protocol version pin or per-tool
  schema version exists in this crate; only the crate's own `CARGO_PKG_VERSION`
  (workspace version, currently `0.1.0`), which versions the binary, not this
  operation's input/output shape. Treated as a gap, not resolved by inventing a
  scheme the code does not have.
- **No ordering or idempotency guarantee across calls.** Each call is an
  independent ephemeral process; the only shared state across calls in one session is
  the fixed server `cwd`, the installed shim, and a monotonically incrementing
  `next_call_id` used solely to name artifact files.

## Authentication and authorization

There is **no authentication or authorization check inside the `shell` tool itself** --
no caller identity check, no per-command allow/deny list, no MCP-level capability
negotiation gating this specific tool. The actual boundary is the OS process
boundary, established one layer up: `buzz-acp`'s `build_mcp_servers` spawns exactly
one `buzz-dev-mcp` process per agent session (over MCP stdio transport, not a network
socket), injecting `BUZZ_RELAY_URL` and a session-scoped `BUZZ_PRIVATE_KEY` (bech32
secret key) as environment variables, plus `BUZZ_AUTH_TAG` and
`BUZZ_ACP_DISPLAY_NAME` when the harness's own environment carries them. Root
`AGENTS.md` documents the same contract from the operator's side. Anyone able to speak
MCP stdio to that one spawned process can run any command string as the host OS user
running it -- the tool trusts the transport, not the caller.

What the process *does* narrow, deliberately, is credential exposure rather than
command execution: `Shim::install` writes any `NOSTR_PRIVATE_KEY` found in the
process's environment to a 0600 keyfile inside a 0700 per-session temp directory,
builds ephemeral `GIT_CONFIG_*` env vars pointing git's nostr credential/signing
helpers at that keyfile, and then unconditionally removes `NOSTR_PRIVATE_KEY` from the
process's own environment -- so a spawned shell command's environment never contains
the raw nostr key, only the keyfile path. `BUZZ_PRIVATE_KEY`, by contrast, is
intentionally inherited into every spawned command unmodified, because the shimmed
`buzz` CLI symlink needs it to authenticate its own relay calls. Every spawned command
also receives a shimmed `PATH` (the per-session tempdir prepended, containing
multicall symlinks for `rg`/`tree`/`buzz`/`git-credential-nostr`/`git-sign-nostr`)
rather than the raw inherited `PATH`. None of this constitutes a sandbox, container,
or capability restriction on what a command can do once it runs -- it narrows which
secrets a command's environment carries, not what the command is permitted to
execute.

## Boundary

This node does not describe:
- **buzz-dev-mcp's MCP transport/protocol wiring as a whole** (stdio server startup,
  `ServerHandler`/`tool_router` registration mechanics, the other five tools
  `read_file`/`view_image`/`str_replace`/`todo`/`_Stop`/`_PostCompact`) -- that is
  issue #987's node (`buzz-dev-mcp`'s MCP protocol surface), authored in parallel and
  not merged at the time this node was written, so no `relationships` edge names it.
- **The `str_replace` (file-edit) tool's own contract** -- issue #988's node, same
  parallel-authoring caveat.
- **A single Nostr event kind's wire contract.** This tool has no Nostr event-kind
  identity at all; it is a pure local MCP tool-call surface.
- **Field-by-field, domain-expert-depth parameter cataloguing** beyond what is above
  -- per `corpus-template-interface`'s own stated depth, this node is not a full API
  reference.
- **Windows-specific shell-resolution internals** beyond the cross-platform
  guarantee stated in *Contract and stability* -- `resolve_bash`'s registry/PATH
  probing order and `KillGroup`'s Job Object mechanics on Windows are implementation
  detail, cited by symbol above rather than restated field by field.

## Relationships

- `implements: corpus-template-interface` -- this node is a concrete instance of the
  interface template.
- `part-of: architecture-containers-agent-runtime` -- `buzz-dev-mcp` is one of the
  three crates the agent-runtime container node names as composing it.
- No `references` edge to a Nostr event-kind node: none applies (see *Boundary*).
- No edge to the sibling MCP interface nodes for issues #987 (protocol) or #988
  (file-edit tool): both are unmerged on `origin/launchpad` at the time this node was
  written, so neither is a valid `relationships` target; mentioned above by issue
  number and filename in prose instead.

## Scope and omissions

**This node covers** the `shell` MCP tool's input schema and defaults, its JSON
output shape and truncation/artifact behavior, its three distinct failure shapes,
its timeout/cancellation/kill semantics on both Unix and Windows, its authorization
boundary (process-level trust, not in-tool auth, plus the specific credential-scoping
the shim performs), the absence of any tool-contract versioning, its lack of an
ordering/idempotency guarantee across calls, a link to the authoritative schema
source (`ShellParams` in code, since no separate schema document exists), and one
passing (`basic_echo`) plus one failing (`timeout_fires`) example grounded in the
crate's own test module.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| buzz-dev-mcp's MCP protocol/transport surface as a whole, and its other five tools | Issue #987's node (unmerged at time of writing) |
| The `str_replace` file-edit tool's own contract | Issue #988's node (unmerged at time of writing) |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **No MCP protocol version or tool-schema version exists to verify against** --
  confirmed absent by inspection (see *Contract and stability*), not merely unchecked.
- **The Model Context Protocol's own specification document was not fetched or read
  directly.** This node describes the `shell` tool's contract from this repository's
  own code (the `rmcp` dependency, the `#[tool(...)]` macro registration) rather than
  from MCP's primary specification text.
- **Whether any MCP client enforces its own caller-side permission gate around
  invoking `shell`** (for example, a human-approval prompt in an agent harness) was
  not investigated -- this node describes only what `buzz-dev-mcp` itself enforces,
  which is nothing, at the tool level.
