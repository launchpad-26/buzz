---
id: layers-observability-structured-logging
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228, which is identical to origin/launchpad's HEAD at authoring time."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "buzz-relay installs a tracing_subscriber registry whose stdout layer calls .json() and overrides the event formatter with a custom formatter, gated by RUST_LOG (default buzz_relay=info)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:8-10"
      - "crates/buzz-relay/src/main.rs:130-136"
  - statement: "buzz-push-gateway installs tracing_subscriber::fmt().json().with_env_filter(EnvFilter::from_default_env()) directly, with no custom event formatter."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs:19-24"
  - statement: "buzz-agent, buzz-acp, buzz-dev-mcp, and buzz-test-client each install tracing_subscriber::fmt() without .json(), producing the crate's plain-text (non-JSON) event format."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs:190-193"
      - "crates/buzz-acp/src/lib.rs:1940-1945"
      - "crates/buzz-dev-mcp/src/lib.rs:174-177"
      - "crates/buzz-test-client/src/main.rs:35-41"
  - statement: "buzz-agent's subscriber is explicitly built with .with_writer(std::io::stderr), and its own ACP wire-protocol frames are written to tokio::io::stdout() by a separate writer task, so the plain-text log stream and the ACP protocol stream are deliberately kept on separate file descriptors."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/lib.rs:189-192"
      - "crates/buzz-agent/src/wire.rs:434"
  - statement: "buzz-acp (the harness that spawns a managed agent subprocess) pipes the child's stdout and inherits its stderr, confirming that the child's stdout carries the ACP wire protocol and stderr carries logs -- consistent with why buzz-agent's own subscriber writes only to stderr rather than to JSON on stdout."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/src/acp.rs:464-467"
      - "crates/buzz-agent/src/lib.rs:189-192"
    confidence: 0.85
  - statement: "buzz-dev-mcp likewise defers tracing_subscriber::fmt() initialization until it has determined it is not running the buzz CLI subcommand, and writes to stderr with ANSI disabled once in MCP-server mode, keeping stdout free for its own stdio-transport MCP protocol."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/lib.rs:163-177"
  - statement: "The relay declares #[tracing::instrument(skip_all, fields(event_id, conn_id))] on handle_auth and #[tracing::instrument(skip_all, fields(event_id, kind))] on handle_event, declaring the span's structured fields empty at the attribute site and populating them later in the function body via tracing::Span::current().record(...) once the values are known."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:42"
      - "crates/buzz-relay/src/handlers/auth.rs:70-73"
      - "crates/buzz-relay/src/handlers/event.rs:607"
      - "crates/buzz-relay/src/handlers/event.rs:614-617"
  - statement: "The buzz-datastore-tracing proc-macro crate's datastore_span attribute macro generates its own #[::tracing::instrument(target = \"buzz_datastore\", name = ..., skip_all, fields(otel.kind = \"client\", db.system.name = \"postgresql\", otel.status_code = ::tracing::field::Empty, ...))] attribute on the annotated function, using tracing::field::Empty as the same deferred-field mechanism, recorded via Span::current().record(\"otel.status_code\", ...) only when the wrapped call returns Err."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:100-134"
  - statement: "No standalone #[instrument] attribute (without a tracing:: or ::tracing:: path prefix) exists anywhere in the crates/ tree; every span-generating instrumentation macro use in this codebase is qualified."
    entry_class: FACT
    evidence:
      - "grep_instrument(crates/, pattern='instrument\\(') -> every match is tracing::instrument or ::tracing::instrument, none is a bare unqualified #[instrument]"
  - statement: "Call sites across the relay use tracing's field-value sigils consistently: a bare field name for typed/Copy values (e.g. kind = kind_u32), %field for Display formatting (e.g. %conn.tenant.host(), %community), and ?field for Debug formatting (e.g. ?invalid_at) -- all three forms appear in the same crate for different value types."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:619"
      - "crates/buzz-relay/src/api/operator.rs:255"
      - "crates/buzz-relay/src/push_runtime.rs:562"
  - statement: "crates/buzz-relay/src/telemetry.rs's TraceContextJson formatter builds on tracing_subscriber::fmt::format().json().flatten_event(true), which flattens an event's fields into the top-level JSON object rather than nesting them under a fields key, and is installed as the event_format for the relay's stdout layer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:53-59"
      - "crates/buzz-relay/src/main.rs:130-136"
  - statement: "TraceContextJson injects trace_id and span_id as lowercase-hex string fields into the emitted JSON object only when the event has a resolvable, valid OpenTelemetry span context; otherwise it falls through to the standard tracing-subscriber JSON format unchanged, and a code comment states Datadog recognizes these two field names specifically when lowercase hex."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:79-83"
      - "crates/buzz-relay/src/telemetry.rs:122-149"
  - statement: "When an event already defines its own trace_id or span_id field (a name collision), the formatter takes a slower path: it re-renders the event to a JSON string, parses it back into a serde_json::Map, overwrites those two keys, and re-serializes -- rather than the allocation-free streaming CorrelationWriter path used for the ordinary, non-colliding case."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:90-115"
      - "crates/buzz-relay/src/telemetry.rs:150-176"
  - statement: "This collision-handling behavior, plus the ordinary correlation path, is exercised by an in-crate unit test that captures rendered JSON log lines against a real OpenTelemetry in-memory span exporter and asserts on trace_id/span_id presence, absence, and value across nested, filtered, and explicit-parent/explicit-root event scenarios."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:307-472"
  - statement: "CONTRIBUTING.md's \"Logging and Tracing\" section instructs contributors to use the tracing crate for all instrumentation and to prefer structured fields over string interpolation, giving tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\") as the preferred form over interpolating those values into the message string -- but states no field-naming convention or JSON-shape detail beyond that preference."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:291-302"
  - statement: "The workspace root Cargo.toml pins tracing = \"0.1\", tracing-subscriber = { version = \"0.3\", features = [\"env-filter\", \"json\"] }, and tracing-opentelemetry = \"0.33\" as shared dependency versions."
    entry_class: FACT
    evidence:
      - "Cargo.toml:85-87"
  - statement: "launchpad/docs/Observability/current-state/relay.md is a pre-existing, non-corpus-schema research document (pinned to an older revision, 678008ea49e790ada52e84d54b47f47dd77c6b38) that already documents the relay's JSON log surface, RUST_LOG default, and a 130-field sensitive-data classification at a broader landscape level; it predates this corpus and is not itself a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/relay.md"
  - statement: "Issue #1144's definition of done requires exactly one hand-authored canonical document with schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE evidence, links to related nodes rather than duplicated content, a check against the recorded provenance revision, and a clean corpus validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1144 definition of done"
  - statement: "As of this node's authoring, issues #1138 (observability-liveness) and #1139 (logging) -- the task brief's stated sibling nodes -- are both still OPEN with no associated pull request, and no layers/ directory exists anywhere under launchpad/docs/corpus on origin/launchpad; the brief's premise that they are already merged does not hold at this revision."
    entry_class: FACT
    evidence:
      - "gh_issue_view(launchpad-26/buzz#1139, field=state) -> OPEN"
      - "gh_pr_list(launchpad-26/buzz, search=1139, state=all) -> no results"
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ path present"
  - statement: "Issue #1136 (document layers/observability/datastore-tracing.md), the sibling task that owns the buzz-datastore-tracing crate's own field policy in depth, is also OPEN with no merged content at this revision."
    entry_class: FACT
    evidence:
      - "gh_issue_view(launchpad-26/buzz#1136, field=state) -> OPEN"
