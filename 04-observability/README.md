# 4. Agent Observability (Strands Observability)

In this chapter, you will learn about the Agent Observability features provided by the Strands SDK. We'll cover Metrics, Logs, and Traces, which are essential for monitoring and debugging agent behavior.

> [!NOTE]
> **Optional Chapter**
> This chapter is **optional**. Proceed if you have enough time. It does not affect the core workshop flow, so you can skip it and move to the next chapter.

> [!TIP]
> **If you're using AgentCore Runtime**
> This chapter covers how to manually configure the observability features provided by the Strands SDK. This approach is suitable if you're running Strands agents in a self-managed environment. If you're running agents on **Amazon Bedrock AgentCore Runtime**, check out [07-agentcore-observability](../07-agentcore-observability/README.md) to see how you can collect metrics, logs, and traces in an integrated way without setting up a separate pipeline.

> [!NOTE]
> **Prerequisites**
> - Environment set up per [00-setup](../00-setup/README.md). The `strands-agents[otel]` extra needed for trace export is already included in `00-setup/pyproject.toml`.
> - Amazon Bedrock model access for `us.amazon.nova-pro-v1:0` (Metrics lab) and `us.anthropic.claude-sonnet-4-20250514-v1:0` (Traces labs)
> - **Docker running locally**, for the OTLP section only (Traces Lab 2 and Lab 3). The AWS-hosted VS Code Server used in the workshop has Docker preinstalled and running. On your own laptop you may need to install Docker Desktop first. The Metrics, Logs, and console-exporter Traces labs do not need Docker.

**What you will learn**
- The `EventLoopMetrics` data structure and how to read agent metrics (tokens, cycles, per-tool stats)
- How to configure the `strands` logger hierarchy and per-module log levels
- How to instrument an agent with OpenTelemetry and print spans to the console
- How to run an ADOT Collector plus Jaeger with Docker and view traces in the Jaeger UI

**Estimated time:** ~30 minutes

## Files in this chapter

The lab pattern in this repo: you write code into the empty file under `labs/`, and `completed/` holds the reference answer to compare against.

| File | Purpose |
|---|---|
| `labs/metrics_basic.py` | (empty) you write this in the Metrics lab |
| `labs/logs_basic.py` | (empty) you write this in the Logs lab |
| `labs/traces_console.py` | (empty) you write this in Traces Lab 1 |
| `labs/traces_otlp.py` | (empty) you write this in Traces Lab 3 |
| `completed/metrics_basic.py` | reference answer |
| `completed/logs_basic.py` | reference answer |
| `completed/traces_console.py` | reference answer |
| `completed/traces_otlp.py` | reference answer |
| `docker/enable-otlp.sh` | starts the Jaeger and ADOT Collector containers |
| `docker/disable-otlp.sh` | stops and removes those containers and the Docker network |
| `docker/otel-config.yaml` | ADOT Collector config, mounted into the collector container |

> [!NOTE]
> The files under `completed/` use Korean prompt and print strings, matching the Korean guide. The English code blocks below are translations of the same code, so your `labs/` file will differ from `completed/` only in those strings.

All commands below assume you are at the repo root with the uv environment from `00-setup` available.

---

## Why Agent Observability?

Is the AI agent we developed actually behaving as expected? The output of language models that agents depend on is non-deterministic, and we cannot always trust the results of the numerous tools they rely on. Therefore, systematic observability is recommended to understand agent behavior and diagnose problems.

### Problems Solved by Observability

- Token costs higher than expected: monitor token usage with **Metrics**
- Certain tools fail frequently: check success/failure rates by tool with **Metrics**
- Response time is slow: analyze latency with **Metrics**
- Need agent internal operation history: check the detailed execution process with **Logs** or **Traces**

### Three Telemetry Primitives

Strands SDK provides 3 telemetry primitives to easily enhance agent observability.

**1. Metrics** are **quantitative measurements** that provide numerical values for agent performance and resource usage. Metrics are available at the agent lifecycle level, per agent invocation, or per event loop cycle.

- Event loop cycle count and duration per cycle
- Token usage (input/output/cache)
- Response latency
- Per-tool call count, success/failure count, total execution time

**2. Logs** are **text-based records** that describe detailed agent internal operations.

