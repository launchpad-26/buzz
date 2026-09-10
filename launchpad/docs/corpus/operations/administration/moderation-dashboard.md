---
id: operations-administration-moderation-dashboard
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The desktop app's Settings navigation carries a 'moderation' section (value `moderation`, label 'Moderation'), the panel-rendering switch renders `ModerationQueueCard` for that value, and the component itself reads the viewer's community role via `useMyRelayMembershipQuery` and only renders its Queue/Audit log tabs when that role is `owner` or `admin` — otherwise it shows 'The moderation queue is available to community moderators only.'"
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:254-257"
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:967-968"
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:563-586"
  - statement: "The relay's `authorize_moderation_action`/`decide_authority` functions grant a community `owner` every `ModerationAction` unconditionally, grant a community `admin` every action except `Ban`/`Timeout` against a target whose own community role is `owner` or `admin`, and otherwise grant only channel-scoped `DeleteMessage`/`Kick` to a channel owner/admin — anyone else is denied with 'moderator access required'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:83-138"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:146-181"
  - statement: "The relay serves `GET /moderation/reports`, `GET /moderation/audit` and `GET /moderation/restricted` through `authorize_moderation_read`, which verifies the request's NIP-98 signature and then requires `ModerationAction::ViewQueue` through the same authorization seam, returning 403 on failure; all three routes are registered on the relay's router."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2288-2333"
      - "crates/buzz-relay/src/router.rs:125-129"
  - statement: "`buzz-cli`'s `ModerationCmd` enum defines eight subcommands — `reports`, `resolve`, `ban`, `unban`, `timeout`, `untimeout`, `restricted`, `audit` — and the CLI's own root help text names `BUZZ_RELAY_URL` (default `http://localhost:3000`) and `BUZZ_PRIVATE_KEY` (required, hex or nsec) as the connection and signing-identity environment variables every subcommand needs; a doc comment on the enum states the signing key must be a community owner/admin because the relay authorizes every command."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1920-2014"
      - "crates/buzz-cli/src/lib.rs:71-90"
  - statement: "`crates/buzz-cli/src/commands/moderation.rs`'s five mutating subcommands (`ban`, `unban`, `timeout`, `untimeout`, `resolve`) each build a signed event with a `buzz_sdk::build_moderation_*` constructor and submit it via `client.submit_event`, while the three read subcommands (`reports`, `restricted`, `audit`) call `client.get_authed` against the corresponding `/moderation/*` path and print the raw response."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs:34-131"
  - statement: "`buzz moderation ban` and `buzz moderation timeout` each accept mutually exclusive `--expires-in <secs>` / `--expires-at <unix>` and an optional `--reason`; omitting both on `ban` produces a permanent ban, while `timeout` requires one of the two (its handler returns a usage error otherwise) — `unban` and `untimeout` take only `--pubkey`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1958-2005"
      - "crates/buzz-cli/src/commands/moderation.rs:61-87"
  - statement: "The relay's 9044 resolve handler (`handle_resolve`) validates the command's `status`/`action` tag pairing (`status` must be `resolved` or `dismissed`; `action` one of `delete|kick|ban|timeout|dismiss|escalate`; `action == \"dismiss\"` if and only if `status == \"dismissed\"`) and then records the decision through `resolve_report_decision_only` — it never itself calls any ban/timeout/delete/kick enforcement logic. The module's own doc comment states this explicitly: for `delete`/`kick`/`ban`/`timeout` resolutions, 'the client's paired 9040-9043 writes the unprefixed enforcement row' — enforcement is a separate command the caller must also issue."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:375-469"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:1-52"
  - statement: "The desktop queue's `handleResolve` enforces first — calling `deleteMessage`, `removeChannelMember`, or the ban mutation depending on the chosen action — and only submits the 9044 resolve mutation for every open report against that target afterward, with a comment explaining why: resolving DMs the reporter 'reviewed and acted on,' so a failed enforcement must not be followed by that message. `resolvableActions` never includes `timeout` for any target kind, and `enforceResolution`'s own `timeout` branch throws 'Timeout is not available from the queue yet.' — so the desktop queue's one-click resolutions cover delete, kick, ban, escalate and dismiss, not timeout."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:401-438"
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx:112-138"
      - "desktop/src/features/settings/lib/moderationQueue.ts:253-264"
  - statement: "`buzz messages delete --event <hex>` (optionally `--action-id`, `--reason-code`, `--public-reason` for the public tombstone) builds a delete-message event via `buzz_sdk::build_delete_message_with_options`, and `buzz channels remove-member --channel <uuid> --pubkey <hex>` builds a member-removal event via `buzz_sdk::build_remove_member` — these are the CLI's delete/kick enforcement primitives, and neither lives inside the `buzz moderation` command group."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:443-455"
      - "crates/buzz-cli/src/commands/messages.rs:820-842"
      - "crates/buzz-cli/src/lib.rs:698-707"
      - "crates/buzz-cli/src/commands/channels.rs:1399-1403"
  - statement: "`crates/buzz-core/src/kind.rs` defines `KIND_REPORT` = 1984, `KIND_NIP29_REMOVE_USER` = 9001, `KIND_NIP29_DELETE_EVENT` = 9005, and the five moderation-command kinds `KIND_MODERATION_BAN` / `UNBAN` / `TIMEOUT` / `UNTIMEOUT` / `RESOLVE_REPORT` = 9040 through 9044."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:327"
      - "crates/buzz-core/src/kind.rs:337"
      - "crates/buzz-core/src/kind.rs:341"
      - "crates/buzz-core/src/kind.rs:358-370"
  - statement: "Migration 0006 constrains `moderation_reports.status` to exactly `open`, `resolved`, `dismissed` or `escalated`, and `buzz moderation reports --status <s>` and `buzz moderation audit`/`buzz moderation restricted` read those rows and the paired `moderation_actions`/ban-timeout state back through the endpoints authorized in the entry above."
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql:16-30"
      - "crates/buzz-cli/src/commands/moderation.rs:105-131"
  - statement: "`crates/buzz-admin/src/main.rs` defines exactly five subcommands — `AddMember`, `RemoveMember`, `ListMembers`, `GenerateKey`, `ReconcileChannels` — none of which bans, times out, or resolves a report; the already-merged `architecture-context-relay-operator` node documents this same command set as the infrastructure operator's relay-membership CLI, a different role and a different command surface than the community moderation this guide operates."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:44-97"
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "A case-insensitive search of `mobile/lib` for 'moderation' returned no matches at the recorded revision, so no mobile moderation surface was found to document in this guide."
    entry_class: INFERENCE
    evidence:
      - "grep_repo(pattern='moderation', scope='mobile/lib', case_insensitive=true) -> no matches, run at commit 473205a7457b208455f188847bfb27b01aa83cac"
    confidence: 0.85
  - statement: "VISION_MODERATION.md states escalation 'writes a durable, queryable record for the platform operator — but the platform-side inbox that consumes it is a separate build,' and separately states the platform-safety layer (as opposed to the community-moderation layer this guide operates) 'belongs to whoever operates the relay.'"
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:55"
      - "VISION_MODERATION.md:17"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped node's required sections — Overview, an optional Before you start, one numbered task sequence per logical goal (forked into labeled branches when the task genuinely has more than one entry point or interface), See also, a Boundary statement, Relationships, and Scope and omissions."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Issue #1195's Definition of Done requires this node to state a goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands/config rather than give generic advice — the procedure-template tail bullets, not a capability-template tail."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1195 definition of done"
