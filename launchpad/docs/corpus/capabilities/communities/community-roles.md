---
id: capabilities-communities-community-roles
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
  - statement: "The `relay_members` table is the persistence for community-wide (relay-wide) roles: its `role` column is constrained by `CHECK (role IN ('owner', 'admin', 'member'))`, and its primary key is `(community_id, pubkey)` — one role per pubkey per community, community-scoped by construction."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:574-584"
  - statement: "`buzz-core::channel::MemberRole` is a separate, channel-scoped role model — its own doc comment states it is 'A member's role within a channel', with a five-value hierarchy Owner > Admin > Member > Guest > Bot (Bot excluded from the linear hierarchy) and a numeric `permission_level()` used for authorization comparisons. This is a distinct role set from the three-value community-wide `relay_members.role`, not an alias for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "`buzz-db::relay_members` implements the full community-role lifecycle: `add_relay_member`, `get_relay_member`, `list_relay_members`, `update_relay_member_role`, `remove_relay_member`, `remove_relay_member_if_role`, `bootstrap_owner`, and `transfer_ownership`, each taking a `CommunityId` and scoping its query to that community so a role never leaks across communities."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "The owner role is structurally protected at the data layer: `remove_relay_member` deletes with `WHERE role <> 'owner'` in one atomic statement (no separate read-then-delete race), and `update_relay_member_role` likewise updates only `WHERE role <> 'owner'` — an owner cannot be deleted or have their role changed through these two functions at all, only through `transfer_ownership`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`bootstrap_owner` runs at every relay startup: it upserts the configured `RELAY_OWNER_PUBKEY` as `owner` in a given community and demotes any other `owner` row in that same community to `admin`, so an owner-pubkey rotation in configuration is enforced idempotently on the next boot rather than requiring a manual role change."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`transfer_ownership` atomically upserts a new owner and demotes every other existing owner in that community to `member` — explicitly **not** `admin` — per a documented product decision that a former owner retains no management capability after a transfer; it also enforces a per-owner community cap (`MAX_COMMUNITIES_PER_OWNER`, default 5, overridable via `BUZZ_MAX_COMMUNITIES_PER_OWNER`) inside the same transaction as the transfer, guards against a stale-owner race with a `FOR UPDATE` lock and an `expected_owner_pubkey` check, and is a no-op (`AlreadyOwner`) when the transferee is already the sole owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "Community roles can be administered over the wire via four NIP-43 relay-admin event kinds handled directly (not stored as ordinary events): kind:9030 add member (sender must be `admin` or `owner`), kind:9031 remove member (sender must be `admin` or `owner`), kind:9032 change an existing member's role (sender must be `owner` only), and kind:9033 set the community's workspace profile/icon (sender must be `admin` or `owner`, with a documented exception on a rosterless open relay)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "The kind:9033 exception is 'steward-wins': on a relay that does not enforce membership (`require_relay_membership == false`) and whose community additionally has no `admin`/`owner` row at all (`has_admin_or_owner` returns false), any NIP-42-authenticated sender may set the workspace icon; the moment any steward (admin or owner) exists for that community, the ordinary admin/owner-only rule applies even on an otherwise-open relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "The four relay-admin kind integers are defined in the shared kind registry: `RELAY_ADMIN_ADD_MEMBER = 9030`, `RELAY_ADMIN_REMOVE_MEMBER = 9031`, `RELAY_ADMIN_CHANGE_ROLE = 9032`, `RELAY_ADMIN_SET_WORKSPACE_PROFILE = 9033`, each doc-commented as part of 'NIP-43: relay membership admin commands'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:387-395"
  - statement: "The operator-facing `buzz-admin` CLI's `validate_role` function accepts only `\"member\"` or `\"admin\"` and explicitly rejects `\"owner\"` with the message \"role 'owner' cannot be set via CLI — use RELAY_OWNER_PUBKEY config\" — the owner role is reachable only through relay configuration (`RELAY_OWNER_PUBKEY`, applied by `bootstrap_owner` at startup) or through `transfer_ownership`, never through a direct CLI or NIP-43 grant."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "Community roles are the primary authority for moderation: `moderation_authz::authorize_moderation_action` reads the actor's `relay_members.role` first, and a community `owner` or `admin` is authorized for every `ModerationAction` (DeleteMessage, Kick, Ban, Unban, Timeout, Untimeout, ResolveReport, ViewQueue) in any channel of their community — this is documented as the 'primary authority', with channel-level `owner`/`admin` roles (from `MemberRole`) granting only `DeleteMessage`/`Kick` within their own channel when no community role applies."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "`moderation_authz::decide_authority` enforces a guard rail on the community `admin` role specifically: an admin cannot `Ban` or `Timeout` a target whose own community role is `owner` or `admin` — only the community `owner` may action a fellow admin or the owner — while `Unban`/`Untimeout` (lifting a restriction) and all other actions against an admin target remain unguarded; a community `owner` has no guard rail against any target for any action, per `community_owner_authorized_for_everything` and `admin_cannot_ban_or_timeout_owner_or_fellow_admin` in that module's own test suite."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "`NOSTR.md`'s own 'Relay Membership (NIP-43)' section documents the same three-role model in operator-facing prose: `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true` gates every authenticated connection against the community-scoped `relay_members` table, the relay owner is bootstrapped from `RELAY_OWNER_PUBKEY` on startup, and the `buzz-admin` CLI (`add-member`, `remove-member`, `list-members`, each accepting `--role`) is the documented operator path for managing membership and role, alongside the four WebSocket NIP-43 admin event kinds."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "The `require_relay_membership` config field (populated from the `BUZZ_REQUIRE_RELAY_MEMBERSHIP` environment variable) defaults to `false` — an 'open' relay does not enforce the `relay_members` roster for connection admission, though the roster and its roles can still exist and still govern moderation and the NIP-43 admin surface regardless of that flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "Community-wide roles (`relay_members.role`) are a distinct concept from NIP-29's per-channel group discovery events (kind:39000 metadata, kind:39001 admins, kind:39002 members, addressable range 39000-39003) — those describe a channel's own membership/admin list at the protocol-discovery layer and are read by the channel-scoped `MemberRole` model, not by `relay_members`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:420-426"
  - statement: "Issue #736's own definition of done requires this node to satisfy the corpus's general capability-node bullets (schema-valid front matter, one independently maintainable idea, traceable claims, linked verification, validation passing) plus four capability-specific bullets: state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#736 definition of done"
