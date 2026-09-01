---
id: verification-formal-multi-tenant-relay
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
  - statement: "docs/spec/MultiTenantRelay.tla's own module doc-comment states its master proof obligation is NOT merely 'no row with the wrong community_id is returned' but non-interference encoded as a label/taint invariant: every state element and observation carries the community labels that influence it, and no value labeled outside a connection's resolved community may flow into that connection's typed observational interface."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:10-15"
  - statement: "The spec's top-level Safety property is the conjunction of TypeOK and twelve named invariants: Inv_NonInterference, Inv_LabelPropagation, Inv_ReadConfinement, Inv_ResolutionFence, Inv_HostBindingFence, Inv_ChannelCommunityImmutable, Inv_AdmissionFence, Inv_AcceptedWritesPersist, Inv_MessageKeyUnique, Inv_NoTenantContextFailsClosed, Inv_ProjectionDerived, and Inv_SanitizedErrors."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:1128-1141"
  - statement: "crates/buzz-conformance/TRACE_SCHEMA.md opens by calling itself 'the contract between the relay's emitter and the independent replay checker,' grounded in docs/spec/MultiTenantRelay.tla, and states that the relay emits one TraceStep per decision at the ingest/auth/read seam which the checker replays against a Rust re-implementation of the spec's Next relation, without calling any production reducer."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md:1-20"
  - statement: "crates/buzz-conformance/Cargo.toml declares dependencies on only serde, serde_json, thiserror and uuid, and a single dev-dependency on proptest -- no dependency on buzz-relay, buzz-db, buzz-auth, or any other production Buzz crate -- and its own comment block states this independence is deliberate so a bug in production type machinery or the production reducer cannot mechanically become a bug in the checker."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/Cargo.toml"
  - statement: "crates/buzz-conformance/src/transitions.rs re-implements the spec's Next relation independently: check_step enforces a universal state-match obligation (resolved_community, bound_host and actor must agree with the model bootstrapped from the trace's first step), row-label confinement for ReadMessageRows/ReadByIdRows/ReadHostFeedRows (every row_communities entry must equal the resolved community), an AuthCheck rule that an Allow verdict with a claimed_community different from the resolved community is an IllegalTransition (the M2/M8 bite), and treats any ImplBug action as a CoverageBreach."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:138-313"
  - statement: "crates/buzz-conformance/src/checker.rs's check_trace bootstraps its model from the first trace step, rejects an empty trace as a CoverageBreach, runs check_step on every subsequent step, and finally fails with a CoverageBreach naming any required_critical_actions kind that never appeared in the trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/checker.rs:60-132"
  - statement: "Running `cargo test -p buzz-conformance` at commit 473205a7457b208455f188847bfb27b01aa83cac reports three green test surfaces: 9 passed in the in-crate `checker::tests` module (`--lib`), 7 passed in `tests/proptest_checker.rs` (128 cases each), and 6 passed in `tests/replay_fixtures.rs` -- 22 tests total, 0 failed, 0 ignored."
    entry_class: FACT
    evidence:
      - "cargo_test(package=buzz-conformance, commit=473205a7457b208455f188847bfb27b01aa83cac) -> lib: 9 passed; tests/proptest_checker.rs: 7 passed; tests/replay_fixtures.rs: 6 passed; 0 failed across all three"
  - statement: "crates/buzz-conformance/LIMITS.md's own 'CI command' section states the replay-fixtures test surface has 5 tests ('Replay fixtures (5 tests)'), but crates/buzz-conformance/tests/replay_fixtures.rs defines 6 #[test] functions (good_trace_passes_check, bad_host_channel_mismatch_is_illegal_transition, coverage_breach_is_caught, foreign_row_leak_is_non_interference, empty_trace_is_coverage_breach, missing_required_action_is_coverage_breach), and the actual run above reports 6 passed, not 5 -- LIMITS.md's headcount has drifted from the file it describes."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:96"
      - "crates/buzz-conformance/tests/replay_fixtures.rs:237-324"
  - statement: "crates/buzz-conformance/LIMITS.md states the harness is wired only at the ingest/auth/read accept-reject boundary in crates/buzz-relay/src/handlers/{ingest,req,event}.rs, that coverage breach can only fire on paths the harness was armed on, and that a new endpoint bypassing EmitGuard::arm is enforced by code review rather than by the harness itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:13-37"
  - statement: "crates/buzz-relay/src/conformance/mod.rs's own module doc-comment, and crates/buzz-conformance/TRACE_SCHEMA.md's 'Where the emitter lives' table, both describe the req.rs/event.rs read-seam emitter as 'held back' -- an additive patch not yet applied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs:25-32"
      - "crates/buzz-conformance/TRACE_SCHEMA.md:130-138"
  - statement: "At the recorded revision, crates/buzz-relay/src/handlers/req.rs itself calls crate::conformance::record_req_authcheck, crate::conformance::record_read_message_rows, and crate::conformance::record_read_by_id_rows -- i.e. the read-seam emitter the module doc-comment and TRACE_SCHEMA.md describe as held back is, in the actual code at this revision, already wired at three call sites."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:162"
      - "crates/buzz-relay/src/handlers/req.rs:422"
      - "crates/buzz-relay/src/handlers/req.rs:750"
  - statement: "Because req.rs's own code already calls the read-seam emitter helpers, conformance/mod.rs's module doc-comment and TRACE_SCHEMA.md's emitter-location table are stale on this specific point at the recorded revision: per this corpus's evidence standard, executable code outranks documentation for a claim about how the system currently behaves, so the wiring is best described as landed rather than held back, even though neither document has been updated to say so."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:162"
      - "crates/buzz-relay/src/handlers/req.rs:422"
      - "crates/buzz-relay/src/handlers/req.rs:750"
      - "crates/buzz-relay/src/conformance/mod.rs:25-32"
      - "crates/buzz-conformance/TRACE_SCHEMA.md:130-138"
    confidence: 0.8
  - statement: "A repository-wide search for check_trace and JsonlTracer outside crates/buzz-conformance/ finds only crates/buzz-relay/src/conformance/mod.rs, crates/buzz-relay/src/conformance/tracers.rs, and a doc-comment on the AppState.tracer field in crates/buzz-relay/src/state.rs; no test file anywhere in the workspace constructs a JsonlTracer against a running or mocked relay and asserts the result with check_trace, so the wiring in req.rs and ingest.rs is exercised only by AppState's production NoopTracer plus the relay's own request-handling tests, not by any automated conformance replay."
    entry_class: FACT
    evidence:
      - "grep(pattern='JsonlTracer|check_trace', scope='crates/buzz-relay/,crates/buzz-test-client/') -> crates/buzz-relay/src/conformance/mod.rs, crates/buzz-relay/src/conformance/tracers.rs, crates/buzz-relay/src/state.rs (doc-comment only); no match in crates/buzz-test-client/"
  - statement: "LIMITS.md itself names this gap as the next step, stating verbatim: 'The integration replay is the next ratchet -- once the read-seam emitter lands on Eva's integration branch the harness will drive the existing e2e suite with a JsonlTracer per request and assert check_trace for every captured trace.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:122-125"
  - statement: "LIMITS.md states plainly that the runtime conformance harness 'is not a proof': it says only that for the executions that actually ran with tracing on, the relay's traced decisions matched a trace the spec accepts, and that spec correctness itself is 'the proof obligation of docs/spec/MultiTenantRelay.tla, machine-checked by TLC' -- i.e. if the spec itself is wrong, both the spec and the Rust checker that re-implements it pass together."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:1-9"
      - "crates/buzz-conformance/LIMITS.md:70-72"
  - statement: "No workflow file under .github/workflows/ references MultiTenantRelay or tlc2.TLC, and docs/spec/MultiTenantRelay.cfg's own header comment gives the TLC invocation ('java -cp ~/.buzz/.scratch/tla2tools.jar tlc2.TLC -config MultiTenantRelay.cfg MultiTenantRelay.tla') as a command for a person to run by hand, not as a script any CI job invokes -- so the spec's own Safety property is not re-model-checked on every commit; only the Rust re-implementation in crates/buzz-conformance is continuously tested."
    entry_class: FACT
    evidence:
      - "grep(pattern='MultiTenantRelay|tlc2.TLC|tla2tools', scope='.github/workflows/') -> no matches"
      - "docs/spec/MultiTenantRelay.cfg:1-3"
  - statement: "The Justfile's test-unit recipe runs `cargo nextest run -p buzz-conformance`, commented as 'the independent replay checker + golden fixtures. No infra -- pure in-process trace replay', and .github/workflows/ci.yml's unit-tests job runs `just test-unit` whenever the job's own changes-detection step reports a change under crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock or rust-toolchain.toml (which any change to buzz-conformance itself satisfies), or on any push event; so the checker's own 22 tests are a required, ungated CI gate for any PR that actually touches this crate, not merely an opt-in or #[ignore]d suite -- though the job is not unconditional for a PR that touches nothing in that path set."
    entry_class: FACT
    evidence:
      - "Justfile:339-343"
      - ".github/workflows/ci.yml:125-134"
      - ".github/workflows/ci.yml:146"
      - ".github/workflows/ci.yml:38-47"
  - statement: "Issue #1371's definition of done requires this node's obligation be stated as one precise testable sentence, its verifying test(s) named exactly with file path and test/module name, a copy-pasteable run command, an honestly-stated enforcement status (verified/gated/pending), and a limits section naming what the verifying test does and does not prove."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1371 definition of done, and launchpad/docs/corpus/templates/test-contract.md's Required sections"
  - statement: "Issue #1371 scopes this node to the formal (TLA+ / model-checked) specification of multi-tenant relay behavior and its independent Rust checker, explicitly distinct from #1370's auth-specific conformance-table scope (docs/multi-tenant-conformance.md paired with crates/buzz-test-client/tests/conformance_multitenant.rs)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1371 task brief, compared against launchpad-26/buzz#1370's scope"
  - statement: "At the recorded revision, origin/launchpad's corpus tree carries no node under launchpad/docs/corpus/verification/, so this is the first verification-type node in the corpus; architecture-principles-fail-closed-boundaries is loadable from origin/launchpad and already cites docs/spec/MultiTenantRelay.tla's Inv_HostBindingFence, Inv_ResolutionFence and Inv_NoTenantContextFailsClosed, plus crates/buzz-relay/src/conformance/mod.rs's EmitGuard, as the formal and runtime verification of the same host-binding invariant this node documents the test contract for."
    entry_class: FACT
    evidence:
      - "git.ls_tree('origin/launchpad', 'launchpad/docs/corpus') -> no verification/ subtree; architecture/principles/fail-closed-boundaries.md present"
      - "launchpad/docs/corpus/architecture/principles/fail-closed-boundaries.md"
  - statement: "LIMITS.md's own CI command section states the EmitGuard coverage-breach self-test surface in crates/buzz-relay/src/conformance/mod.rs has 2 tests, but a count of #[test] attributes in that file at the recorded revision finds 10: counting_tracer_delegates_enabled_to_inner, emit_guard_drop_is_silent_when_an_emit_reached_the_tracer, emit_guard_drop_records_exactly_one_impl_bug_when_no_emit, record_req_authcheck_emits_allow_with_none_claim_when_member, record_req_authcheck_emits_deny_when_not_member, project_row_communities_channelless_uses_resolved, project_row_communities_channel_scoped_uses_lookup_label, project_row_communities_channel_scoped_missing_is_breach, record_read_message_rows_missing_lookup_emits_impl_bug, and record_read_by_id_rows_ok_emits_read_by_id_rows -- this module has grown well past the 2-test EmitGuard self-test LIMITS.md still describes, mirroring the same held-back-emitter drift recorded above."
    entry_class: FACT
    evidence:
      - "grep(pattern='#\\[test\\]', scope='crates/buzz-relay/src/conformance/mod.rs') -> 10 matches"
      - "crates/buzz-conformance/LIMITS.md:110-113"
