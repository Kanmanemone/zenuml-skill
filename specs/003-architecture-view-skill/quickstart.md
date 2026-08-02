# Quickstart: `generating-architecture-views` Skill 검증

이 문서는 skill 구현 후 spec.md의 성공 기준(SC-001~SC-011)을 수동으로 검증하는 절차다. 별도의 자동화 테스트 스위트는 없다(research.md, Decision: 자기검증 워크플로 패턴).

**2026-08-02 재구성 안내**: 아래 시나리오는 Dependency/Responsibility/Collaboration 3섹션 형식(관계 레이블·색상·하이퍼링크·다수 대상 통합 포함)을 검증한다. 이 문서 맨 아래 "Validation Results (T024, 2026-07-31)"는 그 이전의 Components & Dependencies + Responsibility 2섹션 형식(이항대립 비교)에 대한 기록이며, 새 형식에는 적용되지 않는다 — 새 검증 결과는 별도로 기록한다.

## 사전 준비

1. `.claude/skills/generating-architecture-views/SKILL.md`와 `references/templates.md`, `references/examples.md`가 존재해야 한다.
2. `.claude/skills/generating-zenuml-diagrams/`도 이 저장소에 함께 존재해야 한다(위임 대상).
3. Claude Code에서 이 저장소를 열고, 새 대화를 시작한다(skill이 SKILL.md의 `description`을 기준으로 자동 검색되는지 확인하기 위해 명시적으로 skill 이름을 언급하지 않는다).

## 시나리오 1 — 목적 미확인 상태에서 먼저 되묻기 (SC-001)

**입력 예시**: "OrderService는 주문을 생성하고, PaymentService는 결제를 담당하며, OrderService가 PaymentService를 호출한다. 이 시스템의 구조를 보여줘."

**기대 결과**: 구조 뷰를 바로 생성하지 않고, 목적(온보딩/특정 문제 진단/기타)을 확인하는 질문을 먼저 한다(맥락상 목적을 추론할 단서가 없으므로).

**검증**: 질문 없이 바로 구조 뷰가 나오면 실패로 기록한다(SC-001 = 100% 목표).

## 시나리오 2 — 목적이 맥락상 명확해 되묻지 않음 (SC-001)

**입력 예시**: "새로 합류한 팀원한테 이 시스템 구조를 보여주려고 하는데, OrderService가 주문을 생성하고 PaymentService를 호출해서 결제를 처리해."

**기대 결과**: 목적을 1/2/3 중에서 고르라고 되묻지 않고, "새로 합류한 팀원에게 보여주려고"라는 맥락에서 온보딩 목적으로 곧바로 진행해 구조 뷰를 생성한다.

**검증**: 목적 확인 질문이 등장하면 실패로 기록한다(SC-001 = 100% 목표).

## 시나리오 3 — Dependency 정확성: 관계 레이블과 색상, 그룹 없음 (SC-002, SC-003, SC-004)

**입력 예시**: 시나리오 1과 동일한 설명(호출 관계만 명시, 관계 성격 미명시) + "온보딩" 목적 선택.

**기대 결과**:
- Dependency 섹션에 OrderService, PaymentService 두 컴포넌트와 `OrderService -->|호출| PaymentService` 화살표만 등장한다(관계 성격이 설명에 없으므로 기본값 "호출" 사용). 그룹 신호가 없으므로 `subgraph`는 그려지지 않는다.
- OrderService에 `classDef`+`class`로 색상이 부여되고, 그 화살표의 `linkStyle`이 같은 색이다.
- 설명에 없는 컴포넌트(예: NotificationService)나 관계가 등장하지 않는다.

**검증**: 화살표 레이블이 정확히 "호출"인지, `linkStyle` 색이 OrderService의 `class` 색과 일치하는지 확인한다(SC-002, SC-003, SC-004 = 각 100%/100%/0% 목표).

## 시나리오 4 — 그룹과 Responsibility의 책임(추상)/역할(구체) (SC-002, SC-004)

**입력 예시**: "OrderService, PaymentService, InventoryService가 모두 '주문 도메인' 그룹에 속하고, OrderService가 나머지 둘을 호출한다(호출). OrderService는 주문을 생성하고, PaymentService는 결제를 처리한다."

