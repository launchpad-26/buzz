---
id: implementation-web-feature-map
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "web/ is a Vite + React 19 + TypeScript single-page application (buzz-web) whose routing surface is exactly six TanStack Router file routes under web/src/app/routes/: index (repo list), root (layout shell), invite.$code (invite landing), repos (redirects to /), repos.$repoId (repo detail), and repos.$repoId.blob.$ (blob viewer)."
    entry_class: FACT
    evidence:
      - "web/package.json"
      - "web/src/app/routes/index.tsx"
      - "web/src/app/routes/root.tsx"
      - "web/src/app/routes/invite.$code.tsx"
      - "web/src/app/routes/repos.tsx"
      - "web/src/app/routes/repos.$repoId.tsx"
      - "web/src/app/routes/repos.$repoId.blob.$.tsx"
  - statement: "web/src/app/routes/repos.tsx does not render its own page; its component is `() => <Navigate to=\"/\" />`, so /repos immediately redirects to the index route (also ReposPage) rather than being a distinct page."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/repos.tsx"
  - statement: "web/src/app/router.tsx and web/src/app/App.tsx are the only two files wiring the route tree to a rendered app: App.tsx renders a single <RouterProvider router={router} />, and router.tsx builds that router from the generated web/src/app/routeTree.gen.ts with browser history and scroll restoration keyed by pathname. web/src/app/routes.ts is the virtual-file-routes config (@tanstack/virtual-file-routes) that routeTree.gen.ts is generated from, listing each route file against its path."
    entry_class: FACT
    evidence:
      - "web/src/app/App.tsx"
      - "web/src/app/router.tsx"
      - "web/src/app/routes.ts"
  - statement: "web/src/main.tsx is the application entry point: it mounts <App/> wrapped in a TanStack Query QueryClientProvider (retry: 1, refetchOnWindowFocus: false, networkMode: \"always\"), ThemeProvider, TooltipProvider and a sonner Toaster, and imports the Inter variable font and global Tailwind styles."
    entry_class: FACT
    evidence:
      - "web/src/main.tsx"
  - statement: "The repos feature (web/src/features/repos/) has eleven UI components under ui/ (ConnectButton, OrgSidebar, PubkeyAvatar, RepoBlobViewer, RepoCommitsSection, RepoDetailPage, RepoListItem, RepoReadmeSection, RepoRefsSection, RepoTreeSection, ReposPage) and five non-UI modules at its root (git-client.ts, mock-repos.ts, use-git-browse.ts, use-repo-context.ts, use-repo-refs.ts, use-repos.ts)."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/ConnectButton.tsx"
      - "web/src/features/repos/ui/OrgSidebar.tsx"
      - "web/src/features/repos/ui/PubkeyAvatar.tsx"
      - "web/src/features/repos/ui/RepoBlobViewer.tsx"
      - "web/src/features/repos/ui/RepoCommitsSection.tsx"
      - "web/src/features/repos/ui/RepoDetailPage.tsx"
      - "web/src/features/repos/ui/RepoListItem.tsx"
      - "web/src/features/repos/ui/RepoReadmeSection.tsx"
      - "web/src/features/repos/ui/RepoRefsSection.tsx"
      - "web/src/features/repos/ui/RepoTreeSection.tsx"
      - "web/src/features/repos/ui/ReposPage.tsx"
      - "web/src/features/repos/git-client.ts"
      - "web/src/features/repos/mock-repos.ts"
      - "web/src/features/repos/use-git-browse.ts"
      - "web/src/features/repos/use-repo-context.ts"
      - "web/src/features/repos/use-repo-refs.ts"
      - "web/src/features/repos/use-repos.ts"
  - statement: "web/src/features/repos/use-repos.ts derives a Repo from a NIP-34-shaped Nostr event's tags (d, name, description, clone, web, buzz-channel, p for contributors) via queryEvents against the relay WebSocket, and separately exposes a `dedup` helper that keeps only the latest event per (pubkey, kind, d-tag), matching NIP-33 parameterized-replaceable-event semantics."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repos.ts"
  - statement: "web/src/features/repos/mock-repos.ts is not a production data source: use-repos.ts's useRepo only selects it when called with { preview: true }, and web/src/features/repos/ui/ReposPage.tsx only sets that flag when import.meta.env.DEV is true and the page URL carries a `?preview=repositories` or `?preview=empty` query parameter — a dev-only design-preview aid, gated out of production builds by the DEV check."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repos.ts"
      - "web/src/features/repos/ui/ReposPage.tsx"
  - statement: "web/src/features/repos/git-client.ts is an isomorphic-git wrapper for in-browser repo browsing; its header comment states it uses LightningFS (IndexedDB-backed) for persistence and NIP-98 auth for the relay's smart HTTP git transport, and it installs a global Buffer polyfill (the `buffer` package) before any isomorphic-git import runs, since isomorphic-git expects Node's Buffer API."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
  - statement: "web/src/features/repos/ui/RepoBlobViewer.tsx's own header comment states it is designed to be safe by construction: no JS/HTML execution path, no SVG rendered as an image (SVG can carry active content, so it is rendered as text instead), and a hard preview-size cap with a download fallback for anything over that limit; object URLs for image/binary blobs are created in a local effect and revoked on unmount or input change, never cached inside React Query results."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoBlobViewer.tsx"
  - statement: "web/src/features/repos/use-repo-context.ts's header comment describes it as the shared resolver for the (owner, repoName, defaultRef) triple every repo-scoped page needs, combining the NIP-34 announcement (useRepo) with the refs query (useRepoRefs) so callers do not duplicate that wiring, and states that defaultRef falls back to \"main\" until refs load."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repo-context.ts"
  - statement: "The invite feature (web/src/features/invite/) has one non-UI module (invite-api.ts) and two UI components under ui/ (InvitePage.tsx, InviteJoinPolicyNotice.tsx); invite-api.ts's claimInviteInBrowser POSTs a NIP-98-authenticated request (via makeNip98AuthHeader) to `{relayHttpBaseUrl()}/api/invites/claim` with the invite code and an optional policy_receipt, on a 15-second timeout."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/invite-api.ts"
      - "web/src/features/invite/ui/InvitePage.tsx"
      - "web/src/features/invite/ui/InviteJoinPolicyNotice.tsx"
  - statement: "web/src/features/invite/ui/InvitePage.tsx imports platform-download helpers from web/src/shared/lib/buzz-download.ts (detectBuzzDownloadPlatform, resolveBuzzDownloadUrlForPlatform, BUZZ_RELEASES_URL) and a NIP-07-presence check from web/src/shared/lib/nostr-signer.ts (hasNip07Provider), tying the invite landing page to both the desktop-download prompt and the browser-signer capability check."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx"
  - statement: "web/src/shared/lib/ holds eight modules with single, narrowly named responsibilities: buzz-download.ts (platform detection + GitHub-releases download URL resolution, cached for one hour under a versioned localStorage key), cn.ts (clsx + tailwind-merge className helper), nip98.ts (NIP-98 kind:27235 Authorization header construction), nostr-client.ts (minimal NIP-01/NIP-42 relay WebSocket client), nostr-signer.ts (NIP-07 detection plus an ephemeral in-page keypair signer via nostr-tools/pure), pubkey.ts (the one canonical truncated-pubkey display form, its own comment noting it mirrors desktop's equivalent and is a recognition aid, never an identity proof), relative-time.ts (Unix-timestamp-to-relative-string formatting), and relay-url.ts (relay WS/HTTP base URL derivation)."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/buzz-download.ts"
      - "web/src/shared/lib/cn.ts"
      - "web/src/shared/lib/nip98.ts"
      - "web/src/shared/lib/nostr-client.ts"
      - "web/src/shared/lib/nostr-signer.ts"
      - "web/src/shared/lib/pubkey.ts"
      - "web/src/shared/lib/relative-time.ts"
      - "web/src/shared/lib/relay-url.ts"
  - statement: "web/src/shared/ui/ holds six UI primitives (badge.tsx, button.tsx, card.tsx, input.tsx, sonner.tsx, tooltip.tsx) and web/src/shared/theme/ holds two theme modules (ThemeProvider.tsx, ThemeToggle.tsx); these are the app's only shared, cross-feature UI building blocks."
    entry_class: FACT
    evidence:
      - "web/src/shared/ui/badge.tsx"
      - "web/src/shared/ui/button.tsx"
      - "web/src/shared/ui/card.tsx"
      - "web/src/shared/ui/input.tsx"
      - "web/src/shared/ui/sonner.tsx"
      - "web/src/shared/ui/tooltip.tsx"
      - "web/src/shared/theme/ThemeProvider.tsx"
      - "web/src/shared/theme/ThemeToggle.tsx"
  - statement: "web/package.json defines the web app's own quality-gate scripts, distinct from repository-root `just` targets: build (tsc && vite build), typecheck (tsc --noEmit), check:file-sizes and check:pubkey-truncation (two custom Node scripts under web/scripts/), lint and check (biome), and test:e2e / test:e2e:smoke (build then Playwright)."
    entry_class: FACT
    evidence:
      - "web/package.json"
      - "web/scripts/check-file-sizes.mjs"
      - "web/scripts/check-pubkey-truncation.mjs"
  - statement: "The only Playwright spec in web/ is web/tests/e2e/smoke.spec.ts, and web/playwright.config.ts's smoke project runs it against a Vite preview server bound to 127.0.0.1:4173 after a build — the same shape already documented for this pairing in architecture-containers-web."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
      - "web/playwright.config.ts"
  - statement: "architecture-containers-web (merged on origin/launchpad) already documents the web container's two responsibilities (invite landing, Git repository browser), its inbound/outbound interfaces, and its relay-served deployment shape; this node does not restate that content and instead maps those responsibilities onto the concrete source directories and files that realize them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
  - statement: "Issue #952 (\"task: document implementation/web/web-app.md\"), unmerged at time of writing, is a separate task in the same batch that owns a deeper implementation-reference node for the web app's internals; this node deliberately stays at map/breadth depth rather than duplicating that scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#952 (issue title and Objective, checked via gh issue view)"
