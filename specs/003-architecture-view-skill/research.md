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

- **2026-11-13 개정**: 이 Decision 전체가 폐지됐다. 스킬은 다른 스킬과 연계하지 않는 독립 스킬로 바뀌어, 구조 뷰 완성 후 시퀀스 다이어그램을 묻거나 다른 스킬을 실행하지 않는다(spec.md FR-014). 아래 기록과, 이 문서의 다른 Decision에 남은 위임·`generating-zenuml-diagrams` 관련 서술(AP 후보 목록, 목적 기본값 비교 등)은 결정 당시의 기록으로만 남긴다.

- **Decision**: 구조 뷰(파일 저장 포함)를 완료한 뒤, "이 구조를 바탕으로 시퀀스 다이어그램도 만들까요?"라고 짧게 묻는다. 동의하면, 원래 사용자 설명 + Components & Dependencies에서 식별된 컴포넌트/그룹/의존관계 + Responsibility에서 확인된 각 컴포넌트의 책임을 하나의 보강된 자연어 프로세스 설명으로 재구성해, 그 내용을 마치 사용자가 `generating-zenuml-diagrams`에 직접 입력한 것처럼 그 스킬의 워크플로(요청 분류부터)를 그대로 따라 실행한다.
- **Rationale**: spec.md FR-014~018이 확정한 "확인 후 조건부 실행, 대상 스킬은 수정하지 않고 그대로 실행"을 그대로 구현 절차로 옮긴다. "보강된 자연어 설명으로 재구성"하는 방식을 택한 이유는, `generating-zenuml-diagrams`가 프로그램적 API가 아니라 자연어 프로세스 설명을 입력으로 받는 지침 기반 스킬이므로, 그 스킬의 입력 계약(contracts/skill-interface.md, `description` 필드)을 그대로 만족시키는 유일한 방법이 자연어 설명 형태로 컨텍스트를 전달하는 것이기 때문이다.
- **Alternatives considered**: 구조 뷰 파일 경로만 전달하고 그 스킬이 파일을 직접 읽게 함(그 스킬의 Input Contract는 자연어 설명만 받도록 정의되어 있어(001의 contracts/skill-interface.md), 파일 경로 전달은 그 스킬의 기존 계약을 벗어나므로 기각 — FR-018 "그 스킬의 동작을 수정해서는 안 된다"와도 상충).

## Decision: 규모 통제(그룹/컴포넌트 수 제한)

- **Decision**: 하드 캡(예: "그룹당 최대 6개")을 강제하지 않는다. 대신 (a) Components & Dependencies 생성 시 설명에 없는 컴포넌트·그룹을 추가하지 않는다(이미 자연어 입력 규모로 상한이 걸림), (b) 하나의 그룹에 컴포넌트가 많아(예: 8개 이상 — 이 경우 28개 비교 항목) 비교 항목이 많이 늘어날 것으로 예상되면 결과가 길어질 수 있음을 사용자에게 알린다.
- **Rationale**: spec.md FR-011, FR-012, User Story 3이 "생성 자체를 거부하지는 않는다"고 명시했으므로 하드 캡은 스펙과 상충한다. 대신 입력 규모 자체를 넘지 않는다는 자연스러운 상한(자연어 설명에 없는 컴포넌트를 만들지 않음)과, 사용자에게 미리 알리는 소프트한 안내로 충분하다.
- **2026-11-13 개정**: 개정된 FR-012에 따라, 위 결정 중 "항목이 많이 늘어날 것으로 예상되면 사용자에게 미리 알린다"는 소프트 안내는 폐지한다 — 하드 캡을 두지 않고 전체를 생성한다는 결정은 그대로이며, 길이 안내는 파일에도 채팅 응답에도 넣지 않는다(FR-032와 같은 이유: 산출물에는 실제 내용만 둔다).
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

## Decision: 노드 규격 표시어 (FR-036, 2026-11-20)

