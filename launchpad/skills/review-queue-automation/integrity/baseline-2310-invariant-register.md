# Workstream B — invariant mutation findings

## Evidence pin

- Issue snapshots: `issue-2310.md`, `issue-2313.md`, and `issue-2006.md`, retrieved 2026-09-16.
- Execution amendments: `prompt-amendments.md`.
- Implementation base: `4d64f0c4476ed6ab907b69809b96d5c4c2653df6`.
- Infrastructure commit tested: `59b3f03a57f434fc2c39f90d18c975d4abb5feb3`.
- Python: `/private/tmp/rqa-integrity-2310.ZyNTzQ/venv311/bin/python` (Python 3.11).
- Command (from `/private/tmp/rqa-integrity-2310.ZyNTzQ/invariants`):

  ```text
  . ./bin/activate-hermit
  /private/tmp/rqa-integrity-2310.ZyNTzQ/venv311/bin/python launchpad/skills/review-queue-automation/integrity/run_mutations.py
  ```

- Complete raw output: `/private/tmp/rqa-integrity-2310.ZyNTzQ/t3-B-initial.raw.txt` (777 lines; SHA-256 `0798e6972a1e7fb40fe2447fd05487c5b04e86a85bd54db7a60d3a2aa64b286c`).
- Isolation observed in raw output: source exported from the named commit with `git archive` to a disposable temporary tree, freshly copied once per mutation, and deleted on exit. Git context variables are scrubbed before Git and pytest subprocesses.

## Initial T3 result — preserve unchanged

Every named test passed on unmodified source. Every mutation anchor matched exactly once and every mutated Python file parsed. There were no timeouts, collection/import failures, stale anchors, or unrelated failures.

| Inventory ID | Initial result | Initial disposition |
|---|---|---|
| B-INV-001 | SURVIVED | Guard gap; investigate and repair after the shared pre-remediation checkpoint. |
| B-INV-002 | KILLED | Effective guard. |
| B-INV-003 | KILLED | Effective guard. |
| B-INV-004 | KILLED | Effective guard. |
| B-INV-005 | KILLED | Effective guard. |
| B-INV-006 | KILLED | Effective guard. |
| B-INV-007 | KILLED | Effective guard. |
| B-INV-008 | KILLED | Effective guard. |
| B-INV-009 | KILLED | Effective guard. |
| B-INV-010 | SURVIVED | Guard gap; investigate and repair after the shared pre-remediation checkpoint. |
| B-INV-011 | KILLED | Effective guard. |
| B-INV-012 | KILLED | Effective guard. |
| B-INV-013 | KILLED | Effective guard. |
| B-INV-014 | KILLED | Effective guard. |
| B-INV-015 | KILLED | Effective guard. |
| B-INV-016 | KILLED | Effective guard. |
| B-INV-017 | KILLED | Effective guard. |
| B-INV-018 | KILLED | Effective guard. |
| B-INV-019 | KILLED | Effective guard; this mutation reorders the real production `anchor_job_for` composition and the exact named test fails on the anchor/head assertion. |

Initial total: **17 killed, 2 survived, 0 errors**.

## Stable findings

### B-001 — remediation grant-first prose is not guarded against an early head-protection read

- Inventory: B-INV-001.
- Evidence: the mutation adds `facts.pr.head_protected` immediately before `_require_verified_grant(...)` in the real `remediate()` entry point. The named T1 test still passes.
- Classification: ineffective guard for an explicit ordering claim in `rqa/remediation/remediate.py`.
- Scope: bounded test/integrity repair; no intended product-behaviour change identified.
- Initial disposition: open. Do not repair until the lead releases remediation after the combined T1/T2/T3 pre-remediation run.
- Verification required: add an observable head-access trap to the existing real-function T1 path, rerun B-INV-001, and retain its original evidence above.

### B-002 — review-time spend sole-writer guard recognises only keyword-form appends

- Inventory: B-INV-010.
- Evidence: changing the authority gate's positional `record.append(job_id, "grant", ...)` to positional `"spend"` leaves `test_only_the_supply_spend_module_writes_a_spend_entry_for_a_review` green. Its regex recognises only `kind="spend"`.
- Classification: ineffective source guard for the explicit sole-writer claim in `rqa/supply/spend.py`.
- Scope: bounded test/integrity repair; production behaviour is not being changed.
- Initial disposition: open. Do not repair until the lead releases remediation after the combined T1/T2/T3 pre-remediation run.
- Verification required: make the guard recognise both positional and keyword `RecordWriter.append` forms without broad phrase matching, rerun B-INV-010, and retain its original evidence above.

### B-003 — infrastructure runner failure modes are explicitly fail-closed

- Evidence: `tests/test_rqa_invariant_mutation_runner.py` exercises inherited Git-context scrubbing, ambiguous/stale anchors, syntax-breaking mutations, baseline/timeout/collection/unrelated-failure classification, expected assertion matching, and exact pytest node validation.
- Classification: infrastructure verification, not a product finding.
- Disposition: implemented in commit `59b3f03a57f434fc2c39f90d18c975d4abb5feb3`; focused pytest: `5 passed`; fixture-free suite: `PASSED: 1446 test(s)`.

## Deferred input from Workstream C

C-005 reports final-tree surface guards that accept historical alternatives. Per the phase boundary, no existing guard was changed before the shared baseline. After release, add bounded mutation rows and repair those guards where Workstream C's exact evidence identifies a source-comment invariant in this inventory's scope.

