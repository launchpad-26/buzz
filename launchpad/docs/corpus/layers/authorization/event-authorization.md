---
id: layers-authorization-event-authorization
type: layers
status: draft
origin: upstream
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
  - statement: "verify_event() checks that an event's id is the correct hash of its own fields and that its sig is a valid Schnorr signature over that id under the key named in its own pubkey field, returning VerificationError::InvalidId or VerificationError::InvalidSignature otherwise; ingest_event_inner runs it (via spawn_blocking, since it is CPU-bound) before any authorization check and rejects the event on failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest_event_inner requires event.pubkey to equal auth.pubkey() (the authenticated principal) for every kind except gift wraps (KIND_GIFT_WRAP), which deliberately use an unrelated ephemeral signing pubkey per NIP-59; a mismatch outside that exception is rejected as IngestError::AuthFailed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "required_scope_for_kind maps an event's kind (and, for kind:9002, a tag on the event itself) to exactly one required Scope; ingest_event_inner rejects the event with IngestError::AuthFailed(\"restricted: insufficient scope...\") unless auth.scopes() contains that required scope, and rejects a kind absent from the match arms outright with \"restricted: unknown event kind\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Two kind categories are carved out of the ordinary scope check with their own extra rule: relay admin kinds (9030-9033) and the NIP-43 leave request (kind carried in KIND_NIP43_LEAVE_REQUEST) are rejected outright when auth.channel_ids() is Some(_) -- a channel-scoped token cannot issue a global relay-admin or leave command even though the kind itself would otherwise pass the ordinary scope check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Scope is a closed-ish enum (MessagesRead/Write, ChannelsRead/Write, AdminChannels, UsersRead/Write, AdminUsers, JobsRead/Write, SubscriptionsRead/Write, FilesRead/Write, ReposRead/Write, plus an Unknown(String) catch-all for forward compatibility) carried on an authenticated connection or API token; the crate's own module doc states that in pure Nostr mode every NIP-42-authenticated connection receives the full scope set and per-channel access is enforced separately, by NIP-29 membership checks, not by scopes."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
  - statement: "IngestAuth is transport-neutral over two authenticated shapes: Nip42 { pubkey, scopes, channel_ids: Option<Vec<Uuid>>, conn_id } for WebSocket connections, and Http { pubkey, scopes, auth_method } for the HTTP bridge (NIP-98 or a dev-mode X-Pubkey header); only the Nip42 variant can carry a token-level channel_ids restriction, and channel_ids() returns None for every Http request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "requires_h_channel_scope(kind) names a fixed set of channel-scoped content kinds (stream messages and their edit/pin/bookmark/schedule/reminder/diff variants, canvas, forum post/vote/comment, most NIP-29 admin kinds except create-group, and huddle lifecycle/guideline kinds); ingest_event_inner rejects such a kind with \"invalid: channel-scoped events must include an h tag\" whenever the derived channel_id is None."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "is_global_only_kind(kind) names a disjoint set of user-owned or otherwise never-channel-scoped kinds (profile, text note, contact list, long-form, user status, read state, NIP-51 lists/sets, NIP-65 relay list, NIP-30 emoji set/list, agent engram/profile, NIP-AP persona/team/managed-agent/team-catalog, NIP-34 git events, NIP-MP project, moderation commands 9040-9044, NIP-43 relay-admin commands and leave request, NIP-IA archive/unarchive requests, the agent-turn metric, and the NIP-PL push lease); ingest_event_inner forces channel_id to None for any kind in this set even if the event carries a stray h tag, before the requires_h_channel_scope check runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The global-only and h-tag-required kind sets are disjoint -- a repo-native test (global_only_and_channel_scoped_are_disjoint) asserts this directly against the two functions above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "channel_id for an ordinary event is read from its own h tag (extract_channel_id); for a reaction (kind:7) it is derived from the reacted-to event's channel via derive_reaction_channel, rejecting the reaction if the target event or its e-tag reference is missing; for a standard deletion (kind:5, which carries no h tag itself) it is looked up from the target event named in the deletion's e tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "check_token_channel_access rejects an event with \"restricted: token does not have access to this channel\" when the auth context carries a channel_ids allow-list (auth.channel_ids() is Some) that does not contain the resolved channel_id; separately, ingest_event_inner rejects any channel-scoped token (auth.channel_ids().is_some()) outright from publishing an event whose resolved channel_id is None (a global event), with the comment stating this exists specifically so a channel-scoped token cannot bypass its own restriction by submitting a global-kind event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "check_channel_membership grants access if the pubkey is a cached member of the channel (state.is_member_cached); otherwise it falls back to checking whether the channel's own visibility is \"open\" (reading the prefetched channel row, or querying state.db.get_channel if none was prefetched), granting access on an open channel and otherwise rejecting with \"restricted: not a channel member\"; a database error surfaces as an Err(String) rather than a silent allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The generic check_channel_membership gate is explicitly skipped (skip_membership) for six kinds -- NIP-29 join request, NIP-29 create-group, stream-message edit, NIP-29 edit-metadata, NIP-29 delete-event, and NIP-29 delete-group -- with the code comment stating the reason as OQ1: these kinds' own per-kind validators (e.g. validate_edit_ownership) independently enforce authorization and fail closed, and bypassing the generic gate is what lets an owning human act on a private agent channel without being an ordinary member."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "For every kind except moderation-command kinds and relay-admin kinds, ingest_event_inner independently re-checks the community's durable moderation_restriction_state for the authenticated pubkey immediately before channel resolution, rejecting with IngestError::AuthFailed(\"blocked: you are banned...\") or a timed-out message if the state says so; the code comment states this re-check exists as a durable backstop because an already-authenticated live socket never re-authenticates, so a missed live-disconnect fan-out could otherwise let a banned member keep writing indefinitely, and that moderation-command and relay-admin kinds are exempted here only because their own handlers enforce the same durable ban internally, so a timed-out admin can still lift the timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A database error while reading moderation_restriction_state is mapped to IngestError::Internal with the comment \"Fail closed: a DB error must not let a banned/timed-out actor write\", rather than treated as an implicit allow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "buzz-auth's access.rs defines a separate ChannelAccessChecker trait plus check_read_access/check_write_access helpers (scope check + async membership check), but grepping crates/ for callers of check_write_access and check_read_access finds only buzz-auth's own lib.rs re-export and access.rs itself -- the ingest write path (ingest.rs) does not call through this trait at all, calling state.is_member_cached and state.db.get_channel directly instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/access.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-principles-signed-events
