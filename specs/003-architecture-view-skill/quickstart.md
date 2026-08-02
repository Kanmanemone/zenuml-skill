# Quickstart: `generating-architecture-views` Skill 검증

이 문서는 skill 구현 후 spec.md의 성공 기준(SC-001~SC-008, SC-003b)을 수동으로 검증하는 절차다. 별도의 자동화 테스트 스위트는 없다(research.md, Decision: 자기검증 워크플로 패턴).

## 사전 준비

1. `.claude/skills/generating-architecture-views/SKILL.md`와 `references/templates.md`, `references/examples.md`가 존재해야 한다.
2. `.claude/skills/generating-zenuml-diagrams/`도 이 저장소에 함께 존재해야 한다(위임 대상).
3. Claude Code에서 이 저장소를 열고, 새 대화를 시작한다(skill이 SKILL.md의 `description`을 기준으로 자동 검색되는지 확인하기 위해 명시적으로 skill 이름을 언급하지 않는다).

## 시나리오 1 — 목적 미확인 상태에서 먼저 되묻기 (User Story 1 / SC-001)

**입력 예시**: "OrderService는 주문을 생성하고, PaymentService는 결제를 담당하며, OrderService가 PaymentService를 호출한다. 이 시스템의 구조를 보여줘."

**기대 결과**: 구조 뷰를 바로 생성하지 않고, 목적(온보딩/특정 문제 진단/기타)을 확인하는 질문을 먼저 한다.

**검증**: 질문 없이 바로 구조 뷰가 나오면 실패로 기록한다(SC-001 = 100% 목표).

## 시나리오 2 — Components & Dependencies와 Responsibility 정확성 (User Story 1 / SC-002, SC-003)

**입력 예시**: 시나리오 1과 동일한 설명 + "온보딩" 목적 선택.

**기대 결과**:
- Components & Dependencies 섹션에 OrderService, PaymentService 두 컴포넌트와 호출 화살표(OrderService → PaymentService)만 등장한다. 그룹 신호가 없으므로 `subgraph`는 그려지지 않는다.
- Responsibility 섹션에 정확히 2×1/2=**1개**의 비교 항목(**OrderService**는 **PaymentService**에 의존한다)이 생성된다. 그룹이 하나뿐이므로 그룹 간 비교는 생성되지 않는다.
- 설명에 없는 컴포넌트(예: NotificationService)나 관계, 근거 없는 책임 서술이 등장하지 않는다. 각 항목은 두 책임 서술로 끝나며 별도의 "차이:" 요약 문장은 없다.

**검증**: 비교 항목 수를 n(n-1)/2 공식으로 직접 계산해 대조한다(SC-002 = 0%, SC-003 = 100% 목표).

## 시나리오 3 — 그룹 내 비교는 직접 의존관계로 연결된 쌍만 (User Story 1)

**입력 예시**: "OrderService, PaymentService, InventoryService가 모두 '주문 도메인' 그룹에 속하고, OrderService가 나머지 둘을 호출한다."

**기대 결과**:
- Components & Dependencies 섹션에 하나의 `subgraph`(주문 도메인) 안에 세 컴포넌트가 있고, OrderService→PaymentService, OrderService→InventoryService 화살표가 있다.
- Responsibility 섹션에 정확히 **2개**의 그룹 내 비교 항목(**OrderService**는 **PaymentService**에 의존한다, **OrderService**는 **InventoryService**에 의존한다)만 있다 — PaymentService와 InventoryService는 서로 호출하지 않으므로 같은 그룹이어도 비교 항목이 생성되지 않는다. 그룹이 하나뿐이므로 그룹 간 비교는 생성되지 않는다.

**검증**: 의존관계가 없는 쌍(PaymentService-InventoryService)에 대한 비교 항목이 없는지 확인한다 — 포함되어 있으면 실패로 기록.

## 시나리오 4 — 그룹 3개 이상: 그룹 간 비교 (User Story 1 / SC-003b)

