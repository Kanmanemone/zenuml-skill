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

- [X] T001 `.gitignore`에 `!.claude/skills/revealing-code-step-by-step/`를 기존 스킬 허용 줄 옆에 추가한다. 그다음 새 파일 `SK/SKILL.md`, `SK/stages.md`, `SK/settings.jsonc`, `SK/settings.schema.json`, `SK/scripts/stages.py`, `specs/010-stepwise-code-convergence/fixtures/*`가 추적 대상인지 `git check-ignore -v --no-index`로 확인한다.
- [X] T002 [P] 폴더를 만든다: `SK/scripts/`, `specs/010-stepwise-code-convergence/fixtures/{src,work,expected/original}/`.

---

## Phase 2: Foundational (모든 스토리의 전제)

- [X] T003 **diff 층 줄 맞춤 확인** (research R7의 위험을 먼저 없앰). `specs/010-stepwise-code-convergence/prototype/code-gallery.md`에 diff 층을 덧붙인다.
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
- [X] T004 [P] `SK/stages.md`를 작성한다(contract 1절).
  - **머리**: 맨 위 자유 설명에 세 가지를 짧게 적는다. 1원칙(추상 → 구체), 구체화 사다리 표(spec FR-012a 요약), spec 링크다.
  - **단계**: spec FR-008의 7단계 표와 표 아래 문단을 단계마다 `## <별명>` + `- 원본과 같아지는 것:` + `- 아직 드러나지 않은 것:` 형태로 옮긴다.
  - **보조 표기**: 2단계에는 "- 보조 표기: 1단계에서 지어낸 본문과 멤버를 `⟨그 코드가 하던 일⟩`이나 `...`으로 바꾼다" 항목을 둔다. 3~6단계에는 그 단계에서 사다리 칸을 올리는 범위를 적는다.
- [X] T005 [P] `specs/010-stepwise-code-convergence/spec.md`의 FR-008을 고친다. 7단계 표와 표 아래 문단, "이 표는 … 초안이다" 문장을 지우고, 그 자리에 `SK/stages.md`의 링크와 "단계 정의 파일의 처음 내용은 7단계이며, 첫 단계와 마지막 단계는 FR-003~005, FR-010으로 고정"이라는 한 줄만 남긴다. T004가 끝난 뒤에 한다.
- [X] T006 [P] `SK/settings.schema.json`을 작성한다. 형식은 기존 스킬의 `options` 배열이다. 옵션은 둘이다.
  - `stages`: type `stageToggles`, default `{}`, 한국어 description, tokenImpact `{"true": "[0]", "false": "[-]"}`
  - `output.directory`: type `relativePath`, base `viewFileDir`, default `"."`, tokenImpact `{"*": "[0]"}`

  research R12를 따른다.
- [X] T007 [P] `SK/settings.jsonc`를 작성한다.
  - **머리 주석**: 007 관례를 따른다. 첫 줄은 요청 우선 문구, 둘째 줄은 토큰 기호 범례다.
  - **`stages`**: 마지막 단계를 뺀 6단계를 `stages.md` 순서대로 모두 `true`로 둔다. 주석에는 다음을 적는다.
    - `true`/`false`의 뜻과 기호
    - 끈 단계는 다음 단계에 합쳐짐
    - 첫 단계는 화면에만 안 보임
    - 마지막 단계는 항상 보임
    - 여기에 없는 단계는 `true`
  - **`output.directory`**: `"."`로 두고, 주석에는 구조 뷰 폴더 기준 상대 경로, 절대 경로 불가, 그 안에 `<slug>.stages/`가 생긴다는 것을 적는다. 프로젝트 빌드 대상(소스 폴더) 안을 고르면 결과가 빌드에 섞일 수 있으니 고르지 말라는 한 줄도 적는다(spec FR-019).

  research R12의 jsonc 예시를 그대로 쓴다.
- [X] T008 `SK/scripts/stages.py`의 공통 부분을 작성한다. 하위 명령은 아직 비워 두고 아래 함수들만 만든다.
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

- [X] T009 [P] [US1] `specs/010-stepwise-code-convergence/fixtures/`에 입력을 작성한다(quickstart "준비").
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
- [X] T010 [US1] `SK/scripts/stages.py prepare`를 구현한다(contract 2절 `prepare`).
  - **입력 검사**: `*.architecture.md`인지와 Dependency 블록이 있는지 확인한다.
  - **산출 폴더**: `--output-dir`가 설정 `output.directory`보다 우선한다. 산출 폴더 `<view 폴더>/<output.directory>/<slug>.stages/`만 지우고 새로 만든다(FR-019a, FR-020).
  - **만들 단계 목록**: T008(6)으로 정한다.
  - **노드마다 원본 범위**: `work/original/<id>.kt`에 저장한다. 끝은 줄바꿈 하나다.
  - **`contains`**: 이 노드의 원본 범위 안에 든 다른 노드의 Id 목록이다.
  - **`work/manifest.json`과 출력 JSON**: `dir`, `stages`, `notices`, `nodes[]`를 담는다. `nodes[]`의 항목은 `id`·`name`·`stage1`·`original`·`range`·`contains`·`skip_reason`·`doc`다.
  - **종료 코드**: 0이나 2다.
- [X] T011 [US1] `SK/scripts/stages.py build`의 기존 상자 부분을 구현한다(contract 2절 `build` 1~5와 3절). diff 층은 T017에서 덧붙인다.
  - **누락 검사**: 빠진 작업 파일이 있으면 종료 코드 2다.
  - **문서 구성**:
    - 문서마다 제목과 그룹 라벨 소제목을 둔다.
    - 노드마다 `### 이름`과, 구체화하지 않는 노드는 `⚠️ <skip_reason>` 줄을 둔다.
    - 상자: 라디오는 `name`/`id`를 노드 Id로, 클래스는 `sK`로 만든다. 보이는 단계마다 `.stage sK`를 두고, 그 안에 `.head`(제목 `<display>단계: <별명> (<display>/<of>)`, ← → `<label>` 또는 흐린 `<span>`)와 `.note`(한 줄 설명, R13 6), `.code` 안의 코드 블록을 둔다. 펜스는 가장 긴 백틱 연속 + 1이고, 최소 3이다.
    - 문서 끝에 기존 상자 `<style>`을 둔다. 내용은 T003에서 확정한 시제품 규칙과 단계 수만큼의 `input.sK:checked ~ .stage.sK` 규칙이다.
  - **마지막 단계 확인**: 문서를 다시 읽어 마지막 단계 코드를 꺼낸다. 원본 위치에서 다시 읽어 다시 잘라낸 구간과 LF 기준으로 비교한다. 다르면 종료 코드 3과 노드·첫 다른 줄을 출력한다(FR-010).
  - **출력 JSON**: `docs`, `unchanged`, `skipped`, `verified`를 담는다.
