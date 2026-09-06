import os
import logging
from strands import Agent
from strands.multiagent import Swarm
from strands.models import BedrockModel
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # Disable file_write confirmation prompt

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
    system_prompt="""You are a research agent specializing in information collection and analysis.
    Your role in the Swarm is to provide factual information and research insights on topics.
    Focus on providing accurate data and identifying key aspects of problems.

    Important: After completing research, you must save results to a 'research.md' file using the file_write tool, then hand off work to other agents.
    When creative input or critical analysis is needed, use handoff_to_agent to transfer work to appropriate experts.""",
    tools=[file_write]
)

creative_agent = Agent(
    name="creative_agent",
    model=model,
    system_prompt="""You are a creative agent specializing in generating innovative solutions.
    Your role in the Swarm is to think outside the box and suggest creative approaches.
    Based on information from other agents, you should add your own unique creative perspective.

    Important: After completing creative suggestions, you must save them to a 'creative.md' file using the file_write tool, then hand off work to other agents.
    When research data or critical evaluation is needed, transfer work to appropriate agents.""",
    tools=[file_write]
)

critical_agent = Agent(
    name="critical_agent",
    model=model,
    system_prompt="""You are a critical agent specializing in proposal analysis and problem identification.
    Your role in the Swarm is to evaluate solutions proposed by other agents and identify potential issues.
    You should carefully review proposed solutions and find weaknesses or improvement opportunities.

    Important: After completing analysis, you must save results to a 'critical.md' file using the file_write tool, then hand off work to other agents.
    When additional research or creative alternatives are needed, transfer work to appropriate agents.""",
    tools=[file_write]
)

summarizer_agent = Agent(
    name="summarizer_agent",
    model=model,
    system_prompt="""You are a summarizer agent specializing in synthesizing information from multiple sources.
    Your role in the Swarm is to receive input from other agents and create comprehensive, well-structured summaries.
    You should integrate insights from research, creative, and critical perspectives to create coherent final results.

    Important: After writing summaries, you must save them to a 'summarizer.md' file using the file_write tool.""",
    tools=[file_write]
)

swarm = Swarm(
    [research_agent, creative_agent, critical_agent, summarizer_agent],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15 minutes
    node_timeout=300.0,       # 5 minutes per agent
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3
)

result = swarm("I am planning a program for traveling Seoul, South Korea with the overseas MZ generation. Please create a 3-day travel schedule. Save the final result in a travel_plan.md file.")

print(f"Status: {result.status}")
print(f"Node history: {[node.node_id for node in result.node_history]}")
print(f"Final result: {result.results}")

print(f"Total iterations: {result.execution_count}")
print(f"Execution time: {result.execution_time}ms")
print(f"Token usage: {result.accumulated_usage}")
