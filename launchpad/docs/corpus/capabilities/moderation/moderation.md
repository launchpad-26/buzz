---
id: capabilities-moderation-moderation
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "VISION_MODERATION.md states that Buzz moderation splits into two layers: community moderation (subjective, per-community rule enforcement by that community's own owners/admins, structurally scoped to the tenant) and platform safety (the severe class -- illegal content, network-level abuse, legal reporting obligations -- never delegated to community admins), and that this document's subject is the first layer only."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:11-19"
  - statement: "VISION_MODERATION.md states the loop as report -> queue -> human decision -> enforcement -> audit -> notice, and frames the design choice explicitly: most of the nostr ecosystem treats moderation as admission policy (allow/block lists filtering at the door), while Buzz treats a report as the start of a human decision, never a trigger for an automatic one."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:3-7"
  - statement: "A NIP-56 report (kind:1984) is accepted at ingest, validated, and persisted to a tenant-scoped moderation_reports queue; it is never stored as an ordinary event and never fanned out to subscribers, so reporter identity cannot leak through a future query bug against the public event store."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:321-327"
      - "crates/buzz-relay/src/handlers/report.rs:1-18"
      - "crates/buzz-relay/src/handlers/report.rs:39-80"
      - "migrations/0006_moderation.sql:1-14"
  - statement: "A report row carries a target_kind of exactly one of event, pubkey, or blob, is looked up strictly under the requesting TenantContext (never a global/cross-tenant lookup), and REPORT_TYPES pins the accepted NIP-56 category vocabulary to illegal, nudity, malware, spam, impersonation, profanity, other."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/report.rs:6-18"
      - "crates/buzz-relay/src/handlers/report.rs:28-37"
      - "crates/buzz-relay/src/handlers/report.rs:44-75"
      - "migrations/0006_moderation.sql:16-34"
  - statement: "Five community moderation commands exist as dedicated event kinds 9040-9044 (ban, unban, timeout, untimeout, resolve-report), routed like the existing NIP-43 relay-admin 9030-series: validated and executed directly by the relay rather than stored as ordinary events, with is_moderation_command_kind as the single canonical kind-range check used instead of scattering 9040..=9044 matches across the codebase."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:353-385"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:1-57"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:91-133"
  - statement: "A resolve-report command (kind 9044) requires exactly one action from delete|kick|ban|timeout|dismiss|escalate; delete and kick fan out through the existing kind 9005 (NIP-29 delete event) and kind 9001 (NIP-29 remove user) paths, and ban/timeout fan out through the 9040/9042 handlers -- there is no second, duplicate implementation of those side effects for the resolve path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:35-52"
      - "crates/buzz-core/src/kind.rs:333-351"
  - statement: "Authorization for every moderation action routes through one function, authorize_moderation_action, rather than inline role checks: a community owner (relay_members.role, tenant-scoped) holds every ModerationAction community-wide with no guard rail; a community admin holds every action too, except it cannot Ban or Timeout a target whose own community role is owner or admin (only the owner may action an admin); a channel owner/admin (with no community role) holds only DeleteMessage and Kick, scoped to their channel; a plain member or stranger holds none. Unban/Untimeout are deliberately unguarded at this seam because they only lift a restriction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:24-181"
  - statement: "The admin guard rail and the full authorization matrix (owner-unrestricted, admin-guarded-on-ban/timeout-of-privileged-targets, channel-role-scoped-to-delete/kick, member/stranger-denied) is exercised by a dedicated unit-test module covering all eight ModerationAction variants."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:183-335"
  - statement: "A community ban is enforced at the WebSocket authentication seam (NIP-42), immediately after auth verification succeeds and before the allowlist/relay-membership gates: moderation_restriction_state is checked for the authenticated pubkey and, if clear, for its NIP-OA-proven owner pubkey (an owner ban cascades to the agent; an agent ban does not cascade to the owner); a lookup error denies fail-closed and is reported as a distinct internal-error reason rather than a false ban claim; a matched ban closes the connection immediately with zero further processing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:94-180"
  - statement: "The same durable restriction state is re-checked as a write-path backstop at event ingest, even on an already-authenticated connection, so a banned or timed-out member whose live-disconnect broadcast was missed by a still-open socket cannot keep writing; moderation-command and relay-admin kinds are exempted from this specific gate because their own handlers enforce the ban themselves (so a timed-out admin can still lift their own timeout)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2117"
      - "crates/buzz-relay/src/handlers/ingest.rs:2144-2160"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:99-121"
  - statement: "Every ban, unban, timeout, untimeout, and report resolution writes a durable moderation_actions audit row (who, what, whom, why, when), separate from a report's own moderation_reports row; migration 0006_moderation.sql's own header states these three tables (reports, bans/timeouts, audit actions) are all tenant-scoped, with community_id NOT NULL and community-id-leading keys per the repository's tenant-isolation lints."
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql:1-8"
      - "crates/buzz-db/src/store/moderation.rs"
  - statement: "A resolve-report command's audit row records the decision (prefixed resolve:, e.g. resolve:ban, resolve:delete) separately from the paired enforcement row the client's own 9040-9043 command writes for the actual enforcement action, so the audit trail never claims an enforcement happened that the corresponding command row does not itself record; dismiss audits as dismiss_report and escalate as escalate, both left unprefixed so escalate stays queryable for the platform-safety lane."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:35-52"
      - "crates/buzz-db/src/store/moderation.rs"
  - statement: "Resolving a report as escalate sets the report's status to escalated and writes an audit row, but no code in buzz-relay or buzz-db constructs, queues, or forwards that escalation to any separate platform-operator inbox or notification pipeline; the only cross-community read surface found is buzz-db/src/admin_moderation.rs, an explicitly deployment-global (non-tenant-scoped) set of read queries over reports/actions for a private admin plane, which is a data surface for a future consumer rather than an escalation pipeline itself. This matches VISION_MODERATION.md's own statement that escalation is a hook today, not a pipeline: the substrate (a durable, queryable record) exists, but the platform-side inbox that consumes it is a separate, not-yet-built surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/moderation.rs:70"
      - "crates/buzz-db/src/store/moderation.rs:113"
      - "crates/buzz-db/src/store/moderation.rs:126"
      - "crates/buzz-db/src/store/moderation.rs:306"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:35-52"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:387-390"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:445"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:505"
      - "crates/buzz-db/src/store/admin_moderation.rs:1-6"
      - "VISION_MODERATION.md:55"
  - statement: "Moderation resolution and restriction notices are delivered as real, relay-signed direct messages (not synthetic client-only banners): the relay creates or reuses a two-party DM channel between a per-community moderation identity and the affected user, and the same primitive carries reporter-resolution notices, actioned-author notices, and timeout/ban notices; a notice to an actioned author never names the reporter(s) or quotes report notes, and a notice to a reporter never reveals other reporters."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs:1-50"
  - statement: "VISION_MODERATION.md states notices are best-effort and never block enforcement -- a ban lands even if the notice DM fails to send -- framing enforcement as the promise and notification as the courtesy."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:59"
  - statement: "Every moderation-side-effect module's own header comment labels itself '(Phase 1 contract)' and cites a locked design (moderation_commands.rs, moderation_authz.rs, moderation_notices.rs, and report.rs all do this), and migration 0006's header dates the design to a decision locked 2026-07-07; the PLANS/COMMUNITY_MODERATION_PLAN.md design document these comments cite is not present in the repository at the checked revision, so this node's maturity claim rests on the shipped code and its own contract-labeled comments, not on reading that plan document directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:1-3"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-3"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs:1-3"
      - "crates/buzz-relay/src/handlers/report.rs:1-3"
      - "migrations/0006_moderation.sql:1-4"
  - statement: "buzz-cli exposes a moderation command group (buzz moderation ban/unban/timeout/untimeout/resolve) whose mutating subcommands submit signed kind 9040-9044 command events via POST /events -- the same relay validate-and-execute-directly path described above -- while its read subcommands (reports/restricted/audit) hit dedicated mod-only, NIP-98-authenticated relay endpoints under /moderation/* rather than a public REQ filter, because reports and audit rows are structured queue rows, not public nostr events."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs:1-16"
  - statement: "The desktop app has a dedicated moderation feature module (desktop/src/features/moderation) plus moderation-aware code in the settings and channels feature modules (a moderation queue card, per-message moderation menu items, a report-message dialog, and channel-management moderation actions), indicating the capability is exposed as first-class desktop UI rather than only a CLI/API surface -- the UI's own behavior against the accessibility patterns in AGENTS.md was not audited as part of this node."
    entry_class: FACT
    evidence:
      - "desktop/src/features/moderation/ui/MessageModerationMenuItems.tsx"
      - "desktop/src/features/moderation/ui/ReportMessageDialog.tsx"
      - "desktop/src/features/settings/ui/ModerationQueueCard.tsx"
      - "desktop/src/features/channels/ui/ChannelManagementModerationActions.tsx"
  - statement: "Issue #785's own Definition of Done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation without duplicating their canonical content, and link verification demonstrating the capability -- the capability template's own required-sections shape, not the flow template's shape, confirming this task is capability-typed and not mis-generated."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#785 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-event-ingestion
