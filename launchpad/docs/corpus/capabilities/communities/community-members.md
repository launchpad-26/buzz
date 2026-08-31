---
id: capabilities-communities-community-members
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
  - statement: "Relay-wide (community-wide) membership is a NIP-43 roster, `relay_members`, keyed by `(community_id, pubkey)`, with `role` constrained by a CHECK to `'owner'`, `'admin'`, or `'member'`; the module doc comment states every read, write and list is bound to a single `community_id` so admitting a pubkey to one community never admits it to another."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "This roster is distinct from NIP-29 per-channel membership: `channel_members` is a separate table keyed by `(community_id, channel_id, pubkey)`, carrying its own `member_role` enum and its own join/removal timestamps, populated from kind:39002 channel-membership events rather than from the relay-admin commands below."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Membership is granted or changed by three NIP-43 admin command kinds the relay processes directly rather than storing as ordinary events: kind:9030 (add member), kind:9031 (remove member), kind:9032 (change role); a fourth, kind:9033 (set workspace profile/icon), shares the same command file and a similar permission style but governs community branding, not membership, and is out of scope for this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "The relay's own permission matrix, stated in `relay_admin.rs`'s module doc comment, requires the sending pubkey to hold `admin` or `owner` to add or remove a member, and `owner` specifically to change a member's role; `remove_relay_member` and `remove_relay_member_if_role` both refuse to delete a row whose role is `owner`, enforced as a single atomic `DELETE ... WHERE role <> 'owner'` rather than a separate read-then-delete."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "Membership changes are announced relay-side through two further NIP-43 event kinds: kind:13534, an addressable, NIP-70-protected snapshot listing every current member (replaces any previous snapshot, published inside the same lock that serializes the read-build-write cycle), and kind:8000/kind:8001, one-shot 'member added'/'member removed' delta announcements, both relay-signed."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A member can voluntarily leave via kind:28936, a user-signed ephemeral leave request; the desktop client's `leaveCommunity` first checks whether the target relay enforces membership at all (`relayRequiresMembership`) and treats a relay's 'not a relay member' rejection as an idempotent already-left outcome rather than an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "desktop/src/features/communities/leaveCommunity.ts"
  - statement: "Whether relay membership is enforced at all is a per-deployment configuration flag, `require_relay_membership`, defaulting to `false` (open relay); `check_relay_membership` short-circuits to `MembershipDecision::OpenRelay` when the flag is off, so an open-relay deployment performs no membership lookup on the authenticated-request path this function gates."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "On a closed relay, `enforce_relay_membership` grants access either because the caller is a direct `relay_members` row, or — when `allow_nip_oa_auth` is set and the caller presents a valid NIP-OA auth tag — because the caller's cryptographically attested owner pubkey is itself a member; only when neither holds does it return the `relay_membership_required` 403 denial."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "Bulk onboarding is by use-limited v2 invite codes: `relay_invites` stores only `SHA-256(code)` (never the reusable bearer secret) scoped to `(community_id, token_hash)`, and `claim_relay_invite` performs the full redemption — invite lookup, expiry check, membership insert, join-policy evidence insert, and `use_count` increment — inside one transaction with `SELECT ... FOR UPDATE` on the invite row, so concurrent claimants for the last slot cannot both win."
    entry_class: FACT
    evidence:
      - "migrations/0025_relay_invites.sql"
      - "crates/buzz-db/src/relay_invite.rs"
  - statement: "The invite HTTP surface is NIP-98-signed rather than a Nostr admin event: `POST /api/invites` mints a code and requires the caller to hold `owner`/`admin` in the tenant community (mirroring kind:9030's authorization), while `POST /api/invites/claim` is deliberately exempt from the relay-membership gate, since its entire purpose is admitting a pubkey that is not yet a member — NIP-98 proves control of the joining key, and the invite's hash proves an admin authorized the join."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
  - statement: "A `join_policy_acceptances` row records, per `(community_id, pubkey, policy_version)`, that a member accepted a specific join-policy version at claim time; it foreign-keys to `relay_members(community_id, pubkey)` with `ON DELETE CASCADE`, so the acceptance record cannot outlive the membership it evidences, and `claim_relay_membership`/`claim_relay_invite` write both rows in the same transaction so membership is never granted without accompanying policy-acceptance evidence when a policy version is configured."
    entry_class: FACT
    evidence:
      - "migrations/0020_join_policy_acceptances.sql"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "Exactly one `owner` role exists per community at a time. `bootstrap_owner` upserts the configured `RELAY_OWNER_PUBKEY` as owner and demotes any other existing owner rows to `admin`; `transfer_ownership` atomically upserts a new owner and demotes every other owner in that community to `member` (not `admin`, per an explicit product decision recorded in the function's own doc comment), inside a transaction that locks the current owner row `FOR UPDATE` and rejects a stale `expected_owner_pubkey` as `OwnerConflict`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "A single pubkey's ownership is capped across communities: `transfer_ownership` counts communities the transferee already owns inside the same transaction that holds a per-transferee advisory lock, and refuses the transfer as `TransferResult::LimitReached` at or above `max_communities_per_owner()` (default `MAX_COMMUNITIES_PER_OWNER = 5`, overridable via `BUZZ_MAX_COMMUNITIES_PER_OWNER`); the function's own doc comment states this is the authoritative enforcement point, not merely an advisory preflight count performed elsewhere."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "`relay_members.rs` carries an `#[ignore]`-gated (requires a live Postgres) unit test, `membership_is_confined_to_its_community`, whose own comment names it as guarding against exactly the mutation of a `WHERE pubkey = $1` membership check with no community predicate — it asserts that a pubkey admitted to community A is absent from `is_relay_member`, `get_relay_member`, and `list_relay_members` for community B."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "The desktop app ships a Settings > Community Members surface: `CommunityMembersCard` lists members sorted owner-first, lets an owner or admin add a member (with a role) or remove one, and lets an owner promote a member to admin or demote an admin to member; `desktop/src/shared/api/relayMembers.ts` implements this entirely by signing and publishing the kind:9030/9031/9032 Nostr events described above and by reading the kind:13534 snapshot — there is no separate REST call for these mutations."
    entry_class: FACT
    evidence:
      - "desktop/src/features/community-members/ui/CommunityMembersCard.tsx"
      - "desktop/src/features/community-members/hooks.ts"
      - "desktop/src/shared/api/relayMembers.ts"
  - statement: "A case-sensitive-path grep of `mobile/lib` for relay-membership terms (`relay_member`, `RelayMember`, `Nip43`/`nip43`/`NIP-43`/`NIP43`) at the recorded revision returned no matching file, so the Flutter mobile app has no located implementation of this capability's add/remove/role-change/leave surface."
    entry_class: FACT
    evidence:
      - "grep_recursive('relay_member|RelayMember|Nip43|nip43|NIP-43|NIP43', path='mobile/lib') -> no matches, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #734's definition of done requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link the major flows/interfaces/data/platform implementation that realize it, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#734 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# Community members: capability

