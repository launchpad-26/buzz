---
id: layers-security-security-invariants
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`docs/spec/MultiTenantRelay.tla` names a top-level `Safety` property as the conjunction of `TypeOK` and twelve invariants: `Inv_NonInterference`, `Inv_LabelPropagation`, `Inv_ReadConfinement`, `Inv_ResolutionFence`, `Inv_HostBindingFence`, `Inv_ChannelCommunityImmutable`, `Inv_AdmissionFence`, `Inv_AcceptedWritesPersist`, `Inv_MessageKeyUnique`, `Inv_NoTenantContextFailsClosed`, `Inv_ProjectionDerived`, and `Inv_SanitizedErrors`."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:1128-1141"
  - statement: "The spec's own comments state what each of these invariants means in plain terms: `Inv_NonInterference` — no observation scoped to community C may be influenced by data labeled outside C; `Inv_ReadConfinement` — every row in a `ResultRows` observation carries the same community as the observation; `Inv_HostBindingFence` — every accepted write and every recorded duplicate/no-op carries a host whose mapped community equals the write's stored community; `Inv_AdmissionFence` — active memberships and channel-less read capabilities may only exist for an actor admitted in that same community; `Inv_NoTenantContextFailsClosed` — a `ResultRows` observation with no community label serves no rows; `Inv_SanitizedErrors` — every client-visible `SanitizedError` observation's error is drawn from a fixed alphabet, not an ad hoc string."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:981-1001"
      - "docs/spec/MultiTenantRelay.tla:1038-1051"
      - "docs/spec/MultiTenantRelay.tla:1071-1084"
      - "docs/spec/MultiTenantRelay.tla:1114-1126"
  - statement: "The `buzz-conformance` crate's own module documentation states it is 'an independent replay checker' whose `check_trace` function 'consumes a sequence of TraceSteps and validates them against the TLA+ spec's Next transition relation,' re-implementing the relevant spec actions in Rust rather than calling any production reducer, specifically so that a bug shared between the emitter and the checker cannot hide itself from both."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:1-36"
  - statement: "`check_trace` reports three distinct failure modes: an illegal transition (the traced action is not allowed from the checker's current model state), a state mismatch (e.g. `state_after.row_labels` includes a community other than the resolved tenant — the runtime instance of `Inv_NonInterference`), and a coverage breach (an unknown critical action, or a critical seam that exits without a trace step, recorded as `TraceAction::ImplBug`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs:25-36"
  - statement: "`EmitGuard` is the mechanism that turns an unarmed exit into a coverage breach rather than silence: `EmitGuard::arm` wraps the tracer in a counting wrapper, and `EmitGuard`'s `Drop` implementation checks the counter and, if it is still zero, records a `TraceAction::ImplBug` step onto the underlying tracer before the guard is dropped — so a code path that returns early without emitting is caught structurally rather than by someone noticing its absence."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs:344-411"
      - "crates/buzz-relay/src/conformance/mod.rs:413-424"
  - statement: "`ingest_event` (the relay's shared Nostr event-ingest entry point for both WebSocket and HTTP transports) arms an `EmitGuard` around its own inner logic specifically so that 'any exit path that doesn't emit a Write*/SanitizedError action will be caught by the guard's Drop -> ImplBug -> CoverageBreach,' per its own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1867-1900"
  - statement: "The read path is also wired into the same tracer: `req.rs` calls `crate::conformance::record_req_authcheck` for REQ-path membership decisions and `record_read_message_rows` / `record_read_by_id_rows` when returning result rows, each carrying the request's `AbstractState` built from the connection's already-resolved `TenantContext`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:135"
      - "crates/buzz-relay/src/handlers/req.rs:162"
      - "crates/buzz-relay/src/handlers/req.rs:422"
      - "crates/buzz-relay/src/handlers/req.rs:750"
  - statement: "`AppState.tracer` defaults to `NoopTracer` in production ('production binds `crate::conformance::NoopTracer` (zero cost)'; the field's own doc comment states conformance tests overwrite this with a `JsonlTracer` after construction), so every emit and guard-arm in a live deployment is, by the harness's own design, a no-op call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:757-762"
      - "crates/buzz-relay/src/state.rs:937-941"
  - statement: "`crates/buzz-conformance/LIMITS.md`, the crate's own self-documented limits, states the harness is 'wired only at the ingest/auth/read accept-reject boundary in crates/buzz-relay/src/handlers/{ingest,req,event}.rs' and that coverage is 'execution coverage': the gate is silent about any unsafe path that never executes during a run it observed."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:11-32"
  - statement: "The same file states that arming new call sites is not itself enforced by the harness: 'If a new endpoint is added that bypasses EmitGuard::arm, the gate is blind. New endpoints touching the tenant boundary MUST arm a guard at entry -- that's enforced by code review, not by the harness.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:34-37"
  - statement: "`LIMITS.md` lists six categories the gate does not catch even where armed: DB-layer leaks the projection itself does not read, cross-pod leaks (the harness traces one process only), time-bounded/concurrency properties (the spec is untimed), pubsub fan-out (not a modeled spec action; a fan-out leak shows up in the receiver's own ingest/read trace, not the publisher's emit), type-level fence violations (e.g. `CommunityId` gaining a `From<Uuid>` impl -- caught by the Rust compiler today, not by this gate, and not if that fence were ever removed), and spec bugs themselves (the checker re-implements the spec, so a wrong spec and a wrong checker agree)."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:39-72"
  - statement: "`LIMITS.md` names three test surfaces that must stay green on every PR -- 9 unit tests (`cargo test -p buzz-conformance --lib`), 5 replay-fixture tests (`cargo test -p buzz-conformance --test replay_fixtures`, replaying committed JSONL traces including a known-bad `bad_host_channel_mismatch.jsonl` expected to return `IllegalTransition` and `bad_coverage_breach.jsonl` expected to return `CoverageBreach`), and 2 `EmitGuard` coverage-breach self-tests (`cargo test -p buzz-relay --lib conformance::`) -- 16 tests total, none carrying `#[ignore]` in this repository at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:85-120"
      - "grep_repo(pattern='#\\[ignore\\]|#\\[test\\]', path='crates/buzz-conformance/tests/proptest_checker.rs;crates/buzz-conformance/tests/replay_fixtures.rs') -> only #[test] attributes present, zero #[ignore] matches, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`LIMITS.md`'s own words name the gap this node's *Enforcement today* section reports honestly: 'The integration replay (live relay -> JsonlTracer -> check_trace) lands with the read-seam patch onto Max's req.rs work,' described as 'the next ratchet' rather than something already landed."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/LIMITS.md:117-126"
  - statement: "At the recorded revision, no call site anywhere in `crates/buzz-relay` or `crates/buzz-test-client` invokes `check_trace` -- the function is called only from `buzz-conformance`'s own test suite (`proptest_checker.rs`, `replay_fixtures.rs`) against synthetic and fixture traces, not against a real relay's captured runtime traffic -- confirming `LIMITS.md`'s 'next ratchet' framing is still accurate now, not stale prose left behind after the gap closed."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='check_trace', path='crates/buzz-relay/**;crates/buzz-test-client/**') -> zero matches, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`architecture-principles-fail-closed-boundaries` and `architecture-principles-community-is-security-boundary` are both present in `origin/launchpad`'s corpus tree at the recorded revision, alongside dozens of other `architecture/*` nodes; `layers/security/security-invariants.md` and every other `layers/security/*` or `layers/identity/*` sibling task's target file (identity-invariants.md, trust-boundaries.md, trust-model.md) are absent from that tree."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes architecture/principles/fail-closed-boundaries.md and architecture/principles/community-is-security-boundary.md; no layers/ subtree present, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Because the effective severity of a real Safety-conjunct violation today is decided by whether the enforcing code path itself fails closed (documented separately in `architecture-principles-fail-closed-boundaries` and `architecture-principles-community-is-security-boundary`) and not by this conformance gate -- which is observation-only, bound to `NoopTracer` in production, and not yet replayed against live traffic even where a JsonlTracer is used -- a violation reaching production today would not be caught by this specific mechanism at all; whatever protection currently exists against it comes from the underlying enforcement code, not from trace conformance."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/state.rs:937-941"
      - "crates/buzz-conformance/LIMITS.md:74-83"
    confidence: 0.8
  - statement: "Issue #1176's definition of done requires the invariant be stated as one unambiguous property using MUST/MUST NOT only where normative, with scope, named enforcement points and observable failure behavior, and at least one verification/conformance mechanism named or its absence recorded explicitly."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1176 definition of done"
