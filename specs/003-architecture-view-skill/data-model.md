# Data Model: Architecture View Skill

이 기능은 데이터베이스나 영속 저장소를 갖지 않는다. 아래 "엔티티"는 skill 실행 중 다뤄지는 개념적 대상과 그 속성을 정리한 것이며, spec.md의 Key Entities를 구체화한다.

## Process Description (입력)

사용자가 자연어로 제공하는, 구조 뷰로 표현하고자 하는 프로세스 설명.

| 속성 | 설명 |
|------|------|
| raw_text | 사용자가 입력한 원문 설명 |
| identified_components | 설명에서 식별된 컴포넌트 목록 (명시적으로 언급되었거나 명확히 함의된 것만) |
| identified_dependencies | 식별된 컴포넌트 간 호출·의존 관계 |
| grouping_signals | 컴포넌트 이름의 접두사/네임스페이스, 명시적으로 언급된 계층·도메인 구분 등 자동 그룹핑의 근거가 되는 신호 (없으면 빈 목록) |
| responsibility_statements | 설명에서 확인 가능한, 각 컴포넌트 자신의 책임에 대한 서술 (컴포넌트별로 없을 수도 있음) |

**검증 규칙**: `identified_components`나 `identified_dependencies`가 비어 있으면(대상을 특정할 수 없으면), 구조 뷰를 생성하기 전에 사용자에게 무엇을 그려야 하는지 되묻는다.

## Purpose (목적)

결과의 초점을 나타내는 값. 실제로 불분명할 때만 질문으로 확인하며, 명시되거나 맥락상 추론 가능하면 되묻지 않는다(spec.md FR-001).

| 속성 | 설명 |
|------|------|
| value | `onboarding` / `troubleshooting` / `other` 중 하나 |
| source | `stated`(사용자가 명시적으로 밝힘) / `inferred`(설명·맥락에서 추론됨, 질문 없이 확정) / `answered`(실제로 불분명해 질문했고 답변으로 확정됨) / `defaulted`(질문했으나 애매해서 기본값 `onboarding` 적용) 중 하나 |
| other_detail | `value`가 `other`일 때, 후속 질문에 대한 사용자의 자유 서술 답변 |

**검증 규칙**: `source`가 `defaulted`인 경우, 그 사실을 사용자에게 알려야 한다(spec.md FR-002). `value`가 `other`인데 `other_detail`이 없으면 구조 뷰를 생성할 수 없다(spec.md FR-003). `source`가 `stated`나 `inferred`인 경우 목적 확인 질문 자체가 사용자에게 제시되지 않아야 한다(spec.md FR-001).

## Automatic Grouping Rule (판단 로직)

Components & Dependencies 섹션에서 컴포넌트를 `subgraph`로 묶을지 결정하는 규칙.

| 속성 | 설명 |
|------|------|
| signal_present | `Process Description.grouping_signals`가 비어 있지 않은지 여부 |
| groups | `signal_present`가 참일 때만 여러 그룹으로 나뉨. 거짓이면 전체 컴포넌트가 그룹 1개(다이어그램에는 `subgraph` 테두리 없이, 비교 범위 계산에서는 그룹 1개로 취급) |

**검증 규칙**: `signal_present`가 거짓이면 다이어그램에 `subgraph`를 그려서는 안 된다 — 근거 없이 그룹을 만들어서는 안 된다(spec.md FR-006). 단, Responsibility 섹션의 비교 범위 계산에서는 전체 컴포넌트 집합을 그룹 1개로 취급한다(spec.md FR-008).

## Components & Dependencies Section (구조 뷰의 첫 부분)

| 속성 | 설명 |
|------|------|
| components | 식별된 컴포넌트 목록 |
| groups | `Automatic Grouping Rule`에 따라 결정된 그룹(들) |
| dependencies | 컴포넌트 간 의존 화살표 목록 |

**표현 형식**: Mermaid `graph`/`flowchart` — 그룹은 `subgraph`, 의존관계는 화살표(spec.md FR-007).

## Responsibility Comparison Item (책임 비교 항목)

같은 그룹에 속하고 서로 직접 의존관계(호출)로 연결된 두 컴포넌트를 대조한, 순서 없는(unordered) 항목.

