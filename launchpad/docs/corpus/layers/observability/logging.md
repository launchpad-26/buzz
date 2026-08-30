---
id: layers-observability-logging
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "CONTRIBUTING.md states a repository-wide Rust convention: use the `tracing` crate for all instrumentation, and prefer structured fields over string interpolation, giving `tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\")` as the preferred form over `tracing::info!(\"Event ingested: channel={id} kind={kind}\")`."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:287-298"
  - statement: "buzz-relay's main() installs a tracing_subscriber::registry() with a fmt::layer().json() layer that is always active regardless of OpenTelemetry configuration, filtered by an EnvFilter built from RUST_LOG (falling back to \"buzz_relay=info\" when RUST_LOG is unset)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:5-10"
      - "crates/buzz-relay/src/main.rs:96-133"
  - statement: "When OTEL_EXPORTER_OTLP_ENDPOINT is set, buzz-relay additionally attaches an OpenTelemetry tracing layer (tracing_opentelemetry::layer()) that exports spans via OTLP gRPC alongside the JSON stdout logs; when it is unset, telemetry::try_init_tracer is documented as a no-op and only the JSON stdout logs run."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:96-133"
      - "crates/buzz-relay/src/telemetry.rs:1-25"
  - statement: "The OpenTelemetry export path in buzz-relay is filtered independently from the stdout JSON logs: otel_env_filter reads BUZZ_OTEL_FILTER (falling back to \"buzz_relay=info,buzz_datastore=info\"), deliberately separate from the RUST_LOG-driven filter on the stdout layer, so that changing stdout log verbosity does not remove parent spans from exported traces."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:170-185"
      - "crates/buzz-relay/src/main.rs:1121-1145"
  - statement: "buzz-relay's JSON stdout formatter (TraceContextJson in telemetry.rs) injects lowercase-hex trace_id and span_id fields into each JSON log event when it can resolve an active OpenTelemetry span context, specifically because Datadog recognizes those OpenTelemetry-standard field names for correlating logs to traces; outside a valid span, or when OTEL export is disabled, events fall back to the standard tracing-subscriber JSON format with no injected fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:80-179"
  - statement: ".env.example documents RUST_LOG, BUZZ_OTEL_FILTER and OTEL_EXPORTER_OTLP_ENDPOINT together under a \"Logging / Tracing\" heading, with RUST_LOG given a concrete multi-target default (buzz_relay=debug,buzz_datastore=info,buzz_db=debug,buzz_auth=debug,buzz_pubsub=debug,tower_http=debug) and the other two commented out (OTEL export disabled) by default for local development."
    entry_class: FACT
    evidence:
      - ".env.example:122-131"
  - statement: "buzz-push-gateway's main() and buzz-test-client's main() each call tracing_subscriber::fmt() (an EnvFilter-driven human-readable/plain formatter, not fmt().json()) rather than buzz-relay's JSON-plus-OTEL registry pattern, so at least two other binaries in the workspace initialize a differently-shaped tracing subscriber from buzz-relay's."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs:19-24"
      - "crates/buzz-test-client/src/main.rs:35"
  - statement: "crates/buzz-admin/src/main.rs and desktop/src-tauri/src/managed_agents/custom_harnesses.rs call tracing::warn! (and buzz-admin also tracing::info!) directly, but neither crate's source under src/ contains a call to tracing_subscriber::registry(), tracing_subscriber::fmt(), or any other subscriber-installing call (searched with grep across every .rs file in each crate)."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "desktop/src-tauri/src/managed_agents/custom_harnesses.rs:74-144"
  - statement: "Because the `tracing` crate dispatches every event to whatever subscriber is currently registered as the process-global default, and emits nothing when none has been installed, a tracing::warn!/info! call in a crate whose own source never installs a subscriber produces no output unless some other binary entry point in the same process happens to install one first; buzz-admin and desktop-tauri's managed_agents module are two call sites this node found with no subscriber-install call in their own crate source, so whether their events are actually observed depends on something outside the file being read to write this claim."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "desktop/src-tauri/src/managed_agents/custom_harnesses.rs:74-144"
    confidence: 0.6
  - statement: "desktop/src-tauri declares tracing = \"0.1\" as a dependency and desktop/src-tauri/src/managed_agents/custom_harnesses.rs and discovery.rs call tracing::warn! directly, so the desktop app's Rust side (Tauri backend) participates in the same tracing ecosystem as the relay crates, independent of whichever subscriber (if any) is actually installed at runtime."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:148"
      - "desktop/src-tauri/src/managed_agents/custom_harnesses.rs:93-144"
  - statement: "No dedicated logger utility module (matched by filename containing \"logger\" or \"logging\") exists under desktop/src, and desktop/biome.json contains no rule targeting the string \"console\" (checked by grepping the file directly), so the desktop app's TypeScript/React frontend has no repository-enforced logging convention; 92 files under desktop/src call console.log, console.warn, console.error or console.debug directly."
    entry_class: FACT
    evidence:
      - "desktop/biome.json"
  - statement: "AGENTS.md (this repository's root contributor guide, read at CLAUDE.md, a symlink to AGENTS.md) states, in its Mobile App section: \"Do NOT use print() — use debugPrint() or structured logging.\""
    entry_class: FACT
    evidence:
      - "AGENTS.md:565"
  - statement: "mobile/lib contains 59 call sites of debugPrint and zero bare print( calls (grepped directly), consistent with the AGENTS.md mobile rule being followed in practice; mobile/analysis_options.yaml contains no avoid_print or similar rule (grepped directly), so this convention is not enforced by static analysis in this repository, only stated as a contributor-guide rule."
    entry_class: FACT
    evidence:
      - "mobile/analysis_options.yaml"
  - statement: "The proc-macro crate buzz-datastore-tracing (crates/buzz-datastore-tracing/Cargo.toml, description \"Privacy-preserving datastore tracing policy macros for Buzz\") and buzz-relay's own buzz_datastore tracing target (visible in the RUST_LOG and BUZZ_OTEL_FILTER defaults cited above) exist as a distinct, policy-enforcing instrumentation surface layered on top of the general tracing setup described in this node, and issue #1136 (datastore-tracing) is the open task scoped to document it in detail rather than this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml:1-8"
      - "crates/buzz-datastore-tracing/src/lib.rs:1"
  - statement: "Issue #1139's parent PRD is #611, and the issue names #1144 (structured-logging) and #1136 (datastore-tracing) as sibling tasks this general logging node must not duplicate, per the batch-run brief that dispatched this task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1139 task dispatch brief (corpus-batch-author, Feature #611 batch run)"
