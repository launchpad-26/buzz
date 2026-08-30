---
id: debugging
type: development
status: draft
origin: launchpad
audiences:
- developer
- agent
- reviewer
evidence:
- statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
  entry_class: FACT
  evidence:
  - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
- statement: "buzz-relay's stdout logging is a tracing_subscriber::fmt JSON layer, and the RUST_LOG environment variable controls it via a tracing-subscriber EnvFilter that defaults to the string \"buzz_relay=info\" (a target=level directive) when RUST_LOG is unset."
  entry_class: FACT
  evidence:
  - "crates/buzz-relay/src/main.rs"
- statement: "A unit test in buzz-relay's own env_filter_tests module pins this default: with RUST_LOG unset, buzz_relay events at INFO are enabled while buzz_datastore events at INFO are not, and passing an explicit override string (e.g. \"warn\") is honored verbatim by the same log_env_filter function."
  entry_class: FACT
  evidence:
  - "crates/buzz-relay/src/main.rs"
- statement: "CONTRIBUTING.md's \"Logging and Tracing\" section instructs contributors to use the tracing crate for all instrumentation and to prefer structured fields (e.g. tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\")) over string interpolation into the message."
  entry_class: FACT
  evidence:
  - "CONTRIBUTING.md"
- statement: "TESTING.md's Troubleshooting table is the repository's existing canonical symptom/cause/fix reference for common local-relay failures, covering stale binaries, port collisions, missing or stale auth environment variables, ACP agent membership/response-gate issues, and CI-vs-local test drift."
  entry_class: FACT
  evidence:
  - "TESTING.md"
- statement: "TESTING.md documents verifying a running local relay with `curl -s http://localhost:3000/health` and `curl -s http://localhost:8080/_readiness`, and states that health/readiness/liveness are served on a separate port (default 8080, BUZZ_HEALTH_PORT) specifically so Kubernetes probes bypass the relay's auth middleware."
  entry_class: FACT
  evidence:
  - "TESTING.md"
- statement: "buzz-relay's router mounts /_liveness and /_readiness handlers on the health-only router, separate from the main application router."
  entry_class: FACT
  evidence:
  - "crates/buzz-relay/src/router.rs"
- statement: "buzz-relay fails closed on a port collision at startup: binding the health-port listener and the main TCP listener each map a bind error to an anyhow error whose message names the specific port that failed to bind (e.g. \"Failed to bind health port {port}: {e}\")."
  entry_class: FACT
  evidence:
  - "crates/buzz-relay/src/main.rs"
- statement: "buzz-relay separately supports exporting spans over OTLP/gRPC through an OpenTelemetry tracing_subscriber layer, gated on the OTEL_EXPORTER_OTLP_ENDPOINT environment variable (a no-op when unset) and filtered independently of RUST_LOG by BUZZ_OTEL_FILTER, which defaults to \"buzz_relay=info,buzz_datastore=info\"."
  entry_class: FACT
  evidence:
  - "crates/buzz-relay/src/telemetry.rs"
- statement: "launchpad/docs/Observability/current-state/relay.md documents that the relay's stdout surface is newline-delimited JSON carrying timestamp, level, target and message, that events inside a span additionally carry that span's fields, and that when OTLP is enabled, span-correlated lines additionally carry trace_id and span_id while bare events do not."
  entry_class: FACT
  evidence:
  - "launchpad/docs/Observability/current-state/relay.md"
- statement: "The Justfile's `logs` recipe tails all Docker Compose service logs (`docker compose logs -f`), which is how a developer inspects Postgres/Redis (and any other Compose-managed dependency) rather than the relay process's own stdout."
  entry_class: FACT
  evidence:
  - "Justfile"
- statement: "`just reset` runs scripts/dev-reset.sh --yes, which stops all services and deletes all local service volumes (Postgres, MinIO) and development desktop state, then brings services back up and re-runs migrations; installed Buzz app state and its production keyring are preserved, and Redis data is always wiped on restart regardless."
  entry_class: FACT
  evidence:
  - "scripts/dev-reset.sh"
- statement: "TESTING.md warns that a local dev relay and a running Buzz Desktop instance share the same Docker container names and default Postgres/Redis ports, so `just setup` reuses Desktop's services and `just reset` wipes Desktop's data along with the test relay's, unless the developer stops Desktop first or runs the dev stack under a different Compose project name."
  entry_class: FACT
  evidence:
  - "TESTING.md"
- statement: "TESTING.md separates `just test-unit` (unit tests, no infrastructure needed) from `just test` (unit plus integration tests against Postgres and Redis, started automatically if not already running), as the two narrowing levels before reaching for a live local relay."
  entry_class: FACT
  evidence:
  - "TESTING.md"
