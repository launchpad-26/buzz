---
id: capabilities-onboarding-first-channel
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
  - statement: "node.schema.json's type enum lists capabilities as its own dedicated value, distinct from architecture, interfaces-events and operations -- the corpus surface this node documents."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Once the desktop onboarding gate resolves (identity and, unless skipped, profile settled), completeAndShowWelcome calls requestStarterChannels(true), which calls initializeStarterChannels -- this ensures the community's starter channels exist, ensures a private per-member Welcome channel exists, and then navigates the user to that Welcome channel via a stored pending-channel handoff and a window.location.hash update."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/hooks.ts:74-165"
      - "desktop/src/features/onboarding/hooks.ts:621-641"
  - statement: "The desktop Tauri backend's ensure_starter_channels command seeds exactly two open, public stream channels -- slug/name general (\"General conversation and community updates.\") and slug/name welcome-everyone (\"Say hi, ask a question, or share what brought you here.\") -- and derives each channel's id as a UUIDv5 keyed by the community's relay scope plus the channel's fixed slug, so every member of the same community resolves the same two starter-channel ids rather than each member getting a personal copy."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/channels.rs:23-42"
      - "desktop/src-tauri/src/commands/channels.rs:224-227"
      - "desktop/src-tauri/src/commands/channels.rs:364-405"
  - statement: "Distinct from the two public starter channels, welcome.ts defines a private, per-member \"Welcome\" stream channel (visibility: private, description \"A private channel for getting oriented in this community.\"), and ensureWelcomeChannel idempotently reuses an existing one (updating stale metadata) or creates a fresh one rather than always creating a new channel."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/welcome.ts:8-16"
      - "desktop/src/features/onboarding/welcome.ts:227-258"
  - statement: "After ensureWelcomeChannel resolves, completeAndShowWelcome remembers the private Welcome channel's id (rememberPendingWelcomeChannel, sessionStorage) and sets window.location.hash to that channel's route, so the private Welcome channel -- not either public starter channel -- is the channel a first-run desktop member is actually placed into at the end of onboarding."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/hooks.ts:621-641"
      - "desktop/src/features/onboarding/welcome.ts:383-400"
      - "desktop/src/features/onboarding/welcome.ts:438-442"
  - statement: "A client-only phase machine (useWelcomeKickoffStage) shows a \"the team is being set up\" stage only once the active channel is confirmed to be the Welcome channel and its message timeline has settled with zero messages; the stage transitions to exiting the instant any message (agent- or user-authored) lands, and separately times out after 90 seconds, degrading quietly to an ordinary empty channel rather than claiming setup is still in progress."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/useWelcomeKickoffStage.ts:26-38"
      - "desktop/src/features/onboarding/useWelcomeKickoffStage.ts:59-92"
  - statement: "welcomeKickoff.ts defines the kickoff experience's call-to-action copy -- \"What can we help you build? Bring us something you're working on, or give us a quick challenge to see how we work together.\" -- gated behind a separate message asking the member to connect an AI provider in Settings first when none is configured."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/welcomeKickoff.ts:36-49"
  - statement: "welcome.ts, useWelcomeKickoffStage.ts and welcomeKickoff.ts each have a co-located automated test file exercising their exported behavior, indicating this is implemented, tested desktop behavior rather than a design-only or partially-built path."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/welcome.test.mjs"
      - "desktop/src/features/onboarding/useWelcomeKickoffStage.test.mjs"
      - "desktop/src/features/onboarding/welcomeKickoff.test.mjs"
  - statement: "mobile/lib has no onboarding feature module and no equivalent to desktop's starter-channel or private-Welcome-channel concept: mobile/lib/features/onboarding does not exist, and a case-insensitive search of mobile/lib for welcome/starter-channel terms (elcome, starterChannel, StarterChannel) matches only files under the unrelated pairing and invite-redemption features (pairing_page.dart, pairing_welcome_view.dart, invite_join_provider.dart, invite_join_sheet.dart, app.dart)."
    entry_class: FACT
    evidence:
      - "find(mobile/lib/features/onboarding) -> No such file or directory, run at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
      - "grep_case_insensitive('elcome|starterChannel|StarterChannel', path='mobile/lib') -> mobile/lib/features/pairing/pairing_page.dart, mobile/lib/features/pairing/pairing_page/pairing_welcome_view.dart, mobile/lib/features/invites/invite_join_provider.dart, mobile/lib/features/invites/invite_join_sheet.dart, mobile/lib/app.dart, run at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "welcome.ts's own doc comment describes the starter #welcome-everyone channel and the private Welcome channel together as \"channels that get the welcome experience,\" and separately calls the private channel \"the legacy private Welcome channel\" -- the code does not state whether the private channel is being phased out or is intentionally kept alongside the public starter channel indefinitely."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/welcome.ts:147-156"
  - statement: "Issue #796's own Definition of Done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#796 definition of done"
  - statement: "Feature #613's child issue list includes #797 (first-community), #798 (first-identity) and #799 (onboarding, the overall capability) alongside #796 (first-channel) as four separate, parallel document tasks with no merge ordering between them, so none of the other three's node ids exist on origin/launchpad at this node's recorded revision and none is a valid relationships target yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#613 child issue list (read via gh issue view)"
