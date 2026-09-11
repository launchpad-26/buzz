# P-06 Harness interface — code-level contract

This is the implementation contract for P-06. The shared types and cross-part signatures in
[`CONTRACTS.md`](CONTRACTS.md) are normative; P-06 neither redefines them nor accepts an alternative
shape. P-06 deterministically plans regenerated review obligations, owns the complete panel loop, is
the sole RQA part that hands PR-derived content to a harness, and records what it actually ran.

## 1. Modules

```
rqa/harness/
  __init__.py    re-exports plan, run, SupplyPort, HarnessAdapter, BundleFailure and HarnessError
  risk.py        risk classification and deterministic plan selection
  bundle.py      fail-closed bundle assembly and nonce envelopes
  adapters.py    HarnessAdapter registry and generic external-command adapter
  invoke.py      the one process-execution routine used for every harness command
  panel.py       complete route/reservation/invocation/validation/consumption loop
  errors.py      P-06 programming and deployment errors
```

`rqa.harness` imports shared values only from their owning parts and calls only the listed edges:
`rqa.protocol.paths.matches()` (P-04), E-08 `validate`, `RecordWriter.append`, and the methods of its
injected `SupplyPort`. It never imports or calls P-05 functions directly. P-02 constructs `SupplyPort`
over E-06 and E-15, calls `plan()` once, and calls `run()` at most once for a review; it does not own a
retry or fallback loop.

## 2. Types

All exchanged values — including `RouteUnavailable`, `BundleFailure`, `PanelResult`, `Valid` and
`Invalid` — are defined exclusively in [`CONTRACTS.md`](CONTRACTS.md) §§1–8 and imported unchanged.
P-06 defines only its private adapter and programming-error types.

```python
# panel.py — P-06's view of E-06 and E-15. P-02 constructs this adapter over P-05.
class SupplyPort(Protocol):
    def route(self, obligation: str, cursor: RouteCursor) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
    def reserve(self, plan: Plan, route: Route) -> Reservation | Refusal: ...
    def consumed(self, attempt: Attempt, reading: int | None, reservation: Reservation) -> Spend: ...

# adapters.py — adapter_for is the only dispatch point: a non-empty route.command resolves to the
# generic external-command adapter, otherwise route.harness resolves to a built-in adapter.
class HarnessAdapter(Protocol):
    enforceable_efforts: frozenset[str]
    role_separated_data: Literal[True]
    injection_conformance_hash: str
    def argv(self, route: Route, effort: str) -> tuple[str, ...]: ...
    def resolved_effort(self, requested: str) -> str: ...

class HarnessError(Exception): ...
class EmptyPlanError(HarnessError): ...
class ProtocolVersionUnknown(HarnessError): ...
```

`BundleFailure` is the shared E-07 return alternative in `CONTRACTS.md` §5. `HarnessError`
subclasses are programming/deployment errors; policy, availability and budget outcomes remain
values. `AppendFailed` always propagates.

`RISK_CLASSES = ("security", "migration", "infrastructure", "standard")`; the first matching class
is the recorded class. `STRATEGIES` maps `single_pass`, `independent_panel`, and
`challenge_and_verify` to their fixed minimum participant counts and requested effort. Every risk-path
and obligation-path comparison calls only `rqa.protocol.paths.matches(path, pattern)` (P-04); no other
path matcher is permitted.

## 3. Entry points — E-07

