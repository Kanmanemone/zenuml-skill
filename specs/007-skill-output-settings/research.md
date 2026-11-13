# Research: 스킬별 사용자 편집 설정 파일

## Decision: 설정 파일 이름과 형식

- **Decision**: 각 스킬 디렉터리에 `settings.jsonc`를 둔다. 확장자 `.jsonc`(JSON with Comments)로 주석 허용을 드러내고, `//` 줄 주석만 쓴다.
- **Rationale**: FR-020이 주석 허용 JSON을 요구한다. `.jsonc`는 VS Code가 주석 허용 JSON으로 하이라이트·검사하므로 사용자가 편집할 때 주석이 오류로 표시되지 않는다. `.json`에 주석을 넣으면 편집기가 오류로 표시한다.
- **Alternatives considered**: YAML(주석 기본 지원이지만 사용자가 JSON을 지정함), `.json` + `"$comment"` 키(주석이 값처럼 섞여 알 수 없는 키 처리와 충돌).

## Decision: 옵션 정의의 형태

- **Decision**: 각 스킬 디렉터리에 `settings.schema.json`을 두고, `options` 배열에 옵션마다 `key`(점으로 묶음 표현, 예: `responsibility.display`), `type`(`enum` / `boolean` / `number` / `relativePath`), 타입별 제약(`values`, `min`), `default`, `description`(한국어 한 줄), `tokenImpact`(값별 표시 — `enum`/`boolean`은 값마다, 그 외는 `"*"` 하나)을 둔다. 표준 JSON Schema 대신 이 작은 자체 형식을 쓴다.
- **Rationale**: FR-016~FR-018의 "옵션 정의 한 곳 + 공통 처리는 정의만 보고 동작"을 만족하려면 기계가 읽는 정의가 필요하다. 표준 JSON Schema는 토큰 표시·한국어 설명 같은 필드를 확장 키로 붙여야 하고 검증기가 의존성으로 들어온다. 타입 네 가지면 현재와 예상 옵션을 모두 표현한다.
- **Alternatives considered**: SKILL.md 안의 표(스크립트가 읽을 수 없어 exporting과 기준이 둘로 갈림), 표준 JSON Schema + ajv(새 의존성, 과함).

## Decision: 공통 처리의 위치

- **Decision**: LLM이 따르는 두 스킬은 각 SKILL.md에 같은 형태의 "Settings" 절을 둔다(옵션 이름을 하나도 언급하지 않는 일반 절차). exporting은 `scripts/lib/settings.js`의 `loadSettings(skillDir)`가 처리하고, SKILL.md는 `node scripts/read-settings.js`의 JSON 출력(해석된 값 + 안내 문구)을 읽어 대화 흐름(질문 여부, "(기본값)")을 정한다.
- **Rationale**: 003 FR-014가 스킬 간 의존을 금지하므로 공통 코드를 스킬 밖에 둘 수 없다. exporting은 변환이 LLM 판단에 의존하지 않아야 하므로(FR-015b) 검증도 스크립트가 한다. "Settings" 절이 옵션을 이름으로 언급하지 않으면 옵션이 늘어도 절을 고칠 필요가 없다(FR-017).
- **Alternatives considered**: 저장소 공용 `shared/settings.js`(스킬 독립성 위반), exporting도 LLM이 검증(결정성 위반).

## Decision: 주석 허용 JSON 파싱

- **Decision**: 문자열 리터럴 안의 `//`를 건드리지 않는 작은 상태 기계로 `//` 줄 주석과 `/* */` 블록 주석을 제거한 뒤 `JSON.parse`한다. 끝에 붙은 쉼표는 허용하지 않는다(읽지 못한 파일로 처리, FR-005).
- **Rationale**: 새 의존성 없이 결정적으로 동작한다. 경로 값(`./exports`)이나 URL에 `//`가 들어가도 문자열 안이면 안전하다.
- **Alternatives considered**: `jsonc-parser` 패키지(의존성 추가), 정규식 한 줄(문자열 안 `//`를 잘못 지움).

## Decision: 값 검증 규칙

