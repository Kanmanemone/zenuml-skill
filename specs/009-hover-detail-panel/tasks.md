# Tasks: 다이어그램 노드 hover로 책임·협력 보기

**Input**: Design documents from `specs/009-hover-detail-panel/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/apply-hover-contract.md, quickstart.md

**Tests**: 별도 테스트 태스크 없음(spec이 요청하지 않음). 검증은 각 Checkpoint와 Polish 단계에서 quickstart 시나리오로 한다.

**공통 제약**(모든 태스크): Python 3.9 이상에서 동작, 표준 라이브러리만, 3.10+ 전용 문법(`match`, 런타임 `X | Y` 타입 표기) 금지. 파일은 UTF-8로 읽고 쓰며 줄바꿈 형식(LF/CRLF)과 파일 끝 줄바꿈 유무는 입력을 따른다. 본문(`### Responsibility`·`### Collaboration` 아래 줄)은 어떤 경우에도 바꾸지 않는다(FR-002). 산출 파일에 표식·메타 주석을 넣지 않는다(003 AP-13c).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 다른 파일을 고치고 아직 끝나지 않은 태스크에 기대지 않아 동시에 할 수 있음
- **[Story]**: US1·US2·US3 (spec.md의 User Story)

---

## Phase 1: Setup

- [X] T001 `.gitignore`에 `__pycache__/`를 추가하고, 새 파일 `.claude/skills/generating-architecture-views/scripts/apply_hover.py`·`scripts/hover/*.py`와 `specs/009-hover-detail-panel/fixtures/*`가 추적 대상인지 `git check-ignore -v --no-index`로 확인
- [X] T002 [P] 디렉터리와 빈 패키지 만들기 — `.claude/skills/generating-architecture-views/scripts/hover/__init__.py`(빈 파일), `specs/009-hover-detail-panel/fixtures/`
- [X] T003 [P] 고정 입력 `specs/009-hover-detail-panel/fixtures/view.input.md` 작성 — 기능 도입 전 규칙(현재 SKILL.md, templates.md)대로 쓴 구조 뷰. 반드시 포함: `subgraph` 그룹 2개 이상, 링크 있는 노드와 없는 노드, 노드마다 색상 클래스 하나(003 FR-008b), 7개 이상 노드로 6색을 넘겨 색이 처음부터 다시 도는 경우, `Id@{ label: "…" }` 형태 노드 1개, 병렬 형제 묶음 Responsibility 항목 1개(3개 이상), 묶음 이름 협력 1개(3개 이상 대상), 대상 2개 협력(`A와 B에 의존한다`) 1개, 서로 의존하는 쌍 1개, 다른 노드에 의존하지 않는 노드 1개, 본문 문장 안에 큰따옴표 `"`·코드 `` `…` ``·`<`/`>`·Markdown 링크 각 1번 이상, Responsibility·Collaboration은 `collapsed`(`<details>`) 상자 안. 링크 대상은 실제 존재하지 않아도 되는 상대 경로와 URL을 섞는다

---

## Phase 2: Foundational (모든 스토리의 전제)

