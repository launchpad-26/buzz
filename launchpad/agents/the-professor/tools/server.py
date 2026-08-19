#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp", "pyyaml"]
# ///
"""The Professor's tool-server — the Facts layer of the three-layer design in
launchpad/Research/the-professor-design.md.

An MCP server (stdio transport) exposing the facts this agent must not
recall from memory. Step 3 of the plan builds exactly two tools:

  - read_contract()    the handbook's page contract, fetched live
  - list_categories()  the handbook's live navigation categories

Three more tools (resolve_pin, path_exists_at, check_page) are later plan
steps and are deliberately not built here.

Both tools fetch from launchpad-26/handbook at call time and never bake its
text into this file — per the design's own default: "nothing is quoted from
a document that changes... A quoted contract goes stale silently; a read one
cannot" (design doc, section "How the next agent gets built").

Runs as `uv run --script`, which is why the dependencies above are declared
inline (PEP 723) rather than via a requirements file or a checked-in venv:
this file is the single bare executable that a later step (Step 7's
buzz-acp wiring) must be able to spawn directly, with no `python3 <path>`
two-token form and no CLI flags. `uv` resolves and caches the dependencies
the first time this shebang line runs.
"""

import base64
import subprocess

import yaml
from mcp.server.mcpserver import MCPServer

HANDBOOK_REPO = "launchpad-26/handbook"

# Entries in the live mkdocs.yml `nav:` list that are excluded from
# list_categories(). Judgement call, stated here and in the report:
#
#   - "Home" (index.md) is a landing page, not a topic a reader picks
#     because they have a question about it.
#   - "The page contract" (page-contract.md) is reference material ABOUT
#     the corpus (what every page must carry), not a user-need category
#     the corpus is organized into. mkdocs.yml's own nav comment says the
#     hierarchy is "organised by user need, never by repository layout
#     (PRD Ruling 3)" -- the contract itself isn't a user need, it's the
#     spec the corpus is checked against.
#
# Excluding these two from the live 13-entry nav leaves the eleven entries
# PRD #4 Ruling 3 names. This code does not assert "13" or "11" as counts:
# it reads whatever the live nav contains and subtracts exactly these two
# titles, so it tracks the handbook if entries are ever added or renamed.
EXCLUDED_NAV_TITLES = {"Home", "The page contract"}

mcp = MCPServer(name="the-professor-tools")


def _fetch_handbook_file(path: str) -> str:
    """Fetch a file from launchpad-26/handbook at HEAD, live, via `gh api`.

    Uses the `gh` CLI (already authenticated in this environment) rather
    than a hand-rolled HTTP call with a token pulled from the environment,
    and never caches or bakes the result into source -- every call re-fetches.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{HANDBOOK_REPO}/contents/{path}", "-q", ".content"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    encoded_content = result.stdout.strip()
    return base64.b64decode(encoded_content).decode("utf-8")


@mcp.tool()
def read_contract() -> str:
    """Return the current text of the handbook's page contract.

    Fetched live from launchpad-26/handbook's docs/page-contract.md at call
    time -- never quoted into a prompt, so it can never go stale relative to
    a cached or hardcoded copy. See design doc section 4, "What the contract
    must be read, never copied."
    """
    return _fetch_handbook_file("docs/page-contract.md")


@mcp.tool()
def list_categories() -> list[str]:
    """Return the handbook's live navigation categories.

    Parses launchpad-26/handbook's mkdocs.yml `nav:` list at call time (never
    hardcoded) and excludes two structural entries that are not "categories"
    in PRD #4 Ruling 3's sense -- see EXCLUDED_NAV_TITLES above for which two
    and why. The remainder are the slots pages are filed into by the
    question they answer.
    """
    raw_yaml = _fetch_handbook_file("mkdocs.yml")
    nav_entries = yaml.safe_load(raw_yaml)["nav"]
    titles = [next(iter(entry.keys())) for entry in nav_entries]
    return [title for title in titles if title not in EXCLUDED_NAV_TITLES]


if __name__ == "__main__":
    mcp.run()  # defaults to stdio transport