relationships:
  - type: references
    target: capabilities-moderation-operator-dashboard
  - type: references
    target: capabilities-moderation-moderation-command
  - type: references
    target: capabilities-moderation-moderation
  - type: references
    target: architecture-context-relay-operator
---

# Operate the community moderation dashboard: how-to

Review the open-report queue, resolve or dismiss a report, take direct action
against a member (ban, unban, time out, clear a timeout), and check the audit
trail — as a community owner or admin, using either the desktop app's
Moderation settings panel or the `buzz moderation` CLI command group, the two
interfaces onto the same relay-enforced capability
(`capabilities-moderation-operator-dashboard`).

## Before you start

- **Your signing key must hold the `owner` or `admin` community role** in the
  target community's `relay_members` table. The relay's own authorization
  seam (`authorize_moderation_action` / `decide_authority`) enforces this for
  every read and write below; a plain member is denied, and even a
  channel-level owner/admin without a community role is limited to deleting
  messages and kicking members in their own channel — they cannot ban, time
  out, or resolve a report.
- **Desktop path:** the desktop app is already signed in and connected to the
  target community as a member holding that role. No separate login step
  exists for moderation — the same session's role decides whether the
  Moderation panel renders its Queue/Audit tabs or the "moderators only"
  message.
- **CLI path:** `buzz` is built (`cargo build --release -p buzz-cli`), and
  `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY` are set to the target relay and an
  owner/admin's private key (hex or nsec) — either as environment variables or
  as `--relay`/`--private-key` flags on each invocation. Moderation commands
  carry no channel scope; the community is whichever one the relay host in
  `--relay`/`BUZZ_RELAY_URL` resolves to.
