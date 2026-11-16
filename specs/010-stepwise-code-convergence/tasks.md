# Tasks: 꾸며낸 최소 코드에서 원본 코드까지 단계별로 구체화해 보여 주기

**Input**: Design documents from `specs/010-stepwise-code-convergence/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/stages-contract.md, quickstart.md

**Tests**: 별도 테스트 태스크는 없다. spec이 요청하지 않았다. 검증은 각 Checkpoint와 Polish 단계에서 quickstart 시나리오로 한다.

**공통 제약**(모든 태스크에 적용):

- **실행 환경**: Python 3.9 이상에서 동작하고, 표준 라이브러리만 쓴다. 3.10 이상 전용 문법(`match`, 런타임 `X | Y` 타입 표기)은 쓰지 않는다.
- **파일 입출력**: 파일은 UTF-8로 읽고 쓴다. 스크립트가 쓰는 문서와 작업 파일은 LF로 쓰고, 줄바꿈 하나로 끝낸다.
- **경계**: 원본 코드베이스와 구조 뷰 파일은 읽기만 한다(FR-019). 다른 스킬의 코드는 import하지 않는다(research R2·R12).
- **스킬 경로**: `.claude/skills/revealing-code-step-by-step/` (이하 `SK/`)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 다른 파일을 고치고, 아직 끝나지 않은 태스크에 기대지 않아 동시에 할 수 있음
- **[Story]**: US1·US2·US3 (spec.md의 User Story)

---

## Phase 1: Setup

- [ ] T001 `.gitignore`에 `!.claude/skills/revealing-code-step-by-step/`를 기존 스킬 허용 줄 옆에 추가한다. 그다음 새 파일 `SK/SKILL.md`, `SK/stages.md`, `SK/settings.jsonc`, `SK/settings.schema.json`, `SK/scripts/stages.py`, `specs/010-stepwise-code-convergence/fixtures/*`가 추적 대상인지 `git check-ignore -v --no-index`로 확인한다.
- [ ] T002 [P] 폴더를 만든다: `SK/scripts/`, `specs/010-stepwise-code-convergence/fixtures/{src,work,expected/original}/`.

---

## Phase 2: Foundational (모든 스토리의 전제)

- [ ] T003 **diff 층 줄 맞춤 확인** (research R7의 위험을 먼저 없앰). `specs/010-stepwise-code-convergence/prototype/code-gallery.md`에 diff 층을 덧붙인다.
  - **덧붙이는 방법**:
    - 2단계·3단계마다 `.code` 안의 코드 블록 뒤에 `<pre class="diff" aria-hidden="true"><code>`를 넣는다. 줄마다 span을 하나 두고, 그 줄의 코드 글자를 이스케이프해 투명하게 담는다.
    - 추가·변경·삭제 줄을 각각 하나 이상 표시한다.
    - 문서 끝에 두 번째 `<style>`을 둔다. 내용은 `.code`를 기준점으로 삼는 규칙, `pointer-events: none`, `add`·`mod`·`del` 색이다. 색은 `--vscode-editorGutter-*` 테마 변수에 대체 색을 함께 적는다.
    - 기존 상자의 마크업과 첫 번째 `<style>`은 바꾸지 않는다. 기존 상자에 `.code` 감싸개가 없으면 이것만 기존 상자의 몫으로 더한다.
  - **확인 방법**: 이 세션에서 쓴 방식으로 실제 VS Code 미리보기 DOM을 읽는 작은 Node 스크립트를 scratchpad에 둔다. 별도 프로필, `--remote-debugging-port`, 웹뷰 iframe의 `Runtime.evaluate`를 쓴다. 이 스크립트로 다음 셋을 확인한다.
    - (a) 줄마다 코드 줄과 diff 층 줄의 `getBoundingClientRect().top`이 같다.
    - (b) 세로·가로 스크롤 뒤에도 (a)가 같다.
    - (c) diff 층을 지운 문서의 DOM이 기존 상자와 같다.
  - **어긋날 때**: diff 층 CSS에서만 고친다. 그래도 맞출 수 없으면 멈추고 사용자에게 보고한다(R7 대안).
- [ ] T004 [P] `SK/stages.md`를 작성한다(contract 1절).
  - **머리**: 맨 위 자유 설명에 세 가지를 짧게 적는다. 1원칙(추상 → 구체), 구체화 사다리 표(spec FR-012a 요약), spec 링크다.
  - **단계**: spec FR-008의 7단계 표와 표 아래 문단을 단계마다 `## <별명>` + `- 원본과 같아지는 것:` + `- 아직 드러나지 않은 것:` 형태로 옮긴다.
  - **보조 표기**: 2단계에는 "- 보조 표기: 1단계에서 지어낸 본문과 멤버를 `⟨그 코드가 하던 일⟩`이나 `...`으로 바꾼다" 항목을 둔다. 3~6단계에는 그 단계에서 사다리 칸을 올리는 범위를 적는다.
- [ ] T005 [P] `specs/010-stepwise-code-convergence/spec.md`의 FR-008을 고친다. 7단계 표와 표 아래 문단, "이 표는 … 초안이다" 문장을 지우고, 그 자리에 `SK/stages.md`의 링크와 "단계 정의 파일의 처음 내용은 7단계이며, 첫 단계와 마지막 단계는 FR-003~005, FR-010으로 고정"이라는 한 줄만 남긴다. T004가 끝난 뒤에 한다.
- [ ] T006 [P] `SK/settings.schema.json`을 작성한다. 형식은 기존 스킬의 `options` 배열이다. 옵션은 둘이다.
  - `stages`: type `stageToggles`, default `{}`, 한국어 description, tokenImpact `{"true": "[0]", "false": "[-]"}`
  - `output.directory`: type `relativePath`, base `viewFileDir`, default `"."`, tokenImpact `{"*": "[0]"}`

  research R12를 따른다.
- [ ] T007 [P] `SK/settings.jsonc`를 작성한다.
  - **머리 주석**: 007 관례를 따른다. 첫 줄은 요청 우선 문구, 둘째 줄은 토큰 기호 범례다.
  - **`stages`**: 마지막 단계를 뺀 6단계를 `stages.md` 순서대로 모두 `true`로 둔다. 주석에는 다음을 적는다.
    - `true`/`false`의 뜻과 기호
    - 끈 단계는 다음 단계에 합쳐짐
    - 첫 단계는 화면에만 안 보임
    - 마지막 단계는 항상 보임
    - 여기에 없는 단계는 `true`
  - **`output.directory`**: `"."`로 두고, 주석에는 구조 뷰 폴더 기준 상대 경로, 절대 경로 불가, 그 안에 `<slug>.stages/`가 생긴다는 것을 적는다. 프로젝트 빌드 대상(소스 폴더) 안을 고르면 결과가 빌드에 섞일 수 있으니 고르지 말라는 한 줄도 적는다(spec FR-019).

  research R12의 jsonc 예시를 그대로 쓴다.
- [ ] T008 `SK/scripts/stages.py`의 공통 부분을 작성한다. 하위 명령은 아직 비워 두고 아래 함수들만 만든다.
  - (1) **설정 로더**: 기존 스킬 로더와 같은 동작이다. 주석 허용 JSON, 파일 없음 → 기본값, 읽지 못함 → 모든 기본값 + 안내, 형식 위반 → 그 키만 기본값 + 안내, 정의에 없는 키 → 무시 + 안내. 안내 형식은 `⚙️ 설정 안내: settings.jsonc — …`이다.
    - `stageToggles` 검증: 값이 불리언이 아닌 단계는 `true` + 안내, 단계 정의에 없는 별명은 무시 + 안내, 마지막 단계 별명은 무시 + "마지막 단계는 항상 보임" 안내
    - `relativePath` 검증: 절대 경로와 드라이브 문자를 거부한다.
  - (2) **`stages.md` 파서**: `## ` 제목과 정확한 항목 머리 두 개, 선택 `- 보조 표기:`를 읽는다. 단계 2개 미만, 별명 겹침, 필수 항목 없음은 종료 코드 2다(contract 1절).
  - (3) **구조 뷰 파서**(research R2): `### Dependency` 아래 Mermaid 블록에서 다음을 읽는다.
    - 그룹: `subgraph Id["라벨"]`/`end` 중첩을 그룹 경로로 읽는다.
    - 노드 선언: 맨 `Id`, `Id@{ label: "…" }`, `Id["…"]` 세 형태와 선언 순서를 읽는다.
    - 표시 이름: ✨·♻️·🗑️, `&nbsp;`, `<b>`·`<s>`를 정규화한다.
    - 링크: `click Id "대상" "라벨"`을 링크로 읽고, `click Id hoverOnly "…"`는 링크 없음으로 본다.
    - 형식 오류와 노드 없음은 종료 코드 2다.
  - (4) **원본 읽기**(research R8): 로컬 경로는 구조 뷰 폴더 기준으로 읽는다. `http(s)`는 `urllib.request`로 받고, `github.com/…/blob/…`는 raw 주소로 바꾼다. contract 2절 표의 `skip_reason` 문구를 정확히 쓴다.
  - (5) **선언 구간 찾기**(research R5): 문자열(`"…"`, `"""…"""`, 문자 리터럴)·주석·괄호 깊이만 아는 스캐너다.
    - 머리: 주석과 문자열 밖에서 `class|interface|object|fun|typealias|val|var` 뒤에 이름이 오는 곳을 찾는다. `companion object`, `fun <T>`, 확장 함수 수신자를 포함한다.
    - 찾은 수: 0개 또는 2개 이상이면 `skip_reason`을 정한다.
    - 시작: 바로 위의 KDoc·주석·어노테이션 줄로 넓힌다. 빈 줄을 만나면 멈춘다.
    - 끝: 첫 `{`와 짝 `}`가 있는 줄, 또는 괄호 깊이 0에서 문장이 끝나는 줄이다. 이어지는 줄 판단은 `.`·`?.`·`?:`·`&&`·`||`로 한다.
    - 반환: `(start_line, end_line, text)`. 바이트를 그대로 잘라낸다.
  - (6) **만들 단계 목록**(research R13): 단계마다 `work`·`visible`·`display`·`of`·`merged`를 정한다. 입력은 단계 정의, 설정, 요청 옵션 `--show`/`--hide`다.
  - (7) **문서 나누기**: data-model.md의 Document 규칙 1~3이다.
  - (8) **출력**: JSON 한 줄을 출력하는 도우미다. stdout은 UTF-8로 맞춘다.

**Checkpoint**: 다음 세 가지가 확인되면 이 단계를 마친다.

- T003으로 diff 층의 줄이 실제 미리보기에서 맞는다.
- `stages.md`, `settings.jsonc`, 스키마를 로더와 파서가 오류 없이 읽는다.
- 선언 구간 찾기가 `fixtures/src/`의 모든 경우(T009)를 맞게 잘라낸다.

---

## Phase 3: User Story 1 - 꾸며낸 최소 코드로 구조를 먼저 손에 쥐기 (Priority: P1) 🎯 MVP

**Goal**: 구조 뷰 하나로 `prepare`를 실행하고, 격리된 서브에이전트가 1단계 코드를 쓴다. `build`는 노드마다 상자가 있는 문서를 만들고 마지막 단계를 원본 범위와 확인한다. 중간 단계 작업 파일은 fixture가 제공한다.

**Independent Test**: quickstart Q1, Q3(diff 층 제외), Q4, Q7의 1단계 항목(SC-001, SC-002)

- [ ] T009 [P] [US1] `specs/010-stepwise-code-convergence/fixtures/`에 입력을 작성한다(quickstart "준비").
  - **`view.architecture.md`**: 노드 7개로 이뤄진 구조 뷰다.
    - 그룹: 최상위 그룹 2개(노드 3개, 2개)와 그룹 없는 노드 1개로 나뉜다.
    - 링크(노드별 원본 위치):

      | 노드 수 | 링크가 가리키는 곳 |
      |---|---|
      | 2 | 같은 파일 `src/Order.kt` 안의 서로 다른 클래스 |
      | 1 | `Order.kt` 안 클래스의 중첩 클래스 |
      | 1 | 표현식 본문 함수가 있는 `src/Util.kt` |
      | 1 | 링크 없음 |
      | 1 | `src/Legacy.java` |
      | 1 | 선언이 없는 `src/Missing.kt` |
  - **`src/`**: KDoc·어노테이션이 붙은 선언, 문자열 안의 `{`, `"""` 문자열을 넣는다. `Util.kt`는 CRLF로 저장한다.
  - **`expected/original/*.kt`**: 손으로 잘라낸 원본 범위 4개다.
- [ ] T010 [US1] `SK/scripts/stages.py prepare`를 구현한다(contract 2절 `prepare`).
  - **입력 검사**: `*.architecture.md`인지와 Dependency 블록이 있는지 확인한다.
  - **산출 폴더**: `--output-dir`가 설정 `output.directory`보다 우선한다. 산출 폴더 `<view 폴더>/<output.directory>/<slug>.stages/`만 지우고 새로 만든다(FR-019a, FR-020).
  - **만들 단계 목록**: T008(6)으로 정한다.
  - **노드마다 원본 범위**: `work/original/<id>.kt`에 저장한다. 끝은 줄바꿈 하나다.
  - **`contains`**: 이 노드의 원본 범위 안에 든 다른 노드의 Id 목록이다.
  - **`work/manifest.json`과 출력 JSON**: `dir`, `stages`, `notices`, `nodes[]`를 담는다. `nodes[]`의 항목은 `id`·`name`·`stage1`·`original`·`range`·`contains`·`skip_reason`·`doc`다.
  - **종료 코드**: 0이나 2다.
- [ ] T011 [US1] `SK/scripts/stages.py build`의 기존 상자 부분을 구현한다(contract 2절 `build` 1~5와 3절). diff 층은 T017에서 덧붙인다.
  - **누락 검사**: 빠진 작업 파일이 있으면 종료 코드 2다.
  - **문서 구성**:
    - 문서마다 제목과 그룹 라벨 소제목을 둔다.
    - 노드마다 `### 이름`과, 구체화하지 않는 노드는 `⚠️ <skip_reason>` 줄을 둔다.
    - 상자: 라디오는 `name`/`id`를 노드 Id로, 클래스는 `sK`로 만든다. 보이는 단계마다 `.stage sK`를 두고, 그 안에 `.head`(제목 `<display>단계: <별명> (<display>/<of>)`, ← → `<label>` 또는 흐린 `<span>`)와 `.note`(한 줄 설명, R13 6), `.code` 안의 코드 블록을 둔다. 펜스는 가장 긴 백틱 연속 + 1이고, 최소 3이다.
    - 문서 끝에 기존 상자 `<style>`을 둔다. 내용은 T003에서 확정한 시제품 규칙과 단계 수만큼의 `input.sK:checked ~ .stage.sK` 규칙이다.
  - **마지막 단계 확인**: 문서를 다시 읽어 마지막 단계 코드를 꺼낸다. 원본 위치에서 다시 읽어 다시 잘라낸 구간과 LF 기준으로 비교한다. 다르면 종료 코드 3과 노드·첫 다른 줄을 출력한다(FR-010).
  - **출력 JSON**: `docs`, `unchanged`, `skipped`, `verified`를 담는다.
- [ ] T012 [US1] `SK/SKILL.md`를 처음 작성한다.
  - **frontmatter**: `name: revealing-code-step-by-step`. description은 영어로 쓴다. "구조 뷰(.architecture.md)를 받아 노드별 Kotlin 코드를 지어낸 최소 코드에서 원본까지 정제 단계로 넘겨 보는 문서를 만든다"는 내용과 사용·비사용 조건을 담는다.
  - **Workflow**: 다섯 단계를 적는다.
    1. 인터프리터를 찾는다. 순서는 기존 스킬과 같다(`python3` → `python` → `py -3`, Windows는 `python` → `py -3` → `python3`).
    2. `prepare`를 실행한다. 요청에 단계 보이기나 위치가 적혀 있으면 `--show`/`--hide`/`--output-dir`를 넘긴다.
    3. 1단계 서브에이전트를 띄운다.
    4. 중간 단계를 만든다. T015에서 채울 자리만 남긴다.
    5. `build`를 실행한다. 이어서 응답에 문서 링크, 구체화하지 않은 노드 목록, `⚙️` 알림만 담는다.
  - **1단계 서브에이전트 절**(research R1): Agent 도구, 새 general-purpose, fork 금지라고 적는다. 프롬프트 틀을 그대로 싣는다. 틀에는 다음이 들어간다.
    - 넣을 것: 구조 뷰 파일 전문, `stages.md` 첫 단계 정의, FR-004·005 규칙, 노드 Id → 쓸 경로 목록
    - 지시: "Write만 쓰고 Read·Grep·Glob·Bash·웹 도구 금지", "원본과 같은 이름은 우연이어야 함"
  - **멈추는 경우**:
    - Python 3.9 이상이 없을 때: 만들지 않고 이유를 한 줄로 알린다.
    - 서브에이전트를 쓸 수 없을 때: 만들지 않고 이유를 알린다.
    - 종료 코드 2·3일 때: contract 4절을 따른다.
- [ ] T013 [US1] `specs/010-stepwise-code-convergence/fixtures/work/`에 손으로 쓴 작업 파일을 둔다.
  - 1단계: 노드 7개 파일
  - 2~6단계: 구체화하는 노드 4개 파일. 2단계에는 `⟨설명⟩`·`...`를 넣는다. 4단계에는 FR-011a처럼 다른 노드의 호출 이름을 맞춘 예를 넣는다. 바깥 노드 파일에는 중첩 노드를 `⟨이름⟩`으로 접는다. 한 단계는 어떤 노드에서 일부러 바꾸지 않는다.

  T010을 실행해 나온 경로에 맞춘다.

**Checkpoint**: quickstart Q1, Q4가 통과한다. Q3는 diff 층을 뺀 기대 문서 `expected/*.base.md` 기준으로 통과한다. 이 시점에 1단계와 원본, 그리고 fixture의 중간 단계를 넘겨 볼 수 있다.

---

## Phase 4: User Story 2 - 단계를 올려 가며 원본에 가까워지는 모습을 지켜보기 (Priority: P1)

**Goal**: 모델이 `begin`으로 받은 복사본을 단계 정의대로 고쳐 중간 단계를 만든다. 문서에는 달라진 줄이 git 변경 색으로 칠해진다.

**Independent Test**: quickstart Q2, Q3(diff 층 포함), Q6, Q7(US2 항목)

- [ ] T014 [US2] `SK/scripts/stages.py begin <dir> <k>`를 구현한다(contract 2절 `begin`).
  - **검사**: `2 ≤ k ≤ g-1`인지, `work/<k-1>`이 있는지, `work/<k>`가 없는지 확인한다. 어긋나면 종료 코드 2다.
  - **복사**: 구체화하는 노드마다 `work/<k-1>/<id>.kt`를 `work/<k>/<id>.kt`로 복사한다. 폴더 번호는 두 자리다.
  - **출력**: 그 단계의 `nickname`·`becomes`·`unrevealed`·`notation`·`merged`·`files`를 JSON으로 낸다.
- [ ] T015 [US2] `SK/SKILL.md`의 중간 단계 절을 쓴다(research R11, contract 4절 3).
  - **루프**: k = 2…g-1마다 `begin k`를 실행하고, 출력된 정의와 `merged`의 몫을 원본 `work/original/`에 맞춰 Edit로 고친다.
  - **규칙** 다섯 가지를 각각 한 문단으로, 짧은 Kotlin 예와 함께 적는다.
    1. 정의된 측면과 보조 표기만 바꾼다(FR-011).
    2. 드러난 이름은 다른 노드 파일에서도 같은 단계에 맞춘다(FR-011a).
    3. 구체화 사다리를 내려가지 않는다. 드러난 원본 줄의 글자를 바꾸거나 `...`로 가리지 않는다(FR-012, FR-012a).
    4. 2단계에서는 지어낸 본문을 `⟨설명⟩`/`...`로 바꾼다. `⟨⟩`는 U+27E8·U+27E9로 쓴다.
    5. `contains`에 든 노드는 `⟨이름⟩`으로 접는다.
  - **자기 점검**: 다음 `begin` 전에 위 다섯 가지를 확인한다. 지난 단계는 고치지 않는다.
- [ ] T016 [US2] `SK/SKILL.md`에 "Self-check" 목록을 추가한다. 항목은 다음과 같다. 서술하지 말고 확인만 한다.
  - 1단계 프롬프트에 원본 정보가 없다.
  - 노드 이름이 구조 뷰와 같다.
  - 단계마다 R11의 다섯 규칙을 지켰다.
  - 응답이 링크와 허용된 줄만 담는다.
- [ ] T017 [US2] `SK/scripts/stages.py build`에 diff 층을 덧붙인다(research R7, contract 3절).
  - **함수 분리**: 기존 상자를 그리는 함수(T011)는 고치지 않는다. 새 함수 `diff_lines(prev, cur)`와 `render_diff_layer(code, kinds)`만 더한다.
  - **`diff_lines`**: `SequenceMatcher` opcode로 줄마다 종류를 정한다. `insert` → `add`, `replace`의 짝 → `mod`, 남는 새 줄 → `add`, `delete`나 남는 옛 줄 → 다음 줄에 `del`(끝이면 마지막 줄에 `del-after`)이다.
  - **`render_diff_layer`**: `pre.diff > code`를 만든다. 줄마다 span을 두고, 그 줄의 이스케이프한 글자를 투명하게 담는다.
  - **넣는 자리**: 1단계, 직전에 보이는 단계와 같은 단계, 처음 보이는 단계에는 넣지 않는다(R13 7). 그 밖의 단계는 `.code` 안 코드 블록 바로 뒤에 넣는다.
  - **스타일**: 문서 끝에 두 번째 `<style>`(T003에서 확정한 diff 층 규칙)을 둔다.
  - **분리 검사**: `pre.diff` 요소들과 두 번째 `<style>`을 지운 결과가 diff 층 없이 만든 문서와 같은지 확인하는 내부 검사 함수를 둔다. Q3에서 쓴다.

**Checkpoint**: quickstart Q2, Q3(`expected/*.md`와 `*.base.md` 둘 다), Q6이 통과한다. 이 시점에 정제 단계 기능 전체가 동작한다.

---

## Phase 5: User Story 3 - 단계 정의를 고쳐 다른 순서·다른 단계로 다시 만들기 (Priority: P2)

**Goal**: 단계 정의를 고치거나 설정으로 단계를 끄고 켜도, 단계 정의 한 곳(또는 설정 한 곳)만 고쳐서 바뀐 구성으로 결과를 받는다.

**Independent Test**: quickstart Q5, Q5a

- [ ] T018 [US3] `SK/scripts/stages.py prepare`·`begin`·`build`의 끈 단계 처리를 끝까지 확인하고 보완한다(research R13).
  - 첫 단계가 꺼지면 만들기는 하되 `visible: false`이고 문서에 나오지 않는다. 처음 보이는 단계가 `1/<of>`다.
  - 첫 단계가 아닌 끈 단계는 목록에서 빠지고, 다음 단계의 `merged`에 쌓인다(연속이면 차례로).
  - 한 줄 설명은 `원본과 같아진 것: <합쳐진 becomes들>; <자기 becomes>`다.
  - `--show`·`--hide`는 그 실행에서만 설정보다 우선한다.
- [ ] T019 [US3] `SK/SKILL.md`에 "Stage definition and settings" 절을 추가한다.
  - 단계 구성은 `stages.md`에서 고친다(삽입·삭제·순서 변경, 첫 단계와 마지막 단계는 고정).
  - 보이기는 `settings.jsonc`의 `stages`에서, 결과 위치는 `output.directory`에서 정한다.
  - 요청에 적힌 값은 그 요청에서만 우선하며, 옵션으로 넘긴다.
  - 모델은 `stages.md`와 `settings.jsonc`를 직접 읽지 않고 `prepare`·`begin` 출력만 쓴다. `stages.md`는 1단계 서브에이전트 프롬프트에 첫 단계 정의를 넣을 때만 출력에서 가져온다.

**Checkpoint**: quickstart Q5(8단계로 바꾼 정의), Q5a(설정 끄기·알림·요청 우선·결과 위치)가 통과한다.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T020 `specs/010-stepwise-code-convergence/fixtures/expected/`의 기대 문서를 확정한다.
  - `<그룹 Id>.md`, `others.md`, 그리고 같은 이름의 `*.base.md`(diff 층 없음)를 둔다.
  - T011·T017 결과를 한 줄씩 검토해 contract 3절과 맞는지 확인하고 확정한다.
  - 확정한 뒤 Q3를 바이트 비교로 다시 돌린다.
- [ ] T021 [P] `README.md`와 `README.ko.md`의 "Optional add-ons/추가 기능"에 `revealing-code-step-by-step` 항목을 추가한다. 담을 내용은 다음과 같다.
  - 무엇을 하는지(구조 뷰 → 노드별 정제 단계 문서)
  - VS Code 미리보기에서 ← →로 넘김, 달라진 줄의 git 색
  - `stages.md`로 단계 구성을 바꾸고 `settings.jsonc`로 보이기와 위치를 정함
  - GitHub에서는 단계가 나열됨

  "Requirements/요구 사항"에는 Python 3.9 이상이 필요하고 없으면 만들지 않는다고 적는다.
- [ ] T022 quickstart Q1~Q6을 처음부터 다시 돌려 모두 통과하는지 확인한다. 실패한 시나리오가 있으면 해당 태스크로 돌아가 고친다.
- [ ] T023 quickstart Q7을 실행한다. 실제 구조 뷰 `.zenuml/swemo-architecture.architecture.md`로 스킬을 요청하고 다음을 확인한다.
  - 1단계 서브에이전트 프롬프트와 도구 사용(SC-002)
  - 1단계 이름과 의존(SC-001)
  - 2단계 보조 표기
  - 이름 맞추기(FR-011a)
  - `verified` 수(SC-003)
  - 원본 저장소와 구조 뷰의 변경 없음(SC-008)

  몇 개 노드는 미리보기에서 넘겨 보며 FR-011·FR-012를 눈으로 확인한다. 결과는 사용자에게 보고한다.

---

## Dependencies & Execution Order

- **Setup (T001–T002)**: 바로 시작한다.
- **Foundational (T003–T008)**:
  - T003(diff 층 확인)은 다른 태스크와 독립이다. 결과가 T011·T017의 CSS를 정하므로 가장 먼저 한다.
  - T004 → T005 순서다(표를 옮긴 뒤 spec에서 지움).
  - T006·T007은 동시에 할 수 있다.
  - T008은 T004·T006(파서·로더가 읽을 형식)에 기댄다.
- **US1 (T009–T013)**: Foundational이 끝나야 한다. T009는 T008과 동시에 할 수 있다. 순서는 T010 → T011 → T012, T013(T010 출력 경로 필요)이다.
- **US2 (T014–T017)**: US1에 기댄다(같은 `stages.py`와 `SKILL.md`). 순서는 T014 → T015 → T016이고, T017은 T011 뒤에 언제든 할 수 있다.
- **US3 (T018–T019)**: US2에 기댄다(`begin`과 합쳐진 몫의 편집).
- **Polish (T020–T023)**: 모든 스토리 뒤에 한다. T021은 언제든 할 수 있다.

## Parallel Opportunities

- Setup·Foundational: T002와 T004·T006·T007은 서로 다른 파일이다.
- US1: T009(fixture)는 T010과 동시에 할 수 있다.
- Polish: T021(README)은 다른 태스크와 동시에 할 수 있다.
- `stages.py`와 `SKILL.md`를 고치는 태스크는 같은 파일이라 순서대로 한다.

## Implementation Strategy

1. **위험 먼저**: T003으로 diff 층의 줄 맞춤을 실제 미리보기에서 먼저 확인한다. 실패하면 설계(R7 대안)를 사용자와 정한 뒤 진행한다.
2. **MVP = US1**: `prepare`, 1단계 서브에이전트, `build`의 기존 상자까지 만들면, fixture 작업 파일로 단계 넘겨 보기와 원본 확인이 동작한다.
3. **US2**: 모델이 중간 단계를 직접 만드는 루프와 diff 층을 더해 기능을 완성한다.
4. **US3**: 단계 정의 수정과 설정 끄기의 합치기·번호 매기기를 완성하고 확인한다.
5. **Polish**: 기대 문서를 확정하고, README를 갱신하고, 실제 구조 뷰로 끝까지 확인한다.
