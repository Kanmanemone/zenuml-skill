# Contract: 스킬 설정 파일과 공통 처리

## 파일 계약

- 위치: `<skill dir>/settings.jsonc`(사용자 편집), `<skill dir>/settings.schema.json`(옵션 정의).
- `settings.jsonc`: 주석(`//`, `/* */`)을 허용하는 JSON. 최상위는 객체. 묶음 객체 아래 옵션 키. 키·값은 영어.
- 배포본 `settings.jsonc`의 각 옵션 바로 위 주석 형식:

  ```jsonc
  // <한국어 의미 한 줄>
  //   <값1> : <뜻> — <토큰 영향>
  //   <값2> : <뜻> — <토큰 영향>
  //   (기본값: <default>)
  "<leaf key>": <default>
  ```

  `number`·`relativePath`는 값 목록 대신 `//   허용: <규칙> — <토큰 영향>` 한 줄을 쓴다. 주석 내용은 옵션 정의의 `description`·`values`·`tokenImpact`·`default`와 같아야 한다.

## 공통 처리 계약 (모든 스킬 공통)

1. 실행마다 옵션 정의와 설정 파일을 새로 읽는다.
2. data-model.md "해석 규칙" 표대로 값을 정한다.
3. 안내 문구는 채팅 응답에만 붙인다(산출 파일에 넣지 않음). 형식: `⚙️ 설정 안내: <스킬 디렉터리 기준 파일 경로> — <내용>`.
4. 스킬은 설정 파일을 고치지 않는다.

## exporting 스크립트 계약

- `node scripts/read-settings.js` → 표준 출력에 `{"values": {...}, "notices": ["..."]}` 한 줄 JSON. 종료 코드 0(설정 문제로 실패하지 않음).
- `export-diagrams.js`, `export-document-pdf.js`는 시작할 때 같은 로더로 설정을 읽어 `png.scale`, `output.directory`를 적용한다. 명시적 출력 경로 인자가 있으면 그 경로가 `output.directory`보다 우선한다. 안내 문구는 출력하지 않는다(SKILL.md가 `read-settings.js`로 이미 전달).
- `export-document-pdf.js`는 HTML 단계에서 모든 `<details>`에 `open`을 붙여 인쇄한다(FR-015).

## exporting 대화 계약

- `questions.enabled = true`: 기존 질문 규칙 그대로. 각 질문의 선택지 중 `defaults.*` 값과 같은 것의 `label` 끝에 ` (기본값)`을 붙인다. 기본값이 `none`이면 붙이지 않는다.
- `questions.enabled = false`: 빠진 형식·범위·레이아웃을 `defaults.*`로 채운다. `none`이라 채울 수 없는 항목만 기존 규칙대로 묻는다(이때 " (기본값)"은 붙지 않음).
- 문서 전체 범위의 형식 고정(PDF), 형식·범위 한 번에 묻기, 레이아웃 후속 질문 규칙은 바뀌지 않는다.
