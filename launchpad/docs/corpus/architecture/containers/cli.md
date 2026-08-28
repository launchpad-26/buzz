---
id: architecture-containers-cli
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-cli is a Rust crate at crates/buzz-cli producing a library (buzz_cli) and a binary (buzz), described in its own manifest as the 'Agent-first CLI for Buzz relay'."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml"
  - statement: "The buzz binary's entire runtime is one call: main.rs installs no state of its own and immediately awaits buzz_cli::run_from_args, which does clap parsing, dispatch, and error-to-exit-code mapping."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/main.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "buzz-cli's top-level Cmd enum has 22 subcommand groups: agents, messages, channels, canvas, reactions, emoji, dms, users, workflows, feed, social, notes, repos, projects, patches, issues, pr, media, upload, mem, pack, and moderation."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "Each command group's handler logic lives in its own file under crates/buzz-cli/src/commands/ (agents.rs, messages.rs, channels.rs, workflows.rs, mem.rs, pack.rs, moderation.rs, and 14 others), separate from the clap argument definitions in lib.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "crates/buzz-cli/README.md's 'Commands' table lists 8 command groups (messages, channels, canvas, reactions, dms, users, workflows, repos, upload, pack, mem) and omits agents, emoji, feed, social, notes, projects, patches, issues, pr, and moderation, all of which exist as Cmd variants in lib.rs at this revision — the README is not a complete or current enumeration of the command surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "Configuration is three env-backed clap arguments on the root Cli struct: --relay (env BUZZ_RELAY_URL, default http://localhost:3000), --private-key (env BUZZ_PRIVATE_KEY, hex or nsec, the CLI's Nostr identity), and --auth-tag (env BUZZ_AUTH_TAG, a NIP-OA owner-attestation JSON tag injected into every signed event); flags override the env vars."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The buzz-dev-mcp crate depends on buzz-cli as a library and, when its own multicall binary is invoked with argv[0]/personality 'buzz', dispatches straight into buzz_cli::run_from_args(std::env::args()) rather than shelling out to a separate buzz-cli process."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/Cargo.toml"
      - "crates/buzz-dev-mcp/src/lib.rs"
  - statement: "buzz-acp's build_mcp_servers explicitly sets BUZZ_RELAY_URL and BUZZ_PRIVATE_KEY (bech32-encoded from its own configured keypair) in the environment of the dev-mcp server it registers for a session, and forwards the harness's own BUZZ_AUTH_TAG env var into that same server env when it is set and non-empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
  - statement: "AGENTS.md (this repository's root contributor guide) documents that BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, and BUZZ_AUTH_TAG are auto-injected by the ACP harness into managed agent subprocesses, and that in development they must be set manually."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "AcpClient::spawn, which launches an agent binary as a subprocess, calls tokio::process::Command::new(command) and never calls env_clear on it before adding extra_env entries, so the spawned process is not isolated from buzz-acp's own environment by this code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/acp.rs"
  - statement: "Given no env_clear call, tokio::process::Command follows std::process::Command's documented default of inheriting the parent process's full environment, so a spawned agent subprocess inherits BUZZ_RELAY_URL/BUZZ_PRIVATE_KEY/BUZZ_AUTH_TAG whenever buzz-acp itself carries them in its own process environment, in addition to the explicit injection into the dev-mcp server's env."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs"
      - "crates/buzz-acp/src/lib.rs"
    confidence: 0.6
  - statement: "buzz-cli authenticates relay writes and privileged reads by signing a NIP-98 kind:27235 HTTP-auth event (u, method, and payload-hash tags) with the configured Nostr key and sending it as an Authorization header; the README's Authentication table lists BUZZ_PRIVATE_KEY / NIP-98 Schnorr signature as the only supported mode."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-cli/README.md"
  - statement: "When configured, the NIP-OA auth tag is attached to every signed event via BuzzClient::sign_event (which also asserts exactly one auth tag ends up on the event) and additionally sent as a raw x-auth-tag HTTP header on requests, for relay-side owner-attestation checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "BuzzClient's outbound HTTP surface is built entirely from `{relay_url}` plus a small fixed set of relay paths: POST /events (submit a signed event), POST /query and POST /count (Nostr filter bridge), PUT /upload and PUT /media/upload (Blossom uploads), plus generic GET helpers (get_public, get_authed) used for paths such as media downloads; relay_url itself is normalized from ws(s):// to http(s):// and back via normalize_relay_url/to_ws_url."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "buzz-relay's router registers exactly those paths against buzz-cli's HTTP surface: POST /events -> api::bridge::submit_event, POST /query -> api::bridge::query_events, POST /count -> api::bridge::count_events, and PUT /upload plus PUT /media/upload -> api::media::upload_blob."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "buzz-cli also opens a direct WebSocket connection to the relay (via to_ws_url) to publish ephemeral events, used by agent-facing commands including agents draft-create, agents draft-update, and users set-presence, because those event kinds are WebSocket-only on the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "buzz-cli builds and parses buzz:// deep links for repository, coordinate, and related git entities (links.rs), and its own module doc states the desktop parser at desktop/src/shared/lib/entityLink.ts must stay format-compatible with it — a direct contract between the CLI container and the Desktop container that is not carried over HTTP or WebSocket at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/links.rs"
  - statement: "The pack subcommand group (validate, inspect) operates entirely on local persona-pack files via the buzz-persona crate and is documented in the Cli struct's long_about as running without a relay connection, unlike every other command group."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/Cargo.toml"
  - statement: "Every request-shaped operation (reads, writes, uploads) runs inside BuzzClient::with_retry_body, which retries up to RETRY_MAX_ATTEMPTS times on connect/timeout/request/body/decode network errors and on relay statuses 429/502/503/504, using the 429 response's 'retry in Ns' hint (capped at RETRY_IN_MAX_SECS) or exponential jitter otherwise; per-request timeouts (BUZZ_TIMEOUT_SECS, default 30s) and connect timeouts (BUZZ_CONNECT_TIMEOUT_SECS, default 15s) are independently configurable via env vars."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "CliError distinguishes Usage, Relay{status}, Network, Auth, Key, Conflict, NotFound, DeliveryUnknown, and Other, and exit_code maps them to the process exit codes documented in the CLI's own help text and README: 0=ok, 1=user error/not-found, 2=network or non-auth relay error, 3=auth error (401/403 relay responses map here too), 4=other, 5=write conflict (NIP-33 dominated head)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/README.md"
  - statement: "print_error writes a single JSON object to stderr — {\"error\": <category>, \"message\": <text>, \"retryable\": <bool>} — for every non-success exit, so a caller can distinguish transient from permanent failure without re-parsing free text."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "DeliveryUnknown is explicitly never marked retryable, because the relay may already have executed a non-idempotent command before the response was lost, and a blind retry could duplicate the mutation; this is a documented exception to the otherwise-mechanical retryability rule."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "buzz-cli depends on buzz-sdk (typed Nostr event builders) and buzz-core (event kinds, verification, tenant/relay-URL helpers) as its own crates, rather than constructing raw JSON events inline, and on buzz-ws-client for the ephemeral-event WebSocket path."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml"
  - statement: "AGENTS.md (this repository's root contributor guide) states as a repo-wide convention that new agent-facing features belong in buzz-cli first, with the REST/WebSocket call wired in client.rs, and that buzz-dev-mcp (shell + file tools for buzz-agent) is a separate concern from buzz-cli."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "buzz-cli's HTTP calls land on the same host-derived, community-scoped HTTP surface the relay documents for all clients (POST /events, POST /query, POST /count plus Blossom/media, git smart HTTP, and NIP-11/NIP-05), rather than a CLI-private API, per the relay's own documented API surface."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
