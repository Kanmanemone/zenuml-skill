# Tasks: 다이어그램별 개선 이력 로깅

**Input**: Design documents from `/specs/002-diagram-feedback-log/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/feedback-interface.md, quickstart.md

**Tests**: spec.md에 테스트를 명시적으로 요청하지 않았고 이 기능은 실행 코드가 없는 Markdown 기반 skill 확장이므로, 별도 자동화 테스트 태스크는 생성하지 않는다. 대신 `quickstart.md`의 수동 검증 시나리오를 Polish 단계 태스크로 포함한다(feature 001과 동일한 방식).

**Organization**: 태스크는 spec.md의 User Story(P1/P1/P2/P3)별로 그룹화되어 있다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 이 태스크가 속한 user story (US1, US2, US3, US4)
- 모든 태스크에 정확한 파일 경로를 포함한다

## Path Conventions

이 기능은 새 skill이 아니라 기존 Claude Code Skill 번들 확장이다(plan.md, Project Structure 참고). 유일한 소스 파일은:

- `.claude/skills/generating-zenuml-diagrams/SKILL.md`

`.zenuml/<slug>.md`(다이어그램 산출물, feature 001이 이미 만듦)와 `.zenuml/log/<slug>.md`(신규 — 이력 로그)는 런타임에 생성되는 산출물이며, 소스 코드가 아니므로 태스크 대상이 아니다. 둘 다 기존 `.zenuml/` gitignore 규칙이 커버해 새 gitignore 항목은 필요 없다.

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: 다이어그램을 만들거나 파일을 건드리기 전에 항상 가장 먼저 수행되는 "요청 종류 판단" 절차를 `SKILL.md`에 추가한다 — 사용자가 이번 계획에서 최우선으로 요구한 지점이다.

**⚠️ CRITICAL**: 이 단계가 끝나기 전에는 어떤 User Story 작업도 시작할 수 없음. 이 판단이 워크플로 맨 앞에 오지 않으면 재생성/최초 생성이 뒤섞여 잘못된 파일을 덮어쓰는 되돌리기 어려운 사고로 이어질 수 있다.

- [X] T001 `.claude/skills/generating-zenuml-diagrams/SKILL.md`의 기존 생성 워크플로 **맨 앞**에 "요청 종류 판단" 절을 추가 — 다이어그램을 만들거나 어떤 파일도 건드리기 전에, (1) 이번 요청이 이번 대화에서 방금 제시한 다이어그램에 대한 변경 요청인지(→ 재생성), (2) 도출된 slug의 산출물 파일이 아직 없는지(→ 최초 생성), (3) 산출물 파일이 이미 있지만 이번 요청과는 무관한지(→ slug 충돌로 인한 새 요청, 기존 `-2`/`-3` 규칙 적용 후 최초 생성으로 취급)를 순서대로 판정하는 규칙을 명시. 판정이 애매하면 추측하지 않고 feature 001의 기존 "명확화 질문" 패턴을 재사용해 되묻는다는 규칙도 포함 (spec.md FR-002, Edge Cases; data-model.md 요청 분류; research.md Decision: 요청 종류 판단 절차; contracts/feedback-interface.md 0단계)

**Checkpoint**: 이 지점부터 User Story별 작업을 시작할 수 있음

---

## Phase 2: User Story 1 - 다이어그램을 처음 생성하면 산출물과 이력이 함께 남는다 (Priority: P1) 🎯 MVP

**Goal**: 다이어그램이 처음 생성되면(T001의 판정 결과가 "최초 생성"), 기존 `.zenuml/<slug>.md`뿐 아니라 `.zenuml/log/<slug>.md`도 함께 만들어 최초 요청과 응답을 Round 1로 기록한다.

**Independent Test**: 다이어그램을 새로 요청한다. `.zenuml/<slug>.md`(다이어그램만)와 `.zenuml/log/<slug>.md`(최초 요청 원문 + 응답, `## Round 1`)가 둘 다 만들어졌는지 확인한다 (quickstart.md 시나리오 1).

### Implementation for User Story 1

