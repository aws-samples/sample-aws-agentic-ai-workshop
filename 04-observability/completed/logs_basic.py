"""
Strands SDK 로깅 설정 예제
- 루트 로거로 전체 SDK 로그 활성화
- 특정 모듈별 로그 레벨 조정 가능
"""
import logging
from strands import Agent
from strands_tools import calculator

# 1. 루트 로거 설정 - 전체 SDK 로그 활성화
logging.getLogger("strands").setLevel(logging.DEBUG)

# 2. 특정 모듈만 로그 레벨 조정 (선택적)
# logging.getLogger("strands.tools.registry").setLevel(logging.WARNING)  # 도구 등록 로그 숨기기
# logging.getLogger("strands.models").setLevel(logging.INFO)             # 모델 로그만 INFO 이상

# 3. 로그 출력 포맷 설정
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# 에이전트 실행
agent = Agent(tools=[calculator])
result = agent("125 * 37은 얼마야?")
