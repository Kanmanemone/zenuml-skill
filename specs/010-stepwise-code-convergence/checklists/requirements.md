# Specification Quality Checklist: 꾸며낸 최소 코드에서 원본 코드까지 단계별로 구체화해 보여 주기

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-15
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

- 결과로 보여 주는 코드의 언어는 구현 기술이 아니라 산출물의 내용 요구이므로 spec에 적는다. 2026-11-18부터 그 언어는 Kotlin 고정이 아니라 노드 원본의 언어다(FR-006).
- FR-015의 보여 주는 형태와 문서 나누기는 2026-11-15 Clarifications로 확정했다(FR-015~015c).
- FR-008의 기본 단계 정의는 초안이며 사용자 검토가 필요하다.
- 2026-11-17 스코프 트리 개편(FR-004·005·005a·005b·005c·007·011·013·014, SC-001·004·009·010·011)을 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. "스크립트"라는 말은 개편 전부터 FR-009·SC-006·US3에 있던 표현이며, 이번 개편은 "기계적으로"로만 적었다.
- 문장·묶음을 누가(메인 작업자/격리된 작업자) 쓰는지는 의도적으로 plan에 넘겼다(Assumptions). 요구는 SC-009의 구조 조건이다.
- SC-009·SC-010은 숫자 상한(글자 수 배수, 장면당 줄 수) 대신 구조 조건으로 적었다. 줄 수와 글자 수는 인지 크기·비용의 대리 지표라 합격 기준으로 두면 뜻으로 묶은 덩어리를 쪼개게 만들 수 있기 때문이다. 수치는 바꾸기 전과 후의 비교 기록으로만 남긴다.
- 2026-11-18 붙는 선언 좁히기(FR-005a(4), Edge Cases, Key Entities, SC-012)를 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. SC-012는 줄 수 상한이 아니라 "붙는 선언은 한 줄" 구조 조건과 "여러 줄 비공개 멤버가 없는 노드는 결과가 같음" 호환 조건으로 적었다.
- 트리 깊이 1인 노드가 바꾸기 전과 글자까지 같은 결과를 내는 것은 요구하지 않는다. 묶음이 뜻으로 정해지고 접기가 사라지기 때문이다. 대신 장면 종류·순서와 4개 이하 묶음을 요구한다(Edge Cases).
- 2026-11-18 원본 언어와 파일 단위 노드(FR-001a·002·005a·006·012a·017·017a, Edge Cases, US2 시나리오 8, Key Entities, SC-013, Assumptions, 경계)를 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. 선언 찾기와 스코프 트리가 어느 언어까지 기계적으로 되는지는 의도적으로 plan에 넘겼다. 요구는 "언어로 멈추지 않음"과 "Kotlin 선언 노드의 결과는 그대로"(SC-013)다.
- 2026-11-18 블록 구조를 아는 언어로 경계 바꾸기(Clarifications, FR-002·017a, Edge Cases, SC-014, Assumptions, 경계)를 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. 언어 목록은 의도적으로 plan에 넘겼고, spec은 "중괄호·들여쓰기 계열"과 "블록 구조로 확인되지 않으면 찾지 못한 것"을 요구한다.
- 2026-11-23 변화 요청(Clarifications, US4, Edge Cases, Key Entities, FR-028~032, SC-019~021, 경계, Assumptions)을 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. 사용자와 의논해 정했다: 따로 분류하지 않고 비교 기준이 있으면 0단계를 붙인다, 윤곽의 변화 표시는 두지 않는다, 사라진 줄은 빨간 배경(삼각형 없앰), 넘겨 보기를 지원하지 않는 곳은 고려하지 않는다. 0단계 모양은 swemo 샘플로 확인했다. 변경 전 시점을 PR·브랜치·커밋에서 어떻게 해석할지와 색의 구체 값은 plan에 넘겼다.
- 2026-11-23 단계를 넘길 때 스크롤 유지(Clarifications, US2 시나리오 9, Edge Cases, FR-033, SC-022, 경계, Assumptions)를 다시 검증했다. 모든 항목을 통과했고 [NEEDS CLARIFICATION]은 없다. 요청한 조건문은 스크립트가 막힌 미리보기에서 만들 수 없어, 사용자가 샘플로 비교한 뒤 공유 스크롤 상자로 정했다. 단계별 위치 기억과 탭 전환 뒤 복원은 범위 밖으로 적었다.