---

# Structured logging

Structured logging in Buzz means emitting `tracing` events and spans as key-value
fields attached to a machine-parseable record, rather than interpolating those
values into a free-text message string. This node documents the mechanics of that
convention as implemented in this repository: how fields are declared and
populated, how they are shaped into JSON, and where that JSON shape diverges by
process.

## Scope and non-goals

**This node covers** the field-population mechanics (`#[instrument(fields(...))]`
plus deferred `Span::current().record(...)`), the sigil conventions used at
`tracing` call sites (bare / `%` / `?`), the concrete JSON-shape and
trace/span-correlation mechanism the relay's custom event formatter implements,
and which Buzz processes emit JSON logs versus plain text and why.

**It does not cover, and these are named gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The general logging landscape across the whole codebase -- which crates log at all, per-crate log volume, `console.*`/`debugPrint` usage on desktop/mobile | #1139 (`layers/observability/logging.md`), not yet merged at this revision -- no `relationships` edge is declared to it because the target does not exist on `origin/launchpad` yet |
| The `buzz-datastore-tracing` crate's own field policy, redaction rules, and `db.system.name`/`otel.kind` semantic-convention choices in depth | #1136 (`layers/observability/datastore-tracing.md`), also not yet merged |
| OpenTelemetry export configuration, OTLP batching, and the `OTEL_*` environment variables that gate it | #1141 (`layers/observability/opentelemetry.md`) |
| Prometheus metrics (a separate `metrics` facade, not `tracing` fields) | #1140/#1142 |
| Health/readiness probe response shapes | #1137/#1143 |
| Sensitive-field classification and redaction policy for logged values | `launchpad/docs/Observability/current-state/relay.md`'s "Sensitive-data handling" section, which performed a 130-field classification against an older revision; not repeated here |

