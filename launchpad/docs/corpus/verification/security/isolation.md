---
id: verification-security-isolation
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
  - statement: "A grep for isolation-related identifiers across crates/buzz-agent, crates/buzz-acp, and crates/buzz-backend-kubernetes (the agent-runtime and compute-provider crates) turned up only DB transaction-isolation levels, an unrelated MCP-startup process-isolation default, and model-id label-token parsing tests -- no test in any of those crates asserts a security boundary between one agent's execution and another's, or between an agent and its host."
    entry_class: INFERENCE
    evidence:
      - "run_command('grep -rniE \"isolat\" crates/buzz-backend-kubernetes/src/*.rs crates/buzz-backend-kubernetes/tests/*.rs crates/buzz-acp/src/*.rs crates/buzz-agent/src/*.rs crates/sprig/src/*.rs') -> no matches"
      - "run_command('grep -rniE \"isolat\" crates/buzz-agent/src/model_capabilities.rs crates/buzz-acp/src/acp.rs crates/buzz-acp/src/pool.rs crates/buzz-acp/src/lib.rs crates/buzz-agent/src/hints.rs crates/buzz-agent/src/llm.rs crates/buzz-agent/src/auth.rs') -> hits are label/capability-token parsing test names, an MCP-startup env-default comment, a code-flow comment, and doc-comment prose -- none is a cross-agent or agent/host security-boundary test"
    confidence: 0.6
  - statement: "By contrast, tenant/community isolation has a formal specification, a purpose-built independent checker, and a passing unit test asserting cross-community leakage is rejected, so this node documents that obligation rather than agent compute isolation."
    entry_class: INFERENCE
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
      - "crates/buzz-conformance/src/checker.rs:209-223"
    confidence: 0.8
  - statement: "docs/spec/MultiTenantRelay.tla's own header describes itself as 'Formal model of Buzz's proposed multi-tenant relay/database isolation' and states its master proof obligation as non-interference: 'no value labeled outside a connection's resolved community may flow into that connection's typed observational interface.'"
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:1-15"
  - statement: "crates/buzz-conformance is an independent Rust re-implementation of that spec's transition relation, deliberately built without importing buzz-relay, buzz-db, or buzz-auth so that a bug shared between the production emitter and its own checker cannot hide from both; its checker.rs module implements the replay engine returning one of IllegalTransition, StateMismatch, NonInterference, or CoverageBreach."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:1-9"
      - "crates/buzz-conformance/TRACE_SCHEMA.md"
  - statement: "TransitionError::NonInterference is documented in transitions.rs as 'Row labels include a community other than the resolved tenant -- the master Inv_NonInterference failure', returned by check_trace as an Err variant carrying the offending step index and a human-readable detail."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:60-90"
      - "crates/buzz-conformance/src/checker.rs:74"
  - statement: "checker.rs's own unit test cross_community_row_bites_non_interference constructs a single ReadMessageRows trace step whose row_communities vector contains both the request's resolved community and a second, unrelated 'foreign' community, and asserts check_trace returns an error matching TransitionError::NonInterference."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/checker.rs:209-223"
  - statement: "Running exactly that unconditional unit suite (no #[ignore], no external infrastructure) passes, including the non-interference case by name."
    entry_class: FACT
    evidence:
      - "run_command('cargo test -p buzz-conformance --lib') -> running 9 tests; test checker::tests::cross_community_row_bites_non_interference ... ok; test result: ok. 9 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out"
  - statement: "The relay's write-seam emitter (crates/buzz-relay/src/handlers/ingest.rs) is wired to record TraceAction::WriteInsert/WriteInsertGlobal/WriteDuplicate/AuthCheck/SanitizedError steps through an EmitGuard, and the AbstractState/Tracer types those steps carry are the same schema types the checker's own tests construct directly, so the two share one wire format rather than two independently-drifting ones."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2115-2147"
      - "crates/buzz-conformance/src/lib.rs:142-161"
  - statement: "crates/buzz-relay/src/conformance/mod.rs defines record_read_message_rows and record_read_by_id_rows, each projecting a request's returned rows to their true per-channel community labels and emitting TraceAction::ReadMessageRows / ReadByIdRows (or an ImplBug on a missing lookup), and both functions are called from crates/buzz-relay/src/handlers/req.rs -- record_read_message_rows at line 422 (the non-search REQ lane) and record_read_by_id_rows at line 750 (the search-refetch lane)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs:265-330"
      - "crates/buzz-relay/src/handlers/req.rs:422"
      - "crates/buzz-relay/src/handlers/req.rs:750"
  - statement: "crates/buzz-conformance/LIMITS.md states, in its 'Scope' section, that the read-seam emitter is a 'held-back req.rs patch' and that 'the read-seam half of the gate is not yet armed', and its own last commit touching that file (14fba21e57b8d671ebbea473226be52a5f2ae636) is dated 2026-06-29, while the commit wiring record_read_message_rows/record_read_by_id_rows into req.rs (86b9142a09f2af3ba2fff7effa6a6cd53b40f51c) is dated 2026-08-28, two months later."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:41-48"
      - "git_log(-1, --format='%H %ad', --date=short, path='crates/buzz-conformance/LIMITS.md') -> 14fba21e57b8d671ebbea473226be52a5f2ae636 2026-06-29"
      - "git_log(-1, --format='%H %ad', --date=short, path='crates/buzz-relay/src/handlers/req.rs') -> 86b9142a09f2af3ba2fff7effa6a6cd53b40f51c 2026-08-28"
  - statement: "LIMITS.md's statement that the read-seam emitter is held back is stale as of this node's recorded revision: the code that emitter describes as unwritten has since landed. Per this corpus's evidence-ranking rule that executable evidence outranks documentation for a claim about current behavior, this node treats the emitter as wired and records LIMITS.md's text as the drifted source rather than silently repeating it."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-conformance/LIMITS.md:41-48"
      - "crates/buzz-relay/src/handlers/req.rs:422"
      - "crates/buzz-relay/src/handlers/req.rs:750"
    confidence: 0.8
  - statement: "AppState's tracer field is documented 'Production binds NoopTracer' and its constructor sets tracer: Arc::new(crate::conformance::NoopTracer), and NoopTracer's own Tracer::record implementation is a no-op while enabled() returns false, so every trace step built by the write- and read-seam emitters above is discarded by default in production rather than reaching check_trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:760-765"
      - "crates/buzz-relay/src/state.rs:946"
      - "crates/buzz-conformance/src/lib.rs:341-352"
  - statement: "LIMITS.md's own 'CI command' section names the three test surfaces that currently gate every PR (buzz-conformance's 9 library tests, its 5 replay-fixture tests, and 2 EmitGuard coverage-breach tests in buzz-relay) and separately states that wiring a live relay's real traffic through check_trace via a recording tracer -- 'the integration replay' -- is 'the next ratchet', naming it as landing 'with the read-seam patch onto Max's req.rs work' rather than as already existing; a search of crates/buzz-test-client and crates/buzz-relay/tests for any use of JsonlTracer, check_trace, or the buzz_conformance crate found no matches."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:85-125"
      - "run_command('grep -rln \"JsonlTracer\\|check_trace\\|buzz_conformance\" crates/buzz-test-client/ crates/buzz-relay/tests/') -> no matches"
  - statement: "A second, narrower instance of cross-community non-interference is independently enforced today, outside the checker this node documents: crates/buzz-relay/src/audio/room.rs's AudioRoomManager keys its in-memory room registry on (CommunityId, channel Uuid), and its get_unambiguous_by_channel lookup fails closed (returns None) rather than picking one arbitrarily when the same channel UUID exists in two communities, per its own doc comment: 'If two active communities use the same channel UUID, routing would be ambiguous, so fail closed instead of delivering one community's audio to the other.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:222"
      - "crates/buzz-relay/src/audio/room.rs:591-620"
  - statement: "The unit test manager_isolates_same_channel_uuid_across_communities exercises exactly that: it creates rooms for the same channel UUID in two different communities, asserts they are distinct Arc instances with disjoint peer lists, and asserts get_unambiguous_by_channel returns None once the collision exists; running it (no #[ignore], no external infrastructure) passes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/audio/room.rs:805-840"
      - "run_command('cargo test -p buzz-relay --lib audio::room::tests::manager_isolates_same_channel_uuid_across_communities') -> running 1 test; test audio::room::tests::manager_isolates_same_channel_uuid_across_communities ... ok; test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 1080 filtered out"
  - statement: "crates/buzz-conformance/LIMITS.md states the harness is wired only at the ingest/auth/read accept-reject boundary in buzz-relay's handlers, that coverage is exactly the set of code paths exercised by a run that actually happened, and separately lists DB-layer leaks the read projection does not itself read, cross-pod leaks, time-bounded/concurrency properties, pubsub fan-out leaks, and a hypothetical future removal of CommunityId's client-input fence as things the gate does not catch even when it is fully wired and running."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:11-68"
  - statement: "architecture-principles-community-is-security-boundary and corpus-template-test-contract both resolve as ids on origin/launchpad's corpus tree at the recorded revision, alongside architecture-containers-relay, and no node exists there describing agent compute sandboxing specifically."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes architecture/principles/community-is-security-boundary.md and templates/test-contract.md; no agent-sandbox or compute-isolation node present"
  - statement: "Issue #1385's definition of done requires this node to name preconditions/context, action/event and observable expected outcome, to name negative/error cases when they are part of the contract, to link actual verification implementing the contract, and to not claim coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1385 definition of done"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Cross-community non-interference — test contract

