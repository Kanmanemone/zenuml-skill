# Problem Definition: 시퀀스 다이어그램만으로는 채워지지 않는 구조적 mental model

- **Slug**: generate-architecture-views
- **Created**: 2026-07-31
- **Inputs used**: intake.md, research.md

## Problem Statement

이 저장소의 `generating-zenuml-diagrams` 스킬은 자연어로 설명된 프로세스를 시퀀스 다이어그램(행동/Behavior 수준)으로만 시각화하며, 컴포넌트 구성·그룹핑·의존관계 같은 구조적 정보는 산출물에 담기지 않는다. 그 결과 스킬 사용자는 특정 플로우가 "어떻게 동작하는지"는 알 수 있지만, 대상 시스템/프로세스의 "무엇이 존재하고, 어떻게 묶이며, 무엇이 무엇을 의존하는지"에 대한 mental model은 별도 수단(직접 코드 읽기, 수작업 다이어그램 등) 없이는 구축할 수 없다.

## Affected Users & Stakeholders

- **Users**: 이 저장소에서 `generating-zenuml-diagrams` 스킬을 사용해 프로세스를 다이어그램으로 옮기는 사람(현재는 요청자 본인, dogfooding) — 시퀀스 다이어그램만 받고 나면 구조 질문에 답하기 위해 별도로 코드를 읽거나 직접 그림을 그려야 함. — [source: intake.md, research.md] (confidence: high, 표본 1인)
- **Stakeholders**: 저장소 메인테이너(요청자 본인) — 스킬 셋의 스코프와 방향을 결정하는 주체. **결정됨(2026-07-31)**: 이 문제는 `generating-zenuml-diagrams`의 스코프를 바꾸지 않고 **별도의 새 스킬**로 해결한다 — 따라서 해당 스킬의 "코드베이스 분석/비-시퀀스 다이어그램 out-of-scope" 선언([source: .claude/skills/generating-zenuml-diagrams/SKILL.md:156-158])과 충돌하지 않는다.

## Goals

- 시퀀스 다이어그램(Behavior)만으로 충족되지 않는 구조 정보 — 최소한 "무엇이 존재하는가(Components)", "어떻게 묶이는가(Grouping)", "누가 누구를 의존하는가(Dependencies)" — 를 사용자가 별도 수작업 없이 얻을 수 있게 한다. — [source: research.md "Practical Operationalization" 절, C4/ADR 실무 관행 근거]
- **입력은 기존 `generating-zenuml-diagrams`와 동일하게 자연어 프로세스 설명이다** — 실제 코드베이스 정적 분석은 하지 않는다. **결정됨(2026-07-31, 사용자 답변)**
- **Grouping(묶임)은 사용자가 직접 지정하지 않고 자동으로 추론되어야 한다.** **결정됨(2026-07-31, 사용자 답변)** — 무엇을 신호로 자동 그룹을 추론할지는 여전히 열려 있음(아래 Open Questions).
- **Intent(왜 이렇게 설계했는가)도 포함하되, 별도의 긴 섹션이 아니라 다이어그램 내 주석(comment) 등 간결한 형태로 담아 사용자가 느끼는 구조적 모호함을 해소해야 한다.** 단, 너무 길어져서는 안 되고, 근거 없는 추측으로 채워서도 안 된다. **결정됨(2026-07-31, 사용자 답변)**
- 새 산출물이 기존 스킬의 출력 관행(파일로 저장, `.zenuml/` 하위, Mermaid 기반 렌더링 등)과 정합적으로 통합되도록 한다 — 단, 별도 스킬로서 통합하는 구체적 방식(같은 파일 vs 별도 파일)은 아직 미결정(Open Questions 참고). — [source: 내부 선례, .claude/skills/generating-zenuml-diagrams/SKILL.md]

## Non-Goals

- **범용 다이어그램 도구가 되는 것은 아님**: 클래스 다이어그램, 배포 다이어그램 등 임의의 UML 유형 전체를 지원하는 것이 목적이 아니다 — mental model 5단계 중 구조 이해(1~3단계, Components/Grouping/Dependencies)를 보강하는 것이 목적. [source: research.md]
- **실제 코드베이스를 파싱/정적 분석하는 기능은 범위 밖이다** — 입력은 자연어 프로세스 설명이며, `swark` 류의 코드-분석 기반 도구와는 접근 방식이 다르다. **결정됨(2026-07-31, 사용자 답변)**
- **기존 `generating-zenuml-diagrams`의 SKILL.md 자체를 수정하는 것은 범위 밖이다** — 이 문제는 별도의 새 스킬로 해결한다. **결정됨(2026-07-31, 사용자 답변)**
- **근거 없는 Intent 추론은 하지 않는다**: 설명에 명시되지 않은 설계 이유를 지어내 채우는 것은 다루지 않는다 — 이는 `generating-zenuml-diagrams`의 anti-fluff 원칙(AP-1~AP-4)과 동일한 정신을 구조 산출물에도 적용해야 함을 의미한다. [source: .claude/skills/generating-zenuml-diagrams/SKILL.md:68-83]
- **다이어그램의 지속적 자동 동기화는 다루지 않는다**: 코드/설명이 바뀔 때마다 산출물을 자동으로 최신화하는 기능(watch/CI 연동 등)은 이번 문제 정의의 범위 밖이다. [ASSUMPTION — intake/research 어디에도 요청되지 않았음, 문제를 좁히기 위해 배제]

## Success Metrics

