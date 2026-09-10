# Plan: issue #1240 — platforms/desktop/deep-links.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/deep-links.md` does not exist; `platforms/`
  has no entries at all on `origin/launchpad`.
- The desktop container already has a corpus node, `architecture-containers-desktop`
  (`launchpad/docs/corpus/architecture/containers/desktop.md`), which names `buzz://`
  deep links in one paragraph but does not decompose the mechanism.
- `launchpad/docs/corpus/templates/architecture-component.md` is merged (`status:
  active`) and its required sections (purpose/scope, component diagram, notation
  legend, building-block table, boundary, relationships, scope-and-omissions) match
  issue #1240's Definition of Done almost line for line (responsibility + interface,
  dependencies/collaborators, source + tests, component-level not platform-level).
- The real mechanism lives in `desktop/src-tauri/src/deep_link.rs` (URL parsing, three
  pending-link queues, dispatch by host) plus `desktop/src-tauri/src/lib.rs` (plugin
  registration, single-instance argv forwarding, command registration) and
  `desktop/src/shared/deep-link.ts` + two hooks (`useMessageDeepLinks.ts`,
  `useEntityDeepLinks.ts`) on the frontend side — read in full already, not the CLI's
  `buzz://message` handling referenced in root `CLAUDE.md`.
- Repository revision recorded for this task: `cad6c375fdcc590158c1456c9fc7875f0f84a844`.

## STEP 1 — Scaffold front matter and skeleton

Hand-write front matter against `node.schema.json`: `id:
platforms-desktop-deep-links`, `type: architecture` (component-level, per the
template — `platforms` in the schema enum is a different, coarser surface than what
this node actually is), `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`. One evidence entry for the provenance commit.

## STEP 2 — Write the component decomposition body

Follow the `architecture-component` template skeleton: purpose paragraph (naming the
`architecture-containers-desktop` container), notation legend, Mermaid component
diagram (Tauri deep-link plugin -> `handle_deep_link_url` -> three pending queues ->
Tauri commands -> TS listeners -> React hooks), building-block table (one row per
Rust dispatch arm / parser / queue type and per TS listener), boundary section, and a
`part-of` relationship to `architecture-containers-desktop`.

## STEP 3 — Cite evidence per claim

One `evidence` entry per substantive claim, classed `FACT` (opened source) except
where genuinely inferred. No PR/issue/discussion evidence is being used as FACT.

## STEP 4 — Validate in isolation

Confirm the new file contributes zero new `validate.py` FAIL lines by stashing it,
re-running, and comparing against the known 21-FAIL baseline, then restoring.

## STEP 5 — Run corpus unit tests and commit

Run the corpus test suite as the sole content of one Bash call, then commit.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAILs vs. the
  documented 21-FAIL baseline on a clean `origin/launchpad` checkout.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` reports `OK`, run alone with no chained commands.
- `git commit -s` succeeds (fresh gate stamp required).

## OPEN

- Whether a future `architecture-containers-desktop` edit should trim its own
  deep-link paragraph now that a dedicated component node exists — left to that
  node's own maintainers, not decided here.

## LEFT OUT

- The CLI's own `buzz://message?...` link consumption (`crates/buzz-cli`) — a
  different container, out of scope for this node.
- Any second corpus document — none surfaced during authoring.
- `desktop-src-tauri/src/mouse_nav.rs`'s use of the same `"main"` window label — a
  passing implementation detail, not a deep-link concern.
