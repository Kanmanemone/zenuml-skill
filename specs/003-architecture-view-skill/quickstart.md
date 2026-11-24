# Quickstart: `generating-architecture-views` Skill 검증

이 문서는 skill 구현 후 spec.md의 성공 기준(SC-001~SC-011)을 수동으로 검증하는 절차다. 별도의 자동화 테스트 스위트는 없다(research.md, Decision: 자기검증 워크플로 패턴).

**2026-08-02 재구성 안내**: 아래 시나리오는 Dependency/Responsibility/Collaboration 3섹션 형식(관계 레이블·색상·하이퍼링크·다수 대상 통합 포함)을 검증한다. 이 문서 맨 아래 "Validation Results (T024, 2026-07-31)"는 그 이전의 Components & Dependencies + Responsibility 2섹션 형식(이항대립 비교)에 대한 기록이며, 새 형식에는 적용되지 않는다 — 새 검증 결과는 별도로 기록한다.

## 사전 준비

1. `.claude/skills/generating-architecture-views/SKILL.md`와 `references/templates.md`, `references/examples.md`가 존재해야 한다.
2. Claude Code에서 이 저장소를 열고, 새 대화를 시작한다(skill이 SKILL.md의 `description`을 기준으로 자동 검색되는지 확인하기 위해 명시적으로 skill 이름을 언급하지 않는다).

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
- OrderService에 `classDef`+`class`로 색상이 부여되고, 그 화살표(`e0@`)의 엣지 클래스가 같은 색이다.
- 설명에 없는 컴포넌트(예: NotificationService)나 관계가 등장하지 않는다.

**검증**: 화살표 레이블이 정확히 "호출"인지, 엣지 클래스 색이 OrderService의 `class` 색과 일치하는지 확인한다(SC-002, SC-003, SC-004 = 각 100%/100%/0% 목표).

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
- 다이어그램 코드펜스 다음에는 클릭 이동 제약 안내 같은 부연 문구 없이 곧바로 `### Responsibility`가 이어진다(FR-027d).
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

## 시나리오 12 — 구조 뷰만으로 응답 종료 (SC-007, FR-014)

**입력 예시**: 시나리오 3과 동일.

**기대 결과**: 구조 뷰 파일 링크만으로 응답이 끝난다 — 시퀀스 다이어그램을 만들지 묻거나 제안하지 않고, 다른 스킬도 실행되지 않는다.

**검증**: 응답에 시퀀스 다이어그램 관련 질문·제안이 없고 다른 스킬이 실행되지 않았는지 확인한다(SC-007).

## 시나리오 13 — (폐지: 옛 위임 거부/무응답 시나리오, 2026-11-13)

## 시나리오 14 — 통합 후에도 길어지는 경우: 안내 없이 전체 생성 (User Story 2 규모 통제, FR-012)

**입력 예시**: 하나의 그룹에 서로 다른 관계 성격으로 연결된 컴포넌트가 많아(예: 8개, 관계 성격이 제각각이라 통합 조건을 만족하지 않음) 통합을 적용해도 Collaboration 항목이 여전히 많이 남는 설명.

**기대 결과**: 스킬은 설명에 없는 컴포넌트를 추가하지 않고 있는 그대로 반영하며, 생성 자체를 거부하거나 항목을 생략하지 않는다. 결과가 길다는 안내는 파일에도 채팅 응답에도 나타나지 않는다(FR-012).

**검증**: 항목이 빠짐없이 모두 생성되는지, 그리고 "항목이 꽤 깁니다" 같은 길이 안내가 어디에도 없는지 확인한다.

## 시나리오 15 — 범위 밖 요청 (Edge Cases)

**입력 예시 A**: "Controller와 Handler의 차이도 비교해줘." (시스템에 없는 일반 개념 비교 요청)
**기대 결과 A**: 이 기능이 현재 범위에 없다는 안내를 받는다(spec.md FR-013).

**입력 예시 B**: "이 코드베이스를 분석해서 구조를 뽑아줘." (코드베이스 분석 요청)
**기대 결과 B**: 자연어 설명만 입력으로 지원한다는 안내를 받는다(spec.md FR-022).

