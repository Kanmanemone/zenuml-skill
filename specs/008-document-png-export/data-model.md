# Data Model: 문서 전체를 PNG 이미지로 내보내기

## Export Request (대화에서 정해지는 값)

| 필드 | 값 | 규칙 |
|------|----|------|
| scope | `diagram` / `document` | 기존과 같음 |
| format | `diagram`: `svg`/`png`/`pdf`, `document`: `pdf`/`png` | `document` + `svg`는 허용되지 않음(FR-009) |
| pdfLayout | `single` / `paginated` | `document`일 때만. PDF·PNG 공통(FR-010) |

**형식 결정 규칙(scope=document)**:

| 상황 | 결과 |
|------|------|
| 요청이 `pdf`/`png` 지정 | 그 형식 |
| 요청이 `svg` 지정 | 미지원 안내 + PDF·PNG 질문 |
| 미지정, 질문 켬 | PDF·PNG 질문(`defaults.format`이 `pdf`/`png`면 그 선택지에 " (기본값)") |
| 미지정, 질문 끔, `defaults.format` = `pdf`/`png` | 그 형식 |
| 미지정, 질문 끔, `defaults.format` = `svg`/`none` | PDF·PNG 질문(" (기본값)" 없음) |

## Document PNG Output

| 필드 | 설명 |
|------|------|
| files | single: `<base>.png` 1개. paginated: `<base>-page-1.png` … `<base>-page-N.png` |
| base | 출력 경로 인자가 있으면 그 경로(확장자 제외), 없으면 `output.directory`/`<원본 이름>` |
| pixel size | 페이지 크기(CSS px) × `png.scale` |

**불변 조건**: paginated의 N = 같은 입력으로 만든 paginated PDF의 페이지 수(SC-002).
