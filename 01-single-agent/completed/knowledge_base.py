from strands import Agent
from strands_tools import retrieve

KNOWLEDGE_BASE_ID = "<여기에 Knowledge Base ID를 입력하세요>"

agent = Agent(
    system_prompt=f"""당신은 문서 기반 질의응답 어시스턴트입니다.
    사용자의 질문에 답변할 때 반드시 retrieve 도구를 사용하여 Knowledge Base(ID: {KNOWLEDGE_BASE_ID})에서 관련 정보를 검색한 후 답변하세요.
    검색된 문서의 내용을 기반으로 정확하게 답변하고, 문서에 없는 내용은 모른다고 답변하세요.""",
    tools=[retrieve]
)

if __name__ == "__main__":
    response = agent("업로드한 문서의 주요 내용을 요약해주세요.")
    print(response)
