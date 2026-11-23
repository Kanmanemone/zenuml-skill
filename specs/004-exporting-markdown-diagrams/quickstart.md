# Quickstart: `exporting-markdown-diagrams` Skill 검증

## 사전 준비

- 다이어그램(zenuml 플레이버 시퀀스 다이어그램 하나, 일반 Mermaid flowchart 하나)을 포함한 테스트용 마크다운 파일을 준비한다 — 예를 들어 `.zenuml/jetpack-navigation-3.architecture.md`(이 저장소에 이미 존재하는 산출물)를 그대로 활용할 수 있다.
- `@mermaid-js/mermaid-cli`가 zenuml 지원 버전으로 설치돼 있는지 확인한다(`research.md`, 버전 고정 Decision 참고).

## 시나리오 1 — 형식·범위가 모두 명시된 다이어그램 단독 export (SC-001, FR-001, FR-002)

**입력 예시**: "이 다이어그램(`.zenuml/xxx.md`의 첫 번째 다이어그램) png로 뽑아줘."

**기대 결과**: `AskUserQuestion` 없이 바로 PNG 파일이 생성된다.

**검증**: 생성된 PNG 파일이 실제로 존재하고, 원본 다이어그램과 시각적으로 대응하는지 확인한다.

## 시나리오 2 — 형식만 불분명 (SC-002, FR-001)

**입력 예시**: "이 다이어그램 이미지로 만들어줘." (형식 미명시, 대상 다이어그램은 명확)

**기대 결과**: 형식(SVG/PNG/PDF)을 묻는 질문 하나만 `AskUserQuestion`으로 제시된다 — 범위를 묻는 질문은 나오지 않는다(범위는 이미 "다이어그램만"으로 명확하므로).

**검증**: 질문이 정확히 1개(형식)만 제시되는지 확인한다.

## 시나리오 3 — 형식·범위가 모두 불분명 (SC-002, FR-003)

**입력 예시**: "이거 변환해줘." (형식·범위 모두 미명시)

**기대 결과**: 하나의 `AskUserQuestion` 호출 안에 형식 질문과 범위 질문 두 개가 함께 제시된다 — 두 번의 별도 호출로 나뉘지 않는다.

**검증**: `AskUserQuestion`의 `questions` 배열 길이가 2인지, 각각 형식(SVG/PNG/PDF)과 범위(다이어그램만/문서 전체) 선택지를 담고 있는지 확인한다.

## 시나리오 4 — 렌더러 지정이 보존됨 (SC-005, FR-004)

**입력 예시**: `%%{init: {"flowchart": {"defaultRenderer": "elk"}}}%%`가 포함된 Mermaid flowchart를 PNG로 변환.

**기대 결과**: 변환 결과가 elk 렌더러로 그려진 레이아웃과 일치한다 — 기본 렌더러(dagre)로 조용히 대체되지 않는다.

**검증**: 결과 이미지의 레이아웃이 elk 렌더러 특유의 배치(예: 계층적 라우팅)를 보이는지 확인한다. (자동 검증이 어려우면, 최소한 변환 스크립트가 다이어그램 소스 문자열을 수정 없이 렌더러에 전달했는지 코드 리뷰로 확인한다.)

## 시나리오 5 — 문서 전체 PDF export, 형식·범위 모두 명시 (SC-001)

**입력 예시**: "이 문서 전체를 pdf로 만들어줘."

**기대 결과**: `AskUserQuestion` 없이 바로 PDF 파일이 생성된다.

**검증**: 생성된 PDF가 존재하고, 원본 문서의 텍스트와 다이어그램을 모두 포함하는지 확인한다.

## 시나리오 6 — PDF 안 다이어그램 텍스트가 선택·복사 가능 (SC-004, FR-007)

**입력 예시**: 시나리오 5에서 생성된 PDF.

**기대 결과**: PDF 뷰어(예: VS Code 내장 PDF 프리뷰, 또는 브라우저)에서 다이어그램 안의 텍스트(예: 시퀀스 다이어그램의 메서드 이름)를 드래그해 선택하면 실제로 선택되고, 복사한 텍스트가 원본 문자열과 일치한다.

**검증**: 다이어그램이 래스터 이미지로 삽입됐다면 이 선택이 불가능하거나 무의미한 사각형 선택만 되므로, 이 차이로 벡터 삽입 여부를 판별할 수 있다.

## 시나리오 7 — 다이어그램이 여러 개인 문서에서 "다이어그램만" 범위 (Assumptions, Edge Cases)

**입력 예시**: 다이어그램 3개가 포함된 마크다운 파일에 대해 "다이어그램들 svg로 뽑아줘"(특정 다이어그램을 지목하지 않음).

**기대 결과**: 3개의 SVG 파일이 각각 생성된다(번호가 매겨진 개별 파일).

