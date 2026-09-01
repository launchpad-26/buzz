---
id: interfaces-nostr-nip-11
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
  - statement: "Upstream NIP-11 (Relay Information Document) defines a JSON document served over HTTP(S) on the same URI as the relay's WebSocket, returned when a request carries `Accept: application/nostr+json` to a URI supporting WebSocket upgrades, with fields including name, description, banner, icon, pubkey, self, contact, supported_nips, software, version and terms_of_service, and states that any field may be omitted and clients MUST ignore unrecognized additional fields."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/11.md"
  - statement: "Upstream NIP-11 states relays MUST accept CORS requests by sending Access-Control-Allow-Origin, Access-Control-Allow-Headers and Access-Control-Allow-Methods headers, and defines an optional `limitation` object (max_message_length, max_subscriptions, max_limit, max_subid_length, max_event_tags, max_content_length, min_pow_difficulty, auth_required, payment_required, restricted_writes, created_at_lower_limit, created_at_upper_limit, default_limit) describing practical request limits a client should expect enforced."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/11.md"
  - statement: "`crates/buzz-relay/src/nip11.rs` defines the `RelayInfo` struct (name, description, icon, pubkey, contact, supported_nips, supported_extensions, push, software, version, limitation, pairing_relay_url, admin_api, gif, and `self` renamed via serde from `relay_self`), documented in its own doc comment as \"Relay information document served at GET / with Accept: application/nostr+json\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`SUPPORTED_NIPS` in `nip11.rs` is a sorted, module-level constant listing NIPs 1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50 and 56 as unconditionally supported, verified sorted by `supported_nips_are_sorted` and individually asserted by `supported_nips_includes_nip23_and_nip33`, `supported_nips_includes_nip38` and `supported_nips_includes_nip56`; NIP-43 (relay membership, `NIP_RELAY_MEMBERSHIP`) is deliberately excluded from this static list and is instead advertised conditionally by `RelayInfo::build`, confirmed by `nip43_not_in_static_supported_nips`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`RelayInfo::build` (in `nip11.rs`) takes only static and pre-derived-scalar inputs (relay_self, icon, advertise_nip43, max_message_length, pairing_relay_url, admin_api, gif_provider) and is pinned to that exact signature by the module-level `_RELAY_INFO_BUILD_STATIC_INPUT_FENCE` const, whose doc comment states the fence exists so the function \"cannot become an enumeration oracle for other communities\" and that any added unscoped DB/search/audit input is a compile break."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`relay_limitation` in `nip11.rs` sets `auth_required: true` unconditionally, and its doc comment states this is because the REQ, EVENT and COUNT WebSocket handlers unconditionally reject any connection not in `AuthState::Authenticated`, independent of the REST API token toggle -- i.e. `auth_required` describes the WebSocket protocol surface, not a requirement to authenticate before reading the NIP-11 document itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`relay_limitation`'s `max_limit` field is `buzz_db::DEFAULT_MAX_PAGE_LIMIT`, the same constant the REQ filter-clamping path uses, so the advertised ceiling and the enforced one are the same value by construction rather than two numbers that could drift apart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`RelayInfo`'s `version` field is populated from `env!(\"CARGO_PKG_VERSION\")` and `software` is the fixed string \"https://github.com/block/buzz\", confirmed by the `build_advertises_buzz_repository_url` test."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "Beyond the fields upstream NIP-11 itself defines, `RelayInfo` carries Buzz-specific extensions: `push` (a NIP-PL executor descriptor, present only when push delivery is configured, built by `push_descriptor`), `pairing_relay_url` (the NIP-AB device-pairing relay's public WebSocket URL), `admin_api` (the admin console's canonical origin, present only when an admin surface is configured), `gif` (a relay-owned, provider-agnostic GIF-search descriptor gated on `gif_provider`, asserted credential-free by `gif_descriptor_and_extension_are_config_gated_and_credential_free`), and `self` (the relay's own NIP-43 signing pubkey). Their presence is advertised in `supported_extensions` (`nip-er` unconditionally, plus `buzz-gif` and/or `nip-pl` when configured)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "`crates/buzz-relay/src/router.rs` registers `GET /` to `nip11_or_ws_handler` (a content-negotiated handler) and `GET /info` to `relay_info_handler` (which unconditionally returns the NIP-11 document as JSON regardless of the `Accept` header), both inside `build_router`'s `api_router`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`nip11_or_ws_handler` returns the NIP-11 JSON document whenever the request's `Accept` header contains `application/nostr+json`; otherwise it attempts a WebSocket upgrade after binding the request host to a community via `tenant::bind_community`, and on non-WS requests whose upgrade fails, falls back to serving the NIP-11 document as JSON (or the git web SPA's `index.html` when `serve_git_web_gui` is enabled and `Accept` contains `text/html`). The NIP-11 branch runs before host binding, so it never depends on `tenant::bind_community` succeeding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`nip11_or_ws_handler`'s own comment states the fail-open/fail-closed split explicitly: \"NIP-11 above is served before binding and stays fail-open: an unmapped host still gets the document ... so the doc cannot leak which hosts are mapped,\" while an unmapped host's *WebSocket-upgrade or non-`nostr+json`* request is rejected with a generic 404 body that never echoes the requested host, via `tenant::bind_community`'s `Err` branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`build_router` layers `build_cors_layer(&state.config.cors_origins)` over the merged router (which includes the `/` and `/info` routes), and `build_cors_layer` returns `CorsLayer::permissive()` when no `cors_origins` are configured, or an explicit allow-list with `Any` methods/headers otherwise -- satisfying upstream NIP-11's stated MUST that relays accept CORS requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "No authentication middleware wraps `build_router`'s `api_router` as a whole; the only layers applied to the merged router are `track_metrics`, an HTTP trace layer and the CORS layer -- so `GET /` and `GET /info` are reachable, and the NIP-11 document is readable, without any credential."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The integration test `crates/buzz-test-client/tests/e2e_relay.rs::test_nip11_relay_info` (marked `#[ignore]`, requiring a live relay) asserts `GET /info` returns a successful status and a JSON body containing `name`, `description`, `supported_nips` and `version`, and that `limitation.max_subscriptions` equals 1024 and `limitation.auth_required` is `true`, with an inline comment attributing `auth_required` to the REQ/EVENT/COUNT handlers' unconditional authentication requirement."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "`crates/buzz-test-client/tests/conformance_multitenant.rs`'s `nip11_relay_info` module (also `#[ignore]`d, live-relay only) asserts that fetching NIP-11 with `Accept: application/nostr+json` from two different mapped communities (hosts A and B) returns 200 for both, with identical JSON bodies once each community's own `icon` field is stripped -- proving the unauthenticated document is not a cross-community enumeration oracle -- and that an *unmapped* host also receives 200 with the same static document rather than a 404, because a status difference between mapped and unmapped hosts would itself be an enumeration oracle on that door."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "The same test file's `row_zero_host_binding::unmapped_host_fails_closed_generically` test asserts the opposite behavior on the *other* door: a request to an unmapped host with a non-`application/nostr+json` `Accept` header (i.e. the WebSocket-upgrade / SPA-fallback path) returns 404 with a body that echoes neither the requested host's authority nor its bare label, while a mapped host does not 404 on that same door, and a raw WebSocket handshake to the unmapped host is rejected at the upgrade itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "The corpus template for interface-shaped nodes (`corpus-template-interface`) states that a node built from it carries `type: interfaces-events`, the single enum value node.schema.json uses for both interface- and event-kind-shaped subjects, and recommends `implements` (target: `corpus-template-interface`) over `references` for a node's optional self-link to its own template, while leaving that convention unsettled corpus-wide."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "The relay information document is a facet of the relay container's own HTTP surface, which the merged `architecture-containers-relay` node documents at the container level; this node documents one interface of that container rather than duplicating the container node's content."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.75
---

# NIP-11: Relay Information Document

This interface is the HTTP-fetchable relay-information document Buzz serves under
upstream Nostr [NIP-11](https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/11.md).
A client and the relay exchange no messages beyond a single unauthenticated HTTP GET
and a JSON response body: the client asks "what are you, and what can I rely on?" and
the relay answers with a static-per-deployment, host-scoped-only-in-its-`icon`-field
document. It is the one HTTP surface in this repository that both upstream Nostr and
Buzz's own multi-tenant conformance discipline treat as intentionally readable by
anyone, unauthenticated, from any host this relay serves.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `GET /` with `Accept: application/nostr+json` | `crates/buzz-relay/src/router.rs::nip11_or_ws_handler` (dispatches to `crates/buzz-relay/src/nip11.rs::nip11_document`) | Content-negotiated: returns the NIP-11 JSON document. The same route upgrades to a WebSocket connection instead when `Accept` does not request `application/nostr+json` and the request is a valid WS upgrade. |
| `GET /info` | `crates/buzz-relay/src/nip11.rs::relay_info_handler` | Unconditionally returns the NIP-11 JSON document as `application/json`, regardless of the request's `Accept` header. Exists so a caller can fetch the document without content negotiation. |
| Non-WS, non-`nostr+json` `GET /` (fallback) | `crates/buzz-relay/src/router.rs::nip11_or_ws_handler` | When the WebSocket-upgrade attempt fails and `serve_git_web_gui` + `text/html` do not apply, the same NIP-11 JSON document is served as the fallback body. |

Both routes build the served document through the same function,
`crates/buzz-relay/src/nip11.rs::nip11_document`, so the content-negotiated and
dedicated doors cannot drift apart from each other.

## Contract and stability

**Unauthenticated and host-agnostic by design.** `build_router` applies no
authentication middleware around `GET /` or `GET /info` — the merged router's only
layers are metrics, HTTP tracing and CORS. This is intentional, not an oversight:
`conformance_multitenant.rs`'s `nip11_relay_info` test module proves the served
document is byte-identical (once each community's own `icon` is stripped) whether
fetched from community A, community B, or a host mapped to no community at all, and
`RelayInfo::build`'s inputs are pinned by a compile-time const
(`_RELAY_INFO_BUILD_STATIC_INPUT_FENCE`) to static/scalar values only — an
unauthenticated NIP-11 read can never become an oracle for enumerating other
communities on the same deployment.

**`auth_required: true` describes a different surface than this one.** The
`limitation.auth_required` field the document itself advertises is `true`
unconditionally, but that reflects the relay's REQ/EVENT/COUNT WebSocket handlers
(which unconditionally require `AuthState::Authenticated`), not a requirement to
authenticate before reading the NIP-11 document — reading `GET /` or `GET /info`
itself needs no credential.

**No rejection path for the document read itself.** Upstream NIP-11 defines no
failure mode for the relay-information request; Buzz adds none. The one
host-dependent divergence in behavior lives on a *different* door: a WebSocket
upgrade or non-`nostr+json` request to a host this relay does not map to any
community is rejected generically (404, body naming neither the host nor the
failure mode — `row_zero_host_binding::unmapped_host_fails_closed_generically`),
while the identical request with `Accept: application/nostr+json` still returns 200
with the static document. See *Examples* below.

**Versioning.** `version` is the crate's own `CARGO_PKG_VERSION` at build time;
`software` is the fixed string `https://github.com/block/buzz`. Neither is
independently configurable per deployment. `supported_nips` is a sorted,
compile-time list (`SUPPORTED_NIPS`) plus a runtime-conditional entry for NIP-43,
added only when the relay has a stable signing key *and* enforces membership
(`advertise_nip43`) — a `debug_assert!` in `RelayInfo::build` fails fast if NIP-43 is
requested without a stable key, because NIP-43 events are verified against the
document's own `self` field.

**Ordering / idempotency.** This is a stateless read with no ordering guarantee
between requests: two consecutive fetches can return different bodies if
per-deployment configuration changes between them (e.g. an admin sets a workspace
icon, or push delivery becomes configured), but a single fetch is otherwise a pure
function of current config plus the requesting host's `icon`. There is no
Nostr-event-style `created_at`/replaceable-event ordering involved, because this
interface is plain HTTP, not a signed Nostr event.

**Buzz extensions beyond upstream NIP-11.** `push` (NIP-PL executor descriptor),
`pairing_relay_url` (NIP-AB pairing relay), `admin_api` (admin console origin),
`gif` (relay-proxied GIF search descriptor) and `self` (NIP-43 relay identity) are
Buzz-specific fields advertised alongside the upstream-defined ones; their presence
is separately flagged in `supported_extensions`. Per upstream NIP-11's own
compatibility rule, clients MUST ignore additional fields they do not understand, so
these extensions cannot break a spec-conforming client.

## Examples

**Valid example** — an open relay with a stable signing key configured for GIF
search, reduced to the fields these facts establish (see `crates/buzz-relay/src/nip11.rs`
tests `gif_descriptor_and_extension_are_config_gated_and_credential_free` and
`build_open_relay_stable_key_advertises_self_but_not_nip43`):

```json
{
  "name": "Buzz Relay",
  "description": "Buzz — private team communication relay",
  "self": "0000000000000000000000000000000000000000000000000000000000000001",
  "supported_nips": [1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56],
  "supported_extensions": ["nip-er", "buzz-gif"],
  "gif": {
    "provider": "klipy",
    "search": "/gifs/search",
    "share": "/gifs/share"
  },
  "software": "https://github.com/block/buzz",
  "version": "<CARGO_PKG_VERSION>",
  "limitation": {
    "max_message_length": 262144,
    "max_subscriptions": 1024,
    "max_filters": 10,
    "max_limit": 500,
    "max_subid_length": 256,
    "min_pow_difficulty": null,
    "auth_required": true,
    "payment_required": false,
    "restricted_writes": true,
    "due_delivery_mode": "push",
    "max_not_before_delta": 31536000
  }
}
```

(`max_limit` here is illustrative of `buzz_db::DEFAULT_MAX_PAGE_LIMIT`'s shape, not a
literal value opened from that constant in this pass.)

**Failure / edge example** — an unmapped host still gets 200 on the NIP-11 door, but
404s on every other door (`conformance_multitenant.rs`'s
`nip11_is_not_a_cross_community_enumeration_oracle` and
`row_zero_host_binding::unmapped_host_fails_closed_generically`):

```
GET / HTTP/1.1
Host: unknown.localhost
Accept: application/nostr+json

-> 200 OK, the same static NIP-11 document any mapped host receives (no `icon`)

GET / HTTP/1.1
Host: unknown.localhost
Accept: text/html

-> 404 Not Found
   "relay: no community is configured for this host"
```

## Boundary

This node does not describe:
- **Any single Nostr event kind's own wire contract** (tag shape, content semantics,
  referenced NIP) — NIP-11 is a document-fetch interface, not an event kind, and this
  node references no event-kind node because none is merged in this corpus yet.
- **A field-by-field, parameter-by-parameter catalogue** of every NIP-11 field for
  domain-expert readers — see the interface template's own boundary against a future
  reference-depth node, which does not exist yet either.
- **The WebSocket protocol surface itself** (NIP-01/NIP-29 event exchange, REQ/EVENT/
  COUNT authentication) — this node cites `auth_required`'s true meaning but does not
  document that surface's own contract.
- **Changes to `nip11.rs` or `router.rs`** — this node documents existing, already
  tested behavior at the recorded revision; it makes no runtime change.

## Relationships

- implements: corpus-template-interface
- part-of: architecture-containers-relay

## Scope and omissions

**This node covers** the NIP-11 relay-information document as Buzz implements it:
its two HTTP entry points, the content-negotiation and fallback behavior between
them, its unauthenticated/host-agnostic contract and the evidence for that contract,
its versioning fields, the Buzz-specific extensions layered on top of the
upstream-defined fields, and one valid and one failure/edge example.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A single Nostr event kind's own wire contract | a future event-kind corpus node (none merged yet) |
| Field-by-field API-parameter cataloguing for domain experts | a future reference-depth corpus node (undecided, per the interface template) |
| The WebSocket REQ/EVENT/COUNT authentication contract itself | a future corpus node on that surface |
| The NIP-PL push-delivery descriptor's own wire contract | a future corpus node on push delivery |

**Expected but not verified when this node was written:**
- **The literal numeric value of `buzz_db::DEFAULT_MAX_PAGE_LIMIT`** was not opened
  from `buzz-db`'s own source in this pass; the *Valid example* above marks its
  `max_limit` value as illustrative rather than a verified literal for that reason.
- **No live relay was run.** Both integration test suites cited here
  (`e2e_relay.rs::test_nip11_relay_info` and `conformance_multitenant.rs`'s
  `nip11_relay_info` and `row_zero_host_binding` modules) are `#[ignore]`d,
  live-relay-only tests; their assertions were read from source, not executed, in
  this pass.
- **Whether `implements` or `references` is the corpus-wide convention** for a
  node's optional self-link to its own template remains unsettled, per the
  template's own note; this node follows the template's stated preference
  (`implements`).
