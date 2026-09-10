---
id: verification-performance-fanout
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
  - statement: "buzz-pubsub's crate description is 'Redis pub/sub fan-out, presence, and typing indicators for Buzz', and its own module documentation diagrams the fan-out path as: relay process -> deadpool-redis pool PUBLISH -> a dedicated (non-pooled) redis::aio::PubSub connection SUBSCRIBEd to buzz:{community}:channel:{id} / buzz:{community}:global -> run_subscriber() -> a local broadcast::channel(4096) -> N WebSocket receivers."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "publisher::publish_event issues a Redis PUBLISH of the event's JSON to a community- and topic-scoped channel key and returns the subscriber count Redis reports; subscriber::connect_and_subscribe SUBSCRIBEs to the desired-topic snapshot, forwards each received payload to the local broadcast_tx, and reconnects with exponential backoff from 1s up to a 30s cap on any connection error or clean disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/publisher.rs"
      - "crates/buzz-pubsub/src/subscriber.rs"
  - statement: "buzz-pubsub's own module documentation states the local fan-out channel's capacity is fixed at 4096 and that 'Lagged receivers get RecvError::Lagged'; PubSubManager::with_config constructs that channel as broadcast::channel(4096), meaning a locally-subscribed WebSocket connection that falls too far behind has its oldest buffered events dropped and is signaled Lagged, rather than the publisher blocking or the channel's memory growing without bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "On the relay side, fan_out_event_to_local_subscribers and dispatch_persistent_event both call SubscriptionRegistry::fan_out_scoped to find matching local (connection, subscription) pairs, then filter_fanout_by_access to revalidate delivery access, then record the resulting recipient count on the buzz_fanout_recipients Prometheus histogram before writing any WebSocket frames."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/subscription.rs"
  - statement: "buzz_fanout_recipients is registered with integer-count histogram buckets (0, 1, 5, 10, 25, 50, 100, 500, 1000) named FANOUT_BUCKETS -- it measures how many local recipients a single dispatch matched, not delivery latency or Redis publish/subscribe timing, and no code path asserts a bound on its recorded values."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "buzz-pubsub's own test suite includes test_publish_and_subscribe_roundtrip, marked #[ignore = \"requires Redis\"], which publishes one event and asserts it is received on a local broadcast receiver within a 2-second timeout; this is a functional round-trip/liveness assertion (the event arrives at all) rather than a throughput or latency-bound assertion, and the 2-second timeout is a generous failure ceiling, not a documented SLA."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "crates/buzz-test-client/src/bin/wamp_bench.rs is a standalone binary (not a #[test] or #[ignore]-gated test) that opens N authenticated WebSocket connections and sends kind:9 events at a target aggregate qps, measuring the per-message 'OK' (write-acceptance) round-trip latency and reporting p50/p95/p99/max on stdout; its own module doc-comment describes it as a 'load generator for relay write-amplification benchmarking', i.e. it measures the ingest/write-ack path, not delivery latency to other subscribers via Redis pub/sub or local broadcast fan-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/bin/wamp_bench.rs"
  - statement: "wamp_bench.rs was added by block/buzz PR #2125 ('relay: skip TTL deadline bump for known-permanent channels (T1a write-amp)') and its own PR body reports 'measured impact' as net Postgres commits per accepted message at varying qps, comparing baseline against the change -- it was built and used to investigate write-amplification on the ingest path, not fan-out delivery performance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "block/buzz#2125 PR body ('Measured impact' section)"
  - statement: "grep across .github/workflows/*.yml and Justfile for wamp_bench or wamp-bench found no matches, and no criterion (or other benchmark-harness) dependency exists in any workspace crate's Cargo.toml; a repository-wide case-insensitive search for fanout, fan-out, throughput, benchmark, criterion, load.test and latency across *.rs and *.md files found no artifact -- test, benchmark, or CI job -- that exercises buzz-pubsub's Redis-based cross-pod fan-out or the relay's WebSocket broadcast-to-many-subscribers path under load."
    entry_class: FACT
    evidence:
      - "grep_search('wamp_bench|wamp-bench', scope='.github/workflows/*.yml;Justfile') -> no matches"
      - "grep_search('criterion', scope='**/Cargo.toml') -> no matches"
      - "grep_search('fanout|fan-out|throughput|benchmark|criterion|load.test|latency', scope='**/*.rs;**/*.md', case_insensitive=true) -> matches found across the repository, none naming an automated fan-out performance test or CI-gated benchmark"
  - statement: "Because a repository-wide grep sweep cannot prove a negative with certainty -- a differently-worded benchmark, or one invoked only by an undocumented local script, could exist unfound -- the absence of an automated fan-out performance test is reported here as a checked-but-not-exhaustive finding rather than an unconditional guarantee."
    entry_class: INFERENCE
    evidence:
      - "grep_search('fanout|fan-out|throughput|benchmark|criterion|load.test|latency', scope='**/*.rs;**/*.md', case_insensitive=true) -> matches found, none naming an automated fan-out performance test or CI-gated benchmark"
    confidence: 0.6
  - statement: "architecture-flows-live-fanout (a merged corpus node) documents the same dispatch path this node cites -- dispatch_persistent_event, publish_event, fan_out_scoped, filter_fanout_by_access -- as a correctness/authorization flow, and does not itself make any claim about that path's performance under load."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/live-fanout.md"
  - statement: "architecture-containers-redis (a merged corpus node) documents buzz-pubsub's PubSubManager, its Redis PUBLISH/SUBSCRIBE mechanics and its dedicated (non-pooled) connections, without asserting any latency or throughput bound on them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries no node under verification/, so this is the first node in that subtree; architecture-flows-live-fanout and architecture-containers-redis are both present and loadable, so a references edge to each resolves."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, capabilities/**, development/**, layers/**, schema/** (excluded from validation), standards/**, templates/**; no verification/** entries; architecture/flows/live-fanout.md and architecture/containers/redis.md both present"
  - statement: "Issue #1381's definition of done requires this node to name the verifying test(s) that implement the obligation, state enforcement status honestly, and not claim coverage that is not present; per launchpad/docs/corpus/templates/test-contract.md, a pending obligation documented honestly is not a weaker artefact than a passing one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1381 definition of done, and launchpad/docs/corpus/templates/test-contract.md's Required sections §5"
relationships:
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-containers-redis
---

# Fan-out performance — test contract

## Purpose and boundary

This node documents one obligation about **Buzz's live event fan-out under load**: what
happens to a locally-subscribed WebSocket connection when published events arrive faster
than it consumes them, and whether that behavior is enforced by any automated test. It
covers that one obligation only. It does not cover fan-out **correctness** (routing,
authorization, scoping) -- that is `architecture-flows-live-fanout`'s subject, backed by
`buzz-pubsub`'s and `buzz-relay`'s own functional tests -- and it does not cover
cross-pod Redis PUBLISH/PSUBSCRIBE throughput or latency under sustained multi-relay
load, which no test or benchmark in this repository currently measures at all (see
*Scope and omissions*).

## Obligation

> When events published on a subscribed Redis topic arrive faster than a local
> WebSocket connection's fan-out receiver consumes them, that connection's buffered
> events beyond the fixed 4096-entry `broadcast` channel capacity are dropped (surfaced
> to the subscriber loop as `RecvError::Lagged`) rather than the publisher blocking,
> other subscribers being delayed, or the channel's memory growing without bound.

## Verifying test(s)

**None exist at the recorded revision.** No test in this repository constructs a
slow/lagging local subscriber and asserts the `Lagged` drop-and-continue behavior, and
no test or benchmark measures Redis PUBLISH/PSUBSCRIBE fan-out latency or throughput
across relay instances, or WebSocket broadcast-to-many-subscribers latency, under load.

The closest existing artifacts, neither of which verifies this obligation:

- `crates/buzz-pubsub/src/lib.rs`'s `test_publish_and_subscribe_roundtrip`
  (`#[ignore = "requires Redis"]`) -- asserts one event round-trips through
  PUBLISH -> SUBSCRIBE -> local broadcast within a 2-second timeout. It is a
  correctness/liveness check (does the event arrive at all), not a throughput or
  latency measurement, and it never constructs a lagging receiver.
- `crates/buzz-test-client/src/bin/wamp_bench.rs` -- a manual load-generator binary
  that measures per-message write-**acceptance** ("OK") latency on the ingest path, at
  a target qps across N connections. It was built for a write-amplification
  investigation (block/buzz PR #2125), not for fan-out delivery. It measures how fast
  the relay acknowledges a write, not how fast -- or how reliably -- that write is then
  delivered to other subscribers.

## How to run it

N/A. There is no automated verifying test for this obligation to run. The two related
artifacts above can be run manually but do not exercise the obligation stated here:

```bash
# Functional round-trip only (not a load test; requires a local Redis):
cargo test -p buzz-pubsub --lib test_publish_and_subscribe_roundtrip -- --ignored

# Write-acceptance latency under load (not a fan-out-delivery test):
# BUZZ_RELAY_URL and BENCH_PRIVATE_KEY must be set; requires a running relay.
cargo run -p buzz-test-client --bin wamp_bench -- <channel_uuid> <qps> <duration_secs> <conns> <latency_out>
```

## Current enforcement status

**Pending.** The obligation is real, testable, and grounded in code that exists today
(`broadcast::channel(4096)`, `RecvError::Lagged`) -- but nothing in this repository's
test suite, CI configuration, or benchmark tooling currently exercises it. No test
constructs an overloaded local subscriber; no test or benchmark measures Redis
PUBLISH/PSUBSCRIBE fan-out latency or throughput across relay pods; no CI job or
`Justfile` recipe invokes `wamp_bench` or any other load-generation tool. `pending` here
means exactly what `templates/test-contract.md` says it should: the obligation is
stubbed by nothing, tracked only by this document and by issue #1381/#617.

## Limits

Even if the manual tools above were run, neither would establish this obligation:

- `test_publish_and_subscribe_roundtrip` uses one publisher and one subscriber with no
  induced lag, so it can never observe `RecvError::Lagged` or the 4096-entry boundary; a
  passing run says nothing about backpressure behavior.
- `wamp_bench` has no subscriber side at all -- it measures the sender's view of write
  acceptance, never whether or how fast a receiver got the event, and never runs against
  more than one relay pod, so it says nothing about cross-pod Redis fan-out.
- Neither artifact is CI-gated, so even a manual pass today gives no ongoing guarantee
  about tomorrow's code.
- The `buzz_fanout_recipients` Prometheus histogram observes recipient *counts* in
  production, not latency, and nothing reads or alerts on it automatically; it is
  production observability, not a test, and this node does not treat it as one.

## Scope and omissions

**This node covers** one obligation: local per-connection backpressure behavior
(bounded-buffer drop-on-lag) in `buzz-pubsub`'s fan-out broadcast channel, and its
current (pending) enforcement status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Fan-out routing correctness, authorization, and scoping | `architecture-flows-live-fanout` (merged corpus node), and `buzz-relay`'s/`buzz-pubsub`'s own functional test suites |
| Redis PUBLISH/PSUBSCRIBE latency or throughput across multiple relay pods under sustained load | Unowned -- no test, benchmark, or corpus node exists for this at the recorded revision; not raised as a new task per this issue's instruction to name it here rather than file a separate issue |
| End-to-end WebSocket broadcast-to-many-subscribers latency percentiles | Unowned, same as above |
| Write-path ingest/acceptance latency and amplification | `wamp_bench.rs` and block/buzz PR #2125's write-amp workstream -- a different obligation (ingest, not fan-out delivery) that this node deliberately does not fold in |
| The general corpus evidence, citation, and test-reference contracts | `launchpad/docs/corpus/AGENTS.md`, `standards/evidence.md`, `standards/test-references.md`, `standards/confidence.md` |

**Expected but not verified when this node was written:**

- **Whether the 4096-entry broadcast capacity is actually reached in production
  traffic patterns.** No production metric or log line surfaced during this
  investigation counts `RecvError::Lagged` occurrences; `buzz_fanout_recipients`
  measures recipient counts, not lag events, so whether this obligation's failure mode
  has ever actually occurred outside a synthetic test is unknown.
- **Whether an equivalent backpressure obligation exists on the Redis side** (e.g.
  Redis client-side buffer limits, `redis::aio::PubSub` internal buffering) rather than
  only on the local `tokio::sync::broadcast` channel documented here. Only the local
  channel's documented behavior was read for this node.
- **The repository-wide grep sweep for benchmark/load-test artifacts is a checked
  scope, not an exhaustive proof of absence** -- see the INFERENCE entry in this node's
  evidence ledger rating that gap at Medium confidence.
