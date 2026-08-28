---
id: layers-authorization-moderation-authorization
type: layers
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
  - statement: "authorize_moderation_action in crates/buzz-relay/src/handlers/moderation_authz.rs is documented as the single capability seam for every moderation authorization decision, and all of its callers route through it rather than checking roles inline."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "authorize_moderation_action resolves the actor's community role from relay_members via buzz_db::relay_members::get_relay_member, scoped to tenant.community(), and delegates the actual authorization decision to the pure, exhaustively unit-tested function decide_authority."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "A community owner (relay_members.role = 'owner') is authorized for every ModerationAction unconditionally, with no guard rail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "A community admin is authorized for every ModerationAction except Ban and Timeout directed at a target whose own community role is owner or admin; that specific combination returns an anyhow::bail! error from decide_authority."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "Unban, Untimeout, ResolveReport and ViewQueue are unguarded at this authorization seam for a community admin, even when the target's community role is owner or admin -- only Ban and Timeout trip the guard rail, because it protects against applying a restriction, not lifting one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "An actor holding no community owner/admin role is authorized only for DeleteMessage and Kick, and only when they hold the channel-level owner or admin role for the given channel_id, resolved via buzz_db::channel::get_member_role; every other actor/action combination is denied."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-db/src/channel.rs"
  - statement: "Community role is stored in relay_members.role, a TEXT column constrained by CHECK (role IN ('owner', 'admin', 'member')). Channel role is stored in channel_members.role, a Postgres ENUM type member_role with five values ('owner', 'admin', 'member', 'guest', 'bot'), of which decide_authority only ever matches 'owner' and 'admin'."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Every moderation authorization decision in the relay routes through authorize_moderation_action from exactly two call sites: four invocations in moderation_commands.rs guarding the kind 9040-9044 ban/unban/timeout/untimeout/resolve-report commands, and one invocation in bridge.rs guarding the HTTP moderation-queue read with ModerationAction::ViewQueue."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "The unit test admin_cannot_ban_or_timeout_owner_or_fellow_admin asserts decide_authority errors when a community admin actor targets an owner or admin with Ban or Timeout, and the unit test admin_can_ban_or_timeout_a_non_member_target asserts the same call succeeds when the target's community role is None or 'member'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "There is no Moderator role tier in this v1 authorization model -- authority is granted only via the community owner/admin role, or, narrowly, the channel owner/admin role -- but the module's doc comment states that factoring all authorization through authorize_moderation_action makes adding a Moderator tier later a policy change inside decide_authority rather than a rewrite of its callers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "This node declares no relationships because launchpad/docs/corpus/layers/ carries no other node on origin/launchpad at the time this node was authored, so no relationships[].target could resolve."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1037 task brief, cross-checked by listing launchpad/docs/corpus/layers/** on origin/launchpad"
---

# Moderation authorization

**Moderation authorization** is the decision of whether a given actor may perform a
given moderation action (deleting a message, kicking or banning a user, timing out a
user, or managing the report queue) against a given target, within a channel or
community. In Buzz it is answered by exactly one function,
[`authorize_moderation_action`](../../../../../crates/buzz-relay/src/handlers/moderation_authz.rs),
and nowhere else.

## Boundaries / non-goals

This node covers **authorization only** — who may act. It does not cover:

- **Side effects of a moderation command** (audit rows, notice DMs, live
  disconnects, `community_bans`/`muted_until` upserts). Those are
  `moderation_commands.rs`'s and `moderation_notices.rs`'s concern, downstream of an
  authorization decision this node describes.
- **Ordinary channel membership gating** for reads and writes that are not
  moderation actions (joining, posting, viewing). That is a separate authorization
  concern with its own code paths.
- **The report-resolution audit vocabulary** (`resolve:*` prefixed action strings,
  `dismiss_report`, `escalate`). Those are an auditing/workflow detail of
  `moderation_commands.rs`'s handling of kind 9044, not part of the authorization
  decision itself.
- **Whether or when a Moderator role tier is added.** The module documents that as
  a possible future policy change (see evidence ledger), not a decision this node
  makes or predicts.

## Decision model

`authorize_moderation_action` takes the tenant, the actor's pubkey, an optional
`channel_id`, a `ModerationTarget` (an event, a pubkey, or none), and a
`ModerationAction`. It resolves roles via two database reads — the actor's
community role from `relay_members`, and, for the admin guard rail only, the
target's community role — then calls the pure function `decide_authority`, which
returns one of three `ModerationAuthority` outcomes or an error:

| Actor's community role | Action | Target's community role | Result |
|---|---|---|---|
| `owner` | any of the 8 `ModerationAction` variants | any | `ModerationAuthority::CommunityOwner` — always authorized |
| `admin` | `Ban` or `Timeout` | `owner` or `admin` | denied — admin guard rail |
| `admin` | `Ban` or `Timeout` | anything else (`member`, no row) | `ModerationAuthority::CommunityAdmin` |
| `admin` | `Unban`, `Untimeout`, `ResolveReport`, `ViewQueue`, `DeleteMessage`, `Kick` | any | `ModerationAuthority::CommunityAdmin` — unguarded |
| none (not owner/admin) | `DeleteMessage` or `Kick` | — (channel role checked instead) | `ModerationAuthority::ChannelRole` if the actor holds channel `owner`/`admin` in `channel_id`; denied otherwise |
| none | any other action | — | denied — "moderator access required" |

The guard rail on `admin` exists specifically to stop an admin from *applying* a
restriction (`Ban`, `Timeout`) to the community owner or a fellow admin; reversing
one (`Unban`, `Untimeout`) is intentionally left open, and so are the
report-queue and channel-local actions.

Community authority, once it applies, always takes precedence over channel-level
authority: a community owner/admin's channel role is never consulted (`decide_authority`
only reaches the channel-role branch when the actor holds no community owner/admin
role at all).

## Where roles are stored

Community role — `relay_members.role` — is a `TEXT` column with
`CHECK (role IN ('owner', 'admin', 'member'))`. Channel role — `channel_members.role`
— is a Postgres `ENUM` type `member_role` with five values (`owner`, `admin`,
`member`, `guest`, `bot`); `decide_authority` only ever matches `owner`/`admin` out
of that wider set, so `guest` and `bot` channel roles carry no moderation authority
at this seam.

## Worked example

From `moderation_authz.rs`'s own test suite: a community admin acting on a *plain
member* target is authorized for `Ban` (test
`admin_can_ban_or_timeout_a_non_member_target`), but the identical call against a
target whose community role is `admin` is denied (test
`admin_cannot_ban_or_timeout_owner_or_fellow_admin`). The only variable between the
two outcomes is the target's stored community role — the actor, the action, and the
absence of a channel role are unchanged. This is the guard rail in the decision
model table above, exercised directly.

## Callers

Every moderation authorization check in the relay goes through
`authorize_moderation_action` from exactly two source files:

- [`crates/buzz-relay/src/handlers/moderation_commands.rs`](../../../../../crates/buzz-relay/src/handlers/moderation_commands.rs)
  — four call sites, one each guarding the kind 9040 (ban), 9041 (unban), 9042
  (timeout)/9043 (untimeout), and 9044 (resolve report) command handlers.
- [`crates/buzz-relay/src/api/bridge.rs`](../../../../../crates/buzz-relay/src/api/bridge.rs)
  — one call site, gating the HTTP moderation-queue read with
  `ModerationAction::ViewQueue`.

No other code path performs an inline role check for a moderation action; the
module doc comment states this is deliberate, so that adding a Moderator role tier
later is a change to `decide_authority`'s policy, not a rewrite of every caller.

## Relationships

None. At the revision this node was authored, `launchpad/docs/corpus/layers/`
contains no other node — this is the first — so no `relationships[].target` could
resolve to an existing id. This is stated explicitly rather than left silent,
per `launchpad/docs/corpus/AGENTS.md`'s guidance that "there was nothing to point
at" stops being true the moment a sibling node merges.

## Scope and omissions

**Not covered here, and out of scope for this node:** the side effects a moderation
command performs once authorized (audit logging, notices, live disconnects), the
report-resolution audit-string vocabulary, ordinary (non-moderation) channel
membership gating, and any future Moderator role tier.

**Expected but not independently verified:** the runtime behavior of
`get_relay_member` and `get_member_role` under concurrent role changes (e.g. a role
demotion racing an in-flight moderation command) was not exercised — only the pure
`decide_authority` function's logic, which is unit-tested directly, and the two
database read functions' query text, which was read but not run against live data
for this node.
