# MCP Toy Server

A local MCP server exposing this repo's own reading notes (`../notes/*.md`) as **Resources**, plus a search **Tool** on top of them — built while working through the official [MCP quickstart](https://modelcontextprotocol.io/docs/develop/build-server), deliberately covering the Resources primitive the quickstart's weather example leaves out.

Build log and write-up: [`../notes/05-construindo-o-mcp-toy-server.md`](../notes/05-construindo-o-mcp-toy-server.md).

## Roadmap

All six steps done — see the build log for what each one actually involved, including what the quickstart didn't cover.

- [x] Project setup (`uv init`, `mcp[cli]`)
- [x] First Resource (one fixed note, exposed statically)
- [x] Dynamic Resources (list every file in `notes/`)
- [x] Search Tool (`search_notes(term)`)
- [x] Wire it to a real client (stdio, via a real MCP `Client` spawning the server as a subprocess)
- [x] Write-up (the build log above, plus the repo's root README)

## Run

```bash
uv run main.py                 # runs the server over stdio
uv run python smoke_test.py    # end-to-end check via a real MCP client
```
