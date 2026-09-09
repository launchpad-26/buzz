---
id: platforms-relay-admin-api
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The deployment-admin router registers /probe, /reports, /reports/{id}, /reports/{id}/resolve, /reports/{id}/reopen, /reports/{id}/cancel, /feedback, /feedback/{id} (GET and PATCH), /feedback/{id}/attachments/{sha256}, /operators (GET), and /operators/{pubkey} (PUT and DELETE), layered with a security-headers middleware and a 4096-byte request body limit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:45-67"
  - statement: "Every admin route handler calls auth::authorize() before touching the database; read routes accept a resolved principal that may be absent (disabled mode), while resolve_report, reopen_report, cancel_report, update_feedback_status, list_operators, upsert_operator, and delete_operator additionally call require_mutation_principal() to reject a None principal with 403, and list_operators/upsert_operator/delete_operator further call require_operator() to reject a non-Operator role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:145-190"
      - "crates/buzz-relay/src/api/admin/mod.rs:468-491"
      - "crates/buzz-relay/src/api/admin/mod.rs:903-919"
      - "crates/buzz-relay/src/api/admin/mod.rs:986-1004"
      - "crates/buzz-relay/src/api/admin/mod.rs:1058-1075"
  - statement: "authorize() resolves a NIP-98-signed request to an AdminPrincipal via resolve_admin_principal(), which checks (1) pubkey membership in RELAY_OPERATOR_PUBKEYS (Operator/Config), (2) pubkey equality with RELAY_OWNER_PUBKEY only when RELAY_OPERATOR_PUBKEYS is empty (Operator/OwnerFallback), (3) a role column read from the relay_operators DB table, and returns a 403 with no fall-through role if none match; config-backed grants are never demoted by a DB row for the same pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:239-312"
  - statement: "authorize() checks the Host header against the configured admin host and the Origin header against the exact expected scheme+host before granting access, and claims the NIP-98 replay-guard slot only after both checks and roster resolution succeed, so an unrostered but validly-signing caller can never consume a replay slot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:188-237"
  - statement: "require_mutation_principal() maps an absent principal (disabled-auth mode) to a 403 with the message \"mutations require BUZZ_ADMIN_AUTH=nip98\", and require_operator() maps a non-Operator role to a 403 with the message \"staffing endpoints require operator role\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs:314-334"
  - statement: "ApiError renders a JSON error envelope with a code, a message, and a fresh request_id, and attaches a WWW-Authenticate: Nostr header to every 401 response since the admin API authenticates only via NIP-98."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/error.rs:1-118"
  - statement: "resolve_report handles the dismiss/escalate actions as a decision-only transaction via report_resolution::resolve_report_decision_only, and the delete/kick/ban/timeout actions via report_resolution::resolve_report_with_enforcement, deriving the terminal HTTP status from http_validate_and_derive_status and returning {status, activeAction} in both branches; both operator and moderator roles may call it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:462-660"
  - statement: "reopen_report returns a terminal report (resolved/dismissed/escalated) to open via Db::reopen_report, is idempotent on a client-supplied request_id (a retry with the same key returns the same success rather than re-reopening), and returns 409 when the report is not currently reopenable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:662-741"
  - statement: "cancel_report is the only recovery path for a failed enforcement action: it fences the cancel to the action_id the client observed via Db::cancel_admin_action and returns 409 (\"action is not cancellable\") on any mismatch, treating that as a signal to refresh rather than retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:743-836"
  - statement: "upsert_operator and delete_operator canonicalize the path pubkey to lowercase before checking is_config_backed_pubkey(), reject a config-backed target with 409 (\"immutable through the API\"), and both DB calls map buzz_db::DbError::LastOperator to a 409 so the last effective operator can never be removed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:975-1120"
  - statement: "list_operators unions three sources into one effective-principal list -- config RELAY_OPERATOR_PUBKEYS entries, the owner-fallback pubkey when RELAY_OPERATOR_PUBKEYS is empty, and relay_operators DB rows -- annotating a pubkey with multiple sources rather than duplicating it when more than one grant applies to the same key."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:899-972"
  - statement: "buzz-relay's router only nests the admin route tree under /api/admin/v1 when state.config.admin.is_some(); when an admin surface is configured it also serves an externally-supplied SPA bundle (BUZZ_ADMIN_WEB_DIR) from the same admin-host fallback, checked before the public web bundle so the admin surface can never fall through to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:53-60"
      - "crates/buzz-relay/src/router.rs:149-176"
  - statement: "The admin surface is configured from BUZZ_ADMIN_HOST (an exact authority, validated and lowercased), BUZZ_ADMIN_AUTH (nip98 default when unset/empty, or disabled with a startup warning; any other value is a startup error), BUZZ_ADMIN_WEB_DIR (optional SPA bundle directory), RELAY_OPERATOR_PUBKEYS, and RELAY_OWNER_PUBKEY; a set BUZZ_ADMIN_TOKEN is ignored with a startup warning because token authentication was removed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:1040-1160"
  - statement: "AdminConfig and AdminAuth are defined with doc comments describing the same Config > OwnerFallback > DB precedence and the disabled-mode read-only guarantee that auth.rs implements."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:27-73"
  - statement: "The relay's NIP-11 document carries an admin_api field, populated only when the admin surface is configured, derived purely from the configured admin host via crate::api::admin::admin_api_origin so desktop can auto-discover the admin console instead of requiring manual URL entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:55-62"
      - "crates/buzz-relay/src/nip11.rs:359-368"
  - statement: "The admin API's response types (AdminReport, AdminReportDetail, AdminFeedback, AdminActionDto) and the Db methods the handlers call (admin_list_reports, admin_get_report, admin_list_feedback, admin_get_feedback, reopen_report, cancel_admin_action, get_admin_action, upsert_relay_operator, remove_relay_operator, get_relay_operator, list_relay_operators) live in buzz-db, not in buzz-relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/admin_moderation.rs:24-160"
      - "crates/buzz-db/src/store/admin_moderation.rs:409-455"
      - "crates/buzz-db/src/store/relay_operators.rs:285-330"
  - statement: "The relay_operators table (pubkey, role, added_by, created_at) is the deployment-global roster the DB-lookup branch of resolve_admin_principal reads and upsert_operator/delete_operator write; migration 0039 adds an append-only relay_operator_audit table recording every PUT/DELETE roster mutation, written only inside the transactions in crates/buzz-db/src/store/relay_operators.rs, because the roster table alone only holds final state."
    entry_class: FACT
    evidence:
      - "migrations/0035_relay_operators.sql"
      - "migrations/0039_relay_operator_audit.sql"
  - statement: "The admin module's own #[cfg(test)] suite in mod.rs (roughly lines 1257-7651) covers host/origin gating before database access, NIP-98 replay/method/payload-substitution rejection, disabled-mode read-only behavior, Operator-vs-Moderator role gating on staffing routes, config-backed-pubkey immutability (including an uppercase-bypass regression), racing-moderator and idempotent-retry behavior on resolve_report, and the default escalated-only report visibility with a scope=all override."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs:1373-1470"
      - "crates/buzz-relay/src/api/admin/mod.rs:1922-2088"
      - "crates/buzz-relay/src/api/admin/mod.rs:2658-2728"
      - "crates/buzz-relay/src/api/admin/mod.rs:2775-3146"
      - "crates/buzz-relay/src/api/admin/mod.rs:3146-3262"
      - "crates/buzz-relay/src/api/admin/mod.rs:3262-3475"
      - "crates/buzz-relay/src/api/admin/mod.rs:3776-3852"
  - statement: "The last-effective-operator invariant (DbError::LastOperator, rejecting any upsert/delete that would leave the deployment with no effective operator) is tested at the buzz-db layer, not in buzz-relay's own admin/mod.rs suite: relay_operators.rs asserts a demotion is rolled back with LastOperator and no audit row is written, and a delete that would remove the last operator is rejected the same way. Both tests are #[ignore]-gated behind a running Postgres instance rather than run by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_operators.rs:636-690"
  - statement: "No file under desktop/src or web/src references admin_api or /api/admin in this checkout, so the admin SPA that consumes this API is an externally-supplied bundle served via BUZZ_ADMIN_WEB_DIR, not a client present in this repository."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='admin_api|/api/admin', scope='desktop/src/**;web/src/**') -> no matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "regression_relay_admin_ban_gate.rs in buzz-test-client exercises handlers/relay_admin.rs, the community-scoped Nostr relay-admin event handler for kinds 9030-9033, which is a distinct subsystem from the deployment-wide HTTP admin API this node documents and is intentionally out of scope here."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs:1-14"
  - statement: "No platforms-specific corpus template exists yet, and no other node under platforms/** exists on origin/launchpad for this document to follow as precedent, so type: platforms is used as the corpus-surface value (per node.schema.json's enum, 'the corpus surface this node documents') while the body is shaped after templates/component.md's Responsibility/Public interface/Dependencies/Boundary/Relationships/Scope-and-omissions structure, since component.md's four required-section categories map directly onto this task's own four DoD bullets (responsibility and interface/boundary, dependencies and collaborators, links to source and tests, component-level-only scope)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.6
