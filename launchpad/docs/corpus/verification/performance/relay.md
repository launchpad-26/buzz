---
id: verification-performance-relay
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree contains no verification/ subtree at all, so neither verification-performance-fanout nor verification-performance-database -- the sibling nodes for issues #1381 and #1380 -- exist yet to declare a relationship toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no path matching 'verification/' at this revision"
  - statement: "perf/relay_bus_scaling.py, paired with perf/RELAY_BUS_SCALING.md, measures only Redis PUB/SUB fan-out scaling between an old global bus and a new community-scoped bus (simulated relay-pod subscribers, no DB ingest, no WebSocket framing, no relay business logic), and RELAY_BUS_SCALING.md states in its own text that 'live relay latency, DB capacity, and client rendering should be measured separately with a full stack because they include unrelated bottlenecks.'"
    entry_class: FACT
    evidence:
      - "perf/RELAY_BUS_SCALING.md"
  - statement: "crates/buzz-relay/src/metrics.rs installs a Prometheus recorder via PrometheusBuilder bound to the metrics listener (default :9102) and records an http_request_latency_ms histogram plus an http_requests_total counter for every matched HTTP/WebSocket-upgrade request through its track_metrics middleware, with per-metric latency buckets defined for 5ms-10s."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:27-30"
      - "crates/buzz-relay/src/metrics.rs:59-147"
      - "crates/buzz-relay/src/metrics.rs:161-207"
  - statement: "crates/buzz-relay/src/config.rs defines BUZZ_MAX_CONNECTIONS (default 10,000), BUZZ_MAX_CONCURRENT_HANDLERS (default 1,024) and BUZZ_SEND_BUFFER (default 1,000 messages per connection) as the relay's own configured capacity ceilings, read from environment variables at startup with those defaults applied when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:636-649"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's test_multiple_concurrent_clients is #[ignore]d and exercises exactly three concurrently connected clients to verify fan-out correctness -- that every subscriber receives the broadcast content -- not throughput, latency or capacity under load."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:627-681"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's test_subscription_limit_enforced is #[ignore]d, and its own doc comment states explicitly: 'This is a protocol-cap test, not an admission-throughput test.' It proves the NIP-11 max_subscriptions cap (1024) is enforced, not that the relay sustains any given admission rate."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:873-927"
  - statement: "A repository-wide search for load-generation tooling (k6, vegeta, wrk, artillery, gatling, locust) and for any [[bench]] target in a workspace Cargo.toml found no genuine reference: the only regex hits (pnpm-lock.yaml, two desktop persona files) were coincidental substring matches inside base64-encoded avatar image data and an unrelated lockfile entry, confirmed by opening each match; no [[bench]] target exists anywhere in the repository."
    entry_class: FACT
    evidence:
      - "grep_search('k6|vegeta|wrk2?\\b|artillery|gatling|locust', scope='*.rs;*.toml;*.md;*.yml;*.yaml, excluding node_modules/,target/') -> pnpm-lock.yaml, desktop/src-tauri/src/managed_agents/personas.rs, desktop/src-tauri/src/managed_agents/persona_avatars.rs; each match inspected and found unrelated (base64 avatar data, no matching package name)"
      - "grep_search('[[bench]]', scope='**/Cargo.toml') -> no results"
  - statement: ".github/workflows/benchmark-harbor.yml and benchmarks/harbor-buzz-orchestra/ exercise AI-agent task correctness and behavior (e.g. whether an agent replies in the correct thread, mentions the correct user) through the real relay/Postgres stack, not relay throughput, latency, or connection capacity; desktop/playwright.perf.config.ts drives Playwright performance specs against the desktop web client's own preview server, not the relay process."
    entry_class: FACT
    evidence:
      - "benchmarks/harbor-buzz-orchestra/README.md"
      - "benchmarks/buzz-dataset/README.md"
      - "desktop/playwright.perf.config.ts"
  - statement: "launchpad-26/buzz#41 ('prd-05 -- internal performance and agent-workload testing harness'), and its dependent tasks #39 ('build a load-generation tool and measure relay capacity under concurrent load') and #18 ('measure whether the Buzz VPS stack fits 1 vCPU and 1.9 Gi'), were each closed with stateReason NOT_PLANNED; no load-generation harness or relay-capacity measurement was built or merged under any of them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#41, #39 and #18 (issue state and stateReason, each CLOSED / NOT_PLANNED, queried via `gh issue view --json state,stateReason`)"
  - statement: "launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md, ratifying the relay's production VPS sizing, states plainly that the decision was made 'without the measurements it named,' that 'M0 stops waiting on a load test nobody has started,' and that the relay is 'very likely running cluster-sized defaults' (BUZZ_MAX_CONNECTIONS 10,000; BUZZ_SEND_BUFFER 1,000/connection; BUZZ_MAX_CONCURRENT_HANDLERS 1,024) on a 1.9 Gi host with no measured ceiling for peak memory under load."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md"
  - statement: "launchpad/REQUIREMENTS.md's NFR-013 row names 'internal performance and agent-workload testing harness' (linking issue #41) and carries an em-dash in its Milestone column, the marker that row uses for work with no milestone assigned, unlike scheduled NFR rows in the same table."
    entry_class: FACT
    evidence:
      - "launchpad/REQUIREMENTS.md:272"
  - statement: "No test, benchmark, or CI job in this repository currently measures the relay's connection-handling capacity, message-fanout throughput, or request/response latency under concurrent load and gates on the result; the closest artifacts either scope narrower (perf/relay_bus_scaling.py: Redis fan-out only) or explicitly disclaim being a throughput measurement (test_subscription_limit_enforced's own doc comment)."
    entry_class: INFERENCE
    evidence:
      - "perf/RELAY_BUS_SCALING.md"
      - "crates/buzz-test-client/tests/e2e_relay.rs:873-927"
      - "gh_issue_view('41,39,18', fields='state,stateReason') -> all three CLOSED / NOT_PLANNED"
    confidence: 0.8