P-06 provides these signatures verbatim from [`CONTRACTS.md` §9](CONTRACTS.md#9-edge-signatures--one-per-e-nn-verbatim):

```python
def plan(*, job: Job, facts: Facts, snapshot: Snapshot, carry: CarryOver, record: RecordWriter) -> Plan: ...
def run(*, job: Job, plan: Plan, facts: Facts, snapshot: Snapshot, supply: SupplyPort, state_dir: Path,
        record: RecordWriter) -> PanelResult | BundleFailure: ...
```

### 3.1 `plan`

`plan()` is total and deterministic for its inputs. It uses `facts.changed_paths` and P-04 `matches()`
to derive matched risk classes and select obligations. Its strategy and participant count are determined
only by `snapshot.policy.assurance`: the maximum required assurance across all matched classes is used;
`single_pass` is selected for one participant, `challenge_and_verify` for a security or migration review
requiring at least three participants, and otherwise `independent_panel`. A missing assurance entry falls
back only to the snapshot's `standard` value, then to one.

For every policy obligation, processing is total and mutually exclusive:

1. If its id occurs in `carry.reused`, do not plan it and set `omitted[id] = "carried"`.
2. Otherwise, if no matched risk class is in `required_for`, omit it with the deterministic risk-class
   reason.
3. Otherwise, if it has path patterns and no `facts.changed_paths` member satisfies
   `matches(path, pattern)` for one of them, omit it with the deterministic path reason.
4. Otherwise, include its id in `Plan.obligations`.

Thus carried obligations are never planned, while every non-carried policy obligation appears exactly
once in obligations/omitted. The returned `Plan` also copies `job.head_sha`, `snapshot.hash`,
`snapshot.protocol_hash`, and `snapshot.policy.version` into its four pin fields. P-06 appends
`asdict(plan)` as `plan` and returns it; `AppendFailed` propagates. Lifecycle skips `run()` when
`carry.regenerated` is empty. A caller invoking `run()` with no planned obligation gets
`EmptyPlanError`, never an invented evidence outcome.

### 3.2 `run`: the complete panel loop

P-06 assembles the bundle once. On failure it appends a `bundle` entry with
`status="incomplete"` and returns `BundleFailure`; it creates no attempt or partial final bundle.
Otherwise it appends a ready `bundle` entry and selects against the deterministic first planned
obligation. Every valid verdict evaluates the whole bundle; that obligation selects the supply ladder.

Start with an empty `RouteCursor`, no counted families and no attempts. `finish(complete, reason)`
captures UTC **after** the last attempt/consumption, appends one `panel` entry containing the attempt
ids, completeness, reason, that `evidence_cutoff` and `bound_reached`, and returns the identical
shared `PanelResult`.

`bound_reached` is set the first time `supply.reserve` returns any `Refusal` and is never cleared —
**including `Refusal(fallback)`, which resumes candidate selection**. RQA-FR-039's fit criterion is
"no review run in which a configured bound was reached ends in a successful disposition, independent
of which of RQA-FR-022's three outcomes it produced instead", so taking the configured fallback is
permitted while a successful outcome afterwards is not; P-07 §3 step 10 enforces that.

For each candidate selection:

1. Call `supply.route(obligation, cursor)`. `RouteUnavailable` returns
   `finish(False, "exhausted")`. Retain the returned cursor before any local union.
2. **Before the first invocation of a route whose `command` is non-empty**, run the published
   clean/adversarial conformance pair against that exact argv (§3.3). It is the operator's
   declaration, not RQA's build, so it cannot have been verified before release the way a built-in
   adapter is. A pass appends an `attestation` entry whose subject is the conformance run — argv
   hash, protocol hash, suite id, result — and is cached for the rest of the job by
   `(argv_hash, protocol_hash)`; no real PR bytes reach that command before the pass is recorded.
   A failure, a spawn error or a timeout is classified `CANDIDATE_TERMINAL`: the route is excluded
   through the cursor, the failure is recorded, and candidate selection resumes. A built-in
   adapter's registry membership already carries this proof and is not re-run.
3. Immediately before an invocation, call `supply.reserve(plan, route)`. A reservation is consumed
   by exactly one invocation. `Refusal(fallback)` excludes the route family and resumes candidate
   selection; `Refusal(incomplete|escalate)` returns `finish(False, "budget")`; any other value raises
   `HarnessError`.
4. Invoke, validate through E-08, build the attempt/attestation, append `attestation`, and call
   `supply.consumed(attempt, reading, reservation)` for every outcome, including timeout or launch
   failure.
5. A valid verdict from a new provider family counts. If `plan.participants` distinct families have
   counted, return `finish(True, None)`. A non-completing valid verdict and
   `CANDIDATE_TERMINAL` exclude the route; `PROVIDER_TERMINAL` excludes the family.
6. On the **first** `TRANSIENT`, remain on the same route but return to step 3: obtain a new
   reservation before the one permitted retry. If that reservation refuses, follow step 2's refusal
   branch. A second transient excludes the route; no third invocation occurs.

Every invocation therefore has a unique preceding reservation and a following consumption report.
Every non-success selection grows the cursor; the only same-route retry is bounded to one and also
requires a fresh reservation. The finite ladder proves that `run()` completes, returns a named
incomplete panel or `BundleFailure`, or raises a named programming error.

### 3.3 Harness interaction contract — E-19

The harness is a local subprocess. RQA supplies only the minimal environment plus the bundle,
protocol and verdict paths; it supplies no RQA/GitHub credentials. Every registered adapter must
declare `role_separated_data is True`, use its provider's instruction/data roles, and identify the
published injection-conformance suite it passed. An adapter without that channel separation or with
a failing conformance suite is absent from the registry, not a degraded route.

**A harness RQA ships no adapter for runs through the generic external-command adapter** built from
`route.command`: RQA appends the bundle directory, the immutable protocol instruction and the verdict
output path exactly as it does for a built-in, and classifies the result by the same table below. It
is admitted only when the conformance run wired into §3.2 step 2 passes against its exact argv — the
same bar every built-in meets, applied at first use rather than at build time, because an
operator-declared command does not exist when RQA is built. The contract is the gate; RQA's source
is not (RQA-FR-030, AC15). A command whose conformance run fails is never invoked with PR content.

| Condition | Classification |
|---|---|
| Exit 0 and E-08 returns `Valid` | valid `Verdict` |
| Exit 0 without verdict, or E-08 returns `Invalid` | `CANDIDATE_TERMINAL` |
| Exit 2 | `PROVIDER_TERMINAL` |
| Other non-zero exit or timeout | `TRANSIENT` |
| Spawn `OSError` | `CANDIDATE_TERMINAL` |

The published conformance suite runs paired clean/adversarial bundles covering diff, body and
comments, semantic paraphrases, and every authority mode. It requires identical non-defensive
evidence/findings plus a populated `Verdict.injection_attempts` only for the adversarial member.
`ATTEMPT_TIMEOUT_SECONDS = 1800`; timeout terminates the process group. A probe bundle contains only
the marker and must exit zero without a verdict.

## 4. Dependencies consumed

P-06 calls E-08 exactly as defined in [`CONTRACTS.md` §9](CONTRACTS.md#9-edge-signatures--one-per-e-nn-verbatim):

```python
def validate(*, path: Path, attempt_id: str) -> Valid | Invalid: ...
```

It calls `rqa.protocol.paths.matches(path, pattern)` only for risk/obligation selection. Its
E-06/E-15 calls are exclusively the `SupplyPort` methods in §2. `RecordWriter.append` writes plan,
bundle, attestation and panel entries; `AppendFailed` propagates.

## 5. Store

P-06 writes two job-local trees under `state_dir`:

```
jobs/<job>/bundle/          # atomically published after every bundle file is durable
jobs/<job>/harness/<NN>/    # verdict, usage sidecar, stdout/stderr and P-06 attestation
```

The bundle is staged beside its final directory and atomically renamed only after every file and manifest
is flushed. A failed assembly leaves no final bundle directory.

Every value whose bytes originate in PR facts is inside a per-bundle nonce envelope. This includes title,
body, labels, diff, changed-path names, check names, and every file byte. Text values are envelope-encoded
as text; arbitrary file bytes are losslessly base64 encoded and that representation is envelope-encoded.
The manifest contains only bundle-generated nonce, snapshot protocol hash, and hashes of already-enveloped
artifacts. Consequently no PR-derived byte is emitted outside an envelope.

E-19 requires provider-role separation and the paired behavioral conformance property in
`CONTRACTS.md` §12. Nonce envelopes preserve origin and prevent delimiter forgery; semantic
instruction resistance and mandatory `injection_attempts` are verified by the adapter suite, never
by lexical phrase matching.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `plan` | each `plan()` | all `Plan` fields: obligations, omitted, strategy, participants, risk_class, head_sha, snapshot_hash, protocol_hash, policy_version |
| `bundle` | once before selection | ready status with nonce/protocol hash/manifest, or incomplete status with reason |
| `attestation` | after each invocation | attempt id, attested route fields, effort, observed times/exit code, outcome/detail, and separately marked self-reported verdict identity |
| `panel` | every normal `run()` return | attempt ids, complete, incomplete_reason, and `evidence_cutoff` captured after the final attempt/consumption |

P-06 writes no lifecycle transition and does not mutate job status.

## 7. What P-06 does not do

* It does not judge obligations, decide a disposition, submit GitHub output, or mutate job state.
* It does not call a provider itself, probe routes, or manufacture fallback routes.
* It does not implement P-05 budgeting: it requests reservations and reports observed consumption through
  `SupplyPort`.
* It does not plan carried evidence or let a pending check corroborate/block/inherit anything; those are
  P-13/P-07 responsibilities under the shared check conclusions.
* It does not use `fnmatch`, `PurePath.match`, or any matcher other than P-04 `matches()`.

## 8. Tests that prove it

| # | Given | Then |
|---|---|---|
| T1 | identical facts, snapshot, and carry | `plan()` returns identical plans and records identical payloads |
| T2 | a reused obligation and otherwise eligible policy obligation | reused id is absent from `Plan.obligations`; `omitted[id] == "carried"` |
| T3 | non-carried obligations excluded respectively by risk and path | each has the corresponding deterministic omission reason; path selection calls P-04 `matches()` |
| T4 | successful first route and valid verdict | one reservation, invocation and consumption; returned complete panel has cutoff after the attempt; matching `panel` entry exists |
| T5 | candidate-terminal outcome | route excluded before next selection |
| T6 | provider-terminal outcome | family excluded before next selection |
| T7 | transient then success on the same route | two distinct reservations, two invocations and two consumption calls; no new route selection between them |
| T8 | second reservation for a transient retry refuses fallback | no second invocation; family excluded; selection advances |
| T9 | two transient invocations for one route | no third invocation; route excluded |
| T10 | `Refusal(incomplete|escalate)` | incomplete panel with `evidence_cutoff` after the last attempt, if any |
| T11 | `RouteUnavailable` before completion | incomplete exhausted panel and matching panel entry |
| T12 | finite routes and terminal outcomes | termination within finite routes plus one retry per invoked route |
| T13 | usage sidecar and separately none | consumption follows each invocation with the corresponding reservation |
| T14 | every PR-derived field and arbitrary binary bytes | no PR byte appears outside an envelope |
| T14b | a configured route whose harness has no built-in alias but carries a non-empty `command` | the generic external-command adapter runs it with the same bundle/protocol/output arguments and the same classification table; no RQA source change is required (RQA-FR-030, AC15) |
| T14c | a configured `command` route whose clean/adversarial conformance run fails, errors on spawn, or times out | classified `CANDIDATE_TERMINAL` at §3.2 step 2, excluded through the cursor, recorded, and **never invoked with PR content**; a passing run appends its conformance `attestation` once and is cached for the job |
| T15 | paired clean/adversarial diff, body and comment fixtures, including paraphrases, under every authority mode | identical non-defensive result; adversarial result contains a semantic `InjectionAttempt`; adapter registration fails otherwise |
| T16 | bundle assembly failure | no attempt/final bundle; shared `BundleFailure` returned |
| T4b | a per-model bound refuses the first reservation with `Refusal(fallback)` and the configured fallback then returns a valid verdict | the panel is complete, `bound_reached is True`, and the `panel` entry records it (RQA-FR-039) |
| T17 | append fails for plan, bundle, attestation or panel | `AppendFailed` propagates |

## 9. Requirements this part answers for

Accountable: RQA-FR-019, RQA-FR-030, RQA-NFR-001, RQA-NFR-002, RQA-NFR-003, RQA-NFR-014, and
RQA-NFR-015. The E-07 loop is finite and non-inventive: every failure advances the documented cursor or
returns a named incomplete outcome; every PR-derived byte reaches the harness only within the E-19 data
envelope.