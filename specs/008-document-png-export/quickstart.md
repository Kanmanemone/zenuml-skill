# Quickstart: 문서 전체 PNG 검증

## 사전 준비

`.claude/skills/exporting-markdown-diagrams/scripts`에서 `npm install`(pdfjs-dist 포함). 다이어그램 1개·접은 글 상자 1개·여러 페이지 분량의 본문이 있는 시험용 마크다운을 scratch 폴더에 만든다.

## 시나리오 1 — single (US1/AC1, AC3, FR-001·FR-004)

`node scripts/export-document-png.js <md> "" --layout single` → `<output.directory>/<name>.png` 1개. 이미지에 다이어그램과 접은 글 내용이 보인다.

## 시나리오 2 — paginated 장수 (US1/AC2, SC-002)

같은 파일을 `--layout paginated`로 PNG, 그리고 PDF로 변환 → PNG 장수 = PDF 페이지 수, 파일 이름은 `-page-1`부터.

## 시나리오 3 — 배율 (US1/AC4, FR-005)

`png.scale`을 2와 3으로 바꿔 single 변환 → 픽셀 크기 비율 2:3.

## 시나리오 4 — 결정성 (SC-003)

같은 입력·설정으로 두 번 변환 → 장수와 픽셀 크기가 같다.

## 시나리오 5 — 기존 결과 불변 (SC-006)

변경 전후로 같은 파일의 문서 PDF와 다이어그램 PNG를 만들어 페이지 수·픽셀 크기가 같다.

## 시나리오 6 — 다이어그램 없는 문서 (Edge Case)

다이어그램 없는 마크다운도 문서 PNG가 만들어진다.

## 시나리오 7 — 대화 규칙 (US2, FR-006~FR-010)

SKILL.md 규칙 대조: 문서 전체 형식 질문의 선택지가 PDF·PNG뿐인지, SVG 요청 시 안내 후 질문하는지, 질문을 끈 경우의 `defaults.format` 처리, 페이지 구성 질문이 PNG에도 적용되는지.

## Validation Results (T008, 2026-11-13)

시험 문서: 다이어그램 1개 + 접은 글 1개 + 본문 120문단(`long.md`), 본문만 있는 `plain.md`.

| 시나리오 | 결과 | 비고 |
|----------|------|------|
| 1. single | PASS | `long.png` 3000×13721px(= PDF 750×3430pt × 96/72 × 3). 한글·다이어그램·펼쳐진 접은 글 내용을 이미지로 직접 확인 |
| 2. paginated 장수 | PASS | PNG 5장 = 같은 문서의 paginated PDF 5페이지, 각 2384×3368px(A4), 이름 `-page-1`부터 |
| 3. 배율 | PASS | `png.scale` 2 → 2000×9147, 3 → 3000×13721(정확히 2:3) |
| 4. 결정성 | PASS | 같은 입력 두 번 변환 → 장수·크기 같고 1페이지 PNG가 바이트 단위로 동일 |
| 5. 기존 결과 불변 | PASS | 리팩터링 전후 문서 PDF: paginated 5페이지 596×842pt, single 1페이지 750×3430pt로 동일. 다이어그램 PNG 615×210으로 동일 |
| 6. 다이어그램 없는 문서 | PASS | `plain.png` 3000×2400 생성(짧은 문서의 single은 기존 PDF처럼 최소 높이 800 CSS px) |
| (추가) 잘못된 `--layout` | PASS | 종료 코드 2와 이유 출력 |

시나리오 7(대화 규칙)은 SKILL.md 규칙 대조로 확인했다.