Buzz lets a community's owner or admins control who belongs to that community
at the relay level — who can authenticate at all on a closed relay, who holds
`owner`/`admin`/`member` authority over the roster itself, and how new
members are admitted (individually, by an admin action, or in bulk, via a
use-limited invite code). This is *relay-wide* membership: it decides whether
a pubkey is part of the community at all, a distinct and coarser-grained
concept from NIP-29 per-channel membership, which decides whether an
already-admitted member can read or write inside one particular channel.

## Maturity

**Shipped**, both server- and client-side. The `relay_members` roster table,
its role model, the NIP-43 admin-command handlers (kinds 9030-9032), the
membership-enforcement gate, the use-limited v2 invite mint/claim path, and
ownership bootstrap/transfer are implemented and covered by (mostly
Postgres-gated, `#[ignore]`) unit tests in `crates/buzz-db/src/relay_members.rs`
and `crates/buzz-db/src/relay_invite.rs`. The desktop app ships a working
Settings surface (`CommunityMembersCard`) that adds, removes, and promotes/demotes
members and reads the live roster snapshot, built entirely on these same event
kinds. No implementation of this capability was located in the Flutter mobile
app (see evidence ledger) — mobile is a gap, not merely undocumented.

## Boundary

This node does not describe:

- **How the roster is built (architecture).** `relay_members`'s schema,
  `buzz-relay`'s NIP-43 command handler, and the membership-enforcement gate
  are the *how*; no architecture-family corpus node yet documents that
  container/component picture specifically. Not yet in this corpus.
- **The interface contracts this capability is exposed through.** Two
  distinct boundary shapes grant or query membership — the Nostr admin-event
  surface (kinds 9030-9032, and kind:28936 to leave) and the NIP-98-signed
  HTTP invite surface (`POST /api/invites`, `POST /api/invites/claim`) — and
  neither has its own interface-family corpus node yet. Not yet in this
  corpus.
