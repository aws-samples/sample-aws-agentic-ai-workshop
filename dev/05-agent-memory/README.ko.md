# 5. 에이전트 메모리 (AgentCore Memory)

<p align="center"><a href="README.ko.md">한국어</a> | <a href="README.md">English</a></p>

이번 실습에서는 Amazon Bedrock AgentCore Memory를 활용하여 에이전트가 대화를 기억하고 사용자에 대한 지식을 축적하는 방법을 학습합니다.

지금까지 만든 에이전트는 매번 새로운 대화를 시작할 때마다 이전 대화 내용을 기억하지 못했습니다. AgentCore Memory를 사용하면 에이전트가 대화 히스토리를 저장하고, 사용자의 선호도를 학습하며, 중요한 정보를 장기적으로 기억할 수 있습니다.

> [!NOTE]
> **사전 준비 사항**
> - [00-setup](../00-setup/README.ko.md) 에 따라 환경을 구성하고 uv 환경을 활성화합니다
> - `us-west-2` 리전에서 Amazon Bedrock 모델 액세스가 활성화되어 있어야 합니다 (이번 챕터에서 사용하는 리전입니다)
> - `bedrock-agentcore` 컨트롤 플레인과 데이터 플레인을 호출할 수 있는 AWS 자격 증명이 필요합니다 ([트러블슈팅](#트러블슈팅) 참고)
> - Streamlit 섹션은 [03-chatbot-app](../03-chatbot-app/README.ko.md) 챕터를 먼저 학습하면 이해하기 쉽지만, 필수는 아닙니다

> [!WARNING]
> **이번 챕터는 실제 AWS 리소스를 생성합니다**
> AgentCore Memory 리소스 두 개(`workshop_memory`, `workshop_memory_ltm`)를 생성합니다. 삭제하지 않으면 계속 유지되며 비용이 발생합니다. 실습을 마친 후 반드시 [리소스 정리](#리소스-정리) 섹션을 수행하세요.

**학습 목표**
- AgentCore Memory의 핵심 개념 이해 (Session, Actor, Namespace)
- 단기 메모리(STM)로 세션 내 대화 유지
- 장기 메모리(LTM) 전략으로 지식 축적
- Strands 에이전트와 Streamlit 앱에 메모리 통합

**예상 소요 시간:** 약 30분

## 실습 진행 방식

이전 챕터와 동일한 방식으로 진행합니다. `labs/` 폴더의 파일은 비어 있으며 학습자가 직접 코드를 작성하고, `completed/` 폴더에는 정답 코드가 들어 있습니다. `05-agent-memory/completed/` 디렉토리의 완성된 코드를 `05-agent-memory/labs/` 폴더 내의 빈 파일에 직접 작성하면서, AgentCore Memory의 동작 방식을 이해합니다.

아래의 모든 명령어는 레포지토리 루트 디렉토리에서 실행하는 것을 기준으로 합니다.

## 이번 챕터의 파일

| 파일 | 용도 |
|---|---|
| `labs/stm_persistence.py` | (빈 파일) 직접 작성: STM으로 재실행 후에도 대화 유지 |
| `labs/ltm_semantic.py` | (빈 파일) 직접 작성: LTM Semantic 전략 (사실 추출) |
| `labs/ltm_preference.py` | (빈 파일) 직접 작성: LTM User Preference 전략 |
| `labs/streamlit_with_memory.py` | (빈 파일) 직접 작성: 메모리가 있는 Streamlit 챗봇 |
| `completed/stm_persistence.py` | 정답 코드 |
| `completed/ltm_semantic.py` | 정답 코드 |
| `completed/ltm_preference.py` | 정답 코드 |
| `completed/streamlit_with_memory.py` | 정답 코드 |

---

## AgentCore Memory 핵심 개념

<img src="../docs/images/c4-agentcore-memory-logo.png" alt="AgentCore Memory Logo" width="800">

AgentCore Memory는 AI 에이전트가 대화와 지식을 저장하고 활용할 수 있게 해주는 관리형 메모리 서비스입니다.

### 왜 메모리가 필요한가?

일반적인 LLM 기반 에이전트는 대화가 끝나면 모든 내용을 잊어버립니다. AgentCore Memory를 사용하면 다음과 같은 기능을 제공합니다.

- **대화 연속성**: 세션 내에서 이전 대화를 기억
- **지식 축적**: 사용자에 대한 정보를 장기적으로 저장
- **개인화**: 학습한 선호도를 바탕으로 맞춤형 응답 제공

### 단기 메모리와 장기 메모리

AgentCore Memory는 두 가지 유형의 메모리를 제공합니다. 각 메모리가 어떻게 동작하는지 살펴보겠습니다.

#### 단기 메모리 (Short-Term Memory)

<img src="../docs/images/c4-stm-sample-chat-ko.png" alt="STM 대화 예시" width="800">

단기 메모리는 하나의 대화 세션 안에서 흐름을 유지합니다. 고객 서비스 시나리오를 예로 들어보겠습니다. 고객이 "주문 상태 확인해주세요"라고 말하면, 에이전트는 "주문번호를 알려주세요"라고 응답합니다. 고객이 "12345입니다"라고 답하면, 에이전트는 이 주문번호를 기억합니다. 이후 고객이 "언제 도착하나요?"라고 물어도 에이전트는 다시 주문번호를 묻지 않습니다. 이미 12345라는 주문번호를 알고 있기 때문에 바로 "주문 12345는 내일 도착 예정입니다"라고 답할 수 있습니다.

이처럼 단기 메모리는 세션 내에서 턴별 대화를 저장하고, 즉각적인 컨텍스트를 유지하여 반복적인 질문을 줄여줍니다.

#### 장기 메모리 (Long-Term Memory)

<img src="../docs/images/c4-ltm-sample-chat-ko.png" alt="LTM 대화 예시" width="800">

장기 메모리는 세션이 끝나도 지식이 유지됩니다. 예를 들어, 1주 전 대화에서 고객이 "저는 서울 강남구에 살아요"라고 말했다면, 에이전트는 이 주소 정보를 장기 메모리에 저장합니다. 일주일이 지난 오늘, 같은 고객이 "새 주문 배송지 확인해주세요"라고 물으면, 에이전트는 장기 메모리를 조회하여 "강남구 주소로 배송 예정입니다. 맞으신가요?"라고 응답할 수 있습니다.

이처럼 장기 메모리는 사용자 정보를 영구적으로 저장하고, 선호도를 학습하여 개인화된 경험을 제공합니다. 세션을 넘어 축적된 지식을 활용할 수 있다는 점이 단기 메모리와의 가장 큰 차이입니다.

#### STM vs LTM 비교

| 구분 | 단기 메모리 (STM) | 장기 메모리 (LTM) |
|------|------------------|------------------|
| **저장 대상** | 대화 이벤트 (메시지) | 추출된 지식 (사실, 선호도) |
| **범위** | 세션 내 | 세션을 넘어 유지 |
| **만료** | 기본 90일 후 자동 삭제 | 영구 저장 |
| **사용 사례** | 대화 컨텍스트 유지 | 사용자 정보, 개인화 |

### Session (세션)

하나의 대화 세션을 식별하는 단위입니다. 같은 세션 ID를 사용하면 대화가 연결됩니다.

```
Session: "chat_room_123"
├── Message 1: "안녕하세요"
├── Message 2: "반갑습니다"
└── Message 3: "오늘 날씨 어때요?"
```

### Actor (액터)

대화 참여자를 식별하는 것입니다. 액터를 구분하여 메모리를 유지하면 사용자 별로 다른 메모리를 갖게 됩니다.

```
Actor: "user_alice"
├── Session 1의 대화들
├── Session 2의 대화들
└── 학습된 선호도, 사실 정보
```

### Semantic Memory Strategy

장기 메모리는 다양한 전략을 통해 대화에서 지식을 추출합니다. 대화에서 **사실 정보**를 자동으로 추출하여 저장할 수 있습니다.

```
대화: "저는 서울에 살고 있어요"
  ↓
추출: "사용자는 서울에 거주한다"
  ↓
저장: /facts/user_alice
```

### User Preference Strategy

또한, 대화에서 **사용자 선호도**를 학습합니다.

```
대화: "매운 음식을 좋아해요"
  ↓
추출: "사용자는 매운 음식을 선호한다"
  ↓
저장: /preferences/user_alice
```

### Summary Strategy

또한, 사용자와의 대화를 **요약**하여 저장합니다.

```
세션 종료 시
  ↓
요약: "사용자와 여행 계획에 대해 논의함. 제주도 3박 4일 일정 확정"
  ↓
저장: /summaries/user_alice/session_001
```

### Namespace (네임스페이스)

위에서 설명한 전략에 따라 LTM에서 지식을 저장하는 경로입니다. 전략별로 다른 네임스페이스를 사용합니다.

| 네임스페이스 | 용도 |
|-------------|------|
| `/facts/{actorId}` | 사실 정보 저장 |
| `/preferences/{actorId}` | 선호도 저장 |
| `/summaries/{actorId}/{sessionId}` | 대화 요약 저장 |

---

## 단기 메모리 (STM)

이번 섹션에서는 단기 메모리(Short-Term Memory)의 개념을 이해하고, 메모리 리소스를 생성하여 세션 내 대화를 기억하는 방법을 학습합니다.

### 1. 단기 메모리란?

<img src="../docs/images/c4-agentcore-stm.png" alt="AgentCore STM" width="800">

단기 메모리(STM)는 세션 내에서 발생하는 대화 이벤트를 저장합니다.

단기 메모리는 대화가 발생할 때마다 자동으로 이벤트를 저장합니다. 개발자가 별도로 저장 로직을 구현할 필요 없이, 에이전트와 사용자 간의 모든 메시지가 자동으로 기록됩니다. 저장된 대화는 기본적으로 90일 후 자동으로 삭제되어 스토리지를 효율적으로 관리합니다. 동일한 세션 ID를 사용하면 프로그램을 다시 실행해도 이전 대화 컨텍스트가 유지됩니다. 또한 LTM 전략을 설정하지 않아도 STM만으로 바로 대화 기억 기능을 사용할 수 있습니다.

| 특징 | 설명 |
|------|------|
| **자동 저장** | 대화 이벤트가 자동으로 저장됨 |
| **자동 만료** | 기본 90일 후 자동 삭제 |
| **세션 기반** | 동일 세션 ID 내에서 대화 유지 |
| **즉시 사용** | LTM 전략 없이도 바로 사용 가능 |

### 2. STM 메모리 리소스 생성

AWS CLI를 사용하여 메모리 리소스를 생성합니다.

**2-1.** 터미널에서 기본 메모리 리소스를 생성합니다.

```bash
aws bedrock-agentcore-control create-memory \
    --name workshop_memory \
    --description "Strands Workshop Memory" \
    --event-expiry-duration 90
```

> [!NOTE]
> **메모리 활성화 대기**
> 메모리 생성 후 `ACTIVE` 상태로 전환되기까지 약 1-2분 정도 소요됩니다. `list-memories` 명령어로 상태를 확인하고, `ACTIVE` 상태가 된 후 다음 단계를 진행하세요.

**2-2.** 생성된 메모리 정보를 확인합니다.

```bash
aws bedrock-agentcore-control list-memories
```

출력 예시:

```json
{
    "memories": [
        {
            "arn": "arn:aws:bedrock-agentcore:us-west-2:xxxxxxxxxxxx:memory/workshop_memory-pXxxxxxxxxx",
            "id": "workshop_memory-pXxxxxxxxxx",
            "status": "ACTIVE",
            "createdAt": "2026-02-01T09:00:00.082000+09:00",
            "updatedAt": "2026-02-01T09:00:00.240000+09:00"
        }
    ]
}
```

**2-3.** 메모리 ID를 환경 변수로 저장합니다.

```bash
export AGENTCORE_MEMORY_ID=$(aws bedrock-agentcore-control list-memories --query 'memories[0].id' --output text)
echo $AGENTCORE_MEMORY_ID
```

> [!TIP]
> **메모리 ID 저장**
> 메모리 ID(예: `workshop_memory-pXxxxxxxxxx`)는 이번 챕터의 모든 스크립트에서 사용되며, 메모리 ARN은 콘솔과 IAM 정책에서 리소스를 식별하는 값입니다. 터미널 세션이 종료되면 환경 변수를 다시 설정해야 하므로, 이 가이드를 참고할 수 있도록 두거나 ID를 따로 적어두세요.

> [!WARNING]
> **리전 확인**
> `completed/stm_persistence.py` 는 세션 매니저에 `region_name="us-west-2"` 를 지정하여 리전을 고정합니다. 나머지 스크립트는 기본 AWS 리전을 사용합니다. 메모리 리소스는 `us-west-2` 에 생성하고, AWS CLI 기본 리전도 `us-west-2` 로 맞춰 두어야 CLI와 스크립트가 같은 위치를 바라봅니다. 그렇지 않으면 export한 메모리 ID를 스크립트에서 찾지 못합니다.

### 3. 세션 간 대화 유지 테스트

STM은 동일한 세션 ID를 사용하면 프로그램을 다시 실행해도 대화를 기억합니다.

**3-1.** `05-agent-memory/labs/stm_persistence.py` 파일을 엽니다.

**3-2.** 세션 ID를 고정하고 대화를 테스트합니다.

```python
import os
import argparse
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")

def create_agent_with_memory(session_id: str, actor_id: str) -> Agent:
    """Create an agent with memory attached"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config
    )
    
    return Agent(
        system_prompt="You are a friendly assistant. Remember previous conversations and respond in context.",
        session_manager=session_manager
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", default="persistent_session_001")
    parser.add_argument("--actor", default="user_bob")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    agent = create_agent_with_memory(args.session, args.actor)
    response = agent(args.message)
```

> [!NOTE]
> `completed/stm_persistence.py` 정답 코드는 위 설정에 추가로 `AgentCoreMemorySessionManager` 에 `region_name="us-west-2"` 를 전달합니다. 기본 리전이 `us-west-2` 가 아니라면 이 인자를 함께 작성하세요.

**3-3.** 터미널에서 여러 번 실행하여 대화 유지를 테스트합니다.

```bash
# 첫 번째 실행
uv run python 05-agent-memory/labs/stm_persistence.py \
    --message "안녕! 나는 Bob이야. 서울에 살고 있어."

# 두 번째 실행 (같은 세션)
uv run python 05-agent-memory/labs/stm_persistence.py \
    --message "내가 어디 산다고 했지?"

# 다른 세션으로 실행 (기억 못함)
uv run python 05-agent-memory/labs/stm_persistence.py \
    --session "different_session" \
    --message "내가 어디 산다고 했지?"
```

같은 세션 ID를 사용하면 프로그램을 다시 실행해도 이전 대화를 기억하지만, 다른 세션 ID를 사용하면 기억하지 못하는 것을 확인할 수 있습니다.

<details>
<summary>이번 섹션에서의 핵심 개념 다시보기</summary>

### STM 설정 코드

```python
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# 메모리 설정
memory_config = AgentCoreMemoryConfig(
    memory_id="your-memory-id",
    session_id="unique-session-id",
    actor_id="user-identifier"
)

# 세션 매니저 생성
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config
)

# 에이전트에 연결
agent = Agent(
    system_prompt="...",
    session_manager=session_manager
)
```

### 핵심 포인트

1. **session_id**: 같은 세션 ID = 같은 대화 컨텍스트
2. **actor_id**: 사용자 식별자 (멀티 유저 지원)
3. **자동 저장**: 대화가 자동으로 메모리에 저장됨

</details>

---

## 장기 메모리 (LTM)

이번 섹션에서는 장기 메모리(Long-Term Memory) 전략을 사용하여 세션을 넘어 지식을 축적하는 방법을 학습합니다.

### 1. 장기 메모리란?

<img src="../docs/images/c4-agentcore-ltm.png" alt="AgentCore LTM" width="800">

장기 메모리(LTM)는 대화에서 중요한 정보를 추출하여 영구적으로 저장합니다. STM과 달리 세션이 종료되어도 지식이 유지됩니다.

장기 메모리 레코드는 원시 에이전트 상호작용에서 추출된 구조화된 정보를 저장하며, 여러 세션에 걸쳐 유지됩니다. 장기 메모리는 대화 요약, 사실과 지식, 사용자 선호도와 같은 핵심 인사이트만 보존합니다. 예를 들어, 고객이 대화 중에 선호하는 신발 브랜드를 에이전트에게 말하면, AI 에이전트는 이를 장기 메모리로 저장합니다. 나중에 다른 대화에서도 에이전트는 이를 기억하고 해당 신발 브랜드를 제안할 수 있어, 상호작용이 개인화되고 관련성 있게 됩니다.

#### LTM 생성 메커니즘

장기 메모리 생성은 백그라운드에서 실행되는 비동기 프로세스입니다. CreateEvent를 통해 원시 대화/컨텍스트가 단기 메모리에 저장된 후, 자동으로 인사이트를 추출합니다. 이 방식은 실시간 상호작용을 중단하지 않으면서 핵심 정보를 효율적으로 통합합니다.

장기 메모리 생성 과정에서 AgentCore Memory는 다음 작업을 수행합니다. 이 모든 과정이 백그라운드에서 비동기적으로 처리되므로, 사용자와의 대화 흐름에 영향을 주지 않습니다.

1. 먼저 단기 메모리에 저장된 대화 내용을 분석합니다.
2. 그런 다음 설정된 전략(Semantic, User Preference, Summary)에 따라 관련 정보를 추출합니다.
3. 추출된 정보는 벡터 임베딩으로 변환되어 지정된 네임스페이스에 저장됩니다.

#### LTM 전략 종류

AgentCore Memory는 세 가지 LTM 전략을 제공합니다.

- Semantic 전략은 대화에서 사실 정보를 추출합니다. 사용자가 "저는 서울에 살아요"라고 말하면, "사용자는 서울에 거주한다"는 사실을 추출하여 저장합니다.
- Summary 전략은 대화 세션이 종료될 때 전체 대화를 요약하여 저장합니다. 긴 대화의 핵심 내용을 압축하여 나중에 빠르게 참조할 수 있습니다.
- User Preference 전략은 사용자의 선호도를 학습합니다. "매운 음식을 좋아해요"라는 대화에서 음식 선호도를 추출하여 개인화된 추천에 활용합니다.

| 전략 | 설명 | 네임스페이스 예시 |
|------|------|------------------|
| **Semantic** | 대화에서 사실 정보 추출 | `/facts/{actorId}` |
| **Summary** | 대화 세션 요약 생성 | `/summaries/{actorId}/{sessionId}` |
| **User Preference** | 사용자 선호도 학습 | `/preferences/{actorId}` |

### 2. LTM 전략이 포함된 메모리 생성

**2-1.** 터미널에서 LTM 전략이 포함된 메모리를 생성합니다.

```bash
aws bedrock-agentcore-control create-memory \
    --name workshop_memory_ltm \
    --description "Memory with LTM strategies" \
    --event-expiry-duration 90 \
    --memory-strategies '[
        {
            "semanticMemoryStrategy": {
                "name": "FactExtractor",
                "namespaces": ["/facts/{actorId}"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name": "PreferenceLearner", 
                "namespaces": ["/preferences/{actorId}"]
            }
        }
    ]'
```

**2-2.** 생성된 메모리 정보를 확인합니다.

```bash
aws bedrock-agentcore-control list-memories
```

> [!TIP]
> **메모리 ID 저장**
> 이 메모리는 앞서 만든 STM 메모리와는 별개의 리소스입니다. 이 ID는 두 개의 LTM 스크립트에서 사용됩니다. 터미널 세션이 종료되면 다시 설정해야 하므로, 이 가이드를 참고할 수 있도록 두세요.

**2-3.** 생성된 메모리 ID를 환경 변수로 저장합니다.

```bash
export AGENTCORE_MEMORY_LTM_ID=$(aws bedrock-agentcore-control list-memories --query "memories[?contains(id, 'ltm')].id" --output text)
echo $AGENTCORE_MEMORY_LTM_ID
```

> [!NOTE]
> STM 메모리와 마찬가지로 LTM 메모리도 `ACTIVE` 상태가 되기까지 약 1-2분이 소요됩니다. `aws bedrock-agentcore-control get-memory --memory-id $AGENTCORE_MEMORY_LTM_ID --query 'memory.status'` 명령이 `"ACTIVE"` 를 반환한 후에 스크립트를 실행하세요.

### 3. Semantic Memory 전략 사용

Semantic Memory는 대화에서 사실 정보를 자동으로 추출하여 저장합니다.

**3-1.** `05-agent-memory/labs/ltm_semantic.py` 파일을 엽니다.

**3-2.** LTM 설정이 포함된 에이전트를 생성합니다.

```python
import os
import argparse
import uuid
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig
)
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_LTM_ID", "your-ltm-memory-id")

# LTM retrieval configuration
retrieval_config = {
    "/facts/{actorId}": RetrievalConfig(
        top_k=5,           # Top 5 results
        relevance_score=0.5  # Relevance score threshold
    )
}

def create_agent(session_id: str, actor_id: str) -> Agent:
    """Create an agent with memory connected"""

    print(f"Session ID: {session_id} | Actor ID: {actor_id}")
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id,
        retrieval_config=retrieval_config
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )

    return Agent(
        system_prompt="""You are an assistant that learns about users.
        Remember important facts from conversations and use previously learned information in your responses.""",
        session_manager=session_manager
    )
```

**3-3.** 학습 모드와 검색 모드를 분기 처리합니다.

> [!NOTE]
> **LTM 비동기 처리**
> LTM 생성은 백그라운드에서 비동기로 처리됩니다. 학습 후 1-2분 정도 기다린 뒤 검색 모드로 테스트하세요.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["learn", "retrieve"], required=True,
                        help="learn: Learn facts, retrieve: Retrieve learned facts")
    parser.add_argument("--actor", default="user_charlie")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    # Generate a new session ID for each run (to verify LTM persists across sessions)
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    agent = create_agent(session_id, args.actor)
    agent(args.message)
    
    if args.mode == "learn":
        print("\n💡 LTM creation is asynchronous. Test with retrieve mode after 1-2 minutes.")
```

**3-4.** 터미널에서 학습 모드로 실행합니다:

```bash
uv run python 05-agent-memory/labs/ltm_semantic.py --mode learn --actor user_charlie \
    --message "저는 Charlie입니다. 소프트웨어 엔지니어로 일하고 있고, Python을 주로 사용해요."
```

**3-5.** 1-2분 후 검색 모드로 테스트합니다:

```bash
uv run python 05-agent-memory/labs/ltm_semantic.py --mode retrieve --actor user_charlie \
    --message "제가 무슨 일을 한다고 했죠?"
```

다른 세션에서도 이전에 학습한 사실을 기억하는 것을 확인할 수 있습니다.

```text
Charlie님께서 소프트웨어 엔지니어로 일하신다고 말씀하셨습니다. 그리고 Python을 주로 사용하신다고도 하셨고요. 혹시 요즘 어떤 프로젝트나 업무를 진행 중이신지 궁금하네요!
```

### 4. User Preference 전략 사용

User Preference 전략은 사용자의 선호도를 자동으로 학습합니다.

**4-1.** `05-agent-memory/labs/ltm_preference.py` 파일을 엽니다.

**4-2.** 선호도 학습 에이전트를 생성합니다.

```python
import os
import argparse
import uuid
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig
)
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_LTM_ID", "your-ltm-memory-id")

retrieval_config = {
    "/preferences/{actorId}": RetrievalConfig(
        top_k=10,
        relevance_score=0.3
    )
}

def create_agent(session_id: str, actor_id: str) -> Agent:
    """Create an agent with memory connected"""

    print(f"Session ID: {session_id} | Actor ID: {actor_id}")
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id,
        retrieval_config=retrieval_config
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config
    )
    
    return Agent(
        system_prompt="""You are an assistant that provides personalized recommendations.
        Learn user preferences and provide customized suggestions.""",
        session_manager=session_manager
    )
