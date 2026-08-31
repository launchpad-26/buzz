---
id: implementation-desktop-frontend
type: implementation
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "The desktop frontend's declared dependency versions are react ^19.1.0, react-dom ^19.1.0, vite ^8.0.0, tailwindcss ^4.3.0, @tauri-apps/api ~2.11, @tanstack/react-router ^1.168.10 and @tanstack/react-query ^5.90.21."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
  - statement: "desktop/package.json's `check` script runs `biome check .` followed by `pnpm check:px-text` and `pnpm check:pubkey-truncation`; `check:px-text` runs `node ./scripts/check-px-text.mjs`, and a separate `desktop/biome.json` (distinct from the repo-root `biome.json`) configures Biome for this package."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
  - statement: "desktop/scripts/check-px-text.mjs scans all of desktop/src across .ts/.tsx/.css files for arbitrary px or rem text-size literals, allowlists four specific decorative-glyph literals by exact relativePath:matchedLiteral, and states in its own comment that the guard exists because the rem-to-px zoom regression (PR #891) landed in the message-timeline render path and arbitrary text literals had drifted across the whole app before the guard was widened to scan all of src."
    entry_class: FACT
    evidence:
      - "desktop/scripts/check-px-text.mjs"
  - statement: "desktop/src/app/useWebviewZoomShortcuts.ts implements Cmd/Ctrl +/-/0 by writing document.documentElement.style.fontSize directly (BASE_FONT_SIZE_PX=16 times a zoomFactor clamped between 0.75 and 1.5 in 0.1 steps), persists the chosen factor to localStorage under the key buzz:text-scale, listens for cross-window `storage` events to stay in sync, and separately pins the native Tauri webview's own zoom to 1 via `getCurrentWebview().setZoom(1)` so the rem-scaled root font-size is the only zoom mechanism in effect."
    entry_class: FACT
    evidence:
      - "desktop/src/app/useWebviewZoomShortcuts.ts"
  - statement: "desktop/src/app/App.tsx computes a single `communityKey` string (template-composed from the active community id, a reinitKey, the current pubkey, and a signerEpoch) and passes it as the React `key` prop to both `CommunityQueryProvider` and `AppReady`, so a community, identity, or signer-epoch change forces React to unmount and remount that entire subtree rather than diffing it; a code comment on the identical pattern at the CommunityQueryProvider call site explicitly names this as the mechanism for rebuilding \"the entire community boundary (query client, AppReady subtree, module singletons via useCommunityInit)\" so a replacement identity never inherits the previous identity's cached state."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx"
  - statement: "desktop/src/features/communities/useCommunityInit.ts defines an async `resetCommunityState` function whose own doc comment states it tears down \"all community-scoped module singletons so the new community starts with a clean slate\" and names hook-managed singletons as destroyed via effect cleanup instead, pointing to AGENTS.md's \"Community Switching\" section as the fuller contract; the function's body calls 21 distinct reset/clear/disconnect functions (relayClient.disconnect, resetNavigationDeepLinkDrain, resetRateLimitGate, clearAllDrafts, resetAgentObserverStore, resetActiveAgentTurnsStore, resetAgentWorkingSignal, clearTrayAgentActivity [gated on Tauri+macOS], resetAvatarProfileSync, resetAvatarPresentations [both gated on resetAvatarState], resetSidebarRelayConnectionCardState, resetMediaCaches, resetLinkPreviewMetadataCache, resetVideoPlayerState, resetRenderScopedReactionHydration, resetBackgroundMediaUploads, resetLinkPreviewPreparations, resetPersistentAgentAudienceStore, clearSearchHitEventCache, clearMarkdownNodeCache, resetMessageLinkMetadataCache), confirming this is a large, actively maintained inventory rather than a stub."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts"
  - statement: "desktop/src/shared/hooks/useStableReference.ts exports useStableMap, useStableArrayShallow and useStableSet, each returning the previous object/array/Set reference when the new value is structurally equal to the old one, with the file's own comments stating the purpose is letting \"a value that is recomputed into a fresh Map on an unrelated invalidation... keep a stable identity so downstream React.memo boundaries can bail\"; these hooks are called from at least seven other frontend files, including desktop/src/features/channels/useUnreadChannels.ts and desktop/src/features/channels/ui/useChannelUnreadState.ts, confirming real (not merely illustrative) use in the channel-unread render path."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/hooks/useStableReference.ts"
      - "desktop/src/features/channels/useUnreadChannels.ts"
      - "desktop/src/features/channels/ui/useChannelUnreadState.ts"
  - statement: "desktop/src/features/home/useInboxEditMessage.ts calls React Query's useEditMessageMutation and immediately re-wraps its `mutateAsync` in a React.useRef (assigned fresh on every render, read only inside a useCallback with an empty dependency array), rather than depending on the mutation object itself, which is the concrete instance of the \"depend on the stable method, not the object\" React Query guidance CLAUDE.md states in prose."
    entry_class: FACT
    evidence:
      - "desktop/src/features/home/useInboxEditMessage.ts"
  - statement: "desktop/src/app/main.tsx's `renderApp` nests, from outside in: React.StrictMode, RootErrorBoundary, CommunitiesProvider, CommunityOnboardingProvider, ThemeProvider (defaultTheme=\"buzz\"), TooltipProvider, EmojiBurstProvider, PoofBurstProvider, UpdaterProvider (wrapping App and NostrBindConsentDialog), and Toaster as a PoofBurstProvider sibling; this is the concrete provider hierarchy CLAUDE.md's \"Key files\" list names main.tsx for without spelling out the order."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx"
  - statement: "desktop/src/features/ contains 29 feature subdirectories at this revision (agent-memory, agents, channel-templates, channels, chat, communities, community-members, custom-emoji, forum, gifs, home, huddle, identity-archive, local-archive, mesh-compute, messages, moderation, notifications, onboarding, presence, profile, projects, pulse, reminders, search, settings, sidebar, terminal, user-status, workflows), confirming CLAUDE.md's \"organized under desktop/src/features/\" claim structurally but at a scale this node deliberately does not catalogue feature-by-feature."
    entry_class: FACT
    evidence:
      - "ls('desktop/src/features/') -> 29 entries: agent-memory, agents, channel-templates, channels, chat, communities, community-members, custom-emoji, forum, gifs, home, huddle, identity-archive, local-archive, mesh-compute, messages, moderation, notifications, onboarding, presence, profile, projects, pulse, reminders, search, settings, sidebar, terminal, user-status, workflows"
  - statement: "desktop/src/app/App.tsx routes rendering through @tanstack/react-router's RouterProvider (a `router` object imported from desktop/src/app/router.tsx, with a generated desktop/src/app/routeTree.gen.ts), not React Router or a hand-rolled router, which CLAUDE.md's own prose does not name."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx"
  - statement: "The architecture corpus node architecture-containers-desktop states in its own Scope and omissions section: \"The React frontend's internal feature/component architecture — only its existence and IPC-only relationship to the backend is claimed here,\" explicitly leaving the concrete frontend structure this node documents unclaimed by that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "No other implementation-typed corpus node exists in the corpus tree at this task's merge base (origin/launchpad), and architecture-containers-desktop is the only existing node whose subject (the desktop container as a whole) makes this frontend node's part-of relationship a genuine fit; this was checked by enumerating the full corpus tree, not assumed."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> 94 files (excluding the schema/ subtree, which validate.py excludes from checking) at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3, none under implementation/"