relationships:
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: implements
    target: corpus-template-test-contract
---

# Multi-tenant relay formal specification — test contract

## Purpose and boundary

This node documents one obligation: that `buzz-conformance`'s independent
replay checker (`check_trace`) correctly accepts or rejects a recorded
`TraceStep` sequence according to `docs/spec/MultiTenantRelay.tla`'s `Next`
transition relation and its `Safety` invariants. It covers the **formal
specification + independent-checker pairing** only — the TLA+ model, the
Rust re-implementation of its transition relation, and the tests that widen
and pin that re-implementation's correctness.

This is deliberately **not** the same subject as issue #1370's scope.
#1370 documents `docs/multi-tenant-conformance.md`'s per-surface obligation
table paired with `crates/buzz-test-client/tests/conformance_multitenant.rs`
— a migration checklist expressed as prose rows and one Rust module per row,
gated `#[ignore]` per not-yet-landed obligation. This node's subject is a
different pairing entirely: a machine-checkable formal model
(`MultiTenantRelay.tla`) and a from-scratch Rust re-implementation of its
transition relation (`buzz-conformance`) that a runtime trace is replayed
against. The two pairings share a domain (multi-tenant isolation) but are
independently maintainable artifacts with different verifying tests, per
`launchpad/docs/corpus/AGENTS.md`'s one-node-one-idea rule.