**기대 결과**:
- Dependency에 하나의 `subgraph`(주문 도메인) 안에 세 컴포넌트가 있고, OrderService→PaymentService/InventoryService 화살표에 "호출" 레이블이 붙는다.
- Responsibility에 "주문 도메인" 그룹 항목 하나(책임(추상)/역할(구체))와 세 요소 각각의 항목(책임(추상)/역할(구체))이 모두 나타난다. InventoryService는 개별 책임이 설명에 없으므로 "설명에 명시되지 않음"으로 표시된다.

**검증**: 그룹·요소 항목마다 두 필드가 모두 존재하는지, 근거 없는 책임이 지어내지지 않았는지 확인한다(SC-002 = 0%, SC-004 = 0% 목표).

## 시나리오 5 — Collaboration 게이팅: 그룹 레벨과 요소 레벨(같은 그룹·다른 그룹 모두) (SC-005)

**입력 예시**: 시나리오 4와 동일 + "'재고 도메인'에 InventoryService2가 있고, InventoryService가 InventoryService2를 참조한다(타입 참조)."

**기대 결과**:
- Collaboration에 그룹 간 비교(주문 도메인↔재고 도메인, 실제 교차-그룹 의존관계 있음) 항목 하나가 먼저 나온다.
- 요소 간 비교에는 OrderService-PaymentService(같은 그룹), OrderService-InventoryService(같은 그룹), InventoryService-InventoryService2(**다른 그룹**) 항목이 모두 나타난다 — 다른 그룹이라는 이유로 요소 레벨 비교가 빠지지 않는다.
- PaymentService와 InventoryService는 서로 호출하지 않으므로 둘 사이의 요소 레벨 항목은 없다.
- 각 항목이 책임의 경계·분리 이유&합리성 평가·내가 할 수 있는 질문 세 부분을 모두 담는다.

**검증**: 교차-그룹 요소 쌍(InventoryService-InventoryService2)도 요소 레벨에 나타나는지가 핵심 — 나타나지 않으면 실패로 기록한다(SC-005 = 100% 목표).

## 시나리오 6 — 다수 대상 통합 적용 (SC-005)

**입력 예시**: "'알림' 그룹의 NotificationDispatcher가 '채널' 그룹에 속한 EmailSender, SmsSender, PushSender를 전부 호출해(호출)."

**기대 결과**: Collaboration 요소 간 비교에 EmailSender/SmsSender/PushSender 각각에 대한 개별 항목 대신, "NotificationDispatcher는 채널 발신 요소들에 의존한다" 형태의 통합 항목 하나만 나타난다(3개 모두 같은 그룹·같은 관계 성격이며 서로 개별적으로 구분되지 않으므로).

**검증**: 개별 항목 3개가 나타나면 실패, 통합 항목 1개만 나타나면 통과로 기록한다(SC-005 = 100% 목표).

## 시나리오 7 — 다수 대상 통합 미적용(2개 이하 또는 이종) (SC-005)

**입력 예시**: "InterestsListDetailScreen이 InterestsNavigation(타입 참조)과 TopicNavigation(화면·타입 참조)에 의존해 — 각각 다른 그룹(interests, topic)에 속해."

**기대 결과**: 대상이 2개이고 관계 성격도 서로 다르며 그룹도 다르므로, "InterestsListDetailScreen은 InterestsNavigation과 TopicNavigation에 의존한다" 처럼 두 이름이 그대로 나열된 항목 하나만 나타난다(통합된 서술적 표현으로 압축되지 않는다).

**검증**: 두 이름이 개별적으로 나타나는지, 임의로 통합되지 않았는지 확인한다(SC-005 = 100% 목표).

## 시나리오 8 — 하이퍼링크: 로컬 루트 프로젝트 경로 모드 (SC-006)

**입력 예시**: "OrderService(src/order/OrderService.kt)가 PaymentService(src/order/PaymentService.kt)를 호출해. 이 저장소 루트 기준 경로야."