**검증**: 생성된 SVG 파일 수가 원본 문서의 다이어그램 수와 일치하는지 확인한다.

## 시나리오 8 — 다이어그램이 없는 문서에 "다이어그램만" 범위 (Edge Cases)

**입력 예시**: 다이어그램이 전혀 없는 마크다운 파일에 대해 "다이어그램 png로 뽑아줘".

**기대 결과**: 변환할 다이어그램이 없다는 안내와 함께 중단된다 — 빈 파일이나 오류 스택트레이스를 그대로 노출하지 않는다.

**검증**: 사용자에게 보이는 메시지가 "다이어그램 없음"을 명확히 전달하는지 확인한다.

## 시나리오 9 — zenuml 플레이버와 일반 Mermaid flowchart 둘 다 성공 (SC-006, FR-006)

**입력 예시**: `.zenuml/<slug>.md`(zenuml 플레이버, `generating-zenuml-diagrams` 산출물)와 `.zenuml/<slug>.architecture.md`(일반 Mermaid flowchart, `generating-architecture-views` 산출물) 각각에 대해 SVG 변환을 실행.

**기대 결과**: 두 경우 모두 오류 없이 SVG 파일이 생성된다.

**검증**: 두 산출물 각각의 SVG 파일이 실제로 다이어그램 내용을 담고 있는지(빈 파일이나 "UnknownDiagramError" 흔적이 없는지) 확인한다.

## 시나리오 10 — 산출물이 전용 `exports/` 디렉토리에 모임 (SC-007, SC-008, FR-009~012)

**입력 예시**: `exports/`가 아직 없는 상태에서, 다이어그램이 포함된 `.zenuml/foo.architecture.md`를 SVG로, 그리고 같은 파일을 문서 전체 PDF로 각각 변환.

**기대 결과**: `exports/` 디렉토리가 자동으로 생성되고, SVG와 PDF 산출물이 모두 `.zenuml/foo.architecture.md`와 같은 폴더가 아니라 그 아래 `.zenuml/exports/`에 생성된다. 파일명 규칙(베이스 이름, 다이어그램 여러 개일 때의 `-1`/`-2` 번호 매김)은 이전과 동일하게 유지된다.

**검증**: 산출물 경로가 `<원본 디렉토리>/exports/<파일명>`인지, `<원본 디렉토리>`에는 새 파일이 생기지 않았는지, 다이어그램이 여러 개인 파일의 산출물들이 모두 같은 `exports/`에 모이는지 확인한다.

## 시나리오 11 — PNG 해상도가 다이어그램 크기와 무관하게 선명함 (SC-009, FR-013)

**입력 예시**: 노드가 여러 개인 큰 다이어그램(예: `.zenuml/jetpack-navigation-3.architecture.md`)을 PNG로 변환.

**기대 결과**: 생성된 PNG를 실제 크기로 열었을 때 텍스트와 선이 흐릿하지 않다. 가로·세로 픽셀 수는 다이어그램의 실제 레이아웃 크기에 고정 배율(scale)을 곱한 값이어야 한다 — 임의로 정한 고정 너비/높이가 아니다.

**검증**: 산출물 PNG의 픽셀 크기가 SVG 산출물의 뷰박스 크기 × scale 배율과 일치하는지 확인하고, 육안으로 텍스트 가장자리가 계단현상 없이 선명한지 확인한다.

## 시나리오 12 — 문서 전체 PDF 페이지 구성 확인 질문과 두 결과 (SC-010, FR-014~015)

**입력 예시 A**: "이 문서 전체를 pdf로 만들어줘" (페이지 구성 미명시).

**기대 결과 A**: 페이지 구성(1페이지 단일 | 표준 인쇄 규격)을 묻는 확인 질문이 제시된다. "1페이지 단일"을 고르면 결과 PDF가 정확히 1페이지, "표준 인쇄 규격"을 고르면 내용 길이에 따라 여러 페이지로 생성된다.

**입력 예시 B**: "이 문서 한 페이지로 안 잘리게 pdf로 만들어줘" (페이지 구성까지 명시).

**기대 결과 B**: 확인 질문 없이 바로 1페이지 PDF가 생성된다.

**검증**: PDF의 실제 페이지 수(예: PyMuPDF `len(doc)`)로 확인한다.

## 시나리오 13 — 문서 전체 PDF의 글꼴이 VS Code Markdown 미리보기와 일치함 (SC-011, FR-016)

**입력 예시**: 한글 프로즈와 영문 식별자(코드 스팬)가 섞인 마크다운 파일을 문서 전체 PDF로 변환.

**기대 결과**: PDF를 렌더링해 열어 보면 한글·영문·코드 텍스트 모두 VS Code에서 같은 마크다운 파일을 미리보기로 열었을 때와 같은 글꼴로 보인다(임의로 고른 대체 글꼴이 아님).

