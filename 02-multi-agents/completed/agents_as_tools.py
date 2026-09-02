import os
from strands import Agent, tool
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # Disable file_write confirmation prompt

@tool
def research_assistant(query: str) -> str:
    """
    Processes and responds to research-related queries.

    Args:
        query: Research question requiring factual information

    Returns:
        Detailed research answer with citations
    """
    try:
        research_agent = Agent(
            system_prompt="""You are a professional research assistant.
            Focus on providing only factual information with clear sources for research questions.
            Always cite sources whenever possible.""",
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def product_recommendation_assistant(query: str) -> str:
    """
    Handles product recommendation queries by suggesting appropriate products.

    Args:
        query: Product inquiry including user preferences

    Returns:
        Personalized product recommendations with reasoning
    """
    try:
        product_agent = Agent(
            model="us.anthropic.claude-sonnet-4-6",
            system_prompt="""You are a professional product recommendation assistant.
            Provide personalized product suggestions based on user preferences. Always cite sources.""",
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def trip_planning_assistant(query: str) -> str:
    """
    Creates travel itineraries and provides travel advice.

    Args:
        query: Travel planning request including destination and preferences

    Returns:
        Detailed travel itinerary or travel advice
    """
    try:
        travel_agent = Agent(
            model="us.anthropic.claude-sonnet-4-6",
            system_prompt="""You are a professional travel planning assistant.
            Create detailed travel itineraries based on user preferences.""",
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"

if __name__ == "__main__":

    MAIN_SYSTEM_PROMPT = """
    You are an assistant that routes queries to specialized agents:
    - For research questions and factual information → use the research_assistant tool
    - For product recommendations and shopping advice → use the product_recommendation_assistant tool
    - For travel planning and itineraries → use the trip_planning_assistant tool
    - For simple questions that don't require specialized knowledge → answer directly

    Always select the most appropriate tool based on the user's query.
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
    customer_query = "Can you research Spain for me? And I'm planning to travel there with my parents for 7 days, can you help me plan it? Please save the plan you create to a plan.md file."

    response = orchestrator(customer_query)
    