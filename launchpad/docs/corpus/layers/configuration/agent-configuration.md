---
id: layers-configuration-agent-configuration
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "crates/buzz-agent/src/config.rs's Config::from_env resolves BUZZ_AGENT_PROVIDER via resolve_provider into one of five Provider variants (Anthropic, OpenAi, Databricks, DatabricksV2, OpenRouter); an absent or empty value is a hard startup error ('BUZZ_AGENT_PROVIDER is required'), and an unrecognized value is likewise a startup error naming the value."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "BUZZ_AGENT_MODEL is read once, before provider dispatch, and resolve_model() gives it priority over every provider-specific model variable (ANTHROPIC_MODEL, OPENAI_COMPAT_MODEL, DATABRICKS_MODEL, OPENROUTER_MODEL) when both are present; the code comment states it is 'set by the desktop from the persona/record to express explicit user intent' while the provider-specific vars 'serve as defaults for CLI/standalone use.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "Each Provider variant requires its own API-key/model/base-URL trio at startup except Databricks and DatabricksV2, whose api_key (DATABRICKS_TOKEN) is read with unwrap_or_default() rather than req(), and whose own code comment calls this 'the optional DATABRICKS_TOKEN escape hatch — empty means use OAuth PKCE.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "BUZZ_AGENT_SYSTEM_PROMPT and BUZZ_AGENT_SYSTEM_PROMPT_FILE are mutually exclusive (both set is a startup error); when neither is set, Config::from_env falls back to the compiled-in DEFAULT_SYSTEM_PROMPT constant ('You are buzz-agent. Use the provided tools to act. Tool calls are your only output.')."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "Config::validate() enforces cross-field invariants at startup rather than per-field only: max_context_tokens must exceed max_output_tokens (error names both values and states 'the context window must leave room for the response'), max_history_bytes must be >= 4096 and also >= MAX_PROMPT_BYTES (1_048_576), max_tool_result_text_bytes must fall within 1024..=MAX_TOOL_RESULT_BYTES (8_388_608), and BUZZ_AGENT_THINKING_EFFORT of none or minimal is rejected outright when the resolved provider is pure Anthropic (not DatabricksV2's Anthropic route, which defers to request-time normalization)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "Every BUZZ_AGENT_* numeric/duration/boolean field in Config::from_env is parsed through one shared parse_env() helper that falls back to a hardcoded default on an absent variable and returns a config error naming the key on a present-but-unparseable one; MCP_HOOK_SERVERS is parsed by a dedicated parse_hook_servers_env() into HookServers::None (unset/empty), HookServers::All (bare '*'), or HookServers::Only(names), with unit tests covering all three shapes plus trimming and the '*,foo' non-wildcard edge case."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "BUZZ_AGENT_THINKING_EFFORT accepts none|minimal|low|medium|high|xhigh|max via parse_thinking_effort, and BUZZ_AGENT_THINKING_SUMMARY accepts auto|concise|detailed via parse_thinking_summary; both are pure (env-free) parsing functions with dedicated unit-style doc comments stating the unset/empty behavior (None = provider default; Auto respectively)."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/config.rs"
  - statement: "crates/buzz-agent/src/main.rs calls Config::from_env() to build the agent's configuration; no reload mechanism (SIGHUP handler, admin endpoint, or similar) referencing this Config was found in crates/buzz-agent/src, so every BUZZ_AGENT_* value is fixed for the lifetime of one process the same way layers/configuration/secrets.md documents for buzz-relay's Config::from_env()."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/main.rs"
      - "grep_reload(crates/buzz-agent/src/*.rs) -> no matches for SIGHUP or reload, at commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "crates/buzz-acp/src/config.rs's own module doc comment states 'CLI-first: every option is a CLI flag with env var fallback,' and every field on CliArgs (clap::Parser) declares its env fallback name via #[arg(long, env = \"...\")], so every BUZZ_ACP_* variable below is also reachable as an equivalent --flag; the settings table below cites the env-var form only."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_IDLE_TIMEOUT has no default_value_t on its clap arg; Config::from_args resolves it via DEFAULT_IDLE_TIMEOUT_SECS (900) when neither it nor the deprecated BUZZ_ACP_TURN_TIMEOUT is set, with explicit precedence (idle wins when both are set) and a deprecation warning logged whenever BUZZ_ACP_TURN_TIMEOUT is consulted at all; a resolved value of 0 is rejected up to a 1s floor with a warning rather than a hard error."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_MAX_TURN_DURATION defaults to DEFAULT_MAX_TURN_DURATION_SECS (7200s / 2h) via default_value_t, is floored to 60s with a warning if configured as 0, and is hard-rejected above MAX_TURN_DURATION_CEILING_SECS (604_800s / 7 days) with an error naming both the configured and ceiling values; Config::from_args additionally hard-rejects any configuration where idle_timeout_secs >= max_turn_duration_secs, since the wall-clock cap would then fire before the idle timeout ever could."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_HEARTBEAT_INTERVAL defaults to 0 (disabled) via default_value_t, is hard-rejected as a startup error when configured in the range 1..=9 ('heartbeat interval must be 0 (disabled) or >=10 seconds'), and is silently capped at 86400 (24h) with a warning above that value; BUZZ_ACP_TURN_LIVENESS_SECS defaults to 10 and follows the identical validation shape (reject 1..=4, cap at 86400) via the same code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_RESPOND_TO (default owner-only; other values allowlist, anyone, nobody) gates which authors' events the harness forwards to the agent; when it is set to allowlist, BUZZ_ACP_RESPOND_TO_ALLOWLIST must be non-empty (each entry validated as exactly 64 lowercase hex characters) or Config::from_args returns a startup error; BUZZ_ACP_ALLOWED_RESPOND_TO, when set, is validated entry-by-entry as a known RespondTo mode and then rejects startup if the configured --respond-to is not itself in that allowed set."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_MULTIPLE_EVENT_HANDLING (default steer; other values queue, interrupt, owner-interrupt) is validated against BUZZ_ACP_DEDUP by validate_multiple_event_handling: every mode other than queue requires --dedup=queue, and the combination is a hard startup error otherwise, because DedupMode::Drop would discard events during the cancel-drain window and produce incomplete merged prompts."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_MEMORY defaults to true and BUZZ_ACP_NO_MEMORY defaults to false via clap's conflicts_with, and the resulting memory_enabled field is computed as args.memory && !args.no_memory; the doc comment states memory injection controls only prompt-time <core-memory> rendering in the ACP harness and does not affect the buzz mem CLI or the relay's own acceptance of kind:30174 engrams."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
  - statement: "BUZZ_ACP_AGENTS defaults to 1 and is clap-range-validated to 1..=32; desktop/src-tauri/src/managed_agents/reserved_env_keys.rs's RESERVED_ENV_KEYS list separately rejects any user-supplied override of this specific key at save/spawn time for managed (desktop-launched) agents, with its own comment stating the Desktop 'resolves the effective worker-pool size (applying any per-harness cap) and writes it into launch.policy_env,' so an uncapped override would let a definition bypass a harness-specific worker cap; this restriction applies only inside the desktop's managed-agent path, not to a standalone/CLI buzz-acp invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/config.rs"
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs's RESERVED_ENV_KEYS list also names BUZZ_ACP_RESPOND_TO, BUZZ_ACP_RESPOND_TO_ALLOWLIST, BUZZ_ACP_ALLOWED_RESPOND_TO, BUZZ_ACP_AGENT_OWNER, BUZZ_ACP_EXIT_AFTER_INACTIVITY, BUZZ_ACP_NO_PRESENCE, BUZZ_ACP_AGENT_COMMAND, BUZZ_ACP_AGENT_ARGS, and BUZZ_ACP_MCP_COMMAND as keys a managed-agent's persona/agent env_vars UI cannot override, for reasons the file's own doc comment gives per key group (security gates, code-execution surface, desktop-owned lifetime policy); its own comment states plainly that 'behavior knobs (GOOSE_MODE, BUZZ_ACP_MODEL, BUZZ_ACP_SYSTEM_PROMPT, ...) remain freely overridable' by contrast."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs's own module doc comment states the env-var merge precedence as 'desktop parent env < persona env < agent env (last wins on key collision)' for the BTreeMap<String, String> env_vars carried by both personas and managed-agent definitions, layered in at spawn time by runtime::spawn_agent_child."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "desktop/src-tauri/src/managed_agents/global_config/mod.rs's own doc comment states a second, orthogonal precedence axis for the structured provider/model/preferred_runtime fields (not the free-form env_vars map): 'baked build env < GLOBAL < definition (linked) / instance (legacy) < Buzz-identity', and states that unlike per-agent/persona env (snapshotted at create time), global config is 'live-resolved at spawn/readiness/deploy.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/global_config/mod.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs's DERIVED_PROVIDER_MODEL_ENV_KEYS constant (GOOSE_MODEL, GOOSE_PROVIDER, BUZZ_AGENT_MODEL, BUZZ_AGENT_PROVIDER) names env keys that validate_global_config (in global_config/mod.rs) and comparable per-agent validation reject if set directly as env_vars entries, because the code comment states they 'would shadow the structured provider/model fields and break provider/model resolution' and users 'must use the structured fields instead.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
      - "desktop/src-tauri/src/managed_agents/global_config/mod.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs's is_well_formed_env_key requires the POSIX shape [A-Za-z_][A-Za-z0-9_]*, and its own doc comment explains this closes a bypass where a key literally containing '=' (e.g. 'BUZZ_AUTH_TAG=x') would, via Rust's Command::env, land in the child process's environ block as BUZZ_AUTH_TAG=x=forged, making getenv(\"BUZZ_AUTH_TAG\") return the attacker-supplied value despite BUZZ_AUTH_TAG itself being on the reserved-key list."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "MAX_ENV_VALUE_BYTES (32 KiB per value) and MAX_ENV_TOTAL_BYTES (256 KiB total payload) in desktop/src-tauri/src/managed_agents/env_vars.rs bound every persisted persona/agent/global env_vars map; validate_user_env_keys enforces the per-value cap at save time, and a separate runtime path silently drops (rather than truncates) any oversize value with a logged warning."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "launchpad/docs/corpus/layers/configuration/secrets.md (id layers-configuration-secrets, drafted by sibling task #1058, not yet merged on origin/launchpad) already catalogues BUZZ_PRIVATE_KEY, BUZZ_AUTH_TAG, the BUZZ_ACP_PRIVATE_KEY -> BUZZ_PRIVATE_KEY legacy-alias rename, and the desktop's reserved-key stripping mechanism as the secret-shaped subset of this same buzz-agent/buzz-acp/managed_agents configuration surface; this node defers to it for those rows rather than re-cataloguing them, and cannot declare a relationships edge to it because it is not merged on origin/launchpad at the recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "sibling task launchpad-26/buzz#1058's own worktree (task-1058-configuration-secrets, branch task/1058-configuration-secrets), read directly by this node's author; not a citable in-repo path since that file is uncommitted to origin/launchpad at the recorded revision"
  - statement: "launchpad/docs/corpus/architecture/containers/agent-runtime.md (id architecture-containers-agent-runtime, merged on origin/launchpad) documents buzz-acp, buzz-agent and buzz-dev-mcp's composition, responsibilities and lifecycle at architecture-container altitude — what each crate is and does — distinct from this node's configuration-catalog altitude covering how each crate's behavior is tuned via environment variables."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "This task (launchpad-26/buzz#1051) was dispatched as one worker in a batch run against Feature #611, alongside sibling configuration-catalog tasks #1052-#1059 covering other configuration surfaces (defaults, desktop, environment, mobile, relay, secrets, validation); none of those sibling nodes are merged on origin/launchpad at the recorded revision, so none is declared as a relationships target here, and the task brief itself directed this node to stay scoped to buzz-agent/buzz-acp/managed_agents env-config specifically to avoid duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "task brief dispatching launchpad-26/buzz#1051 as part of the Feature #611 batch run"
  - statement: "Whether ANTHROPIC_API_KEY, OPENAI_COMPAT_API_KEY, OPENROUTER_API_KEY and DATABRICKS_TOKEN (buzz-agent's own LLM-provider credential variables) fall under sibling task #1058's configuration-secrets scope was not settled by that node's own drafted text (per the TEAM_KNOWLEDGE entry above, its secrets.md names BUZZ_PRIVATE_KEY/BUZZ_S3_*/BUZZ_GIT_HOOK_HMAC_SECRET/BUZZ_RELAY_PRIVATE_KEY/BUZZ_AUTH_TAG but not these four provider-credential names); this node includes them as its own rows, marked Secret: yes, as a deliberate scope choice rather than a silent assumption, since they are genuinely part of buzz-agent's configuration surface per its own from_env dispatch and no other node's evidence claims them."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-agent/src/config.rs"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-containers-agent-runtime
  - type: implements
    target: corpus-template-configuration
