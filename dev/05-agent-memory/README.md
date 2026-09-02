# 5. Agent Memory (AgentCore Memory)

[한국어](README.ko.md) | English

In this lab, you will learn how to use Amazon Bedrock AgentCore Memory to enable agents to remember conversations and accumulate knowledge about users.

The agents we've built so far couldn't remember previous conversations when starting a new chat. With AgentCore Memory, agents can store conversation history, learn user preferences, and retain important information long-term.

> [!NOTE]
> **Prerequisites**
> - Environment set up per [00-setup](../00-setup/README.md), with the uv environment active
> - Amazon Bedrock model access enabled in `us-west-2` (the region used throughout this chapter)
> - AWS credentials that can call the `bedrock-agentcore` control plane and data plane (see [Troubleshooting](#troubleshooting))
> - Chapter [03-chatbot-app](../03-chatbot-app/README.md) is helpful for the Streamlit section, but not required

> [!WARNING]
> **This chapter creates real AWS resources**
> You will create two AgentCore Memory resources (`workshop_memory` and `workshop_memory_ltm`). They persist and incur charges until you delete them. Follow the [Cleanup](#cleanup) section when you are done.

**What you will learn**
- Understand AgentCore Memory core concepts (Session, Actor, Namespace)
- Use Short-Term Memory (STM) for session conversation persistence
- Apply Long-Term Memory (LTM) strategies for knowledge accumulation
- Integrate memory with Strands agents and a Streamlit app

**Estimated time:** ~30 minutes

## How this lab works

The lab pattern is the same as the previous chapters: the files in `labs/` are empty and you type the code into them, while `completed/` holds the reference answer. Write the code from `05-agent-memory/completed/` into the empty files in `05-agent-memory/labs/` to understand how AgentCore Memory works.

All commands below assume you are at the repo root.

## Files in this chapter

| File | Purpose |
|---|---|
| `labs/stm_persistence.py` | (empty) you write this: STM conversation persistence across restarts |
| `labs/ltm_semantic.py` | (empty) you write this: LTM Semantic strategy (fact extraction) |
| `labs/ltm_preference.py` | (empty) you write this: LTM User Preference strategy |
| `labs/streamlit_with_memory.py` | (empty) you write this: Streamlit chatbot with memory |
| `completed/stm_persistence.py` | reference answer |
| `completed/ltm_semantic.py` | reference answer |
| `completed/ltm_preference.py` | reference answer |
| `completed/streamlit_with_memory.py` | reference answer |

> [!NOTE]
> The reference files in `completed/` use Korean system prompts, matching the Korean version of the guide. The code snippets in this README use English prompts. Behavior is identical; use whichever you prefer.

---

## AgentCore Memory concepts

<img src="../docs/images/c4-agentcore-memory-logo.png" alt="AgentCore Memory Logo" width="800">

AgentCore Memory is a managed memory service that enables AI agents to store and utilize conversations and knowledge.

### Why do we need memory?

Typical LLM-based agents forget everything once a conversation ends. With AgentCore Memory, you get the following capabilities.

- **Conversation Continuity**: Remember previous conversations within a session
- **Knowledge Accumulation**: Store information about users long-term
- **Personalization**: Provide customized responses based on learned preferences

### Short-term memory and long-term memory

AgentCore Memory provides two types of memory. Let's look at how each memory works.

#### Short-Term Memory (STM)

<img src="../docs/images/c4-stm-sample-chat-en.png" alt="STM sample chat" width="800">

Short-term memory maintains conversation flow within a single session. Consider a customer service scenario as an example. When a customer says "Check my order status please," the agent responds with "Please tell me your order number." The customer replies "It's 12345," and the agent remembers this order number. Later, when the customer asks "When will it arrive?", the agent doesn't ask for the order number again. Since it already knows the order number is 12345, it can directly respond with "Order 12345 is expected to arrive tomorrow."

In this way, short-term memory saves turn-by-turn conversations within a session, maintains immediate context, and reduces repetitive questions.

#### Long-Term Memory (LTM)

<img src="../docs/images/c4-ltm-sample-chat-en.png" alt="LTM sample chat" width="800">

Long-term memory persists knowledge even after sessions end. For example, if a customer said "I live in Gangnam, Seoul" during a conversation a week ago, the agent stores this address information in long-term memory. A week later, when the same customer asks "Please check the delivery address for my new order," the agent can query its long-term memory and respond with "It will be delivered to your Gangnam address. Is that correct?"

In this way, long-term memory permanently stores user information and learns preferences to provide personalized experiences. The key difference from short-term memory is the ability to utilize accumulated knowledge across sessions.

#### STM vs LTM comparison

| Type | Short-Term Memory (STM) | Long-Term Memory (LTM) |
|------|------------------------|------------------------|
| **Stores** | Conversation events (messages) | Extracted knowledge (facts, preferences) |
| **Scope** | Within session | Persists across sessions |
| **Expiry** | Auto-delete after 90 days | Permanent storage |
| **Use Case** | Conversation context | User info, personalization |

### Session

A unit that identifies a single conversation session. Using the same session ID connects conversations.

```
Session: "chat_room_123"
├── Message 1: "Hello"
├── Message 2: "Nice to meet you"
└── Message 3: "How's the weather today?"
```

### Actor

Identifies conversation participants. By distinguishing actors and maintaining memory, each user can have their own separate memory.

```
Actor: "user_alice"
├── Conversations from Session 1
├── Conversations from Session 2
└── Learned preferences, factual information
```

### Semantic Memory Strategy

Long-term memory extracts knowledge from conversations through various strategies. Automatically extracts and stores **factual information** from conversations.

```
Conversation: "I live in Seoul"
  ↓
Extract: "User resides in Seoul"
  ↓
Store: /facts/user_alice
```

### User Preference Strategy

Also, learns **user preferences** from conversations.

```
Conversation: "I like spicy food"
  ↓
Extract: "User prefers spicy food"
  ↓
Store: /preferences/user_alice
```

### Summary Strategy

Also, **summarizes** conversations with users and stores them.

```
On session end
  ↓
Summary: "Discussed travel plans with user. Confirmed 3-night Jeju trip"
  ↓
Store: /summaries/user_alice/session_001
```

### Namespace

The path where knowledge is stored in LTM. Different namespaces are used per strategy.

| Namespace | Purpose |
|-----------|---------|
| `/facts/{actorId}` | Store factual information |
| `/preferences/{actorId}` | Store preferences |
| `/summaries/{actorId}/{sessionId}` | Store conversation summaries |

---

## Short-term memory (STM)

In this section, you will understand the concept of Short-Term Memory (STM) and learn how to create a memory resource to retain conversation context within a session.

### 1. What is short-term memory?

<img src="../docs/images/c4-agentcore-stm.png" alt="AgentCore STM" width="800">

Short-Term Memory (STM) stores conversation events that occur within a session.

STM automatically saves events as conversations happen. Developers don't need to implement separate storage logic: all messages between the agent and user are recorded automatically. Stored conversations are automatically deleted after 90 days by default, managing storage efficiently. Using the same session ID preserves previous conversation context even when the program is restarted. Additionally, STM can be used immediately for conversation memory without configuring an LTM strategy.

| Feature | Description |
|---------|-------------|
| **Auto Save** | Conversation events are saved automatically |
| **Auto Expiry** | Automatically deleted after 90 days by default |
| **Session-Based** | Conversation maintained within the same session ID |
| **Ready to Use** | Available immediately without an LTM strategy |

### 2. Creating an STM memory resource

Use the AWS CLI to create a memory resource.

**2-1.** Create a default memory resource from the terminal.

```bash
aws bedrock-agentcore-control create-memory \
    --name workshop_memory \
    --description "Strands Workshop Memory" \
    --event-expiry-duration 90
```

> [!NOTE]
> **Waiting for memory activation**
> After creating the memory, it takes approximately 1-2 minutes to transition to `ACTIVE` status. Check the status with the `list-memories` command and proceed to the next step once it shows `ACTIVE`.

**2-2.** Verify the created memory information.

```bash
aws bedrock-agentcore-control list-memories
```

Example output:

```json
{
    "memories": [
        {
            "arn": "arn:aws:bedrock-agentcore:us-west-2:xxxxxxxxxxxx:memory/workshop_memory-pXxxxxxxxxx",
            "id": "workshop_memory-pXxxxxxxxxx",
            "status": "ACTIVE",
            "createdAt": "2026-02-01T09:00:00.082000+09:00",
            "updatedAt": "2026-02-01T09:00:00.240000+09:00"
        }
    ]
}
```

**2-3.** Save the memory ID as an environment variable.

```bash
export AGENTCORE_MEMORY_ID=$(aws bedrock-agentcore-control list-memories --query 'memories[0].id' --output text)
echo $AGENTCORE_MEMORY_ID
```

> [!TIP]
> **Saving the memory ID**
> The memory ID (for example `workshop_memory-pXxxxxxxxxx`) is used by every script in this chapter, and the memory ARN is what identifies the resource in the console and in IAM policies. Since the environment variable needs to be set again if the terminal session ends, keep this guide handy or note the ID somewhere.

> [!WARNING]
> **Region**
> `completed/stm_persistence.py` pins the session manager to `us-west-2` with `region_name="us-west-2"`. The other scripts use your default AWS region. Create the memory resources in `us-west-2` and keep your AWS CLI default region set to `us-west-2` so that the CLI and the scripts look at the same place. Otherwise the scripts will fail to find the memory ID you exported.

### 3. Testing conversation persistence across sessions

STM remembers conversations even when the program is restarted, as long as the same session ID is used.

**3-1.** Open the `05-agent-memory/labs/stm_persistence.py` file.

**3-2.** Fix the session ID and test the conversation.

```python
import os
import argparse
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")

def create_agent_with_memory(session_id: str, actor_id: str) -> Agent:
    """Create an agent with memory attached"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config
    )
    
    return Agent(
        system_prompt="You are a friendly assistant. Remember previous conversations and respond in context.",
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
```

> [!NOTE]
> The reference answer in `completed/stm_persistence.py` passes `region_name="us-west-2"` to `AgentCoreMemorySessionManager` in addition to the config above. Add it if your default region is not `us-west-2`.

**3-3.** Run multiple times from the terminal to test conversation persistence.

```bash
# First run
uv run python 05-agent-memory/labs/stm_persistence.py \
    --message "Hi! I'm Bob. I live in Seoul."

# Second run (same session)
uv run python 05-agent-memory/labs/stm_persistence.py \
    --message "Where did I say I live?"

# Run with a different session (no memory)
uv run python 05-agent-memory/labs/stm_persistence.py \
    --session "different_session" \
    --message "Where did I say I live?"
```

You can verify that using the same session ID retains previous conversations even after restarting the program, while using a different session ID results in no memory of prior exchanges.

<details>
<summary>Review key concepts from this section</summary>

### STM configuration code

```python
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Memory configuration
memory_config = AgentCoreMemoryConfig(
    memory_id="your-memory-id",
    session_id="unique-session-id",
    actor_id="user-identifier"
)

# Create session manager
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config
)

# Attach to agent
agent = Agent(
    system_prompt="...",
    session_manager=session_manager
)
```

### Key points

1. **session_id**: Same session ID = same conversation context
2. **actor_id**: User identifier (supports multi-user)
3. **Auto Save**: Conversations are automatically saved to memory

</details>

---

## Long-term memory (LTM)

In this section, you will learn how to accumulate knowledge across sessions using Long-Term Memory (LTM) strategies.

### 1. What is long-term memory?

<img src="../docs/images/c4-agentcore-ltm.png" alt="AgentCore LTM" width="800">

Long-Term Memory (LTM) extracts important information from conversations and stores it permanently. Unlike STM, knowledge persists even after sessions end.

Long-term memory records store structured information extracted from raw agent interactions and are maintained across multiple sessions. Long-term memory preserves only key insights such as conversation summaries, facts and knowledge, and user preferences. For example, if a customer tells an agent their preferred shoe brand during a conversation, the AI agent stores this as long-term memory. Later, in a different conversation, the agent can remember this and suggest that shoe brand, making interactions personalized and relevant.

#### LTM creation mechanism

Long-term memory creation is an asynchronous process that runs in the background. After raw conversations/context are stored in short-term memory via CreateEvent, insights are automatically extracted. This approach efficiently consolidates key information without interrupting real-time interactions.

During the long-term memory creation process, AgentCore Memory performs the following tasks. Since all of this is processed asynchronously in the background, it doesn't affect the conversation flow with users.

1. First, it analyzes the conversation content stored in short-term memory.
2. Then, it extracts relevant information according to the configured strategy (Semantic, User Preference, Summary).
3. The extracted information is converted to vector embeddings and stored in the designated namespace.

#### Types of LTM strategies

AgentCore Memory provides three LTM strategies.

- The Semantic strategy extracts factual information from conversations. When a user says "I live in Seoul," it extracts and stores the fact "The user resides in Seoul."
- The Summary strategy summarizes the entire conversation when a session ends. It compresses the key content of long conversations for quick reference later.
- The User Preference strategy learns user preferences. From a conversation like "I like spicy food," it extracts food preferences for use in personalized recommendations.

| Strategy | Description | Namespace Example |
|----------|-------------|-------------------|
| **Semantic** | Extract factual information from conversations | `/facts/{actorId}` |
| **Summary** | Generate conversation session summaries | `/summaries/{actorId}/{sessionId}` |
| **User Preference** | Learn user preferences | `/preferences/{actorId}` |

### 2. Creating memory with LTM strategies

**2-1.** Create a memory with LTM strategies in the terminal.

```bash
aws bedrock-agentcore-control create-memory \
    --name workshop_memory_ltm \
    --description "Memory with LTM strategies" \
    --event-expiry-duration 90 \
    --memory-strategies '[
        {
            "semanticMemoryStrategy": {
                "name": "FactExtractor",
                "namespaces": ["/facts/{actorId}"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name": "PreferenceLearner", 
                "namespaces": ["/preferences/{actorId}"]
            }
        }
    ]'
```

**2-2.** Verify the created memory information.

```bash
aws bedrock-agentcore-control list-memories
```

> [!TIP]
> **Save the memory ID**
> This is a second, separate memory resource from the STM one. Its ID is used by both LTM scripts. Since it needs to be set again if the terminal session ends, keep this guide handy.

**2-3.** Save the created memory ID as an environment variable.

```bash
export AGENTCORE_MEMORY_LTM_ID=$(aws bedrock-agentcore-control list-memories --query "memories[?contains(id, 'ltm')].id" --output text)
echo $AGENTCORE_MEMORY_LTM_ID
```

> [!NOTE]
> Like the STM memory, the LTM memory also takes about 1-2 minutes to become `ACTIVE`. Wait until `aws bedrock-agentcore-control get-memory --memory-id $AGENTCORE_MEMORY_LTM_ID --query 'memory.status'` returns `"ACTIVE"` before running the scripts.

### 3. Using the Semantic Memory strategy

Semantic Memory automatically extracts and stores factual information from conversations.

**3-1.** Open the `05-agent-memory/labs/ltm_semantic.py` file.

**3-2.** Create an agent with LTM configuration.

```python
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
```

**3-3.** Handle branching between learn mode and retrieve mode.

> [!NOTE]
> **LTM asynchronous processing**
> LTM creation is processed asynchronously in the background. Wait 1-2 minutes after learning before testing with retrieve mode.

```python
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
```

**3-4.** Run in learn mode from the terminal:

```bash
uv run python 05-agent-memory/labs/ltm_semantic.py --mode learn --actor user_charlie \
    --message "I'm Charlie. I work as a software engineer and mainly use Python."
```

**3-5.** Test with retrieve mode after 1-2 minutes:

```bash
uv run python 05-agent-memory/labs/ltm_semantic.py --mode retrieve --actor user_charlie \
    --message "What did I say I do for work?"
```

You can verify that it remembers previously learned facts even in a different session.

```text
You mentioned that you work as a software engineer, Charlie. You also said you mainly use Python. By the way, I'm curious what projects or work you're currently working on!
```

### 4. Using the User Preference strategy

The User Preference strategy automatically learns user preferences.

**4-1.** Open the `05-agent-memory/labs/ltm_preference.py` file.

**4-2.** Create a preference learning agent.

```python
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

retrieval_config = {
    "/preferences/{actorId}": RetrievalConfig(
        top_k=10,
        relevance_score=0.3
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
        agentcore_memory_config=memory_config
    )
    
    return Agent(
        system_prompt="""You are an assistant that provides personalized recommendations.
        Learn user preferences and provide customized suggestions.""",
        session_manager=session_manager
    )
```

**4-3.** Handle branching between learn mode and recommend mode.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["learn", "recommend"], required=True,
                        help="learn: Learn preferences, recommend: Preference-based recommendations")
    parser.add_argument("--actor", default="user_diana")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    # Generate a new session ID for each run (to verify LTM persists across sessions)
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    agent = create_agent(session_id, args.actor)
    agent(args.message)
    
    if args.mode == "learn":
        print("\n💡 LTM creation is asynchronous. Test with recommend mode after 1-2 minutes.")
```

**4-4.** Train preferences from the terminal:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode learn --actor user_diana \
    --message "I like Korean food, especially kimchi jjigae. I enjoy spicy food."
```

**4-5.** Train additional preferences:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode learn --actor user_diana \
    --message "I like sci-fi movies, and I enjoy hiking on weekends."
```

**4-6.** Test with recommend mode after 1-2 minutes:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode recommend --actor user_diana \
    --message "Can you recommend what I should have for dinner tonight?"
```

You can verify that the agent provides personalized recommendations based on learned preferences.

```text
Based on your preference for spicy food and Korean cuisine, let me recommend some dinner options!

**🌶️ Spicy Korean Food Recommendations:**
- **Tteokbokki + Sundae Gukbap**: A combination of sweet and spicy rice cakes with hearty blood sausage soup
- **Jeyuk Bokkeum with Cheongyang Peppers**: Similar spicy kick to the kimchi jjigae you love
- **Bulgogi Jeongol**: A hearty and spicy hot pot dish
```

### 5. How LTM works

> [!NOTE]
> **How LTM accumulates knowledge**
>
> ```
> [Conversation]
> User: "I'm a Python developer"
>     ↓
> [Semantic Strategy Operation]
>   - Fact extraction: "The user is a Python developer"
>   - Namespace: /facts/user_charlie
>   - Vector embedding generation and storage
>     ↓
> [Question in Different Session]
> User: "What did I say I do for work?"
>     ↓
> [LTM Search]
>   - Query: "User's occupation"
>   - Search namespace /facts/user_charlie
>   - Related fact found: "Python developer"
>     ↓
> Agent: "You said you're a Python developer!"
> ```

---

## Streamlit integration

In this section, you will learn how to integrate AgentCore Memory with a Streamlit web application to create a chatbot that remembers conversations.

### 1. Building a chatbot with memory

By integrating AgentCore Memory with a Streamlit chatbot, you can create a chatbot that remembers conversations even when users refresh the browser.

A regular chatbot stores conversations only in the browser's session state. When users refresh the browser, all conversations are reset, and previous conversations cannot be continued from other devices. In contrast, a memory chatbot stores conversations in AgentCore Memory. Conversations persist even after browser refresh, and using the same session ID allows continuing conversations from other devices.

| Item | Regular Chatbot | Memory Chatbot |
|------|-----------------|----------------|
| Conversation Storage | Session state (browser memory) | AgentCore Memory |
| On Refresh | Conversation reset | Conversation persists |
| Other Devices | Cannot share conversations | Share via same session ID |

### 2. Writing memory integration code

**2-1.** Open the `05-agent-memory/labs/streamlit_with_memory.py` file.

**2-2.** Import required libraries.

```python
import os
import json
import asyncio
import streamlit as st
from datetime import datetime
from strands import Agent
from strands_tools import calculator, current_time, python_repl
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Page configuration
st.set_page_config(
    page_title="Memory Chatbot",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Chatbot with Memory")
```

**2-3.** Configure memory settings.

```python
# Get memory ID from environment variable
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")

# Initialize session ID (URL parameter or generate new one)
if "session_id" not in st.session_state:
    query_params = st.query_params
    st.session_state.session_id = query_params.get(
        "session", 
        f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

# User ID (in real apps, integrate with login system)
if "actor_id" not in st.session_state:
    st.session_state.actor_id = "default_user"
```

**2-4.** Write function to create agent with memory.

```python
def create_agent_with_memory():
    """Create agent with memory connection"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=st.session_state.session_id,
        actor_id=st.session_state.actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )
    
    return Agent(
        system_prompt="""You are a friendly assistant. 
        Remember conversations with users and use previous context in responses.
        Remember user names, preferences, and previously discussed topics.""",
        tools=[calculator, current_time, python_repl],
        session_manager=session_manager
    )

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = create_agent_with_memory()
```

**2-5.** Display session info in sidebar. You can directly enter a session ID to connect to an existing session.

```python
# Sidebar
with st.sidebar:
    st.header("📋 Session Info")
    
    # Direct session ID input
    new_input = st.text_input(
        "Session ID",
        value=st.session_state.session_id,
        placeholder="Enter a session ID",
        help="Enter an existing session ID to continue that conversation."
    )
    
    # Reconnect session if input changed
    if new_input and new_input != st.session_state.session_id:
        st.session_state.session_id = new_input
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.text(f"User ID: {st.session_state.actor_id}")
    
    st.divider()
    
    # Start chat with current session ID
    if st.button("💬 Start Chat!"):
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ Available Tools")
    st.markdown("""
    - 🧮 Calculator: Math calculations
    - ⏰ Current Time: Current time
    - 🐍 Python REPL: Code execution
    """)
```

**2-6.** Add chat history display and input handling code.

```python
# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your message..."):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent(prompt)
                response_text = str(response)
                
                st.markdown(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
```

### 3. Running and testing the memory chatbot

**3-1.** Run the Streamlit app in terminal:

```bash
export AGENTCORE_MEMORY_ID=$(aws bedrock-agentcore-control list-memories --query 'memories[0].id' --output text)
echo $AGENTCORE_MEMORY_ID
uv run streamlit run 05-agent-memory/labs/streamlit_with_memory.py
```

**3-2.** Test the following in browser.

1. Enter `my-session` in the Session ID input field in the sidebar and click the "💬 Start Chat!" button.
2. **Start conversation**: "Hi! I'm Alice. I live in Seoul."
3. **Refresh browser** (F5)
4. **Check memory**: "What's my name?"

You can verify that the agent remembers previous conversations even after browser refresh.

<img src="../docs/images/c4-streamlit-sample-chat1.png" alt="Streamlit Chat 1" width="800">

**3-3.** Test new session.

1. Enter `my-session` in the Session ID input field in the sidebar.
2. Click the "💬 Start Chat!" button.
3. Ask "What's my name?"
4. Verify that new session doesn't remember previous conversations

Because the app reads the session ID from the `session` URL parameter, you can also reopen a conversation by visiting the app with `?session=<session-id>`. The agent recalls what was said in that session.

<img src="../docs/images/c4-streamlit-sample-chat2.png" alt="Streamlit Chat 2" width="800">

<details>
<summary>Chapter key concepts review</summary>

### Memory integration core code

```python
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Memory configuration
memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=session_id,
    actor_id=actor_id
)

# Create session manager
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
)

# Connect to agent
agent = Agent(
    system_prompt="...",
    tools=[...],
    session_manager=session_manager
)
```

### Memory types summary

| Type | Scope | Expiry | Use Case |
|------|-------|--------|----------|
| STM | Within session | 90 days | Conversation context |
| LTM Semantic | Per user | Permanent | Fact retention |
| LTM Preference | Per user | Permanent | Personalization |
| LTM Summary | Per session | Permanent | Conversation summary |

</details>

You have learned how to integrate AgentCore Memory with Strands agents and Streamlit applications. Your agents can now remember conversations, accumulate knowledge about users, and provide personalized experiences.

---

## Cleanup

The two memory resources created in this chapter (`workshop_memory` and `workshop_memory_ltm`) keep storing events and memory records until you delete them. Delete both when you are finished.

**1.** List the memory resources and their IDs.

```bash
aws bedrock-agentcore-control list-memories --query 'memories[].[id,status]' --output table
```

**2.** Delete each memory by ID.

```bash
aws bedrock-agentcore-control delete-memory --memory-id $AGENTCORE_MEMORY_ID
aws bedrock-agentcore-control delete-memory --memory-id $AGENTCORE_MEMORY_LTM_ID
```

If the environment variables are no longer set, pass the IDs from step 1 directly:

```bash
aws bedrock-agentcore-control delete-memory --memory-id workshop_memory-pXxxxxxxxxx
aws bedrock-agentcore-control delete-memory --memory-id workshop_memory_ltm-pXxxxxxxxxx
```

**3.** Confirm the memories are gone. Deletion also removes all events and extracted memory records they contained.

```bash
aws bedrock-agentcore-control list-memories
```

> [!WARNING]
> Deletion is not instantaneous: a memory may report `DELETING` for a short while before it disappears from `list-memories`. Re-run the list command until the resource is no longer returned.

---

## Troubleshooting

<details>
<summary>AccessDeniedException when calling bedrock-agentcore</summary>

An error such as `AccessDeniedException: User ... is not authorized to perform: bedrock-agentcore:CreateMemory` means the identity you are using lacks AgentCore Memory permissions. Two sets of operations are needed:

- Control plane (creating and managing the resource): `CreateMemory`, `ListMemories`, `GetMemory`, `DeleteMemory`
- Data plane (what the scripts call at runtime): `CreateEvent`, `ListEvents`, `ListMemoryRecords`, `RetrieveMemoryRecords`

Check which identity you are using and confirm it has these `bedrock-agentcore:*` actions attached:

```bash
aws sts get-caller-identity
```

Also confirm you are calling the same region where the memory was created. A memory created in `us-west-2` is not visible from another region, which surfaces as a not-found or access error.

</details>

<details>
<summary>The script fails because the memory is still in CREATING state</summary>

A newly created memory takes about 1-2 minutes to become `ACTIVE`, and it cannot store events before then. Check the status and wait:

```bash
aws bedrock-agentcore-control get-memory --memory-id $AGENTCORE_MEMORY_ID --query 'memory.status'
```

Run the scripts only once this returns `"ACTIVE"`. If you are using `list-memories` instead, look at the `status` field of the entry.

Also verify that the exported variable is actually populated. If `echo $AGENTCORE_MEMORY_ID` prints nothing or `None`, the `--query` in the export command matched no memory, and the script will fall back to the placeholder `your-memory-id-here` and fail.

</details>

<details>
<summary>LTM queries return nothing</summary>

LTM extraction is asynchronous. Right after a `learn` run, short-term events exist but no memory records have been extracted yet, so retrieval returns nothing and the agent answers as if it never learned anything. Things to check, in order:

1. **Wait 1-2 minutes** after the `learn` run, then retry the `retrieve` / `recommend` run.
2. **Inspect the namespace directly** to see whether any records were extracted:

   ```bash
   aws bedrock-agentcore list-memory-records \
       --memory-id $AGENTCORE_MEMORY_LTM_ID \
       --namespace "/facts/user_charlie"
   ```

   For preferences, use `--namespace "/preferences/user_diana"`.
3. **Use the LTM memory ID, not the STM one.** The LTM scripts read `AGENTCORE_MEMORY_LTM_ID`. The plain `workshop_memory` resource has no strategies, so it never extracts records.
4. **Match the actor ID.** Records are stored under `/facts/{actorId}`, so learning with `--actor user_charlie` and retrieving with a different `--actor` returns nothing.
5. **Relevance threshold.** `RetrievalConfig(relevance_score=...)` filters out weak matches (`0.5` in `ltm_semantic.py`, `0.3` in `ltm_preference.py`). If records exist but are not being used, lower the threshold or phrase the question closer to what was learned.

</details>

---
Prev: [Observability](../04-observability/README.md) | Next: [AgentCore Runtime](../06-agentcore-runtime/README.md)
