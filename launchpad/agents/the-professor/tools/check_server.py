#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""Test harness for server.py -- Step 3 of launchpad/plans/2026-08-19-issue-9-the-professor-persona.md.

This spawns `server.py` as a real subprocess (exactly how buzz-acp will
later spawn it: one bare executable path, no arguments) and talks to it
over stdio using the official MCP client, so this exercises the running
MCP server -- the JSON-RPC framing, the initialize handshake, tool
discovery, tool invocation -- not just the Python functions inside it.

Named check_server.py (not test_server.py) so verify-gate.sh's naming
convention recognizes it and this repo's pre-commit hook stamps a real
pass, matching launchpad/review-agent/check_*.py precedent.

Exit code 0 and "ALL CHECKS PASSED" on success; non-zero and a message
naming the failing check otherwise.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "server.py"


async def main() -> int:
    params = StdioServerParameters(command=str(SERVER_PATH), args=[])

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tool_names = {tool.name for tool in tools_result.tools}
            print(f"tools/list -> {sorted(tool_names)}")

            expected = {"read_contract", "list_categories"}
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

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