---

# Desktop frontend: implementation reference

This node documents `desktop/src/`, the React 19 + Vite frontend of the Buzz desktop
app, as the concrete realization of the frontend conventions this repository's own
`CLAUDE.md` states in prose under its "Desktop App" section: Tauri 2 + React 19 + Vite
+ Tailwind with Biome lint/format, rem-based text sizing for Cmd +/- zoom with a CI
guard, community switching via React-key remount plus explicit singleton reset, and
React render-performance patterns around `React.memo`, React Query result stability,
and a shared stable-reference hook. It goes one layer deeper than
`architecture-containers-desktop`, which explicitly disclaims the frontend's internal
structure.

## Target

The realization target is `CLAUDE.md`'s "Desktop App" section (repository root,
`/home/serina/Launchpad/buzz/CLAUDE.md`, the "Text sizing & zoom" and "Community
Switching" subsections plus the "React render perf" gotcha in the root "Common
Gotchas" list) — a repository convention document, not a formal spec, ADR, or NIP.
`CLAUDE.md` is not itself a corpus node and carries no corpus `id`, so no `implements`
edge is declared here; per `AGENTS.md`'s explicit rule, an edge to a nonexistent id is
a hard validation error, not a soft placeholder, and this node names the target by its
real path instead.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `desktop/package.json` (`dependencies`/`devDependencies`) | "Tauri 2 + React 19 + Vite + Tailwind CSS. Biome handles linting and formatting." | react/react-dom `^19.1.0`, vite `^8.0.0`, tailwindcss `^4.3.0`, `@tauri-apps/api` `~2.11` |
| `desktop/package.json` `check`/`check:px-text` scripts, `desktop/biome.json` | Biome-driven lint/format plus the px-text CI guard | `check` runs `biome check .` then `check:px-text` then `check:pubkey-truncation` |
| `desktop/scripts/check-px-text.mjs` | "A CI guard (`pnpm check:px-text`...) scans all of `desktop/src` and fails on any new arbitrary text-size literal" | Scans `.ts`/`.tsx`/`.css` under `src`; 4 named literal exceptions, not a blanket allowlist |
| `desktop/src/app/useWebviewZoomShortcuts.ts` | "implements Cmd +/- zoom by scaling the root `<html>` font-size... and pinning the native webview zoom" | Writes `document.documentElement.style.fontSize`; persists to `localStorage['buzz:text-scale']`; pins native webview zoom via `getCurrentWebview().setZoom(1)` |
| `desktop/src/app/App.tsx` (`communityKey`, `CommunityQueryProvider`/`AppReady` `key` props) | "`<AppReady key={communityKey} />`... forces the entire community-scoped subtree to unmount and remount with fresh state" | `communityKey` composes community id, `reinitKey`, current pubkey and `signerEpoch` |
| `desktop/src/features/communities/useCommunityInit.ts` (`resetCommunityState`) | "Every community-scoped singleton needs a reset function wired into `resetCommunityState()`" | 21-call reset inventory at this revision (3 calls conditionally gated); own doc comment cites `AGENTS.md`'s "Community Switching" as the fuller contract |
| `desktop/src/shared/hooks/useStableReference.ts` (`useStableMap`, `useStableArrayShallow`, `useStableSet`) | "wrap in a content-equality ref cache (`shared/hooks/useStableReference.ts`)" | Called from `useUnreadChannels.ts`, `useChannelUnreadState.ts` and 5 other feature files |
| `desktop/src/features/home/useInboxEditMessage.ts` (`mutateRef`) | "depend on the stable method (`mutation.mutateAsync`), not the object" | Wraps `editMessageMutation.mutateAsync` in a `useRef`, read inside a zero-dependency `useCallback` |
| `desktop/src/features/channels/ui/ChannelPane.tsx`, `MessageActionBar.tsx`, `EmojiPicker.tsx` (`React.memo`) | "`React.memo` is all-or-nothing — it only skips a re-render when *every* prop is reference-stable" | Real `React.memo`-wrapped components in the message-timeline render path CLAUDE.md's own gotcha names |
| `desktop/src/main.tsx` (`renderApp`) | Not explicitly named in `CLAUDE.md`'s prose, but is the provider hierarchy `desktop/src/main.tsx` is cited for | `StrictMode` > `RootErrorBoundary` > `CommunitiesProvider` > `CommunityOnboardingProvider` > `ThemeProvider` > `TooltipProvider` > `EmojiBurstProvider` > `PoofBurstProvider` > `UpdaterProvider` (wraps `App`) |
| `desktop/src/app/App.tsx`, `router.tsx`, `routeTree.gen.ts` | Routing layer, not named by `CLAUDE.md` at all | `@tanstack/react-router`'s `RouterProvider`, not React Router |
| `desktop/src/features/*` (29 directories) | "organized under `desktop/src/features/`" | Directory existence confirmed; internal structure of each feature module is out of scope here (see *Scope and omissions*) |