## 시나리오 16 — `.zenuml/<slug>.architecture.md` 출력 파일 (SC-009)

**입력 예시**: 시나리오 3과 동일.

**기대 결과**:
- 채팅 응답에는 구조 뷰 코드가 직접 노출되지 않고, `.zenuml/<slug>.architecture.md`를 가리키는 상대 경로 링크 한 줄만 나온다.
- VS Code에서 그 파일의 마크다운 프리뷰를 열면 Dependency 섹션의 Mermaid `flowchart`가 별도 확장 없이 도형으로(색상·레이블 포함) 렌더링된다.
- 파일 저장이 불가능한 환경이라면, 링크 대신 구조 뷰 텍스트가 채팅 응답에 직접 제공된다.

**검증**: 파일 저장이 가능한 세션에서 응답에 코드 없이 링크만 붙는지, 그 파일을 열었을 때 Mermaid 섹션이 실제로 도형으로 렌더링되는지 확인한다(SC-009 = 100% 목표).

## 시나리오 17 — 산출물만으로 질문에 답하기 (SC-010)

**입력 예시**: 시나리오 3의 결과물(구조 뷰 파일).

**기대 결과**: 원본 설명을 보지 않은 제3자가, 그 시점에 실제로 존재하는 산출물만 보고 다음 질문에 답할 수 있다 — "무엇이 있는가"(Dependency), "각자 무엇이 다른가"(Responsibility), "왜 나뉘어 있는가"(Collaboration).

**검증**: 원본 설명은 가리고 산출물 파일만 제3자에게 제공한 뒤 위 세 질문에 답하게 한다.

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

## 시나리오 22 — Dependency 렌더러 지정: 명시 시 포함, 미명시 시 생략 (FR-007b)

**입력 예시(22a)**: 시나리오 1과 동일한 설명 + "다이어그램은 elk 렌더러로 그려줘"(렌더러 명시).

**입력 예시(22b)**: 시나리오 1과 동일한 설명, 렌더러 언급 없음.

**기대 결과**:
- 22a: YAML frontmatter `config` 바로 아래에 `layout: elk`가 포함된다(값은 사용자가 입력한 문자열 그대로 — 다른 렌더러 이름을 요청해도 동일하게 그 값이 그대로 들어가야 한다).
- 22b: `layout` 필드 자체가 `config`에 등장하지 않는다(기존 동작과 동일). 어느 경우에도 `config.flowchart.defaultRenderer`는 쓰이지 않는다.
- 22a로 생성된 뷰를 렌더러 언급 없이 재생성 요청하면(예: "컴포넌트 하나 추가해서 다시 만들어줘"), 새로 생성된 YAML `config`에는 이전 라운드의 `layout: elk`가 이어지지 않고 생략된다.

**검증**: 22a/22b 각각에서 `layout` 필드의 유무가 요청의 명시 여부와 정확히 일치하는지, 재생성 시 이전 라운드 값이 상태로 남아 이어지지 않는지 확인한다(FR-007b — 명시율/생략율 각각 100% 목표).

## 시나리오 23 — 산출물에 실제 내용만 담기 (FR-032, SC-012)

**입력 예시**: 시나리오 8(로컬 경로)과 시나리오 14(항목이 많음)를 합친 설명, 또는 표준 flowchart 외의 렌더러 호환성을 언급할 여지가 있는 설명.

**기대 결과**:
- 산출 파일에는 `### Dependency`(캡션 + 다이어그램), `### Responsibility`, `### Collaboration`의 헤딩과 실제 내용만 있다 — 클릭 이동 안내, 길이 안내, 렌더러 호환성 경고, 레이아웃·배치 설명, 생성 과정 해설 같은 blockquote·문단이 없다.
- 채팅 응답은 파일 링크만 담는다(목적 확인이 필요했다면 그 질문, 온보딩 기본값을 적용했다면 그 고지는 허용).

**검증**: 산출 파일에서 세 섹션의 실제 내용과 캡션이 아닌 줄이 하나도 없는지, 채팅 응답에 FR-032가 허용하지 않은 부연 문구가 없는지 확인한다.

## 시나리오 24 — Dependency 캡션 (FR-033, SC-013, US1/AC5)

