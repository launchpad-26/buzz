---
id: layers-tenancy-community-membership
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
  - statement: "The `relay_members` table (NIP-43) has primary key `(community_id, pubkey)` and a `role` column typed `TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member'))`; a row's mere existence for a `(community_id, pubkey)` pair is what the codebase treats as community membership, independent of the role value it carries."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`crates/buzz-relay/src/api/mod.rs`'s `relay_members` module documents `check_relay_membership`/`enforce_relay_membership` as 'Relay membership enforcement — single gate for all authenticated entry points,' called by `media.rs`, `bridge.rs`, `git/transport.rs`, and `audio/handler.rs`; it returns a `MembershipDecision` (`OpenRelay`, `Member`, `ViaOwner(pubkey)`, `Denied`) and is explicitly community-scoped so admitting a pubkey to community A never admits it to community B."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "When a caller's pubkey is not directly present in `relay_members`, `check_relay_membership` falls back to NIP-OA owner delegation: it verifies the request's auth-tag header against the agent pubkey via `buzz_sdk::nip_oa::verify_auth_tag`, and if the recovered owner pubkey is itself a relay member, returns `MembershipDecision::ViaOwner(owner)` — admission granted through the owner rather than the agent's own row."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "`require_relay_membership` (`crates/buzz-relay/src/config.rs`, env `BUZZ_REQUIRE_RELAY_MEMBERSHIP`) defaults to `false`; when false the membership check is a no-op and every authenticated caller is admitted regardless of any `relay_members` row, i.e. tenancy admission is opt-in per deployment, not always enforced."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`claim_invite` (`crates/buzz-relay/src/api/invites.rs`) admits a pubkey via two code paths keyed by token prefix: a v2 database-backed path (`state.db.claim_relay_invite`, tracking expiry/exhaustion) and a v1 stateless HMAC path (`invite_token::verify_invite` plus `state.db.claim_relay_membership`); both require a join-policy acceptance receipt when `state.config.join_policy` is set, verified before any membership row is written."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "`claim_relay_membership` (`crates/buzz-db/src/relay_members.rs`) inserts the membership row and records the accepted `policy_version` in the same database transaction, so a v1-path membership can never exist without its policy-acceptance evidence persisted atomically alongside it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`crates/buzz-relay/src/handlers/relay_admin.rs` handles kind:9030 (add member), kind:9031 (remove member) and kind:9032 (change role) as admin-driven tenancy commands: the sender must already hold `admin` or `owner` role; only an owner may grant the `admin` role or change any role; an admin's removal is routed through the atomic `remove_relay_member_if_role(..., \"member\")` (refusing to touch admins/owners), while an owner's removal is routed through `remove_relay_member`, which refuses to delete a row with role `owner`; a sender may not remove or role-change themself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "`remove_relay_member` and `remove_relay_member_if_role` (`crates/buzz-db/src/relay_members.rs`) collapse the owner/role check and the `DELETE` into one conditional SQL statement each, so there is no time-of-check-to-time-of-use race between reading a member's current role and deleting the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`crates/buzz-relay/src/handlers/ingest.rs` (around line 2351) handles kind:28936 (`KIND_NIP43_LEAVE_REQUEST`) as a self-service tenancy removal: it is rejected outside a ±120s freshness window and unless it carries a NIP-70 `-` protected-event tag, then calls `state.db.remove_relay_member` for the sender's own pubkey; `RemoveResult::IsOwner` is surfaced back to the caller as 'relay owner cannot leave' and `RemoveResult::NotFound` as 'you are not a relay member.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`crates/buzz-core/src/kind.rs` defines the NIP-43 tenancy-command and announcement kinds this node discusses: 9030/9031/9032 (add/remove/change-role admin commands, user-signed), 8000/8001 (member-added/member-removed relay-signed delta announcements), 13534 (relay-signed membership-list snapshot), and 28936 (user-signed leave request)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "`bootstrap_owner` and `transfer_ownership` (`crates/buzz-db/src/relay_members.rs`) are both scoped to a single `community: CommunityId` argument and operate inside one transaction; `transfer_ownership` enforces a per-owner community cap (`MAX_COMMUNITIES_PER_OWNER`, overridable via `BUZZ_MAX_COMMUNITIES_PER_OWNER`) atomically inside the transfer, while `bootstrap_owner`'s own doc comment states it is a deployment-root-only path that does NOT enforce that cap, because it is not an end-user admission route."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "Unit tests `membership_is_confined_to_its_community` and `owner_bootstrap_is_confined_to_its_community` (`crates/buzz-db/src/relay_members.rs`, `#[cfg(test)] mod tests`) assert that admitting or bootstrapping a pubkey in one community's `relay_members` never admits or bootstraps that pubkey in a different community, guarding the exact class of cross-tenant admission leak issue #1285 targeted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`launchpad/docs/corpus/AGENTS.md` states that one corpus node is one independently maintainable idea, and that a second concept, contract or procedure discovered while writing is filed as its own task and linked, not folded in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "`launchpad/docs/corpus/layers/authorization/community-membership.md` (task #1034, PR #1799) does not exist in this worktree's `launchpad/docs/corpus` tree at this node's recorded revision — confirmed by running `find launchpad/docs/corpus -type f` in this worktree, which lists no `layers/` directory at all — so no `relationships` edge is declared to it here."
    entry_class: FACT
    evidence:
      - "find('launchpad/docs/corpus', type='f') -> no layers/ path listed, run in this worktree at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`authorize_moderation_action`'s module doc comment (`crates/buzz-relay/src/handlers/moderation_authz.rs`) states its checks read the actor's role from `relay_members`/`channel_members` 'under tenant.community() only,' and that 'callers must have already resolved target inside the same tenant' — i.e. the authorization seam presupposes admission has already happened and does not itself decide it. `git_perms::default_min_role`/`evaluate_ref_update` (`crates/buzz-core/src/git_perms.rs`) likewise take a caller's already-resolved `MemberRole` as input rather than deciding whether that caller is a community member at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "Tenancy admission (whether a `relay_members` row exists for a pubkey in a community, decided by `check_relay_membership`/`enforce_relay_membership`, `claim_invite`, the kind:9030-9032 admin commands, and the kind:28936 leave request) and community-member authorization (what an already-admitted pubkey with a given role may do, decided by `authorize_moderation_action` and `git_perms::evaluate_ref_update`) are two distinct concerns handled by disjoint functions with no shared decision path between them, so they warrant two separate corpus nodes rather than one that conflates admission with permission."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-core/src/git_perms.rs"
    confidence: 0.85
  - statement: "This node draws a clear boundary against sibling task #1034 (`layers/authorization/community-membership.md`) so that the two documents — one on tenancy admission, one on authorization — do not collide in meaning; issue #1184's own body does not state this #1034-boundary framing, but it follows from `launchpad/docs/corpus/AGENTS.md`'s one-node-one-concept rule applied against the sibling task's existing, non-overlapping subject."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "https://github.com/launchpad-26/buzz/issues/1184"
      - "https://github.com/launchpad-26/buzz/issues/1034"
    confidence: 0.75
