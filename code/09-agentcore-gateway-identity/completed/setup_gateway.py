"""
Sets up everything needed for the Gateway in one run:
1. A Cognito User Pool for Inbound Auth (who can call the Gateway)
2. An IAM role the Gateway uses
3. The Gateway itself (Inbound Auth: Cognito JWT)
4. An OpenAPI Target exposing the public Petstore API as MCP tools

Run this once. Everything is saved to gateway_config.json for the other
scripts (gateway_agent.py, cleanup.py) to reuse.
"""
import json
import secrets
import string
import time

import boto3
import requests

REGION = "us-west-2"
POOL_NAME = "agentcore-workshop-gateway-pool"
RESOURCE_SERVER_ID = "gateway"
SCOPE_NAME = "invoke"
APP_CLIENT_NAME = "agentcore-workshop-gateway-client"
ROLE_NAME = "agentcore-workshop-gateway-role"
GATEWAY_NAME = "petstore-gateway"
TARGET_NAME = "petstore-target"
PETSTORE_OPENAPI_URL = "https://petstore3.swagger.io/api/v3/openapi.json"
CONFIG_FILE = "gateway_config.json"


def random_suffix(n: int = 6) -> str:
    return "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def setup_cognito() -> dict:
    print("1) Setting up Cognito (User Pool, Resource Server, App Client, domain)...")
    cognito = boto3.client("cognito-idp", region_name=REGION)

    # Re-running this script should not pile up duplicate pools: reuse one if it exists.
    existing = [p for p in cognito.list_user_pools(MaxResults=60)["UserPools"] if p["Name"] == POOL_NAME]
    for pool in existing:  # start clean so the client secret below is fresh
        old_domain = cognito.describe_user_pool(UserPoolId=pool["Id"])["UserPool"].get("Domain")
        if old_domain:
            cognito.delete_user_pool_domain(Domain=old_domain, UserPoolId=pool["Id"])
        cognito.delete_user_pool(UserPoolId=pool["Id"])
    user_pool_id = cognito.create_user_pool(PoolName=POOL_NAME)["UserPool"]["Id"]

    cognito.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier=RESOURCE_SERVER_ID,
        Name="AgentCore Gateway Resource Server",
        Scopes=[{"ScopeName": SCOPE_NAME, "ScopeDescription": "Invoke gateway tools"}],
    )
    full_scope = f"{RESOURCE_SERVER_ID}/{SCOPE_NAME}"

    app_client = cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=APP_CLIENT_NAME,
        GenerateSecret=True,
        AllowedOAuthFlows=["client_credentials"],
        AllowedOAuthScopes=[full_scope],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=["COGNITO"],
    )

    domain = f"agentcore-ws-{random_suffix()}"
    cognito.create_user_pool_domain(Domain=domain, UserPoolId=user_pool_id)

    return {
        "user_pool_id": user_pool_id,
        "client_id": app_client["UserPoolClient"]["ClientId"],
        "client_secret": app_client["UserPoolClient"]["ClientSecret"],
        "domain": domain,
        "discovery_url": (
            f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}"
            "/.well-known/openid-configuration"
        ),
        "token_endpoint": f"https://{domain}.auth.{REGION}.amazoncognito.com/oauth2/token",
        "scope": full_scope,
    }


def setup_gateway_role() -> str:
    print("2) Creating the IAM role the Gateway will use...")
    iam = boto3.client("iam", region_name=REGION)
    account_id = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {"StringEquals": {"aws:SourceAccount": account_id}},
        }],
    }
    # Minimal permissions for this workshop. Scope resources down further for production use.
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:*",
                "secretsmanager:GetSecretValue",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
            ],
            "Resource": "*",
        }],
    }

    try:
        role_arn = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="AgentCore Gateway workshop execution role",
        )["Role"]["Arn"]
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = iam.get_role(RoleName=ROLE_NAME)["Role"]["Arn"]

    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="agentcore-workshop-gateway-policy",
        PolicyDocument=json.dumps(permissions_policy),
    )
    time.sleep(10)  # let the new role propagate
    return role_arn


