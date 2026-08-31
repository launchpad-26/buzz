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
and **ADR-0031** (#1418, closed 2026-08-26) later made that permanent for the
shipped crate — Option D (a curated, bounded natural-language question set) is
named as the one upgrade worth reconsidering later, but is not adopted now.

**This boundary is enforced, not just stated (`#552`).**
`desktop/scripts/check-no-corpus-pipeline.mjs` (wired into `pnpm check`,
which runs in every pre-push `desktop-check` lane and CI) fails if
`desktop/package.json`, `desktop/vite.config.ts`, or
`desktop/src-tauri/tauri.conf.json` ever reference
`project-intelligence/corpus` — the pipeline's own directory. A legitimate
build never needs to name it: the packaged artifact the Settings panel reads
is a relative import of a committed file
(`desktop/src/launchpad/settings/knowledge/generated/corpus.json`), produced
out-of-band by `launchpad/project-intelligence/corpus/package.py` and never
invoked from these build files.

## Seeded content and regeneration (`#552`)

The crate now embeds the packaged canonical documentation corpus:
`generated/corpus.json`, read via `include_str!` and exposed as `nodes()`. It
is a **committed, generated artefact** — never hand-edited. The identical
JSON is also copied to
`desktop/src/launchpad/settings/knowledge/generated/corpus.json`, which the
Settings panel renders directly (a static asset import, not Tauri IPC — see
the open question below).

After any change to `launchpad/docs/corpus/`, regenerate both copies and
commit the result:

```
just knowledge-package
```

This runs `launchpad/project-intelligence/corpus/package.py`, which reads the
validated corpus via `validate.load_nodes()` and rewrites both output paths
from `DEFAULT_OUTPUTS`. A CI drift guard fails if a committed copy no longer
matches what regeneration would produce — see `just corpus-validate` and
`DriftGuardTest` in `launchpad/project-intelligence/corpus/tests/test_package.py`.

## What is not here yet

No `knowledge.*` query interface (`#553`, `F22`) exists in this crate yet —
that is separate, later work.

**Not yet wired to the desktop app, and that path is an open question.** This
crate is a root-workspace member (`Cargo.toml`'s `members` list), but root
`Cargo.toml` excludes `desktop/src-tauri` from that workspace. Root-workspace
membership alone does not make this crate reachable from the Tauri backend —
depending on it from `desktop/src-tauri` would mean editing
`desktop/src-tauri/Cargo.toml`, a third upstream file ADR-0045's granted
exception (the root `Cargo.toml` members list) does not cover. Whoever wires
the crate into the desktop build (`#552` or later) needs to resolve that, not
assume it falls out of this scaffold.