- **(정성적)** 스킬 산출물만 보고 사용자가 "이 시스템에 어떤 컴포넌트가 있고, 그것들이 어떻게 그룹지어지며, 누가 누구를 의존하는지"를 별도의 코드 탐색 없이 설명할 수 있다. (baseline: 현재는 불가능 — 시퀀스 다이어그램은 참가자 간 호출은 보여주지만 그룹/전체 의존 구조를 한눈에 보여주지 않음) [ASSUMPTION — 정량 지표 부재, 표본 1인 dogfooding이라 정성적 신호로만 판단 가능; 향후 사용자가 늘면 재검토 필요]
- **(정성적)** 새 산출물이 기존 `.zenuml/<slug>.md` 워크플로에 자연스럽게 얹혀, 사용자가 별도 도구나 별도 실행 절차를 배우지 않고 사용할 수 있다. (baseline: 현재 워크플로는 시퀀스 다이어그램 1종만 생성)

## Cost of Inaction

아무것도 만들지 않으면, 사용자는 계속 시퀀스 다이어그램만으로 프로세스의 동작(Behavior)은 파악하되 구조(Components/Grouping/Dependencies)는 파악하지 못한 상태로 남는다. 구조를 알아야 할 때마다 코드를 직접 읽거나 수작업으로 별도 다이어그램을 그려야 하며, 이는 이 저장소가 애초에 해결하려던 "다이어그램 생성 자동화"의 가치를 구조 이해 영역에서는 얻지 못하는 상태가 지속됨을 의미한다. 시장에는 이미 유사 문제를 코드베이스 분석으로 푸는 도구(`swark` 등)가 있으므로, 이 저장소가 계속 손을 대지 않으면 사용자는 결국 외부 도구로 이탈하거나 수작업을 계속해야 한다. — [source: research.md "Prior Art"]

## Open Questions

이전 라운드의 5개 질문 중 4개는 2026-07-31에 사용자가 답하여 위 Goals/Non-Goals에 반영되었다 (입력 방식=자연어, Grouping=자동, Intent=포함(주석 형태, 간결하게), 새 스킬 여부=별도 신규 스킬). 남은 것과 새로 파생된 질문:

- [NEEDS CLARIFICATION: 결과물 파일 구조 — 새 스킬의 산출물을 기존 `.zenuml/<slug>.md`와 같은 파일에 넣을지, 같은 슬러그를 공유하는 별도 파일(예: `.zenuml/log/`처럼 형제 하위 경로)로 분리할지. 사용자가 조언을 요청함 — `/speckit-assess-shape` 단계에서 이 저장소의 기존 파일 배치 관례(아래 참고)를 근거로 결정 권장.]
- [NEEDS CLARIFICATION: "자동 Grouping"의 판단 근거(신호)는 무엇인가 — 참가자 이름의 접두사/네임스페이스, 설명에서 언급된 계층 구조, 호출 빈도/결합도 등 중 무엇을 기준으로 자동 추론할 것인가? 자동 추론이 틀렸을 때 사용자가 어떻게 정정하는가(재질문 vs 무시)도 함께 결정 필요.]
- [NEEDS CLARIFICATION: Intent를 담을 "주석"의 위치와 트리거 조건 — 모든 컴포넌트/의존관계에 항상 주석을 달 것인가, 아니면 "사용자가 모호함을 느낄 만한" 지점에만 선별적으로 달 것인가? 후자라면 그 판단 기준이 필요하다.]
- [NEEDS CLARIFICATION: 새 스킬과 `generating-zenuml-diagrams`는 서로 독립적으로 호출되는가, 아니면 한쪽이 다른 쪽을 트리거하거나 같은 대화 안에서 함께 제안되는가? (예: 시퀀스 다이어그램을 만든 직후 "구조 뷰도 만들까요?"처럼 연계할지)]

### 참고 — 파일 구조 조언을 위한 이 저장소의 기존 관례

`/speckit-assess-shape`에서 파일 구조를 결정할 때 참고할 수 있도록, 이번 조사에서 확인한 이 저장소의 기존 산출물 배치 패턴을 기록해 둔다 (문제 정의 자체의 결정은 아님):

- **`generating-zenuml-diagrams`**: 슬러그 하나당 산출물 파일 하나(`.zenuml/<slug>.md`, 재생성 시 덮어씀) + 같은 슬러그의 append-only 이력 파일을 형제 하위 디렉터리에 분리(`.zenuml/log/<slug>.md`). 즉 "현재 상태"와 "이력"을 서로 다른 파일로 분리하는 패턴.
- **`speckit-assess-*` 계열(이번 파이프라인)**: 슬러그 하나당 디렉터리(`.specify/assessments/<slug>/`)를 만들고, 파이프라인 단계마다 별도 파일(`intake.md`, `research.md`, `problem.md`, `concept.md`, `decision.md`)을 쌓는 패턴. 즉 "종류가 다른 정보"는 파일을 나누고, "같은 슬러그"는 디렉터리로 묶는 패턴.
- 두 관례 모두 공통적으로 **"같은 슬러그 = 같은 폴더/같은 파일 계열", "성격이 다른 정보(현재 상태 vs 이력, 혹은 파이프라인 단계)는 별도 파일"** 이라는 원칙을 따른다. 이번 문제의 "구조 뷰"는 시퀀스 다이어그램과 *같은 슬러그, 같은 대상*을 다루지만 *성격이 다른 정보*이므로, 두 관례 모두 "같은 폴더 안 별도 파일"을 가리킨다는 점은 참고할 만하다.
