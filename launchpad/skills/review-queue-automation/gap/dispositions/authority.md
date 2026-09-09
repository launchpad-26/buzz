# RQA gap analysis — dispositions: authority

### U-AUTHORITY-01 — Per-repo, per-activity authority mode resolution

Disposition: rework
Requirements: RQA-NFR-017, RQA-FR-029, RQA-NFR-008, RQA-NFR-018, RQA-NFR-026
Root cause: built contrary (RQA-NFR-017, RQA-NFR-018); not built (RQA-FR-029, RQA-NFR-008, RQA-NFR-026)

Per-repository activity authority is required, and disabled defaults remain the intended baseline for the five activities RQA-NFR-026 can be evaluated against here — that met portion is the whole of what this entry claims for it. The responsibility must change shape: its activity vocabulary and enforcement do not cover the six required activities, merge is absent, and malformed authority input can raise rather than fail closed. That merge absence is also why RQA-NFR-026 reads `partial gap` / `not built` rather than `fit`, under the maintainer's 2026-09-08 ruling that an activity the system cannot perform at all does not count as defaulting to disabled. Retain the intent of independent repository/activity resolution, not this incomplete activity model or its widening failure path.

### U-AUTHORITY-02 — GitHub auth token discovery, proven-capability probing and capability-bounded downgrade

Disposition: rework
Requirements: RQA-NFR-024, RQA-NFR-030
Root cause: not built (RQA-NFR-024); built contrary (RQA-NFR-030)

Credential acquisition and authority bounding are required responsibilities, but the current pipeline cannot inspect granted scopes and can adopt the operator-wide `gh auth token`, contrary to the per-repository permission ceiling. Rework it around the frozen credential floor and ceiling. Retain only the intent that proven capability may reduce configured authority; the present ambient-token discovery and repository-role proxy cannot establish either credential requirement.

### U-AUTHORITY-03 — Deterministic approval gate computation and disposition

Disposition: rework
Requirements: RQA-NFR-017, RQA-FR-011, RQA-FR-037, RQA-BR-011, RQA-FR-004
Root cause: built contrary (RQA-NFR-017, RQA-FR-011, RQA-FR-037); not built (RQA-BR-011); - (RQA-FR-004)

Approval evaluation remains required and its explicit conjunction of authority, evidence, and policy state is the right intent. It must be reworked because the same responsibility permits a human authorization to persist an eligible decision without re-establishing the unsatisfied obligations or their evidence, producing the successful outcome RQA-FR-011 and RQA-FR-037 forbid. Policy hashing may remain an input, but eligibility must no longer have a bypass outside the governing gate semantics. RQA-FR-004 is `fit` (`gap/register/fr.md:204`) and carries no root cause; whole-config policy hashing is retained as the input that binds a decision to the policy in force. RQA-NFR-017's contrary execution is not in this unit: `gap/register/nfr.md:414` locates it at `scripts/dispatcher.py:1316`, which runs the reviewer panel with no authority check on the review activity at all — a dispatch-cluster site, distinct from this unit's own already-conjunctive `authority.approve` check at `scripts/approval_evaluate.py:151`.

### U-AUTHORITY-04 — Deterministic request-changes action gate

Disposition: keep
Requirements: RQA-FR-009, RQA-BR-004, RQA-FR-037, RQA-NFR-010
Root cause: not built (RQA-BR-004); built contrary (RQA-FR-037, RQA-NFR-010); - (RQA-FR-009)

Keep the named conjunction for RQA-FR-009: live request-changes authority, verified blocker evidence, assurance, exact current-head handling at its production caller, and final revalidation produce a reproducible action decision rather than a reviewer-selected severity outcome. A materially simpler boolean or severity-only switch would omit these independently necessary inputs and make the blocking result non-reproducible. RQA-FR-009 is `fit` (`gap/register/fr.md:176`) and carries no root cause. The mapped conflicting causes arise in the human-approval bypass and ledger handling, not in this gate.

