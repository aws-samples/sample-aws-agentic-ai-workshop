from pathlib import Path
from strands import tool

PROMPT_FILE = Path(".prompt")


@tool
def system_prompt(action: str, prompt: str | None = None) -> dict:
    """에이전트 자신의 시스템 프롬프트를 런타임에 관리합니다.

    Args:
        action: "view", "update", "add_context", "reset" 중 하나.
        prompt: 새 프롬프트 텍스트 (update / add_context 시 필요).

    Returns:
        status와 content를 담은 dict.
    """
    if action == "view":
        current = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
        return {"status": "success", "content": [{"text": current or "(비어 있음)"}]}

    if action == "update":
        if not prompt:
            return {"status": "error", "content": [{"text": "prompt가 필요합니다"}]}
        PROMPT_FILE.write_text(prompt)   # 디스크에 영속화 -> 재시작해도 유지
        return {"status": "success",
                "content": [{"text": f"프롬프트를 갱신하고 저장했습니다 ({len(prompt)}자)."}]}

    if action == "add_context":
        if not prompt:
            return {"status": "error", "content": [{"text": "prompt가 필요합니다"}]}
        existing = PROMPT_FILE.read_text() if PROMPT_FILE.exists() else ""
        merged = f"{existing}\n\n{prompt}" if existing else prompt
        PROMPT_FILE.write_text(merged)
        return {"status": "success", "content": [{"text": "컨텍스트를 추가했습니다."}]}

    if action == "reset":
        if PROMPT_FILE.exists():
            PROMPT_FILE.unlink()
        return {"status": "success", "content": [{"text": "프롬프트를 기본값으로 초기화했습니다."}]}

    return {"status": "error", "content": [{"text": f"알 수 없는 action: {action}"}]}