- **Decision — 누가 쓰나**: 스킬(에이전트)이 007 설정의 `dependency.nodeNameFormat` 세 값을 읽고 노드 라벨에 직접 쓴다. `declarationMarkers=true`면 `Foo@{ label: "class&nbsp;Foo" }`, 파일 자체 노드는 설정과 무관하게 `Foo@{ label: "Foo.kt" }`처럼 쓰고, `fileExtensions=false`이면 `build_diagram.py`가 그 확장자를 지운다. 라벨이 `click` 대상의 파일 이름과 같은지로 파일 자체 노드를 알아보며, FR-037의 표시 대상 판정도 같은 판정을 쓴다.
- **Rationale**: 표시어는 원본 코드를 읽고 옮겨 오는 판단이라 FR-008d의 "판단이 필요한 부분은 스킬이 쓴다"에 속한다. `build_diagram.py`는 노드 선언 줄을 해석하지 않고 그대로 옮기므로 라벨이 달라져도 영향이 없다. 표시어가 붙은 노드만 `@{ label }` 형식이 되어 늘어나는 토큰은 그 노드 수만큼이다.
- **Alternatives considered**: 스크립트가 붙이기(스크립트가 종류를 알려면 에이전트가 종류를 따로 넘겨야 해서 쓰는 양이 줄지 않고 인터페이스만 늘어 기각).

- **Decision — 근거**: 실제 코드가 있으면 코드를 읽어 설명을 만들 때 노드마다 선언 키워드(원본에 쓰인 그대로, 예: `data class`, `sealed interface`, `fun`, `def`)와 파일 이름(확장자 포함)을 근거로 함께 적는다. 표시어는 그 근거에서만 가져온다. 근거에 없으면 붙이지 않는다. 표시어는 그것이 무엇인지(규격)를 정하는 키워드(`class`, `enum class`, `interface`, `object`, `fun` …)이며, 어떻게 동작하는지(기능)를 정하는 수식어(`suspend`, `async`, `inline`), 접근 제한자(`private`), 어노테이션(`@Composable`)은 넣지 않는다 — `suspend fun foo`는 `fun foo`, `async def foo`는 `def foo`.
- **Rationale**: FR-022에 따라 구조 뷰 생성 단계는 설명만 쓴다. 표시어도 경로·식별자처럼 설명에 담긴 근거여야 같은 원칙이 지켜진다(SKILL.md의 코드베이스 입력 안내에 "선언 종류"를 근거 목록에 더한다).
- **Alternatives considered**: 이름 관례로 짐작(`I` 접두 → interface 등 — FR-036이 금지해 기각).

- **Decision — 붙이는 모양**: `declarationMarkers=true`일 때 표시어와 이름 사이, 여러 단어 표시어의 단어 사이는 `&nbsp;`로 잇는다(`data&nbsp;class&nbsp;Foo`). `fileExtensions=true`일 때만 파일 자체 노드에 마지막 확장자가 남는다(지우는 쪽은 `build_diagram.py`). `functionParentheses=true`일 때만 함수 노드 이름 끝에 `()`를 정확히 한 번 붙인다. 세 설정은 독립이다. 변화 표시와 함께 쓰면 설정 적용 뒤의 표시어·이름·확장자·함수 괄호를 함께 `<b>`/`<s>` 안에 둔다.
- **Rationale**: 변화 표시 이모지에 `&nbsp;`를 쓴 이유(FR-035)와 같이, 긴 라벨이 줄바꿈될 때 `class`만 윗줄에 남지 않게 한다. 함수의 `()`는 언어별 표시어와 무관한 단일 접미 규칙이라 별도 키워드 목록이 필요 없다. 공백이 든 이름(`Now in Android 앱`)은 `&nbsp;`가 없으므로 그대로 남는다.
- **Alternatives considered**: 보통 공백으로 잇기(줄바꿈 문제, 그리고 공백 든 이름과 구분할 수 없어 기각). 언어별 키워드 목록으로 함수 여부를 다시 판별하기(기존 근거를 중복하고 열린 어휘라 빠짐이 생겨 기각).