---

# Community roles: capability

Buzz communities support a small, relay-wide role system — **owner**, **admin**, and
**member** — that is independent of any single channel. A community's owner or admin
can add, remove, and re-role other members of that same community; grant or revoke
moderation authority across every channel in the community; and, in the owner's case,
transfer ownership of the community itself to another member. This is what lets a
community have stewards who outrank any individual channel's own owner/admin, and it
is the seam every other community-wide authorization decision in the relay currently
reads from.

## Maturity

**Shipped.** The `relay_members` table has existed since the relay's initial schema
migration (`migrations/0001_initial_schema.sql`), and every path described below —
data-layer CRUD, the four NIP-43 WebSocket admin event kinds, the `buzz-admin`
operator CLI, and the moderation-authorization bridge — is implemented, code-reachable,
and covered by unit tests in the current tree (`crates/buzz-db/src/relay_members.rs`,
`crates/buzz-relay/src/handlers/relay_admin.rs`,
`crates/buzz-relay/src/handlers/moderation_authz.rs`,
`crates/buzz-admin/src/main.rs`). This capability's live-database integration tests
(`#[ignore = "requires Postgres"]` in `relay_members.rs`) were not executed while
authoring this node — see *Scope and omissions* below.

## Roles

| Role | Granted via | Removable/demotable via |
|---|---|---|
| `owner` | `RELAY_OWNER_PUBKEY` config, applied by `bootstrap_owner` at startup; or `transfer_ownership` | Only `transfer_ownership` (never `remove_relay_member` or `update_relay_member_role`, both of which explicitly exclude `role = 'owner'`) |
| `admin` | NIP-43 kind:9030 (by an existing admin/owner) or `update_relay_member_role` via NIP-43 kind:9032 (owner only), or the `buzz-admin` CLI's `add-member --role admin` | NIP-43 kind:9031, kind:9032 (owner only), or the CLI |
| `member` | NIP-43 kind:9030 (default role), the CLI's `add-member` (default role), or invite-code claiming (`claim_relay_membership`) | NIP-43 kind:9031, kind:9032 (owner only), or the CLI |

Exactly one role per `(community_id, pubkey)` pair — the `relay_members` primary key
enforces this structurally, so a pubkey cannot simultaneously hold two community roles
in the same community.

## Behavioral rules

- **The owner role cannot be granted or changed by direct command.** Neither the
  `buzz-admin` CLI (`validate_role` explicitly rejects `"owner"`) nor the NIP-43
  kind:9032 change-role command can produce an owner. The only paths to becoming owner
  are relay-configuration bootstrap (`RELAY_OWNER_PUBKEY`) and `transfer_ownership`.
- **Changing a member's role requires the owner specifically; adding or removing a
  member requires only admin or owner.** The NIP-43 permission matrix is
  fine-grained: kind:9030 (add) and kind:9031 (remove) accept admin or owner as
  sender; kind:9032 (change role) accepts owner only.
- **Ownership transfer demotes the old owner to `member`, not `admin`.** This is a
  deliberate product decision recorded in `transfer_ownership`'s own doc comment: a
  former owner keeps no residual management capability after handing the community
  off.
- **An admin cannot ban or time out the owner or a fellow admin — only the owner
  can.** This guard rail is scoped narrowly: it applies only to `Ban` and `Timeout`
  (applying a restriction), never to `Unban`/`Untimeout` (lifting one) or to any other
  moderation action, and it triggers only when the *target's* community role is
  `owner` or `admin` — an admin may still ban or time out a plain member or a pubkey
  with no `relay_members` row at all.
- **A community owner has no guard rail.** `decide_authority` authorizes `owner` for
  every `ModerationAction` against every target, including another owner or admin,
  with no exception.