relationships:
  - type: part-of
    target: capabilities-onboarding-onboarding
  - type: references
    target: architecture-containers-desktop
---

# First channel: capability

A brand-new desktop member, once their identity is established and they have joined or
created a community, is placed into a real, working channel rather than an empty channel
list: the community's public starter channels (`#general`, `#welcome-everyone`) are
guaranteed to exist, a private per-member `Welcome` channel is created or reused for them,
and the member is navigated straight into that private channel with an agent-led kickoff
message inviting them to bring something to work on. This is the on-ramp step between
finishing identity/community setup and being a participating member of the community.

## Maturity

**Shipped**, on the desktop app only. `initializeStarterChannels` (`hooks.ts`) is wired
into the onboarding completion path (`completeAndShowWelcome`), the starter-channel
seeding is implemented server-side in the desktop Tauri backend
(`desktop/src-tauri/src/commands/channels.rs`), the private Welcome channel logic
(`welcome.ts`) and the kickoff stage machine (`useWelcomeKickoffStage.ts`,
`welcomeKickoff.ts`) each carry co-located automated tests, and the mechanism runs
unconditionally for every first-run member (`desktop/src/features/onboarding/hooks.ts`).
No VISION document's own status marker names this capability directly; maturity here
rests on the shipped, tested code path itself.

## Boundary

This node does not describe:
- **How identity (a Nostr keypair) is established.** That is first-identity's territory
  (`#798`, a sibling task in this same batch; no node id exists to reference yet).
- **How a member joins or creates the community itself**, including invite redemption.
  That is first-community's territory (`#797`; no node id exists to reference yet).
- **The onboarding capability as a whole**, of which this is one step. That is
  `#799`'s territory (`onboarding.md`; no node id exists to reference yet).
- **How channels are built** -- the Tauri commands, the relay's NIP-29 channel model, the
  React state layer. That is the architecture family's territory
  (`#1326`/`#1327`/`#1328` templates); this node `references` the desktop container node
  that hosts the implementation cited above, without describing it.
- **The interface/protocol surface** a channel is exposed through (CLI, HTTP, relay
  events). That is the interface template's territory (`#1342`); no channels-specific
  interface node is merged yet.
- **The step-by-step interaction sequence** a user takes through this moment. That is the
  flow template's territory (`#1338`, not yet drafted).
- **The full behavior of the agent-led welcome-kickoff conversation** -- which agents are
  seeded, how they are selected per community, what they say beyond the cited
  call-to-action. Only the trigger and exit conditions of the kickoff *stage* (a UI
  loading state) are cited here; the kickoff conversation's own content is a distinct
  concern this node does not restate.
- **Mobile.** At this revision mobile has no equivalent step at all -- this is a gap in
  the product, not merely an undocumented one (see evidence ledger).

## Relationships

- `references`: `architecture-containers-desktop` -- the platform container that hosts
  this capability's implementation.
- No relationship targets the onboarding-family siblings (`#797`, `#798`, `#799`): all
  four are parallel, unmerged tasks in the same batch at this node's recorded revision,
  so none of their ids exist on `origin/launchpad` yet. The first of those to merge is the
  natural moment to add a `part-of` edge from this node toward the overall onboarding
  capability, once `capabilities-onboarding-onboarding` (or whatever id `#799` assigns)
  exists there.

## Scope and omissions

**This node covers** the moment onboarding hands a new desktop member into a working
channel: the two deterministic, community-shared public starter channels, the private
per-member Welcome channel, the client-side logic that focuses a first-run member on the
private channel, and the existence (not full behavior) of an agent-led kickoff banner
shown only on a confirmed-empty Welcome channel.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Identity/keypair setup | `#798` (first-identity, unmerged) |
| Joining or creating the community | `#797` (first-community, unmerged) |
| The onboarding capability as a whole | `#799` (onboarding, unmerged) |
| How channels are architected/built | architecture family (`#1326`/`#1327`/`#1328` templates); no channels-specific instance node merged yet |
| The interface/protocol surface for channels | interface template (`#1342`); no instance node merged yet |
| The step-by-step interaction flow through this moment | flow template (`#1338`, not yet drafted) |
| Full behavior/content of the agent-led kickoff conversation | not attempted here |
| A mobile equivalent | none exists in the product at this revision |

**Expected but not verified when this node was written:**
- Whether the public `#welcome-everyone` starter channel is intended to eventually
  replace the private per-member `Welcome` channel, or whether both are deliberately kept
  indefinitely -- `welcome.ts`'s own doc comment calls the private channel "legacy" while
  the code still creates/reuses it unconditionally on every first run. No PR or issue
  history was read to resolve this; it is stated here as an open question, not settled.
- Whether any `buzz-workflow` automation participates in first-channel seeding (for
  example, community-side triggers on member join) was not checked; this node's evidence
  is scoped to the desktop client and its own Tauri backend command.
- No corpus verification node exists yet to link for "verification demonstrating the
  capability" (the Definition of Done's own phrase); the automated test files cited above
  are the closest available evidence at this revision.
