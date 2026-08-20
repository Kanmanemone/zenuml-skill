# Data Model: Markdown 다이어그램/PDF export 스킬

spec.md의 Key Entities를 실행 가능한 수준으로 구체화한다. 이 스킬에는 영속 데이터베이스가 없으므로, 여기서 정의하는 "엔티티"는 스킬 실행 한 번(하나의 변환 요청)의 생애주기 동안만 존재하는 개념적 자료구조다.

## ConversionRequest (변환 요청)

사용자의 요청에서 판단되거나 `AskUserQuestion`으로 확인된 값을 담는다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `targetFile` | path | 변환 대상 마크다운 파일 경로 |
| `scope` | `"diagram"` \| `"document"` | 다이어그램만 변환할지, 문서 전체를 변환할지 (FR-002) |
| `format` | `"svg"` \| `"png"` \| `"pdf"` | 출력 형식 (FR-001) |
| `diagramSelector` | 선택적, 문자열/인덱스 | 사용자가 특정 다이어그램을 지목했다면 그 식별자 — 없으면 문서의 모든 다이어그램을 대상으로 함(Assumptions 기본값) |

**검증 규칙**:
- `format`이 명시되지 않은 요청에서는 `AskUserQuestion`으로 확정되기 전까지 `ConversionRequest`가 완결되지 않는다(FR-001).
- `scope`가 명시되지 않은 요청에서도 마찬가지다(FR-002).
- `format`과 `scope`가 모두 미확정이면, 확정 질문은 하나의 `AskUserQuestion` 호출(두 개의 `questions` 항목)로 함께 이뤄져야 한다(FR-003) — 자세한 모양은 `contracts/skill-interface.md` 참고.
- `scope = "document"`이면서 `format = "svg"` 또는 `"png"`인 조합을 spec.md 자체가 금지하지는 않지만, 이번 구현(tasks.md User Story 2)은 `scope = "document"`를 항상 `format = pdf`로 처리한다 — PDF만 여러 페이지·다중 다이어그램 문서를 온전히 표현할 수 있고, `export-document-pdf.js` 외의 문서 전체용 스크립트는 이번 범위에서 만들지 않았기 때문이다(오버엔지니어링 방지). `scope = document`가 확정되면 `format` 질문 자체를 생략한다(SKILL.md "Scope: whole document" 참고).

## DiagramSource (다이어그램 소스)

마크다운 파일 안에 있는, 변환 대상이 되는 다이어그램 원본 코드.

| 필드 | 타입 | 설명 |
|---|---|---|
| `rawCode` | string | 코드펜스 안의 원본 다이어그램 정의 — 렌더러 지정(예: `%%{init: {"flowchart": {"defaultRenderer": "elk"}}}%%`)을 포함해 **수정 없이 그대로** 렌더러에 전달됨 (FR-004) |
| `flavor` | `"zenuml"` \| `"mermaid"` | `rawCode`의 첫 토큰이 `zenuml`인지 여부로 구분 — 렌더러 선택에는 영향 없음(둘 다 같은 `mmdc` 호출로 처리, FR-006) |
| `position` | 정수(등장 순서) | 문서 안에서 몇 번째로 등장하는 다이어그램인지 — `mmdc`가 매기는 번호(`-1`, `-2`, ...)와 대응 |

**불변 조건**: `rawCode`는 렌더링 이전에 스킬이나 스크립트에 의해 파싱·재작성되지 않는다. 렌더러(`mmdc`)에게 그대로 넘겨 렌더러 자신이 해석하게 한다 — 이것이 FR-004("렌더러 지정을 임의로 제거·대체하지 않는다")를 보장하는 유일한 방법이다(스킬이 직접 `defaultRenderer` 유무를 감지해 분기하는 로직을 두지 않음 — 오버엔지니어링 방지).

## ConversionArtifact (변환 산출물)

완료된 변환 결과 파일.

| 필드 | 타입 | 설명 |
|---|---|---|
| `path` | path | 생성된 파일 경로 — 항상 `sourceFile`이 있는 디렉토리 바로 아래의 `ExportDirectory` 안이다(FR-009) |
| `format` | `"svg"` \| `"png"` \| `"pdf"` | 실제 산출물의 형식 |
| `scope` | `"diagram"` \| `"document"` | 어느 범위의 변환 결과인지 |
| `sourceFile` | path | 원본 마크다운 파일 경로 |
| `diagramTextSelectable` | boolean | `format = "pdf"` && `scope = "document"`일 때만 의미 있음 — true여야 FR-007을 만족 |

## ExportDirectory (전용 산출물 디렉토리)

원본 마크다운 파일이 위치한 디렉토리 바로 아래에 있는, 변환 산출물만을 모아두는 하위 디렉토리(`exports/`, FR-009~012).

| 필드 | 타입 | 설명 |
|---|---|---|
| `sourceDir` | path | 변환 대상 마크다운 파일이 위치한 디렉토리 (`path.dirname(targetFile)`) |
| `path` | path | `sourceDir` 바로 아래의 고정된 하위 디렉토리 — `<sourceDir>/exports` |

**불변 조건**:
- 존재하지 않으면 산출물을 쓰기 직전 재귀적으로 생성한다(FR-010).
- 같은 `sourceDir`를 공유하는 여러 원본 파일의 산출물은 모두 같은 `path`에 모인다 — 원본 파일마다 별도 하위 디렉토리를 만들지 않는다(FR-012).
- `ConversionArtifact`의 베이스 이름·번호 매김 규칙은 이 디렉토리 규칙과 무관하게 유지된다(FR-011).

## IntermediateDocument (중간 산출물 — 문서 전체 PDF 파이프라인 전용)

`research.md`의 "User Story 2 파이프라인" 결정에서 1단계 산출물. 사용자에게 직접 노출되지 않는, 파이프라인 내부에서만 쓰이는 임시 산출물이다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `markdownWithImageRefs` | path | `mmdc -o *.md`가 만들어낸, 다이어그램 코드펜스가 이미지 참조로 치환된 마크다운 |
| `diagramSvgFiles` | path[] | 1단계에서 렌더링된 개별 SVG 파일들 — 2단계에서 HTML에 인라인 삽입된 뒤 삭제되는 임시 파일 |

**생애주기**: `ConversionRequest`(scope=document, format=pdf) 하나를 처리하는 동안만 존재한다. 최종 `ConversionArtifact`(PDF)가 만들어지면 임시 파일은 정리된다(구현 세부사항).

## 관계 요약

```text
ConversionRequest ──(대상)──> DiagramSource[] (마크다운에서 발견된 다이어그램들)
ConversionRequest ──(scope=document, format=pdf 인 경우)──> IntermediateDocument ──> ConversionArtifact
ConversionRequest ──(그 외 조합)──> ConversionArtifact (DiagramSource 1개당 1개, 또는 scope=diagram이면 여러 개)
```
