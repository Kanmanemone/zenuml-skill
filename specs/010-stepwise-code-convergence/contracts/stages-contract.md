# Contract: 단계 정의 파일, `stages.py`, 산출물 형식

## 1. 단계 정의 파일 `stages.md`

위치는 `.claude/skills/revealing-code-step-by-step/stages.md`이다.

```markdown
# 단계 정의

(자유 설명 — 스크립트는 읽지 않는다. 1원칙, 구체화 사다리 요약, spec 링크)

## 꾸며낸 뼈대

- 원본과 같아지는 것: 없음(노드 이름만 구조 뷰와 같음)
- 아직 드러나지 않은 것: 전부(원본을 모르고 지어낸 코드로 채움)

## 선언의 종류

- 원본과 같아지는 것: …
- 아직 드러나지 않은 것: …
- 보조 표기: 1단계의 지어낸 본문을 `⟨설명⟩`으로 바꾼다 …

(이하 단계마다 반복)
```

- **단계 하나의 형태**: `## ` 제목 하나와 그 아래 항목들이다. 스크립트가 읽는 항목 머리는 정확히 `- 원본과 같아지는 것:`과 `- 아직 드러나지 않은 것:` 둘이다. `- 보조 표기:`와 그 밖의 문단은 모델만 읽는다.
- **처음 내용**: spec FR-008의 7단계 표와 그 아래 문단을 옮긴다. 옮긴 뒤 spec의 FR-008에는 이 파일의 링크만 남긴다.
- **오류(종료 코드 2)**: 다음 중 하나라도 해당하면 오류로 끝난다.
  - 단계가 2개 미만
  - 별명이 겹침
  - 필수 항목이 하나라도 없음

## 2. 실행 규약

```text
<python> <skill>/scripts/stages.py prepare <구조 뷰 파일> [--show=<별명,…>] [--hide=<별명,…>] [--output-dir=<상대 경로>] [--pick=<id>:<번호>,…]
<python> <skill>/scripts/stages.py begin   <산출 폴더> <단계 번호>
<python> <skill>/scripts/stages.py build   <산출 폴더>
```

- 작업 폴더를 바꾸지 않고 실행한다. 경로는 프로젝트 루트를 기준으로 한다.
- 표준 출력에는 결과 JSON 한 줄을 낸다. 오류는 표준 오류에 한국어 한 줄로 내고, 0이 아닌 종료 코드로 끝난다.

| 코드 | 뜻 | 예 |
|---|---|---|
| 0 | 성공 | |
| 2 | 입력 문제 | 구조 뷰 형식이 아님, 노드가 없음, `stages.md` 오류, 작업 파일 누락, 이미 시작한 단계 |
| 3 | 마지막 단계가 원본 범위와 다름 | `build` 확인 실패 |

### `prepare <view>`

1. 다음 경우에는 종료 코드 2로 끝난다.
   - `<view>`가 `*.architecture.md`가 아님
   - `### Dependency` 아래에 Mermaid 블록이 없음
   - 노드가 없음
2. 설정(`settings.jsonc`)을 읽는다. 요청 옵션(`--show`, `--hide`, `--output-dir`)이 있으면 이번 실행에서 설정보다 우선한다(research R12). 산출 폴더는 `<view 폴더>/<output.directory>/<slug>.stages/`다. 이 폴더가 있으면 통째로 지우고 새로 만든다(FR-020). 지우는 것은 이 폴더뿐이다(FR-019a).
3. 단계 정의와 보이기 값으로 만들 단계 목록을 정한다(research R13).
4. 노드, 그룹, 링크를 읽고([data-model.md](../data-model.md)의 Node), 문서를 어떻게 나눌지 정한다(Document).
5. 노드마다 원본을 읽고 원본 범위를 찾는다(research R5, R8). 찾으면 `work/original/<id>.kt`에 바이트 그대로 쓴다. 이 파일은 줄바꿈 하나로 끝난다. 찾지 못하면 `skip_reason`을 다음 중 하나로 정한다.

   | 경우 | `skip_reason` |
   |---|---|
   | 링크 없음 | `원본 위치가 없어 구체화하지 않음` |
   | 폴더이거나 파일 하나로 정해지지 않음 | `링크가 파일 하나를 가리키지 않아 구체화하지 않음` |
   | `.kt`·`.kts` 아님 | `원본이 Kotlin이 아니어서 구체화하지 않음` |
   | 없거나 받지 못함 | `원본을 읽을 수 없어 구체화하지 않음 (<원인>)` |
   | UTF-8 아님 | `원본을 UTF-8로 읽을 수 없어 구체화하지 않음` |
   | 선언 0개 | `원본 파일에서 <이름> 선언을 찾지 못해 구체화하지 않음` |
   | 선언 2개 이상이고 `--pick` 없음 | `원본 파일에 <이름> 선언이 여럿 — --pick으로 하나를 골라야 함` (노드에 `candidates`가 붙는다. 모델이 고른 뒤 `--pick`으로 다시 실행) |

