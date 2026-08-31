---
id: platforms-agents-dev-mcp
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
  - statement: "crates/buzz-dev-mcp is a Rust workspace member with both a library target (`buzz_dev_mcp`, src/lib.rs) and a binary target (`buzz-dev-mcp`, src/main.rs), and src/main.rs's only job is to call buzz_dev_mcp::run()."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-dev-mcp/src/main.rs"
  - statement: "buzz-dev-mcp is a Model Context Protocol (MCP) server that runs over stdio and registers seven tools -- shell, read_file, view_image, str_replace, todo, _Stop, _PostCompact -- through an rmcp #[tool_router]/#[tool_handler] pair on a DevMcp struct, served via rmcp::ServiceExt::serve(stdio()) inside async_main."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "crates/buzz-dev-mcp/src/lib.rs carries no crate-level //! doc comment; its first lines are #![cfg_attr(...)] attributes followed directly by use statements and mod declarations, unlike some other crates in this repository that open lib.rs with a //! summary."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "The binary's run() function dispatches on argv[0]'s file stem before building a Tokio runtime: rg and tree run synchronously in-process via rg::run/tree::run, git-credential-nostr and git-sign-nostr delegate to those crates' own run() functions, and any other name -- including buzz-dev-mcp itself and buzz -- falls through to async_main, which special-cases buzz to call buzz_cli::run_from_args and otherwise starts the MCP stdio server."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "The shell tool (declared in src/lib.rs, implemented in src/shell.rs) runs an ephemeral shell command per call (bash by default, overridable via BUZZ_SHELL), tail-truncates the LLM-visible output to about 8KB while saving up to 10MB to an artifact file, and defaults timeout_ms to 120000ms capped at 600000ms."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs"
      - "crates/buzz-dev-mcp/src/shell.rs"
  - statement: "The read_file tool (src/read_file.rs) reads a text file and returns numbered lines in `{number}:{content}` format, accepting a required path plus optional 0-based offset, optional limit (default 2000), and optional workdir for relative-path resolution."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/read_file.rs"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "The view_image tool (src/view_image.rs) loads an image from a file path, http(s) URL, or data: URL and returns it as an MCP image content block, resizes to a default longest-edge of 1568px (overridable 64..=2048 via max_dim), rejects animated GIF/WebP, and caps source size at 20 MiB."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/view_image.rs"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "The str_replace tool (src/str_replace.rs) performs an atomic find-and-replace in a file, requiring old_str to match exactly once unless replace_all is set, and returns a unified diff."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "The todo tool and its _Stop/_PostCompact hook tools (src/todo.rs) maintain an in-memory, per-process session checklist of {text, done} items with no ids; _Stop returns objection text when items remain open (used by the agent's Stop lifecycle hook to advise against ending with incomplete work) and _PostCompact returns the full list state for re-injection after context compaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/todo.rs"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "crates/buzz-dev-mcp/Cargo.toml declares path dependencies on buzz-cli, git-credential-nostr and git-sign-nostr, workspace dependencies including buzz-core, nostr, rmcp, schemars, tokio, tokio-util, serde, serde_json, tracing, tracing-subscriber, rustls and reqwest, crate-pinned dependencies similar, tempfile, ignore, base64 and image, and a platform-specific dependency on nix (unix) or windows-sys (windows)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
  - statement: "crates/sprig declares a path dependency on buzz-dev-mcp, and sprig's src/main.rs dispatches to buzz_dev_mcp::run() for any argv0 personality other than buzz-acp, buzz-agent, and sprig itself, bundling the developer MCP server into Sprig's single multicall binary alongside its own rg/tree/buzz/git-credential-nostr/git-sign-nostr personality names."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml"
      - "crates/sprig/src/main.rs"
  - statement: "crates/buzz-backend-kubernetes/src/env.rs sets the BUZZ_ACP_MCP_COMMAND environment variable to the literal string buzz-dev-mcp when building an agent container's launch environment; buzz-acp's own config (crates/buzz-acp/src/config.rs) exposes BUZZ_ACP_MCP_COMMAND as an environment-configurable field (empty string by default) documented in crates/buzz-acp/README.md as 'Path to an optional MCP server binary to provide to the agent subprocess.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs"
      - "crates/buzz-acp/src/config.rs"
      - "crates/buzz-acp/README.md"
  - statement: "crates/buzz-agent/src/agent.rs's own test suite asserts that both dev__shell and buzz-dev-mcp__shell are recognized as shell-tool-shaped tool-call names, which is consistent with an MCP host prefixing a served tool's name with the MCP server's own configured name joined by a double underscore, though the prefixing behavior itself lives in the host/agent side, not in buzz-dev-mcp's own source."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-agent/src/agent.rs"
    confidence: 0.65
  - statement: "This repository's root AGENTS.md lists buzz-dev-mcp in its repo-structure table as 'Developer MCP server -- shell + file-edit tools' and states separately that buzz-dev-mcp (shell and file tools for buzz-agent) is a distinct surface from buzz-cli, where new agent-facing operations belong instead."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "At the checked revision, crates/buzz-dev-mcp has no tests/ integration-test directory; 8 of its 11 source files (read_file.rs, paths.rs, str_replace.rs, shim.rs, shell.rs, todo.rs, rg.rs, view_image.rs) contain inline #[cfg(test)] unit-test modules, while lib.rs, main.rs and tree.rs contain none."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='#[cfg(test)]|#[test]', scope='crates/buzz-dev-mcp/src/*.rs') -> nonzero matches in read_file.rs, paths.rs, str_replace.rs, shim.rs, shell.rs, todo.rs, rg.rs, view_image.rs; zero matches in lib.rs, main.rs, tree.rs, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "At the checked revision, crates/buzz-dev-mcp does not contain a README.md."
    entry_class: FACT
    evidence:
      - "find_crate_readme(crate='buzz-dev-mcp') -> no README.md found, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
