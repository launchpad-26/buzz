# RQA architecture — C4 view: dynamic flow of one review

> A view of the design described in [`architecture.md`](architecture.md). Read that first; this
> view is the step-by-step, cited form of its §4.


One scenario, end to end: a pull request appears (or gains a new head) on a managed repository and RQA
carries it to a terminal disposition. Follows the corpus `flow` template's section shape (flow
statement, sequence, diagram, outcome, boundary, scope) without corpus node machinery. Every step
names the part that performs it (`P-NN`, [`components.md`](components.md) §4) and the contract it
uses (`E-NN`, §6). The table in §4 is canonical; [`validate.py`](validate.py) reads it.

This is not a happy path. §3 reaches every one of RQA-FR-016's six dispositions, and traverses the
escalation-and-resume branch (RQA-FR-026, RQA-FR-027), the resource-bound-reached branch (RQA-FR-022,
RQA-FR-039), the no-configured-fallback stop (RQA-FR-038) and the mechanical-remediation cycle
(RQA-FR-017, RQA-FR-018).

## 1. Flow statement

**Trigger.** The OS scheduler launches `rqa tick` (E-21). **Actors.** The thirteen parts; GitHub; the
review harness; the operator as human decider. **Scenario.** A managed repository has an open pull
request whose head RQA has not reviewed. **Ends when** the job reaches `approved`, `merged`,
`changes_requested`, or a recorded `stopped`, or is `superseded` by a job for a newer head.

## 2. Invariants that hold at every step

- Every state change is a P-02 transition committed in one transaction with its `transition` entry
  (E-13). A failed append is a failed transition; the job goes to `stopped` with the append failure as
  its reason [RQA-NFR-010].
- No part other than P-02 changes `jobs.status`. Every other part returns a value.
- No action on GitHub, no harness invocation and no remediation happens without a `Grant` from P-08
  obtained for that action (E-04) [RQA-NFR-017].
- Every PR-derived byte the harness sees is inside the nonce envelope [RQA-NFR-015].
- The record is written by P-12 only; the harness's identity is an input P-06 attests [RQA-NFR-032].
- The credential is the operator's `gh auth token` (maintainer constraint); P-08 addresses no
  repository outside the configured set with it.

## 3. Sequence

Numbered steps are the main line; lettered steps are branches, each re-joining or terminating where
stated. Bracketed ids are the requirements the step is the observable point for.

1. **Tick.** The scheduler launches the process (E-21). P-01 takes the exclusive runtime lock; if held,
   exits as a named successful no-op. P-01 resolves each configured repository's `.rqa/config.json`
   through P-03; a repository with no valid config is refused by the admission gate and skipped, the
   refusal naming the reason and the onboarding command [RQA-NFR-018, RQA-NFR-006].
2. **Inventory.** For each admitted repository, P-01 asks P-09 for open pull requests (E-01). For each
   PR, P-01 upserts `pr_facts` and creates a job for `(repo, number, head_sha)` if none exists
   [RQA-BR-007]. If a job exists for the same PR at an older head, P-01 marks it `superseded` through
   P-02 and any open escalation on it is closed as superseded. Job → `queued`.
3. **Snapshot and review authority.** P-01 hands the job to P-02 (E-02) before any GitHub write; the job
   stays `queued`. P-02 asks P-03 for the pinned snapshot (E-03) — the
   snapshot hash is written on the job and never re-read [RQA-FR-004, RQA-NFR-005] — and asks P-08
   `grant(repo, review, snapshot)` (E-04). P-08 reads the credential (E-22), probes proven capability on
   this repository (E-16), and returns `Grant` or `Deny`. The `review` activity covers every write the
   review itself needs that is not one of the other five activities: the assignee lease claim and
   release, and nothing else.
   - **3a. Denied.** P-02 asks P-11 to raise an escalation with cause *authority requirement* (E-11):
     `queued` → `escalated` (**awaiting human judgement**). No lease is taken and nothing further runs.
     [RQA-NFR-026, RQA-FR-026]
4. **Claim.** Under the `review` grant, P-01 claims the GitHub-verified assignee lease (E-01
   `claim_lease`). P-02: `queued` → `claimed`. P-02 fetches the PR facts, diff, files and labels through
   E-23; they are the fact set every later step reads.