**입력 예시**: "Jetpack Navigation 3에서 백스택과 화면 전환 구조를 보여줘" + 관련 컴포넌트 설명.

**기대 결과**:
- `### Dependency` 헤딩과 Mermaid 코드펜스 사이에 일반 텍스트 한 줄(예: `Jetpack Navigation 3의 백스택과 화면 전환 의존 구조`)이 정확히 하나 있다 — blockquote·헤딩·볼드가 아니다.
- 캡션은 요청의 핵심 키워드(Navigation 3, 백스택, 화면 전환)로만 이뤄지고, 요청에 없는 내용이나 렌더링·레이아웃 설명이 없다.
- 이후 초점을 바꾼 재생성 요청을 하면 캡션도 그 라운드까지의 요청을 반영해 다시 쓰인다.

**검증**: 캡션 줄의 위치·개수·형식과, 그 단어가 요청에서 나온 것인지 확인한다.

## 시나리오 25 — 구조 변화 CRUD 표시 (FR-034, FR-035, SC-014, US1/AC6)

**입력 예시**: "이 커밋에서 `NewNode`가 추가되고 `ChangedNode`가 바뀌고 `RemovedNode`가 삭제됐어. 변화를 설명해줘" + 관련 컴포넌트 설명. 비교용으로 같은 시스템의 "구조를 보여줘" 요청도 낸다.

**기대 결과**:
- 동적 요청: CRUD class가 하나 이상이면 도식 안에 제목 없이 `✨: 추가`, `♻️: 변경`, `🗑️: 삭제`가 3줄 text로 정확히 한 번 보인다.
- 두 요청 모두 CRUD 구역 주석 바로 다음 줄에 라벨 규칙 주석 `%% 라벨: ✨&nbsp;<b>추가</b> · ♻️&nbsp;변경 · 🗑️&nbsp;<s>삭제</s>`이 있다.
- 정적 요청: CRUD 구역과 세 `classDef crud*`는 있지만 `class … crud*` 줄·이모지 접두·범례가 없다.
- CRUD class를 하나만 둬도 세 줄 설명이 모두 생기며, 세 class를 모두 둬도 한 번만 생긴다.
- 정적/동적을 묻는 질문은 판단이 실제로 불가능할 때만 나온다.

**검증**: `python specs/003-architecture-view-skill/test_build_diagram.py`를 실행하고 미리보기에서 3줄 설명을 확인한다.

## 시나리오 26 — 노드 규격 표시어 (FR-036, SC-015)

**입력 예시**: Now in Android처럼 실제 코드가 있는 프로젝트에서 "`NiaAppState`와 `NiaNavHost`, 그리고 `core` 모듈의 구조를 보여줘". 코드에서 `NiaAppState`는 `class`, `NiaNavHost`는 `@Composable fun`, `TopLevelDestination`은 `enum class`로 선언되어 있고, `colors.xml` 같은 파일 하나를 가리키는 노드도 섞는다. 비교용으로 같은 구성의 동적 요청("이 커밋에서 `NiaNavHost`가 바뀌었다")도 낸다.

**기대 결과**:
- `declarationMarkers=false`, `fileExtensions=true`, `functionParentheses=true`에서는 `NiaAppState`, `NiaNavHost()`, `TopLevelDestination`, `colors.xml`로 표시된다.
- 세 설정의 8개 조합에서 선언 키워드·파일의 마지막 확장자·함수 `()`가 서로 독립적으로 나타나거나 사라진다. 모두 true면 `class&nbsp;NiaAppState`, `fun&nbsp;NiaNavHost()`, `enum&nbsp;class&nbsp;TopLevelDestination`, `colors.xml`이다.
- `core` 모듈 노드처럼 선언도 파일도 아닌 노드는 이름만 있다.
- 동적 요청에서는 변화 표시가 설정 적용 뒤 라벨 앞에 온다(세 값이 모두 true면 `♻️&nbsp;fun&nbsp;NiaNavHost()`).
- 어떤 라벨에도 `Foo(state)` 같은 괄호 설명이 없고, Responsibility·Collaboration의 굵은 이름에는 표시어가 없다.

