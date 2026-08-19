# Data Model: Architecture View Skill

이 기능은 데이터베이스나 영속 저장소를 갖지 않는다. 아래 "엔티티"는 skill 실행 중 다뤄지는 개념적 대상과 그 속성을 정리한 것이며, spec.md의 Key Entities를 구체화한다.

## Process Description (입력)

사용자가 자연어로 제공하는, 구조 뷰로 표현하고자 하는 프로세스 설명.

| 속성 | 설명 |
|------|------|
| raw_text | 사용자가 입력한 원문 설명 |
| identified_components | 설명에서 식별된 컴포넌트 목록 (명시적으로 언급되었거나 명확히 함의된 것만) |
| identified_dependencies | 식별된 컴포넌트 간 의존 관계 목록 (각 관계는 아래 Dependency Edge로 구체화됨) |
| grouping_signals | 컴포넌트 이름의 접두사/네임스페이스, 명시적으로 언급된 계층·도메인 구분 등 자동 그룹핑의 근거가 되는 신호 (없으면 빈 목록) |
| responsibility_statements | 설명에서 확인 가능한, 각 그룹·컴포넌트 자신의 책임(추상/구체)에 대한 서술 (없을 수도 있음) |
| location_evidence | 설명이 제공하는 실제 위치 근거 — 로컬 루트 프로젝트 안의 파일/폴더 경로, 웹 레포지토리 URL, 또는 둘 다 없음 (하이퍼링크 해석의 유일한 근거, spec.md FR-022) |

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

Dependency 섹션에서 컴포넌트를 `subgraph`로 묶을지 결정하는 규칙.

| 속성 | 설명 |
|------|------|
| signal_present | `Process Description.grouping_signals`가 비어 있지 않은지 여부 |
| groups | `signal_present`가 참일 때만 여러 그룹으로 나뉨. 거짓이면 전체 컴포넌트가 그룹 1개(다이어그램에는 `subgraph` 테두리 없이, Collaboration 게이팅 계산에서는 그룹 1개로 취급) |

**검증 규칙**: `signal_present`가 거짓이면 다이어그램에 `subgraph`를 그려서는 안 된다 — 근거 없이 그룹을 만들어서는 안 된다(spec.md FR-006).

## Dependency Edge (의존 관계)

두 컴포넌트 사이의 실제 의존관계 하나.

| 속성 | 설명 |
|------|------|
| source, target | 관계의 출발/도착 컴포넌트 |
| nature | 관계의 성격(예: 호출, 타입 참조, 선언 참조) — 설명이 명시한 그대로, 열린 어휘. 명시되지 않았으면 `호출`이 기본값 |
| color | 이 엣지의 `linkStyle` 색 — 항상 `source`의 Node Color Class와 동일 |

**검증 규칙**: `nature`가 설명에 없으면 기본값(`호출`)을 쓰고 더 구체적인 성격을 추측해서는 안 된다(spec.md FR-008). `color`는 항상 `source` 노드의 색과 일치해야 한다(spec.md FR-008b).

## Node Color Class (노드 색상 클래스)

Dependency 다이어그램에서 노드를 시각적으로 구분하는 색상 지정.

| 속성 | 설명 |
|------|------|
| class_name | 역할을 반영한 서술적 이름(예: `navHostNode`) — 일련번호 같은 무의미한 이름 금지 |
| color | `references/templates.md`의 고정 팔레트(Tailwind 500번대) 중 하나, 첫 등장 순서대로 배정 |
| members | 이 클래스를 공유하는 노드 목록 — 보통 1개(개별 노드), 서로 개별적으로 구분할 필요가 없는 형제 노드는 여러 개가 하나의 클래스를 공유할 수 있음 |

**검증 규칙**: `members`가 2개 이상인 클래스는, 그 노드들이 다이어그램 안에서 서로 개별적으로 구분되지 않을 때만(엣지를 직접 만들지 않고, 다른 곳에서 개별적으로 구별되지 않을 때) 허용된다(spec.md FR-008b).

