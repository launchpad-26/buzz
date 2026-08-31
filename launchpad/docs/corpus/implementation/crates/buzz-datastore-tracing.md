---
id: implementation-crates-buzz-datastore-tracing
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-datastore-tracing is a proc-macro-only crate (lib.proc-macro = true) described in its own Cargo.toml as \"Privacy-preserving datastore tracing policy macros for Buzz\", depending on syn, quote, and proc-macro2, with tracing/tracing-opentelemetry/metrics/opentelemetry_sdk/tokio only as dev-dependencies for its own tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml"
  - statement: "The crate exports exactly one public item, the #[proc_macro_attribute] fn datastore_span(args, item), which parses name/system/fields arguments via the DatastoreArgs struct, rejects non-async functions and any system value other than the literal string \"postgresql\" with a compile error, then rewrites the function body to record elapsed time, emit a buzz_db_operation_duration_seconds histogram, and log a sampled (every 100th occurrence) slow-operation warning (target buzz_datastore, parent: None) for completions >= 500ms."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:76-179"
  - statement: "The generated #[tracing::instrument] attribute always sets target = \"buzz_datastore\", skip_all (so function arguments are never captured as span fields), fields otel.kind = \"client\" and db.system.name = \"postgresql\", plus otel.status_code left Empty and only set to \"ERROR\" on an Err return -- no error value is ever formatted into a field."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:100-134"
  - statement: "The crate's own doc comment on datastore_span states the policy in prose: \"PostgreSQL spans always omit function arguments, use the buzz_datastore target, and expose only canonical semantic fields plus explicitly supplied safe fields. An Err sets otel.status_code without inspecting the error... arguments, error values, and return values are never formatted.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:68-75"
  - statement: "The crate's own unit tests (mod tests in src/lib.rs) cover DatastoreArgs argument parsing only -- accepting safe field expressions and rejecting duplicate name/system/fields arguments -- and carry no runtime span/metrics assertions themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:181-208"
  - statement: "crates/buzz-datastore-tracing/tests/runtime.rs is an integration test exercising the expanded macro end to end: exports_policy_fields_without_error_or_argument_data asserts the emitted OpenTelemetry span carries otel.kind=client, db.system.name=postgresql, the declared safe field (limit), and the operation-duration histogram labeled by operation/outcome, while asserting neither the exported span's Debug output nor its events ever contain the two synthetic secret constants (DIRECT_ERROR, QUESTION_ERROR) used as the functions' error payloads; slow_operation_logging_is_guarded_sampled_and_redacted asserts exactly one slow-operation log line is emitted across three calls where two exceed the 500ms threshold (1-in-100 sampling), that its four fields are only message/operation/outcome/elapsed_ms, and that it too never contains the secret constants."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/tests/runtime.rs"
  - statement: "Four other crates depend on buzz-datastore-tracing per their Cargo.toml: buzz-audit, buzz-search, buzz-db, buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "In buzz-db, #[datastore_span(...)] annotates async fns across 250 call sites in 28 source files under src/ (e.g. store/event.rs's insert_event, query_events, query_events_routed, query_events_routed_bounded at lines 1353/1379/1400/1435, and store/relay_admin_actions.rs, store/relay_operators.rs, runtime/replica_fence.rs, runtime/mod.rs among others), each wrapping one logical Postgres-backed operation."
    entry_class: FACT
    evidence:
      - "grep_count(pattern='#\\[datastore_span', path='crates/buzz-db/src') -> 250 occurrences across 28 files"
      - "crates/buzz-db/src/store/event.rs:1353-1435"
      - "crates/buzz-db/src/store/relay_admin_actions.rs"
      - "crates/buzz-db/src/store/relay_operators.rs"
      - "crates/buzz-db/src/runtime/replica_fence.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "buzz-audit's AuditService::log method is annotated #[datastore_span(name = \"audit_log\", system = \"postgresql\", fields(action = %entry.action))], instrumenting the hash-chain audit append inside a per-community pg_advisory_lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:53-58"
  - statement: "buzz-search's search() function, the Postgres full-text search entry point whose doc comment states \"community_id = $ctx is the first predicate and is non-negotiable\", is annotated #[datastore_span(name = \"search\", system = \"postgresql\")]."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs:211-219"
  - statement: "buzz-relay's persist_command_event, the function that inserts an event row (and idempotently applies any associated domain mutation) inside command_executor.rs, is annotated #[datastore_span(name = \"persist_command_event\", system = \"postgresql\")]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:101-107"
  - statement: "crates/buzz-relay/src/router.rs's http_and_datastore_spans_are_exported_in_the_same_trace test asserts a manually constructed span carrying the same target/otel.kind/db.system.name fields datastore_span generates is exported as a child of the surrounding HTTP request span under the same trace id, verifying the macro's span shape composes with the relay's own HTTP tracing layer rather than the macro itself being re-tested."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:716-767"
  - statement: "crates/buzz-db/tests/observability_source.rs's database_metrics_and_slow_logs_exclude_sensitive_or_unbounded_fields test does a literal source-text scan (include_str! of both buzz-db's own runtime/observability.rs and this crate's src/lib.rs) asserting neither ever emits forbidden field names (community, event_id, event_kind, kind, sql, query, query_id, d_tag, coordinate) as metric/log labels, and separately asserts datastore_macro.contains(\"parent: None\") specifically so that slow-operation warnings never inherit dynamic datastore span fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/tests/observability_source.rs:1-38"
  - statement: "crates/buzz-db/src/runtime/observability.rs is a separate module (module doc: \"Bounded-cardinality database pressure instrumentation primitives... Label values come only from the closed enums in this module\") providing connection-pool pressure metrics (PoolRole, LockType enums) that buzz-datastore-tracing does not implement, own, or depend on -- the two are tested together only by the shared source-scan policy test above, not because one wraps the other."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/observability.rs:1-53"
  - statement: "git log for crates/buzz-datastore-tracing shows two commits: 397796c5f \"feat(tracing): add PostgreSQL tracing spans (#3678)\" (crate creation) and 113a33b7e \"Add database pressure observability (#6700)\"."
    entry_class: FACT
    evidence:
      - "git_log(pathspec='crates/buzz-datastore-tracing', oneline=true) -> 113a33b7e Add database pressure observability (#6700); 397796c5f feat(tracing): add PostgreSQL tracing spans (#3678)"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md (id architecture-containers-postgres) is a merged corpus node describing buzz-db as the crate owning Postgres connection pooling, migrations, and typed data-access modules; every current datastore_span call site instruments a Postgres-backed operation and the macro hard-rejects any system value other than \"postgresql\", making this node's references edge to that container node accurate rather than aspirational."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "crates/buzz-datastore-tracing/src/lib.rs:89-96"
  - statement: "At repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c, git ls-tree -r --name-only HEAD -- launchpad/docs/corpus contains no implementation/ subtree node other than this one, so no part-of or implements edge toward a sibling implementation-reference node (e.g. one documenting buzz-db as a whole) can be declared -- such a node does not exist yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> no implementation/ subtree node other than this one, at commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
