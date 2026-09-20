from pathlib import Path

from mcp.server import MCPServer

NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"
FIRST_NOTE = NOTES_DIR / "01-building-effective-agents.md"

mcp = MCPServer("agentic-systems-notes")


@mcp.resource(
    "notes://building-effective-agents",
    name="building-effective-agents",
    title="Fichamento: Building Effective Agents",
    description="Reading note on workflow vs. agent, augmented LLM, and ACI.",
    mime_type="text/markdown",
)
def get_building_effective_agents() -> str:
    """Return this repo's fichamento for 'Building Effective Agents' as markdown."""
    return FIRST_NOTE.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")
