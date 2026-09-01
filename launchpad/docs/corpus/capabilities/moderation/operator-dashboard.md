---
id: capabilities-moderation-operator-dashboard
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The desktop app's Settings surface has a dedicated 'Moderation' panel (nav entry value 'moderation', label 'Moderation') that renders `ModerationQueueCard`, and that card exposes a 'Queue' tab (open reports, grouped by target) and an 'Audit log' tab (accepted moderation actions, newest first)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:209-212"
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:868-869"
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:553-596"
  - statement: "The panel gates itself client-side on the viewer's own community role, read via `useMyRelayMembershipQuery`, and only renders the queue/audit tabs when that role is 'owner' or 'admin' -- otherwise it shows 'The moderation queue is available to community moderators only.'"
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:553-575"
  - statement: "The panel's reads (`GET /moderation/reports`, `GET /moderation/audit`, `GET /moderation/restricted`) are NIP-98-authed HTTP requests, and its writes (report resolution, ban, unban, timeout, untimeout) are signed Nostr events (kinds 9040-9044) published over the same WebSocket path as every other desktop write -- the client-side role gate mirrors, rather than replaces, the relay's own authorization."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/moderation.ts:1-20"
      - "desktop/src/shared/api/moderation.ts:339-375"
      - "crates/buzz-core/src/kind.rs:358"
      - "crates/buzz-core/src/kind.rs:360"
      - "crates/buzz-core/src/kind.rs:363"
      - "crates/buzz-core/src/kind.rs:365"
      - "crates/buzz-core/src/kind.rs:370"
  - statement: "The relay serves those three reads from dedicated handlers -- `moderation_reports` (`GET /moderation/reports`), `moderation_audit` (`GET /moderation/audit`), `moderation_restricted` (`GET /moderation/restricted`) -- registered on the relay's router, and every one of them calls `authorize_moderation_read`, which verifies the NIP-98 signature and then calls `authorize_moderation_action` with `ModerationAction::ViewQueue` before returning `403 Forbidden` on failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:122"
      - "crates/buzz-relay/src/api/bridge.rs:2207-2260"
      - "crates/buzz-relay/src/api/bridge.rs:2142-2183"
  - statement: "`authorize_moderation_action` reads the actor's role from `relay_members` (community-scoped) as the primary authority -- owner and admin can moderate any channel in their community -- and only falls back to a channel-local moderator role for the two channel-scoped actions (`DeleteMessage`, `Kick`) when the actor holds neither community role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-52"
  - statement: "The queue's one-click resolutions are: delete content, kick author, ban author, time out author (disabled until the resolve flow can collect a duration), escalate ('route to the platform-safety lane'), and dismiss -- and `resolvableActions` only offers an action when it can actually be enforced for the given target kind (e.g. delete/kick need an event target with a channel; ban needs only an author pubkey)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:140-175"
      - "desktop/src/features/settings/lib/moderationQueue.ts:234-264"
  - statement: "Report and audit rows persist in Postgres tables `moderation_reports` and `moderation_actions` (plus `community_bans` for active restrictions), created by a dedicated migration."
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql"
  - statement: "The same capability is also exposed through `buzz-cli`'s `moderation` command group -- `reports`/`restricted`/`audit` reads against the identical `/moderation/*` endpoints, and `ban`/`unban`/`timeout`/`untimeout`/`resolve` mutations submitting the identical signed command events (kinds 9040-9044) via `POST /events` -- so the desktop dashboard and the CLI are two interfaces onto one capability, not two capabilities."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs:1-15"
  - statement: "Client-side triage logic (severity ranking, grouping reports by target, prior-actions correlation, which resolutions are enforceable) has unit test coverage separate from the UI component, and the relay-side authorization and command handling each carry their own `mod tests`."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/lib/moderationQueue.test.mjs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "Root `VISION_MODERATION.md` states plainly that only two roles moderate today ('Owners and admins moderate. There is no volunteer-moderator tier yet -- deliberately'), that a moderation action is 'a cryptographically signed event, validated against their actual role and executed -- never stored as content,' and that 'Escalation is a hook today, not a pipeline. Escalating writes a durable, queryable record for the platform operator -- but the platform-side inbox that consumes it is a separate build.'"
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:43"
      - "VISION_MODERATION.md:55"
      - "VISION_MODERATION.md:57"
  - statement: "A separate, already-merged corpus node (`architecture-context-relay-operator`) defines 'the relay operator' as the role responsible for provisioning, deploying and administering the running `buzz-relay` process and its stateful dependencies (via `buzz-admin`, Docker Compose, or the Helm chart), and explicitly places 'interacting with channels as a member' -- the community layer this node documents -- out of that role's scope, in a separate context node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "This node's title uses 'operator' for the community owner/admin who moderates their own community (the two roles VISION_MODERATION.md names), not for the infrastructure 'relay operator' role `architecture-context-relay-operator` documents; the two dashboards these labels could name are not the same thing, and no platform-level escalation inbox for the infrastructure operator exists yet per the citation above."
    entry_class: INFERENCE
    evidence:
      - "VISION_MODERATION.md:55"
      - "VISION_MODERATION.md:57"
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
    confidence: 0.75
  - statement: "At repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, `origin/launchpad`'s `launchpad/docs/corpus/capabilities/` directory does not exist (no sibling capability node is merged), and `launchpad/docs/corpus/architecture/` carries the four C4 subtrees (`containers`, `context`, `deployment`, `flows`) plus `principles`, including `architecture-containers-desktop`, `architecture-containers-cli`, `architecture-containers-relay` and `architecture-context-relay-operator` -- the only nodes this document declares relationships toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no capabilities/ directory; architecture/{containers,context,deployment,flows,principles}/*.md present, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-cli
  - type: references
    target: architecture-context-relay-operator