relationships:
  - type: part-of
    target: architecture-containers-web
---

# Web app: feature-to-directory map (implementation reference)

This node documents `web/` — the Buzz browser web client (Vite + React 19 +
TypeScript) — as an implementation surface: which source directories and files
realize the two responsibilities `architecture-containers-web` already
declares for this container (invite landing, in-browser Git repository
browser), plus the routing and shared-library scaffolding both depend on. It
is a **map**, not a deep-dive: it names what exists and where, at
file/module grain, without tracing internal control flow, render logic, or
line-level behavior. That depth is sibling issue #952's
(`implementation/web/web-app.md`), explicitly out of scope here — see *Scope
and omissions*.

## Target

What this node maps is the responsibility surface `architecture-containers-web`
already states, in `launchpad/docs/corpus/architecture/containers/web.md`
(corpus node id `architecture-containers-web`, merged on `origin/launchpad`):
an invite-acceptance landing page and a read-only Git repository browser,
compiled to static assets and served by `buzz-relay` itself. That node
documents the *what* and the *why* (responsibility, inbound/outbound
interfaces, deployment, security). This node documents the *where*: which
files under `web/src/` implement each piece of that surface.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `web/src/app/routes/index.tsx` | Repository browser — root route (`/`) | Renders `ReposPage`. |
| `web/src/app/routes/root.tsx` | App shell layout | `createRootRoute`; wraps every route in a flex column with an `<Outlet/>`. |
| `web/src/app/routes/repos.tsx` | Repository browser — `/repos` | Redirects to `/` via `<Navigate to="/" />`; not an independent page. |
| `web/src/app/routes/repos.$repoId.tsx` | Repository browser — repo detail (`/repos/:repoId`) | Renders `RepoDetailPage`. |
| `web/src/app/routes/repos.$repoId.blob.$.tsx` | Repository browser — blob viewer (`/repos/:repoId/blob/*`) | Renders `RepoBlobPage` (exported from `RepoBlobViewer.tsx`). |
| `web/src/app/routes/invite.$code.tsx` | Invite landing (`/invite/:code`) | Renders `InvitePage` with the route's `code` param. |
| `web/src/app/router.tsx`, `web/src/app/routeTree.gen.ts`, `web/src/app/App.tsx`, `web/src/app/routes.ts` | Routing scaffolding shared by both responsibilities | TanStack Router setup; `routeTree.gen.ts` is generated from `routes.ts`, not hand-authored. |
| `web/src/main.tsx` | App entry point shared by both responsibilities | Mounts `<App/>` inside `QueryClientProvider`, `ThemeProvider`, `TooltipProvider`, `Toaster`. |
| `web/src/features/repos/ui/ReposPage.tsx` | Repository browser — repo list page | Search/sort over repos; dev-only `?preview=` mock-data mode. |
| `web/src/features/repos/ui/RepoDetailPage.tsx` | Repository browser — repo detail page | Assembles refs/readme/tree/commits sections for one repo. |
| `web/src/features/repos/ui/RepoTreeSection.tsx` | Repository browser — file/tree listing | Sub-tree navigation into folders is not implemented (folders render `aria-disabled`). |
| `web/src/features/repos/ui/RepoReadmeSection.tsx` | Repository browser — rendered README | Renders Markdown via `react-markdown` + `remark-gfm`. |
| `web/src/features/repos/ui/RepoCommitsSection.tsx` | Repository browser — commit log display | Renders `CommitInfo` rows (author, relative time, short oid). |
| `web/src/features/repos/ui/RepoRefsSection.tsx` | Repository browser — branch/tag display | Renders `RepoRefs` (branches, tags, head). |
| `web/src/features/repos/ui/RepoBlobViewer.tsx` | Repository browser — blob viewer | Safe-by-construction: no script execution, SVG rendered as text, preview-size cap with download fallback. |
| `web/src/features/repos/ui/RepoListItem.tsx` | Repository browser — one repo row | Used by both the real list and the `preview` mock-data path. |
| `web/src/features/repos/ui/OrgSidebar.tsx` | Repository browser — contributor/owner sidebar | Deduplicates pubkeys across repos, caps avatars at 20. |
| `web/src/features/repos/ui/PubkeyAvatar.tsx` | Repository browser — pubkey-derived avatar | Deterministic hue from a hash of the hex pubkey; no image fetch. |
| `web/src/features/repos/ui/ConnectButton.tsx` | Repository browser — "Open in Buzz" deep link | Builds a `buzz://connect?relay=...` link from `relayWsUrl()`. |
| `web/src/features/repos/use-repos.ts` | Repository browser — repo list/detail data | Maps NIP-34-shaped Nostr events to `Repo`; NIP-33 `dedup` helper. |
| `web/src/features/repos/use-repo-refs.ts` | Repository browser — branch/tag data | Queries and parses ref events into `RepoRefs`. |
| `web/src/features/repos/use-repo-context.ts` | Repository browser — shared `(owner, repoName, defaultRef)` resolver | Combines `useRepo` + `useRepoRefs`; used by every repo-scoped page. |
| `web/src/features/repos/use-git-browse.ts` | Repository browser — in-browser Git reads | React Query hooks over `git-client.ts` (clone, tree, blob, commit log, README). |
| `web/src/features/repos/git-client.ts` | Repository browser — isomorphic-git transport | Clones/fetches via NIP-98-authed smart HTTP into an IndexedDB `LightningFS`. |
| `web/src/features/repos/mock-repos.ts` | Repository browser — dev-only preview data | Not reachable in production; gated by `import.meta.env.DEV` + `?preview=`. |
| `web/src/features/invite/ui/InvitePage.tsx` | Invite landing — join page | Renders join UI; checks NIP-07 presence; links platform-specific downloads. |
| `web/src/features/invite/ui/InviteJoinPolicyNotice.tsx` | Invite landing — terms/privacy/age consent | Renders `terms_markdown` / `privacy_markdown`, an age-attestation checkbox. |
| `web/src/features/invite/invite-api.ts` | Invite landing — claim call | `POST {relay}/api/invites/claim`, NIP-98-authenticated, 15s timeout. |
| `web/src/shared/lib/nostr-client.ts` | Shared — relay WebSocket client | Used by both `use-repos.ts`/`use-repo-refs.ts` and (indirectly) invite flow. |
| `web/src/shared/lib/nip98.ts` | Shared — NIP-98 auth header construction | Used by `git-client.ts` and `invite-api.ts`. |
| `web/src/shared/lib/nostr-signer.ts` | Shared — NIP-07 detection + ephemeral signer | Used by `InvitePage.tsx`; ephemeral identity path used by `nostr-client.ts`. |
| `web/src/shared/lib/relay-url.ts` | Shared — relay WS/HTTP base URL derivation | Same-origin by default; `VITE_RELAY_URL` override. |
| `web/src/shared/lib/pubkey.ts` | Shared — canonical pubkey truncation | Mirrors desktop's equivalent per its own header comment. |
| `web/src/shared/lib/relative-time.ts` | Shared — relative timestamp formatting | Used by `RepoListItem.tsx`, `RepoDetailPage.tsx`, `RepoCommitsSection.tsx`. |
| `web/src/shared/lib/buzz-download.ts` | Shared — platform-specific download URL resolution | Used by `InvitePage.tsx`; caches the GitHub releases lookup for one hour. |
| `web/src/shared/lib/cn.ts` | Shared — className merge helper | `clsx` + `tailwind-merge`; used throughout `ui/`. |
| `web/src/shared/ui/*.tsx` (badge, button, card, input, sonner, tooltip) | Shared — UI primitives | `button.tsx` is the only one imported by both feature areas; `badge`/`input`/`tooltip` are used only within `features/repos/ui/`; `sonner.tsx`'s `Toaster` is mounted once from `main.tsx`, not per-feature; `card.tsx` has no importer found under `web/src`. |
| `web/src/shared/theme/ThemeProvider.tsx`, `ThemeToggle.tsx` | Shared — light/dark theme | Wraps the whole app from `main.tsx`. |

