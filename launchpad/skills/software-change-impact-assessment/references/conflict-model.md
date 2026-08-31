# Conflict Model

Report the three conflict classes separately.

## Textual conflict

Git cannot combine changes automatically: overlapping hunks, add/add, delete/modify, rename, or equivalent merge/rebase conflict evidence. Record command/output and affected paths. A textual conflict is deterministic but not the complete risk.

## Semantic conflict

Git combines the text, but resulting behaviour may violate a downstream assumption. Look beyond shared files: changed lifecycle/state transitions, defaults, error handling, timing, resource limits, protocol meaning, schemas, or dependency contracts can affect untouched consumers. Label `POTENTIAL` unless runtime incompatibility is demonstrated by tests or stronger evidence.

## Policy conflict

Incoming behaviour contradicts an explicit downstream ADR, security/architecture/testing/operational policy, invariant, or product requirement. Cite the authoritative document and changed evidence. A policy conflict is distinct from a Git conflict and need not imply a code defect.

For each class state `CONFIRMED`, `POTENTIAL`, `NONE DETECTED`, or `UNKNOWN` with evidence availability. `NONE DETECTED` means the checked evidence contained no instance; it is not a guarantee.
