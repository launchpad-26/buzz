---
id: layers-configuration-relay-configuration
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
  - statement: "node.schema.json's type enum includes layers as one of its thirteen members, and architecture/containers/relay.md (a merged node) establishes this corpus's own id/type convention for a path-mirrored node: id is the path's directory segments plus basename, kebab-joined (architecture-containers-relay for architecture/containers/relay.md), and type is the top-level directory name (architecture). Applying that same convention to this node's own path (layers/configuration/relay-configuration.md) yields id layers-configuration-relay-configuration and type layers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "launchpad/docs/corpus/templates/configuration.md (the assigned template) names crates/buzz-relay/src/config.rs's environment variables as the specific first real instance it expects to test whether its required sections are sufficient: its own Expected-but-not-verified section states 'No node has yet been authored from this template ... The first real configuration node -- likely buzz-relay's environment variables, given crates/buzz-relay/src/config.rs's size -- is what will actually test whether the required sections above are sufficient or need revision.' This node is that first instance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/configuration.md"
  - statement: "crates/buzz-relay/src/config.rs defines pub struct Config (a single flat struct, plus the nested AdminConfig and JoinPolicyConfig structs) and pub fn Config::from_env(), which is the relay's entire configuration-loading surface; a search for every quoted environment-variable-shaped literal (pattern \"[A-Z][A-Z0-9_]{3,}\") in that one file finds 81 distinct names."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/main.rs calls Config::from_env() exactly once, at process startup (main.rs:142-145), and maps a returned ConfigError to an anyhow error that main() propagates with '?' -- an invalid setting therefore aborts process startup before any HTTP/WebSocket listener binds, rather than being logged and ignored. crates/buzz-relay/src/state.rs stores the loaded value as 'pub config: Arc<Config>' on AppState (state.rs:632, constructed at state.rs:858) with no interior-mutability wrapper (no Mutex/RwLock/watch::Sender around it anywhere it is declared), and no reload/SIGHUP/file-watch code exists anywhere under crates/buzz-relay/src/ (checked by grep for 'SIGHUP', 'reload_config', and 'watch' near config in that directory, with zero matches) -- every setting in this document is therefore load-once-at-startup and requires a process restart to change; none is dynamically reloadable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:142"
      - "crates/buzz-relay/src/state.rs:632"
      - "crates/buzz-relay/src/state.rs:858"
  - statement: "crates/buzz-relay has no clap dependency and no command-line argument parsing anywhere in its Cargo.toml or src/*.rs -- the relay's entire configuration surface is environment variables read via std::env::var/std::env::var_os; there are no CLI flags to document for this crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "The root .env.example (252 lines) documents development-only default values for a subset of these variables (for example DATABASE_URL, REDIS_URL, BUZZ_BIND_ADDR, RELAY_URL, and the BUZZ_S3_* group), and deploy/charts/buzz/values.yaml (a real Helm chart) names, in its 'Chart-managed secrets' comment block, exactly the settings that carry credentials in a production deployment: BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, DATABASE_URL, READ_DATABASE_URL, REDIS_URL, BUZZ_S3_ACCESS_KEY and BUZZ_S3_SECRET_KEY. Neither file contains a live credential value; both are template/placeholder sources."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "deploy/charts/buzz/values.yaml"
  - statement: "config.rs's from_env implements two different environment-variable compatibility behaviors on real, already-shipped settings: BUZZ_REPLICA_HEAD_MAX_AGE_SECS is a hard startup error naming its replacement (BUZZ_REPLICA_READ_MAX_AGE_MS) rather than a silently honored alias, because the old name was seconds-denominated and the new one is milliseconds-denominated -- silently reusing the old name at the new unit would apply a 1000x-wrong budget. BUZZ_REQUIRE_MEDIA_GET_AUTH and BUZZ_REQUIRE_MEDIA_READ_AUTH (INERT_MEDIA_READ_AUTH_VARS) are accepted without error but no longer read for any decision; if either is set, startup logs a warning naming it inert, because unauthenticated media GET/HEAD is unconditional now and a lingering false value no longer reopens it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:474"
      - "crates/buzz-relay/src/config.rs:434"
      - "crates/buzz-relay/src/config.rs:800"
  - statement: "The relay's network, pool and connection settings (BUZZ_BIND_ADDR, DATABASE_URL, READ_DATABASE_URL, BUZZ_REPLICA_READ_MAX_AGE_MS, BUZZ_DRAIN_JITTER_MS, REDIS_URL, BUZZ_REDIS_POOL_SIZE, BUZZ_DB_POOL_SIZE, BUZZ_DB_READ_POOL_SIZE, RELAY_URL, BUZZ_PAIRING_RELAY_URL, BUZZ_MAX_CONNECTIONS, BUZZ_MAX_CONCURRENT_HANDLERS, BUZZ_SEND_BUFFER, BUZZ_MAX_FRAME_BYTES, BUZZ_SLOW_CLIENT_GRACE_LIMIT, BUZZ_UDS_PATH, BUZZ_HEALTH_PORT, BUZZ_METRICS_PORT) are parsed at config.rs lines 462-580 and 711-724, with defaults 0.0.0.0:3000, postgres://buzz:buzz_dev@localhost:5432/buzz, unset, 0 (disabled), 0 (disabled, capped at MAX_DRAIN_JITTER_MS=20000 from line 51), redis://localhost:6379, 16, 50, unset (falls back to db_pool_size), ws://localhost:3000, unset, 10000, 1024, 1000, 512*1024 (DEFAULT_MAX_FRAME_BYTES, line 14), 15, unset, 8080 and 9102 respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:462"
      - "crates/buzz-relay/src/config.rs:514"
      - "crates/buzz-relay/src/config.rs:556"
      - "crates/buzz-relay/src/config.rs:711"
  - statement: "The relay's auth, membership and identity settings (BUZZ_REQUIRE_AUTH_TOKEN, BUZZ_PUBKEY_ALLOWLIST, BUZZ_REQUIRE_RELAY_MEMBERSHIP, BUZZ_ALLOW_NIP_OA_AUTH, BUZZ_CORS_ORIGINS, BUZZ_RELAY_PRIVATE_KEY, RELAY_OWNER_PUBKEY, RELAY_OPERATOR_API_ORIGIN, RELAY_OPERATOR_PUBKEYS) are parsed at config.rs lines 582-689 and 702-709, all four boolean flags defaulting to false and accepting only the literal strings \"true\" or \"1\" as true (unlike BUZZ_AUDIT_ENABLED's parse_bool, which additionally accepts \"on\"); RELAY_OWNER_PUBKEY is warn-and-ignore on an invalid 64-hex-char value (config.rs:633-649) while RELAY_OPERATOR_PUBKEYS entries are a hard config error on the same validation (config.rs:662-683), and RELAY_OPERATOR_API_ORIGIN is required (hard error) whenever RELAY_OPERATOR_PUBKEYS is non-empty (config.rs:684-689)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:582"
      - "crates/buzz-relay/src/config.rs:633"
      - "crates/buzz-relay/src/config.rs:656"
      - "crates/buzz-relay/src/config.rs:702"
  - statement: "The relay's seven rate-limit settings (BUZZ_RATE_LIMIT_HUMAN_MESSAGES_PER_MIN, BUZZ_RATE_LIMIT_HUMAN_API_CALLS_PER_MIN, BUZZ_RATE_LIMIT_HUMAN_WS_EVENTS_PER_SEC, BUZZ_RATE_LIMIT_AGENT_STANDARD_MESSAGES_PER_MIN, BUZZ_RATE_LIMIT_AGENT_STANDARD_API_CALLS_PER_MIN, BUZZ_RATE_LIMIT_AGENT_ELEVATED_MESSAGES_PER_MIN, BUZZ_RATE_LIMIT_AGENT_PLATFORM_MESSAGES_PER_MIN) are parsed by rate_limit_config_from_env (config.rs:315-347) via positive_u64_from_env, which rejects zero and non-numeric values as a hard config error and otherwise falls back to buzz_auth::RateLimitConfig::default(); those seven defaults (60, 300, 10, 120, 600, 300, 600) are defined in crates/buzz-auth/src/rate_limit.rs's default_human_msg/default_human_api/default_human_ws/default_agent_std_msg/default_agent_std_api/default_agent_elev_msg/default_agent_plat_msg functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:315"
      - "crates/buzz-relay/src/config.rs:301"
      - "crates/buzz-auth/src/rate_limit.rs:110"
      - "crates/buzz-auth/src/rate_limit.rs:132"
  - statement: "The relay's media/S3 settings (BUZZ_S3_ENDPOINT, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, BUZZ_S3_BUCKET, BUZZ_S3_REGION, AWS_REGION, BUZZ_S3_ADDRESSING_STYLE, BUZZ_MAX_IMAGE_BYTES, BUZZ_MAX_GIF_BYTES, BUZZ_MAX_VIDEO_BYTES, BUZZ_MAX_FILE_BYTES, BUZZ_MEDIA_BASE_URL, BUZZ_MEDIA_UPLOAD_RECORDS, BUZZ_MEDIA_UPLOAD_IP_HEADER, BUZZ_MEDIA_UPLOAD_PORT_HEADER, BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS, BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS_PER_PUBKEY, BUZZ_MEDIA_UPLOADS_PER_MINUTE) are parsed at config.rs lines 726-798, with AWS_REGION read only as a fallback when BUZZ_S3_REGION is unset (config.rs:744-746), BUZZ_S3_ADDRESSING_STYLE defaulting to buzz_media::config::S3AddressingStyle::Path (crates/buzz-media/src/config.rs:8-14) on either absence or a non-Unicode value, and media_max_concurrent_uploads_per_pubkey being clamped to never exceed media_max_concurrent_uploads (config.rs:787-793)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:726"
      - "crates/buzz-media/src/config.rs:8"
  - statement: "BUZZ_EPHEMERAL_TTL_OVERRIDE (config.rs:808-818) is parsed as an optional positive i32 of seconds; when set, every ephemeral channel uses this TTL instead of the client-provided value, and startup logs a warning naming the override -- the field's own doc comment describes it as useful for testing ephemeral expiry quickly, not a production knob."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:808"
  - statement: "The relay's product-behavior toggles BUZZ_HUDDLE_AUDIO_AVAILABLE, BUZZ_MESH, BUZZ_MESH_BIND_ADDR, BUZZ_MESH_DEMO_ECHO and BUZZ_AUDIT_ENABLED are parsed at config.rs lines 594-625 and 910. BUZZ_HUDDLE_AUDIO_AVAILABLE defaults true (inverted logic: only the literal strings \"false\" or \"0\" turn it off) because huddle audio is peer-to-peer within one pod and a single-pod deployment (N=1) is the common case; a horizontally-scaled deployment must explicitly set it false. BUZZ_MESH and BUZZ_MESH_DEMO_ECHO both default off and require an explicit \"on\"/\"true\"/\"1\" (case-insensitive \"on\") to enable, a strict opt-in the field doc calls a 'no-regression rollout' guarantee. BUZZ_AUDIT_ENABLED defaults true via parse_bool, which additionally accepts \"on\"/\"off\" alongside \"true\"/\"1\"/\"false\"/\"0\"/empty-string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:594"
      - "crates/buzz-relay/src/config.rs:605"
      - "crates/buzz-relay/src/config.rs:910"
      - "crates/buzz-relay/src/config.rs:394"
  - statement: "The relay's git-server settings (BUZZ_GIT_REPO_PATH, BUZZ_GIT_PACK_CACHE_PATH, BUZZ_GIT_MAX_PACK_BYTES, BUZZ_GIT_MAX_REPO_BYTES, BUZZ_GIT_PACK_CACHE_MAX_BYTES, BUZZ_GIT_PACK_CACHE_MAX_CONCURRENT_POPULATIONS, BUZZ_GIT_MAX_REPOS_PER_PUBKEY, BUZZ_GIT_MAX_CONCURRENT_OPS, BUZZ_GIT_HOOK_HMAC_SECRET) are parsed at config.rs lines 820-861, with three of the byte-size limits deriving their default from one another (git_max_repo_bytes defaults to 2x git_max_pack_bytes; git_pack_cache_max_bytes defaults to 5x git_max_repo_bytes) rather than each being an independent literal, and BUZZ_GIT_HOOK_HMAC_SECRET auto-generating a random 32-byte hex secret when unset (config.rs:856-861) but rejecting an explicitly-set value shorter than 32 characters as a hard config error (config.rs:982-987)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:820"
      - "crates/buzz-relay/src/config.rs:838"
      - "crates/buzz-relay/src/config.rs:856"
      - "crates/buzz-relay/src/config.rs:982"
  - statement: "The relay's push-gateway settings (BUZZ_PUSH_EXECUTOR_KEY_ID, BUZZ_PUSH_GATEWAY_DELIVERY_URL, BUZZ_PUSH_GATEWAY_TIMEOUT_MS) are parsed at config.rs lines 862-889. BUZZ_PUSH_EXECUTOR_KEY_ID defaults to \"relay-v1\" and is a hard error if empty or over 64 bytes. BUZZ_PUSH_GATEWAY_DELIVERY_URL defaults to the constant DEFAULT_PUSH_GATEWAY_DELIVERY_URL (config.rs:370, https://push.buzz.xyz/v1/deliveries/apns) and, whether defaulted or explicitly set, is validated as an exact HTTPS URL at path /v1/deliveries/apns with no credentials/query/fragment (config.rs:372-392); an explicit empty value disables push lease support entirely (sets the field to None). BUZZ_PUSH_GATEWAY_TIMEOUT_MS defaults to 2000ms and is a hard error outside the inclusive range 100..=10000."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:862"
      - "crates/buzz-relay/src/config.rs:370"
      - "crates/buzz-relay/src/config.rs:876"
  - statement: "The relay's join-policy, deployment-admin and web-UI settings (BUZZ_TERMS_OF_SERVICE_MARKDOWN, BUZZ_PRIVACY_POLICY_MARKDOWN, BUZZ_AGE_ATTESTATION_REQUIRED, BUZZ_ADMIN_HOST, BUZZ_ADMIN_WEB_DIR, BUZZ_WEB_DIR, BUZZ_SERVE_GIT_WEB_GUI) are parsed at config.rs lines 891-977. The two policy-markdown variables are capped at 256KiB each (MAX_POLICY_MARKDOWN_BYTES, config.rs:891) and, when either is set or age-attestation is required, are hashed together (SHA-256) into a content-derived join_policy.version so a policy edit changes the version every client/attestation record can be checked against. BUZZ_ADMIN_HOST is a hard error if it contains '/', '\\\\' or '@' (not a bare authority); the admin surface (and BUZZ_ADMIN_WEB_DIR) is entirely absent when BUZZ_ADMIN_HOST is unset, per its own doc comment 'Deny-by-default read-only deployment-admin configuration.' BUZZ_WEB_DIR and BUZZ_ADMIN_WEB_DIR are each a hard error if the directory does not contain an index.html file."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:891"
      - "crates/buzz-relay/src/config.rs:930"
      - "crates/buzz-relay/src/config.rs:959"
  - statement: "A configuration node built from corpus-template-configuration should declare a part-of relationship toward the broader node this configuration surface is a subsection of, and architecture-containers-relay (a merged node) already treats crates/buzz-relay/src/config.rs as core evidence for the relay container's own description -- including a direct comparison between this exact Helm chart secret list and config.rs's own env reads -- making it the natural part-of target for a node that documents that same file's settings in full."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
    confidence: 0.75
  - statement: "corpus-template-configuration itself states that a node built from it 'should declare implements targeting corpus-template-configuration ... once this node is merged,' naming relationships.schema.json's own worked example for implements ('a template instance of a standard') as the reason -- not the weaker references edge."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/configuration.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
