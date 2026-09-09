# Plan — issue #1126: `layers/networking/host-routing.md` (flow node)

Issue: `launchpad-26/buzz#1126` (Feature #609)
Target: `launchpad/docs/corpus/layers/networking/host-routing.md`
Node id: `layers-networking-host-routing`
Template: `launchpad/docs/corpus/templates/flow.md` (body shape only)
Base: `origin/launchpad` @ `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`

## ALREADY TRUE

- Worktree `__worktrees/task-1126-host-routing` on branch `task/1126-host-routing`
  exists at the base revision above.
- `launchpad/docs/corpus/layers/networking/` does **not** exist yet — this node
  creates the directory. Existing `layers/` subtrees are `compute`,
  `configuration`, `data`, `lifecycle`, `observability`.
- The runtime path has been read end to end, not inferred:
  - `crates/buzz-relay/src/router.rs` — `nip11_or_ws_handler` reads
    `header::HOST` (defaulting to `""`), short-circuits the admin authority,
    serves NIP-11 before binding, then calls `bind_community` before
    `WebSocketUpgrade::from_request`, returning `404 "relay: no community is
    configured for this host"` on any bind failure.
  - `crates/buzz-relay/src/tenant.rs` — `HostResolver`, `BindError`,
    `bind_community` (normalize → empty-host fence → resolve → three-way
    outcome), `bind_deployment_community`, and the `Db` resolver impl.
  - `crates/buzz-core/src/tenant.rs` — `normalize_host` (trim, ASCII-lowercase,
    strip `:443`/`:80`, strip one trailing FQDN dot), `TenantContext::resolved`,
    `CommunityId::from_uuid`.
  - `crates/buzz-db/src/store/community.rs` — `lookup_community_by_host`'s SQL,
    including its `archived_at IS NULL AND deleted_at IS NULL AND
    deletion_state = 'active'` predicate.
  - `crates/buzz-relay/src/connection.rs` — `handle_connection` takes the
    `TenantContext` and reads `tenant.community()` for registry + liveness.
  - `migrations/0001_initial_schema.sql` — `communities` table and
    `CREATE UNIQUE INDEX idx_communities_host ON communities (lower(host))`.
  - `crates/buzz-relay/src/api/admin/auth.rs` — `is_admin_host`'s exact compare.
  - `crates/buzz-test-client/tests/conformance_multitenant.rs` — the
    `unmapped_host_fails_closed_generically` obligation, `#[ignore]` by default.
- The two merged principle nodes were read in full:
  `architecture-principles-host-selects-community` and
  `architecture-principles-community-is-security-boundary`. Both own the
  **invariant** (`req.community = resolve_host(connection.host)`, fail closed,
  no client override). Neither narrates the ordered runtime sequence.
- `architecture-flows-websocket-connection` is merged and names host binding as
  **one precondition line**; it does not narrate normalization, the empty-host
  fence, the SQL predicate, or the non-WebSocket surfaces.
- Relationship targets confirmed present in the merged-id index.

## STEP 1 — create the node file with front matter

Write `launchpad/docs/corpus/layers/networking/host-routing.md` with exactly the
seven permitted front-matter fields: `id: layers-networking-host-routing`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, operator]`, `evidence`, `relationships`.

One provenance FACT citing `commit 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`
and no second commit-only FACT. Every sequence step gets its own FACT entry
citing bare repo-relative paths.

**Done when:** front matter parses and carries no eighth field.

## STEP 2 — write the flow body

Sections, per `templates/flow.md`: Flow statement · Sequence · Diagram ·
Outcome · Boundary · Relationships · Scope and omissions.

Sequence covers: Host read → admin short-circuit → NIP-11 fail-open →
`normalize_host` → empty-host fence → `communities` lookup → three-way outcome
→ `TenantContext` carried into the connection. Outcome covers success **and**
three real rejection paths (unmapped, lookup error, archived/deleted community
row). Diagram is a Mermaid `sequenceDiagram` whose participants match the prose
actors.

**Done when:** every sequence step carries a citation and the failure paths are
cited, not assumed.

## STEP 3 — boundary and relationships

Boundary says explicitly that the two principle nodes own the invariant and
this node owns the sequence; that `architecture-flows-websocket-connection`
owns the post-bind connection lifecycle; and names the template's five
exclusions. Relationships point only at merged ids.

**Done when:** no principle text is restated, only linked.

## STEP 4 — validate, stamp, commit

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`, as the sole command in its own call.
- `git add` + `git commit -s -m "docs(corpus): document host routing flow (#1126)"`.

**Done when:** validator exits 0, unittest prints OK, commit exists.

## STEP 5 — self-review against the DoD

Walk the issue's eleven DoD checkboxes one at a time against the written file.

**Done when:** each box is answered with the section that satisfies it.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → exit 0
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK
- No relationship target outside the merged-id index
- Exactly one hand-authored corpus file changed

## BUDGET

Five steps. One new corpus file plus this plan. No code changes, no generated
artifacts, no second corpus document.

## OPEN

- Whether a reverse proxy in front of the relay rewrites or preserves the
  `Host` header in the deployed topology is not established in this repository's
  relay source and is not settled here.
- The `#[ignore]`-gated conformance suite needs a live two-host relay; it is
  cited for the assertions it makes, not run.

## LEFT OUT

- `bind_deployment_community` (host-less server-internal paths) is a distinct
  subject — mentioned as a boundary, not narrated. Candidate follow-up task.
- The admin-host surface (`BUZZ_ADMIN_HOST`, admin SPA, NIP-98 `u`-host check)
  is its own subject. It appears in the sequence only as the short-circuit that
  precedes binding.
- `normalize_host`'s rule set as a standalone contract, and the
  `communities` schema itself.