**검증**: 각 노드 라벨을 원본 선언과 대조해 지어낸 표시어가 없는지 보고, 8개 조합과 기본값을 확인한다. 선언 표시어는 파일 확장자를, 파일 확장자는 선언 표시어를 바꾸지 않는지 확인한다. 함수 종류를 특정 키워드로 하드코딩하지 않고도 함수에만 `()`가 정확히 한 번 붙는지, 009 hover 패널과 010 단계별 펼치기가 같은 기본 이름을 찾는지 확인한다.

## 시나리오 27 — 파일 이름 표시 (FR-037, SC-017)

**입력 예시**: 파일 `Memo.kt` 노드와 그 안의 `class Memo` 노드, 다른 파일의 함수 노드가 모두 링크를 가진 구조 뷰.

**기대 결과**:
- `Memo` 선언 노드와 함수 노드의 위쪽 테두리 선 위, 설정한 자리(왼쪽·중간·오른쪽)에 파일 이름이 그 노드 테두리 색으로 보이고 글자 뒤 테두리 선은 가려진다. `Memo.kt` 파일 노드와 링크 없는 노드에는 없다.
- Mermaid의 `classic`(VS Code 미리보기)·`neo`(Mermaid CLI) 두 모양과 라이트·다크 테마에서 같은 자리에 같은 모양으로 보인다.
- 노드 라벨 텍스트에 파일 이름이 없다. 문서 끝 `<details>` 블록을 지우거나 GitHub에서 보면 파일 이름만 사라지고 노드 크기·이름 위치는 같다.
- `fileExtensions=false`에서도 파일 노드에는 표시가 없고 같은 이름 선언 노드에는 있다.

**검증**: `python specs/003-architecture-view-skill/test_build_diagram.py`와 009 fixture 회귀를 실행하고, Mermaid CLI로 `look: classic`·`neo` × 왼쪽·중간·오른쪽과 다크 테마 변수를 넣은 렌더링을 확인한다.

## 시나리오 28 — 점검 케이스 재실행 (FR-027, FR-040, SC-018)

**입력 예시**: 두 요청을 새 에이전트에게 각각 준다.
- 정적: "신규 팀원 온보딩 목적으로 주문 처리 시스템의 구조를 보여줘. OrderController가 주문 요청을 받아 OrderService를 호출한다. OrderService는 InventoryRepository로 재고를 확인하고 PaymentService로 결제한다. PaymentService는 외부 PG API를 호출하고, 결제가 끝나면 NotificationService가 메일을 보낸다."
- 동적: "이번 PR에서 검색 기능 구조가 어떻게 바뀌었는지 보여줘. 원래 feature/search/SearchViewModel.kt가 data/LegacySearchApi.kt를 직접 호출했는데, 이번에 data/SearchRepository.kt를 새로 만들어서 SearchViewModel은 SearchRepository만 호출하고, SearchRepository가 data/remote/SearchRemoteDataSource.kt를 호출하게 바꿨어. LegacySearchApi는 삭제했고, SearchViewModel은 수정됐어."

**기대 결과**:
- 정적: `NotificationService`는 엣지 없는 노드, 외부 PG API는 `subgraph` 없는 일반 노드이고, 목적을 묻지 않는다.
- 동적: `data` 안에 `data/remote`가 중첩되고, 그룹 쌍은 가장 안쪽 그룹 기준으로 엣지가 가로지를 때만 있다. 삭제된 노드의 엣지에는 별도 표시가 없고 목적을 묻지 않는다.
- 두 결과 모두 Collaboration의 근거 없는 하위 항목에 "설명에 명시되지 않음" bullet이 하나만 있다.

**검증**: 두 산출물을 위 기대와 `SKILL.md` "Evidence and checks"에 대조한다.

## 시나리오 29 — 사용 외 의존 옅은 선 (FR-042~045, SC-019·020, 007 SC-011)

**입력 예시**: "`MemoFeed`는 `ReorderableState`를 만들어 `MemoList`에 넘기고, `MemoList`는 그 상태의 `moved()`를 호출한다. `MemoFeed`는 `MemoList`를 화면에 그린다." 같은 구성에 변화 표시가 있는 동적 요청도 낸다.

