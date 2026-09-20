"""End-to-end check: spawn main.py as a real subprocess over stdio and talk
MCP to it through the actual client/session/wire-protocol path — the same
path Claude Desktop or any other MCP host uses, not the server's internal
manager shortcuts used while building steps 2-4.
"""

import asyncio

from mcp import Client
from mcp.client.stdio import StdioServerParameters

SERVER = StdioServerParameters(command="uv", args=["run", "main.py"])


async def main() -> None:
    async with Client(SERVER) as client:
        resources = await client.list_resources()
        print(f"Resources ({len(resources.resources)}):")
        for r in resources.resources:
            print(f"  - {r.uri}  ({r.title})")

        tools = await client.list_tools()
        print(f"\nTools ({len(tools.tools)}):")
        for t in tools.tools:
            print(f"  - {t.name}: {t.description}")

        read = await client.read_resource("notes://03-model-context-protocol")
        print("\nread_resource('notes://03-model-context-protocol'), first 100 chars:")
        print(" ", read.contents[0].text[:100].replace("\n", " "))

        search = await client.call_tool("search_notes", {"term": "ACI"})
        print("\ncall_tool('search_notes', term='ACI'):")
        for line in search.content[0].text.splitlines()[:5]:
            print(" ", line)


if __name__ == "__main__":
    asyncio.run(main())
