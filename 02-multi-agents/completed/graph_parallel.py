from strands import Agent
from strands.multiagent import GraphBuilder

financial_advisor = Agent(name="financial_advisor", system_prompt="당신은 비용 편익 분석, 예산 영향, ROI 계산에 집중하는 재무 고문입니다. 다른 전문가들과 협력하여 포괄적인 재무 관점을 구축하세요.")
technical_architect = Agent(name="technical_architect", system_prompt="당신은 실현 가능성, 구현 과제, 기술적 위험을 평가하는 기술 설계자입니다. 다른 전문가들과 협력하여 기술적 타당성을 확보하세요.")
market_researcher = Agent(name="market_researcher", system_prompt="당신은 시장 상황, 사용자 요구, 경쟁 환경을 분석하는 시장 조사원입니다. 다른 전문가들과 협력하여 시장 기회를 검증하세요.")
risk_analyst = Agent(name="risk_analyst", system_prompt="당신은 잠재적 위험, 완화 전략, 규정 준수 문제를 식별하는 위험 분석가입니다. 다른 전문가들과 협력하여 포괄적인 위험 평가를 보장하세요.")

builder = GraphBuilder()

builder.add_node(financial_advisor, "finance_expert")
builder.add_node(technical_architect, "tech_expert")
builder.add_node(market_researcher, "market_expert")
builder.add_node(risk_analyst, "risk_analyst")

# 병렬 실행 정의
builder.add_edge("finance_expert", "tech_expert")
builder.add_edge("finance_expert", "market_expert")
builder.add_edge("tech_expert", "risk_analyst")
builder.add_edge("market_expert", "risk_analyst")

builder.set_entry_point("finance_expert")

graph = builder.build()

result = graph("우리 회사는 새로운 AI 기반 고객 서비스 플랫폼 출시를 고려하고 있습니다. 초기 투자액은 200만 달러이며 3년 ROI는 150%로 예상됩니다. 이에 대해 재무적 평가를 해주세요.")

print(f"Response: {result}")

for node in result.execution_order:
    print(f"Executed: {node.node_id}")

print(f"Total nodes: {result.total_nodes}")
print(f"Completed nodes: {result.completed_nodes}")
print(f"Execution time: {result.execution_time}ms")

print("Financial Advisor:")
print(result.results["finance_expert"].result)
print("============================================================\n")

print("Technical Expert:")
print(result.results["tech_expert"].result)
print("============================================================\n")

print("Market Researcher:")
print(result.results["market_expert"].result)
print("============================================================\n")