---

# Moderation: capability

Buzz gives a community's own owners and admins the tools to enforce their
community's rules against their own members: a member can report a message,
pubkey, or media blob privately; an owner or admin sees those reports in a
queue and, in one signed action, dismisses, deletes, kicks, times out, bans,
or escalates; the relay enforces the decision structurally (a ban blocks
authentication itself, not just future feed reads); the decision and its
enforcement are both durably audited; and the affected member and the
reporter both hear the outcome. This is the *community* moderation layer --
subjective, per-community rule enforcement, structurally fenced to the
tenant it happened in. A second, more severe layer (illegal content,
platform-level abuse, legal reporting obligations) is never delegated to
community admins; a report or action here can only be *escalated* toward
that layer today, not fully routed into it (see *Maturity*).

## Maturity

**Shipped, not designed-only.** The report/decide/enforce/audit loop exists
in merged code: NIP-56 report ingest (`crates/buzz-relay/src/handlers/report.rs`),
the five moderation command kinds 9040-9044
(`crates/buzz-relay/src/handlers/moderation_commands.rs`), the single
authorization seam (`crates/buzz-relay/src/handlers/moderation_authz.rs`,
with a dedicated unit-test module exercising every action against every
role), ban enforcement at the WebSocket auth seam plus a durable re-check at
ingest, relay-signed notice DMs
(`crates/buzz-relay/src/handlers/moderation_notices.rs`), a three-table
tenant-scoped schema (`migrations/0006_moderation.sql`), a `buzz-cli
moderation` command group, and a dedicated desktop moderation feature
module. Every side-effecting module labels itself "(Phase 1 contract)" in
its own header comment, consistent with a deliberately scoped first
increment rather than a finished, final surface.

