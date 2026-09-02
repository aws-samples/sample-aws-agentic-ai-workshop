from strands import Agent
from strands_tools import calculator, current_time, python_repl # Reference: https://github.com/strands-agents/tools

agent = Agent(
    tools=[calculator, current_time, python_repl],
    system_prompt="Answer as if you are explaining to an elementary school student"
    )
response = agent("What is the square root of 80 / 4 * 5?") # prompt