relationships:
  - type: part-of
    target: architecture-containers-relay
  - type: implements
    target: corpus-template-configuration
---

# Relay: configuration

This node catalogues `buzz-relay`'s entire runtime configuration surface: every
setting `crates/buzz-relay/src/config.rs`'s `pub struct Config` reads via
`Config::from_env()`, which is the relay's only configuration-loading path. It applies
to every deployment of the relay — local development (`.env.example`), the bundled
`docker-compose.yml` backing services plus a locally-run relay binary, and the
production Helm chart (`deploy/charts/buzz/values.yaml`) — since the same
`from_env()` code runs unconditionally regardless of deployment target; only the
*values* supplied differ per deployment, never the parsing or validation logic. There
is no CLI-flag surface for this crate (no `clap` dependency, no argument parsing
anywhere in `crates/buzz-relay`) — environment variables are the entire input.

`Config::from_env()` runs exactly once, at process startup
(`crates/buzz-relay/src/main.rs:142`). A `ConfigError` from any setting below aborts
startup before the relay binds its HTTP/WebSocket listener — invalid configuration is
fail-closed, not logged-and-ignored. The loaded value is stored as `pub config:
Arc<Config>` on `AppState` (`crates/buzz-relay/src/state.rs:632,858`) with no
interior-mutability wrapper, and no reload/SIGHUP/file-watch mechanism exists anywhere
in the crate. **Every setting in this document requires a process restart to change;
none is dynamically reloadable at runtime.**

