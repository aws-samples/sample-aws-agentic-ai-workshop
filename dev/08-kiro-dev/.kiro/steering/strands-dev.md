---
inclusion: always
---
# Strands Agents development rules

## Working directory
Create code artifacts under 08-kiro-dev/labs/.

## Code style
- Use Python 3.11+ syntax
- Type hints are mandatory
- Use Google style for docstrings

## Strands SDK rules
- Always specify system_prompt when creating an Agent
- Use the @tool decorator for tool functions
- Use Amazon Bedrock Claude models
- Develop accurately by referencing the Strands SDK documentation provided by MCP tools

## Model configuration
- Default model: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- Region: `us-west-2`

## Error handling
- Wrap all agent calls with try-except
- Use the strands built-in logger for logging

## OTLP trace generation
- Use the Strands SDK Otel extension to send OTLP traces.
- OTLP Receiver address (OTEL_EXPORTER_OTLP_ENDPOINT) = "http://localhost:4318"

## Basic example
import os
from strands import Agent
from strands.tools import tool
from strands.telemetry import StrandsTelemetry

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "<OTLP Receiver Endpoint>"

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return result

agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="You are a helpful AI assistant.",
    name="<adequate name>",
    tools=[my_tool]
)

response = agent("Hello World!")