- Tool registration and validation process
- Model calls and responses
- Detailed information on errors
- Detailed execution flow for debugging

**3. Traces** are **distributed tracing** records that hierarchically visualize the entire path where a request is executed.

- Full flow from agent invocation to response
- Reasoning process for each cycle
- Timing of model calls and tool executions
- Span structure connected by parent-child relationships

**References**

- [Strands Agents - Observability](https://strandsagents.com/latest/user-guide/observability-evaluation/observability/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

---

## Metrics

In this lab, you will learn about the **event loop metrics** data structure provided by Strands SDK and how to check agent metrics.

**Best Practices**

1. **Monitor Token Usage**: Track token consumption to optimize costs and stay within limits.
2. **Analyze Tool Performance**: Identify tools with high error rates or long execution times.
3. **Track Cycle Efficiency**: Agents requiring many cycles may benefit from improved prompting.
4. **Benchmark Latency**: Establish performance baselines using latency metrics.

### Event Loop Metrics

Event loop metrics aggregate all performance data generated during the execution of an agent loop. The **agent invocation result** includes not only the agent's natural language response but also **metrics**.

> [!NOTE]
> **Developer Tips**
>
> The agent invocation result is represented by the `AgentResult` class. Within it, you can find the `metrics` member, which is an instance of `EventLoopMetrics`.

```python
from strands import Agent
from strands_tools import calculator

agent = Agent(tools=[calculator])
result = agent("What is 125 * 37?")

print(result.metrics) # Access metrics
```

Output:

```
EventLoopMetrics(
    cycle_count=2,
    cycle_durations=[1.0775706768035889],
    tool_metrics={
        'calculator': ToolMetrics(
            tool={
                'toolUseId': 'tooluse_uJvpOKTaJX7azOVIx8w3wk',
                'name': 'calculator',
                'input': {'expression': '125 * 37'}
            },
            call_count=1,
            success_count=1,
            error_count=0,
            total_time=0.007710933685302734
        )
    },
    traces=[
        <strands.telemetry.metrics.Trace object>,
        <strands.telemetry.metrics.Trace object>
    ],
    accumulated_usage={
        'inputTokens': 3109,
        'outputTokens': 73,
        'totalTokens': 3182
    },
    accumulated_metrics={
        'latencyMs': 2018
    }
)
```

For more details, refer to the [Python SDK](https://github.com/strands-agents/sdk-python/blob/main/src/strands/telemetry/metrics.py).

### Lab: Collecting Metrics

**1.** Open the empty file `04-observability/labs/metrics_basic.py`.

**2.** Import the required libraries.

```python
from strands import Agent
from strands_tools import calculator, current_time
from strands.models import BedrockModel
```

**3.** Create a model and agent, then execute a query.

```python
model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
agent = Agent(model=model, tools=[calculator, current_time])
result = agent([
    {
        "role": "user",
        "content": [
            {"text": "What is 125 * 37? Also, what time is it now?"},
            {"cachePoint": {"type": "default"}}
        ]
    }
])
```

> [!NOTE]
> **Agent Invocation Methods**
> Strands agents support various input formats.
> - String: `agent("hello!")`
> - ContentBlock list: `agent([{"text": "hello"}, {"image": {...}}])`
> - Message list: `agent([{"role": "user", "content": [{"text": "hello"}]}])`
> - No input: `agent()`, which uses existing conversation history
>
> In this lab, we use the Message list format with `cachePoint` to trigger Amazon Nova model's [Prompt Caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) behavior.

**4.** Check basic metrics.

```python
metrics = result.metrics

print("=== Basic Metrics ===")
print(f"Cycle count: {metrics.cycle_count}")
print(f"Cycle durations: {metrics.cycle_durations}")
print(f"Total duration: {sum(metrics.cycle_durations):.2f} seconds")
```

**5.** Check token usage.

```python
print("\n=== Token Usage ===")
usage = metrics.accumulated_usage
print(f"Input tokens: {usage.get('inputTokens', 0)}")
print(f"Output tokens: {usage.get('outputTokens', 0)}")
print(f"Total tokens: {usage.get('totalTokens', 0)}")

# Cache metrics
if 'cacheReadInputTokens' in usage:
    print(f"Cache read tokens: {usage['cacheReadInputTokens']}")
if 'cacheWriteInputTokens' in usage:
    print(f"Cache write tokens: {usage['cacheWriteInputTokens']}")
```

**6.** Check tool metrics.

```python
print("\n=== Tool Metrics ===")
for tool_name, tool_metric in metrics.tool_metrics.items():
    print(f"\nTool: {tool_name}")
    print(f"  Call count: {tool_metric.call_count}")
    print(f"  Success count: {tool_metric.success_count}")
    print(f"  Error count: {tool_metric.error_count}")
    print(f"  Total time: {tool_metric.total_time:.3f} seconds")
    if tool_metric.call_count > 0:
        print(f"  Avg time: {tool_metric.total_time / tool_metric.call_count:.3f} seconds")
```

**7.** Run the code.

```bash
uv run python 04-observability/labs/metrics_basic.py
```

> [!WARNING]
> **Try running the lab code multiple times.**
> - **First run**: `cacheWriteInputTokens` will show a value (cache stored)
> - **Subsequent runs**: `cacheReadInputTokens` will show a value (cache hit)
>
> Cache hits reduce input token costs by 90%. System prompts and tool definitions are cached, significantly reducing costs for repeated calls.

**8.** Execution result.

```
Tool #1: calculator

Tool #2: current_time
125 * 37 is 4625. And the current time is February 6, 2026, 15:28:18 UTC.
=== Basic Metrics ===
Cycle count: 2
Cycle durations: [1.0885756015777588]
Total duration: 1.09

=== Token Usage ===
Input tokens: 265
Output tokens: 238
Total tokens: 4891
Cache read tokens: 4388 #On 2nd run
Cache write tokens: 2109 #On 1st run

=== Tool Metrics ===

Tool: calculator
  Call count: 1
  Success count: 1
  Error count: 0
  Total time: 0.006 seconds
  Avg time: 0.006 seconds

Tool: current_time
  Call count: 1
  Success count: 1
  Error count: 0
  Total time: 0.006 seconds
  Avg time: 0.006 seconds
```

### Using get_summary()

`EventLoopMetrics` provides a convenient `get_summary()` method that returns all metrics as a structured dictionary. Append this to your file and run it again.

```python
# Get complete metrics summary
summary = result.metrics.get_summary()

print("\n=== Metrics Summary ===")
print(f"Total cycles: {summary['total_cycles']}")
print(f"Total duration: {summary['total_duration']:.2f} seconds")
print(f"Average cycle time: {summary['average_cycle_time']:.2f} seconds")
print(f"Accumulated usage: {summary['accumulated_usage']}")
print(f"Accumulated metrics: {summary['accumulated_metrics']}")
```

<details>
<summary>Appendix: EventLoopMetrics structure</summary>

`EventLoopMetrics` has a hierarchical structure. The following table shows all attributes by level:

| Level | Class | Attribute | Type | Description |
|-------|-------|-----------|------|-------------|
| **1. Top Level** | `EventLoopMetrics` | `cycle_count` | `int` | Number of event loop cycles executed |
| | | `cycle_durations` | `list[float]` | Duration of each cycle (seconds) |
| | | `tool_metrics` | `dict[str, ToolMetrics]` | Metrics per tool (by tool name) |
| | | `traces` | `list[Trace]` | List of execution traces |
| | | `accumulated_usage` | `Usage` | Total accumulated token usage |
| | | `accumulated_metrics` | `Metrics` | Total accumulated performance metrics |
| | | `agent_invocations` | `list[AgentInvocation]` | List of agent invocations |
| **2. Agent Invocation** | `AgentInvocation` | `cycles` | `list[EventLoopCycleMetric]` | List of cycles for this invocation |
| | | `usage` | `Usage` | Accumulated token usage for this invocation |
| **3. Cycle** | `EventLoopCycleMetric` | `event_loop_cycle_id` | `str` | Unique cycle ID |
| | | `usage` | `Usage` | Token usage for this cycle |
| **4. Tool Metrics** | `ToolMetrics` | `tool` | `ToolUse` | Tool information being tracked |
| | | `call_count` | `int` | Number of tool calls |
| | | `success_count` | `int` | Number of successful calls |
| | | `error_count` | `int` | Number of failed calls |
| | | `total_time` | `float` | Total execution time (seconds) |
| **5. Trace** | `Trace` | `id` | `str` | Unique trace ID (UUID) |
| | | `name` | `str` | Operation name (human-readable) |
| | | `raw_name` | `str \| None` | System-level name |
| | | `parent_id` | `str \| None` | Parent trace ID |
| | | `start_time` | `float` | Start timestamp |
| | | `end_time` | `float \| None` | End timestamp |
| | | `children` | `list[Trace]` | List of child traces |
| | | `metadata` | `dict[str, Any]` | Additional context information |
| | | `message` | `Message \| None` | Associated message |

**Usage type**

| Attribute | Description |
|-----------|-------------|
| `inputTokens` | Number of input tokens |
| `outputTokens` | Number of output tokens |
| `totalTokens` | Total number of tokens |
| `cacheReadInputTokens` | Cache read input tokens (optional) |
| `cacheWriteInputTokens` | Cache write input tokens (optional) |

**Metrics type**

| Attribute | Description |
|-----------|-------------|
| `latencyMs` | Latency in milliseconds |
| `timeToFirstByteMs` | Time to first byte (optional) |

**Token usage aggregation hierarchy**

Token usage can be tracked at three levels:

```
Total accumulated (accumulated_usage)
    └── Per agent invocation (agent_invocations[].usage)
            └── Per cycle (agent_invocations[].cycles[].usage)
```

This structure allows you to analyze token consumption from overall totals down to individual cycles.

</details>

---

## Logs

In this lab, you will learn how to configure logging in the Strands SDK.

Strands SDK uses Python's standard `logging` module. Each module is configured as a child of the `strands` root logger, allowing you to adjust log levels for the entire SDK or specific modules individually.

```
strands                              # Root logger - controls entire SDK logging
├── strands.agent                    # Agent creation and execution
├── strands.models                   # Model interactions
│   └── strands.models.bedrock       # Bedrock model calls
├── strands.tools                    # Tool-related
│   └── strands.tools.registry       # Tool registration and validation
└── strands.event_loop               # Event loop
    └── strands.event_loop.event_loop
```

### Lab: Configuring Logging

**1.** Write the following into `04-observability/labs/logs_basic.py`.

```python
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
```

**2.** Run the code.

```bash
uv run python 04-observability/labs/logs_basic.py
```

You can see detailed logs of tool registration, model calls, and event loop processing like this:

```
# Bedrock model initialization
DEBUG | strands.models.bedrock | config=<{'model_id': '...'}> | initializing
DEBUG | strands.models.bedrock | region=<ap-northeast-2> | bedrock client created

# Tool registration process
DEBUG | strands.tools.loader | tool_name=<calculator>, module=<calculator> | loading tools from module
DEBUG | strands.tools.registry | tool_name=<calculator>, tool_type=<function>, is_dynamic=<False> | registering tool
DEBUG | strands.tools.registry | tool_count=<1> | tools configured

# Model invocation and response
DEBUG | strands.event_loop.streaming | model=<...> | streaming messages
DEBUG | strands.models.bedrock | invoking model
DEBUG | strands.models.bedrock | got response from model

# Tool execution
DEBUG | strands.tools.executors._executor | tool_use=<{'name': 'calculator', 'input': {'expression': '125 * 37'}}> | streaming
```

Try enabling the commented lines to adjust log levels for specific modules.

---

## Traces

In this lab, you will learn how to trace agent execution using Strands SDK's OpenTelemetry integration.

**Best Practices**

1. **Appropriate Detail Level**: Capture sufficient information while avoiding excessive data
2. **Add Business Context**: Include business-related attributes like customer ID or transaction value
3. **Implement Sampling**: Reduce data volume with sampling in high-volume applications
4. **Protect Sensitive Data**: Prevent capturing PII or sensitive information in traces
5. **Correlate with Logs and Metrics**: Use trace IDs to link with corresponding logs

### OTLP (OpenTelemetry Protocol)

OTLP is a standard protocol defined by OpenTelemetry for transmitting telemetry data (traces, metrics, logs). It supports two transport methods, gRPC and HTTP. In this lab, we use **HTTP on port 4318**.

<img src="../docs/images/c4-traces-pipeline-architecture.png" alt="Trace pipeline architecture" width="800">

Trace data is collected and visualized through three components. First, the **Strands Agent** generates trace data during agent execution. The generated traces can be sent to OTLP-compatible tools, and today we use the **ADOT Collector**. ADOT acts as an intermediate collector that receives data via OTLP protocol on HTTP port 4318 and forwards it to backend systems. Finally, **Jaeger** stores the traces and provides visualized trace information through its web UI on port 16686.

| Component | Role | Endpoint |
|-----------|------|----------|
| **Strands Agent** | Generate trace data | - |
| **ADOT Collector** | Collect and forward traces | `localhost:4318` |
| **Jaeger** | Store and visualize traces | UI: `localhost:16686` |

> [!NOTE]
> [ADOT (AWS Distro for OpenTelemetry)](https://aws-otel.github.io/docs/getting-started/collector) is an AWS-managed OpenTelemetry distribution that integrates easily with AWS services. While Strands SDK can send trace data directly to Jaeger, using ADOT as an intermediary makes it easy to integrate with multiple backends like AWS X-Ray or CloudWatch in production environments.

### Trace Structure

Tracing hierarchically visualizes the entire agent execution path. Here are the characteristics of information instrumented by Strands SDK using OpenTelemetry standards:

- **Agent Lifecycle**: From initial prompt to final response
- **Individual LLM Calls**: Prompts, completions, token usage
- **Tool Execution**: Tools called, parameters, results
- **Performance Measurement**: Identify bottlenecks and optimization opportunities

The trace structure instrumented with Strands looks like this:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Strands Agent                                                        │
│ - gen_ai.system: strands-agents                                      │
│ - gen_ai.agent.name: <agent name>                                    │
│ - gen_ai.user.message: <user query>                                  │
│ - gen_ai.choice: <agent response>                                    │
│ - gen_ai.usage.total_tokens: <number>                                │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ Cycle <cycle-id>                                               │  │
│  │ - event_loop.cycle_id: <cycle identifier>                      │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐  │  │
│  │  │ Chat                                                     │  │  │
│  │  │ - gen_ai.request.model: <model identifier>               │  │  │
│  │  │ - gen_ai.usage.input_tokens: <number>                    │  │  │
│  │  │ - gen_ai.usage.output_tokens: <number>                   │  │  │
│  │  └──────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐  │  │
│  │  │ Execute Tool: <tool name>                                │  │  │
│  │  │ - gen_ai.tool.name: <tool name>                          │  │  │
│  │  │ - gen_ai.tool.call.id: <tool use identifier>             │  │  │
│  │  │ - tool.status: <execution status>                        │  │  │
│  │  └──────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

- **Agent Span**: Top-level span representing the entire agent invocation
- **Cycle Spans**: Child spans for each event loop cycle
- **Model Invoke Spans**: Model invocation spans
- **Tool Spans**: Tool execution spans

### Python Package Installation

To enable OTEL export supported by Strands SDK, install Strands Agents with the `otel` extra dependency. The environment from [00-setup](../00-setup/README.md) already pins `strands-agents[otel]`, so you can skip this if you followed that chapter.

```bash
pip install 'strands-agents[otel]'
```

Or if using `uv`:

```bash
uv add 'strands-agents[otel]'
```

### Lab 1: Console Tracing

**1.** Open the empty file `04-observability/labs/traces_console.py`.

**2.** Import the required libraries.

```python
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator
```

**3.** Set up telemetry with console export.

```python
# Create StrandsTelemetry instance
strands_telemetry = StrandsTelemetry()

# Output traces to console
strands_telemetry.setup_console_exporter()
```

**4.** Create and run the agent.

```python
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="You are a helpful AI assistant.",
    tools=[calculator]
)

response = agent("What is 125 * 37?")
print(response)
```

**5.** Run the code.

```bash
uv run python 04-observability/labs/traces_console.py
```

You can see span information output to the console. No Docker or collector is required for this lab.

### Lab 2: OTLP Tracing Environment Setup

Now let's send agent call traces using the OpenTelemetry protocol and visualize them. To set up this pipeline, we will run ADOT and Jaeger as **Docker containers**.

- The ADOT container receives OTLP traces sent by Strands applications and fans them out to Jaeger in the backend.
- The Jaeger container receives OTLP traces and visualizes them in the UI.

> [!WARNING]
> **Docker is required from here on.** The AWS-hosted VS Code Server used in the workshop has Docker preinstalled and running. If you are working on your own laptop, install and start Docker Desktop (or an equivalent runtime) before continuing. Check with `docker ps`. If Docker is not available, you can stop after Lab 1 or use the managed alternative in [07-agentcore-observability](../07-agentcore-observability/README.md).

**1.** A script is prepared to set up the OTLP pipeline.

```bash
cd 04-observability/docker
chmod +x *.sh
./enable-otlp.sh
cd -
```

`enable-otlp.sh` runs the following, in order:

1. `docker network create tracing-net`, a user-defined bridge network so the two containers can reach each other by name.
2. Starts Jaeger: `docker run -d --name jaeger --network tracing-net -e COLLECTOR_OTLP_ENABLED=true -p 16686:16686 jaegertracing/jaeger:latest`. Only the UI port 16686 is published to the host. Jaeger's own OTLP port stays inside the Docker network.
3. Waits 5 seconds for Jaeger to become ready.
4. Starts the collector: `docker run -d --name adot --network tracing-net -v "<docker dir>/otel-config.yaml:/etc/otel-config.yaml" -p 4318:4318 amazon/aws-otel-collector:latest --config=/etc/otel-config.yaml`. Port 4318 is published to the host, which is the endpoint your agent sends to.

`docker/otel-config.yaml` is the mounted collector config: an `otlp` receiver listening on HTTP `0.0.0.0:4318`, and a traces pipeline that exports to `otlphttp` at `http://jaeger:4318` (resolved over `tracing-net`) plus a `debug` exporter with detailed verbosity, which is why the collector logs each span it receives.

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlphttp:
    endpoint: http://jaeger:4318
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlphttp, debug]
```

Check the output after running the script.

```
🔧 Creating Docker network...
🚀 Starting Jaeger...
⏳ Waiting for Jaeger to be ready (5 seconds)...
🚀 Starting ADOT Collector...

✅ Tracing stack started successfully!

📊 Jaeger UI: http://localhost:16686
📡 OTLP Endpoint: localhost:4318 (HTTP)
```

> [!NOTE]
> The last line the script prints refers to `./stop-tracing.sh`. That file does not exist in this repo. Use `./disable-otlp.sh` instead (see [Cleanup](#cleanup)).

**2.** Set environment variables.

Store the ADOT container's HTTP/4318 (OTLP) endpoint information in an environment variable. This tells the Strands application where to send traces.

```bash
# Specify custom OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
```

**3.** Verify Jaeger UI is working properly.

Access `http://localhost:16686/` in your browser. Since there's no trace data yet, an empty screen will be displayed.

<img src="../docs/images/c4-jaeger-ui-empty.png" alt="Jaeger UI Empty" width="756">

> [!NOTE]
> **Workshop Jaeger access information**
> In AWS Workshop environments where you are using the hosted VS Code Server, use the following URL to access the Jaeger UI:
>
> `https://<CodeServer domain>/proxy/16686/`

<img src="../docs/images/c4-jaeger-url-sample.png" alt="Jaeger URL Sample" width="756">

### Lab 3: Sending Traces to the OTLP Endpoint

Now that the tracing stack is ready, let's send traces from the agent.

**1.** Write the following into `04-observability/labs/traces_otlp.py`.

```python
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
```

**2.** Run the code.

```bash
uv run python 04-observability/labs/traces_otlp.py
```

**3.** Check traces in the Jaeger UI.

Access `http://localhost:16686/` in your browser. Wait a moment for traces to arrive.

1. Select `strands-agents` from the **Service** dropdown
2. Click the **Find Traces** button
3. Click on a trace to view detailed span information

<img src="../docs/images/c4-jaeger-ui-search.png" alt="Jaeger UI trace search" width="756">
<img src="../docs/images/c4-jaeger-span-chat.png" alt="Jaeger span detail for a Chat span" width="756">

<details>
<summary>Appendix: span attributes and other export options</summary>

**Agent-level attributes**

| Attribute | Description |
|-----------|-------------|
| `gen_ai.system` | Agent system identifier ("strands-agents") |
| `gen_ai.agent.name` | Agent name |
| `gen_ai.user.message` | User's initial prompt |
| `gen_ai.choice` | Agent's final response |
| `gen_ai.request.model` | Model ID used by the agent |
| `gen_ai.usage.total_tokens` | Total token usage |

**Tool-level attributes**

| Attribute | Description |
|-----------|-------------|
| `gen_ai.tool.name` | Name of the tool called |
| `gen_ai.tool.call.id` | Unique identifier for the tool call |
| `tool.status` | Execution status (success/error) |
| `gen_ai.choice` | Formatted tool result |

**Custom attributes**

You can add custom attributes when creating an agent. These attributes are included in all spans and can be used for filtering and analysis.

```python
agent = Agent(
    system_prompt="You are a helpful assistant.",
    tools=[calculator],
    trace_attributes={
        "session.id": "abc-1234",
        "user.id": "user@example.com",
        "tags": [
            "Agent-SDK",
            "Production",
            "Observability",
        ]
    },
)
```

**Sampling control**

In high-volume applications, you can implement sampling to reduce data volume.

```python
import os

# Example: Sample 10% of traces
os.environ["OTEL_TRACES_SAMPLER"] = "traceidratio"
os.environ["OTEL_TRACES_SAMPLER_ARG"] = "0.1"
```

**Saving traces to a file**

```python
from os import linesep
from strands.telemetry import StrandsTelemetry

strands_telemetry = StrandsTelemetry()

# Save telemetry to local file
logfile = open("traces.jsonl", "wt")
strands_telemetry.setup_console_exporter(
    out=logfile,
    formatter=lambda span: span.to_json() + linesep,
)

# ... agent execution code ...

logfile.close()
```

</details>

---

## Cleanup

When you're done with the lab, shut down the tracing stack. This is only needed if you ran Lab 2.

```bash
cd 04-observability/docker
./disable-otlp.sh
cd -
```

`disable-otlp.sh` runs `docker stop adot jaeger`, then `docker rm adot jaeger`, then `docker network rm tracing-net`. Every command is suffixed with `2>/dev/null || true`, so the script succeeds even if some of the containers or the network are already gone. Nothing is left running on ports 4318 or 16686 afterwards.

If you exported `OTEL_EXPORTER_OTLP_ENDPOINT` in your shell, unset it so later chapters do not try to send traces to a stopped collector:

```bash
unset OTEL_EXPORTER_OTLP_ENDPOINT
```

This chapter creates no billable AWS resources beyond the Bedrock model invocations made by the labs.

## Troubleshooting

**`Connection refused` or `Failed to export spans` on port 4318**

The ADOT Collector is not running. Confirm with `docker ps`, which should list containers named `adot` and `jaeger`. If they are missing, start them again:

```bash
cd 04-observability/docker && ./enable-otlp.sh && cd -
```

Note that the agent keeps working even when export fails: the SDK logs the export error and continues, so a successful agent response does not mean traces arrived.

**Jaeger UI is empty, or `strands-agents` is not in the Service dropdown**

Spans are exported in batches, and the final flush happens when the Python process exits. Let `traces_otlp.py` finish, wait a few seconds, then reload the Jaeger UI and click **Find Traces** again. Also make sure you widen the **Lookback** window if your run was a while ago. You can confirm the collector received data by checking its log, since `otel-config.yaml` enables the `debug` exporter:

```bash
docker logs adot | tail -50
```

**`docker: command not found`, or Docker is not running**

The OTLP labs need a local Docker runtime. The AWS-hosted VS Code Server used in the workshop has Docker preinstalled, but a personal laptop may not. Install Docker Desktop and start it, then re-run `enable-otlp.sh`. If you cannot install Docker, do Lab 1 (console exporter) only, or use the managed pipeline in [07-agentcore-observability](../07-agentcore-observability/README.md), which needs no local collector.

**`Conflict. The container name "/jaeger" is already in use`**

A previous run left the containers behind. Run `./disable-otlp.sh` first, then `./enable-otlp.sh` again.

**`404` errors mentioning `/v1/metrics` in the console output**

`traces_otlp.py` also enables an OTLP metrics exporter through `setup_meter(enable_otlp_exporter=True)`, but `otel-config.yaml` defines a traces pipeline only. Metric export to the collector fails while traces work normally. This is expected with the provided config, and the console exporter still prints the metrics locally.

---
Prev: [3. Chatbot App](../03-chatbot-app/README.md) | Next: [5. Agent Memory](../05-agent-memory/README.md)
