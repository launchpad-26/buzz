---
id: platforms-relay-nip-11
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The NIP-11 relay information document is served at `GET /` with `Accept: application/nostr+json`, per nip11.rs's own module and struct doc comments."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:1"
      - "crates/buzz-relay/src/nip11.rs:23-25"
  - statement: "The router registers two GET routes that both serve the NIP-11 document: `/` (content-negotiated with the WebSocket upgrade) and `/info` (always NIP-11, regardless of Accept header), both wired to handlers imported from the nip11 module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:26"
      - "crates/buzz-relay/src/router.rs:64-65"
  - statement: "nip11_or_ws_handler's content-negotiation logic: an exact admin-host match is short-circuited first and never receives the NIP-11 document or a WebSocket upgrade; otherwise a request whose Accept header contains `application/nostr+json` gets the document immediately; otherwise the handler attempts a WebSocket upgrade, and on upgrade failure falls back to serving the SPA (if git-web-gui is enabled and the client accepts text/html) or, failing that, the NIP-11 document again."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:304-389"
  - statement: "The handler's own comment states that NIP-11 is served before the request is bound to a community and stays fail-open: an unmapped host still receives the document, with host-scoped fields (like the workspace icon) simply absent, so the document itself cannot be used to enumerate which hosts are mapped to a community on this deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:336-342"
  - statement: "This fail-open, host-scoped-fields-only behavior is independently corroborated by docs/multi-tenant-conformance.md's own conformance table row for this exact surface ('NIP-11 relay info and relay self'), which states the same contract: host-derived community for community-specific facts, workspace icon pre-fetched as a scalar via bind_community with fail-open to absent on an unmapped host, and no other DB lookup from unauthenticated global state."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md:43"
  - statement: "RelayInfo (the served JSON shape) carries: name, description, an optional per-community icon (NIP-11 icon, sourced from the community's kind:9033-set workspace icon), operator pubkey and contact (both currently always None), supported_nips, an optional supported_extensions list, an optional push descriptor (NIP-PL), software (a fixed GitHub URL), version (the crate's own Cargo package version), an optional limitation block, an optional pairing_relay_url, an optional admin_api origin, an optional GifDescriptor, and an optional relay_self (serialized as the NIP-11 `self` field, NIP-43) pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:24-70"
  - statement: "RelayLimitation carries max_message_length, max_subscriptions (1024), max_filters (10), max_limit, max_subid_length (256), min_pow_difficulty (always None), auth_required (always true), payment_required (always false), restricted_writes (always true), and two NIP-ER fields (due_delivery_mode, max_not_before_delta)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:83-143"
  - statement: "auth_required is hardcoded true in relay_limitation because the REQ, EVENT and COUNT handlers unconditionally reject any connection not in AuthState::Authenticated -- a claim the function's own doc comment makes and that the unit test auth_required_is_advertised_true exercises directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:120-123"
      - "crates/buzz-relay/src/nip11.rs:548-554"
  - statement: "max_limit is set from buzz_db::DEFAULT_MAX_PAGE_LIMIT (1_000), the same constant the REQ handler's filter-limit clamp uses, and the relay's own test req_filter_limit_clamps_to_advertised_nip11_max_limit exists specifically to keep the advertised ceiling and the enforced one from drifting apart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:134"
      - "crates/buzz-db/src/store/event.rs:33"
      - "crates/buzz-relay/src/handlers/req.rs:1576-1591"
  - statement: "SUPPORTED_NIPS is a module-level constant, [1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56], advertised unconditionally; NIP-43 (relay membership, constant NIP_RELAY_MEMBERSHIP) is appended to the list only when RelayInfo::build is called with advertise_nip43=true, which nip11_facts computes as true only when the relay has a stable signing key (BUZZ_RELAY_PRIVATE_KEY configured) AND membership enforcement is enabled (BUZZ_REQUIRE_RELAY_MEMBERSHIP=true)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:8-21"
      - "crates/buzz-relay/src/nip11.rs:352-356"
  - statement: "relay_self (the NIP-11 `self` field) is set whenever the relay has a stable signing key, independent of membership enforcement, because NIP-29 group-metadata events (kinds 39000/39001/39002, always signed with the relay keypair) need a verifiable self key even on relays that do not enforce NIP-43 membership; RelayInfo::build's own debug_assert additionally makes it a programmer error (a debug-build panic) to advertise NIP-43 without relay_self set, and unit test build_nip43_without_self_panics_in_debug exercises exactly that assertion."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:148-163"
      - "crates/buzz-relay/src/nip11.rs:181-185"
      - "crates/buzz-relay/src/nip11.rs:632-639"
  - statement: "SUPPORTED_NIPS does not list 45, yet NIP-45 (COUNT) is genuinely implemented in this relay: a dedicated handler module (crates/buzz-relay/src/handlers/count.rs, whose own module doc comment names 'NIP-45 COUNT handler'), a COUNT protocol message with request parsing and response formatting (protocol.rs), the POST /count HTTP bridge endpoint, and count-query support in buzz-db (store/event.rs). This is the same advertised-vs-implemented gap sibling issue #1268's count-handler node independently found; it is verified here directly against the current SUPPORTED_NIPS constant and the count handler's own source, not merely repeated from that sibling node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
      - "crates/buzz-relay/src/handlers/count.rs:1"
      - "crates/buzz-relay/src/protocol.rs:28"
      - "crates/buzz-relay/src/protocol.rs:213"
      - "crates/buzz-db/src/store/event.rs:658"
      - "crates/buzz-db/src/store/event.rs:1459"
  - statement: "Every other NIP number in SUPPORTED_NIPS (1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56) and the conditional 43 has an independent implementation footprint elsewhere in the repository -- checked directly by grepping each NIP number (including the zero-padded NIP-01/NIP-02 forms used for single-digit NIPs) across crates/ and finding real, non-nip11.rs source referencing it -- so the NIP-45 omission recorded above is an isolated gap in this list, not evidence of a broader pattern of unverified advertisement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:38"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "The NIP-45 omission most likely reflects the COUNT handler and the SUPPORTED_NIPS constant being maintained independently, with no automated or reviewer-held check tying an implemented protocol feature to this constant's contents -- the same category of drift the relay's own max_limit cross-reference test (see above) was written specifically to prevent for a different field, suggesting the pattern is known but was not yet applied to the supported_nips list itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs:15"
      - "crates/buzz-relay/src/nip11.rs:113-118"
    confidence: 0.55
  - statement: "supported_extensions always includes nip-er (NIP-ER, due reminders); buzz-gif is appended only when a GIF provider is configured (config.klipy is Some), and nip-pl is appended only when push delivery is both configured and successfully resolves a tenant host for the request -- each addition is exercised by its own unit test (gif_descriptor_and_extension_are_config_gated_and_credential_free; push_descriptor_is_gated_by_gateway_configuration_and_tenant_binding)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:192-219"
      - "crates/buzz-relay/src/nip11.rs:276-317"
      - "crates/buzz-relay/src/nip11.rs:406-420"
      - "crates/buzz-relay/src/nip11.rs:482-510"
  - statement: "RelayInfo::build itself takes only static and pre-derived scalar inputs (no &Db, &AppState, search, or audit handle); the file enforces this at compile time with a const function-pointer type binding (_RELAY_INFO_BUILD_STATIC_INPUT_FENCE) whose own comment states the conformance obligation this protects: an unauthenticated NIP-11 read must never become an enumeration oracle for other communities, and any future signature change that adds an unscoped input breaks the build rather than failing silently."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:371-400"
  - statement: "The one host-scoped fact RelayInfo::build does receive -- the workspace icon -- is fetched by workspace_icon_for_host through crate::tenant::bind_community, the same scoped-lookup function the relay's row-zero tenancy binding uses elsewhere, and its own doc comment states the lookup fails open to None (omitting the icon field) rather than erroring, specifically because NIP-11 must still be served to unmapped hosts."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:319-338"
  - statement: "The admin_api field is present only when the deployment's admin surface is configured (config.admin.is_some()), derived purely from the configured admin host via admin_api_origin (loopback host -> http scheme, else https), and is omitted entirely -- not serialized as null -- when the admin surface is unconfigured; three unit tests exercise the absent, loopback and non-loopback cases."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:359-369"
      - "crates/buzz-relay/src/nip11.rs:649-694"
  - statement: "Both ARCHITECTURE.md's own HTTP route table and its E2E test-coverage table corroborate the two-route shape and test placement described above: GET / as 'WebSocket upgrade or NIP-11 relay info', GET /info as 'NIP-11 relay info', and crates/buzz-test-client/tests/e2e_relay.rs listed as covering NIP-11 among the WebSocket protocol E2E suite's 27 tests."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:614"
      - "ARCHITECTURE.md:615"
      - "ARCHITECTURE.md:702"
  - statement: "test_nip11_relay_info in crates/buzz-test-client/tests/e2e_relay.rs is an ignore-gated (requires a running relay) end-to-end test that performs a real HTTP GET /info and asserts the presence of name, description, supported_nips and version fields, plus limitation.max_subscriptions == 1024 and limitation.auth_required, giving this endpoint live E2E coverage in addition to nip11.rs's own 15 unit tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs:955-1000"
