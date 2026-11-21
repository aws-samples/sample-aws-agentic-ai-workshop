"""
Strands agent that connects to the Gateway and uses the Petstore API as an
MCP tool.

Run setup_gateway.py first.
"""
import json

import requests
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

CONFIG_FILE = "gateway_config.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)


def get_access_token() -> str:
    """Gets an OAuth2 access token from Cognito (client_credentials flow).
    This token goes into the Authorization header when calling the Gateway."""
    response = requests.post(
        config["token_endpoint"],
        data={
            "grant_type": "client_credentials",
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "scope": config["scope"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


access_token = get_access_token()

gateway_mcp_client = MCPClient(lambda: streamablehttp_client(
    config["gateway_url"],
    headers={"Authorization": f"Bearer {access_token}"},
))

if __name__ == "__main__":
    # Ask by status rather than by a specific pet ID: the public Petstore is a
    # shared sandbox whose records anyone can delete, so a hardcoded ID may 404.
    user_input = (
        "Find the pets that are currently available in the store. "
        "List a couple of them and tell me which tool you used."
    )

    bedrock_model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

    agent = Agent(model=bedrock_model, tools=[gateway_mcp_client])
    response = agent(user_input)
