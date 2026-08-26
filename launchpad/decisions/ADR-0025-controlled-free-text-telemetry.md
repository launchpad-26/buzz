---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#490
decided_in: launchpad-26/buzz#490
supersedes: none
---

# ADR-0025 — Permit controlled free text in telemetry

## Decision

Buzz telemetry may contain free-text user and agent activity because reconstructing what a user said and what an agent did is a required diagnostic capability.

Free text is not unrestricted. Export requires:

- explicit field classification, such as user message, agent response, tool input, tool output, subprocess output, or error text;
- secret and credential filtering before the product export boundary;
- field and payload size limits with a visible truncation marker;
- restricted access and audited queries;
- defined retention and deletion behavior; and
- contributor consent on participating client machines.

Private keys, authentication tokens, raw environment variables, and binary attachments are prohibited telemetry content under every configuration profile.

## Context

PRD #289 requires evidence sufficient to reproduce witnessed failures and produce agent-authored bug reports. Structured operation names, status codes, and durations cannot always establish what request was made, what an agent attempted, or why an external tool failed. Excluding all free text would preserve safety by discarding evidence the product explicitly needs.

Exporting arbitrary text and attempting to redact only in a downstream collector is also insufficient. Sensitive content would already have crossed the product boundary, and completed research found that allowlists cannot infer the safety of unbounded message bodies. The product therefore permits diagnostic content but owns controls before export.

## Consequences

**Good.** Authorized investigators can reconstruct user and agent activity rather than infer it from generic status codes.

**Good.** Free-text fields become named, reviewable product contracts instead of accidental stdout, span, or error-message leakage.

**Bad.** The telemetry corpus may contain member conversations, prompts, repository material, and tool output. It requires stricter access, retention, audit, deletion, and incident-response controls than operational metadata alone.

**Bad.** Filtering cannot guarantee detection of every secret. Size limits and classification reduce exposure but do not eliminate the risk of a user pasting sensitive material into an allowed field.

**Bad.** Truncation can remove the exact evidence needed for a diagnosis. Truncation must be explicit so investigators know the record is incomplete.

## Security implications

This decision deliberately expands telemetry's sensitivity and attacker value. Product-side filtering is mandatory; collector-only redaction is not an adequate control. Infrastructure must enforce least-privilege access, query audit, retention, deletion, and protected transport and storage. Consent must be revocable. No profile may override the absolute prohibition on private keys, authentication tokens, raw environment variables, or binary attachments.