## Settings

### Network, pool and connection

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_BIND_ADDR` | socket addr | `0.0.0.0:3000` | no | no | HTTP/WebSocket bind address; invalid value is a hard startup error. |
| `DATABASE_URL` | Postgres URL | `postgres://buzz:buzz_dev@localhost:5432/buzz` | no (dev default is not production-safe) | yes | Primary Postgres connection. |
| `READ_DATABASE_URL` | Postgres URL | unset (all reads on writer) | no | yes | Optional read-replica URL for bounded-staleness read routing. |
| `BUZZ_REPLICA_READ_MAX_AGE_MS` | non-negative integer (ms) | `0` (replica routing disabled) | no | no | Replica read budget; `0` keeps all reads on the writer. |
| `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` | — | — | — | no | **Removed.** Setting this at all is a hard startup error naming the renamed replacement above (see *Compatibility and deprecation*). |
| `BUZZ_DRAIN_JITTER_MS` | non-negative integer (ms), capped | `0` (no jitter) | no | no | Upper bound of per-connection random delay before the `1012` close frame on graceful shutdown; clamped to `MAX_DRAIN_JITTER_MS` = 20000. Empty string is treated as unset, not an error. |
| `REDIS_URL` | Redis URL | `redis://localhost:6379` | no (dev default is not production-safe) | yes | Pub/sub, presence and rate-limit backing store. |
| `BUZZ_REDIS_POOL_SIZE` | positive integer | `16` | no | no | Max connections in the shared Redis pool. |
| `BUZZ_DB_POOL_SIZE` | positive integer | `50` | no | no | Max connections in the Postgres writer pool. |
| `BUZZ_DB_READ_POOL_SIZE` | positive integer | unset (falls back to `BUZZ_DB_POOL_SIZE`) | no | no | Max connections in the Postgres read-replica pool, sized independently. |
| `RELAY_URL` | ws(s) URL | `ws://localhost:3000` | no | no | Public WebSocket URL advertised in NIP-11; also drives the Helm chart's default `mediaBaseUrl`. |
| `BUZZ_PAIRING_RELAY_URL` | ws(s) URL | unset | no | no | Public URL of the dedicated device-pairing relay; must parse as `ws://`/`wss://` with a host or startup fails. |
| `BUZZ_MAX_CONNECTIONS` | integer | `10000` | no | no | Max concurrent WebSocket connections. |
| `BUZZ_MAX_CONCURRENT_HANDLERS` | integer | `1024` | no | no | Max concurrently executing message handlers. |
| `BUZZ_SEND_BUFFER` | integer | `1000` | no | no | Per-connection outbound message buffer size (messages). |
| `BUZZ_MAX_FRAME_BYTES` | positive integer (bytes) | `524288` (512 KiB, `DEFAULT_MAX_FRAME_BYTES`) | no | no | Max inbound WebSocket frame size. |
| `BUZZ_SLOW_CLIENT_GRACE_LIMIT` | integer | `15` | no | no | Consecutive buffer-full events tolerated before a slow client is cancelled. |
| `BUZZ_UDS_PATH` | filesystem path | unset | no | no | Optional Unix Domain Socket the relay also listens on (health probes still use TCP). |
| `BUZZ_HEALTH_PORT` | port | `8080` | no | no | Health-only router port (`/_liveness`, `/_readiness`, `/_status`); separate router so k8s probes bypass Istio/auth middleware. |
| `BUZZ_METRICS_PORT` | port | `9102` | no | no | Prometheus `/metrics` exporter port. |

