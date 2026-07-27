# Tasks: ZenUML Diagram Skill

**Input**: Design documents from `/specs/001-zenuml-diagram-skill/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-interface.md, quickstart.md

**Tests**: spec.md에 테스트를 명시적으로 요청하지 않았고 이 기능은 실행 코드가 없는 Markdown 기반 skill이므로, 별도 자동화 테스트 태스크는 생성하지 않는다. 대신 `quickstart.md`의 수동 검증 시나리오를 Polish 단계 태스크로 포함한다.

**Organization**: 태스크는 spec.md의 User Story(P1/P2/P3)별로 그룹화되어 있다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 이 태스크가 속한 user story (US1, US2, US3)
- 모든 태스크에 정확한 파일 경로를 포함한다

## Path Conventions

이 기능은 전통적인 `src/`/`tests/` 구조가 아니라 Claude Code Skill 번들이다 (plan.md, Project Structure 참고):

- `.claude/skills/generating-zenuml-diagrams/SKILL.md`
- `.claude/skills/generating-zenuml-diagrams/references/syntax.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: skill 디렉터리 뼈대 준비

- [X] T001 `.claude/skills/generating-zenuml-diagrams/` 및 `.claude/skills/generating-zenuml-diagrams/references/` 디렉터리 생성

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story가 공통으로 의존하는 번들 자산(문법 레퍼런스, SKILL.md 뼈대) 준비

**⚠️ CRITICAL**: 이 단계가 끝나기 전에는 어떤 User Story 작업도 시작할 수 없음

- [X] T002 [P] `mermaid-js/zenuml-core`의 `docs/DSL_SYNTAX.md`를 재구성해 `.claude/skills/generating-zenuml-diagrams/references/syntax.md` 작성 — 상단에 MIT 출처 고지(원본 저장소 링크 포함)와 100줄 이상 대비 목차를 포함하고, 참가자 선언·동기/비동기 메시지·반환값·조건문/반복문·예외 처리·주석·스타일링 섹션을 담는다 (research.md Decision: 참조 파일 구조, 라이선스 고지; data-model.md Syntax Reference; spec.md FR-003, FR-004, FR-009)
- [X] T003 [P] `.claude/skills/generating-zenuml-diagrams/SKILL.md` 뼈대 작성 — YAML frontmatter(`name: generating-zenuml-diagrams`, ZenUML/시퀀스 다이어그램 요청 트리거와 "정확하고 군더더기 없는 생성"을 3인칭으로 명시하는 `description`)와 섹션 헤딩만 우선 채운다 (research.md Decision: Skill 이름; contracts/skill-interface.md Trigger)

**Checkpoint**: 이 지점부터 User Story별 작업을 시작할 수 있음

---

## Phase 3: User Story 1 - 설명한 대로만 정확한 다이어그램 받기 (Priority: P1) 🎯 MVP

**Goal**: 자연어 프로세스 설명을 입력받아, 설명에 언급된 참가자·상호작용만 포함하는 문법적으로 정확한 ZenUML DSL을 생성한다.

**Independent Test**: "Client가 Server.getData()를 호출한다" 같은 단순 설명과, 조건/반복이 섞인 설명을 입력해 생성된 DSL에 설명되지 않은 참가자·메시지·분기가 없는지 직접 대조한다 (quickstart.md 시나리오 1, 2).

### Implementation for User Story 1

- [X] T004 [US1] `SKILL.md`에 "생성 규칙" 섹션 작성 — `references/syntax.md`를 1단계 깊이로 링크하고, 설명에 명시되었거나 명확히 함의된 참가자·메시지·제어 흐름만 사용하도록 지시 (spec.md FR-001, FR-002, FR-003)
- [X] T005 [US1] `SKILL.md`에 단순 요청 예시(입력/출력 쌍) 추가 — quickstart.md 시나리오 1("Client가 Server.getData()를 호출")을 기준으로 최소 다이어그램 생성 예시 수록
- [X] T006 [US1] `SKILL.md`에 조건/반복이 포함된 요청 예시(입력/출력 쌍) 추가 — quickstart.md 시나리오 2를 기준으로, 설명에 없는 예외 처리나 참가자를 추가하지 않는 예시 수록

**Checkpoint**: User Story 1이 독립적으로 완전히 동작하고 테스트 가능해야 함

---

## Phase 4: User Story 2 - 생성 전 자기검증으로 군더더기 걸러내기 (Priority: P2)