- [X] T012 [US1] `SK/SKILL.md`를 처음 작성한다.
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
- [X] T013 [US1] `specs/010-stepwise-code-convergence/fixtures/work/`에 손으로 쓴 작업 파일을 둔다.
  - 1단계: 노드 7개 파일
  - 2~6단계: 구체화하는 노드 4개 파일. 2단계에는 `⟨설명⟩`·`...`를 넣는다. 4단계에는 FR-011a처럼 다른 노드의 호출 이름을 맞춘 예를 넣는다. 바깥 노드 파일에는 중첩 노드를 `⟨이름⟩`으로 접는다. 한 단계는 어떤 노드에서 일부러 바꾸지 않는다.

  T010을 실행해 나온 경로에 맞춘다.

**Checkpoint**: quickstart Q1, Q4가 통과한다. Q3는 diff 층을 뺀 기대 문서 `expected/*.base.md` 기준으로 통과한다. 이 시점에 1단계와 원본, 그리고 fixture의 중간 단계를 넘겨 볼 수 있다.

---

## Phase 4: User Story 2 - 단계를 올려 가며 원본에 가까워지는 모습을 지켜보기 (Priority: P1)

**Goal**: 모델이 `begin`으로 받은 복사본을 단계 정의대로 고쳐 중간 단계를 만든다. 문서에는 달라진 줄이 git 변경 색으로 칠해진다.

**Independent Test**: quickstart Q2, Q3(diff 층 포함), Q6, Q7(US2 항목)

- [X] T014 [US2] `SK/scripts/stages.py begin <dir> <k>`를 구현한다(contract 2절 `begin`).
  - **검사**: `2 ≤ k ≤ g-1`인지, `work/<k-1>`이 있는지, `work/<k>`가 없는지 확인한다. 어긋나면 종료 코드 2다.
  - **복사**: 구체화하는 노드마다 `work/<k-1>/<id>.kt`를 `work/<k>/<id>.kt`로 복사한다. 폴더 번호는 두 자리다.
  - **출력**: 그 단계의 `nickname`·`becomes`·`unrevealed`·`notation`·`merged`·`files`를 JSON으로 낸다.
- [X] T015 [US2] `SK/SKILL.md`의 중간 단계 절을 쓴다(research R11, contract 4절 3).
  - **루프**: k = 2…g-1마다 `begin k`를 실행하고, 출력된 정의와 `merged`의 몫을 원본 `work/original/`에 맞춰 Edit로 고친다.
  - **규칙** 다섯 가지를 각각 한 문단으로, 짧은 Kotlin 예와 함께 적는다.
    1. 정의된 측면과 보조 표기만 바꾼다(FR-011).
    2. 드러난 이름은 다른 노드 파일에서도 같은 단계에 맞춘다(FR-011a).
    3. 구체화 사다리를 내려가지 않는다. 드러난 원본 줄의 글자를 바꾸거나 `...`로 가리지 않는다(FR-012, FR-012a).
    4. 2단계에서는 지어낸 본문을 `⟨설명⟩`/`...`로 바꾼다. `⟨⟩`는 U+27E8·U+27E9로 쓴다.
    5. `contains`에 든 노드는 `⟨이름⟩`으로 접는다.
  - **자기 점검**: 다음 `begin` 전에 위 다섯 가지를 확인한다. 지난 단계는 고치지 않는다.
- [X] T016 [US2] `SK/SKILL.md`에 "Self-check" 목록을 추가한다. 항목은 다음과 같다. 서술하지 말고 확인만 한다.
  - 1단계 프롬프트에 원본 정보가 없다.
  - 노드 이름이 구조 뷰와 같다.
  - 단계마다 R11의 다섯 규칙을 지켰다.
  - 응답이 링크와 허용된 줄만 담는다.
- [X] T017 [US2] `SK/scripts/stages.py build`에 diff 층을 덧붙인다(research R7, contract 3절).
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

- [X] T018 [US3] `SK/scripts/stages.py prepare`·`begin`·`build`의 끈 단계 처리를 끝까지 확인하고 보완한다(research R13).
  - 첫 단계가 꺼지면 만들기는 하되 `visible: false`이고 문서에 나오지 않는다. 처음 보이는 단계가 `1/<of>`다.
  - 첫 단계가 아닌 끈 단계는 목록에서 빠지고, 다음 단계의 `merged`에 쌓인다(연속이면 차례로).
  - 한 줄 설명은 `원본과 같아진 것: <합쳐진 becomes들>; <자기 becomes>`다.
  - `--show`·`--hide`는 그 실행에서만 설정보다 우선한다.
- [X] T019 [US3] `SK/SKILL.md`에 "Stage definition and settings" 절을 추가한다.
  - 단계 구성은 `stages.md`에서 고친다(삽입·삭제·순서 변경, 첫 단계와 마지막 단계는 고정).
  - 보이기는 `settings.jsonc`의 `stages`에서, 결과 위치는 `output.directory`에서 정한다.
  - 요청에 적힌 값은 그 요청에서만 우선하며, 옵션으로 넘긴다.
  - 모델은 `stages.md`와 `settings.jsonc`를 직접 읽지 않고 `prepare`·`begin` 출력만 쓴다. `stages.md`는 1단계 서브에이전트 프롬프트에 첫 단계 정의를 넣을 때만 출력에서 가져온다.

**Checkpoint**: quickstart Q5(8단계로 바꾼 정의), Q5a(설정 끄기·알림·요청 우선·결과 위치)가 통과한다.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T020 `specs/010-stepwise-code-convergence/fixtures/expected/`의 기대 문서를 확정한다.
  - `<그룹 Id>.md`, `others.md`, 그리고 같은 이름의 `*.base.md`(diff 층 없음)를 둔다.
  - T011·T017 결과를 한 줄씩 검토해 contract 3절과 맞는지 확인하고 확정한다.
  - 확정한 뒤 Q3를 바이트 비교로 다시 돌린다.
- [X] T021 [P] `README.md`와 `README.ko.md`의 "Optional add-ons/추가 기능"에 `revealing-code-step-by-step` 항목을 추가한다. 담을 내용은 다음과 같다.
  - 무엇을 하는지(구조 뷰 → 노드별 정제 단계 문서)
  - VS Code 미리보기에서 ← →로 넘김, 달라진 줄의 git 색
  - `stages.md`로 단계 구성을 바꾸고 `settings.jsonc`로 보이기와 위치를 정함
  - GitHub에서는 단계가 나열됨

  "Requirements/요구 사항"에는 Python 3.9 이상이 필요하고 없으면 만들지 않는다고 적는다.
- [X] T022 quickstart Q1~Q6을 처음부터 다시 돌려 모두 통과하는지 확인한다. 실패한 시나리오가 있으면 해당 태스크로 돌아가 고친다.
- [X] T023 quickstart Q7을 실행한다. 실제 구조 뷰 `.zenuml/swemo-architecture.architecture.md`로 스킬을 요청하고 다음을 확인한다.
  - 1단계 서브에이전트 프롬프트와 도구 사용(SC-002)
  - 1단계 이름과 의존(SC-001)
  - 2단계 보조 표기
  - 이름 맞추기(FR-011a)
  - `verified` 수(SC-003)
  - 원본 저장소와 구조 뷰의 변경 없음(SC-008)

  몇 개 노드는 미리보기에서 넘겨 보며 FR-011·FR-012를 눈으로 확인한다. 결과는 사용자에게 보고한다.

---

---

## Phase 7: T023에서 드러난 문제 보완 (2026-11-16 clarify 결정)

