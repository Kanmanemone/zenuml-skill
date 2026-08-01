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

- [X] T001 `.claude/skills/generating-architecture-views/` 및 `.claude/skills/generating-architecture-views/references/` 디렉터리 생성

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story가 공통으로 의존하는 번들 자산(SKILL.md 뼈대, 섹션 템플릿) 준비

**⚠️ CRITICAL**: 이 단계가 끝나기 전에는 어떤 User Story 작업도 시작할 수 없음

- [X] T002 [P] `.claude/skills/generating-architecture-views/SKILL.md` 뼈대 작성 — YAML frontmatter(`name: generating-architecture-views`, 구조/아키텍처 요청 트리거를 3인칭으로 명시하되 `generating-zenuml-diagrams`의 시퀀스/행동 트리거와 겹치지 않도록 구분하는 `description`)와 섹션 헤딩만 우선 채운다 (research.md Decision: Skill 이름; contracts/skill-interface.md Trigger)
- [X] T003 [P] `.claude/skills/generating-architecture-views/references/templates.md` 작성 — Components & Dependencies 섹션용 Mermaid `graph`/`flowchart`(+`subgraph`, 화살표) 템플릿과, Responsibility 섹션용 그룹 간/그룹 내 비교 항목 서술 템플릿을 담는다 (research.md Decision: 참조 파일 구조; data-model.md Components & Dependencies Section, Responsibility Comparison Item, Group Comparison Item)

**Checkpoint**: 이 지점부터 User Story별 작업을 시작할 수 있음

---

## Phase 3: User Story 1 - 구조와 책임을 명확히 이해하기 (Priority: P1) 🎯 MVP

**Goal**: 목적을 확인한 뒤, 설명에 근거한 컴포넌트·그룹·의존관계(Components & Dependencies)와 그룹 간·그룹 내 전체 쌍을 이항대립 비교한 책임(Responsibility)을 생성한다 — 설명에 없는 내용은 지어내지 않는다.

**Independent Test**: quickstart.md 시나리오 1~5 — 목적 미확인 시 되묻기, Components & Dependencies/Responsibility 정확성(그룹 내 n×(n-1)/2, 그룹 간 m×(m-1)/2), 그룹 내 비의존 쌍도 비교 포함, 그룹 간 비교가 그룹 레이블만 근거로 하는지, 책임 미명시 컴포넌트 처리.

### Implementation for User Story 1

