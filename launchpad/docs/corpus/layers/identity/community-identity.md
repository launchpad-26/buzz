---
id: layers-identity-community-identity
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
  - statement: "The `communities` table has columns `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `host VARCHAR(255) NOT NULL`, `signing_key BYTEA`, and `created_at`, with a unique index on `lower(host)` so host comparison is case-insensitive; `icon TEXT` was added by a later migration."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0003_community_icon.sql"
  - statement: "`RelayInfo::build` (the NIP-11 relay information document, served at `GET /` with `Accept: application/nostr+json`) takes only static or pre-derived scalar inputs, and a compile-time function-pointer fence (`_RELAY_INFO_BUILD_STATIC_INPUT_FENCE`) pins its exact signature so an unscoped DB/search/audit input cannot be added without breaking the build; the fence's own doc comment states its purpose is preventing an unauthenticated NIP-11 read from becoming a cross-community enumeration oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "Of `RelayInfo`'s fields, `name` (\"Buzz Relay\") and `description` are fixed string literals shared by every community served by one relay process, and `self` (the relay's NIP-11 identity pubkey) comes from the process-wide `state.relay_keypair` via `nip11_facts`, not from per-community state; the one field that is genuinely host-scoped is `icon`, fetched by `workspace_icon_for_host` through `crate::tenant::bind_community` and `Db::get_community_icon`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The workspace icon is set by an admin or owner (or, on an open relay with no steward yet, admitted without a roster role and logged) sending a kind:9033 (`RELAY_ADMIN_SET_WORKSPACE_PROFILE`) event; the handler resolves the icon tag, validates it, and calls `Db::set_community_icon(tenant.community(), icon)`, scoped to the sender's already-bound community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "`KIND_NIP29_GROUP_METADATA` = 39000 is documented as 'NIP-29: Addressable group metadata state', part of the addressable range 39000-39003 (metadata, admins, members, roles); this range identifies a NIP-29 group, which Buzz's own domain vocabulary calls a channel, not a community — a community may host many channels, each independently addressable by kind:39000-39002 events whose `d` tag holds the channel's UUID."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The `signing_key BYTEA` column on `communities` is only ever written as `NULL` (cleared as part of the community-deletion purge path); a repository-wide search of the relay, db and core crates for `signing_key` found no other read or write site, so it is not currently wired into how a community identifies or signs anything."
    entry_class: FACT
    evidence:
      - "grep_signing_key(crates/buzz-db/src, crates/buzz-relay/src, crates/buzz-core/src, migrations) -> only migrations/0001_initial_schema.sql (column definition) and crates/buzz-db/src/deletion.rs:1622 (cleared to NULL on deletion) matched; no other read or write site"
  - statement: "A community is bound from an inbound request's Host header, normalized and resolved to a `CommunityId` before any tenant-scoped handler runs, and this binding fails closed on an unmapped or malformed host rather than falling back to a default community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "Because only `icon` is genuinely per-community in the NIP-11 document, and the relay's own `self` pubkey and `name`/`description` are shared across every community a relay process hosts, a community's addressable identity to an external Nostr client is carried primarily by the host it is reached on (the same host-resolution mechanism documented in `architecture-principles-host-selects-community`), with the NIP-11 document and its host-scoped `icon` field as the one piece of per-community presentation state layered on top."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/tenant.rs"
    confidence: 0.75
  - statement: "Issue #1104 frames this node as 'the identity angle' of community identification, distinct from a sibling task documenting `layers/tenancy/community-id.md` (#1183, the internal `communities.id` UUID and host-mapping angle) — both issues share an identical generic definition-of-done checklist, and neither issue body states the intended boundary between the two beyond their titles and file paths."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1104 and #1183 issue bodies, read directly while authoring this node"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Community identity

**Community identity** is what makes one Buzz community recognizable and
addressable as a distinct entity — the host it is reached on, and the small
set of self-describing state (currently just a workspace icon) it presents
through the Nostr protocol's own relay-description mechanism. It is the
outward-facing counterpart to a community's internal database primary key.

## Definition

A Buzz deployment can serve many **communities** from a single relay
process, each bound to its own domain (`communities.host`, unique
case-insensitively). A client never addresses a community by its internal
identifier — it addresses it by connecting to that community's host. Once
connected, two things establish the community's identity from the client's
side:

1. **The host itself.** Every request is bound to exactly one community by
   resolving the connection's `Host` header, before any handler runs, and
   that binding fails closed on an unmapped host rather than defaulting to
   some other community. The host *is* the address a client uses to reach
   this community and no other.
2. **The NIP-11 relay information document**, served at `GET /` with
   `Accept: application/nostr+json`. This is the standard Nostr mechanism a
   relay uses to describe itself to a connecting client — name, description,
   supported NIPs, and (in Buzz's case) an `icon`. Most of that document is
   static and shared by every community a given relay process hosts (`name`
   is always `"Buzz Relay"`; the `self` signing pubkey is the relay
   process's own key, not a per-community one). The one field that is
   genuinely per-community is `icon` — a workspace logo an admin or owner
   sets by publishing a kind:9033 event, stored in `communities.icon` and
   scoped to that community's already-bound identity by the same
   host-resolution path.

**Community identity, as this node defines it, is therefore the combination
of "which host reaches this community" plus "what that community's own
NIP-11 document presents" — not a single dedicated identity artifact.**
No event or field in the codebase gives a community a NIP-29-style
addressable identity of its own the way a channel or a user has one (see
Boundary, below); its identity is assembled from the tenancy boundary and a
thin layer of per-community presentation state on top of it.

## Boundary — what this is not

**Not `community-id` (#1183, `layers/tenancy/community-id.md`, not yet
authored).** That sibling node's subject is the internal identifier —
`communities.id`, a `UUID` primary key, and the host-to-id mapping that
resolves it. This node's subject is different: how that same community
*presents* itself outward, once bound. The two are related (the NIP-11
lookup for `icon` is itself keyed by the resolved `CommunityId`) but are not
the same concept — one is a database key, the other is what a connecting
client actually observes.

**Not channel/NIP-29-group identity (kind:39000–39002).** Buzz's NIP-29
group-metadata range (`KIND_NIP29_GROUP_METADATA` = 39000, plus 39001
admins and 39002 members) gives each **channel** inside a community its own
addressable, parameterized-replaceable identity — a `d` tag holding the
channel's UUID. A community can host many channels, each independently
identified this way. That is a real, code-level "addressable identity"
mechanism, but it identifies a channel, not the community that contains it;
folding it into this node would conflate two different corpus surfaces.

**Not the relay's own signing identity.** The NIP-11 `self` field is the
relay process's signing pubkey, shared across every community that process
hosts — it identifies the *relay*, not any one community. `communities` does
carry a `signing_key` column, but nothing in the relay, db, or core crates
reads it outside the deletion-purge path that clears it to `NULL`; it is not
part of how a community is identified today.

## Use cases

- **A client deciding which community it has reached.** After connecting to
  a host and completing NIP-42 auth, a client can fetch the NIP-11 document
  to show a workspace icon and confirm basic relay capabilities — but the
  fact of *which* community it is talking to was already settled by the host
  it dialed, not by anything in that document.
- **An admin branding their community.** Setting a workspace icon (kind:9033)
  is the one self-service way a community's operators customize what the
  community presents to the outside world, distinct from the immutable host
  binding and the internal id.
- **Reasoning about isolation.** Understanding that `name`/`description`/
  `self` are relay-process-wide, not per-community, matters when auditing
  what NIP-11 can and cannot leak across communities sharing one relay
  process — the compile-time static-input fence on `RelayInfo::build` exists
  specifically to keep that surface from silently growing an unscoped input.

## Scope and omissions

**This document covers** what constitutes a community's outward-facing,
Nostr-visible identity today: host-based addressing plus the NIP-11
document's one per-community field (`icon`), and the code-level mechanisms
(`bind_community`, `RelayInfo::build`, kind:9033) that produce it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The internal `communities.id` UUID, its generation and host-mapping | #1183, `layers/tenancy/community-id.md` (not yet authored) |
| Channel/NIP-29-group identity (kind:39000-39002) | Not yet filed as its own `layers/identity` task at this revision |
| The row-zero host-binding mechanism itself, in full | `architecture-principles-host-selects-community` |
| Why the community boundary is treated as a security boundary | `architecture-principles-community-is-security-boundary` |
| Whether `communities.signing_key` should be wired into community identity | Not filed as its own issue at the recorded revision |

**Expected but not verified when this node was written:** whether any
in-progress or planned work intends to make `name`, `description`, or `self`
per-community rather than relay-process-wide — no such issue was found, but
the search was not exhaustive across the full issue tracker.