```

**4-3.** 학습 모드와 추천 모드를 분기 처리합니다.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["learn", "recommend"], required=True,
                        help="learn: Learn preferences, recommend: Preference-based recommendations")
    parser.add_argument("--actor", default="user_diana")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    # Generate a new session ID for each run (to verify LTM persists across sessions)
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    agent = create_agent(session_id, args.actor)
    agent(args.message)
    
    if args.mode == "learn":
        print("\n💡 LTM creation is asynchronous. Test with recommend mode after 1-2 minutes.")
```

**4-4.** 터미널에서 선호도를 학습시킵니다:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode learn --actor user_diana \
    --message "저는 한식을 좋아하고, 특히 김치찌개를 자주 먹어요. 매운 음식을 좋아해요."
```

**4-5.** 추가 선호도를 학습시킵니다:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode learn --actor user_diana \
    --message "영화는 SF 장르를 좋아하고, 주말에는 등산을 즐겨요."
```

**4-6.** 1-2분 후 추천 모드로 테스트합니다:

```bash
uv run python 05-agent-memory/labs/ltm_preference.py --mode recommend --actor user_diana \
    --message "오늘 저녁 뭐 먹을지 추천해줄래?"
```

에이전트가 학습한 선호도를 바탕으로 개인화된 추천을 제공하는 것을 확인할 수 있습니다.