---

# Relay deployment-admin HTTP API

One paragraph: this documents the relay's private, deployment-wide HTTP admin
API -- the `/api/admin/v1/*` route tree in `crates/buzz-relay/src/api/admin/` --
answering what surface it exposes, who may call it, and what it depends on.
It does not document the relay's public Nostr protocol surface, the
community-scoped moderation *event* handlers, or any specific admin console
frontend.

## Responsibility

The admin API is the relay's deployment-operator control plane: a private,
host-gated HTTP surface (mounted only when `BUZZ_ADMIN_HOST` is configured)
that lets a deployment-level Operator or Moderator triage cross-community
reports and product feedback, act on reports (dismiss, escalate, or enforce
delete/kick/ban/timeout), and staff the deployment's own operator/moderator
roster -- independent of any single community's own membership or moderation
state (`crates/buzz-relay/src/api/admin/mod.rs:1-5`).

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `GET /probe` | route | Returns auth mode, resolved role/source, and `canAct`/`canStaff` capability flags so a client can render its UI before attempting a mutation. | `crates/buzz-relay/src/api/admin/mod.rs:124-189` |
| `GET /reports`, `GET /reports/{id}` | route | Lists/reads cross-community reports; defaults to escalated-only visibility unless `status` or `scope=all` is given. Available in all auth modes. | `crates/buzz-relay/src/api/admin/mod.rs:191-263` |
| `POST /reports/{id}/resolve` | route | Dismiss/escalate (decision-only) or delete/kick/ban/timeout (enforcement state machine); requires a resolved principal (Operator or Moderator). | `crates/buzz-relay/src/api/admin/mod.rs:462-660` |
| `POST /reports/{id}/reopen` | route | Returns a terminal report to `open`, idempotent on a client `request_id`; requires a resolved principal. | `crates/buzz-relay/src/api/admin/mod.rs:662-741` |
| `POST /reports/{id}/cancel` | route | Cancels a pre-mutation `failed` enforcement action, fenced to the observed `action_id`; requires a resolved principal. | `crates/buzz-relay/src/api/admin/mod.rs:743-836` |
| `GET /feedback`, `GET /feedback/{id}`, `GET /feedback/{id}/attachments/{sha256}` | route | Lists/reads deployment-global product feedback and its media attachments, with tenant provenance re-verified server-side before serving an attachment. | `crates/buzz-relay/src/api/admin/mod.rs:265-405` |
| `PATCH /feedback/{id}` | route | Updates feedback lifecycle status (`new`/`reviewed`/`archived`); requires a resolved principal. | `crates/buzz-relay/src/api/admin/mod.rs:838-882` |
| `GET /operators`, `PUT /operators/{pubkey}`, `DELETE /operators/{pubkey}` | route | Lists the effective operator/moderator roster (config + DB union) and staffs it; requires Operator role. Config-backed pubkeys are immutable through the API and the last effective operator can never be removed. | `crates/buzz-relay/src/api/admin/mod.rs:886-1120` |
| `authorize()`, `resolve_admin_principal()`, `require_mutation_principal()`, `require_operator()` | fn | The auth boundary every route above calls before touching the database: Host/Origin gating, NIP-98 verification, Config > OwnerFallback > DB role resolution, and the mutation/staffing gates. | `crates/buzz-relay/src/api/admin/auth.rs:188-334` |
| `ApiError` | type | Uniform JSON error envelope (`code`, `message`, `request_id`); attaches `WWW-Authenticate: Nostr` on every 401. | `crates/buzz-relay/src/api/admin/error.rs:1-118` |
| `admin_api_origin()` | fn | Derives the canonical `scheme://host` origin (http for loopback, https otherwise) shared by NIP-98 `u`-tag verification and the NIP-11 `admin_api` advertisement. | `crates/buzz-relay/src/api/admin/auth.rs:147-156` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-auth` (`verify_nip98_event`) | Verifies the NIP-98 signature, timestamp, `u`/`method`/`payload` tags on every authenticated request. | `crates/buzz-relay/src/api/admin/auth.rs:399-401` |
| `buzz-db` (`admin_moderation`, `relay_operators` stores) | Backs every report/feedback/operator read and write: `AdminReport`/`AdminReportDetail`/`AdminFeedback`/`AdminActionDto` types and the `admin_*`/`reopen_report`/`cancel_admin_action`/`upsert_relay_operator`/`remove_relay_operator` methods. | `crates/buzz-db/src/store/admin_moderation.rs:24-455`, `crates/buzz-db/src/store/relay_operators.rs:285-330` |
| `crate::handlers::report_resolution` | Supplies the enforcement state machine (`resolve_report_with_enforcement`, `resolve_report_decision_only`, `http_validate_and_derive_status`, `enforcement_audit_action`) `resolve_report` calls into. | `crates/buzz-relay/src/api/admin/mod.rs:475-478` |
| `crate::tenant::bind_community` | Resolves the tenant from server-owned report/feedback provenance (never from client input) before any mutation or attachment read. | `crates/buzz-relay/src/api/admin/mod.rs:381-383`, `crates/buzz-relay/src/api/admin/mod.rs:536-539` |
| `crate::config::{AdminConfig, AdminAuth}` | Supplies the parsed `BUZZ_ADMIN_HOST`/`BUZZ_ADMIN_AUTH`/`BUZZ_ADMIN_WEB_DIR`/`RELAY_OPERATOR_PUBKEYS`/`RELAY_OWNER_PUBKEY` configuration every `authorize()` call reads. | `crates/buzz-relay/src/config.rs:27-73`, `crates/buzz-relay/src/config.rs:1040-1160` |
| `crate::api::media::serve_feedback_attachment` | Serves feedback attachment bytes once tenant provenance and the imeta hash are verified. | `crates/buzz-relay/src/api/admin/mod.rs:393-397` |
| `axum`, `tower-http` | Router, extractors, and the `RequestBodyLimitLayer`/`middleware::from_fn` layers the route tree is built from. | `crates/buzz-relay/src/api/admin/mod.rs:16-28` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crate::router::build_router` | Nests this module's router at `/api/admin/v1` (only when `state.config.admin.is_some()`) and routes the admin-host fallback to an externally-supplied SPA bundle before the public web bundle. | `crates/buzz-relay/src/router.rs:53-60`, `crates/buzz-relay/src/router.rs:149-176` |
| `crate::nip11::relay_info_handler` | Re-exports `admin_api_origin()` into the NIP-11 `admin_api` field so desktop can auto-discover the admin console origin. | `crates/buzz-relay/src/nip11.rs:55-62`, `crates/buzz-relay/src/nip11.rs:359-368` |
| An externally-supplied admin console SPA (not in this repository) | The intended human consumer of every route in *Public interface* above, served from `BUZZ_ADMIN_WEB_DIR`. No file under `desktop/src` or `web/src` in this checkout calls any `/api/admin/*` path. | grep across `desktop/src/**` and `web/src/**` for `admin_api`/`/api/admin` returns no matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523 |

