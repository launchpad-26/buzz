---
id: interfaces-nostr-nip-29
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "node.schema.json's type enum has no interface value; the enum member for the corpus's combined interface/event-kind surface is the single hyphenated token interfaces-events, per PRD #602's own success-criteria list treating 'interfaces/events' as one item."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This repository's root AGENTS.md states: 'Channels use h tags (NIP-29 group tag), not e tags... Addressable events that describe a channel carry its id in their d tag instead: kind:39000 (metadata), kind:39001, kind:39002 (membership). get_channels resolves a user's channels from the d tag of their kind:39002 events, not from h.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "NIP-29, fetched directly at the pinned commit dabfcb2aaecf4fa374eda8b1232ab303a03f60ba, is marked with the stability badges 'draft optional relay', and states that events sent by users to groups (chat messages, text notes, moderation events etc) MUST have an h tag with the value set to the group id."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "NIP-29 defines a group's access-control tags on its kind:39000 metadata event: 'private' means only members can read (its absence means anyone can read); 'restricted' means only members can write (its absence means anyone can write); 'closed' means join requests are ignored (its absence means join requests are expected to be honored)."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "NIP-29 defines the group-admin/moderation event kinds in the 9000-9020 range with one kind per action -- among them put-user (9000, a p tag with pubkey and optional roles), remove-user (9001, a p tag with pubkey), edit-metadata (9002, carrying all the group-metadata fields), delete-event (9005, an e tag naming the event id), create-group (9007, no additional tags) and delete-group (9008, no additional tags) -- and separately defines join-request (9021) and leave-request (9022), stating that 'any user can send a kind 9021 event to the relay in order to request admission to the group' and that a kind 9022 event lets a user 'be automatically removed from the group.'"
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
  - statement: "crates/buzz-core/src/kind.rs declares the NIP-29 admin/moderation kind constants KIND_NIP29_PUT_USER=9000, KIND_NIP29_REMOVE_USER=9001, KIND_NIP29_EDIT_METADATA=9002, KIND_NIP29_DELETE_EVENT=9005, KIND_NIP29_CREATE_GROUP=9007 and KIND_NIP29_DELETE_GROUP=9008, plus KIND_NIP29_JOIN_REQUEST=9021 and KIND_NIP29_LEAVE_REQUEST=9022, and separately the addressable group-state kinds KIND_NIP29_GROUP_METADATA=39000, KIND_NIP29_GROUP_ADMINS=39001, KIND_NIP29_GROUP_MEMBERS=39002 and KIND_NIP29_GROUP_ROLES=39003, matching NIP-29's own numbering exactly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:333-351"
      - "crates/buzz-core/src/kind.rs:420-428"
  - statement: "KIND_NIP29_GROUP_ROLES (39003) is registered in kind.rs's ALL_KINDS table but is never referenced by any handler under crates/buzz-relay -- confirmed by grepping the whole crates/ tree for the constant, which returns only its two occurrences inside kind.rs itself. Buzz's relay does not materialize a kind:39003 group-roles event for any channel, even though NIP-29 defines the kind and kind.rs declares the constant."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:428"
      - "crates/buzz-core/src/kind.rs:692"
  - statement: "buzz-core's filter.rs matches a NIP-01 #h filter tag against an event's own h tags when present, and only falls back to the stored event's channel_id when the event carries no h tag at all (its own comment names kind:7 reactions and kind:5 deletions as the motivating case); when an event does carry h tags but none match the filter, filter_match_one rejects it outright rather than falling back."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs:35-104"
  - statement: "ingest.rs's required_scope_for_kind maps KIND_NIP29_PUT_USER, KIND_NIP29_REMOVE_USER and KIND_NIP29_DELETE_GROUP to Scope::AdminChannels; maps KIND_NIP29_CREATE_GROUP to Scope::ChannelsWrite; maps KIND_NIP29_JOIN_REQUEST and KIND_NIP29_LEAVE_REQUEST to Scope::ChannelsRead; and splits KIND_NIP29_EDIT_METADATA itself -- Scope::AdminChannels when the event carries an 'archived' tag, Scope::ChannelsWrite otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:485-521"
  - statement: "When an authenticated actor's token does not carry the scope required_scope_for_kind computes for the submitted event's kind, ingest.rs rejects the write with IngestError::AuthFailed(format!(\"restricted: insufficient scope (need {})\", required)) -- one instance of a repository-wide NIP-20-style OK-message prefix convention (other prefixes observed in the same function include 'invalid:', 'blocked:' and 'auth:')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2249-2274"
  - statement: "side_effects.rs's emit_group_discovery_events builds and stores exactly three relay-signed addressable events after a group's creation, metadata edit, or membership change -- kind:39000 (group metadata: d, name, optional about, public/private, hidden for DM-type channels (with participant p tags), closed (always present -- 'Buzz channels always require explicit membership'), a t tag naming the channel type, optional topic/purpose, and archived/ttl/ttl_deadline when applicable), kind:39001 (group admins: a p tag per owner/admin member carrying their role) and kind:39002 (group members, built separately by store_group_members_event) -- and its own doc comment states these are stored channel-scoped (channel_id = Some(...)) rather than pushed through live global fan-out, so a client discovers them via historical REQ queries, not a live {kinds:[39000]} subscription."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1062-1234"
  - statement: "Nowhere in emit_group_discovery_events's kind:39000 tag-construction block does the code build a 'restricted' tag; the only two access/visibility tags it conditionally emits are 'private'/'public' and 'hidden', alongside the unconditional 'closed' tag -- confirmed by reading the full tag-building block, not by absence of a grep hit alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1138-1199"
  - statement: "store_group_members_event signs the relay's kind:39002 replacement with a timestamp computed as max(now, latest_recorded_member_event_timestamp + 1), so a rapid sequence of membership changes still produces a strictly increasing created_at for each successive addressable replacement rather than relying on wall-clock time alone to order them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1062-1097"
  - statement: "buzz-relay's nip11.rs declares SUPPORTED_NIPS as a fixed array that includes 29 unconditionally, unlike NIP-43 (relay membership) which nip11.rs's own comments and tests (nip43_not_in_static_supported_nips) show is only added to the advertised list when the relay is configured with a stable signing key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
      - "crates/buzz-relay/src/nip11.rs:575"
  - statement: "buzz-cli's `channels list --member` resolves the caller's own channel membership in two round trips: first a kind:39002 query filtered by #p on the caller's own pubkey, extracting each result's d tag as a channel id; then a kind:39000 query filtered by #d on those ids to fetch display metadata -- the concrete implementation of the d-tag-driven resolution root AGENTS.md describes in prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:29-69"
  - statement: "Buzz layers its own moderation surface -- ban, unban, timeout, untimeout and resolve-report, each a Buzz-specific kind handled by handle_moderation_command and authorized by authorize_moderation_action's community-role/channel-role lookups against relay_members and per-channel membership -- on top of, and separate from, NIP-29's own put-user/remove-user (9000/9001); a kind:9000/9001 event is a NIP-29 group-admin action materialized straight into the kind:39001/39002 snapshots above, while Buzz's ban/timeout kinds instead write a durable moderation_restriction row consulted independently of group membership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "Issue #1012's Definition of Done requires this node to define inputs/messages, outputs/responses and error/rejection behavior; authentication/authorization, versioning/compatibility and ordering/idempotency where applicable; link the authoritative machine/spec representation; and include at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1012 definition of done"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus confirms architecture-principles-relay-is-source-of-truth.md and templates/interface.md (id corpus-template-interface) are both present on the merge target, so both are valid relationships[] targets; no kind:39000/39001/39002 corpus node exists on that same tree, so no relationships[] entry can target one yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> includes architecture/principles/relay-is-source-of-truth.md and templates/interface.md; no interfaces/ or kind-39000/39001/39002 node present"