**Goal**: 다이어그램 초안을 사용자에게 보여주기 전, 흔한 안티패턴이 있는지 자체 점검하고 필요시 수정한다.

**Independent Test**: 여러 참가자가 얽힌 복잡한 설명을 입력해, 결과물이 안티패턴 체크리스트를 통과했는지 확인한다 (quickstart.md 시나리오 2).

### Implementation for User Story 2

- [X] T007 [US2] `SKILL.md`에 Anti-Pattern 체크리스트(AP-1~AP-5: 요청되지 않은 참가자/메시지/분기 없음, 근거 없는 예외 처리·반환값 없음, 가장 얕은 중첩 사용) 를 복사-붙여넣기용 진행 체크리스트 형태로 추가 (data-model.md Anti-Pattern Checklist; research.md Decision: 안티패턴 체크리스트 항목)
- [X] T008 [US2] `SKILL.md`에 "생성 → 체크리스트 대조 → 수정" 자기검증 워크플로 섹션 작성 — T007의 체크리스트를 사용해 초안(Draft)이 전 항목을 통과(Checked)한 뒤에만 사용자에게 제시(Presented)하도록 명시 (data-model.md 상태 전이; spec.md FR-005, FR-006; research.md Decision: 자기검증 워크플로 패턴)

**Checkpoint**: User Story 1과 2가 함께 독립적으로 동작해야 함 — 결과물이 이제 자기검증을 거침

---

## Phase 5: User Story 3 - 설명이 불충분할 때 지어내지 않고 되묻기 (Priority: P3)

**Goal**: 설명이 다이어그램을 정확히 구성하기에 불충분할 때, 내용을 지어내지 않고 사용자에게 구체적으로 되묻는다.

**Independent Test**: 호출 주체나 순서가 불명확한 설명을 입력해, 스킬이 다이어그램을 즉시 만들지 않고 명확화 질문을 하는지 확인한다 (quickstart.md 시나리오 3).

### Implementation for User Story 3

- [X] T009 [US3] `SKILL.md`에 "명확화 판단 기준" 섹션 작성 — 호출 주체/대상 불명확, 분기 조건 불명확 등 다이어그램 정확성에 직접 영향을 주는 모호함을 식별하는 기준과, 그런 경우 구체적 질문을 하고 다이어그램을 생성하지 않는 규칙을 명시 (spec.md FR-007; research.md Decision: 모호한 입력 처리)
- [X] T010 [US3] `SKILL.md`에 "범위 밖 요청 안내" 섹션 작성 — 시퀀스 다이어그램 외 유형 요청(FR-008), 기존 다이어그램/코드 변환 요청, 렌더링된 이미지 요청(FR-010)에 대해 각각 어떻게 안내할지 명시 (contracts/skill-interface.md 범위 밖 요청; spec.md Edge Cases)

**Checkpoint**: 모든 User Story가 독립적으로 동작해야 함

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 skill의 품질 확인

- [X] T011 [P] `SKILL.md` 본문 길이가 Anthropic 권장 기준(~500줄) 이내인지 확인하고, 초과 시 세부 내용을 `references/syntax.md`로 이동
- [X] T012 [P] `references/syntax.md` 상단의 MIT 출처 고지가 원본(mermaid-js/zenuml-core) 링크와 함께 정확히 남아 있는지 확인 (spec.md FR-009)
- [X] T013 [P] `SKILL.md`의 YAML `description` 필드가 3인칭 서술이며 트리거 조건(ZenUML/시퀀스 다이어그램)과 핵심 가치(정확성·군더더기 없음)를 모두 포함하는지 검토
- [X] T014 `quickstart.md`의 시나리오 1~5와 세션 내 일관성 확인 절차를 완성된 skill에 대해 실행하고, 통과/실패를 기록 (SC-001~SC-005 커버)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 — 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 시작 — 모든 User Story를 블로킹함
- **User Stories (Phase 3~5)**: 모두 Foundational 완료에 의존
  - 우선순위 순서(P1 → P2 → P3)로 순차 진행 권장, 또는 병렬 진행 가능(각 스토리가 SKILL.md의 서로 다른 섹션을 다루므로 충돌 최소화를 위해 순차 권장)
