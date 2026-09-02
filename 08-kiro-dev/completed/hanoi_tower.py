"""
하노이 탑 퍼즐 해결 Agent

이 모듈은 Strands SDK를 사용하여 하노이 탑 퍼즐을 해결하는 AI Agent를 구현합니다.
"""

import os
from typing import List, Tuple
from strands import Agent
from strands.tools import tool
from strands.telemetry import StrandsTelemetry


# OTLP 설정
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()


# 하노이 탑 상태를 저장하는 전역 변수
hanoi_state = {
    "A": [],
    "B": [],
    "C": [],
    "moves": []
}


@tool
def initialize_hanoi(n: int) -> str:
    """
    하노이 탑을 초기화합니다.
    
    Args:
        n: 디스크의 개수 (1-10)
        
    Returns:
        초기화 결과 메시지
    """
    if n < 1 or n > 10:
        return "디스크 개수는 1에서 10 사이여야 합니다."
    
    global hanoi_state
    hanoi_state = {
        "A": list(range(n, 0, -1)),  # [n, n-1, ..., 2, 1]
        "B": [],
        "C": [],
        "moves": []
    }
    
    return f"하노이 탑이 초기화되었습니다. 기둥 A에 {n}개의 디스크가 있습니다.\n현재 상태: {get_current_state()}"


@tool
def move_disk(from_rod: str, to_rod: str) -> str:
    """
    디스크를 한 기둥에서 다른 기둥으로 이동합니다.
    
    Args:
        from_rod: 출발 기둥 (A, B, C 중 하나)
        to_rod: 도착 기둥 (A, B, C 중 하나)
        
    Returns:
        이동 결과 메시지
    """
    global hanoi_state
    
    # 입력 검증
    if from_rod not in ["A", "B", "C"] or to_rod not in ["A", "B", "C"]:
        return "기둥은 A, B, C 중 하나여야 합니다."
    
    if from_rod == to_rod:
        return "같은 기둥으로는 이동할 수 없습니다."
    
    # 출발 기둥이 비어있는지 확인
    if not hanoi_state[from_rod]:
        return f"기둥 {from_rod}에 디스크가 없습니다."
    
    # 이동할 디스크
    disk = hanoi_state[from_rod][-1]
    
    # 도착 기둥에 더 작은 디스크가 있는지 확인
    if hanoi_state[to_rod] and hanoi_state[to_rod][-1] < disk:
        return f"더 큰 디스크를 더 작은 디스크 위에 놓을 수 없습니다. (디스크 {disk}를 기둥 {to_rod}의 디스크 {hanoi_state[to_rod][-1]} 위에 놓으려고 시도)"
    
    # 디스크 이동
    hanoi_state[from_rod].pop()
    hanoi_state[to_rod].append(disk)
    hanoi_state["moves"].append((from_rod, to_rod))
    
    move_count = len(hanoi_state["moves"])
    return f"이동 {move_count}: 디스크 {disk}를 기둥 {from_rod}에서 기둥 {to_rod}로 이동했습니다.\n현재 상태: {get_current_state()}"


@tool
def get_current_state() -> str:
    """
    현재 하노이 탑의 상태를 반환합니다.
    
    Returns:
        현재 상태를 나타내는 문자열
    """
    global hanoi_state
    
    state_str = f"""
기둥 A: {hanoi_state['A']}
기둥 B: {hanoi_state['B']}
기둥 C: {hanoi_state['C']}
총 이동 횟수: {len(hanoi_state['moves'])}
"""
    return state_str.strip()


@tool
def check_solution() -> str:
    """
    퍼즐이 해결되었는지 확인합니다.
    
    Returns:
        해결 여부 메시지
    """
    global hanoi_state
    
    # 모든 디스크가 기둥 C에 있고, 올바른 순서인지 확인
    if not hanoi_state["C"]:
        return "아직 해결되지 않았습니다. 기둥 C가 비어있습니다."
    
    if hanoi_state["A"] or hanoi_state["B"]:
        return "아직 해결되지 않았습니다. 모든 디스크를 기둥 C로 이동해야 합니다."
    
    # 디스크가 올바른 순서인지 확인 (큰 것부터 작은 것 순서)
    disks = hanoi_state["C"]
    if disks == sorted(disks, reverse=True):
        total_moves = len(hanoi_state["moves"])
        n = len(disks)
        optimal_moves = 2**n - 1
        return f"축하합니다! 퍼즐을 해결했습니다! 총 {total_moves}번 이동했습니다. (최적 해: {optimal_moves}번)"
    
    return "디스크 순서가 올바르지 않습니다."


@tool
def get_hint(n: int) -> str:
    """
    하노이 탑 퍼즐 해결을 위한 힌트를 제공합니다.
    
    Args:
        n: 디스크의 개수
        
    Returns:
        힌트 메시지
    """
    optimal_moves = 2**n - 1
    hint = f"""
하노이 탑 해결 전략:
1. n개의 디스크를 이동하려면 최소 {optimal_moves}번의 이동이 필요합니다.
2. 재귀적 접근: 
   - n-1개의 디스크를 보조 기둥으로 이동
   - 가장 큰 디스크를 목표 기둥으로 이동
   - n-1개의 디스크를 목표 기둥으로 이동
3. 규칙: 큰 디스크는 작은 디스크 위에 놓을 수 없습니다.
"""
    return hint.strip()


def main():
    """하노이 탑 Agent를 실행합니다."""
    
    # Agent 생성
    agent = Agent(
        name="hanoi_tower_solver",
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt="""당신은 하노이 탑 퍼즐을 해결하는 전문가 AI 어시스턴트입니다.

하노이 탑 규칙:
- 세 개의 기둥(A, B, C)이 있습니다
- 처음에 모든 디스크는 기둥 A에 크기 순서대로 쌓여 있습니다 (아래가 큰 디스크)
- 목표는 모든 디스크를 기둥 C로 이동하는 것입니다
- 한 번에 하나의 디스크만 이동할 수 있습니다
- 큰 디스크를 작은 디스크 위에 놓을 수 없습니다

사용자가 디스크 개수를 지정하면:
1. initialize_hanoi로 퍼즐을 초기화합니다
2. move_disk를 사용하여 디스크를 이동합니다
3. 각 이동 후 상태를 확인합니다
4. check_solution으로 완료 여부를 확인합니다

재귀적 알고리즘을 사용하여 최적의 해를 찾으세요.
각 단계를 명확하게 설명하면서 진행하세요.""",
        tools=[
            initialize_hanoi,
            move_disk,
            get_current_state,
            check_solution,
            get_hint
        ]
    )
    
    try:
        print("=" * 60)
        print("하노이 탑 퍼즐 해결 Agent")
        print("=" * 60)
        
        # 사용자 입력
        n = int(input("\n디스크 개수를 입력하세요 (1-10): "))
        
        if n < 1 or n > 10:
            print("디스크 개수는 1에서 10 사이여야 합니다.")
            return
        
        print(f"\n{n}개의 디스크로 하노이 탑 퍼즐을 시작합니다...\n")
        
        # Agent 실행
        response = agent(f"{n}개의 디스크로 하노이 탑 퍼즐을 해결해주세요. 각 단계를 설명하면서 진행해주세요.")
        
        print("\n" + "=" * 60)
        print("Agent 응답:")
        print("=" * 60)
        print(response)
        
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
