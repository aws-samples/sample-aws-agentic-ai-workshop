from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

boto_session = Session()
region = boto_session.region_name

agentcore_runtime = Runtime()

response = agentcore_runtime.configure(
    entrypoint="my_agent.py", # or "my_agent_advanced.py"
    agent_name="strands_workshop_agent", # or "strands_workshop_agent_advanced"
    requirements_file="requirements.txt",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    region="us-west-2",
)

print("🚀 배포 시작...")
launch_result = agentcore_runtime.launch()
print(launch_result)
