---
id: capabilities-invites-invite
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "buzz-core declares a NIP-29 event kind for creating a group invite, KIND_NIP29_CREATE_INVITE = 9009, but buzz-relay's side-effect dispatcher routes kind 9009 to a no-op that only logs a warning that the handler is deferred to a future phase -- this kind is not the mechanism the shipped invite capability uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:346-347"
      - "crates/buzz-relay/src/handlers/side_effects.rs:207-213"
  - statement: "The shipped invite capability is a bespoke HTTP mint/claim API living outside the Nostr event data plane: POST /api/invites mints a code and POST /api/invites/claim redeems one, both routed in buzz-relay's router to handlers in crates/buzz-relay/src/api/invites.rs, whose module doc states both routes are NIP-98 signed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:106-123"
      - "crates/buzz-relay/src/api/invites.rs:1-13"
  - statement: "Minting an invite (POST /api/invites) is authorized only for a caller holding the owner or admin role in the tenant community, mirroring the authorization used by the kind:9030 admin add-member command, and the handler rejects any other role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:276-298"
  - statement: "Claiming an invite (POST /api/invites/claim) is deliberately exempt from the relay's membership gate, because the caller is by definition not yet a member; the code's HMAC or database record substitutes for that gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:1-13"
  - statement: "The capability has shipped in two code-format generations. The v1 format is a stateless, HMAC-signed payload (community id, role, expiry, nonce) keyed from the relay's own signing secret, requiring no server-side invite storage; its own module doc states codes are multi-use until expiry, community-scoped, and role-capped at member, with revocation limited to rotating the relay keypair or removing the member after the fact."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/invite_token.rs:1-39"
  - statement: "The v2 format is an opaque database-backed code -- the literal prefix \"v2.\" followed by the unpadded base64url encoding of a 32-byte random secret -- with TTL bounds of 60 seconds minimum, 72 hours default, and 30 days maximum, and a maximum of 10,000 uses; buzz-core hashes the complete code with SHA-256 before it is ever persisted."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/invite.rs:11-56"
  - statement: "v2 invites are persisted in a relay_invites table keyed by (community_id, id), storing only the 32-byte SHA-256 token_hash and never the bearer secret itself, with max_uses, use_count, expires_at and created_by columns, a UNIQUE constraint on (community_id, token_hash) that prevents cross-tenant hash collisions, and a CHECK that use_count never exceeds max_uses; role is pinned to the literal 'member' at the schema level, so an invite link can never mint an admin."
    entry_class: FACT
    evidence:
      - "migrations/0025_relay_invites.sql"
  - statement: "buzz-db implements the v2 lifecycle as mint_relay_invite, claim_relay_invite and reap_expired_relay_invites, with claim_relay_invite returning a typed ClaimOutcome distinguishing Joined, AlreadyMember (idempotent re-claim by an existing member), Expired, Exhausted and Invalid rather than a single boolean."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_invite.rs:35-57"
      - "crates/buzz-db/src/store/relay_invite.rs:99-146"
      - "crates/buzz-db/src/store/relay_invite.rs:174-191"
      - "crates/buzz-db/src/store/relay_invite.rs:212-382"
  - statement: "The desktop app exposes both halves of the capability: InviteLinkSection and CommunityInviteDialog let an owner/admin mint and copy an invite link, while InviteRedeemForm (backed by the useClaimInvite hook and a shared invites API client) lets a joining user redeem one, including a join-policy consent step before the claim is submitted."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/invites.ts"
      - "desktop/src/features/community-members/ui/InviteLinkSection.tsx"
      - "desktop/src/features/community-members/ui/CommunityInviteDialog.tsx"
      - "desktop/src/features/onboarding/ui/InviteRedeemForm.tsx"
  - statement: "The mobile app exposes the same two halves against the same HTTP API: invite_create_page.dart (with its invite_link_section.dart and person_invite_section.dart parts) mints and shares invites, and invite_join_sheet.dart presents a bottom sheet that redeems one, including deep-link parsing for buzz://join and https://<relay>/invite/<code> forms."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/invites/invite_create_page.dart"
      - "mobile/lib/features/invites/invite_join_sheet.dart"
      - "mobile/lib/shared/deeplink/deep_link.dart"
  - statement: "The capability's HTTP mint/claim/landing-page/deep-link surface shipped as PR #1668 ('feat: relay invite links (mint + claim + landing page + deep link)'), and use-limited (v2, max_uses-bearing) invites were added afterward as PR #3141 ('feat(invites): add use-limited invite links'), per the repository's recorded CHANGELOG history."
    entry_class: FACT
    evidence:
      - "CHANGELOG.md:1162"
      - "CHANGELOG.md:711"
  - statement: "End-to-end coverage in buzz-test-client exercises minting and claiming to admit a new pubkey, rejecting an invalid code, and enforcing that only an owner or admin may mint -- confirming the capability's core behavior is under test, not merely implemented."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:263"
      - "crates/buzz-test-client/tests/e2e_relay.rs:307"
      - "crates/buzz-test-client/tests/e2e_relay.rs:322"
  - statement: "VISION.md's channel-visibility table describes private channels as 'invite-only' with join 'Invited by member', and guests as 'Invited' -- language that names a channel-scoped membership mechanism (adding a user to one channel/group), not the community-level invite-link capability this node documents. buzz-core defines that separate mechanism as KIND_NIP29_PUT_USER (kind 9000, 'add a user to a group') and RELAY_ADMIN_ADD_MEMBER (kind 9030), both handled by their own side-effect functions distinct from the /api/invites mint/claim handlers."
    entry_class: FACT
    evidence:
      - "VISION.md:38-44"
      - "crates/buzz-core/src/kind.rs:334-335"
      - "crates/buzz-core/src/kind.rs:389"
      - "crates/buzz-relay/src/handlers/side_effects.rs:201"
  - statement: "buzz-cli has no invite-related subcommand; a repository-wide search of every .rs file under crates/buzz-cli for the case-insensitive string 'invite' returns only one unrelated hit, an English-language code comment using the word as a verb, not an invite feature."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('invite', path='crates/buzz-cli/**/*.rs') -> one hit, crates/buzz-cli/src/client.rs:228, unrelated verb usage; no invite subcommand exists"