- [X] T024 `SK/scripts/stages.py`에서 같은 이름의 선언이 여럿이면 후보(`candidates`)를 내놓고, `prepare --pick=<id>:<번호>`로 고르게 한다. `build`의 마지막 단계 확인도 같은 번호로 다시 찾는다(spec FR-002, research R5). swemo `MemoScreen`으로 확인: 후보 2개(공개 54–86줄, 비공개 88–254줄), `--pick=MemoScreen:1`이면 공개 함수가 범위가 된다.
- [X] T025 `SK/stages.md`에서 어노테이션을 선언 단계로 옮긴다. "선언의 종류"는 선언의 종류·수식어·상속·어노테이션을 함께 드러내고, 긴 인자는 `...`로 둔다. "공개 시그니처"는 멤버 어노테이션과 함께 드러낸다. "나머지 로직"과 "원본"에서는 어노테이션 몫을 뺀다(FR-011b).
- [X] T026 `SK/SKILL.md`를 고친다.
  - 오버로드 후보를 고르는 절차를 넣는다.
  - 규칙 4에 "우연히 원본과 같은 줄은 둔다"를 더한다(FR-013).
  - 규칙 5로 어노테이션 규칙을 넣는다.
  - `unchanged` 점검 지시를 뺀다(FR-014).
  - 편집 지침을 "바꿀 부분만, Edit 도구나 정확히 한 번 나오는 글만 바꾸는 도구로"로 고친다.
  - research R1·R5·R11, contract, data-model을 함께 맞춘다.
- [X] T027 바뀐 `stages.md`의 한 줄 설명에 맞춰 `fixtures/expected/*.md`·`*.base.md`를 다시 만든다. 그다음 Q1~Q4 회귀를 다시 확인한다(원본 범위 4개 같음, `verified` 4).

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

---

## Phase 8: Convergence

- [X] T028 `specs/010-stepwise-code-convergence/fixtures/`에 같은 이름의 선언이 둘인 노드(예: `src/Screen.kt`의 공개 `fun Screen(vm: Vm)`과 `private fun Screen(state: State)`)를 넣고, `quickstart.md`에 시나리오를 추가해 실행한다 — `--pick` 없이 `prepare`하면 그 노드에 `candidates` 2개와 "--pick으로 골라야 함" 사유가 나오고, `--pick=<id>:1`로 다시 하면 첫 선언이 원본 범위가 되며 `build`의 확인도 통과한다. 기존 Q1~Q4 기대 결과가 바뀌면 함께 갱신한다 per FR-002 (partial)

## Phase 9: 상황에서 원본으로 이어지는 학습 단계

과거 가상 코드·7단계 관련 작업의 결과는 이 개편으로 대체한다. 기존 검증 fixture는 legacy 계약 회귀에 재사용한다.

- [X] T029 [US1] `SK/stages.md`, `SK/stage1-prompt.md`, `SK/SKILL.md`를 상황·책임·책임 틀로 시작하도록 개정하고 가상 API 발명 규칙 제거 — FR-003~008
- [X] T030 [US1] `SK/scripts/stages.py`의 정의 파서와 그래프 파서를 확장하고 실제 의존별 반복·대상을 prepare/begin에 제공 — FR-005, FR-007~009
- [X] T031 [US2] 같은 스크립트의 prose 표시·노드별 번호·diff 전환·원본 없는 노드·최종 원본 검증·숨기기 처리 구현 — FR-009a, FR-010, FR-015~017
- [X] T032 [US2] 학습 흐름과 기존 fixture 계약의 회귀를 검증하는 표준 라이브러리 테스트 추가·실행 — SC-001~006
- [X] T033 [US3] `README.md`, `README.ko.md`, `quickstart.md`, 기본 설정의 단계 별명 및 계약을 현 동작에 맞춤 — FR-007, FR-009a
- [X] T034 [US2] 북마크 7개 노드 문서를 새 스킬로 재생성하고 최종 원본 일치 및 입력 보존 확인 — US1/AC1~3, SC-003, SC-008
- [X] T035 [US1] 상황 본문의 식별자 생략을 문서 제목에 적용한 해석을 바로잡아 노드 이름을 복구한다. 스킬 지침·렌더러·명세·계획·회귀 검증을 맞추고 북마크 문서를 다시 생성한다 — US1/AC4, FR-015e (테스트 7개 통과, 원본 일치 7개 확인)
- [X] T036 [US2] 단계 질문 문구와 해당 정의·출력·렌더링 필드를 제거하고 스킬 지침·명세·계약·회귀 검증을 맞춘다. 기존 manifest로도 질문이 표시되지 않게 북마크 문서를 재생성한다 — FR-015, FR-018 (테스트 7개 통과, 원본 일치 7개 확인)
- [X] T037 [US1] 상황과 담당 책임을 하나의 첫 장면으로 합치고 별도의 책임 단계를 제거한다. 단계 정의·격리 프롬프트·설정·명세·계획·검증을 맞추고 북마크 문서를 다시 생성한다 — FR-003~004, US1/AC1~2 (테스트 7개 통과, 원본 일치 7개 확인)
- [X] T038 [US1] 별도의 책임 틀 단계를 제거하고 상황·책임·최소 틀을 같은 첫 장면에 표시한다. intro 표현·격리 프롬프트·설정·문서·회귀 검증을 맞추고 북마크 예제의 이후 코드 내용은 보존한다 — FR-003~004, US1/AC2~3 (테스트 9개 통과, 원본 일치 7개 확인)
- [X] T040 [US1] 상자 위 책임 줄과 겹치는 첫 장면의 담당 책임 문단을 단계 정의·격리 프롬프트·스킬 지침·README·회귀 검증에서 빼고 북마크 첫 장면을 다시 생성한다 — FR-003, FR-015e (테스트 9개 통과, 원본 일치 7개 확인)
- [X] T041 [US1] 상자 위 책임 줄과 겹치는 첫 장면의 책임 틀을 없애 첫 장면을 상황 문단 하나로 줄이고 별명을 "사용 상황"으로 바꾼다. intro 처리를 제거하고 문장 장면 다음 첫 코드의 시작 파일을 만들며, 격리 프롬프트·스킬 지침·README·회귀 검증을 맞춘다. 북마크 예제는 상황을 격리 작성으로 다시 쓰고 책임 줄과 같은 자리표시자 2개를 나눈 일로 바꾼다 — FR-003~004 (테스트 7개 통과, 원본 일치 7개 확인)

실행 순서: T029 → T030 → T031 → T032 → T033 → T034. 검증 뒤 converge로 남은 요구를 점검한다.

## Phase 10: 단위 펼치기

문법 범주 단계와 `begin`/`apply` 흐름을 대체한다. SK는 `.agents/skills/revealing-code-step-by-step`이다.

