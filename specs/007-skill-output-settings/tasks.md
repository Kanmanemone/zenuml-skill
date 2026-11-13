# Tasks: 스킬별 사용자 편집 설정 파일

**Input**: Design documents from `specs/007-skill-output-settings/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/settings-contract.md, quickstart.md

**Tests**: 별도 테스트 태스크 없음(spec이 요청하지 않음). 검증은 Polish 단계에서 quickstart 시나리오로 한다.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 세 스킬 디렉터리의 새 파일(`settings.jsonc`, `settings.schema.json`, `scripts/read-settings.js`, `scripts/lib/settings.js`)이 `.gitignore`에 걸리지 않고 추적 대상인지 `git check-ignore --no-index`로 확인

---

## Phase 2: Foundational

없음 — 스킬 간 의존을 금지하므로(003 FR-014) 공통 처리는 각 스킬 Phase 안에서 스킬마다 따로 만든다.

---

## Phase 3: User Story 1 - 구조 뷰의 Responsibility·Collaboration 표시 방식 고르기 (Priority: P1) 🎯 MVP

**Goal**: `generating-architecture-views`가 `settings.jsonc`를 읽어 Responsibility·Collaboration 표시 방식과 Dependency 렌더러를 적용한다.

**Independent Test**: quickstart 시나리오 1(architecture 부분), 2, 3

- [X] T002 [P] [US1] `.claude/skills/generating-architecture-views/settings.schema.json` 작성 — `responsibility.display`·`collaboration.display`(type `enum`, values `hidden`/`plain`/`collapsed`/`expanded`, default `plain`, tokenImpact `hidden`=토큰 소모 줄어듦·나머지=영향 거의 없음), `dependency.renderer`(type `enum`, values `default`/`elk`, default `default`, tokenImpact 둘 다 영향 거의 없음), 각 항목에 한국어 `description` (data-model.md "Option Definition")
- [X] T003 [P] [US1] `.claude/skills/generating-architecture-views/settings.jsonc` 작성 — T002와 같은 기본값을 `responsibility`/`collaboration`/`dependency` 묶음 아래에 두고, 각 옵션 위에 contracts/settings-contract.md 형식의 한국어 주석(의미, 값별 뜻·토큰 영향, 기본값)
- [X] T004 [US1] `.claude/skills/generating-architecture-views/SKILL.md`에 옵션 이름을 언급하지 않는 일반 "Settings" 절 추가 — 실행마다 `settings.schema.json`과 `settings.jsonc`를 읽고 data-model.md "해석 규칙" 표대로 값을 정하며, 요청 문장의 지정이 우선하고, 안내는 `⚙️ 설정 안내: <파일> — <내용>` 형식으로 채팅에만 붙이며, 설정 파일을 고치지 않는다. Workflow overview 첫 단계로 설정 읽기를 넣는다 (FR-002, FR-004~FR-007, FR-017, FR-019)
- [X] T005 [US1] `SKILL.md` Step 3·Step 4와 "File contents"/"Nothing but content"에 `display` 동작 규칙 추가 — `hidden`은 헤딩·내용·그 섹션 전용 자기검증(AP 항목)을 모두 생략, `collapsed`/`expanded`는 헤딩을 밖에 두고 research.md "접은 글 상자 마크업" 형태로 감싸며(`expanded`는 `<details open>`), 상자 마크업은 메타 코멘트가 아닌 허용 구조로 명시. 자기검증에 표시 방식 점검 AP 항목 추가, 채팅 안내 허용 예외에 설정 안내 추가 (FR-008~FR-010, FR-012, FR-005)
- [X] T006 [US1] `SKILL.md` Step 2 "Renderer selection"에 `dependency.renderer`가 `elk`이면 요청이 렌더러를 밝히지 않아도 `"defaultRenderer": "elk"`를 넣고, 요청이 밝히면 요청 값이 우선한다는 규칙 추가, AP-5b 문구를 이에 맞게 갱신 (FR-011b)
- [X] T007 [P] [US1] `.claude/skills/generating-architecture-views/references/templates.md`에 접은 글 상자 형태(`collapsed`/`expanded`) 템플릿 추가

**Checkpoint**: 구조 뷰가 설정대로 나온다.

---

## Phase 4: User Story 2 - 내보내기 기본값을 설정으로 고정하기 (Priority: P2)

**Goal**: `exporting-markdown-diagrams`가 질문 여부·기본값·PNG 배율·산출물 위치를 설정에서 읽고, 문서 PDF는 접은 글을 펼쳐 담는다.

**Independent Test**: quickstart 시나리오 1(exporting 부분), 5, 6, 7, 8, 9

- [X] T008 [P] [US2] `.claude/skills/exporting-markdown-diagrams/settings.schema.json` 작성 — `questions.enabled`(boolean, default `true`, tokenImpact `true`=영향 거의 없음·`false`=토큰 소모 줄어듦), `defaults.format`(enum `none`/`svg`/`png`/`pdf`, default `none`), `defaults.scope`(enum `none`/`diagram`/`document`, default `none`), `defaults.pdfLayout`(enum `none`/`single`/`paginated`, default `none`), `png.scale`(number, min 0 초과, default `3`), `output.directory`(relativePath, base `sourceFileDir`, default `./exports`), 각 한국어 description·tokenImpact
- [X] T009 [P] [US2] `.claude/skills/exporting-markdown-diagrams/settings.jsonc` 작성 — T008 기본값과 한국어 주석(contracts 형식)
- [X] T010 [US2] `.claude/skills/exporting-markdown-diagrams/scripts/lib/settings.js` 작성 — `loadSettings(skillDir)`: JSONC 주석 제거(문자열 안 `//` 보존) → `JSON.parse` → 옵션 정의의 각 `key`를 점 경로로 읽어 타입별 검증(`enum` 허용 값, `boolean`, `number` 유한·`min` 초과, `relativePath` 비어 있지 않고 `/`·`\`·`~`·드라이브 문자로 시작하지 않음) → 위반·알 수 없는 잎 키·읽기 실패를 안내 문구로 모아 `{values, notices}` 반환. 파일 없음·키 없음은 안내 없음. 옵션 이름을 코드에 하드코딩하지 않음 (FR-017, FR-019)
- [X] T011 [US2] `.claude/skills/exporting-markdown-diagrams/scripts/read-settings.js` 작성 — `loadSettings`를 호출해 `{"values":…, "notices":[…]}` 한 줄 JSON을 표준 출력, 항상 종료 코드 0
- [X] T012 [US2] `scripts/lib/export-dir.js`를 `output.directory`(원본 파일 디렉터리 기준 상대 경로)를 받아 해석·생성하도록 바꾸고, `scripts/export-diagrams.js`와 `scripts/export-document-pdf.js`가 시작 시 `loadSettings`로 값을 읽어 전달하게 함(명시적 출력 경로 인자가 있으면 그것이 우선) (FR-014)
- [X] T013 [US2] `scripts/export-diagrams.js`의 고정값 `PNG_SCALE`을 `png.scale` 설정 값으로 대체 (FR-014)
- [X] T014 [US2] `scripts/export-document-pdf.js`에서 `markdown-it` 렌더 결과의 `open` 없는 모든 `<details` 여는 태그에 `open`을 붙인 뒤 인쇄 (FR-015)
- [X] T015 [US2] `.claude/skills/exporting-markdown-diagrams/SKILL.md` 갱신 — 첫 단계로 `node scripts/read-settings.js` 실행·안내 문구 전달, `questions.enabled`가 `true`면 기존 질문 규칙대로 묻되 `defaults.*`와 같은 선택지 label 끝에 ` (기본값)`(기본값 `none`이면 없음), `false`면 빠진 정보를 `defaults.*`로 채우고 `none`인 항목만 묻기, 요청 문장 지정이 우선, "never pre-select" 문구를 이 규칙으로 교체, 문서 PDF는 접은 글을 항상 펼친다는 사실 반영 (FR-013, FR-013b, FR-015)

