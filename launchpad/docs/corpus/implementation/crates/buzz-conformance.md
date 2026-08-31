---
id: implementation-crates-buzz-conformance
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-conformance's own package description is 'Runtime trace schema + independent replay checker for MultiTenantRelay.tla', and its Cargo.toml carries an explicit 'Independence rule' comment: depend on NO production buzz crate (buzz-db, buzz-relay, buzz-pubsub, buzz-auth, buzz-search, buzz-audit are named explicitly as forbidden), because the checker re-implements the spec transition relation from scratch so a bug in production code cannot mechanically become a bug in the checker."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/Cargo.toml"
  - statement: "The crate's dependency list is limited to serde, serde_json, thiserror and uuid (plus proptest as a dev-dependency for property tests only), confirming no production-crate dependency exists in either the main or dev-dependency sections."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/Cargo.toml"
  - statement: "src/lib.rs's crate-level doc states the crate is the schema (TraceStep, TraceAction, AbstractState) the relay emits at its ingest/read accept-reject boundary, plus an independent replay checker (check_trace) that validates a sequence of TraceSteps against the TLA+ spec's Next transition relation without calling any production reducer; and states explicitly what it is NOT -- a proof (only checks executions that ran) and not a re-export of production helpers."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:1-36"
  - statement: "CommunityLabel, OpaqueId, HostLabel, ChannelLabel and ActorLabel are opaque newtypes carried by the trace schema; CommunityLabel deliberately does not reuse buzz_core::CommunityId, both to preserve buzz-core's own no-Serde/no-From<Uuid> fence on CommunityId and to keep the checker's type machinery independent of production types that could launder a bug into it."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:44-112"
  - statement: "TraceAction is a closed enum with nine variants -- WriteInsert, WriteInsertGlobal, WriteDuplicate, SanitizedError, AuthCheck, ReadMessageRows, ReadByIdRows, ReadHostFeedRows, and ImplBug (the coverage-breach witness) -- and every variant's is_critical() returns true unconditionally, which is what makes the coverage-breach mode non-vacuous."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:177-286"
  - statement: "The Tracer trait is the only surface production code touches (record() plus an enabled() gate defaulting to true), and NoopTracer is the zero-cost production default whose enabled() returns false so hot-path emitters can skip building emit inputs entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:312-354"
  - statement: "checker::check_trace runs four stages against a Scenario (trace plus a set of required_critical_actions): reject an empty trace as a coverage breach; check each step's schema_version equals SCHEMA_VERSION; run transitions::check_step per step, stopping at the first failure (fail-closed); and after all steps pass, fail as a coverage breach if any declared required_critical_actions kind never appeared in the trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/checker.rs:60-132"
  - statement: "checker.rs carries 9 in-crate unit tests (counted directly: 13 fn items minus 4 non-#[test] helper functions), covering: empty-trace coverage breach, a full write+read pass case, a cross-community row biting NonInterference, an AuthCheck Allow with a foreign claim biting IllegalTransition (M2), the symmetric Deny-with-foreign-claim case passing, a mid-trace resolved_community/host change biting StateMismatch, an ImplBug step biting CoverageBreach, a scenario-required action that never appeared biting CoverageBreach by name, and all three SanitizedReason variants passing alone as well-formed."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/checker.rs:134-337"
  - statement: "transitions.rs is described in its own module doc as an independent translation of docs/spec/MultiTenantRelay.tla's Next transition relation into Rust, reading only the trace schema in `crate` and the spec text, explicitly not importing buzz-relay, buzz-db, buzz-auth or any other production crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:1-44"
  - statement: "check_step enforces three universal obligations per step (resolved_community, bound_host and actor from state_after must all agree with the model bootstrapped from the first trace step) before applying action-specific spec obligations, and returns TransitionError::StateMismatch on any of the three universal checks failing."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:129-166"
  - statement: "TransitionError is a 4-variant closed enum -- IllegalTransition, StateMismatch, NonInterference, CoverageBreach -- each carrying a step_index (except CoverageBreach, which is trace-level) and a human-readable detail string."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/transitions.rs:58-100"
  - statement: "docs/spec/MultiTenantRelay.tla defines WriteInsert at line 514, WriteInsertGlobal at line 559, WriteDuplicate at line 606, ReadMessageRows at line 643, ReadByIdRows at line 681, ReadHostFeedRows at line 703, SanitizedError at line 778, AuthCheck at line 794, the Next relation at line 933, Inv_NonInterference at line 985, and Inv_ReadConfinement at line 999 -- confirmed by grepping the spec file directly, not merely reading TRACE_SCHEMA.md's own citation of these numbers."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:514"
      - "docs/spec/MultiTenantRelay.tla:559"
      - "docs/spec/MultiTenantRelay.tla:606"
      - "docs/spec/MultiTenantRelay.tla:643"
      - "docs/spec/MultiTenantRelay.tla:681"
      - "docs/spec/MultiTenantRelay.tla:703"
      - "docs/spec/MultiTenantRelay.tla:778"
      - "docs/spec/MultiTenantRelay.tla:794"
      - "docs/spec/MultiTenantRelay.tla:933"
      - "docs/spec/MultiTenantRelay.tla:985"
      - "docs/spec/MultiTenantRelay.tla:999"
  - statement: "tests/replay_fixtures.rs round-trips three committed JSONL fixtures (good.jsonl, bad_host_channel_mismatch.jsonl, bad_coverage_breach.jsonl) plus a fourth trace built but not committed as a named JSONL file (bad_foreign_row_leak_trace, still asserted via assert_fixture_matches against bad_foreign_row_leak.jsonl) through check_trace, asserting good.jsonl returns Ok, bad_host_channel_mismatch.jsonl returns IllegalTransition, bad_coverage_breach.jsonl returns CoverageBreach, and bad_foreign_row_leak.jsonl returns NonInterference; each fixture is reconstructed from typed Rust builders and asserted byte-identical to the committed file before being replayed, so a schema change cannot silently desync the committed JSONL from what the relay actually emits."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/tests/replay_fixtures.rs"
      - "crates/buzz-conformance/tests/fixtures/good.jsonl"
      - "crates/buzz-conformance/tests/fixtures/bad_host_channel_mismatch.jsonl"
      - "crates/buzz-conformance/tests/fixtures/bad_coverage_breach.jsonl"
      - "crates/buzz-conformance/tests/fixtures/bad_foreign_row_leak.jsonl"
  - statement: "tests/proptest_checker.rs states its own design rule explicitly: it does NOT re-implement transitions::check_step as a parallel oracle (that would test the code against itself and prove nothing), and instead asserts spec-derived facts about check_trace's result read off the shape of the generated trace -- e.g. any read carrying a foreign row label MUST be rejected, a fully clean trace MUST be accepted, the checker never panics and is deterministic -- touching only the public checker::check_trace surface and never a production crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/tests/proptest_checker.rs:1-33"
  - statement: "LIMITS.md states the harness is 'not a proof' -- it only says that for executions that ran with tracing on, the relay's ingest/read decisions matched a trace the spec accepts -- and is wired only at the ingest/auth/read accept-reject boundary in crates/buzz-relay/src/handlers/{ingest,req,event}.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:1-26"
  - statement: "LIMITS.md names five things the gate does NOT catch: DB-layer leaks the read projection doesn't itself read (the read-seam half of the gate is explicitly 'not yet armed' pending a design decision); cross-pod leaks (the harness traces one process only); time-bounded/concurrency properties (the spec and gate are both untimed); pubsub fan-out (not a spec action; a fan-out leak surfaces in the receiver's own trace, not the publisher's); and type-level fence violations such as CommunityId gaining From<Uuid> (enforced by the Rust compiler, not this gate)."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:39-68"
  - statement: "LIMITS.md's CI command section requires three test surfaces to stay green on every PR: `cargo test -p buzz-conformance --lib` (LIMITS.md's own comment says 9 schema/checker unit tests), `cargo test -p buzz-conformance --test replay_fixtures` (LIMITS.md's own comment says 5 replay-fixture tests), and `cargo test -p buzz-relay --lib conformance::` (LIMITS.md's own comment says 2 EmitGuard coverage-breach self-tests) -- LIMITS.md sums these as 16 tests total -- and states the integration replay (live relay -> JsonlTracer -> check_trace) is the next ratchet, not yet landed."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:85-126"
  - statement: "Counted directly against the current source rather than trusting LIMITS.md's own comment: `crates/buzz-conformance/src/checker.rs`'s `#[cfg(test)] mod tests` carries exactly 9 `#[test]` functions (matching LIMITS.md); `crates/buzz-conformance/tests/replay_fixtures.rs` carries 6 `#[test]` functions, not 5 -- `foreign_row_leak_is_non_interference` and `missing_required_action_is_coverage_breach` both exist in the file today; and `crates/buzz-relay/src/conformance/mod.rs`'s `#[cfg(test)] mod tests` (matched in full by the `conformance::` substring filter in LIMITS.md's own CI command) carries 10 `#[test]` functions, not 2 -- LIMITS.md's '2' names only the two EmitGuard-Drop-specific self-tests (`emit_guard_drop_is_silent_when_an_emit_reached_the_tracer`, `emit_guard_drop_records_exactly_one_impl_bug_when_no_emit`) and does not account for the other 8 tests in the same module (`counting_tracer_delegates_enabled_to_inner`, two `record_req_authcheck_*` tests, three `project_row_communities_*` tests, and two `record_read_*_rows_*` tests) that the literal command it prescribes also runs. The actual count for the three commands as written is 9 + 6 + 10 = 25, not the 16 LIMITS.md sums."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/checker.rs:164-337"
      - "crates/buzz-conformance/tests/replay_fixtures.rs:237-324"
      - "crates/buzz-relay/src/conformance/mod.rs:441-780"
  - statement: "The Justfile's unit-test job runs `cargo nextest run -p buzz-conformance` (all targets, not just --lib) with an inline comment stating this is the multi-tenant conformance gate, that it needs no infra because it is pure in-process trace replay, and that it belongs in the unit job."
    entry_class: FACT
    evidence:
      - "Justfile:339-343"
  - statement: "buzz-relay's own Cargo.toml declares `buzz-conformance = { workspace = true }` as a dependency, and buzz-relay's crate-level lib.rs doc names its `conformance` module as the runtime conformance harness -- abstract trace emission at the ingest/read accept-reject boundary, replayed against docs/spec/MultiTenantRelay.tla by the independent buzz-conformance checker."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:20"
      - "crates/buzz-relay/src/lib.rs:14-18"
  - statement: "crates/buzz-relay/src/conformance/mod.rs hosts the emitter-side helpers that translate the relay's real decisions into TraceSteps: state_for_request (builds AbstractState from a TenantContext and authenticated pubkey), claimed_community_from_event (extracts the client-claimed community from an event's h tag, never trusted for resolution), emit/step helpers, record_req_authcheck for the REQ-path membership decision, project_row_community and RowCommunityProjection (the (B)-strategy per-row community lookup guard-rail that fails closed to ImplBug on a missing lookup rather than silently defaulting to the resolved community), an EmitGuard whose Drop records ImplBug if a critical seam exits without an emit, and sanitized_reason_for mapping IngestError variants onto the closed SanitizedReason alphabet."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs:1-220"
      - "crates/buzz-relay/src/conformance/mod.rs:344"
      - "crates/buzz-relay/src/conformance/mod.rs:385"
      - "crates/buzz-relay/src/conformance/mod.rs:413"
      - "crates/buzz-relay/src/conformance/mod.rs:432"
  - statement: "TRACE_SCHEMA.md's own 'Where the emitter lives' table states the req.rs/event.rs read-seam emitter is 'held back' as an additive patch pending integration, and its 'Where the checker lives' table names src/lib.rs (schema + Tracer trait), src/transitions.rs (spec Next re-implementation) and src/checker.rs (replay engine) as the checker's three files."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md:130-145"
  - statement: "buzz-conformance was introduced by PR #1321 ('Multi-tenant Buzz relay: community_id as a server-resolved key (comprehensive rewrite)') and has one subsequent touching commit, PR #4647 ('perf(relay): index channel-id lookups and skip trace-only reads'), per `git log --oneline -- crates/buzz-conformance`."
    entry_class: FACT
    evidence:
      - "git_log(path='crates/buzz-conformance') -> 14fba21e5 (#1321), bc9e6528a (#4647)"
  - statement: "launchpad/docs/corpus/architecture/flows/event-ingestion.md (id architecture-flows-event-ingestion) already documents the same conformance-tracer wiring this node describes -- the outer ingest_event wrapper arming an EmitGuard, the AuthCheck verdict recording claimed-vs-resolved community, and the ImplBug coverage-breach guarantee -- citing crates/buzz-relay/src/conformance/mod.rs directly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
  - statement: "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md (id architecture-principles-community-is-security-boundary) documents the same host-derived-community invariant this crate's checker enforces, citing docs/multi-tenant-conformance.md and the separate, currently #[ignore]-gated A/B isolation suite crates/buzz-test-client/tests/conformance_multitenant.rs as the repository's other (black-box, not trace-replay) conformance mechanism for the same invariant."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "docs/multi-tenant-conformance.md's 'Row zero' section states the same host-binding contract in prose -- req.community = resolve_host(connection.host), bound before any request handler observes tenant data, with unmapped hosts failing closed and NIP-98/token community stamps never overriding the host-derived community -- that buzz-conformance's AuthCheck / WriteInsert / WriteInsertGlobal transition rules encode mechanically."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:1-36"
  - statement: "No corpus node currently exists for docs/spec/MultiTenantRelay.tla itself, checked by grepping every id in the corpus tree at origin/launchpad; per AGENTS.md step 9 and the implementation-reference template's own Target guidance, this means no `implements` edge can be declared toward it without producing a hard validation error, so the spec is named by its repository path in the Target section instead."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no node documents docs/spec/MultiTenantRelay.tla"
  - statement: "The corpus node.schema.json's type enum includes both `implementation` and `verification`; choosing `verification` for this node rather than `implementation` reflects that the crate's entire reason for existing is checking runtime behavior against a formal spec (a verification apparatus) rather than realizing product-facing behavior, which is the distinction the implementation-reference template's 'A note on type' section explicitly allows an author to weigh."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/implementation-reference.md"
      - "crates/buzz-conformance/src/lib.rs:1-36"
    confidence: 0.75
