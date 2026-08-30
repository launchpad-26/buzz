---
id: layers-configuration-environment-configuration
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The repository root's .env.example documents relay, database, Redis, Typesense, git, S3, media-admission, ephemeral-channel, logging/tracing, and ACP-harness environment variables in named sections, with most settings commented out to show their default and only a minimal set of variables (DATABASE_URL, PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE, REDIS_URL, TYPESENSE_API_KEY, TYPESENSE_URL, BUZZ_BIND_ADDR, RELAY_URL, BUZZ_S3_ENDPOINT/ACCESS_KEY/SECRET_KEY/BUCKET/REGION/ADDRESSING_STYLE, RUST_LOG) left active by default."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "The repository's .gitignore excludes .env, .env.local and .env.*.local from version control while .env.example (placeholder/dev-only values) is committed at the repository root."
    entry_class: FACT
    evidence:
      - ".gitignore"
      - ".env.example"
  - statement: "The root AGENTS.md's 'Agent CLI (buzz-cli)' section states that BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY and BUZZ_AUTH_TAG are auto-injected by the ACP harness into managed agent subprocesses, and that in development these must be set manually."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "crates/buzz-relay/src/config.rs's Config::from_env reads BUZZ_BIND_ADDR (default \"0.0.0.0:3000\"), DATABASE_URL (default \"postgres://buzz:buzz_dev@localhost:5432/buzz\", matching .env.example's dev value), READ_DATABASE_URL (unset/blank keeps all reads on the writer), REDIS_URL (default \"redis://localhost:6379\"), BUZZ_REDIS_POOL_SIZE (default 16, non-positive values fall back to the default), BUZZ_DB_POOL_SIZE (default 50, same fallback rule) and RELAY_URL (default \"ws://localhost:3000\") via std::env::var, each with the same default the code falls back to when the variable is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/config.rs's Config::from_env treats BUZZ_REPLICA_HEAD_MAX_AGE_SECS as a hard startup error (not a silently-honoured alias) because the replacement variable BUZZ_REPLICA_READ_MAX_AGE_MS is denominated in milliseconds, not seconds, and honouring the old name unchanged would silently apply a budget 1000x larger than intended."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/config.rs's BUZZ_DRAIN_JITTER_MS parsing treats an empty or whitespace-only value the same as an unset one (jitter off, value 0), so setting the variable to the empty string is a documented, valid kill switch rather than a parse failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs's RESERVED_ENV_KEYS constant lists environment variable keys (including BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG, BUZZ_API_TOKEN, BUZZ_RELAY_URL, BUZZ_ACP_AGENT_COMMAND, BUZZ_ACP_AGENT_ARGS, BUZZ_ACP_AGENTS, BUZZ_ACP_RESPOND_TO and its allowlist variants) that a managed agent's persona/agent env_vars UI must not override, grouped in the source's own comments into three categories: identity/secrets, code-execution surface, and security gates; the same file is include!'d into both build.rs (compile-time bake rejection) and env_vars.rs (save-time validation and spawn-time filtering) so both checks share one list."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/reserved_env_keys.rs"
  - statement: "desktop/src-tauri/src/managed_agents/readiness.rs's resolve_effective_agent_env_with_def assembles a managed agent's effective process environment in six layers, applied in this order so each later layer overrides the previous on key collision: (1) baked build defaults (compile-time floor, empty in OSS builds), (2) runtime metadata env vars derived from the record's resolved model/provider, (2b) the harness definition's own author-supplied default env, (3a) global env vars (the lowest user-settable layer), (3b) live persona env, then the record's own per-agent env_vars (last-wins)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/readiness.rs"
  - statement: "desktop/src-tauri/src/managed_agents/runtime.rs's spawn_agent_child writes the six-layer descriptor.env map onto the spawned std::process::Command last, after Buzz's own identity and security-gate variables (BUZZ_PRIVATE_KEY, BUZZ_RELAY_URL, BUZZ_AUTH_TAG, the inbound-author respond-to gate) have already been written; this is safe because reserved keys were already stripped out of descriptor.env by the same is_reserved_env_key filter used for save-time validation, not because of the write order itself."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
  - statement: "desktop/src-tauri/src/managed_agents/agent_env.rs's baked_build_env reads three compile-time option_env! values (BUZZ_DESKTOP_BUILD_BUZZ_AGENT_PROVIDER, BUZZ_DESKTOP_BUILD_BUZZ_AGENT_MODEL, BUZZ_DESKTOP_BUILD_AGENT_ENV, the last base64-encoded and newline-delimited) and returns an empty map when none are set, which is always the case for OSS builds; internal builds (buzz-releases) are the only builds that bake values into these."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/agent_env.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs's validate_user_env_keys rejects malformed keys (must match [A-Za-z_][A-Za-z0-9_]*), rejects any key in RESERVED_ENV_KEYS case-insensitively, rejects values containing NUL bytes, caps a single value at MAX_ENV_VALUE_BYTES (32 KiB) and the total key+value payload at MAX_ENV_TOTAL_BYTES (256 KiB)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs's is_safe_to_reveal is a default-deny allowlist for displaying an env var's value verbatim in the UI: only BUZZ_AGENT_PROVIDER, BUZZ_AGENT_MODEL, BUZZ_AGENT_THINKING_EFFORT, BUZZ_AGENT_THINKING_SUMMARY, DATABRICKS_HOST and DATABRICKS_MODEL are shown; every other key is masked."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "launchpad/AGENT_PR_TEMPLATE.md's Verification checklist includes the unchecked box 'No secrets, keys, tokens or hostnames were added to tracked files', applied to every agent-authored pull request including one adding this corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/AGENT_PR_TEMPLATE.md"
  - statement: "The six-layer desktop managed-agent env precedence configures the environment of a spawned agent subprocess, which is itself environment-variable-based configuration of a Buzz-launched process (distinct from the relay's own process env), so it belongs in this node's scope rather than being out of scope as a purely desktop-UI concern."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/managed_agents/readiness.rs"
      - "desktop/src-tauri/src/managed_agents/runtime.rs"
    confidence: 0.8
  - statement: "Issue #1054's Objective describes this document as 'the single canonical configuration node for environment configuration', and this dispatch batch runs four sibling configuration tasks in parallel (#1051 agent-configuration, #1052 defaults, #1053 desktop-configuration, #1055 feature-flags) whose target documents are not yet merged on origin/launchpad at the time this node was written."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1054 issue body, and the dispatching batch-run instructions naming sibling tasks #1051/#1052/#1053/#1055"