**Checkpoint**: 내보내기가 설정대로 동작하고 스크립트 결과가 결정적이다.

---

## Phase 5: User Story 3 - 시퀀스 다이어그램 피드백 로그 저장 위치 정하기 (Priority: P3)

**Goal**: `generating-zenuml-diagrams`가 `log.directory`에 피드백 로그를 남긴다.

**Independent Test**: quickstart 시나리오 1(zenuml 부분), 4

- [X] T016 [P] [US3] `.claude/skills/generating-zenuml-diagrams/settings.schema.json` 작성 — `log.directory`(relativePath, base `projectRoot`, default `./.zenuml/log`, tokenImpact 영향 거의 없음, 한국어 description)
- [X] T017 [P] [US3] `.claude/skills/generating-zenuml-diagrams/settings.jsonc` 작성 — `log` 묶음 아래 `directory`와 한국어 주석
- [X] T018 [US3] `.claude/skills/generating-zenuml-diagrams/SKILL.md`에 T004와 같은 형태의 일반 "Settings" 절을 추가하고, "Diagram feedback log"와 인용 시 스테이징 규칙의 `.zenuml/log/` 경로를 `log.directory` 해석 값으로 바꾸며(없으면 생성, 이전 위치 로그는 옮기지 않음), 채팅 허용 예외(FR-012/AP-6)에 설정 안내 추가 (FR-015c, FR-005)