- **To resolve a specific report,** you need its kind:1984 event id (hex) —
  obtained from the queue itself in Task 1, step 1.
- **To act on a member directly,** you need their pubkey (hex).
- **This guide does not cover filing a report** — that is the member-facing
  "Report" action VISION_MODERATION.md describes, a different capability from
  the one this guide operates.

## Task 1: Review and resolve an open report

1. **Open the queue.**
   - Desktop: Settings → Moderation → Queue tab.
   - CLI: `buzz moderation reports --status open` (add `--limit <n>` to change
     the default of 50). Each row carries `reporterPubkey`, `targetKind`,
     `target`, `reportType`, `note`, and `channelId`.
2. **Identify the target and which resolutions are actually enforceable.**
   - Desktop groups open reports by target and only offers a resolution the
     enforcement machinery can carry out for that target's kind: `delete` and
     `kick` require an event target with a resolvable channel; `ban` needs
     only a pubkey (looked up from an event target's signer when necessary);
     `escalate` and `dismiss` are always offered. **`timeout` is never offered
     from the desktop queue for any target kind** — see step 4b below for why,
     and how to time out a reported member anyway.
   - CLI: nothing filters the action for you — read `targetKind` yourself and
     choose from `delete | kick | ban | timeout | dismiss | escalate`
     accordingly; an unenforceable choice fails when you issue the paired
     command in step 3, not before.
3. **Enforce first, if the action requires it — before recording the
   resolution.** A 9044 resolve command only records the decision; it does
   **not** itself ban, time out, delete, or kick anyone. The desktop UI
   automates this ordering for you (its one click enforces, then resolves);
   the CLI does not chain the two calls, so skipping this step on the CLI
   records a decision that was never carried out.
   - Desktop: this step happens automatically as part of clicking a
     resolution in step 4a.
   - CLI, issue the matching command before step 4b:
     - `ban` → `buzz moderation ban --pubkey <hex> [--expires-in <secs> |
       --expires-at <unix>] [--reason "..."]`
     - `timeout` → `buzz moderation timeout --pubkey <hex> (--expires-in
       <secs> | --expires-at <unix>) [--reason "..."]`
     - `delete` → `buzz messages delete --event <hex> [--public-reason
       "..."]`
     - `kick` → `buzz channels remove-member --channel <uuid> --pubkey <hex>`
     - `dismiss` and `escalate` need no enforcement command — go straight to
       step 4.
4. **Record the resolution.**
   - 4a. Desktop: click the report group's resolve action; the panel issues
     the paired enforcement (step 3) and the 9044 resolve call together.
   - 4b. CLI: `buzz moderation resolve --report <report-event-id-hex> --status
     <resolved|dismissed> --action <delete|kick|ban|timeout|dismiss|escalate>
     [--reason "..."]`. `dismiss` pairs only with `--status dismissed`; every
     other action pairs with `--status resolved` — the relay rejects any
     other pairing. To time out a reported member (unavailable as a one-click
     desktop resolution), enforce with `buzz moderation timeout` in step 3
     and then resolve here with `--action timeout --status resolved`.
5. **Verify.** `buzz moderation reports --status resolved` (or `--status
   dismissed`) should now list the target's report with `resolvedBy` and
   `actionId` populated; in the desktop queue, the report group disappears
   once every open report against that target is resolved.

## Task 2: Ban, unban, time out, or clear a timeout directly

Use this task when you are acting on a member without an open report to
resolve — for example, a direct ban after out-of-band evidence.

1. Confirm you have the target member's pubkey (hex).
2. **Ban:** `buzz moderation ban --pubkey <hex> [--expires-in <secs> |
   --expires-at <unix>] [--reason "..."]`. Omit both expiry flags for a
   permanent ban. Enforcement is immediate — the ban is checked at the
   identity/session seam, not only as a queue flag.
   - **Guard rail:** if you hold the `admin` role, you cannot ban a target
     whose own community role is `owner` or `admin` — only the owner may act
     on one. This guard does not apply to `unban`/`untimeout` below.
3. **Time out:** `buzz moderation timeout --pubkey <hex> (--expires-in <secs>
   | --expires-at <unix>) [--reason "..."]` — one expiry flag is required;
   there is no permanent timeout. A timeout blocks writes only — the member
   stays connected and can still read.
4. **Lift a restriction early:** `buzz moderation unban --pubkey <hex>` or
   `buzz moderation untimeout --pubkey <hex>`.
5. **Verify:** `buzz moderation restricted` lists every currently-banned or
   timed-out member in the community.

There is no desktop-only equivalent of this task outside the queue at the
recorded revision — the desktop app's ban action is reachable through the
queue's resolve flow (Task 1); acting on a member with no open report is a
CLI-only path today.

## See also

- `capabilities-moderation-operator-dashboard` — the capability this guide
  operates: what the dashboard is, its maturity, and its authorization model,
  stated once and not repeated here.
- `capabilities-moderation-moderation-command` — the full kind 9040–9044 wire
  contract, the freshness/replay defenses, and the complete authorization
  decision table behind every command this guide issues.
- `capabilities-moderation-moderation` — the product-level moderation
  capability this dashboard is one interface onto, including the
  community/platform-safety two-layer design and the report/decide/enforce
  /audit/notice loop.
- VISION_MODERATION.md — the product vision this dashboard implements,
  including the member-facing report action this guide does not cover.

## Boundary

This node does not describe:

- **Which action is the right call for a given report.** That is a
  community-judgment call VISION_MODERATION.md leaves to the community's own
  owners and admins; this guide covers how to execute a decision once made,
  not how to make it.
- **The full per-role authorization decision table, freshness/replay
  defenses, or notice-DM mechanics** behind these commands — see
  `capabilities-moderation-moderation-command` and
  `capabilities-moderation-moderation`.
- **How to acquire moderation judgment from scratch as a newcomer.** No
  Diátaxis Tutorial-form corpus template exists yet
  (`corpus-template-procedure`'s own Boundary section names the same gap).
- **Provisioning, deploying, or monitoring the relay process itself.** That is
  the distinct "relay operator" role's territory
  (`architecture-context-relay-operator`) — a different role from the
  community owner/admin this guide addresses, and a different CLI
  (`buzz-admin`, which has no moderation subcommand at all, not `buzz-cli`).
- **A platform-safety escalation dashboard for the infrastructure operator.**
  Choosing `--action escalate` writes an audit record only; no inbox consumes
  it in this repository at the recorded revision (see *Scope and omissions*).
- **Filing a report as a member.** That is the input to this guide's Task 1,
  not a step in it.

## Relationships

- `references`: [`capabilities-moderation-operator-dashboard`](../../capabilities/moderation/operator-dashboard.md)
  — the capability this guide is the operational how-to for.
- `references`: [`capabilities-moderation-moderation-command`](../../capabilities/moderation/moderation-command.md)
  — the wire contract and authorization matrix underlying every command
  issued in Tasks 1 and 2.
- `references`: [`capabilities-moderation-moderation`](../../capabilities/moderation/moderation.md)
  — the product-level capability and the two-layer design named in *Before
  you start* and *Boundary*.
- `references`: [`architecture-context-relay-operator`](../../architecture/context/relay-operator.md)
  — cited for the boundary distinction above: that node's "relay operator"
  role and its `buzz-admin` CLI are different from the community owner/admin
  and `buzz-cli` this guide addresses.

No `part-of` edge is declared: at the recorded revision no broader
`operations`-typed node exists on `origin/launchpad` for this document to sit
under — checked by enumeration
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
returns no path under `operations/`), not assumed. This is the first
`operations`-typed node and the first node authored from
`corpus-template-procedure`; a future `operations`-level parent node, if one
is added, is the moment to add that edge.

## Scope and omissions

**This node covers** how a community owner or admin operates the moderation
dashboard today: opening and reading the report queue, choosing and
enforcing a resolution, recording that resolution, acting on a member
directly outside the queue, and checking the audit trail — on both the
desktop app and the `buzz-cli` interface, including the operationally
significant ordering rule (enforce, then record) that a CLI operator must
apply by hand.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What the moderation capability is, its maturity, and its shipped/not-shipped boundary | `capabilities-moderation-operator-dashboard`, `capabilities-moderation-moderation` |
| The kind 9040–9044 wire contract, freshness/replay defenses, and full authorization matrix | `capabilities-moderation-moderation-command` |
| Notice-DM delivery mechanics and privacy rules | a dedicated moderation-notice capability node (not yet merged at the recorded revision) |
| Filing a report as a member | a separate capability, not this procedure |
| Deploying, upgrading, or monitoring the relay itself | `architecture-context-relay-operator` |
| A platform-operator escalation inbox for `--action escalate` | not built yet, per VISION_MODERATION.md's "Honest Edges" |
| A mobile moderation surface | none found — see the evidence ledger's search result |
| Whether an autonomous agent (as opposed to a human operator scripting `buzz-cli`) should ever issue a ban/timeout/resolve command on its own judgment | out of scope for this guide, which assumes a human decision behind every command it documents |

**Expected but not verified when this node was written:**

- **No command in this guide was executed against a live relay and Postgres
  instance while drafting it.** Every step is grounded in the source that
  implements it (the CLI's argument parsing and event-building code, the
  relay's handler and authorization logic, the desktop UI's own resolve
  flow), not in an end-to-end run. The Good Docs Project discipline
  `corpus-template-procedure` adopts calls for testing a how-to "from start to
  finish"; that run was not performed here, and re-verifying against a live
  relay before treating this guide as load-bearing for an actual incident is
  reasonable caution.
- **Whether `buzz-agent` or any other automated harness in this repository
  currently invokes `buzz moderation` commands programmatically** was not
  checked; this guide is written for a human operator typing these commands,
  not for an autonomous caller.
- **The exact JSON shape `buzz moderation reports`/`audit`/`restricted` print**
  was not enumerated field-by-field beyond the `ModerationReport` type read
  from the desktop API layer — the CLI prints the relay's raw response
  unformatted, and its precise schema is `capabilities-moderation-moderation-command`'s
  territory, not re-derived here.