---

# Logging

## Definition

**Logging**, in Buzz, is the practice of emitting structured, leveled diagnostic events
from running code using the Rust [`tracing`](https://docs.rs/tracing) crate as the one
instrumentation library used across the workspace's Rust surfaces — the relay, the
CLI/admin tools, and the desktop app's Rust (Tauri) backend. `CONTRIBUTING.md` states this
convention directly for the whole repository: use `tracing` for all instrumentation, and
prefer structured fields (`channel_id = %id`) over string-interpolated messages, because
structured fields stay machine-parseable downstream while an interpolated string does not.

This node is the **general/umbrella concept**: what logging means across Buzz's surfaces,
what the common convention is, and where each surface's actual subscriber setup diverges
from — or omits — that convention. It does not define the structured-field schema itself
(that is #1144's territory) or the datastore-specific tracing policy macros (that is
#1136's territory) — see *Boundaries and non-goals* below.

## What "logging" means per surface

**Relay (`buzz-relay`).** The most fully-built surface. `main()` installs a
`tracing_subscriber::registry()` carrying a `fmt::layer().json()` layer that is always
active, filtered by an `EnvFilter` built from the `RUST_LOG` environment variable
(falling back to `"buzz_relay=info"` when unset). Output is JSON-only, deliberately —
the source comment above the subscriber install calls it "JSON-only structured logs —
simple, machine-parseable, CAKE-compatible." When `OTEL_EXPORTER_OTLP_ENDPOINT` is set,
an additional OpenTelemetry tracing layer exports spans via OTLP gRPC alongside the same
JSON stdout logs; when it is unset, that layer is absent and only the JSON stdout logs
run. The OTEL export path is filtered independently, via `BUZZ_OTEL_FILTER` (default
`"buzz_relay=info,buzz_datastore=info"`), specifically so that turning stdout log
verbosity up or down cannot silently drop parent spans from an exported trace. When an
OTEL span context is active, the JSON formatter (`TraceContextJson` in `telemetry.rs`)
additionally injects lowercase-hex `trace_id`/`span_id` fields into each log line, so a
JSON log event and the trace it belongs to can be correlated in the same log line — this
is done because Datadog recognizes those exact OpenTelemetry-standard field names for
that purpose.

**Other Rust binaries (`buzz-push-gateway`, `buzz-test-client`).** Both call
`tracing_subscriber::fmt()` — a plain, human-readable `EnvFilter`-driven formatter, not
`fmt().json()`. This is a second, simpler subscriber shape than the relay's, present in
the same workspace.

**`buzz-admin` and the desktop app's Rust backend (`desktop/src-tauri`, specifically the
`managed_agents` module).** Both call `tracing::warn!`/`tracing::info!` directly, but
neither crate's own source installs a subscriber anywhere this node could find (grepped
every `.rs` file under each crate for `tracing_subscriber::registry()`,
`tracing_subscriber::fmt()`, or any other subscriber-installing call — none found). The
`tracing` crate dispatches events to whichever subscriber is currently registered as the
process-global default and emits nothing when none is installed, so whether these
`warn!`/`info!` calls are actually observed depends on whether some other part of the
same process installs a subscriber — this node did not trace that further and records it
as an inference, not a fact, in the evidence ledger above.