6. 만들 단계 목록을 `work/manifest.json`에 함께 적는다. `begin`과 `build`는 `stages.md`가 아니라 이 사본을 쓴다. 한 번 만드는 동안 정의가 바뀌지 않게 하기 위해서다.
7. 출력 JSON은 아래 형태다. `notices`는 설정 알림(`⚙️ 설정 안내: …`) 목록이고, 모델은 이것을 응답 끝에 그대로 전한다.

```json
{"dir": ".zenuml/<slug>.stages",
 "stages": [{"work": 1, "nickname": "꾸며낸 뼈대", "visible": true, "display": 1, "of": 7,
             "becomes": "…", "unrevealed": "…", "notation": null, "merged": []}, …],
 "notices": [],
 "nodes": [{"id": "OrderService", "name": "OrderService", "stage1": ".zenuml/<slug>.stages/work/01/OrderService.kt",
            "original": ".zenuml/<slug>.stages/work/original/OrderService.kt",
            "range": {"source": "../app/.../OrderService.kt", "start_line": 12, "end_line": 80},
            "contains": ["Validator"], "candidates": [], "skip_reason": null, "doc": "all.md"}, …]}
```

- `contains`: 이 노드의 원본 범위 안에 들어 있는 다른 노드의 Id 목록이다. 모델은 이 목록을 보고 중간 단계에서 그 부분을 `⟨이름⟩`으로 접어 둔다.

### `begin <dir> <k>`

- 다음을 모두 만족해야 한다. 하나라도 어긋나면 종료 코드 2로 끝난다.
  - `2 ≤ k ≤ g-1` (`g`는 만드는 단계 수, research R13)
  - `work/<k-1>`이 있음
  - `work/<k>`가 없음
- 구체화하는 노드마다 `work/<k-1>/<id>.kt`를 `work/<k>/<id>.kt`로 그대로 복사한다. 구체화하지 않는 노드는 복사하지 않는다.
- 폴더 이름의 번호는 두 자리다(`01`, `02`, …).
- 출력 JSON은 `{"stage": k, "nickname": "…", "becomes": "…", "unrevealed": "…", "notation": "…", "merged": [{"nickname": "…", "becomes": "…", "notation": "…"}], "files": [...]}` 형태다. `merged`는 꺼져서 이 단계에 합쳐진 단계들의 몫이고, 모델은 이것까지 함께 바꾼다.

### `build <dir>`

1. 작업 파일을 확인한다. `work/01`의 모든 노드 파일과, 2…g-1단계마다 구체화하는 모든 노드 파일이 있어야 한다. 빠진 것이 있으면 종료 코드 2로 끝나고 빠진 목록을 출력한다.
2. 노드마다 단계별 코드를 정한다.
   - 1…g-1단계: 작업 파일
   - g단계(마지막): `work/original/<id>.kt`
   - 구체화하지 않는 노드: 1단계 하나뿐
3. 문서마다 `<dir>/<doc>.md`를 쓴다(3절).
4. 쓴 문서를 다시 읽는다. 구체화하는 노드마다 마지막 단계의 코드 블록 내용을 꺼낸다. 원본 위치에서 파일을 다시 읽고(R8) 다시 잘라낸 구간(R5)과 비교한다. 줄바꿈 종류는 LF로 맞춘다. 하나라도 다르면 종료 코드 3으로 끝나고, 그 노드와 첫 번째로 다른 줄 번호를 출력한다. 이때 문서는 지우지 않는다.
5. 출력 JSON은 아래 형태다.

```json
{"docs": [".zenuml/…/all.md", …],
 "unchanged": {"<별명>": ["<id>", …]},
 "skipped": [{"node": "…", "reason": "…"}],
 "verified": <개수>}
```

- `unchanged`: "달라진 것이 없음"이 붙은 노드 목록이다. 모델은 이 목록으로 그 단계에서 바꿔야 할 것을 빠뜨리지 않았는지 다시 확인한다.

## 3. 문서 형식

줄 끝은 LF이고, 파일은 줄바꿈 하나로 끝난다. 구조는 [prototype/code-gallery.md](../prototype/code-gallery.md)를 따르고, 거기에 단계 제목·한 줄 설명·표시 줄을 더한다.

````markdown
# <문서 title> — 정제 단계

## <하위 그룹 또는 작은 그룹 라벨>          ← 문서 안에 구분할 그룹이 있을 때만

### <노드 이름>

<div class="stages">

<input type="radio" name="<id>" id="<id>-1" class="s1" checked>
<input type="radio" name="<id>" id="<id>-2" class="s2">
…

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/7)</span><span class="nav">←</span><label class="nav" for="<id>-2">→</label></div>
<div class="note">원본과 같아진 것: 없음(노드 이름만 구조 뷰와 같음)</div>

<div class="code">

```kotlin
…단계 코드…
```

<pre class="diff" aria-hidden="true"><code><span class="mod">…1번째 줄 글자(투명)…</span>
<span>…2번째 줄 글자(투명)…</span>
<span class="add del">…3번째 줄 글자(투명)…</span></code></pre>      ← diff 층(2단계부터). 이 요소 하나를 지우면 기존 상자만 남는다

</div>

</div>

