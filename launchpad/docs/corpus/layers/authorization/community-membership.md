---
id: layers-authorization-community-membership
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
  - statement: "buzz-core defines a `MemberRole` enum (Owner, Admin, Member, Guest, Bot) with a documented linear hierarchy Owner > Admin > Member > Guest, a `permission_level()` numeric mapping, and a `has_at_least(required)` comparison used for authorization checks; Bot is explicitly excluded from the hierarchy and never satisfies any requirement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "The `channel_members` table's role column is typed as the Postgres enum `member_role` with values `owner, admin, member, guest, bot` (five values, matching buzz-core's `MemberRole`), while the separate `relay_members` table's role column is a plain `TEXT` column constrained by `CHECK (role IN ('owner', 'admin', 'member'))` (three values, a subset of the same vocabulary)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`crates/buzz-relay/src/api/mod.rs`'s `relay_members` module (`check_relay_membership`, `enforce_relay_membership`) is documented as 'Relay membership enforcement — single gate for all authenticated entry points,' answering whether a pubkey is admitted to the community at all; it is the tenancy-side gate, not the subject of this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "`authorize_moderation_action` in `crates/buzz-relay/src/handlers/moderation_authz.rs` is documented as the single capability seam for every moderation decision: community `owner`/`admin` (read from tenant-scoped `relay_members`) are authorized for every `ModerationAction` in any channel of their community, while channel owner/admin hold only `DeleteMessage`/`Kick` within their own channel, and plain members hold none of the eight defined moderation actions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "`decide_authority` (the pure policy function behind `authorize_moderation_action`) denies a community admin from applying `Ban` or `Timeout` against a target whose own community role is `owner` or `admin`; only the owner may action an admin, and this guard is scoped to applying a restriction, not lifting one (`Unban`/`Untimeout` are unguarded at this seam)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "`handle_ban` in `crates/buzz-relay/src/handlers/moderation_commands.rs` calls `authorize_moderation_action(..., ModerationAction::Ban)` and maps a denial to a client-safe error via `authz_denial` before any call to `state.db.ban_community_member`, so the authorization check runs before the side effect, not after it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "`buzz_core::git_perms::default_min_role(ref_name, kind)` maps a git ref update (branch/tag, create/fast-forward/non-fast-forward/delete) to a minimum required `MemberRole`, and `evaluate_ref_update` denies the update with a `Denial` unless `role.has_at_least(min_role)`; an explicit `push:role` protection tag may only raise this floor, never lower it, per the function's own comment ('Explicit push:role can NEVER weaken the built-in default')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "`crates/buzz-relay/src/api/git/policy.rs` calls `buzz_core::git_perms::evaluate_push()` as a documented step in its own git-push policy pipeline, wiring the `MemberRole`-based git authorization check into the real git-over-HTTP push path rather than leaving it an unused library function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "`get_member_role` and `is_member` in `crates/buzz-db/src/channel.rs` read a pubkey's channel-scoped role (or membership) from `channel_members`, scoped by `community_id`, `channel_id` and `pubkey`, and excluding rows where `removed_at IS NOT NULL` — a channel-local, not community-wide, membership/role read."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs"
  - statement: "`AGENTS.md` states that one corpus node is one independently maintainable idea, and that a second concept, contract or procedure discovered while writing is filed as its own task and linked, not folded in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Community membership admission (whether a pubkey is in `relay_members`/`channel_members` at all, enforced by `check_relay_membership`/`enforce_relay_membership`) and community-member authorization (what a member with a given role may do, decided by `authorize_moderation_action` and `git_perms::evaluate_ref_update`) are two distinct concerns handled by two disjoint code paths with no shared decision function between them, so they warrant two separate corpus nodes rather than one that conflates admission and permission."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-core/src/git_perms.rs"
    confidence: 0.85
  - statement: "Issue #1034 requires this node to draw a clear boundary against the sibling task #1184 (`layers/tenancy/community-membership.md`), so that the two documents — one on tenancy admission, one on authorization — do not collide in meaning."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1034 task body"
---

# Community membership authorization

## Definition

**Community membership authorization** is the set of rules Buzz uses to decide
*what a pubkey that is already inside a community is allowed to do*, once
that pubkey's membership has been established. It answers a narrower
question than "is this actor a member of the community at all" — that
narrower, prior question is **tenancy admission**, and it is a different
concept, covered by the sibling corpus node at
`layers/tenancy/community-membership.md` (task #1184, not yet written at
this node's recorded revision — see *Scope and omissions*).

The two questions are answered by different code paths in Buzz today.
Admission is decided once, at the front door, by
`check_relay_membership`/`enforce_relay_membership` in
`crates/buzz-relay/src/api/mod.rs`, which the module's own doc comment calls
"the single gate for all authenticated entry points" — a pubkey either is or
is not in `relay_members` (directly, or via NIP-OA owner delegation), full
stop. **This node's subject starts after that gate has already passed.**
Given an admitted member, authorization asks a further question — *which*
things can they do — and the answer depends on a **role**, not just
membership: `MemberRole` (`crates/buzz-core/src/channel.rs`) defines a
five-value hierarchy, Owner > Admin > Member > Guest, with Bot deliberately
excluded from the ordering. `permission_level()` and `has_at_least()` turn
that hierarchy into the numeric comparison every authorization check in this
node's scope is built on.

Two independent role tables carry this vocabulary at different scopes:
`relay_members.role` is community-wide (`owner`/`admin`/`member` — a
three-value subset), and `channel_members.role` is channel-scoped (the full
five-value `member_role` enum, `owner`/`admin`/`member`/`guest`/`bot`). A
member's authorization for a community-wide action is decided from
`relay_members.role`; for a channel-local action, from `channel_members.role`
in that channel specifically. Neither table decides admission — a row in
either one already presupposes it.

## Background

The clearest statement of this concept in the codebase is
`authorize_moderation_action`'s own doc comment
(`crates/buzz-relay/src/handlers/moderation_authz.rs`): it is described as
"One capability seam for every moderation decision," so that "adding [a new
tier] later is a policy change, not a rewrite." That design goal — a single
place role is turned into permission, rather than authorization logic
scattered across each handler — is the organizing idea this node documents,
not a rule this node invents. The same shape recurs, independently, in git
push authorization: `git_perms::evaluate_ref_update` turns a `MemberRole`
and a ref update into an allow/deny decision through one function, called
from the real git-over-HTTP push path in
`crates/buzz-relay/src/api/git/policy.rs`.