**기대 결과**:
- `MemoFeed → ReorderableState`는 라벨 `생성`의 옅은 선(출발 노드 색, 화살촉·라벨 글자도 옅음)이고, `MemoList → ReorderableState`와 `MemoFeed → MemoList`는 진한 선이다.
- 옅은 선이 진한 선과 겹치면 아래에 깔린다. 범례 `옅은 선: 사용 외 의존 (생성·전달)`은 한 줄이고, 동적 요청에서는 ✨·♻️·🗑️ 세 줄 다음에 온다.
- `dependency.faintNonUsageEdges=false`(또는 요청에서 끔)이면 모든 간선이 진한 선이고 범례 줄이 없으며, 라벨·간선 ID는 켰을 때와 같다.
- 사용 의존만 있는 요청의 산출물은 이 기능 전과 같다.

**검증**: `python -m unittest specs/003-architecture-view-skill/test_build_diagram.py`를 실행하고, 산출물을 VS Code 미리보기와 GitHub(임시 push 후 되돌림)에서 보고 옅은 선·겹침·범례 한 줄을 확인한다.

## 결과 기록

각 시나리오의 통과/실패와 구체적 이슈를 표로 기록해 두면, 구현을 반복 개선할 때 회귀 확인 기준으로 재사용할 수 있다.

## Validation Results (T159, 2026-11-22)

- `test_build_diagram.py`: 공통 4규칙(테두리 선 위 위치·look별 보정·노드 채움색 배경·기울임)과 노드별 `content`·테두리 색, 왼쪽·중간·오른쪽, 꺼짐, 멱등을 포함한 9개 테스트가 통과했다.
- 009 fixture: 기본·사용자 설정 기대 출력과 끄기 복원이 바이트 단위로 같았고, 010 테스트 33개가 통과했다.
- Mermaid CLI 12.3 렌더링: `look: classic`·`neo` × 왼쪽·중간·오른쪽 6가지 모두 파일 이름이 위쪽 테두리 선 위에 노드 테두리 색으로 놓이고 글자 뒤 선이 가려졌으며, 파일 노드에는 없었다. VS Code Dark Modern 색 변수를 넣은 다크 렌더링에서 배경이 노드 채움과 같이 어두워졌다. 실제 VS Code 미리보기는 확인하지 못했다.

## Validation Results (T155, 2026-11-22)

- `test_build_diagram.py`: 라벨 불변·`class … srcFile` 표식, `fileExtensions=false` 파일 노드 판정, style 블록 규칙·멱등, 왼쪽·꺼짐을 포함한 9개 테스트가 통과했다.
- 009 fixture: 기본·사용자 설정 기대 출력과 끄기 복원이 바이트 단위로 같았고, 010 테스트 33개가 통과했다.
- Mermaid CLI 12.3 렌더링(문서 style을 페이지 CSS로 주입): 오른쪽·왼쪽 모두 파일 이름이 테두리 안쪽 끝에 붙고, 파일 노드와 링크 없는 노드에는 없으며, 노드 이름 위치와 노드 크기는 그대로였다. VS Code 미리보기는 확인하지 못했다.

## Validation Results (T143, 2026-11-21)

- `read_settings.py`: `dependency.nodeNameFormat`의 배포 기본값이 `false`·`true`·`true`이고 안내가 없음을 확인했다.
- `test_build_diagram.py`: 배포값·키 누락 기본값, 세 boolean의 8개 조합 독립성, 제거된 구형 두 키의 안내를 포함한 5개 테스트가 통과했다.
- 지침 대조: 선언 표시어는 파일 내부 선언에만, 확장자는 파일 자체 노드에만, 괄호는 함수에만 적용하며 다른 이름·ID·링크·hover에는 적용하지 않도록 `SKILL.md`와 template가 일치한다.
- 회귀: 009 hover 기본·사용자 설정 기대 출력이 일치했고, 010 단계 문서 테스트 33개가 통과했다.

## Validation Results (T139, 2026-11-21)

- `test_build_diagram.py`: CRUD 없음과 추가·변경·삭제 각각의 조건을 포함한 2개 테스트 통과.
- `swemo-a7f94cc-function-changes.architecture.md`: 제목 없는 3줄 이모지 설명을 Mermaid CLI로 렌더링 성공.

