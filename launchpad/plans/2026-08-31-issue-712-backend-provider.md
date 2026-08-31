# Plan: issue #712 — document capabilities/agents/backend-provider.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/agents/backend-provider.md` does not exist
  (confirmed by `test -f`); no directory `launchpad/docs/corpus/capabilities/` exists
  yet at all (`git ls-tree -r origin/launchpad -- launchpad/docs/corpus` lists none).
- `launchpad/docs/corpus/templates/capability.md` is merged and is the template to
  follow; `node.schema.json`'s `type` enum includes `capabilities` as its own value.
- `docs/remote-agents.md` ("Remote Agents and Their Management: A Formal
  Specification", status `draft`) is the authoritative in-repo spec for this
  capability: the provider protocol (`info`/`deploy` over stdin/stdout JSON),
  the remote lifecycle invariants (I1-I5), and the Kubernetes binding.
- The wire protocol is implemented in `crates/buzz-backend-kubernetes/src/wire.rs`
  and exercised by golden fixtures in
  `crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/` plus
  `tests/wire_fixtures.rs`.
- The desktop side lives in `desktop/src-tauri/src/managed_agents/backend.rs`
  (discovery, invocation, redaction, config validation, staged-negotiation
  deploy) and `desktop/src-tauri/src/commands/agents_deploy.rs` (payload
  construction including the `launch` block) / `commands/agents.rs`
  (`start_managed_agent`).
- CLAUDE.md's ecosystem table names `squareup/sprout-backend-blox` as a second,
  out-of-repo provider implementation ("Desktop backend provider script
  connecting Blox workstation agents to the relay") — its code is not in this
  repo and will not be cited as in-repo evidence.
- `launchpad/docs/corpus/architecture/deployment/kubernetes.md` already exists
  and explicitly scopes `buzz-backend-kubernetes` **out** of its own coverage
  (it documents the relay's deployment, not the agent-compute provider), so no
  duplication risk there.
- Repository revision for this node: `131b02f989684117d9ab1dd426f1673fa638e523`
  (current worktree HEAD, tracking `origin/launchpad`).

## STEP 1 — Draft the capability node

Write `launchpad/docs/corpus/capabilities/agents/backend-provider.md` using the
`capability.md` template shape (Capability statement / Maturity / Boundary /
Relationships / Scope and omissions), front matter:
`id: capabilities-agents-backend-provider`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator,
reviewer]`.

Evidence: cite `docs/remote-agents.md` (spec), `crates/buzz-backend-kubernetes/
src/wire.rs`, the provider-wire fixtures, `desktop/src-tauri/src/managed_agents/
backend.rs` (discovery/invocation/redaction/config validation/staged deploy),
`desktop/src-tauri/src/commands/agents_deploy.rs` (payload + launch block),
`desktop/src-tauri/src/commands/agents.rs` (`start_managed_agent`), CLAUDE.md's
ecosystem table (TEAM_KNOWLEDGE-adjacent but is in-repo Markdown so cited as
FACT), and `architecture/deployment/kubernetes.md`'s own out-of-scope
statement. Maturity claim will note that two of the spec's own "Known Defects
(at 28ae6cd21)" — the missing `launch` block and the missing `protocol_version`
negotiation gate — are verified fixed in the current tree (`build_launch_block`
is called from `deploy_payload_json`; `provider_deploy` now stages, calls
`info`, validates, then `deploy`), while the remaining listed defects are not
re-verified here and are left to the spec's own accounting.

One relationship: `references` → `architecture-containers-agent-runtime` (the
harness this capability launches onto a remote substrate), the only existing
corpus node that fits the template's "architecture node that realizes this
capability" guidance.

Done-when: file exists, front matter parses as YAML, all five required
template sections present, every FACT/INFERENCE citation points at a real
in-repo path.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Done-when: exit 0, and the new node contributes zero new FAIL entries (the 21
pre-existing FAILs tracked in #1951 are expected and untouched).

## STEP 3 — Earn the commit gate and commit

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Done-when: `OK`. Then, in a separate call, `git add` the new doc + this plan
file and `git commit -s`.

## GATES

- `validate.py` exit 0, zero new FAIL entries.
- `unittest discover` on corpus tests: `OK`.
- Commit is local only — no push, no PR.

## BUDGET

Single node, single commit. No code changes.

## OPEN

- Whether `docs/remote-agents.md`'s remaining "Known Defects" (harness
  inactivity reaper, pinned clean-exit contract, shutdown grace budget,
  Windows discovery suffix, numeric-field coercion) are still open at this
  revision was not re-verified beyond the two defects checked directly; the
  node states this as an explicit gap rather than assuming either way.

## LEFT OUT

- Any relationship to `architecture-deployment-kubernetes` (it deliberately
  scopes this capability out; adding an edge back would misrepresent that
  node's own boundary rather than support it — mentioned in prose instead).
- A second corpus node for the not-yet-drafted flow/interface siblings; out of
  scope per issue #712's own "Out of scope" list.
