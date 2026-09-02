import os
from strands import Agent, tool
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # file_write 확인 프롬프트 비활성화

@tool
def research_assistant(query: str) -> str:
    """
    연구 관련 쿼리를 처리하고 응답합니다.

    Args:
        query: 사실적 정보가 필요한 연구 질문

    Returns:
        인용이 포함된 상세한 연구 답변
    """
    try:
        research_agent = Agent(
            system_prompt="""당신은 전문 리서치 어시스턴트입니다.
            연구 질문에 대해 사실적이고 출처가 명확한 정보만 제공하는 데 집중하세요.
            가능한 한 항상 출처를 인용하세요.""",
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def product_recommendation_assistant(query: str) -> str:
    """
    적절한 제품을 제안하여 제품 추천 쿼리를 처리합니다.

    Args:
        query: 사용자 선호도가 포함된 제품 문의

    Returns:
        추론이 포함된 개인화된 제품 추천
    """
    try:
        product_agent = Agent(
            model="us.anthropic.claude-sonnet-4-6",
            system_prompt="""당신은 전문 제품 추천 어시스턴트입니다.
            사용자의 선호도를 바탕으로 개인화된 제품 제안을 제공하세요. 항상 출처를 인용하세요.""",
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def trip_planning_assistant(query: str) -> str:
    """
    여행 일정을 작성하고 여행 조언을 제공합니다.

    Args:
        query: 목적지와 선호도가 포함된 여행 계획 요청

    Returns:
        상세한 여행 일정 또는 여행 조언
    """
    try:
        travel_agent = Agent(
            model="us.anthropic.claude-sonnet-4-6",
            system_prompt="""당신은 전문 여행 계획 어시스턴트입니다.
            사용자의 선호도를 바탕으로 상세한 여행 일정을 작성하세요.""",
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"

if __name__ == "__main__":

    MAIN_SYSTEM_PROMPT = """
    당신은 쿼리를 특화된 에이전트로 라우팅하는 보조(Assistant)입니다:
    - 연구 질문 및 사실적 정보를 위해 → research_assistant 도구를 사용하세요
    - 제품 추천 및 쇼핑 조언을 위해 → product_recommendation_assistant 도구를 사용하세요
    - 여행 계획 및 일정을 위해 → trip_planning_assistant 도구를 사용하세요
    - 특화된 지식이 필요하지 않은 간단한 질문을 위해 → 직접 답변하세요

    항상 사용자의 쿼리에 따라 가장 적절한 도구를 선택하세요.
    """

    orchestrator = Agent(
        system_prompt=MAIN_SYSTEM_PROMPT,
        tools=[
            research_assistant,
            product_recommendation_assistant,
            trip_planning_assistant,
            file_write,
        ],
    )

    os.environ["DEV"] = "true"
    customer_query = "스페인 국가에 대해서 리서치 좀 해줄 수 있니? 그리고 부모님과 그곳으로 7일 여행 가려고 하는데 계획 세우는 걸 좀 도와줘. 너가 세운 계획은 plan.md 파일로 저장해줘."

    response = orchestrator(customer_query)
    