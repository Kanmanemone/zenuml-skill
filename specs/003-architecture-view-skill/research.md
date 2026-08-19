# Phase 0 Research: Architecture View Skill

이 문서는 `plan.md`의 Technical Context에 남아 있던 구현 수준 결정 사항을 정리한다. 문제/증거/컨셉 수준 조사는 이미 `.specify/assessments/generate-architecture-views/research.md`에서 완료되었고, 스펙 자체의 범위 결정은 `spec.md`의 `## Clarifications`에서 확정되었으므로(여러 차례 개정을 거쳐 현재의 "2섹션 + 사용자 확인 후 조건부 위임" 형태로 정착), 여기서는 **skill을 실제로 어떻게 구성할지**에 대한 남은 결정만 다룬다.

## Decision: Skill 이름

- **Decision**: `generating-architecture-views`
- **Rationale**: `generating-zenuml-diagrams`와 동일하게 Anthropic 공식 skill 저작 가이드가 권장하는 gerund(동명사) 명명 규칙을 따른다. `architecture`, `views`, `generating` 키워드를 포함해 discovery(description 매칭)에 유리하다. 스펙이 여러 번 개정됐지만(6섹션 → 2섹션 + 위임) "구조 뷰를 생성한다"는 핵심 정체성은 바뀌지 않았으므로 이름을 바꿀 이유가 없다.
- **Alternatives considered**: 이전 라운드와 동일 — `architecture-view-skill`(gerund 아님, feature 슬러그와 혼동), `generating-structure-views`(discovery 신호가 약함).

## Decision: 참조 파일 구조

- **Decision**: `SKILL.md` 하나 + `references/templates.md`(Components & Dependencies, Responsibility 섹션의 Mermaid/표 템플릿) + `references/examples.md`(완성 예시 2~3개). 위임(delegation) 확인 절차 자체는 참조 파일로 분리하지 않고 SKILL.md 본문의 워크플로 안에 직접 둔다.
- **Rationale**: 이전 라운드의 결정(SKILL.md + references/, `.temp`식 5-파일 분리 기각)을 그대로 유지한다. 위임 절차는 "매 실행마다 반드시 거치는 핵심 분기"이므로, 참조 파일로 분리해 필요할 때만 불러오는 것보다 SKILL.md 본문에 항상 로드되는 규칙으로 두는 것이 안전하다 — 참조 파일은 세션 중 누락되거나 늦게 읽힐 수 있지만, SKILL.md 본문은 스킬이 선택되는 순간 항상 로드된다.
- **Alternatives considered**: 위임 절차를 별도 `references/delegation.md`로 분리(참조 깊이가 SKILL.md에서 1단계로 유지되긴 하지만, 매번 반드시 필요한 로직을 "필요할 때만 읽는" 자료로 취급하는 것은 위험 — 기각).

## Decision: 목적(Purpose) 확인 질문 설계

- **Decision**: 구조 뷰 생성 전, 사용자가 목적을 이미 밝히지 않았다면 3지선다 질문을 한다 — "이 구조 뷰를 어떤 목적으로 보시나요? (1) 온보딩 — 전체 구조 이해, (2) 특정 문제 진단 — 특정 컴포넌트/관계에 집중, (3) 기타 — 직접 설명". "기타"를 고르면 "어떤 정보가 필요하신지 한 문장으로 알려주세요"라고 후속 질문을 한다.
- **Rationale**: 이전 라운드의 결정을 유지한다 — spec.md FR-001~003이 "반드시 되묻는다"는 원칙만 확정하고 구체적 질문 문구는 구현 단계로 남겼다.
- **Alternatives considered**: 이전 라운드와 동일(설명 분석으로 목적 자동 추측 — 기각, 자유 서술형만 질문 — 기각).

## Decision: Components & Dependencies 자동 그룹핑 및 표현

