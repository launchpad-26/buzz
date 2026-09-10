---
id: platforms-relay-admission
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "`required_scope_for_kind(kind, event)` maps an event's kind to the `buzz_auth::Scope` an authenticated principal must hold to write it, returning `Err(&'static str)` for a kind with no match arm — an unrecognized kind is rejected, never silently admitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Inside `ingest_event_inner`, after signature/timestamp/pubkey checks, the authenticated principal's scopes (`auth.scopes()`) must contain the scope `required_scope_for_kind` returned, or the write is rejected with `IngestError::AuthFailed(\"restricted: insufficient scope (need <scope>)\")`; relay-admin kinds and NIP-43 leave requests are additionally rejected outright when the caller's token carries a channel restriction (`auth.channel_ids().is_some()`), because those commands are relay-global by definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`check_channel_membership` admits a channel-scoped write when the pubkey is a cached member of the channel, or — if not a member — when the channel's `visibility` column reads `\"open\"`; it accepts an already-fetched channel row from the caller to avoid a second query within the same request, and falls back to a direct `get_channel` lookup when the caller has none."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`check_token_channel_access` rejects a write when the caller authenticated with a channel-restricted API token (`auth.channel_ids()` is `Some`) whose allowed-channel set does not include the event's resolved channel; in pure-Nostr mode `channel_ids()` is always `None`, so this specific gate is a no-op and channel access is enforced through NIP-29 membership (`check_channel_membership`) instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`is_serving_active(community)` is a single SQL `EXISTS` check that a community row has `archived_at IS NULL`, `deleted_at IS NULL`, and `deletion_state = 'active'`; `ingest_event_inner` calls it as the first admission gate on every write, before any other check, and a lookup error (not merely `false`) fails the write closed as an internal error rather than admitting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Before storage, `ingest_event_inner` re-checks the authoring pubkey's moderation restriction state via `state.db.moderation_restriction_state(community, pubkey)`: a `banned` result rejects with `IngestError::AuthFailed(\"blocked: you are banned from this community\")`, an active `muted_until` in the future rejects with `\"restricted: you are timed out until <ts>\"`, and a database error fails the write closed as `IngestError::Internal` rather than admitting it. Moderation-command kinds and relay-admin kinds are exempted from this specific gate because their own handlers enforce the ban themselves, so a timed-out admin can still lift their own timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/moderation.rs"
  - statement: "On the read path, `handle_req` (the WebSocket `REQ` handler) rejects a subscription outright — closing it with `\"restricted: insufficient scope\"` — when the authenticated context's `scopes` is non-empty and does not contain `Scope::MessagesRead`; an empty `scopes` list (the pure-Nostr NIP-42 case, per `buzz-auth`'s own crate documentation) is treated as full access rather than as zero scopes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-auth/src/lib.rs"
  - statement: "`p_gated_filters_authorized(filters, authed_pubkey_hex)` is a single shared function, called verbatim from three call sites — the WebSocket `REQ` handler, the HTTP `POST /query` bridge, and the HTTP `POST /count` handler — that rejects any filter naming a kind in `buzz_core::kind::P_GATED_KINDS` unless the filter's `#p` tag matches the caller's own authenticated pubkey; this is the read-path admission gate for gift wraps, membership notifications and other pubkey-owned kinds, independent of channel membership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "`buzz_auth::scope::Scope` is a closed-but-forward-compatible enum (`MessagesRead`, `MessagesWrite`, `ChannelsRead`, `ChannelsWrite`, `AdminChannels`, `UsersRead`, `UsersWrite`, `AdminUsers`, `JobsRead`, `JobsWrite`, `SubscriptionsRead`, `SubscriptionsWrite`, `FilesRead`, `FilesWrite`, `ReposRead`, `ReposWrite`, plus `Unknown(String)`) with a stable wire-format string per variant (e.g. `\"messages:write\"`); it is the type every admission gate above checks a caller's granted permissions against."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/scope.rs"
  - statement: "`crates/buzz-auth/src/access.rs` defines `check_read_access`, `check_write_access` and the `ChannelAccessChecker` trait as a scope-plus-membership admission API, but a repository-wide search for their call sites (`check_read_access`, `check_write_access`, `ChannelAccessChecker`) finds no reference anywhere outside `crates/buzz-auth/src/lib.rs` and `access.rs` itself — no production code path in `buzz-relay` or elsewhere calls into it."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='check_read_access|check_write_access|ChannelAccessChecker', scope='**/*.rs') -> crates/buzz-auth/src/lib.rs, crates/buzz-auth/src/access.rs only, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "`crates/buzz-relay/Cargo.toml` declares `buzz-auth`, `buzz-db` and `buzz-core` as workspace dependencies, corroborating that the admission gates described here (spanning `buzz-relay`'s own handlers plus the `buzz_auth::Scope` type and `buzz-db` queries) cross exactly those three crate boundaries and no others."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
  - statement: "Unit tests co-located with `required_scope_for_kind` and the community write fence in `crates/buzz-relay/src/handlers/ingest.rs`'s own `#[cfg(test)] mod tests` include `serving_fence_active_community_admits_write`, `serving_fence_inactive_community_maps_to_restricted`, `serving_fence_lookup_outage_fails_closed_as_internal` (the `is_serving_active` gate's three outcomes), `long_form_requires_messages_write_scope`, `user_status_requires_users_write_scope`, `private_sidecars_and_moderation_commands_require_messages_write_scope`, `per_kind_scope_allowlist_covers_all_migrated_kinds` (the scope allowlist), and `relay_admin_ban_maps_to_blocked_auth_failure` (the ban/timeout mapping)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs`'s `banned_admin_is_refused_but_timed_out_admin_still_administers` is a live end-to-end regression test asserting the exact rejection string `\"blocked: you are banned from this community\"` for a banned actor, distinct from the timed-out-admin case that the same test exercises as still permitted for administrative commands."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs"
  - statement: "`architecture-flows-event-ingestion` already documents, step by step, the full ordered write-path pipeline these admission gates sit inside (community fence, categorical rejections, signature verification, timestamp/size bounds, pubkey match, scope check, channel resolution, storage, fan-out); `architecture-flows-historical-query` and `architecture-flows-search-query` already document the full ordered read-path pipeline including the three shared pre-DB filter gates. This node documents the admission gates themselves as a cross-cutting component — their responsibility, interface and dependencies — rather than repeating either ordered flow."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/flows/historical-query.md"
      - "launchpad/docs/corpus/architecture/flows/search-query.md"
  - statement: "No `platforms`-specific corpus template exists yet, so this node follows the path-based convention this Feature's sibling tasks have settled on — `type: platforms` for documents under `launchpad/docs/corpus/platforms/**` — rather than inventing a second, competing convention; the body's section shape (Responsibility, Public interface, Dependencies, Boundary) is borrowed from `templates/component.md` because issue #1262's own Definition-of-Done bullets restate that template's required sections almost verbatim, even though `component.md` itself prescribes `type: implementation`."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.6
