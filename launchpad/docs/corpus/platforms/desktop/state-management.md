---
id: platforms-desktop-state-management
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
  - statement: "The desktop app constructs two independent React Query `QueryClient` instances via the same factory, `createBuzzQueryClient()`: one app/machine-scoped instance created once in the top-level `App()` component, and one community-scoped instance created inside `CommunityQueryProvider`, re-created via a `useState` initializer every time that component remounts."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:805"
      - "desktop/src/app/App.tsx:230-241"
      - "desktop/src/shared/api/queryClient.ts:23-38"
  - statement: "`createBuzzQueryClient()` configures identical default options for both instances (retry: 1, refetchOnWindowFocus: false, networkMode: \"always\", gcTime 5 minutes) and lazily wires a shared window-focus manager the first time it is called; it does not itself add any per-community or per-identity scoping."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/queryClient.ts:8-38"
  - statement: "Both `CommunityQueryProvider` and the `AppReady` component it wraps are rendered with an identical `key={communityKey}` prop inside `CommunityApp`, so any change to `communityKey` unmounts the entire community-scoped subtree -- including the community `QueryClient` -- and remounts it from scratch rather than re-rendering it in place."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:629-656"
  - statement: "`communityKey` is a template-string composite of the active community's id, a `reinitKey`, the current signer's pubkey, and a `signerEpoch` counter that is bumped whenever `CommunityIdentityReplacementSentinel` observes the community-scoped identity query's pubkey change after mount (an in-app key import) -- so a community switch, a relay/token config change, a machine-level identity change, and an in-app identity replacement all force the same full remount."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:407"
      - "desktop/src/app/App.tsx:266-299"
  - statement: "Cache isolation between communities and identities is achieved by constructing a fresh `QueryClient` instance per `communityKey` change, not by namespacing individual query keys with a community id or pubkey: `useIdentityQuery`, for example, uses the bare literal key `[\"identity\"]` with no community- or pubkey-specific segment, relying entirely on which `QueryClient` instance the hook is called under."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/hooks.ts:5-11"
  - statement: "The community `QueryClient` is seeded synchronously inside its own `useState` initializer -- calling `seedProjectSnapshot` and `hydrateChannelHeads` before first render -- rather than in a `useEffect`, because React Query invokes a subscribed query's `queryFn` as soon as a component subscribes, before any parent effect has run; the surrounding comment notes this also means React 19 Strict Mode's dev-only double-invoke of the initializer issues one redundant read against a discarded client rather than a duplicate mount effect."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:225-241"
  - statement: "`useCommunityInit.ts` defines a private (non-exported) function, `resetCommunityState()`, that synchronously tears down a fixed list of module-level singleton stores and caches every time the active community changes; its own doc comment states it is the mechanism for tearing down \"all community-scoped module singletons\" and that hook-managed singletons such as `ChannelMuteSyncManager` and `ChannelSectionSyncManager` are deliberately excluded because they are destroyed via React effect cleanup instead."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:45-84"
  - statement: "`ChannelMuteSyncManager` and `ChannelSectionSyncManager` are held in a `useRef` inside their owning hooks (`useChannelMutes`, `useChannelSections`) rather than at module scope, so they are torn down by the owning component's own unmount/effect-cleanup lifecycle rather than needing an entry in `resetCommunityState()`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/sidebar/lib/useChannelMutes.ts:33-58"
      - "desktop/src/features/sidebar/lib/useChannelSections.ts:44-58"
  - statement: "Root `CLAUDE.md`'s \"Community Switching\" section states that `resetCommunityState()` is \"the canonical inventory of community-scoped singletons\" and that any new module-level cache, Map, or class instance holding community-scoped data must add its own reset call there in the same change, or data from the old community can leak into the new one."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:529-556"
  - statement: "`useCommunityInit`'s effect gates its reset call on a `hasInitializedRef` flag: on the very first mount (`hasInitializedRef.current === false`) it skips calling `resetCommunityState()` because there is nothing yet to tear down, and only calls it on a subsequent switch away from an already-initialized community."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:123"
      - "desktop/src/features/communities/useCommunityInit.ts:143-166"
      - "desktop/src/features/communities/useCommunityInit.ts:249-283"
  - statement: "`desktop/src/features/agents/activeAgentTurnsStore.ts` implements a save-then-reset-then-restore sequence instead of a plain reset for one specific module singleton: `saveActiveAgentTurnsForCommunity(communityId)` deep-clones the live per-agent turn/offset/watermark/tombstone maps into a `savedByCommunity` map keyed by the outgoing community id, `resetCommunityState()` then calls the same module's `resetActiveAgentTurnsStore()` to clear the live maps, and `restoreActiveAgentTurnsForCommunity(communityId)` replays the saved snapshot for the new community once `applyCommunity` has succeeded -- so an A to B to A community round trip preserves each agent's elapsed turn timers instead of losing them."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agents/activeAgentTurnsStore.ts:740-774"
      - "desktop/src/features/agents/activeAgentTurnsStore.ts:794-830"
      - "desktop/src/features/communities/useCommunityInit.ts:145"
      - "desktop/src/features/communities/useCommunityInit.ts:253"
      - "desktop/src/features/communities/useCommunityInit.ts:343"
  - statement: "`resetActiveAgentTurnsStore()`'s own doc comment states it intentionally preserves the `savedByCommunity` map, because \"community-switch snapshots must survive the reset that runs between save and restore\" -- naming the ordering dependency explicitly rather than leaving it implicit in call order alone."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agents/activeAgentTurnsStore.ts:702-706"
  - statement: "`restoreActiveAgentTurnsForCommunity` is called from `useCommunityInit.ts` after `applyCommunity` has resolved for the new community and before `setResult` marks the community ready, so restored turn timers are present on the first render that shows the new community's UI rather than arriving in a later re-render."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:315-343"
  - statement: "Two module-level stores under `desktop/src/features/` export a reset-shaped function that is not among the calls inside `resetCommunityState()` and is not invoked anywhere else in the application's production code: `resetCardMintStore` in `cardMintStore.ts`, and `resetTerminalPanelForTests` in `terminalPanelStore.ts` (the latter's name marks it as a test-only helper, not a production reset path)."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/features/agents/cardMintStore.ts:190-196"
      - "desktop/src/features/terminal/terminalPanelStore.ts:47-50"
    confidence: 0.6
  - statement: "Issue #1249's Definition of Done requires this node to state a component's responsibility and well-defined interface/boundary, name its dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire containing platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1249 definition of done"