## Field-population mechanics: `#[instrument]` and deferred `record`

Two of the relay's handler functions declare their span's structured fields
up front, empty, and populate them once the real values are known -- rather than
requiring every field to be known at the function's entry point:

```rust
#[tracing::instrument(skip_all, fields(event_id, conn_id))]
pub async fn handle_auth(event: nostr::Event, conn: Arc<ConnectionState>, state: Arc<AppState>) {
    let event_id_hex = event.id.to_hex();
    let (challenge, conn_id) = { /* ... */ };
    // Record the declared span fields now that we have the values.
    tracing::Span::current()
        .record("event_id", event_id_hex.as_str())
        .record("conn_id", conn_id.to_string().as_str());
    // ...
}
```

`skip_all` opts the whole argument list out of automatic field capture (the
`event`, `conn`, and `state` parameters are not cheap or safe to log wholesale),
and `fields(event_id, conn_id)` reserves two named slots on the span that start
empty and get filled in later. `handlers/event.rs`'s `handle_event` follows the
identical shape with `fields(event_id, kind)`.

`crates/buzz-datastore-tracing` -- a proc-macro crate, not a normal library --
generates a variant of the same pattern for every function it annotates with
`#[datastore_span(name = "...", system = "postgresql")]`. It expands to:

```rust
#[::tracing::instrument(
    target = "buzz_datastore",
    name = "...",
    skip_all,
    fields(
        otel.kind = "client",
        db.system.name = "postgresql",
        otel.status_code = ::tracing::field::Empty
        /* extra caller-supplied fields */
    )
)]
```

`tracing::field::Empty` is the explicit form of the same deferred-field idea used
implicitly above by the relay handlers (an unassigned `fields(name)` entry is
already empty until recorded) -- the generated code records
`"otel.status_code"` only when the wrapped call returns `Err`, leaving it absent
from the span on the success path rather than recording a placeholder value.
This crate's own field and redaction policy beyond this mechanical pattern is
#1136's subject, not repeated here.

## Sigil conventions at call sites

Across `crates/buzz-relay`, three field-value forms appear side by side for
different value shapes:

- **Bare** (`kind = kind_u32`, `reaped`) -- a value that is already `Copy`/cheap
  to move into the field, or where `tracing`'s `Value` impl covers the type
  directly (e.g. integers).
- **`%field`** (`%conn.tenant.host()`, `%community`, `%error`) -- formats the
  value with its `Display` impl. Used for types like UUIDs, hex-encoded IDs, and
  error values where a human-readable rendering is wanted.
- **`?field`** (`?invalid_at`) -- formats the value with its `Debug` impl. Used
  where no `Display` impl exists or the debug rendering is the more useful one.

All three appear within the same crate depending on the value's type, not as a
project-wide convention that always prefers one -- there is no lint or written
rule in this repository enforcing a single sigil per field name.

## JSON shape and trace correlation

The relay's stdout tracing layer does not use the stock `tracing_subscriber` JSON
formatter directly. It installs a custom `event_format`, `TraceContextJson`
(`crates/buzz-relay/src/telemetry.rs`), built on top of
`tracing_subscriber::fmt::format().json().flatten_event(true)`. `flatten_event(true)`
is what puts an event's fields directly at the top level of the JSON object
(`{"message": "...", "conn_id": "...", ...}`) instead of nesting them under a
separate `"fields"` key.

On top of that stock shape, `TraceContextJson` adds exactly one behavior: when
the event resolves to a valid OpenTelemetry span context, it injects `trace_id`
and `span_id` as lowercase-hex string fields into the same JSON object, so a
stdout log line can be joined to its exported OTLP span. A code comment in the
same file states the reason for that specific casing: "Datadog recognizes the
OpenTelemetry-standard `trace_id` and `span_id` fields when they are lowercase
hexadecimal strings." Two code paths exist depending on whether the event
already defines fields with those exact names:

- **Ordinary case (no collision):** a `CorrelationWriter` wraps the underlying
  writer and splices the two fields in immediately after the JSON object's
  opening brace, streaming the rest of the line through unchanged -- no
  intermediate allocation of the full line.
- **Collision case** (the event itself defines a `trace_id` or `span_id`
  field): the formatter renders the full line into a `String`, parses it back
  into a `serde_json::Map`, overwrites the two keys, and re-serializes. This is
  the slower path, taken only when a caller's own field names happen to collide.