---

# Relay admission: authorization gates

How `buzz-relay` decides whether an already-authenticated request — a write
(event ingest) or a read (subscription `REQ`, HTTP `/query`, HTTP `/count`) —
is actually admitted to proceed. Admission here is not one function; it is a
small set of gates, reused across transports, that check tenant serving
state, permission scope, channel membership, moderation restriction, and
gated-content ownership before a request's own logic ever runs.

## Responsibility

The admission gates decide, independently of each other, whether a request
may proceed:

- **Tenant serving state** — `is_serving_active` refuses writes to an
  archived, deleted, or otherwise non-serving community before any other
  check runs.
- **Permission scope** — `required_scope_for_kind` (write path) and the
  inline `Scope::MessagesRead` check in `handle_req` (read path) refuse a
  request when the authenticated principal's granted `buzz_auth::Scope` set
  does not cover the operation.
- **Channel membership/visibility** — `check_channel_membership` and the
  legacy `check_token_channel_access` refuse a channel-scoped write when the
  caller is neither a member nor the channel is open, or when a
  channel-restricted token does not cover the target channel.
- **Moderation restriction** — a durable ban/timeout re-check via
  `moderation_restriction_state` refuses a write from a banned or
  currently-timed-out pubkey, as a backstop independent of live
  disconnect broadcasts.