- [X] T042 [US2] `SK/scripts/stages.py`에 펼치기 단위 계산(본문 최상위 항목 나누기, 비공개 멤버·상태·매개변수 붙이기, 본문 없는 선언 묶기, 4개 상한, 주석은 멤버와 함께)과 장면 렌더링(윤곽·펼치기·접기·원본)을 넣는다 — FR-004~005a, FR-011
- [X] T043 [US2] `prepare`가 단위를 manifest에 두고 단위별 원본 줄을 한 번 출력하며, 1단계 프롬프트에서 `click` 줄을 빼게 한다 — FR-003, FR-005b, SC-009
- [X] T044 [US2] `build`가 `work/outline.json`을 검증해 잘못된 입력을 거부하고, 장면을 만들어 모두 펼친 장면과 마지막 장면을 원본과 대조하게 한다. `begin`/`apply`/`edits.txt`를 제거한다 — FR-005b, FR-010, FR-014
- [X] T045 [US3] `SK/stages.md`(종류·순서와 단계 고치기 원칙), `SK/settings.jsonc`, `SK/SKILL.md`, `README.md`, `README.ko.md`를 새 흐름에 맞춘다 — FR-007~009a, SC-006
- [X] T046 [US2] `test_learning_stages.py`를 새 흐름의 회귀 검증으로 바꾸고 fixture 기대 문서를 새로 만든다 — SC-001, SC-003~005, SC-009 (테스트 16개 통과)
- [X] T047 [US2] 북마크 예제를 새 흐름으로 다시 만들고 원본 일치와 입력 보존, 읽고 쓰는 양을 확인한다 — SC-003, SC-008, SC-009 (원본 일치 7개, 구조 뷰 SHA256 동일, 읽는 원본 목록 11,730자·쓰는 입력 930자·1단계 프롬프트 16,848자)

## Phase 11: 스코프 트리 정제 (2026-11-17)

Phase 10의 펼치기 단위(최상위 문장, 4개 합치기, 접기)를 대체한다. SK는 `.agents/skills/revealing-code-step-by-step`이다. 근거와 세부 규칙은 [research.md](research.md) S1~S8, 형식은 [contracts/stages-contract.md](contracts/stages-contract.md) 맨 위 절, 데이터는 [data-model.md](data-model.md) 맨 위 절에 있다. 설계 기준은 구조에서 오는 최적화다. 원본 크기에 비례하는 비용은 그대로 두고 구조적 낭비만 없앤다(spec SC-009). 장면 그리기 규칙은 research S6에 모두 적혀 있으며, 손으로 만든 트리의 시제품으로 사용자와 확인했다. 시제품 코드는 저장소에 없으므로 기대지 않는다.

- [X] T048 [US2] `SK/scripts/stages.py`에 스코프 트리 만들기를 넣는다 — FR-005a, research S1
  - 기존 `analyse`의 본문 항목 나누기를 "영역 하나(시작·끝 줄, 종류)를 나누는 함수"로 일반화하고, 여러 줄 항목마다 재귀로 적용한다.
  - 영역 종류별 나누기:
    - `{`: 문장. 주석·어노테이션은 다음 문장에 붙고, 여러 줄 raw string과 줄 끝·줄 머리 이어짐 규칙은 지금 그대로다.
    - `(`·`[`: 깊이 0 쉼표로 나눈 인자. 이어지는 한 줄 인자는 한 노드로 묶는다.
    - 둘째 줄부터 `.`·`?.`로 시작하는 줄들: 체인 고리마다 한 노드
  - 한 항목의 영역이 여럿이면(인자 목록 뒤의 람다 등) 자식을 영역 순서대로 잇는다.
  - **외길 병합**: 나눈 결과가 자식 하나뿐이면 층을 만들지 않고, 그 자식의 자기 줄·자식을 부모로 올린다.
  - 루트에도 외길 병합을 적용한다(자식 하나뿐인 루트는 그 자식의 자식을 루트의 자식으로 삼는다) — spec US2 AC5.
  - 매개변수와 루트 영역의 비공개 멤버·한 줄 가변 상태는 지금처럼 붙는 선언으로 둔다.
  - 본문 없는 선언(시그니처·추상 프로퍼티)이 같은 종류로 이어지면 지금의 `bodyless`·`kind` 판단으로 한 노드로 묶는다 — FR-005a(5).
  - 불변식: 원본 범위의 모든 줄이 루트 머리·어떤 노드의 자기 줄·붙는 선언 중 정확히 한 곳에 속한다. 어기면 `SourceMismatch`(종료 코드 3)다.
  - 노드 필드는 data-model의 `lines`·`children`·`first`다.
- [X] T049 [US2] `SK/scripts/stages.py`의 `prepare`가 단위 목록 대신 스코프 목록을 출력하고, 트리를 manifest에 두게 한다 — FR-005b, SC-009(a)·(d)
  - 출력 형식은 contract 맨 위 절 그대로다: `===== <id> · 책임: … · 스코프 <k>개 =====`, `--- #<n> (부모 #<m> | 루트)`, 줄 표시 `-`·자식 번호·빈칸·`=`, 스코프 자식은 `⟨#<스코프 번호>⟩` 한 줄.
  - 스코프는 후위 순서로 1부터 매기고 루트가 마지막이다. 자식이 없는 루트는 블록을 내지 않는다.
  - 출력 전체에서 원본의 각 줄이 정확히 한 번 나오는지 스스로 확인한다(어기면 종료 코드 3).
- [X] T050 [US2] `SK/scripts/stages.py`의 `build`가 새 `work/outline.json`을 검사하게 한다 — FR-005b, SC-009(f), SC-011, research S4·S5
  - 형식: `{"<node id>": [{"s", "with", "sep": [{"ids", "s"}]}, …]}`, 스코프 순서 배열, 루트 항목에는 `s`·`with`가 없음
  - 거부(종료 코드 2): contract의 목록 전부. 틀린 곳마다 `<id> 스코프 #<n>: <이유>` 한 줄씩을 표준 오류로 모두 낸다(첫 오류에서 멈추지 않음).
  - 문장 규칙(research S5, 그대로 옮김): "빈 문장, 45자 초과, `⟨`·`⟩` 포함, 책임 한 줄과 같은 문장(앞뒤 공백·마침표 무시). 나열 표지: 쉼표, `하고`·`이고`·`되고`·`며` 뒤에 공백이 오는 연결"
  - `sep`은 4개 이하. 모든 자식 번호가 `with`·`sep`에 정확히 한 번씩 나와야 한다.
  - 기존 `check_outline`의 단위·접기 검사를 지운다.
