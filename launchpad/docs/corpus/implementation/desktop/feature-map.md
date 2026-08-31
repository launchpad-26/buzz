---
id: implementation-desktop-feature-map
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
  - statement: "The repository's own contributor guide states, in its 'Desktop App' section, that the desktop app is Tauri 2 + React 19 + Vite + Tailwind CSS and that 'Features are organized under `desktop/src/features/`.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md:480-481"
  - statement: "The merged architecture container node for the desktop app (id architecture-containers-desktop) explicitly names 'the React frontend's internal feature/component architecture' as a gap it does not cover, stating only that its existence and IPC-only relationship to the backend is claimed there -- so this node is the frontend feature-breadth counterpart to that stated omission, not a duplicate of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "Listing desktop/src/features/ (`ls desktop/src/features/`) returns exactly 30 top-level directories: agent-memory, agents, channel-templates, channels, chat, communities, community-members, custom-emoji, forum, gifs, home, huddle, identity-archive, local-archive, mesh-compute, messages, moderation, notifications, onboarding, presence, profile, projects, pulse, reminders, search, settings, sidebar, terminal, user-status, workflows."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agent-memory/hooks.ts"
      - "desktop/src/features/workflows/hooks.ts"
  - statement: "desktop/src/ also contains app/ (shell, routing, cross-cutting hooks), shared/ (cross-feature code) and testing/ alongside features/, so the feature-module convention is one of four top-level organizing directories, not the whole of desktop/src/."
    entry_class: FACT
    evidence:
      - "desktop/src/main.tsx"
  - statement: "desktop/src/app/routes.ts defines the TanStack Router virtual route tree with exactly twelve routes: the index route, /agents, /pulse, /reminders, /settings, /workflows, /workflows/$workflowId, /projects, /projects/$projectId, /messages/new, /channels/$channelId, and /channels/$channelId/posts/$postId, each mapped to a named file under desktop/src/app/routes/."
    entry_class: FACT
    evidence:
      - "desktop/src/app/routes.ts"
  - statement: "Eight feature directories are wired to a dedicated top-level route in routes.ts: agents (agents.tsx), pulse (pulse.tsx), reminders (reminders.tsx), settings (settings.tsx), workflows (workflows.tsx, workflows.$workflowId.tsx), projects (projects.tsx, projects.$projectId.tsx), messages (messages.new.tsx), and channels (channels.$channelId.tsx, channels.$channelId.posts.$postId.tsx) -- confirmed by grepping each route file for a features/<name> import."
    entry_class: FACT
    evidence:
      - "desktop/src/app/routes/agents.tsx"
      - "desktop/src/app/routes/channels.$channelId.tsx"
  - statement: "desktop/src/app/routes/index.tsx (the root index route, matched at '/') imports from features/home and features/onboarding, so the home feed and onboarding flow are wired at the app's root path even though neither owns a named path segment of its own in routes.ts."
    entry_class: FACT
    evidence:
      - "desktop/src/app/routes/index.tsx"
  - statement: "Fourteen further feature directories are imported directly by a named file under desktop/src/app/ (shell chrome, not a route file) with no dedicated entry in routes.ts: channel-templates (AppShell.tsx), communities (App.tsx, AppShell.tsx, useCommunityNavigationTransitions.ts), community-members (useAppShellDesktopNotifications.ts), custom-emoji (AppShell.tsx), huddle (App.tsx, AppHuddleBar.tsx, AppHuddleShell.tsx), local-archive (AppShell.tsx), notifications (AppShell.helpers.ts, AppShell.tsx, useAppShellDesktopNotifications.ts), presence (AppShell.tsx), profile (App.tsx, AppShell.tsx, routes/ChannelRouteScreen.tsx), sidebar (AppShell.tsx, AppShellOverlays.tsx, RelayConnectionOverlay.tsx), terminal (AppShellOverlays.tsx), and user-status (AppShell.tsx) -- confirmed by grepping desktop/src/app/**/*.{ts,tsx} for each feature's import path."
    entry_class: FACT
    evidence:
      - "desktop/src/app/AppShell.tsx"
      - "desktop/src/app/useAppShellDesktopNotifications.ts"
  - statement: "Eight feature directories have no import from any file under desktop/src/app/ at all, and are reached only by being imported from inside a sibling feature's own UI: chat (imported by features/channels/ui/ChannelScreenHeader.tsx), forum (imported by features/channels/ui/ChannelScreenLazyViews.ts, features/projects/ui/*, features/pulse/ui/PulseView.tsx), gifs (imported by features/messages/ui/ComposerEmojiPicker.tsx), search (imported by features/messages/ui/*, features/projects/ui/DiscussionChannels.tsx, features/sidebar/ui/AppSidebarPinnedHeader.tsx, features/workflows/ui/WorkflowMessagePicker.tsx), moderation (imported by features/agents/ui/*, features/channels/ui/*, features/forum/hooks.ts, features/home/ui/HomeView.tsx, features/huddle/hooks/*, features/messages/hooks.ts), agent-memory (imported by features/profile/ui/*, features/projects/ui/*), identity-archive (imported by features/agents/ui/*, features/channels/*, features/messages/lib/useMentions.ts, features/community-members/ui/AddMemberDialog.tsx), and mesh-compute (imported by features/settings/ui/SettingsPanels.tsx)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/ui/ChannelScreenHeader.tsx"
      - "desktop/src/features/settings/ui/SettingsPanels.tsx"
  - statement: "desktop/src/shared/features/ is a directory of the same basename as the top-level desktop/src/features/ directory, but holds feature-flagging infrastructure (FeatureGate.tsx, manifest.ts, resolveEnabled.ts, useFeatureEnabled.ts, store.ts) rather than a feature module -- a genuine naming collision between 'feature' as in 'feature module' (desktop/src/features/*) and 'feature' as in 'feature flag' (desktop/src/shared/features/)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/manifest.ts"
  - statement: "Unlike the mobile app's CLAUDE.md-stated rule that 'Feature modules must not import from other feature modules -- only from shared/', no equivalent isolation rule is stated for the desktop app in CLAUDE.md's own 'Desktop App' section, and the cross-feature import evidence recorded above (moderation, search, identity-archive, agent-memory, forum, gifs, mesh-compute all imported directly by sibling feature directories, not only by shared/ or app/) shows desktop features are not siloed the way the mobile rule requires -- this is a factual difference in current structure, not a violation of any stated desktop rule, since no such rule exists to violate."
    entry_class: INFERENCE
    evidence:
      - "CLAUDE.md:599"
      - "desktop/src/features/channels/ui/ChannelPane.tsx"
    confidence: 0.85
  - statement: "No automated test or lint check in this repository asserts that a feature directory is reachable only through routes.ts, an app/ import, or a sibling feature's import, nor does anything check that desktop/src/shared/features/ and desktop/src/features/ stay distinct in naming; the corpus's own validate.py checks this document's front matter and citation shapes structurally and never the accuracy of the feature-to-directory mapping it asserts."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