**One documented gap in that increment: escalation is a hook, not a
pipeline.** Resolving a report as `escalate` records status `escalated` and
an audit row, but no code path was found that forwards that record to a
separate platform-operator inbox or notification system. The nearest
existing surface, `crates/buzz-db/src/admin_moderation.rs`, is an explicitly
deployment-global (non-tenant-scoped) set of *read* queries over reports and
actions -- a data surface a future consumer could build against, not an
escalation pipeline itself. This matches `VISION_MODERATION.md`'s own
framing: the substrate is there, the tooling above it is a separate,
not-yet-built piece.

**Two other scoped-out pieces, named in the product vision and not found in
code either:** there is no volunteer-moderator tier (only community
owner/admin hold moderation authority today -- deliberately, per
`VISION_MODERATION.md`, so a moderator tier can be added later as a policy
change rather than a rewrite), and there is no automod -- nothing scans
content before it posts; pre-send filtering, trusted-reporter weighting, and
shared blocklists are named as future layers on top of this substrate, not
present today.

## Boundary

This node states *what the moderation capability is and can do* at a
product level. It deliberately does not re-derive the depth already owned
by neighboring, more specific documents (some of which are separate,
not-yet-merged corpus tasks at the time this node was written, and so are
named here in prose only, with no `relationships` edge to an id that does
not yet exist on `origin/launchpad`):

- **How authorization is decided, role by role** -- the full
  `authorize_moderation_action` decision table and its guard rails belong to
  a dedicated moderation-authorization node, not restated here beyond the
  one-paragraph summary above.
- **The exact command wire contract** -- kind 9040-9044 tag vocabulary,
  validation rules, and per-kind side effects belong to a dedicated
  moderation-command node.
- **The notice-delivery mechanism** -- the DM-channel-reuse pattern, message
  templates, and privacy rules for what a notice may and may not say belong
  to a dedicated moderation-notice node.