- [X] T004 [P] `.claude/skills/generating-architecture-views/scripts/hover/settings.py` 작성 — `.claude/skills/exporting-markdown-diagrams/scripts/lib/settings.js`와 같은 동작을 Python으로: 문자열 안 `//`는 지키며 `//`·`/* */` 주석 제거 → JSON 해석, `settings.schema.json`의 `options`만 보고 `{ "values": {"<dotted.key>": 값}, "notices": [...] }`를 만든다. 규칙: 파일 없음 → 모든 기본값·안내 없음 / 읽지 못함(JSON 아님·최상위가 객체 아님) → 모든 기본값 + `읽지 못해 모든 값을 기본값으로 사용` / 키 없음 → 기본값·안내 없음 / 값이 규칙 위반 → 그 키만 기본값 + `` `<key>` 값이 허용되지 않아 기본값 `<default>` 사용 `` / 정의에 없는 말단 키 → 무시 + `` 알 수 없는 키 `<key>` 무시 ``. 안내 형식은 `⚙️ 설정 안내: settings.jsonc — <내용>`. 타입 `enum`·`boolean`·`relativePath`는 settings.js와 같게, 새 타입 `itemList`는 "배열이고, 모든 원소가 `items`에 있는 문자열이며, 중복이 없을 때만 유효(빈 배열 유효)". 기본값을 안내에 쓸 때 목록은 JSON 표기(`["targets", "boundary", "rationale"]`). 같은 검증 함수를 명령줄 재정의 값에도 쓸 수 있게 공개한다(research R2·R4)
- [X] T005 [P] `.claude/skills/generating-architecture-views/settings.schema.json`에 옵션 4개 추가 — `hover.enabled`(type `boolean`, default `true`), `hover.responsibility`(type `itemList`, items `abstract`·`concrete`, default `["abstract", "concrete"]`), `hover.collaboration`(type `itemList`, items `targets`·`boundary`·`rationale`·`questions`, default `["targets", "boundary", "rationale"]`), `hover.position`(type `enum`, values `bottom`·`node`, default `bottom`). 각 항목에 한국어 `description`, `tokenImpact`는 모든 값(`itemList`는 항목별)이 "토큰 소모 영향 없음"(data-model.md "설정 옵션", FR-018)
- [X] T006 [P] `.claude/skills/generating-architecture-views/scripts/hover/style_blocks.py` 작성 — 상수 두 개: `BOTTOM`은 `docs/hover-tooltip-test/inline-style.md`의 `<style>…</style>` 블록, `NODE`는 `docs/hover-tooltip-test/node-25em.md`의 `<style>…</style>` 블록을 바이트 단위로 그대로(줄바꿈은 `\n`로 저장하고 출력할 때 입력 파일 형식에 맞춘다). 함수 `block_for(position)`. 두 블록 모두 밑줄 규칙 `.node.clickable:hover .nodeLabel { text-decoration: underline; }`를 포함하는지 확인(FR-005, contract "style 블록 원본")
- [X] T007 `.claude/skills/generating-architecture-views/scripts/hover/view_parser.py` 작성 — 구조 뷰 파일 텍스트를 data-model.md의 Node·Edge·ResponsibilityEntry·CollaborationEntry로 읽는다(research R6·R7). Dependency 코드 블록 위치, 노드 선언 3형태(`Id`, `Id@{ label: "…" }`, `Id["…"]`)와 표시 이름 정규화(✨/♻️/🗑️, `&nbsp;`, `<b>`·`<s>` 제거), `class Id xxx` 줄로 노드의 색상 클래스, 엣지 `Src eN@-->|관계| Dst`, 링크 `click Id "대상" "툴팁"`과 `click Id hoverOnly "툴팁"` 줄 위치, `classDef` 줄 위치, CRUD 절 마지막 `classDef crud*` 줄 위치, `#### 요소의 책임`·`#### 요소 간 비교` 아래 항목(`<details>` 안팎 동일), Collaboration 첫 줄의 주어·`oneWay`/`mutual`·대상 글자·대상 노드 이름, 세부 분석 3종의 하위 글머리 항목, 파일 끝 패널 모양 블록(`div.mermaidTooltip`을 담은 마지막 `<style>` 블록)과 그 앞 빈 줄의 위치. `### Dependency` 아래 Mermaid 코드 블록이 없으면 형식 오류를 낸다. 섹션 제목이 없으면 그 섹션 항목은 빈 목록(research R5)

**Checkpoint**: 설정 로더가 `settings.jsonc`를 읽고, 파서가 `fixtures/view.input.md`의 노드·엣지·본문 항목을 빠짐없이 돌려준다.

---

