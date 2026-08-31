---
id: platforms-web-application
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 46eb901e5aa928aa147fdaef9a509b636218653f."
    entry_class: FACT
    evidence:
      - "commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "web/src/main.tsx is the application's entry point: it mounts React into `#root` inside React.StrictMode, wrapping the app in, from outermost to innermost, a TanStack Query `QueryClientProvider` (retry: 1, refetchOnWindowFocus: false, networkMode: 'always', gcTime 5 minutes), the app's own `ThemeProvider`, a Radix `TooltipProvider` (delayDuration 300ms), then `<App />` and a `<Toaster />`."
    entry_class: FACT
    evidence:
      - "web/src/main.tsx"
  - statement: "web/index.html declares a single `<div id=\"root\"></div>` and loads `/src/main.tsx` as a module script; there is no server-rendered markup beyond that mount point."
    entry_class: FACT
    evidence:
      - "web/index.html"
  - statement: "web/src/app/App.tsx's entire body is `<RouterProvider router={router} />`, delegating all page rendering to the TanStack Router instance created in web/src/app/router.tsx."
    entry_class: FACT
    evidence:
      - "web/src/app/App.tsx"
  - statement: "web/src/app/router.tsx creates the router from a generated `routeTree` (web/src/app/routeTree.gen.ts), browser history, and scroll restoration keyed on pathname; it also registers the router's type on TanStack Router's `Register` interface for typed navigation."
    entry_class: FACT
    evidence:
      - "web/src/app/router.tsx"
  - statement: "web/src/app/routes.ts is a TanStack Router virtual file-route config declaring one root route (root.tsx) with four children: index (index.tsx), /invite/$code (invite.$code.tsx), /repos (repos.tsx), /repos/$repoId (repos.$repoId.tsx), and /repos/$repoId/blob/$ (repos.$repoId.blob.$.tsx)."
    entry_class: FACT
    evidence:
      - "web/src/app/routes.ts"
  - statement: "web/vite.config.ts's `tanstackRouter` plugin reads routesDirectory './src/app/routes', virtualRouteConfig './src/app/routes.ts', and writes the generated route tree to './src/app/routeTree.gen.ts'; the file-size gate's own generated-file exemption pattern is not asserted here, only the plugin wiring that produces routeTree.gen.ts."
    entry_class: FACT
    evidence:
      - "web/vite.config.ts"
  - statement: "web/src/app/routes/root.tsx defines the one root layout component for every route: a flex column div containing a `<main>` that renders the matched child route via TanStack Router's `<Outlet />`. It adds no navigation chrome, header, or sidebar of its own."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/root.tsx"
  - statement: "Every route file under web/src/app/routes/ (index.tsx, invite.$code.tsx, repos.tsx, repos.$repoId.tsx, repos.$repoId.blob.$.tsx) follows the same pattern: create a `Route` via `createFileRoute`, and render a page component imported from a feature module under web/src/features/ (e.g. index.tsx renders `ReposPage` from web/src/features/repos/ui/ReposPage.tsx; invite.$code.tsx reads its `$code` param and renders `InvitePage` from web/src/features/invite/ui/InvitePage.tsx). No route file contains page-level business logic of its own."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/index.tsx"
      - "web/src/app/routes/invite.$code.tsx"
      - "web/src/features/repos/ui/ReposPage.tsx"
      - "web/src/features/invite/ui/InvitePage.tsx"
  - statement: "web/src/features/ (per its own .gitkeep marker plus the invite/ and repos/ subdirectories) holds exactly two feature areas at the recorded revision: invite and repos; web/src/shared/ holds cross-feature code: lib/ (nostr-client.ts, nip98.ts, relay-url.ts, nostr-signer.ts, pubkey.ts, relative-time.ts, cn.ts, buzz-download.ts), theme/ (ThemeProvider.tsx, ThemeToggle.tsx), styles/globals.css, and ui/ (badge.tsx, button.tsx, card.tsx, input.tsx, sonner.tsx, tooltip.tsx)."
    entry_class: FACT
    evidence:
      - "web/src/features/.gitkeep"
      - "web/src/features/invite/invite-api.ts"
      - "web/src/features/repos/git-client.ts"
      - "web/src/shared/lib/nostr-client.ts"
      - "web/src/shared/theme/ThemeProvider.tsx"
      - "web/src/shared/ui/button.tsx"
  - statement: "web/src/shared/theme/ThemeToggle.tsx exists but is not imported by any other file in web/src (a repository-wide grep for 'ThemeToggle' outside its own definition file returned no matches), so the app currently exposes no in-app light/dark toggle; ThemeProvider.tsx follows the OS `prefers-color-scheme` media query in production and only honors a `?previewTheme=light|dark` query param override in development (`import.meta.env.DEV`)."
    entry_class: FACT
    evidence:
      - "web/src/shared/theme/ThemeProvider.tsx"
      - "grep_repo(pattern='ThemeToggle', scope='web/src/**/*.tsx') -> only web/src/shared/theme/ThemeToggle.tsx itself, no import sites, at commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "web/components.json configures shadcn/ui code generation ('new-york' style, zinc base color, CSS variables) with aliases mapping 'components'/'ui' to @/shared/ui and 'lib'/'utils' to @/shared/lib and @/shared/lib/cn respectively, establishing web/src/shared/ui/ as generated-and-hand-edited shadcn component output rather than a hand-rolled design system."
    entry_class: FACT
    evidence:
      - "web/components.json"
  - statement: "web/package.json names the package buzz-web, private, and defines dev (vite), build (`tsc && vite build`), typecheck (`tsc --noEmit`), lint (`biome lint .`), check (`biome check . && pnpm check:pubkey-truncation`), format (`biome format --write .`), preview (vite preview), test:e2e and test:e2e:smoke (each `pnpm build` then playwright test) scripts, plus check:file-sizes and check:pubkey-truncation scripts backed by web/scripts/check-file-sizes.mjs and web/scripts/check-pubkey-truncation.mjs."
    entry_class: FACT
    evidence:
      - "web/package.json"
      - "web/scripts/check-file-sizes.mjs"
      - "web/scripts/check-pubkey-truncation.mjs"
  - statement: "web/scripts/check-file-sizes.mjs enforces a 1000-line ceiling on every .ts/.tsx file under src/app, src/features and src/shared/api by delegating to the shared ../../scripts/check-file-sizes-core.mjs, the same repository-wide file-size gate CLAUDE.md documents for mobile; web/scripts/check-pubkey-truncation.mjs enforces (with two named line-level overrides and one allowed file, web/src/shared/lib/pubkey.ts) that raw pubkey strings are not truncated ad hoc outside that shared helper."
    entry_class: FACT
    evidence:
      - "web/scripts/check-file-sizes.mjs"
      - "web/scripts/check-pubkey-truncation.mjs"
  - statement: "web/src/app/routeTree.gen.ts, the generated route tree the check-file-sizes.mjs rule for src/app would otherwise scan, is 144 lines at the recorded revision -- well under the 1000-line ceiling regardless of whether the gate treats generated files differently, so this file does not currently test that distinction."
    entry_class: FACT
    evidence:
      - "web/src/app/routeTree.gen.ts"
  - statement: "web/biome.json extends the repository-root ../biome.json rather than defining its own lint/format rules; web/tsconfig.json enables `strict`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, targets ES2020 with bundler module resolution, and maps the `@/*` path alias to `./src/*` (the same alias web/vite.config.ts's `resolve.alias` registers for the bundler)."
    entry_class: FACT
    evidence:
      - "web/biome.json"
      - "web/tsconfig.json"
      - "web/vite.config.ts"
  - statement: "The repository-root Justfile defines web (start the Vite dev server on a worktree-derived port against BUZZ_RELAY_URL), web-check (`biome check .` inside web/), web-fix (`biome check --write .`), web-typecheck (`pnpm typecheck`), web-build (`pnpm build`), and web-e2e-smoke (`pnpm test:e2e:smoke`) targets, each a thin `cd web && pnpm <script>` wrapper except web itself, which also derives a collision-avoiding port via scripts/instance-env.sh."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "web/playwright.config.ts's 'smoke' project runs only web/tests/e2e/smoke.spec.ts against Desktop Chrome, with a webServer block that runs `vite preview` on 127.0.0.1:4173 and reuses an existing server outside CI; web/tests/e2e/smoke.spec.ts includes two app-shell-level assertions — the home route renders an image with accessible name 'Buzz' inside the page's `main` landmark, and the home route shows a 'Repositories' heading — alongside several invite-flow-specific tests."
    entry_class: FACT
    evidence:
      - "web/playwright.config.ts"
      - "web/tests/e2e/smoke.spec.ts"
  - statement: "launchpad/docs/corpus/architecture/containers/web.md (id architecture-containers-web) is merged on origin/launchpad and already documents the web container's responsibility, technology choice, ownership boundary, inbound/outbound interfaces, deployment implications (how buzz-relay serves the built bundle via BUZZ_WEB_DIR/BUZZ_SERVE_GIT_WEB_GUI), data implications, and security implications; this node does not restate any of that container-level ground and instead references it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
  - statement: "Because architecture-containers-web already owns the container-level (deployment, relay-serving, data, security) ground and issue #1286's own Definition of Done requires this node to explain only component-level behavior, the appropriate scope for platforms-web-application is the in-repo application shell -- entry point, provider stack, routing mechanism, and the app-level build/lint/test tooling contract other feature code relies on -- rather than a second pass over how the bundle is served or secured."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
      - "web/src/main.tsx"
      - "web/src/app/routes.ts"
    confidence: 0.85
