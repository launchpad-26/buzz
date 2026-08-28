# Issue #1183 — layers/tenancy/community-id.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and the `concept.md` template are merged on `origin/launchpad`. `launchpad/docs/corpus/layers/tenancy/` and `launchpad/docs/corpus/layers/identity/` do not exist yet on `origin/launchpad` or in this worktree — confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists no `layers/` path at all. Sibling issue #1104 (`layers/identity/community-identity.md`) has an open, unmerged PR (#1811) — its file is not on disk here and is not a valid relationship target.

STEP 1  Gather evidence: read `crates/buzz-core/src/tenant.rs` (`CommunityId`, `TenantContext`, `normalize_host`, `relay_url_authority`), `crates/buzz-relay/src/tenant.rs` (`HostResolver`, `bind_community`, the row-zero seam), `migrations/0001_initial_schema.sql` (the `communities` table, the `channels.community_id` immutability trigger, composite `(community_id, id)` keys on scoped tables), and `docs/multi-tenant-conformance.md` (row-zero contract and the per-surface tenancy table). ← RUNS HERE (done)

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-tenancy-community-id`, type `layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, no `relationships` — no existing merged node is a legitimate target, and #1104's sibling node is unmerged) and the body against the `concept.md` template shape: a one-sentence definition, scope/boundary against #1104 (identity/addressability: host-binding as the resolution mechanism and NIP-11 presentation) and against a future data-entity-style "Community" node, use cases (why the tenancy key matters: row-scoping, isolation, immutability), and a scope-and-omissions section.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must report `OK`. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review — not run here.

BUDGET: small — one document, no code changes, evidence gathering scoped to `buzz-core::tenant`, `buzz-relay::tenant`, one migration file, and one conformance doc.

OPEN: Issue #1183's own summary line (in the batch dispatch) distinguishes this node's tenancy angle (the internal `communities.id` as the isolation/scoping key) from #1104's identity/addressability angle (host-binding as an outward-facing resolution mechanism, NIP-11 relay-info presentation such as the workspace icon). Both nodes necessarily touch host resolution, since that is the one mechanism that produces a `CommunityId` — this node describes it only as the provenance of the tenancy key ("where does `community_id` come from"), not as its own subject; the addressability/NIP-11 story stays out.

LEFT OUT: No relationships to `layers-identity-community-identity` (#1104) — its file does not exist on `origin/launchpad` yet, and `AGENTS.md`'s creation procedure requires a target to already be merged into the branch being merged into. No claim about NIP-11 relay-info fields, `RelayInfo::build`, or the workspace `icon` — that is #1104's subject. No attempt to model "Community" as a full data-entity node (attributes, invariants beyond the tenancy key itself) — out of scope for a `layers`-typed concept node about the identifier.
