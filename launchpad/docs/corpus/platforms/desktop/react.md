---
id: platforms-desktop-react
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The desktop app declares react and react-dom ^19.1.0 and @tanstack/react-query ^5.90.21 as direct dependencies."
    entry_class: FACT
    evidence:
      - "desktop/package.json:50"
      - "desktop/package.json:75"
      - "desktop/package.json:77"
  - statement: "desktop/src is organized into three top-level directories: app/ (bootstrap, routing composition, and app-wide providers), features/ (thirty domain feature directories, e.g. channels, chat, agents, workflows, settings), and shared/ (cross-feature reusable code: api/, constants/, context/, hooks/, layout/, lib/, styles/, theme/, ui/), plus testing/ (E2E/mock-bridge support) and types/."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx"
      - "desktop/src/features/channels/hooks.ts"
      - "desktop/src/shared/api/queryClient.ts"
      - "desktop/src/testing/e2eBridge.ts"
  - statement: "A feature directory has no single mandated internal layout, but the largest ones consistently group files under ui/ (components), lib/ (pure helpers) and hooks/ or hooks.ts (React hooks) inside the feature's own directory -- observed directly in features/chat (ui/ only), features/agents (assets/, lib/, ui/) and features/settings (hooks/, lib/, ui/)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/chat/ui/ChatHeader.tsx"
      - "desktop/src/features/agents/lib/personaSaveNotice.ts"
      - "desktop/src/features/agents/ui/AgentConfigFields.tsx"
      - "desktop/src/features/agents/assets/agent-outline.svg"
      - "desktop/src/features/settings/hooks/useSendFeedback.ts"
      - "desktop/src/features/settings/lib/appearanceScopeCopy.ts"
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx"
  - statement: "desktop/src/main.tsx is the single ReactDOM.createRoot bootstrap entry point. Its bootstrap() function runs a fixed sequence of synchronous setup calls (dev-only webview state reset, dev-only E2E bridge configuration from URL params, localStorage quota recovery, density/font-size preference initialization, a localStorage sweep), then awaits the E2E mock-bridge installer and a legacy-community-storage migration, before calling renderApp()."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx:81-137"
  - statement: "renderApp() wraps <App /> in React.StrictMode and a fixed, community-independent provider stack: RootErrorBoundary, CommunitiesProvider, CommunityOnboardingProvider, ThemeProvider, TooltipProvider, EmojiBurstProvider, PoofBurstProvider, UpdaterProvider (plus a sibling NostrBindConsentDialog and Toaster). None of these providers are re-created per community; they wrap App once for the process's lifetime."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx:81-109"
  - statement: "The exported App() function (desktop/src/app/App.tsx) creates one QueryClient via useState(createBuzzQueryClient) and renders it as a QueryClientProvider wrapping MachineBootstrap, before any community is selected; this is a pre-community, process-lifetime React Query client, separate from the per-community one described below."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:800-823"
  - statement: "createBuzzQueryClient (desktop/src/shared/api/queryClient.ts) configures a shared TanStack Query focus-manager listener once (guarded by a module-level boolean) and returns a QueryClient with defaultOptions.queries = { retry: 1, refetchOnWindowFocus: false, networkMode: 'always', gcTime: 5 minutes } and defaultOptions.mutations = { networkMode: 'always' }; both the pre-community and per-community QueryClient instances are built from this same factory."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/queryClient.ts:1-38"
  - statement: "CommunityQueryProvider (desktop/src/app/App.tsx) creates a second, per-community QueryClient via useState(() => createBuzzQueryClient()), and -- when a pubkey and relayUrl are known -- synchronously seeds a project snapshot and starts hydrating channel heads into that client during the state initializer itself (not inside a useEffect), with an inline comment explaining this is required because React Query fires a child's queryFn on subscription, before any parent effect runs."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:218-244"
  - statement: "CommunityApp (desktop/src/app/App.tsx) computes a composite communityKey string from the active community id, a reinit counter, the current pubkey, and a signer-replacement epoch, and applies that same key to both <CommunityQueryProvider key={communityKey}> and the nested <AppReady key={communityKey}>, so a community switch (or an in-place identity replacement) unmounts and remounts both the per-community QueryClient and the AppReady subtree together via React's key-based remount mechanism, rather than the app manually resetting either one's internal state."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:407-421"
      - "desktop/src/app/App.tsx:629-642"
  - statement: "Root CLAUDE.md's Desktop App / Community Switching section documents this same mechanism in prose: '<AppReady key={communityKey} /> in App.tsx forces the entire community-scoped subtree to unmount and remount with fresh state,' and states that module-level singletons (Maps, class instances, cached promises) are not cleared by this remount and must be reset explicitly through resetCommunityState() in useCommunityInit.ts -- a rule about this same React key-based remount pattern's limits, not a separate mechanism."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/src/features/communities/useCommunityInit.ts:47-84"
  - statement: "desktop/src/shared/hooks/useStableReference.ts exports useStableMap and useStableArrayShallow, both of which return the previous render's reference when a freshly recomputed Map or array is value-equal to it, specifically so that a React.memo boundary further down the tree can bail out on an unchanged derived value -- documented in each function's own doc comment as existing because React.memo only skips a re-render when every prop is reference-stable."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/hooks/useStableReference.ts:1-24"
  - statement: "Root CLAUDE.md's Common Gotchas item 6 states the same React.memo constraint in prose ('React.memo is all-or-nothing -- it only skips a re-render when every prop is reference-stable') and names two repeat offenders (a React Query mutation/query result being a new object each render, and derived Map/array state recomputed on a version bump), naming desktop/src/shared/hooks/useStableReference.ts as the mitigation for the second."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/src/shared/hooks/useStableReference.ts"
  - statement: "The desktop app's own component-level tests are co-located *.test.mjs files run by Node's built-in test runner (package.json's test script: node --import ./test-loader.mjs --experimental-strip-types --test \"src/**/*.test.mjs\"), and at least the ones that render React components (e.g. src/app/RootErrorBoundary.test.mjs) construct a JSDOM environment by hand and use @testing-library/react's cleanup/render utilities against it, rather than a browser-based or Vitest-based component test runner."
    entry_class: FACT
    evidence:
      - "desktop/package.json:17"
      - "desktop/src/app/RootErrorBoundary.test.mjs:1-27"
  - statement: "desktop/biome.json (extending the repository-root biome.json) is the desktop app's sole configured linter/formatter, with the 'recommended' rule set enabled and double-quote JS string formatting; desktop/tsconfig.json sets \"strict\": true. Neither configuration file declares any rule restricting which directories a module under desktop/src/features may import from."
    entry_class: FACT
    evidence:
      - "desktop/biome.json:1-29"
      - "desktop/tsconfig.json:23"
  - statement: "A repository-wide search of every desktop/src/features/**/*.{ts,tsx} import statement of the form `from \"@/features/<name>\"` found 1033 cases where the importing file's own feature directory differs from the imported feature name (for example features/onboarding/hooks.ts imports from features/agents, features/channels, features/profile and features/communities), confirming that, unlike the mobile Flutter app's documented rule that feature modules may only import from shared/, the desktop app's feature directories routinely import from one another directly and nothing in its lint configuration restricts this."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='from \"@/features/[a-z0-9-]+', scope='desktop/src/features/**/*.{ts,tsx}') -> 1033 cross-feature matches (e.g. desktop/src/features/onboarding/hooks.ts importing @/features/agents, @/features/channels, @/features/profile, @/features/communities), at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The repository-wide differential file-size ratchet (Justfile's file-size-check target, enforced in just check, CI, and pre-push) applies a 1000-line-per-file cap to desktop/src/app, desktop/src/features, desktop/src/shared/api, desktop/src/shared/context, desktop/src/shared/lib and desktop/src/shared/ui (.ts/.tsx) and desktop/src/shared/styles (.css), but -- per the Justfile's own comment -- 'inspects only files changed from the merge base,' so it is a ratchet against regressions in touched files rather than an absolute cap enforced against every existing file in desktop/src on every run."
    entry_class: FACT
    evidence:
      - "Justfile:96"
      - "Justfile:103-109"
      - "desktop/scripts/check-file-sizes.mjs:8-55"
  - statement: "Root CLAUDE.md's Text sizing & zoom section documents a related, separately-enforced repository convention specific to this React frontend: a CI guard (pnpm check:px-text, desktop/scripts/check-px-text.mjs) scans all of desktop/src and fails on any new arbitrary text-size literal (px or rem/em) that bypasses the app's rem-based, zoom-safe Tailwind typography tokens."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/package.json:9"
  - statement: "architecture-containers-desktop (launchpad/docs/corpus/architecture/containers/desktop.md) exists in the corpus tree on origin/launchpad at the recorded revision and documents the desktop app as one architectural container, naming its React frontend under desktop/src/ without describing that frontend's internal bootstrap, provider composition, or render-perf conventions -- leaving this node's subject undocumented at the container level."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "node.schema.json's type enum has thirteen members and platforms is one of them, described only as 'the corpus surface this node documents' with no further distinguishing text. The already-committed sibling node platforms-desktop-navigation (from this same #1240-#1251 task batch) records the identical reasoning at 0.7 confidence: templates/deployment.md's own evidence ledger states 'this repository's own platform-shaped subject matter is client platforms (desktop/web/mobile), not infrastructure' when explaining its own, different type: platforms choice, which this node treats as confirming platforms is this corpus's established term for the desktop/web/mobile client surface this task's target path (platforms/desktop/react.md) sits under."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/deployment.md:211-212"
    confidence: 0.7
  - statement: "No template in launchpad/docs/corpus/templates/ is written for a platforms-surface node. This node's shape instead follows corpus-template-component's required sections (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) because that template's own scope statement -- 'one software component ... documented as a standalone knowledge artifact' -- matches this task's subject (the React frontend's own architecture as one cohesive layer, not a whole container's decomposition) more closely than corpus-template-architecture-component's, which requires a full building-block table and diagram for every component inside a container. This node departs from that template's own type: implementation recommendation in favor of type: platforms, for the reason given in the INFERENCE above, matching the already-committed platforms-desktop-navigation sibling's identical departure."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/templates/architecture-component.md"
    confidence: 0.65
  - statement: "Issue #1245 requires this node to explain only component-level behavior, not the entire containing platform, and lists platforms/desktop/react.md as its sole in-scope impacted document, with a second hand-authored canonical document explicitly out of scope."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1245 definition of done and out-of-scope list"
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Desktop: React frontend architecture

One paragraph up front, per this node's adapted template: this document
describes the desktop app's React 19 frontend as one architectural layer
inside the `architecture-containers-desktop` container -- how the app boots
and composes its provider tree, how React Query is scoped in two tiers
(pre-community and per-community), how a community switch is driven through
React's own key-based remount mechanism rather than manual state resets, and
the render-performance and file-size conventions specific to this frontend.
It answers: if I need to know how this React app starts up, where a new
provider or feature directory belongs, or why a memoized component isn't
skipping renders, what already exists and where the real answer lives.

## Responsibility

The React frontend layer is responsible for: bootstrapping the single-page
app (`main.tsx`), composing the fixed, community-independent provider stack
that wraps the whole app for its process lifetime, scoping a second,
per-community React Query client that is torn down and rebuilt on a
community switch via React's `key` prop, organizing UI and logic into
`features/` (one directory per domain) and `shared/` (cross-feature reusable
code), and holding the frontend-specific render-performance and file-size
conventions (`React.memo` reference-stability helpers, the differential
file-size ratchet, the rem-based text-sizing lint) that keep 19 React and its
biome/TypeScript toolchain usable at this codebase's size.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `bootstrap()` / `renderApp()` | functions | The single `ReactDOM.createRoot` entry point. Runs a fixed synchronous setup sequence, then awaits the E2E bridge installer and a legacy-storage migration, before rendering `<App />` inside `React.StrictMode` and the fixed provider stack (`RootErrorBoundary`, `CommunitiesProvider`, `CommunityOnboardingProvider`, `ThemeProvider`, `TooltipProvider`, `EmojiBurstProvider`, `PoofBurstProvider`, `UpdaterProvider`). | `desktop/src/main.tsx:81-137` |
| `App()` | component | Creates one process-lifetime `QueryClient` (pre-community) via `createBuzzQueryClient`, and renders `MachineBootstrap` inside its `QueryClientProvider`. | `desktop/src/app/App.tsx:800-823` |
| `createBuzzQueryClient()` | function | Shared factory for every `QueryClient` in the app (pre-community and per-community): `retry: 1`, `refetchOnWindowFocus: false`, `networkMode: "always"`, `gcTime: 5m`; configures the TanStack focus-manager listener once, guarded by a module-level flag. | `desktop/src/shared/api/queryClient.ts:1-38` |
| `CommunityQueryProvider` | component | Creates a second, per-community `QueryClient`, seeding a project snapshot and channel-head hydration synchronously in the `useState` initializer (not an effect) when a pubkey/relayUrl are known, because React Query fires a subscribed child's `queryFn` before any parent effect runs. | `desktop/src/app/App.tsx:218-266` |
| `communityKey` / `key={communityKey}` | pattern | A composite string (community id, reinit counter, pubkey, signer epoch) applied as the React `key` on both `CommunityQueryProvider` and the nested `AppReady`, so a community switch or in-place identity replacement remounts both the per-community query client and the community-scoped subtree together via React's own reconciliation, rather than an imperative reset. | `desktop/src/app/App.tsx:407-421`, `desktop/src/app/App.tsx:629-642` |
| `useStableMap` / `useStableArrayShallow` | hooks | Return the previous render's reference when a freshly recomputed `Map`/array is value-equal to it, so a downstream `React.memo` boundary can bail on an otherwise-fresh derived value. | `desktop/src/shared/hooks/useStableReference.ts:1-24` |
| `features/*`, `shared/*` directories | convention | `features/` holds thirty domain-scoped directories, each typically grouping its own `ui/`, `lib/`, and `hooks/`/`hooks.ts`; `shared/` holds cross-feature reusable code (`api/`, `constants/`, `context/`, `hooks/`, `layout/`, `lib/`, `styles/`, `theme/`, `ui/`). | `desktop/src/features/channels/hooks.ts`, `desktop/src/shared/api/queryClient.ts` |

## Dependencies

**Depends on** (this layer requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `react`, `react-dom` (^19.1.0) | The rendering framework itself. | `desktop/package.json:75,77` |
| `@tanstack/react-query` (^5.90.21) | Backs both the pre-community and per-community `QueryClient` instances this layer creates and provides. | `desktop/package.json:50` |
| `@testing-library/react`, Node's built-in test runner, `jsdom` | Component-level test infrastructure: co-located `*.test.mjs` files construct a JSDOM environment and use Testing Library's `render`/`cleanup` against it. | `desktop/package.json:17`, `desktop/src/app/RootErrorBoundary.test.mjs:1-27` |
| `biome` | The desktop app's sole configured linter/formatter (`recommended` rules, double-quote JS strings); `tsconfig.json` additionally enables TypeScript `strict` mode. | `desktop/biome.json:1-29`, `desktop/tsconfig.json:23` |

**Depended on by** (these require this layer):

| Component | Why | Evidence |
|---|---|---|
| Every module under `desktop/src/features/*` and `desktop/src/app/*` | All UI in the desktop app is a React component tree rendered through the `main.tsx` bootstrap described above; there is no non-React rendering path in this container. | `desktop/src/main.tsx:81-109` |
| `platforms-desktop-navigation` (routing) | The routing layer's `router` singleton and `AppShell` render inside this layer's `App()`/`renderApp()` composition, not independently of it. | `desktop/src/app/App.tsx:800-823` |

## Boundary

This node does not describe:
- **Client-side routing itself** (route table, the router singleton, navigation
  guards, back/forward handling) -- that is `platforms-desktop-navigation`'s
  subject. This node covers only the provider/bootstrap layer that renders the
  router's output.
- **The Tauri frontend-backend IPC bridge** (command registration,
  `invokeTauri`, case-conversion rules) -- that is
  `platforms-desktop-frontend-backend-bridge`'s subject.
- **React Query's own caching/invalidation semantics and community-scoped
  state singletons in depth** -- this node states only that two `QueryClient`
  tiers exist and how they are scoped and remounted; the state-management
  task in this same batch (`platforms/desktop/state-management.md`, unmerged
  at the time of writing) is the intended owner of that deeper detail.
- **The Tauri native shell** (window management, packaging, updater) -- those
  are separate sibling tasks in this batch (`platforms/desktop/tauri.md`,
  `platforms/desktop/packaging.md`, `platforms/desktop/updater.md`), unmerged
  at the time of writing.
- **Any individual feature's business logic** under `desktop/src/features/*`
  -- each is its own potential future corpus node; this node documents the
  frontend-wide bootstrap, composition and conventions they are all built on,
  not what any one feature does.
- **The desktop container's own deployment topology, security boundary, or
  its outbound interfaces to the relay and managed-agent subprocesses** --
  see `architecture-containers-desktop` for those.

## Relationships

- part-of: `architecture-containers-desktop`

## Scope and omissions

**This node covers** the desktop app's React 19 frontend as one architectural
layer: the `main.tsx`/`App()` bootstrap and provider composition, the
two-tier (pre-community/per-community) React Query client scoping, the
`communityKey` React-key-based remount mechanism for community switches, the
`features/`/`shared/` directory convention, the co-located
Node-test-runner-plus-Testing-Library component test convention, and the
frontend-specific tooling conventions (biome, TypeScript strict mode, the
`React.memo` reference-stability helpers, the differential file-size ratchet,
and the rem-based text-sizing lint).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Client-side routing and navigation | `platforms-desktop-navigation` (already documented) |
| The Tauri frontend-backend IPC bridge | `platforms-desktop-frontend-backend-bridge` (already documented) |
| React Query caching/invalidation semantics and community-scoped state singletons, in depth | `platforms/desktop/state-management.md`, unmerged at time of writing |
| The Tauri native shell, packaging, and the updater | `platforms/desktop/tauri.md`, `platforms/desktop/packaging.md`, `platforms/desktop/updater.md`, unmerged at time of writing |
| Any individual feature's business logic | Not yet assigned per-feature corpus nodes at the recorded revision |
| The desktop container's overall responsibility, technology and security boundary | `architecture-containers-desktop` |
| Whether `type: platforms` is this corpus's settled convention for every `platforms/*` node, versus a convention this batch of tasks is establishing by precedent | Not resolved here; recorded as an `INFERENCE` above, matching the identical open question already recorded in the `platforms-desktop-navigation` sibling |

**Expected but not verified when this node was written:**

- **`desktop/src/shared/features/`** (a feature-*flag* system --
  `FeatureGate`, `manifest.ts`, `resolveEnabled.ts` -- distinct in meaning
  from the `desktop/src/features/` domain-feature directories this node
  documents) was seen by directory listing only and not opened in depth; it
  is plausibly its own future corpus node rather than this one's subject, and
  is named here only to avoid confusing the two similarly-named concepts
  silently.
- **Whether every one of the thirty `features/*` directories follows the
  `ui/`/`lib/`/`hooks/` internal grouping** was checked against three
  examples (`chat`, `agents`, `settings`), not all thirty; the *Public
  interface* row above is stated as "typically," not universally.
- **No other node from this task batch (#1240-#1251) other than the four
  already committed at authoring time (deep-links, frontend-backend-bridge,
  local-agent-management, navigation) was read in full** -- the boundary
  statements above referencing `state-management.md`, `tauri.md`,
  `packaging.md` and `updater.md` are based on their issue titles in the
  batch list, not on reading their (not yet existing) content.