- **Polish (Phase 6)**: 원하는 모든 User Story 완료에 의존

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 이후 시작 가능 — 다른 스토리에 의존하지 않음
- **User Story 2 (P2)**: Foundational 이후 시작 가능 — US1이 만든 "생성 규칙" 위에 자기검증 단계를 추가하지만, 독립적으로 테스트 가능
- **User Story 3 (P3)**: Foundational 이후 시작 가능 — US1/US2와 별개의 SKILL.md 섹션(명확화 판단)이므로 독립적으로 테스트 가능

### Within Each User Story

- 같은 파일(`SKILL.md`)을 편집하는 태스크는 충돌 방지를 위해 순차 진행
- 스토리 완료 후 다음 우선순위로 이동

### Parallel Opportunities

- Phase 2의 T002, T003은 서로 다른 파일이므로 병렬 실행 가능
- Phase 6의 T011, T012, T013은 서로 다른 검토 관점이므로 병렬 실행 가능
- User Story 3개는 모두 `SKILL.md`의 서로 다른 섹션을 추가하는 작업이라 논리적으로는 독립적이지만, 파일 충돌을 피하려면 한 번에 한 스토리씩 진행하는 것을 권장

---

## Parallel Example: Phase 2 (Foundational)

```bash
# T002와 T003은 서로 다른 파일을 다루므로 함께 실행 가능:
Task: "mermaid-js/zenuml-core docs/DSL_SYNTAX.md를 재구성해 references/syntax.md 작성"
Task: "SKILL.md 뼈대(frontmatter + 섹션 헤딩) 작성"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료 (문법 레퍼런스 + SKILL.md 뼈대) — 모든 스토리의 전제조건
3. Phase 3: User Story 1 완료
4. **STOP and VALIDATE**: quickstart.md 시나리오 1, 2로 User Story 1을 독립적으로 검증
5. 이 시점에서 이미 "정확한 ZenUML 생성"이라는 핵심 가치를 제공하는 MVP가 완성됨

### Incremental Delivery

1. Setup + Foundational 완료 → 기반 준비 완료
2. User Story 1 추가 → 독립 검증 → MVP 완성
3. User Story 2 추가(자기검증 루프) → 독립 검증 → 품질 게이트 강화
4. User Story 3 추가(명확화 질문) → 독립 검증 → 모호한 입력에 대한 안전장치 완성
5. Polish(Phase 6) → 문서 길이/라이선스 고지/description 품질/quickstart 전체 재검증

---

## Notes

- [P] 태스크 = 서로 다른 파일, 의존성 없음
- [Story] 라벨은 태스크를 특정 user story로 추적하기 위함
- 각 user story는 독립적으로 완료·테스트 가능해야 함
- 이 기능은 실행 코드가 없으므로 "테스트 실패 확인" 절차 대신 quickstart.md 시나리오 수동 검증으로 대체함
- 논리적 작업 단위(태스크)마다 커밋 권장
- 체크포인트마다 멈춰서 해당 스토리를 독립적으로 검증할 것
- 피할 것: 모호한 태스크, 동일 파일 동시 편집 충돌, 스토리 간 독립성을 깨는 교차 의존

---

## Phase 7: Convergence

- [X] T015 `.claude/skills/generating-zenuml-diagrams/SKILL.md`에 참가자 수가 매우 많거나 프로세스가 지나치게 복잡한 설명이 주어졌을 때 결과가 읽기 어려워질 수 있음을 사용자에게 알리는 안내를 추가 per spec.md Edge Case: 참가자 수/복잡도 (missing)

---

## Phase 8: Output File Link

- [X] T016 `.claude/skills/generating-zenuml-diagrams/SKILL.md`에 "Output file" 섹션 추가 — 자기검증(AP-1~AP-5)을 통과한 다이어그램을 채팅 응답에 코드로 노출하지 않고, ZenUML 원문을 Mermaid `zenuml` 코드펜스에 담아 `.zenuml/<slug>.md` 파일에 저장한 뒤 그 파일을 가리키는 상대 경로 링크만 응답에 남기는 규칙을 명시한다(번역 불필요 — VS Code 마크다운 프리뷰가 `zenuml` 타입을 네이티브로 렌더링함이 실측으로 확인됨; Claude Artifact는 발행 시 자동 팝업을 억제할 수 없고 `zenuml` 타입도 렌더링되지 않아 사용하지 않는다). 파일 저장이 불가능한 환경에서는 채팅 응답에 ZenUML DSL 텍스트를 직접 제공하는 규칙도 포함한다 per spec.md FR-011
- [X] T017 `.gitignore`에 `.zenuml/` 항목 추가 per research.md Decision: 출력 파일 위치와 이름
