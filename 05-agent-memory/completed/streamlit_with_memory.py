import os
import json
import asyncio
import streamlit as st
from datetime import datetime
from strands import Agent
from strands_tools import calculator, current_time, python_repl
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# 페이지 설정
st.set_page_config(
    page_title="메모리 챗봇",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 메모리가 있는 챗봇")

# 환경 변수에서 메모리 ID 가져오기
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")

# 세션 ID 초기값 설정 (URL 파라미터 또는 새로 생성)
if "session_id" not in st.session_state:
    query_params = st.query_params
    st.session_state.session_id = query_params.get(
        "session", 
        f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

# 사용자 ID (실제 앱에서는 로그인 시스템과 연동)
if "actor_id" not in st.session_state:
    st.session_state.actor_id = "default_user"

def create_agent_with_memory():
    """메모리가 연결된 에이전트 생성"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=st.session_state.session_id,
        actor_id=st.session_state.actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )
    
    return Agent(
        system_prompt="""당신은 친절한 어시스턴트입니다. 
        사용자와의 대화를 기억하고, 이전 대화 맥락을 활용하여 응답하세요.
        사용자의 이름, 선호도, 이전에 논의한 주제를 기억해주세요.""",
        tools=[calculator, current_time, python_repl],
        session_manager=session_manager
    )

# 에이전트 초기화
if "agent" not in st.session_state:
    st.session_state.agent = create_agent_with_memory()

# 사이드바
with st.sidebar:
    st.header("📋 세션 정보")
    
    # 세션 ID 직접 입력
    new_input = st.text_input(
        "세션 ID",
        value=st.session_state.session_id,
        placeholder="세션 ID를 입력하세요",
        help="기존 세션 ID를 입력하면 해당 대화를 이어갈 수 있습니다."
    )
    
    # 입력값이 변경되면 세션 재연결
    if new_input and new_input != st.session_state.session_id:
        st.session_state.session_id = new_input
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.text(f"사용자 ID: {st.session_state.actor_id}")
    
    st.divider()
    
    # 입력된 세션 ID로 대화 시작
    if st.button("💬 대화 시작!"):
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ 사용 가능한 도구")
    st.markdown("""
    - 🧮 Calculator: 수학 계산
    - ⏰ Current Time: 현재 시간
    - 🐍 Python REPL: 코드 실행
    """)

# 채팅 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            try:
                response = st.session_state.agent(prompt)
                response_text = str(response)
                
                st.markdown(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
