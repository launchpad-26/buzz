---
id: layers-observability-datastore-tracing
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
  - statement: "crates/buzz-datastore-tracing/Cargo.toml describes the crate as \"Privacy-preserving datastore tracing policy macros for Buzz\" and declares itself proc-macro only (`[lib] proc-macro = true`, no other lib target); its only source file is src/lib.rs, and it exposes exactly one public item: the `#[datastore_span]` attribute macro."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml"
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "`datastore_span`'s own doc comment states it \"instruments an async logical datastore operation according to Buzz policy\": PostgreSQL spans always omit function arguments, use the `buzz_datastore` target, and expose only canonical semantic fields plus explicitly supplied safe fields; an `Err` sets `otel.status_code` without inspecting the error value itself. The macro rejects any function it is applied to that is not `async` (a compile error via `Error::new_spanned`), and rejects any `system` argument other than the literal string `\"postgresql\"` at compile time with the message \"unsupported datastore system; only `postgresql` is currently supported\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "The macro's generated code wraps the annotated function body to: time the call with `std::time::Instant`; record a `metrics::histogram!(\"buzz_db_operation_duration_seconds\", \"operation\" => name, \"outcome\" => outcome)` sample on every call (outcome is `\"error\"` only when the return type is `Result` and the value is `Err`, otherwise `\"success\"`); and, when the elapsed time is >= 500ms, emit a `tracing::warn!` event at `target: \"buzz_datastore\"` carrying only `operation`, `outcome`, and `elapsed_ms` — no function arguments, no error value, no return value are ever formatted into either the span, the metric labels, or the slow-operation log line."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "The slow-operation log path is sampled, not unconditional: a per-call-site `static AtomicU64` counter increments on every slow (>=500ms) completion, and the `tracing::warn!` event fires only when that counter's post-increment value is a multiple of 100 (`% 100 == 0`) — so the first slow call at a given call site logs, and the next 99 are suppressed."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "crates/buzz-datastore-tracing/tests/runtime.rs's `exports_policy_fields_without_error_or_argument_data` test builds a real `tracing_opentelemetry` layer over an `InMemorySpanExporter`, calls an annotated function with a raw secret string as an argument and as an `Err` payload (`DIRECT_ERROR`, `QUESTION_ERROR`), and asserts on the exported spans that: the span name and `otel.kind = \"client\"`/`db.system.name = \"postgresql\"` attributes are present, the `limit` field (an explicitly listed safe field) is present, the `direct_error`/`question_error` arguments are never present as attributes, and neither raw secret string appears anywhere in the exported span's `{:?}` debug output or its events — a positive-and-negative check on the redaction claim, not merely on the fields the macro is supposed to add."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/tests/runtime.rs"
  - statement: "The same test file's `slow_operation_logging_is_guarded_sampled_and_redacted` test drives one 1ms call and two consecutive 510ms calls through a `#[datastore_span]`-annotated function that always returns `Err(DIRECT_ERROR)`, and asserts exactly one \"slow datastore operation\" event is captured across the two slow calls (confirming the 1-in-100 sampling), that its four fields are exactly `message`, `operation`, `outcome`, `elapsed_ms` (no fifth field), and that the raw error string never appears in the captured event's debug output."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/tests/runtime.rs"
  - statement: "A repository-wide count of `#[datastore_span` attribute usages at the recorded revision, by crate, is: `buzz-db` 251 (one attribute per data-access method across store modules such as user.rs, event.rs, channel.rs, workflow.rs, moderation.rs, and buzz-db's own runtime/replica_fence.rs), `buzz-audit` 3 (crates/buzz-audit/src/service.rs's `AuditService::log` and two other methods), `buzz-search` 1 (crates/buzz-search/src/query.rs), `buzz-relay` 1 (crates/buzz-relay/src/handlers/command_executor.rs), and `buzz-datastore-tracing` 2 (its own two test fixtures in tests/runtime.rs, exercising the macro rather than instrumenting real production data access) — 258 usages in total, 256 of them production call sites in four consuming crates. Every one of these 258 usages sets `system = \"postgresql\"` — no usage names any other system, and the macro's own compile-time check (above) means no other value could compile."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs"
      - "crates/buzz-db/src/store/event.rs"
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-datastore-tracing/tests/runtime.rs"
  - statement: "crates/buzz-pubsub (Redis) does not import or use `datastore_span` anywhere in its source, and `launchpad/docs/corpus/templates/datastore.md` (a merged corpus node) independently records this same gap as deliberate and enforced, not merely unexercised: `buzz-datastore-tracing`'s own macro implementation rejects any `system` value other than `\"postgresql\"` at compile time. This node treats that restriction as already established fact rather than re-deriving it, citing the template that first named it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "crates/buzz-relay/src/telemetry.rs's `otel_env_filter` function builds the `EnvFilter` used specifically for the OpenTelemetry span-export layer, and its own doc comment states this is \"intentionally independent from `RUST_LOG`: changing stdout log verbosity must not remove parent spans from exported traces\"; its default (`configured` unset) is `\"buzz_relay=info,buzz_datastore=info\"`, so `buzz_datastore`-target spans are included in OTel export by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs"
  - statement: "crates/buzz-relay/src/main.rs's separate `log_env_filter` function, which builds the filter for stdout/JSON logs, defaults to `\"buzz_relay=info\"` alone — the `buzz_datastore` target is not enabled by that default. The two functions' independence is directly asserted by crates/buzz-relay/src/main.rs's own `env_filter_tests` module: `unset_enables_datastore_only_for_otel_filter` builds a subscriber from each filter separately and asserts `buzz_datastore` logging is disabled under `log_env_filter(None)` while `tracing::enabled!(target: \"buzz_datastore\", ...)` is true under `otel_env_filter(None)`; `explicit_datastore_off_is_preserved_alone` and `explicit_datastore_debug_is_preserved_alone` confirm `BUZZ_OTEL_FILTER` overrides are passed through verbatim."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/telemetry.rs"
  - statement: "crates/buzz-relay/src/telemetry.rs's own integration test, `http_and_datastore_spans_are_exported_in_the_same_trace`, builds a real `tracing_opentelemetry` layer filtered by `otel_env_filter(None)` over an `InMemorySpanExporter`, drives an HTTP request through `http_trace_layer()`, and inside that request's handler creates a manual `target: \"buzz_datastore\"` span (with `otel.kind = \"client\"`, `db.system.name = \"postgresql\"`) nested under the HTTP span — asserting that a datastore-target span and the HTTP span it occurs within are exported together as parent/child spans in one trace, which is the concrete evidence that `buzz_datastore`-target spans (whether from this manual pattern or the `#[datastore_span]` macro, which emits the identical `otel.kind`/`db.system.name` shape) participate in the relay's real distributed-tracing pipeline rather than being a standalone logging concern."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs"
  - statement: "Issue #611 (parent Feature/PRD) and issue #1136's own Definition of done require: exactly one hand-authored canonical document per task; schema-valid front matter with a stable id, type, status, origin, audiences, evidence and typed relationships; one independently maintainable knowledge node; every substantive claim traceable and classified FACT/INFERENCE/TEAM_KNOWLEDGE; links to implementation/verification/specification/neighboring nodes without duplicating their content; a check against the recorded revision; a clean corpus validator run; a one-sentence definition; stated boundaries/non-goals; links to related concepts; and examples that clarify without introducing a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1136 definition of done, opened directly via gh issue view"
  - statement: "Eight sibling observability-document tasks are being authored in parallel under the same parent Feature (#611) at this node's authoring time: audit-log (#1135), health-checks (#1137), metrics (#1140), opentelemetry (#1141), prometheus (#1142), readiness (#1143), structured-logging (#1144), tracing (#1145) — none of their PRs exist yet, so the boundary this node draws against them is this node's own reasoned placement, to be revisited once each lands, the same caveat the parallel `layers/compute/liveness.md` node (PR #1903) records for its own undrafted siblings."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus batch-run dispatch brief for issue #1136, naming the eight concurrent sibling tasks and their issue numbers"
  - statement: "`origin/launchpad`'s `launchpad/docs/corpus` tree carries no `layers/` directory at all at the fetched revision, so no `layers/observability/*.md` or `layers/compute/*.md` sibling node (including the eight named above, or the parallel, unmerged `layers/compute/liveness.md` and `layers/compute/local-agent-compute.md` nodes visible in open PR #1903) exists as a legal `relationships.target` for this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no layers/ directory present"
  - statement: "`launchpad/docs/corpus/architecture/containers/postgres.md` is a merged node on `origin/launchpad` with id `architecture-containers-postgres`, describing `buzz-db` as the crate owning Postgres connection pooling, migrations, and data access generally — a legal, existing relationship target this node can reference for the container this instrumentation layer wraps, without restating that node's content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
