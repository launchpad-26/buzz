---
id: interfaces-mcp-file-edit-tool
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
  - statement: "Root AGENTS.md lists buzz-dev-mcp as the 'Developer MCP server — shell + file-edit tools' and separately states that buzz-dev-mcp holds 'shell + file tools for buzz-agent', distinct from buzz-cli and the ACP harness."
    entry_class: FACT
    evidence:
      - "AGENTS.md:72"
      - "AGENTS.md:189"
  - statement: "buzz-dev-mcp registers a tool named str_replace via the rmcp #[tool(...)] macro, with the description 'Atomic find-and-replace in a file. old_str must occur exactly once unless replace_all is true, in which case all occurrences are replaced. Returns a unified diff. Path resolved relative to workdir (defaults to server cwd). Prefer over sed/awk.', dispatching to str_replace::run."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:74-83"
  - statement: "StrReplaceParams is a serde::Deserialize + schemars::JsonSchema struct with fields path (String), old_str (String), new_str (String), replace_all (bool, defaults to false), and workdir (Option<String>)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:12-23"
  - statement: "run() rejects an empty old_str, and rejects old_str or new_str longer than MAX_INPUT_BYTES (1 MiB, 1024*1024 bytes) before doing any file I/O, both as invalid_params errors."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:9"
      - "crates/buzz-dev-mcp/src/str_replace.rs:26-37"
  - statement: "When old_str has zero matches, run() returns an invalid_params error containing the truncated old_str plus, when available, a nearest-line hint: the closest line (by character-level similarity > 0.6) within the first 200 lines of the file (HINT_SCAN_LINE_LIMIT)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:10"
      - "crates/buzz-dev-mcp/src/str_replace.rs:47-59"
      - "crates/buzz-dev-mcp/src/str_replace.rs:196-215"
  - statement: "Without replace_all, old_str matching more than one location is an invalid_params error asking for more surrounding context; count_occurrences_capped stops counting at 2 rather than scanning the whole file, since only 0 vs 1 vs >1 is needed."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:60-68"
      - "crates/buzz-dev-mcp/src/str_replace.rs:108-122"
  - statement: "With replace_all=true every occurrence of old_str is replaced (str::replace); without it, exactly the single occurrence is replaced (str::replacen with a count of 1)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:41-45"
      - "crates/buzz-dev-mcp/src/str_replace.rs:84-88"
  - statement: "Before writing, run() computes the projected post-replacement byte size and rejects the call with invalid_params if it would exceed MAX_FILE_BYTES (10 MiB, defined in paths.rs), without allocating the new content first."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:70-82"
      - "crates/buzz-dev-mcp/src/paths.rs:17"
  - statement: "The write is atomic: atomic_write creates a tempfile::NamedTempFile in the target's own parent directory, writes the full new content, flushes, and persists it over the target (a rename), and separately re-applies the original file's permissions afterward so the rename does not silently change the file's mode. A write failure is returned as an internal_error."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:90-95"
      - "crates/buzz-dev-mcp/src/str_replace.rs:124-138"
  - statement: "On success, run() returns a plain-text response naming the resolved target path and occurrence count, followed by a unified diff (3 lines of context) truncated with a '[diff truncated]' marker if it would exceed MAX_DIFF_BYTES (64 KiB)."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:96-105"
      - "crates/buzz-dev-mcp/src/str_replace.rs:140-155"
  - statement: "paths.rs's own module doc comment states resolve_path performs 'No containment enforcement — the resolved path may land anywhere on the filesystem (consistent with the shell tool's posture)', and resolve_path's implementation canonicalizes an absolute or workdir-joined path with no subsequent check that the result stays under the workspace root."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/paths.rs:1-7"
      - "crates/buzz-dev-mcp/src/paths.rs:44-54"
  - statement: "A committed test, run_allows_path_outside_workspace, targets a real file in a second tempdir genuinely outside the workspace root and confirms str_replace resolves and operates on it (asserting a 'not found' content error rather than any path-escape rejection); a second test in paths.rs, resolve_path_allows_outside_workspace, confirms the same posture through a symlink that resolves to a target outside the workspace directory."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:257-281"
      - "crates/buzz-dev-mcp/src/paths.rs:283-304"
  - statement: "When the str_replace call omits workdir, the effective workspace root is SharedState.cwd, which is set once at process startup from std::env::current_dir() — i.e. the buzz-dev-mcp server process's own working directory, not any per-call value supplied by the MCP client."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/paths.rs:197-205"
      - "crates/buzz-dev-mcp/src/lib.rs:179-181"
  - statement: "read_text_file rejects a target that is not a regular file, one whose size exceeds MAX_FILE_BYTES, or one that grows past MAX_FILE_BYTES while being read, each as invalid_params; it reports a stat failure, an open failure, a read failure, or non-UTF-8 content each as internal_error."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/paths.rs:210-274"
  - statement: "The root workspace Cargo.toml pins rmcp to version 1.1.0 with the server, transport-io and macros features, and crates/buzz-dev-mcp/Cargo.toml depends on it as a workspace dependency; buzz-dev-mcp's own lib.rs imports rmcp's ToolRouter, Parameters, CallToolResult, ServerCapabilities, ServerInfo, tool/tool_handler/tool_router macros, the stdio transport, ErrorData and ServerHandler directly."
    entry_class: FACT
    evidence:
      - "Cargo.toml:136"
      - "crates/buzz-dev-mcp/Cargo.toml:26"
      - "crates/buzz-dev-mcp/src/lib.rs:1-9"
  - statement: "buzz-dev-mcp serves the Model Context Protocol over stdio (DevMcp::new(state).serve(stdio())), and its ServerInfo reports its own name ('buzz-dev-mcp') and Cargo package version (env!(\"CARGO_PKG_VERSION\")) to the connecting client."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:126-136"
      - "crates/buzz-dev-mcp/src/lib.rs:183-185"
  - statement: "No source file under crates/buzz-dev-mcp or crates/buzz-agent/src/mcp.rs contains a protocol-version string or constant (protocol_version, protocolVersion or ProtocolVersion all return zero matches), so MCP protocol-version negotiation, if any, is handled entirely inside the rmcp crate rather than pinned or asserted anywhere in this repository's own code."
    entry_class: FACT
    evidence:
      - "grep_repo('protocol_version|protocolVersion|ProtocolVersion', paths='crates/buzz-dev-mcp/**,crates/buzz-agent/src/mcp.rs') -> zero matches, verified 2026-09-01 against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "An MCP tool's qualified name as seen by the agent is the server name and the bare tool name joined by a two-underscore separator (buzz-agent's SEP constant is \"__\"), matching the concrete example buzz-dev-mcp__shell used in buzz-agent's own test suite and in crates/buzz-agent/README.md's description of buzz-dev-mcp's shell tool; by the same rule the file-edit tool's qualified name is buzz-dev-mcp__str_replace."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shell.rs:19"
      - "crates/buzz-agent/src/agent.rs:1507"
      - "crates/buzz-agent/README.md:199"
  - statement: "rmcp's #[tool_router]/#[tool(...)] macros generate the MCP tool's advertised JSON input schema from each parameter struct's schemars::JsonSchema derive (StrReplaceParams derives it, and the crate is depended on with the \"macros\" feature specifically enabled), rather than from any hand-written schema document; this was reasoned from buzz-dev-mcp's own code and Cargo features, not from reading the rmcp crate's own source, which is not vendored in this checkout or cached under ~/.cargo."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:2-4"
      - "crates/buzz-dev-mcp/src/str_replace.rs:12-13"
      - "Cargo.toml:136"
    confidence: 0.75
  - statement: "A repeated, identical str_replace call is not idempotent in the general case: once a call without replace_all has succeeded, old_str is ordinarily no longer present at that location, so an identical second call takes the zero-match error path rather than silently repeating the edit; run() carries no idempotency key or before/after content check that would make repetition either a guaranteed no-op or a guaranteed re-application."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:39-68"
    confidence: 0.8
  - statement: "No lock, file-version check, or other concurrency guard is acquired anywhere between read_text_file's read and atomic_write's write inside run(), so two concurrent str_replace calls against the same path can race: the second call's occurrence count and replacement are computed against content read before the first call's write landed, and atomic_write's atomicity guarantees only that the write step itself does not tear, not that the read-then-write span is serialized against other writers."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-dev-mcp/src/str_replace.rs:25-95"
    confidence: 0.7
  - statement: "Issue #987's own Definition of Done requires this node to define inputs/messages, outputs/responses, error/rejection behavior, authentication/authorization, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative machine/spec representation, and at least one valid example and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#987 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# File-edit tool (`str_replace`): interface