**기대 결과**:
- Dependency의 두 노드에 각각 `click OrderService "../src/order/OrderService.kt" "..."`, `click PaymentService "../src/order/PaymentService.kt" "..."`가 붙는다.
- 다이어그램 바로 아래에 VS Code Mermaid 렌더러의 로컬 클릭 이동 제약 안내 문구가 나타난다.
- Responsibility/Collaboration의 두 이름도 동일한 상대 경로로 Markdown 링크된다.

**검증**: `click` 대상 경로와 Markdown 링크 대상이 정확히 일치하는지, 안내 문구가 나타나는지 확인한다(SC-006 = 100% 목표).

## 시나리오 9 — 하이퍼링크: 웹 레포지토리 URL 모드 (SC-006)

**입력 예시**: "OrderService가 PaymentService를 호출해. 이 코드는 https://github.com/example/shop 저장소의 src/order/OrderService.kt, src/order/PaymentService.kt에 있어."

**기대 결과**: `click`과 Markdown 링크 모두 `https://github.com/example/shop/blob/.../OrderService.kt` 형태의 완전한 URL을 가리킨다. 로컬 클릭 제약 안내 문구는 나타나지 않는다(모든 링크가 URL이므로).

**검증**: 링크가 상대 경로가 아니라 완전한 URL인지, 안내 문구가 불필요하게 나타나지 않는지 확인한다(SC-006 = 100% 목표).

## 시나리오 10 — 하이퍼링크: 근거 없음 모드 (SC-006)

**입력 예시**: 시나리오 1과 동일(파일 경로도 URL도 없음).

**기대 결과**: Dependency의 어떤 노드에도 `click`이 붙지 않고, Responsibility/Collaboration의 이름도 일반 텍스트(볼드만)로 남는다 — 링크를 억지로 만들어 붙이지 않는다.

**검증**: `click` 지시어나 Markdown 링크가 하나라도 나타나면 실패로 기록한다(SC-006 = 100% 목표).

## 시나리오 11 — 근거 없는 책임을 지어내지 않음 (Edge Cases, SC-002)

**입력 예시**: 컴포넌트 중 하나(예: InventoryService)의 책임(추상/구체 모두)이 설명에 명시되지 않은 입력.

**기대 결과**: Responsibility 섹션에서 InventoryService의 책임(추상)과 역할(구체) 모두 "설명에 명시되지 않음"으로 표시되고, InventoryService가 포함된 Collaboration 항목에서도 그럴듯한 책임을 추측해서 채우지 않는다.

**검증**: Anti-Pattern Checklist(data-model.md AP-1~AP-14)를 결과에 대해 직접 대조한다. 전부 "예"여야 통과.

## 시나리오 12 — 위임 확인 후 동의 (SC-007, SC-008)

**입력 예시**: 시나리오 3과 동일 → 구조 뷰 완성 후 위임 확인 질문에 "네"로 응답.

**기대 결과**:
- 구조 뷰가 완성된 직후 "시퀀스 다이어그램까지 만들까요?" 같은 확인 질문이 제시된다.
- 동의하면 `generating-zenuml-diagrams`가 구조 뷰의 컴포넌트·의존관계·책임 정보를 반영한 프로세스 설명으로 실행되고, 그 결과 시퀀스 다이어그램이 구조 뷰와 함께 제시된다.

**검증**: 확인 질문이 실제로 제시되는지(SC-007), 동의 시 시퀀스 다이어그램이 실제로 생성되는지(SC-008) 확인한다.

## 시나리오 13 — 위임 확인 후 거부/무응답 (SC-008)

**입력 예시**: 시나리오 12와 동일하되, 확인 질문에 "아니요" 또는 무관한 다른 요청으로 응답.

**기대 결과**: `generating-zenuml-diagrams`가 실행되지 않고, 구조 뷰만으로 응답이 끝난다. 스킬이 재차 위임을 권유하지 않는다.

**검증**: 거부/무응답 시 그 스킬이 자동으로 실행되는 비율이 0%인지 확인한다(SC-008).

## 시나리오 14 — 통합 후에도 길어지는 경우의 경고 (User Story 2 규모 통제)