---

# Event authorization

How the relay decides, at the moment a signed Nostr event reaches its shared
ingest seam, whether the pubkey that authenticated the connection is
permitted to publish *this specific event* -- as opposed to merely having
proven which key it holds.

## Definition

**Event authorization** is the sequence of checks the relay's write path
(`ingest_event` / `ingest_event_inner` in
`crates/buzz-relay/src/handlers/ingest.rs`) applies to an already-verified,
already-authenticated event before it is stored or fanned out, to decide
*whether this write is allowed* rather than merely *who sent it*. It answers
three separable questions for one event, not one:

1. **Category** -- does the authenticated connection hold the permission
   scope this event's *kind* requires? (`required_scope_for_kind` +
   `auth.scopes()`.)
2. **Place** -- if the kind is channel-scoped, is the connection allowed to
   write into *this* channel? (token-level channel restriction via
   `check_token_channel_access`, then community membership or open-channel
   fallback via `check_channel_membership`.)
3. **Standing** -- has the community's moderation state (a ban, or an active
   timeout) revoked this pubkey's standing to write at all, independent of
   scope or channel? (the `moderation_restriction_state` re-check.)

All three must pass; each is a distinct rejection reason with its own error
message, and none substitutes for another. A connection with every scope it
needs is still refused if it is banned; a connection in good standing with
the right scope is still refused if the event's channel is neither one it
is a member of nor open.

**What this is not.** Event authorization presupposes two things this node
does not itself cover, each already the property of a different corpus
node once merged: that the event's `id` and `sig` are cryptographically
valid for the `pubkey` in its own envelope (`verify_event`, the
*signed-events* principle -- an integrity/identity check, not a permission
check), and that `event.pubkey` matches the identity `auth.pubkey()`
already authenticated for the connection, with NIP-59 gift wraps as the one
deliberate exception (an unrelated ephemeral signing key by design). Both
run, and both must pass, *before* any of the three authorization questions
above are even asked.

## How the checks are ordered

```mermaid
flowchart TD
    A[Event arrives on ingest_event] --> B[verify_event: id hash + Schnorr sig]
    B -->|fail| RejectInvalid[Rejected: invalid]
    B -->|pass| C{event.pubkey == auth.pubkey?<br/>gift wrap exempt}
    C -->|no| RejectAuth[AuthFailed]
    C -->|yes| D[required_scope_for_kind]
    D --> E{auth.scopes contains required?}
    E -->|no| RejectScope[AuthFailed: insufficient scope]
    E -->|yes| F{banned or timed out?<br/>skipped for moderation/relay-admin kinds}
    F -->|yes| RejectBanned[AuthFailed: blocked/restricted]
    F -->|db error| RejectInternal[Internal: fail closed]
    F -->|no| G[resolve channel_id:<br/>h tag / reaction target / deletion target]
    G --> H{is_global_only_kind?}
    H -->|yes| I[channel_id = None]
    H -->|no| J{requires_h_channel_scope<br/>and channel_id is None?}
    J -->|yes| RejectNoH[Rejected: missing h tag]
    J -->|no| K{channel_id present?}
    K -->|yes| L[check_token_channel_access]
    K -->|no, but token is channel-scoped| RejectGlobal[AuthFailed: token cannot publish global events]
    L --> M{skip_membership kind?}
    M -->|yes| Accepted[Admitted to storage/fan-out]
    M -->|no| N[check_channel_membership:<br/>member OR channel is open]
    N -->|fail| RejectMember[Rejected: not a channel member]
    N -->|pass| Accepted
    I --> Accepted
```