- **Decision — 다른 기능에 미치는 영향**: 표시 설정은 Dependency 라벨에만 적용한다. Responsibility·Collaboration의 굵은 이름, 노드 ID, 링크 대상과 hover 내용은 바꾸지 않는다. 009·010은 기존처럼 노드 ID와 마지막 `&nbsp;` 뒤의 기본 이름을 사용하고 끝 `()`를 제거하므로 새 정규화가 필요 없다.
- **Rationale**: 두 기능 모두 이미 표시 라벨을 기본 이름으로 정규화하는 책임이 있다. 접미사 한 쌍만 제거하면 기존 표시어 열린 어휘 규칙을 유지하면서 함수 노드의 hover와 선언 찾기가 깨지지 않는다.
- **Alternatives considered**: 언어별 함수 표시어 목록으로 괄호 제거 여부를 판단(하드코딩과 중복이라 기각). 소비자가 `foo()`를 기본 이름으로 사용(Responsibility·Collaboration과 실제 선언 이름 `foo`의 연결이 끊겨 기각).

## Decision: 파일 이름 표시 (FR-037, 2026-11-22)

- **Decision — 판정과 그리기를 나눔**: `build_diagram.py`는 지금처럼 파일 자체 노드를 판정하되 라벨을 바꾸지 않고, 표시 대상 노드 ID를 `class A,B srcFile` 한 줄로 남긴다(설정과 무관하게 항상). `apply_hover.py`는 이 줄의 노드마다 `click` 대상의 파일 이름으로 `.srcFile.<색상 class> .nodeLabel::before` 규칙을 만들어, 문서 끝 `<details class="zenuml-hover-style">` 속 `<style>`에 붙인다. `dependency.sourceFile.enabled`·`position`과 그 명령줄 값은 `apply_hover.py`가 읽는다. hover가 꺼져도 규칙이 있으면 같은 블록을 쓰므로 SKILL.md는 이 스크립트를 항상 실행한다.
- **Rationale**: `fileExtensions=false`이면 파일 노드와 같은 이름 선언 노드의 라벨이 같아져 나중에는 구분할 수 없으므로, 확장자를 지우는 쪽이 판정 결과를 남겨야 한다. 정의 없는 class는 Mermaid에서 아무것도 바꾸지 않아 GitHub 렌더링과 라벨에 영향이 없다. 문서 끝 style 블록은 GitHub가 적용하지 않고 지우면 함께 사라지므로 FR-037의 OCP 조건을 그대로 만족한다. `::before`를 `position: absolute`로 띄우므로 노드 크기와 이름 위치는 바뀌지 않는다.
- **위치(2026-11-22 개정)**: 노드 사각형은 라벨 상자보다 한쪽마다 Mermaid `neo` look(Mermaid CLI 기본)에서 가로 16px·세로 12px, `classic` look(VS Code 미리보기 기본)에서 가로 30px·세로 15px 크다(Mermaid CLI 12.3 실측, VS Code 내장 미리보기는 Mermaid 12.2에 `look: "classic"`). 위쪽 테두리 선이 높이 12px(글자 10px + 위아래 1px 여백) 글자 상자의 가운데를 지나도록 `top`을 neo `-18px`, classic `-21px`로 둔다. 왼쪽·오른쪽은 3px 테두리 안쪽 끝에서 약 8px 들어간 neo `-5px`, classic `-19px`, 중간은 `left: 50%; transform: translateX(-50%)`다. Mermaid는 노드(링크 노드는 감싸는 `<a>`)에 `data-look`을 달므로 classic 값은 그 속성으로 덮는다. `foreignObject`의 `overflow: visible`로 라벨 상자 밖을 그린다.
- **색(2026-11-22)**: 글자 배경은 VS Code 미리보기가 노드 채움(`mainBkg`)에 쓰는 `var(--vscode-editorWidget-background, #ffffff)`로 불투명하게 칠한다. 같은 변수라 라이트·다크 테마에서 노드 채움과 함께 바뀌고, 변수가 없는 렌더러(Mermaid CLI)는 그 기본 채움 `#ffffff`가 된다. 글자색은 `apply_hover.py`가 노드 색상 class의 `classDef … stroke:#RRGGBB` 값을 읽어 노드별 규칙에 넣는다.
- **Alternatives considered(위치)**: 테두리 안쪽 끝(look마다 여백이 달라 classic에서 빈 공간이 남았고, 사용자가 테두리 선 위를 골라 대체). 테두리 바깥 위(레이아웃 엔진이 모르는 자리라 간선이 지나가 기각). 측정 시 CSS로 라벨을 키워 자리 예약(노드 테두리가 그 자리까지 감싸 노드가 커져 기각). 엣지 라벨처럼 70% 반투명 배경(테두리 선이 글자 뒤로 비쳐 기각).
- **Alternatives considered**: 라벨에 span을 넣고 themeCSS로 꾸미기(이전 방식 — GitHub에 글자가 남고 이름을 아래로 밀어 기각). `build_diagram.py`가 별도 style 블록을 쓰기(문서 끝 블록이 둘이 되고 `apply_hover.py`의 블록 제거와 충돌해 기각). `apply_hover.py`가 라벨만 보고 판정(`fileExtensions=false`에서 구분 불가로 기각).