…단계마다 stage 하나…

</div>

…노드마다 반복…

<style>
…기존 상자 규칙: 시제품의 규칙 + 단계 수만큼의 `.stages > input.sK:checked ~ .stage.sK { display: block; }` + .note·.code 규칙…
</style>

<style>
…diff 층 규칙: .diff와 add·mod·del 색칠, .code를 기준점으로 삼는 규칙…
</style>
````

- **제목**: `<k>단계: <별명> (<k>/<n>)` 형식이다(spec FR-015).
- **한 줄 설명**: 다음 셋 중 하나다.
  - 1단계: `원본과 같아진 것: <becomes>`
  - 2단계 이후이고 직전 단계와 다를 때: `원본과 같아진 것: <becomes>`
  - 2단계 이후이고 직전 단계와 같을 때: `이 단계에서는 달라진 것이 없음`
- **달라진 줄 색칠**(research R7, VS Code의 git 변경 표시 규칙): 2단계부터 직전 단계와 비교해 줄마다 종류를 정한다.
  - `add`(추가): 왼쪽 초록 막대 + 옅은 초록 줄 배경
  - `mod`(변경): 왼쪽 파란 막대 + 옅은 파란 줄 배경
  - `del`(그 줄 바로 위에서 지워짐): 빨간 삼각형. 끝에서 지워졌으면 마지막 줄에 `del-after`를 붙인다.

  diff 층(`pre.diff`)은 줄마다 span 하나를 두고, 그 안에 그 줄의 코드 글자를 이스케이프해 그대로 넣는다. 글자색은 투명이다. 종류는 클래스로 단다. 한 줄에 `add`와 `del`이 함께 붙을 수 있다. 줄 수는 코드 줄 수와 같다. 1단계와 "달라진 것이 없음"인 단계에는 diff 층을 두지 않는다.
- **기존 상자와 diff 층의 경계**(research R7의 다섯 원칙): 이 경계는 다음 세 가지로 확인할 수 있어야 한다.
  - 기존 상자의 마크업과 첫 번째 `<style>`은 diff 층을 모른다.
  - diff 층은 `pre.diff` 요소들과 두 번째 `<style>`로만 이뤄진다. 코드 위에 절대 위치로 얹히고, 자리를 차지하지 않으며, `pointer-events: none`이다.
  - 문서에서 `pre.diff` 요소와 두 번째 `<style>`을 지우면, 그 문서는 같은 단계 코드로 diff 층 없이 만든 문서와 바이트 단위로 같다.
- **코드 블록**: 펜스 길이는 코드 안에서 가장 긴 백틱 연속보다 하나 더 길게 한다(최소 3).
- **`.code` 영역**(기존 상자의 몫): 코드의 높이 상한 `min(30lh, 70vh)`과 세로·가로 스크롤을 맡는다. 코드는 `white-space: pre`로 줄바꿈하지 않는다.
- **diff 층 CSS**(두 번째 `<style>`): `.code`를 기준점으로 삼아 `pre.diff`를 코드 위에 겹친다. 줄 위치는 `pre > code` 구조와 글자가 같아서 맞는다(research R7 원칙 4). 기존 상자의 여백·줄 높이 수치를 베끼지 않는다. 가로·세로로 스크롤해도 줄을 따라간다. 색은 `--vscode-editorGutter-addedBackground`·`modifiedBackground`·`deletedBackground` 테마 변수를 쓰고, 대체 색을 함께 적는다.
- **구체화하지 않는 노드**: `### <노드 이름>` 바로 아래에 `⚠️ <skip_reason>` 한 줄을 두고, 상자에는 1단계 하나만 둔다(spec FR-017, 넘길 단계 없음).
- **같은 문서에서 Id가 겹치는 경우**: 라디오의 `name`과 `id`는 노드 Id로 만든다. 노드 Id는 구조 뷰 안에서 유일하다.
- 문서에는 단계 코드와 위 표시만 담는다(FR-018).

## 4. SKILL.md가 정하는 모델의 일

1. `prepare`를 실행한다. 종료 코드가 2이면 그 이유를 알리고 멈춘다.
2. 1단계 서브에이전트를 띄운다(R1). 서브에이전트는 `nodes[].stage1` 경로에만 쓴다.
3. k = 2…g-1마다 `begin k`를 실행하고, 출력된 파일들을 그 단계의 정의대로 Edit로 고친다. 이때 R11의 규칙을 지킨다. 원본은 `work/original/`에서 읽는다. 다음 `begin`을 실행하기 전에, 이 단계의 파일들이 R11을 지키는지 스스로 점검하고 고친다. 다음 단계가 이 단계의 복사본에서 시작하므로, 이 단계를 고칠 수 있는 것은 이때뿐이다.
4. `build`를 실행한다.
5. 종료 코드가 3이면, 만드는 동안 원본이 바뀌었거나 스크립트에 버그가 있다는 뜻이다. 작업 파일을 고치지 말고 메시지를 그대로 알린다.
6. 채팅 응답에는 문서 링크들과, 구체화하지 않은 노드가 있으면 그 목록만 넣는다.