```text
매운 음식과 한식을 좋아하시는 취향을 고려해서 오늘 저녁 메뉴를 추천해드릴게요!

**🌶️ 매운 한식 추천:**
- **떡볶이 + 순대국밥**: 매콤달콤한 떡볶이와 얼큰한 순대국밥 조합
- **청양고추 들어간 제육볶음**: 평소 좋아하시는 김치찌개와 비슷한 매운맛
- **불고기전골**: 매콤하면서도 든든한 전골 요리
```

### 5. LTM 동작 원리

> [!NOTE]
> **LTM이 지식을 축적하는 방식**
>
> ```
> [대화]
> 사용자: "저는 Python 개발자예요"
>     ↓
> [Semantic Strategy 동작]
>   - 사실 추출: "사용자는 Python 개발자이다"
>   - 네임스페이스: /facts/user_charlie
>   - 벡터 임베딩 생성 및 저장
>     ↓
> [다른 세션에서 질문]
> 사용자: "제가 무슨 일을 한다고 했죠?"
>     ↓
> [LTM 검색]
>   - 쿼리: "사용자의 직업"
>   - 네임스페이스 /facts/user_charlie 검색
>   - 관련 사실 검색: "Python 개발자"
>     ↓
> 에이전트: "Python 개발자라고 하셨어요!"
> ```