---

# Desktop: state management

This node documents how the Buzz desktop app (Tauri 2 + React 19, under
`desktop/src/`) scopes and resets application state across two axes that
matter for correctness: **community boundaries** (a user has several
communities, each backed by a different relay) and **identity boundaries**
(the signing key currently active). It answers, for a reader touching this
code: which state lives in a React Query cache versus a module-level
singleton, how each is scoped, and what forces a scope boundary to be
crossed cleanly instead of leaking.

It complements, without restating, `launchpad/docs/corpus/architecture/containers/desktop.md`
(the desktop container's overall responsibility, technology boundary, and
security implications) by going one level deeper into this one cross-cutting
concern.

## Responsibility

Desktop state management exists to answer one question consistently
throughout the app: **when the active community or identity changes, which
in-memory state must be thrown away, and which must survive the switch?**
Two mechanisms divide that responsibility:

- **React Query cache scoping** — server-derived state (queries, mutations)
  is isolated per community/identity boundary by constructing a fresh
  `QueryClient` instance rather than by namespacing individual query keys.
- **Module-level singleton reset** — plain in-memory module state (`Map`s,
  cached values, subscriptions) that lives outside React's tree is torn down
  by an explicit, hand-maintained inventory function, because remounting a
  React subtree does not, by itself, clear a module-scope variable.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `createBuzzQueryClient()` | function | Builds one `QueryClient` with this app's shared default options (retry, focus-refetch, network mode, `gcTime`) and lazily wires the window-focus manager once, process-wide. | `desktop/src/shared/api/queryClient.ts:23-38` |
