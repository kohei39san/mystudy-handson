import os
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient


app = BedrockAgentCoreApp()


def create_gateway_client() -> MCPClient | None:
    gateway_url = os.getenv("AGENTCORE_GATEWAY_URL")
    if not gateway_url:
        return None
    return MCPClient(lambda: streamablehttp_client(gateway_url))


def run_agent(prompt: str) -> Any:
    mcp_client = create_gateway_client()
    if mcp_client is None:
        return Agent()(prompt)

    with mcp_client:
        tools = mcp_client.list_tools_sync()
        return Agent(tools=tools)(prompt)


@app.entrypoint
def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    result = run_agent(prompt)
    return {"response": str(result)}


if __name__ == "__main__":
    app.run()
