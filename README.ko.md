# Agentic AI 101 on AWS

[English README](README.md)

[Strands Agents SDK](https://strandsagents.com/latest/)로 AI 에이전트를 처음부터 만들고, [Amazon Bedrock AgentCore](https://aws.amazon.com/ko/bedrock/agentcore/)로 배포·운영하는 과정을 다루는 핸즈온 워크샵입니다.

각 챕터는 `labs/` 폴더와 `completed/` 폴더로 구성됩니다. `labs/`의 빈 파일에 직접 코드를 작성하고, `completed/`의 완성된 코드와 비교하면서 학습합니다.

![Agentic AI 101 on AWS](docs/images/agentic-ai-101.png)

**레벨:** 100~200 (입문~중급). 에이전트나 LLM 사전 경험이 없어도 진행할 수 있습니다.
**소요 시간:** 필수 챕터 기준 약 3시간.

---

## 챕터 구성

| # | 챕터 | 내용 | 구분 |
|---|------|------|------|
| 00 | [환경 설정](00-setup/README.ko.md) | Python 환경, AWS 자격 증명, Bedrock 모델 액세스 | 필수 |
| 01 | [단일 에이전트](01-single-agent/README.ko.md) | Prompt·Model·Tools 기본 구성, Bedrock Knowledge Base, MCP 도구, 자가개선 에이전트 | 필수 |
| 02 | [멀티 에이전트 패턴](02-multi-agents/README.ko.md) | Agents-as-Tools, Swarm, Graph | 필수 |
| 03 | [챗봇 애플리케이션](03-chatbot-app/README.ko.md) | Streamlit 채팅 UI, 스트리밍 응답, 도구 호출 시각화 | 선택 |
| 04 | [Strands Observability](04-observability/README.ko.md) | 메트릭, 로그, OTLP 트레이스와 로컬 Jaeger | 선택 |
| 05 | [에이전트 메모리](05-agent-memory/README.ko.md) | AgentCore Memory 단기·장기 메모리 | 필수 |
| 06 | [AgentCore Runtime](06-agentcore-runtime/README.ko.md) | 에이전트 서버리스 배포 | 필수 |
| 07 | [AgentCore Observability](07-agentcore-observability/README.ko.md) | CloudWatch GenAI Observability 대시보드 | 필수 |
| 08 | [Kiro IDE로 개발하기](08-kiro-dev/README.ko.md) | Steering, MCP 설정, 스펙 기반 개발 | 선택 |

> [!TIP]
> 01, 02, 05, 06, 07 챕터가 핵심 경로입니다. 03, 04, 08 챕터는 독립적으로 구성되어 있어 건너뛸 수 있습니다.

---

## 빠르게 시작하기

**사전 요구사항**

- Amazon Bedrock 호출과 AgentCore 리소스 생성이 가능한 권한의 AWS 계정
- `us-west-2` 리전에서 아래 표의 Anthropic Claude 모델 액세스 활성화
- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker (04, 06 챕터에만 필요)
- AWS CLI 설정 완료 (`aws configure`), 기본 리전 `us-west-2`

**설치**

```bash
git clone https://github.com/aws-samples/sample-aws-agentic-ai-workshop.git
cd sample-aws-agentic-ai-workshop/00-setup
uv sync
cd ..
```

**첫 에이전트 실행**

```bash
uv run --project 00-setup python 01-single-agent/completed/basic.py
```

에이전트 응답이 출력되면 환경 준비가 끝났습니다. 자세한 설정 안내는 [00-setup/README.ko.md](00-setup/README.ko.md)를 참고하고, [01 챕터](01-single-agent/README.ko.md)부터 실습을 시작하세요.

---

## 사용 모델과 리전

모든 실습은 **`us-west-2`** 리전의 Amazon Bedrock을 사용합니다. 시작 전에 아래 모델의 액세스를 활성화하세요.

| 모델 ID | 사용 위치 |
|---|---|
| `us.anthropic.claude-sonnet-4-20250514-v1:0` | 01~06 챕터 |
| `us.anthropic.claude-sonnet-4-6` | 01 챕터 자가개선 에이전트 실습, 02 챕터 |
| `us.amazon.nova-pro-v1:0` | 04 챕터 메트릭 실습 |

[Bedrock 콘솔](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess)의 **Model access**에서 활성화합니다. `us.` 접두사가 붙은 모델 ID는 교차 리전 추론 프로파일이며, 프로파일 대상 리전의 액세스는 콘솔에서 함께 처리됩니다.

---

## 레포지토리 구조

```
sample-aws-agentic-ai-workshop/
├── 00-setup/                     # 환경 설정, uv 프로젝트, 의존성
│   ├── pyproject.toml
│   ├── uv.lock
│   └── create-uv-env.sh
├── 01-single-agent/
│   ├── labs/                     # 직접 작성하는 파일
│   ├── completed/                # 완성된 참고 코드
│   └── README.md
├── 02-multi-agents/
├── 03-chatbot-app/
├── 04-observability/
│   └── docker/                   # OTel Collector + Jaeger
├── 05-agent-memory/
├── 06-agentcore-runtime/
├── 07-agentcore-observability/   # 콘솔 실습 전용, README만 존재
├── 08-kiro-dev/
│   └── .kiro/                    # steering 규칙과 MCP 설정
└── docs/images/                  # 챕터 README에서 참조하는 스크린샷
```

모든 챕터 폴더는 동일한 구조를 따릅니다.

```
NN-chapter/
├── README.md        # 영문 실습 가이드
├── README.ko.md     # 한글 실습 가이드
├── labs/            # 빈 파일, 직접 코드를 작성합니다
└── completed/       # 참고 답안, 막히면 실행해 보세요
```

---

## 비용과 리소스 정리

실습은 Bedrock 모델을 호출하며, 일부 챕터는 존재하는 동안 계속 과금되는 AWS 리소스를 생성합니다.

| 챕터 | 생성되는 리소스 |
|---|---|
| 01 | Bedrock Knowledge Base, OpenSearch Serverless 컬렉션, S3 버킷 |
| 05 | AgentCore Memory 리소스 |
| 06 | AgentCore Runtime, ECR 리포지토리, IAM 실행 역할, CloudWatch 로그 그룹 |
| 07 | CloudWatch Transaction Search 수집, 트레이스·로그 보관 |

> [!WARNING]
> 각 챕터에는 **리소스 정리** 섹션이 있습니다. 실습을 마치면 특히 01, 05, 06 챕터의 정리 단계를 반드시 수행하세요. 특히 OpenSearch Serverless 컬렉션은 조회하지 않아도 계속 과금됩니다.

---

## 참고 자료

- [Strands Agents SDK 공식 문서](https://strandsagents.com/latest/documentation/)
- [멀티 에이전트 패턴 가이드](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/)
- [Amazon Bedrock 사용자 가이드](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock AgentCore 개발자 가이드](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWS MCP 서버](https://awslabs.github.io/mcp/)

## 보안

보안 이슈 제보 방법은 [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications)을 참고하세요.

## 라이선스

이 코드는 MIT-0 라이선스를 따릅니다. [LICENSE](LICENSE)를 참고하세요.
