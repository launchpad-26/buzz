---
id: layers-configuration-validation
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
  - statement: "crates/buzz-relay/src/config.rs defines Config::from_env() -> Result<Self, ConfigError>, which loads the relay's runtime configuration once from environment variables; ConfigError has two variants, InvalidBindAddr and InvalidValue, both carrying a message string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:16-25"
      - "crates/buzz-relay/src/config.rs:459-461"
  - statement: "crates/buzz-relay/src/main.rs calls Config::from_env() once, at process startup, before installing metrics, connecting the database pools, or building the router, and propagates any Err through `?` inside an anyhow::Result main function — a configuration error aborts relay startup before the process serves any traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:140-145"
  - statement: "from_env() performs per-value type/shape validation inline as each variable is read: parse_bind_addr rejects a BUZZ_BIND_ADDR that does not parse as a SocketAddr, parse_operator_api_origin and parse_push_gateway_delivery_url reject a RELAY_OPERATOR_API_ORIGIN / BUZZ_PUSH_GATEWAY_DELIVERY_URL that is not a URL of the required exact shape (scheme, no credentials, no query/fragment, and for the push gateway URL an exact path), and numeric fields such as BUZZ_REPLICA_READ_MAX_AGE_MS and BUZZ_DRAIN_JITTER_MS return ConfigError::InvalidValue on an unparsable value rather than silently falling back to a default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:296-298"
      - "crates/buzz-relay/src/config.rs:349-392"
      - "crates/buzz-relay/src/config.rs:486-491"
      - "crates/buzz-relay/src/config.rs:500-512"
  - statement: "from_env() also performs cross-field semantic validation beyond single-value parsing: it refuses RELAY_OPERATOR_PUBKEYS as ConfigError::InvalidValue when pubkeys are present but RELAY_OPERATOR_API_ORIGIN is unset, and it refuses the old, renamed BUZZ_REPLICA_HEAD_MAX_AGE_SECS environment variable outright as a hard startup error naming its replacement, rather than silently honouring the old name."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:662-689"
      - "crates/buzz-relay/src/config.rs:474-482"
  - statement: "The renamed-variable hard-fail is exercised by test replica_read_max_age_defaults_off_and_rejects_junk, which sets the old BUZZ_REPLICA_HEAD_MAX_AGE_SECS name and asserts Config::from_env() returns Err(ConfigError::InvalidValue) whose message names the replacement variable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:1325-1373"
  - statement: "Not every invalid or unrecognized value in from_env() is fail-fast: when RELAY_OWNER_PUBKEY is present but is not a 64-character lowercase hex string, from_env() logs a tracing::warn! and treats the field as None (ignored) instead of returning a ConfigError."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:633-649"
  - statement: "BUZZ_DRAIN_JITTER_MS is shape-validated (a non-parsable value is a hard ConfigError::InvalidValue) but an in-range numeric value above MAX_DRAIN_JITTER_MS (20,000 ms) is silently clamped to that maximum rather than rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:500-512"
      - "crates/buzz-relay/src/config.rs:49-51"
  - statement: "A second, independent validation call happens after from_env() returns and before the media subsystem is initialized: crates/buzz-relay/src/main.rs calls config.media.validate(), mapping any Err(String) to an anyhow error propagated with `?`; MediaConfig::validate enforces single-field rules (public_base_url must end with \"/media\" and must not end with \"/\"; max_image_bytes, max_gif_bytes, max_video_bytes and max_file_bytes must be nonzero, with max_gif_bytes additionally bounded by max_image_bytes) and cross-field rules (upload_ip_header set while upload_records_enabled is false is refused; upload_port_header set without upload_ip_header is refused)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:448-451"
      - "crates/buzz-media/src/config.rs:100-145"
  - statement: "A third startup validation-shaped check is not routed through ConfigError or MediaConfig::validate's Result type at all: crates/buzz-relay/src/main.rs enforces, via a bare panic! rather than a returned error, that BUZZ_RELAY_PRIVATE_KEY must be set whenever BUZZ_REQUIRE_AUTH_TOKEN=true; when the private key is absent and require_auth_token is false, the relay instead falls back to a hardcoded, logged development keypair."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:425-446"
  - statement: "crates/buzz-relay/src/main.rs also validates the shape of a secret-shaped configuration value after Config::from_env returns: it calls nostr::Keys::parse(hex) on BUZZ_RELAY_PRIVATE_KEY when the value is present, failing startup with an anyhow error (via `?`) if the value does not parse as a valid Nostr keypair; the value's content is never logged, only whether parsing succeeded."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:425-427"
  - statement: "Config and MediaConfig values are read into their structs exactly once, in from_env()/main(), at process startup; no code in crates/buzz-relay/src/config.rs or crates/buzz-relay/src/main.rs re-reads the environment or reloads configuration afterward, and a search of both files for reload/SIGHUP-style mechanisms (rg -i \"reload|SIGHUP\") returns no matches. Applying a changed environment variable therefore requires restarting the relay process."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/main.rs:140-145"
    confidence: 0.75
  - statement: "crates/buzz-backend-kubernetes/src/config.rs implements a structurally distinct validation mechanism for a different Buzz surface (the Kubernetes agent-launch provider_config): parse(cfg: &serde_json::Value) -> Result<ProviderConfig, String> validates a caller-supplied JSON object without trusting its declared shape — helper functions optional_string and optional_u64 explicitly reject a wrong-typed JSON value (e.g. a JSON number where a string field is expected) with a field-named error message, rather than coercing it."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:76-106"
      - "crates/buzz-backend-kubernetes/src/config.rs:121-176"
  - statement: "buzz-backend-kubernetes's parse() refuses a legal-but-currently-unsupported value rather than silently reinterpreting it: inactivity_seconds: 0 is a value the crate's own spec comment calls meaningful (\"no auto-stop\"), but parse() returns Err naming both the field and the unmet precondition (the gated restartPolicy: OnFailure), instead of silently downgrading to a supported policy. Test refuses_indefinite_lifetime asserts the returned error names both inactivity_seconds and OnFailure."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:148-166"
      - "crates/buzz-backend-kubernetes/src/config.rs:307-320"
  - statement: "buzz-backend-kubernetes exposes a JSON Schema, config_schema(), describing the same fields parse() validates; two tests (schema_default_namespace_round_trips_through_parse, schema_default_image_round_trips_through_parse) assert the schema's own default values successfully round-trip through parse(), so a UI form prefilled from the schema cannot itself fail the validator on submit."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:192-243"
      - "crates/buzz-backend-kubernetes/src/config.rs:398-424"
  - statement: "buzz-backend-kubernetes's ProviderConfig has no field for cluster credentials by design (documented as invariant I2); test credential_fields_have_no_effect asserts that supplying token/client_key JSON fields has no effect on the parsed struct (formatting it with {:?} never contains the supplied value), and a separate test, no_schema_field_trips_the_i2_key_lint, asserts no config_schema() field name contains a banned word (secret, password, token, key, credential)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:64-74"
      - "crates/buzz-backend-kubernetes/src/config.rs:362-377"
      - "crates/buzz-backend-kubernetes/src/config.rs:454-469"
  - statement: "Validation posture is not uniform across every Buzz surface: mobile's RelayConfig.baseUrl getter parses the persisted relay origin with Uri.tryParse and, on a parse failure, returns the raw unparsed string rather than raising an error or substituting a validated default — no explicit validation gate rejects a malformed persisted relay URL at read time in this code path."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart:43-52"
  - statement: "Issue #1059's Definition of Done requires this node, beyond the corpus-wide requirements in AGENTS.md, to define type/shape, source, default/required behavior and validation; to state whether a setting is sensitive/secret, environment-specific, restart-required or dynamically reloadable; to define effects/failure behavior and compatibility/deprecation; and to link implementation and deployment examples without embedding real secrets."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1059 definition of done"
  - statement: "Sibling issues #1051-#1058 each scope one configuration surface's own settings catalog (agent, defaults, desktop, environment, feature-flags, mobile, relay, secrets) as a separate corpus node, so this node is deliberately scoped to the cross-cutting validation mechanism/contract rather than duplicating any one surface's variable list."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1059 Objective, cross-checked against launchpad-26/buzz#1051, #1052, #1053, #1054, #1055, #1056, #1057, #1058 titles"
