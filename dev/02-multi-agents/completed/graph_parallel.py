from strands import Agent
from strands.multiagent import GraphBuilder

financial_advisor = Agent(name="financial_advisor", system_prompt="You are a financial advisor focusing on cost-benefit analysis, budget impact, and ROI calculations. Collaborate with other experts to build comprehensive financial perspectives.")
technical_architect = Agent(name="technical_architect", system_prompt="You are a technical architect evaluating feasibility, implementation challenges, and technical risks. Collaborate with other experts to ensure technical viability.")
market_researcher = Agent(name="market_researcher", system_prompt="You are a market researcher analyzing market conditions, user needs, and competitive environment. Collaborate with other experts to validate market opportunities.")
risk_analyst = Agent(name="risk_analyst", system_prompt="You are a risk analyst identifying potential risks, mitigation strategies, and compliance issues. Collaborate with other experts to ensure comprehensive risk assessment.")

builder = GraphBuilder()

builder.add_node(financial_advisor, "finance_expert")
builder.add_node(technical_architect, "tech_expert")
builder.add_node(market_researcher, "market_expert")
builder.add_node(risk_analyst, "risk_analyst")

# Define parallel execution
builder.add_edge("finance_expert", "tech_expert")
builder.add_edge("finance_expert", "market_expert")
builder.add_edge("tech_expert", "risk_analyst")
builder.add_edge("market_expert", "risk_analyst")

builder.set_entry_point("finance_expert")

graph = builder.build()

result = graph("Our company is considering launching a new AI-based customer service platform. The initial investment is $2 million with an expected 3-year ROI of 150%. Please provide a financial evaluation.")

print(f"Response: {result}")

for node in result.execution_order:
    print(f"Executed: {node.node_id}")

print(f"Total nodes: {result.total_nodes}")
print(f"Completed nodes: {result.completed_nodes}")
print(f"Execution time: {result.execution_time}ms")

print("Financial Advisor:")
print(result.results["finance_expert"].result)
print("============================================================\n")

print("Technical Expert:")
print(result.results["tech_expert"].result)
print("============================================================\n")

print("Market Researcher:")
print(result.results["market_expert"].result)
print("============================================================\n")
