# 07. 에이전트 가시성 (AgentCore Observability)

[English README](README.md)

> [!WARNING]
> 이 챕터를 진행하려면 먼저 [06. 에이전트 런타임 (AgentCore Runtime)](../06-agentcore-runtime/README.ko.md) 실습을 완료해야 합니다. 이 챕터는 이전 챕터에서 배포한 에이전트가 생성한 텔레메트리를 확인합니다. 배포된 에이전트가 없으면 대시보드에는 아무 데이터도 표시되지 않습니다.

이번 실습에서는 이전 챕터에서 AgentCore Runtime에 배포한 에이전트의 트레이스, 메트릭, 로그를 Amazon CloudWatch GenAI Observability 대시보드에서 확인하는 방법을 학습합니다.

> [!NOTE]
> **사전 준비 사항**
> - [00-setup](../00-setup/README.ko.md) 기준으로 환경 구성 완료
> - [06. 에이전트 런타임 (AgentCore Runtime)](../06-agentcore-runtime/README.ko.md) 완료 (`strands_workshop_agent`가 배포되어 호출 가능한 상태)
> - 계정에 CloudWatch Transaction Search 활성화 (C6에서 수행했으며, 아래에서 다시 확인합니다)
> - CloudWatch 메트릭, 로그, 트레이스를 조회할 수 있는 권한이 있는 AWS Management Console 접근

**학습 내용**

- AgentCore Runtime이 자동으로 발행하는 텔레메트리의 종류와 저장 위치
- CloudWatch GenAI Observability 대시보드 읽는 방법: Agents, Sessions, Traces 뷰
- `Bedrock-AgentCore` 네임스페이스에 발행되는 Runtime 메트릭
- 에이전트의 stdout/stderr 및 OTEL 구조화 로그가 저장되는 CloudWatch Logs 위치

**예상 소요 시간:** 약 10분

## 이 챕터의 파일

이 챕터에는 별도의 코드가 없습니다. 모든 작업은 C6에서 배포한 에이전트를 대상으로 AWS Management Console에서 진행합니다. 실행하는 명령은 이전 챕터의 호출 스크립트 하나뿐입니다.

| 파일 | 용도 |
|---|---|
| `../06-agentcore-runtime/labs/invoke_agent.py` | 배포된 에이전트를 호출하여 텔레메트리 생성 |

---

## AgentCore Observability란?

<img src="../docs/images/agentcore-observability-logo.png" alt="AgentCore logo" width="800">

AgentCore Runtime에 배포된 에이전트는 자동으로 텔레메트리 데이터를 생성합니다. [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)는 이 데이터를 Amazon CloudWatch에 수집하고, GenAI 전용 대시보드를 통해 시각화합니다.

### 자동으로 수집되는 데이터

- **트레이스**: 에이전트 호출부터 모델 추론, 도구 실행까지의 전체 경로
- **메트릭**: 세션 수, 지연 시간, 토큰 사용량, 에러율
- **로그**: 에이전트 프로세스의 stdout/stderr 출력

계측 코드를 작성할 필요가 없습니다. 이 점이 OTLP exporter를 직접 설정하고 컬렉터를 직접 실행했던 [04. Strands SDK로 가시성 확보하기](../04-observability/README.ko.md)와의 차이입니다.

---

## 1. Transaction Search 활성화 확인

> [!WARNING]
> 이 챕터의 대시보드에서 트레이스, 세션, 메트릭 데이터를 확인하려면 **CloudWatch Transaction Search가 활성화**되어 있어야 합니다. [C6](../06-agentcore-runtime/README.ko.md)의 사전 준비 단계에서 이미 활성화한 경우 이 섹션을 건너뛰어도 됩니다.

Transaction Search는 AWS 계정당 한 번만 수행하는 설정입니다. 활성화 후 트레이스가 검색 가능해지기까지 약 10분이 소요될 수 있으므로, 대시보드를 보기 시작한 뒤가 아니라 지금 확인해 두는 것이 좋습니다.