5. **Plan and carry-over.** P-02 asks P-06 to plan (E-07 `plan`) from the fetched facts and the snapshot's stated
   assurance (which obligations, which strategy, how many independent participants) [RQA-FR-019]. If a
   predecessor job exists, P-02 asks P-13 for the carry-over (E-05, with the head-to-head diff from E-23): obligations that diff
   does not invalidate are `reused` with their prior evidence state and reviewer attestation; the rest
   are `regenerated`. Both sets are recorded [RQA-FR-006, RQA-FR-007]. `claimed` → `planned`.
   - **5a. Nothing regenerated.** Zero harness invocations. P-02 constructs an empty complete panel
     whose cutoff is the already captured facts time, calls step 8 to write the current-job
     `judgement` with `reused_from`, then transitions `planned` → `judged`. The judgement plus no
     current-job `attestation` proves reuse [RQA-FR-005].
6. **Supply (inside the panel loop).** When work was regenerated, P-02 transitions `planned` →
   `reviewing` immediately before its one E-07 `run` call. P-06 owns everything until the panel is
   complete/exhausted. It asks P-05 for a route, then obtains a fresh reservation immediately before
   **each** harness invocation—including the one allowed same-route transient retry.
   - **6a. Route unavailable, fallback configured.** The cursor excludes what failed; P-05 returns the
     next configured route in the ladder; the record shows the substitution [RQA-FR-023]. Because the
     cursor only ever grows, the ladder is walked at most once.
   - **6b. Route unavailable, no fallback.** P-05 returns `RouteUnavailable`; P-06 records/returns an
     incomplete exhausted panel. P-02 transitions `reviewing` → `stopped`; nothing invents success.
   - **6c. Bound reached.** `Refusal(fallback)` advances past that family without invoking.
     `Refusal(incomplete|escalate)` records/returns an incomplete budget panel and P-02 stops. A retry
     reservation refusal follows the same branches; an earlier reservation never authorizes it.
     [RQA-FR-022, RQA-FR-039]
7. **Run (inside the panel loop).** P-06 builds one bundle from the coherent E-23 facts plus protocol,
   nonce-envelopes every PR byte, and passes it only in the provider's data role under the published
   E-19 contract. Adapters must pass the paired clean/adversarial injection suite; every verdict must
   include `injection_attempts`. P-06 attests the actual route, validates the verdict, reports
   consumption for its unique reservation, and advances until complete/exhausted. It captures and
   records `PanelResult.evidence_cutoff` only after the final attempt/consumption.
   - **7a. Invalid verdict.** Candidate-terminal; route excluded.
   - **7b. Provider failure.** Provider-terminal excludes family. First transient returns to
     reservation on the same route; second transient excludes it. No third invocation.
8. **Judge.** P-07 receives the complete panel and uses its recorded cutoff; `facts.fetched_at` remains
   only GitHub capture time. It materialises every planned/carried obligation, handles check
   attribution, multi-category corroboration and assurance, and turns every reported injection attempt
   or envelope break into an immediately blocking EVIDENCE finding. A suspiciously clean one-family
   result also blocks. It may identify a remediation candidate only for an exact non-substantive remedy
   whose policy/tool checks pass; the model's behavior assertion is a veto, not proof. P-10 proves the
   actual diff later. After the judgement record, the fresh path transitions `reviewing` → `judged`;
   carry-only transitions `planned` → `judged`.
9. **Act on the judgement.** P-02 reads the judgement and takes exactly one of the following.
   - **9a. Mechanical candidate, no blocking substantive finding.** P-02 obtains the remediation grant,
     transitions `judged` → `remediating`, and passes finding, facts and pinned snapshot to P-10.
     P-10 itself rejects disallowed forks/protected heads; validates every remedy target as an exact
     confined regular changed file; runs only the closed tool on those files; proves before/after
     semantic fingerprints equal; verifies exact scope, named check and fixpoint; then pushes only to
     the validated PR head ref without force. A refusal escalates; a push is observed as a new head on
     the next tick and reused evidence is recalculated.
   - **9b. A cause for escalation.** An unresolved decision, conflicting judgement between reviewers,
     evidence gap, required information, or authority requirement — including a behaviour-changing
     finding [RQA-NFR-033]. P-02 asks P-11 to raise it (E-11): `judged` → `escalated` (**awaiting human
     judgement**). No notification is pushed; a routine condition never reaches this branch
     [RQA-FR-025, RQA-BR-013, RQA-FR-026].
   - **9c. Obligations satisfied, or a blocking finding stands.** Continue at 10.