This node documents the boundary between an MCP client that drives an AI coding
agent — currently `buzz-agent`, connecting as an MCP client over stdio — and the
`buzz-dev-mcp` server process's `str_replace` tool call, the atomic
find-and-replace file-editing capability of the "shell + file-edit tools" server
root `AGENTS.md` describes for `buzz-agent`. The two sides exchange one MCP
`tools/call` request carrying a JSON arguments object matching
`StrReplaceParams`'s schema, and one MCP tool result: either a plain-text success
message with a unified diff, or an MCP error.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `str_replace` (qualified as `buzz-dev-mcp__str_replace` when exposed to an agent) | `crates/buzz-dev-mcp/src/lib.rs:74-83` (tool registration) and `crates/buzz-dev-mcp/src/str_replace.rs` (`StrReplaceParams`, `run`) | Atomic find-and-replace of `old_str` with `new_str` in the file at `path`, requiring exactly one match unless `replace_all` is set; returns a unified diff of the write it performed. |

This node covers only `str_replace`. `buzz-dev-mcp` exposes several other tools
(`shell`, `read_file`, `view_image`, `todo`, and the `_Stop`/`_PostCompact`
hooks) registered in the same `lib.rs`; each is a distinct operation with its
own contract and belongs in its own corpus node rather than folded in here, per
`AGENTS.md`'s one-idea-per-node rule. `interfaces/mcp/shell-tool.md` (issue
#989) is the sibling node for `shell`, and `interfaces/mcp/protocol.md` (issue
#988) is the sibling node for the Model Context Protocol surface itself; both
are being authored in parallel and are not yet merged, so neither is named in
`relationships` here — only by filename, per this task's own instructions.