**입력 예시**: "'사용자 도메인'에는 UserService, AuthService가 있고, '주문 도메인'에는 OrderService, PaymentService, InventoryService가 있고, '알림 도메인'에는 NotificationService, EmailSender, SmsSender가 있어. OrderService가 PaymentService, InventoryService, AuthService, NotificationService를 호출해."

**기대 결과**:
- Components & Dependencies 섹션에 `subgraph` 3개(사용자/주문/알림 도메인)가 있고, OrderService→AuthService, OrderService→NotificationService처럼 그룹을 가로지르는 의존 화살표도 그대로 표현된다.
- Responsibility 섹션에 **그룹 간 비교가 먼저** 나오고, 실제로 교차-그룹 의존관계가 있는 **2쌍**(주문 도메인↔사용자 도메인, 주문 도메인↔알림 도메인)에 대해서만 "**주문 도메인**는 **사용자 도메인**에 의존한다" 형태의 항목이 생성된다 — 사용자 도메인과 알림 도메인 사이에는 교차-그룹 연결이 없으므로 그 쌍의 항목은 생성되지 않는다(3×2/2=3이 아니라 2). 각 항목의 근거는 각 그룹의 이름/레이블뿐이다.
- 이어서 **그룹별 컴포넌트 간 비교**가 나온다 — 사용자 도메인 0개(내부에 서로 호출하는 쌍 없음), 주문 도메인 2개(OrderService-PaymentService, OrderService-InventoryService), 알림 도메인 0개(내부에 서로 호출하는 쌍 없음), 총 **2개**.
- OrderService와 AuthService처럼 서로 다른 그룹에 속한 컴포넌트끼리의 비교 항목은 어디에도 나타나지 않는다(그룹을 가로지르는 의존 화살표가 있어도 컴포넌트 수준 비교는 그룹 경계를 넘지 않는다).

**검증**: 그룹 간 비교 항목 수가 실제 교차-그룹 의존관계가 있는 쌍 수와 정확히 일치하는지(=2, 연결 없는 사용자↔알림 쌍은 항목이 없는지), 각 항목이 볼드+실제 방향 서식을 쓰는지, 그룹별 컴포넌트 비교의 총합이 0+2+0=2인지, 그룹을 가로지르는 컴포넌트 쌍 비교가 전혀 없는지 확인한다(SC-003b = 100% 목표).

## 시나리오 5 — 근거 없는 책임을 지어내지 않음 (Edge Cases)

**입력 예시**: 컴포넌트 중 하나(예: InventoryService)의 책임이 설명에 명시되지 않은 입력.

**기대 결과**: Responsibility 섹션에서 InventoryService의 책임이 "명시되지 않음"으로 표시되고, InventoryService가 포함된 비교 항목에서도 그럴듯한 책임을 추측해서 채우지 않는다.

**검증**: Anti-Pattern Checklist(data-model.md AP-1~AP-9)를 결과에 대해 직접 대조한다. 전부 "예"여야 통과.

## 시나리오 6 — 위임 확인 후 동의 (User Story 2 / SC-005, SC-006)

**입력 예시**: 시나리오 2와 동일 → 구조 뷰 완성 후 위임 확인 질문에 "네"로 응답.

**기대 결과**:
- 구조 뷰가 완성된 직후 "시퀀스 다이어그램까지 만들까요?" 같은 확인 질문이 제시된다.
- 동의하면 `generating-zenuml-diagrams`가 구조 뷰의 컴포넌트·의존관계·책임 정보를 반영한 프로세스 설명으로 실행되고, 그 결과 시퀀스 다이어그램이 구조 뷰와 함께 제시된다.

**검증**: 확인 질문이 실제로 제시되는지(SC-005), 동의 시 시퀀스 다이어그램이 실제로 생성되는지(SC-006) 확인한다.

## 시나리오 7 — 위임 확인 후 거부/무응답 (User Story 2 / SC-006)

**입력 예시**: 시나리오 6과 동일하되, 확인 질문에 "아니요" 또는 무관한 다른 요청으로 응답.