relationships:
  - type: references
    target: architecture-principles-relay-is-source-of-truth
  - type: implements
    target: corpus-template-interface
---

# NIP-29 group protocol: interface

This node documents the boundary Buzz's relay and clients use to create, join,
moderate and discover **groups** (Buzz's channels) -- the upstream Nostr NIP-29
protocol as this repository actually implements it, over the same WebSocket + Nostr
event transport every other Buzz interface uses. Two sides exchange NIP-29-shaped
events across it: a client (desktop, mobile, CLI or agent) sending `h`-tag-scoped
messages and 9000-range admin/membership commands, and the relay, which authorizes
each command, applies it to durable channel/member state, and republishes that state
as relay-signed addressable events in the 39000 range. This is the interface AGENTS.md
means by "Channels use `h` tags (NIP-29 group tag), not `e` tags."

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Scope a write to a group | NIP-29 `h` tag requirement; `crates/buzz-core/src/filter.rs` (`filter_match_one`) | Every event a user sends to a group MUST carry an `h` tag naming the group id; the relay's `#h` filter matching falls back to the stored event's `channel_id` only for events with no `h` tag at all (reactions, deletions), and rejects outright when `h` tags exist but none match. |
| Put user (admin add) | kind `9000`, `KIND_NIP29_PUT_USER` (`crates/buzz-core/src/kind.rs:335`) | Adds a pubkey to the group with optional roles; `ingest.rs` requires `Scope::AdminChannels`. |
| Remove user | kind `9001`, `KIND_NIP29_REMOVE_USER` (`kind.rs:337`) | Removes a pubkey from the group; requires `Scope::AdminChannels`. |
| Edit metadata | kind `9002`, `KIND_NIP29_EDIT_METADATA` (`kind.rs:339`) | Rewrites the group's metadata fields; requires `Scope::AdminChannels` when the event carries an `archived` tag, otherwise `Scope::ChannelsWrite`. |
| Delete event | kind `9005`, `KIND_NIP29_DELETE_EVENT` (`kind.rs:341`) | Names an event id (via an `e` tag) to remove from the group; grouped under `Scope::MessagesWrite` in `ingest.rs`. |
| Create group | kind `9007`, `KIND_NIP29_CREATE_GROUP` (`kind.rs:343`) | Requires `Scope::ChannelsWrite`; triggers `emit_group_discovery_events` once the channel exists. |
| Delete group | kind `9008`, `KIND_NIP29_DELETE_GROUP` (`kind.rs:345`) | Requires `Scope::AdminChannels`. |
| Join request | kind `9021`, `KIND_NIP29_JOIN_REQUEST` (`kind.rs:349`) | Any user may send this to request admission; requires only `Scope::ChannelsRead`. |
| Leave request | kind `9022`, `KIND_NIP29_LEAVE_REQUEST` (`kind.rs:351`) | Any member may send this to leave; requires only `Scope::ChannelsRead`. |
| Read group metadata | kind `39000`, `KIND_NIP29_GROUP_METADATA` (`kind.rs:422`) | Addressable (`d`-tagged) event the relay republishes after create/edit; carries `name`, `about`, `public`/`private`, `closed` (always present), `t`, `topic`, `purpose`, `archived`/`ttl`/`ttl_deadline`. |
| Read group admins | kind `39001`, `KIND_NIP29_GROUP_ADMINS` (`kind.rs:424`) | Addressable event listing owner/admin members and their roles as `p` tags. |
| Read group members | kind `39002`, `KIND_NIP29_GROUP_MEMBERS` (`kind.rs:426`) | Addressable event listing the full member roster; `buzz-cli`'s `channels list --member` resolves a caller's own channels by querying this kind with `#p` = the caller's pubkey, then extracting each result's `d` tag. |
| Read group roles | kind `39003`, `KIND_NIP29_GROUP_ROLES` (`kind.rs:428`) | Defined in `kind.rs` and part of `ALL_KINDS`, but **not implemented** -- see *Boundary* below. |

## Contract and stability

**Authorization is scope-gated, not role-gated at the transport layer.** Every NIP-29
write kind maps to one of `Scope::AdminChannels`, `Scope::ChannelsWrite` or
`Scope::ChannelsRead` in `required_scope_for_kind`; a token lacking the required scope
is rejected before the event ever reaches channel-state logic. `KIND_NIP29_EDIT_METADATA`
is the one kind whose required scope depends on the event's own content (the presence
of an `archived` tag), not on the kind alone.

