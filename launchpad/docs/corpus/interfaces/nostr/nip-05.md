---
id: interfaces-nostr-nip-05
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
  - statement: "The relay serves NIP-05 identity verification at `GET /.well-known/nostr.json`, implemented by `nostr_nip05` and registered in the route table alongside the rest of Buzz's narrow HTTP surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:22-73"
      - "crates/buzz-relay/src/router.rs:66"
  - statement: "The endpoint takes an optional `name` query parameter and first binds the request to a community from the `Host` header (the same tenant-binding path the WebSocket door and NIP-11 use); an unmapped host falls through to an empty `{names:{}, relays:{}}` body rather than a default tenant or an error that would leak which communities exist on the deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:24-46"
      - "crates/buzz-relay/src/tenant.rs:69"
  - statement: "A successful lookup returns `{\"names\": {\"<local-part>\": \"<hex pubkey>\"}, \"relays\": {\"<hex pubkey>\": [\"<relay url>\"]}}`; the advertised relay URL is built from the config's scheme (`ws`/`wss`) but the *bound tenant's own host*, not the process-global configured host, since each community can be reached at its own host in a multi-tenant deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:47-59"
      - "crates/buzz-relay/src/api/nip05.rs:101-112"
  - statement: "The endpoint's doc comment states it requires no authentication, matching its purpose as a public discovery endpoint; a permissive `Access-Control-Allow-Origin: *` header is set on every response so browser clients can query it cross-origin."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs:23"
      - "crates/buzz-relay/src/api/nip05.rs:67-72"
  - statement: "A NIP-05 handle is set by including a `nip05` field in a kind:0 (NIP-01 profile metadata, `KIND_PROFILE = 0`) event's JSON content; the relay's kind:0 ingest side effect parses that field and calls `canonicalize_nip05`, which requires the handle's domain to equal the current tenant's bound host — not the relay's static configured URL — case-insensitively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1271-1305"
      - "crates/buzz-core/src/kind.rs:8-9"
      - "crates/buzz-relay/src/api/nip05.rs:79-99"
  - statement: "An invalid or off-domain `nip05` value is never rejected at the event level — the kind:0 event is still accepted and stored as signed and published — the relay instead silently omits/clears the handle in the `users` table side-effect projection, since the signed event itself cannot be un-published once persisted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1297-1305"
  - statement: "Handle storage and lookup live in the `users` table's `nip05_handle` column, matched case-insensitively (`LOWER(nip05_handle) = LOWER($2)`) and constrained by a partial unique index (`community_id, lower(nip05_handle)`) scoped per community, so the same local-part can be registered independently by different communities but not twice within one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/user.rs:169-208"
      - "schema/schema.sql:170"
      - "schema/schema.sql:191-192"
  - statement: "If a kind:0 update's `nip05` value collides with another user's unique-index entry, the relay retries the same profile-sync write with the handle omitted rather than failing the whole update, so `display_name`/`about`/`avatar_url` still sync even when the handle is contested."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:1323-1355"
  - statement: "kind:0 is a NIP-01 *replaceable* event, so only the latest kind:0 per `(community, pubkey)` is stored and the profile (including whichever `nip05` value it carried) always reflects the most recent publish — this is the interface's ordering/idempotency guarantee."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:943-947"
  - statement: "`buzz-sdk` exposes a typed client-side builder, `build_profile`, that accepts an optional `nip05: Option<&str>` argument and serializes it into the kind:0 content object alongside `display_name`/`name`/`picture`/`about` when present."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:545-573"
  - statement: "An end-to-end regression test publishes a kind:0 with a valid, in-domain `nip05` handle, confirms it round-trips through `POST /query` and resolves correctly via `GET /.well-known/nostr.json`, then publishes a second kind:0 with an off-domain handle and confirms the event is still accepted but the handle no longer resolves."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:1067-1215"
  - statement: "A multi-tenant conformance test confirms the domain check is bound to the *request's* tenant host rather than the relay's global config: the same local-part registered as a NIP-05 handle on two different community hosts resolves independently on each host without collision."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:917-1258"
  - statement: "The relay's NIP-11 relay-information document advertises a fixed `SUPPORTED_NIPS` list (1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56) that does not include `5`, even though `/.well-known/nostr.json` fully implements NIP-05 discovery."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:14"
  - statement: "The omission of `5` from `SUPPORTED_NIPS` most likely reflects that constant enumerating protocol-level NIPs negotiated over the WebSocket/event pipeline, while NIP-05 is a separate discovery-only HTTP path outside that negotiation — no code comment or decision record confirms this reasoning directly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs:1-20"
    confidence: 0.5
  - statement: "This node is scoped as the single canonical interface node documenting Buzz's implementation of standard, upstream Nostr NIP-05 — not a Buzz-specific protocol extension."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1007 (parent PRD #616)"
relationships:
  - type: implements
    target: corpus-template-interface
---

# NIP-05: interface

This node documents Buzz's implementation of [NIP-05](https://github.com/nostr-protocol/nips/blob/master/05.md)
("Mapping Nostr keys to DNS-based internet identifiers"), the upstream Nostr
specification for verifying that a human-readable `local-part@domain` handle
resolves to a given public key. The boundary is an unauthenticated HTTP
`GET` request from any client (browser, mobile app, desktop app, or another
relay) against the relay's `/.well-known/nostr.json` path, exchanging a
`name` query parameter for a JSON document mapping names to hex pubkeys and
pubkeys to relay URLs. The handle a client registers travels a second,
separate path: a signed Nostr kind:0 (NIP-01 profile metadata) event whose
JSON content carries an optional `nip05` field, ingested over the relay's
primary WebSocket surface and projected into a Postgres side table that the
HTTP lookup reads from. Two sides, two different transports, one identifier.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `GET /.well-known/nostr.json?name=<local-part>` | `crates/buzz-relay/src/api/nip05.rs::nostr_nip05`, registered at `crates/buzz-relay/src/router.rs:66` | Public, unauthenticated NIP-05 identity lookup. Binds the request to a community via `Host`, then resolves `<local-part>@<tenant host>` to a pubkey and relay URL. |
| Publish kind:0 with a `nip05` field | NIP-01 (`crates/buzz-core/src/kind.rs::KIND_PROFILE = 0`); typed client builder `crates/buzz-sdk/src/builders.rs::build_profile` | The only way to *set* a NIP-05 handle. Ingested by `crates/buzz-relay/src/handlers/side_effects.rs::handle_kind0_profile`, which validates and canonicalizes the handle via `crate::api::nip05::canonicalize_nip05` before writing it to `users.nip05_handle`. |
| Handle lookup (internal) | `crates/buzz-db/src/store/user.rs::get_user_by_nip05` | Case-insensitive exact match on `(community_id, nip05_handle)`, enforced unique per community by a partial index on `schema/schema.sql`'s `users` table. |

## Contract and stability

- **No authentication.** `/.well-known/nostr.json` is explicitly documented as
  requiring none — it is a public discovery endpoint, and every response
  carries `Access-Control-Allow-Origin: *` so browser clients can call it
  cross-origin (`crates/buzz-relay/src/api/nip05.rs:23,67-72`).
- **Tenant/host scoping, not a global namespace.** A handle's domain must
  match the *request's* bound tenant host, resolved from `Host` per request,
  not the relay's static `config.relay_url`. The same local-part can be
  registered independently on two different community hosts without
  collision (`crates/buzz-test-client/tests/conformance_multitenant.rs:917-1258`).
- **Errors never reject the underlying event.** An invalid or off-domain
  `nip05` value in a kind:0 event does not cause the relay to reject that
  event — the profile-metadata event is still accepted and stored as any
  other valid signed event would be. Only the *derived* `nip05_handle`
  projection is left cleared, so the handle simply stops resolving via
  `/.well-known/nostr.json` (`crates/buzz-relay/src/handlers/side_effects.rs:1297-1305`).
  A lookup for an unresolvable name returns HTTP 200 with an empty
  `{"names": {}, "relays": {}}` body — never a 404 — matching the upstream
  NIP-05 convention of an always-200 JSON document.
- **Ordering: kind:0 is NIP-01 replaceable.** Only the newest kind:0 per
  `(community, pubkey)` is retained, so the resolvable handle always reflects
  the most recently published profile; there is no way to have two kind:0
  events "race" and leave a stale handle live
  (`crates/buzz-test-client/tests/conformance_multitenant.rs:943-947`).
- **Uniqueness is a hard per-community constraint, not a soft convention.**
  A partial unique index on `(community_id, lower(nip05_handle))` enforces
  one owner per handle within a community at the database level. A
  contested update retries the same profile write with the handle omitted
  rather than losing the rest of the profile sync
  (`schema/schema.sql:170,191-192`; `crates/buzz-relay/src/handlers/side_effects.rs:1323-1355`).

## Boundary

This node does not describe:
- **A single Nostr event kind's own wire contract.** kind:0 (NIP-01 profile
  metadata) is the vehicle that *carries* a `nip05` field, but its full tag
  shape and other content fields (`display_name`, `picture`, `about`, etc.)
  are NIP-01's own contract, not this interface's — no event-kind corpus
  node for kind:0 exists yet in this corpus to `references` instead.