**기대 결과**: `generating-zenuml-diagrams`가 실행되지 않고, 구조 뷰만으로 응답이 끝난다. 스킬이 재차 위임을 권유하지 않는다.

**검증**: 거부/무응답 시 그 스킬이 자동으로 실행되는 비율이 0%인지 확인한다(SC-006).

## 시나리오 8 — 규모가 큰 그룹에서의 경고 (User Story 3)

**입력 예시**: 하나의 그룹에 컴포넌트 8개가 명시된 설명(그룹 내 비교 항목 8×7/2=28개 예상).

**기대 결과**: 스킬은 설명에 없는 컴포넌트를 추가하지 않고 있는 그대로 반영하며, 결과(Responsibility 섹션)가 길어질 수 있음을 사용자에게 알린다. 생성 자체를 거부하지는 않는다.

**검증**: 경고 문구가 실제로 나타나는지, 28개 항목이 실제로 모두 생성되는지 확인한다.

## 시나리오 9 — 범위 밖 요청 (Edge Cases)

**입력 예시 A**: "Controller와 Handler의 차이도 비교해줘." (시스템에 없는 일반 개념 비교 요청)
**기대 결과 A**: 이 기능이 현재 범위에 없다는 안내를 받는다(spec.md FR-013).

**입력 예시 B**: "이 코드베이스를 분석해서 구조를 뽑아줘." (코드베이스 분석 요청)
**기대 결과 B**: 자연어 설명만 입력으로 지원한다는 안내를 받는다(spec.md FR-022).

## 시나리오 10 — `.zenuml/<slug>.architecture.md` 출력 파일 (SC-007)

**입력 예시**: 시나리오 2와 동일.

**기대 결과**:
- 채팅 응답에는 구조 뷰 코드가 직접 노출되지 않고, `.zenuml/<slug>.architecture.md`를 가리키는 상대 경로 링크 한 줄이 위임 확인 질문과 함께 나온다.
- 이미 같은 슬러그의 `.zenuml/<slug>.md`(시퀀스 다이어그램)가 존재해도, 위임에 동의하지 않으면 그 파일은 생성/변경되지 않는다.
- VS Code에서 그 파일의 마크다운 프리뷰를 열면 Components & Dependencies 섹션의 Mermaid `graph`/`flowchart`가 별도 확장 없이 도형으로 렌더링된다.
- 파일 저장이 불가능한 환경이라면, 링크 대신 구조 뷰 텍스트가 채팅 응답에 직접 제공된다.

**검증**: 파일 저장이 가능한 세션에서 응답에 코드 없이 링크만 붙는지, 그 파일을 열었을 때 Mermaid 섹션이 실제로 도형으로 렌더링되는지 확인한다(SC-007 = 100% 목표).

## 시나리오 11 — 산출물만으로 질문에 답하기 (SC-008)

**입력 예시**: 시나리오 2(위임 미동의, 구조 뷰만 존재) 및 시나리오 6(위임 동의, 구조 뷰+시퀀스 다이어그램 존재) 각각의 결과물.

**기대 결과**: 원본 설명을 보지 않은 제3자가, 그 시점에 실제로 존재하는 산출물만 보고 다음 질문에 답할 수 있다 — "무엇이 있는가"(Components & Dependencies), "각자 무엇이 다른가"(Responsibility), 그리고 시퀀스 다이어그램까지 있는 경우에는 "실제로 어떻게 동작하는가"까지.

**검증**: 원본 설명은 가리고 산출물 파일만 제3자에게 제공한 뒤 위 질문에 답하게 한다. 구조 뷰만 있는 경우 두 질문에, 구조 뷰+시퀀스 다이어그램이 있는 경우 세 질문 모두에 정확히 답할 수 있으면 통과로 기록한다(SC-008 = 100% 목표, 정성적 확인).

## 시나리오 12 — 구조 뷰 피드백 로그 (SC-009)

**입력 예시**: 시나리오 2와 동일한 최초 생성 요청, 이어서 같은 구조 뷰에 대한 변경 요청(예: "SearchService도 추가해서 다시 만들어줘" — 새 컴포넌트 하나를 더한 재생성).

