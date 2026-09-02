import streamlit as st
from strands import Agent
from strands_tools import calculator, current_time, use_aws, python_repl
import json
import asyncio

# Page configuration
st.set_page_config(
    page_title="Strands Agent Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("🤖 Strands Agent Chatbot")

# Agent initialization (stored in session state)
if "agent" not in st.session_state:
    st.session_state.agent = Agent(tools=[calculator, current_time, use_aws, python_repl])

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            # Display thinking process
            if message.get("thinking_steps"):
                with st.expander("🧠 View Thinking Process", expanded=False):
                    for step in message["thinking_steps"]:
                        st.markdown(step)
            # Display final response
            st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your message..."):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant response
    with st.chat_message("assistant"):
        # Create main container
        main_container = st.container()

        try:
            # Define async function
            async def run_agent():
                final_response = ""
                current_text = ""
                tool_info = {}
                current_text_box = None

                # Execute Agent stream
                agent_stream = st.session_state.agent.stream_async(prompt)

                async for event in agent_stream:
                    # Text streaming
                    if "data" in event:
                        text = event["data"]
                        current_text += text

                        # Create new text box if none exists
                        if current_text_box is None:
                            with main_container:
                                current_text_box = st.empty()

                        # Display current text in text box
                        current_text_box.info(current_text)

                    # Tool call information
                    elif "current_tool_use" in event:
                        # Finish current text box if exists
                        if current_text:
                            current_text_box = None
                            current_text = ""

                        current_tool_use = event["current_tool_use"]
                        tool_name = current_tool_use.get("name", "")
                        tool_input = current_tool_use.get("input", {})
                        tool_use_id = current_tool_use.get("toolUseId", "")

                        # Store tool information
                        if tool_use_id not in tool_info:
                            tool_info[tool_use_id] = {
                                "name": tool_name,
                                "input": tool_input,
                                "result": None
                            }

                            # Display tool call in real-time
                            with main_container:
                                if tool_input:
                                    st.warning(f"🔧 **Tool Call:** `{tool_name}`\n\n**Input:**\n```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```")
                                else:
                                    st.warning(f"🔧 **Tool Call:** `{tool_name}`")

                    # Tool results
                    elif "message" in event:
                        message = event["message"]
                        if "content" in message:
                            content = message["content"]
                            if content and "toolResult" in content[0]:
                                tool_result = content[0]["toolResult"]
                                tool_use_id = tool_result["toolUseId"]
                                tool_content = tool_result["content"]
                                result_text = tool_content[0].get("text", "") if tool_content else ""

                                # Store and display tool results
                                if tool_use_id in tool_info:
                                    tool_info[tool_use_id]["result"] = result_text

                                    with main_container:
                                        st.success(f"✅ **Tool Result:** {result_text[:200]}...")

                    # Final result
                    elif "result" in event:
                        # Finish current text box if exists
                        if current_text:
                            current_text_box = None

                        final = event["result"]
                        message = final.message
                        if message:
                            content = message.get("content", [])
                            if content:
                                final_response = content[0].get("text", "")

                return final_response, tool_info

            # Execute async function
            final_response, tool_info = asyncio.run(run_agent())

            # Display final response (as plain text)
            with main_container:
                st.markdown("---")
                st.markdown(final_response)

            # Save message (including reasoning information)
            reasoning_text = ""
            if tool_info:
                reasoning_text = "### 🔧 Tools Used\n\n"
                for tool_id, info in tool_info.items():
                    reasoning_text += f"**Tool Name:** `{info['name']}`\n\n"
                    reasoning_text += f"**Input:** `{json.dumps(info['input'], ensure_ascii=False)}`\n\n"
                    if info['result']:
                        reasoning_text += f"**Result:** {info['result'][:200]}...\n\n"
                    reasoning_text += "---\n\n"

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response,
                "thinking_steps": [reasoning_text] if reasoning_text else None
            })

        except Exception as e:
            import traceback
            error_message = f"An error occurred: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

# Additional information in sidebar
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    **Available Tools:**
    - 🧮 Calculator: Mathematical calculations
    - ⏰ Current Time: Current time
    - ☁️ AWS: AWS operations
    - 🐍 Python REPL: Python code execution

    **Example Questions:**
    - "What is 80 divided by 4?"
    - "Tell me the current time"
    - "Calculate the square root of 10"
    """)

    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.rerun()