10. **Verdict authority.** P-02 asks P-08 `grant(repo, approve | request_changes, snapshot)` for the
    activity the judgement calls for (E-04).
    - **10a. Denied.** If `comment` is granted, P-02 has P-09 post the judgement's rendering — findings
      with categories, evidence states, achieved against required assurance — as a comment (E-12). Then
      P-11 raises *authority requirement*: `judged` → `escalated` (**awaiting human judgement**). The
      record states that no source-conforming next transition was available
      [RQA-NFR-007; ADR-D assumed; issue #2157].
    - **10b. Granted.** `judged` → `submitting`. P-09 submits the review (E-12) with mandatory pre-check
      (head unchanged, no newer job) and post-check (the submission is visible) [RQA-FR-028].
      CHANGES_REQUESTED: `submitting` → `changes_requested` (**blocked**). APPROVED: `submitting` →
      `approved` (**review-complete**).
11. **Merge.** From `approved`, if the snapshot configures merge-after-review, P-02 asks P-08
    `grant(repo, merge, snapshot)`; granted, P-09 merges (E-12): `approved` → `merged`
    (**review-complete**). Not configured or denied: the job rests at `approved` and the record says
    which [RQA-FR-029, RQA-NFR-008].
12. **Resume.** The human runs `rqa decide` naming the escalation, the actor and the basis (E-17). P-11
    records a `decision` entry with actor, basis and the obligation it substantiates [RQA-FR-013,
    RQA-BR-011] and signals P-02. What follows depends on the escalation's cause:
    - **12a. Evidence gap, conflicting judgement, unresolved decision, required information.** P-02
      re-enters at step 8 with the decision as a recorded input: P-07 re-evaluates, treating the
      substantiated obligation as satisfied by a named approval and re-running nothing else.
      `escalated` → `judged`, then step 9 [RQA-FR-027].
    - **12b. Authority requirement.** RQA is not permitted to act, so the human acts on GitHub and
      records what they did: `rqa decide --outcome approved|changes_requested`. P-02 verifies the
      submitted review is visible through E-23 with the same head, records the decision as the
      authoritative human outcome, and transitions `escalated` → `approved` or `changes_requested`
      directly. Step 10 is not re-entered [RQA-NFR-007; ADR-D assumed; issue #2157].
    - A decision is refused if the head or snapshot it was made against has moved.
13. **Release.** On every terminal transition and every stop, P-01 releases the lease. On the next tick,
    crash recovery releases any lease whose job is `stopped` or whose process is gone, and re-enters
    the job at its recorded state without re-deciding anything.

## 4. Internal states and the six dispositions

The disposition command (`rqa status`, E-17) answers from `jobs.status` and the latest `transition`
entry of the job for the PR's *current* head, with the entry's reason. `superseded` is never returned:
a superseded job is not the current head's job.

| internal state | FR-016 disposition | meaning | may transition to |
|---|---|---|---|
| `queued` | being reviewed | P-01 created the job; no lease yet | claimed, escalated (3a), superseded |
| `claimed` | being reviewed | lease held under the `review` grant, snapshot pinned, facts fetched | planned, escalated, stopped, superseded |
| `planned` | being reviewed | plan and carry-over recorded; reservation and route resolved | reviewing, judged (nothing regenerated), escalated, stopped |
| `reviewing` | being reviewed | one or more harness attempts in flight or complete | judged, escalated, stopped |
| `judged` | being reviewed | judgement entry recorded; awaiting an action decision | remediating, escalated, submitting, stopped |
| `remediating` | awaiting remediation | a `remediate` grant is held and P-10 is working or has pushed | superseded (new head observed), escalated, stopped |
| `escalated` | awaiting human judgement | an open escalation names its cause; nothing else runs for this job | judged (on `decide`, 12a), approved or changes_requested (on `decide`, 12b), stopped, superseded |
| `submitting` | being reviewed | a `review_submit` mutation is in flight | changes_requested, approved, escalated, stopped |
| `changes_requested` | blocked | CHANGES_REQUESTED submitted by RQA (10b) or by the human and recorded (12b); waiting for a new head | superseded |
| `approved` | review-complete | APPROVED submitted by RQA (10b) or by the human and recorded (12b); `merge` not configured or not granted | merged, superseded |
| `merged` | review-complete | merge performed under a `merge` grant | — |
| `stopped` | unable to progress | a recorded reason no transition was available; resumable by the next tick where the reason has cleared | claimed (on retry), superseded |
| `superseded` | — | a newer head has its own job; the disposition command answers for that job | — |

Every one of RQA-FR-016's six values appears in the table and is reached by a step in §3: being
reviewed (steps 2–8, 10b), blocked (10b), awaiting remediation (9a), awaiting human judgement (3a, 9b,
10a), review-complete (10b, 11), unable to progress (6b, 6c, and any append failure).

## 5. Diagram

```mermaid
sequenceDiagram
  autonumber
  participant T as OS scheduler
  participant I as Intake
  participant L as Lifecycle
  participant C as Policy
  participant G as Authority gate
  participant S as Reviewer supply
  participant H as Harness interface
  participant X as Review harness (the AI)
  participant J as Judgement
  participant A as GitHub adapter
  participant M as Remediation
  participant E as Escalation
  participant R as Record
  T->>I: a sweep starts
  I->>A: which PRs are open?
  I->>L: here is a new job for PR #N at commit X
  L->>C: give me this repo's pinned rules
  L->>G: may I review PRs on this repo?
  alt no
    L->>E: ask a human: RQA lacks authority here
    Note over L: escalated — awaiting human judgement
  else yes
    I->>A: claim the PR (assign myself)
    L->>A: fetch the diff, files, checks and labels
    L->>H: plan the review, then run the whole panel
    loop each attempt, until the panel is complete or every route is exhausted
      H->>S: which model next, and is there budget?
      H->>X: here is the evidence bundle; return a verdict
      H->>S: this is what it cost
    end
    alt every route exhausted, or a budget limit hit
      Note over L: stopped — unable to progress (retried next sweep)
    else panel complete
      L->>J: what does this evidence mean?
      J->>A: CI results for the PR head and for its base
      alt only a mechanical finding, and fixing is allowed
        L->>M: apply the fix
        M->>A: push one commit to the PR branch
        Note over L: remediating — awaiting remediation (re-judged next sweep)
      else something needs a human
        L->>E: ask a human, naming exactly what
        Note over L: escalated — awaiting human judgement
      else clear outcome
        L->>G: may I approve / request changes here?
        L->>A: submit the review
        Note over L: blocked (changes requested) or review-complete (approved)
        opt merge configured and allowed
          L->>A: merge
        end
      end
    end
  end
  E-->>L: a human answered — either re-judge with their input, or record the verdict they gave on GitHub
  L->>R: every one of the above is written down as it happens
```

## 6. Outcome

**Success path.** GitHub carries a submitted APPROVED (and a merge where configured); the job is
`approved` or `merged`; the record holds plan, carry-over, attestation per attempt, judgement with
every obligation's evidence state, the grant consulted for each action, and each mutation id;
`rqa explain` reconstructs every RQA-FR-012 element from it alone; the lease is released.

**Blocked path.** GitHub carries CHANGES_REQUESTED whose body lists only corroborated, categorised
findings; the job is `changes_requested`; the next head supersedes it and inherits every obligation the
new diff does not invalidate.

**Human path.** No notification was sent; `rqa status` reports *awaiting human judgement* with the
named cause; after `rqa decide`, the review continues from step 8 without a second harness run for
anything the decision did not touch.

**Stop path.** The job is `stopped` with a reason the next tick can test; the lease is released; no
verdict was submitted, no partial record was written as authoritative, no authority was widened, no
repository outside the configured set was addressed; a later tick where the reason has cleared
re-enters at `claimed`.

**Failure inside a step.** An append failure, a persistence error or an audit-write error is
converted at P-02's containment boundary into a safe stop for that job only; a programming error is
not converted and fails loudly; other jobs in the sweep continue.

## 7. Boundary

This document does not describe: the standing structure of any part (`components.md`); the container
or its state (`container.md`); external actors beyond naming them (`context.md`); the operator's
onboarding flow (`rqa onboard`, a one-step write of a starter config, not a review); the shadow,
backtest or calibration flows, which are binned; or the author-triage lane, which is not in the frozen
specification.

## 8. Scope and omissions

**This document covers** one review from tick to terminal disposition, every branch a requirement
names, the state table, and the outcome on every path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Timing: how long a job may rest in `escalated` or `stopped` | Repository governance; no frozen requirement bounds it |
| Panel width and independence rules per assurance profile | P-06's plan, from the snapshot; policy content |
| What the harness does between receiving the bundle and writing the verdict | The harness; outside the system boundary by RQA-FR-030 |

**Expected but not verifiable while drafting:** whether GitHub's review-submission pre-check (head
unchanged) can be made atomic with the submission; the design tolerates a race by superseding on the
next tick and never by re-deciding.
