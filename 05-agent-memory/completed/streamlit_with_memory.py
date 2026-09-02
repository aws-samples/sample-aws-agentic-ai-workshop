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
