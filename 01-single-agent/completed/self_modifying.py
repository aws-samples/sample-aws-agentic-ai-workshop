import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # 도구 실행 시 y/n 확인 프롬프트 비활성화

from pathlib import Path
from strands import Agent
from strands.models import BedrockModel
from tools.system_prompt import system_prompt

PROMPT_FILE = Path(".prompt")


def build_system_prompt() -> str:
    """매 턴, 여러 소스에서 시스템 프롬프트를 다시 조립합니다."""
    base = (
        "당신은 스스로 개선하는 리서치 에이전트입니다.\n"
        "당신은 system_prompt 도구를 사용해 자신의 시스템 프롬프트를 수정할 수 있습니다.\n"
        "가능한 action: view, update, add_context, reset.\n"
        "사용자가 당신의 행동을 '앞으로' 또는 '영구적으로' 바꿔달라고 하면, "
        "system_prompt(action='update', prompt=...)를 호출하세요."
    )
    persisted = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
    parts = [base]
    if persisted:
        parts.append(f"\n## 저장된 지침 (.prompt):\n{persisted}")
    return "\n".join(parts)


bedrock_model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

if __name__ == "__main__":
    print("🦆 자가수정 에이전트입니다. 'exit'을 입력하면 종료합니다.\n")
    while True:
        q = input("🦆 ").strip()
        if q.lower() in ("exit", "quit", "q", ""):
            break

        # 매 턴 에이전트를 새로 만들어 프롬프트 수정이 곧바로 적용되게 함
        agent = Agent(
            model=bedrock_model,
            tools=[system_prompt],
            system_prompt=build_system_prompt(),
        )
        agent(q)