---

# buzz-conformance: implementation reference

`crates/buzz-conformance` is the trace schema plus independent replay checker that verifies the
Buzz relay's tenant-boundary decisions conform to `docs/spec/MultiTenantRelay.tla`'s `Next`
transition relation. It does not implement product behavior; it realizes a **verification
mechanism** for a specific invariant class (multi-tenant non-interference) that the relay's
production request-handling code is separately responsible for upholding. The crate ships a
closed `TraceAction` vocabulary, a `Tracer` trait the relay's request handlers call at the
ingest/auth/read boundary, and a `check_trace` replay engine that fails closed on illegal
transitions, state mismatches, cross-tenant row leaks, and missing trace coverage.

## Target

The realized target is `docs/spec/MultiTenantRelay.tla`, the TLA+ formal model of Buzz's
multi-tenant relay/database isolation (opened directly at this revision; 1142 lines). Its stated
proof obligation is non-interference: "no value labeled outside a connection's resolved community
may flow into that connection's typed observational interface." `buzz-conformance`'s
`transitions::check_step` re-implements the relevant fragment of the spec's `Next` action
vocabulary in Rust — `WriteInsert` (line 514), `WriteInsertGlobal` (line 559), `WriteDuplicate`
(line 606), `ReadMessageRows` (line 643), `ReadByIdRows` (line 681), `ReadHostFeedRows` (line 703),
`SanitizedError` (line 778), and `AuthCheck` (line 794) — and checks traced runtime observations
against `Inv_NonInterference` (line 985) and `Inv_ReadConfinement` (line 999).