## Phase 3: User Story 1 - 노드에 마우스를 올려 책임과 협력을 그 자리에서 보기 (Priority: P1) 🎯 MVP

**Goal**: 기본 설정으로 만든 구조 뷰에서 모든 노드에 hover 패널이 뜬다.

**Independent Test**: quickstart Q1, V1, V2, V3, V5, E1, E2, S1

- [X] T008 [US1] `.claude/skills/generating-architecture-views/scripts/hover/panel_text.py` 작성 — 노드 하나의 NodePanel 문자열을 data-model.md "NodePanel" 대로 조립: 맨 윗줄 `<b>{name}</b>`, Responsibility 부분(목록 순서대로 `<b>책임 (추상)</b>: …`, `<b>역할 (구체)</b>: …`, 줄 사이 `<br/>`), 두 부분 사이에만 `<br/><br/>`, Collaboration 부분은 그 노드가 주어인 `oneWay` 항목과 그 노드가 들어 있는 `mutual` 항목만 본문 순서대로(의존받는 쪽 없음, FR-011). 협력 머리줄 `<b>{대상 글자}에 의존한다 ({관계})</b>` / `<b>{상대}와 서로 의존한다 ({관계})</b>`, 관계 이름은 research R7 규칙(패널 주인 노드에서 나가는 엣지 라벨만 사용, 정해지지 않으면 괄호 생략), 세부 분석은 목록 순서대로 `<b>{제목}</b>: {하위 항목을 공백 하나로 이은 문단}`(제목: 책임의 경계 / 분리 이유 &amp; 합리성 평가 / 내가 할 수 있는 질문), 목록에 `targets`가 없어도 다른 항목이 있으면 머리줄을 붙인다, 협력 사이는 세부 분석이 있으면 `<br/><br/>` 아니면 `<br/>`(FR-012). 병렬 형제 묶음 Responsibility 항목은 묶인 각 노드에 항목 전체를 넣는다. 글자 변환은 research R8(`<strong>`→`<b>`, 코드 → `<code>`(안쪽 `&<>` 엔터티), Markdown 링크 → 글자, 나머지 `&<>` 엔터티, `"` → `&quot;`). 두 부분이 모두 비면 `None`
- [X] T009 [US1] `.claude/skills/generating-architecture-views/scripts/apply_hover.py` 작성(켜짐 경로) — contracts/apply-hover-contract.md "실행"과 "변환 규칙 (켜짐)": 인자 파싱(`argparse`, 파일 경로 필수), 스크립트 위치 기준 스킬 디렉터리에서 설정 읽기, 유효 설정 계산, 노드마다 NodePanel 계산 후 (1) 링크 `click` 줄 세 번째 인자 교체(대상은 그대로), (2) 이전 `hoverOnly` 줄 삭제 후 링크 없는 노드 중 NodePanel 있는 노드마다 `  click Id hoverOnly "…"`를 마지막 링크 `click` 줄 다음(없으면 마지막 `classDef crud*` 줄 다음 빈 줄 하나 뒤)에 노드 선언 순서대로, (3) 이전 `,cursor:auto` 삭제 후 `hoverOnly` 노드의 색상 `classDef` 줄 끝에 `,cursor:auto`(색상 클래스는 노드마다 하나, 003 FR-008b), (4) 파일 끝 패널 모양 블록 교체 또는 빈 줄 하나 + 새 블록 추가. 내용이 같으면 다시 쓰지 않고 `변경 없음: <파일>`, 바뀌면 `hover 적용: <파일> (노드 N개에 패널, 위치 <position>)`을 UTF-8 표준 출력으로, 이어서 설정 안내 줄. 종료 코드 0 / 인자 오류·읽기 실패 1 / 형식 오류 2(파일 그대로). `if __name__ == "__main__":` 진입. 이 태스크에서는 꺼짐 경로(T016)를 호출하는 자리만 남긴다
- [X] T010 [US1] `.claude/skills/generating-architecture-views/SKILL.md` "Output file"과 Workflow overview 6단계 개정 — 저장 순서를 "구조 뷰 파일 → 피드백 로그 → 유효 hover 설정이 켜짐이면 `apply_hover.py` 실행"으로 적는다. 인터프리터는 `python3` → `python` → `py -3` 순으로 찾아 3.9 이상인 것을 쓰고, 스킬 디렉터리 기준 `scripts/apply_hover.py <구조 뷰 파일 경로>`로 실행. 찾지 못하면 실행하지 않고 응답 끝에 `⚙️ hover 건너뜀: Python 3.9 이상을 찾지 못함` 한 줄, 종료 코드가 0이 아니면 파일은 그대로 두고 한 줄로 알림. 스크립트가 낸 설정 안내 줄은 응답 끝 설정 안내에 합치되 같은 줄을 두 번 쓰지 않는다. 피드백 로그 `**Response**:`는 스크립트 실행 전 모델이 쓴 내용(research R3). 채팅 응답 허용 예외 목록에 hover 건너뜀·실패 안내를 추가
- [X] T011 [US1] `SKILL.md` Step 2 "Hyperlinks"와 click 툴팁 규칙 개정(003 개정 FR-017) — 모델은 지금처럼 툴팁을 파일 이름으로 쓰고 링크 없는 노드에는 `click`을 두지 않으며, 툴팁 내용·`hoverOnly` 줄·`,cursor:auto`·패널 모양 블록은 스크립트만 쓴다고 명시. "링크 대상이 없으면 `click`을 두지 않는다"에 "스크립트가 패널 내용이 있을 때 `click Id hoverOnly "…"`를 단다(이동 대상을 지어내는 것이 아님)" 예외를 덧붙인다
- [X] T012 [US1] `SKILL.md` "Nothing but content"·AP-13c 허용 목록 개정(003 개정 FR-016) — 파일 끝 패널 모양 `<style>` 블록, `click Id hoverOnly "…"` 줄, 색상 `classDef`의 `,cursor:auto`를 메타 코멘트가 아닌 표시 규칙으로 허용하고, 이 셋과 채워진 툴팁은 스크립트가 쓴 것만 허용(모델이 직접 쓰면 위반)이라고 적는다. AP-13c 체크 문구도 같게 고친다
- [X] T013 [P] [US1] `.claude/skills/generating-architecture-views/references/templates.md` "Hyperlink syntax" 아래에 스크립트 실행 후 모습 예시 추가 — 채워진 툴팁의 링크 `click` 줄 1개, `hoverOnly` 줄 1개, `,cursor:auto`가 붙은 `classDef` 1개, 그리고 "모델은 이 형태를 직접 쓰지 않는다" 한 줄
- [X] T014 [P] [US1] `.claude/skills/generating-architecture-views/settings.jsonc`에 `hover` 그룹 추가 — T005와 같은 기본값을 `"hover": { "enabled", "responsibility", "collaboration", "position" }` 아래에 두고, 기존 형식대로 옵션마다 한국어 주석(의미, 값·항목별 뜻과 토큰 영향 "토큰 소모 영향 없음", 기본값). 그룹 맨 위 주석에: VS Code Markdown 미리보기 전용, `display`가 `hidden`이면 그 섹션 목록은 빈 목록으로 동작, 두 목록이 모두 비거나 `enabled`가 `false`면 기능이 꺼짐, `collaboration` 항목은 그 노드가 의존하는 협력마다 표시, `targets`를 빼도 대상 줄은 붙음(FR-010, FR-018)