# Desktop feature map: implementation reference

This node documents the desktop app's (`desktop/src/`) top-level feature-module
directory structure and how each feature is wired into the running app --
whether it owns a dedicated top-level route, is imported directly by the app
shell with no dedicated route, or is reached only by composition from inside a
sibling feature. It claims to realize this repository's own stated convention,
`CLAUDE.md`'s "Features are organized under `desktop/src/features/`," and to
fill the frontend-feature-breadth gap the merged `architecture-containers-desktop`
node explicitly leaves open.

## Target

The target is `CLAUDE.md`'s "Desktop App" section, which states plainly:
"Features are organized under `desktop/src/features/`." (`CLAUDE.md:480-481`).
That statement is not itself a corpus node at the time this node was written, so
no `implements` edge is declared toward it -- per `launchpad/docs/corpus/AGENTS.md`,
an edge to a nonexistent id is a hard validation error, not a soft placeholder. A
reader can open the convention directly at `CLAUDE.md:478-481`.

Secondarily, this node is the frontend-feature-breadth half of a gap the merged
`architecture-containers-desktop` node's own *Scope and omissions* names outright:
"The React frontend's internal feature/component architecture -- only its
existence and IPC-only relationship to the backend is claimed here." This node
declares `part-of` toward that node (see *Relationships*).

## Implementation surface

All directory paths below are relative to `desktop/src/features/` unless noted.
"Wiring" classifies how each feature is reached from the running app, not what
the feature does internally -- see *Scope and omissions* for what is
deliberately not attempted here.

