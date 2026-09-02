---
inclusion: always
---
# Strands Agents 개발 규칙

## 작업 디렉토리
코드 산출물은 08-kiro-dev/labs/ 하위에 생성합니다.

## 코드 스타일
- Python 3.11+ 문법 사용
- Type hints 필수 적용
- Docstring은 Google 스타일 사용

## Strands SDK 규칙
- Agent 생성 시 항상 system_prompt 명시
- 도구 함수는 @tool 데코레이터 사용
- 모델은 Amazon Bedrock Claude 모델 사용
- MCP 도구가 제공하는 Strands SDK 문서를 참고하며 정확하게 개발

## 모델 설정
- 기본 모델: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- 리전: `us-west-2`

## 에러 처리
- 모든 에이전트 호출은 try-except로 감싸기
- 로깅은 strands 내장 로거 사용

## OTLP 트레이스 생성
- Strands SDK 의 Otel 확장을 활용하여 OTLP 트레이스를 전송해야 합니다.
- OTLP Receiver 주소(OTEL_EXPORTER_OTLP_ENDPOINT) = "http://localhost:4318"

## 기본 예제
import os
from strands import Agent
from strands.tools import tool
from strands.telemetry import StrandsTelemetry

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "<OTLP Receiver Endpoint>"

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()

@tool
def my_tool(param: str) -> str:
    """도구 설명"""
    return result

agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    name="<adequate name>",
    tools=[my_tool]
)

response = agent("Hello World!")