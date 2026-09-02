"""
STM 세션 간 대화 유지 테스트
"""
import os
import argparse
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")


def create_agent_with_memory(session_id: str, actor_id: str) -> Agent:
    """메모리가 연결된 에이전트 생성"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name="us-west-2"
    )
    
    return Agent(
        system_prompt="당신은 친절한 어시스턴트입니다. 이전 대화를 기억하고 맥락에 맞게 응답하세요.",
        session_manager=session_manager
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", default="persistent_session_001")
    parser.add_argument("--actor", default="user_bob")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    agent = create_agent_with_memory(args.session, args.actor)
    response = agent(args.message)
