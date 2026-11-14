# Quickstart: 다이어그램 노드 hover로 책임·협력 보기

구현이 spec을 만족하는지 확인하는 실행 시나리오. 형식 규칙은 [contracts/apply-hover-contract.md](contracts/apply-hover-contract.md), 구조는 [data-model.md](data-model.md)를 본다.

## 준비

- Python 3.9 이상(외부 패키지 없음, 설치 단계 없음), VS Code 1.146 이상.
- `.vscode/settings.json`에 `markdown.styles`가 있으면 뺀다.
- 고정 입력: `specs/009-hover-detail-panel/fixtures/`
  - `view.input.md` — 기능 도입 전 규칙으로 만든 구조 뷰(그룹 2개 이상, 링크 있는 노드·없는 노드, 묶음 협력 1개, 서로 의존하는 쌍 1개, 본문에 큰따옴표·코드·링크 포함).
  - `view.<설정 이름>.expected.md` — 설정별 기대 출력.

아래에서 `AH`는 `python3 .claude/skills/generating-architecture-views/scripts/apply_hover.py`다(Windows는 `python` 또는 `py -3`). 각 시나리오는 입력을 임시 파일로 복사해 그 복사본에 실행한다.

## 스크립트 시나리오 (바이트 비교)

| # | 실행 | 기대 결과 | 확인하는 것 |
|---|---|---|---|
| Q1 | 기본 설정으로 `AH tmp.md` | `view.default.expected.md`와 같음 | FR-001·005·008·009·011·012·013, SC-003 |
| Q2 | Q1 결과에 `AH tmp.md` 한 번 더 | 출력 `변경 없음`, 파일 그대로 | FR-003, SC-004 |
| Q3 | `AH tmp.md --responsibility=concrete,abstract --collaboration=questions --position=node` | `view.custom.expected.md`와 같음(역할이 먼저, 협력마다 머리줄 + 질문만, `node` 블록) | FR-008·009·014·019 |
| Q4 | Q1 결과에 `AH tmp.md --enabled=false` | `view.input.md`와 같음 | FR-006·020, SC-005 |
| Q5 | Q1 결과의 본문 책임 문장 하나를 고친 뒤 `AH tmp.md` | 그 노드 패널만 바뀌고 나머지는 Q1과 같음 | FR-002, US3 |
| Q6 | Responsibility 섹션을 지운 입력에 `AH tmp.md` | 패널에 Responsibility 부분 없음, 안내 줄 없음 | FR-010 |
| Q7 | 설정 파일의 `hover.collaboration`을 `["targets", "targets"]`로 바꾸고 `AH tmp.md` | 기본값으로 동작 + `⚙️ 설정 안내` 한 줄 | FR-009a |
| Q8 | `### Dependency`가 없는 Markdown에 `AH x.md` | 종료 코드 `2`, 파일 그대로 | 계약 |

모든 시나리오에서 `### Responsibility`·`### Collaboration` 아래 줄은 입력과 바이트 단위로 같아야 한다(FR-002). 기대 출력의 툴팁 안에는 `"`가 없어야 한다.

## 화면 시나리오 (VS Code 미리보기)

| # | 파일 | 할 일 | 기대 결과 |
|---|---|---|---|
| V1 | Q1 결과 | 각 노드에 마우스 | 아래쪽 넓은 패널, 맨 윗줄 노드 이름(굵게), 책임·역할, 의존 대상과 경계·분리 이유, 의존받는 쪽 없음, 이름에 밑줄 |
| V2 | Q1 결과 | 링크 없는 노드 클릭 | 이동·오류 없음, 커서 일반 모양 |
| V3 | Q1 결과 | 미리보기 폭 약 750px 이상에서 협력 많은 노드에 마우스 | 내용이 여러 칸으로 나뉨 |
| V4 | Q3 결과 | 오른쪽 끝 노드 → 왼쪽 끝 노드 순서로 마우스 | 둘 다 같은 폭, 오른쪽은 미리보기 오른쪽 끝에 붙음, 왼쪽은 노드 아래 |
| V5 | Q1 결과 | 본문 큰따옴표가 있는 항목의 노드에 마우스 | 다이어그램이 정상으로 그려지고 패널에 따옴표가 보임(research R8의 `&quot;` 확인) |
| V6 | Q4 결과 | 노드에 마우스 | 기본 툴팁(파일 이름), 문서 맨 아래에 CSS 글자 없음 |

## 내보내기 시나리오

| # | 실행 | 기대 결과 |
|---|---|---|
| E1 | Q1 결과를 `exporting-markdown-diagrams`로 문서 전체 PDF | 결과에 CSS 글자 없음, 다이어그램 정상(FR-015, SC-006) |
| E2 | 같은 파일의 다이어그램만 SVG/PNG | 정상 렌더링, 툴팁 글자 없음 |

## 스킬 전체 시나리오

| # | 요청 | 기대 결과 |
|---|---|---|
| S1 | 기본 설정으로 구조 뷰 생성 요청 | 저장 후 스크립트가 자동 실행되어 V1과 같은 동작, 피드백 로그 `Response`에는 툴팁 없는 모델 출력(research R3) |
| S2 | "hover 빼고 만들어줘" | 스크립트가 `--enabled=false`로 실행되거나 실행되지 않고, 결과가 기능 도입 전 형태 |
| S3 | 같은 설명으로 hover 켜고/끄고 생성 | 모델 출력 분량 차이 없음(SC-007) |
| S4 | Python을 찾을 수 없는 환경(PATH에서 뺌)에서 생성 요청 | 구조 뷰는 기능 도입 전 형태로 정상 저장, 응답 끝에 hover를 건너뛰었다는 안내 한 줄 |
