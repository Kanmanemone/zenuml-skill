# Tasks: 문서 전체를 PNG 이미지로 내보내기

**Input**: Design documents from `specs/008-document-png-export/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: 별도 테스트 태스크 없음. Polish 단계에서 quickstart 시나리오를 실제 실행해 확인한다.

## Phase 1: Setup

- [X] T001 `.claude/skills/exporting-markdown-diagrams/scripts/package.json`에 `pdfjs-dist` 의존성을 추가하고 같은 폴더에서 `npm install`로 `package-lock.json`을 갱신

---

## Phase 2: Foundational

- [X] T002 `scripts/export-document-pdf.js`의 문서 → PDF 파이프라인(다이어그램 추출, SVG viewBox 보정, HTML 생성, 접은 글 펼침, single/paginated 인쇄, 임시 파일 정리)을 `scripts/lib/document-pdf.js`의 `renderDocumentPdf(browser, targetFile, layout, outputFile)`로 옮기고, `export-document-pdf.js`는 인자 처리·설정 읽기·브라우저 실행·결과 출력만 하는 얇은 CLI로 정리 — 인자·출력·결과 PDF는 바뀌지 않아야 함 (SC-006)

**Checkpoint**: 문서 PDF가 리팩터링 전과 같은 페이지 수로 만들어진다.

---

## Phase 3: User Story 1 - 문서 전체를 PNG로 받기 (Priority: P1) 🎯 MVP

**Goal**: 문서 전체 PNG를 single/paginated로 만든다.

**Independent Test**: quickstart 시나리오 1~4, 6

- [X] T003 [US1] `scripts/lib/rasterize-pdf.js` 작성 — `rasterizePdf(browser, pdfFile, scale, outputFiles)`: `127.0.0.1` 임의 포트의 임시 HTTP 서버로 `pdfjs-dist`의 브라우저용 모듈·worker와 PDF를 제공하고, 브라우저 페이지에서 pdf.js로 각 페이지를 viewport scale `scale × 96 / 72`로 canvas에 그려 PNG 데이터를 받아 페이지 순서대로 파일에 쓴 뒤 서버를 닫음. 렌더링 실패(크기 한계 포함) 시 페이지 번호·크기를 담은 오류를 던짐 (FR-002, FR-005, FR-012)
- [X] T004 [US1] `scripts/export-document-png.js` 작성 — contracts/cli.md대로: `<targetFile.md> [outputBase] --layout <single|paginated>`(기본 `paginated`), 설정 `png.scale`·`output.directory` 읽기, `renderDocumentPdf`로 임시 PDF 생성 → `rasterizePdf`로 PNG(single: `<base>.png`, paginated: `<base>-page-<N>.png`, N은 1부터), 성공 시 경로를 줄마다 출력, 실패 시 종료 코드 ≠ 0, 임시 파일 정리 (FR-001~FR-005, FR-011, FR-012)

**Checkpoint**: 스크립트만으로 문서 전체 PNG가 만들어진다.

---

## Phase 4: User Story 2 - 형식·범위 선택과 설정이 문서 전체 PNG와 맞물리기 (Priority: P2)

**Goal**: 대화 흐름이 문서 전체에서 PDF·PNG를 고르고 PNG 스크립트로 디스패치한다.

**Independent Test**: quickstart 시나리오 7

- [X] T005 [US2] `.claude/skills/exporting-markdown-diagrams/SKILL.md` Step 2를 data-model.md "형식 결정 규칙(scope=document)" 표대로 고침 — "scope=document면 format=pdf 자동" 규칙 제거, 문서 전체 형식 질문 선택지는 `PDF`, `PNG`뿐(" (기본값)"은 `defaults.format`이 `pdf`/`png`일 때만), SVG 요청은 미지원 안내 후 PDF·PNG 질문, 질문을 끈 경우 `defaults.format`이 `svg`/`none`이면 PDF·PNG 질문, 페이지 구성 질문·`defaults.pdfLayout`은 PDF·PNG 공통, 질문 문구 "PDF 페이지를 어떻게 만들까요?"를 PDF·PNG 공통 표현으로 (FR-006~FR-010)
- [X] T006 [US2] `SKILL.md` "Scope: whole document"에 PNG 디스패치(`node scripts/export-document-png.js <targetFile> "" --layout <single|paginated>`)와 결과 보고 규칙 추가, frontmatter description과 Workflow overview·Step 1의 "whole document = PDF" 서술을 PDF·PNG로 갱신
- [X] T007 [P] [US2] `settings.schema.json`·`settings.jsonc`의 `defaults.pdfLayout` 설명을 "문서 전체(PDF·PNG)의 페이지 구성"으로, `defaults.scope`의 `document` 설명에서 "항상 PDF"를 "PDF 또는 PNG"로, `defaults.format` 설명에 "문서 전체에는 svg를 쓸 수 없음"을 반영 — 키 이름은 바꾸지 않음

---

## Phase 5: Polish & Cross-Cutting

- [X] T008 quickstart 시나리오 1~6을 실제로 실행하고 결과를 `specs/008-document-png-export/quickstart.md` 끝에 기록
- [X] T009 [P] `README.md`·`README.ko.md`의 `exporting-markdown-diagrams` 설명에 문서 전체 PNG를 반영

---

## Dependencies & Execution Order

- T001 → T002 → T003 → T004 → (T005, T006, T007) → T008, T009
- T007은 T005·T006과 다른 파일이라 병렬 가능

## Implementation Strategy

MVP는 US1(스크립트로 문서 PNG 생성). 이어 US2로 대화 흐름을 연결한다.
