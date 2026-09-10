---
id: interfaces-nostr-buzz-nips-nip-wp
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
  - statement: "NIP-WP ('Workspace Profile') is a draft, optional, relay-scoped Nostr Implementation Possibility defining how a relay-scoped workspace icon is set (kind:9033, admin/owner-signed command) and read (the standard NIP-11 `icon` field), depending on NIP-01, NIP-11, NIP-42 and NIP-43."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-WP.md:1-15"
  - statement: "The kind:9033 event carries an empty `content` and exactly one `icon` tag; an empty or absent `icon` tag clears the icon; the value must be an http(s) URL or a data:image/* URL with no whitespace or control characters and within relay size limits (2048 bytes for plain URLs, 96 KiB RECOMMENDED for inline data URLs); non-image data: URLs MUST be rejected; last accepted command wins."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-WP.md:45-73"
  - statement: "The icon read path is plain, unauthenticated NIP-11 (GET on the relay's HTTP endpoint with Accept: application/nostr+json); NIP-WP adds no new event kind or endpoint for reading the icon, and clients MAY cache it locally keyed by relay URL."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-WP.md:75-82"
  - statement: "kind:9033 is defined in code as RELAY_ADMIN_SET_WORKSPACE_PROFILE = 9033, alongside the NIP-43 admin commands 9030 (add member), 9031 (remove member) and 9032 (change role) that it shares a permission-matrix module with."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:388-395"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:1-13"
  - statement: "The relay's actual authorization rule for kind:9033 is steward-wins, not a flat admin/owner-only rule: on a closed relay (require_relay_membership=true) or any relay where a steward (admin/owner row) already exists, only admin/owner may set the icon; on a genuinely rosterless open relay (no admin/owner row at all) any NIP-42-authenticated sender may set it, because the desktop shows the icon editor on open relays and without this exception the icon would be permanently unsettable there. This is a documented refinement of the spec text's simpler 'verify the actor holds the admin or owner role... reject otherwise', not a contradiction of it -- the spec's own Client Behavior section already anticipates a widened relay-side rule ('the relay-side role check ... is the enforcement')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:97-124"
      - "docs/nips/NIP-WP.md:65-71"
      - "docs/nips/NIP-WP.md:82"
  - statement: "validate_workspace_icon enforces the wire-format rules from the spec's Relay Processing Algorithm and Security Considerations: empty clears; data:image/* URLs capped at 98,304 bytes; http(s) URLs capped at 2048 bytes; any control character or whitespace rejected; non-http(s)/non-data:image URLs (e.g. javascript: or data:text/html) rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:59-95"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:614-686"
  - statement: "On acceptance the relay persists the icon via Db::set_community_icon against the communities.icon column, scoped per community; Db::get_community_icon returns None for both a NULL and an empty-string stored value."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/community.rs:227-270"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:290-304"
  - statement: "The relay serves the stored icon in RelayInfo.icon (NIP-11 document), omitting the field entirely when unset; workspace_icon_for_host resolves the icon through crate::tenant::bind_community so a request can only ever observe the icon of the community its own host resolves to, and fails open to None (not an error) on any lookup failure so an icon problem never breaks NIP-11 itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:23-33"
      - "crates/buzz-relay/src/nip11.rs:276-338"
  - statement: "kind:9033 (with 9030-9032) is exempted from ingest_event's durable write-path restriction gate so a timed-out admin retains administrative capability, but that exemption is ban-blind at the ingest layer; the actual ban enforcement for all four kinds happens inside handle_relay_admin_event, which checks moderation_restriction_state before executing the command and fails closed (RelayAdminError::Internal) on a DB error rather than admitting on a blip."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:485-496"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:150-208"
  - statement: "A valid kind:9033 is accepted and its icon stored: a unit test signs a fresh kind:9033 with an icon tag from a relay owner and asserts both Ok(()) and that get_community_icon subsequently returns that exact value; a second unit test shows the same acceptance from a rosterless open relay's first authenticated sender."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:758-771"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:787-803"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:832-838"
  - statement: "A failure example: once a steward (owner) exists on an open relay, a subsequent kind:9033 from a roleless sender is rejected with RelayAdminError::Rejected(\"actor not authorized: must be admin or owner\") and the previously stored icon is left unchanged; the same rejection occurs on a closed relay for both a roleless sender and a plain 'member'-role sender."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs:805-829"
      - "crates/buzz-relay/src/handlers/relay_admin.rs:848-889"
  - statement: "A second failure example at the transport layer: a banned admin's signed kind:9033 POST to /events is refused with HTTP 403 and the exact body {\"error\":\"blocked: you are banned from this community\"}, and the community's icon column is asserted unchanged afterward."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs:206-291"
  - statement: "NIP-WP, the kind:9033 handler and the icon-serving NIP-11 path originate from three commits: 5bfd5ca27 ('feat: per-community workspace icon set by admins, served via NIP-11', #1463) introduced the feature; e2e007910 ('fix(security): enforce durable community ban on NIP-43 relay-admin kinds 9030-9033', #3128) added the ban gate; 5765fc74b ('fix(relay): allow open relays to set their NIP-11 workspace icon (kind:9033)', #3998) added the rosterless-open-relay admit."
    entry_class: FACT
    evidence:
      - "commit 5bfd5ca27"
      - "commit e2e007910"
      - "commit 5765fc74b"
  - statement: "node.schema.json's type enum has no separate 'interface' value; interface-shaped and event-kind-shaped corpus nodes both carry type: interfaces-events, per Feature #602's success criteria listing 'interfaces/events' as one combined corpus surface."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md:216-228"