### Auth, membership and relay identity

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_REQUIRE_AUTH_TOKEN` | bool (`true`/`1` only) | `false` | no | no | Whether REST requests must present a valid token; WebSocket protocol auth is always required regardless. `false` logs a startup warning. |
| `BUZZ_PUBKEY_ALLOWLIST` | bool (`true`/`1` only) | `false` | no | no | Restricts NIP-42 pubkey-only auth (no token) to the `pubkey_allowlist` table; token-authenticated users bypass it. |
| `BUZZ_REQUIRE_RELAY_MEMBERSHIP` | bool (`true`/`1` only) | `false` | no | no | When true, every authenticated request also needs a `relay_members` row. |
| `BUZZ_ALLOW_NIP_OA_AUTH` | bool (`true`/`1` only) | `false` | no | no | Allows NIP-OA owner-attestation agent auth to grant membership on closed relays. |
| `BUZZ_CORS_ORIGINS` | comma-separated list | empty (permissive CORS — dev mode) | no | no | Allowed CORS origins for the HTTP surface. |
| `BUZZ_RELAY_PRIVATE_KEY` | hex-encoded private key | unset (fresh keypair generated at startup) | no | yes | The relay's own signing identity. |
| `RELAY_OWNER_PUBKEY` | 64-char hex pubkey | unset | no | no (public key, not a credential) | Auto-bootstrapped into `relay_members` with the `owner` role on first startup. Invalid value: warn and ignore (not a hard error). |
| `RELAY_OPERATOR_API_ORIGIN` | http(s) origin, no path/query/fragment | unset | required iff `RELAY_OPERATOR_PUBKEYS` is non-empty | no | Canonical origin every operator NIP-98 `u` tag is verified against, independent of the inbound `Host` header. |
| `RELAY_OPERATOR_PUBKEYS` | comma-separated 64-char hex pubkeys | empty (community provisioning disabled — fail closed) | no | no (public keys, not credentials) | Deployment-level operators allowed to use `/operator/communities`. An invalid entry is a hard error, not a skip. |

### Rate limiting

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_RATE_LIMIT_HUMAN_MESSAGES_PER_MIN` | positive integer | `60` | no | no | Human message rate limit. |
| `BUZZ_RATE_LIMIT_HUMAN_API_CALLS_PER_MIN` | positive integer | `300` | no | no | Human REST call rate limit. |
| `BUZZ_RATE_LIMIT_HUMAN_WS_EVENTS_PER_SEC` | positive integer | `10` | no | no | Human WebSocket event rate limit. |
| `BUZZ_RATE_LIMIT_AGENT_STANDARD_MESSAGES_PER_MIN` | positive integer | `120` | no | no | Standard-tier agent message rate limit. |
| `BUZZ_RATE_LIMIT_AGENT_STANDARD_API_CALLS_PER_MIN` | positive integer | `600` | no | no | Standard-tier agent REST call rate limit. |
| `BUZZ_RATE_LIMIT_AGENT_ELEVATED_MESSAGES_PER_MIN` | positive integer | `300` | no | no | Elevated-tier agent message rate limit. |
| `BUZZ_RATE_LIMIT_AGENT_PLATFORM_MESSAGES_PER_MIN` | positive integer | `600` | no | no | Platform-tier agent message rate limit. |

