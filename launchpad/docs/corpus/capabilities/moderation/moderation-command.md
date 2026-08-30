---
id: capabilities-moderation-moderation-command
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "VISION_MODERATION.md describes an owner/admin acting on a report 'in one motion: dismiss, delete the message, kick, timeout, ban, or escalate,' and states that a Buzz community's moderation actions are 'a cryptographically signed event, validated against their actual role and executed -- never stored as content.'"
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md"
  - statement: "buzz-cli exposes a `buzz moderation` command group (`ModerationCmd` in `crates/buzz-cli/src/lib.rs`) with eight subcommands: `ban`, `unban`, `timeout`, `untimeout`, `resolve`, `reports`, `restricted`, `audit`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-cli/src/commands/moderation.rs"
  - statement: "The five mutating subcommands (`ban`, `unban`, `timeout`, `untimeout`, `resolve`) each build a signed event via a dedicated `buzz_sdk::build_moderation_*` constructor and submit it through `POST /events`, the same path the WebSocket transport uses; the three read subcommands (`reports`, `restricted`, `audit`) instead call NIP-98-authed, moderator-only relay endpoints under `/moderation/*` (`/moderation/reports`, `/moderation/restricted`, `/moderation/audit`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "`buzz-core/src/kind.rs` defines five moderation-command kinds -- `KIND_MODERATION_BAN` (9040), `KIND_MODERATION_UNBAN` (9041), `KIND_MODERATION_TIMEOUT` (9042), `KIND_MODERATION_UNTIMEOUT` (9043), `KIND_MODERATION_RESOLVE_REPORT` (9044) -- plus a canonical `is_moderation_command_kind` range check, and its own comment states these kinds are 'direct commands (executed, never stored)', mirroring the NIP-43 relay-admin 9030-series."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "`crates/buzz-relay/src/handlers/moderation_commands.rs`'s `handle_moderation_command` is the single entry point for kinds 9040-9044: before any command-specific handler runs, it rejects an actor who is themself currently banned in the tenant (`ensure_actor_not_banned`) and rejects a command whose `created_at` is more than 120 seconds (`MAX_COMMAND_SKEW_SECS`) from the relay's clock, because these commands are never stored and a captured, replayed command is the threat that freshness check exists to stop."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "Every one of the five command kinds routes through one authorization seam, `moderation_authz::authorize_moderation_action` / its pure decision function `decide_authority`, rather than an inline role check per handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "`decide_authority` grants a community `owner` every moderation action with no guard rail, grants a community `admin` every action except that it refuses `Ban`/`Timeout` when the target's own community role is `owner` or `admin` ('an admin cannot ban or time out a community owner or fellow admin' -- only the owner may act on an admin), and leaves `Unban`/`Untimeout` unguarded at this same seam, deliberately, because an already-banned actor is separately blocked at every transport by `ensure_actor_not_banned`. A community non-owner/admin instead keeps channel-local `DeleteMessage`/`Kick` authority only when they hold `owner`/`admin` role on that channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "This authorization policy is exhaustively unit-tested as pure logic, decoupled from I/O: `community_owner_authorized_for_everything` asserts the owner has no guard rail even against an admin target, and `community_admin_authorized_against_non_privileged_targets` asserts the admin path, in `crates/buzz-relay/src/handlers/moderation_authz.rs`'s own `#[cfg(test)]` module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "A ban (kind 9040) is enforced immediately at the identity/session seam, not only as a database flag: `handle_ban` calls `state.disconnect_pubkey_clusterwide`, which closes the banned pubkey's open sessions on the local pod synchronously and fans the disconnect out to every other pod, before any notice DM is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "A timeout (kind 9042) is a distinct restriction from a ban: `moderation_commands.rs`'s own `banned_admin_cannot_reach_an_unban_command` test asserts `ensure_actor_not_banned` blocks a banned actor but passes a merely timed-out actor through, and `buzz-db`'s `RestrictionState` (`banned: bool`, `muted_until: Option<DateTime<Utc>>`) models the two as separate fields rather than one restricted flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-db/src/moderation.rs"
  - statement: "Resolving a report (kind 9044) re-validates the tag vocabulary the SDK already validated at build time -- `status` must be `resolved` or `dismissed`, `action` must be one of `delete`/`kick`/`ban`/`timeout`/`dismiss`/`escalate`, and `dismiss` may only pair with `dismissed` -- because, per the handler's own comment, 'the relay must not trust the client.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "A 9044 resolution records the moderator's *decision* as a `resolve:`-prefixed audit row (via `resolution_audit_action`, e.g. `resolve:ban`, `resolve:timeout`) distinct from the *enforcement* row the paired 9040/9042 command (or the existing kind:9005 delete / kind:9001 kick paths) writes when the client separately composes it; `dismiss` audits as `dismiss_report` and `escalate` audits unprefixed as `escalate` so it stays queryable for the platform-safety lane. The unit test `resolve_audit_actions_are_allowed_by_db_check_vocabulary` pins every mapped value against `buzz_db::moderation::MODERATION_ACTION_CHECK_VOCAB`, the same vocabulary `migrations/0006_moderation.sql`'s CHECK constraint enforces at the database."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-db/src/moderation.rs"
      - "migrations/0006_moderation.sql"
  - statement: "`buzz-core::kind::KIND_NIP29_REMOVE_USER` (9001, kick) and `buzz-core::kind::KIND_NIP29_DELETE_EVENT` (9005, delete message) are the existing NIP-29 kinds a `delete`/`kick` report resolution fans out through, per `moderation_commands.rs`'s own module doc comment -- confirming the resolve-report action vocabulary is not a second implementation of message deletion or channel removal."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "Every accepted moderation command writes a durable audit row through `buzz_db::moderation::insert_action` (table backed by `migrations/0006_moderation.sql`), which `buzz moderation audit` reads back via the `/moderation/audit` endpoint -- giving an operator a queryable ledger of who did what to whom and why, independent of the notice DMs sent to affected users."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-db/src/moderation.rs"
      - "migrations/0006_moderation.sql"
  - statement: "Notice delivery -- the DM telling a banned/timed-out member the terms of their restriction, and the DM telling a reporter their report was resolved -- is best-effort and does not block or unwind the enforcement already committed: both `handle_ban` and `handle_resolve` log a delivery failure via `send_moderation_notice` and continue, rather than returning an error, matching VISION_MODERATION.md's own 'Notices are best-effort ... a ban lands even if the notice fails' statement."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "VISION_MODERATION.md"
  - statement: "VISION_MODERATION.md's own 'Honest Edges' section states 'Escalation is a hook today, not a pipeline' -- escalating a report writes a durable, queryable record (the unprefixed `escalate` audit action), but no platform-operator inbox that consumes it exists yet in this repository."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md"
  - statement: "`architecture-containers-cli` and `architecture-containers-relay` are corpus nodes already merged to `origin/launchpad`, documenting the `buzz-cli` and relay containers this capability's command surface and its handlers respectively live in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree contains no node of type `capabilities`, no node of type `interfaces-events`, and no `flow`-shaped node under `architecture/flows/` documenting this command surface or a moderation interaction, so this node declares no `references` toward an interface or flow node -- there is none to point at yet, not merely a choice to omit one."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> capabilities/, interfaces-events/ and a moderation-related architecture/flows/ node are all absent; only architecture/{containers,context,deployment,flows,principles}, standards/, templates/, AGENTS.md and README.md are present, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #783's Definition of Done requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/relevant variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- the capability-shaped DoD tail, not the flow-shaped tail (sequence/diagram/outcome) some sibling capability-typed issues carry."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#783 definition of done"
