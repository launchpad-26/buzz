# Plan: issue #1040 — document layers/authorization/scopes.md

Parent PRD: #607. Sibling task #1035 (event-authorization) targets the same
`layers/authorization/` directory but has not merged to `origin/launchpad` at
this revision (338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) — the directory does
not exist yet on that branch, confirmed by `find launchpad/docs/corpus/layers`
returning nothing.

## ALREADY TRUE

- `crates/buzz-auth/src/scope.rs` defines `Scope`, a 16-variant enum plus
  `Unknown(String)`, with `all_known()`, `all_non_admin()`, `as_str()`,
  `Display`, `FromStr` (infallible — unrecognised strings become `Unknown`),
  and `parse_scopes()`.
- `crates/buzz-auth/src/lib.rs`'s `AuthContext.scopes: Vec<Scope>` plus
  `has_scope()`; `AuthService::verify_auth_event` (NIP-42) always grants
  `Scope::all_known()` — "pure Nostr mode" grants full scopes and relies on
  NIP-29 channel membership for per-channel enforcement.
- `crates/buzz-auth/src/access.rs`'s `require_scope()`, `check_read_access()`
  (requires `MessagesRead`), `check_write_access()` (requires `MessagesWrite`).
- `crates/buzz-relay/src/handlers/ingest.rs`'s `required_scope_for_kind()`
  maps every enforced event kind to a required `Scope`.
- `crates/buzz-relay/src/handlers/event.rs` enforces `MessagesWrite` for
  ephemeral kinds and for `KIND_AGENT_OBSERVER_FRAME` directly against
  `ctx.scopes`/`scopes` before dispatch.
- `crates/buzz-relay/src/api/bridge.rs:835` also grants `Scope::all_known()`
  on the bridge HTTP auth path, same "pure Nostr" reasoning.
- `crates/buzz-auth/src/error.rs`'s `AuthError::InsufficientScope { required,
  have }` is the enforcement failure shape.
- No existing corpus node targets `crates/buzz-auth/src/scope.rs`,
  `AuthContext.scopes`, or `require_scope` (grep of `launchpad/docs/corpus/`
  found none).
- `launchpad/docs/corpus/layers/authorization/scopes.md` does not exist.
- No corpus template is literally named "layers" — `type` is the corpus
  *surface* taxonomy (PRD #602), not the documentation form. The doc's
  *form* here is Explanation/Concept (Diátaxis), matching
  `templates/concept.md`'s required sections; `type: layers` per the issue.

## STEP 1 — Confirm evidence and gap

Re-open `crates/buzz-auth/src/scope.rs`, `lib.rs`, `access.rs`,
`error.rs`, `ingest.rs::required_scope_for_kind`, `event.rs` (ephemeral +
observer-frame gates), `bridge.rs:835`. Confirm one real gap worth recording:
`all_non_admin()` is defined and doc-commented as "used in dev mode" but has
zero call sites outside `scope.rs`'s own tests (grepped repo-wide) — the dev
mode fallback that would call it is not yet wired. Record this as an
INFERENCE/gap in the "Expected but not verified" section, not silently
smoothed over.
Done when: every cited symbol has been read at its current line range.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/layers/authorization/scopes.md` against
`node.schema.json` directly (no template file matches "layers" as a form;
`concept.md`'s required-sections shape is followed for the prose). Front
matter: `id: layers-authorization-scopes`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, evidence
ledger citing only opened files, no `relationships` (no sibling node exists
on disk in this directory yet). Body: one-sentence definition first, scope
mechanics (grant, storage as wire strings, enforcement points), boundary
against channel-membership-based access (NIP-29) and against
event-kind-to-scope mapping owned by `ingest.rs` (not duplicated here),
worked example, scope-and-omissions section naming the dev-mode gap.
Done when: file exists, one canonical document only.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix any
schema violation until exit 0.
Done when: validator exits 0.

## STEP 4 — Test suite + commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own call, confirm `OK`, then
commit with `git commit -s`.
Done when: suite reports OK and commit succeeds (or is reported blocked, not
forced).

## STEP 5 — PR

Push branch, open draft PR against `launchpad-26/buzz` closing #1040, body
states validator + unittest pass, self-review only, draft note per the task
brief.
Done when: PR URL exists.

## GATES

- Corpus `validate.py` exit 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Exactly one hand-authored corpus file created:
  `launchpad/docs/corpus/layers/authorization/scopes.md`.

## OPEN

- Whether `all_non_admin()`'s intended dev-mode call site will ever land —
  not this task's to resolve; recorded as a gap only.

## LEFT OUT

- Documenting `required_scope_for_kind`'s full kind-to-scope table (that's
  `ingest.rs`'s own implementation detail, linked not duplicated).
- Documenting NIP-29 channel membership mechanics (separate concept, not
  this node's subject — scopes and membership are two different gates that
  compose, per `access.rs`'s `check_read_access`/`check_write_access`).
- Any relationship edge to sibling authorization docs (#1035, #1036, #1037,
  #1038, #1039) — none exist on disk in `origin/launchpad` at this revision.
