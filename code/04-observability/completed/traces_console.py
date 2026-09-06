"""Traces Console Output - Print trace information to the console"""
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator

# Create a StrandsTelemetry instance
strands_telemetry = StrandsTelemetry()

# Output traces to console
strands_telemetry.setup_console_exporter()

# Create agent
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="You are a helpful AI assistant.",
    tools=[calculator]
)

# Run the agent
response = agent("What is 125 * 37?")