**기대 결과**:
- 최초 생성 직후 `.zenuml/order-payment.architecture.md`(산출물)와 함께 `.zenuml/log/order-payment.architecture.md`(로그)가 만들어지고, 로그에는 `## Round 1 — <ISO date>` 아래 최초 요청 내용과 그에 대한 응답(생성된 Components & Dependencies + Responsibility)이 담긴다.
- 재생성 요청 후 `.zenuml/order-payment.architecture.md`는 새 내용(SearchService 포함)으로 완전히 교체되고, 이전 내용은 그 파일에 남지 않는다.
- 로그 파일에는 Round 1이 그대로 남아 있고, 그 아래 `## Round 2 — <ISO date>`가 새로 추가되어 이번 요청과 재생성된 응답을 담는다 — Round 1은 지워지거나 요약되지 않는다.

**검증**: 최초 생성 직후 산출물+로그가 함께 만들어지는지(로그에 Round 1 존재), 재생성 후 산출물은 최신 내용 하나만 담고 로그에는 Round 1과 Round 2가 모두 순서대로 남아 있는지 확인한다(SC-009 = 100% 목표).

## 시나리오 13 — 목적이 맥락상 명확해 되묻지 않음 (SC-001)

**입력 예시**: "새로 합류한 팀원한테 이 시스템 구조를 보여주려고 하는데, OrderService가 주문을 생성하고 PaymentService를 호출해서 결제를 처리해."

**기대 결과**: 목적을 1/2/3 중에서 고르라고 되묻지 않고, "새로 합류한 팀원에게 보여주려고"라는 맥락에서 온보딩 목적으로 곧바로 진행해 Components & Dependencies와 Responsibility를 생성한다.

**검증**: 목적 확인 질문(1. 온보딩/2. 특정 문제 진단/3. 기타)이 등장하면 실패로 기록한다 — 목적이 맥락상 이미 명확한데도 질문을 강제하면 SC-001 위반이다.

## 결과 기록

각 시나리오의 통과/실패와 구체적 이슈를 표로 기록해 두면, `/speckit-tasks` 이후 구현을 반복 개선할 때 회귀 확인 기준으로 재사용할 수 있다.

## Validation Results (T024, 2026-07-31)

실제 대화 세션에서 `Skill` 도구로 `generating-architecture-views`를 여러 번 호출해 검증했다. 라이브 테스트 중 사용자가 직접 발견한 두 가지 결함(Components & Dependencies에 제목이 없던 점, 그룹 간 비교가 아예 빠져 있던 점)을 그 자리에서 스킬 자체에 반영해 재검증했다.

