# Knowledge Crate — Contributor Rules

Scope: `launchpad/crates/knowledge/` (Buzz's help surface, surfaced in desktop
Settings). Read this before adding content, a query interface, or a build step
to this crate.

Parent PRD: #4. Feature: #532. This scaffold: #551.

## The one rule

**This crate reads a static, already-committed artefact — it never re-derives
it.** No AST parsing, no embeddings, no traversal logic, and no invocation of
the Python corpus-generation pipeline under `launchpad/project-intelligence/`
belongs in this crate or in the desktop build that packages it. That pipeline
runs once, out-of-band, and commits its output; this crate only reads that
output.

This is Ruling 11 / Ruling 12 from PRD #4, **ratified by ADR-0027** (#578,
closed 2026-08-24): the crate serves two pre-rendered front doors over the
committed corpus (a human Settings surface and a keyed `knowledge.*` agent
surface) and resolves neither live. `knowledge.find`'s free-text search (and
`knowledge.ask`, which routes to it) has no finite answer set a pipeline could
pre-render against arbitrary text — ADR-0027 first deferred both out of v1,
and **ADR-0031** (#1418, closed 2026-08-25) later made that permanent: both
methods are out of scope for the shipped crate, full stop, not a pending gap
to revisit here.

## What is not here yet

No seeded content (`#552`) and no `knowledge.*` query interface (`#553`,
`F22`) exist in this crate yet — both are separate, later work.
