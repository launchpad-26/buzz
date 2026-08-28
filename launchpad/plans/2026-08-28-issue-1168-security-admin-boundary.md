# Plan: issue #1168 — document layers/security/admin-boundary.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/security/admin-boundary.md` does not exist yet
  (confirmed: `launchpad/docs/corpus` has no `layers/` directory at all —
  this is the first `type: layers` node in the corpus).
- Sibling `layers/authorization/operator-authorization.md` (#1038, PR #1805)
  also does not exist on disk in this worktree (checked out fresh from
  `origin/launchpad` at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`) — it is
  not a valid `relationships[].target` yet.
- `launchpad/docs/corpus/templates/invariant.md` (`id:
  corpus-template-invariant`) is the closest-fitting template: the DoD
  bullets ("state the invariant as one unambiguous property", "name
  enforcement points and observable failure behavior", "link a
  verification/conformance mechanism") are that template's own required
  sections almost verbatim, and no `policy`/`threat-model` fit is closer for
  a boundary framed as "what's on each side, what crossing it means, what's
  at risk."
- Real source evidence for the boundary already exists and is unusually
  well self-documented in-repo:
  - `crates/buzz-relay/src/handlers/community_provisioning.rs`'s module doc
    states the boundary directly: every other admin surface is
    community-scoped (role looked up in `relay_members`), but community
    *creation* requires an authority that "sits above tenants" — the
    deployment-level `RELAY_OPERATOR_PUBKEYS` allowlist.
  - `crates/buzz-relay/src/api/operator.rs::authorize_operator_request`
    checks a NIP-98-signed pubkey against `state.config.relay_operator_pubkeys`
    only — never against any `relay_members` row — and returns 403
    (`non_allowlisted_operator_key_gets_403`) otherwise.
  - `crates/buzz-relay/src/config.rs` doc comment on `relay_operator_pubkeys`:
    "Unlike `relay_owner_pubkey` (a role *within* the deployment community),
    operators span tenants" and "Empty (the default) disables community
    provisioning entirely — fail closed."
  - `crates/buzz-relay/src/handlers/relay_admin.rs::execute_relay_admin_command`
    is the contrasting in-band case: kind 9030-9033 commands are gated on
    the sender's own `relay_members` role for the tenant already resolved
    by `TenantContext` — strictly community-scoped, never cross-tenant.
  - `crates/buzz-admin/src/main.rs` (the `buzz-admin` CLI) is a third,
    deeper tier: no Nostr auth at all, run via `compose exec relay
    buzz-admin ...` inside the relay container, gated only by
    deployment/container access outside Buzz's own code.
- `launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md`
  and `.../fail-closed-boundaries.md` both exist on disk and are genuinely
  on-topic (tenant-boundary framing; fail-closed-on-empty-config framing) —
  legitimate `references` targets.

## STEP 1 — Confirm target absence and read governance docs

Re-confirm no `layers/` directory exists, read
`launchpad/docs/corpus/AGENTS.md` and `templates/invariant.md` in full, and
read `schema/node.schema.json` for the front-matter contract. (Done during
research for this plan.)

## STEP 2 — Gather and pin evidence

Read `community_provisioning.rs`, `operator.rs` (`authorize_operator_request`,
`provision_community`, `non_allowlisted_operator_key_gets_403`),
`relay_admin.rs` (`execute_relay_admin_command`, `handle_relay_admin_event`),
`config.rs` (`relay_operator_pubkeys`, `relay_owner_pubkey`), and
`buzz-admin/src/main.rs`, recording exact line numbers against
`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`. (Done during research for this
plan — see evidence ledger drafted into the node itself.)

**Done when:** every claim planned for the node's body has a citation opened
and read, not assumed.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/layers/security/admin-boundary.md` following
`templates/invariant.md`'s skeleton:
- `id: layers-security-admin-boundary`, `type: layers`, `status: draft`,
  `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`.
- Invariant statement: a community-scoped `relay_members` admin/owner role
  never grants deployment-level operator authority, and vice versa — the two
  are independent, non-overlapping checks.
- Scope: three tiers (in-community admin via kind 9030-9033; deployment
  operator via `/operator/communities*`; host/container-level `buzz-admin`
  CLI), what "crossing" means at each boundary, what's at risk if a tier
  boundary collapses.
- Enforcement today: named per tier (predicate/role-lookup-enforced for
  in-community; allowlist-check-enforced, fail-closed-on-empty, for
  operator; convention/deployment-access-only for `buzz-admin` CLI — no
  Buzz-internal enforcement at all).
- Consequence of violation: cite the actual 403 test and the `Banned`/`403`
  categorization work in `relay_admin.rs` for the in-band case; state
  plainly that the CLI tier has no in-repo enforcement to cite.
- Relationships: `references` → `architecture-principles-community-is-security-boundary`,
  `references` → `architecture-principles-fail-closed-boundaries`,
  `implements` → `corpus-template-invariant` (all three exist on
  `origin/launchpad` right now).
- Boundary + Scope and omissions sections per the template, explicitly
  naming `layers-authorization-operator-authorization` (#1038) as the
  sibling that will own the authorization *mechanism* once it exists, and
  naming that it does not exist yet.

**Done when:** `python3 launchpad/project-intelligence/corpus/validate.py`
exits 0 and every DoD bullet in #1168 is satisfied.

## STEP 4 — Verify, test, commit, PR

Re-read the diff against the DoD checklist and re-open every cited source.
Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as its own
command and confirm `OK`. Commit with `-s`. Push and open a **draft** PR.

**Done when:** PR is open, draft, `Closes #1168`, states self-review only.

## GATES

- `validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`, run as the sole command in its own call.
- Only one hand-authored canonical file created:
  `launchpad/docs/corpus/layers/security/admin-boundary.md`.

## OPEN

- Whether `layers-authorization-operator-authorization` (#1038) will
  ultimately `references` this node or vice versa is left to that task —
  not resolved here since it doesn't exist yet.

## LEFT OUT

- No relationship to `layers-authorization-operator-authorization` (doesn't
  exist on disk).
- No changes to any other corpus file, generated index, or non-corpus code.
- No resolution of whether `buzz-admin` CLI access should someday be brought
  under Buzz-internal enforcement — that's a product decision, not this
  node's job to make.
