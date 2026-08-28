# Plan: issue #1191 — document layers/tenancy/single-community-mode.md

Parent PRD: #607. Repository revision checked: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`
(origin/launchpad).

## ALREADY TRUE

- `launchpad/docs/corpus/layers/tenancy/single-community-mode.md` does not exist
  on disk (confirmed via `ls`) and no `layers/tenancy/` directory exists yet.
- `launchpad/docs/corpus/architecture/deployment/single-relay.md`
  (`id: architecture-deployment-single-relay`) is a merged, draft-status corpus
  node describing the *deployment topology* (one Compose bundle, one host, one
  relay process) — confirmed present on `origin/launchpad` at the recorded
  revision, not just in this worktree.
- `launchpad/docs/corpus/architecture/principles/host-selects-community.md`
  (`id: architecture-principles-host-selects-community`) is a merged, draft-status
  corpus node describing the row-zero host-binding invariant, and already states
  the one sentence closest to this task's subject: "The single-community
  deployment is the degenerate case of the same rule: one configured host
  resolves to the one default community, so an existing single-tenant deployment
  observes no behavior change." Confirmed present on `origin/launchpad`.
- Sibling issue #1190 (`layers/tenancy/multi-community-mode.md`) has no file on
  disk under `launchpad/docs/corpus/layers/` at all — nothing to link yet.
- `docs/multi-tenant-conformance.md` and `crates/buzz-relay/src/main.rs` /
  `crates/buzz-db/src/lib.rs` (`ensure_configured_community`, doc-commented
  "the startup/config seeding path for N=1 deployments") are real, already-open
  primary sources for the runtime behavior this node must describe.
- No `check-plan.sh` script is discoverable in this checkout.

## Gap this task fills

`single-relay.md` documents *where the process runs* (Compose topology). It does
not document what changes about the relay's *runtime tenancy behavior* when
exactly one community is configured — which is this node's subject: host
resolution is not bypassed or specialized for N=1, it is the same fail-closed
`bind_community` path with exactly one row in `communities`, auto-provisioned at
boot from `relay_url`.

## STEP 1 — Confirm no duplication, gather evidence

Re-confirm the target path is absent (done above) and that no other corpus node
already covers single-community runtime *behavior* specifically (`single-relay.md`
covers topology; `host-selects-community.md` covers the general row-zero
invariant, of which single-community is one sentence, not full treatment).
Evidence already gathered this session:
- `crates/buzz-relay/src/main.rs` (deployment-community bootstrap sequence,
  `ensure_configured_community`, `backfill_from_allowlist`, `bootstrap_owner`)
- `crates/buzz-db/src/lib.rs#symbol=ensure_configured_community` (doc comment:
  "the startup/config seeding path for N=1 deployments")
- `crates/buzz-relay/src/config.rs` (`RELAY_URL` default, `relay_operator_pubkeys`
  default-empty test assertion, `require_relay_membership` default-false test
  assertion)
- `crates/buzz-relay/src/handlers/community_provisioning.rs` (module doc: operator
  provisioning is disabled by default; the mechanism that would grow N past 1)
- `docs/multi-tenant-conformance.md` (N=1 compatibility rule, "degenerate case"
  language, migration gate 5)
- `crates/buzz-test-client/tests/conformance_multitenant.rs` (`mod n1_parity`:
  N=1 parity is asserted by the *existing* e2e suites staying green, not a new
  test)
- `scripts/cutover/README.md` + `scripts/cutover/1321_backfill_default_community.sql`
  (historical: pre-1321 Buzz *was* single-community-only; this is the one-time
  cutover script, not startup behavior — cited as background/history, not as
  current runtime behavior)
- `scripts/seed-local-community.sh` (local-dev bootstrap of the host→community row)

Done when: evidence list above is what backs the node's evidence ledger; no
claim in the body lacks a citation to one of these opened sources.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/layers/tenancy/single-community-mode.md` directly
against `node.schema.json` (no `layers`-typed template exists yet per
`launchpad/docs/corpus/AGENTS.md`'s gap table). Front matter: `id:
layers-tenancy-single-community-mode`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator]`. Body covers: what
single-community mode *is* (N=1 case of the tenancy model, not a separate code
path), how it is reached (boot-time auto-provisioning from `relay_url`, not an
explicit "mode" flag), what stays identical to pre-multi-tenant Buzz (N=1 parity
guarantee), what an operator can/cannot do while N=1 (provisioning a second
community is opt-in and off by default), and the historical cutover path for
pre-1321 data. `relationships`: `references` → `architecture-deployment-single-relay`
(topology) and → `architecture-principles-host-selects-community` (the general
invariant this is the degenerate case of) — both confirmed present on
`origin/launchpad`.

Done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
and every DoD checklist bullet in issue #1191 is satisfied by name.

## STEP 3 — Verify

Re-read the diff against every DoD bullet; re-open every cited source to confirm
it supports its claim; confirm exactly one hand-authored file was created; re-run
`validate.py`.

## STEP 4 — Commit gate and PR

Run the corpus unittest suite as its own command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`),
confirm `OK`, then commit (`git commit -s`), push, and open a draft PR per the
task's exact template, closing #1191.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Only one hand-authored file under `launchpad/docs/corpus/` in the diff.

## OPEN

- Whether issue #1190's node lands before this PR merges (checked: it has not,
  as of this revision) — no relationship targets it either way.

## LEFT OUT

- Any edit to `architecture/deployment/single-relay.md` or
  `architecture/principles/host-selects-community.md` — this task only links to
  them, per the issue's explicit instruction not to duplicate their framing.
- A `layers`-type template — none exists yet (AGENTS.md gap table); not this
  task's job to create one.
