---
id: operations-observability-logs
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "CONTRIBUTING.md's \"Logging and Tracing\" section states the repository-wide convention: use the tracing crate for all instrumentation, and prefer structured fields (tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\")) over string interpolation."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:291-302"
  - statement: "buzz-relay's main() installs a tracing_subscriber::registry() carrying a fmt::layer().json() stdout layer with a custom event formatter, gated by an EnvFilter built from the RUST_LOG environment variable via a log_env_filter helper that falls back to \"buzz_relay=info\" when RUST_LOG is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:6-10"
      - "crates/buzz-relay/src/main.rs:130-136"
  - statement: "When OTEL_EXPORTER_OTLP_ENDPOINT is set, buzz-relay additionally attaches an OpenTelemetry tracing layer that exports spans via OTLP gRPC alongside the same JSON stdout logs; this layer is filtered independently via BUZZ_OTEL_FILTER (falling back to \"buzz_relay=info,buzz_datastore=info\" when unset), deliberately separate from the RUST_LOG-driven stdout filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:113-141"
      - "crates/buzz-relay/src/telemetry.rs:183-184"
  - statement: "The relay's stdout JSON formatter (TraceContextJson, built on tracing_subscriber::fmt::format().json().flatten_event(true)) flattens each event's fields, including any caller-supplied fields and the standard message field, into one top-level JSON object rather than nesting them under a fields key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:55"
  - statement: "The formatter's own in-crate test module captures rendered JSON lines and asserts concrete keys: message and arbitrary caller fields (e.g. answer) always appear at the top level; trace_id and span_id appear as lowercase-hex strings (32 and 16 characters respectively) only on events that resolve to a valid OpenTelemetry span context, and are absent entirely (no null placeholder) otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:391-401"
      - "crates/buzz-relay/src/telemetry.rs:422-424"
  - statement: ".env.example documents RUST_LOG, BUZZ_OTEL_FILTER and OTEL_EXPORTER_OTLP_ENDPOINT together under a \"Logging / Tracing\" heading, with RUST_LOG given a concrete multi-target default (buzz_relay=debug,buzz_datastore=info,buzz_db=debug,buzz_auth=debug,buzz_pubsub=debug,tower_http=debug) for local development, and the other two commented out (OTEL export disabled by default)."
    entry_class: FACT
    evidence:
      - ".env.example:174-183"
  - statement: "deploy/compose/.env.example — the environment file for the single-VPS production Compose bundle — sets a different, uniformly info-level RUST_LOG default (buzz_relay=info,buzz_db=info,buzz_auth=info,buzz_pubsub=info,tower_http=info) and defines no BUZZ_OTEL_FILTER or OTEL_EXPORTER_OTLP_ENDPOINT variable at all, so OTLP trace export stays disabled in that bundle unless an operator adds those variables themselves."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example:22"
  - statement: "deploy/charts/buzz's Helm chart sets no RUST_LOG or other log-level value anywhere in its default values.yaml or in the relay container's hardcoded env block in templates/deployment.yaml; the only operator-facing knob for injecting one is the generic relay.extraEnv / relay.extraEnvFrom list (defaulting to an empty array), which templates/deployment.yaml splices into the relay container's env after its hardcoded entries."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:202-203"
      - "deploy/charts/buzz/templates/deployment.yaml:228-231"
  - statement: "The Justfile's logs recipe runs `docker compose logs -f {{ARGS}}` against the repository root's docker-compose.yml, whose services are postgres, redis, adminer, keycloak, minio, minio-init and prometheus — backing services only, with no relay service defined."
    entry_class: FACT
    evidence:
      - "Justfile:81-83"
      - "docker-compose.yml"
  - statement: "The Justfile's relay recipe starts the relay for local development by sourcing .env and running `cargo run -p buzz-relay` directly, not as a container, so the relay's own JSON stdout goes to whatever terminal invoked `just relay`; `just logs` (which only reaches the root compose project) therefore never shows the relay's own log stream in local development."
    entry_class: FACT
    evidence:
      - "Justfile:465-472"
  - statement: "deploy/compose/compose.yml — the single-VPS production Compose bundle, distinct from the root docker-compose.yml — defines a relay service that runs the buzz-relay binary itself as a container, alongside postgres, redis, minio and minio-init."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/run.sh's logs subcommand runs `compose logs -f \"${@:-relay}\"`, defaulting to the relay service when no service argument is given; launchpad/deploy/run.sh is a guard wrapper whose every subcommand, including logs, execs straight into deploy/compose/run.sh with the same arguments, so `./launchpad/deploy/run.sh logs` reaches the identical command."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:75-78"
      - "launchpad/deploy/run.sh:7"
      - "launchpad/deploy/run.sh:130"
  - statement: "Neither docker-compose.yml nor deploy/compose/compose.yml declares a logging: key on any service, so both rely on Docker Compose's default json-file logging driver rather than a repository-configured driver, size cap, or rotation policy."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "deploy/compose/compose.yml"
  - statement: "deploy/charts/buzz's templates directory contains no log-shipping sidecar container (no fluent-bit, logstash, filebeat, or vector container definition anywhere under templates/), so a relay Pod's stdout is captured only by whatever the surrounding Kubernetes cluster's own node-level log pipeline does with container stdout; that pipeline is not part of this chart."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "crates/buzz-relay/src/config.rs's KlipyConfig struct carries a private api_key field and a hand-written Debug impl that renders it as the literal string \"[REDACTED]\" instead of the real value, specifically so that a {:?}-formatted dump of the surrounding Config cannot disclose it; this is the one deliberate log/debug redaction mechanism found in the relay's configuration surface, and it is exercised by an in-crate unit test asserting the debug string contains \"[REDACTED]\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:88-110"
      - "crates/buzz-relay/src/config.rs:1269-1275"
  - statement: "Config itself (the struct KlipyConfig is nested inside) derives Debug via #[derive(Debug, Clone)] rather than a custom, redacting implementation, and its fields include database_url: String (a Postgres connection URL, which commonly embeds credentials) with no redaction; no call site under crates/buzz-relay/src was found that logs or debug-formats the whole Config value (only individual scalar fields, e.g. config.health_port and config.bind_addr, are passed to tracing macros by name)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:117"
      - "crates/buzz-relay/src/main.rs:1299"
      - "crates/buzz-relay/src/main.rs:1374"
  - statement: "A pre-existing, non-corpus research document, launchpad/docs/Observability/current-state/relay.md (pinned to an older revision, 678008ea49e790ada52e84d54b47f47dd77c6b38), performed a source classification of 130 relay field keys and concluded that no field it found carries a database connection string, authentication token, private key, or environment dump by construction, while noting arbitrary error text and up to 64 KiB of raw Git subprocess stderr as the most open-ended, unproven-safe surfaces; it also states plainly: \"No redaction, collection, access, or retention policy is defined here.\""
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/relay.md:179-202"
  - statement: "The same document states that the relay's standard-output JSON log stream has no product-side OTLP log exporter and that persistence of that stream \"depends on whatever launches and captures that stream\" — i.e. this repository defines no log retention policy of its own; retention, if any, is a property of whatever terminal, Docker daemon, or Kubernetes node log pipeline captures the process's stdout."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/relay.md:94-98"
  - statement: "Issue #1211's batch dispatch brief states that metrics (#1212), traces (#1213), alerts (#1209) and dashboards (#1210) are sibling operations/observability reference nodes being authored in the same batch run, and instructs this node to name that boundary in prose without declaring relationships to them, since none is merged on origin/launchpad at this revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1211 batch dispatch brief (corpus-batch-author, Feature #618 batch run)"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a Reference description, structured entries, an optional Commands table, an explicit boundary statement, relationships, and a scope-and-omissions section — the shape this node's body follows."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-observability-logging
  - type: references
    target: layers-observability-structured-logging
  - type: references
    target: architecture-deployment-docker-compose
  - type: references
    target: architecture-deployment-kubernetes