**Rejection is a NIP-20-style prefixed OK-message reason, not a bare boolean.** An
insufficient-scope rejection is worded `"restricted: insufficient scope (need
{scope})"`, one instance of a prefix convention (`invalid:`, `blocked:`, `auth:`,
`restricted:`) `ingest.rs` uses uniformly across kinds, not something this interface
invents on its own.

**The relay is the sole writer of 39000/39001/39002.** Buzz materializes group
discovery state itself, signed with the relay's own keypair, in
`emit_group_discovery_events` and `store_group_members_event` — never as a
pass-through of a client-submitted addressable event. This is the concrete instance of
the corpus's own `architecture-principles-relay-is-source-of-truth` principle for this
interface, not a NIP-29 requirement in itself.

**Membership state is versioned by a monotonic timestamp, not wall-clock time alone.**
`store_group_members_event` computes each kind:39002 replacement's `created_at` as
`max(now, latest_recorded_timestamp + 1)`, so a burst of membership changes still
produces strictly increasing addressable-event timestamps even if two changes land in
the same wall-clock second — the ordering guarantee a NIP-01 addressable/replaceable
event's "last write wins by `created_at`" semantics depends on.

**Discovery state is channel-scoped, not globally fanned out.** `39000`/`39001`/`39002`
events are stored with `channel_id = Some(...)` so existing per-channel access control
applies to a private channel's member list; a live global `{kinds:[39000]}`
subscription will not receive them, and a client must instead issue a historical `REQ`.