**Checkpoint**: 로그가 설정 위치에 쌓인다.

---

## Phase 6: Polish & Cross-Cutting

- [X] T019 quickstart 시나리오 5·6·7·9를 실제로 실행해 확인하고 결과를 `specs/007-skill-output-settings/quickstart.md` 끝에 기록
- [X] T020 [P] `README.md`·`README.ko.md`에 각 스킬 폴더의 `settings.jsonc`로 동작을 바꿀 수 있다는 한 줄 안내 추가
- [X] T021 모든 옵션의 배포 초기값을 사용자에게 항목별로 확인하고, 답에 맞춰 세 스킬의 `settings.schema.json` `default`와 `settings.jsonc` 값·주석의 기본값 표기를 함께 갱신 (FR-003)

---

## Dependencies & Execution Order

- Phase 1 → Phase 3/4/5(서로 독립, 어느 순서든 가능) → Phase 6
- 같은 스킬 안: 옵션 정의(T002/T008/T016) → 설정 파일·SKILL.md 규칙. exporting은 T010 → T011·T012·T013 → T015
- T021은 다른 모든 태스크 완료 후

## Parallel Opportunities

- 스토리 간: US1·US2·US3는 서로 다른 스킬 디렉터리라 동시에 진행 가능
- 스토리 안: T002/T003/T007, T008/T009, T016/T017

## Implementation Strategy

MVP는 US1(사용자가 처음 요청한 구조 뷰 접기). 이후 US2, US3, Polish 순으로 하나씩 완료·검증한다.

---

## Phase 7: Convergence

**Purpose**: `/speckit-converge`가 사용자가 배포 초기값을 확정(T021)한 뒤에도 잠정값을 전제로 남아 있는 설계 문서를 찾아 바로잡는다.

- [ ] T022 `specs/007-skill-output-settings/quickstart.md` 시나리오 1을, 확정 초기값이 세 스킬의 `settings.schema.json` `default`와 `settings.jsonc` 값에 똑같이 들어 있는지와, 잠정값(기능 도입 전 동작)으로 설정을 바꾸면 산출물이 기능 도입 전과 같은지를 확인하는 내용으로 고친다 per FR-003, SC-001 (partial)
- [ ] T023 [P] `specs/007-skill-output-settings/data-model.md` "현재 옵션 목록"에 사용자가 확정한 배포 초기값 열을 추가하고 표 제목을 그에 맞게 바꾼다 per FR-003 (partial)