---

# Logs: reference

This node catalogues the operator-facing logging surface of `buzz-relay`: how log
verbosity is configured, what shape the emitted log lines take, where those log
lines land once the relay runs under Docker Compose or Kubernetes, and the
commands an operator runs to actually read them. It is the lookup surface for
"how do I turn up log verbosity" or "where do I find the relay's logs right
now" — for *why* the logging pipeline is built the way it is (subscriber
mechanics, JSON-shape internals, per-surface conventions across the whole
workspace), see `layers-observability-logging` and
`layers-observability-structured-logging`, which this node references rather
than repeats.

## Configuration and output shape

| Field / Item | Description | Example |
|---|---|---|
| `RUST_LOG` | Filters the relay's stdout JSON log layer. Read via a `log_env_filter` helper that falls back to `"buzz_relay=info"` when unset. Local development's `.env.example` sets a debug-heavy, multi-target default; the production Compose bundle's `deploy/compose/.env.example` sets a uniformly `info`-level default instead. | `RUST_LOG=buzz_relay=debug,buzz_datastore=info,buzz_db=debug,buzz_auth=debug,buzz_pubsub=debug,tower_http=debug` (`.env.example`) |
| `BUZZ_OTEL_FILTER` | Filters the *separate* OpenTelemetry export layer, independent of `RUST_LOG`, so raising or lowering stdout log verbosity cannot silently drop parent spans from an exported trace. Falls back to `"buzz_relay=info,buzz_datastore=info"` when unset. Only relevant when `OTEL_EXPORTER_OTLP_ENDPOINT` is also set. | `BUZZ_OTEL_FILTER=buzz_relay=info,buzz_datastore=info` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | When set, attaches an OpenTelemetry tracing layer alongside the JSON stdout logs; trace/span export, not log export, is what this variable gates. Absent from `deploy/compose/.env.example` entirely, so the production Compose bundle ships with OTLP export disabled unless an operator adds it. | `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` |
| Output format | Always newline-delimited JSON on stdout, produced by a custom `tracing_subscriber` event formatter (`TraceContextJson`) built on `.json().flatten_event(true)`. Not configurable to plain text — there is no environment variable that switches the relay's own log format. | one JSON object per line |
| Top-level fields (every line) | `message` and any caller-supplied structured fields (e.g. `channel_id`, `event_kind`) sit at the top level of the same JSON object — `flatten_event(true)` means they are never nested under a `fields` key. Standard `tracing_subscriber` JSON also carries `timestamp`, `level`, and `target`, which this node did not re-verify field-by-field beyond what the formatter's own test asserts (`message` and caller fields). | `{"message":"root event","answer":42,...}` |
| `trace_id` / `span_id` | Injected as lowercase-hex strings (32 and 16 hex characters respectively) only on events that resolve to a live OpenTelemetry span context; absent — not null, not present as an empty string — on every other line, including when OTLP export is disabled entirely. | `{"trace_id":"…32 hex chars…","span_id":"…16 hex chars…"}` |
| Per-binary format | `buzz-relay` and `buzz-push-gateway` emit JSON; `buzz-agent`, `buzz-acp`, `buzz-dev-mcp`, and `buzz-test-client` emit plain text instead, several of them deliberately keeping stdout free for a non-logging wire protocol. Full per-binary detail, and the reasoning behind each choice, is `layers-observability-logging`'s and `layers-observability-structured-logging`'s territory, not repeated here. | — |