**NIP-29 support is unconditional.** `buzz-relay`'s NIP-11 `SUPPORTED_NIPS` lists `29`
statically, unlike NIP-43 (relay membership), which is added to the advertised list
only when the relay is configured with a stable signing key — a caller can rely on
NIP-29 being advertised regardless of relay configuration.

## Boundary

This node does not describe:
- **Any single event kind's own full wire contract** — tag cardinality, exact JSON
  shape, content-field semantics for one kind in isolation — which is a kind-shaped
  node's own territory (`#1337`'s template). No `interfaces-nostr-nip-29` node
  restates a kind's tag shape beyond what the Operations table's one-line summary
  needs; the eventual kind-level nodes for `kind:39000` (issue `#874`), `kind:39001`
  (issue `#875`) and `kind:39002` (issue `#876`) are the canonical source once merged
  — none is merged on `origin/launchpad` as of this node's recorded revision, so no
  `relationships[]` edge can target them yet (see *Scope and omissions*).
- **A full parameter-by-parameter API-reference catalogue** for domain-expert
  readers — the Operations table above is a pointer to the defining source per
  operation, not an exhaustive field-by-field specification.
- **Buzz's own ban/timeout/unban/untimeout/resolve-report moderation layer.** That
  surface exists, is authorized independently (`authorize_moderation_action`'s
  community-role/channel-role lookups against `relay_members` and per-channel
  membership, consulting a durable `moderation_restriction` row rather than group
  membership), and is a Buzz-specific extension layered *above* NIP-29's own
  `put-user`/`remove-user`, not a restatement of it — named here so a reader knows it
  exists, without this node absorbing its own contract.