- [X] T002 [US1] `SKILL.md`의 기존 "Output file" 절 바로 뒤에 "다이어그램 피드백 로그 생성" 절 추가 — T001의 판정이 "최초 생성"(또는 "slug 충돌로 인한 새 요청")일 때, 기존 `.zenuml/<slug>.md` 생성과 함께 `.zenuml/log/<slug>.md`를 새로 만들어 `## Round 1`로 최초 요청 원문과 응답(생성된 ZenUML 코드펜스 포함)을 기록하는 규칙을 명시. 이 로그는 사람이 직접 훑어보기 위한 것이며 skill이 내용을 자동 요약하거나 패턴을 자동 탐지해서는 안 된다는 점도 함께 명시 (spec.md FR-001, FR-008; data-model.md 다이어그램 피드백 로그, 교정 라운드; research.md Decision: 로그 파일 위치; contracts/feedback-interface.md Output Contract — 최초 생성)

**Checkpoint**: User Story 1이 독립적으로 완전히 동작하고 테스트 가능해야 함 — 최초 생성 시 두 파일이 함께 생김

---

## Phase 3: User Story 2 - 재생성을 요청하면 산출물은 교체되고 이력은 누적된다 (Priority: P1)

**Goal**: T001의 판정이 "재생성"일 때, `.zenuml/<slug>.md`는 새 내용으로 완전히 교체하고 `.zenuml/log/<slug>.md`에는 이번 라운드를 이어붙인다.

**Independent Test**: User Story 1로 만들어진 다이어그램에 변경을 요청한다. `.zenuml/<slug>.md`가 새 다이어그램 하나만 담고 있고(이전 내용은 사라짐), `.zenuml/log/<slug>.md`에는 최초 라운드와 이번 라운드가 모두 남아 있는지 확인한다 (quickstart.md 시나리오 2).

### Implementation for User Story 2

- [X] T003 [US2] `SKILL.md`에 "재생성 처리" 절 추가 — T001의 판정이 "재생성"일 때, 전달된 요청을 반영해 다이어그램을 재생성하되 기존 생성 규칙과 안티패턴 자기검증(AP-1~AP-5)을 동일하게 적용하고, `.zenuml/<slug>.md`를 새 내용으로 **완전히 교체**(이전 내용 미보존)하며, `.zenuml/log/<slug>.md`에는 기존 라운드를 그대로 둔 채 새 `## Round N — <날짜>` 절(이번 요청 원문 + 응답)을 이어붙이는 규칙을 명시 (spec.md FR-002, FR-003, FR-004; data-model.md 다이어그램 산출물, 교정 라운드; research.md Decision: 다이어그램 산출물은 전체 교체, 로그는 append; contracts/feedback-interface.md Output Contract — 재생성)

**Checkpoint**: User Story 1과 2가 함께 독립적으로 동작해야 함 — 최초 생성과 재생성 두 경로가 모두 올바르게 분기됨

---

## Phase 4: User Story 3 - 같은 다이어그램에 여러 번 이어지는 교정을 모두 보존한다 (Priority: P2)

**Goal**: 재생성이 여러 차례 이어져도 `.zenuml/log/<slug>.md`에는 모든 라운드가 순서대로 남고, `.zenuml/<slug>.md`는 항상 최신 상태만 담는다.

**Independent Test**: 동일 다이어그램에 재생성 요청을 연속 두 번 보낸다. `.zenuml/<slug>.md`는 세 번째(최신) 버전만 담고, `.zenuml/log/<slug>.md`에는 최초·1차·2차 라운드가 모두 순서대로 남아 있는지 확인한다 (quickstart.md 시나리오 3 관련 확장, 연속 재생성).

### Implementation for User Story 3

- [X] T004 [US3] `SKILL.md`의 "재생성 처리" 절(T003)에 라운드 반복에 대한 명시적 확인 문구 추가 — 재생성이 몇 차례 이어지든 T003의 append 규칙이 매번 동일하게 적용되어 기존 라운드가 절대 수정·삭제되지 않으며, 재생성 후에도 다시 T001의 판단 절차로 돌아가 다음 요청을 새로 판정한다는 점을 명시 (spec.md FR-004, User Story 3; contracts/feedback-interface.md Output Contract — 재생성)

**Checkpoint**: User Story 1~3이 모두 함께 독립적으로 동작해야 함 — 여러 라운드가 로그에 누적되고 산출물은 항상 최신만 유지됨

---

