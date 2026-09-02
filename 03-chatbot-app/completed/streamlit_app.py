import streamlit as st
from strands import Agent
from strands_tools import calculator, current_time, use_aws, python_repl
import json
import asyncio

# 페이지 설정
st.set_page_config(
    page_title="Strands Agent 챗봇",
    page_icon="🤖",
    layout="centered"
)

# 제목
st.title("🤖 Strands Agent 챗봇")

# Agent 초기화 (세션 상태에 저장)
if "agent" not in st.session_state:
    st.session_state.agent = Agent(tools=[calculator, current_time, use_aws, python_repl])

# 채팅 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            # 생각 과정 표시
            if message.get("thinking_steps"):
                with st.expander("🧠 생각 과정 보기", expanded=False):
                    for step in message["thinking_steps"]:
                        st.markdown(step)
            # 최종 응답 표시
            st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant 응답 생성
    with st.chat_message("assistant"):
        # 메인 컨테이너 생성
        main_container = st.container()

        try:
            # 비동기 함수 정의
            async def run_agent():
                final_response = ""
                current_text = ""
                tool_info = {}
                current_text_box = None

                # Agent 스트림 실행
                agent_stream = st.session_state.agent.stream_async(prompt)

                async for event in agent_stream:
                    # 텍스트 스트리밍
                    if "data" in event:
                        text = event["data"]
                        current_text += text

                        # 현재 텍스트 박스가 없으면 새로 생성
                        if current_text_box is None:
                            with main_container:
                                current_text_box = st.empty()

                        # 텍스트 박스에 현재 텍스트 표시
                        current_text_box.info(current_text)

                    # 도구 호출 정보
                    elif "current_tool_use" in event:
                        # 현재 텍스트가 있으면 박스 마무리
                        if current_text:
                            current_text_box = None
                            current_text = ""

                        current_tool_use = event["current_tool_use"]
                        tool_name = current_tool_use.get("name", "")
                        tool_input = current_tool_use.get("input", {})
                        tool_use_id = current_tool_use.get("toolUseId", "")

                        # 도구 정보 저장
                        if tool_use_id not in tool_info:
                            tool_info[tool_use_id] = {
                                "name": tool_name,
                                "input": tool_input,
                                "result": None
                            }

                            # 실시간으로 도구 호출 표시
                            with main_container:
                                if tool_input:
                                    st.warning(f"🔧 **도구 호출:** `{tool_name}`\n\n**입력:**\n```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```")
                                else:
                                    st.warning(f"🔧 **도구 호출:** `{tool_name}`")

                    # 도구 결과
                    elif "message" in event:
                        message = event["message"]
                        if "content" in message:
                            content = message["content"]
                            if content and "toolResult" in content[0]:
                                tool_result = content[0]["toolResult"]
                                tool_use_id = tool_result["toolUseId"]
                                tool_content = tool_result["content"]
                                result_text = tool_content[0].get("text", "") if tool_content else ""

                                # 도구 결과 저장 및 표시
                                if tool_use_id in tool_info:
                                    tool_info[tool_use_id]["result"] = result_text

                                    with main_container:
                                        st.success(f"✅ **도구 결과:** {result_text[:200]}...")

                    # 최종 결과
                    elif "result" in event:
                        # 현재 텍스트가 있으면 박스 마무리
                        if current_text:
                            current_text_box = None

                        final = event["result"]
                        message = final.message
                        if message:
                            content = message.get("content", [])
                            if content:
                                final_response = content[0].get("text", "")

                return final_response, tool_info

            # 비동기 함수 실행
            final_response, tool_info = asyncio.run(run_agent())

            # 최종 응답 표시 (일반 텍스트로)
            with main_container:
                st.markdown("---")
                st.markdown(final_response)

            # 메시지 저장 (reasoning 정보 포함)
            reasoning_text = ""
            if tool_info:
                reasoning_text = "### 🔧 사용된 도구\n\n"
                for tool_id, info in tool_info.items():
                    reasoning_text += f"**도구명:** `{info['name']}`\n\n"
                    reasoning_text += f"**입력:** `{json.dumps(info['input'], ensure_ascii=False)}`\n\n"
                    if info['result']:
                        reasoning_text += f"**결과:** {info['result'][:200]}...\n\n"
                    reasoning_text += "---\n\n"

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response,
                "thinking_steps": [reasoning_text] if reasoning_text else None
            })

        except Exception as e:
            import traceback
            error_message = f"오류가 발생했습니다: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": f"오류: {str(e)}"})

# 사이드바에 추가 정보
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    **사용 가능한 도구:**
    - 🧮 Calculator: 수학 계산
    - ⏰ Current Time: 현재 시간
    - ☁️ AWS: AWS 작업
    - 🐍 Python REPL: 파이썬 코드 실행

    **예시 질문:**
    - "80을 4로 나눈 값은?"
    - "현재 시간 알려줘"
    - "10의 제곱근을 계산해줘"
    """)

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