---

# Buzz: agent configuration

This node catalogues the **agent-specific configuration surface** of Buzz's own
code — the environment variables (and equivalent CLI flags) that tune how a
standalone `buzz-agent` process behaves, how the `buzz-acp` harness spawns and
supervises an agent subprocess, and how the desktop's `managed_agents` module
layers env-var and structured-field overrides on top of both. It applies to
every context these components run in: a bare `buzz-agent`/`buzz-acp`
invocation (local development, CI, a hand-run CLI), and a desktop-managed
local or remote agent instance, since the settings below tune agent behavior
identically regardless of what launched the process.

## Settings — `buzz-agent` (`crates/buzz-agent/src/config.rs`, `Config::from_env`)

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_AGENT_PROVIDER` | enum: `anthropic`\|`openai`\|`databricks`\|`databricks_v2`\|`openrouter` | none | yes | no | Selects the LLM provider; absent or unrecognized is a startup error. |
| `BUZZ_AGENT_MODEL` | string | none | no | no | Universal model-id override; wins over every provider-specific model var below when both are set. |
| `ANTHROPIC_MODEL` / `OPENAI_COMPAT_MODEL` / `DATABRICKS_MODEL` / `OPENROUTER_MODEL` | string | none | yes, unless `BUZZ_AGENT_MODEL` is set | no | Provider-specific model id; whichever one matches the resolved provider is required if `BUZZ_AGENT_MODEL` is absent. |
| `ANTHROPIC_API_KEY` / `OPENAI_COMPAT_API_KEY` / `OPENROUTER_API_KEY` | string | none | yes, for the matching provider | yes | Provider API credential; required (`req()`) for Anthropic, OpenAI-compat and OpenRouter. |
| `DATABRICKS_TOKEN` | string | empty (falls back to OAuth PKCE) | no | yes | Optional static bearer for Databricks/DatabricksV2; empty means the runtime negotiates OAuth PKCE instead. |
| `ANTHROPIC_BASE_URL` / `OPENAI_COMPAT_BASE_URL` / `OPENROUTER_BASE_URL` / `DATABRICKS_HOST` | URL string | `https://api.anthropic.com` / `https://api.openai.com/v1` / `https://openrouter.ai/api/v1` / none (Databricks host is required) | no (Databricks: yes) | no | Overrides the provider's API base URL; `DATABRICKS_HOST` has no default and is a startup error if absent when a Databricks provider is selected. |
| `OPENAI_COMPAT_API` | enum: `auto`\|`chat`\|`responses` | `auto` | no | no | Selects which OpenAI-family HTTP surface to call; only read when the resolved provider is OpenAI-compat. `auto` picks Responses for `*.openai.com` hosts, Chat Completions otherwise. |
| `ANTHROPIC_API_VERSION` | string | `2023-06-01` | no | no | Anthropic Messages API version header value. |
| `DATABRICKS_MODEL_FILTER` | comma-separated `*`/`?` glob patterns | none (no filtering) | no | no | Restricts the Databricks model catalog exposed to callers; a nonblank value with zero valid patterns is a startup error. |
| `BUZZ_AGENT_SYSTEM_PROMPT` / `BUZZ_AGENT_SYSTEM_PROMPT_FILE` | string / file path | compiled-in `DEFAULT_SYSTEM_PROMPT` | no | no | System prompt text, inline or from a file; setting both is a startup error. |
| `BUZZ_AGENT_MAX_ROUNDS` | integer | `0` (unbounded) | no | no | Caps LLM/tool round-trips per turn. |
| `BUZZ_AGENT_MAX_OUTPUT_TOKENS` | integer | `65536` | no | no | Per-request output token cap; must be >=1 and strictly less than `BUZZ_AGENT_MAX_CONTEXT_TOKENS`. |
| `BUZZ_AGENT_MAX_TOKEN_RECOVERIES` | integer | `3` | no | no | Retries after a truncated-output response; `0` disables truncation recovery. |
| `BUZZ_AGENT_LLM_TIMEOUT_SECS` | integer (seconds) | `240` | no | no | Per-LLM-call timeout; must be >=1. |
| `BUZZ_AGENT_TOOL_TIMEOUT_SECS` | integer (seconds) | `660` | no | no | Per-tool-call timeout; must be >=1. |
| `BUZZ_AGENT_MCP_INIT_TIMEOUT_SECS` | integer (seconds) | `30` | no | no | MCP subprocess initialization timeout; must be >=1. |
| `BUZZ_AGENT_MCP_RESTART_MAX_ATTEMPTS` / `_BASE_MS` / `_MAX_MS` | integers | `3` / `500` / `30000` | no | no | MCP subprocess restart backoff policy (attempts, base and max backoff); max must be >= base and attempts must be >=1. |
| `BUZZ_AGENT_MAX_SESSIONS` | integer | `usize::MAX` (unbounded) | no | no | Caps concurrently tracked ACP sessions. |
| `BUZZ_AGENT_MAX_LINE_BYTES` | integer (bytes) | `4194304` (4 MiB) | no | no | Max single-line size read from an MCP subprocess's stdout; must be >=1024. |
| `BUZZ_AGENT_MAX_HISTORY_BYTES` | integer (bytes) | `16777216` (16 MiB) | no | no | Max conversation-history size retained; must be >=4096 and >= `MAX_PROMPT_BYTES` (1 MiB). |
| `BUZZ_AGENT_MAX_TOOL_RESULT_TEXT_BYTES` | integer (bytes) | `51200` (50 KiB) | no | no | Per-tool-result text cap before middle-elision; must fall within 1024..=8388608. Images are exempt and bounded separately. |
| `BUZZ_AGENT_MAX_CONTEXT_TOKENS` | integer | `200000` | no | no | Provider context-window size used to gate proactive context handoff/compaction; must exceed `BUZZ_AGENT_MAX_OUTPUT_TOKENS`. |
| `BUZZ_AGENT_MAX_HANDOFFS` | integer | `10` | no | no | Caps context-handoff (compaction) attempts within a single turn. |
| `BUZZ_AGENT_MAX_PARALLEL_TOOLS` | integer | `8` | no | no | Caps simultaneously in-flight tool calls; must be >=1. |
| `BUZZ_AGENT_MAX_PENDING_PERMISSIONS` | integer | `32` | no | no | Process-wide cap on outstanding permission-broker asks; must be >=1. |
| `BUZZ_AGENT_PERMISSION_TIMEOUT_SECS` | integer (seconds) | `330` | no | no | Absolute deadline for one permission ask; must be >=1. Chosen to outlast a 300s client auto-deny. |
| `BUZZ_AGENT_HOOK_TIMEOUT_MS` | integer (ms) | `2500` | no | no | Timeout for one `_Stop`/hook-server call. |
| `BUZZ_AGENT_STOP_MAX_REJECTIONS` | integer | `3` | no | no | Max `_Stop`-hook rejections honored per prompt; `0` disables `_Stop` hooks entirely. |
| `BUZZ_AGENT_REQUIRE_REPLY` | boolean (`0`/`1`) | `0` (off) | no | no | Reminds the model to publish before ending a turn with no recognized reply attempt. |
| `MCP_HOOK_SERVERS` | `none` \| `*` \| comma-separated names | unset = none | no | no | Hook-server allowlist; `*` enables all, an empty/unset value disables hooks entirely. |
| `BUZZ_AGENT_NO_HINTS` | boolean (`0`/`1`) | `0` (hints on) | no | no | Disables the agent's built-in hint system when set to a nonzero value. |
| `BUZZ_AGENT_THINKING_EFFORT` | enum: `none`\|`minimal`\|`low`\|`medium`\|`high`\|`xhigh`\|`max` | unset (provider default; no thinking config sent) | no | no | Reasoning/thinking effort; `none`/`minimal` are a hard startup error for a pure-Anthropic provider. |
| `BUZZ_AGENT_THINKING_SUMMARY` | enum: `auto`\|`concise`\|`detailed` | `auto` | no | no | Reasoning-summary verbosity on the OpenAI Responses route only; ignored elsewhere. |
| `BUZZ_AGENT_PROMPT_CACHING` | boolean (`0`/`1`) | `1` (on) | no | no | Enables Anthropic `cache_control` breakpoints on the stable prompt prefix and conversation tail. |