- **The platform-operator/deployment-global view** -- `admin_moderation.rs`
  and whatever consumes it belong to a dedicated operator-dashboard node.
- **The report data model and lifecycle in depth** -- `moderation_reports`
  row shape, status transitions, and idempotency belong to a dedicated
  report node.
- **How this capability is built** -- containers, components, and
  technology choices (Postgres tables, the relay's handler modules) are
  cited here as evidence of the capability's existence, not described as
  architecture in their own right; this node `references` the two merged
  architecture-flow nodes that already document the enforcement seams this
  capability depends on (see *Relationships*) rather than restating them.
- **The step-by-step path through one report** -- the sequence a single
  report takes from submission to notice is a flow concern, not this
  capability-level statement of what the product can do.
- **How the running system is operated** -- deployment, monitoring, and
  incident response for the moderation subsystem are an operations concern,
  not covered here.

## Relationships

- `references`: [`architecture-flows-websocket-authentication`](../../architecture/flows/websocket-authentication.md)
  -- the merged flow node that already documents the NIP-42 ban gate this
  capability's enforcement relies on (auth-seam ban check, NIP-OA
  owner-to-agent cascade, fail-closed on a DB error). This capability node
  cites the behavior in one paragraph and does not restate its mechanics.
- `references`: [`architecture-flows-event-ingestion`](../../architecture/flows/event-ingestion.md)
  -- the merged flow node that already documents the sidecarred, never-stored
  handling of NIP-56 reports and moderation-command kinds, and the durable
  ingest-time restriction re-check that backstops the auth-seam gate above.
- No `relationships` toward `capabilities-moderation-*` sibling documents
  (authorization, command, notice, operator dashboard, report) are declared,
  because none of them exist as merged nodes on `origin/launchpad` at the
  recorded revision -- checked directly with
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/capabilities/moderation/`,
  which returned nothing. Declaring an edge to an id that does not yet
  resolve is a hard validation error, not merely premature; the first of
  those sibling nodes to merge is the moment to add the corresponding edge
  back to this one.

## Scope and omissions

**This node covers** the moderation capability as a product-level statement:
what a member, an owner/admin, the room, a restricted user, and a reporter
each experience; the two-layer split between community moderation and
platform safety; the report/decide/enforce/audit/notice loop and the design
choice (reports are signals, never triggers) that shapes it; and what is
shipped versus what is named as a future layer (a moderator tier, automod,
a full escalation pipeline).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full per-role authorization decision table | a dedicated moderation-authorization capability node (not yet merged) |
| The kind 9040-9044 wire contract in depth | a dedicated moderation-command capability node (not yet merged) |
| Notice delivery mechanics and privacy rules | a dedicated moderation-notice capability node (not yet merged) |
| The platform-operator/deployment-global view | a dedicated operator-dashboard capability node (not yet merged) |
| The report data model and lifecycle in depth | a dedicated report capability node (not yet merged) |
| How the capability is built (containers, components, schema detail) | `architecture-flows-websocket-authentication`, `architecture-flows-event-ingestion`, and any future architecture/component nodes over `buzz-relay`/`buzz-db` |
| The step-by-step path through one report, end to end | a future flow node (not yet merged) |
| How the running system is operated (deployment, monitoring, incident response) | the `operations` corpus surface |
| Accessibility of the desktop moderation UI | not audited as part of this node |

**Expected but not verified when this node was written:**

- **`PLANS/COMMUNITY_MODERATION_PLAN.md`, cited by name in several code
  comments as the design's source of record, is not present in this
  repository at the checked revision.** This node's maturity and design
  claims rest on the shipped code and its own contract-labeled comments,
  never on that plan document, which could not be opened.
- **Whether any consumer currently reads `admin_moderation.rs`'s
  deployment-global queries was not checked.** This node states only that
  the module exists and is not tenant-scoped; whether a platform-operator
  UI or process already consumes it is unverified.
- **Whether every desktop moderation surface enforces the same
  authorization rules as the relay (defense in depth vs. UI-only gating) was
  not checked.** This node verified the relay-side authorization seam only.
- **Volunteer-moderator-tier and automod claims come from `VISION_MODERATION.md`
  stating they do not exist yet, corroborated only by their absence from a
  targeted code search (`ModerationAction`'s closed variant list, and no
  pre-send content-scanning call site found in the ingest path) rather than
  an exhaustive audit of every code path that could implement either.**
