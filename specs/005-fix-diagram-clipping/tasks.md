# Tasks: 다이어그램 가장자리 잘림 수정

**Input**: Design documents from `specs/005-fix-diagram-clipping/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/export-scripts.md, quickstart.md

**Tests**: 자동 테스트는 요청되지 않았다 — 검증은 quickstart.md 시나리오로 수행한다.

**Organization**: 사용자 스토리별로 묶는다. 경로는 저장소 루트 기준이며 `SK = .claude/skills/exporting-markdown-diagrams/scripts`.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 수정 전 스크립트로 회귀 비교 기준선을 만든다: 현재 커밋의 `SK/export-diagrams.js`로 `.zenuml/*.md`(다이어그램 있는 파일 전부)와 quickstart.md의 `clip.md` 샘플을 SVG로 뽑아 저장소 밖 임시 디렉토리(세션 scratchpad)에 보관한다

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T002 `SK/lib/fit-svg.js`를 새로 만든다: `readViewBox`, `patchRootTag`(루트 태그의 `viewBox`와 `max-width: Npx`만 문자열 치환, DOM 재직렬화 금지), `withSvgPage`(호출자 browser로 새 page에 SVG를 띄우고 항상 page를 닫음), 그리고 export `fitSvgFile(browser, svgPath)` — data-model.md "보정 규칙"(넘친 변만 16 unit 여백, 1 unit 이하 무시, 바뀐 게 없으면 파일 미수정)대로 동작하고 `FitResult`를 반환
- [X] T003 `SK/lib/fit-svg.js`에 `svgFileToPng(browser, svgPath, pngPath, scale)`(viewBox 크기 뷰포트 + `deviceScaleFactor=scale`, 흰 배경, 루트 svg에 px 크기 지정·`max-width: none` 후 요소 screenshot)와 `svgFileToPdf(browser, svgPath, pdfPath)`(viewBox 크기 한 페이지, `printBackground`, `pageRanges: "1-1"`)를 추가한다

**Checkpoint**: 공용 보정·렌더 모듈 준비 완료

---

## Phase 3: User Story 1 - 다이어그램 단독 export에서 내용이 잘리지 않기 (Priority: P1) 🎯 MVP

**Goal**: SVG/PNG/PDF 다이어그램 단독 산출물에서 가장자리 내용이 잘리지 않는다.

**Independent Test**: quickstart.md 시나리오 1·2.

- [X] T004 [US1] `SK/export-diagrams.js` 파이프라인을 교체한다: mmdc는 형식과 무관하게 OS 임시 디렉토리에 `<base>.svg`로만 렌더(`-s` 옵션 제거), 임시 디렉토리에서 `^<base>(-N)?\.svg$` 파일을 다이어그램 순서로 수집(없으면 실패), 브라우저를 `headless: "shell"`로 한 번 띄워 각 SVG에 `fitSvgFile` 후 `svg`=복사 / `png`=`svgFileToPng(…, PNG_SCALE)` / `pdf`=`svgFileToPdf`로 `outputDir/<같은 이름>.<format>` 생성, 이번 실행에서 만든 파일만 순서대로 stdout 출력. 기존 입력 검증·오류 메시지·종료 코드·"No mermaid charts found" 검사는 유지
- [X] T005 [US1] `SK/export-diagrams.js`에서 `fail()`(process.exit)로 끝나는 경로에서도 임시 디렉토리가 지워지도록 한다(예: `process.on("exit", …)` 정리), 그리고 비동기 예외는 `main().catch`로 `fail`에 넘긴다
- [X] T006 [US1] `SK/export-diagrams.js`의 `PNG_SCALE` 주석을 새 동작(보정된 viewBox 크기로 뷰포트를 잡고 축소 없이 배율로 캡처)에 맞게 고친다
- [X] T007 [US1] quickstart.md 시나리오 1·2를 실행하고 `clip-1.png`를 열어 주석 전문이 보이는지, PNG 폭이 viewBox 폭 × 3인지, PDF가 1페이지인지 확인한다

**Checkpoint**: US1 단독으로 잘림 해소 확인

---

## Phase 4: User Story 2 - 문서 전체 PDF에 삽입된 다이어그램도 잘리지 않기 (Priority: P2)

**Goal**: 문서 전체 PDF의 삽입 다이어그램도 보정된다.

**Independent Test**: quickstart.md 시나리오 3.

- [X] T008 [US2] `SK/export-document-pdf.js`: `fitSvgFile`을 import하고, 브라우저 launch를 Stage 1 직후로 옮겨 `workDir/*.svg` 각각에 `fitSvgFile`을 적용(Stage 1.5)한 뒤 기존 Stage 2(인라인·인쇄)를 같은 브라우저로 수행한다. `fullHtml` 템플릿 리터럴 내부 HTML의 들여쓰기는 바꾸지 않는다
- [X] T009 [US2] quickstart.md 시나리오 3(`--layout single`, `--layout paginated`)을 실행해 오류 없이 PDF가 생성되고 삽입 다이어그램 주석 전문이 보이는지 확인한다

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T010 quickstart.md 시나리오 4: T001 기준선과 수정 후 SVG를 `cmp`로 비교해, 넘침 없는 다이어그램 전부가 바이트 동일하고 바뀐 것은 viewBox만 넓어졌는지 확인한다
- [X] T011 [P] `.claude/skills/exporting-markdown-diagrams/SKILL.md`가 새 동작과 모순되는 서술(예: mmdc가 png/pdf를 직접 만든다는 설명)을 담고 있는지 확인하고, 있을 때만 최소 수정한다

---

## Dependencies & Execution Order

- T001 → (T002 → T003) → US1(T004 → T005 → T006 → T007) → US2(T008 → T009) → T010, T011
- US2는 Phase 2 모듈에만 의존하므로 US1과 독립적으로 구현 가능하지만, 같은 사람이 순서대로 진행한다.

### Parallel Opportunities

- T011은 다른 파일이라 T010과 병렬 가능. T004~T006은 같은 파일이라 순차.

## Implementation Strategy

- MVP = Phase 1~3(US1). US2는 같은 보정 함수를 재사용하는 작은 증분.
