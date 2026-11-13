# Contract: `exporting-markdown-diagrams` Skill Interface

이 skill은 API나 CLI가 아니라 Claude Code Skill이므로, "계약"은 `SKILL.md`가 Claude에게 보장해야 하는 **입력→동작→출력 규약**으로 정의한다. 이 스킬은 다른 두 스킬(`generating-zenuml-diagrams`, `generating-architecture-views`)의 산출물(`.zenuml/*.md`)을 다룰 수 있지만, 그 두 스킬에 의존하지는 않는다 — 임의의 마크다운 파일도 대상이 될 수 있다.

## Trigger (언제 이 skill이 선택되어야 하는가)

- 사용자가 마크다운 파일 속 다이어그램을 이미지(SVG/PNG)로 뽑아달라고 요청할 때.
- 사용자가 마크다운 파일(다이어그램 포함 여부와 무관)을 PDF로 만들어달라고 요청할 때.
- SKILL.md frontmatter의 `description`은 "export", "변환", "SVG/PNG/PDF로 뽑기" 같은 트리거 조건을 명시하며, `generating-zenuml-diagrams`/`generating-architecture-views`(다이어그램 *생성*)와 트리거가 겹치지 않도록 "이미 있는 다이어그램/문서를 다른 형식으로 바꾼다"는 점을 명확히 구분해야 한다.

## Input Contract

| 필드 | 필수 | 설명 |
|------|------|------|
| targetFile | 필수 | 변환 대상 마크다운 파일 경로 또는 그것을 특정할 수 있는 설명 |
| format | 선택 | `svg` \| `png` \| `pdf` — 요청에 명시돼 있지 않으면 `AskUserQuestion`으로 확인(FR-001) |
| scope | 선택 | `diagram`(다이어그램만) \| `document`(문서 전체) — 요청에 명시돼 있지 않으면 `AskUserQuestion`으로 확인(FR-002) |
| pdfLayout | 선택, `scope = document`일 때만 의미 있음 | `single`(1페이지 단일) \| `paginated`(표준 인쇄 규격) — `scope`가 `document`로 확정됐는데 명시돼 있지 않으면 `AskUserQuestion`으로 확인(FR-014) |

**전제조건**: `targetFile`을 특정할 수 없으면(파일이 존재하지 않거나 마크다운이 아니면) 변환을 시작하지 않고 그 사실을 안내한다(spec.md Edge Cases).

## Clarification Contract (`AskUserQuestion` 모양)

빠진 항목(형식, 범위, 페이지 구성)은 모두 **하나의 `AskUserQuestion` 호출**에 `questions` 배열로 함께 담아 묻는다(FR-003, FR-014) — 한 항목의 답을 받은 뒤 다른 항목을 따로 이어 묻지 않는다. 이미 명시된 항목은 절대로 다시 묻지 않는다(SC-001). 무엇이 "빠진" 항목인지는 설정(`questions.enabled`, `defaults.*`, 007)이 정한다.

- **형식 질문**: 선택지 `SVG` / `PNG` / `PDF`. `scope`가 이미 `document`면 `PDF` / `PNG`만(문서 전체 SVG는 없음, 008).
- **범위 질문**: 선택지 `다이어그램만` / `문서 전체`. 형식도 함께 묻거나 요청이 SVG를 지정했으면 `문서 전체` 설명에 PDF·PNG만 가능함을 밝힌다.
- **페이지 구성 질문**: `scope`가 `document`이거나 미정이고 `pdfLayout`이 명시되지 않았을 때만 넣는다. 선택지 순서는 `1페이지 단일` 먼저, `표준 인쇄 규격` 다음. 범위 질문과 함께 물을 때는 문서 전체일 때만 적용된다고 질문에 밝힌다. `scope`가 `diagram`으로 정해지면 그 답은 쓰지 않는다.
- **재질문**: 답 또는 요청이 `문서 전체` + `SVG`로 모순될 때만, 지원하지 않는다고 안내하고 형식 질문(`PDF` / `PNG`) 하나만 다시 묻는다. 그 밖에는 두 번째 질문 상호작용이 생기지 않는다.
- 빠진 항목이 없으면 질문 없이 바로 진행한다.

## Rendering Contract

- 대상 다이어그램의 원본 코드(코드펜스 안 내용 전체 — 렌더러 지정을 포함해)는 수정 없이 그대로 렌더러에 전달되어야 한다(FR-004, data-model.md `DiagramSource`의 불변 조건). 스킬은 다이어그램 코드를 파싱해 렌더러 설정을 감지·분기하는 로직을 두지 않는다.
- 변환은 항상 번들 스크립트(결정적 도구 실행)로 수행하며, 다이어그램/문서의 내용을 LLM이 재해석하거나 다시 생성하지 않는다(FR-005). `SKILL.md`는 어느 스크립트를 어떤 인자로 호출할지 판단하는 오케스트레이션만 담당한다.
- zenuml 플레이버 다이어그램과 일반 Mermaid flowchart 모두 같은 경로로 처리되어야 한다(FR-006) — 스킬이 둘을 구분해 다른 로직을 타지 않는다(`research.md` Decision 참고).

## Output Contract

산출물은 항상 `targetFile`이 있는 디렉토리 바로 아래의 전용 하위 디렉토리(`exports/`)에 생성된다(FR-009) — `targetFile`과 같은 디렉토리에 흩어놓지 않는다. 그 디렉토리가 없으면 변환 전에 자동으로 생성한다(FR-010). 파일명 규칙(베이스 이름, `-1`/`-2` 번호 매김)은 이 디렉토리 규칙과 무관하게 그대로 유지된다(FR-011).

### 성공 시 — `scope = diagram`

```text
<생성된 SVG/PNG(/PDF) 파일 경로 한 줄 또는 다이어그램별로 여러 줄>
```

- 문서에 다이어그램이 여러 개 있고 특정 다이어그램이 지목되지 않았다면, 각 다이어그램이 개별 파일로 변환되고 각각의 경로가 제시된다(spec.md Assumptions, `data-model.md`).

### 성공 시 — `scope = document`, `format = pdf`

```text
<생성된 PDF 파일 경로 한 줄>
```

- 결과 PDF에 포함된 다이어그램은 벡터(SVG)로 삽입되어 PDF 뷰어에서 텍스트를 선택·복사할 수 있어야 한다(FR-007, SC-004). 이 계약을 어기는 산출물(다이어그램이 래스터로 삽입된 PDF)은 실패로 취급한다.

### 실패 시(대상 파일 없음 / 지원하지 않는 다이어그램 문법 / 도구 실행 실패)

```text
<무엇이 실패했는지에 대한 명확한 안내 — LLM이 대신 내용을 지어내 응답하지 않는다>
```

- 렌더링 도구가 보고하는 오류를 그대로 전달한다(spec.md Edge Cases). 실패를 감추고 LLM 추론으로 조용히 대체하는 것은 FR-005 위반이므로 금지된다.