---

# Operator dashboard: capability

A community's owner or admin can review every open user report in one place, see
what was already done about a target, and resolve it with a single action --
delete the content, kick or ban the author, time them out, escalate it to the
platform-safety lane, or dismiss it outright -- then check an audit log of every
enforcement action the community's moderators have taken. This is the capability
that turns Buzz's NIP-56 reporting substrate into something a human moderator can
actually act on, rather than a pile of unread signals.

## Maturity

**Shipped**, in the desktop app. The panel lives in Settings under "Moderation"
and is wired into the settings navigation and the panel-rendering switch that
picks a card per selected section (`desktop/src/features/settings/ui/
SettingsPanels.tsx:209-212,868-869`), rendering `ModerationQueueCard`
(`desktop/src/features/settings/ui/ModerationQueueCard.tsx`). It reads the open
report queue and the audit log over NIP-98-authed relay endpoints and writes
through the same signed-event path as every other desktop mutation
(`desktop/src/shared/api/moderation.ts`). The same capability is independently
reachable through `buzz-cli`'s `moderation` command group
(`crates/buzz-cli/src/commands/moderation.rs`), which is the agent-facing route
into the identical relay endpoints and command kinds.

**A narrower, adjacent surface is explicitly not shipped.** `VISION_MODERATION.md`
states escalation "writes a durable, queryable record for the platform operator --
but the platform-side inbox that consumes it is a separate build" (line 55). That
is a different dashboard, for a different role (the infrastructure "relay
operator" `architecture-context-relay-operator` documents), and this node's
Boundary section below draws that line explicitly so the two are not conflated
under the shared word "operator."

## Boundary

This node does not describe:

- **How it is built.** The containers that implement this capability -- the
  desktop app, the relay's HTTP/router layer, the CLI -- are documented by
  `architecture-containers-desktop`, `architecture-containers-relay` and
  `architecture-containers-cli` respectively. This node references them rather
  than restating their internals.
- **The interface contract itself.** The exact `/moderation/*` route shapes and
  the 9040-9044 command-event wire contract are a boundary-contract concern; no
  interface-family corpus node exists yet to hold that detail, so it stays
  uncited-in-full here beyond the citations needed to support this node's own
  claims.
- **The step-by-step path through one resolution.** The ordered sequence of "a
  moderator clicks Resolve -> the client enforces the action -> only then does
  it send the 9044 decision" is a flow, not a capability statement; no flow-family
  corpus node is merged yet to hold it.
- **How the running relay is operated.** Deploying, upgrading or monitoring
  `buzz-relay` itself is `architecture-context-relay-operator`'s territory, not
  this capability's -- see the naming note above.
- **The platform-safety escalation inbox.** Per `VISION_MODERATION.md:55`, the
  tooling that would consume an escalated report on the platform-operator side
  does not exist yet in this checkout; this node documents the community-level
  dashboard that exists today, not that future surface.

## Relationships

- `references`: `architecture-containers-desktop` -- the container that hosts
  the `ModerationQueueCard` panel this node documents.
- `references`: `architecture-containers-relay` -- the container serving the
  `/moderation/*` reads and validating the signed command events this panel's
  actions submit.
- `references`: `architecture-containers-cli` -- the container exposing the same
  capability to agents via `buzz moderation`.
- `references`: `architecture-context-relay-operator` -- cited for the boundary
  distinction above: that node's "relay operator" is a different role than the
  community owner/admin this capability's dashboard is built for.

## Scope and omissions

**This node covers** the community-facing moderation dashboard: where it lives
in the desktop app, what it lets an owner or admin see and do, how its two
client-facing interfaces (desktop UI, CLI) both resolve to the same relay
endpoints and command events, how access is authorized, and what test coverage
exists for its logic.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The containers that implement this capability | `architecture-containers-desktop`, `architecture-containers-relay`, `architecture-containers-cli` |
| The `/moderation/*` HTTP contract and the 9040-9044 command-event wire contract in full | a future interface-family corpus node |
| The step-by-step sequence of one resolve action | a future flow-family corpus node |
| Deploying, upgrading or monitoring the relay itself | `architecture-context-relay-operator` |
| A platform-operator escalation inbox | not yet built, per `VISION_MODERATION.md:55` |
| The mobile app's moderation surface, if any | not checked while writing this node -- see below |

**Expected but not verified when this node was written:**

- **Whether the Flutter mobile app has an equivalent moderation surface.**
  `mobile/lib` was not searched while drafting this node; the capability
  statement above is grounded only in the desktop and CLI evidence actually
  opened.
- **The exact wire numbers behind the "delete", "kick" enforcement paths**
  (referenced in code comments as separate from the 9040-9044 resolve-decision
  kinds) were not individually traced to their own `kind.rs` constants -- this
  node cites only the five moderation-command kinds it directly opened
  (9040-9044) and does not claim completeness over every event kind the
  enforcement paths touch.
- **Whether any end-to-end (Playwright or relay integration) test exercises this
  panel.** Only the unit-level test files cited above were located; no broader
  `crates/buzz-test-client` or `desktop/tests/e2e` moderation-specific suite was
  found while writing this node.
