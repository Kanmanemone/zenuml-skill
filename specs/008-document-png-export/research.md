# Research: 문서 전체를 PNG 이미지로 내보내기

## Decision: PNG를 PDF에서 래스터화해 만든다

- **Decision**: 기존 문서 PDF 파이프라인으로 요청한 페이지 구성(single/paginated)의 PDF를 임시 폴더에 만든 뒤, 각 페이지를 PNG로 렌더링한다.
- **Rationale**: FR-002(PDF와 같은 페이지 나눔·장수)와 FR-003(같은 모양)을 구조적으로 보장한다. 브라우저 인쇄 엔진의 페이지 나눔(줄·이미지를 페이지 사이에서 자르지 않음)을 다른 방법으로 재현할 수 없다. PDF에 이미 적용된 글꼴 일치, 다이어그램 잘림 방지(viewBox 보정), 접은 글 펼침이 그대로 이어진다.
- **Alternatives considered**: 렌더링한 HTML의 전체 화면 캡처(single에는 가능하지만 paginated 페이지 나눔을 재현 못 함), 고정 높이로 자르기(줄이 잘리고 장수가 달라짐), 시스템 도구 `pdftoppm`(플랫폼마다 설치가 달라 번들할 수 없음).

## Decision: 래스터화 도구 — `pdfjs-dist`를 headless 브라우저 안에서 실행

- **Decision**: `pdfjs-dist`를 의존성에 추가하고, 이미 띄우는 puppeteer 브라우저 페이지에서 pdf.js로 각 페이지를 canvas에 그려 PNG 데이터를 받아 파일로 쓴다. pdf.js 모듈과 PDF는 `127.0.0.1`의 임시 로컬 HTTP 서버(Node `http`, 실행 중에만 열림)로 브라우저에 넘긴다.
- **Rationale**: 순수 JS라 네이티브 빌드가 필요 없고, 브라우저 canvas를 쓰므로 Node용 canvas 패키지도 필요 없다. ES 모듈과 worker는 `file://`에서 막히므로 로컬 HTTP로 제공한다.
- **Alternatives considered**: Node에서 pdf.js + `canvas` 패키지(네이티브 빌드 필요), Chromium 내장 PDF 뷰어 캡처(headless에서 쓸 수 없음).

## Decision: 배율

- **Decision**: pdf.js viewport scale을 `png.scale × 96 / 72`로 둔다. PDF 1pt = 1/72in, CSS 1px = 1/96in이므로 결과 PNG의 픽셀 = 문서 CSS 픽셀 × `png.scale`.
- **Rationale**: 다이어그램 PNG의 `deviceScaleFactor = png.scale`과 같은 해상도 의미를 준다(FR-005).

## Decision: 파일 이름

- **Decision**: single → `<원본이름>.png`. paginated → `<원본이름>-page-<N>.png`(N은 1부터). 사용자가 출력 경로를 직접 주면 그 경로에서 확장자를 뗀 이름을 같은 규칙의 기준으로 쓴다. 기본 위치는 `output.directory`.
- **Rationale**: Edge Case "출력 이름 지정 시 페이지 번호를 붙임"과 다이어그램 PNG 번호 규칙(`-1`, `-2`)과의 혼동 방지.

## Decision: 크기 한계 처리

- **Decision**: 렌더링할 canvas 크기가 브라우저 한계를 넘거나 렌더링이 실패하면, 그 페이지 번호와 크기를 담은 오류로 종료한다(종료 코드 ≠ 0). 축소·분할 같은 자동 대처는 하지 않는다.
- **Rationale**: FR-012, spec Assumptions "이미지 크기 한계".

## Decision: 공용 모듈 추출

- **Decision**: `export-document-pdf.js`의 본문(다이어그램 추출 → SVG 보정 → HTML → 접은 글 펼침 → 인쇄)을 `lib/document-pdf.js`의 `renderDocumentPdf(browser, targetFile, layout, outputFile)`로 옮기고, 두 CLI가 이를 호출한다.
- **Rationale**: 같은 파이프라인을 복제하지 않아 PDF와 PNG가 어긋나지 않는다. PDF 결과는 그대로여야 하므로(SC-006) 코드 이동만 하고 동작은 바꾸지 않는다.

## Decision: 대화 규칙

- **Decision**: SKILL.md의 "scope=document면 format=pdf 자동" 규칙을 다음으로 바꾼다 — 문서 전체에서 형식은 `pdf`/`png`; 요청이 `svg`면 미지원 안내 후 PDF·PNG 질문; 형식 미정이면 질문을 켠 경우 PDF·PNG 두 선택지 질문(`defaults.format` 일치 선택지에 " (기본값)"), 끈 경우 `defaults.format`이 `pdf`/`png`면 채우고 아니면 질문. 페이지 구성 질문·`defaults.pdfLayout`은 PDF와 PNG에 공통.
- **Rationale**: FR-006~FR-010.
