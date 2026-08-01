# Tasks: Architecture View Skill

**Input**: Design documents from `/specs/003-architecture-view-skill/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-interface.md, quickstart.md

**Tests**: spec.md에 테스트를 명시적으로 요청하지 않았고 이 기능은 실행 코드가 없는 Markdown 기반 skill이므로, 별도 자동화 테스트 태스크는 생성하지 않는다. 대신 `quickstart.md`의 수동 검증 시나리오를 Polish 단계 태스크로 포함한다.

**Organization**: 태스크는 spec.md의 User Story(P1/P2/P3)별로 그룹화되어 있다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 이 태스크가 속한 user story (US1, US2, US3)
- 모든 태스크에 정확한 파일 경로를 포함한다

## Path Conventions

이 기능은 전통적인 `src/`/`tests/` 구조가 아니라 Claude Code Skill 번들이다 (plan.md, Project Structure 참고):

- `.claude/skills/generating-architecture-views/SKILL.md`
- `.claude/skills/generating-architecture-views/references/templates.md`
- `.claude/skills/generating-architecture-views/references/examples.md`

이 스킬은 `.claude/skills/generating-zenuml-diagrams/`(기존 스킬)에 의존하지만, 그 스킬 자신의 파일은 수정하지 않는다(spec.md FR-018) — 아래 태스크 중 어떤 것도 `generating-zenuml-diagrams/` 아래 파일을 건드리지 않는다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: skill 디렉터리 뼈대 준비

- [ ] T001 `.claude/skills/generating-architecture-views/` 및 `.claude/skills/generating-architecture-views/references/` 디렉터리 생성

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story가 공통으로 의존하는 번들 자산(SKILL.md 뼈대, 섹션 템플릿) 준비

**⚠️ CRITICAL**: 이 단계가 끝나기 전에는 어떤 User Story 작업도 시작할 수 없음

- [ ] T002 [P] `.claude/skills/generating-architecture-views/SKILL.md` 뼈대 작성 — YAML frontmatter(`name: generating-architecture-views`, 구조/아키텍처 요청 트리거를 3인칭으로 명시하되 `generating-zenuml-diagrams`의 시퀀스/행동 트리거와 겹치지 않도록 구분하는 `description`)와 섹션 헤딩만 우선 채운다 (research.md Decision: Skill 이름; contracts/skill-interface.md Trigger)
- [ ] T003 [P] `.claude/skills/generating-architecture-views/references/templates.md` 작성 — Context+Dependency 섹션용 Mermaid `graph`/`flowchart`(+`subgraph`, 화살표) 템플릿과, Responsibility 섹션용 비교 항목(두 컴포넌트의 책임과 차이) 서술 템플릿을 담는다 (research.md Decision: 참조 파일 구조; data-model.md Context+Dependency Section, Responsibility Comparison Item)

**Checkpoint**: 이 지점부터 User Story별 작업을 시작할 수 있음

---

## Phase 3: User Story 1 - 구조와 책임을 명확히 이해하기 (Priority: P1) 🎯 MVP

**Goal**: 목적을 확인한 뒤, 설명에 근거한 컴포넌트·그룹·의존관계(Context+Dependency)와 그룹 내 전체 쌍을 이항대립 비교한 책임(Responsibility)을 생성한다 — 설명에 없는 내용은 지어내지 않는다.

**Independent Test**: quickstart.md 시나리오 1~4 — 목적 미확인 시 되묻기, Context+Dependency/Responsibility 정확성(n×(n-1)/2), 그룹 내 비의존 쌍도 비교 포함, 책임 미명시 컴포넌트 처리.

### Implementation for User Story 1

- [ ] T004 [US1] `SKILL.md`에 "목적 확인" 섹션 작성 — 목적을 이미 밝히지 않았으면 3지선다 질문(온보딩/특정 문제 진단/기타)을 먼저 하고, 애매한 답변·무응답이면 온보딩을 기본값으로 적용한 뒤 그 사실을 알리고, "기타"면 구체적으로 되묻는 규칙 (spec.md FR-001, FR-002, FR-003; research.md Decision: 목적 확인 질문 설계)
- [ ] T005 [US1] `SKILL.md`에 "Context+Dependency 생성 규칙" 섹션 작성 — 설명에 명시/함의된 컴포넌트·의존관계만 사용하고, 이름 접두사/네임스페이스나 명시적 계층·도메인 언급이 있을 때만 `subgraph`로 그룹을 만들며 신호가 없으면 전체를 그룹 1개로 취급(다이어그램에는 `subgraph` 미표시)하는 규칙을 작성하고 `references/templates.md`의 Mermaid 템플릿을 1단계 깊이로 링크 (spec.md FR-004, FR-006, FR-007; data-model.md Automatic Grouping Rule, Context+Dependency Section; research.md Decision: Context+Dependency 자동 그룹핑 및 표현)
- [ ] T006 [US1] `SKILL.md`에 "Responsibility 생성 규칙" 섹션 작성 — 그룹(그룹이 없으면 전체 컴포넌트 집합) 내부의 컴포넌트를 의존관계 유무와 무관하게 중복 없는 순서 없는 쌍으로 전부 비교해 정확히 n×(n-1)/2개의 항목을 만들고, 각 항목은 설명에서 확인 가능한 두 책임을 대조하며, 책임이 설명에 없는 컴포넌트는 "명시되지 않음"으로 표시하고 그 컴포넌트가 포함된 항목의 차이도 추측하지 않는 규칙을 작성하고 `references/templates.md`의 비교 항목 템플릿을 링크 (spec.md FR-008, FR-009, FR-010; data-model.md Responsibility Comparison Item; research.md Decision: Responsibility 비교 항목 생성 순서)
- [ ] T007 [US1] `SKILL.md`에 Anti-Pattern 체크리스트 AP-1~AP-5(설명에 없는 컴포넌트/의존관계 없음, 근거 없는 그룹 없음, 비교 항목 수가 정확히 n×(n-1)/2, 책임 미명시 시 추측 금지)를 복사-붙여넣기용 진행 체크리스트로 추가하고, "생성 → 체크리스트 대조 → 수정" 자기검증 워크플로 섹션 작성 (data-model.md Anti-Pattern Checklist, Architecture View 상태 전이; spec.md FR-019, FR-020; research.md Decision: 안티패턴 체크리스트 항목, 자기검증 워크플로 패턴)
- [ ] T008 [US1] `SKILL.md`에 "출력 파일" 섹션 작성 — 자기검증(Checked)을 통과한 구조 뷰를 채팅 응답에 코드로 노출하지 않고 Context+Dependency → Responsibility 순서로 `.zenuml/<slug>.architecture.md`에 저장하며, 같은 슬러그의 `.zenuml/<slug>.md`(존재한다면)는 건드리지 않는다는 규칙, 파일 저장이 불가능한 환경에서는 텍스트를 채팅에 직접 제공하는 대체 동작을 명시 (spec.md FR-021, FR-024 전반부; data-model.md Output Files)
- [ ] T009 [US1] `SKILL.md`에 "범위 밖 요청" 섹션 작성 — 실제 코드베이스 분석 요청, 클래스/배포 다이어그램 등 미지원 구조 표현 요청, 시스템에 등장하지 않는 일반적 개념 비교 요청 각각에 대한 안내 문구 (spec.md FR-013, FR-022, FR-023, Edge Cases)
- [ ] T010 [US1] `SKILL.md`에 최소 요청 예시(입력/출력 쌍) 추가 — quickstart.md 시나리오 2 기준, 그룹 신호 없는 2개 컴포넌트 입력 → Context+Dependency(그룹 없음) + Responsibility(1개 항목) 출력 예시
- [ ] T011 [US1] `SKILL.md`에 그룹 있는 요청 예시 추가 — quickstart.md 시나리오 3 기준, 3개 컴포넌트가 한 그룹에 속하고 그중 한 쌍은 서로 호출하지 않는 입력 → `subgraph` 1개 + 정확히 3개의 비교 항목(비의존 쌍 포함) 출력 예시

**Checkpoint**: User Story 1이 독립적으로 완전히 동작하고 테스트 가능해야 함 — 이 시점에서 이미 구조 뷰(Context+Dependency + Responsibility)만으로 완결된 가치를 제공함

---

## Phase 4: User Story 2 - 원할 때 시퀀스 다이어그램까지 이어가기 (Priority: P2)

**Goal**: 구조 뷰 완성 후, 시퀀스 다이어그램까지 만들지 사용자에게 확인하고, 동의할 때만 구조 뷰 내용을 컨텍스트로 담아 `generating-zenuml-diagrams`를 실행한다.

**Independent Test**: quickstart.md 시나리오 5, 6 — 위임 확인 질문 제시, 동의 시 실행, 거부/무응답 시 미실행·재권유 없음.

### Implementation for User Story 2

- [ ] T012 [US2] `SKILL.md`에 "위임 확인" 섹션 작성 — 구조 뷰가 `.zenuml/<slug>.architecture.md`에 저장된 직후, "이 구조를 바탕으로 시퀀스 다이어그램도 만들까요?" 같은 확인 질문을 반드시 제시하는 규칙과, 구조 뷰 생성 자체가 완료되지 못한 경우(대상 컴포넌트 특정 불가)에는 이 질문을 하지 않는 규칙 (spec.md FR-014, FR-017; data-model.md Delegation Handoff; research.md Decision: 위임 확인 질문과 컨텍스트 전달 방식)
- [ ] T013 [US2] `SKILL.md`에 "위임 실행" 섹션 작성 — 사용자가 동의하면 원래 설명 + Context+Dependency의 컴포넌트·그룹·의존관계 + Responsibility의 책임 정보를 하나의 보강된 자연어 프로세스 설명으로 재구성하고, 이를 마치 사용자가 직접 입력한 것처럼 `generating-zenuml-diagrams`의 기존 워크플로(요청 분류부터 출력·피드백 로그까지)를 그대로 따라 실행하며, 그 스킬의 SKILL.md나 동작 자체는 수정하지 않는다는 제약을 명시 (spec.md FR-015, FR-018; research.md Decision: 위임 확인 질문과 컨텍스트 전달 방식)
- [ ] T014 [US2] `SKILL.md`에 "위임 거부/무응답" 규칙 작성 — 동의하지 않거나 응답이 애매하면 `generating-zenuml-diagrams`를 실행하지 않고, 재차 권유하지 않으며, 구조 뷰만으로 응답을 마친다는 규칙(목적 확인과 달리 애매하면 "실행하지 않음"이 기본값임을 명시) (spec.md FR-016; research.md Decision: 모호한 입력 처리; Edge Cases)
- [ ] T015 [US2] `SKILL.md`의 Anti-Pattern 체크리스트에 AP-6(일반 개념 비교나 Runtime Flow 다이어그램을 직접 만들지 않음), AP-7(위임 확인을 했는지, 동의 없이 실행하지 않았는지)을 추가 (data-model.md Anti-Pattern Checklist; research.md Decision: 안티패턴 체크리스트 항목)
- [ ] T016 [US2] `SKILL.md`에 위임 관련 예시 추가 — quickstart.md 시나리오 5(동의 → 시퀀스 다이어그램까지 제시)와 시나리오 6(거부 → 구조 뷰만으로 종료) 각각 1개씩

**Checkpoint**: User Story 1과 2가 함께 독립적으로 동작해야 함 — 사용자가 원할 때만 시퀀스 다이어그램까지 이어짐

---

## Phase 5: User Story 3 - 그룹/컴포넌트 규모를 처음부터 통제하기 (Priority: P3)

**Goal**: Responsibility 섹션의 비교 항목 폭증(n×(n-1)/2)을 막기 위해, Context+Dependency 단계에서부터 꼭 필요한 컴포넌트·그룹만 만든다.

**Independent Test**: quickstart.md 시나리오 7 — 설명에 없는 컴포넌트를 추가하지 않는지, 큰 그룹(8개 이상)에서 경고가 나오는지.

### Implementation for User Story 3

- [ ] T017 [US3] `SKILL.md`에 "규모 통제" 섹션 작성 — Context+Dependency 생성 시 설명에 없는 컴포넌트나 그룹을 추가해 더 세분화하지 않는다는 규칙과, 하나의 그룹에 컴포넌트가 많아(예: 8개 이상, 28개 비교 항목) 결과가 길어질 것으로 예상되면 그 사실을 사용자에게 알리되 생성 자체는 거부하지 않는다는 규칙 (spec.md FR-011, FR-012; research.md Decision: 규모 통제)
- [ ] T018 [US3] `SKILL.md`에 규모 경고 예시 추가 — quickstart.md 시나리오 7(그룹 내 컴포넌트 8개 → 28개 비교 항목 예상) 기준 경고 문구 예시

**Checkpoint**: 모든 User Story가 독립적으로 동작해야 함

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 skill의 품질 확인

- [ ] T019 `SKILL.md` 본문 길이가 Anthropic 권장 기준(~500줄) 이내인지 확인하고, 초과 시 세부 내용을 `references/templates.md`로 이동
- [ ] T020 [P] `.claude/skills/generating-architecture-views/references/examples.md` 작성 — 완성된 구조 뷰 예시 2~3개(온보딩 목적 1개, 특정 문제 진단 목적 1개, 위임 동의로 시퀀스 다이어그램까지 이어진 예시 1개)
- [ ] T021 `SKILL.md`의 YAML `description` 필드가 3인칭 서술이며, `generating-zenuml-diagrams`(시퀀스/행동)와 트리거가 겹치지 않게 "구조/아키텍처" 키워드를 명확히 구분하는지 검토
- [ ] T022 `quickstart.md`의 시나리오 1~9를 완성된 skill에 대해 실행하고, 통과/실패를 기록 (SC-001~SC-008 커버)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 — 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 시작 — 모든 User Story를 블로킹함
- **User Stories (Phase 3~5)**: 모두 Foundational 완료에 의존
  - 우선순위 순서(P1 → P2 → P3)로 순차 진행 권장 — 같은 파일(`SKILL.md`)을 계속 확장하므로 순차 진행이 충돌을 줄인다
- **Polish (Phase 6)**: 원하는 모든 User Story 완료에 의존

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 이후 시작 가능 — 다른 스토리에 의존하지 않음. 구조 뷰만으로 완결된 가치를 제공하는 최소 단위
- **User Story 2 (P2)**: Foundational 이후 시작 가능 — US1이 만든 구조 뷰(Context+Dependency, Responsibility)의 내용을 위임 컨텍스트로 사용하지만, "구조 뷰가 있다"는 전제만 필요할 뿐 US1의 SKILL.md 섹션을 수정하지는 않으므로 독립적으로 테스트 가능
- **User Story 3 (P3)**: Foundational 이후 시작 가능 — US1의 Context+Dependency 생성 규칙에 제약을 추가하는 별도 섹션이라 독립적으로 테스트 가능

### Within Each User Story

- 같은 파일(`SKILL.md`)을 편집하는 태스크는 충돌 방지를 위해 순차 진행
- 스토리 완료 후 다음 우선순위로 이동

### Parallel Opportunities

- Phase 2의 T002, T003은 서로 다른 파일이므로 병렬 실행 가능
- Phase 6의 T020은 새 파일(`references/examples.md`)이라 T019/T021과 병렬 실행 가능하지만, T019와 T021은 둘 다 `SKILL.md`를 다루므로 순차 진행
- User Story 3개는 모두 `SKILL.md`의 서로 다른 섹션을 추가하는 작업이라 논리적으로는 독립적이지만, 파일 충돌을 피하려면 한 번에 한 스토리씩 진행하는 것을 권장

---

## Parallel Example: Phase 2 (Foundational)

```bash
# T002와 T003은 서로 다른 파일을 다루므로 함께 실행 가능:
Task: "SKILL.md 뼈대(frontmatter + 섹션 헤딩) 작성"
Task: "references/templates.md에 Context+Dependency, Responsibility 템플릿 작성"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료 (SKILL.md 뼈대 + 섹션 템플릿) — 모든 스토리의 전제조건
3. Phase 3: User Story 1 완료
4. **STOP and VALIDATE**: quickstart.md 시나리오 1~4로 User Story 1을 독립적으로 검증
5. 이 시점에서 이미 "설명에 근거한 구조 + 명확한 책임 구분"이라는 핵심 가치를 제공하는 MVP가 완성됨(시퀀스 다이어그램 위임 없이도 완결된 산출물)

### Incremental Delivery

1. Setup + Foundational 완료 → 기반 준비 완료
2. User Story 1 추가 → 독립 검증 → MVP 완성(구조 뷰만)
3. User Story 2 추가(위임 확인/실행) → 독립 검증 → 원할 때 시퀀스 다이어그램까지 이어짐
4. User Story 3 추가(규모 통제) → 독립 검증 → 큰 그룹에서도 안전장치 확보
5. Polish(Phase 6) → 문서 길이/예시/description 품질/quickstart 전체 재검증

---

## Notes

- [P] 태스크 = 서로 다른 파일, 의존성 없음
- [Story] 라벨은 태스크를 특정 user story로 추적하기 위함
- 각 user story는 독립적으로 완료·테스트 가능해야 함
- 이 기능은 실행 코드가 없으므로 "테스트 실패 확인" 절차 대신 quickstart.md 시나리오 수동 검증으로 대체함
- 논리적 작업 단위(태스크)마다 커밋 권장
- 체크포인트마다 멈춰서 해당 스토리를 독립적으로 검증할 것
- 피할 것: 모호한 태스크, 동일 파일 동시 편집 충돌, 스토리 간 독립성을 깨는 교차 의존, `generating-zenuml-diagrams/` 파일 수정(FR-018)
