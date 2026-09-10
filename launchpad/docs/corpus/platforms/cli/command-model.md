---
id: platforms-cli-command-model
type: implementation
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
  - statement: "buzz-cli's crate manifest names it 'Agent-first CLI for Buzz relay', producing library target buzz_cli and binary target buzz, and depends on clap version 4 with the derive and env features enabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml"
  - statement: "The buzz binary's entire main() is a single call into buzz_cli::run_from_args(std::env::args()), whose result is passed to std::process::exit; no argument parsing or dispatch logic lives in main.rs itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/main.rs"
  - statement: "run_from_args parses argv into a `Cli` struct via Cli::try_parse_from; a parse error that clap flags for stderr becomes CliError::Usage printed as JSON with exit code 1, while --help/--version (which clap marks for stdout, not stderr) are printed via clap's own e.print() and exit 0."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:24-61"
  - statement: "The top-level `Cli` struct is a clap derive(Parser) with four flags -- relay (env BUZZ_RELAY_URL, default http://localhost:3000), private_key (env BUZZ_PRIVATE_KEY, hide_env_values), auth_tag (env BUZZ_AUTH_TAG, hide_env_values), and format (value_enum OutputFormat, default \"json\") -- plus one #[command(subcommand)] field, `command: Cmd`, that holds the selected command group and its own arguments."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:63-99"
  - statement: "The `Cmd` enum (derive(Subcommand)) has exactly 22 variants, each itself a #[command(subcommand)] wrapping a per-group Cmd enum: Agents(AgentsCmd), Messages(MessagesCmd), Channels(ChannelsCmd), Canvas(CanvasCmd), Reactions(ReactionsCmd), Emoji(EmojiCmd), Dms(DmsCmd), Users(UsersCmd), Workflows(WorkflowsCmd), Feed(FeedCmd), Social(SocialCmd), Notes(NotesCmd), Repos(ReposCmd), Projects(ProjectsCmd), Patches(PatchesCmd), Issues(IssuesCmd), Pr(PrCmd), Media(MediaCmd), Upload(UploadCmd), Mem(MemCmd), Pack(PackCmd), Moderation(ModerationCmd) -- so the command tree is exactly two levels deep: `buzz <group> <subcommand> [flags]`, never three."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:175-243"
  - statement: "Each per-group Cmd enum (e.g. AgentsCmd, MessagesCmd, ChannelsCmd) is its own derive(Subcommand) declared in lib.rs, with per-variant #[arg(long, ...)] fields carrying clap constraints such as required_unless_present, conflicts_with, conflicts_with_all, value_enum, and default_value -- for example ChannelsCmd and MessagesCmd variants use required_unless_present/conflicts_with pairs to express mutually-exclusive input modes (e.g. an explicit channel/event pair versus a single --link deep link)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:371-533"
      - "crates/buzz-cli/src/lib.rs:484-505"
  - statement: "commands/mod.rs declares one Rust module per command group (agents, channel_templates, channels, dms, emoji, feed, issues, mem, messages, moderation, notes, pack, patches, pr, project_channel, projects, reactions, repos, social, upload, users, workflows) and holds only shared cross-group helpers -- with_git_provenance/apply_git_provenance (attaches ACP-harness-supplied channel or agent provenance to an event builder) and parse_write_response (maps a relay write response's 'duplicate'/'duplicate:*' message to CliError::Conflict) -- not per-group dispatch logic itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs"
  - statement: "18 of the 22 command groups expose a `pub async fn dispatch(cmd: crate::<Group>Cmd, client: &BuzzClient[, format: &crate::OutputFormat]) -> Result<(), CliError>` function in their own module (agents, channels, emoji, issues, messages, patches, reactions, notes, users, dms, social, feed, moderation, mem, pr, repos, projects, workflows); Media and Upload instead share `commands/upload.rs`'s two entry points, dispatch and dispatch_media; Canvas is dispatched by `commands::channels::dispatch_canvas`, a second function in the channels module rather than its own file; Pack has no `dispatch` at all -- its two subcommands are called directly from `run()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:12"
      - "crates/buzz-cli/src/commands/channels.rs:1473"
      - "crates/buzz-cli/src/commands/channels.rs:1578"
      - "crates/buzz-cli/src/commands/upload.rs:4"
      - "crates/buzz-cli/src/commands/upload.rs:17"
      - "crates/buzz-cli/src/lib.rs:2051-2122"
  - statement: "run() special-cases Cmd::Pack before any authentication: PackCmd::Validate and PackCmd::Inspect are dispatched directly to commands::pack::cmd_validate/cmd_inspect and the function returns without constructing a BuzzClient or requiring BUZZ_PRIVATE_KEY, matching the crate's own long_about text that 'the pack subcommand runs locally and does not require a relay connection.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2054-2060"
      - "crates/buzz-cli/src/lib.rs:67-75"
  - statement: "For every other command group, run() requires cli.private_key (erroring CliError::Auth if absent), parses it into a Keys pair, optionally normalizes/parses/verifies a NIP-OA cli.auth_tag via buzz_sdk::nip_oa, constructs one BuzzClient, and then matches cli.command against the 21 remaining Cmd variants, forwarding to each group's dispatch(sub, &client[, &cli.format]) function; Cmd::Pack is unreachable at this point (already handled above)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2051-2123"
  - statement: "Of the 21 non-Pack groups, exactly 5 dispatch functions accept the global `&cli.format: &OutputFormat` parameter: Messages, Channels, Users, Feed, and Moderation. The remaining 16 (Agents, Canvas, Reactions, Emoji, Dms, Workflows, Social, Notes, Repos, Projects, Patches, Issues, Pr, Media, Upload, Mem) take no format parameter at all and always emit the same (full) JSON shape regardless of the --format flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2100-2120"
  - statement: "Of the 5 dispatch functions that accept a format parameter, Moderation's is named `_format` (Rust's unused-binding convention) and is never referenced anywhere else in moderation.rs -- confirmed by grepping the file for 'format' and finding no OutputFormat match arm -- so `buzz moderation` accepts --format but silently ignores it; only Messages, Channels, Users, and Feed actually branch on OutputFormat::Compact to reduce their output."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs:133-140"
      - "grep_repo(pattern='format', scope='crates/buzz-cli/src/commands/moderation.rs') -> only `format!()` string-formatting macro calls and one `_format: &OutputFormat` parameter, no OutputFormat match"
  - statement: "The compact-mode transform is not a single shared function: messages.rs, feed.rs, channels.rs, and users.rs each define their own local logic that matches on OutputFormat::Compact versus OutputFormat::Json, rather than calling one common helper in commands/mod.rs. messages.rs's own `format_events` is representative: for OutputFormat::Compact it re-parses the normalized JSON array and rebuilds each element as {id, content, created_at} only, dropping every other field; for OutputFormat::Json it returns the normalized string unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs:335-354"
      - "crates/buzz-cli/src/commands/channels.rs:100"
      - "crates/buzz-cli/src/commands/users.rs:71"
      - "crates/buzz-cli/src/commands/users.rs:333"
      - "crates/buzz-cli/src/commands/feed.rs:8-10"
  - statement: "`buzz pack inspect` takes its own per-subcommand `format: PackInspectFormat` argument (a distinct clap ValueEnum declared and used only for that one subcommand), separate from and unrelated to the global `--format` (OutputFormat) flag on the root Cli struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1897"
      - "crates/buzz-cli/src/lib.rs:1910"
      - "crates/buzz-cli/src/commands/pack.rs:8"
  - statement: "CliError (thiserror derive) has 8 variants -- Usage, Relay{status,body}, Network, Auth, Key, Conflict, NotFound, DeliveryUnknown, Other -- and exit_code() maps them to fixed process exit codes: Usage/NotFound=1, Relay (401/403)=3 else 2, Network=2, Auth=3, Key=3, Conflict=5, DeliveryUnknown=2, Other=4; print_error() serializes every non-success outcome as one JSON object on stderr, {\"error\": <category>, \"message\": <text>, \"retryable\": <bool>}, with retryability decided by is_retryable_error (network connect/timeout/request/body/decode errors and relay 429/502/503/504 are retryable; DeliveryUnknown is explicitly never retryable)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs:1-136"
  - statement: "A unit test, `cli_definition_is_valid`, calls `Cli::command().debug_assert()` -- clap's own self-consistency check (duplicate flag names, conflicting arg groups, and similar definition errors panic here) -- as the only automated verification of the command tree's structural validity; no test enumerates or asserts the full list of 22 groups or their per-group flag sets."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2176-2179"
  - statement: "src/validate.rs provides shared input-validation helpers (parse_event_id, parse_uuid, validate_uuid, validate_hex64, validate_repo_id, and others) that command handlers call on raw string arguments before building a request, each mapping a malformed value to CliError::Usage rather than a panic or a relay round-trip."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/validate.rs:1-40"
  - statement: "The already-merged architecture-containers-cli node documents buzz-cli at the whole-container level (responsibility, technology, inbound/outbound interfaces, deployment/security implications) and explicitly defers 'full per-subcommand behavior (22 command groups, crates/buzz-cli/src/commands/*.rs)' to 'implementation-reference nodes for individual capabilities, not this container-level node' -- this command-model node is scoped narrower still, to the shape of the command tree and its dispatch mechanism, not any one group's business logic."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
