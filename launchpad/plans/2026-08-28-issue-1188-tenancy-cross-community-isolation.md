# Plan: issue #1188 — document layers/tenancy/cross-community-isolation.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/tenancy/cross-community-isolation.md` does not
  exist anywhere in this worktree or on `origin/launchpad` at revision
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- `launchpad/docs/corpus/templates/invariant.md` is merged and present
  (`id: corpus-template-invariant`), so this node is written against that
  template's required sections, not against a bare schema with no template.
- `launchpad/docs/corpus/standards/normative-language.md` is merged, so
  MUST/MUST NOT phrasing follows its RFC 2119 convention.
- Three closely related nodes are already merged and provide real
  relationship targets: `architecture-principles-host-selects-community`
  (the row-zero host→community selection invariant), `architecture-
  principles-community-is-security-boundary` (client signals never override
  the resolved community), and `architecture-deployment-multi-community`
  (the deployment shape). All three focus on *which* community a request is
  bound to. Neither covers *confinement* — whether data already scoped to
  community B ever becomes observable from a B-scoped connection when it
  should not — which is this issue's actual subject.
- The sibling security-framing doc `layers/security/tenancy-boundary.md`
  (#1179, PR #1832) is not present in this worktree (branched before it
  would have merged) — the boundary between the two documents is drawn in
  prose only, per the task brief.
- Real, verifiable mechanism-level evidence exists for the confinement
  invariant specifically: `docs/multi-tenant-relay.md`'s Isolation Boundary
  and Safety Theorems sections, `docs/spec/MultiTenantRelay.tla`'s
  `Inv_NonInterference`/`Inv_ReadConfinement`, the composite
  `community_id`-leading primary keys in `migrations/0001_initial_schema.sql`,
  `EventQuery::for_community` and `get_accessible_channel_ids` in
  `crates/buzz-db`, and the runtime conformance checker in
  `crates/buzz-conformance` with its always-run
  `foreign_row_leak_is_non_interference` test.
- Postgres native Row-Level Security (the formal spec's A-RLS axiom family)
  was searched for (`CREATE POLICY`, `ENABLE ROW LEVEL SECURITY`) across
  `migrations/` and found nowhere — the shipped schema does not carry the
  backstop the formal proof assumes as an axiom. This is a real gap, not
  resolved by this task, and belongs in the node's honest "Enforcement
  today" section rather than being smoothed over.
- `crates/buzz-relay/src/conformance/mod.rs`'s own doc comment states the
  read path (`req.rs` / `event.rs`) wiring into the runtime trace emitter is
  "held back as an additive patch" — the live relay does not yet emit
  read-confinement traces for the checker to verify against real traffic.

## STEP 1 — Draft the node

Hand-author `launchpad/docs/corpus/layers/tenancy/cross-community-isolation.md`
against `templates/invariant.md`'s required sections (Invariant statement,
Scope, Enforcement today, Consequence of violation, Boundary, Relationships,
Scope and omissions). Front matter: `id: layers-tenancy-cross-community-
isolation`, `type: layers`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator, reviewer]`. State the invariant as
read/write confinement (non-interference), not as the host-selection
mechanism (already owned by the two `architecture/principles` nodes above,
which this node `depends-on`/`references` rather than restates). Classify
every claim honestly: FACT only for sources actually opened this session;
name the RLS gap and the partial runtime-wiring gap explicitly rather than
rounding either up.

**Done when:** the file exists with schema-required front matter and all
required template sections, citing only sources opened this session.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root.

**Done when:** exit code 0.

## STEP 3 — Run the corpus unit test suite

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call, per the commit-gate contract.

**Done when:** output ends `OK`.

## STEP 4 — Commit, push, open draft PR

Commit with `git commit -s`. Push the branch. Open a draft PR against
`launchpad` with `--head`/`--base` explicit (no `cd` in the same Bash call as
`gh pr create`), body stating `Closes #1188`, that validation and the unit
suite both passed, that verification was self-review only, and the standard
"draft — adjudicate/cross-model pass deferred" line.

**Done when:** PR URL is returned by `gh pr create`.

## GATES

- `validate.py` exits 0 before every "done" claim.
- The corpus unit test suite (`python3 -m unittest discover -s
  launchpad/project-intelligence/corpus/tests -p "test_*.py"`) must print `OK`
  before committing, run as its own isolated command.
- No `entry_class: FACT` without a source actually opened this session.
- No `relationships[].target` naming an id not present in `origin/launchpad`'s
  corpus tree as of this plan (verified above: the three architecture nodes
  plus `corpus-template-invariant` all exist there).

## OPEN

- Whether `layers/security/tenancy-boundary.md` (#1179) ends up drawing the
  boundary the same way this node expects — not verifiable from this
  worktree since that PR is not merged here. Stated as a prose-only boundary,
  not a `relationships` edge, since the target file does not exist on
  `origin/launchpad` at this revision.
- Whether `conformance_multitenant.rs`'s `#[ignore]`-gated A/B isolation
  suite currently passes against a live two-host deployment — not run this
  session (matches the same caveat the two sibling architecture nodes
  already recorded).

## LEFT OUT

- Standing up a live multi-tenant relay to actually execute the `#[ignore]`d
  conformance suite — out of scope for a documentation task and explicitly
  out of scope per the issue's own "Out of scope" list ("changing runtime
  product behavior").
- Wiring the missing `req.rs`/`event.rs` runtime trace emission — a real
  code gap this node names but does not fix; filing it is a candidate
  follow-up issue, not part of this task.
- Restating `docs/multi-tenant-conformance.md`'s full per-surface obligation
  table — already out of scope for the two sibling architecture nodes for
  the same reason (duplication), and out of scope here too.