relationships:
  - type: references
    target: architecture-containers-cli
  - type: references
    target: architecture-containers-relay
---

# Moderation command: capability

Buzz gives a community's owners and admins a signed, directly-executed command
surface for enforcing their own rules: ban or unban a member, time out or clear a
member's timeout, and resolve or dismiss an open report — one motion each, from the
`buzz moderation` CLI command group or any client that composes the same signed
events. A command takes effect immediately (a ban disconnects the target
cluster-wide; a timeout blocks their writes) and is never stored as a public event —
only its outcome is, as a durable audit row and (best-effort) a notice DM to whoever
is affected. This is the enforcement half of Buzz's moderation loop: a member's
report is the input, and this capability is how a human decision on that report (or
a direct disciplinary action) becomes real.

## Maturity

**Shipped**, for community-level enforcement. Every one of the five command kinds
(9040 ban, 9041 unban, 9042 timeout, 9043 untimeout, 9044 resolve-report) has: a kind
constant and a routing helper in `crates/buzz-core/src/kind.rs`; a relay handler in
`crates/buzz-relay/src/handlers/moderation_commands.rs` wired through the shared
authorization seam in `moderation_authz.rs`; a `buzz-cli` subcommand in
`crates/buzz-cli/src/commands/moderation.rs`; a database migration
(`migrations/0006_moderation.sql`) backing its audit and restriction state; and unit
tests exercising both the enforcement path and the owner/admin guard rail. Nothing in
that chain is stubbed or `TODO`-marked at the recorded revision.