| 속성 | 설명 |
|------|------|
| group | 이 항목이 속한 그룹 (그룹이 없으면 전체 컴포넌트 집합) |
| component_a, component_b | 비교 대상 두 컴포넌트 — 서로 직접 호출하는 쌍만 해당 (a, b의 순서는 항목 식별에 의미가 없음 — (A,B)와 (B,A)는 같은 항목) |
| dependency_direction | `a_depends_on_b` / `b_depends_on_a` / `mutual`(양방향 호출) 중 하나 — 항목 서식이 그대로 반영해야 하는 실제 방향 |
| responsibility_a, responsibility_b | 설명에서 확인 가능한 각 컴포넌트의 책임 (없으면 "명시되지 않음") |

**검증 규칙(개수)**: 그룹 내에서 서로 직접 호출하는 컴포넌트 쌍마다 정확히 하나씩 존재해야 한다 — 서로 호출하지 않는 쌍이나 서로 다른 그룹에 속한 컴포넌트 사이에는 항목을 만들지 않는다(spec.md FR-008). 개수는 그룹 내 실제 의존관계 엣지 수와 같으며, 상한은 그룹 크기가 n일 때 n×(n-1)/2(모든 쌍이 서로 호출하는 경우)다.
**검증 규칙(내용)**: `responsibility_a`나 `responsibility_b`가 "명시되지 않음"이면 추측해서 채워서는 안 되며(spec.md FR-009, FR-010), 항목은 `dependency_direction`을 볼드 이름과 함께 그대로 서술하고 별도의 "차이" 요약 문장은 담지 않는다 — 예: "**A**는 **B**에 의존한다: A는 <책임>. B는 <책임>."(spec.md FR-027).

## Group Comparison Item (그룹 비교 항목)

서로 다른 두 그룹 중 실제로 교차-그룹 의존관계(한쪽 그룹의 컴포넌트가 다른 쪽 그룹의 컴포넌트를 호출)가 있는 쌍만 대조한, 순서 없는 항목. 컴포넌트 대신 그룹 자체가 비교 대상이라는 점만 다르고 나머지 구조는 Responsibility Comparison Item과 같다.

| 속성 | 설명 |
|------|------|
| group_a, group_b | 비교 대상 두 그룹 — 실제로 교차-그룹 의존관계가 있는 쌍만 해당 (순서는 항목 식별에 의미가 없음) |
| dependency_direction | `a_depends_on_b` / `b_depends_on_a` / `mutual`(양방향) 중 하나 |
| label_a, label_b | 설명이 실제로 부여한 각 그룹의 이름/레이블. 설명이 그 그룹에 대해 레이블을 넘어서는 내용을 실제로 언급했다면 그 내용도 포함 |

**검증 규칙(개수)**: 그룹 간에 실제 교차-그룹 의존관계가 있는 쌍마다 정확히 하나씩 존재해야 한다. 의존관계가 없는 그룹 쌍이나, 그룹이 1개 이하(그룹이 없거나 하나뿐)인 경우에는 항목 자체가 하나도 없어야 한다(spec.md FR-025). 개수는 실제 연결된 그룹 쌍 수와 같으며, 상한은 그룹이 m개일 때 m×(m-1)/2(모든 그룹 쌍이 서로 연결된 경우)다.
**검증 규칙(내용)**: `label_a`/`label_b`(및 그 이상 실제로 언급된 내용)만 근거로 삼아야 하며, 레이블을 넘어서는 역할·목적을 추측해서는 안 된다(spec.md FR-026). 항목은 `dependency_direction`을 볼드 이름과 함께 그대로 서술하고 별도의 "차이" 요약 문장은 담지 않는다(spec.md FR-027).

## Architecture View (출력물)

Components & Dependencies 섹션과 Responsibility 섹션으로 구성된 문서.

| 상태 | 설명 | 전이 조건 |
|------|------|-----------|
| Draft | `Purpose`가 확정된 뒤, Components & Dependencies와 Responsibility가 1차 생성된 문서 | `Purpose.value`가 확정되고 대상 컴포넌트가 식별되었을 때 생성 |
| Checked | Anti-Pattern Checklist(AP-1~AP-12) 전체 항목을 통과(또는 위반 수정 완료)한 상태 | Draft에 대해 AP-1~AP-12 전부 "예" |
| Presented | 사용자에게 최종적으로 제시된 결과 — 채팅 응답에는 Output File 링크만 포함(코드 미노출) | Draft가 Checked 상태에 도달한 후에만 전이 가능 |

