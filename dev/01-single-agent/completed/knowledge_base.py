from strands import Agent
from strands_tools import retrieve

KNOWLEDGE_BASE_ID = "<Enter your Knowledge Base ID here>"

agent = Agent(
    system_prompt=f"""You are a document-based Q&A assistant.
    When answering user questions, you must use the retrieve tool to search for relevant information from the Knowledge Base (ID: {KNOWLEDGE_BASE_ID}) before answering.
    Answer accurately based on the retrieved document content, and say you don't know if the information is not in the documents.""",
    tools=[retrieve]
)

if __name__ == "__main__":
    response = agent("Please summarize the main content of the uploaded document.")
    print(response)
