import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # file_write/shell 실행 시 y/n 확인 프롬프트 비활성화

from strands import Agent
from strands.models import BedrockModel
from strands_tools import shell, file_write

SYSTEM_PROMPT = """당신은 스스로 확장하는 리서치 에이전트입니다.

당신은 ./tools/ 디렉토리에 Python 파일을 작성하여 새로운 도구를 만들 수 있습니다.
각 파일은 strands 패키지의 `@tool` 데코레이터가 붙은 함수를 하나 이상 정의해야 합니다.
파일을 저장하면 도구가 즉시 사용 가능해집니다.

새 도구 템플릿:

```python
from strands import tool

@tool
def my_tool(argument: str) -> str:
    \"\"\"이 도구가 하는 일에 대한 짧은 설명.

    Args:
        argument: 이 인자가 의미하는 것.

    Returns:
        문자열 결과.
    \"\"\"
    return f"result for {argument}"
```

사용자가 당신이 가지고 있지 않은 기능을 요청하면, 도구를 만들고(CREATE), 그 도구를 사용(USE)하세요.
답변은 간결하게 하세요.
"""

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6"
)

agent = Agent(
    model=bedrock_model,
    tools=[shell, file_write],
    load_tools_from_directory=True,   # ./tools/*.py 를 실시간으로 로드/재로드
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    user_input = "URL을 QR 코드로 출력하는 도구를 만들고, https://strandsagents.com 에 대한 코드를 만들어줘."

    response = agent(user_input)