**검증**: PDF 페이지를 이미지로 렌더링해(예: PyMuPDF `page.get_pixmap()`) VS Code Markdown 미리보기 스크린샷과 나란히 비교한다.

## 시나리오 14 — VS Code 미리보기 모양 (SC-014, FR-023)

**입력 예시**: subgraph와 노드 색 지정이 있는 구조 뷰(`.zenuml/*.architecture.md`)를 다이어그램 PNG와 문서 전체 PNG로 내보낸다. `render.theme`을 `vscode-light-plus`, `mermaid-default`로 바꿔 가며, 그리고 `--theme=mermaid-default`로 한 번 더.

**기대 결과**:
- `vscode-light-plus`: subgraph 배경이 흰색, 노드 배경 `#F3F3F3`, 노드 모양 classic, 다이어그램이 지정한 테두리·간선 색은 그대로. VS Code Light+ 미리보기와 나란히 보면 같다.
- `mermaid-default`와 `--theme=mermaid-default`: 도입 전과 같은 연노랑 subgraph·연보라 노드.
- 허용되지 않는 `--theme=` 값: 설정 값으로 내보내고 `⚙️ 설정 안내` 한 줄.

**검증**: 생성된 PNG를 VS Code Light+ 미리보기 화면과 비교한다.

## 시나리오 15 — 다이어그램 내보내기에 문서 style 적용 (SC-015, FR-024)

**입력 예시**: 노드 테두리 위 파일 이름을 문서 끝 `<style>`로 그리는 구조 뷰, 그리고 링크 노드가 subgraph 없이 맨 위에 있는 작은 구조 뷰를 다이어그램만 PNG·SVG로 내보낸다. 비교용으로 `<style>`이 없는 문서도 내보낸다.

**기대 결과**: 파일 이름이 미리보기와 같은 자리·색으로 보이고 맨 위 노드에서도 잘리지 않는다. `<style>`이 없는 문서의 SVG는 이 기능 전과 같다.

**검증**: 결과 PNG를 미리보기와 비교하고, `<style>` 없는 문서의 SVG에 `<style><![CDATA[`가 없는지 본다.

## 결과 기록

각 시나리오의 통과/실패와 구체적 이슈를 표로 기록해 두면, 구현을 반복 개선할 때 회귀 확인 기준으로 재사용할 수 있다.

| 시나리오 | 결과 | 비고 |
|---|---|---|
| 1. 형식·범위 모두 명시 | PASS | `export-diagrams.js`를 svg/png/pdf 각각으로 직접 실행해 확인 |
| 2. 형식만 불분명 | PASS | Skill 도구로 실제 라이브 호출 — `AskUserQuestion`이 형식 질문 1개만 제시함을 확인 |
| 3. 형식·범위 모두 불분명 | PASS | Skill 도구로 실제 라이브 호출 — `AskUserQuestion` 한 번에 질문 2개(형식/범위)가 함께 제시됨을 확인 |
| 4. 렌더러 지정 보존(elk) | PASS | `jetpack-navigation-3.architecture.md`(defaultRenderer: elk) → SVG 변환 결과의 `aria-roledescription="flowchart-elk"`로 elk 렌더러가 실제 사용됐음을 확인 |
| 5. 문서 전체 PDF, 형식·범위 명시 | PASS | `export-document-pdf.js` 직접 실행 — exit 0, PDF 정상 생성(6페이지) |
| 6. PDF 안 다이어그램 텍스트 선택·복사 가능 | PASS | `pymupdf`로 PDF를 직접 파싱 — 다이어그램 라벨(`MyApp`, `NavDisplay`, `EntryProvider`, `NavBackStack`)이 전부 추출 가능한 텍스트로 존재, 임베드된 래스터 이미지 0개(완전히 벡터로 삽입됨) |
| 7. 다이어그램 여러 개, "다이어그램만" 범위 | PASS | 다이어그램 3개짜리 테스트 파일 → `-1`/`-2`/`-3` 3개 PNG 파일 개별 생성 확인 |
| 8. 다이어그램 없음 | PASS | "No diagrams found... — nothing to convert." 메시지와 exit 1로 명확히 종료(스택트레이스 노출 없음) |
| 9. zenuml/일반 Mermaid 둘 다 성공 | PASS | `navigation3.md`(zenuml)와 `jetpack-navigation-3.architecture.md`(일반 flowchart) 각각 SVG 변환 성공, `UnknownDiagramError` 없음 — `@mermaid-js/mermaid-cli` `^11.0.0` 버전 고정이 유효함을 확인 |
| 10. 산출물이 전용 `exports/`에 모임 | PASS | `.zenuml/exports/`가 없는 상태에서 SVG·PDF 변환 실행 → 자동 생성 확인, 두 산출물 모두 `.zenuml/exports/`에 생성되고 원본 폴더에는 새 파일 없음, 다이어그램 여러 개 파일의 `-1`/`-2` 산출물도 같은 `exports/`에 함께 생성됨 확인 |