- [X] T004 [US1] `SKILL.md`에 "목적 확인" 섹션 작성 — 목적을 이미 밝히지 않았으면 3지선다 질문(온보딩/특정 문제 진단/기타)을 먼저 하고, 애매한 답변·무응답이면 온보딩을 기본값으로 적용한 뒤 그 사실을 알리고, "기타"면 구체적으로 되묻는 규칙 (spec.md FR-001, FR-002, FR-003; research.md Decision: 목적 확인 질문 설계)
- [X] T005 [US1] `SKILL.md`에 "Components & Dependencies 생성 규칙" 섹션 작성 — 설명에 명시/함의된 컴포넌트·의존관계만 사용하고, 이름 접두사/네임스페이스나 명시적 계층·도메인 언급이 있을 때만 `subgraph`로 그룹을 만들며 신호가 없으면 전체를 그룹 1개로 취급(다이어그램에는 `subgraph` 미표시)하는 규칙을 작성하고 `references/templates.md`의 Mermaid 템플릿을 1단계 깊이로 링크 (spec.md FR-004, FR-006, FR-007; data-model.md Automatic Grouping Rule, Components & Dependencies Section; research.md Decision: Components & Dependencies 자동 그룹핑 및 표현)
- [X] T006 [US1] `SKILL.md`에 "Responsibility 생성 규칙 — 그룹 내부" 섹션 작성 — 그룹(그룹이 없으면 전체 컴포넌트 집합) 내부의 컴포넌트를 의존관계 유무와 무관하게 중복 없는 순서 없는 쌍으로 전부 비교해 정확히 n×(n-1)/2개의 항목을 만들고, 각 항목은 설명에서 확인 가능한 두 책임을 대조하며, 책임이 설명에 없는 컴포넌트는 "명시되지 않음"으로 표시하고 그 컴포넌트가 포함된 항목의 차이도 추측하지 않는 규칙을 작성하고 `references/templates.md`의 비교 항목 템플릿을 링크 (spec.md FR-008, FR-009, FR-010; data-model.md Responsibility Comparison Item; research.md Decision: Responsibility 비교 항목 생성 순서)
- [X] T007 [US1] `SKILL.md`에 "Responsibility 생성 규칙 — 그룹 간" 섹션 작성 — 그룹이 2개 이상이면 그룹 자체도 중복 없는 순서 없는 쌍으로 전부 비교해 정확히 m×(m-1)/2개의 그룹 비교 항목을 만들고(그룹이 1개 이하면 생성하지 않음), 각 항목은 그룹에 실제로 부여된 이름/레이블만 근거로 하며 그 이상의 역할·목적을 추측하지 않는 규칙을 작성. Responsibility 섹션 안에서 그룹 간 비교를 그룹별 컴포넌트 비교보다 먼저 배치(넓은 것에서 좁은 것 순) (spec.md FR-025, FR-026; data-model.md Group Comparison Item; research.md Decision: 그룹 간(Group-to-Group) 비교 추가)
- [X] T008 [US1] `SKILL.md`에 Anti-Pattern 체크리스트 AP-1~AP-7(설명에 없는 컴포넌트/의존관계 없음, 근거 없는 그룹 없음, 그룹 내 비교 항목 수가 정확히 n×(n-1)/2, 그룹 간 비교 항목 수가 정확히 m×(m-1)/2이고 레이블만 근거로 함, 책임 미명시 시 추측 금지, 시스템에 없는 일반적 개념 비교 섹션 미생성)을 복사-붙여넣기용 진행 체크리스트로 추가하고, "생성 → 체크리스트 대조 → 수정" 자기검증 워크플로 섹션 작성 (data-model.md Anti-Pattern Checklist, Architecture View 상태 전이; spec.md FR-013, FR-019, FR-020, FR-025, FR-026; research.md Decision: 안티패턴 체크리스트 항목, 자기검증 워크플로 패턴) — AP-7은 FR-013(Responsibility 범위 밖의 일반 개념 비교 금지)이 User Story 1 체크포인트에서부터 자기검증되도록 여기에 포함한다(US2로 미루지 않음)
- [X] T009 [US1] `SKILL.md`에 "출력 파일" 섹션 작성 — 자기검증(Checked)을 통과한 구조 뷰를 채팅 응답에 코드로 노출하지 않고 Components & Dependencies → Responsibility(그룹 간 비교 → 그룹별 컴포넌트 비교) 순서로 `.zenuml/<slug>.architecture.md`에 저장하며, 같은 슬러그의 `.zenuml/<slug>.md`(존재한다면)는 건드리지 않는다는 규칙, 파일 저장이 불가능한 환경에서는 구조 뷰 텍스트를 채팅에 직접 제공하는 대체 동작을 명시 (spec.md FR-021, FR-024 — 구조 뷰 쪽; data-model.md Output Files). 위임 실행 쪽 대체 동작은 T015에서 다룸
- [X] T010 [US1] `SKILL.md`에 "범위 밖 요청" 섹션 작성 — 실제 코드베이스 분석 요청, 클래스/배포 다이어그램 등 미지원 구조 표현 요청, 시스템에 등장하지 않는 일반적 개념 비교 요청 각각에 대한 안내 문구 (spec.md FR-013, FR-022, FR-023, Edge Cases)
- [X] T011 [US1] `SKILL.md`에 최소 요청 예시(입력/출력 쌍) 추가 — quickstart.md 시나리오 2 기준, 그룹 신호 없는 2개 컴포넌트 입력 → Components & Dependencies(그룹 없음) + Responsibility(1개 항목, 그룹 간 비교 없음) 출력 예시
- [X] T012 [US1] `SKILL.md`에 그룹 1개짜리 요청 예시 추가 — quickstart.md 시나리오 3 기준, 3개 컴포넌트가 한 그룹에 속하고 그중 한 쌍은 서로 호출하지 않는 입력 → `subgraph` 1개 + 그룹 내 비교 3개(비의존 쌍 포함) + 그룹이 하나뿐이므로 그룹 간 비교 없음 출력 예시
- [X] T013 [US1] `SKILL.md`에 그룹 3개 이상 요청 예시 추가 — quickstart.md 시나리오 4 기준, 서로 다른 그룹 3개(그룹을 가로지르는 의존 화살표 포함)에 걸친 입력 → `subgraph` 3개 + 그룹 간 비교 3×2/2=3개(그룹 레이블만 근거) + 각 그룹 내부 컴포넌트 비교가 모두 나타나고, 서로 다른 그룹에 속한 컴포넌트끼리의 비교는 나타나지 않는 출력 예시

**Checkpoint**: User Story 1이 독립적으로 완전히 동작하고 테스트 가능해야 함 — 이 시점에서 이미 구조 뷰(Components & Dependencies + Responsibility)만으로 완결된 가치를 제공함

---

## Phase 4: User Story 2 - 원할 때 시퀀스 다이어그램까지 이어가기 (Priority: P2)

**Goal**: 구조 뷰 완성 후, 시퀀스 다이어그램까지 만들지 사용자에게 확인하고, 동의할 때만 구조 뷰 내용을 컨텍스트로 담아 `generating-zenuml-diagrams`를 실행한다.

**Independent Test**: quickstart.md 시나리오 6, 7 — 위임 확인 질문 제시, 동의 시 실행, 거부/무응답 시 미실행·재권유 없음.

