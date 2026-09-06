from strands import Agent
from strands_tools import calculator, current_time, python_repl # Reference: https://github.com/strands-agents/tools

agent = Agent(
    tools=[calculator, current_time, python_repl],
    system_prompt="Answer as if you are explaining to an elementary school student"
    )
response = agent("What is the square root of 80 / 4 * 5?") # prompt

# No model is set above, so Strands uses its default Bedrock model. If the run fails with
# AccessDeniedException or ValidationException, that default is not callable from your
# account. Specify the model directly instead:
#
# from strands import Agent
# from strands_tools import calculator, current_time, python_repl
#
# agent = Agent(
#     model="us.anthropic.claude-sonnet-4-6",   # 👈 specify the model directly
#     tools=[calculator, current_time, python_repl],
# )
# response = agent("What is the square root of 80 / 4 * 5?") # prompt
