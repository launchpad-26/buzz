---
id: layers-authorization-channel-roles
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
  - statement: "`MemberRole` is a five-variant enum — Owner, Admin, Member, Guest, Bot — defined once in `buzz-core`, with a doc comment stating the hierarchy is 'Owner > Admin > Member > Guest' and that 'Bot is a separate designation — it is not part of the linear hierarchy.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:102-119"
  - statement: "`MemberRole::permission_level` assigns Owner=4, Admin=3, Member=2, Guest=1, Bot=0, and its doc comment states 'Bot returns 0 (must use explicit grants)' and that callers should compare with `role.permission_level() >= required.permission_level()`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:138-150"
  - statement: "`MemberRole::has_at_least` implements that comparison directly (`self.permission_level() >= required.permission_level()`), and its own doc comment states 'Bot never meets any requirement (returns false for all non-Bot requirements)' — since Bot's permission level (0) is lower than every other role's, including Guest (1)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:152-157"
  - statement: "`MemberRole::is_elevated` returns true only for Owner and Admin, with a doc comment describing elevated roles as 'Elevated roles that only existing owners/admins may grant.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs:133-136"
  - statement: "The Postgres schema defines `CREATE TYPE member_role AS ENUM ('owner', 'admin', 'member', 'guest', 'bot')` and the `channel_members.role` column uses that enum with `DEFAULT 'member'` — the same five values, same order, as `MemberRole::as_str()`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:30"
      - "migrations/0001_initial_schema.sql:136"
      - "crates/buzz-core/src/channel.rs:122-131"
  - statement: "`buzz-db`'s channel module does not define its own role type; it re-exports the canonical one directly: `pub use buzz_core::channel::{ChannelType, ChannelVisibility, MemberRole};`. Every `buzz_db::channel::MemberRole` reference elsewhere in the codebase (e.g. `buzz-relay`'s handlers) resolves to this same `buzz-core` type, not a second, independent role type."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/channel.rs:17"
  - statement: "For kind:9000 (PUT_USER) on a private channel, the relay's `validate_admin_event` requires the actor to already be an active member, and separately rejects the request with 'only owners/admins may grant elevated roles' when the requested role `is_elevated()` and the actor's own role does not."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:365-381"
  - statement: "Still within kind:9000, changing an *existing active* member's role (in either direction — promotion or demotion) requires the actor's role to be elevated, and separately blocks demoting the channel's last remaining owner ('cannot demote the last owner — transfer ownership first') unless a role transfer accompanies it, counted only among members with `removed_at IS NULL`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:383-414"
  - statement: "For kind:9001 (REMOVE_USER), removing someone other than oneself requires the actor's stored role to be `\"owner\"` or `\"admin\"` (string comparison against the DB-stored role, not the `MemberRole` enum directly), or — for a bot target — that the actor owns that bot agent; a self-removal by the sole remaining owner is rejected with 'cannot remove the last owner.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:452-494"
  - statement: "For kind:9002 (EDIT_METADATA), the `name`, `about`, `archived`, `visibility`, and `ttl` tags require the actor to hold `\"owner\"` or `\"admin\"` (or be the owning human of an active owner-role agent in the channel); the `topic` and `purpose` tags require only active channel membership, with an explicit inline comment noting this diverges intentionally from kind:9001's stricter check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:592-636"
  - statement: "`buzz-core`'s git-permission module states its own model in its module doc comment: 'The permission model: channel role = repo role; `buzz-protect` tags on kind:30617 add constraints that apply to everyone (including the owner).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs:1-5"
  - statement: "`default_min_role` (used when no `buzz-protect` tag matches a ref) requires `MemberRole::Member` to create or fast-forward-push a branch, and `MemberRole::Admin` for a non-fast-forward push, a delete, or any tag create/move — reusing the exact same `MemberRole` type and `permission_level` ordering that gates the NIP-29 admin kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs:427-452"
  - statement: "Parsing a `push:<role>` protection-rule token explicitly rejects Bot and Guest as a configurable minimum role, with inline comments giving each its own reason: 'Bot is promoted to Member at the policy layer; push:bot is meaningless' and 'Guest cannot push regardless; push:guest would be confusing.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs:343-352"
  - statement: "The relay's git pre-receive hook callback (`crates/buzz-relay/src/api/git/policy.rs`) explicitly promotes `MemberRole::Bot` to `MemberRole::Member` before evaluating push permissions — `let git_role = match role { MemberRole::Bot => MemberRole::Member, other => other };` — and its own module doc comment states this promotion is 'scoped to this module; the core `MemberRole::Bot` hierarchy is unchanged,' and that 'Bot is a designation (what it is), not a permission tier (what it can do).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs:1-20"
      - "crates/buzz-relay/src/api/git/policy.rs:403-409"
  - statement: "A separate table, `relay_members`, stores a differently-scoped role — `role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member'))`, community-scoped rather than channel-scoped, documented in its own migration comment as 'Conformance: membership gate, community-scoped' for NIP-43. It has only three values (no guest, no bot) and is a distinct concept from channel-level `MemberRole`, not an alternate serialization of it."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:568-580"
  - statement: "Channel-level role authorization (this node's subject) and community-level tenant/request boundary enforcement (`architecture/principles/community-is-security-boundary.md`, `architecture/principles/fail-closed-boundaries.md`) are two different layers of the same authorization stack rather than the same mechanism described twice — the community boundary is resolved once per connection from the Host header before any handler runs, while `MemberRole` is looked up per channel, per action, after the community is already bound."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/git_perms.rs:1-5"
      - "crates/buzz-relay/src/handlers/side_effects.rs:309-341"
    confidence: 0.75
  - statement: "Issue #1033's Definition of Done requires the document to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts and implementation/verification without duplicating them, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1033 definition of done"
