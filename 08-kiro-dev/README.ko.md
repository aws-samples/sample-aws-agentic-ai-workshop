# 08. Kiro IDE로 개발하기

[English README](README.md)

> [!NOTE]
> 이 챕터는 **선택 사항**입니다. C1부터 C7까지의 내용을 전제로 하지 않으며, 이후 챕터가 이 챕터에 의존하지도 않습니다. Strands Agents와 AgentCore 경로만 진행하려면 건너뛰어도 됩니다.

이번 챕터에서는 AWS의 AI 기반 IDE인 **Kiro**를 활용하여 Strands Agents 개발 환경을 구성하고, 실제 개발 워크플로우를 체험합니다. Power 설치, Steering 규칙 정의, MCP 서버 연결을 거친 뒤 Kiro가 Strands 에이전트를 직접 작성하게 합니다.

## Kiro란?

[Kiro](https://kiro.dev/)는 AWS에서 제공하는 AI 기반 통합 개발 환경(IDE)입니다. VS Code 기반으로 구축되어 익숙한 개발 경험을 제공하면서도, AI 에이전트가 개발 과정 전반을 지원합니다.

![Kiro logo](../docs/images/kiro-logo.png)

### Kiro의 주요 특징

- **Spec 기반 개발**: 요구사항부터 설계, 구현까지 체계적인 개발 프로세스 지원
- **Steering**: 프로젝트별 컨텍스트와 규칙을 정의하여 AI가 일관된 코드 생성
- **Hooks**: IDE 이벤트에 반응하는 자동화 워크플로우 구성
- **Powers**: MCP 서버와 문서를 패키징하여 도메인별 AI 역량 확장

> [!NOTE]
> **사전 준비 사항**
> - [00-setup](../00-setup/README.ko.md) 기준으로 환경 구성 완료
> - `us-west-2` 리전에서 Anthropic Claude 모델 액세스 활성화 (Kiro가 생성한 에이전트를 실행하기 위해 필요)
> - Kiro IDE ([kiro.dev](https://kiro.dev/)에서 직접 설치하거나, 워크샵 환경에서 제공되는 것을 사용)
> - Kiro 구독 (실습 체험에는 Free 티어로도 충분하며, 워크샵에서는 Kiro Pro를 사용합니다)

**학습 내용**

- Kiro Power가 특정 기술 스택용 MCP 서버와 문서를 패키징하는 방식
- Steering 파일이 Kiro의 코드 생성을 제약하는 방식과 파일 위치
- Kiro가 Strands SDK 문서를 조회할 수 있도록 MCP 서버를 등록하는 방법
- 자연어 프롬프트 하나로 동작하는 Strands 에이전트를 만들고, 검토하고, 실행하는 방법

**예상 소요 시간:** 약 30분

## 이 챕터의 파일

| 파일 | 용도 |
|---|---|
| `labs/hanoi_tower.py` | (빈 파일) 실습 중 Kiro가 생성합니다 |
| `completed/hanoi_tower.py` | 참고용 결과물, 이 실습을 작성할 때 Kiro가 생성한 에이전트 |
| `.kiro/steering/strands-dev.md` | 이 폴더에서 코드를 생성할 때 Kiro가 따르는 Steering 규칙 |
| `.kiro/settings/mcp.json` | 이 폴더의 MCP 서버 설정 |

이 챕터도 워크샵의 다른 챕터와 같은 `labs/`, `completed/` 구조를 따르지만 한 가지가 다릅니다. `labs/hanoi_tower.py`는 직접 타이핑하지 않고 Kiro가 작성합니다. `completed/hanoi_tower.py`는 참고용 결과물로, Kiro가 여러분에게 생성해 준 코드와 비교해 볼 수 있습니다. 언어 모델이 파일을 생성하므로 여러분의 결과물은 완전히 동일하지 않으며, 이는 정상입니다.

---

## 실습 환경: 워크샵 제공 환경과 개인 환경

AWS에서 제공하는 워크샵 환경은 Kiro IDE가 미리 설치된 EC2 인스턴스를 프로비저닝하고 NICE DCV 원격 데스크톱 세션으로 접속하도록 구성되어 있어, 참가자가 로컬에 별도로 설치할 필요가 없습니다. 아래 두 개의 `<details>` 섹션이 그 경로를 다룹니다. AWS 콘솔에서 Kiro 구독 사용자를 생성하고, 원격 데스크톱에 접속하는 절차입니다.

**개인 환경에서 이 리포지토리로 실습한다면 두 섹션을 모두 건너뛰세요.** [https://kiro.dev/](https://kiro.dev/)에서 Kiro를 설치하고, 원하는 방식으로 로그인한 뒤, 이 리포지토리를 폴더로 열고 [개발 환경 구성](#개발-환경-구성)부터 진행하면 됩니다.

<details>
<summary>Kiro 구독 설정 (워크샵 제공 환경)</summary>

AWS Management Console에서 Kiro 프로파일을 생성하고 구독을 설정합니다.

### Kiro 구독이란?

Kiro는 크레딧 기반의 요금제를 제공합니다. AWS 콘솔에서 조직 사용자를 생성하고 구독 플랜을 연결할 수 있습니다.

| 티어 | 월 요금 | 크레딧 | 초과 사용 |
|------|---------|--------|-----------|
| **Free** | $0 | 50 크레딧 | - |
| **Pro** | $20 | 1,000 크레딧 | $0.04/크레딧 |
| **Pro+** | $40 | 2,000 크레딧 | $0.04/크레딧 |
| **Power** | $200 | 10,000 크레딧 | $0.04/크레딧 |

> [!NOTE]
> **크레딧이란?**
> 크레딧은 Kiro AI 기능 사용량을 측정하는 단위입니다. 코드 생성, 채팅, Spec 작성 등 AI 기능을 사용할 때마다 크레딧이 소모됩니다.

<img src="../docs/images/c7-kiro-plans.png" alt="Kiro Console" width="800">

### 1단계: Kiro 프로파일 만들기

N.Virginia 리전의 AWS 콘솔에서 Kiro 프로파일을 생성합니다.

**1.** AWS 콘솔에서 [Kiro 콘솔](https://us-east-1.console.aws.amazon.com/amazonq/developer/home)로 이동합니다.

<img src="../docs/images/c7-kiro-console.png" alt="Kiro Console" width="800">

**2.** **Enable small teams**를 클릭합니다. 이 기능으로 Kiro 사용자를 신규 등록하고 구독 플랜을 연결할 수 있습니다.

<img src="../docs/images/c7-kiro-add-user.png" alt="Kiro Create User" width="800">

**3.** 사용자 정보를 입력합니다.
- **이메일 주소**: 정확하게 입력해주세요 (후속 절차에 필요)
- **이름** (First name)
- **성** (Last name)

**4.** 사용자 정보를 입력하고 **계속**을 클릭합니다.

**5.** 이 유저에게 할당할 Kiro 구독 플랜을 선택합니다. **Kiro Pro**를 선택하고 **Continue**를 클릭합니다.

<img src="../docs/images/c7-kiro-plan-selection.png" alt="Kiro Plan Selection" width="800">

**6.** **Enable and Subscribe**를 클릭합니다.

<img src="../docs/images/c7-kiro-enable-subs.png" alt="Kiro Enable and Subscribe" width="800">

### 2단계: 다중인증(MFA) 설정

Kiro 프로파일 생성 시 함께 설정된 IAM Identity Center 조직 인스턴스의 MFA 정책을 구성합니다.

**7.** N.Virginia의 [AWS IAM Identity Center 콘솔](https://us-east-1.console.aws.amazon.com/singlesignon/home)로 이동합니다.

<img src="../docs/images/c7-sso-console.png" alt="IAM Identity Center Console" width="800">

**8.** **Configure MFA**를 클릭합니다.

<img src="../docs/images/c7-sso-mfa-config.png" alt="MFA Configuration" width="800">

**9.** 이번 실습에서는 MFA 인증 절차를 생략합니다. **Prompt users for MFA** 속성에서 **Never**를 선택하고 저장합니다.

> [!WARNING]
> **프로덕션 환경 권장사항**
> 프로덕션 환경에서는 향상된 보안을 위해 IAM Identity Center 조직 인스턴스에서 다중인증 정책을 구성하는 것이 바람직합니다.

### 3단계: 이메일 인증 및 구독 확인

등록한 이메일로 전송된 초대를 수락하고 구독을 활성화합니다.

**10.** 등록한 이메일로 전송된 초대 메일에서 **초대 수락** 버튼을 클릭합니다.

<img src="../docs/images/c7-kiro-invitation-email.png" alt="Invitation Email" width="800">

> [!NOTE]
> **주요 정보**
> 초대 메일에는 Kiro IDE 조직 사용자로 로그인할 때 필요한 정보가 제공됩니다. 다음 항목을 메모해 두세요.
> - **Your AWS access portal URL**

**11.** 새 사용자의 비밀번호를 설정합니다.

<img src="../docs/images/c7-kiro-set-password.png" alt="Set Password" width="800">

**12.** AWS access portal로 이동됩니다. 이 유저가 Kiro 서비스에 접근하도록 허가하는 절차입니다.

<img src="../docs/images/c7-kiro-access-portal.png" alt="Kiro Access Portal" width="800">

### 구독 확인

**13.** [Kiro 콘솔](https://us-east-1.console.aws.amazon.com/amazonq/developer/home)로 돌아갑니다.

**14.** 좌측 메뉴에서 **Users & Groups** > **Users** 탭을 확인합니다.

<img src="../docs/images/c7-kiro-user-tab.png" alt="Kiro User Tab" width="800">

<img src="../docs/images/c7-kiro-sub-tab.png" alt="Kiro Subscription Tab" width="800">

현재 Kiro Pro 플랜에 등록된 사용자가 확인됩니다. 여러분이 제공한 정보와 일치하는지 확인해 주세요.

> [!NOTE]
> **구독 활성 시점**
> **대기중** 상태의 Kiro 구독은 첫 사용이 발생한 후 **활성** 상태로 변경됩니다.

</details>

<details>
<summary>NICE DCV로 Kiro IDE 접속 (워크샵 제공 환경)</summary>

### Amazon DCV란?

[Amazon DCV](https://aws.amazon.com/hpc/dcv/)는 고성능 원격 데스크톱 프로토콜로, 클라우드 환경의 그래픽 워크스테이션에 안전하게 접속할 수 있게 해줍니다. 이 워크샵에서는 DCV를 통해 Kiro IDE가 설치된 환경에 접속합니다.

### Kiro IDE 접속

**1.** AWS 콘솔에서 **CloudFormation** 서비스로 이동합니다.

**2.** 워크샵용 스택을 선택하고 **Outputs** 탭을 클릭합니다.

**3.** 다음 값들을 확인합니다.

| Output Key | 설명 |
|------------|------|
| **KiroIDEURL** | Kiro IDE 접속 URL (DCV 웹 클라이언트) |
| **Password** | 로그인 비밀번호 |

<img src="../docs/images/c7-cfn-outputs.png" alt="CloudFormation Outputs" width="800">

**4.** **KiroIDEURL** 값을 복사하여 브라우저에서 새 탭으로 엽니다.

**5.** DCV 로그인 화면이 나타나면 다음 정보를 입력합니다.

- **Username**: `ec2-user`
- **Password**: CloudFormation Output의 **Password** 값

<img src="../docs/images/c7-dcv-login.png" alt="DCV Login" width="800">

**6.** 로그인 후 데스크톱 환경이 표시됩니다.

**7.** 앱 목록 또는 바탕화면에서 **Kiro IDE** 아이콘을 찾아 클릭하여 실행합니다.

<img src="../docs/images/c7-kiro-icon-search.png" alt="Kiro IDE Icon" width="800">

<img src="../docs/images/c7-kiro-icon.png" alt="Kiro IDE Icon" width="800">

### Kiro IDE 초기 설정

**8.** Kiro IDE가 실행되면 **Sign in**을 진행하고, 나타난 화면에서 **Your organization** 옵션으로 로그인합니다.

<img src="../docs/images/c7-kiro-login-options.png" alt="Kiro Login Options" width="800">

<img src="../docs/images/c7-org-start-url.png" alt="Organization Start URL" width="800">

- Start URL: 조직 초대 과정에서 받은 메일에서 조직 URL 정보를 확인해서 기입합니다.

**9.** 로그인이 완료되면 Kiro IDE 메인 화면이 표시됩니다.

<img src="../docs/images/c7-kiro-main.png" alt="Kiro IDE Main" width="800">

> [!WARNING]
> **접속 문제 해결**
> DCV 접속이 안 되는 경우:
> 1. CloudFormation 스택이 `CREATE_COMPLETE` 상태인지 확인
> 2. 보안 그룹에서 DCV 포트(8443)가 열려있는지 확인
> 3. 브라우저 팝업 차단이 해제되어 있는지 확인

### 워크샵 프로젝트 열기

**10.** Kiro IDE에서 **File** > **Open Folder**를 선택합니다.

**11.** 워크샵 실습 디렉토리를 선택합니다.

```text
/home/ec2-user/workspace/my-workspace/dev
```

<img src="../docs/images/c7-open-project.png" alt="Open Project" width="800">

**12.** 프로젝트가 열리면 좌측 Explorer에서 파일 구조를 확인할 수 있습니다.

</details>

---

## 개발 환경 구성

Kiro의 **Power**와 **Steering**을 활용하여 Strands Agents 개발 환경을 구성합니다.

### Kiro Power란?

Power는 Kiro에서 MCP(Model Context Protocol) 서버, 문서, 워크플로우 가이드를 패키징한 것입니다. 특정 도메인이나 기술 스택에 맞는 AI 역량을 확장할 수 있습니다.

**Power의 구성 요소**

- **MCP 서버**: 외부 도구와 데이터 소스 연결
- **문서 (POWER.md)**: 도메인 지식과 사용 가이드
- **Steering 파일**: 워크플로우별 상세 지침

### Strands Agents Power 설치

**1.** Kiro IDE에서 **Command Palette**를 엽니다 (`Cmd+Shift+P` 또는 `Ctrl+Shift+P`).

**2.** `View: Show Powers`를 검색하여 실행합니다.

**3.** Powers 패널에서 **Browse Powers**를 클릭합니다.

**4.** Available 창에서 **Build an agent with Strands** Power를 찾습니다.

<img src="../docs/images/c7-get-strands-power.png" alt="Strands Power" width="800">

**5.** **Install** 버튼을 클릭하여 Power를 설치합니다.

> [!NOTE]
> **Power 설치 확인**
> 설치된 Power는 `.kiro/powers/` 디렉토리에 저장됩니다. Powers 패널의 **Installed** 탭에서 확인할 수 있습니다.

### Steering 규칙

Steering은 Kiro AI가 코드를 생성할 때 따라야 할 규칙과 컨텍스트를 정의합니다. Steering 파일은 `.kiro/steering/` 하위의 마크다운 파일로, 앞부분에 작은 frontmatter 블록이 붙습니다. `inclusion: always`로 설정하면 Kiro가 해당 워크스페이스의 모든 요청에서 이 파일을 컨텍스트로 불러오므로, 매 프롬프트마다 규칙을 다시 적을 필요가 없습니다.

이 리포지토리에는 실습용 Steering 파일이 [`.kiro/steering/strands-dev.md`](.kiro/steering/strands-dev.md)에 이미 포함되어 있습니다. 주요 규칙은 다음과 같습니다.

**작업 디렉토리**

> `코드 산출물은 08-kiro-dev/labs/ 하위에 생성합니다.`

> [!NOTE]
> 이 규칙 덕분에 Kiro가 생성한 에이전트 코드가 임의의 위치가 아니라 `08-kiro-dev/labs/`에 저장됩니다. 다른 폴더를 워크스페이스로 열었다면 워크스페이스 루트 기준 상대 경로로 맞춰 수정하세요.

**코드 스타일**

> - Python 3.11+ 문법 사용
> - Type hints 필수 적용
> - Docstring은 Google 스타일 사용

**Strands SDK 규칙**

> - Agent 생성 시 항상 `system_prompt` 명시
> - 도구 함수는 `@tool` 데코레이터 사용
> - 모델은 Amazon Bedrock Claude 모델 사용
> - MCP 도구가 제공하는 Strands SDK 문서를 참고하며 정확하게 개발

**모델 설정**

> - 기본 모델: `us.anthropic.claude-sonnet-4-20250514-v1:0`
> - 리전: `us-west-2`

**에러 처리**

> - 모든 에이전트 호출은 try-except로 감싸기
> - 로깅은 strands 내장 로거 사용

**OTLP 트레이스 생성**

> - Strands SDK의 Otel 확장을 활용하여 OTLP 트레이스를 전송해야 합니다.
> - OTLP Receiver 주소(`OTEL_EXPORTER_OTLP_ENDPOINT`) = `"http://localhost:4318"`

파일 마지막에는 생성될 코드의 형태를 고정하는 기본 예제가 들어 있습니다.

```python
import os
from strands import Agent
from strands.tools import tool
from strands.telemetry import StrandsTelemetry

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "<OTLP Receiver Endpoint>"

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()

@tool
def my_tool(param: str) -> str:
    """도구 설명"""
    return result

agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    name="<adequate name>",
    tools=[my_tool]
)

response = agent("Hello World!")
```

> [!NOTE]
> OTLP 엔드포인트 `http://localhost:4318`은 [04. Strands SDK로 가시성 확보하기](../04-observability/README.ko.md)에서 사용한 로컬 컬렉터입니다. 컬렉터를 실행하고 있지 않아도 생성된 에이전트는 동작하며, 트레이스만 전송되지 않습니다. 트레이스를 확인하려면 C4의 Jaeger 컨테이너를 먼저 실행하세요.

리포지토리에 포함된 파일을 쓰지 않고 직접 작성하고 싶다면, 프로젝트 루트에 `.kiro/steering/` 디렉토리를 만들고 `strands-dev.md` 파일을 추가한 뒤 다음 frontmatter로 시작합니다.

```markdown
---
inclusion: always
---
```

그 뒤에 위의 규칙들을 작성합니다.

### MCP 서버 구성

Kiro는 워크스페이스의 MCP 서버 설정을 `.kiro/settings/mcp.json`에서 읽습니다. 이 리포지토리의 [`.kiro/settings/mcp.json`](.kiro/settings/mcp.json)은 비어 있는 상태로 제공됩니다.

```json
{
  "mcpServers": {
  }
}
```

Kiro가 코드를 작성하면서 Strands Agents 문서를 조회할 수 있도록 `strands-docs` 서버를 채워 넣습니다.

```json
{
  "mcpServers": {
    "strands-docs": {
      "command": "uvx",
      "args": ["strands-agents-mcp-server"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": ["search_docs", "fetch_doc"]
    }
  }
}
```

이 설정은 `strands-docs`라는 서버 하나를 구성하며, 필요할 때 `uvx strands-agents-mcp-server`로 실행됩니다. Kiro는 이 서버를 통해 Strands Agents 문서에 대한 두 개의 도구를 얻습니다. 관련 페이지를 찾는 `search_docs`와 해당 페이지를 읽는 `fetch_doc`입니다. 두 도구 모두 `autoApprove`에 포함되어 있어 매번 확인을 거치지 않고 호출됩니다. 이 덕분에 "MCP 도구가 제공하는 Strands SDK 문서를 참고하며 정확하게 개발"이라는 Steering 규칙이 실제로 동작합니다. Kiro가 추측하지 않고 현재 API를 직접 확인할 수 있습니다.

변경 사항을 적용하려면 Kiro IDE를 재시작하거나 Command Palette에서 `Kiro: Reconnect MCP Servers`를 실행합니다.

---

## Vibe Coding 실습

### 하노이 탑 에이전트 생성

Power를 설치하고 Steering 규칙을 두고 MCP 서버까지 연결했으면, Kiro에게 에이전트를 만들어 달라고 요청합니다. Kiro 채팅창에 다음을 입력합니다.

```text
Strands SDK를 사용하여 하노이 탑 퍼즐을 풀어주는 Agent를 만들어 줘.
```

Kiro는 `.kiro/steering/strands-dev.md`를 읽고, `strands-docs` MCP 서버로 SDK를 조회한 뒤, 에이전트를 `08-kiro-dev/labs/hanoi_tower.py`에 작성합니다 (위에서 안내한 작업 디렉토리 규칙을 수정했다고 가정합니다). Kiro가 Steering 규칙에 맞는 코드를 생성하면 환경 구성이 완료된 것입니다.

생성된 코드를 검토한 뒤 실행합니다.

```bash
uv run --project 00-setup python 08-kiro-dev/labs/hanoi_tower.py
```

이 프롬프트에 대한 참고 결과물은 [`completed/hanoi_tower.py`](completed/hanoi_tower.py)에 있습니다. 공유 퍼즐 상태를 다루는 다섯 개의 `@tool` 함수(`initialize_hanoi`, `move_disk`, `get_current_state`, `check_solution`, `get_hint`)를 정의하고, Steering 규칙이 요구하는 모델과 system prompt로 `hanoi_tower_solver` 에이전트를 생성하며, 호출을 try-except로 감싸고, `http://localhost:4318`로 향하는 OTLP exporter를 설정합니다. 여러분의 결과물과 비교해 보세요. 세부 내용은 다르더라도 Steering 규칙에 따른 구조는 일치해야 합니다.

C4의 컬렉터를 실행한 상태라면 에이전트의 도구 호출이 스팬으로 표시됩니다.

<img src="../docs/images/c7-strands-hanoi-traces.png" alt="Strands Hanoi traces" width="800">

### 자유 실습

이제 직접 작성한 코드로 **Vibe Coding**을 체험합니다. 이전 챕터에서 작성한 파일 중 하나를 선택하여 Kiro와 함께 개선해보세요.

| 챕터 | 파일 | 개선 아이디어 |
|------|------|---------------|
| **01** | `01-single-agent/labs/custom_tool1.py` | 에러 처리, 로깅 |
| **02** | `02-multi-agents/labs/agents_as_tools.py` | 새 에이전트 추가 |
| **03** | `03-chatbot-app/labs/streamlit_app.py` | UI 개선 |
| **04** | `04-observability/labs/traces_otlp.py` | 커스텀 메트릭 |
| **05** | `05-agent-memory/labs/stm_persistence.py` | 대화 종료 시 요약 출력 |

> [!TIP]
> 채팅창에서 `#`을 입력하면 특정 파일이나 폴더를 컨텍스트로 지정할 수 있습니다. 예: `#custom_tool1.py`

**01 - 단일 에이전트**
```text
#custom_tool1.py 이 코드를 분석해줘. 개선할 수 있는 부분이 있을까?
```

**02 - 멀티 에이전트**
```text
#agents_as_tools.py 새로운 전문가 에이전트를 추가해줘
```

**03 - 애플리케이션**
```text
#streamlit_app.py UI를 개선하고 대화 히스토리 저장 기능을 추가해줘
```

**04 - Observability**
```text
#traces_otlp.py 커스텀 메트릭을 추가해줘
```

**05 - 에이전트 메모리**
```text
#stm_persistence.py 대화가 끝날 때 대화 내용을 요약해서 출력해줘
```

---

## 리소스 정리

Kiro 자체는 AWS 리소스를 만들지 않지만, 구독과 모델 호출에는 비용이 발생합니다.

- **Kiro Pro** 구독은 사용자당 월 $20입니다. 이번 워크샵만을 위해 생성했다면 [Kiro 콘솔](https://us-east-1.console.aws.amazon.com/amazonq/developer/home)의 **Users & Groups**에서 해당 사용자의 구독을 해지하거나 Free 티어로 변경하세요.
- Kiro 프로파일 생성을 위해 **IAM Identity Center** 조직 인스턴스가 새로 만들어졌고 더 이상 필요하지 않다면 삭제하세요.
- Kiro가 생성한 에이전트는 실행할 때마다 **Amazon Bedrock**을 호출하며, 다른 챕터와 동일하게 토큰 단위로 과금됩니다.
- Kiro IDE와 DCV를 실행하는 워크샵 EC2 인스턴스는 실행 중인 동안 과금됩니다. AWS 제공 워크샵 환경에서는 CloudFormation 스택과 함께 제거됩니다.

---

## 참고 자료

- [Kiro 공식 사이트](https://kiro.dev/)
- [Kiro Documentation](https://kiro.dev/docs/)
- [Strands Agents SDK](https://strandsagents.com/latest/)
- [Amazon DCV](https://aws.amazon.com/hpc/dcv/)

---

워크샵의 모든 챕터를 완료했습니다. Kiro와 함께 자유롭게 실험하고, 여러분만의 AI 에이전트를 만들어보세요.

---
Prev: [에이전트 가시성 (AgentCore Observability)](../07-agentcore-observability/README.ko.md) | [워크샵 개요로 돌아가기](../README.ko.md)