**입력 예시**: 하나의 그룹에 서로 다른 관계 성격으로 연결된 컴포넌트가 많아(예: 8개, 관계 성격이 제각각이라 통합 조건을 만족하지 않음) 통합을 적용해도 Collaboration 항목이 여전히 많이 남는 설명.

**기대 결과**: 스킬은 설명에 없는 컴포넌트를 추가하지 않고 있는 그대로 반영하며, 결과(Collaboration 섹션)가 길어질 수 있음을 사용자에게 알린다. 생성 자체를 거부하지는 않는다.

**검증**: 경고 문구가 실제로 나타나는지, 항목이 빠짐없이 모두 생성되는지 확인한다.

## 시나리오 15 — 범위 밖 요청 (Edge Cases)

**입력 예시 A**: "Controller와 Handler의 차이도 비교해줘." (시스템에 없는 일반 개념 비교 요청)
**기대 결과 A**: 이 기능이 현재 범위에 없다는 안내를 받는다(spec.md FR-013).

**입력 예시 B**: "이 코드베이스를 분석해서 구조를 뽑아줘." (코드베이스 분석 요청)
**기대 결과 B**: 자연어 설명만 입력으로 지원한다는 안내를 받는다(spec.md FR-022).

## 시나리오 16 — `.zenuml/<slug>.architecture.md` 출력 파일 (SC-009)

**입력 예시**: 시나리오 3과 동일.

**기대 결과**:
- 채팅 응답에는 구조 뷰 코드가 직접 노출되지 않고, `.zenuml/<slug>.architecture.md`를 가리키는 상대 경로 링크 한 줄이 위임 확인 질문과 함께 나온다.
- 이미 같은 슬러그의 `.zenuml/<slug>.md`(시퀀스 다이어그램)가 존재해도, 위임에 동의하지 않으면 그 파일은 생성/변경되지 않는다.
- VS Code에서 그 파일의 마크다운 프리뷰를 열면 Dependency 섹션의 Mermaid `flowchart`가 별도 확장 없이 도형으로(색상·레이블 포함) 렌더링된다.
- 파일 저장이 불가능한 환경이라면, 링크 대신 구조 뷰 텍스트가 채팅 응답에 직접 제공된다.

**검증**: 파일 저장이 가능한 세션에서 응답에 코드 없이 링크만 붙는지, 그 파일을 열었을 때 Mermaid 섹션이 실제로 도형으로 렌더링되는지 확인한다(SC-009 = 100% 목표).

## 시나리오 17 — 산출물만으로 질문에 답하기 (SC-010)

**입력 예시**: 시나리오 3(위임 미동의, 구조 뷰만 존재) 및 시나리오 12(위임 동의, 구조 뷰+시퀀스 다이어그램 존재) 각각의 결과물.

**기대 결과**: 원본 설명을 보지 않은 제3자가, 그 시점에 실제로 존재하는 산출물만 보고 다음 질문에 답할 수 있다 — "무엇이 있는가"(Dependency), "각자 무엇이 다른가"(Responsibility), "왜 나뉘어 있는가"(Collaboration), 그리고 시퀀스 다이어그램까지 있는 경우에는 "실제로 어떻게 동작하는가"까지.

**검증**: 원본 설명은 가리고 산출물 파일만 제3자에게 제공한 뒤 위 질문에 답하게 한다. 구조 뷰만 있는 경우 세 질문에, 구조 뷰+시퀀스 다이어그램이 있는 경우 네 질문 모두에 정확히 답할 수 있으면 통과로 기록한다(SC-010 = 100% 목표, 정성적 확인).

## 시나리오 18 — 구조 뷰 피드백 로그 (SC-011)

**입력 예시**: 시나리오 3과 동일한 최초 생성 요청, 이어서 같은 구조 뷰에 대한 변경 요청(예: "SearchService도 추가해서 다시 만들어줘" — 새 컴포넌트 하나를 더한 재생성).