---

## Streamlit 앱에 메모리 통합

이번 섹션에서는 Streamlit 웹 애플리케이션에 AgentCore Memory를 통합하여, 대화를 기억하는 챗봇을 만드는 방법을 학습합니다.

### 1. 메모리가 있는 챗봇 만들기

AgentCore Memory를 Streamlit 챗봇에 통합하면, 사용자가 브라우저를 새로고침해도 대화를 기억하는 챗봇을 만들 수 있습니다.

일반 챗봇은 대화를 브라우저의 세션 상태에만 저장합니다. 사용자가 브라우저를 새로고침하면 모든 대화가 초기화되고, 다른 기기에서는 이전 대화를 이어갈 수 없습니다. 반면 메모리 챗봇은 대화를 AgentCore Memory에 저장합니다. 브라우저를 새로고침해도 대화가 유지되고, 같은 세션 ID를 사용하면 다른 기기에서도 대화를 이어갈 수 있습니다.

| 항목 | 일반 챗봇 | 메모리 챗봇 |
|------|--------|--------|
| 대화 저장 | 세션 상태 (브라우저 메모리) | AgentCore Memory |
| 새로고침 시 | 대화 초기화 | 대화 유지 |
| 다른 기기 | 대화 공유 불가 | 같은 세션 ID로 대화 공유 |