- [X] T051 [US2] `SK/scripts/stages.py`에 단계와 장면 만들기를 넣고 Phase 10의 단위·접기 코드를 지운다 — FR-004, FR-005, FR-005c, FR-013, SC-010, research S6·S7
  - 단계: `sep` 묶음마다 하나. 노드는 묶음 노드와 그 "함께 보임" 자손이다. 부모 단계는 묶음을 가진 스코프가 드러나는 단계다. 전위 순서이고, 형제끼리는 첫 줄이 위에 있는 순서다. 그 순서가 번호다.
  - 장면:
    - 숨은 노드 가운데 가장 바깥 것마다 `⟨번호. 문장⟩`을 그 노드 첫 줄의 들여쓰기로 둔다.
    - 빈 줄만 사이에 둔 같은 부모·같은 단계는 합친다.
    - 숨은 자리 안에 첫 노드가 든 뒤 단계들은 그 아래에, 단계 트리 깊이 차이 × 4칸으로 들여 쓴다.
    - 붙는 선언은 단계 순서에서 이름이 처음 쓰이는 단계에 드러나고, 숨은 매개변수는 `...`으로 접는다.
    - 한 묶음이 떨어진 여러 자리에 있으면 자리마다 같은 `⟨번호. 묶음 문장⟩`이다. 일부는 중첩, 일부는 제자리에 있으면 양쪽에 같은 번호가 나온다.
  - 제목: `<k>단계: <별명> <n>/<N> — <묶음 문장> (<k>/<전체>)`
  - 모든 단계를 연 장면이 원본과 같지 않으면 종료 코드 3이다. 원본 장면은 마지막으로 보이는 코드 장면이 원본과 같을 때만 두지 않는다(기존 `node_scenes` 규칙 그대로). 그래서 설정으로 펼치기를 끄면 윤곽 다음에 원본이 나온다.
  - `MAX_UNFOLDS`·`make_units`·접기 렌더링·단위 목록 출력을 지운다. 설정 로더, 1단계 프롬프트, 상자·diff·책임 줄 렌더링은 바꾸지 않는다.
- [X] T052 [P] [US3] 지침과 설명을 새 흐름에 맞춘다 — FR-007, FR-008, SC-006
  - `SK/stages.md`의 `## 펼치기` 정의: 스코프 트리, 묶음, 순서, 번호 자리표시자, 한 장면에 한 겹. "단계를 고칠 때" 원칙의 `work/outline.json` 설명도 함께 맞춘다.
  - `SK/SKILL.md`:
    - frontmatter description과 첫 문단
    - 1단계의 `prepare` 출력 설명
    - 3단계 Outline input: 형식, 한 스코프 한 줄, 후위 순서로 한 스코프씩 쓰기, 목적 수준 문장 규칙과 나쁜 예·좋은 예, 두 가지를 잇지 않기, 45자
    - 4단계 Build의 거부 설명(보고된 스코프 줄만 고치기)
  - `README.md`, `README.ko.md`의 이 스킬 항목: "일마다 자리표시자 한 문장" → 스코프마다 목적 문장과 묶음, 한 겹씩 펼치기
- [X] T053 [US2] `test_learning_stages.py`를 새 흐름의 회귀 검증으로 바꾸고 fixture를 새로 만든다 — SC-001, SC-003~005, SC-009(a)·(f), SC-010, quickstart 1
  - quickstart 1의 항목을 모두 테스트로 둔다.
  - 여러 겹 샘플은 테스트 안의 합성 Kotlin이다(호출 인자 목록 → 람다 → 체인 → 그리기 블록). 사용자 프로젝트 코드는 복사하지 않는다.
  - 본문 없는 선언 묶기, 루트의 외길 병합, 결정성(같은 원본의 `prepare` 출력 두 번, 같은 입력의 `build` 문서 두 번이 글자까지 같음 — SC-004), 펼치기를 끈 경우의 원본 장면을 테스트한다.
  - 접기·4개 상한 테스트를 지운다.
  - `fixtures/unfold*/outline.json`은 새 형식으로 다시 쓰고, `fixtures/expected/*.md`는 `REGENERATE=1`로 다시 만든 뒤 diff를 읽어 확인한다.
- [X] T054 [US2] 실제 예제로 끝까지 실행하고 비교 기록을 남긴다 — SC-003, SC-008, SC-009, SC-010, quickstart 2·3
  - `.zenuml/swemo-ui-bulleted-list-testbed.architecture.md`로 prepare → 격리된 상황 작성 → 메인 에이전트의 `outline.json` → build를 실행한다.
  - 확인할 것: `verified`, 구조 뷰 SHA256 전후, 읽기·쓰기 글자 수, BulletedListTextField의 장면별 새 줄 수, 작업자 호출 수
  - 결과를 research S8의 "바꾼 뒤"에 바꾸기 전 testbed 기록(원본 14,022자, `outline.json` 2,412자, 장면별 3, 4, 3, 60, 14)과 나란히 적는다. 비교 예제는 testbed 하나다(spec SC-009).

실행 순서: T048 → T049 → T050 → T051(같은 파일) → T053 → T054. T052는 contract만 기대므로 T048과 함께 진행할 수 있다. 끝나면 converge로 남은 요구를 점검한다.

## Phase 12: Convergence

- [X] T055 `test_learning_stages.py`에 깊이 1 노드(안쪽 블록이 없는 본문)의 장면 종류·순서가 사용 상황 → 윤곽 → 묶음 수(4개 이하)만큼의 펼치기이고 원본 장면이 따로 없음을 확인하는 테스트를 추가한다 per quickstart 1, spec Edge Cases "안쪽 블록이 없는 본문" (partial)
- [X] T056 `SK/scripts/stages.py`의 `build_tree`가 manifest에 남기는 트리 노드에 data-model의 `first`(노드 첫 줄, 자리표시자 들여쓰기와 형제 순서의 기준)를 기록하고, `plan_steps`·`render_steps_scene`의 첫 줄 계산이 그 값을 쓰게 한다 per data-model TreeNode, T048 (partial)

## Phase 13: 붙는 선언 좁히기 (2026-11-18)

붙는 선언을 한 줄 선언으로 좁힌다(spec FR-005a(4), SC-012). SK는 `.agents/skills/revealing-code-step-by-step`이다. 근거는 [research.md](research.md) S9, 데이터는 [data-model.md](data-model.md)의 Attached, 출력 표시는 [contracts/stages-contract.md](contracts/stages-contract.md) 맨 위 절에 있다. 바꾸는 것은 분류 조건 하나이고, 트리·목록·검사·단계·장면 코드는 그대로 쓴다.

- [X] T057 [US2] `SK/scripts/stages.py`의 `build_tree`에서 루트 항목을 붙는 선언으로 돌리는 조건을 "(비공개이거나 한 줄 가변 상태) 그리고 항목의 `lines`(코드 줄, 주석·따로 선 어노테이션 제외)가 하나"로 바꾼다. 나머지 항목은 모두 루트 자식이 된다. docstring의 `attached` 설명도 맞춘다 — FR-005a(4), research S9
- [X] T058 [P] [US3] 붙는 선언 설명을 "한 줄 선언"으로 맞춘다 — FR-007, SC-006
  - `SK/stages.md` `## 펼치기`의 "처음 쓰이는 비공개 멤버·상태·매개변수"
  - `SK/SKILL.md` 1단계 prepare 출력의 `=` 설명
- [X] T059 [US2] `specs/010-stepwise-code-convergence/test_learning_stages.py`에 여러 줄 비공개 멤버 시험을 더한다 — SC-012, quickstart 1
  - 합성 Kotlin 클래스(여러 줄 비공개 흐름 하나는 안에 람다·갈림길이 든 여러 겹, 한 줄 비공개 상태 하나, 그 둘을 쓰는 공개 멤버 하나)
  - 확인: 여러 줄 비공개 멤버가 `attached`에 없고 루트 자식 스코프이며 그 안의 겹이 따로 펼쳐짐, `attached`의 모든 선언이 코드 한 줄, 한 줄 상태는 처음 쓰는 단계에 붙음, 모두 연 장면이 원본과 같음
  - 기존 `fixtures/expected/*.md`가 다시 만들지 않아도 그대로 통과함(여러 줄 비공개 멤버가 없는 노드는 결과가 같음)
