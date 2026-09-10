---
status: Accepted
date: 2026-09-11
issue: launchpad-26/buzz#2217
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: none
---

# ADR-0065 — A harness RQA ships no adapter for runs from an operator-declared command, gated by the conformance pair

## Decision

A configured review route may carry **`command`**: an argv the operator writes into the managed
repository's own `.rqa/config.json`. A non-empty `command` resolves to the generic external-command
adapter rather than to a built-in one, so a conforming harness participates **by configuration, never
by an edit to RQA's source**. This is option **B** of
[`ADR-H`](../skills/review-queue-automation/architecture/adr-drafts/ADR-H.md), the architecture's
recommendation.

Eligibility is not admission to invocation. Both gates hold:

1. **P-05 §3.1 step 2** admits such a route to *probing* because the operator configured it — the
   literal "with the system's own source held constant" gate RQA-FR-030's fit criterion demands.
2. **P-06 §3.2 step 2** runs the published clean/adversarial conformance pair against that **exact
   argv** before any pull-request content reaches it. A pass appends an `attestation` recording the
   argv hash, protocol hash, suite id and result, and is cached for the job by
   `(argv_hash, protocol_hash)`. A failure, spawn error or timeout is classified
   `CANDIDATE_TERMINAL`: the route is excluded through the cursor, the failure is recorded, and
   candidate selection resumes. **A command whose conformance run has not passed is never invoked
   with PR content.**
3. A built-in adapter's registry membership already carries that proof and is not re-run.
4. `command` is **required** for a route whose harness RQA ships no alias for, and **rejected** for a
   built-in alias, so the two paths cannot be confused in a policy file.

**Option C — the same declaration held in an operator-owned file outside the reviewed repository —
remains the named fallback** if the residual below is later judged too wide.

## Context

AC15 of #2006 requires that a harness not built into RQA participates "by satisfying the published
interaction contract alone, with no change to RQA's own source", and RQA-FR-030's fit criterion
explicitly fails a run in which a transient patch admits the harness and is reverted afterwards.

The #2071 architecture as merged could not meet either. P-05's `route()` admitted a configured route
only when its `(harness, model)` pair was a key of `aliases.py` — a closed table owned by RQA's
source — so a fourth harness required an RQA source edit. A Codex review of the #2072 decomposition
found this; the repair landed in PR #2176, and a second review correctly objected that the repair was
a *decision about what RQA executes* rather than a contract-consistency fix, and belonged in an ADR
alongside ADR-0061…0064. That objection is why this record exists.

Option A — keep the closed registry and have third parties submit a pull request adding a built-in
adapter — is rejected because it *is* the source change AC15 forbids; the success criterion would go
permanently unsatisfied.

Affected parts: **P-05** (supply), **P-06** (harness interface), **P-03** (policy/config surface).
Requirements: RQA-FR-030, RQA-NFR-001, RQA-NFR-002, RQA-NFR-015.

## Consequences

- **Good.** AC15 and RQA-FR-030 are met as written, and the injection-conformance property is
  enforced rather than assumed: the gate runs against the operator's exact argv at first use, which is
  the only point at which it *can* run, since an operator-declared command does not exist when RQA is
  built.
- **Bad, stated plainly.** **RQA now spawns an executable named by a file inside the repository it is
  reviewing.** The conformance gate, the minimal environment, the absence of RQA and GitHub
  credentials and the nonce-envelope data role all still apply, and an unverified command never sees
  PR content — but *which binary runs* is no longer RQA's decision. Anyone who can edit a managed
  repository's `.rqa/config.json` can name a different binary, and the gate verifies the harness's
  injection behaviour, not the operator's intent in naming it. Option C would have kept AC15 met with
  a narrower blast radius, at the cost of a per-repository harness choice; it was not chosen.
- **Decomposition.** `Route.command`, P-05 §3.1 step 2's eligibility disjunct, P-06's `adapter_for`
  dispatch and the §3.2 step 2 conformance gate are contracts #2183 (reviewer supply) and #2184
  (harness panel) build to. Those lanes were filed against this option while it was open; this record
  settles them.

## Provenance

**This outcome was written by an AI agent exercising `launchpad/AGENTS.md` §5 delegated authority on
behalf of @tucktuck101**, whose instruction is quoted verbatim:

> theres a new ADR? eh just go with the recomendation and take this as my approval

**Deviation from `launchpad/decisions/README.md`, recorded here rather than below the conclusion it
qualifies:** that README requires the deciding human's instruction to be quoted verbatim *and* the
comment where they said it to be linked. **No such comment exists** — the instruction was given in an
agent session, which §5 rule 2 states is not a record. The same deviation was disclosed and accepted
for ADR-0061…0064. An auditor cannot reach the original instruction; this quotation is its only
surviving form, and its fidelity — including its typing errors, left intact — is the only control on
it.

**A second caveat belongs at the decision, not below it:** this ADR was raised *because* an
independent reviewer judged the change too consequential to settle in a pull-request body, and it was
then settled in one sentence without the residual being discussed. The recommendation is followed as
instructed. If the exposure above is unacceptable on reflection, option C is a contained change —
P-03's config surface and P-05's eligibility test — and is cheapest to make before #2183 and #2184
are built.

The argument is on [#2217](https://github.com/launchpad-26/buzz/issues/2217) and in
[`ADR-H`](../skills/review-queue-automation/architecture/adr-drafts/ADR-H.md).