## Use cases

A reader needs this concept when they are asking, for an already-admitted
community member, *"can they do X"* — not *"are they here at all."* Concrete
cases in the current codebase:

- **Moderation commands** (kinds 9040–9044: ban, unban, timeout, untimeout,
  resolve-report). `handle_moderation_command`
  (`crates/buzz-relay/src/handlers/moderation_commands.rs`) routes every one
  of these through `authorize_moderation_action` before touching the
  database — see, for example, `handle_ban`'s call to it ahead of
  `state.db.ban_community_member`. A community owner is authorized for all
  eight defined `ModerationAction` values, community-wide, with no guard
  rail; a community admin holds the same set but is blocked from applying
  `Ban`/`Timeout` to a target who is themself an owner or admin (only the
  owner may action an admin); a channel owner/admin without community role
  is authorized only for `DeleteMessage`/`Kick`, and only inside their own
  channel; a plain member is authorized for none of it.
- **Git ref pushes.** `default_min_role` maps a ref update (create,
  fast-forward, non-fast-forward, delete; branch or tag) to a minimum
  `MemberRole`, and `evaluate_ref_update` denies the push unless the
  pusher's role meets that floor. An explicit `push:role` protection tag can
  only raise the floor, never lower it below the built-in default.
- **Channel-scoped reads.** `get_member_role`/`is_member`
  (`crates/buzz-db/src/channel.rs`) are how a handler learns a pubkey's role
  or presence in one specific channel, as opposed to the community overall.

## Comparison

| | `relay_members.role` | `channel_members.role` |
|---|---|---|
| Scope | Whole community | One channel |
| Values | `owner`, `admin`, `member` (TEXT + CHECK) | `owner`, `admin`, `member`, `guest`, `bot` (Postgres enum `member_role`) |
| Read by | `authorize_moderation_action` (community authority path) | `authorize_moderation_action` (channel-role fallback for `DeleteMessage`/`Kick`), `get_member_role`, `git_perms` callers passing a resolved `MemberRole` |
| Decides | Whether a member may act community-wide | Whether a member may act inside one channel |

Both tables draw roles from the same underlying vocabulary
(`owner`/`admin`/`member` at minimum), but they are two separate rows for
the same pubkey and are not kept in lockstep by any code inspected for this
node — a pubkey's community role and its role in a specific channel can
differ.

## Scope and omissions

**This node covers** the concept of role-based authorization for an
already-admitted community member: the `MemberRole` hierarchy, the two role
tables that carry it at different scopes, and the two concrete policy seams
(`authorize_moderation_action`, `git_perms::evaluate_ref_update`) that
consult it. It does not itself explain any single one of those seams
exhaustively (their full rule sets belong to their own reference-shaped
documentation, not a concept node), and it does not cover:

- **Tenancy admission** — whether a pubkey is a community member at all.
  Owned by task #1184's `layers/tenancy/community-membership.md`. That file
  does not exist on `origin/launchpad` at this node's recorded revision, so
  no `relationships` edge is declared to it here; add one once it merges.
- **The join/invite flow** that creates a `relay_members`/`channel_members`
  row in the first place (`buzz-db/src/relay_members.rs`'s
  `claim_relay_membership`, `has_join_policy_acceptance`, and the invite API)
  — that is how a member is admitted, which is tenancy's subject, not this
  node's.
- **The full grammar of git protection-tag parsing**
  (`git_perms::parse_protection_tag`, pattern matching, `require_patch`) —
  only the role-floor mechanism (`default_min_role`,
  `evaluate_ref_update`/`evaluate_push`) is documented here, as one instance
  of the authorization concept; the full protection-rule syntax is reference
  material.
- **NIP-OA agent-owner delegation** (`extract_nip_oa_owner`,
  `materialize_nip_oa_owner`) — that is part of the tenancy admission gate
  (an agent acting for its owner is still an admission question, "who is
  this request from"), not an authorization question about role.

**Expected but not verified when this node was written:** whether any other
subsystem (e.g. workflow execution, search, media upload) consults
`MemberRole` or either role table for its own authorization decision was not
searched exhaustively — `authorize_moderation_action` and
`git_perms::evaluate_ref_update` are the two seams this node found and
verified by opening the source; there may be others not yet surfaced into
the corpus.