Events outside any valid span, or emitted while OTel is disabled entirely
(`OTEL_EXPORTER_OTLP_ENDPOINT` unset), pass through the stock JSON formatter with
no `trace_id`/`span_id` fields at all -- there is no placeholder or null value
for them. This whole formatter, both code paths, is exercised by a unit test that
captures rendered JSON against a real in-memory OTel exporter across nested,
filtered, and explicit-parent/root scenarios (`crates/buzz-relay/src/telemetry.rs`,
test module).

## Which processes emit JSON, and why some deliberately do not

Two of Buzz's Rust binaries emit JSON-structured logs on stdout:

- **`buzz-relay`** — `tracing_subscriber::fmt().json()` plus the custom
  `TraceContextJson` event formatter described above, gated by `RUST_LOG`
  (default `buzz_relay=info`).
- **`buzz-push-gateway`** — a plain `tracing_subscriber::fmt().json()`, gated
  by `RUST_LOG` via `EnvFilter::from_default_env()`, with no custom formatter.

Four other binaries deliberately install a plain-text (non-JSON) formatter
instead:

- **`buzz-agent`** writes logs to `std::io::stderr` explicitly
  (`.with_writer(std::io::stderr)`), while a separate writer task streams its
  ACP wire-protocol frames to `tokio::io::stdout()`. `buzz-acp` (the harness that
  spawns `buzz-agent` as a managed subprocess) pipes the child's stdout and
  inherits its stderr — confirming stdout is reserved for the ACP protocol and
  stderr for logs, rather than an arbitrary choice.
- **`buzz-acp`** itself installs `tracing_subscriber::fmt().compact()` with an
  `EnvFilter` (default `buzz_acp=info`), deferred until after its own CLI
  subcommand branches (`models`, `auth-methods`, `authenticate`) return early.
- **`buzz-dev-mcp`** installs `tracing_subscriber::fmt().with_writer(std::io::stderr)`,
  and only after determining it is not running the `buzz` CLI subcommand — it
  serves an MCP stdio transport, which also needs stdout kept clear of anything
  but protocol frames.
- **`buzz-test-client`** installs a plain `tracing_subscriber::fmt()` with an
  `EnvFilter` (default `buzz_test_client=debug`); it is a test/integration
  binary rather than a service whose logs feed a log pipeline, so no JSON
  requirement applies.

The pattern across the four plain-text binaries is consistent: each is either a
CLI tool whose stdout is read by a human, or a process whose stdout is a
different, non-logging wire protocol (ACP JSON-RPC frames, MCP stdio). JSON
structured logging in this repository is a property of the two long-running
services meant to be scraped by a log pipeline, not a project-wide rule applied
to every binary.

## Relationship to project-wide style guidance

`CONTRIBUTING.md`'s "Logging and Tracing" section states the project-wide
preference — structured fields over string interpolation — with one example
(`channel_id = %id, event_kind = kind`). It does not specify a field-naming
convention, a required sigil per type, or the JSON-shape details this node
documents; those are established here by reading the actual implementation
rather than a written style rule.

## Scope and omissions

**No `relationships` entry is declared.** The natural target,
`layers-observability-logging` (#1139), does not exist as a node on
`origin/launchpad` at this revision — confirmed by direct check
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), not
assumed. Per `launchpad/docs/corpus/AGENTS.md`, an edge may only name a node
present on the branch being merged into; adding one here would be a hard
validation error the moment this document reaches CI. If and when #1139 merges,
a `references` edge from this node to it (and vice versa) would be the
appropriate follow-up edit, made against that node's actual content rather than
guessed at now.

**Expected but not verified when this node was written:**

- **Desktop and mobile logging conventions were not surveyed.** This node covers
  only the Rust `tracing`-based structured logging in `crates/`; whether the
  desktop (TypeScript/React) or mobile (Flutter) clients have an analogous
  structured-field convention is out of scope here and, per the table above, is
  #1139's subject.
- **Whether every `#[instrument]` call site in the relay was found.** The search
  for `instrument(` covered `crates/` exhaustively at this revision, but new call
  sites can be added at any time; this node describes the pattern and cites
  representative examples, not an exhaustive inventory.
- **Runtime JSON output was not captured from a live relay process for this
  node.** The JSON shape described above is read from the formatter's source and
  its unit tests, not from observing a running process's stdout directly;
  `launchpad/docs/Observability/current-state/relay.md` performed that kind of
  runtime capture (at an older revision) and is the place to look for measured
  output.