## Obligation

> A `TraceStep` sequence recorded at the relay's ingest/auth/read seam is
> accepted by `buzz_conformance::checker::check_trace` if and only if it is
> consistent with `docs/spec/MultiTenantRelay.tla`'s `Next` transition
> relation and its `Safety` invariants: no row's community label may differ
> from the request's resolved community (`Inv_NonInterference` /
> `Inv_ReadConfinement`), no `AuthCheck` verdict of `Allow` may carry a
> claimed community different from the resolved community
> (`Inv_HostBindingFence` / `Inv_ResolutionFence`, the M2/M8 mutation
> target), the request's `resolved_community`/`bound_host`/`actor` may not
> change mid-trace, and no critical seam may exit without emitting a
> recognized action (`TraceAction::ImplBug` is always a coverage breach).

## Verifying test(s)

- `crates/buzz-conformance/src/checker.rs` — `checker::tests` module (9
  tests, `#[cfg(test)]` in-crate). Exercises `check_trace` directly against
  hand-built traces for every `TransitionError` variant: an empty trace,
  a clean write-then-read trace, a foreign row label (`NonInterference`),
  an `AuthCheck` Allow with a foreign claim (`IllegalTransition`, the M2
  bite), a Deny with a foreign claim (must pass), a mid-trace state flip
  (`StateMismatch`), an `ImplBug` step and a missing required action (both
  `CoverageBreach`), and a `SanitizedError` alone (must pass).
