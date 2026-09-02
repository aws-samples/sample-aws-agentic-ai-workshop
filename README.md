# Agentic AI 101 on AWS

[한국어 README](README.ko.md)

Build an AI agent from scratch with the [Strands Agents SDK](https://strandsagents.com/latest/), then deploy and operate it with [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/).

This is a hands-on workshop. Each chapter has a `labs/` folder with empty files that you fill in yourself, and a `completed/` folder holding the reference implementation. You learn by typing the code, then comparing against the reference.

![Agentic AI 101 on AWS](docs/images/agentic-ai-101.png)

**Level:** 100 to 200 (beginner to intermediate). No prior agent or LLM experience required.
**Duration:** about 3 hours for the required chapters.

---

## Chapters

| # | Chapter | What you build | Type |
|---|---------|----------------|------|
| 00 | [Setup](00-setup/README.md) | Python environment, AWS credentials, Bedrock model access | Required |
| 01 | [Single agent](01-single-agent/README.md) | Agent with prompt, model, and tools. Bedrock Knowledge Base, MCP tools, self-improving agent | Required |
| 02 | [Multi-agent patterns](02-multi-agents/README.md) | Agents-as-Tools, Swarm, and Graph | Required |
| 03 | [Chatbot application](03-chatbot-app/README.md) | Streamlit chat UI with streaming and tool-call display | Optional |
| 04 | [Observability with Strands](04-observability/README.md) | Metrics, logs, and OTLP traces to a local Jaeger | Optional |
| 05 | [Agent memory](05-agent-memory/README.md) | Short-term and long-term memory with AgentCore Memory | Required |
| 06 | [AgentCore Runtime](06-agentcore-runtime/README.md) | Serverless deployment of the agent | Required |
| 07 | [AgentCore Observability](07-agentcore-observability/README.md) | CloudWatch GenAI Observability dashboard | Required |
| 08 | [Developing with Kiro IDE](08-kiro-dev/README.md) | Steering, MCP config, and spec-driven development | Optional |

> [!TIP]
> Chapters 01, 02, 05, 06, and 07 form the core path. Chapters 03, 04, and 08 are self-contained and can be skipped.

---

## Quick start

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

## Models and region

The labs run against Amazon Bedrock in **`us-west-2`**. Enable model access for these before you start:

| Model ID | Used in |
|---|---|
| `us.anthropic.claude-sonnet-4-20250514-v1:0` | Chapters 01 to 06 |
| `us.anthropic.claude-sonnet-4-6` | Chapter 01 self-improving agent labs, chapter 02 |
| `us.amazon.nova-pro-v1:0` | Chapter 04, metrics lab |

Enable them in the [Bedrock console](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess) under **Model access**. Cross-region inference profiles (the `us.` prefix) require access in the destination regions of the profile, which the console handles for you.

---

## Repository layout

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

## Cost and cleanup

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

## Reference

- [Strands Agents SDK documentation](https://strandsagents.com/latest/documentation/)
- [Multi-agent patterns](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/)
- [Amazon Bedrock user guide](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock AgentCore developer guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWS MCP servers](https://awslabs.github.io/mcp/)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for how to report a security issue.

## License

This library is licensed under the MIT-0 License. See [LICENSE](LICENSE).
