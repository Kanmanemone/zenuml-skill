# Contract: export 스크립트 CLI (변경 후)

SKILL.md가 호출하는 인터페이스는 바뀌지 않는다(FR-010). 바뀌는 것은 산출물 내용뿐이다.

## `export-diagrams.js <targetFile.md> <svg|png|pdf> [outputBase]`

- 입력 검증·종료 코드·오류 메시지: 기존과 동일(사용법 오류 2, 그 밖의 실패 1, "No diagrams found …").
- 산출물 이름: `<outputBase>-N.<format>` (N = 문서 안 다이어그램 순서, 1부터). 기본 `outputBase`는 `<targetFile 디렉토리>/exports/<파일명>`.
- stdout: **이번 실행에서 만든** 산출물 경로를 다이어그램 순서대로 한 줄에 하나(FR-009).
- 산출물 내용:
  - `svg`: 보정된 SVG(넘침 없으면 mmdc 출력과 바이트 동일).
  - `png`: 보정된 viewBox 크기 × 3 픽셀, 흰 배경.
  - `pdf`: 보정된 viewBox 크기와 같은 한 페이지 벡터 PDF.

## `export-document-pdf.js <targetFile.md> [outputFile.pdf] [--layout single|paginated]`

- 인터페이스·출력: 기존과 동일.
- 변경: 삽입되는 각 다이어그램 SVG가 인라인 전에 보정된다(FR-002).

## `lib/fit-svg.js` (내부 모듈)

| export | 시그니처 | 설명 |
|--------|----------|------|
| `fitSvgFile` | `(browser, svgPath) → Promise<FitResult>` | data-model.md 규칙대로 파일을 제자리 보정 |
| `svgFileToPng` | `(browser, svgPath, pngPath, scale) → Promise<void>` | viewBox 크기 × scale PNG |
| `svgFileToPdf` | `(browser, svgPath, pdfPath) → Promise<void>` | viewBox 크기 한 페이지 PDF |

`browser`는 호출자가 띄운 Puppeteer Browser(측정과 렌더에 같은 인스턴스를 쓴다).