**The spec has no corpus node id yet.** `docs/spec/MultiTenantRelay.tla` is not itself a document
under `launchpad/docs/corpus/`, so this node declares no `implements` edge toward it — per
`AGENTS.md`'s creation rule, an edge to a nonexistent id is a hard validation error, not a soft
placeholder. The target is named here by its repository path instead.

A second, related target exists in prose form: `docs/multi-tenant-conformance.md` states the same
"row zero" host-binding contract this crate's `AuthCheck`/`WriteInsert` rules encode mechanically.
This crate does not claim to realize that document directly — it realizes the formal spec; the
prose checklist is supporting context, linked under *Relationships* below via the corpus nodes that
already cite it.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/lib.rs` — `TraceStep`, `TraceAction`, `AbstractState`, `CommunityLabel`/`HostLabel`/`ChannelLabel`/`ActorLabel`/`OpaqueId` | The trace schema itself — the projected observation vocabulary the checker replays against | Deliberately shares zero type machinery with `buzz_core` (see Cargo.toml's independence-rule comment); `CommunityLabel` is a standalone newtype so a bug in production types cannot launder into the checker |
| `src/lib.rs` — `Tracer` trait, `NoopTracer` | The emit seam production code calls; `enabled()` lets hot-path callers skip building emit inputs when tracing is off | `NoopTracer` is the production default — zero decision-path cost |
| `src/transitions.rs` — `ModelState::bootstrap`, `check_step` | The spec's `Next` relation, independently re-implemented: three universal per-step obligations (resolved community / bound host / actor agree with the bootstrapped model) plus per-action guards (e.g. `AuthCheck` `Allow` requires claimed == resolved) | Explicitly does not import any production crate (module doc, `transitions.rs:1-44`) |
| `src/checker.rs` — `Scenario`, `check_trace` | The replay engine: bootstrap, schema-version check, per-step `check_step`, then coverage-breach check against `required_critical_actions` | Fail-closed: first transition error stops the trace; an empty trace is itself a coverage breach |
| `crates/buzz-relay/src/conformance/mod.rs` — `state_for_request`, `claimed_community_from_event`, `record_req_authcheck`, `project_row_community`/`RowCommunityProjection`, `EmitGuard`, `sanitized_reason_for` | The relay-side emitter that projects real request decisions into `TraceStep`s and arms/drops `EmitGuard` at critical seams | This file lives in `buzz-relay`, not in `buzz-conformance` itself — the independence rule requires the checker and the emitter to be separate crates; this node documents the checker's crate, and cites the emitter only as the seam that feeds it |
| `crates/buzz-relay/src/handlers/ingest.rs` | Wires `AuthCheck`, `WriteInsert`/`WriteInsertGlobal`/`WriteDuplicate`, and the outer-wrapper `SanitizedError` emit | Confirmed via `TRACE_SCHEMA.md`'s "Where the emitter lives" table; the ingest.rs body itself was not read line-by-line for this node |
| `crates/buzz-relay/src/handlers/req.rs` | The read-seam emitter (`ReadMessageRows`/`ReadByIdRows`/`ReadHostFeedRows`) | **Held back** as an additive patch not yet landed — see *Divergences* |

## Divergences

These are named directly by the crate's own `LIMITS.md`, not inferred:

- **The read-seam half of the gate is not yet armed.** `LIMITS.md` states the per-row community
  projection for `read_message_rows`/`read_by_id_rows` is a design question still awaiting review,
  and until it lands "the read-seam half of the gate is not yet armed" — `TraceAction::ReadMessageRows`
  and friends exist in the schema and are checker-tested, but the production emit site
  (`crates/buzz-relay/src/handlers/req.rs`) is a held-back patch, not merged code.
- **Coverage is execution coverage, not exhaustive.** The gate is silent about any code path that
  never runs during a CI execution; a new endpoint that bypasses `EmitGuard::arm` produces no
  signal at all — enforced by code review, not by the harness.
- **Cross-pod leaks are out of scope.** The harness traces one process; a multi-pod leak is visible
  only on the pod that observes it.
- **Time-bounded and concurrency properties are out of scope.** Both the spec and the gate are
  untimed.
- **Pub/sub fan-out is not a spec action.** A fan-out leak shows up in the receiver's own
  ingest/read trace, never in the publisher's emit.
- **Type-level fences are enforced by the compiler, not this gate.** If `CommunityId` ever grew a
  `From<Uuid>` impl, breaking the no-parse-from-client fence, this gate would not detect it.

**One drift was found beyond what `LIMITS.md` names as a scope limit: `LIMITS.md`'s own test-count
comment has drifted from the code it describes.** It states 9 + 5 + 2 = 16 tests across the three
CI commands; counting `#[test]` functions directly against current source gives 9 + 6 + 10 = 25.
The `--lib` count (9) still matches. The `replay_fixtures` count is stale by one test
(`missing_required_action_is_coverage_breach`, or possibly `foreign_row_leak_is_non_interference`,
was added after the comment was last updated — which one was not determined). The `buzz-relay`
count is stale by 8: `LIMITS.md`'s comment describes only the two `EmitGuard`-Drop self-tests it
was written to justify, but the `conformance::` substring filter it prescribes as the literal CI
command also runs `CountingTracer`'s `enabled()`-delegation test and 7 tests of
`record_req_authcheck`/row-projection helpers that share the same test module. This is a
documentation-lags-code drift in the crate's own file, not a gate that is failing — the tests
themselves are real and passing (see *Verification*); nobody has gone back to update the comment's
count as the module grew. Beyond this, the checked-in fixture suite (`good.jsonl`,
`bad_host_channel_mismatch.jsonl`, `bad_coverage_breach.jsonl`, `bad_foreign_row_leak.jsonl`)
demonstrates each of `LIMITS.md`'s stated failure modes actually fires, and no other drift was
found while writing this node.

