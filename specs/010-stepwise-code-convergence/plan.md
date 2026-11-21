# Implementation Plan: 꾸며낸 최소 코드에서 원본 코드까지 단계별로 구체화해 보여 주기

**Branch**: `010-stepwise-code-convergence` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-stepwise-code-convergence/spec.md`

## Summary

### 블록 구조를 아는 언어로 넓히기 (2026-11-18, 아래의 모든 앞선 설계보다 우선)

선언 찾기와 한 겹씩 펼치기를 Kotlin에서 **블록 구조를 아는 프로그래밍 언어 전부**로 넓힌다(spec FR-002·017a, SC-014). 결정과 근거는 [research.md](research.md) S11에 있다. 바로 아래 절(S10)의 "선언 찾기·트리는 Kotlin만"을 대체하고, 파일 단위 노드 규칙은 그대로 쓴다.

- **`LANGS`**(`scripts/stages.py` 안의 표): 확장자 → 언어 프로필. 중괄호 계열 Kotlin·Java·Scala·Groovy·Swift·C#·Go·Rust·Dart·JavaScript·TypeScript·C·C++, 들여쓰기 계열 Python. Kotlin 프로필은 지금 상수를 그대로 가리킨다.
- **언어를 받는 함수**: `mask_code`, `find_declaration`, `_declaration_end`, `analyse`, `split_items`, `build_tree`, 여러 줄 문자열 판정이 프로필을 인자로 받는다(기본값 Kotlin). 들여쓰기 계열만 항목 나누기(`split_items_indent`)와 선언 끝을 따로 둔다.
- **범위 확인**: Kotlin 밖의 언어에서 찾은 선언 범위는 괄호 짝·머리 줄의 이름·들여쓰기로 확인하고, 아니면 찾지 못한 것으로 본다.
- **`locate_range`·`node_tree`·`source_lang`**: "Kotlin인가" 대신 "프로필이 있는가"로 가른다. 코드 블록 이름은 프로필의 `fence`(`java`, `typescript`, `python` …), 프로필이 없으면 지금처럼 소문자 확장자다.
- **바뀌지 않는 것**: Kotlin 노드의 원본 범위·트리·문서(시험 기대 결과 그대로), `outline.json` 형식과 검사, 장면 그리기, 단계 정의, 설정, 내부 작업 파일 이름.
- **바꾸는 파일**: `scripts/stages.py`, `SKILL.md`·README 두 벌의 언어 범위 문장, `test_learning_stages.py`(언어별 시험 원본), `fixtures/expected/others*.md`(Java 노드 `LegacyBridge`가 이제 선언을 찾음), 이 Spec의 research·계약·quickstart.

**Constitution Check (이 개편)**
- I. 통과: 새 의존성·설정이 없다. 언어마다 스캐너를 새로 쓰지 않고 값의 표 하나와 들여쓰기 계열의 두 함수만 더한다. 파서 라이브러리는 설치 단계 때문에 기각했다(S11). 아래 Complexity Tracking을 보라.
- II. 통과: 010 Spec의 갱신이다.
- III. 해당 없음: 요구 변경이다(FR-002, SC-014).

### 원본 언어와 파일 단위 노드 (2026-11-18)

Kotlin만 받던 제한을 없애고, 노드가 파일 자체를 가리키면 파일 전체를 원본 범위로 삼는다(spec FR-001a·002·006·017·017a, SC-013). 결정과 근거는 [research.md](research.md) S10에 있다.

- **`read_source`**: `.kt`·`.kts`가 아니면 멈추던 검사를 없앤다.
- **`locate_range`**(새 함수, prepare와 build의 확인이 함께 씀): Kotlin이면 지금처럼 선언을 찾는다. 선언이 없거나 Kotlin이 아니면, 노드 Id나 표시 이름이 파일 이름·확장자 뺀 이름·Kotlin 파일 클래스 이름(`ColorKt`)과 같은지 본다. 같으면 파일 전체를 원본 범위로 하고 `range.whole_file`을 참으로 둔다. 둘 다 아니면 이유를 표시한다.
- **`analyse`/`build_tree`**: `whole_file` 인자를 더한다. Kotlin 파일 단위 노드는 맨 앞의 빈 줄·주석·`@file:`·`package`·`import`를 루트의 자기 줄로 두고, 나머지를 최상위 항목으로 나눈다. Kotlin이 아닌 원본은 트리를 만들지 않아 사용 상황 → 원본이 된다.
- **`fence`/`extract_last_stage`**: 코드 블록 언어를 원본에 맞춘다(Kotlin은 `kotlin`, 그 밖은 소문자 확장자). 마지막 단계를 꺼내는 정규식은 언어 이름을 가리지 않는다.
- **바뀌지 않는 것**: 노드 이름과 같은 Kotlin 선언을 찾는 노드의 원본 범위·트리·문서, `outline.json` 형식과 검사, 단계 정의, 설정, 내부 작업 파일 이름(`.kt`), 상자 형식.
- **바꾸는 파일**: `scripts/stages.py`, `SKILL.md`(설명과 본문의 Kotlin 전용 문구), `stage1-prompt.md`(Kotlin 전용 문구가 있으면), `README.md`·`README.ko.md`(이 스킬 소개에 Kotlin 전용 문구가 있으면), `test_learning_stages.py`(XML 파일 단위 노드, Kotlin 파일 단위 노드, Kotlin이 아닌 선언 노드 시험), 이 Spec의 research·data-model·계약·quickstart.

**Constitution Check (이 개편)**
- I. 통과: 새 설정·의존성·장면 종류가 없다. 언어별 문법 규칙을 더하지 않는다. 모든 언어에 두는 규칙은 "이름이 파일을 가리키면 파일 전체" 하나다. 다른 언어로 스캐너를 넓히는 방법과 언어별 대응표는 기각했다(S10).
- II. 통과: 010 Spec의 갱신이다.
- III. 해당 없음: 요구 변경이다(FR-017, SC-013).

### 붙는 선언 좁히기 (2026-11-18)

붙는 선언을 **한 줄 선언**으로 좁힌다(spec FR-005a(4), SC-012). 결정과 근거는 [research.md](research.md) S9에 있다.

- **`build_tree`**: 루트 항목 가운데 비공개 멤버를 붙는 선언으로 돌리는 조건에 "선언 줄이 하나"를 더한다. 여러 줄 비공개 멤버는 공개 멤버와 같은 루트 자식이 되어, 이미 있는 영역 나누기·외길 병합·묶음·펼치기가 그대로 적용된다. 한 줄 판정은 항목의 코드 줄 수다. 주석과 따로 선 어노테이션은 이미 `split_items`에서 코드 줄과 따로 모이므로 새 규칙이 필요 없다.
- **바뀌지 않는 것**: `outline.json` 형식, 검사, 단계 순서, 장면 그리기, 붙는 선언을 처음 쓰이는 단계에 두는 `attach_steps`, 설정, 1단계 프롬프트. 여러 줄 비공개 멤버가 없는 노드는 스코프 트리와 결과가 글자까지 같다.
- **바꾸는 파일**: `scripts/stages.py`(조건 한 줄), `stages.md`·`SKILL.md`(붙는 선언 설명에 "한 줄"), `test_learning_stages.py`(여러 줄 비공개 멤버 시험), 이 Spec의 research·data-model·계약·quickstart.

**Constitution Check (이 개편)**
- I. 통과: 새 개념·설정·의존성이 없다. 예외(붙는 선언)의 범위를 줄일 뿐이다. 붙는 선언에 따로 펼치기 단계를 주는 방식은 새 개념을 들이므로 기각했다(S9).
- II. 통과: 010 Spec의 갱신이다.
- III. 해당 없음: 요구 변경이다(FR-005a(4), SC-012).

### 스코프 트리 정제 (2026-11-17)

펼치기 단위를 "본문의 최상위 문장"에서 **스코프 트리의 묶음**으로 바꾼다. 설계 전체의 기준은 구조에서 오는 최적화다. 원본 크기에 비례하는 비용은 그대로 두고, 같은 줄을 두 번 보이기, 다시 읽기, 기계적으로 정할 일을 모델에게 맡기기, 호출 추가, 전부 다시 쓰기 같은 구조적 낭비를 없앤다(spec SC-009). 결정과 근거는 [research.md](research.md) S1~S8에 있다.

- **`prepare`**: 노드 원본 범위를 스코프 트리로 나눈다(S1). 기존 `analyse`의 항목 나누기를 영역 하나를 나누는 함수로 일반화해 재귀로 쓴다. 영역은 블록·여러 줄 인자 목록·여러 줄 체인이고, 외길은 합친다. 단위 목록 대신 후위 순서의 **스코프 목록**을 출력한다. 원본의 각 줄은 한 번만 나오고, 자식 스코프는 `⟨#n⟩`로 접힌다(S2).
- **메인 에이전트**: 스코프 목록을 한 번 읽고 `work/outline.json`에 스코프마다 한 줄(목적 문장, `with`, `sep`)을 쓴다(S3·S4). 문장·묶음용 서브에이전트는 두지 않는다. 지금도 메인 에이전트가 원본을 한 번 읽으므로 새 읽기가 없고, 서브에이전트를 더하면 원본과 무관한 고정 비용(시험에서 약 4.8만 토큰)이 호출마다 든다. 상황 서브에이전트는 원본을 몰라야 하므로 합칠 수 없다.
- **`build`**: 검사(S5)를 하고, 틀린 스코프마다 한 줄씩 알린다. 단계 트리, 번호, 장면, 붙는 선언을 만든다(S6). 모두 연 장면 = 원본이라는 검증은 그대로다.
- **없애는 것**: 접기, 4개 합치기, 단위 목록, 단위 검사(S7). 설정, 1단계 프롬프트, 문서 상자 형식은 바꾸지 않는다.
- **바꾸는 파일**: `scripts/stages.py`, `stages.md`(펼치기 정의), `SKILL.md`(3단계 outline 입력 설명), `test_learning_stages.py`, 이 Spec의 계약·데이터 모델·quickstart. 장면 그리기는 scratchpad 시제품(`trial_dfs.py`, `trial_bu.py`)에서 손으로 만든 트리로 검증한 규칙을 옮긴다.

