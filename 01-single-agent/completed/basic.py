from strands import Agent
from strands_tools import calculator, current_time, python_repl # 참고: https://github.com/strands-agents/tools

agent = Agent(
    tools=[calculator, current_time, python_repl],
    system_prompt="초등학생에게 설명하듯 답변하세요"
    )
response = agent("80 / 4 * 5 의 제곱근은?") # prompt
