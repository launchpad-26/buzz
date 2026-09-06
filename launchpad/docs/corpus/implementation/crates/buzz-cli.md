---
id: implementation-crates-buzz-cli
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "The buzz binary's entire runtime is one call: main.rs installs no state of its own, calls std::process::exit on the result of buzz_cli::run_from_args(std::env::args()), and is 4 lines long."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/main.rs"
  - statement: "The top-level Cli struct's long_about text (embedded in lib.rs, shown by buzz --help) states the exit-code contract verbatim: 'Exit codes: 0=ok  1=bad input  2=relay/network error  3=auth error  4=other  5=write conflict', and that errors are JSON on stderr in the shape {\"error\": \"<category>\", \"message\": \"<detail>\"}."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "error.rs's exit_code function maps CliError variants to exactly that scheme: Usage and NotFound to 1, Network/DeliveryUnknown/non-401/403 Relay statuses to 2, Auth/Key/401-or-403 Relay status to 3, Other to 4, Conflict to 5."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "print_error in error.rs writes a single JSON object to stderr for every non-success exit -- {\"error\": <category>, \"message\": <text>, \"retryable\": <bool>} -- where retryable is computed by is_retryable_error: true only for connect/timeout/request/body/decode-class reqwest errors and relay statuses 429/502/503/504; DeliveryUnknown is explicitly excluded from ever being retryable regardless of its underlying cause."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "error.rs's own test module exercises this mapping directly: relay_429_502_503_504_are_retryable, relay_400_401_403_404_422_are_not_retryable, and json_error_includes_retryable_field_for_network assert the retryable predicate and the JSON error shape by construction, not by inspection of prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "The root Cli struct (lib.rs) declares three env-backed global arguments -- --relay/BUZZ_RELAY_URL (default http://localhost:3000), --private-key/BUZZ_PRIVATE_KEY, --auth-tag/BUZZ_AUTH_TAG -- both of the latter two marked hide_env_values = true, plus a fourth global argument, --format (value_enum OutputFormat: json default, compact), all parsed before the #[command(subcommand)] field selects one of 22 Cmd variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The dispatch match block routing cli.command to each command group's handler passes &cli.format to exactly 5 of the 21 dispatched arms (Messages, Channels, Users, Feed, Moderation); the remaining 16 (Agents, Canvas, Reactions, Emoji, Dms, Workflows, Social, Notes, Repos, Projects, Patches, Issues, Pr, Media, Upload, Mem) call their dispatch functions without it, and Pack is handled earlier in the function as a local-only path."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "messages get accepts a --kinds flag (comma-separated event kinds) while the sibling messages search subcommand's Search struct has no such field -- confirming CLAUDE.md's documented gotcha that messages search chooses its own supported kinds and does not accept a --kinds option, unlike raw relay-filter-shaped commands such as messages get."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "CLAUDE.md"
  - statement: "messages thread's Thread variant declares channel and event as required_unless_present = \"link\", conflicts_with = \"link\", and a separate link field with conflicts_with_all = [\"channel\", \"event\"] -- so buzz messages thread --link 'buzz://message?channel=<uuid>&id=<event>[&thread=<root>]' is a first-class alternative input path to the explicit --channel/--event flags, not merely something a caller pre-parses by hand."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "lib.rs's own test suite exercises this directly: messages_thread_accepts_link_or_explicit_identifiers asserts both forms parse via Cli::try_parse_from, and messages_thread_rejects_partial_or_mixed_targets asserts an incomplete or mixed set of channel/event/link arguments is a parse error."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "links.rs's parse_message_link function is the actual buzz://message parser: it validates scheme, host, empty/absent path, absence of userinfo and fragment, and exactly one occurrence each of the channel/id/thread query parameters, rejecting any unrecognized parameter (including a relay= parameter, which links.rs's own doc comment says is deliberate -- the link chooses only the channel and event within the relay already configured for this CLI process, and cannot override relay or identity)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/links.rs"
  - statement: "links.rs's module doc states the desktop parser at desktop/src/shared/lib/entityLink.ts (for git entities) and desktop/src/features/messages/lib/messageLink.ts (for messages) must stay format-compatible with this crate's link builders/parser, and links.rs's own test suite loads a shared golden fixture (test-fixtures/entity-links.json) to check pull_request_link, issue_link, repo_link, project_link, and is_linkable_dtag against values the desktop side is expected to agree on."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/links.rs"
  - statement: "client.rs defines RETRY_MAX_ATTEMPTS = 3 and RETRY_IN_MAX_SECS = 30 as module constants, and BuzzClient's reqwest::Client is built with a per-request timeout from env_duration_secs(\"BUZZ_TIMEOUT_SECS\", 30) and a connect timeout from env_duration_secs(\"BUZZ_CONNECT_TIMEOUT_SECS\", 15)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "client.rs's with_retry_body loops up to RETRY_MAX_ATTEMPTS times, and its own doc comment states a 429 response's server-supplied retry-after hint is honored (capped at RETRY_IN_MAX_SECS) with exponential jitter used otherwise; a dedicated test asserts RETRY_MAX_ATTEMPTS == 3 directly against the constant."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
  - statement: "client.rs contains 46 #[test]/#[tokio::test] functions and lib.rs plus the rest of crates/buzz-cli/src together contain 375 #[test] occurrences total, spanning retry/timeout policy (client.rs), exit-code and retryability mapping (error.rs), CLI parse-shape and mutual-exclusion rules (lib.rs), deep-link parse/build/golden-fixture parity (links.rs), and NIP-OA auth-tag normalization/priority (agent_management.rs, 4 tests)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/src/links.rs"
      - "crates/buzz-cli/src/agent_management.rs"
  - statement: "buzz-acp's build_mcp_servers (crates/buzz-acp/src/lib.rs) explicitly pushes BUZZ_RELAY_URL and BUZZ_PRIVATE_KEY as named env entries onto the dev-mcp server it registers for a session, and separately forwards BUZZ_AUTH_TAG (read from its own process environment) into that same server env only when the variable is set, matching CLAUDE.md's documented claim that these three vars are auto-injected by the ACP harness into managed agent subprocesses."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs"
      - "CLAUDE.md"
  - statement: "crates/buzz-cli/README.md's own 'Commands' table lists 8 command groups (messages, channels, canvas, reactions, dms, users, workflows, repos, upload, pack, mem) and omits agents, emoji, feed, social, notes, projects, patches, issues, pr, and moderation, all of which exist as dispatched Cmd variants in lib.rs at this revision -- the README is not a complete enumeration of the command surface, a gap already recorded in architecture-containers-cli's own evidence ledger and re-confirmed here independently against the current Cmd dispatch block."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/README.md"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "architecture-containers-cli is the merged corpus node documenting buzz-cli as an architecture container (responsibility, technology, inbound/outbound interfaces, deployment implications), and its own Scope and omissions table names 'Full per-subcommand behavior (22 command groups, crates/buzz-cli/src/commands/*.rs)' as owned by 'Implementation-reference nodes for individual capabilities, not this container-level node' -- the exact gap this node fills."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
---

# buzz-cli: implementation reference

This node documents `crates/buzz-cli` (the `buzz` binary and `buzz_cli`
library), and traces its code to the agent-facing CLI contract this
repository's own `CLAUDE.md` states for it: environment-first configuration
with auto-injected auth (`BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG`),
a global `--format compact` flag, deep-link resolution for `buzz://message`
links, and a fixed exit-code scheme (0=ok, 1=input error, 2=network, 3=auth,
4=other, 5=write conflict). Where the container-level `architecture-containers-cli`
node already establishes `buzz-cli`'s responsibility, technology, and
interfaces, this node goes one level deeper: does the code actually realize
what `CLAUDE.md` tells an agent to expect, and where does it not.

## Target

The target is `CLAUDE.md` (this repository's root contributor guide,
committed at the repository root) — specifically its "Agent CLI (`buzz-cli`)"
section and its "Common Gotchas" items #2 and #3. `CLAUDE.md` is not itself a
corpus node at this revision, so no `implements` edge is declared toward it
(per `templates/implementation-reference.md`'s explicit rule against
inventing an id for a target that has none); it is named here by its real
path instead. A reader can open it directly at the repository root.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-cli/src/main.rs` | The whole binary's entry point | 4 lines: `std::process::exit(buzz_cli::run_from_args(...).await)`. No logic of its own — everything lives in the library. |
| `crates/buzz-cli/src/lib.rs`, `Cli` struct (`--relay`/`BUZZ_RELAY_URL`, `--private-key`/`BUZZ_PRIVATE_KEY`, `--auth-tag`/`BUZZ_AUTH_TAG`) | CLAUDE.md's "set `BUZZ_PRIVATE_KEY` and `BUZZ_RELAY_URL` ... manually" / auto-injection contract | Flags override env vars (clap `env` support); the private-key and auth-tag flags carry `hide_env_values = true` so they never print in `--help`. |
| `crates/buzz-cli/src/lib.rs`, `--format` global flag / `OutputFormat` enum | CLAUDE.md's "`--format compact` is a global flag — it goes before the subcommand" | True as parsed: `format` sits on the same top-level `Cli` struct as `command`. See *Divergences* — only 5 of 21 dispatched command groups actually consume it. |
| `crates/buzz-cli/src/lib.rs`, `messages get`'s `--kinds` vs. `messages search`'s absent `--kinds` | CLAUDE.md Gotcha #3 ("`messages search` chooses its own supported kinds ... do not add a `--kinds` option") | Confirmed directly in the `Get`/`Search` subcommand structs, not merely from the doc's own claim. |
| `crates/buzz-cli/src/lib.rs`, `messages thread`'s `Thread` variant (`--channel`/`--event`/`--link`, mutually exclusive via `required_unless_present`/`conflicts_with`) | Deep-link resolution: `buzz --format compact messages thread --channel <uuid> --event <hex>` | See *Divergences* — `--link` accepts the raw `buzz://message` URL directly, beyond what CLAUDE.md's own workflow instructions describe. |
| `crates/buzz-cli/src/links.rs`, `parse_message_link` | `buzz://message?channel=<uuid>&id=<hex>[&thread=<root>]` deep-link parsing referenced in CLAUDE.md's "Deep Links" section | Rejects unknown query params (including a `relay=` override attempt), userinfo, and fragments — the link may only select channel/event within the CLI's already-configured relay and identity. |
| `crates/buzz-cli/src/error.rs`, `CliError`, `exit_code`, `print_error`, `is_retryable_error` | CLAUDE.md's exit-code table (0/1/2/3/4/5) and "all reads return sig-stripped JSON ... all writes return `{event_id, accepted, message}`" error-shape contract | `print_error`'s JSON envelope (`error`/`message`/`retryable`) is the CLI-wide error contract; `DeliveryUnknown` is deliberately never `retryable`. |
| `crates/buzz-cli/src/client.rs`, `BuzzClient::with_retry_body`, `RETRY_MAX_ATTEMPTS`, `RETRY_IN_MAX_SECS`, `env_duration_secs` | Not directly named in CLAUDE.md, but the transport layer underneath every subcommand's relay call | Retries transient network errors and 429/502/503/504 relay responses up to 3 attempts; per-request/connect timeouts are independently env-configurable. |
| `crates/buzz-acp/src/lib.rs`, `build_mcp_servers` | CLAUDE.md's "Auth env vars ... are auto-injected by the ACP harness into managed agent subprocesses" | Lives outside this crate — cited here because it is the other half of the contract `buzz-cli`'s own env-first config surface depends on being populated. |

## Divergences

Two were found by reading the code directly against `CLAUDE.md`'s prose, not
assumed from the prose alone:

1. **`--format compact` is a global flag, but most command groups ignore
   it.** CLAUDE.md states the flag's *position* correctly ("it goes before
   the subcommand"), and that is true — `format` is parsed on the top-level
   `Cli` struct before `command`. What CLAUDE.md does not say is that the
   dispatch match block in `lib.rs` only forwards `&cli.format` to 5 of the
   21 dispatched command groups (`messages`, `channels`, `users`, `feed`,
   `moderation`); the other 16 (`agents`, `canvas`, `reactions`, `emoji`,
   `dms`, `workflows`, `social`, `notes`, `repos`, `projects`, `patches`,
   `issues`, `pr`, `media`, `upload`, `mem`) parse the flag without error but
   never read it. Passing `--format compact` before an unsupported
   subcommand silently has no effect rather than erroring — a caller cannot
   tell from the CLI's own behavior which groups honor it.
2. **`messages thread --link` accepts a raw deep link directly.** CLAUDE.md's
   "Deep Links" section instructs an agent to "Extract `channel` and `id`
   from the URL query parameters" and then pass `--channel`/`--event`
   explicitly. The actual `Thread` subcommand also accepts `--link
   '<the full buzz://message URL>'` as a mutually-exclusive alternative to
   the two explicit flags, parsed by `links.rs::parse_message_link` — so the
   manual-extraction step CLAUDE.md describes is not strictly necessary; it
   is one valid path, not the only one. This is a capability CLAUDE.md
   under-documents, not a contradiction of what it says.

No other divergence was found in the surface checked above: the exit-code
scheme, the `--kinds` asymmetry between `messages get` and `messages
search`, and the auth-tag/relay-URL/private-key env wiring all match
CLAUDE.md's stated contract exactly, verified against `error.rs`, `lib.rs`,
and `buzz-acp/src/lib.rs` directly rather than assumed from the doc's own
wording.

## Verification

Automated, in-tree: `crates/buzz-cli/src/*.rs` carries 375 `#[test]`/
`#[tokio::test]` functions across `client.rs` (46, including retry/timeout
policy under `tokio::test`'s paused-time control), `error.rs` (exit-code and
retryability mapping), `lib.rs` (CLI parse-shape and mutual-exclusion rules,
including the two `messages thread` tests cited above, plus a
`cli_definition_is_valid` smoke test that runs `Cli::command().debug_assert()`
so a malformed clap definition fails the test suite rather than only
surfacing at runtime), `links.rs` (deep-link parse/build against a golden
fixture shared in spirit with the desktop parser, though not run against the
TypeScript code in the same CI job), and `agent_management.rs` (4 tests,
NIP-OA auth-tag normalization/priority). These run under `just test-unit` /
`cargo test -p buzz-cli`, no external services required.

Manual: `crates/buzz-cli/TESTING.md` is a live-testing runbook exercising
every command group against a running relay + Postgres/Redis stack — the
CLAUDE.md-documented contract's end-to-end behavior is confirmed this way,
not by an automated integration suite that asserts CLAUDE.md's specific
claims (exit codes, `--format` scope, deep-link resolution) as a group.
Nothing in the test suite specifically asserts the CLAUDE.md exit-code table
against a live relay round-trip; the closest automated coverage is
`error.rs`'s unit-level mapping from `CliError` to exit code, which does not
exercise an actual relay response reaching that code.

## Relationships

- part-of: architecture-containers-cli

No `implements` edge: the target this node traces is `CLAUDE.md`'s prose
contract, which carries no corpus node id at this revision (see *Target*).
No `references` edge: no verification/test-strategy corpus node exists yet
for this node to point at as the `Verification` section's backing (the
`test-strategy` template, `#1350` in the corpus roadmap, is not the same as
a merged node this crate's tests could cite).

## Scope and omissions

**This node covers** `buzz-cli`'s realization of `CLAUDE.md`'s documented
agent-facing contract: environment-first auth configuration, the `--format`
global flag and which command groups actually honor it, deep-link
resolution (including the undocumented `--link` shortcut), the exit-code and
JSON-error scheme, the retry/timeout policy underlying every relay call, and
where automated versus manual verification of that contract lives today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-cli`'s responsibility, technology stack, and full inbound/outbound interface inventory | `architecture-containers-cli` (this node's `part-of` target) — not restated here |
| Full per-subcommand behavior for all 22 `Cmd` groups (`crates/buzz-cli/src/commands/*.rs`) | Future per-capability implementation-reference nodes; only representative, CLAUDE.md-relevant rows are covered above |
| Relay-side authorization, storage, and NIP-29 scoping that `buzz-cli`'s requests land on | `buzz-auth`, `buzz-db`, `buzz-relay` — their own container/implementation nodes, not yet written |
| `buzz-dev-mcp`'s embedding of this crate as one multicall personality, and its other (non-`buzz`) personalities | `buzz-dev-mcp`'s own container/implementation node, not yet written |
| `buzz-admin` (the separate operator CLI) | A distinct crate and audience; not this node's subject |
| Whether the desktop TypeScript parsers (`entityLink.ts`, `messageLink.ts`) actually stay in sync with `links.rs` today | Confirmed only that both sides declare the intent and that `links.rs` tests against a shared golden fixture; the TypeScript side's own test run was not executed as part of authoring this node |

**Expected but not verified when this node was written:**

- **Whether every one of the 16 command groups that ignore `--format` do so
  deliberately** (their output has no compact/full-field distinction to make)
  **or as an unfinished rollout of the flag.** Only the dispatch signatures
  were compared; no per-command-group review of whether `--format compact`
  would be meaningful for, say, `agents` or `repos` output was performed.
- **Whether the golden fixture `links.rs` tests against
  (`test-fixtures/entity-links.json`) is actually exercised by a
  corresponding desktop-side test in the same CI job**, keeping the two
  parsers honestly in sync rather than only by shared intent in the module
  doc comment. Not checked against `desktop/`'s own test suite.
- **Whether any command group beyond the ones read in depth here
  (`messages`, `links`, error/retry plumbing) calls a relay path outside
  `client.rs`'s enumerated HTTP/WS surface.** `architecture-containers-cli`
  already flags this as unverified for its own broader interface inventory;
  it is inherited here rather than independently re-checked.