**Constitution Check (이 개편)**
- I. 통과: 새 설정·의존성이 없다. 트리는 Kotlin 파서가 아니라 기존 마스킹·괄호 깊이 판단의 재귀다. 외길 병합은 규칙 하나를 더하지만, 늘 뻔한 판단 하나와 빈 장면 하나를 없앤다. 아래 Complexity Tracking을 보라.
- II. 통과: 010 Spec의 갱신이다.
- III. 해당 없음: 요구 변경이다(단위 정의·성공 기준).

### 단위 펼치기 (아래의 모든 앞선 설계보다 우선)

단계는 사용 상황(`prose`) → 윤곽(`outline`) → 펼치기(`unfold`, 단위마다 반복) → 원본(`source`)이다. 모든 코드 장면은 `stages.py`가 원본 범위와 펼치기 입력에서 만든다. 메인 에이전트가 단계마다 수정 블록을 쓰던 `begin`/`apply`와 `edits.txt`, `work/02…` 작업 파일은 제거한다.

- `prepare`: 지금처럼 원본 범위를 자르고, 노드마다 펼치기 단위(spec FR-005a)를 계산해 manifest에 둔다. 단위별 원본 줄(범위 기준 줄 번호, 주석 포함)을 한 번만 출력해 메인 에이전트가 자리표시자와 접기를 정하게 한다. 1단계 프롬프트에는 구조 뷰에서 Mermaid `click` 줄을 뺀 내용을 넣는다(마우스오버 문구가 Responsibility·Collaboration을 되풀이해 프롬프트의 약 27%를 차지했다).
- 메인 에이전트: `work/outline.json` 하나에 노드별 `placeholders`와 `folds`를 쓴다.
- `build`: 펼치기 입력을 검증한다(개수, 빈 문장, 책임 줄과 같은 문장, 단위 밖이나 겹치는 접기). 장면을 만들고, 모두 펼친 장면이 원본과 같은지와 마지막 장면이 원본 범위와 같은지 확인한 뒤 문서를 쓴다.
- 단위 계산은 `mask_code`로 문자열·주석을 가린 뒤 괄호 깊이와 줄 끝·줄 머리의 이어짐 표시로 본문의 최상위 항목을 나눈다. 시제품(`tmp/unfold_proto.py`)으로 북마크 예제 7개 노드에서 모두 펼친 장면이 원본에서 주석을 뺀 것과 같음을 확인했다. 이번 구현에서는 주석을 멤버와 함께 펼치므로 모두 펼친 장면이 원본과 같아야 한다.
- 토큰: 북마크 예제 기준으로 메인 에이전트가 읽는 코드는 21,007자에서 약 7,900자로, 쓰는 입력은 11,583자에서 약 1,000자로 줄고, 주고받기는 7번에서 1번으로 준다.

