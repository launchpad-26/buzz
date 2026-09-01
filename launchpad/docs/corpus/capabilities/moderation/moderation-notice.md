---
id: capabilities-moderation-moderation-notice
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "send_moderation_notice delivers a moderation notice to a recipient inside a relay-authored two-party DM channel between the relay's moderation key and that recipient, created on first use via the participant-hash-idempotent open_dm and reused on every later notice to the same user in the same community -- it is a private DM to the affected user, not a message posted into the channel where the underlying action occurred."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "ModerationNotice is an enum of exactly three variants: ReportResolved (to a reporter, carrying report_id/status/summary), ContentActioned (to an actioned author, carrying action_id/public_reason), and Restriction (to a banned or timed-out user, carrying action_id/kind/public_reason), and each variant's source_id() names the report or audit-action database row the notice was derived from."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "Only two of the three ModerationNotice variants are constructed anywhere in the codebase: handle_ban and handle_timeout in moderation_commands.rs each call send_moderation_notice with ModerationNotice::Restriction (kind \"ban\" or \"timeout\") after the restriction is applied and audited, and the report-resolution handler calls send_moderation_notice with ModerationNotice::ReportResolved after a report is resolved or dismissed; ModerationNotice::ContentActioned is defined and unit-tested but has no call site anywhere in the repository outside its own test module, so notice delivery for a standalone content-removal action (with no accompanying ban/timeout) is designed but not wired to any moderation command."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "grep across every .rs file in the repository for ModerationNotice::ContentActioned returns four matches, all inside moderation_notices.rs itself (the enum variant definition, its two match arms, and its own unit test); no other file in the repository constructs it."
    entry_class: FACT
    evidence:
      - "grep_recursive('ContentActioned', glob='**/*.rs') -> 4 matches, all in crates/buzz-relay/src/handlers/moderation_notices.rs, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The notice is stored as a relay-signed kind:9 event (KIND_STREAM_MESSAGE) tagged with h=<dm_channel_id> and a non-standard moderation_source tag naming the source report/action row's UUID; the moderation_source tag is deliberately not an e tag because e is reserved for 32-byte event ids and the source is an opaque database row id, and that tag is also the idempotency key a retry after a crash checks before sending a duplicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "Before inserting the notice event, send_moderation_notice unconditionally re-publishes the relay's own kind:0 profile named \"{community host} Moderation\" (via publish_moderation_profile, a replaceable NIP-01 event) and re-emits the DM's kind:39000 discovery event with hidden and t=dm tags on every send rather than only on first creation, and it calls unhide_dm for the recipient so a user who previously hid the moderation DM thread still sees a later notice -- the module's own comments state this closed-loop delivery requirement explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "The recipient-facing body text is built only from each notice variant's own already-sanitized fields (status, summary, and public_reason, which mirrors the tombstone's public_reason) and never includes a reporter's identity, other reporters, or raw report notes; this is stated as a module-level privacy invariant and is exercised by the unit tests report_resolved_body_reflects_status_and_never_leaks_reporter, restriction_body_distinguishes_ban_from_timeout, and content_actioned_body_carries_only_the_public_reason, all in moderation_notices.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs"
  - statement: "Notice delivery failure does not fail the moderation command itself: handle_ban, handle_timeout and the report-resolution handler each log the send_moderation_notice error and continue, because the restriction or resolution has already landed and been audited by the time the notice is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "VISION_MODERATION.md states, as part of the product's own vision for moderation, that a restricted user \"hear[s] it straight: a message from the community's moderation identity telling you what restriction was applied, why, and for how long\" and that \"everyone affected hears the truth about what happened\" -- the same private, per-user notice this node documents, described there at product-vision level rather than as an implementation."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:31"
      - "VISION_MODERATION.md:5"
  - statement: "The moderation notice DM primitive is described in the module's own doc comment as implementing 'Plan §0.3 (Tyler, 2026-07-07)', a design note not present anywhere in this repository as a citable file at the recorded revision -- its content is known only through the module's paraphrase of it, so it is not cited here as an independent source."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "crates/buzz-relay/src/handlers/moderation_notices.rs module doc comment, attributing the design to Tyler's 2026-07-07 plan note"
---

# Moderation notice: capability

Buzz gives every person a moderation action touches a direct, private explanation of
what happened and why. When a community owner or admin bans or times out a member,
or when a member's report is resolved or dismissed, the relay itself -- not a human
moderator typing a reply -- delivers a message from a recognizable "{community}
Moderation" identity into a one-to-one thread with that specific person. A banned or
timed-out user is told which restriction applies and the stated reason; a reporter is
told the outcome of their report. Nobody has to guess whether their report went
anywhere, and nobody is silently restricted with no explanation -- the relay closes
that loop automatically, every time, whether or not any human remembers to write to
the affected person by hand.

## Maturity

**Shipped, for two of its three designed notice kinds.** `send_moderation_notice` is
wired into `handle_ban` and `handle_timeout` (both send `ModerationNotice::Restriction`
after the restriction is applied and audited) and into the report-resolution handler
(which sends `ModerationNotice::ReportResolved` after a report is resolved or
dismissed). `ModerationNotice::ContentActioned` -- a notice to an actioned author
about a standalone content action -- is defined, documented, and unit-tested, but no
moderation command in the repository constructs it, so a user whose message is removed
without an accompanying ban or timeout does not currently receive a notice through this
mechanism.

## Boundary

This node does not describe:
- **How the underlying moderation actions are authorized or enforced** -- who may ban,
  time out, or act on a report, and how that authority is checked, is a separate
  concern realized in `crates/buzz-relay/src/handlers/moderation_authz.rs` and
  `moderation_commands.rs`. This node covers only the notice that follows an action,
  not the action's own authorization.
- **The audit trail moderation actions write.** `insert_audit` records the action
  itself; this node's notice is a downstream side effect of that record; it does not
  describe the audit log's own shape or retention.
- **The interface surface a moderator uses to issue a ban, timeout, or report
  resolution** -- the moderation-command event kinds and any CLI/HTTP surface over
  them are a separate capability's concern.
- **The step-by-step flow of one moderation action from submission to enforcement.**
  This node states that a notice capability exists and what it delivers; it does not
  narrate the full sequence (authorize -> enforce -> audit -> notify) as a flow node
  would.
- **How the running relay is operated or monitored.** Deployment and operations
  concerns for the relay generally are out of scope here.
- **Whether the notice is publicly visible in the channel where the action occurred.**
  It is not: the notice is a private DM to the affected individual only, delivered in
  a dedicated relay-authored thread, never posted into the original channel as a
  visible system message.

## Relationships

None declared. `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
at the recorded revision holds no `capabilities/` node yet (this is the first), and no
architecture node specifically documenting the moderation-command or moderation-authz
flow exists among the merged `architecture/flows/*` or `architecture/containers/*`
nodes to `references`. The natural edges -- `references` toward a future
moderation-command capability/interface node and toward a future
moderation-authorization node -- are left for whichever of those merges first, per
`AGENTS.md`'s rule that a relationship target must already resolve on the branch being
merged into.

## Scope and omissions

**This node covers** what the moderation-notice capability delivers (a private,
per-recipient DM from a relay-authored moderation identity), which moderation events
trigger it today (ban, timeout, report resolution/dismissal), which designed notice
kind is not yet wired to any caller (content-actioned), the delivery mechanics that
make it idempotent and resilient to a user hiding the thread, and the privacy
invariant its body text honors.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Authorization for moderation actions (who may ban/time out/resolve a report) | a future moderation-authorization node, over `crates/buzz-relay/src/handlers/moderation_authz.rs` |
| The moderation-command interface/event surface | a future moderation-command capability/interface node, over `crates/buzz-relay/src/handlers/moderation_commands.rs` |
| The audit log moderation actions write | not yet documented in this corpus |
| The step-by-step flow from report/command to enforcement and notice | a future flow node, not yet drafted |
| How the relay is deployed and operated | the `operations`/`architecture` corpus surfaces |

**Expected but not verified when this node was written:**
- **Whether `ModerationNotice::ContentActioned` is planned for a near-term caller or
  is dead code.** No issue or PR describing that intent was located while drafting
  this node; the Maturity section states only what the code does today.
- **The "Plan §0.3 (Tyler, 2026-07-07)" design note the module's doc comment
  references.** It was not found as a file in this repository at the recorded
  revision, so its content beyond the module's own paraphrase is unverified here.
- **Whether a v2 appeal-routing reply path (mentioned in the module's own doc
  comment as future work) has since been designed or built.** Not investigated for
  this node; the module's comments describe the current thread as "non-replyable in
  v1".