---

# Community membership tenancy

## Definition

**Community membership tenancy** is the question of whether a pubkey is
admitted to a Buzz community *at all* — whether a row for that
`(community_id, pubkey)` pair exists in the `relay_members` table. It is a
strictly prior, narrower question than "what is this pubkey allowed to do,"
which is a different concept: **community membership authorization**,
covered by the sibling corpus node at
`layers/authorization/community-membership.md` (task #1034, not merged as of
this node's recorded revision — see *Scope and omissions*). This node's
subject ends the moment a row exists or is removed; it does not cover which
capabilities that row's `role` value grants.

Buzz draws this boundary in its own code, not just in this document. The
authorization seam's own module doc comment
(`crates/buzz-relay/src/handlers/moderation_authz.rs`) says its checks read
role "under `tenant.community()` only" and that "callers must have already
resolved target inside the same tenant" — authorization takes admission as
a precondition it does not itself decide. `git_perms`'s ref-update
authorization takes an already-resolved `MemberRole` as an input parameter
for the same reason. Tenancy, by contrast, is decided once, at the front
door: `check_relay_membership`/`enforce_relay_membership`
(`crates/buzz-relay/src/api/mod.rs`) is documented as "the single gate for
all authenticated entry points," called from `media.rs`, `bridge.rs`,
`git/transport.rs`, and `audio/handler.rs`. It returns a `MembershipDecision`
— `OpenRelay`, `Member`, `ViaOwner(owner_pubkey)`, or `Denied` — scoped to
one community, so admission to community A never implies admission to
community B.

Tenancy admission in Buzz is **opt-in per deployment**: `require_relay_membership`
(env `BUZZ_REQUIRE_RELAY_MEMBERSHIP`) defaults to `false`, and on an open
relay the gate is a no-op — every authenticated caller passes regardless of
any `relay_members` row. The `relay_members` table and its admission
machinery exist and are enforceable, but a given deployment chooses whether
the gate actually gates anything.

## Background

`relay_members` implements NIP-43 relay-membership semantics. A row's
existence is binary tenancy — present or absent — while its `role` column
(`owner`/`admin`/`member`, a three-value `TEXT CHECK`, narrower than the
five-value `channel_members.role` enum the authorization node documents)
only becomes meaningful once authorization reads it. A pubkey can be
admitted (`relay_members` row exists) with role `member` and simultaneously
be authorized for nothing beyond ordinary participation — admission does not
imply any particular capability, it implies only presence.

Admission and removal both need an actor and a rule for who may perform
them; several distinct routes exist, and each is enforced independently
rather than through one shared "can this actor add/remove a member"
function.

## Use cases

A reader needs this concept when asking, for a given pubkey and community,
*"are they here at all,"* or *"how did they get here / how did they leave"* —
not "what can they do now that they are." Concrete admission and removal
routes in the current codebase:

- **Invite claim** (`POST` handled by `claim_invite`,
  `crates/buzz-relay/src/api/invites.rs`). Two token formats: a v2
  database-backed invite (`state.db.claim_relay_invite`, tracking expiry and
  exhaustion) and a v1 stateless HMAC token
  (`invite_token::verify_invite` + `state.db.claim_relay_membership`). Both
  require a signed join-policy acceptance receipt when the deployment
  configures `join_policy`, verified before the membership row is written;
  the v1 path additionally records the accepted `policy_version` in the same
  transaction as the row insert, so a member can never exist without that
  evidence.
- **Admin-driven add/remove/role-change** (kind:9030/9031/9032, handled in
  `crates/buzz-relay/src/handlers/relay_admin.rs`). The sender must already
  be `admin` or `owner`; only an owner may grant `admin` or change any role;
  an admin may only remove plain `member`s (enforced atomically via
  `remove_relay_member_if_role`, closing a TOCTOU window where a target
  could be promoted between a role read and a delete); an owner may remove
  admins or members but never another owner (`remove_relay_member` refuses
  to delete a row with role `owner`); nobody may remove or role-change
  themself through this path.
- **Self-service leave** (kind:28936 / `KIND_NIP43_LEAVE_REQUEST`, handled
  in `crates/buzz-relay/src/handlers/ingest.rs`). Requires a NIP-70 `-`
  protected-event tag and a timestamp within ±120s of receipt, then calls
  `remove_relay_member` for the sender's own pubkey. The relay owner cannot
  leave this way (`RemoveResult::IsOwner`); a non-member's leave request is
  rejected (`RemoveResult::NotFound`).
- **NIP-OA owner delegation** (`check_relay_membership`,
  `crates/buzz-relay/src/api/mod.rs`). When the caller's own pubkey is not a
  `relay_members` row, a cryptographically verified NIP-OA auth tag can
  admit the request on behalf of an owner pubkey that *is* a member —
  `MembershipDecision::ViaOwner(owner)`. This grants request-scoped access;
  it does not by itself insert a `relay_members` row for the agent (that is
  a separate backfill path, `materialize_nip_oa_owner`, which records the
  agent→owner mapping via `set_agent_owner`, not a membership grant).
- **Owner bootstrap and rotation** (`bootstrap_owner`, `transfer_ownership`,
  `crates/buzz-db/src/relay_members.rs`). Both are community-scoped and
  transactional. `bootstrap_owner` runs at every relay startup, ensuring
  `RELAY_OWNER_PUBKEY` holds the `owner` role and demoting any other owner
  in that community to `admin`; it is explicitly exempt from the per-owner
  community limit because it is a deployment-root path, not an end-user
  admission route. `transfer_ownership` enforces
  `MAX_COMMUNITIES_PER_OWNER` atomically inside its own transaction so
  concurrent transfers cannot both pass the limit, and demotes the previous
  owner to `member` — not `admin` — by product decision.

Every admission or removal that succeeds through the invite, admin-command,
or leave-request paths publishes a NIP-43 announcement: kind:8000
(member-added) or kind:8001 (member-removed) as a relay-signed delta, and a
refreshed kind:13534 membership-list snapshot.

**Verification.** `crates/buzz-db/src/relay_members.rs`'s
`membership_is_confined_to_its_community` and
`owner_bootstrap_is_confined_to_its_community` unit tests are the checked
evidence for the tenant-confinement claim running through every route
above: admitting or bootstrapping a pubkey in one community's
`relay_members` never admits or bootstraps it in another.

## Comparison

| Route | Actor | Target | Guard |
|---|---|---|---|
| Invite claim | The joining pubkey itself | Self | Valid invite token + join-policy receipt (if configured) |
| kind:9030 add | Admin or owner | Any pubkey | Only owner may grant `admin`; idempotent no-op if already a member |
| kind:9031 remove | Admin or owner | Any pubkey except self | Admin limited to removing plain members; owner cannot be removed by anyone |
| kind:28936 leave | The member itself | Self | NIP-70 tag + ±120s freshness; owner cannot leave |
| Owner bootstrap/transfer | Deployment config / owner | Owner role only | Community-scoped; transfer enforces per-owner community cap |

## Scope and omissions

**This node covers** the concept of tenancy admission for Buzz community
membership: the `relay_members` table and what a row's existence means, the
single admission gate (`check_relay_membership`/`enforce_relay_membership`),
and the concrete routes by which a row is created or removed (invite claim,
admin commands, self-leave, NIP-OA delegation, owner bootstrap/rotation).
It does not exhaustively document any one route's full request/response
contract, and it does not cover:

- **Community membership authorization** — what an already-admitted
  pubkey's role permits it to do (`authorize_moderation_action`,
  `git_perms::evaluate_ref_update`, the `MemberRole` hierarchy). Owned by
  task #1034's `layers/authorization/community-membership.md`. That file
  does not exist in `launchpad/docs/corpus` on `origin/launchpad` at this
  node's recorded revision (PR #1799 is open, not merged), so no
  `relationships` edge is declared to it here; add one once it merges.