## Hyperlink Target (하이퍼링크 대상)

그룹 또는 요소 이름에 붙는(또는 붙지 않는) 링크.

| 속성 | 설명 |
|------|------|
| kind | `local_path`(로컬 루트 프로젝트 안 상대 경로) / `url`(웹 레포지토리의 파일 URL) / `none`(둘 다 확인 불가) 중 하나 |
| value | `kind`가 `local_path`면 `.zenuml/` 기준 상대 경로, `url`이면 완전한 URL, `none`이면 값 없음 |

**검증 규칙**: `value`는 오직 `Process Description.location_evidence`에서만 나와야 한다 — 이 스킬은 코드베이스를 직접 탐색해 경로를 알아내지 않는다(spec.md FR-022, FR-027c). `kind`가 `none`이면 Dependency의 `click`도, Responsibility/Collaboration의 Markdown 링크도 만들어서는 안 된다. 같은 그룹/요소는 Dependency·Responsibility·Collaboration 전체에서 동일한 Hyperlink Target을 재사용해야 한다(한 번만 해석).

## Dependency Section (구조 뷰의 첫 부분)

| 속성 | 설명 |
|------|------|
| components | 식별된 컴포넌트 목록 |
| groups | `Automatic Grouping Rule`에 따라 결정된 그룹(들) |
| edges | Dependency Edge 목록 |
| node_classes | Node Color Class 목록 |
| hyperlinks | 노드별 Hyperlink Target |

**표현 형식**: Mermaid `flowchart LR`, 그룹별 `direction TB`, 고정 `%%{init}%%` 스타일 블록(curve: basis, nodeSpacing 45, rankSpacing 70, cluster-label 20px/weight 700) — 그룹은 `subgraph`, 의존관계는 성격 레이블이 붙은 화살표, 각 노드는 `classDef`+`class`, 각 엣지는 `linkStyle`, 하이퍼링크가 있는 노드는 `click`(spec.md FR-007, FR-008, FR-008b, FR-027c).

## Responsibility Entry (책임 서술)

그룹 또는 요소 하나에 대한 책임 서술 — 더 이상 쌍끼리 비교하지 않는다(2026-08-02 두 번째 세션에서 옛 Responsibility/Group Comparison Item을 대체).

| 속성 | 설명 |
|------|------|
| target | 이 항목이 서술하는 그룹 또는 요소 — 아래 Multi-target (Parallel-Sibling) Consolidation Rule 조건을 만족하면 단일 대상이 아니라 병렬 형제 요소 3개 이상의 집합일 수 있다(각각 Hyperlink Target을 유지) |
| responsibility_abstract | 책임(추상) — 한 문장 요약. `target`이 병렬 형제 집합이면 그 병렬 역할을 설명하는 공유 문장 하나. 설명에서 확인할 수 없으면 "설명에 명시되지 않음" |
| responsibility_concrete | 역할(구체) — 설명이 실제로 언급한 이름·동작을 인용한 서술. `target`이 병렬 형제 집합이면 각 요소의 근거를 빠짐없이 요소별로 인용. 설명에서 확인할 수 없으면 "설명에 명시되지 않음" |

**검증 규칙**: 두 필드 중 어느 쪽도 추측으로 채워서는 안 되며, 설명에 없으면 "설명에 명시되지 않음"으로 정직하게 표시해야 한다(spec.md FR-009, FR-010). 그룹 하위 목록이 먼저(그룹이 있을 때만), 요소 하위 목록이 그다음이다(spec.md FR-005). `target`이 병렬 형제 집합인 경우, 헤딩에는 모든 이름이 "A, B, C" 형태로 나열되고 각각 개별 하이퍼링크된다(spec.md FR-009b).

## Collaboration Item (협력 항목)

실제 의존관계가 있는 그룹 쌍 또는 요소 쌍(또는 다수 대상 통합 조건을 만족하는 하나의 source와 통합된 target 집합)을 대조한 항목 — 옛 Responsibility/Group Comparison Item의 이항대립 메커니즘을 계승·확장한다.

