"""
Cleans up everything created in this chapter.
Order: Gateway Target -> Gateway -> Cognito -> IAM role -> Identity (Outbound Auth demo)
"""
import json
import os
import time

import boto3

CONFIG_FILE = "gateway_config.json"
OUTBOUND_AUTH_REGION = "us-west-2"
OUTBOUND_AUTH_PROVIDER_NAME = "workshop-weather-api-key-provider"
OUTBOUND_AUTH_WORKLOAD_IDENTITY_NAME = "workshop-outbound-auth-identity"


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
        print("Deleting Gateway Target...")
        agentcore.delete_gateway_target(
            gatewayIdentifier=config["gateway_id"], targetId=config["target_id"]
        )
        time.sleep(5)

    if "gateway_id" in config:
        print("Deleting Gateway...")
        agentcore.delete_gateway(gatewayIdentifier=config["gateway_id"])

    print("Deleting Cognito resources (deleting the User Pool also removes the App Client/Resource Server)...")
    cognito.delete_user_pool_domain(Domain=config["domain"], UserPoolId=config["user_pool_id"])
    cognito.delete_user_pool(UserPoolId=config["user_pool_id"])

    print("Deleting IAM role...")
    role_name = config["role_arn"].split("/")[-1]
    try:
        iam.delete_role_policy(RoleName=role_name, PolicyName="agentcore-workshop-gateway-policy")
    except iam.exceptions.NoSuchEntityException:
        pass
    iam.delete_role(RoleName=role_name)


def cleanup_outbound_auth_demo() -> None:
    client = boto3.client("bedrock-agentcore-control", region_name=OUTBOUND_AUTH_REGION)

    print("Deleting Outbound Auth demo credential provider...")
    try:
        client.delete_api_key_credential_provider(name=OUTBOUND_AUTH_PROVIDER_NAME)
    except client.exceptions.ResourceNotFoundException:
        pass

    print("Deleting Outbound Auth demo workload identity...")
    try:
        client.delete_workload_identity(name=OUTBOUND_AUTH_WORKLOAD_IDENTITY_NAME)
    except client.exceptions.ResourceNotFoundException:
        pass

    if os.path.exists(".agentcore.json"):
        os.remove(".agentcore.json")


def main() -> None:
    cleanup_gateway_resources()
    cleanup_outbound_auth_demo()
    print("Cleanup complete")


if __name__ == "__main__":
    main()
