Issue #1141 — task: document layers/observability/opentelemetry.md
Parent: #611
Stated size: not stated in issue body -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/layers/observability/opentelemetry.md` does not exist in this
  worktree (`ls` confirms no such path; the parent `layers/` directory does not exist
  either — no `layers` node is merged on `origin/launchpad` at `ed133f4c5`).
- `node.schema.json`'s `type` enum includes `layers` among 13 values; this node uses
  that value, not an invented one.
- A sibling agent (issue #1139, `logging`) has already authored and committed
  `layers-observability-logging` locally in worktree `__worktrees/task-1139-logging`
  (commit `428d479f8`, id `layers-observability-logging`, `type: layers`,
  `status: draft`, `origin: launchpad`) — not yet merged to `origin/launchpad`. It is
  the concrete precedent for this node's front-matter shape, and the reason no
  `relationships` are added here: no `layers` node is merged yet to target.
- `crates/buzz-relay/src/telemetry.rs` and `crates/buzz-relay/src/main.rs` (lines
  ~96-179) contain the entirety of Buzz's OTEL SDK wiring; `crates/buzz-datastore-tracing`
  and `crates/buzz-relay` are the only two crates depending on the `opentelemetry` crate
  family (grepped every `Cargo.toml`), and `buzz-datastore-tracing` is a distinct
  proc-macro concern owned by #1136, not this node.
- The module doc-comment in `telemetry.rs` (lines 20-24) claims `OTEL_TRACES_SAMPLER`
  and `OTEL_TRACES_SAMPLER_ARG` are "honoured", but neither name appears anywhere in
  `crates/buzz-relay/src/*.rs` outside that comment (grepped), and
  `SdkTracerProvider::builder()` is never called with `.with_sampler(...)`. This is a
  genuine doc/code discrepancy to state carefully, not repeat as settled fact.

STEP 1 — Write the corpus node [independent] <- RUNS HERE

Create `launchpad/docs/corpus/layers/observability/opentelemetry.md` with:
- Front matter: `id: layers-observability-opentelemetry`, `type: layers`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator]`,
  no `relationships` (per ALREADY TRUE), and an `evidence` ledger citing only sources
  actually opened this session (`telemetry.rs`, `main.rs`, root `Cargo.toml`,
  `crates/buzz-relay/Cargo.toml`, `.env.example`, and the docs.rs source read for the
  SDK's default-sampler behavior).
- Body covering: what the OTEL layer is (a `tracing_subscriber::Layer` attached
  conditionally alongside the always-on JSON stdout layer), how it is initialized
  (`telemetry::service_resource()` + `telemetry::try_init_tracer()` in `main()`, gated
  entirely on `OTEL_EXPORTER_OTLP_ENDPOINT` being set), what exporter is configured
  (`opentelemetry_otlp::SpanExporter` via `.with_tonic()`, batch-exported), how the
  resource/service name is derived, how the independent `BUZZ_OTEL_FILTER` works, the
  `TracerInit` three-state outcome and its logging-after-subscriber-install constraint,
  and the sampler discrepancy stated as an honest, evidenced observation.
- Explicit non-goals: no trace-span semantics/instrumentation content (#1145), no
  datastore-tracing policy macros (#1136), no metrics/Prometheus content (#1140/#1142).
- done when: the file exists, is schema-shaped per `node.schema.json`, and every DoD
  bullet in issue #1141 is addressed in the body.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits with `PASS` and
  zero FAIL-class errors attributable to the new node.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  prints `OK`, run as the sole command in its own tool call.

PARALLEL

None. This is a single-file, single-step documentation task authored by one agent in
isolation; there is nothing to run concurrently.

BUDGET

One file added (plus this plan file). Single step, no code changes, no relationships
to wire up. Well inside the 5-step cap.

OPEN

- Whether `OTEL_TRACES_SAMPLER`/`OTEL_TRACES_SAMPLER_ARG` are read by SDK
  auto-configuration outside `trace/provider.rs` (e.g. a separate env-config module)
  was not fully ruled out — the docs.rs source view checked only that one file, not
  the whole `opentelemetry_sdk` crate. Recorded as an INFERENCE, not a FACT, in the
  node's evidence ledger. A builder must not upgrade this to FACT without opening the
  rest of the crate.

LEFT OUT

- Any edit to `telemetry.rs`/`main.rs` themselves — documentation-only task; the
  discrepancy found is reported, not fixed, and is out of this issue's scope.
- Trace-span content, datastore-tracing macros, and metrics/Prometheus content — owned
  by sibling issues #1145, #1136, #1140/#1142 respectively, not folded in here.