relationships:
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Buzz's security invariants are formally named and mechanically checkable: invariant

## Invariant statement

Every observation, accepted write, and recorded duplicate/no-op outcome the
relay produces at its ingest/auth/read accept-reject boundary **MUST**
satisfy every conjunct of the `Safety` property defined in
`docs/spec/MultiTenantRelay.tla` (`TypeOK` and the twelve `Inv_*` invariants
named in *Scope* below) simultaneously. No accepted decision **MUST NOT**
violate any one of them, regardless of which handler or code path produced
it — the conjuncts are not independent options a given surface may satisfy
selectively.

This is stated as one property, not twelve, because the spec itself states
it that way: `Safety` is a single top-level definition, and a trace that
satisfies eleven conjuncts and fails a twelfth is not "mostly compliant," it
is a Safety violation. Buzz additionally maintains an independent,
non-production Rust reimplementation of that same model
(`buzz-conformance::check_trace`) capable of judging a captured runtime
trace against every one of those conjuncts — this second fact documents how
the first is checked, not a second invariant. The security properties Buzz
claims to hold at this boundary are not merely asserted in prose: they are
named, formally specified, and machine-checkable against real code paths,
even where — see *Enforcement today* below — the checking machinery is not
yet wired to run against live traffic.

## Scope

**Binds:** the relay's ingest/auth/read accept-reject boundary in
`crates/buzz-relay/src/handlers/{ingest,req,event}.rs` — the seam
`LIMITS.md` itself names as the harness's wiring point, chosen because
tenant-derived decisions become observable behavior there and every other
layer (DB filter SQL, Redis pub/sub, S3 metadata) is downstream of a
decision made at this seam.