- **Decision**: 컴포넌트 이름의 접두사/네임스페이스나 설명에 명시된 계층·도메인 구분이 있을 때만 Mermaid `subgraph`로 그룹을 만들고, 없으면 전체 컴포넌트를 하나의 암묵적 그룹(비교 범위 계산상으로는 "그룹 1개"로 취급하되 다이어그램에는 `subgraph` 테두리를 그리지 않음)으로 취급한다. 의존관계는 화살표로 표현한다.
- **Rationale**: spec.md FR-006, FR-007이 이미 확정한 내용을 그대로 구현 규칙으로 옮긴다. "그룹이 없을 때도 비교 범위 계산에서는 전체를 그룹 1개로 본다"는 점을 명시해야, Responsibility 섹션의 n(n-1)/2 공식이 그룹 유무와 무관하게 항상 적용되도록 구현이 흔들리지 않는다.
- **Alternatives considered**: 그룹이 없을 때 비교 자체를 생략(spec.md FR-008이 "그룹이 없으면 전체 컴포넌트 집합을 하나의 그룹으로 취급"이라고 명시했으므로 기각 — User Story 1 Acceptance Scenario 2와도 상충).

## Decision: Responsibility 비교 항목 생성 순서

- **Decision**: 그룹 내 컴포넌트를 나열한 뒤, 사전순(또는 설명에 등장한 순서)으로 정렬해 중복 없는 순서 없는 쌍(unordered pair)을 전부 생성한다 — 예를 들어 [A, B, C]면 (A,B), (A,C), (B,C) 3개만 만들고 (B,A), (C,A), (C,B)는 만들지 않는다.
- **Rationale**: spec.md의 수학 정정(Clarifications, 2026-07-31)에 따라 n(n-1)/2개만 만들어야 한다. 구현 시 실수로 순서 있는 쌍(n(n-1)개)을 만들지 않도록, "이미 나열한 컴포넌트와의 쌍은 다시 만들지 않는다"는 생성 순서 규칙을 명시적으로 둔다.
- **Alternatives considered**: 모든 컴포넌트에 대해 "다른 모든 컴포넌트와 비교"를 독립적으로 수행(구현이 단순해 보이지만 자연스럽게 중복(순서 있는 쌍)을 만들게 되므로 기각 — 정정된 스펙과 정면으로 상충).

## Decision: 그룹 간(Group-to-Group) 비교 추가

- **Decision**: 그룹이 2개 이상이면, 컴포넌트 간 비교와 별개로 그룹 자체도 서로 순서 없는 쌍으로 전부 비교한다 — 그룹이 m개면 m×(m-1)/2개의 그룹 비교 항목을 만든다. 항목의 근거는 각 그룹에 실제로 부여된 이름/레이블뿐이다. 그룹이 1개 이하면 이 비교는 만들지 않는다. Responsibility 섹션 안에서 그룹 간 비교를 먼저 보여준 뒤, 그룹별 컴포넌트 간 비교를 이어서 보여준다(넓은 것에서 좁은 것 순 — Top-down Processing).
- **Rationale**: 실사용 검증(dogfooding) 중, 사용자가 원래 요청("subgraph 및 그 속의 요소들을 '전부' 이항대립시켜서 비교")이 그룹 내부뿐 아니라 그룹 자체끼리의 비교도 포함한 것이었음을 확인했다(spec.md Clarifications, 2026-07-31 재정정). 그룹 이름만 근거로 삼는 이유는, 그룹의 전반적 역할을 설명이 별도 문장으로 서술하는 경우가 드물기 때문에 — 근거 없이 그룹의 목적을 추측해서 채우면 이 스킬 전체를 관통하는 anti-fluff 원칙(FR-004 등)에 어긋난다. 그룹 이름 자체는 사용자가 설명에서 실제로 부여한 문자열이므로 이를 근거로 삼는 것은 추측이 아니다.
- **Alternatives considered**: 그룹의 멤버 컴포넌트들의 책임을 종합해 그룹의 역할을 추론(각 컴포넌트 책임이 없거나 부분적인 경우가 많아 일관성이 떨어지고, 컴포넌트 책임을 조합한 요약 자체가 설명에 없는 새 사실을 만들어내는 것이라 기각); 그룹 간 비교를 아예 생략하고 그룹 내부 비교만 유지(사용자가 명시적으로 정정을 요청했으므로 기각).

## Decision: 위임(Delegation) 확인 질문과 컨텍스트 전달 방식

