from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

aws_docs_mcptool = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx",
                          args=["awslabs.aws-documentation-mcp-server@latest"]
                          )
))
# Add below the existing AWS Documentation MCP
playwright_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx",
                          args=["@playwright/mcp@latest"]
                          )
))


if __name__ == "__main__":
    user_input = "Visit https://aws.amazon.com and take a screenshot"

    agent = Agent(tools=[aws_docs_mcptool, playwright_mcp_client])
    response = agent(user_input) 