What is *not* shipped, per VISION_MODERATION.md's own "Honest Edges" section: a
volunteer-moderator authority tier (only owner/admin exist today — "a policy change,
not a rewrite" when it lands), a platform-operator inbox consuming escalated reports
(escalation writes a durable record only), and any pre-send content filtering
("No automod").

## Behavioral rules

- **Authority is community-scoped and role-based, not per-command.** A community
  `owner` holds every moderation action with no guard rail. A community `admin`
  holds every action too, except that `Ban`/`Timeout` is refused when the *target's*
  own role is `owner` or `admin` — only the owner may act on an admin.
  `Unban`/`Untimeout` are deliberately left unguarded at this seam, because a banned
  actor is already blocked from reaching any moderation command at all. A member who
  is neither a community owner/admin nor a channel owner/admin holds none of these
  actions; a channel owner/admin retains only channel-local delete/kick.
- **A banned actor cannot issue any moderation command.** `handle_moderation_command`
  checks the actor's own restriction state before dispatching to any of the five
  handlers, on every transport (WebSocket or NIP-98 HTTP) — a ban is an admission
  boundary, not only a role check.
- **Commands must be fresh.** A command's `created_at` must be within ±120 seconds of
  the relay's clock, because these events are validated and executed directly and
  never stored — freshness is the defense against a captured command being replayed.
- **Ban and timeout are different restrictions.** A ban disconnects the target
  cluster-wide, immediately, at the identity/session seam, and blocks
  re-authentication. A timeout is a write-block only — the member stays connected and
  can still read. `unban`/`untimeout` reverse the respective restriction; enforcement
  is symmetric (each pairs with its own SQL upsert/clear and its own audit action).
- **A resolve-report decision and its enforcement are recorded separately.**
  Resolving with `action=ban` (for example) writes a `resolve:ban` audit row for the
  *decision*; the client's separately-composed 9040 ban then writes its own
  unprefixed `ban` audit row for the *enforcement*. `dismiss` and `escalate` are
  audited unprefixed, so both stay queryable in their own right — escalate
  particularly, since it is the record a future platform-safety inbox will consume.
- **Notices are best-effort and never block enforcement.** A ban, timeout, or report
  resolution lands and is audited before any notice DM is attempted; a DM delivery
  failure is logged and does not undo or delay the already-committed action.
- **Reports remain private structural state**, not public events — this capability
  acts *on* a report (by its signed kind:1984 event id), but the report queue and
  audit trail are read only through moderator-only, NIP-98-authed endpoints, never
  through a public relay filter.

## Boundary

This node does not describe:

- **How the CLI and relay containers are built.** `architecture-containers-cli` and
  `architecture-containers-relay` (referenced below) own the component-level detail
  of those containers; this node cites their handlers and modules as evidence of the
  capability's existence, not as its own subject matter.
- **The interface contract this capability is exposed through** — the exact
  `buzz-cli` flag/argument shape and the `/moderation/*` HTTP route group. No
  `interfaces-events`-typed corpus node exists yet at the recorded revision to
  `references`; this is a gap, not a choice (see *Scope and omissions*).
- **The step-by-step flow of one moderation interaction** (e.g. a member reports,
  an admin opens the queue, resolves with `action=ban`, the target is disconnected
  and notified). No moderation `flow`-typed node exists yet under
  `architecture/flows/` at the recorded revision; this is also a gap, not a choice.
- **How the running relay is operated** (deployment, monitoring, incident response
  for the moderation subsystem specifically) — that is the `operations` corpus
  surface's territory, not this capability's.
- **The report-filing capability itself** (kind:1984, NIP-56, the member-facing
  "Report" action) or **platform-level safety escalation handling** beyond the
  `escalate` audit hook — both are named in VISION_MODERATION.md as separate lanes
  from the command surface this node documents.

## Relationships

- `references`: `architecture-containers-cli` — the container hosting the
  `buzz moderation` command group.
- `references`: `architecture-containers-relay` — the container hosting the
  command handlers, authorization seam, and audit persistence.

No `references` toward an interface or flow node: none of type `interfaces-events`
or a moderation-shaped `flow` exists in `origin/launchpad`'s corpus tree at the
recorded revision (verified by enumeration, not assumed — see the evidence ledger).
No `capabilities`-typed node is merged either, so no `part-of` broader-capability
edge is declared. The first interface, flow, or sibling capability node that merges
is the moment to add the corresponding edge here.

## Scope and omissions

**This node covers** the moderation-command capability: what a community owner or
admin can do (ban, unban, timeout, untimeout, resolve/dismiss a report), the
authority model and its guard rail, the freshness and never-stored contract for
these commands, how ban differs from timeout, how a resolve-report decision is
recorded distinctly from its enforcement, the audit and best-effort-notice behavior,
and the capability's current maturity and honest edges per VISION_MODERATION.md.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the CLI and relay containers implementing this capability are built | `architecture-containers-cli`, `architecture-containers-relay` |
| The CLI flag/argument and HTTP route-group contract this capability is exposed through | an `interfaces-events`-typed node, not yet drafted |
| The step-by-step sequence of one moderation interaction (report → queue → resolve → enforce → notify) | a `flow`-typed node, not yet drafted |
| How the running relay/moderation subsystem is operated | the `operations` corpus surface |
| The member-facing report-filing capability (kind:1984, NIP-56) | a separate capability node, not this one |
| Platform-level safety escalation handling beyond the `escalate` audit hook | a separate node once that pipeline is built (per VISION_MODERATION.md's "Honest Edges") |

**Expected but not verified when this node was written:**

- **No end-to-end (live relay + Postgres) test run was executed for this capability
  while drafting this node.** The unit tests cited in the evidence ledger cover the
  authorization decision and the audit-vocabulary mapping as pure logic; they do not
  exercise a real `POST /events` round trip against a running relay. The nearest
  relay-admin regression test (`crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs`)
  covers the 9030-series relay-admin kinds, not 9040-9044, and was read only to
  confirm it is a different kind range, not cited as verification of this capability.
- **The `/moderation/reports`, `/moderation/restricted`, and `/moderation/audit`
  HTTP endpoint handlers themselves were not opened** — only the CLI call sites that
  target them (`crates/buzz-cli/src/commands/moderation.rs`). Their NIP-98
  authorization and response shape are therefore not independently confirmed here.
- **`buzz-db/src/moderation.rs`'s `ban_member`/`unban_member`/`timeout_member`/
  `untimeout_member`/`resolve_report` implementations were not read in full** — only
  their signatures and the `MODERATION_ACTION_CHECK_VOCAB` constant, cited above.