- **Decision — 예시 정리**: SKILL.md와 `references/templates.md`의 `ComponentB@{ label: "ComponentB(state)" }` 예시를 FR-036에 맞는 `ComponentB@{ label: "class&nbsp;ComponentB" }`로 바꾼다.
- **Rationale**: FR-036은 라벨에 부가 설명을 넣지 않는다. 예시가 괄호 설명을 보여 주면 에이전트가 그대로 따라 써서 원본 표기 `foo()`와 헷갈린다.

- **Decision — 라벨 형식은 하나**: 라벨이 Id와 다른 노드는 표시어든 변화 표시든 모두 FR-007의 `Id@{ label: "…" }`로 쓴다. SKILL.md "Change marks" 표의 `Id["✨&nbsp;<b>Name</b>"]` 같은 대괄호 형식도 `Id@{ label: "✨&nbsp;<b>Name</b>" }`로 맞춘다(그룹의 `subgraph Id["라벨"]`은 그대로).
- **Rationale**: 같은 일에 형식이 두 가지면 에이전트가 두 규칙을 배워야 한다. `@{ label }`은 2026-11-13 clarify에서 사용자가 고른 형식이다. `build_diagram.py`는 줄 맨 앞의 Id만 읽고 009·010 파서는 두 형식을 다 읽으므로, 이미 만들어진 산출물도 그대로 동작한다.
- **Alternatives considered**: 노드 라벨을 모두 대괄호 `Id["…"]`로 통일(노드당 약 5토큰, 노드 11개 파일에서 약 50토큰 — 파일의 1% 남짓 — 를 아끼지만 사용자의 형식 결정을 뒤집어 기각).

## Decision: CRUD 이모지 설명 (FR-035, 2026-11-21)

- **Decision**: `build_diagram.py`가 이미 모은 CRUD class가 하나 이상이면 Mermaid text node `✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제`를 추가한다.
- **Rationale**: 조건과 문구가 모두 고정이므로 에이전트 판단, 설정, 새 의존성이 필요 없다.
- **Alternatives considered**: 에이전트가 직접 생성(불필요한 출력 변동성과 토큰 사용).

## Decision: 옅은 선 (FR-042~045, 2026-11-23)

- **Decision — 판단은 에이전트, 표시는 스크립트**: 에이전트는 간선이 사용 의존인지 판단해 사용 외 의존이면 `생성`·`전달`·`타입 참조` 중 하나를 라벨로 쓴다. `build_diagram.py`는 라벨이 이 셋 중 하나와 정확히 같을 때만 옅게 칠한다.
- **Rationale**: 판단에는 근거 읽기가 필요하지만 표시는 규칙만으로 정해진다(FR-008d와 같은 나눔). 라벨이 표시를 정하므로 에이전트 출력은 늘지 않는다(SC-020). 정확히 같은 글자만 보므로 `생성·호출`처럼 사용을 함께 밝힌 라벨은 진한 선이 된다.
- **Alternatives considered**: 에이전트가 `class eN …Faint` 줄을 직접 씀(출력과 실수가 늘어 기각). 라벨 대신 별도 표시어(`-.->` 등)(Mermaid 점선이 되어 사용자 결정과 어긋나 기각).

