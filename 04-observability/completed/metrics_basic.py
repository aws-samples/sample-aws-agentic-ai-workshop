from strands import Agent
from strands_tools import calculator, current_time
from strands.models import BedrockModel

model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
agent = Agent(model=model, tools=[calculator, current_time])
result = agent([
    {
        "role": "user",
        "content": [
            {"text": "125 * 37은 얼마야? 그리고 지금 몇 시야?"},
            {"cachePoint": {"type": "default"}}
        ]
    }
])

metrics = result.metrics

print("=== 기본 메트릭 ===")
print(f"사이클 수: {metrics.cycle_count}")
print(f"사이클별 소요시간: {metrics.cycle_durations}")
print(f"총 소요시간: {sum(metrics.cycle_durations):.2f}")

print("\n=== 토큰 사용량 ===")
usage = metrics.accumulated_usage
print(f"입력 토큰: {usage.get('inputTokens', 0)}")
print(f"출력 토큰: {usage.get('outputTokens', 0)}")
print(f"총 토큰: {usage.get('totalTokens', 0)}")

# 캐시 메트릭
if 'cacheReadInputTokens' in usage:
    print(f"캐시 읽기 토큰: {usage['cacheReadInputTokens']}")
if 'cacheWriteInputTokens' in usage:
    print(f"캐시 쓰기 토큰: {usage['cacheWriteInputTokens']}")

print("\n=== 도구 메트릭 ===")
for tool_name, tool_metric in metrics.tool_metrics.items():
    print(f"\n도구: {tool_name}")
    print(f"  호출 횟수: {tool_metric.call_count}")
    print(f"  성공 횟수: {tool_metric.success_count}")
    print(f"  실패 횟수: {tool_metric.error_count}")
    print(f"  총 실행시간: {tool_metric.total_time:.3f}초")
    if tool_metric.call_count > 0:
        print(f"  평균 실행시간: {tool_metric.total_time / tool_metric.call_count:.3f}초")

# 전체 메트릭 요약 가져오기
summary = result.metrics.get_summary()

print("\n=== 메트릭 요약 ===")
print(f"총 사이클: {summary['total_cycles']}")
print(f"총 소요시간: {summary['total_duration']:.2f}초")
print(f"평균 사이클 시간: {summary['average_cycle_time']:.2f}초")
print(f"누적 사용량: {summary['accumulated_usage']}")
print(f"누적 메트릭: {summary['accumulated_metrics']}")