relationships:
  - type: implements
    target: corpus-template-configuration
---

# Buzz: environment configuration

This node catalogues Buzz's **environment-variable-based configuration** —
settings a running process reads from its environment rather than a config
file or compiled-in default — across two surfaces that both use environment
variables as their configuration mechanism: the `buzz-relay` process (via
`crates/buzz-relay/src/config.rs`'s `Config::from_env`, loaded once at
relay startup) and a desktop-managed agent subprocess spawned by the Buzz
desktop app (via `desktop/src-tauri/src/managed_agents/runtime.rs`'s
`spawn_agent_child`, assembled fresh on every spawn). It applies to local
development (`docker compose up` plus `.env`, per the root `AGENTS.md`'s
Getting Started section) and to any other deployment that sets the same
variable names; it does not itself describe kubernetes/staging-specific
values, which live in that deployment's own configuration surface, not this
repository's `.env.example`.

## Settings

Representative sample — see *Boundary* below for what full coverage would
require. Ordered as `.env.example`'s own section order for the relay rows;
ACP harness rows follow AGENTS.md's own ordering.

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `DATABASE_URL` | Postgres connection string | `postgres://buzz:buzz_dev@localhost:5432/buzz` | no | yes | Relay's writer Postgres connection. |
| `READ_DATABASE_URL` | Postgres connection string | unset (blank/whitespace-only treated as unset) | no | yes | Optional read-replica; unset keeps all reads on the writer. |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` | no | yes | Relay's shared Redis pool (pub/sub, presence, rate limits). |
| `BUZZ_REDIS_POOL_SIZE` | positive integer | `16` | no | no | Max connections in the relay's shared Redis pool; non-positive or unparsable values fall back to the default. |
| `BUZZ_DB_POOL_SIZE` | positive integer | `50` | no | no | Max connections in the relay's writer (and reader, when `READ_DATABASE_URL` is set) Postgres pool; same fallback rule as above. |
| `BUZZ_BIND_ADDR` | `host:port` socket address | `0.0.0.0:3000` | no | no | Bind address for the relay's HTTP/WebSocket listener; unparsable values are a startup error (`ConfigError::InvalidBindAddr`). |
| `RELAY_URL` | WebSocket URL | `ws://localhost:3000` | no | no | Public WebSocket URL used in NIP-42 auth challenges. |
| `BUZZ_RELAY_PRIVATE_KEY` | 32-byte hex private key | none — random per process if unset | no | yes | Stable relay signing key so REST-created posts keep resolving to the same author across relay restarts. |
| `BUZZ_WEB_DIR` | filesystem path | unset | no | no | When set, the relay serves the web UI dist directory at `/`. |
| `BUZZ_GIT_REPO_PATH` | filesystem path | `./repos` | no | no | Root directory for ephemeral Git workspaces and the pack cache. |
| `RUST_LOG` | tracing filter directive | unset (process default applies) | no | no | Log verbosity per crate target. |
| `BUZZ_OTEL_FILTER` | tracing filter directive | unset (falls back to `RUST_LOG` scope) | no | no | Deliberately independent from `RUST_LOG` so log-verbosity changes cannot break OpenTelemetry trace parentage, per `.env.example`'s own comment. |
| `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` | — | — | no | no | Renamed to `BUZZ_REPLICA_READ_MAX_AGE_MS`; setting this old name is a hard startup error, not a silently honoured alias (the units changed from seconds to milliseconds). |
| `BUZZ_PRIVATE_KEY` | hex or `nsec1…` Nostr private key | none — required | yes | yes | Identifies the ACP harness's agent on the relay. Auto-injected by the ACP harness into managed agent subprocesses; reserved on desktop (`RESERVED_ENV_KEYS`) so a persona/agent env override cannot swap it. |
| `BUZZ_RELAY_URL` | WebSocket URL | none in the CLI/harness; desktop always sets it at spawn | ACP: yes; desktop: n/a | no | Relay the ACP harness connects to. Distinct from the relay process's own `RELAY_URL`; the two happen to point at the same value in local dev. Reserved on desktop. |
| `BUZZ_AUTH_TAG` | opaque string | unset unless the record carries one | no | no | NIP-OA auth tag; auto-injected by the ACP harness / desktop. Reserved on desktop. |