All seven are a hard config error on zero or non-numeric input (`positive_u64_from_env`); there is no "0 = unlimited" convention here.

### Media and S3

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_S3_ENDPOINT` | URL | `http://localhost:9000` | no | no | S3-compatible endpoint. |
| `BUZZ_S3_ACCESS_KEY` | string | `buzz_dev` | no | yes | S3 access key. |
| `BUZZ_S3_SECRET_KEY` | string | `buzz_dev_secret` | no | yes | S3 secret key. |
| `BUZZ_S3_BUCKET` | string | `buzz-media` | no | no | S3 bucket name. |
| `BUZZ_S3_REGION` | string | falls back to `AWS_REGION`, then `us-east-1` | no | no | S3 region. |
| `AWS_REGION` | string | — | no | no | Only consulted when `BUZZ_S3_REGION` is unset. |
| `BUZZ_S3_ADDRESSING_STYLE` | `path` \| `virtual` | `path` | no | no | Path-style keeps compatibility with bundled MinIO's internal DNS; `virtual` is required by some providers (e.g. Railway Storage Buckets). Invalid/non-Unicode value is a hard error. |
| `BUZZ_MAX_IMAGE_BYTES` | integer (bytes) | `52428800` (50 MiB) | no | no | Max image upload size. |
| `BUZZ_MAX_GIF_BYTES` | integer (bytes) | `10485760` (10 MiB) | no | no | Max GIF upload size. |
| `BUZZ_MAX_VIDEO_BYTES` | integer (bytes) | `524288000` (500 MB) | no | no | Max video upload size. |
| `BUZZ_MAX_FILE_BYTES` | integer (bytes) | `104857600` (100 MiB) | no | no | Max generic file upload size. |
| `BUZZ_MEDIA_BASE_URL` | URL | `http://localhost:3000/media` | no | no | Public base URL media links resolve against. |
| `BUZZ_MEDIA_UPLOAD_RECORDS` | bool (`true`/`1` only) | `false` | no | no | Enables the `_uploads/` moderation side-channel; coherence with the two header settings below is checked at startup by `MediaConfig::validate`. |
| `BUZZ_MEDIA_UPLOAD_IP_HEADER` | header name (lowercased) | unset | no | no | Header trusted for uploader IP when set. |
| `BUZZ_MEDIA_UPLOAD_PORT_HEADER` | header name (lowercased) | unset | no | no | Header trusted for uploader port when set. |
| `BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS` | positive integer | `8` | no | no | Max concurrent uploads for the whole relay process. |
| `BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS_PER_PUBKEY` | positive integer, clamped | `2` (never exceeds the process-wide max above) | no | no | Max concurrent uploads from one pubkey. |
| `BUZZ_MEDIA_UPLOADS_PER_MINUTE` | positive integer | `30` | no | no | Max upload starts per pubkey per minute. |
| `BUZZ_REQUIRE_MEDIA_GET_AUTH` | — | — | — | no | **Inert.** Accepted but no longer read for any decision (see *Compatibility and deprecation*). |
| `BUZZ_REQUIRE_MEDIA_READ_AUTH` | — | — | — | no | **Inert**, same as above; was documented in `.env.example` as an alias but was never actually read. |

