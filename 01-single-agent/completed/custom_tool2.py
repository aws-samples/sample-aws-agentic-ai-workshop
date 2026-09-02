from strands import Agent
from tools import python_repl_tool, bash_tool

agent = Agent(
    tools=[bash_tool, python_repl_tool]
    )

if __name__ == "__main__":
    user_input = "Can you write and execute Python code that prints Hello world?"
    
    ## Or, uncomment below to change the prompt and execute
    # user_input = "Check what files are in the 01-single-agent/completed folder"

    response = agent(user_input)

