import os
import argparse
import uuid
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig
)
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_LTM_ID", "your-ltm-memory-id")

# LTM 검색 설정
retrieval_config = {
    "/facts/{actorId}": RetrievalConfig(
        top_k=5,           # 상위 5개 결과
        relevance_score=0.5  # 관련성 점수 임계값
    )
}

def create_agent(session_id: str, actor_id: str) -> Agent:
    """메모리가 연결된 에이전트 생성"""

    print(f"Session ID: {session_id} | Actor ID: {actor_id}")
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id,
        retrieval_config=retrieval_config
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )

    return Agent(
        system_prompt="""당신은 사용자에 대해 학습하는 어시스턴트입니다.
        대화에서 중요한 사실을 기억하고, 이전에 학습한 정보를 활용하여 응답하세요.""",
        session_manager=session_manager
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["learn", "retrieve"], required=True,
                        help="learn: 사실 학습, retrieve: 학습된 사실 검색")
    parser.add_argument("--actor", default="user_charlie")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    # 매 실행마다 새로운 세션 ID 생성 (LTM이 세션 간 지속되는지 검증)
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    agent = create_agent(session_id, args.actor)
    agent(args.message)
    
    if args.mode == "learn":
        print("\n💡 LTM 생성은 비동기입니다. 1-2분 후 retrieve 모드로 테스트하세요.")
