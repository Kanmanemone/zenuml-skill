# Research: 다이어그램 노드 hover로 책임·협력 보기

spec의 VS Code 동작 확인(선행 확인 결과, Clarifications 2026-11-14)은 이미 끝났다. 여기서는 그 결과를 구현으로 옮길 때의 기술 결정만 정리한다.

## R1. 스크립트 실행 환경

- **Decision**: Python 3.9 이상에서 동작, 표준 라이브러리만, 설치 단계 없음. 환경에 있는 인터프리터를 `python3` → `python` → `py -3` 순으로 찾아 `<인터프리터> scripts/apply_hover.py <file> [옵션]`으로 실행한다. 인터프리터를 찾지 못하거나 3.9 미만이면 스크립트를 건너뛰고 구조 뷰는 기능 도입 전 형태로 둔 채 응답에 안내 한 줄을 남긴다.
- **Rationale**: Agent Skills의 번들 스크립트는 Python이 사실상 표준이다(이 개발 환경에 설치된 스킬들의 `scripts/` 기준 Python 150개, Bash 11개, JavaScript 3개 — Anthropic 공식 pdf·docx·xlsx·pptx·skill-creator 포함). JavaScript는 npm에만 있는 라이브러리가 필요할 때 쓰는데, 이 변환은 텍스트 처리뿐이라 그럴 이유가 없다. 이 개발 환경에서 Python은 바로 실행되고 Node는 PATH에 없었다.
- **버전 근거**: macOS 기본 `python3`이 3.9, Ubuntu 22.04가 3.10, Debian 12가 3.11, Ubuntu 24.04가 3.12다. 3.9를 하한으로 두면 추가 설치 없이 가장 많은 환경에서 돈다. 이 스크립트는 3.10+ 전용 문법이 필요 없다.
- **설치 방식 근거**: Anthropic 공식 스킬을 포함한 Agent Skills 스크립트는 대부분 환경의 Python을 찾아 쓰고, 패키지가 필요할 때만 `pip install`을 안내한다. `uv run` + PEP 723(실행 시 Python·패키지 자동 마련)도 늘고 있지만 `uv` 설치가 먼저 필요해 의존성 없는 이 스크립트에는 이득이 없다.
- **Alternatives considered**: `uv run` + PEP 723(위 이유), Python 동봉 배포(용량·플랫폼별 빌드 부담), Node.js ESM(이 저장소 `exporting-markdown-diagrams`와 같은 실행 방식이지만, 그 스킬이 Node인 이유는 `mermaid-cli`·`puppeteer` 같은 npm 라이브러리 때문이고 이 기능에는 해당하지 않음), 모델이 직접 툴팁 작성(SC-007 위반, 결정적이지 않음).

## R2. 설정 읽기와 항목 목록 타입

- **Decision**: `exporting-markdown-diagrams/scripts/lib/settings.js`와 같은 동작(주석 제거 → JSON 해석 → 옵션 정의대로 검증·기본값·안내)을 이 스킬의 `scripts/hover/settings.py`로 옮기고, 검증에 `itemList` 타입을 더한다. `itemList`는 배열이고, 모든 원소가 `items`에 있는 문자열이며, 중복이 없을 때만 유효하다. 빈 배열은 유효하다. 잘못된 값은 기존 규칙대로 기본값 + 안내 한 줄(FR-009a, 007 FR-005).
- **Rationale**: 스킬끼리 코드를 공유하지 않는다는 원칙(003 FR-014)과, 옵션 정의만 보고 동작하는 007의 공통 절차를 그대로 따른다. SKILL.md의 "Settings" 절(모델이 따르는 절차)에도 같은 규칙을 한 줄 더한다.
- **Alternatives considered**: 공용 패키지로 분리(스킬 독립성 위반), 쉼표 구분 문자열(`"abstract,concrete"` — 순서·중복 검사가 더 어렵고 JSON답지 않음).

## R3. 실행 시점과 피드백 로그

- **Decision**: 모델은 지금처럼 구조 뷰 파일을 쓰고(툴팁은 기존 규칙대로 파일 이름, 링크 없는 노드는 `click` 없음), 피드백 로그를 쓴 뒤, hover가 켜져 있으면 `apply-hover.js`를 실행한다. 피드백 로그의 `**Response**:`는 모델이 쓴 내용(스크립트 실행 전)이다.
- **Rationale**: 툴팁을 로그에 다시 옮겨 쓰면 모델 출력이 늘어 SC-007을 어긴다. 툴팁은 본문의 복사본이라 로그에 없어도 정보 손실이 없다. 로그 형식은 바꾸지 않는다(Assumptions).
- **Alternatives considered**: 스크립트가 로그도 고침(로그는 사람이 쓰는 기록이라는 003 원칙과 어긋나고 범위가 커짐), 실행 후 로그 작성(모델이 파일을 다시 읽어 옮겨야 함).

