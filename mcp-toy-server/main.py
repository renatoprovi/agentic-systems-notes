from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.resources import FileResource

NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"

mcp = MCPServer("agentic-systems-notes")

for note_path in sorted(NOTES_DIR.glob("*.md")):
    slug = note_path.stem
    mcp.add_resource(
        FileResource(
            uri=f"notes://{slug}",
            name=slug,
            title=note_path.name,
            description=f"Fichamento: {note_path.name}",
            mime_type="text/markdown",
            path=note_path,
        )
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