---

# buzz-dev-mcp

`buzz-dev-mcp` (crate `crates/buzz-dev-mcp`, library name `buzz_dev_mcp`) is the
developer-tools Model Context Protocol (MCP) server that gives an agent subprocess
launched by `buzz-acp` a shell, file-editing, image-viewing and session-checklist
surface over stdio. This node answers: what does this one crate expose, what does
it depend on, and what else in the repository depends on it.

## Responsibility

`buzz-dev-mcp` runs as an MCP stdio server: it registers a fixed set of tools on a
`DevMcp` struct via `rmcp`'s `#[tool_router]`/`#[tool_handler]` macros and serves
them with `rmcp::ServiceExt::serve(stdio())`. Its binary is also a multicall
dispatcher — invoked under the names `rg`, `tree`, `git-credential-nostr`,
`git-sign-nostr` or `buzz`, it runs that personality instead of starting the MCP
server, so a single compiled artifact can stand in for several developer-tool
binaries.

`src/lib.rs` carries no crate-level `//!` doc comment stating this in prose; the
description above is drawn from reading the tool registrations and the multicall
dispatch in `run()`/`async_main()` directly, not from an authored summary. That
absence is recorded again in *Scope and omissions* below.

## Public interface

MCP tools registered on `DevMcp` (`src/lib.rs`):

| Tool | Kind | Contract | Evidence |
|---|---|---|---|
| `shell` | MCP tool (async fn) | Runs one shell command per call; bash by default, `BUZZ_SHELL` overrides; timeout defaults to 120000ms, capped at 600000ms; output tail-truncated to ~8KB, full output (up to 10MB) saved to an artifact file | `src/lib.rs`, `src/shell.rs` |
| `read_file` | MCP tool (async fn) | Returns a file's contents as numbered lines (`{number}:{content}`); `offset`/`limit` window into large files (default limit 2000); `workdir` resolves relative paths | `src/lib.rs`, `src/read_file.rs` |
| `view_image` | MCP tool (async fn) | Loads an image from a path/URL/`data:` URL and returns an MCP image content block; resizes to 1568px longest edge by default (`max_dim` 64..=2048); rejects animated GIF/WebP; 20 MiB source cap | `src/lib.rs`, `src/view_image.rs` |
| `str_replace` | MCP tool (async fn) | Atomic find-and-replace; `old_str` must match exactly once unless `replace_all`; returns a unified diff | `src/lib.rs`, `src/str_replace.rs` |
| `todo` | MCP tool (async fn) | Reads or replaces an in-memory `{text, done}` session checklist; omitting `todos` reads, providing the full list replaces it | `src/lib.rs`, `src/todo.rs` |
| `_Stop` | MCP tool (async fn, hook) | Returns open todo items as objection text; used by the agent's Stop lifecycle hook | `src/lib.rs`, `src/todo.rs` |
| `_PostCompact` | MCP tool (async fn, hook) | Returns the full todo state for re-injection after context compaction/handoff | `src/lib.rs`, `src/todo.rs` |