## Phase 5: User Story 4 - 실제로 인용된 로그만 선별적으로 버전관리에 편입한다 (Priority: P3)

**Goal**: 어떤 작업이 특정 다이어그램 피드백 로그를 실제로 인용하는 순간, 그 로그 파일 하나만 버전관리에 편입되고 나머지(산출물 파일 포함)는 그대로 남는다.

**Independent Test**: 누적된 `.zenuml/log/<slug>.md` 중 하나를 인용한다고 가정하고 `git add -f`를 실행한다. 그 로그 파일만 스테이징 상태로 바뀌고 산출물 파일이나 다른 로그 파일은 여전히 미스테이징 상태인지 확인한다 (quickstart.md 시나리오 4).

### Implementation for User Story 4

- [X] T005 [US4] `SKILL.md`에 "교정 이력 인용 시 스테이징" 절 추가 — 어떤 작업이 `.zenuml/log/` 아래 특정 로그 파일을 실제로 읽고 근거로 인용하기로 결정한 순간 `git add -f <그 로그 파일 경로>`로 그 파일 하나만 강제 스테이징하는 컨벤션을 명시하고, 다이어그램 산출물(`.zenuml/<slug>.md`)은 재생성마다 교체되어 이력 가치가 없으므로 이 컨벤션의 대상이 아니라는 점, 그리고 이 skill이 다른 Spec Kit 스킬 파일을 호출하거나 수정하지 않는다는 점도 함께 명시 (spec.md FR-006, FR-007; research.md Decision: 인용 시 선별적 스테이징; data-model.md 인용 스테이징 컨벤션; contracts/feedback-interface.md 인용 시 스테이징 Contract)

**Checkpoint**: 모든 User Story가 독립적으로 동작해야 함

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 확장의 품질 확인

- [X] T006 `SKILL.md` 본문 길이가 Anthropic 권장 기준(~500줄) 이내인지 확인하고, 초과 시 이번에 추가한 절 중 상세 내용을 `references/`로 분리할지 검토
- [X] T007 `quickstart.md`의 시나리오 0(요청 종류 판단, 0-A~0-D)부터 시나리오 5까지 완성된 확장에 대해 실행하고, 통과/실패를 기록 (SC-001~SC-005 커버, 특히 시나리오 0은 다른 모든 시나리오의 전제조건이므로 우선 검증)

---

## Phase 7: Convergence

- [X] T008 `.claude/skills/generating-zenuml-diagrams/SKILL.md`의 "Diagram feedback log" 절에 있는 Round 1과 Round N 템플릿 둘 다에서 `**Request**:` 줄과 `**Response**:` 줄 사이에 빈 줄을 추가 — 현재는 빈 줄이 없어 CommonMark 기준 같은 문단으로 렌더링되어 실제 생성된 로그 파일에서 두 줄이 붙어 보이는 문제가 실사용 중 확인됨 per FR-008 (partial)

---

## Phase 8: Convergence

- [X] T009 `.claude/skills/generating-zenuml-diagrams/SKILL.md`의 "Diagram feedback log" 절에서 Round 1/Round N 템플릿의 `**Request**:` 필드 설명(`<the user's request, verbatim or lightly summarized>` / `<this round's request>`)을 명확화 — 직전 라운드(또는 최초 요청) 이후 이번 라운드의 다이어그램 구성에 실제로 기여한 모든 턴(사용자의 명확화 질문에 대한 답변 등 포함)을 모아, ZenUML 생성과 무관한 내용은 제외하고 간결하게 정리해서 담으라는 규칙을 명시. 실사용 중 이 동작이 실제로 필요함이 확인됐으나(예: 명확화 질문→답변을 거쳐 생성된 다이어그램의 경우) SKILL.md 문구가 이를 명시하지 않아 에이전트의 그때그때 판단에 의존하고 있었음 per FR-001, FR-004 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: 의존성 없음 — 즉시 시작 가능. 모든 User Story를 블로킹함
- **User Stories (Phase 2~5)**: 모두 Foundational(T001, 요청 종류 판단) 완료에 의존
  - US1은 Foundational 이후 바로 시작 가능 — 다른 스토리에 의존하지 않음
  - US2는 T001의 "재생성" 분기를 다루므로 Foundational 이후 시작 가능하지만, 실제 검증에는 US1이 만든 다이어그램이 필요함
  - US3은 US2(T003의 append 규칙)에 문구를 더하는 것이므로 US2 이후 진행
  - US4는 인용할 로그 파일이 실제로 있어야 검증 가능하므로 US1 이후 진행 권장
