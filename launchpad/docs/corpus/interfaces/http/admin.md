---
id: interfaces-http-admin
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052 on origin/launchpad."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "The deployment-admin HTTP surface is nested at the fixed path prefix /api/admin/v1, and the whole sub-router is mounted into the relay's app router only when config.admin.is_some() (i.e. BUZZ_ADMIN_HOST is configured) -- when unset, every route under this prefix 404s at the routing layer, before any handler runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:53-61"
  - statement: "The router() function registers exactly thirteen routes under that prefix: GET /probe, GET /reports, GET /reports/{id}, POST /reports/{id}/resolve, POST /reports/{id}/reopen, POST /reports/{id}/cancel, GET /feedback, GET /feedback/{id}, PATCH /feedback/{id}, GET /feedback/{id}/attachments/{sha256}, GET /operators, PUT /operators/{pubkey}, DELETE /operators/{pubkey}."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:45-67"
  - statement: "The module's own doc comment states the surface is a private deployment-moderation API where read routes are available in both auth modes (nip98, disabled) while mutation and staffing routes require an authenticated nip98 principal attributed to a resolved operator or moderator."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:1-5"
  - statement: "Authentication mode is selected by the BUZZ_ADMIN_AUTH environment variable: unset, empty, or \"nip98\" selects AdminAuth::Nip98 (the fail-secure default); \"disabled\" selects AdminAuth::Disabled (always read-only, an explicit operator assertion that the surface is protected at the network layer); any other value is a startup error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "In nip98 mode every request must carry an Authorization: Nostr <base64 event> header containing a signed kind:27235 (NIP-98 HTTP Auth) event, verified by buzz_auth::verify_nip98_event against: Schnorr signature, created_at within +/-60 seconds of server time, a u tag matching the canonical request URL, a method tag matching the actual HTTP method, and (when a request body is present) a payload tag whose value equals SHA-256(body)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs:1-24"
      - "crates/buzz-relay/src/api/admin/auth.rs:349-406"
  - statement: "The canonical URL used for NIP-98 u-tag verification is derived from the configured admin host, not the inbound Host header, and uses http:// for loopback hosts (localhost, *.localhost, ::1, 127.x -- matching the repo's admin.localhost:3000 dev default) and https:// for every other host; the NIP-11-advertised admin_api origin uses the identical scheme rule so a client that auto-discovers the origin signs against the exact scheme the relay verifies."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:109-156"
      - "crates/buzz-relay/src/nip11.rs:359-368"
  - statement: "authorize() additionally requires the inbound Host header to exactly equal the configured admin host (is_admin_host) and, when an Origin header is present, requires it to equal the same canonical scheme+host -- both checks run after the NIP-98 credential check so an unauthenticated caller learns nothing about the expected Host/Origin from a differential response, and both produce the same generic 403 as any other authorization failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:188-237"
  - statement: "A verified NIP-98 event's pubkey resolves to an AdminPrincipal by a four-branch, config-outranks-DB order: Operator/Config if the pubkey is in RELAY_OPERATOR_PUBKEYS; Operator/OwnerFallback if the pubkey equals RELAY_OWNER_PUBKEY and RELAY_OPERATOR_PUBKEYS is empty (evaluated from config only, never demoted by a DB row); Moderator or Operator per a relay_operators DB row otherwise; and 403 with no principal if none of the three match -- there is no fall-through role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:239-312"
  - statement: "The NIP-98 event id is claimed against a Redis-backed replay guard scoped to the constant \"admin-moderation\", but only after Host/Origin validation and roster resolution succeed -- so an unrostered but validly-signing caller can never burn a legitimate caller's replay slot -- and a Redis failure during the claim is treated as a replay-guard rejection (fails closed), never as an implicit pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:408-434"
  - statement: "In disabled mode authorize() returns Ok(None) for every request (reads still pass Host/Origin checks); require_mutation_principal() turns that None into a 403 with the message \"mutations require BUZZ_ADMIN_AUTH=nip98\", so mutation and staffing routes are unreachable in disabled mode regardless of caller, while every GET-only route under this prefix still functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:24-28"
      - "crates/buzz-relay/src/api/admin/auth.rs:314-323"
  - statement: "Two of the thirteen routes carry an additional role check beyond require_mutation_principal: GET /operators, PUT /operators/{pubkey} and DELETE /operators/{pubkey} all call require_operator(), which 403s with \"staffing endpoints require operator role\" for an authenticated Moderator -- only Operator may read or write the roster."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:325-334"
      - "crates/buzz-relay/src/api/admin/mod.rs:903-919"
  - statement: "Every response from this API uses one JSON error envelope, {\"error\":{\"code\",\"message\",\"requestId\"}} (a fresh UUID per response, not correlated to any request-supplied id), and every 401 additionally carries a WWW-Authenticate: Nostr header per RFC 9110's requirement that a 401 name its auth scheme."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/error.rs"
  - statement: "GET /reports supports community_id, status, scope, reportType, targetKind, before, after and limit query filters; an explicit status is honored as-is, but with no status given the default view is escalated-only (scope=all restores full cross-status visibility for platform-safety/legal review), and limit is clamped server-side to the inclusive range 1..=200 (400 invalid_limit outside it)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:89-240"
  - statement: "POST /reports/{id}/resolve accepts one of six actions (delete, kick, ban, timeout, dismiss, escalate). dismiss and escalate are decision-only, running a compare-and-swap open-to-terminal transition plus an audit row in one transaction; the other four are server-side enforcement actions and require a client-supplied requestId (400 missing_request_id if absent), used as an idempotency key against the enforcement state machine."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:409-660"
  - statement: "resolve_report returns 409 conflict if the report is not currently open, 400 bad_request (invalid_action_for_target) if the action/target-kind/channel combination is invalid, and 422 unprocessable_entity (enforcement_failed) if server-side enforcement fails after passing validation; a timeout action's expirationSecs is rejected 400 if zero or greater than 365 days (MAX_TIMEOUT_SECS), bounding the arithmetic so it can never overflow or silently yield a past expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:430-460"
      - "crates/buzz-relay/src/api/admin/mod.rs:576-636"
  - statement: "POST /reports/{id}/reopen requires a client-generated requestId and is itself idempotent: a retry with the same requestId against an already-reopened report (ReopenResult::AlreadyReopened) returns the identical {\"status\":\"open\"} success rather than an error, while a report that is not in a terminal state returns 409 conflict (not reopenable)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:662-741"
  - statement: "POST /reports/{id}/cancel takes an actionId naming exactly the activeAction.id the client last observed and fences the cancel to that id via a compare-and-swap DB call (cancel_admin_action); a mismatch -- already cancelled, superseded by a newer claim, or past the mutation point -- returns 409 conflict rather than silently no-op'ing, and is the only recovery path for a failed enforcement action (no client-side retry composition)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:743-836"
  - statement: "PATCH /feedback/{id} accepts exactly one of the three status values new, reviewed or archived (400 invalid_status otherwise) and returns 404 if the feedback id does not exist; GET /feedback/{id}/attachments/{sha256} re-derives the owning community from the feedback row's own provenance (never from client input), verifies the sha256 is referenced by the feedback's own imeta tags, and fails closed to 404 for a severed feedback row (source community already purged) or any tenant-provenance mismatch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:838-883"
      - "crates/buzz-relay/src/api/admin/mod.rs:340-407"
  - statement: "PUT /operators/{pubkey} is an idempotent upsert of a DB-backed operator/moderator row, and both PUT and DELETE /operators/{pubkey} return 409 conflict, immutable-through-the-API, for any pubkey covered by a config-backed grant (RELAY_OPERATOR_PUBKEYS or the owner-fallback); the underlying DB layer additionally rejects (409, mapped from DbError::LastOperator) any upsert-demotion or delete that would leave the deployment with zero effective operators."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:974-1112"
  - statement: "All thirteen routes sit behind a security_headers middleware layer that unconditionally sets Cache-Control: no-store, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: no-referrer and a restrictive Content-Security-Policy (default-src 'none'; frame-ancestors 'none'), and mutation routes are additionally capped to a 4096-byte request body via RequestBodyLimitLayer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:63-87"
  - statement: "GET /probe returns {status, authMode, role, source, canAct, canStaff} so a client can discover the effective auth mode and the calling principal's own role/capabilities before rendering any admin-console UI, without that client needing to guess from error responses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:124-189"
  - statement: "This surface's own name is shared with two unrelated things elsewhere in the repository: crates/buzz-admin is a separate, offline Nostr membership-list CLI (kind:13534 snapshot publishing) with no HTTP surface at all, and crates/buzz-relay/src/api/operator.rs's own doc comment names its routes \"Deployment-operator HTTP APIs\" for community provisioning/archive/transfer -- mounted at /operator/communities/* (outside /api/admin/v1), NIP-98-signed but authorizing a different capability than this API's Operator/Moderator moderation roles."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:1-21"
      - "crates/buzz-relay/src/api/operator.rs:1-5"
  - statement: "node.schema.json's type enum has no member named interface; the enum's single combined value for interface- and event-kind-shaped nodes is interfaces-events, and this is the value corpus-template-interface itself documents nodes built from this template as carrying."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "No integration or end-to-end test exercising this API over a real HTTP client was found in crates/buzz-test-client/tests/; the only test coverage located is the unit-test modules embedded in admin/mod.rs and admin/auth.rs themselves, which exercise individual handlers and helper functions in-process rather than the full authenticated request/response cycle."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:1257"
      - "grep_repo(pattern='admin/v1|api/admin', path='crates/buzz-test-client/tests') -> zero matches at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
    confidence: 0.8
