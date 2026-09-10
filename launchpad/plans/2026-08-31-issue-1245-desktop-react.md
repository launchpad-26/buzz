# Plan: issue #1245 — document platforms/desktop/react.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/` does not yet contain `react.md`.
- Sibling batch tasks (#1240 deep-links, #1241 frontend-backend-bridge, #1242
  local-agent-management, #1243 navigation) are already committed on their own
  branches and establish a precedent shape for `platforms/desktop/*.md`:
  `type: platforms`, `id: platforms-desktop-<name>`, `component.md` template's
  section shape (Responsibility / Public interface / Dependencies / Boundary /
  Relationships / Scope and omissions), and `part-of: architecture-containers-desktop`.
- `architecture-containers-desktop` exists on `origin/launchpad` and is a valid
  relationship target.
- No template is written specifically for `type: platforms`; `component.md` is
  the closest fit (one cohesive frontend layer as a standalone artifact), same
  choice the navigation.md sibling already made and documented as an INFERENCE.

## STEP 1 — Confirm scope boundary against sibling tasks

Read the issue body and the already-committed siblings
(navigation.md, frontend-backend-bridge.md) to draw the line: this node covers
the React 19 frontend's own architecture (feature/shared/app directory
convention, component composition, provider hierarchy, render-perf
conventions) — not routing (#1243), not Tauri IPC (#1241), not state
management specifics (#1249, unmerged), not Tauri/native shell (#1250,
unmerged).

## STEP 2 — Gather evidence from real source

Inspect `desktop/package.json` (React/React Query versions), `desktop/src/main.tsx`
and `desktop/src/app/App.tsx` (bootstrap, provider hierarchy, the two-tier
QueryClient, the `communityKey`-driven remount pattern), `desktop/src/features/*`
and `desktop/src/shared/*` directory shape, `desktop/scripts/check-file-sizes.mjs`
and `Justfile` (differential 1000-line ratchet), `desktop/src/shared/hooks/useStableReference.ts`
(the `React.memo` stabilization pattern named in root `CLAUDE.md`), and
`desktop/biome.json`/`tsconfig.json` (lint/format/strict-mode tooling).

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/desktop/react.md`: `type: platforms`,
`id: platforms-desktop-react`, `status: draft`, `origin: launchpad`, evidence
citing only sources actually opened, `relationships: [part-of:
architecture-containers-desktop]`. Body follows `component.md`'s required
sections. Explicit boundary excludes routing, IPC, state management detail,
and Tauri shell — naming the owning sibling task for each.

## STEP 4 — Validate locally

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
file present, then with it stashed, confirming the FAIL count is identical
(the known pre-existing 21) in both runs — i.e. the new node adds zero new
FAILs (an `UNVERIFIED` notice on the commit-citation entry is expected).

## STEP 5 — Commit

Run the corpus unit test suite as the sole content of one Bash call, then
commit both the node and this plan file with `git commit -s`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAILs.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — OK.
- Every evidence citation opened and read; no `path#line=` fragment citations
  (use `path:A-B`).

## OPEN

- Whether `type: platforms` (rather than `component.md`'s own recommended
  `type: implementation`) is the corpus's settled convention for
  `platforms/*` nodes is still an open INFERENCE inherited from the
  already-committed navigation.md sibling, not resolved by this task.

## LEFT OUT

- Routing/navigation internals (#1243, already documented).
- Tauri IPC/bridge internals (#1241, already documented).
- React Query caching semantics and community-scoped state management detail
  (#1249, a separate sibling task).
- Tauri/native shell packaging (#1250, a separate sibling task).
- Any per-feature business logic under `desktop/src/features/*`.
