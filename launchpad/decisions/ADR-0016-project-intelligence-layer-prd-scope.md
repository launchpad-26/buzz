---
status: Accepted
date: 2026-08-18
issue: launchpad-26/buzz#190
decided_in: launchpad-26/buzz#190
supersedes: none
---

# ADR-0016 — Project Intelligence Layer becomes PRD #4 scope, not a new PRD

## Decision

**Amend #4 directly.** The Project Intelligence Layer — the agent-facing knowledge-graph,
semantic-search, and tool-execution architecture specified in
`launchpad/Research/project-intelligence-layer-design.md` — becomes part of PRD #4's own scope,
via a new Ruling 10 and updates to its Non-goals, Success criteria, Impacted components, and
Security implications. It is not filed as a separate PRD, and #4's existing Non-goals bullets
excluding a RAG system, vector databases, embeddings, or agent-retrieval infrastructure are
superseded.

## Context

#4's Ruling 9 already named a five-stage roadmap, staging "Knowledge retrieval" (agents search
and cite the corpus) and "Knowledge bot / Buzz integration" (stage 4) as future work, while its
Non-goals excluded them from the PRD as filed: *"No requirement to build a RAG system or
knowledge bot yet... This PRD establishes the knowledge layer, not the future retrieval system
that may consume it."*

A complete architecture and system-prompt specification for that retrieval layer was written
(`launchpad/Research/project-intelligence-layer-design.md`), and ADR #190 asked whether it should
become tracked work: left as untracked research, filed as a new standalone PRD, or folded into
#4 directly. #190 recorded folding it in as an expected-rejection option, on the reasoning that
#4's Non-goals excluded it deliberately, not by oversight, and that reopening a deliberate
exclusion inside the existing PRD risked quietly reversing a decision #4 had already made about
itself.

## Consequences

**Good.** One PRD now owns the full progression Ruling 9 originally described, rather than
splitting it across #4 and a second PRD that would need its own rulings restating provenance,
audience separation, and source boundaries #4 already established. The design document already
exists and needs no rework to serve as #4's Ruling 10 reference.

**Bad, stated honestly.** #4's own Non-goals excluded this scope in explicit language, and this
decision reverses that exclusion inside the same PRD rather than through a fresh one — the
scenario #190 flagged as the reason to expect rejection. Folding it in also means #4 now carries
two materially different systems under one PRD: a published documentation site (stages 1/2,
largely built) and an unbuilt agent-execution architecture (stages 3/4, design-only) — reviewers
judging #4's completion need to track which parts of it are shipped and which are still a design
document.

## Security implications

No code or config changes as a result of this decision alone — it is a scope amendment to an
issue, not an implementation. But the amendment commits #4 to eventually including tools with a
different trust boundary than anything #4 has shipped so far: the Project Intelligence Layer's
`run_command` and `run_test` investigation tools are execute-capable against the repository the
agent is reasoning about, where the handbook (stages 1/2) is read-only synthesis. Any future
implementation must re-confirm the private-repository exposure boundary already settled for the
handbook (ADR-0001, ADR-0003) before it indexes or executes against private sources — that
re-confirmation is not done by this ADR and remains a gate on implementation, not on the scope
decision recorded here.

## Provenance

Decided by @serina-mcfall directly in conversation on 2026-08-18, in response to the options
drafted in #190. Recorded here per `launchpad/AGENTS.md` §4 rule 3 and the decisions/README
lifecycle — the decision record is written in the same PR that closes #190.