| Feature directory | Wiring | Note |
|---|---|---|
| `agents/` | Dedicated route: `/agents` (`app/routes/agents.tsx`) | Managed-agent creation, snapshot import/export, ACP runtime status; largest feature by file count observed. |
| `pulse/` | Dedicated route: `/pulse` (`app/routes/pulse.tsx`) | Activity feed view (`ui/PulseView.tsx`, `ui/NoteCard.tsx`); composes `forum/`. |
| `reminders/` | Dedicated route: `/reminders` (`app/routes/reminders.tsx`) | Reminder notifications and hooks. |
| `settings/` | Dedicated route: `/settings` (`app/routes/settings.tsx`) | App settings panels; composes `mesh-compute/` and `community-members/`. |
| `workflows/` | Dedicated route: `/workflows`, `/workflows/$workflowId` | Workflow editor/list screens; composes `search/`. |
| `projects/` | Dedicated route: `/projects`, `/projects/$projectId` | Largest directory by file count (repo/PR/issue integration); composes `forum/`, `search/`, `agent-memory/`. |
| `messages/` | Dedicated route: `/messages/new` (also used throughout `channels/`) | Message composition, threading; composes `gifs/`, `search/`. |
| `channels/` | Dedicated route: `/channels/$channelId`, `.../posts/$postId` | Channel pane, unread/roster state; composes `chat/`, `forum/`, `moderation/`, `identity-archive/`. |
| `home/` | App-root wiring: index route (`app/routes/index.tsx`) and `app/AppShell.tsx`, `app/AppShellContext.tsx` | Personal inbox / home feed view. |
| `onboarding/` | App-root wiring: index route (`app/routes/index.tsx`), `app/App.tsx` | First-run and community-join onboarding flows. |
| `channel-templates/` | App-shell import, no route (`app/AppShell.tsx`) | Applies channel templates. |
| `communities/` | App-shell import, no route (`app/App.tsx`, `app/AppShell.tsx`, `app/useCommunityNavigationTransitions.ts`) | Multi-community state, storage, icon cache. |
| `community-members/` | App-shell import (`app/useAppShellDesktopNotifications.ts`), also composed from `channels/`, `moderation/`, `settings/` | Member roster, invite/join alerts. |
| `custom-emoji/` | App-shell import, no route (`app/AppShell.tsx`) | Custom emoji picker category data. |
| `huddle/` | App-shell import, no route (`app/App.tsx`, `app/AppHuddleBar.tsx`, `app/AppHuddleShell.tsx`) | Voice-channel ("huddle") audio UI and context; composes `moderation/`. |
| `local-archive/` | App-shell import, no route (`app/AppShell.tsx`) | Local sync of archived agent-metric/observer data. |
| `notifications/` | App-shell import, no route (`app/AppShell.helpers.ts`, `app/AppShell.tsx`, `app/useAppShellDesktopNotifications.ts`) | Desktop notification dispatch. |
| `presence/` | App-shell import, no route (`app/AppShell.tsx`) | Online/presence indicator state. |
| `profile/` | App-shell import, no route (`app/App.tsx`, `app/AppShell.tsx`, `app/routes/ChannelRouteScreen.tsx`) | User profile panels/popovers; composes `agent-memory/`, `identity-archive/`. |
| `sidebar/` | App-shell import, no route (`app/AppShell.tsx`, `app/AppShellOverlays.tsx`, `app/RelayConnectionOverlay.tsx`) | Community/channel sidebar; composes `search/`. |
| `terminal/` | App-shell import, no route (`app/AppShellOverlays.tsx`) | Embedded PTY terminal bootstrap/rendering (frontend half of the container node's `terminal_runtime.rs`). |
| `user-status/` | App-shell import, no route (`app/AppShell.tsx`) | User status indicator. |
| `chat/` | Composed-only; imported by `channels/ui/ChannelScreenHeader.tsx` | Small: one header component. |
| `forum/` | Composed-only; imported by `channels/`, `projects/`, `pulse/` | Forum-style channel view logic. |
| `gifs/` | Composed-only; imported by `messages/ui/ComposerEmojiPicker.tsx` | GIF search/attach API. |
| `search/` | Composed-only; imported by `messages/`, `projects/`, `sidebar/`, `workflows/`, `shared/lib/rehypeSearchHighlight.ts` | Search results hook, widely reused. |
| `moderation/` | Composed-only; imported by `agents/`, `channels/`, `forum/`, `home/`, `huddle/`, `messages/` | Moderation actions/menu items, widely reused. |
| `agent-memory/` | Composed-only; imported by `profile/`, `projects/` | Agent memory display in profile/project panels. |
| `identity-archive/` | Composed-only; imported by `agents/`, `channels/`, `messages/`, `community-members/` | Archived-identity lookups for mentions/member lists. |
| `mesh-compute/` | Composed-only; imported by `settings/ui/SettingsPanels.tsx` | Mesh-LLM share/model-classification UI (frontend half of the container node's optional `mesh-llm` Cargo feature). |

## Divergences

- **The stated convention is a simplification of the actual top-level layout.**
  `CLAUDE.md:480-481` says only "Features are organized under
  `desktop/src/features/`," but `desktop/src/` also holds `app/` (routing and
  substantial shell-level logic -- notifications, tray menu, keyboard shortcuts,
  huddle bar chrome -- that is not itself a feature module) and `shared/`
  (cross-feature code). Feature-shaped logic is not confined to `features/`
  alone; the convention names where features live, not the whole of
  `desktop/src/`'s organization.
- **A naming collision exists between `features/` and `shared/features/`.**
  `desktop/src/shared/features/` holds feature-flagging infrastructure
  (`FeatureGate.tsx`, `manifest.ts`, `resolveEnabled.ts`), an unrelated sense of
  "feature" from the feature-module convention this node maps. A reader or
  agent grepping for "features" without qualifying the path can land on the
  wrong directory. This is reported as a real, checked divergence between the
  convention's plain-language name and the code's own two distinct uses of the
  word "feature" -- not a defect to fix here.
- **No desktop-specific feature-isolation rule exists, unlike mobile's.** The
  mobile app's `CLAUDE.md` section states "Feature modules must not import
  from other feature modules -- only from `shared/`." No equivalent sentence
  appears in the desktop section, and the import evidence above shows desktop
  features routinely import each other directly (`moderation`, `search`,
  `identity-archive`, `agent-memory`, `forum`, `gifs`, `mesh-compute` are all
  imported by sibling feature directories, not only by `app/` or `shared/`).
  This is a factual observation about current structure, not a violation --
  there is no rule for desktop to violate -- but it means the two platforms'
  "features are organized under X" statements do not carry the same
  guarantees.

## Verification

No automated test or lint check verifies this node's central claim (which
feature lives where, and how it is wired). Individual features carry their own unit tests (numerous `*.test.mjs`
files observed per directory, e.g. `agents/agentManagement.test.mjs`,
`channels/hooks.test.mjs`), but those verify feature *behavior*, not the
organizational map this node asserts. The only automated check that touches
this document at all is the corpus's own
`launchpad/project-intelligence/corpus/validate.py`, which validates front
matter and citation shapes structurally and never checks that a table row's
claim is still true. Verification here is manual: the directory listings,
`routes.ts` read, and import greps recorded in this node's evidence ledger,
re-run against `HEAD` at read time.