## Purpose and boundary

"Isolation" in this repository could plausibly mean either of two things, and this node
investigated both before choosing one. **Tenant/community isolation** — that one
community's data is never observable from a different community's context — has a
formal specification (`docs/spec/MultiTenantRelay.tla`), a purpose-built independent
checker crate (`buzz-conformance`), and an unconditional, currently-passing unit test
that asserts a cross-community leak is rejected. **Agent compute isolation** — sandboxing
one agent's execution from another's, or from its host — was searched for across
`crates/buzz-agent`, `crates/buzz-acp`, and `crates/buzz-backend-kubernetes` and turned up
no comparable test: every "isolation"-named hit in those crates is either a database
transaction-isolation level, an MCP-startup process default unrelated to security, or a
model-id label-token parsing test (see this node's evidence ledger). This node therefore
covers **tenant/community non-interference only**, and specifically the one obligation
`buzz-conformance`'s replay checker enforces: that a trace step reporting a community
label other than the request's own resolved community is rejected, never silently
accepted. It does not restate the general architecture principle already stated at
`architecture-principles-community-is-security-boundary`, and it does not attempt to
cover the full per-surface table in `docs/multi-tenant-conformance.md`, which spans many
distinct obligations across many relay surfaces by design.

## Obligation

> A trace step recorded at the relay's ingest/auth/read seam whose reported per-row (or
> per-action) community label set includes any community other than the request's own
> server-resolved community MUST be rejected by the runtime conformance checker
> (`check_trace`) as a non-interference violation — never accepted as a conforming trace.