---

# Channel Roles

A channel role is the per-channel, per-member authorization level Buzz uses to decide
whether a specific action inside a specific channel is allowed. It is the mechanism
`buzz-relay` and `buzz-core`'s git-permission logic both consult before letting a
NIP-29 admin action or a git push through — not a description of any one endpoint, but
of the shared role vocabulary and comparison rule underneath several of them.

## Definition

**A channel role is a `MemberRole` value — `Owner`, `Admin`, `Member`, `Guest`, or
`Bot` — recorded once per `(channel, pubkey)` pair, that gates what its holder may do
inside that one channel.** `Owner`, `Admin`, `Member`, and `Guest` form a strict linear
hierarchy (`Owner > Admin > Member > Guest`), compared numerically via
`permission_level()` (4/3/2/1) and `has_at_least()`. `Bot` is a fifth value carrying
`permission_level() == 0` and is explicitly *not* part of that hierarchy — it never
satisfies any requirement on its own, including the lowest tier (`Guest`, level 1); a
bot's authorization instead comes from being granted a specific role explicitly, or
from an owning human acting on its behalf (see *Worked example* below).

**What a channel role is not:**

- **Not a community-wide or global permission.** A pubkey can hold different roles in
  different channels within the same community; nothing here describes cross-channel
  or cross-community authority.
- **Not the same thing as `relay_members.role`.** That is a separate, community-scoped
  table (documented in its own migration as a NIP-43 "membership gate") with only three
  values (`owner`, `admin`, `member` — no `guest`, no `bot`). It answers "is this pubkey
  a member of the relay/community at all," a different question from "what can this
  member do inside this one channel."
- **Not the community/tenant security boundary.** Host-based tenant resolution
  (`architecture/principles/community-is-security-boundary.md`,
  `architecture/principles/fail-closed-boundaries.md`) is resolved once per connection,
  before any channel or role is even in scope. Channel roles are the next, narrower
  layer down, evaluated per action once a community is already bound.
- **Not itself an event kind or a wire format.** `MemberRole` is a Rust enum with a
  canonical string form (`as_str()`/`FromStr`) that happens to match a Postgres enum
  and Nostr tag values; the NIP-29 event kinds that carry or consume it are a separate
  subject.

## The role hierarchy

| Role | `permission_level()` | In the linear hierarchy? | Elevated (`is_elevated()`)? |
|---|---|---|---|
| `Owner` | 4 | Yes (top) | Yes |
| `Admin` | 3 | Yes | Yes |
| `Member` | 2 | Yes | No |
| `Guest` | 1 | Yes (bottom) | No |
| `Bot` | 0 | **No** — separate designation | No |

`has_at_least(required)` is `self.permission_level() >= required.permission_level()`.
Because `Bot`'s level (0) is below even `Guest`'s (1), a bot never satisfies *any*
`has_at_least` check against a non-Bot requirement — including the lowest one. A bot's
authorization always has to come from somewhere other than this comparison: an explicit
role grant, or an owning human's own role (see below).

## Use cases

A reader reaches for this document when they need to know **who is allowed to do what
inside a channel** — before adding a new role-gated action, before reviewing one, or
before explaining why a request that "should" have worked was rejected as
`"actor not authorized"`.

Two independent subsystems currently key off the same `MemberRole` type and the same
`permission_level` ordering:

- **NIP-29 channel administration** (`crates/buzz-relay/src/handlers/side_effects.rs`,
  `validate_admin_event`) — membership changes, role changes, metadata edits, and
  message deletion.
- **Git push permissions** (`crates/buzz-core/src/git_perms.rs`) — its own module doc
  comment states the model plainly: *"channel role = repo role."*

## Worked example: role-gated actions

**Granting or changing a role (kind:9000, PUT_USER).** On a private channel, only an
existing active member may act at all. Granting an *elevated* role (`Owner` or
`Admin`) requires the actor's own role to already be elevated. Changing an *existing*
active member's role — promotion or demotion — is privileged in both directions:
non-elevated actors are rejected regardless of which direction the change goes, and
demoting the channel's sole remaining owner is blocked outright ("cannot demote the
last owner — transfer ownership first"), counting only currently-active members
(`removed_at IS NULL`). A self-add is always allowed, bypassing the elevated-actor
check entirely — the gate exists to stop a member from being changed by someone else
without sufficient standing, not to stop someone from joining themselves.