- **Gated-content ownership** — `p_gated_filters_authorized` refuses a read
  filter that could match a `#p`-gated kind (gift wraps, membership
  notifications, and similar) unless the filter's `#p` tag names the caller.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `required_scope_for_kind(kind, event)` | fn | Maps an event kind to the `Scope` required to write it; `Err` for an unrecognized kind | `crates/buzz-relay/src/handlers/ingest.rs` |
| `check_channel_membership(tenant, state, ch_id, pubkey_bytes, channel)` | async fn | Admits if the pubkey is a channel member or the channel is open-visibility | `crates/buzz-relay/src/handlers/ingest.rs` |
| `check_token_channel_access(auth, channel_id)` | fn | Legacy: rejects if a channel-restricted API token does not cover `channel_id`; a no-op in pure-Nostr mode | `crates/buzz-relay/src/handlers/ingest.rs` |
| `is_serving_active(community)` | async fn (`buzz-db`) | `true` only if the community is not archived, not deleted, and `deletion_state = 'active'` | `crates/buzz-db/src/store/deletion.rs` |
| `moderation_restriction_state(community, pubkey)` | async fn (`buzz-db`) | Returns current ban/timeout state for a pubkey in a community | `crates/buzz-db/src/store/moderation.rs` |
| `handle_req`'s inline scope check | code path | Closes a `REQ` subscription with `"restricted: insufficient scope"` unless `scopes` is empty (pure-Nostr) or contains `MessagesRead` | `crates/buzz-relay/src/handlers/req.rs` |
| `p_gated_filters_authorized(filters, authed_pubkey_hex)` | fn | Rejects a filter matching a `P_GATED_KINDS` kind unless its `#p` tag names the caller; shared by WS `REQ`, HTTP `/query`, HTTP `/count` | `crates/buzz-relay/src/handlers/req.rs` (also called from `crates/buzz-relay/src/api/bridge.rs`, `crates/buzz-relay/src/handlers/count.rs`) |
| `buzz_auth::scope::Scope` | enum | The closed-but-forward-compatible permission-scope type every gate above checks against | `crates/buzz-auth/src/scope.rs` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-auth` | Supplies the `Scope` type every scope gate checks against | `crates/buzz-relay/Cargo.toml` |
| `buzz-db` | Supplies `is_serving_active`, `moderation_restriction_state`, and the channel-membership/visibility queries `check_channel_membership` reads | `crates/buzz-relay/Cargo.toml` |
| `buzz-core` | Supplies `P_GATED_KINDS` and the kind-classification helpers `required_scope_for_kind` matches against | `crates/buzz-relay/Cargo.toml` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/handlers/ingest.rs` | Calls every write-path gate (`is_serving_active`, `required_scope_for_kind`, `check_channel_membership`, `check_token_channel_access`, `moderation_restriction_state`) | `crates/buzz-relay/src/handlers/ingest.rs` |
| `crates/buzz-relay/src/handlers/req.rs` | Calls the read-path scope check and defines/calls `p_gated_filters_authorized` for WS `REQ` | `crates/buzz-relay/src/handlers/req.rs` |
| `crates/buzz-relay/src/handlers/count.rs` | Calls `p_gated_filters_authorized` for HTTP `/count` | `crates/buzz-relay/src/handlers/count.rs` |
| `crates/buzz-relay/src/api/bridge.rs` | Calls `p_gated_filters_authorized` for HTTP `/query`, and constructs the `Scope::all_known()` grant for pure-Nostr HTTP auth | `crates/buzz-relay/src/api/bridge.rs` |