relationships:
  - type: implements
    target: corpus-template-test-contract
---

# Relay performance -- test contract

## Purpose and boundary

This node documents one obligation: that the Buzz relay's own **process-wide**
performance under concurrent client load -- connection admission, message
throughput, and request/response latency, considered as a property of the
`buzz-relay` binary as a whole -- is measured by a repeatable, automated check
rather than assumed safe from configuration defaults alone. It covers **only**
that whole-process obligation. It explicitly does not cover the Redis
fan-out-scoped scaling claim measured by `perf/relay_bus_scaling.py` (the
future `verification-performance-fanout` node, issue #1381's subject) or any
Postgres/database-specific capacity claim (the future
`verification-performance-database` node, issue #1380's subject) -- both are
narrower slices of "relay performance" that get their own independently
maintainable nodes once authored, per this corpus's one-node-one-idea rule.
Neither sibling node exists in `origin/launchpad`'s corpus tree at the
recorded revision, so this node declares no relationship toward either.

## Obligation

> The relay's WebSocket connection admission and message-fanout throughput
> under concurrent client load are measured against the relay's own
> configured capacity ceilings (`BUZZ_MAX_CONNECTIONS`,
> `BUZZ_MAX_CONCURRENT_HANDLERS`, `BUZZ_SEND_BUFFER`) by a repeatable,
> automated load-generation check, rather than assumed safe from those
> defaults alone.

## Verifying test(s)

**None exist today.** No test, benchmark, or CI job in this repository
currently exercises the relay under concurrent synthetic load and reports
throughput, latency, or connection-capacity figures. The nearest artifacts,
and why none of them verify this obligation:

- `perf/relay_bus_scaling.py` / `perf/test_relay_bus_scaling.py` -- measures
  only the Redis PUB/SUB fan-out bus (old global vs. new community-scoped
  channel subscription), using simulated pod subscribers with no DB, no
  WebSocket framing, and no relay business logic. Its own document says so:
  "Live relay latency, DB capacity, and client rendering should be measured
  separately with a full stack because they include unrelated bottlenecks."
  This is the fan-out-specific harness the future `verification-performance-fanout`
  node should cite, not this one.
- `crates/buzz-test-client/tests/e2e_relay.rs::test_multiple_concurrent_clients`
  (`#[ignore]`d) -- verifies fan-out *correctness* across exactly three
  concurrently connected clients (every subscriber receives one broadcast
  message), not throughput or scale.
- `crates/buzz-test-client/tests/e2e_relay.rs::test_subscription_limit_enforced`
  (`#[ignore]`d) -- verifies the NIP-11 `max_subscriptions` protocol cap
  (1024) is enforced; its own doc comment states plainly, "This is a
  protocol-cap test, not an admission-throughput test."
- `.github/workflows/benchmark-harbor.yml` /
  `benchmarks/harbor-buzz-orchestra/` -- grades AI-agent task *behavior*
  (correct thread, correct mention target, correct channel shape) run
  through the real relay/Postgres stack. It is not a throughput or capacity
  measurement of the relay process.
- `desktop/playwright.perf.config.ts` -- drives Playwright performance specs
  against the desktop web client's own static preview server
  (`python3 -m http.server`), not against a running relay.

## How to run it

There is no command to run, because no such check exists. The closest
related, already-`#[ignore]`d correctness tests can be run with:

```bash
cargo test -p buzz-test-client --test e2e_relay -- --ignored test_multiple_concurrent_clients
cargo test -p buzz-test-client --test e2e_relay -- --ignored test_subscription_limit_enforced
```

against a running relay, per `TESTING.md`. Running them exercises the paths
named above; it does not establish anything about the stated obligation, for
the reasons given in *Verifying test(s)*.

## Current enforcement status

**Pending**, as of `473205a7457b208455f188847bfb27b01aa83cac`. No automated
load-generation harness or performance gate exists for the relay as a whole
process. This is not merely an unnoticed gap: a dedicated effort to build one
was proposed and explicitly abandoned. `launchpad-26/buzz#41` ("prd-05 --
internal performance and agent-workload testing harness") and its dependent
tasks `#39` ("build a load-generation tool and measure relay capacity under
concurrent load") and `#18` were each closed `NOT_PLANNED`. `ADR-0018`
ratified the relay's production VPS sizing without the load measurement it
had originally named as a gate, recording plainly that "M0 stops waiting on a
load test nobody has started" and that the relay is "very likely running
cluster-sized defaults" with no measured ceiling. `REQUIREMENTS.md`'s
`NFR-013` still names the harness as a requirement, unscheduled (no
milestone).

## Limits

There is nothing to state limits *of*, because no test exists to have limits.
What follows is what a reader must not infer from that absence:

- **The relay exposing Prometheus metrics is not the same as the obligation
  being verified.** `crates/buzz-relay/src/metrics.rs` records an
  `http_request_latency_ms` histogram and related counters, and these are the
  raw material a future load-generation check would read. Their existence
  proves the relay is *observable* under load, not that anyone has generated
  load and read them.
- **The configured capacity ceilings are defaults, not measured limits.**
  `BUZZ_MAX_CONNECTIONS` (10,000), `BUZZ_MAX_CONCURRENT_HANDLERS` (1,024) and
  `BUZZ_SEND_BUFFER` (1,000/connection) describe what the relay is configured
  to *accept*, not what the host it runs on has been shown to *sustain*.
  `ADR-0018` records exactly this gap for the cohort's own production host.
- **`test_multiple_concurrent_clients` and `test_subscription_limit_enforced`
  proving their own narrow correctness properties does not partially verify
  this obligation.** Three clients is not "concurrent load," and an admission
  cap being enforced is not a throughput or latency measurement -- the
  second test's own doc comment draws that line explicitly.

## Scope and omissions

**This node covers** the single obligation that the relay's own
connection-handling and message-throughput capacity under concurrent load is
measured by an automated check, as a whole-process property distinct from
fan-out-bus scaling and database-specific capacity, and states honestly that
no such check exists today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis fan-out bus scaling under multiple relay pods | The future `verification-performance-fanout` node (issue #1381), not yet authored |
| Postgres/database-specific capacity and query performance | The future `verification-performance-database` node (issue #1380), not yet authored |
| Whether the cohort's own production relay currently holds under real traffic | Operational monitoring, not a corpus verification node -- `ADR-0018` names this a live, unresolved exposure |
| AI-agent task behavior/correctness benchmarking | `benchmarks/harbor-buzz-orchestra/`, `.github/workflows/benchmark-harbor.yml` -- a different kind of "benchmark" entirely |
| Desktop client-side render/interaction performance | `desktop/playwright.perf.config.ts` -- client, not relay |
| Whether to build the abandoned load-generation harness | Closed `NOT_PLANNED` under `#41`/`#39`/`#18`; reopening it is a product decision this node does not make |

**Expected but not verified when this node was written:**

- **Whether any manual or ad-hoc load test was ever run against the cohort's
  relay outside this repository, with results kept only in conversation or a
  dashboard, was not established.** `ADR-0018` states no figure was recorded
  for its own decision; this node cannot rule out an unrecorded exercise
  elsewhere, only that none is documented in this repository.
- **Whether the Prometheus metrics `metrics.rs` records are actually scraped,
  retained, or alerted on in any deployed environment was not checked.**
  This node establishes only that the relay emits them, not that anything
  downstream consumes them for a capacity signal.
- **The rate limiter's per-tier ceilings** (`crates/buzz-auth/src/rate_limit.rs`:
  60/min humans, 120/300/600 per minute across agent tiers) **bound
  request *admission* per identity and were read for context, but whether
  they were sized from any load measurement, or are simply the same kind of
  unmeasured default as the connection/handler/buffer ceilings above, was not
  established** and is not asserted either way.