### Ephemeral channels

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_EPHEMERAL_TTL_OVERRIDE` | positive integer (seconds) | unset | no | no | Forces every ephemeral channel to this TTL regardless of the client-provided value; intended for testing expiry quickly, not production tuning. Setting it logs a startup warning. |

### Product behavior toggles

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_HUDDLE_AUDIO_AVAILABLE` | bool, inverted (`false`/`0` only turn it off) | `true` | no | no | Whether this deployment can serve huddle (voice) audio. Huddles are peer-relayed within one pod; a horizontally-scaled deployment must set this `false` until an out-of-relay SFU exists, or peers on different pods silently can't hear each other. |
| `BUZZ_MESH` | bool (`on`/`true`/`1`, case-insensitive `on`) | `false` (off) | no | no | Opt-in inter-relay mesh. Absent/off is byte-for-byte today's single-instance behavior (no bind, no Redis registry write) — a strict no-regression rollout gate. |
| `BUZZ_MESH_BIND_ADDR` | socket addr | `0.0.0.0:3478` | no | no | UDP bind for the mesh transport; invalid value is a hard error. |
| `BUZZ_MESH_DEMO_ECHO` | bool (`on`/`true`/`1`, case-insensitive `on`) | `false` (off) | no | no | Testbed-only reliable-stream echo consumer; explicitly not a product flow. |
| `BUZZ_AUDIT_ENABLED` | bool (`true`/`1`/`on` / `false`/`0`/`off`/empty) | `true` | no | no | Tamper-evident event/media audit logging. Does not control the separate `moderation_actions` trail. |

### Git server

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_GIT_REPO_PATH` | filesystem path | `./repos` | no | no | Root for the relay's local git scratch; created on startup if absent. Repo-name uniqueness lives in Postgres, not on disk, so this need not be persistent or shared across replicas. |
| `BUZZ_GIT_PACK_CACHE_PATH` | filesystem path | `<git_repo_path>/.pack-cache` | no | no | Parent directory for process-isolated immutable pack cache sessions. |
| `BUZZ_GIT_MAX_PACK_BYTES` | integer (bytes) | `524288000` (500 MB) | no | no | Max pack file size for a git push. |
| `BUZZ_GIT_MAX_REPO_BYTES` | integer (bytes) | 2x `BUZZ_GIT_MAX_PACK_BYTES` (1 GB at defaults) | no | no | Max total bytes materialized for one git repo request. |
| `BUZZ_GIT_PACK_CACHE_MAX_BYTES` | integer (bytes) | 5x the effective `BUZZ_GIT_MAX_REPO_BYTES` (5 GB at defaults) | no | no | Max bytes retained in the process-local immutable pack/index cache; `0` disables retention while still allowing request-local hydration. |
| `BUZZ_GIT_PACK_CACHE_MAX_CONCURRENT_POPULATIONS` | positive integer | `2` | no | no | Max pack digests populated concurrently in one process. |
| `BUZZ_GIT_MAX_REPOS_PER_PUBKEY` | integer | `100` | no | no | Max repos per pubkey. |
| `BUZZ_GIT_MAX_CONCURRENT_OPS` | integer | `20` | no | no | Max concurrent git subprocess operations. |
| `BUZZ_GIT_HOOK_HMAC_SECRET` | string, ≥32 chars | auto-generated random 32-byte hex (dev mode) | no | yes | Authenticates internal git pre-receive hook callbacks. An explicitly-set value under 32 characters is a hard startup error; the Helm chart marks this required when `replicaCount > 1` (autogen is only effective at first install and is per-process, so multiple replicas need a shared explicit value). |

### Push gateway

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_PUSH_EXECUTOR_KEY_ID` | string, 1..=64 bytes | `relay-v1` | no | no | Descriptor key id accepted in kind:30350 `exec` tags. Empty or over 64 bytes is a hard error. |
| `BUZZ_PUSH_GATEWAY_DELIVERY_URL` | exact HTTPS URL, path `/v1/deliveries/apns` | `https://push.buzz.xyz/v1/deliveries/apns` | no | no | Gateway endpoint for client-authorized APNs delivery capabilities. An explicit empty value disables push lease support entirely; any other value is validated as an exact-path HTTPS URL with no credentials/query/fragment. |
| `BUZZ_PUSH_GATEWAY_TIMEOUT_MS` | integer, `100..=10000` | `2000` | no | no | Timeout for one gateway delivery request; out-of-range is a hard error. |

