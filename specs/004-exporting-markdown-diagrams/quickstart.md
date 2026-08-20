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