## Divergences

None found for the specific claims checked in *Implementation surface* above — each
row's `CLAUDE.md` prose was verified against the cited file and matched. Two nuances
worth naming as refinements rather than divergences: (1) `CLAUDE.md`'s "Community
Switching" section names `<AppReady key={communityKey} />` in `App.tsx`, but the actual
code applies the same `communityKey` to `CommunityQueryProvider` as well — a broader
remount boundary than the single component `CLAUDE.md`'s prose names, not a
contradiction of it. (2) `CLAUDE.md` does not mention `@tanstack/react-router` or
`main.tsx`'s specific provider order at all; those are documented here as additive
detail, not as something `CLAUDE.md` got wrong. What was **not** checked and is
therefore not claimed clean: the 29 individual feature modules' own internal
conventions, and whether every one of them follows the rem-sizing/render-perf patterns
consistently — the `check:px-text` CI guard is the actual enforcement mechanism for the
former, not this node's own reading of each file.

## Verification

- **Rem-based text sizing**: enforced automatically. `desktop/scripts/check-px-text.mjs`
  runs in `pnpm check` (wired via `desktop/package.json`'s `check` script) and fails the
  build on a new arbitrary px/rem text-size literal outside its four named exceptions.
- **Biome lint/format**: enforced automatically via `desktop/biome.json` and the `check`/
  `lint`/`format` scripts in `desktop/package.json`; not independently re-verified for CI
  wiring beyond the package script definitions themselves in this node.
- **Community-switching singleton reset**: no automated test was found or checked for
  this node; `resetCommunityState`'s own doc comment names `AGENTS.md`'s "Community
  Switching" section as the maintained contract, which is process/convention-level
  verification (a required entry in that function whenever a new singleton is added),
  not an automated one.
- **React render-performance patterns** (`React.memo`, `useStableReference.ts`,
  `mutateAsync` stability): no dedicated automated test was found for these patterns
  specifically; verification is direct code reading of real call sites, done for this
  node, not a CI-enforced invariant the way `check-px-text.mjs` is.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the concrete frontend realization of the specific conventions
`CLAUDE.md`'s "Desktop App" section states in prose: dependency/tooling versions, the
rem-based zoom sizing mechanism and its CI guard, the community-switching React-key
remount pattern and its module-singleton reset inventory, and the React render-
performance patterns (`React.memo` all-or-nothing behavior, React Query result
stability, the `useStableReference.ts` hook family) — plus `main.tsx`'s provider
hierarchy and the routing layer, both read directly since `CLAUDE.md` names the file
without detailing its contents.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The internal structure/conventions of the 29 individual `desktop/src/features/*` modules | A future, narrower implementation node per module or feature area, per the corpus's one-idea-per-node rule |
| The desktop container's architecture-level responsibility, technology boundary, and Rust backend | `architecture-containers-desktop` |
| The E2E screenshot testing workflow and Playwright spec conventions | Not covered here even though `CLAUDE.md` documents them at length; a distinct verification-surface concept from frontend implementation structure |
| Whether every one of the 29 feature modules actually follows the rem-sizing and render-perf conventions consistently, beyond what `check-px-text.mjs` enforces automatically for text sizing | Not verified here; would require a full-tree audit outside this task's scope |
| Mobile (`mobile/`) or web (`web/`) client frontend structure | Their own future implementation nodes, if written |

**Expected but not verified when this node was written:**

- **CI wiring beyond the package.json script definitions.** This node confirms
  `check:px-text` is wired into `desktop/package.json`'s `check` script, but did not
  open the GitHub Actions workflow file(s) that invoke `pnpm check` in CI — that the
  script runs locally is verified; that CI actually calls it was not independently
  re-checked here, though `AGENTS.md`-adjacent repository convention (`just ci`) implies
  it does.
- **Whether `useStableReference.ts`'s three hooks cover every render-perf hotspot
  CLAUDE.md's gotcha describes**, or whether other, undiscovered ad hoc stability
  patterns exist elsewhere in the tree, was not exhaustively searched.
- **The exact CSS mechanism by which `text-2xs`/`text-3xs` Tailwind tokens are defined**
  (`desktop/tailwind.config.js`, per `CLAUDE.md`'s own citation) was not opened directly
  for this node; `CLAUDE.md`'s claim about their values is not independently re-verified
  here.