### 2. 메모리 통합 코드 작성

**2-1.** `05-agent-memory/labs/streamlit_with_memory.py` 파일을 엽니다.

**2-2.** 필요한 라이브러리를 import 합니다.

```python
import os
import json
import asyncio
import streamlit as st
from datetime import datetime
from strands import Agent
from strands_tools import calculator, current_time, python_repl
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Page configuration
st.set_page_config(
    page_title="Memory Chatbot",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Chatbot with Memory")
```

**2-3.** 메모리 설정을 구성합니다.

```python
# Get memory ID from environment variable
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id-here")

# Initialize session ID (URL parameter or generate new one)
if "session_id" not in st.session_state:
    query_params = st.query_params
    st.session_state.session_id = query_params.get(
        "session", 
        f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

# User ID (in real apps, integrate with login system)
if "actor_id" not in st.session_state:
    st.session_state.actor_id = "default_user"
```

**2-4.** 메모리가 연결된 에이전트를 생성하는 함수를 작성합니다.

```python
def create_agent_with_memory():
    """Create agent with memory connection"""
    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=st.session_state.session_id,
        actor_id=st.session_state.actor_id
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
    )
    
    return Agent(
        system_prompt="""You are a friendly assistant. 
        Remember conversations with users and use previous context in responses.
        Remember user names, preferences, and previously discussed topics.""",
        tools=[calculator, current_time, python_repl],
        session_manager=session_manager
    )

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = create_agent_with_memory()
```