**Checkpoint**: quickstart Q1(기대 출력은 T025에서 확정)·V1·V2·V3·V5가 통과한다. 이 시점에서 기본 설정 hover는 완전히 동작한다.

---

## Phase 4: User Story 2 - hover 패널에 넣을 양을 설정으로 고르기 (Priority: P2)

**Goal**: 항목 목록·순서·위치·켜고 끄기·요청 재정의가 설정대로 동작한다.

**Independent Test**: quickstart Q3, Q6, Q7, V4, S2

- [X] T015 [US2] `apply_hover.py`에 명령줄 재정의 추가 — `--enabled=true|false`, `--responsibility=<항목,…>`, `--collaboration=<항목,…>`, `--position=bottom|node`. 값이 비면(`--responsibility=`) `[]`. 값은 T004의 검증 함수로 확인하고 잘못되면 설정 값을 쓰고 안내 한 줄. 설정 파일 값 위에 덮어 유효 설정을 만든다(research R4, FR-014, FR-020)
- [X] T016 [US2] `apply_hover.py`에 꺼짐 경로 구현 — contract "변환 규칙 (꺼짐)": 유효 설정이 꺼짐(`enabled` `false` 또는 두 목록 모두 `[]`)이거나 NodePanel이 하나도 없으면 링크 `click` 툴팁을 대상의 파일 이름(경로·URL의 마지막 조각, 폴더면 폴더 이름, `?`·`#` 뒤 제외)으로 되돌리고, `hoverOnly` 줄 삭제, `classDef` 끝 `,cursor:auto` 삭제, 패널 모양 블록과 그 앞 빈 줄 삭제. 출력 `hover 해제: <파일>`(바뀐 게 없으면 `변경 없음`) (FR-006, SC-005)
- [X] T017 [US2] `SKILL.md` Workflow·Output file에 요청 재정의 전달 규칙 추가 — 요청 문장이 hover 켜기/끄기, 넣을 항목·순서, 위치를 밝혔을 때만 해당 명령줄 옵션을 붙여 실행. 요청이 hover를 끄라고 하면(`--enabled=false`에 해당) 스크립트를 실행하지 않아도 된다(파일이 이미 기능 도입 전 형태). 유효 설정이 꺼짐인지는 `settings.jsonc`와 요청으로 판단 (FR-014, FR-020)
- [X] T018 [US2] `SKILL.md` "Settings" 절에 `itemList` 타입 규칙 한 줄 추가 — 값은 배열, 원소는 정의된 항목 문자열, 중복 없음, 빈 배열 허용, 어기면 그 옵션만 기본값 + 안내 (FR-009a)

