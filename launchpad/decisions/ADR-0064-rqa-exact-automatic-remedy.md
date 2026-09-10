---
status: Accepted
date: 2026-09-11
issue: launchpad-26/buzz#2160
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: none
---

# ADR-0064 — RQA may run closed tools on exact files, never a model-supplied patch

## Decision

The only remedy review-queue-automation (RQA) may apply and push itself is **a closed-set tool run
over exact named files, with behaviour-neutrality proved on the resulting bytes**. This is option
**(a)** of [`ADR-G`](../skills/review-queue-automation/architecture/adr-drafts/ADR-G.md), the
architecture's recommendation. **No model-supplied patch ever reaches a branch.**

A remedy is `Remedy(tool, paths, check)`, and P-10 refuses unless every one of these holds:

1. **`tool`** is one member of the closed tool set, which names its supported extensions and its
   exact fix and check argv. **Repository policy may remove tools; it may never add one or weaken the
   oracle** (RQA-NFR-031).
2. **`paths`** are unique, normalized, repository-relative **changed files** — never patterns — each
   present in the fact set, each suffix-accepted by the selected tool, confined beneath a fresh
   worktree, and **including the finding's own location**.
3. **The tool's registered check passes**, the diff scope is exactly those paths, and re-running is a
   **fixpoint**.
4. **A parser-derived semantic fingerprint is identical before and after.** A parse error, an
   unsupported construct, or a changed fingerprint refuses the remediation.
5. **Eligibility vetoes are vetoes only.** A substantive finding category, or a reviewer's
   `behaviour_changing` assertion that is not `false`, disqualifies a candidate — but a `false`
   assertion never *proves* neutrality; only the oracle does.
6. **Import-fixing stays excluded**, because reordering imports can change import-time behaviour.
7. **The push is exact and non-forced**, to the validated pull-request head repository and ref only,
   under a `remediate` grant bound to that job, snapshot and the finding's complete category set.

## Context

AC09 of #2006 lets RQA apply and push a fix "where the finding is mechanical — its remedy is
deterministic and does not change the system's behaviour", and RQA-NFR-031 forbids repository policy
from widening that definition. RQA-BR-006 speaks of a finding "accompanied by its exact remedy". The
open question was what *form* that remedy may take.

This is where the line falls between model output RQA merely records and model output RQA turns into
commits on a contributor's branch — the largest new exposure Security bullet 3 names, and a risk
decision the maintainer owns rather than the architecture.

Both rejected options fail on verifiability, not on convenience. Reviewer-supplied patches (b) are
deterministic to *apply* but not to *produce*, so two reviews of the same head may push different
commits; and whether a patch changes behaviour is precisely the judgement #2006 says must go to a
human. Allowlisting paths (c) narrows the blast radius without making patch semantics verifiable.

Affected parts: **P-10** (remediation), **P-07** (judgement), **P-08** (authority gate).
Requirements: RQA-BR-006, RQA-FR-017, RQA-NFR-019, RQA-NFR-031, RQA-NFR-033.

## Consequences

- **Good.** Behaviour-neutrality is checked on the actual bytes rather than inferred from a formatter
  label or a trusted model Boolean. Untrusted model output cannot become an arbitrary branch
  mutation, which is the failure mode this decision exists to prevent.
- **Bad, stated plainly.** **RQA fixes strictly less.** Every automatic remedy needs a registered
  tool with a parser-based oracle, so any finding whose fix is real but unformalised goes to a human
  instead — including cases a contributor would consider obviously mechanical. Adding a tool is
  deliberate work: extensions, fix and check argv, and a semantic fingerprint implementation.
- **Decomposition.** E-10's payload (`tool_id` rather than a patch), P-07's mechanical-classification
  rule, and P-08's `remediate` grant categories are all shaped by this choice, so the P-10 lane could
  not be cut before it was ratified. It can be cut now.

## Provenance

**This outcome was written by an AI agent exercising `launchpad/AGENTS.md` §5 delegated authority on
behalf of @tucktuck101**, who ruled on all four RQA architecture ADRs (#2157, #2158, #2159, #2160) in
one instruction, verbatim:

> urgh just go with the recomendations, record the adr files we need and submit a pr for them as a batch.

**Deviation from `launchpad/decisions/README.md`, recorded here rather than below the conclusion it
qualifies:** that README requires the deciding human's instruction to be quoted verbatim *and the
comment where they said it to be linked*. **No such comment exists.** The instruction was given only
in an agent session, which §5 rule 2 states is not a record — "not addressable, not durable, and not
readable by whoever audits this later". Offered the choice between posting the instruction as a
comment first and proceeding without one, @tucktuck101 selected "I proceed now, quoting this session
verbatim", with the deviation disclosed in every record and in the pull request. An auditor therefore
cannot reach the original instruction; this quotation is its only surviving form.

**This is the highest-risk of the four decisions**, and it was ruled on collectively rather than
individually. It is recorded as instructed; a maintainer who wants the risk weighed on its own terms
should revisit it before the P-10 lane is implemented, not after.

The argument is on [#2160](https://github.com/launchpad-26/buzz/issues/2160) and in
[`ADR-G`](../skills/review-queue-automation/architecture/adr-drafts/ADR-G.md).
