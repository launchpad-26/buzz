# Plan: issue #1187 — document layers/tenancy/community.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/tenancy/community.md` does not exist on disk in
  this worktree or on `origin/launchpad` (checked directly).
- No `layers/` subtree exists under `launchpad/docs/corpus/` yet at all — this
  will be the first node under `layers/tenancy/`.
- `launchpad/docs/corpus/templates/concept.md` is a merged, real template
  (Diátaxis Explanation form + Good Docs Project Concept template). "Community"
  is an idea a reader must understand before the other tenancy nodes make
  sense, so this is a **concept**-shaped node, authored with `type: layers`
  (the corpus-surface enum value, per PRD #602 — `type` names the surface, not
  the documentation form).
- `launchpad/docs/corpus/architecture/context/buzz-platform.md`
  (`id: architecture-context-buzz-platform`) already exists on
  `origin/launchpad` and briefly defines community at context level (its
  "What 'the Buzz platform' is" section). It does not own the tenancy
  mechanism in depth — that is this node's job — so this node **references**
  it rather than duplicating its content.
- Primary sources read directly and confirmed as evidence-grade for this node:
  `ARCHITECTURE.md` (community definition + Step 0 Community Binding),
  `docs/multi-tenant-conformance.md` (row-zero conformance contract),
  `crates/buzz-core/src/tenant.rs` (`CommunityId`, `TenantContext`,
  `normalize_host`), `crates/buzz-relay/src/tenant.rs` (`HostResolver`,
  `bind_community`, `bind_deployment_community`, fail-closed semantics),
  `migrations/0001_initial_schema.sql` (`communities` table, operator-global
  registry, `community_id` FK pattern), `crates/buzz-core/src/kind.rs`
  (NIP-29 kind 39000/39001/39002 — these describe **channels**, not
  communities — a boundary this node must draw explicitly), and
  `crates/buzz-relay/src/handlers/community_provisioning.rs`
  (`provision_community`, the operator endpoint that creates/ensures a
  community by host).
- A genuine discrepancy was found and will be recorded as a verified gap, not
  resolved: `migrations/0001_initial_schema.sql`'s own header comment says
  existing single-community deployments "migrate via the documented backfill
  migration (0002)", but the current `migrations/0002_git_repo_names.sql` is
  unrelated (NIP-34 repo name registry), and no other migration filename
  matches "default community"/"backfill" except `0001` itself.

## STEP 1 — Confirm no in-flight duplicate

Re-check `origin/launchpad`'s corpus tree and open PRs targeting this issue
number/branch name before drafting, per the corpus-author skill's "one task,
one document" gate. (Already done once above; re-confirm immediately before
writing, since state can move between planning and drafting.)

**Done when:** confirmed no second canonical document exists for this task.

## STEP 2 — Draft `layers/tenancy/community.md`

Hand-author front matter (id: `layers-tenancy-community`, type: `layers`,
status: `draft`, origin: `launchpad`, audiences: `agent`, `developer`,
`operator`, `reviewer`) directly against `node.schema.json` (no `scaffold.py`
call needed — the template is merged, so this is not the "absent template"
branch). Follow `concept.md`'s required sections: Definition (community =
the tenant-visible workspace selected by request host, `TenantContext`/
`CommunityId` as the resolved key), Background (why host-derived resolution,
citing the conformance doc's row-zero rule), Use cases (why an agent/developer
needs to understand this before touching any community-scoped code), boundary
against Channel (NIP-29 kind 39000-39002 describe channels *inside* a
community, not the community itself — the single easiest confusion to make),
and Scope and omissions naming the nine sibling nodes from the issue body
that are deliberately deferred (community-id, community-membership,
community-scoped-cache, community-scoped-data, cross-community-isolation,
host-resolution, multi-community-mode, single-community-mode, tenant-context)
plus the migration-0002 discrepancy as an unresolved verified gap.

**Done when:** the file exists with schema-legal front matter and a body
satisfying every DoD bullet in issue #1187.

## STEP 3 — Validate

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

**Done when:** exit code 0.

## STEP 4 — Commit gate

Run, as the sole command in its own tool call:

```bash
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```

Confirm `OK`, then commit in a separate call with `git commit -s`.

**Done when:** suite reports `OK` and the commit is created (or a genuine
stamp-gate blocker is reported as a finding, never bypassed).

## STEP 5 — Push and open draft PR

Push the branch, then open a draft PR as a lone `gh pr create` command (no
`cd` prefix), body stating `Closes #1187`, that `validate.py` and the corpus
unittest suite both passed, that verification was self-review, and the
required "Draft — adjudicate/cross-model pass deferred..." line.

**Done when:** PR URL is in hand and reported back with the issue number.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Exactly one hand-authored canonical file created:
  `launchpad/docs/corpus/layers/tenancy/community.md`.

## OPEN

- Whether `#605`/`#607`'s eventual `layers/tenancy/` sibling nodes will want a
  `part-of` relationship pointing back at this node once they exist — left for
  those tasks to add, per AGENTS.md's "target must exist on the branch you
  merge into" rule.

## LEFT OUT

- No relationships to the nine sibling tenancy nodes named in the issue body —
  none exist on disk on `origin/launchpad` yet.
- No changes to `docs/`, `ARCHITECTURE.md`, or any product code.
- No resolution of the migration-0002 backfill-comment discrepancy — named as
  a verified gap only.