### Join policy, deployment admin and web UI

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_TERMS_OF_SERVICE_MARKDOWN` | Markdown string, ≤256 KiB | unset | no | no | Operator-provided Terms of Service, shown on join surfaces. |
| `BUZZ_PRIVACY_POLICY_MARKDOWN` | Markdown string, ≤256 KiB | unset | no | no | Operator-provided Privacy Policy, shown on join surfaces. |
| `BUZZ_AGE_ATTESTATION_REQUIRED` | bool (`true`/`1`/`on`/etc., `parse_bool` rules) | `false` | no | no | Whether join surfaces must collect an 18+ attestation. Any of the three settings above being non-default creates a `JoinPolicyConfig` with a SHA-256 content-derived `version` binding receipts to the exact policy revision. |
| `BUZZ_ADMIN_HOST` | exact HTTP authority (no `/`, `\`, or `@`) | unset (admin surface entirely absent) | no | no | Enables the read-only, deny-by-default deployment-admin API/SPA at this authority. Deny-by-default: unset means the route does not exist at all. |
| `BUZZ_ADMIN_WEB_DIR` | directory containing `index.html` | unset | no | no | Optional admin SPA bundle directory; missing `index.html` is a hard error only when the directory value is set. |
| `BUZZ_WEB_DIR` | directory containing `index.html` | unset (no static file serving) | no | no | When set, the relay serves the invite landing page and static assets from this directory. |
| `BUZZ_SERVE_GIT_WEB_GUI` | bool (`true`/`1` only) | `false` | no | no | Whether the configured `BUZZ_WEB_DIR` bundle also serves Git browser routes in addition to the public invite landing page. |

## Litmus test

Every row above varies between deploys per the Twelve-Factor litmus test — "whether
the codebase could be made open source at any moment, without compromising any
credentials" — and every value comes from `std::env::var`/`std::env::var_os`, never a
compiled-in constant that changes with the source. Nothing considered here failed the
test and was excluded: `crates/buzz-relay/src/config.rs` has no settings-shaped field
that is *not* read from the environment (its only non-`from_env`-sourced constants are
`DEFAULT_MAX_FRAME_BYTES`, `MAX_DRAIN_JITTER_MS` and `DEFAULT_PUSH_GATEWAY_DELIVERY_URL`,
which are caps/defaults the environment can override, not internal application config
in Twelve-Factor's excluded sense).

## Secrets discipline

No row above quotes a live credential, key, token, or hostname value. Rows marked
`Secret: yes` above are `DATABASE_URL`, `READ_DATABASE_URL`, `REDIS_URL`,
`BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_S3_ACCESS_KEY` and `BUZZ_S3_SECRET_KEY` —
connection strings and keys that embed or are themselves credentials. `RELAY_OWNER_PUBKEY`
and `RELAY_OPERATOR_PUBKEYS` are marked `no` even though they look sensitive: a Nostr
pubkey is a public identifier by design, not a credential, and both are validated as
public 64-char hex values, never a private key. `BUZZ_GIT_HOOK_HMAC_SECRET` is marked
`Secret: yes` — it authenticates internal HMAC callbacks. Every secret-marked row's
*dev-mode* value in this document (`buzz_dev`, `buzz_dev_secret`,
`postgres://buzz:buzz_dev@localhost:5432/buzz`) is copied from the already-committed
`.env.example`, not invented for this node, and is a local-development-only
placeholder — never a value any real deployment should keep. Where the code
auto-generates a secret (`BUZZ_GIT_HOOK_HMAC_SECRET`, `BUZZ_RELAY_PRIVATE_KEY`), this
document names the mechanism, never a generated value.

## Compatibility and deprecation

- **`BUZZ_REPLICA_HEAD_MAX_AGE_SECS` — removed, hard error.** This was the old,
  seconds-denominated name for what is now `BUZZ_REPLICA_READ_MAX_AGE_MS`
  (milliseconds). Setting the old name at all refuses startup with a message naming
  the replacement, rather than being silently accepted at the wrong unit (which would
  apply a 1000x-wrong budget).