- **NIP-11 (the relay information document).** `GET /` with
  `Accept: application/nostr+json` is a related, but separate, discovery
  interface implemented in `crates/buzz-relay/src/nip11.rs`. Notably, that
  document's `SUPPORTED_NIPS` constant does not list `5`
  (`crates/buzz-relay/src/nip11.rs:14`) even though NIP-05 is fully
  implemented — see the evidence ledger's INFERENCE entry above for why that
  is plausibly correct rather than a gap. No corpus node for NIP-11 exists
  yet to `references`; it is prose-mentioned by filename only.
- **Field-by-field, domain-expert-depth cataloguing** of every profile
  content field kind:0 may carry — only the `nip05` field and its
  validation path are in scope here.

## Relationships

- `implements: corpus-template-interface` — this node is drafted from, and
  follows the required-section shape of, `launchpad/docs/corpus/templates/interface.md`.
- No `references` edge is declared toward a kind:0 event-kind node or a
  NIP-11 interface node: neither exists yet on `origin/launchpad` at the
  recorded revision. Both are named above by filename/path instead, per this
  corpus's rule that an edge naming an unresolved id is a hard validation
  failure, not a soft warning.

## Scope and omissions

**This node covers** the `GET /.well-known/nostr.json` HTTP interface, how a
NIP-05 handle is set via kind:0's `nip05` field and validated/canonicalized
against the request's bound tenant host, the response shapes for both a
resolved and an unresolved/cleared handle, the per-community uniqueness
guarantee, and the ordering guarantee kind:0's replaceable-event semantics
provide.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| kind:0 / NIP-01's full wire contract (all content fields, tag shape) | A future event-kind corpus node for kind:0, not yet created |
| NIP-11's relay information document and its own `SUPPORTED_NIPS` list | A future interfaces-events corpus node for NIP-11, not yet created |
| Field-by-field API-parameter cataloguing for domain-expert readers | A future reference-depth node, if the corpus ever builds one (`#1346`/`#1532`) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |

