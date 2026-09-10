---
id: platforms-cli-exit-codes
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "crates/buzz-cli/src/error.rs defines CliError with exactly nine variants: Usage(String), Relay { status: u16, body: String }, Network(#[from] reqwest::Error), Auth(String), Key(String), Conflict(String), NotFound(String), DeliveryUnknown(String), and Other(String)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/error.rs's exit_code function maps each CliError variant to a process exit code: Usage and NotFound both map to 1; Relay maps to 3 when status is 401 or 403 and to 2 otherwise; Network and DeliveryUnknown both map to 2; Auth and Key both map to 3; Conflict maps to 5; Other maps to 4."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/error.rs's print_error function writes one JSON object to stderr for every non-success exit, shaped {\"error\": <category>, \"message\": <Display string>, \"retryable\": <bool>}, where category is one of user_error (Usage), relay_error or auth_error (Relay, split on the same 401/403 check exit_code uses), network_error (Network), auth_error (Auth), key_error (Key), conflict (Conflict), not_found (NotFound), delivery_unknown (DeliveryUnknown), or error (Other)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/error.rs's is_retryable_error returns true only for a Network error whose underlying reqwest::Error reports is_connect(), is_timeout(), is_request(), is_body(), or is_decode() (excluding builder errors), and for a Relay error whose status is 429, 502, 503, or 504; DeliveryUnknown is hard-coded to false with a comment explaining the relay may have already executed the mutation before the response was lost, and every other variant falls through a catch-all _ => false."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/error.rs's own #[cfg(test)] mod tests exercises is_retryable_error (builder errors not retryable, 429/502/503/504 retryable, 400/401/403/404/422 not retryable, all non-Network/Relay variants not retryable) and the JSON error envelope's retryable field, but no test in that module calls exit_code directly or asserts its return value for any variant."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/lib.rs's run_from_args parses arguments with Cli::try_parse_from; on a parse error where clap's ClapError::use_stderr() is true it calls print_error(&CliError::Usage(...)) and returns 1 without constructing any other CliError variant; on a parse error where use_stderr() is false (the --help and --version paths) it prints clap's own output and returns 0; on a successful parse it calls run(cli).await, returning 0 for Ok(()) or, for Err(e), calling print_error(&e) and returning error::exit_code(&e)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "crates/buzz-cli/src/main.rs's entire body is a single #[tokio::main] async fn main that calls std::process::exit(buzz_cli::run_from_args(std::env::args()).await) — the i32 run_from_args returns is used as the real OS process exit code with no other logic in between."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/main.rs"
  - statement: "crates/buzz-cli/README.md states, in one line: \"All output is JSON on stdout. Errors are JSON on stderr. Exit codes: 0=ok, 1=user error, 2=network, 3=auth, 4=other, 5=write conflict.\" — a summary that does not separately name that NotFound also maps to 1 (alongside Usage) or that DeliveryUnknown also maps to 2 (alongside Network and non-401/403 Relay statuses)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md"
  - statement: "This repository's root CLAUDE.md documents buzz-cli's exit codes as \"0=ok, 1=input error, 2=network/relay, 3=auth, 4=other, 5=write conflict (NIP-33 LWW)\" — the same coarser-than-source summary as the crate README, worded slightly differently (\"input error\" rather than \"user error\")."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "crates/buzz-cli/src/lib.rs constructs CliError::Auth (not CliError::Usage) when BUZZ_PRIVATE_KEY is not configured (\"BUZZ_PRIVATE_KEY is required (use --private-key or set env var)\"), and CliError::Key when the configured value fails to parse as a Nostr key (\"invalid BUZZ_PRIVATE_KEY: {e}\"); both therefore exit 3, not 1, per exit_code's mapping."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "crates/buzz-cli/TESTING.md's live-testing runbook documents manual verification scenarios consistent with this mapping: malformed flag values (invalid UUID, invalid hex64, invalid enum value, an empty required-field guard) are each annotated \"exit: 1\", and running a command against a relay with no BUZZ_PRIVATE_KEY configured is annotated \"exit: 3\" (\"No auth configured\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "launchpad/docs/corpus/architecture/containers/cli.md (id architecture-containers-cli, type architecture, status draft) already states as FACT that CliError distinguishes Usage/Relay/Network/Auth/Key/Conflict/NotFound/DeliveryUnknown/Other and that exit_code maps them to 0/1/2/3/4/5, and its own Scope and omissions table defers \"Full per-subcommand behavior\" to \"Implementation-reference nodes for individual capabilities, not this container-level node\" — this exit-codes node is exactly that deeper, structured-table level of detail for one facet the container node only summarizes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "launchpad/docs/corpus/templates/reference.md (id corpus-template-reference, merged on origin/launchpad) is a Diátaxis Reference-form template whose own Boundary section names \"a status code's meaning\" as an example of the kind of fact a reader looks up in a reference node, and whose required sections are a Reference description, structured entries, an optional Commands table, a Boundary statement, Relationships, and Scope and omissions."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
  - statement: "relationships.schema.json defines part-of's directionality as \"source is a constituent section/child of target\", with a generated inverse has-part."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At the recorded revision, launchpad/docs/corpus/platforms/ does not exist anywhere on origin/launchpad, so no already-merged platforms-typed corpus node exists to follow as precedent for this node's own choice of type: platforms; that choice is instead grounded directly in node.schema.json's own enum, which lists platforms as one of PRD #602's named in-scope corpus surfaces, and in the fact that this node's own path (launchpad/docs/corpus/platforms/cli/exit-codes.md) sits under that surface's directory, the same path-to-type correspondence architecture/**/*.md nodes already show for type: architecture."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/containers/cli.md"
    confidence: 0.6
