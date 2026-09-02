"""
Traces OTLP 전송 - OpenTelemetry Collector로 트레이스 전송
"""
import os
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator

# OTLP 엔드포인트 설정 (localhost에 OTEL Collector가 실행 중이라고 가정)
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

# 텔레메트리 설정
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()      # OTLP 엔드포인트로 전송
strands_telemetry.setup_console_exporter()   # 콘솔에도 출력 (디버깅용)
strands_telemetry.setup_meter(
    enable_otlp_exporter=True,
    enable_console_exporter=True
)

# 에이전트 생성 (커스텀 속성 포함)
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    tools=[calculator],
    trace_attributes={
        "session.id": "workshop-demo-001",
        "user.id": "workshop-user",
        "tags": ["Agent-SDK", "Workshop", "Observability"]
    }
)

# 첫 번째 질문
print("=== 첫 번째 질문 ===")
response = agent("화성에 대해 알려줘. 대기는 어떤가요?")

# 후속 질문 (도구 사용)
print("=== 후속 질문 ===")
response = agent("지구에서 화성까지 시속 10만 km로 가면 얼마나 걸려?")
