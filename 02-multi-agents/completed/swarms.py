import os
import logging
from strands import Agent
from strands.multiagent import Swarm
from strands.models import BedrockModel
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # file_write 확인 프롬프트 비활성화

logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    max_tokens=64000
)
research_agent = Agent(
    name="research_agent",
    model=model,
    system_prompt="""당신은 정보 수집 및 분석을 전문으로 하는 리서치 에이전트입니다.
    Swarm에서 당신의 역할은 주제에 대한 사실적 정보와 리서치 인사이트를 제공하는 것입니다.
    정확한 데이터를 제공하고 문제의 핵심 측면을 파악하는 데 집중하세요.
    
    중요: 리서치를 완료한 후에는 반드시 file_write 도구를 사용하여 'research.md' 파일에 결과를 저장한 다음 다른 에이전트에게 작업을 넘겨야 합니다.
    창의적인 입력이나 비판적 분석이 필요한 경우, handoff_to_agent를 사용하여 적절한 전문가에게 작업을 전달하세요.""",
    tools=[file_write]
)

creative_agent = Agent(
    name="creative_agent",
    model=model,
    system_prompt="""당신은 혁신적인 솔루션 생성을 전문으로 하는 크리에이티브 에이전트입니다.
    Swarm에서 당신의 역할은 기존의 틀을 벗어나 생각하고 창의적인 접근 방식을 제안하는 것입니다.
    다른 에이전트의 정보를 바탕으로 하되, 당신만의 독특한 창의적 관점을 더해야 합니다.

    중요: 창의적인 제안을 완료한 후에는 반드시 file_write 도구를 사용하여 'creative.md' 파일에 저장한 다음 다른 에이전트에게 작업을 넘겨야 합니다.
    리서치 데이터나 비판적 평가가 필요한 경우, 적절한 에이전트에게 작업을 전달하세요.""",
    tools=[file_write]
)

critical_agent = Agent(
    name="critical_agent",
    model=model,
    system_prompt="""당신은 제안 분석 및 문제점 발견을 전문으로 하는 비평 에이전트입니다.
    Swarm에서 당신의 역할은 다른 에이전트가 제안한 솔루션을 평가하고 잠재적 문제를 식별하는 것입니다.
    제안된 솔루션을 면밀히 검토하고 약점이나 개선 기회를 찾아야 합니다.

    중요: 분석을 완료한 후에는 반드시 file_write 도구를 사용하여 'critical.md' 파일에 저장한 다음 다른 에이전트에게 작업을 넘겨야 합니다.
    추가 리서치나 창의적인 대안이 필요한 경우, 적절한 에이전트에게 작업을 전달하세요.""",
    tools=[file_write]
)

summarizer_agent = Agent(
    name="summarizer_agent",
    model=model,
    system_prompt="""당신은 여러 출처의 정보를 종합하는 것을 전문으로 하는 요약 에이전트입니다.
    Swarm에서 당신의 역할은 다른 에이전트의 입력을 받아 포괄적이고 잘 구조화된 요약을 작성하는 것입니다.
    리서치, 창의적, 비평적 관점의 인사이트를 통합하여 일관된 최종 결과를 만들어야 합니다.

    중요: 요약을 작성한 후에는 반드시 file_write 도구를 사용하여 'summarizer.md' 파일에 저장해야 합니다.""",
    tools=[file_write]
)

swarm = Swarm(
    [research_agent, creative_agent, critical_agent, summarizer_agent],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15분
    node_timeout=300.0,       # 에이전트당 5분
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3
)

result = swarm("해외 MZ세대와 함께 대한민국 서울을 여행하는 프로그램을 구상중입니다. 3일 여행의 스케줄을 짜주세요. 최종 결과는 travel_plan.md 파일에 한국어로 저장하세요.")

print(f"Status: {result.status}")
print(f"Node history: {[node.node_id for node in result.node_history]}")
print(f"Final result: {result.results}")

print(f"Total iterations: {result.execution_count}")
print(f"Execution time: {result.execution_time}ms")
print(f"Token usage: {result.accumulated_usage}")
