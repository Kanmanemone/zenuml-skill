# Idea Intake: 구조 이해를 위한 아키텍처 뷰 생성 스킬

- **Slug**: generate-architecture-views
- **Created**: 2026-07-31
- **Source**: pasted text
- **Type**: new-capability

## Idea (as captured)

> 시퀀스 다이어그램만으로는 구조를 명확하게 알 수 없어. 사용자의 mental model을 구축시켜주기 위한 스킬이 필요해

## Restated

시퀀스 다이어그램만으로는 시스템/코드의 구조를 명확히 파악하기 어렵다는 문제 인식이 있으며, 사용자가 대상 구조에 대한 mental model을 세울 수 있도록 돕는 새로운 스킬(또는 기존 스킬의 확장)이 필요하다는 제안이다.

## Origin & Context

- **Raised by**: 사용자 (이 대화에서 직접 제기)
- **Trigger**: 기존 `generating-zenuml-diagrams` 스킬이 시퀀스 다이어그램만 생성하며, 시퀀스 다이어그램만으로는 구조(컴포넌트 관계, 계층, 책임 분리 등)를 파악하기 어렵다는 한계 인식 [NEEDS CLARIFICATION: 이 한계를 인식하게 된 구체적 계기(특정 사용 사례, 사용자 피드백 등)가 있는지]

## First-Glance Unknowns

- [NEEDS CLARIFICATION: "구조를 명확하게 알 수 없다"는 것이 구체적으로 어떤 정보의 부재를 의미하는가 — 컴포넌트/클래스 관계, 모듈 경계, 데이터 흐름, 계층 구조 등 중 무엇인가]
- [NEEDS CLARIFICATION: 이 스킬이 생성해야 할 산출물의 형태 — 컴포넌트 다이어그램, 클래스 다이어그램, C4 모델 등 다이어그램 종류가 정해져 있는가, 아니면 다이어그램 외 형태(텍스트 설명, 트리 구조 등)도 고려하는가]
- [NEEDS CLARIFICATION: 기존 `generating-zenuml-diagrams` 스킬과의 관계 — 이를 보완하는 별도 스킬인지, 확장인지, 통합인지]
- [NEEDS CLARIFICATION: 이 스킬의 입력은 무엇인가 — 코드베이스, 기존 시퀀스 다이어그램, 자연어 설명, 혹은 이들의 조합인가]
- [NEEDS CLARIFICATION: 대상 사용자는 누구인가 — 신규 합류자, 기존 팀원, 리뷰어 등 mental model을 구축해야 할 주체]
- [NEEDS CLARIFICATION: "구조"의 범위 — 전체 시스템 아키텍처인지, 특정 기능/모듈 단위인지]