- statement: "The repository's agentic-debugging skill (.claude/skills/agentic-debugging/SKILL.md) defines a separate evidence-first investigation loop — reproduce, gather evidence, localize, hypothesize, test, fix, add coverage, verify, review — that governs how an agent diagnoses a bug before changing code; it does not describe buzz-relay's own logging, health, or reset tooling, which is this node's subject."
  entry_class: FACT
  evidence:
  - ".claude/skills/agentic-debugging/SKILL.md"
- statement: "Overriding RUST_LOG to raise buzz-relay's own log verbosity (e.g. RUST_LOG=buzz_relay=debug) follows the identical target=level directive syntax as the crate's own default filter string, rather than a separately-documented override convention."
  entry_class: INFERENCE
  evidence:
  - "crates/buzz-relay/src/main.rs"
  confidence: 0.75
---

# Debugging a local buzz-relay: how-to

Diagnose unexpected `buzz-relay` behavior on a local development instance using the
relay's own structured logs, health/readiness endpoints, and the repository's existing
troubleshooting and reset tooling — without reaching for a debugger or reading
unfamiliar code cold.

## Before you start

- A local relay set up per `TESTING.md`'s "Live Local Relay" section: Hermit toolchain
  activated, `.env` copied, `just setup` run, and release binaries on `PATH`.
- A terminal running `buzz-relay` (or `cargo run --release -p buzz-relay`) in the
  foreground, and a separate working terminal for the commands below.

## Read the relay's logs at the right verbosity

1. Note that `buzz-relay` always writes newline-delimited JSON logs to stdout — this
   layer is unconditional and unrelated to whether OpenTelemetry export is configured.
2. Reproduce the behavior you're diagnosing with the relay running in its foreground
   terminal, and read the JSON lines it emits there; each line carries at minimum
   `timestamp`, `level`, `target`, and `message`, plus any fields of the enclosing span.
3. If the default verbosity (`RUST_LOG` unset, equivalent to `buzz_relay=info`) doesn't
   show what you need, restart the relay with `RUST_LOG=buzz_relay=debug buzz-relay` —
   the override string follows the same `target=level` syntax as the built-in default,
   just at a lower level. Narrow further to a specific crate (e.g.
   `RUST_LOG=buzz_relay=debug,buzz_datastore=debug`) rather than raising every crate's
   verbosity at once.
4. If you're adding a new `tracing::` call to see a value you don't currently log,
   follow CONTRIBUTING.md's "Logging and Tracing" convention — structured fields
   (`tracing::info!(channel_id = %id, …)`), not string-interpolated messages — so the
   new field is queryable the same way existing fields are.

## Confirm the relay is actually up and reachable

1. `curl -s http://localhost:3000/health` should return `ok`.
2. `curl -s http://localhost:8080/_readiness` should return `{"status":"ready"}`. This
   is a separate port (default 8080, `BUZZ_HEALTH_PORT`) precisely so a probe or a
   developer can check liveness/readiness without going through the relay's auth
   middleware.
3. If either call hangs or refuses the connection, check the relay's own terminal for a
   startup error before assuming the symptom is elsewhere — a bind failure on either
   the main port or the health port fails closed at startup and names the specific port
   in its error message (e.g. `Failed to bind health port 8080: …`).
4. If you're running multiple relays (a local dev relay alongside Buzz Desktop, for
   example), confirm you're actually probing the one you think you are — each bound
   port (`BUZZ_BIND_ADDR`, `BUZZ_HEALTH_PORT`, `BUZZ_METRICS_PORT`) is independently
   overridable, and a stale relay from an earlier session can be listening on the
   default ports instead of the one you just started.

## Localize a specific symptom

1. Check TESTING.md's Troubleshooting table first — it already maps common local-relay
   symptoms (stale binaries, port collisions, missing or stale auth environment
   variables, ACP membership/response-gate misses, CI-vs-local drift) to their fix.
   This node does not restate that table; treat it as the first stop, not this doc.
2. If the symptom isn't in that table, widen from the relay's own logs to its
   dependencies: `just logs` tails every Docker Compose service (Postgres, Redis, and
   anything else Compose-managed) rather than the relay process's own stdout.
3. If you suspect the bug is in a specific code path rather than local environment
   drift, narrow with the automated suite before touching a live relay: `just
   test-unit` (no infrastructure) first, then `just test` (adds Postgres/Redis
   integration coverage) — both are faster feedback loops than reproducing through a
   live relay and CLI.
4. If you're diagnosing a genuine bug (not a local environment problem) and are about
   to change code, this node's job stops here — hand off to the systematic
   evidence-before-fix loop the repository's `agentic-debugging` skill defines for
   exactly that transition (see *Boundary*, below).

## Reset local state safely

1. If local Postgres/Redis/MinIO state itself looks corrupted (not just the relay
   process), stop chasing it through logs and run `just reset` instead — it stops all
   services, deletes all local service volumes, and brings everything back up with
   migrations re-run.