- **`kind:39003` (group roles) as an implemented surface.** `kind.rs` declares the
  constant and lists it in `ALL_KINDS`, but no handler under `crates/buzz-relay`
  builds, stores or serves a `kind:39003` event for any channel today — this is Buzz's
  own coverage gap against the upstream NIP-29 spec, not a claim that the kind is
  unsupported by the protocol.
- **NIP-43's relay-membership admin surface** (kinds 9030-9036) — a textually adjacent
  but separately-numbered admin surface with its own contract, out of this node's
  one-idea boundary.

## Relationships

- `references`: `architecture-principles-relay-is-source-of-truth` — this node's own
  "relay is the sole writer of 39000/39001/39002" claim in *Contract and stability* is
  the concrete instance of that principle for this interface.
- `implements`: `corpus-template-interface` — this node is drafted from that
  template's required-sections skeleton.

No `relationships[]` edge targets a kind:39000/39001/39002 node: none is merged on
`origin/launchpad` at this node's recorded revision (issues `#874`/`#875`/`#876` are
open, unmerged). They are named above by filename and kind number in prose instead,
per the corpus's own linking guidance for a target that does not yet resolve on the
merge branch.

## Examples

**Valid: joining an open group.** A user with a channel-scoped `Scope::ChannelsRead`
token submits a kind `9021` join-request event carrying an `h` tag naming the group
id. `ingest.rs` accepts it (join-request only requires `Scope::ChannelsRead`), the
relay applies the membership change, and `emit_group_discovery_events` /
`store_group_members_event` republish an updated, relay-signed kind `39002` whose
`created_at` is strictly greater than the previous membership snapshot's. The client
resolves its own membership afterward by querying kind `39002` with `#p` set to its
own pubkey and reading the `d` tag of the result, exactly as `buzz-cli`'s `channels
list --member` does.

**Failure: insufficient scope on an admin action.** A user holding only
`Scope::ChannelsWrite` submits a kind `9000` (put-user) event to add another member as
an admin. `required_scope_for_kind` computes `Scope::AdminChannels` for that kind; the
actor's token does not carry it, so `ingest.rs` rejects the event before any channel
state changes, with the message `"restricted: insufficient scope (need
admin:channels)"` — no `kind:39001`/`39002` republication occurs.

## Scope and omissions

**This node covers** the NIP-29 group protocol boundary as Buzz's relay implements
it: the `h`-tag write-scoping rule, the 9000-range admin/membership commands and their
authorization scopes, the 39000-range addressable discovery state the relay
republishes, the ordering/idempotency guarantee on membership snapshots, and NIP-29's
unconditional advertisement in the relay's NIP-11 document.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `kind:39000`'s own full tag/content contract | Issue `#874` (unmerged) |
| `kind:39001`'s own full tag/content contract | Issue `#875` (unmerged) |
| `kind:39002`'s own full tag/content contract | Issue `#876` (unmerged) |
| Buzz's ban/timeout/unban/untimeout/resolve-report moderation contract | Not yet a filed corpus task as of this node's recorded revision |
| NIP-43's relay-membership admin surface (kinds 9030-9036) | Not yet a filed corpus task as of this node's recorded revision |
| Field-by-field, domain-expert-depth API-parameter cataloguing | `#1346`/`#1532` (reference / API Reference gap, undecided) |

**Expected but not verified when this node was written:**
- **No end-to-end integration test was run against a live relay** to confirm the
  join-request and insufficient-scope examples above behave exactly as the source
  reading predicts; both examples are traced through the code paths that would
  execute, not observed at runtime.
- **Whether `kind:39003` is planned for a future implementation, or is a dead
  constant, was not established from any source** — `kind.rs` and its own doc
  comments were read for this node and neither states an intent either way.
- **Buzz's exact wording of every NIP-01 OK-message rejection prefix** (`invalid:`,
  `blocked:`, `auth:`, `restricted:`, `error:`) was read from `ingest.rs` and
  `event.rs` call sites encountered while tracing NIP-29 kinds specifically, not from
  an exhaustive audit of every rejection path in the relay.
