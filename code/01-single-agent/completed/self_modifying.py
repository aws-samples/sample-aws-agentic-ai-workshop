import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from pathlib import Path
from strands import Agent
from strands.models import BedrockModel
from tools.system_prompt import system_prompt

PROMPT_FILE = Path(".prompt")


def build_system_prompt() -> str:
    """Reassemble the system prompt from multiple sources every turn."""
    base = (
        "You are a self-improving research agent.\n"
        "You can MODIFY YOUR OWN SYSTEM PROMPT using the system_prompt tool.\n"
        "Actions: view, update, add_context, reset.\n"
        "When a user asks you to change your behavior 'from now on' or "
        "'permanently', call system_prompt(action='update', prompt=...)."
    )
    persisted = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
    parts = [base]
    if persisted:
        parts.append(f"\n## Persisted instructions (.prompt):\n{persisted}")
    return "\n".join(parts)


bedrock_model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

if __name__ == "__main__":
    print("🦆 Self-modifying agent. Type 'exit' to quit.\n")
    while True:
        q = input("🦆 ").strip()
        if q.lower() in ("exit", "quit", "q", ""):
            break

        # Rebuild the agent each turn so prompt updates apply right away
        agent = Agent(
            model=bedrock_model,
            tools=[system_prompt],
            system_prompt=build_system_prompt(),
        )
        agent(q)