relationships:
  - type: references
    target: architecture-containers-web
---

# Platform: `web` application shell

The application-level structure of `web/` — the browser client's React entry
point, provider stack, and routing mechanism, plus the app-level build, lint
and test tooling contract that every feature module builds against. This
node answers "how is the app wired together and what must a new route or
feature conform to", not "how is the bundle served" (see
`architecture-containers-web`) or "what does any one feature do" (see the
sibling `platforms/web/*` nodes below).

## Purpose and scope

`web/` is a Vite + React 19 + TypeScript single-page application (package
`buzz-web`). This node documents its application shell: the code that runs
before any feature-specific page renders, and the conventions a new route or
feature must follow to plug into it.

## Responsibility

`web/src/main.tsx` is the sole entry point. It mounts React into the single
`#root` element declared in `web/index.html` inside `React.StrictMode`, and
establishes the app-wide provider stack, outermost to innermost:

1. `QueryClientProvider` (TanStack Query) — a shared `QueryClient` configured
   with `retry: 1`, `refetchOnWindowFocus: false`, `networkMode: "always"`,
   and a 5-minute `gcTime`.
2. `ThemeProvider` — applies a `light`/`dark` class to `<html>` based on the
   OS `prefers-color-scheme` media query in production; only in development
   does a `?previewTheme=light|dark` query parameter override it.
