import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from strands import Agent
from strands.models import BedrockModel
from strands_tools import shell, file_write

SYSTEM_PROMPT = """You are a self-extending research agent.

You can CREATE new tools by writing Python files to ./tools/. Each file should
define one or more functions decorated with `@tool` from the strands package.
Tools become available instantly after the file is saved.

Template for a new tool:

```python
from strands import tool

@tool
def my_tool(argument: str) -> str:
    \"\"\"Short description of what this tool does.

    Args:
        argument: What this argument means.

    Returns:
        A string result.
    \"\"\"
    return f"result for {argument}"
```

When a user asks for a capability you don't have, CREATE the tool, then USE it.
Be concise in your replies.
"""

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6"
)

agent = Agent(
    model=bedrock_model,
    tools=[shell, file_write],
    load_tools_from_directory=True,   # load/reload ./tools/*.py at runtime
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    user_input = "Create a tool that prints a URL I give you as a QR code, then generate the code for https://strandsagents.com."

    response = agent(user_input)
