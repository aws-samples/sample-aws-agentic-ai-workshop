from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    additional_request_fields={
        "anthropic_beta": [ "interleaved-thinking-2025-05-14" ],
        "thinking": { "type": "enabled", "budget_tokens": 8000 },
    }
)

agent = Agent(
    model=bedrock_model,
    tools=[calculator]
    )

if __name__ == "__main__":
    user_input = "Amazon Bedrock이 뭐야?"

    response = agent(user_input)
    
    print("\n\n")
    print("=========================================")
    print("=========================================\n")

    last_msg = agent.messages[-1]
    for content in last_msg['content']:
        if 'reasoningContent' in content:
            print("\n ==== REASONING ==== \n")
            print(content['reasoningContent']['reasoningText']['text'])
        elif 'text' in content:
            print("\n ==== RESPONSE ==== \n")
            print(content['text'])
