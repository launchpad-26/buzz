---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#603
decided_in: launchpad-26/buzz#603
supersedes: none
---

# ADR-0028 — Markdown with YAML front matter is the canonical corpus representation

## Decision

Markdown files with YAML front matter are the one canonical, authored representation of
every corpus node. JSON, search indexes, dependency graphs, and any knowledge-crate-facing
serialization are generated derived views — never hand-authored, always reproducible from
the canonical Markdown.

Front matter carries the machine-checkable fields: stable ID, provenance, typed
relationships, status, and whatever other schema fields #605 defines. The Markdown body
carries the human-readable prose content that #604 ("adr: documentation corpus evidence
precedence and conflicting-source policy") governs.

This rejects a machine-record-canonical format (option 2) and two separately authored
corpora (option 3, already excluded as violating the one-corpus requirement).

## Context

#602 ("prd: canonical Buzz documentation corpus") needed one answer before #605 (the corpus
contract/schema/validator feature) or any content feature could start: what file format is
the corpus actually written in? Two live options existed — author Markdown directly, with
structured front matter for the fields tooling needs, or author a machine-readable record
format and generate Markdown from it for humans to read.

The deciding factor is Ruling 12: the corpus is a committed artefact, reviewed at the pull
request that changes it, not audited after the fact. That means the primary authored form
has to be something a human reviewer can read comfortably in a PR diff. Raw JSON or YAML
records work well as machine input but are a worse reviewing experience than prose — and PRD
#4's whole security argument rests on that PR-diff audit actually happening rather than being
skipped because the diff is unreadable.

It also matches an authored-document convention already established in this repository: ADRs
themselves are Markdown with YAML front matter (this record is one), and the handbook pages
built under the earlier PRD #4 work used the same shape (ADR-0003's provenance-contract
front matter). Introducing a second document shape for the corpus specifically would buy
determinism at the cost of consistency, for a problem #605's schema and validator can already
solve without it.

## Consequences

**Good.** The corpus stays reviewable as a human-read PR diff, which is the enforcement
mechanism the rest of Ruling 12 depends on.

**Good.** One canonical representation removes the risk of two authored corpora quietly
diverging; every projection — validator, indexes, knowledge-crate serialization — derives
from the same canonical Markdown, rather than any of them reading (or authoring) a second
source of truth. Per ADR-0027, the knowledge crate itself consumes pre-rendered projections
of this corpus, not the corpus files directly; this decision is what makes those projections
reproducible from one canonical source instead of independently authored.

**Good.** Consistent with the Markdown+front-matter convention already used for ADRs in this
repository, so no new document shape needs its own reviewing habits built around it.

**Bad.** Front matter plus a validator has to enforce structure that a fully
machine-readable record format would get for free (strict typing, for instance). #605's
schema and validator now carry that enforcement burden.

**Bad.** Generated projections — indexes, graphs, crate serializations — must be kept
reproducible from the canonical Markdown. Any generator that free-hands content instead of
deriving it from the corpus becomes a silent second authored corpus, which is exactly what
this decision forbids.

## Security implications

The corpus is public and may ship inside desktop builds, so the representation must not
create a path where private or sensitive source material ends up embedded in generated
projections that bypass whatever provenance fields #605 defines. Provenance and claim
classification (FACT/INFERENCE/TEAM KNOWLEDGE) must stay structurally encoded — validator-
checkable, not asserted only in free-form body prose that could be misread or forged as a
stronger claim than it is. This decision does not itself say classification is a page-level
front-matter field: the existing contract (`launchpad/project-intelligence/CONTRACT.md`)
classifies at the granularity of an individual claim within a response, not a whole page or
node. Whether a single corpus node holds one claim or several is exactly the corpus-shape
question CONTRACT.md §9.1 leaves open — it is #605's to decide, not something this ADR or
that contract settles. Generated views must not silently drop whatever security-relevant
provenance their source node carries.

## Provenance

Decided by Serina McFall in conversation on 2026-08-25, after an agent-drafted
recommendation.

**Her call:** Markdown files with YAML front matter, canonical (option 1), over a
machine-record-canonical format (option 2).

**The recommendation:** drafted by an AI agent (Claude Sonnet 5) on 2026-08-25, on the
reasoning that the corpus's audit mechanism (Ruling 12) depends on human-readable PR diffs,
and that Markdown+front-matter is already an established authored-document shape in this
repository (ADRs). The agent drafted the recommendation; per issue #603's own record, the
Decision outcome is Serina's, filled directly rather than left to an agent to approve.