**Complexity Tracking**: `begin`/`apply` 흐름을 지우고 단위 계산·장면 렌더링을 더한다. 모델이 장면 코드를 쓰는 더 단순한 방법은 노드·실행마다 나누는 크기가 달라지는 문제(사용자 우려)를 막지 못해 택하지 않는다.


### 첫 장면 정리 (앞선 장면 분리·책임 틀 통합 설계보다 우선)

첫 장면은 `kind=prose`인 상황 문단 하나다. 책임 문장은 상자 위 책임 한 줄이 맡으므로 격리 프롬프트는 그 문장을 되풀이하지 말고 책임 한 줄에 없는 상황만 쓰게 한다. 첫 장면에서 책임 틀을 없애고 `intro` 표현과 그 분리·거부 처리를 제거한다. 문장 장면 다음의 첫 코드 장면은 `begin`이 노드 이름만 담은 `이름 {`·`}` 작업 파일로 시작시키며, 이 시작 파일은 화면에 보이지 않는다. 책임 자리표시자는 선언의 종류 단계에서 처음 넣고 책임 한 줄을 그대로 되풀이하지 않는다. 현재 예제는 이후 코드 단계를 그대로 두고 첫 장면만 다시 쓴다.

### 2026-11-16 학습 단계 개편 (초기 설계보다 우선)

