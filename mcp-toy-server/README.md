# MCP Toy Server

A local MCP server exposing this repo's own reading notes (`../notes/*.md`) as **Resources**, plus a search **Tool** on top of them — built while working through the official [MCP quickstart](https://modelcontextprotocol.io/docs/develop/build-server), deliberately covering the Resources primitive the quickstart's weather example leaves out.

Build log and write-up: [`../notes/05-construindo-o-mcp-toy-server.md`](../notes/05-construindo-o-mcp-toy-server.md).

## Roadmap

1. Project setup (`uv init`, `mcp[cli]`)
2. First Resource (one fixed note, exposed statically)
3. Dynamic Resources (list every file in `notes/`)
4. Search Tool (`search_notes(term)`)
5. Wire it to a real client (stdio + Claude Desktop or MCP Inspector)
6. Write-up (the build log above)

## Run

```bash
uv run main.py
```
