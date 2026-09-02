"""
Strands SDK logging configuration example
- Enable all SDK logs through the root logger
- Adjust log levels per module
"""
import logging
from strands import Agent
from strands_tools import calculator

# 1. Root logger setup - enable all SDK logs
logging.getLogger("strands").setLevel(logging.DEBUG)

# 2. Adjust log level for specific modules (optional)
# logging.getLogger("strands.tools.registry").setLevel(logging.WARNING)  # Hide tool registration logs
# logging.getLogger("strands.models").setLevel(logging.INFO)             # Only INFO and above for model logs

# 3. Configure log output format
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Run the agent
agent = Agent(tools=[calculator])
result = agent("What is 125 * 37?")