| `CommunityQueryProvider` | React component | Owns the community-scoped `QueryClient`; created once per `communityKey` via a `useState` initializer, seeded synchronously with `seedProjectSnapshot`/`hydrateChannelHeads` before first render. | `desktop/src/app/App.tsx:218-263` |
| `useCommunityInit(activeCommunity, communityKey, isSharedIdentity, suppressAutoConnect)` | hook | Applies the active community config to the Tauri backend and returns a discriminated-union readiness result; internally calls the module's private `resetCommunityState()` on every switch away from an already-initialized community. | `desktop/src/features/communities/useCommunityInit.ts:109-371` |
| `communityKey` (composite string) | derived value | `${activeCommunity.id}-${reinitKey}-${currentPubkey}-${signerEpoch}`; used as the React `key` on both `CommunityQueryProvider` and `AppReady` to force a full remount of the community-scoped subtree on any component change. | `desktop/src/app/App.tsx:407`, `desktop/src/app/App.tsx:629-656` |
| Per-singleton `reset*`/`save*ForCommunity`/`restore*ForCommunity` functions (e.g. `resetActiveAgentTurnsStore`, `saveActiveAgentTurnsForCommunity`, `restoreActiveAgentTurnsForCommunity`, `resetMediaCaches`, `resetAgentObserverStore`, and the rest called from `resetCommunityState()`) | functions, one per module | Each module owns its own singleton state and exposes the minimal reset (or save/restore) surface `resetCommunityState()` calls; the module itself is the only writer of that state. | `desktop/src/features/communities/useCommunityInit.ts:1-43` (import list), `desktop/src/features/agents/activeAgentTurnsStore.ts:707-830` |

`resetCommunityState()` itself is intentionally **not** part of this
component's public interface — it is a private function local to
`useCommunityInit.ts`, reachable only through calling the `useCommunityInit`
hook. The current, authoritative list of what it calls lives in that one
file; this node describes the *pattern* it implements rather than
reproducing the list, per root `CLAUDE.md`'s own instruction not to
duplicate it (`CLAUDE.md:550-556`).

## Dependencies

**Depends on** (this pattern requires these to function correctly):

| Component | Why | Evidence |
|---|---|---|
| `@tanstack/react-query` | Supplies the `QueryClient`/`QueryClientProvider` primitives both client instances are built from. | `desktop/package.json` (`"@tanstack/react-query": "^5.90.21"`) |
| Tauri backend community/identity commands (`applyCommunity`, `getIdentity`, `isSharedIdentity`) | `useCommunityInit` and `App()` read the active community/identity from the Rust backend before deciding whether to reset or remount. | `desktop/src/features/communities/useCommunityInit.ts:1-16` |
| Every module listed in `resetCommunityState()`'s own import list (drafts, media caches, agent stores, avatar caches, markdown caches, and the rest) | Each is a collaborator this pattern coordinates the teardown of; `resetCommunityState()`'s correctness depends on every one of them being included and kept correct as new singletons are added. | `desktop/src/features/communities/useCommunityInit.ts:1-43` |

**Depended on by** (these require this pattern to behave correctly):

| Component | Why | Evidence |
|---|---|---|
| `CommunityApp` (`desktop/src/app/App.tsx`) | Renders `CommunityQueryProvider`/`AppReady` keyed on `communityKey` and calls `useCommunityInit`; a bug in either the key composition or the reset inventory surfaces here as stale or cross-community data. | `desktop/src/app/App.tsx:379-656` |
| Every feature that reads community- or identity-scoped React Query data (channels, messages, profiles, projects) | Relies on the community `QueryClient` being fully replaced, not merely invalidated, on a community/identity boundary crossing. | `desktop/src/app/App.tsx:218-263` |
| Every feature owning a module-level singleton reset from `resetCommunityState()` (agents, messages, media, profile, sidebar features) | Relies on being included in, and correctly reset by, that inventory on every community switch. | `desktop/src/features/communities/useCommunityInit.ts:54-84` |

