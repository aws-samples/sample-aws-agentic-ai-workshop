from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands_tools import calculator, current_time

app = BedrockAgentCoreApp()

agent = Agent(
    system_prompt="You are a helpful AI assistant.",
    tools=[calculator, current_time]
)

@app.entrypoint
def invoke(payload):
    """Agent invocation entrypoint"""
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