relationships:
  - type: part-of
    target: architecture-containers-relay
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Deployment-admin HTTP API: interface

This node documents the relay's **private deployment-admin API** -- a NIP-98-authenticated
JSON/HTTP boundary between a human operator or moderator (typically via an admin console
client) and the relay's moderation and staffing state, mounted at `/api/admin/v1` and only
present at all when the deployment configures `BUZZ_ADMIN_HOST`. It is one of the relay's
deliberately narrow set of non-Nostr HTTP surfaces (root `AGENTS.md` §Key Patterns), distinct
from the Nostr event data plane and from the community-provisioning "operator" surface
described in *Boundary* below.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `GET /api/admin/v1/probe` | `crates/buzz-relay/src/api/admin/mod.rs#probe` | Discover auth mode, resolved role/source, and available capabilities before rendering a console UI. |
| `GET /api/admin/v1/reports` | `crates/buzz-relay/src/api/admin/mod.rs#reports` | List moderation reports, filtered by community/status/scope/type/target/date; escalated-only by default. |
| `GET /api/admin/v1/reports/{id}` | `crates/buzz-relay/src/api/admin/mod.rs#report_detail` | One report's full detail plus any active enforcement action. |
| `POST /api/admin/v1/reports/{id}/resolve` | `crates/buzz-relay/src/api/admin/mod.rs#resolve_report` | Decide (dismiss/escalate) or enforce (delete/kick/ban/timeout) against an open report. |
| `POST /api/admin/v1/reports/{id}/reopen` | `crates/buzz-relay/src/api/admin/mod.rs#reopen_report` | Return a terminal report to `open`; idempotent via client `requestId`. |
| `POST /api/admin/v1/reports/{id}/cancel` | `crates/buzz-relay/src/api/admin/mod.rs#cancel_report` | Cancel a failed enforcement action, fenced to the observed `actionId`. |
| `GET /api/admin/v1/feedback` | `crates/buzz-relay/src/api/admin/mod.rs#feedback` | List product-feedback submissions. |
| `GET /api/admin/v1/feedback/{id}` | `crates/buzz-relay/src/api/admin/mod.rs#feedback_detail` | One feedback submission's full detail. |
| `PATCH /api/admin/v1/feedback/{id}` | `crates/buzz-relay/src/api/admin/mod.rs#update_feedback_status` | Update feedback lifecycle status (`new`/`reviewed`/`archived`). |
| `GET /api/admin/v1/feedback/{id}/attachments/{sha256}` | `crates/buzz-relay/src/api/admin/mod.rs#feedback_attachment` | Serve one feedback attachment blob, tenant- and hash-verified from server-owned provenance. |
| `GET /api/admin/v1/operators` | `crates/buzz-relay/src/api/admin/mod.rs#list_operators` | List the effective operator/moderator roster (config ∪ DB, source-annotated). Operator role only. |
| `PUT /api/admin/v1/operators/{pubkey}` | `crates/buzz-relay/src/api/admin/mod.rs#upsert_operator` | Idempotent upsert of a DB-backed operator/moderator row. Operator role only. |
| `DELETE /api/admin/v1/operators/{pubkey}` | `crates/buzz-relay/src/api/admin/mod.rs#delete_operator` | Remove a DB-backed operator/moderator row. Operator role only. |