## Inputs

The MCP `tools/call` arguments object, deserialized as `StrReplaceParams`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | Resolved relative to `workdir` (or the server's own process `cwd` if `workdir` is omitted). No containment check — see *Contract and stability*. |
| `old_str` | string | yes | Must be non-empty and at most 1 MiB (`MAX_INPUT_BYTES`). |
| `new_str` | string | yes | May be empty (a pure deletion); at most 1 MiB. |
| `replace_all` | boolean | no, defaults `false` | `false` requires `old_str` to match exactly once; `true` replaces every match. |
| `workdir` | string or omitted | no | When omitted, defaults to the server process's own current directory (`SharedState.cwd`, fixed at process startup), not any client-declared default. |

The Rust `StrReplaceParams` struct (`crates/buzz-dev-mcp/src/str_replace.rs:12-23`)
derives `schemars::JsonSchema`, which `rmcp`'s tool macros use to advertise the
JSON input schema shown above to an MCP client — see *Link to the authoritative
representation*.

## Outputs

On success, a plain-text MCP result: `Replaced {N} occurrence(s) in {resolved
path}.` followed by a blank line and a unified diff (3 lines of context,
truncated at 64 KiB with a trailing `[diff truncated]` marker if the diff is
larger). See *Example: successful replacement* below.

## Error / rejection behavior

Every rejection is an MCP tool-call error built from `rmcp::ErrorData`, using
one of two constructors:

**`invalid_params`** (caller-fixable — bad arguments or file state):
- `old_str` is empty.
- `old_str` or `new_str` exceeds the 1 MiB (`MAX_INPUT_BYTES`) limit.
- `old_str` has zero matches in the file — the message includes the truncated
  `old_str` and, when a line elsewhere in the file is similar enough, a
  "nearest match" hint (see *Example: failed replacement*).
- `old_str` matches more than one location and `replace_all` is `false`.
- The projected post-replacement file size would exceed `MAX_FILE_BYTES` (10
  MiB).
- The resolved path is not accessible (propagated from path resolution), is
  not a regular file, already exceeds `MAX_FILE_BYTES`, or grew past that limit
  while being read.

**`internal_error`** (server/environment failure, not the caller's input):
- The resolved file cannot be stat'ed, opened, or read.
- The file's bytes are not valid UTF-8.
- The atomic write itself fails.

## Contract and stability

**Authorization boundary: none beyond the OS.** `paths.rs`'s own doc comment
states plainly that path resolution performs "No containment enforcement — the
resolved path may land anywhere on the filesystem," explicitly matching the
`shell` tool's posture, and a committed test
(`run_allows_path_outside_workspace`) exercises exactly this: a path outside
the workspace root resolves and is edited, not rejected. A second test
(`resolve_path_allows_outside_workspace`) confirms the same posture through a
symlink. The tool's only access boundary is therefore whatever OS-level file
permissions the `buzz-dev-mcp` process itself runs with — there is no
MCP-level authentication, capability token, or per-path allow-list in this
tool's own code. A caller able to reach this MCP server at all can ask it to
edit any file the host process account can write.

**Atomicity, not isolation.** Each write is atomic at the filesystem level
(`tempfile::NamedTempFile` in the target's own directory, then `persist`/rename,
with original permissions re-applied afterward), so a reader never observes a
half-written file. Nothing serializes the read-modify-write span against a
second concurrent caller: two simultaneous `str_replace` calls against the same
path can race, each computing its replacement against content read before the
other's write landed.

**Versioning.** There is no explicit versioning scheme for this tool's own
contract (no changelog, no version field in `StrReplaceParams`). What a caller
can observe is: the tool name `str_replace` and its schema-derived input shape
(changing either is effectively a breaking change for any client that has
cached the tool's schema); the server's own crate version, reported in
`ServerInfo` via `CARGO_PKG_VERSION`; and the pinned `rmcp` dependency version
(`1.1.0`) that governs the underlying MCP wire behavior. No protocol-version
string or constant appears anywhere in `buzz-dev-mcp`'s or `buzz-agent`'s MCP
client code, so protocol-version negotiation is handled entirely inside the
`rmcp` crate rather than asserted by this repository.

**Ordering / idempotency.** A single call is a single atomic write; there is no
batching or multi-file transaction. Repetition is not generally safe to assume
idempotent: once a non-`replace_all` call has succeeded, `old_str` is
ordinarily gone from that location, so an identical repeat call takes the
zero-match `invalid_params` path rather than silently repeating the edit. This
follows from reading `run()`'s logic (no idempotency key or generation check
exists), not from an explicit contract statement in the code.

## Boundary

This node does not describe:
- The Model Context Protocol itself, or how `buzz-dev-mcp` advertises tools,
  negotiates capabilities, or serves other tools over the same connection —
  that is `interfaces/mcp/protocol.md` (issue #988).
- The `shell` tool, or any other `buzz-dev-mcp` tool (`read_file`, `view_image`,
  `todo`, `_Stop`, `_PostCompact`) — each is a distinct operation with its own
  contract; `shell` specifically is `interfaces/mcp/shell-tool.md` (issue #989).
- A full parameter-by-parameter API reference for domain-expert readers beyond
  the table above — see `templates/interface.md`'s own boundary against
  `#1346`/`#1532` (reference / API-Reference depth, unresolved).
- Whether the no-containment posture is the *right* design for a file-edit
  tool. This node records the behavior as built and tested, not a verdict on
  it; changing it is implementation work with its own issue, not something a
  documentation task should silently paper over or silently endorse.

## Relationships

- **implements**: `corpus-template-interface` — this node is an instance of
  that template.
- No `references` or `part-of` edge is declared. The natural `references`
  targets — an event-kind node for any Buzz-specific wire format this tool
  might touch, or the sibling protocol/shell-tool nodes above — either do not
  apply (this tool touches no Nostr event kind at all) or are not yet merged
  (issues #988/#989), and `AGENTS.md`'s step 9 treats a target absent from the
  merge branch as a hard validation error to avoid, not a risk to accept.

## Link to the authoritative representation

There is no separate, hand-written specification document for this tool's wire
shape. The authoritative representation is the code itself:
- The tool's JSON input schema is generated at compile/registration time from
  `StrReplaceParams`'s `schemars::JsonSchema` derive by `rmcp`'s
  `#[tool_router]`/`#[tool(...)]` macros (`crates/buzz-dev-mcp/src/lib.rs:74-83`,
  `crates/buzz-dev-mcp/src/str_replace.rs:12-23`) — not restated by hand in this
  node, per this template's own evidence expectations.
- The wire protocol this tool is served over is the externally specified Model
  Context Protocol, implemented via the `rmcp` crate (pinned to `1.1.0` in the
  root `Cargo.toml`), not a Buzz-invented format.

## Example: successful replacement

Request arguments (JSON, as an MCP `tools/call` `arguments` object):

```json
{
  "path": "a.txt",
  "old_str": "beta",
  "new_str": "BETA",
  "replace_all": false,
  "workdir": "/workspace"
}
```

Given `a.txt` containing `alpha\nbeta\ngamma\n`, the tool result text is (from
the equivalent assertion in `run_basic_replace_emits_diff`,
`crates/buzz-dev-mcp/src/str_replace.rs:236-255`):

```
Replaced 1 occurrence in /workspace/a.txt.

--- a//workspace/a.txt
+++ b//workspace/a.txt
@@ -1,3 +1,3 @@
 alpha
-beta
+BETA
 gamma
```

## Example: failed replacement

Request arguments where `old_str` does not occur in the file (from
`run_replace_all_errors_on_zero_matches`, `crates/buzz-dev-mcp/src/str_replace.rs:321-337`):

```json
{
  "path": "nomatch.txt",
  "old_str": "xyz",
  "new_str": "abc",
  "replace_all": true,
  "workdir": "/workspace"
}
```

Given `nomatch.txt` containing `hello world\n`, the call returns an
`invalid_params` MCP error whose message is of the shape:

```
old_str not found in /workspace/nomatch.txt.
old_str (truncated): "xyz"
```

(a "Hint: nearest match around line N" line is appended when a sufficiently
similar line exists within the first 200 lines of the file — see
`nearest_line_hint`, `crates/buzz-dev-mcp/src/str_replace.rs:196-215`; there is
none here because `nomatch.txt`'s only line is dissimilar to `xyz`).

## Scope and omissions

**This node covers** the `str_replace` MCP tool exposed by `buzz-dev-mcp`: its
input arguments and their constraints, its output shape, its full set of
rejection paths and which error constructor each uses, its authorization
posture (explicitly no path containment, matching the `shell` tool), what
versioning signal exists today, its ordering/idempotency behavior, and where
its authoritative schema and wire protocol live in code rather than in this
document.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Model Context Protocol surface itself (capability negotiation, transport, serving multiple tools) | `interfaces/mcp/protocol.md` (issue #988, not yet merged) |
| The `shell` tool | `interfaces/mcp/shell-tool.md` (issue #989, not yet merged) |
| The `read_file`, `view_image`, and `todo`/`_Stop`/`_PostCompact` tools | Not yet filed as corpus nodes at the time this node was written |
| Field-by-field, domain-expert-depth API-parameter cataloguing beyond the input table above | `#1346`/`#1532` (reference / API-Reference depth, unresolved) |
| Whether the no-containment posture should change | A separate implementation issue, not filed by this documentation task |

**Expected but not verified when this node was written:**
- **`rmcp`'s own source was not read.** It is not vendored in this checkout and
  was not found under `~/.cargo` on this machine, so the claim that its tool
  macros derive the input schema from `schemars::JsonSchema` is recorded as an
  `INFERENCE`, not a `FACT`, reasoned from `buzz-dev-mcp`'s own code and
  declared Cargo features rather than from `rmcp`'s implementation directly.
- **The exact MCP JSON-RPC error shape `rmcp::ErrorData::invalid_params` and
  `::internal_error` produce on the wire was not inspected** — this node
  records which of the two constructors each rejection uses in
  `buzz-dev-mcp`'s own code, not the resulting wire-level error code or field
  names, which `rmcp` itself owns.
- **No live MCP client/server round trip was exercised while writing this
  node.** The request/response examples above are reconstructed from
  `buzz-dev-mcp`'s own committed unit tests (which call `str_replace::run`
  directly, not through a live stdio MCP connection), not captured from an
  actual `tools/call` exchange.