relationships:
  - type: references
    target: architecture-containers-postgres
---

# Datastore tracing

**Datastore tracing**, in Buzz, is the privacy-preserving instrumentation
policy implemented by the `buzz-datastore-tracing` crate's single public
item, the `#[datastore_span]` attribute macro: a compile-time-enforced,
opinionated wrapper around an async Postgres data-access method that
produces a tracing span, a duration metric, and a sampled slow-operation log
line — all deliberately stripped of function arguments, return values, and
raw error content. This node documents that one crate: what it instruments,
what it deliberately withholds, and where its output actually goes once
emitted.

## Definition

`datastore_span(name = "...", system = "postgresql", fields(...))` is an
attribute macro applied to an `async fn`. Applying it to a non-`async`
function, or supplying any `system` value other than the literal
`"postgresql"`, is a compile error — this is not a naming convention, it is
enforced by the macro's own generated code before anything runs. It is used
258 times in this repository: 256 production call sites across four
consuming crates (`buzz-db` 251, `buzz-audit` 3, `buzz-search` 1,
`buzz-relay` 1 handler), plus 2 more inside `buzz-datastore-tracing`'s own
test fixtures. Every one of these 258 usages sets `system = "postgresql"`;
no other datastore in the codebase (Redis, the S3-compatible object store)
is instrumented by this mechanism today, and `buzz-pubsub` — the Redis
crate — does not import it at all.

