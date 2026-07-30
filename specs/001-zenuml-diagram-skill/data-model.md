# Data Model: ZenUML Diagram Skill

이 기능은 데이터베이스나 영속 저장소를 갖지 않는다. 아래 "엔티티"는 skill 실행 중 다뤄지는 개념적 대상과 그 속성을 정리한 것이며, spec.md의 Key Entities를 구체화한다.

## Process Description (입력)

사용자가 자연어로 제공하는, 다이어그램으로 표현하고자 하는 프로세스 설명.

| 속성 | 설명 |
|------|------|
| raw_text | 사용자가 입력한 원문 설명 |
| identified_participants | 설명에서 식별된 참가자 목록 (명시적으로 언급된 것만) |
| identified_flow | 식별된 메시지/호출 순서, 조건 분기, 반복 구조 |
| ambiguities | 다이어그램을 정확히 구성하기에 정보가 부족한 지점 목록 (FR-007과 연결) |

**검증 규칙**: `ambiguities`가 비어 있지 않으면, 다이어그램을 생성하기 전에 사용자에게 명확화 질문을 먼저 제시해야 한다(spec.md User Story 3).

## Syntax Reference (번들 자산)

`references/syntax.md`에 저장된, ZenUML DSL 문법 규칙 문서.

| 속성 | 설명 |
|------|------|
| source | `mermaid-js/zenuml-core` 저장소의 `docs/DSL_SYNTAX.md` |
| license | MIT — 원출처 고지 필수 |
| sections | 참가자 선언, 동기/비동기 메시지, 반환값, 조건/반복, 예외 처리, 주석, 스타일링 등 (research.md, Phase 0 참조) |

**상태 변화**: 없음 — 정적 참조 문서로, skill 실행 중 읽히기만 하고 수정되지 않는다.

## Anti-Pattern Checklist (번들 자산)

다이어그램 초안을 사용자에게 보여주기 전 대조하는 규칙 목록. `.claude/skills/generating-zenuml-diagrams/SKILL.md` 본문에 포함된다.

| 항목 ID | 검사 내용 |
|---------|-----------|
| AP-1 | 설명에 없는 참가자가 추가되지 않았는가 |
| AP-2 | 설명에 없는 메시지/메서드 호출이 추가되지 않았는가 |
| AP-3 | 설명에 없는 조건 분기·반복이 추가되지 않았는가 |
| AP-4 | 근거 없는 예외 처리(try/catch)나 반환값이 삽입되지 않았는가 |
| AP-5 | 동일 로직을 표현하는 가장 얕은 중첩 구조를 사용했는가 |

**검증 규칙**: 하나라도 위반(위반=해당 항목에 대해 "아니오")이면, 사용자에게 결과를 제시하기 전에 초안을 수정해야 한다(spec.md FR-006).

## ZenUML Diagram Draft → Final (출력물)

skill이 생성하는 ZenUML DSL 텍스트. 상태가 두 단계로 전이된다.

| 상태 | 설명 | 전이 조건 |
|------|------|-----------|
| Draft | Process Description으로부터 1차 생성된 ZenUML DSL 텍스트 | Process Description에 `ambiguities`가 없을 때 생성 |
| Checked | Anti-Pattern Checklist 전체 항목을 통과(또는 위반 수정 완료)한 상태 | Draft에 대해 AP-1~AP-5 전부 "예" |
| Presented | 사용자에게 최종적으로 제시된 결과 — 채팅 응답에는 Output File 링크만 포함(코드 미노출) | Draft가 Checked 상태에 도달한 후에만 전이 가능 |

**불변 조건**: `Presented` 상태의 다이어그램은 항상 `Checked`를 거쳐야 하며, `Checked`를 건너뛰고 바로 `Presented`될 수 없다(spec.md FR-005, FR-006).

## Output File (출력 부속물)

저장소의 `.zenuml/` 아래 저장되는 파일. `Checked` 상태의 ZenUML 원문을 Mermaid `zenuml` 코드펜스에 그대로 담는다 — 원문 자체가 VS Code 마크다운 프리뷰에서 렌더링 가능한 미리보기이기도 하다(번역 불필요). 채팅 응답에는 이 파일을 가리키는 상대 경로 링크만 노출된다(코드 자체는 응답에 직접 노출하지 않음).

| 속성 | 설명 |
|------|------|
| source_diagram | 파일에 담기는 `Checked` 상태의 ZenUML Diagram 원문 (Mermaid `zenuml` 코드펜스로 감싸짐) |
| file_path | `.zenuml/` 아래 저장된 상대 경로 |
| available | 파일 저장(파일시스템 접근) 가능 여부 — `false`면 파일 대신 채팅 응답에 ZenUML DSL 텍스트를 직접 제공 |

**검증 규칙**: `source_diagram`이 `Checked` 상태에 도달하기 전에는 파일이 생성되지 않는다(spec.md FR-011). `available`이 `false`인 경우 `Presented` 결과에는 파일 링크 대신 ZenUML DSL 텍스트가 직접 포함된다(spec.md Edge Cases).
