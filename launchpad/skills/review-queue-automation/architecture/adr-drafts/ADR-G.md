# ADR-G — What counts as an exact remedy RQA may apply itself

**Status:** decided 2026-09-11 — recommendation (a) accepted; recorded as [ADR-0064](../../../../decisions/ADR-0064-rqa-exact-automatic-remedy.md), which closes [issue #2160](https://github.com/launchpad-26/buzz/issues/2160). This draft is retained as the architecture's rationale, not as an open question.
**Parent:** [#2006](https://github.com/launchpad-26/buzz/issues/2006) · **Raised by:** #2071 architecture · **Decomposition-blocking:** **blocking**
**Parts affected:** P-10, P-07, P-08 · **Requirements:** RQA-BR-006, RQA-FR-017, RQA-NFR-019, RQA-NFR-031, RQA-NFR-033

## Question

AC09 lets RQA apply and push a fix "where the finding is mechanical — its remedy is deterministic and
does not change the system's behaviour", and RQA-NFR-031 says no repository policy may widen that
definition. RQA-BR-006 speaks of a finding "accompanied by its exact remedy". What *form* may that
remedy take for RQA to apply it?

## Why the architecture cannot settle it alone

The answer draws the line between model output that RQA records and model output that RQA turns into
commits on a contributor's branch. That is the largest new exposure Security bullet 3 names, and where
to draw it is a risk decision the maintainer owns.

## Options

| | option | determinism | behaviour-neutrality | consequence |
|---|---|---|---|---|
| (a) | **Closed formatters on exact files, with a registered behavior oracle.** `Remedy(tool, paths, check)` names one system tool, unique normalized repository-relative changed files (never patterns), and that tool's registered check. P-10 validates confinement/suffix/location, runs only those files, requires exact diff scope/check/fixpoint, and compares parser-derived before/after semantic fingerprints. A substantive category or non-false reviewer assertion vetoes eligibility but never proves neutrality. | Tool argv, files and oracle are closed and recorded. | Proved on the actual diff by the registered language parser; parse/unsupported/different fingerprint refuses. Policy may narrow, never add/weaken. | E-10 carries finding plus pinned snapshot; no model patch reaches a branch. |
| (b) | **Reviewer-supplied patches for mechanical-category findings.** The harness returns a patch; P-10 applies it. | Applying a given patch is deterministic; producing it is not, so two reviews of the same head may push different commits. | Cannot be verified: whether a patch changes behaviour is the judgement the specification says must go to a human. | E-10 carries a patch; model output reaches a branch. |
| (c) | Both, with (b) restricted to files a policy allowlist names. | As (b). | As (b), narrowed by path — still not verifiable. | As (b). |

## Recommendation — (a)

It is the only option where behavior-neutrality is checked on the actual bytes rather than inferred
from a formatter label or trusted model Boolean. P-10's closed registry names exact extensions,
fix/check argv and one parser-based semantic fingerprint per tool; any unsupported parse or changed
fingerprint refuses. Paths are exact changed files, confined beneath the fresh worktree, and the
finding location must be included. Policy may remove tools but cannot widen the set or oracle.
Import-fixing remains excluded because reordering can change import-time behavior.

## Why blocking

E-10's payload (`tool_id` versus a patch), P-07's mechanical classification rule and P-08's `remediate`
grant categories are all shaped by this choice; P-10's lane cannot be cut until it is ratified.
