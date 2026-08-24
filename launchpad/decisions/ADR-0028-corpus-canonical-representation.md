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
carries the human-readable prose content that #604's evidence-precedence policy governs.

This rejects a machine-record-canonical format (option 2) and two separately authored
corpora (option 3, already excluded as violating the one-corpus requirement).

## Context

#602 needed one answer before #605 (the corpus contract/schema/validator feature) or any
content feature could start: what file format is the corpus actually written in? Two live
options existed — author Markdown directly, with structured front matter for the fields
tooling needs, or author a machine-readable record format and generate Markdown from it for
humans to read.

The deciding factor is Ruling 12: the corpus is a committed artefact, reviewed at the pull
request that changes it, not audited after the fact. That means the primary authored form
has to be something a human reviewer can read comfortably in a PR diff. Raw JSON or YAML
records work well as machine input but are a worse reviewing experience than prose — and PRD
#4's whole security argument rests on that PR-diff audit actually happening rather than being
skipped because the diff is unreadable.

It also matches every other authored-document convention already in this repository: ADRs
are Markdown, the RepoQL concept capsules are Markdown with front matter, and the
now-superseded handbook pages were Markdown with front matter (ADR-0003). Introducing a
second document shape for the corpus specifically would buy determinism at the cost of
consistency, for a problem #605's schema and validator can already solve without it.

## Consequences

**Good.** The corpus stays reviewable as a human-read PR diff, which is the enforcement
mechanism the rest of Ruling 12 depends on.

**Good.** One canonical representation removes the risk of two authored corpora quietly
diverging; every consumer — validator, indexes, knowledge crate — reads the same source.

**Good.** Consistent with the existing Markdown+front-matter convention already used for
ADRs and RepoQL concepts, so no new document shape needs its own reviewing habits built
around it.

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
projections that bypass front-matter provenance fields. Provenance and claim classification
(FACT/INFERENCE/TEAM KNOWLEDGE) must stay structural — encoded in front-matter fields a
validator checks — not asserted in body prose that could be misread or forged as a stronger
claim than it is. Generated views must not silently drop the security-relevant provenance
carried in their source node's front matter.

## Provenance

Decided by Serina McFall in conversation on 2026-08-25, after an agent-drafted
recommendation.

**Her call:** Markdown files with YAML front matter, canonical (option 1), over a
machine-record-canonical format (option 2).

**The recommendation:** drafted by an AI agent (Claude Sonnet 5) on 2026-08-25, on the
reasoning that the corpus's audit mechanism (Ruling 12) depends on human-readable PR diffs,
and that Markdown+front-matter is already the established authored-document shape elsewhere
in this repository (ADRs, RepoQL concepts). The agent drafted the recommendation; Serina
reached the same option independently before it was given, and confirmed it.
