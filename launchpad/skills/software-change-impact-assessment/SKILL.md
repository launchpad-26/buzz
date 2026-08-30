---
name: software-change-impact-assessment
description: Assess proposed software changes with an evidence-backed Markdown report, especially upstream-to-downstream Git comparisons. Use when humans need material behaviour, architecture, interface, data, dependency, CI/CD, security, operational, overlap, conflict, risk, and verification impact before acceptance. Assessment only: never synchronize, merge, approve, deploy, or enforce policy.
---

# Software Change Impact Assessment

Produce a concise, reproducible Markdown assessment—not a changelog and not a merge decision. Read the linked references before analysis; use repository conventions when they add context, but do not silently change the report contract.

## Non-negotiable boundaries

- Establish an immutable baseline and incoming revision before interpreting changes. Record repository identities, branches/tags, SHAs, merge-base where applicable, and timestamp.
- Separate **Evidence**, **Interpretation**, and **Uncertainty**. Every material conclusion points to files, commits, commands, or authoritative repository documents.
- Missing or unavailable evidence is `UNKNOWN`; it is never a clean bill of health. Distinguish no detected artifact from no impact.
- Analyze upstream relative to downstream. Inspect downstream-only modifications, shared paths/components, assumptions, ADRs, policies, and consumers—not only textual overlap.
- Distinguish textual, semantic, and policy conflicts.
- Treat security, CI/CD, dependencies, and supply chain as first-class categories.
- Group low-level changes into meaningful themes. Do not dump the complete commit history into the report.
- Scale depth to significance: documentation-only changes can be short; authentication, trust-boundary, persistence, or runtime changes require focused evidence.
- Recommendation is advisory. Do not execute or authorize synchronization, merging, deployment, approval, scheduling, notification, or policy enforcement.

## Procedure

1. **Identify scope.** Verify both revisions exist. Capture exact source/downstream repositories, revisions, baseline/common revision, merge-base, comparison commands, and evidence availability. If a baseline cannot be established, stop interpretation at `UNKNOWN` and explain why.
2. **Measure shape.** Collect commit/file/rename/add/remove/line statistics, changed paths, top-level areas, and commit range. Treat volume as context only.
3. **Build change themes.** Read diffs and relevant surrounding code/configuration. Group related commits into behaviour-level themes; identify added, changed, removed, default, failure, compatibility, and deprecation effects.
4. **Classify impact.** Consider every category in `references/change-categories.md`: functional, architecture, API/interfaces, schema/data, configuration, dependencies/supply chain, build/toolchain, CI/CD, security/authentication/authorization/networking, deployment, operations/observability, testing, developer experience, documentation, and downstream overlap. Include relevant categories; mark materially important categories `UNKNOWN` when evidence is insufficient.
5. **Compare downstream.** Determine downstream-only changes and shared files/components. Trace changed upstream contracts or behaviour to downstream consumers, configuration, tests, documentation, and ADRs. Inspect semantic and policy conflicts even when Git merges cleanly.
6. **Assess security and supply chain.** Examine trust boundaries, identity/privilege, secrets, parsing/input, code execution, network exposure, auditability, workflow permissions and checkout, third-party actions, dependency sources/locks/licenses/findings/provenance. Interpret scanner output; do not invent vulnerabilities.
7. **Assess risk and attention.** Apply `references/risk-model.md`; provide qualitative rationale, not an opaque score. Identify required verification, owner-facing questions, reversibility, and unknowns.
8. **Write the report.** Use `references/report-template.md`. Put the most decision-relevant understanding in the Executive Summary. Use finding IDs (for example `CIA-SEC-001`) and the structure in `references/evidence-guidance.md`.
9. **Self-check.** Confirm every material finding has evidence and confidence; every unavailable evidence source is represented; provenance is reproducible; recommendation is advisory; scope boundaries are respected.

## Evidence collection guidance

Prefer standard Git and repository tools: `git rev-parse`, `git merge-base`, `git log`, `git diff --stat`, `git diff --name-status`, `git diff --find-renames`, file inspection, dependency/package-manager output, migration/schema inspection, workflow/config inspection, security scanner and test output when available. Record commands and their status in Evidence. If a command errors, report evidence status `ERROR` or `UNAVAILABLE`, not an inferred result.

**Completion criterion:** evidence sources, commands, statuses, and limitations are recorded or explicitly unavailable.

## Output contract

Return one Markdown **Software Change Impact Assessment** using the standard template. Use status values `CONFIRMED`, `STRONGLY_SUPPORTED`, `POTENTIAL`, `UNKNOWN`, `NOT_APPLICABLE` as appropriate; interface compatibility values `COMPATIBLE`, `POTENTIALLY_BREAKING`, `BREAKING`, `UNKNOWN`; and risk levels `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. A concise report may state `NOT_APPLICABLE` for irrelevant sections, but must not omit material uncertainty.

Read:
- [`references/report-template.md`](references/report-template.md)
- [`references/assessment-method.md`](references/assessment-method.md)
- [`references/change-categories.md`](references/change-categories.md)
- [`references/conflict-model.md`](references/conflict-model.md)
- [`references/evidence-guidance.md`](references/evidence-guidance.md)
- [`references/risk-model.md`](references/risk-model.md)
- [`references/examples.md`](references/examples.md)
