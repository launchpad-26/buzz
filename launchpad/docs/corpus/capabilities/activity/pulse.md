---
id: capabilities-activity-pulse
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "preview-features.json describes the `pulse` feature as \"Activity feed with notes, social posts, and agent activity\", scoped to the `desktop` platform, and carries no `defaultEnabled` field."
    entry_class: FACT
    evidence:
      - "preview-features.json:16-21"
  - statement: "`resolveEnabled()` returns the manifest's `defaultEnabled` (defaulting to `false` when the field is omitted) unless an explicit user override is set, so the `pulse` feature is off by default until a user or operator enables it in Settings."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/resolveEnabled.ts"
  - statement: "The desktop `/pulse` route is registered in the router, and its route component calls `usePreviewFeatureWarning(\"pulse\")`, which fires a toast telling the user Pulse is a preview feature to enable in Settings when the flag is off, and is a no-op when the flag is on."
    entry_class: FACT
    evidence:
      - "desktop/src/app/routes.ts:6"
      - "desktop/src/app/routes/pulse.tsx:37-48"
      - "desktop/src/shared/features/useFeatureEnabled.ts:140-159"
  - statement: "Desktop sidebar navigation exposes Pulse as a destination alongside channels, home, projects and agents, via a `goPulse` navigation callback wired into `AppShell.tsx`."
    entry_class: FACT
    evidence:
      - "desktop/src/app/navigation/useAppNavigation.ts:96-111"
      - "desktop/src/app/AppShell.tsx:151"
      - "desktop/src/app/AppShell.tsx:890"
  - statement: "Publishing and reading Pulse notes is built on plain NIP-01 kind:1 text notes, not on the separate Forum feature's kind:45001/45003 range: the Tauri commands `publish_note`, `get_global_notes`, `get_user_notes` and `get_note` are each doc-commented as operating on \"kind:1\" and filter or construct events with `kinds: [1]`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/social.rs:53"
      - "desktop/src-tauri/src/commands/social.rs:123-133"
      - "desktop/src-tauri/src/commands/social.rs:154-164"
      - "crates/buzz-core/src/kind.rs:547-553"
  - statement: "A note may be published as a reply by passing a `reply_to` event id, which `publish_note` resolves to an `EventId` and threads via `events::build_note`, giving the reply an `e` tag (NIP-10) back to its parent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/social.rs:53-69"
  - statement: "The \"Following\" tab (labelled `people` in code) is backed by the standard NIP-02 kind:3 contact list, read and replaced through the `get_contact_list` and `set_contact_list` Tauri commands."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/social.rs:72-81"
      - "desktop/src-tauri/src/commands/social.rs:101"
      - "desktop/src/shared/api/social.ts:127-169"
  - statement: "Note reactions (\"likes\") are NIP-25 kind:7 events: `get_note_reactions` queries `kinds: [7]` for the visible notes and separately queries `kinds: [5]` (NIP-09 deletions) to exclude retracted reactions before folding counts by emoji, defaulting an empty reaction body to \"+\"."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/social.rs:179-215"
      - "desktop/src-tauri/src/commands/social.rs:45-50"
  - statement: "The desktop Pulse feed exposes six tabs in its own view state -- `search`, `everyone`, `people`, `liked`, `agents` and `mine` -- rendered by `PulseTabBar.tsx` as \"Everyone\", \"Following\", \"Liked\", \"Agents\" (with a live relay-agent count badge) and \"Mine\", plus an icon-only search tab."
    entry_class: FACT
    evidence:
      - "desktop/src/features/pulse/ui/PulseView.tsx:35-41"
      - "desktop/src/features/pulse/ui/PulseTabBar.tsx"
  - statement: "The \"Agents\" tab does not read a distinct event kind; it groups the same kind:1 notes by author pubkey using `groupAgentNotes`, collapsing consecutive notes from one pubkey into a single `AgentNoteGroup` as long as consecutive notes are within a 300-second window, and renders each group with `AgentActivityCard`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/pulse/lib/groupAgentNotes.ts:1-40"
      - "desktop/src/features/pulse/ui/AgentActivityCard.tsx:1-45"
  - statement: "A reply's parent event is resolved client-side by `getReplyParent`, which prefers a NIP-10 `reply`-marked `e` tag, falls back to a `root`-marked tag, and otherwise falls back to the last unmarked `e` tag -- behavior directly exercised by `replies.test.mjs`'s six test cases."
    entry_class: FACT
    evidence:
      - "desktop/src/features/pulse/lib/replies.ts"
      - "desktop/src/features/pulse/lib/replies.test.mjs:20-73"
  - statement: "Local reaction-count state transitions (adding/removing a current user's like, never decrementing below zero, detecting a relay's duplicate-reaction error response) are covered by `noteActions.test.mjs`, and the 30-second note / 60-second reaction / 5-minute focus-stale polling cadence is covered by `focusRefetchPolicy.test.mjs`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/pulse/lib/noteActions.test.mjs:8-58"
      - "desktop/src/features/pulse/focusRefetchPolicy.test.mjs:47-57"
      - "desktop/src/features/pulse/hooks.ts:16-27"
  - statement: "A `mobile/lib/features/pulse/` module exists (page, provider, note card, agent-activity card, compose page), but the mobile app's own bottom-navigation destinations, defined in `home_page.dart`, contain zero references to it -- the mobile Pulse code is present in the tree but is not currently reachable through mobile navigation."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pulse/pulse_page.dart"
      - "mobile/lib/features/home/home_page.dart"
  - statement: "Pulse is best characterized as an in-progress / preview capability rather than a shipped or merely designed one: it has a complete desktop UI, a working Tauri backend, and unit test coverage, but ships behind a preview flag defaulting to off, is absent from `VISION_PROJECTS.md`'s own Capability/Status table (which only tracks the git/forge product line), and its mobile counterpart exists in code but is unwired."
    entry_class: INFERENCE
    evidence:
      - "preview-features.json:16-21"
      - "desktop/src/shared/features/resolveEnabled.ts"
      - "desktop/src-tauri/src/commands/social.rs"
      - "mobile/lib/features/pulse/pulse_page.dart"
    confidence: 0.75
