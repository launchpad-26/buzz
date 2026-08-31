---
id: capabilities-moderation-moderation-authorization
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "authorize_moderation_action in crates/buzz-relay/src/handlers/moderation_authz.rs is the one authorization seam for every ModerationAction variant (DeleteMessage, Kick, Ban, Unban, Timeout, Untimeout, ResolveReport, ViewQueue), and its own module doc states that routing every decision through it is deliberate so a future Moderator tier is a policy change, not a rewrite."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-47"
  - statement: "The pure decide_authority function grants a community owner every ModerationAction with no guard rail, grants a community admin every action except it rejects Ban/Timeout when the target's own community role is owner or admin, grants a channel owner/admin only DeleteMessage and Kick within their channel, and denies a plain member or a stranger every action."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:146-181"
  - statement: "Seven unit tests in moderation_authz.rs's own tests module exercise exactly this grid: an owner authorized for every action, an admin authorized against non-privileged targets, an admin blocked from banning or timing out an owner or fellow admin, an admin still able to ban/timeout a non-member or plain-member target, the guard rail confirmed scoped to only Ban/Timeout, a channel owner/admin authorized for only DeleteMessage/Kick, and a plain channel member or stranger denied every action."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:183-335"
  - statement: "authorize_moderation_action resolves actor and target community roles from relay_members, whose primary key is (community_id, pubkey) and whose every read is bound to a single community_id, so community-wide moderation authority cannot cross a tenant boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs:1-7"
      - "crates/buzz-db/src/relay_members.rs:68-90"
  - statement: "The kind:9040-9044 community moderation commands (Ban, Unban, Timeout, Untimeout, ResolveReport) each call authorize_moderation_action before executing their side effect, per moderation_commands.rs's own module-doc table and its five call sites."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:1-16"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:156"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:235"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:274"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:338"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:399"
  - statement: "The HTTP bridge's authorize_moderation_read helper gates every moderation-queue and audit-log GET route on NIP-98 signed auth plus a ViewQueue call to authorize_moderation_action, denying with 403 'restricted: moderator access required' on failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2131-2188"
  - statement: "The kind:9001 (remove user/kick) and kind:9005 (delete event) NIP-29 handlers in side_effects.rs authorize purely from channel-local membership and role (or, for 9005, event self-authorship), and neither calls authorize_moderation_action, so a community owner/admin who is not already a member of the target channel cannot yet kick or delete a message through these two kinds -- moderation_authz.rs's own module doc names this exact gap, calling itself 'the bridge validate_admin_event is missing today.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:452-495"
      - "crates/buzz-relay/src/handlers/side_effects.rs:634-719"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:1-8"
  - statement: "A kind:9044 resolution carrying action=delete, kick, or ban only authorizes and records the moderator's ResolveReport decision; moderation_commands.rs's own module doc and an inline comment state that the actual enforcement event (the 9005/9001/9040 write) is composed and authorized separately by the client, rather than executed automatically by the resolve handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:9-16"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:440-457"
  - statement: "Root VISION_MODERATION.md states that community moderation gives 'community owners and admins the full loop,' that 'the relay enforces' while 'the community provides the judgment,' and separately that there are 'two roles, not three' today -- owners and admins moderate, with no volunteer-moderator tier -- because 'authority is structured as capabilities, so adding a moderator tier later is a policy change, not a rewrite.'"
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:5"
      - "VISION_MODERATION.md:57"
  - statement: "This capability is shipped rather than merely designed, because its authorization seam is exercised by seven passing unit tests, wired into five live command handlers (kinds 9040-9044), and wired into the HTTP moderation-queue/audit read path, all at the repository revision this node cites."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs:183-335"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs:156"
      - "crates/buzz-relay/src/api/bridge.rs:2171-2185"
    confidence: 0.85
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: implements
    target: corpus-template-capability
---

# Moderation authorization: capability

Buzz community owners and admins can moderate their own community -- delete a
message, kick or ban a member, time a member's writes out, resolve or dismiss a
report, and view the moderation queue and audit log -- and every one of those
decisions is authorized through a single seam,
`authorize_moderation_action`/`decide_authority`, rather than scattered inline role
checks. A community `owner` holds every capability community-wide with no guard
rail; a community `admin` holds every capability too, but cannot ban or time out
the owner or a fellow admin -- only the owner may action an admin. A channel
`owner`/`admin` keeps a narrower, channel-local authority: they may delete a
message or kick a member within their own channel, but hold no community-wide
capability. A plain member or an unauthenticated stranger holds none of this. All
of it stays fenced to one community: role lookups are keyed to
`(community_id, pubkey)`, so authority granted in one community never reaches
another.

## Authorization rules

- **Community owner.** Authorized for every `ModerationAction` (delete, kick, ban,
  unban, timeout, untimeout, resolve report, view queue), community-wide, against
  any target, with no guard rail.
