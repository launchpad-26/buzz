# P-07 Judgement — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-07 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Turn the selected plan, carried evidence, validated panel verdicts,
pinned policy, and canonical captured facts into one deterministic current-job decision basis.

**Depends on.** ADR-G ([#2160](https://github.com/launchpad-26/buzz/issues/2160), assumed) for exact-remedy candidate boundaries. Not ADR-D/E/F.

## 1. Modules

```
rqa/judgement/
  __init__.py        re-exports: judge, render, Judgement, Assurance, JudgementError
  judge.py           E-09 algorithm and disposition selection
  evidence.py        cutoff-bounded obligation-state and assurance calculation
  findings.py        corroboration, envelope detection, and mechanical classification
  checks.py          captured-check attribution and evidence completeness
  render.py          pure GitHub review/comment body renderer
```

No other RQA module imports from `rqa.judgement` except through `__init__`. P-07 imports shared types
only from their owners and `rqa.record`. It consumes no GitHub edge: P-02 captures checks through E-23
and provides them in `Facts`.

## 2. Types

`Assurance`, `Judgement`, `CarriedEvidence`, and `CarryOver` are defined only in
[`CONTRACTS.md`](CONTRACTS.md) §6. In particular, `Judgement.obligations` is exactly
`set(plan.obligations) | {c.obligation_id for c in carry.reused}`, and `Judgement.reused_from` is the
predecessor job id when any evidence was carried. P-07 does not redefine them.

`Job`, `Plan`, `PanelResult`, `Attempt`, `Attestation`, `Verdict`, `Finding`, `InjectionAttempt`,
`Remedy`, `EvidenceState`, `Category`, both category groups, `Facts`, captured-check constants,
`Snapshot`, `Decision`, `EscalationCause`, `RecordWriter`, `Entry`, and `AppendFailed` are consumed
exactly as defined in [`CONTRACTS.md`](CONTRACTS.md) §§1–8.

```python
class JudgementError(Exception):
    """Programming error or internally inconsistent supposedly validated input."""
```

P-07 reads the checks frozen in `Facts`; it never fetches them. Evidence cutoff is exclusively
`panel.evidence_cutoff`, captured by P-06 after the final attempt. `facts.fetched_at` only timestamps
the coherent GitHub snapshot. Pending checks never corroborate, block, or inherit.

## 3. Entry point(s) — E-09

```python
def judge(*, job: Job, plan: Plan, panel: PanelResult, carry: CarryOver, facts: Facts, snapshot: Snapshot,
          decision: Decision | None, record: RecordWriter) -> Judgement: ...
```

**Behaviour, in order.** Every normal branch appends exactly one `judgement` entry and returns;
`AppendFailed` propagates. The function is deterministic, preserves supplied stable order to break
ties, and reads neither clock, filesystem, configuration, environment, network, nor a neighbour.

1. Validate programming invariants: facts identify the job; both check sequences and timestamps are
   present; `panel.complete is True`; `panel.incomplete_reason is None`; every attempt's
   `attestation.ended_at <= panel.evidence_cutoff`; plan/carried ids are unique/disjoint; every
   verdict is validated; and a decision's `substantiates` id is in the universe. Any violation raises
   `JudgementError` and appends nothing. A late attempt is corrupt panel input, never silently omitted.
2. Set the obligation universe to exactly `set(plan.obligations) | {c.obligation_id for c in
   carry.reused}`. Do not add a policy obligation merely because it exists in
   `snapshot.policy.obligations`; an obligation omitted by the plan is absent from the judgement.
   Resolve each universe member in plan order, followed by carried-only ids in carry order.
3. A carried `CarriedEvidence` yields `VERIFIED` directly, with its `source_job`,
   `source_judgement_seq`, and `source_attestations` retained as provenance. Set `reused_from` to
   `carry.source_job` when at least one carried item exists, otherwise `None`. A carried obligation is
   not changed by a pending check or re-decided from stale panel material.
4. For a non-carried obligation, consider only verdicts in `panel.attempts`; the invariant above
   proves all ended by the recorded panel cutoff. A matching non-empty recorded decision overrides
   only its `substantiates` obligation. Otherwise choose, in order: `VERIFIED` for qualifying positive
   evidence, `CONTRADICTORY`, `FAILED`, `UNAVAILABLE`, `INCOMPLETE`, `NOT_VERIFIED`, then `UNKNOWN`.
   Evidence depending on a pending cited check supplies no positive evidence and yields `INCOMPLETE`
   unless independent evidence verifies the obligation.
5. Read attribution solely from captured checks whose immutable `observed_at <=
   panel.evidence_cutoff`; later checks are excluded from all judgement inputs. For each eligible
   head check in `FAILING`, classify it `inherited` only when an eligible same-name merge-base check
   is also failing; otherwise classify it `pr`. `UNSETTLED`/`PASSING` checks have no attribution.
   An inherited failure remains visible but cannot corroborate or block.
6. Take findings only from panel verdicts. A supposedly validated malformed value raises
   `JudgementError`. A finding fingerprint is
   `(tuple(sorted(category.value for category in categories)),
   location.path.casefold().strip(), location.line)`. It is corroborated by two distinct attested
   provider families or by a cited PR-attributed failing head check; pending, passing and inherited
   checks never corroborate.
7. A corroborated finding blocks when any category blocks under policy. It is a **remediation
   candidate** only when its categories are a subset of both `MECHANICAL_GROUP` and the configured
   mechanical categories, its exact remedy tool is allowed, a remedy is present, and
   `behaviour_changing is False`. `False` is only a conservative eligibility veto: P-10 must still
   prove actual before/after behavior equivalence with the registered `ToolSpec`. A mixed substantive
   finding is never a candidate; `None` is treated as behavior-changing.
8. For every `InjectionAttempt` in every panel verdict, add a synthetic, immediately corroborated,
   policy-independent blocking `EVIDENCE` finding. Its deterministic id covers source attempt, field,
   span hash and reason; its evidence contains only the hash/reason, never the untrusted bytes. Also
   add such a finding for an unbalanced or forged nonce envelope detected in any PR field. Do not use
   phrase lists or semantic keyword matching.

   As defense in depth, when fewer than two eligible provider families report an all-`VERIFIED`,
   zero-finding result for an evidence-bearing changed path, add `suspicious_clean_verdict` as a
   blocking `EVIDENCE` finding. A panel with independent second-family evidence does not satisfy that
   predicate. Synthetic EVIDENCE findings are never remediation candidates.
9. Compute `Assurance` over the universe only: `required` is the assurance value for
   `plan.risk_class`; `achieved = floor(required * verified / total)`, with an empty universe yielding
   `(0, 0)`. Add `CONFLICTING_JUDGEMENT` for contradictory evidence,
   `REQUIRED_INFORMATION` for unavailable or incomplete evidence, `UNRESOLVED_DECISION` for failed
   evidence or behaviour-changing findings, and `EVIDENCE_GAP` for unknown/not-verified evidence or
   assurance shortfall. Deduplicate causes in first-occurrence order.
10. Select disposition in order: blocking finding → `request_changes`; behavior-changing finding or
    escalation cause → `escalate`; remediation candidate → `remediate`; otherwise `approve`.
    Approval requires every universe member verified, achieved assurance, and no injection/envelope/
    suspicious-clean finding. An empty carry-only panel follows the same computation and records a
    current-job judgement.
11. Construct the shared `Judgement`, including `reused_from`, append the §6 payload, and return it.

```python
def render(judgement: Judgement) -> str:
```

`render` is pure and byte-identical for the same judgement. It lists corroborated findings in retained
order, each category set, blocking marker, provenance, every judged obligation/state, inherited check
attribution, assurance, and `reused_from`; all values are escaped as data.

## 4. Dependencies consumed

```python
# E-13, rqa.record (P-12)
RecordWriter.append(job_id, kind, payload) -> Entry
```

P-07 calls `append` exactly once for every normal `judge` call. `AppendFailed` always propagates.
P-07 has no E-14 dependency: P-02 fetched both check sets into `Facts` through E-23.

## 5. Store

None. P-07 owns no database table, file, cache, or mutable module state. Its durable output is the
P-12 `judgement` entry, so the carry-only path has the same current-job audit object as a panel run.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `judgement` | every normal `judge()` return, before it returns | `snapshot_hash`, `protocol_hash`, `cutoff` (`panel.evidence_cutoff`), `facts_fetched_at`, `obligations` (id → state), `reused_from`, `carried_provenance`, `contributing_attempts`, `decision`, `findings` (including injection/envelope synthetic findings), `corroborated`, `blocking`, `attribution`, `assurance`, `remediation_candidates`, `escalation_causes`, `disposition`, `rendered_body` |

The payload contains the current-job materialisation even when it was formed wholly from carry-over.
It does not write a transition, mutate job status, write an escalation, or post a review.

## 7. What P-07 does not do

- Does not validate `verdict.json`; P-04 does that before an `Attempt` reaches P-07.
- Does not invoke a harness, plan, route, reserve capacity, or decide whether more review is available.
- Does not call E-14, GitHub, a path matcher other than `rqa.protocol.paths.matches`, or use
  `fnmatch` or `PurePath.match`.
- Does not make a GitHub mutation, determine authority, hold a grant, claim a lease, or change job state.
- Does not run a mechanical tool, decide a remediation grant, raise an escalation, or let a decision
  satisfy more than its one named obligation.

## 8. Tests that prove it

Each test uses immutable `Facts`, validated attempts, a frozen `Snapshot`, `Plan`, `CarryOver`, and a
fake `RecordWriter`.

| # | Given | Then |
|---|---|---|
| T1 | identical complete inputs passed twice | byte-identical judgement/rendering and equivalent entries |
| T2 | a policy obligation omitted by `plan.obligations` | it is absent from `Judgement.obligations` and assurance |
| T3 | an attempt ends after `panel.evidence_cutoff` | `JudgementError`; no evidence is silently dropped |
| T4 | empty complete panel with cutoff equal to facts capture, no regenerated obligations, complete carried evidence | current-job judgement approves normally and records its cutoff |
| T5 | required non-carried obligation lacks positive evidence | `UNKNOWN`; not approve |
| T6 | evidence depends only on pending check | `INCOMPLETE`; pending is not attributed/corroborating/blocking |
| T7 | same failing check at head/base plus pending check | inherited excluded; pending ignored |
| T7b | same-head resume facts contain a failing check completed after panel cutoff | excluded from attribution, corroboration and blocking |
| T8 | corroborated multi-category finding with one blocking category | blocking |
| T9 | mechanical plus substantive categories | never remediation candidate |
| T10 | otherwise mechanical with assertion `None` or `True` | not a candidate |
| T11 | each verdict reports an `InjectionAttempt` | deterministic immediately blocking EVIDENCE finding retains hash/reason, never raw bytes |
| T12 | forged/unbalanced envelope | deterministic immediately blocking EVIDENCE finding |
| T13 | single-family suspicious clean result, then equivalent two-family panel | first blocks; second does not synthesize suspicious-clean |
| T14 | same valid finding fingerprint from two families | corroborated |
| T15 | append failure | propagates |
| T16 | invalid panel cutoff/completeness, duplicate ids, invalid finding, or decision outside universe | `JudgementError`; no entry |

## 9. Requirements this part answers for

Accountable: RQA-BR-004, RQA-BR-008, RQA-BR-009, RQA-BR-014, RQA-FR-009, RQA-FR-010,
RQA-FR-011, RQA-FR-014, RQA-FR-015, RQA-FR-036, RQA-FR-037, RQA-NFR-016, RQA-NFR-031.

- **RQA-BR-004 / RQA-FR-009** → multi-category corroboration and policy blocking, T8.
- **RQA-BR-008 / RQA-FR-010 / RQA-FR-011** → bounded obligation universe, cutoff evidence, carry
  materialisation, and fail-closed approval, T2–T5.
- **RQA-BR-009 / RQA-FR-014 / RQA-FR-015 / RQA-FR-036** → captured-check attribution and unsettled
  semantics, T6–T7.
- **RQA-BR-014 / RQA-FR-037** → assurance and non-success for unsatisfied evidence, T2–T6.
- **RQA-NFR-016** → structural envelope and suspicious-clean-verdict findings, T11–T12.
- **RQA-NFR-031** → exact shared remedy and conservative multi-category/behaviour classification,
  T9–T10.
