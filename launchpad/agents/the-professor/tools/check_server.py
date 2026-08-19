#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""Test harness for server.py -- Steps 3-4 of launchpad/plans/2026-08-19-issue-9-the-professor-persona.md.

This spawns `server.py` as a real subprocess (exactly how buzz-acp will
later spawn it: one bare executable path, no arguments) and talks to it
over stdio using the official MCP client, so this exercises the running
MCP server -- the JSON-RPC framing, the initialize handshake, tool
discovery, tool invocation -- not just the Python functions inside it.

resolve_pin's check goes one step further than "did it return 40 hex
characters": it independently cross-checks the SHA against `git ls-remote`
against the real block/buzz repo, so a plausible-looking but wrong SHA
(e.g. a stale or truncated response that happened to still be 40 hex chars)
would still be caught.

path_exists_at's check exercises both the true and false cases against a
real pinned commit (resolved via resolve_pin, not hardcoded): a real path
known to exist in block/buzz at that commit, and a fabricated path that
does not. A check that only tried the happy path would not catch a version
of the tool that always returns True regardless of the path.

check_page's check runs two REAL fixtures from launchpad-26/handbook's own
tests/fixtures/ through the tool over stdio, not synthetic input this file
invents:

  - tests/fixtures/compliant.md must come back with zero findings AND zero
    skipped (both -- a tool that silently skipped everything would also
    report zero findings, and only checking findings would not catch that).
  - tests/fixtures/broken-03-prefix-repo-mismatch.md must come back with a
    finding whose rule is exactly "prefix-repo-mismatch".

broken-01-behaviour-claim-unsourced.md is deliberately NOT used as a negative
control here: tests/fixtures/README.md's own engine column marks it a
judgement-engine fixture, and check_provenance.py's own docstring says the
judgement rules (unsourced behaviour claims, unattributed opinion,
self-contradiction) are "a separate engine and deliberately not in this
script" -- so that fixture returns zero findings regardless of whether
check_page works, and a check built on it could never fail. broken-03 is a
script-engine rule (prefix_repo.py) and fires deterministically.

Named check_server.py (not test_server.py) so verify-gate.sh's naming
convention recognizes it and this repo's pre-commit hook stamps a real
pass, matching launchpad/review-agent/check_*.py precedent.