- **Community admin.** Authorized for every `ModerationAction` community-wide,
  *except* it is rejected for `Ban`/`Timeout` when the target's own community role
  is `owner` or `admin` -- only the owner may apply that restriction to another
  privileged actor. The guard trips on a privileged target *role*, not on a
  missing `relay_members` row, so a drive-by target who already left is still
  bannable, and the guard is scoped to *applying* a restriction: `Unban`/
  `Untimeout` and every non-restriction action remain allowed against an admin
  target.
- **Channel owner/admin.** Authorized for `DeleteMessage` and `Kick` only, and
  only within the channel they hold that role in. They hold no community-wide
  capability (`Ban`, `Timeout`, `Unban`, `Untimeout`, `ResolveReport`, `ViewQueue`
  are all denied at this role).
- **Plain member / stranger.** Denied every `ModerationAction`.
- **Tenant invariant.** Every role lookup this seam performs is scoped to a single
  `community_id`; moderation authority granted in one community confers nothing
  in another.

**Where this seam is actually exercised today** (a maturity boundary, not a
description of intent):

- The kind:9040-9044 direct commands (ban, unban, timeout, untimeout, resolve
  report) each call this seam before acting, so a community owner/admin exercises
  full community-wide authority through them today.
- The relay's HTTP moderation-queue and audit-log reads call this seam with
  `ViewQueue`, gated behind NIP-98 signed auth.
- The kind:9001 (remove user) and kind:9005 (delete event) NIP-29 handlers --
  the same actions this seam models as `Kick` and `DeleteMessage` -- do **not**
  yet call this seam. They authorize purely from channel-local membership and
  role (or, for a 9005 self-delete, event authorship), so a community owner/admin
  who is not already a member of the target channel cannot currently kick or
  delete a message through these two kinds. This is a known, named gap: the
  authorization module's own doc comment calls itself "the bridge
  `validate_admin_event` is missing today." A kind:9044 resolution with
  `action=delete`/`kick`/`ban` only authorizes and records the moderator's
  *decision*; the client composes and separately authorizes the actual
  enforcement event.

## Maturity

**Shipped**, for the seam itself and the surfaces that already call it (the
9040-9044 command family and the HTTP moderation-read routes): the policy
function is exhaustively unit-tested and is live in production code paths at the
cited revision. **Not yet extended** to the kind:9001/9005 NIP-29 paths, per the
named gap above -- that remains channel-local-only authority today, independent
of any community-wide role the actor may hold.

## Boundary

This node does not describe:
- **How the capability is built.** `authorize_moderation_action`'s callers, the
  Postgres schema behind `relay_members`/`channel_members`, and the surrounding
  relay process are the `architecture-containers-relay` node's territory, not
  restated here.
- **The interface(s) this capability is exposed through.** The kind:9040-9044
  Nostr event contract (`buzz-relay`), the moderation HTTP read routes
  (`buzz-relay`'s bridge), and the `buzz-cli moderation` command group each
  expose this capability; no interface-shaped corpus node exists yet to
  `references`, so they are cited here as evidence rather than as a
  relationship.
- **The step-by-step flow through moderation** (a member reports, a queue fills,
  an admin acts, notices go out). That is a flow node's territory, not yet
  drafted in this corpus.
- **How the running relay is operated** (deployment, monitoring, incident
  response for moderation infrastructure). That is the `operations` surface.

## Relationships

- `references`: `architecture-containers-relay` -- the container this
  authorization seam runs inside.
- `references`: `architecture-principles-community-is-security-boundary` -- the
  tenant-fence principle this capability's role lookups enforce structurally.
- `implements`: `corpus-template-capability` -- this node follows that
  template's shape.

## Scope and omissions

**This node covers** who may exercise which moderation capability in a Buzz
community (owner/admin/channel-role/member authority for delete, kick, ban,
unban, timeout, untimeout, resolve-report and view-queue), the guard rail
protecting a privileged target, the tenant fence the role lookups enforce, and
which real call sites already route through this authorization seam versus which
NIP-29 kinds still authorize channel-locally only.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, its database, and its process topology are built | `architecture-containers-relay` |
| The kind:9040-9044 event/tag contract and the CLI/HTTP surfaces exposing this capability | no interface corpus node exists yet |
| The step-by-step report -> queue -> action -> notice flow | no flow corpus node exists yet |
| How the running relay is deployed and operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- Whether closing the kind:9001/9005 gap (routing them through
  `authorize_moderation_action` too) is already tracked by an open issue was not
  checked; this node names the gap from the code and the authorization module's
  own doc comment, not from an issue search.
- `moderation_notices.rs` (the notice-DM side effect) and `buzz-db`'s
  `moderation.rs`/`admin_moderation.rs` (report/action storage) were not opened
  in detail -- this node's evidence is scoped to the authorization decision
  itself, not the storage or notification side effects a granted action then
  triggers.
