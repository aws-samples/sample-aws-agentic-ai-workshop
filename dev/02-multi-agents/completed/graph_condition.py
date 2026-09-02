import os, argparse
from strands import Agent
from strands.multiagent import GraphBuilder
from strands_tools import file_write

os.environ['BYPASS_TOOL_CONSENT'] = 'true' # Disable file_write confirmation prompt

classifier = Agent(
    name="classifier", 
    system_prompt="You are an agent that classifies report requests. Return only Technical or Business classification."
    )

technical_report = Agent(
    name="technical_expert", 
    system_prompt="You are a technical expert who writes reports from a technical perspective. Save reports as technical_report.md.",
    tools=[file_write]
    )
    
business_report = Agent(
    name="business_expert", 
    system_prompt="You are a business expert who writes reports from a business perspective. Save reports as business_report.md.",
    tools=[file_write]
    )

def is_technical(state):
    classifier_result = state.results.get("classifier")
    if not classifier_result:
        return False
    result_text = str(classifier_result.result)
    return "technical" in result_text.lower()

def is_business(state):
    classifier_result = state.results.get("classifier")
    if not classifier_result:
        return False
    result_text = str(classifier_result.result)
    return "business" in result_text.lower()

builder = GraphBuilder()

builder.add_node(classifier, "classifier")
builder.add_node(technical_report, "technical_report")
builder.add_node(business_report, "business_report")

# Add conditional edges
builder.add_edge("classifier", "technical_report", condition=is_technical)
builder.add_edge("classifier", "business_report", condition=is_business)

builder.set_entry_point("classifier")

graph = builder.build()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        type=str,
        default="Please write a report on the impact of remote work on business. Summarize considerations and key risk factors."
    )

    args = parser.parse_args()
    prompt = args.query

    print(f"Input Prompt: {prompt}")
    print("\n============================================================")

    result = graph(prompt)

    print(f"Response: {result}")

    for node in result.execution_order:
        print(f"Executed: {node.node_id}")

    print("\n============================================================")
    print("Classifier:")
    print(result.results["classifier"].result)

    print(f"Total nodes: {result.total_nodes}")
    print(f"Completed nodes: {result.completed_nodes}")
    print(f"Failed nodes: {result.failed_nodes}")
    print(f"Execution time: {result.execution_time}ms")
    print(f"Token usage: {result.accumulated_usage}")
    print("\n============================================================\n")