---

# Container: `buzz-cli`

## Responsibility

`buzz-cli` (crate `crates/buzz-cli`, binary `buzz`) is Buzz's **agent-first
command-line interface**: a thin, scriptable translation layer between
shell-driven callers — AI agents in particular — and the relay's Nostr event
model. It turns flag-driven subcommands (`buzz messages send`, `buzz channels
create`, `buzz mem set`, …) into signed Nostr events or Nostr-filter queries,
sends them to a configured relay over HTTP or WebSocket, and prints the
relay's response (or a structured error) as JSON. `AGENTS.md`'s own
convention — new agent-facing features get a `buzz-cli` subcommand first — is
what keeps this container as the single place that surface grows.

It does one narrow job well: **request shaping, signing, and transport**, not
business logic. Filtering, persistence, fan-out, and NIP-29 scoping all live
relay-side; `buzz-cli` never talks to Postgres, Redis, or the filesystem
except to read a persona-pack file for the local-only `pack` group.

## Technology

- **Language/runtime:** Rust, `tokio` (multi-thread runtime), async throughout.
- **CLI parsing:** `clap` (derive macros), with `env` support wiring flags to
  env vars automatically.
- **Transport:** `reqwest` (HTTP/JSON) for the request/response surface, plus
  a direct WebSocket connection (`buzz-ws-client`) for events the relay only
  accepts over WS.
- **Identity/crypto:** the `nostr` crate for key handling and event signing
  (NIP-98 HTTP-auth events, NIP-33 addressable events, etc.), `sha2` for
  payload hashes, `base64` for the Authorization header.