**기대 결과**:
- 최초 생성 직후 `.zenuml/order-payment.architecture.md`(산출물)와 함께 `.zenuml/log/order-payment.architecture.md`(로그)가 만들어지고, 로그에는 `## Round 1 — <ISO date>` 아래 최초 요청 내용과 그에 대한 응답(생성된 Dependency + Responsibility + Collaboration)이 담긴다.
- 재생성 요청 후 `.zenuml/order-payment.architecture.md`는 새 내용(SearchService 포함)으로 완전히 교체되고, 이전 내용은 그 파일에 남지 않는다.
- 로그 파일에는 Round 1이 그대로 남아 있고, 그 아래 `## Round 2 — <ISO date>`가 새로 추가되어 이번 요청과 재생성된 응답을 담는다 — Round 1은 지워지거나 요약되지 않는다.

**검증**: 최초 생성 직후 산출물+로그가 함께 만들어지는지(로그에 Round 1 존재), 재생성 후 산출물은 최신 내용 하나만 담고 로그에는 Round 1과 Round 2가 모두 순서대로 남아 있는지 확인한다(SC-011 = 100% 목표).

## 시나리오 19 — 다수 대상 통합: 개별 차이가 있어도 통합됨 (SC-005, FR-027b)

**입력 예시**: 시나리오 6과 동일 + "EmailSender는 sendEmail()을, SmsSender는 sendSms()를, PushSender는 sendPush()를 각각 호출해서 발송해."(서로 다른 함수 이름을 명시)

**기대 결과**: 세 대상이 서로 다른 함수 이름을 갖고(다이어그램·Responsibility 모두에서 개별적으로 구분되더라도), 같은 그룹·같은 관계 성격에서 병렬적 구조적 역할(발신 방식만 다른 채널 발신자)을 수행하므로 여전히 "NotificationDispatcher는 채널 발신 요소들에 의존한다" 형태의 통합 항목 하나로 압축된다.

**검증**: 개별 함수 이름이 다르다는 이유만으로 통합이 취소되고 3개 항목이 개별 나열되면 실패로 기록한다(SC-005 = 100% 목표).

## 시나리오 20 — 종류가 다른 대상은 통합에서 제외됨 (SC-005, FR-027b)

**입력 예시**: 시나리오 19와 동일 + "PushSender는 추가로 발송 재시도 정책(retry policy)을 자체적으로 관리하는데, 이 재시도 정책은 EmailSender·SmsSender에는 없어."

**기대 결과**: EmailSender와 SmsSender만 병렬 형제로 남아 통합되고(둘뿐이므로 이제 "EmailSender와 SmsSender에 의존한다"처럼 개별 나열— 통합 임계값 3개 미달), 재시도 정책이라는 다른 대상에 없는 별도 책임을 가진 PushSender는 개별 항목으로 별도 등장한다.

**검증**: PushSender가 통합/나열된 서술 안에 섞여 사라지면 실패, 별도 항목으로 명확히 구분되면 통과로 기록한다.

## 시나리오 21 — Responsibility 병렬 형제 통합 (SC-002, FR-009b)

**입력 예시**: "'채널' 그룹에 EmailSender, SmsSender, PushSender가 있고, 각각 sendEmail(), sendSms(), sendPush()를 통해 발송을 수행해. 셋 다 발송 채널을 구현하는 동일한 역할이야."

**기대 결과**: Responsibility 요소의 책임에 세 요소가 각각 별도 항목으로 나열되는 대신, "EmailSender, SmsSender, PushSender" 세 이름이 모두 나열된(각각 하이퍼링크된) 통합 항목 하나가 만들어진다. 책임(추상)은 "발송 채널을 구현해 실제 메시지를 내보낸다" 같은 공유 문장이고, 역할(구체)은 `sendEmail()`, `sendSms()`, `sendPush()` 세 함수 이름을 모두 빠짐없이 인용한다.

**검증**: 세 요소 각각의 함수 이름이 통합 항목 안에 모두 등장하는지(통합으로 개별 근거가 누락되지 않았는지), 별도 항목 3개로 쪼개지지 않았는지 확인한다(SC-002 = 0% 목표 — 근거 누락은 실패).

## 결과 기록

각 시나리오의 통과/실패와 구체적 이슈를 표로 기록해 두면, 구현을 반복 개선할 때 회귀 확인 기준으로 재사용할 수 있다.

## Validation Results (T024, 2026-07-31) — 2섹션 구형 형식 기준, 참고용