- **`BUZZ_REQUIRE_MEDIA_GET_AUTH` / `BUZZ_REQUIRE_MEDIA_READ_AUTH` — inert, accepted.**
  Both are accepted without error (no startup failure) but no longer read for any
  access decision: authenticated media reads are unconditional now. If either is set,
  startup logs a warning naming it inert — a lingering `false` no longer reopens
  unauthenticated reads, which is the trap an operator carrying an old `.env` could
  otherwise fall into.

No other setting in this document has a deprecated or renamed predecessor as of the
recorded revision.

## Boundary

This node does not describe:

- **The parsing/validation implementation itself** beyond what is needed to state each
  setting's type, default and failure behavior above — a deeper description of
  `Config::from_env()`'s internal structure (helper functions, error types, control
  flow) belongs to an `implementation` node, not this one, if one is later written.
- **`crates/buzz-relay/src/main.rs`'s own separate environment reads that are outside
  the `Config` struct** — `RUST_LOG` (via `log_env_filter`), `BUZZ_AUTO_MIGRATE`
  (`buzz_auto_migrate_enabled`), `BUZZ_USAGE_METRICS_PER_COMMUNITY` (`EmissionScope::
  from_env`), and `storage_sweep::StorageSweepConfig::from_env` are each a different
  struct/module's own configuration surface, not `config.rs`'s `Config`. Folding them
  in here would document two concepts (config.rs's `Config` and main.rs's ad hoc
  startup env reads) as one node.
- **A CLI-flag surface** — there is none for this crate; noted above rather than
  silently omitted.
- **Configuration for any other component** — desktop, mobile, the CLI, the agent
  harness, or the ACP bridge each has its own surface, owned by sibling corpus tasks
  under Feature #611 (agent-configuration #1051, configuration-defaults #1052,
  desktop-configuration #1053, environment-configuration #1054,
  mobile-configuration #1056, configuration-secrets #1058,
  configuration-validation #1059).
- **The general environment-variable loading *mechanism*** (how `std::env::var` and
  its error variants are used as a pattern across the codebase) rather than this one
  crate's actual settings — owned by #1054.
- **Secrets-handling policy in general** (rotation, storage, injection) beyond what
  each row above states about its own value — owned by #1058.

## Relationships

- `part-of`: `architecture-containers-relay` — this node documents one subsection of
  the relay container that node already describes at a higher level (and already
  cites `config.rs` extensively as evidence for the container's own claims).
- `implements`: `corpus-template-configuration` — this is a template instance of that
  standard, per the template's own required-relationship guidance.

## Scope and omissions

**This node covers** every environment variable `crates/buzz-relay/src/config.rs`'s
`Config::from_env()` reads: 81 distinct settings across network/pool, auth/membership/
identity, rate limiting, media/S3, ephemeral channels, product-behavior toggles, the
git server, the push gateway, and join-policy/admin/web-UI — their type/shape, source,
default, required/secret status, and effect; the Twelve-Factor litmus test applied to
this surface; the secrets discipline every row holds to; the two real compatibility/
deprecation cases already shipped in this file; and the explicit boundary against
main.rs's own separate env reads and every sibling component's configuration.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `main.rs`'s own env reads outside the `Config` struct (`RUST_LOG`, `BUZZ_AUTO_MIGRATE`, `BUZZ_USAGE_METRICS_PER_COMMUNITY`, `StorageSweepConfig`) | No specific corpus task found for this narrower surface as of this writing |
| Desktop, mobile, CLI and agent-harness configuration | #1051, #1053, #1056 |
| Environment-variable loading as a general mechanism | #1054 |
| Configuration defaults policy | #1052 |
| Configuration validation framework | #1059 |
| Secrets handling generally (rotation, storage, injection) | #1058 |
| The `Config::from_env()` implementation's own internal structure | No `implementation`-type node found for this file as of this writing |

**Expected but not verified when this node was written:**

- **Every default value above was read directly from `config.rs`'s parsing code, not
  from `.env.example` or the Helm chart, per the template's own rule that the loading
  code is authoritative when the two could disagree.** `.env.example` and
  `deploy/charts/buzz/values.yaml` were both opened and are cited only for the
  deployment-example and secret-inventory claims above, not for any default value in
  the settings tables.
- **Every field's behavior was traced from the code actually invoked by
  `Config::from_env()`, including two levels of nested config (`buzz_auth::
  RateLimitConfig::default()`, `buzz_media::config::S3AddressingStyle::default()`) —
  but this node's search for environment-variable names was a single regex pass over
  one file (`config.rs`) rather than a crate-wide or workspace-wide search.** If any
  other file in `crates/buzz-relay` reads an environment variable that ends up on the
  `Config` struct through some path this node's search did not follow, it is missing
  from the table above.
- **Runtime behavior under an actually-invalid value for every setting was not
  individually executed** — the hard-error/warn-and-ignore/silently-defaulted
  classification above is read from the parsing code's own logic (`Result`-returning
  vs. `unwrap_or`/`ok()`-swallowing patterns), not from running the binary with each
  bad value and observing the outcome.