This is the "master" property `docs/spec/MultiTenantRelay.tla` calls `Inv_NonInterference`,
narrowed to the one thing this node can point at a specific, currently-passing negative
test for.

## Verifying test(s)

- `crates/buzz-conformance/src/checker.rs` — `checker::tests::cross_community_row_bites_non_interference`
  (lines 209–223). This is the negative case for the obligation: it builds a single
  `TraceAction::ReadMessageRows` step whose `row_communities` contains the request's
  resolved community *and* a second, unrelated community, and asserts
  `check_trace` returns `Err(TransitionError::NonInterference { .. })` rather than `Ok(())`.
  It is the only test in this repository, at this revision, that directly exercises the
  checker's rejection of a cross-community trace.

No other test in `checker.rs`'s own suite or in `crates/buzz-conformance/tests/replay_fixtures.rs`
covers this specific failure mode: the three committed replay fixtures cover a
positive trace (`good.jsonl`), a host/channel-fence skip (`bad_host_channel_mismatch.jsonl`
→ `IllegalTransition`), and a coverage breach (`bad_coverage_breach.jsonl` →
`CoverageBreach`) — none of the three is a `NonInterference` case.

## How to run it

```bash
cargo test -p buzz-conformance --lib checker::tests::cross_community_row_bites_non_interference
```

No gate to satisfy: the test is not `#[ignore]`d and needs no Postgres, Redis, or live
relay. `cargo test -p buzz-conformance --lib` (the whole library suite, 9 tests) was run
in full while authoring this node and passed unconditionally — see the evidence ledger
for the exact invocation and result.

## Current enforcement status

**Gated**, and the gate is specific enough to name precisely:

- **The rule itself is verified.** The checker's rejection of a cross-community trace is
  proven by an unconditional, currently-passing unit test with no external dependency
  (`cargo test -p buzz-conformance --lib` → 9 passed, 0 failed, including this case by
  name).
- **Whether that rule is ever applied to a real relay's live traffic is not yet
  established, and is the specific thing gating this obligation.** Production always
  binds `NoopTracer` (`crates/buzz-relay/src/state.rs:946`), which discards every trace
  step by design — this is a passive, observation-only conformance gate, not a runtime
  enforcement mechanism (see *Limits*). No test in this repository wires a live relay's
  real request handling through a recording tracer (`JsonlTracer`) and `check_trace`
  together; `crates/buzz-conformance/LIMITS.md` itself names that integration replay "the
  next ratchet," described as landing with future work rather than as already built.
