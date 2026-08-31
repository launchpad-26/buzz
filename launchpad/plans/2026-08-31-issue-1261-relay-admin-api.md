# Plan: issue #1261 — corpus node for platforms/relay/admin-api

## ALREADY TRUE

- Isolated worktree exists at `__worktrees/task-1261-relay-admin-api`, branch
  `task/1261-relay-admin-api`, based on `origin/launchpad` @
  `131b02f989684117d9ab1dd426f1673fa638e523`.
- Issue #1261 read (`gh issue view 1261 --repo launchpad-26/buzz`). Its DoD requires:
  one hand-authored node, schema-valid front matter with typed relationships,
  one independently-maintainable idea, every substantive claim traceable and
  classed FACT/INFERENCE/TEAM_KNOWLEDGE, links to source+tests+specs without
  duplicating them, checked against a recorded revision, `validate.py` clean,
  and four component-shaped bullets: states responsibility and
  well-defined interface/boundary, names dependencies and collaborators, links
  source implementation and tests, explains only component-level behavior (not
  the whole platform).
- `launchpad/docs/corpus/platforms/relay/admin-api.md` does not exist.
  `launchpad/docs/corpus/platforms/` does not exist at all yet on
  `origin/launchpad` — this is the first node under that surface in this
  worktree's view of the corpus.
- Investigated the real admin HTTP API in `crates/buzz-relay/src/api/admin/`:
  - `mod.rs` (7651 lines): `pub fn router()` wires
    `/probe`, `/reports`, `/reports/{id}`, `/reports/{id}/resolve|reopen|cancel`,
    `/feedback`, `/feedback/{id}` (GET+PATCH), `/feedback/{id}/attachments/{sha256}`,
    `/operators` (GET), `/operators/{pubkey}` (PUT/DELETE). Two middleware
    layers (`security_headers`, a 4096-byte body limit). ~2500 lines of
    `#[cfg(test)] mod tests` exercise host/origin gating, NIP-98 replay/
    substitution, role gating (Operator vs Moderator), config-backed-pubkey
    immutability, last-operator invariant, and report/feedback CRUD.
  - `auth.rs`: `authorize()`, `resolve_admin_principal()` (Config >
    OwnerFallback > DB precedence), `require_mutation_principal()`,
    `require_operator()`, NIP-98 verification via `buzz_auth::verify_nip98_event`.
  - `error.rs`: `ApiError` envelope, `WWW-Authenticate: Nostr` on 401.
  - `crates/buzz-relay/src/router.rs`: mounts the admin router at
    `/api/admin/v1` only when `state.config.admin.is_some()`, and serves an
    externally-supplied admin SPA bundle (`BUZZ_ADMIN_WEB_DIR`) from the same
    admin-host fallback, isolated from the public web bundle.
  - `crates/buzz-relay/src/config.rs`: `AdminConfig`/`AdminAuth` parsed from
    `BUZZ_ADMIN_HOST`, `BUZZ_ADMIN_AUTH` (`nip98` default / `disabled`),
    `BUZZ_ADMIN_WEB_DIR`, `RELAY_OPERATOR_PUBKEYS`, `RELAY_OWNER_PUBKEY`.
  - `crates/buzz-relay/src/nip11.rs`: re-exports `admin_api_origin()` into the
    NIP-11 `admin_api` field for desktop auto-discovery.
  - `crates/buzz-db/src/store/admin_moderation.rs` and
    `relay_admin_actions.rs`: `AdminReport`, `AdminReportDetail`,
    `AdminFeedback`, `AdminActionDto`, `Db::admin_list_reports`,
    `Db::admin_get_report`, `Db::reopen_report`, `Db::cancel_admin_action`, etc.
  - `migrations/0035_relay_operators.sql`, `0039_relay_operator_audit.sql`:
    the `relay_operators` roster table this module reads/writes.
  - Confirmed **no** consumer of `/api/admin/v1` exists inside `desktop/` or
    `web/` in this repo (grep for `admin_api`/`/api/admin` — no hits): the
    admin SPA is an externally-supplied bundle, not part of this checkout.
  - Confirmed `regression_relay_admin_ban_gate.rs` in `buzz-test-client` tests
    a **different** subsystem (`handlers/relay_admin.rs`, Nostr kind
    9030-9033 community-scoped admin *events*) — not this HTTP API. Kept out
    of this node to avoid folding two ideas together.