**Expected but not verified when this node was written:**
- Whether `SUPPORTED_NIPS`'s omission of `5` is intentional design or an
  oversight was not confirmed against any commit message, PR discussion, or
  decision record — only inferred from the surrounding code's own framing
  (see the INFERENCE entry above).
- The upstream NIP-05 specification text itself
  (https://github.com/nostr-protocol/nips/blob/master/05.md) was not fetched
  and read directly while drafting this node; the claims above were checked
  against this repository's own implementation and tests, which independently
  match the well-known `{names, relays}` shape and `/.well-known/nostr.json`
  path the spec defines.

## Examples

**Valid lookup.** A client that has published a kind:0 event with
`{"nip05": "alice@relay.example"}` (accepted because `relay.example` matches
the request's bound tenant host) can later resolve it:

```
GET /.well-known/nostr.json?name=alice HTTP/1.1
Host: relay.example
```

```json
{
  "names": { "alice": "<64-char hex pubkey>" },
  "relays": { "<64-char hex pubkey>": ["wss://relay.example"] }
}
```

**Failure/cleared example.** The same user later publishes a newer kind:0
with `{"nip05": "alice@evil.com"}` — a domain that does not match
`relay.example`. The event is still accepted and stored (NIP-01 replaceable
kind:0 succeeds), but the handle fails `canonicalize_nip05` and is cleared
from the `users` projection, so the same lookup now returns an empty result
rather than an error:

```
GET /.well-known/nostr.json?name=alice HTTP/1.1
Host: relay.example
```

```json
{
  "names": {},
  "relays": {}
}
```

(`crates/buzz-test-client/tests/e2e_relay.rs::test_kind0_nip05_sync` exercises
exactly this valid-then-cleared sequence.)