- **Community role outranks channel role for moderation.** `authorize_moderation_action`
  checks the actor's community role first; only when no community role applies does it
  fall back to the actor's channel-level `MemberRole` (`Owner`/`Admin`), and even then
  only for the two channel-local actions `DeleteMessage` and `Kick` — a channel role
  never grants a community-wide action like `Ban` or `Timeout`.
- **Community roles are enforced independent of the relay's open/closed setting.**
  `require_relay_membership` (`BUZZ_REQUIRE_RELAY_MEMBERSHIP`) governs whether the
  roster gates *connection admission* on an otherwise-open relay; it does not disable
  role checks for moderation or the NIP-43 admin surface, which read `relay_members`
  regardless. The one documented exception is kind:9033 (workspace profile/icon) on a
  rosterless open relay, where any authenticated sender is admitted specifically
  because no steward exists yet to gate on.

## Boundary

This node does not describe:

- **How a community role is stored or queried at the SQL/Rust level beyond what
  supports the claims above** — see `crates/buzz-db/src/relay_members.rs` and
  `migrations/0001_initial_schema.sql` directly rather than this node's paraphrase,
  which will drift the moment those files change.
- **The channel-level `MemberRole` hierarchy (Owner/Admin/Member/Guest/Bot) in its own
  right** — that is a distinct capability with its own permission-level model in
  `crates/buzz-core/src/channel.rs`; this node only describes where it yields to
  community role and where it does not (see *Behavioral rules* above). No corpus node
  for it existed at authoring time to `references`.
- **The NIP-29 channel-discovery events (kind:39000/39001/39002)** — those describe a
  channel's own metadata/admin/member list at the protocol layer and are a separate
  mechanism from `relay_members`; see `crates/buzz-core/src/kind.rs`.
- **The interface(s) this capability is exposed through** (the NIP-43 WebSocket event
  surface, the `buzz-admin` CLI, and any future HTTP admin surface) as boundary
  contracts in their own right — no interface-type corpus node existed at authoring
  time to `references`.
- **The step-by-step flow of, e.g., one ownership transfer or one role change** — that
  is a flow-type node's job, none of which exists yet for this subject.
- **How the running relay is operated** (deployment, monitoring) beyond the
  configuration flags this capability itself reads (`RELAY_OWNER_PUBKEY`,
  `BUZZ_REQUIRE_RELAY_MEMBERSHIP`, `BUZZ_MAX_COMMUNITIES_PER_OWNER`).
- **Community invite codes and join-policy acceptance** (`invite.rs`,
  `claim_relay_membership`'s policy-version bookkeeping) beyond noting that claiming
  an invite is one path to the default `member` role — the invite mechanism itself is
  a separate concept.

## Relationships

None declared. No architecture, interface, or flow corpus node describing
`relay_members`, the NIP-43 admin surface, or `buzz-admin` existed under
`launchpad/docs/corpus/` at the recorded revision — the merged tree contains
architecture nodes for containers, context, deployment, flows, and principles, but
none whose subject is community/relay membership or moderation authorization
specifically (verified by listing `launchpad/docs/corpus/architecture/**/*.md` at this
revision). Declaring a `references` edge to an unrelated node would misrepresent this
capability's actual dependencies; the first sibling node on this subject is the
moment to add one.

## Scope and omissions

**This node covers** the community-wide (relay-wide) role model — owner, admin,
member — as distinct from channel-level roles: how each role is granted and revoked,
the permission matrix for the four NIP-43 relay-admin commands, the `buzz-admin` CLI's
role rules, and how community role feeds community-wide moderation authorization.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The channel-level `MemberRole` hierarchy in its own right | a future capability/architecture node for channel roles, not yet drafted |
| The NIP-43 WebSocket / `buzz-admin` CLI surfaces as interface contracts | a future interface-type node, not yet drafted |
| Step-by-step ownership-transfer or role-change flow | a future flow-type node, not yet drafted |
| Full moderation capability grid beyond the community-role guard rail described here | `crates/buzz-relay/src/handlers/moderation_authz.rs` and `PLANS/COMMUNITY_MODERATION_PLAN.md` directly |
| Relay invite codes and join-policy acceptance | a future node on invites, not yet drafted |

**Expected but not verified when this node was written:**

- **The live-database integration tests in `relay_members.rs`** (all marked
  `#[ignore = "requires Postgres"]`) were read for their asserted behavior but not
  executed against a running Postgres instance while authoring this node — what is
  verified above is the presence and shape of the code and its test assertions, not a
  passing run of them at this revision.
- **`PLANS/COMMUNITY_MODERATION_PLAN.md`**, referenced by `moderation_authz.rs`'s own
  doc comment as the source design document for the moderation capability grid, was
  not opened while authoring this node; the behavioral rules above are drawn directly
  from the implementation and its own unit tests, not from that plan document.
- **Whether any request surface added after this revision correctly reads
  `relay_members` before granting community-scoped authority** — this node documents
  the mechanism and its current call sites, not a guarantee that every future surface
  complies.