---

# NIP-WP (Workspace Profile): interface

This node documents Buzz's own custom Nostr NIP extension, NIP-WP, which
defines a relay-scoped **write** path (a new command kind, `9033` "Set
Workspace Profile") plus reuse of an existing standard **read** path (NIP-11's
`icon` field on the relay information document) for a workspace's identifying
icon. The two sides of the boundary are a relay-admin-or-owner-signed client
(write) and any NIP-11-aware client, Buzz or third-party (read); the protocol
is a Nostr event over WebSocket/HTTP for the write, and an unauthenticated
`GET` + `Accept: application/nostr+json` HTTP request for the read. The
authoritative spec text is `docs/nips/NIP-WP.md`; this node cites it and the
implementation, it does not restate the wire format from memory.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `kind:9033` Set Workspace Profile (write) | `docs/nips/NIP-WP.md:37-63`; `crates/buzz-core/src/kind.rs:395` (`RELAY_ADMIN_SET_WORKSPACE_PROFILE`); `crates/buzz-relay/src/handlers/relay_admin.rs:223-305` (`execute_relay_admin_command`, the `kind == RELAY_ADMIN_SET_WORKSPACE_PROFILE` branch) | Admin/owner-signed command setting or clearing the relay's workspace icon via a single `icon` tag |
| Icon persistence | `crates/buzz-db/src/store/community.rs:227-270` (`get_community_icon`, `set_community_icon`) | Per-community `communities.icon` column; empty string is normalized to `None` on read |
| NIP-11 `icon` field (read) | `docs/nips/NIP-WP.md:75-82`; `crates/buzz-relay/src/nip11.rs:23-33` (`RelayInfo.icon`), `:276-338` (`nip11_document`, `workspace_icon_for_host`) | Standard, unauthenticated NIP-11 relay-information-document field; omitted when unset |
| POST `/events` (transport for `kind:9033`) | `crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs:54-68` (`post_event`, NIP-98-authenticated) | Same generic Nostr event ingest path documented in root `AGENTS.md`; no endpoint specific to NIP-WP |

## Contract and stability

- **Authorization**: steward-wins, not a flat role check. A closed relay
  (`require_relay_membership=true`), or any relay where an admin/owner row
  already exists, requires the sender to hold `admin` or `owner` in
  `relay_members`; a genuinely rosterless open relay admits any
  NIP-42-authenticated sender instead, so the icon is not permanently
  unsettable on relays with no configured owner
  (`crates/buzz-relay/src/handlers/relay_admin.rs:97-124`). This is the
  concrete relay-side enforcement the spec's Client Behavior section defers
  to (`docs/nips/NIP-WP.md:82`).
- **Validation**: an `icon` value must be empty (clear), or an `http(s)` /
  `data:image/*` URL with no whitespace or control characters, capped at 2048
  bytes (plain URL) or 98,304 bytes (data URL); non-image `data:` URLs are
  rejected (`crates/buzz-relay/src/handlers/relay_admin.rs:59-95`, matching
  `docs/nips/NIP-WP.md:65-71,84-88`).
- **Error/rejection behavior**: an unauthorized sender's command is rejected
  with `"actor not authorized: must be admin or owner"`
  (`RelayAdminError::Rejected`); a durably banned sender is rejected before
  the command body runs at all, surfacing as HTTP 403 with the exact body
  `{"error":"blocked: you are banned from this community"}`
  (`crates/buzz-relay/src/handlers/relay_admin.rs:150-208`; regression-tested
  in `crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs:206-291`);
  an internal restriction-lookup failure fails closed as
  `RelayAdminError::Internal`, never silently admitting the command.
  `kind:9033` is exempted from `ingest_event`'s durable write-path timeout
  gate (so a timed-out, non-banned admin keeps administering), but is not
  exempt from the ban check (`crates/buzz-relay/src/handlers/ingest.rs:485-496`).
- **Ordering/idempotency**: last accepted command wins
  (`docs/nips/NIP-WP.md:73`); `set_community_icon` is an unconditional
  `UPDATE`, so repeated identical commands are idempotent
  (`crates/buzz-db/src/store/community.rs:251-270`). Commands more than ±120
  seconds stale (by `created_at`) are rejected as a replay guard
  (`crates/buzz-relay/src/handlers/relay_admin.rs:230-246`).