## Divergences

No divergence was found between this map and `architecture-containers-web`'s
stated responsibility surface: every source file under `web/src/` sits under
either `features/repos/` (Git repository browser), `features/invite/`
(invite landing), `app/` (routing scaffolding), or `shared/` (libraries and
UI primitives both features depend on), which matches that node's own
two-responsibility description exactly. Checked by running `find web/src
-type f` and placing every result in the table above except a small,
explicitly-named set of non-feature files — build/type declarations
(`vite-env.d.ts`), a placeholder (`features/.gitkeep`), a static asset
(`assets/app-icon@3x.png`), and the global stylesheet (`shared/styles/globals.css`)
— listed in *Scope and omissions* rather than given a table row, since none
of them realize a responsibility.

One internal inconsistency was found and is recorded here rather than
smoothed over: `RepoTreeSection.tsx` renders folder rows as
`aria-disabled="true"` with a code comment stating "sub-tree navigation is
deferred" — the repository browser's tree view does not yet support
navigating into subdirectories, a real functional gap in the responsibility
`architecture-containers-web` describes as "browse trees/blobs/refs/commits."
This node does not own fixing it; it is named here because a map that hid it
would misrepresent the surface it maps.

## Verification

The only automated verification exercising this surface end-to-end is
`web/tests/e2e/smoke.spec.ts`, run via `pnpm -C web test:e2e:smoke` against a
Playwright-driven Vite preview server (`web/playwright.config.ts`'s `smoke`
project, `127.0.0.1:4173`). No component-level or unit tests were found under
`web/src/`. `web/package.json`'s `check` script (biome lint/format plus the
`check:pubkey-truncation` custom script) and `typecheck` (`tsc --noEmit`) are
static gates, not behavioral verification of the feature surface itself. This
node makes no claim about `web/tests/e2e/smoke.spec.ts`'s actual scenario
coverage — that is unread depth left to #952 or a future verification-focused
node.