## Where logs land, and how to reach them

| Environment | Where the JSON lines go | How an operator reaches them |
|---|---|---|
| Local development (`just relay`) | The relay runs directly via `cargo run -p buzz-relay`, not as a container, so its stdout goes straight to whichever terminal invoked `just relay`. | Read that terminal directly. `just logs` does **not** show it — see below. |
| Root `docker-compose.yml` (`just logs`) | This project defines only backing services (`postgres`, `redis`, `adminer`, `keycloak`, `minio`, `minio-init`, `prometheus`) — no `relay` service. Docker Compose's default `json-file` logging driver applies; no repository config overrides it. | `just logs` (all services) or `just logs <service>`, both wrapping `docker compose logs -f`. This never includes the relay's own log stream in local development. |
| Production Compose bundle (`deploy/compose/`) | `deploy/compose/compose.yml` runs `buzz-relay` itself as the `relay` service, alongside `postgres`, `redis`, `minio`, `minio-init`. Same default `json-file` driver; no `logging:` override. | `./deploy/compose/run.sh logs` (defaults to the `relay` service) or `./launchpad/deploy/run.sh logs`, an exec-wrapper that reaches the identical command; `docker compose logs -f relay` reaches the same output directly. |
| Kubernetes (`deploy/charts/buzz`) | The relay Pod's container stdout is captured by whatever the cluster's own node-level log pipeline does with container stdout. No log-shipping sidecar (fluent-bit, logstash, filebeat, vector) is defined anywhere in the chart's `templates/`. | `kubectl logs <relay-pod>` (or `kubectl logs -f deployment/<release>-buzz`) reads it directly from the container runtime; any further aggregation is the cluster operator's own pipeline, outside this chart. |