2. Before running it, check whether Buzz Desktop is also running: `just setup` and
   `just reset` reuse Desktop's Docker container names and default ports, so a test
   relay's `just reset` also wipes Desktop's local data. Stop Desktop first, or run
   the dev stack under a different `COMPOSE_PROJECT_NAME`, if you need isolation.
   Installed Buzz app state and its production keyring are preserved either way; Redis
   data is always ephemeral regardless of `reset`.
3. Verify recovery the same way as *Confirm the relay is actually up and reachable*,
   above, before resuming the diagnosis you were in the middle of.

## See also

- `TESTING.md` — the canonical local-relay setup and troubleshooting reference this
  node builds on; its Troubleshooting table is authoritative, not duplicated here.
- `CONTRIBUTING.md`'s "Logging and Tracing" section — the convention for writing new
  structured log statements.
- `launchpad/docs/Observability/current-state/relay.md` — the fuller current-state
  description of the relay's four independent instrumentation mechanisms (logs,
  OTLP traces, Prometheus metrics, health/status routes), for when a symptom needs
  trace- or metric-level evidence rather than logs alone.
- `.claude/skills/agentic-debugging/SKILL.md` — the evidence-first loop for diagnosing
  and fixing an actual bug, once this node's tooling has produced evidence to reason
  from.

## Boundary

This node does not describe:
- The specific symptom-to-fix mappings already catalogued in TESTING.md's
  Troubleshooting table — that table is the reference for those, and this node
  defers to it rather than re-deriving or copying it.
- The full architecture of the relay's logging/tracing/metrics/health instrumentation
  — see `launchpad/docs/Observability/current-state/relay.md` for that lookup content.
- How to acquire debugging skill from scratch as a newcomer — a tutorial, which has no
  corpus template as of this writing.
- The methodology for diagnosing and fixing a genuine bug once you have evidence in
  hand (forming a falsifiable hypothesis, testing it, adding regression coverage) —
  that is `.claude/skills/agentic-debugging/SKILL.md`'s subject for agents, and
  ordinary engineering judgement for a human contributor; this node stops at
  producing the evidence.
- Debugging a deployed/production relay, or any Buzz surface other than a locally-run
  `buzz-relay` (desktop, mobile, web) — those are separate procedures, in scope for
  other tasks under Feature #619 and elsewhere, not this one.

## Relationships

- implements: corpus-template-procedure

## Scope and omissions

**This node covers** the concrete, repository-specific tools and commands a developer
or agent uses to diagnose unexpected `buzz-relay` behavior on a local instance: reading
its structured JSON logs at an adjusted verbosity, confirming liveness/readiness,
localizing a symptom via the existing troubleshooting table and the automated test
suite's two narrowing levels, and resetting local service state safely (including the
shared-with-Desktop pitfall).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The symptom-to-fix table itself | `TESTING.md`'s Troubleshooting section |
| The relay's full instrumentation architecture (logs/traces/metrics/health as a system) | `launchpad/docs/Observability/current-state/relay.md` |
| The evidence-before-fix investigation methodology once a bug is localized | `.claude/skills/agentic-debugging/SKILL.md` (agents); ordinary engineering practice (humans) |
| Debugging a deployed/production relay | Not yet authored under this Feature (#619) at the time of writing |
| Debugging desktop, mobile, or web clients specifically | Other, separate tasks; out of this node's scope |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**No other relationships declared.** The only merged corpus nodes at the recorded
revision besides templates are the `architecture/*` nodes (containers, context,
deployment, flows, principles) — none of them are how-to-shaped or about diagnosing
relay behavior, so none is a fit for `references`/`depends-on`/`part-of`. The sibling
`development/*` tasks under Feature #619 (setup, run-relay, rust-style, and the rest)
were open with no merged node at the time of writing, so no edge could target them
either; the first of them to merge is the natural moment to add a `references` edge
back and forth (e.g. to `development/setup.md` or `development/run-relay.md`, once
either exists).

**Expected but not verified when this node was written:**

- **The `RUST_LOG=buzz_relay=debug` override was not actually executed against a
  running relay** — building the release binaries and starting the Docker-backed
  Postgres/Redis stack was out of reach in the environment this node was authored in.
  The claim rests on reading `log_env_filter`'s source and its own unit tests (which do
  exercise the default and an explicit override string, just not that specific one),
  not on having run the command — hence that step's evidence entry is classed
  `INFERENCE`, not `FACT`, per this corpus's own rule that a `FACT` about a procedure
  needs to have been executed, not merely read about.
- **Whether the 8-10-step guidance in `corpus-template-procedure` needed adjustment for
  a real instance** was not separately re-verified beyond following it; this is the
  first node authored from that template (per the template's own "expected but not
  verified" note), so this node is itself the first real test of that guidance.
- **BUZZ_METRICS_PORT and the Prometheus /metrics surface** were not exercised as a
  debugging signal in this node's steps, even though `launchpad/docs/Observability/current-state/relay.md`
  documents them; they were judged out of scope for a first-pass logs/health/reset
  how-to rather than actively verified as irrelevant.
