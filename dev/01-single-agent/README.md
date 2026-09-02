# 1. Building a Basic Single Agent

[한국어](README.ko.md) | English

In this chapter, we will learn how to create a basic agent by working with the core components of the Strands SDK: Prompt, Model, and Tools.

![Strands SDK components](../../docs/images/c1-strands-diagram.png)

The agent we build first has 1) mathematical calculation, 2) time checking, and 3) Python code execution capabilities. From there we add a Bedrock Knowledge Base for document search, connect external MCP servers, and finally build an agent that writes its own tools and rewrites its own system prompt.

> [!NOTE]
> **Prerequisites**
> - Environment set up per [00-setup](../00-setup/README.md), with the uv environment available from the repo root
> - Amazon Bedrock model access enabled in **us-west-2** for:
>   - `us.anthropic.claude-sonnet-4-20250514-v1:0` (used in `models.py`)
>   - `us.anthropic.claude-sonnet-4-6` (used in `self_extending.py`, `self_modifying.py`)
>   - `amazon.titan-embed-text-v2:0` (Titan Text Embeddings V2, used by the Knowledge Base)
> - An AWS identity with permission to create an S3 bucket, a Bedrock Knowledge Base, and an OpenSearch Serverless collection (section 2)
> - Node.js / `npx` available if you want to run the Playwright MCP part of section 3

**What you will learn**

- Creating an agent with built-in tools from `strands_tools`
- Configuring `BedrockModel` and enabling Extended Thinking (reasoning)
- Writing custom tools two ways: the `@tool` decorator and a `TOOL_SPEC` tool module
- Creating an Amazon Bedrock Knowledge Base and querying it with the `retrieve` tool (RAG)
- Connecting MCP servers (AWS Documentation MCP, Playwright MCP) as agent tools
- Two self-improving patterns: an agent that writes its own tools, and an agent that rewrites its own system prompt

**Estimated time:** ~30 minutes for sections 1 and 3 (section 2 adds ~30 minutes of console work; section 4 is optional)

## How the labs work

Each lab file exists twice:

- `labs/<file>.py` is **empty**. You type the code into it, step by step.
- `completed/<file>.py` holds the **reference answer**. Open it if you get stuck or want to compare.

![labs and completed folders](../../docs/images/c1-labs.png)

All commands below assume you are at the **repo root** with the uv environment from [00-setup](../00-setup/README.md) in place.

## Files in this chapter

| File | Purpose |
|---|---|
| `labs/basic.py` | (empty) you write this: the most basic agent |
| `labs/models.py` | (empty) you write this: `BedrockModel` + Extended Thinking |
| `labs/custom_tool1.py` | (empty) you write this: custom tool with `@tool` |
| `labs/custom_tool2.py` | (empty) you write this: importing local `TOOL_SPEC` tools |
| `labs/knowledge_base.py` | (empty) you write this: RAG agent using `retrieve` |
| `labs/mcp_tool.py` | (empty) you write this: MCP server integration |
| `labs/self_extending.py` | (empty) you write this: agent that writes its own tools |
| `labs/self_modifying.py` | (empty) you write this: agent that rewrites its own prompt |
| `labs/tools/bash_tool.py` | prefilled helper: `TOOL_SPEC` tool that runs bash commands |
| `labs/tools/python_repl_tool.py` | prefilled helper: `TOOL_SPEC` tool that runs Python code |
| `labs/tools/decorators.py` | prefilled helper: `log_io` logging decorator used by the two tools above |
| `labs/tools/system_prompt.py` | (empty) you write this in section 4; the agent then rewrites its own `.prompt` file through it |
| `completed/*.py` | reference answers for every file above |
| `completed/tools/*.py` | reference answers, including a filled-in `system_prompt.py` |

> [!NOTE]
> The Streamlit chatbot UI that used to live in this chapter has moved. See [../03-chatbot-app/README.md](../03-chatbot-app/README.md).

---

## 1. Building a Basic Agent

In this section, we will practice the core features of the Strands SDK step by step, from creating the most basic agent to model configuration, custom tool development, and local tool modules.

### 1. Creating the Most Basic Agent

As the first step, let's create the simplest form of agent. The agent we're about to create has 1) **mathematical calculation functionality**, 2) **time checking functionality**, and 3) **Python code execution functionality**, so when users ask questions in natural language, it not only provides answers but also **selects and performs appropriate actions** among these functions.

Let's follow the guide below to create a basic agent directly.

**1-1.** Open the `01-single-agent/labs/basic.py` file.

**1-2.** Import the necessary libraries.
- `Agent` is the core class of the Strands SDK, and `strands_tools` is a collection of ready-to-use built-in tools.
- More tools can be found at https://github.com/strands-agents/tools.

```py
from strands import Agent
from strands_tools import calculator, current_time, python_repl

```

**1-3.** Create an agent.

Create an agent by passing a list of tools to use to the `Agent()` constructor. The agent will analyze user questions and automatically select and execute the appropriate tool from these tools.

```py
agent = Agent(tools=[calculator, current_time, python_repl])

```

**1-4.** Ask the agent a question and receive a response.

```py
response = agent("What is the square root of 80 / 4 * 5?") # prompt

```

Pass a calculation question to the agent defined above. The agent will automatically select and use the most appropriate tool among its available tools, which is the `calculator` tool.

**1-5.** Open the terminal and run the following command to check the result:

```bash
uv run python 01-single-agent/labs/basic.py
```

You can confirm that the agent automatically selects the `calculator` tool to calculate the square root of 80/4*5 and returns an answer containing the result **10**.

![calculator result](../../docs/images/c1-calculator.png)

<details>
<summary>Getting an error? (⚠️ How to fix a model access error)</summary>

