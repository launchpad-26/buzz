---
id: layers-authorization-authorization
type: layers
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
  - statement: "buzz-auth verifies a caller's identity through two independent event-signature paths -- a NIP-42 AUTH event for WebSocket connections, checked by `verify_nip42_event` for signature, challenge, relay URL and a ±60s timestamp window, and a NIP-98 HTTP Auth event (kind:27235) for HTTP requests, checked by `verify_nip98_event` -- and this identity check is prior to and separate from every authorization decision described in this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "An authenticated connection or API token carries a set of `Scope` values (for example `MessagesRead`, `MessagesWrite`, `ChannelsWrite`, `AdminChannels`, `AdminUsers`) drawn from a closed enum with an `Unknown(String)` forward-compatibility fallback, and `require_scope` rejects an operation whose required scope is absent from that set with `AuthError::InsufficientScope`."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
      - "crates/buzz-auth/src/error.rs"
  - statement: "`check_read_access` and `check_write_access` in buzz-auth compose a scope check with a channel-membership check behind one call: both require the caller's scope set to contain the relevant scope AND the caller to be a member of the target channel inside the request's own tenant context, resolved through the `ChannelAccessChecker` trait's `can_access`/`accessible_channel_ids` methods."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
  - statement: "`ChannelAccessChecker`'s own doc comment states every method takes `&TenantContext` because the frozen schema's `channels` primary key is `(community_id, id)`, so a channel UUID is not globally unique, and requires every implementation to scope its query by `ctx.community()` so that membership can never be evaluated against the wrong community -- named in the source as the 'S1 cross-community fence at the access layer.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
  - statement: "The corpus already carries a merged node, `architecture-principles-community-is-security-boundary`, documenting that every request's community is bound exactly once from the connection's Host header before any handler observes tenant data, and that no client-supplied signal may override it; every layer this node describes operates only after that binding has already happened and inside the community it produced."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "Community-level membership and role are one row per `(community_id, pubkey)` in the `relay_members` table, with `role` constrained by a CHECK constraint to exactly `'owner'`, `'admin'` or `'member'`; the table's owning module doc comment names this NIP-43 relay-level membership and states every read, write and list is bound to a single `community_id` so that admission to one community can never admit a pubkey to another."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:574-584"
      - "crates/buzz-db/src/relay_members.rs"
  - statement: "Channel-level membership and role are a separate row per `(community_id, channel_id, pubkey)` in the `channel_members` table, foreign-keyed to `channels (community_id, id)`, with its own `role` column of Postgres enum type `member_role` defaulting to `'member'` -- a structurally distinct membership record from `relay_members`, keyed to a channel rather than the whole community."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:132-148"
  - statement: "The channel-level role vocabulary is `MemberRole` in buzz-core -- Owner, Admin, Member, Guest, and a separate Bot designation not part of the linear hierarchy -- whose doc comment states the hierarchy as 'Owner > Admin > Member > Guest' and whose `permission_level`/`has_at_least` methods are the numeric comparison buzz-relay code is documented to use for authorization checks, with Bot fixed at permission level 0 so it never satisfies any non-Bot requirement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/channel.rs"
  - statement: "`check_channel_membership` in buzz-relay's ingest handler is the read/write gate a message-sending or message-reading request passes through: it checks `is_member_cached(tenant.community(), channel_id, pubkey)` first, and only if that is false falls back to allowing the request when the channel's own `visibility` is `'open'` -- so channel membership and channel visibility (open vs. private, `ChannelVisibility` in buzz-core) are two different, composed conditions, not one."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:650-676"
      - "crates/buzz-core/src/channel.rs"
  - statement: "Above channel membership and channel role, `authorize_moderation_action` in buzz-relay decides a third, action-specific authorization question -- whether `actor` may perform a named `ModerationAction` (DeleteMessage, Kick, Ban, Unban, Timeout, Untimeout, ResolveReport, ViewQueue) against a target -- by first checking the actor's community-level `relay_members` role (owner or admin of the whole community are authorized for every action in any of that community's channels) and only falling back to the actor's channel-level role (channel owner/admin) for the two channel-local actions, DeleteMessage and Kick, when community authority does not apply."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "`authorize_moderation_action`'s own doc comment states a guard rail as part of this same decision: an actor holding the community `admin` role cannot Ban or Timeout the community `owner` or a fellow `admin` -- only the `owner` may action an `admin` -- and its test suite (`admin_cannot_ban_or_timeout_owner_or_fellow_admin`, `admin_guard_rail_is_scoped_to_ban_and_timeout`) exercises exactly that restriction, separately from the plain role-hierarchy checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "Which incoming event kinds route through the moderation-action authorization layer at all is itself a closed, named check: `is_moderation_command_kind` in buzz-core matches only the five moderation-command kind constants (ban, unban, timeout, untimeout, resolve-report), so an event's `kind` value is the dispatch key that decides whether `authorize_moderation_action`'s decision applies to it in the first place."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:376-384"
  - statement: "A structurally separate per-event visibility mechanism also exists and is keyed by kind: `is_shared_gated_kind`/`is_unshared_gated_event` in buzz-core withhold a shared-gated event from a reader who is not its author and for which the event does not carry a `[\"shared\", \"true\"]` tag -- this decides whether a specific event is visible to a specific reader, which is a narrower and different question from whether a caller may perform a named action, and this node does not describe its rules further."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:219-240"
  - statement: "buzz-auth's own unit test suite for the scope-plus-membership composition includes `read_access_denied_by_scope`, `read_access_denied_by_membership`, `read_access_granted` and `access_does_not_cross_communities`, and buzz-relay's `moderation_authz.rs` test suite separately covers the community-role and channel-role composition, including `community_owner_authorized_for_everything`, `community_admin_authorized_against_non_privileged_targets`, `admin_cannot_ban_or_timeout_owner_or_fellow_admin` and `channel_role_covers_only_delete_and_kick`; these are unit tests exercising the pure decision logic (`decide_authority`) and the in-memory `MockAccessChecker`, not an end-to-end integration or E2E run against a live relay, which this node did not execute while being authored."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "Because each of the four layers below the community boundary (community membership/role, channel membership, channel role, action-specific authorization) is backed by its own table or its own dedicated decision function rather than one shared check, a caller's overall permission for a given request is the composition of independently-evaluated layers rather than a single flat lookup -- read directly from the four distinct code paths cited above rather than derived from any single source that states the composition as a rule."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/access.rs"
      - "crates/buzz-db/src/relay_members.rs"
      - "migrations/0001_initial_schema.sql:132-148"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
    confidence: 0.75
  - statement: "Issue #1031 requires this node to represent the shared shape and contract of authorization across the subtree rather than duplicate the canonical content of its sibling documents (channel-membership, channel-roles, community-membership, event-authorization), and to reference those siblings by their expected node id only after checking that their files do not yet exist, rather than assuming they do."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1031 definition of done, and its dispatching task brief"
  - statement: "At the checked revision, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no file under `launchpad/docs/corpus/layers/`, and issues #1032 (channel-membership), #1033 (channel-roles), #1034 (community-membership) and #1035 (event-authorization) -- the four sibling document tasks named in issue #1031 -- are each open with no corresponding file in that listing, so none of their expected ids (`layers-authorization-channel-membership`, `layers-authorization-channel-roles`, `layers-authorization-community-membership`, `layers-authorization-event-authorization`, following this node's own `layers-authorization-authorization` naming pattern) resolves to a loaded node yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, standards/**, templates/**; no layers/ directory present; run at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "gh_issue_list(repo='launchpad-26/buzz', search='layers/authorization in:title') -> #1032, #1033, #1034, #1035, #1031 all state:open"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Authorization