---

# Invite: capability

Buzz lets a community owner or admin mint a shareable invite link that a
person who is not yet a member can redeem, over HTTP, to join that community
without needing an existing member to add them one at a time. The link
carries an opaque code; redeeming it proves control of the joining Nostr
keypair (via NIP-98) and, once accepted, seats the new pubkey as a `member`
of the community. This is the mechanism behind "share a link to bring someone
into this community" across the desktop app, the mobile app, and the relay's
own web landing page for a bare `/invite/<code>` link.

## Maturity

**Shipped.** The mint/claim HTTP surface, its landing page, and deep-link
handoff shipped as PR #1668 ("feat: relay invite links (mint + claim +
landing page + deep link)"). A second generation of durable, use-limited
codes (a maximum number of redemptions per link, backed by a database table
rather than a stateless signature) shipped afterward as PR #3141
("feat(invites): add use-limited invite links"). Both desktop
(`InviteLinkSection`, `InviteRedeemForm`) and mobile
(`invite_create_page.dart`, `invite_join_sheet.dart`) ship UI for both
halves of the capability today, and `crates/buzz-test-client/tests/e2e_relay.rs`
exercises the mint-then-claim path, invalid-code rejection, and the
owner/admin-only mint authorization end to end.

A related but separate NIP-29 event kind, `KIND_NIP29_CREATE_INVITE`
(kind 9009), exists in `buzz-core`'s kind registry but is **not** the
mechanism above -- its side-effect handler is a stub that only logs that the
handler is "deferred to future phase" and takes no action. Nothing in the
product today creates or consumes a kind:9009 event as an invite.

## Boundary

This node does not describe:
- **How the capability is built.** The relay's HTTP handlers, the two code
  formats (stateless HMAC v1, database-backed opaque v2), and the
  `relay_invites` table are implementation detail behind this capability, not
  its own subject matter here -- no architecture node exists yet for this
  container/component to `references`, so those details are cited above as
  evidence of the capability's existence and maturity, not restated as this
  node's own content.