### U-AUTHORITY-05 — Durable SQLite human-approval request queue

Disposition: rework
Requirements: RQA-BR-007, RQA-FR-026, RQA-FR-013, RQA-BR-011, RQA-FR-011, RQA-FR-037
Root cause: not built (RQA-FR-026, RQA-FR-013, RQA-BR-011); built contrary (RQA-FR-011, RQA-FR-037); - (RQA-BR-007)

A durable, revision- and policy-bound human-decision queue is required, but its persisted records allow empty rationale and do not preserve the approving actor and basis on the authoritative decision record. Rework the responsibility while retaining the specific stale-decision mechanism: approval usability is bound to matching `head_sha`, `policy_hash`, and expiry, and pending requests supersede on either mismatch. That mechanism prevents an old decision authorising a different revision without inheriting the incomplete evidence model. RQA-BR-007 is `fit` (`gap/register/br.md:141`) and carries no root cause; the four-key idempotent enqueue is part of what satisfies it.

### U-AUTHORITY-06 — Human decision CLI: inspect and decide pending requests

Disposition: rework
Requirements: RQA-FR-013
Root cause: not built

A documented operator surface for recording a human assurance decision remains necessary, but requiring an actor alone does not meet RQA-FR-013 because the basis may be empty. Rework the decision operation so the required named human and substantiated basis travel together into the authoritative record. Retain the responsibility of an explicit human command, not the current CLI contract that permits an ungrounded decision.

### U-AUTHORITY-07 — Human-authorized resume through the guarded approval executor

Disposition: rework
Requirements: RQA-FR-011, RQA-FR-037, RQA-NFR-010, RQA-FR-028, RQA-BR-011, RQA-FR-013
Root cause: built contrary (RQA-FR-011, RQA-FR-037, RQA-NFR-010, RQA-FR-028); not built (RQA-BR-011, RQA-FR-013)

Human-authorized execution must remain guarded by current-state checks, but this path currently turns authorization into an eligible approval even when the gates that prevented success remain unsatisfied. Rework it so a human decision cannot manufacture success without the recorded substantiated basis the requirements require. Retain the intent and the specific shared-executor discipline: refuse a non-pending or stale job, resolve only a current approval, and use the guarded mutation executor rather than a separate unverified mutation path. RQA-FR-028's contrary execution is not in this unit's files: `gap/register/fr.md:188` places it in the non-live, advisory and shadow terminal branches of `scripts/dispatcher.py`, with `scripts/advisory.py`, `scripts/authority.py`, `scripts/config.py` and `scripts/github_mutate.py:99-113` — none of them `scripts/human_cli.py`, this unit's own resume path.

### U-AUTHORITY-08 — Guarded APPROVE mutation execution with mandatory pre/post REST checks

Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037, RQA-NFR-010, RQA-BR-007, RQA-NFR-017
Root cause: built contrary (RQA-FR-011, RQA-FR-037, RQA-NFR-010, RQA-NFR-017); - (RQA-BR-007)

Keep the guarded executor: it loads the decision by identifier instead of caller payload, refuses absent or failed pre-mutation REST checks, and records a final state only after post-mutation verification distinguishes verified, failed, and uncertain outcomes. No materially simpler request sender can meet RQA-NFR-010, because accepting a response without independent confirmation leaves an ambiguous authoritative result; bypassing the approval-only entrypoint would also defeat the separate approval authority boundary. RQA-BR-007 is `fit` (`gap/register/br.md:141`) and carries no root cause. Each mapped contrary cause is located outside this executor, at three distinct sites: the human-eligibility path for RQA-FR-011 and RQA-FR-037 (`gap/register/fr.md:186`, `gap/register/fr.md:190`, citing `scripts/human_cli.py` and `scripts/approval_evaluate.py:352-358`); the dispatcher ledger's `_ledger_record` for RQA-NFR-010 (`gap/register/nfr.md:400`); and the unchecked reviewer-panel authority gate at `scripts/dispatcher.py:1316` for RQA-NFR-017 (`gap/register/nfr.md:414`), where this unit's own `scripts/github_mutate.py:99-113` appears only as corroborating context for the absent merge activity, not as the site of the violation.