**Removing a member (kind:9001, REMOVE_USER).** Self-removal is allowed unless the
actor is the channel's last owner. Removing someone *else* requires the actor to
already hold `owner` or `admin` — or, for a bot target specifically, that the actor is
the bot's registered owner. A non-member cannot remove anyone, including their own bot;
membership in the channel is checked first, deliberately, before any bot-ownership
shortcut is considered.

**Editing metadata (kind:9002, EDIT_METADATA).** The tag being changed decides which
role is required. `name`, `about`, `archived`, `visibility`, and `ttl` all require
`owner` or `admin` — or, notably, allow the *human* who owns an active owner-role agent
in the channel, even when that human is not themselves a member (an intentional
divergence from kind:9001's stricter membership-first rule). `topic` and `purpose`
require only active membership at any role.

**Git push (`default_min_role`).** The same `MemberRole` ordering reappears outside the
relay's NIP-29 handlers entirely: creating or fast-forwarding a branch requires
`Member`; a non-fast-forward push, a delete, or any tag create/move requires `Admin`. A
channel operator can raise the bar further with a `push:<role>` protection tag; the
parser rejects `Guest` outright ("cannot push regardless") and rejects `Bot` for a
different reason — the relay's git pre-receive hook already promotes `Bot` to `Member`
before evaluating push policy, scoped to that one module only, so `push:bot` would be
meaningless rather than dangerous. This is the one place a role is substituted before
the hierarchy comparison runs: the core `has_at_least`/`permission_level` logic never
changes, and the promotion is a policy-layer decision local to git push, not a
revision of Bot's status everywhere else in this document.

## Comparison

| Role | Typical holder | Can be granted by | Can grant/revoke roles? |
|---|---|---|---|
| `Owner` | Channel creator, or an explicit ownership transfer | Another owner (never self-assigned except at channel creation) | Yes, including demoting/promoting other owners and admins |
| `Admin` | A trusted human or agent operator | An owner or admin | Yes, within the limits above |
| `Member` | An ordinary participant | Any active member (self-add is always allowed) | No |
| `Guest` | A read-only external participant | Any active member | No |
| `Bot` | An automated agent/integration | Any active member, or via channel-add policy | No — and never satisfies a role requirement on its own |

Guest and Bot are the two roles nothing above `Member` protects granting: any active
member may add a guest or an ordinary bot. What separates them is not the hierarchy
(both sit at the bottom, and Bot is not even *in* the hierarchy) but what they are for:
Guest is a human-facing read-only tier inside the linear ordering, while Bot is
deliberately outside it and depends on explicit grants or an owning human's standing.

## Scope and omissions

**This node covers** the `MemberRole` type, its five values and their ordering, the
distinction between the linear hierarchy and Bot's separate status, and one worked
example of the two independent subsystems (NIP-29 channel administration, git push
permissions) that currently gate actions on it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full NIP-29 event-kind catalogue and wire format | A future `interfaces-events` node, not yet written |
| The git-permission protection-rule grammar (`buzz-protect` tags, ref patterns, rule unioning) beyond the single `default_min_role` example above | A future `implementation` node scoped to `crates/buzz-core/src/git_perms.rs`, not yet written |
| Community/tenant-level request authentication and the host-to-community binding that runs before any channel role is evaluated | `architecture/principles/community-is-security-boundary.md`, `architecture/principles/fail-closed-boundaries.md` |
| `relay_members.role`, the separate community-scoped NIP-43 membership gate | Not yet documented as its own corpus node |
| Workflow- or agent-specific authorization built on top of channel roles (e.g. `buzz-workflow`, `buzz-persona`) | Not yet documented as its own corpus node |
| Desktop/mobile client-side enforcement or presentation of role state | Not inspected for this node — see below |

**Expected but not verified when this node was written:**

- **Not every role-gating call site was read in depth.** `validate_admin_event`
  (`side_effects.rs`), `default_min_role`/`push:<role>` parsing (`git_perms.rs`), and
  the Bot-promotion step in the git pre-receive hook (`api/git/policy.rs`) were all
  opened and are cited above. `MemberRole`/`permission_level`/`has_at_least` also
  appear in `crates/buzz-relay/src/audio/handler.rs`, `crates/buzz-relay/src/workflow_sink.rs`,
  and `crates/buzz-relay/src/api/git/transport.rs`; whether those call sites apply the
  same rules described here, or add their own additional gating, was not checked
  claim-by-claim for this node.
- **No relationships to other corpus nodes are declared.** Checked against
  `origin/launchpad`'s corpus tree at authoring time: no existing node's subject is
  channel-scoped role authorization. The two architecture-principle nodes named above
  are the closest topical neighbors and are described in prose (per this node's own
  *Definition* boundary), but declaring a typed `relationships` edge to either would
  overstate the overlap — they describe a different, earlier-evaluated layer, not this
  one's subject. Revisit once a sibling `layers/authorization/*` or
  `interfaces-events` node exists to link against.
- **Whether client-side (desktop/mobile) code independently re-derives or merely
  displays server-decided role state** was not verified — this node is grounded in the
  relay/core enforcement path only, per the issue's own framing.
