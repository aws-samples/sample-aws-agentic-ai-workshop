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

# LTM retrieval configuration
retrieval_config = {
    "/facts/{actorId}": RetrievalConfig(
        top_k=5,           # Top 5 results
        relevance_score=0.5  # Relevance score threshold
    )
}

def create_agent(session_id: str, actor_id: str) -> Agent:
    """Create an agent with memory connected"""

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
        system_prompt="""You are an assistant that learns about users.
        Remember important facts from conversations and use previously learned information in your responses.""",
        session_manager=session_manager
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["learn", "retrieve"], required=True,
                        help="learn: Learn facts, retrieve: Retrieve learned facts")
    parser.add_argument("--actor", default="user_charlie")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    # Generate a new session ID for each run (to verify LTM persists across sessions)
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    agent = create_agent(session_id, args.actor)
    agent(args.message)
    
    if args.mode == "learn":
        print("\n💡 LTM creation is asynchronous. Test with retrieve mode after 1-2 minutes.")