relationships:
  - type: implements
    target: corpus-template-configuration
---

# Configuration: validation

This node catalogues **how Buzz validates configuration values**, as a mechanism and
contract that recurs across surfaces — not the settings catalog for any one surface.
The relay's environment-variable startup config
(`crates/buzz-relay/src/config.rs`), the Kubernetes agent-launch provider's
JSON `provider_config` (`crates/buzz-backend-kubernetes/src/config.rs`), and (as
a single contrasting data point) mobile's persisted relay connection config are
the concrete surfaces this node draws its mechanisms from. It applies at parse
time and at process/app startup — the point at which a value is first read from
its source and turned into a typed in-memory structure — not to how a valid
value is subsequently used.

## Structured entries

The rows below are the **distinct validation mechanisms** found across these
surfaces, not individual settings — a deliberate adaptation of the
`configuration` template's row shape (see *Boundary* below), because this node
documents the contract itself rather than one surface's variable list.

| Mechanism | Enforced in | Failure mode | Representative example |
|---|---|---|---|
| Per-value type/shape parse | `Config::from_env` (relay, env vars); `parse()` (buzz-backend-kubernetes, JSON) | Fail-fast: `Err(ConfigError::InvalidValue \| InvalidBindAddr)` / `Err(String)`, returned to the caller | `parse_bind_addr` rejects an unparsable `BUZZ_BIND_ADDR`; `optional_u64` rejects a non-numeric JSON value with a field-named message |
| Cross-field / semantic validation | Same `from_env`/`parse` functions, plus a distinct post-parse `.validate()` call | Fail-fast: `Err`, checked once all fields are read | `RELAY_OPERATOR_PUBKEYS` requires `RELAY_OPERATOR_API_ORIGIN`; `MediaConfig::validate`'s upload-header coherence rules; `inactivity_seconds: 0` refused because it needs a gated `restartPolicy` |
| Deprecated/renamed name detection | `Config::from_env` | Fail-fast: hard `Err` naming the replacement, no silent alias | `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` (old name) refused outright |
| Best-effort / non-fatal validation | `Config::from_env` | Warn and drop: `tracing::warn!`, field silently becomes `None` | Malformed `RELAY_OWNER_PUBKEY` is logged and ignored, not a startup error |
| Range clamping | `Config::from_env` | Silent clamp to a maximum, no error surfaced | `BUZZ_DRAIN_JITTER_MS` above `MAX_DRAIN_JITTER_MS` is capped, not rejected |
| Startup invariant enforced outside the `Result`/`Err` type | `main()` directly, after config is loaded | Process `panic!`, not a returned/propagated error | `BUZZ_RELAY_PRIVATE_KEY` required when `BUZZ_REQUIRE_AUTH_TOKEN=true` |
| Secret-shaped value: shape checked, content never asserted | `main()`, after `Config::from_env` | Fail-fast on unparsable shape (`nostr::Keys::parse`); value never logged | `BUZZ_RELAY_PRIVATE_KEY` must parse as a valid keypair |
| No validation gate (fail-open) | Client-side config accessor | Malformed value passed through unchanged, not rejected | Mobile `RelayConfig.baseUrl` returns the raw string on `Uri.tryParse` failure |

