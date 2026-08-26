# Corpus schema compatibility

## Rule

Any change to `node.schema.json` or `relationships.schema.json` that **removes a field,
removes an enum value, or narrows a type** is breaking. A breaking change requires, in
the same pull request:

1. A dated entry below naming what changed and why.
2. A re-validation pass of every existing corpus node against the new schema before
   merge — a compatibility note that only describes the change without checking it
   against real nodes is a claim, not a check.

Additive changes — a new optional field, a new enum value, a new relationship type — are
not breaking and do not require an entry here, though noting them is welcome.

## History

### v1 — initial (2026-08-25, issue #622)

First version of `node.schema.json` and `relationships.schema.json`. No prior schema
existed to invalidate, so there is nothing to reconcile — this entry exists only to give
the version history a starting point.