---

# Platform surface: relay NIP-11 (relay information document)

The Buzz relay's implementation of NIP-11, the Nostr protocol's relay
information document: a small, unauthenticated JSON document describing the
relay's identity, protocol support, and operational limits, served over plain
HTTP alongside the same address the relay serves the WebSocket protocol on.
This node answers what the document contains, how a request reaches it, what
each field is derived from, and whether the relay's own advertisement of NIP
support (`supported_nips`) matches what is actually implemented.

**No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`
at the recorded revision** (verified: `templates/` holds `architecture-*`,
`component.md`, `capability.md`, `interface.md`, `event-kind.md`, and others,
but none named for the `platforms` corpus surface). Per `AGENTS.md`'s
documented path for this situation and this batch's own settled convention
(sibling `platforms/**` tasks in this Feature), this node is hand-authored
directly against `node.schema.json`, borrowing `templates/component.md`'s
section shape (Responsibility / Public interface / Dependencies / Boundary /
Relationships / Scope and omissions) since the NIP-11 handler is,
structurally, one small component of the relay container.

## Responsibility

Serve one JSON document, `RelayInfo`, describing this relay to any
unauthenticated HTTP client: its name and description, an optional
per-community icon, the Nostr NIPs it supports, protocol/resource limits it
enforces, and a handful of optional feature descriptors (push delivery,
pairing relay, admin API origin, GIF search). It is the standard mechanism by
which a Nostr client discovers what a relay supports and enforces before
connecting.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `GET /` | HTTP route | Content-negotiated: serves the NIP-11 document when `Accept: application/nostr+json`; otherwise attempts a WebSocket upgrade, falling back to the SPA or the NIP-11 document again on upgrade failure. An exact admin-host match is short-circuited before either branch. | `crates/buzz-relay/src/router.rs:64`, `:304-389` |
| `GET /info` | HTTP route | Unconditionally serves the NIP-11 document, regardless of `Accept`. | `crates/buzz-relay/src/router.rs:65` |
| `RelayInfo` | struct | The served JSON shape: `name`, `description`, `icon?`, `pubkey`, `contact`, `supported_nips`, `supported_extensions?`, `push?`, `software`, `version`, `limitation?`, `pairing_relay_url?`, `admin_api?`, `gif?`, `self?` (serialized field name `self`). | `crates/buzz-relay/src/nip11.rs:24-70` |
| `RelayLimitation` | struct | `max_message_length`, `max_subscriptions` (1024), `max_filters` (10), `max_limit` (`buzz_db::DEFAULT_MAX_PAGE_LIMIT`), `max_subid_length` (256), `min_pow_difficulty` (always `None`), `auth_required` (always `true`), `payment_required` (always `false`), `restricted_writes` (always `true`), `due_delivery_mode?`, `max_not_before_delta?` (NIP-ER). | `crates/buzz-relay/src/nip11.rs:83-143` |
| `RelayInfo::build` | fn | Pure, static-input constructor for `RelayInfo`; compile-time fenced (see *Boundary*) to take only static/scalar arguments -- no DB, search, or audit handle. | `crates/buzz-relay/src/nip11.rs:173-219`, fence at `:371-400` |
| `relay_info_handler` | fn (Axum handler) | Reads the request's `Host` header and returns `nip11_document(&state, host)` as JSON. Bound to `GET /info`. | `crates/buzz-relay/src/nip11.rs:222-232` |
| `nip11_document` | fn | Assembles the per-request document: resolves `relay_self`/`advertise_nip43` from config (`nip11_facts`), fetches the host-scoped workspace icon, derives the admin API origin, calls `RelayInfo::build`, then conditionally attaches a push descriptor. Shared by both routes so they cannot drift apart. | `crates/buzz-relay/src/nip11.rs:276-317` |
| `SUPPORTED_NIPS` | const | `[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]` -- unconditionally advertised. See *SUPPORTED_NIPS accuracy* below for a discrepancy found while writing this node. | `crates/buzz-relay/src/nip11.rs:15` |
| `NIP_RELAY_MEMBERSHIP` (43) | const | Appended to `supported_nips` only when `advertise_nip43=true` is passed to `build`. | `crates/buzz-relay/src/nip11.rs:17-21` |

## Content negotiation and tenancy behavior

- **`GET /`** first checks for an exact admin-host match and, if matched,
  never serves NIP-11 or a WebSocket upgrade -- it serves the admin SPA
  instead. Otherwise, an `Accept: application/nostr+json` request gets the
  NIP-11 document immediately. Otherwise the handler attempts a WebSocket
  upgrade; on upgrade failure it falls back to the SPA (if git-web-gui is
  enabled and the client accepts `text/html`) or, as the last resort, the
  NIP-11 document again.
- **Fail-open by design.** NIP-11 is served *before* the request is bound to
  a community, and deliberately so: an unmapped host still receives the
  document, with host-scoped fields (the workspace `icon`) simply absent, so
  the document itself cannot be used to probe which hosts have a community
  configured on a given deployment. This is independently corroborated by
  `docs/multi-tenant-conformance.md`'s own conformance table row for this
  exact surface, which states the same host-derived-icon,
  fail-open-to-absent contract.
- **Static-input fence.** `RelayInfo::build` is bound, at compile time, to an
  exact function-pointer type with no `&Db`/`&AppState`/search/audit
  parameter (`_RELAY_INFO_BUILD_STATIC_INPUT_FENCE`). Any future change that
  adds an unscoped input breaks the build instead of silently becoming a
  cross-tenant enumeration surface. The one host-scoped input the document
  does carry -- the workspace icon -- is fetched through
  `crate::tenant::bind_community`, the same scoped lookup the relay's row-zero
  tenancy binding uses, and fails open to an absent field rather than an
  error.

## SUPPORTED_NIPS accuracy

Checked directly against source, not assumed: **`SUPPORTED_NIPS` omits 45.**
NIP-45 (COUNT) is genuinely implemented in this relay --
`crates/buzz-relay/src/handlers/count.rs` (module doc: "NIP-45 COUNT
handler"), a `COUNT` protocol message (`protocol.rs:28,213`), the `POST
/count` HTTP bridge route, and count-query support in `buzz-db`
(`store/event.rs:658,1459`) -- yet it never appears in the constant a client
reads to discover relay capabilities. This is the same gap sibling issue
`#1268`'s count-handler node independently found; it is re-verified here
against the current `nip11.rs` and `count.rs` source rather than taken on the
sibling's word.

Every other advertised NIP was checked for an independent implementation
footprint elsewhere in the repository (grepping both `NIP-N` and the
zero-padded `NIP-0N` form used for single-digit NIPs) and each has one, so
this is recorded as an isolated omission, not a broader pattern -- see
*Scope and omissions* for what was not exhaustively re-checked.

**Why this likely happened (reasoned, not confirmed):** the relay already
has one precedent for exactly this kind of drift -- `max_limit`'s
cross-reference test (`req_filter_limit_clamps_to_advertised_nip11_max_limit`)
exists specifically to keep an advertised NIP-11 field and an enforcement
path from silently diverging. No equivalent check ties `SUPPORTED_NIPS` to
the set of protocol features the relay actually implements, so the same
category of drift this repository already guards against for one field
appears to have reached this list unguarded.

## Dependencies

**Depends on** (this endpoint requires these to build/run its response):

| Component | Why | Evidence |
|---|---|---|
| `buzz-db` | `DEFAULT_MAX_PAGE_LIMIT` sets `RelayLimitation::max_limit`, kept in sync with the REQ handler's own clamp by a dedicated cross-reference test. | `crates/buzz-db/src/store/event.rs:33`; `crates/buzz-relay/src/handlers/req.rs:1576-1591` |
| Relay config (`crate::config`) | `max_frame_bytes`, `pairing_relay_url`, `klipy` (GIF provider), `admin`, `push_enabled`, `relay_private_key`, `require_relay_membership` all feed `nip11_document`/`nip11_facts`/`admin_api_advertisement`. | `crates/buzz-relay/src/nip11.rs:283-317`, `:352-356`, `:367-369` |
| `crate::tenant::bind_community` | Scoped lookup used by `workspace_icon_for_host` (and, for the push descriptor, to resolve the tenant host) -- the same function the relay's row-zero tenancy binding uses. | `crates/buzz-relay/src/nip11.rs:296-303`, `:328-338` |
| Relay signing keypair (`state.relay_keypair`) | Source of the `self` field and of the push descriptor's `pubkey`. | `crates/buzz-relay/src/nip11.rs:284`, `:308` |

**Depended on by** (what relies on this endpoint's contract):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/router.rs` | Both `GET /` and `GET /info` route to handlers this node documents. | `crates/buzz-relay/src/router.rs:26,64-65` |
| `crates/buzz-relay/src/handlers/req.rs` | Enforces the same `max_limit` ceiling this document advertises; its own test exists to keep the two from drifting apart. | `crates/buzz-relay/src/handlers/req.rs:1576-1591` |
| Nostr clients generally (external) | NIP-11 is the standard relay-discovery document; any conformant client may fetch it before connecting. Not independently re-verified here -- this is the protocol's own purpose, not a repository-internal dependency edge. | n/a (protocol-level, not a citable in-repo dependency) |

## Boundary

This node does not describe:
- The relay container's full inbound/outbound surface, deployment shape, or
  graceful-shutdown behavior -- see `architecture-containers-relay`
  (referenced below), which already covers those and explicitly leaves
  per-endpoint depth to a future node such as this one.
- NIP-43 (relay membership) as a protocol/feature in its own right -- only
  the conditions under which this endpoint advertises it.
- The full Nostr NIP catalog or an exhaustive audit of every NIP the relay
  implements against every NIP it advertises anywhere in the system -- only
  the one discrepancy (NIP-45) found while directly checking this
  endpoint's own `SUPPORTED_NIPS` constant.
- Install/usage instructions for a human running the relay -- the relay
  crate carries no `README.md` (verified: `crates/buzz-relay/` has none) so
  there is nothing to point to instead; operational instructions belong in
  `launchpad/`, per this repository's `CLAUDE.md`.

## Relationships

- references: architecture-containers-relay

## Scope and omissions

**This node covers** the NIP-11 relay information document as served by this
relay: its two HTTP routes, the `RelayInfo`/`RelayLimitation` shapes, the
content-negotiation and fail-open tenancy behavior, the static-input
compile-time fence, and a directly re-verified check of whether
`supported_nips` matches what is actually implemented (it does not, for
NIP-45).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The relay container's full responsibility, technology, inbound/outbound surface, deployment and shutdown behavior | `architecture-containers-relay` |
| NIP-45 (COUNT) as its own protocol feature/handler | sibling issue #1268's count-handler node |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| A `platforms`-specific template's required sections, once one is authored | Not yet filed as an issue at the recorded revision; this node used `component.md`'s shape as the nearest fit, per `AGENTS.md`'s no-template path |

**Expected but not verified when this node was written:**

- **Whether any NIP besides 45 is implemented but unadvertised, or advertised
  but not actually implemented, was not exhaustively checked.** Only the one
  gap found by directly grepping each of the fourteen currently-advertised
  NIP numbers (plus the conditional NIP-43) was recorded; a full audit of
  every NIP this relay implements anywhere in the codebase against this one
  constant was out of this node's scope.
- **Whether other relays or NIP-11-serving deployments in this repository
  (e.g. `buzz-pair-relay`) share this same `SUPPORTED_NIPS`-drift risk was
  not checked** -- this node scopes strictly to `buzz-relay`'s own
  `crates/buzz-relay/src/nip11.rs`.
- **Whether a `platforms`-level template will require reshaping this node's
  section structure once one is authored** -- flagged, not resolved, per
  `AGENTS.md`'s documented no-template path.