- **Decision — 모양**: 출발 노드 색에 알파 `4D`(약 30%)를 붙인 `stroke`, 굵기 3px(진한 선 3.5px), 라벨 글자 `color:<색>80`. 옅은 간선을 먼저 선언한다. 범례가 있을 때만 `flowchart.wrappingWidth: 400`.
- **Rationale**: 샘플(`.specify/assessments/architecture-view-assembly-edges/sample/`)로 사용자가 확정했다. `#RRGGBBAA` 색이면 Mermaid가 화살촉도 같은 색으로 그린다. SVG는 나중에 그린 것이 위에 오므로 먼저 선언한 간선이 아래에 깔린다. text 노드는 기본 폭(약 200px)에서 범례 줄이 꺾이는데, 폭 설정 한 줄로 풀린다. 이 설정은 모든 라벨에 적용되므로 범례가 있을 때만 넣어 기존 산출물을 바꾸지 않는다(FR-044). 색약 시뮬레이션(Machado 2009, CIE76)에서 진한 선과 자기 옅은 선의 ΔE는 26 이상이다.
- **Alternatives considered**: 회색(그룹 테두리와 헷갈려 기각), 점선·블러·물결선(사용자가 기각, 블러는 GitHub 미지원), 곡선(ELK가 간선별 curve를 무시하고 dagre는 레이아웃이 흐트러져 기각), 범례에 `&nbsp;`(줄바꿈이 풀리지 않아 기각).

- **Decision — 간선 ID와 설정 이름**: 간선 ID는 원래 순서로 매기고 줄 순서만 바꾼다. 설정은 `dependency.faintNonUsageEdges`(boolean), 요청 값은 `--faint-edges=`.
- **Rationale**: 켜고 끈 산출물의 ID가 같아야 한다(007 SC-011). `view_parser.py`의 간선 정규식은 ID 숫자와 줄 순서를 보지 않는다. 설정 이름은 기존 `dependency.*` 묶음에 둔다.

- **Decision — 암묵적 의존과 판단 순서(2026-11-23 보강)**: 간선 판단을 질문 네 개의 순서로 적고, 코드에 이름이 없지만 동작에 기대는 관계는 근거가 밝힐 때만 진한 선으로 그린다.
- **Rationale**: swemo `TouchOverlay → MemoCard`는 코드에 `MemoCard`가 나오지 않는 형제 관계지만, 카드가 터치를 소비한다는 가정 때문에 존재한다. 옅은 선은 "코드에 보이지만 영향이 작은 관계"이고, 이 관계는 "코드에 안 보이지만 깨지기 쉬운 관계"라 반대다. 질문 순서로 쓰면 기존 섞인 문장보다 판단이 갈리지 않는다.
- **Alternatives considered**: `덮음`·`배치`를 옅은 라벨에 추가(코드에 숨은 관계를 흐리게 해 기각). 코드 참조가 없으면 간선을 그리지 않음(변경 영향 정의와 어긋나 기각).

## Decision: 링크 노드 글자색 (FR-046, 2026-11-24)

- **Decision**: 설정이 `plain`이면 `build_diagram.py`가 config `themeCSS`에 `.node a, .node a:hover { color: inherit !important; text-decoration: none !important; }`를 더한다.
- **Rationale (밑줄)**: 평소 밑줄은 라벨 안 `<a>`에 붙은 기본 링크 스타일이라 같은 규칙에서 없앤다. 마우스를 올렸을 때의 밑줄(009)은 바깥 `.nodeLabel`에 걸린 장식이라 안쪽 `<a>`의 `none`으로 지워지지 않고 그대로 남는다.
- **Rationale**: 노드 라벨의 `<a>`는 보는 곳의 링크 색(VS Code `--vscode-textLink-foreground` 등)을 받는다. `inherit`는 그 노드 글자에 이미 정해진 색(삭제 표시의 회색 포함)을 따르므로 색 값을 새로 고를 필요가 없다. `themeCSS`는 Mermaid가 다이어그램 안에만 적용하므로 문서의 다른 링크에는 영향이 없고, 이미 다른 규칙이 `!important`로 들어 있는 자리다.
- **Alternatives considered**: (a) 라벨에서 `<a>`를 빼고 `click`만 남기기 — 노드 글자를 눌러 여는 동작이 바뀌고 hover·단계별 코드 공개(010)가 라벨 링크를 읽는다. (b) 색 값을 직접 지정 — 밝은·어두운 테마와 삭제 표시 색을 따로 맞춰야 한다.
