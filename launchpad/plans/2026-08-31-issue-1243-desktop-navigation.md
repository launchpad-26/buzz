# Plan: issue #1243 — document platforms/desktop/navigation.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad` — no
  collision, no sibling document to update instead of create.
- The desktop app's routing is `@tanstack/react-router` (`desktop/package.json`), with
  a virtual route tree (`desktop/src/app/routes.ts`) compiled by
  `@tanstack/router-plugin/vite` into `desktop/src/app/routeTree.gen.ts`, and a single
  module-level `router` instance (`desktop/src/app/router.tsx`, hash history, scroll
  restoration).
- `architecture/containers/desktop.md` (id `architecture-containers-desktop`) already
  exists on `origin/launchpad` and is a valid `part-of` relationship target.
- No `templates/platforms-*.md` template exists. `component.md`'s required-sections
  shape (Responsibility / Public interface / Dependencies / Boundary / Relationships /
  Scope and omissions) is the closest fit for "one cohesive module, standalone,"
  but its own ledger recommends `type: implementation` — this repo's own precedent
  (`templates/deployment.md`'s ledger) states `platforms` is this repo's own surface
  for client platforms (desktop/web/mobile), which matches the target path directly.

## STEP 1 — Read the issue and confirm scope

Read issue #1243's DoD checklist in full; confirm the four "component-level" bullets
(responsibility/interface/boundary, dependencies/collaborators, source+tests links,
component- not platform-level scope) match `component.md`'s shape rather than
`architecture-component.md`'s (which requires enumerating *every* building block in
the desktop container plus a diagram — out of scope for one subsystem).

## STEP 2 — Investigate the real routing code

Read, in full or by relevant section: `desktop/src/app/routes.ts`, `router.tsx`,
`navigation/useAppNavigation.ts`, `navigation/navigationGuard.ts`,
`navigation/useBackForwardControls.ts`, `navigation/backForwardChords.ts`,
`AppShell.helpers.ts` (`deriveShellRoute`), `App.tsx` (community-key remount boundary
and `transitionCommunity`), `useCommunityNavigationTransitions.ts`,
`features/communities/communityNavigationStorage.ts`, `communityViewTransition.ts`,
`useCommunityInit.ts`'s `resetCommunityState` (confirms `router` is NOT a
community-scoped singleton it resets), and `routes/root.tsx`. Note the existing test
files (`navigationGuard.test.mjs`, `backForwardChords.test.mjs`,
`searchHitNavigation.test.mjs`, `searchHighlightNavigation.test.mjs`) as evidence for
the "links tests" DoD bullet.

## STEP 3 — Draft the node

`id: platforms-desktop-navigation`, `type: platforms` (INFERENCE, cited against
`node.schema.json` and `templates/deployment.md`'s own reasoning), `status: draft`,
`origin: launchpad`. Body follows `component.md`'s shape: Responsibility, Public
interface (the `useAppNavigation` action surface + guard registration API), Boundary
(explicitly excludes deep-link URL parsing — owned by #1240 — and the sidebar/channel
selection UI itself), Dependencies (TanStack Router, the community-switch boundary),
Relationships (`part-of: architecture-containers-desktop`), Scope and omissions.

## STEP 4 — Validate in isolation

Run `validate.py` with the new file present, then with it stashed, to confirm the new
node contributes zero new FAIL lines against the pre-existing 21-FAIL baseline.

## STEP 5 — Commit

Run the corpus unittest suite as the sole content of its own Bash call, then commit
with `-s`, per the batch's commit-gate contract.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (or the same
  21 pre-existing FAILs, no new ones).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
- `git commit -s` succeeds (fresh gate stamp).

## OPEN

- Whether `type: platforms` is the corpus's eventual settled convention for
  `platforms/*` nodes is not fully established — no template or merged instance
  exists yet to confirm it beyond `templates/deployment.md`'s own reasoning about
  what "platforms" means in this repo. Recorded as an `INFERENCE`, not a `FACT`.

## LEFT OUT

- Deep-link URL parsing/handling (`buzz://` scheme, `useDraftMentionRouting`,
  entity-link activation) — owned by issue #1240 (`platforms/desktop/deep-links.md`).
- The sidebar/channel-list selection UI itself and `AppShell`'s broader composition —
  those are other components' concern, not navigation's.
- Whether the TanStack Router route tree could/should be restructured — out of scope
  per the issue's "no runtime behavior change" boundary.