## Validation Results (T136, 2026-11-20)

- 시나리오 26: 임의의 원본 표시어 `sourceKeyword`를 사용한 함수 라벨 `sourceKeyword&nbsp;render()`가 `build_diagram.py` 실행 뒤에도 그대로 보존되고, 비함수 `class&nbsp;Worker`에는 괄호가 붙지 않음을 확인했다.
- hover 이름 연결: `view_parser.clean_name`이 함수 라벨은 `render`, 비함수 라벨은 `Worker`로 반환했다.
- 단계별 펼치기: 함수·비함수·변화 표시 사례를 포함한 `test_learning_stages.py` 33개 테스트가 모두 통과했다.

## Validation Results (T131, 2026-11-20)

`build_diagram.py`로 시나리오 25·26의 기본 다이어그램을 완성한 뒤 라벨과 CRUD 구역을 검사했다.

| 시나리오 | 결과 | 비고 |
|----------|------|------|
| 25. 구조 변화 CRUD 표시 | PASS | 추가·변경·삭제 라벨이 모두 `Id@{ label: "…" }` 형식을 유지했고, CRUD class·고정 라벨 주석·세 classDef가 생성되며 미변경 노드는 표시되지 않음을 확인 |
| 26. 노드 규격 표시어 | PASS (부분 보류) | 선언 키워드·파일 확장자·`&nbsp;`·변화 표시 조합을 보존하고, 모듈 노드는 표시어 없이 남으며 본문 굵은 이름과 라벨 부가 설명에는 표시어가 없음을 확인. 009 hover와 010 단계별 펼치기는 해당 기능이 새 라벨의 마지막 `&nbsp;` 뒤 이름 규칙을 반영할 때까지 보류 |

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

## Validation Results (T164, 2026-11-23)

- 003 `test_build_diagram.py` 9개, 002 `test_append_feedback.py` 2개 통과.
- `examples.md`의 다섯 Mermaid 예시를 `build_diagram.py`에 넣어 모두 exit 0. `.kt` 파일 노드 라벨에 확장자가 없는 경우 0건. 지침 문서에 다른 스킬 이름 0건(SC-008).
- 시나리오 28의 새 에이전트 재실행은 아직 하지 않음(SC-018 일부 미검증).

## Validation Results (T165, 2026-11-23)

시나리오 28을 스킬만 복사한 빈 프로젝트에서 새 에이전트 둘로 실행했다(기대 결과는 알려 주지 않음).

| 케이스 | 결과 | 비고 |
|---|---|---|
| 정적 주문 시스템 | PASS | `NotificationService` 엣지 없음, `PgApi@{ label: "외부 PG API" }`는 그룹 없는 노드, 목적 질문 없음, 분리 이유마다 미지 문구 bullet 1개. 약 69k 토큰, 90초 |
| 동적 PR 변경 | PASS(구조 뷰) | `data` ⊃ `remote` 중첩, 그룹 쌍 search→data·data→remote, 삭제 노드 엣지 별도 표시 없음·링크 유지, `SearchRemoteDataSource` 표시 없음, 목적 질문 없음. 약 84k 토큰, 115초 |

동적 케이스에서 hover 결함이 따로 드러났다. 본문 이름을 FR-036대로 기본 이름(`SearchViewModel`)으로 쓰면 `apply_hover.py`가 노드 ID나 확장자가 붙은 라벨(`SearchViewModel.kt`)과만 맞춰 보므로, 아무 패널도 넣지 못한 채 exit 0과 "변경 없음"으로 끝난다. 이번 지침 변경과 무관한 기존 결함이므로 버그 흐름으로 따로 다룬다.

## 시나리오 30 — 링크 노드 글자색 (FR-046, SC-021, 007 SC-012)

```
python specs/003-architecture-view-skill/test_build_diagram.py
```