- **Channel-level membership** (`channel_members`, `get_member_role`,
  `is_member` in `crates/buzz-db/src/channel.rs`, and the kind:9001/9022
  channel join/leave/kick flows in
  `crates/buzz-relay/src/handlers/side_effects.rs`). Channel membership is a
  separate, channel-scoped tenancy question — a pubkey can be a community
  member with no channel memberships, or vice versa in an open-relay
  configuration — and is left as a distinct concept for its own task rather
  than folded in here.
- **The full join-policy acceptance mechanism** (policy versioning,
  receipt cryptography, `has_join_policy_acceptance`) — only that an
  acceptance receipt gates invite-based admission when configured is
  documented here; the mechanism itself is reference material for its own
  node.
- **NIP-OA agent identity and delegation mechanics** beyond the admission
  decision itself (auth-tag verification, `agent_owner_pubkey` backfill
  semantics) — only the admission consequence (`ViaOwner`) is in scope here.

**Expected but not verified when this node was written:** whether every
authenticated entry point in the relay actually calls
`enforce_relay_membership`/`check_relay_membership` (versus one that bypasses
it) was not exhaustively audited — the four call sites named in
`api/mod.rs`'s own doc comment (`media.rs`, `bridge.rs`, `git/transport.rs`,
`audio/handler.rs`) were taken as authoritative but not each individually
re-verified by opening those four files in this session; a later audit could
surface a fifth, unguarded entry point.