실제 대화 세션에서 `Skill` 도구로 `generating-architecture-views`를 여러 번 호출해 검증했다. 라이브 테스트 중 사용자가 직접 발견한 두 가지 결함(Components & Dependencies에 제목이 없던 점, 그룹 간 비교가 아예 빠져 있던 점)을 그 자리에서 스킬 자체에 반영해 재검증했다. **이 표는 2026-08-02 재구성 이전(Components & Dependencies + 이항대립 Responsibility 2섹션) 형식에 대한 기록이며, 현재 형식(Dependency/Responsibility/Collaboration)에는 그대로 적용되지 않는다 — 위 시나리오 1~18로 재검증이 필요하다.**

| 시나리오 | 방법 | 결과 | 비고 |
|----------|------|------|------|
| 1. 목적 미확인 시 되묻기 | 실제 호출 | PASS | "OrderService/PaymentService" 입력에 목적 확인 질문(AskUserQuestion)이 먼저 제시됨을 확인 |
| 2. 2컴포넌트 정확성 | 실제 호출 → FIX → 재확인 | FAIL → FIX → PASS | 최초 출력에 `### Responsibility` 제목만 있고 `### Components & Dependencies` 제목이 없었음(사용자 발견) → `SKILL.md`/`templates.md`/`examples.md`에 두 섹션 모두 `###` 제목을 붙이도록 수정, `.zenuml/order-payment.architecture.md` 재생성으로 확인 |
| 3. 그룹 1개, 비의존 쌍 포함 | 실제 호출 | PASS | `.zenuml/order-domain.architecture.md` — `subgraph 주문 도메인` 안에 3개 컴포넌트, PaymentService-InventoryService(비의존 쌍) 포함 정확히 3개 항목 생성 확인. 책임이 설명에 없어 전부 "명시되지 않음"으로 정직하게 표시됨 |
| 4. 그룹 3개 이상, 그룹 간 비교 | 실제 호출 → FIX(그룹 간 비교 누락) → 재확인 | FAIL → FIX → PASS | 최초 구현은 그룹 간 비교를 생성하지 않았는데, 사용자가 원래 의도를 정정 — `.zenuml/three-domains.architecture.md`로 재확인 |
| 5. 책임 미명시 처리 | 실제 호출(시나리오 3, 4와 함께) | PASS | 위 참고 |
| 6. 위임 확인 후 동의 | 실제 호출(end-to-end 완주) | PASS | `three-domains` 구조 뷰에 "응"으로 동의 → `generating-zenuml-diagrams`가 실제 실행되어 시퀀스 다이어그램을 생성함을 확인 |
| 7. 위임 확인 후 거부/무응답 | SKILL.md 대조(수동) | PASS | "위임 거부/무응답" 규칙이 재권유 없이 종료하도록 명시되어 있음을 확인 |
| 8. 대규모 그룹 경고 | SKILL.md 대조(수동) | PASS | "규모 통제" 섹션과 예시가 8개 컴포넌트/28개 항목 케이스를 명시하고 생성을 거부하지 않음을 확인 |
| 9. 범위 밖 요청 | SKILL.md 대조(수동) | PASS | "범위 밖 요청" 섹션이 코드베이스 분석/미지원 다이어그램/일반 개념 비교 요청을 모두 다룸 |
| 10. 출력 파일 링크 | 실제 호출(시나리오 2~4, 6에서 매번 확인) | PASS | 매번 채팅에 코드 없이 파일 링크만 제시됨을 확인 |
| 11. 산출물만으로 답변 | 구조적 검토 | PASS | `three-domains.architecture.md` + `three-domains.md`가 함께 존재하는 상태로 세 질문 모두에 산출물만으로 답할 수 있음을 확인 |

**결론(2섹션 구형 형식 기준)**: 실제 호출로 검증한 시나리오 중 둘(시나리오 2, 4)에서 스킬 설계 자체의 결함을 실전 검증으로 발견해 수정했다. 위임 실행(시나리오 6)까지 end-to-end로 완주했다. 이 결과는 2026-08-02 3섹션 재구성 이전 형식에 대한 것이므로, 새 형식에 대한 실제 검증(시나리오 1~18)은 별도로 수행해야 한다.