- `linkStyle: plain`: config의 `themeCSS`에 `.node a, .node a:hover { color: inherit !important; text-decoration: none !important; }`가 한 번 있다.
- `linkStyle: link`: 출력이 도입 전과 같다. 두 출력은 config 줄 밖이 같다.
- **수동 확인**: 링크가 있는 노드와 없는 노드가 함께 있는 구조 뷰를 VS Code 미리보기로 열어, 두 노드 이름이 같은 글자색이고 평소 밑줄이 없으며, 마우스를 올리면 밑줄이 생기고 링크 노드를 누르면 열리는지 본다.

## Validation Results (T170, 2026-11-23)

- `python -m unittest specs/003-architecture-view-skill/test_build_diagram.py` 16 OK, 010 `test_learning_stages.py` 40 OK, 002 `test_append_feedback.py` 2 OK.
- 시나리오 29 구성(정적·동적, `생성` 하나, 진한 간선 둘)을 `build_diagram.py`로 서식하고 Mermaid CLI(ELK)로 렌더링: `생성` 간선만 선·화살촉·라벨이 옅은 주황, 진한 간선은 그대로, 옅은 간선 줄이 먼저 선언됨(`e1`, `e0`, `e2`), 범례는 ✨·♻️·🗑️ 다음 `옅은 선: 사용 외 의존 (생성·전달)` 한 줄.
- `--faint-edges=false`: `Faint`·범례 줄·`wrappingWidth`가 없고 간선 ID·라벨은 켰을 때와 같음.
- 확인하지 않음: VS Code 미리보기와 GitHub의 육안 확인(SC-019), 에이전트가 새 규칙으로 라벨을 고르는 실제 실행(SC-020).

## Validation Results (T173, 2026-11-23)

- 시나리오 29 설명을 `SKILL.md` 새 규칙으로 판정(이 규칙을 쓴 에이전트 자신이 실행, 독립 실행 아님): `MemoFeed → ReorderableState`는 만들어 넘기기만 하므로 `생성`, `MemoList → ReorderableState`는 `moved()` 호출이라 사용 의존, `MemoFeed → MemoList`는 함수 노드를 그리는(호출하는) 사용 의존. T170의 정적 산출물과 같고, 늘어난 출력은 라벨 단어뿐이다.
- 어긋난 사례: handoff의 4라운드 판정은 `TouchOverlay → MemoCard`(덮음)를 옅게 봤지만, 새 규칙에서는 화면 함수를 호출해 그리는 것이 사용 의존이라 진한 선이 되고 `덮음`은 세 라벨 중 하나도 아니다. 사용자 확인 필요.

## Validation Results (T172, 2026-11-23)

- VS Code 미리보기: 사용자가 시나리오 29 동적 산출물을 열어 옅은 선과 범례가 잘 나온다고 확인.
- GitHub: 샘플 파일 하나만 담은 임시 브랜치를 push해 파일 미리보기로 확인. `생성` 간선의 선·화살촉·라벨이 옅은 주황, 진한 간선 둘은 그대로, 범례는 ✨·♻️·🗑️ 다음 `옅은 선: 사용 외 의존 (생성·전달)` 한 줄. 확인 뒤 원격·로컬 임시 브랜치를 지움.

## Validation Results (T175, 2026-11-23)

- 003 테스트 16 OK, 010 테스트 40 OK.
- 새 질문 순서로 판정(규칙을 쓴 에이전트 자신이 실행): 시나리오 29의 `MemoFeed → ReorderableState`는 ①예 ②아니오 ③예 → `생성`(옅음), `MemoList → ReorderableState`·`MemoFeed → MemoList`는 ②예 → 진함. T170·T173과 같다.
- swemo 4라운드: `CategorySelector → ReorderableState`·`MemoFeed → ReorderableState`는 ③ → `생성`(옅음), `draggedItem → ReorderableState`는 key·offset 읽기라 ② → 진함(handoff 판정과 같음). `TouchOverlay → MemoCard`는 코드에 `MemoCard`가 없는 형제 관계지만 ①예(카드가 터치를 먹지 않게 바뀌면 레이어가 불필요) ②아니오 ③아니오 ④예, 근거("카드 안 TextField가 터치를 소비하기 때문")가 가정을 밝히므로 진한 선이며 라벨에 그 가정을 담는다. handoff의 옅음 판정은 이 규칙으로 바뀐다.
