from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands_tools import calculator, current_time

app = BedrockAgentCoreApp()

agent = Agent(
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    tools=[calculator, current_time]
)

@app.entrypoint
def invoke(payload):
    """에이전트 호출 엔트리포인트"""
    user_message = payload.get("prompt", "안녕하세요!")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