**1-1.** AWS 콘솔에서 [CloudWatch](https://console.aws.amazon.com/cloudwatch/) 서비스를 엽니다.

![CloudWatch](../../docs/images/c7-o11y_1.png)

**1-2.** 좌측 메뉴에서 **Settings**를 클릭한 뒤 **Application signals** 탭을 열고, **Transaction Search** 패널의 **Edit**을 클릭합니다.

![CloudWatch Settings](../../docs/images/c7-o11y_2.png)

**1-3.** **Enable Transaction Search**가 켜져 있고 Sample rate가 **100%** 인지 확인한 후 **Save**를 클릭합니다.

![Enable Transaction Search](../../docs/images/c7-o11y_3.png)

> [!WARNING]
> Sample rate를 기본값(1%)으로 두면 대부분의 트레이스가 수집되지 않아 대시보드에서 데이터를 확인할 수 없습니다. 이번 실습에서는 반드시 **100%** 로 설정해야 합니다.

---

## 2. 에이전트 호출하여 텔레메트리 생성

C6에서 배포한 에이전트를 호출하여 Observability 데이터를 생성합니다. 여러 번 호출하면 대시보드에서 더 풍부한 데이터를 확인할 수 있습니다.

```bash
uv run --project 00-setup python 06-agentcore-runtime/labs/invoke_agent.py
```

---

## 3. GenAI Observability 대시보드 확인

CloudWatch GenAI Observability 대시보드는 추가 설정 없이 에이전트 활동, 세션, 트레이스에 대한 즉각적인 인사이트를 제공합니다.

**3-1.** CloudWatch 콘솔 좌측 메뉴에서 **GenAI Observability** > **Bedrock AgentCore**를 선택합니다.

### Agents View

**3-2.** **Agents** 탭에서 배포된 에이전트의 전체 현황을 확인할 수 있습니다.

- **Summary metrics**: 총 세션 수, 트레이스, 에러, 스로틀
- **Runtime metrics**: 세션 수, 호출 횟수, 에러, 지연 시간 추세 (시계열 그래프)
- **Per-agent breakdown**: 각 에이전트별 세션, 트레이스, 에러, P95 지연 시간

### Sessions View

**3-3.** **Sessions** 탭에서 세션별 대화 흐름을 확인할 수 있습니다.

- 세션 ID, 트레이스 수, 에러, P95 지연 시간으로 정렬 가능
- 세션 ID를 클릭하면 해당 세션의 상세 메트릭과 트레이스로 이동
- 높은 지연 시간이나 반복된 에러가 있는 세션을 비교하여 이상 징후 발견 가능

### Traces View

**3-4.** **Traces** 탭에서 개별 요청의 실행 경로를 확인할 수 있습니다.

- 트레이스 ID, 스팬 수, 에러, 지연 시간으로 정렬 및 필터링 가능
- 트레이스를 클릭하면 에이전트의 실행 경로를 계층적으로 확인할 수 있습니다.
  - 에이전트 호출, 모델 추론, 도구 실행 순서
  - 각 단계의 소요 시간
  - 도구 호출 파라미터 및 결과

![GenAI Observability Dashboard](../../docs/images/c7-o11y_8.png)

---

## 4. CloudWatch 메트릭 확인

AgentCore는 **AWS/Bedrock-AgentCore** 네임스페이스 아래에 메트릭을 자동으로 발행합니다.

**4-1.** CloudWatch 콘솔 좌측 메뉴에서 **Metrics** > **All metrics**를 선택합니다.

**4-2.** 메트릭 브라우저에서 네임스페이스 **Bedrock-AgentCore**를 선택합니다.

**4-3.** 검색창에 `strands_workshop_agent`를 입력하여 배포한 에이전트의 메트릭을 필터링합니다.

**4-4.** 다음 Runtime 메트릭을 확인할 수 있습니다.

| 메트릭 | 설명 |
|--------|------|
| **Invocations** | 에이전트가 수신한 총 요청 수 |
| **Latency** | 요청부터 최종 응답까지의 종단 간 응답 시간 |
| **Sessions** | 활성 에이전트 세션 수 |
| **UserErrors** | 클라이언트 측 에러 (400, 403, 404) |
| **SystemErrors** | 서버 측 에러 (500) |
| **Throttles** | 제한 초과로 거부된 요청 (429) |

![CloudWatch Metrics](../../docs/images/c7-o11y_4.png)

---

## 5. CloudWatch 로그 확인

AgentCore Runtime은 에이전트의 로그를 자동으로 CloudWatch Logs에 전송합니다.

**5-1.** CloudWatch 콘솔 좌측 메뉴에서 **Log Management**를 선택합니다.

**5-2.** 검색창에 `/aws/bedrock-agentcore/runtimes/strands_workshop_agent`를 입력합니다.

![Log Group Filtering](../../docs/images/c7-o11y_5.png)

**5-3.** 로그 그룹을 클릭하면 두 가지 유형의 로그 스트림을 확인할 수 있습니다.

- **runtime-logs**: 에이전트의 stdout/stderr 출력 (Python print 문, 에러 트레이스백 등)
- **otel-rt-logs**: OTEL 구조화 로그 (실행 상세, 에러 추적, 성능 데이터)

**5-4.** `runtime-logs`가 포함된 로그 스트림을 클릭하면 에이전트 실행의 상세 로그를 확인할 수 있습니다.

![Runtime Log Filtering](../../docs/images/c7-o11y_6.png)

![Runtime Log Results](../../docs/images/c7-o11y_7.png)

---

## 관리형 가시성과 직접 구성하는 가시성

이제 두 가지 방식을 모두 확인했습니다.

| | [04. Strands SDK로 가시성 확보하기](../04-observability/README.ko.md) | 이 챕터 |
|---|---|---|
| 계측 | 코드에 `StrandsTelemetry`를 추가하고 `OTEL_EXPORTER_OTLP_ENDPOINT`를 설정 | 없음, AgentCore Runtime이 자동 발행 |
| 백엔드 | 직접 실행하는 컬렉터 (Docker 기반 로컬 Jaeger) | Amazon CloudWatch |
| 적용 범위 | 에이전트를 실행할 수 있는 모든 환경 (로컬 노트북 포함) | AgentCore Runtime에 배포된 에이전트 |

에이전트를 로컬에서 실행하거나 직접 운영하는 OpenTelemetry 백엔드로 텔레메트리를 보낼 때는 C4의 방식을 사용합니다. 에이전트를 AgentCore Runtime에 배포한 뒤에는 이 챕터의 방식을 사용합니다.

---

## 리소스 정리

이 챕터는 새 리소스를 만들지 않지만, 조회하는 데이터에는 비용이 발생합니다.

- **CloudWatch Transaction Search**는 모든 스팬을 `aws/spans` 로그 그룹에 구조화 로그로 수집하며, Application Signals 요금제로 과금됩니다. 이번 실습에서 사용한 100% 샘플 레이트는 기본값(1%)보다 비용이 높습니다.
- **CloudWatch Logs와 트레이스**는 만료되거나 삭제할 때까지 보관되며, 보관 비용이 과금됩니다.

워크샵 이후 Transaction Search를 켜 두고 싶지 않다면 활성화했던 곳에서 다시 끌 수 있습니다. CloudWatch 콘솔 > **Settings** > **Application signals** 탭 > **Transaction Search** > **Edit** 에서 **Enable Transaction Search** 토글을 끄고 저장합니다. **Log Management**에서 `/aws/bedrock-agentcore/runtimes/strands_workshop_agent` 로그 그룹을 삭제하거나 보관 기간을 짧게 설정할 수도 있습니다.

배포한 에이전트 자체와 그 뒤의 ECR 이미지, IAM 역할은 [C6](../06-agentcore-runtime/README.ko.md)에서 만든 리소스입니다. 실습을 마친 뒤 해당 챕터에서 정리하세요.

---

## 참고 자료

- [AgentCore Observability 시작하기](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html)
- [AgentCore Observability 데이터 확인](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-view.html)
- [AgentCore Observability 리소스 구성](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html)
- [AgentCore Starter Toolkit - Observability 퀵스타트](https://aws.github.io/bedrock-agentcore-starter-toolkit/user-guide/observability/quickstart.html#getting-started-with-agentcore-observability)

---
Prev: [에이전트 런타임 (AgentCore Runtime)](../06-agentcore-runtime/README.ko.md) | Next: [Kiro IDE로 개발하기](../08-kiro-dev/README.ko.md)