relationships:
  - type: references
    target: architecture-containers-desktop
---

# Pulse: capability

Pulse is Buzz's activity feed -- a stream of short, public or followed social
notes, with likes, threaded replies, and a distinct view of AI agent activity,
independent of any single channel. A user (or an agent acting on a user's
behalf) can post a short update, follow other participants to shape their
feed, like and reply to others' notes, and separately watch what the
community's AI agents have been doing, grouped by agent and by time. It is
reachable from the desktop sidebar as its own destination, alongside
channels, home, projects and agents.

## Maturity

**In progress / preview.** The desktop implementation is functionally
complete -- a full tabbed UI (`PulseScreen`/`PulseView`/`PulseTabBar`), a
working Tauri backend (`publish_note`, `get_global_notes`, `get_user_notes`,
`get_note`, `get_contact_list`, `set_contact_list`, `get_note_reactions`), and
unit test coverage over its trickiest logic (reply-parent resolution,
reaction-count transitions, refetch cadence) -- but it ships behind the
`pulse` entry in `preview-features.json`, which carries no `defaultEnabled`
and therefore resolves to off until a user opts in via Settings. It does not
appear in `VISION_PROJECTS.md`'s own "Capability | Status" table, which is
scoped to the git-hosting/forge product line and does not track every
product surface in the repository. A parallel `mobile/lib/features/pulse/`
module exists in the mobile codebase but is not wired into the mobile app's
bottom navigation (`home_page.dart`), so on mobile the capability currently
exists in code only.

## Boundary

This node does not describe:

- **How Pulse is built.** The desktop container that ships it --
  Tauri 2 + React 19 UI over a Rust/`buzz_lib` backend -- is documented by
  `architecture-containers-desktop`; this node references that node rather
  than restating its technology choices.
- **The interface Pulse is exposed through.** The Tauri IPC command surface
  (`publish_note`, `get_global_notes`, `get_contact_list`,
  `get_note_reactions`, etc.) is cited here as evidence the capability
  exists, not documented as an interface contract -- no interface-shaped
  corpus node covering it is merged yet.
- **The step-by-step flow through Pulse.** The exact sequence a note or
  reply takes from compose to relay to feed refresh is a flow-shaped
  concern; no flow-shaped corpus node covering it is merged yet.
- **How Pulse is operated.** Feature-flag rollout, monitoring, or incident
  response for Pulse specifically is not covered here.
- **Whether Pulse and the separate Forum feature (kind:45001/45003, its own
  preview flag) are meant to converge, stay parallel, or be disambiguated
  for users.** No source read while drafting this node settles that
  question; it is left open, not resolved.

## Relationships

- references: `architecture-containers-desktop` -- the container (Tauri
  desktop shell) Pulse currently ships in and is exercised against.

No interface or flow node exists yet on `origin/launchpad` for Pulse's Tauri
command surface or its step-by-step publish/reply/react path, so no
`references` edge is declared toward either. No other capability node is
merged yet, so no `part-of` or sibling `references` edge is declared.

## Scope and omissions

**This node covers** what the Pulse activity-feed capability lets a user or
agent do today (post, follow, like, reply, view agent activity), its current
maturity as a gated desktop preview feature with an unwired mobile
counterpart, and the boundary between this capability description and the
architecture, interface, flow and operations concerns that are each a
different corpus surface.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the desktop container implementing Pulse is built | `architecture-containers-desktop` |
| The Tauri IPC command contract Pulse is exposed through | An interface-shaped node, not yet merged |
| The step-by-step publish/reply/react sequence | A flow-shaped node, not yet merged |
| Feature-flag rollout and operational monitoring of Pulse | The `operations` corpus surface |
| Whether Pulse and Forum (kind:45001/45003) are meant to converge | Unresolved; not settled by any source read here |

**Expected but not verified when this node was written:**

- **Why mobile Pulse is unwired was not investigated.** Its presence in
  `mobile/lib/features/pulse/` without a navigation entry point is reported
  as a code-level fact; no issue or PR search was performed to establish
  whether this is deliberate (feature paused), incidental (navigation not
  yet updated), or something else.
- **Whether the six-tab shape (`search`/`everyone`/`people`/`liked`/`agents`/`mine`)
  is stable product design or still actively changing was not checked**
  against any design document -- it is reported as the shape present in
  code at the recorded revision only.
- **No end-to-end or Playwright coverage of Pulse was found or exercised**
  beyond the unit tests cited above; whether a live-relay integration test
  exists elsewhere in the suite was not confirmed.