**2-5.** 사이드바에 세션 정보를 표시합니다. 세션 ID를 직접 입력하여 기존 세션에 연결할 수 있습니다.

```python
# Sidebar
with st.sidebar:
    st.header("📋 Session Info")
    
    # Direct session ID input
    new_input = st.text_input(
        "Session ID",
        value=st.session_state.session_id,
        placeholder="Enter a session ID",
        help="Enter an existing session ID to continue that conversation."
    )
    
    # Reconnect session if input changed
    if new_input and new_input != st.session_state.session_id:
        st.session_state.session_id = new_input
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.text(f"User ID: {st.session_state.actor_id}")
    
    st.divider()
    
    # Start chat with current session ID
    if st.button("💬 Start Chat!"):
        st.session_state.agent = create_agent_with_memory()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ Available Tools")
    st.markdown("""
    - 🧮 Calculator: Math calculations
    - ⏰ Current Time: Current time
    - 🐍 Python REPL: Code execution
    """)
```

**2-6.** 채팅 히스토리 표시 및 입력 처리 코드를 추가합니다.

```python
# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your message..."):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent(prompt)
                response_text = str(response)
                
                st.markdown(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
```

### 3. 메모리 챗봇 실행 및 테스트

**3-1.** 터미널에서 Streamlit 앱을 실행합니다:

```bash
export AGENTCORE_MEMORY_ID=$(aws bedrock-agentcore-control list-memories --query 'memories[0].id' --output text)
echo $AGENTCORE_MEMORY_ID
uv run streamlit run 05-agent-memory/labs/streamlit_with_memory.py
```

**3-2.** 브라우저에서 다음을 테스트합니다.

1. 사이드바의 세션 ID 입력란에 `my-session`을 입력하고 "💬 대화 시작!" 버튼을 클릭합니다.
2. **대화 시작**: "안녕! 나는 Alice야. 서울에 살고 있어."
3. **브라우저 새로고침** (F5)
4. **기억 확인**: "내 이름이 뭐라고 했지?"

브라우저를 새로고침해도 에이전트가 이전 대화를 기억하는 것을 확인할 수 있습니다.

<img src="../docs/images/c4-streamlit-sample-chat1.png" alt="Streamlit Chat 1" width="800">

**3-3.** 새 세션 테스트.

1. 사이드바의 세션 ID 입력란에 `my-session`을 입력합니다.
2. "💬 대화 시작!" 버튼을 클릭합니다.
3. "내 이름이 뭐라고 했지?" 질문
4. 새 세션에서는 이전 대화를 기억하지 못하는 것 확인

이 앱은 `session` URL 파라미터에서 세션 ID를 읽어오므로, `?session=<세션-ID>` 를 붙여 접속하는 방식으로도 이전 대화를 이어갈 수 있습니다. 해당 세션에서 나눈 대화를 에이전트가 기억합니다.

<img src="../docs/images/c4-streamlit-sample-chat2.png" alt="Streamlit Chat 2" width="800">

<details>
<summary>이번 챕터에서의 핵심 개념 다시보기</summary>

### 메모리 통합 핵심 코드

```python
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# 메모리 설정
memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=session_id,
    actor_id=actor_id
)

# 세션 매니저 생성
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
)

# 에이전트에 연결
agent = Agent(
    system_prompt="...",
    tools=[...],
    session_manager=session_manager
)
```

### 메모리 유형 요약

| 유형 | 범위 | 만료 | 사용 사례 |
|------|------|------|----------|
| STM | 세션 내 | 90일 | 대화 컨텍스트 |
| LTM Semantic | 사용자별 | 영구 | 사실 기억 |
| LTM Preference | 사용자별 | 영구 | 개인화 |
| LTM Summary | 세션별 | 영구 | 대화 요약 |

</details>

AgentCore Memory를 Strands 에이전트와 Streamlit 애플리케이션에 통합하는 방법을 학습했습니다. 이제 에이전트가 대화를 기억하고, 사용자에 대한 지식을 축적하며, 개인화된 경험을 제공할 수 있습니다.

---

## 리소스 정리

이번 챕터에서 생성한 두 개의 메모리 리소스(`workshop_memory`, `workshop_memory_ltm`)는 삭제하지 않으면 이벤트와 메모리 레코드를 계속 저장합니다. 실습을 마쳤다면 두 리소스를 모두 삭제합니다.

**1.** 메모리 리소스 목록과 ID를 확인합니다.

```bash
aws bedrock-agentcore-control list-memories --query 'memories[].[id,status]' --output table
```

**2.** ID를 지정하여 각 메모리를 삭제합니다.

```bash
aws bedrock-agentcore-control delete-memory --memory-id $AGENTCORE_MEMORY_ID
aws bedrock-agentcore-control delete-memory --memory-id $AGENTCORE_MEMORY_LTM_ID
```

환경 변수가 더 이상 설정되어 있지 않다면, 1번에서 확인한 ID를 직접 전달합니다.