## Relationships

- part-of: architecture-containers-desktop

No `implements` edge is declared: the target this node claims to realize
(`CLAUDE.md`'s feature-organization statement) is not itself a corpus node at
this task's merge base, and inventing an id for it would be a hard validation
error per `launchpad/docs/corpus/AGENTS.md`. No `references` edge is declared:
no verification/test-strategy corpus node exists yet for this node to point at
(`launchpad/docs/corpus/templates/test-strategy.md` is a template, not an
instance node).

## Scope and omissions

**This node covers** a feature-to-directory index of the desktop app's 30
top-level `desktop/src/features/` directories, one level of each directory's
own structure, and how each is wired into the running app (dedicated route,
app-shell import, or composed-only from a sibling feature) -- breadth, not
depth.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any single feature's internal design -- state management, hooks, component composition | launchpad-26/buzz#947 (frontend internals) |
| The Tauri/Rust backend's own command surface realizing these frontend features | launchpad-26/buzz#948 (Tauri backend internals) |
| `mobile/` or `web/`'s own feature organization | Not this node -- desktop-scoped only |
| The huddle audio pipeline's internal protocol/codec | `architecture-containers-desktop`'s own stated gap; not resolved here either |
| Whether the `shared/features/` naming collision has caused a real defect | Not investigated; flagged in *Divergences* as a documentation/discoverability risk only |
| A convention corpus node for `CLAUDE.md`'s feature-organization statement, and the `implements` edge this node would then declare toward it | Unfiled; the next author who needs that node should check for an existing task before filing a new one, per `AGENTS.md`'s own guidance |

**Expected but not verified when this node was written:**

- **Reachability was checked by import graph, not by running the app.** A
  composed-only feature (e.g. `mesh-compute/`) is confirmed reachable via a
  static import chain from a route-wired feature, not by navigating the actual
  UI to a screen that renders it.
- **File counts and "largest by file count" notes in the Implementation
  surface table are directory-listing impressions, not exhaustive counts** --
  they were not computed with `find | wc -l` and could be off by a few files
  each without changing the wiring classification, which is this node's actual
  claim.
- **Whether any feature directory is dead code (imported nowhere, or imported
  only by its own tests) was not checked.** Every directory in the table above
  was confirmed to have at least one non-test importer or a routes.ts entry;
  none were found with zero importers, but the search was not exhaustive
  across generated/dynamic import forms (e.g. lazy `import()` calls), only
  static `from` imports.
