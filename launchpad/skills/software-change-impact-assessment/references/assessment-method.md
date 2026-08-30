# Assessment Method

This is design guidance informed by ITIL 4 Change Enablement, NIST SP 800-53 CM-3/CM-4, NIST SP 800-218 SSDF, NIST SP 800-161, SLSA provenance concepts, OpenSSF secure-development guidance, and ISO/IEC 27002 change control and traceability. It is not certification or a compliance claim.

## Analysis loop

1. Fix the baseline and incoming SHA; preserve repository and command provenance.
2. Inventory scope and evidence availability.
3. Read the actual diff plus consumers, tests, manifests, workflows, ADRs, and policy.
4. Group changes into themes and classify impact.
5. Compare each theme with downstream customizations and assumptions.
6. Record findings as evidence → interpretation → impact/attention → uncertainty.
7. Rate risk using the qualitative model; explain drivers and counter-evidence.
8. Produce the report and run the self-check in SKILL.md.

## Theme quality test

A theme states the behaviour or contract that changed, why it matters, affected downstream surface, and evidence. File lists and commit subjects are supporting evidence, not themes. Separate confirmed deltas from likely consequences and open questions.

## Proportionality

Start with changed paths and high-signal classifiers. For small changes, inspect only relevant evidence and state `NOT_APPLICABLE` where justified. For security, identity, persistence, trust-boundary, dependency-source, or irreversible changes, expand to consumers, configuration, tests, and operational effects regardless of diff size. For broad mechanical changes, prioritize risk-bearing themes rather than line-by-line narration.

## Finding format

```yaml
id: CIA-<CATEGORY>-NNN
category: security
significance: high
confidence: CONFIRMED
summary: What evidence shows changed.
evidence:
  files: [path]
  commits: [full-or-short SHA with repository context]
  commands: [reproducible command]
impact: Why the change matters.
downstream_relevance: Which downstream surface is exposed, or NOT_APPLICABLE.
attention_required: Verification or review needed.
uncertainty: What evidence does not establish.
```

Finding IDs are unique within the report. Use `UNKNOWN` when evidence cannot support a stronger statement.