---

# buzz-datastore-tracing: implementation reference

`crates/buzz-datastore-tracing` is a proc-macro-only crate providing the single
attribute macro `#[datastore_span]`, which four other crates (`buzz-db`,
`buzz-audit`, `buzz-search`, `buzz-relay`) apply to async functions that perform
logical PostgreSQL operations. It claims to realize an unwritten but
test-enforced privacy policy: datastore instrumentation (tracing spans, a
duration histogram, and sampled slow-operation logs) must never leak function
arguments, error contents, return values, or a fixed list of sensitive field
names (SQL text, query identifiers, community/event/coordinate values) into
telemetry.

## Target

The target is not an ADR, NIP, or other named specification -- it is a policy
implicit in the crate's own doc comments and enforced directly by a sibling
test, `crates/buzz-db/tests/observability_source.rs`. That test has no
corpus node of its own yet; a reader verifies the policy by opening the test
file itself; the statement of the policy in prose is the macro's own doc
comment at `crates/buzz-datastore-tracing/src/lib.rs` lines 68-75. There is no
existing corpus node this target maps onto, so no `implements` edge is
declared (see *Relationships* below).

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-datastore-tracing/src/lib.rs::datastore_span` | The whole policy: argument-omitting span, canonical/safe-only fields, error-status-without-error-value, duration histogram, sampled slow-op log | The only public item this crate exports (`#[proc_macro_attribute]`) |
| `crates/buzz-datastore-tracing/src/lib.rs::DatastoreArgs` (private parser) | Parses `name`, `system`, `fields` macro arguments; rejects duplicates and non-`"postgresql"` systems | Unit-tested directly in `mod tests` within the same file |
| `crates/buzz-db/src/store/event.rs` (`insert_event`, `query_events`, `query_events_routed`, `query_events_routed_bounded`, and 246 more call sites across 27 other files in `store/`, `runtime/`) | Applies `#[datastore_span]` to buzz-db's own Postgres-backed operations | Representative sample; not exhaustively enumerated here |
| `crates/buzz-audit/src/service.rs::AuditService::log` | Applies `#[datastore_span(name = "audit_log", ..., fields(action = %entry.action))]` to the hash-chain audit append | One `fields(...)` argument beyond the canonical set |
| `crates/buzz-search/src/query.rs::search` | Applies `#[datastore_span(name = "search", system = "postgresql")]` to the full-text search entry point | No extra fields |
| `crates/buzz-relay/src/handlers/command_executor.rs::persist_command_event` | Applies `#[datastore_span(name = "persist_command_event", system = "postgresql")]` to the relay's event-insert path | No extra fields |
| `crates/buzz-datastore-tracing/tests/runtime.rs` | Integration-tests the macro's expansion: span fields, histogram labels, and slow-op-log redaction against synthetic secret values | Exercises the macro itself, not a call site |
| `crates/buzz-db/tests/observability_source.rs::database_metrics_and_slow_logs_exclude_sensitive_or_unbounded_fields` | Cross-crate source-text policy test asserting neither this macro's generated code nor buzz-db's own observability module ever names a forbidden field | The actual enforcement mechanism for the policy stated in *Target* |
| `crates/buzz-relay/src/router.rs::http_and_datastore_spans_are_exported_in_the_same_trace` | Confirms a `buzz_datastore`-shaped span nests correctly under the relay's HTTP request span in the same trace | Tests composition with relay-level tracing, not the macro's own field policy |