| 속성 | 설명 |
|------|------|
| level | `group` 또는 `element` |
| source | 비교의 출발 대상 (그룹 또는 요소) |
| target | 단일 대상 이름, 또는 Multi-target (Parallel-Sibling) Consolidation Rule을 만족하면 대상들을 아우르는 서술적 표현 |
| direction | `source_depends_on_target` / `target_depends_on_source` / `mutual`(양방향) 중 하나 |
| boundary | 책임의 경계 — 양쪽이 각각 맡은 책임과 책임이 넘어가는 지점 |
| separation_rationale | 분리 이유 & 합리성 평가 — 하나로 합치지 않고 분리한 이유와 그 타당성 |
| questions | 내가 할 수 있는 질문 — 검토 시 다시 물어볼 질문 목록 |

**검증 규칙(존재 여부)**: `level`이 `group`이면 그룹 간에 실제 교차-그룹 의존관계가 있는 쌍에만 존재하며, 그룹이 1개 이하면 존재해서는 안 된다(spec.md FR-025). `level`이 `element`이면 실제로 직접 연결된 요소 쌍에만 존재하며, 같은 그룹 여부와 무관하게(그룹이 달라도) 생성된다 — 그룹 레벨 항목과 배타적이지 않다.
**검증 규칙(내용)**: `boundary`/`separation_rationale`/`questions` 세 필드 모두 반드시 채워야 하며, `source`/`target` 이름은 설명이 실제로 부여한 것만 근거로 삼아야 한다(spec.md FR-026, FR-027). `direction`은 볼드 이름과 함께 실제 방향(또는 양방향이면 상호 의존)을 그대로 서술해야 한다.

## Multi-target (Parallel-Sibling) Consolidation Rule (다수 대상/병렬 형제 통합 규칙)

같은 그룹에 속하고 서로 병렬적인 구조적 역할(같은 종류의 자리를 채우는 형제 요소 — 이름·구현 세부사항만 다를 뿐 종류가 다른 역할을 가진 대상은 없음)을 수행하는 대상 3개 이상에 대해, 각각을 별개 항목으로 나열하는 대신 하나로 묶어 서술하는 규칙. Collaboration Item(`target` 측, spec.md FR-027b)과 Responsibility Entry(그룹/요소 측, spec.md FR-009b) 양쪽에 동일한 판단 기준으로 적용된다(2026-08-02 세 번째 세션 — 이전의 "다이어그램의 다른 곳에서 개별적으로 구분되지 않음" 조건을 대체).

| 조건 | Collaboration Item 결과 | Responsibility Entry 결과 |
|------|------|------|
| 대상 3개 이상 **and** 모두 같은 그룹 **and** (Collaboration만) 모두 같은 `nature` **and** 병렬적 구조적 역할을 공유하며 종류가 다른 역할을 가진 대상 없음 | 하나의 Collaboration Item으로 통합(`target`은 집합을 아우르는 서술적 표현, 하이퍼링크 없음) — 대상들이 각자 자기 엣지를 갖거나 Responsibility 서술이 서로 달라도(예: 서로 다른 함수 이름) 무방 | 하나의 Responsibility Entry로 통합(`target`은 모든 이름을 "A, B, C"로 나열, 각각 하이퍼링크; `responsibility_abstract`는 공유 문장 하나, `responsibility_concrete`는 요소별 근거를 빠짐없이 인용) |
| 대상 2개 이하, 그룹이 다름, (Collaboration만) `nature`가 다름, 또는 대상 중 하나라도 종류가 다른 역할을 가짐(다른 대상에 없는 별도의 책임·관계) | 대상마다 개별 Collaboration Item 생성(target 2개면 "와"/"과"로 이어 서술) | 대상마다 개별 Responsibility Entry 생성 |

