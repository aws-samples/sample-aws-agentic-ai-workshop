"""Traces OTLP Export - Send traces to OpenTelemetry Collector"""
import os
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator

# OTLP endpoint configuration (assuming OTEL Collector is running on localhost)
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

# Telemetry setup
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()      # Send to OTLP endpoint
strands_telemetry.setup_console_exporter()   # Also output to console (for debugging)
strands_telemetry.setup_meter(
    enable_otlp_exporter=True,
    enable_console_exporter=True
)

# Create agent (with custom attributes)
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="You are a helpful AI assistant.",
    tools=[calculator],
    trace_attributes={
        "session.id": "workshop-demo-001",
        "user.id": "workshop-user",
        "tags": ["Agent-SDK", "Workshop", "Observability"]
    }
)

# First question
print("=== First Question ===")
response = agent("Tell me about Mars. What is its atmosphere like?")

# Follow-up question (using tools)
print("\n=== Follow-up Question ===")
response = agent("How long would it take to travel from Earth to Mars at 100,000 km/h?")
