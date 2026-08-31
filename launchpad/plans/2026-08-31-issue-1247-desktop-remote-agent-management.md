# Plan: issue #1247 — platforms/desktop/remote-agent-management corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/` does not exist yet on `origin/launchpad`; no duplicate to update.
- `launchpad/docs/corpus/architecture/containers/desktop.md` (id `architecture-containers-desktop`) and
  `.../agent-runtime.md` (id `architecture-containers-agent-runtime`) already exist on `origin/launchpad` —
  both are valid `relationships[].target`s.
- `launchpad/docs/corpus/templates/architecture-component.md` is the fitting template (issue text: "single
  canonical architecture component node"); required sections: purpose/scope, component diagram (mermaid),
  notation legend, building-block table, boundary statement, relationships, scope/omissions.
- `docs/remote-agents.md` (repo root) is the formal spec for the provider protocol; its own "Implementation
  Correspondence" table (lines 1687-1707) already maps spec concepts to the exact `desktop/src-tauri/src/
  managed_agents/` and `commands/agents*` files this node decomposes — confirms scope and avoids duplicating
  the spec's content.
- `desktop/src-tauri/src/managed_agents/types.rs` defines `BackendKind::{Local, Provider{id,config}}` — the
  code-level boundary named in the issue.

## STEP 1 — Read remote-provider code paths

Read `types.rs` (BackendKind), `managed_agents/backend.rs` (discovery, invocation, staging, redaction,
config validation), `commands/agents_deploy.rs` (deploy payload / launch block), `commands/agents/
provider_deploy.rs` (deploy orchestration + tenant-scope guard), `commands/agents/provider_access.rs`
(access-policy reconciliation), `managed_agents/access_policy.rs` (owner-only projection),
`commands/agent_providers.rs` (discovery/probe Tauri commands), and the `BackendKind::Local` branch guards
in `commands/agents.rs` (create/start/stop/delete). Cross-check against `docs/remote-agents.md`'s Stop-and-
Delete and Implementation Correspondence sections. Done.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/platforms/desktop/remote-agent-management.md`, `type: architecture`, id
`platforms-desktop-remote-agent-management`, following the architecture-component template: 7-row building
block table, C4-style Mermaid component diagram + legend, explicit boundary excluding local-agent-management
(#1242), the provider binary's own internals (`buzz-backend-kubernetes`), and the harness/spec content
already owned by `agent-runtime.md` / `docs/remote-agents.md`. `relationships`: `part-of` the desktop
container node, `depends-on` the agent-runtime container node (the launch/env contract this component builds
is consumed by that container's harness).

## STEP 3 — Validate

Run the corpus unit tests, then `python3 launchpad/project-intelligence/corpus/validate.py` with the new file
present and with it temporarily removed, confirming the new file adds zero new FAIL lines against the
pre-existing 21.

## STEP 4 — Commit

Stage the node + this plan file, commit with `-s`, per the batch's two-call gate sequence.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- `validate.py` FAIL set is identical with and without the new file (21 pre-existing FAILs, none new).
- Every evidence citation with a line range uses `path:A-B`.

## OPEN

- Whether `buzz-backend-kubernetes` (the shipped provider binary) deserves its own container-level or
  component-level corpus node — not filed as of this writing; flagged as a gap in *Scope and omissions*.
- Whether the harness-side shutdown-timing defect `docs/remote-agents.md` documents (Known Defect 7) should
  be re-derived in a corpus node — left to whichever node eventually documents `crates/buzz-acp`'s shutdown
  path; not re-derived here.

## LEFT OUT

- `BackendKind::Local` / the local-spawn lifecycle — issue #1242's scope, not duplicated here.
- The provider protocol's wire schema and five stated invariants in full — `docs/remote-agents.md` is
  authoritative; this node cites it rather than restating it.
- The ACP harness's internal shutdown/pool mechanics — `agent-runtime.md`'s and `crates/buzz-acp`'s scope.