## Boundary

This node does not describe:
- The relay's public Nostr protocol surface (WebSocket, NIP-01/NIP-98 bridge,
  media, git) -- that is the relay platform's own container-level concern,
  not this module.
- The community-scoped Nostr relay-admin *event* handlers (kinds 9030-9033,
  `crates/buzz-relay/src/handlers/relay_admin.rs`), pinned by
  `regression_relay_admin_ban_gate.rs`. That is a different subsystem: it acts
  on Nostr events signed by a *community* admin/owner, not on this module's
  NIP-98-authenticated HTTP requests from a *deployment-wide* Operator/
  Moderator. It is deliberately a separate node's subject, not folded in here.
- The externally-supplied admin console SPA frontend served from
  `BUZZ_ADMIN_WEB_DIR` -- it is not part of this repository, so there is no
  source to cite for its behavior.
- Deployment/operations concerns (how `BUZZ_ADMIN_HOST`/`BUZZ_ADMIN_AUTH` are
  actually set for a given environment, reverse-proxy or network-layer
  isolation when `BUZZ_ADMIN_AUTH=disabled`) -- that is operations-surface
  content, not this component's own interface/dependency description.

## Relationships

None declared. `launchpad/docs/corpus/platforms/` does not exist yet on
`origin/launchpad`, so there is no sibling `platforms/**` node (a relay
container/platform-level node, or a sibling `platforms/relay/*` component
node) to declare `part-of` or `depends-on` toward. Per `AGENTS.md`'s own rule,
a relationship target must resolve on the branch being merged into, not the
author's own worktree -- so none is declared here rather than guessed.

