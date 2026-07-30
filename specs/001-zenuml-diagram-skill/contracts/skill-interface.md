# Contract: `generating-zenuml-diagrams` Skill Interface

이 skill은 API나 CLI가 아니라 Claude Code Skill이므로, "계약"은 SKILL.md가 Claude에게 보장해야 하는 **입력→동작→출력 규약**으로 정의한다.

## Trigger (언제 이 skill이 선택되어야 하는가)

- 사용자가 ZenUML, ZenUML DSL, 또는 (문맥상 시퀀스 다이어그램을 뜻하는) "zenuml 다이어그램/시퀀스 다이어그램 그려줘" 류의 요청을 할 때.
- SKILL.md frontmatter의 `description`은 이 트리거 조건과 스킬이 하는 일(정확하고 군더더기 없는 ZenUML DSL 생성)을 3인칭으로 명시해야 한다(Anthropic 가이드 준수).

## Input Contract

| 필드 | 필수 | 설명 |
|------|------|------|
| description | 필수 | 다이어그램으로 표현할 프로세스에 대한 자연어 설명 (한국어/영어 등 사용자 언어 그대로) |
| target_participants_hint | 선택 | 사용자가 참가자 이름을 명시적으로 지정한 경우 |

**전제조건**: 입력이 비어있거나 프로세스를 특정할 수 없으면, skill은 다이어그램을 생성하지 않고 무엇을 그려야 하는지 되묻는다.

## Output Contract

### 성공 시 (Process Description에 ambiguity 없음, 파일 저장 가능)

```text
<.zenuml/<slug>.md 를 가리키는 상대 경로 링크 한 줄>
```

- 채팅 응답에는 ZenUML DSL 코드를 직접 노출하지 않는다 — `references/syntax.md` 문법을 준수하는 유효한 ZenUML DSL(spec.md FR-003)을 `.zenuml/` 아래 파일에 저장하고, 그 파일을 가리키는 상대 경로 링크만 응답에 남긴다(spec.md FR-011).
- 저장되는 파일은 ZenUML 원문을 Mermaid `zenuml` 코드펜스에 담는다 — 번역 없이 원문 그대로가 VS Code 마크다운 프리뷰에서 렌더링되는 미리보기이기도 하다(research.md 참조. Claude Artifact는 `zenuml` 타입을 렌더링하지 않으므로 이 파일 방식을 쓰는 이유이기도 하다).
- 설명에 없는 참가자·메시지·분기·예외 처리를 포함해서는 안 된다(spec.md FR-001, FR-002).
- 파일에 저장되는 내용은 Anti-Pattern Checklist(data-model.md 참조) 전체 항목을 통과한 이후에만 확정된다.

### 성공 시 (파일 저장 불가능한 환경)

```text
<ZenUML DSL 코드 블록>
```

- 파일시스템 접근이 없는 환경에서는 `.zenuml/` 링크 대신 ZenUML DSL 텍스트를 채팅 응답에 직접 제공한다(spec.md FR-011, Edge Cases).

### 명확화가 필요할 때 (Process Description에 ambiguity 있음)

- ZenUML DSL을 생성하지 않고, 다이어그램 정확성에 직접 영향을 주는 구체적 질문을 제시한다(spec.md FR-007, User Story 3).
- 질문은 "누가 누구를 호출하는가", "어떤 조건에서 분기하는가"처럼 다이어그램 구조에 영향을 주는 것에 한정하고, 사소한 표시 이름 같은 세부사항은 합리적으로 기본값을 사용한다(research.md, Phase 0).

### 범위 밖 요청일 때

- ZenUML이 지원하지 않는 다이어그램 유형(클래스/배포 등) 요청 시: 지원 범위(시퀀스 다이어그램 전용)를 안내한다(spec.md FR-008, Edge Cases).
- 기존 Mermaid/PlantUML 변환이나 코드베이스 분석 요청 시: 현재 범위 밖임을 안내한다(spec.md Edge Cases, Assumptions).
- 렌더링된 이미지 요청 시: 주 출력물은 텍스트 DSL이며, FR-011에 따라 저장되는 파일 안에 Mermaid 미리보기가 이미 포함되어 있으므로 그 파일을 열어 확인하면 된다는 점을 안내한다(spec.md FR-010, Edge Cases).

## Error/Fallback Behavior

이 skill에는 실행 코드가 없으므로 "예외"는 발생하지 않는다. 대신 위 "범위 밖 요청" 및 "명확화가 필요할 때" 분기가 유일한 비-happy-path이며, 두 경우 모두 사용자에게 명확한 다음 행동(질문에 답하거나, 범위 밖임을 인지)을 안내하는 것으로 끝난다.