**Which invariants:** the twelve named conjuncts of `Safety`
(`Inv_NonInterference`, `Inv_LabelPropagation`, `Inv_ReadConfinement`,
`Inv_ResolutionFence`, `Inv_HostBindingFence`, `Inv_ChannelCommunityImmutable`,
`Inv_AdmissionFence`, `Inv_AcceptedWritesPersist`, `Inv_MessageKeyUnique`,
`Inv_NoTenantContextFailsClosed`, `Inv_ProjectionDerived`,
`Inv_SanitizedErrors`) plus `TypeOK`, each stated in the spec as a condition
over the model's `observations`, `messages`, `acceptedWrites`,
`duplicateWrites`, `createdChannels`, `memberships`, and related state — see
the evidence ledger above for what several of them mean in plain terms.

**Every externally-visible moment, not necessarily every intermediate
instruction:** the spec's invariants are stated over completed transitions
(an accepted write, a recorded observation), not over intermediate steps of
handling one request — this node makes no claim about what is true
mid-request, only about what the accept-reject boundary produces once a
decision is made.

**Does not bind:** internal server-to-server paths with no request/connection
observation at this boundary (e.g. background jobs that never emit a trace
step), and does not claim coverage of every code path in the three wired
handler files — only the ones armed with `EmitGuard` or an explicit
`record_*` call, per *Enforcement today* below.

## Enforcement today

This is a mixed picture, and the weakest true tier — per this template's own
instruction not to round up — is **convention-and-review only**, for one
specific reason named by the crate's own limits document: nothing but code
review stops a new endpoint that touches the tenant boundary from skipping
`EmitGuard::arm` entirely, and if that happens the gate is blind to it, not
merely silent about a violation. Layered on top of that:

- **Structurally enforced, for the write path.** `ingest_event` wraps its own
  inner logic in an `EmitGuard`, so *within that function*, any exit that
  doesn't emit a `Write*`/`SanitizedError` action is caught by the guard's
  `Drop` as a coverage breach — the code's shape makes silent omission
  unreachable inside that one function, though nothing stops a rewrite of
  `ingest_event` itself from removing the guard.