**Checkpoint**: quickstart Q3·Q6·Q7·V4·S2가 통과한다.

---

## Phase 5: User Story 3 - 본문을 고친 뒤 패널 내용 다시 맞추기 (Priority: P3)

**Goal**: 본문만 고친 파일, 기능 도입 전 파일, 이미 적용된 파일에 스크립트를 다시 돌려도 결과가 맞고 멱등이다.

**Independent Test**: quickstart Q2, Q4, Q5, Q8

- [X] T019 [US3] `apply_hover.py` 멱등성 점검·보강 — 켜짐 결과에 같은 설정으로 다시 돌리면 바이트 단위로 같아야 한다(FR-003, SC-004). 확인할 것: `hoverOnly` 줄·`,cursor:auto`·패널 모양 블록을 지운 뒤 다시 만드는 순서가 줄 위치를 흔들지 않음, 파일 끝 빈 줄 수가 실행마다 늘거나 줄지 않음, CRLF 입력에서 LF가 섞이지 않음, 내용이 같으면 파일을 다시 쓰지 않음(수정 시각 유지)
- [X] T020 [US3] `apply_hover.py`가 본문만 바뀐 파일을 다시 계산하는지 점검 — 이미 툴팁이 채워진 링크 `click` 줄의 세 번째 인자를 기존 값과 상관없이 새 NodePanel로 덮고, 본문에서 노드 항목이 사라진 경우 그 노드의 해당 부분을 비우며 두 부분 모두 비면 파일 이름(링크 노드) 또는 `hoverOnly` 줄 삭제(링크 없는 노드)로 처리(Edge Case "본문에 해당 노드 항목이 없는 경우", US3 시나리오 1·3)
- [X] T021 [US3] `SKILL.md`에 "기존 구조 뷰 파일에 hover만 다시 맞추기" 안내 추가 — 사용자가 본문을 직접 고친 파일이나 기능 도입 전 파일을 지정하면, 구조 뷰를 다시 만들지 않고 `apply_hover.py <파일>`만 설정 값으로 실행한다(FR-004, US3). 이 경우 피드백 로그는 쓰지 않는다

