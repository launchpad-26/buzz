---
id: capabilities-onboarding-onboarding
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
  - statement: "The desktop app's top-level `MachineBootstrap` component (`App()` renders it once `sharedIdentity` resolves) computes a `machine.stage` from `useMachineOnboardingState` and, based on that value, renders one of `ResetFailedScreen`, `KeyringLockedScreen`, `RelaunchRequiredScreen`, a loading gate (`blocking`), `CommunityApp` (`ready`), or `MachineOnboardingFlow` for every other stage -- this is the single router that decides whether a session sees onboarding at all and which slice of it."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:684-798"
  - statement: "`useMachineOnboardingState` (in `machineOnboarding.ts`) types its own return value's `stage` as one of exactly six values: `blocking`, `keyring-locked`, `onboarding`, `ready`, `relaunch-required`, `reset-failed`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/machineOnboarding.ts:10-16"
  - statement: "That stage is resolved by an explicit if/else-if precedence chain: a failed boot-time reset outranks a locked keyring, which outranks a required relaunch, which outranks a lost identity, which outranks an identity-query error, which outranks the not-yet-settled/not-yet-evaluated case (`blocking`), before falling through to `onboarding` (lost, or explicitly continuing, or not yet completed for this pubkey) and finally `ready`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/machineOnboarding.ts:213-246"
  - statement: "Once `machine.stage` is `ready`, `MachineBootstrap` renders `CommunityApp`, which reads `useCommunityOnboarding().transaction` and, whenever a transaction exists, renders `CommunityOnboardingFlow` (optionally as a full-screen curtain over the mounting app when the transaction's stage is `entering`) alongside the community's main content; the component further gates that content through `AppReady`, whose own `useAppOnboardingState` stage can still show `OnboardingFlow` (a relay-scoped profile/avatar step), `ResetFailedScreen`, `KeyringLockedScreen`, `RelaunchRequiredScreen`, or a loading gate before the router mounts."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:353-373"
      - "desktop/src/app/App.tsx:620-682"
      - "desktop/src/app/App.tsx:301-351"
  - statement: "`CommunityOnboardingStage` (in `communityOnboarding.tsx`) is typed as one of six values -- `claiming`, `connecting`, `profile`, `team-intro`, `finalizing`, `entering` -- and `CommunityOnboardingSource` distinguishes why the transaction started: `first-community`, `add-community`, `membership-recovery`, `deep-link-connect`, `deep-link-join`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/communityOnboarding.tsx:10-28"
  - statement: "`CommunityOnboardingFlow`'s `finalize` handler calls `initializeStarterChannels` (exported from `hooks.ts`) while the transaction is in the `finalizing` stage; a successful result carrying a `focusChannelId` routes the window hash directly to that channel and holds the flow mounted as a curtain (`entering` stage) until a `WELCOME_SURFACE_READY_EVENT` fires or a safety timeout elapses, rather than landing the user on a generic Home view first."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/CommunityOnboardingFlow.tsx:259-298"
      - "desktop/src/features/onboarding/hooks.ts:74"
  - statement: "`MachineOnboardingFlow` (the per-device flow rendered while `machine.stage` is not `ready`) is typed over exactly five pages -- `identity`, `key-import`, `backup`, `setup`, `config` -- covering identity creation/import, encrypted backup, and agent-runtime setup before any community exists."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/MachineOnboardingFlow.tsx:48-53"
  - statement: "`OnboardingFlow.tsx`'s own comment states that by the time it renders, \"Machine-level identity, backup, and provider setup have already completed\" and that \"this relay-scoped flow now owns only the community profile\" -- i.e. it is the narrower, already-a-relay-member case, distinct from the `CommunityOnboardingFlow` transaction that runs before relay membership is established."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/OnboardingFlow.tsx:382-384"
  - statement: "Playwright specs under `desktop/tests/e2e/` exercise onboarding end to end under the mock Tauri bridge, including `onboarding-agent-defaults.spec.ts` and `onboarding-avatar-skip.spec.ts`, and unit suites `machineOnboarding.test.mjs` and `communityOnboarding.test.mjs` cover the stage-resolution and transaction logic directly -- this capability is exercised by both levels of test, not merely present in source."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/onboarding-agent-defaults.spec.ts"
      - "desktop/tests/e2e/onboarding-avatar-skip.spec.ts"
      - "desktop/src/features/onboarding/machineOnboarding.test.mjs"
      - "desktop/src/features/onboarding/communityOnboarding.test.mjs"
  - statement: "All of the onboarding router logic cited above (`MachineBootstrap`, `AppReady`, `CommunityApp`) is unconditional code reached from `App()`'s own render path, not code behind a feature flag or dev-only branch, so the capability is shipped rather than in-progress or designed-only."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/app/App.tsx:800-820"
    confidence: 0.9
  - statement: "Sibling tasks #796 (first-channel), #797 (first-community) and #798 (first-identity) are each their own capability-node task under the same parent PRD #613, and as of this node's authoring none of the three had a merged corpus document -- so this node declares no relationship toward any of them and does not restate their per-step behavioral rules."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#796, #797, #798 issue bodies (read directly via gh issue view); batch-run dispatch instructions for #799"