- `crates/buzz-conformance/tests/proptest_checker.rs` — 7 property tests
  (128 generated cases each, per `#![proptest_config(ProptestConfig::with_cases(128))]`),
  asserting spec-derived facts about `check_trace`'s behaviour rather than
  re-deriving a parallel oracle: a fully clean trace is always accepted
  (`clean_trace_is_accepted`), any read carrying a foreign row label is
  always rejected (`foreign_row_label_is_rejected`), `AuthCheck` Allow with
  a foreign claim always bites (`auth_allow_foreign_claim_bites`), Deny with
  any claim is always in-spec (`auth_deny_any_claim_is_ok`), `ImplBug`
  always bites (`impl_bug_bites_coverage_breach`), a mid-trace field flip
  always bites `StateMismatch` (`state_flip_bites_state_mismatch`), and
  `check_trace` is deterministic and never panics
  (`check_trace_is_deterministic_and_total`).
- `crates/buzz-conformance/tests/replay_fixtures.rs` — 6 tests. Three JSONL
  fixtures under `crates/buzz-conformance/tests/fixtures/` (`good.jsonl`,
  `bad_host_channel_mismatch.jsonl`, `bad_coverage_breach.jsonl`, plus a
  fourth, `bad_foreign_row_leak.jsonl`, covering a fourth scenario) are
  each round-tripped — built from typed Rust, asserted byte-identical to
  the committed file, then replayed through `check_trace` — so a
  schema-change PR that does not update the committed fixture fails loudly
  rather than silently drifting. `good_trace_passes_check` expects `Ok(())`;
  `bad_host_channel_mismatch_is_illegal_transition`,
  `coverage_breach_is_caught` and `foreign_row_leak_is_non_interference`
  each expect a specific `TransitionError` variant;
  `empty_trace_is_coverage_breach` and
  `missing_required_action_is_coverage_breach` cover the two coverage-breach
  paths independently of any fixture file.

