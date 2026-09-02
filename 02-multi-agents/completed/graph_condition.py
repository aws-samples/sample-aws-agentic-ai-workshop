import os, argparse
from strands import Agent
from strands.multiagent import GraphBuilder
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # file_write 확인 프롬프트 비활성화

classifier = Agent(
    name="classifier", 
    system_prompt="당신은 보고서 요청을 분류하는 에이전트입니다. Technical 또는 Business 분류만 반환하세요."
    )

technical_report = Agent(
    name="technical_expert", 
    system_prompt="당신은 기술적 관점에서 보고서를 작성하는 기술 전문가입니다. 보고서는 technical_report.md 로 저장합니다.",
    tools=[file_write]
    )
    
business_report = Agent(
    name="business_expert", 
    system_prompt="당신은  비즈니스 관점에서 보고서를 작성하는 비즈니스 전문가입니다. 보고서는 business_report.md 로 저장합니다.",
    tools=[file_write]
    )

def is_technical(state):
    classifier_result = state.results.get("classifier")
    if not classifier_result:
        return False
    result_text = str(classifier_result.result)
    return "technical" in result_text.lower()

def is_business(state):
    classifier_result = state.results.get("classifier")
    if not classifier_result:
        return False
    result_text = str(classifier_result.result)
    return "business" in result_text.lower()

builder = GraphBuilder()

builder.add_node(classifier, "classifier")
builder.add_node(technical_report, "technical_report")
builder.add_node(business_report, "business_report")

# 조건부 엣지 추가
builder.add_edge("classifier", "technical_report", condition=is_technical)
builder.add_edge("classifier", "business_report", condition=is_business)

builder.set_entry_point("classifier")

graph = builder.build()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        type=str,
        default="재택근무가 비즈니스에 미치는 영향에 대한 보고서를 작성해주세요. 고려해야 할 사항과 주요 위험 요소를 요약하세요"
    )

    args = parser.parse_args()
    prompt = args.query

    print(f"Input Prompt: {prompt}")
    print("\n============================================================")

    result = graph(prompt)

    print(f"Response: {result}")

    for node in result.execution_order:
        print(f"Executed: {node.node_id}")

    print("\n============================================================")
    print("Classifier:")
    print(result.results["classifier"].result)

    print(f"Total nodes: {result.total_nodes}")
    print(f"Completed nodes: {result.completed_nodes}")
    print(f"Failed nodes: {result.failed_nodes}")
    print(f"Execution time: {result.execution_time}ms")
    print(f"Token usage: {result.accumulated_usage}")
    print("\n============================================================\n")