Log level in Kubernetes has no dedicated chart value (no `logLevel` or
equivalent in `values.yaml`): an operator sets `RUST_LOG` there via the
generic `relay.extraEnv` list, which `templates/deployment.yaml` appends to
the relay container's hardcoded environment entries.

## Commands

| Command | Description | Argument | Example |
|---|---|---|---|
| `just logs` | Tail the root Compose project's backing-service containers. Does not include the relay's own logs in local dev (see table above). | `*ARGS` — passed through to `docker compose logs -f` | `just logs postgres` |
| `docker compose logs -f [service]` | Direct Compose invocation, equivalent to what the wrappers above call. Omitting `service` follows every container in that project. | optional service name | `docker compose logs -f relay` (inside `deploy/compose/`) |
| `./deploy/compose/run.sh logs [svc]` | Production Compose bundle's own wrapper. Defaults to the `relay` service when no argument is given. | optional service name, default `relay` | `./deploy/compose/run.sh logs` |
| `./launchpad/deploy/run.sh logs [svc]` | Launchpad's guard wrapper; execs straight into the command above with the same arguments. | optional service name, default `relay` | `./launchpad/deploy/run.sh logs` |
| `kubectl logs <pod-or-selector>` | Standard Kubernetes log read against a relay Pod. Not wrapped by anything in this chart. | pod name, or `-l`/`deployment/...` selector, plus optional `-f` | `kubectl logs -f deployment/buzz-buzz` |

## Redaction and retention

**Redaction.** Exactly one deliberate log/debug redaction mechanism exists in
the relay's configuration surface: `KlipyConfig`'s hand-written `Debug` impl
renders its `api_key` field as the literal string `[REDACTED]`, guarding
against a `{:?}`-formatted dump of the surrounding `Config` disclosing that
key, and an in-crate unit test asserts the redacted string appears. That
protection is scoped to `KlipyConfig` specifically — the surrounding `Config`
struct derives a plain, unredacted `Debug`, and its `database_url` field (a
Postgres connection URL, which commonly embeds credentials) is not redacted by
that derive. No call site found under `crates/buzz-relay/src` logs or
debug-formats the whole `Config` value today — only individual scalar fields
(e.g. a health-check port, a bind address) are passed to `tracing` macros by
name — so this is reported as a real gap in the redaction surface rather than
an active leak: nothing in this repository currently causes it, but nothing in
this repository prevents it either, the way `KlipyConfig`'s impl does for the
one field it covers. A pre-existing, non-corpus research document
(`launchpad/docs/Observability/current-state/relay.md`, pinned to an older
revision) separately classified 130 actually-emitted field keys and found none
carrying a database connection string, token, or private key by construction —
consistent with this node's own finding, since that classification covered
fields relay code actually logs, not a hypothetical whole-`Config` dump.

**Retention.** No log retention or rotation policy is configured anywhere in
this repository. Neither Compose file sets a `logging:` key on any service, so
both fall back to Docker Compose's default `json-file` driver with no
repository-set size cap or rotation. The Kubernetes chart ships no
log-shipping sidecar, so retention there is entirely a property of the
surrounding cluster's own log pipeline, outside this chart's scope. The
pre-existing research document cited above states this directly for the
relay's stdout stream: "No redaction, collection, access, or retention policy
is defined here," and separately that persistence of the stdout JSON stream
"depends on whatever launches and captures that stream" — this node's own
source reading is consistent with both statements.

## Boundary

This node does not describe:

- **Why the logging pipeline is built this way, or how its mechanics work
  internally** — the subscriber/formatter code, the field-population pattern,
  the sigil conventions, and the full per-binary survey are
  `layers-observability-logging`'s and `layers-observability-structured-logging`'s
  territory; this node links them rather than repeating that content.
- **How to accomplish a diagnostic task step by step** — this is a lookup
  table, not a runbook. No procedure/how-to node for log-based diagnosis
  exists in this corpus at the time of writing.