Multicall personalities dispatched from the same binary (`run()` in `src/lib.rs`),
not served as MCP tools:

| Personality | Behavior | Evidence |
|---|---|---|
| `rg` | Runs `rg::run`, preferring a system `rg` and falling back to a bundled implementation | `src/lib.rs`, `src/rg.rs` |
| `tree` | Runs `tree::run`, a directory-tree renderer | `src/lib.rs`, `src/tree.rs` |
| `git-credential-nostr` | Delegates to `git_credential_nostr::run()` | `src/lib.rs` |
| `git-sign-nostr` | Delegates to `git_sign_nostr::run()` | `src/lib.rs` |
| `buzz` | Delegates to `buzz_cli::run_from_args` inside `async_main` | `src/lib.rs` |

MCP tool names observed by an agent host are namespaced by the MCP server's own
configured name (for example `dev__shell` or `buzz-dev-mcp__shell`, per the
naming this crate's tool descriptions and `buzz-agent`'s own tests assume) — that
namespacing is applied by the host/agent side, not by code in this crate.

## Tests

`crates/buzz-dev-mcp` has no dedicated `tests/` integration-test directory.
Verification instead lives as inline `#[cfg(test)] mod tests` unit-test modules
next to the code they exercise, present in `src/read_file.rs`, `src/paths.rs`,
`src/str_replace.rs`, `src/shim.rs`, `src/shell.rs`, `src/todo.rs`, `src/rg.rs`
and `src/view_image.rs`; `src/lib.rs`, `src/main.rs` and `src/tree.rs` carry no
unit tests of their own.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-cli` (path dep) | The `buzz` multicall personality delegates to `buzz_cli::run_from_args` | `Cargo.toml` |
| `git-credential-nostr` (path dep) | The `git-credential-nostr` multicall personality delegates to it | `Cargo.toml` |
| `git-sign-nostr` (path dep) | The `git-sign-nostr` multicall personality delegates to it | `Cargo.toml` |
| `buzz-core` (workspace dep) | Core Nostr/event types shared across the workspace | `Cargo.toml` |
| `rmcp`, `schemars` (workspace deps) | MCP protocol implementation and JSON-schema generation for tool parameters | `Cargo.toml` |
| `nostr`, `zeroize` (workspace deps) | Nostr key handling and secret zeroing in `src/shim.rs` | `Cargo.toml` |
| `tokio`, `tokio-util` (workspace deps) | Async runtime and cancellation tokens for the shell/server loop | `Cargo.toml` |
| `rustls` (workspace dep, ring feature) | TLS provider installed at startup for HTTPS tool calls (e.g. `view_image` fetching a URL) | `Cargo.toml` |
| `reqwest`, `base64`, `image` (crate-pinned) | `view_image`'s HTTP fetch, base64 encoding, and image decode/resize | `Cargo.toml` |
| `similar`, `tempfile`, `ignore` | Unified diffs (`str_replace`), scratch directories (`shim`), and gitignore-aware directory walking (`tree`) | `Cargo.toml` |
| `nix` (unix) / `windows-sys` (windows) | Process-group signal delivery and Windows Job Object APIs for the shell tool's timeout-kill path | `Cargo.toml` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `sprig` (path dep) | `crates/sprig/src/main.rs` dispatches to `buzz_dev_mcp::run()` for every multicall personality name it does not handle itself, bundling this crate's binary and MCP server into Sprig's single artifact | `crates/sprig/Cargo.toml`, `crates/sprig/src/main.rs` |
| `buzz-acp` (spawned as a subprocess, not a Cargo dependency) | `buzz-acp` spawns the binary named by `BUZZ_ACP_MCP_COMMAND` as the agent subprocess's MCP server; `crates/buzz-backend-kubernetes/src/env.rs` sets that variable to the literal `buzz-dev-mcp` when constructing an agent container's launch environment | `crates/buzz-backend-kubernetes/src/env.rs`, `crates/buzz-acp/src/config.rs`, `crates/buzz-acp/README.md` |

No other crate in the workspace lists `buzz-dev-mcp` as a Cargo dependency.

## Boundary

This node does not describe:
- The `buzz-acp` harness's own responsibility for spawning and supervising the MCP
  server subprocess named by `BUZZ_ACP_MCP_COMMAND`, or the ACP protocol it speaks
  to the agent — that is `buzz-acp`'s own component, not this one.
- The `buzz-agent`/Sprig personalities that happen to share a binary artifact with
  `buzz-dev-mcp` under Sprig's multicall dispatch — those are separate components
  with their own responsibilities.
- Any container-level decomposition or diagram of an "agent runtime" container that
  `buzz-dev-mcp` might be one building block of; no `architecture-component` or
  `architecture-container` node for such a container exists in the corpus at this
  revision for this node to sit inside (see *Relationships*).
- Class/function-level design detail inside `buzz-dev-mcp`'s own modules (e.g. how
  `shell.rs` implements process-group timeout kill, or how `view_image.rs`
  transcodes images) beyond what is needed to state the public tool contract above.
- Install/usage instructions for a human running `buzz-dev-mcp` directly — no
  `crates/buzz-dev-mcp/README.md` exists at this revision (see *Scope and
  omissions*).

## Relationships

None declared. `buzz-dev-mcp` is depended on by `sprig` and is spawned as a
subprocess by `buzz-acp`, but neither `sprig` nor `buzz-acp` has a corpus node at
this revision (`launchpad/docs/corpus/platforms/` contains no other file yet), so
there is no existing node id for a `depends-on`/`references` edge to target. Per
`AGENTS.md`'s node-creation rule, a relationship target must already exist on the
branch being merged into — `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` at this revision lists only `AGENTS.md`, `README.md`,
`schema/**`, and the `standards/`/`templates/` documents already described above,
none of which this node's subject `depends-on`, `references`, or sits `part-of`.
The first `sprig`, `buzz-acp`, or agent-runtime `architecture-component` node to
merge is the natural moment to add the corresponding edge here.

## Scope and omissions

**This node covers** what `buzz-dev-mcp` is (an MCP stdio server plus a multicall
developer-tool dispatcher), its seven MCP tools and five multicall personalities,
its real build-time dependencies in both directions, and its explicit boundary
against the harness, sibling multicall personalities, and any not-yet-existing
container-level decomposition.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `buzz-acp` harness's subprocess-spawning and ACP-protocol behavior | A future component/implementation node for `buzz-acp`, not yet authored |
| The `buzz-agent` and `sprig` personalities sharing the same compiled binary | Their own future component nodes, not yet authored |
| Container-level decomposition of an "agent runtime" container, with diagram | A future `architecture-component`/`architecture-container` node, not yet authored under `launchpad/docs/corpus/platforms/` or `architecture/` |
| Class/function-level design inside `buzz-dev-mcp`'s modules | A future implementation-reference node, if one is ever authored for this crate |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No crate-level `//!` doc comment exists on `crates/buzz-dev-mcp/src/lib.rs`** to
  cite as an authored responsibility statement; the Responsibility section above is
  derived from reading the tool registrations and dispatch logic directly, not from
  prose the crate's own author wrote about it.
- **No `crates/buzz-dev-mcp/README.md` exists**, so no install/usage document could
  be cited or linked from *Boundary* above.
- **The exact MCP tool-name namespacing behavior (`<server-name>__<tool-name>`) is
  inferred from `buzz-agent`'s test assertions, not read from a specification or
  from `rmcp`'s own source** — it is recorded as an `INFERENCE` in the evidence
  ledger, not a `FACT`.
- **Whether any non-Cargo (e.g. build-script, CI, or documentation-only) dependency
  edge exists between `buzz-dev-mcp` and another component was not checked** — only
  `Cargo.toml` manifests were consulted, per this template's own evidence
  expectations.