- **Event construction:** `buzz-sdk` (typed builders) and `buzz-core` (kind
  registry, tenant/relay-URL helpers) rather than hand-built JSON.
- **Packaging:** ships as its own binary (`cargo install --path
  crates/buzz-cli`) **and** as a library embedded inside `buzz-dev-mcp`'s
  multicall binary — see *Inbound interfaces* below.

## Ownership boundary

`buzz-cli` owns: argument parsing and validation (`validate.rs`), event
signing and HTTP/WS transport (`client.rs`), the retry/timeout policy around
that transport, the exit-code and JSON-error contract (`error.rs`), and
`buzz://` deep-link construction/parsing for git entities (`links.rs`).

`buzz-cli` does **not** own: relay-side authorization, storage, or NIP-29
scoping (that's `buzz-relay` / `buzz-auth` / `buzz-db`); the desktop or
mobile UI that renders the same events; or the local shell/file-edit tools
bundled alongside it in `buzz-dev-mcp` (`rg`, `tree`, `read_file`,
`str_replace`, `shell`, …) — those are a distinct tool surface that happens
to ship in the same binary, not part of this container's responsibility.

## Inbound interfaces

- **Direct process invocation.** A human or agent shell runs `buzz <group>
  <subcommand> [flags]`. `main.rs` does nothing but call
  `buzz_cli::run_from_args` and exit with its returned code.
- **Embedded inside `buzz-dev-mcp`.** `buzz-dev-mcp` depends on `buzz-cli` as
  a library; its multicall binary, when invoked as `buzz` (a symlink/argv0
  personality), dispatches directly into `buzz_cli::run_from_args` — no
  second process, no IPC. This means `buzz-cli`'s command surface is
  reachable both as a standalone binary and as one personality of the
  developer-MCP binary an agent's harness spawns.
- **Configuration is environment-first.** `--relay`/`BUZZ_RELAY_URL`,
  `--private-key`/`BUZZ_PRIVATE_KEY`, and `--auth-tag`/`BUZZ_AUTH_TAG` are the
  whole of it; flags override the env vars, and CLI flags with `hide_env_values`
  keep the key and auth tag out of `--help` output. In an ACP-managed agent
  session, `buzz-acp` sets `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` explicitly in
  the `buzz-dev-mcp` server's own environment and forwards `BUZZ_AUTH_TAG`
  when present; whether an agent's own subprocess additionally inherits those
  same vars from `buzz-acp`'s process environment depends on `buzz-acp`'s own
  environment at spawn time — confirmed only that no `env_clear` call removes
  that possibility (see the INFERENCE entry in this node's evidence ledger).

## Outbound interfaces / directly connected containers

- **`buzz-relay` (HTTP).** `POST /events` (submit any signed event), `POST
  /query` / `POST /count` (Nostr-filter bridge), `PUT /upload` and `PUT
  /media/upload` (Blossom media), and generic authenticated/public `GET`
  reads. These land on the router's `api::bridge::*` and `api::media::*`
  handlers — the same narrow HTTP surface every other Buzz client uses, not a
  CLI-private API.
- **`buzz-relay` (WebSocket).** A direct WS connection for event kinds the
  relay only accepts over WebSocket (ephemeral kind:20001 events), used by
  `agents draft-create`, `agents draft-update`, and `users set-presence`.
- **Buzz Desktop, indirectly.** `links.rs` builds `buzz://` deep links that
  Desktop's `entityLink.ts` parser must stay format-compatible with — a
  contract carried inside message *content*, not over HTTP/WS, and enforced
  by a pair of mirrored tests rather than a shared schema.
- **Local filesystem, `pack` group only.** `buzz pack validate`/`buzz pack
  inspect` read a persona-pack file directly and never touch the relay —
  the one command group with no network dependency.

## Deployment, data, and security implications

- **No independent deployment artifact of its own significance beyond the
  binary.** `buzz-cli` is not a long-running service; it has no deployment
  pipeline entry in this repo's ecosystem table (see `AGENTS.md`'s Ecosystem
  section) the way the relay, desktop, and mobile containers do. It ships as
  part of whatever consumes it — a standalone install, or embedded in
  `buzz-dev-mcp`.
- **Identity is a bare secret key in the environment.** `BUZZ_PRIVATE_KEY`
  (hex or `nsec1...`) is the CLI's entire identity; there is no keychain
  integration, no rotation mechanism, and `hide_env_values` only keeps it out
  of `--help`, not out of the process environment or a parent shell's
  history if set inline.
- **NIP-98 signs every authenticated request**, binding method, URL, and a
  payload hash into the Authorization header — this is the CLI's sole
  authentication mode today (no session cookie, no OAuth path).
- **The NIP-OA `x-auth-tag` header carries owner-attestation data in the
  clear** alongside the signed event; `sign_event`'s single-auth-tag
  assertion is the CLI-side guard against a caller accidentally forging or
  duplicating that attestation.
- **Non-idempotent writes can leave `DeliveryUnknown` outcomes** (response
  lost after the relay may have already executed the mutation); the CLI
  deliberately never auto-retries these, trading a manual-recovery burden on
  the caller for safety against duplicate mutations.
- **Data never persists locally** except transiently for `mem patch`'s diff
  application and `upload`'s file read — `buzz-cli` holds no local database
  or cache; every read is a fresh relay round-trip.

## Implementation

- `crates/buzz-cli/src/lib.rs` — CLI surface (`clap` definitions, top-level
  dispatch, env-backed config).
- `crates/buzz-cli/src/commands/` — one file per command group's handler
  logic.
- `crates/buzz-cli/src/client.rs` — `BuzzClient`: signing, HTTP/WS transport,
  retry policy.
- `crates/buzz-cli/src/error.rs` — `CliError`, exit-code mapping, JSON error
  envelope.
- `crates/buzz-cli/src/validate.rs`, `src/links.rs`,
  `src/agent_management.rs` — input validation, deep links, and agent-draft
  helpers respectively.
- `crates/buzz-cli/README.md` — usage examples and (partially stale, see
  evidence ledger) command table.
- `crates/buzz-cli/TESTING.md` — live-testing runbook against a real relay.
- `crates/buzz-dev-mcp/src/lib.rs` — the multicall dispatch that embeds this
  crate.
- `crates/buzz-acp/src/lib.rs` (`build_mcp_servers`) and
  `crates/buzz-acp/src/acp.rs` (`AcpClient::spawn`) — how the ACP harness
  wires this container's env-based config into a running agent session.

This node does not restate any of that source; read it for behavior, this
node for the shape of the container and its boundaries.

## Scope and omissions

**This node covers** `buzz-cli`'s responsibility, technology, ownership
boundary, its inbound and outbound interfaces, the containers/systems it
connects to directly, and the deployment/data/security implications visible
from its own source.

**It does not cover, and these are boundaries rather than gaps:**

| Not covered here | Owned by |
|---|---|
| Relay-side authorization, NIP-29 scoping, storage | `buzz-auth`, `buzz-db`, `buzz-relay` (their own container nodes, not yet written) |
| Full per-subcommand behavior (22 command groups, `crates/buzz-cli/src/commands/*.rs`) | Implementation-reference nodes for individual capabilities, not this container-level node |
| `buzz-dev-mcp`'s non-`buzz` personalities (`rg`, `tree`, `read_file`, `shell`, …) | `buzz-dev-mcp`'s own container node (not yet written) |
| `buzz-admin` (the separate operator CLI for relay administration) | `buzz-admin`'s own container node (not yet written) — not the same crate or audience as this one |

**Expected but not verified when this node was written:**

- **Whether every one of the 22 command groups' outbound calls stays within
  the HTTP/WS surface enumerated in *Outbound interfaces*.** Only `client.rs`
  itself and a representative slice of command handlers were read in depth;
  a command group calling a relay path not covered above (for example,
  workflow webhook delivery at `/hooks/{id}`, which is relay-side and not a
  `buzz-cli` outbound call) was not exhaustively ruled out for every group.
- **Whether an ACP-spawned agent subprocess actually receives
  `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` via environment inheritance from
  `buzz-acp`, as opposed to only the explicit `buzz-dev-mcp`-server injection
  this node confirmed as FACT.** `crates/buzz-acp/src/acp.rs`'s `spawn`
  function was read far enough to confirm no `env_clear` call removes that
  possibility; the INFERENCE entry in this node's evidence ledger is rated
  accordingly and a live ACP session was not run to observe the child
  process's actual environment.
- **The exact relationship between `crates/buzz-cli/README.md`'s
  "Architecture" diagram (which names a `commands/*.rs` layer) and this
  node.** The diagram is directionally accurate — `commands/` handlers do sit
  between `lib.rs` dispatch and `client.rs` — but the README's own command
  table was found materially incomplete at this revision (see the evidence
  ledger), so it was not relied on as a citation for the command inventory.

**No `relationships` in this node's front matter.** At the reviewed
revision no other `architecture-containers-*` (or any architecture-typed)
node is merged on `origin/launchpad` for this one to point at, and a
`relationships[].target` naming an id no loaded node carries is a hard
validation error per `node.schema.json`. This is the same situation
`AGENTS.md` describes explicitly: check what exists before claiming there is
nothing to link, and revisit once a sibling node (relay, desktop, dev-mcp,
auth, etc.) merges.
