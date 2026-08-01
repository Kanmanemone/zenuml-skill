# Quickstart: `generating-architecture-views` Skill 검증

이 문서는 skill 구현 후 spec.md의 성공 기준(SC-001~SC-008)을 수동으로 검증하는 절차다. 별도의 자동화 테스트 스위트는 없다(research.md, Decision: 자기검증 워크플로 패턴).

## 사전 준비

1. `.claude/skills/generating-architecture-views/SKILL.md`와 `references/templates.md`, `references/examples.md`가 존재해야 한다.
2. `.claude/skills/generating-zenuml-diagrams/`도 이 저장소에 함께 존재해야 한다(위임 대상).
3. Claude Code에서 이 저장소를 열고, 새 대화를 시작한다(skill이 SKILL.md의 `description`을 기준으로 자동 검색되는지 확인하기 위해 명시적으로 skill 이름을 언급하지 않는다).

## 시나리오 1 — 목적 미확인 상태에서 먼저 되묻기 (User Story 1 / SC-001)

**입력 예시**: "OrderService는 주문을 생성하고, PaymentService는 결제를 담당하며, OrderService가 PaymentService를 호출한다. 이 시스템의 구조를 보여줘."

**기대 결과**: 구조 뷰를 바로 생성하지 않고, 목적(온보딩/특정 문제 진단/기타)을 확인하는 질문을 먼저 한다.

**검증**: 질문 없이 바로 구조 뷰가 나오면 실패로 기록한다(SC-001 = 100% 목표).

## 시나리오 2 — Context+Dependency와 Responsibility 정확성 (User Story 1 / SC-002, SC-003)

**입력 예시**: 시나리오 1과 동일한 설명 + "온보딩" 목적 선택.

**기대 결과**:
- Context+Dependency 섹션에 OrderService, PaymentService 두 컴포넌트와 호출 화살표(OrderService → PaymentService)만 등장한다. 그룹 신호가 없으므로 `subgraph`는 그려지지 않는다.
- Responsibility 섹션에 정확히 2×1/2=**1개**의 비교 항목(OrderService vs PaymentService)이 생성된다.
- 설명에 없는 컴포넌트(예: NotificationService)나 관계, 근거 없는 차이 서술이 등장하지 않는다.

**검증**: 비교 항목 수를 n(n-1)/2 공식으로 직접 계산해 대조한다(SC-002 = 0%, SC-003 = 100% 목표).

## 시나리오 3 — 그룹 내 전체 쌍 비교, 의존관계 무관 (User Story 1)

**입력 예시**: "OrderService, PaymentService, InventoryService가 모두 '주문 도메인' 그룹에 속하고, OrderService가 나머지 둘을 호출한다."

**기대 결과**:
- Context+Dependency 섹션에 하나의 `subgraph`(주문 도메인) 안에 세 컴포넌트가 있고, OrderService→PaymentService, OrderService→InventoryService 화살표가 있다.
- Responsibility 섹션에 정확히 3×2/2=**3개**의 비교 항목(OrderService-PaymentService, OrderService-InventoryService, **PaymentService-InventoryService**)이 있다 — 마지막 쌍은 서로 직접 호출하지 않지만 같은 그룹이므로 비교 대상에 포함되어야 한다.

**검증**: 의존관계가 없는 쌍(PaymentService-InventoryService)도 비교 항목에 포함되는지 확인한다 — 빠져 있으면 실패로 기록.

## 시나리오 4 — 근거 없는 책임/차이를 지어내지 않음 (Edge Cases)

**입력 예시**: 컴포넌트 중 하나(예: InventoryService)의 책임이 설명에 명시되지 않은 입력.

**기대 결과**: Responsibility 섹션에서 InventoryService의 책임이 "명시되지 않음"으로 표시되고, InventoryService가 포함된 비교 항목에서도 차이를 추측해서 채우지 않는다.

**검증**: Anti-Pattern Checklist(data-model.md AP-1~AP-7)를 결과에 대해 직접 대조한다. 전부 "예"여야 통과.

