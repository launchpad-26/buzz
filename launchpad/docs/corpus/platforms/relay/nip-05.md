---
id: platforms-relay-nip-05
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The relay routes `GET /.well-known/nostr.json` to `api::nip05::nostr_nip05`, alongside the rest of the axum router's public HTTP surface (WebSocket, HTTP bridge, media, git, NIP-05, health probes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:66"
  - statement: "`nostr_nip05` requires no authentication and is documented as a public discovery endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:22-23"
  - statement: "`nostr_nip05` binds the request's community from the request's `Host` header via `crate::tenant::bind_community` (row zero) before doing any tenant-scoped lookup; an unmapped host, or a request with no `name` query parameter, falls through to the empty `{\"names\":{},\"relays\":{}}` response rather than a default tenant or an error that would reveal which communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:24-65"
  - statement: "When a community is bound and a `name` query parameter is present, the handler lowercases the name, derives the expected domain from the bound tenant's own host (not the process-global `relay_url`), and looks up the user via `state.db.get_user_by_nip05(tenant.community(), &name, &domain)`; a hit returns `{\"names\":{name: hex_pubkey}, \"relays\":{hex_pubkey: [relay_url]}}`, everything else returns the empty document."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:41-64"
  - statement: "The response always carries `Access-Control-Allow-Origin: *`, permitting cross-origin reads of the NIP-05 document from any web origin."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:67-72"
  - statement: "The advertised relay URL for a resolved handle is built by `relay_url_for_tenant_host`, which keeps the `ws`/`wss` scheme from the deployment's configured `relay_url` but substitutes the bound tenant's own host — never the globally configured host — so a client on tenant host A is pointed back at A, not at the deployment's default `relay_url`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:105-112"
  - statement: "`extract_domain` strips a leading `wss://`, `ws://`, `https://` or `http://` scheme and any trailing port or path segment from a URL or host string, returning the lowercased bare hostname (defaulting to `\"localhost\"` if nothing remains)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:116-128"
  - statement: "A NIP-05 handle is only ever set through `canonicalize_nip05`, which requires the `local@domain` shape, rejects an empty local part or domain, and requires the domain to case-insensitively match the domain extracted from the caller-supplied `expected_host_or_url` — returning the lowercased canonical `local@domain` string on success or a descriptive error string otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:79-99"
  - statement: "Two inline unit tests in `nip05.rs` cover `canonicalize_nip05` accepting a handle matching the bound tenant host and rejecting one matching only the (different) configured relay URL, and `relay_url_for_tenant_host` preserving the config's scheme while substituting the tenant host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:134-153"
  - statement: "The relay-side registration path for a NIP-05 handle is the kind:0 (NIP-01 profile metadata) ingest side effect, `handle_kind0_profile`: it reads the event content's `nip05` field, passes it through `canonicalize_nip05(raw, tenant.host())`, and on success stores the canonical handle via `update_user_profile`; on failure (missing field, malformed shape, or domain mismatch) the handle is silently cleared (treated as absent) rather than the event being rejected, because the event itself is already persisted and cannot be rejected at this stage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1296-1305"
  - statement: "kind:0 is treated as absolute state: `handle_kind0_profile` always passes `Some(nip05_handle)` (possibly the empty string, which `update_user_profile` treats as clearing the column) so a field omitted from a later kind:0 event clears any previously stored handle rather than leaving the old one in place."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1280-1282"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1321-1335"
  - statement: "If `update_user_profile` fails with a Postgres unique-constraint violation (the handle is already taken by another user in the same community), `handle_kind0_profile` logs a warning and retries the same write with the NIP-05 field set to `None`, so the rest of the profile (display name, avatar, about) still syncs even when the handle is contested; any other database error is propagated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1336-1356"
  - statement: "`get_user_by_nip05(pool, community_id, local_part, domain)` looks up a user by the exact, case-insensitive `local_part@domain` handle, scoped to `community_id`, via `WHERE community_id = $1 AND LOWER(nip05_handle) = LOWER($2)`. Both `local_part` and `domain` must already be lowercased by the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs:169-209"
  - statement: "`users.nip05_handle` is a nullable `VARCHAR(255)` column, and `idx_users_nip05` is a partial unique index on `(community_id, lower(nip05_handle))` that only applies `WHERE nip05_handle IS NOT NULL` — so multiple users may have no handle, but within one community no two non-null handles may collide case-insensitively, and the same local part may exist in two different communities without conflict."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:157"
      - "migrations/0001_initial_schema.sql:178-179"
  - statement: "`bind_community` is the shared row-zero tenant-binding entry point used by `nostr_nip05` (and by every other public door in the relay): it normalizes the raw host, resolves it through a `HostResolver`, and fails closed (`BindError::UnmappedHost` or `BindError::Lookup`) on any unmapped host, empty/whitespace host, or lookup error — there is deliberately no default/fallback community path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:61-92"
  - statement: "The row-zero host-binding pattern `nostr_nip05` depends on (`bind_community`, fail-closed on unmapped host, no default tenant) is already documented at the principle level by the corpus node `architecture-principles-host-selects-community`; this node references that node rather than re-describing the mechanism."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
  - statement: "A multi-tenant conformance test module, `users_profiles_nip05` in `conformance_multitenant.rs`, exercises the full registration-then-lookup path: two communities each register the same local part `alice` under distinct pubkeys via kind:0 `{\"nip05\": \"...\"}`, and `same_nip05_local_part_on_two_hosts_is_independent` asserts `GET /.well-known/nostr.json?name=alice` on each host resolves to that host's own pubkey and advertises that host's own relay URL in `relays`, never the other community's or the global `relay_url`. The test is `#[ignore]`-gated (it requires two live, differently-hosted relay instances) rather than run by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:917-951"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:1117-1226"
  - statement: "No node in the corpus tree merged on origin/launchpad at the recorded revision lives under `platforms/**`, and no `platforms`-specific template exists in `launchpad/docs/corpus/templates/`; this node borrows `templates/component.md`'s section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) as the closest existing fit for a single HTTP endpoint's behavior, pending a platforms-specific template."
    entry_class: INFERENCE
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no platforms/ entries, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-principles-host-selects-community
---