- **Polish (Phase 6)**: 원하는 모든 User Story 완료에 의존

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 이후 시작 가능 — 다른 스토리에 의존하지 않음
- **User Story 2 (P1)**: Foundational 이후 시작 가능(T001의 판단 결과를 그대로 분기해서 쓰므로 문서 작성 자체는 US1과 독립적) — 다만 독립 테스트를 실행하려면 US1로 만든 산출물이 필요함
- **User Story 3 (P2)**: US2(T003) 완료 후 진행 — 같은 절에 문구를 추가하는 태스크이므로
- **User Story 4 (P3)**: Foundational 이후 시작 가능(문서 작성은 독립적) — 다만 독립 테스트에는 US1이 만든 로그 파일이 필요함

### Within Each User Story

- 모든 태스크가 같은 파일(`SKILL.md`)을 편집하므로 충돌 방지를 위해 순차 진행
- 스토리 완료 후 다음 우선순위로 이동

### Parallel Opportunities

- 이번 기능은 유일한 소스 파일이 `SKILL.md` 하나뿐이라 실질적인 [P] 병렬 실행 대상이 없다 — 모든 태스크를 순차로 진행한다
- Phase 6의 T006, T007은 서로 다른 관점(문서 길이 vs 시나리오 검증)이지만 T006이 SKILL.md를 수정할 수 있으므로 순차 진행 권장

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Foundational 완료(요청 종류 판단) — 모든 스토리의 전제조건이자 이번 계획의 최우선 요구사항
2. Phase 2: User Story 1 완료
3. **STOP and VALIDATE**: quickstart.md 시나리오 0(판단 정확도)과 시나리오 1로 User Story 1을 독립적으로 검증
4. 이 시점에서 이미 "요청을 정확히 분류하고, 최초 생성 시 산출물+이력을 함께 남긴다"는 핵심 가치를 제공하는 MVP가 완성됨

### Incremental Delivery

1. Foundational 완료(요청 종류 판단) → 기반 준비 완료 — 이 판단이 틀리면 이후 무엇을 더해도 신뢰할 수 없으므로 가장 먼저 꼼꼼히 검증
2. User Story 1 추가(최초 생성) → 독립 검증 → MVP 완성
3. User Story 2 추가(재생성 시 교체+누적) → 독립 검증 → 핵심 가치(산출물/이력 분리) 완성
4. User Story 3 추가(다중 라운드) → 독립 검증 → 반복 교정 이력 완성
5. User Story 4 추가(선별적 스테이징) → 독립 검증 → 장기 목표(재료로 재사용) 완성
6. Polish(Phase 6) → 문서 길이·quickstart 전체 재검증

---

## Notes

- [Story] 라벨은 태스크를 특정 user story로 추적하기 위함
- 각 user story는 독립적으로 완료·테스트 가능해야 함
- 이 기능은 실행 코드가 없으므로 "테스트 실패 확인" 절차 대신 quickstart.md 시나리오 수동 검증으로 대체함
- 모든 태스크가 `SKILL.md` 하나를 편집하므로 [P] 병렬 태스크가 없다 — 논리적 작업 단위(태스크)마다 커밋 권장
- 체크포인트마다 멈춰서 해당 스토리를 독립적으로 검증할 것
- 피할 것: 모호한 태스크, 동일 파일(`SKILL.md`) 동시 편집 충돌, 스토리 간 독립성을 깨는 교차 의존
- **이전 판과의 차이**: 확인 질문/선택 UI(AskUserQuestion, 하드코딩 텍스트 메뉴)를 전부 없애고, 대신 "요청 종류 판단"을 워크플로 맨 앞의 명시적 Foundational 단계로 승격했다. 저장 구조도 다시 두 파일로 분리했다 — 산출물(`.zenuml/<slug>.md`, 재생성마다 교체)과 로그(`.zenuml/log/<slug>.md`, 계속 누적). 자세한 배경은 research.md 개정 이력 참고.