- **Metrics, traces, alerts, or dashboards** — `operations/observability/`
  sibling reference nodes for those four subjects are being authored in the
  same batch run as this one and are not yet merged on `origin/launchpad`, so
  no `relationships` edge names them; a future edit to this node (or to them)
  is the right place to cross-link once they exist.
- **Downstream, Block-internal log ingestion** (the `CAKE`-compatible JSON
  format the relay's own source comment mentions, or Datadog log ingestion) —
  that pipeline lives outside this repository and was not inspected here.
- **An API Reference for a structured-field schema** — no such schema is
  catalogued here; `layers-observability-structured-logging` states plainly
  that a field-naming catalogue does not exist in this repository today.

## Relationships

- `references` → `layers-observability-logging` — the general logging
  convention and per-surface subscriber survey this node's Configuration table
  summarizes operator-relevant slices of.
- `references` → `layers-observability-structured-logging` — the JSON-shape
  and trace-correlation mechanics behind the Configuration table's `trace_id`
  / `span_id` row.
- `references` → `architecture-deployment-docker-compose` — the Compose
  topology (root vs. `deploy/compose/`) this node's "Where logs land" table
  depends on without re-describing.
- `references` → `architecture-deployment-kubernetes` — the Helm chart
  topology (single relay Deployment, no log-shipping sidecar) this node's
  Kubernetes row depends on without re-describing.

No relationship is declared toward the sibling `operations/observability/`
nodes for metrics, traces, alerts, or dashboards — see *Boundary* above for
why.

## Scope and omissions

**This node covers** `buzz-relay`'s log-level configuration (`RUST_LOG`,
`BUZZ_OTEL_FILTER`), its JSON output shape and trace-correlation fields at the
level an operator needs to read a log line, where those logs land under local
development, the production Compose bundle, and the Kubernetes chart, the
commands to reach them in each environment, and what this repository does and
does not do about redaction and retention.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| General logging convention and per-surface subscriber mechanics across the whole workspace (desktop, mobile, CLI tools) | `layers-observability-logging` |
| Structured-field population mechanics, sigil conventions, and JSON-formatter internals | `layers-observability-structured-logging` |
| Datastore tracing policy-macro field/redaction choices (`buzz-datastore-tracing`) | `layers-observability-datastore-tracing` |
| Metrics | Sibling task #1212, `operations/observability/metrics.md`, not yet merged |
| Traces | Sibling task #1213, `operations/observability/traces.md`, not yet merged |
| Alerts | Sibling task #1209, `operations/observability/alerts.md`, not yet merged |
| Dashboards | Sibling task #1210, `operations/observability/dashboards.md`, not yet merged |
| Downstream Block-internal log ingestion (`CAKE`, Datadog) | Outside this repository |
| Compose/Kubernetes deployment topology beyond what this node's log-location table needs | `architecture-deployment-docker-compose`, `architecture-deployment-kubernetes` |

**Expected but not verified when this node was written:**

- **Whether any code path outside `crates/buzz-relay/src` logs or
  debug-formats the whole `Config` value**, which would bypass `KlipyConfig`'s
  redaction and disclose `database_url` in plaintext. This node's search was
  scoped to `crates/buzz-relay/src` and found no such call site there, but did
  not extend to every crate in the workspace.
- **Whether Block's internal, staging-cluster log pipeline (operated via the
  private `squareup/block-coder-tf-stacks` repository, referenced from
  `AGENTS.md`'s ecosystem table) adds its own log-shipping sidecar or
  retention policy on top of the OSS chart documented here.** That repository
  is not present in this checkout and could not be inspected.
- **Runtime JSON output was not captured from a live relay process for this
  node.** The shapes and fields above are read from the formatter's source and
  its own unit tests, not from observing a running process's stdout directly.
  `launchpad/docs/Observability/current-state/relay.md` performed that kind of
  runtime capture, at an older pinned revision, and remains the place to look
  for measured output.
- **Whether the standard `timestamp`, `level`, and `target` fields
  `tracing_subscriber`'s stock JSON formatter normally emits survive unchanged
  through the relay's custom formatter** was not re-verified field-by-field
  here beyond what the formatter's own test module asserts (`message` and
  caller-supplied fields); this node reports that test's actual assertions
  rather than assuming the stock shape is untouched.