- **Decision**: 구조 뷰(파일 저장 포함)를 완료한 뒤, "이 구조를 바탕으로 시퀀스 다이어그램도 만들까요?"라고 짧게 묻는다. 동의하면, 원래 사용자 설명 + Components & Dependencies에서 식별된 컴포넌트/그룹/의존관계 + Responsibility에서 확인된 각 컴포넌트의 책임을 하나의 보강된 자연어 프로세스 설명으로 재구성해, 그 내용을 마치 사용자가 `generating-zenuml-diagrams`에 직접 입력한 것처럼 그 스킬의 워크플로(요청 분류부터)를 그대로 따라 실행한다.
- **Rationale**: spec.md FR-014~018이 확정한 "확인 후 조건부 실행, 대상 스킬은 수정하지 않고 그대로 실행"을 그대로 구현 절차로 옮긴다. "보강된 자연어 설명으로 재구성"하는 방식을 택한 이유는, `generating-zenuml-diagrams`가 프로그램적 API가 아니라 자연어 프로세스 설명을 입력으로 받는 지침 기반 스킬이므로, 그 스킬의 입력 계약(contracts/skill-interface.md, `description` 필드)을 그대로 만족시키는 유일한 방법이 자연어 설명 형태로 컨텍스트를 전달하는 것이기 때문이다.
- **Alternatives considered**: 구조 뷰 파일 경로만 전달하고 그 스킬이 파일을 직접 읽게 함(그 스킬의 Input Contract는 자연어 설명만 받도록 정의되어 있어(001의 contracts/skill-interface.md), 파일 경로 전달은 그 스킬의 기존 계약을 벗어나므로 기각 — FR-018 "그 스킬의 동작을 수정해서는 안 된다"와도 상충).

## Decision: 규모 통제(그룹/컴포넌트 수 제한)

- **Decision**: 하드 캡(예: "그룹당 최대 6개")을 강제하지 않는다. 대신 (a) Components & Dependencies 생성 시 설명에 없는 컴포넌트·그룹을 추가하지 않는다(이미 자연어 입력 규모로 상한이 걸림), (b) 하나의 그룹에 컴포넌트가 많아(예: 8개 이상 — 이 경우 28개 비교 항목) 비교 항목이 많이 늘어날 것으로 예상되면 결과가 길어질 수 있음을 사용자에게 알린다.
- **Rationale**: spec.md FR-011, FR-012, User Story 3이 "생성 자체를 거부하지는 않는다"고 명시했으므로 하드 캡은 스펙과 상충한다. 대신 입력 규모 자체를 넘지 않는다는 자연스러운 상한(자연어 설명에 없는 컴포넌트를 만들지 않음)과, 사용자에게 미리 알리는 소프트한 안내로 충분하다.
- **Alternatives considered**: 그룹당 컴포넌트 수 하드 캡(스펙의 "생성 자체를 거부하지는 않는다"는 명시적 요구와 상충하므로 기각).

## Decision: 안티패턴 체크리스트 항목

- **Decision**: 자기검증 체크리스트는 다음 항목으로 구성한다:
  - AP-1: 설명에 없는 컴포넌트가 추가되지 않았는가
  - AP-2: 설명에 없는 의존관계가 추가되지 않았는가
  - AP-3: 설명에서 확인되는 신호 없이 만들어진 그룹(subgraph)이 없는가
  - AP-4: 각 그룹 내부의 비교 항목 수가 정확히 n×(n-1)/2인가(순서 있는 쌍으로 중복 생성되지 않았는가)
  - AP-5: 그룹이 2개 이상이면 그룹 간 비교 항목 수가 정확히 m×(m-1)/2인가(그룹이 1개 이하면 이 비교 자체가 없는가), 그리고 그 내용이 그룹 레이블만 근거로 하는가
  - AP-6: 책임이 설명에 명시되지 않은 컴포넌트에 대해 책임이나 차이를 추측해서 채우지 않았는가
  - AP-7: 시스템에 등장하지 않는 일반적 개념을 비교하는 섹션을 만들지 않았는가 (FR-013)
  - AP-8: Runtime Flow(시퀀스) 다이어그램을 스스로 그리지 않았는가 (위임 대상 영역 침범 금지)
  - AP-9: 시퀀스 다이어그램 생성 여부를 사용자에게 확인했는가(구조 뷰가 완성됐다면), 그리고 동의 없이 `generating-zenuml-diagrams`를 실행하지 않았는가
