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

This is Ruling 11 / Ruling 12 from PRD #4, stated here so a contributor sees
the constraint before writing code against it. **It is not yet ratified** —
issue #578 is open and flags a real conflict between this rule and the
`knowledge.*` query interface's free-text `find` method, which cannot be
served from a static artefact alone. If #578 changes the ruling, this file and
the crate's shape both need revisiting; until then, treat re-derivation as
disallowed.

## What is not here yet

No seeded content (`#552`) and no `knowledge.*` query interface (`#553`,
`F22`) exist in this crate yet — both are separate, later work.
