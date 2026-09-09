# Plan: issue #1280 — document platforms/relay/operator-api

## ALREADY TRUE

- Issue #1280's DoD and scope are fixed: create exactly one hand-authored node at
  `launchpad/docs/corpus/platforms/relay/operator-api.md`. No such file exists on
  `origin/launchpad` today.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad` — this is
  the first node under that surface, alongside sibling tasks #1261 (`admin-api.md`,
  unmerged local branch, not present here) and #1266 (`community-provisioning.md`).
- No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`; sibling
  nodes in this Feature settled on borrowing `templates/component.md`'s section shape
  (Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope
  and omissions) with `type: platforms` instead of `type: implementation`, since
  `component.md` itself directs `type: implementation` for a single-crate subject but
  this Feature's own convention diverges for the `platforms/**` path.
- `launchpad/docs/corpus/architecture/context/relay-operator.md` (`architecture-context-
  relay-operator`) already exists on `origin/launchpad` and documents the *relay operator
  role* at context level — actors, two deployment paths, boundary — but explicitly defers
  "buzz-admin's command handling, the relay's own request routing" to a future
  container/component-level node. It does not document the `/operator/*` HTTP surface at
  all. This new node is that deferred detail, one level down.
- The real surface lives at `crates/buzz-relay/src/api/operator.rs` (1313 lines,
  route handlers + a `#[cfg(test)]` module), wired into the router at
  `crates/buzz-relay/src/router.rs` under five routes: `GET`/`POST
  /operator/communities`, `POST /operator/communities/archive`, `POST
  /operator/communities/unarchive`, `GET /operator/communities/availability`, `POST
  /operator/communities/transfer`.
- The operator API is deployment-root/multi-tenant (community lifecycle), NIP-98-only
  (no dev-mode fallback), authorized against a static `RELAY_OPERATOR_PUBKEYS` allowlist
  and a fixed `RELAY_OPERATOR_API_ORIGIN` — verified independent of the inbound `Host`
  header, unlike normal tenant-scoped NIP-98 bridge auth.
- The **admin API** (`/api/admin/v1/*`, `crates/buzz-relay/src/api/admin/mod.rs`) is a
  materially different surface: per-deployment moderation (reports/feedback) plus
  staffing (`/operators` roster CRUD), gated by `AdminConfig`/`AdminAuth` (`disabled` or
  `nip98`), and gives its own `AdminRole::Operator` grant to the *same*
  `RELAY_OPERATOR_PUBKEYS` allowlist as a fallback principal source — but does not
  require `RELAY_OPERATOR_API_ORIGIN` at all. This overlap (one pubkey allowlist, two
  distinct HTTP surfaces with different origin-binding and route sets) is a real,
  easy-to-conflate detail worth stating explicitly rather than silently.
- Community-provisioning mechanics themselves (host normalization, ownership bootstrap,
  membership snapshot publication) are issue #1266's scope
  (`community-provisioning.md`) — this node names the routes and auth surface, not the
  provisioning algorithm.

## STEP 1 — Confirm scope and template shape

Re-read `node.schema.json`, `AGENTS.md`, `templates/component.md`, and the existing
`architecture-context-relay-operator` node (done above). Confirm the target file does
not exist, and confirm `platforms/` is untouched on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`). Done —
verified no collision.

## STEP 2 — Read the real operator API surface

Read `crates/buzz-relay/src/api/operator.rs` in full (module doc, `authorize_operator_
request`, `check_operator_replay`, all five handlers, and the test module for behavior
this node can cite as FACT). Cross-check route wiring in `router.rs`, and the
`relay_operator_api_origin`/`relay_operator_pubkeys` config fields plus their boot-time
validation and warning in `config.rs`. Read `api/admin/mod.rs` and `api/admin/auth.rs`
far enough to state the operator-vs-admin distinction accurately (`AdminRole::Operator`
sourced from the same allowlist, but a separate route/origin surface). Done.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/operator-api.md` with:
- Front matter: `id: platforms-relay-operator-api`, `type: platforms`, `status: draft`,
  `origin: launchpad`, `audiences: [operator, developer, agent]`, evidence ledger citing
  only sources actually opened, `relationships: [{type: references, target:
  architecture-context-relay-operator}]` (confirmed present on `origin/launchpad`).
- Body sections (component.md shape, `platforms` convention): purpose/scope,
  responsibility, public interface (route table), auth model (NIP-98 + fixed origin +
  static allowlist + replay scope), dependencies, boundary (explicit: not admin-api, not
  community-provisioning mechanics, not the context-level role doc), relationships,
  scope and omissions (including the admin/operator allowlist-overlap gap and anything
  unverified, e.g. the unmerged admin-api sibling).

## STEP 4 — Validate and commit

Run the corpus unittest suite as the sole content of one Bash call, confirm `OK`; stage
exactly the new doc and this plan; commit with `git commit -s`, following the two-
separate-tool-call gate exactly. Verify zero new `validate.py` FAILs by diffing the FAIL
set with and without the new file.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must print `OK`, as the sole content of its Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` FAIL set must be identical
  with and without the new file present.
- Every `evidence[].evidence` citation must resolve to a real file actually opened
  (`crates/buzz-relay/src/api/operator.rs`, `crates/buzz-relay/src/router.rs`,
  `crates/buzz-relay/src/config.rs`, `crates/buzz-relay/src/api/admin/mod.rs`,
  `crates/buzz-relay/src/api/admin/auth.rs`, `launchpad/docs/corpus/architecture/
  context/relay-operator.md`).
- The `references` relationship target must resolve on `origin/launchpad`, confirmed via
  `git ls-tree`.

## OPEN

- Whether the admin-api sibling node (`#1261`) lands with an id this node should later
  cross-reference — it does not exist on `origin/launchpad` yet, so no relationship
  targets it now. Left as a scope-and-omissions gap, per finding #4/#5 in the batch
  instructions.
- Whether `platforms` is the Feature's final settled `type` for this path, or whether a
  dedicated `platforms`-shaped template lands later and this node needs reshaping. Noted
  as an inference, matching sibling nodes' own convention statement.

## LEFT OUT

- Community-provisioning algorithmic detail (host normalization, ownership bootstrap
  transaction, NIP-43 membership snapshot publication) — owned by #1266.
- The admin API's own moderation/staffing route detail — owned by #1261.
- Deployment/runbook instructions for setting `RELAY_OPERATOR_PUBKEYS`/
  `RELAY_OPERATOR_API_ORIGIN` operationally — that is `deploy/`-level material the
  existing `architecture-context-relay-operator` node already scopes out too.