def wait_until(describe_fn) -> dict:
    """Polls describe_fn() until its 'status' field is READY (or raises on failure)."""
    while True:
        resp = describe_fn()
        status = resp["status"]
        if status == "READY":
            return resp
        if status in ("FAILED", "UPDATE_UNSUCCESSFUL", "SYNCHRONIZE_UNSUCCESSFUL"):
            raise RuntimeError(f"Failed with status {status}: {resp.get('statusReasons')}")
        time.sleep(5)


def setup_gateway_and_target(cognito_info: dict, role_arn: str) -> dict:
    client = boto3.client("bedrock-agentcore-control", region_name=REGION)

    print("3) Creating the Gateway (Inbound Auth: Cognito JWT) and waiting for it to be READY...")
    authorizer = {
        "customJWTAuthorizer": {
            "discoveryUrl": cognito_info["discovery_url"],
            "allowedClients": [cognito_info["client_id"]],
        }
    }
    try:
        gateway_id = client.create_gateway(
            name=GATEWAY_NAME,
            roleArn=role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration=authorizer,
            description="Workshop: Gateway exposing the Petstore OpenAPI as MCP tools",
        )["gatewayId"]
    except client.exceptions.ConflictException:
        # Left over from an earlier run: reuse it, but point it at the Cognito pool we just made.
        gateway_id = next(g["gatewayId"] for g in client.list_gateways()["items"] if g["name"] == GATEWAY_NAME)
        print(f"   Gateway '{GATEWAY_NAME}' already exists ({gateway_id}), reusing it.")
        wait_until(lambda: client.get_gateway(gatewayIdentifier=gateway_id))
        client.update_gateway(
            gatewayIdentifier=gateway_id,
            name=GATEWAY_NAME,
            roleArn=role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration=authorizer,
        )
    gateway_url = wait_until(lambda: client.get_gateway(gatewayIdentifier=gateway_id))["gatewayUrl"]

    print("4) Registering the Petstore OpenAPI as a Target and waiting for it to be READY...")
    # The public spec needs two fixes: servers must be an absolute HTTPS URL
    # (the original is relative, "/api/v3"), and the Gateway's OpenAPI
    # importer doesn't support the uploadImage operation's
    # application/octet-stream request body.
    spec = requests.get(PETSTORE_OPENAPI_URL, timeout=30).json()
    spec["servers"] = [{"url": "https://petstore3.swagger.io/api/v3"}]
    spec["paths"].pop("/pet/{petId}/uploadImage", None)

    try:
        target_id = client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=TARGET_NAME,
            # Petstore needs no auth, so credentialProviderConfigurations is
            # omitted entirely. (GATEWAY_IAM_ROLE is for AWS services the
            # Gateway SigV4-signs requests to, not public APIs like this one.)
            targetConfiguration={"mcp": {"openApiSchema": {"inlinePayload": json.dumps(spec)}}},
            description="Public Swagger Petstore API",
        )["targetId"]
    except client.exceptions.ConflictException:
        target_id = next(
            tg["targetId"]
            for tg in client.list_gateway_targets(gatewayIdentifier=gateway_id)["items"]
            if tg["name"] == TARGET_NAME
        )
        print(f"   Target '{TARGET_NAME}' already exists ({target_id}), reusing it.")
    wait_until(lambda: client.get_gateway_target(gatewayIdentifier=gateway_id, targetId=target_id))

    return {"gateway_id": gateway_id, "gateway_url": gateway_url, "target_id": target_id}


if __name__ == "__main__":
    cognito_info = setup_cognito()
    role_arn = setup_gateway_role()
    gateway_info = setup_gateway_and_target(cognito_info, role_arn)

    config = {**cognito_info, "role_arn": role_arn, "region": REGION, **gateway_info}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nDone! Gateway URL: {config['gateway_url']}")