**Checkpoint**: quickstart Q2·Q4·Q5·Q8이 통과한다.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T022 [P] `.claude/skills/generating-architecture-views/references/examples.md`의 예시 중 하나에 스크립트 실행 후 Dependency 코드 블록 끝부분과 파일 끝 `<style>` 블록이 어떻게 보이는지 덧붙인다(모델이 직접 쓰지 않는다는 문장 포함)
- [X] T023 [P] `docs/hover-tooltip-test/README.md`의 "파일" 절에 두 테스트 문서의 CSS가 `scripts/hover/style_blocks.py`의 원본이며, CSS를 바꿀 때는 두 곳을 같이 바꾼다는 한 줄 추가
- [X] T024 [P] `README.md`·`README.ko.md`의 hover·Python 요구 사항 설명이 구현 결과(실행 방식, 건너뜀 동작, 설정 키 이름)와 맞는지 확인하고 다르면 고친다
- [X] T025 `specs/009-hover-detail-panel/fixtures/`에 기대 출력 작성 — `view.default.expected.md`(기본 설정), `view.custom.expected.md`(`--responsibility=concrete,abstract --collaboration=questions --position=node`). 스크립트 출력을 그대로 베끼지 말고 contract와 data-model 규칙으로 노드마다 직접 대조해 확정한다(SC-003)
- [X] T026 quickstart.md 스크립트 시나리오 Q1~Q8을 Python 3.9(가능하면)와 최신 Python에서 실행해 통과 확인, 결과를 이 태스크 아래에 한 줄씩 기록
  - 결과(2026-11-14): Python 3.15·3.13에서 Q1(기본 설정 = `view.default.expected.md`)·Q2(두 번째 실행 변경 없음)·Q3(= `view.custom.expected.md`)·Q4(끄기 = `view.input.md`)·Q5(고친 노드만 바뀜)·Q6(Responsibility 없으면 그 부분 없음, 안내 없음)·Q7(중복 항목 → 기본값 + 안내 한 줄)·Q8(종료 코드 2, 파일 그대로) 통과. CRLF 입력·파일 끝 줄바꿈 없음도 왕복 통과. Python 3.9는 설치되어 있지 않아 `ast.parse(feature_version=(3,9))`로 문법 호환만 확인.
- [ ] T027 quickstart.md 화면 시나리오 V1~V6을 VS Code 1.146 미리보기에서 확인 — 특히 V5(`&quot;`가 따옴표로 보이고 다이어그램이 깨지지 않는지). 안 되면 research R8 대안(`“ ”`)으로 `panel_text.py`를 고치고 T025·T026을 다시 한다
- [ ] T028 quickstart.md 내보내기 시나리오 E1·E2와 스킬 전체 시나리오 S1~S4 확인(S4는 PATH에서 Python을 뺀 셸에서)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 바로 시작
- **Foundational (Phase 2)**: Setup 뒤. T004·T005·T006은 동시에, T007은 T003(입력 파일로 확인) 뒤
- **US1 (Phase 3)**: Foundational 뒤. T008 → T009 → (T010·T011·T012는 같은 SKILL.md라 순서대로) / T013·T014는 T005 뒤 언제든
- **US2 (Phase 4)**: T009 뒤. T015 → T016, T017·T018은 T010 뒤(같은 SKILL.md)
- **US3 (Phase 5)**: T016 뒤(꺼짐 경로와 다시 계산이 같은 코드를 지남). T021은 T017 뒤
- **Polish (Phase 6)**: 모든 스토리 뒤. T025 → T026 → T027 → T028