Exit code 0 and "ALL CHECKS PASSED" on success; non-zero and a message
naming the failing check otherwise.
"""

import asyncio
import base64
import json
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "server.py"
HANDBOOK_REPO = "launchpad-26/handbook"


def _fetch_handbook_fixture(name: str) -> str:
    """Fetch one tests/fixtures/*.md file from launchpad-26/handbook, live.

    Same `gh api` + base64-decode convention server.py's own
    `_fetch_handbook_file` uses -- this check does not hardcode fixture text
    into this file either, so it always exercises check_page against
    whatever the handbook's fixtures currently say.
    """
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{HANDBOOK_REPO}/contents/tests/fixtures/{name}",
            "-q",
            ".content",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return base64.b64decode(result.stdout.strip()).decode("utf-8")


async def main() -> int:
    params = StdioServerParameters(command=str(SERVER_PATH), args=[])

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tool_names = {tool.name for tool in tools_result.tools}
            print(f"tools/list -> {sorted(tool_names)}")

            expected = {
                "read_contract",
                "list_categories",
                "resolve_pin",
                "path_exists_at",
                "check_page",
            }
            if tool_names != expected:
                print(
                    f"FAIL: expected exactly {expected}, server exposes {tool_names}"
                )
                return 1

            # --- list_categories ---
            categories_result = await session.call_tool("list_categories", {})
            if categories_result.is_error:
                print(f"FAIL: list_categories errored: {categories_result.content}")
                return 1
            categories = categories_result.structured_content
            print(f"list_categories() -> {categories}")

            if "Home" in str(categories) or "The page contract" in str(categories):
                print("FAIL: list_categories did not exclude Home / The page contract")
                return 1

            # --- read_contract ---
            contract_result = await session.call_tool("read_contract", {})
            if contract_result.is_error:
                print(f"FAIL: read_contract errored: {contract_result.content}")
                return 1
            contract_text = "".join(
                block.text for block in contract_result.content if hasattr(block, "text")
            )
            print(f"read_contract() -> {len(contract_text)} chars")

            if "The claim rule" not in contract_text:
                print("FAIL: read_contract text does not contain 'The claim rule'")
                return 1

            # --- resolve_pin ---
            pin_result = await session.call_tool(
                "resolve_pin", {"repo": "block/buzz", "ref": "main"}
            )
            if pin_result.is_error:
                print(f"FAIL: resolve_pin errored: {pin_result.content}")
                return 1
            sha = "".join(
                block.text for block in pin_result.content if hasattr(block, "text")
            ).strip()
            print(f"resolve_pin('block/buzz', 'main') -> {sha}")

            if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
                print(f"FAIL: resolve_pin did not return a 40-char hex SHA: {sha!r}")
                return 1

            # Independently confirm the SHA against the real remote -- not
            # just "is it 40 hex chars", but "is it the actual current main".
            ls_remote = subprocess.run(
                ["git", "ls-remote", "https://github.com/block/buzz", "main"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if ls_remote.returncode != 0:
                print(f"FAIL: git ls-remote failed: {ls_remote.stderr}")
                return 1
            remote_sha = ls_remote.stdout.split()[0] if ls_remote.stdout.split() else ""
            print(f"git ls-remote block/buzz main -> {remote_sha}")

            if sha != remote_sha:
                print(
                    f"FAIL: resolve_pin's SHA {sha!r} does not match "
                    f"git ls-remote's {remote_sha!r}"
                )
                return 1

            # --- path_exists_at: true case (real path, pinned commit) ---
            true_result = await session.call_tool(
                "path_exists_at",
                {
                    "repo": "block/buzz",
                    "commit": sha,
                    "path": "crates/buzz-persona/PERSONA_PACK_SPEC.md",
                },
            )
            if true_result.is_error:
                print(
                    "FAIL: path_exists_at errored on a real path: "
                    f"{true_result.content}"
                )
                return 1
            exists = true_result.structured_content
            print(f"path_exists_at(real path) -> {exists}")
            if exists.get("result") is not True:
                print(f"FAIL: path_exists_at(real path) did not return True: {exists!r}")
                return 1

            # --- path_exists_at: false case (fabricated path, same commit) ---
            false_result = await session.call_tool(
                "path_exists_at",
                {
                    "repo": "block/buzz",
                    "commit": sha,
                    "path": "crates/buzz-persona/THIS_FILE_DOES_NOT_EXIST_9f8e7d6c.md",
                },
            )
            if false_result.is_error:
                print(
                    "FAIL: path_exists_at errored on a fabricated path (should "
                    f"return False, not error): {false_result.content}"
                )
                return 1
            missing = false_result.structured_content
            print(f"path_exists_at(fabricated path) -> {missing}")
            if missing.get("result") is not False:
                print(
                    f"FAIL: path_exists_at(fabricated path) did not return False: "
                    f"{missing!r}"
                )
                return 1

            # --- check_page: compliant fixture, must be clean ---
            compliant_content = _fetch_handbook_fixture("compliant.md")
            compliant_result = await session.call_tool(
                "check_page", {"draft_content": compliant_content}
            )
            if compliant_result.is_error:
                print(
                    "FAIL: check_page errored on compliant.md: "
                    f"{compliant_result.content}"
                )
                return 1
            # check_page returns a plain `dict`, which the mcp SDK does not
            # populate `structured_content` for (unlike the `bool`/`list[str]`
            # tools above) -- parsed from the text content instead, same as
            # read_contract's check does.
            compliant_text = "".join(
                block.text for block in compliant_result.content if hasattr(block, "text")
            )
            compliant_report = json.loads(compliant_text)
            print(f"check_page(compliant.md) -> {compliant_report}")

            if compliant_report.get("findings"):
                print(
                    "FAIL: check_page(compliant.md) reported findings, expected "
                    f"none: {compliant_report['findings']!r}"
                )
                return 1
            if compliant_report.get("skipped"):
                print(
                    "FAIL: check_page(compliant.md) reported skipped pages, "
                    f"expected none: {compliant_report['skipped']!r}"
                )
                return 1

            # --- check_page: broken-03, must report prefix-repo-mismatch ---
            #
            # NOT broken-01-behaviour-claim-unsourced.md -- see this file's module
            # docstring for why that fixture cannot serve as a negative control.
            broken03_content = _fetch_handbook_fixture(
                "broken-03-prefix-repo-mismatch.md"
            )
            broken03_result = await session.call_tool(
                "check_page", {"draft_content": broken03_content}
            )
            if broken03_result.is_error:
                print(
                    "FAIL: check_page errored on broken-03: "
                    f"{broken03_result.content}"
                )
                return 1
            broken03_text = "".join(
                block.text for block in broken03_result.content if hasattr(block, "text")
            )
            broken03_report = json.loads(broken03_text)
            print(f"check_page(broken-03) -> {broken03_report}")

            broken03_rules = {
                finding.get("rule") for finding in broken03_report.get("findings", [])
            }
            if "prefix-repo-mismatch" not in broken03_rules:
                print(
                    "FAIL: check_page(broken-03) did not report a "
                    f"prefix-repo-mismatch finding. Rules seen: {broken03_rules!r}"
                )
                return 1

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
