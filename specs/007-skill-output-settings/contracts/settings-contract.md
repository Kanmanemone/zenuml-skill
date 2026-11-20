# Contract: 스킬 설정 파일과 공통 처리

## 파일 계약

- 위치: `<skill dir>/settings.jsonc`(사용자 편집), `<skill dir>/settings.schema.json`(옵션 정의).
- `settings.jsonc`: 주석(`//`, `/* */`)을 허용하는 JSON. 최상위는 객체. 묶음 객체 아래 옵션 키. 키·값은 영어.
- 배포본 `settings.jsonc` 맨 위 두 줄과 각 옵션 바로 위 주석 형식:

  ```jsonc
  // <skill> 설정 — 요청 문장에서 다르게 말하면 그 요청에서는 말한 쪽이 우선
  // 토큰 소모(초기 기본값 대비): [-] 줄어듦  [0] 거의 같음  [+] 늘어남  [++] 큼
  {
    "<group>": {
      // <한국어 의미 한 줄> (초기 기본값: <default>)
      //   <값1> [<토큰 영향>] <뜻>
      //   <값2> [<토큰 영향>] <뜻>
      "<leaf key>": <default>
    }
  }
  ```

  값 이름은 열을 맞춰 적는다. `number`·`relativePath`는 값 목록 대신 `//   허용 [<토큰 영향>] <규칙>` 한 줄을 쓴다. 주석 내용은 옵션 정의의 `description`·`values`·`tokenImpact`·`default`와 같아야 한다.

## 공통 처리 계약 (모든 스킬 공통)

1. 실행마다 옵션 정의와 설정 파일을 새로 읽는다.
2. data-model.md "해석 규칙" 표대로 값을 정한다.
3. 안내 문구는 채팅 응답에만 붙인다(산출 파일에 넣지 않음). 형식: `⚙️ 설정 안내: <스킬 디렉터리 기준 파일 경로> — <내용>`.
4. 스킬은 설정 파일을 고치지 않는다.

## generating 스크립트 계약 (FR-017b)

- `generating-architecture-views`, `generating-zenuml-diagrams`는 각자 `scripts/read_settings.py`를 둔다(다른 스킬의 코드를 import하지 않음 — 003 FR-014). 표준 라이브러리만 쓰고 Python 3.9 이상에서 돈다.
- 인터프리터는 `python3` → `python` → `py -3` 순으로 찾되 Windows에서는 `python` → `py -3` → `python3` 순으로 찾아(Windows의 `python3`은 Microsoft Store 안내만 띄우는 경우가 많음) `<인터프리터> scripts/read_settings.py`로 실행한다. 출력은 exporting의 `read-settings.js`와 같은 한 줄 JSON `{"values": {...}, "notices": ["..."]}`이고 종료 코드는 0이다.
- 인터프리터를 찾지 못하거나 실행이 실패하면 스킬은 옵션 정의(`settings.schema.json`)의 `default`만 읽어 쓰고(`settings.jsonc`는 읽지 않음) `⚙️ 설정 안내: settings.jsonc — 설정 스크립트를 실행하지 못해 모든 값을 기본값으로 사용` 한 줄을 남긴다.

### architecture 노드 이름 적용 계약 (FR-012d)

- `dependency.nodeMarkers = true`: 실제 원본에서 확인한 선언 키워드를 이름 앞에 보이고 파일 노드의 마지막 확장자를 보인다. `false`: 선언 키워드와 마지막 확장자를 감춘다.
- `dependency.functionParentheses = true`: 실제 원본에서 함수임을 확인한 노드 이름 끝에 `()`를 정확히 한 번 붙인다. `false`: 붙이지 않는다.
- 두 값은 독립적으로 적용한다. 함수 종류를 `fun`, `def` 같은 목록으로 판별하지 않고 입력 근거로 확인한다.
- 적용 범위는 Dependency 라벨뿐이다. Responsibility·Collaboration 이름, Mermaid ID, 링크 대상과 hover 내용은 바꾸지 않는다.
- 요청이 표시 방식을 직접 밝히면 그 요청에서만 해당 값보다 우선한다.

## exporting 스크립트 계약

- `node scripts/read-settings.js` → 표준 출력에 `{"values": {...}, "notices": ["..."]}` 한 줄 JSON. 종료 코드 0(설정 문제로 실패하지 않음).
- `export-diagrams.js`, `export-document-pdf.js`는 시작할 때 같은 로더로 설정을 읽어 `png.scale`, `output.directory`를 적용한다. 명시적 출력 경로 인자가 있으면 그 경로가 `output.directory`보다 우선한다. 안내 문구는 출력하지 않는다(SKILL.md가 `read-settings.js`로 이미 전달).
- `export-document-pdf.js`는 HTML 단계에서 모든 `<details>`에 `open`을 붙여 인쇄한다(FR-015).

## exporting 대화 계약

- `questions.enabled = true`: 기존 질문 규칙 그대로. 각 질문의 선택지 중 `defaults.*` 값(`settings.jsonc`에 사용자가 설정한 값이며, 초기 기본값이 아님)과 같은 것의 `label` 끝에 ` (기본값)`을 붙인다. 기본값이 `none`이면 붙이지 않는다.
- `questions.enabled = false`: 빠진 형식·범위·레이아웃을 `defaults.*`로 채운다. `none`이라 채울 수 없는 항목만 기존 규칙대로 묻는다(이때 " (기본값)"은 붙지 않음).
- 문서 전체 범위의 형식 고정(PDF), 형식·범위 한 번에 묻기, 레이아웃 후속 질문 규칙은 바뀌지 않는다.