### U-AUTHORITY-09 — Fixed-event GitHub mutation transport (comment / request-changes / issue / labels / reviewer-request / thread-reply / assignee)

Disposition: rework
Requirements: RQA-NFR-017, RQA-BR-007, RQA-NFR-010
Root cause: built contrary (RQA-NFR-017, RQA-NFR-010); - (RQA-BR-007)

Mutation transport is required, but non-approval review mutations make verification caller-optional and let a probe failure escape without an unambiguous transport outcome. Rework the transport so its authority and final-state obligations hold at the transport boundary. Retain the specific fixed-event registry and deterministic `(job, operation)` mutation identifier: fixed GraphQL events prevent callers from selecting a more-authoritative review event, and the stable identifier prevents a retry from duplicating a completed mutation. RQA-BR-007 is `fit` (`gap/register/br.md:141`) and carries no root cause; that deterministic identifier is the mechanism its row credits to this unit.

### U-AUTHORITY-10 — Bulk read-only GraphQL queue-inventory transport

Disposition: keep
Requirements: RQA-NFR-010
Root cause: built contrary (RQA-NFR-010, in the ledger path rather than this inventory transport)

Keep the fail-closed inventory mechanism for RQA-NFR-010: connection and pull-request page caps raise instead of silently truncating, and null repositories, GraphQL errors, missing heads, and file-count mismatches are refusals. No materially simpler bulk query can suffice, because returning a partial queue or file set makes a downstream decision appear authoritative despite omitted review inputs. The requirement's contrary root cause is the dispatcher ledger's swallowed write failure, not this read transport.

### U-AUTHORITY-11 — Allowlisted per-PR REST read transport and its ETag-cached backing GET

Disposition: keep
Requirements: RQA-NFR-010
Root cause: built contrary (RQA-NFR-010, in the ledger path rather than this REST transport)

Keep the allowlisted per-PR read surface for RQA-NFR-010: each decision-critical read has a bounded method, `changed_files` is paginated, and incomplete or inaccessible data becomes an error rather than an apparently complete result. No materially simpler generic GET surface suffices: it would both dissolve the constrained read boundary and permit page-one data to be treated as the whole PR, yielding a partially authoritative downstream outcome. The cited ETag backing behavior is owned by its defining cluster; this unit retains the fail-closed wrapper contract.

### U-AUTHORITY-12 — Human notification delivery (file/command/none transports)

Disposition: bin
Requirements: RQA-FR-025, RQA-BR-013
Root cause: not built (RQA-FR-025); built contrary (RQA-BR-013)

Remove notification delivery. No frozen requirement obliges a push transport or an immediate human-facing notification: RQA-FR-025 is the only requirement row citing this unit for what it fails to do (`gap/register/fr.md:193`) and needs only a durable record, which the human-request queue supplies without any delivery at all, while RQA-BR-013 is the row this unit's own reachable code contradicts (`gap/register/br.md:149`). RQA-FR-026's escalation obligation is discharged by the queue record naming its cause, not by delivering it. This mechanism instead sends routine gate failures and protected-trigger denials through the same transport with no urgency or routing distinction, producing the immediate interruption RQA-BR-013 forbids. No other register row depends on it — searching all three registers returns two hits, both already named above; command run from `launchpad/skills/review-queue-automation/gap/` and its output verbatim:

```
$ python3 -c "
for p in ('register/br.md','register/fr.md','register/nfr.md'):
    for i,l in enumerate(open(p),1):
        if 'U-AUTHORITY-12' in l: print(f'{p}:{i}')"
register/br.md:149
register/fr.md:193
```

Binning loses the optional file and command delivery transports; nothing in the frozen specification depends on that responsibility.