## Litmus test

Every mechanism above validates a value that is genuinely deploy-varying in the
Twelve-Factor sense — read from the process environment (`crates/buzz-relay/src/
config.rs`'s `std::env::var` calls) or supplied by a caller at request time
(`buzz-backend-kubernetes`'s `provider_config` JSON payload) rather than
compiled into the binary. This node does not independently re-verify the full
Twelve-Factor argument for why these particular values count as configuration —
`corpus-template-configuration` (this node's `implements` target) already
establishes that for `crates/buzz-relay/src/config.rs`'s pattern, and this node
does not re-litigate it.

## Secrets discipline

No row above, and no sentence in this node, quotes a live credential, key,
token, or hostname value. Where a secret-shaped field is named
(`BUZZ_RELAY_PRIVATE_KEY`, `provider_config`'s absent credential fields), this
node cites the environment variable or field name and the code path that reads
or rejects it, never a value. `buzz-backend-kubernetes`'s discipline is
architectural: `ProviderConfig` simply has no field a credential could occupy
(I2), verified by a test asserting a supplied `token`/`client_key` has no
effect on the parsed struct.

**Not verified**: whether other secret-shaped relay fields visible in
`crates/buzz-relay/src/config.rs` (for example `git_hook_hmac_secret`,
`buzz_media::MediaConfig.s3_secret_key`) receive an equivalent shape check the
way `BUZZ_RELAY_PRIVATE_KEY` does. Only `BUZZ_RELAY_PRIVATE_KEY`'s
`nostr::Keys::parse` check was traced to a validation call; the other fields
were seen read via `std::env::var` with no validation call site found in the
files read for this node, but a full audit of every field in a 1736-line file
was not performed. Named here as a gap, not asserted either way.

## Boundary

This node does not describe:

- **Any single surface's settings catalog** — the full list of relay
  environment variables, agent config fields, desktop/mobile config, feature
  flags, secrets, or defaults. That is `#1051`-`#1058`'s job, each as its own
  corpus node built from `corpus-template-configuration`.
- **The parsing/loading implementation in full** — this node cites specific
  functions (`Config::from_env`, `MediaConfig::validate`,
  `buzz-backend-kubernetes::parse`) as evidence for the *mechanism*, not as a
  complete description of everything those functions do.
- **The corpus's own front-matter schema** (`node.schema.json`) — that is a
  different, unrelated validation system (this repository's documentation
  tooling), not a Buzz product configuration surface, despite also being a
  JSON Schema that validates structured input.
- **Desktop's and mobile's configuration surfaces in full.** Only one mobile
  data point (`RelayConfig.baseUrl`) was traced for this node; desktop's
  agent-configuration and managed-agent config files
  (`desktop/src-tauri/src/commands/agent_config.rs`,
  `desktop/src-tauri/src/managed_agents/global_config`, etc.) were located but
  not read in depth, and are `#1053`'s and `#1051`'s scope, not this node's.
- **This template's own literal row shape.** `corpus-template-configuration`'s
  *Structured entries* section describes a per-variable table (name, type,
  default, required, secret, effect). This node's *Structured entries* table
  instead rows the validation mechanisms themselves, because the subject is
  the contract, not a variable list — a deliberate specialization, not an
  oversight, and named explicitly so a reader comparing this node against the
  template skeleton is not misled.

## Relationships

- `implements`: `corpus-template-configuration` — this node is an instance of
  that template, per the template's own stated convention that a node built
  from it should declare `implements` targeting the template once merged.
- No `references` or `part-of` edges are declared. No sibling
  `layers/configuration/*` node (`#1051`-`#1058`) is merged on
  `origin/launchpad` at the recorded revision, so none is a legal
  `relationships` target — see *Scope and omissions* below.

## Scope and omissions

**This node covers** the validation *mechanism* Buzz applies to configuration
values at parse/startup time, illustrated with concrete, traced examples from
two structurally different surfaces (the relay's environment-variable startup
config and the Kubernetes agent-launch provider's JSON `provider_config`) plus
one contrasting client-side data point (mobile's relay connection config), and
states, per issue `#1059`'s Definition of Done: which mechanisms exist
(type/shape, cross-field, deprecated-name, best-effort, clamping), where each
is enforced, whether the values involved are environment-specific
(all traced examples are) and restart-required (relay: yes, by inference — see
below), and what compatibility/deprecation looks like in practice (the
renamed-variable hard-fail).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Relay environment variables, their individual defaults and effects | `#1057` |
| Agent configuration fields | `#1051` |
| Desktop configuration | `#1053` |
| Mobile configuration (beyond the one traced `RelayConfig.baseUrl` data point) | `#1056` |
| Feature flags | `#1055` |
| Secrets (which values are secret, how they are supplied) | `#1058` |
| Defaults, as a cross-surface catalog | `#1052` |
| Environment-specific configuration as its own concern | `#1054` |
| The corpus's own front-matter validation (`node.schema.json`, `validate.py`) | `launchpad/docs/corpus/AGENTS.md` |
| The `configuration` template's per-variable row shape and its full evidence expectations | `launchpad/docs/corpus/templates/configuration.md` (`corpus-template-configuration`) |

**No `relationships` beyond `implements: corpus-template-configuration`.**
Checked against `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/
corpus` at the recorded revision: no `layers/configuration/*` node exists there
yet — this is the first. The eight sibling tasks (`#1051`-`#1058`) are open,
unmerged batch work at the time this node was written; declaring an edge to any
of them would resolve locally but fail CI's validation against
`origin/launchpad`, per `AGENTS.md`'s own warning about this exact trap.

**Expected but not verified when this node was written:**

- **Whether desktop has an equivalent config-validation mechanism was not
  traced in depth.** Several candidate files were located
  (`desktop/src-tauri/src/commands/agent_config.rs`,
  `desktop/src-tauri/src/managed_agents/global_config`,
  `desktop/src-tauri/src/managed_agents/config_bridge`) but not read; whether
  they validate fail-fast, fail-open, or not at all is unknown from this
  node's evidence.
- **Whether other secret-shaped relay fields** (`git_hook_hmac_secret`,
  `buzz_media::MediaConfig.s3_secret_key`, `BUZZ_S3_ACCESS_KEY`) receive a
  shape check equivalent to `BUZZ_RELAY_PRIVATE_KEY`'s `nostr::Keys::parse`
  call was not established — see *Secrets discipline* above.
- **The "no reload mechanism" claim is a search result, not an exhaustive
  proof.** `rg -i "reload|SIGHUP"` against `crates/buzz-relay/src/config.rs`
  and `crates/buzz-relay/src/main.rs` found no matches; this is evidence for,
  not conclusive proof of, the absence of a reload path elsewhere in the
  relay's dependency graph — hence classified `INFERENCE` with `confidence:
  0.75` rather than `FACT`.
- **Whether `buzz-backend-kubernetes`'s `provider_config` is
  environment-specific in the Twelve-Factor sense the same way relay env vars
  are was not independently argued.** It is caller-supplied per agent-launch
  request rather than read from the process environment, which is a
  structurally different kind of "deploy-varying" than an env var; this node
  notes the distinction in the *Structured entries* table's "Enforced in"
  column but does not resolve whether both belong under the same litmus-test
  reasoning `corpus-template-configuration` establishes for env vars
  specifically.

## Candidate follow-up (not filed)

While tracing `crates/buzz-relay/src/main.rs`'s startup sequence, a second,
separate concept surfaced: the *order* in which multiple independent
validation calls run at relay startup (`Config::from_env` → the
`BUZZ_RELAY_PRIVATE_KEY`/`nostr::Keys::parse` check → `media.validate()` →
database/Redis connection) and what state each failure leaves the process in.
That is a startup-sequencing/flow concern, not a validation-contract concern,
and is not folded into this node.