## R4. 요청 문장 재정의(FR-014, FR-020)

- **Decision**: 스크립트는 설정 파일 값을 읽고, 명령줄 옵션이 있으면 그 값으로 덮는다 — `--enabled=true|false`, `--responsibility=abstract,concrete`(빈 값 `--responsibility=`은 `[]`), `--collaboration=...`, `--position=bottom|node`. 모델은 요청 문장이 hover 값을 밝힌 경우에만 해당 옵션을 붙인다. 명령줄 값도 설정 값과 같은 검증을 거친다.
- **Rationale**: 요청 우선 규칙(007 FR-006)을 스크립트에서도 지킬 수 있는 가장 단순한 통로다. 따로 실행할 때(FR-004)는 옵션 없이 돌려 설정 값만 따른다.
- **Alternatives considered**: 모델이 임시 설정 파일을 씀(설정 파일 편집 금지 규칙 위반).

## R5. `display: hidden` 처리(FR-010)

- **Decision**: 스크립트는 `display` 설정을 읽지 않는다. 섹션 제목(`### Responsibility`/`### Collaboration`)이 파일에 없으면 그 섹션의 항목 목록을 빈 목록으로 다룬다.
- **Rationale**: `hidden`이면 섹션이 아예 없으므로(003 SKILL.md) 결과가 같고, 요청 문장으로 `display`를 바꾼 경우까지 파일이 이미 반영하고 있다. 원본은 본문이라는 FR-002와도 맞는다.

## R6. 구조 뷰 파일 읽기

- **Decision**: 003이 고정한 파일 구조에 기대어 줄 단위로 읽는다.
  - Dependency 코드 블록: 첫 ```` ```mermaid ```` ~ 닫는 ```` ``` ````.
  - 노드 선언: 코드 블록에서 `%% ---- 엣지 ----` 앞, `subgraph`/`direction`/`end`/`flowchart`/frontmatter를 뺀 줄 — `Id`, `Id@{ label: "표시 이름" }`, `Id["표시 이름"]` 세 형태.
  - 엣지: `Src eN@-->|관계| Dst`.
  - 링크 `click`: `click Id "대상" "툴팁"`. 스크립트가 다는 이동 없는 줄: `click Id hoverOnly "툴팁"`.
  - 본문: Responsibility의 `#### 요소의 책임` 아래 항목, Collaboration의 `#### 요소 간 비교` 아래 항목. `<details>` 상자 안이든 밖이든 같게 읽는다.
- **Rationale**: 형식이 스킬 규칙으로 고정돼 있어 범용 Markdown/Mermaid 파서가 필요 없다. 읽지 못한 항목은 건너뛰고 해당 노드 패널을 비우는 것으로 안전하게 처리한다(Edge Case "본문에 해당 노드 항목이 없는 경우").
- **Alternatives considered**: markdown-it 등 파서(의존성 추가, `<details>`·HTML 혼합 처리에 이점 없음).

## R7. 본문 항목과 노드 연결

- **Decision**: 표시 이름으로 연결한다. 노드 표시 이름에서 ✨/♻️/🗑️ 접두, `&nbsp;`, `<b>`/`<s>` 태그를 걷어 낸 이름과, 본문 `<strong>[이름](경로)</strong>`·`<strong>이름</strong>`의 이름을 비교한다. 병렬 형제로 묶인 Responsibility 항목(`<strong>A</strong>, <strong>B</strong>, …`)은 묶인 모든 이름에 연결한다.
- **Collaboration 첫 줄 해석**: 주어는 첫 `<strong>` 이름, `…는 X에 의존한다.`의 X 부분은 태그·링크를 걷어 낸 글자 그대로(`A와 B`, 묶음 이름 포함), `…와 Y는 서로 의존한다.`는 양쪽에 연결한다. 패널 머리줄은 FR-011 문장(`X에 의존한다 (관계)`, `Y와 서로 의존한다 (관계)`).
- **관계 이름**: 다이어그램 엣지 라벨에서 찾되, 항상 **패널 주인 노드에서 나가는 엣지**만 본다. 서로 의존하는 쌍도 각 노드 패널에는 그 노드에서 상대로 가는 엣지의 라벨을 쓴다. 한 방향 협력은 출발 노드에서 대상 노드(들)로 가는 엣지 라벨이 하나로 모이면 그 값, 묶음 이름처럼 대상 노드를 특정할 수 없으면 출발 노드의 나가는 엣지 중 다른 협력 항목에 쓰이지 않은 엣지들의 라벨이 하나로 모일 때 그 값, 그래도 하나로 정해지지 않으면 괄호를 생략한다.

