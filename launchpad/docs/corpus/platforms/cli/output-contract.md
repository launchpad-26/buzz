---
id: platforms-cli-output-contract
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
  - statement: "normalize_events maps each raw event JSON value into an object carrying exactly id, pubkey, kind, content, created_at and tags with defaulted values, and additionally carries sig only when the source value's sig field is present and is a JSON string; any other field on the source value (e.g. a relay-internal field) is dropped."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1328-1347"
  - statement: "A dedicated test signs a real Nostr event, adds an extra relay_internal field, runs it through normalize_events, and asserts the output round-trips through nostr::Event and verifies, that sig is present, and that relay_internal is absent; a second test asserts that an event with no sig field and an event with a non-string sig both omit sig from the normalized output."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:2336-2366"
  - statement: "normalize_write_response reads a raw relay response, and when the parsed JSON carries an event_id or accepted field, re-emits exactly {event_id, accepted, message} with defaulted values for any of the three that are absent or the wrong type; any other field on the raw response (such as an unrecognized extra key) is dropped; when the raw response carries neither field, or fails to parse as JSON, the raw text is returned unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1448-1463"
  - statement: "A test posts a raw write response containing event_id, accepted, message and an unrecognized extra key, and asserts the normalized output keeps only the three canonical keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/repos.rs:839-854"
  - statement: "create_response_with_id_if_accepted parses a write response, reads its accepted boolean (defaulting to false when absent or non-boolean), and sets the given id_key to id_val on the response object only when accepted is true; when accepted is false the object is returned with no id field injected."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1415-1426"
  - statement: "A comment directly above create_response_with_id_if_accepted states the rationale for the accepted-only injection: emitting a locally-computed link when the relay rejected the event would let a caller share a link to an event that was never stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1415-1418"
  - statement: "Two tests exercise create_response_with_id_if_accepted directly: one asserts the id is injected and the original event_id/accepted fields are preserved when accepted is true, the other asserts no id is injected when accepted is false."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:2411-2429"
  - statement: "extract_relay_response_field parses a raw response's message field as a string, strips a literal 'response:' prefix, parses the remainder as JSON, and reads one named field from it as a string; it returns None at any step that fails (response is not JSON, message is absent or not a string, message does not start with 'response:', the remainder does not parse as JSON, or the named field is absent or not a string)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:1436-1446"
  - statement: "parse_write_response, in commands/mod.rs, is the shared helper documented as used by every command that publishes a NIP-33 addressable event: it parses the raw response as JSON (erroring as CliError::Other if it is not JSON), reads accepted and message, returns CliError::Other when accepted is false, returns CliError::Conflict with the caller-supplied message when message is exactly 'duplicate' or starts with 'duplicate:', and otherwise returns normalize_write_response's output."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs:74-96"
  - statement: "A test in commands/repos.rs calls the crate's own validate_write_response wrapper (which delegates to parse_write_response) with a response whose message is 'duplicate: superseded' and asserts the result is Err(CliError::Conflict(_)), and a second test with message 'saved' asserts the result normalizes to exactly {event_id, accepted, message} with the extra key dropped."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/repos.rs:189-194"
      - "crates/buzz-cli/src/commands/repos.rs:829-854"
  - statement: "CliError::exit_code maps CliError::Usage and CliError::NotFound to 1, CliError::Relay with status 401 or 403 (and CliError::Auth, CliError::Key) to 3, CliError::Relay with any other status, CliError::Network and CliError::DeliveryUnknown to 2, CliError::Other to 4, and CliError::Conflict to 5; a doc comment directly above the function states this same mapping in prose (0=success, 1=user/not-found, 2=network/relay, 3=auth, 4=other, 5=write conflict)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs:87-108"
  - statement: "print_error serializes every CliError to a JSON object on stderr shaped {error: <category>, message: <Display string>, retryable: <bool from is_retryable_error>}, with category one of user_error, auth_error, relay_error, network_error, key_error, conflict, not_found, delivery_unknown, or error; run_from_args calls print_error and then error::exit_code on every Err branch of run(), and calls neither on the Ok(()) branch, which returns exit code 0."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs:110-136"
      - "crates/buzz-cli/src/lib.rs:41-59"
  - statement: "is_retryable_error returns true only for a CliError::Network whose underlying reqwest::Error is a connect, timeout, request, body, or decode failure, and for a CliError::Relay whose status is 429, 502, 503, or 504; CliError::DeliveryUnknown and every other variant, including CliError::Relay at any other status, return false. A doc comment states DeliveryUnknown is deliberately never retryable because the operation may already have executed."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs:64-85"
  - statement: "Tests assert relay statuses 429, 502, 503 and 504 are retryable and that 400, 401, 403, 404 and 422 are not; a builder-level reqwest error (constructed from an invalid URL) is asserted not retryable, distinguishing it from a live transport failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs:144-192"
  - statement: "The Cli struct's format field, of type OutputFormat (json default, or compact), is declared directly on the top-level Cli struct that clap derives argument parsing from, one field above the #[command(subcommand)] field; it is not declared on any individual subcommand's own argument struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:80-96"
  - statement: "Because clap's derive parses a struct's own flags before it can recognize which subcommand variant follows, and format is a field of the outer Cli struct rather than any subcommand's struct, --format must be given before the subcommand name on the command line for clap to associate it with the run; a subcommand-positioned --format is not a flag any subcommand struct declares."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/lib.rs:80-96"
    confidence: 0.75
  - statement: "OutputFormat is a two-variant clap::ValueEnum (Json, default; Compact) whose doc comment states it is the 'Output format for read commands.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:163-172"
  - statement: "format_events in both commands/feed.rs and commands/messages.rs projects a normalized event array down to exactly {id, content, created_at} under OutputFormat::Compact, and passes the full normalized JSON through unchanged under OutputFormat::Json; a test in each file, named identically (compact_event_format_remains_the_three_key_contract), signs a full seven-field event and asserts the compact output is exactly those three keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/feed.rs:8-26"
      - "crates/buzz-cli/src/commands/feed.rs:87-113"
      - "crates/buzz-cli/src/commands/messages.rs:335-352"
      - "crates/buzz-cli/src/commands/messages.rs:1082-1103"
  - statement: "cmd_get_users, in commands/users.rs, does not pass a raw or normalize_events-shaped event through OutputFormat at all: it first decodes each kind:0 event's content string as a JSON profile object and injects the event's pubkey into it, then, under OutputFormat::Compact, projects that profile down to {pubkey, display_name}, and under OutputFormat::Json serializes the full decoded-profile array; neither branch touches the seven-field normalized event shape normalize_events produces."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:44-81"
  - statement: "cmd_list_channels, in commands/channels.rs, similarly builds its output from extract_channel_metadata-shaped channel objects rather than from normalize_events output; under OutputFormat::Compact it projects each channel down to {channel_id, name}, and under OutputFormat::Json it serializes the full channel-metadata array."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:69-113"
  - statement: "Because the root CLAUDE.md states as a repository-wide claim that 'Normal output preserves the seven canonical signed Nostr event fields' on reads, but cmd_get_users and cmd_list_channels both read a filter, then discard the raw event shape entirely in favor of a domain-specific reshaping (a decoded profile, an extracted channel-metadata object) before ever branching on OutputFormat, that root-level claim describes the message- and feed-style read commands that route through normalize_events and format_events, not every CLI read command; a user or channel listing's json output is a reshaped domain object, not the seven-field event."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:44-81"
      - "crates/buzz-cli/src/commands/channels.rs:69-113"
      - "crates/buzz-cli/src/commands/feed.rs:8-26"
    confidence: 0.8
  - statement: "buzz-cli's own Cargo.toml lists clap, reqwest, tokio, serde, serde_json, thiserror, nostr and uuid as its direct dependencies, with the manifest's own inline comment on the thiserror line reading 'Structured error types with exit code mapping.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml:17-38"
  - statement: "Three other crate manifests in this repository declare a dependency on buzz-cli: buzz-backend-kubernetes, buzz-dev-mcp, and git-sign-nostr."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/git-sign-nostr/Cargo.toml"
  - statement: "A comment in run_from_args explains that buzz-dev-mcp delegates to run_from_args directly (in-process, not by shelling to the buzz binary) and that when it does so it has already installed the ring rustls CryptoProvider, so run_from_args's own best-effort install is a harmless no-op double-install in that path."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:29-39"
  - statement: "run_from_args prints normal --help/--version text via clap's own e.print() and returns exit code 0 for that branch specifically, rather than routing it through print_error's JSON-on-stderr error contract; a parse error for any other reason is routed through print_error(&CliError::Usage(...)) and returns exit code 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:41-53"
  - statement: "part-of is the relationship type this node declares toward architecture-containers-cli, because relationships.schema.json defines part-of's directionality as 'source is a constituent section/child of target', which matches this node's subject -- one behavioral contract belonging to the buzz-cli container -- more closely than any of the schema's other four relationship types; architecture-containers-cli is already merged on origin/launchpad (checked via git ls-tree immediately before finalizing this front matter), so the edge resolves."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/architecture/containers/cli.md"
    confidence: 0.75
  - statement: "Issue #1239's Definition of Done requires this node to state responsibility and a well-defined interface/boundary, name dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire containing platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1239 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-cli