---

# `buzz-cli` exit codes: reference

This node catalogues every process exit code the `buzz` binary
(`crates/buzz-cli`) can return, the `CliError` variant(s) that produce it, the
JSON error category `print_error` writes to stderr alongside it, and whether
that category is ever retried automatically. It is linked from, and goes one
level deeper than, `architecture-containers-cli`'s own container-level summary
of the same contract — that node states the mapping exists and gives its
five/six-way split; this node is the structured table a script or agent
consuming `buzz`'s exit status actually needs.

## Exit code table

`run_from_args` (`crates/buzz-cli/src/lib.rs`) is the only place a `buzz`
invocation's exit code is decided, and `main.rs`'s sole statement,
`std::process::exit(buzz_cli::run_from_args(...).await)`, is the only place
that value reaches the OS. Two paths return an exit code without ever
constructing a `CliError`: a successful command returns `0`, and a clap parse
failure that clap itself classifies as `--help`/`--version` output (rather
than a real usage error) prints normally and also returns `0`. Every other
non-zero code comes from `error::exit_code`, applied to whichever `CliError`
variant the command produced (or to a synthesized `CliError::Usage` for any
other clap parse failure).

| Exit code | `CliError` variant(s) | JSON `error` category | Condition | Retryable |
|---|---|---|---|---|
| 0 | — | — | Command succeeded (`Ok(())`), or clap printed `--help`/`--version` output | n/a |
| 1 | `Usage`, `NotFound` | `user_error`, `not_found` | Invalid argument/flag value (including any clap parse failure that isn't `--help`/`--version`), or a requested resource that does not exist / is tombstoned | false |
| 2 | `Relay { status }` (any status other than 401/403), `Network`, `DeliveryUnknown` | `relay_error`, `network_error`, `delivery_unknown` | A non-2xx relay response outside the auth range; a transport-level failure (connect, timeout, DNS, mid-request, mid-body, decode); or a non-idempotent command whose outcome could not be confirmed | `Relay`: only 429/502/503/504. `Network`: only connect/timeout/request/body/decode failures, never a builder error. `DeliveryUnknown`: never — the relay may already have executed the mutation |
| 3 | `Auth`, `Key`, `Relay { status: 401 \| 403 }` | `auth_error`, `key_error` | `BUZZ_PRIVATE_KEY` missing or unparsable, `BUZZ_AUTH_TAG` malformed, or the relay rejected the request with 401/403 | false |
| 4 | `Other` | `error` | Catch-all for a failure not covered by any other variant | false |
| 5 | `Conflict` | `conflict` | The relay accepted the write but reports it superseded by a newer head (NIP-33 last-write-wins) | false |

**The JSON envelope.** Every non-zero exit additionally writes one line of
JSON to stderr: `{"error": "<category>", "message": "<Display string of the
error>", "retryable": <bool>}`. `retryable` is exactly `is_retryable_error`'s
result for that error — a caller can branch on it instead of re-deriving
retryability from the exit code or category string.

**Two crate-level summaries are coarser than this table, not wrong.**
`crates/buzz-cli/README.md` and this repository's root `CLAUDE.md` each state
the mapping in one line (`0=ok, 1=user/input error, 2=network/relay, 3=auth,
4=other, 5=write conflict`). Both are accurate as far as they go; neither
separately calls out that `NotFound` shares code 1 with `Usage`, or that
`DeliveryUnknown` shares code 2 with `Network` and non-auth `Relay` statuses.
This table is the fuller version those two summaries point to.

## Boundary

This node does not describe:
- `buzz-cli`'s full command surface, its container-level technology choices,
  or its inbound/outbound interfaces — see `architecture-containers-cli` for
  that, and see this node's own *Relationships* section for how the two fit
  together.
- The retry/backoff policy inside `BuzzClient::with_retry_body` (timeouts,
  jitter, the 429 `retry in Ns` hint) — that is `client.rs`'s own mechanism
  for *when* a retryable error is retried, not part of the exit-code contract
  itself. `is_retryable_error`'s boolean result is the only piece of that
  mechanism this table depends on.
- `buzz-admin`'s exit codes, if it has its own contract — that is a separate
  crate and binary, not `buzz-cli`, and is out of scope here.
- How to accomplish a task with `buzz` step by step — that is a how-to/
  procedure document, not this reference table, per Diátaxis's own boundary
  between the two forms.

## Relationships

- part-of: architecture-containers-cli
- references: corpus-template-reference

`architecture-containers-cli` already exists on `origin/launchpad` and its own
Scope and omissions table explicitly defers "full per-subcommand behavior" to
a node like this one, so `part-of` — "source is a constituent section/child of
target" per `relationships.schema.json` — is the type that matches this node
actually being the deeper detail behind one line of that container node's own
summary. The `references` edge toward `corpus-template-reference` is optional
and records which template this node's shape follows; it is dropped only if
review prefers to rely on the node's own shape as evidence of that instead.

## Scope and omissions

**This node covers** every `CliError` variant, its mapped exit code, its JSON
`error` category string, and whether `print_error`'s `retryable` field is ever
`true` for it — sourced directly from `crates/buzz-cli/src/error.rs`,
`lib.rs`'s `run_from_args`, and `main.rs`'s exit wiring.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-cli`'s full command surface and container-level architecture | `architecture-containers-cli` |
| The retry/backoff mechanism that decides *when* a retryable error is retried | A future component/implementation-reference node for `client.rs`, not yet written |
| `buzz-admin`'s own exit-code contract, if any | `buzz-admin`'s own future container/component node, not yet written |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No automated unit test asserts `exit_code`'s return value directly.**
  `error.rs`'s own test module exercises `is_retryable_error` and the JSON
  envelope's `retryable` field, but no test calls `exit_code` and checks the
  integer it returns for any variant — the mapping in this node's table is
  read straight from `exit_code`'s match arms, not confirmed by a passing
  assertion.
- **Whether every one of `buzz-cli`'s 22 command groups only ever constructs
  the nine `CliError` variants shown here was not exhaustively checked.** A
  representative sample (`commands/channels.rs`, `commands/issues.rs`,
  `commands/moderation.rs`) was grepped for `CliError::` construction sites
  and all matched one of the nine variants; the remaining command files were
  not individually read in full.
- **Whether `buzz-cli` embedded inside `buzz-dev-mcp`'s multicall binary
  (invoked as the `buzz` personality) surfaces these same exit codes
  identically to the standalone binary was not traced.** `main.rs`'s
  `std::process::exit` wiring is specific to the standalone binary;
  `architecture-containers-cli` names the embedded path as a FACT but does not
  trace its own exit-code plumbing either, and that trace was not done here.
- **`crates/buzz-cli/TESTING.md`'s exit-code annotations are read as
  documentation of expected behavior, not as evidence a live run was
  performed while authoring this node.** No live `buzz` invocation was made
  to confirm any of the runbook's annotated exit codes during this node's
  authoring.