## R8. 패널 글자 변환(FR-012)

- **Decision**: 본문 조각을 툴팁 HTML로 바꾸는 규칙 — `<strong>…</strong>` → `<b>…</b>`, `` `코드` `` → `<code>코드</code>`(안의 `&`,`<`,`>`는 엔터티), Markdown 링크 `[글자](경로)` → `글자`, 그 밖의 `&`,`<`,`>`는 엔터티, 큰따옴표 `"` → `&quot;`. 줄 나눔은 `<br/>`, 빈 줄은 `<br/><br/>`. 세부 분석 문단은 하위 글머리 항목을 공백 하나로 잇는다.
- **Rationale**: Mermaid 문자열은 큰따옴표에서 끝나므로 `"`가 남으면 안 된다. Mermaid는 툴팁을 HTML로 넣되 sanitize하므로 `<b>`, `<code>`, `<br/>`, 엔터티는 살아남는다(테스트 키트에서 확인). `&quot;`가 따옴표로 보이는지는 quickstart Q4에서 확인한다 — 안 되면 대체 문자 `“ ”`로 바꾼다.

## R9. 링크 없는 노드(FR-013)

- **Decision**: `click Id hoverOnly "툴팁"` 줄을 링크 `click` 줄들 뒤에 노드 선언 순서대로 둔다. 그 노드의 색상 `classDef` 끝에 `,cursor:auto`를 붙인다. 색상 클래스는 노드마다 하나씩이므로(003 FR-008b) 이 속성은 그 노드에만 적용된다. 예외 규칙은 두지 않는다.
- **Rationale**: strict 보안 수준에서 Mermaid는 콜백 이름을 무시하고 툴팁만 단다 — 어떤 이름이든 같으며(테스트 키트 `noHoverLink`로 확인), 뜻이 드러나는 `hoverOnly`를 고정 이름으로 쓴다. `cursor:default`는 Mermaid 예약어라 쓰지 않는다(Assumptions).

## R10. `<style>` 블록 관리(FR-005, FR-006)

- **Decision**: 블록 원본은 VS Code에서 확인한 테스트 키트 CSS다 — `bottom`은 `docs/hover-tooltip-test/inline-style.md`, `node`는 `docs/hover-tooltip-test/node-25em.md`의 `<style>`(둘 다 밑줄 규칙 포함). 스크립트는 파일 끝에 있는 `<style>` 블록 중 `div.mermaidTooltip`을 담은 것을 "패널 모양 블록"으로 보고 바꾸거나 지운다. 새로 붙일 때는 본문 마지막 줄 다음에 빈 줄 하나를 두고 붙인다. 표식 주석은 넣지 않는다.
- **Rationale**: 산출물에 메타 주석을 남기지 않는 규칙(003 AP-13c)을 지키면서도 블록을 다시 찾을 수 있다. 스킬은 이 블록 말고 `<style>`을 쓰지 않으므로 오인할 대상이 없다.

## R11. 끄기·되돌리기(FR-006, SC-005)

- **Decision**: 패널 내용이 있는 노드가 하나도 없으면 — 링크 `click` 줄의 툴팁을 대상의 파일 이름으로 되돌리고(경로·URL의 마지막 조각, 폴더면 폴더 이름, 질의·조각 표시 제외), `hoverOnly` 줄을 지우고, `classDef`의 `,cursor:auto`를 지우고, 패널 모양 블록을 지운다.
- **Rationale**: 003의 툴팁 규칙이 "파일 이름"이므로 대상에서 다시 계산할 수 있다. 결과가 기능 도입 전 산출물과 같아진다(SC-005).

## R12. PNG/PDF 내보내기(FR-015, SC-006)

- **Decision**: 내보내기 스킬은 바꾸지 않는다.
- **Rationale**: 문서 전체 PDF/PNG는 `markdown-it`을 `html: true`로 써서(`exporting-markdown-diagrams/scripts/lib/document-pdf.js`) `<style>`이 글자가 아니라 스타일로 들어가며, 툴팁은 마우스를 올려야 생기므로 결과에 보이지 않는다. 다이어그램 단독 내보내기는 코드 블록만 렌더링하므로 블록이 아예 들어가지 않는다. quickstart Q8에서 확인한다.

## R13. 시험 방법

- **Decision**: `specs/009-hover-detail-panel/fixtures/`에 입력 파일과 설정별 기대 출력 파일을 두고, 스크립트 결과를 바이트 비교한다. 같은 출력에 스크립트를 한 번 더 돌려 바뀌지 않는지 본다(SC-004). 화면 동작은 VS Code 미리보기로 확인한다.
- **Rationale**: 저장소에 테스트 프레임워크가 없고, 결정적 텍스트 변환은 기대 출력 비교로 충분하다.