`basic.py` passes no `model` argument, so Strands falls back to its default Bedrock model. Whether that default is callable depends on the account: model access for it may not be enabled in `us-west-2`, or the account may not be able to use that inference profile. The error appears when `agent(...)` runs, not at import time. It usually shows up as `AccessDeniedException` or `ValidationException`.

You do not need to restructure the lab. Add a `model` argument with an ID you do have access to:

```py
from strands import Agent
from strands_tools import calculator, current_time, python_repl

agent = Agent(
    model="us.anthropic.claude-sonnet-4-6",   # 👈 specify the model directly
    tools=[calculator, current_time, python_repl],
)
response = agent("What is the square root of 80 / 4 * 5?") # prompt
```

To see which IDs this account can actually call, list them and pick one:

```bash
aws bedrock list-inference-profiles --region us-west-2 \
  --query "inferenceProfileSummaries[].inferenceProfileId"
```

The same applies to `custom_tool1.py`, `custom_tool2.py`, `knowledge_base.py`, and `mcp_tool.py`, which also leave the model unset. Section 2 below introduces `BedrockModel`, the fuller form of this setting, and [Troubleshooting](#troubleshooting) covers the other Bedrock errors in this chapter.

</details>

<details>
<summary>Check Complete Code</summary>

The complete code for `basic.py` written so far is as follows. You can find the same content by opening the `01-single-agent/completed/basic.py` file:

```py
from strands import Agent
from strands_tools import calculator, current_time, python_repl # Reference: https://github.com/strands-agents/tools

agent = Agent(
    tools=[calculator, current_time, python_repl],
    system_prompt="Answer as if you are explaining to an elementary school student"
    )
response = agent("What is the square root of 80 / 4 * 5?") # prompt

# No model is set above, so Strands uses its default Bedrock model. If the run fails with
# AccessDeniedException or ValidationException, that default is not callable from your
# account. Specify the model directly instead:
#
# from strands import Agent
# from strands_tools import calculator, current_time, python_repl
#
# agent = Agent(
#     model="us.anthropic.claude-sonnet-4-6",   # 👈 specify the model directly
#     tools=[calculator, current_time, python_repl],
# )
# response = agent("What is the square root of 80 / 4 * 5?") # prompt
```

</details>

---

### 2. Model Configuration and Reasoning Functionality

Strands uses the Claude model by default, but you can change to other models or enable advanced features. Let's learn how to use the Claude model through Amazon Bedrock and enable the **Extended Thinking** feature.

**2-1.** Open the `01-single-agent/labs/models.py` file.

**2-2.** Import the necessary libraries.

```py
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator

```

**2-3.** Configure BedrockModel.
- `BedrockModel` allows you to use multiple LLM models through [Amazon Bedrock](https://aws.amazon.com/bedrock/) with the same interface and fine-tune settings.
- Specify the model as **Claude Sonnet 4** and enable the Extended Thinking feature. `interleaved-thinking` is an advanced reasoning mode that alternates between thinking and action during tool usage, making the agent think about why a tool is needed before using it. For more details, please refer to the [Claude Extended Thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) documentation.

```py
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    additional_request_fields={
        "anthropic_beta": [ "interleaved-thinking-2025-05-14" ],
        "thinking": { "type": "enabled", "budget_tokens": 8000 },
    }
)

```

**2-4.** Write code to create an agent.

```py
agent = Agent(
    model=bedrock_model,
    tools=[calculator]
    )

```

**2-5.** Execute the agent.

```py
if __name__ == "__main__":
    user_input = "What is Amazon Bedrock?"

    response = agent(user_input)

```

**2-6.** Run the following command in the terminal to check the result.

```bash
uv run python 01-single-agent/labs/models.py
```

![BedrockModel result](../../docs/images/c1-bedrockmodel.png)

**2-7.** ***(Optional)*** To output the agent's reasoning content and final response separately, add the following code at the bottom of models.py.

```py
    print("\n\n")
    print("=========================================")
    print("=========================================\n")

    last_msg = agent.messages[-1]
    for content in last_msg['content']:
        if 'reasoningContent' in content:
            print("\n ==== REASONING ==== \n")
            print(content['reasoningContent']['reasoningText']['text'])
        elif 'text' in content:
            print("\n ==== RESPONSE ==== \n")
            print(content['text'])

```

**2-8.** ***(Optional)*** Run the following command in the terminal again to check the result. You can confirm that Reasoning and Response are output separately.

```bash
uv run python 01-single-agent/labs/models.py
```

![reasoning and response separated](../../docs/images/c1-reasoning.png)

---

### 3. Connecting Custom Tools (1): Defining Tools Directly with the `@tool` Decorator

In addition to built-in tools, you can create your own tools and connect them to the agent. Simply write a Python function and add the `@tool` decorator.

In this workshop, we will implement a simple weather information tool and attach it to the agent, then test whether the agent calls the appropriate tool.

**3-1.** Open the `01-single-agent/labs/custom_tool1.py` file.

**3-2.** Import the necessary libraries.

```py
from strands import Agent, tool
from strands_tools import calculator
import random

```

**3-3.** Write a custom tool function.

- This function randomly selects weather from multiple options and provides it to the user.
- Adding the `@tool` decorator above the function allows Strands to automatically convert this function into a tool that the agent can use.
- The function's parameter type hints (`city: str`, `days: int`) and return type (`-> str`) provide necessary information for the agent to use the tool correctly.

```py
@tool
def weather_forecast(city: str, days: int = 3) -> str:
    """Gets the weather for a city.
        Args:
            city: Name of the city
            days: Forecast period (in days)
    """
    weather_options = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Foggy"]
    selected_weather = random.choice(weather_options)

    print(f"Checking weather for {city} (forecast period: {days} days)...\n")
    print(f"Expected weather: {selected_weather}\n")
    print("="*10)
    return selected_weather

```

**3-4.** Create an agent that includes the custom tool.

Pass both the custom `weather_forecast` tool and the built-in `calculator` tool together. The agent will automatically select the appropriate tool based on user questions.

```py
agent = Agent(
    tools=[weather_forecast, calculator]
    )

```

**3-5.** Execute the agent.

```py
if __name__ == "__main__":
    user_input = "How's the weather in Seoul tomorrow?"

    response = agent(user_input)

```

The agent will recognize the "Seoul weather" keyword and call the `weather_forecast` tool, automatically extracting and passing the parameters `city="Seoul", days=1`.

**3-6.** Open the terminal and run the following command to check the result:

```bash
uv run python 01-single-agent/labs/custom_tool1.py
```

You can confirm that the agent analyzes the question, calls the `weather_forecast` tool, and returns weather information for Seoul.

![custom tool result](../../docs/images/c1-customtool1.png)

---

### 4. Connecting Custom Tools (2): Using Pre-defined Local Tool Files with TOOL_SPEC

As projects grow, it's good practice to separate tools into separate files for management.

If you open the `01-single-agent/labs/tools` folder, you'll find 2 pre-defined tool files (plus `decorators.py`, a logging helper they both use). Let's learn how to import and use these 2 tool modules written as files.

**4-1.** Open the `01-single-agent/labs/custom_tool2.py` file.

**4-2.** Import the necessary libraries and local tools. Import two tools pre-implemented in the `tools/` directory.

- `python_repl_tool` generates and executes Python code,
- `bash_tool` executes system commands.

```py
from strands import Agent
from tools import python_repl_tool, bash_tool

```

**4-3.** Create an agent that includes the tools.

```py
agent = Agent(
    tools=[bash_tool, python_repl_tool]
    )

```

**4-4.** Write code to execute the agent.

The first user_input requests Python code writing and execution, so it will use `python_repl_tool`.

The commented request is a prompt that requests file system inquiry, so it will use `bash_tool`. Feel free to change and use it.

```py

if __name__ == "__main__":
    user_input = "Can you write and execute Python code that prints Hello world?"

    ## Or, uncomment below to change the prompt and execute
    # user_input = "Check what files are in the 01-single-agent/completed folder"

    response = agent(user_input)

```

**4-5.** Run in the terminal to check the result:

```bash
uv run python 01-single-agent/labs/custom_tool2.py
```

You can confirm the process where the agent generates Python code and executes it through `python_repl_tool`.

![python repl tool result](../../docs/images/c1-customtool-py.png)

Try the other commented user_input as well. It will call the tool that executes bash commands, displaying results like below.

![bash tool result](../../docs/images/c1-customtool-bash.png)

> [!NOTE]
> **Congratulations!**
> We have practiced various ways to create agents using the Strands SDK. From basic agent creation to custom tool development, and advanced model configuration, we have experienced the core features of Strands.

<details>
<summary>Review of Key Concepts from This Section</summary>

### 1. Basic Pattern of Agent Creation

```py
# Most basic form
agent = Agent(tools=[...])

# Using custom model
agent = Agent(model=custom_model, tools=[...])
```

The agent analyzes user questions, automatically selects and executes provided tools when necessary, and generates final answers.

### 2. Three Types of Tools

**Built-in Tools**

```py
from strands_tools import calculator, current_time
agent = Agent(tools=[calculator, current_time])
```

**Custom Tools**

```py
from strands import tool

@tool
def my_custom_tool(param: str) -> str:
    return f"Processing result: {param}"

agent = Agent(tools=[my_custom_tool])
```

**MCP Tools**

```py
from strands.tools.mcp import MCPClient

with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(tools=tools)
```

### 3. Model Configuration

**Using Default Model**

```py
agent = Agent(tools=[...])  # Using Strands default model
```

**Custom Model Configuration**

```py
from strands.models import BedrockModel

bedrock_model = BedrockModel(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    additional_request_fields={
        "thinking": { "type": "enabled", "budget_tokens": 8000 }
    }
)
agent = Agent(model=bedrock_model, tools=[...])
```

### 4. Execution Patterns

**Synchronous Execution**

```py
response = agent("User question")
```

**When Using MCP Tools**

```py
with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(tools=tools)
    response = agent("User question")
```

</details>

---

## 2. Knowledge Base Integration

In this section, we will create an Amazon Bedrock Knowledge Base and build a RAG (Retrieval-Augmented Generation) agent that retrieves information from the Knowledge Base using the Strands agent's `retrieve` tool.

> [!WARNING]
> This section creates AWS resources that **bill continuously**: an OpenSearch Serverless collection (created together with the Knowledge Base) and an S3 bucket. Follow the [Cleanup](#cleanup) section when you are done.

### What is Amazon Bedrock Knowledge Base?

[Amazon Bedrock Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) is a service that configures and manages RAG capabilities in Amazon Bedrock. It automatically embeds documents stored in S3 into a vector database, enabling agents to search relevant documents and answer natural language questions.

#### Why Do We Need a Knowledge Base?

LLMs struggle to provide accurate answers about the latest information or internal company documents not included in their training data. By integrating a Knowledge Base:

- **Up-to-date information**: Answers based on updated documents
- **Accurate answers**: Finds evidence from actual documents (reduces hallucination)
- **Internal knowledge utilization**: Agents can reference company documents, manuals, etc.

---

### 1. Create S3 Bucket and Upload Documents

Upload documents to an S3 bucket for use with the Knowledge Base.

**1-1.** Search for and click the **S3** service in the AWS Console.

![S3](../../docs/images/c1-2-s3_1.png)

**1-2.** Click the **Create bucket** button to create a new S3 bucket.

![S3 Create Bucket](../../docs/images/c1-2-s3_2.png)

**1-3.** Enter `strands-kb-{unique-identifier}` for the Bucket name. Set `{unique-identifier}` to a unique value such as your Account ID. Leave the remaining options as default and click **Create bucket**.

![S3 Bucket Name](../../docs/images/c1-2-s3_3.png)

**1-4.** Navigate to the created bucket and click the **Upload** button.

**1-5.** Upload a document file for the Knowledge Base. Download the Amazon Shareholder Letter PDF from the link below and upload it.

[Amazon 2024 Shareholder Letter (PDF)](https://ws-assets-prod-iad-r-icn-ced060f0d38bc0b0.s3.ap-northeast-2.amazonaws.com/04290929-3dc2-4978-a65d-70e93eafe0d1/2024-Amazon-Shareholder-Letter.pdf)

> [!NOTE]
> Click the link above to download the PDF, then upload it to the S3 bucket.

**1-6.** Verify that the files have been uploaded successfully.

---

### 2. Create Knowledge Base

**2-1.** Search for and click the **Amazon Bedrock** service in the AWS Console.

![Bedrock Page](../../docs/images/c1-2-kb_1.png)

**2-2.** Select **Knowledge bases** from the left menu, then click the **Create > Knowledge base with vector store** button.

![Bedrock Create KB](../../docs/images/c1-2-kb_2.png)

**2-3.** Enter `strands-workshop-kb` for the Knowledge Base Name, select **Amazon S3** as the Data Source, and click the **Next** button.

![Bedrock S3 Selection](../../docs/images/c1-2-kb_3.png)

**2-4.** Click the **Browse S3** button to select the bucket you created earlier, then click the **Next** button.

**2-5.** Select **Titan Text Embeddings V2** as the Embeddings model. For Vector Store Type, select **Amazon OpenSearch Serverless**, then click the **Next** button.

![Bedrock Create KB](../../docs/images/c1-2-kb_4.png)

**2-6.** Click the **Create knowledge base** button to create the Knowledge Base. Wait for the creation to complete.

**2-7.** Select the created item in the Data source and click the **Sync** button to synchronize.

**2-8.** When the Status shows **Available**, synchronization is complete.

---

### 3. Test Knowledge Base (Console)

Let's test the Knowledge Base directly from the Bedrock console to verify it works correctly.

**3-1.** Select the created Knowledge Base in the Amazon Bedrock console.

![Bedrock Check KB](../../docs/images/c1-2-kb_6.png)

**3-2.** Click the **Select model** button in the **Test knowledge base** section.

![Bedrock Test KB](../../docs/images/c1-2-kb_7.png)

**3-3.** Select a Claude model and click the **Apply** button.

![Bedrock Choose Model](../../docs/images/c1-2-kb_8.png)

**3-4.** Enter a question and click the **Run** button to check the response.

![Bedrock KB Run](../../docs/images/c1-2-kb_9.png)

---

### 4. Get Knowledge Base ID

**4-1.** Copy the **Knowledge Base ID** from the detail page of the created Knowledge Base. This ID will be used when accessing the Knowledge Base from the Strands agent.

![Bedrock Get KB ID](../../docs/images/c1-2-kb_10.png)

> [!IMPORTANT]
> Note this ID down now. In the next step you must paste it into the `KNOWLEDGE_BASE_ID` variable in `01-single-agent/labs/knowledge_base.py`. The agent has no other way to find your Knowledge Base, and leaving the placeholder text in place makes the `retrieve` tool fail.

---

### 5. Using Knowledge Base with Strands Agent

Now let's create an agent that retrieves information from the Knowledge Base using the Strands SDK's `retrieve` tool.

**5-1.** Open the `01-single-agent/labs/knowledge_base.py` file.

**5-2.** Import the necessary libraries.

```py
from strands import Agent
from strands_tools import retrieve

```

**5-3.** Create an agent that uses the Knowledge Base.

The `retrieve` tool is a built-in tool that searches for relevant documents from an Amazon Bedrock Knowledge Base. Include the Knowledge Base ID in the system prompt so the agent references the correct Knowledge Base.

Replace `<Enter your Knowledge Base ID here>` with the ID you copied in step 4-1.

```py
KNOWLEDGE_BASE_ID = "<Enter your Knowledge Base ID here>"

agent = Agent(
    system_prompt=f"""You are a document-based Q&A assistant.
    When answering user questions, you must use the retrieve tool to search for relevant information from the Knowledge Base (ID: {KNOWLEDGE_BASE_ID}) before answering.
    Answer accurately based on the retrieved document content, and say you don't know if the information is not in the documents.""",
    tools=[retrieve]
)

```

**5-4.** Ask the agent a question.

```py
if __name__ == "__main__":
    response = agent("Please summarize the main content of the uploaded document.")
    print(response)

```

**5-5.** Run in the terminal to check the result:

```bash
uv run python 01-single-agent/labs/knowledge_base.py
```

You can confirm that the agent uses the `retrieve` tool to search for relevant documents from the Knowledge Base and answers based on the retrieved content.

> [!NOTE]
> **Congratulations!**
> You have created an Amazon Bedrock Knowledge Base and built a RAG-based Q&A agent using the Strands agent's `retrieve` tool. This enables the agent to reference external documents and provide more accurate answers.

<details>
<summary>Review of Key Concepts</summary>

### Knowledge Base + Strands Integration Pattern

```py
from strands import Agent
from strands_tools import retrieve

agent = Agent(
    system_prompt="Use the retrieve tool to search the Knowledge Base before answering.",
    tools=[retrieve]
)
response = agent("Your question")
```

### Benefits of RAG

- **Reduced hallucination**: Answers based on actual documents
- **Up-to-date information**: Automatically reflects document updates
- **Source traceability**: Can verify the source documents for answers

</details>

---

## 3. MCP Tool Integration

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/docs/getting-started/intro) is **a standard protocol for connecting external data sources or services to AI agents**. Through MCP servers, agents can access external information in real-time.

In this section, we will connect two MCP servers to the agent:

1. **AWS Documentation MCP**: Agent that searches AWS official documentation
2. **Playwright MCP**: Agent that automates web browsers to interact with web pages

---

### 1. AWS Documentation MCP Integration

**1-1.** Open the `01-single-agent/labs/mcp_tool.py` file.

**1-2.** Import the necessary libraries.

- `MCPClient` is a class that connects tools provided by MCP servers so that Strands agents can use them.

```py
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

```

**1-3.** Configure the MCP client.
- This code connects to the [AWS Documentation MCP Server](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server), an MCP server for searching AWS official documentation.
- You can find more AWS MCPs on [this page](https://awslabs.github.io/mcp/), and you can update the MCP server name in the `args=` parameter.

```py
stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx",
                          args=["awslabs.aws-documentation-mcp-server@latest"]
                          )
))

```

**1-4.** Execute an agent that uses MCP tools.

```py
if __name__ == "__main__":
    user_input = "What is the Amazon Bedrock pricing model? Please explain concisely."

    agent = Agent(tools=[stdio_mcp_client])
    response = agent(user_input) 

```

**1-5.** Run in the terminal to check the result:

```bash
uv run python 01-single-agent/labs/mcp_tool.py
```

You can confirm that the agent connects to the AWS documentation MCP server to search for the latest information in real-time and provide answers.

![MCP tool result](../../docs/images/c1-mcptool.png)

---

### 2. Adding Playwright MCP

Now let's add **Playwright MCP**. Playwright is a tool for automating web browsers, capable of visiting web pages, taking screenshots, filling out forms, and more.

> [!WARNING]
> Playwright MCP needs a GUI browser. If your environment has no browser installed (for example a bare workshop or SageMaker Studio environment), Playwright MCP will not work properly. Test this part in a local environment where a browser is installed.

#### 2-1. Finding MCP Servers on mcp.so

[mcp.so](https://mcp.so) is a hub that aggregates various MCP servers. You can search for MCP servers with desired functionality and get their configuration information.

![mcp.so](../../docs/images/mcp-so.png)

**2-1-1.** Visit [mcp.so](https://mcp.so).

**2-1-2.** Search for "playwright" to find the [Playwright MCP Server](https://mcp.so/server/playwright-mcp/microsoft).

**2-1-3.** Check the configuration information provided on the page. You'll see information like below:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

![mcp config](../../docs/images/mcp-config.png)

#### 2-2. Integrating Playwright MCP

**2-2-1.** Add the Playwright MCP client in the `01-single-agent/labs/mcp_tool.py` file:

```py
# Add below the existing AWS Documentation MCP
playwright_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx",
                          args=["@playwright/mcp@latest"]
                          )
))

```

**2-2-2.** Connect both MCP tools to the agent:

```py
if __name__ == "__main__":
    user_input = "Visit https://aws.amazon.com and take a screenshot"

    agent = Agent(tools=[stdio_mcp_client, playwright_mcp_client])
    response = agent(user_input)

```

<details>
<summary>View Full Code (mcp_tool.py)</summary>

```py
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx",
                          args=["awslabs.aws-documentation-mcp-server@latest"]
                          )
))

playwright_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx",
                          args=["@playwright/mcp@latest"]
                          )
))

if __name__ == "__main__":
    user_input = "Visit https://aws.amazon.com and take a screenshot"

    agent = Agent(tools=[stdio_mcp_client, playwright_mcp_client])
    response = agent(user_input)
```

The reference answer in `01-single-agent/completed/mcp_tool.py` is the same code, except that the AWS Documentation MCP client is named `aws_docs_mcptool` instead of `stdio_mcp_client`.

</details>

**2-2-3.** Run in the terminal to check the result:

```bash
uv run python 01-single-agent/labs/mcp_tool.py
```

You can confirm that the agent uses Playwright to visit the web page and save a screenshot.

> [!NOTE]
> **Congratulations!**
> You've created an agent that integrates with external systems using MCP. From AWS documentation search to web browser automation, your agent can now use various tools.

---

## 4. (Optional) Self-Improving Agent

So far, the agents we built could only use the **tools we defined in advance**, and only behaved according to the **system prompt we wrote**.

In this application section, we go one step further and practice two patterns for a **self-improving agent**. It is still a single agent, but it is far more autonomous in that it expands its own capabilities and changes its own behavior at runtime.

1. **Self-extending**: the agent **writes the code for a tool it needs** and **uses it immediately**, with no restart. (`load_tools_from_directory`)
2. **Self-modifying**: the agent **rewrites its own system prompt**, permanently changing how it behaves.

> [!NOTE]
> The ideas in this section are adapted for the workshop environment from the AWS Summit session **AIM308: "Using Strands to build fully autonomous, self-improving AI agents"** ([strands-agents/samples](https://github.com/strands-agents/samples/tree/main/python/01-learn/18-self-improving-agents)).

> [!WARNING]
> **These two agents write files into your working tree.**
> - `self_extending.py` gives the agent a `file_write` tool and lets it create brand new `.py` files inside `tools/`. Those files stay on disk and are reloaded on the next run.
> - `self_modifying.py` writes a `.prompt` file, and in this lab you write `labs/tools/system_prompt.py` yourself (the reference version is in `completed/tools/system_prompt.py`).
>
> After running these labs, `git status` will show new and modified files. Review and delete anything you do not want to keep. Because `load_tools_from_directory` executes any Python file it finds in `tools/`, read the generated code before rerunning.

> [!NOTE]
> **Run these two labs from the lab directory.** `load_tools_from_directory` watches `./tools/` and the `.prompt` file is written relative to the **current working directory**, so run them like this:
>
> ```bash
> cd 01-single-agent/labs
> uv run python self_extending.py
> ```
>
> That way the agent writes into `01-single-agent/labs/tools/` and `01-single-agent/labs/.prompt`, next to the code you are editing.

---

### 1. Self-extending Agent: Writing Its Own Tools

The first pattern is about **an agent building the tools it needs, by itself**.

There are just two key pieces:
- The `Agent(load_tools_from_directory=True)` option: the SDK watches the `./tools/` directory and, whenever a `.py` file is created or changed, automatically (re)registers the tool **without a restart** (hot-reload).
- Giving the agent a **tool that can write files** (`file_write`) and a system prompt that tells it **how to create a tool**.

Put these together and, whenever the agent hits "something I can't do with my current tools," it writes a tool file itself and calls it right away.

**1-1.** Open the `01-single-agent/labs/self_extending.py` file.

**1-2.** Import the required libraries.

- `shell` and `file_write` are Built-in tools for running shell commands and writing files, respectively. The agent uses this `file_write` tool to author new tool files.
- `BYPASS_TOOL_CONSENT=true` disables the `y/n` confirmation prompt that `strands_tools` shows before each tool execution. Without it, every `file_write` and `shell` call stops and waits for you to type `y`. It keeps the lab flowing smoothly, and it must be set **before** importing `strands_tools`. Keep in mind that this also removes the human approval step, so the agent runs shell commands and writes files unattended.

```py
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from strands import Agent
from strands.models import BedrockModel
from strands_tools import shell, file_write

```

**1-3.** Write a system prompt that tells the agent "how to create a tool."

- The key is to include a **template** for the `@tool` decorator in the system prompt. This makes the agent write tool files in the correct format the SDK can recognize.

````py
SYSTEM_PROMPT = """You are a self-extending research agent.

You can CREATE new tools by writing Python files to ./tools/. Each file should
define one or more functions decorated with `@tool` from the strands package.
Tools become available instantly after the file is saved.

Template for a new tool:

```python
from strands import tool

@tool
def my_tool(argument: str) -> str:
    \"\"\"Short description of what this tool does.

    Args:
        argument: What this argument means.

    Returns:
        A string result.
    \"\"\"
    return f"result for {argument}"
```

When a user asks for a capability you don't have, CREATE the tool, then USE it.
Be concise in your replies.
"""

````

**1-4.** Create the model and the agent.

- Here, `load_tools_from_directory=True` is **the key option for this lab**. (The SDK default is `False`; because it carries the risk of arbitrary code execution, you must enable it explicitly.)

```py
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6"
)

agent = Agent(
    model=bedrock_model,
    tools=[shell, file_write],
    load_tools_from_directory=True,   # load/reload ./tools/*.py at runtime
    system_prompt=SYSTEM_PROMPT,
)

```

**1-5.** Run the agent.

- The request below is a capability the agent **does not currently have**. The agent must build a tool for it and then use that tool.

```py
if __name__ == "__main__":
    user_input = "Create a tool that prints a URL I give you as a QR code, then generate the code for https://strandsagents.com."

    response = agent(user_input)

```

**1-6.** Run the following commands in the terminal to check the result:

```bash
cd 01-single-agent/labs
uv run python self_extending.py
```

You can see that the agent 1) **writes a tool file** such as `qr_generator.py` into the `tools/` directory, 2) the SDK **loads it instantly**, and 3) within the same run it **calls** that tool to print the QR code in the terminal.

![agent writes its own tool](../../docs/images/c1-4-self-extending-1.png)

![agent calls the tool it just wrote](../../docs/images/c1-4-self-extending-2.png)

**1-7.** Open the `tools/` folder in the lab directory and you will see that the **tool file the agent just wrote** is actually saved there. This file will be reloaded as-is on the next run.

![generated tool file](../../docs/images/c1-4-generated-tool.png)

<details>
<summary>View the full code</summary>

The complete `self_extending.py` code you have written so far is as follows. You can find the same content in `01-single-agent/completed/self_extending.py`:

````py
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from strands import Agent
from strands.models import BedrockModel
from strands_tools import shell, file_write

SYSTEM_PROMPT = """You are a self-extending research agent.

You can CREATE new tools by writing Python files to ./tools/. Each file should
define one or more functions decorated with `@tool` from the strands package.
Tools become available instantly after the file is saved.

Template for a new tool:

```python
from strands import tool

@tool
def my_tool(argument: str) -> str:
    \"\"\"Short description of what this tool does.

    Args:
        argument: What this argument means.

    Returns:
        A string result.
    \"\"\"
    return f"result for {argument}"
```

When a user asks for a capability you don't have, CREATE the tool, then USE it.
Be concise in your replies.
"""

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6"
)

agent = Agent(
    model=bedrock_model,
    tools=[shell, file_write],
    load_tools_from_directory=True,   # load/reload ./tools/*.py at runtime
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    user_input = "Create a tool that prints a URL I give you as a QR code, then generate the code for https://strandsagents.com."
    response = agent(user_input)
````

</details>

---

### 2. Self-modifying Agent: Rewriting Its Own System Prompt

The second pattern is about **an agent changing its own behavior (system prompt) by itself**.

Again there are two key pieces:
- A **custom tool that manipulates the system prompt** (`system_prompt`): it persists the prompt to a `.prompt` file.
- **Reassembling the system prompt every turn**: instead of hardcoding it, we read it back from disk (`.prompt`) each time and merge it. That way changes take effect immediately and **survive restarts**.

**2-1.** First we build the tool that manipulates the prompt. Open the `01-single-agent/labs/tools/system_prompt.py` file. Unlike the other files in `labs/tools/`, this one is empty; you write it now, and from then on the agent overwrites the `.prompt` file through it.

**2-2.** Write a `@tool` function that saves / views / resets the prompt to a file.

- `update`: fully replaces the prompt with a new one and saves it to the `.prompt` file.
- `add_context`: appends content to the existing prompt.
- `view` / `reset`: views the current prompt or reverts to the default.

```py
from pathlib import Path
from strands import tool

PROMPT_FILE = Path(".prompt")

@tool
def system_prompt(action: str, prompt: str | None = None) -> dict:
    """Manage the agent's own system prompt at runtime.

    Args:
        action: One of "view", "update", "add_context", "reset".
        prompt: The new prompt text (required for update / add_context).

    Returns:
        Dict with status and content.
    """
    if action == "view":
        current = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
        return {"status": "success", "content": [{"text": current or "(empty)"}]}

    if action == "update":
        if not prompt:
            return {"status": "error", "content": [{"text": "prompt required"}]}
        PROMPT_FILE.write_text(prompt)   # persist to disk -> survives restarts
        return {"status": "success",
                "content": [{"text": f"Prompt updated & persisted ({len(prompt)} chars)."}]}

    if action == "add_context":
        if not prompt:
            return {"status": "error", "content": [{"text": "prompt required"}]}
        existing = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
        merged = f"{existing}\n\n{prompt}" if existing else prompt
        PROMPT_FILE.write_text(merged)
        return {"status": "success", "content": [{"text": "Context appended."}]}

    if action == "reset":
        if PROMPT_FILE.exists():
            PROMPT_FILE.unlink()
        return {"status": "success", "content": [{"text": "Prompt reset to default."}]}

    return {"status": "error", "content": [{"text": f"Unknown action: {action}"}]}

```

**2-3.** Now we build the agent that uses this tool. Open the `01-single-agent/labs/self_modifying.py` file.

**2-4.** Import the required libraries and the tool you just created.

```py
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from pathlib import Path
from strands import Agent
from strands.models import BedrockModel
from tools.system_prompt import system_prompt

PROMPT_FILE = Path(".prompt")

```

**2-5.** Write a function that reassembles the system prompt **every turn**.

- It merges the base prompt with the modifications persisted on disk (`.prompt`) and returns the result.
- When the agent changes `.prompt` via `system_prompt(action="update", ...)`, this function reads that content back on the next turn and reflects it.

```py
def build_system_prompt() -> str:
    """Reassemble the system prompt from multiple sources every turn."""
    base = (
        "You are a self-improving research agent.\n"
        "You can MODIFY YOUR OWN SYSTEM PROMPT using the system_prompt tool.\n"
        "Actions: view, update, add_context, reset.\n"
        "When a user asks you to change your behavior 'from now on' or "
        "'permanently', call system_prompt(action='update', prompt=...)."
    )
    persisted = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
    parts = [base]
    if persisted:
        parts.append(f"\n## Persisted instructions (.prompt):\n{persisted}")
    return "\n".join(parts)

```

**2-6.** Write the conversation loop.

- The key is to **recreate the agent every turn**. This way `build_system_prompt()` reads the just-changed `.prompt` again, so prompt modifications take effect **immediately**.

```py
bedrock_model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

if __name__ == "__main__":
    print("🦆 Self-modifying agent. Type 'exit' to quit.\n")
    while True:
        q = input("🦆 ").strip()
        if q.lower() in ("exit", "quit", "q", ""):
            break

        # Rebuild the agent each turn so prompt updates apply right away
        agent = Agent(
            model=bedrock_model,
            tools=[system_prompt],
            system_prompt=build_system_prompt(),
        )
        agent(q)

```

**2-7.** Run it in the terminal:

```bash
cd 01-single-agent/labs
uv run python self_modifying.py
```

**2-8.** Ask the agent to **permanently change its behavior, or to remember something**. For example:

```
My name is Gildong. Remember it permanently.
```

Instructions that change its tone or output format work well too:

```
From now on, append "🐿️" to the end of every sentence. Example: I'm a research agent 🐿️ How can I help you 🐿️
```

You can see the agent call the `system_prompt` tool with `action="update"` to rewrite its own prompt.

![agent updates its own system prompt](../../docs/images/c1-4-self-modifying.png)

**2-9.** Now ask any question. From this turn on, the agent follows the changed instruction (e.g. appending "🐿️" to every sentence). If you open the `.prompt` file created in the lab directory, you will see the changed instruction is actually saved. Even if you **quit and rerun the program**, the setting persists.

![persisted prompt file](../../docs/images/c1-4-persisted-prompt.png)

<details>
<summary>View the full code</summary>

The complete `self_modifying.py` code you have written so far is as follows. You can find the same content in `01-single-agent/completed/self_modifying.py`:

```py
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"  # disable the y/n confirmation prompt on tool execution

from pathlib import Path
from strands import Agent
from strands.models import BedrockModel
from tools.system_prompt import system_prompt

PROMPT_FILE = Path(".prompt")

def build_system_prompt() -> str:
    base = (
        "You are a self-improving research agent.\n"
        "You can MODIFY YOUR OWN SYSTEM PROMPT using the system_prompt tool.\n"
        "Actions: view, update, add_context, reset.\n"
        "When a user asks you to change your behavior 'from now on' or "
        "'permanently', call system_prompt(action='update', prompt=...)."
    )
    persisted = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
    parts = [base]
    if persisted:
        parts.append(f"\n## Persisted instructions (.prompt):\n{persisted}")
    return "\n".join(parts)

bedrock_model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

if __name__ == "__main__":
    print("🦆 Self-modifying agent. Type 'exit' to quit.\n")
    while True:
        q = input("🦆 ").strip()
        if q.lower() in ("exit", "quit", "q", ""):
            break
        agent = Agent(
            model=bedrock_model,
            tools=[system_prompt],
            system_prompt=build_system_prompt(),
        )
        agent(q)
```

</details>

> [!NOTE]
> **Congratulations!**
> You have built an agent that improves itself with the Strands SDK. You experienced two autonomous patterns: expanding capabilities by writing its own tools, and changing behavior by rewriting its own system prompt.

<details>
<summary>Review of the key concepts from this section</summary>

### 1. Self-extending

```py
agent = Agent(
    tools=[shell, file_write],
    load_tools_from_directory=True,   # load/reload ./tools/*.py at runtime
    system_prompt=SYSTEM_PROMPT,      # tells the agent "how to build a tool with @tool"
)
```

When the agent writes a tool file to `./tools/` via `file_write`, the SDK registers that tool instantly without a restart, so it can be used right away.

### 2. Self-modifying

```py
# (1) A tool that saves the prompt to a file
@tool
def system_prompt(action, prompt=None): ...   # write to the .prompt file

# (2) Reassemble the prompt every turn + recreate the agent every turn
agent = Agent(system_prompt=build_system_prompt(), tools=[system_prompt])
```

Because the prompt lives on **disk (`.prompt`)** rather than in code and is read back every turn, changes apply immediately and survive restarts.

### 3. Design principles that run through both

- **Always keep self-modification state on disk / externally**: tools as `./tools/*.py`, the prompt as a `.prompt` file. They survive restarts and can be inspected and rolled back.
- **To reflect changes instantly, create a point that "re-reads and reconstructs" state every time** (hot-reload / per-turn reassembly).
- **Grant capability via prompt + tool set**: simply giving the LLM a template of "this is how you build a tool" enables self-extension.

</details>

---

## Cleanup

Section 2 creates AWS resources that keep billing until you delete them. An **OpenSearch Serverless collection bills per OCU-hour even when idle**, so delete it as soon as you finish the lab.

Delete them in this order:

1. **Bedrock Knowledge Base**: Amazon Bedrock console > **Knowledge bases** > select `strands-workshop-kb` > **Delete**. Note whether the console offers to delete the associated vector store; if it does not, delete it manually in step 2.
2. **OpenSearch Serverless collection**: Amazon OpenSearch Service console > **Serverless** > **Collections** > select the collection created for the Knowledge Base (its name starts with `bedrock-knowledge-base-`) > **Delete**. Also remove the associated data access, network, and encryption policies if they remain.
3. **S3 bucket**: S3 console > select `strands-kb-{unique-identifier}` > **Empty** the bucket, then **Delete** it.

Local files created by section 4:

```bash
# from the repo root, review before deleting
git status 01-single-agent
rm -f 01-single-agent/labs/.prompt
```

Also delete any `01-single-agent/labs/tools/*.py` file that the agent generated (for example `qr_generator.py`). Keep `bash_tool.py`, `decorators.py`, `python_repl_tool.py`, and `system_prompt.py`.

## Troubleshooting

**`AccessDeniedException` when calling Bedrock**

The model is not enabled for your account. Open the Amazon Bedrock console > **Model access** and request/enable access for the Anthropic Claude models. This chapter uses:

- `us.anthropic.claude-sonnet-4-20250514-v1:0` (`models.py`)
- `us.anthropic.claude-sonnet-4-6` (`self_extending.py`, `self_modifying.py`)
- `amazon.titan-embed-text-v2:0` (Titan Text Embeddings V2, used by the Knowledge Base)

`basic.py`, `custom_tool1.py`, `custom_tool2.py`, `knowledge_base.py`, and `mcp_tool.py` do not set a model, so they use the Strands default Bedrock model, which also has to be enabled. The same error can also come from a missing IAM permission (`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`) on the identity you are using.

**Wrong region**

The labs assume **us-west-2**. Model access is per region, so a model enabled in another region still fails here. Check and set the region before running:

```bash
aws configure get region
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=us-west-2
```

For section 2, the Knowledge Base, its OpenSearch Serverless collection, and the agent must all be in the same region. If the `retrieve` tool reports that the Knowledge Base does not exist, you are almost certainly pointing at a different region.

**`ValidationException` mentioning the model ID**

The model ID string is not usable from this account/region: it is not enabled, it does not exist in this region, or the on-demand vs. inference-profile form is wrong. The `us.` prefix (as in `us.anthropic.claude-sonnet-4-6`) is a **cross-region inference profile** and only resolves in US regions. List what your account can actually call:

```bash
aws bedrock list-inference-profiles --region us-west-2
aws bedrock list-foundation-models --region us-west-2 --by-provider anthropic \
  --query "modelSummaries[].modelId"
```

Then set `model_id` to a value from that output.

**`retrieve` returns nothing**

The data source has not been synced. In the Bedrock console, open the Knowledge Base, select the data source, click **Sync**, and wait for **Available**. Also confirm you replaced `KNOWLEDGE_BASE_ID` in `knowledge_base.py` with your real ID.

**The tool run stops and asks `y/n`**

That is the `strands_tools` consent prompt. Either answer `y`, or set `os.environ["BYPASS_TOOL_CONSENT"] = "true"` **before** importing `strands_tools`, as section 4 does.

**Playwright MCP fails to start**

`npx` must be on your PATH and a browser must be installed. Run `node --version` to confirm Node.js is present. In a headless environment, skip this part.

---
Prev: [00. Setup](../00-setup/README.md) | Next: [02. Multi-Agent Systems](../02-multi-agents/README.md)