## Boundary

This node does not describe:

- **The full ordered write-path pipeline** these gates sit inside — signature
  verification, timestamp/size bounds, storage, side effects, fan-out. See
  `architecture-flows-event-ingestion`.
- **The full ordered read-path pipeline** these gates sit inside — filter
  parsing, historical scan, subscription registration, EOSE. See
  `architecture-flows-historical-query` and `architecture-flows-search-query`.
- **NIP-42/NIP-98 authentication mechanics** — how a connection or request
  becomes authenticated in the first place is a distinct concern from
  authorizing what an already-authenticated principal may do; owned by
  `crates/buzz-auth/src/nip42.rs` and `nip98.rs`, neither opened for this
  node.
- **`crates/buzz-auth/src/access.rs`'s `check_read_access`/`check_write_access`/
  `ChannelAccessChecker`.** These are defined in `buzz-auth` but, per this
  node's own evidence, called from nowhere else in the repository. This node
  does not claim they are the live admission mechanism — the gates
  documented above are the ones actually wired into `buzz-relay`'s handlers.
- **The relay container's own deployment topology.** See
  `architecture-containers-relay`.
- **The roughly thirty per-kind structural validators** inside
  `ingest_event_inner` (edit ownership, forum-vote target, and similar) —
  those are content-shape validators, not admission gates, and are already an
  explicit named gap in `architecture-flows-event-ingestion`.

## Relationships

- part-of: architecture-containers-relay
- references: architecture-flows-event-ingestion
- references: architecture-flows-historical-query
- references: architecture-flows-search-query

## Scope and omissions

**This node covers** the admission gates `buzz-relay` evaluates before
admitting a write or read request — tenant serving state, permission scope,
channel membership/visibility, moderation restriction, and gated-content
ownership — as a cross-cutting component: their responsibility, public
interface, and dependency edges, independent of either transport's own
ordered pipeline.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full ordered write-path ingest pipeline | `architecture-flows-event-ingestion` |
| The full ordered read-path query/subscription pipeline | `architecture-flows-historical-query`, `architecture-flows-search-query` |
| NIP-42/NIP-98 authentication mechanics | `crates/buzz-auth/src/nip42.rs`, `nip98.rs` (not yet a corpus node) |
| The relay container's deployment topology | `architecture-containers-relay` |
| Per-kind content-shape structural validators | `architecture-flows-event-ingestion` (named as its own gap) |

**Expected but not verified when this node was written:**

- **Whether `buzz-auth::access`'s `check_read_access`/`check_write_access`/
  `ChannelAccessChecker` are dead code, reserved for a not-yet-wired future
  path, or a deliberate parallel API for an external consumer of the
  `buzz-auth` crate was not determined.** This node only establishes, by
  repository-wide search, that nothing in this repository currently calls
  them.
- **Whether `P_GATED_KINDS`, `RESULT_GATED_KINDS`, and `SHARED_GATED_KINDS`
  (all referenced alongside `p_gated_filters_authorized` in
  `crates/buzz-relay/src/handlers/req.rs`) name exactly the same or a
  different set of kinds was not compared.** Only `P_GATED_KINDS` was
  inspected for this node; the other two gated-kind sets are out of scope
  here.
- **Whether `handle_req`'s inline scope check has an exact HTTP-bridge
  counterpart for `/query`/`/count`, beyond the shared `p_gated_filters_authorized`
  call, was not checked.** This node verified the WS `REQ` scope check
  directly but did not trace whether `bridge.rs`'s `/query` and `/count`
  handlers apply an equivalent `MessagesRead` scope check before or after
  the shared gate.