## Definition

**Authorization** is the relay's decision, on every request from an already-authenticated
caller inside an already-bound community, of what that caller is permitted to do — a
decision built from several independently-checked layers (which scope the request
carries, whether the caller belongs to the community, whether the caller belongs to the
target channel, what role the caller holds at each of those two levels, and whether the
specific action the request names is one that role is allowed to take) rather than one
flat permission check.

This node is the category-level overview for that whole layered decision. It states the
shape shared across every layer and the order they compose in; it does not restate any
one layer's own rules in detail. Each layer's specifics belong to its own sibling node —
see *Scope: what this node covers, and what it defers* below.

## Not to be confused with

**Authentication** (verifying *who* the caller is) is a separate, prior concern. buzz-auth
verifies identity through two independent signed-event paths — a NIP-42 `AUTH` event for
WebSocket connections and a NIP-98 HTTP Auth event (kind:27235) for HTTP requests — and
every authorization decision described here assumes that check has already produced a
pubkey and a set of granted `Scope` values before it runs. This node does not describe
how that identity check works.

**Community binding** (deciding *which* community a request belongs to, from the
connection's Host header) is also a separate, prior concern, and is already the subject of
a merged corpus node, `architecture-principles-community-is-security-boundary`. That node
documents that a community is bound exactly once, fails closed, and cannot be overridden
by any client-supplied signal. Every layer below in this node runs only after that binding
has already happened and only inside the community it produced; this node does not
restate that principle's content, only depends on it.

## Scope: what this node covers, and what it defers

**Covers:** the shared shape of authorization across the whole subtree — the layers that
exist, the order they are checked in, what each layer's own table or decision function is
(named, not explained in full), and how the layers compose into one overall decision for
a request.

**Defers, by design, to a sibling node this task does not create:**

| Layer | What it decides | Deferred to |
|---|---|---|
| Community membership and role | Whether the caller belongs to the community at all, and whether their role there is `owner`, `admin` or plain `member` | expected id `layers-authorization-community-membership` (issue #1034) |
| Channel membership | Whether the caller belongs to a specific channel, and how that interacts with a channel's `open`/`private` visibility | expected id `layers-authorization-channel-membership` (issue #1032) |
| Channel role | The `Owner`/`Admin`/`Member`/`Guest`/`Bot` hierarchy within one channel and how it is compared numerically | expected id `layers-authorization-channel-roles` (issue #1033) |
| Action-specific (event-level) authorization | How a specific action — deleting a message, kicking, banning, timing out, resolving a report — is authorized against the composed membership/role state above | expected id `layers-authorization-event-authorization` (issue #1035) |

None of those four files exists in the corpus at the revision this node was checked
against — confirmed directly (see the evidence ledger) rather than assumed, per this
corpus's own warning that "nothing to point at" stops being true the moment a sibling
merges. Because none exists yet, this node names each by its expected id and issue number
in prose only; it declares no `relationships` edge to any of them, since a
`relationships[].target` naming an id no node carries is a hard validation error. Adding
those edges is a follow-up once each sibling lands.

**Does not cover:** authentication (see *Not to be confused with*), the community-boundary
principle itself (already documented, referenced not restated), scope enforcement's own
full contract (`buzz-auth`'s `Scope` enum and `require_scope` are named below only as the
first layer in the chain), and the per-event *visibility* gate (`is_shared_gated_kind` /
`is_unshared_gated_event`) — which decides whether one specific event is shown to one
specific reader, a different and narrower question from whether an actor may perform a
named action, and is named below only to distinguish it from the layers this node does
describe.

## The layered shape

Five checks compose, in this order, before a request is fully authorized. The first two
are prerequisites this node depends on rather than owns; the remaining three are this
subtree's own subject, detailed by the sibling nodes above.

1. **Identity and scope.** `buzz-auth` verifies the signed AUTH/HTTP-Auth event and
   attaches a set of `Scope` values (for example `MessagesRead`, `MessagesWrite`,
   `AdminChannels`) to the connection or API token. `require_scope` rejects a request
   outright if its required scope is missing, before any membership check runs.
2. **Community binding.** The request's community is resolved once, from the Host header,
   fail-closed — the security boundary every later layer operates inside. Not this node's
   subject; see `architecture-principles-community-is-security-boundary`.
3. **Community membership and role.** One row per `(community_id, pubkey)` in
   `relay_members`, role `owner`/`admin`/`member`. A community `owner` or `admin` carries
   authority across every channel in that community for the moderation actions layer 5
   checks. Full treatment: the community-membership sibling.
4. **Channel membership and role.** A separate row per `(community_id, channel_id,
   pubkey)` in `channel_members`, with its own `role` (`Owner`/`Admin`/`Member`/`Guest`/
   `Bot`, `MemberRole` in `buzz-core`). `check_channel_membership` is the read/write gate:
   member of the channel, OR the channel is `open`. Full treatment: the
   channel-membership and channel-roles siblings.
5. **Action-specific authorization.** For actions narrower than plain read/write —
   deleting a message, kicking, banning, timing out, resolving a report —
   `authorize_moderation_action` composes layers 3 and 4: a community `owner`/`admin` is
   authorized for every such action anywhere in their community; a channel `owner`/`admin`
   is authorized only for the two channel-local actions (delete, kick) within their own
   channel; a plain member or a stranger is authorized for none of them. A guard rail on
   top of that composition: a community `admin` cannot Ban or Timeout the community
   `owner` or a fellow `admin` — only the `owner` can action an `admin`. Which incoming
   event kinds are even routed through this layer is itself a closed, named check
   (`is_moderation_command_kind`). Full treatment: the event-authorization sibling.

## Why layered, not flat

Each layer below the community boundary is backed by its own storage (a distinct table)
or its own decision function, rather than all four being facets of one shared check. A
request's overall permission is therefore the *composition* of independently-evaluated
layers — scope, then community role, then channel membership, then channel role, then
(where relevant) the action-specific guard rail — not a single flat lookup that could be
satisfied or denied by one row. This is read directly from the four separate code paths
cited in the evidence ledger, not asserted from a single source that states the
composition as a design rule; treat it as reasoned from the code rather than as something
any one document declares.

## Enforcement points

| Point | Layer | What it does |
|---|---|---|
| `require_scope`, `check_read_access`, `check_write_access` (`crates/buzz-auth/src/access.rs`) | 1, 4 | Rejects a request whose scope set lacks the required scope, or whose caller is not a channel member (composed with the channel's own open/private visibility via `ChannelAccessChecker`). |
| `relay_members` table + `crates/buzz-db/src/relay_members.rs` | 3 | Community-scoped membership and role (`owner`/`admin`/`member`), keyed `(community_id, pubkey)`. |
| `channel_members` table + `MemberRole` (`crates/buzz-core/src/channel.rs`) | 4 | Channel-scoped membership and role (`Owner`/`Admin`/`Member`/`Guest`/`Bot`), keyed `(community_id, channel_id, pubkey)`. |
| `check_channel_membership` (`crates/buzz-relay/src/handlers/ingest.rs`) | 4 | The read/write gate: member of the channel, or the channel is `open`. |
| `authorize_moderation_action` / `decide_authority` (`crates/buzz-relay/src/handlers/moderation_authz.rs`) | 3 + 4 → 5 | Composes community role and channel role into one decision per named `ModerationAction`, including the admin-cannot-action-owner-or-fellow-admin guard rail. |
| `is_moderation_command_kind` (`crates/buzz-core/src/kind.rs`) | 5 (dispatch) | Names the five event kinds that route through the action-specific authorization layer at all. |

## Verification

Two unit-test suites exercise this composition directly, without infrastructure:
`crates/buzz-auth/src/access.rs`'s own tests (`read_access_denied_by_scope`,
`read_access_denied_by_membership`, `read_access_granted`,
`access_does_not_cross_communities`) cover layers 1 and 4 composed together against an
in-memory `MockAccessChecker`; `crates/buzz-relay/src/handlers/moderation_authz.rs`'s own
tests (`community_owner_authorized_for_everything`,
`community_admin_authorized_against_non_privileged_targets`,
`admin_cannot_ban_or_timeout_owner_or_fellow_admin`,
`channel_role_covers_only_delete_and_kick`, `plain_channel_member_and_stranger_are_denied`)
cover layers 3, 4 and 5 composed together against `decide_authority`'s pure decision logic.

**These are unit tests against pure decision functions and an in-memory mock, not an
end-to-end run against a live relay.** No integration or E2E suite exercising this full
composition end-to-end (a real request, a real Postgres-backed `relay_members`/
`channel_members` pair, a real response) was found or run while authoring this node —
whether one exists is left to whichever sibling node (most likely the
event-authorization or channel-roles node) is positioned to verify it.

## Scope and omissions

**This node covers** the definition of authorization as this system uses the term, its
boundary against authentication and against the already-documented community boundary,
the five-layer shape the whole subtree composes, the enforcement point for each layer,
and what unit-level verification exists for the composition.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Full community-membership semantics (join policies, invites, bans, the `relay_members` role contract in depth) | expected id `layers-authorization-community-membership`, issue #1034 |
| Full channel-membership semantics (join/invite, visibility interaction, removal) | expected id `layers-authorization-channel-membership`, issue #1032 |
| Full channel-role semantics (`MemberRole`'s hierarchy, `permission_level`, `Bot`'s special case, elevation rules) | expected id `layers-authorization-channel-roles`, issue #1033 |
| Full action-specific/event-level authorization (the complete `ModerationAction` grid, the guard rails, kind-level dispatch) | expected id `layers-authorization-event-authorization`, issue #1035 |
| The community-boundary principle itself | `architecture-principles-community-is-security-boundary` (already merged; referenced, not restated) |
| Authentication (NIP-42, NIP-98, replay prevention) | Not this subtree's subject |
| The per-event visibility gate (`is_shared_gated_kind`/`is_unshared_gated_event`) | Named only to distinguish it from action authorization; not otherwise described here |

**No `relationships` edge to any of the four sibling documents.** Checked directly before
finalizing front matter (`git fetch origin launchpad && git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus`, at the revision this node's provenance entry
records): none of `layers-authorization-community-membership`,
`layers-authorization-channel-membership`, `layers-authorization-channel-roles` or
`layers-authorization-event-authorization` is a loaded node, so a `relationships[].target`
naming any of them would be a hard validation error. Each is instead named by its expected
id and issue number in prose, in the table above. **One edge is declared:**
`references` → `architecture-principles-community-is-security-boundary`, which is loaded
on `origin/launchpad` at the checked revision and is a real dependency — every layer this
node describes runs only inside the boundary that node documents.

**Expected but not verified when this node was written:**

- **No end-to-end or integration test of the full five-layer composition was found or
  run.** See *Verification* above — everything cited there is unit-level.
- **Whether every request-handling surface in `buzz-relay` actually calls these
  enforcement points, versus a surface that bypasses one, was not audited.** This node
  verified the enforcement points exist and what they individually do; it did not
  enumerate every call site the way the community-boundary node's own ledger did for its
  narrower binding question.
- **The `Guest` and `Bot` channel roles' exact treatment across every action** — this
  node names their existence in `MemberRole` but leaves their full behavior to the
  channel-roles sibling, which was not yet available to verify against.
- **Whether a client-facing document (an API reference, an error-code table) states this
  same five-layer shape anywhere else in the repository was not searched for**; if one
  exists, a future edit should link it rather than let this node be the only place the
  shape is stated.