`stages.md`에 `표현`(`prose`/`code`, 기본 `code`), `반복`(`dependency`) 선택 필드를 추가한다. 첫 상황은 격리된 에이전트가 구조 뷰만 보고 쓰고, 상황과 책임은 하나의 첫 장면으로 작성하고 책임 틀부터 메인 에이전트가 작성한다. 가상의 API 발명 규칙은 제거한다. 단계의 정본은 이 파일 하나다.

직접 화살표와 라벨을 순서대로 읽어 Node의 `dependencies`로 보존한다. `prepare`는 반복 템플릿을 최대 직접 의존 수만큼 펼치고 노드별 상대를 `targets` 맵에 기록한다. 대상 없는 장면은 그 노드 화면에서 건너뛰고 번호를 다시 매긴다. `begin`은 이번 상대를 출력한다. 단계에 질문 문구는 표시하지 않는다. 기본 별명으로 반복 전체를 숨길 수 있고 합친 몫은 대상 정보를 보존한다. prose 숨기기는 다음 코드에 문장을 합치지 않는다.

내부 작업 파일 `.kt`는 유지한다. `kind=prose`는 HTML 이스케이프한 일반 문단으로 렌더링하며 fence·diff가 없다. code 장면끼리만 diff를 적용한다. 바깥 제목은 모든 장면에서 구조 뷰의 노드 이름을 그대로 사용한다. 상황 본문의 식별자 생략을 제목까지 확장하지 않는다. 노드 책임 고정 줄·분할·넘기기는 유지한다. 원본 없는 노드는 상황 장면까지만 생성한다. 마지막 원본 검증은 노드별 실제 마지막 번호를 사용한다. 기존 manifest는 새 필드 부재를 code로 처리한다.

기존 7단계 fixture는 테스트에서 legacy 정의를 명시해 회귀를 확인한다. 새 기본 정의는 학습 흐름 자동 테스트와 실제 북마크 7개 노드로 검증한다. 원본 및 구조 뷰는 보존한다. 새 의존성·설정 옵션은 없다. 헌법 I·II 통과, III 해당 없음. 실제 인지 부하 감소를 실측했다고 주장하지 않는다. 아래 과거의 가상 첫 코드·고정 7단계 전제는 대체된다.

새 스킬 `revealing-code-step-by-step`를 더한다. 이 스킬은 구조 뷰 파일(`.zenuml/<slug>.architecture.md`) 하나를 받아, 노드마다 상자 하나씩 정제 단계를 넘겨 보는 문서를 만든다. 첫 단계는 원본을 모르고 지어낸 최소 Kotlin 코드이고, 마지막 단계는 원본 파일에서 그 노드의 선언 구간을 그대로 잘라낸 코드다.

