# Tasks: 변환 중 터미널 창 깜빡임 제거

**Input**: Design documents from `specs/006-hide-console-windows/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: 자동 테스트는 요청되지 않았다 — 검증은 quickstart.md 시나리오로 수행한다.

**Organization**: 경로는 저장소 루트 기준이며 `SK = .claude/skills/exporting-markdown-diagrams/scripts`.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 변경 전 기준선을 만든다: 현재 커밋의 스크립트로 `.zenuml/*.md`(다이어그램 있는 파일 전부)와 005 quickstart.md의 `clip.md`를 SVG로 뽑아 저장소 밖 임시 디렉토리에 보관하고, 같은 PNG 변환의 웜 실행 시간을 기록한다

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T002 `SK/puppeteer-config.json`을 만든다: `{ "headless": true, "args": ["--lang=en-US"] }`
- [X] T003 `SK/lib/browser-config.js`를 만든다: `PUPPETEER_CONFIG_FILE`(위 JSON의 절대 경로)과 그 파일을 파싱한 `BROWSER_LAUNCH_OPTIONS`를 export하고, 왜 이 설정인지(창 생성 회피, `--lang`이 산출물을 유지) 짧게 주석으로 남긴다

**Checkpoint**: 공통 브라우저 설정 준비 완료

---

## Phase 3: User Story 1 - 변환 중에 터미널 창이 뜨지 않기 (Priority: P1) 🎯 MVP

**Goal**: 모든 변환에서 새 창 0개, 산출물 불변.

**Independent Test**: quickstart.md 시나리오 1·2·3.

- [X] T004 [US1] `SK/lib/run-mmdc.js`: `runMmdc`가 넘겨받은 인자 앞에 항상 `-p <PUPPETEER_CONFIG_FILE>`를 붙이도록 한다
- [X] T005 [P] [US1] `SK/export-diagrams.js`: `puppeteer.launch({ headless: "shell" })`를 `puppeteer.launch(BROWSER_LAUNCH_OPTIONS)`로 바꾸고, 옆 주석을 "mmdc와 같은 공통 설정"으로 고친다
- [X] T006 [P] [US1] `SK/export-document-pdf.js`: 같은 방식으로 `puppeteer.launch(BROWSER_LAUNCH_OPTIONS)` 사용
- [X] T007 [US1] `SK/lib/fit-svg.js` 상단 주석의 "측정 브라우저 = 렌더 브라우저" 설명이 공통 설정 도입 후에도 맞는지 확인하고, 필요하면 `lib/browser-config.js`를 가리키도록 최소 수정한다
- [X] T008 [US1] quickstart.md 시나리오 1(창 감시)·2(SVG 바이트 비교)·3(시간)을 실행해 결과를 확인한다

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T009 `.claude/skills/exporting-markdown-diagrams/SKILL.md`에 브라우저 종류·창에 관한 서술이 있는지 확인하고, 모순이 있을 때만 최소 수정한다

---

## Dependencies & Execution Order

- T001 → T002 → T003 → T004 → (T005 ∥ T006) → T007 → T008 → T009

### Parallel Opportunities

- T005와 T006은 서로 다른 파일이라 병렬 가능.

## Implementation Strategy

- MVP = Phase 1~3 전체(스토리가 하나뿐이다).
