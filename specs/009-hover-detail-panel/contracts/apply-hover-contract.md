# Contract: `apply_hover.py`

`generating-architecture-views` 스킬에 들어가는 스크립트의 실행 규약과, 구조 뷰 파일에 가하는 변환 규칙.

## 실행

```text
<python> .claude/skills/generating-architecture-views/scripts/apply_hover.py <구조 뷰 파일> [--enabled=<true|false>] [--responsibility=<항목,…>] [--collaboration=<항목,…>] [--position=<bottom|node>] [--source-file=<true|false>] [--source-file-position=<left|right>]
```

| 인자 | 뜻 |
|---|---|
| `<python>` | 환경에 있는 Python 3.9 이상. `python3` → `python` → `py -3` 순으로 찾는다. 설치 단계는 없다. |
| `<구조 뷰 파일>` | 필수. `.zenuml/<slug>.architecture.md` 같은 구조 뷰 파일 하나. 제자리에서 덮어쓴다. |
| `--enabled` 등 | 선택. 이번 실행에서만 설정 값을 덮는다(FR-014, research R4). `--responsibility=`처럼 값이 비면 `[]`. 검증은 설정 값과 같다. |

- 설정은 스크립트가 들어 있는 스킬 디렉터리의 `settings.jsonc`·`settings.schema.json`을 읽는다(실행 위치와 무관).
- **표준 출력**: 사람이 읽는 결과 한 줄 — `hover 적용: <파일> (노드 N개에 패널, 위치 <position>)`, `hover 해제: <파일>`, 또는 `변경 없음: <파일>`. 그 뒤에 설정 안내 줄(`⚙️ 설정 안내: …`, 007 형식)이 있으면 한 줄씩.
- **종료 코드**: `0` 성공(변경 없음 포함). `1` 인자 오류 또는 파일을 읽을 수 없음. `2` 구조 뷰 형식이 아님(`### Dependency` 아래 Mermaid 코드 블록이 없음) — 이때 파일은 건드리지 않는다.
- 파일 내용이 바뀌지 않으면 파일을 다시 쓰지 않는다(수정 시각 유지).
- 파일은 UTF-8로 읽고 쓰며, 표준 출력도 UTF-8로 낸다(Windows 콘솔 기본 인코딩에 기대지 않는다).
- 줄바꿈 형식(LF/CRLF)과 파일 끝 줄바꿈 유무는 입력을 따른다.

## 변환 규칙 (켜짐)

입력 파일에서 다음만 바꾼다. 그 밖의 줄은 바이트 단위로 그대로 둔다.