## Divergences

None found. The macro's implementation (`src/lib.rs` lines 76-179) matches its
own doc comment claim line for line: `skip_all` omits arguments, the fixed
`fields(...)` list is exactly `otel.kind`, `db.system.name`, `otel.status_code`
plus whatever the caller passed via `fields(...)`, the error branch only calls
`.record("otel.status_code", "ERROR")` and never touches the `Err` payload, and
the slow-log branch (`tracing::warn!` with `parent: None`) logs only
`operation`, `outcome`, `elapsed_ms` -- confirmed independently by
`observability_source.rs`'s source-text assertions and by
`tests/runtime.rs`'s two integration tests, which is the "checked, not just
asserted absent" evidence this section requires. What was checked: every line
of `src/lib.rs`, both test files in this crate, and the cross-crate policy
test in `buzz-db`. No caller-side divergence was checked exhaustively -- see
*Scope and omissions*.

## Verification

Verified today by three automated, non-overlapping mechanisms:

1. **Unit tests** inside `crates/buzz-datastore-tracing/src/lib.rs` (`mod
   tests`) -- `DatastoreArgs` parsing only.
2. **Integration tests** in `crates/buzz-datastore-tracing/tests/runtime.rs` --
   the expanded macro's actual span/metric/log output, run against real
   `tracing-opentelemetry` and `metrics-util` recorders.
3. **Cross-crate source-scan policy test** in
   `crates/buzz-db/tests/observability_source.rs` -- asserts, by literal text
   inspection of this crate's own source plus `buzz-db`'s
   `runtime/observability.rs`, that neither ever names a forbidden sensitive
   field. This is the test that actually enforces the privacy policy stated in
   *Target*, and it is owned by `buzz-db`, not by this crate.

Additionally, `crates/buzz-relay/src/router.rs`'s
`http_and_datastore_spans_are_exported_in_the_same_trace` verifies the
macro-shaped span composes correctly with the relay's HTTP tracing layer,
though it constructs its test span manually rather than invoking the macro.

## Relationships

- references: architecture-containers-postgres

## Scope and omissions

**This node covers** what `buzz-datastore-tracing` is responsible for (the
`#[datastore_span]` attribute macro and the privacy/observability policy it
generates), its one public interface, its dependencies, where it is applied
across `buzz-db`, `buzz-audit`, `buzz-search`, and `buzz-relay`, and how that
policy is verified today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Connection-pool pressure instrumentation (`PoolRole`, `LockType` metrics) | `crates/buzz-db/src/runtime/observability.rs` -- a separate module this crate does not implement or depend on |
| The metrics/tracing pipeline the emitted spans and histogram feed into (OpenTelemetry exporter configuration, Prometheus scraping) | `crates/buzz-relay/src/telemetry.rs` (e.g. `otel_env_filter`) and relay-level deployment configuration, not this crate |
| Whether every one of the ~250 `#[datastore_span]` call sites across ~28 `buzz-db` modules individually satisfies the policy, beyond the source-scan test's blanket assertion | `crates/buzz-db/tests/observability_source.rs`, which checks the generated code and the observability module textually, not each call site's specific `fields(...)` arguments |
| Non-PostgreSQL datastore tracing | Not implemented; the macro compile-errors on any `system` value other than `"postgresql"` |

**Expected but not verified when this node was written:**

- **No corpus node yet exists for the policy this crate implements** (a
  written specification of "datastore telemetry must never leak these field
  classes"). The only artifact stating it is the macro's own doc comment and
  the `observability_source.rs` test; whether a future policy/specification
  node should exist and whether this node should then declare `implements`
  toward it was not decided here.
- **No `buzz-db` (or other dependent crate) implementation-reference node
  exists yet** to declare a `part-of` or sibling relationship toward; `git
  ls-tree` against `HEAD` at this node's recorded revision confirms no other
  `implementation/` node is present in the corpus tree.
- **Every individual call site's `fields(...)` argument was not audited** for
  whether it independently avoids the forbidden field list beyond what
  `observability_source.rs`'s blanket source-text scan already checks; the
  scan covers this crate's generated code and `buzz-db`'s own module, not each
  of the ~250 call sites' bespoke `fields(...)` expressions individually.
