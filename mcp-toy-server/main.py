from pathlib import Path
from typing import Annotated

from pydantic import Field

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


@mcp.tool()
def search_notes(
    term: Annotated[str, Field(description="Word or phrase to search for (case-insensitive).")],
) -> str:
    """Search this repo's reading notes for a term and return matching lines."""
    term_lower = term.lower()
    matches: list[str] = []
    for note_path in sorted(NOTES_DIR.glob("*.md")):
        text = note_path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if term_lower in line.lower():
                matches.append(f"{note_path.name}:{line_number}: {line.strip()}")

    if not matches:
        return f"No match for '{term}'."
    return "\n".join(matches)


if __name__ == "__main__":
    mcp.run(transport="stdio")