### Implementation for User Story 2

- [X] T014 [US2] `SKILL.md`에 "위임 확인" 섹션 작성 — 구조 뷰가 `.zenuml/<slug>.architecture.md`에 저장된 직후, "이 구조를 바탕으로 시퀀스 다이어그램도 만들까요?" 같은 확인 질문을 반드시 제시하는 규칙과, 구조 뷰 생성 자체가 완료되지 못한 경우(대상 컴포넌트 특정 불가)에는 이 질문을 하지 않는 규칙 (spec.md FR-014, FR-017; data-model.md Delegation Handoff; research.md Decision: 위임 확인 질문과 컨텍스트 전달 방식)
- [X] T015 [US2] `SKILL.md`에 "위임 실행" 섹션 작성 — 사용자가 동의하면 원래 설명 + Components & Dependencies의 컴포넌트·그룹·의존관계 + Responsibility의 책임 정보를 하나의 보강된 자연어 프로세스 설명으로 재구성하고, 이를 마치 사용자가 직접 입력한 것처럼 `generating-zenuml-diagrams`의 기존 워크플로(요청 분류부터 출력·피드백 로그까지)를 그대로 따라 실행하며, 그 스킬의 SKILL.md나 동작 자체는 수정하지 않는다는 제약을 명시. 이 실행 환경의 파일 저장 가용성(`available`)도 함께 전달해, 저장이 불가능한 환경이면 그 스킬 자신의 대체 동작(001의 FR-011 — 채팅에 DSL 텍스트 직접 제공)이 위임 실행에도 동일하게 적용되도록 한다 (spec.md FR-015, FR-018, FR-024; research.md Decision: 위임 확인 질문과 컨텍스트 전달 방식)
- [X] T016 [US2] `SKILL.md`에 "위임 거부/무응답" 규칙 작성 — 동의하지 않거나 응답이 애매하면 `generating-zenuml-diagrams`를 실행하지 않고, 재차 권유하지 않으며, 구조 뷰만으로 응답을 마친다는 규칙(목적 확인과 달리 애매하면 "실행하지 않음"이 기본값임을 명시) (spec.md FR-016; research.md Decision: 모호한 입력 처리; Edge Cases)
- [X] T017 [US2] `SKILL.md`의 Anti-Pattern 체크리스트에 AP-8(Runtime Flow 다이어그램을 스스로 그리지 않음 — 위임 대상 영역 침범 금지), AP-9(위임 확인을 했는지, 동의 없이 실행하지 않았는지)을 추가 (data-model.md Anti-Pattern Checklist; research.md Decision: 안티패턴 체크리스트 항목)
- [X] T018 [US2] `SKILL.md`에 위임 관련 예시 추가 — quickstart.md 시나리오 6(동의 → 시퀀스 다이어그램까지 제시)와 시나리오 7(거부 → 구조 뷰만으로 종료) 각각 1개씩

**Checkpoint**: User Story 1과 2가 함께 독립적으로 동작해야 함 — 사용자가 원할 때만 시퀀스 다이어그램까지 이어짐

---

## Phase 5: User Story 3 - 그룹/컴포넌트 규모를 처음부터 통제하기 (Priority: P3)

**Goal**: Responsibility 섹션의 비교 항목 폭증(그룹 내 n×(n-1)/2, 그룹 간 m×(m-1)/2)을 막기 위해, Components & Dependencies 단계에서부터 꼭 필요한 컴포넌트·그룹만 만든다.

**Independent Test**: quickstart.md 시나리오 8 — 설명에 없는 컴포넌트를 추가하지 않는지, 큰 그룹(8개 이상)에서 경고가 나오는지.

### Implementation for User Story 3

- [X] T019 [US3] `SKILL.md`에 "규모 통제" 섹션 작성 — 새로운 금지 규칙을 만들지 않고 T005가 이미 세운 "설명에 없는 컴포넌트·그룹을 추가하지 않는다"는 규칙(FR-004, FR-006)을 참조해 "이 규칙이 Responsibility 비교 항목 수(그룹 내 n×(n-1)/2, 그룹 간 m×(m-1)/2)의 폭증도 함께 막는다"는 연결고리만 명시하고, 하나의 그룹에 컴포넌트가 많아(예: 8개 이상, 28개 비교 항목) 결과가 길어질 것으로 예상되면 그 사실을 사용자에게 알리되 생성 자체는 거부하지 않는다는 새 규칙을 추가 (spec.md FR-011, FR-012; research.md Decision: 규모 통제)
- [X] T020 [US3] `SKILL.md`에 규모 경고 예시 추가 — quickstart.md 시나리오 8(그룹 내 컴포넌트 8개 → 28개 비교 항목 예상) 기준 경고 문구 예시

**Checkpoint**: 모든 User Story가 독립적으로 동작해야 함

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 skill의 품질 확인