- **Rationale**: spec.md FR-004, FR-006, FR-008~010, FR-013~017, FR-025~026의 자기검증 요구(FR-019)를 항목화했다. AP-4는 수학 정정을, AP-5는 그룹 간 비교 추가를, AP-9는 위임이 확인-후-실행 방식으로 바뀐 것을 반영해 새로 추가했다. AP-7과 AP-8은 원래 하나로 합쳐져 있었으나(`/speckit-analyze` 발견 U1), FR-013(Responsibility 범위 제한)은 User Story 1 관심사이고 Runtime Flow 금지는 User Story 2(위임 경계) 관심사라 서로 다른 단계에서 검증되어야 하므로 분리했다 — AP-7은 US1의 체크리스트(T007)에, AP-8은 AP-9와 함께 US2의 체크리스트(T015)에 배치한다.
- **Alternatives considered**: 이전(자동 위임 모델) 버전의 AP("Runtime Flow를 실행시켰는가")를 그대로 유지(더 이상 "항상 실행"이 아니므로 기각 — "확인했는가/동의 없이 실행하지 않았는가"로 대체). 일반 개념 비교 금지와 Runtime Flow 금지를 하나로 유지(US1 MVP 체크포인트에서 FR-013이 검증되지 않는 문제가 있어 기각). 그룹 간 비교를 AP-4에 합쳐서 표현(항목 성격이 달라 — 하나는 컴포넌트 개수 n, 하나는 그룹 개수 m 기준이라 혼동을 피하기 위해 분리).

## Decision: 자기검증 워크플로 패턴

- **Decision**: `generating-zenuml-diagrams`와 동일한 "generate → validate → fix" 피드백 루프를 채택한다.
- **Rationale**: 이전 라운드와 동일 — 이미 검증된 패턴을 재사용.
- **Alternatives considered**: 없음.

## Decision: 다이어그램 피드백 로그(002 기능)와의 관계

- **Decision**: 이번 범위에서는 `generating-architecture-views`에 대해 `.zenuml/log/<slug>.md`류의 피드백 로그를 만들지 않는다.
- **Rationale**: 이전 라운드와 동일 — `002-diagram-feedback-log`는 `generating-zenuml-diagrams`를 대상으로 정의됐고, 이번 spec.md의 어떤 FR도 새 스킬에 피드백 로그를 요구하지 않는다.
- **Alternatives considered**: 두 스킬 모두에 적용되는 공통 피드백 로그로 확장(스코프 밖 — 필요해지면 별도 라운드).

## Decision: 모호한 입력 처리

- **Decision**: 목적이 불분명하면 추측하지 않고 되묻는다(FR-001). 그룹 신호나 개별 컴포넌트의 책임이 설명에 없으면, 되묻지 않고 조용히 생략한다(그룹은 나누지 않음, 책임/차이는 "명시되지 않음"으로 표시, FR-010). 시퀀스 다이어그램 생성 동의 여부가 불분명하면(애매한 답변, 무응답), 동의로 간주하지 않고 실행하지 않는다(FR-016) — 목적 확인과 달리 "기본값을 적용해 진행"하지 않고 "기본값은 실행하지 않음"이다.
- **Rationale**: 목적은 이후 전체 산출물의 모양을 바꾸는 상위 결정이라 잘못 추측하면 산출물 전체가 쓸모없어지므로 반드시 확인해야 한다. 반면 위임 동의는 "확실한 동의가 없으면 하지 않는다"는 보수적 기본값이 안전하다 — 사용자가 원치 않는 스킬을 실행시키는 것이 사용자가 원하는 실행을 놓치는 것보다 더 나쁘다.
- **Alternatives considered**: 위임 동의가 애매하면 목적 확인처럼 기본값(예: "실행함")을 적용(사용자가 원치 않는 `generating-zenuml-diagrams` 실행을 유발할 위험이 있어 기각).