## How to run it

```bash
# All three surfaces together (22 tests):
cargo test -p buzz-conformance

# Individually:
cargo test -p buzz-conformance --lib                    # 9 tests
cargo test -p buzz-conformance --test proptest_checker   # 7 tests
cargo test -p buzz-conformance --test replay_fixtures    # 6 tests

# To intentionally refresh a fixture after a deliberate schema change:
BUZZ_CONFORMANCE_UPDATE=1 cargo test -p buzz-conformance --test replay_fixtures

# What CI actually runs (no test-specific flag or #[ignore] gate):
cargo nextest run -p buzz-conformance
```

No infrastructure (Postgres, Redis, a running relay) is required — every
test constructs `TraceStep` values in-process and calls `check_trace`
directly or through the fixture round-trip. None of the three surfaces is
`#[ignore]`d.

## Current enforcement status

**Verified**, for the scope stated in the obligation above: `cargo nextest
run -p buzz-conformance` runs unconditionally inside the `Justfile`'s
`test-unit` recipe, and `.github/workflows/ci.yml`'s `unit-tests` job runs
`just test-unit` whenever its `changes` job detects a diff under
`crates/**` (among other Rust-wide paths) or on a push event -- so any PR
that touches `buzz-conformance` itself runs this gate with no opt-out, and
every push to the default branch runs it regardless. It is not literally
gated on "every PR" irrespective of what that PR changes. At commit
`473205a7457b208455f188847bfb27b01aa83cac` all 22 tests across the three
surfaces above pass (verified by running `cargo test -p buzz-conformance`
directly while authoring this node).

**This status covers the checker's own conformance logic, not the live
relay's emitted output.** `check_trace`'s obligation is fully exercised by
hand-built fixtures and generated property-test traces, and demonstrably
enforced in CI. Whether the relay's actual, currently-wired emit call sites
(`crates/buzz-relay/src/handlers/ingest.rs` and, per this node's own
finding, `req.rs` as well) produce traces that would in turn pass
`check_trace` under real traffic is a **separate, currently unverified**
claim: no test in the workspace constructs a `JsonlTracer`, drives it
through a running or mocked relay, and asserts the captured trace with
`check_trace`. `LIMITS.md` names this integration replay as "the next
ratchet," not yet landed. See *Limits* below.

## Limits

Quoting `crates/buzz-conformance/LIMITS.md` verbatim, because this is the
crate's own stated boundary and this node does not relax it: *"The runtime
conformance harness is not a proof. It says only this: for the executions
that actually ran with tracing on, the relay's ingest/auth/read decisions
matched a trace the spec accepts. Coverage is exactly the set of code paths
exercised — no more, no less."*

What a green run of this obligation's verifying tests does and does not
establish:

- **Proves:** `check_trace`'s Rust re-implementation of the spec's `Next`
  relation correctly accepts every hand-built and property-generated
  in-spec trace, and correctly rejects every trace built to violate
  non-interference, host/claim agreement, mid-request state consistency, or
  seam coverage — across the input space the 9 unit tests, 7 property tests
  (128 cases each) and 6 fixture tests actually exercise.
- **Does not prove the spec itself is correct.** `LIMITS.md` states this
  directly: "the checker re-implements the spec; if the spec is wrong, both
  pass." `docs/spec/MultiTenantRelay.tla`'s own `Safety` property is
  intended to be machine-checked by TLC (the model-check command is
  documented in `docs/spec/MultiTenantRelay.cfg`'s header comment), but no
  CI workflow in this repository invokes TLC — this node's own search of
  `.github/workflows/` found no reference to `MultiTenantRelay` or
  `tlc2.TLC`. A regression in the spec's `Safety` conjunction (for example,
  a mutation like the thirteen M1–M13 mutations the spec's own header
  comment documents as "Confirmed red") is only caught if a person re-runs
  TLC by hand; nothing re-runs it automatically per commit.