3. `TooltipProvider` (Radix, via `web/src/shared/ui/tooltip.tsx`) —
   `delayDuration={300}`.
4. `<App />` — renders `<RouterProvider router={router} />`
   (`web/src/app/App.tsx`), delegating all page content to the router.
5. `<Toaster />` (`web/src/shared/ui/sonner.tsx`) — a global toast host
   rendered as a sibling of `<App />`, not nested inside it.

`web/src/app/router.tsx` builds the TanStack Router instance from a
generated route tree (`web/src/app/routeTree.gen.ts`), browser history, and
pathname-keyed scroll restoration. The route tree is generated by the
`@tanstack/router-plugin` Vite plugin (configured in `web/vite.config.ts`)
from the virtual route config in `web/src/app/routes.ts`, which declares one
root route (`root.tsx`) and five children: `index.tsx` (`/`),
`invite.$code.tsx` (`/invite/$code`), `repos.tsx` (`/repos`),
`repos.$repoId.tsx` (`/repos/$repoId`), and `repos.$repoId.blob.$.tsx`
(`/repos/$repoId/blob/$`). `web/src/app/routes/root.tsx` is the one shared
layout: a flex column with a `<main>` that renders the matched child via
`<Outlet />`, adding no navigation chrome of its own.

Every leaf route file follows the same shape: a `createFileRoute(...)` call
whose `component` renders a page component imported from a feature module
under `web/src/features/` — e.g. `index.tsx` renders `ReposPage` from
`web/src/features/repos/ui/`, and `invite.$code.tsx` reads its `$code` path
param and renders `InvitePage` from `web/src/features/invite/ui/`. No route
file carries page-level business logic itself; that is each feature's own
concern.