**검증 규칙**: 이 규칙은 spec.md FR-011(설명에 없는 컴포넌트 추가 금지)과 함께 이 스킬의 규모 통제 메커니즘 전체를 구성한다(spec.md FR-009b, FR-027b) — 통합 여부와 무관하게 실제로 존재하는 대상 외의 것을 포함해서는 안 되며, 압축된 Collaboration 서술적 표현 자체는 개별 이름을 나열하지 않는 집합 표현으로 유지된다(이는 이번 완화로 바뀌지 않는다). 종류가 다른 역할을 가진 대상은 두 엔티티 모두에서 통합 대상에서 제외되고 개별 항목을 유지한다.

## Architecture View (출력물)

Dependency, Responsibility, Collaboration 세 섹션으로 구성된 문서.

| 상태 | 설명 | 전이 조건 |
|------|------|-----------|
| Draft | `Purpose`가 확정된 뒤, Dependency·Responsibility·Collaboration이 1차 생성된 문서 | `Purpose.value`가 확정되고 대상 컴포넌트가 식별되었을 때 생성 |
| Checked | Anti-Pattern Checklist(AP-1~AP-14) 전체 항목을 통과(또는 위반 수정 완료)한 상태 | Draft에 대해 AP-1~AP-14 전부 "예" |
| Presented | 사용자에게 최종적으로 제시된 결과 — 채팅 응답에는 Output File 링크만 포함(코드 미노출) | Draft가 Checked 상태에 도달한 후에만 전이 가능 |

**불변 조건**: `Presented` 상태의 구조 뷰는 항상 `Checked`를 거쳐야 한다(spec.md FR-019, FR-020).

## Delegation Handoff (위임)

구조 뷰가 `Presented` 상태에 도달한 뒤, 시퀀스 다이어그램 생성 여부를 결정하는 절차.

| 속성 | 설명 |
|------|------|
| offered | 확인 질문을 했는지 (구조 뷰가 `Presented`에 도달하면 항상 `true`) |
| user_response | `agreed` / `declined` / `no_response` |
| enriched_description | 원래 `Process Description.raw_text` + Dependency의 컴포넌트·그룹·의존관계 + Responsibility의 책임 정보를 반영해 재구성한, 더 풍부한 자연어 프로세스 설명 — `user_response == agreed`일 때만 생성되어 `generating-zenuml-diagrams`의 입력이 됨 |

**검증 규칙**: `user_response`가 `agreed`일 때만 `generating-zenuml-diagrams`를 실행한다. `declined`나 `no_response`면 실행하지 않으며, 재차 확인 질문을 하지 않는다(spec.md FR-015, FR-016). `offered`가 `false`인 경우(구조 뷰 생성이 완료되지 않은 경우)는 이 엔티티 자체가 생성되지 않는다(spec.md FR-017).

## Anti-Pattern Checklist (번들 자산)

구조 뷰 초안을 사용자에게 보여주기 전 대조하는 규칙 목록. `.claude/skills/generating-architecture-views/SKILL.md` 본문에 포함된다.