```bash
aws bedrock-agentcore-control delete-memory --memory-id workshop_memory-pXxxxxxxxxx
aws bedrock-agentcore-control delete-memory --memory-id workshop_memory_ltm-pXxxxxxxxxx
```

**3.** 메모리가 삭제되었는지 확인합니다. 메모리를 삭제하면 그 안에 저장된 모든 이벤트와 추출된 메모리 레코드도 함께 삭제됩니다.

```bash
aws bedrock-agentcore-control list-memories
```

> [!WARNING]
> 삭제는 즉시 완료되지 않습니다. `list-memories` 목록에서 사라지기 전까지 잠시 `DELETING` 상태로 표시될 수 있습니다. 해당 리소스가 목록에 나오지 않을 때까지 명령을 다시 실행하여 확인하세요.

---

## 트러블슈팅

<details>
<summary>bedrock-agentcore 호출 시 AccessDeniedException 발생</summary>

`AccessDeniedException: User ... is not authorized to perform: bedrock-agentcore:CreateMemory` 와 같은 오류는 사용 중인 자격 증명에 AgentCore Memory 권한이 없다는 의미입니다. 다음 두 가지 계열의 작업 권한이 필요합니다.

- 컨트롤 플레인 (리소스 생성 및 관리): `CreateMemory`, `ListMemories`, `GetMemory`, `DeleteMemory`
- 데이터 플레인 (스크립트가 런타임에 호출): `CreateEvent`, `ListEvents`, `ListMemoryRecords`, `RetrieveMemoryRecords`

현재 어떤 자격 증명을 사용하는지 확인하고, 위 `bedrock-agentcore:*` 액션이 연결되어 있는지 점검합니다.

```bash
aws sts get-caller-identity
```

또한 메모리를 생성한 리전과 동일한 리전을 호출하고 있는지 확인하세요. `us-west-2` 에 생성한 메모리는 다른 리전에서 보이지 않으며, 이 경우 리소스를 찾을 수 없다는 오류나 권한 오류로 나타납니다.

</details>

<details>
<summary>메모리가 아직 CREATING 상태여서 스크립트가 실패함</summary>

새로 생성한 메모리는 `ACTIVE` 상태가 되기까지 약 1-2분이 걸리며, 그 전에는 이벤트를 저장할 수 없습니다. 상태를 확인하고 기다리세요.

```bash
aws bedrock-agentcore-control get-memory --memory-id $AGENTCORE_MEMORY_ID --query 'memory.status'
```

이 명령이 `"ACTIVE"` 를 반환한 후에 스크립트를 실행합니다. `list-memories` 를 사용한다면 해당 항목의 `status` 필드를 확인하세요.

환경 변수가 실제로 채워졌는지도 확인합니다. `echo $AGENTCORE_MEMORY_ID` 가 아무것도 출력하지 않거나 `None` 을 출력하면 export 명령의 `--query` 가 아무 메모리도 찾지 못한 것이며, 스크립트는 기본값인 `your-memory-id-here` 를 사용하여 실패합니다.

</details>

<details>
<summary>LTM 조회 결과가 비어 있음</summary>

LTM 추출은 비동기로 처리됩니다. `learn` 실행 직후에는 단기 이벤트만 저장되어 있고 아직 메모리 레코드가 추출되지 않았기 때문에, 조회 결과가 비어 있고 에이전트는 학습한 내용이 없는 것처럼 응답합니다. 다음 순서로 확인하세요.

1. **`learn` 실행 후 1-2분 기다린 다음** `retrieve` / `recommend` 모드를 다시 실행합니다.
2. **네임스페이스를 직접 조회**하여 레코드가 추출되었는지 확인합니다.

   ```bash
   aws bedrock-agentcore list-memory-records \
       --memory-id $AGENTCORE_MEMORY_LTM_ID \
       --namespace "/facts/user_charlie"
   ```

   선호도의 경우 `--namespace "/preferences/user_diana"` 를 사용합니다.
3. **STM 메모리 ID가 아니라 LTM 메모리 ID를 사용합니다.** LTM 스크립트는 `AGENTCORE_MEMORY_LTM_ID` 를 읽습니다. 전략이 없는 `workshop_memory` 리소스는 레코드를 추출하지 않습니다.
4. **액터 ID를 일치시킵니다.** 레코드는 `/facts/{actorId}` 경로에 저장되므로, `--actor user_charlie` 로 학습한 뒤 다른 `--actor` 로 조회하면 결과가 없습니다.
5. **관련성 임계값을 확인합니다.** `RetrievalConfig(relevance_score=...)` 는 관련성이 낮은 결과를 걸러냅니다 (`ltm_semantic.py` 는 `0.5`, `ltm_preference.py` 는 `0.3`). 레코드는 있는데 응답에 활용되지 않는다면 임계값을 낮추거나, 학습한 내용에 더 가까운 표현으로 질문해 보세요.

</details>

---
Prev: [관측 가능성](../04-observability/README.ko.md) | Next: [AgentCore Runtime](../06-agentcore-runtime/README.ko.md)
