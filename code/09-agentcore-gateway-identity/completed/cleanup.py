"""
Cleans up everything created in this chapter.
Order: Gateway Target -> Gateway -> Cognito -> IAM role -> Identity (Outbound Auth demo)

Safe to run twice: a resource that is already gone is reported and skipped.
"""
import json
import os
import time

import boto3
from botocore.exceptions import ClientError

CONFIG_FILE = "gateway_config.json"
OUTBOUND_AUTH_REGION = "us-west-2"
OUTBOUND_AUTH_PROVIDER_NAME = "workshop-weather-api-key-provider"
OUTBOUND_AUTH_WORKLOAD_IDENTITY_NAME = "workshop-outbound-auth-identity"

# Error codes the AWS APIs below return when the resource is already deleted.
ALREADY_GONE = ("ResourceNotFoundException", "NoSuchEntity", "NotFoundException")


def delete_quietly(label: str, delete_fn) -> None:
    """Runs one delete call, treating an already-deleted resource as success."""
    print(f"Deleting {label}...")
    try:
        delete_fn()
    except ClientError as e:
        if e.response["Error"]["Code"] in ALREADY_GONE:
            print("   Already gone, skipping.")
            return
        raise


def cleanup_gateway_resources() -> None:
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} not found, skipping Gateway/Cognito/IAM cleanup.")
        return

    with open(CONFIG_FILE) as f:
        config = json.load(f)

    agentcore = boto3.client("bedrock-agentcore-control", region_name=config["region"])
    cognito = boto3.client("cognito-idp", region_name=config["region"])
    iam = boto3.client("iam", region_name=config["region"])

    if "target_id" in config:
        delete_quietly("Gateway Target", lambda: agentcore.delete_gateway_target(
            gatewayIdentifier=config["gateway_id"], targetId=config["target_id"]
        ))
        time.sleep(5)

    if "gateway_id" in config:
        delete_quietly("Gateway", lambda: agentcore.delete_gateway(
            gatewayIdentifier=config["gateway_id"]
        ))

    print("Deleting Cognito resources (deleting the User Pool also removes the App Client/Resource Server)...")
    delete_quietly("Cognito domain", lambda: cognito.delete_user_pool_domain(
        Domain=config["domain"], UserPoolId=config["user_pool_id"]
    ))
    delete_quietly("Cognito User Pool", lambda: cognito.delete_user_pool(
        UserPoolId=config["user_pool_id"]
    ))

    role_name = config["role_arn"].split("/")[-1]
    delete_quietly("IAM role policy", lambda: iam.delete_role_policy(
        RoleName=role_name, PolicyName="agentcore-workshop-gateway-policy"
    ))
    delete_quietly("IAM role", lambda: iam.delete_role(RoleName=role_name))

    # The config now points at deleted resources, so drop it.
    os.remove(CONFIG_FILE)


def cleanup_outbound_auth_demo() -> None:
    client = boto3.client("bedrock-agentcore-control", region_name=OUTBOUND_AUTH_REGION)

    delete_quietly("Outbound Auth demo credential provider",
                   lambda: client.delete_api_key_credential_provider(
                       name=OUTBOUND_AUTH_PROVIDER_NAME))

    delete_quietly("Outbound Auth demo workload identity",
                   lambda: client.delete_workload_identity(
                       name=OUTBOUND_AUTH_WORKLOAD_IDENTITY_NAME))

    if os.path.exists(".agentcore.json"):
        os.remove(".agentcore.json")


def main() -> None:
    cleanup_gateway_resources()
    cleanup_outbound_auth_demo()
    print("Cleanup complete")


if __name__ == "__main__":
    main()
