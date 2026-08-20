# Tasks: Markdown 다이어그램/PDF export 스킬

**Input**: Design documents from `/specs/004-exporting-markdown-diagrams/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-interface.md, quickstart.md

**Tests**: spec.md가 자동화 테스트를 명시적으로 요구하지 않으므로, 검증은 `quickstart.md`의 시나리오를 실제로 실행하는 방식으로 한다(001/003과 동일한 관례).

**Organization**: User Story(P1/P2)별로 태스크를 묶어 각 스토리를 독립적으로 구현·검증할 수 있게 한다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능(다른 파일, 선행 의존성 없음)
- **[Story]**: 이 태스크가 속한 User Story(US1, US2)
- 모든 설명에는 실제 파일 경로를 포함한다

## Path Conventions

이 기능은 `plan.md`의 Project Structure를 그대로 따른다 — 단일 Claude Code Skill 모듈:

```text
.claude/skills/exporting-markdown-diagrams/
├── SKILL.md
└── scripts/
    ├── export-diagrams.js
    ├── export-document-pdf.js
    ├── package.json
    └── lib/
        └── inline-svg.js
```

---

## Phase 1: Setup

**Purpose**: 스킬 디렉터리와 Node.js 패키지 초기화

- [X] T001 `.claude/skills/exporting-markdown-diagrams/`, `.claude/skills/exporting-markdown-diagrams/scripts/`, `.claude/skills/exporting-markdown-diagrams/scripts/lib/` 디렉터리 구조를 만든다
- [X] T002 [P] `.claude/skills/exporting-markdown-diagrams/scripts/package.json`을 만들고 `@mermaid-js/mermaid-cli`를 zenuml 지원이 병합된 2023-08-03 이후 릴리스된 버전으로 고정한다 (research.md Decision: `mermaid-cli` 버전 고정)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: User Story 1·2 모두가 의존하는 SKILL.md의 공통 골격(요청 파싱, 확인 질문, 렌더러 보존, 실패 처리)

**⚠️ CRITICAL**: 이 phase가 끝나야 두 User Story의 작업을 시작할 수 있다

- [X] T003 `.claude/skills/exporting-markdown-diagrams/SKILL.md`의 frontmatter(name/description)와 기본 워크플로(요청에서 `targetFile`/`format`/`scope` 판단)를 작성한다 (contracts/skill-interface.md Trigger, Input Contract)
- [X] T004 SKILL.md에 확인 질문 로직을 작성한다 — `format`과 `scope` 중 불분명한 것만 묻되, 둘 다 불분명하면 `AskUserQuestion` 한 번의 `questions` 배열에 두 항목을 함께 담는다 (spec.md FR-001~003, contracts/skill-interface.md Clarification Contract)
- [X] T005 SKILL.md에 렌더러 보존 규칙을 명시한다 — 다이어그램 소스(코드펜스 내용 전체)를 파싱·수정하지 않고 그대로 스크립트에 전달해야 한다는 지침 (spec.md FR-004, data-model.md `DiagramSource` 불변 조건)
- [X] T006 SKILL.md에 실패 처리 규칙을 명시한다 — 대상 파일이 없거나 도구 실행이 실패하면 그 오류를 그대로 전달하고, LLM 추론으로 조용히 대체하지 않는다 (spec.md Edge Cases, FR-005, contracts/skill-interface.md 실패 시 Output Contract)

**Checkpoint**: SKILL.md가 요청을 파싱하고 필요한 확인 질문까지 마친 뒤 스크립트를 호출할 준비가 된 상태 — 이제 User Story별 작업을 시작할 수 있다.

---

## Phase 3: User Story 1 - 다이어그램을 이미지로 export하기 (Priority: P1) 🎯 MVP

**Goal**: `scope=diagram`일 때 대상 다이어그램(들)을 SVG/PNG(선택적으로 PDF)로 변환한다.

**Independent Test**: `quickstart.md` 시나리오 1, 2, 4, 7, 8, 9 — 다이어그램이 포함된 마크다운 파일에 대해 형식 명시/미명시, 다이어그램 여러 개/없음, 렌더러 지정 보존, zenuml/일반 Mermaid 각각을 실행해 확인한다.

### Implementation for User Story 1

- [X] T007 [US1] `.claude/skills/exporting-markdown-diagrams/scripts/export-diagrams.js`를 작성한다 — 대상 마크다운 파일과 확정된 출력 형식을 받아 `mmdc -i <입력> -o <출력>.<형식>`을 호출한다. 문서에 다이어그램이 여러 개 있으면 `mmdc` 자체의 번호 매김 출력(`-1`, `-2`, ...)을 그대로 사용하고 별도의 다이어그램 탐지·분리 로직을 새로 만들지 않는다 (research.md Decision: User Story 1 구현 방식, data-model.md `ConversionArtifact`)
- [X] T008 [US1] `export-diagrams.js`에 "대상 문서에 다이어그램이 없음" 실패 케이스를 처리하는 로직을 추가한다 — `mmdc`가 다이어그램을 찾지 못했다고 보고하면 그 사실을 명확한 메시지로 변환해 반환한다 (spec.md Edge Cases, quickstart.md 시나리오 8)
- [X] T009 [US1] SKILL.md에 `scope=diagram` 분기를 연결한다 — Phase 2에서 확정된 `ConversionRequest`를 `export-diagrams.js` 호출 인자로 매핑하고, 생성된 파일 경로(들)를 응답으로 제시한다 (contracts/skill-interface.md Output Contract — `scope=diagram`)
- [X] T010 [US1] `quickstart.md` 시나리오 1, 2, 4, 7, 8, 9를 실제로 실행해 검증한다 (spec.md SC-001, SC-002, SC-005, SC-006) — 실제 실행 결과: 시나리오 1(svg/png/pdf 단일 변환) 통과, 시나리오 4(elk 렌더러 보존 — 결과 SVG의 `aria-roledescription="flowchart-elk"`로 확인) 통과, 시나리오 7(다이어그램 3개 → `-1`/`-2`/`-3` 개별 파일) 통과, 시나리오 8(다이어그램 없음 → 명확한 오류 메시지, exit 1) 통과, 시나리오 9(zenuml 플레이버 변환 성공, `UnknownDiagramError` 없음) 통과. 시나리오 2(AskUserQuestion 동작)는 스크립트가 아니라 SKILL.md의 오케스트레이션 동작이라 코드 리뷰로 확인(T004 참고) — Windows에서 `.cmd` 셰임을 직접 spawn하면 EINVAL이 나는 버그를 발견해 mermaid-cli의 JS 엔트리포인트(`src/cli.js`)를 Node로 직접 실행하는 방식으로 수정함

**Checkpoint**: User Story 1이 독립적으로 완전히 동작한다 — 여기까지만 구현해도 배포 가능한 MVP.

---

## Phase 4: User Story 2 - 문서 전체를 PDF로 export하기 (Priority: P2)

**Goal**: `scope=document`, `format=pdf`일 때 문서 전체를, 포함된 다이어그램이 벡터(SVG)로 삽입되어 텍스트가 선택·복사 가능한 PDF로 변환한다.

**Independent Test**: `quickstart.md` 시나리오 3, 5, 6 — 형식·범위가 모두 불분명한 요청의 확인 질문 모양, PDF 생성, PDF 안 다이어그램 텍스트의 선택·복사 가능 여부를 실행해 확인한다.

### Implementation for User Story 2

- [X] T011 [P] [US2] `.claude/skills/exporting-markdown-diagrams/scripts/package.json`에 마크다운→HTML 변환 라이브러리 의존성을 추가한다(구체적 선택은 이 태스크에서 확정 — research.md Decision: 마크다운→HTML 변환 라이브러리) — `markdown-it`으로 확정. `puppeteer`도 명시적 직접 의존성으로 추가(mermaid-cli가 요구하는 버전 범위 `^23||^24||^25`와 겹치는 `^25.0.0`으로 고정해 Chromium 중복 다운로드 없이 dedupe되는 것을 확인함
- [X] T012 [US2] `.claude/skills/exporting-markdown-diagrams/scripts/lib/inline-svg.js`를 작성한다 — HTML 문자열 안의 `<img src="*.svg">` 참조를 찾아 해당 SVG 파일의 실제 내용(`<svg>...</svg>`)으로 인라인 치환하는 함수 (data-model.md `IntermediateDocument`, research.md Decision: User Story 2 파이프라인 2단계)
- [X] T013 [US2] `.claude/skills/exporting-markdown-diagrams/scripts/export-document-pdf.js`의 1단계를 작성한다 — `mmdc -i <원본.md> -o <중간>.md -e svg`를 호출해 각 다이어그램을 SVG로 추출하고, 다이어그램 코드펜스가 이미지 참조로 치환된 중간 마크다운을 얻는다 (research.md Decision: User Story 2 파이프라인 1단계)
- [X] T014 [US2] `export-document-pdf.js`의 2단계를 작성한다 — 중간 마크다운을 HTML로 변환하고, T012의 `inline-svg.js`로 SVG를 인라인 삽입한 뒤, 헤드리스 브라우저로 그 HTML을 열어 `page.pdf()`로 인쇄한다 (depends on T011, T012, T013; spec.md FR-007)
- [X] T015 [US2] `export-document-pdf.js`에 임시 파일 정리 로직을 추가한다 — 최종 PDF가 생성되면 1단계의 중간 마크다운·SVG 파일을 삭제한다 (data-model.md `IntermediateDocument` 생애주기) — `try/finally`로 작업 디렉터리(`fs.mkdtempSync`) 전체를 정리하도록 구현
- [X] T016 [US2] SKILL.md에 `scope=document` 분기를 연결한다 — 확정된 `ConversionRequest`를 `export-document-pdf.js` 호출로 매핑하고, 생성된 PDF 경로를 응답으로 제시한다 (contracts/skill-interface.md Output Contract — `scope=document`) — 구현 중 발견: `scope=document`는 이번 범위에서 항상 `format=pdf`로 처리하도록 좁혔으므로(data-model.md 갱신 참고), SKILL.md Step 2의 확인 질문 로직에도 "scope=document면 format 질문 생략, 사용자가 다른 형식을 명시하면 지원하지 않는다고 안내" 규칙을 함께 반영함
- [X] T017 [US2] `quickstart.md` 시나리오 3, 5, 6을 실제로 실행해 검증한다 — 특히 시나리오 6(PDF 뷰어에서 다이어그램 텍스트를 드래그해 선택·복사)을 직접 확인한다 (spec.md SC-002, SC-004) — 실제 실행 결과: `.zenuml/jetpack-navigation-3.architecture.md`를 PDF로 변환(exit 0, 6페이지 생성) 후 `pymupdf`로 직접 검증 — 다이어그램 라벨(`MyApp`, `NavDisplay`, `EntryProvider`, `NavBackStack`)이 전부 추출 가능한 실제 텍스트로 존재하고, 임베드된 래스터 이미지는 0개(완전히 벡터로 삽입됐다는 뜻) — 시나리오 5·6 통과. 시나리오 3(AskUserQuestion 질문 2개 동시 제시)은 스크립트가 아니라 SKILL.md 오케스트레이션 동작이라 코드 리뷰로 확인(T004/T016 참고)

**Checkpoint**: User Story 1과 2 모두 독립적으로 동작한다.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 두 User Story에 걸친 마무리 작업

- [X] T018 [P] SKILL.md의 trigger `description`을 다듬는다 — `generating-zenuml-diagrams`/`generating-architecture-views`(다이어그램을 새로 *생성*)와 트리거가 겹치지 않도록 "이미 있는 다이어그램/문서를 다른 형식으로 *변환*한다"는 점을 명확히 한다 (contracts/skill-interface.md Trigger) — research.md에서 확인한 Anthropic `skill-creator` 가이드의 "undertrigger 방지를 위해 description을 약간 pushy하게" 권고를 반영해 짧은 예시 문구("이거 png로" 등)도 추가함
- [X] T019 `quickstart.md`의 시나리오 1~9를 전부 다시 실행하고 결과 표를 채운다 — 9개 전부 PASS(결과표 참고). 시나리오 2·3은 Skill 도구로 실제 라이브 호출해 `AskUserQuestion` 동작까지 직접 검증함
- [X] T020 `README.md`/`README.ko.md`에 새 스킬 소개를 추가한다 — 기존 `generating-architecture-views`를 소개한 방식과 동일하게 "Optional add-on" 절에 한 줄 추가한다(이 저장소가 새 스킬을 만들 때마다 README를 함께 갱신해온 관례를 따름) — Development history 목록에 004 항목 추가, Requirements 절도 `exporting-markdown-diagrams`가 Node.js를 필요로 한다는 점을 반영해 갱신함(기존 "실행 코드 없음" 문구가 더는 전체 저장소에 정확하지 않으므로)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 — 바로 시작 가능
- **Foundational (Phase 2)**: Setup 완료에 의존 — 완료 전까지 모든 User Story 작업을 막는다
- **User Story 1 (Phase 3)**: Foundational 완료 후 시작 가능, 다른 스토리에 의존하지 않는다
- **User Story 2 (Phase 4)**: Foundational 완료 후 시작 가능 — User Story 1과 동일한 SKILL.md 골격을 공유할 뿐, US1의 스크립트(`export-diagrams.js`)에 의존하지 않으므로 US1과 병행하거나 US1 없이도 독립적으로 완결될 수 있다
- **Polish (Phase 5)**: 구현하기로 한 User Story가 모두 끝난 뒤

### Within Each User Story

- User Story 1: T007(스크립트) → T008(실패 처리) → T009(SKILL.md 연결) → T010(검증)
- User Story 2: T011(의존성)·T012(inline-svg) → T013(1단계) → T014(2단계, T011·T012·T013에 의존) → T015(정리) → T016(SKILL.md 연결) → T017(검증)

### Parallel Opportunities

- T002(패키지 초기화)는 T001(디렉터리 생성) 완료 후 다른 Setup 태스크가 없으므로 사실상 순차적이지만, Foundational 태스크들과는 독립적이지 않다(같은 `package.json`을 여러 태스크가 건드리므로 순서 유지 권장).
- Foundational(T003~T006)은 모두 같은 `SKILL.md` 파일을 다루므로 순차 진행을 권장한다(같은 파일 충돌 방지).
- User Story 1과 User Story 2는 서로 다른 스크립트 파일을 다루므로, Foundational 완료 후 두 스토리를 병행 진행할 수 있다.
- User Story 2 내부에서 T011과 T012는 서로 다른 파일이라 병렬 가능하다.

---

## Parallel Example: User Story 2 시작 시점

```bash
# Foundational(Phase 2) 완료 후, User Story 2의 독립적인 두 준비 작업을 함께 진행:
Task: "package.json에 마크다운→HTML 변환 라이브러리 의존성 추가"
Task: "scripts/lib/inline-svg.js 작성"
```

---

## Implementation Strategy

### MVP First (User Story 1만)

1. Phase 1(Setup) 완료
2. Phase 2(Foundational) 완료 — SKILL.md 골격, 확인 질문, 렌더러 보존, 실패 처리
3. Phase 3(User Story 1) 완료
4. **중단하고 검증**: `quickstart.md` 시나리오 1, 2, 4, 7, 8, 9로 User Story 1을 독립적으로 확인
5. 여기까지만으로도 "다이어그램을 이미지로 export"하는 반복 요청을 완전히 대체할 수 있다

### Incremental Delivery

1. Setup + Foundational 완료 → 기반 준비 완료
2. User Story 1 추가 → 독립 검증 → 사용 시작(MVP)
3. User Story 2 추가 → 독립 검증 → 사용 시작
4. Polish(README 갱신 등)로 마무리

---

## Notes

- `[P]` 태스크는 서로 다른 파일을 건드리며 선행 의존성이 없다.
- `[Story]` 라벨은 태스크를 특정 User Story로 추적할 수 있게 한다.
- 각 User Story는 독립적으로 완결·검증 가능해야 한다.
- 논리적 단위(태스크 하나 또는 관련 태스크 묶음)마다 커밋한다.
- 각 체크포인트에서 멈춰 해당 스토리를 독립적으로 검증할 수 있다.
- 피해야 할 것: 모호한 태스크, 같은 파일을 동시에 건드리는 병렬 태스크, 두 스토리의 독립성을 깨는 교차 의존성.

---

## Phase 6: Convergence

**Purpose**: `/speckit-converge`가 실제 실행 결과(테스트 파일 직접 넘겨보기)와 파일 목록 대조로 발견한, spec.md/plan.md/contracts와 실제 구현 사이의 잔여 불일치를 바로잡는다.

- [X] T021 [P] `.claude/skills/exporting-markdown-diagrams/scripts/export-diagrams.js`와 `export-document-pdf.js`의 진입점에 대상 파일이 `.md`/`.markdown` 확장자인지 확인하는 검증을 추가한다 — 아니면 mermaid-cli를 호출하지 않고 "지원하지 않는 파일 형식입니다(.md/.markdown만 지원)" 같은 한 줄 메시지로 즉시 종료한다. 현재는 검증이 없어 비-마크다운 파일을 넘기면 mermaid-cli의 원시 `UnknownDiagramError` 스택트레이스가 그대로 노출됨(실제 실행으로 재현 확인) per spec.md Edge Cases (partial) — 두 스크립트 모두에 확장자 검증 추가 후 재실행으로 확인: `.txt` 파일 → 깔끔한 한 줄 메시지로 exit 1, 정상 `.md` 파일은 회귀 없이 그대로 동작
- [X] T022 [P] `specs/004-exporting-markdown-diagrams/plan.md`의 Project Structure 소스 트리에 `scripts/lib/run-mmdc.js`(Windows에서 mermaid-cli `.cmd` 셰임을 직접 spawn할 때 발생하는 EINVAL을 피하기 위해 구현 중 추가된, 두 스크립트가 공유하는 mmdc 호출 헬퍼)를 반영한다 per plan.md Project Structure (partial)
- [X] T023 `specs/004-exporting-markdown-diagrams/contracts/skill-interface.md`의 Clarification Contract를 실제 SKILL.md 동작으로 갱신한다 — `scope=document`가 확정되면 `format` 질문을 건너뛰고 항상 `pdf`로 처리하며, 사용자가 `scope=document`와 함께 `pdf`가 아닌 형식을 명시적으로 요청하면 조용히 대체하지 않고 PDF로 진행해도 되는지 되묻는다는 규칙(SKILL.md Step 2, T016 참고)을 문서에 반영한다 per contracts/skill-interface.md Clarification Contract (partial)
- [X] T024 [P] `.claude/skills/exporting-markdown-diagrams/scripts/lib/export-dir.js`를 작성한다 — 원본 마크다운 경로를 받아 `<그 디렉토리>/exports`를 계산하고 없으면 재귀적으로 생성해 반환하는 `ensureExportDir()` 헬퍼 (spec.md FR-009~010, data-model.md `ExportDirectory`)
- [X] T025 `export-diagrams.js`와 `export-document-pdf.js`의 기본 출력 경로 계산을 T024의 `ensureExportDir()`을 쓰도록 바꾼다 — 출력 경로 인자가 명시적으로 주어지지 않았을 때만 적용하고, 베이스 이름·번호 매김 규칙은 그대로 둔다(spec.md FR-011~012, contracts/skill-interface.md Output Contract)
- [X] T026 `quickstart.md` 시나리오 10을 실제로 실행해 검증한다 — `exports/`가 없는 상태에서 SVG·PDF 변환 각각 실행해 자동 생성, 산출물 위치, 다이어그램 여러 개일 때의 공유 여부, 기존 회귀(형식/범위 선택·렌더러 보존·실패 처리) 없음을 확인한다(spec.md SC-007, SC-008)
- [X] T027 `plan.md`의 Project Structure 소스 트리와 `README.md`/`README.ko.md`의 스킬 소개에 `exports/` 산출물 디렉토리 동작을 반영한다 per plan.md Project Structure, README "Optional add-ons"
- [X] T028 [US1] `export-diagrams.js`가 `mmdc`를 호출할 때, `format === "png"`이면 고정 배율 상수(`PNG_SCALE = 3`, research.md "PNG 해상도" Decision)를 `-s`/`--scale` 인자로 함께 전달하도록 고친다 — svg/pdf 형식에는 영향 없음(spec.md FR-013)
- [X] T029 `quickstart.md` 시나리오 11을 실제로 실행해 검증한다 — 큰 다이어그램을 PNG로 변환해 픽셀 크기가 `SVG 뷰박스 × 3`과 일치하는지, 텍스트가 실제 크기에서 선명한지 확인하고, svg/pdf 변환에 회귀가 없는지 확인한다(spec.md SC-009)
- [X] T030 [US2] `export-document-pdf.js`에 `--layout single|paginated`(기본값 `paginated`) 인자를 추가한다 — `paginated`는 기존 `page.pdf({ format: "A4", ... })`를 그대로 쓰고, `single`은 뷰포트를 본문 `max-width`보다 넉넉히 넓게 고정한 뒤 `document.documentElement.scrollWidth`/`scrollHeight`를 측정해 그 값을 `page.pdf()`의 `width`/`height`로 전달하고 `pageRanges: "1-1"`을 함께 준다(spec.md FR-014~015, research.md "문서 전체 PDF의 페이지 구성" Decision)
- [X] T031 [US2] `SKILL.md`에 `pdfLayout` 확인 질문 로직을 추가한다 — `scope`가 `document`로 확정됐는데 페이지 구성이 명시돼 있지 않으면, 옵션 순서 "1페이지 단일" → "표준 인쇄 규격"으로 별도의 단일 질문 `AskUserQuestion`을 제시한 뒤 그 답을 `--layout`으로 스크립트에 전달한다. 범위가 `diagram`이면 이 질문을 하지 않는다(spec.md FR-014, contracts/skill-interface.md Clarification Contract)
- [X] T032 `quickstart.md` 시나리오 12를 실제로 실행해 검증한다 — 페이지 구성 미명시 시 확인 질문이 뜨는지, "1페이지 단일"/"표준 인쇄 규격" 각각의 결과 페이지 수(PyMuPDF로 확인)가 기대와 일치하는지 확인한다(spec.md SC-010)
- [X] T033 [US2] `export-document-pdf.js`의 HTML 템플릿에서 `font-family: sans-serif`/`monospace` 제네릭 키워드를 한글·영문·코드를 지원하는 구체적 글꼴 스택으로 교체한다(spec.md FR-016, research.md "문서 전체 PDF의 글꼴" Decision)
- [X] T034 `quickstart.md` 시나리오 13을 실제로 실행해 검증한다 — 변환된 PDF를 이미지로 렌더링해 한글·영문·코드 텍스트가 선명한지 육안으로 확인한다(spec.md SC-011)
- [X] T035 [US2] T033의 직접 고른 글꼴 스택을 폐기하고, `export-document-pdf.js`의 본문·코드 `font-family`/`font-size`/`line-height`를 VS Code 자신의 Markdown 미리보기 스타일시트(`markdown-language-features/media/markdown.css`)의 `html, body`/`code` 규칙에서 그대로 옮긴 값으로 교체한다(spec.md FR-016 갱신판, research.md "문서 전체 PDF의 글꼴" Decision 갱신판)
- [X] T036 `quickstart.md` 시나리오 13(갱신판)을 실제로 실행해 검증한다 — 재변환한 PDF를 이미지로 렌더링해 한글이 여전히 정상 표시되는지(OS 폰트 링킹에 의존), 영문·코드가 VS Code Markdown 미리보기와 같은 글꼴로 보이는지 확인한다(spec.md SC-011 갱신판)