- [X] T060 [US2] 실제 예제로 다시 실행하고 기록한다 — SC-003, SC-008, SC-012, quickstart 2
  - 바꾸기 전 `.zenuml/swemo-ui-bulleted-list-testbed.stages/`의 문서를 scratchpad에 복사해 두고, 같은 구조 뷰로 prepare를 다시 실행한다. MemoViewModel 외 노드의 `outline.json` 항목은 그대로 쓰고, MemoViewModel 항목만 새 스코프 목록에 맞춰 다시 쓴 뒤 build한다(1단계 파일은 보존).
  - 확인: `verified`, 구조 뷰 SHA256 전후, MemoViewModel의 장면별 새 줄 수와 붙는 선언이 모두 한 줄인지, MemoViewModel 외 노드의 상자는 바꾸기 전과 글자까지 같음
  - 결과를 research S9 끝에 바꾸기 전 MemoViewModel 기록(64, 11, 5, 36, 5, 28, 17)과 나란히 적는다.

실행 순서: T057 → T059 → T060. T058은 T057과 함께 진행할 수 있다. 끝나면 converge로 남은 요구를 점검한다.

## Phase 14: 원본 언어와 파일 단위 노드 (2026-11-18)

Kotlin만 받던 제한을 없애고, 노드 이름이 파일 자체를 가리키면 파일 전체를 원본 범위로 삼는다(spec FR-001a·002·006·017·017a, SC-013). SK는 `.agents/skills/revealing-code-step-by-step`이다. 근거는 [research.md](research.md) S10, 데이터는 [data-model.md](data-model.md)의 Node `range`(`whole_file: true`), 이유 문구는 [contracts/stages-contract.md](contracts/stages-contract.md) `prepare` 5번 표에 있다. 노드 이름과 같은 Kotlin 선언을 찾는 노드의 결과는 글자까지 같아야 한다.

- [X] T061 [US2] `SK/scripts/stages.py`에서 원본 범위 정하기를 한 함수로 모은다 — FR-002, FR-017, research S10
  - `read_source`: `.kt`·`.kts`가 아니면 `원본이 Kotlin이 아니어서 구체화하지 않음`을 돌려주던 검사를 지운다. 마지막 경로 조각에 `.`이 없으면 `링크가 파일 하나를 가리키지 않아 구체화하지 않음`, 폴더·읽기·UTF-8 검사는 그대로 둔다.
  - 새 `locate_range(text, node, link)` → `(span, reason, candidates, whole_file)`: 원본이 `.kt`·`.kts`이면 `find_declaration(text, declaration_names(node), node["pick"])`을 먼저 쓴다. span이 있거나 후보가 여럿이면 그 결과를 그대로 돌려준다. 그렇지 않으면 링크의 마지막 경로 조각(`#`·`?` 앞)에서 파일 이름 `f`, 확장자 뺀 이름 `stem`을 얻고, 노드 Id나 표시 이름이 `f`·`stem`·(Kotlin이면) `stem + "Kt"` 가운데 하나와 대소문자까지 같으면 span `(1, 파일 줄 수)`와 `whole_file=True`를 돌려준다. 둘 다 아니면 Kotlin은 `find_declaration`의 이유를 그대로, Kotlin이 아니면 `Kotlin이 아닌 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음`을 돌려준다.
  - `cmd_prepare`와 `cmd_build`의 마지막 단계 확인이 둘 다 `locate_range`를 쓰게 한다. prepare는 `range`에 `whole_file`이 참일 때만 `"whole_file": true`를 더한다(거짓이면 키를 두지 않아 기존 manifest와 같다).
- [X] T062 [US2] `SK/scripts/stages.py`의 `analyse`·`build_tree`에 `whole_file`(기본 False) 인자를 더한다 — FR-005a, FR-017a, research S10
  - Kotlin 파일 단위 노드: 맨 앞에서 빈 줄·주석 줄·`@file:` 어노테이션·`package`·`import` 줄이 이어지는 구간을 머리로 보고, `body_open`을 그 마지막 줄 번호(머리가 없으면 -1)로 둔다. 매개변수는 없고, 항목은 `split_items(lines, masked, body_open + 1, len(lines), raw)`다. 마지막 줄이 `}`인지 보는 검사는 이 경우 하지 않는다. 항목이 없으면 지금처럼 트리가 없다.
  - Kotlin이 아닌 원본은 `cmd_prepare`에서 `build_tree`를 부르지 않고 `tree`를 null로 둔다.
  - `node_scenes`가 트리를 다시 만들 때 `node["range"].get("whole_file")`과 원본 언어를 prepare와 똑같이 넘기게 한다.
- [X] T063 [US2] `SK/scripts/stages.py`의 코드 블록 언어를 원본에 맞춘다 — FR-006, research S10
  - `fence(code, lang)`: Kotlin(`.kt`·`.kts`) 원본은 `kotlin`, 그 밖은 링크의 마지막 경로 조각에서 얻은 확장자를 소문자로 쓴다. `render_box`까지 노드의 언어를 넘긴다.
  - `extract_last_stage`의 정규식이 `kotlin` 대신 아무 언어 이름(`[\w+.#-]*`)이나 받게 한다.
- [X] T064 [P] [US3] Kotlin 전용·비Kotlin 제외 문구를 고친다 — FR-001a
  - `SK/SKILL.md` frontmatter `description`: "gradual Kotlin walkthrough" → 언어를 말하지 않는 표현, "or non-Kotlin source" 제외 문구 삭제. 본문에 Kotlin 전용이라는 설명이 있으면 함께 고친다.
  - `SK/stage1-prompt.md`: "never Kotlin code" → "never code".
  - `README.md` 42·81행, `README.ko.md` 42·81행: "each node's Kotlin code"/"노드마다 Kotlin 코드", "Kotlin syntax highlighting stays"/"Kotlin 구문 색칠은 그대로", "It works on Kotlin sources…"/"Kotlin 원본만 다룹니다"를 원본 언어 기준으로 고치고, 파일 전체를 가리키는 노드는 파일 전체를 보인다는 점과 Kotlin이 아닌 원본은 상황 → 원본으로 보인다는 점을 한 문장으로 적는다.