- [X] T021 `SKILL.md` 본문 길이가 Anthropic 권장 기준(~500줄) 이내인지 확인하고, 초과 시 세부 내용을 `references/templates.md`로 이동
- [X] T022 [P] `.claude/skills/generating-architecture-views/references/examples.md` 작성 — 완성된 구조 뷰 예시 2~3개 이상(온보딩 목적 1개, 특정 문제 진단 목적 1개, 그룹 3개 이상인 예시 1개, 위임 동의로 시퀀스 다이어그램까지 이어진 예시 1개)
- [X] T023 `SKILL.md`의 YAML `description` 필드가 3인칭 서술이며, `generating-zenuml-diagrams`(시퀀스/행동)와 트리거가 겹치지 않게 "구조/아키텍처" 키워드를 명확히 구분하는지 검토
- [X] T024 `quickstart.md`의 시나리오 1~11을 완성된 skill에 대해 실행하고, 통과/실패를 기록 (SC-001~SC-008, SC-003b 커버, 시나리오 11이 SC-008 담당)

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
- **User Story 2 (P2)**: Foundational 이후 시작 가능 — US1이 만든 구조 뷰(Components & Dependencies, Responsibility)의 내용을 위임 컨텍스트로 사용하지만, "구조 뷰가 있다"는 전제만 필요할 뿐 US1의 SKILL.md 섹션을 수정하지는 않으므로 독립적으로 테스트 가능
- **User Story 3 (P3)**: Foundational 이후 시작 가능 — US1의 Components & Dependencies 생성 규칙에 제약을 추가하는 별도 섹션이라 독립적으로 테스트 가능

### Within Each User Story

- 같은 파일(`SKILL.md`)을 편집하는 태스크는 충돌 방지를 위해 순차 진행
- 스토리 완료 후 다음 우선순위로 이동

### Parallel Opportunities

- Phase 2의 T002, T003은 서로 다른 파일이므로 병렬 실행 가능
- Phase 6의 T022는 새 파일(`references/examples.md`)이라 T021/T023과 병렬 실행 가능하지만, T021과 T023은 둘 다 `SKILL.md`를 다루므로 순차 진행
- User Story 3개는 모두 `SKILL.md`의 서로 다른 섹션을 추가하는 작업이라 논리적으로는 독립적이지만, 파일 충돌을 피하려면 한 번에 한 스토리씩 진행하는 것을 권장

---

## Parallel Example: Phase 2 (Foundational)