| 항목 ID | 검사 내용 |
|---------|-----------|
| AP-1 | 설명에 없는 컴포넌트가 추가되지 않았는가 |
| AP-2 | 설명에 없는 의존관계가 추가되지 않았는가(홉을 건너뛰는 축약 화살표 포함) |
| AP-3 | 신호 없이 만들어진 그룹(subgraph)이 없는가 |
| AP-4 | 모든 화살표에 설명에 근거한(또는 기본값 "호출") 관계 성격 레이블이 있는가 |
| AP-5 | 모든 노드에 색상 클래스가 있고 엣지가 출발 노드와 같은 색인가, 형제 노드 공유가 조건에 맞는가 |
| AP-6 | 모든 그룹·요소가 책임(추상)과 역할(구체)을 모두 갖는가(추측 없이, 없으면 "설명에 명시되지 않음") |
| AP-6b | Responsibility 병렬 형제 통합이 조건에 맞을 때만 적용됐는가(3개 이상·같은 그룹·병렬적 구조적 역할, 종류가 다른 대상은 제외되어 개별 항목으로 남았는가) |
| AP-7 | 그룹 레벨 Collaboration 항목이 실제 교차-그룹 의존관계가 있는 쌍에만 있는가 |
| AP-8 | 요소 레벨 Collaboration 항목이 실제 직접 의존관계가 있는 쌍에만 있는가(그룹 동일 여부 무관) |
| AP-9 | Collaboration 다수 대상 통합이 조건에 맞을 때만 적용됐는가(개별 엣지·개별 Responsibility 서술만으로는 제외 사유가 아니며, 종류가 다른 대상만 제외되는가) |
| AP-10 | 모든 Collaboration 항목이 볼드 이름·실제 방향과 책임의 경계/분리 이유&합리성 평가/내가 할 수 있는 질문 세 가지를 모두 담는가 |
| AP-11 | 시스템에 등장하지 않는 일반적 개념을 비교하는 섹션을 만들지 않았는가 (FR-013) |
| AP-12 | 모든 항목이 백레퍼런스 없이 완전히 독립적으로 서술됐고, 목록 뒤쪽이라고 부실해지지 않았는가 |
| AP-13 | 모든 하이퍼링크가 규칙(로컬 경로/URL/링크 없음)대로 붙었고 근거 없이 지어낸 링크가 없는가 |
| AP-14 | 요청이 올바르게 분류됐고(신규/재생성/충돌) 로그 기록이 그에 맞으며, Dependency~Collaboration이 완료되지 못했으면 산출물·로그 모두 만들지 않았는가 |
| AP-15 | Runtime Flow(시퀀스) 다이어그램을 스스로 그리지 않았는가 (위임 대상 영역 침범 금지) |
| AP-16 | 시퀀스 다이어그램 생성 여부를 확인했는가, 동의 없이 `generating-zenuml-diagrams`를 실행하지 않았는가 |

**검증 규칙**: 하나라도 위반(위반=해당 항목에 대해 "아니오")이면, 사용자에게 결과를 제시하기 전에 초안을 수정해야 한다(spec.md FR-019, FR-020).

## Architecture View Feedback Log (구조 뷰 피드백 로그)

구조 뷰 산출물과는 별개의 append-only 이력 문서.

| 속성 | 설명 |
|------|------|
| log_file_path | `.zenuml/log/<slug>.architecture.md` |
| rounds | `## Round N — <ISO date>` 단위로 순서대로 쌓이는 이력 — 각 라운드는 `**Request**`(그 라운드에 실제로 기여한 대화 내용)와 `**Response**`(그 시점에 생성된 Dependency/Responsibility/Collaboration 전체 내용)를 담는다 |

**검증 규칙**: 구조 뷰가 처음 성공적으로 생성되면 Round 1과 함께 새로 만들어져야 한다(spec.md FR-028). 재생성 시 기존 라운드는 지우지 않고 새 라운드만 이어붙여야 한다(spec.md FR-029). 이 로그를 자동 요약·분석해서는 안 되며, 다른 작업이 실제로 인용할 때만 그 파일 하나가 선별적으로 버전관리에 편입된다(spec.md FR-030). 구조 뷰 생성 자체가 완료되지 않으면 이 엔티티도 만들어지지 않는다(spec.md FR-031).

## Output Files (출력 부속물)

| 속성 | 설명 |
|------|------|
| architecture_file_path | `.zenuml/<slug>.architecture.md` — 구조 뷰(Dependency, Responsibility, Collaboration)를 담는 파일. 항상 생성됨(구조 뷰가 완성된 경우) |
| sequence_file_path | `.zenuml/<slug>.md` — `generating-zenuml-diagrams`가 생성하는 시퀀스 다이어그램 파일. `Delegation Handoff.user_response == agreed`일 때만 존재 |
| available | 파일 저장(파일시스템 접근) 가능 여부 — `false`면 파일 대신 채팅 응답에 텍스트를 직접 제공 |

**검증 규칙**: `sequence_file_path`는 위임에 동의하지 않으면 존재하지 않는다(spec.md Key Entities "출력 파일"). `available`이 `false`인 경우 두 산출물 모두 채팅 응답에 직접 텍스트로 제공된다(spec.md FR-024).
