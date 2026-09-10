---
id: platforms-cli-authentication
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
  - statement: "launchpad/docs/corpus/templates/component.md is a merged corpus template for a standalone software component or surface, directing an author to set type: implementation since node.schema.json's type enum has no dedicated component member; the sibling platforms/agents/* nodes already authored in this batch (e.g. platforms-agents-kubernetes-backend) follow that same id/type convention for a single behavioral surface, not only for a whole crate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "buzz-cli's root Cli struct defines exactly three configuration arguments: --relay (env BUZZ_RELAY_URL, default http://localhost:3000), --private-key (env BUZZ_PRIVATE_KEY, no default, hide_env_values set), and --auth-tag (env BUZZ_AUTH_TAG, no default, hide_env_values set); a command-line flag overrides the corresponding env var because clap resolves the env value only when no flag is supplied."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "run()'s auth setup, executed for every command except the local-only pack group, requires cli.private_key to be Some or returns CliError::Auth(\"BUZZ_PRIVATE_KEY is required (use --private-key or set env var)\") before any relay call is attempted; the private key string is then parsed with nostr::Keys::parse, which accepts either 64-hex or nsec1... bech32 form, and a parse failure becomes CliError::Key(\"invalid BUZZ_PRIVATE_KEY: {e}\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The parsed Keys value is the CLI's entire identity for the rest of the process: run() passes it straight into BuzzClient::new alongside the optional NIP-OA auth tag, and every other command handler receives only a &BuzzClient, never the raw key material directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "When --auth-tag/BUZZ_AUTH_TAG is set and non-empty, run() first runs normalize_auth_tag_input (rewriting the unquoted shorthand [auth,hex,,hex] into strict JSON when the input is not already valid JSON but is bracket-delimited with exactly four comma-separated fields containing no quote characters; anything else passes through unchanged), then feeds the normalized string to buzz_sdk::nip_oa::parse_auth_tag (structure-only: four elements, first is \"auth\", second is 64-hex, fourth is 128-hex) and buzz_sdk::nip_oa::verify_auth_tag (Schnorr-verifies the tag's signature against the CLI's own parsed public key); either failure becomes a CliError::Auth naming BUZZ_AUTH_TAG."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-sdk/src/nip_oa.rs"
  - statement: "buzz_sdk::nip_oa::verify_auth_tag's own doc comment states it reconstructs the signed preimage, hashes it, and verifies the BIP-340 Schnorr signature against the owner pubkey embedded in the tag, returning that owner PublicKey on success; parse_auth_tag's doc comment states it validates structure only (element count, the literal \"auth\" tag name, hex lengths) with no cryptographic check, and is the fast path used at MCP startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/nip_oa.rs"
  - statement: "normalize_auth_tag_input is unit-tested for three cases: the unquoted shorthand with an empty conditions field, the unquoted shorthand with a non-empty conditions field, and already-valid JSON passed through unchanged; a fourth test asserts unrecognizable garbage is returned trimmed but otherwise untouched rather than coerced."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "buzz-cli signs two structurally different kinds of authentication event depending on transport, both keyed off the same nostr::Keys and optional NIP-OA auth tag: sign_nip98 (client.rs) builds a NIP-98 kind:27235 HTTP-auth event carrying u (full request URL), method, a fresh uuid nonce, and (when a body is present) a payload tag holding the hex SHA-256 of the request body, signs it, and returns an Authorization: Nostr <base64-of-event-json> header value; publish_ephemeral_event delegates to buzz_ws_client::publish_event for the WebSocket transport, whose own doc comment states it performs NIP-42 authentication (connect, auth challenge/response, EVENT send, OK wait) before the ephemeral event is accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "sign_nip98 is called fresh on every attempt of an HTTP request, including retries: client.rs's comments at three call sites (submit_event, upload paths) state 're-sign NIP-98 each attempt: the nonce tag generates a fresh event id, so a retried request is never rejected as a signature/nonce replay of the prior attempt'; an integration test spinning up a local TCP listener asserts three retry attempts of a Blossom upload each carry a distinct, non-empty Authorization: Nostr ... header."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "BuzzClient::sign_event is the single method through which every relay-bound event builder must pass: it appends the configured NIP-OA auth tag (if any) to the builder's tags before signing, then re-counts auth-named tags on the signed event and returns CliError::Other if that count does not exactly equal 1 (auth tag configured) or 0 (not configured), enforcing that no caller adds its own auth tag ahead of this injection."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "A second signing entry point, sign_event_unchecked, exists specifically for NIP-IA identity-archive events (kind 9035) so that a caller-supplied content-level auth tag (proving ownership of a third-party identity being archived) is preserved verbatim rather than being overwritten by the client's own ambient NIP-OA auth tag; two unit tests assert this directly, one confirming the ambient tag is not injected into such an event and one confirming a caller's own auth tag on the builder survives signing unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "with_auth_tag attaches the client's auth_tag_json verbatim as a raw x-auth-tag HTTP header on a request only when one is configured, and is a no-op otherwise; two unit tests assert both branches: the header is present and equal to the configured JSON when an auth tag exists, and absent entirely when none was configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "CliError enumerates Auth(String) (\"missing or rejected (401/403)\") and Key(String) (Nostr key parse failure) as distinct variants from Relay{status,..}, Network, Conflict, NotFound, DeliveryUnknown, and Other; exit_code maps both Auth and Key to process exit code 3, and additionally maps a Relay{status} of 401 or 403 to exit code 3 as well, so an auth failure surfaces as exit 3 whether it was caught client-side (missing/malformed key or tag) or reported by the relay after a request was sent."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "print_error serializes every non-success exit as a single JSON object on stderr, {\"error\": <category>, \"message\": <text>, \"retryable\": <bool>}; CliError::Auth, CliError::Key, and a Relay{401|403} all map to the \"auth_error\" category, and is_retryable_error returns false unconditionally for CliError::Auth and CliError::Key (they fall through to the default false arm), so an auth failure is never automatically retried by the CLI's own with_retry_body loop."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "crates/buzz-cli/src/lib.rs's test secret_env_args_hide_their_values_in_help walks the full clap command tree (root plus every subcommand, recursively) and asserts that every argument whose env-var name contains KEY, SECRET, TOKEN, PASSWORD, CRED, or AUTH has hide_env_values set, which is how --private-key and --auth-tag are kept out of --help output at every level of the command tree, not only at the root."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "crates/buzz-cli/README.md's Authentication section lists a single row -- BUZZ_PRIVATE_KEY / NIP-98 Schnorr signature -- as the CLI's authentication mode, and its Usage section states the CLI's own exit-code convention (0=ok, 1=user error, 2=network, 3=auth, 4=other, 5=write conflict) matching error.rs's exit_code mapping exactly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md"
  - statement: "crates/buzz-cli/TESTING.md's '8. Auth Testing' section gives a live runbook for both the success and failure path: BUZZ_PRIVATE_KEY=\"nsec1...\" buzz channels list is expected to succeed, and running the same command with BUZZ_PRIVATE_KEY unset (env -u BUZZ_PRIVATE_KEY) is expected to print {\"error\":\"auth_error\",\"message\":\"auth error: BUZZ_PRIVATE_KEY is required (use --private-key or set env var)\"} on stderr and exit 3."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "The Archive subcommand's own --help text (kind 9035, NIP-IA identity archival) documents a distinct owner/agent authorization rule for this one command: when the target identity differs from the signer, the CLI fetches the target's kind:0 profile and attaches its embedded owner-auth tag, retrying once on extraction failure; the same text states plainly that 'an agent running under BUZZ_AUTH_TAG signs as itself, so it can only ever satisfy the self path (target == signer) -- not the owner-of-agent path for another identity,' naming --admin as the bypass for a relay-admin key."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "launchpad/docs/corpus/architecture/containers/cli.md (id architecture-containers-cli), an already-merged sibling node, states in its own security-implications section that 'NIP-98 signs every authenticated request ... this is the CLI's sole authentication mode today (no session cookie, no OAuth path),' citing only client.rs and README.md; that node's own Outbound interfaces section separately names the WebSocket path for ephemeral events without describing it as a second authentication mode, so its 'sole authentication mode' phrasing does not account for the NIP-42 WebSocket path this node documents above from the same client.rs file."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
      - "crates/buzz-cli/src/client.rs"
  - statement: "launchpad/docs/corpus/architecture/flows/websocket-authentication.md (id architecture-flows-websocket-authentication) already documents the generic NIP-42 challenge/response protocol between a client and buzz-relay in full, including the client-side connect_authenticated function in buzz-ws-client that publish_ephemeral_event (this node's WS auth path) ultimately calls; this node does not restate that mechanics and instead links to it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "launchpad/docs/corpus/architecture/flows/http-event-submission.md (id architecture-flows-http-event-submission) already documents the relay-side verification of the same NIP-98 Authorization: Nostr <base64> header this node's sign_nip98 produces, including buzz_auth::verify_nip98_event and the replay guard keyed on the auth event's own id; this node covers only the CLI's client-side construction of that header, not its relay-side verification."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
  - statement: "Issue #1235 requires exactly one hand-authored canonical corpus document with schema-valid front matter, evidence traceable to current code/tests/specification/decisions, links to implementation/verification/specification/neighboring nodes without duplicating their content, a stated responsibility and well-defined interface/boundary, named dependencies and collaborators, links to source implementation and tests, and component-level (not whole-platform) scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1235 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-cli
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-http-event-submission
---

# `buzz-cli` authentication

How `buzz-cli` (crate `crates/buzz-cli`, binary `buzz`) proves its own
identity to a Buzz relay: what configuration it reads, which cryptographic
mechanism it uses on each of its two transports, how it carries an optional
NIP-OA owner attestation, and how an authentication failure surfaces to a
caller. This node documents `buzz-cli`'s own authentication surface, not the
generic NIP-42/NIP-98 protocols themselves — those are `architecture/flows/*`
subjects, linked below rather than restated.

## Responsibility

`buzz-cli` has exactly one source of identity: a Nostr keypair configured
via `--private-key`/`BUZZ_PRIVATE_KEY` (hex or `nsec1...`). There is no
session, no token, and no separate login step — every relay-bound request or
event is signed fresh with that keypair. An optional second input,
`--auth-tag`/`BUZZ_AUTH_TAG`, carries a NIP-OA owner attestation the CLI
verifies against its own key and then attaches to outgoing requests/events,
letting an agent act with a human owner's delegated relay membership without
holding the owner's key.

Authentication is checked once, in `run()`, before any command handler runs
(except the local-only `pack` group, which never touches a relay): the key
is required and parsed, the auth tag (if present) is normalized, parsed, and
Schnorr-verified against the parsed key, and only then is a `BuzzClient`
constructed and handed to the command dispatcher. A command handler never
sees raw key material — only a `&BuzzClient` — and every signing/header
operation from that point on funnels through the client's own methods.

## Public interface

The "interface" other code and callers rely on is this configuration and
signing contract, not a Rust API — `buzz-cli` is a binary, and its identity
inputs are environment/flag surface plus two per-transport wire formats.

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `--private-key` / `BUZZ_PRIVATE_KEY` | CLI flag / env var | Required for every non-`pack` command; hex or `nsec1...`; `hide_env_values` keeps it out of `--help` | `crates/buzz-cli/src/lib.rs` |
| `--auth-tag` / `BUZZ_AUTH_TAG` | CLI flag / env var | Optional NIP-OA owner attestation JSON (or the unquoted 4-field shorthand); `hide_env_values` set | `crates/buzz-cli/src/lib.rs` |
| `sign_nip98(keys, method, url, body)` | function | Builds and signs a kind:27235 event (`u`, `method`, `nonce`, optional `payload` tags); returns an `Authorization: Nostr <base64>` header value | `crates/buzz-cli/src/client.rs` |
| `BuzzClient::sign_event(builder)` | method | Injects the configured NIP-OA `auth` tag (if any) and signs; asserts exactly the expected number of `auth` tags land on the result | `crates/buzz-cli/src/client.rs` |
| `BuzzClient::sign_event_unchecked(builder)` | method | Signs without ambient auth-tag injection, preserving any caller-supplied content-level `auth` tag verbatim — used for NIP-IA identity archival | `crates/buzz-cli/src/client.rs` |
| `with_auth_tag(req)` | method | Attaches the raw `x-auth-tag` header when an auth tag is configured; no-op otherwise | `crates/buzz-cli/src/client.rs` |
| `publish_ephemeral_event(event)` | method | Opens a direct WebSocket connection and authenticates via NIP-42 (delegated to `buzz_ws_client::publish_event`) before sending the event | `crates/buzz-cli/src/client.rs`, `crates/buzz-ws-client/src/connection.rs` |
| `CliError::Auth` / `CliError::Key`, `exit_code`, `print_error` | error contract | Every auth-related failure (missing key, bad key, malformed/unverifiable auth tag, or a relay 401/403) maps to exit code 3 and the JSON `{"error":"auth_error", ...}`/`{"error":"key_error", ...}` envelope on stderr | `crates/buzz-cli/src/error.rs` |

## Dependencies

**Depends on** (this surface requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `nostr` | Key parsing (`Keys::parse`, hex or `nsec1...`), event building, and BIP-340 Schnorr signing for both the NIP-98 and NIP-42 paths | `crates/buzz-cli/Cargo.toml`, `crates/buzz-cli/src/client.rs` |
| `buzz-sdk` (`nip_oa` module) | `parse_auth_tag` (structural validation) and `verify_auth_tag` (Schnorr verification against the CLI's own key) for the optional `BUZZ_AUTH_TAG` | `crates/buzz-cli/Cargo.toml`, `crates/buzz-sdk/src/nip_oa.rs` |
| `buzz-ws-client` | `publish_event`, which performs the NIP-42 connect/challenge/response/OK round trip for the WebSocket transport | `crates/buzz-cli/Cargo.toml`, `crates/buzz-ws-client/src/connection.rs` |
| `sha2`, `base64`, `uuid` | Payload-hash (`sha2`), Authorization-header encoding (`base64`), and per-signing-attempt nonce generation (`uuid`) inside `sign_nip98` | `crates/buzz-cli/Cargo.toml`, `crates/buzz-cli/src/client.rs` |
| `clap` (`env` feature) | Wires `--private-key`/`--auth-tag` to `BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` and enforces `hide_env_values` at the argument-definition level | `crates/buzz-cli/Cargo.toml`, `crates/buzz-cli/src/lib.rs` |

**Depended on by** (these require this surface):

| Component | Why | Evidence |
|---|---|---|
| Every `buzz-cli` command group except `pack` | `run()` constructs one authenticated `BuzzClient` before dispatch, and all 21 relay-touching command groups receive only that client, never raw key material | `crates/buzz-cli/src/lib.rs` |
| `buzz-relay`'s HTTP bridge (`POST /events`, `/query`, `/count`, media upload) | Verifies the NIP-98 `Authorization` header this surface produces (relay-side mechanics documented in `architecture-flows-http-event-submission`, linked below, not restated here) | `crates/buzz-cli/src/client.rs` |
| `buzz-relay`'s WebSocket handler | Verifies the NIP-42 challenge/response this surface produces for ephemeral-event publishing (relay-side mechanics documented in `architecture-flows-websocket-authentication`, linked below) | `crates/buzz-cli/src/client.rs`, `crates/buzz-ws-client/src/connection.rs` |

## Boundary

This node does not describe:
- **The generic NIP-98 or NIP-42 protocol mechanics** — event shape,
  relay-side verification, replay protection, or the WebSocket
  challenge/response state machine. Those are normative content of
  `architecture-flows-http-event-submission` and
  `architecture-flows-websocket-authentication` respectively; this node
  covers only how `buzz-cli`, as one client, constructs its side of each.
- **The NIP-OA attestation format itself** (what a valid `auth` tag's
  `conditions` grammar allows, how it is minted by an owner) — that is
  `buzz-sdk`'s `nip_oa` module's own subject; this node covers only how
  `buzz-cli` consumes and verifies a tag it is handed.
- **`buzz-cli`'s full container-level responsibility, interfaces, and
  deployment** (all 22 command groups, the retry/timeout policy, the
  `buzz://` deep-link contract, embedding inside `buzz-dev-mcp`) — that is
  `architecture-containers-cli`'s subject; this node is one narrower slice
  of it (`part-of`, declared below).
- **How an ACP-managed agent session's environment comes to carry
  `BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` in the first place** (`buzz-acp`'s
  `build_mcp_servers`/`AcpClient::spawn`) — `architecture-containers-cli`
  already covers that provisioning path; this node starts from the
  assumption those env vars are already set in the process environment.
- **Whether `architecture-containers-cli`'s "sole authentication mode"
  phrasing should be revised.** This node's own evidence shows `buzz-cli`
  has two authentication mechanisms in code today (NIP-98 over HTTP, NIP-42
  over WebSocket), which that already-merged sibling node's security section
  does not mention when it calls NIP-98 the CLI's sole mode. That is
  disclosed here as a discrepancy between two corpus nodes rather than
  resolved by editing the other node, which is out of this task's scope.

## Relationships

- `part-of`: `architecture-containers-cli` — this node documents one
  behavioral surface (authentication) of the container that node documents
  in full.
- `references`: `architecture-flows-websocket-authentication` — the
  generic NIP-42 mechanics `publish_ephemeral_event`'s WebSocket path relies
  on.
- `references`: `architecture-flows-http-event-submission` — the generic
  NIP-98 verification mechanics the relay applies to the header
  `sign_nip98` produces.

All three targets were confirmed present in `origin/launchpad`'s corpus tree
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`) at
the recorded revision before being declared, per `AGENTS.md`'s rule to check
the merge-target branch rather than the authoring worktree.

## Scope and omissions

**This node covers** `buzz-cli`'s own authentication configuration
(`BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, `BUZZ_RELAY_URL`'s role in the NIP-98
`u` tag), its two per-transport signing paths (NIP-98 over HTTP, NIP-42 over
WebSocket), the NIP-OA auth-tag parse/verify/injection/header lifecycle, the
`hide_env_values` credential-hygiene guard, and the CLI's own auth-specific
error and exit-code contract.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Generic NIP-98 event shape and relay-side verification/replay protection | `architecture-flows-http-event-submission` |
| Generic NIP-42 challenge/response protocol and relay-side gates | `architecture-flows-websocket-authentication` |
| The NIP-OA attestation format and grammar itself | `crates/buzz-sdk/src/nip_oa.rs` (no dedicated corpus node yet) |
| `buzz-cli`'s full container-level responsibility and interfaces | `architecture-containers-cli` |
| How an ACP-managed session's environment comes to carry these env vars | `architecture-containers-cli`'s Inbound interfaces section |
| Per-subcommand authorization nuances beyond the `Archive` example cited above (e.g. `moderation` commands requiring elevated relay-side permission) | Individual command implementation, not yet a corpus node |

**Expected but not verified when this node was written:**

- **No live relay round trip was run.** Every claim above is grounded in
  reading `buzz-cli`'s and `buzz-ws-client`'s source and their unit/
  integration tests, not in observing a real `buzz channels list` or
  `buzz agents draft-create` invocation against a running relay.
- **Whether every one of the 21 relay-touching command groups' outbound
  calls actually route through `sign_nip98`/`publish_ephemeral_event` and
  no other path was not exhaustively checked group-by-group** — only
  `client.rs`'s shared signing/header methods and a representative slice of
  call sites were read; a command group calling some other outbound path
  not covered above was not ruled out for every group.
- **Whether `moderation` subcommands enforce any relay-side authorization
  beyond the identity-proof this node documents** (e.g. requiring the
  signer to hold a specific relay role) was not investigated; this node
  covers only how the signer's identity is established and carried, not
  what a relay does with it afterward for any specific command.
