---
id: capabilities-onboarding-first-community
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
  - statement: "At the recorded revision, origin/launchpad's corpus tree contains no capabilities/, architecture-component, or interface node for this capability to reference, and none of this task's siblings (#796, #798, #799) are merged, so this node declares no relationships."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, standards/**, schema/**, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844 -- no capabilities/ subtree present"
  - statement: "On the desktop app, a first-run user with no configured communities is shown WelcomeSetup's 'welcome' page, headed 'Join or create a community', offering exactly three choices: 'Join a community', 'Create a community', and 'I already have a community'."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:129-186"
  - statement: "App.tsx renders WelcomeSetup only when there is no in-flight community-onboarding transaction and the community-init hook reports needsSetup: true, i.e. only for a user who has not yet applied any community configuration to the backend."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:586-597"
  - statement: "useCommunityInit's CommunityInitResult is a discriminated union whose needsSetup: true variant is the only one carrying a defaultRelayUrl for the caller to seed a first-run welcome screen with, and every other variant (ready, error, not-yet-applied) carries needsSetup: false."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:86-99"
  - statement: "Some desktop builds bypass the WelcomeSetup choice screen entirely: when suppressAutoConnect is false and either isSharedIdentity is true, or autoConnectDefaultRelay is enabled and shouldAutoConnectDefaultRelay(defaultRelayUrl) holds, useCommunityInit calls initFirstCommunity with the configured default relay and reloads, silently treating that relay as the user's first community."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:168-207"
  - statement: "Choosing 'Join a community', 'I already have a community' -> 'I'm a member or admin', or entering an invite/relay URL on WelcomeSetup's join/member page renders InviteRedeemForm, which accepts either a bare relay URL (via onConnect, calling startConnection) or a full invite link with a code (via onRedeem, calling redeemInvite)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:68-90"
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:239-268"
      - "desktop/src/features/onboarding/ui/InviteRedeemForm.tsx:45-61"
  - statement: "Choosing 'Create a community' or 'I own the community' opens HostedCommunityOnboarding, a Builderlab-account-backed flow that signs the user in, lists any hosted communities already tied to that account, and offers creating a new one, before calling back onReady to reveal the 'owned' page."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:92-95"
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:231-238"
      - "desktop/src/features/communities/ui/WelcomeSetup.tsx:318-327"
      - "desktop/src/features/communities/ui/HostedCommunityOnboarding.tsx:59-120"
  - statement: "A relay with a configured join policy can require age and agreement consent before an invite is accepted; JoinPolicyNotice renders that consent block (with Terms/Privacy links opened in the system browser, not in-app) on every join surface, including WelcomeSetup's join page."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/JoinPolicyNotice.tsx:1-40"
  - statement: "If the relay reports the chosen identity is not a member (a relay-membership-denied error), the community-onboarding flow renders MembershipDenied, which offers retrying, changing the target community, or importing a different Nostr key, rather than stranding the user."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/CommunityOnboardingFlow.tsx:381-418"
      - "desktop/src/features/onboarding/ui/MembershipDenied.tsx:1-49"
  - statement: "CommunityOnboardingSource has a dedicated 'first-community' value, distinguishing the first-run join/create entry point from adding a second community, membership recovery, or a deep link, and CommunityOnboardingTransaction persists a firstCommunityPage ('join' | 'member' | 'owned') so a cancelled transaction restores the same first-run page instead of dropping the user into a blank state."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/communityOnboarding.tsx:10-30"
      - "desktop/src/app/App.tsx:493-510"
  - statement: "Once a relay is chosen (by either the join or the create path), the same CommunityOnboardingTransaction advances through 'claiming' or 'connecting' stages -- rendered as 'Joining {communityName}' / 'Accepting your invite...' / 'Connecting securely...' -- before moving on to profile setup; selecting a community and finishing the connection to it are one continuous transaction, not two separate mechanisms."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/communityOnboarding.tsx:17-28"
      - "desktop/src/features/onboarding/ui/CommunityOnboardingFlow.tsx:525-552"
  - statement: "communityOnboarding.test.mjs unit-tests the underlying transaction primitives this capability depends on (startCommunityOnboarding's relay-canonicalization and dedup behavior, shouldSkipCommunityOnboarding, resolveProfileCheckAction's timeout/skip logic), but no test file targets WelcomeSetup.tsx's own choice screen directly."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/communityOnboarding.test.mjs:1-127"
  - statement: "The mobile app has no WelcomeSetup-equivalent join/create choice screen; its onboarding entry point (_PairingWelcomeView) is a QR-scan or manually-entered pairing-code flow that pairs the phone with an already-onboarded desktop identity rather than independently choosing or creating a community."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_page/pairing_welcome_view.dart:1-20"
      - "mobile/lib/features/pairing/pairing_page.dart"
  - statement: "VISION.md states identity is portable across every community a keypair joins, while profile, DMs, and channel-less content are per-community -- i.e. choosing which community to join or create is conceptually distinct from creating the underlying identity keypair, which this capability's evidence above treats as already resolved before WelcomeSetup is shown."
    entry_class: FACT
    evidence:
      - "VISION.md:56"
  - statement: "VISION_SOVEREIGN.md describes a no-separate-onboarding 'Connect on Buzz' web-embedded join path ('no separate onboarding flow') as part of the sovereign-community vision, distinct from the desktop WelcomeSetup screen documented above; no desktop or web source implementing that specific embedded flow was found while drafting this node."
    entry_class: INFERENCE
    evidence:
      - "VISION_SOVEREIGN.md:53"
      - "VISION_SOVEREIGN.md:158"
    confidence: 0.6
  - statement: "Issue #797's task description frames this node as 'the desktop/mobile onboarding step for joining or creating the first community/relay connection,' scoped separately from sibling tasks #796 (first-channel), #798 (first-identity), and #799 (the overall onboarding capability)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#797 task description"
relationships:
  - type: part-of
    target: capabilities-onboarding-onboarding
---

# First community: capability

Buzz lets a first-run user, once their identity exists, choose to **join an
existing community** (by invite link, code, or relay URL), **create a new
hosted community**, or **reconnect to a community they already belong to** --
before anything else in the app becomes available. This is the single gate
between "Buzz is installed and has an identity" and "Buzz is connected to a
relay and ready to show channels."

## Maturity

**Shipped**, on desktop. `WelcomeSetup` presents the three-way choice
("Join a community" / "Create a community" / "I already have a community")
whenever `useCommunityInit` reports `needsSetup: true` and no
community-onboarding transaction is already in flight, and `App.tsx` wires
that gate in directly ahead of the rest of the app shell. The join path
(`InviteRedeemForm`, `JoinPolicyNotice`, `MembershipDenied`) and the create
path (`HostedCommunityOnboarding`, Builderlab-backed) are both live code,
not placeholders. The underlying transaction state machine
(`CommunityOnboardingTransaction` and its stage sequence) has direct unit
coverage; the `WelcomeSetup` choice screen itself does not have a dedicated
test file, which is recorded below as a verification gap rather than a
maturity gap -- the code path is exercised by the manual/E2E onboarding
flow, just not asserted against directly.

**Bypassed by design on some builds.** Internal/shared-identity builds skip
this screen entirely: `useCommunityInit` auto-selects a configured default
relay as the first community without ever showing the choice UI. This is a
deliberate variant, not a bug, and a reader relying on "the user always sees
WelcomeSetup" would be wrong for that build configuration.

**Different on mobile.** Mobile has no independent join/create choice
screen. Its onboarding entry point pairs the phone with an already-onboarded
desktop identity (QR scan or a manually entered pairing code), inheriting
whichever community that desktop identity already resolved through this
same capability. Mobile does not re-implement first-community selection; it
consumes its result.

**Designed but not confirmed built:** `VISION_SOVEREIGN.md` describes a
"Connect on Buzz" web-embedded join with no separate onboarding flow, for
a sovereign-hosted community reachable from that community's own web
presence. No implementation of that specific flow was found while drafting
this node -- see *Scope and omissions* below.

## Boundary

This node does not describe:
- **How the underlying Nostr identity/keypair is created or backed up.**
  That is `#798`'s territory (first-identity). This capability's evidence
  above treats an identity as already resolved by the time `WelcomeSetup`
  is shown -- `WelcomeSetup` reads an existing identity's pubkey, it does
  not create one.
- **What happens after a community is chosen, once the transaction moves
  into profile setup, the starter-team introduction, and landing on the
  Welcome channel.** The same `CommunityOnboardingTransaction` continues
  into those stages (see the evidence entry on `CommunityOnboardingFlow.tsx`
  above), but their own UI, copy, and channel-landing behavior belong to
  `#796` (first-channel) and `#799` (the overall onboarding capability), not
  to the join/create choice documented here.
- **The onboarding capability as a whole** -- the full sequence from app
  install through identity, first community, first channel, and first
  message. That is `#799`'s document; this node is one step inside it.
- **Adding, switching, or leaving a community after first-run setup is
  complete.** `AddCommunityDialog`, `CommunitySwitcher`, and
  `leaveCommunity.ts` cover that ongoing-management surface, which reuses
  some of the same primitives (`InviteRedeemForm`, the community-onboarding
  transaction) but is not itself a first-run capability.
- **The Builderlab hosted-account backend's own API contract or
  architecture.** `hostedCommunityApi.ts` is cited here only as evidence
  that the "create a community" path exists and is wired up, not as this
  node's subject matter -- a future interface or architecture node for
  Builderlab integration would own that.

## Relationships

Declared: none. Checked: origin/launchpad's corpus tree at the recorded
revision carries no `capabilities`, architecture-component, or interface
node this capability could `references`, and none of this task's siblings
(`#796`, `#798`, `#799`) are merged, so an edge to any of them would resolve
in this worktree but not on the branch being merged into -- exactly the trap
`AGENTS.md`'s "Creating a node" step 9 warns against. Once `#798`
(first-identity) and `#799` (onboarding) merge, this node is the natural
place to add `part-of: <onboarding capability id>` and a `references` edge
toward whatever architecture or interface node eventually documents the
Builderlab hosted-community backend.

## Scope and omissions

**This node covers** the first-run capability of choosing to join an
existing community, create a new hosted one, or reconnect to one already
known, on desktop; the three entry surfaces that choice leads to (invite/
relay-URL join, join-policy consent, Builderlab-hosted create); the
membership-denied recovery path; the internal-build bypass that skips the
choice screen; and how mobile's pairing-based onboarding differs from and
depends on this same capability.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Identity/keypair creation and backup | `#798` (first-identity) |
| Profile setup, starter-team intro, and Welcome-channel landing after a community is chosen | `#796` (first-channel), `#799` (onboarding) |
| The onboarding capability end-to-end | `#799` |
| Post-first-run community add/switch/leave | ongoing community-management surfaces (`AddCommunityDialog`, `CommunitySwitcher`, `leaveCommunity.ts`) |
| The Builderlab hosted-account backend's own contract | a future architecture/interface node, not yet drafted |

**Expected but not verified when this node was written:**
- **No dedicated test file exercises `WelcomeSetup.tsx`'s own choice
  screen.** `communityOnboarding.test.mjs` covers the transaction primitives
  it drives, and an E2E screenshot spec exists
  (`desktop/tests/e2e/welcome-agent-modal-screenshots.spec.ts`), but neither
  was read in enough depth to confirm it exercises all three first-run
  choices end to end.
- **The Builderlab hosted-community create/select flow
  (`HostedCommunityOnboarding.tsx`) was read for its shape, not
  runtime-exercised**, so its sign-in and community-creation behavior is
  documented from source only.
- **`VISION_SOVEREIGN.md`'s "Connect on Buzz" web-embedded join path was
  not confirmed as built or unbuilt** beyond a source search that found no
  matching desktop/web implementation -- see the `INFERENCE` entry in the
  evidence ledger above.
- **Mobile's pairing-based onboarding was read only at its entry view**
  (`_PairingWelcomeView`); the full pairing protocol and how it resolves
  the paired community were not traced end to end for this node.
