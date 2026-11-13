# Quickstart: 스킬별 사용자 편집 설정 파일 검증

## 사전 준비

1. 세 스킬 디렉터리에 `settings.jsonc`, `settings.schema.json`이 있다.
2. exporting 스크립트 의존성이 설치돼 있다(`.claude/skills/exporting-markdown-diagrams/scripts`에서 `npm install`).
3. 각 시나리오는 끝나면 `settings.jsonc`를 배포본으로 되돌린다(`git checkout -- <파일>`).

## 시나리오 1 — 확정 초기값 반영과 잠정값 = 기존 동작 (FR-003, SC-001)

(a) 세 스킬의 `settings.schema.json` `default`와 배포 `settings.jsonc` 값·주석의 "(기본값: …)"이 data-model.md "현재 옵션 목록"의 확정 초기값과 모두 같은지 대조한다. (b) 설정을 잠정값(같은 표의 잠정값 열 — 기능 도입 전 동작)으로 바꿔 세 스킬을 한 번씩 실행해, 산출물이 기능 도입 전과 같은지 확인한다(구조 뷰 상자 없음·렌더러 지정 없음, 로그 `.zenuml/log/`, 내보내기 질문 그대로·" (기본값)" 없음·`exports/`·PNG 배율 3).

## 시나리오 2 — 구조 뷰 표시 방식 (US1, FR-008~FR-010, SC-008)

`responsibility.display`를 `collapsed`, `collaboration.display`를 `expanded`로 바꿔 구조 뷰를 생성한다. Responsibility는 처음 접힌 상자, Collaboration은 처음 펼친 상자이며 헤딩은 상자 밖에 있는지 확인한다. 이어 `responsibility.display`를 `hidden`으로 바꿔 재생성하고 `### Responsibility`가 한 줄도 없는지 확인한다.

## 시나리오 3 — 렌더러 (FR-011b)

`dependency.renderer`를 `elk`로 바꿔 생성 → YAML 설정의 `config` 바로 아래에 `layout: elk`가 있다. 같은 설정에서 요청에 다른 렌더러를 밝히면 그 값이 쓰인다.

## 시나리오 4 — zenuml 로그 위치 (US3, FR-015c)

`log.directory`를 `./tmp/diagram-logs`로 바꿔 다이어그램을 생성·재생성 → `tmp/diagram-logs/<slug>.md`가 만들어지고 이어 쓰인다.

## 시나리오 5 — exporting 설정 해석 (FR-005, FR-019, SC-003)

```text
node .claude/skills/exporting-markdown-diagrams/scripts/read-settings.js
```

다음을 차례로 넣어 출력을 확인한다: (a) 배포본 → 안내 없음, (b) `png.scale: 0` → 그 키만 기본값 + 안내 1줄, (c) 정의에 없는 키 → 무시 안내 1줄, (d) 끝 쉼표로 깨진 파일 → 읽지 못함 안내 1줄·모든 값 기본값, (e) 파일 삭제 → 안내 없음.

## 시나리오 6 — PNG 배율·산출물 위치 (US2, FR-014)

`png.scale: 2`, `output.directory: "../tmp-exports"`로 바꿔 다이어그램이 있는 마크다운을 PNG로 내보낸다 → 원본 디렉터리 한 단계 위 `tmp-exports/`에 생기고, 픽셀 크기가 배율 3일 때의 2/3이다.

## 시나리오 7 — PDF 접은 글 펼치기 (FR-015, SC-004)

`<details>`(open 없음)로 접힌 섹션이 있는 마크다운을 문서 전체 PDF로 내보내고, PDF 텍스트에 접힌 내용이 들어 있는지 확인한다.

## 시나리오 8 — 질문 여부와 " (기본값)" (FR-013, FR-013b, SC-009)

(a) `questions.enabled: true`, `defaults.format: "png"`로 "이거 변환해줘" → 형식 선택지가 `SVG`, `PNG (기본값)`, `PDF`. (b) `questions.enabled: false`, `defaults.scope: "document"`, `defaults.pdfLayout: "single"` → 아무것도 묻지 않고 1페이지 PDF. (c) `questions.enabled: false`, `defaults.format: "none"`, 범위가 다이어그램만으로 정해진 요청 → 형식 질문만 뜸.

## 시나리오 9 — 옵션 추가 내구성 (SC-006)

시험용 옵션 하나를 exporting의 옵션 정의에 더하고(설정 파일엔 추가하지 않음) `read-settings.js`를 실행 → 기본값으로 해석되고 안내가 없으며 `lib/settings.js`는 바꿀 필요가 없다. 확인 후 되돌린다.

## Validation Results (T019, 2026-11-13)

| 시나리오 | 방법 | 결과 | 비고 |
|----------|------|------|------|
| 5. 설정 해석 | `read-settings.js` 실제 실행 | PASS | (a) 배포본·(e) 파일 없음 → 안내 없음. (b) `png.scale: 0` → 그 키만 기본값 + 안내 1줄. (c) 절대 경로 `output.directory`·정의에 없는 `pngg.scale` → 각각 안내 1줄, 나머지 값(`png.scale: 2`)은 적용. (d) 끝 쉼표 → 읽지 못함 안내 1줄·모든 값 기본값. 문자열 안 `//`(`"url//x"`)는 주석으로 잘리지 않고 값 검증 단계에서 거부됨 |
| 6. PNG 배율·산출물 위치 | 다이어그램 1개짜리 마크다운을 실제 변환 | PASS | 배포본: `src/exports/sample-1.png` 615×210. `png.scale: 2`, `output.directory: "../tmp-exports"`: 원본 한 단계 위 `tmp-exports/sample-1.png` 410×140(정확히 2/3) |
| 7. PDF 접은 글 펼치기 | `<details>`(open 없음)가 있는 파일을 문서 PDF로 변환 후 `pypdf`로 텍스트 추출 | PASS | 접힌 내용의 표식 문자열이 PDF 텍스트에 포함됨 |
| 9. 옵션 추가 내구성 | exporting 옵션 정의에 시험용 `trial.flag` 추가 후 `read-settings.js` 실행 | PASS | `lib/settings.js` 수정 없이 기본값 `false`로 해석, 안내 없음. 확인 후 되돌림 |

시나리오 1~4·8은 LLM이 따르는 지침 동작이라 실제 스킬 호출로 확인해야 하며, 이번 구현 단계에서는 SKILL.md 규칙 대조까지만 했다.