# Relay NIP-05 identity verification endpoint

This node documents `GET /.well-known/nostr.json`, the relay's NIP-05
identifier-verification HTTP endpoint (`crates/buzz-relay/src/api/nip05.rs`):
what it accepts, how it resolves a handle to a pubkey inside a multi-tenant
relay, and how a handle gets registered in the first place. It answers "what
does this one endpoint do and what does it depend on", not "how does the
relay's whole HTTP surface work."

## Responsibility

The endpoint implements NIP-05 (DNS-based identifier verification for Nostr):
given a `name` query parameter, it returns a JSON document mapping that local
part to a hex-encoded pubkey and advertising the relay URL a client should use
to reach that pubkey's home relay, per the standard `{"names": {...}, "relays":
{...}}` shape. It requires no authentication — it is a public discovery
endpoint (`crates/buzz-relay/src/api/nip05.rs:22-23`) — and always responds
with CORS enabled (`Access-Control-Allow-Origin: *`,
`crates/buzz-relay/src/api/nip05.rs:67-72`) so a browser on any origin can
fetch it directly.

Because this relay is multi-tenant (one deployment can host several
communities, each bound to its own request `Host`), the endpoint's first
responsibility before any lookup is **row-zero host binding**: resolving the
request's community from its `Host` header via `crate::tenant::bind_community`
(`crates/buzz-relay/src/api/nip05.rs:24-40`). That binding mechanism — fail
closed on an unmapped host, no default tenant — is the same shared mechanism
every other public door in the relay uses, and is documented at the principle
level by `architecture-principles-host-selects-community`; see *Relationships*
below.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `GET /.well-known/nostr.json?name=<local-part>` | HTTP route | Public, unauthenticated. Returns `{"names": {name: hex_pubkey}, "relays": {hex_pubkey: [relay_url]}}` on a resolved handle in a bound community; `{"names": {}, "relays": {}}` for an unmapped host, a missing `name`, or no matching user. Always sets `Access-Control-Allow-Origin: *`. | `crates/buzz-relay/src/router.rs:66`, `crates/buzz-relay/src/api/nip05.rs:22-73` |
| `canonicalize_nip05(raw: &str, expected_host_or_url: &str) -> Result<String, String>` | fn (crate-internal, `pub(crate)`) | Validates `raw` is `local@domain`, requires `domain` to case-insensitively match the domain extracted from `expected_host_or_url`, returns the lowercased canonical handle or a descriptive error. The sole gate through which any handle enters storage. | `crates/buzz-relay/src/api/nip05.rs:79-99` |
| `relay_url_for_tenant_host(config_relay_url: &str, tenant_host: &str) -> String` | fn (crate-internal, `pub(crate)`) | Keeps the `ws`/`wss` scheme from the deployment's configured relay URL, substitutes the bound tenant's own host. | `crates/buzz-relay/src/api/nip05.rs:105-112` |
| `extract_domain(url: &str) -> String` | fn (crate-internal, `pub(crate)`) | Strips a leading scheme and any trailing port/path, lowercases, defaults to `"localhost"`. | `crates/buzz-relay/src/api/nip05.rs:116-128` |

## Dependencies

**Depends on** (this endpoint requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `crate::tenant::bind_community` (this crate, `buzz-relay`) | Row-zero host-to-community binding before any tenant-scoped lookup. | `crates/buzz-relay/src/api/nip05.rs:39`, `crates/buzz-relay/src/tenant.rs:61-92` |
| `state.db.get_user_by_nip05` (`buzz-db`) | The community-scoped, case-insensitive handle lookup the endpoint calls. | `crates/buzz-relay/src/api/nip05.rs:47-51`, `crates/buzz-db/src/store/user.rs:169-209` |
| `users.nip05_handle` column + `idx_users_nip05` partial unique index (Postgres, via `buzz-db`) | Storage and per-community uniqueness for the handle the lookup reads. | `migrations/0001_initial_schema.sql:157`, `migrations/0001_initial_schema.sql:178-179` |
| `state.config.relay_url` (relay configuration) | Supplies the `ws`/`wss` scheme used when building the advertised relay URL (the host substituted is the tenant's, not this config value's). | `crates/buzz-relay/src/api/nip05.rs:54-55` |

**Depended on by** (these require this endpoint's registration path):

| Component | Why | Evidence |
|---|---|---|
| `handle_kind0_profile` (kind:0 ingest side effect, `buzz-relay`) | The only path that writes a NIP-05 handle; it calls `canonicalize_nip05` against the bound tenant host and, on success, stores the canonical handle via `update_user_profile`. On a unique-constraint collision it retries the write with the handle omitted so the rest of the profile still syncs. | `crates/buzz-relay/src/handlers/side_effects.rs:1296-1305`, `crates/buzz-relay/src/handlers/side_effects.rs:1336-1356` |

## Boundary

This node does not describe:
- Row-zero host-to-community binding itself (`bind_community`, the
  `HostResolver` trait, fail-closed semantics) — see
  `architecture-principles-host-selects-community`, which already documents
  that mechanism; this node only states that `nostr_nip05` uses it.
- The relay's wider public HTTP surface (`/events`, `/query`, `/count`, NIP-11
  `/.well-known/nostr.json`-adjacent content-negotiation, media, git,
  webhooks) — each is its own component, out of scope per this task's own
  Definition of Done ("Explains only component-level behavior, not the entire
  containing platform").
- The full kind:0 profile-sync side effect (display name, avatar, about) —
  only the `nip05` field's validation and write path is in scope here; the
  rest of `handle_kind0_profile` belongs to a profile-sync node, if one is
  written.
- Install/usage instructions for running the relay — `buzz-relay` carries no
  `README.md` at the recorded revision; not this node's subject either way.

## Relationships

- references: `architecture-principles-host-selects-community` — the
  row-zero host-binding mechanism this endpoint uses is documented there; this
  node cites it as supporting context rather than re-explaining the mechanism,
  per the `references` relationship's own directionality ("source cites
  target as supporting context; no ownership or currency dependency
  implied").
- No `depends-on`, `implements`, `supersedes` or `part-of` edge is declared.
  No `platforms/**` node exists yet on `origin/launchpad` at the recorded
  revision (checked via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`) for this node to sit `part-of`, and no
  `implementation-reference` or spec node covering this endpoint exists to
  `implements` against.

## Scope and omissions

**This node covers** the `GET /.well-known/nostr.json` endpoint's contract,
its row-zero tenant binding, its per-community handle lookup and uniqueness
guarantee, and the `canonicalize_nip05`/kind:0 registration path that is the
only way a handle enters storage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Row-zero host-binding mechanism itself | `architecture-principles-host-selects-community` |
| The relay's other public HTTP endpoints (`/events`, `/query`, `/count`, NIP-11, media, git, webhooks) | Their own component nodes, not yet written |
| The rest of `handle_kind0_profile` (display_name/avatar/about sync) | A profile-sync node, if written |
| A `platforms`-specific template's exact required sections | Not yet authored; this node borrows `templates/component.md`'s shape as the closest existing fit (see the front-matter `INFERENCE` above) |

**Expected but not verified when this node was written:**

- **Live behavior of `same_nip05_local_part_on_two_hosts_is_independent`.**
  This test is `#[ignore]`-gated and requires two live, differently-hosted
  relay instances; its assertions were read but the test itself was not run
  as part of authoring this node.
- **Client-side consumption of the returned document** (how the CLI, desktop,
  or mobile app use a resolved NIP-05 document) was not inspected; this node
  documents only the relay-side endpoint.
