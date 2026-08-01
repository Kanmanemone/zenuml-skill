# Contract: `generating-architecture-views` Skill Interface

이 skill은 API나 CLI가 아니라 Claude Code Skill이므로, "계약"은 SKILL.md가 Claude에게 보장해야 하는 **입력→동작→출력 규약**으로 정의한다. 이 스킬은 `generating-zenuml-diagrams`에 의존하므로, 그 스킬의 계약(001의 `contracts/skill-interface.md`)도 함께 참고해야 한다.

## Trigger (언제 이 skill이 선택되어야 하는가)

- 사용자가 시스템/프로세스의 "구조", "아키텍처", "컴포넌트 관계", "책임", "구조를 이해하고 싶다" 류의 요청을 할 때 — 특히 이미 시퀀스 다이어그램을 본 뒤 "구조는 잘 모르겠다"고 말하는 경우.
- SKILL.md frontmatter의 `description`은 이 트리거 조건과 스킬이 하는 일(목적에 맞는 구조 뷰 생성, 이어서 시퀀스 다이어그램까지 확인 후 생성)을 3인칭으로 명시해야 하며, `generating-zenuml-diagrams`(시퀀스/행동 전용)와 트리거가 겹치지 않도록 "구조/아키텍처" 쪽 키워드를 명확히 구분해야 한다.

## Input Contract

| 필드 | 필수 | 설명 |
|------|------|------|
| description | 필수 | 구조 뷰로 표현할 프로세스/시스템에 대한 자연어 설명 |
| purpose | 선택 | 사용자가 이미 목적(온보딩/특정 문제 진단/기타)을 밝힌 경우. 없으면 skill이 먼저 확인 질문을 한다 |

**전제조건**: `description`이 비어있거나 대상 컴포넌트를 특정할 수 없으면, skill은 구조 뷰를 생성하지 않고 무엇을 그려야 하는지 되묻는다. `purpose`가 없으면, 컴포넌트를 특정할 수 있더라도 구조 뷰 생성 전에 반드시 목적 확인 질문을 먼저 한다(spec.md FR-001).

## Output Contract

### 성공 시 (목적 확정 + 대상 컴포넌트 식별됨, 파일 저장 가능)

```text
<.zenuml/<slug>.architecture.md 를 가리키는 상대 경로 링크 한 줄>

시퀀스 다이어그램까지 만들까요? [예/아니오]
```

- 채팅 응답에는 구조 뷰 코드를 직접 노출하지 않는다 — Checked 상태에 도달한 구조 뷰(data-model.md 참조)를 `.zenuml/<slug>.architecture.md`에 저장하고, 그 파일을 가리키는 상대 경로 링크와 위임 확인 질문을 함께 응답에 남긴다(spec.md FR-021, FR-014).
- 파일에는 Components & Dependencies 섹션 다음 Responsibility 섹션이 이 순서로 온다(spec.md FR-005).
- 설명에 없는 컴포넌트·의존관계·그룹·책임 차이를 포함해서는 안 된다(spec.md FR-004, FR-006, FR-009, FR-010).

### 위임 확인 질문에 사용자가 동의한 경우

- 스킬은 구조 뷰의 컴포넌트·그룹·의존관계·책임 정보를 반영한 보강된 프로세스 설명을 구성해, `generating-zenuml-diagrams`를 그 설명으로 실행한다(spec.md FR-015, research.md Decision: 위임 확인 질문과 컨텍스트 전달 방식).
- 그 결과(`.zenuml/<slug>.md` 링크 또는 명확화 질문 등, 001의 Output Contract 그대로)가 구조 뷰 응답에 이어서 사용자에게 제시된다.

### 위임 확인 질문에 사용자가 동의하지 않거나 응답하지 않은 경우

```text
(추가 응답 없음 — 구조 뷰만으로 종료)
```

- 스킬은 `generating-zenuml-diagrams`를 실행하지 않고, 재차 권유하지 않는다(spec.md FR-016, Edge Cases).

### 성공 시 (파일 저장 불가능한 환경)

```text
<구조 뷰 텍스트 — Components & Dependencies, Responsibility 섹션>

시퀀스 다이어그램까지 만들까요? [예/아니오]
```

- 파일시스템 접근이 없는 환경에서는 `.zenuml/` 링크 대신 구조 뷰 텍스트를 채팅 응답에 직접 제공한다(spec.md FR-024). 동의 시 이어지는 `generating-zenuml-diagrams` 실행에도 그 스킬 자신의 동일한 대체 동작이 적용된다.

### 목적 확인이 필요할 때 (purpose 미확정)

- 구조 뷰를 생성하지 않고, 3지선다 질문(온보딩/특정 문제 진단/기타)을 먼저 제시한다(spec.md FR-001, research.md Decision: 목적 확인 질문 설계).
- 애매한 답변이 오면 추측하지 않고 기본값(온보딩)을 적용한 뒤 그 사실을 알린다(spec.md FR-002).
- "기타"를 고르면 어떤 범위를 원하는지 한 문장으로 되묻는다(spec.md FR-003).

### 명확화가 필요할 때 (대상 컴포넌트 특정 불가)

- 구조 뷰를 생성하지 않고, 어떤 프로세스/시스템을 그려야 하는지 구체적으로 되묻는다. 이 경우 위임 확인 질문도 하지 않는다(spec.md FR-017).

### 범위 밖 요청일 때

- Runtime Flow(실행 순서/흐름)를 즉시 만들어달라고 요청하면: 이 스킬은 직접 그리지 않으므로, 구조 뷰를 먼저 만들고 그 뒤 위임 확인 질문의 흐름으로 자연스럽게 안내한다(spec.md FR-005, FR-014).
- "헷갈리는 개념 비교"(시스템에 없는 일반 개념)를 요청하면: 이번 범위에 없음을 안내한다(spec.md FR-013, Edge Cases).
- 클래스/배포 다이어그램 등 지원하지 않는 구조 표현을 요청하면: 지원 범위를 안내한다(spec.md FR-023).
- 실제 코드베이스 분석을 요청하면: 자연어 설명만 입력으로 지원함을 안내한다(spec.md FR-022, Edge Cases).

## Error/Fallback Behavior

이 skill에는 실행 코드가 없으므로 "예외"는 발생하지 않는다. 대신 위 "목적 확인이 필요할 때", "명확화가 필요할 때", "위임 확인 질문에 동의하지 않은 경우", "범위 밖 요청일 때" 네 분기가 비-happy-path이며, 모두 사용자에게 명확한 다음 행동(질문에 답하거나, 범위 밖임을 인지하거나, 구조 뷰만으로 만족하거나, 다른 스킬로 안내받음)을 제시하는 것으로 끝난다.