## Litmus test

Every row above varies between deploys per the Twelve-Factor litmus test
this node's template adapts — "whether the codebase could be made open
source at any moment, without compromising any credentials." `RUST_LOG` and
`BUZZ_OTEL_FILTER` are borderline (they tune observability rather than
carry a secret or an environment-specific address) but are included because
their *values* are still expected to differ by deploy (verbose in dev,
quieter in production) even though neither fails the credentials half of
the test on its own. No internal-application-config value (a value that does
not vary between deploys, per Twelve-Factor's own exclusion) was found
mixed into either `.env.example` or `Config::from_env`'s reads during this
review — deploy-time relay/ACP settings and desktop-managed-agent env
overrides were the only environment-variable surfaces found within this
node's scope.

## Secrets discipline

No row above quotes a live credential, key, token, or hostname value.
`DATABASE_URL`, `READ_DATABASE_URL` and `REDIS_URL`'s shown defaults are
`.env.example`'s own committed, dev-only placeholder values (`buzz_dev` /
`buzz_dev_secret`-style credentials scoped to the local `docker compose`
stack, never valid outside it), not production secrets. `BUZZ_RELAY_PRIVATE_KEY`
and `BUZZ_PRIVATE_KEY` are marked `Secret: yes` and cite only where their
values come from (an env var of that name, read by the code paths cited in
this node's evidence ledger) — never a value. This follows
`AGENT_PR_TEMPLATE.md`'s own Verification checklist, which a corpus node is
bound by like any other tracked file.

## Boundary

This node does not describe:
- The parsing/validation implementation in detail beyond what backs the
  settings-table claims above — `crates/buzz-relay/src/config.rs` is ~1700
  lines with roughly 87 `std::env::var`-shaped call sites by the corpus
  template's own count; this node samples a representative subset (bind
  address, database/Redis pool sizing, drain jitter's empty-string kill
  switch, the replica-variable rename's hard-error behavior) rather than
  auditing every field. A future `implementation` node on `Config::from_env`
  itself would be the right place for full coverage, and could `references`
  this node.
- Desktop UI-persisted settings that are not environment variables at all
  (e.g. structured fields on `AgentDefinition` written to disk as JSON) —
  out of scope for this node and named as sibling task #1053's
  (`desktop-configuration`) territory, not yet merged.
- Agent-persona configuration structures and their own defaults — sibling
  tasks #1051 (`agent-configuration`) and #1052 (`defaults`), not yet
  merged.
- Feature-flag values — sibling task #1055 (`feature-flags`), not yet
  merged.
- A wire contract or event-kind shape any of these settings happens to
  influence — no such coupling was found for the sampled rows above.
- The `.env.example` ACP harness section's dozens of remaining variables
  (turn timeouts, subscription filtering, heartbeat, context limits,
  presence/typing toggles, event buffer sizing) beyond the identity/auth
  trio sampled here — `AGENTS.md`'s "Agent CLI (buzz-cli)" section and
  `.env.example`'s own comments are the authoritative source for each; this
  node does not restate them individually.

## Relationships

- `implements: corpus-template-configuration` — per that template's own
  guidance that a merged instance node should declare this edge, targeting
  the only currently-merged node that is a legitimate fit for a
  configuration-shaped document.

No `references` or `part-of` edges are declared: no other configuration-
surface node, and no broader capability/deployment node describing this
subject, is merged on `origin/launchpad` at the recorded revision. The four
sibling batch tasks (#1051, #1052, #1053, #1055) are open, unmerged PRs and
are therefore not valid `relationships.target` values per `AGENTS.md`'s own
rule to resolve against the merge-target branch, not the author's worktree.

## Scope and omissions

**This node covers** environment-variable-based configuration for the
`buzz-relay` process and for a desktop-managed agent subprocess: which
values qualify as configuration under the Twelve-Factor litmus test, a
representative settings table for both surfaces with type/default/
required/secret/effect, the desktop's six-layer env-assembly precedence
and where it writes relative to Buzz's own identity/security-gate
variables, and the secrets-discipline this node itself holds to.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Exhaustive row-by-row coverage of every `crates/buzz-relay/src/config.rs` field | Not yet a specific corpus task; a future `implementation` node is the natural home |
| Desktop UI-persisted (non-env-var) configuration | #1053 `desktop-configuration`, this batch, not yet merged |
| Agent-persona configuration and defaults | #1051 `agent-configuration` / #1052 `defaults`, this batch, not yet merged |
| Feature-flag values | #1055 `feature-flags`, this batch, not yet merged |
| The generic corpus configuration template's own rules | `launchpad/docs/corpus/templates/configuration.md` (`corpus-template-configuration`) |
| Creating/updating/retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether the `.env.example` ACP harness section's remaining ~30
  variables (turn timeout, subscription mode, heartbeat, context limit,
  presence/typing toggles, event buffer, legacy aliases) each still match
  their consuming code's actual default** was not checked field-by-field
  against `buzz-acp`'s own source in this pass — only the identity/auth
  trio (`BUZZ_PRIVATE_KEY`, `BUZZ_RELAY_URL`, `BUZZ_AUTH_TAG`) and the
  desktop env-assembly mechanics were verified against source.
- **Whether any kubernetes/staging deployment overlay sets values that
  diverge from `.env.example`'s documented defaults** was not checked —
  `squareup/block-coder-tf-stacks` (per the root `AGENTS.md`'s ecosystem
  table) is a separate, non-OSS repository this task did not have access
  to.
- **Whether the desktop's `global_env` layer (layer 3a) and the ACP CLI's
  own env-driven flags share any variable names that could collide** was
  not cross-checked; the two are documented from separate source files in
  this pass.
