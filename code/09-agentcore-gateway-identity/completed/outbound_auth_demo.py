"""
Demonstrates AgentCore Identity's Outbound Auth: the agent retrieves a stored
API key credential at runtime, without ever hardcoding the secret in code.
"""
import json
import os

import boto3
from bedrock_agentcore.identity import requires_api_key

REGION = "us-west-2"
PROVIDER_NAME = "workshop-weather-api-key-provider"
WORKLOAD_IDENTITY_NAME = "workshop-outbound-auth-identity"

# requires_api_key() below reads AWS_REGION to decide which region to call.
# Force it to match the region we create resources in, in case the shell
# has a different AWS_REGION/AWS_DEFAULT_REGION already set.
os.environ["AWS_REGION"] = REGION


def register_demo_credential() -> None:
    """One-time setup: register a sample API key with Identity, and
    pre-provision the workload identity used to retrieve it.

    We create the workload identity directly against the control plane here,
    instead of letting requires_api_key() create one automatically. Outside
    of AgentCore Runtime, its auto-create path isn't available yet.
    """
    client = boto3.client("bedrock-agentcore-control", region_name=REGION)

    print("1) Registering a sample API key with Identity...")
    try:
        client.create_api_key_credential_provider(name=PROVIDER_NAME, apiKey="demo-secret-456")
    except client.exceptions.ValidationException as e:
        if "already exists" not in str(e):
            raise
        print(f"   Provider '{PROVIDER_NAME}' already exists, reusing it.")

    print("2) Pre-provisioning the workload identity...")
    try:
        client.create_workload_identity(name=WORKLOAD_IDENTITY_NAME, allowedResourceOauth2ReturnUrls=[])
    except (client.exceptions.ConflictException, client.exceptions.ValidationException) as e:
        if "already exists" not in str(e).lower():
            raise
        print(f"   Workload identity '{WORKLOAD_IDENTITY_NAME}' already exists, reusing it.")

    with open(".agentcore.json", "w") as f:
        json.dump(
            {"workload_identity_name": WORKLOAD_IDENTITY_NAME, "user_id": "workshop-user"},
            f,
            indent=2,
        )
    print("Done.")


@requires_api_key(provider_name=PROVIDER_NAME)
def call_weather_api(*, api_key: str) -> None:
    """Stands in for a call to a real external weather API. This function
    never hardcodes the key -- requires_api_key fetches it from Identity's
    Token Vault and injects it here."""
    print(f"Calling the weather API with a key that starts with '{api_key[:4]}...'")
    print("(This is a demo -- no real external API is actually called.)")


if __name__ == "__main__":
    register_demo_credential()
    call_weather_api()