## Scope and omissions

**This node covers** the relay's deployment-admin HTTP API as one standalone
component: its route surface, its authorization boundary (Host/Origin/NIP-98/
role resolution), and its real dependency edges into `buzz-auth`, `buzz-db`,
and the rest of `buzz-relay`, plus what calls into it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The community-scoped Nostr relay-admin event handlers (kinds 9030-9033) | A separate, not-yet-filed corpus task -- distinct subsystem, per *Boundary* above |
| The relay's public Nostr/WebSocket/media/git surface | The relay platform's own container-level corpus node, once one exists |
| The admin console SPA frontend | Not in this repository (externally supplied via `BUZZ_ADMIN_WEB_DIR`) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Whether `type: platforms` is the corpus's settled convention for this surface | Not settled by any merged template at the time this node was written; used here per this batch's own sibling-node precedent (see the `INFERENCE` entry in this node's evidence ledger) |

**Expected but not verified when this node was written:**

- **Whether a `platforms`-specific template will later reshape this node's
  required sections.** No such template exists yet on `origin/launchpad`;
  this node borrows `templates/component.md`'s shape as the closest fit to
  issue #1261's own DoD bullets, and may need reshaping once a
  `platforms`-specific template is authored and merged.
- **The exact identity and behavior of the admin console SPA that consumes
  this API.** Confirmed only that no consumer exists inside `desktop/src` or
  `web/src` in this checkout; the SPA served from `BUZZ_ADMIN_WEB_DIR` was not
  located or inspected.
- **Whether any relay-hosted admin operations exist beyond the routes listed
  in *Public interface*.** This node enumerates exactly the routes registered
  in `crates/buzz-relay/src/api/admin/mod.rs`'s `router()` function at the
  recorded revision; a future route added there would need this node updated
  alongside it.