- **One correction to `LIMITS.md`, found while authoring this node.** It currently states
  the read-seam emitter is a "held-back req.rs patch" and that "the read-seam half of the
  gate is not yet armed." That is stale at this node's recorded revision:
  `record_read_message_rows` and `record_read_by_id_rows` are already called from
  `crates/buzz-relay/src/handlers/req.rs` (lines 422 and 750), in a commit dated two
  months after `LIMITS.md`'s own last edit. This node follows this corpus's own rule that
  executable evidence outranks documentation for a current-behavior claim, and reports
  the drift rather than repeating the stale text as fact.

## Limits

- The verifying test proves the checker's logic is correct against the specific
  synthetic scenario it constructs (one step, two communities in one row-labels vector).
  It does not prove that any *live* relay execution has ever produced a trace — synthetic
  or real — that was actually replayed through `check_trace`; no such run exists in this
  repository yet (see *Current enforcement status*).
- Even once the integration replay LIMITS.md describes lands, `LIMITS.md`'s own "Scope"
  and "What it does NOT catch" sections state the harness is wired only at the
  ingest/auth/read seam in `buzz-relay`'s handlers, and by its own account cannot see: a
  leak introduced purely in DB/SQL filtering that the read projection never re-reads,
  Redis pub/sub fan-out to the wrong subscriber, a leak that only manifests across pods,
  or a future regression that silently added `From<Uuid>` to `CommunityId` and broke the
  client-input fence at the type level. These are named gaps in the underlying mechanism,
  not something this test-contract node's citations can independently rule out.
- `docs/spec/MultiTenantRelay.tla` grounds the checker's model, but whether that spec
  itself has been machine-checked by TLC at this revision was not established while
  authoring this node — `LIMITS.md` attributes spec correctness to TLC separately from
  the runtime gate, and this node did not independently reproduce that check.
- This node makes no claim about search, git object storage, presence, or any other
  surface named in `docs/multi-tenant-conformance.md`'s conformance table; the obligation
  above is scoped to whatever a `TraceAction` step can represent (write/auth/read at the
  ingest and REQ handlers), nothing wider.

## Scope and omissions

**This node covers** one obligation — that `buzz-conformance`'s replay checker rejects a
trace reporting a cross-community row label — its one directly negative unit test, that
test's current unconditional pass, and an honest account of how far production wiring
currently reaches (write-seam armed and observed by that test's model; read-seam code
present but not yet exercised end-to-end against a live relay; production tracer a no-op
by default).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The general architecture principle that a community is the security boundary | `architecture-principles-community-is-security-boundary` (referenced above, not restated) |
| The full per-surface conformance obligation table (search, git, presence, pub/sub key prefixing, audit labelling, and the rest) | `docs/multi-tenant-conformance.md` |
| `#[ignore]`-gated end-to-end isolation assertions over a real two-host relay deployment (`crates/buzz-test-client/tests/conformance_multitenant.rs`, e.g. `client_supplied_community_cannot_override_host`) | Out of scope for this node — a different verifying mechanism (a live two-host relay) for a related but distinct obligation at the HTTP/WebSocket protocol layer, not the trace-checker obligation documented here |
| A second, independently-enforced instance of cross-community non-interference in the audio/huddle room registry (`crates/buzz-relay/src/audio/room.rs`, test `manager_isolates_same_channel_uuid_across_communities`, currently passing unconditionally) | Not folded into this node per the one-obligation-per-node rule — it is enforced by a different mechanism (in-memory registry keying) than the trace checker this node documents, and would be its own test-contract node if one is written |
| Whether agent compute (sandboxing one agent's execution from another or from its host) has an isolation obligation and test at all | Not established here; the investigation in this node's *Purpose and boundary* section found no such test in the crates searched, but did not exhaustively audit every compute-provider crate |
| Building the live integration replay (`JsonlTracer` driving `check_trace` against a running relay's real e2e suite) | `crates/buzz-conformance/LIMITS.md`, described there as the next unbuilt step |
| Whether `docs/spec/MultiTenantRelay.tla` has been machine-checked by TLC at this revision | Not established here |

**Expected but not verified when this node was written:**

- Whether the read-seam emitter's wiring (confirmed present in source at
  `crates/buzz-relay/src/handlers/req.rs:422,750`) has itself been exercised by any test —
  unit, integration, or manual — beyond the narrow `record_read_message_rows`/
  `record_read_by_id_rows` unit tests already cited in `crates/buzz-relay/src/conformance/mod.rs`.
  This node did not trace every caller of the REQ handler to confirm the emit path is
  reached on a real subscription.
- Whether any corpus node describing `docs/multi-tenant-conformance.md`'s full obligation
  table, or `TenantContext` itself, exists or is planned; if one lands, it is a more
  on-topic `references` target for this node than the broader architecture-principle node
  currently declared.