At the recorded revision, `web/src/features/` holds exactly two feature
areas — `invite` and `repos` — and `web/src/shared/` holds the cross-feature
code every feature may depend on: `lib/` (Nostr client, NIP-98 signing, relay
URL derivation, and other utilities), `theme/`, `styles/globals.css`, and
`ui/` (shadcn/ui-generated primitives — button, card, input, badge, tooltip,
sonner — configured by `web/components.json`, `style: "new-york"`, base color
`zinc`).

## Public interface / boundary

The contract other code is expected to hold to:

- **Mount point.** `web/index.html` declares exactly one `<div id="root">`
  and loads `/src/main.tsx` as a module script. There is no server-rendered
  markup; everything below the mount point is client-rendered.
- **Route registration.** A new page is added by creating a route file under
  `web/src/app/routes/`, registering it in the virtual route config
  `web/src/app/routes.ts`, and having that file's `component` render a page
  from a feature's `ui/` directory — not by editing `root.tsx`,
  `router.tsx`, or `App.tsx`, none of which change per-route.
- **Feature/shared boundary.** Code specific to one feature area lives under
  `web/src/features/<name>/`; code more than one feature (or the app shell
  itself) depends on lives under `web/src/shared/`. `web/components.json`'s
  aliases (`@/shared/ui`, `@/shared/lib`) encode this as the accepted import
  surface for shadcn-generated components and shared utilities.
- **Path alias.** `@/*` resolves to `./src/*`, configured identically in
  `web/tsconfig.json`'s `paths` and `web/vite.config.ts`'s `resolve.alias` —
  the two must be kept in sync for the bundler and the type checker to agree.

## Dependencies

**Depends on** (this shell requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `react`, `react-dom` (19.x) | Rendering runtime | `web/package.json` |
| `@tanstack/react-router`, `@tanstack/router-plugin`, `@tanstack/virtual-file-routes` | File-based routing and its Vite-time code generation | `web/package.json`, `web/vite.config.ts` |
| `@tanstack/react-query` | App-wide data-fetching/cache provider wired in `main.tsx` | `web/package.json`, `web/src/main.tsx` |
| `vite`, `@vitejs/plugin-react`, `typescript` | Build, dev server and type checking (`tsc && vite build`) | `web/package.json` |
| `@biomejs/biome` (via the repo-root config) | Lint and format, extended not redefined | `web/biome.json` |
| Feature modules (`web/src/features/invite`, `web/src/features/repos`) | Supply the page components every route file renders | `web/src/app/routes/index.tsx`, `web/src/app/routes/invite.$code.tsx` |
| Shared modules (`web/src/shared/lib`, `web/src/shared/theme`, `web/src/shared/ui`) | Cross-feature utilities, theming, and shadcn-generated UI primitives used by the shell's own provider stack (`ThemeProvider`, `TooltipProvider`, `Toaster`) | `web/src/main.tsx` |

**Depended on by** (these require this shell):

| Component | Why | Evidence |
|---|---|---|
| Every route file and feature page | Cannot render without the provider stack (`QueryClientProvider`, `ThemeProvider`, `TooltipProvider`) `main.tsx` establishes | `web/src/main.tsx` |
| `buzz-relay`'s static bundle serving | Serves the compiled output of `pnpm -C web build`, which starts from this shell's entry point; the relay-serving contract itself is `architecture-containers-web`'s subject, not this node's | `launchpad/docs/corpus/architecture/containers/web.md` |
| `web/playwright.config.ts`'s `smoke` project | Exercises the shell end-to-end (`vite preview` against the built app) via `web/tests/e2e/smoke.spec.ts` | `web/playwright.config.ts` |
| Repository-root `Justfile` (`web`, `web-check`, `web-fix`, `web-typecheck`, `web-build`, `web-e2e-smoke`) | Thin wrappers that `cd web && pnpm <script>`, giving the rest of the repo a stable entry point into this shell's tooling | `Justfile` |

## Boundary

This node does not describe:

- **How the built bundle is served, deployed, or secured.** That is
  `architecture-containers-web`'s subject (`BUZZ_WEB_DIR`,
  `BUZZ_SERVE_GIT_WEB_GUI`, CORS, the Docker build) — referenced here, not
  restated.