- **Decision**: `enum`은 `values` 중 하나, `boolean`은 `true`/`false`, `number`는 유한한 수이며 `min`보다 커야 함(배율은 0 초과), `relativePath`는 비어 있지 않은 문자열이며 절대 경로가 아님(`/`, `\`, `~`로 시작하거나 `C:` 같은 드라이브 문자로 시작하면 거부). 상위 이동(`..`)은 허용한다. 위반 시 그 키만 기본값으로 대체하고 안내한다.
- **Rationale**: spec FR-014·FR-015c가 상대 경로 표기와 절대 경로 거부를 요구하고, 사용자 예시(`../exports`)가 상위 이동을 포함한다.
- **Alternatives considered**: 경로 존재 여부 검사(위치는 없으면 새로 만들어야 하므로 부적합).

## Decision: 안내 문구 형식

- **Decision**: 안내는 채팅 응답 끝에 줄마다 `⚙️ 설정 안내: <파일> — <내용>` 형식으로 붙인다. 내용은 세 가지 — 읽지 못함(모든 값 기본값 사용), `<키>` 값이 허용되지 않아 기본값 `<값>` 사용, 알 수 없는 키 `<키>` 무시. 설정 파일이 없거나 키가 빠진 경우는 안내하지 않는다.
- **Rationale**: FR-005·FR-019. 문구가 정해져 있어야 세 스킬이 같은 모양으로 안내하고 스크립트가 생성할 수 있다.

## Decision: 접은 글 상자 마크업

- **Decision**: 섹션 헤딩 다음에 아래 형태를 쓴다(`expanded`면 `<details open>`). `<summary>` 뒤와 `</details>` 앞에 빈 줄을 둔다.

  ```markdown
  ### Responsibility

  <details>
  <summary>Details</summary>

  …섹션 내용(하위 헤딩·항목 그대로)…

  </details>
  ```

- **Rationale**: VS Code 미리보기와 GitHub는 `<details>` 안에서 빈 줄로 분리된 마크다운을 정상 렌더링하고, `open` 속성으로 처음 펼친 상태를 표현한다(FR-009). exporting의 `markdown-it`은 `html: true`로 같은 구조를 통과시킨다.
- **2026-11-13 개정**: 요약 줄은 섹션 이름 대신 고정 문구 `Details`로 쓴다(FR-009 개정). 섹션 이름을 쓰면 바로 위 헤딩과 단어가 겹치기 때문이며, `Details`는 HTML이 요약 줄이 없을 때 쓰는 기본값과 같은 영어 관례다.
- **Alternatives considered**: 섹션 헤딩을 `<summary>` 안에 넣기(헤딩이 접힌 상자 안으로 들어가 FR-009의 "헤딩은 상자 밖"과 어긋남. GitHub은 요약 줄 안 헤딩을 inline-block으로 그리지만 VS Code 개요에서 빠질 수 있음), 요약 줄 생략(브라우저 기본값이 언어 설정에 따라 달라짐).

## Decision: PDF에서 접은 글 펼치기

- **Decision**: `export-document-pdf.js`가 `markdown-it` 렌더 결과 HTML에서 `open` 속성이 없는 모든 `<details` 여는 태그에 `open`을 붙인 뒤 PDF로 인쇄한다. 원본 파일은 건드리지 않는다.
- **Rationale**: FR-015는 고정 동작이며 결정적이어야 한다. 브라우저 단계에서 DOM을 조작하는 것보다 HTML 문자열 단계에서 처리하는 편이 single·paginated 두 레이아웃에 똑같이 적용되고 단순하다.

## Decision: Dependency 렌더러 옵션 적용

- **Decision**: `dependency.renderer`가 `elk`이면 003 FR-007b와 같은 방식으로 YAML 설정의 `config` 바로 아래에 `layout: elk`를 넣는다(2026-11-13 개정 — `config.flowchart.defaultRenderer`는 VS Code 내장 Mermaid가 무시해 elk가 적용되지 않았다). `default`면 넣지 않는다. 요청 문장이 렌더러를 밝히면 그 값이 우선한다.
- **Rationale**: 기존 FR-007b 경로를 그대로 재사용한다. `default`는 "지정 없음"이라 보는 곳의 기본 레이아웃을 따른다 — mermaid 11(내보내기 스크립트)은 dagre, VS Code 내장 Mermaid(12 계열)는 ELK. 그래서 배포 기본값은 `elk`로 두어 미리보기와 내보내기가 같은 배치가 되게 한다(2026-11-13 사용자 확정).

## Decision: 배포 초기값

- **Decision**: 구현 단계에서는 모든 옵션의 초기값을 spec의 잠정값(= 기능 도입 전 동작)으로 둔다. 세 스킬 구현과 converge가 끝나면 사용자에게 옵션별 초기값을 한꺼번에 확인해 `settings.schema.json`의 `default`와 `settings.jsonc` 값을 함께 고친다(FR-003).
- **Rationale**: 사용자 요청(2026-11-13). 정의와 배포 파일 두 곳을 같이 고쳐야 SC-001이 만족된다.