- **Does not prove the live relay's traces conform.** As this node's own
  evidence ledger records, `req.rs` already calls the read-seam emitter
  helpers that `TRACE_SCHEMA.md` and `conformance/mod.rs`'s own
  module doc-comment still describe as "held back" — but no automated test
  anywhere feeds the relay's actual emitted output (via `JsonlTracer` or
  otherwise) through `check_trace`. Coverage breach can only fire on paths
  the harness was armed on in the first place; a new endpoint that bypasses
  `EmitGuard::arm` is, per `LIMITS.md`, caught by code review, not by this
  gate.
- **Does not cover cross-pod, timing, or pubsub-fanout leaks.** `LIMITS.md`
  explicitly places multi-pod replay leaks, timing/concurrency bugs, and
  pub/sub fan-out leaks outside this gate's scope, since the harness traces
  one process's ingest/auth/read seam only.
- **Does not cover the DB-layer leaks the projection never reads.**
  `LIMITS.md` names the design of `row_community` labelling for the
  read-seam projection as still under review ("Eva's review call before
  fixtures land" for the per-row lookup versus uniform-label choice); a
  leak the projection's own lookup never observes cannot appear as a
  foreign label in the trace.

## Scope and omissions

**This node covers** the `docs/spec/MultiTenantRelay.tla` formal model, the
`buzz-conformance` crate's independent re-implementation of its `Next`
relation and replay checker, and the three test surfaces
(`checker::tests`, `proptest_checker.rs`, `replay_fixtures.rs`) that verify
`check_trace`'s own correctness. It states, as an explicit finding rather
than folding it silently into the obligation, that the relay-side wiring
(`req.rs`, `ingest.rs`) is more complete than two of the crate's own
documents (`TRACE_SCHEMA.md`, `conformance/mod.rs`'s module doc-comment)
currently say, and that no automated test yet closes the loop from a live
relay's traced output back through `check_trace`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The per-surface conformance table and its executable form | #1370 (`docs/multi-tenant-conformance.md` / `conformance_multitenant.rs`) |
| The `crates/buzz-relay/src/conformance/mod.rs` `EmitGuard` coverage-breach self-test (10 tests at the recorded revision, not the 2 `LIMITS.md`'s CI-command section currently states) and the relay-side emitter's own correctness | A future test-contract or component node scoped to `buzz-relay`'s emitter, not this one |
| Whether `docs/spec/MultiTenantRelay.tla` still model-checks clean under TLC at the recorded revision | Not established here — TLC was not re-run while authoring this node; see *Limits* |
| The live-relay-to-`check_trace` integration replay `LIMITS.md` calls "the next ratchet" | Unlanded; no issue number found in the files read for this node |
| Updating `TRACE_SCHEMA.md`'s emitter-location table and `conformance/mod.rs`'s module doc-comment to reflect that `req.rs` is already wired | Not this node's job to fix; recorded here as a finding under `AGENTS.md`'s evidence-standard ranking (code outranks stale docs for current behaviour) |

**Expected but not verified when this node was written:**

- **TLC was not re-run against `docs/spec/MultiTenantRelay.tla`.** Whether
  the model still model-checks the `Safety` property clean at the recorded
  revision, and whether the thirteen documented mutations (M1–M13) still
  reproduce their stated counterexamples, was not re-verified — only the
  spec file's own text was read.
- **`crates/buzz-relay/src/conformance/mod.rs`'s 10 `#[test]` functions
  were counted but not executed as part of authoring this node.** Whether
  they currently pass is not asserted above; only their existence and
  count (contradicting `LIMITS.md`'s stated "2 tests") is recorded as a
  FACT.
- **Whether an issue already exists tracking the live-relay integration
  replay `LIMITS.md` names as "the next ratchet" was not searched for.**
  This node names the gap from `LIMITS.md`'s own text rather than from a
  linked issue.