---

# buzz-cli: output contract

`crates/buzz-cli` normalizes every relay response before printing it and maps every
error to one of six process exit codes. This node documents that shared
normalization and exit-code contract as one component-level knowledge artifact,
independent of any single subcommand's own business logic -- what a caller of the
`buzz` binary, or a library caller of `buzz_cli::run_from_args`, can rely on across
every command.

## Responsibility

`buzz-cli` is responsible for turning a relay's raw HTTP/JSON response into one of a
small number of predictable output shapes, and for turning every internal failure
into one of six documented process exit codes plus a JSON error object on stderr --
so that a calling agent or script can branch on structure rather than parsing
human-readable text. The crate's own `long_about` states this contract directly:
"Exit codes: 0=ok 1=bad input 2=relay/network error 3=auth error 4=other 5=write
conflict" and "Errors are JSON on stderr: `{"error": "<category>", "message":
"<detail>"}`" (`crates/buzz-cli/src/lib.rs:63-78`). No crate-level `//!` doc comment
exists in `lib.rs` to cite instead; the `long_about` string is the nearest equivalent
authored responsibility statement, and is cited as such above.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `normalize_events` | fn | Reshapes a raw event JSON array into the canonical `{id, pubkey, kind, content, created_at, tags}` shape, plus `sig` only when present and a string; drops every other field. | `crates/buzz-cli/src/client.rs:1328-1347` |
| `normalize_write_response` | fn | Reshapes a raw relay write response into exactly `{event_id, accepted, message}` when either key is present; passes raw text through unchanged otherwise. | `crates/buzz-cli/src/client.rs:1448-1463` |
| `create_response_with_id_if_accepted` | fn | Injects a caller-supplied entity id into a write response only when `accepted` is `true`; never on rejection. | `crates/buzz-cli/src/client.rs:1415-1426` |
| `extract_relay_response_field` | fn | Reads one named field out of a write response's `message: "response:{...}"` envelope, or `None` if any parse step fails. | `crates/buzz-cli/src/client.rs:1436-1446` |
| `commands::parse_write_response` | fn | Shared write-response gate used by every NIP-33 write path: rejects with `CliError::Other` when not accepted, maps a `"duplicate"`/`"duplicate:*"` message to `CliError::Conflict`, otherwise returns `normalize_write_response`'s output. | `crates/buzz-cli/src/commands/mod.rs:74-96` |
| `error::exit_code` | fn | Maps every `CliError` variant to one of the six documented process exit codes (0 is the `Ok(())` path in `run_from_args`, never this function). | `crates/buzz-cli/src/error.rs:87-108` |
| `error::print_error` | fn | Serializes any `CliError` to `{error, message, retryable}` JSON on stderr. | `crates/buzz-cli/src/error.rs:110-136` |
| `error::is_retryable_error` | fn | Reports whether a given `CliError` is transient (connect/timeout/body/decode network failures, or relay 429/502/503/504); feeds the `retryable` field above. | `crates/buzz-cli/src/error.rs:64-85` |
| `--format` (global flag) | CLI flag | `json` (default, full normalized/reshaped output) or `compact` (per-command reduced projection); declared on the top-level `Cli` struct, so it must precede the subcommand name. | `crates/buzz-cli/src/lib.rs:80-96`, `crates/buzz-cli/src/lib.rs:163-172` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `clap` | Derives `Cli`'s argument parsing, including the global `--format` flag and every subcommand. | `crates/buzz-cli/Cargo.toml:17-19` |
| `serde_json` | Backs every normalization function's JSON parsing and re-serialization. | `crates/buzz-cli/Cargo.toml:28-30` |
| `thiserror` | Derives `CliError`'s `Display` impl that `print_error` serializes into the `message` field. | `crates/buzz-cli/Cargo.toml:32-33` |
| `reqwest` | Supplies the transport-level error variants `is_retryable_error` inspects (`is_connect`, `is_timeout`, `is_request`, `is_body`, `is_decode`). | `crates/buzz-cli/Cargo.toml:21-22` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `buzz-dev-mcp` | Delegates to `buzz_cli::run_from_args` in-process rather than shelling to the `buzz` binary. | `crates/buzz-dev-mcp/Cargo.toml`, `crates/buzz-cli/src/lib.rs:29-39` |
| `buzz-backend-kubernetes` | Depends on the `buzz-cli` crate. | `crates/buzz-backend-kubernetes/Cargo.toml` |
| `git-sign-nostr` | Depends on the `buzz-cli` crate. | `crates/git-sign-nostr/Cargo.toml` |

