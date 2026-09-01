---
id: capabilities-moderation-report
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
  - statement: "Kind 1984 is a Buzz event kind documented as 'NIP-56: Report an event, pubkey, or blob to relay moderators', defined as the constant KIND_REPORT."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:322-327"
  - statement: "A kind:1984 report event must carry exactly one `p` tag (the reported pubkey) and at most one of an `e` tag (a reported message/event, by 32-byte hex id) or an `x` tag (a reported media blob, by sha256); carrying both an `e` and an `x` tag is rejected, and a report with no `p` tag is rejected. The report type (one of `illegal`, `nudity`, `malware`, `spam`, `impersonation`, `profanity`, `other`) rides the third element of whichever target tag is present, and an unrecognized type is rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/report.rs:29-49"
      - "crates/buzz-relay/src/handlers/report.rs:121-174"
  - statement: "An `e`-tag (event) or `x`-tag (blob) report target is resolved only inside the reporting connection's own tenant/community: an event id not found in that tenant is rejected rather than searched for elsewhere, and a bare blob sha256 is resolved through a tenant-scoped media reference rather than treated as globally identifying."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/report.rs:1-18"
      - "crates/buzz-relay/src/handlers/report.rs:44-94"
  - statement: "A valid report is persisted to the `moderation_reports` table (via `insert_report`, keyed idempotently on `(community_id, report_event_id)`) and is never stored in the public events table or fanned out to subscribers; ingest explicitly suppresses public storage/fanout for this kind, and a banned or timed-out member may still submit one because a report is treated as a non-actioning signal rather than an ordinary write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2080-2091"
      - "crates/buzz-db/src/store/moderation.rs:186-230"
  - statement: "Submitting a report (kind:1984) requires only the ordinary `MessagesWrite` transport scope, the same scope required for a text note -- it is not gated by the community's moderation-authorization seam (`authorize_moderation_action`), which instead governs the moderator-side actions (delete, kick, ban, unban, timeout, resolve)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:345-362"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-15"
  - statement: "The desktop client's member-facing report entry point (`submitReport`) always targets a specific message: it signs a kind:1984 event carrying both the reported author's `p` tag and the message's `e` tag (with the report type as the `e` tag's third element) and an optional free-text note, then publishes it over the same signed-event WebSocket path used for other writes."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/moderation.ts:103-125"
  - statement: "`buzz-cli`'s `moderation` subcommand group exposes only the moderator- and reader-facing operations -- `reports` (list the queue), `resolve` (kind 9044), `ban`/`unban` (kind 9040/9041), `timeout`/`untimeout` (kind 9042/9043), `restricted` and `audit` -- and has no subcommand that submits a kind:1984 report itself; report submission is wired only through the desktop client's `submitReport`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1891-1978"
      - "crates/buzz-cli/src/commands/moderation.rs"
  - statement: "`list_reports` filters by an optional `status` column (open/resolved/dismissed/escalated, per the CLI's own `--status` help text) and orders results newest-first; `resolve_report` only updates a report row whose current status is `'open'`, making resolution a single-transition guard rather than an unconditional update."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/moderation.rs:234-258"
      - "crates/buzz-db/src/store/moderation.rs:308-332"
      - "crates/buzz-cli/src/lib.rs:1896-1903"
  - statement: "Resolving a report (kind:9044, `resolveReport` in the desktop client) pairs the `dismiss` action with a `dismissed` status and every other action (delete/kick/ban/timeout/escalate) with a `resolved` status, carries an optional moderator-authored `reason` that is described as landing in the public tombstone and the reporter-notice DM, and is gated by the same community owner/admin authorization seam as ban/timeout/kick."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/moderation.ts:185-208"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-15"
  - statement: "VISION_MODERATION.md states the product-level shape of this capability: a member's report is 'never broadcast, never stored as a public event, never visible to the person you reported'; it 'goes to the people who can act on it, and only them'; an owner/admin's moderation queue shows the reporter's identity to the moderator but never to the reported author; a report is 'validated and filed -- never stored in the event log, never fanned out to subscribers'; and 'no user report auto-removes anything' -- reports are signals a human must act on, never automatic triggers."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:3"
      - "VISION_MODERATION.md:25"
      - "VISION_MODERATION.md:27"
      - "VISION_MODERATION.md:39"
      - "VISION_MODERATION.md:41"
  - statement: "VISION_MODERATION.md states that the severe class of report (illegal content, network-level abuse, legal reporting obligations) is 'never delegated to community admins' and that a community owner or admin can escalate a report upward, with the escalation 'recorded durably for the platform operator's safety process' -- naming a platform-level escalation path this node's evidence does not otherwise trace into relay code."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:17"
  - statement: "Issue #787's Definition of Done requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- the capability-shaped Definition of Done, not the flow-shaped one (`States trigger, preconditions and termination/outcome`, `Lists ordered interactions...`) that a known generator bug attached to sibling issues #770 and #777 despite those issues also targeting `capabilities/` paths."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#787 definition of done (read directly via gh issue view; cross-checked against #770 and #777's definitions of done for the known generator-bug shape)"
  - statement: "No end-to-end test exercising `handle_report_event` against a running relay (submit a report, list it via `GET /moderation/reports`, resolve it) was found or run for this node; the behavior above is established by reading the handler, persistence and client code, plus the unit tests inside `crates/buzz-relay/src/handlers/report.rs`'s own `mod tests`, not by an integration run performed while drafting this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/report.rs:231-337"
