# Plan: issue #713 — document capabilities/agents/managed-agent.md

## ALREADY TRUE

- Repo revision for this plan: `131b02f989684117d9ab1dd426f1673fa638e523` (= `origin/launchpad` tip at
  worktree creation).
- Target file `launchpad/docs/corpus/capabilities/agents/managed-agent.md` does not exist.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`) is the template to
  follow; it requires: Capability statement, Maturity (cited), Boundary, Relationships, Scope and
  omissions, and states `type: capabilities` (plural — confirmed in `node.schema.json`'s enum, not
  invented).
- No `capabilities`-typed node is merged yet (`grep -rl "^type: capabilities"` returns nothing) — this
  is the first node under `capabilities/`.
- `architecture-containers-agent-runtime` (`launchpad/docs/corpus/architecture/containers/agent-runtime.md`)
  is already merged and documents the agent-runtime container in depth, including the managed-vs-remote
  launcher distinction at a container level. My node must `references` it rather than re-describe it.
- Sibling issue #716 (`capabilities/agents/remote-agent.md`) is OPEN/unmerged — no relationship target
  exists for it yet.
- Evidence gathered directly from source, confirmed by line number:
  - `crates/buzz-acp/src/acp.rs` — `spawn` (fn at line 454) inherits the parent process environment
    (no `env_clear()` anywhere in the file) and layers persona `extra_env` on top with operator-wins
    precedence; `shutdown` (fn at line 422) kills the subprocess's process group and bounds the wait at
    5s.
  - Root `AGENTS.md:203-205` — "Auth env vars (`BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`) are
    auto-injected by the ACP harness into managed agent subprocesses."
  - `docs/remote-agents.md:31-36` — "the desktop is one launcher among many": what makes a process a
    live Buzz agent is a keypair, NIP-OA auth tag, and relay URL handed as environment to `buzz-acp`.
  - `docs/remote-agents.md:1770-1775` (Summary) — "Remote agents extend Buzz's managed-agent model
    across a deliberately thin boundary" — states managed-agent as the base model remote-agent extends.
  - `desktop/src-tauri/src/managed_agents/types.rs:6-9` — `BackendKind::Local` (`#[default]`) is the
    variant for a managed/local agent, contrasted with `BackendKind::Provider { id, config }` for remote.
  - `desktop/src-tauri/src/managed_agents/types.rs:761` — `DEFAULT_ACP_COMMAND: &str = "buzz-acp"`,
    the sidecar the desktop spawns for every local managed agent.
  - `desktop/src-tauri/src/managed_agents/runtime.rs:592-593` — desktop stamps a spawned local agent's
    env with `BUZZ_MANAGED_AGENT` (an ownership marker), confirming the desktop directly manages the
    subprocess it launches.

## STEP 1 — Write the node

Create `launchpad/docs/corpus/capabilities/agents/managed-agent.md` from the capability template:
front matter (`id: capabilities-agents-managed-agent`, `type: capabilities`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`), one `references` relationship to
`architecture-containers-agent-runtime`, and a body with Capability statement / Maturity / Boundary /
Relationships / Scope and omissions, satisfying every #713 DoD bullet.

**Done when:** file exists, front matter matches `node.schema.json`, body has all required sections.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root of the worktree.

**Done when:** exit 0, and diffing against the known 21 pre-existing baseline FAIL entries (#1951)
shows zero new FAIL entries attributable to the new node.

## STEP 3 — Self-review against DoD and re-open cited sources

Re-read every #713 DoD line against the drafted body. Re-open every cited source (acp.rs, AGENTS.md,
remote-agents.md, managed_agents/types.rs, runtime.rs) to confirm the citations still say what the
evidence ledger claims.

**Done when:** every DoD bullet is traceable to a specific section of the node; no citation found stale.

## STEP 4 — Earn the commit gate, commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then, in a separate tool call, `git add` the new node + this plan file and
`git commit -s`.

**Done when:** commit created locally; no push, no PR.

## PARALLEL

None — single file, single author, no independent parallel track.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests` reports `OK`.
- Commit is signed off (`-s`), created locally only.

## BUDGET

Single node, ~1 sitting. No architecture/interface/flow content duplicated.

## OPEN

- Whether a future `capabilities-agents-remote-agent` node (once #716 merges) should declare the
  inverse `references` edge back to this node — left for that node's own author, per AGENTS.md's
  merge-target relationship rule.

## LEFT OUT

- No second corpus document. No relationship to `capabilities-agents-remote-agent` (unmerged — would be
  a hard validation error in CI per AGENTS.md's own merge-target-branch rule).
- No architecture, interface, or flow content restated — `references` the existing
  `architecture-containers-agent-runtime` node instead.
