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

A caller MUST select the narrowest truthful label, and MUST NOT apply any of the
contract's seven pre-existing labels — `pr_title`, `pr_body`, `pr_diff`,
`pr_issue_comments`, `pr_review_comments`, `pr_review_bodies`, `linked_issue` —
to upstream-authored material. The prohibition is stated against all seven rather
than against the `pr_*` prefix because `linked_issue` does not carry that prefix:
a prefix-scoped rule would leave it available as a label for an upstream diff,
which is precisely the false provenance this record exists to prevent.

Text rendered only for a human in a GitHub issue or pull-request body does not
require model-prompt containment. It MUST retain explicit provenance and MUST NOT
be re-ingested into a model without first applying the applicable upstream
containment envelope.

#273 consumes this contract. #120 and PRD #109 own the contract extension and
its implementation.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

The existing containment contract explicitly covers seven pull-request surfaces.
`launchpad/review-agent/CONTAINMENT.md` lists them: "All four route the same
seven labels: `pr_title`, `pr_body`, `pr_diff`, `pr_issue_comments`,
`pr_review_comments`, `pr_review_bodies`, `linked_issue`." Six of the seven are
pull-request-author surfaces; `linked_issue` is not, which is why the prohibition
above enumerates all seven instead of relying on the `pr_*` prefix. Its
nonce-delimited envelope and escaping are technically generic, but its labels are
provenance declarations and none of the seven truthfully describes an upstream
commit message, diff, file path, file content, or release note.

The escalation workflow needs to present upstream material to models. Reusing any
of those seven labels would make the provenance false; omitting containment would
place untrusted text alongside instructions. A second containment implementation
under #273 would create a security control that can drift from the review-agent
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
- **The implementation work this decision creates is not yet filed, and must
  be.** It comprises: adding the five `upstream_*` labels to
  `launchpad/review-agent/CONTAINMENT.md` and to the containment implementation;
  extending the label prohibition to all seven pre-existing labels; and adding
  tests covering each new label and the rejection of a pre-existing label for
  upstream-authored material. Naming #120 and PRD #109 as owners is not a linked
  work item, and §4.1 of `launchpad/AGENTS.md` requires that "Work a decision
  creates is filed separately afterwards and linked back". At the time of writing
  no issue exists for it.

## Security implications

Upstream code trust does not authorize upstream-authored text to influence a
model in instruction position. The envelope separates text from instructions and
makes its origin explicit. Truthful upstream labels preserve auditability and
prevent an upstream diff or commit message from being misrepresented as
pull-request-author input.

A prohibition scoped to the `pr_*` prefix would have been satisfiable by
labelling upstream material `linked_issue`, leaving the audit trail wrong while
every stated MUST held. The enumeration above closes that hole in the record;
closing it in the implementation is part of the unfiled work named in
Consequences.

The decision does not claim that containment eliminates prompt injection. It
sets the required boundary for text that enters an AI prompt and prevents a
second implementation from weakening or drifting from that boundary.

## Supersedes

none — extends the existing review-agent containment contract without replacing
its pull-request-author coverage.

## Provenance

N/A - the decision was settled in #303 on 2026-08-26 and does not predate its ADR
issue, which is the only case `launchpad/decisions/README.md` scopes this section
to.