---

# Command model: `buzz-cli`

`buzz-cli`'s command surface -- the two-level `buzz <group> <subcommand>
[flags]` tree, how it is declared with `clap`, and how a parsed command
reaches its handler -- documented as one standalone component inside the
`buzz-cli` container (see `architecture-containers-cli.md` for the container
as a whole). This node answers: what shape does the command tree have, how
is a flag or subcommand added to it, and what happens between "argv parsed"
and "a group's handler runs"?

## Responsibility

`buzz-cli`'s command model is responsible for turning `argv` into one of 22
typed command-group values plus their group-specific arguments, then routing
that value to exactly one dispatch function per group. It owns argument
declaration (`clap`'s derive macros on the `Cli` struct and each per-group
`*Cmd` enum), the environment-variable fallback for the three connection
flags, the single global `--format` flag, and the `run()` match that decides
which module handles a parsed command. It is deliberately thin: dispatch
functions receive an already-authenticated `BuzzClient` and, in five of 21
non-`Pack` cases, the caller's requested `OutputFormat` -- everything past
that point (request shaping, relay calls, output rendering) is each command
group's own responsibility, not the command model's.

`main.rs` itself carries none of this: its entire body is one call into
`buzz_cli::run_from_args`, so the command model lives wholly inside the
library crate and not in the binary's own entry point.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `run_from_args<I, S>(args: I) -> i32` | async fn | Parses `argv`, dispatches, returns a process exit code; the sole entry point `main.rs` calls. | `crates/buzz-cli/src/lib.rs:24-61` |
| `Cli` | struct (`derive(Parser)`) | Root argument set: `relay`, `private_key`, `auth_tag`, `format`, and the `command: Cmd` subcommand field. | `crates/buzz-cli/src/lib.rs:63-99` |
| `Cmd` | enum (`derive(Subcommand)`) | 22 variants, one per command group, each wrapping that group's own `*Cmd` enum. | `crates/buzz-cli/src/lib.rs:175-243` |
| `OutputFormat` | enum (`derive(ValueEnum)`) | `Json` (default) or `Compact`; the value of the global `--format` flag. | `crates/buzz-cli/src/lib.rs:163-173` |
| `run(cli: Cli) -> Result<(), CliError>` | async fn (private) | Authenticates (except for `Pack`), builds one `BuzzClient`, matches `cli.command` to one of 21 group `dispatch` calls. | `crates/buzz-cli/src/lib.rs:2051-2123` |
| `commands::<group>::dispatch(...)` | async fn, per group | Group-specific handler entry point; 18 groups have exactly this signature (`cmd`, `client`[, `format`]); `Canvas`/`Media` share a second function in a sibling module, `Pack` has none. | `crates/buzz-cli/src/commands/{agents,channels,...}.rs` (see evidence ledger) |
| `error::exit_code(&CliError) -> i32` / `error::print_error(&CliError)` | fn | Maps the 8 `CliError` variants to a process exit code and a single stderr JSON error object. | `crates/buzz-cli/src/error.rs:1-136` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `clap` (v4, `derive` + `env` features) | Declares the entire `Cli`/`Cmd`/per-group enum tree and its `--help`/env-var-fallback behavior. | `crates/buzz-cli/Cargo.toml` |
| `crate::client::BuzzClient` | Constructed once in `run()` and passed by reference into every non-`Pack` dispatch call; the command model does not itself talk to the relay. | `crates/buzz-cli/src/lib.rs:2097-2120` |
| `crate::error::CliError` | The `Result` error type every dispatch function returns; `run_from_args` maps it to an exit code and JSON stderr output. | `crates/buzz-cli/src/error.rs` |
| `crate::validate` | Shared input-validation helpers (`parse_uuid`, `validate_hex64`, ...) command handlers call before building requests. | `crates/buzz-cli/src/validate.rs:1-40` |
| `buzz_sdk::nip_oa` | Parses and verifies the optional NIP-OA `auth_tag` before it is attached to the constructed `BuzzClient`. | `crates/buzz-cli/src/lib.rs:2077-2095` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `buzz` binary (`crates/buzz-cli/src/main.rs`) | Its entire body is `buzz_cli::run_from_args(std::env::args())`. | `crates/buzz-cli/src/main.rs` |
| `buzz-dev-mcp` | Depends on `buzz-cli` as a library and, under its `buzz` multicall personality, calls `buzz_cli::run_from_args` directly rather than shelling out -- reusing this exact command model in-process. | `crates/buzz-cli/Cargo.toml` (crate name `buzz_cli`, cited via the already-merged `architecture-containers-cli` node's own `buzz-dev-mcp/Cargo.toml` and `buzz-dev-mcp/src/lib.rs` citations) |

## Boundary

This node does not describe:
- The whole `buzz-cli` container's responsibility, technology stack,
  inbound/outbound interfaces, or deployment/security posture -- see
  `architecture-containers-cli.md`, which already covers those and
  explicitly defers per-group behavior to component/implementation-level
  nodes such as this one.
- Any single command group's business logic (event construction, relay
  paths called, retry behavior) -- that is `client.rs`'s and each
  `commands/*.rs` module's own concern, not the shape of the command tree.
- Authentication mechanics (how `BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` are
  verified and signed into requests) -- `platforms/cli/authentication.md`
  (issue #1235, not yet written at this revision) owns that; this node only
  notes that `run()` performs that step before dispatch.
- Install/usage instructions for a human running `buzz` -- see
  `crates/buzz-cli/README.md`, which the container node already flags as a
  partially stale command inventory; this node relies on the source
  (`lib.rs`), not the README, for the command list.

## Relationships

None declared. `architecture-containers-cli` is the one existing node this
subject is conceptually closest to, but it is a different `type`
(`architecture`, documenting the whole container) and no `part-of`/
`depends-on`/`references` direction in `relationships.schema.json` fits
"this component is scoped narrower than that container node" without
inventing a relationship the schema does not define for it. No other
`platforms/**` node is merged on `origin/launchpad` at this revision
(confirmed via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) for this node to sit `part-of` or `depends-on`. A
future `architecture-component` node decomposing the `cli` container (once
that template and an instance exist) is the natural place to add a
`part-of` edge from this node, per `component.md`'s own guidance that such
an edge is optional and normally added once both sides exist.

## Scope and omissions

**This node covers** the shape of `buzz-cli`'s command tree (`Cli`/`Cmd`
and the 22 per-group enums), how a command is declared with `clap`, the
`run_from_args` → `run()` → group `dispatch` control flow, which command
groups do and do not honor the global `--format` flag (and the one case,
`Moderation`, that accepts but ignores it), the `Pack` group's no-relay
exception, and the `CliError`/exit-code contract every dispatch function
shares.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whole-container responsibility, technology, and interfaces for `buzz-cli` | `architecture/containers/cli.md` (already merged) |
| Authentication/signing mechanics | `platforms/cli/authentication.md` (issue #1235, not yet written) |
| Per-group business logic (all 22 groups) | Each group's own future implementation-reference/capability node |
| HTTP/WS transport, retry policy | `crates/buzz-cli/src/client.rs`, summarized in `architecture/containers/cli.md` |
| `buzz://` deep-link construction/parsing | `crates/buzz-cli/src/links.rs`, summarized in `architecture/containers/cli.md` |

**Expected but not verified when this node was written:**

- **Whether every one of the 21 non-`Pack` dispatch functions' internal
  `match` arms is exhaustive against its own `*Cmd` enum was not checked
  arm-by-arm for all 22 groups.** The signatures and the five that accept
  `format` were confirmed for all groups; each group's full internal
  behavior was not read in depth (see *Boundary*).
- **Whether any command group outside the five identified
  (Messages/Channels/Users/Feed/Moderation) reads `cli.format` indirectly**
  (for example, via a value stored on the client or a thread-local) rather
  than as an explicit function parameter was not exhaustively ruled out --
  the confirmed claim above is limited to the `dispatch` function
  signatures `run()` actually calls.
- **No corpus node instance for `buzz-dev-mcp`'s own container or command
  surface exists yet to link against**, so the "depended on by" row above
  cites the already-merged `architecture-containers-cli` node's evidence
  rather than a `buzz-dev-mcp` component node of its own.