## 시나리오 5 — 위임 확인 후 동의 (User Story 2 / SC-005, SC-006)

**입력 예시**: 시나리오 2와 동일 → 구조 뷰 완성 후 위임 확인 질문에 "네"로 응답.

**기대 결과**:
- 구조 뷰가 완성된 직후 "시퀀스 다이어그램까지 만들까요?" 같은 확인 질문이 제시된다.
- 동의하면 `generating-zenuml-diagrams`가 구조 뷰의 컴포넌트·의존관계·책임 정보를 반영한 프로세스 설명으로 실행되고, 그 결과 시퀀스 다이어그램이 구조 뷰와 함께 제시된다.

**검증**: 확인 질문이 실제로 제시되는지(SC-005), 동의 시 시퀀스 다이어그램이 실제로 생성되는지(SC-006) 확인한다.

## 시나리오 6 — 위임 확인 후 거부/무응답 (User Story 2 / SC-006)

**입력 예시**: 시나리오 5와 동일하되, 확인 질문에 "아니요" 또는 무관한 다른 요청으로 응답.

**기대 결과**: `generating-zenuml-diagrams`가 실행되지 않고, 구조 뷰만으로 응답이 끝난다. 스킬이 재차 위임을 권유하지 않는다.

**검증**: 거부/무응답 시 그 스킬이 자동으로 실행되는 비율이 0%인지 확인한다(SC-006).

## 시나리오 7 — 규모가 큰 그룹에서의 경고 (User Story 3)

**입력 예시**: 하나의 그룹에 컴포넌트 8개가 명시된 설명(비교 항목 8×7/2=28개 예상).

**기대 결과**: 스킬은 설명에 없는 컴포넌트를 추가하지 않고 있는 그대로 반영하며, 결과(Responsibility 섹션)가 길어질 수 있음을 사용자에게 알린다. 생성 자체를 거부하지는 않는다.

**검증**: 경고 문구가 실제로 나타나는지, 28개 항목이 실제로 모두 생성되는지 확인한다.

## 시나리오 8 — 범위 밖 요청 (Edge Cases)

**입력 예시 A**: "Controller와 Handler의 차이도 비교해줘." (시스템에 없는 일반 개념 비교 요청)
**기대 결과 A**: 이 기능이 현재 범위에 없다는 안내를 받는다(spec.md FR-013).

**입력 예시 B**: "이 코드베이스를 분석해서 구조를 뽑아줘." (코드베이스 분석 요청)
**기대 결과 B**: 자연어 설명만 입력으로 지원한다는 안내를 받는다(spec.md FR-022).

## 시나리오 9 — `.zenuml/<slug>.architecture.md` 출력 파일 (SC-007)

**입력 예시**: 시나리오 2와 동일.

**기대 결과**:
- 채팅 응답에는 구조 뷰 코드가 직접 노출되지 않고, `.zenuml/<slug>.architecture.md`를 가리키는 상대 경로 링크 한 줄이 위임 확인 질문과 함께 나온다.
- 이미 같은 슬러그의 `.zenuml/<slug>.md`(시퀀스 다이어그램)가 존재해도, 위임에 동의하지 않으면 그 파일은 생성/변경되지 않는다.
- VS Code에서 그 파일의 마크다운 프리뷰를 열면 Context+Dependency 섹션의 Mermaid `graph`/`flowchart`가 별도 확장 없이 도형으로 렌더링된다.
- 파일 저장이 불가능한 환경이라면, 링크 대신 구조 뷰 텍스트가 채팅 응답에 직접 제공된다.

**검증**: 파일 저장이 가능한 세션에서 응답에 코드 없이 링크만 붙는지, 그 파일을 열었을 때 Mermaid 섹션이 실제로 도형으로 렌더링되는지 확인한다(SC-007 = 100% 목표).

## 결과 기록

각 시나리오의 통과/실패와 구체적 이슈를 표로 기록해 두면, `/speckit-tasks` 이후 구현을 반복 개선할 때 회귀 확인 기준으로 재사용할 수 있다.