## Contract and stability

**Versioning.** The path itself carries the version segment (`/api/admin/v1`); no
separate version negotiation or deprecation-header mechanism was found for this
surface, and no `v2` exists yet.

**Authentication.** `BUZZ_ADMIN_AUTH` selects `nip98` (default, fail-secure) or
`disabled`. In `nip98` mode every request needs a valid `Authorization: Nostr
<base64 kind:27235 event>` header (NIP-98 HTTP Auth): Schnorr-signed, timestamped
within ±60s, `u`-tag matching the canonical admin URL, `method`-tag matching the
actual verb, and (body-bearing requests) a `payload` SHA-256 tag matching the
buffered body. `Host` must exactly equal the configured admin authority and
`Origin`, when present, must equal the same canonical scheme+host — both checked
only after the credential check, so an unauthenticated caller cannot fingerprint
the expected values from a differential error. A verified event's replay id is
claimed against a Redis-backed guard scoped `"admin-moderation"`, claimed only
after Host/Origin and roster checks pass; a Redis failure during that claim is
treated as a rejection, never an implicit pass.

**Authorization.** In `nip98` mode the authenticated pubkey resolves to
`Operator`/`Config` (in `RELAY_OPERATOR_PUBKEYS`), `Operator`/`OwnerFallback`
(equals `RELAY_OWNER_PUBKEY` *and* `RELAY_OPERATOR_PUBKEYS` is empty — evaluated
from config only, never demoted by a DB row), `Moderator`/`Db` or `Operator`/`Db`
(a `relay_operators` row), or no principal at all (403) — config always outranks
the DB. Reads work in both auth modes; mutation routes require a resolved
principal (403 `"mutations require BUZZ_ADMIN_AUTH=nip98"` in `disabled` mode);
the three `/operators` routes additionally require the `Operator` role specifically
(403 for an authenticated `Moderator`).

