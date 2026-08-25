---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#303
decided_in: launchpad-26/buzz#303
supersedes: none
---

# ADR-0048 — Review-agent containment covers upstream content read by models

## Decision

The review-agent containment contract extends to every upstream-authored value
inserted into an AI prompt. The existing nonce-delimited envelope and escaping
mechanism remain the sole containment implementation.

The contract MUST define distinct provenance labels for:

- `upstream_commit_message`
- `upstream_diff`
- `upstream_file_path`
- `upstream_file_content`
- `upstream_release_note`

A caller MUST select the narrowest truthful label and MUST NOT use a `pr_*` label
for upstream-authored material.

Text rendered only for a human in a GitHub issue or pull-request body does not
require model-prompt containment. It MUST retain explicit provenance and MUST NOT
be re-ingested into a model without first applying the applicable upstream
containment envelope.

#273 consumes this contract. #120 and PRD #109 own the contract extension and
its implementation.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

The existing containment contract explicitly covers seven pull-request-author
surfaces. Its nonce-delimited envelope and escaping are technically generic, but
its labels are provenance declarations and none truthfully describes an upstream
commit message, diff, file path, file content, or release note.

The escalation workflow needs to present upstream material to models. Reusing a
`pr_*` label would make the provenance false; omitting containment would place
untrusted text alongside instructions. A second containment implementation under
#273 would create a security control that can drift from the review-agent
contract.

## Consequences

- Upstream text that enters a model prompt receives the same containment
  discipline as pull-request-author text.
- The contract and its tests have one implementation and one audit surface.
- The extension is owned by the PRD that owns the normative contract; #273 does
  not modify it independently.
- Human-readable GitHub artifacts remain readable while retaining provenance.
- Any later model use of those artifacts must contain upstream material before
  prompt construction.

## Security implications

Upstream code trust does not authorize upstream-authored text to influence a
model in instruction position. The envelope separates text from instructions and
makes its origin explicit. Truthful upstream labels preserve auditability and
prevent an upstream diff or commit message from being misrepresented as
pull-request-author input.

The decision does not claim that containment eliminates prompt injection. It
sets the required boundary for text that enters an AI prompt and prevents a
second implementation from weakening or drifting from that boundary.

## Supersedes

none — extends the existing review-agent containment contract without replacing
its pull-request-author coverage.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives and evidence remain in #303.