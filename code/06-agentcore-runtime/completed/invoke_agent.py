import json
import uuid
import boto3

agent_arn = "<<Enter the copied Runtime ARN>>"
prompt = "What is the square root of 80 / 4 * 5?"

client = boto3.client('bedrock-agentcore')

payload = json.dumps({"prompt": prompt}).encode()

response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId=str(uuid.uuid4()),
    payload=payload,
)

content = []
for chunk in response.get("response", []):
    content.append(chunk.decode('utf-8'))

result = json.loads(''.join(content))

print("\n" + "=" * 60)
print("🤖 Agent Response")
print("=" * 60 + "\n")

if 'result' in result and 'content' in result['result']:
    for item in result['result']['content']:
        if 'text' in item:
            print(item['text'])
else:
    print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n" + "=" * 60 + "\n")

# import json
# import uuid
# import boto3
# from urllib.parse import quote

# agent_arn = "<<Enter the copied Runtime ARN>>"
# region = "us-west-2"
# prompt = "Can you research Tokyo, Japan? Also plan a 3-day trip there and recommend products needed for the trip."

# # Generate session ID
# session_id = str(uuid.uuid4())

# # Extract Agent name (from ARN)
# agent_name = agent_arn.split("/")[-1]

# # Construct CloudWatch Logs group name
# log_group_name = f"/aws/bedrock-agentcore/runtimes/{agent_name}-DEFAULT"

# # Generate CloudWatch Logs group URL
# log_group_url = (
#     f"https://console.aws.amazon.com/cloudwatch/home?region={region}"
#     f"#logsV2:log-groups/log-group/{quote(log_group_name, safe='')}"
# )

# client = boto3.client('bedrock-agentcore')
# payload = json.dumps({"prompt": prompt}).encode()

# print(f"\n\nPrompt: {prompt}\n")
# print(f"Session ID: {session_id}\n")
# print("⏳ Invoking agent...\n")
# print(f"📊 CloudWatch Logs (filter by session ID): {log_group_url}\n\n")

# try:
#     response = client.invoke_agent_runtime(
#         agentRuntimeArn=agent_arn,
#         runtimeSessionId=session_id,
#         payload=payload,
#     )

#     # Consume response stream (without printing)
#     for _ in response.get("response", []):
#         pass

#     print("✅ Agent invocation complete\n")
#     print(f"📊 Check logs (Session ID: {session_id}): {log_group_url}\n")
# except Exception as e:
#     print(f"⚠️  Error: {str(e)}\n")
#     print(f"📊 Check logs (Session ID: {session_id}): {log_group_url}\n")