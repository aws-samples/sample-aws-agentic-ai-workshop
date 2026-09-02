import json
import uuid
import boto3

agent_arn = "<<복사해둔 Runtime ARN을 입력하세요>>"
prompt = "80 / 4 * 5 의 제곱근은?"

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

# agent_arn = "<<복사해둔 Runtime ARN을 입력하세요>>"
# region = "us-west-2"
# prompt = "일본 도쿄에 대해서 리서치 좀 해줄 수 있니? 그리고 거기로 3일 여행 계획도 세워줘. 여행에 필요한 제품도 추천해줘."

# # 세션 ID 생성
# session_id = str(uuid.uuid4())

# # Agent 이름 추출 (ARN에서)
# agent_name = agent_arn.split("/")[-1]

# # CloudWatch Logs 그룹 이름 구성
# log_group_name = f"/aws/bedrock-agentcore/runtimes/{agent_name}-DEFAULT"

# # CloudWatch Logs 그룹 URL 생성
# log_group_url = (
#     f"https://console.aws.amazon.com/cloudwatch/home?region={region}"
#     f"#logsV2:log-groups/log-group/{quote(log_group_name, safe='')}"
# )

# client = boto3.client('bedrock-agentcore')
# payload = json.dumps({"prompt": prompt}).encode()

# print(f"\n\n프롬프트: {prompt}\n")
# print(f"세션 ID: {session_id}\n")
# print("⏳ 에이전트 호출 중...\n")
# print(f"📊 CloudWatch Logs (세션 ID로 필터링하세요): {log_group_url}\n\n")

# try:
#     response = client.invoke_agent_runtime(
#         agentRuntimeArn=agent_arn,
#         runtimeSessionId=session_id,
#         payload=payload,
#     )

#     # 응답 스트림 소비 (출력하지 않음)
#     for _ in response.get("response", []):
#         pass

#     print("✅ 에이전트 호출 완료\n")
#     print(f"📊 로그 확인 (세션 ID: {session_id}): {log_group_url}\n")
# except Exception as e:
#     print(f"⚠️  에러: {str(e)}\n")
#     print(f"📊 로그 확인 (세션 ID: {session_id}): {log_group_url}\n")