## Settings — `buzz-acp` (`crates/buzz-acp/src/config.rs`, `CliArgs`/`Config::from_args`)

Every variable below is also reachable as an equivalent `--flag` (CLI-first
with env-var fallback, per the crate's own module doc comment); the table
cites the env-var form only.

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_RELAY_URL` | WebSocket URL | `ws://localhost:3000` | no | no | Relay the harness connects to. |
| `BUZZ_ACP_AGENT_OWNER` | 64-char hex pubkey | none | no | no | Owner pubkey used for the `owner-only`/`owner-interrupt` gates. |
| `BUZZ_ACP_AGENT_COMMAND` | string | `goose` | no | no | Agent binary to spawn. Desktop-reserved: `managed_agents` rejects a user override of this key for desktop-launched agents (code-execution surface). |
| `BUZZ_ACP_AGENT_ARGS` | comma-delimited list | `acp` | no | no | Arguments passed to the agent binary. Desktop-reserved, same rationale as `BUZZ_ACP_AGENT_COMMAND`. |
| `BUZZ_ACP_MCP_COMMAND` | string | `""` | no | no | Dev-MCP binary/command the harness wires in for the agent. Desktop-reserved, same rationale. |
| `BUZZ_ACP_IDLE_TIMEOUT` | integer (seconds) | `900` (via `DEFAULT_IDLE_TIMEOUT_SECS`) | no | no | Max silence before killing a turn; resets on agent stdout activity. A resolved `0` is floored to `1` with a warning. |
| `BUZZ_ACP_MAX_TURN_DURATION` | integer (seconds) | `7200` (2h) | no | no | Absolute wall-clock cap per turn; floored to `60` at `0`, hard-rejected above `604800` (7 days), and must exceed the resolved idle timeout. |
| `BUZZ_ACP_TURN_TIMEOUT` | integer (seconds) | none | no | no | Deprecated alias for `BUZZ_ACP_IDLE_TIMEOUT`; ignored (with a warning) whenever the latter is also set. |
| `BUZZ_ACP_SYSTEM_PROMPT` / `BUZZ_ACP_SYSTEM_PROMPT_FILE` | string / file path | none | no | no | Harness-level system prompt override, inline or from file; mutually exclusive via `clap`. |
| `BUZZ_ACP_AGENTS` | integer, range 1..=32 | `1` | no | no | Number of parallel agent subprocesses. Desktop-reserved: `managed_agents` rejects a user override so a definition cannot bypass a Desktop-applied per-harness worker cap; unrestricted for a standalone/CLI invocation. |
| `BUZZ_ACP_HEARTBEAT_INTERVAL` | integer (seconds) | `0` (disabled) | no | no | Self-prompt heartbeat interval; values `1`-`9` are a startup error, values above `86400` are capped with a warning. |
| `BUZZ_ACP_TURN_LIVENESS_SECS` | integer (seconds) | `10` | no | no | Per-turn liveness ping interval (crash backstop, distinct from the heartbeat above); same `1`-`4`-error / `86400`-cap validation shape. |
| `BUZZ_ACP_HEARTBEAT_PROMPT` / `_FILE` | string / file path | none | no | no | Heartbeat prompt text, inline or from file; mutually exclusive. |
| `BUZZ_ACP_INITIAL_MESSAGE` | string | none | no | no | Message sent to the agent once at harness startup. |
| `BUZZ_ACP_SUBSCRIBE` | enum: `mentions`\|`all`\|`config` | `mentions` | no | no | Event-subscription mode; `config` mode ignores `--kinds`/`--channels`/`--no-mention-filter` (each logged as a warning if also set). |
| `BUZZ_ACP_KINDS` | comma-delimited integers | none (kind-scope default) | no | no | Overrides the subscribed Nostr event kinds; ignored in `config` mode. |
| `BUZZ_ACP_CHANNELS` | comma-delimited UUIDs | none (all discovered channels) | no | no | Restricts subscription to specific channels; an entry that fails UUID parsing is dropped with a warning. |
| `BUZZ_ACP_NO_MENTION_FILTER` | boolean flag | off | no | no | Disables the @-mention requirement in `mentions`/`all` subscribe modes. |
| `BUZZ_ACP_CONFIG` | file path | `./buzz-acp.toml` | no | no | TOML rules file consulted only in `config` subscribe mode; more than 100 rules is a startup error. |
| `BUZZ_ACP_DEDUP` | enum: `drop`\|`queue` | `queue` | no | no | Whether concurrent per-channel events are dropped or queued while a turn is in flight. |
| `BUZZ_ACP_MULTIPLE_EVENT_HANDLING` | enum: `queue`\|`steer`\|`interrupt`\|`owner-interrupt` | `steer` | no | no | Mid-turn @-mention handling; every mode but `queue` requires `BUZZ_ACP_DEDUP=queue` or startup fails. |
| `BUZZ_ACP_NO_IGNORE_SELF` | boolean flag | off (self events ignored) | no | no | Stops the harness from ignoring its own published events. |
| `BUZZ_ACP_CONTEXT_MESSAGE_LIMIT` | integer, range 0..=100 | `12` | no | no | Max prior-thread messages fetched for context; `0` disables automatic context fetching. |
| `BUZZ_ACP_MAX_TURNS_PER_SESSION` | integer | `0` (disabled) | no | no | Proactive session rotation after N turns; `0` rotates only on provider-signalled `MaxTokens`/`MaxTurnRequests`. |
| `BUZZ_ACP_NO_PRESENCE` | boolean flag | off (presence on) | no | no | Disables automatic online/offline presence publishing. Desktop-reserved, same class as the lifetime-policy keys below. |
| `BUZZ_ACP_NO_TYPING` | boolean flag | off (typing indicator on) | no | no | Disables the typing indicator while the agent processes a turn. |
| `BUZZ_ACP_MEMORY` / `BUZZ_ACP_NO_MEMORY` | boolean / boolean | `true` / `false` | no | no | NIP-AE core-memory prompt injection toggle; mutually exclusive via `clap`. Controls prompt-time injection only, not the `buzz mem` CLI or the relay's own engram acceptance. |
| `BUZZ_ACP_NO_BASE_PROMPT` | boolean flag | off (base prompt on) | no | no | Disables the compiled-in `<base>` platform-context prompt section. |
| `BUZZ_ACP_BASE_PROMPT_FILE` | file path | none (compiled-in default) | no | no | Custom base-prompt file, capped at 1 MiB; mutually exclusive with `--no-base-prompt`. |
| `BUZZ_ACP_MODEL` | string | none (agent/adapter default) | no | no | Desired model id, applied to every new ACP session after creation. |
| `BUZZ_ACP_EFFORT_LEVEL` | string | none | no | no | Persisted effort-level value applied via `session/set_config_option` if the adapter advertises a `thought_level` capability; silently ignored otherwise. |
| `BUZZ_ACP_SESSION_TITLE` | string | none | no | no | Session title sent out-of-band in `session/new` `_meta`; sanitized and capped at 80 characters. |
| `BUZZ_ACP_PERMISSION_MODE` | enum: `default`\|`auto`\|`acceptEdits`\|`bypassPermissions`\|`dontAsk`\|`plan` | `bypass-permissions` | no | no | Permission mode applied via `session/set_config_option` for adapters that support `configId: "mode"`. |
| `BUZZ_ACP_RESPOND_TO` | enum: `owner-only`\|`allowlist`\|`anyone`\|`nobody` | `owner-only` | no | no | Inbound author gate. Desktop-reserved: `managed_agents` rejects a user override so a saved gate cannot diverge from a running one; unrestricted for a standalone/CLI invocation. |
| `BUZZ_ACP_RESPOND_TO_ALLOWLIST` | comma-delimited 64-char hex pubkeys | none | conditional — required when `--respond-to=allowlist` | no | Allowlist entries for the `allowlist` gate mode; each validated as exactly 64 hex chars. Desktop-reserved, same class as `BUZZ_ACP_RESPOND_TO`. |
| `BUZZ_ACP_ALLOWED_RESPOND_TO` | comma-delimited mode names | none (all modes allowed) | no | no | Restricts which `--respond-to` values this deployment permits; the configured mode must be in this set or startup fails. Desktop-reserved, same class as `BUZZ_ACP_RESPOND_TO`. |
| `BUZZ_ACP_TEAM_INSTRUCTIONS` | string | none | no | no | Team-owned instructions layered after the system prompt and before agent memory. |
| `BUZZ_ACP_RELAY_OBSERVER` | boolean flag | `false` | no | no | Publishes encrypted ACP observer frames over the relay. |
| `BUZZ_ACP_EXIT_AFTER_INACTIVITY` | integer (seconds) | `0` (disabled) | no | no | Self-termination after N seconds with no dispatched events and no in-flight turn. Desktop-reserved: prevents a definition from disabling a Desktop-set lifetime bound. |
| `BUZZ_ACP_LAZY_POOL` | boolean flag | `false` | no | no | Defers ACP/LLM subprocess startup until the harness connects and subscribes. |
| `BUZZ_ACP_IDLE_POOL_SLEEP` | integer (seconds) | `0` (disabled) | no | no | Idle-teardown window for a woken lazy pool; only meaningful with `--lazy-pool`. Desktop-reserved, same rationale as `BUZZ_ACP_EXIT_AFTER_INACTIVITY`. |

## Precedence and overrides — `managed_agents` (`desktop/src-tauri/src/managed_agents`)

The desktop's `managed_agents` module does not introduce its own named
settings distinct from the two tables above; instead it layers **two
independent override axes** on top of whichever `buzz-agent`/`buzz-acp`
process it spawns:

1. **Free-form `env_vars` overrides** (`env_vars.rs`). Precedence, per that
   file's own doc comment: *desktop parent env < persona env < agent env*
   (last wins on key collision), applied at spawn time by
   `runtime::spawn_agent_child`. Every key is validated at save time
   (`validate_user_env_keys`): POSIX-shaped (`[A-Za-z_][A-Za-z0-9_]*`, closing
   a `Command::env` bypass the file's own comment documents in detail), not on
   the reserved-key list (`reserved_env_keys.rs`, cataloguing which
   `BUZZ_ACP_*` keys are desktop-reserved is folded into the settings table
   above rather than repeated here), value size capped at 32 KiB
   (`MAX_ENV_VALUE_BYTES`), and total payload capped at 256 KiB
   (`MAX_ENV_TOTAL_BYTES`).
2. **Structured `provider`/`model`/`preferred_runtime` fields**
   (`global_config/mod.rs`, `effective_config/mod.rs`). A second, orthogonal
   precedence axis for these three fields specifically: *baked build env <
   GLOBAL < definition (linked) / instance (legacy) < Buzz-identity*, and
   unlike `env_vars` (snapshotted at record-create time), this axis is
   **live-resolved at spawn/readiness/deploy** — editing the global default
   takes effect on every agent's next restart with no delete-and-respawn
   required.

The two axes are kept from colliding by `DERIVED_PROVIDER_MODEL_ENV_KEYS`
(`GOOSE_MODEL`, `GOOSE_PROVIDER`, `BUZZ_AGENT_MODEL`, `BUZZ_AGENT_PROVIDER`):
these keys are rejected if set directly in any `env_vars` map, because doing
so would shadow the structured fields above and desynchronize the two
resolution paths. A user who wants to set the model or provider must use the
structured fields, never a raw `env_vars` entry naming one of these four keys
directly.

## Litmus test

Every row in both settings tables above is genuinely deploy-varying per the
Twelve-Factor litmus test — "whether the codebase could be made open source at
any moment, without compromising any credentials." One category was
considered and excluded because it fails the test in the *other* direction:
the numeric parsing/validation helpers themselves (`parse_env`,
`parse_hook_servers`, `validate_multiple_event_handling`, `Config::validate`'s
cross-field checks) are compiled-in logic, not deploy-varying values, and are
named here only to explain what a row's constraint means — they are not rows
in either table. `MAX_ENV_VALUE_BYTES`/`MAX_ENV_TOTAL_BYTES` and
`DEFAULT_SYSTEM_PROMPT`/`DEFAULT_IDLE_TIMEOUT_SECS`/etc. are likewise compiled
constants, not settings themselves — they are cited above only as the
*default value* half of a genuinely deploy-varying row.

## Secrets discipline

No row above quotes a live credential value. `ANTHROPIC_API_KEY`,
`OPENAI_COMPAT_API_KEY`, `OPENROUTER_API_KEY` and `DATABRICKS_TOKEN` are
marked `Secret: yes` and each row names only the environment variable and the
code path that reads it (`crates/buzz-agent/src/config.rs`'s provider-dispatch
match arms) — never a value, real or placeholder. `BUZZ_PRIVATE_KEY`,
`BUZZ_AUTH_TAG`, and every other identity/credential variable this same
surface touches are deliberately **not** rows in this node — they are
`layers/configuration/secrets.md`'s subject (sibling task #1058, drafted but
not yet merged), and re-cataloguing them here would duplicate that node's
canonical claims once it lands.

## Boundary

This node does not describe:

- **Identity and secret-shaped variables** across this same surface
  (`BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, `BUZZ_ACP_PRIVATE_KEY`, and the
  desktop's reserved-key rejection mechanism in depth) — that is
  `layers/configuration/secrets.md`'s subject (sibling task #1058), not yet
  merged; this node's *Secrets discipline* section above names the boundary
  explicitly.
- **The agent-runtime container's own composition, responsibilities and
  lifecycle** (what `buzz-acp`, `buzz-agent` and `buzz-dev-mcp` each *do*, and
  how `sprig` packages them) — that is
  `architecture/containers/agent-runtime.md`'s subject, at a different
  altitude (architecture, not configuration).
- **Non-agent configuration surfaces** owned by sibling Feature #611 tasks:
  configuration defaults generally (#1052), desktop application settings
  outside `managed_agents` (#1053), general environment/deploy configuration
  (#1054), mobile app configuration (#1056), the relay's own `buzz-relay`
  configuration surface (#1057, already documented for secrets in
  `secrets.md`), and configuration validation mechanics generally (#1059).
- **`buzz-persona`'s persona-pack resolution** (how `persona_env_vars` is
  populated from a resolved pack before being layered into a spawn) — this
  node documents only the env-var merge precedence once populated, not the
  pack-resolution algorithm itself, which is a separate concept with no
  corpus node found for it at the recorded revision.
- **The parsing/validation implementation in exhaustive depth** — both
  settings tables cite the specific validation rules each row is subject to,
  but the full source of `Config::from_args`/`Config::from_env`/
  `Config::validate` (well beyond 500 combined lines) is not reproduced;
  an `implementation` node describing either function in full, should one be
  authored, would `references` this node rather than duplicate it.
- **Any node-specific exclusion beyond the above** — none found.

## Relationships

- **references** → `architecture-containers-agent-runtime` — the merged node
  documenting what `buzz-acp`, `buzz-agent` and `buzz-dev-mcp` each are and do,
  at architecture-container altitude, distinct from this node's
  configuration-catalog altitude. Loose coupling per
  `relationships.schema.json`'s directionality for `references` ("source cites
  target as supporting context; no ownership or currency dependency
  implied") — this node's settings tables stay accurate even if that node's
  architecture description is later revised.
- **implements** → `corpus-template-configuration` — this node is an instance
  of that template, per `relationships.schema.json`'s own worked example for
  `implements` ("a template instance of a standard").
- **Checked and not declared:** no relationship to
  `layers/configuration/secrets.md` (sibling task #1058) or to any of sibling
  tasks #1052-#1057, #1059 (other configuration surfaces) — all are open,
  unmerged draft PRs at the recorded revision, and `AGENTS.md` step 9 requires
  resolving targets against `origin/launchpad`, not this worktree.

## Scope and omissions

**This node covers** the agent-specific, non-secret configuration surface of
`buzz-agent`'s `Config::from_env`, `buzz-acp`'s CLI/env `Config::from_args`,
and the desktop `managed_agents` module's two independent override axes
(free-form `env_vars` precedence and structured provider/model precedence)
that sit on top of both — which settings qualify as configuration under the
Twelve-Factor litmus test, their type/default/required/secret/effect per the
tables above, which `BUZZ_ACP_*` keys the desktop reserves against user
override and why, and the mechanism (`DERIVED_PROVIDER_MODEL_ENV_KEYS`) that
keeps the two `managed_agents` override axes from colliding.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Identity/secret-shaped variables across this same surface (`BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, etc.) | `layers/configuration/secrets.md`, sibling task #1058, drafted but not yet merged |
| `buzz-acp`/`buzz-agent`/`buzz-dev-mcp`'s composition, responsibilities and lifecycle | `architecture/containers/agent-runtime.md`, merged |
| Other configuration surfaces (defaults, desktop-general, environment, mobile, relay, validation) | sibling tasks #1052-#1054, #1056, #1057, #1059, not yet merged |
| `buzz-persona`'s pack-resolution algorithm that populates `persona_env_vars` before spawn | corpus's `implementation`/`capabilities` surface, no specific node found for it |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Whether the ownership of `ANTHROPIC_API_KEY`/`OPENAI_COMPAT_API_KEY`/`OPENROUTER_API_KEY`/`DATABRICKS_TOKEN` between this node and `secrets.md` is genuinely settled | Neither node's evidence settles it; this node claims them as a deliberate, disclosed choice (see evidence ledger) rather than a silent assumption |

**Expected but not verified when this node was written:**

- **Whether `layers/configuration/secrets.md` (sibling #1058) will, once
  merged, claim `ANTHROPIC_API_KEY`/`OPENAI_COMPAT_API_KEY`/
  `OPENROUTER_API_KEY`/`DATABRICKS_TOKEN` for itself was not checked against
  its final merged text**, only against the draft read from its own working
  worktree at this node's recorded revision. If it does, this node's rows for
  those four variables should be reconciled (deduplicated or cross-referenced)
  in a follow-up edit rather than left duplicated silently.
- **Whether every `BUZZ_ACP_*` CLI flag was individually re-verified against
  a live `--help` run** was not checked; all rows above were read directly
  from `crates/buzz-acp/src/config.rs`'s `clap` attribute macros rather than
  from generated `--help` output, so a `clap` attribute that resolves
  differently than its literal declaration (a custom `value_parser` edge
  case, for instance) would not be caught by this node's evidence.
- **Whether `buzz-persona`'s resolution algorithm populates any additional
  env vars beyond the ones named in `buzz-acp/src/config.rs`'s own doc
  comments** (`GOOSE_PROVIDER`, `GOOSE_MODEL`, `BUZZ_AGENT_MODEL`) was not
  independently traced through `crates/buzz-persona/src`; this node reports
  only what `buzz-acp`'s own comments name as persona-populated.
- **Whether a Flutter/mobile-launched agent (if one exists) uses the same
  `buzz-agent`/`buzz-acp` env-var surface or a distinct one** was not checked;
  `mobile/` was not inspected for this node, and sibling task #1056
  (mobile-configuration) is the node expected to settle it.

Back to the corpus root: [`launchpad/docs/corpus/README.md`](../../../README.md).