- **Versioning/compatibility**: NIP-WP is marked `draft` and `optional`
  (`docs/nips/NIP-WP.md:7`) — clients and relays must not assume every relay
  advertises or accepts it. The read side (NIP-11 `icon`) is stable upstream
  Nostr syntax with zero Buzz-specific parsing required on the client.
- **Multi-tenancy**: the icon is scoped per community via
  `crate::tenant::bind_community`; an unmapped host's NIP-11 document has no
  `icon` field, and a request can only ever observe its own resolved
  community's icon (`crates/buzz-relay/src/nip11.rs:319-338,371-390`).

## Examples

**Valid**: a relay owner signs and submits a `kind:9033` event with tag
`["icon", "https://example.com/owner.png"]`; `handle_relay_admin_event`
returns `Ok(())` and a subsequent `get_community_icon` read returns exactly
that URL (`crates/buzz-relay/src/handlers/relay_admin.rs:832-838`). The
NIP-11 document served afterward carries `"icon":"https://example.com/owner.png"`.

**Failure**: (a) once any steward exists on an open relay, a roleless
sender's `kind:9033` is refused with
`RelayAdminError::Rejected("actor not authorized: must be admin or owner")`
and the previously stored icon is left unchanged
(`crates/buzz-relay/src/handlers/relay_admin.rs:805-829`); (b) a durably
banned admin's signed `kind:9033` POST to `/events` is refused with HTTP 403
and body `{"error":"blocked: you are banned from this community"}`, with the
community's `icon` column asserted unchanged
(`crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs:206-291`).

## Boundary

This node does not describe:
- NIP-11's own full relay-information-document schema (name, description,
  pubkey, supported_nips, limitation, etc.) — only the `icon` field NIP-WP
  feeds. NIP-11 itself has no corpus node yet.
- NIP-43's own admin-command wire contract for kinds 9030-9032 (add/remove
  member, change role) — this node only notes that `kind:9033` shares their
  module, permission-matrix shape and ban-gate enforcement path. NIP-43 has
  no corpus node yet.
- NIP-86's `changerelayicon` management-API method, which NIP-WP's own
  Motivation section explains it deliberately does not adopt (a separate
  JSON-RPC/HTTP surface rather than the NIP-42/NIP-43 role state Buzz
  already enforces).
- A full parameter-by-parameter API-reference catalogue of every
  `relay_admin.rs` function; only the operations and contract points a
  caller needs are covered here.

## Relationships

No `relationships` front-matter entries are declared: no sibling `buzz-nips`
corpus node (for NIP-11, NIP-43, or NIP-86) exists yet under
`launchpad/docs/corpus/interfaces/nostr/buzz-nips/` to resolve as a target,
and `AGENTS.md`'s own rule requires every declared relationship to resolve
against `origin/launchpad`. Related NIPs are named in prose instead, by
filename: `docs/nips/NIP-11.md` is not present in this repository's
`docs/nips/` tree (NIP-11 is upstream, unmirrored here) but is referenced
throughout `docs/nips/NIP-WP.md` and `crates/buzz-relay/src/nip11.rs`;
`docs/nips/NIP-AA.md`/other `NIP-*` files under `docs/nips/` were checked and
none is NIP-43 or NIP-86 by that exact name either — both are referenced by
number only in `docs/nips/NIP-WP.md:9,25,90-94` and in code comments
(`crates/buzz-relay/src/handlers/relay_admin.rs:1`), not as a separate
mirrored spec file in this repository. The first `buzz-nips` sibling node
drafted (for NIP-11 or NIP-43) is the natural point to add a `references`
edge back to this node, once one exists.

## Scope and omissions

**This node covers**: the `kind:9033` write path (event shape, validation,
authorization including the steward-wins refinement, ban/timeout enforcement,
persistence) and the NIP-11 `icon` read path this NIP feeds, each grounded in
both the spec text and the current implementation, with one valid and two
failure examples drawn from this repository's own tests.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-11's full document schema | a future NIP-11 corpus node (does not yet exist) |
| NIP-43's 9030-9032 wire contract | a future NIP-43 corpus node (does not yet exist) |
| NIP-86's `changerelayicon` method | upstream NIP-86 spec; not implemented by Buzz |
| Desktop's icon-editor UI (`canEditIcon`, `EditCommunityDialog.tsx`) | desktop feature code, referenced only in passing by `relay_admin.rs`'s own doc comment (issue #2640), not independently verified here |

**Expected but not verified when this node was written:**
- The desktop client's actual icon-editor behavior (`canEditIcon` gating in
  `EditCommunityDialog.tsx`, cited by `relay_admin.rs`'s own comments) was not
  opened or verified directly for this node — only the relay-side contract
  it depends on was.
- Whether any third-party (non-Buzz) NIP-11-aware client has been observed
  actually rendering the `icon` field end-to-end was not tested; the client
  behavior described is per the upstream NIP-11 contract NIP-WP inherits,
  not an observed interop test in this repository.