- [X] T065 [US2] `specs/010-stepwise-code-convergence/test_learning_stages.py`에 시험을 더한다 — SC-003, SC-013, quickstart 맨 위 절
  - 임시 폴더에 구조 뷰 하나와 원본을 만든다: `colors.xml`(노드 `ColorsXml`, 표시 이름 `colors.xml`), `Color.kt`(`package`·`import`와 최상위 `val` 셋, 노드 `ColorKt`, 표시 이름 `Color.kt`), `Shapes.java`(클래스 `Circle`, 노드 `Circle`), `Order.kt`(`class Order`, 노드 `Order`).
  - 확인: `ColorsXml`은 `skip_reason` 없음·`range.whole_file` 참·`tree` null이고, 문서에 `⚠️` 줄이 없으며 장면이 사용 상황·원본 둘이고 원본 장면 fence가 `xml`이며 파일 전체와 같다. `ColorKt`는 원본 범위가 파일 전체이고 스코프 목록의 `package`·`import` 줄이 `-`이며 최상위 `val`이 루트 자식이다. 윤곽에 `package` 줄이 보이고 마지막 장면이 파일 전체와 같다. `Circle`의 `skip_reason`이 contract 문구와 같다. `Order`는 `whole_file` 키가 없다. `build`의 `verified`가 3이다.
  - 기존 `fixtures/expected/*.md`가 다시 만들지 않아도 그대로 통과한다(SC-013 호환).
  - 결과: 시험 26개 통과. 기존 fixture의 `LegacyBridge`(`src/Legacy.java`, 파일 이름과 다른 선언 노드)는 이유 줄이 새 contract 문구로 바뀌는 것이 의도된 변경이라 `fixtures/expected/others.md`·`others.base.md`에서 그 한 줄만 고쳤다. 나머지 기대 문서는 글자까지 같다.
- [X] T066 [US2] 시험 전체를 실행하고, 사용자 예제가 저장소 안에 있으면 다시 만들어 확인한다 — SC-003, SC-008, SC-013
  - `python specs/010-stepwise-code-convergence/test_learning_stages.py`가 모두 통과한다.
  - Color.kt·Theme.kt·colors.xml이 든 swemo 구조 뷰는 저장소에 없으면 다시 만들지 않고, 사용자 환경에서 확인할 일로 보고한다.
  - 결과: `.zenuml/`에 `colors.xml`을 링크한 구조 뷰가 없어 다시 만들지 않았다(사용자 환경에서 확인).

실행 순서: T061 → T062 → T063 → T065 → T066. T064는 T061과 함께 진행할 수 있다. 끝나면 converge로 남은 요구를 점검한다.

## Phase 15: Convergence

- [X] T067 `specs/010-stepwise-code-convergence/quickstart.md` 맨 위 절의 "기존 결과 불변" 항목을, 노드 이름과 같은 Kotlin 선언을 찾는 노드의 상자는 바꾸기 전과 글자까지 같고 Kotlin이 아닌 선언 노드 `LegacyBridge`(`src/Legacy.java`)의 이유 줄만 새 contract 문구로 바뀐다고 고친다 per SC-013 (partial)

## Phase 16: 블록 구조를 아는 언어로 넓히기 (2026-11-18)

선언 찾기와 한 겹씩 펼치기를 블록 구조를 아는 프로그래밍 언어 전부로 넓힌다(spec FR-002·017a, SC-014). SK는 `.agents/skills/revealing-code-step-by-step`이다. 근거와 프로필 항목·언어 목록·범위 확인 규칙은 [research.md](research.md) S11, 이유 문구는 [contracts/stages-contract.md](contracts/stages-contract.md) `prepare` 5번 표에 있다. Kotlin 결과는 글자까지 같아야 한다.

- [X] T068 [US2] `SK/scripts/stages.py`에 언어 프로필 표 `LANGS`와 `lang_of(link)`를 둔다 — research S11
  - Kotlin 프로필은 지금 상수(`HEADER`, `CONTINUE_END`, `CONTINUE_START`, `DECL_HEAD`, `PARAM_HEAD`, `COMMENT_LINE`, `ANNOTATION_LINE`)와 지금 문자열·주석 규칙을 그대로 가리킨다.
  - 중괄호 계열: Java, Scala, Groovy, Swift, C#, Go, Rust, Dart, JavaScript, TypeScript, C, C++. 들여쓰기 계열: Python. 확장자는 research S11 목록대로.