**불변 조건**: `Presented` 상태의 구조 뷰는 항상 `Checked`를 거쳐야 한다(spec.md FR-019, FR-020).

## Delegation Handoff (위임)

구조 뷰가 `Presented` 상태에 도달한 뒤, 시퀀스 다이어그램 생성 여부를 결정하는 절차.

| 속성 | 설명 |
|------|------|
| offered | 확인 질문을 했는지 (구조 뷰가 `Presented`에 도달하면 항상 `true`) |
| user_response | `agreed` / `declined` / `no_response` |
| enriched_description | 원래 `Process Description.raw_text` + Components & Dependencies의 컴포넌트·그룹·의존관계 + Responsibility의 책임 정보를 반영해 재구성한, 더 풍부한 자연어 프로세스 설명 — `user_response == agreed`일 때만 생성되어 `generating-zenuml-diagrams`의 입력이 됨 |

**검증 규칙**: `user_response`가 `agreed`일 때만 `generating-zenuml-diagrams`를 실행한다. `declined`나 `no_response`면 실행하지 않으며, 재차 확인 질문을 하지 않는다(spec.md FR-015, FR-016). `offered`가 `false`인 경우(구조 뷰 생성이 완료되지 않은 경우)는 이 엔티티 자체가 생성되지 않는다(spec.md FR-017).

## Anti-Pattern Checklist (번들 자산)

구조 뷰 초안을 사용자에게 보여주기 전 대조하는 규칙 목록. `.claude/skills/generating-architecture-views/SKILL.md` 본문에 포함된다.

| 항목 ID | 검사 내용 |
|---------|-----------|
| AP-1 | 설명에 없는 컴포넌트가 추가되지 않았는가 |
| AP-2 | 설명에 없는 의존관계가 추가되지 않았는가 |
| AP-3 | 신호 없이 만들어진 그룹(subgraph)이 없는가 |
| AP-4 | 각 그룹 내부의 비교 항목 수가 정확히 n×(n-1)/2인가(순서 있는 쌍으로 중복 생성되지 않았는가) |
| AP-5 | 그룹이 2개 이상이면 그룹 간 비교 항목 수가 정확히 m×(m-1)/2인가(그룹이 1개 이하면 이 비교 자체가 없는가), 그리고 그 내용이 그룹 레이블만 근거로 하는가 |
| AP-6 | 책임이 명시되지 않은 컴포넌트에 대해 책임·차이를 추측해서 채우지 않았는가 |
| AP-7 | 시스템에 등장하지 않는 일반적 개념을 비교하는 섹션을 만들지 않았는가 (FR-013) |
| AP-8 | Runtime Flow(시퀀스) 다이어그램을 스스로 그리지 않았는가 (위임 대상 영역 침범 금지) |
| AP-9 | 시퀀스 다이어그램 생성 여부를 확인했는가, 동의 없이 `generating-zenuml-diagrams`를 실행하지 않았는가 |

**검증 규칙**: 하나라도 위반(위반=해당 항목에 대해 "아니오")이면, 사용자에게 결과를 제시하기 전에 초안을 수정해야 한다(spec.md FR-019, FR-020).

## Output Files (출력 부속물)

| 속성 | 설명 |
|------|------|
| architecture_file_path | `.zenuml/<slug>.architecture.md` — 구조 뷰(Components & Dependencies, Responsibility)를 담는 파일. 항상 생성됨(구조 뷰가 완성된 경우) |
| sequence_file_path | `.zenuml/<slug>.md` — `generating-zenuml-diagrams`가 생성하는 시퀀스 다이어그램 파일. `Delegation Handoff.user_response == agreed`일 때만 존재 |
| available | 파일 저장(파일시스템 접근) 가능 여부 — `false`면 파일 대신 채팅 응답에 텍스트를 직접 제공 |

**검증 규칙**: `sequence_file_path`는 위임에 동의하지 않으면 존재하지 않는다(spec.md Key Entities "출력 파일"). `available`이 `false`인 경우 두 산출물 모두 채팅 응답에 직접 텍스트로 제공된다(spec.md FR-024).