**What the macro is not:** it is not a general-purpose tracing macro (see
`docs/corpus/layers/observability/tracing.md`, issue #1145, for spans
elsewhere in the codebase), not the OpenTelemetry pipeline configuration
itself (see `.../opentelemetry.md`, issue #1141, for exporter/provider
setup), not the metrics pipeline in general (see `.../metrics.md`, issue
#1140, for the histogram/counter/gauge surface this macro happens to emit
one histogram into), and not a description of Postgres's own schema, tables,
or access patterns (that is a future `architecture`-type Postgres *instance*
document, built from the already-merged `templates/datastore.md` template —
this node covers the instrumentation wrapped around that access, not the
access itself).

## What each annotated call produces

Three outputs, from one attribute:

1. **A tracing span**, named by the macro's `name` argument, emitted at
   `target: "buzz_datastore"`, `skip_all` (function arguments are never
   captured as span fields), carrying fixed fields `otel.kind = "client"`,
   `db.system.name = "postgresql"`, and `otel.status_code` — set to
   `"ERROR"` only when the wrapped function returns `Err`, and never
   populated with the error's own content. Any additional `fields(...)`
   passed to the macro are recorded verbatim — these are the call site's own
   explicit opt-in list of safe values (e.g. `fields(action = %entry.action)`
   in `buzz-audit`'s `AuditService::log`, or `fields(limit = limit)` in
   `buzz-db`), not something the macro infers automatically.
2. **A duration histogram**, `buzz_db_operation_duration_seconds`, recorded
   via the `metrics` crate on every call (success or error), labeled
   `operation` (the same `name` string) and `outcome` (`"success"` or
   `"error"`).
3. **A sampled slow-operation log**, at `target: "buzz_datastore"`,
   `tracing::warn!`, fired only when the call took >= 500ms, and only on
   every 100th such slow completion at that call site (a per-call-site
   `AtomicU64` counter gates this). The event carries exactly four fields:
   `message`, `operation`, `outcome`, `elapsed_ms` — never the function's
   arguments or the error value.

`crates/buzz-datastore-tracing/tests/runtime.rs` verifies both the
positive claim (the fixed/opt-in fields are present) and the negative claim
(two literal secret strings passed as arguments and as `Err` payloads never
appear in the exported span's debug output, its events, or the sampled log
line) — the redaction policy is asserted against real
`tracing_opentelemetry` + `InMemorySpanExporter` output, not merely
documented as intent.

## Where the output goes: two independently configured filters

The `buzz_datastore` tracing target is wired into two separate `EnvFilter`s
in `buzz-relay`, and they disagree by default:

- **`otel_env_filter`** (`crates/buzz-relay/src/telemetry.rs`) governs what
  is exported through the OpenTelemetry span pipeline. Its own doc comment
  states it is "intentionally independent from `RUST_LOG`: changing stdout
  log verbosity must not remove parent spans from exported traces." Its
  default is `buzz_relay=info,buzz_datastore=info` — datastore spans are
  exported by default.
- **`log_env_filter`** (`crates/buzz-relay/src/main.rs`) governs stdout/JSON
  logs. Its default is `buzz_relay=info` alone — datastore-target events are
  *not* emitted to stdout by default.