단계 목록은 스킬 폴더의 단계 정의 파일 `stages.md` 한 곳에만 둔다. 단계마다 보일지는 스킬 설정 `settings.jsonc`의 `stages` 맵(별명 → `true`/`false`)으로 정한다. 끈 단계는 만들지 않고, 그 단계가 맡던 변화는 다음에 보이는 단계에 합친다. 보이는 단계끼리 번호를 다시 매긴다(spec FR-009a). 결정적으로 정해지는 일은 번들 Python 스크립트 `scripts/stages.py`가 맡는다.

- `prepare`: 설정과 요청의 단계 보이기를 반영해 이번에 만들 단계 목록을 정한다. 구조 뷰를 읽고, 노드마다 원본 범위를 찾아 잘라 두고, 문서를 어떻게 나눌지 정한다.
- `begin`: 다음 단계의 작업 파일을 직전 단계에서 복사해 둔다.
- `build`: 단계별 문서를 조립하고, 마지막 단계가 원본 범위와 같은지 확인한다. 직전 단계와 달라진 줄은 VS Code의 git 변경 표시처럼 칠한다(추가는 초록, 변경은 파랑, 삭제는 빨간 삼각형). 이때 Kotlin 구문 색칠은 유지한다(research R7).

모델이 쓰는 것은 두 가지뿐이다.

- 1단계 코드: 원본을 모르는 새 서브에이전트가 구조 뷰 내용만 받아서 쓴다.
- 중간 단계 코드: 메인 에이전트가 복사된 직전 단계 파일을 고친다. 고칠 범위는 그 단계 정의, 구체화 사다리(보조 표기 `...`·`⟨설명⟩`), 다른 노드의 이름 맞추기 규칙이 정한다.

## Technical Context

> 아래 Technical Context와 Project Structure는 초기 설계 때의 기록이다. 현재 동작은 Summary 맨 위 절(스코프 트리 정제)이 우선한다.

**Language/Version**: Python 3.9 이상에서 동작하는 스크립트와 Markdown 지침 문서(SKILL.md, `stages.md`)로 이뤄진다. 스크립트는 표준 라이브러리만 쓰고 3.10 이상 전용 문법을 쓰지 않는다. 003 스킬과 같은 조건이다. 산출물의 코드는 노드 원본의 언어다(spec FR-006, 2026-11-18 전에는 Kotlin).

**Primary Dependencies**: 없음. 표준 라이브러리(`argparse`, `json`, `re`, `pathlib`, `shutil`, `difflib`, `html`, `urllib.request`)만 쓴다. 003 스킬의 코드는 import하지 않는다(스킬 독립성, research R2).

**Storage**: 파일만 쓴다. 스킬 폴더의 `settings.jsonc`·`settings.schema.json`은 읽기만 한다.

- 입력(읽기만): `.zenuml/<slug>.architecture.md`와, 그 링크가 가리키는 원본 파일(언어 제한 없음, 2026-11-18)
- 산출물: `<output.directory>/<slug>.stages/` 아래의 문서(`*.md`)와 작업 폴더(`work/`). 기본값으로는 `.zenuml/<slug>.stages/`

**Testing**: 자동화 테스트 프레임워크는 없다(기존 스킬과 같다). [quickstart.md](quickstart.md)에 다음 세 가지 확인을 둔다.

- 고정 입력(fixture)에 스크립트를 돌려 기대 결과와 바이트 비교하기. fixture는 작은 구조 뷰, 여러 노드가 든 Kotlin 원본, 손으로 쓴 단계 작업 파일로 이뤄진다.
- VS Code 미리보기를 수동으로 확인하기
- 실제 구조 뷰 하나로 처음부터 끝까지 돌려 보기

**Target Platform**: Claude Code(Windows/macOS/Linux)에서 돌린다. 1단계는 Agent 도구로 띄운 새 general-purpose 서브에이전트가 만든다(fork는 쓰지 않는다). 결과는 VS Code 1.146 내장 Markdown 미리보기에서 확인한다. 기준은 실제 VS Code 미리보기 DOM에서 검증한 시제품 [prototype/code-gallery.md](prototype/code-gallery.md)이다.

