# Agentic AI 101 on AWS

[한국어 README](README.ko.md)

🎯 **Learning path**: Setup → Single agent → Multi-agent patterns → Memory → Deployment → Observability

Build an AI agent from scratch with the [Strands Agents SDK](https://strandsagents.com/docs/), then deploy and operate it with [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/).

This is a hands-on workshop. Each chapter has a `labs/` folder with empty files that you fill in yourself, and a `completed/` folder holding the reference implementation. You learn by typing the code, then comparing against the reference.

![Agentic AI 101 on AWS](docs/images/agentic-ai-101.png)

**Level:** 100 to 200 (beginner to intermediate). No prior agent or LLM experience required.
**Duration:** about 4 hours for the required chapters, about 5.5 hours for all nine.

---

## 📚 What you will learn

- **Strands Agents SDK**: build an agent from a prompt, a model, and tools, then extend it with custom tools and MCP servers
- **Retrieval**: query an Amazon Bedrock Knowledge Base from an agent with the `retrieve` tool
- **Multi-agent systems**: Agents-as-Tools, Swarm, and Graph, and when to reach for each
- **Memory**: short-term and long-term memory with Amazon Bedrock AgentCore Memory
- **Deployment**: turn a local agent into a serverless one on AgentCore Runtime with four added lines
- **Observability**: agent metrics, logs, and OpenTelemetry traces, both self-managed and through CloudWatch GenAI Observability

---

## 🗂️ Chapters

| # | Chapter | What you build | ⏱️ Time | 📊 Level | Track |
|---|---------|----------------|---------|----------|-------|
| 00 | [Setup](00-setup/README.md) | Python environment, AWS credentials, Bedrock model access | 10 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Required |
| 01 | [Single agent](01-single-agent/README.md) | Agent with prompt, model, and tools. Bedrock Knowledge Base, MCP tools, self-improving agent | 90 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Required |
| 02 | [Multi-agent patterns](02-multi-agents/README.md) | Agents-as-Tools, Swarm, and Graph | 50 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Required |
| 03 | [Chatbot application](03-chatbot-app/README.md) | Streamlit chat UI with streaming and tool-call display | 20 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Optional |
| 04 | [Observability with Strands](04-observability/README.md) | Metrics, logs, and OTLP traces to a local Jaeger | 30 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Optional |
| 05 | [Agent memory](05-agent-memory/README.md) | Short-term and long-term memory with AgentCore Memory | 40 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Required |
| 06 | [AgentCore Runtime](06-agentcore-runtime/README.md) | Serverless deployment of the agent | 40 min | ![Advanced](https://img.shields.io/badge/-Advanced-red) | Required |
| 07 | [AgentCore Observability](07-agentcore-observability/README.md) | CloudWatch GenAI Observability dashboard | 20 min | ![Advanced](https://img.shields.io/badge/-Advanced-red) | Required |
| 08 | [Developing with Kiro IDE](08-kiro-dev/README.md) | Steering, MCP config, and spec-driven development | 30 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Optional |

> [!TIP]
> Chapters 01, 02, 05, 06, and 07 form the core path. Chapters 03, 04, and 08 are self-contained and can be skipped. Chapter 07 is the one dependency worth noting: it reads telemetry from the agent you deploy in chapter 06.

---

## 🧪 Chapter details

### 00. Setup
**Files**: `create-uv-env.sh`, `pyproject.toml`, `uv.lock`, `install_korean_font.sh`

Two paths, and you only need one: run the labs on your own machine (~10 min), or deploy an AWS-hosted VS Code Server with CloudFormation (~30 min, as used in the instructor-led workshop).

- A Python 3.12 project managed by [uv](https://docs.astral.sh/uv/), shared by every later chapter
- AWS credentials that can call Amazon Bedrock, and model access in `us-west-2`
- Optional symlinks at the repository root so a bare `uv run` works from anywhere in the repo

### 01. Building a Basic Single Agent
**Files**: `basic.py`, `models.py`, `custom_tool1.py`, `custom_tool2.py`, `knowledge_base.py`, `mcp_tool.py`, `self_extending.py`, `self_modifying.py`, `tools/`

The three core pieces of the SDK (prompt, model, tools) and then everything you bolt onto them:

- Creating an agent with built-in tools from `strands_tools`
- Configuring `BedrockModel` and enabling Extended Thinking (reasoning)
- Writing custom tools two ways: the `@tool` decorator and a `TOOL_SPEC` tool module
- Creating an Amazon Bedrock Knowledge Base and querying it with the `retrieve` tool (RAG)
- Connecting MCP servers (AWS Documentation MCP, Playwright MCP) as agent tools
- Two self-improving patterns: an agent that writes its own tools, and one that rewrites its own system prompt

> **Note**: Section 2 creates a Knowledge Base backed by an OpenSearch Serverless collection, which bills continuously. Section 4 is optional.

### 02. Multi-Agent Patterns
**Files**: `agents_as_tools.py`, `swarms.py`, `graph_parallel.py`, `graph_condition.py`

Three ways to make agents collaborate on tasks a single agent handles poorly:

- Wrapping specialized agents as tools with `@tool` and routing through an orchestrator ([Agents-as-Tools](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/))
- Letting agents autonomously hand off work to each other with [`Swarm`](https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/)
- Defining explicit execution order, dependencies, and parallel branches with [`GraphBuilder`](https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/)
- Branching a graph to different agents with conditional edges

### 03. Applying Agents to a Chatbot Application
**Files**: `streamlit_app.py`

Move the agent out of the terminal and into a web app:

- A chatbot UI with Streamlit, and conversation history in session state
- Real-time responses with `stream_async` and asynchronous streaming
- Visualizing the tool-calling process as it happens

### 04. Agent Observability with Strands
**Files**: `metrics_basic.py`, `logs_basic.py`, `traces_console.py`, `traces_otlp.py`, `docker/`

Self-managed observability, for agents you run yourself:

- The `EventLoopMetrics` structure: tokens, cycles, and per-tool statistics
- The `strands` logger hierarchy and per-module log levels
- Instrumenting an agent with OpenTelemetry and printing spans to the console
- Running an ADOT Collector plus Jaeger in Docker and reading traces in the Jaeger UI

> **Note**: If you plan to run on AgentCore Runtime, chapter 07 gets you the same telemetry without building a pipeline.

### 05. Agent Memory with AgentCore Memory
**Files**: `stm_persistence.py`, `ltm_semantic.py`, `ltm_preference.py`, `streamlit_with_memory.py`

Give the agent something to remember between turns and between sessions:

- Core concepts: Session, Actor, and Namespace
- Short-term memory (STM) for conversation persistence within a session
- Long-term memory (LTM) strategies for facts and user preferences
- Wiring memory into a Strands agent and into the Streamlit app from chapter 03

> **Note**: This chapter creates two AgentCore Memory resources that bill until deleted.

### 06. Agent Deployment with AgentCore Runtime
**Files**: `my_agent.py`, `deploy_agent.py`, `invoke_agent.py`, `Dockerfile`, `requirements.txt`

Take the local agent to production without rewriting it:

- What Runtime gives you over running an agent on your machine
- Enabling CloudWatch Transaction Search (once per AWS account)
- Turning a local agent into a deployable one by adding four lines
- Deploying with the AgentCore starter toolkit (`configure()` and `launch()`)
- Invoking a deployed runtime with boto3 and session IDs
- Optionally deploying the multi-agent system from chapter 02

> **Note**: Requires a running container runtime (Docker, Finch, or Podman) and creates billable resources: a Runtime and an ECR repository.

### 07. Agent Observability with AgentCore Observability
**Files**: none, this chapter is console work

Read the telemetry the deployed agent produces on its own:

- What Runtime emits automatically, and where it lands
- The CloudWatch GenAI Observability dashboard: Agents, Sessions, and Traces views
- Runtime metrics published under the `Bedrock-AgentCore` namespace
- Where stdout/stderr and OTEL structured logs are stored in CloudWatch Logs

> **Note**: Complete chapter 06 first. Without a deployed agent the dashboards are empty.

### 08. Developing with Kiro IDE
**Files**: `.kiro/steering/strands-dev.md`, `.kiro/settings/mcp.json`, `completed/hanoi_tower.py`

Hand the agent-writing to an AI IDE and see what changes:

- How a Kiro Power packages MCP servers and documentation for a stack
- How Steering files constrain what Kiro generates, and where they live
- Registering an MCP server so Kiro can look up Strands SDK documentation
- Producing a working Strands agent from one natural-language prompt, then reviewing and running it

---

## 🚀 Quick start

**Prerequisites**

- An AWS account with permission to call Amazon Bedrock and create AgentCore resources
- Amazon Bedrock model access enabled in `us-west-2` for the Anthropic Claude models listed below
- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker, for chapters 04 and 06 only
- AWS CLI configured (`aws configure`), default region `us-west-2`

**Install**

```bash
git clone https://github.com/aws-samples/sample-aws-agentic-ai-workshop.git
cd sample-aws-agentic-ai-workshop/00-setup
uv sync
cd ..
```

**Run your first agent**

```bash
uv run --project 00-setup python 01-single-agent/completed/basic.py
```

If that prints an agent response, your environment is ready. Now open [00-setup/README.md](00-setup/README.md) for the full setup notes, then start [chapter 01](01-single-agent/README.md).

---

## 🤖 Models and region

The labs run against Amazon Bedrock in **`us-west-2`**. Enable model access for these before you start:

| Model ID | Used in |
|---|---|
| `us.anthropic.claude-sonnet-4-20250514-v1:0` | Chapters 01 to 06 |
| `us.anthropic.claude-sonnet-4-6` | Chapter 01 self-improving agent labs, chapter 02 |
| `us.amazon.nova-pro-v1:0` | Chapter 04, metrics lab |

Enable them in the [Bedrock console](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess) under **Model access**. Cross-region inference profiles (the `us.` prefix) require access in the destination regions of the profile, which the console handles for you.

---

## 🛠️ Technologies and services

| Technology | Purpose | Used in | Documentation |
|---|---|---|---|
| **Strands Agents SDK** | Agent framework | All chapters | [Docs](https://strandsagents.com/docs/) |
| **Amazon Bedrock** | Managed model inference | All chapters | [Docs](https://docs.aws.amazon.com/bedrock/) |
| **Bedrock Knowledge Bases** | Managed RAG over your documents | 01 | [Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Model Context Protocol** | Tool integration standard | 01, 08 | [Docs](https://modelcontextprotocol.io/docs/getting-started/intro) |
| **AWS MCP servers** | Ready-made MCP servers for AWS | 01, 08 | [Docs](https://awslabs.github.io/mcp/) |
| **Streamlit** | Chat UI | 03, 05 | [Docs](https://docs.streamlit.io/) |
| **OpenTelemetry, ADOT, Jaeger** | Trace collection and viewing | 04 | [Docs](https://opentelemetry.io/docs/) |
| **AgentCore Memory** | Short-term and long-term agent memory | 05 | [Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) |
| **AgentCore Runtime** | Serverless agent hosting | 06 | [Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) |
| **AgentCore Observability** | CloudWatch GenAI Observability | 07 | [Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) |
| **uv** | Python environment and dependencies | All chapters | [Docs](https://docs.astral.sh/uv/) |
| **Kiro** | AI-powered IDE | 08 | [Docs](https://kiro.dev/docs/) |

---

## 📁 Repository layout

```
sample-aws-agentic-ai-workshop/
├── 00-setup/                     # environment setup, uv project, dependencies
│   ├── pyproject.toml
│   ├── uv.lock
│   └── create-uv-env.sh
├── 01-single-agent/
│   ├── labs/                     # you write these
│   ├── completed/                # reference implementation
│   └── README.md
├── 02-multi-agents/
├── 03-chatbot-app/
├── 04-observability/
│   └── docker/                   # OTel collector + Jaeger
├── 05-agent-memory/
├── 06-agentcore-runtime/
├── 07-agentcore-observability/   # console-only chapter, README only
├── 08-kiro-dev/
│   └── .kiro/                    # steering rules and MCP config
└── docs/images/                  # screenshots referenced by the chapter READMEs
```

Every chapter folder follows the same shape:

```
NN-chapter/
├── README.md        # English lab guide
├── README.ko.md     # Korean lab guide
├── labs/            # empty files, you write the code here
└── completed/       # reference answers, run these if you get stuck
```

---

## 💰 Cost and cleanup

The labs call Bedrock models on demand, and several chapters create AWS resources that bill for as long as they exist:

| Chapter | Standing resources |
|---|---|
| 01 | Bedrock Knowledge Base, OpenSearch Serverless collection, S3 bucket |
| 05 | AgentCore Memory resource |
| 06 | AgentCore Runtime, ECR repository, IAM execution role, CloudWatch log groups |
| 07 | CloudWatch Transaction Search ingestion, trace and log retention |

> [!WARNING]
> Each chapter has its own **Cleanup** section. Work through them when you are done, especially chapters 01, 05, and 06. An OpenSearch Serverless collection in particular bills continuously whether or not you query it.

---

## 🐛 Troubleshooting

These are the failures that come up across chapters. Each chapter also has its own Troubleshooting section for problems specific to it: [00](00-setup/README.md#troubleshooting), [01](01-single-agent/README.md#troubleshooting), [02](02-multi-agents/README.md#troubleshooting), [03](03-chatbot-app/README.md#troubleshooting), [04](04-observability/README.md#troubleshooting), [05](05-agent-memory/README.md#troubleshooting), [06](06-agentcore-runtime/README.md#troubleshooting).

| Symptom | Cause and fix |
|---|---|
| `uv: command not found` | The installer puts the binary in `~/.local/bin`. Open a new shell, or `export PATH="$HOME/.local/bin:$PATH"`. |
| `ModuleNotFoundError` for `strands` or `bedrock_agentcore` | You are on the system Python. Use `uv run --project 00-setup python ...`, or activate `00-setup/.venv`. |
| `AccessDeniedException` when a lab calls a model | Model access is not enabled for that model ID in `us-west-2`, or your credentials lack `bedrock:InvokeModel`. Check the [model access page](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess). |
| `ValidationException` mentioning a region, or model not found | Your default region is not `us-west-2`. Check with `aws configure get region`. |
| `Cannot connect to the Docker daemon` in chapter 04 or 06 | Start Docker Desktop (or Finch / Podman) and confirm with `docker info`, then re-run. |
| Memory calls fail right after creating a memory (chapter 05) | A new AgentCore Memory takes 1 to 2 minutes to reach `ACTIVE`. Wait, then retry. LTM extraction is also asynchronous. |
| CloudWatch GenAI Observability dashboards are empty (chapter 07) | Transaction Search must be enabled, and the agent from chapter 06 must have been invoked at least once. |

---

## 📚 Additional resources

**Official documentation**
- [Strands Agents documentation](https://strandsagents.com/docs/)
- [Strands Agents observability and evaluation](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/)
- [Multi-agent patterns](https://strandsagents.com/docs/user-guide/concepts/multi-agent/multi-agent-patterns/)
- [Amazon Bedrock user guide](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock AgentCore developer guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AgentCore starter toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/user-guide/runtime/quickstart.html)
- [Model Context Protocol specification](https://modelcontextprotocol.io/docs/getting-started/intro)
- [AWS MCP servers](https://awslabs.github.io/mcp/)

**Code and samples**
- [Strands Agents SDK source](https://github.com/strands-agents/harness-sdk)
- [Strands Agents built-in tools](https://github.com/strands-agents/tools)
- [Strands Agents samples](https://github.com/strands-agents/samples)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for how to report a security issue.

## License

This library is licensed under the MIT-0 License. See [LICENSE](LICENSE).
