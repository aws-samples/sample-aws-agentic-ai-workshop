from strands import Agent
from strands_tools import calculator, current_time
from strands.models import BedrockModel

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

metrics = result.metrics

print("=== Basic Metrics ===")
print(f"Cycle count: {metrics.cycle_count}")
print(f"Cycle durations: {metrics.cycle_durations}")
print(f"Total duration: {sum(metrics.cycle_durations):.2f} seconds")

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

print("\n=== Tool Metrics ===")
for tool_name, tool_metric in metrics.tool_metrics.items():
    print(f"\nTool: {tool_name}")
    print(f"  Call count: {tool_metric.call_count}")
    print(f"  Success count: {tool_metric.success_count}")
    print(f"  Error count: {tool_metric.error_count}")
    print(f"  Total time: {tool_metric.total_time:.3f} seconds")
    if tool_metric.call_count > 0:
        print(f"  Avg time: {tool_metric.total_time / tool_metric.call_count:.3f} seconds")

# Get complete metrics summary
summary = result.metrics.get_summary()

print("\n=== Metrics Summary ===")
print(f"Total cycles: {summary['total_cycles']}")
print(f"Total duration: {summary['total_duration']:.2f} seconds")
print(f"Average cycle time: {summary['average_cycle_time']:.2f} seconds")
print(f"Accumulated usage: {summary['accumulated_usage']}")
print(f"Accumulated metrics: {summary['accumulated_metrics']}")