- **Authentication mechanics** (NIP-07 signer detection, NIP-98 request
  signing, the ephemeral read-only identity) — owned by the sibling task for
  `platforms/web/authentication.md` (#1287), not yet drafted at time of
  writing.
- **The invite landing page's own UI and flow** (age/consent gating, the
  Mac-model download chooser, mobile fallback) — owned by the sibling task
  for `platforms/web/invite-ui.md` (#1288), not yet drafted.
- **The relay's own request routing and gating logic** for which paths serve
  this bundle — owned by the sibling task for `platforms/web/relay-serving.md`
  (#1289), not yet drafted, and partly by `architecture-containers-web`
  above.
- **The Git repository browser feature** (`isomorphic-git`, the
  IndexedDB-backed `LightningFS`, tree/blob/commit rendering) — owned by the
  sibling task for `platforms/web/repository-browser.md` (#1290), not yet
  drafted.
- **Class/function-level implementation detail** inside any one feature or
  shared module — this node names the shell's structure and contracts, not
  every function's behavior.

## Relationships

- `references`: `architecture-containers-web` — the container-level node this
  one deliberately does not duplicate (deployment, serving-gate, data,
  security implications for the same `web/` source tree).
- No `part-of` or `depends-on` edge is declared toward the sibling
  `platforms/web/*` nodes (#1287 authentication, #1288 invite-ui, #1289
  relay-serving, #1290 repository-browser): none is merged on
  `origin/launchpad` at the recorded revision, and a `relationships[].target`
  naming an id no loaded node carries is a hard validation error. Once any of
  them merges, a `references` or `part-of` edge in one direction or the other
  is the natural follow-up.

## Scope and omissions

**This node covers** the `web/` application shell: its entry point and
provider stack, its TanStack Router-based routing mechanism and the
route/feature wiring convention, the feature/shared code-organization
boundary, and the app-level build, lint, format and test tooling contract
(`package.json` scripts, the repo-root `Justfile` targets, the file-size and
pubkey-truncation quality gates, Biome and TypeScript configuration).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Deployment, relay-side serving/gating, data and security implications of the same source tree | `architecture-containers-web` |
| Authentication mechanics (NIP-07/NIP-98) | `platforms/web/authentication.md` (#1287), not yet drafted |
| Invite landing page UI/flow | `platforms/web/invite-ui.md` (#1288), not yet drafted |
| Relay-side request routing/gating for this bundle | `platforms/web/relay-serving.md` (#1289), not yet drafted |
| Git repository browser feature (isomorphic-git, IndexedDB, tree/blob rendering) | `platforms/web/repository-browser.md` (#1290), not yet drafted |
| The `admin-web` bundle (separate source tree, not this application) | Not yet documented in this corpus |
| Desktop and mobile clients | Separate platform surfaces, not this node's subject |

**Expected but not verified when this node was written:**

- **Whether `web/src/shared/theme/ThemeToggle.tsx` is dead code or a pending
  feature.** It exists and is exported but is imported nowhere else in
  `web/src` at the recorded revision — flagged here rather than asserted
  either way.
- **Whether every `web/src/features/*` and `web/src/shared/*` file
  individually passes the file-size and pubkey-truncation gates today** —
  this node establishes that the gates exist and what they check
  (`web/scripts/check-file-sizes.mjs`, `web/scripts/check-pubkey-truncation.mjs`),
  not that every current file is currently compliant; that is `pnpm check`'s
  job to report, not this document's.
- **Whether `check-file-sizes.mjs` treats generated files (like
  `routeTree.gen.ts`) differently from hand-authored ones.** Its rule list
  scopes to `src/app`, `src/features` and `src/shared/api` with no visible
  generated-file exemption, but at 144 lines the generated route tree stays
  far under the 1000-line ceiling either way, so this repository's current
  state does not exercise that distinction.