구현 중 발견해 함께 고친 이슈: Windows에서 mermaid-cli의 `.cmd` 셰임을 `spawnSync`로 직접 실행하면 `EINVAL`이 발생 — mermaid-cli의 JS 엔트리포인트(`node_modules/@mermaid-js/mermaid-cli/src/cli.js`)를 현재 Node 바이너리로 직접 실행하는 방식(`scripts/lib/run-mmdc.js`)으로 교체해 셸 이스케이핑 위험 없이 해결함.

## Validation Results (T040, 2026-11-13) — Mermaid 12 업그레이드

설치 버전(lock): `@mermaid-js/mermaid-cli` 12.2.0, `mermaid` 12.3.0, `@mermaid-js/mermaid-zenuml` 1.0.1, `markdown-it` 15.0.3, `pdfjs-dist` 6.5.438, `puppeteer` 25.17.0(Chrome 157). 별도 `@mermaid-js/layout-elk`는 제거됨(ELK가 Mermaid에 내장).

| 항목 | 결과 | 근거 |
|---|---|---|
| Mermaid 다이어그램 SVG/PNG/PDF | PASS | 구조 뷰 예시(`references/examples.md`, 2개) |
| ZenUML 다이어그램 SVG/PNG/PDF | PASS | `swemo-user-scenario.md`, 렌더 이미지 육안 확인 |
| `layout: elk` 다이어그램 | PASS | `swemo-architecture.architecture.md` 문서 전체 변환 |
| 문서 전체 PDF single / paginated | PASS | 1쪽 / 11쪽, pypdf로 다이어그램 텍스트(`MemoRepository`, `타입 참조`) 추출됨 |
| 문서 전체 PNG single / paginated | PASS | 1장 / 11장 |
| 렌더러 지정 보존 | PASS | 원본 `layout: elk`를 수정 없이 넘김 |


## Validation Results (T049, 2026-11-23)

- swemo `drag-reorder-iteration-11-4.architecture.md`를 다이어그램 PNG로 내보냄.
  - 설정 `vscode-light-plus`: subgraph 배경 흰색·테두리 옅은 회색, 노드 배경 `#F3F3F3`, classic 모양. 다이어그램이 지정한 노드·간선 색과 `ReorderableItem.kt` 그룹의 주황 테두리는 그대로.
  - `--theme=mermaid-default`: `-c` 없이 도입 전과 같은 인자로 실행되어 Mermaid 기본(neo, 색 채운 subgraph) 결과.
  - `--theme=dark`: `⚙️ 설정 안내` 한 줄과 함께 설정 값(`vscode-light-plus`)으로 내보냄.
- 문서 전체 PNG(single)도 같은 Light+ 모양으로 나옴(흰 subgraph, 회색 노드, 파일 이름 표시 유지).
- 확인하지 않음: VS Code Light+ 미리보기 화면과의 나란한 비교(사용자 확인 필요).

## Validation Results (T053, 2026-11-23)

- 사용자가 Light+ PNG를 VS Code Light+ 미리보기와 나란히 비교: 색과 노드 모양은 같음.
- 간선 라벨이 선 아래로 내려오는 결함(미리보기에도 있음)은 `subGraphTitleMargin`을 빼서 없앴다(라벨 중심 오프셋 약 2.4px → -0.4px).
- 긴 간선 라벨 "길게 누르기·드래그 감지를 맡김"의 마지막 글자가 PNG에서만 둘째 줄로 넘어감: 한글 대체 글꼴 차이로 줄바꿈 폭 경계에 걸린 것. 사용자 결정으로 그대로 둔다(글꼴·폭을 따로 맞추지 않음).
- 테두리 위 파일 이름이 다이어그램만 내보낸 PNG에 없음: 이번 변경 전부터 그랬다(문서 안 style 블록이 다이어그램 내보내기에 적용되지 않음). 별도 작업으로 다룬다.

## Validation Results (T055, 2026-11-23)

- swemo 구조 뷰 다이어그램 PNG: 노드 10개 중 링크가 있고 파일 자체가 아닌 노드마다 테두리 위 파일 이름이 미리보기와 같은 자리·색으로 나옴.
- 링크 노드가 subgraph 없이 맨 위에 있는 작은 구조 뷰: PNG에서 파일 이름이 잘리지 않음. SVG에도 문서 style이 들어감(`nodeLabel::before` 규칙 4개).
- `<style>` 없는 문서(시나리오 29 정적 산출물)의 SVG: 변경 전 스크립트 결과와 바이트 단위로 같음.