1. **링크 `click` 줄** — `click Id "대상" "툴팁"`: NodePanel이 있는 노드는 세 번째 인자를 NodePanel로, 없는 노드는 파일 이름으로 둔다. 대상은 바꾸지 않는다(FR-017).
2. **`hoverOnly` 줄** — 링크 없는 노드 중 NodePanel이 있는 노드마다 `  click Id hoverOnly "NodePanel"`. 위치는 마지막 링크 `click` 줄 다음(링크 `click` 줄이 없으면 CRUD 표시 절의 마지막 `classDef crud*` 줄 다음에 빈 줄 하나를 두고), 노드 선언 순서대로. 이전 실행이 남긴 `hoverOnly` 줄은 모두 지우고 다시 만든다.
3. **`cursor:auto`** — `hoverOnly` 줄을 단 노드의 색상 `classDef` 줄 끝에 `,cursor:auto`. 색상 클래스는 노드마다 하나씩이므로(003 FR-008b) 그 노드에만 적용된다. 이전 실행이 붙인 `,cursor:auto`는 먼저 모두 지운다.
4. **패널 모양 블록** — 파일 끝의 `div.mermaidTooltip`을 담은 새 `<details>…</details>` 블록이나 기존 생 `<style>…</style>` 블록을 지우고, 파일 끝에 빈 줄 하나 + 현재 `position`의 고정 wrapper를 붙인다. 블록 내용은 [style 블록 원본](#style-블록-원본)과 바이트 단위로 같다.

## 파일 이름 표시 (003 FR-037)

`dependency.sourceFile.enabled`가 켜져 있고 다이어그램의 `class … srcFile` 줄에 링크 `click`이 있는 노드가 있으면, 패널 모양 블록의 `<style>` 끝에 그 노드마다 아래 규칙을 하나씩 붙인다(노드 선언 순서). hover가 꺼짐이어도 이 규칙이 있으면 wrapper 숨김 규칙과 이 규칙만 담은 같은 wrapper를 붙인다. `SIDE`는 `dependency.sourceFile.position`, `<color>`는 노드의 색상 class, `<file>`은 링크 대상의 파일 이름(`"`·`\`는 `\` 이스케이프)이다.

```css
.node.srcFile foreignObject { overflow: visible; }
.node.srcFile .label foreignObject > div { position: relative; }
.srcFile.<color> .nodeLabel::before { content: "<file>"; position: absolute; top: -9px; SIDE: -13px; font-size: 10px; line-height: 1; font-weight: normal; color: #9CA3AF; }
```

공통 두 규칙은 한 번만 쓴다. `--source-file`·`--source-file-position`은 이번 실행에서만 두 설정 값을 덮는다.

## 변환 규칙 (꺼짐)

유효 설정이 꺼짐이거나 NodePanel이 하나도 없으면(파일 이름 규칙이 있으면 4는 위 절을 따른다):

1. 링크 `click` 줄의 툴팁을 파일 이름으로 되돌린다(research R11).
2. `hoverOnly` 줄을 모두 지운다.
3. `classDef` 줄 끝의 `,cursor:auto`를 지운다.
4. 패널 모양 블록과 그 앞 빈 줄을 지운다.

결과는 기능 도입 전 규칙으로 만든 파일과 같다(SC-005).

## NodePanel 형식

[data-model.md의 NodePanel](../data-model.md#nodepanel-노드-하나의-툴팁-문자열)과 [research R7·R8](../research.md#r7-본문-항목과-노드-연결)을 따른다. 예(기본 설정):

```text
<b>MemoViewModel</b><br/><b>책임 (추상)</b>: 화면 상태를 계산하고 사용자 이벤트를 처리한다.<br/><b>역할 (구체)</b>: …<br/><br/><b>MemoUiState에 의존한다 (생성)</b><br/><b>책임의 경계</b>: …<br/><b>분리 이유 &amp; 합리성 평가</b>: …<br/><br/><b>MemoRepository에 의존한다 (호출)</b><br/>…
```

문자열 안에 `"`는 남지 않는다.

## style 블록 원본

- wrapper와 설명: `docs/hover-tooltip-test/details-wrapped-style.md`의 `<details class="zenuml-hover-style">` 구조와 GFM 공식 문서 링크.
- `bottom`: 같은 검증 문서의 `<style>` 블록(아래 패널 고정, `columns: 25em`, 밑줄 규칙, wrapper 숨김 규칙).
- `node`: `docs/hover-tooltip-test/node-25em.md`의 CSS를 같은 wrapper에 넣은 블록(폭 `25em`, `width: max-content`, `position-try-fallbacks`, `html { position: relative; }`, hover 중이 아닐 때 `display: none`, 밑줄 규칙, wrapper 숨김 규칙).

두 블록은 `scripts/hover/style_blocks.py`에 상수로 옮기며, 테스트 키트와 달라지면 테스트 키트 쪽을 기준으로 맞춘다.

## SKILL.md 쪽 규약

- 저장 순서: 구조 뷰 파일 → 피드백 로그 → `apply_hover.py` 실행(파일 이름 표시도 이 스크립트가 그리므로 hover 설정과 무관하게 항상). 요청 문장이 hover 값을 밝혔으면 해당 옵션만 명령줄에 붙인다.
- 스크립트의 설정 안내 줄은 채팅 응답 끝 설정 안내에 합친다(같은 안내를 두 번 쓰지 않는다).
- 종료 코드가 `0`이 아니면 구조 뷰 파일은 그대로 두고, 응답에 한 줄로 알린다.
- Python 3.9 이상을 찾지 못하면 스크립트를 건너뛴다. 구조 뷰는 기능 도입 전 형태(툴팁은 파일 이름)로 남고, 응답 끝에 `⚙️ hover 건너뜀: Python 3.9 이상을 찾지 못함` 한 줄을 남긴다. 구조 뷰 생성 자체는 실패로 보지 않는다.
- AP-13c 허용 목록에 패널 모양 블록, `hoverOnly` 줄, `,cursor:auto`를 더한다(FR-016). 모델은 이 셋을 직접 쓰지 않는다.