**Project Type**: Claude Code skill(지침 문서 + 번들 스크립트)

**Performance Goals**: 모델 출력 토큰을 줄인다.

- 마지막 단계는 모델이 쓰지 않는다. 스크립트가 원본 범위를 복사한다.
- 중간 단계는 직전 단계의 복사본을 Edit로 고치므로, 바뀌지 않는 부분은 다시 쓰지 않는다.
- 스크립트는 구조 뷰 하나(노드 수십 개, 원본 수천 줄)를 몇 초 안에 처리한다.

**Constraints**:

- 원본 코드베이스와 구조 뷰 파일은 바꾸지 않는다(FR-019).
- 1단계를 만드는 주체에는 구조 뷰 내용만 준다(FR-003).
- 단계의 별명·순서·수는 `stages.md`만으로 정해진다(FR-007, SC-004).
- 마지막 단계는 원본 범위와 같은지 확인한다(FR-010).

**Scale/Scope**:

- 새 스킬 1개: SKILL.md, `stages.md`, `settings.jsonc`, `settings.schema.json`, `scripts/stages.py` 1개
- 새 설정 옵션 2개: `stages`(단계 별명 → 보이기), `output.directory`(결과 위치, 구조 뷰 폴더 기준 상대 경로, 기본값 `.`). 설정 로더는 기존 스킬과 같은 동작을 `stages.py` 안에 옮겨 쓴다.
- `.gitignore`의 허용 목록에 새 스킬 폴더 추가
- README 영어·한국어 두 벌에 항목 추가
- spec FR-008의 7단계 표는 `stages.md`로 옮기고, spec에는 링크만 남긴다.
- 003 스킬은 바꾸지 않는다(FR-001).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 원칙 | 판단 | 근거 |
|---|---|---|
| I. 오버엔지니어링 금지 | 통과 | 설정 옵션은 spec이 요구하는 두 개만 둔다 — `stages`(FR-009a), `output.directory`(FR-019a). 설정 파일 형식과 주석 규칙은 기존 두 스킬의 관례(007)를 그대로 따르고, 로더도 그 동작을 옮겨 쓴다(R12). 스크립트는 파일 하나이고, 하위 명령 셋은 각각 spec 요구를 하나 이상 맡는다(R4). 새 의존성은 없다. URL 원본 지원은 spec Assumptions("원본 접근")가 요구하는 만큼만 하며, GitHub blob 주소 변환 하나로 한정한다(R8). 선언 구간 찾기는 Kotlin 전체 파서가 아니라 문자열·주석·괄호만 아는 최소 스캐너로 한다(R5). |
| II. 요청은 해당 Spec에서 진행 | 통과 | 010 spec의 구현이다. 003의 동작은 바꾸지 않는다. |
| III. 출력 변동성 수정에 Spec Kit 미사용 | 해당 없음 | 새 기능이다. |

Phase 1 설계를 마친 뒤 다시 확인했고, 달라진 것은 없다.

## Project Structure

### Documentation (this feature)

```text
specs/010-stepwise-code-convergence/
├── plan.md              # 이 파일
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── stages-contract.md   # stages.md 형식, stages.py 실행 규약, 작업 폴더와 문서 형식
├── prototype/
│   └── code-gallery.md      # 기존 — 넘겨 보기 구조의 원본
└── tasks.md             # /speckit-tasks 산출물
```

### Source Code (repository root)

```text
.agents/skills/revealing-code-step-by-step/      # 신규
├── SKILL.md            # 작업 순서: prepare → 1단계 서브에이전트 → 단계마다 begin+apply → build → reply 응답
├── stage1-prompt.md    # 1단계 서브에이전트 지시의 틀 — prepare가 채워 work/stage1-prompt.md로 씀
├── stages.md           # 단계 정의 파일 — 단계 구성을 고치는 유일한 곳(spec FR-007·008)
├── settings.jsonc      # 단계마다 보일지(stages 맵), 결과 위치(output.directory) — 007 주석·토큰 기호 관례
├── settings.schema.json # 두 옵션의 정의(stageToggles 타입 기본값 {}, relativePath 타입 기본값 ".")
└── scripts/
    └── stages.py       # python scripts/stages.py prepare|begin|apply|build ...

.gitignore              # 개정 — !.agents/skills/revealing-code-step-by-step/ 추가
README.md, README.ko.md # 개정 — "추가 기능"·"요구 사항"에 이 스킬 항목
specs/010-stepwise-code-convergence/spec.md   # 개정 — FR-008의 표를 stages.md 링크로 바꿈

specs/010-stepwise-code-convergence/fixtures/   # 신규 — quickstart용 입력·작업 파일·기대 결과
```

