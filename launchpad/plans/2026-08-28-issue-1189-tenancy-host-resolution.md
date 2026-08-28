Issue #1189 — task: document layers/tenancy/host-resolution.md
Stated size: none stated  →  cap: 5 steps (single-document corpus task, parent PRD #607)

Target file: `launchpad/docs/corpus/layers/tenancy/host-resolution.md`
Node id: `layers-tenancy-host-resolution` (assigned by the task brief; permanent)
Base branch: `origin/launchpad` at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5

ALREADY TRUE  (verified against git at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, not notes)
  `launchpad/docs/corpus/layers/` does not exist in this worktree; this task creates it.
  `launchpad/docs/corpus/architecture/principles/host-selects-community.md` (id
    `architecture-principles-host-selects-community`) IS merged and on disk in this
    worktree — it states the row-zero *invariant* (host alone selects the community,
    fail closed) at the principle level and explicitly defers "the full per-surface
    conformance table" and implementation detail elsewhere. This task is that detail:
    the exact `Host` header → `CommunityId` mechanism, not a restatement of the
    invariant.
  Sibling issue #1104 ("document layers/identity/community-identity.md") has an open,
    unmerged PR (#1811); its target file does not exist on disk in this worktree. Per
    `launchpad/docs/corpus/AGENTS.md` step 9, a `relationships[].target` must resolve on
    the branch being merged into — so no relationship edge to it is possible yet. It is
    referenced in prose (not duplicated) as a pointer only.
  No `layers`-typed template exists under `launchpad/docs/corpus/templates/`, and
    `AGENTS.md`'s own scope table names per-type templates as not-yet-landed (#1307–
    #1351 range). Per AGENTS.md: "write the node against `node.schema.json` and the
    rules above."
  `node.schema.json` requires id, type, status, origin, audiences, evidence; permits
    `relationships`; rejects any other field. `type` includes `layers` in its enum.
  The mechanism lives in three places, already read in full: `crates/buzz-core/src/tenant.rs`
    (`normalize_host`, `relay_url_authority`), `crates/buzz-relay/src/tenant.rs`
    (`HostResolver`, `bind_community`, `bind_deployment_community`, the `redteam_attack2`
    empty-host regression tests), and the call site in
    `crates/buzz-relay/src/router.rs` (`nip11_or_ws_handler`, lines 273–320: raw `Host`
    header extraction via `.unwrap_or("")`, and the generic 404 rejection).
  `crates/buzz-db/src/lib.rs::lookup_community_by_host` (line 1262) does the durable
    lookup: `WHERE lower(host) = lower($1) AND archived_at IS NULL AND deleted_at IS NULL
    AND deletion_state = 'active'` — an exact, case-folded match only; no wildcard or
    subdomain pattern matching exists anywhere in the lookup. A community that has been
    archived or is mid-deletion (`deletion_state` != `active`, per migrations 0016/0029)
    stops resolving through this path and produces the identical generic rejection as a
    host that was never mapped.
  `migrations/0001_initial_schema.sql` line 61: `CREATE UNIQUE INDEX idx_communities_host
    ON communities (lower(host))` — the durable-side half of the same case-fold rule
    `normalize_host` applies on the lookup side.
  `crates/buzz-relay/src/api/admin/auth.rs::is_admin_host` is a *separate*, exact-string
    comparison against a single configured admin host, entirely outside `bind_community`
    and outside tenant resolution — a boundary this doc must name so a reader does not
    conflate the two host checks.

STEP 1  Create the node file with schema-valid front matter and provenance   [independent]
        Create `launchpad/docs/corpus/layers/tenancy/host-resolution.md` with
        `id: layers-tenancy-host-resolution`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, and the single
        commit-only FACT recording revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5. No
        `relationships` yet (added in STEP 2, only if the target genuinely resolves).
        done when: file exists with valid YAML front matter and
                   `git cat-file -e 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` exits 0.

STEP 2  Write the definition, boundaries, and the resolution algorithm     [needs 1]
        One-sentence definition up front (what host resolution is: the mechanism that
        maps an inbound `Host` header to a `CommunityId`). A boundaries/non-goals
        paragraph: this is not the row-zero *invariant* (linked to the principle node,
        not restated), not authorization inside a resolved community, and not the
        separate `is_admin_host` deployment-admin check. Then the algorithm end to end:
        header extraction and its `unwrap_or("")` empty-string fallback, `normalize_host`
        (lowercase, strip default port, strip trailing FQDN dot), the empty-host
        short-circuit in `bind_community` before any lookup, the exact case-folded DB
        lookup and its `archived_at`/`deleted_at`/`deletion_state` lifecycle filter, and
        the generic-rejection response shape. One `relationships` entry of type
        `references` to `architecture-principles-host-selects-community` (confirmed
        present on `origin/launchpad`). One `evidence` entry per claim, opened and cited
        to the real path.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
                   every FACT's cited file was opened in this session (checked by the
                   read tool calls already made, not re-read blind).

STEP 3  Write edge cases: missing Host, unknown host, no wildcard/subdomain support  [needs 2]
        Missing/unparseable `Host` header → empty string → same fail-closed rejection as
        an unmapped host (never a distinct error shape). Unknown host → `UnmappedHost`,
        generic 404, host never echoed. No wildcard or subdomain pattern matching exists:
        each community maps exactly one literal normalized host string; a deployment
        wanting `*.example.com` per-tenant hosting needs one `communities` row per
        subdomain, not a pattern. Archived/deleting communities lose resolution
        identically to never-mapped hosts. Cite the `redteam_attack2` regression tests
        for the empty-host case and the exact-match SQL for the no-wildcard case.
        done when: validator exits 0; each edge case names its source file/test.

STEP 4  Write "where this happens in the pipeline" and scope-and-omissions   [needs 3]
        State where in the request pipeline this runs: before `WebSocketUpgrade::from_request`
        in `nip11_or_ws_handler`, i.e. before any frame is read — cite the exact call
        site and line range read in this session. Note the one documented exception
        already covered by the principle node (NIP-11 served fail-open before binding)
        by reference, not restated in full. `bind_deployment_community` for
        no-inbound-Host surfaces gets one paragraph (what it is, why it exists) without
        re-deriving the principle node's per-surface enumeration. Scope-and-omissions:
        what this doc does not cover (full per-surface conformance table — linked to
        `docs/multi-tenant-conformance.md`; authorization inside a resolved community;
        the `is_admin_host` admin-plane check) and what was expected but not verified
        (whether every non-test call site outside the ones read here also goes through
        `bind_community`/`bind_deployment_community` — that audit belongs to the
        principle node, not duplicated here).
        done when: validator exits 0; body names the exact call-site file and the
                   principle-node link exists exactly once (not restated).

STEP 5  Audit the finished node against the issue's DoD and AGENTS.md          [needs 4]
        Re-read the diff against every Definition-of-Done checkbox in issue #1189 and
        against `AGENTS.md`'s create procedure. Confirm: exactly one hand-authored file
        was created; every FACT's citation was actually opened; the `references` edge to
        the principle node resolves; no second concept was folded in; the one-sentence
        definition and boundaries sections are both present; examples (if any) do not
        introduce a second canonical concept.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
                   `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
                   -p "test_*.py"` reports OK; `git status --short` shows exactly one new
                   file under `launchpad/docs/corpus/` plus this plan file.

PARALLEL  None. All five steps edit the same single file; corpus-node writing is
          inherently sequential regardless of section independence.

GATES     No `check-plan.sh` was found in this worktree (searched `launchpad/scripts/`
          and repo root); proceeding without it per the task's own fallback. Self-review
          only — verification in this task is not an independent `review-code` pass; the
          PR body says so and defers adjudication/cross-model review to the batch owner.

BUDGET    STEP 2/3. Distinguishing what this mechanism doc owns from what the already-
          merged principle node owns is the real risk — restating the principle's
          per-surface enforcement table here would be exactly the duplication AGENTS.md's
          atomicity rule forbids. Time goes into citing the algorithm precisely without
          re-deriving the invariant.

OPEN      Whether `developer` belongs in `audiences`. Resolved as **yes** here (unlike
          the pure-policy atomicity node): this document is mechanism detail a Buzz
          developer would read when adding a new host-scoped surface, not corpus-policy
          prose for agents/reviewers only.

LEFT OUT  A `relationships` edge to `community-identity` (#1104's node) — its file does
          not exist on `origin/launchpad`; adding it now would be exactly the trap
          AGENTS.md step 9 names. Follow-up once #1811 merges.
          Restating `docs/multi-tenant-conformance.md`'s full per-surface table — linked,
          not duplicated.
          Any change to `crates/buzz-relay` or `crates/buzz-core` source — this is a
          documentation-only task.