- **The step-by-step path through an invite claim or a member add.** The
  ordered mechanics of `claim_relay_invite`'s transaction, or of a
  `handle_relay_admin_command` add/remove/role-change round trip, belong to a
  flow-family node. Not yet in this corpus. (`architecture-flows-websocket-authentication`,
  referenced below, documents one adjacent step — the relay-membership check
  that runs during NIP-42 authentication — but not this capability's own
  admission/removal/role-change/invite paths.)
- **How the running system is operated.** Bootstrapping `RELAY_OWNER_PUBKEY`
  at deployment time is an operations concern touched only incidentally here
  (`bootstrap_owner`); the `operations` corpus surface, not this node, owns
  deployment-time procedure.
- **Kind:9033 (workspace profile/icon).** It is processed by the same
  `relay_admin.rs` handler and shares this capability's permission-matrix
  *style*, but it sets a community's display icon, not who belongs to the
  community — a separate concern this node deliberately does not narrate.
- **NIP-29 per-channel membership.** `channel_members` (kind:39002) is a
  separate, per-channel roster with its own role enum and its own capability
  document, not this one.
- **NIP-OA's owner-delegation attestation format.** This node states that
  `enforce_relay_membership` can admit an agent via its owner's membership,
  but not how that attestation is minted or verified — see
  `architecture-flows-websocket-authentication`'s own scope note on the same
  boundary.

## Relationships

- `references`: `architecture-flows-websocket-authentication` — the merged
  flow node that documents the NIP-42 authentication round trip, one step of
  which (`enforce_relay_membership`) is this capability's own
  membership-enforcement gate running inline in that flow. Checked against
  `origin/launchpad`'s corpus tree at the recorded revision, where this id is
  present.

No other `relationships` are declared. No architecture, interface, or flow
node documenting this capability's own implementation is yet merged to
`origin/launchpad`, and a target naming an id no loaded node carries is a hard
validation error (`launchpad/docs/corpus/AGENTS.md`); this is the moment to
add such an edge once one of those sibling nodes exists.

## Scope and omissions

**This node covers** the relay-wide (community-wide) membership capability:
the `relay_members` roster and its `owner`/`admin`/`member` role model; the
NIP-43 admin commands that add, remove, and re-role a member (kinds 9030-9032)
and their permission matrix; the relay-signed membership-snapshot and
delta-announcement events (kinds 13534, 8000, 8001); the voluntary leave
request (kind 28936); the open-vs-closed-relay enforcement flag
(`require_relay_membership`) and its NIP-OA owner-delegation fallback; the
use-limited v2 invite mint/claim path and its join-policy-acceptance evidence;
single-owner-per-community bootstrap and capped ownership transfer; and the
desktop Settings UI that exercises all of the above.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the roster and its enforcement are built (containers/components) | not yet in this corpus (architecture template family) |
| The Nostr admin-event and HTTP invite interface contracts | not yet in this corpus (interface template family) |
| The step-by-step add-member / invite-claim flow | not yet in this corpus (flow template family) |
| NIP-29 per-channel membership (`channel_members`, kind:39002) | a separate capability, not yet in this corpus |
| Kind:9033 workspace-profile/icon behavior | out of scope for this node (see *Boundary*) |
| NIP-OA owner-delegation attestation format | `architecture-flows-websocket-authentication`'s own scope note |
| Deployment-time owner bootstrapping procedure | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- Whether the `#[ignore]`-gated Postgres tests in `crates/buzz-db/src/relay_members.rs`
  and `crates/buzz-db/src/relay_invite.rs` (including
  `membership_is_confined_to_its_community` and the invite-claim concurrency
  tests) currently pass against the recorded revision — this task did not
  stand up a live Postgres instance to run them.
- Whether an HTTP admin endpoint for listing or bulk-managing `relay_members`
  exists beyond the invite mint/claim routes; a targeted read of
  `crates/buzz-relay/src/api/admin/mod.rs` and `crates/buzz-relay/src/api/invites.rs`
  found none, but this was not an exhaustive audit of every route registered
  in `crates/buzz-relay/src/router.rs`.
- Whether the mobile-app gap noted above (no located implementation) reflects
  a deliberate product scoping decision or simply unbuilt work; only the
  absence of code was established, not the reason for it.
