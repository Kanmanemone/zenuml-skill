# Specification Quality Checklist: Architecture View Skill

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-31
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- 2026-07-31 클래리피케이션 세션에서 범위가 "의존성 그래프 단일 산출물"에서 "목적에 따라 달라지는 다단계 구조 뷰(Context/Responsibility/Dependency 필수 + 조건부 Internal/Technology/Design Rationale)"로 확장되었고, 스펙 전체를 다시 작성했다. 재작성 후에도 모든 항목이 여전히 통과 상태다(16/16, 변경 없음) — 3개의 클래리피케이션 질문(단계 범위, Comparison 포함 여부, 목적 확인 방식)으로 새로운 모호함이 모두 해소되어 [NEEDS CLARIFICATION] 마커 없이 재작성을 완료할 수 있었다.
- 2026-07-31 두 번째 요청("스킬을 여러 파일로 분리하자")은 스펙 수준(WHAT)이 아니라 구현 계획 수준(HOW)의 결정이라고 판단해 정식 클래리피케이션 질문으로 다루지 않았다 — 방향성만 Assumptions에 비구속적 권고로 남기고 formal Q&A는 진행하지 않음.
- 2026-07-31 세 번째(가장 큰) 재구성: (1) Context와 Dependency를 하나의 섹션으로 병합, (2) Responsibility를 "그룹 내 컴포넌트 전부를 이항대립(n×(n-1)개) 비교"하는 구체적 메커니즘으로 명세, (3) Internal Architecture/Technology/Design Rationale 3개 조건부 섹션을 완전히 폐기, (4) 이 스킬이 `generating-zenuml-diagrams`에 의존하며 단독으로 완결되지 않고 매 실행마다 그 스킬을 실행시켜 시퀀스 다이어그램까지 이어서 제시하도록 방향을 뒤집음(이전의 "완전히 독립적" 가정을 대체). 스펙 전체를 다시 작성했고, 재작성 후에도 모든 항목이 여전히 통과 상태다(16/16, 변경 없음).
- 남은 세부 사항("기타" 목적 선택 시 후속 질문 구성, 정확한 출력 파일명 규칙, 렌더링 실측 재검증, 위임(delegation) 메커니즘의 구체적 구현 방식과 확인 질문 문구, 확장된 범위에 따른 appetite 재평가, 스킬 내부 파일 구성 방향성)은 스펙의 모호함이 아니라 구현 단계의 판단으로 분류해 Assumptions 섹션에 기록했다 — `/speckit-plan` 재실행에서 확정 권장.
- 2026-07-31 네 번째 재구성: "구조 뷰 2개 섹션 + 시퀀스 다이어그램 위임을 한 번에 묶어서 자동 실행"하던 것을 "구조 뷰 완성 → 시퀀스 다이어그램까지 만들지 사용자에게 확인 → 동의해야만 실행"으로 변경(User Story 2, FR-014~017, SC-005~006, Assumptions "두 스킬의 관계" 갱신). `generating-zenuml-diagrams`에 대한 **의존**(설계상 그 스킬로 이어지도록 만들어짐) 자체는 유지되지만, "매번 자동 실행"은 더 이상 아니다. 재작성 후에도 모든 체크리스트 항목이 여전히 통과 상태다(16/16, 변경 없음).
- 2026-07-31 수학 정정: 이항대립 비교 항목 수 공식이 n×(n-1)(순서 있는 쌍, 중복 포함)에서 n×(n-1)/2(순서 없는 쌍)로 정정되었다 — "A vs B"와 "B vs A"는 같은 관계를 중복 서술하는 것이므로 하나의 항목으로 충분하다. FR-008, FR-019, SC-003, Key Entities, User Story 1/3의 모든 예시 수치를 갱신했다. 같은 세션에서 "비교를 의존관계로 연결된 쌍만으로 한정할지"도 논의했으나 그룹 내 전체 쌍 비교(현행)를 유지하기로 확정했다(FR-008에 명시).
- 2026-07-31 `/speckit-plan` 재실행: 위 모든 개정을 반영해 `plan.md`/`research.md`/`data-model.md`/`contracts/skill-interface.md`/`quickstart.md`를 현재 스펙(Components & Dependencies+Responsibility 2섹션, n×(n-1)/2 그룹 내 전체 쌍 비교, 사용자 확인 후 조건부 위임)에 맞게 다시 생성했다. 더 이상 갱신이 미뤄진 아티팩트는 없다.
- 2026-07-31 `/speckit-implement` 중 실사용 테스트에서 발견된 두 가지 결함을 즉시 스펙에 반영: (1) 산출물 파일에서 Components & Dependencies 섹션에만 `###` 제목이 없던 것을 발견해 FR-021 서술을 보강(내용 변경은 아니고 명확화). (2) **그룹(subgraph) 자체끼리도 이항대립 비교하라는 원래 요청이 누락되어 있었음을 발견** — FR-025(그룹이 m개면 그룹 간 비교도 m×(m-1)/2개), FR-026(그룹 비교는 레이블만 근거)을 추가하고, Key Entities에 "그�룹 비교 항목" 추가, SC-003b 추가, User Story 1에 Acceptance Scenario 3(그룹 3개 이상) 추가. 재작성 후에도 모든 체크리스트 항목이 여전히 통과 상태다(16/16, 변경 없음) — 새 FR을 기존 번호 뒤에 추가하는 방식으로 반영해 기존 FR 번호 재부여로 인한 광범위한 교차 참조 깨짐을 피했다.
- 2026-08-01 다섯 번째 클래리피케이션: 실제 산출물 `android-nav3-migration-before.architecture.md`을 검토하던 사용자가 각 Responsibility 항목 끝의 "차이: <대조>" 절이 불필요하다고 지적 — 두 책임/레이블을 나란히 서술하는 것만으로 이미 차이가 드러나므로 별도 요약 문장은 군더더기라는 판단. FR-009, FR-010, FR-019, SC-002, Key Entities의 Responsibility Comparison Item 정의, User Story 1 본문/Acceptance Scenario 2, Edge Cases에서 "차이" 요약 절 관련 서술을 모두 제거했다. 재작성 후에도 모든 체크리스트 항목이 여전히 통과 상태다(16/16, 변경 없음) — 이 변경은 서식을 단순화할 뿐 테스트 가능성이나 모호함에 영향을 주지 않는다.
- 2026-08-01 여섯 번째 클래리피케이션: 사용자가 "왜 이 스킬만 `.zenuml/log/`에 아무것도 안 남기냐"고 물어 확인해보니, `generating-zenuml-diagrams`(001)가 002-diagram-feedback-log로 이미 갖춘 재생성 이력 로그 메커니즘이 이 스킬(003) 자신의 산출물에는 애초에 요구사항으로 존재한 적이 없었음을 발견 — FR-018은 위임 대상 스킬 자신의 로그를 건드리지 말라는 뜻일 뿐이었다. 002의 메커니즘(최초 생성 시 로그 Round 1 생성, 재생성 시 산출물 교체+로그에 라운드 추가, 자동 요약 금지, 인용 시에만 선별 스테이징, 미완료 시 로그 미생성)을 최소한으로 이식해 FR-028~031, Key Entities에 "구조 뷰 피드백 로그", SC-009, Assumptions에 로그 디렉터리 관례를 추가했다. 재작성 후에도 모든 체크리스트 항목이 여전히 통과 상태다(16/16, 변경 없음).
- 2026-08-02 일곱 번째 클래리피케이션(v10 실사용 산출물 `navigation.architecture.md` 검토 중 발견): 사용자가 병렬적 형제 요소(같은 그룹·같은 관계 성격에서 같은 역할을 채우는 요소들)가 Collaboration에서 개별 이름·구현 차이만으로 통합이 막히는 것에 불만을 제기 — FR-027b의 "다른 곳에서 개별적으로 구분되지 않음" 조건을 "병렬적 구조적 역할을 수행함"으로 완화(종류가 다른 역할을 가진 대상은 여전히 제외)하고, Responsibility에도 동일한 조건의 신규 FR-009b(병렬 형제 통합)를 추가했다. User Story 1 Acceptance Scenario 4, User Story 2 Acceptance Scenario 2 개정 및 4 신설, Edge Cases 1건 추가, Key Entities("책임 서술", "협력 항목", "다수 대상(병렬 형제) 통합 규칙") 갱신, Assumptions에 "병렬적 구조적 역할" 판단 방식(질적 판단, 두 섹션이 동일 기준 재사용) 기록. 오버엔지니어링 방지를 위해 새 메커니즘을 만들지 않고 기존 다수 대상 통합 규칙의 조건만 완화·재사용했다. 재작성 후에도 모든 체크리스트 항목이 여전히 통과 상태다(16/16, 변경 없음) — 조건 완화이며 임계값(3개 이상)·게이팅 자체(같은 그룹·같은 관계 성격)는 그대로 유지되어 기존 테스트 가능성에 영향 없음.