This is the actual order the code runs the checks in, not an idealized
model: the ban/timeout re-check runs *before* channel resolution, and the
token-channel and community-membership checks both run only once a
`channel_id` (or its deliberate absence) has been settled.

## Background

**Why a ban/timeout re-check exists on the write path at all**, given that
NIP-42 authentication is itself where a ban would normally be enforced: an
already-authenticated WebSocket connection never re-authenticates for the
lifetime of the socket. If the live moderation fan-out that would otherwise
disconnect a newly-banned member is missed (a fire-and-forget publish, a
slow subscriber, a reconnect race), that member's still-open socket would
otherwise keep writing indefinitely. The code comment in `ingest.rs`
describes this re-check as the durable backstop for exactly that gap.
Moderation-command kinds and relay-admin kinds are carved out of this
specific re-check only, and only because each enforces the same durable ban
inside its own handler -- the carve-out exists so a timed-out community
admin retains the one capability needed to lift their own timeout.

**Why scope and channel membership are two separate gates rather than one.**
Scope answers a category-level question ("can this connection write
messages at all, anywhere") that is meaningful even for a connection with
no channel restriction at all (`auth.channel_ids()` is `None` for most
connections and always `None` over HTTP). Channel membership answers a
place-level question that only exists once a concrete channel has been
resolved. Collapsing them would either force every scope to be
channel-specific (losing the global/user-owned kind category entirely) or
force channel membership to be expressible as a scope (losing per-channel
precision). Keeping them separate is also why a channel-scoped token is
independently blocked from publishing any kind that resolves to no channel
at all -- the token-channel check alone cannot express "this token may
never post a global event," so `ingest_event_inner` states that rule
directly.

## Use cases

- **A developer adding a new event kind** needs to decide, and encode, three
  independent answers for it: which `Scope` it requires
  (`required_scope_for_kind`), whether it is channel-scoped or global-only
  (`requires_h_channel_scope` / `is_global_only_kind` -- the disjointness
  test in `ingest.rs`'s own test suite exists to catch a kind accidentally
  landing in both or neither), and whether its own handler needs to bypass
  the generic membership gate because it enforces authorization itself
  (the `skip_membership` list).
- **An operator investigating "why was this write rejected"** needs to know
  which of the three questions (category / place / standing) produced the
  rejection, because each has a distinct, differently-actionable message:
  an insufficient-scope rejection means the token/connection was issued the
  wrong permissions; a not-a-channel-member rejection means the actor needs
  an invite or the channel needs to be opened; a banned/timed-out rejection
  means moderation state is the blocker, not permissions at all.
- **A reviewer checking a PR that touches ingest.rs** needs to confirm a new
  or moved check still runs in the right relative order -- in particular,
  that nothing bypasses the ban/timeout backstop for a kind that is not
  moderation-command or relay-admin, and that a new channel-scoped kind is
  added to `requires_h_channel_scope` rather than left to fall through
  silently with `channel_id = None`.

## Scope and omissions

**This node covers** the relay's ingest-time authorization sequence for a
client-submitted event: per-kind scope requirements, the token-level and
community-level channel-access gates, and the durable ban/timeout write-block
backstop, as implemented in `crates/buzz-relay/src/handlers/ingest.rs` and
`crates/buzz-auth/src/scope.rs`. It states, but does not itself define, the
two preconditions (signature validity and pubkey/principal identity match)
that already have to hold before any of these checks run.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| How NIP-42 or NIP-98 authentication establishes `auth.pubkey()` and `auth.scopes()` in the first place | A separate concern (authentication, not authorization) with its own source in `buzz-auth/src/nip42.rs` and `nip98.rs`, not opened for this node |
| `buzz-auth::access::ChannelAccessChecker` / `check_read_access` / `check_write_access` | Confirmed by grep to have no caller in `crates/` outside `buzz-auth` itself -- it is not part of the event-authorization path this node documents, and is named here rather than folded in as a second concept |
| Per-kind command-handler-local authorization (e.g. capability/role checks inside `handle_command`, `validate_edit_ownership`, `handle_relay_admin_event`, `handle_moderation_command`) for the kinds that skip or exit the generic gates early | Each is its own, kind-specific authorization surface; documenting them is a separate node per kind-family, not this one |
| Read-path authorization (subscription filters, `messages read` scope enforcement, fan-out visibility gating) | A distinct question ("what can this pubkey see") from this node's "what can this pubkey write" |
| The exact NIP-29 role/capability model behind `AdminChannels` / `AdminUsers` scopes | Not traced in the sources opened for this node |

**Expected but not verified when this node was written:** whether every
event kind currently defined in `buzz-core/src/kind.rs` is reachable
through exactly one of `required_scope_for_kind`'s match arms, `is_global_
only_kind`, and `requires_h_channel_scope` (the disjointness test found
covers the second pair only, not a three-way exhaustiveness check against
the full kind registry) was not independently re-verified against
`kind.rs` for this node -- the claims above rest on reading `ingest.rs`'s
own match arms and test suite, not on cross-checking every kind constant
individually.
