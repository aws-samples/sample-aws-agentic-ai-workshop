"""
Traces 콘솔 출력 - 콘솔에 트레이스 정보 출력
"""
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator

# StrandsTelemetry 인스턴스 생성
strands_telemetry = StrandsTelemetry()

# 콘솔에 트레이스 출력
strands_telemetry.setup_console_exporter()

# 에이전트 생성
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    tools=[calculator]
)

# 에이전트 실행
response = agent("125 * 37은 얼마야?")