`crates/buzz-relay/src/main.rs`'s `env_filter_tests` module asserts this
divergence directly: under `log_env_filter(None)`,
`tracing::enabled!(target: "buzz_datastore", Level::INFO)` is `false`; under
`otel_env_filter(None)`, the same check is `true`. `BUZZ_OTEL_FILTER` can
override the OTel-side default explicitly (e.g. `buzz_datastore=off` or
`buzz_datastore=debug`), independent of `RUST_LOG`.

`telemetry.rs`'s own `http_and_datastore_spans_are_exported_in_the_same_trace`
test confirms the practical consequence: a `buzz_datastore`-target span
created inside an HTTP request handler is exported as a child of that
request's own HTTP span in the same trace — datastore spans are not a
side-channel, they participate in the relay's real distributed trace tree.

## Use cases

- **Adding a new Postgres-backed data-access method** to `buzz-db` or a
  similar crate: apply `#[datastore_span(name = "...", system =
  "postgresql")]` and, if the call needs specific context beyond
  success/failure and timing, add only explicitly safe values via
  `fields(...)` — never the row payload, a user-supplied string, or an error
  value.
- **Debugging a missing datastore trace in an OTel backend**: check
  `BUZZ_OTEL_FILTER`/`otel_env_filter`'s default first; a `buzz_datastore`
  span absent from stdout logs is expected behavior (`log_env_filter`
  excludes it by default), not evidence the span was never created.
- **Investigating a slow-query alert**: the sampled `tracing::warn!` line at
  `target: "buzz_datastore"` is deliberately throttled to 1-in-100 per call
  site once a site is running slow continuously — absence of a fresh log
  line does not mean the operation sped back up, only that the counter has
  not rolled over again.
- **Auditing what a Postgres-adjacent crate's tracing exposes**: the
  compile-time `system = "postgresql"`-only restriction and the `skip_all`
  argument policy mean any reviewer can trust that no `#[datastore_span]`
  call site in this repository can leak a function argument through this
  particular mechanism — a leak would have to come from an explicit
  `fields(...)` entry, which is visible in the annotation itself.

## Scope and omissions

**This document covers** the `buzz-datastore-tracing` crate's
`#[datastore_span]` macro: what it instruments, its privacy-preserving
redaction policy, its three concrete outputs (span, histogram, sampled
slow-log), and the two independently configured filters that decide where
its `buzz_datastore`-target output actually lands.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| General OpenTelemetry pipeline setup (exporter, provider, resource detection) | #1141, `layers/observability/opentelemetry.md` |
| Tracing spans elsewhere in the codebase, outside this one macro | #1145, `layers/observability/tracing.md` |
| The metrics pipeline in general (this node names only the one histogram this macro emits) | #1140, `layers/observability/metrics.md` |
| Structured logging in general (stdout/JSON formatting, correlation IDs) | #1144, `layers/observability/structured-logging.md` |
| Postgres's own schema, tables, migration mechanism, and general access-pattern shape | a future `architecture`-type Postgres instance document, built from the merged `templates/datastore.md` template; today, `architecture/containers/postgres.md` names the container only at one-line depth |
| Whether Redis or the object store will ever be wired into this macro's `system` enum | a future design decision, not this documentation task's to make; the restriction is enforced and deliberate today per `templates/datastore.md`'s own evidence |

**No relationship to any sibling `layers/*` node.** Checked against
`origin/launchpad`'s actual corpus tree (`git ls-tree -r --name-only`), not
assumed: no `layers/` directory exists there at the recorded revision, so
none of the eight parallel observability-document tasks named above, nor
the parallel `layers/compute/*.md` nodes visible only in open PR #1903, are
legal `relationships.target`s yet. One relationship is declared instead, to
`architecture-containers-postgres` — the existing, merged node for the
container this instrumentation layer wraps.

**Expected but not verified when this node was written:**

- Whether `#1140`, `#1141`, `#1144`, and `#1145` land with boundary language
  that actually agrees with what this node assumes about their scope — none
  of their PRs exist yet, so every cross-reference above is this node's own
  placement, not a confirmed mutual boundary.
- Whether a future architecture-type Postgres instance document will declare
  its own relationship back to this node (e.g. a `references` or `part-of`
  edge) — that document does not exist yet, and this node does not decide
  that document's own front matter.
- Whether any call site outside the five crates scanned here (`buzz-db`,
  `buzz-audit`, `buzz-search`, `buzz-relay`, and `buzz-datastore-tracing`'s
  own test fixtures) uses `datastore_span` — the 258-usage count and the
  five-crate breakdown were established by a repository-wide grep at the
  recorded revision, not by an exhaustive manual review of every call
  site's individual `fields(...)` list for policy compliance.