```bash
# T002와 T003은 서로 다른 파일을 다루므로 함께 실행 가능:
Task: "SKILL.md 뼈대(frontmatter + 섹션 헤딩) 작성"
Task: "references/templates.md에 Components & Dependencies, Responsibility 템플릿 작성"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료 (SKILL.md 뼈대 + 섹션 템플릿) — 모든 스토리의 전제조건
3. Phase 3: User Story 1 완료
4. **STOP and VALIDATE**: quickstart.md 시나리오 1~5로 User Story 1을 독립적으로 검증
5. 이 시점에서 이미 "설명에 근거한 구조 + 명확한 책임 구분(그룹 내부와 그룹 간 모두)"이라는 핵심 가치를 제공하는 MVP가 완성됨(시퀀스 다이어그램 위임 없이도 완결된 산출물)

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

---

## Phase 7: Convergence

**Purpose**: `/speckit-converge`가 실제 구현(`SKILL.md`) 대 spec.md/data-model.md를 대조해 발견한, 구현 자체의 내부 불일치를 바로잡는다.

- [X] T025 `SKILL.md`의 "Workflow overview" 4번 항목("Self-check (AP-1–AP-6)")과 자기검증 섹션의 "Workflow: generate a draft → check it against AP-1 through AP-6" 문장을 "AP-1 through AP-7"로 수정 — 바로 위 체크리스트(AP-1~AP-7)에 이미 존재하는 AP-7(FR-013: 일반 개념 비교 섹션 금지 검사)이 이 요약 문구 때문에 실행 시 누락될 위험이 있음 per FR-019, FR-013 (contradicts)
- [X] T026 `SKILL.md`의 "Workflow overview" 7번 항목의 "(AP-7–AP-8)"을 "(AP-8–AP-9)"로 수정 — 실제 위임(hand-off) 체크리스트는 AP-8, AP-9이므로 번호가 어긋나 있음 per FR-019, FR-016 (contradicts)
- [X] T027 `SKILL.md`의 "Out-of-scope requests" 항목 중 "non-Context/Dependency/Responsibility structural view"를 "non-Components & Dependencies/Responsibility structural view"로 수정 — 이 섹션 이름은 이미 저장소 전체에서 "Components & Dependencies"로 통일되었는데 이 한 곳만 예전 이름("Context/Dependency")이 남아 있음 per spec.md Clarifications(명명 결정) (contradicts)

---

## Phase 8: Convergence

**Purpose**: `/speckit-converge`가 실제 산출물(`.zenuml/*.architecture.md`) 대 `SKILL.md`/`references/templates.md`의 자체 관행을 대조해 발견한, 규칙 누락으로 인한 품질 저하를 바로잡는다.

- [X] T028 `SKILL.md` Step 3(Responsibility 생성 규칙)과 Self-check 체크리스트에 "각 Responsibility 항목(그룹 간/그룹 내 모두)은 앞서 나온 항목을 참조("위와 동일" 등)하지 않고 양쪽의 책임을 매번 완전히·독립적으로 새로 서술해야 하며, 목록이 길어져도 뒤쪽 항목이 앞쪽보다 부실해져서는 안 된다"는 규칙을 명시적으로 추가 — `SKILL.md`/`references/templates.md`/`references/examples.md`의 모든 예시는 이미 이 관행(항목마다 완전히 독립적으로 서술)을 따르는데 이를 강제하는 규칙 자체가 없어서, 실제 산출물 `.zenuml/android-nav3-migration-before.architecture.md`의 `#### app 모듈` 섹션(10개 중 7개가 "MainActivity는 위와 동일" 식 backreference를 사용했고 목록 뒤로 갈수록 항목이 눈에 띄게 짧고 뻔해짐)에서 이 관행이 깨짐 per FR-009, 기존 예시들의 서술 관행 (missing)

---

## Phase 9: Convergence

**Purpose**: `/speckit-converge`가 `/speckit-clarify`로 개정된 FR-026(그룹 간 비교의 근거 범위) 대 `SKILL.md`/`references/templates.md`의 실제 규칙 문구를 대조해 발견한, 스펙-구현 간 불일치를 바로잡는다.

- [X] T029 `SKILL.md` Step 3의 그룹 레벨 규칙("Each entry's 'responsibility' for a group is the name/label the description actually gave it... comparing two groups means contrasting their given labels, nothing more")과 Self-check 체크리스트의 AP-5("each is based only on the groups' given labels")를 개정된 FR-026("그룹 이름/레이블은 항상 근거로 삼되, 설명이 그 그룹에 대해 레이블을 넘어서는 내용을 실제로 언급했다면 그것도 근거로 사용해야 한다 — 추측/발명은 여전히 금지")에 맞춰 수정 — 컴포넌트 책임(FR-009/FR-010)과 동일한 "설명에 있으면 쓰고 없으면 지어내지 않는다" 원칙을 그룹에도 적용하도록 갱신 per FR-026 (contradicts)
- [X] T030 `references/templates.md`의 "Group-to-group comparisons" 절("The 'responsibility' of a group is the name/label the description actually gave it — never an inferred summary of what its member components do")을 개정된 FR-026에 맞춰 수정 — 레이블은 항상 근거로 삼되, 설명이 그룹에 대해 실제로 언급한 추가 내용이 있으면 그것도 근거로 사용 가능하다는 점을 명시(추측/발명 금지는 유지) per FR-026 (contradicts)

---

## Phase 10: Convergence

**Purpose**: `/speckit-converge`가 `/speckit-clarify`로 개정된 FR-008(그룹 내 이항대립 비교를 직접 의존관계 쌍으로 한정) 대 `SKILL.md`/`references/templates.md`/`references/examples.md`의 실제 규칙·예시 문구를 대조해 발견한, 스펙-구현 간 불일치를 바로잡는다.

- [X] T031 `SKILL.md` Step 3의 컴포넌트 레벨 규칙("compare every unordered pair of components — regardless of whether they call each other... A group of n components gets exactly n×(n-1)/2 entries")과 Self-check 체크리스트의 AP-4("Each group's within-group Responsibility list has exactly n×(n-1)/2 entries")를 개정된 FR-008("그룹 내에서 서로 직접 의존관계로 연결된 쌍만 비교하며, 항목 수는 그룹 내 실제 의존관계 엣지 수와 일치")에 맞춰 재작성 per FR-008 (contradicts)
- [X] T032 `SKILL.md`의 "Example: request with a group"(PaymentService vs InventoryService 비의존 쌍을 포함하며 "두 그룹이 같은 그룹이라 포함된다"고 설명)과 "Example: request with 3+ groups"(UserService vs AuthService, PaymentService vs InventoryService 비의존 쌍 포함)에서 비의존 쌍 항목을 제거하고, 설명 문구를 개정된 FR-008에 맞춰 "비의존 쌍은 항목이 생성되지 않는다"로 정정 per FR-008, US1/AC1 (contradicts)
- [X] T033 `SKILL.md`의 "Scale control" 섹션("entry count grows with the square of group size", "8 or more components in one group means 28 or more entries")을 "그룹이 완전 연결(모든 쌍이 서로 호출)인 경우의 최댓값"이라는 조건으로 정정 per FR-008 (contradicts)
- [X] T034 `references/templates.md`의 "Within-group comparisons" 절("Never add more or fewer entries than n×(n-1)/2 for a given group of size n")과 53행의 쌍 생성 설명("this naturally produces exactly n×(n-1)/2 entries... whether n counts groups or components")을 개정된 FR-008에 맞춰 재작성 — 그룹 레벨(m×(m-1)/2)은 영향 없으므로 그대로 두고 컴포넌트 레벨만 "직접 의존관계로 연결된 쌍만" 규칙으로 수정 per FR-008 (contradicts)
- [X] T035 `references/examples.md`의 Example 2(AuthService/TokenValidator/SessionStore — TokenValidator vs SessionStore 비의존 쌍을 포함하며 "정직하게 포함한다"고 설명)와 Example 3(three-domains — UserService vs AuthService, PaymentService vs InventoryService 비의존 쌍 포함)에서 비의존 쌍 항목을 제거하고 설명 문구를 정정(사용자 도메인 그룹은 내부 의존관계가 없으므로 비교 항목이 0개가 됨을 명시) per FR-008 (contradicts)

---

## Phase 11: Convergence

**Purpose**: `/speckit-converge`가 `/speckit-clarify`로 개정된 FR-025(그룹 간 비교를 의존관계 있는 쌍으로 한정)와 FR-027(신규 — 항목 서식: 볼드, 실제 방향/상호 의존, 마침표) 대 `SKILL.md`/`references/templates.md`/`references/examples.md`의 실제 규칙·예시 문구를 대조해 발견한, 스펙-구현 간 불일치를 바로잡는다.

- [X] T036 `SKILL.md` Step 3의 그룹 레벨 규칙("compare every unordered pair of groups against each other. m groups gets exactly m×(m-1)/2 entries")과 Self-check 체크리스트의 AP-5를 개정된 FR-025("그룹 간에 실제 의존관계가 있는 쌍만 비교, 의존관계 없는 쌍은 항목 없음")에 맞춰 재작성 per FR-025 (contradicts)
- [X] T037 `SKILL.md` Step 3의 항목 서식 규칙과 Self-check을, 개정된 FR-027("**A**는 **B**에 의존한다" 볼드+실제 방향 서술, 양방향이면 "**A**와 **B**는 서로 의존한다", 세미콜론 대신 마침표)에 맞춰 재작성 — 그룹/컴포넌트 레벨 모두 적용 per FR-027 (contradicts)
- [X] T038 `SKILL.md`의 worked example 3개(minimal request, request with a group, request with 3+ groups)를 새 서식(볼드+방향/상호 의존+마침표)과 그룹 간 의존관계 기준 비교로 재작성 — 특히 "request with 3+ groups" 예시는 그룹 쌍 중 의존관계 없는 쌍(예: 사용자 도메인-알림 도메인)의 그룹 간 비교 항목이 사라짐을 반영 per FR-025, FR-027 (contradicts)
- [X] T039 `references/templates.md`의 Responsibility 템플릿 모양, "Group-to-group comparisons" 절, "Within-group comparisons" 절을 개정된 FR-025/FR-027에 맞춰 재작성 — 그룹 간 비교도 의존관계 게이팅 적용, 항목 서식도 볼드+방향/상호 의존+마침표로 변경 per FR-025, FR-027 (contradicts)
- [X] T040 `references/examples.md`의 Example 1~4를 전부 개정된 FR-025/FR-027에 맞춰 재작성(서식 변경 + Example 3의 그룹 간 비교를 의존관계 기준으로 축소) per FR-025, FR-027 (contradicts)

---

## Phase 12: Convergence

**Purpose**: `/speckit-converge`가 `SKILL.md` 내부의 잔여 불일치 — "Scale control" 섹션이 개정된 FR-025(그룹 간 비교의 의존관계 게이팅)를 반영하지 않고 이전(무조건 m×(m-1)/2) 버전 문구를 그대로 남긴 것 — 를 바로잡는다.

- [X] T041 `SKILL.md`의 "Scale control" 섹션(241행 부근) 중 "The group level always grows with the square of group count (m×(m-1)/2)." 문장을, 같은 파일 Step 3(50행)·Self-check AP-5(72행)·`references/templates.md`(82행)가 이미 반영한 개정된 FR-025("그룹 간 비교는 실제 연결된 그룹 쌍 수만큼만 생성되며, 모든 그룹 쌍이 서로 연결된 경우에만 m×(m-1)/2가 상한")에 맞춰, 바로 다음 문장의 컴포넌트 레벨 서술과 동일한 어조로 재작성 per FR-025 (contradicts)

---

## Phase 13: Convergence

**Purpose**: `/speckit-converge`가 이 기능의 유일한 수동 검증 자산인 `quickstart.md`를, 2026-08-01 세션에서 개정된 FR-008/FR-025/FR-027 및 그 개정을 이미 반영한 `SKILL.md`/`references/*.md`와 대조해 발견한, 검증 시나리오 자체의 구식 기대값을 바로잡는다.

- [X] T042 `quickstart.md`의 "시나리오 3"(30~38행) 기대 결과·검증 문구 중 "Responsibility 섹션에 정확히 3×2/2=3개의 그룹 내 비교 항목(... PaymentService-InventoryService ...)이 있다 — 마지막 쌍은 서로 직접 호출하지 않지만 같은 그룹이므로 비교 대상에 포함되어야 한다"를, 개정된 FR-008(그룹 내에서 직접 의존관계로 연결된 쌍만 비교)에 맞춰 "PaymentService-InventoryService는 서로 호출하지 않으므로 비교 항목이 생성되지 않고, 정확히 2개(OrderService-PaymentService, OrderService-InventoryService)만 존재한다"로 정정하고, 검증 문구도 "비의존 쌍이 포함되면 실패"로 뒤집는다 — 현재 `SKILL.md`/`references/examples.md`의 동일 입력 예시가 이미 이렇게 동작하므로, 고치지 않으면 이 시나리오로 재검증할 때 올바른 현재 동작을 실패로 오판하게 됨 per US1/AC1, FR-008 (contradicts)
- [X] T043 `quickstart.md`의 "시나리오 4"(40~50행) 기대 결과·검증 문구 중 "그룹 간 비교가... 3×2/2=3개(사용자-주문, 사용자-알림, 주문-알림)", "그룹별 컴포넌트 간 비교가... 사용자 도메인 1개, 주문 도메인 3개, 알림 도메인 3개, 총 7개", "그룹 간 비교 항목 수가 정확히 m(m-1)/2(=3)"를, 개정된 FR-025(그룹 간에도 실제 교차-그룹 의존관계가 있는 쌍만 비교)에 맞춰 "그룹 간 비교는 실제 연결된 2쌍(사용자 도메인↔주문 도메인, 주문 도메인↔알림 도메인)만 생성되고 사용자 도메인↔알림 도메인은 연결이 없어 생성되지 않으며, 그룹별 컴포넌트 비교 총합은 0(사용자 도메인)+2(주문 도메인)+0(알림 도메인)=2개"로 정정하고, "사용자 도메인 vs 주문 도메인" 서식 예시를 FR-027에 맞춰 "**주문 도메인**는 **사용자 도메인**에 의존한다" 형태로 바꾼다 — 현재 `SKILL.md`의 동일 입력 예시가 이미 이렇게 동작하므로, 고치지 않으면 이 시나리오로 재검증할 때 올바른 현재 동작을 실패로 오판하게 됨 per SC-003b, FR-025, FR-027 (contradicts)
- [X] T044 `quickstart.md`의 "시나리오 2"(25행) 괄호 설명 "(OrderService vs PaymentService)"를, FR-027 개정 이후 이 스킬 전체가 사용하는 볼드+실제 의존 방향 서식에 맞춰 "(**OrderService**는 **PaymentService**에 의존한다)"로 정정해 문서 전체의 서식 표기를 일관되게 유지 per FR-027 (contradicts)

---

## Phase 14: Convergence

**Purpose**: `/speckit-converge`가 사용자의 직접 질의("의존성 그래프가 간접 의존까지 표시하는가?")를 계기로 재점검해 발견한, Components & Dependencies의 의존관계 포함 규칙이 다단계 호출 체인을 하나의 간접 화살표로 압축하는 것을 명시적으로 막지 않는 문제를 바로잡는다.

- [X] T045 `SKILL.md` Step 2("Generate Components & Dependencies")의 의존관계 규칙과 Self-check AP-2에, "두 컴포넌트 사이에 설명이 직접 명시하거나 명확히 함의한 호출만 화살표로 그리며, A가 B를 호출하고 B가 C를 호출한다고만 설명된 경우 A→C처럼 여러 홉을 거치는 체인을 하나의 간접 화살표로 합쳐서 그리지 않는다"는 규칙을 명시적으로 추가하고, `references/templates.md`의 Components & Dependencies 템플릿 절에도 동일한 제약을 한 줄로 반영 — FR-004("설명에 없는 내용을 임의로 추가해서는 안 된다")가 이미 원론적으로 요구하는 것이지만 이 구체적 실패 패턴(다단계 체인의 간접 압축)을 SKILL.md의 운영 규칙이 명시적으로 방어하지 않고 있음 per FR-004, FR-006, FR-007 (partial)

---

## Phase 15: Convergence

**Purpose**: `/speckit-converge`가 `/speckit-clarify`로 개정된 FR-009/FR-010("차이" 요약 절 제거) 대 `SKILL.md`/`references/templates.md`/`references/examples.md`/`quickstart.md`의 실제 규칙·예시·검증 문구를 대조해 발견한, 스펙-구현 간 불일치를 바로잡는다.

- [X] T046 `SKILL.md` Step 3의 Format 규칙(58행 부근)과 모든 worked example(minimal request, request with a group, request with 3+ groups)에서 각 항목 끝의 "차이: <대조>" 절을 제거 — 개정된 FR-009("두 책임/레이블을 요약하는 별도의 '차이' 문장을 덧붙여서는 안 된다")에 맞춰, 항목은 "**A**는 **B**에 의존한다: A는 <책임>. B는 <책임>."으로 끝나야 함 per FR-009, FR-010 (contradicts)
- [X] T047 `references/templates.md`의 Responsibility 템플릿 모양(그룹 간/그룹 내 예시)과 "Within-group comparisons" 절의 "차이" 관련 서술("don't guess a '차이' for that entry — write `차이: 명시되지 않음`")을 개정된 FR-009에 맞춰 제거 — 항목은 두 책임/레이블만 담고 끝남 per FR-009 (contradicts)
- [X] T048 `references/examples.md`의 Example 1~3 전체 항목에서 "차이: ..." 절을 제거하고, 각 항목이 두 책임/레이블 서술로 끝나도록 재작성 per FR-009 (contradicts)
- [X] T049 `quickstart.md`의 시나리오 2(26행 "근거 없는 차이 서술이 등장하지 않는다")와 시나리오 5(52행 제목 "근거 없는 책임/차이를 지어내지 않음", 56행 "차이를 추측해서 채우지 않는다")를 개정된 FR-009/FR-010에 맞춰 "차이" 대신 "책임"을 지어내지 않는지 검증하는 문구로 정정 — 88행의 "Controller와 Handler의 차이" 언급은 Responsibility 서식과 무관한 별개 시나리오(범위 밖 일반 개념 비교)이므로 손대지 않음 per FR-009, FR-010 (contradicts)

---

## Phase 16: Convergence

**Purpose**: `/speckit-converge`가 `/speckit-clarify`로 신규 추가된 FR-028~031(구조 뷰 피드백 로그, `generating-zenuml-diagrams`의 002 메커니즘 이식) 대 `SKILL.md`의 실제 규칙을 대조해 발견한, 아예 존재하지 않는 로그 메커니즘을 새로 추가한다.

- [X] T050 `SKILL.md`의 "Output file" 섹션 뒤에 "Feedback log" 절을 신설 — `generating-zenuml-diagrams`의 SKILL.md "Diagram feedback log" 절과 동일한 구조로: (1) 구조 뷰가 처음 성공적으로 생성될 때 `.zenuml/log/<slug>.architecture.md`를 만들고 최초 요청+응답(생성된 구조 뷰)을 `## Round 1 — <ISO date>`로 기록, (2) FR-021 재생성 분류에 따라 재생성되면 산출물(`.zenuml/<slug>.architecture.md`)은 완전히 교체하되 로그는 기존 라운드를 지우지 않고 `## Round N`으로 새 라운드를 이어붙임, (3) 로그 내용을 자동 요약·분석하지 않으며 이후 다른 Spec Kit 작업이 실제로 인용할 때만 `git add -f`로 그 로그 파일 하나만 선별 스테이징(`.zenuml/log/`는 이미 002를 위해 gitignore 처리되어 있어 추가 설정 불필요), (4) 구조 뷰 생성 자체가 완료되지 않으면(질문으로 끝나는 등) 산출물도 로그도 만들지 않음 per FR-028, FR-029, FR-030, FR-031 (missing)
- [X] T051 `SKILL.md`의 Workflow overview(5번 항목 "Save the architecture view file and present it")와 Self-check 체크리스트에 로그 파일 생성/라운드 추가가 누락되지 않았는지 확인하는 항목(AP-12: 최초 생성 시 로그 Round 1이 만들어졌는지, 재생성 시 기존 라운드를 지우지 않고 새 라운드가 추가됐는지)을 추가 per FR-028, FR-029 (missing)

---

## Phase 17: Convergence

**Purpose**: `/speckit-converge`가 신규 SC-009(구조 뷰 피드백 로그)에 대응하는 검증 시나리오가 `quickstart.md`에 하나도 없음을 발견해 바로잡는다.

- [X] T052 `quickstart.md`에 "시나리오 12 — 구조 뷰 피드백 로그 (SC-009)"를 추가 — (a) 시나리오 2와 동일한 최초 생성 요청 후 `.zenuml/log/order-payment.architecture.md`가 `## Round 1 — <ISO date>`로 최초 요청+응답을 담아 함께 만들어지는지, (b) 이어서 같은 구조 뷰에 변경을 요청(예: 컴포넌트 하나 추가)했을 때 산출물(`.zenuml/order-payment.architecture.md`)은 새 내용으로 완전히 교체되고 로그에는 Round 1이 지워지지 않은 채 `## Round 2`가 새로 추가되는지 검증하는 절차를 시나리오 1~11과 동일한 형식(입력 예시/기대 결과/검증)으로 작성 per SC-009, FR-028, FR-029 (missing)