**Desktop frontend (TypeScript/React, `desktop/src`).** No dedicated logger utility
module exists (searched for filenames containing "logger" or "logging"), and
`desktop/biome.json` carries no lint rule targeting `console` (checked directly). 92
files under `desktop/src` call `console.log`, `console.warn`, `console.error` or
`console.debug` directly. This is the frontend's de facto logging convention: there is
no enforced structured-logging layer on this surface today.

**Mobile (Flutter/Dart, `mobile/`).** This repository's own contributor guide states the
rule directly: "Do NOT use `print()` — use `debugPrint()` or structured logging"
(`AGENTS.md:565`). In practice, `mobile/lib` contains 59 `debugPrint` call sites and zero
bare `print(` calls. `mobile/analysis_options.yaml` carries no `avoid_print` (or
equivalent) lint rule, so this convention is followed but not statically enforced in this
repository — a contributor-guide rule, not a tooling gate.

## Use cases

A reader reaches for this node when they need to understand, before diving into any one
surface's specifics: what logging library or convention Buzz uses generally, whether a
given surface's log output is machine-parseable JSON or plain text, how log verbosity is
controlled (`RUST_LOG` vs. the frontend's/mobile's lack of an equivalent knob), and
whether OpenTelemetry trace correlation is available for a given log line. It is also the
first stop for noticing that not every Rust surface actually initializes a subscriber —
a gap worth knowing about before assuming `tracing::warn!` anywhere in the workspace is
necessarily going somewhere.

## Boundaries and non-goals

This node does **not** cover:

- **The structured-field schema** — which fields a given event kind or subsystem should
  attach, naming conventions for fields, or a catalogue of fields already in use. That is
  issue #1144's (structured-logging) territory; this node states only the general
  "prefer structured fields" convention from `CONTRIBUTING.md` and does not attempt to
  enumerate or standardize fields itself.
- **Datastore tracing policy.** `buzz-datastore-tracing` is a separate proc-macro crate
  ("Privacy-preserving datastore tracing policy macros for Buzz") layered on top of the
  general tracing setup described here, with its own `buzz_datastore` tracing target
  visible in the `RUST_LOG`/`BUZZ_OTEL_FILTER` defaults. Its policy mechanics are issue
  #1136's (datastore-tracing) territory, not this node's.
  Neither #1144 nor #1136 has a merged corpus node on `origin/launchpad` at this node's
  recorded revision, so no `relationships` edge to either exists yet — see *Scope and
  omissions*.
- **Metrics and non-log telemetry** (e.g. the Datadog gauge-series cost control visible
  in `buzz-relay/src/main.rs`'s `EmissionScope`) — a related but distinct observability
  concern this node does not describe.
- **Operational log aggregation, retention, or dashboarding** (e.g. how CAKE or Datadog
  actually ingest and store these logs downstream) — this node describes what Buzz emits,
  not what happens to it afterward.

## Scope and omissions

**This document covers** the general logging convention stated in `CONTRIBUTING.md`, and
how each surface this node inspected (relay, push-gateway, test-client, admin CLI,
desktop Rust backend, desktop frontend, mobile) actually initializes — or in two cases
does not initialize — logging, at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Structured-field schema/catalogue for log events | #1144 (structured-logging), not yet a merged corpus node |
| Datastore tracing policy-macro mechanics (`buzz-datastore-tracing`) | #1136 (datastore-tracing), not yet a merged corpus node |
| Metrics/gauge telemetry (separate from logging) | Not investigated for this node |
| Downstream log aggregation/retention (CAKE, Datadog) | Not investigated for this node |

**Expected but not verified when this node was written:**

- **Whether `buzz-admin` or desktop-tauri's `managed_agents` `tracing::warn!`/`info!`
  calls actually produce visible output at runtime.** This node found no
  subscriber-install call in either crate's own source, but did not trace whether a
  subscriber is installed by some other part of the same process (e.g. a shared
  workspace crate, or Tauri's own logging integration) — recorded as an INFERENCE with
  `confidence: 0.6`, not a FACT, in the evidence ledger.
  - **Candidate follow-up** (not filed as part of this task, per the batch-run
    instruction to note rather than file it): confirm whether `buzz-admin` and
    desktop-tauri's `managed_agents` module actually emit observable log output, and if
    not, whether that is an intentional gap or an oversight worth its own issue.
- **Buzz CLI (`buzz-cli`)'s own logging behavior was not established.** `crates/buzz-cli`
  was checked for a `tracing_subscriber`/`env_logger` subscriber-install call and none
  was found in `main.rs`; whether `buzz-cli` relies on `println!`/structured JSON output
  instead of `tracing` (its documented output contract in `AGENTS.md` says CLI reads
  return "sig-stripped JSON arrays") was not traced further, since the CLI's actual
  output contract is a different concern from this node's logging-convention scope.
- **Whether the desktop frontend's 92 `console.*` call sites are read anywhere in
  production** (versus being development-only) was not established — only their
  existence and the absence of a lint rule against them.
