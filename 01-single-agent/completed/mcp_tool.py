from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

aws_docs_mcptool = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx",
                          args=["awslabs.aws-documentation-mcp-server@latest"]
                          )
))
# 기존 AWS Documentation MCP 아래에 추가
playwright_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx",
                          args=["@playwright/mcp@latest"]
                          )
))


if __name__ == "__main__":
    user_input = "https://aws.amazon.com 페이지를 방문해서 스크린샷을 찍어줘"

    agent = Agent(tools=[aws_docs_mcptool, playwright_mcp_client])
    response = agent(user_input) 