- **Present but not guard-wrapped, for the read path.** `req.rs` calls
  `record_req_authcheck`, `record_read_message_rows`, and
  `record_read_by_id_rows` directly at specific call sites — these are
  present today (contradicting an out-of-date comment elsewhere in the
  conformance module suggesting the read seam was "held back"), but this
  node did not verify whether every exit from `req.rs`'s read paths is
  itself `EmitGuard`-wrapped the way `ingest_event` is.
- **Test-enforced, for the checker and guard machinery itself.** Sixteen
  tests (9 unit + 5 replay-fixture + 2 `EmitGuard` self-tests), none
  `#[ignore]`d, assert that `check_trace` correctly rejects known-bad
  synthetic traces (`bad_host_channel_mismatch.jsonl` →
  `IllegalTransition`, `bad_coverage_breach.jsonl` → `CoverageBreach`) and
  that `EmitGuard`'s `Drop` fires on a missing emit. This proves the
  *checking logic* works against fixtures — it does not prove any real
  relay request has ever been checked by it.
- **Not yet built, for the part that would actually catch a live
  violation.** No call site in `crates/buzz-relay` or
  `crates/buzz-test-client` invokes `check_trace` against a captured live
  trace, production binds a zero-cost `NoopTracer` by design, and
  `LIMITS.md` names the live-relay-to-checker integration replay as "the
  next ratchet" — a planned, not-yet-landed step.

## Consequence of violation

Grounded in what the code and `LIMITS.md` actually say, not assumed: if a
Safety-conjunct violation occurred in a JsonlTracer-instrumented test run
that reaches an armed seam, `check_trace` would return a `TransitionError`
(`IllegalTransition`, a state mismatch such as an `Inv_NonInterference`
breach, or `CoverageBreach`), and the fixture-based tests demonstrate this
mechanism actually distinguishes a bad trace from a good one. But
`LIMITS.md` is explicit that the gate is "observation only — it does not
feed back into the decision," and production runs `NoopTracer`, so **the
practical consequence of a real violation reaching production today is
silence from this specific mechanism**: no denial, no alarm, no crash
attributable to trace conformance. Whatever actually stops or catches such
a violation in production is the underlying enforcement code documented in
`architecture-principles-fail-closed-boundaries` and
`architecture-principles-community-is-security-boundary` (fail-closed
lookups, the host-binding fence), not this conformance gate — this node's
own INFERENCE entry above states that connection explicitly.

## Boundary

This node does not describe:

- **Event authenticity (Schnorr signature / event-ID verification).** A
  real, distinct invariant enforced by `buzz_core::verification::verify_event`
  and gated at ingest (`crates/buzz-relay/src/handlers/ingest.rs`), but this
  node's scope is the tenant/security `Safety` conjunction the TLA+ spec and
  `buzz-conformance` model — signature verification is not one of that
  spec's modeled actions. It is `#1166`'s subject
  (`layers/protocol/signature.md`, not yet merged).
- **Audit-log tamper evidence (the SHA-256 hash chain in `buzz-audit`).**
  A distinct, deterministic-hash-based invariant with its own enforcement
  and verification story (`compute_hash`, `AuditService::verify_chain`) —
  `#1135`'s subject (`layers/observability/audit-log.md`, not yet merged),
  not restated here.
- **The tenant/host-binding fence and fail-closed decision-making
  themselves.** Already documented, in depth, by the two merged nodes this
  node `references` — `architecture-principles-community-is-security-boundary`
  and `architecture-principles-fail-closed-boundaries`. This node names
  which TLA+ conjuncts formalize pieces of those principles
  (`Inv_HostBindingFence`, `Inv_ResolutionFence`, `Inv_AdmissionFence` for
  the boundary; `Inv_NoTenantContextFailsClosed` for fail-closed reads) but
  does not restate their enforcement-point tables.
- **The other `layers/security/*` topic docs in this same PRD.** Each of
  `admin-boundary` (`#1168`), `provider-boundary` (`#1171`),
  `relay-boundary` (`#1172`), `input-validation` (`#1170`),
  `cryptographic-boundary` (`#1169`), `replay-protection` (`#1173`),
  `residual-risks` (`#1174`), `secret-management` (`#1175`),
  `tenancy-boundary` (`#1179`), `ssrf-protection` (`#1178`),
  `threat-model` (`#1180`), `trust-boundaries` (`#1181`),
  `trust-model` (`#1182`), and `security-model` (`#1177`) is its own task
  and its own future node — none is merged at this revision, so none is a
  legitimate `relationships` target, and this node makes no claim about
  their subject matter.
