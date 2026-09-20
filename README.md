# Agentic Systems Notes

Personal reading notes and small experiments on agentic systems, context engineering, and the Model Context Protocol — part of a self-directed study path toward platform/context architecture.

## Notes

Fichamentos, written in Portuguese (processing the material well matters more here than the display language). Read in order — each builds on the last:

- [00 · Mapa conceitual](notes/00-mapa-conceitual.md) — how the four texts below connect, with a diagram
- [01 · Building Effective Agents](notes/01-building-effective-agents.md) — workflow vs. agent, augmented LLM, ACI
- [02 · Agent Skills](notes/02-agent-skills.md) — the `SKILL.md` format, progressive disclosure
- [03 · Introducing the Model Context Protocol](notes/03-model-context-protocol.md) — the M×N problem, client-server architecture
- [04 · Build an MCP Server](notes/04-build-mcp-server.md) — resources/tools/prompts, the official quickstart
- [05 · Construindo o MCP toy server](notes/05-construindo-o-mcp-toy-server.md) — meta-fichamento: the build log for the project below, step by step, including what went differently from the quickstart

## `mcp-toy-server/`

A local MCP server that exposes this repo's own fichamentos (`notes/*.md`) as MCP **Resources**, plus a `search_notes` **Tool** on top of them — built while working through the official [MCP quickstart](https://modelcontextprotocol.io/docs/develop/build-server), deliberately covering the Resources primitive the quickstart's weather example leaves out. Full build log, including the API discoveries that didn't come from the docs: [05](notes/05-construindo-o-mcp-toy-server.md).

```bash
cd mcp-toy-server
uv run main.py                 # runs the server over stdio
uv run python smoke_test.py    # end-to-end check via a real MCP client (spawns main.py as a subprocess)
```

To use it from Claude Desktop or another MCP host, see the `claude_desktop_config.json` snippet in the build log (step 5).

## Scope

This repo is personal and independent — it has no affiliation with any employer, and contains no proprietary or internal material from anywhere I've worked.