- No `platforms-specific` template exists yet in
  `launchpad/docs/corpus/templates/`. Read `templates/component.md` (its
  Required sections — Responsibility, Public interface, Dependencies,
  Boundary, Relationships, Scope and omissions — map almost 1:1 onto #1261's
  four component-shaped DoD bullets) and `templates/architecture-component.md`
  (rejected: that template is for decomposing a *container*, with a required
  diagram; this node documents one HTTP-API module standing alone, not a
  container's whole internal structure).
- Per the orchestrator's known finding #4, sibling nodes in this Feature have
  already settled on `type: platforms` for files under `platforms/**`, as an
  `INFERENCE` (no platforms-specific template exists to confirm it). Followed
  here for consistency; `component.md`'s own suggested `type: implementation`
  is not used, since surface (`type`) and document shape (template) are
  orthogonal per that template's own text.
- Read `launchpad/docs/corpus/schema/node.schema.json` and
  `launchpad/docs/corpus/AGENTS.md` in full for the front-matter contract and
  authoring procedure.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/admin-api.md`:
- Front matter: `id: platforms-relay-admin-api`, `type: platforms`,
  `status: draft`, `origin: launchpad`,
  `audiences: [agent, developer, operator, reviewer]`, an `evidence` ledger
  (commit citation + one `FACT` per source file/test actually opened, plus the
  `INFERENCE` for the `type: platforms` convention choice), no
  `relationships` (nothing on `origin/launchpad`'s corpus tree to target yet —
  `platforms/` itself doesn't exist there).
- Body shaped like `component.md`'s skeleton: Responsibility, Public interface
  (route table), Dependencies (depends-on / depended-on-by), Boundary
  (explicitly excludes the relay-admin Nostr-event subsystem, the admin SPA
  frontend, and deployment/ops concerns), Relationships, Scope and omissions.
Done when: file exists, every evidence citation names a path this session
actually opened, every DoD bullet in #1261 is answered by a named section.

## STEP 2 — Local re-verification pass

Re-open every cited file/line against the diff and confirm each statement is
actually supported (not just structurally present). Done when: a full re-read
of the new file against #1261's DoD checklist finds no unsupported claim.

## STEP 3 — Zero-new-FAIL check

Stash the new file, run
`python3 launchpad/project-intelligence/corpus/validate.py`, record the FAIL
set, restore the file, run it again, diff. Done when: the FAIL set is
byte-identical before/after (this node introduces zero new FAILs).

## STEP 4 — Commit gate

Two separate Bash calls, in order:
1. `cd .../task-1261-relay-admin-api && python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole content of the call.
2. `git add` the two new files and `git commit -s -m "docs(corpus): document platforms/relay/admin-api (#1261)"`.
Done when: commit succeeds with a verification stamp (retry once per finding
#5 if refused).

## STEP 5 — Final report

Diff review against DoD, confirm zero new validate.py FAILs, report worktree
path / branch / commit SHA. Stop — no push, no PR.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`, as the sole content of its Bash call.
- `validate.py` FAIL set unchanged with vs. without the new file.
- `git commit -s` succeeds with the commit-gate's verification stamp (retry once, then report BLOCKED if it fails twice).

## OPEN

- Whether `type: platforms` is genuinely the sibling-batch convention cannot
  be independently confirmed from this worktree (no sibling `platforms/**`
  branches are visible here) — trusting the orchestrator's stated finding #4
  and flagging the choice as an `INFERENCE` in the node's own evidence ledger.
- No `relationships` declared — nothing on `origin/launchpad`'s corpus tree
  is a valid target yet.

## LEFT OUT

- A second node for the community-scoped Nostr relay-admin event subsystem
  (kinds 9030-9033, `handlers/relay_admin.rs`) — a distinct idea from the
  deployment-wide HTTP admin API this node documents; not folded in.
- Any change to `crates/buzz-relay` or other production code — this is a
  docs-only corpus task.
- Documenting the admin SPA frontend itself — it is an externally-supplied
  bundle (`BUZZ_ADMIN_WEB_DIR`) not present in this repository.