## Boundary

This node does not describe:

- **IPC/bridge mechanics between the React frontend and the Tauri Rust
  backend** — the `invoke`/command surface itself is a distinct concern
  owned elsewhere (issue #1241, frontend-backend-bridge).
- **General React patterns used across the desktop codebase** (hooks
  conventions, component composition) beyond the specific remount/reset
  mechanics this node's subject requires — owned elsewhere (issue #1245,
  react).
- **Routing and navigation** — `communityKey`'s effect on which route is
  shown, and how navigation state is preserved or reset across a community
  switch, is a related but distinct concern owned elsewhere (issue #1243,
  navigation). This node covers only the state-container remount itself.
- **The desktop container's overall architecture, security model, or
  deployment lane** — see
  `launchpad/docs/corpus/architecture/containers/desktop.md` for that.
- **The internal design of any single reset target** (e.g. how
  `activeAgentTurnsStore` computes agent turn liveness) beyond what is
  needed to explain the save/reset/restore pattern itself.
- **Whether the two module-level stores noted above with an unwired reset
  function (`resetCardMintStore`, `resetTerminalPanelForTests`) represent a
  real cross-community data leak** — flagged only as an observed gap in
  *Scope and omissions* below, not established as a bug, and not fixed here.

## Relationships

None declared. `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` was checked before writing this node and contains no
existing node this document's subject could `depends-on`, `references`, or
sit `part-of` — the corpus's platform/architecture nodes for desktop are
either not yet merged to `origin/launchpad` or (for
`architecture-containers-desktop`) document the container as a whole rather
than this specific state-management concern at a granularity this node
could cite without risk of the target drifting. Per `AGENTS.md`'s explicit
warning, this justification is checked against the actual merge-target tree
at authoring time, not assumed to remain true.

## Scope and omissions

**This node covers** the desktop app's two state-scoping mechanisms —
per-`communityKey` `QueryClient` construction, and the `resetCommunityState()`
module-singleton-teardown inventory — how `communityKey`'s composition
forces both to be crossed cleanly on a community switch, relay/token
change, or identity replacement, the documented hook-managed-singleton
exception, and the one documented save/reset/restore exception
(`activeAgentTurnsStore`).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Tauri IPC/bridge mechanics | #1241 (frontend-backend-bridge) |
| General React patterns and conventions | #1245 (react) |
| Routing/navigation state and its interaction with community switches | #1243 (navigation) |
| The desktop container's overall architecture and security model | `launchpad/docs/corpus/architecture/containers/desktop.md` |
| Internal design of any individual reset target beyond the pattern it participates in | Each target module's own source |

**Expected but not verified when this node was written:**

- **Whether `resetCardMintStore` and `resetTerminalPanelForTests` being
  absent from `resetCommunityState()` is a deliberate design choice (e.g.
  because their state is not actually community-scoped) or an incomplete
  reset inventory.** Both exports were confirmed to exist and confirmed not
  to be called from `resetCommunityState()` or from any other production
  call site found by a repository-wide search; whether the underlying data
  they guard is genuinely community-scoped was not traced further, so no
  claim beyond the structural fact is made here.
- **Whether every one of `resetCommunityState()`'s current call targets
  still exists with the same name at a later revision.** This node
  deliberately does not reproduce that list verbatim (per `CLAUDE.md`'s own
  instruction), so it will not go stale as singletons are added or renamed,
  but this also means a reader wanting the exact current list must open
  `useCommunityInit.ts` directly rather than trusting a copy here.
- **Whether any other module besides `activeAgentTurnsStore` implements a
  save/restore-across-switch exception rather than a plain reset.** Only
  one such case was found by the searches performed for this node; a
  broader audit of every `resetCommunityState()` call target for the same
  pattern was not performed.
