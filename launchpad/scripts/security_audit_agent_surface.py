"""The agent-configuration surface, in one place, for #68 and any future check
that needs the same list.

**Adding a new agent tool means adding one entry here** — a new directory (a
fifth `.<tool>/` convention) or a new config filename shape (a fifth kind of
persona/plugin/MCP file). Nothing else in #68's check needs to change.

Two kinds of surface, because they show up differently in the tree:

  AGENT_SURFACE_DIRS       top-level dotdirs a specific agent tool owns.
                            Scanned whole — anything under one of these is
                            in scope, regardless of filename.
  AGENT_CONFIG_FILE_GLOBS  filename shapes an agent pack uses wherever it
                            lives (e.g. `launchpad/agents/the-professor/`,
                            not under any `.{tool}/` directory at all) —
                            matched by glob across the whole repository.
"""

from __future__ import annotations

#: Top-level directories a specific agent tool owns. Verified present at repo
#: root as of #68 (each currently holds only a `skills/` subtree, but that is
#: not asserted here — the whole directory is in scope, not just what it
#: happens to contain today).
AGENT_SURFACE_DIRS = [
    ".claude",
    ".codex",
    ".goose",
    ".agents",
]

#: Filename shapes an agent/persona pack uses, wherever in the repository it
#: lives. Glob patterns, matched with `Path.rglob` from the repo root.
AGENT_CONFIG_FILE_GLOBS = [
    "**/.mcp.json",
    "**/*.persona.md",
    "**/plugin.json",
]
