# Plan: issue #1266 — document platforms/relay/community-provisioning.md

## ALREADY TRUE

- Worktree `__worktrees/task-1266-relay-community-provisioning` exists on branch
  `task/1266-relay-community-provisioning`, forked from `origin/launchpad` at
  commit `131b02f989684117d9ab1dd426f1673fa638e523`.
- `launchpad/docs/corpus/platforms/relay/community-provisioning.md` does not exist yet.
- No `platforms/**` directory exists at all yet under `launchpad/docs/corpus/` on
  `origin/launchpad` — this is the first node in that subtree.
- No `templates/platforms-*.md` template exists. `templates/component.md` is
  merged (`status: active`) and is the closest fit by section shape, but its own
  front matter prescribes `type: implementation` for a node built from it.
- Two existing merged nodes already cover adjacent ground and must not be
  duplicated: `architecture-principles-host-selects-community` (the row-zero
  host-resolution invariant) and `architecture-deployment-multi-community`
  (deployment topology, including a summary of `POST /operator/communities`
  as one bullet). Neither documents the handler-level contract, the two
  provisioning code paths (operator endpoint vs. startup seeding), or the
  `buzz-db` functions backing them — that gap is this node's scope.
- Investigated source (read in full): `crates/buzz-relay/src/handlers/community_provisioning.rs`,
  `crates/buzz-relay/src/api/operator.rs` (routes, NIP-98 auth wrapper,
  availability endpoint), `crates/buzz-relay/src/router.rs` (route table),
  `crates/buzz-db/src/store/community.rs` (`ensure_configured_community`,
  `create_community_with_owner`), `crates/buzz-db/src/store/relay_members.rs`
  (`bootstrap_owner`, `MAX_COMMUNITIES_PER_OWNER`), `crates/buzz-relay/src/main.rs`
  (startup seeding path), `crates/buzz-relay/src/config.rs` (`RELAY_OPERATOR_PUBKEYS`
  / `RELAY_OPERATOR_API_ORIGIN` parsing), `migrations/0001_initial_schema.sql`
  (`communities` table shape).
- Confirmed by reading both DB functions in full: no provisioning path inserts
  into `channels` or any other community-scoped table — a new community starts
  with zero channels. Worth stating explicitly as a scope note, not assumed.

## STEP 1 — Draft front matter

`type: platforms` (batch convention for `platforms/**`, no dedicated template
exists), `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
operator]`. One `evidence` entry per substantive claim below, classified
honestly (FACT for opened source, one INFERENCE for the `type: platforms` /
no-template choice and for the "this node's scope is the gap between the two
existing nodes" observation).

## STEP 2 — Write body per `component.md`'s section shape

Sections: opening paragraph (what/why), Responsibility, Public interface
(the two-path contract: `POST /operator/communities` request/response shape,
`GET /operator/communities/availability`), Dependencies (depends on:
`buzz-db` community/relay_members functions, NIP-98 auth, config; depended on
by: none found — this is a leaf operator surface), Boundary (explicit: not
the row-zero invariant, not deployment topology, not channel/message content
model), Relationships, Scope and omissions.

## STEP 3 — Declare relationships

`references` → `architecture-principles-host-selects-community` and
`references` → `architecture-deployment-multi-community` (both confirmed
present on `origin/launchpad` by `git ls-tree`, both read in full above).

## STEP 4 — Validate

Run `validate.py`, diff its FAIL set against a stashed-file baseline run to
confirm zero new FAILs, then restore the file.

## STEP 5 — Test, commit

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as its own Bash call, then `git add` + `git commit -s`.

## GATES

- `validate.py` exit 0, and the new file introduces zero new FAIL lines
  relative to the pre-existing ~21-23 baseline FAILs.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`.
- Every evidence citation points to a file actually opened during this task.
- Every DoD bullet in issue #1266 is satisfied.

## OPEN

- Whether a `platforms`-specific template ever lands and reshapes this node's
  section structure — not this task's to resolve, per `AGENTS.md`.

## LEFT OUT

- Re-documenting the row-zero host-resolution invariant (owned by
  `architecture-principles-host-selects-community`).
- Re-documenting deployment topology, Kubernetes/Helm, backup/recovery
  (owned by `architecture-deployment-multi-community`).
- Community deletion/archival state machines (owned by that same deployment
  node, citing `migrations/0016_community_archival.sql` /
  `migrations/0029_community_deletion.sql`, not re-read here).
- Channel/message data model — out of scope per the DoD's "component-level,
  not the entire containing platform" bullet.