---

# Onboarding: capability

Onboarding is what lets a person with no Buzz identity yet become an active
member of a community, seeing and sending their first message, without
needing an existing account or invite beyond a relay URL or invite link. It
is the product-level capability that decides, at every app launch, whether a
session needs setup at all and, if so, which of several distinct setup
moments to show next.

## Maturity

**Shipped.** The router logic that implements this capability --
`MachineBootstrap`'s stage switch, `CommunityApp`'s transaction-driven
rendering of `CommunityOnboardingFlow`, and `AppReady`'s further profile gate
-- is unconditional code on the desktop app's main render path, not behind a
feature flag, and is covered by unit tests (`machineOnboarding.test.mjs`,
`communityOnboarding.test.mjs`) and Playwright E2E specs
(`onboarding-agent-defaults.spec.ts`, `onboarding-avatar-skip.spec.ts`, and
others under `desktop/tests/e2e/`). No VISION document's own status table
lists "Onboarding" as a named row; this maturity claim rests on the code and
tests cited above, not on a VISION status marker.

## Boundary

This node does not describe:
- **How each constituent moment behaves internally.** The specific rules,
  constraints and variants of creating or importing an identity (first
  identity), joining or founding a community (first community), and landing
  in a starter channel (first channel) are each their own capability-node
  task -- #798, #797 and #796 respectively -- under this same parent PRD
  (#613). This node covers the router that sequences and gates those three
  moments, not the internal behavior of any one of them.
- **How the onboarding UI is built.** No architecture node for the
  desktop onboarding container/component currently exists in the merged
  corpus; when one does, it owns the component tree, state management and
  technology choices under `desktop/src/features/onboarding/`.
- **The boundary contract onboarding is exposed through.** Onboarding today
  is a desktop-app-only surface (`desktop/src/features/onboarding/`); no CLI
  or HTTP interface node for it exists to reference.
- **The step-by-step path through onboarding.** A flow node narrating the
  exact sequence of screens a user sees is a distinct node type from this
  capability statement.
- **How the running system is operated.** Deployment, monitoring and
  incident response for the relay or desktop build are outside this node.

## Relationships

None. #796, #797 and #798 -- the natural `part-of`/`references` targets for
this node -- had no merged corpus document as of this node's authoring
revision, and a `relationships[].target` naming an id no node carries is a
hard validation error. The first of those three siblings to merge is the
right moment to add the corresponding edge back to this node.

## Scope and omissions

**This node covers** the onboarding capability as a whole: what it lets a
new user accomplish, that it is shipped and exercised by tests, and the
router logic (`MachineBootstrap` / `AppReady` / `CommunityApp`) that
sequences and gates its constituent moments -- machine-level identity setup,
community-level joining/founding, and the community-profile/starter-channel
finish -- described here only at the level of *which stage is shown when*,
not the internal rules of any one stage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| First-identity behavioral rules and variants | `#798` (unmerged at authoring time) |
| First-community behavioral rules and variants | `#797` (unmerged at authoring time) |
| First-channel behavioral rules and variants | `#796` (unmerged at authoring time) |
| How the onboarding UI is built (components, state, technology) | a future architecture node for `desktop/src/features/onboarding/` |
| The step-by-step path through onboarding | a future flow node |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **No relay-side (server) onboarding equivalent was checked.** This node
  describes the desktop app's onboarding router only; whether `buzz-cli` or
  the mobile app expose an analogous sequence was not investigated.
- **Whether `useAppOnboardingState`'s relay-scoped profile step
  (`OnboardingFlow.tsx`) is itself part of "first community" or a fourth,
  undocumented moment was not resolved.** Its own comment
  (`OnboardingFlow.tsx:382-384`) states it runs after machine-level setup and
  owns only the community profile, which overlaps in subject with #797's
  scope; that overlap is left for #797's own drafting to resolve, not decided
  here.