- **Identity-specific invariants.** `#1108`'s subject
  (`layers/identity/identity-invariants.md`, not yet merged).
- **Whether the spec itself is correct.** `LIMITS.md`'s own words: "the
  checker re-implements the spec; if the spec is wrong, both pass. Spec
  correctness is the proof obligation of `docs/spec/MultiTenantRelay.tla`,
  machine-checked by TLC" — a claim about the model, not about this
  documentation task.

## Relationships

- references: `architecture-principles-fail-closed-boundaries` — that
  node's fail-closed shape is the enforcement story behind
  `Inv_NoTenantContextFailsClosed`.
- references: `architecture-principles-community-is-security-boundary` —
  that node's host-binding-fence enforcement story is the concrete code
  behind `Inv_HostBindingFence`, `Inv_ResolutionFence`, and
  `Inv_AdmissionFence`.

Both targets are confirmed present in `origin/launchpad`'s corpus tree at
the recorded revision (see the evidence ledger's `git_ls_tree` entry). No
`depends-on` or `implements` edge is declared: this node's own claim does
not require either referenced node's claim to hold in order to be true
(each is independently verifiable), and while `templates/invariant.md`
(`corpus-template-invariant`) permits an optional self-referencing
`implements` edge, this node omits it for the same reason the two
referenced nodes omit their own — the node's shape already shows which
template it followed, and the corpus does not yet have a settled convention
for whether that edge is worth adding (see `templates/invariant.md`'s own
open question on this point).

## Scope and omissions

**This node covers:** that Buzz's tenant/security invariants at the
relay's accept-reject boundary are formally named (the `Safety` conjuncts
in `docs/spec/MultiTenantRelay.tla`) and backed by an independent,
non-production runtime checker (`buzz-conformance::check_trace`) rather
than only informal review; which handler call sites are wired into that
checker today; and — honestly, per the invariant template's evidence
expectations — how far that wiring currently reaches versus where it does
not yet reach production traffic at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Event signature/ID verification | `#1166` (`layers/protocol/signature.md`, not yet merged) |
| Audit-log hash-chain tamper evidence | `#1135` (`layers/observability/audit-log.md`, not yet merged) |
| The host-binding fence's own enforcement-point table | `architecture-principles-community-is-security-boundary` (merged) |
| The fail-closed decision shape's own enforcement-point table | `architecture-principles-fail-closed-boundaries` (merged) |
| Identity-specific invariants | `#1108` (`layers/identity/identity-invariants.md`, not yet merged) |
| Trust boundaries and trust model | `#1181`, `#1182` (not yet merged) |
| Threat model, residual risks, and the other boundary-specific topics | `#1168`–`#1180` as listed in *Boundary* above (not yet merged) |
| Whether the TLA+ spec itself is a correct model of the intended system | `docs/spec/MultiTenantRelay.tla`, machine-checked by TLC — not this node |

**Expected but not verified when this node was written:**

- **Whether TLC has actually been run against the current spec at this
  revision, and with what result.** This node cites the spec's own text
  and `LIMITS.md`'s claim that TLC is the proof obligation; it does not
  re-run or reproduce a TLC check.
- **Whether every exit path in `req.rs`'s read handlers is `EmitGuard`-
  wrapped the way `ingest_event` is**, or whether some read-path exits rely
  only on the direct `record_*` calls without a Drop-based backstop — this
  node verified the calls exist, not an exhaustive audit of every return
  path in `req.rs`.
- **Whether the module doc comment in `crates/buzz-relay/src/conformance/
  mod.rs` describing the read seam as "held back... for Eva to apply" is
  simply stale** (the calls it describes as pending already exist in
  `req.rs`) or reflects a narrower, still-pending sub-patch this node did
  not identify. Reported as an open discrepancy rather than resolved either
  way.
- **Whether any deployment configuration other than the default enables a
  non-`NoopTracer` in production** — this node verified the *default*
  construction path in `state.rs`, not every configuration surface that
  might override it.
