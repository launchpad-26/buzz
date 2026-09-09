# Plan: issue #1237 — document platforms/cli/environment-injection.md

## ALREADY TRUE

- `launchpad/docs/corpus/templates/architecture-component.md` is merged on
  `origin/launchpad` and matches this task's DoD bullets (responsibility,
  interface/boundary, dependencies/collaborators, source/test links,
  component-not-platform scope) almost verbatim.
- `launchpad/docs/corpus/architecture/containers/cli.md`
  (id `architecture-containers-cli`) is merged on `origin/launchpad` and
  already summarizes env injection in one paragraph plus one INFERENCE — this
  node exists to go one level deeper on that single facet, not to duplicate
  the container view.
- `launchpad/docs/corpus/platforms/cli/environment-injection.md` does not
  exist yet (confirmed: no `platforms/` tree on `origin/launchpad` at all).
- The real mechanism (`crates/buzz-acp/src/{acp.rs,lib.rs,config.rs,pool.rs}`)
  has been read directly at commit `cad6c375fdcc590158c1456c9fc7875f0f84a844`.

## STEP 1 — Front matter

`id: platforms-cli-environment-injection`, `type: architecture` (per the
architecture-component template's own INFERENCE: no finer-grained enum value
exists for component vs. container vs. context), `status: draft`,
`origin: launchpad`, `audiences: [agent, developer]`. One evidence entry per
substantive claim below; commit citation for the revision.

## STEP 2 — Body, from the template skeleton

Purpose paragraph naming `architecture-containers-cli` as the container being
decomposed. Mermaid component diagram + notation legend covering the two
real injection paths found in source: (a) the declarative `McpServer.env`
payload built by `build_mcp_servers` and enriched per-session by
`mcp_servers_with_git_origin`, sent over ACP `session/new`; (b) the direct
`Command::env` calls in `AcpClient::spawn` for the agent binary itself
(`default_agent_env`, `persona_env_vars`/`codex_network_env`), plus the
passive inheritance path from never calling `env_clear`.

## STEP 3 — Building block table

One row per mechanism, each citing the actual function/struct and line
range read: `CliArgs` env bindings, `build_mcp_servers`, `McpServer`/`EnvVar`,
`mcp_servers_with_git_origin`, `session_new_full`, `AcpClient::spawn`,
`default_agent_env`/`codex_network_env`.

## STEP 4 — Boundary, relationships, scope/omissions

Boundary excludes buzz-cli's own command/transport/exit-code facets (sibling
`platforms/cli/*` tasks), external actors, relay-side credential handling,
and manual (non-ACP) developer setup. One relationship:
`part-of: architecture-containers-cli` (confirmed present on
`origin/launchpad`). Scope/omissions names what wasn't verified: live
observation of env inheritance, and whether every ACP adapter actually
honors the declared `McpServer.env` when spawning the MCP subprocess.

## STEP 5 — Gate and commit

Run the corpus unittest suite as the sole content of one Bash call, confirm
`OK`, then run `validate.py` before/after (file removed/restored) to confirm
zero new FAILs, then stage + commit with `-s`.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK, as its own isolated Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` → identical 21
  pre-existing FAILs with and without this node (this node contributes zero
  new FAILs; its own commit-only FACT entries may print non-fatal
  UNVERIFIED, which is expected).
- Exactly one canonical document created:
  `launchpad/docs/corpus/platforms/cli/environment-injection.md`.

## OPEN

- Whether the agent/adapter that receives `session/new` actually spawns
  `buzz-dev-mcp` with the declared `env` is an ACP-protocol behavior outside
  this repository — not independently confirmed, named as a gap in the node.
- CLAUDE.md's own wording ("auto-injected... into managed agent
  subprocesses") does not distinguish the two mechanisms found in source;
  flagged in the node rather than resolved.

## LEFT OUT

- buzz-cli's command model, exit codes, output contract, and authentication
  — each is its own sibling task (#1236, #1238, #1239, #1235).
- Relay-side / `buzz-auth` handling of the injected credentials once used.
- Any change to runtime behavior — this is documentation only.