- **The interface contract the capability is exposed through.** `POST
  /api/invites` and `POST /api/invites/claim` are the concrete HTTP contract;
  no interface-family corpus node exists yet to own that contract, so this
  node cites the route declarations as maturity evidence rather than
  documenting request/response shapes itself.
- **The step-by-step flow through this capability.** How an invite expires
  (trigger, preconditions, outcome) and how a claim is processed
  (ordered interactions, failure/rollback behavior) are the subject of the
  sibling flow tasks for `capabilities/invites/invite-expiry.md` and
  `capabilities/invites/invite-redemption.md`. Neither sibling node is merged
  to `origin/launchpad` at this revision, so no `relationships` edge to
  either is declared below -- see *Relationships*.
- **The invite code as a data entity.** The opaque v2 code's exact encoding,
  hashing and validation contract is `capabilities/invites/invite-token.md`'s
  subject, not restated here beyond what is needed to establish this
  capability's maturity. That sibling is also unmerged at this revision.
- **The unrelated channel-membership "invite" mechanism.** VISION.md's
  channel-visibility table calls private-channel joining "invite-only" and
  guest access "Invited" -- that is `KIND_NIP29_PUT_USER` (kind 9000, add a
  user to one channel/group) and `RELAY_ADMIN_ADD_MEMBER` (kind 9030), a
  channel- or role-scoped membership action distinct from the community-level
  invite link this node documents. The two share the English word "invite"
  and nothing else in their implementation.
- **How the running system is operated** (deployment, monitoring, incident
  response for the relay this capability runs on) -- the `operations`
  corpus surface's territory, not this node's.

## Relationships

**Declared: none.** `AGENTS.md` requires every declared `relationships[].target`
to resolve against `origin/launchpad`'s own corpus tree, not the author's
worktree, and at this revision that tree contains no `capabilities/**` node
at all -- this is the first one. The natural future edges are `references`
toward an architecture node for the relay's invite handlers (once one exists),
`references` toward an interface node for the `/api/invites` route group
(once `#1342`'s family lands an instance), and `part-of`/sibling cross-links
to `invite-expiry`, `invite-redemption` and `invite-token` once those three
sibling documents merge. None of the three exists in `origin/launchpad` at
this revision, so declaring any of those edges now would be a hard validation
error the moment this node's own PR runs `validate.py` against a branch that
does not yet contain them.

## Scope and omissions

**This node covers** what the invite capability is, at the level a product
stakeholder recognizes it -- mint a link, share it, someone redeems it and
becomes a community member -- its current maturity, the two code-format
generations that realize it, its client surfaces on desktop and mobile, and
the boundary separating it from the unrelated channel-membership "invite"
language in VISION.md and from the deferred, unused NIP-29 kind:9009.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Invite expiry: trigger, preconditions, outcome | `capabilities/invites/invite-expiry.md` (issue #759, not yet merged) |
| Invite redemption: ordered interactions, failure/rollback | `capabilities/invites/invite-redemption.md` (issue #760, not yet merged) |
| The invite code as a data entity (encoding, hashing, validation contract) | `capabilities/invites/invite-token.md` (issue #761, not yet merged) |
| How the capability is built (containers, components) | a future architecture node; none exists yet |
| The HTTP interface contract itself | a future interface node; none exists yet |
| The unrelated channel-membership "invite" mechanism (kind 9000/9030) | out of scope for this capability entirely; not tracked by any cited sibling task |

**Expected but not verified when this node was written:**
- **No relay-side revocation of a single outstanding v1 (HMAC) code exists**
  beyond rotating the relay's own signing key or removing the member after
  the fact -- stated directly by `invite_token.rs`'s own module doc, but not
  independently confirmed against a test that attempts single-code
  revocation and fails.
- **buzz-cli has no invite subcommand.** Confirmed by a repository-wide
  search returning no feature-shaped hits, but not confirmed by reading
  every line of every file under `crates/buzz-cli` -- a subcommand named
  without the literal substring "invite" would not have surfaced.
- **Whether `KIND_NIP29_CREATE_INVITE` (kind 9009) is planned to ever become
  functional**, or is dead code awaiting removal, was not established --
  the side-effect handler's own log message says "deferred to future phase"
  but no linked issue or roadmap entry for that phase was found or cited
  here.