## Verification

Per `LIMITS.md`'s own CI command section, three test surfaces are required to stay green on every
PR. **`LIMITS.md`'s own inline comment undercounts them** (see *Divergences*) — the counts below
were recounted directly against current source, not copied from that comment:

1. `cargo test -p buzz-conformance --lib` — 9 schema/checker unit tests in `checker.rs`, covering
   every `TraceAction` variant plus at least one mutation-class bite (M2 claim-vs-resolved,
   coverage breach, state mismatch, non-interference).
2. `cargo test -p buzz-conformance --test replay_fixtures` — 6 tests (not the 5 `LIMITS.md`'s own
   comment names): the 3 committed-JSONL round-trips against `good.jsonl` /
   `bad_host_channel_mismatch.jsonl` / `bad_coverage_breach.jsonl`, a 4th round-trip against
   `bad_foreign_row_leak.jsonl`, plus a standalone empty-trace case and a scenario-required-action
   case that use no fixture file. Each fixture is round-tripped byte-exact against a typed Rust
   builder before being replayed, so a schema change forces a deliberate fixture refresh
   (`BUZZ_CONFORMANCE_UPDATE=1`) rather than a silent drift.
3. `cargo test -p buzz-relay --lib conformance::` — this filter matches all 10 tests in that
   module's `#[cfg(test)] mod tests`, not only the 2 `EmitGuard`-Drop-specific self-tests
   `LIMITS.md`'s comment names (which do prove the coverage guard fires `ImplBug` on Drop when
   nothing was emitted, and stays silent when an emit did occur). The other 8 cover
   `CountingTracer`'s `enabled()` delegation and the `record_req_authcheck`/row-projection helpers
   this node's Implementation surface table also names.