**Structure Decision**: 003과 성격이 달라 스킬을 따로 둔다(FR-001). 스크립트는 이 스킬의 `scripts/`에 두고, 다른 스킬의 코드를 import하지 않는다.

`stages.md`는 SKILL.md와 분리한 단계 정의 파일이고, `settings.jsonc`는 단계 구성은 그대로 두고 보일지만 정하는 설정이다. 설정은 단계를 별명으로 가리키므로, 단계를 넣거나 옮겨도 설정을 고칠 필요가 없다(SC-006). 스크립트는 여기서 별명·순서를 읽고, 모델은 단계마다 바꿀 것을 읽는다.

산출물은 `.zenuml/<slug>.stages/`에 둔다. 원본 코드베이스의 빌드 대상과 섞이지 않게 하기 위해서다(FR-019).

### 2026-11-20 호환성 보완

003 FR-036의 규격 표시어 라벨은 기존 `scripts/stages.py`의 `clean_name`에서 처리한다. 변화 표시와 HTML 태그를 제거한 뒤 원본 라벨의 마지막 `&nbsp;` 뒤 토큰을 실제 이름으로 반환한다. 003 FR-037의 파일 이름 표시 `<span class=srcFile>…</span>`는 태그와 함께 내용째 지운다. 새 파서나 공용 모듈은 만들지 않고, 기존 `test_learning_stages.py`에 복합 표시어·변화 표시·기존 라벨을 함께 검사하는 회귀를 추가한다.

### 2026-11-21 GitHub CSS 원문 접기

`stages.py`가 이미 문서 끝에 붙이는 기본·diff `<style>`을 `docs/hover-tooltip-test/details-wrapped-style.md`와 같은 `<details>` 하나로 감싼다. 기본 CSS에 wrapper 숨김 규칙 하나를 더하고, 기존 `strip_diff_layer`의 정확한 문자열 제거 경계를 유지해 diff CSS만 뺀 결과가 `with_diff=False` 결과와 계속 같게 한다. 별도 스크립트·설정·의존성은 추가하지 않는다. 네 사용자 스킬 중 구조 뷰와 이 스킬만 Markdown `<style>`을 출력하며, ZenUML 생성은 미사용, 내보내기는 임시 HTML 내부 CSS라 변경하지 않는다.

## 2026-11-21 토큰 효율 보완 계획

이미 짧은 SKILL.md의 description과 도입부 중복만 제거한다. outline의 목적 문장과
그룹 판단은 모델 판단으로 유지하며 새 reference나 스크립트를 만들지 않는다.

## Complexity Tracking

| 더하는 복잡도 | 필요한 이유 | 더 단순한 방법을 고르지 않은 이유 |
|---|---|---|
| 스코프 트리(영역 나누기의 재귀) | 여러 겹이 한 장면에 열리지 않게 한다(SC-010) | 최상위 문장 단위에 문장 지침만 더하는 방법은 BulletedListTextField에서 60줄 장면을 막지 못했다. 원본 순서의 연속 구간으로 자르는 방법은 시험에서 상관없는 것을 한 단계로 묶었다. |
| 단계 트리와 들여 쓴 번호 자리표시자 | 윤곽에서 모든 단계를 보인다(FR-004) | 별도 목차는 사용자가 자리표시자 안의 번호를 원해 취소했다. |
| 언어 프로필 표와 들여쓰기 계열의 항목 나누기·선언 끝 | Kotlin 밖의 언어에서도 선언을 찾고 펼친다(FR-002, SC-014) | Kotlin만 받는 방법은 근거 없는 제한이었다. 파일 단위 노드만 받는 방법은 Java·Python의 선언 노드를 멈추게 한다. 언어마다 스캐너를 따로 쓰면 같은 코드가 언어 수만큼 생긴다. |