---

# Report: capability

A member (human or agent) can report a specific message, a media blob, or a user's
account to the community's own owners and admins for moderation review. A report
names a reason (spam, profanity, illegal content, impersonation, malware, nudity, or
another supported category) and may carry a short free-text note. The report is
private end to end: it is never broadcast to the room, never stored as a public
event, and never visible to the person being reported. It reaches only the
community's owners and admins, who see it queued alongside other reports against the
same target and act on it -- dismiss, delete the message, kick, timeout, ban, or
escalate to the platform operator. The reporting member is later told the outcome.

## Maturity

**Shipped.** The relay validates and persists kind:1984 reports
(`crates/buzz-relay/src/handlers/report.rs`, `crates/buzz-db/src/moderation.rs`), the
desktop client has a working member-facing submission path
(`desktop/src/shared/api/moderation.ts`'s `submitReport`) and a moderator-facing
queue/resolution UI backed by `buzz-cli`'s `moderation` subcommand group and the
`/moderation/*` HTTP endpoints. `VISION_MODERATION.md` describes this loop as the
product's current design, not an aspiration.

**Partially shipped: platform-level escalation.** `VISION_MODERATION.md` describes an
escalate action whose record becomes durable input to "the platform operator's safety
process," but this node's evidence only traces the escalate action as far as the
community-level audit log (`crates/buzz-relay/src/handlers/moderation_authz.rs`) --
no platform-operator-facing consumer of an escalated report was located while
drafting this node. See *Scope and omissions*.

## Boundary

This node does not describe:
- **How the relay, database, and desktop client are built** -- their containers,
  components, and technology choices. See the architecture family
  (`launchpad/docs/corpus/architecture/**`) for that; no architecture node
  specifically covering moderation exists in the corpus yet, so no `references`
  edge is declared here (see *Relationships*).
- **The full moderation command surface** -- ban, unban, timeout, kick, and delete are
  separate community-moderation-enforcement operations that a report can lead to, but
  a report is a signal, not an enforcement action. This node covers the report/queue
  half of the loop; the enforcement half is a related but separate capability.
- **The step-by-step sequence of a single report's journey through ingest, queue,
  resolution, and notification.** That is a flow node's shape, not this node's -- no
  flow node for this capability exists yet in the corpus.
- **How the relay is operated day to day** (deployment, monitoring, incident
  response). That is the `operations` corpus surface, not this one.

## Relationships

Declared: none. The corpus's merged tree under `launchpad/docs/corpus/architecture/**`
(checked against `origin/launchpad`) contains no node about moderation, the relay's
event-kind dispatch, or the desktop moderation surface that this capability could
`references` without inventing a target id that resolves to nothing. The first
architecture, interface, or flow node covering moderation is the natural moment to
add a `references` edge back to this node.

## Scope and omissions

**This node covers** the member-facing report capability: what a report can target
(message, blob, or pubkey), what reason categories and optional note it carries, the
privacy guarantee that a report is never public and never visible to its subject, that
report submission requires no special authorization beyond ordinary message-write
access, and how a report's lifecycle (open to resolved/dismissed, or escalated)
connects to the moderation queue and its resolution.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay/database/desktop client are architected | the architecture corpus surface (no moderation node exists there yet) |
| The ban/timeout/kick/delete enforcement actions a resolved report can trigger | a separate moderation-enforcement capability node (not yet written) |
| The step-by-step flow of one report from submission through notification | a flow node for this capability (not yet written) |
| Day-to-day operation of the moderation queue | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **No live integration run.** This node's behavioral claims come from reading
  `report.rs`, `moderation.rs`, `ingest.rs`, `moderation_authz.rs`, and the desktop
  client, plus `report.rs`'s own unit tests -- not from submitting a real report
  against a running relay and observing the queue and resolution end to end.
- **The platform-level consumer of an escalated report** -- `VISION_MODERATION.md`
  describes escalation feeding "the platform operator's safety process," but no code
  path beyond the community audit log was located for it while drafting this node.
- **Mobile client support.** No reference to `KIND_REPORT` or an equivalent report
  submission path was found under `mobile/lib` while drafting this node; whether
  reporting is available from the Flutter mobile app was not established either way.