## Relationships

- part-of: `architecture-containers-web` — this node is a narrower,
  implementation-level breakdown of the same container that node documents at
  the architecture level.
- implements: none. This map does not trace code to a spec, decision, or
  contract node (the shape `implements` is for per the template's own
  boundary section); it traces an already-documented container's stated
  responsibilities to the source files that realize them, which `part-of`
  more accurately describes.
- references: none. No verification/test-strategy corpus node exists yet for
  this surface to cite.

## Scope and omissions

**This node covers** a feature-to-directory/file map of `web/`'s two
responsibilities (invite landing, Git repository browser) and their shared
routing/library scaffolding, at file and module grain, checked against
`architecture-containers-web`'s existing responsibility statement.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Internal control flow, render logic, and line-level behavior of any file in the table above | #952 (`implementation/web/web-app.md`, unmerged at time of writing) |
| The relay-side serving, deployment, and security implications of this bundle (`BUZZ_WEB_DIR`, `BUZZ_SERVE_GIT_WEB_GUI`, CORS) | `architecture-containers-web`, already documented there |
| The `admin-web` bundle (a separate source tree and container) | Not yet documented in this corpus, per `architecture-containers-web`'s own scope table |
| Desktop and mobile clients | Separate containers, not yet documented in this corpus |
| `web/tests/e2e/smoke.spec.ts`'s actual scenario coverage | Unread depth; a future verification-focused node |
| Whether the missing sub-tree navigation in `RepoTreeSection.tsx` is tracked as a known gap or an open issue | Not checked; named as a real functional gap above but no issue search was run for it |
| `web/src/vite-env.d.ts` (Vite ambient type declarations), `web/src/features/.gitkeep` (empty placeholder), `web/src/assets/app-icon@3x.png` (static image asset), `web/src/shared/styles/globals.css` (global stylesheet) | Not given implementation-surface rows — none realizes a responsibility; each is confirmed to exist by `find web/src -type f` |

**Expected but not verified when this node was written:**

- **Whether `git-client.ts`'s IndexedDB `LightningFS` store has any eviction
  or size-limit behavior** — `architecture-containers-web` already flags this
  as unverified, and nothing found while building this map resolves it.
- **Whether `web/src/shared/lib/nostr-client.ts`'s ephemeral-identity fallback
  and `nostr-signer.ts`'s NIP-07 detection are exercised by
  `smoke.spec.ts`** — the spec's scenario content was not opened for this
  node.
- **Whether any file listed here has changed shape on `origin/launchpad`
  since the recorded revision** — this node was checked once, against the
  commit in the evidence ledger.