### User Story Dependencies

- **US1**: Foundational만 필요 — 단독으로 MVP
- **US2**: US1의 `apply_hover.py` 위에 옵션·꺼짐 경로를 더함
- **US3**: US2의 꺼짐 경로를 재사용(되돌리기 시나리오 Q4)

### Parallel Opportunities

- T002·T003 / T004·T005·T006 / T013·T014 / T022·T023·T024

## Parallel Example: User Story 1

```text
T008(panel_text.py) 진행 중에 동시에:
  T013 references/templates.md 예시
  T014 settings.jsonc hover 그룹
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1·2 완료
2. Phase 3(US1) 완료 → 기본 설정으로 구조 뷰를 만들어 VS Code에서 V1·V2 확인
3. 여기서 멈춰도 핵심 문제(시선 전환 피로)는 해결된다

### Incremental Delivery

1. US1 → 기본 hover
2. US2 → 항목·순서·위치·끄기·요청 재정의
3. US3 → 본문 수정 후 다시 맞추기, 멱등·되돌리기 보장
4. Polish → 기대 출력 확정과 전체 시나리오 확인

## Notes

- SKILL.md를 고치는 태스크(T010·T011·T012·T017·T018·T021)는 같은 파일이라 [P]가 없다
- 각 Checkpoint에서 커밋한다(커밋 메시지 규칙은 AGENTS.md)

## Phase 7: Convergence

- [X] T029 Give `bottom` panel columns a minimum height of 3 lines so content of 3 lines or fewer flows in one column (update BOTTOM in `.claude/skills/generating-architecture-views/scripts/hover/style_blocks.py`, its source of truth `docs/hover-tooltip-test/inline-style.md`, and `specs/009-hover-detail-panel/fixtures/view.default.expected.md` together) per FR-005 (missing)

## Phase 8: Convergence

- [X] T030 Change the `hover.collaboration` default to `["targets", "boundary", "rationale", "questions"]` in `.agents/skills/generating-architecture-views/settings.schema.json` and `settings.jsonc`, and note FR-009b in its jsonc comment per FR-009, FR-009b (contradicts)
- [X] T031 Regenerate `specs/009-hover-detail-panel/fixtures/view.default.expected.md` for the new default and confirm quickstart Q1–Q4 still pass per FR-009, SC-003 (contradicts)

## Phase 9: 규격 표시 노드 hover 연결 (FR-021, SC-008)

**Purpose**: 003 FR-036의 규격 표시어가 Dependency 라벨에 붙어도 이름만 쓰는 본문과 hover 패널을 연결한다.

**Independent Test**: quickstart Q1–Q4와 Q9를 실행해 기존 기대 출력, 멱등, 끄기 복원, 규격 표시 노드 연결을 확인한다.

- [ ] T032 [US1] `specs/009-hover-detail-panel/fixtures/view.input.md`의 `CartStore` 라벨을 `class&nbsp;CartStore` 규격 표시 사례로 바꾸고 `view.default.expected.md`·`view.custom.expected.md`의 대응 선언을 맞춘 뒤, 현재 `apply_hover.py` 결과가 기대 출력과 달라지는지 확인한다 per FR-021
- [ ] T033 [US1] `.agents/skills/generating-architecture-views/scripts/hover/view_parser.py`의 `clean_name`이 변화 표시·HTML 태그를 제거한 원본 라벨에서 마지막 `&nbsp;` 뒤 이름을 반환하게 하고 quickstart Q1–Q4·Q9를 실행한다 per FR-021, SC-003, SC-004, SC-005, SC-008

**Dependencies**: T032 → T033.