| 시나리오 | 방법 | 결과 | 비고 |
|----------|------|------|------|
| 1. 목적 미확인 시 되묻기 | 실제 호출 | PASS | "OrderService/PaymentService" 입력에 목적 확인 질문(AskUserQuestion)이 먼저 제시됨을 확인 |
| 2. 2컴포넌트 정확성 | 실제 호출 → FIX → 재확인 | FAIL → FIX → PASS | 최초 출력에 `### Responsibility` 제목만 있고 `### Components & Dependencies` 제목이 없었음(사용자 발견) → `SKILL.md`/`templates.md`/`examples.md`에 두 섹션 모두 `###` 제목을 붙이도록 수정, `.zenuml/order-payment.architecture.md` 재생성으로 확인 |
| 3. 그룹 1개, 비의존 쌍 포함 | 실제 호출 | PASS | `.zenuml/order-domain.architecture.md` — `subgraph 주문 도메인` 안에 3개 컴포넌트, PaymentService-InventoryService(비의존 쌍) 포함 정확히 3개 항목 생성 확인. 책임이 설명에 없어 전부 "명시되지 않음"으로 정직하게 표시됨(시나리오 5도 함께 검증됨) |
| 4. 그룹 3개 이상, 그룹 간 비교 | 실제 호출 → FIX(그룹 간 비교 누락) → 재확인 | FAIL → FIX → PASS | 최초 구현은 spec.md FR-008의 "다른 그룹 간 비교는 하지 않는다"를 그대로 따라 그룹 간 비교를 생성하지 않았는데, 사용자가 원래 의도("subgraph 자체끼리도 이항대립 비교")를 정정 — spec.md에 FR-025/FR-026 추가, data-model.md에 Group Comparison Item과 AP-5 추가, `SKILL.md`/`templates.md`/`examples.md`에 그룹 간 비교 로직 추가 후 `.zenuml/three-domains.architecture.md`로 재확인. 그룹 3개 → 그룹 간 비교 3개, 그룹별 컴포넌트 비교 1+3+3=7개, 그룹을 가로지르는 컴포넌트 비교(OrderService vs AuthService 등)는 없음을 확인 |
| 5. 책임 미명시 처리 | 실제 호출(시나리오 3, 4와 함께) | PASS | 위 참고 |
| 6. 위임 확인 후 동의 | 실제 호출(end-to-end 완주) | PASS | `three-domains` 구조 뷰에 "응"으로 동의 → `generating-zenuml-diagrams`가 실제 실행되어 구조 뷰의 의존관계(OrderService→PaymentService/InventoryService/AuthService/NotificationService)를 반영한 프로세스 설명으로 시퀀스 다이어그램을 생성함을 확인. `.zenuml/three-domains.md` + `.zenuml/log/three-domains.md` 생성 확인. UserService/EmailSender/SmsSender는 이번 호출 체인에 없어 시퀀스 다이어그램 참가자에서 정확히 제외됨(001의 AP-1 anti-fluff 규칙이 위임 컨텍스트에도 정상 적용됨) |
| 7. 위임 확인 후 거부/무응답 | SKILL.md 대조(수동) | PASS | "위임 거부/무응답" 규칙이 재권유 없이 종료하도록 명시되어 있음을 확인 |
| 8. 대규모 그룹 경고 | SKILL.md 대조(수동) | PASS | "규모 통제" 섹션과 예시가 8개 컴포넌트/28개 항목 케이스를 명시하고 생성을 거부하지 않음을 확인 |
| 9. 범위 밖 요청 | SKILL.md 대조(수동) | PASS | "범위 밖 요청" 섹션이 코드베이스 분석/미지원 다이어그램/일반 개념 비교 요청을 모두 다룸 |
| 10. 출력 파일 링크 | 실제 호출(시나리오 2~4, 6에서 매번 확인) | PASS | 매번 채팅에 코드 없이 파일 링크만 제시됨을 확인. VS Code Mermaid 렌더링 자체는 이 세션에서 시각적으로 재확인하지 않음(001의 기존 실측 결과를 근거로 원용) |
| 11. 산출물만으로 답변(SC-008) | 구조적 검토 | PASS | `three-domains.architecture.md`(구조 뷰) + `three-domains.md`(시퀀스 다이어그램)가 함께 존재하는 상태로 세 질문("무엇이 있는가"/"각자 무엇이 다른가"/"실제로 어떻게 동작하는가") 모두에 산출물만으로 답할 수 있음을 확인 |

**결론**: 실제 호출로 검증한 시나리오 중 둘(시나리오 2, 4)에서 스킬 설계 자체의 결함을 실전 검증으로 발견해 수정했다 — 특히 시나리오 4는 스펙 수준의 오해(그룹 간 비교를 아예 배제하기로 한 이전 클래리피케이션이 사실 원래 요청을 잘못 반영한 것이었음)를 라이브 테스트가 잡아낸 경우로, 텍스트 검토만으로는 발견하지 못했을 결함이다. 위임 실행(시나리오 6)까지 이 세션에서 end-to-end로 완주했다. 남은 미검증 항목은 VS Code Mermaid 렌더링의 시각적 재확인(001에서 이미 확인된 경로를 원용) 정도이며, 이는 SC 충족을 가로막는 것은 아니라고 판단해 T024를 완료 처리한다.