The Justfile's unit-test job runs the equivalent `cargo nextest run -p buzz-conformance` (all
targets) unconditionally, with an inline comment stating this is deliberately infra-free so it
belongs in the fast unit job rather than the Postgres/Redis-backed integration job.

**Not yet verified:** the integration replay — a live relay driving `JsonlTracer` per request
against the real e2e suite, then asserting every captured trace through `check_trace` — is named in
`LIMITS.md` as "the next ratchet," landing once the held-back `req.rs` read-seam patch is applied.
Until then, conformance is proven only for the traces the unit/fixture/property tests construct by
hand or generate, not for live relay traffic.

## Relationships

- references: architecture-flows-event-ingestion
- references: architecture-principles-community-is-security-boundary

No `implements` edge: the realized target, `docs/spec/MultiTenantRelay.tla`, has no corpus node id
at this revision (checked directly against `origin/launchpad`'s corpus tree; see the evidence
ledger). No `part-of` edge toward `architecture-containers-relay`: the crate's own independence
rule makes it deliberately not a sub-component of the relay crate it is checked against — it is a
peer crate the relay depends on, not the reverse, and `relay.md` does not itself mention
`buzz-conformance` at this revision.

## Scope and omissions

**This node covers** what `buzz-conformance` is responsible for: the trace schema, the `Tracer`
seam, and the independent replay checker (`check_trace`/`check_step`) that validates recorded
traces against `docs/spec/MultiTenantRelay.tla`'s `Next` relation and its non-interference
invariants; its public entry points; its committed fixture and property-test surfaces; and the
three-part CI gate that keeps it load-bearing rather than decorative.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay-side emitter that actually produces `TraceStep`s from live requests | `crates/buzz-relay/src/conformance/mod.rs`, `tracers.rs`, and the wiring in `handlers/ingest.rs` — documented in this node's Implementation surface table but not itself a `buzz-conformance` source file |
| The formal spec's own correctness (TLC model-checking obligation) | `docs/spec/MultiTenantRelay.tla`, machine-checked separately from this crate |
| The black-box A/B isolation suite for the same invariant | `crates/buzz-test-client/tests/conformance_multitenant.rs`, `#[ignore]`-gated, requiring a live two-host multi-tenant deployment; already described in `architecture-principles-community-is-security-boundary` |
| The prose "row zero" conformance checklist | `docs/multi-tenant-conformance.md` |
| Whether every route touching the tenant boundary correctly arms an `EmitGuard` | Enforced by code review per `LIMITS.md`, not by this crate or any automated check |

**Expected but not verified when this node was written:**

- **The read-seam integration replay has not landed.** `LIMITS.md` names it as the next ratchet;
  this node describes the checker as it exists today, schema-complete but only unit/fixture/property
  tested, not yet exercised against live relay traffic.
- **`ingest.rs`'s emit call sites were not read line-by-line.** Their existence and shape are taken
  from `TRACE_SCHEMA.md`'s own "Where the emitter lives" table (itself a `FACT` citation in this
  node's ledger) rather than independently re-derived from the handler source.
- **Whether the `#[ignore]`-gated `conformance_multitenant.rs` suite currently passes** was not
  checked — it requires standing up a two-host deployment, out of scope for authoring this node, and
  is already flagged as unexecuted by `architecture-principles-community-is-security-boundary`.
