"""Bridge between this server's MCP tools and litellm's tool-calling format.

litellm (and the OpenAI-compatible providers it wraps) expect tools as
{"type": "function", "function": {"name", "description", "parameters"}} —
confirmed against litellm's own type definitions
(ChatCompletionToolParamFunctionChunk in litellm/types/llms/openai.py), not
guessed from memory. An MCP tool's `name`, `description` and `input_schema`
map onto that directly: MCP tool schemas are already JSON Schema, same as
`parameters` here.
"""

from typing import Any


def mcp_tool_to_litellm_tool(mcp_tool: Any) -> dict:
    """Convert one MCP Tool (from Client.list_tools()) into a litellm tool dict."""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.input_schema,
        },
    }


def decide(model: str, messages: list[dict], tools: list[dict]) -> "litellm.types.utils.ModelResponse":
    """Stand-in for `litellm.completion(model=model, messages=messages, tools=tools)`.

    In a real run, `model` is the ONLY thing that changes to point at a
    different provider — this function's signature mirrors that call shape
    exactly. What's simulated is only the model's decision (litellm's own
    `mock_response` can't simulate a tool_calls decision, confirmed in step
    2) — everything around this call (schema conversion, parsing the
    decision, executing the real tool) is unmodified by which `model` string
    comes in.
    """
    import json

    import litellm
    from litellm.types.utils import ChatCompletionMessageToolCall, Function, Message

    print(f"  [decide] chamado com model={model!r} ({len(tools)} tool(s) disponíveis)")

    # Whichever model this were pointed at, assume it reads the user's
    # message and decides to call the one relevant tool — the decision
    # itself doesn't vary by provider in this simulation; what we're
    # proving is that nothing downstream needs to know which model answered.
    tool_call = ChatCompletionMessageToolCall(
        id="call_simulated_0",
        type="function",
        function=Function(name="search_notes", arguments=json.dumps({"term": "ACI"})),
    )
    message = Message(role="assistant", content=None, tool_calls=[tool_call])
    return litellm.ModelResponse(
        model=model,
        choices=[{"message": message, "finish_reason": "tool_calls", "index": 0}],
    )


if __name__ == "__main__":
    import asyncio
    import json

    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    SERVER = StdioServerParameters(command="uv", args=["run", "main.py"])

    async def run_with_model(client: Client, tools: list[dict], model: str) -> None:
        messages = [{"role": "user", "content": "busca ACI nos fichamentos"}]
        response = decide(model=model, messages=messages, tools=tools)
        decided_call = response.choices[0].message.tool_calls[0]
        args = json.loads(decided_call.function.arguments)

        # Daqui pra baixo é tudo real, idêntico pros dois modelos: chama a
        # tool de verdade no servidor MCP e processa o resultado.
        result = await client.call_tool(decided_call.function.name, args)
        print(f"    -> tool real respondeu {len(result.content[0].text.splitlines())} linha(s)")

    def load_providers() -> list[dict]:
        from pathlib import Path

        import yaml

        path = Path(__file__).parent / "providers.yaml"
        return yaml.safe_load(path.read_text())["providers"]

    async def main() -> None:
        async with Client(SERVER) as client:
            mcp_tools = (await client.list_tools()).tools
            litellm_tools = [mcp_tool_to_litellm_tool(t) for t in mcp_tools]

            print("Passo 6 — provedores vêm do YAML, não do código:")
            for provider in load_providers():
                print(f"  [{provider['name']}]")
                await run_with_model(client, litellm_tools, provider["model"])

    asyncio.run(main())