## Boundary

This node does not describe:
- The rest of the `buzz-cli` container -- its subcommand catalogue, auth flow, retry
  policy beyond `is_retryable_error`'s classification, or the relay HTTP surface it
  calls -- see `architecture-containers-cli` for that broader decomposition.
- Any single subcommand's own domain logic or validation rules (channel name
  validation, hex-key checks, and similar) -- those live in each `commands/*.rs`
  module and are not part of the shared output/exit-code contract.
- The relay's own wire contract for what it returns before the CLI normalizes it --
  that is the relay's concern, not the CLI's.
- Every read command's `--format compact` projection as a single shared shape. It is
  not one: `feed`/`messages` compact to the same three keys (`id`, `content`,
  `created_at`) from a normalized event, while `users get`/`channels list` compact to
  entirely different, domain-specific key sets (`{pubkey, display_name}`,
  `{channel_id, name}`) from an already-reshaped object that never passed through
  `normalize_events` at all. This node documents the shared normalization/exit-code
  machinery; it does not catalogue every command's own compact key set.
- `--help` and `--version` output, which `run_from_args` prints as plain clap text on
  the success path (exit 0), outside the JSON-error/exit-code contract entirely.

## Relationships

- part-of: architecture-containers-cli

## Scope and omissions

**This node covers** the shared response-normalization functions (`normalize_events`,
`normalize_write_response`, `create_response_with_id_if_accepted`,
`extract_relay_response_field`, `parse_write_response`), the `CliError` → exit-code
and → JSON-error-object mappings, the retryability classification that feeds the
error object's `retryable` field, and the top-level `--format` flag's `json`/`compact`
contract and its consequence for flag placement -- each cited to the real
declaration and, where one exists, to a real test.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The CLI container's full internal decomposition | `architecture-containers-cli` |
| Per-command business logic and validation | Each `commands/*.rs` module |
| The relay's own response contract, independent of how the CLI reshapes it | Not yet a corpus node at the time of writing |
| Every individual command's own `--format compact` key set | Not yet a corpus node at the time of writing; flagged above as a real difference, not a shared shape |
| Auth (NIP-98), retry backoff timing, and agent-management subcommands | Not this node's subject |

**Expected but not verified when this node was written:**

- **No integration/E2E run of the `buzz` binary was performed for this node.** Every
  claim above is grounded in reading the source and the unit tests that ship beside
  it, not in observing a live relay round trip.
- **Whether `buzz-backend-kubernetes` and `git-sign-nostr` call any of the functions
  named in *Public interface*, versus only linking the crate for an unrelated item,
  was not checked** -- their `Cargo.toml` manifests confirm the dependency edge; their
  own source was not read for this node.
- **Whether every `commands/*.rs` module ultimately routes its writes through
  `commands::parse_write_response` was not exhaustively checked file-by-file** -- it is
  confirmed for `repos.rs` by a direct test and stated in `parse_write_response`'s own
  doc comment as the intended shared path for every NIP-33 write, but not verified
  against every other `commands/*.rs` write site.
