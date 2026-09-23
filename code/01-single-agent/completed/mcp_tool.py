import os

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# Where the screenshot gets saved. Next to this script, so it lands in the same place
# no matter which directory you run the command from.
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts-mcp")

aws_docs_mcptool = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx",
                          args=["awslabs.aws-documentation-mcp-server@latest"]
                          )
))
# Add below the existing AWS Documentation MCP
# The workshop instance is a remote EC2 machine with no display, so the browser runs
# headless. The screenshot is still saved to disk.
playwright_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx",
                          args=["@playwright/mcp@latest",
                                "--headless",
                                "--output-dir", OUTPUT_DIR]
                          )
))


if __name__ == "__main__":
    user_input = (
        f"Visit https://aws.amazon.com and take a screenshot. "
        f"Save it as a file named aws-homepage.png under {OUTPUT_DIR} "
        f"and then tell me the full path of the file you saved."
    )

    agent = Agent(tools=[aws_docs_mcptool, playwright_mcp_client])
    response = agent(user_input)