**Error semantics.** One envelope everywhere: `{"error":{"code","message",
"requestId"}}` (a fresh UUID per response). Every `401` carries `WWW-Authenticate:
Nostr`. `403` covers Host/Origin mismatch, an unrostered signer, and a Moderator
hitting an Operator-only route. `404` covers an unknown report/feedback/operator
id and a mismatched or non-hex pubkey path segment. `409` covers a report that is
not `open`/not-terminal/not-cancellable, a config-backed pubkey targeted by
`PUT`/`DELETE /operators/{pubkey}`, and a roster change that would leave zero
effective operators. `422` covers a validated enforcement action that failed at
the enforcement step. `400` covers malformed JSON, an unknown `action`/`status`/
`role`, an out-of-range `limit`, and an out-of-range `expirationSecs`.

**Ordering and idempotency.** `POST .../reopen` takes a client `requestId`;
replaying the same id against an already-reopened report returns the identical
success rather than erroring. Enforcement actions on `POST .../resolve` require a
`requestId` used as the enforcement state machine's own idempotency key.
`POST .../cancel` is not idempotent by a client-supplied key — it is
compare-and-swap fenced to the `actionId` the client last observed, so a stale or
repeated cancel against a since-changed action returns `409` rather than silently
no-op'ing.

**Transport-level constraints.** Mutation routes cap the request body at 4096
bytes. All routes carry `Cache-Control: no-store`, `X-Content-Type-Options:
nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a
`default-src 'none'; frame-ancestors 'none'` CSP.

## Boundary

This node does not describe:

- **NIP-98 (kind:27235) itself.** The wire format, signature scheme, and tag
  semantics are the NIP's own contract, implemented once in `buzz-auth`
  (`crates/buzz-auth/src/nip98.rs`) and reused unmodified here — this node cites
  that verification, it does not re-derive it.
- **The admin console's static-asset hosting.** The same admin `Host` also serves
  a separate SPA bundle (`is_admin_host`/`ADMIN_CSP` in `crates/buzz-relay/src/router.rs`)
  with its own content-security-policy and fallback routing. That is static-file
  serving for a browser client, not this JSON API, and is out of scope here.
- **`crates/buzz-admin` (the CLI).** An unrelated, offline Nostr membership-list
  tool (`kind:13534` snapshot publishing) with no HTTP surface — sharing this
  API's "admin" name only by coincidence.
- **`crates/buzz-relay/src/api/operator.rs`'s deployment-operator routes.**
  Community provisioning/archive/transfer, mounted at `/operator/communities/*`
  outside `/api/admin/v1` — NIP-98-signed like this API, but authorizing a
  different capability (who may create/archive/transfer *communities*) than this
  API's Operator/Moderator *moderation* roles. A reader looking for "the operator
  API" may mean either; this node is the moderation one.
- **Field-by-field, parameter-by-parameter DTO cataloguing** for every request and
  response body, at the depth `#1346`/`#1532` (reference / API Reference gap)
  would provide — this node points at the handler and DTO source instead of
  restating every field.

## Relationships

- part-of: architecture-containers-relay
- references: architecture-principles-fail-closed-boundaries

## Scope and omissions

**This node covers** the private deployment-admin HTTP API mounted at
`/api/admin/v1`: its thirteen routes, its NIP-98 authentication and
config-then-DB role resolution, its uniform error envelope and status-code
semantics, its idempotency devices (`requestId` on reopen/enforcement,
`actionId` fencing on cancel), and an explicit boundary against the two other
"admin"/"operator"-named surfaces in this repository that a reader could
otherwise conflate it with.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-98 (kind:27235) wire format | `crates/buzz-auth/src/nip98.rs`, the NIP itself |
| Admin console SPA static hosting / CSP | `crates/buzz-relay/src/router.rs` (not this node) |
| `buzz-admin` CLI (membership snapshots) | `crates/buzz-admin` — unrelated tool |
| Deployment-operator community provisioning | `crates/buzz-relay/src/api/operator.rs` — separate corpus task, if one does not already exist |
| Field-by-field API-parameter cataloguing | `#1346`/`#1532` (reference / API Reference gap, undecided) |

**Expected but not verified when this node was written:**
- **No integration or end-to-end test exercising this API over a real HTTP client
  was found.** `crates/buzz-test-client/tests/` has no reference to `api/admin` or
  `admin/v1`; coverage located is limited to the unit-test modules inside
  `admin/mod.rs` and `admin/auth.rs` themselves, which exercise handlers and
  helpers in-process rather than a full authenticated request/response cycle
  against a running relay.
- **The `relay_operators` table's own schema/migration was not opened.** Its shape
  is known here only through the Rust call surface (`state.db.get_relay_operator`,
  `list_relay_operators`, `upsert_relay_operator`, `remove_relay_operator`), not
  through the SQL migration that defines the table.
- **Whether a real admin-console client of this API exists in this repository**
  (e.g. under `desktop/` or a standalone tool) was not verified; only the NIP-11
  `admin_api` advertisement that such a client could use for auto-discovery was
  confirmed.

## Examples

**Valid request — listing open moderation reports:**

```
GET /api/admin/v1/reports?status=open&limit=25 HTTP/1.1
Host: admin.example.com
Authorization: Nostr <base64 kind:27235 event, u=https://admin.example.com/api/admin/v1/reports?status=open&limit=25, method=GET>
```

A caller resolved to `Operator` or `Moderator` receives `200` with a JSON array of
`AdminReport` objects (`crates/buzz-relay/src/api/admin/mod.rs:191-240`).

**Failure — a Moderator attempting a staffing write:**

```
PUT /api/admin/v1/operators/<64-hex-pubkey> HTTP/1.1
Host: admin.example.com
Authorization: Nostr <base64 kind:27235 event, u=..., method=PUT, payload=<sha256(body)>>

{"role":"moderator"}
```

A principal resolved to `Moderator` (not `Operator`) receives `403` with
`{"error":{"code":"forbidden","message":"staffing endpoints require operator
role","requestId":"..."}}` (`crates/buzz-relay/src/api/admin/auth.rs:325-334`),
never a `200` that silently downgrades the write.
