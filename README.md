# Agentic AI on AWS Workshop

[한국어 README](README.ko.md)

Build an AI agent from scratch with the [Strands Agents SDK](https://strandsagents.com/docs/), then deploy and operate it with [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/).

<!-- ![Agentic AI on AWS Workshop](docs/images/agentic-ai-101.png) -->
<p align="center">
  <img src="docs/images/agentic-ai-learning-path.png" alt="Agentic AI on AWS, a complete learning path: chapter 1 getting started with Strands Agents, 2 building multi-agent systems, 3 serving agents in a chatbot application, 4 observability with Strands, 5 adding memory to your agent, 6 deploying agents to production, 7 observing agents in production" width="620">
</p>

- **How you learn:** each chapter has a `labs/` folder with empty files that you fill in yourself, and a `completed/` folder holding the reference implementation. You write the code, then compare against the reference.

- **Level:** 100 to 200 (beginner to intermediate). No prior agent or LLM experience required.

- **Duration:** about 2 hours for the required chapters, about 3 hours for all eight lab chapters.

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
| 00 | [Setup](dev/00-setup/README.md) | Python environment, AWS credentials, Bedrock model access | 10 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Required |
| 01 | [Single agent](dev/01-single-agent/README.md) | Agent with prompt, model, and tools. Bedrock Knowledge Base, MCP tools, self-improving agent | 30 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Required |
| 02 | [Multi-agent patterns](dev/02-multi-agents/README.md) | Agents-as-Tools, Swarm, and Graph | 30 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Required |
| 03 | [Chatbot application](dev/03-chatbot-app/README.md) | Streamlit chat UI with streaming and tool-call display | 10 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Optional |
| 04 | [Observability with Strands](dev/04-observability/README.md) | Metrics, logs, and OTLP traces to a local Jaeger | 30 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Optional |
| 05 | [Agent memory](dev/05-agent-memory/README.md) | Short-term and long-term memory with AgentCore Memory | 30 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | Required |
| 06 | [AgentCore Runtime](dev/06-agentcore-runtime/README.md) | Serverless deployment of the agent | 20 min | ![Advanced](https://img.shields.io/badge/-Advanced-red) | Required |
| 07 | [AgentCore Observability](dev/07-agentcore-observability/README.md) | CloudWatch GenAI Observability dashboard | 10 min | ![Advanced](https://img.shields.io/badge/-Advanced-red) | Required |
| 08 | [Developing with Kiro IDE](dev/08-kiro-dev/README.md) | Steering, MCP config, and spec-driven development | 10 min | ![Beginner](https://img.shields.io/badge/-Beginner-brightgreen) | Optional |

> [!IMPORTANT]
> Chapters 01, 02, 05, 06, and 07 form the core path. Chapters 03, 04, and 08 are self-contained and can be skipped. Chapter 07 is the one dependency worth noting: it reads telemetry from the agent you deploy in chapter 06.

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

If that prints an agent response, your environment is ready. Now open [00-setup/README.md](dev/00-setup/README.md) for the full setup notes, then start [chapter 01](dev/01-single-agent/README.md).

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