- [X] T069 [US2] `mask_code`·여러 줄 문자열 판정이 프로필을 받게 한다 — research S11
  - 문자열 목록(긴 구분자 먼저, 여러 줄 허용, `\` 이스케이프, `${…}` 템플릿), 줄 주석 표기, 블록 주석 중첩 여부, 문자 리터럴(Kotlin 밖은 같은 줄 12글자 안에서 닫힐 때만)을 프로필에서 읽는다.
  - `_raw_string_flags`를 `mask_code`가 기록한 여러 줄 문자열 구간으로 판정하게 바꾼다. Kotlin fixture 결과가 같아야 한다.
- [X] T070 [US2] 선언 찾기와 선언 끝을 프로필로 한다 — FR-002, research S11
  - `find_declaration(text, names, pick, lang)`: 프로필의 선언 머리 정규식, 없으면(허용 언어만) 키워드 없는 함수 선언 후보(이름 뒤 `(`, 짝 `)` 다음 `;`보다 먼저 깊이 0의 `{`, `new`·`return`·`throw`·`await`·`=`·`.` 뒤가 아님). 다른 후보 범위 안에 든 후보는 버린다. 위로 넓히는 주석·어노테이션 판정도 프로필로 한다.
  - `_declaration_end`: `;` 계열은 깊이 0의 `;`, 그 밖은 지금 규칙. 들여쓰기 계열은 `:` 머리 뒤 더 깊은 줄과 사이 빈 줄까지, 할당문은 괄호·`\` 이어짐 끝까지.
  - 범위 확인(Kotlin 밖): 괄호가 음수 없이 0으로 끝남, 머리 줄에 이름, 범위 다음 첫 비지 않은 줄이 머리 줄보다 깊지 않음, 들여쓰기 계열이면 머리 뒤 줄이 비었거나 더 깊음. 어기면 찾지 못한 것으로 보고 contract의 "블록 구조로 확인하지 못해" 이유를 쓴다.
- [X] T071 [US2] 스코프 트리를 프로필로 한다 — FR-005a, FR-017a, research S11
  - `analyse`·`split_items`·`build_tree`가 프로필을 받는다. 항목 이름·비공개·한 줄 가변 상태·본문 없는 선언·매개변수 이름 판정을 프로필로 한다.
  - 들여쓰기 계열: `split_items_indent`(기준 들여쓰기, 더 깊은 줄·괄호 안·`\` 이어짐·`elif`/`else`/`except`/`finally`는 앞 항목, `#`·`@`는 다음 항목), `analyse`의 머리 끝은 괄호 깊이 0에서 `:`로 끝나는 줄, `children_of`의 안쪽 영역은 괄호가 더 깊거나 항목 첫 줄보다 깊게 들여 쓴 줄이며 앞 줄이 `:`로 끝나면 문장 블록, 아니면 인자 목록.
  - 파일 단위 노드의 머리는 최상위 항목 가운데 맨 앞의 프로필 머리 정규식에 맞는 항목들이다.
  - 붙는 선언의 이름 찾기를 `(?<!\w)이름(?!\w)`로 한다.
- [X] T072 [US2] `locate_range`·`node_tree`·`source_lang`·`node_scenes`가 "프로필이 있는가"로 가르고 프로필을 넘기게 한다. 프로필이 없는 원본의 이유를 contract 문구로 바꾼다 — FR-002, FR-006, FR-017
- [X] T073 [P] [US3] `SK/SKILL.md`에 언어 범위 문장이 있으면, `README.md`·`README.ko.md` 81행의 언어 범위 문장을 블록 구조를 아는 언어(중괄호·들여쓰기 계열) 기준으로 고친다 — FR-001a
- [X] T074 [US2] `specs/010-stepwise-code-convergence/test_learning_stages.py`에 언어별 시험을 더하고 기존 시험을 새 동작에 맞춘다 — SC-013, SC-014, quickstart 맨 위 절
  - Java·TypeScript·JavaScript·Go·Rust·C#·Swift·C++·Python마다 머리와 선언 둘 이상이 든 원본: 노드 이름의 원본 범위가 기대 범위와 같음, 블록이 든 선언은 트리가 있고 `auto_entry`로 모두 연 장면이 원본 범위와 같음.
  - JavaScript 함수 안의 정규식 리터럴 `/}/`: "블록 구조로 확인하지 못해" 이유.
  - `Languages` 시험의 `Circle`(Shapes.java)은 이제 `class Circle` 범위다. `fixtures/expected/others*.md`의 `LegacyBridge`도 선언을 찾으므로 `REGENERATE=1`로 다시 만들고 diff가 그 상자뿐인지 확인한다.
  - 기존 Kotlin 시험과 기대 문서는 그대로 통과한다.
- [X] T075 [US2] 시험 전체를 실행한다 — SC-003, SC-013, SC-014
  - 결과: 시험 31개 통과. 기대 문서는 `REGENERATE=1`로 다시 만들었고 diff는 `LegacyBridge` 상자(이유 줄 → `class LegacyBridge` 원본 장면)뿐이다.
  - 추가 확인(합격 기준 아님): 저장소 스킬의 Python·JavaScript 스크립트에서 이름이 하나뿐인 함수·클래스 196개 가운데 195개의 범위를 찾았고, 모두 연 장면이 범위와 같았다(남은 1개는 시험 스크립트가 문서 문자열 속 단어를 이름으로 뽑은 것). Python 선언 165개는 표준 `ast`의 범위(데코레이터 포함)와 모두 같았다.
  - 구현 중 고친 것: Kotlin 밖 문자 리터럴을 "한 글자, 또는 `\`로 시작하는 이스케이프"로 좁혔다(Rust 수명 `'a`가 문자로 읽혀 괄호가 가려졌음). 이름으로 비공개를 정하는 언어(Go·Rust·Python·Dart)는 선언 모양의 줄에만 적용했다(함수 본문 문장이 붙는 선언으로 빠졌음). JavaScript·TypeScript의 값 자리 정규식 리터럴을 가리게 했다(research S11에 반영).

실행 순서: T068 → T069 → T070 → T071 → T072 → T074 → T075. T073은 T068과 함께 진행할 수 있다. 끝나면 converge로 남은 요구를 점검한다.

## Phase 17: Convergence

- [X] T076 `specs/010-stepwise-code-convergence/test_learning_stages.py`의 `SOURCES_BY_LANGUAGE`에 Scala(`scala`)·Groovy(`groovy`)·Dart(`dart`)·C(`c`) 원본을 더해, 머리와 선언 둘 이상이 든 파일에서 노드 이름의 원본 범위가 기대 범위와 같고 블록이 든 선언이 모두 연 장면에서 원본 범위로 돌아오는지 확인한다 per SC-014 (partial)
- [X] T077 `specs/010-stepwise-code-convergence/test_learning_stages.py`에 Kotlin 밖 언어의 파일 단위 노드 시험을 더한다 — Java 파일(`package`·`import`와 최상위 클래스 둘)과 Python 파일(`import`·`from`과 최상위 함수 둘)을 `whole_file`로 트리로 만들 때 머리 항목 줄이 루트의 자기 줄이고 최상위 선언이 루트 자식이며 모두 연 장면이 파일과 같다 per research S11 "파일 단위 노드의 머리", FR-005a (partial)
  - 결과: 시험 32개 통과. Scala 원본의 동반 객체 이름은 클래스와 겹치면 FR-002대로 `--pick` 후보가 나오므로, 범위 시험에서는 `object CartOps`로 두었다.

## Phase 18: 규격 표시 노드 원본 연결 (FR-021, SC-015)

**Purpose**: 003 FR-036의 규격 표시어가 Dependency 라벨에 붙어도 실제 이름의 선언·파일을 찾아 단계별로 펼친다.

**Independent Test**: 표준 라이브러리 테스트 전체가 통과하고, 복합 표시어·변화 표시 라벨이 실제 이름으로 정규화되며 마지막 장면이 해당 원본 범위와 일치한다.

- [X] T078 [US2] `specs/010-stepwise-code-convergence/test_learning_stages.py`에 `class&nbsp;NiaAppState`, `enum&nbsp;class&nbsp;TopLevelDestination`, `♻️&nbsp;fun&nbsp;NiaNavHost`, 표시어 없는 이름을 실제 이름으로 읽는 회귀 테스트를 추가하고 현재 실패를 확인한다 per FR-021, SC-015
- [X] T079 [US2] `.agents/skills/revealing-code-step-by-step/scripts/stages.py`의 `clean_name`이 변화 표시·HTML 태그를 제거한 원본 라벨에서 마지막 `&nbsp;` 뒤 이름을 반환하게 하고 전체 `test_learning_stages.py`를 실행한다 per FR-021, SC-003, SC-015

**Dependencies**: T078 → T079.

## Phase 19: GitHub에서 단계 문서 CSS 원문 접기 (FR-022, SC-016)

**Purpose**: 편집기 단계·diff 스타일은 유지하면서 GitHub 첫 화면에는 적용되지 않는 CSS의 설명 한 줄만 보인다.

**Independent Test**: 전체 테스트가 통과하고, 생성된 `.md`가 wrapper 하나 안에 기본·diff CSS를 가지며 `.base.md`에는 같은 wrapper 안 기본 CSS만 있는지 확인한다.

- [X] T080 [US2] `test_learning_stages.py`에 wrapper 하나, 요약·공식 링크, 기본·diff CSS 포함 여부와 diff 제거 동등성을 확인하는 회귀를 추가한다 per FR-022, SC-016
- [X] T081 [US2] `.agents/skills/revealing-code-step-by-step/scripts/stages.py`가 기본·diff `<style>`을 고정 `<details>` 하나로 감싸고 기본 CSS로 wrapper를 숨기게 한다 per FR-022
- [X] T082 [US2] `fixtures/expected/*.md`와 `*.base.md`를 새 wrapper 형식으로 재생성한다 per FR-022
- [X] T083 [US2] 전체 테스트와 skill validator를 실행한다 per SC-003, SC-004, SC-016
  - 표준 라이브러리 테스트 33개가 통과했다. skill validator는 실행했으나 환경에 PyYAML이 없어 시작 전에 종료됐다(`ModuleNotFoundError: yaml`).

**Dependencies**: T080 → T081 → T082 → T083.
## Phase 20: SKILL.md 최소화

- [X] T084 [US1] `.agents/skills/revealing-code-step-by-step/SKILL.md`의 description과 도입부 중복을 줄이고 outline 판단 규칙을 보존한다 per FR-023, FR-024
- [X] T085 [US1] `specs/010-stepwise-code-convergence/test_learning_stages.py` 전체를 실행해 fixture 결과 불변을 확인한다 per SC-017
